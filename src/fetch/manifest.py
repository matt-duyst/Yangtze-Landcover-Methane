"""Reading, checking and updating data/manifest.json.

The manifest is the record of what was fetched and what it hashed to. Its value
depends entirely on never being quietly rewritten: an entry that silently
adopts whatever is on disk records nothing.

So the update path here is conservative. A new entry, or a field that was null,
is filled in. A field that already holds a value and disagrees with a fresh
computation is *not* overwritten; :func:`check_files` reports the disagreement
and the caller is expected to stop. For a published archive that should be
immutable, a changed checksum means the distribution changed, and that is a
finding rather than a routine update.
"""

from __future__ import annotations

import collections
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping


@dataclass(frozen=True)
class ChecksumComparison:
    """One file's recorded digest against a freshly computed one."""

    path: str
    recorded: str | None
    computed: str | None
    recorded_bytes: int | None = None
    computed_bytes: int | None = None

    @property
    def status(self) -> str:
        if self.recorded is None:
            return "new"
        if self.computed is None:
            return "absent"
        return "match" if self.recorded.lower() == self.computed.lower() else "MISMATCH"

    @property
    def ok(self) -> bool:
        return self.status in ("match", "new")


def load(path: str | Path) -> dict:
    path = Path(path)
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"),
                      object_pairs_hook=collections.OrderedDict)


def save(manifest: Mapping, path: str | Path) -> None:
    path = Path(path)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
                    encoding="utf-8")


def check_files(
    entry: Mapping,
    computed: Mapping[str, tuple[int, str]],
) -> list[ChecksumComparison]:
    """Compare an entry's recorded file digests against fresh ones.

    ``computed`` maps a manifest ``path`` to ``(bytes, sha256)``. Files present
    in the entry but absent from ``computed`` are reported as ``absent`` rather
    than dropped.
    """
    recorded = {f["path"]: f for f in entry.get("files", [])}
    comparisons = []
    for path in sorted(set(recorded) | set(computed)):
        was = recorded.get(path, {})
        now = computed.get(path)
        comparisons.append(
            ChecksumComparison(
                path=path,
                recorded=was.get("sha256"),
                computed=now[1] if now else None,
                recorded_bytes=was.get("bytes"),
                computed_bytes=now[0] if now else None,
            )
        )
    return comparisons


def mismatches(comparisons: Iterable[ChecksumComparison]) -> list[ChecksumComparison]:
    return [c for c in comparisons if c.status == "MISMATCH"]


def fill_archive_digest(entry: dict, *, sha256: str, size: int | None = None) -> str:
    """Record an archive digest, refusing to change one that is already set.

    Returns ``"filled"``, ``"unchanged"`` or ``"MISMATCH"``. A null field is
    what this exists to fill; a populated field that disagrees is a finding and
    is left alone for the caller to report.
    """
    archive = entry.setdefault("archive", {})
    existing = archive.get("sha256")
    if existing is None:
        archive["sha256"] = sha256
        if size is not None:
            archive["bytes"] = size
        return "filled"
    if existing.lower() == sha256.lower():
        return "unchanged"
    return "MISMATCH"


def update_files(entry: dict, computed: Mapping[str, tuple[int, str]]) -> dict:
    """Fill missing per-file digests, leaving disagreeing ones untouched.

    Returns a summary keyed by outcome. Call :func:`check_files` first and stop
    on a mismatch; this will not resolve one.
    """
    summary = {"filled": [], "unchanged": [], "mismatched": [], "added": []}
    by_path = {f["path"]: f for f in entry.setdefault("files", [])}
    for path, (size, digest) in computed.items():
        record = by_path.get(path)
        if record is None:
            entry["files"].append(
                collections.OrderedDict(path=path, bytes=size, sha256=digest))
            summary["added"].append(path)
            continue
        if record.get("sha256") is None:
            record["sha256"] = digest
            record["bytes"] = size
            summary["filled"].append(path)
        elif record["sha256"].lower() == digest.lower():
            summary["unchanged"].append(path)
        else:
            summary["mismatched"].append(path)
    entry["files"].sort(key=lambda f: f["path"])
    return summary
