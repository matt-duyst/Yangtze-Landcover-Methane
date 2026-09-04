"""Tests for the study area map.

Offline, reading only the committed reference layers. The figure is built and
asserted on in memory; nothing is written.

The check worth having is that the drawn extent equals the lattice's measured
extent. Everything else about a reference map is judged by looking at it, but
a map whose frame is one cell away from the data it will later carry is wrong
in a way that looking will not reveal.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import pytest
from matplotlib.figure import Figure

from src.figures import geo, style
from src.figures.study_area import PROVINCE_LABELS, study_area_figure
from src.methane.grid import GridSpec

STUDY = GridSpec(west=114.8, south=27.0, east=122.6, north=35.2, resolution=0.25)


@pytest.fixture
def figure():
    fig = study_area_figure(STUDY)
    yield fig
    plt.close(fig)


def test_the_figure_function_returns_a_figure_and_writes_nothing(tmp_path):
    before = set(tmp_path.iterdir())

    fig = study_area_figure(STUDY)
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


def test_the_drawn_extent_is_the_lattice_extent_not_the_declared_box(figure):
    extent = geo.lattice_extent(STUDY)
    main = figure.axes[0]

    assert main.get_xlim() == pytest.approx((extent.west, extent.east))
    assert main.get_ylim() == pytest.approx((extent.south, extent.north))
    # Specifically not the declared bounds, which differ on two edges.
    assert main.get_xlim()[1] != pytest.approx(STUDY.east)
    assert main.get_ylim()[0] != pytest.approx(STUDY.south)


def test_the_map_carries_the_projection_aspect(figure):
    extent = geo.lattice_extent(STUDY)

    assert figure.axes[0].get_aspect() == pytest.approx(
        1.0 / geo.geographic_aspect(extent.centre_latitude))


def test_the_figure_is_shaped_to_the_map_rather_than_the_map_to_the_figure(figure):
    extent = geo.lattice_extent(STUDY)
    width_cm = figure.get_figwidth() / style.CM
    height_cm = figure.get_figheight() / style.CM

    assert height_cm > width_cm            # the extent draws portrait
    assert height_cm == pytest.approx(geo.figure_height_cm(extent, width_cm),
                                      abs=0.01)
    assert width_cm >= style.MIN_WIDTH_CM  # still above the venue floor


def test_the_lattice_is_drawn_at_every_cell_edge(figure):
    lons, lats = geo.cell_edges(STUDY)
    main = figure.axes[0]

    drawn = [line for line in main.lines
             if line.get_color() == style.MAP_LATTICE]
    assert len(drawn) == lons.size + lats.size


def test_the_only_grid_is_the_analysis_lattice(figure):
    """The venue standard forbids background gridlines."""
    main = figure.axes[0]

    assert main.xaxis._major_tick_kw.get("gridOn") in (None, False)
    assert not main.xaxis.get_gridlines()[0].get_visible() if \
        main.xaxis.get_gridlines() else True


def test_all_four_provinces_are_named_on_the_map(figure):
    labels = {text.get_text() for text in figure.axes[0].texts}

    assert {"Anhui", "Jiangsu", "Zhejiang", "Shanghai"} <= labels


def test_every_label_sits_inside_the_drawn_extent(figure):
    """A label placed off the frame is a label the reader never sees."""
    extent = geo.lattice_extent(STUDY)

    for lon, lat, _anchor in PROVINCE_LABELS.values():
        assert extent.west <= lon <= extent.east, (lon, lat)
        assert extent.south <= lat <= extent.north, (lon, lat)


def test_the_legend_names_every_areal_class(figure):
    legend = figure.axes[0].get_legend()
    entries = {text.get_text() for text in legend.get_texts()}

    assert "sea" in entries
    assert any("study provinces" in entry for entry in entries)
    assert any("outside" in entry for entry in entries)
    assert any("0.25" in entry for entry in entries)
    # Black text, never coloured: the venue standard, and the readers it is
    # for are the same readers the colour map is chosen for.
    import matplotlib.colors as mcolors
    for text in legend.get_texts():
        assert mcolors.to_rgba(text.get_color()) == (0.0, 0.0, 0.0, 1.0)


def test_the_figure_has_a_locator_inset_with_no_ticks(figure):
    assert len(figure.axes) == 2
    inset = figure.axes[1]

    assert list(inset.get_xticks()) == []
    assert list(inset.get_yticks()) == []
    assert inset.get_aspect() == 1.0  # "equal" resolves to a ratio


def test_the_areal_classes_stay_separable_in_greyscale():
    luminance = style.map_luminances()
    areal = [luminance[name] for name in style.MAP_AREAL_CLASSES]

    gaps = [abs(a - b) for i, a in enumerate(areal) for b in areal[i + 1:]]
    assert min(gaps) >= 0.15


def test_every_map_colour_separates_from_every_other_in_greyscale():
    """Line colours included, not only the fills.

    A reader in black and white has to tell a lattice line from a coastline
    as well as a fill from a fill, and the two line colours are the pair that
    has failed twice.
    """
    luminance = style.map_luminances()
    values = sorted(luminance.items(), key=lambda item: item[1])

    for (lo_name, lo), (hi_name, hi) in zip(values, values[1:]):
        assert hi - lo >= 0.15, f"{lo_name} {lo:.3f} vs {hi_name} {hi:.3f}"
