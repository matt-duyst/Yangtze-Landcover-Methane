#!/usr/bin/env python3
"""Regenerate the GloRice rows of data/processed/rice_area_by_province.csv.

A thin wrapper over ``src.landcover``. All arithmetic lives there.

    python scripts/compute_rice_areas.py            # compare, write nothing
    python scripts/compute_rice_areas.py --write    # regenerate the CSV

Comparison is the default and the script refuses to write when anything
differs beyond tolerance.

GloRice is not a categorical raster. Its cells hold hectares of rice per
5-arcmin cell, so a provincial total is an area-weighted sum of values rather
than a count of selected pixels, and it uses ``zonal_value_sum`` rather than
``zonal_area``. At 5 arcmin one cell is roughly 9 km across and a provincial
boundary cuts through many of them, so cells are apportioned by the fraction
inside the province instead of being taken or dropped whole.

The committed table also holds eight SPAM rows. SPAM 2020 is behind a Dataverse
guestbook form that cannot be scripted, no SPAM fetch module exists, and the
processed README already records that SPAM is not used in analysis. Those rows
are therefore carried forward unchanged and labelled, on the same principle as
the GADM rows in compute_urban_areas.py: not regenerable is recorded, not
hidden by deletion.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
import xarray as xr
import yaml
from rasterio.transform import from_origin

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.landcover import load_zones, zonal_value_sum  # noqa: E402

PROVINCES = ["Shanghai", "Zhejiang", "Anhui", "Jiangsu"]

#: GloRice cells are hectares; one hectare is 0.01 square kilometres.
HECTARES_TO_KM2 = 0.01

THESIS = {
    "2000": {"Shanghai": 1123, "Zhejiang": 5983, "Anhui": 19651, "Jiangsu": 15505},
    "2010": {"Shanghai": 577, "Zhejiang": 6028, "Anhui": 22977, "Jiangsu": 18825},
    "2018": {"Shanghai": 536, "Zhejiang": 4463, "Anhui": 17430, "Jiangsu": 16038},
}

FIELDS = ["source", "year", "province", "rice_area_km2", "thesis_pppm_km2"]


def transform_of(dataset: xr.Dataset):
    """Affine transform of a regular lat/lon netCDF grid."""
    lon = np.asarray(dataset["lon"].values, dtype="float64")
    lat = np.asarray(dataset["lat"].values, dtype="float64")
    dx = float(abs(lon[1] - lon[0]))
    dy = float(abs(lat[1] - lat[0]))
    # cell edges, not centres: GloRice's coordinates are the upper-left corners
    return from_origin(float(lon[0]), float(lat[0]), dx, dy)


def glorice_rows(glorice_dir, zones_path, years, variable="area"):
    zones_all = load_zones(zones_path)
    zones = {p: zones_all[p] for p in PROVINCES}
    rows = []
    for year in years:
        path = Path(glorice_dir) / f"exten_phsc_{year}.nc"
        if not path.exists():
            raise SystemExit(
                f"{path} is missing. Fetch GloRice first; see config/sources.yml "
                f"and src/fetch/figshare.py."
            )
        with xr.open_dataset(path) as dataset:
            results = zonal_value_sum(
                dataset[variable].values, transform_of(dataset), zones,
                unit_scale=HECTARES_TO_KM2, label=f"GloRice {variable} {year}",
            )
        for result in results:
            rows.append(dict(
                source="GloRice", year=str(year), province=result.zone,
                rice_area_km2=f"{result.area_km2:.1f}",
                thesis_pppm_km2=THESIS.get(str(year), {}).get(result.zone, ""),
            ))
        print(f"  {year}: " + "  ".join(
            f"{r.zone} {r.area_km2:,.1f}" for r in results))
    return rows


def read_csv(path):
    if not Path(path).exists():
        return []
    with open(path, newline="") as handle:
        return list(csv.DictReader(handle))


def compare(new_rows, committed, tolerance):
    index = {(r["source"], r["year"], r["province"]): r for r in committed}
    differences, additions = [], []
    for row in new_rows:
        key = (row["source"], row["year"], row["province"])
        if key not in index:
            additions.append((key, float(row["rice_area_km2"])))
            continue
        was = float(index[key]["rice_area_km2"])
        now = float(row["rice_area_km2"])
        rel = abs(now - was) / max(abs(was), 1e-12)
        if rel > tolerance:
            differences.append((key, was, now, f"{100 * rel:.3f}%"))
    return differences, additions


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(REPO / "config" / "sources.yml"))
    parser.add_argument("--glorice", default=None)
    parser.add_argument("--zones",
                        default=str(REPO / "data" / "reference" / "yrd_provinces.geojson"))
    parser.add_argument("--out",
                        default=str(REPO / "data" / "processed" / "rice_area_by_province.csv"))
    parser.add_argument("--tolerance", type=float, default=0.001)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))["glorice"]
    glorice_dir = args.glorice or str(REPO / config["destination"])
    years = config["years"]

    committed = read_csv(args.out)
    print(f"  GloRice years from config: {years}")
    rows = glorice_rows(glorice_dir, args.zones, years)

    carried = [r for r in committed if r["source"] != "GloRice"]
    if carried:
        sources = sorted({r["source"] for r in carried})
        print(f"\n  {len(carried)} rows carried forward unchanged, NOT regenerated "
              f"({', '.join(sources)}): SPAM 2020 is behind a Dataverse guestbook "
              f"form that cannot be scripted and no SPAM fetch module exists. "
              f"The processed README records that SPAM is not used in analysis.")

    differences, additions = compare(rows, committed, args.tolerance)
    print(f"\n  compared {len(rows)} regenerated rows against "
          f"{sum(1 for r in committed if r['source'] == 'GloRice')} committed "
          f"GloRice rows at {100 * args.tolerance:.1f}% tolerance")
    if differences:
        print(f"  {len(differences)} row(s) differ:")
        for key, was, now, how in differences:
            print(f"    {key}  committed {was}  regenerated {now}  ({how})")
    else:
        print("  every comparable row matches within tolerance")
    if additions:
        print(f"  {len(additions)} regenerated row(s) are not in the committed file:")
        for key, value in additions:
            print(f"    {key}  regenerated {value:,.1f}  (no committed counterpart)")

    if not args.write:
        print("\ncomparison only: nothing written. Pass --write to regenerate.")
        return 0
    if differences:
        print("\nrefusing to write: differences above tolerance are reported above.")
        return 1

    order = {p: i for i, p in enumerate(PROVINCES)}
    rows.sort(key=lambda r: (r["source"], r["year"], order[r["province"]]))
    carried.sort(key=lambda r: (r["source"], r["year"], order[r["province"]]))
    with open(args.out, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows + carried)
    print(f"\nwrote {len(rows) + len(carried)} rows to {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
