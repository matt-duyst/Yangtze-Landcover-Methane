"""Tests for the baseline models.

Offline throughout. Tables are built in memory with a known answer, so each
test checks arithmetic rather than agreement with a remembered number.

The cases that carry the weight are the ones a baseline could be quietly wrong
about and still look plausible: that a constant predictor's error is the target's
own spread and nothing cleverer, that least squares recovers a coefficient it was
given, that a held-out province is genuinely absent from its own training set,
that the spatial null cannot see the cell it is predicting or any cell held out
with it, and that a missing predictor is never filled in.
"""

from __future__ import annotations

import numpy as np
import pytest

from src.model import baselines as bl
from src.model.baselines import (
    ConstantFit,
    GlobalMean,
    LinearModel,
    Metrics,
    MissingPredictor,
    NeighbourMean,
    ProvinceMean,
    Table,
    evaluate,
    leave_one_province_out,
    rows_for,
    spatial_blocks,
    weighted_mean,
)


def make_table(y, *, weight=None, province=None, row=None, col=None, **columns):
    """A table on a single lattice row unless positions are given."""
    y = np.asarray(y, dtype="float64")
    n = y.size
    return Table(
        y=y,
        weight=np.ones(n) if weight is None else np.asarray(weight, "float64"),
        row=np.zeros(n, "int64") if row is None else np.asarray(row, "int64"),
        col=np.arange(n) if col is None else np.asarray(col, "int64"),
        province=np.array(["A"] * n if province is None else province, dtype=object),
        columns={k: np.asarray(v, "float64") for k, v in columns.items()})


def lattice(side, values, **columns):
    """A square lattice of ``side`` by ``side`` cells, filled row-major."""
    rows, cols = np.divmod(np.arange(side * side), side)
    return make_table(values, row=rows, col=cols, **columns)


# --------------------------------------------------------------------------
# metrics
# --------------------------------------------------------------------------

def test_a_constant_at_the_mean_has_the_targets_standard_deviation_as_rmse():
    """The whole point of the null: its error is the spread, restated."""
    y = np.array([1890.0, 1900.0, 1910.0, 1925.0, 1880.0])
    table = make_table(y)
    fit = GlobalMean().fit(table, table.all_rows, np.ones(y.size))
    predicted = fit.predict(table, table.all_rows)
    assert fit.fallback == pytest.approx(y.mean())
    assert bl.rmse(y, predicted, np.ones(y.size)) == pytest.approx(y.std())
    assert bl.r2(y, predicted, np.ones(y.size)) == pytest.approx(0.0, abs=1e-12)


def test_weighted_rmse_of_the_weighted_mean_is_the_weighted_spread():
    y = np.array([1890.0, 1900.0, 1930.0])
    w = np.array([1.0, 10.0, 100.0])
    centre = weighted_mean(y, w)
    expected = np.sqrt(np.sum(w * (y - centre) ** 2) / w.sum())
    assert bl.rmse(y, np.full(3, centre), w) == pytest.approx(expected)


def test_r2_is_nan_when_the_target_has_no_variance():
    y = np.full(4, 1900.0)
    assert np.isnan(bl.r2(y, y, np.ones(4)))


def test_metrics_carry_the_sample_size_they_were_computed_on():
    m = Metrics.of(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]), np.ones(3))
    assert m.n == 3 and m.rmse == pytest.approx(0.0)


# --------------------------------------------------------------------------
# least squares
# --------------------------------------------------------------------------

def test_ols_recovers_a_coefficient_it_was_given():
    x = np.linspace(0.0, 1.0, 60)
    y = 1880.0 + 42.0 * x
    table = make_table(y, impervious_fraction=x)
    fit = LinearModel(("impervious_fraction",)).fit(
        table, table.all_rows, np.ones(x.size))
    assert fit.terms["intercept"] == pytest.approx(1880.0, abs=1e-8)
    assert fit.terms["impervious_fraction"] == pytest.approx(42.0, abs=1e-8)


def test_ols_recovers_two_coefficients_and_an_interaction():
    rng = np.random.default_rng(0)
    a, b = rng.uniform(0, 1, 200), rng.uniform(0, 1, 200)
    y = 1890.0 + 30.0 * a - 12.0 * b + 25.0 * a * b
    table = make_table(y, impervious_fraction=a, rice_fraction_single=b)
    names = ("impervious_fraction", "rice_fraction_single")
    fit = LinearModel(names, interaction=True).fit(
        table, table.all_rows, np.ones(200))
    terms = fit.terms
    assert terms["intercept"] == pytest.approx(1890.0, abs=1e-8)
    assert terms["impervious_fraction"] == pytest.approx(30.0, abs=1e-8)
    assert terms["rice_fraction_single"] == pytest.approx(-12.0, abs=1e-8)
    assert terms[" x ".join(names)] == pytest.approx(25.0, abs=1e-8)


