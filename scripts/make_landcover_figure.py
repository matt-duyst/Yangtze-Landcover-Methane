#!/usr/bin/env python
"""Render the native-resolution land cover figure.

    python scripts/make_landcover_figure.py [--stem NAME]

Reports the drawn pixels per native pixel for each raster panel, because that
number is the figure's claim: below one it is showing a resampled picture of
30 m or 10 m data and should not say otherwise.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.figures import export, figures_root, style  # noqa: E402
from src.figures import landcover  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stem", default="landcover_native")
    args = parser.parse_args()

    window = landcover.WINDOW
    print(f"  window         {window.west} to {window.east} E, "
          f"{window.south} to {window.north} N, in Anhui")
    panel_px = landcover.PANEL_CM / 2.54 * style.MIN_DPI
    print(f"  panel          {landcover.PANEL_CM:.2f} cm = "
          f"{panel_px:.0f} px at {style.MIN_DPI} dpi")
    for name, path, product in (
            ("GISA 30 m", landcover.IMPERVIOUS_GISA, "gisa"),
            ("GAIA 30 m", landcover.IMPERVIOUS_GAIA, "gaia")):
        mask, _, description = landcover.impervious_mask(path, product)
        print(f"  {name:14s} {mask.shape[1]} x {mask.shape[0]} native px, "
              f"{panel_px / mask.shape[1]:.2f} drawn px per native px, "
              f"{description}, {100 * mask.mean():.2f}% impervious")
    values, _ = landcover.rice_classes()
    single = float((values == 1).mean())
    double = float((values == 2).mean())
    print(f"  NESDC 10 m     {values.shape[1]} x {values.shape[0]} native px, "
          f"{panel_px / values.shape[1]:.2f} drawn px per native px, "
          f"{100 * single:.2f}% single, {100 * double:.2f}% double season")

    figure = landcover.landcover_figure()
    result = export(figure, args.stem, directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
