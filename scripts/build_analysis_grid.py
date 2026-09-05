#!/usr/bin/env python3
"""Join rice and impervious fractions onto the 2018 methane grid.

A thin wrapper over ``src.grid``. All arithmetic lives there.

    python scripts/build_analysis_grid.py                       # report only
    python scripts/build_analysis_grid.py --write
    python scripts/build_analysis_grid.py --rice-source scidb --write

One row per covered methane cell. The 96 uncovered cells cannot produce a row:
``CellRow`` refuses to construct with a zero sounding count, so the exclusion is
enforced by the type rather than by a filter at the end.

**Two denominators, deliberately.** Rice is masked by the union of the four
province polygons before any fraction is taken, because the rice rasters
declare no nodata and their 0 means both genuine non-rice land and
out-of-province background. GAIA is not masked, because it is a global product
whose 0 means non-urban everywhere and masking it would silently redefine
impervious fraction as a share of land in four particular provinces. The
consequence is that the two fractions have different denominators, and the two
coverage columns are what say so: a coastal cell may show impervious coverage
near 1.0 and rice coverage near 0.4. This is a real conflict between two
recorded constraints and is resolved here rather than hidden.

**Rice source.** ``--rice-source nesdc`` uses the FTP product, which carries the
double-season class but arrived under a personal-use grant that cannot be
scripted. ``--rice-source scidb`` uses the anonymous Science Data Bank product,
which is reproducible but single-season only. That looks like a trade of
reproducibility against completeness and mostly is not: for 2018 the two are the
same classification, and building the grid both ways changes only
``rice_fraction_combined``, in 190 of 927 rows. The committed table is built from
the FTP rasters for the extra column; a reader without the grant regenerates
every other column exactly. notes/decisions.md carries the pixel counts.
"""

from __future__ import annotations

import argparse
import csv
import glob
import sys
from pathlib import Path

import numpy as np
import rasterio
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.grid import cells as gc  # noqa: E402
from src.grid.cells import CellFraction, CellRow, UnobservedCell  # noqa: E402
from src.landcover import at_least, between, in_classes, load_zones  # noqa: E402
from src.methane.grid import GridSpec  # noqa: E402

#: GAIA encodes the year of first imperviousness counting downward from 2023,
#: so 2018 extent is value >= 5. See notes/decisions.md.
GAIA_EPOCH = 2023

#: GISA encodes the same quantity as GAIA in the opposite direction: values 1
#: to 37 are the years 1972 to 2019 counting UPWARD, and 0 is non-impervious.
#: Extent as of 2018 is the closed interval 1 to 36. See config/sources.yml.
GISA_YEARS = [1972, 1978] + list(range(1985, 2020))


def gisa_value_for(year: int) -> int:
    if year not in GISA_YEARS:
        raise SystemExit(f"GISA has no value for {year}; it encodes {GISA_YEARS}")
    return GISA_YEARS.index(year) + 1


def gisa_tile_bounds(path):
    """Nominal ten-degree extent of a GISA tile, from its own georeferencing.

    GISA filenames carry no coordinates, so the corner is recovered by rounding
    the tile's actual bounds to the nearest ten degrees. The tiles overlap by
    exactly one pixel on every shared edge, so without this the seams are
    counted twice, the same problem GAIA's thirty-metre merge buffer creates.
    """
    import rasterio

    with rasterio.open(path) as source:
        b = source.bounds
    west = round(b.left / 10.0) * 10.0
    south = round(b.bottom / 10.0) * 10.0
    return (west, south, west + 10.0, south + 10.0)

PROVINCES = ["Shanghai", "Zhejiang", "Anhui", "Jiangsu"]

FIELDS = ["centre_lat", "centre_lon", "sounding_count",
          "ch4_bias_corrected_ppb", "ch4_raw_ppb",
          "impervious_fraction", "impervious_coverage",
          "rice_fraction_single", "rice_fraction_combined", "rice_coverage",
          "province_share_outside",
          "share_anhui", "share_jiangsu", "share_shanghai", "share_zhejiang"]

