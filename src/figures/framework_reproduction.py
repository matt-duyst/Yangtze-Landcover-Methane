"""What the reproduction found about each part of the 2023 study.

`ERRATA.md` records twenty-eight findings across seven sections. Read straight
through, it is a list, and a list of defects is the wrong shape for what the
reproduction actually established: most of the study is intact, four parts are
not, and the reasons differ in kind. This puts all of it in one frame.

The grammar is not this repository's
------------------------------------

Stages as rows, studies as columns, one state per cell. That is the visual tool
Patil, Peng and Leek published for reproducibility and replicability (2019,
doi:10.1038/s41562-019-0629-z), taken from the authors' own reference
implementation, the `scifigure` package on CRAN, because the paper is
paywalled. `src/figures/diagram.py` holds the eleven stage names in the
source's order and the states as declared shapes; nothing here invents either.

Four adaptations, each a decision rather than a detail
------------------------------------------------------

**A fifth state.** The source declares four -- `observed`, `different`,
`unobserved`, `incorrect`. `ERRATA.md` 3.5 is none of them: every execution
count in the committed notebook is null while 22 cells retain stored outputs,
and the committed transform sequence would raise on the tensor the dataset
class returns, so the stored losses cannot be tied to the code beside them.
That is not `incorrect`, which asserts a value is wrong; the losses may be
real, from a version not committed. It is not `unobserved`, which asserts
nothing was recorded; something was. It is the absence of a link, and the
errata is careful about exactly this -- "None of these establishes *why*". So
`state_unattributable`, declared as an addition and drawn with a question mark.

**A findings column that is not a study.** The source's columns are studies.
This one has two, and no more, because there is one study and one reproduction.
The text on the right is row annotation, the mirror of the stage names on the
left, and it carries what a two-column grid cannot: which `ERRATA.md` section
establishes each state, and which kind of reproduction produced it.

**The same-as-original state is not de-emphasised.** The source's difference
mode fades cells where both studies agree, because across nine columns that is
noise. Here it is signal: four of the eleven stages come through unchanged and a
figure that drew them faintly would be the page of failures the errata's own
preamble is careful not to write.

**No colour carries meaning.** The source's default palette is a red and a teal,
which `src/figures/style.py` exists partly to refuse. Nor is it replaced: five
states would need five tones separating by 0.15 in luminance, and `style.SERIES`
records the measurement that says Crameri's categorical set has no such
five-colour subset below the line-ink ceiling. The glyph carries the state and
nothing else does, so the figure is **achromatic**: red, green and blue are
equal at every pixel. Greyscale and every dichromat simulation therefore return
the same image to within one level of 255, which is the rounding of the sRGB
round trip and not a change of colour. A test asserts both -- the channel
equality exactly, and the four renders to that tolerance.

Which kind of reproduction, and where
-------------------------------------

Desai, Abdelhamid and Padalkar (2025, doi:10.1002/aaai.70004): "Dependent
reproducibility involves using the original materials and validating the
correctness of the implementation as described in the study. Independent
reproducibility is achieved by reconstructing the experiment based on the
original study's methodology."

That hierarchy maps onto `ERRATA.md`'s own structure, which is worth stating
because neither was built with the other in mind. Sections 1 to 6 read the
thesis PDF, the committed notebook and the repository's history: **dependent**.
Section 7 rebuilds the composite from Level 2 granules, joins the lattice and
runs the baselines: **independent**. The errata says as much in section 7's own
preamble -- the six sections above record what reading found, and this one is
"different in kind".

One case sits on the boundary and is marked as such. 7.5 recomputes the
provincial urban areas from the same product, which is dependent in method, but
from a later release, which is not the original material. That is not a
technicality: it is the finding. GAIA stores the year each pixel first became
impervious, so a reprocessing re-dates pixels, and the 2000 extent moves while
the 2018 extent does not.

What this figure must not be
----------------------------

It is not an attack on the thesis, and the states are chosen so it cannot read
as one. The 2023 numbers were consistent with the data the thesis had, and the
data changed. Where a claim recomputes, that is drawn; where three of four
multipliers in a paragraph recompute and one does not, the annotation says
three of four.

It is also not a redrawing of the 2023 thesis's Figure 3.1. No row, state or
annotation names a network, a backbone or an epoch, and a test asserts that --
the same test the pipeline figure carries, extended to cover this one.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from . import diagram, style

REPO = Path(__file__).resolve().parents[2]
ERRATA = REPO / "ERRATA.md"

#: The two columns, in the source's own layout: studies across the top.
COLUMNS = (("Original", "2023"), ("Reproduction", "2026"))

#: The kinds of validation, from Desai et al. (2025). The empty string is for a
#: stage no validation attempt touched.
DEPENDENT = "dependent"
INDEPENDENT = "independent"
BOTH = "dependent and independent"


@dataclass(frozen=True)
class Row:
    """One stage of the scientific process, in both studies.

    ``errata`` names the sections that establish the two states, and
    ``evidence`` gives exact strings that must appear in them. The first is the
    diagram equivalent of the pipeline figure's path check -- a citation that
    stopped existing fails a test rather than sitting on the page. The second is
    there because a section number that resolves is weak evidence that the cell
    says what the section says.
    """

    stage: str
    original: str
    reproduction: str
    finding: str
    errata: tuple[str, ...] = ()
    evidence: tuple[str, ...] = ()
    kind: str = ""
    intact: bool = False


def rows() -> tuple[Row, ...]:
    """Every stage, in the source's order. Eleven, and none of them padding."""
    return (
        Row("Population", "state_observed", "state_observed",
            "The same four provinces and the same 1,023 cells of lattice.",
            intact=True),
        Row("Question", "state_observed", "state_observed",
            "Unchanged: whether urban and paddy extent explain the methane "
            "field.", intact=True),
        Row("Hypothesis", "state_observed", "state_observed",
            "Unchanged, and tested directly here rather than through a "
            "network.", intact=True),
        Row("Exp. design", "state_incorrect", "state_different",
            "The training target was a colour-ramp JPEG, 81.5% of it white "
            "page; the backbone was randomly initialised and then frozen "
            "while described as pretrained. Rebuilt as baselines under two "
            "spatial cross-validation schemes.",
            errata=("3.1", "3.3", "4.2"),
            evidence=("81.5%", "requires_grad", "scale invariant"),
            kind=DEPENDENT),
        Row("Experimenter", "state_unobserved", "state_unobserved",
            "Neither study collected data. Both read published satellite "
            "products, so this stage belongs to third parties in both "
            "columns."),
        Row("Data", "state_observed", "state_different",
            "The 2018 urban extent reproduces from the same product to "
            "within 0.8%; the 2000 extent comes back 1.98 times high, because "
            "GAIA stores the year a pixel first turned impervious and a "
            "reprocessing re-dates it. Three products published since 2023 "
            "were used as well.",
            errata=("7.5", "7.3", "5.1"),
            evidence=("0.8 percent low", "rice_area_by_province.csv",
                      "reference"),
            kind=BOTH),
        Row("Analysis plan", "state_incorrect", "state_different",
            "Section 3.3 describes a masked autoencoder, citing He et al. "
            "throughout; the implementation is supervised segmentation with "
            "nn.MSELoss and no masking anywhere.",
            errata=("4.1",), evidence=("masked autoencoder", "nn.MSELoss"),
            kind=DEPENDENT),
        Row("Analyst", "state_observed", "state_observed",
            "The same person, which is the limit on what any of this can "
            "claim: a reproduction by its own author is not an independent "
            "check of the analyst.", intact=True),
        Row("Code", "state_unattributable", "state_different",
            "Every execution count in the committed notebook is null while 22 "
            "cells retain stored outputs, and the committed transforms would "
            "raise on the tensor the dataset class returns, so the stored "
            "losses cannot be tied to the code beside them. Rebuilt as tested "
            "modules under src/.",
            errata=("3.5", "3.2"),
            evidence=("execution_count", "ToTensor"),
            kind=DEPENDENT),
        Row("Estimate", "state_incorrect", "state_different",
            "Figure 4.7's three placements resolve to one PDF object with "
            "identical pixel hashes: it is the raw observation, not a "
            "prediction, and its caption states input years the body "
            "contradicts. No classification accuracy is reported anywhere. "
            "Held-out metrics are reported here instead.",
            errata=("1.1", "1.2", "6.5"),
            evidence=("object 180", "in the year 2018", "confusion matrix"),
            kind=DEPENDENT),
        Row("Claim", "state_incorrect", "state_different",
            "One stated multiplier is 3.84 against a stated sixfold and the "
            "2010 total is out by 1; three neighbouring multipliers do "
            "recompute. The rice attribution is not supported, and the "
            "headline growth factor is reproduced by neither product.",
            errata=("2.1", "2.2", "7.1", "7.5"),
            evidence=("3.84", "24,831", "spatial null", "factor of 3.0"),
            kind=BOTH),
    )


