"""The decay curve draws the committed artefact and nothing else.

**Why this file exists.** `figures/README.md` records the reason a figure must
not compute its own numbers: a residual-field figure that recomputed its
residuals could have drawn a cloud whose slope disagreed with the number
printed in the caption beside it, and nothing would have caught the
disagreement. This figure carries a claim the paper rests on, so the
correspondence is asserted rather than assumed.

The assertion is literal. Every y value of every line in the rendered figure is
compared against the column of the committed CSV it is supposed to come from,
elementwise. A figure that recomputed a fold, interpolated a crossing, or
rescaled a threshold would fail here rather than in a reader's understanding.
"""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

PROCESSED = REPO / "data" / "processed"


def rows(name: str) -> list[dict]:
    with (PROCESSED / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


# --------------------------------------------------------------------------
# the decay curve, whose figure module may not recompute a fold
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def decay():
    from src.figures.buffered_decay import decay_figure, from_artefact
    curves = from_artefact()
    return curves, decay_figure(curves)


def test_the_decay_reader_returns_every_curve_the_artefact_holds(decay):
    curves, _ = decay
    table = rows("buffered_loo_2018.csv")

    assert set(curves) == {(r["field"], r["model"]) for r in table}
    assert len(curves) == 6
    for curve in curves.values():
        assert len(curve.radii) == 10


def test_every_decay_line_is_a_column_of_the_artefact(decay):
    """Each drawn line matches one artefact column elementwise."""
    curves, fig = decay
    table = rows("buffered_loo_2018.csv")

    def column(field, model, name):
        picked = sorted((r for r in table
                         if r["field"] == field and r["model"] == model),
                        key=lambda r: float(r["radius_km"]))
        return [float(r[name]) for r in picked]

    # panel (a) holds three raw-metric lines, panel (b) four above-constant.
    expected = [column("operational", m, "held_out_r2") for m in (
        "spatial null (queen neighbour mean)", "OLS impervious fraction",
        "constant (training mean)")]
    expected += [column(f, m, "r2_above_constant")
                 for m in ("spatial null (queen neighbour mean)",
                           "OLS impervious fraction")
                 for f in ("operational", "blended")]

    drawn = []
    for axis in fig.axes:
        for line in axis.get_lines():
            y = np.asarray(line.get_ydata(), dtype="float64")
            if len(y) == 10:
                drawn.append(list(y))

    assert len(drawn) == len(expected), (
        f"{len(drawn)} ten-point lines drawn, {len(expected)} expected")
    for series in expected:
        assert any(np.allclose(series, d) for d in drawn), (
            f"no drawn line matches {series[:3]}...")


def test_the_province_out_marker_comes_from_the_other_scheme(decay):
    """The horizontal reference is the baseline table's value, not this one's."""
    from src.figures.buffered_decay import _province_out_null

    value = _province_out_null()
    table = rows("baseline_results_2018.csv")
    wanted = [r for r in table
              if r["model"] == "spatial null (queen neighbour mean)"
              and r["scheme"] == "leave-one-province-out"
              and r["weighting"] == "unweighted"]

    assert len(wanted) == 1
    assert value == float(wanted[0]["held_out_r2"])
    # And it must fall inside the buffered curve's own range at the radii the
    # figure shades, which is the bracketing claim the panel makes.
    curves, _ = decay
    buffered = dict(zip(curves[("operational",
                                "spatial null (queen neighbour mean)")].radii,
                        curves[("operational",
                                "spatial null (queen neighbour mean)")].held_out))
    assert buffered[200.0] <= value <= buffered[150.0]


def test_the_shaded_band_is_the_bracketing_interval_and_not_an_assumption(decay):
    """The band's meaning changed once and must not drift back.

    It was first shaded as the distance from a held-out province's interior to
    the nearest training cell, which this repository does not measure. It is
    now derived: the two adjacent swept radii whose held-out R squared straddle
    the leave-one-province-out value. This asserts the derivation against the
    artefact, and that the fallback constant recorded in the module still
    matches, so a re-run of the curve that moved the crossing fails here
    instead of relabelling the band.
    """
    from src.figures import buffered_decay

    curves, figure = decay
    value = buffered_decay._province_out_null()
    curve = curves[("operational", "spatial null (queen neighbour mean)")]
    band = buffered_decay._bracket(curve, value)

    assert band == buffered_decay.BRACKET_FALLBACK_KM

    # and it really does straddle: the artefact's own two rows, by radius.
    by_radius = dict(zip(curve.radii, curve.held_out))
    assert by_radius[band[1]] <= value <= by_radius[band[0]]

    # The band is drawn from the derivation, not from the constant.
    spans = [p for p in figure.axes[0].patches
             if p.get_window_extent().width > 1]
    assert len(spans) == 1, "expected exactly one shaded span on panel (a)"
    # axvspan returns a Rectangle on a blended transform: its path is the unit
    # square and the x placement is in data coordinates on the rectangle.
    span = spans[0]
    assert (round(float(span.get_x()), 6),
            round(float(span.get_x() + span.get_width()), 6)) == band
