#!/usr/bin/env python3
"""Equivalence tests for the land-cover associations, against named bounds.

**Why this exists and what it changes.** `notes/grounding-methods.md` records
that a conventional test can argue against a null and never in favour of one,
so "no association was detected" is the strongest claim this project has been
entitled to. Equivalence testing is what licenses the stronger form. It is two
one-sided tests against non-nil nulls at plus and minus a smallest effect size
of interest, and the record is explicit about the interval: "because the
equivalence test is based on two one-sided tests, a 90% confidence interval is
appropriate when those tests are assessed against the 5% alpha level".

**The bound is a scientific judgement, so all three candidates are reported and
one is named primary.**

*The policy bound is unavailable, and that is a finding rather than an
omission.* `notes/grounding-rice.md` records that water regime moves rice
emissions by a factor of about 13.7 at constant area, and that variety, straw
and nitrogen each move them by tens of percent. Those are bounds on
**emissions**. Converting an emission change into a column-methane change needs
a transport model, which is precisely what this study does not run and says it
does not run. So the most defensible basis in the record cannot be reached from
here, and saying so is more useful than substituting an arbitrary number for it.

*The comparative bound is primary.* The paper's claim is already comparative --
land cover fails *relative to* a spatial null -- so setting the bound at the
null's own explanatory power introduces no arbitrary fraction and tests exactly
the sentence the paper wants to write. `SPATIAL_NULL_R2` is the committed
held-out figure and the bound is its equivalent correlation.

*The precision bound is reported beside it*, as the smallest correlation this
design could detect at conventional power given the effective sample size. It
is a statement about the study rather than about the science, which is why it is
not primary, but it is the honest description of the design's resolution.

**What a reader loses under the primary bound.** An effect smaller than the
spatial benchmark's but still physically substantial would pass as "equivalent".
The comparative bound licenses "smaller than the benchmark this paper reports
against", not "small enough not to matter". No bound available here licenses the
second, and the reason is the missing transport model rather than a missing
decision.

**Effective degrees of freedom throughout.** `notes/decisions.md` records the
median effective sample size at roughly 53 of 926 and that 27 of 72 reported
associations lost significance once it was applied, so a nominal interval here
would be the same error over again. The effective size is computed per
predictor-field pair from `src/model/spatial_dof.py` and the Fisher interval
uses it in place of n.

**The interval is an approximation and the approximation is named.** The Fisher
z transform's standard error is 1/sqrt(n-3); the effective size is substituted
for n, which is the natural extension of the modified t-test this repository
already uses and is not an exact result. Under a weighting the substitution is
looser still, because the effective size is computed from the spatial
configuration and the fields' structure rather than from the weights. Both are
stated because an equivalence test reported to four decimals invites being read
as exact.

**One dimension of the brief's request does not apply.** Equivalence is a test
on a *parameter*, and the two cross-validation schemes -- spatial blocks and
leave-one-province-out -- are designs for estimating held-out prediction, not
parameters. There is no scheme dimension to a correlation. The weighting
dimension does apply and all three weightings are reported.

Run with no arguments to report; ``--write`` to write the artefact.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model import spatial_dof as sdof  # noqa: E402

PROCESSED = REPO / "data" / "processed"
GRID = PROCESSED / "analysis_grid_2018.csv"
OUT = PROCESSED / "equivalence_bounds_2018.csv"

#: The committed held-out R squared of the spatial null under the design the
#: drafts report, spatial blocks unweighted. The comparative bound's basis.
SPATIAL_NULL_R2 = 0.3324

#: Two one-sided tests at 5 percent need a 90 percent interval.
Z_90 = 1.6448536269514722

#: For the precision bound: a two-sided test at 5 percent with 80 percent power
#: needs |z| of about this before the correlation is detectable.
Z_POWER = 2.801585

#: Companion tables holding the other two fields, and the target column in each.
FIELDS = {
    "operational": (GRID, "ch4_bias_corrected_ppb"),
    "raw": (GRID, "ch4_raw_ppb"),
    "blended": (PROCESSED / "methane_blended_2018.csv", "ch4_blended_ppb"),
    "deseasonalised": (PROCESSED / "methane_deseasonalised_2018.csv",
                       "ch4_deseasonalised_ppb"),
}

PREDICTORS = ("impervious_fraction", "rice_fraction_single",
              "rice_fraction_combined")


def key(lat: float, lon: float) -> tuple[str, str]:
    return (f"{lat:.4f}", f"{lon:.4f}")


def load() -> dict:
    """The grid, the two companion fields and the representativeness weight."""
    rows = list(csv.DictReader(GRID.open(newline="")))
    lat = np.array([float(r["centre_lat"]) for r in rows])
    lon = np.array([float(r["centre_lon"]) for r in rows])
    out = {"lat": lat, "lon": lon,
           "count": np.array([float(r["sounding_count"]) for r in rows])}

    def numeric(name, source=rows):
        return np.array([float(r[name]) if r[name] != "" else np.nan
                         for r in source])

    for name in PREDICTORS:
        out[name] = numeric(name)

    for field, (path, column) in FIELDS.items():
        if path == GRID:
            out[f"field::{field}"] = numeric(column)
            continue
        joined = {key(float(r["centre_lat"]), float(r["centre_lon"])): r
                  for r in csv.DictReader(path.open(newline=""))}
        values = np.full(lat.size, np.nan)
        for i in range(lat.size):
            record = joined.get(key(lat[i], lon[i]))
            if record is not None and record[column] != "":
                values[i] = float(record[column])
        out[f"field::{field}"] = values

    quality = PROCESSED / "cell_quality_2018.csv"
    weight = np.full(lat.size, np.nan)
    if quality.exists():
        joined = {key(float(r["centre_lat"]), float(r["centre_lon"])): r
                  for r in csv.DictReader(quality.open(newline=""))}
        for i in range(lat.size):
            record = joined.get(key(lat[i], lon[i]))
            if record is not None and record["weight_representativeness"]:
                weight[i] = float(record["weight_representativeness"])
    out["representativeness"] = weight
    return out


def weighted_corr(x, y, w) -> float:
    total = w.sum()
    mx, my = (w * x).sum() / total, (w * y).sum() / total
    cov = (w * (x - mx) * (y - my)).sum() / total
    vx = (w * (x - mx) ** 2).sum() / total
    vy = (w * (y - my) ** 2).sum() / total
    if vx <= 0 or vy <= 0:
        return float("nan")
    return float(cov / np.sqrt(vx * vy))


def weighted_slope(x, y, w) -> float:
    """Slope in ppb per unit predictor fraction, for interpretability."""
    total = w.sum()
    mx, my = (w * x).sum() / total, (w * y).sum() / total
    vx = (w * (x - mx) ** 2).sum() / total
    if vx <= 0:
        return float("nan")
    return float((w * (x - mx) * (y - my)).sum() / total / vx)


def verdict(low: float, high: float, bound: float) -> str:
    """Which of the three outcomes the interval and the bound give."""
    if not np.isfinite(low) or not np.isfinite(high):
        return "not computable"
    if low > -bound and high < bound:
        return "within the bounds: evidence of no meaningful effect"
    if low >= bound or high <= -bound:
        return "outside the bounds: a positive result"
    return "spans a bound: cannot distinguish a meaningful effect from none"


def rows_for(data: dict) -> list[dict]:
    out: list[dict] = []
    comparative = float(np.sqrt(SPATIAL_NULL_R2))
    for field in FIELDS:
        y = data[f"field::{field}"]
        for predictor in PREDICTORS:
            x = data[predictor]
            for weighting, w in (("unweighted", None),
                                 ("by sounding count", data["count"]),
                                 ("by representativeness",
                                  data["representativeness"])):
                mask = np.isfinite(x) & np.isfinite(y)
                if w is not None:
                    mask &= np.isfinite(w) & (w > 0)
                if int(mask.sum()) < 10:
                    continue
                xs, ys = x[mask], y[mask]
                r = (float(np.corrcoef(xs, ys)[0, 1]) if w is None
                     else weighted_corr(xs, ys, w[mask]))
                ones = np.ones(xs.size)
                slope = weighted_slope(xs, ys, ones if w is None else w[mask])

                # The effective size corrects for spatial dependence, which is
                # a property of the locations and the fields' spatial structure
                # rather than of the weighting, so one value serves all three
                # weightings of the same pair. Stated rather than hidden.
                effective = sdof.effective_sample_size(
                    xs, ys, data["lat"][mask], data["lon"][mask])
                effective = min(effective, float(xs.size + 1))

                if effective > 3 and abs(r) < 1:
                    se = 1.0 / np.sqrt(effective - 3.0)
                    z = np.arctanh(r)
                    low, high = np.tanh(z - Z_90 * se), np.tanh(z + Z_90 * se)
                    precision = float(np.tanh(Z_POWER * se))
                else:
                    low = high = precision = float("nan")

                out.append(dict(
                    field=field, predictor=predictor, weighting=weighting,
                    n=int(xs.size), effective_n=f"{effective:.1f}",
                    pearson_r=f"{r:+.4f}",
                    slope_ppb_per_unit=f"{slope:+.2f}",
                    ci90_low=f"{low:+.4f}", ci90_high=f"{high:+.4f}",
                    bound_comparative=f"{comparative:.4f}",
                    verdict_comparative=verdict(low, high, comparative),
                    bound_precision=f"{precision:.4f}",
                    verdict_precision=verdict(low, high, precision),
                ))
    return out


def report(rows: list[dict]) -> None:
    comparative = float(np.sqrt(SPATIAL_NULL_R2))
    print(f"  primary bound, comparative: |r| = {comparative:.4f}, the spatial "
          f"null's held-out R squared of {SPATIAL_NULL_R2} expressed as a "
          f"correlation")
    print(f"  policy bound: UNAVAILABLE -- the record bounds emissions, and "
          f"converting to column needs the transport model this study does "
          f"not run\n")
    width = max(len(r["predictor"]) for r in rows)
    print(f"  {'field':<16}{'predictor':<{width + 2}}{'weighting':<22}"
          f"{'eff n':>7}{'r':>9}{'90% CI':>20}  verdict vs the primary bound")
    for r in rows:
        interval = f"[{r['ci90_low']}, {r['ci90_high']}]"
        print(f"  {r['field']:<16}{r['predictor']:<{width + 2}}"
              f"{r['weighting']:<22}{r['effective_n']:>7}{r['pearson_r']:>9}"
              f"{interval:>20}  {r['verdict_comparative'].split(':')[0]}")

    inside = sum(1 for r in rows if r["verdict_comparative"].startswith("within"))
    outside = sum(1 for r in rows
                  if r["verdict_comparative"].startswith("outside"))
    print(f"\n  against the primary bound: {inside} of {len(rows)} within, "
          f"{outside} outside, {len(rows) - inside - outside} spanning")
    inside_p = sum(1 for r in rows if r["verdict_precision"].startswith("within"))
    print(f"  against the precision bound: {inside_p} of {len(rows)} within")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    rows = rows_for(load())
    report(rows)

    if args.write:
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        try:
            shown = Path(args.out).resolve().relative_to(REPO)
        except ValueError:
            shown = Path(args.out)
        print(f"  wrote {shown}")
    else:
        print("\n  re-run with --write to write the artefact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
