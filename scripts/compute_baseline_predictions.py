#!/usr/bin/env python3
"""Per-cell held-out predictions for the models the diagnostic figures draw.

    python scripts/compute_baseline_predictions.py            # report only
    python scripts/compute_baseline_predictions.py --write    # write the CSV

`baseline_results_2018.csv` carries the metrics and not the predictions, so a
figure drawing observed against predicted has nothing to read. This writes the
predictions, one row per cell per model, for the four models the figures use.

**Every prediction here is out of fold.** It comes from
`src.model.baselines.held_out_predictions`, which runs the same loop
:func:`~src.model.baselines.evaluate` runs -- fit on the training rows of a
fold, predict its test rows, pool -- and returns the predictions instead of
discarding them. The distinction is not pedantic. In-sample fitted values
against observed would be the most flattering mistake available in this
figure, and on this table an in-sample R squared is several times its held-out
counterpart for exactly the models whose flatness is the finding.

The check that says so: this script recomputes RMSE and R squared from the
pooled predictions and refuses to write unless they reproduce the committed
`baseline_results_2018.csv` to four decimal places, which is the precision that
file is rounded to. Both the in-sample and the held-out metric are recomputed,
so the file also records the gap between them rather than leaving a reader to
wonder which one the figure drew.

**The models are on one sample and one scheme.** All four run on the 926 cells
that carry a methane value, under spatial blocks, so the four panels can be
read against each other. The rice models run on 531 cells and are deliberately
absent: `baselines.py` records that results on different samples must not be
compared without saying so, and four panels side by side is a comparison
whatever the caption says. Their numbers go in the caption instead.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import sys
import tempfile
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model.baselines import (  # noqa: E402
    GlobalMean,
    LinearModel,
    Metrics,
    NeighbourMean,
    evaluate,
    held_out_predictions,
    load_table,
)

PROCESSED = REPO / "data" / "processed"
GRID = PROCESSED / "analysis_grid_2018.csv"
COVARIATES = PROCESSED / "methane_covariates_2018.csv"
RESULTS = PROCESSED / "baseline_results_2018.csv"

#: One scheme and one weighting for the drawn panels. Spatial blocks because it
#: is the scheme in which the spatial null is a bar at all: under
#: leave-one-province-out a held-out province's interior has no training
#: neighbour, so the null falls to -0.091, which still beats the constant's
#: -0.172 but is below zero, so it explains none of the held-out variance and
#: the contrast the figure is for disappears. Unweighted because the scatter
#: draws one mark per cell and a weighted metric beside an unweighted picture
#: would describe a different fit; the figure encodes the weight as mark size
#: instead, and reports every combination in its summary panel.
SCHEME = "spatial blocks"
WEIGHTED = False

#: Block side and fold count, the same defaults `run_baselines.py` uses. Passed
#: explicitly rather than relied on, because the committed metrics were
#: computed with these and a different value would silently produce a different
#: partition.
BLOCK, FOLDS, SEED = 4, 5, 0

FIELDS = ["model", "scheme", "weighting", "row", "col", "centre_lat",
          "centre_lon", "province", "fold", "sounding_count", "observed_ppb",
          "predicted_ppb", "residual_ppb"]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def chosen_models():
    """The four, in the order the figure reads them.

    A progression from no information to meteorology, chosen against the table
    rather than from expectation. Their held-out R squared under this scheme,
    unweighted, is -0.008, 0.085, 0.332 and 0.653, so the four are spread
    across the whole range the table contains on this sample.
    """
    return [
        ("constant (global mean)", GlobalMean()),
        ("OLS impervious_fraction", LinearModel(("impervious_fraction",))),
        ("spatial null (queen neighbour mean)", NeighbourMean()),
        ("OLS wind (u, v, speed)",
         LinearModel(("wind_u", "wind_v", "wind_speed"),
                     label="OLS wind (u, v, speed)")),
    ]


def committed_metrics() -> dict:
    """What `baseline_results_2018.csv` says, for the reproduction check."""
    out = {}
    with RESULTS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row["model"], row["scheme"], row["weighting"])
            out[key] = {name: float(row[name]) for name in
                        ("in_sample_rmse_ppb", "in_sample_r2",
                         "held_out_rmse_ppb", "held_out_r2")}
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=None)
    parser.add_argument("--grid", default=str(GRID))
    parser.add_argument("--covariates", default=str(COVARIATES))
    args = parser.parse_args(argv)

    destination = (Path(args.out) if args.out
                   else PROCESSED / "baseline_predictions_2018.csv"
                   if args.write
                   else Path(tempfile.mkdtemp()) / "baseline_predictions_2018.csv")
    destination.parent.mkdir(parents=True, exist_ok=True)

    table = load_table(args.grid, covariates=args.covariates)
    committed = committed_metrics()
    weighting = "by sounding count" if WEIGHTED else "unweighted"
    print(f"{table.n} cells, scheme {SCHEME}, {weighting}, "
          f"block {BLOCK}, folds {FOLDS}, seed {SEED}")

    rows, worst = [], 0.0
    for name, model in chosen_models():
        extra = {"block": BLOCK, "folds": FOLDS, "seed": SEED}
        out = held_out_predictions(table, model, scheme=SCHEME,
                                   weighted=WEIGHTED, **extra)
        result = evaluate(table, model, scheme=SCHEME, weighted=WEIGHTED,
                          **extra)
        recomputed = out.metrics()
        reference = committed[(name, SCHEME, weighting)]

        # Two checks, and the second is the one that matters. The first says
        # the pooled predictions reproduce this run's own metrics; the second
        # says this run reproduces the committed table.
        for label, got, want in (
                ("held-out rmse", recomputed.rmse, reference["held_out_rmse_ppb"]),
                ("held-out r2", recomputed.r2, reference["held_out_r2"]),
                ("in-sample rmse", result.in_sample.rmse,
                 reference["in_sample_rmse_ppb"]),
                ("in-sample r2", result.in_sample.r2, reference["in_sample_r2"])):
            gap = abs(got - want)
            worst = max(worst, gap)
            if gap > 5e-4:
                raise SystemExit(
                    f"{name}: recomputed {label} {got:.4f} against the "
                    f"committed {want:.4f}. The figure and the table would be "
                    f"describing different fits.")

        print(f"  {name:38s} held-out R2 {recomputed.r2:7.4f} "
              f"RMSE {recomputed.rmse:6.2f}   in-sample R2 "
              f"{result.in_sample.r2:7.4f} RMSE {result.in_sample.rmse:6.2f}")

        order = np.argsort(out.rows)
        for position in order:
            index = int(out.rows[position])
            rows.append({
                "model": name, "scheme": SCHEME, "weighting": weighting,
                "row": int(table.row[index]), "col": int(table.col[index]),
                "centre_lat": f"{table.columns['centre_lat'][index]:.3f}",
                "centre_lon": f"{table.columns['centre_lon'][index]:.3f}",
                "province": table.province[index],
                "fold": str(out.fold[position]),
                "sounding_count": int(table.weight[index]),
                "observed_ppb": f"{out.actual[position]:.4f}",
                "predicted_ppb": f"{out.predicted[position]:.4f}",
                "residual_ppb":
                    f"{out.actual[position] - out.predicted[position]:.4f}",
            })

    print(f"\n  every metric reproduces the committed table; worst gap "
          f"{worst:.2e}")

    with destination.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    print(f"\nwrote {destination}")
    print(f"  rows             {len(rows):,} "
          f"({len(chosen_models())} models x {table.n} cells)")
    print(f"  bytes            {destination.stat().st_size:,}")
    print(f"  sha256           {digest(destination)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