def test_a_perfect_linear_fit_has_r2_of_one():
    x = np.linspace(0, 1, 30)
    table = make_table(1900.0 + 10.0 * x, impervious_fraction=x)
    result = evaluate(table, LinearModel(("impervious_fraction",)),
                      scheme="spatial blocks", weighted=False, block=2, folds=3)
    assert result.in_sample.r2 == pytest.approx(1.0)
    assert result.in_sample.rmse == pytest.approx(0.0, abs=1e-9)


# --------------------------------------------------------------------------
# weighting
# --------------------------------------------------------------------------

def test_weighting_moves_the_fit_towards_the_well_observed_cells():
    """One badly observed outlier should not drag a weighted fit."""
    x = np.array([0.0, 0.25, 0.5, 0.75, 1.0])
    y = np.array([1900.0, 1905.0, 1910.0, 1915.0, 1960.0])   # last one is off
    weight = np.array([100.0, 100.0, 100.0, 100.0, 1.0])     # and barely observed
    table = make_table(y, weight=weight, impervious_fraction=x)

    unweighted = LinearModel(("impervious_fraction",)).fit(
        table, table.all_rows, np.ones(5)).terms["impervious_fraction"]
    weighted = LinearModel(("impervious_fraction",)).fit(
        table, table.all_rows, weight).terms["impervious_fraction"]

    # The four solid cells alone have a slope of exactly 20. The outlier keeps a
    # weight of 1 rather than 0, so the weighted fit lands near 20 but not on it.
    assert weighted == pytest.approx(20.8, abs=0.1)
    assert unweighted == pytest.approx(52.0, abs=0.5)
    assert unweighted > 2 * weighted, "the outlier dominates the unweighted fit"


def test_a_constant_is_the_weighted_mean_when_weighted():
    y = np.array([1890.0, 1950.0])
    weight = np.array([99.0, 1.0])
    table = make_table(y, weight=weight)
    fit = GlobalMean().fit(table, table.all_rows, weight)
    assert fit.fallback == pytest.approx(1890.6)
    assert fit.fallback < np.mean(y)


# --------------------------------------------------------------------------
# leave one province out
# --------------------------------------------------------------------------

def test_leave_one_province_out_holds_out_exactly_one_province():
    province = ["A"] * 4 + ["B"] * 3 + ["C"] * 5
    table = make_table(np.arange(12, dtype="float64"), province=province)
    folds = leave_one_province_out(table, table.all_rows)
    assert [f.name for f in folds] == ["A", "B", "C"]
    for fold in folds:
        assert set(table.province[fold.test]) == {fold.name}
        assert fold.name not in set(table.province[fold.train])
        assert fold.train.size + fold.test.size == table.n
        assert not set(fold.train) & set(fold.test)
    assert sorted(np.concatenate([f.test for f in folds])) == list(range(12))


def test_every_row_is_held_out_exactly_once_across_the_folds():
    province = ["A", "B", "A", "C", "B", "C", "A"]
    table = make_table(np.arange(7, dtype="float64"), province=province)
    held = np.concatenate([f.test for f in leave_one_province_out(
        table, table.all_rows)])
    assert sorted(held.tolist()) == list(range(7))


def test_a_per_province_constant_degenerates_to_the_global_one_under_lopo():
    """The held-out province is by construction the group with no training data.

    This is not a defect to work around. It is what the scheme means, and the
    results table showing identical numbers for the two constants under
    leave-one-province-out is that fact rather than a copied row.
    """
    province = ["A"] * 6 + ["B"] * 6
    y = np.concatenate([np.full(6, 1890.0), np.full(6, 1930.0)])
    table = make_table(y, province=province)
    globally = evaluate(table, GlobalMean(), scheme="leave-one-province-out",
                        weighted=False)
    per_province = evaluate(table, ProvinceMean(), scheme="leave-one-province-out",
                            weighted=False)
    assert per_province.held_out.rmse == pytest.approx(globally.held_out.rmse)
    assert per_province.in_sample.rmse < globally.in_sample.rmse, \
        "in sample it is strictly better, which is the whole reason to report both"


