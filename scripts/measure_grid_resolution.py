#!/usr/bin/env python3
"""Measure what a finer analysis grid would and would not buy.

**The question and why it was reopened.** `notes/decisions.md` closed the 0.1
degree grid on a pilot estimate of 32.91 percent annual coverage, and recorded
in the same place that the estimate came from an understated granule sample and
that "reopening it needs a measured curve at each resolution, not another
sample". This is that curve, measured from the committed 0.25 degree artefact
rather than from a sample.

**What cannot be measured here, stated first.** Coverage at a finer resolution
is a property of where individual soundings fell, and this repository does not
retain sounding coordinates. The checkpoint's `granule_cells` bitset is 1024
bits per granule *over the 0.25 degree lattice*, so it records which coarse cell
each granule touched and cannot be subdivided; `data/raw/s5p` holds one of the
578 granules. So the fine-resolution rows here are **projections** from the
measured coarse counts under an explicit assumption, not measurements, and they
are labelled as such in the artefact.

**The assumption and its direction.** Soundings are assumed uniformly
distributed inside each 0.25 degree cell, and are allocated to fine cells by
area overlap -- which handles resolutions that do not divide 0.25 degree, the
0.1 degree case included. TROPOMI soundings arrive in along-track swaths rather
than uniformly, and clustering can only put more soundings in fewer fine cells.
**So every projected coverage figure is an upper bound and every projected
count-below-threshold figure is a lower bound.** A projection that already fails
the question therefore fails it for real.

**Effective sample size is computed, not scaled.** The temptation is to assume
degrees of freedom grow with cell count. They do not: Dutilleul's effective n
is set by the domain's size relative to the autocorrelation length, and
regridding changes neither. It is computed here on a model correlogram whose
half-sill is the measured operational range, validated against
`src/model/spatial_dof.py`'s empirical estimator at 0.25 degree, where the two
agree to about 8 percent. The model is used only in the *fine* direction, where
cells shrink further below the correlation length and the point approximation
improves; it underpredicts the loss from coarsening, where averaging within
cells changes the support, so no coarsening claim is made from it.

Run with no arguments to report; ``--write`` to write the artefact.
"""

from __future__ import annotations

import argparse
import csv
import math
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

GRID = REPO / "data" / "processed" / "analysis_grid_2018.csv"
OUT = REPO / "data" / "processed" / "grid_resolution_2018.csv"

#: The declared study box, as `data/interim/extent_2018.npz` carries it.
WEST, SOUTH, EAST, NORTH = 114.8, 26.95, 122.55, 35.2
COARSE = 0.25

#: Resolutions to measure. 0.25 is measured; the rest are projected.
RESOLUTIONS = (0.25, 0.2, 0.15, 0.125, 0.1)

#: TCCON single-retrieval precision for the operational product and the
#: mission's recommended error multiplication factor, both from
#: `notes/grounding-methods.md`.
PRECISION_PPB = 14.5
ERROR_MULTIPLICATION_FACTOR = 2.0

#: The measured operational autocorrelation half-sill, in km.
HALF_SILL_KM = 103.2

#: The field's between-cell standard deviation, the signal a cell must resolve.
FIELD_SD_PPB = 14.856922079855249

EARTH_RADIUS_KM = 6371.0

#: Fixed so the projection is reproducible byte for byte.
SEED = 20260915


def lattice(res: float) -> tuple[int, int]:
    """Columns and rows at `res`, taking whole cells inside the declared box."""
    return (math.floor((EAST - WEST) / res + 1e-9),
            math.floor((NORTH - SOUTH) / res + 1e-9))


def effective_n(lat: np.ndarray, lon: np.ndarray) -> float:
    """Dutilleul's effective sample size on a spherical model correlogram."""
    phi = np.radians(lat)
    lam = np.radians(lon)
    a = (np.sin((phi[:, None] - phi[None, :]) / 2.0) ** 2
         + np.cos(phi)[:, None] * np.cos(phi)[None, :]
         * np.sin((lam[:, None] - lam[None, :]) / 2.0) ** 2)
    d = 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))
    span = 3.0 * HALF_SILL_KM
    rho = np.where(d < span, 1.0 - 1.5 * (d / span) + 0.5 * (d / span) ** 3, 0.0)
    return 1.0 + len(lat) ** 2 / float((rho * rho).sum())


