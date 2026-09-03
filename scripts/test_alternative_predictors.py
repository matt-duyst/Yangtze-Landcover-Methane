#!/usr/bin/env python3
"""Does the negative land-cover finding survive better predictors?

    python scripts/test_alternative_predictors.py
    python scripts/test_alternative_predictors.py --write

Measurement error in a predictor attenuates an association toward zero, so it
makes a negative finding less trustworthy rather than more. Both land-cover
predictors carry documented error: GAIA is reported to omit impervious surface
relative to GISA, and the NESDC rice rasters have pinned provincial totals, an
unclassified region in northern and western Anhui, and no declared nodata. If
the association is equally near zero computed from independently built
products, measurement error is not the explanation.

The two alternatives are not equivalent substitutes. GISA is an independent
Landsat classification of the same quantity GAIA classifies. GloRice is not an
independent observation of rice at all: it allocates official statistics to grid
cells through a model, so it inherits the statistics' accuracy and the
allocation's assumptions. Its value here is that its errors are uncorrelated
with the NESDC classification's, not that it is closer to the truth.

The four grids this reads are built by scripts/build_analysis_grid.py with
--urban-source and --rice-source, and the baseline tables by
scripts/run_baselines.py over each. Both are slow enough to be separate steps.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model.association import correlate, partial_correlation  # noqa: E402
from src.model.baselines import join_column, load_table  # noqa: E402

URBAN = ("gaia", "gisa")
RICE = ("nesdc", "glorice")
ALBEDO = "surface_albedo_SWIR"
NULL = "spatial null (queen neighbour mean)"
LAND_COVER = (
    "OLS impervious_fraction", "OLS impervious_fraction [rice sample]",
    "OLS rice_fraction_single", "OLS rice_fraction_combined",
    "OLS impervious_fraction + rice_fraction_single",
    "OLS impervious_fraction + rice_fraction_single + interaction")

BASELINE_FIELDS = ["predictors", "model", "scheme", "weighting", "n",
                   "in_sample_rmse_ppb", "in_sample_r2",
                   "held_out_rmse_ppb", "held_out_r2", "beats_spatial_null"]
COMPARISON_FIELDS = ["predictor", "methane_field", "weighting", "n",
                     "pearson", "spearman",
                     "partial_pearson_given_albedo", "partial_pearson_p",
                     "partial_spearman_given_albedo"]


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--grids", default=str(REPO / "data" / "interim" / "alt_grids"))
    parser.add_argument("--base", default=str(REPO / "data" / "processed" /
                                              "analysis_grid_2018.csv"))
    parser.add_argument("--covariates", default=str(REPO / "data" / "processed" /
                                                    "methane_covariates_2018.csv"))
    parser.add_argument("--out-baselines",
                        default=str(REPO / "data" / "processed" /
                                    "alternative_predictors_2018.csv"))
    parser.add_argument("--out-comparison",
                        default=str(REPO / "data" / "processed" /
                                    "predictor_comparison_2018.csv"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    grids = Path(args.grids)

    table = load_table(args.base, covariates=args.covariates)
    lat, lon = table.columns["centre_lat"], table.columns["centre_lon"]
    albedo = table.columns[ALBEDO]
    corrected = table.y
    raw = np.array([float(r["ch4_raw_ppb"]) for r in
                    csv.DictReader(open(args.base, newline=""))])

    def column(name, field):
        path = grids / f"grid_{name}.csv"
        if not path.exists():
            raise SystemExit(f"missing {path}; build it with "
                             f"scripts/build_analysis_grid.py --write --out {path}")
        return join_column(list(csv.DictReader(open(path, newline=""))),
                           lat, lon, field)

    predictors = {
        "GAIA": column("gaia_nesdc", "impervious_fraction"),
        "GISA": column("gisa_nesdc", "impervious_fraction"),
        "NESDC": column("gaia_nesdc", "rice_fraction_single"),
        "GloRice": column("gaia_glorice", "rice_fraction_single"),
    }
    comparison = _describe(predictors, corrected, raw, albedo, table.weight)
    baselines = _collect(grids)
    _verdict(baselines)

    if args.write:
        _dump(Path(args.out_comparison), COMPARISON_FIELDS, comparison)
        _dump(Path(args.out_baselines), BASELINE_FIELDS, baselines)
    else:
        print("\n  report only: nothing written. Pass --write to save.")
    return 0


def _dump(path, fields, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {path}  ({path.stat().st_size:,} B, {len(rows)} rows)")


def _describe(predictors, corrected, raw, albedo, weight):
    print("=== how the products compare with each other ===")
    gaia, gisa = predictors["GAIA"], predictors["GISA"]
    agree = correlate("urban", gaia, gisa)
    difference = gisa - gaia
    print(f"  GAIA vs GISA impervious: Pearson {agree.pearson:+.4f}, "
          f"Spearman {agree.spearman:+.4f}, n {agree.n}")
    print(f"    GISA minus GAIA: mean {difference.mean():+.4f}, "
          f"sd {difference.std():.4f}, median {np.median(difference):+.4f}, "
          f"range {difference.min():+.4f} to {difference.max():+.4f}")
    print(f"    GISA is the larger in {int((difference > 0).sum())} of "
          f"{difference.size} cells")

    nesdc, glorice = predictors["NESDC"], predictors["GloRice"]
    both = np.isfinite(nesdc) & np.isfinite(glorice)
    shared = correlate("rice", nesdc[both], glorice[both])
    print(f"  NESDC vs GloRice rice, on the {int(both.sum())} cells with both: "
          f"Pearson {shared.pearson:+.4f}, Spearman {shared.spearman:+.4f}")
    print(f"    NESDC covers {int(np.isfinite(nesdc).sum())} cells, "
          f"GloRice {int(np.isfinite(glorice).sum())}")

    print("\n=== each predictor against methane, raw and controlling for albedo ===")
    print(f"  {'predictor':<10}{'field':<11}{'w':<5}{'n':>5}{'Pearson':>10}"
          f"{'Spearman':>10}{'| albedo':>10}{'p':>11}")
    rows = []
    for name, values in predictors.items():
        for field, y in (("bias corrected", corrected), ("raw", raw)):
            for label, w in (("unw", None), ("wtd", weight)):
                c = correlate(name, y, values, weight=w)
                p = partial_correlation(name, y, values, [albedo], [ALBEDO],
                                        weight=w)
                print(f"  {name:<10}{field:<11}{label:<5}{c.n:>5}"
                      f"{c.pearson:>+10.3f}{c.spearman:>+10.3f}"
                      f"{p.pearson:>+10.3f}{p.pearson_p:>11.2e}")
                rows.append({
                    "predictor": name, "methane_field": field,
                    "weighting": "unweighted" if w is None else "by sounding count",
                    "n": c.n, "pearson": round(c.pearson, 4),
                    "spearman": round(c.spearman, 4),
                    "partial_pearson_given_albedo": round(p.pearson, 4),
                    "partial_pearson_p": f"{p.pearson_p:.3e}",
                    "partial_spearman_given_albedo": round(p.spearman, 4),
                })
    return rows


def _collect(grids):
    """Every baseline row from the four runs, tagged with its predictor pair."""
    rows = []
    for urban in URBAN:
        for rice in RICE:
            path = grids / f"bl_{urban}_{rice}.csv"
            if not path.exists():
                raise SystemExit(f"missing {path}; run scripts/run_baselines.py "
                                 f"over grid_{urban}_{rice}.csv")
            records = list(csv.DictReader(open(path, newline="")))
            nulls = {(r["scheme"], r["weighting"], r["n"]):
                     float(r["held_out_rmse_ppb"])
                     for r in records if r["model"].startswith(NULL)}
            for record in records:
                key = (record["scheme"], record["weighting"], record["n"])
                null = nulls.get(key)
                beats = (record["model"] in LAND_COVER and null is not None
                         and float(record["held_out_rmse_ppb"]) < null)
                rows.append({
                    "predictors": f"{urban}+{rice}",
                    "model": record["model"], "scheme": record["scheme"],
                    "weighting": record["weighting"], "n": record["n"],
                    "in_sample_rmse_ppb": record["in_sample_rmse_ppb"],
                    "in_sample_r2": record["in_sample_r2"],
                    "held_out_rmse_ppb": record["held_out_rmse_ppb"],
                    "held_out_r2": record["held_out_r2"],
                    "beats_spatial_null": "yes" if beats else "no",
                })
    return rows


def _verdict(rows):
    print("\n=== does any land-cover model beat the spatial null? ===")
    weighted = [r for r in rows if r["weighting"] == "by sounding count"
                and r["beats_spatial_null"] == "yes"]
    print(f"  under inverse-variance weighting, across all four predictor pairs, "
          f"both schemes and both sample sizes: {len(weighted)} cases")
    unweighted = [r for r in rows if r["weighting"] == "unweighted"
                  and r["beats_spatial_null"] == "yes"]
    print(f"  unweighted: {len(unweighted)} cases")
    for r in unweighted:
        print(f"    {r['predictors']:<16}n={r['n']:<5}{r['scheme']:<24}"
              f"{r['model'][:44]:<46}{float(r['held_out_rmse_ppb']):.3f}")


if __name__ == "__main__":
    raise SystemExit(main())
