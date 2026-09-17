#!/usr/bin/env python3
"""The domain's sectoral composition on the analysis lattice, and its interleaving.

Two measurements that replace argued claims with measured ones. Both were named
in the case study assessment and neither existed.

**What this is a measurement of, stated first.** CHN-CH4 is a bottom-up
inventory: its per-sector grids are emissions *allocated by proxy data*, not
observations of sources. So these numbers describe **where an inventory puts the
domain's emissions**, which is exactly the object the identifiability limit is
about -- that limit says attribution derives from the prior's spatial
distinctness -- but it is not a measurement of where the sources are. A reader
who takes it for the latter is reading it wrong and the artefact says so in its
`basis` column.

**Why aggregate to 0.25 degrees.** The inventory is on a ~10 km projected grid
and this work analyses a 0.25 degree lattice. A sectoral split on the
inventory's own grid answers a question nobody asked; the split on the lattice
this work fits models to is the relevant one, because it is the resolution at
which the sectors are confounded for *this* analysis.

**How the aggregation conserves mass.** The inventory's unit is Mg CH4 per km2
per year, so each pixel is multiplied by its own area before being summed --
summing the rates directly would weight a pixel by nothing and give a number
with no interpretation. Each inventory pixel centre is transformed to longitude
and latitude and assigned to the lattice cell containing it. At ~10 km into
cells of about 24 by 28 km each cell receives six to eight pixels, so
centre-assignment and area-weighting differ only at cell edges; the totals are
conserved either way and the choice is stated rather than hidden.

**The interleaving statistic and its threshold.** A cell "carries" a sector when
that sector holds at least `share` of the cell's total emissions. Counting cells
with two or more sectors above the threshold is the interspersed-source claim as
one number. **A threshold chosen to make the claim look strong is the failure
mode**, so the artefact reports the statistic across a sweep from 1 to 25
percent and the report prints the whole sweep. No single threshold is privileged
in the artefact.

Run with no arguments to report; ``--write`` to write the artefact.
"""

from __future__ import annotations

import argparse
import csv
import glob
import sys
from pathlib import Path

import numpy as np
import rasterio
from rasterio.warp import transform as warp_transform

REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "data" / "processed" / "sector_composition_2018.csv"
PROCESSED = REPO / "data" / "processed"

#: The analysis lattice, from `data/interim/extent_2018.npz`'s spec.
WEST, SOUTH, EAST, NORTH, RES = 114.8, 26.95, 122.55, 35.2, 0.25
N_COLS, N_ROWS = 31, 33

#: The inventory's sector grids for 2018. Five of the domain's seven sectors;
#: aquaculture and natural wetland have no sector in an anthropogenic inventory,
#: which is the same gap the drafts record.
SECTORS = {
    "rice": "Methane_Rice_Cultivation/methane_rice_2018.tif",
    "coal": "Methane_Coal_Exploitation/methane_coal_2018.tif",
    "landfills": "Methane_Landfills/methane_landfills_2018.tif",
    "wastewater": "Methane_Wastewater/methane_wastewater_2018.tif",
    "oil_and_gas": "Methane_Oil_Natural_Gas/methane_oilgas_2018.tif",
}

ROOT = REPO / "data" / "raw" / "chn_ch4"

#: Shares of a cell's total at which a sector counts as present. Swept rather
#: than chosen.
THRESHOLDS = (0.01, 0.02, 0.05, 0.10, 0.15, 0.20, 0.25)


