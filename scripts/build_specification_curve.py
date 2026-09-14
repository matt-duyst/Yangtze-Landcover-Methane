#!/usr/bin/env python3
"""Every defensible specification of the land-cover result, in one ordered table.

`notes/grounding-methods.md` records specification curve analysis as the
reporting frame for a result that varies across defensible analytical choices.
This project has four methane fields, several predictor sets, two
cross-validation schemes, three weightings and five preprocessing variants, and
`notes/decisions.md` already reports the land-cover result as a range across
four scheme-weighting combinations rather than as a single number. The curve is
where the range becomes inspectable instead of asserted.

**Assembled rather than recomputed.** Every row here is read from a committed
artefact that a recipe reproduces: the three baseline result tables and the
preprocessing sensitivity table. Nothing is refitted, so the curve cannot
disagree with the tables it summarises.

**What counts as a specification.** One choice of field, land-cover predictor
set, cross-validation scheme, weighting and preprocessing variant. Only
predictor sets that are *land cover alone* are included -- `wind + impervious`
is a different claim and belongs to the confounding analysis, not here.

**Two definitions of "positive", and the stricter one is the paper's.** A
specification is *nominally positive* if its held-out R squared exceeds zero,
which only says the model beat the sample mean. It *beats the benchmark* if it
also exceeds the spatial null fitted under the identical specification, which is
the comparison the paper's claim is stated against. The second is reported as
the headline because the first is satisfiable by any predictor with a spatial
gradient.

**The duplicate that had to be dropped.** The sensitivity table's "committed (no
filter)" variant is by construction the same fit as the operational baseline
table's, so those rows would otherwise appear twice and weight the curve toward
the operational field. They are taken once, from the baseline table.

Run with no arguments to report; ``--write`` to write the artefact.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
PROCESSED = REPO / "data" / "processed"
OUT = PROCESSED / "specification_curve_2018.csv"

#: Baseline tables, one per field.
BASELINES = {
    "operational": "baseline_results_2018.csv",
    "blended": "baseline_results_blended_2018.csv",
    "deseasonalised": "baseline_results_deseasonalised_2018.csv",
}

SENSITIVITY = "preprocessing_sensitivity_2018.csv"

#: Land cover alone. `wind + impervious` and the covariate models are excluded:
#: they test confounding rather than the land-cover claim.
LAND_COVER = (
    "OLS impervious_fraction",
    "OLS impervious_fraction [rice sample]",
    "OLS rice_fraction_single",
    "OLS rice_fraction_combined",
    "OLS impervious_fraction + rice_fraction_single",
    "OLS impervious_fraction + rice_fraction_single + interaction",
)

NULL = "spatial null (queen neighbour mean)"


def read(name: str) -> list[dict]:
    with (PROCESSED / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def collect() -> list[dict]:
    rows: list[dict] = []

    for field, table in BASELINES.items():
        records = read(table)
        nulls = {(r["scheme"], r["weighting"]): float(r["held_out_r2"])
                 for r in records if r["model"] == NULL}
        for r in records:
            if r["model"] not in LAND_COVER:
                continue
            rows.append(dict(
                field=field, predictors=r["model"], scheme=r["scheme"],
                weighting=r["weighting"], preprocessing="committed",
                n=r["n"], held_out_r2=float(r["held_out_r2"]),
                benchmark_r2=nulls[(r["scheme"], r["weighting"])],
                source=table))

    if (PROCESSED / SENSITIVITY).exists():
        records = read(SENSITIVITY)
        nulls = {(r["variant"], r["scheme"], r["weighting"]):
                 float(r["held_out_r2"])
                 for r in records if r["model"] == NULL}
        for r in records:
            # The committed variant duplicates the operational baseline rows.
            if r["model"] not in LAND_COVER or \
                    r["variant"] == "committed (no filter)":
                continue
            weighting = r["weighting"]
            preprocessing = r["variant"]
            if preprocessing == "representativeness weighting":
                # This variant *is* a weighting, not a preprocessing step, so
                # it is recorded on the axis it belongs to. Its "by sounding
                # count" rows are the ones whose weight column holds the
                # representativeness weight. Its "unweighted" rows are ordinary
                # unweighted fits that happen to sit on the 905-cell subset
                # with a weight defined, which is not a specification anyone
                # would choose, so they are dropped.
                if weighting == "unweighted":
                    continue
                weighting, preprocessing = "by representativeness", "committed"
            value = float(r["held_out_r2"])
            if not np.isfinite(value):
                continue
            rows.append(dict(
                field="operational", predictors=r["model"], scheme=r["scheme"],
                weighting=weighting, preprocessing=preprocessing,
                n=r["n"], held_out_r2=value,
                benchmark_r2=nulls[(r["variant"], r["scheme"], r["weighting"])],
                source=SENSITIVITY))

    rows.sort(key=lambda r: r["held_out_r2"])
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
        row["nominally_positive"] = "yes" if row["held_out_r2"] > 0 else "no"
        row["beats_benchmark"] = (
            "yes" if row["held_out_r2"] > row["benchmark_r2"] else "no")
        row["held_out_r2"] = f"{row['held_out_r2']:+.4f}"
        row["benchmark_r2"] = f"{row['benchmark_r2']:+.4f}"
    return rows


def report(rows: list[dict]) -> None:
    values = np.array([float(r["held_out_r2"]) for r in rows])
    positive = [r for r in rows if r["nominally_positive"] == "yes"]
    beating = [r for r in rows if r["beats_benchmark"] == "yes"]

    print(f"  {len(rows)} specifications, held-out R squared from "
          f"{values.min():+.4f} to {values.max():+.4f}")
    print(f"  median {np.median(values):+.4f}, "
          f"interquartile {np.percentile(values, 25):+.4f} to "
          f"{np.percentile(values, 75):+.4f}")
    print(f"  nominally positive (beats the sample mean): "
          f"{len(positive)} of {len(rows)}")
    print(f"  BEATS THE SPATIAL NULL in the same specification: "
          f"{len(beating)} of {len(rows)}")

    if beating:
        print("\n  the specifications that beat the benchmark:")
        for r in beating:
            print(f"    {r['field']:<15}{r['predictors']:<48}"
                  f"{r['scheme'][:14]:<15}{r['weighting'][:21]:<22}"
                  f"{r['preprocessing'][:26]:<27}"
                  f"{r['held_out_r2']:>9} vs {r['benchmark_r2']:>9}")

    print("\n  spread attributable to each axis, as the range of medians "
          "across its levels:")
    for axis in ("field", "predictors", "scheme", "weighting", "preprocessing"):
        medians = {}
        for r in rows:
            medians.setdefault(r[axis], []).append(float(r["held_out_r2"]))
        summary = {k: float(np.median(v)) for k, v in medians.items()}
        spread = max(summary.values()) - min(summary.values())
        worst = min(summary, key=summary.get)
        best = max(summary, key=summary.get)
        print(f"    {axis:<16}{spread:.4f}   lowest {worst[:34]!r} "
              f"{summary[worst]:+.4f}, highest {best[:34]!r} {summary[best]:+.4f}")

    print("\n  the five worst and five best specifications:")
    for r in rows[:5] + rows[-5:]:
        print(f"    {r['rank']:>4}  {r['held_out_r2']:>9}  {r['field']:<15}"
              f"{r['predictors']:<48}{r['scheme'][:14]:<15}"
              f"{r['weighting'][:21]:<22}{r['preprocessing'][:26]}")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    rows = collect()
    fields = ["rank", "field", "predictors", "scheme", "weighting",
              "preprocessing", "n", "held_out_r2", "benchmark_r2",
              "nominally_positive", "beats_benchmark", "source"]
    report(rows)

    if args.write:
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields)
            writer.writeheader()
            writer.writerows({k: r[k] for k in fields} for r in rows)
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
