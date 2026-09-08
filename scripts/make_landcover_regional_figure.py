#!/usr/bin/env python
"""Render the regional land cover distribution figure.

    python scripts/make_landcover_regional_figure.py [--stem NAME]

Prints the threshold's cost, because that is what the caption rests on when it
tells a reader the drawn area is the true area: the inked total against the
provincial totals, and the double-season colour against its own true area,
which it under-draws and says so.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.figures import export, figures_root, style  # noqa: E402
from src.figures import landcover_regional as lr  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stem", default="landcover_regional")
    args = parser.parse_args()

    rice = lr.provincial_rice()
    print("  provincial rice, km2 (assessed area as the denominator):")
    for province, entry in rice.items():
        print(f"    {province:9s} single {entry['single']:9,.1f}  "
              f"double {entry['double']:8,.1f}  "
              f"assessed/polygon {entry['assessed_over_polygon']:.4f}")

    ratios = lr.drawn_area_ratio()
    print(f"\n  inked at a {lr.THRESHOLD:.0%} threshold on a 1/64 degree cell")
    print(f"    total rice  drawn {ratios['total_drawn_km2']:9,.0f} km2 of "
          f"{ratios['total_true_km2']:9,.0f} = {ratios['total']:.3f}")
    print(f"    double only drawn {ratios['double_drawn_km2']:9,.0f} km2 of "
          f"{ratios['double_true_km2']:9,.0f} = {ratios['double']:.3f}")

    classes, _ = lr.rice_classes()
    panel_px = lr.MAP_CM / 2.54 * style.MIN_DPI
    print(f"\n  drawn cells {classes.shape[1]} across, panel {panel_px:.0f} px, "
          f"{panel_px / classes.shape[1]:.2f} drawn px per cell")

    figure = lr.landcover_regional_figure()
    result = export(figure, args.stem, directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
