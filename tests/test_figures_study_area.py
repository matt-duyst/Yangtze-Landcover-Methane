"""Tests for the study area map.

Offline, reading only the committed reference layers. The figure is built and
asserted on in memory; nothing is written.

Four kinds of check, and the last two are the ones that earn their place.

* **The frame is the data's frame.** A map whose extent is one cell away from
  the lattice it will later carry is wrong in a way looking at it will not
  reveal.
* **The layout closes.** Panel widths are stated in centimetres and have to sum
  to the figure's width; a column that runs off the page is a rendering
  everybody sees and nobody can diff.
* **Nothing is drawn where it cannot be seen, and nothing that is drawn
  contributes nothing.** The label points are asserted to lie inside the
  polygons they name, and the relief image is asserted to cover pixels. This
  repository has already shipped an element at exactly zero visible pixels.
* **The decisions that were made are the ones the code makes.** No lattice on
  the main panel, no leader line to Shanghai, the inset off the data, the
  boundary layer unfiltered. Each of those was a choice, and a test is how a
  choice survives the next edit.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure
from shapely.geometry import Point

from src.figures import geo, style
from src.figures import study_area as sa
from src.figures.study_area import (
    DETAIL_WINDOW,
    PROVINCE_LABELS,
    study_area_figure,
)

#: The real grid, read from the configuration rather than written out here, so
#: the figure cannot be tested against a spec the data was not built on.
STUDY = geo.study_spec()


@pytest.fixture(scope="module")
def figure():
    fig = study_area_figure(STUDY)
    yield fig
    plt.close(fig)


@pytest.fixture(scope="module")
def provinces():
    return geo.read_layer(geo.PROVINCES)


def test_the_figure_function_returns_a_figure_and_writes_nothing(tmp_path):
    before = set(tmp_path.iterdir())

    fig = study_area_figure(STUDY)
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# the frame
# --------------------------------------------------------------------------

def test_the_drawn_extent_is_the_lattice_extent_not_the_declared_box(figure):
    extent = geo.lattice_extent(STUDY)
    main = figure.axes[0]

    assert main.get_xlim() == pytest.approx((extent.west, extent.east))
    assert main.get_ylim() == pytest.approx((extent.south, extent.north))
    assert main.get_xlim()[1] == pytest.approx(STUDY.east)
    assert main.get_ylim()[0] == pytest.approx(STUDY.south)


def test_the_map_carries_the_projection_aspect(figure):
    extent = geo.lattice_extent(STUDY)

    assert figure.axes[0].get_aspect() == pytest.approx(
        1.0 / geo.geographic_aspect(extent.centre_latitude))


def test_the_layout_closes_across_the_page(figure):
    """The stated centimetres have to add up to the figure they describe."""
    total = (sa.LEFT_CM + sa.MAP_WIDTH_CM + sa.GUTTER_CM + sa.COLUMN_CM
             + sa.RIGHT_CM)

    assert total == pytest.approx(sa.FIG_WIDTH_CM, abs=1e-9)
    assert figure.get_figwidth() / style.CM == pytest.approx(sa.FIG_WIDTH_CM)
    # And the map's own height follows from its extent, not from a guess.
    map_height = sa.MAP_WIDTH_CM * geo.display_ratio(geo.lattice_extent(STUDY))
    assert figure.get_figheight() / style.CM == pytest.approx(
        map_height + sa.BOTTOM_CM + sa.TOP_CM, abs=1e-6)


def test_every_panel_sits_inside_the_figure(figure):
    for index, ax in enumerate(figure.axes):
        box_ = ax.get_position()
        assert 0.0 <= box_.x0 and box_.x1 <= 1.0, index
        assert 0.0 <= box_.y0 and box_.y1 <= 1.0, index


# --------------------------------------------------------------------------
# the inset is off the data
# --------------------------------------------------------------------------

def test_the_inset_does_not_overlap_the_map(figure):
    """The first version covered Zhejiang's coast and the Zhoushan islands."""
    main, inset = figure.axes[0].get_position(), figure.axes[1].get_position()

    assert main.x1 <= inset.x0 or inset.x1 <= main.x0


