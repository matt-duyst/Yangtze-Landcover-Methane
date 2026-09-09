"""Tests for the reproduction status figure.

Offline, reading only committed artefacts. The figure is built and asserted on
in memory; nothing is written.

Four things carry this figure.

**Every cell is a claim about what the reproduction found, and each is tied to
the `ERRATA.md` section that establishes it.** This is the correspondence check
the pipeline figure makes against repository paths, made here against a
document: a cited section that stops existing fails, and so does a cell whose
declared evidence is not in the sections it cites. A section number that
resolves says only that a heading exists.

**The grammar is the source's and the departures are declared.** Eleven stages
in the source's order and its spelling, two columns, five states of which four
are the source's. A fifth is used and is asserted to be declared as an
addition rather than absorbed.

**Which kind of reproduction produced which finding.** Desai's hierarchy maps
onto `ERRATA.md`'s own structure -- sections 1 to 6 read the original
materials, section 7 rebuilds from the methodology -- and that mapping is
asserted rather than described, because it was found rather than designed.

**No colour carries meaning.** The figure is asserted to be achromatic -- red,
green and blue equal at every pixel -- and its greyscale and three dichromat
renders to match within one level of 255, which is the rounding of the sRGB
round trip. That is a stronger claim than the palette's usual separation check
and it is available here only because the glyph carries the state, which is
itself a consequence of a measurement: five states cannot be given five tones
0.15 apart.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from src.figures import diagram, style
from src.figures import framework_reproduction as fr
from src.figures.framework_reproduction import framework_reproduction_figure


@pytest.fixture(scope="module")
def figure():
    fig = framework_reproduction_figure()
    yield fig
    plt.close(fig)


def test_the_figure_function_returns_a_figure_and_writes_nothing(tmp_path):
    before = set(tmp_path.iterdir())

    fig = framework_reproduction_figure()
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# every cell is tied to the errata section that establishes it
# --------------------------------------------------------------------------

def test_every_cited_errata_section_exists():
    """A citation that stopped resolving would sit on the page indefinitely."""
    assert fr.missing_citations() == []


def test_every_cell_is_about_what_its_sections_are_about():
    """A section number that resolves says only that a heading exists."""
    assert fr.unsupported_evidence() == []


def test_the_evidence_check_would_catch_a_cell_that_drifted():
    """The positive control. A check that finds nothing must be able to find."""
    sections = fr.errata_sections()
    body = " ".join(sections[number] for number in ("3.5", "3.2"))

    assert "execution_count" in body
    assert "a phrase no errata section contains" not in body


def test_no_row_cites_a_section_it_does_not_use():
    for row in fr.rows():
        if row.errata:
            assert row.evidence, row.stage
        else:
            assert not row.evidence, row.stage


def test_the_findings_the_brief_named_are_all_on_the_figure():
    """Seven findings, each in the cell whose stage it belongs to."""
    cited = {row.stage: set(row.errata) for row in fr.rows()}

    assert "1.1" in cited["Estimate"]        # Figure 4.7 is the raw field
    assert "4.1" in cited["Analysis plan"]   # masked autoencoder described
    assert "3.3" in cited["Exp. design"]     # random then frozen backbone
    assert "3.5" in cited["Code"]            # outputs not attributable
    assert "7.5" in cited["Claim"]           # the growth factor
    assert "7.1" in cited["Claim"]           # the rice attribution
    assert "6.5" in cited["Estimate"]        # no classification accuracy


def test_the_figure_cites_more_than_half_the_errata_sections():
    """It exists to carry in one frame what the errata carries across seven."""
    cited = {number for row in fr.rows() for number in row.errata}
    sections = fr.errata_sections()

    assert len(sections) == 28
    assert len(cited) >= 15
    assert len({number.split(".")[0] for number in cited}) >= 6


# --------------------------------------------------------------------------
# the grammar is the source's, and the departures are declared
# --------------------------------------------------------------------------

def test_the_rows_are_the_sources_eleven_stages_in_its_own_order():
    """Not padded and not trimmed: the row set is the grammar's."""
    assert tuple(row.stage for row in fr.rows()) == diagram.STAGES


def test_there_are_two_columns_because_there_are_two_studies():
    assert len(fr.COLUMNS) == 2
    assert fr.COLUMNS[0][0] == "Original"
    assert fr.COLUMNS[1][0] == "Reproduction"


def test_every_state_drawn_is_a_declared_shape_of_the_one_grammar():
    states = {row.original for row in fr.rows()}
    states |= {row.reproduction for row in fr.rows()}

    assert states <= set(diagram.STATE_GLYPH)
    assert diagram.check_grammar(states) == diagram.PATIL


