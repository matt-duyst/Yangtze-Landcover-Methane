#!/usr/bin/env python
"""Render the coverage saturation and monthly yield figure.

    python scripts/make_coverage_figure.py [--checkpoint PATH] [--stem NAME]

Reads the 2018 composite checkpoint, builds the figure, and writes the vector
and raster forms through the verified export path. Prints what it measured from
the files rather than what it asked for.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.figures import export, figures_root  # noqa: E402
from src.figures.coverage import coverage_figure, from_checkpoint  # noqa: E402
from src.figures.style import PALETTE_SOURCE  # noqa: E402

DEFAULT_CHECKPOINT = Path("data/interim/seasonal_2018.npz")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--stem", default="coverage_saturation_2018")
    args = parser.parse_args()

    if not args.checkpoint.exists():
        print(f"no checkpoint at {args.checkpoint}", file=sys.stderr)
        return 1

    record = from_checkpoint(args.checkpoint)
    print(f"  palette source                {PALETTE_SOURCE}")
    print(f"  granules acquired             {record.granules_acquired}")
    print(f"  productive granules           {record.productive_granules}")
    print(f"  saturation curve points       {record.curve_length}")
    print(f"  soundings in box              {record.total_soundings:,}")
    for n in (6, 16, 36):
        print(f"  coverage at {n:>2} productive     {100 * record.fraction_at(n):.2f} %")
    print(f"  coverage at end               {100 * record.final_fraction:.2f} %")
    print("  month  soundings  granules  per granule")
    for m in record.monthly:
        if m.observed:
            print(f"  {m.month:>5}  {m.soundings:>9,}  {m.granules:>8}"
                  f"  {m.per_granule:>11.0f}")
        else:
            print(f"  {m.month:>5}  {'absent':>9}  {'--':>8}  {'--':>11}")

    figure = coverage_figure(record)
    result = export(figure, args.stem, directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
