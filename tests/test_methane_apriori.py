"""Tests for the a priori column computation.

Offline. Synthetic profiles with a known answer, plus one test against the
retained granule that skips when it is absent, so the suite still runs on a
clone with nothing fetched.

The cases that carry weight are the ones where a wrong answer would still look
plausible: a fill value that survives into a sum, a partial profile given a
partial sum instead of being excluded, and a layer axis silently in the wrong
order. The last cannot break this computation, because a ratio of sums does not
care about order, and there is a test asserting exactly that so nobody adds a
per-layer step assuming the same protection.
"""

from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
import pytest

from src.methane import apriori as ap
from src.methane.apriori import (
    AprioriError,
    ProfileShapeMismatch,
    column_apriori,
    departure,
    surface_first,
)

FILL = 9.96921e+36
REPO = Path(__file__).resolve().parents[1]


def profiles(ch4_per_layer, air_per_layer, soundings=1, layers=12):
    ch4 = np.full((soundings, layers), ch4_per_layer, dtype="float64")
    air = np.full((soundings, layers), air_per_layer, dtype="float64")
    return ch4, air


# --------------------------------------------------------------------------
# the arithmetic
# --------------------------------------------------------------------------

def test_a_known_ratio_gives_a_known_column():
    """1.8e-6 mol CH4 per mol dry air is 1800 ppb, however it is split."""
    ch4, air = profiles(1.8e-6, 1.0)
    got = column_apriori(ch4, air)
    assert got.values[0] == pytest.approx(1800.0)
    assert got.valid.all() and got.excluded == 0 and got.layers == 12


def test_the_column_is_the_ratio_of_sums_not_the_mean_of_ratios():
    """A layer with more air must pull the column mean toward its own value."""
    ch4 = np.array([[1.0, 9.0]])
    air = np.array([[1.0e6, 9.0e6]])
    got = column_apriori(ch4, air)
    ratio_of_sums = 10.0 / 1.0e7 * 1e9
    mean_of_ratios = np.mean([1.0 / 1.0e6, 9.0 / 9.0e6]) * 1e9
    assert got.values[0] == pytest.approx(ratio_of_sums)
    assert ratio_of_sums == pytest.approx(1000.0)
    assert mean_of_ratios == pytest.approx(1000.0)   # equal here by construction

    ch4 = np.array([[1.0, 1.0]])
    air = np.array([[1.0e6, 9.0e6]])
    got = column_apriori(ch4, air)
    assert got.values[0] == pytest.approx(2.0 / 1.0e7 * 1e9)
    assert got.values[0] != pytest.approx(
        np.mean([1.0 / 1.0e6, 1.0 / 9.0e6]) * 1e9), "weighting must matter"


def test_several_soundings_are_computed_independently():
    ch4 = np.array([[1.8e-6] * 4, [1.9e-6] * 4])
    air = np.ones((2, 4))
    got = column_apriori(ch4, air)
    assert got.values == pytest.approx([1800.0, 1900.0])
    assert got.n == 2


# --------------------------------------------------------------------------
# layer order
# --------------------------------------------------------------------------

def test_the_column_is_invariant_to_layer_order():
    """Why this computation is safe against the file's top-first storage."""
    rng = np.random.default_rng(0)
    ch4 = rng.uniform(1e-7, 1e-6, (5, 12))
    air = rng.uniform(1e4, 1e5, (5, 12))
    forward = column_apriori(ch4, air).values
    reversed_ = column_apriori(ch4[:, ::-1], air[:, ::-1]).values
    assert forward == pytest.approx(reversed_, rel=1e-12)


def test_surface_first_reverses_the_layer_axis():
    """The helper a per-layer operation would need, which is not order-safe."""
    profile = np.arange(24, dtype="float64").reshape(2, 12)
    flipped = surface_first(profile)
    assert flipped[0, 0] == 11.0 and flipped[0, -1] == 0.0
    assert np.array_equal(surface_first(flipped), profile)


# --------------------------------------------------------------------------
# fill handling
# --------------------------------------------------------------------------

def test_a_fill_in_any_layer_excludes_the_whole_sounding():
    ch4 = np.array([[1.8e-6] * 12, [1.8e-6] * 12])
    ch4[1, 5] = FILL
    air = np.ones((2, 12))
    got = column_apriori(ch4, air, methane_fill=FILL)
    assert got.valid.tolist() == [True, False]
    assert np.isnan(got.values[1])
    assert got.excluded == 1 and got.partial == 1


