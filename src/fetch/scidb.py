"""Anonymous acquisition from Science Data Bank via its public Croissant export.

Science Data Bank serves dataset metadata in the Croissant JSON-LD format from
an endpoint that needs no account, no session and no cookie. That export
carries, for every file in a record, its name, size, media type, MD5 and a
direct download URL. Four unauthenticated GETs therefore take a DOI to verified
files on disk, which is why this source is the first one wired up.

The authenticated API surface is a different thing entirely: every route under
``/api/sdb-dataset-service`` and ``/api/sdb-filetree-service`` answers
``{"code":20001,"message":"用户未登录"}`` to an anonymous caller. Only the
``/public/`` Croissant route is open. Do not reach for the other endpoints.

Two behaviours of that endpoint will silently produce wrong results and are
guarded here rather than described in a comment:

* The ``version`` parameter must carry its ``V`` prefix. ``version=V8`` returns
  the real record; ``version=8`` returns HTTP 200 and a syntactically valid
  Croissant document with every field blank and an empty ``distribution``. A
  caller who trusts the status code gets an empty file list and no error.
* A download that fails at the edge can still answer HTTP 200 with an HTML
  error page or a truncated body. Writing that to a ``.tif`` path produces a
  file that fails much later, somewhere less informative.

No credentials appear in this module and none are needed. The NESDC FTP grant
covering the same data is personal-use and is deliberately not scripted.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

import requests

#: Public Croissant export. The ``/public/`` segment is what makes it anonymous.
DEFAULT_BASE_URL = "https://www.scidb.cn/api/gin-sdb-croissant/public/exportCroissant"

#: DOI resolver. Answers a redirect to the record page, whose query string
#: carries the dataset id.
DEFAULT_DOI_RESOLVER = "https://doi.org"

#: Seconds. Generous enough for a cold cache, short enough to fail rather than
#: hang a batch.
DEFAULT_TIMEOUT = 60.0

#: Media types a data file may legitimately arrive as. An error page is HTML or
#: JSON and will not appear here, which is the point.
DEFAULT_ALLOWED_CONTENT_TYPES = (
    "application/octet-stream",
    "binary/octet-stream",
    "image/tiff",
    "application/zip",
    "application/x-zip-compressed",
    "application/gzip",
    "application/x-netcdf",
)

_DATASET_ID_RE = re.compile(r"dataSetId=([0-9a-fA-F]{32})")
_CONTENT_SIZE_RE = re.compile(r"^\s*(\d+)\s*(?:B|bytes?)?\s*$", re.IGNORECASE)
_CHUNK = 1 << 20


class ScidbError(RuntimeError):
    """Base class for every failure this module raises deliberately."""


class EmptyDistributionError(ScidbError):
    """The Croissant document parsed but listed no files.

    Almost always the ``V``-prefix trap rather than an empty record.
    """


class ChecksumMismatch(ScidbError):
    """A downloaded or existing file does not match its published MD5."""


class UnexpectedContentType(ScidbError):
    """The server answered 200 with something that is not a data file."""


class TruncatedDownload(ScidbError):
    """Fewer bytes arrived than the record declared."""


@dataclass(frozen=True)
class FileRecord:
    """One file in a Science Data Bank record."""

    name: str
    content_size: int | None
    encoding_format: str | None
    md5: str | None
    content_url: str

    @property
    def stem(self) -> str:
        """Filename without directories, for use as a destination name."""
        return self.name.rsplit("/", 1)[-1]


def require_versioned(version: str) -> str:
    """Return ``version`` unchanged, or raise if it lacks its ``V`` prefix.

    The endpoint does not reject a bare number; it answers with an empty
    skeleton. Catching it here turns a silent wrong answer into an error at the
    call site that made the mistake.
    """
    if not isinstance(version, str) or not version:
        raise ValueError("version must be a non-empty string such as 'V8'")
    if not version.startswith("V"):
        raise ValueError(
            f"version must carry its 'V' prefix; got {version!r}. "
            f"Science Data Bank answers HTTP 200 with an empty record for a "
            f"bare number, so {version!r} would yield no files and no error."
        )
    return version


def _parse_content_size(value: object) -> int | None:
    """Croissant reports sizes as strings like ``'27719296 B'``."""
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        m = _CONTENT_SIZE_RE.match(value)
        if m:
            return int(m.group(1))
    return None


def resolve_doi(
    doi: str,
    *,
    resolver: str = DEFAULT_DOI_RESOLVER,
    timeout: float = DEFAULT_TIMEOUT,
    session: requests.Session | None = None,
) -> str:
    """Resolve a Science Data Bank DOI to its 32-character dataset id."""
    sess = session or requests.Session()
    url = f"{resolver.rstrip('/')}/{doi.lstrip('/')}"
    response = sess.get(url, timeout=timeout, allow_redirects=True)
    response.raise_for_status()
    final = str(getattr(response, "url", "") or "")
    match = _DATASET_ID_RE.search(final)
    if not match:
        raise ScidbError(
            f"could not find a dataSetId in the URL {doi!r} resolved to: {final!r}"
        )
    return match.group(1)


def fetch_croissant(
    dataset_id: str,
    version: str,
    *,
    base_url: str = DEFAULT_BASE_URL,
    timeout: float = DEFAULT_TIMEOUT,
    session: requests.Session | None = None,
) -> dict:
    """Retrieve the Croissant JSON-LD document for one dataset version."""
    require_versioned(version)
    sess = session or requests.Session()
    response = sess.get(
        base_url,
        params={"datasetId": dataset_id, "version": version},
        timeout=timeout,
    )
    response.raise_for_status()
    return response.json()


def parse_distribution(croissant: dict, *, version: str | None = None) -> list[FileRecord]:
    """Turn a Croissant document into file records.

    Raises :class:`EmptyDistributionError` when the document lists no files,
    naming the version string so the ``V``-prefix trap is obvious from the
    message alone.
    """
    distribution = croissant.get("distribution") or []
    records = [
        FileRecord(
            name=str(entry.get("name") or ""),
            content_size=_parse_content_size(entry.get("contentSize")),
            encoding_format=entry.get("encodingFormat"),
            md5=entry.get("md5"),
            content_url=str(entry.get("contentUrl") or ""),
        )
        for entry in distribution
        if entry.get("contentUrl")
    ]
    if not records:
        sent = f" for version {version!r}" if version is not None else ""
        raise EmptyDistributionError(
            f"the Croissant record{sent} lists no downloadable files. "
            f"Science Data Bank returns HTTP 200 with an empty skeleton when the "
            f"version is sent without its 'V' prefix, so check that first."
        )
    return records


def filter_records(
    records: Iterable[FileRecord], predicate: Callable[[FileRecord], bool]
) -> list[FileRecord]:
    """Select records by a caller-supplied predicate."""
    return [record for record in records if predicate(record)]


def name_contains_any(tokens: Sequence[str]) -> Callable[[FileRecord], bool]:
    """Predicate matching any of ``tokens`` in a record's filename.

    The tokens come from configuration. Which provinces matter is a property of
    the study, not of the fetch layer, so no province name appears in this
    module.
    """
    lowered = [token.lower() for token in tokens]
    def predicate(record: FileRecord) -> bool:
        stem = record.stem.lower()
        return any(token in stem for token in lowered)
    return predicate


def md5_of(path: Path, *, chunk: int = _CHUNK) -> str:
    """MD5 of a file on disk, read in chunks."""
    digest = hashlib.md5()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            digest.update(block)
    return digest.hexdigest()


def is_already_fetched(record: FileRecord, destination: Path) -> bool:
    """True when ``destination`` exists and matches the record's MD5.

    A record with no published MD5 falls back to a size comparison, and says so
    by returning False when the size is unknown too, because an unverifiable
    file is not a fetched file.
    """
    if not destination.exists():
        return False
    if record.md5:
        return md5_of(destination) == record.md5.lower()
    if record.content_size is not None:
        return destination.stat().st_size == record.content_size
    return False


def download_record(
    record: FileRecord,
    destination: Path,
    *,
    timeout: float = DEFAULT_TIMEOUT,
    session: requests.Session | None = None,
    allowed_content_types: Sequence[str] = DEFAULT_ALLOWED_CONTENT_TYPES,
    chunk: int = _CHUNK,
) -> Path:
    """Download one record, verify it, and only then put it at ``destination``.

    Returns ``destination`` untouched when it already holds a matching file.

    The download goes to a sibling ``.part`` file and is renamed into place
    only after the content type, the byte count and the MD5 all check out, so a
    failure never leaves a partial or unverified file where a later step would
    read it as real.
    """
    destination = Path(destination)
    if is_already_fetched(record, destination):
        return destination

    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_suffix(destination.suffix + ".part")

    sess = session or requests.Session()
    response = sess.get(record.content_url, timeout=timeout, stream=True)
    response.raise_for_status()

    content_type = str(response.headers.get("Content-Type", "")).split(";")[0].strip().lower()
    if allowed_content_types and content_type not in [c.lower() for c in allowed_content_types]:
        raise UnexpectedContentType(
            f"{record.stem}: server answered HTTP 200 with Content-Type "
            f"{content_type!r}, which is not a data file. An HTML or JSON body "
            f"here is an error page served with a success status."
        )

    digest = hashlib.md5()
    written = 0
    try:
        with open(partial, "wb") as handle:
            for block in response.iter_content(chunk_size=chunk):
                if not block:
                    continue
                handle.write(block)
                digest.update(block)
                written += len(block)

        if record.content_size is not None and written != record.content_size:
            raise TruncatedDownload(
                f"{record.stem}: received {written:,} bytes but the record "
                f"declares {record.content_size:,}. Refusing to write a partial file."
            )

        if record.md5:
            got = digest.hexdigest()
            if got != record.md5.lower():
                raise ChecksumMismatch(
                    f"{record.stem}: MD5 {got} does not match the published "
                    f"{record.md5.lower()}. Refusing to write the file."
                )

        partial.replace(destination)
    finally:
        if partial.exists():
            partial.unlink()

    return destination


def plan(records: Sequence[FileRecord], destination_dir: Path) -> dict:
    """Describe what a fetch would do, without touching the network.

    Returns counts and byte totals split into what is already present and what
    would be downloaded, which is what the dry run reports.
    """
    destination_dir = Path(destination_dir)
    present, missing = [], []
    for record in records:
        target = destination_dir / record.stem
        (present if is_already_fetched(record, target) else missing).append(record)
    total = sum(r.content_size or 0 for r in records)
    return {
        "records": list(records),
        "present": present,
        "missing": missing,
        "total_bytes": total,
        "missing_bytes": sum(r.content_size or 0 for r in missing),
    }
