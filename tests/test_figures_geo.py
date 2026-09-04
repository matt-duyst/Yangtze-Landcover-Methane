"""Tests for the shared geospatial conventions.

Offline. The only files read are the committed layers in `data/reference/`,
which are public-domain Natural Earth extracts held in the repository exactly
so that nothing reaches into a machine-local cache at draw time.

The test that carries the weight is the extent. The analysis grid's declared
bounds and the bounds its cells actually occupy are not the same, and they
differ in opposite directions on the two axes, so a map drawn to the declared
box disagrees with the data at two of its four edges by one cell. That is the
kind of quiet inconsistency this project exists to catch, and it is cheap to
pin.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.figures import geo
from src.methane.grid import GridSpec

STUDY = GridSpec(west=114.8, south=27.0, east=122.6, north=35.2, resolution=0.25)


def test_the_lattice_extent_is_the_measured_one_not_the_declared_one():
    extent = geo.lattice_extent(STUDY)

    # 7.8 degrees is 31.2 cells, rounded down: the grid stops short of 122.6.
    assert extent.east == pytest.approx(122.55)
    assert extent.east < STUDY.east
    # 8.2 degrees is 32.8 cells, rounded up: the grid runs past 27.0.
    assert extent.south == pytest.approx(26.95)
    assert extent.south < STUDY.south
    # The two anchored edges are untouched.
    assert extent.west == pytest.approx(STUDY.west)
    assert extent.north == pytest.approx(STUDY.north)


def test_the_extent_spans_exactly_the_declared_number_of_cells():
    extent = geo.lattice_extent(STUDY)

    assert (extent.east - extent.west) / STUDY.resolution == pytest.approx(STUDY.n_cols)
    assert (extent.north - extent.south) / STUDY.resolution == pytest.approx(STUDY.n_rows)


def test_cell_edges_bound_every_cell_and_agree_with_the_extent():
    lons, lats = geo.cell_edges(STUDY)
    extent = geo.lattice_extent(STUDY)

    assert lons.size == STUDY.n_cols + 1
    assert lats.size == STUDY.n_rows + 1
    assert lons[0] == pytest.approx(extent.west)
    assert lons[-1] == pytest.approx(extent.east)
    assert lats[0] == pytest.approx(extent.south)
    assert lats[-1] == pytest.approx(extent.north)
    assert np.allclose(np.diff(lons), STUDY.resolution)
    assert np.allclose(np.diff(lats), STUDY.resolution)


def test_the_aspect_is_the_cosine_of_the_latitude():
    # Without this a degree of longitude is drawn as long as a degree of
    # latitude and the map is stretched east-west by 1/cos.
    assert geo.geographic_aspect(0.0) == pytest.approx(1.0)
    assert geo.geographic_aspect(60.0) == pytest.approx(0.5, abs=1e-9)
    assert geo.geographic_aspect(31.075) == pytest.approx(0.85649, abs=1e-5)


def test_the_study_box_draws_taller_than_it_is_wide():
    extent = geo.lattice_extent(STUDY)

    # 7.75 degrees of longitude against 8.25 of latitude: wider in degrees,
    # taller on the page.
    assert extent.east - extent.west < extent.north - extent.south
    assert geo.display_ratio(extent) == pytest.approx(1.2426, abs=1e-3)


def test_figure_height_follows_from_the_extent_and_the_width():
    extent = geo.lattice_extent(STUDY)

    height = geo.figure_height_cm(extent, 11.4, margins_cm=(1.0, 1.0))

    assert height == pytest.approx((11.4 - 1.0) * geo.display_ratio(extent) + 1.0)


def test_apply_projection_sets_both_limits_and_the_aspect():
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots()
    try:
        extent = geo.lattice_extent(STUDY)
        geo.apply_projection(ax, extent)

        assert ax.get_xlim() == pytest.approx((extent.west, extent.east))
        assert ax.get_ylim() == pytest.approx((extent.south, extent.north))
        assert ax.get_aspect() == pytest.approx(
            1.0 / geo.geographic_aspect(extent.centre_latitude))
    finally:
        plt.close(fig)


def test_degree_ticks_carry_a_hemisphere_letter():
    east = geo.degree_formatter("x")
    north = geo.degree_formatter("y")

    assert east(122.55) == "122.55°E"
    assert east(-10.0) == "10°W"
    assert north(31.0) == "31°N"
    assert north(-31.0) == "31°S"


def test_the_graticule_falls_on_whole_degrees_inside_the_extent():
    extent = geo.lattice_extent(STUDY)

    xticks, yticks = geo.graticule(extent, step=2.0)

    assert list(xticks) == [116.0, 118.0, 120.0, 122.0]
    assert list(yticks) == [28.0, 30.0, 32.0, 34.0]
    assert xticks.min() >= extent.west and xticks.max() <= extent.east
    assert yticks.min() >= extent.south and yticks.max() <= extent.north


def test_albers_projects_to_metres_and_is_not_the_identity():
    x, y = geo.to_albers([121.4737], [31.2304])

    # A silent identity transform would return the degrees back.
    assert abs(float(x[0])) > 1e5
    assert abs(float(y[0])) > 1e5


def test_the_committed_reference_layers_exist_and_are_geographic():
    for path in (geo.PROVINCES, geo.LAND, geo.CHINA):
        assert path.is_file(), path
        frame = geo.read_layer(path)
        assert len(frame) > 0
        assert frame.crs.to_epsg() == 4326


def test_the_province_layer_holds_the_four_study_provinces():
    frame = geo.read_layer(geo.PROVINCES)
    names = set(frame.get("name_en", frame.get("name")))

    assert names == {"Anhui", "Jiangsu", "Zhejiang", "Shanghai"}


def test_the_land_layer_covers_the_whole_drawn_extent():
    """A gap would leave sea colour where there is land."""
    extent = geo.lattice_extent(STUDY)
    bounds = geo.read_layer(geo.LAND).total_bounds

    assert bounds[0] <= extent.west and bounds[2] >= extent.east
    assert bounds[1] <= extent.south and bounds[3] >= extent.north
