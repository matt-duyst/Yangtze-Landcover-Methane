"""The shape vocabulary, declared the way the colour roles are declared.

`style.py` says a figure may not name a colour: it must name a **role**, and
`tests/test_figures_palette.py` scans the syntax tree for literals. This module
does the same job for shapes. A diagram may not draw an outline of its own; it
names a shape in :data:`SHAPES` and gets the one path that shape means.

The structure is not imposed on the standard, it is the standard's own first
principle. ISO 5807:1985, *Information processing -- Documentation symbols and
conventions for data, program and system flowcharts, program network charts and
system resources charts*, defines the symbol set; the design principles adapted
from it (Chaudhuri, 2020) open with "agree in advance a minimal set of design
shapes, and only use shapes from the set". A module that holds the set is what
"agree in advance" looks like in a repository.

**The standard itself was not read.** ISO 5807 is paywalled and no clause is
quoted or cited here. What is claimed is the symbol *names*, which are
documented in every secondary account of the standard, and the design
principles, which come from Chaudhuri via a source named in
`notes/references.md`. Where this module says a shape is ISO 5807's `decision`
symbol, that is a claim about the name and the diamond, not about a clause.

Two grammars, and they are not fused
------------------------------------

The set carries shapes from two different visual languages and every shape says
which. `framework_pipeline` is a flowchart and follows ISO 5807.
`framework_reproduction` follows the grammar Patil, Peng and Leek published for
reproducibility and replicability (2019, doi:10.1038/s41562-019-0629-z), whose
reference implementation is the `scifigure` R package: stages as rows, studies
as columns, and a small set of states per cell.

A single figure using both would be a third grammar that follows neither, so
:func:`check_grammar` refuses a figure that mixes them, and a test asserts each
figure draws from one.

Why a diagram is declared as data
---------------------------------

Every node and edge is a dataclass in a list, and the drawing code reads that
list. Three things follow that cannot be had from a hand-placed diagram.

* ISO's one-entry-one-exit rule, and its rule that every decision branch is
  labelled, become assertions over the edge list rather than things a reader
  has to check by eye.
* Reading order -- top-down and left-right -- is a property of the declared
  grid positions and is asserted.
* **Every box can name the repository path it stands for, and a test can open
  it.** A pipeline diagram showing a step the code does not perform is the
  diagram equivalent of a stale prose figure, and nothing else in this suite
  would catch it.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from . import style

#: How finely a curved edge is approximated. A stadium end at 300 dpi on a
#: 1.6 cm box is about 190 pixels of arc, so 48 segments puts each under four
#: pixels and the polygon is a circle on the page. Everything here is a polygon
#: so that :func:`outline_signature` can compare any two shapes the same way.
ARC_SEGMENTS = 48


@dataclass(frozen=True)
class Shape:
    """One member of the agreed set.

    ``grammar`` is the visual language the shape belongs to, and is what stops
    the two figures from quietly becoming one. ``symbol`` is the name the
    grammar gives it. ``against`` names the shapes it appears beside and must
    be told apart from, which is the same declaration the colour roles make and
    is checked the same way -- there, by luminance; here, by outline.
    """

    name: str
    grammar: str
    symbol: str
    why: str
    against: frozenset = field(default_factory=frozenset)
    #: A mark drawn *inside* the outline rather than a different outline. ISO
    #: separates `process` from `predefined process` this way -- one rectangle,
    #: two inner bars -- so an outline comparison cannot tell them apart and
    #: :func:`outline_report` says so instead of scoring them zero and failing.
    decoration: str = ""


ISO = "ISO 5807:1985"
PATIL = "Patil, Peng and Leek (2019)"


def _rectangle(width: float = 1.0, height: float = 1.0):
    w, h = width / 2, height / 2
    return np.array([(-w, -h), (w, -h), (w, h), (-w, h), (-w, -h)])


def _stadium(width: float = 1.0, height: float = 1.0):
    """A rectangle with semicircular ends. ISO's terminator."""
    w, h = width / 2, height / 2
    radius = h
    flat = max(w - radius, 0.0)
    angles = np.linspace(-np.pi / 2, np.pi / 2, ARC_SEGMENTS)
    right = np.stack([flat + radius * np.cos(angles),
                      radius * np.sin(angles)], axis=1)
    left = np.stack([-flat - radius * np.cos(angles),
                     -radius * np.sin(angles)], axis=1)
    return np.concatenate([right, left, right[:1]])


