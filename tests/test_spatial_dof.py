"""The effective-degrees-of-freedom correction, checked against known answers.

A correction that silently does nothing and a correction that silently does too
much look the same in a table of p-values, so both ends are pinned here. The
estimator must reduce to the nominal test on independent fields and must
collapse on strongly dependent ones, and the reconstruction of the reported
correlations must reproduce them exactly before their significance is corrected.

That last check is the one that matters most. This correction is only meaningful
if the series it estimates dependence from are the same series the published
coefficients came from, and the only way to know that is to recompute the
coefficients and compare. They agree to the last digit reported.
"""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model import spatial_dof as sd  # noqa: E402

ARTEFACT = REPO / "data" / "processed" / "correlation_dof_2018.csv"


@pytest.fixture(scope="module")
def rows() -> list[dict]:
    with ARTEFACT.open(newline="") as handle:
        return list(csv.DictReader(handle))


@pytest.fixture(scope="module")
def scattered() -> tuple[np.ndarray, np.ndarray]:
    rng = np.random.default_rng(20260912)
    return rng.uniform(27.0, 35.0, 400), rng.uniform(115.0, 122.0, 400)


# --------------------------------------------------------------------------
# the estimator's two ends
# --------------------------------------------------------------------------

def test_independent_fields_keep_most_of_their_sample_size(scattered):
    """No dependence to correct means little correction.

    Not exactly `n + 1`: the binned correlogram carries sampling noise that
    inflates the trace, so the estimator is mildly conservative even here. The
    script's docstring records the measured size of that bias so a shrinkage
    near 0.87 is read as "nothing detected" rather than as a real loss.
    """
    lat, lon = scattered
    rng = np.random.default_rng(1)
    x, y = rng.normal(size=len(lat)), rng.normal(size=len(lat))

    test = sd.modified_t_test(x, y, lat, lon)

    assert 0.75 < test.shrinkage <= 1.0


def test_strongly_dependent_fields_lose_most_of_their_sample_size(scattered):
    """Two fields with a 150 km correlation range keep under a fifth."""
    lat, lon = scattered
    rng = np.random.default_rng(2)
    cov = np.exp(-sd.great_circle_km(lat, lon) / 150.0)
    root = np.linalg.cholesky(cov + 1e-9 * np.eye(len(lat)))
    x = root @ rng.normal(size=len(lat))
    y = root @ rng.normal(size=len(lat))

    test = sd.modified_t_test(x, y, lat, lon)

    assert test.shrinkage < 0.2


def test_the_correction_never_adds_information(scattered):
    """The effective sample size is capped at the nominal one.

    Without the cap a noisy correlogram can return `M > n + 1`, which would
    make a p-value smaller than the uncorrected one. That direction is never
    right and would be the most misleading possible failure.
    """
    lat, lon = scattered
    rng = np.random.default_rng(3)
    for seed in range(5):
        x = rng.normal(size=len(lat))
        y = rng.normal(size=len(lat))
        test = sd.modified_t_test(x, y, lat, lon)
        assert test.effective_n <= len(lat) + 1


def test_a_perfect_correlation_is_handled_rather_than_dividing_by_zero(scattered):
    lat, lon = scattered
    x = np.asarray(lat, dtype="float64")

    test = sd.modified_t_test(x, x, lat, lon)

    assert np.isnan(test.p_nominal) and np.isnan(test.p_corrected)


def test_a_constant_field_is_refused(scattered):
    lat, lon = scattered
    with pytest.raises(ValueError):
        sd.effective_sample_size(np.ones(len(lat)), np.asarray(lat), lat, lon)


def test_great_circle_distance_is_symmetric_and_zero_on_the_diagonal(scattered):
    lat, lon = scattered
    d = sd.great_circle_km(lat, lon)

    assert np.allclose(d, d.T)
    assert np.allclose(np.diag(d), 0.0)
    # The domain is about 750 by 900 km, so the longest separation is near
    # 1,200 km. A planar approximation would be wrong by several percent here,
    # which is why the estimator uses great-circle distance.
    assert 1000.0 < d.max() < 1400.0


# --------------------------------------------------------------------------
# the artefact
# --------------------------------------------------------------------------

def test_the_reported_pearson_coefficients_are_reproduced_exactly(rows):
    """The reconstruction reads the same series the published numbers used.

    If this fails the correction is meaningless, because the dependence would
    have been estimated from different data than the coefficient.
    """
    checked = 0
    for row in rows:
        if row["method"] != "pearson" or not row["coefficient_reported"]:
            continue
        assert row["coefficient_recomputed"] == row["coefficient_reported"], \
            f"{row['field']} {row['weighting']} {row['relationship']}"
        checked += 1

    assert checked == 26, "all twenty-six reported Pearson rows must be checked"


def test_every_row_loses_sample_size(rows):
    """A lattice field cannot carry its nominal n, and none of them does."""
    for row in rows:
        assert float(row["shrinkage"]) < 0.3, row["relationship"]


def test_corrected_p_is_never_smaller_than_nominal(rows):
    for row in rows:
        nominal, corrected = float(row["p_nominal"]), float(row["p_corrected"])
        if np.isfinite(nominal) and np.isfinite(corrected):
            assert corrected >= nominal - 1e-12, row["relationship"]


def test_the_verdict_column_agrees_with_the_p_values(rows):
    for row in rows:
        nominal, corrected = float(row["p_nominal"]), float(row["p_corrected"])
        if row["verdict"] == "was significant, now is not":
            assert nominal < 0.05 <= corrected
        elif row["verdict"] == "significant":
            assert corrected < 0.05
        else:
            assert nominal >= 0.05 and corrected >= 0.05


def test_the_blended_field_rows_are_present_and_new(rows):
    """The blended correlations existed only in README prose before this."""
    blended = [r for r in rows if r["field"] == "blended"]

    assert len(blended) == 10
    assert all(not r["coefficient_reported"] for r in blended), \
        "the blended coefficients are computed here, not carried forward"


def test_the_script_is_deterministic_and_reproduces_the_committed_artefact():
    """Run the command and compare, rather than asserting it would agree.

    The committed file is read first, the script rewrites it, and the two are
    compared byte for byte. `tests/test_recipes.py` runs the same command
    through the registry; this is here as well because the correlogram bins
    pair distances and an unstable binning would show up as a diff rather than
    as a failure anywhere else.
    """
    before = ARTEFACT.read_bytes()
    result = subprocess.run(
        [sys.executable, "scripts/correct_correlation_dof.py", "--write"],
        cwd=REPO, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr[-2000:]
    assert ARTEFACT.read_bytes() == before
