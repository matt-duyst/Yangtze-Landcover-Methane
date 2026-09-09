"""What this repository does, from source to result, as an ISO 5807 flowchart.

The set had eight figures and no diagram. It is a real system with a test suite
behind it and nothing depicted it, so a reader had to reconstruct the route
from five source files and a recipe table.

The 2023 thesis had a diagram, Figure 3.1, of a DeepLabv3+ architecture. This
is deliberately not a redrawing of it. `ERRATA.md` 4.1 records that Section 3.3
describes a masked autoencoder while the implementation is supervised
segmentation, and 3.3 records that the backbone was randomly initialised and
then frozen, so the published diagram depicts an architecture that was neither
described accurately nor implemented as described. The reproduction never built
a network at all: `notes/repository-architecture.md` records that decision and
the baselines that forced it.

Two things a naive pipeline diagram would leave out
---------------------------------------------------

**Which inputs are obtained and which arrive with the clone.** `data/raw/` is
gitignored, so a reader running this fetches most of its inputs rather than
receiving them. That is carried by *shape* -- ISO's `data` symbol for what must
be obtained, `stored_data` for what is committed -- which costs no colour and
survives a black and white print.

**Where the system refuses.** Four gates here do not warn and carry on; they
stop. The manifest will not overwrite a populated digest that disagrees. The
area scripts will not write a row that has moved by more than a tenth of a
percent. The rice extent script will not write when a province's assessed area
falls outside 0.80 to 1.02 of its polygon. The exporter will not write a figure
below 300 dpi or 8 cm, or above the venue's byte limits. A diagram without the
refusals describes a system that carries on, which is a different system.

The graph is data
-----------------

:func:`nodes` and :func:`edges` return dataclasses and the drawing code reads
them, so ISO's structural principles are assertions rather than things a reader
checks by eye, and **every box names the repository paths it stands for** so a
test can open them. A pipeline diagram showing a step the code does not perform
is the diagram equivalent of a stale prose figure, and nothing else in this
suite would catch one.
"""

from __future__ import annotations

from pathlib import Path

from . import diagram, style
from .diagram import Edge, Node

REPO = Path(__file__).resolve().parents[2]

#: Two panels, decided by rendering rather than by planning. Panel (a) is
#: top-down over six columns because acquisition forks; panel (b) is
#: left-right in one row because modelling is a single chain. As one top-down
#: frame the chart is eleven rows and 23.4 cm tall at this width, which is the
#: whole usable height of a Copernicus page; as two it is 17.8. ISO reads both
#: ways, so the principle is satisfied either way and the choice is legibility.
PANEL_A = "a"
PANEL_B = "b"

# Layout in centimetres.
FIG_WIDTH_CM = style.FULL_WIDTH_CM
LEFT_CM = 0.30
RIGHT_CM = 0.30
BOX_W_CM = 2.42
BOX_H_CM = 0.88
COL_CM = 2.58
ROW_CM = 1.95
#: A diamond narrows away from its middle, so two lines of text in one the
#: height of a rectangle overflow at top and bottom. Taller rather than wider,
#: because wider costs a column and the columns are full.
DECISION_HEIGHT = 1.45
TOP_CM = 0.10
MID_CM = 0.70          # between the two panels
NOTE_CM = 0.12
BOTTOM_CM = 1.42
LABEL_CM = 0.46        # panel label above each panel's first row
#: Extra headroom above each panel's first row, in rows. Panel (a) carries two
#: functional labels over row 0 -- the set's convention for telling a reader
#: what they are looking at without writing a caption inside the frame -- and
#: panel (b) carries none.
TOP_PAD = {PANEL_A: 0.86, PANEL_B: 0.42}
#: What the two labels say, and the column each is centred over.
ROW_LABELS = ((1.50, "obtained: data/raw/ is gitignored"),
              (5.35, "committed: arrives with the clone"))