def test_the_detail_box_does_not_overlap_the_map(figure):
    main, detail = figure.axes[0].get_position(), figure.axes[2].get_position()

    assert main.x1 <= detail.x0 or detail.x1 <= main.x0


def test_the_inset_has_no_ticks_and_is_drawn_in_the_equal_area_conic(figure):
    inset = figure.axes[1]

    assert list(inset.get_xticks()) == []
    assert list(inset.get_yticks()) == []
    # Albers metres, not degrees: a longitude would never reach six figures.
    assert abs(inset.get_xlim()[0]) > 1e5


def test_the_inset_draws_every_boundary_line_in_its_extent_and_filters_none():
    """It asserts nothing by filtering nothing. See `_draw_inset`."""
    lines = geo.read_layer(geo.INSET_BOUNDARIES)
    classes = set(lines["featurecla"])

    assert len(lines) >= 50
    # Natural Earth's own hedging is carried through rather than resolved.
    assert any("Disputed" in name for name in classes)
    assert any("International boundary" in name for name in classes)


# --------------------------------------------------------------------------
# labels
# --------------------------------------------------------------------------

def test_every_province_label_sits_inside_the_province_it_names(provinces):
    """A name outside its own polygon is a name pointing at the wrong thing."""
    indexed = provinces.set_index("name_en")

    for name, (lon, lat) in PROVINCE_LABELS.items():
        assert indexed.loc[name].geometry.contains(Point(lon, lat)), name


def test_shanghai_is_named_once_and_takes_no_leader_line(figure):
    """The leader was the tell that the encoding was not working.

    Shanghai is too small to hold a province label at this scale, so it is
    named by its city label instead -- it is also one of the four capitals --
    and no line is drawn from a name to a place anywhere on the map.
    """
    assert "Shanghai" not in PROVINCE_LABELS

    main = figure.axes[0]
    names = [text.get_text() for text in main.texts]
    assert names.count("Shanghai") == 1

    # Every line on the main panel is a place marker; none is a leader.
    for line in main.lines:
        assert str(line.get_linestyle()).lower() == "none", line.get_label()
        assert line.get_marker() != "None", line.get_label()


def test_all_four_study_provinces_are_identifiable_by_name(figure):
    names = {text.get_text() for text in figure.axes[0].texts}

    assert {"Anhui", "Jiangsu", "Zhejiang", "Shanghai"} <= names


def test_every_neighbouring_province_is_named(figure):
    names = {text.get_text() for text in figure.axes[0].texts}
    neighbours = set(geo.read_layer(geo.NEIGHBOURS)["name"])

    assert neighbours == {"Fujian", "Henan", "Hubei", "Jiangxi", "Shandong"}
    assert neighbours <= names


def test_every_label_sits_inside_the_drawn_extent(figure):
    """A label placed off the frame is a label the reader never sees."""
    extent = geo.lattice_extent(STUDY)

    for text in figure.axes[0].texts:
        lon, lat = text.get_position()
        assert extent.west <= lon <= extent.east, text.get_text()
        assert extent.south <= lat <= extent.north, text.get_text()


# --------------------------------------------------------------------------
# places
# --------------------------------------------------------------------------

def test_the_capitals_are_one_per_study_province_and_chosen_by_a_rule():
    """Not a hand-picked list: a threshold and two filters on the layer.

    A bare scale-rank threshold cannot produce this set. Shanghai is rank 0,
    Nanjing and Hangzhou are rank 2 and Hefei is rank 4, so a threshold that
    reaches Hefei reaches fourteen other places as well.
    """
    places = geo.read_layer(geo.PLACES)

    assert set(places["name"]) == {"Shanghai", "Nanjing", "Hangzhou", "Hefei"}
    assert set(places["province"]) == {"Shanghai", "Jiangsu", "Zhejiang",
                                       "Anhui"}
    assert places["scalerank"].max() == 4
    assert places["scalerank"].min() == 0


def test_each_capital_is_drawn_as_a_marker_inside_its_own_province(provinces):
    places = geo.read_layer(geo.PLACES)
    indexed = provinces.set_index("name_en")

    for _, row in places.iterrows():
        polygon = indexed.loc[row["province"]].geometry
        assert polygon.contains(row.geometry), row["name"]


