#!/usr/bin/env python3
"""Fetch the Copernicus DEM GLO-90 tiles covering the study box.

    python scripts/fetch_copernicus_dem.py             # report what it would fetch
    python scripts/fetch_copernicus_dem.py --download  # actually fetch

Into `data/raw/copernicus_dem/`, which is gitignored. What is committed is the
shaded relief derived from these by `scripts/build_map_reference.py`, not the
elevation model: 80 tiles are 408 MB and the figure needs a 2 MB raster.

**The bucket is `copernicus-dem-90m`, not `copernicus-dem-30m`.** Both exist on
AWS Open Data and both serve the same `readme.html` without credentials -- the
two files are byte-identical -- which makes it easy to read the readme from one
and then look for GLO-90 tiles in the other, where they are not. `10` in a tile
name is the arc-second spacing of GLO-30 and `30` is GLO-90's; the bucket name
is in metres and the tile name is in arc seconds, so the two numbers for one
product are never the same.

Ocean areas have no tiles at all, which the readme states and which is the
reason this script does not treat a missing tile as an error: it lists the
bucket's own `tileList.txt` and fetches the intersection with the study box.
Twenty of the hundred one-degree tiles over the padded box are absent and all
twenty are offshore, which `build_map_reference.py` fills with zero.

Licence: free of charge for any use, and **attribution is required**. The
notice is quoted in `build_map_reference.py` and in `data/manifest.json`.
"""

from __future__ import annotations

import argparse
import re
import sys
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

BUCKET = "https://copernicus-dem-90m.s3.amazonaws.com"
TILE_LIST = f"{BUCKET}/tileList.txt"
DEST = REPO / "data" / "raw" / "copernicus_dem"

#: The padded study box, matching `build_map_reference.CLIP`. Whole degrees,
#: because tiles are whole-degree.
WEST, EAST = 114, 123
SOUTH, NORTH = 26, 35

_NAME = re.compile(r"Copernicus_DSM_COG_30_N(\d\d)_00_E(\d\d\d)_00_DEM")


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if abs(n) < 1024 or unit == "GB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{n:,.0f} B"
        n /= 1024.0
    return f"{n:,.1f} GB"


def tile_list(url: str = TILE_LIST) -> list[str]:
    """Every tile the bucket declares. The file is CRLF; strip it."""
    with urllib.request.urlopen(url, timeout=120) as response:
        text = response.read().decode("utf-8")
    return [line.strip() for line in text.splitlines() if line.strip()]


def covering(names, west=WEST, east=EAST, south=SOUTH, north=NORTH):
    """Tiles whose one-degree square falls in the box, in a stable order."""
    out = []
    for name in names:
        match = _NAME.fullmatch(name)
        if match is None:
            continue
        lat, lon = int(match.group(1)), int(match.group(2))
        if south <= lat <= north and west <= lon <= east:
            out.append((lat, lon, name))
    return [name for _, _, name in sorted(out)]


def fetch(name: str, dest: Path) -> int:
    """Download one tile through a temporary, so a partial file is never left.

    The same rule the figure exporter follows and for the same reason: on a
    rerun a truncated file looks exactly like a complete one.
    """
    target = dest / f"{name}.tif"
    if target.exists() and target.stat().st_size:
        return 0
    url = f"{BUCKET}/{name}/{name}.tif"
    partial = target.with_suffix(".tif.part")
    with urllib.request.urlopen(url, timeout=300) as response:
        partial.write_bytes(response.read())
    partial.replace(target)
    return target.stat().st_size


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--dest", default=str(DEST))
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args(argv)

    dest = Path(args.dest)
    names = covering(tile_list())
    span = (EAST - WEST + 1) * (NORTH - SOUTH + 1)
    print(f"{len(names)} of {span} one-degree tiles exist over "
          f"{WEST}-{EAST + 1} E, {SOUTH}-{NORTH + 1} N")
    print(f"the other {span - len(names)} are ocean, which the bucket does not "
          f"tile; they are filled with zero downstream")
    if not args.download:
        print(f"\nwould fetch into {dest}; pass --download to do it")
        return 0

    dest.mkdir(parents=True, exist_ok=True)
    total = 0
    for i, name in enumerate(names, 1):
        total += fetch(name, dest)
        print(f"  [{i:>3}/{len(names)}] {name}")
    print(f"\n{human(total)} fetched into {dest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