def test_no_shape_from_the_flowchart_grammar_appears_here():
    """The two grammars are not fused, and this is where that is enforced."""
    states = {row.original for row in fr.rows()}
    states |= {row.reproduction for row in fr.rows()}

    assert not states & set(diagram.PATHS)


def test_the_fifth_state_is_used_and_is_declared_as_an_addition():
    """If the source's four covered it, the departure would not be needed."""
    used = [row.stage for row in fr.rows()
            if "state_unattributable" in (row.original, row.reproduction)]

    assert used == ["Code"]
    extra = diagram.SHAPES["state_unattributable"]
    assert extra.symbol == "not attributable"
    assert "Not one of the source's four states" in extra.why


def test_the_fifth_state_is_not_a_synonym_for_the_two_it_sits_between():
    """`incorrect` asserts a value is wrong; `unobserved` asserts none exists.

    ERRATA 3.5 is neither: something was recorded, and what cannot be
    established is the link to the code beside it. The errata says so in as
    many words, and this asserts the wording rather than trusting the reading.
    """
    body = fr.errata_sections()["3.5"]

    flat = " ".join(body.split())
    assert "These facts cannot all describe a single run." in flat
    assert "should not be cited as results of the code as committed" in flat
    # If the losses were known to be wrong, `incorrect` would be the state.
    # The errata deliberately does not say that: it says they cannot be tied
    # to the committed source, which is a different and weaker claim.
    assert "wrong" not in flat.lower()


def test_the_source_de_emphasises_the_unchanged_case_and_this_figure_does_not(
        figure):
    """A declared departure: here the unchanged cells are the finding."""
    marks = [t for ax in figure.axes for t in ax.texts
             if t.get_text() in diagram.STATE_GLYPH.values()]
    cells = [t for t in marks if t.get_fontsize() == fr.GLYPH_SIZE]
    keys = [t for t in marks if t.get_fontsize() != fr.GLYPH_SIZE]

    assert len(cells) == 2 * len(fr.rows())
    assert len(keys) == len(diagram.STATES)
    # One tone across every cell, and one size: the source fades the cells
    # where both studies agree, and here those are the finding.
    assert len({t.get_color() for t in marks}) == 1
    assert len({t.get_fontsize() for t in cells}) == 1


# --------------------------------------------------------------------------
# what reproduced, and by which route
# --------------------------------------------------------------------------

def test_the_reproduction_found_four_of_eleven_stages_unchanged():
    """A figure showing only failures would misreport the reproduction."""
    intact = [row.stage for row in fr.rows() if row.intact]

    assert intact == ["Population", "Question", "Hypothesis", "Analyst"]
    for row in fr.rows():
        if row.intact:
            assert row.original == row.reproduction == "state_observed"


def test_the_one_stage_that_is_unchanged_and_is_a_limitation_says_so():
    analyst = next(row for row in fr.rows() if row.stage == "Analyst")

    assert "same person" in analyst.finding
    assert "not an independent check" in analyst.finding


def test_the_original_column_is_not_a_list_of_defects():
    """Five of eleven cells in the 2023 column are unchanged or absent."""
    states = [row.original for row in fr.rows()]

    assert states.count("state_observed") == 5
    assert states.count("state_unobserved") == 1
    assert len([s for s in states if s in ("state_incorrect",
                                           "state_unattributable")]) == 5


def test_the_figure_says_the_data_changed_rather_than_that_the_numbers_were_wrong(
        figure):
    """ERRATA 7.5's mechanism, which is what keeps this from being an attack."""
    data = next(row for row in fr.rows() if row.stage == "Data")

    assert data.original == "state_observed"
    assert "reproduces from the same product to within 0.8%" in data.finding
    assert "re-dates" in data.finding
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)
    assert "consistent with the data the thesis had" in flat


def test_reading_the_original_materials_is_dependent_and_rebuilding_is_not():
    """Desai's hierarchy against the errata's own section structure.

    Sections 1 to 6 read the thesis PDF, the committed notebook and the
    repository's history. Section 7 rebuilds the composite, joins the lattice
    and runs the baselines. The mapping was found rather than designed, so it
    is asserted rather than described.
    """
    for row in fr.rows():
        if not row.errata:
            assert row.kind == "", row.stage
            continue
        chapters = {number.split(".")[0] for number in row.errata}
        reads = bool(chapters - {"7"})
        rebuilds = "7" in chapters

        assert row.kind, row.stage
        assert (fr.DEPENDENT in row.kind) is reads, row.stage
        assert (fr.INDEPENDENT in row.kind) is rebuilds, row.stage