def nodes() -> tuple[Node, ...]:
    """Every box, with the repository paths it stands for."""
    return (
        # -- panel (a), row 0: what a reader must obtain, and what arrives
        # with the clone. Carried by shape, not by colour.
        Node("gaia", "data", "GAIA impervious\n30 m, figshare", 0.00, 0,
             ("src/fetch/figshare.py", "scripts/fetch_gaia.py"), panel=PANEL_A),
        Node("glorice", "data", "GloRice rice\n1/12 deg, figshare", 1.00, 0,
             ("src/fetch/figshare.py", "scripts/fetch_glorice.py"),
             panel=PANEL_A),
        Node("nesdc", "data", "NESDC rice 10 m\nScience Data Bank", 2.00, 0,
             ("src/fetch/scidb.py", "scripts/fetch_rice.py"), panel=PANEL_A),
        Node("s5p", "data", "Sentinel-5P L2\nCH$_4$, MEEO mirror", 3.00, 0,
             ("src/fetch/s5p.py", "scripts/fetch_s5p.py"), panel=PANEL_A),
        Node("gisa", "data", "GISA impervious\n30 m, WHU bundle",
             4.00, 0, ("scripts/fetch_gisa.py",), panel=PANEL_A),
        Node("reference", "stored_data", "data/reference/\nprovinces, land",
             5.35, 0, ("data/reference",), panel=PANEL_A),

        # -- row 1: the first refusal
        Node("manifest", "decision", "digest agrees with\nthe manifest?",
             1.50, 1, ("src/fetch/manifest.py", "data/manifest.json"),
             panel=PANEL_A, span=1.50),
        Node("stop_manifest", "terminator", "stop. nothing\noverwritten",
             3.10, 1, (), panel=PANEL_A, span=0.76),

        # -- row 2: two aggregation branches
        Node("landcover", "predefined_process",
             "src/landcover/\nzonal statistics\nonto the lattice",
             0.75, 2, ("src/landcover/zonal.py", "src/landcover/geometry.py"),
             panel=PANEL_A),
        Node("methane", "predefined_process",
             "src/methane/grid.py\nQA filter, then a\nstreaming mean",
             3.90, 2,
             ("src/methane/grid.py", "scripts/compute_methane_composite.py"),
             panel=PANEL_A),

        # -- row 3: the second and third refusals, and the methane artefact
        Node("area", "decision", "within 0.1% of the\ncommitted row?",
             0.00, 3,
             ("scripts/compute_urban_areas.py", "scripts/compute_rice_areas.py"),
             panel=PANEL_A, span=1.50),
        Node("stop_area", "terminator", "stop.\nnothing written", 1.35, 3, (),
             panel=PANEL_A, span=0.68),
        Node("coverage", "decision", "assessed area within\n0.80 and 1.02?",
             2.50, 3, ("scripts/compute_rice_extent.py",), panel=PANEL_A,
             span=1.50),
        Node("stop_coverage", "terminator", "stop.\nnothing written",
             3.75, 3, (), panel=PANEL_A, span=0.68),
        Node("composite", "stored_data",
             "methane_composite\n_2018.tif, 926 of\n1,023 cells", 4.75, 3,
             ("data/processed/methane_composite_2018.tif",), panel=PANEL_A),

        # -- rows 4 and 5: the join, and what a fresh clone can rebuild
        Node("join", "predefined_process",
             "src/grid/cells.py\njoin land cover onto\nthe methane lattice",
             2.20, 4, ("src/grid/cells.py", "scripts/build_analysis_grid.py"),
             panel=PANEL_A),
        Node("grid", "stored_data",
             "analysis_grid_2018\n.csv, 926 rows", 2.20, 5,
             ("data/processed/analysis_grid_2018.csv",), panel=PANEL_A),
        Node("to_b", "connector", "b", 3.60, 5, (), panel=PANEL_A, span=0.30),

        # -- panel (b): one chain, left to right
        Node("from_a", "connector", "b", 0.00, 0, (), panel=PANEL_B, span=0.30),
        Node("baselines", "predefined_process",
             "src/model/\nbaselines.py, 22\nmodels, 2 schemes",
             1.00, 0, ("src/model/baselines.py", "scripts/run_baselines.py"),
             panel=PANEL_B),
        Node("results", "stored_data",
             "baseline_results\n_2018.csv, 88 rows", 2.05, 0,
             ("data/processed/baseline_results_2018.csv",), panel=PANEL_B),
        Node("figures", "process",
             "src/figures/\none module each,\none role palette",
             3.10, 0, ("src/figures/style.py", "src/figures/output.py"),
             panel=PANEL_B),
        Node("export", "decision", "300 dpi and 8 cm, under\nthe byte limits?",
             4.35, 0, ("src/figures/output.py",), panel=PANEL_B, span=1.50),
        Node("published", "stored_data",
             f"figures/\n{figure_pairs()} PDF and PNG\npairs",
             5.70, 0, ("figures",), panel=PANEL_B),
        Node("stop_export", "terminator", "stop.\nnothing written", 4.35, 1,
             (), panel=PANEL_B, span=0.68),
    )


