"""Tests for the two things the 2018 re-run was made to retain.

Offline, on granules written into `tmp_path`. Nothing reads `data/raw/`.

Both fields exist because a pass over the year costs 28.9 GB and about an hour,
so a quantity that is cheap to accumulate and impossible to recover afterwards
should be accumulated whether or not it is wanted yet.

**Per-granule cell sets.** The saturation record holds newly-covered and
cumulative-covered counts, which cannot answer per-granule coverage: a
newly-covered count of zero is recorded both by a granule that covered nothing
and by one that covered three hundred cells some earlier granule had already
reached. 141 of the 222 productive granules in the first 2018 run recorded
exactly zero. The cell set separates them.

**The a priori column and the departure.** Both are derived from profiles the
granule already carries, and both travel as ordinary covariates so that each
carries its own count and cannot be separated from its own denominator.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import netCDF4
import numpy as np
import pytest

from src.methane import grid as mg
from src.methane.grid import (
    APRIORI,
    DEPARTURE,
    DERIVED,
    CovariateSpec,
    GridSpec,
    read_soundings,
)

ROOT = Path(__file__).resolve().parents[1]
METHANE_FILL = 9.969209968386869e36


def load_script():
    spec = importlib.util.spec_from_file_location(
        "composite_script", ROOT / "scripts" / "compute_methane_composite.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_granule(path, *, lat, lon, methane, profile=None, dry_air=None,
                  layers=12):
    """A granule carrying the a priori profiles as well as methane."""
    lat = np.asarray(lat, "float64")
    n = lat.size
    with netCDF4.Dataset(path, "w") as ds:
        product = ds.createGroup("PRODUCT")
        product.createDimension("time", 1)
        product.createDimension("scanline", 1)
        product.createDimension("ground_pixel", n)
        product.createDimension("layer", layers)
        dims = ("time", "scanline", "ground_pixel")

        def put(group, name, values, dtype, fill, shape=dims):
            var = group.createVariable(name, dtype, shape, fill_value=fill)
            var.set_auto_maskandscale(False)
            var[:] = np.asarray(values).reshape(
                (1, 1, n) if shape == dims else (1, 1, n, layers))
            return var

        put(product, "latitude", lat, "f8", -999.0)
        put(product, "longitude", lon, "f8", -999.0)
        qa = put(product, "qa_value", np.full(n, 100, "uint8"), "u1", 255)
        qa.scale_factor = 0.01
        for name in (mg.PRIMARY, mg.SECONDARY):
            put(product, name, methane, "f8", METHANE_FILL)

        support = product.createGroup("SUPPORT_DATA")
        inputs = support.createGroup("INPUT_DATA")
        support.createGroup("DETAILED_RESULTS")
        support.createGroup("GEOLOCATIONS")
        if profile is not None:
            wide = ("time", "scanline", "ground_pixel", "layer")
            put(inputs, "methane_profile_apriori", profile, "f8",
                METHANE_FILL, wide)
            put(inputs, "dry_air_subcolumns", dry_air, "f8", METHANE_FILL, wide)
    return path


@pytest.fixture
def spec():
    return GridSpec(west=0.0, south=0.0, east=1.0, north=1.0, resolution=0.25)


DERIVED_PAIR = (CovariateSpec(APRIORI, DERIVED), CovariateSpec(DEPARTURE, DERIVED))


def constant_profile(n, layers=12, ppb=1800.0):
    """Profiles whose ratio of sums is exactly ``ppb``."""
    dry_air = np.full((n, layers), 1.0)
    methane = np.full((n, layers), ppb * 1e-9)
    return methane, dry_air


# --------------------------------------------------------------------------
# the a priori column and the departure
# --------------------------------------------------------------------------

def test_the_prior_is_the_ratio_of_the_summed_profiles(tmp_path, spec):
    methane, dry_air = constant_profile(4)
    path = write_granule(tmp_path / "g.nc", lat=[0.5] * 4, lon=[0.5] * 4,
                         methane=[1900.0] * 4, profile=methane, dry_air=dry_air)

    soundings, _ = read_soundings(path, spec, covariates=DERIVED_PAIR)

    assert np.allclose(soundings.covariates[APRIORI], 1800.0)
    assert soundings.covariate_valid[APRIORI].all()


def test_the_departure_is_the_bias_corrected_retrieval_minus_the_prior(tmp_path,
                                                                      spec):
    methane, dry_air = constant_profile(3)
    path = write_granule(tmp_path / "g.nc", lat=[0.5] * 3, lon=[0.5] * 3,
                         methane=[1850.0, 1800.0, 1750.0],
                         profile=methane, dry_air=dry_air)

    soundings, contribution = read_soundings(path, spec, covariates=DERIVED_PAIR)

    assert np.allclose(soundings.covariates[DEPARTURE], [50.0, 0.0, -50.0])
    assert contribution.departure_mean == pytest.approx(0.0)
    assert contribution.departure_sd == pytest.approx(np.std([50.0, 0.0, -50.0]))
    assert contribution.departure_n == 3


def test_a_granule_without_the_profiles_is_gridded_for_everything_else(tmp_path,
                                                                      spec):
    """One missing support field is not a reason to discard a swath."""
    path = write_granule(tmp_path / "g.nc", lat=[0.5], lon=[0.5],
                         methane=[1900.0])

    soundings, contribution = read_soundings(path, spec, covariates=DERIVED_PAIR)

    assert len(soundings) == 1
    assert soundings.values[mg.PRIMARY][0] == pytest.approx(1900.0)
    assert set(contribution.covariates_missing) == {APRIORI, DEPARTURE}
    assert contribution.departure_n == 0


def test_a_sounding_with_a_fill_in_its_profile_carries_no_prior(tmp_path, spec):
    methane, dry_air = constant_profile(2)
    methane[1, 3] = METHANE_FILL
    path = write_granule(tmp_path / "g.nc", lat=[0.5, 0.5], lon=[0.5, 0.5],
                         methane=[1900.0, 1900.0], profile=methane,
                         dry_air=dry_air)

    soundings, contribution = read_soundings(path, spec, covariates=DERIVED_PAIR)

    valid = soundings.covariate_valid[APRIORI]
    assert list(valid) == [True, False]
    # The sounding keeps its methane; only its prior is absent.
    assert len(soundings) == 2
    assert contribution.departure_n == 1


def test_the_derived_covariates_carry_their_own_counts(tmp_path, spec):
    """The count is never separable from the mean it divides."""
    methane, dry_air = constant_profile(2)
    methane[0, 0] = METHANE_FILL
    path = write_granule(tmp_path / "g.nc", lat=[0.5, 0.5], lon=[0.5, 0.5],
                         methane=[1900.0, 1880.0], profile=methane,
                         dry_air=dry_air)
    soundings, _ = read_soundings(path, spec, covariates=DERIVED_PAIR)

    sums = {name: np.zeros(spec.shape) for name in (APRIORI, DEPARTURE)}
    counts = {name: np.zeros(spec.shape, "int64") for name in (APRIORI, DEPARTURE)}
    row, col, _ = spec.cell_of(soundings.latitude, soundings.longitude)
    mg.accumulate_covariates(soundings, row, col, sums, counts)

    assert counts[APRIORI].sum() == 1
    assert counts[DEPARTURE].sum() == 1
    assert sums[DEPARTURE].sum() == pytest.approx(80.0)


def test_an_unknown_derived_covariate_is_refused_rather_than_ignored(tmp_path,
                                                                    spec):
    methane, dry_air = constant_profile(1)
    path = write_granule(tmp_path / "g.nc", lat=[0.5], lon=[0.5],
                         methane=[1900.0], profile=methane, dry_air=dry_air)

    with pytest.raises(mg.MissingVariable, match="unknown derived"):
        read_soundings(path, spec,
                       covariates=(CovariateSpec("not_a_thing", DERIVED),))


# --------------------------------------------------------------------------
# per-granule cell sets
# --------------------------------------------------------------------------

def test_the_cell_set_records_which_cells_a_granule_reached(spec):
    module = load_script()
    acc = module.Accumulator(spec, 0.75, [mg.PRIMARY])

    packed = acc._pack_cells(np.array([0, 0, 2]), np.array([0, 1, 3]))
    bits = np.unpackbits(packed)[:spec.n_cells]

    assert packed.size == (spec.n_cells + 7) // 8
    assert bits.sum() == 3
    assert [i for i, b in enumerate(bits) if b] == [0, 1, 2 * spec.n_cols + 3]


def test_an_empty_granule_still_gets_a_row_so_the_index_stays_aligned(spec,
                                                                     tmp_path):
    """A shorter array would silently reassign every later granule's set."""
    module = load_script()
    acc = module.Accumulator(spec, 0.75, [mg.PRIMARY])
    path = write_granule(tmp_path / "g.nc", lat=[0.5], lon=[0.5],
                         methane=[1900.0])
    inside, contribution = read_soundings(path, spec)
    outside_path = write_granule(tmp_path / "out.nc", lat=[80.0], lon=[80.0],
                                 methane=[1900.0])
    outside, empty_contribution = read_soundings(outside_path, spec)

    acc.add(inside, contribution)
    acc.add(outside, empty_contribution)

    assert len(outside) == 0
    assert len(acc.granule_cells) == len(acc.contributions) == 2
    assert np.unpackbits(acc.granule_cells[0]).sum() == 1
    assert np.unpackbits(acc.granule_cells[1]).sum() == 0