def _overlap(a0: float, a1: float, b0: float, b1: float) -> float:
    return max(0.0, min(a1, b1) - max(b0, a0))


def project(res: float, lat: np.ndarray, lon: np.ndarray,
            count: np.ndarray, rng) -> np.ndarray:
    """Allocate each coarse cell's soundings to fine cells by area overlap."""
    nx, ny = lattice(res)
    grid = np.zeros((ny, nx))
    for y, x, n in zip(lat, lon, count):
        if n <= 0:
            continue
        y0, y1 = y - COARSE / 2.0, y + COARSE / 2.0
        x0, x1 = x - COARSE / 2.0, x + COARSE / 2.0
        j0 = max(0, int(math.floor((x0 - WEST) / res)))
        j1 = min(nx, int(math.ceil((x1 - WEST) / res)))
        i0 = max(0, int(math.floor((y0 - SOUTH) / res)))
        i1 = min(ny, int(math.ceil((y1 - SOUTH) / res)))
        cells, fractions = [], []
        for i in range(i0, i1):
            for j in range(j0, j1):
                area = (_overlap(y0, y1, SOUTH + i * res, SOUTH + (i + 1) * res)
                        * _overlap(x0, x1, WEST + j * res, WEST + (j + 1) * res))
                if area > 0:
                    cells.append((i, j))
                    fractions.append(area)
        weights = np.array(fractions)
        for (i, j), drawn in zip(cells,
                                 rng.multinomial(int(n), weights / weights.sum())):
            grid[i, j] += drawn
    return grid


def measured_grid(lat, lon, count) -> np.ndarray:
    """The 0.25 degree counts back on their lattice."""
    nx, ny = lattice(COARSE)
    grid = np.zeros((ny, nx))
    for y, x, n in zip(lat, lon, count):
        grid[int(round((y - SOUTH - COARSE / 2) / COARSE)),
             int(round((x - WEST - COARSE / 2) / COARSE))] = n
    return grid


