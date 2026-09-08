#!/usr/bin/env python3
"""Clip the native-resolution land-cover window the resolution figure draws.

    python scripts/clip_landcover_window.py            # report, write nothing
    python scripts/clip_landcover_window.py --write    # write into data/processed/

Three small rasters, at the products' own resolutions and with their own pixel
values, over one 5.7 by 5.6 km window. Committed because the products are
900 MB and 3.5 GB of gitignored `data/raw/`, and because a figure whose whole
claim is that it shows native pixels should not be reachable only on the
machine that has them.

**The values are the products' own, not a mask.** The impervious rasters carry
the year code and the figure applies `src.landcover.selectors` to them, so the
selector that decides what counts is the same object in the figure, in the
provincial totals, and in the aggregation to the display grid. Committing a
boolean here would move that decision out of the code and into a file nobody
would re-examine.

**The window.** 118.44 to 118.49 east, 31.3248 to 31.3582 north: 5.7 by 3.7 km
on the eastern edge of Wuhu, in Anhui, on the south bank of the Yangtze. What
it had to satisfy, and what was rejected:

* **Both classes present, and abundant.** 23.9 percent of the window is
  impervious under GISA and 34.2 percent is rice, of which 4.9 points are
  double-season. A window that is nearly all one thing shows a reader a
  texture rather than a boundary.
* **An aspect the figure can lay out.** Its height is set so that it draws in
  the same proportion as the three-by-two block of analysis cells the figure
  puts beside it, which is what lets four panels share one grid instead of one
  of them standing 0.9 cm taller than the rest.
* **Double-season rice present.** Only two of the four provinces carry the
  class -- Anhui at 1.0 percent of pixels and Zhejiang at 0.4, against none at
  all in Jiangsu and Shanghai -- so a window in Jiangsu or Shanghai could not
  show a distinction the figure needs to make. Seven cities were scored across
  both provinces; Wuhu won on the balance of the three classes.
* **Wholly inside one province.** The NESDC rasters declare no nodata and 0
  means both real non-rice land and out-of-province background, so a window
  straddling a boundary would draw two different things in one colour. Every
  candidate was tested with `Anhui.contains(window)` rather than by eye.
* **Wholly inside one analysis cell.** The window sits in the 0.25 degree cell
  centred at 31.325 N, 118.425 E, which is what lets the figure put the native
  pixels and the number they are aggregated into on the same page.

The study area figure's detail window, 121.30 to 122.05 east over the Yangtze
mouth, was considered and does not serve here. It was chosen for a land
fraction of 0.58, because that figure needed a land-water boundary; this one
needs an urban-rice boundary, it is in Jiangsu and Shanghai where there is no
double-season class, and at 0.75 degrees it is thirteen times too wide to draw
a 10 m pixel.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.landcover.selectors import at_least, between  # noqa: E402

RAW = REPO / "data" / "raw"
PROCESSED = REPO / "data" / "processed"

#: The window, on no particular grid: it is a place, not a subdivision.
WEST, EAST = 118.44, 118.49
SOUTH, NORTH = 31.3248, 31.3582

#: The province whose rice raster covers it, and which contains it entirely.
PROVINCE = "Anhui"
YEAR = 2018

#: Which raw file each output comes from, and what its values mean.
SOURCES = {
    "landcover_window_impervious_gisa.tif": {
        "glob": "gisa/urban_206.tif",
        "meaning": "GISA year code: 0 non-impervious, 1..37 the year of first "
                   "imperviousness counting up from 1972",
        "resolution_m": 30,
    },
    "landcover_window_impervious_gaia.tif": {
        "glob": "gaia/GAIA_1985_2022_115_35.tif",
        "meaning": "GAIA year code: 0 non-urban, 2..38 the year of first "
                   "imperviousness counting down from 2021",
        "resolution_m": 30,
    },
    "landcover_window_rice_nesdc.tif": {
        "glob": f"nesdc_rice/*{YEAR}*/**/classified-{PROVINCE}-{YEAR}-*.tif",
        "meaning": "NESDC rice class: 0 non-rice, 1 single-season, "
                   "2 double-season. No nodata is declared.",
        "resolution_m": 10,
    },
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clip(source: Path, out: Path) -> dict:
    """The window at the source's own resolution, nothing resampled."""
    import rasterio
    from rasterio.windows import from_bounds

    with rasterio.open(source) as src:
        window = from_bounds(WEST, SOUTH, EAST, NORTH, src.transform)
        data = src.read(1, window=window)
        transform = src.window_transform(window)
        profile = src.profile
    profile.update(height=data.shape[0], width=data.shape[1], count=1,
                   transform=transform, compress="deflate", driver="GTiff",
                   tiled=False)
    profile.pop("blockxsize", None)
    profile.pop("blockysize", None)
    with rasterio.open(out, "w", **profile) as dst:
        dst.write(data, 1)
    return {"shape": data.shape,
            "values": {int(v): int(c) for v, c in
                       zip(*np.unique(data, return_counts=True))}}


def _directory(where: str) -> Path:
    """``where`` if it names a directory, otherwise the directory holding it."""
    path = Path(where)
    return path if path.suffix == "" else path.parent


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument(
        "--out", default=None,
        help="write beside this path. The recipe verifier hands a script the "
             "path of the one artefact it is checking, and a script that "
             "writes several writes them all into that directory.")
    args = parser.parse_args(argv)

    destination = (_directory(args.out) if args.out
                   else PROCESSED if args.write else Path(tempfile.mkdtemp()))
    destination.mkdir(parents=True, exist_ok=True)
    print(f"window {WEST} to {EAST} E, {SOUTH} to {NORTH} N, in {PROVINCE}")
    print(f"writing into {destination}")

    for name, spec in SOURCES.items():
        matches = sorted(RAW.glob(spec["glob"]))
        if not matches:
            raise SystemExit(f"no source for {name} matching {spec['glob']}")
        out = destination / name
        detail = clip(matches[0], out)
        rows, cols = detail["shape"]
        metres = spec["resolution_m"]
        print(f"  {name}")
        print(f"    from             {matches[0].relative_to(REPO)}")
        print(f"    native pixels    {cols} x {rows} at {metres} m")
        if "rice" in name:
            total = sum(detail["values"].values())
            for value, label in ((1, "single-season"), (2, "double-season")):
                count = detail["values"].get(value, 0)
                print(f"    class {value} {label:14s} "
                      f"{count:>9,} px, {100 * count / total:5.2f}%")
        else:
            import rasterio
            with rasterio.open(out) as src:
                block = src.read(1)
            selector = (between(1, 36) if "gisa" in name
                        else at_least(2023 - YEAR))
            print(f"    impervious       {selector.description}, "
                  f"{100 * selector(block).mean():.2f}% of the window")
        print(f"    bytes            {out.stat().st_size:,}")
        print(f"    sha256           {digest(out)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
