#!/usr/bin/env python
"""Render the 2018 methane composite figure.

    python scripts/make_composite_figure.py [--stem NAME]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np  # noqa: E402

from src.figures import export, figures_root, geo  # noqa: E402
from src.figures.composite import composite_figure, read_composite  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stem", default="methane_composite_2018")
    args = parser.parse_args()

    spec = geo.study_spec()
    corrected, counts, absent = read_composite()
    covered = ~absent
    print(f"  lattice           {spec.n_rows} x {spec.n_cols} = {spec.n_cells} cells")
    print(f"  covered           {int(covered.sum())}")
    print(f"  absent            {int(absent.sum())}")
    print(f"  counts            {counts[covered].min()} to {counts[covered].max()}, "
          f"median {np.median(counts[covered]):g}")
    print(f"  XCH4 ppb          {corrected[covered].min():.1f} to "
          f"{corrected[covered].max():.1f}, sd {corrected[covered].std(ddof=1):.2f}")

    figure = composite_figure(spec, corrected, counts, absent)
    result = export(figure, args.stem, directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
