#!/usr/bin/env python3
"""Draw the albedo collinearity figure and report what it claims.

    python scripts/make_albedo_collinearity_figure.py

Prints every correlation the figure draws, for both methane fields and both
weightings, the check that the bias-corrected values reproduce
`albedo_confounder_2018.csv`, and the mark-size arithmetic behind the claim
that panel (a)'s colour carries order rather than magnitude.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import matplotlib  # noqa: E402
matplotlib.use("Agg")  # noqa: E402

from src.figures import albedo_collinearity as ac  # noqa: E402
from src.figures import style  # noqa: E402
from src.figures.observed_predicted import MARK_AREAS  # noqa: E402
from src.figures.output import export, figures_root  # noqa: E402


def main() -> int:
    cells = ac.load_cells()
    computed = ac.associations(cells)

    print(f"{cells.n} cells; {ac.negative_albedo(cells)} carry a negative "
          f"mean {ac.ALBEDO}, kept, see data/processed/README.md")
    print(f"sounding count {int(cells.weight.min())} to "
          f"{int(cells.weight.max())}\n")

    head = (f"{'field':16s} {'weighting':18s} {'albedo~imperv':>14s} "
            f"{'meth~albedo':>12s} {'meth~imperv':>12s} {'partial':>12s}")
    print(head)
    print("-" * len(head))
    for _, label in ac.FIELDS:
        for weighting, _ in ac.WEIGHTINGS:
            e = computed[(label, weighting)]
            print(f"{label:16s} {weighting:18s} "
                  f"{e['albedo_predictor'].spearman:+14.4f} "
                  f"{e['methane_albedo'].pearson:+12.4f} "
                  f"{e['methane_predictor'].pearson:+12.4f} "
                  f"{e['partial'].pearson:+12.4f}")
    print("  (albedo~impervious is Spearman; the rest are Pearson)")

    print("\npartial correlations with their p values")
    for _, label in ac.FIELDS:
        for weighting, _ in ac.WEIGHTINGS:
            e = computed[(label, weighting)]
            print(f"  {label:16s} {weighting:18s} "
                  f"{e['methane_predictor'].pearson:+.4f} -> "
                  f"{e['partial'].pearson:+.4f}  "
                  f"p {e['partial'].pearson_p:.3e}")

    fitted = ac.slopes()
    print("\nppb per unit SWIR albedo, from albedo_correction_2018.csv")
    for series in ("raw retrieval", "bias corrected"):
        for weighting, _ in ac.WEIGHTINGS:
            entry = fitted[(series, weighting)]
            print(f"  {series:16s} {weighting:18s} "
                  f"{entry['slope']:8.3f} +/- {entry['standard_error']:.3f} "
                  f"(R2 {entry['r2']:.4f})")
    for weighting, _ in ac.WEIGHTINGS:
        print(f"  the correction removes "
              f"{ac.correction_reduction(weighting):.1%} of the slope, "
              f"{weighting}")

    disagreements = ac.reproduces_committed_table(computed)
    print(f"\nreproduction of albedo_confounder_2018.csv: "
          f"{len(disagreements)} disagreements above {ac.TOLERANCE:.0e}")
    for text in disagreements:
        print(f"  {text}")
    if disagreements:
        raise SystemExit("the figure and the committed table disagree")

    # Whether a reader can read a value off the ramp at mark size, which is a
    # different question from whether the ramp is perceptually uniform.
    panel_cm = (ac.WIDTH_CM - ac.LEFT_CM - 2 * ac.PANEL_GAP_CM
                - ac.RIGHT_CM) / 3.0
    print("\nmark size against the colour bar, panel (a)")
    for area in (MARK_AREAS[0], MARK_AREAS[-1]):
        diameter_cm = 2 * np.sqrt(area / np.pi) / 72.0 * 2.54
        print(f"  area {area:5.1f} pt^2 -> {diameter_cm:.3f} cm across, "
              f"{diameter_cm / 2.54 * style.MIN_DPI:5.1f} px at 300 dpi")
    print(f"  the bar is {panel_cm:.2f} cm wide for a "
          f"{ac.WIDTH_CM:.0f} cm figure")

    figure = ac.albedo_collinearity_figure()
    result = export(figure, "albedo_collinearity", directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
