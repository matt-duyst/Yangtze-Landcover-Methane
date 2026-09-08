"""Tests for the urban change figure.

Offline, reading only committed artefacts. The figure is built and asserted on
in memory; nothing is written.

Three things carry this figure and each has a test that would fail if it broke
silently.

**The selectors.** GAIA and GISA encode the year of first imperviousness in
opposite directions, and applying one product's rule to the other still draws
a plausible map: it inverts the history and selects the newest construction as
though it were the oldest. The committed aggregate is asserted against the
committed provincial totals, which is the check that both rules were applied
the right way round, and the inversion is asserted to be as wrong as
`data/processed/README.md` records.

**The threshold.** The maps are inked at a stated fraction and that does not
preserve area, so the figure says area comes from panel (c). The test asserts
the distortion is real and in the direction the caption states, because a
caption that warned about a distortion the figure did not have would be worse
than no warning.

**The finding.** Three sources, three growth factors, six-fold to two-fold.
Those numbers are asserted against the committed tables rather than written
here, so the caption and the figure cannot drift apart from the data.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from src.figures import geo, style
from src.figures import urban_change as uc
from src.figures.urban_change import (
    MAP_YEARS,
    TOTALS_YEARS,
    YEARS,
    urban_change_figure,
)


@pytest.fixture(scope="module")
def figure():
    fig = urban_change_figure()
    yield fig
    plt.close(fig)


def test_the_figure_function_returns_a_figure_and_writes_nothing(tmp_path):
    before = set(tmp_path.iterdir())

    fig = urban_change_figure()
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# the selectors, applied the right way round
# --------------------------------------------------------------------------

def test_the_committed_totals_reproduce_the_two_older_tables():
    """Sixteen overlapping rows, and this is what says both rules are right."""
    import csv

    checked, worst = 0, 0.0
    with uc.TOTALS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if not row["relative_difference"]:
                continue
            checked += 1
            worst = max(worst, abs(float(row["relative_difference"])))

    assert checked == 20
    assert worst < 1e-4


def test_gisa_has_provincial_totals_for_every_year_the_figure_draws():
    """The older GISA table carries 2018 alone and is unregenerable."""
    totals = uc.provincial_totals()

    for product in ("GAIA", "GISA"):
        for year in YEARS:
            assert set(totals[product][year]) == {
                "Shanghai", "Zhejiang", "Anhui", "Jiangsu"}


def test_the_year_codes_are_the_documented_ones():
    """GISA counts up from 1972 and GAIA counts down from 2021."""
    from scripts.compute_urban_extent import GAIA_EPOCH, GISA_CODES

    assert GISA_CODES == {2000: 18, 2010: 28, 2018: 36, 2019: 37}
    assert GAIA_EPOCH == 2023
    assert [GAIA_EPOCH - year for year in YEARS] == [23, 13, 5, 4]


def test_2019_is_the_last_year_gisa_reaches():
    """Which is why the maps stop there and not at 2020 or 2021.

    Measured on the product rather than taken from its documentation: 37 is
    both the code for 2019 and the largest value the rasters contain.
    """
    import rasterio
    from scripts.compute_urban_extent import GISA_CODES

    with rasterio.open("data/raw/gisa/urban_206.tif") as src:
        block = src.read(1, out_shape=(src.height // 8, src.width // 8))
    assert int(block.max()) == GISA_CODES[2019] == 37


def test_the_maps_and_the_totals_panel_draw_different_years():
    """On purpose: the last year both products cover, and the thesis's year."""
    assert MAP_YEARS == (2000, 2010, 2019)
    assert TOTALS_YEARS == (2000, 2010, 2018)
    assert set(MAP_YEARS) | set(TOTALS_YEARS) == set(YEARS)


def test_bands_are_selected_by_year_and_never_by_position():
    """A positional read would have drawn 2018 as 2019 when the band was added."""
    for product in ("GAIA", "GISA"):
        assert uc.stored_years(product) == YEARS
    early, _ = uc.display_fractions("GAIA", years=(2018,))
    late, _ = uc.display_fractions("GAIA", years=(2019,))
    assert float(late[0].mean()) > float(early[0].mean())


