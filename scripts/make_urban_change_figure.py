#!/usr/bin/env python
"""Render the urban change figure.

    python scripts/make_urban_change_figure.py [--stem NAME]

Prints the totals it draws, the growth factor each source implies, and the
drawn-to-true area ratio of the thresholded maps for all six product-years.
That last set is the reason the caption tells a reader to take area from the
numbers panel and not from the maps, so it is measured on every build rather
than recorded once.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.figures import export, figures_root  # noqa: E402
from src.figures import urban_change as uc  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stem", default="urban_change")
    args = parser.parse_args()

    values = uc.series()
    factors = uc.growth_factors()
    print("  four-province totals, km2, as panel (c) draws them")
    print("    " + " " * 32
          + "  ".join(f"{y:>9d}" for y in uc.TOTALS_YEARS) + "   2018/2000")
    for pair in uc.SERIES_PAIRS:
        name = f"{pair[0]}, {pair[1]}"
        row = "  ".join(f"{values[pair][y]:9,.0f}" for y in uc.TOTALS_YEARS)
        print(f"    {name:30s} {row}       x{factors[pair]:.2f}")
    print("    two sources, one of them computed twice; the thesis's figures "
          "are GAIA's")

    print(f"\n  maps inked at a {uc.THRESHOLD:.0%} threshold on a 1/64 degree cell, "
          f"years {uc.MAP_YEARS}")
    print("  drawn area / true area, inside the four provinces:")
    for product in ("GAIA", "GISA"):
        ratios = uc.drawn_area_ratio(product)
        print(f"    {product}  "
              + "  ".join(f"{y} {ratios[y]:.3f}" for y in uc.MAP_YEARS))

    figure = uc.urban_change_figure()
    result = export(figure, args.stem, directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