# --------------------------------------------------------------------------
# the correspondence check
# --------------------------------------------------------------------------

def errata_sections() -> dict:
    """Every `### N.M` section of `ERRATA.md`, as number to body text.

    Read rather than listed, so a section that is renumbered or removed fails
    the figure's tests instead of leaving a citation on the page that resolves
    to nothing.
    """
    text = ERRATA.read_text(encoding="utf-8")
    parts = re.split(r'^### (\d+\.\d+) ', text, flags=re.M)
    return {parts[i]: parts[i + 1] for i in range(1, len(parts), 2)}


def missing_citations() -> list[str]:
    """Cited sections that `ERRATA.md` does not have."""
    sections = errata_sections()
    return [f"{row.stage}: ERRATA {number}" for row in rows()
            for number in row.errata if number not in sections]


def unsupported_evidence() -> list[str]:
    """Declared evidence that does not appear in any section the row cites.

    A section number that resolves says only that a heading exists. This says
    the cell is about what the section is about.
    """
    sections = errata_sections()
    out = []
    for row in rows():
        body = " ".join(sections.get(number, "") for number in row.errata)
        for phrase in row.evidence:
            if phrase not in body:
                out.append(f"{row.stage}: {phrase!r} not in "
                           f"ERRATA {'/'.join(row.errata)}")
    return out


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------