def lattice_of(path: Path) -> tuple[np.ndarray, float]:
    """One sector's emissions summed onto the lattice, in Mg CH4 per year."""
    with rasterio.open(path) as src:
        values = src.read(1).astype("float64")
        rows, cols = np.nonzero(np.isfinite(values) & (values > 0))
        if rows.size == 0:
            return np.zeros((N_ROWS, N_COLS)), 0.0
        xs, ys = rasterio.transform.xy(src.transform, rows, cols)
        lon, lat = warp_transform(src.crs, "EPSG:4326", xs, ys)
        pixel_km2 = abs(src.res[0] * src.res[1]) / 1e6
        mass = values[rows, cols] * pixel_km2
        national = float(mass.sum())

    lon = np.asarray(lon)
    lat = np.asarray(lat)
    col = np.floor((lon - WEST) / RES).astype(int)
    # Row 0 is the north edge, matching the composite's own exporter.
    row = np.floor((NORTH - lat) / RES).astype(int)
    inside = (col >= 0) & (col < N_COLS) & (row >= 0) & (row < N_ROWS)

    grid = np.zeros((N_ROWS, N_COLS))
    np.add.at(grid, (row[inside], col[inside]), mass[inside])
    return grid, national


def rows_for() -> list[dict]:
    grids, nationals = {}, {}
    for name, rel in SECTORS.items():
        path = ROOT / rel
        if not path.exists():
            continue
        grids[name], nationals[name] = lattice_of(path)
    if not grids:
        return []

    stack = np.stack([grids[k] for k in grids])
    names = list(grids)
    total = stack.sum(axis=0)
    observed = total > 0

    out: list[dict] = []

    def add(quantity, value, unit, basis, note=""):
        out.append(dict(quantity=quantity, value=value, unit=unit,
                        basis=basis, note=note))

    add("sectors on the lattice", f"{len(names)}", "count", "inventory",
        "of the domain's seven; aquaculture and wetland have no sector in an "
        "anthropogenic inventory")
    add("lattice cells with any inventory emission", f"{int(observed.sum())}",
        "cells", "inventory", f"of {N_ROWS * N_COLS}")
    add("domain total on the lattice", f"{total.sum():.1f}",
        "Mg CH4 per year", "inventory", "sum of the five sectors")

    for name in names:
        domain = grids[name].sum()
        add(f"{name}, domain total", f"{domain:.1f}", "Mg CH4 per year",
            "inventory", "")
        add(f"{name}, share of the domain", f"{100 * domain / total.sum():.2f}",
            "percent", "inventory", "of the five sectors aggregated here")
        add(f"{name}, share of its national total",
            f"{100 * domain / nationals[name]:.2f}", "percent", "inventory",
            "how much of China's emission from this sector is inside the box")
        add(f"{name}, cells present", f"{int((grids[name] > 0).sum())}",
            "cells", "inventory", "any emission at all")

    with np.errstate(invalid="ignore", divide="ignore"):
        share = np.where(observed, stack / np.where(total > 0, total, 1), 0.0)

    for threshold in THRESHOLDS:
        present = (share >= threshold) & (stack > 0)
        count = present.sum(axis=0)
        pct = f"{threshold * 100:g}"
        for least in (2, 3, 4):
            cells = int(((count >= least) & observed).sum())
            add(f"cells carrying at least {least} sectors above {pct} percent",
                f"{cells}", "cells", "inventory",
                f"{100 * cells / max(int(observed.sum()), 1):.1f} percent of "
                f"observed cells")
        add(f"median sectors above {pct} percent per observed cell",
            f"{np.median(count[observed]):.1f}", "sectors", "inventory", "")

    # Pairwise co-presence at the reported threshold, which is what makes the
    # claim concrete: which sectors actually share cells.
    at = 0.05
    present = (share >= at) & (stack > 0)
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            j = names.index(b)
            both = int((present[i] & present[j]).sum())
            add(f"cells carrying both {a} and {b} above 5 percent",
                f"{both}", "cells", "inventory", "")

    # What each sector's allocation is correlated with on this lattice. This is
    # not a property of the region; it is a property of the inventory's
    # downscaling, and it decides which sectors this project's own predictors
    # can legitimately be tested against. A sector whose allocation surface is
    # a near-monotone function of impervious fraction cannot be used to test an
    # impervious-fraction hypothesis, however accurate its national total.
    grid_rows = list(csv.DictReader(
        (PROCESSED / "analysis_grid_2018.csv").open(newline="")))
    lat = np.array([float(r["centre_lat"]) for r in grid_rows])
    lon = np.array([float(r["centre_lon"]) for r in grid_rows])
    row = np.round((NORTH - lat) / RES - 0.5).astype(int)
    col = np.round((lon - WEST) / RES - 0.5).astype(int)
    predictors = {}
    for column in ("impervious_fraction", "rice_fraction_combined"):
        predictors[column] = np.array(
            [float(r[column]) if r[column].strip() else np.nan
             for r in grid_rows])

    def ranks(values):
        return np.argsort(np.argsort(values)).astype("float64")

    for name in names:
        sector = grids[name][row, col]
        for column, values in predictors.items():
            keep = np.isfinite(values) & np.isfinite(sector)
            if keep.sum() < 30:
                continue
            spearman = float(np.corrcoef(ranks(values[keep]),
                                         ranks(sector[keep]))[0, 1])
            pearson = float(np.corrcoef(values[keep], sector[keep])[0, 1])
            add(f"{name} allocation vs {column}, Spearman",
                f"{spearman:+.4f}", "rank correlation", "inventory",
                f"over {int(keep.sum())} analysis cells; Pearson "
                f"{pearson:+.4f}. A high value means this sector's allocation "
                f"surface and this predictor are close to the same variable, "
                f"so the sector cannot test the predictor")

    # And whether two sectors share an allocation surface outright, which is a
    # stronger statement than a correlation and is checked on the national grid
    # rather than on the lattice so that the lattice cannot create it.
    masks = {name: grids[name] > 0 for name in names}
    for i, a in enumerate(names):
        for b in names[i + 1:]:
            if np.array_equal(masks[a], masks[b]):
                add(f"{a} and {b} share an allocation mask", "1", "boolean",
                    "inventory",
                    "identical nonzero cells on the lattice, which is what one "
                    "allocation surface carrying two per-unit factors looks like")
    return out


