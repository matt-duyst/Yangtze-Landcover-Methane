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

#: The live study grid, 26.95 to 35.2 north and 114.8 to 122.55 east. These
#: are the bounds the 0.25 degree lattice occupies; the box used to be declared
#: as 27.0 and 122.6 and did not.
STUDY = GridSpec(west=114.8, south=26.95, east=122.55, north=35.2,
                 resolution=0.25)


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
    assert int(uncovered.sum()) == 97
    assert np.isnan(primary[uncovered]).all()
    assert np.isnan(secondary[uncovered]).all()
    assert np.isfinite(primary[~uncovered]).all()
    assert not (primary[~uncovered] == 0).any()

    rows = list(csv.DictReader(open(CSV, newline="")))
    blank = [r for r in rows if r["ch4_bias_corrected_ppb"] == ""]
    zero = [r for r in rows if int(r["sounding_count"]) == 0]
    assert len(blank) == len(zero) == 97
    assert blank == zero, "blank mean and zero count must mark the same cells"


def test_the_committed_composite_matches_the_reported_headline_numbers():
    with rasterio.open(TIF) as src:
        primary, counts = src.read(1), src.read(3)
        tags = src.tags()
    covered = counts > 0
    assert int(covered.sum()) == 926
    # 110,920 since the extent reconciliation: +151 soundings gained in the
    # southern row that used to be discarded, -159 removed from the eastern
    # column that used to be clipped in.
    assert int(counts.sum()) == 110_920
    assert int(tags["soundings"]) == 110_920
    assert int(tags["granules_gridded"]) == 578
    # 223: one July granule whose only in-box soundings fell in the southern
    # 26.95-27.0 strip, previously discarded whole so it counted as barren.
    assert int(tags["granules_with_data"]) == 223
    assert float(tags["qa_threshold"]) == 0.75
    # 74: the median moved by one as the least-sampled edge cells changed.
    assert int(np.median(counts[covered])) == 74
    assert int(counts.max()) == 410
    assert 1880.0 < float(np.nanmean(primary)) < 1900.0


def test_the_bias_correction_is_positive_in_every_covered_cell():
    with rasterio.open(TIF) as src:
        primary, secondary, counts = src.read(1), src.read(2), src.read(3)
    covered = counts > 0
    difference = primary[covered] - secondary[covered]
    assert (difference > 0).all()
    assert float(difference.mean()) == pytest.approx(11.64, abs=0.05)


# --------------------------------------------------------------------------
# the covariate companion file
# --------------------------------------------------------------------------

def make_covariate_composite(spec, cells, covariates):
    """A composite whose covariate counts differ from its sounding counts."""
    specs = tuple(mg.CovariateSpec(name=n, group="PRODUCT/SUPPORT_DATA/INPUT_DATA")
                  for n in covariates)
    acc = cm.Accumulator(spec, 0.75, (mg.PRIMARY, mg.SECONDARY), specs)
    for (row, col), (n, primary, secondary) in cells.items():
        acc.counts[row, col] = n
        acc.sums[mg.PRIMARY][row, col] = primary * n
        acc.sums[mg.SECONDARY][row, col] = secondary * n
    for name, (row, col, count, total) in covariates.items():
        acc.covariate_counts[name][row, col] = count
        acc.covariate_sums[name][row, col] = total
    return acc.composite()


def test_covariate_export_pairs_every_mean_with_its_own_count(tmp_path):
    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    composite = make_covariate_composite(
        spec, {(0, 0): (10, 1900.0, 1880.0)},
        {"eastward_wind": (0, 0, 10, 30.0), "surface_albedo_SWIR": (0, 0, 2, 0.4)})
    tif, csv_path = cm.export_covariates(composite, tmp_path / "cov")
    with rasterio.open(tif) as src:
        assert src.count == 4, "two bands per covariate"
        assert list(src.descriptions) == [
            "eastward_wind mean", "eastward_wind count",
            "surface_albedo_SWIR mean", "surface_albedo_SWIR count"]
        wind_mean, wind_count = src.read(1), src.read(2)
        albedo_mean, albedo_count = src.read(3), src.read(4)
    assert wind_mean[0, 0] == pytest.approx(3.0)
    assert wind_count[0, 0] == 10
    assert albedo_mean[0, 0] == pytest.approx(0.2), \
        "0.4 over its own count of 2, not over the sounding count of 10"
    assert albedo_count[0, 0] == 2


