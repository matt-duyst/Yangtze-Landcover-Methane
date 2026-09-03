"""Tests for the committed baseline results.

These read data/processed/baseline_results_2018.csv and the analysis grid it
was computed from. Both are committed, so these run in every clone.

The point of a baseline table is that it cannot quietly become flattering, so
what is pinned here is mostly structure: that every model appears under both
schemes and both weightings, that sample sizes are what the missing rice
fractions imply, and that the two constants coincide out of sample under
leave-one-province-out, which is a property of the scheme rather than a number
anyone chose.
"""

from __future__ import annotations

import csv
import importlib.util
from pathlib import Path

import numpy as np
import pytest

from src.model.baselines import load_table

REPO = Path(__file__).resolve().parents[1]
RESULTS = REPO / "data" / "processed" / "baseline_results_2018.csv"
GRID = REPO / "data" / "processed" / "analysis_grid_2018.csv"

SCHEMES = {"leave-one-province-out", "spatial blocks"}
WEIGHTINGS = {"unweighted", "by sounding count"}


def rows():
    return list(csv.DictReader(open(RESULTS, newline="")))


def load_script():
    path = REPO / "scripts" / "run_baselines.py"
    spec = importlib.util.spec_from_file_location("_run_baselines", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_every_model_appears_under_both_schemes_and_both_weightings():
    records = rows()
    seen = {}
    for record in records:
        seen.setdefault(record["model"], set()).add(
            (record["scheme"], record["weighting"]))
    assert seen, "the table is empty"
    for model, combinations in seen.items():
        assert combinations == {(s, w) for s in SCHEMES for w in WEIGHTINGS}, \
            f"{model} is missing a scheme or a weighting"
    assert len(records) == len(seen) * 4


def test_sample_sizes_are_927_or_the_532_with_a_rice_fraction():
    grid = list(csv.DictReader(open(GRID, newline="")))
    with_rice = sum(1 for r in grid if r["rice_fraction_single"] != "")
    assert len(grid) == 927 and with_rice == 532
    # A model's name no longer encodes its columns, so the requirement is read
    # from the model definitions rather than guessed from the label.
    module = load_script()
    table = load_table(GRID, covariates=REPO / "data" / "processed" /
                       "methane_covariates_2018.csv")
    needs_rice = {model.name for model, _ in module.models(table)
                  if any("rice" in name for name in model.requires)}
    restricted = {model.name for model, subset in module.models(table)
                  if subset is not None}

    for record in rows():
        n, dropped = int(record["n"]), int(record["dropped_missing"])
        assert n in (927, 532)
        if n == 927:
            assert dropped == 0
        elif dropped:
            # Asked for the whole grid and lost the cells with no rice.
            assert dropped == 395, record["model"]
            assert record["model"] in needs_rice, record["model"]
        else:
            # Asked only for the rice sample, so nothing was dropped from it.
            assert record["model"] in restricted, record["model"]


def test_a_model_naming_rice_never_runs_on_the_full_grid():
    """Rice is absent in 395 cells and is never filled in to reach 927."""
    for record in rows():
        if "rice_fraction" in record["model"]:
            assert int(record["n"]) == 532


def test_the_two_constants_agree_out_of_sample_under_leave_one_province_out():
    """The held-out province is the group with no training data, so they must.

    Not a coincidence and not a duplicated row: the per-province constant has
    nothing to say about a province it never saw, and falls back to the global
    mean for every held-out cell.
    """
    by_key = {(r["model"], r["scheme"], r["weighting"]): r for r in rows()}
    for weighting in WEIGHTINGS:
        for suffix in ("", " [rice sample]"):
            a = by_key[(f"constant (global mean){suffix}",
                        "leave-one-province-out", weighting)]
            b = by_key[(f"constant (per province){suffix}",
                        "leave-one-province-out", weighting)]
            assert a["held_out_rmse_ppb"] == b["held_out_rmse_ppb"]
            assert float(b["in_sample_rmse_ppb"]) < float(a["in_sample_rmse_ppb"]), \
                "in sample the province constant is strictly better"


def test_the_global_constants_in_sample_error_is_the_targets_spread():
    """A constant at the mean cannot do better than the standard deviation."""
    table = load_table(GRID)
    by_key = {(r["model"], r["weighting"]): r for r in rows()
              if r["scheme"] == "spatial blocks"}
    unweighted = by_key[("constant (global mean)", "unweighted")]
    assert float(unweighted["in_sample_rmse_ppb"]) == pytest.approx(
        table.y.std(), abs=0.001)
    assert float(unweighted["in_sample_r2"]) == pytest.approx(0.0, abs=1e-6)

    weighted = by_key[("constant (global mean)", "by sounding count")]
    centre = np.average(table.y, weights=table.weight)
    spread = np.sqrt(np.average((table.y - centre) ** 2, weights=table.weight))
    assert float(weighted["in_sample_rmse_ppb"]) == pytest.approx(spread, abs=0.001)


def test_held_out_error_is_never_better_than_in_sample_error():
    for record in rows():
        assert float(record["held_out_rmse_ppb"]) >= \
            float(record["in_sample_rmse_ppb"]) - 1e-6, record["model"]


def test_every_linear_model_records_its_coefficients():
    """Every fitted term is named and valued, whatever the model is called."""
    module = load_script()
    table = load_table(GRID, covariates=REPO / "data" / "processed" /
                       "methane_covariates_2018.csv")
    columns = {model.name: model.requires for model, _ in module.models(table)}

    for record in rows():
        if not record["model"].startswith("OLS"):
            continue
        assert record["detail"].startswith("intercept ")
        for name in columns.get(record["model"], ()):
            assert name in record["detail"], f"{record['model']} omits {name}"
        terms = record["detail"].split("; ")
        assert len(terms) == len(columns.get(record["model"], ())) + 1 \
            or "x" in record["detail"], "one term per column, plus the intercept"


def test_no_tree_or_network_appears_in_the_baseline_table():
    """This part establishes the bar. Anything that clears it belongs elsewhere."""
    forbidden = ("xgboost", "random forest", "gradient", "network", "cnn",
                 "unet", "neural", "lightgbm")
    for record in rows():
        lowered = record["model"].lower()
        assert not any(word in lowered for word in forbidden), record["model"]


def test_the_script_offers_every_null_on_both_samples():
    """A null on 927 cells cannot referee a model fitted on 532."""
    module = load_script()
    table = load_table(GRID)
    sizes = {}
    for model, subset in module.models(table):
        n = table.n if subset is None else int(subset.size)
        sizes.setdefault(n, []).append(model.name)
    assert set(sizes) == {927, 532}
    for n, names in sizes.items():
        joined = " ".join(names)
        assert "global mean" in joined, f"no global constant on the {n}-cell sample"
        assert "per province" in joined, f"no province constant on the {n}-cell sample"
        assert "spatial null" in joined, f"no spatial null on the {n}-cell sample"


def test_results_are_grouped_by_the_rows_used_not_by_the_model_name():
    """An OLS on rice has no tag but still runs on 532 rows."""
    module = load_script()
    tagged = type("R", (), {"model": "OLS rice_fraction_single", "n": 532})()
    untagged = type("R", (), {"model": "constant (global mean)", "n": 927})()
    assert module._sample_of(tagged) != module._sample_of(untagged)
    assert module._sample_of(tagged) == "532 cells"