def test_the_cell_set_distinguishes_what_the_saturation_pair_cannot(spec,
                                                                   tmp_path):
    """Two granules, both recording zero newly covered, covering 0 and 1 cells."""
    module = load_script()
    acc = module.Accumulator(spec, 0.75, [mg.PRIMARY])
    hit = write_granule(tmp_path / "a.nc", lat=[0.5], lon=[0.5], methane=[1900.0])
    miss = write_granule(tmp_path / "b.nc", lat=[80.0], lon=[80.0], methane=[1900.0])

    for path in (hit, hit, miss):
        soundings, contribution = read_soundings(path, spec)
        acc.add(soundings, contribution)

    newly = [pair[0] for pair in acc.saturation]
    reached = [int(np.unpackbits(row)[:spec.n_cells].sum())
               for row in acc.granule_cells]

    assert newly == [1, 0, 0]      # the pair cannot tell granules 2 and 3 apart
    assert reached == [1, 1, 0]    # the cell set can


def test_cell_sets_and_departure_stats_survive_a_checkpoint(spec, tmp_path):
    module = load_script()
    acc = module.Accumulator(spec, 0.75, [mg.PRIMARY], list(DERIVED_PAIR))
    methane, dry_air = constant_profile(2)
    path = write_granule(tmp_path / "g.nc", lat=[0.5, 0.1], lon=[0.5, 0.1],
                         methane=[1850.0, 1750.0], profile=methane,
                         dry_air=dry_air)
    soundings, contribution = read_soundings(path, spec, covariates=DERIVED_PAIR)
    acc.add(soundings, contribution)

    checkpoint = tmp_path / "c.npz"
    acc.save(checkpoint)
    restored = module.Accumulator.load(checkpoint)

    assert len(restored.granule_cells) == 1
    assert np.array_equal(restored.granule_cells[0], acc.granule_cells[0])
    assert restored.contributions[0].departure_mean == pytest.approx(0.0)
    assert restored.contributions[0].departure_n == 2
    assert set(restored.covariate_sums) == {APRIORI, DEPARTURE}


def test_a_checkpoint_without_cell_sets_loads_with_none_rather_than_fabricating(
        spec, tmp_path):
    module = load_script()
    acc = module.Accumulator(spec, 0.75, [mg.PRIMARY])
    checkpoint = tmp_path / "c.npz"
    acc.save(checkpoint)

    with np.load(checkpoint) as data:
        payload = {k: data[k] for k in data.files if k != "granule_cells"}
    with open(checkpoint, "wb") as handle:
        np.savez_compressed(handle, **payload)

    restored = module.Accumulator.load(checkpoint)
    assert restored.granule_cells == []