def edges() -> tuple[Edge, ...]:
    """Every flowline. Out of a decision, both branches carry a label."""
    return (
        *(Edge(source, "manifest", exit="bottom", entry="top")
          for source in ("gaia", "glorice", "nesdc", "s5p", "gisa")),
        Edge("manifest", "stop_manifest", "no", exit="right", entry="left"),
        Edge("manifest", "landcover", "yes", exit="bottom", entry="top"),
        Edge("manifest", "methane", "yes", exit="bottom", entry="top"),
        Edge("landcover", "area", exit="bottom", entry="top"),
        Edge("landcover", "coverage", exit="bottom", entry="top"),
        Edge("methane", "composite", exit="bottom", entry="top"),
        Edge("area", "stop_area", "no", exit="right", entry="left"),
        Edge("area", "join", "yes", exit="bottom", entry="top", shift=0.22),
        Edge("coverage", "stop_coverage", "no", exit="right", entry="left"),
        Edge("coverage", "join", "yes", exit="bottom", entry="top",
             shift=0.22),
        Edge("composite", "join", exit="bottom", entry="top", shift=0.22),
        # Shifted well off the halfway line. The committed reference layers
        # enter at the top and are used at the bottom, so this line crosses
        # four rows; unshifted its sideways leg runs through the middle of the
        # methane box, and at the default gutter it is drawn on top of the two
        # "yes" legs already there.
        Edge("reference", "join", exit="bottom", entry="top", shift=-3.15),
        Edge("join", "grid", exit="bottom", entry="top"),
        Edge("grid", "to_b", exit="right", entry="left"),

        Edge("from_a", "baselines", exit="right", entry="left"),
        Edge("baselines", "results", exit="right", entry="left"),
        Edge("results", "figures", exit="right", entry="left"),
        Edge("figures", "export", exit="right", entry="left"),
        Edge("export", "published", "yes", exit="right", entry="left"),
        Edge("export", "stop_export", "no", exit="bottom", entry="top"),
    )


def missing_paths() -> list[str]:
    """Every declared path that is not in the repository.

    This is the check a diagram needs and a chart drawn by hand cannot have. A
    box naming a module that was renamed, or a step the code stopped
    performing, fails here rather than sitting on the page indefinitely.
    """
    return [f"{node.key}: {path}" for node in nodes() for path in node.exists
            if not (REPO / path).exists()]


def inputs_shown() -> dict:
    """Which nodes have an input drawn into them, for ISO principle 5.

    "Events or decisions that require the availability of information must
    clearly show this." Every process and decision here must be reached by at
    least one flowline, or the figure is asserting a step that runs on nothing.
    """
    incoming: dict = {node.key: 0 for node in nodes()}
    for edge in edges():
        incoming[edge.target] += 1
    return {node.key: incoming[node.key] for node in nodes()
            if node.shape in ("process", "predefined_process", "decision")}


NOTE = (
    "Read (a) top-down and (b) left-right. Symbols are ISO 5807:1985's, from "
    "the set declared in src/figures/diagram.py: a parallelogram is data the "
    "reader must obtain, because data/raw/ is gitignored; a bowed rectangle is "
    "a file the clone already has; a rectangle with side bars is a named "
    "module under src/; a diamond is a decision, and every one of the "
    "{gates} here is a refusal -- the failing branch stops, and nothing is "
    "written or overwritten. Of {recipes} registered recipes, {committed} "
    "rebuild from what a fresh clone holds, {local} need a fetched input and "
    "{network} need a network run. This is not a redrawing of the 2023 "
    "thesis's Figure 3.1: see ERRATA.md 4.1 and 3.3, and "
    "notes/repository-architecture.md for why no network was built."
)

TITLES = {PANEL_A: "from source to lattice",
          PANEL_B: "from lattice to result"}


def figure_pairs() -> int:
    """How many figures the recipe register carries, counted rather than typed.

    Read from `config/recipes.yml` and not from a listing of `figures/`,
    because the register is what the test suite rebuilds and compares: a figure
    on disk that nobody registered is not part of the set, and a number taken
    from the directory would say it was.
    """
    import yaml

    entries = yaml.safe_load((REPO / "config" / "recipes.yml").read_text())
    entries = entries["recipes"] if isinstance(entries, dict) else entries
    return sum(1 for entry in entries
               if entry["artefact"].startswith("figures/")
               and entry["artefact"].endswith(".png"))


def recipe_tiers() -> dict:
    """How many recipes rebuild from what, read from the register."""
    import yaml

    entries = yaml.safe_load((REPO / "config" / "recipes.yml").read_text())
    entries = entries["recipes"] if isinstance(entries, dict) else entries
    counts: dict = {}
    for entry in entries:
        counts[entry["verified"]] = counts.get(entry["verified"], 0) + 1
    counts["total"] = len(entries)
    return counts


