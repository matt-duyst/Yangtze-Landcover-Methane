#!/usr/bin/env python3
"""Fit every baseline over the 2018 analysis grid and write the results table.

    python scripts/run_baselines.py                 # report only
    python scripts/run_baselines.py --write

Nothing here is a model of the study's question. These are the numbers a model
has to beat, established before there is a model with an interest in where the
bar sits. No network, tree ensemble or nonlinear fit belongs in this script.

Every model is run under two held-out schemes and both weightings, so each row
of the output is one model under one scheme at one weighting. In-sample and
held-out metrics sit side by side because the gap between them is the finding:
a model that fits the study area and does not transfer has learned the area.

Sample sizes differ by design and are carried on every row. Any model using
rice runs on the 532 cells that have a rice fraction; the impervious-only and
constant models could run on all 927. Metrics on different samples are not
comparable, so the impervious-only model is additionally run restricted to the
same 532 rows, which is the only like-for-like comparison against rice in the
table.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model.baselines import (  # noqa: E402
    GlobalMean,
    LinearModel,
    NeighbourMean,
    ProvinceMean,
    Table,
    evaluate,
    load_table,
    rows_for,
)

IMPERVIOUS = "impervious_fraction"
RICE = "rice_fraction_single"
RICE_BOTH = "rice_fraction_combined"

#: Wind enters as components plus speed, never as a bearing. A bearing is
#: circular, so 359 and 1 degrees are adjacent in the world and 358 apart in the
#: arithmetic, and a linear coefficient on it means nothing. A linear model in
#: (u, v) is a linear model in speed and direction jointly, in coordinates where
#: that discontinuity does not exist. Speed is added because it is a nonlinear
#: function of the pair and so carries something they do not.
WIND = ("wind_u", "wind_v", "wind_speed")
#: Position as a linear trend, the control every smooth covariate must clear.
TREND = ("centre_lat", "centre_lon")
ALBEDO = ("surface_albedo_SWIR",)
#: Everything the granules carry, for the most generous linear model available.
FULL = (*WIND, "surface_albedo_SWIR", "surface_albedo_NIR",
        "solar_zenith_angle", "surface_altitude", "surface_pressure")

FIELDS = ["model", "scheme", "weighting", "n", "dropped_missing",
          "in_sample_rmse_ppb", "in_sample_r2",
          "held_out_rmse_ppb", "held_out_r2", "detail"]

#: The published bar. An XGBoost downscaling of TROPOMI XCH4 to 1 km using
#: CarbonTracker, MODIS land surface temperature and cloud cover, and ERA-5
#: temperature and wind. Far more predictors than two land-cover fractions, and
#: a different target resolution, so it is a bar to be aware of rather than a
#: like-for-like comparison.
PUBLISHED_R2 = 0.63
PUBLISHED_RMSE_PPB = 13.26


def models(table: Table):
    """Every baseline, with the row subset each is honestly entitled to.

    A subset of None means all 927 rows. The restricted impervious model is the
    same model on the rice sample, present so the rice comparison is
    like-for-like rather than a comparison between two different study areas.
    """
    rice_rows = rows_for(table, LinearModel((RICE,)), on_missing="drop")
    tag = " [rice sample]"
    return [
        # On all 927 cells.
        (GlobalMean(), None),
        (ProvinceMean(), None),
        (NeighbourMean(), None),
        (LinearModel((IMPERVIOUS,)), None),
        # On the 532 cells that have a rice fraction. Every null is repeated
        # here, because a metric from the 927-cell sample says nothing about a
        # model fitted on 532 different cells and comparing them would be the
        # exact mistake this split exists to prevent.
        (GlobalMean(name=f"constant (global mean){tag}"), rice_rows),
        (ProvinceMean(name=f"constant (per province){tag}"), rice_rows),
        (NeighbourMean(name=f"spatial null (queen neighbour mean){tag}"), rice_rows),
        (LinearModel((IMPERVIOUS,), label=f"OLS {IMPERVIOUS}{tag}"), rice_rows),
        (LinearModel((RICE,)), None),
        (LinearModel((RICE_BOTH,)), None),
        (LinearModel((IMPERVIOUS, RICE)), None),
        (LinearModel((IMPERVIOUS, RICE), interaction=True), None),
        # A control, not a candidate. The methane field is smooth, so any smooth
        # function of position reproduces some of it; a covariate that beats the
        # spatial null but not this has only rediscovered where the cell is.
        (LinearModel(TREND, label="OLS trend surface (lat, lon)"), None),
    ] + covariate_models(table, rice_rows)


def covariate_models(table, rice_rows):
    """The meteorological models, when the covariate join has been done.

    Empty when the table has no covariate columns, so the script still runs
    against a grid alone and the earlier results stay reproducible.
    """
    if not all(name in table.columns for name in WIND):
        return []
    tag = " [rice sample]"
    return [
        (LinearModel(WIND, label="OLS wind (u, v, speed)"), None),
        (LinearModel(ALBEDO, label="OLS albedo (SWIR)"), None),
        (LinearModel((*WIND, IMPERVIOUS), label="OLS wind + impervious"), None),
        # Repeated on the rice sample so the models below have a null and a
        # wind-only comparison fitted on the same 532 cells.
        (LinearModel(WIND, label=f"OLS wind (u, v, speed){tag}"), rice_rows),
        (LinearModel(ALBEDO, label=f"OLS albedo (SWIR){tag}"), rice_rows),
        (LinearModel((*WIND, IMPERVIOUS, RICE),
                     label="OLS wind + both fractions"), None),
        (LinearModel((*FULL, IMPERVIOUS, RICE),
                     label="OLS full covariates + both fractions"), None),
        (LinearModel((*WIND, *TREND), label="OLS wind + trend surface"), None),
        # The control that matters most. Not a candidate model: it is a measure
        # of when each cell was sampled, and it has no physical content at all.
        (LinearModel(("sampling_season",),
                     label="OLS sampling composition (when observed)"), None),
    ]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--grid", default=str(REPO / "data" / "processed" /
                                              "analysis_grid_2018.csv"))
    parser.add_argument("--target", default="ch4_bias_corrected_ppb")
    parser.add_argument("--target-from", default=None,
                        help="companion table holding the target column, "
                             "matched to cells by centre")
    parser.add_argument("--covariates", default=None,
                        help="composite covariate CSV to join onto the grid; "
                             "without it only the land-cover models are run")
    parser.add_argument("--out", default=str(REPO / "data" / "processed" /
                                             "baseline_results_2018.csv"))
    parser.add_argument("--block", type=int, default=4,
                        help="spatial block side in cells; 4 is one degree")
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    table = load_table(args.grid, target=args.target,
                       target_from=args.target_from,
                       covariates=args.covariates)
    if args.target_from:
        print(f"  target {args.target} joined from "
              f"{Path(args.target_from).name}")
    if args.covariates:
        present = [n for n in (*WIND, *FULL) if n in table.columns]
        print(f"  joined {len(set(present))} covariate columns from "
              f"{Path(args.covariates).name}")
    print(f"  {table.n} cells; target {args.target}, "
          f"weighted mean {np.average(table.y, weights=table.weight):.2f} ppb, "
          f"unweighted {table.y.mean():.2f} ppb, sd {table.y.std():.2f} ppb")
    print(f"  soundings per cell: min {int(table.weight.min())}, "
          f"median {int(np.median(table.weight))}, max {int(table.weight.max())}")
    groups = {p: int((table.province == p).sum()) for p in sorted(set(table.province))}
    print(f"  leave-one-province-out folds: {groups}")

    results = []
    for model, subset in models(table):
        for scheme in ("leave-one-province-out", "spatial blocks"):
            extra = ({"block": args.block, "folds": args.folds, "seed": args.seed}
                     if scheme == "spatial blocks" else {})
            for weighted in (False, True):
                results.append(evaluate(table, model, scheme=scheme,
                                        weighted=weighted, index=subset,
                                        **extra))

    _table(results)
    _commentary(results, table)

    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            for result in results:
                writer.writerow(result.as_dict())
        print(f"\n  wrote {out}  ({out.stat().st_size:,} B, {len(results)} rows)")
    else:
        print("\n  report only: nothing written. Pass --write to save the table.")
    return 0


def _table(results):
    print(f"\n{'model':<46} {'scheme':<24} {'weighting':<18} {'n':>4} "
          f"{'in RMSE':>9} {'in R2':>8} {'out RMSE':>9} {'out R2':>8}")
    print("-" * 132)
    for r in results:
        print(f"{r.model:<46} {r.scheme:<24} {r.weighting:<18} {r.n:>4} "
              f"{r.in_sample.rmse:>9.3f} {r.in_sample.r2:>8.3f} "
              f"{r.held_out.rmse:>9.3f} {r.held_out.r2:>8.3f}")


def _best(results, scheme, weighting, predicate=lambda r: True):
    chosen = [r for r in results if r.scheme == scheme and r.weighting == weighting
              and predicate(r)]
    return min(chosen, key=lambda r: r.held_out.rmse) if chosen else None


def _sample_of(result) -> str:
    """Which sample a result belongs to, keyed by the rows it actually used.

    Grouping has to be by ``n`` and not by the label. A model needing rice
    silently runs on the 532 rows that have it, whether or not its name says so,
    and grouping by name would have put ``OLS rice_fraction_single`` alongside
    nulls fitted on all 927 cells. That is the comparison this split exists to
    prevent, and it is easy to make by accident.
    """
    return f"{result.n} cells"


def _samples(results) -> list[str]:
    return sorted(set(_sample_of(r) for r in results),
                  key=lambda s: -int(s.split()[0]))


def _commentary(results, table):
    """The comparisons the table exists to support, stated rather than implied.

    Comparisons are made only within a sample. A model fitted on the 532 cells
    that have a rice fraction cannot be ranked against a null fitted on all 927,
    because the two describe different study areas: the 395 cells without rice
    are disproportionately coastal and outside the provinces, and dropping them
    removes a chunk of the field's spread rather than a random slice of it.
    """
    for sample in _samples(results):
        for weighting in ("unweighted", "by sounding count"):
            for scheme in ("leave-one-province-out", "spatial blocks"):
                here = {r.model: r for r in results
                        if r.scheme == scheme and r.weighting == weighting
                        and _sample_of(r) == sample}
                nulls = {k: v for k, v in here.items() if "OLS" not in k}
                constant = next(v for k, v in nulls.items() if "global" in k)
                province = next(v for k, v in nulls.items() if "province" in k)
                spatial = next(v for k, v in nulls.items() if "spatial" in k)
                print(f"\n=== {sample} | {scheme} | {weighting} ===")
                print(f"  global constant   {constant.held_out.rmse:7.3f} ppb "
                      f"held out (R2 {constant.held_out.r2:+.3f})")
                print(f"  province constant {province.held_out.rmse:7.3f} ppb "
                      f"held out (R2 {province.held_out.r2:+.3f})")
                print(f"  spatial null      {spatial.held_out.rmse:7.3f} ppb "
                      f"held out (R2 {spatial.held_out.r2:+.3f})")
                for name, result in here.items():
                    if name in nulls:
                        continue
                    marks = []
                    for label, null in (("global", constant),
                                        ("province", province),
                                        ("spatial null", spatial)):
                        if result.held_out.rmse < null.held_out.rmse:
                            marks.append(f"beats {label}")
                    short = name.replace(" [rice sample]", "")
                    print(f"  {short:<58} {result.held_out.rmse:7.3f} ppb  "
                          f"{', '.join(marks) if marks else 'beats none of them'}")

    print("\n=== against the published bar ===")
    for sample in _samples(results):
        best = min((r for r in results if _sample_of(r) == sample),
                   key=lambda r: r.held_out.rmse)
        print(f"  {sample}: best held-out is {best.model} under {best.scheme}, "
              f"{best.weighting}, RMSE {best.held_out.rmse:.3f} ppb, "
              f"R2 {best.held_out.r2:+.3f}, n={best.n}")
    print(f"  published XGBoost downscaling: RMSE {PUBLISHED_RMSE_PPB} ppb, "
          f"R2 {PUBLISHED_R2}. Richer predictors, 1 km target, different area: "
          f"a bar to be aware of, not a like-for-like comparison.")

    print("\n=== linear coefficients, in sample ===")
    for weighting in ("unweighted", "by sounding count"):
        print(f"  {weighting}:")
        for r in results:
            if r.detail and r.weighting == weighting \
                    and r.scheme == "leave-one-province-out" and "OLS" in r.model:
                print(f"    {r.model:<58} {r.detail}")

    print("\n=== how much the spatial null had to fall back ===")
    for r in results:
        if "spatial null" in r.model and r.detail:
            print(f"  {r.model:<50} {r.scheme:<24} {r.weighting:<18} {r.detail}")


if __name__ == "__main__":
    raise SystemExit(main())
