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

This module holds only what is specific to that route: DOI resolution, the
Croissant request, and parsing. Verification and downloading live in
``src.fetch.common``, which figshare uses too, and are re-exported here so
existing callers keep working.

One behaviour of the endpoint will silently produce wrong results and is
guarded in code rather than described in a comment: the ``version`` parameter
must carry its ``V`` prefix. ``version=V8`` returns the real record;
``version=8`` returns HTTP 200 and a syntactically valid Croissant document
with every field blank and an empty ``distribution``. A caller who trusts the
status code gets an empty file list and no error.

No credentials appear in this module and none are needed. The NESDC FTP grant
covering the same data is personal-use and is deliberately not scripted.
"""

from __future__ import annotations

import re

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

#: Public Croissant export. The ``/public/`` segment is what makes it anonymous.
DEFAULT_BASE_URL = "https://www.scidb.cn/api/gin-sdb-croissant/public/exportCroissant"

#: DOI resolver. Answers a redirect to the record page, whose query string
#: carries the dataset id.
DEFAULT_DOI_RESOLVER = "https://doi.org"

_DATASET_ID_RE = re.compile(r"dataSetId=([0-9a-fA-F]{32})")
_CONTENT_SIZE_RE = re.compile(r"^\s*(\d+)\s*(?:B|bytes?)?\s*$", re.IGNORECASE)


class ScidbError(FetchError):
    """Base class for failures specific to this route."""


class EmptyDistributionError(ScidbError):
    """The Croissant document parsed but listed no files.

    Almost always the ``V``-prefix trap rather than an empty record.
    """


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
            digest=entry.get("md5"),
            content_url=str(entry.get("contentUrl") or ""),
            digest_algorithm="md5",
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
