#!/usr/bin/env python3
"""Draw the predicted-field-and-residual figure and report what it contains.

    python scripts/make_residual_field_figure.py

Prints the shared scale's ends, each field's span, the residual distribution
and what the residual has left in it, then writes the PNG and PDF.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import matplotlib  # noqa: E402
matplotlib.use("Agg")  # noqa: E402

from src.figures import fields, residual_field as rf  # noqa: E402
from src.figures.output import export, figures_root  # noqa: E402


def main() -> int:
    observed, predicted, residual, absent = rf.load_field()
    low, high = rf.shared_ends(observed, predicted)
    extent = rf.spans(observed, predicted)
    values = residual[~absent]

    print(f"model  {rf.MODEL}, {rf.SCHEME}, {rf.WEIGHTING}, "
          f"held-out R2 {rf.held_out_r2():.4f}")
    print(f"cells  {int((~absent).sum())} observed, {int(absent.sum())} absent, "
          f"{absent.size} on the lattice")
    print(f"\nshared scale for (a) and (b): {low:.1f} to {high:.1f} ppb, "
          f"unclipped")
    print(f"  observed field   {np.nanmin(observed):.2f} to "
          f"{np.nanmax(observed):.2f}   span {extent['observed']:.2f} ppb")
    print(f"  model field      {np.nanmin(predicted):.2f} to "
          f"{np.nanmax(predicted):.2f}   span {extent['model']:.2f} ppb"
          f"   ({extent['model'] / extent['observed']:.0%} of the observed span)")
    print(f"\nresidual: {extent['residual_low']:.2f} to "
          f"{extent['residual_high']:.2f} ppb, "
          f"mean {values.mean():+.3f}, sd {values.std(ddof=1):.2f}")
    print(f"  scale +/-{fields.RESIDUAL_LIMIT:.0f} ppb, symmetric; "
          f"{int(np.sum(np.abs(values) > fields.RESIDUAL_LIMIT))} of "
          f"{values.size} cells run past an end")

    structure = rf.structure_report(observed, residual, absent)
    print(f"\nspatial structure, weights: {structure['weights']}")
    for name in ("observed", "residual"):
        entry = structure[name]
        print(f"  {name:9s} I {entry['i']:+.4f}  E[I] {entry['expected']:+.5f}"
              f"  z {entry['z']:6.1f}  pseudo p "
              f"{rf._p_text(entry['p'], entry['permutations'])}"
              f"  ({entry['permutations']} permutations, "
              f"{entry['isolated']} isolated cell dropped)")
    removed = 1 - structure["residual"]["i"] / structure["observed"]["i"]
    print(f"  the fit removes {removed:.1%} of the observed field's Moran's I")

    figure = rf.residual_field_figure()
    result = export(figure, "residual_field", directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