def test_a_per_province_constant_is_the_group_mean_in_sample():
    province = ["A"] * 3 + ["B"] * 3
    y = np.array([1890.0, 1892.0, 1894.0, 1930.0, 1932.0, 1934.0])
    table = make_table(y, province=province)
    fit = ProvinceMean().fit(table, table.all_rows, np.ones(6))
    assert fit.by_group["A"] == pytest.approx(1892.0)
    assert fit.by_group["B"] == pytest.approx(1932.0)
    assert fit.predict(table, np.array([0, 5])).tolist() == [1892.0, 1932.0]


def test_a_group_absent_from_training_takes_the_fallback():
    fit = ConstantFit(fallback=1900.0, by_group={"A": 1880.0})
    table = make_table(np.zeros(2), province=["A", "Z"])
    assert fit.predict(table, np.array([0, 1])).tolist() == [1880.0, 1900.0]


# --------------------------------------------------------------------------
# spatial blocks
# --------------------------------------------------------------------------

def test_spatial_blocks_group_whole_blocks_into_the_same_fold():
    table = lattice(8, np.arange(64, dtype="float64"))
    folds = spatial_blocks(table, table.all_rows, block=4, folds=2, seed=0)
    seen = {}
    for k, fold in enumerate(folds):
        for i in fold.test:
            key = (int(table.row[i]) // 4, int(table.col[i]) // 4)
            assert seen.setdefault(key, k) == k, "a block must not span two folds"
    assert len(seen) == 4, "an 8 by 8 lattice holds four 4 by 4 blocks"


def test_spatial_blocks_hold_out_every_row_exactly_once():
    table = lattice(6, np.arange(36, dtype="float64"))
    folds = spatial_blocks(table, table.all_rows, block=2, folds=3, seed=0)
    held = np.concatenate([f.test for f in folds])
    assert sorted(held.tolist()) == list(range(36))
    for fold in folds:
        assert not set(fold.train) & set(fold.test)


def test_the_block_split_is_the_same_every_run():
    table = lattice(6, np.arange(36, dtype="float64"))
    first = spatial_blocks(table, table.all_rows, block=2, folds=3, seed=0)
    again = spatial_blocks(table, table.all_rows, block=2, folds=3, seed=0)
    assert [f.test.tolist() for f in first] == [f.test.tolist() for f in again]


def test_a_different_seed_gives_a_different_split():
    table = lattice(6, np.arange(36, dtype="float64"))
    a = spatial_blocks(table, table.all_rows, block=2, folds=3, seed=0)
    b = spatial_blocks(table, table.all_rows, block=2, folds=3, seed=7)
    assert [f.test.tolist() for f in a] != [f.test.tolist() for f in b]


# --------------------------------------------------------------------------
# the spatial null
# --------------------------------------------------------------------------

def test_the_spatial_null_excludes_the_cell_it_is_predicting():
    """A 3 by 3 lattice with a spike in the middle."""
    values = np.full(9, 1900.0)
    values[4] = 2000.0
    table = lattice(3, values)
    fit = NeighbourMean().fit(table, table.all_rows, np.ones(9))
    assert fit.predict(table, np.array([4]))[0] == pytest.approx(1900.0), \
        "the centre must be predicted from its eight neighbours, not itself"


def test_the_spatial_null_averages_only_adjacent_cells():
    values = np.arange(9, dtype="float64")
    table = lattice(3, values)
    fit = NeighbourMean().fit(table, table.all_rows, np.ones(9))
    corner = fit.predict(table, np.array([0]))[0]
    assert corner == pytest.approx(np.mean([1.0, 3.0, 4.0])), \
        "the top-left corner has exactly three queen neighbours"


def test_the_spatial_null_cannot_see_cells_held_out_with_the_target():
    """A cell in the interior of a held-out block has nothing to lean on."""
    table = lattice(4, np.arange(16, dtype="float64"))
    train = np.array([i for i in range(16) if table.row[i] < 2])
    fit = NeighbourMean().fit(table, train, np.ones(train.size))
    far = np.array([i for i in range(16) if table.row[i] == 3])
    assert fit.fallbacks_for(table, far) == far.size
    assert np.allclose(fit.predict(table, far), fit.fallback)


def test_the_spatial_null_falls_back_rather_than_inventing_a_neighbour():
    table = lattice(3, np.arange(9, dtype="float64"))
    train = np.array([0])
    fit = NeighbourMean().fit(table, train, np.ones(1))
    isolated = np.array([8])                       # opposite corner, not adjacent
    assert fit.predict(table, isolated)[0] == pytest.approx(fit.fallback)
    assert fit.fallbacks_for(table, isolated) == 1


# --------------------------------------------------------------------------
# missing predictors
# --------------------------------------------------------------------------

def test_rows_without_a_predictor_are_dropped_not_imputed():
    x = np.array([0.1, np.nan, 0.3, np.nan, 0.5])
    table = make_table(np.arange(5, dtype="float64"), rice_fraction_single=x)
    model = LinearModel(("rice_fraction_single",))
    kept = rows_for(table, model, table.all_rows, on_missing="drop")
    assert kept.tolist() == [0, 2, 4]


def test_a_model_can_be_made_to_refuse_rather_than_narrow_the_sample():
    x = np.array([0.1, np.nan, 0.3])
    table = make_table(np.arange(3, dtype="float64"), rice_fraction_single=x)
    model = LinearModel(("rice_fraction_single",))
    with pytest.raises(MissingPredictor, match="lack one"):
        rows_for(table, model, table.all_rows, on_missing="raise")


def test_fitting_on_rows_with_a_missing_predictor_raises_rather_than_imputing():
    x = np.array([0.1, np.nan, 0.3, 0.4])
    table = make_table(np.arange(4, dtype="float64"), rice_fraction_single=x)
    with pytest.raises(MissingPredictor, match="never imputed"):
        LinearModel(("rice_fraction_single",)).fit(
            table, table.all_rows, np.ones(4))


def test_evaluation_reports_the_rows_it_dropped():
    rng = np.random.default_rng(1)
    x = rng.uniform(0, 1, 40)
    y = 1900.0 + 5.0 * x
    rice = x.copy()
    rice[:12] = np.nan
    table = lattice(
        1, y, impervious_fraction=x, rice_fraction_single=rice) \
        if False else make_table(
            y, row=np.repeat(np.arange(8), 5), col=np.tile(np.arange(5), 8),
            impervious_fraction=x, rice_fraction_single=rice)
    result = evaluate(table, LinearModel(("rice_fraction_single",)),
                      scheme="spatial blocks", weighted=False, block=2, folds=2)
    assert result.n == 28 and result.dropped == 12
    impervious = evaluate(table, LinearModel(("impervious_fraction",)),
                          scheme="spatial blocks", weighted=False, block=2, folds=2)
    assert impervious.n == 40 and impervious.dropped == 0


def test_a_constant_model_requires_nothing_and_keeps_every_row():
    x = np.array([np.nan] * 5)
    table = make_table(np.arange(5, dtype="float64"), rice_fraction_single=x)
    assert rows_for(table, GlobalMean(), table.all_rows).tolist() == list(range(5))


# --------------------------------------------------------------------------
# evaluation bookkeeping
# --------------------------------------------------------------------------

def test_held_out_metrics_are_pooled_over_folds_not_averaged():
    """A fold of one cell must not weigh as much as a fold of many."""
    province = ["A"] * 20 + ["B"]
    y = np.concatenate([np.full(20, 1900.0), np.array([2100.0])])
    table = make_table(y, province=province)
    result = evaluate(table, GlobalMean(), scheme="leave-one-province-out",
                      weighted=False)
    # Pooled: 20 cells are predicted at 2100/21 off, one is far off.
    fit_a = np.full(20, 2100.0)                     # trained on B alone
    fit_b = np.array([1900.0])                      # trained on A alone
    expected = bl.rmse(y, np.concatenate([fit_a, fit_b]), np.ones(21))
    assert result.held_out.rmse == pytest.approx(expected)
    assert result.held_out.n == 21


def test_in_sample_and_held_out_are_reported_separately():
    rng = np.random.default_rng(3)
    x = rng.uniform(0, 1, 36)
    y = 1900.0 + 8.0 * x + rng.normal(0, 2.0, 36)
    table = lattice(6, y, impervious_fraction=x)
    result = evaluate(table, LinearModel(("impervious_fraction",)),
                      scheme="spatial blocks", weighted=False, block=2, folds=3)
    assert result.in_sample.n == result.n == 36
    assert result.held_out.n == 36
    assert result.in_sample.rmse <= result.held_out.rmse + 1e-9, \
        "held out cannot beat in sample on the same fitted family"


def test_the_result_records_the_coefficients_for_a_linear_model():
    x = np.linspace(0, 1, 36)
    table = lattice(6, 1900.0 + 7.0 * x, impervious_fraction=x)
    result = evaluate(table, LinearModel(("impervious_fraction",)),
                      scheme="spatial blocks", weighted=False, block=2, folds=3)
    assert "impervious_fraction +7.0000" in result.detail
    assert result.as_dict()["model"] == "OLS impervious_fraction"


def test_an_unknown_scheme_is_refused():
    table = make_table(np.arange(5, dtype="float64"))
    with pytest.raises(bl.ModelError, match="unknown scheme"):
        evaluate(table, GlobalMean(), scheme="random", weighted=False)
