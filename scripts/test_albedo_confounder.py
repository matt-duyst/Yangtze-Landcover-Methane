#!/usr/bin/env python3
"""Ask whether the land-cover signal is a retrieval artefact.

    python scripts/test_albedo_confounder.py
    python scripts/test_albedo_confounder.py --write

This runs before the predictor results, not after, because if it comes back
positive then every land-cover number downstream needs a caveat attached and it
is better to attach it first.

The concern is specific and mechanical. TROPOMI's methane retrieval needs light
back from the surface, so it fails preferentially over dark ground:
reconnaissance over this study area measured a median surface_albedo_SWIR of
0.1058 on valid soundings against 0.0621 on invalid ones. The literature reports
a seasonal surface-albedo bias in TROPOMI methane over agricultural land. Rice
paddies flood, which moves their albedo on the same seasonal cycle as their
methane. Cities are bright and dry all year. So albedo is plausibly correlated
with both the land cover and the retrieved value, which is the shape of a
confounder rather than a nuisance.

Two legs have to hold for a retrieval bias to masquerade as a land-cover signal:
albedo must correlate with methane, and albedo must correlate with the
land-cover fraction. Both are quantified here, and then the land-cover
association is recomputed with albedo partialled out of both sides. Nothing here
is causal in either direction; it establishes whether an alternative explanation
is available, not which explanation is true.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model.association import (  # noqa: E402
    Association,
    correlate,
    paired,
    partial_correlation,
)
from src.model.baselines import load_table  # noqa: E402

TARGET = "methane"
ALBEDO = "surface_albedo_SWIR"

FIELDS = ["weighting", "relationship", "controlling_for", "n", "pearson",
          "pearson_p", "spearman", "spearman_p"]


def show(results: list[Association]) -> None:
    print(f"  {'relationship':<52}{'n':>6}{'Pearson':>10}{'p':>12}"
          f"{'Spearman':>10}{'p':>12}")
    for r in results:
        label = r.name if not r.controls else f"{r.name} | {', '.join(r.controls)}"
        print(f"  {label:<52}{r.n:>6}{r.pearson:>+10.3f}{r.pearson_p:>12.2e}"
              f"{r.spearman:>+10.3f}{r.spearman_p:>12.2e}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--grid", default=str(REPO / "data" / "processed" /
                                              "analysis_grid_2018.csv"))
    parser.add_argument("--covariates",
                        default=str(REPO / "data" / "processed" /
                                    "methane_covariates_2018.csv"))
    parser.add_argument("--out", default=str(REPO / "data" / "processed" /
                                             "albedo_confounder_2018.csv"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    table = load_table(args.grid, covariates=args.covariates)
    column = table.columns
    _sample(table, column)

    # Both weightings, always. A cell's methane is the mean of between 1 and
    # 410 soundings, so the inverse-variance weight is the sounding count; but
    # sounding count is not random over the study area, and reporting only one
    # weighting would let a reader assume the other agrees. Here they do agree,
    # which is worth more than either alone.
    rows = []
    for label, weight in (("unweighted", None),
                          ("by sounding count", table.weight)):
        print(f"\n{'=' * 74}\n=== {label} ===\n{'=' * 74}")
        rows += _run(table, column, weight, label)

    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            for label, record in rows:
                writer.writerow({"weighting": label, **record.as_dict()})
        print(f"\n  wrote {out}  ({out.stat().st_size:,} B, {len(rows)} rows)")
    else:
        print("\n  report only: nothing written. Pass --write to save.")
    return 0


def _sample(table, column) -> None:
    """3c, stated first because it bounds everything below."""
    print("=== sample ===")
    print(f"  cells in the analysis grid                {table.n}")
    for name in (ALBEDO, "surface_albedo_NIR", "solar_zenith_angle", "wind_speed"):
        have = int(np.isfinite(column[name]).sum())
        print(f"  cells with {name:<28}{have:>5}  ({100 * have / table.n:.1f}%)")
    with_rice = int(np.isfinite(column["rice_fraction_single"]).sum())
    both = int((np.isfinite(column[ALBEDO])
                & np.isfinite(column["rice_fraction_single"])).sum())
    print(f"  cells with a rice fraction                {with_rice:>5}")
    print(f"  cells with both albedo and rice           {both:>5}")


def _run(table, column, weight, label):
    y = table.y

    results: list[Association] = []

    # ---- 3a leg one: does albedo correlate with methane? ---------------
    print("\n=== 3a. methane against the retrieval covariates ===")
    leg_one = [
        correlate(f"methane ~ {ALBEDO}", y, column[ALBEDO], weight=weight),
        correlate("methane ~ surface_albedo_NIR", y,
                  column["surface_albedo_NIR"], weight=weight),
        correlate("methane ~ solar_zenith_angle", y,
                  column["solar_zenith_angle"], weight=weight),
    ]
    show(leg_one)
    results += leg_one

    # ---- 3b leg two: does albedo correlate with the land cover? --------
    print("\n=== 3b. the covariates against the land-cover fractions ===")
    leg_two = [
        correlate(f"{ALBEDO} ~ impervious_fraction", column[ALBEDO],
                  column["impervious_fraction"], weight=weight),
        correlate(f"{ALBEDO} ~ rice_fraction_single", column[ALBEDO],
                  column["rice_fraction_single"], weight=weight),
        correlate("surface_albedo_NIR ~ impervious_fraction",
                  column["surface_albedo_NIR"], column["impervious_fraction"],
                  weight=weight),
        correlate("surface_albedo_NIR ~ rice_fraction_single",
                  column["surface_albedo_NIR"], column["rice_fraction_single"],
                  weight=weight),
    ]
    show(leg_two)
    results += leg_two

    # ---- the raw land-cover associations, for comparison ---------------
    print("\n=== the land-cover associations, raw ===")
    raw = [
        correlate("methane ~ impervious_fraction", y,
                  column["impervious_fraction"], weight=weight),
        correlate("methane ~ rice_fraction_single", y,
                  column["rice_fraction_single"], weight=weight),
    ]
    show(raw)
    results += raw

    # ---- 3a: the same associations with albedo partialled out ----------
    print("\n=== 3a. the same associations, controlling for albedo ===")
    controlled = [
        partial_correlation("methane ~ impervious_fraction", y,
                            column["impervious_fraction"], [column[ALBEDO]],
                            [ALBEDO], weight=weight),
        partial_correlation("methane ~ rice_fraction_single", y,
                            column["rice_fraction_single"], [column[ALBEDO]],
                            [ALBEDO], weight=weight),
        partial_correlation(
            "methane ~ impervious_fraction", y, column["impervious_fraction"],
            [column[ALBEDO], column["surface_albedo_NIR"],
             column["solar_zenith_angle"]],
            [ALBEDO, "surface_albedo_NIR", "solar_zenith_angle"], weight=weight),
        partial_correlation(
            "methane ~ rice_fraction_single", y, column["rice_fraction_single"],
            [column[ALBEDO], column["surface_albedo_NIR"],
             column["solar_zenith_angle"]],
            [ALBEDO, "surface_albedo_NIR", "solar_zenith_angle"], weight=weight),
    ]
    show(controlled)
    results += controlled

    _verdict(raw, controlled, leg_one, leg_two)
    return [(label, record) for record in results]


def _verdict(raw, controlled, leg_one, leg_two) -> None:
    """State whether the confounding path is open, and whether it matters."""
    print("\n=== verdict ===")
    albedo_methane = leg_one[0]
    print(f"  leg one, albedo to methane      Pearson {albedo_methane.pearson:+.3f}"
          f"  Spearman {albedo_methane.spearman:+.3f}  (n {albedo_methane.n})")
    for record in leg_two[:2]:
        print(f"  leg two, {record.name:<38} Pearson {record.pearson:+.3f}"
              f"  Spearman {record.spearman:+.3f}")

    for before, after in zip(raw, controlled[:2]):
        kept = (abs(after.pearson) / abs(before.pearson)
                if before.pearson else float("nan"))
        print(f"\n  {before.name}")
        print(f"    raw                Pearson {before.pearson:+.3f}  "
              f"Spearman {before.spearman:+.3f}")
        print(f"    given albedo       Pearson {after.pearson:+.3f}  "
              f"Spearman {after.spearman:+.3f}")
        print(f"    Pearson retained   {100 * kept:.1f}% of its magnitude"
              if np.isfinite(kept) else "    Pearson retained   undefined")


if __name__ == "__main__":
    raise SystemExit(main())
