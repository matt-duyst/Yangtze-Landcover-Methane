#!/usr/bin/env python3
"""Aggregate GAIA and GISA to a display grid, as impervious fraction by year.

    python scripts/compute_urban_extent.py            # report, write nothing
    python scripts/compute_urban_extent.py --write    # write into data/processed/

Two rasters, one per product, three bands each: the fraction of the display
cell that was impervious by 2000, by 2010 and by 2018. Committed so that
`figures/urban_change.png` regenerates on a fresh clone; the products
themselves are 900 MB of gitignored `data/raw/`.

**Why a fraction and not a class.** A 30 m product cannot be drawn over 7.75
degrees at native resolution -- that is 880 million pixels against a panel that
resolves about a million -- so something has to be aggregated, and the question
is what. Storing the fraction keeps the aggregation reversible and leaves the
display decision where display decisions belong, in the figure module, which
states the threshold it draws at. Storing a class here would bake a cartographic
choice into a data product and make it unrecoverable.

**Why 1/128 degree.** It divides the 0.25 degree analysis cell exactly, 32 to a
side, so a display cell is a clean subdivision of the unit the analysis
consumes rather than an unrelated grid. It is 0.0078125 degrees, about 720 m
here, which is 992 by 1056 cells over the study lattice -- a little more than
the 874 pixels a 7.4 cm panel resolves at 300 dpi, which is the headroom a
resampler wants.

**The selectors come from `src.landcover.selectors`, not from thresholds
written here.** The two products encode the year in opposite directions and
getting one backwards does not fail loudly: it inverts the urbanisation
history, turning the oldest core into the newest expansion, and still produces
a plausible map. GAIA counts down from the newest year, so extent is
``at_least(2023 - year)``. GISA counts up from the oldest and uses 0 for
non-impervious, so extent is ``between(1, code)`` over a value-to-year table
that is not annual at its start: 1 is 1972, 2 is 1978, and 3 onward is 1985
onward, one per year. Both conventions are in `notes/decisions.md`.

Aggregation is exact rather than resampled. Each display cell is read at 32 by
32 sub-samples aligned to its own bounds, nearest-neighbour so no value is
invented, the selector is applied, and the mean is taken. Nearest-neighbour at
1/4096 degree slightly oversamples a 30 m grid, by a factor of 1.10, which
duplicates pixels and does not create them.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.figures import geo  # noqa: E402
from src.landcover import load_zones, zonal_histogram  # noqa: E402
from src.landcover.selectors import at_least, between  # noqa: E402

RAW = REPO / "data" / "raw"
PROCESSED = REPO / "data" / "processed"

#: Display cells per degree. See the module docstring.
CELLS_PER_DEGREE = 128
#: Sub-samples per display cell, per axis, for the exact aggregation.
SUBSAMPLE = 32

YEARS = (2000, 2010, 2018)

#: GAIA's epoch: year = EPOCH - value. From ReadMe-GAIA.txt, and the same
#: constant `scripts/compute_urban_areas.py` uses.
GAIA_EPOCH = 2023

#: GISA's value-to-year table is not annual at its start: 1 is 1972, 2 is 1978,
#: and from 3 onward it runs one per year from 1985. So value = year - 1982 for
#: any year this figure draws.
GISA_CODES = {2000: 18, 2010: 28, 2018: 36}

PRODUCTS = {
    "gaia": {
        "tiles": "gaia/GAIA_1985_2022_*.tif",
        "selector": lambda year: at_least(GAIA_EPOCH - year),
        "product": "GAIA 1985-2022, 30 m",
    },
    "gisa": {
        "tiles": "gisa/urban_*.tif",
        "selector": lambda year: between(1, GISA_CODES[year]),
        "product": "GISA 1972-2019, 30 m",
    },
}


PROVINCES = ["Shanghai", "Zhejiang", "Anhui", "Jiangsu"]

#: Where the committed provincial totals live, for the agreement column.
COMMITTED = {
    "gaia": (PROCESSED / "urban_area_by_province.csv", "natural_earth"),
    "gisa": (PROCESSED / "urban_area_by_province_gisa.csv", "natural_earth"),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_grid():
    """Bounds and shape of the display grid, from the analysis lattice."""
    extent = geo.lattice_extent(geo.study_spec())
    cols = round((extent.east - extent.west) * CELLS_PER_DEGREE)
    rows = round((extent.north - extent.south) * CELLS_PER_DEGREE)
    return extent, rows, cols


def aggregate(name: str, work: Path, rows_at_a_time: int = 16):
    """Impervious fraction per display cell, one band per year."""
    import rasterio
    from rasterio.enums import Resampling
    from rasterio.windows import from_bounds

    spec = PRODUCTS[name]
    tiles = sorted(RAW.glob(spec["tiles"]))
    if not tiles:
        raise SystemExit(f"no {name} tiles under {RAW}; fetch them first")
    vrt = work / f"{name}.vrt"
    subprocess.run(["gdalbuildvrt", "-q", "-overwrite", str(vrt)]
                   + [str(t) for t in tiles], check=True)

    extent, rows, cols = display_grid()
    step = 1.0 / CELLS_PER_DEGREE
    out = np.zeros((len(YEARS), rows, cols), dtype="float32")
    selectors = [spec["selector"](year) for year in YEARS]

    with rasterio.open(vrt) as src:
        for start in range(0, rows, rows_at_a_time):
            stop = min(start + rows_at_a_time, rows)
            north = extent.north - start * step
            south = extent.north - stop * step
            window = from_bounds(extent.west, south, extent.east, north,
                                 src.transform)
            block = src.read(
                1, window=window, boundless=True, fill_value=0,
                out_shape=((stop - start) * SUBSAMPLE, cols * SUBSAMPLE),
                resampling=Resampling.nearest)
            for index, selector in enumerate(selectors):
                mask = selector(block).reshape(
                    stop - start, SUBSAMPLE, cols, SUBSAMPLE)
                out[index, start:stop] = mask.mean(axis=(1, 3))
    return out, extent, rows, cols


#: Stored value = fraction x this. 100, so the stored number is the percentage
#: and a hand-check against the products needs no arithmetic. Finer steps buy
#: nothing -- the figure draws a threshold, not a gradient -- and cost real
#: bytes: at 200 the pair of files is 2.65 MB, at 100 it is 1.87 MB, because
#: what is being compressed is mostly the low-order noise.
FRACTION_SCALE = 100


def write(name: str, fractions, extent, rows, cols, path: Path) -> dict:
    """Write the three bands as uint8 percentages.

    uint8 rather than float32 because the file is committed and the figure
    draws a threshold from it. `predictor=1` rather than 2, measured: a
    horizontal predictor helps smooth data and hurts this, which is noisy at
    the pixel scale, by about 12 percent.
    """
    import rasterio
    from rasterio.transform import from_bounds as transform_from_bounds

    scaled = np.clip(np.rint(fractions * FRACTION_SCALE),
                     0, FRACTION_SCALE).astype("uint8")
    transform = transform_from_bounds(extent.west, extent.south, extent.east,
                                      extent.north, cols, rows)
    with rasterio.open(
            path, "w", driver="GTiff", height=rows, width=cols,
            count=len(YEARS), dtype="uint8", crs=geo.GEOGRAPHIC,
            transform=transform, compress="deflate", predictor=1,
            tiled=True) as dst:
        for index, year in enumerate(YEARS):
            dst.write(scaled[index], index + 1)
            dst.set_band_description(
                index + 1, f"impervious percent by {year}")
        dst.update_tags(product=PRODUCTS[name]["product"],
                        scale=f"stored value / {FRACTION_SCALE} = fraction",
                        years=",".join(str(y) for y in YEARS))
    return {
        "shape": (rows, cols),
        "mean_fraction": {year: round(float(fractions[i].mean()), 5)
                          for i, year in enumerate(YEARS)},
    }


def nominal_bounds(path: Path) -> tuple[float, float, float, float]:
    """The whole-degree box a tile is named for, from its georeferencing.

    Both products ship tiles with a merge buffer, so tiles overlap and summing
    whole tiles double-counts every shared edge. GAIA's filename carries its
    corner and `compute_urban_areas.py` reads it from there; GISA's filenames
    carry nothing at all -- 257 tiles named urban_1 to urban_257 -- so the box
    is recovered by rounding the bounds, which are within a pixel of whole
    degrees in every tile here.
    """
    import rasterio
    with rasterio.open(path) as src:
        left, bottom, right, top = src.bounds
    return (round(left), round(bottom), round(right), round(top))


def provincial_totals(name: str, zones):
    """Exact per-province area for each year, by the same route GAIA's table took.

    `zonal_histogram` rather than the display grid: the display grid agrees
    with it to better than 0.1 percent, which is a useful check and not a
    substitute, and a number that goes in a table and gets quoted in a caption
    should come from the exact computation.
    """
    spec = PRODUCTS[name]
    tiles = sorted(RAW.glob(spec["tiles"]))
    totals = {province: {} for province in zones}
    for tile in tiles:
        histograms = zonal_histogram(tile, zones,
                                     clip_bounds=nominal_bounds(tile))
        for province, histogram in histograms.items():
            for value, area in histogram.area_km2_by_value.items():
                totals[province][value] = (
                    totals[province].get(value, 0.0) + area)
    out = {}
    for year in YEARS:
        selector = spec["selector"](year)
        values = np.arange(0, 256, dtype="int32")
        keep = set(values[selector(values)].tolist())
        for province in zones:
            out[(year, province)] = sum(
                area for value, area in totals[province].items()
                if int(value) in keep)
    return out


def _committed_totals(name: str) -> dict:
    """Provincial totals already in the repository, for the agreement column."""
    import csv
    path, boundary = COMMITTED[name]
    if not path.exists():
        return {}
    out = {}
    with path.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row.get("boundary") != boundary:
                continue
            out[(int(row["year"]), row["province"])] = float(
                row["urban_area_km2"])
    return out


def write_totals(path: Path) -> dict:
    """One table, both products, three years, four provinces.

    It does not replace `urban_area_by_province_gisa.csv`, which is registered
    `unregenerable` and carries only 2018. It sits beside it and states its
    agreement with it, so the figure has a regenerable source for every number
    it draws and the older file's provenance is left alone.
    """
    import csv

    zones = load_zones(REPO / "data" / "reference" / "yrd_provinces.geojson")
    zones = {province: zones[province] for province in PROVINCES}
    rows, checked = [], []
    for name in PRODUCTS:
        totals = provincial_totals(name, zones)
        committed = _committed_totals(name)
        for year in YEARS:
            for province in PROVINCES:
                area = totals[(year, province)]
                was = committed.get((year, province))
                if was is not None:
                    checked.append(abs(area - was) / was)
                rows.append({
                    "source": name.upper(), "year": year, "province": province,
                    "urban_area_km2": f"{area:.1f}",
                    "boundary": "natural_earth",
                    "committed_km2": "" if was is None else f"{was:.1f}",
                    "relative_difference":
                        "" if was is None else f"{(area - was) / was:+.5f}",
                })
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return {"rows": len(rows),
            "checked_against_committed": len(checked),
            "worst_relative_difference":
                f"{max(checked):.2e}" if checked else "none"}


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
    print(f"writing into {destination}")
    with tempfile.TemporaryDirectory() as tmp:
        for name in PRODUCTS:
            path = destination / f"urban_extent_{name}.tif"
            fractions, extent, rows, cols = aggregate(name, Path(tmp))
            detail = write(name, fractions, extent, rows, cols, path)
            print(f"  {path.name}")
            for key, value in detail.items():
                print(f"    {key:16s} {value}")
            print(f"    bytes            {path.stat().st_size:,}")
            print(f"    sha256           {digest(path)}")
    totals = destination / "urban_extent_totals.csv"
    detail = write_totals(totals)
    print(f"  {totals.name}")
    for key, value in detail.items():
        print(f"    {key:28s} {value}")
    print(f"    bytes                        {totals.stat().st_size:,}")
    print(f"    sha256                       {digest(totals)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
