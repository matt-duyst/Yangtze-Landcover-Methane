#!/usr/bin/env python3
"""Aggregate the NESDC rice classification to a display grid, by season.

    python scripts/compute_rice_extent.py            # report, write nothing
    python scripts/compute_rice_extent.py --write    # write into data/processed/

Three bands at 1/128 degree over the analysis lattice -- single-season rice,
double-season rice, and the share of each cell the product actually classified
-- plus a provincial totals table. Committed so that
`figures/landcover_regional.png` regenerates on a fresh clone; the rasters
themselves are 3.5 GB of gitignored `data/raw/`.

Same grid and same reasoning as `scripts/compute_urban_extent.py`: 1/128 degree
divides the 0.25 degree analysis cell exactly, 32 to a side, and the figure
averages to 1/64 for drawing because that is what the page resolves. The
fraction is stored rather than a class, so the display threshold stays in the
figure where display decisions belong.

**Each raster is masked by the province it is named for, and this is the whole
difficulty.** The four files declare no nodata, their 0 means both genuine
non-rice land and out-of-province background, and their bounding boxes overlap
heavily -- between 23 and 60 percent of each file's box lies outside its own
province. Masking every file by the union of the four assesses the shared
ground once per file: measured, that produced a cell at 2.94 times its own area
and a median single-season fraction of 0.079 against a correct 0.129. So the
mask is `fraction_over_grid`'s callable form, one province per file, and this
script asserts the assessed area back against the province polygons before it
writes anything.

**A third band, because absence has two meanings here.** The denominator is the
area a raster assessed, never the cell, so a cell the product did not reach
carries no fraction rather than a zero one. Anhui is the case that forces it:
every annual raster terminates classification at 33.3462 N and 115.2682 E to
within 22 metres, which is a processing boundary and not an absence of rice --
GloRice puts about 320 km2 of rice in the region NESDC leaves out. Band 3 is
what lets the figure draw that region as unclassified instead of as empty.
"""

from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import src.grid.cells as gc  # noqa: E402
from src.landcover import load_zones  # noqa: E402
from src.landcover.geometry import CHINA_ALBERS  # noqa: E402
from src.landcover.selectors import in_classes  # noqa: E402
from src.methane.grid import GridSpec  # noqa: E402

PROCESSED = REPO / "data" / "processed"
ZONES = REPO / "data" / "reference" / "yrd_provinces.geojson"

PROVINCES = ["Shanghai", "Zhejiang", "Anhui", "Jiangsu"]
YEAR = 2018

#: Display cells per degree. Matches `scripts/compute_urban_extent.py`.
CELLS_PER_DEGREE = 128

#: Stored value = fraction x this, so a stored number is a percentage.
FRACTION_SCALE = 100

#: The seasons, by the class values the product documents.
CLASSES = {"single": (1,), "double": (2,)}

#: How far the assessed area may fall short of the province polygon before the
#: script refuses to write. Anhui is legitimately short -- its rasters cover
#: 86.1 percent of the province -- so the floor is well below that, and what
#: the check is really for is the failure in the other direction: a union mask
#: assesses shared ground repeatedly and pushes the ratio above one.
COVERAGE_FLOOR = 0.80
COVERAGE_CEILING = 1.02


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def display_spec() -> GridSpec:
    """The display grid, from the analysis lattice."""
    from src.figures import geo
    extent = geo.lattice_extent(geo.study_spec())
    return GridSpec(extent.west, extent.south, extent.east, extent.north,
                    1.0 / CELLS_PER_DEGREE)


def province_of(path) -> str:
    """The province a rice file is named for: classified-<Province>-<year>-..."""
    return Path(path).stem.split("-")[1]


def rice_rasters(year: int = YEAR) -> list[Path]:
    found = glob.glob(
        f"{REPO}/data/raw/nesdc_rice/**/classified-*-{year}-rice-WGS84-v*.tif",
        recursive=True)
    wanted = [Path(p) for p in found
              if any(f"-{province}-" in Path(p).name for province in PROVINCES)]
    return sorted(wanted)


def polygon_areas(zones) -> dict:
    """Province polygon area in km2, on the equal-area conic used throughout."""
    import geopandas as gpd
    frame = gpd.GeoDataFrame(geometry=[zones[p] for p in PROVINCES],
                             crs="EPSG:4326").to_crs(CHINA_ALBERS)
    return {p: float(area) / 1e6
            for p, area in zip(PROVINCES, frame.geometry.area)}


def aggregate(spec: GridSpec, rasters, zones):
    """Per-province, per-season selected area, and per-province assessed area.

    One pass per raster per season, eight in all, and everything else is
    derived by summing rather than by reading again. The masks are
    `fraction_over_grid`'s callable form in spirit -- one province per file --
    because the files overlap; see the module docstring for what a union mask
    costs.
    """
    by_province = {}
    assessed = {}
    for raster in rasters:
        province = province_of(raster)
        mask = zones[province]
        by_province[province] = {}
        own = None
        for name, values in CLASSES.items():
            selected, seen = gc.accumulate_fraction(
                raster, spec, in_classes(values), mask_geometry=mask,
                selected=np.zeros(spec.shape, dtype="float64"),
                assessed=np.zeros(spec.shape, dtype="float64"))
            by_province[province][name] = selected
            # Both seasons assess the same ground, so the second pass is a
            # free check on the first rather than a second measurement.
            if own is not None and not np.allclose(own, seen):
                raise SystemExit(
                    f"{raster.name}: the two season passes disagree about "
                    f"which ground was assessed, which they cannot")
            own = seen
        assessed[province] = own
    return by_province, assessed


