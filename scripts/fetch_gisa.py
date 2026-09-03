#!/usr/bin/env python3
"""Fetch the four GISA tiles covering the study box.

    python scripts/fetch_gisa.py                # report what would be fetched
    python scripts/fetch_gisa.py --download     # actually fetch

GISA is an independently built impervious-surface product, used here to test
whether the negative land-cover finding is an artefact of GAIA's known omission
error rather than a property of the methane field.

Two things about this route are worth knowing before running it. The documented
per-tile links go through Zenodo, which returns 403 at the network level from
this host, so the only reachable route is the whole 882 MB bundle from Wuhan
University over plain HTTP. And the bundle's filenames carry no version, no year
and no coordinate: 257 tiles named urban_1.tif to urban_257.tif. The tiles that
cover a given box therefore cannot be chosen by name and are selected here by
reading each member's georeferencing straight out of the archive, without
extracting it, which costs a header read per tile and no disk.

The archive is deleted after extraction. Free space is reported either side.
"""

from __future__ import annotations

import argparse
import shutil
import sys
import zipfile
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.fetch.common import FileRecord, digest_of, download_record  # noqa: E402


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{n:,.0f} B"
        n /= 1024.0
    return f"{n:,.1f} TB"


def tiles_covering(archive: Path, west: float, south: float,
                   east: float, north: float) -> list[str]:
    """Members whose georeferencing intersects the box, read without extracting.

    The filenames say nothing, so this opens each member through GDAL's zip
    virtual filesystem and reads only its header.
    """
    import rasterio

    names = [n for n in zipfile.ZipFile(archive).namelist() if n.endswith(".tif")]
    covering = []
    for name in sorted(names):
        with rasterio.open(f"/vsizip/{archive}/{name}") as src:
            b = src.bounds
            if b.left < east and b.right > west and b.bottom < north and b.top > south:
                covering.append(name)
    return covering


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(REPO / "config" / "sources.yml"))
    parser.add_argument("--source", default="gisa")
    parser.add_argument("--box", default="s5p",
                        help="config entry whose bounding_box selects the tiles")
    parser.add_argument("--dest", default=None)
    parser.add_argument("--keep-archive", action="store_true")
    parser.add_argument("--download", action="store_true")
    args = parser.parse_args(argv)

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))
    entry = config[args.source]
    box = config[args.box]["bounding_box"]
    dest = Path(args.dest) if args.dest else REPO / entry["destination"]

    print(f"  product   {entry['product']}")
    print(f"  url       {entry['url']}")
    print(f"  archive   {entry['archive']}  "
          f"({entry['archive_bytes']:,} B, {human(entry['archive_bytes'])})")
    print(f"  sha256    {entry['archive_sha256']}")
    print(f"  box       {box['west']} to {box['east']} E, "
          f"{box['south']} to {box['north']} N")
    print(f"  expected  {', '.join(entry['tiles'])}")
    print(f"  encoding  {entry['extent_2018_selector']} for 2018 extent; "
          f"values ascend from {entry['year_first_impervious_min']}")

    present = [t for t in entry["tiles"] if (dest / t).exists()]
    if len(present) == len(entry["tiles"]):
        print(f"\n  all {len(present)} tiles already in {dest}; nothing to do")
        return 0

    if not args.download:
        print("\n  dry run: nothing fetched. Pass --download to fetch "
              f"{human(entry['archive_bytes'])}.")
        return 0

    dest.mkdir(parents=True, exist_ok=True)
    archive = dest / entry["archive"]
    print(f"\n  free before {human(shutil.disk_usage(dest).free)}")
    if not archive.exists():
        record = FileRecord(name=entry["archive"], url=entry["url"],
                            size=entry["archive_bytes"], digest=None)
        download_record(record, archive)
    got = digest_of(archive, algorithm="sha256")
    print(f"  downloaded {archive.stat().st_size:,} B, sha256 {got}")
    if got != entry["archive_sha256"]:
        raise SystemExit(
            f"sha256 mismatch: expected {entry['archive_sha256']}, got {got}. "
            f"The distribution has changed; stopping rather than extracting it.")
    print("  sha256 matches the recorded digest")

    covering = tiles_covering(archive, box["west"], box["south"],
                              box["east"], box["north"])
    print(f"  {len(covering)} members intersect the box by their own "
          f"georeferencing: {', '.join(Path(c).name for c in covering)}")
    expected = sorted(entry["tiles"])
    if sorted(Path(c).name for c in covering) != expected:
        raise SystemExit(
            f"tile selection changed: config lists {expected}, the archive "
            f"gives {sorted(Path(c).name for c in covering)}")

    with zipfile.ZipFile(archive) as z:
        for member in covering:
            out = dest / Path(member).name
            with z.open(member) as src, open(out, "wb") as handle:
                shutil.copyfileobj(src, handle, 1024 * 1024)
            print(f"    extracted {out.name}  ({out.stat().st_size:,} B)")

    if not args.keep_archive:
        archive.unlink()
        print(f"  deleted {archive.name}")
    print(f"  free after {human(shutil.disk_usage(dest).free)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