def test_the_capitals_are_drawn_as_points_and_not_as_lines(figure):
    markers = [line for line in figure.axes[0].lines
               if line.get_label() == "place-marker"]

    assert len(markers) == 4
    for marker in markers:
        assert marker.get_marker() == "o"
        assert len(marker.get_xdata()) == 1


# --------------------------------------------------------------------------
# the lattice moved to a detail box
# --------------------------------------------------------------------------

def test_the_main_panel_draws_no_lattice(figure):
    """Redundant with the composite, which draws the cells as the data."""
    main = figure.axes[0]
    lattice = style.role("lattice")

    assert not [line for line in main.lines if line.get_color() == lattice]
    assert not [c for c in main.collections
                if getattr(c, "get_color", None)
                and lattice in [str(x) for x in np.atleast_1d(c.get_color())]]


def test_the_detail_window_lies_on_cell_edges():
    """A window that cuts a cell in half shows the reader the wrong size."""
    lons, lats = geo.cell_edges(STUDY)

    for value, edges in ((DETAIL_WINDOW.west, lons), (DETAIL_WINDOW.east, lons),
                         (DETAIL_WINDOW.south, lats), (DETAIL_WINDOW.north, lats)):
        assert np.min(np.abs(edges - value)) < 1e-9, value


def test_the_detail_box_shows_six_cells(figure):
    cols = round((DETAIL_WINDOW.east - DETAIL_WINDOW.west) / STUDY.resolution)
    rows = round((DETAIL_WINDOW.north - DETAIL_WINDOW.south) / STUDY.resolution)

    assert cols * rows == 6
    detail = figure.axes[2]
    assert len(detail.lines) == (cols + 1) + (rows + 1)


def test_the_detail_box_draws_no_coastline_stroke(figure):
    """Measured, not omitted. See `_draw_detail` and `style.py`.

    With the relief band's floor where it is, no assignment holds the sea, a
    coastline and a lattice line all 0.15 apart in luminance and all clear of
    the band. The stroke is what was dropped.
    """
    detail = figure.axes[2]
    coastline = style.role("coastline")

    assert not [line for line in detail.lines
                if line.get_color() == coastline]


def test_the_detail_window_is_outlined_on_the_main_panel(figure):
    """So the reader sees the true drawn size as well as the legible one."""
    windows = [p for p in figure.axes[0].patches
               if p.get_label() == "detail-window"]

    assert len(windows) == 1
    patch = windows[0]
    assert patch.get_x() == pytest.approx(DETAIL_WINDOW.west)
    assert patch.get_width() == pytest.approx(
        DETAIL_WINDOW.east - DETAIL_WINDOW.west)


def test_the_detail_box_is_an_enlargement_and_says_by_how_much():
    assert sa._detail_scale() > 1.0
    assert sa._detail_scale() == pytest.approx(4.61, abs=0.05)


def test_one_cell_in_kilometres_is_computed_and_not_written_down():
    east_west, north_south = sa.cell_kilometres(
        STUDY, DETAIL_WINDOW.centre_latitude)

    # A quarter degree of latitude is a quarter degree of latitude anywhere.
    assert north_south == pytest.approx(27.8, abs=0.1)
    # And a quarter degree of longitude is shorter, by cos(latitude).
    assert east_west == pytest.approx(
        north_south * np.cos(np.radians(DETAIL_WINDOW.centre_latitude)),
        rel=1e-9)


# --------------------------------------------------------------------------
# the relief
# --------------------------------------------------------------------------

def test_the_relief_is_one_image_and_it_covers_pixels(figure):
    """Present, correct in isolation, and contributing nothing is a real bug."""
    images = [im for im in figure.axes[0].images
              if im.get_label() == sa.RELIEF_ARTIST]

    assert len(images) == 1
    array = images[0].get_array()
    assert array.size > 0
    assert np.ptp(array) > 0.0  # not a flat fill wearing a relief's name


