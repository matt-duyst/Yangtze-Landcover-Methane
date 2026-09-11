#!/usr/bin/env python3
"""Held-out skill against buffer radius: the decay curve, not one buffer.

    python scripts/buffered_loo_curve.py
    python scripts/buffered_loo_curve.py --write

`notes/grounding-methods.md` records this as the diagnostic the spatial
cross-validation literature recommends and this project does not have: buffered
leave-one-out across a range of increasing radii, so that predictive power's
decay with distance from the training data is visible as a shape rather than
asserted at one arbitrary buffer. Neither of this project's two schemes buffers
at all.

**How it works.** For each radius, each covered cell in turn is held out, every
cell within that radius of it is also excluded from training, the model is
fitted on what remains, and the held-out cell is predicted. The resulting 926
predictions give one held-out R squared per radius per model.

**How the radii were chosen, which is gated on the measured ranges.**
`data/processed/residual_range_2018.csv` puts the residual half-sill range at
96.1 km for the impervious model on the operational field and 134.5 km on the
blended one, and at 12 to 23 km for the models that include albedo. The block
in use is 111 km north-south by 95 km east-west. So the radii have to resolve
three scales: below a cell, across the measured residual ranges, and out to the
width of a held-out province, which is where leave-one-province-out sits. They
run 0, 25, 50, 75, 100, 150, 200, 300, 400 and 500 km.

The upper end is where the curve must end rather than where it becomes
uninformative. The domain is roughly 750 by 900 km, so a 500 km buffer removes
most of the training data for a central cell, and beyond that almost every cell
would have no training data at all. Roberts et al. used 100, 500 and 1,000 km
in a continental setting; 1,000 km is larger than this domain.

**The shapes are the point and they differ by model.** The spatial null has
nothing but neighbours, so it should collapse as soon as the buffer exceeds one
cell. Land cover uses no spatial information at all, so it should be flat:
distance to the training data cannot matter to a model that never looks at
where anything is. A land-cover curve that is *not* flat would mean the fitted
coefficient depends on which part of the domain trained it, which is a different
and more interesting failure.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model import spatial_dof as sd  # noqa: E402

PROCESSED = REPO / "data" / "processed"
OUT = PROCESSED / "buffered_loo_2018.csv"

#: Chosen from the measured residual ranges; see the module docstring.
RADII_KM = (0.0, 25.0, 50.0, 75.0, 100.0, 150.0, 200.0, 300.0, 400.0, 500.0)

#: A fold needs some training data left. Below this the radius has removed so
#: much that the fit is not meaningful, and the cell is dropped with a count
#: kept so the attrition is visible rather than silent.
MIN_TRAINING = 30


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def cell_key(row: dict) -> tuple[int, int]:
    return (round(float(row["centre_lat"]) * 1000),
            round(float(row["centre_lon"]) * 1000))


def load() -> dict[str, np.ndarray]:
    grid = read_csv(PROCESSED / "analysis_grid_2018.csv")
    blend = {cell_key(r): r for r in read_csv(PROCESSED / "methane_blended_2018.csv")}

    def f(value: str) -> float:
        return float(value) if value not in ("", None) else float("nan")

    cols: dict[str, list[float]] = {k: [] for k in (
        "lat", "lon", "operational", "blended", "impervious", "count")}
    for r in grid:
        b = blend.get(cell_key(r))
        cols["lat"].append(f(r["centre_lat"]))
        cols["lon"].append(f(r["centre_lon"]))
        cols["operational"].append(f(r["ch4_bias_corrected_ppb"]))
        cols["blended"].append(f(b["ch4_blended_ppb"]) if b else float("nan"))
        cols["impervious"].append(f(r["impervious_fraction"]))
        cols["count"].append(f(r["sounding_count"]))
    return {k: np.asarray(v, dtype="float64") for k, v in cols.items()}


def neighbour_index(lat: np.ndarray, lon: np.ndarray, *,
                    resolution: float = 0.25) -> list[list[int]]:
    """The eight queen neighbours of each cell, as indices into the arrays."""
    key = {(round(a / resolution), round(o / resolution)): i
           for i, (a, o) in enumerate(zip(lat, lon))}
    return [[key[(round(a / resolution) + dr, round(o / resolution) + dc)]
             for dr in (-1, 0, 1) for dc in (-1, 0, 1)
             if (dr, dc) != (0, 0)
             and (round(a / resolution) + dr, round(o / resolution) + dc) in key]
            for a, o in zip(lat, lon)]


def r2(actual: np.ndarray, predicted: np.ndarray) -> float:
    """Held-out R squared against the held-out set's own mean.

    The same definition `src/model/baselines.py` uses, which is why it can be
    negative: a model predicting the training mean scores below zero whenever
    the held-out values sit away from it.
    """
    residual = float(np.sum((actual - predicted) ** 2))
    total = float(np.sum((actual - actual.mean()) ** 2))
    return 1.0 - residual / total if total > 0 else float("nan")


def curve(y: np.ndarray, x: np.ndarray, lat: np.ndarray, lon: np.ndarray,
          model: str) -> list[dict]:
    """One row per radius for one model on one field."""
    distance = sd.great_circle_km(lat, lon)
    neighbours = neighbour_index(lat, lon)
    n = len(y)
    rows: list[dict] = []

    for radius in RADII_KM:
        actual, predicted, dropped = [], [], 0
        for i in range(n):
            excluded = distance[i] <= radius
            excluded[i] = True
            train = ~excluded
            if train.sum() < MIN_TRAINING:
                dropped += 1
                continue

            if model == "spatial null (queen neighbour mean)":
                usable = [j for j in neighbours[i] if train[j]]
                value = (float(np.mean(y[usable])) if usable
                         else float(np.mean(y[train])))
            elif model == "constant (training mean)":
                value = float(np.mean(y[train]))
            else:
                design = np.column_stack([np.ones(int(train.sum())), x[train]])
                beta, *_ = np.linalg.lstsq(design, y[train], rcond=None)
                value = float(beta[0] + beta[1] * x[i])

            actual.append(y[i])
            predicted.append(value)

        actual_a, predicted_a = np.asarray(actual), np.asarray(predicted)
        rows.append({
            "model": model, "radius_km": f"{radius:.0f}",
            "cells_predicted": len(actual), "cells_dropped": dropped,
            "median_training_cells": int(np.median(
                [int((~(distance[i] <= radius)).sum()) - 0 for i in range(n)])),
            "held_out_r2": f"{r2(actual_a, predicted_a):.4f}",
            "rmse_ppb": f"{np.sqrt(np.mean((actual_a - predicted_a) ** 2)):.3f}",
        })
    return rows


def add_deltas(table: list[dict]) -> list[dict]:
    """Each model's skill above a constant fitted on the same training set.

    **This is the column to read and the raw R squared is not.** A constant
    predictor's held-out skill falls as the buffer grows, because the training
    mean drifts away from the held-out cell's neighbourhood, so every model's
    curve slopes down whether or not the model itself is degrading. The
    difference removes that common term.
    """
    baseline = {(r["field"], r["radius_km"]): float(r["held_out_r2"])
                for r in table if r["model"] == "constant (training mean)"}
    for row in table:
        key = (row["field"], row["radius_km"])
        row["r2_above_constant"] = f"{float(row['held_out_r2']) - baseline[key]:+.4f}"
    return table


#: The leave-one-province-out held-out R squared this repository reports for the
#: spatial null, from `figures/README_fragments.md`. The decay curve is the
#: measurement that would say whether the two schemes bracket the truth: if the
#: null's skill at a buffer comparable to the distance from a held-out
#: province's interior to the nearest training cell matches this, the reading
#: `notes/grounding-methods.md` offers is supported.
NULL_LOPO_R2 = -0.091


def rows() -> list[dict]:
    data = load()
    out: list[dict] = []
    for field in ("operational", "blended"):
        y = data[field]
        ok = np.isfinite(y) & np.isfinite(data["impervious"])
        yv, xv = y[ok], data["impervious"][ok]
        lat, lon = data["lat"][ok], data["lon"][ok]
        for model in ("spatial null (queen neighbour mean)",
                      "OLS impervious fraction",
                      "constant (training mean)"):
            for row in curve(yv, xv, lat, lon, model):
                out.append({"field": field, **row})
    return add_deltas(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT),
                        help="where to write; the recipe runner redirects it")
    args = parser.parse_args()

    table = rows()
    for field in ("operational", "blended"):
        print(f"\n=== {field} ===")
        models = [m for m in dict.fromkeys(r["model"] for r in table)]
        header = "  radius km " + "".join(f"{m[:26]:>28}" for m in models)
        print(header)
        for radius in RADII_KM:
            line = f"  {radius:>9.0f} "
            for model in models:
                match = [r for r in table if r["field"] == field
                         and r["model"] == model
                         and float(r["radius_km"]) == radius]
                line += f"{match[0]['held_out_r2']:>28}" if match else " " * 28
            print(line)

    # Where the null's buffered skill matches its leave-one-province-out value.
    print(f"\n  the spatial null's leave-one-province-out R squared is "
          f"{NULL_LOPO_R2:+.3f}; buffered, it passes that at")
    for field in ("operational", "blended"):
        null = [(float(r["radius_km"]), float(r["held_out_r2"])) for r in table
                if r["field"] == field
                and r["model"] == "spatial null (queen neighbour mean)"]
        crossing = [radius for radius, value in null if value <= NULL_LOPO_R2]
        nearest = min(null, key=lambda pair: abs(pair[1] - NULL_LOPO_R2))
        where = f"{min(crossing):.0f} km" if crossing else "no radius in range"
        print(f"    {field:<12} first at or below it: {where:<18} "
              f"closest {nearest[0]:.0f} km at {nearest[1]:+.4f}")

    if args.write:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(table[0]))
            writer.writeheader()
            writer.writerows(table)
        print(f"\nwrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
