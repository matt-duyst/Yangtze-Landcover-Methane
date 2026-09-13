#!/usr/bin/env python
"""Render the capability assessment figure: the DOFS sweep and its two limits.

    python scripts/make_capability_figure.py [--artefact PATH] [--stem NAME]

Reads the committed DOFS table, builds the figure, and writes the vector and
raster forms through the verified export path. Every plotted value comes from
that file; the sensitivity expression is not evaluated here.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.figures import export, figures_root  # noqa: E402
from src.figures.capability import (  # noqa: E402
    ARTEFACT, capability_figure, from_artefact,
)
from src.figures.style import PALETTE_SOURCE  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artefact", type=Path, default=ARTEFACT)
    parser.add_argument("--stem", default="capability")
    args = parser.parse_args()

    sweep = from_artefact(args.artefact)
    print(f"  palette source                {PALETTE_SOURCE}")
    print(f"  covered cells                 {sweep.cells}")
    print(f"  sweep points                  {len(sweep.totals)} "
          f"({min(sweep.totals):g} to {max(sweep.totals):g} Tg/y)")
    print(f"  DOFS range                    {min(sweep.dofs):.3f} to "
          f"{max(sweep.dofs):.3f}")
    for threshold, total in sorted(sweep.crossings.items()):
        print(f"  DOFS {threshold:g} reached at        {total:.3f} Tg/y")
    lo, hi = sweep.band
    print(f"  literature band               {lo:g} to {hi:g} Tg/y")
    for total in (lo, hi):
        vals = [sweep.sensitivity[(n, total)]
                for n in ("median", "90th percentile", "maximum")]
        print(f"  sensitivity at {total:>4g} Tg/y      median {vals[0]:.5f}, "
              f"p90 {vals[1]:.5f}, max {vals[2]:.5f}")
    print(f"  prior-free, median cell       {sweep.prior_free_median_gg:.1f} Gg/y")
    print(f"  prior-free, best-observed     {sweep.prior_free_best_gg:.1f} Gg/y")

    figure = capability_figure(sweep)
    result = export(figure, args.stem, directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