#: The subset written for the GISA impervious comparison. That table exists to
#: carry a second impervious product on the same cells, and the other eleven
#: columns would duplicate analysis_grid_2018.csv, giving them a second place
#: to drift. The committed file was reduced by hand and the reduction was not
#: documented, so the recipe could not reproduce it; --impervious-only is that
#: reduction, made part of the script.
IMPERVIOUS_FIELDS = ["centre_lat", "centre_lon",
                     "impervious_fraction", "impervious_coverage"]


def gaia_tile_bounds(path: Path):
    """Nominal five-degree extent of a GAIA tile, from its filename.

    Tiles ship with a 30 m merge buffer and overlap; without this the shared
    edges are counted twice. Same rule as scripts/compute_urban_areas.py, which
    is the only other place GAIA's tiling is known about.
    """
    lon, lat = (int(part) for part in Path(path).stem.split("_")[-2:])
    return (float(lon), float(lat - 5), float(lon + 5), float(lat))


def province_of(path) -> str:
    """The province a rice file is named for: classified-<Province>-<year>-..."""
    return Path(path).stem.split("-")[1]


def rice_rasters(source: str, year: int) -> list[Path]:
    if source == "nesdc":
        found = glob.glob(
            f"{REPO}/data/raw/nesdc_rice/**/classified-*-{year}-rice-WGS84-v*.tif",
            recursive=True)
    else:
        found = glob.glob(
            f"{REPO}/data/raw/scidb_rice/**/classified-*-{year}-*-WGS84-v*.tif",
            recursive=True)
    wanted = [Path(p) for p in found
              if any(f"-{prov}-" in Path(p).name for prov in PROVINCES)]
    return sorted(wanted)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(REPO / "config" / "sources.yml"))
    parser.add_argument("--year", type=int, default=2018)
    parser.add_argument("--rice-source",
                        choices=("nesdc", "scidb", "glorice"), default="nesdc")
    parser.add_argument("--urban-source", choices=("gaia", "gisa"), default="gaia")
    parser.add_argument("--gisa", default=str(REPO / "data" / "raw" / "gisa"))
    parser.add_argument("--glorice", default=str(REPO / "data" / "raw" / "glorice"))
    parser.add_argument("--composite",
                        default=str(REPO / "data" / "processed" /
                                    "methane_composite_2018.tif"))
    parser.add_argument("--zones",
                        default=str(REPO / "data" / "reference" /
                                    "yrd_provinces.geojson"))
    parser.add_argument("--gaia", default=str(REPO / "data" / "raw" / "gaia"))
    parser.add_argument("--out", default=str(REPO / "data" / "processed" /
                                             "analysis_grid_2018.csv"))
    parser.add_argument("--impervious-only", action="store_true",
                        help="write only the two impervious columns, which is "
                             "the form impervious_gisa_2018.csv is committed in")
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))["s5p"]
    box_cfg = config["bounding_box"]
    spec = GridSpec(box_cfg["west"], box_cfg["south"], box_cfg["east"],
                    box_cfg["north"], config["grid_resolution_deg"])

    with rasterio.open(args.composite) as src:
        ch4_primary, ch4_raw, counts = src.read(1), src.read(2), src.read(3)
    covered = counts > 0
    print(f"  methane grid {spec.shape[0]} x {spec.shape[1]} = {spec.n_cells} cells; "
          f"{int(covered.sum())} covered, {int((~covered).sum())} excluded")

    zones = load_zones(args.zones)
    provinces = {p: zones[p] for p in PROVINCES}

    if args.urban_source == "gaia":
        tiles = sorted(Path(args.gaia).glob("GAIA_1985_2022_*.tif"))
        if not tiles:
            raise SystemExit(f"no GAIA tiles in {args.gaia}; run scripts/fetch_gaia.py")
        cutoff = GAIA_EPOCH - args.year
        selector, bounds_of = at_least(cutoff), gaia_tile_bounds
        note = f"value >= {cutoff}, counting downward from {GAIA_EPOCH}"
    else:
        tiles = sorted(Path(args.gisa).glob("urban_*.tif"))
        if not tiles:
            raise SystemExit(f"no GISA tiles in {args.gisa}; run scripts/fetch_gisa.py")
        selector = between(1, gisa_value_for(args.year))
        bounds_of, note = gisa_tile_bounds, f"{selector.description}, counting upward"
    print(f"  impervious: {len(tiles)} {args.urban_source.upper()} tiles, {note}, "
          f"NOT masked by province (0 means non-urban everywhere in a global product)")
    impervious = gc.fraction_over_grid(
        tiles, spec, selector, mask_geometry=None, clip_bounds_of=bounds_of)

    if args.rice_source == "glorice":
        single = combined = _glorice_fractions(args.glorice, args.year, spec)
        return _finish(args, spec, counts, ch4_primary, ch4_raw, impervious,
                       single, combined, provinces)

    rice = rice_rasters(args.rice_source, args.year)
    if not rice:
        raise SystemExit(f"no {args.rice_source} rice rasters for {args.year}")
    print(f"  rice: {len(rice)} {args.rice_source} rasters, each masked by the "
          f"province it is named for (0 means both non-rice and out-of-province, "
          f"and the files' boxes overlap)")
    for path in rice:
        print(f"    {path.name:<52} -> {province_of(path)}")
    own_province = lambda path: provinces[province_of(path)]  # noqa: E731
    single = gc.fraction_over_grid(rice, spec, in_classes([1]),
                                   mask_geometry=own_province)
    combined = gc.fraction_over_grid(rice, spec, in_classes([1, 2]),
                                     mask_geometry=own_province)

    return _finish(args, spec, counts, ch4_primary, ch4_raw, impervious,
                   single, combined, provinces)


