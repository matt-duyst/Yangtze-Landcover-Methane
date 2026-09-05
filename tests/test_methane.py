"""Tests for the methane gridding module.

Offline throughout. Granules are built in ``tmp_path`` with the real group
structure and real attribute names, and the geometry of each fixture is chosen
so the gridded answer is known in advance rather than merely self-consistent.

Two cases carry most of the weight. The quality threshold is applied to a
``uint8`` array with ``scale_factor`` 0.01, so a naive float comparison keeps
everything; there is a test that fails if the conversion is dropped. And an
empty cell must come back as NaN rather than zero, because a cell nobody
observed and a cell with no methane are different claims and most of this grid
is the former.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import numpy as np
import pytest

from src.methane import grid as mg
from src.methane import Composite, GridSpec, coverage_of, grid_granules, read_soundings

FILL = 9.969209968386869e+36

#: 0.25 degree over the study box: 33 by 31 cells, as the config declares.
#: The live study grid, 26.95 to 35.2 north and 114.8 to 122.55 east. These
#: are the bounds the 0.25 degree lattice occupies; the box used to be declared
#: as 27.0 and 122.6 and did not.
STUDY = GridSpec(west=114.8, south=26.95, east=122.55, north=35.2,
                 resolution=0.25)

#: A small grid with round numbers, for fixtures whose answer is hand-checkable.
TOY = GridSpec(west=0.0, south=0.0, east=1.0, north=1.0, resolution=0.5)


def write_granule(path, *, lat, lon, primary, secondary=None, qa_stored,
                  lat_fill=None, lon_fill=None, qa_fill=255, qa_scale=0.01,
                  value_fill=FILL):
    """Write a granule from explicit per-sounding arrays.

    Shapes follow the real product: (time, scanline, ground_pixel).
    """
    import netCDF4

    lat = np.asarray(lat, dtype="f4")
    n = lat.size
    lon = np.asarray(lon, dtype="f4")
    primary = np.asarray(primary, dtype="f4")
    secondary = np.asarray(primary if secondary is None else secondary, dtype="f4")
    qa_stored = np.asarray(qa_stored, dtype="u1")

    with netCDF4.Dataset(path, "w", format="NETCDF4") as ds:
        group = ds.createGroup("PRODUCT")
        group.createDimension("time", 1)
        group.createDimension("scanline", 1)
        group.createDimension("ground_pixel", n)
        dims = ("time", "scanline", "ground_pixel")

        for name, values in ((mg.PRIMARY, primary), (mg.SECONDARY, secondary)):
            var = group.createVariable(name, "f4", dims, fill_value=value_fill)
            var.set_auto_maskandscale(False)
            var[:] = values.reshape(1, 1, n)

        qa = group.createVariable("qa_value", "u1", dims, fill_value=qa_fill)
        qa.set_auto_maskandscale(False)
        qa.scale_factor = qa_scale
        qa[:] = qa_stored.reshape(1, 1, n)

        for name, values, fill in (("latitude", lat, lat_fill),
                                   ("longitude", lon, lon_fill)):
            var = (group.createVariable(name, "f4", dims, fill_value=fill)
                   if fill is not None else group.createVariable(name, "f4", dims))
            var.set_auto_maskandscale(False)
            var[:] = values.reshape(1, 1, n)
    return path


def named(tmp_path, stem="S5P_RPRO_L2__CH4____20180514T042147_20180514T060317"
                        "_03019_03_020400_20221109T092730"):
    return tmp_path / f"{stem}.nc"


# --------------------------------------------------------------------------
# grid geometry
# --------------------------------------------------------------------------

def test_the_study_grid_is_33_by_31():
    assert STUDY.shape == (33, 31)
    assert STUDY.n_cells == 33 * 31 == 1023


def test_cells_are_indexed_from_the_north_west():
    row, col, inside = STUDY.cell_of([35.1, 27.1], [114.9, 122.5])
    assert (row[0], col[0]) == (0, 0)                 # north-west corner
    assert (row[1], col[1]) == (32, 30)               # south-east corner
    assert inside.all()


def test_soundings_outside_the_box_are_flagged_not_clipped():
    _, _, inside = STUDY.cell_of([40.0, 31.0, 10.0], [118.0, 130.0, 118.0])
    assert list(inside) == [False, False, False]


# --------------------------------------------------------------------------
# binning
# --------------------------------------------------------------------------

def test_soundings_bin_into_the_expected_cells(tmp_path):
    """One sounding in each of the toy grid's four cells."""
    path = write_granule(named(tmp_path),
                         lat=[0.75, 0.75, 0.25, 0.25],
                         lon=[0.25, 0.75, 0.25, 0.75],
                         primary=[1900.0, 1910.0, 1920.0, 1930.0],
                         qa_stored=[100, 100, 100, 100])
    composite = grid_granules([path], TOY)
    mean, count = composite.grids(mg.PRIMARY)
    assert count.tolist() == [[1, 1], [1, 1]]
    assert mean[0, 0] == pytest.approx(1900.0)
    assert mean[0, 1] == pytest.approx(1910.0)
    assert mean[1, 0] == pytest.approx(1920.0)
    assert mean[1, 1] == pytest.approx(1930.0)


