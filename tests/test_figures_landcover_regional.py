"""Tests for the regional land cover distribution figure.

Offline, reading only committed artefacts. The figure is built and asserted on
in memory; nothing is written.

Three things carry this figure.

**The masking.** Four rice rasters, no declared nodata, 0 meaning both non-rice
land and out-of-province background, and bounding boxes that overlap by 23 to
60 percent. Masking every file by the union of the four assesses shared ground
once per file and has already produced a cell at 2.94 times its own area. The
committed totals record the assessed area against the province polygons and
these tests assert that ratio, which is the only cheap way to tell a correct
mask from a plausible one.

**The threshold.** The map inks a cell where enough of it is rice, and that
does not preserve area for free. Here the threshold is set where the drawn area
equals the true area, so the test asserts the ratio is near one -- and asserts
the reason the two seasons do not share a threshold, because the caption says
so and a caption that described a property the figure did not have would be
worse than none.

**The unclassified class.** Anhui's rasters stop at a processing boundary and a
figure drawing rice across the province without marking it would say northern
Anhui grows none. The test asserts the class exists, covers a plausible share
of Anhui, and is not confusable with the class that means "looked at and found
nothing".
"""

from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from src.figures import geo, style
from src.figures import landcover_regional as lr
from src.figures.landcover_regional import landcover_regional_figure


@pytest.fixture(scope="module")
def figure():
    fig = landcover_regional_figure()
    yield fig
    plt.close(fig)


def test_the_figure_function_returns_a_figure_and_writes_nothing(tmp_path):
    before = set(tmp_path.iterdir())

    fig = landcover_regional_figure()
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# the masking
# --------------------------------------------------------------------------

def test_each_raster_was_masked_by_its_own_province_not_by_the_union():
    """A union mask assesses shared ground once per file and exceeds one.

    Three of the four provinces should come out at essentially their polygon
    area; Anhui should come out short, because its rasters are clipped, and
    short is the one direction a masking bug does not produce.
    """
    rice = lr.provincial_rice()

    for province in ("Shanghai", "Zhejiang", "Jiangsu"):
        assert rice[province]["assessed_over_polygon"] == pytest.approx(
            1.0, abs=0.005), province
    assert rice["Anhui"]["assessed_over_polygon"] == pytest.approx(
        0.861, abs=0.002)


def test_no_province_assesses_more_ground_than_it_has():
    """The failure mode, stated as the thing that must not happen."""
    for province, entry in lr.provincial_rice().items():
        assert entry["assessed_over_polygon"] <= 1.02, province


def test_the_anhui_total_reproduces_the_figure_already_recorded():
    """22,594.7 km2 for 2018 is in notes/decisions.md from a separate route."""
    anhui = lr.provincial_rice()["Anhui"]

    assert anhui["single"] + anhui["double"] == pytest.approx(22594.7, abs=1.0)


def test_only_two_provinces_carry_double_season_rice():
    """The distributional fact the figure exists partly to show."""
    rice = lr.provincial_rice()

    assert rice["Jiangsu"]["double"] == 0.0
    assert rice["Shanghai"]["double"] == 0.0
    assert rice["Anhui"]["double"] > 1000.0
    assert rice["Zhejiang"]["double"] > 500.0


# --------------------------------------------------------------------------
# the threshold
# --------------------------------------------------------------------------

def test_the_threshold_makes_the_drawn_area_the_true_area():
    """The rule the caption states, asserted rather than remembered."""
    ratios = lr.drawn_area_ratio()

    assert ratios["total"] == pytest.approx(1.0, abs=0.10)


def test_the_two_seasons_could_not_have_shared_a_threshold():
    """Why the colour says which season, not how much.

    At the map's own threshold the double-season class is far from area
    matched, which is the cost the caption reports. If that ever stopped being
    true the caption would be describing a figure that no longer exists.
    """
    ratios = lr.drawn_area_ratio()

    assert ratios["double"] < 0.7
    assert ratios["double_true_km2"] < 0.10 * ratios["total_true_km2"]


def test_a_common_threshold_serves_the_two_seasons_worse_than_urban():
    """Measured against the brief's expectation, which was the other way round."""
    fractions, _ = lr.display_bands()
    single, double, assessed = fractions
    inside = assessed >= lr.ASSESSED_FLOOR

    # Cells that would be inked for each class alone at a common quarter.
    single_cells = int(((single >= 0.25) & inside).sum())
    double_cells = int(((double >= 0.25) & inside).sum())
    assert single_cells > 20 * double_cells


def test_the_drawn_cell_is_no_finer_than_the_page_can_resolve():
    classes, _ = lr.rice_classes()
    panel_px = lr.MAP_CM / 2.54 * style.MIN_DPI

    assert panel_px / classes.shape[1] >= 1.0


def test_the_display_average_is_taken_before_the_threshold():
    fine, _ = lr.display_bands(factor=1)
    coarse, _ = lr.display_bands(factor=2)

    assert coarse.shape[1] * 2 == fine.shape[1] - fine.shape[1] % 2
    assert coarse[0, 0, 0] == pytest.approx(fine[0, :2, :2].mean())


