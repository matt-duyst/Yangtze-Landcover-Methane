"""Tests for the albedo collinearity figure.

Offline, reading only committed artefacts. The figure is built and asserted on
in memory; nothing is written.

Four things carry this figure.

**Nothing on it is a literal.** Every correlation is recomputed at build time
from `analysis_grid_2018.csv` and `methane_covariates_2018.csv` through
`src.model.association`, and the figure refuses to build unless the
bias-corrected values reproduce `albedo_confounder_2018.csv`. A number typed
into a figure module goes stale silently and this repository has already had
that failure in prose. The module's own syntax tree is scanned for a pasted
value as a second line of defence.

**The three legs are present and in the right direction.** Impervious fraction
and albedo co-vary; albedo predicts methane; controlling for albedo removes the
impervious association. A reader must be able to follow all three without the
caption, so each has its own panel and each panel prints its own statistic.

**The asymmetry is drawn rather than flattened.** On the raw retrieval the
impervious association survives control and on the bias-corrected field it does
not. Panel (e) draws all four field-by-weighting combinations so neither field
stands for the answer, and the note gives the reading -- the raw field carries
the larger uncorrected bias, so incomplete control is at least as available an
explanation as a real urban signal.

**It does not claim the urban signal is an artefact.** What the data supports is
that the two cannot be separated. The tests assert the caveats are on the
figure, not only in the caption, because `ERRATA.md` 7.4 is careful and the
figure has to match its care rather than exceed it.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from src.figures import albedo_collinearity as ac
from src.figures import fields, style
from src.figures.albedo_collinearity import albedo_collinearity_figure
from src.figures.observed_predicted import MARK_AREAS

MODULE = Path(ac.__file__)


@pytest.fixture(scope="module")
def cells():
    return ac.load_cells()


@pytest.fixture(scope="module")
def computed(cells):
    return ac.associations(cells)


@pytest.fixture(scope="module")
def figure():
    fig = albedo_collinearity_figure()
    yield fig
    plt.close(fig)


def test_the_figure_function_returns_a_figure_and_writes_nothing(tmp_path):
    before = set(tmp_path.iterdir())

    fig = albedo_collinearity_figure()
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# nothing on the figure is a literal
# --------------------------------------------------------------------------

def test_the_recomputed_values_reproduce_the_committed_table():
    """The gate the figure refuses to build without."""
    assert ac.reproduces_committed_table() == []


def test_the_gate_would_catch_a_disagreement(computed):
    """The positive control. A check that finds nothing must be able to find."""
    from src.model.association import Association

    broken = {key: dict(value) for key, value in computed.items()}
    entry = broken[("bias corrected", "unweighted")]
    original = entry["partial"]
    entry["partial"] = Association(
        name=original.name, n=original.n, pearson=original.pearson + 0.01,
        pearson_p=original.pearson_p, spearman=original.spearman,
        spearman_p=original.spearman_p, controls=original.controls)

    assert ac.reproduces_committed_table(broken) != []


def test_the_figure_refuses_to_build_on_a_disagreement(monkeypatch):
    monkeypatch.setattr(ac, "reproduces_committed_table",
                        lambda *a, **k: ["a planted disagreement"])

    with pytest.raises(ValueError, match="describe different computations"):
        albedo_collinearity_figure()


def _precise_literals() -> set[float]:
    """Numbers written in the module to three or more decimal places.

    Scanned from the source text and not from the parsed value, because the
    parsed value cannot tell 0.7 from 0.700 and a line width of 0.7 is not a
    correlation of 0.700. A pasted correlation is written the way this figure
    prints one, to three places or to the table's four.
    """
    source = MODULE.read_text(encoding="utf-8")
    body = "\n".join(line for line in source.splitlines()
                     if not line.lstrip().startswith("#"))
    return {float(match) for match in re.findall(r"\d+\.\d{3,}", body)}


def test_no_correlation_is_written_into_the_module(computed):
    """The second line of defence.

    A two-decimal literal would slip through -- 0.03 is an annotation's corner
    and also the weighted partial to two places -- so this is not the
    guarantee. The guarantee is structural: `associations` is the only source
    of a correlation in this module and it reads the committed tables.
    """
    literals = _precise_literals()
    planted = []
    for entry in computed.values():
        for association in entry.values():
            for value in (association.pearson, association.spearman):
                for places in (3, 4):
                    if round(abs(value), places) in literals:
                        planted.append(f"{association.name} {value:.4f}")

    assert planted == []


def test_the_literal_scan_can_see_a_three_decimal_number():
    """The positive control for the scan itself."""
    assert _precise_literals()          # the module has some, all layout


def test_no_correlation_is_written_into_a_string_either():
    """A pasted printed value, which the constant scan cannot see."""
    source = MODULE.read_text(encoding="utf-8")
    strings = [node.value for node in ast.walk(ast.parse(source))
               if isinstance(node, ast.Constant)
               and isinstance(node.value, str)]
    # A signed three-decimal number is what this figure prints. Docstrings are
    # prose about the finding and are allowed two places, which is how the
    # module's own summary reads.
    offences = [s for s in strings if re.search(r"[+-]\d\.\d{3}", s)]

    assert offences == []


def test_the_two_slopes_come_from_the_committed_correction_table():
    fitted = ac.slopes()

    assert fitted[("raw retrieval", "unweighted")]["slope"] > 200.0
    assert fitted[("bias corrected", "unweighted")]["slope"] < 200.0
    assert 0.015 < ac.correction_reduction("unweighted") < 0.030
    assert ac.correction_reduction("by sounding count") > 0.25


# --------------------------------------------------------------------------
# the three legs
# --------------------------------------------------------------------------

def test_impervious_fraction_and_albedo_co_vary(computed):
    entry = computed[("bias corrected", "unweighted")]["albedo_predictor"]

    assert entry.spearman == pytest.approx(0.761, abs=0.002)
    assert entry.n == 926


def test_albedo_predicts_methane_on_both_fields(computed):
    corrected = computed[("bias corrected", "unweighted")]["methane_albedo"]
    raw = computed[("raw retrieval", "unweighted")]["methane_albedo"]

    assert corrected.pearson == pytest.approx(0.700, abs=0.002)
    assert raw.pearson == pytest.approx(0.738, abs=0.002)
    assert raw.pearson > corrected.pearson       # the raw carries more of it


def test_controlling_for_albedo_removes_the_impervious_association(computed):
    entry = computed[("bias corrected", "unweighted")]

    assert entry["methane_predictor"].pearson == pytest.approx(0.345, abs=0.002)
    assert entry["partial"].pearson == pytest.approx(0.021, abs=0.002)
    assert entry["partial"].pearson_p > 0.05


def test_each_leg_has_its_own_panel_and_prints_its_own_statistic(figure):
    """A reader must follow all three without the caption."""
    assert len(figure.axes) == 6                 # five panels and a colour bar
    for index in range(4):
        text = " ".join(t.get_text() for t in figure.axes[index].texts)
        assert re.search(r"[+-]\d\.\d{3}", text), index


def test_the_added_variable_panel_draws_what_the_partial_correlates(cells,
                                                                    computed):
    """The cloud and the number must not disagree about what was removed."""
    from src.model.association import residuals

    rx = residuals(cells.predictor, [cells.albedo])
    ry = residuals(cells.methane["bias corrected"], [cells.albedo])
    drawn = float(np.corrcoef(rx, ry)[0, 1])

    assert drawn == pytest.approx(
        computed[("bias corrected", "unweighted")]["partial"].pearson,
        abs=1e-9)


# --------------------------------------------------------------------------
# the asymmetry, drawn rather than flattened
# --------------------------------------------------------------------------

def test_the_partial_survives_on_the_raw_field_and_not_on_the_corrected(
        computed):
    raw = computed[("raw retrieval", "unweighted")]["partial"]
    corrected = computed[("bias corrected", "unweighted")]["partial"]

    assert raw.pearson == pytest.approx(0.151, abs=0.002)
    assert raw.pearson_p < 1e-05
    assert corrected.pearson_p > 0.5


def _pairs(summary):
    """The four before-to-after lines, by the label each declares."""
    wanted = {f"{field}-{weighting}" for _, field in ac.FIELDS
              for weighting, _ in ac.WEIGHTINGS}
    return [line for line in summary.lines if line.get_label() in wanted]


def test_all_four_field_and_weighting_combinations_are_drawn(figure):
    summary = figure.axes[4]
    pairs = _pairs(summary)

    assert len(pairs) == len(ac.FIELDS) * len(ac.WEIGHTINGS)
    labels = " ".join(t.get_text() for t in summary.texts)
    for _, field in ac.FIELDS:
        for weighting, _ in ac.WEIGHTINGS:
            assert f"{field}, {weighting}" in labels


def test_every_pair_runs_from_before_to_after_control(figure, computed):
    summary = figure.axes[4]
    drawn = {tuple(np.round(line.get_xdata(), 4)) for line in _pairs(summary)}
    expected = {(round(entry["partial"].pearson, 4),
                 round(entry["methane_predictor"].pearson, 4))
                for entry in computed.values()}

    assert drawn == expected


def test_the_figure_gives_the_reading_that_keeps_the_raw_survival_open(figure):
    """It must not imply the raw field's survival is the truer result."""
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "larger uncorrected bias" in flat
    assert "incomplete control reads as well as a real signal" in flat


