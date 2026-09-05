"""Tests for the committed 2018 analysis grid.

These read data/processed/analysis_grid_2018.csv and the methane composite it
was built on. Both are committed, so these run in every clone with nothing
fetched. They check the table against the composite rather than against
remembered numbers wherever they can, so the pair cannot drift apart silently.

The properties that matter: the table holds exactly the covered cells and no
others; a fraction that was never assessed is blank rather than zero; and every
fraction and coverage lies in a range that is arithmetically possible. The last
is what caught a real error, when masking four overlapping province rasters by
their union pushed one cell's assessed area to 2.94 times the cell.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest
import rasterio

REPO = Path(__file__).resolve().parents[1]
GRID = REPO / "data" / "processed" / "analysis_grid_2018.csv"
TIF = REPO / "data" / "processed" / "methane_composite_2018.tif"

PROVINCE_COLUMNS = ["share_anhui", "share_jiangsu", "share_shanghai", "share_zhejiang"]


def rows():
    return list(csv.DictReader(open(GRID, newline="")))


def numbers(records, column):
    """Non-blank values in a column, as floats."""
    return np.array([float(r[column]) for r in records if r[column] != ""])


def test_the_table_holds_one_row_per_covered_cell():
    with rasterio.open(TIF) as src:
        counts = src.read(3)
    assert len(rows()) == int((counts > 0).sum()) == 926


def test_every_row_matches_the_composite_cell_it_names():
    with rasterio.open(TIF) as src:
        primary, secondary, counts = src.read(1), src.read(2), src.read(3)
        transform = src.transform
    inverse = ~transform
    for record in rows():
        col, row = inverse * (float(record["centre_lon"]), float(record["centre_lat"]))
        r, c = int(row), int(col)
        assert int(record["sounding_count"]) == int(counts[r, c])
        assert float(record["ch4_bias_corrected_ppb"]) == pytest.approx(
            float(primary[r, c]), abs=0.01)
        assert float(record["ch4_raw_ppb"]) == pytest.approx(
            float(secondary[r, c]), abs=0.01)


def test_no_row_has_a_zero_sounding_count():
    """The 97 uncovered cells are excluded, and CellRow refuses to build one."""
    assert all(int(r["sounding_count"]) > 0 for r in rows())


def test_fractions_lie_between_zero_and_one():
    records = rows()
    for column in ("impervious_fraction", "rice_fraction_single",
                   "rice_fraction_combined"):
        values = numbers(records, column)
        assert values.size, f"{column} is blank in every row"
        assert values.min() >= 0.0
        assert values.max() <= 1.0, f"{column} exceeds 1: a fraction cannot"


def test_coverage_never_meaningfully_exceeds_the_cell():
    """Assessed area above the cell means a raster was counted twice.

    The tolerance is for pixel-centre quantisation: a 30 m pixel grid does not
    divide a 0.25 degree cell evenly, so a cell gains or loses up to about one
    pixel row, which is roughly 0.1 percent.
    """
    records = rows()
    for column in ("impervious_coverage", "rice_coverage"):
        values = numbers(records, column)
        assert values.min() >= 0.0
        assert values.max() <= 1.002, f"{column} exceeds the cell by more than " \
                                      f"quantisation: {values.max()}"


def test_an_unassessed_cell_is_blank_rather_than_zero():
    """No rice raster reached these cells, which is not the same as no rice."""
    blank = [r for r in rows() if r["rice_fraction_single"] == ""]
    assert len(blank) == 395
    for record in blank:
        assert float(record["rice_coverage"]) == 0.0
        assert record["rice_fraction_combined"] == ""


#: Edges of the 2018 Anhui rice raster, which stops short of the province.
ANHUI_RASTER_TOP = 33.34618621
ANHUI_RASTER_LEFT = 115.268237325


def test_the_only_unassessed_cells_inside_a_province_are_the_clipped_anhui_ones():
    """The Anhui clip reappears on the grid, from the other direction.

    The 2018 rice raster classifies Anhui only up to 33.3462 north and only
    east of 115.2682, so cells beyond those edges lie inside the province and
    still have no rice denominator. Eleven of them are wholly inside Anhui. They
    are blank rather than zero, which is the distinction the whole table exists
    to preserve: nobody looked there, and that is not an absence of rice.

    Every other blank cell is outside all four provinces entirely, and no
    province other than Anhui contributes one, because only Anhui's raster
    falls short of its own polygon.
    """
    inside = [r for r in rows()
              if r["rice_fraction_single"] == ""
              and sum(float(r[c] or 0) for c in PROVINCE_COLUMNS) > 1e-6]
    assert len(inside) == 27

    north, west = 0, 0
    for record in inside:
        assert float(record["share_anhui"]) > 0, "only Anhui is short of its polygon"
        assert all(float(record[c] or 0) == 0
                   for c in PROVINCE_COLUMNS if c != "share_anhui")
        lat, lon = float(record["centre_lat"]), float(record["centre_lon"])
        beyond_top = lat > ANHUI_RASTER_TOP
        beyond_left = lon < ANHUI_RASTER_LEFT
        assert beyond_top or beyond_left, \
            f"cell at {lat}, {lon} is inside the raster and should be assessed"
        north += beyond_top
        west += beyond_left
    assert (north, west) == (25, 2), "both edges are clipped, not only the north"


def test_cells_wholly_inside_anhui_can_still_have_no_rice_denominator():
    """The strongest form of the clip: province share 1.0, coverage 0.0."""
    whole = [r for r in rows()
             if r["rice_fraction_single"] == ""
             and float(r["share_anhui"] or 0) == 1.0]
    assert len(whole) == 11
    for record in whole:
        assert float(record["rice_coverage"]) == 0.0
        assert float(record["centre_lat"]) > ANHUI_RASTER_TOP
        assert record["impervious_fraction"] != "", \
            "GAIA is unmasked and still assesses these cells"


def test_the_combined_class_is_never_smaller_than_the_single_class():
    for record in rows():
        if record["rice_fraction_single"] == "":
            continue
        assert (float(record["rice_fraction_combined"])
                >= float(record["rice_fraction_single"]) - 1e-12)


def test_province_shares_are_consistent_with_the_reported_remainder():
    for record in rows():
        total = sum(float(record[c]) for c in PROVINCE_COLUMNS if record.get(c))
        outside = float(record["province_share_outside"])
        assert total + outside == pytest.approx(1.0, abs=2e-3)
        assert 0.0 <= outside <= 1.0


def test_impervious_is_assessed_everywhere_and_rice_is_not():
    """The two layers carry different denominators, deliberately.

    GAIA is global and unmasked, so it assesses every cell. The rice rasters
    are masked to the province each is named for, so a cell over sea or outside
    the four provinces has no rice denominator at all.
    """
    records = rows()
    assert all(r["impervious_fraction"] != "" for r in records)
    assert numbers(records, "impervious_coverage").min() > 0.99
    rice_blank = sum(1 for r in records if r["rice_fraction_single"] == "")
    assert rice_blank == 395
    assert numbers(records, "rice_coverage").min() == 0.0