def framework_pipeline_figure(width_cm: float = FIG_WIDTH_CM):
    """Build and return the two-panel flowchart. Writes nothing."""
    every = nodes()
    diagram.check_grammar({node.shape for node in every})

    rows = {panel: max(n.row for n in every if n.panel == panel)
            for panel in (PANEL_A, PANEL_B)}
    height_cm = (BOTTOM_CM + LABEL_CM + MID_CM + LABEL_CM + TOP_CM
                 + sum((rows[panel] + 0.42 + TOP_PAD[panel]) * ROW_CM
                       for panel in (PANEL_A, PANEL_B)))

    fig = style.figure(width_cm=width_cm, height_cm=height_cm)
    panel_width = width_cm - LEFT_CM - RIGHT_CM

    axes = {}
    top = height_cm - TOP_CM - LABEL_CM
    for panel in (PANEL_A, PANEL_B):
        panel_height = (rows[panel] + 0.42 + TOP_PAD[panel]) * ROW_CM
        axes[panel] = fig.add_axes(
            (LEFT_CM / width_cm, (top - panel_height) / height_cm,
             panel_width / width_cm, panel_height / height_cm))
        top -= panel_height + MID_CM + LABEL_CM

    # One scale for both panels, from the widest row in either, so a box in
    # (b) is the same size as a box in (a) and the two read as one chart.
    reach = max(node.column for node in every) * COL_CM + BOX_W_CM / 2
    for panel, ax in axes.items():
        ax.set_xlim(-BOX_W_CM / 2 - 0.06, reach + 0.06)
        ax.set_ylim(-(rows[panel] + 0.42) * ROW_CM,
                    TOP_PAD[panel] * ROW_CM)
        ax.set_axis_off()

    placed = {}
    for node in every:
        ax = axes[node.panel]
        x, y = node.column * COL_CM, -node.row * ROW_CM
        width = BOX_W_CM * node.span
        height = BOX_H_CM * (node.span if node.shape == "connector"
                             else DECISION_HEIGHT if node.shape == "decision"
                             else 1.0)
        diagram.draw_node(ax, node, x, y, width, height,
                          fontsize=style.TICK_SIZE - 1.8)
        placed[node.key] = (ax, x, y, width, height)

    labelled: set = set()
    for edge in edges():
        ax, x0, y0, w0, h0 = placed[edge.source]
        _, x1, y1, w1, h1 = placed[edge.target]
        start = diagram.anchor(None, x0, y0, w0, h0, edge.exit)
        end = diagram.anchor(None, x1, y1, w1, h1, edge.entry)
        # A decision's branch may fan out to more than one target, and the
        # label belongs to the branch rather than to each line in it.
        seen = (edge.source, edge.label)
        diagram.draw_edge(ax, start, end, exit_side=edge.exit,
                          entry_side=edge.entry, shift=edge.shift,
                          label="" if seen in labelled else edge.label,
                          key=f"{edge.source}->{edge.target}")
        labelled.add(seen)

    for column, text in ROW_LABELS:
        axes[PANEL_A].text(column * COL_CM, 0.62 * ROW_CM, text,
                           ha="center", va="center",
                           fontsize=style.TICK_SIZE - 1.4, style="italic",
                           color=style.role("label_text"))

    for panel, ax in axes.items():
        box = ax.get_position()
        fig.text(box.x0, box.y1 + 0.06 / height_cm,
                 f"({panel}) {TITLES[panel]}", ha="left", va="bottom",
                 fontsize=style.LABEL_SIZE, fontweight="bold",
                 color=style.role("label_text"))

    _note(fig, width_cm, height_cm)
    return fig


def _note(fig, width_cm, height_cm) -> None:
    tiers = recipe_tiers()
    gates = sum(1 for node in nodes() if node.shape == "decision")
    text = NOTE.format(gates=gates, recipes=tiers["total"],
                       committed=tiers.get("continuously", 0),
                       local=tiers.get("on_local", 0),
                       network=tiers.get("on_demand", 0))
    fig.text(LEFT_CM / width_cm, NOTE_CM / height_cm, _wrap(text, 166),
             ha="left", va="bottom", fontsize=style.TICK_SIZE - 1.5,
             linespacing=1.4, color=style.role("label_text"))


def _wrap(text: str, width: int) -> str:
    import textwrap
    return "\n".join(textwrap.wrap(text, width))