def rows_for(lat, lon, count) -> list[dict]:
    from scipy import ndimage

    rng = np.random.default_rng(SEED)
    effective = ERROR_MULTIPLICATION_FACTOR * PRECISION_PPB
    out: list[dict] = []

    def add(resolution, quantity, value, unit, basis, note=""):
        out.append(dict(resolution_deg=resolution, quantity=quantity,
                        value=value, unit=unit, basis=basis, note=note))

    add("", "per-sounding uncertainty", f"{effective:.1f}", "ppb", "literature",
        f"{PRECISION_PPB} ppb TCCON precision times the recommended factor "
        f"{ERROR_MULTIPLICATION_FACTOR:.0f}")
    add("", "field between-cell sd", f"{FIELD_SD_PPB:.2f}", "ppb", "measured",
        "the spatial signal a single cell has to resolve")
    add("", "autocorrelation half-sill", f"{HALF_SILL_KM}", "km", "measured",
        "the operational field's range; sets the effective sample size")

    for res in RESOLUTIONS:
        nx, ny = lattice(res)
        total = nx * ny
        basis = "measured" if res == COARSE else "projected"
        exact_x = (EAST - WEST) / res
        exact_y = (NORTH - SOUTH) / res
        divides = (abs(exact_x - round(exact_x)) < 1e-9
                   and abs(exact_y - round(exact_y)) < 1e-9)
        centre = (SOUTH + NORTH) / 2.0

        add(res, "lattice columns by rows", f"{nx} x {ny}", "cells", basis,
            f"exactly {exact_x:.2f} x {exact_y:.2f} cells fit the declared box")
        add(res, "cells", f"{total}", "cells", basis, "")
        add(res, "divides the extent cleanly", "yes" if divides else "no",
            "boolean", "derived",
            "" if divides else "whole cells taken from the southwest corner, "
            "leaving a remainder strip outside the lattice")
        add(res, "extent covered by whole cells",
            f"{WEST}..{WEST + nx * res:.3f}, {SOUTH}..{SOUTH + ny * res:.3f}",
            "degrees", "derived", "")
        add(res, "cell size at the domain centre",
            f"{res * 111.32 * math.cos(math.radians(centre)):.2f} x "
            f"{res * 111.32:.2f}", "km", "derived",
            f"east-west by north-south at {centre:.3f} N")

        grid = (measured_grid(lat, lon, count) if res == COARSE
                else project(res, lat, lon, count, rng))
        flat = grid.ravel()
        covered = flat[flat > 0]
        quartiles = np.percentile(covered, [0, 25, 50, 75, 100])
        errors = effective / np.sqrt(covered)

        add(res, "covered cells", f"{len(covered)}", "cells", basis,
            "an upper bound where projected: swaths cluster, which can only "
            "put the same soundings in fewer cells")
        add(res, "annual coverage", f"{len(covered) / total * 100:.1f}",
            "percent", basis, "")
        for name, value in zip(("minimum", "first quartile", "median",
                                "third quartile", "maximum"), quartiles):
            add(res, f"soundings per covered cell, {name}", f"{value:.0f}",
                "soundings", basis, "")
        for threshold in (5, 10, 30):
            add(res, f"covered cells below {threshold} soundings",
                f"{int((covered < threshold).sum())}", "cells", basis,
                "a lower bound where projected")
        add(res, "per-cell standard error, median", f"{np.median(errors):.2f}",
            "ppb", basis, "per-sounding uncertainty over the root of the count")
        add(res, "per-cell standard error as a share of the field spread",
            f"{np.median(errors) / FIELD_SD_PPB * 100:.0f}", "percent", basis,
            "at 100 percent a cell's noise equals the whole spatial signal")
        add(res, "cells whose standard error exceeds the field spread",
            f"{int((errors > FIELD_SD_PPB).sum())}", "cells", basis, "")

        uncovered = flat.size - len(covered)
        labels, components = ndimage.label(grid == 0)
        sizes = np.bincount(labels.ravel())[1:] if components else np.array([0])
        add(res, "uncovered cells", f"{uncovered}", "cells", basis, "")
        add(res, "uncovered connected components", f"{components}", "components",
            basis, "four-connectivity")
        add(res, "largest uncovered component", f"{int(sizes.max())}", "cells",
            basis, "")
        add(res, "share of gaps in the largest component",
            f"{sizes.max() / max(uncovered, 1) * 100:.1f}", "percent", basis,
            "falling with resolution means the gaps fragment rather than "
            "concentrate")
        add(res, "single-cell gaps", f"{int((sizes == 1).sum())}", "cells",
            basis, "")

        lon_c = WEST + (np.arange(nx) + 0.5) * res
        lat_c = SOUTH + (np.arange(ny) + 0.5) * res
        mesh_lon, mesh_lat = np.meshgrid(lon_c, lat_c)
        add(res, "effective sample size, full lattice",
            f"{effective_n(mesh_lat.ravel(), mesh_lon.ravel()):.1f}",
            "observations", "modelled",
            "Dutilleul on a spherical correlogram at the measured half-sill")

    add("", "effective sample size at 0.25 degree, empirical",
        f"{_empirical(lat, lon):.1f}", "observations", "measured",
        "src/model/spatial_dof.py on the committed field, as the model's check")
    return out


def _empirical(lat, lon) -> float:
    from src.model import spatial_dof as sd
    rows = list(csv.DictReader(GRID.open(newline="")))
    values = np.array([float(r["ch4_bias_corrected_ppb"]) for r in rows])
    return sd.effective_sample_size(values, values, lat, lon)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--grid", default=str(GRID))
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    rows = list(csv.DictReader(Path(args.grid).open(newline="")))
    lat = np.array([float(r["centre_lat"]) for r in rows])
    lon = np.array([float(r["centre_lon"]) for r in rows])
    count = np.array([int(float(r["sounding_count"])) for r in rows])

    table = rows_for(lat, lon, count)
    width = max(len(r["quantity"]) for r in table)
    for row in table:
        tag = f"{row['resolution_deg']:>5}" if row["resolution_deg"] != "" else "    -"
        print(f"  {tag}  {row['quantity']:<{width}}  {row['value']:>16}  "
              f"{row['unit']}  [{row['basis']}]")

    if args.write:
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(
                handle, fieldnames=["resolution_deg", "quantity", "value",
                                    "unit", "basis", "note"])
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