FIG_WIDTH_CM = style.FULL_WIDTH_CM
LEFT_CM = 0.30
STAGE_RIGHT_CM = 2.55       # stage labels are right-aligned here
COLUMN_CM = (3.30, 5.55)    # the two study columns
FINDING_CM = 6.60           # where the annotation block starts
RIGHT_CM = 0.30
#: Row pitch. Four wrapped lines of annotation stand 1.03 cm, so this leaves
#: a tenth of a centimetre of air between one row's block and the next. Set
#: from the measurement rather than by eye: an over-full row collides with its
#: neighbour and matplotlib draws the overlap without complaint.
ROW_CM = 1.13
HEADER_CM = 0.92            # column headings and the rule under them
GAP_CM = 0.34               # between the rule and the first row
LEGEND_CM = 1.05
NOTE_CM = 0.12
BOTTOM_CM = 2.12            # seven wrapped lines of note
TOP_CM = 0.16

#: Point sizes, in one place because three blocks have to agree about them for
#: the measured wrap below to mean anything.
STAGE_SIZE = style.TICK_SIZE - 0.5
FINDING_SIZE = style.TICK_SIZE - 1.6
HEADER_SIZE = style.LABEL_SIZE - 0.5
LEGEND_SIZE = style.TICK_SIZE - 1.0
NOTE_SIZE = style.TICK_SIZE - 1.5

#: Point size of a state glyph. Larger than the text around it, because it is
#: the mark a reader scans the column for and the words are what they read
#: once they have stopped.
GLYPH_SIZE = 9.5

