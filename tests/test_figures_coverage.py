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
        cumulative_cells=np.array([10, 40, 55, 60, 61]),
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
    path = write_checkpoint(tmp_path / "c.npz",
                            [contribution("2018-05-02T00:00:00", 5)],
                            [25, 50, 90])

    result = from_checkpoint(path, total_cells=100)

    assert result.granules_processed == 3
    assert result.fraction_at(1) == pytest.approx(0.25)
    assert result.final_fraction == pytest.approx(0.90)


def test_per_granule_yield_is_nan_when_a_month_produced_nothing():
    empty = MonthlyYield(month=1, soundings=0, granules=0, acquired=3)

    assert np.isnan(empty.per_granule)
    assert MonthlyYield(2, 300, 2, 2).per_granule == pytest.approx(150.0)
