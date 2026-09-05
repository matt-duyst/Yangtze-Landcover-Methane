"""Tests for the committed GISA layer.

Reads the two committed companion files and the analysis grid. Offline.

What is pinned is that the GISA layer describes the same cells as the analysis
grid, and that its provincial totals sit below GAIA's rather than above, which
is the direction that matters: the product was fetched to test whether GAIA's
reported omission error was attenuating the land-cover association, and it
cannot have been if GISA finds less impervious surface than GAIA does.
"""

from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
CELLS = REPO / "data" / "processed" / "impervious_gisa_2018.csv"
PROVINCES = REPO / "data" / "processed" / "urban_area_by_province_gisa.csv"
GRID = REPO / "data" / "processed" / "analysis_grid_2018.csv"


def rows(path):
    return list(csv.DictReader(open(path, newline="")))


def test_the_gisa_cells_are_the_analysis_grid_cells():
    gisa, grid = rows(CELLS), rows(GRID)
    # 926 since the extent reconciliation: one column-30 cell was covered
    # only by soundings clipped in from the 122.55-122.6 strip.
    assert len(gisa) == len(grid) == 926
    for a, b in zip(gisa, grid):
        assert a["centre_lat"] == b["centre_lat"]
        assert a["centre_lon"] == b["centre_lon"]


def test_every_cell_has_a_gisa_fraction_and_full_coverage():
    """GISA is global and unmasked, so no cell is unassessed."""
    for record in rows(CELLS):
        assert record["impervious_fraction"] != ""
        fraction = float(record["impervious_fraction"])
        assert 0.0 <= fraction <= 1.0
        assert float(record["impervious_coverage"]) > 0.99


def test_gisa_and_gaia_fractions_agree_closely_but_are_not_identical():
    gisa = np.array([float(r["impervious_fraction"]) for r in rows(CELLS)])
    gaia = np.array([float(r["impervious_fraction"]) for r in rows(GRID)])
    correlation = np.corrcoef(gisa, gaia)[0, 1]
    assert correlation > 0.9, "two products measuring the same thing"
    assert not np.allclose(gisa, gaia), "but not the same numbers"


def test_gisa_finds_less_impervious_surface_than_gaia_in_every_province():
    """The opposite of what the global validation literature predicts."""
    records = rows(PROVINCES)
    assert len(records) == 4
    assert {r["province"] for r in records} == {"Shanghai", "Zhejiang",
                                                "Anhui", "Jiangsu"}
    for record in records:
        assert record["source"] == "GISA"
        assert record["year"] == "2018"
        ratio = float(record["gisa_over_gaia"])
        assert ratio < 1.0, f"{record['province']} has GISA above GAIA"
        assert float(record["urban_area_km2"]) < float(record["gaia_urban_km2"])


def test_the_shortfall_is_not_uniform_across_provinces():
    """Anhui is nearly unchanged while Jiangsu falls by a quarter."""
    ratios = {r["province"]: float(r["gisa_over_gaia"]) for r in rows(PROVINCES)}
    assert ratios["Anhui"] == pytest.approx(0.952, abs=0.002)
    assert ratios["Jiangsu"] == pytest.approx(0.736, abs=0.002)
    assert max(ratios.values()) - min(ratios.values()) > 0.2


def test_the_gisa_provincial_totals_are_below_the_thesis_except_in_anhui():
    for record in rows(PROVINCES):
        gisa = float(record["urban_area_km2"])
        thesis = float(record["thesis_urban_km2"])
        if record["province"] == "Anhui":
            assert gisa > thesis
        else:
            assert gisa < thesis