def test_a_fill_in_the_dry_air_profile_also_excludes():
    ch4 = np.full((2, 12), 1.8e-6)
    air = np.ones((2, 12))
    air[0, 0] = FILL
    got = column_apriori(ch4, air, dry_air_fill=FILL)
    assert got.valid.tolist() == [False, True]
    assert got.excluded == 1


def test_a_wholly_filled_sounding_is_excluded_but_not_counted_as_partial():
    ch4 = np.full((2, 12), 1.8e-6)
    ch4[0, :] = FILL
    got = column_apriori(ch4, np.ones((2, 12)), methane_fill=FILL)
    assert got.excluded == 1 and got.partial == 0


def test_a_partial_profile_never_produces_a_partial_sum():
    """The failure that would look plausible: a column from eleven layers."""
    ch4 = np.full((1, 12), 1.8e-6)
    ch4[0, 3] = FILL
    got = column_apriori(ch4, np.ones((1, 12)), methane_fill=FILL)
    assert np.isnan(got.values[0])
    partial = (1.8e-6 * 11) / 12 * 1e9
    assert not np.isclose(np.nan_to_num(got.values[0]), partial)


def test_a_fill_that_is_not_declared_still_fails_the_finiteness_check():
    ch4 = np.full((1, 12), 1.8e-6)
    ch4[0, 2] = np.nan
    got = column_apriori(ch4, np.ones((1, 12)))
    assert not got.valid[0] and got.excluded == 1


def test_zero_dry_air_does_not_divide():
    got = column_apriori(np.full((1, 4), 1e-6), np.zeros((1, 4)))
    assert not got.valid[0] and np.isnan(got.values[0])


def test_mismatched_profiles_are_refused():
    with pytest.raises(ProfileShapeMismatch, match="same soundings"):
        column_apriori(np.ones((2, 12)), np.ones((2, 11)))


# --------------------------------------------------------------------------
# the departure
# --------------------------------------------------------------------------

def test_the_departure_is_retrieved_minus_prior_where_both_exist():
    ch4 = np.full((3, 4), 1.8e-6)
    ch4[2, 0] = FILL
    prior = column_apriori(ch4, np.ones((3, 4)), methane_fill=FILL)
    retrieved = np.array([1900.0, 1850.0, 1875.0])
    got = departure(retrieved, prior)
    assert got[0] == pytest.approx(100.0)
    assert got[1] == pytest.approx(50.0)
    assert np.isnan(got[2]), "no prior means no departure, not a bare retrieval"


def test_the_departure_refuses_a_mismatched_retrieval():
    prior = column_apriori(np.ones((2, 4)) * 1e-6, np.ones((2, 4)))
    with pytest.raises(ProfileShapeMismatch):
        departure(np.array([1900.0]), prior)


# --------------------------------------------------------------------------
# the real granule, when it is present
# --------------------------------------------------------------------------

def granule():
    found = glob.glob(str(REPO / "data" / "raw" / "s5p" / "*.nc"))
    return found[0] if found else None


@pytest.mark.skipif(granule() is None, reason="no granule fetched")
def test_the_retained_granule_gives_a_plausible_methane_column():
    got = ap.from_granule(granule())
    summary = got.summary()
    assert summary["layers"] == 12
    assert 1700.0 < summary["mean_ppb"] < 1950.0, "a plausible methane column"
    assert summary["with_apriori"] > 0
    assert summary["partial_profiles"] == 0, \
        "on this granule a profile is either whole or wholly absent"
    assert summary["with_apriori"] + summary["excluded_for_fill"] == \
        summary["soundings"]


@pytest.mark.skipif(granule() is None, reason="no granule fetched")
def test_a_missing_variable_is_reported_by_name(tmp_path):
    import netCDF4

    path = tmp_path / "empty.nc"
    with netCDF4.Dataset(path, "w") as ds:
        ds.createGroup("PRODUCT").createGroup("SUPPORT_DATA").createGroup("INPUT_DATA")
    with pytest.raises(AprioriError, match="methane_profile_apriori"):
        ap.from_granule(path)
