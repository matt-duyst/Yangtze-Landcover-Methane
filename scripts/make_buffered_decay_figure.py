#!/usr/bin/env python
"""Render the buffered leave-one-out decay curve figure.

    python scripts/make_buffered_decay_figure.py [--artefact PATH] [--stem NAME]

Reads the committed decay-curve table and the committed baseline table, builds
the figure, and writes the vector and raster forms through the verified export
path. Every plotted value comes from those two files; nothing is recomputed
here.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.figures import export, figures_root  # noqa: E402
from src.figures.buffered_decay import (  # noqa: E402
    ARTEFACT, _province_out_null, decay_figure, from_artefact,
)
from src.figures.style import PALETTE_SOURCE  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artefact", type=Path, default=ARTEFACT)
    parser.add_argument("--stem", default="buffered_decay")
    args = parser.parse_args()

    curves = from_artefact(args.artefact)
    province_out = _province_out_null()
    print(f"  palette source                {PALETTE_SOURCE}")
    print(f"  curves in the artefact        {len(curves)}")
    for (field, model), curve in curves.items():
        print(f"  {field:<13} {model[:34]:<34} "
              f"raw {curve.held_out[0]:+.4f} to {curve.held_out[-1]:+.4f}, "
              f"above {curve.above_constant[0]:+.4f} to "
              f"{curve.above_constant[-1]:+.4f}")
    print(f"  spatial null, province-out    {province_out:+.4f}")

    figure = decay_figure(curves, province_out=province_out)
    result = export(figure, args.stem, directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
