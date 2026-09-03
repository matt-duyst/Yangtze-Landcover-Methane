"""Anonymous acquisition from figshare.

figshare's public API needs no token for an open record. An article's JSON
carries, per file, its name, size, ``computed_md5`` and a direct download URL,
which is the same shape Science Data Bank's Croissant export provides, so this
module holds only the metadata parsing and shares everything downstream with
``src.fetch.common``.

Two differences from the Science Data Bank route are worth naming.

First, a figshare DOI encodes its own article id and version:
``10.6084/m9.figshare.27965832.v2`` is article 27965832 at version 2. The id
can therefore be recovered without a network round-trip, which
:func:`article_id_from_doi` does; :func:`resolve_doi` remains for a DOI that
does not follow the pattern.

Second, the payload here is a zip of 61 netCDF files when a study needs six of
them. :func:`extract_members` unpacks only what a predicate selects, and
reports what it took, so the manifest can record the extracted members rather
than only the archive that held them.
"""

from __future__ import annotations

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

import requests

from src.fetch.common import (  # noqa: F401  (re-exported for callers)
    DEFAULT_ALLOWED_CONTENT_TYPES,
    DEFAULT_TIMEOUT,
    ChecksumMismatch,
    FetchError,
    FileRecord,
    TruncatedDownload,
    UnexpectedContentType,
    digest_of,
    download_record,
    filter_records,
    is_already_fetched,
    md5_of,
    name_contains_any,
    plan,
)

DEFAULT_API_BASE = "https://api.figshare.com/v2"
DEFAULT_DOI_RESOLVER = "https://doi.org"

#: ``10.6084/m9.figshare.<article>.v<version>``; the version part is optional.
_DOI_RE = re.compile(r"figshare\.(\d+)(?:\.v(\d+))?\s*$", re.IGNORECASE)
#: ``figshare.com/articles/dataset/<slug>/<article>/<version>``. Anchored at the
#: end and non-greedy, because a greedy walk captures the trailing version
#: number instead of the article id.
_ARTICLE_URL_RE = re.compile(r"/articles/(?:[^/]+/)*?(\d+)(?:/\d+)?/?$")


class FigshareError(FetchError):
    """Base class for failures specific to this route."""


class NoFilesError(FigshareError):
    """The article parsed but listed no files."""


class MemberNotFound(FigshareError):
    """A requested archive member is not in the archive."""


@dataclass(frozen=True)
class ExtractedMember:
    """One member taken out of a downloaded archive."""

    archive: str
    member: str
    path: Path
    bytes: int
    sha256: str

    def as_dict(self) -> dict:
        return {
            "archive": self.archive,
            "member": self.member,
            "path": str(self.path),
            "bytes": self.bytes,
            "sha256": self.sha256,
        }


def article_id_from_doi(doi: str) -> tuple[int, int | None]:
    """Parse a figshare DOI into ``(article_id, version)`` without a request.

    Returns ``version`` as None when the DOI carries no ``.vN`` suffix.
    """
    match = _DOI_RE.search(doi.strip())
    if not match:
        raise FigshareError(
            f"{doi!r} does not look like a figshare DOI of the form "
            f"10.6084/m9.figshare.<article>[.v<version>]"
        )
    version = int(match.group(2)) if match.group(2) else None
    return int(match.group(1)), version


def resolve_doi(
    doi: str,
    *,
    resolver: str = DEFAULT_DOI_RESOLVER,
    timeout: float = DEFAULT_TIMEOUT,
    session: requests.Session | None = None,
) -> int:
    """Resolve a DOI to a figshare article id by following it.

    Prefer :func:`article_id_from_doi`, which needs no network. This exists for
    a DOI that does not follow figshare's naming.
    """
    sess = session or requests.Session()
    url = f"{resolver.rstrip('/')}/{doi.lstrip('/')}"
    response = sess.get(url, timeout=timeout, allow_redirects=True)
    response.raise_for_status()
    final = str(getattr(response, "url", "") or "")
    match = _ARTICLE_URL_RE.search(final)
    if not match:
        raise FigshareError(
            f"could not find an article id in the URL {doi!r} resolved to: {final!r}"
        )
    return int(match.group(1))


