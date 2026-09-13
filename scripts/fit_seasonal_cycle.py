#!/usr/bin/env python3
"""Expose the fitted seasonal cycle's parameters as an artefact.

Queue item 12a. The column field's fitted seasonal peak at day of year 245.8
has been quoted in `notes/decisions.md`, `notes/grounding-rice.md` and the
discussion draft, and has existed in no committed artefact, so it could carry no
resolver. It is load-bearing: it is what makes EDGAR's uniform June peak roughly
ten weeks early over this domain.

**This exposes an existing computation rather than performing a new one.** The
composite's checkpoint already carries the per-cell harmonic sufficient
statistics under `hs::`, accumulated one sounding at a time during the granule
pass, and `src/methane/seasonal.py` already fits from them and already computes
amplitude, phase, peak day, trough day, peak-to-trough range and variance
explained. Nothing here re-reads a granule.

**The cycle is fitted on one field, and that is a property of the checkpoint
rather than a choice made here.** `scripts/compute_methane_composite.py`
accumulates the harmonic statistics from `mg.PRIMARY`, the operationally
bias-corrected retrieval, so there is exactly one set of accumulators —
`hs::sum_y`, `hs::sum_yx` and `hs::sum_yy` carry a single `y`. The raw field is
in the checkpoint only as a cell sum, with no harmonic terms, and the blended
field is not in the checkpoint at all. **So a cycle for the raw or blended
fields would need another pass over the 28.9 GB granule archive, and the
deseasonalised field has no independent cycle because it is defined as the
primary field with this one removed.** One cycle, not four.

**The peak's uncertainty is computed rather than asserted**, because a claim
that a prior's peak is ten weeks early wants to know whether the peak is
determined to a week or a month. The fit is a linear model on within-cell
centred cross products, so the coefficient covariance is `sigma^2 * A^-1` with
`A` the cross-product matrix from `seasonal._within` and `sigma^2` the residual
mean square. The peak day is a non-linear function of the coefficients — with
two harmonics the maximum of the sum is not the maximum of either term — so it
is propagated by simulation from that covariance rather than by a delta-method
approximation, and reported as a percentile interval.

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

from src.methane import seasonal as se  # noqa: E402

CHECKPOINT = REPO / "data" / "interim" / "extent_2018.npz"
OUT = REPO / "data" / "processed" / "seasonal_cycle_2018.csv"

#: The field the accumulators were built from, for the record.
FIELD = "methane_mixing_ratio_bias_corrected"

#: Draws for the peak-day interval. Fixed so the artefact is reproducible.
DRAWS = 20000
SEED = 20260914


def load_stats(path: Path) -> se.HarmonicStats:
    """Rebuild the harmonic sufficient statistics from the checkpoint."""
    data = np.load(path, allow_pickle=False)
    harmonics = int(data["harmonics"])
    shape = tuple(data["hs::n"].shape)
    stats = se.HarmonicStats(shape, se.HarmonicBasis(harmonics))
    stats.n[...] = data["hs::n"]
    stats.sum_d[...] = data["hs::sum_d"]
    stats.sum_dd[...] = data["hs::sum_dd"]
    stats.sum_y[...] = data["hs::sum_y"]
    stats.sum_yy[...] = data["hs::sum_yy"]
    stats.sum_x[...] = data["hs::sum_x"]
    stats.sum_yx[...] = data["hs::sum_yx"]
    stats.sum_xx[...] = data["hs::sum_xx"]
    return stats


def peak_interval(fit: se.SeasonalFit, stats: se.HarmonicStats):
    """A percentile interval on the peak day, by simulation from the fit.

    Returns ``(low, high, sd)`` in days. The interval is on the *location of the
    maximum*, which is what the prior-seasonality claim turns on, not on the
    amplitude.
    """
    cross, _, _ = se._within(stats)
    sigma_sq = fit.residual_ss / fit.degrees_of_freedom
    covariance = sigma_sq * np.linalg.inv(cross)
    rng = np.random.default_rng(SEED)
    draws = rng.multivariate_normal(fit.coefficients, covariance, size=DRAWS)
    grid = np.linspace(0.0, fit.basis.period, 2000, endpoint=False)
    design = fit.basis.design(grid)
    peaks = grid[np.argmax(draws @ design.T, axis=1)]
    return float(np.percentile(peaks, 2.5)), float(np.percentile(peaks, 97.5)), \
        float(peaks.std(ddof=1))


def rows_for(fit: se.SeasonalFit, stats: se.HarmonicStats) -> list[dict]:
    low, high, sd = peak_interval(fit, stats)
    out: list[dict] = []

    def add(quantity, value, unit, note):
        out.append(dict(quantity=quantity, value=value, unit=unit, note=note))

    add("field the cycle is fitted on", FIELD, "field name",
        "the only field the checkpoint carries harmonic accumulators for")
    add("harmonics", f"{fit.basis.harmonics}", "count",
        "two beat one; the comparison is in notes/decisions.md")
    add("peak day of year", f"{fit.peak_day:.1f}", "day",
        "the maximum of the summed harmonics, found on a grid")
    add("peak day 2.5th percentile", f"{low:.1f}", "day",
        "simulated from the coefficient covariance; a percentile interval")
    add("peak day 97.5th percentile", f"{high:.1f}", "day",
        "simulated from the coefficient covariance; a percentile interval")
    add("peak day standard deviation", f"{sd:.2f}", "days",
        "spread of the simulated peak location")
    add("trough day of year", f"{fit.trough_day:.1f}", "day", "")
    add("peak to trough range", f"{fit.peak_to_trough:.2f}", "ppb",
        "the full seasonal range, which is twice the amplitude only for one harmonic")
    for k, (amplitude, phase) in enumerate(zip(fit.amplitudes, fit.phases), start=1):
        add(f"harmonic {k} amplitude", f"{amplitude:.3f}", "ppb", "")
        add(f"harmonic {k} phase", f"{phase:.4f}", "radians",
            "as A sin(theta + phi)")
    add("variance explained within cells", f"{fit.variance_explained:.4f}", "share",
        "share of the within-cell variance the cycle accounts for")
    add("residual standard deviation", f"{fit.residual_sd:.3f}", "ppb", "")
    add("soundings in the fit", f"{fit.n_soundings}", "soundings", "")
    add("cells in the fit", f"{fit.n_cells}", "cells", "")
    add("degrees of freedom", f"{fit.degrees_of_freedom}", "count",
        "soundings less cells less terms")
    add("condition number", f"{fit.condition_number:.2f}", "ratio",
        "of the within-cell cross-product matrix")
    add("poorly identified cells", f"{int(fit.poorly_identified.sum())}", "cells",
        "sampled over too little of the year to identify a cycle")
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--checkpoint", default=str(CHECKPOINT))
    parser.add_argument("--out", default=str(OUT))
    args = parser.parse_args(argv)

    path = Path(args.checkpoint)
    if not path.exists():
        print(f"  missing {path}; this needs the granule checkpoint, which is "
              f"gitignored. Build it with compute_methane_composite.py --run")
        return 1

    stats = load_stats(path)
    fit = se.solve(stats)
    table = rows_for(fit, stats)

    width = max(len(r["quantity"]) for r in table)
    for row in table:
        print(f"  {row['quantity']:<{width}}  {row['value']:>12}  {row['unit']}")

    if args.write:
        with Path(args.out).open("w", newline="") as handle:
            writer = csv.DictWriter(handle,
                                    fieldnames=["quantity", "value", "unit", "note"])
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
