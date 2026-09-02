"""Tests for the committed 2018 methane composite.

Two kinds of test here. The first build a composite in ``tmp_path`` from
synthetic granules and check the export round-trips, so they run on a clone
with nothing fetched. The second read the committed GeoTIFF and CSV directly
and check they agree with each other; those are committed files, present in
every clone, so they need no fetch either.

The property that matters most is that an unobserved cell says so twice and
consistently: NaN in the two mean bands, zero in the count band, and a blank
mean with a zero count in the table. A cell nobody observed and a cell with no
methane are different claims, and the export must not let them collapse.
"""

from __future__ import annotations

import csv
import importlib.util
import math
from pathlib import Path

import numpy as np
import pytest
import rasterio

from src.methane import grid as mg
from src.methane.grid import GridSpec

REPO = Path(__file__).resolve().parents[1]
TIF = REPO / "data" / "processed" / "methane_composite_2018.tif"
CSV = REPO / "data" / "processed" / "methane_coverage_2018.csv"

STUDY = GridSpec(114.8, 27.0, 122.6, 35.2, 0.25)


def load_script(name):
    path = REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_script_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


cm = load_script("compute_methane_composite")


# --------------------------------------------------------------------------
# synthetic round trip
# --------------------------------------------------------------------------

def make_composite(spec, cells):
    """A composite with known counts and sums, without touching a granule."""
    acc = cm.Accumulator(spec, 0.75, (mg.PRIMARY, mg.SECONDARY))
    for (row, col), (n, primary, secondary) in cells.items():
        acc.counts[row, col] = n
        acc.sums[mg.PRIMARY][row, col] = primary * n
        acc.sums[mg.SECONDARY][row, col] = secondary * n
    return acc.composite()


def test_export_writes_three_named_bands(tmp_path):
    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    composite = make_composite(spec, {(0, 0): (4, 1900.0, 1880.0)})
    tif, _ = cm.export(composite, tmp_path / "c")
    with rasterio.open(tif) as src:
        assert src.count == 3
        assert src.crs.to_string() == "EPSG:4326"
        assert [d.split(",")[0] for d in src.descriptions] == [
            "methane_mixing_ratio_bias_corrected mean",
            "methane_mixing_ratio mean",
            "sounding count"]


def test_export_round_trips_values_and_marks_empties(tmp_path):
    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    composite = make_composite(spec, {(0, 0): (4, 1900.0, 1880.0),
                                      (1, 1): (2, 1950.0, 1930.0)})
    tif, csv_path = cm.export(composite, tmp_path / "c")
    with rasterio.open(tif) as src:
        primary, secondary, counts = src.read(1), src.read(2), src.read(3)

    assert primary[0, 0] == pytest.approx(1900.0)
    assert secondary[1, 1] == pytest.approx(1930.0)
    assert counts[0, 0] == 4 and counts[1, 1] == 2
    for cell in ((0, 1), (1, 0)):
        assert counts[cell] == 0
        assert np.isnan(primary[cell]), "an unobserved cell must be NaN, not zero"
        assert np.isnan(secondary[cell])
    assert not (primary == 0).any()


def test_export_csv_holds_every_cell_including_empty_ones(tmp_path):
    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    composite = make_composite(spec, {(0, 0): (4, 1900.0, 1880.0)})
    _, csv_path = cm.export(composite, tmp_path / "c")
    rows = list(csv.DictReader(open(csv_path, newline="")))
    assert len(rows) == spec.n_cells == 4
    empty = [r for r in rows if int(r["sounding_count"]) == 0]
    assert len(empty) == 3
    for row in empty:
        assert row["ch4_bias_corrected_ppb"] == ""
        assert row["ch4_raw_ppb"] == ""


def test_export_takes_a_separate_csv_path(tmp_path):
    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    composite = make_composite(spec, {(0, 0): (1, 1900.0, 1880.0)})
    elsewhere = tmp_path / "sub" / "coverage.csv"
    tif, csv_path = cm.export(composite, tmp_path / "c", elsewhere)
    assert csv_path == elsewhere and elsewhere.exists()
    assert tif.name == "c.tif"