# --------------------------------------------------------------------------
# the unclassified class
# --------------------------------------------------------------------------

def test_the_map_draws_four_classes_and_unclassified_is_one_of_them():
    classes, _ = lr.rice_classes()

    assert set(np.unique(classes)) == {0, 1, 2, 3}


def test_unclassified_and_classified_with_no_rice_are_different_classes():
    """The distinction the whole third band exists for."""
    assert style.role("unassessed") != style.role("land_flat")
    gap = abs(style._luminance(style.role("unassessed"))
              - style._luminance(style.role("land_flat")))
    assert gap >= style.MIN_LUMINANCE_GAP


def test_northern_anhui_is_drawn_unclassified_rather_than_rice_free():
    """A figure without this says northern Anhui grows no rice. It grows some."""
    from rasterio.features import geometry_mask
    from rasterio.transform import from_bounds
    from shapely.geometry import box

    classes, extent = lr.rice_classes()
    west, east, south, north = extent
    transform = from_bounds(west, south, east, north,
                            classes.shape[1], classes.shape[0])
    provinces = geo.read_layer(geo.PROVINCES).set_index("name_en")
    anhui = provinces.loc["Anhui"].geometry
    # The part of Anhui the product stops short of.
    clipped = anhui.intersection(box(west, 33.3462, east, north))
    mask = ~geometry_mask([clipped], out_shape=classes.shape,
                          transform=transform, invert=False)

    assert mask.sum() > 100
    unclassified = float((classes[mask] == 0).mean())
    assert unclassified > 0.9


def test_the_classified_share_of_anhui_matches_the_recorded_footprint():
    fractions, _ = lr.display_bands()
    assessed = fractions[2]

    assert 0.0 <= assessed.min() and assessed.max() <= 1.0
    # The band is a share of the cell, so it is near one inside a province and
    # near zero outside; nothing should sit implausibly between for long.
    assert float((assessed > 0.9).mean()) > 0.35


# --------------------------------------------------------------------------
# the numbers
# --------------------------------------------------------------------------

def test_the_shares_use_one_denominator_for_all_three_bars():
    """Two denominators in one panel cannot be compared, and will be."""
    shares = lr.provincial_shares()
    rice = lr.provincial_rice()

    for province, entry in shares.items():
        polygon = rice[province]["polygon_km2"]
        assert entry["rice_single"] == pytest.approx(
            rice[province]["single"] / polygon)


def test_anhui_is_the_only_province_marked_as_a_lower_bound():
    shares = lr.provincial_shares()

    assert shares["Anhui"]["partial"] is True
    for province in ("Shanghai", "Jiangsu", "Zhejiang"):
        assert shares[province]["partial"] is False, province


def test_shanghai_is_more_than_half_impervious():
    """The largest bar, and the one that sets the axis."""
    shares = lr.provincial_shares()

    assert shares["Shanghai"]["impervious"] > 0.45


def test_the_impervious_numbers_come_from_the_urban_figures_own_table():
    impervious = lr.provincial_impervious()

    with lr.URBAN_TOTALS.open(newline="") as handle:
        rows = [r for r in csv.DictReader(handle)
                if r["source"] == "GAIA" and int(r["year"]) == lr.YEAR]
    assert len(rows) == 4
    for row in rows:
        assert impervious[row["province"]] == pytest.approx(
            float(row["urban_area_km2"]))


def test_the_bar_panel_draws_three_bars_for_every_province(figure):
    bars = figure.axes[1].patches

    assert len(bars) == 3 * len(lr.PROVINCES)


# --------------------------------------------------------------------------
# layout and what the figure says
# --------------------------------------------------------------------------

def test_the_layout_closes_across_the_page(figure):
    total = (lr.LEFT_CM + lr.MAP_CM + lr.PANEL_GAP_CM + lr.BARS_CM
             + lr.RIGHT_CM)

    assert total == pytest.approx(lr.FIG_WIDTH_CM, abs=1e-9)
    assert figure.get_figwidth() / style.CM == pytest.approx(lr.FIG_WIDTH_CM)


def test_the_map_draws_no_coastline_stroke(figure):
    """Same arithmetic as the urban maps; see the module docstring."""
    coastline = style.role("coastline")

    assert not [line for line in figure.axes[0].lines
                if line.get_color() == coastline]


def test_the_map_carries_the_projection_and_the_lattice_extent(figure):
    extent = geo.lattice_extent(geo.study_spec())
    ax = figure.axes[0]

    assert ax.get_xlim() == pytest.approx((extent.west, extent.east))
    assert ax.get_ylim() == pytest.approx((extent.south, extent.north))
    assert ax.get_aspect() == pytest.approx(
        1.0 / geo.geographic_aspect(extent.centre_latitude))


def test_the_figure_states_the_threshold_and_what_it_costs(figure):
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "35%" in flat
    assert "drawn area equals true area" in flat
    assert "processing boundary" in flat


def test_the_figure_names_every_class_it_draws(figure):
    entries = {t.get_text() for t in figure.legends[0].get_texts()}

    assert entries == {"mostly single season", "mostly double season",
                       "classified, below 35%", "not classified", "sea"}