def test_the_covariate_file_never_carries_the_sounding_count_as_a_band(tmp_path):
    """The mistake the companion file exists to prevent."""
    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    composite = make_covariate_composite(
        spec, {(0, 0): (10, 1900.0, 1880.0)},
        {"surface_albedo_SWIR": (0, 0, 2, 0.4)})
    tif, _ = cm.export_covariates(composite, tmp_path / "cov")
    with rasterio.open(tif) as src:
        assert "sounding count" not in list(src.descriptions)
        assert "count" in src.tags()["note"] or "covariate" in src.tags()["note"]


def test_the_covariate_csv_blanks_a_mean_with_no_count(tmp_path):
    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    composite = make_covariate_composite(
        spec, {(0, 0): (10, 1900.0, 1880.0)},
        {"surface_albedo_SWIR": (0, 0, 2, 0.4)})
    _, csv_path = cm.export_covariates(composite, tmp_path / "cov")
    rows = list(csv.DictReader(open(csv_path, newline="")))
    assert len(rows) == spec.n_cells == 4
    populated = [r for r in rows if int(r["surface_albedo_SWIR_count"]) > 0]
    assert len(populated) == 1
    for record in rows:
        if int(record["surface_albedo_SWIR_count"]) == 0:
            assert record["surface_albedo_SWIR_mean"] == "", \
                "an unmeasured covariate is blank, never zero"


def test_exporting_covariates_from_a_composite_without_any_is_refused(tmp_path):
    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    composite = make_composite(spec, {(0, 0): (4, 1900.0, 1880.0)})
    with pytest.raises(SystemExit, match="no covariates"):
        cm.export_covariates(composite, tmp_path / "cov")


# --------------------------------------------------------------------------
# the reproduction check
# --------------------------------------------------------------------------

def test_verify_reports_zero_difference_against_an_identical_composite(tmp_path):
    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    composite = make_composite(spec, {(0, 0): (4, 1900.0, 1880.0),
                                      (1, 1): (2, 1950.0, 1930.0)})
    tif, _ = cm.export(composite, tmp_path / "c")
    check = cm.verify_methane(composite, tif)
    assert check["bias_corrected"] == 0.0
    assert check["raw"] == 0.0
    assert check["counts"] == 0.0
    assert check["covered_cells_new"] == check["covered_cells_reference"] == 2


def test_verify_catches_a_changed_value(tmp_path):
    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    reference = make_composite(spec, {(0, 0): (4, 1900.0, 1880.0)})
    tif, _ = cm.export(reference, tmp_path / "c")
    moved = make_composite(spec, {(0, 0): (4, 1905.0, 1880.0)})
    check = cm.verify_methane(moved, tif)
    assert check["bias_corrected"] == pytest.approx(5.0, abs=0.01)
    assert check["raw"] == 0.0


def test_verify_treats_a_new_or_lost_cell_as_infinite_difference(tmp_path):
    """A cell that gained or lost coverage is not a small numeric difference."""
    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    reference = make_composite(spec, {(0, 0): (4, 1900.0, 1880.0)})
    tif, _ = cm.export(reference, tmp_path / "c")
    extra = make_composite(spec, {(0, 0): (4, 1900.0, 1880.0),
                                  (1, 1): (1, 1910.0, 1890.0)})
    check = cm.verify_methane(extra, tif)
    assert check["bias_corrected"] == float("inf")
    assert check["covered_cells_new"] == 2
    assert check["covered_cells_reference"] == 1


def test_the_committed_composite_verifies_against_itself():
    """A sanity check on the checker, using a file every clone has.

    The composite is reconstructed here by multiplying the stored float32 means
    back up by their counts, which is lossy: a real accumulator holds float64
    sums built from the soundings themselves, never a mean multiplied out. The
    residue is that reconstruction and not the checker, so the tolerance is one
    float32 ulp at 1900 ppb rather than zero. A genuine re-run accumulates in
    the same order from the same values and is expected to give exactly zero.
    """
    import numpy as np
    with rasterio.open(TIF) as src:
        primary, secondary, counts = src.read(1), src.read(2), src.read(3)
    composite = mg.Composite(
        spec=STUDY, qa_threshold=0.75, counts=counts.astype("int64"),
        sums={mg.PRIMARY: np.nan_to_num(primary) * counts,
              mg.SECONDARY: np.nan_to_num(secondary) * counts})
    check = cm.verify_methane(composite, TIF)
    assert check["bias_corrected"] < 1e-3
    assert check["raw"] < 1e-3
    assert check["counts"] == 0.0, "counts are integers and must match exactly"
    assert check["covered_cells_new"] == check["covered_cells_reference"] == 926


