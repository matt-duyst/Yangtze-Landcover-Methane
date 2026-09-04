"""Tests for the coverage figure.

Offline, on a checkpoint built in `tmp_path`, reading nothing from `data/`. The
real 2018 checkpoint is gitignored and is not available to the test suite, so
everything here is constructed with a known answer.

Two properties carry the weight. The first is that the figure function returns
a figure and writes nothing, because that is what makes every other figure in
this repository testable. The second is the distinction between a month with no
soundings and a month with no granules: the 2018 record contains no month that
was sampled and yielded nothing, so that case is constructed here rather than
waiting for a year that has one.
"""

from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from src.figures.coverage import (
    CoverageRecord,
    MonthlyYield,
    coverage_figure,
    from_checkpoint,
)


def write_checkpoint(path, contributions, cumulative):
    """A checkpoint holding only the two fields the figure reads."""
    saturation = np.stack([np.arange(len(cumulative)), np.asarray(cumulative)], axis=1)
    with open(path, "wb") as handle:
        np.savez_compressed(handle, saturation=saturation,
                            contributions=json.dumps(contributions))
    return path


def contribution(date, soundings):
    return {"acquired": date, "soundings_in_box": soundings}


@pytest.fixture
def record():
    """Three months: one absent, one sampled but empty, one productive."""
    return CoverageRecord(
        cumulative_cells=np.concatenate([
            np.array([10, 40, 55, 60, 61]),
            np.linspace(62, 88, 55).astype(int)]),
        monthly=tuple(
            MonthlyYield(month=m, soundings=0, granules=0, acquired=0)
            if m < 6 else
            MonthlyYield(month=m, soundings=100 * m, granules=m, acquired=m + 1)
            for m in range(1, 13)),
        total_cells=100)


def test_the_figure_function_returns_a_figure_and_writes_nothing(record, tmp_path):
    before = set(tmp_path.iterdir())

    fig = coverage_figure(record)
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


def test_the_figure_has_three_labelled_panels(record):
    fig = coverage_figure(record)
    try:
        assert len(fig.axes) == 3
        labels = {text.get_text() for ax in fig.axes for text in ax.texts}
        assert {"(a)", "(b)", "(c)"} <= labels
    finally:
        plt.close(fig)


def test_every_axis_label_names_its_units_in_parentheses(record):
    """The house form for the venue's "units on every axis label" rule.

    Parentheses are the convention rather than the requirement, but making the
    convention the testable thing is what lets the rule be enforced at all.
    """
    fig = coverage_figure(record)
    try:
        labels = [ax.get_xlabel() for ax in fig.axes if ax.get_xlabel()]
        labels += [ax.get_ylabel() for ax in fig.axes if ax.get_ylabel()]
        assert labels
        for label in labels:
            assert "(" in label and ")" in label, label
    finally:
        plt.close(fig)


def test_absent_months_are_drawn_as_absent_rather_than_as_zero(record):
    fig = coverage_figure(record)
    try:
        bars = [patch for ax in fig.axes for patch in ax.patches]
        # Nothing is drawn at a month that was never sampled, so a reader
        # cannot mistake an absence for a measured zero.
        assert bars
        assert all(patch.get_height() > 0 for patch in bars)
        wording = " ".join(text.get_text() for ax in fig.axes for text in ax.texts)
        assert "no granules" in wording
    finally:
        plt.close(fig)


def test_from_checkpoint_aggregates_soundings_and_granules_by_month(tmp_path):
    path = write_checkpoint(
        tmp_path / "c.npz",
        [contribution("2018-05-02T00:00:00", 100),
         contribution("2018-05-09T00:00:00", 40),
         contribution("2018-10-01T00:00:00", 7)],
        [1, 2, 3])

    result = from_checkpoint(path, total_cells=10)

    may = result.monthly[4]
    assert (may.month, may.soundings, may.granules) == (5, 140, 2)
    assert result.curve_length == result.productive_granules
    assert result.monthly[9].soundings == 7
    assert result.total_soundings == 147
    assert result.productive_granules == 3


def test_a_month_that_was_sampled_but_yielded_nothing_is_not_an_absence(tmp_path):
    path = write_checkpoint(
        tmp_path / "c.npz",
        [contribution("2018-07-02T00:00:00", 0),
         contribution("2018-07-03T00:00:00", 0),
         contribution("2018-08-01T00:00:00", 12)],
        [0, 0, 4])

    result = from_checkpoint(path, total_cells=10)

    july = result.monthly[6]
    assert july.acquired == 2      # the satellite passed over
    assert july.granules == 0      # and returned nothing usable
    assert july.observed is True   # which is not the same as never looking

    january = result.monthly[0]
    assert (january.acquired, january.granules, january.observed) == (0, 0, False)


