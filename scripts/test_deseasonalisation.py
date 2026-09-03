#!/usr/bin/env python3
"""Did removing the seasonal cycle remove the sampling artefact?

    python scripts/test_deseasonalisation.py
    python scripts/test_deseasonalisation.py --write

The whole pass exists for this question, so it is answered before anything
else. Each relationship is computed on the raw composite mean and on the
deseasonalised offsets, over the same cells with the same weights, and the two
are printed side by side.

There are three things to look for and they are not the same thing. If the
sampling-composition correlations collapse, the deseasonalisation worked. If
they do not, it failed and no amount of interpretation rescues it. And if the
land-cover correlations sit at zero on the corrected field, that is the same
negative finding as before but on a sound object, which is a stronger result
than the same finding on a contaminated one rather than a weaker one.

The sampling axis is reported two ways. Mean day of year comes straight from
the composite now, accumulated per cell alongside the harmonic statistics. Mean
solar zenith angle is the covariate that first exposed the problem and is kept
because it was the diagnostic, not because it is the better measure.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model.association import correlate  # noqa: E402
from src.model.baselines import load_table  # noqa: E402

RAW = "ch4_bias_corrected_ppb"
MU = "ch4_deseasonalised_ppb"

#: Grouped so the report reads as an argument rather than a list. The first
#: group is the artefact, the second the covariates it contaminated, the third
#: the question the study actually asks.
GROUPS = (
    ("sampling composition", ("mean_day_of_year", "solar_zenith_angle",
                              "day_of_year_sd")),
    ("retrieval and meteorology", ("surface_albedo_SWIR", "surface_albedo_NIR",
                                   "wind_u", "wind_v", "wind_speed")),
    ("land cover", ("impervious_fraction", "rice_fraction_single",
                    "rice_fraction_combined")),
)

FIELDS = ["group", "predictor", "weighting", "n",
          "raw_pearson", "raw_spearman", "mu_pearson", "mu_spearman",
          "pearson_change", "spearman_change"]


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
                                             "deseasonalisation_2018.csv"))
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)

    table = load_table(args.grid, covariates=args.covariates)
    companion = list(csv.DictReader(open(args.deseasonalised, newline="")))
    from src.model.baselines import join_column
    lat, lon = table.columns["centre_lat"], table.columns["centre_lon"]
    mu = join_column(companion, lat, lon, MU)
    for name in ("mean_day_of_year", "day_of_year_sd", "poorly_identified"):
        table.columns[name] = join_column(companion, lat, lon, name)

    raw = table.y
    print(f"=== the two fields ===")
    print(f"  cells                         {table.n}")
    print(f"  raw composite mean            {raw.mean():9.3f} ppb, "
          f"sd {raw.std():6.3f}")
    print(f"  deseasonalised offsets        {np.nanmean(mu):9.3f} ppb, "
          f"sd {np.nanstd(mu):6.3f}")
    print(f"  correlation between them      "
          f"{correlate('raw ~ mu', raw, mu).pearson:+.4f}")
    flagged = int(np.nansum(table.columns["poorly_identified"]))
    print(f"  cells flagged poorly identified {flagged}")
    spread = table.columns["day_of_year_sd"]
    print(f"  sampling spread, days         min {np.nanmin(spread):.2f}  "
          f"median {np.nanmedian(spread):.2f}  max {np.nanmax(spread):.2f}")

    rows = []
    for label, weight in (("unweighted", None),
                          ("by sounding count", table.weight)):
        print(f"\n{'=' * 96}\n=== {label} ===\n{'=' * 96}")
        print(f"  {'predictor':<26}{'n':>5}"
              f"{'raw Pear':>10}{'mu Pear':>10}{'change':>9}"
              f"{'raw Spear':>11}{'mu Spear':>10}{'change':>9}")
        for group, names in GROUPS:
            print(f"  -- {group} --")
            for name in names:
                if name not in table.columns:
                    print(f"  {name:<26} absent from the table")
                    continue
                x = table.columns[name]
                before = correlate(f"raw ~ {name}", raw, x, weight=weight)
                after = correlate(f"mu ~ {name}", mu, x, weight=weight)
                print(f"  {name:<26}{after.n:>5}"
                      f"{before.pearson:>+10.3f}{after.pearson:>+10.3f}"
                      f"{after.pearson - before.pearson:>+9.3f}"
                      f"{before.spearman:>+11.3f}{after.spearman:>+10.3f}"
                      f"{after.spearman - before.spearman:>+9.3f}")
                rows.append({
                    "group": group, "predictor": name, "weighting": label,
                    "n": after.n,
                    "raw_pearson": round(before.pearson, 4),
                    "raw_spearman": round(before.spearman, 4),
                    "mu_pearson": round(after.pearson, 4),
                    "mu_spearman": round(after.spearman, 4),
                    "pearson_change": round(after.pearson - before.pearson, 4),
                    "spearman_change": round(after.spearman - before.spearman, 4),
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


def _verdict(rows) -> None:
    """Say whether it worked, in the terms the question was asked in."""
    print("\n=== verdict ===")
    for label in ("unweighted", "by sounding count"):
        here = [r for r in rows if r["weighting"] == label]
        sampling = [r for r in here if r["group"] == "sampling composition"]
        land = [r for r in here if r["group"] == "land cover"]
        worst_before = max(abs(r["raw_pearson"]) for r in sampling)
        worst_after = max(abs(r["mu_pearson"]) for r in sampling)
        land_after = max(abs(r["mu_pearson"]) for r in land)
        print(f"  {label}:")
        print(f"    strongest sampling correlation {worst_before:+.3f} "
              f"-> {worst_after:+.3f}")
        print(f"    strongest land-cover correlation on the corrected field "
              f"{land_after:+.3f}")
        if worst_after < 0.15:
            print("    the sampling artefact is removed")
        elif worst_after < 0.5 * worst_before:
            print("    the sampling artefact is reduced but NOT removed")
        else:
            print("    the sampling artefact SURVIVES; deseasonalising failed")


if __name__ == "__main__":
    raise SystemExit(main())