def _parallelogram(width: float = 1.0, height: float = 1.0, slant: float = 0.22):
    w, h = width / 2, height / 2
    d = slant * height
    return np.array([(-w + d, -h), (w + d, -h), (w - d, h), (-w - d, h),
                     (-w + d, -h)])


def _diamond(width: float = 1.0, height: float = 1.0):
    w, h = width / 2, height / 2
    return np.array([(0, -h), (w, 0), (0, h), (-w, 0), (0, -h)])


def _circle(width: float = 1.0, height: float = 1.0):
    """ISO's connector. Drawn on the smaller dimension so it stays a circle."""
    radius = min(width, height) / 2
    t = np.linspace(0, 2 * np.pi, ARC_SEGMENTS * 2 + 1)
    return np.stack([radius * np.cos(t), radius * np.sin(t)], axis=1)


def _stored_data(width: float = 1.0, height: float = 1.0, bow: float = 0.10):
    """A rectangle whose left edge bows inward. ISO's stored data."""
    w, h = width / 2, height / 2
    d = bow * width
    t = np.linspace(np.pi / 2, -np.pi / 2, ARC_SEGMENTS)
    # The right edge bows out and the left edge bows in by the same amount, so
    # a column of these tiles without a gap, which is what the symbol is for.
    right = np.stack([w + d * np.cos(t), h * np.sin(t)], axis=1)
    left = np.stack([-w + d * np.cos(-t), -h * np.sin(-t)], axis=1)
    return np.concatenate([right, left[::-1], right[:1]])


#: Every shape a diagram in this repository may draw. Adding one is the same
#: act as adding a colour role: it is declared here, with what it is for and
#: what it must not be confused with, or it does not exist.
SHAPES: dict[str, Shape] = {
    shape.name: shape for shape in (
        Shape("terminator", ISO, "terminal",
              "Where the flow starts and where it stops. Here the start is a "
              "fresh clone of the repository, which is the only entry point "
              "the pipeline has, and the stop is the committed artefact.",
              ("process", "decision", "connector")),
        Shape("process", ISO, "process",
              "A step performed by code in this repository that is not a "
              "named module of its own -- a script body, an arithmetic step.",
              ("terminator", "predefined_process", "decision", "data",
               "stored_data", "connector")),
        Shape("predefined_process", ISO, "predefined process",
              "A step performed by a named module under `src/`, which is "
              "documented and tested elsewhere and is a black box to the "
              "flow. The distinction from `process` is the one ISO draws and "
              "is the reason the double bars exist.",
              ("process", "decision"), decoration="two inner vertical bars"),
        Shape("decision", ISO, "decision",
              "A test with two labelled outcomes. In this pipeline every one "
              "of them is a refusal: the branch that fails does not warn and "
              "carry on, it stops. This is the only shape ISO allows more "
              "than one exit.",
              ("process", "predefined_process", "terminator", "data",
               "stored_data", "connector")),
        Shape("data", ISO, "data",
              "A dataset the reader must **obtain**. `data/raw/` is "
              "gitignored, so most inputs are fetched rather than received, "
              "and the shape is what carries that: a reader can see which "
              "boxes are a download before reading a word.",
              ("stored_data", "process", "decision")),
        Shape("connector", ISO, "connector",
              "Where a flow leaves one panel and resumes in another. ISO's "
              "own answer to a chart too long for its frame, and the reason "
              "the two panels here are one flowchart rather than two.",
              ("terminator", "process", "decision")),
        Shape("stored_data", ISO, "stored data",
              "A file that is **committed**, so a fresh clone already has it. "
              "Distinguished from `data` by shape rather than by fill, which "
              "costs no colour and survives a black and white print.",
              ("data", "process", "decision")),

        # -- the reproduction grammar. Four states from the source, and one
        # more that the source has no room for; see `STATES`.
        Shape("state_observed", PATIL, "observed",
              "The stage is present, and is what the original study had. "
              "The least informative cell on the page, and drawn like every "
              "other one all the same: a grid showing only failures would "
              "misreport a reproduction that found things reproducing.",
              ("state_different", "state_unobserved", "state_incorrect",
               "state_unattributable")),
        Shape("state_different", PATIL, "different",
              "The stage is present and differs from what the original had. The "
              "ordinary state of a reproduction, and not by itself a finding "
              "against the study.",
              ("state_observed", "state_unobserved", "state_incorrect",
               "state_unattributable")),
        Shape("state_unobserved", PATIL, "unobserved",
              "The stage is not present at all. Distinct from differing: a thing "
              "that is absent cannot be compared, and a grid that drew the two "
              "alike would claim a comparison it never made.",
              ("state_observed", "state_different", "state_incorrect",
               "state_unattributable")),
        Shape("state_incorrect", PATIL, "incorrect",
              "The stage is present but is not accurately represented or "
              "described. The state this whole figure needed: three of the "
              "errata's findings are of exactly this kind and no other grammar "
              "surveyed has a word for it.",
              ("state_observed", "state_different", "state_unobserved",
               "state_unattributable")),
        Shape("state_unattributable", PATIL, "not attributable",
              "Present, but cannot be tied to what is said to have produced "
              "it. Not one of the source's four states; see `STATES` for why "
              "this repository needs a fifth and why it is not `incorrect`.",
              ("state_observed", "state_different", "state_unobserved",
               "state_incorrect")),
    )
}