def test_coverage_fractions_are_read_against_the_grid_size(tmp_path):
    path = write_checkpoint(
        tmp_path / "c.npz",
        [contribution(f"2018-05-0{d}T00:00:00", 5) for d in (2, 3, 4)],
        [25, 50, 90])

    result = from_checkpoint(path, total_cells=100)

    assert result.curve_length == 3
    assert result.fraction_at(1) == pytest.approx(0.25)
    assert result.final_fraction == pytest.approx(0.90)


def test_the_curve_runs_over_productive_granules_only(tmp_path):
    """The axis is productive granules, so unproductive rows leave no step.

    Two of the four granules returned nothing. They cannot have covered a cell,
    so dropping them removes flat segments and nothing else: the curve keeps
    its endpoint and loses two points.
    """
    path = write_checkpoint(
        tmp_path / "c.npz",
        [contribution("2018-05-02T00:00:00", 5),
         contribution("2018-05-03T00:00:00", 0),
         contribution("2018-05-04T00:00:00", 0),
         contribution("2018-05-05T00:00:00", 3)],
        [40, 40, 40, 70])

    result = from_checkpoint(path, total_cells=100)

    assert result.curve_length == 2 == result.productive_granules
    assert result.granules_acquired == 4
    assert list(result.cumulative_cells) == [40, 70]
    assert result.final_fraction == pytest.approx(0.70)


def test_a_checkpoint_whose_two_records_disagree_is_refused(tmp_path):
    """An unproductive granule that gained coverage means the records disagree.

    Dropping its row would silently change the curve, so the read fails instead.
    """
    path = write_checkpoint(
        tmp_path / "c.npz",
        [contribution("2018-05-02T00:00:00", 5),
         contribution("2018-05-03T00:00:00", 0)],
        [40, 55])

    with pytest.raises(ValueError, match="no in-box soundings increased coverage"):
        from_checkpoint(path, total_cells=100)


def test_a_checkpoint_whose_records_are_different_lengths_is_refused(tmp_path):
    path = write_checkpoint(tmp_path / "c.npz",
                            [contribution("2018-05-02T00:00:00", 5)],
                            [25, 50, 90])

    with pytest.raises(ValueError, match="must be the same granules in order"):
        from_checkpoint(path, total_cells=100)


def test_per_granule_yield_is_nan_when_a_month_produced_nothing():
    empty = MonthlyYield(month=1, soundings=0, granules=0, acquired=3)

    assert np.isnan(empty.per_granule)
    assert MonthlyYield(2, 300, 2, 2).per_granule == pytest.approx(150.0)


def test_panel_a_is_plotted_against_productive_granules(record):
    """The axis changed from granules processed, so pin the new one.

    Processing order is arbitrary, so a mark placed on an axis of granules
    processed means whatever the loop happened to do first. On productive
    granules a mark at n is a sample of n granules that returned data.
    """
    fig = coverage_figure(record)
    try:
        saturation = fig.axes[0]
        assert saturation.get_xlabel() == "Productive granules (count)"
        assert saturation.get_xlim()[1] >= record.curve_length
    finally:
        plt.close(fig)


def test_only_the_sample_size_is_marked_and_not_the_endpoint(record):
    fig = coverage_figure(record)
    try:
        saturation = fig.axes[0]
        marked = [line for line in saturation.lines
                  if line.get_linestyle() == "None" and line.get_marker() != "None"]
        assert len(marked) == 1
        assert marked[0].get_xdata()[0] < record.curve_length
    finally:
        plt.close(fig)


def test_the_extreme_months_carry_their_per_granule_yield(record):
    """The ratio is the finding, so it has to be on the page.

    Panel (c) plots granule counts, because the count is what makes the
    sounding shortfall mean something. The yield is annotated at the two
    extremes so the factor is readable without a fourth panel.
    """
    fig = coverage_figure(record)
    try:
        annotations = {text.get_text() for text in fig.axes[2].texts}
        yields = [m.per_granule for m in record.monthly if m.granules]
        for extreme in (min(yields), max(yields)):
            assert f"{extreme:,.0f}" in annotations
        assert any("per granule" in text for text in annotations)
    finally:
        plt.close(fig)


def test_a_curve_too_short_to_reach_the_mark_carries_no_mark(record):
    """Better no mark than one clamped onto the endpoint.

    A mark at the reconnaissance sample size says "this is what a sample that
    size reaches". Slid onto the last point of a shorter curve it would say
    the sample reached everything, which is the opposite.
    """
    short = CoverageRecord(cumulative_cells=np.array([10, 40, 55]),
                           monthly=record.monthly, total_cells=100)

    fig = coverage_figure(short)
    try:
        marked = [line for line in fig.axes[0].lines
                  if line.get_linestyle() == "None" and line.get_marker() != "None"]
        assert marked == []
    finally:
        plt.close(fig)