def test_the_boundary_case_is_marked_as_both_rather_than_as_dependent():
    """7.5 recomputes from the same product but from a later release."""
    data = next(row for row in fr.rows() if row.stage == "Data")

    assert data.kind == fr.BOTH
    assert "7.5" in data.errata


# --------------------------------------------------------------------------
# no colour carries meaning
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def rendered(figure):
    from scripts.verify_figure import _simulate_image, render

    image = render(figure, dpi=110)
    return image, _simulate_image


def test_the_figure_is_achromatic(rendered):
    """Stronger than the palette's separation check, and available because the
    glyph carries the state and nothing else does."""
    image, _ = rendered
    channels = image.astype("int16")

    assert np.array_equal(channels[..., 0], channels[..., 1])
    assert np.array_equal(channels[..., 1], channels[..., 2])


def test_every_dichromat_simulation_returns_the_same_image(rendered):
    """To within one level of 255: the sRGB round trip rounds, it does not
    change the colour, and an achromatic image has no colour to change."""
    image, simulate = rendered

    for kind in style.CVD_KINDS:
        seen = simulate(image, kind)
        difference = np.abs(seen.astype("int16") - image.astype("int16"))
        assert difference.max() <= 1, kind


def test_no_role_was_added_for_the_states():
    """Five tones 0.15 apart do not exist in this palette; SERIES records it."""
    assert len(style.SERIES) == 4
    assert len(diagram.STATE_GLYPH) == 5
    assert "state_mark" not in style.ROLES


def test_the_figure_draws_only_roles_the_palette_already_had(figure):
    drawn = {t.get_color() for ax in figure.axes for t in ax.texts}
    drawn |= {t.get_color() for t in figure.texts}
    drawn |= {line.get_color() for ax in figure.axes for line in ax.lines}

    assert drawn <= {style.role("label_text"), style.role("boundary_minor")}


# --------------------------------------------------------------------------
# layout and what the figure says
# --------------------------------------------------------------------------

def test_no_row_is_taller_than_its_pitch():
    """An over-full row collides with its neighbour and matplotlib says nothing."""
    tallest = max(fr.row_line_counts().values())

    assert fr.annotation_height_cm(tallest) < fr.ROW_CM


def test_the_legend_fits_across_the_page():
    assert fr.legend_extent() < fr.FIG_WIDTH_CM - fr.RIGHT_CM


def test_the_layout_closes_across_the_page(figure):
    assert figure.get_figwidth() / style.CM == pytest.approx(fr.FIG_WIDTH_CM)
    assert fr.FINDING_CM > fr.COLUMN_CM[1]
    assert fr.COLUMN_CM[0] > fr.STAGE_RIGHT_CM


def test_the_figure_carries_no_title_of_its_own(figure):
    """The set's convention: the caption carries the title, the image does not."""
    assert figure._suptitle is None
    for ax in figure.axes:
        assert ax.get_title() == ""
    bold = [t.get_text() for ax in figure.axes for t in ax.texts
            if t.get_fontweight() == "bold"]
    assert bold == ["Original\n2023", "Reproduction\n2026"]


def test_the_annotation_block_carries_a_functional_label(figure):
    labels = [t.get_text() for ax in figure.axes for t in ax.texts
              if t.get_style() == "italic"]

    assert labels == ["what the reproduction found, and by which route"]


def test_the_figure_names_both_grammars_it_borrows(figure):
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "Patil, Peng and Leek" in flat
    assert "Desai, Abdelhamid and Padalkar" in flat


def test_the_figure_does_not_depict_the_thesis_architecture():
    """The pipeline figure bans these words from its boxes. Here they are the
    subject, so the ban is on structure instead.

    A word like `backbone` in this figure is a finding about the original, not
    a component of anything drawn: `ERRATA.md` 3.3 is what the cell is for. So
    what is asserted is that no *row* is an architecture component -- the stage
    set is the grammar's eleven -- and that wherever such a word appears it is
    inside a finding that cites an errata section.
    """
    banned = ("deeplab", "resnet", "encoder", "epoch", "backbone", "neural")

    assert tuple(row.stage for row in fr.rows()) == diagram.STAGES
    for row in fr.rows():
        assert not any(word in row.stage.lower() for word in banned), row.stage
        if any(word in row.finding.lower() for word in banned):
            assert row.errata, row.stage


def test_the_figure_points_at_the_errata_for_what_it_does_not_draw(figure):
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "Nothing here depicts the thesis's Figure 3.1" in flat
    assert "ERRATA.md 4.1 and 3.3" in flat
