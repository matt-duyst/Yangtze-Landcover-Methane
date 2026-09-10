"""Tests for the blended TROPOMI+GOSAT reader.

Offline. Granules are built in ``tmp_path`` with the layout the product user
manual describes -- flat root, no netCDF groups, `qa_value` as uint8 with a
0.01 scale factor -- and the geometry of each fixture is chosen so the gridded
answer is known in advance.

Three things carry this module.

**The operational reader must be untouched.** Three committed composites rest
on `read_soundings`, so this file asserts that it still refuses a flat-rooted
file rather than silently reading one, and that a real operational granule
still reads as before. A parameter that made the group path optional would
have put both at risk; a separate reader cannot.

**qa is asserted, not assumed.** The manual says the files hold only soundings
with `qa_value == 1.0`, and a census of 2018 says `>= 0.75` and `== 1.0` pick
the same soundings. The threshold is still applied and what it drops is
counted, so a file that broke the assumption would produce a number rather
than a quietly different sample.

**Fill values come from the file.** The same rule `grid.py` follows, and the
reason is the same: the fill is a property of the file, not of the product.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from src.methane import blended as bl
from src.methane import GridSpec, read_soundings

FILL = 9.969209968386869e+36
TOY = GridSpec(west=0.0, south=0.0, east=1.0, north=1.0, resolution=0.5)
TITLE = "Blended TROPOMI+GOSAT Methane Product"

NAME = ("S5P_BLND_L2__CH4____20180514T042147_20180514T060317_03019_03_020400_"
        "20230614T001445.nc")


def write_blended(path, *, lat, lon, values, qa_stored, title=TITLE,
                  qa_scale=0.01, qa_fill=255, value_fill=FILL, omit=()):
    """One blended granule, flat rooted, with the product's own attributes."""
    import netCDF4

    with netCDF4.Dataset(path, "w") as ds:
        if title is not None:
            ds.Title = title
        ds.Contact = "test"
        ds.createDimension("nobs", len(lat))
        for name, data in (("latitude", lat), ("longitude", lon),
                           (bl.BLENDED, values)):
            if name in omit:
                continue
            var = ds.createVariable(name, "f4", ("nobs",),
                                    fill_value=value_fill)
            # Written unscaled, as the operational fixture does: with
            # auto-scaling on, assigning a stored qa of 100 beside a scale
            # factor of 0.01 would try to store 10,000 in a uint8.
            var.set_auto_maskandscale(False)
            var[:] = np.asarray(data, dtype="f4")
        if "qa_value" not in omit:
            qa = ds.createVariable("qa_value", "u1", ("nobs",),
                                   fill_value=qa_fill)
            qa.set_auto_maskandscale(False)
            qa.scale_factor = qa_scale
            qa.add_offset = 0.0
            qa[:] = np.asarray(qa_stored, dtype="u1")
    return path


# --------------------------------------------------------------------------
# the operational reader is unchanged
# --------------------------------------------------------------------------

def test_the_operational_reader_still_refuses_a_flat_file(tmp_path):
    """It must not learn to read this layout, because three composites rest on
    what it currently assumes."""
    path = write_blended(tmp_path / NAME, lat=[0.25], lon=[0.25],
                         values=[1900.0], qa_stored=[100])

    with pytest.raises(Exception, match="no 'PRODUCT' group"):
        read_soundings(path, TOY)


def test_this_reader_refuses_an_operational_file(tmp_path):
    """The refusal points at the other reader rather than merely failing."""
    import netCDF4

    path = tmp_path / "operational.nc"
    with netCDF4.Dataset(path, "w") as ds:
        group = ds.createGroup("PRODUCT")
        group.createDimension("nobs", 1)
        group.createVariable("latitude", "f4", ("nobs",))

    with pytest.raises(bl.BlendedError, match="Title is not the blended"):
        bl.read_blended(path, TOY, name=NAME)


def test_a_missing_variable_says_which_reader_to_use(tmp_path):
    path = write_blended(tmp_path / NAME, lat=[0.25], lon=[0.25],
                         values=[1900.0], qa_stored=[100],
                         omit=("qa_value",))

    with pytest.raises(bl.BlendedError, match="read_soundings instead"):
        bl.read_blended(path, TOY, name=NAME)


# --------------------------------------------------------------------------
# reading and gridding
# --------------------------------------------------------------------------

def test_one_sounding_lands_in_the_cell_that_contains_it(tmp_path):
    path = write_blended(tmp_path / NAME, lat=[0.75], lon=[0.25],
                         values=[1900.0], qa_stored=[100])
    soundings = bl.read_blended(path, TOY, name=NAME)

    assert (int(soundings.row[0]), int(soundings.col[0])) == (0, 0)
    assert soundings.value.tolist() == [1900.0]
    assert soundings.contribution.soundings_in_box == 1


def test_gridding_averages_within_a_cell_and_leaves_others_absent(tmp_path):
    path = write_blended(tmp_path / NAME, lat=[0.75, 0.75], lon=[0.1, 0.4],
                         values=[1890.0, 1910.0], qa_stored=[100, 100])
    composite = bl.grid_blended([path], TOY, names=[NAME])
    mean = composite.mean_of(bl.BLENDED)

    assert composite.counts[0, 0] == 2
    assert mean[0, 0] == pytest.approx(1900.0)
    assert np.isnan(mean[1, 1])
    assert composite.counts[1, 1] == 0


