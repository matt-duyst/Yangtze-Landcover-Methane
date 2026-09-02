#!/usr/bin/env python3
"""Regenerate data/processed/urban_area_by_province.csv from GAIA.

A thin wrapper over ``src.landcover``. All arithmetic lives there.

    python scripts/compute_urban_areas.py            # compare, write nothing
    python scripts/compute_urban_areas.py --write    # regenerate the CSV
    python scripts/compute_urban_areas.py --gadm PATH_TO_GADM.json

Comparison is the default. The script prints every row that differs from the
committed file by more than a tolerance and refuses to write when anything
does, because a silent overwrite would destroy the evidence that something
changed.

Two things about the GADM rows. GADM 4.1 cannot be committed: its licence
forbids redistribution without permission, so twelve of the hundred and sixty
rows cannot be regenerated from committed inputs alone. Rather than drop them,
the script carries them forward from the existing CSV and says so, and will
regenerate them instead when a user supplies their own GADM file with --gadm.
Carried rows are labelled in the output so nobody mistakes them for
recomputed ones.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.landcover import load_zones, zonal_histogram  # noqa: E402

PROVINCES = ["Shanghai", "Zhejiang", "Anhui", "Jiangsu"]
YEARS = list(range(1985, 2022))

#: GAIA encodes the year a pixel first became impervious, counting downward
#: from the newest year: value 2 is 2021 and 38 is 1985 and before. See
#: notes/decisions.md, "Year-of-change products are version-dependent".
EPOCH = 2023

THESIS = {
    2000: {"Shanghai": 1211, "Zhejiang": 1752, "Anhui": 2326, "Jiangsu": 3008},
    2010: {"Shanghai": 3310, "Zhejiang": 6731, "Anhui": 4748, "Jiangsu": 10042},
    2018: {"Shanghai": 5121, "Zhejiang": 14957, "Anhui": 10217, "Jiangsu": 19430},
}

FIELDS = ["source", "year", "province", "urban_area_km2", "boundary",
          "thesis_urban_km2"]


def tile_clip_bounds(path: Path) -> tuple[float, float, float, float]:
    """The nominal 5-degree extent a GAIA tile is named for.

    Tiles ship with a 30 m merge buffer and therefore overlap; summing whole
    tiles double-counts every shared edge. The filename gives the upper-left
    corner as ``GAIA_1985_2022_<lon>_<lat>.tif``.
    """
    lon, lat = (int(part) for part in path.stem.split("_")[-2:])
    return (float(lon), float(lat - 5), float(lon + 5), float(lat))


def accumulate(tiles, zones):
    """Sum per-value areas for each zone across every tile."""
    totals = {name: {} for name in zones}
    for tile in tiles:
        histograms = zonal_histogram(tile, zones, clip_bounds=tile_clip_bounds(tile))
        for name, histogram in histograms.items():
            for value, area in histogram.area_km2_by_value.items():
                totals[name][value] = totals[name].get(value, 0.0) + area
    return totals


def series_from(totals):
    """Cumulative area per province per year from per-value areas."""
    rows = {}
    for name, by_value in totals.items():
        for year in YEARS:
            cutoff = EPOCH - year
            rows[(year, name)] = sum(
                area for value, area in by_value.items() if value >= cutoff
            )
    return rows


def build_rows(gaia_dir, zones_path, gadm_path, committed):
    tiles = sorted(Path(gaia_dir).glob("GAIA_1985_2022_*.tif"))
    if not tiles:
        raise SystemExit(f"no GAIA tiles in {gaia_dir}; run the GAIA fetch first")
    natural_earth = load_zones(zones_path)
    zones = {p: natural_earth[p] for p in PROVINCES}

    print(f"  mosaicking {len(tiles)} tiles with per-tile clip bounds")
    ne_series = series_from(accumulate(tiles, zones))

    rows, carried = [], []
    if gadm_path:
        gadm_zones = load_zones(gadm_path, name_field="NAME_1")
        selected = {p: gadm_zones[p] for p in PROVINCES}
        print(f"  regenerating GADM rows from {gadm_path}")
        gadm_totals = accumulate(tiles, selected)
        for year in (2000, 2010, 2018):
            for province in PROVINCES:
                cutoff = EPOCH - year
                area = sum(a for v, a in gadm_totals[province].items() if v >= cutoff)
                rows.append(dict(source="GAIA", year=str(year), province=province,
                                 urban_area_km2=f"{area:.1f}", boundary="gadm",
                                 thesis_urban_km2=THESIS[year][province]))
    else:
        for row in committed:
            if row["boundary"] == "gadm":
                rows.append(dict(row))
                carried.append((row["year"], row["province"]))

    for year in YEARS:
        for province in PROVINCES:
            rows.append(dict(
                source="GAIA", year=str(year), province=province,
                urban_area_km2=f"{ne_series[(year, province)]:.1f}",
                boundary="natural_earth",
                thesis_urban_km2=THESIS.get(year, {}).get(province, ""),
            ))
    return rows, carried


def read_csv(path):
    if not Path(path).exists():
        return []
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle))


def compare(new_rows, committed, tolerance):
    """Split the regenerated rows against the committed ones three ways.

    Disagreements block a write because they mean the pipeline and the record
    no longer agree. Additions do not: a first run against an empty file, or a
    newly configured year, is not a regression. Rows present in the committed
    file and absent from the regenerated set do block, because writing would
    lose them.
    """
    index = {(r["year"], r["province"], r["boundary"]): r for r in committed}
    differences, additions = [], []
    for row in new_rows:
        key = (row["year"], row["province"], row["boundary"])
        if key not in index:
            additions.append((key, float(row["urban_area_km2"])))
            continue
        was = float(index[key]["urban_area_km2"])
        now = float(row["urban_area_km2"])
        if was == 0 and now == 0:
            continue
        rel = abs(now - was) / max(abs(was), 1e-12)
        if rel > tolerance:
            differences.append((key, was, now, f"{100 * rel:.3f}%"))
    missing = set(index) - {(r["year"], r["province"], r["boundary"]) for r in new_rows}
    return differences, additions, sorted(missing)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--gaia", default=str(REPO / "data" / "raw" / "gaia"))
    parser.add_argument("--zones",
                        default=str(REPO / "data" / "reference" / "yrd_provinces.geojson"))
    parser.add_argument("--gadm", default=None,
                        help="optional GADM admin-1 file; GADM cannot be committed")
    parser.add_argument("--out",
                        default=str(REPO / "data" / "processed" / "urban_area_by_province.csv"))
    parser.add_argument("--tolerance", type=float, default=0.001,
                        help="relative difference treated as a match (default 0.1%%)")
    parser.add_argument("--write", action="store_true",
                        help="write the CSV; without this the script only compares")
    args = parser.parse_args(argv)

    committed = read_csv(args.out)
    rows, carried = build_rows(args.gaia, args.zones, args.gadm, committed)

    print(f"  built {len(rows)} rows "
          f"({sum(1 for r in rows if r['boundary'] == 'natural_earth')} natural_earth, "
          f"{sum(1 for r in rows if r['boundary'] == 'gadm')} gadm)")
    if carried:
        print(f"  {len(carried)} GADM rows carried forward unchanged, NOT regenerated: "
              f"GADM cannot be committed (licence forbids redistribution). "
              f"Pass --gadm to recompute them.")

    differences, additions, missing = compare(rows, committed, args.tolerance)
    if committed:
        print(f"\n  compared against {len(committed)} committed rows at "
              f"{100 * args.tolerance:.1f}% tolerance")
        if differences:
            print(f"  {len(differences)} row(s) differ:")
            for key, was, now, how in differences:
                print(f"    {key}  committed {was}  regenerated {now}  ({how})")
        else:
            print("  every row matches within tolerance")
        if additions:
            print(f"  {len(additions)} regenerated row(s) are not in the committed file:")
            for key, value in additions:
                print(f"    {key}  regenerated {value:,.1f}  (no committed counterpart)")
        if missing:
            print(f"  {len(missing)} committed row(s) absent from the regenerated set:")
            for key in missing:
                print(f"    {key}")
    else:
        print("  no committed file to compare against; every row is new")

    if not args.write:
        print("\ncomparison only: nothing written. Pass --write to regenerate.")
        return 0
    if differences or missing:
        print("\nrefusing to write: differences above tolerance are reported above.")
        return 1

    with open(args.out, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nwrote {len(rows)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