def fetch_article(
    article_id: int,
    *,
    version: int | None = None,
    api_base: str = DEFAULT_API_BASE,
    timeout: float = DEFAULT_TIMEOUT,
    session: requests.Session | None = None,
) -> dict:
    """Retrieve an article's metadata, optionally pinned to a version."""
    sess = session or requests.Session()
    url = f"{api_base.rstrip('/')}/articles/{article_id}"
    if version is not None:
        url = f"{url}/versions/{version}"
    response = sess.get(url, timeout=timeout)
    response.raise_for_status()
    return response.json()


def parse_files(article: dict) -> list[FileRecord]:
    """Turn an article's ``files`` array into file records.

    figshare publishes ``computed_md5``, the digest it calculated from the
    stored bytes, and ``supplied_md5``, whatever the depositor typed. The
    computed one is preferred because it describes the file that will actually
    arrive.
    """
    files = article.get("files") or []
    records = [
        FileRecord(
            name=str(entry.get("name") or ""),
            content_size=int(entry["size"]) if entry.get("size") is not None else None,
            encoding_format=entry.get("mimetype"),
            digest=entry.get("computed_md5") or entry.get("supplied_md5"),
            content_url=str(entry.get("download_url") or ""),
            digest_algorithm="md5",
        )
        for entry in files
        if entry.get("download_url")
    ]
    if not records:
        raise NoFilesError(
            f"figshare article {article.get('id', '?')} lists no downloadable "
            f"files. An embargoed or metadata-only record looks like this."
        )
    return records


def licence_of(article: dict) -> str | None:
    """The licence name the record declares, if any."""
    licence = article.get("license") or {}
    return licence.get("name")


def extract_members(
    archive: Path,
    destination_dir: Path,
    predicate: Callable[[str], bool],
    *,
    overwrite: bool = False,
) -> list[ExtractedMember]:
    """Extract only the archive members ``predicate`` selects.

    The GloRice archive holds 61 yearly netCDF files and a study needs six, so
    unpacking everything would cost roughly ten times the disk for no gain.
    Each extracted member is hashed as it is written and reported, so the
    manifest can record what came out rather than only what went in.

    Directory entries are skipped, and any member whose name would escape
    ``destination_dir`` is refused rather than written.
    """
    archive = Path(archive)
    destination_dir = Path(destination_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)
    resolved_root = destination_dir.resolve()

    taken: list[ExtractedMember] = []
    with zipfile.ZipFile(archive) as bundle:
        names = [n for n in bundle.namelist() if not n.endswith("/")]
        wanted = [n for n in names if predicate(n)]
        if not wanted:
            raise MemberNotFound(
                f"no member of {archive.name} matched the selection; the archive "
                f"holds {len(names)} files, for example {names[:3]}"
            )
        for name in wanted:
            target = (destination_dir / Path(name).name).resolve()
            if not str(target).startswith(str(resolved_root)):
                raise FigshareError(f"refusing to write {name!r} outside {destination_dir}")
            if target.exists() and not overwrite:
                taken.append(
                    ExtractedMember(
                        archive=archive.name, member=name, path=Path(target),
                        bytes=target.stat().st_size,
                        sha256=digest_of(Path(target), algorithm="sha256"),
                    )
                )
                continue
            with bundle.open(name) as source, open(target, "wb") as handle:
                while True:
                    block = source.read(1 << 20)
                    if not block:
                        break
                    handle.write(block)
            taken.append(
                ExtractedMember(
                    archive=archive.name, member=name, path=Path(target),
                    bytes=target.stat().st_size,
                    sha256=digest_of(Path(target), algorithm="sha256"),
                )
            )
    return taken


def year_selector(years: Iterable[int | str]) -> Callable[[str], bool]:
    """Predicate matching archive members whose name contains any given year.

    Which years matter is a study choice and comes from configuration, so no
    year appears in this module.
    """
    tokens = [str(y) for y in years]
    if not tokens:
        raise ValueError("year_selector() needs at least one year")

    def predicate(name: str) -> bool:
        stem = Path(name).name
        return any(token in stem for token in tokens)

    return predicate