#: The outline each shape draws, in a unit box centred on the origin. State
#: shapes are glyphs rather than outlines and carry None; see `STATE_GLYPH`.
PATHS = {
    "terminator": _stadium,
    "connector": _circle,
    "process": _rectangle,
    "predefined_process": _rectangle,
    "decision": _diamond,
    "data": _parallelogram,
    "stored_data": _stored_data,
}

#: The mark each state draws. Chosen the way the source's own difference mode
#: chooses: symbols "semantically close to the scenarios that they are
#: encoding", where that mode uses a cross for unobserved, a not-equals for
#: different and an exclamation mark for incorrect. Those three are kept as
#: they are. A filled dot stands for `observed`, and a question mark for the
#: state added here.
STATE_GLYPH = {
    "state_observed": "●",
    "state_different": "≠",
    "state_unobserved": "✕",
    "state_incorrect": "!",
    "state_unattributable": "?",
}

#: The states in legend order, with the wording the figure prints.
STATES = (
    ("state_observed", "as the original had it"),
    ("state_different", "present and different"),
    ("state_unobserved", "not present"),
    ("state_incorrect", "not accurately represented"),
    ("state_unattributable", "cannot be tied to its stated source"),
)

#: The eleven stages of the source's grammar, in its own order and its own
#: spelling. Taken from `scifigure`'s `sci_figure` default rather than from the
#: paper's figure, because the package is the authors' own implementation and
#: can be read; the paper is paywalled.
STAGES = ("Population", "Question", "Hypothesis", "Exp. design", "Experimenter",
          "Data", "Analysis plan", "Analyst", "Code", "Estimate", "Claim")


def shape(name: str) -> Shape:
    """The declared shape, or an error naming what a figure must do instead."""
    try:
        return SHAPES[name]
    except KeyError:
        raise KeyError(
            f"{name!r} is not a declared shape. Add it to SHAPES in "
            f"src/figures/diagram.py with its grammar and what it is drawn "
            f"against, the way a colour is added to style.ROLES."
        ) from None


def outline(name: str, width: float = 1.0, height: float = 1.0):
    """The shape's outline as an (n, 2) array in the given box."""
    builder = PATHS.get(name)
    if builder is None:
        raise KeyError(f"{name!r} draws a glyph, not an outline")
    return builder(width, height)


def _densify(points, per_edge: int = 24):
    """Points along an outline rather than only at its corners."""
    out = []
    for a, b in zip(points[:-1], points[1:]):
        t = np.linspace(0.0, 1.0, per_edge, endpoint=False)[:, None]
        out.append(a + (b - a) * t)
    return np.concatenate(out)


#: The box a flowchart node is drawn in, as a width-to-height ratio. Shapes are
#: compared at this aspect and not at 1:1, because at 1:1 a stadium *is* a
#: circle and the terminator and the connector would be declared confusable
#: when on the page they are nothing alike. The number is the pipeline figure's
#: own box, so the comparison is of what is drawn.
DRAWN_ASPECT = 2.9