def test_several_soundings_in_one_cell_are_averaged(tmp_path):
    path = write_granule(named(tmp_path),
                         lat=[0.75, 0.76, 0.74],
                         lon=[0.25, 0.24, 0.26],
                         primary=[1800.0, 1900.0, 2000.0],
                         qa_stored=[100, 100, 100])
    composite = grid_granules([path], TOY)
    mean, count = composite.grids(mg.PRIMARY)
    assert count[0, 0] == 3
    assert mean[0, 0] == pytest.approx(1900.0)
    assert composite.total_soundings == 3


def test_soundings_from_several_granules_pool_into_one_cell(tmp_path):
    a = write_granule(tmp_path / "a.nc", lat=[0.75], lon=[0.25],
                      primary=[1800.0], qa_stored=[100])
    b = write_granule(tmp_path / "b.nc", lat=[0.75], lon=[0.25],
                      primary=[2000.0], qa_stored=[100])
    composite = grid_granules([a, b], TOY)
    mean, count = composite.grids(mg.PRIMARY)
    assert count[0, 0] == 2
    assert mean[0, 0] == pytest.approx(1900.0)


# --------------------------------------------------------------------------
# the qa threshold, in stored units
# --------------------------------------------------------------------------

def test_stored_threshold_converts_through_the_scale_factor():
    assert mg.stored_threshold(0.75, 0.01) == pytest.approx(75.0)
    assert mg.stored_threshold(0.5, 0.01) == pytest.approx(50.0)
    assert mg.stored_threshold(0.75, None) == pytest.approx(0.75)


def test_the_threshold_is_applied_to_the_stored_uint8_not_the_float(tmp_path):
    """The test that fails if the scale_factor conversion is dropped.

    Stored qa of 10, 50 and 100 is 0.10, 0.50 and 1.00. At a threshold of 0.75
    only the last survives. Comparing 0.75 against the raw uint8 would keep all
    three, because every stored value exceeds 0.75.
    """
    path = write_granule(named(tmp_path),
                         lat=[0.75, 0.75, 0.75], lon=[0.25, 0.25, 0.25],
                         primary=[1000.0, 2000.0, 3000.0],
                         qa_stored=[10, 50, 100])
    composite = grid_granules([path], TOY, qa_threshold=0.75)
    mean, count = composite.grids(mg.PRIMARY)
    assert count[0, 0] == 1
    assert mean[0, 0] == pytest.approx(3000.0)


def test_a_lower_threshold_keeps_more(tmp_path):
    path = write_granule(named(tmp_path),
                         lat=[0.75, 0.75, 0.75], lon=[0.25, 0.25, 0.25],
                         primary=[1000.0, 2000.0, 3000.0],
                         qa_stored=[10, 50, 100])
    assert grid_granules([path], TOY, qa_threshold=0.5).counts[0, 0] == 2
    assert grid_granules([path], TOY, qa_threshold=0.05).counts[0, 0] == 3


