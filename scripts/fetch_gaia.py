#!/usr/bin/env python3
"""Fetch the nine GAIA tiles covering the study box.

A thin wrapper over ``src.fetch.figshare`` and ``src.fetch.manifest``. All
logic lives there; this file parses arguments, reads configuration and prints.

Dry run is the default. Downloading requires ``--download`` explicitly.

    python scripts/fetch_gaia.py                # report what would be fetched
    python scripts/fetch_gaia.py --download     # actually fetch

The archive is 2.3 GB and is not internally addressable over this route, so the
whole thing must be fetched to reach any tile. It is deleted immediately after
extraction, which is why free space is reported either side.

Extraction goes to a staging directory first. The tiles are hashed there and
compared against the digests already in data/manifest.json before anything is
moved into place, so a changed distribution is reported rather than silently
replacing verified files.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.fetch import figshare as fs  # noqa: E402
from src.fetch import manifest as mf  # noqa: E402

MANIFEST_KEY = "gaia_1985_2022"


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{n:,.0f} B"
        n /= 1024.0
    return f"{n:,.1f} TB"


def free_space(path: Path) -> int:
    return shutil.disk_usage(path).free


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(REPO / "config" / "sources.yml"))
    parser.add_argument("--source", default="gaia")
    parser.add_argument("--dest", default=None)
    parser.add_argument("--manifest", default=str(REPO / "data" / "manifest.json"))
    parser.add_argument("--download", action="store_true",
                        help="perform the fetch; without this only a plan is printed")
    parser.add_argument("--timeout", type=float, default=fs.DEFAULT_TIMEOUT)
    args = parser.parse_args(argv)

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))[args.source]
    dest = Path(args.dest) if args.dest else REPO / config["destination"]
    tiles = list(config["tiles"])

    article_id, version = fs.article_id_from_doi(config["doi"])
    print(f"source      {args.source}")
    print(f"product     {config['product']}")
    print(f"doi         {config['doi']}  -> article {article_id} version {version}")
    print(f"licence     {config['licence']}")
    print(f"destination {dest}")
    print()

    article = fs.fetch_article(article_id, version=version,
                               api_base=config.get("api_base", fs.DEFAULT_API_BASE),
                               timeout=args.timeout)
    records = fs.parse_files(article)
    wanted = fs.filter_records(records, fs.name_contains_any([config["archive"]]))
    if len(wanted) != 1:
        raise SystemExit(
            f"expected exactly one archive named {config['archive']!r}; "
            f"found {[r.name for r in wanted]}")
    archive_record = wanted[0]

    print(f"  record holds {len(records)} files; licence on record: "
          f"{fs.licence_of(article)}")
    print(f"  archive {archive_record.name}  {archive_record.content_size:,} B "
          f"({human(archive_record.content_size)})  md5 {archive_record.md5}")
    print(f"  the archive is NOT internally addressable over this route, so the "
          f"full {human(archive_record.content_size)} must be fetched to reach "
          f"any tile")
    print()
    print(f"  {len(tiles)} members would be extracted:")
    for name in tiles:
        on_disk = dest / name
        state = "present" if on_disk.exists() else "absent"
        size = f"{on_disk.stat().st_size:,} B" if on_disk.exists() else "-"
        print(f"    {name:<32} {size:>16}  {state}")

    present_bytes = sum((dest / n).stat().st_size for n in tiles if (dest / n).exists())
    print()
    print(f"  extracted tiles already on disk: {present_bytes:,} B "
          f"({human(present_bytes)})")
    print(f"  peak additional space needed:    "
          f"{archive_record.content_size:,} B for the archive, freed after extraction")
    print(f"  free space now:                  {human(free_space(dest.parent if dest.exists() else REPO))}")

    if not args.download:
        print("\ndry run: nothing was downloaded and nothing was written. "
              "Pass --download to fetch.")
        return 0

    before = free_space(REPO)
    dest.mkdir(parents=True, exist_ok=True)
    archive_path = dest / archive_record.stem
    print(f"\n  downloading {archive_record.stem} ...", flush=True)
    fs.download_record(archive_record, archive_path, timeout=args.timeout)
    archive_sha = fs.digest_of(archive_path, algorithm="sha256")
    print(f"  md5 verified against the figshare record")
    print(f"  archive sha256 {archive_sha}")

    staging = dest / "_staging"
    if staging.exists():
        shutil.rmtree(staging)
    wanted_set = set(tiles)
    taken = fs.extract_members(archive_path, staging,
                               lambda name: Path(name).name in wanted_set,
                               overwrite=True)
    print(f"  extracted {len(taken)} members to staging")

    archive_path.unlink()
    print(f"  archive deleted")

    computed = {f"gaia/{m.path.name}": (m.bytes, m.sha256) for m in taken}
    manifest = mf.load(args.manifest)
    entry = manifest.get(MANIFEST_KEY)
    if entry is None:
        raise SystemExit(f"{args.manifest} has no {MANIFEST_KEY!r} entry to update")

    comparisons = mf.check_files(entry, computed)
    print("\n  tile checksums against data/manifest.json:")
    for c in comparisons:
        name = c.path.rsplit("/", 1)[-1]
        print(f"    {name:<32} {c.status}")
    bad = mf.mismatches(comparisons)
    if bad:
        print(f"\n  {len(bad)} tile(s) DIFFER from the recorded digests. The "
              f"distributed archive has changed. Staging kept at {staging}; "
              f"nothing was moved into place and the manifest was not written.")
        return 1

    for member in taken:
        target = dest / member.path.name
        member.path.replace(target)
    shutil.rmtree(staging, ignore_errors=True)
    print(f"  {len(taken)} tiles moved into {dest}")

    archive_status = mf.fill_archive_digest(
        entry, sha256=archive_sha, size=archive_record.content_size)
    summary = mf.update_files(entry, computed)
    if archive_status == "MISMATCH":
        print(f"\n  the recorded archive sha256 differs from the fetched one; "
              f"leaving it untouched and not writing the manifest.")
        return 1
    mf.save(manifest, args.manifest)
    print(f"  manifest archive sha256: {archive_status}")
    print(f"  manifest files: {len(summary['unchanged'])} unchanged, "
          f"{len(summary['filled'])} filled, {len(summary['added'])} added")

    after = free_space(REPO)
    print(f"\n  free space before {human(before)}  ->  after {human(after)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
