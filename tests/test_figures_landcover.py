"""Tests for the native-resolution land cover figure.

Offline, reading only committed artefacts. The figure is built and asserted on
in memory; nothing is written.

The check that carries this figure is the one about resolution. Every other
property could be wrong and a reader would see it; a raster silently resampled
from 10 m to 100 m looks exactly like a raster that was not, and the figure's
whole claim is that it was not. So the drawn pixels per native pixel is
asserted for each panel, and the interpolation setting that would break it is
asserted too, because `imshow` defaults to something that would.

The second check is the one about the window. It has to lie wholly inside one
province, or the rice raster's undeclared nodata draws out-of-province
background and real non-rice land in the same colour, and it has to lie wholly
inside one analysis cell, or panel (d) cannot say which number the pixels
became.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure
from shapely.geometry import box

from src.figures import geo, style
from src.figures import landcover as lc
from src.figures.landcover import CELLS, WINDOW, landcover_figure

STUDY = geo.study_spec()


@pytest.fixture(scope="module")
def figure():
    fig = landcover_figure()
    yield fig
    plt.close(fig)


def test_the_figure_function_returns_a_figure_and_writes_nothing(tmp_path):
    before = set(tmp_path.iterdir())

    fig = landcover_figure()
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# the resolution claim
# --------------------------------------------------------------------------

def _drawn_pixels_per_native(native_columns: int) -> float:
    return lc.PANEL_CM / 2.54 * style.MIN_DPI / native_columns


@pytest.mark.parametrize("path,product,expected", [
    (lc.IMPERVIOUS_GISA, "gisa", 186),
    (lc.IMPERVIOUS_GAIA, "gaia", 186),
])
def test_each_impervious_panel_draws_at_least_one_pixel_per_native_pixel(
        path, product, expected):
    mask, _, _ = lc.impervious_mask(path, product)

    assert mask.shape[1] == expected
    assert _drawn_pixels_per_native(mask.shape[1]) >= 1.0


def test_the_rice_panel_draws_at_least_one_pixel_per_native_pixel():
    """The tight one: 10 m over 5.7 km is 557 pixels against a 812-pixel panel."""
    values, _ = lc.rice_classes()

    assert values.shape == (372, 557)
    assert _drawn_pixels_per_native(values.shape[1]) >= 1.0


def test_the_rasters_are_drawn_without_interpolation(figure):
    """Any other setting invents values between classes that have none."""
    images = [im for ax in figure.axes for im in ax.images]

    assert len(images) == 3
    for image in images:
        assert image.get_interpolation() == "nearest", image.get_label()


def test_the_rice_raster_is_three_times_finer_than_the_impervious_one():
    values, _ = lc.rice_classes()
    mask, _, _ = lc.impervious_mask(lc.IMPERVIOUS_GISA, "gisa")

    assert values.shape[1] / mask.shape[1] == pytest.approx(3.0, abs=0.01)


# --------------------------------------------------------------------------
# the window
# --------------------------------------------------------------------------

def test_the_window_lies_wholly_inside_one_province():
    """Otherwise 0 in the rice raster draws two different things alike."""
    provinces = geo.read_layer(geo.PROVINCES).set_index("name_en")
    window = box(WINDOW.west, WINDOW.south, WINDOW.east, WINDOW.north)

    assert provinces.loc["Anhui"].geometry.contains(window)
    for name in ("Jiangsu", "Shanghai", "Zhejiang"):
        assert not provinces.loc[name].geometry.intersects(window), name


def test_the_window_lies_wholly_inside_one_analysis_cell():
    lons, lats = geo.cell_edges(STUDY)
    west = lons[lons <= WINDOW.west].max()
    east = lons[lons >= WINDOW.east].min()
    south = lats[lats <= WINDOW.south].max()
    north = lats[lats >= WINDOW.north].min()

    assert east - west == pytest.approx(STUDY.resolution)
    assert north - south == pytest.approx(STUDY.resolution)


def test_the_window_carries_all_three_classes_and_none_is_marginal():
    """A window that is nearly all one thing shows a texture, not a boundary."""
    values, _ = lc.rice_classes()
    mask, _, _ = lc.impervious_mask(lc.IMPERVIOUS_GISA, "gisa")

    assert 0.20 < float(mask.mean()) < 0.40
    assert 0.20 < float((values == 1).mean()) < 0.40
    assert 0.02 < float((values == 2).mean()) < 0.10


def test_the_rice_raster_holds_only_the_three_documented_values():
    """No fourth value acts as an undeclared fill; the product has none."""
    values, _ = lc.rice_classes()

    assert set(np.unique(values)) <= {0, 1, 2}


def test_the_cells_panel_covers_the_window_and_is_three_by_two():
    cols = round((CELLS.east - CELLS.west) / STUDY.resolution)
    rows = round((CELLS.north - CELLS.south) / STUDY.resolution)

    assert (cols, rows) == (3, 2)
    assert CELLS.west <= WINDOW.west and WINDOW.east <= CELLS.east
    assert CELLS.south <= WINDOW.south and WINDOW.north <= CELLS.north


def test_the_window_is_not_representative_of_the_cell_it_sits_in():
    """Stated on the figure, so it has to be true of the figure's own numbers."""
    values, _ = lc.rice_classes()
    window_rice = float((values > 0).mean())
    cell = lc.cell_values()[(31.325, 118.425)]

    assert window_rice > 1.5 * cell["rice_fraction_combined"]


