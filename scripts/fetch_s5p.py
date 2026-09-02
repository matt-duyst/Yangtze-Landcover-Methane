#!/usr/bin/env python3
"""Fetch Sentinel-5P Level 2 methane granules from the MEEO mirror.

A thin wrapper over ``src.fetch.s5p``. All logic lives there.

Dry run is the default, and downloading needs two flags rather than one:

    python scripts/fetch_s5p.py                          # cost estimate only
    python scripts/fetch_s5p.py --download --max-gb 5    # fetch, capped

Granules are 40 to 60 MB and a year of candidates runs to hundreds, so
``--download`` alone is not enough: ``--max-gb`` must also be given, and the
run stops before exceeding it. An invocation that forgets the cap reports a
plan instead of pulling tens of gigabytes.

The mirror publishes no usable checksum, so each granule is verified
structurally after download: it must open as netCDF4 and hold a PRODUCT group
with the expected variables. That is weaker than the MD5 check the figshare and
Science Data Bank routes get, and a granule that fails it is not written.
"""

from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.fetch import s5p  # noqa: E402


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{n:,.0f} B"
        n /= 1024.0
    return f"{n:,.1f} TB"


def as_date(value) -> dt.date:
    if isinstance(value, dt.date):
        return value
    return dt.date.fromisoformat(str(value))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(REPO / "config" / "sources.yml"))
    parser.add_argument("--source", default="s5p")
    parser.add_argument("--dest", default=None)
    parser.add_argument("--start", default=None, help="override start date")
    parser.add_argument("--end", default=None, help="override end date")
    parser.add_argument("--all-orbits", action="store_true",
                        help="do not restrict to orbits that could see the box")
    parser.add_argument("--keep-all-versions", action="store_true",
                        help="do not reduce to the highest processor version per orbit")
    parser.add_argument("--download", action="store_true")
    parser.add_argument("--max-gb", type=float, default=None,
                        help="hard cap on download volume; required with --download")
    parser.add_argument("--timeout", type=float, default=s5p.DEFAULT_TIMEOUT)
    args = parser.parse_args(argv)

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))[args.source]
    dest = Path(args.dest) if args.dest else REPO / config["destination"]
    box = config["bounding_box"]
    start = as_date(args.start or config["start_date"])
    end = as_date(args.end or config["end_date"])

    print(f"source      {args.source}")
    print(f"product     {config['product']}")
    print(f"mirror      {config['base_url']}  {config['stream']}/{config['product_type']}")
    print(f"box         {box['west']} to {box['east']} east, "
          f"{box['south']} to {box['north']} north")
    print(f"dates       {start} to {end}")
    print(f"destination {dest}")
    print()

    print("  listing the mirror ...", flush=True)
    every = s5p.list_range(start, end, stream=config["stream"],
                           product=config["product_type"],
                           base_url=config["base_url"], timeout=args.timeout)
    print(f"  {len(every)} keys listed")

    granules = every
    if not args.keep_all_versions:
        granules = s5p.latest_per_orbit(granules)
        print(f"  {len(granules)} after keeping the highest processor version per orbit")
    if not args.all_orbits:
        granules = [g for g in granules
                    if s5p.intersects_box(g, box["west"], box["east"])]
        print(f"  {len(granules)} after the overpass-time filter "
              f"(a SUPERSET: the filename carries no footprint, so this keeps "
              f"orbits that COULD have seen the box)")
    print()

    grouped = s5p.by_year(granules)
    print(f"  {'year':<6}{'granules':>10}{'volume':>16}{'on disk':>10}{'to fetch':>10}")
    total = have = 0
    for year, items in grouped.items():
        present = sum(1 for g in items if (dest / g.name).exists())
        size = s5p.volume(items)
        total += size
        have += present
        print(f"  {year:<6}{len(items):>10}{size:>13,} B{present:>10}"
              f"{len(items) - present:>10}")
    missing = [g for g in granules if not (dest / g.name).exists()]
    missing_bytes = s5p.volume(missing)
    print(f"  {'TOTAL':<6}{len(granules):>10}{total:>13,} B{have:>10}{len(missing):>10}")
    print()
    print(f"  total volume       {total:,} B ({human(total)})")
    print(f"  already on disk    {have} granules")
    print(f"  would download     {len(missing)} granules, {missing_bytes:,} B "
          f"({human(missing_bytes)})")
    if granules:
        mean = total / len(granules)
        print(f"  mean granule size  {mean:,.0f} B ({human(mean)})")

    if not args.download:
        print("\ndry run: nothing was downloaded. Pass --download together with "
              "--max-gb to fetch.")
        return 0

    if args.max_gb is None:
        print("\nrefusing to download without --max-gb. Granules are tens of "
              "megabytes each and a year of candidates runs to gigabytes; the "
              "cap is required so an accidental invocation cannot pull them all.")
        return 2

    cap = args.max_gb * 1024 ** 3
    if missing_bytes > cap:
        print(f"\n  {human(missing_bytes)} exceeds the --max-gb cap of "
              f"{human(cap)}; fetching until the cap is reached and stopping.")

    dest.mkdir(parents=True, exist_ok=True)
    fetched = fetched_bytes = 0
    for granule in missing:
        if fetched_bytes + granule.size > cap:
            print(f"  cap reached after {fetched} granules "
                  f"({human(fetched_bytes)}); stopping.")
            break
        s5p.download_granule(granule, dest / granule.name,
                             base_url=config["base_url"], timeout=args.timeout)
        fetched += 1
        fetched_bytes += granule.size
        print(f"  [{fetched}/{len(missing)}] {granule.name}  "
              f"{granule.size:,} B  netCDF structure verified", flush=True)
    print(f"\nfetched {fetched} granules, {fetched_bytes:,} B ({human(fetched_bytes)})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
