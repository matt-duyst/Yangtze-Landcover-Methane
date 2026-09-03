#!/usr/bin/env python3
"""Does Sentinel-5P's operational bias correction reduce the albedo dependence?

    python scripts/test_albedo_correction.py
    python scripts/test_albedo_correction.py --write

Reads committed tables only. No download, no re-run.

The composite grids both methane variables. ``methane_mixing_ratio`` is the raw
retrieval and ``methane_mixing_ratio_bias_corrected`` is the operational
product, and the correction the latter carries is described in the literature as
an a posteriori correction for underestimation at low surface albedo and
overestimation at high albedo. This repository measured a strong positive
association between composite methane and composite albedo without ever
establishing which of the two variables produced it, or whether the correction
reduces the dependence at all.

Every association reported anywhere in this repository used the bias-corrected
variable. ``src.model.baselines.TARGET`` is ``ch4_bias_corrected_ppb`` and both
analysis scripts take that default, so the figures on record are post-correction
figures. This script recomputes them on the raw variable, on the corrected one,
and on the correction itself, so the effect of the correction is visible rather
than assumed.

Slopes matter more than correlations here. A correlation says how tightly two
things move together and depends on how much albedo happened to vary in this
sample; a slope in ppb per unit albedo is comparable against a published
residual sensitivity. The comparison is still not like for like: a published
residual is measured after correction against reference data, while a slope
fitted across an annual composite absorbs everything else that varies spatially
with albedo. The slope here is an upper bound on residual albedo sensitivity,
not a measurement of it.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model.association import correlate, sensitivity  # noqa: E402
from src.model.baselines import join_column, load_table  # noqa: E402

ALBEDOS = ("surface_albedo_SWIR", "surface_albedo_NIR")

FIELDS = ["albedo", "series", "weighting", "n", "pearson", "spearman",
          "slope_ppb_per_unit_albedo", "standard_error", "r2"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--grid", default=str(REPO / "data" / "processed" /
                                              "analysis_grid_2018.csv"))
    parser.add_argument("--covariates", default=str(REPO / "data" / "processed" /
                                                    "methane_covariates_2018.csv"))
    parser.add_argument("--deseasonalised",
                        default=str(REPO / "data" / "processed" /
                                    "methane_deseasonalised_2018.csv"))
    parser.add_argument("--out", default=str(REPO / "data" / "processed" /
                                             "albedo_correction_2018.csv"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    table = load_table(args.grid, covariates=args.covariates)
    grid = list(csv.DictReader(open(args.grid, newline="")))
    corrected = table.y
    raw = np.array([float(r["ch4_raw_ppb"]) for r in grid])
    correction = corrected - raw
    companion = list(csv.DictReader(open(args.deseasonalised, newline="")))
    mu = join_column(companion, table.columns["centre_lat"],
                     table.columns["centre_lon"], "ch4_deseasonalised_ppb")

    series = (("raw retrieval", raw),
              ("bias corrected", corrected),
              ("the correction itself", correction),
              ("deseasonalised", mu))

    print("=== the correction ===")
    print(f"  cells {table.n}, all of which differ: "
          f"{bool((correction != 0).all())}")
    print(f"  mean {correction.mean():+.3f} ppb, sd {correction.std():.3f}, "
          f"range {correction.max() - correction.min():.3f} "
          f"({correction.min():+.3f} to {correction.max():+.3f})")

    rows = []
    for albedo in ALBEDOS:
        x = table.columns[albedo]
        print(f"\n=== against {albedo} "
              f"(range {x.min():+.4f} to {x.max():+.4f}) ===")
        print(f"  {'series':<24}{'w':<5}{'n':>5}{'Pearson':>10}{'Spearman':>10}"
              f"{'ppb/albedo':>13}{'se':>8}{'R2':>9}")
        for label, y in series:
            for weighting, weight in (("unw", None), ("wtd", table.weight)):
                c = correlate(label, y, x, weight=weight)
                s = sensitivity(label, y, x, weight=weight)
                print(f"  {label:<24}{weighting:<5}{c.n:>5}{c.pearson:>+10.3f}"
                      f"{c.spearman:>+10.3f}{s.slope:>13.2f}"
                      f"{s.standard_error:>8.2f}{s.r2:>9.4f}")
                rows.append({
                    "albedo": albedo, "series": label,
                    "weighting": "unweighted" if weight is None
                                 else "by sounding count",
                    "n": c.n,
                    "pearson": round(c.pearson, 4),
                    "spearman": round(c.spearman, 4),
                    "slope_ppb_per_unit_albedo": round(s.slope, 3),
                    "standard_error": round(s.standard_error, 3),
                    "r2": round(s.r2, 6),
                })

    _verdict(rows)

    if args.write:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=FIELDS)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\n  wrote {out}  ({out.stat().st_size:,} B, {len(rows)} rows)")
    else:
        print("\n  report only: nothing written. Pass --write to save.")
    return 0


def _find(rows, albedo, series, weighting):
    for row in rows:
        if (row["albedo"] == albedo and row["series"] == series
                and row["weighting"] == weighting):
            return row
    raise KeyError((albedo, series, weighting))


def _verdict(rows) -> None:
    print("\n=== does the correction reduce the albedo dependence? ===")
    for albedo in ALBEDOS:
        for weighting in ("unweighted", "by sounding count"):
            before = _find(rows, albedo, "raw retrieval", weighting)
            after = _find(rows, albedo, "bias corrected", weighting)
            change = ((after["slope_ppb_per_unit_albedo"]
                       - before["slope_ppb_per_unit_albedo"])
                      / abs(before["slope_ppb_per_unit_albedo"]) * 100)
            print(f"  {albedo:<20}{weighting:<18}"
                  f"{before['slope_ppb_per_unit_albedo']:8.2f} -> "
                  f"{after['slope_ppb_per_unit_albedo']:8.2f} ppb/albedo "
                  f"({change:+.1f}%), Pearson {before['pearson']:+.3f} -> "
                  f"{after['pearson']:+.3f}")
    residual = _find(rows, "surface_albedo_SWIR", "bias corrected", "unweighted")
    print(f"\n  residual sensitivity of the corrected variable: "
          f"{residual['slope_ppb_per_unit_albedo']:.2f} "
          f"+/- {residual['standard_error']:.2f} ppb per unit albedo, "
          f"R2 {residual['r2']:.4f}")
    print("  a published residual for a differently corrected product is of "
          "order 1 ppb per unit albedo at R2 near zero; see notes/decisions.md "
          "for what that comparison does and does not support")


if __name__ == "__main__":
    raise SystemExit(main())