# --------------------------------------------------------------------------
# the committed artefacts
# --------------------------------------------------------------------------

def test_the_committed_raster_has_the_study_grid():
    with rasterio.open(TIF) as src:
        assert (src.height, src.width) == STUDY.shape == (33, 31)
        assert src.count == 3
        assert src.crs.to_string() == "EPSG:4326"
        assert src.bounds.left == pytest.approx(STUDY.west)
        assert src.bounds.top == pytest.approx(STUDY.north)
        assert abs(src.transform.a) == pytest.approx(STUDY.resolution)


def test_the_committed_raster_and_table_agree():
    """The two files must describe the same grid cell for cell."""
    with rasterio.open(TIF) as src:
        primary, secondary, counts = src.read(1), src.read(2), src.read(3)
        transform = src.transform

    rows = list(csv.DictReader(open(CSV, newline="")))
    assert len(rows) == counts.size == 1023

    for row_index in range(counts.shape[0]):
        for col_index in range(counts.shape[1]):
            record = rows[row_index * counts.shape[1] + col_index]
            lon, lat = transform * (col_index + 0.5, row_index + 0.5)
            assert float(record["centre_lat"]) == pytest.approx(lat, abs=1e-4)
            assert float(record["centre_lon"]) == pytest.approx(lon, abs=1e-4)
            n = int(record["sounding_count"])
            assert n == int(counts[row_index, col_index])
            if n == 0:
                assert record["ch4_bias_corrected_ppb"] == ""
                assert np.isnan(primary[row_index, col_index])
            else:
                assert float(record["ch4_bias_corrected_ppb"]) == pytest.approx(
                    float(primary[row_index, col_index]), abs=0.01)
                assert float(record["ch4_raw_ppb"]) == pytest.approx(
                    float(secondary[row_index, col_index]), abs=0.01)


def test_uncovered_cells_are_nan_in_the_raster_and_zero_count_in_the_table():
    with rasterio.open(TIF) as src:
        primary, secondary, counts = src.read(1), src.read(2), src.read(3)
    uncovered = counts == 0
    assert int(uncovered.sum()) == 96
    assert np.isnan(primary[uncovered]).all()
    assert np.isnan(secondary[uncovered]).all()
    assert np.isfinite(primary[~uncovered]).all()
    assert not (primary[~uncovered] == 0).any()

    rows = list(csv.DictReader(open(CSV, newline="")))
    blank = [r for r in rows if r["ch4_bias_corrected_ppb"] == ""]
    zero = [r for r in rows if int(r["sounding_count"]) == 0]
    assert len(blank) == len(zero) == 96
    assert blank == zero, "blank mean and zero count must mark the same cells"


def test_the_committed_composite_matches_the_reported_headline_numbers():
    with rasterio.open(TIF) as src:
        primary, counts = src.read(1), src.read(3)
        tags = src.tags()
    covered = counts > 0
    assert int(covered.sum()) == 927
    assert int(counts.sum()) == 110_928
    assert int(tags["soundings"]) == 110_928
    assert int(tags["granules_gridded"]) == 578
    assert int(tags["granules_with_data"]) == 222
    assert float(tags["qa_threshold"]) == 0.75
    assert int(np.median(counts[covered])) == 75
    assert int(counts.max()) == 410
    assert 1880.0 < float(np.nanmean(primary)) < 1900.0


def test_the_bias_correction_is_positive_in_every_covered_cell():
    with rasterio.open(TIF) as src:
        primary, secondary, counts = src.read(1), src.read(2), src.read(3)
    covered = counts > 0
    difference = primary[covered] - secondary[covered]
    assert (difference > 0).all()
    assert float(difference.mean()) == pytest.approx(11.64, abs=0.05)