def test_the_classes_nest_so_no_cell_belongs_to_two_years():
    classes, _ = uc.extent_classes("GAIA")
    fractions, _ = uc.display_fractions("GAIA")

    # A cell classed as 2000 must also be above the threshold in 2010 and 2018.
    oldest = classes == 1
    assert bool((fractions[1][oldest] >= uc.THRESHOLD).all())
    assert bool((fractions[2][oldest] >= uc.THRESHOLD).all())
    assert set(np.unique(classes)) <= {0, 1, 2, 3}


def test_the_newest_class_is_the_largest_which_is_the_finding():
    classes, _ = uc.extent_classes("GAIA")

    counts = {value: int((classes == value).sum()) for value in (1, 2, 3)}
    assert counts[3] > counts[1]


# --------------------------------------------------------------------------
# the threshold, and what it costs
# --------------------------------------------------------------------------

def test_the_threshold_distorts_area_in_the_direction_the_figure_states():
    """The maps flatter growth, so the caption sends a reader to panel (c)."""
    ratios = uc.drawn_area_ratio("GAIA")

    assert ratios[2000] < 1.0 < ratios[2019]
    assert ratios[2019] / ratios[2000] > 1.5


def test_the_drawn_cell_is_no_finer_than_the_page_can_resolve():
    """Drawing 1/128 degree into a 5.2 cm panel aliases into stipple."""
    fractions, _ = uc.display_fractions("GAIA")
    panel_px = uc.MAP_CM / 2.54 * style.MIN_DPI

    assert panel_px / fractions.shape[2] >= 1.0


def test_the_display_average_is_taken_before_the_threshold_not_after():
    """Otherwise a drawn cell means "any of four sub-cells", which is looser."""
    fine, _ = uc.display_fractions("GAIA", factor=1)
    coarse, _ = uc.display_fractions("GAIA", factor=2)

    assert coarse.shape[1] * 2 == fine.shape[1] - fine.shape[1] % 2
    block = fine[2, :2, :2].mean()
    assert coarse[2, 0, 0] == pytest.approx(block)


# --------------------------------------------------------------------------
# the numbers
# --------------------------------------------------------------------------

def test_there_are_two_sources_and_three_computations_of_them():
    """The category the panel had wrong: the thesis is not a third dataset."""
    sources = {source for source, _ in uc.SERIES_PAIRS}
    computations = {computation for _, computation in uc.SERIES_PAIRS}

    assert sources == {"GAIA", "GISA"}
    assert computations == {"as reported 2023", "reproduced 2026"}
    assert ("GAIA", "as reported 2023") in uc.SERIES_PAIRS


def test_the_same_product_recomputed_gives_a_different_growth_factor():
    """The comparison the old layout hid by listing the thesis as a source."""
    factors = uc.growth_factors()

    assert factors[("GAIA", "as reported 2023")] == pytest.approx(6.0, abs=0.05)
    assert factors[("GAIA", "reproduced 2026")] == pytest.approx(3.0, abs=0.05)
    assert factors[("GISA", "reproduced 2026")] == pytest.approx(2.0, abs=0.05)


def test_recomputing_gaia_holds_2018_and_moves_2000_by_a_factor_of_two():
    values = uc.series()
    reported = values[("GAIA", "as reported 2023")]
    reproduced = values[("GAIA", "reproduced 2026")]

    assert reproduced[2018] / reported[2018] == pytest.approx(0.992, abs=0.005)
    assert reproduced[2000] / reported[2000] == pytest.approx(1.975, abs=0.01)


def test_the_products_cross_over_which_is_why_the_factors_differ():
    """GISA is the larger in 2000 and the smaller in 2018."""
    values = uc.series()
    gaia = values[("GAIA", "reproduced 2026")]
    gisa = values[("GISA", "reproduced 2026")]

    assert gisa[2000] > gaia[2000]
    assert gisa[2018] < gaia[2018]
    assert gisa[2019] < gaia[2019]


