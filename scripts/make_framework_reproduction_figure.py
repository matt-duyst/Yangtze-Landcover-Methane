#!/usr/bin/env python3
"""Draw the reproduction status figure and report what it claims.

    python scripts/make_framework_reproduction_figure.py

Prints the state assigned to each stage in each column, the ERRATA sections
that establish it, the kind of reproduction that produced it, and the
correspondence check -- every cited section must exist in ERRATA.md, and every
declared piece of evidence must appear in the sections the row cites.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import matplotlib  # noqa: E402
matplotlib.use("Agg")  # noqa: E402

from src.figures import diagram, framework_reproduction as fr  # noqa: E402
from src.figures.output import export, figures_root  # noqa: E402


def main() -> int:
    rows = fr.rows()
    states = {row.original for row in rows} | {row.reproduction for row in rows}
    print(f"grammar   {diagram.check_grammar(states)}")
    print(f"rows      {len(rows)} stages, {len(fr.COLUMNS)} columns, "
          f"{len(states)} of {len(diagram.STATE_GLYPH)} states used\n")

    head = f"{'stage':14s} {'2023':>4s} {'2026':>4s}  {'kind':24s} errata"
    print(head)
    print("-" * len(head))
    for row in rows:
        print(f"{row.stage:14s} "
              f"{diagram.STATE_GLYPH[row.original]:>4s} "
              f"{diagram.STATE_GLYPH[row.reproduction]:>4s}  "
              f"{row.kind or '-':24s} {', '.join(row.errata) or '-'}")

    intact = [row.stage for row in rows if row.intact]
    print(f"\nunchanged in both columns: {len(intact)} of {len(rows)} "
          f"({', '.join(intact)})")

    kinds: dict = {}
    for row in rows:
        if row.kind:
            kinds.setdefault(row.kind, []).append(row.stage)
    print("\nkind of reproduction, after Desai et al. (2025)")
    for kind, stages in sorted(kinds.items()):
        print(f"  {kind:24s} {', '.join(stages)}")

    missing = fr.missing_citations()
    unsupported = fr.unsupported_evidence()
    sections = fr.errata_sections()
    cited = sorted({n for row in rows for n in row.errata})
    print(f"\ncorrespondence: {len(cited)} sections cited of {len(sections)} "
          f"in ERRATA.md; {len(missing)} missing, {len(unsupported)} "
          f"unsupported")
    for text in missing + unsupported:
        print(f"  {text}")
    if missing or unsupported:
        raise SystemExit("a cell cites something ERRATA.md does not establish")

    lines = fr.row_line_counts()
    tallest = max(lines.values())
    print(f"\nlayout: tallest annotation {tallest} lines "
          f"({fr.annotation_height_cm(tallest):.3f} cm) against a "
          f"{fr.ROW_CM:.2f} cm row; legend ends at "
          f"{fr.legend_extent():.2f} cm of "
          f"{fr.FIG_WIDTH_CM - fr.RIGHT_CM:.2f}")

    figure = fr.framework_reproduction_figure()
    result = export(figure, "framework_reproduction", directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