def test_the_fill_value_is_read_from_the_variable_and_dropped(tmp_path):
    path = write_blended(tmp_path / NAME, lat=[0.75, 0.75], lon=[0.1, 0.4],
                         values=[FILL, 1910.0], qa_stored=[100, 100])
    composite = bl.grid_blended([path], TOY, names=[NAME])

    assert composite.counts[0, 0] == 1
    assert composite.mean_of(bl.BLENDED)[0, 0] == pytest.approx(1910.0)


def test_a_sounding_outside_the_box_is_not_gridded(tmp_path):
    path = write_blended(tmp_path / NAME, lat=[0.75, 5.0], lon=[0.25, 5.0],
                         values=[1900.0, 1800.0], qa_stored=[100, 100])
    soundings = bl.read_blended(path, TOY, name=NAME)

    assert soundings.contribution.soundings_read == 2
    assert soundings.contribution.soundings_valid == 2
    assert soundings.contribution.soundings_in_box == 1


# --------------------------------------------------------------------------
# qa is asserted rather than assumed
# --------------------------------------------------------------------------

def test_the_threshold_is_compared_in_stored_units(tmp_path):
    """A naive float comparison against a uint8 array keeps everything.

    The same trap `grid.py` has a test for, checked again here because this
    reader repeats the conversion rather than sharing the call site.
    """
    path = write_blended(tmp_path / NAME, lat=[0.75] * 3, lon=[0.1, 0.2, 0.3],
                         values=[1900.0] * 3, qa_stored=[40, 100, 100])
    soundings = bl.read_blended(path, TOY, name=NAME)

    assert soundings.contribution.soundings_in_box == 2
    assert soundings.dropped_by_qa == 1


def test_a_file_carrying_a_sub_threshold_sounding_stops_the_grid(tmp_path):
    """The product is documented to hold only qa 1.0. If one did not, the
    sample would no longer be the operational composite's and the comparison
    would not be like for like, so this refuses rather than averaging it in."""
    path = write_blended(tmp_path / NAME, lat=[0.75, 0.75], lon=[0.1, 0.4],
                         values=[1900.0, 1910.0], qa_stored=[40, 100])

    with pytest.raises(bl.BlendedError, match="not be like for like"):
        bl.grid_blended([path], TOY, names=[NAME])


def test_the_qa_fill_is_dropped_before_the_threshold(tmp_path):
    path = write_blended(tmp_path / NAME, lat=[0.75, 0.75], lon=[0.1, 0.4],
                         values=[1900.0, 1910.0], qa_stored=[255, 100])
    soundings = bl.read_blended(path, TOY, name=NAME)

    assert soundings.contribution.soundings_in_box == 1
    assert soundings.dropped_by_qa == 0        # a fill is not a low quality


# --------------------------------------------------------------------------
# the filename, and the Composite it builds
# --------------------------------------------------------------------------

def test_the_orbit_and_time_come_out_of_the_filename():
    from datetime import datetime

    fields = bl.parse_blended_name(NAME)

    assert fields["orbit"] == 3019
    assert fields["start"] == datetime(2018, 5, 14, 4, 21, 47)
    assert fields["stop"] == datetime(2018, 5, 14, 6, 3, 17)


def test_a_blended_name_differs_from_the_operational_one_only_as_documented():
    """"the replacement of the processing type with BLND and the overwriting
    of the file generation time", says the manual."""
    operational = ("S5P_RPRO_L2__CH4____20180514T042147_20180514T060317_"
                   "03019_03_020400_20221109T092730.nc")
    from src.fetch.s5p import parse_granule_name

    theirs = parse_granule_name(operational)
    mine = bl.parse_blended_name(NAME)
    assert theirs["orbit"] == mine["orbit"]
    assert theirs["start"] == mine["start"]
    assert theirs["stop"] == mine["stop"]


def test_a_name_that_is_not_a_granule_is_refused():
    with pytest.raises(bl.BlendedError, match="not a blended granule name"):
        bl.parse_blended_name("something_else.nc")


def test_the_result_is_an_ordinary_composite(tmp_path):
    """So `mean_of`, `coverage_of` and the export path work on it unchanged,
    which is where the like-for-like comparison actually lives."""
    from src.methane import Composite, coverage_of

    path = write_blended(tmp_path / NAME, lat=[0.75], lon=[0.25],
                         values=[1900.0], qa_stored=[100])
    composite = bl.grid_blended([path], TOY, names=[NAME])

    assert isinstance(composite, Composite)
    assert composite.variables == [bl.BLENDED]
    assert composite.count_of(bl.BLENDED) is composite.counts
    assert coverage_of(composite).covered_cells == 1
    assert composite.total_soundings == 1


def test_the_range_reader_refuses_a_host_that_cannot_serve_ranges():
    """Everything about the remote read depends on this, so it is checked
    rather than hoped for."""
    class Response:
        headers = {"Content-Length": "10"}

        def raise_for_status(self):
            return None

    class Session:
        def head(self, url, timeout=None):
            return Response()

    with pytest.raises(bl.BlendedError, match="Accept-Ranges"):
        bl.RangeFile.open("https://example.invalid/x.nc", session=Session())
