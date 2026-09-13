"""The capability figure draws the committed artefact and nothing else.

**Why this file exists.** `figures/README.md` records the reason a figure must
not compute its own numbers: a residual-field figure that recomputed its
residuals could have drawn a cloud whose slope disagreed with the number
printed in the caption beside it, and nothing would have caught the
disagreement. This figure carries the claim the paper rests on, so the
correspondence is asserted rather than assumed.

The assertion is literal. The swept curve, the three threshold crossings, the
six per-cell sensitivity points and the two prior-free thresholds are each
compared against the row of the committed CSV they come from. A figure that
evaluated the sensitivity expression itself, interpolated a crossing, or
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
# the capability figure
# --------------------------------------------------------------------------

@pytest.fixture(scope="module")
def capability():
    from src.figures.capability import capability_figure, from_artefact
    sweep = from_artefact()
    return sweep, capability_figure(sweep)


def test_the_sweep_is_the_artefacts_sweep(capability):
    sweep, _ = capability
    table = rows("inversion_dofs_2018.csv")
    swept = [(float(r["quantity"].split(" at ")[1].split(" Tg")[0]),
              float(r["value"]))
             for r in table if r["quantity"].startswith("expected DOFS at ")]
    swept.sort()

    assert list(sweep.totals) == [t for t, _ in swept]
    assert list(sweep.dofs) == [d for _, d in swept]
    assert len(sweep.totals) == 23


def test_the_swept_curve_is_the_only_long_line_drawn(capability):
    sweep, fig = capability
    drawn = [np.asarray(line.get_ydata(), dtype="float64")
             for axis in fig.axes for line in axis.get_lines()
             if len(line.get_ydata()) == len(sweep.totals)]

    assert len(drawn) == 1
    assert np.allclose(drawn[0], sweep.dofs)


def test_the_crossings_are_read_and_not_interpolated(capability):
    """The markers sit at the artefact's bisected crossings.

    `notes/decisions.md` had reported each crossing as the next swept point
    above it -- 0.5 "at about 2 Tg" where the bisection gives 1.767 -- so this
    pins that the figure uses the computed value.
    """
    sweep, _ = capability
    table = {r["quantity"]: float(r["value"])
             for r in rows("inversion_dofs_2018.csv")}

    for threshold in (0.5, 1.0, 2.0):
        key = f"domain prior at which DOFS reaches {threshold:g}"
        assert sweep.crossings[threshold] == table[key]
        # and the crossing must lie at or below the next swept point above
        # the threshold, which is what the earlier prose got wrong: it reported
        # that point as the crossing. "At or below" rather than "below"
        # because the sweep was densified to include 2.5, and DOFS reaches 1
        # there almost exactly.
        above = min(t for t, d in zip(sweep.totals, sweep.dofs)
                    if d >= threshold)
        assert sweep.crossings[threshold] <= above


def test_no_cell_reaches_half_sensitivity_anywhere_in_the_band(capability):
    """The finding panel (b) exists to carry, asserted on the artefact."""
    sweep, _ = capability

    for (name, total), value in sweep.sensitivity.items():
        assert value < 0.5, f"{name} at {total} Tg/y reaches {value}"
    # the maximum at the top of the band is the strongest form of the claim
    hi = max(sweep.band)
    assert sweep.sensitivity[("maximum", hi)] < 0.1


def test_the_prior_free_thresholds_are_the_artefacts_in_gigagrams(capability):
    sweep, _ = capability
    table = {r["quantity"]: float(r["value"])
             for r in rows("inversion_dofs_2018.csv")}

    assert sweep.prior_free_median_gg == pytest.approx(
        1000.0 * table["emission for a = 0.5, median cell"])
    assert sweep.prior_free_best_gg == pytest.approx(
        1000.0 * table["emission for a = 0.5, best-observed cell"])
    # The claim the panel makes, stated exactly, because a first version of
    # this test asserted it too strongly. A median cell's threshold sits above
    # the whole landfill range, so no landfill would half-constrain a typical
    # cell. The best-observed cell's threshold, 49.2 Gg/y, falls *inside* the
    # range: a landfill at the top of it would just reach half-constraint, in
    # the one cell of 926 with the most observation days.
    from src.figures.capability import LANDFILL_GG

    assert sweep.prior_free_median_gg > LANDFILL_GG[1]
    assert LANDFILL_GG[0] < sweep.prior_free_best_gg < LANDFILL_GG[1]
