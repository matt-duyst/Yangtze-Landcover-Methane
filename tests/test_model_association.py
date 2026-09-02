"""Tests for correlation and partial correlation.

Offline, on constructed data where the answer is known before the code runs.

The case that carries the weight is a genuine confounder: two variables with no
relationship to each other, both driven by a third. The raw correlation between
them is large and the partial correlation given the third is zero. That is
exactly the structure the albedo test is looking for, so it is worth pinning
that the tool can find it and, just as importantly, that it does not find one
where none exists.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.model.association import (
    Association,
    AssociationError,
    correlate,
    paired,
    partial_correlation,
)


def test_paired_keeps_only_rows_where_everything_is_finite():
    a = np.array([1.0, np.nan, 3.0, 4.0])
    b = np.array([1.0, 2.0, np.nan, 4.0])
    x, y = paired(a, b)
    assert x.tolist() == [1.0, 4.0]
    assert y.tolist() == [1.0, 4.0]


def test_paired_refuses_arrays_of_different_lengths():
    with pytest.raises(AssociationError, match="same length"):
        paired(np.zeros(3), np.zeros(4))


def test_a_perfect_linear_relationship_correlates_at_one():
    x = np.linspace(0, 1, 50)
    result = correlate("y ~ x", x, 3.0 * x + 1.0)
    assert result.pearson == pytest.approx(1.0)
    assert result.spearman == pytest.approx(1.0)
    assert result.n == 50


def test_a_monotone_but_curved_relationship_separates_the_two_measures():
    x = np.linspace(0.1, 3.0, 60)
    result = correlate("y ~ x", x, np.exp(4.0 * x))
    assert result.spearman == pytest.approx(1.0), "still perfectly monotone"
    assert result.pearson < 0.85, "but far from linear"


def test_correlation_ignores_rows_where_either_side_is_missing():
    x = np.array([1.0, 2.0, 3.0, 4.0, np.nan])
    y = np.array([2.0, 4.0, 6.0, 8.0, 100.0])
    assert correlate("y ~ x", x, y).n == 4


def test_too_few_paired_observations_is_refused():
    with pytest.raises(AssociationError, match="paired observations"):
        correlate("y ~ x", np.array([1.0, np.nan]), np.array([1.0, 2.0]))


# --------------------------------------------------------------------------
# the confounder case
# --------------------------------------------------------------------------

def test_a_common_cause_produces_a_correlation_that_partialling_removes():
    """Neither variable touches the other; both are driven by z."""
    rng = np.random.default_rng(0)
    z = rng.normal(size=500)
    x = z + rng.normal(0, 0.4, 500)
    y = z + rng.normal(0, 0.4, 500)

    raw = correlate("x ~ y", x, y)
    given = partial_correlation("x ~ y", x, y, [z], ["z"])
    assert raw.pearson > 0.7, "the confounded association looks strong"
    assert abs(given.pearson) < 0.1, "and vanishes once the cause is removed"
    assert given.controls == ("z",)
    assert given.n == raw.n == 500


def test_a_real_relationship_survives_partialling_out_something_else():
    rng = np.random.default_rng(1)
    z = rng.normal(size=500)
    x = rng.normal(size=500)
    y = 2.0 * x + z                       # y genuinely depends on x
    raw = correlate("x ~ y", x, y)
    given = partial_correlation("x ~ y", x, y, [z], ["z"])
    assert raw.pearson > 0.6
    assert given.pearson > 0.85, "removing z strengthens rather than kills it"


def test_partialling_out_an_irrelevant_variable_changes_almost_nothing():
    rng = np.random.default_rng(2)
    x = rng.normal(size=400)
    y = 1.5 * x + rng.normal(0, 0.5, 400)
    noise = rng.normal(size=400)
    raw = correlate("x ~ y", x, y)
    given = partial_correlation("x ~ y", x, y, [noise], ["noise"])
    assert given.pearson == pytest.approx(raw.pearson, abs=0.03)


def test_several_controls_can_be_partialled_at_once():
    rng = np.random.default_rng(3)
    a, b = rng.normal(size=400), rng.normal(size=400)
    x = a + b + rng.normal(0, 0.3, 400)
    y = a + b + rng.normal(0, 0.3, 400)
    given = partial_correlation("x ~ y", x, y, [a, b], ["a", "b"])
    assert abs(given.pearson) < 0.15
    assert given.controls == ("a", "b")


def test_a_sample_too_small_for_its_controls_is_refused():
    rng = np.random.default_rng(4)
    with pytest.raises(AssociationError, match="cannot support"):
        partial_correlation("x ~ y", rng.normal(size=5), rng.normal(size=5),
                            [rng.normal(size=5), rng.normal(size=5)], ["a", "b"])


def test_partial_correlation_drops_rows_missing_a_control():
    rng = np.random.default_rng(5)
    x, y = rng.normal(size=100), rng.normal(size=100)
    z = rng.normal(size=100)
    z[:20] = np.nan
    assert partial_correlation("x ~ y", x, y, [z], ["z"]).n == 80


# --------------------------------------------------------------------------
# weighting
# --------------------------------------------------------------------------

def test_weighting_can_reverse_the_sign_of_a_correlation():
    """The rice result depends on this being possible, so it is pinned.

    Sixty lightly weighted cells on a rising line and twelve heavily weighted
    ones on a falling line. Counting cells the association is positive;
    weighting by how well each was observed it is negative. Neither is a
    mistake, which is why both weightings are reported everywhere.
    """
    light_x = np.linspace(0.0, 1.0, 60)
    heavy_x = np.linspace(0.0, 1.0, 12)
    x = np.concatenate([light_x, heavy_x])
    y = np.concatenate([light_x, 0.55 - 0.5 * heavy_x])
    weight = np.concatenate([np.ones(60), np.full(12, 200.0)])

    plain = correlate("y ~ x", x, y)
    weighted = correlate("y ~ x", x, y, weight=weight)
    assert plain.pearson == pytest.approx(0.750, abs=0.01)
    assert weighted.pearson == pytest.approx(-0.891, abs=0.01)
    assert plain.spearman > 0 and weighted.spearman < 0


def test_uniform_weights_reproduce_the_unweighted_correlation():
    rng = np.random.default_rng(6)
    x = rng.normal(size=200)
    y = 0.8 * x + rng.normal(0, 0.6, 200)
    plain = correlate("y ~ x", x, y)
    uniform = correlate("y ~ x", x, y, weight=np.ones(200))
    assert uniform.pearson == pytest.approx(plain.pearson, abs=1e-9)
    assert uniform.spearman == pytest.approx(plain.spearman, abs=1e-9)


def test_the_record_serialises_with_its_controls_and_sample_size():
    rng = np.random.default_rng(7)
    x, y, z = (rng.normal(size=300) for _ in range(3))
    record = partial_correlation("methane ~ rice", x, y, [z],
                                 ["surface_albedo_SWIR"]).as_dict()
    assert record["relationship"] == "methane ~ rice"
    assert record["controlling_for"] == "surface_albedo_SWIR"
    assert record["n"] == 300