def test_the_relief_stays_inside_the_bands_the_palette_declares(provinces):
    """What the raster delivers has to be what the convention promised."""
    land = geo.read_layer(geo.LAND)
    layers = sa.relief_image(land, provinces,
                             panel_width_cm=sa.MAP_WIDTH_CM)
    rgb = layers["rgb"]
    lum = (0.2126 * rgb[..., 0] + 0.7152 * rgb[..., 1] + 0.0722 * rgb[..., 2])

    inside = style.veiled_band("province_fill", style.REGION_TINT_ALPHA)
    outside = style.veiled_band("land_outside", style.LAND_VEIL_ALPHA)
    floor = min(inside[0], outside[0])
    ceiling = max(inside[1], outside[1])
    # The sea is painted into the array where the clip path hides it, so it is
    # excluded here by value rather than by mask.
    sea = style._luminance(style.role("sea"))
    relief = lum[np.abs(lum - sea) > 1e-6]

    assert relief.min() >= floor - 1e-6
    assert relief.max() <= ceiling + 1e-6


def test_the_relief_is_drawn_over_land_and_not_over_water(provinces):
    land = geo.read_layer(geo.LAND)
    layers = sa.relief_image(land, provinces,
                             panel_width_cm=sa.MAP_WIDTH_CM)

    # Most of the frame is land, and the study provinces are most of that.
    assert 0.7 < layers["land_fraction"] < 0.9
    assert 0.4 < layers["inside_fraction"] < 0.7


def test_the_hillshade_covers_the_drawn_extent():
    """A relief that stops short of the frame leaves a band of bare sea."""
    extent = geo.lattice_extent(STUDY)
    _, (west, east, south, north) = geo.read_raster(geo.HILLSHADE)

    assert west <= extent.west and east >= extent.east
    assert south <= extent.south and north >= extent.north


# --------------------------------------------------------------------------
# attribution
# --------------------------------------------------------------------------

def test_the_figure_carries_the_licence_notice_the_dem_requires(figure):
    """Article 6(b), for adapted or modified data, quoted rather than
    paraphrased. A figure travels away from its caption."""
    text = " ".join(t.get_text() for t in figure.texts)
    flat = " ".join(text.split())

    assert "produced using Copernicus WorldDEM" in flat
    assert "DLR e.V. 2010–2014" in flat
    assert "Airbus Defence and Space GmbH 2014–2018" in flat
    assert "all rights reserved" in flat
    assert "Natural Earth" in flat


def test_the_legend_names_every_class_it_draws_and_in_black(figure):
    legend = figure.legends[0]
    entries = {text.get_text() for text in legend.get_texts()}

    assert entries == {"study provinces", "neighbouring provinces", "sea",
                       "provincial capital"}
    import matplotlib.colors as mcolors
    for text in legend.get_texts():
        assert mcolors.to_rgba(text.get_color()) == (0.0, 0.0, 0.0, 1.0)


# --------------------------------------------------------------------------
# the palette, from this figure's side
# --------------------------------------------------------------------------

def test_the_areal_classes_stay_separable_in_greyscale():
    report = style.relief_report()

    assert report["flat_ground_gap"] >= style.MIN_LUMINANCE_GAP
    assert report["sea_clearance"] >= style.MIN_LUMINANCE_GAP
    assert report["failures"] == []


def test_the_map_colours_are_roles_and_the_roles_are_checked_elsewhere():
    """The all-pairs check this file used to carry has moved, and narrowed.

    It asserted that all six map colours separate from each other in
    greyscale. That is no longer possible and, measured, it never was
    necessary. With shaded relief under the overlays the relief's floor takes
    the top third of the scale, and sea, a coastline and a lattice line cannot
    all sit 0.15 apart in what is left; the detail box drops its coastline
    stroke for exactly that reason. The check that replaced it is over the
    pairs that actually meet on the page, in `tests/test_figures_palette.py`,
    and it runs once over the role set rather than once per figure.
    """
    colours = {role.colour for role in style.ROLES.values()}
    for constant in ("MAP_SEA", "MAP_LAND", "MAP_STUDY_FILL", "MAP_LATTICE",
                     "MAP_BOUNDARY", "MAP_COASTLINE"):
        assert getattr(style, constant) in colours
    assert style.greyscale_report()["failures"] == []
