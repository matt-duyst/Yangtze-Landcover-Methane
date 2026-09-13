#!/usr/bin/env python3
"""Decompose the GAIA-GISA disagreement into quantity and allocation components.

Queue item 10. This repository has reported the two impervious products'
difference as a single percentage of provincial area, which is **quantity
disagreement alone** and says nothing about whether the two put impervious
surface in the same places. Only the allocation component bears on a fractional
predictor's error, because a layer can have the right total and the wrong
locations and only the second attenuates a regression coefficient.

**The method does not transfer unmodified and that is recorded rather than
glossed.** Pontius and Millones (2011), which `notes/references.md` already
carries for the kappa correction, defines quantity and allocation disagreement
on a cross-tabulation matrix built with a Boolean operator over **hard**
classified pixels. This project's layers are fractional. Pontius and Cheuk
(2006, doi:10.1080/13658810500391024) is the soft-classified companion and it is
closed access, so its Composite operator could not be read.

What is computed here is the **two-class fractional specialisation**, which is
exact and needs no cross-tabulation machinery. For two fractional maps `a` and
`b` over units of area `w`:

    total difference      D = sum_i w_i * |a_i - b_i|
    quantity difference   Q = |sum_i w_i * a_i  -  sum_i w_i * b_i|
    allocation difference A = D - Q

`D = Q + A` identically, `A >= 0` by the triangle inequality, and `Q` is the
mismatch in totals while `A` is the part of the difference that would vanish if
one map were rearranged to match the other's total without changing it. In the
binary limit these reduce to Pontius and Millones's two-class definitions. The
test module asserts the identity and the binary-limit agreement.

**Both resolutions are reported, because they answer different questions and
because multiple-resolution analysis is the point of the soft-classified
method.** `notes/decisions.md` records the decision.

* The committed **868 m percent grid** (0.0078125 degrees), which is the finest
  comparable form of the two products this repository holds. It gives a
  disagreement in the products themselves.
* The **0.25 degree analysis lattice**, which is what the association actually
  consumes. Misallocation *within* a lattice cell cancels when the cell mean is
  taken, so this is the disagreement that survives into the regression.

The native 30 m products are **not** available for this: only small windows are
committed, and the full products are a 1-to-2 GB refetch.

Areas are computed per raster row as `res * 111.32 km` by the same times the
cosine of latitude, so a cell's area shrinks northward rather than being
assumed constant.

Run with no arguments to report; ``--write`` to write the artefact.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

PROCESSED = REPO / "data" / "processed"
OUT = PROCESSED / "urban_disagreement_2018.csv"

#: The two committed extent rasters carry impervious percent in four bands.
BANDS = {2000: 1, 2010: 2, 2018: 3, 2019: 4}

#: The analysis lattice, from analysis_grid_2018.csv.
CELL = 0.25
LAT0, LON0 = 27.075, 114.925


def load_products():
    """Both products as fractions, the transform, and a per-pixel area in km²."""
    import rasterio

    out = {}
    for name, fname in (("GAIA", "urban_extent_gaia.tif"),
                        ("GISA", "urban_extent_gisa.tif")):
        with rasterio.open(PROCESSED / fname) as src:
            out[name] = {year: src.read(band).astype(np.float64) / 100.0
                         for year, band in BANDS.items()}
            transform, height, width, crs = src.transform, src.height, src.width, src.crs
    res = transform.a
    lat = transform.f - (np.arange(height) + 0.5) * res
    row_km2 = (res * 111.32) * (res * 111.32 * np.cos(np.radians(lat)))
    area = np.repeat(row_km2[:, None], width, axis=1)
    return out, transform, area, crs


def province_mask(transform, shape, crs):
    """True where a pixel centre falls in one of the four provinces."""
    import geopandas as gpd
    from rasterio.features import rasterize

    provinces = gpd.read_file(REPO / "data" / "reference" / "yrd_provinces.geojson")
    provinces = provinces.to_crs(crs)
    burned = rasterize(((geom, 1) for geom in provinces.geometry),
                       out_shape=shape, transform=transform, fill=0, dtype="uint8")
    return burned.astype(bool)


def cell_index(transform, shape):
    """Analysis-cell row index per pixel, or -1 where the pixel is off-lattice."""
    rows = list(csv.DictReader((PROCESSED / "analysis_grid_2018.csv").open(newline="")))
    res = transform.a
    height, width = shape
    iy, ix = np.mgrid[0:height, 0:width]
    plat = transform.f - (iy + 0.5) * res
    plon = transform.c + (ix + 0.5) * res
    clat = np.round(np.round((plat - LAT0) / CELL) * CELL + LAT0, 4)
    clon = np.round(np.round((plon - LON0) / CELL) * CELL + LON0, 4)
    index = np.full(shape, -1, dtype=np.int32)
    for i, row in enumerate(rows):
        key_lat = round(float(row["centre_lat"]), 4)
        key_lon = round(float(row["centre_lon"]), 4)
        index[(clat == key_lat) & (clon == key_lon)] = i
    return index, len(rows)


def decompose(a, b, weight):
    """``(total, quantity, allocation)`` in the units of ``weight``."""
    total = float((np.abs(a - b) * weight).sum())
    quantity = float(abs((a * weight).sum() - (b * weight).sum()))
    return total, quantity, total - quantity


def rows_for(products, area, mask, index, n_cells) -> list[dict]:
    out: list[dict] = []
    for year in sorted(BANDS):
        gaia, gisa = products["GAIA"][year], products["GISA"][year]

        # --- the committed 868 m percent grid, province-clipped
        total, quantity, allocation = decompose(gaia[mask], gisa[mask], area[mask])
        out.append(dict(
            year=year, resolution="868 m pixel", domain="four provinces",
            gaia_km2=f"{(gaia[mask] * area[mask]).sum():.1f}",
            gisa_km2=f"{(gisa[mask] * area[mask]).sum():.1f}",
            total_difference_km2=f"{total:.1f}",
            quantity_km2=f"{quantity:.1f}",
            allocation_km2=f"{allocation:.1f}",
            allocation_share=f"{allocation / total:.4f}"))

        # --- the 0.25 degree analysis lattice, unclipped, which is what the
        # regression consumes: the committed impervious_fraction is the GAIA
        # cell mean over the whole cell rather than over its in-province part.
        sel = index >= 0
        num_g = np.bincount(index[sel], weights=(gaia * area)[sel], minlength=n_cells)
        num_s = np.bincount(index[sel], weights=(gisa * area)[sel], minlength=n_cells)
        den = np.bincount(index[sel], weights=area[sel], minlength=n_cells)
        keep = den > 0
        fg, fs, w = num_g[keep] / den[keep], num_s[keep] / den[keep], den[keep]
        total, quantity, allocation = decompose(fg, fs, w)
        out.append(dict(
            year=year, resolution="0.25 degree cell", domain="analysis lattice",
            gaia_km2=f"{(fg * w).sum():.1f}",
            gisa_km2=f"{(fs * w).sum():.1f}",
            total_difference_km2=f"{total:.1f}",
            quantity_km2=f"{quantity:.1f}",
            allocation_km2=f"{allocation:.1f}",
            allocation_share=f"{allocation / total:.4f}"))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    products, transform, area, crs = load_products()
    shape = area.shape
    mask = province_mask(transform, shape, crs)
    index, n_cells = cell_index(transform, shape)
    table = rows_for(products, area, mask, index, n_cells)

    fields = ["year", "resolution", "domain", "gaia_km2", "gisa_km2",
              "total_difference_km2", "quantity_km2", "allocation_km2",
              "allocation_share"]
    width = max(len(f) for f in fields)
    for row in table:
        print(f"  {row['year']}  {row['resolution']:<18}"
              f"total {float(row['total_difference_km2']):>9,.0f}  "
              f"quantity {float(row['quantity_km2']):>9,.0f}  "
              f"allocation {float(row['allocation_km2']):>9,.0f}  "
              f"({100 * float(row['allocation_share']):.1f} % allocation)")

    if args.write:
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows(table)
        try:
            shown = Path(args.out).resolve().relative_to(REPO)
        except ValueError:
            shown = Path(args.out)
        print(f"  wrote {shown}")
    else:
        print("  re-run with --write to write the artefact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
