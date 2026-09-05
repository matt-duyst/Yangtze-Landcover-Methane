"""Tests for the committed albedo-correction result.

Reads data/processed/albedo_correction_2018.csv and the analysis grid, both
committed, so these run in every clone.

What is pinned is the shape of the result rather than its exact values: that
both methane variables and the correction between them are reported against
both albedo bands at both weightings, that the correction is not identically
zero, and that the corrected variable's residual albedo sensitivity is large.
The last is the finding, and if a later change makes it small this should fail
and be argued with rather than quietly accepted.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "data" / "processed" / "albedo_correction_2018.csv"
GRID = REPO / "data" / "processed" / "analysis_grid_2018.csv"

SERIES = {"raw retrieval", "bias corrected", "the correction itself",
          "deseasonalised"}
ALBEDOS = {"surface_albedo_SWIR", "surface_albedo_NIR"}
WEIGHTINGS = {"unweighted", "by sounding count"}


def rows():
    return list(csv.DictReader(open(RESULTS, newline="")))


def find(albedo, series, weighting):
    for record in rows():
        if (record["albedo"] == albedo and record["series"] == series
                and record["weighting"] == weighting):
            return record
    raise AssertionError(f"no row for {albedo} / {series} / {weighting}")


def test_every_series_is_reported_against_both_bands_at_both_weightings():
    records = rows()
    assert len(records) == len(SERIES) * len(ALBEDOS) * len(WEIGHTINGS) == 16
    seen = {(r["albedo"], r["series"], r["weighting"]) for r in records}
    assert seen == {(a, s, w) for a in ALBEDOS for s in SERIES for w in WEIGHTINGS}
    for record in records:
        assert int(record["n"]) == 926


def test_the_correction_is_not_zero_and_is_positive_on_average():
    """Both variables are gridded, and they are not the same variable."""
    grid = list(csv.DictReader(open(GRID, newline="")))
    corrected = np.array([float(r["ch4_bias_corrected_ppb"]) for r in grid])
    raw = np.array([float(r["ch4_raw_ppb"]) for r in grid])
    delta = corrected - raw
    assert (delta != 0).all(), "the correction changes every covered cell"
    assert delta.mean() == pytest.approx(11.64, abs=0.05)
    assert delta.min() > 0, "the correction is positive everywhere here"


def test_the_corrected_variable_retains_a_large_albedo_sensitivity():
    """The finding: the operational correction does not remove the dependence."""
    for weighting in WEIGHTINGS:
        record = find("surface_albedo_SWIR", "bias corrected", weighting)
        slope = float(record["slope_ppb_per_unit_albedo"])
        assert slope > 100.0, "residual sensitivity is hundreds of ppb per unit"
        assert float(record["r2"]) > 0.3
        assert abs(slope) > 20 * float(record["standard_error"]), \
            "and it is nowhere near zero"


def test_the_correction_reduces_the_swir_slope_but_does_not_remove_it():
    before = float(find("surface_albedo_SWIR", "raw retrieval",
                        "unweighted")["slope_ppb_per_unit_albedo"])
    after = float(find("surface_albedo_SWIR", "bias corrected",
                       "unweighted")["slope_ppb_per_unit_albedo"])
    assert 0 < after < before, "reduced"
    assert after > 0.5 * before, "but only slightly, unweighted"


def test_the_correction_does_not_reduce_the_nir_slope_unweighted():
    """Against NIR the corrected variable is worse, which is worth pinning."""
    before = float(find("surface_albedo_NIR", "raw retrieval",
                        "unweighted")["slope_ppb_per_unit_albedo"])
    after = float(find("surface_albedo_NIR", "bias corrected",
                       "unweighted")["slope_ppb_per_unit_albedo"])
    assert after > before


def test_the_correction_itself_is_only_weakly_related_to_swir_albedo_unweighted():
    """An albedo correction should be a function of albedo. Unweighted it is not."""
    record = find("surface_albedo_SWIR", "the correction itself", "unweighted")
    assert float(record["r2"]) < 0.01
    assert abs(float(record["slope_ppb_per_unit_albedo"])) < 2 * float(
        record["standard_error"]), "indistinguishable from no relationship"


def test_the_correction_is_clearly_related_to_swir_albedo_when_weighted():
    record = find("surface_albedo_SWIR", "the correction itself",
                  "by sounding count")
    assert float(record["slope_ppb_per_unit_albedo"]) < -20.0, \
        "larger correction over darker surfaces, the documented direction"
    assert float(record["r2"]) > 0.2