NOTE = (
    "Rows are the eleven stages of the scientific process and columns are "
    "studies, which is the visual grammar Patil, Peng and Leek published for "
    "reproducibility and replicability (2019); the glyphs are its four states "
    "and one added here. {unattributable} is not one of the source's four: it "
    "marks something recorded that cannot be tied to what is said to have "
    "produced it, which is neither wrong nor absent, and ERRATA.md 3.5 is "
    "exactly that case. No colour carries meaning -- five states cannot be "
    "given five tones that separate by 0.15 in luminance, so the glyph carries "
    "the state and no pixel of this figure carries a hue. Which kind of "
    "reproduction is named per row after Desai, Abdelhamid and Padalkar "
    "(2025): dependent uses the original materials, independent rebuilds from "
    "the methodology. {intact} of the {stages} stages are unchanged in both "
    "columns, though one of those is the analyst, who is the same person, "
    "which is the limit on what any of this can claim. "
    "The 2023 numbers were consistent with the data the thesis had, and for "
    "the urban extents the data changed. Nothing here depicts the thesis's "
    "Figure 3.1: see ERRATA.md 4.1 and 3.3."
)


def row_line_counts(width_cm: float = FIG_WIDTH_CM) -> dict:
    """How many wrapped lines each row's annotation takes.

    A row taller than `ROW_CM` collides with its neighbour, and the collision
    is silent: matplotlib draws the overlap without complaint. Returned so a
    test can assert it rather than a reader noticing it.
    """
    width = width_cm - RIGHT_CM - FINDING_CM
    out = {}
    for row in rows():
        lead = f"ERRATA {', '.join(row.errata)}. " if row.errata else ""
        tail = f" [{row.kind}]" if row.kind else ""
        text = wrap_to_cm(lead + row.finding + tail, width, FINDING_SIZE)
        out[row.stage] = text.count("\n") + 1
    return out


def annotation_height_cm(lines: int) -> float:
    """How tall a wrapped annotation of ``lines`` lines stands."""
    return lines * FINDING_SIZE * 1.35 / 72.0 * 2.54


def framework_reproduction_figure(width_cm: float = FIG_WIDTH_CM):
    """Build and return the reproduction status figure. Writes nothing."""
    every = rows()
    diagram.check_grammar({row.original for row in every}
                          | {row.reproduction for row in every})

    height_cm = (BOTTOM_CM + LEGEND_CM + len(every) * ROW_CM + GAP_CM
                 + HEADER_CM + TOP_CM)
    fig = style.figure(width_cm=width_cm, height_cm=height_cm)
    ax = fig.add_axes((0.0, 0.0, 1.0, 1.0))
    ax.set_xlim(0.0, width_cm)
    ax.set_ylim(0.0, height_cm)
    ax.set_axis_off()

    top = height_cm - TOP_CM - HEADER_CM
    _header(ax, width_cm, top)
    for index, row in enumerate(every):
        _draw_row(ax, row, top - GAP_CM - (index + 0.5) * ROW_CM, width_cm)
    _legend(ax, BOTTOM_CM + LEGEND_CM * 0.5)
    _note(fig, width_cm, height_cm, every)
    return fig


def _header(ax, width_cm, top) -> None:
    """Column headings, the rule under them, and one functional label."""
    for x, (name, year) in zip(COLUMN_CM, COLUMNS):
        ax.text(x, top + 0.30, f"{name}\n{year}", ha="center", va="bottom",
                fontsize=HEADER_SIZE, fontweight="bold",
                linespacing=1.2, color=style.role("label_text"))
    # The set's functional-label convention: what a reader is looking at,
    # without a caption inside the frame.
    ax.text(FINDING_CM, top + 0.30,
            "what the reproduction found, and by which route",
            ha="left", va="bottom", fontsize=style.TICK_SIZE - 1.0,
            style="italic", color=style.role("label_text"))
    ax.plot([LEFT_CM, width_cm - RIGHT_CM], [top + 0.14] * 2,
            color=style.role("boundary_minor"), linewidth=0.6,
            solid_capstyle="butt", label="header-rule")