def outline_signature(name: str, samples: int = 64,
                      aspect: float = DRAWN_ASPECT) -> np.ndarray:
    """A shape's outline as a radius profile, for telling two shapes apart.

    Resampled by angle from the centroid, so the comparison does not depend on
    how many vertices each builder happens to emit, and normalised by the
    profile's own mean, so it measures *form* rather than size -- a connector
    drawn small must still be a different shape from a terminator drawn large,
    and would be indistinguishable to a check that compared raw radii.

    Two shapes declared against each other must differ in this. It is the
    outline analogue of the luminance gap the colour roles hold, and it exists
    for the same reason: a declared adjacency that nothing checks is a comment.
    """
    # Densified first. A rectangle is four vertices, and interpolating radius
    # between two corners by angle gives a straight line where the true edge
    # follows a secant -- which collapsed the rectangle's profile to a constant
    # and declared it identical to a circle. The points have to lie on the
    # outline, not merely at its corners.
    points = _densify(outline(name, aspect, 1.0))
    angles = np.arctan2(points[:, 1], points[:, 0])
    radii = np.hypot(points[:, 0], points[:, 1])
    order = np.argsort(angles)
    grid = np.linspace(-np.pi, np.pi, samples, endpoint=False)
    profile = np.interp(grid, angles[order], radii[order], period=2 * np.pi)
    return profile / profile.mean()


#: How far apart two shapes declared against each other must sit, as a
#: root-mean-square difference between their normalised outline profiles.
#:
#: Measured rather than chosen, and the measurement is the caveat. The closest
#: declared pair is `terminator` against `process` at 0.051: at the aspect a
#: flowchart box is actually drawn, a stadium's rounding is confined to its two
#: ends and is a small share of its perimeter, so the number understates a
#: difference that is obvious on the page. The floor sits below that and well
#: above zero, which is what it is for -- catching a shape added as a
#: near-duplicate of one already in the set, not adjudicating close calls.
MIN_OUTLINE_DIFFERENCE = 0.04


def outline_report() -> dict:
    """How far every declared pair of shapes sits apart in outline."""
    pairs = sorted({tuple(sorted((name, other)))
                    for name, entry in SHAPES.items()
                    for other in entry.against
                    if name in PATHS and other in PATHS})
    # A pair separated by a decoration inside a shared outline is excluded and
    # named, rather than scored zero. This is ISO's own construction for
    # `predefined process` and not a shortcut taken here.
    decorated = sorted(pair for pair in pairs
                       if any(SHAPES[name].decoration for name in pair))
    pairs = [pair for pair in pairs if pair not in decorated]
    distances = {}
    for a, b in pairs:
        difference = outline_signature(a) - outline_signature(b)
        distances[(a, b)] = float(np.sqrt(np.mean(difference ** 2)))
    worst = min(distances, key=distances.get) if distances else None
    return {
        "pairs": len(distances),
        "separated_by_decoration": decorated,
        "distances": distances,
        "min_difference": distances[worst] if worst else float("nan"),
        "min_pair": worst,
        "failures": [(a, b, d) for (a, b), d in distances.items()
                     if d < MIN_OUTLINE_DIFFERENCE],
    }


def check_grammar(names) -> str:
    """The one grammar these shapes belong to, or an error saying they differ."""
    grammars = {shape(name).grammar for name in names}
    if len(grammars) > 1:
        raise ValueError(
            f"a figure may not mix visual grammars: {sorted(grammars)}. Each "
            f"grammar has its own reading conventions and a figure following "
            f"both follows neither.")
    return grammars.pop() if grammars else ""


# --------------------------------------------------------------------------
# a flowchart, declared as data
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Node:
    """One box. ``exists`` names what in the repository it stands for."""

    key: str
    shape: str
    label: str
    column: float
    row: int
    exists: tuple[str, ...] = ()
    panel: str = ""
    span: float = 1.0
    note: str = ""


@dataclass(frozen=True)
class Edge:
    """One flowline. ``label`` is required out of a decision."""

    source: str
    target: str
    label: str = ""
    #: Which side of the source the line leaves from, and which side of the
    #: target it enters. Declared rather than inferred, because ISO's reading
    #: order is a claim about the drawing and inference would make it a
    #: coincidence.
    exit: str = "bottom"
    entry: str = "top"
    #: Shifts the turning leg off the halfway line, in the figure's own units.
    #: Two lines crossing the same gutter would otherwise be drawn on top of
    #: each other and read as one line going somewhere neither goes.
    shift: float = 0.0


