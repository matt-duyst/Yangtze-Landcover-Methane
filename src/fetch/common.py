"""Machinery shared by every fetch module.

Science Data Bank and figshare differ in how they describe a record and agree
in how a file must be handled once described: check the media type, count the
bytes, check the digest, and only then let the file appear at the path a later
step will read. That second half is here, so a new source implements only its
own metadata parsing.

The verification order matters and is the reason this is shared rather than
reimplemented. Content type is checked first because an HTML error page served
with HTTP 200 is the cheapest failure to detect; byte count second because a
truncated body is next cheapest; digest last because it costs a full read. A
file that fails any of them is never written to its destination, only to a
sibling ``.part`` that is removed on the way out.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable, Sequence

import requests

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

_CHUNK = 1 << 20


class FetchError(RuntimeError):
    """Base class for every failure a fetch module raises deliberately."""


class ChecksumMismatch(FetchError):
    """A downloaded or existing file does not match its published digest."""


class UnexpectedContentType(FetchError):
    """The server answered 200 with something that is not a data file."""


class TruncatedDownload(FetchError):
    """Fewer bytes arrived than the record declared."""


@dataclass(frozen=True)
class FileRecord:
    """One file in a published record, however that record describes itself.

    ``digest`` and ``digest_algorithm`` are whatever the publisher supplies:
    Science Data Bank and figshare both publish MD5, but the field is not named
    for it so a source that publishes SHA-256 needs no new type.
    """

    name: str
    content_size: int | None
    encoding_format: str | None
    digest: str | None
    content_url: str
    digest_algorithm: str = "md5"

    @property
    def stem(self) -> str:
        """Filename without directories, for use as a destination name."""
        return self.name.rsplit("/", 1)[-1]

    @property
    def md5(self) -> str | None:
        """The digest when it is an MD5, else None.

        Both current sources publish MD5 and callers read this by name. A
        source publishing something else returns None here rather than a digest
        that is not what the caller asked for.
        """
        return self.digest if self.digest_algorithm == "md5" else None


def digest_of(path: Path, *, algorithm: str = "md5", chunk: int = _CHUNK) -> str:
    """Digest of a file on disk, read in chunks."""
    hasher = hashlib.new(algorithm)
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(chunk), b""):
            hasher.update(block)
    return hasher.hexdigest()


def md5_of(path: Path, *, chunk: int = _CHUNK) -> str:
    """MD5 of a file on disk. Retained because both current sources publish MD5."""
    return digest_of(path, algorithm="md5", chunk=chunk)


def is_already_fetched(record: FileRecord, destination: Path) -> bool:
    """True when ``destination`` exists and matches the record's digest.

    A record with no published digest falls back to a size comparison, and
    returns False when the size is unknown too, because an unverifiable file is
    not a fetched file.
    """
    destination = Path(destination)
    if not destination.exists():
        return False
    if record.digest:
        return digest_of(destination, algorithm=record.digest_algorithm) == \
            record.digest.lower()
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
    only after the content type, the byte count and the digest all check out,
    so a failure never leaves a partial or unverified file where a later step
    would read it as real.
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

    hasher = hashlib.new(record.digest_algorithm)
    written = 0
    try:
        with open(partial, "wb") as handle:
            for block in response.iter_content(chunk_size=chunk):
                if not block:
                    continue
                handle.write(block)
                hasher.update(block)
                written += len(block)

        if record.content_size is not None and written != record.content_size:
            raise TruncatedDownload(
                f"{record.stem}: received {written:,} bytes but the record "
                f"declares {record.content_size:,}. Refusing to write a partial file."
            )

        if record.digest:
            got = hasher.hexdigest()
            if got != record.digest.lower():
                raise ChecksumMismatch(
                    f"{record.stem}: {record.digest_algorithm} {got} does not match "
                    f"the published {record.digest.lower()}. Refusing to write the file."
                )

        partial.replace(destination)
    finally:
        if partial.exists():
            partial.unlink()

    return destination


def filter_records(
    records: Iterable[FileRecord], predicate: Callable[[FileRecord], bool]
) -> list[FileRecord]:
    """Select records by a caller-supplied predicate."""
    return [record for record in records if predicate(record)]


def name_contains_any(tokens: Sequence[str]) -> Callable[[FileRecord], bool]:
    """Predicate matching any of ``tokens`` in a record's filename.

    The tokens come from configuration. Which provinces or years matter is a
    property of the study, not of the fetch layer, so no such name appears in
    any fetch module.
    """
    lowered = [token.lower() for token in tokens]

    def predicate(record: FileRecord) -> bool:
        stem = record.stem.lower()
        return any(token in stem for token in lowered)

    return predicate


def plan(records: Sequence[FileRecord], destination_dir: Path) -> dict:
    """Describe what a fetch would do, without touching the network."""
    destination_dir = Path(destination_dir)
    present, missing = [], []
    for record in records:
        target = destination_dir / record.stem
        (present if is_already_fetched(record, target) else missing).append(record)
    return {
        "records": list(records),
        "present": present,
        "missing": missing,
        "total_bytes": sum(r.content_size or 0 for r in records),
        "missing_bytes": sum(r.content_size or 0 for r in missing),
    }
