#!/usr/bin/env python3
"""Bound how much measurement error could be attenuating the land-cover coefficient.

Queue item 11. `notes/grounding-methods.md` records why this matters more than
the other confounds: measurement error in a predictor attenuates its coefficient
toward zero, so it is **the one mechanism that could manufacture this project's
null rather than explain it**. Every other confound either leaves the
association alone or accounts for its genuine absence.

**The question is a bound, not an estimate**, and the direction of the bound is
the step a reviewer will check, so it is derived here explicitly.

Let `T` be the true impervious fraction of a cell, `X = T + e` the GAIA fraction
the regression uses, and `Z` the GISA fraction. For classical error the observed
slope is `beta_obs = lambda * beta_true` with the reliability ratio
`lambda = Var(T) / Var(X)`, and `R2_obs = lambda * R2_true` for a simple
regression, because `corr(X, Y)^2 = lambda * corr(T, Y)^2`.

**To bound `beta_true` from above, `lambda` must be bounded from below, so
`Var(e)` must be bounded from ABOVE.** That is the opposite of what a lower
bound on the error variance provides, and an earlier version of this
repository's record had the chain pointing the wrong way; `notes/decisions.md`
records the correction.

The upper bound comes from the second product. With `D = X - Z` and errors
`e_X`, `e_Z` that are independent of each other:

    Var(D) = Var(e_X) + Var(e_Z)  >=  Var(e_X)

so `Var(e_X) <= Var(D)`, hence

    lambda >= 1 - Var(D) / Var(X)      and      beta_true <= beta_obs / lambda_min

**Independence of the two products' errors is the load-bearing assumption and it
is not testable here.** GAIA and GISA are built from the same Landsat archive by
similar algorithms, so their errors are plausibly positively correlated, in
which case `Var(D)` understates `Var(e_X) + Var(e_Z)` and the bound is optimistic.
The script therefore reports a **sensitivity sweep** over `Var(e) = k * Var(D)`
for `k` from 0.5 to 8, and the multiple `k` at which the bound would reach the
spatial null. Regression calibration is what `notes/grounding-methods.md`
records for this purpose — unbiased for linear regression at a median bias of
1.4 percent against simulation-extrapolation's -12.8 percent — and its own
recommendation is that "in the absence of validation data, the use of regression
calibration is recommended for **sensitivity analysis** for measurement error".

`k = 0.5` is the conventional two-replicate point estimate, which assumes the
two error variances are equal as well as independent. `k = 1` is the
independence bound above.

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

PROCESSED = REPO / "data" / "processed"
OUT = PROCESSED / "attenuation_bound_2018.csv"

BANDS = {2000: 1, 2010: 2, 2018: 3, 2019: 4}
CELL = 0.25
LAT0, LON0 = 27.075, 114.925

#: The multiples of Var(D) to sweep. 0.5 is the equal-and-independent two-replicate
#: estimate; 1 is the independence bound; the rest are the sensitivity analysis.
SWEEP = (0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0)

#: The model whose coefficient is bounded, and the reference it is compared to.
MODEL = "OLS impervious_fraction"
NULL = "spatial null (queen neighbour mean)"


def gisa_cell_fraction(grid: list[dict]) -> np.ndarray:
    """The committed GISA per-cell impervious fraction, in analysis-grid order.

    **Read rather than re-derived.** `impervious_gisa_2018.csv` already holds
    this quantity on the same lattice and the same area-weighted basis as the
    committed GAIA `impervious_fraction`. Re-aggregating it from the extent
    raster here would be a second derivation of a committed number, which is
    the failure mode `figures/README.md` records for figure modules: two
    derivations can drift apart and nothing would catch it. The two were
    compared once when this script was written -- Pearson r 0.999999 with a
    maximum absolute difference of 0.00091 -- and the committed one is used.
    """
    table = {}
    for row in csv.DictReader((PROCESSED / "impervious_gisa_2018.csv").open(newline="")):
        key = (round(float(row["centre_lat"]), 4), round(float(row["centre_lon"]), 4))
        table[key] = float(row["impervious_fraction"])
    out = np.empty(len(grid))
    for i, row in enumerate(grid):
        key = (round(float(row["centre_lat"]), 4), round(float(row["centre_lon"]), 4))
        out[i] = table[key]
    return out


def suite(field: str) -> dict:
    """Held-out R squared per model and combination, from the committed suite."""
    name = {"operational": "baseline_results_2018.csv",
            "blended": "baseline_results_blended_2018.csv"}[field]
    out = {}
    for row in csv.DictReader((PROCESSED / name).open(newline="")):
        out[(row["model"], row["scheme"], row["weighting"])] = row
    return out


def rows_for() -> list[dict]:
    grid = list(csv.DictReader((PROCESSED / "analysis_grid_2018.csv").open(newline="")))
    x = np.array([float(r["impervious_fraction"]) for r in grid])
    z = gisa_cell_fraction(grid)
    d = x - z
    var_x = float(x.var(ddof=1))
    var_d = float(d.var(ddof=1))

    out: list[dict] = []
    out.append(dict(quantity="Var(X), the GAIA cell fraction in use",
                    value=f"{var_x:.6f}", unit="fraction squared",
                    note="the predictor the association regresses on"))
    out.append(dict(quantity="Var(D), GAIA minus GISA on the same cells",
                    value=f"{var_d:.6f}", unit="fraction squared",
                    note="upper bound on Var(e_GAIA) if the two errors are independent"))
    out.append(dict(quantity="correlation of the two cell fractions",
                    value=f"{float(np.corrcoef(x, z)[0, 1]):.4f}", unit="Pearson r",
                    note="high correlation is why the disagreement variance is small"))
    out.append(dict(quantity="Var(D) as a share of Var(X)",
                    value=f"{var_d / var_x:.4f}", unit="share",
                    note="the most error the disagreement can support, under independence"))
    out.append(dict(quantity="reliability ratio lower bound",
                    value=f"{1 - var_d / var_x:.4f}", unit="lambda",
                    note="lambda >= 1 - Var(D)/Var(X); a bound, not an estimate"))
    out.append(dict(quantity="maximum de-attenuation factor",
                    value=f"{1 / (1 - var_d / var_x):.4f}", unit="multiplier",
                    note="1/lambda_min, applied to a coefficient or to an R squared"))
    out.append(dict(quantity="reliability ratio, equal independent errors",
                    value=f"{1 - 0.5 * var_d / var_x:.4f}", unit="lambda",
                    note="the conventional two-replicate point estimate, Var(e)=Var(D)/2"))

    factor = 1.0 / (1 - var_d / var_x)
    for field in ("operational", "blended"):
        s = suite(field)
        for scheme in ("spatial blocks", "leave-one-province-out"):
            for weighting in ("unweighted", "by sounding count"):
                imp = s.get((MODEL, scheme, weighting))
                null = s.get((NULL, scheme, weighting))
                if imp is None or null is None:
                    continue
                r2 = float(imp["held_out_r2"])
                nr2 = float(null["held_out_r2"])
                # De-attenuation raises a positive R squared and cannot rescue a
                # negative held-out R squared, which is not a squared correlation.
                bound = r2 * factor if r2 > 0 else r2
                need = ((1 - r2 / nr2) * var_x / var_d) if (r2 > 0 and nr2 > r2) else float("nan")
                out.append(dict(
                    quantity=f"held-out R2 upper bound, {field}, {scheme}, {weighting}",
                    value=f"{bound:.4f}", unit="R squared",
                    note=f"observed {r2:+.4f}; spatial null {nr2:+.4f}; "
                         + (f"reaching the null needs Var(e) = {need:.1f} x Var(D)"
                            if np.isfinite(need) else
                            "negative held-out R2, so de-attenuation does not apply")))
                if np.isfinite(need):
                    # The same thing as a share and as a multiple, because the
                    # prose quotes both and a note column carries no resolver.
                    out.append(dict(
                        quantity=f"error share needed to reach the null, {field}, "
                                 f"{scheme}, {weighting}",
                        value=f"{1 - r2 / nr2:.4f}", unit="share of Var(X)",
                        note="the fraction of the predictor's variance that would have "
                             "to be error; a requirement, not a measurement"))
                    out.append(dict(
                        quantity=f"multiple of Var(D) needed to reach the null, {field}, "
                                 f"{scheme}, {weighting}",
                        value=f"{need:.2f}", unit="multiplier",
                        note="how many times the observed product disagreement that "
                             "error share would be"))
        coef = s.get((MODEL, "spatial blocks", "unweighted"))
        if coef and "impervious_fraction" in coef.get("detail", ""):
            beta = float(coef["detail"].split("impervious_fraction")[1].split(";")[0])
            out.append(dict(
                quantity=f"coefficient upper bound, {field}, unweighted",
                value=f"{beta * factor:.2f}", unit="ppb per unit fraction",
                note=f"observed {beta:+.2f}; in-sample R2 {coef['in_sample_r2']}"))

    for k in SWEEP:
        var_e = k * var_d
        if var_e >= var_x:
            continue
        out.append(dict(quantity=f"reliability at Var(e) = {k:g} x Var(D)",
                        value=f"{1 - var_e / var_x:.4f}", unit="lambda",
                        note="sensitivity sweep; k=0.5 equal-error estimate, k=1 the bound"))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    table = rows_for()
    width = max(len(r["quantity"]) for r in table)
    for row in table:
        print(f"  {row['quantity']:<{width}}  {row['value']:>10}  {row['unit']}")

    if args.write:
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=["quantity", "value", "unit", "note"])
            writer.writeheader()
            writer.writerows(table)
        try:
            shown = Path(args.out).resolve().relative_to(REPO)
        except ValueError:
            shown = Path(args.out)
        print(f"  wrote {shown}")
    else:
        print("  re-run with --write to write the artefact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