def _draw_row(ax, row, y, width_cm) -> None:
    ax.text(STAGE_RIGHT_CM, y, row.stage, ha="right", va="center",
            fontsize=STAGE_SIZE, color=style.role("label_text"))
    for x, state in zip(COLUMN_CM, (row.original, row.reproduction)):
        ax.text(x, y, diagram.STATE_GLYPH[state], ha="center", va="center",
                fontsize=GLYPH_SIZE, color=style.role("label_text"),
                label=f"{row.stage}-{state}")

    lead = ""
    if row.errata:
        lead = f"ERRATA {', '.join(row.errata)}. "
    tail = f" [{row.kind}]" if row.kind else ""
    width = width_cm - RIGHT_CM - FINDING_CM
    ax.text(FINDING_CM, y,
            wrap_to_cm(lead + row.finding + tail, width, FINDING_SIZE),
            ha="left", va="center", fontsize=FINDING_SIZE,
            linespacing=1.35, color=style.role("label_text"))


#: Space after a legend glyph, and between one entry and the next.
LEGEND_GLYPH_GAP = 0.40
LEGEND_ENTRY_GAP = 0.50


def legend_extent(start: float = LEFT_CM) -> float:
    """Where the legend's last entry ends, measured rather than estimated."""
    x = start
    for name, wording in diagram.STATES:
        x += (LEGEND_GLYPH_GAP + text_width_cm(wording, LEGEND_SIZE)
              + LEGEND_ENTRY_GAP)
    return x - LEGEND_ENTRY_GAP


def _legend(ax, y) -> None:
    """The five states, in the order `diagram.STATES` declares them."""
    x = LEFT_CM
    for name, wording in diagram.STATES:
        ax.text(x, y, diagram.STATE_GLYPH[name], ha="left", va="center",
                fontsize=GLYPH_SIZE - 1.0, color=style.role("label_text"),
                label=f"key-{name}")
        ax.text(x + LEGEND_GLYPH_GAP, y, wording, ha="left", va="center",
                fontsize=LEGEND_SIZE, color=style.role("label_text"))
        x += (LEGEND_GLYPH_GAP + text_width_cm(wording, LEGEND_SIZE)
              + LEGEND_ENTRY_GAP)


def _note(fig, width_cm, height_cm, every) -> None:
    text = NOTE.format(
        unattributable=diagram.STATE_GLYPH["state_unattributable"],
        intact=sum(1 for row in every if row.intact),
        stages=len(every))
    fig.text(LEFT_CM / width_cm, NOTE_CM / height_cm,
             wrap_to_cm(text, width_cm - LEFT_CM - RIGHT_CM, NOTE_SIZE),
             ha="left", va="bottom", fontsize=NOTE_SIZE,
             linespacing=1.4, color=style.role("label_text"))


def text_width_cm(text: str, size: float) -> float:
    """How wide ``text`` renders, in centimetres, at ``size`` points.

    Measured through the same font matplotlib will draw with, rather than
    estimated from a characters-per-centimetre constant. The first draft used
    such a constant and every long annotation ran off the right edge: the
    figure's own text is proportionally spaced, so a count of characters is not
    a width, and a block of prose at 5.4 point varies by a fifth depending on
    what is in it.
    """
    import matplotlib.pyplot as plt
    from matplotlib.font_manager import FontProperties
    from matplotlib.textpath import TextPath

    prop = FontProperties(family=plt.rcParams["font.family"], size=size)
    extent = TextPath((0, 0), text, size=size, prop=prop).get_extents()
    return float(extent.width) / 72.0 * 2.54


def wrap_to_cm(text: str, width_cm: float, size: float) -> str:
    """Greedy wrap to a measured width. Returns the text with newlines."""
    lines, current = [], ""
    for word in text.split():
        candidate = f"{current} {word}".strip()
        if current and text_width_cm(candidate, size) > width_cm:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return "\n".join(lines)