def entries_and_exits(edges) -> dict:
    """How many flowlines enter and leave each node."""
    counts: dict = {}
    for edge in edges:
        counts.setdefault(edge.source, {"in": 0, "out": 0})["out"] += 1
        counts.setdefault(edge.target, {"in": 0, "out": 0})["in"] += 1
    return counts


def iso_violations(nodes, edges) -> list[str]:
    """Where the flowchart departs from the principles, as a list.

    The principles, adapted from Chaudhuri (2020) and stated in accordance with
    ISO 5807:1985 where possible:

    1. only shapes from the agreed set;
    2. reads top-down and left-right;
    3. one entry and one exit per shape, the decision symbol excepted;
    4. every decision branch labelled;
    5. an event needing information shows it;
    6. an event needing a resource shows it.

    The first four are structural and are returned here. The last two are
    claims about content: this module cannot know whether a step needs an
    input, so the figure's own test asserts them against the repository.
    """
    out = []
    by_key = {node.key: node for node in nodes}

    # "One entry point and one exit point" is a claim about the shape, not
    # about the number of lines: a flowline may leave a box once and fork at a
    # junction beyond it, and lines routinely merge before entering one. So
    # what is checked is the *point* -- every line into a node arrives on the
    # same side, and every line out of a non-decision leaves from the same
    # side. A decision is the exception the principle names, and its two
    # branches must leave from different sides so the fork is visible.
    sides: dict = {}
    for edge in edges:
        sides.setdefault(edge.source, {"out": set(), "in": set()})
        sides.setdefault(edge.target, {"out": set(), "in": set()})
        sides[edge.source]["out"].add(edge.exit)
        sides[edge.target]["in"].add(edge.entry)

    for node in nodes:
        if node.shape not in SHAPES:
            out.append(f"{node.key}: {node.shape!r} is not a declared shape")
        seen = sides.get(node.key, {"out": set(), "in": set()})
        if len(seen["in"]) > 1:
            out.append(f"{node.key}: entered on {sorted(seen['in'])}, which is "
                       f"more than one entry point")
        if node.shape == "decision":
            # A *branch*, not an edge. A branch may fan out past the box the
            # same way a process's single exit may, so what has to be two is
            # the set of labelled outcomes, and each outcome has to leave from
            # its own side so the fork is visible rather than inferred.
            branches = [e for e in edges if e.source == node.key]
            labels = {e.label for e in branches}
            if len(labels) != 2:
                out.append(f"{node.key}: a decision with {len(labels)} "
                           f"labelled outcomes: {sorted(labels)}")
            else:
                sides_by_label = {}
                for branch in branches:
                    sides_by_label.setdefault(branch.label, set()).add(
                        branch.exit)
                if any(len(used) > 1 for used in sides_by_label.values()):
                    out.append(f"{node.key}: an outcome leaves from more than "
                               f"one side")
                elif len({next(iter(used)) for used
                          in sides_by_label.values()}) != 2:
                    out.append(f"{node.key}: both outcomes share one side, so "
                               f"the fork is not visible")
        elif len(seen["out"]) > 1:
            out.append(f"{node.key}: leaves from {sorted(seen['out'])}, which "
                       f"is more than one exit point")

    for edge in edges:
        source = by_key.get(edge.source)
        if source is None or edge.target not in by_key:
            out.append(f"{edge.source} -> {edge.target}: unknown node")
            continue
        if source.shape == "decision" and not edge.label:
            out.append(f"{edge.source} -> {edge.target}: unlabelled branch "
                       f"out of a decision")
        target = by_key[edge.target]
        forward = (target.row > source.row
                   or (target.row == source.row
                       and target.column > source.column))
        if not forward and not edge.label:
            out.append(f"{edge.source} -> {edge.target}: runs against the "
                       f"reading order without saying so")
    return out


# --------------------------------------------------------------------------
# drawing
# --------------------------------------------------------------------------