# --------------------------------------------------------------------------
# the deseasonalised companion
# --------------------------------------------------------------------------

def seasonal_fixture(spec, *, per_cell=60, seed=0):
    """A synthetic accumulator whose harmonic statistics are fittable."""
    import numpy as np
    from src.methane import seasonal as se

    rng = np.random.default_rng(seed)
    acc = cm.Accumulator(spec, 0.75, (mg.PRIMARY, mg.SECONDARY))
    mu_true = rng.normal(1900.0, 10.0, spec.shape)
    coefficients = np.array([9.0, -4.0, 1.0, 0.5])
    for row in range(spec.shape[0]):
        for col in range(spec.shape[1]):
            day = rng.uniform(1.0, 365.0, per_cell)
            y = mu_true[row, col] + se.HarmonicBasis(2).evaluate(day, coefficients)
            acc.harmonics.add(np.full(per_cell, row), np.full(per_cell, col),
                              y, day)
            acc.counts[row, col] = per_cell
            acc.sums[mg.PRIMARY][row, col] = y.sum()
            acc.sums[mg.SECONDARY][row, col] = y.sum() - per_cell * 11.0
    return acc, mu_true, coefficients


def test_the_deseasonalised_export_pairs_the_field_with_its_diagnostics(tmp_path):
    from src.methane import seasonal as se

    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    acc, mu_true, _ = seasonal_fixture(spec)
    fit = se.solve(acc.harmonics)
    tif, csv_path = cm.export_deseasonalised(fit, acc.harmonics, spec,
                                             tmp_path / "d")
    with rasterio.open(tif) as src:
        assert src.count == 5
        assert list(src.descriptions) == [
            "deseasonalised methane mean, ppb", "sounding count",
            "mean day of year", "day of year standard deviation",
            "poorly identified flag"]
        mu, counts = src.read(1), src.read(2)
        tags = src.tags()
    assert np.allclose(mu, mu_true, atol=0.05)
    assert (counts == 60).all()
    assert "SOUNDING level" in tags["note"]
    assert float(tags["peak_day_of_year"]) > 0


def test_the_deseasonalised_csv_blanks_unobserved_cells(tmp_path):
    from src.methane import seasonal as se

    spec = GridSpec(0.0, 0.0, 1.0, 1.0, 0.5)
    acc, _, _ = seasonal_fixture(spec)
    acc.counts[1, 1] = 0                       # pretend one cell was never seen
    acc.harmonics.n[1, 1] = 0
    fit = se.solve(acc.harmonics)
    _, csv_path = cm.export_deseasonalised(fit, acc.harmonics, spec,
                                           tmp_path / "d")
    rows = list(csv.DictReader(open(csv_path, newline="")))
    assert len(rows) == spec.n_cells == 4
    blank = [r for r in rows if int(r["sounding_count"]) == 0]
    assert len(blank) == 1
    for record in blank:
        assert record["ch4_deseasonalised_ppb"] == ""
        assert record["mean_day_of_year"] == ""
        assert record["poorly_identified"] == ""


def test_the_deseasonalised_field_is_not_the_composite_mean_minus_a_cycle(tmp_path):
    """The distinction the whole approach rests on.

    Two cells with the same true offset sampled in different seasons have
    different composite means. Subtracting the cycle evaluated at each cell's
    MEAN date does not bring them together in general, because the mean of a
    nonlinear function is not the function of the mean. Fitting at the sounding
    level does.
    """
    import numpy as np
    from src.methane import seasonal as se

    spec = GridSpec(0.0, 0.0, 1.0, 0.5, 0.5)
    basis = se.HarmonicBasis(1)
    coefficients = np.array([12.0, 0.0])
    stats = se.HarmonicStats(spec.shape, basis)
    for col, days in ((0, np.linspace(30.0, 120.0, 150)),
                      (1, np.linspace(210.0, 300.0, 150))):
        y = 1900.0 + basis.evaluate(days, coefficients)
        stats.add(np.zeros(days.size, "int64"), np.full(days.size, col), y, days)

    raw = stats.sum_y / stats.n
    fit = se.solve(stats)
    assert abs(raw[0, 0] - raw[0, 1]) > 10.0
    assert fit.mu[0, 0] == pytest.approx(fit.mu[0, 1], abs=0.05)
    assert fit.mu[0, 0] == pytest.approx(1900.0, abs=0.05)
