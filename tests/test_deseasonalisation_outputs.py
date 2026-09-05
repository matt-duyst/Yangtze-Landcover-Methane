"""Tests for the committed deseasonalisation result.

Reads data/processed/deseasonalisation_2018.csv, the deseasonalised field, and
the baseline table computed on it. All committed, so these run in every clone.

The result these pin is a negative one: removing a shared seasonal cycle did
not remove the sampling artefact. That is worth pinning precisely because it is
the kind of finding a later change could quietly reverse into a positive one,
and if it does the change should have to argue with a test.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
COMPARISON = REPO / "data" / "processed" / "deseasonalisation_2018.csv"
FIELD = REPO / "data" / "processed" / "methane_deseasonalised_2018.csv"
RAW_BASELINES = REPO / "data" / "processed" / "baseline_results_2018.csv"
MU_BASELINES = REPO / "data" / "processed" / "baseline_results_deseasonalised_2018.csv"

SAMPLING = "sampling composition"
LAND = "land cover"


def rows(path):
    return list(csv.DictReader(open(path, newline="")))


def find(records, predictor, weighting):
    for record in records:
        if record["predictor"] == predictor and record["weighting"] == weighting:
            return record
    raise AssertionError(f"no row for {predictor} at {weighting}")


# --------------------------------------------------------------------------
# the field itself
# --------------------------------------------------------------------------

def test_the_deseasonalised_field_covers_the_927_observed_cells():
    records = rows(FIELD)
    assert len(records) == 1023
    observed = [r for r in records if int(r["sounding_count"]) > 0]
    assert len(observed) == 926
    for record in observed:
        assert record["ch4_deseasonalised_ppb"] != ""
        assert record["mean_day_of_year"] != ""
    for record in records:
        if int(record["sounding_count"]) == 0:
            assert record["ch4_deseasonalised_ppb"] == ""


def test_the_composite_covers_only_part_of_the_year():
    """No soundings before day 120, so the cycle is extrapolated over a third."""
    days = np.array([float(r["mean_day_of_year"]) for r in rows(FIELD)
                     if r["mean_day_of_year"] != ""])
    assert days.min() > 119.0, "the record starts at the end of April"
    assert days.max() < 366.0
    assert days.max() - days.min() > 200.0, \
        "cells differ by more than two hundred days in their mean sampling date"


def test_cells_sampled_on_one_date_are_flagged():
    records = [r for r in rows(FIELD) if int(r["sounding_count"]) > 0]
    flagged = [r for r in records if r["poorly_identified"] == "1"]
    assert len(flagged) == 66
    for record in flagged:
        assert float(record["day_of_year_sd"]) < 15.0
    unflagged = [r for r in records if r["poorly_identified"] == "0"]
    for record in unflagged:
        assert float(record["day_of_year_sd"]) >= 15.0


# --------------------------------------------------------------------------
# the finding
# --------------------------------------------------------------------------

def test_deseasonalising_did_not_remove_the_sampling_association():
    """The negative result. If a change reverses this, it fails here first."""
    records = rows(COMPARISON)
    for weighting in ("unweighted", "by sounding count"):
        record = find(records, "mean_day_of_year", weighting)
        before, after = float(record["raw_pearson"]), float(record["mu_pearson"])
        assert before > 0.6, "the raw field is strongly tied to sampling date"
        assert after > 0.5, "and the corrected field still is"
        assert abs(after) > 0.7 * abs(before), \
            "the association kept most of its magnitude"


def test_the_land_cover_associations_are_unchanged_by_deseasonalising():
    records = rows(COMPARISON)
    for weighting in ("unweighted", "by sounding count"):
        for predictor in ("impervious_fraction", "rice_fraction_single"):
            record = find(records, predictor, weighting)
            change = abs(float(record["pearson_change"]))
            assert change < 0.05, f"{predictor} moved by {change}"


def test_every_relationship_is_reported_on_both_fields_and_both_weightings():
    records = rows(COMPARISON)
    assert {r["weighting"] for r in records} == {"unweighted", "by sounding count"}
    per = {}
    for record in records:
        per.setdefault(record["predictor"], set()).add(record["weighting"])
    for predictor, weightings in per.items():
        assert len(weightings) == 2, predictor
    assert {r["group"] for r in records} == {
        SAMPLING, "retrieval and meteorology", LAND}


# --------------------------------------------------------------------------
# the baselines on the corrected field
# --------------------------------------------------------------------------

def baseline(path, model, scheme, weighting):
    for record in rows(path):
        if (record["model"] == model and record["scheme"] == scheme
                and record["weighting"] == weighting):
            return record
    raise AssertionError(f"no row for {model}")


def test_the_two_baseline_tables_cover_the_same_models():
    raw = {(r["model"], r["scheme"], r["weighting"]) for r in rows(RAW_BASELINES)}
    mu = {(r["model"], r["scheme"], r["weighting"]) for r in rows(MU_BASELINES)}
    assert raw == mu
    assert len(raw) == 88


def test_sampling_composition_still_predicts_the_corrected_field():
    """Said plainly rather than explained: the correction did not work."""
    record = baseline(MU_BASELINES, "OLS sampling composition (when observed)",
                      "spatial blocks", "unweighted")
    null = baseline(MU_BASELINES, "spatial null (queen neighbour mean)",
                    "spatial blocks", "unweighted")
    assert float(record["held_out_r2"]) > 0.4
    assert float(record["held_out_rmse_ppb"]) < float(null["held_out_rmse_ppb"]), \
        "a variable with no physical content still beats the smoothness bar"


def test_land_cover_still_does_not_beat_the_spatial_null_on_the_corrected_field():
    for weighting in ("unweighted", "by sounding count"):
        null = baseline(MU_BASELINES, "spatial null (queen neighbour mean)",
                        "spatial blocks", weighting)
        land = baseline(MU_BASELINES, "OLS impervious_fraction",
                        "spatial blocks", weighting)
        assert float(land["held_out_rmse_ppb"]) > float(null["held_out_rmse_ppb"])


def test_the_r_squared_of_every_working_model_is_essentially_unchanged():
    """Deseasonalising rescaled the target and moved almost nothing else.

    Restricted to models that are not already failing. A model at R squared
    -0.75 is predicting worse than the held-out mean and its R squared is not a
    meaningful scale to compare small movements on; three such models drift by
    up to 0.17 between the two fields and that says nothing about either.
    """
    moved, examined = [], 0
    for record in rows(RAW_BASELINES):
        mu = baseline(MU_BASELINES, record["model"], record["scheme"],
                      record["weighting"])
        before, after = float(record["held_out_r2"]), float(mu["held_out_r2"])
        if min(before, after) < -0.5:
            continue
        examined += 1
        if abs(after - before) > 0.15:
            moved.append((record["model"], record["scheme"],
                          record["weighting"], before, after))
    assert examined > 70, "most models should be scoreable on both fields"
    assert not moved, f"models whose R2 moved materially: {moved}"
