#!/usr/bin/env python3
"""Fetch the GloRice years the study needs.

A thin wrapper over ``src.fetch.figshare`` and ``src.fetch.manifest``, matching
scripts/fetch_gaia.py in shape. All logic lives there.

Dry run is the default; downloading requires ``--download``.

    python scripts/fetch_glorice.py               # report what would be fetched
    python scripts/fetch_glorice.py --download    # actually fetch

The archive holds one netCDF per year for 1961 to 2021 and the study needs
seven of them, so only those are extracted and the 148 MB archive is deleted
afterwards. Extraction goes to a staging directory and is checked against any
digests already in data/manifest.json before anything is moved into place.
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

MANIFEST_KEY = "glorice_phsc_ex"


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{n:,.0f} B"
        n /= 1024.0
    return f"{n:,.1f} TB"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(REPO / "config" / "sources.yml"))
    parser.add_argument("--source", default="glorice")
    parser.add_argument("--dest", default=None)
    parser.add_argument("--manifest", default=str(REPO / "data" / "manifest.json"))
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--timeout", type=float, default=fs.DEFAULT_TIMEOUT)
    args = parser.parse_args(argv)

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))[args.source]
    dest = Path(args.dest) if args.dest else REPO / config["destination"]
    years = list(config["years"])

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
    print(f"  the archive holds one netCDF per year for 1961 to 2021; "
          f"{len(years)} will be extracted and the rest discarded")
    print()
    print(f"  years from config: {years}")
    for year in years:
        target = dest / f"exten_phsc_{year}.nc"
        state = "present" if target.exists() else "absent"
        size = f"{target.stat().st_size:,} B" if target.exists() else "-"
        print(f"    exten_phsc_{year}.nc {size:>18}  {state}")

    if not args.download:
        print("\ndry run: nothing was downloaded and nothing was written. "
              "Pass --download to fetch.")
        return 0

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
    taken = fs.extract_members(archive_path, staging, fs.year_selector(years),
                               overwrite=True)
    print(f"  extracted {len(taken)} members to staging")
    archive_path.unlink()
    print("  archive deleted")

    computed = {f"glorice/{m.path.name}": (m.bytes, m.sha256) for m in taken}
    manifest = mf.load(args.manifest)
    entry = manifest.get(MANIFEST_KEY)
    if entry is None:
        raise SystemExit(f"{args.manifest} has no {MANIFEST_KEY!r} entry to update")

    comparisons = mf.check_files(entry, computed)
    print("\n  member checksums against data/manifest.json:")
    for c in comparisons:
        print(f"    {c.path.rsplit('/', 1)[-1]:<24} {c.status}")
    bad = mf.mismatches(comparisons)
    if bad:
        print(f"\n  {len(bad)} member(s) DIFFER from the recorded digests. The "
              f"distributed archive has changed. Staging kept at {staging}; "
              f"nothing moved into place and the manifest not written.")
        return 1

    for member in taken:
        member.path.replace(dest / member.path.name)
    shutil.rmtree(staging, ignore_errors=True)
    print(f"  {len(taken)} members moved into {dest}")

    archive_status = mf.fill_archive_digest(entry, sha256=archive_sha)
    if archive_status == "MISMATCH":
        print("\n  the recorded archive sha256 differs from the fetched one; "
              "leaving it untouched and not writing the manifest.")
        return 1
    summary = mf.update_files(entry, computed)
    mf.save(manifest, args.manifest)
    print(f"  manifest archive sha256: {archive_status}")
    print(f"  manifest files: {len(summary['unchanged'])} unchanged, "
          f"{len(summary['filled'])} filled, {len(summary['added'])} added")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