def combine(spec: GridSpec, by_province, assessed):
    """The four provinces summed into one grid per season, and one assessed."""
    selected = {name: np.zeros(spec.shape, dtype="float64") for name in CLASSES}
    total = np.zeros(spec.shape, dtype="float64")
    for province, seasons in by_province.items():
        for name, values in seasons.items():
            selected[name] += values
        total += assessed[province]
    return selected, total


def check_masking(per_province, zones) -> list[dict]:
    """Assessed area against the province polygons, before anything is written.

    The assertion the brief for this figure asked for, and it catches the
    specific failure that has already happened once: a union mask assesses
    ground shared between two files twice and drives the ratio above one.
    """
    areas = polygon_areas(zones)
    rows = []
    for province in PROVINCES:
        assessed_km2 = float(per_province[province].sum()) / 1e6
        ratio = assessed_km2 / areas[province]
        rows.append({"province": province,
                     "assessed_km2": assessed_km2,
                     "polygon_km2": areas[province],
                     "ratio": ratio})
    bad = [r for r in rows
           if not (COVERAGE_FLOOR <= r["ratio"] <= COVERAGE_CEILING)]
    if bad:
        detail = ", ".join(f"{r['province']} {r['ratio']:.3f}" for r in bad)
        raise SystemExit(
            f"assessed area is not the province area for: {detail}. A ratio "
            f"above one means the mask assessed shared ground more than once, "
            f"which is what masking each raster by its own province prevents.")
    return rows


def write_raster(spec, selected, assessed, path: Path) -> dict:
    """Three bands of uint8 percentages: single, double, and coverage."""
    import rasterio
    from rasterio.transform import from_bounds

    from src.grid.cells import cell_areas_m2

    cell_m2 = cell_areas_m2(spec)
    bands = [selected["single"] / cell_m2, selected["double"] / cell_m2,
             assessed / cell_m2]
    scaled = [np.clip(np.rint(band * FRACTION_SCALE), 0,
                      FRACTION_SCALE).astype("uint8") for band in bands]
    transform = from_bounds(spec.west, spec.south, spec.east, spec.north,
                            spec.n_cols, spec.n_rows)
    with rasterio.open(
            path, "w", driver="GTiff", height=spec.n_rows, width=spec.n_cols,
            count=3, dtype="uint8", crs="EPSG:4326", transform=transform,
            compress="deflate", predictor=1, tiled=True) as dst:
        for index, description in enumerate(
                ("single-season rice percent of cell",
                 "double-season rice percent of cell",
                 "percent of cell the product classified")):
            dst.write(scaled[index], index + 1)
            dst.set_band_description(index + 1, description)
        dst.update_tags(product=f"NESDC rice {YEAR}, 10 m, per province",
                        scale=f"stored value / {FRACTION_SCALE} = fraction",
                        bands="single,double,coverage")
    return {"shape": spec.shape,
            "mean_percent": {name: round(float(scaled[i].mean()), 3)
                             for i, name in enumerate(("single", "double",
                                                       "coverage"))}}


def write_totals(per_province, selected_by_province, checks, path: Path) -> dict:
    """Provincial rice area by season, with the assessed denominator beside it."""
    rows = []
    for check in checks:
        province = check["province"]
        for season in CLASSES:
            area = float(selected_by_province[province][season].sum()) / 1e6
            rows.append({
                "province": province,
                "season": season,
                "rice_area_km2": f"{area:.1f}",
                "assessed_km2": f"{check['assessed_km2']:.1f}",
                "polygon_km2": f"{check['polygon_km2']:.1f}",
                "assessed_over_polygon": f"{check['ratio']:.4f}",
                "rice_share_of_assessed": f"{area / check['assessed_km2']:.5f}",
            })
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    return {"rows": len(rows)}


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

    spec = display_spec()
    zones = load_zones(ZONES)
    zones = {p: zones[p] for p in PROVINCES}
    rasters = rice_rasters()
    if len(rasters) != len(PROVINCES):
        raise SystemExit(
            f"expected one {YEAR} rice raster per province, found "
            f"{len(rasters)}: {[r.name for r in rasters]}")
    print(f"grid {spec.shape[0]} x {spec.shape[1]} at 1/{CELLS_PER_DEGREE} degree")
    for raster in rasters:
        print(f"  {raster.name:<52} -> masked by {province_of(raster)}")

    by_province, per_province = aggregate(spec, rasters, zones)
    selected, assessed = combine(spec, by_province, per_province)
    checks = check_masking(per_province, zones)
    print("\n  assessed area against the province polygons:")
    for check in checks:
        print(f"    {check['province']:9s} {check['assessed_km2']:9,.0f} km2 "
              f"of {check['polygon_km2']:9,.0f} = {check['ratio']:.4f}")

    print(f"\nwriting into {destination}")
    raster_path = destination / f"rice_extent_{YEAR}.tif"
    detail = write_raster(spec, selected, assessed, raster_path)
    print(f"  {raster_path.name}")
    for key, value in detail.items():
        print(f"    {key:16s} {value}")
    print(f"    bytes            {raster_path.stat().st_size:,}")
    print(f"    sha256           {digest(raster_path)}")

    totals_path = destination / f"rice_extent_totals_{YEAR}.csv"
    detail = write_totals(per_province, by_province, checks, totals_path)
    print(f"  {totals_path.name}")
    for key, value in detail.items():
        print(f"    {key:16s} {value}")
    print(f"    bytes            {totals_path.stat().st_size:,}")
    print(f"    sha256           {digest(totals_path)}")
    return 0


def _directory(where: str) -> Path:
    """``where`` if it names a directory, otherwise the directory holding it."""
    path = Path(where)
    return path if path.suffix == "" else path.parent


if __name__ == "__main__":
    raise SystemExit(main())
