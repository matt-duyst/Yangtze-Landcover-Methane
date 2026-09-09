#!/usr/bin/env python3
"""Draw the pipeline framework figure and report what it asserts.

    python scripts/make_framework_pipeline_figure.py

Prints the shape set the figure draws, the ISO conformance check, the recipe
tiering the note quotes, and every repository path the boxes name -- which is
the check a diagram needs and a chart drawn by hand cannot have.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

import matplotlib  # noqa: E402
matplotlib.use("Agg")  # noqa: E402

from src.figures import diagram, framework_pipeline as fp  # noqa: E402
from src.figures.output import export, figures_root  # noqa: E402


def main() -> int:
    nodes, edges = fp.nodes(), fp.edges()
    used = sorted({node.shape for node in nodes})
    print(f"grammar   {diagram.check_grammar(used)}")
    print(f"nodes     {len(nodes)} over {len(used)} shapes, {len(edges)} "
          f"flowlines")
    for name in used:
        count = sum(1 for node in nodes if node.shape == name)
        print(f"  {name:20s} {count:2d}  ISO symbol: "
              f"{diagram.SHAPES[name].symbol}")

    violations = diagram.iso_violations(nodes, edges)
    print(f"\nISO conformance: {len(violations)} structural violations")
    for text in violations:
        print(f"  {text}")

    print("\ninputs shown, for the principle that an event needing "
          "information must show it")
    for key, count in sorted(fp.inputs_shown().items()):
        mark = "" if count else "   <-- runs on nothing"
        print(f"  {key:16s} {count} incoming{mark}")

    tiers = fp.recipe_tiers()
    print(f"\nrecipe tiers, quoted on the figure: {tiers['total']} registered, "
          f"{tiers.get('continuously', 0)} from a fresh clone, "
          f"{tiers.get('on_local', 0)} local, {tiers.get('on_demand', 0)} "
          f"network")
    print(f"figures registered: {fp.figure_pairs()} PDF and PNG pairs")

    missing = fp.missing_paths()
    declared = sum(len(node.exists) for node in nodes)
    print(f"\npaths named by boxes: {declared} declared, {len(missing)} missing")
    for text in missing:
        print(f"  MISSING {text}")
    if missing:
        raise SystemExit("a box names something the repository does not have")

    figure = fp.framework_pipeline_figure()
    result = export(figure, "framework_pipeline", directory=figures_root())
    print("\n" + result.summary())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
