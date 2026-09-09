#!/usr/bin/env python
"""Render the observed-against-predicted diagnostic figure.

    python scripts/make_observed_predicted_figure.py [--stem NAME]

Prints the held-out and in-sample metric for every panel, because the gap
between them is why the figure draws the first and not the second.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.figures import export, figures_root  # noqa: E402
from src.figures import observed_predicted as op  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stem", default="observed_predicted")
    args = parser.parse_args()

    with op.RESULTS.open(newline="") as handle:
        rows = {(r["model"], r["scheme"], r["weighting"]): r
                for r in csv.DictReader(handle)}
    print(f"  {op.SCHEME}, {op.WEIGHTING}")
    print(f"    {'model':38s} {'held R2':>8s} {'held RMSE':>10s} "
          f"{'in-sample R2':>13s}")
    for name, label in op.PANELS:
        row = rows[(name, op.SCHEME, op.WEIGHTING)]
        print(f"    {label:38s} {float(row['held_out_r2']):8.3f} "
              f"{float(row['held_out_rmse_ppb']):10.2f} "
              f"{float(row['in_sample_r2']):13.3f}")

    predictions = op.load_predictions()
    limits = op.shared_limits(predictions)
    print(f"\n  shared axis limits {limits[0]:.1f} to {limits[1]:.1f} ppb")
    for name, label in op.PANELS:
        field = predictions[name]["predicted"]
        print(f"    {label:38s} model field spans "
              f"{field.min():8.2f} to {field.max():8.2f} ppb "
              f"({field.max() - field.min():6.2f} wide)")
    observed = predictions[op.PANELS[0][0]]["observed"]
    print(f"    {'observed':38s} spans          "
          f"{observed.min():8.2f} to {observed.max():8.2f} ppb "
          f"({observed.max() - observed.min():6.2f} wide)")

    figure = op.observed_predicted_figure()
    result = export(figure, args.stem, directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