def draw_node(ax, node, x, y, width, height, *, fill=None, edge=None,
              fontsize=None, linewidth=0.7):
    """Draw one declared shape at a position in data coordinates."""
    from matplotlib.patches import Polygon

    fill = style.role("diagram_gate" if node.shape == "decision"
                      else "diagram_fill") if fill is None else fill
    edge = style.role("boundary") if edge is None else edge
    points = outline(node.shape, width, height) + np.array([x, y])
    patch = Polygon(points, closed=True, facecolor=fill, edgecolor=edge,
                    linewidth=linewidth, zorder=3, label=node.key)
    ax.add_patch(patch)

    if node.shape == "predefined_process":
        inset = width * 0.09
        for sign in (-1, 1):
            ax.plot([x + sign * (width / 2 - inset)] * 2,
                    [y - height / 2, y + height / 2],
                    color=edge, linewidth=linewidth, zorder=4,
                    solid_capstyle="butt", label=f"{node.key}-bar")

    ax.text(x, y, node.label, ha="center", va="center", zorder=5,
            fontsize=style.TICK_SIZE - 1.2 if fontsize is None else fontsize,
            color=style.role("label_text"), linespacing=1.25)
    return patch


def anchor(node, x, y, width, height, side):  # noqa: ARG001
    """The point on a shape's box that a flowline attaches to."""
    return {"top": (x, y + height / 2), "bottom": (x, y - height / 2),
            "left": (x - width / 2, y), "right": (x + width / 2, y)}[side]


def route(start, end, exit_side, entry_side, shift: float = 0.0):
    """The polyline a flowline follows between two anchors.

    Right angles, not curves. A flowchart's lines carry no magnitude, so a
    spline would suggest one; and across a dense frame a right angle is easier
    to follow with the eye than a curve that passes near three other boxes.

    The turning point is placed halfway between the two shapes rather than at
    either end, so a line that leaves one row and enters the next makes its
    sideways move in the gutter between them, where nothing else is drawn.
    """
    (x0, y0), (x1, y1) = start, end
    vertical = exit_side in ("top", "bottom")
    arrives_vertical = entry_side in ("top", "bottom")

    if vertical and arrives_vertical:
        if abs(x1 - x0) < 1e-9:
            return [(x0, y0), (x1, y1)]
        mid = (y0 + y1) / 2 + shift
        return [(x0, y0), (x0, mid), (x1, mid), (x1, y1)]
    if not vertical and not arrives_vertical:
        if abs(y1 - y0) < 1e-9:
            return [(x0, y0), (x1, y1)]
        mid = (x0 + x1) / 2 + shift
        return [(x0, y0), (mid, y0), (mid, y1), (x1, y1)]
    if vertical:                      # leaves top or bottom, arrives at a side
        return [(x0, y0), (x0, y1), (x1, y1)]
    return [(x0, y0), (x1, y0), (x1, y1)]   # leaves a side, arrives top/bottom


def _label_point(points, offset: float):
    """A point ``offset`` along the polyline from its start.

    The label goes near the source rather than at the midpoint, because a
    decision's branch label answers the question in the diamond and belongs
    beside it. At a midpoint it lands wherever the route happens to turn, which
    in the first draft was on top of three other boxes.
    """
    import numpy as np

    remaining = offset
    for a, b in zip(points[:-1], points[1:]):
        length = float(np.hypot(b[0] - a[0], b[1] - a[1]))
        if length >= remaining or length == 0:
            t = remaining / length if length else 0.0
            return (a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t)
        remaining -= length
    return points[-1]


def draw_edge(ax, start, end, *, exit_side="bottom", entry_side="top",
              label="", colour=None, linewidth=0.7, label_offset=0.30,
              shift=0.0, key=""):
    """A flowline with one arrowhead, routed by :func:`route`."""
    from matplotlib.patches import FancyArrowPatch

    colour = style.role("boundary") if colour is None else colour
    points = route(start, end, exit_side, entry_side, shift)
    for index, (a, b) in enumerate(zip(points[:-2], points[1:-1])):
        ax.plot([a[0], b[0]], [a[1], b[1]], color=colour, linewidth=linewidth,
                zorder=2, solid_capstyle="round", label=f"{key}-leg{index}")
    ax.add_patch(FancyArrowPatch(
        points[-2], points[-1], arrowstyle="-|>", mutation_scale=5.0,
        linewidth=linewidth, color=colour, zorder=2, shrinkA=0, shrinkB=0,
        label=f"{key}-head"))
    if label:
        x, y = _label_point(points, label_offset)
        ax.text(x, y, label, ha="center", va="center", zorder=6,
                fontsize=style.TICK_SIZE - 2.2,
                color=style.role("label_text"),
                bbox=dict(facecolor=style.role("page"), edgecolor="none",
                          pad=0.5))
    return points
