#!/usr/bin/env python3
"""Fetch the Science Data Bank rice rasters for the configured provinces.

A thin wrapper over ``src.fetch.scidb``. All logic lives there; this file
parses arguments, reads configuration and prints.

Dry run is the default. Downloading requires ``--download`` explicitly, so an
accidental invocation reports a plan instead of pulling gigabytes.

    python scripts/fetch_rice.py                 # report what would be fetched
    python scripts/fetch_rice.py --download      # actually fetch
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.fetch import scidb  # noqa: E402


def human(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{n:,} B"
        n /= 1024.0
    return f"{n:,.1f} TB"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(REPO / "config" / "sources.yml"))
    parser.add_argument("--source", default="scidb_rice", help="key in sources.yml")
    parser.add_argument("--dest", default=None, help="override the configured destination")
    parser.add_argument(
        "--download",
        action="store_true",
        help="perform the download; without this the script only reports a plan",
    )
    parser.add_argument("--timeout", type=float, default=scidb.DEFAULT_TIMEOUT)
    args = parser.parse_args(argv)

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))[args.source]
    dest = Path(args.dest) if args.dest else REPO / config["destination"]

    version = scidb.require_versioned(config["version"])
    print(f"source      {args.source}")
    print(f"product     {config['product']}")
    print(f"doi         {config['doi']}")
    print(f"dataset id  {config['dataset_id']}")
    print(f"version     {version}")
    print(f"licence     {config['licence']}")
    print(f"destination {dest}")
    print()

    croissant = scidb.fetch_croissant(
        config["dataset_id"], version,
        base_url=config.get("base_url", scidb.DEFAULT_BASE_URL),
        timeout=args.timeout,
    )
    every = scidb.parse_distribution(croissant, version=version)
    provinces = config["provinces"]
    selected = scidb.filter_records(every, scidb.name_contains_any(provinces))

    print(f"record holds {len(every)} files; {len(selected)} match "
          f"{', '.join(provinces)}")
    print()

    report = scidb.plan(selected, dest)
    width = max((len(r.stem) for r in selected), default=0)
    for record in sorted(selected, key=lambda r: r.stem):
        state = "present" if record in report["present"] else "would fetch"
        size = f"{record.content_size:,}" if record.content_size is not None else "unknown"
        print(f"  {record.stem:<{width}}  {size:>14} B  {record.md5 or '-':<32}  {state}")

    print()
    print(f"  selected      {len(selected):>4} files  {report['total_bytes']:>15,} B  "
          f"({human(report['total_bytes'])})")
    print(f"  already here  {len(report['present']):>4} files")
    print(f"  to download   {len(report['missing']):>4} files  {report['missing_bytes']:>15,} B  "
          f"({human(report['missing_bytes'])})")

    if not args.download:
        print("\ndry run: nothing was downloaded. Pass --download to fetch.")
        return 0

    print()
    for i, record in enumerate(sorted(report["missing"], key=lambda r: r.stem), 1):
        target = dest / record.stem
        print(f"[{i}/{len(report['missing'])}] {record.stem} ...", end="", flush=True)
        scidb.download_record(record, target, timeout=args.timeout)
        print(" verified")
    print(f"\ndone: {len(report['missing'])} files fetched and MD5-verified into {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