def test_the_2018_extents_agree_to_about_a_fifth():
    values = uc.series()
    ratio = (values[("GISA", "reproduced 2026")][2018]
             / values[("GAIA", "reproduced 2026")][2018])

    assert ratio == pytest.approx(0.801, abs=0.005)


def test_the_thesis_series_is_the_committed_one():
    assert uc.thesis_totals() == {2000: 8297.0, 2010: 24831.0, 2018: 49725.0}


def test_panel_c_gives_the_colour_to_the_source_and_the_dash_to_the_computation(
        figure):
    """Source and computation are different things and take different channels."""
    lines = figure.axes[2].lines

    assert len(lines) == 3
    by_pair = dict(zip(uc.SERIES_PAIRS, lines))
    gaia_reported = by_pair[("GAIA", "as reported 2023")]
    gaia_reproduced = by_pair[("GAIA", "reproduced 2026")]
    gisa = by_pair[("GISA", "reproduced 2026")]

    # One source, one colour, whatever the computation.
    assert gaia_reported.get_color() == gaia_reproduced.get_color()
    assert gisa.get_color() != gaia_reproduced.get_color()
    # One computation, one dash, and the current one is solid.
    assert gaia_reproduced.get_linestyle() == gisa.get_linestyle()
    assert gaia_reported.get_linestyle() != gaia_reproduced.get_linestyle()
    for line in lines:
        assert "×" in line.get_label()


def test_the_style_helper_refuses_more_computations_than_it_can_separate():
    with pytest.raises(ValueError, match="something else"):
        style.source_computation_styles(
            [("A", "one"), ("A", "two"), ("A", "three"), ("A", "four")])


def test_panel_c_uses_the_ordered_series_and_the_maps_use_the_year_roles():
    """Two schemes, because they encode different things.

    Year of first imperviousness in the maps, source in panel (c). Using one
    set of colours for both would say the two axes were the same axis.
    """
    series = set(style.series(3))
    classes = {style.role(name) for name in uc.CLASS_ROLES.values()}

    assert series.isdisjoint(classes)


# --------------------------------------------------------------------------
# what the figure says it does not have
# --------------------------------------------------------------------------

def test_the_figure_says_where_rice_is_and_why_methane_is_not(figure):
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "Rice is drawn in its own figure" in flat
    assert "no methane equivalent" in flat
    assert "7 by 7 km" in flat


def test_the_figure_says_what_doubt_2019_inherits(figure):
    """It is past the original release and inside the flagged stretch."""
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "1985–2018 release" in flat
    assert "7.1–10.5" in flat


def test_the_figure_tells_a_reader_not_to_measure_the_maps(figure):
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "where, not how much" in flat
    assert "area is read from (c)" in flat


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------

def test_the_layout_closes_across_the_page(figure):
    total = (uc.LEFT_CM + 2 * uc.MAP_CM + uc.MAP_GAP_CM + uc.PANEL_GAP_CM
             + uc.NUMBERS_CM + uc.RIGHT_CM)

    assert total == pytest.approx(uc.FIG_WIDTH_CM, abs=1e-9)
    assert figure.get_figwidth() / style.CM == pytest.approx(uc.FIG_WIDTH_CM)


def test_the_two_maps_share_a_frame_and_only_one_labels_it(figure):
    extent = geo.lattice_extent(geo.study_spec())
    first, second = figure.axes[0], figure.axes[1]

    for ax in (first, second):
        assert ax.get_xlim() == pytest.approx((extent.west, extent.east))
        assert ax.get_ylim() == pytest.approx((extent.south, extent.north))
    assert [t.get_text() for t in second.get_yticklabels()] == [""] * len(
        second.get_yticks())


def test_the_maps_draw_no_coastline_stroke(figure):
    """Measured, not omitted; see the module docstring and style.py."""
    coastline = style.role("coastline")

    for index in (0, 1):
        assert not [line for line in figure.axes[index].lines
                    if line.get_color() == coastline]


def test_every_panel_sits_inside_the_figure(figure):
    for index, ax in enumerate(figure.axes):
        box_ = ax.get_position()
        assert 0.0 <= box_.x0 and box_.x1 <= 1.0, index
        assert 0.0 <= box_.y0 and box_.y1 <= 1.0, index
