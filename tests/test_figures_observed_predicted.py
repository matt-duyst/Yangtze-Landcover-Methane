"""Tests for the observed-against-predicted diagnostic figure.

Offline, reading only committed artefacts. The figure is built and asserted on
in memory; nothing is written.

Four things carry this figure and each would fail silently without a test.

**The predictions are held out.** In-sample fitted values against observed are
the most flattering mistake available in a figure like this one, and they look
entirely plausible: on this table the spatial null's in-sample R squared is
0.685 against a held-out 0.332, so a figure drawing the first would show a
smoothness bar twice the bar it is. The committed predictions are asserted to
reproduce the committed metrics, which is the only cheap way to tell one from
the other after the fact.

**The panels share one sample.** `baselines.py` records that results on
different samples must not be compared without saying so, and four panels side
by side is a comparison whatever a caption says.

**The panels share one pair of axis limits.** Autoscaled, a model predicting a
1.4 ppb range would fill the same box as one predicting 74, and the flatness
that is the finding would be invisible.

**The weight is drawn.** A cell's observed value is the mean of between 1 and
410 soundings and a scatter that drew them alike would misrepresent the fit.
"""

from __future__ import annotations

import csv

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from src.figures import fields, style
from src.figures import observed_predicted as op
from src.figures.observed_predicted import observed_predicted_figure


@pytest.fixture(scope="module")
def figure():
    fig = observed_predicted_figure()
    yield fig
    plt.close(fig)


def test_the_figure_function_returns_a_figure_and_writes_nothing(tmp_path):
    before = set(tmp_path.iterdir())

    fig = observed_predicted_figure()
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# the predictions are held out
# --------------------------------------------------------------------------

def test_the_committed_predictions_reproduce_the_committed_metrics():
    """Which is what says these are the held-out values and not the fitted ones."""
    from src.model.baselines import Metrics

    predictions = op.load_predictions()
    metrics = op.load_metrics()
    for name, _ in op.PANELS:
        data = predictions[name]
        weight = np.ones(data["observed"].size)
        recomputed = Metrics.of(data["observed"], data["predicted"], weight)
        reference = metrics[(name, op.SCHEME, op.WEIGHTING)]
        assert recomputed.r2 == pytest.approx(reference["r2"], abs=5e-4), name
        assert recomputed.rmse == pytest.approx(reference["rmse"], abs=5e-4), name


def test_the_in_sample_metrics_would_have_been_flattering_and_are_not_drawn():
    """The mistake this figure had available. Asserted so it stays available."""
    in_sample, held_out = {}, {}
    with op.RESULTS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row["scheme"] != op.SCHEME or row["weighting"] != op.WEIGHTING:
                continue
            in_sample[row["model"]] = float(row["in_sample_r2"])
            held_out[row["model"]] = float(row["held_out_r2"])

    null = "spatial null (queen neighbour mean)"
    assert in_sample[null] > 2 * held_out[null]
    for name, _ in op.PANELS:
        assert in_sample[name] >= held_out[name] - 1e-9, name


def test_every_cell_is_predicted_exactly_once_per_model():
    """Folds must partition the sample, or a cell is drawn twice."""
    counts = {}
    with op.PREDICTIONS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row["model"], row["row"], row["col"])
            counts[key] = counts.get(key, 0) + 1

    assert set(counts.values()) == {1}
    assert len(counts) == 4 * 926


# --------------------------------------------------------------------------
# one sample, one scheme, one pair of limits
# --------------------------------------------------------------------------

def test_every_panel_runs_on_the_same_sample():
    """The rice models run on 531 cells and are deliberately absent."""
    metrics = op.load_metrics()
    sizes = {metrics[(name, op.SCHEME, op.WEIGHTING)]["n"]
             for name, _ in op.PANELS}

    assert sizes == {926}
    for name, _ in op.PANELS:
        assert "[rice sample]" not in name


def test_the_four_panels_span_the_range_the_table_holds_on_that_sample():
    """Chosen against the table, so the panels are not four similar models."""
    metrics = op.load_metrics()
    values = [metrics[(name, op.SCHEME, op.WEIGHTING)]["r2"]
              for name, _ in op.PANELS]

    assert values == sorted(values)
    assert values[0] < 0.0 < values[-1]
    assert values[-1] - values[0] > 0.6


def test_all_four_panels_share_one_pair_of_axis_limits(figure):
    panels = figure.axes[:4]
    limits = {(tuple(np.round(ax.get_xlim(), 6)),
               tuple(np.round(ax.get_ylim(), 6))) for ax in panels}

    assert len(limits) == 1
    x, y = limits.pop()
    assert x == y                      # the 1:1 line has to be the diagonal
    for ax in panels:
        assert ax.get_aspect() == 1.0


def test_the_limits_come_from_the_observed_field_and_hold_every_model():
    predictions = op.load_predictions()
    low, high = op.shared_limits(predictions)

    for name, _ in op.PANELS:
        data = predictions[name]
        assert low <= data["observed"].min() and data["observed"].max() <= high
        assert low <= data["predicted"].min()
        assert data["predicted"].max() <= high


def test_the_land_cover_field_is_flatter_than_the_observed_one():
    """The finding, as a number rather than as a shape."""
    predictions = op.load_predictions()
    observed = predictions["constant (global mean)"]["observed"]
    impervious = predictions["OLS impervious_fraction"]["predicted"]
    null = predictions["spatial null (queen neighbour mean)"]["predicted"]

    observed_span = float(observed.max() - observed.min())
    assert float(impervious.max() - impervious.min()) < 0.5 * observed_span
    assert float(null.max() - null.min()) > float(impervious.max()
                                                  - impervious.min())