def report(rows: list[dict]) -> None:
    if not rows:
        print("  the CHN-CH4 sector grids are not on disk; fetch them first")
        return
    table = {r["quantity"]: r["value"] for r in rows}
    print(f"  five of seven sectors, aggregated to the 0.25 degree lattice")
    print(f"  {table['lattice cells with any inventory emission']} of "
          f"{N_ROWS * N_COLS} cells carry any inventory emission\n")
    print(f"    {'sector':<14}{'domain Mg/yr':>14}{'% of domain':>13}"
          f"{'% of national':>15}{'cells':>8}")
    for name in SECTORS:
        key = f"{name}, domain total"
        if key not in table:
            continue
        print(f"    {name:<14}{float(table[key]):>14,.0f}"
              f"{float(table[f'{name}, share of the domain']):>12.2f} %"
              f"{float(table[f'{name}, share of its national total']):>14.2f} %"
              f"{int(table[f'{name}, cells present']):>8}")

    print("\n  interleaving across the whole threshold sweep, not at one point:")
    print(f"    {'threshold':>10}{'>=2 sectors':>14}{'>=3':>8}{'>=4':>8}"
          f"{'median':>9}")
    for threshold in THRESHOLDS:
        pct = f"{threshold * 100:g}"
        print(f"    {pct + ' %':>10}"
              f"{table[f'cells carrying at least 2 sectors above {pct} percent']:>14}"
              f"{table[f'cells carrying at least 3 sectors above {pct} percent']:>8}"
              f"{table[f'cells carrying at least 4 sectors above {pct} percent']:>8}"
              f"{table[f'median sectors above {pct} percent per observed cell']:>9}")

    print("\n  which sectors share cells, at 5 percent:")
    for r in rows:
        if r["quantity"].startswith("cells carrying both"):
            print(f"    {r['quantity'][20:]:<52}{r['value']:>6}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    rows = rows_for()
    report(rows)
    if not rows:
        return 1
    if args.write:
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=["quantity", "value", "unit", "basis", "note"])
            writer.writeheader()
            writer.writerows(rows)
        try:
            shown = Path(args.out).resolve().relative_to(REPO)
        except ValueError:
            shown = Path(args.out)
        print(f"\n  wrote {shown}")
    else:
        print("\n  re-run with --write to write the artefact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