# --------------------------------------------------------------------------
# what it must not claim
# --------------------------------------------------------------------------

def test_the_figure_says_it_does_not_show_an_artefact(figure):
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "does not show that the urban signal is an artefact" in flat
    assert "over-controls by an unknown amount" in flat
    assert "cities really are brighter" in flat


def test_the_figure_says_what_would_separate_them(figure):
    """A reader will ask, and saying so is stronger than leaving it implicit."""
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "retrieval known to be albedo-unbiased" in flat
    assert "urban extent varying at constant albedo" in flat
    assert "limit of the study design rather than of the analysis" in flat


def test_the_figure_points_at_the_errata_that_states_this_carefully(figure):
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "ERRATA.md 7.4" in flat


# --------------------------------------------------------------------------
# weighting, and the cells a reader will think are errors
# --------------------------------------------------------------------------

def test_mark_area_carries_the_sounding_count_on_the_shared_classes(figure):
    """The convention observed_predicted set, reused rather than reinvented."""
    for index in range(4):
        sizes = np.unique(figure.axes[index].collections[0].get_sizes())
        assert sizes.size > 1, index
        assert set(sizes) <= set(MARK_AREAS), index


def test_both_weightings_are_reported_because_they_differ(computed):
    unweighted = computed[("bias corrected", "unweighted")]
    weighted = computed[("bias corrected", "by sounding count")]

    assert weighted["methane_predictor"].pearson < (
        unweighted["methane_predictor"].pearson)
    assert weighted["albedo_predictor"].spearman < (
        unweighted["albedo_predictor"].spearman)


