"""Tests for the committed alternative-predictor result.

Reads data/processed/alternative_predictors_2018.csv and
predictor_comparison_2018.csv, both committed.

The result pinned here is that the negative finding survives independently
built predictors. That is the whole point of the exercise: measurement error in
a predictor attenuates an association toward zero, so a negative finding is only
worth stating if it holds with better predictors too.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
BASELINES = REPO / "data" / "processed" / "alternative_predictors_2018.csv"
COMPARISON = REPO / "data" / "processed" / "predictor_comparison_2018.csv"

PAIRS = {"gaia+nesdc", "gisa+nesdc", "gaia+glorice", "gisa+glorice"}


def baselines():
    return list(csv.DictReader(open(BASELINES, newline="")))


def comparison():
    return list(csv.DictReader(open(COMPARISON, newline="")))


def test_all_four_predictor_pairs_are_present():
    rows = baselines()
    assert {r["predictors"] for r in rows} == PAIRS
    counts = {p: sum(1 for r in rows if r["predictors"] == p) for p in PAIRS}
    assert counts["gaia+nesdc"] == counts["gisa+nesdc"]
    assert counts["gaia+glorice"] == counts["gisa+glorice"]


def test_nothing_beats_the_spatial_null_under_inverse_variance_weighting():
    """The finding, on every predictor pair. If this fails, the claim changed."""
    offenders = [r for r in baselines()
                 if r["weighting"] == "by sounding count"
                 and r["beats_spatial_null"] == "yes"]
    assert offenders == [], f"land cover beat the null when weighted: {offenders}"


def test_the_unweighted_exceptions_are_few_and_small():
    rows = [r for r in baselines()
            if r["weighting"] == "unweighted" and r["beats_spatial_null"] == "yes"]
    assert len(rows) == 8
    assert {r["predictors"] for r in rows} == PAIRS, \
        "the exceptions appear on every pair, so they are not a property of one"


def test_the_glorice_grid_covers_more_cells_than_the_nesdc_one():
    """NaN means no rice in GloRice and an unassessed cell in NESDC."""
    rows = comparison()
    nesdc = {int(r["n"]) for r in rows if r["predictor"] == "NESDC"}
    glorice = {int(r["n"]) for r in rows if r["predictor"] == "GloRice"}
    assert nesdc == {532}
    assert glorice == {927}


def test_the_two_urban_products_are_reported_on_the_same_cells():
    rows = comparison()
    for name in ("GAIA", "GISA"):
        assert {int(r["n"]) for r in rows if r["predictor"] == name} == {927}


def test_the_rice_association_does_not_survive_albedo_control_on_nesdc():
    for record in comparison():
        if record["predictor"] == "NESDC":
            assert abs(float(record["partial_pearson_given_albedo"])) < 0.10


def test_every_comparison_row_reports_both_methane_fields_and_both_weightings():
    rows = comparison()
    seen = {(r["predictor"], r["methane_field"], r["weighting"]) for r in rows}
    assert len(seen) == len(rows) == 16
    assert {r["methane_field"] for r in rows} == {"bias corrected", "raw"}
    assert {r["weighting"] for r in rows} == {"unweighted", "by sounding count"}