def _glorice_fractions(directory, year, spec):
    """Rice fraction from GloRice, which stores hectares rather than classes."""
    import xarray as xr
    from rasterio.transform import from_origin

    path = Path(directory) / f"exten_phsc_{year}.nc"
    if not path.exists():
        raise SystemExit(f"no GloRice file at {path}; run scripts/fetch_glorice.py")
    dataset = xr.open_dataset(path)
    lat, lon = dataset["lat"].values, dataset["lon"].values
    transform = from_origin(float(lon[0]), float(lat[0]),
                            abs(float(lon[1] - lon[0])), abs(float(lat[1] - lat[0])))
    print(f"  rice: GloRice {year}, {dataset['area'].shape} at "
          f"{abs(float(lon[1] - lon[0])):.6f} degrees, hectares per cell, "
          f"apportioned by area share")
    print("        NOT masked by province: NaN means no rice, which is a value, "
          "so every cell gets a fraction and none is blank")
    # Hectares to square kilometres.
    return gc.value_sum_over_grid(dataset["area"].values, transform, spec,
                                  unit_scale=0.01)


def _finish(args, spec, counts, ch4_primary, ch4_raw, impervious,
            single, combined, provinces):
    shares = gc.province_shares(spec, provinces)

    rows, refused = [], 0
    for r in range(spec.shape[0]):
        lat = spec.north - (r + 0.5) * spec.resolution
        for c in range(spec.shape[1]):
            lon = spec.west + (c + 0.5) * spec.resolution
            try:
                rows.append(CellRow(
                    row=r, col=c, centre_lat=lat, centre_lon=lon,
                    sounding_count=int(counts[r, c]),
                    ch4_bias_corrected=float(ch4_primary[r, c]),
                    ch4_raw=float(ch4_raw[r, c]),
                    impervious=impervious[r][c],
                    rice_single=single[r][c],
                    rice_combined=combined[r][c],
                    province_shares=shares[r][c]))
            except UnobservedCell:
                refused += 1
    print(f"\n  built {len(rows)} rows; {refused} cells refused for zero soundings")

    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", newline="") as handle:
            fields = IMPERVIOUS_FIELDS if args.impervious_only else FIELDS
            writer = csv.DictWriter(handle, fieldnames=fields, restval="",
                                    extrasaction="ignore")
            writer.writeheader()
            for row in rows:
                writer.writerow(row.as_dict())
        print(f"  wrote {out}  ({out.stat().st_size:,} B)")
    else:
        print("  report only: nothing written. Pass --write to build the table.")

    _report(rows, spec)
    return 0