def test_the_negative_albedo_cells_are_kept_and_explained(cells, figure):
    """Dropping them would remove 18 percent of the grid non-randomly."""
    negative = ac.negative_albedo(cells)

    assert negative == 166
    assert cells.n == 926
    assert float(cells.albedo.min()) < 0.0
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)
    assert "not an error and not a fill value" in flat
    assert "data/processed/README.md" in flat


def test_a_zero_line_marks_where_albedo_changes_sign(figure):
    """So a reader meeting a negative value sees it is a region, not a stray."""
    for index in (0, 1):
        marked = [line for line in figure.axes[index].lines
                  if line.get_label() == "albedo-zero"]
        assert len(marked) == 1, index


# --------------------------------------------------------------------------
# the colour ramp, which here carries a third variable
# --------------------------------------------------------------------------

def test_panel_a_draws_methane_through_the_sets_own_sequential_ramp(figure):
    mesh = figure.axes[0].collections[0]

    assert mesh.get_array() is not None
    assert mesh.cmap.name == fields.field_cmap().name
    for index in (1, 2, 3):
        assert figure.axes[index].collections[0].get_array() is None


def test_the_ramp_clears_the_page_at_both_ends():
    """It is drawn on white, unlike the composite's, which is drawn on a map."""
    luminance = fields.ramp_luminances()
    page = style._luminance(style.role("page"))

    assert page - luminance.max() >= style.MIN_LUMINANCE_GAP
    assert page - luminance.min() >= style.MIN_LUMINANCE_GAP