def test_a_constant_model_produces_almost_no_range_at_all():
    predictions = op.load_predictions()
    constant = predictions["constant (global mean)"]["predicted"]

    # Not exactly constant: each fold's fit is the mean of its own training
    # rows, so five folds give five values.
    assert float(constant.max() - constant.min()) < 3.0
    assert np.unique(np.round(constant, 4)).size <= 5


# --------------------------------------------------------------------------
# weight is drawn
# --------------------------------------------------------------------------

def test_mark_area_carries_the_sounding_count_on_the_composite_classes():
    areas = op.mark_areas([1, 3, 4, 10, 11, 31, 32, 99, 100, 315, 316, 410])

    assert list(areas[:2]) == [op.MARK_AREAS[0]] * 2
    assert list(areas[-2:]) == [op.MARK_AREAS[-1]] * 2
    assert list(areas) == sorted(areas)
    assert len(op.MARK_AREAS) == len(fields.COUNT_LABELS)


def test_the_scatter_marks_are_sized_and_not_all_alike(figure):
    collection = figure.axes[0].collections[0]
    sizes = np.unique(collection.get_sizes())

    assert sizes.size > 1
    assert set(sizes) <= set(op.MARK_AREAS)


def test_the_counts_the_marks_encode_span_the_documented_range():
    predictions = op.load_predictions()
    counts = predictions["constant (global mean)"]["count"]

    assert int(counts.min()) == 1
    assert int(counts.max()) == 410


# --------------------------------------------------------------------------
# the summary panel
# --------------------------------------------------------------------------

def test_the_summary_reports_every_scheme_and_weighting():
    metrics = op.load_metrics()
    rows = op.summary_rows(metrics)

    assert len(rows) == len(op.PANELS)
    for entry in rows:
        assert set(entry["values"]) == set(op.COMBINATIONS)


def test_the_spatial_null_is_only_a_bar_under_spatial_blocks():
    """Which is why the panels draw that scheme, and the summary says so.

    Under leave-one-province-out the null is negative, so it explains none of
    the held-out variance and there is no diagonal-tracking cloud to set the
    flat ones against. It does still beat the constant there, which an earlier
    draft of this test and of the module docstring had backwards.
    """
    metrics = op.load_metrics()
    null = "spatial null (queen neighbour mean)"
    constant = "constant (global mean)"

    blocks = metrics[(null, "spatial blocks", "unweighted")]["r2"]
    provinces = metrics[(null, "leave-one-province-out", "unweighted")]["r2"]
    assert blocks > 0.3
    assert provinces < 0.0
    assert provinces > metrics[(constant, "leave-one-province-out",
                                "unweighted")]["r2"]


def test_no_land_cover_model_beats_the_spatial_null_under_weighting():
    """The recorded claim, which is about land cover and not about everything."""
    metrics = op.load_metrics()
    weighted = "by sounding count"
    for scheme in ("spatial blocks", "leave-one-province-out"):
        null = metrics[("spatial null (queen neighbour mean)", scheme,
                        weighted)]["r2"]
        land = metrics[("OLS impervious_fraction", scheme, weighted)]["r2"]
        assert land < null, scheme


def test_the_summary_gives_colour_to_scheme_and_fill_to_weighting(figure):
    """Two different things, two channels; the same rule panel (c) of the
    urban figure follows for lines."""
    summary = figure.axes[4]
    marks = [line for line in summary.lines if line.get_marker() == "o"]

    assert len(marks) == len(op.PANELS) * len(op.COMBINATIONS)
    colours = {mark.get_markeredgecolor() for mark in marks}
    assert len(colours) == 2
    faces = {str(mark.get_markerfacecolor()) for mark in marks}
    assert style.role("page") in faces      # the weighted fits are open


# --------------------------------------------------------------------------
# layout and what the figure says
# --------------------------------------------------------------------------

def test_the_layout_closes_across_the_page(figure):
    total = (op.LEFT_CM + 2 * op.PANEL_CM + op.PANEL_GAP_CM
             + op.COLUMN_GAP_CM + op.SUMMARY_CM + op.RIGHT_CM)

    assert total == pytest.approx(op.FIG_WIDTH_CM, abs=1e-9)
    assert figure.get_figwidth() / style.CM == pytest.approx(op.FIG_WIDTH_CM)


def test_every_panel_sits_inside_the_figure(figure):
    for index, ax in enumerate(figure.axes):
        box = ax.get_position()
        assert 0.0 <= box.x0 and box.x1 <= 1.0, index
        assert 0.0 <= box.y0 and box.y1 <= 1.0, index


def test_each_panel_reports_its_own_numbers(figure):
    for index in range(4):
        text = " ".join(t.get_text() for t in figure.axes[index].texts)
        assert "held-out" in text and "RMSE" in text


def test_the_figure_says_the_predictions_are_held_out(figure):
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "out of fold" in flat
    assert "in-sample" in flat
    assert "share one pair of axis limits" in flat


def test_no_panel_is_titled_as_a_prediction_of_methane(figure):
    """The framing constraint. These are model fields, not methane forecasts."""
    titles = [t.get_text() for t in figure.texts if t.get_text().startswith("(")]

    assert len(titles) == 5
    for title in titles:
        assert "predict" not in title.lower()
    for index in range(4):
        assert figure.axes[index].get_ylabel() in ("", "Model field (ppb)")


def test_the_figure_points_at_the_errata_for_what_it_does_not_claim(figure):
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "ERRATA.md 7.1" in flat
    assert "ERRATA.md 7.4" in flat
