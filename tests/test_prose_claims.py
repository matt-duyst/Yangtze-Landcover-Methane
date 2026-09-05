"""Numeric claims in the prose are checked against the artefacts they came from.

Offline, reading only committed files.

The third drift class. Recipes drifting from artefacts is caught by
`tests/test_recipes.py`. Artefacts moving under the sentences that quote them
was caught by nobody: eight figures in README.md and ERRATA.md went stale when
the extent re-run moved the tables, and were found by a manual sweep before a
push. `data/processed/README.md` had twenty more that the sweep did not reach.

A claim is brought under the check by marking it where it lives, in the
sentence, with an HTML comment naming the quantity:

    There are 926<!--#grid.rows--> of them and fifteen columns.

The marker renders as nothing and travels with its sentence, so it cannot drift
from the claim the way a table of claims maintained beside the prose would.
That parallel-table failure is the one this repository already had, in the
README regeneration table, so it is not repeated here.

**The mechanism is deliberately incomplete, and errs toward false negatives.**
An unmarked number is unchecked. Checking every number in the prose would fire
on DOIs, byte counts, years, published figures from cited papers, and the whole
historical record in `notes/decisions.md` -- thousands of them, most of which
must never be "corrected". A check that noisy is not a check with a high false
positive rate; it is a check that gets turned off. So marking is a judgement
made once, at writing time, and `test_the_unchecked_surface_is_reported`
records how much prose is not covered rather than letting the gap go unstated.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.verify_claims import (  # noqa: E402
    CLAIM,
    QUANTITIES,
    SCANNED,
    agrees,
    check,
    find_claims,
    unmarked,
)

RESULTS = check()


def test_every_marked_claim_matches_the_data():
    """The whole point. A regenerated table that moves a value fails here."""
    stale = [f"{r['file']}:{r['line']} {r['quantity']} says {r['written']}, "
             f"data says {r['actual']}" for r in RESULTS if not r["ok"]]

    assert stale == []


def test_some_claims_are_actually_marked():
    """Guards against the check passing because it found nothing.

    A verification that silently scans zero items is indistinguishable from one
    that passes, which is a failure this project has already had once in a
    credential sweep.
    """
    assert len(RESULTS) >= 30


def test_every_marker_names_a_quantity_that_can_be_computed():
    for result in RESULTS:
        assert result["quantity"] in QUANTITIES, \
            f"{result['file']}:{result['line']} names unknown {result['quantity']}"


def test_every_quantity_computes_to_a_number():
    for name, compute in QUANTITIES.items():
        value = compute()
        assert isinstance(value, (int, float)), name


def test_markers_are_invisible_in_rendered_markdown():
    """An HTML comment renders as nothing, so a reader sees only the number.

    A README full of visible machinery would be worse than a stale figure, so
    the marker form is part of the design rather than an implementation detail.
    """
    for name in SCANNED:
        text = (REPO / name).read_text(encoding="utf-8")
        for match in CLAIM.finditer(text):
            marker = match.group(0)[len(match.group(1)):].lstrip()
            assert marker.startswith("<!--") and marker.endswith("-->"), marker


def test_the_decision_log_is_excluded_on_purpose():
    """Its figures are as-measured-at-the-time and must not be rewritten.

    `notes/decisions.md` records what was believed and measured when each
    decision was taken. A mechanism that updated those numbers to the current
    values would destroy exactly what the file exists to preserve.
    """
    assert "notes/decisions.md" not in SCANNED

    log = (REPO / "notes" / "decisions.md").read_text(encoding="utf-8")
    assert not CLAIM.search(log), "the decision log has acquired claim markers"


def test_a_historical_figure_in_the_prose_is_left_unmarked():
    """data/processed/README.md keeps one superseded set of figures on purpose.

    It states what the composite reported before the extent reconciliation.
    That sentence must stay as written, so it carries no marker and the check
    leaves it alone.
    """
    text = (REPO / "data" / "processed" / "README.md").read_text(encoding="utf-8")
    line = next(l for l in text.splitlines() if "They were 222 granules" in l)

    assert "927" in line and "110,928" in line
    assert "<!--#" not in line


# --------------------------------------------------------------------------
# the mechanism has to actually catch something
# --------------------------------------------------------------------------

def test_the_check_catches_a_number_that_has_gone_stale(tmp_path, monkeypatch):
    """Proves the check fails on drift rather than passing vacuously."""
    import scripts.verify_claims as vc

    doc = tmp_path / "prose.md"
    doc.write_text("The grid holds 999<!--#grid.rows--> rows.\n", encoding="utf-8")
    monkeypatch.setattr(vc, "REPO", tmp_path)

    results = vc.check(paths=("prose.md",))

    assert len(results) == 1
    assert results[0]["ok"] is False
    assert results[0]["written"] == "999"


def test_the_check_accepts_the_number_when_it_is_right(tmp_path, monkeypatch):
    import scripts.verify_claims as vc

    correct = QUANTITIES["grid.rows"]()
    doc = tmp_path / "prose.md"
    doc.write_text(f"The grid holds {correct}<!--#grid.rows--> rows.\n",
                   encoding="utf-8")
    monkeypatch.setattr(vc, "REPO", tmp_path)

    assert vc.check(paths=("prose.md",))[0]["ok"] is True


def test_an_unknown_quantity_is_reported_rather_than_ignored(tmp_path, monkeypatch):
    import scripts.verify_claims as vc

    doc = tmp_path / "prose.md"
    doc.write_text("Something 12<!--#not.a.quantity--> here.\n", encoding="utf-8")
    monkeypatch.setattr(vc, "REPO", tmp_path)

    result = vc.check(paths=("prose.md",))[0]
    assert result["ok"] is False
    assert result["reason"] == "unknown quantity"


def test_rounding_in_the_prose_is_not_treated_as_drift():
    """The sentence decides its own precision.

    "90.52 percent" is checked to two decimals; a value of 90.5234 agrees with
    it. Without this the check would fire on every rounded figure, which is the
    false-positive rate that gets a check disabled.
    """
    assert agrees("90.52", 90.5234)
    assert agrees("926", 926)
    assert agrees("110,920", 110920)
    assert not agrees("90.52", 90.61)
    assert not agrees("926", 927)


def test_a_number_without_a_marker_is_not_claimed_to_be_checked():
    text = "The year was 2018 and the DOI ends 415324.018.\n"

    assert find_claims(text) == []


def test_the_unchecked_surface_is_reported():
    """The gap is stated, not assumed away."""
    counts = unmarked()

    assert set(counts) == set(SCANNED)
    assert all(isinstance(v, int) for v in counts.values())