def test_no_tone_could_clear_the_ramp_at_both_ends():
    """A new case for the palette, and it has no pairwise answer.

    The convention wants 0.15 of luminance either side. The ramp is 0.67 wide,
    so a clearing tone would have to sit below zero or above 0.92, and 0.92 is
    the page. The line is therefore drawn under the marks instead, which is the
    relief band's treatment rather than a pairwise one.
    """
    luminance = fields.ramp_luminances()
    span = luminance.max() - luminance.min()

    assert span > 2 * style.MIN_LUMINANCE_GAP
    assert luminance.max() + style.MIN_LUMINANCE_GAP > (
        style._luminance(style.role("page")) - 0.08)


def test_the_zero_line_sits_under_the_marks_in_the_coloured_panel(figure):
    """So the darkest cells occlude it rather than blending with it."""
    panel = figure.axes[0]
    line = next(line for line in panel.lines
                if line.get_label() == "albedo-zero")

    assert line.get_zorder() < panel.collections[0].get_zorder()


def test_the_zero_line_clears_the_marks_in_the_uncoloured_panels(figure):
    """Where the marks are a role rather than a ramp, the convention holds."""
    gap = abs(style._luminance(style.role("observation_mark"))
              - style._luminance(style.role("reference_line")))

    assert gap >= style.MIN_LUMINANCE_GAP
    for index in (1, 3):
        assert [line for line in figure.axes[index].lines
                if line.get_label().endswith("-zero")]


def test_the_smallest_mark_cannot_carry_a_value_only_an_order():
    """Which is why methane is an axis in (b) and only a colour in (a).

    A mark of the smallest sounding class is under six pixels across at the
    export resolution. A reader can rank two such marks; nobody can read a
    concentration off one against a bar.
    """
    smallest = 2 * np.sqrt(MARK_AREAS[0] / np.pi) / 72.0 * 2.54

    assert smallest / 2.54 * style.MIN_DPI < 8.0
    assert figure_has_methane_on_an_axis()


def figure_has_methane_on_an_axis() -> bool:
    fig = albedo_collinearity_figure()
    try:
        return any("XCH" in ax.get_ylabel() for ax in fig.axes[:4])
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------

def test_the_note_fits_the_space_reserved_for_it():
    """An over-full note runs through both axis labels, as the first draft did."""
    budget = ac.NOTE_CM + ac.note_height_cm() + ac.AXIS_LABEL_CM

    assert budget <= ac.BOTTOM_CM


def test_the_layout_closes_across_the_page(figure):
    total = (ac.LEFT_CM + 3 * ac.PANEL_CM + 2 * ac.PANEL_GAP_CM + ac.RIGHT_CM)

    assert total == pytest.approx(ac.FIG_WIDTH_CM, abs=1e-9)
    assert figure.get_figwidth() / style.CM == pytest.approx(ac.FIG_WIDTH_CM)


def test_every_axes_sits_inside_the_figure(figure):
    for index, ax in enumerate(figure.axes):
        box = ax.get_position()
        assert 0.0 <= box.x0 and box.x1 <= 1.0, index
        assert 0.0 <= box.y0 and box.y1 <= 1.0, index


def test_the_figure_carries_no_title_of_its_own(figure):
    assert figure._suptitle is None
    for ax in figure.axes:
        assert ax.get_title() == ""
    bold = [t.get_text() for t in figure.texts if t.get_fontweight() == "bold"]
    assert len(bold) == 5
    assert all(t.startswith(f"({letter}) ")
               for letter, t in zip("abcde", bold))
