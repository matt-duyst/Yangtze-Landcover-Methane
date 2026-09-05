"""Tests for the committed albedo confounder result.

Reads data/processed/albedo_confounder_2018.csv, which is committed, so these
run in every clone.

What is pinned here is the structure of the argument rather than its numbers.
A confounding path needs both legs open, the controlled association has to be
computed on the same cells as the raw one, and both weightings have to be
present so a reader cannot be shown only the one that agrees with the
conclusion. The one number pinned is that the impervious association does not
survive the control, because that is the finding and it should fail loudly if a
later change moves it.
"""

from __future__ import annotations

import csv
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "data" / "processed" / "albedo_confounder_2018.csv"

WEIGHTINGS = {"unweighted", "by sounding count"}
ALBEDO = "surface_albedo_SWIR"


def rows():
    return list(csv.DictReader(open(RESULTS, newline="")))


def find(records, relationship, controlling_for, weighting):
    for record in records:
        if (record["relationship"] == relationship
                and record["controlling_for"] == controlling_for
                and record["weighting"] == weighting):
            return record
    raise AssertionError(f"no row for {relationship} | {controlling_for}")


def test_both_weightings_are_reported():
    records = rows()
    assert {r["weighting"] for r in records} == WEIGHTINGS
    per = {w: sum(1 for r in records if r["weighting"] == w) for w in WEIGHTINGS}
    assert per["unweighted"] == per["by sounding count"], \
        "the two weightings must cover the same relationships"


def test_every_row_states_its_sample_size():
    for record in rows():
        assert int(record["n"]) in (926, 531)


def test_the_controlled_association_uses_the_same_cells_as_the_raw_one():
    """Partialling must not quietly change the sample it is computed on."""
    records = rows()
    for weighting in WEIGHTINGS:
        for relationship, n in (("methane ~ impervious_fraction", 926),
                                ("methane ~ rice_fraction_single", 531)):
            raw = find(records, relationship, "", weighting)
            given = find(records, relationship, ALBEDO, weighting)
            assert int(raw["n"]) == int(given["n"]) == n


def test_both_legs_of_the_confounding_path_are_measured():
    """A confounder needs albedo to reach methane and to reach the land cover."""
    records = rows()
    for weighting in WEIGHTINGS:
        leg_one = find(records, f"methane ~ {ALBEDO}", "", weighting)
        leg_two = find(records, f"{ALBEDO} ~ impervious_fraction", "", weighting)
        assert abs(float(leg_one["pearson"])) > 0.4, "albedo reaches methane"
        assert abs(float(leg_two["pearson"])) > 0.2, "albedo reaches the land cover"


def test_albedo_explains_the_methane_field_better_than_land_cover_does():
    records = rows()
    for weighting in WEIGHTINGS:
        albedo = float(find(records, f"methane ~ {ALBEDO}", "", weighting)["pearson"])
        land = float(find(records, "methane ~ impervious_fraction", "",
                          weighting)["pearson"])
        assert abs(albedo) > abs(land), \
            "a retrieval covariate should not be beaten by the predictor of interest"


def test_the_impervious_association_does_not_survive_the_control():
    """The finding. If a change moves this, it should fail here first."""
    records = rows()
    for weighting in WEIGHTINGS:
        raw = float(find(records, "methane ~ impervious_fraction", "",
                         weighting)["pearson"])
        given = find(records, "methane ~ impervious_fraction", ALBEDO, weighting)
        assert abs(float(given["pearson"])) < 0.25 * abs(raw), \
            "the association keeps less than a quarter of its magnitude"
        assert float(given["pearson_p"]) > 0.05, \
            "and is no longer distinguishable from zero"


def test_the_rice_association_does_not_survive_either():
    records = rows()
    for weighting in WEIGHTINGS:
        given = find(records, "methane ~ rice_fraction_single", ALBEDO, weighting)
        assert float(given["pearson"]) <= 0.0, "what is left is not positive"
        assert float(given["pearson_p"]) > 0.05


def test_the_multi_control_row_names_all_three_controls():
    records = rows()
    controls = f"{ALBEDO}, surface_albedo_NIR, solar_zenith_angle"
    for weighting in WEIGHTINGS:
        record = find(records, "methane ~ impervious_fraction", controls, weighting)
        assert int(record["n"]) == 926