# --------------------------------------------------------------------------
# what the analysis reads
# --------------------------------------------------------------------------

def test_the_cell_numbers_come_from_the_committed_tables():
    """Not recomputed: the figure shows what the baselines were fitted on."""
    import csv

    values = lc.cell_values()
    assert len(values) == 6

    with open(lc.GRID, newline="") as handle:
        rows = {(round(float(r["centre_lat"]), 3),
                 round(float(r["centre_lon"]), 3)): r
                for r in csv.DictReader(handle)}
    for key, drawn in values.items():
        assert drawn["impervious_fraction"] == pytest.approx(
            float(rows[key]["impervious_fraction"]))


def test_every_drawn_cell_has_full_coverage_so_no_caveat_is_owed():
    for values in lc.cell_values().values():
        assert values["rice_coverage"] == pytest.approx(1.0, abs=0.01)
        assert values["impervious_coverage"] == pytest.approx(1.0, abs=0.01)


def test_the_cells_panel_writes_a_number_for_every_cell(figure):
    cells = figure.axes[3]
    numbers = [t for t in cells.texts if "GISA" in t.get_text()]

    assert len(numbers) == 6
    for text in numbers:
        assert "GAIA" in text.get_text() and "rice" in text.get_text()


def test_the_native_window_is_marked_and_named_on_the_cells_panel(figure):
    cells = figure.axes[3]
    marks = [p for p in cells.patches if p.get_label() == "native-window"]

    assert len(marks) == 1
    assert any("(a)" in t.get_text() for t in cells.texts)


# --------------------------------------------------------------------------
# selectors, not thresholds
# --------------------------------------------------------------------------

def test_the_two_products_are_selected_by_their_own_conventions():
    """Applying one product's rule to the other inverts its history."""
    _, _, gisa = lc.impervious_mask(lc.IMPERVIOUS_GISA, "gisa")
    _, _, gaia = lc.impervious_mask(lc.IMPERVIOUS_GAIA, "gaia")

    assert gisa == "1 <= value <= 36"
    assert gaia == "value >= 5"


def test_the_inverted_gisa_rule_would_have_selected_almost_nothing():
    """The failure the selectors exist to prevent, measured on this window."""
    from src.landcover.selectors import at_least

    values, _ = geo.read_raster(lc.IMPERVIOUS_GISA)
    correct, _, _ = lc.impervious_mask(lc.IMPERVIOUS_GISA, "gisa")
    inverted = at_least(lc.GISA_2018_CODE)(values)

    assert inverted.sum() < 0.1 * correct.sum()


def test_the_two_products_disagree_about_this_window_as_they_do_regionally():
    gisa, _, _ = lc.impervious_mask(lc.IMPERVIOUS_GISA, "gisa")
    gaia, _, _ = lc.impervious_mask(lc.IMPERVIOUS_GAIA, "gaia")

    ratio = float(gisa.mean()) / float(gaia.mean())
    assert 0.75 < ratio < 0.85     # four-province 2018 ratio is 0.801


# --------------------------------------------------------------------------
# layout
# --------------------------------------------------------------------------

def test_the_layout_closes_across_the_page(figure):
    total = (lc.LEFT_CM + lc.PANEL_CM + lc.GUTTER_CM + lc.PANEL_CM
             + lc.RIGHT_CM)

    assert total == pytest.approx(lc.FIG_WIDTH_CM, abs=1e-9)
    assert figure.get_figwidth() / style.CM == pytest.approx(lc.FIG_WIDTH_CM)


def test_all_four_panels_are_the_same_shape(figure):
    """The window's height was chosen for this; see the module docstring.

    Not to machine precision: the window's south and north are rounded to four
    decimal places, which leaves its drawn proportion 0.08 percent away from
    the cells panel's, and `apply_projection` sets an aspect that matplotlib
    honours by shrinking each axes box to fit. The tolerance is that rounding
    and nothing else.
    """
    shapes = [figure.axes[i].get_position() for i in range(4)]

    for box_ in shapes:
        assert box_.width == pytest.approx(shapes[0].width, abs=1e-9)
        assert box_.height == pytest.approx(shapes[0].height, rel=0.002)
    assert geo.display_ratio(WINDOW) == pytest.approx(
        geo.display_ratio(CELLS), rel=0.002)


def test_every_panel_sits_inside_the_figure(figure):
    for index, ax in enumerate(figure.axes):
        box_ = ax.get_position()
        assert 0.0 <= box_.x0 and box_.x1 <= 1.0, index
        assert 0.0 <= box_.y0 and box_.y1 <= 1.0, index


def test_the_figure_names_every_class_it_draws(figure):
    entries = {t.get_text() for t in figure.legends[0].get_texts()}

    assert entries == {"impervious surface", "rice, single season",
                       "rice, double season", "neither, and looked at"}


def test_the_source_asymmetry_is_stated_on_the_figure(figure):
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "30 m from Landsat" in flat
    assert "Sentinel-1 and Sentinel-2" in flat
    assert "0.25° cell" in flat