def test_the_qa_fill_value_is_excluded(tmp_path):
    path = write_granule(named(tmp_path),
                         lat=[0.75, 0.75], lon=[0.25, 0.25],
                         primary=[1900.0, 2000.0],
                         qa_stored=[100, 255])         # 255 is the qa _FillValue
    assert grid_granules([path], TOY).counts[0, 0] == 1


# --------------------------------------------------------------------------
# fill values, read from the attribute
# --------------------------------------------------------------------------

def test_the_methane_fill_value_is_excluded_and_read_from_the_attribute(tmp_path):
    path = write_granule(named(tmp_path),
                         lat=[0.75, 0.75], lon=[0.25, 0.25],
                         primary=[1900.0, FILL],
                         qa_stored=[100, 100])
    mean, count = grid_granules([path], TOY).grids(mg.PRIMARY)
    assert count[0, 0] == 1
    assert mean[0, 0] == pytest.approx(1900.0)


def test_a_granule_with_a_different_fill_value_is_still_handled(tmp_path):
    """Nothing assumes a sentinel; the attribute is what is used."""
    odd = -12345.0
    path = write_granule(named(tmp_path),
                         lat=[0.75, 0.75], lon=[0.25, 0.25],
                         primary=[1900.0, odd],
                         qa_stored=[100, 100], value_fill=odd)
    mean, count = grid_granules([path], TOY).grids(mg.PRIMARY)
    assert count[0, 0] == 1
    assert mean[0, 0] == pytest.approx(1900.0)


def test_the_latitude_fill_value_is_excluded(tmp_path):
    path = write_granule(named(tmp_path),
                         lat=[0.75, -999.0], lon=[0.25, 0.25],
                         primary=[1900.0, 1900.0],
                         qa_stored=[100, 100], lat_fill=-999.0)
    assert grid_granules([path], TOY).counts.sum() == 1


# --------------------------------------------------------------------------
# empty cells
# --------------------------------------------------------------------------

def test_a_cell_with_no_soundings_is_nan_and_not_zero(tmp_path):
    """The distinction this module exists to preserve."""
    path = write_granule(named(tmp_path), lat=[0.75], lon=[0.25],
                         primary=[1900.0], qa_stored=[100])
    mean, count = grid_granules([path], TOY).grids(mg.PRIMARY)
    assert count[0, 0] == 1 and np.isfinite(mean[0, 0])
    for cell in ((0, 1), (1, 0), (1, 1)):
        assert count[cell] == 0
        assert np.isnan(mean[cell]), "an unobserved cell must not read as zero"
    assert not (mean == 0).any()


def test_a_granule_with_nothing_in_the_box_yields_an_all_nan_grid(tmp_path):
    path = write_granule(named(tmp_path), lat=[50.0], lon=[50.0],
                         primary=[1900.0], qa_stored=[100])
    composite = grid_granules([path], TOY)
    mean, count = composite.grids(mg.PRIMARY)
    assert count.sum() == 0
    assert np.isnan(mean).all()


# --------------------------------------------------------------------------
# both variables
# --------------------------------------------------------------------------

def test_both_methane_variables_are_carried_separately(tmp_path):
    path = write_granule(named(tmp_path), lat=[0.75], lon=[0.25],
                         primary=[1900.0], secondary=[1850.0], qa_stored=[100])
    composite = grid_granules([path], TOY)
    assert composite.variables == sorted([mg.PRIMARY, mg.SECONDARY])
    assert composite.mean_of(mg.PRIMARY)[0, 0] == pytest.approx(1900.0)
    assert composite.mean_of(mg.SECONDARY)[0, 0] == pytest.approx(1850.0)


def test_asking_for_a_variable_that_was_not_gridded_raises(tmp_path):
    path = write_granule(named(tmp_path), lat=[0.75], lon=[0.25],
                         primary=[1900.0], qa_stored=[100])
    composite = grid_granules([path], TOY, variables=(mg.PRIMARY,))
    with pytest.raises(KeyError):
        composite.mean_of(mg.SECONDARY)


