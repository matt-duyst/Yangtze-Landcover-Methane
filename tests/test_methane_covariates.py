"""Tests for gridding support-data covariates alongside methane.

Offline. Granules are written in ``tmp_path`` with the real three-level group
structure -- PRODUCT, then SUPPORT_DATA, then INPUT_DATA, DETAILED_RESULTS and
GEOLOCATIONS -- because the thing most likely to go wrong is looking for a
variable in the wrong group and quietly finding nothing.

The property that carries the most weight is that covariates do not gate. Only
about 3 percent of in-box soundings carry a valid albedo, so if albedo joined
the validity mask the methane composite would lose almost all of itself. Two
tests pin that from opposite directions: the methane result is identical with
and without covariates requested, and a covariate's count is its own rather
than methane's.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.methane import grid as mg
from src.methane.grid import (
    CovariateSpec,
    GridSpec,
    MissingVariable,
    grid_granules,
    open_group,
    read_soundings,
)

netCDF4 = pytest.importorskip("netCDF4")

TOY = GridSpec(west=0.0, south=0.0, east=1.0, north=1.0, resolution=0.5)

METHANE_FILL = 9.969209968386869e+36
ALBEDO_FILL = 9.969209968386869e+36

#: Where each covariate really lives in a TROPOMI L2 CH4 granule.
GROUPS = {
    "eastward_wind": "PRODUCT/SUPPORT_DATA/INPUT_DATA",
    "northward_wind": "PRODUCT/SUPPORT_DATA/INPUT_DATA",
    "surface_altitude": "PRODUCT/SUPPORT_DATA/INPUT_DATA",
    "surface_pressure": "PRODUCT/SUPPORT_DATA/INPUT_DATA",
    "surface_albedo_SWIR": "PRODUCT/SUPPORT_DATA/DETAILED_RESULTS",
    "surface_albedo_NIR": "PRODUCT/SUPPORT_DATA/DETAILED_RESULTS",
    "solar_zenith_angle": "PRODUCT/SUPPORT_DATA/GEOLOCATIONS",
}


def specs(*names):
    return tuple(CovariateSpec(name=n, group=GROUPS[n]) for n in names)


def write_granule(path, *, lat, lon, methane, qa=None, covariates=None,
                  omit=(), fills=None):
    """A granule with PRODUCT and the three real support subgroups.

    ``covariates`` maps a name to its per-sounding values; anything in ``omit``
    is left out of the file entirely. ``fills`` overrides a variable's
    ``_FillValue`` so a test can give a covariate a different one from methane.
    """
    lat = np.asarray(lat, "float64")
    n = lat.size
    qa = np.full(n, 100, "uint8") if qa is None else np.asarray(qa, "uint8")
    covariates = dict(covariates or {})
    fills = dict(fills or {})

    with netCDF4.Dataset(path, "w") as ds:
        product = ds.createGroup("PRODUCT")
        product.createDimension("time", 1)
        product.createDimension("scanline", 1)
        product.createDimension("ground_pixel", n)
        dims = ("time", "scanline", "ground_pixel")

        def put(group, name, values, dtype, fill):
            var = group.createVariable(name, dtype, dims, fill_value=fill)
            var.set_auto_maskandscale(False)
            var[:] = np.asarray(values).reshape(1, 1, n)
            return var

        put(product, "latitude", lat, "f8", -999.0)
        put(product, "longitude", lon, "f8", -999.0)
        qa_var = put(product, "qa_value", qa, "u1", 255)
        qa_var.scale_factor = 0.01
        for name in (mg.PRIMARY, mg.SECONDARY):
            put(product, name, methane, "f8", METHANE_FILL)

        support = product.createGroup("SUPPORT_DATA")
        subgroups = {name: support.createGroup(name)
                     for name in ("INPUT_DATA", "DETAILED_RESULTS", "GEOLOCATIONS")}
        for name, values in covariates.items():
            if name in omit:
                continue
            leaf = GROUPS[name].rsplit("/", 1)[1]
            put(subgroups[leaf], name, values, "f8",
                fills.get(name, ALBEDO_FILL))
    return path


#: Four soundings, one per cell. Row 0 is the NORTHERNMOST row, so latitude
#: 0.75 is row 0 and 0.25 is row 1; the four land in cells (1,0) (1,1) (0,0)
#: (0,1) in that order.
CELLS = ((1, 0), (1, 1), (0, 0), (0, 1))


def simple(tmp_path, name="g.nc", **kwargs):
    lat = kwargs.pop("lat", [0.25, 0.25, 0.75, 0.75])
    lon = kwargs.pop("lon", [0.25, 0.75, 0.25, 0.75])
    methane = kwargs.pop("methane", [1900.0, 1910.0, 1920.0, 1930.0])
    return write_granule(tmp_path / name, lat=lat, lon=lon, methane=methane,
                         **kwargs)


# --------------------------------------------------------------------------
# finding a variable in a subgroup
# --------------------------------------------------------------------------

def test_a_covariate_in_a_subgroup_is_found_and_gridded(tmp_path):
    path = simple(tmp_path, covariates={"eastward_wind": [1.0, 2.0, 3.0, 4.0]})
    composite = grid_granules([path], TOY, covariates=specs("eastward_wind"))
    mean, count = composite.grids("eastward_wind")
    assert composite.covariates == ["eastward_wind"]
    assert count.sum() == 4
    assert mean[CELLS[0]] == pytest.approx(1.0)
    assert mean[CELLS[3]] == pytest.approx(4.0)


def test_covariates_are_found_across_all_three_subgroups(tmp_path):
    values = [1.0, 2.0, 3.0, 4.0]
    names = ("eastward_wind", "surface_albedo_SWIR", "solar_zenith_angle")
    path = simple(tmp_path, covariates={n: values for n in names})
    composite = grid_granules([path], TOY, covariates=specs(*names))
    assert composite.covariates == sorted(names)
    for name in names:
        assert composite.count_of(name).sum() == 4


def test_open_group_says_where_the_path_stopped(tmp_path):
    path = simple(tmp_path, covariates={"eastward_wind": [1.0, 2.0, 3.0, 4.0]})
    with netCDF4.Dataset(path, "r") as ds:
        assert open_group(ds, ("PRODUCT", "SUPPORT_DATA", "INPUT_DATA")) is not None
        with pytest.raises(MissingVariable, match="NOT_A_GROUP"):
            open_group(ds, ("PRODUCT", "SUPPORT_DATA", "NOT_A_GROUP"))


# --------------------------------------------------------------------------
# each variable's own fill value
# --------------------------------------------------------------------------

def test_a_covariate_uses_its_own_fill_value_not_methanes(tmp_path):
    """The albedo fill here is 0, which is a perfectly good methane value."""
    path = simple(
        tmp_path,
        covariates={"surface_albedo_SWIR": [0.10, 0.0, 0.30, 0.40]},
        fills={"surface_albedo_SWIR": 0.0})
    composite = grid_granules([path], TOY,
                              covariates=specs("surface_albedo_SWIR"))
    mean, count = composite.grids("surface_albedo_SWIR")
    assert count.sum() == 3, "the sounding holding the albedo fill is not counted"
    assert np.isnan(mean[CELLS[1]]), "and its cell has no albedo at all"
    assert composite.counts.sum() == 4, "while methane keeps all four soundings"


def test_a_covariate_fill_does_not_remove_the_sounding_from_methane(tmp_path):
    path = simple(
        tmp_path,
        covariates={"surface_albedo_SWIR": [0.1, ALBEDO_FILL, ALBEDO_FILL,
                                            ALBEDO_FILL]})
    with_covariates = grid_granules([path], TOY,
                                    covariates=specs("surface_albedo_SWIR"))
    without = grid_granules([path], TOY)
    assert with_covariates.counts.tolist() == without.counts.tolist()
    assert np.allclose(with_covariates.mean_of(mg.PRIMARY),
                       without.mean_of(mg.PRIMARY), equal_nan=True)
    assert with_covariates.count_of("surface_albedo_SWIR").sum() == 1


def test_methane_fill_still_removes_the_sounding(tmp_path):
    path = simple(tmp_path, methane=[1900.0, METHANE_FILL, 1920.0, 1930.0],
                  covariates={"eastward_wind": [1.0, 2.0, 3.0, 4.0]})
    composite = grid_granules([path], TOY, covariates=specs("eastward_wind"))
    assert composite.counts.sum() == 3
    assert composite.count_of("eastward_wind").sum() == 3, \
        "the covariate is read on the soundings methane kept, not on all of them"


# --------------------------------------------------------------------------
# per-variable counts
# --------------------------------------------------------------------------

def test_per_variable_counts_differ_where_validity_differs(tmp_path):
    """Albedo valid on one sounding, wind on three, methane on all four."""
    path = simple(
        tmp_path,
        covariates={
            "surface_albedo_SWIR": [0.11, ALBEDO_FILL, ALBEDO_FILL, ALBEDO_FILL],
            "eastward_wind": [1.0, 2.0, 3.0, ALBEDO_FILL],
        })
    composite = grid_granules(
        [path], TOY, covariates=specs("surface_albedo_SWIR", "eastward_wind"))
    assert int(composite.counts.sum()) == 4
    assert int(composite.count_of("eastward_wind").sum()) == 3
    assert int(composite.count_of("surface_albedo_SWIR").sum()) == 1
    assert composite.count_of("surface_albedo_SWIR").tolist() \
        != composite.counts.tolist()


def test_a_covariate_mean_divides_by_its_own_count(tmp_path):
    """Two soundings in one cell, only one with albedo: the mean is that one."""
    path = write_granule(
        tmp_path / "g.nc", lat=[0.25, 0.26], lon=[0.25, 0.26],
        methane=[1900.0, 1950.0],
        covariates={"surface_albedo_SWIR": [0.20, ALBEDO_FILL]})
    composite = grid_granules([path], TOY,
                              covariates=specs("surface_albedo_SWIR"))
    cell = (1, 0)                                  # latitude 0.25 is the south row
    assert composite.counts[cell] == 2
    assert composite.mean_of(mg.PRIMARY)[cell] == pytest.approx(1925.0)
    assert composite.count_of("surface_albedo_SWIR")[cell] == 1
    assert composite.mean_of("surface_albedo_SWIR")[cell] == pytest.approx(0.20), \
        "dividing the albedo sum by the methane count would give 0.10"


# --------------------------------------------------------------------------
# a mean is never separable from its count
# --------------------------------------------------------------------------

def test_a_mean_is_unreachable_without_its_count_for_every_variable(tmp_path):
    path = simple(
        tmp_path,
        covariates={"surface_albedo_SWIR": [0.11, ALBEDO_FILL, ALBEDO_FILL, 0.4]})
    composite = grid_granules([path], TOY,
                              covariates=specs("surface_albedo_SWIR"))
    for name in composite.all_variables:
        mean, count = composite.grids(name)
        assert mean.shape == count.shape
        assert np.isnan(mean[count == 0]).all(), f"{name} claims a value with no count"
        assert np.isfinite(mean[count > 0]).all()


def test_an_unobserved_covariate_cell_is_nan_and_not_zero(tmp_path):
    path = simple(tmp_path,
                  covariates={"surface_albedo_SWIR": [ALBEDO_FILL] * 4})
    composite = grid_granules([path], TOY,
                              covariates=specs("surface_albedo_SWIR"))
    mean = composite.mean_of("surface_albedo_SWIR")
    assert np.isnan(mean).all(), "no albedo anywhere is not albedo of zero"
    assert int(composite.counts.sum()) == 4, "methane is untouched"


def test_asking_for_an_unknown_variable_names_what_is_available(tmp_path):
    path = simple(tmp_path, covariates={"eastward_wind": [1.0, 2.0, 3.0, 4.0]})
    composite = grid_granules([path], TOY, covariates=specs("eastward_wind"))
    with pytest.raises(KeyError, match="eastward_wind"):
        composite.mean_of("northward_wind")
    with pytest.raises(KeyError):
        composite.count_of("northward_wind")


# --------------------------------------------------------------------------
# a missing covariate does not fail the granule
# --------------------------------------------------------------------------

def test_a_covariate_absent_from_a_granule_is_reported_not_fatal(tmp_path):
    path = simple(tmp_path,
                  covariates={"eastward_wind": [1.0, 2.0, 3.0, 4.0]},
                  omit=("northward_wind",))
    wanted = specs("eastward_wind", "northward_wind")
    soundings, contribution = read_soundings(path, TOY, covariates=wanted)
    assert contribution.covariates_missing == ("northward_wind",)
    assert contribution.soundings_in_box == 4, "the granule is still gridded"
    assert contribution.covariates_valid == {"eastward_wind": 4}

    composite = grid_granules([path], TOY, covariates=wanted)
    assert int(composite.counts.sum()) == 4
    assert int(composite.count_of("eastward_wind").sum()) == 4
    assert int(composite.count_of("northward_wind").sum()) == 0
    assert np.isnan(composite.mean_of("northward_wind")).all()


def test_a_granule_missing_every_covariate_still_grids_methane(tmp_path):
    path = simple(tmp_path)
    wanted = specs("eastward_wind", "surface_albedo_SWIR")
    composite = grid_granules([path], TOY, covariates=wanted)
    assert int(composite.counts.sum()) == 4
    assert composite.contributions[0].covariates_missing == (
        "eastward_wind", "surface_albedo_SWIR")


def test_the_missing_list_survives_serialisation(tmp_path):
    path = simple(tmp_path, covariates={"eastward_wind": [1.0, 2.0, 3.0, 4.0]},
                  omit=("northward_wind",))
    _, contribution = read_soundings(
        path, TOY, covariates=specs("eastward_wind", "northward_wind"))
    record = contribution.as_dict()
    assert record["covariates_missing"] == ["northward_wind"]
    assert record["covariates_valid"] == {"eastward_wind": 4}


# --------------------------------------------------------------------------
# the methane result does not move
# --------------------------------------------------------------------------

def test_requesting_covariates_changes_no_methane_number(tmp_path):
    """The guarantee the whole re-run depends on."""
    rng = np.random.default_rng(0)
    lat = rng.uniform(0.01, 0.99, 40)
    lon = rng.uniform(0.01, 0.99, 40)
    methane = rng.normal(1900.0, 20.0, 40)
    albedo = np.where(rng.uniform(size=40) < 0.9, ALBEDO_FILL,
                      rng.uniform(0.05, 0.3, 40))
    path = write_granule(tmp_path / "g.nc", lat=lat, lon=lon, methane=methane,
                         covariates={"surface_albedo_SWIR": albedo,
                                     "eastward_wind": rng.normal(0, 5, 40)})
    wanted = specs("surface_albedo_SWIR", "eastward_wind")

    plain = grid_granules([path], TOY)
    loaded = grid_granules([path], TOY, covariates=wanted)

    assert plain.counts.tolist() == loaded.counts.tolist()
    for name in (mg.PRIMARY, mg.SECONDARY):
        assert np.array_equal(plain.sums[name], loaded.sums[name])
        assert np.allclose(plain.mean_of(name), loaded.mean_of(name),
                           equal_nan=True, rtol=0, atol=0)
    assert int(loaded.count_of("surface_albedo_SWIR").sum()) < int(
        loaded.counts.sum()), "albedo is valid on far fewer soundings"