def _describe(name, values):
    finite = np.array([v for v in values if v is not None], dtype="float64")
    if not finite.size:
        print(f"  {name:<26} no values")
        return
    print(f"  {name:<26}n {finite.size:>4}  min {finite.min():.4f}  "
          f"median {np.median(finite):.4f}  max {finite.max():.4f}  "
          f"zero {int((finite == 0).sum()):>4}")


def _report(rows, spec):
    print("\n=== distributions ===")
    _describe("impervious fraction", [r.impervious.fraction for r in rows])
    _describe("rice fraction single", [r.rice_single.fraction for r in rows])
    _describe("rice fraction combined", [r.rice_combined.fraction for r in rows])
    print("\n=== coverage ===")
    for label, getter in (("impervious", lambda r: r.impervious.coverage),
                          ("rice", lambda r: r.rice_single.coverage)):
        vals = np.array([getter(r) for r in rows])
        print(f"  {label:<12} min {vals.min():.4f}  median {np.median(vals):.4f}  "
              f"max {vals.max():.4f}  below 0.99: {int((vals < 0.99).sum())}")
    print("\n=== provinces ===")
    multi = sum(1 for r in rows if len(r.province_shares) > 1)
    partly = sum(1 for r in rows if r.outside_provinces > 0.001)
    none = sum(1 for r in rows if not r.province_shares)
    print(f"  cells straddling more than one province : {multi}")
    print(f"  cells partly outside all four           : {partly}")
    print(f"  cells entirely outside all four         : {none}")
    _correlations(rows)


def _pairs(rows, left, right):
    """Rows where both quantities exist, as two aligned arrays."""
    a, b = [], []
    for row in rows:
        x, y = left(row), right(row)
        if x is None or y is None or not np.isfinite(x) or not np.isfinite(y):
            continue
        a.append(x); b.append(y)
    return np.array(a), np.array(b)


def _correlations(rows):
    """Descriptive association only.

    These are not a model and support no causal reading. Every one of them is
    confounded at least by the two denominators differing, by the 96 excluded
    cells being a systematic terrain gap rather than a random sample, and by
    cells being contiguous and therefore not independent observations.
    """
    from scipy.stats import pearsonr, spearmanr

    quantities = {
        "methane (bias corrected)": lambda r: r.ch4_bias_corrected,
        "impervious fraction": lambda r: r.impervious.fraction,
        "rice fraction single": lambda r: r.rice_single.fraction,
        "rice fraction combined": lambda r: r.rice_combined.fraction,
    }
    print("\n=== correlations (descriptive, not a model) ===")
    names = list(quantities)
    for i, left in enumerate(names):
        for right in names[i + 1:]:
            a, b = _pairs(rows, quantities[left], quantities[right])
            if a.size < 3:
                print(f"  {left} vs {right}: too few paired cells ({a.size})")
                continue
            r_p, p_p = pearsonr(a, b)
            r_s, p_s = spearmanr(a, b)
            print(f"  {left:<24} vs {right:<24} n {a.size:>4}  "
                  f"Pearson {r_p:+.3f} (p {p_p:.2e})  "
                  f"Spearman {r_s:+.3f} (p {p_s:.2e})")


if __name__ == "__main__":
    raise SystemExit(main())