# --------------------------------------------------------------------------
# provenance and coverage
# --------------------------------------------------------------------------

def test_per_granule_provenance_is_preserved(tmp_path):
    path = write_granule(named(tmp_path),
                         lat=[0.75, 0.75, 50.0], lon=[0.25, 0.25, 50.0],
                         primary=[1900.0, 2000.0, 1900.0],
                         qa_stored=[100, 10, 100])
    composite = grid_granules([path], TOY, qa_threshold=0.75)
    assert len(composite.contributions) == 1
    contribution = composite.contributions[0]
    assert contribution.soundings_read == 3
    assert contribution.soundings_valid == 2       # the low-qa one is dropped
    assert contribution.soundings_in_box == 1      # and one is outside the box
    assert contribution.acquired == datetime(2018, 5, 14, 4, 21, 47)
    assert contribution.year == 2018
    assert "granule" in contribution.as_dict()


def test_coverage_reports_fraction_median_max_and_years(tmp_path):
    a = write_granule(
        tmp_path / "S5P_RPRO_L2__CH4____20180514T042147_20180514T060317"
                   "_03019_03_020400_20221109T092730.nc",
        lat=[0.75, 0.75, 0.25], lon=[0.25, 0.25, 0.25],
        primary=[1900.0] * 3, qa_stored=[100] * 3)
    b = write_granule(
        tmp_path / "S5P_RPRO_L2__CH4____20200514T042147_20200514T060317"
                   "_13019_03_020400_20221109T092730.nc",
        lat=[50.0], lon=[50.0], primary=[1900.0], qa_stored=[100])
    composite = grid_granules([a, b], TOY)
    coverage = coverage_of(composite)
    assert coverage.n_cells == 4
    assert coverage.covered_cells == 2
    assert coverage.fraction == pytest.approx(0.5)
    assert coverage.max_per_covered_cell == 2
    assert coverage.median_per_covered_cell == pytest.approx(1.5)
    assert coverage.soundings_by_year == {2018: 3, 2020: 0}
    assert coverage.contributing_granules == 1
    assert coverage.empty_granules == 1
    assert "soundings_by_year" in coverage.as_dict()


def test_coverage_of_an_empty_composite_is_zero_not_an_error(tmp_path):
    path = write_granule(named(tmp_path), lat=[50.0], lon=[50.0],
                         primary=[1900.0], qa_stored=[100])
    coverage = coverage_of(grid_granules([path], TOY))
    assert coverage.covered_cells == 0
    assert coverage.fraction == 0.0
    assert coverage.max_per_covered_cell == 0


def test_a_mean_cannot_be_had_without_its_count(tmp_path):
    """Structural, not a message: grids() returns the pair together."""
    path = write_granule(named(tmp_path), lat=[0.75], lon=[0.25],
                         primary=[1900.0], qa_stored=[100])
    composite = grid_granules([path], TOY)
    result = composite.grids(mg.PRIMARY)
    assert isinstance(result, tuple) and len(result) == 2
    assert hasattr(composite, "counts")
    assert composite.counts.shape == composite.mean_of(mg.PRIMARY).shape


def test_read_soundings_returns_the_filtered_soundings_and_a_contribution(tmp_path):
    path = write_granule(named(tmp_path),
                         lat=[0.75, 0.75], lon=[0.25, 0.25],
                         primary=[1900.0, 2000.0], qa_stored=[100, 10])
    soundings, contribution = read_soundings(path, TOY, qa_threshold=0.75)
    assert len(soundings) == 1
    assert soundings.values[mg.PRIMARY][0] == pytest.approx(1900.0)
    assert soundings.qa_stored[0] == 100
    assert contribution.soundings_read == 2


def test_a_granule_without_a_product_group_raises(tmp_path):
    import netCDF4
    path = tmp_path / "flat.nc"
    with netCDF4.Dataset(path, "w", format="NETCDF4") as ds:
        ds.createDimension("x", 1)
    with pytest.raises(mg.MissingVariable, match="PRODUCT"):
        read_soundings(path, TOY)
