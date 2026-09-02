"""Tests for the one-pass seasonal fit.

Offline. Soundings are generated from a known set of offsets and a known cycle,
so every test checks recovery of something chosen in advance rather than
agreement with a remembered number.

Two properties carry the weight. The first is that the sufficient statistics are
genuinely sufficient: the same soundings must give the same answer however they
are split across granules, and must survive a checkpoint, or the streaming pass
is not equivalent to holding everything in memory. The second is that a cell
sampled on a single date still gets an offset and is flagged, because its offset
and the seasonal term are the same quantity at that date and nothing in the data
separates them.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.methane import seasonal as se
from src.methane.seasonal import (
    HarmonicBasis,
    HarmonicStats,
    NotEnoughSeasonalSpread,
    SeasonalError,
    solve,
)

SHAPE = (4, 5)
PERIOD = se.DEFAULT_PERIOD


def cycle(day, coefficients, harmonics=1):
    return HarmonicBasis(harmonics).evaluate(day, coefficients)


def synthetic(mu, coefficients, *, per_cell=80, noise=0.0, seed=0,
              harmonics=1, days=None):
    """Soundings drawn from a known model, as (row, col, y, day) arrays."""
    rng = np.random.default_rng(seed)
    rows, cols, ys, ds = [], [], [], []
    for r in range(mu.shape[0]):
        for c in range(mu.shape[1]):
            day = (rng.uniform(1.0, PERIOD, per_cell) if days is None
                   else np.asarray(days, dtype="float64"))
            value = mu[r, c] + cycle(day, coefficients, harmonics)
            if noise:
                value = value + rng.normal(0.0, noise, day.size)
            rows.append(np.full(day.size, r))
            cols.append(np.full(day.size, c))
            ys.append(value)
            ds.append(day)
    return (np.concatenate(rows), np.concatenate(cols),
            np.concatenate(ys), np.concatenate(ds))


# --------------------------------------------------------------------------
# the basis
# --------------------------------------------------------------------------

def test_the_basis_has_two_terms_per_harmonic_and_names_them():
    assert HarmonicBasis(1).n_terms == 2
    assert HarmonicBasis(2).n_terms == 4
    assert HarmonicBasis(2).labels == ("sin1", "cos1", "sin2", "cos2")


def test_the_basis_is_periodic_over_the_year():
    basis = HarmonicBasis(2)
    a = basis.design(np.array([10.0]))
    b = basis.design(np.array([10.0 + PERIOD]))
    assert np.allclose(a, b)


def test_a_basis_with_no_harmonics_is_refused():
    with pytest.raises(SeasonalError, match="at least one harmonic"):
        HarmonicBasis(0)


# --------------------------------------------------------------------------
# recovery
# --------------------------------------------------------------------------

def test_a_known_cycle_and_known_offsets_are_recovered():
    rng = np.random.default_rng(1)
    mu = rng.normal(1900.0, 15.0, SHAPE)
    coefficients = np.array([9.0, -4.0])
    stats = HarmonicStats(SHAPE, HarmonicBasis(1))
    stats.add(*synthetic(mu, coefficients, per_cell=200, noise=0.5, seed=1))

    fit = solve(stats)
    assert fit.coefficients == pytest.approx(coefficients, abs=0.05)
    assert np.nanmax(np.abs(fit.mu - mu)) < 0.25
    assert fit.residual_sd == pytest.approx(0.5, abs=0.02)
    assert fit.degrees_of_freedom == 200 * 20 - 20 - 2


def test_a_two_harmonic_cycle_is_recovered_when_two_are_fitted():
    rng = np.random.default_rng(2)
    mu = rng.normal(1900.0, 10.0, SHAPE)
    coefficients = np.array([8.0, -3.0, 2.5, 1.5])
    stats = HarmonicStats(SHAPE, HarmonicBasis(2))
    stats.add(*synthetic(mu, coefficients, per_cell=300, noise=0.4, seed=2,
                         harmonics=2))
    fit = solve(stats)
    assert fit.coefficients == pytest.approx(coefficients, abs=0.05)
    assert np.nanmax(np.abs(fit.mu - mu)) < 0.2


def test_amplitude_and_peak_day_match_the_cycle_they_were_fitted_to():
    """A pure sine peaks a quarter period after its zero crossing."""
    mu = np.full((2, 2), 1900.0)
    stats = HarmonicStats((2, 2), HarmonicBasis(1))
    stats.add(*synthetic(mu, np.array([10.0, 0.0]), per_cell=400, seed=3))
    fit = solve(stats)
    assert fit.amplitudes[0] == pytest.approx(10.0, abs=0.01)
    assert fit.peak_day == pytest.approx(PERIOD / 4.0, abs=1.0)
    assert fit.peak_to_trough == pytest.approx(20.0, abs=0.05)


def test_a_field_with_no_seasonal_cycle_fits_coefficients_near_zero():
    rng = np.random.default_rng(4)
    mu = rng.normal(1900.0, 12.0, SHAPE)
    stats = HarmonicStats(SHAPE, HarmonicBasis(1))
    stats.add(*synthetic(mu, np.array([0.0, 0.0]), per_cell=250, noise=1.0,
                         seed=4))
    fit = solve(stats)
    assert np.abs(fit.coefficients).max() < 0.3
    assert abs(fit.variance_explained) < 0.02


def test_the_offsets_are_free_of_the_cycle_even_when_cells_are_sampled_differently():
    """The whole point: cells sampled in different seasons must still agree."""
    mu = np.full((1, 2), 1900.0)
    coefficients = np.array([12.0, 0.0])
    basis = HarmonicBasis(1)
    stats = HarmonicStats((1, 2), basis)
    # Cell 0 is sampled in spring, cell 1 in autumn, from the same true offset.
    spring = np.linspace(60.0, 150.0, 200)
    autumn = np.linspace(240.0, 330.0, 200)
    for col, days in ((0, spring), (1, autumn)):
        y = mu[0, col] + basis.evaluate(days, coefficients)
        stats.add(np.zeros(days.size, "int64"), np.full(days.size, col), y, days)

    raw = stats.sum_y / stats.n
    assert abs(raw[0, 0] - raw[0, 1]) > 10.0, "the raw means differ by season"
    fit = solve(stats)
    assert fit.mu[0, 0] == pytest.approx(fit.mu[0, 1], abs=0.05), \
        "the deseasonalised offsets agree, which is what the fit is for"


# --------------------------------------------------------------------------
# a cell sampled on one date
# --------------------------------------------------------------------------

def test_a_cell_sampled_on_one_day_gets_an_offset_and_is_flagged():
    rng = np.random.default_rng(5)
    mu = rng.normal(1900.0, 10.0, (1, 3))
    coefficients = np.array([9.0, -4.0])
    basis = HarmonicBasis(1)
    stats = HarmonicStats((1, 3), basis)
    # Two well-sampled cells identify the cycle; the third sees one date only.
    for col in (0, 1):
        days = rng.uniform(1.0, PERIOD, 300)
        stats.add(np.zeros(300, "int64"), np.full(300, col),
                  mu[0, col] + basis.evaluate(days, coefficients), days)
    single = np.array([200.0])
    stats.add(np.array([0]), np.array([2]),
              np.array([mu[0, 2] + basis.evaluate(single, coefficients)[0]]),
              single)

    fit = solve(stats)
    assert fit.poorly_identified[0, 2], "a single date cannot identify an offset"
    assert not fit.poorly_identified[0, 0]
    assert np.isfinite(fit.mu[0, 2]), "it still gets an offset rather than a NaN"
    assert fit.mu[0, 2] == pytest.approx(mu[0, 2], abs=0.01), \
        "and the offset is right, because the cycle came from the other cells"


def test_a_singleton_cell_contributes_nothing_to_the_fitted_cycle():
    """It carries no information about the cycle and must not bias it."""
    rng = np.random.default_rng(6)
    mu = rng.normal(1900.0, 10.0, (1, 2))
    coefficients = np.array([7.0, 2.0])
    basis = HarmonicBasis(1)

    def build(with_outlier):
        stats = HarmonicStats((1, 2), basis)
        days = rng2.uniform(1.0, PERIOD, 300)
        stats.add(np.zeros(300, "int64"), np.zeros(300, "int64"),
                  mu[0, 0] + basis.evaluate(days, coefficients), days)
        if with_outlier:
            stats.add(np.array([0]), np.array([1]), np.array([5000.0]),
                      np.array([200.0]))
        return stats

    rng2 = np.random.default_rng(7)
    without = solve(build(False))
    rng2 = np.random.default_rng(7)
    with_it = solve(build(True))
    assert with_it.coefficients == pytest.approx(without.coefficients, abs=1e-9)


def test_a_composite_of_one_date_cannot_be_deseasonalised():
    stats = HarmonicStats((2, 2), HarmonicBasis(1))
    day = np.full(40, 100.0)
    rng = np.random.default_rng(8)
    stats.add(rng.integers(0, 2, 40), rng.integers(0, 2, 40),
              rng.normal(1900, 5, 40), day)
    with pytest.raises(NotEnoughSeasonalSpread, match="rank deficient"):
        solve(stats)


# --------------------------------------------------------------------------
# sufficiency: batching, order and checkpoints
# --------------------------------------------------------------------------

def test_statistics_are_identical_whether_soundings_arrive_together_or_split():
    rng = np.random.default_rng(9)
    mu = rng.normal(1900.0, 12.0, SHAPE)
    row, col, y, day = synthetic(mu, np.array([6.0, -2.0]), per_cell=120,
                                 noise=0.7, seed=9)

    whole = HarmonicStats(SHAPE, HarmonicBasis(2))
    whole.add(row, col, y, day)

    pieces = HarmonicStats(SHAPE, HarmonicBasis(2))
    order = rng.permutation(y.size)
    for chunk in np.array_split(order, 37):
        pieces.add(row[chunk], col[chunk], y[chunk], day[chunk])

    assert np.array_equal(whole.n, pieces.n)
    for name in ("sum_y", "sum_yy", "sum_d", "sum_dd", "sum_x", "sum_xx",
                 "sum_yx"):
        assert np.allclose(getattr(whole, name), getattr(pieces, name),
                           rtol=0, atol=1e-6), name
    assert solve(whole).coefficients == pytest.approx(
        solve(pieces).coefficients, abs=1e-9)


def test_an_empty_batch_changes_nothing():
    stats = HarmonicStats(SHAPE, HarmonicBasis(1))
    stats.add(np.array([0]), np.array([0]), np.array([1900.0]), np.array([50.0]))
    before = stats.sum_y.copy()
    stats.add(np.array([]), np.array([]), np.array([]), np.array([]))
    assert np.array_equal(stats.sum_y, before)
    assert stats.n.sum() == 1


def test_mismatched_batch_lengths_are_refused():
    stats = HarmonicStats(SHAPE, HarmonicBasis(1))
    with pytest.raises(SeasonalError, match="same length"):
        stats.add(np.array([0, 0]), np.array([0]), np.array([1900.0]),
                  np.array([50.0]))


# --------------------------------------------------------------------------
# the sampling-date diagnostics
# --------------------------------------------------------------------------

def test_date_mean_and_spread_describe_the_sampling_not_the_values():
    stats = HarmonicStats((1, 2), HarmonicBasis(1))
    tight = np.array([100.0, 101.0, 102.0])
    wide = np.array([10.0, 180.0, 350.0])
    stats.add(np.zeros(3, "int64"), np.zeros(3, "int64"),
              np.full(3, 1900.0), tight)
    stats.add(np.zeros(3, "int64"), np.ones(3, "int64"),
              np.full(3, 1900.0), wide)
    assert stats.date_mean()[0, 0] == pytest.approx(101.0)
    assert stats.date_mean()[0, 1] == pytest.approx(180.0)
    assert stats.date_spread()[0, 0] == pytest.approx(np.std(tight))
    assert stats.date_spread()[0, 1] == pytest.approx(np.std(wide))
    assert stats.date_spread()[0, 1] > stats.date_spread()[0, 0]


def test_an_unobserved_cell_has_no_date_statistics():
    stats = HarmonicStats((1, 2), HarmonicBasis(1))
    stats.add(np.array([0]), np.array([0]), np.array([1900.0]), np.array([50.0]))
    assert np.isnan(stats.date_mean()[0, 1])
    assert np.isnan(stats.date_spread()[0, 1])
    assert stats.date_spread()[0, 0] == 0.0, "one sounding has zero spread"


# --------------------------------------------------------------------------
# fitting fewer harmonics from the same statistics
# --------------------------------------------------------------------------

def test_a_lower_order_fit_comes_from_the_same_accumulation():
    """One pass must answer whether the second harmonic is worth having."""
    rng = np.random.default_rng(10)
    mu = rng.normal(1900.0, 10.0, SHAPE)
    coefficients = np.array([8.0, -3.0, 2.5, 1.5])
    stats = HarmonicStats(SHAPE, HarmonicBasis(2))
    stats.add(*synthetic(mu, coefficients, per_cell=250, noise=0.4, seed=10,
                         harmonics=2))

    two = solve(stats)
    one = solve(stats.truncated(1))
    assert two.coefficients == pytest.approx(coefficients, abs=0.05)
    assert one.coefficients == pytest.approx(coefficients[:2], abs=0.1)
    assert one.basis.harmonics == 1 and two.basis.harmonics == 2
    assert one.residual_sd > two.residual_sd, \
        "dropping a real harmonic must cost residual variance"
    assert one.n_soundings == two.n_soundings, "the same soundings, both times"


def test_truncating_beyond_what_was_accumulated_is_refused():
    stats = HarmonicStats(SHAPE, HarmonicBasis(1))
    with pytest.raises(SeasonalError, match="cannot fit 2 harmonics"):
        stats.truncated(2)


def test_a_second_harmonic_that_is_not_there_is_fitted_near_zero():
    rng = np.random.default_rng(11)
    mu = rng.normal(1900.0, 10.0, SHAPE)
    stats = HarmonicStats(SHAPE, HarmonicBasis(2))
    stats.add(*synthetic(mu, np.array([7.0, -2.0, 0.0, 0.0]), per_cell=300,
                         noise=0.5, seed=11, harmonics=2))
    fit = solve(stats)
    assert abs(fit.coefficients[2]) < 0.15 and abs(fit.coefficients[3]) < 0.15
