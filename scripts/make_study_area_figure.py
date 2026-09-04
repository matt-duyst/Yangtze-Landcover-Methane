#!/usr/bin/env python
"""Render the study area map.

    python scripts/make_study_area_figure.py [--stem NAME]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.figures import export, figures_root  # noqa: E402
from src.figures import geo  # noqa: E402
from src.figures.study_area import study_area_figure  # noqa: E402
from src.methane.grid import GridSpec  # noqa: E402

SPEC = GridSpec(west=114.8, south=27.0, east=122.6, north=35.2, resolution=0.25)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stem", default="study_area")
    args = parser.parse_args()

    extent = geo.lattice_extent(SPEC)
    print(f"  declared box   {SPEC.west} to {SPEC.east} E, "
          f"{SPEC.south} to {SPEC.north} N")
    print(f"  drawn extent   {extent.west} to {extent.east} E, "
          f"{extent.south:.2f} to {extent.north} N")
    print(f"  lattice        {SPEC.n_rows} x {SPEC.n_cols} = {SPEC.n_cells} cells")
    print(f"  aspect         {geo.geographic_aspect(extent.centre_latitude):.6f} "
          f"at {extent.centre_latitude:.3f} N")

    figure = study_area_figure(SPEC)
    result = export(figure, args.stem, directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
