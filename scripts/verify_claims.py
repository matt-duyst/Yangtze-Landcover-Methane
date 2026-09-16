#!/usr/bin/env python
"""Check numeric claims in the prose against the artefacts they came from.

    python scripts/verify_claims.py            # report every marked claim
    python scripts/verify_claims.py --stale    # only the ones that disagree
    python scripts/verify_claims.py --coverage # how much prose is marked

A third drift class, after recipes drifting from artefacts and artefacts
drifting from each other. Every figure quoted in the prose was correct when it
was written. Regenerating a table moves the values, and the sentences quoting
them go stale silently, because nothing connects a sentence to the table it
came from.

**How a claim is marked.** The number stays where it is, in the sentence, and
carries an HTML comment naming the quantity:

    There are 926<!--#grid.rows--> of them and fifteen columns.

The marker is invisible in rendered markdown and travels with the sentence it
belongs to, so it cannot drift from its claim the way a parallel table of
claims maintained beside the prose would. That parallel table is exactly the
failure this repository already had once, in the README regeneration table.

**Three classes of number, and only one is checked.** A claim derived from a
committed artefact is marked and checked. A property of external data -- a
DOI, a granule's byte count, an accuracy figure from a cited paper -- is stable
and needs no watching. A historical record of what was measured at some past
time must **not** be updated even when the current value differs, because
rewriting it destroys the record; `notes/decisions.md` is full of these by
design and is excluded from this mechanism entirely.

Marking is therefore a deliberate act at writing time, not something inferred.
An unmarked number is not checked, and `--coverage` reports how many there are
so the gap is visible rather than assumed away.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from pathlib import Path

import numpy as np

REPO = Path(__file__).resolve().parents[1]
# One quantity reads the committed land layer through `src.figures.geo`, and
# this script is run directly as well as imported by the test suite.
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
PROCESSED = REPO / "data" / "processed"

#: Files scanned for markers. `notes/decisions.md` is deliberately absent: it
#: is a decision log, its figures are as-measured-at-the-time, and a mechanism
#: that corrected them would destroy what it records.
SCANNED = ("README.md", "ERRATA.md", "data/processed/README.md",
           "data/reference/README.md", "figures/README_fragments.md",
           "notes/repository-architecture.md", "notes/grounding-yrd.md",
           "notes/grounding-methods.md", "notes/grounding-urban.md",
           "notes/grounding-rice.md", "notes/grounding-methane.md",
           "notes/paper-target.md", "notes/draft-methods.md",
           "notes/draft-results.md", "notes/draft-discussion.md",
           "notes/draft-introduction.md",
           # The reference audit's counts come from an artefact and will drift
           # as the drafts gain citations, so they are guarded like any other.
           "notes/reference-audit.md",
           # The availability statements quote the recipe tier counts, which
           # move whenever a recipe is added. notes/draft-*.md is also the name
           # tests/test_drafts_are_scanned.py requires to be scanned.
           "notes/draft-availability.md",
           # The verified case-study background. Its literature figures cannot
           # carry resolvers; the artefact-backed ones must.
           "notes/draft-case-study-background.md")

#: number, then optional space, then the marker naming what it is
CLAIM = re.compile(r"(-?[\d][\d,]*(?:\.\d+)?)\s*<!--#([a-zA-Z0-9_.]+)-->")

#: Every marker in the prose must name one of these.
_cache: dict = {}


def _read_csv(path) -> list[dict]:
    """Every row of a committed CSV as a dict. Used by the Tier 0 resolvers."""
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def _grid() -> list[dict]:
    if "grid" not in _cache:
        with (PROCESSED / "analysis_grid_2018.csv").open(newline="") as h:
            _cache["grid"] = list(csv.DictReader(h))
    return _cache["grid"]


def _covariates() -> list[dict]:
    if "cov" not in _cache:
        with (PROCESSED / "methane_covariates_2018.csv").open(newline="") as h:
            rows = list(csv.DictReader(h))
        _cache["cov"] = [r for r in rows
                         if r.get("sounding_count") not in ("", "0", None)]
    return _cache["cov"]


def _composite():
    if "comp" not in _cache:
        import rasterio
        with rasterio.open(PROCESSED / "methane_composite_2018.tif") as src:
            _cache["comp"] = (src.read(1), src.read(2), src.read(3), src.tags())
    return _cache["comp"]


def _column(name: str) -> np.ndarray:
    return np.array([float(r[name]) if r[name] not in ("", None) else np.nan
                     for r in _grid()])


def _cov_column(name: str) -> np.ndarray:
    return np.array([float(r[name]) for r in _covariates()
                     if r.get(name) not in ("", None)])


def _absence_blocks() -> tuple[int, int]:
    """Connected components of the absent cells, and the largest, 8-connected."""
    if "blocks" not in _cache:
        from scipy import ndimage
        absent = _composite()[2] == 0
        labels, n = ndimage.label(absent, structure=np.ones((3, 3)))
        sizes = ndimage.sum(absent, labels, range(1, n + 1))
        _cache["blocks"] = (int(n), int(sizes.max()) if n else 0)
    return _cache["blocks"]


def _cell_elevation() -> np.ndarray:
    """Mean GLO-90 elevation per analysis cell, on the composite's own grid.

    Committed to `data/reference/` by `scripts/build_map_reference.py`, which
    is what lets the study area figure's caption quote an elevation and have it
    checked: the DEM itself is 408 MB and gitignored.
    """
    if "elev" not in _cache:
        import rasterio
        path = (REPO / "data" / "reference" / "yrd_cell_elevation.tif")
        with rasterio.open(path) as src:
            _cache["elev"] = src.read(1)
    return _cache["elev"]


def _absent_on_land() -> int:
    """Absent cells lying wholly on land.

    Wholly, and the qualifier is doing work: of the 97, 93 touch land at all,
    83 have their centre on land, 81 are more than half land and 74 are
    entirely land. Any of the four is defensible and they are not the same
    number, so the caption says which one it means.
    """
    if "absent_land" not in _cache:
        from shapely.geometry import box

        from src.figures import geo

        spec = geo.study_spec()
        land = geo.read_layer(geo.LAND).union_all()
        absent = _composite()[2] == 0
        res = spec.resolution
        total = 0
        for row, col in zip(*np.where(absent)):
            west = spec.west + col * res
            south = spec.north - (row + 1) * res
            cell = box(west, south, west + res, south + res)
            if land.intersection(cell).area / cell.area >= 0.999:
                total += 1
        _cache["absent_land"] = total
    return _cache["absent_land"]


def _sea_fraction() -> "np.ndarray":
    """Per-cell sea fraction, from the committed land layer and the lattice.

    Read once and cached, because the land union is the expensive part and two
    quantities want it. `_absent_on_land` above computes a land fraction for a
    subset of cells with the same geometry; this is the whole grid, and the
    complement, because the statements it serves are about coastlines.
    """
    if "sea" not in _cache:
        from shapely.geometry import box

        from src.figures import geo

        spec = geo.study_spec()
        land = geo.read_layer(geo.LAND).union_all()
        res = spec.resolution
        out = np.zeros(_composite()[2].shape, dtype="float64")
        for row in range(out.shape[0]):
            for col in range(out.shape[1]):
                west = spec.west + col * res
                south = spec.north - (row + 1) * res
                cell = box(west, south, west + res, south + res)
                out[row, col] = 1.0 - land.intersection(cell).area / cell.area
        _cache["sea"] = out
    return _cache["sea"]


def _median_soundings(where: "np.ndarray") -> float:
    """Median sounding count over covered cells satisfying `where`.

    Covered cells only, and that restriction is the whole difference between
    the pair of figures this repository quotes. Over all 1,023 cells, with the
    uncovered counted as zero, the coastline's median is 2 to 3 and pure land's
    is about 108, which is what `data/processed/README.md` states. Over the 926
    covered cells the same two populations give 6 and 133. Both are true of the
    same composite; neither is wrong; they answer different questions, and a
    sentence quoting one has to say which.
    """
    counts = _composite()[2]
    return float(np.median(counts[where & (counts > 0)]))


def _urban_series() -> dict:
    """Four-province totals by source and year, from the committed tables.

    The figure reads the same two files through `src.figures.urban_change`, so
    a caption number and a drawn number cannot disagree without one of them
    failing here.
    """
    if "urban" not in _cache:
        from src.figures import urban_change
        _cache["urban"] = urban_change.series()
    return _cache["urban"]


#: The figure keys its series by (source, computation), because "GAIA" alone
#: does not say whether a number is the 2023 report or the 2026 recomputation
#: and those differ by a factor of two in 2000. These are the short spellings
#: the prose uses, mapped onto the pairs.
_URBAN_KEYS = {"gaia": ("GAIA", "reproduced 2026"),
               "gisa": ("GISA", "reproduced 2026"),
               "thesis": ("GAIA", "as reported 2023")}


def _urban(source: str, year: int) -> float:
    return _urban_series()[_URBAN_KEYS[source]][year]


def _urban_factor(source: str) -> float:
    values = _urban_series()[_URBAN_KEYS[source]]
    return values[2018] / values[2000]


def _window() -> dict:
    """Class shares and native pixel counts of the land-cover window."""
    if "window" not in _cache:
        from src.figures import landcover
        gisa, _, _ = landcover.impervious_mask(landcover.IMPERVIOUS_GISA, "gisa")
        gaia, _, _ = landcover.impervious_mask(landcover.IMPERVIOUS_GAIA, "gaia")
        rice, _ = landcover.rice_classes()
        _cache["window"] = {
            "impervious_gisa_percent": 100.0 * float(gisa.mean()),
            "impervious_gaia_percent": 100.0 * float(gaia.mean()),
            "rice_single_percent": 100.0 * float((rice == 1).mean()),
            "rice_double_percent": 100.0 * float((rice == 2).mean()),
            "rice_columns": int(rice.shape[1]),
            "impervious_columns": int(gisa.shape[1]),
            "cell_rice_combined":
                landcover.cell_values()[(31.325, 118.425)]
                ["rice_fraction_combined"],
            "cell_impervious_gisa":
                landcover.cell_values()[(31.325, 118.425)]["impervious_gisa"],
        }
    return _cache["window"]


def _rice() -> dict:
    """Rice areas and provincial shares, from the committed regional tables.

    The figure reads the same files through
    `src.figures.landcover_regional`, so a caption number and a drawn number
    cannot disagree without one of them failing here.
    """
    if "rice" not in _cache:
        from src.figures import landcover_regional as lr
        provincial = lr.provincial_rice()
        shares = lr.provincial_shares()
        ratios = lr.drawn_area_ratio()
        _cache["rice"] = {
            "total_km2": sum(v["single"] + v["double"]
                             for v in provincial.values()),
            "double_km2": sum(v["double"] for v in provincial.values()),
            "double_anhui_km2": provincial["Anhui"]["double"],
            "double_zhejiang_km2": provincial["Zhejiang"]["double"],
            "anhui_coverage": provincial["Anhui"]["assessed_over_polygon"],
            "drawn_over_true": ratios["total"],
            "share_shanghai_percent": 100.0 * shares["Shanghai"]["rice_single"],
            "share_jiangsu_percent": 100.0 * shares["Jiangsu"]["rice_single"],
            "urban_share_shanghai_percent":
                100.0 * shares["Shanghai"]["impervious"],
            "urban_share_jiangsu_percent":
                100.0 * shares["Jiangsu"]["impervious"],
            **{f"double_share_{name.lower()}_percent":
               (100.0 * v["double"] / (v["single"] + v["double"])
                if (v["single"] + v["double"]) else 0.0)
               for name, v in provincial.items()},
        }
    return _cache["rice"]


#: The four methane fields, as (artefact, column) pairs. The results draft
#: reports every field's spread and every field's baseline performance, and
#: before this pass only the operational field had resolvers.
FIELDS = {
    "raw": ("analysis_grid_2018.csv", "ch4_raw_ppb"),
    "operational": ("analysis_grid_2018.csv", "ch4_bias_corrected_ppb"),
    "blended": ("methane_blended_2018.csv", "ch4_blended_ppb"),
    "deseasonalised": ("methane_deseasonalised_2018.csv",
                       "ch4_deseasonalised_ppb"),
}


def _field_sd(name: str) -> float:
    """Between-cell standard deviation of one methane field, in ppb."""
    artefact, column = FIELDS[name]
    rows = _read_csv(PROCESSED / artefact)
    values = np.asarray([float(r[column]) for r in rows
                         if r[column] not in ("", None)], dtype="float64")
    return float(values.std())


def _suite(field: str, model: str, scheme: str, weighting: str) -> float:
    """One held-out R squared from one of the three baseline suites.

    The suites are separate artefacts with identical shape, so the results
    draft's field comparison is a lookup across three files rather than a
    column in one.
    """
    artefact = {"operational": "baseline_results_2018.csv",
                "blended": "baseline_results_blended_2018.csv",
                "deseasonalised": "baseline_results_deseasonalised_2018.csv",
                }[field]
    key = f"suite:{artefact}"
    if key not in _cache:
        _cache[key] = _read_csv(PROCESSED / artefact)
    for r in _cache[key]:
        if (r["model"] == model and r["scheme"] == scheme
                and r["weighting"] == weighting):
            return float(r["held_out_r2"])
    raise KeyError((field, model, scheme, weighting))


def _albedo_series_slope(series: str) -> float:
    """Unweighted SWIR albedo slope in ppb per unit albedo, for one series."""
    if "albedo_corr" not in _cache:
        _cache["albedo_corr"] = _read_csv(PROCESSED / "albedo_correction_2018.csv")
    for r in _cache["albedo_corr"]:
        if (r["albedo"] == "surface_albedo_SWIR" and r["series"] == series
                and r["weighting"] == "unweighted"):
            return float(r["slope_ppb_per_unit_albedo"])
    raise KeyError(series)


def _above_constant(field: str, model: str, scheme: str, weighting: str) -> float:
    """Held-out R squared above a constant fitted on the same training data.

    The interpretable column when the constant itself scores badly, which it
    does under leave-one-province-out: a province's mean differs from the
    domain's, so withholding a whole province penalises every model including
    the one with no predictors. `notes/decisions.md` records why nothing had
    computed this across all four combinations until 16 September 2026.
    """
    return (_suite(field, model, scheme, weighting)
            - _suite(field, "constant (global mean)", scheme, weighting))


def _suite_spread(field: str, model: str) -> float:
    """Range of held-out R squared across the four scheme-weighting combinations.

    The quantity that decides whether the four-way spread is a property of the
    predictor or of the evaluation. It is the latter: land cover has the
    smallest spread of any predictor in the suite.
    """
    values = [_suite(field, model, scheme, weighting)
              for scheme in ("spatial blocks", "leave-one-province-out")
              for weighting in ("unweighted", "by sounding count")]
    return max(values) - min(values)


def _albedo_series_pearson(series: str) -> float:
    """Unweighted SWIR albedo Pearson correlation, for one series."""
    if "albedo_corr" not in _cache:
        _cache["albedo_corr"] = _read_csv(PROCESSED / "albedo_correction_2018.csv")
    for r in _cache["albedo_corr"]:
        if (r["albedo"] == "surface_albedo_SWIR" and r["series"] == series
                and r["weighting"] == "unweighted"):
            return float(r["pearson"])
    raise KeyError(series)


def _deseason(predictor: str, column: str) -> float:
    """One cell of the deseasonalisation comparison, unweighted."""
    if "deseason" not in _cache:
        _cache["deseason"] = _read_csv(PROCESSED / "deseasonalisation_2018.csv")
    for r in _cache["deseason"]:
        if r["predictor"] == predictor and r["weighting"] == "unweighted":
            return float(r[column])
    raise KeyError(predictor)


def _dof() -> dict:
    """The effective-degrees-of-freedom table, which had no resolver until now.

    Tier 0 committed four artefacts and none of them was reachable from prose.
    The methods draft quotes all four, so they are resolved here: a capability
    claim whose numbers cannot be checked is the drift this mechanism exists to
    prevent, and these are the numbers the paper rests on.
    """
    if "dof" not in _cache:
        rows = _read_csv(PROCESSED / "correlation_dof_2018.csv")
        shrink = [float(r["shrinkage"]) for r in rows]
        eff = [float(r["effective_n"]) for r in rows]
        _cache["dof"] = {
            "rows": float(len(rows)),
            "shrinkage_min": min(shrink),
            "shrinkage_max": max(shrink),
            "effective_n_min": min(eff),
            "effective_n_max": max(eff),
            "verdict_changed": float(sum(
                1 for r in rows if r["verdict"] == "was significant, now is not")),
            "effective_n_median": float(np.median(eff)),
        }
    return _cache["dof"]


def _range() -> dict:
    """Residual semivariogram ranges against the cross-validation block size."""
    if "range" not in _cache:
        rows = _read_csv(PROCESSED / "residual_range_2018.csv")
        by = {(r["field"], r["model"]): r for r in rows}
        _cache["range"] = {
            "block_ns_km": float(rows[0]["block_ns_km"]),
            "block_ew_km": float(rows[0]["block_ew_km"]),
            "operational_impervious_km":
                float(by[("operational", "OLS impervious fraction")]
                      ["half_sill_range_km"]),
            "blended_impervious_km":
                float(by[("blended", "OLS impervious fraction")]
                      ["half_sill_range_km"]),
            "operational_field_km":
                float(by[("operational", "the field itself (no model)")]
                      ["half_sill_range_km"]),
            "blended_field_km":
                float(by[("blended", "the field itself (no model)")]
                      ["half_sill_range_km"]),
            "operational_full_km":
                float(by[("operational",
                          "OLS full covariates (albedo SWIR, NIR, SZA)")]
                      ["half_sill_range_km"]),
            "too_small": float(sum(1 for r in rows
                                   if r["verdict"].startswith("residual still"))),
            "models": float(len(rows)),
        }
    return _cache["range"]


def _cycle(quantity: str) -> float:
    """One row of the fitted seasonal cycle table, by its `quantity` label."""
    if "cycle" not in _cache:
        _cache["cycle"] = {r["quantity"]: r for r
                           in _read_csv(PROCESSED / "seasonal_cycle_2018.csv")}
    return float(_cache["cycle"][quantity]["value"])


def _stripe():
    """Across-track offset spread, low and high, in ppb.

    Recomputed here from the checkpoint rather than read from a table, because
    the stripe is a property of the accumulator and no committed artefact
    carries the per-column offsets. Local-tier: returns NaN without the
    checkpoint, which the claim checker reports as unresolvable rather than
    passing silently.
    """
    if "stripe" not in _cache:
        path = REPO / "data" / "interim" / "extent_2018_extended.npz"
        if not path.exists():
            _cache["stripe"] = (float("nan"),) * 3
        else:
            data = np.load(path, allow_pickle=False)
            sums = data["atsum::methane_mixing_ratio_bias_corrected"]
            counts = data["across_track_counts"].astype("int64")
            used = counts > 0
            means = sums[used] / counts[used]
            offsets = means - float(sums.sum() / counts.sum())
            _cache["stripe"] = (float(offsets.std()), float(offsets.min()),
                                float(offsets.max()))
    return _cache["stripe"]


def _weighting():
    """Correlation between the two weightings, and the spatial variance share."""
    if "weighting" not in _cache:
        rows = [r for r in _read_csv(PROCESSED / "cell_quality_2018.csv")
                if r["weight_representativeness"]]
        n = np.array([int(r["sounding_count"]) for r in rows], dtype="float64")
        sd = np.array([float(r["within_cell_sd_ppb"]) for r in rows])
        w = np.array([float(r["weight_representativeness"]) for r in rows])
        share = sd ** 2 / (29.0 ** 2 / n + sd ** 2)
        _cache["weighting"] = (float(np.corrcoef(n, w)[0, 1]),
                               float(np.median(share) * 100.0))
    return _cache["weighting"]


def _equivalence() -> list[dict]:
    """The equivalence table, one row per field, predictor and weighting."""
    if "equiv" not in _cache:
        _cache["equiv"] = _read_csv(PROCESSED / "equivalence_bounds_2018.csv")
    return _cache["equiv"]


def _equiv_count(predictor: str, outcome: str) -> int:
    """How many of a predictor's rows reach one of the three outcomes."""
    return sum(1 for r in _equivalence()
               if r["predictor"] == predictor
               and r["verdict_comparative"].startswith(outcome))


def _curve() -> list[dict]:
    if "curve" not in _cache:
        _cache["curve"] = _read_csv(PROCESSED / "specification_curve_2018.csv")
    return _cache["curve"]


def _claims() -> list[dict]:
    """The claim inventory, one row per numeric claim."""
    if "claims" not in _cache:
        _cache["claims"] = _read_csv(PROCESSED / "claim_inventory_2026.csv")
    return _cache["claims"]


def _claim_count(category: str = "", source: str = "") -> int:
    rows = _claims()
    if category:
        rows = [r for r in rows if r["category"] == category]
    if source:
        rows = [r for r in rows if source in r["source"]]
    return len(rows)


def _sector(quantity: str) -> float:
    """One row of the sectoral composition table."""
    if "sector" not in _cache:
        _cache["sector"] = {r["quantity"]: r for r
                            in _read_csv(PROCESSED / "sector_composition_2018.csv")}
    return float(_cache["sector"][quantity]["value"])


def _change(quantity: str) -> float:
    """One row of the change-design power table."""
    if "change" not in _cache:
        _cache["change"] = {r["quantity"]: r for r
                            in _read_csv(PROCESSED / "change_design_power_2018.csv")}
    return float(_cache["change"][quantity]["value"])


def _tccon(quantity: str) -> float:
    """One row of the Hefei TCCON coincidence table.

    The table is written by a network-tier recipe because the TCCON Data
    License reserves redistribution, so the station file cannot be committed
    and the counts stand in for it.
    """
    if "tccon" not in _cache:
        _cache["tccon"] = {r["quantity"]: r for r
                           in _read_csv(PROCESSED / "tccon_hefei_2018.csv")}
    return float(_cache["tccon"][quantity]["value"])


def _register_entries() -> int:
    """DOIs the reference register names, via the BibTeX generator's own parser.

    Read from the generator rather than counted here, so the register's stated
    total and the checker's cannot drift apart -- which they had, the register
    claiming 189 where the BibTeX held 194.
    """
    if "register" not in _cache:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_brb", REPO / "scripts" / "build_references_bib.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _cache["register"] = len(module.register_dois())
    return int(_cache["register"])


def _reference_use(column: str, value: str = "") -> int:
    """Rows of the reference-use audit, optionally where `column` is non-empty."""
    if "refuse" not in _cache:
        _cache["refuse"] = _read_csv(PROCESSED / "reference_use_2026.csv")
    rows = _cache["refuse"]
    if not column:
        return len(rows)
    if value:
        return sum(1 for r in rows if r[column] == value)
    return sum(1 for r in rows if r[column])


def _quality_granules() -> list[dict]:
    """Per-granule quality accounting from the Tier 3 retention pass."""
    if "qgran" not in _cache:
        _cache["qgran"] = _read_csv(PROCESSED / "granule_quality_2018.csv")
    return _cache["qgran"]


def _quality_cells() -> list[dict]:
    if "qcell" not in _cache:
        _cache["qcell"] = _read_csv(PROCESSED / "cell_quality_2018.csv")
    return _cache["qcell"]


def _qsum(column: str) -> int:
    return int(sum(int(r[column]) for r in _quality_granules()))


def _sensitivity(variant: str, model: str, scheme: str, weighting: str,
                 column: str = "held_out_r2") -> float:
    """One row of the preprocessing sensitivity table."""
    if "sens" not in _cache:
        _cache["sens"] = {
            (r["variant"], r["model"], r["scheme"], r["weighting"]): r
            for r in _read_csv(PROCESSED / "preprocessing_sensitivity_2018.csv")}
    return float(_cache["sens"][(variant, model, scheme, weighting)][column])


def _resolution(resolution: str, quantity: str) -> float:
    """One row of the grid-resolution table, by resolution and quantity label.

    `resolution` is the column's literal text -- "0.1", "0.25", or "" for the
    rows belonging to no single resolution. Named `_resolution` rather than
    `_grid` because `_grid` is the analysis grid's reader and both the function
    name and the cache key were already taken.
    """
    if "resolution" not in _cache:
        _cache["resolution"] = {
            (r["resolution_deg"], r["quantity"]): r for r
            in _read_csv(PROCESSED / "grid_resolution_2018.csv")}
    return float(_cache["resolution"][(resolution, quantity)]["value"])


def _atten(quantity: str) -> float:
    """One row of the attenuation bound table, by its `quantity` label."""
    if "atten" not in _cache:
        _cache["atten"] = {r["quantity"]: r for r
                           in _read_csv(PROCESSED / "attenuation_bound_2018.csv")}
    return float(_cache["atten"][quantity]["value"])


def _disagree(year: str, resolution: str, column: str) -> float:
    """One cell of the GAIA-GISA disagreement decomposition."""
    if "disagree" not in _cache:
        _cache["disagree"] = _read_csv(PROCESSED / "urban_disagreement_2018.csv")
    for row in _cache["disagree"]:
        if row["year"] == year and row["resolution"] == resolution:
            return float(row[column])
    raise KeyError((year, resolution, column))


def _loo(model: str, radius: str, column: str = "r2_above_constant") -> float:
    if "loo" not in _cache:
        _cache["loo"] = _read_csv(PROCESSED / "buffered_loo_2018.csv")
    for r in _cache["loo"]:
        if (r["field"] == "operational" and r["model"].startswith(model)
                and r["radius_km"] == radius):
            return float(r[column])
    raise KeyError((model, radius))


def _dofs(quantity: str) -> float:
    """One row of the inversion DOFS table, by its `quantity` label."""
    if "dofs" not in _cache:
        _cache["dofs"] = {r["quantity"]: r
                          for r in _read_csv(PROCESSED / "inversion_dofs_2018.csv")}
    return float(_cache["dofs"][quantity]["value"])


def _dofs_cells_above_half() -> float:
    """How many cells reach an averaging-kernel sensitivity above 0.5.

    Every row of the sweep records this in its own note, and every row records
    zero. The claim the paper makes is about the whole sweep, so the resolver
    reads every row rather than one.
    """
    if "dofs" not in _cache:
        _dofs("k")
    counts = {r["note"].split("cells with a > 0.5:")[1].strip()
              for r in _cache["dofs"].values()
              if "cells with a > 0.5:" in r["note"]}
    if len(counts) != 1:
        raise ValueError(f"the sweep disagrees with itself: {counts}")
    return float(counts.pop())


def _baseline() -> dict:
    """Held-out and in-sample metrics for the diagnostic figure's four models.

    Read through `src.figures.observed_predicted`, which is what the figure
    reads, so a caption number and a drawn number cannot disagree.
    """
    if "baseline" not in _cache:
        import csv as _csv

        from src.figures import observed_predicted as op
        metrics = op.load_metrics()
        predictions = op.load_predictions()
        in_sample = {}
        with op.RESULTS.open(newline="") as handle:
            for row in _csv.DictReader(handle):
                if (row["scheme"] == op.SCHEME
                        and row["weighting"] == op.WEIGHTING):
                    in_sample[row["model"]] = float(row["in_sample_r2"])

        def span(name):
            field = predictions[name]["predicted"]
            return float(field.max() - field.min())

        observed = predictions["constant (global mean)"]["observed"]
        _cache["baseline"] = {
            "constant_r2": metrics[("constant (global mean)", op.SCHEME,
                                    op.WEIGHTING)]["r2"],
            "impervious_r2": metrics[("OLS impervious_fraction", op.SCHEME,
                                      op.WEIGHTING)]["r2"],
            "impervious_rmse": metrics[("OLS impervious_fraction", op.SCHEME,
                                        op.WEIGHTING)]["rmse"],
            "null_r2": metrics[("spatial null (queen neighbour mean)",
                                op.SCHEME, op.WEIGHTING)]["r2"],
            "null_in_sample_r2": in_sample["spatial null (queen neighbour mean)"],
            "wind_r2": metrics[("OLS wind (u, v, speed)", op.SCHEME,
                                op.WEIGHTING)]["r2"],
            "observed_span_ppb": float(observed.max() - observed.min()),
            "impervious_span_ppb": span("OLS impervious_fraction"),
            "constant_span_ppb": span("constant (global mean)"),
            "null_span_ppb": span("spatial null (queen neighbour mean)"),
            "rice_alone_r2": _rice_sample_r2("OLS rice_fraction_single"),
            "rice_plus_impervious_r2": _rice_sample_r2(
                "OLS impervious_fraction + rice_fraction_single"),
            "impervious_rice_sample_r2": _rice_sample_r2(
                "OLS impervious_fraction [rice sample]"),
        }
    return _cache["baseline"]


def _pipeline() -> dict:
    """What the two framework figures quote, from the routes they draw from."""
    if "pipeline" not in _cache:
        from src.figures import diagram
        from src.figures import framework_pipeline as fp

        nodes = fp.nodes()
        tiers = fp.recipe_tiers()
        outline = diagram.outline_report()
        _cache["pipeline"] = {
            "shapes_declared": float(len(diagram.SHAPES)),
            "shapes_drawn": float(len({n.shape for n in nodes})),
            "outline_pairs": float(outline["pairs"]),
            "outline_min": outline["min_difference"],
            "nodes": float(len(nodes)),
            "edges": float(len(fp.edges())),
            "paths_named": float(sum(len(n.exists) for n in nodes)),
            "gates": float(sum(1 for n in nodes if n.shape == "decision")),
            "fetch_routes": float(sum(1 for n in nodes if n.shape == "data")),
            "recipes": float(tiers["total"]),
            "recipes_committed": float(tiers.get("continuously", 0)),
            "recipes_local": float(tiers.get("on_local", 0)),
            "recipes_network": float(tiers.get("on_demand", 0)),
            "figure_pairs": float(fp.figure_pairs()),
        }
    return _cache["pipeline"]


def _collinear() -> dict:
    """What the albedo collinearity figure quotes, from the route it draws.

    Keyed `collinear` rather than `albedo` because `_albedo_slope` already owns
    that cache key and `albedo.slope_raw` and `albedo.slope_corrected` already
    exist; this adds the correlations, not the slopes.
    """
    if "collinear" not in _cache:
        from src.figures import albedo_collinearity as ac

        cells = ac.load_cells()
        computed = ac.associations(cells)
        corrected = computed[("bias corrected", "unweighted")]
        weighted = computed[("bias corrected", "by sounding count")]
        raw = computed[("raw retrieval", "unweighted")]
        raw_weighted = computed[("raw retrieval", "by sounding count")]
        fitted = ac.slopes()  # noqa: F841 -- kept for the reduction below
        _cache["collinear"] = {
            "cells": float(cells.n),
            "negative_cells": float(ac.negative_albedo(cells)),
            "negative_percent": 100.0 * ac.negative_albedo(cells) / cells.n,
            "collinearity": corrected["albedo_predictor"].spearman,
            "collinearity_weighted": weighted["albedo_predictor"].spearman,
            "methane_albedo": corrected["methane_albedo"].pearson,
            "methane_albedo_weighted": weighted["methane_albedo"].pearson,
            "methane_albedo_raw": raw["methane_albedo"].pearson,
            "zero_order": corrected["methane_predictor"].pearson,
            "zero_order_weighted": weighted["methane_predictor"].pearson,
            "partial": corrected["partial"].pearson,
            "partial_p": corrected["partial"].pearson_p,
            "partial_weighted": weighted["partial"].pearson,
            "partial_weighted_p": weighted["partial"].pearson_p,
            "zero_order_raw": raw["methane_predictor"].pearson,
            "partial_raw": raw["partial"].pearson,
            "partial_raw_p": raw["partial"].pearson_p,
            "partial_raw_weighted": raw_weighted["partial"].pearson,
            "reduction_percent": 100.0 * ac.correction_reduction("unweighted"),
            "reduction_weighted_percent":
                100.0 * ac.correction_reduction("by sounding count"),
        }
    return _cache["collinear"]


def _reproduction() -> dict:
    """What the reproduction status figure quotes, from the route it draws."""
    if "reproduction" not in _cache:
        from src.figures import diagram
        from src.figures import framework_reproduction as fr

        rows = fr.rows()
        cited = {number for row in rows for number in row.errata}
        states = [row.original for row in rows]
        _cache["reproduction"] = {
            "stages": float(len(rows)),
            "columns": float(len(fr.COLUMNS)),
            "states": float(len(diagram.STATE_GLYPH)),
            "source_states": float(len(diagram.STATE_GLYPH) - 1),
            "intact": float(sum(1 for row in rows if row.intact)),
            "errata_sections": float(len(fr.errata_sections())),
            "errata_cited": float(len(cited)),
            "errata_chapters": float(len({n.split(".")[0] for n in cited})),
            "original_observed": float(states.count("state_observed")),
            "original_incorrect": float(states.count("state_incorrect")),
            "dependent_rows": float(sum(1 for row in rows
                                        if row.kind == fr.DEPENDENT)),
            "both_rows": float(sum(1 for row in rows
                                   if row.kind == fr.BOTH)),
        }
    return _cache["reproduction"]


def _residual() -> dict:
    """What the model field and residual figure quotes, from the same route."""
    if "residual" not in _cache:
        import numpy as _np

        from src.figures import fields as _fields
        from src.figures import residual_field as rf

        observed, predicted, residual, absent = rf.load_field()
        low, high = rf.shared_ends(observed, predicted)
        values = residual[~absent]
        structure = rf.structure_report(observed, residual, absent)
        _cache["residual"] = {
            "observed_moran": structure["observed"]["i"],
            "residual_moran": structure["residual"]["i"],
            "moran_removed_percent": 100.0 * (
                1.0 - structure["residual"]["i"] / structure["observed"]["i"]),
            "isolated_cells": float(structure["residual"]["isolated"]),
            "permutations": float(rf.PERMUTATIONS),
            "scale_low_ppb": low,
            "scale_high_ppb": high,
            "residual_low_ppb": float(values.min()),
            "residual_high_ppb": float(values.max()),
            "residual_sd_ppb": float(values.std(ddof=1)),
            "scale_limit_ppb": float(_fields.RESIDUAL_LIMIT),
            "clipped_cells": float(
                _np.sum(_np.abs(values) > _fields.RESIDUAL_LIMIT)),
            "absent_cells": float(absent.sum()),
            "observed_cells": float((~absent).sum()),
        }
    return _cache["residual"]


def _rice_sample_r2(model: str) -> float:
    """Held-out R squared on the 531-cell rice sample, same scheme."""
    import csv as _csv

    from src.figures import observed_predicted as op
    with op.RESULTS.open(newline="") as handle:
        for row in _csv.DictReader(handle):
            if (row["model"] == model and row["scheme"] == op.SCHEME
                    and row["weighting"] == op.WEIGHTING):
                return float(row["held_out_r2"])
    raise KeyError(model)


def _albedo_slope(series: str) -> float:
    if "albedo" not in _cache:
        with (PROCESSED / "albedo_correction_2018.csv").open(newline="") as h:
            _cache["albedo"] = list(csv.DictReader(h))
    row = next(r for r in _cache["albedo"]
               if r["series"] == series and r["weighting"] == "unweighted"
               and r["albedo"] == "surface_albedo_SWIR")
    return float(row["slope_ppb_per_unit_albedo"])


def _shares() -> np.ndarray:
    keys = [k for k in _grid()[0] if k.startswith("share_")]
    return np.array([[float(r[k]) if r[k] else 0.0 for k in keys]
                     for r in _grid()])


#: name -> a callable returning the current value. Adding a quantity here and a
#: marker in the prose is what brings a claim under the check.
QUANTITIES = {
    "composite.covered_cells": lambda: int((_composite()[2] > 0).sum()),
    "composite.uncovered_cells": lambda: int((_composite()[2] == 0).sum()),
    "composite.total_cells": lambda: int(_composite()[2].size),
    "composite.soundings": lambda: int(_composite()[2].sum()),
    "composite.coverage_percent":
        lambda: 100.0 * (_composite()[2] > 0).sum() / _composite()[2].size,
    "composite.median_soundings":
        lambda: float(np.median(_composite()[2][_composite()[2] > 0])),
    "composite.max_soundings": lambda: int(_composite()[2].max()),
    "composite.granules_gridded": lambda: int(_composite()[3]["granules_gridded"]),
    "composite.granules_with_data":
        lambda: int(_composite()[3]["granules_with_data"]),
    "composite.bias_mean": lambda: float(
        (_composite()[0] - _composite()[1])[_composite()[2] > 0].mean()),
    "composite.min_soundings": lambda: int(_composite()[2][_composite()[2] > 0].min()),
    "composite.uncovered_percent":
        lambda: 100.0 * (_composite()[2] == 0).sum() / _composite()[2].size,
    "composite.absent_components": lambda: _absence_blocks()[0],
    "composite.largest_absent_block": lambda: _absence_blocks()[1],
    "composite.absent_on_land": _absent_on_land,
    "composite.absent_median_elevation":
        lambda: float(np.median(_cell_elevation()[_composite()[2] == 0])),
    "composite.covered_median_elevation":
        lambda: float(np.median(_cell_elevation()[_composite()[2] > 0])),
    "composite.absent_above_500m":
        lambda: int((_cell_elevation()[_composite()[2] == 0] > 500).sum()),
    "composite.covered_above_500m":
        lambda: int((_cell_elevation()[_composite()[2] > 0] > 500).sum()),
    "composite.coast_median_soundings":
        lambda: _median_soundings((_sea_fraction() >= 0.25)
                                  & (_sea_fraction() <= 0.99)),
    "composite.land_median_soundings":
        lambda: _median_soundings(_sea_fraction() < 0.01),
    "urban.gaia_2000": lambda: _urban("gaia", 2000),
    "urban.gaia_2010": lambda: _urban("gaia", 2010),
    "urban.gaia_2018": lambda: _urban("gaia", 2018),
    "urban.gisa_2000": lambda: _urban("gisa", 2000),
    "urban.gisa_2010": lambda: _urban("gisa", 2010),
    "urban.gisa_2018": lambda: _urban("gisa", 2018),
    "urban.thesis_2000": lambda: _urban("thesis", 2000),
    "urban.thesis_2010": lambda: _urban("thesis", 2010),
    "urban.thesis_2018": lambda: _urban("thesis", 2018),
    "urban.gaia_factor": lambda: _urban_factor("gaia"),
    "urban.gisa_factor": lambda: _urban_factor("gisa"),
    "urban.thesis_factor": lambda: _urban_factor("thesis"),
    "urban.gaia_2019": lambda: _urban("gaia", 2019),
    "urban.gisa_2019": lambda: _urban("gisa", 2019),
    "urban.gisa_over_gaia_2018":
        lambda: _urban("gisa", 2018) / _urban("gaia", 2018),
    "window.impervious_gisa_percent":
        lambda: _window()["impervious_gisa_percent"],
    "window.impervious_gaia_percent":
        lambda: _window()["impervious_gaia_percent"],
    "window.rice_single_percent": lambda: _window()["rice_single_percent"],
    "window.rice_double_percent": lambda: _window()["rice_double_percent"],
    "window.rice_columns": lambda: _window()["rice_columns"],
    "window.impervious_columns": lambda: _window()["impervious_columns"],
    "window.cell_rice_combined": lambda: _window()["cell_rice_combined"],
    "window.cell_impervious_gisa": lambda: _window()["cell_impervious_gisa"],
    # The caption speaks in percent where the tables store a fraction. Both
    # spellings exist rather than the prose converting, because a marked claim
    # has to name the quantity it is, not one a reader must rescale.
    "window.cell_rice_combined_percent":
        lambda: 100.0 * _window()["cell_rice_combined"],
    "window.cell_impervious_gisa_percent":
        lambda: 100.0 * _window()["cell_impervious_gisa"],
    "rice.total_km2": lambda: _rice()["total_km2"],
    "rice.double_km2": lambda: _rice()["double_km2"],
    "rice.double_anhui_km2": lambda: _rice()["double_anhui_km2"],
    "rice.double_zhejiang_km2": lambda: _rice()["double_zhejiang_km2"],
    "rice.anhui_coverage": lambda: _rice()["anhui_coverage"],
    # The prose speaks in percent where the table stores a fraction, and a
    # marked claim must name the quantity it is rather than one a reader
    # rescales; the same pair exists for the window figures above.
    "rice.anhui_coverage_percent": lambda: 100.0 * _rice()["anhui_coverage"],
    "rice.drawn_over_true": lambda: _rice()["drawn_over_true"],
    "rice.share_shanghai_percent": lambda: _rice()["share_shanghai_percent"],
    "rice.share_jiangsu_percent": lambda: _rice()["share_jiangsu_percent"],
    "urban.share_shanghai_percent":
        lambda: _rice()["urban_share_shanghai_percent"],
    "urban.share_jiangsu_percent":
        lambda: _rice()["urban_share_jiangsu_percent"],
    # Double-cropped share of each province's paddy area. `notes/grounding-rice.md`
    # turns on these: the sown-against-planted definitional gap can only exist
    # where a field is cropped twice, so a province at zero cannot have it.
    "rice.double_share_shanghai_percent":
        lambda: _rice()["double_share_shanghai_percent"],
    "rice.double_share_jiangsu_percent":
        lambda: _rice()["double_share_jiangsu_percent"],
    "rice.double_share_anhui_percent":
        lambda: _rice()["double_share_anhui_percent"],
    "rice.double_share_zhejiang_percent":
        lambda: _rice()["double_share_zhejiang_percent"],
    "baseline.constant_r2": lambda: _baseline()["constant_r2"],
    "baseline.impervious_r2": lambda: _baseline()["impervious_r2"],
    "baseline.impervious_rmse": lambda: _baseline()["impervious_rmse"],
    "baseline.null_r2": lambda: _baseline()["null_r2"],
    "baseline.null_in_sample_r2": lambda: _baseline()["null_in_sample_r2"],
    "baseline.wind_r2": lambda: _baseline()["wind_r2"],
    "baseline.observed_span_ppb": lambda: _baseline()["observed_span_ppb"],
    "baseline.impervious_span_ppb": lambda: _baseline()["impervious_span_ppb"],
    "baseline.constant_span_ppb": lambda: _baseline()["constant_span_ppb"],
    "baseline.null_span_ppb": lambda: _baseline()["null_span_ppb"],
    "baseline.rice_alone_r2": lambda: _baseline()["rice_alone_r2"],
    "baseline.rice_plus_impervious_r2":
        lambda: _baseline()["rice_plus_impervious_r2"],
    "baseline.impervious_rice_sample_r2":
        lambda: _baseline()["impervious_rice_sample_r2"],
    "collinear.cells": lambda: _collinear()["cells"],
    "collinear.negative_cells": lambda: _collinear()["negative_cells"],
    "collinear.negative_percent": lambda: _collinear()["negative_percent"],
    "collinear.collinearity": lambda: _collinear()["collinearity"],
    "collinear.collinearity_weighted": lambda: _collinear()["collinearity_weighted"],
    "collinear.methane_albedo": lambda: _collinear()["methane_albedo"],
    "collinear.methane_albedo_weighted": lambda: _collinear()["methane_albedo_weighted"],
    "collinear.methane_albedo_raw": lambda: _collinear()["methane_albedo_raw"],
    "collinear.zero_order": lambda: _collinear()["zero_order"],
    "collinear.zero_order_weighted": lambda: _collinear()["zero_order_weighted"],
    "collinear.partial": lambda: _collinear()["partial"],
    "collinear.partial_p": lambda: _collinear()["partial_p"],
    "collinear.partial_weighted": lambda: _collinear()["partial_weighted"],
    "collinear.partial_weighted_p": lambda: _collinear()["partial_weighted_p"],
    "collinear.zero_order_raw": lambda: _collinear()["zero_order_raw"],
    "collinear.partial_raw": lambda: _collinear()["partial_raw"],
    "collinear.partial_raw_p": lambda: _collinear()["partial_raw_p"],
    "collinear.partial_raw_weighted": lambda: _collinear()["partial_raw_weighted"],
    "collinear.reduction_percent": lambda: _collinear()["reduction_percent"],
    "collinear.reduction_weighted_percent": lambda: _collinear()["reduction_weighted_percent"],
    "reproduction.stages": lambda: _reproduction()["stages"],
    "reproduction.columns": lambda: _reproduction()["columns"],
    "reproduction.states": lambda: _reproduction()["states"],
    "reproduction.source_states": lambda: _reproduction()["source_states"],
    "reproduction.intact": lambda: _reproduction()["intact"],
    "reproduction.errata_sections": lambda: _reproduction()["errata_sections"],
    "reproduction.errata_cited": lambda: _reproduction()["errata_cited"],
    "reproduction.errata_chapters": lambda: _reproduction()["errata_chapters"],
    "reproduction.original_observed":
        lambda: _reproduction()["original_observed"],
    "reproduction.original_incorrect":
        lambda: _reproduction()["original_incorrect"],
    "reproduction.dependent_rows": lambda: _reproduction()["dependent_rows"],
    "reproduction.both_rows": lambda: _reproduction()["both_rows"],
    "pipeline.shapes_declared": lambda: _pipeline()["shapes_declared"],
    "pipeline.shapes_drawn": lambda: _pipeline()["shapes_drawn"],
    "pipeline.outline_pairs": lambda: _pipeline()["outline_pairs"],
    "pipeline.outline_min": lambda: _pipeline()["outline_min"],
    "pipeline.nodes": lambda: _pipeline()["nodes"],
    "pipeline.edges": lambda: _pipeline()["edges"],
    "pipeline.paths_named": lambda: _pipeline()["paths_named"],
    "pipeline.gates": lambda: _pipeline()["gates"],
    "pipeline.fetch_routes": lambda: _pipeline()["fetch_routes"],
    "pipeline.recipes": lambda: _pipeline()["recipes"],
    "pipeline.recipes_committed": lambda: _pipeline()["recipes_committed"],
    "pipeline.recipes_local": lambda: _pipeline()["recipes_local"],
    "pipeline.recipes_network": lambda: _pipeline()["recipes_network"],
    "pipeline.figure_pairs": lambda: _pipeline()["figure_pairs"],
    "residual.observed_moran": lambda: _residual()["observed_moran"],
    "residual.residual_moran": lambda: _residual()["residual_moran"],
    "residual.moran_removed_percent":
        lambda: _residual()["moran_removed_percent"],
    "residual.isolated_cells": lambda: _residual()["isolated_cells"],
    "residual.permutations": lambda: _residual()["permutations"],
    "residual.scale_low_ppb": lambda: _residual()["scale_low_ppb"],
    "residual.scale_high_ppb": lambda: _residual()["scale_high_ppb"],
    "residual.residual_low_ppb": lambda: _residual()["residual_low_ppb"],
    "residual.residual_high_ppb": lambda: _residual()["residual_high_ppb"],
    "residual.residual_sd_ppb": lambda: _residual()["residual_sd_ppb"],
    "residual.scale_limit_ppb": lambda: _residual()["scale_limit_ppb"],
    "residual.clipped_cells": lambda: _residual()["clipped_cells"],
    "residual.absent_cells": lambda: _residual()["absent_cells"],
    "residual.observed_cells": lambda: _residual()["observed_cells"],
    "albedo.slope_corrected": lambda: _albedo_slope("bias corrected"),
    "albedo.slope_raw": lambda: _albedo_slope("raw retrieval"),

    "field.sd_raw": lambda: _field_sd("raw"),
    "field.sd_operational": lambda: _field_sd("operational"),
    "field.sd_blended": lambda: _field_sd("blended"),
    "field.sd_deseasonalised": lambda: _field_sd("deseasonalised"),
    "albedo.slope_deseasonalised": lambda: _albedo_series_slope("deseasonalised"),
    # Added 16 September 2026, when the blended series was added to the
    # artefact. The measurement already existed in `notes/decisions.md` under
    # *The albedo dependence rose*; what it lacked was a row anything could
    # resolve, which is why the results draft could not quote it.
    "albedo.slope_blended": lambda: _albedo_series_slope("blended"),
    "albedo.pearson_blended":
        lambda: _albedo_series_pearson("blended"),
    "albedo.pearson_corrected":
        lambda: _albedo_series_pearson("bias corrected"),
    "albedo.blended_over_corrected_percent":
        lambda: 100.0 * (_albedo_series_slope("blended")
                         / _albedo_series_slope("bias corrected") - 1.0),
    "albedo.slope_correction": lambda: _albedo_series_slope("the correction itself"),
    # The land-cover models and the spatial null on each field, under the
    # scheme and weighting the draft reports as primary.
    "suite.impervious_operational":
        lambda: _suite("operational", "OLS impervious_fraction",
                       "spatial blocks", "unweighted"),
    "suite.impervious_blended":
        lambda: _suite("blended", "OLS impervious_fraction",
                       "spatial blocks", "unweighted"),
    "suite.impervious_deseasonalised":
        lambda: _suite("deseasonalised", "OLS impervious_fraction",
                       "spatial blocks", "unweighted"),
    "suite.null_operational":
        lambda: _suite("operational", "spatial null (queen neighbour mean)",
                       "spatial blocks", "unweighted"),
    "suite.null_blended":
        lambda: _suite("blended", "spatial null (queen neighbour mean)",
                       "spatial blocks", "unweighted"),
    "suite.null_deseasonalised":
        lambda: _suite("deseasonalised", "spatial null (queen neighbour mean)",
                       "spatial blocks", "unweighted"),
    "suite.impervious_operational_lopo":
        lambda: _suite("operational", "OLS impervious_fraction",
                       "leave-one-province-out", "unweighted"),
    "suite.impervious_operational_weighted":
        lambda: _suite("operational", "OLS impervious_fraction",
                       "spatial blocks", "by sounding count"),
    "suite.both_operational_lopo_weighted":
        lambda: _suite("operational",
                       "OLS impervious_fraction + rice_fraction_single",
                       "leave-one-province-out", "by sounding count"),
    # The four-way grid, above a constant on the same training data.
    "above.impervious_bu":
        lambda: _above_constant("operational", "OLS impervious_fraction",
                                "spatial blocks", "unweighted"),
    "above.impervious_bw":
        lambda: _above_constant("operational", "OLS impervious_fraction",
                                "spatial blocks", "by sounding count"),
    "above.impervious_pu":
        lambda: _above_constant("operational", "OLS impervious_fraction",
                                "leave-one-province-out", "unweighted"),
    "above.impervious_pw":
        lambda: _above_constant("operational", "OLS impervious_fraction",
                                "leave-one-province-out", "by sounding count"),
    "above.null_pu":
        lambda: _above_constant("operational",
                                "spatial null (queen neighbour mean)",
                                "leave-one-province-out", "unweighted"),
    "above.rice_combined_pu":
        lambda: _above_constant("operational", "OLS rice_fraction_combined",
                                "leave-one-province-out", "unweighted"),
    # Four-way spreads. The comparison that settles whether the spread belongs
    # to land cover or to the evaluation design.
    "spread.impervious": lambda: _suite_spread("operational",
                                               "OLS impervious_fraction"),
    "spread.rice": lambda: _suite_spread("operational",
                                         "OLS rice_fraction_single"),
    "spread.both": lambda: _suite_spread(
        "operational", "OLS impervious_fraction + rice_fraction_single"),
    "spread.wind": lambda: _suite_spread("operational",
                                         "OLS wind (u, v, speed)"),
    "spread.albedo": lambda: _suite_spread("operational", "OLS albedo (SWIR)"),
    "spread.null": lambda: _suite_spread(
        "operational", "spatial null (queen neighbour mean)"),
    "spread.sampling": lambda: _suite_spread(
        "operational", "OLS sampling composition (when observed)"),
    "spread.trend": lambda: _suite_spread("operational",
                                          "OLS trend surface (lat, lon)"),
    "suite.rice_combined_pu":
        lambda: _suite("operational", "OLS rice_fraction_combined",
                       "leave-one-province-out", "unweighted"),
    "suite.null_operational_pu":
        lambda: _suite("operational", "spatial null (queen neighbour mean)",
                       "leave-one-province-out", "unweighted"),
    "suite.albedo_operational":
        lambda: _suite("operational", "OLS albedo (SWIR)",
                       "spatial blocks", "unweighted"),
    # Whether removing the seasonal cycle at the sounding level changes the
    # land-cover association. This is the fourth field's whole purpose.
    "deseason.impervious_raw": lambda: _deseason("impervious_fraction", "raw_pearson"),
    "deseason.impervious_mu": lambda: _deseason("impervious_fraction", "mu_pearson"),
    "deseason.impervious_change":
        lambda: _deseason("impervious_fraction", "pearson_change"),
    "deseason.rice_raw": lambda: _deseason("rice_fraction_single", "raw_pearson"),
    "deseason.rice_change":
        lambda: _deseason("rice_fraction_single", "pearson_change"),
    "deseason.doy_raw": lambda: _deseason("mean_day_of_year", "raw_pearson"),
    "deseason.doy_mu": lambda: _deseason("mean_day_of_year", "mu_pearson"),
    "dofs.prior_free_median":
        lambda: _dofs("emission for a = 0.5, median cell"),
    "dofs.prior_free_best":
        lambda: _dofs("emission for a = 0.5, best-observed cell"),
    "dof.effective_n_median": lambda: _dof()["effective_n_median"],
    # The prose speaks in percent where the table stores a fraction.
    "dof.shrinkage_min_percent": lambda: 100.0 * _dof()["shrinkage_min"],
    "dof.shrinkage_max_percent": lambda: 100.0 * _dof()["shrinkage_max"],
    # How much of the zero-order impervious association survives control for
    # albedo. `collinear.reduction_percent` is a different quantity -- how much
    # the operational bias correction reduced the field's albedo slope -- and
    # the two were conflated in a first draft of the results section.
    "collinear.partial_attenuation_percent":
        lambda: 100.0 * (1.0 - _collinear()["partial"]
                         / _collinear()["zero_order"]),
    "dof.rows": lambda: _dof()["rows"],
    "dof.shrinkage_min": lambda: _dof()["shrinkage_min"],
    "dof.shrinkage_max": lambda: _dof()["shrinkage_max"],
    "dof.effective_n_min": lambda: _dof()["effective_n_min"],
    "dof.effective_n_max": lambda: _dof()["effective_n_max"],
    "dof.verdict_changed": lambda: _dof()["verdict_changed"],
    # Added for queue item 11, the attenuation bound. Every one of these is a
    # bound or a sensitivity value; none is an estimate.
    # Queue item 12a: the fitted seasonal cycle, which existed only in prose.
    # Coverage and precision across candidate grid resolutions. The 0.25
    # degree rows are measured; the finer ones are projections whose
    # direction the artefact's `basis` and `note` columns state.
    "resolution.cells_025": lambda: _resolution("0.25", "cells"),
    "resolution.coverage_025": lambda: _resolution("0.25", "annual coverage"),
    "resolution.median_n_025": lambda: _resolution("0.25", "soundings per covered cell, median"),
    "resolution.se_025": lambda: _resolution("0.25", "per-cell standard error, median"),
    "resolution.se_share_025": lambda: _resolution("0.25", "per-cell standard error as a share of the field spread"),
    "resolution.effective_n_025": lambda: _resolution("0.25", "effective sample size, full lattice"),
    "resolution.cells_02": lambda: _resolution("0.2", "cells"),
    "resolution.coverage_02": lambda: _resolution("0.2", "annual coverage"),
    "resolution.median_n_02": lambda: _resolution("0.2", "soundings per covered cell, median"),
    "resolution.se_02": lambda: _resolution("0.2", "per-cell standard error, median"),
    "resolution.se_share_02": lambda: _resolution("0.2", "per-cell standard error as a share of the field spread"),
    "resolution.effective_n_02": lambda: _resolution("0.2", "effective sample size, full lattice"),
    "resolution.cells_015": lambda: _resolution("0.15", "cells"),
    "resolution.coverage_015": lambda: _resolution("0.15", "annual coverage"),
    "resolution.median_n_015": lambda: _resolution("0.15", "soundings per covered cell, median"),
    "resolution.se_015": lambda: _resolution("0.15", "per-cell standard error, median"),
    "resolution.se_share_015": lambda: _resolution("0.15", "per-cell standard error as a share of the field spread"),
    "resolution.effective_n_015": lambda: _resolution("0.15", "effective sample size, full lattice"),
    "resolution.cells_0125": lambda: _resolution("0.125", "cells"),
    "resolution.coverage_0125": lambda: _resolution("0.125", "annual coverage"),
    "resolution.median_n_0125": lambda: _resolution("0.125", "soundings per covered cell, median"),
    "resolution.se_0125": lambda: _resolution("0.125", "per-cell standard error, median"),
    "resolution.se_share_0125": lambda: _resolution("0.125", "per-cell standard error as a share of the field spread"),
    "resolution.effective_n_0125": lambda: _resolution("0.125", "effective sample size, full lattice"),
    "resolution.cells_01": lambda: _resolution("0.1", "cells"),
    "resolution.coverage_01": lambda: _resolution("0.1", "annual coverage"),
    "resolution.median_n_01": lambda: _resolution("0.1", "soundings per covered cell, median"),
    "resolution.se_01": lambda: _resolution("0.1", "per-cell standard error, median"),
    "resolution.se_share_01": lambda: _resolution("0.1", "per-cell standard error as a share of the field spread"),
    "resolution.effective_n_01": lambda: _resolution("0.1", "effective sample size, full lattice"),
    "resolution.below5_025": lambda: _resolution("0.25", "covered cells below 5 soundings"),
    "resolution.below10_025": lambda: _resolution("0.25", "covered cells below 10 soundings"),
    "resolution.below30_025": lambda: _resolution("0.25", "covered cells below 30 soundings"),
    "resolution.over_spread_025": lambda: _resolution("0.25", "cells whose standard error exceeds the field spread"),
    "resolution.uncovered_025": lambda: _resolution("0.25", "uncovered cells"),
    "resolution.components_025": lambda: _resolution("0.25", "uncovered connected components"),
    "resolution.largest_share_025": lambda: _resolution("0.25", "share of gaps in the largest component"),
    "resolution.singletons_025": lambda: _resolution("0.25", "single-cell gaps"),
    "resolution.below5_01": lambda: _resolution("0.1", "covered cells below 5 soundings"),
    "resolution.below10_01": lambda: _resolution("0.1", "covered cells below 10 soundings"),
    "resolution.below30_01": lambda: _resolution("0.1", "covered cells below 30 soundings"),
    "resolution.over_spread_01": lambda: _resolution("0.1", "cells whose standard error exceeds the field spread"),
    "resolution.uncovered_01": lambda: _resolution("0.1", "uncovered cells"),
    "resolution.components_01": lambda: _resolution("0.1", "uncovered connected components"),
    "resolution.largest_share_01": lambda: _resolution("0.1", "share of gaps in the largest component"),
    "resolution.singletons_01": lambda: _resolution("0.1", "single-cell gaps"),
    "resolution.effective_n_empirical": lambda: _resolution(
        "", "effective sample size at 0.25 degree, empirical"),
    # The Tier 3 retention pass: what the quality threshold removed over this
    # domain, and how the composite responds to the omitted preprocessing.
    # Equivalence bounds and the specification curve, Tier 5.
    "equiv.rows": lambda: len(_equivalence()),
    "equiv.bound_comparative": lambda: float(
        _equivalence()[0]["bound_comparative"]),
    "equiv.within_comparative": lambda: sum(
        1 for r in _equivalence()
        if r["verdict_comparative"].startswith("within")),
    "equiv.outside_comparative": lambda: sum(
        1 for r in _equivalence()
        if r["verdict_comparative"].startswith("outside")),
    "equiv.spanning_comparative": lambda: sum(
        1 for r in _equivalence()
        if r["verdict_comparative"].startswith("spans")),
    "equiv.rice_within": lambda: _equiv_count("rice_fraction_single", "within")
        + _equiv_count("rice_fraction_combined", "within"),
    "equiv.rice_rows": lambda: sum(
        1 for r in _equivalence()
        if r["predictor"].startswith("rice_fraction")),
    "equiv.impervious_within": lambda: _equiv_count(
        "impervious_fraction", "within"),
    "equiv.impervious_spans": lambda: _equiv_count(
        "impervious_fraction", "spans"),
    "equiv.impervious_rows": lambda: sum(
        1 for r in _equivalence() if r["predictor"] == "impervious_fraction"),
    "curve.specifications": lambda: len(_curve()),
    "curve.positive": lambda: sum(
        1 for r in _curve() if r["nominally_positive"] == "yes"),
    "curve.beats_benchmark": lambda: sum(
        1 for r in _curve() if r["beats_benchmark"] == "yes"),
    "curve.positive_and_beats": lambda: sum(
        1 for r in _curve() if r["nominally_positive"] == "yes"
        and r["beats_benchmark"] == "yes"),
    "curve.best_r2": lambda: max(
        float(r["held_out_r2"]) for r in _curve()),
    "curve.worst_r2": lambda: min(
        float(r["held_out_r2"]) for r in _curve()),
    "curve.median_r2": lambda: float(np.median(
        [float(r["held_out_r2"]) for r in _curve()])),
    # The reference register read as a reference list.
    # The claim audit.
    "claims.total": lambda: _claim_count(),
    "claims.measured": lambda: _claim_count("measured"),
    "claims.cited": lambda: _claim_count("cited"),
    "claims.unresolved": lambda: _claim_count("unresolved"),
    "claims.self_evident": lambda: _claim_count("self_evident"),
    "claims.neither": lambda: _claim_count("neither"),
    "claims.neither_captions": lambda: len(
        [r for r in _claims()
         if r["category"] == "neither" and "README_fragments" in r["source"]]),
    "claims.neither_introduction": lambda: len(
        [r for r in _claims()
         if r["category"] == "neither" and "introduction" in r["source"]]),
    # The domain's sectoral composition on the analysis lattice.
    "change.gaia_median": lambda: _change(
        "gaia impervious change 2010-2018, median"),
    "change.gaia_max": lambda: _change(
        "gaia impervious change 2010-2018, maximum"),
    "change.gisa_max": lambda: _change(
        "gisa impervious change 2010-2018, maximum"),
    "change.gaia_above_20": lambda: _change("gaia cells with change above 0.2"),
    "change.product_ratio": lambda: _change(
        "product disagreement on change, ratio of means"),
    "change.effective_n": lambda: _change(
        "gaia effective sample size, change against methane"),
    "change.rate_urban": lambda: _change(
        "urban-sector rate, through-origin slope"),
    "change.rice_correlation": lambda: _change(
        "rice emission against rice area, correlation"),
    "change.beta": lambda: _change("beta, expected slope"),
    "change.enhancement_median": lambda: _change(
        "gaia implied enhancement, median"),
    "change.enhancement_max": lambda: _change(
        "gaia implied enhancement, maximum"),
    "change.se_median": lambda: _change("per-cell standard error, median"),
    "change.t_gaia": lambda: _change("gaia t statistic at effective n"),
    "change.needed": lambda: _change(
        "gaia effective cells needed for 80 percent power"),
    "change.shortfall": lambda: _change("gaia shortfall factor"),
    "change.mde": lambda: _change("minimum detectable slope"),
    "change.effect_shortfall": lambda: _change("effect-size shortfall"),
    "change.detectable_emission": lambda: _change(
        "emission change a detectable cell would need"),
    "change.coal_total": lambda: _change("coal emission, domain total"),
    "change.coal_cells": lambda: _change("coal cells"),
    "change.coal_enhancement": lambda: _change(
        "coal implied enhancement per coal cell"),
    "change.coal_multiple": lambda: _change(
        "coal enhancement as a multiple of the per-cell error"),
    "change.rice_enhancement": lambda: _change(
        "rice implied enhancement per rice cell"),
    "change.coal_vs_impervious": lambda: _change(
        "coal emission against impervious fraction, correlation"),
    "change.r_max": lambda: _change("maximum correlation the physics permits"),
    "change.bound_ratio": lambda: _change(
        "comparative equivalence bound, ratio to the physical ceiling"),
    "change.xsec_contrast": lambda: _change(
        "cross-sectional implied contrast, p5 to p95"),
    "change.xsec_share": lambda: _change(
        "cross-sectional contrast as a share of the field sd"),
    "change.xsec_r2": lambda: _change("cross-sectional implied R squared"),
    "tccon.retrievals": lambda: _tccon("retrievals in 2018"),
    "tccon.days": lambda: _tccon("days with a retrieval in 2018"),
    "tccon.coincident_days": lambda: _tccon("coincident days"),
    "tccon.granules": lambda: _tccon("granules covering the station cell"),
    "tccon.granule_days": lambda: _tccon(
        "days a granule covered the station cell"),
    "tccon.cell_soundings": lambda: _tccon("soundings in the station cell"),
    "sector.cells_any": lambda: _sector(
        "lattice cells with any inventory emission"),
    "sector.coal_share": lambda: _sector("coal, share of the domain"),
    "sector.coal_cells": lambda: _sector("coal, cells present"),
    "sector.rice_share": lambda: _sector("rice, share of the domain"),
    "sector.rice_cells": lambda: _sector("rice, cells present"),
    "sector.landfill_share": lambda: _sector("landfills, share of the domain"),
    "sector.wastewater_share": lambda: _sector(
        "wastewater, share of the domain"),
    "sector.rice_national": lambda: _sector(
        "rice, share of its national total"),
    "sector.two_at_5pct": lambda: _sector(
        "cells carrying at least 2 sectors above 5 percent"),
    "sector.two_at_25pct": lambda: _sector(
        "cells carrying at least 2 sectors above 25 percent"),
    "sector.three_at_5pct": lambda: _sector(
        "cells carrying at least 3 sectors above 5 percent"),
    "sector.landfill_wastewater_pair": lambda: _sector(
        "cells carrying both landfills and wastewater above 5 percent"),
    "sector.rice_coal_pair": lambda: _sector(
        "cells carrying both rice and coal above 5 percent"),
    "register.entries": lambda: _register_entries(),
    "register.draft_cited": lambda: _reference_use("draft_verified"),
    "register.named_no_year": lambda: _reference_use("draft_named_no_year"),
    "register.datasets": lambda: sum(
        1 for r in _cache.setdefault("refuse", _read_csv(
            PROCESSED / "reference_use_2026.csv"))
        if r["kind"] in {"dataset record", "dataset paper",
                         "the deposit, fetched", "the deposit, not fetched"}),
    "quality.granules": lambda: len(_quality_granules()),
    "quality.read": lambda: _qsum("soundings_read"),
    "quality.in_box_total": lambda: _qsum("in_box_total"),
    "quality.in_box_retrieved": lambda: _qsum("in_box_retrieved"),
    "quality.in_box_passed": lambda: _qsum("in_box_passed"),
    "quality.no_retrieval_pct": lambda: 100.0 * (
        _qsum("in_box_total") - _qsum("in_box_retrieved")) / _qsum("in_box_total"),
    "quality.threshold_rejected_pct": lambda: 100.0 * (
        _qsum("in_box_retrieved") - _qsum("in_box_passed"))
        / _qsum("in_box_retrieved"),
    "quality.within_sd_median": lambda: float(np.median(
        [float(r["within_cell_sd_ppb"]) for r in _quality_cells()
         if r["within_cell_sd_ppb"]])),
    "quality.cells_with_spread": lambda: sum(
        1 for r in _quality_cells() if r["within_cell_sd_ppb"]),
    "quality.months_median": lambda: float(np.median(
        [int(r["months_observed"]) for r in _quality_cells()
         if int(r["sounding_count"])])),
    "sens.precision_kept": lambda: _sensitivity(
        "precision under 10 ppb", "OLS impervious_fraction",
        "spatial blocks", "unweighted", "soundings"),
    "sens.albedo_kept": lambda: _sensitivity(
        "SWIR albedo at least 0.05", "OLS impervious_fraction",
        "spatial blocks", "unweighted", "soundings"),
    "sens.committed_soundings": lambda: _sensitivity(
        "committed (no filter)", "OLS impervious_fraction",
        "spatial blocks", "unweighted", "soundings"),
    "sens.albedo_cells": lambda: _sensitivity(
        "SWIR albedo at least 0.05", "OLS impervious_fraction",
        "spatial blocks", "unweighted", "n"),
    "sens.impervious_destriped": lambda: _sensitivity(
        "first-order destriping", "OLS impervious_fraction",
        "spatial blocks", "unweighted"),
    "sens.null_destriped": lambda: _sensitivity(
        "first-order destriping", "spatial null (queen neighbour mean)",
        "spatial blocks", "unweighted"),
    "sens.impervious_repweight": lambda: _sensitivity(
        "representativeness weighting", "OLS impervious_fraction",
        "spatial blocks", "by sounding count"),
    "sens.null_repweight": lambda: _sensitivity(
        "representativeness weighting", "spatial null (queen neighbour mean)",
        "spatial blocks", "by sounding count"),
    "sens.null_committed_weighted": lambda: _sensitivity(
        "committed (no filter)", "spatial null (queen neighbour mean)",
        "spatial blocks", "by sounding count"),
    "sens.albedo_removed": lambda: int(
        _sensitivity("committed (no filter)", "OLS impervious_fraction",
                     "spatial blocks", "unweighted", "soundings")
        - _sensitivity("SWIR albedo at least 0.05", "OLS impervious_fraction",
                       "spatial blocks", "unweighted", "soundings")),
    "sens.albedo_cells_lost": lambda: int(
        _sensitivity("committed (no filter)", "OLS impervious_fraction",
                     "spatial blocks", "unweighted", "n")
        - _sensitivity("SWIR albedo at least 0.05", "OLS impervious_fraction",
                       "spatial blocks", "unweighted", "n")),
    "sens.impervious_committed_weighted": lambda: _sensitivity(
        "committed (no filter)", "OLS impervious_fraction",
        "spatial blocks", "by sounding count"),
    "sens.stripe_sd": lambda: _stripe()[0],
    "sens.stripe_low": lambda: _stripe()[1],
    "sens.stripe_high": lambda: _stripe()[2],
    "sens.weight_correlation": lambda: _weighting()[0],
    "sens.spatial_share_pct": lambda: _weighting()[1],
    "sens.impervious_albedo": lambda: _sensitivity(
        "SWIR albedo at least 0.05", "OLS impervious_fraction",
        "spatial blocks", "unweighted"),
    "sens.null_albedo": lambda: _sensitivity(
        "SWIR albedo at least 0.05", "spatial null (queen neighbour mean)",
        "spatial blocks", "unweighted"),
    "cycle.peak_day": lambda: _cycle("peak day of year"),
    "cycle.peak_low": lambda: _cycle("peak day 2.5th percentile"),
    "cycle.peak_high": lambda: _cycle("peak day 97.5th percentile"),
    "cycle.peak_sd": lambda: _cycle("peak day standard deviation"),
    "cycle.trough_day": lambda: _cycle("trough day of year"),
    "cycle.range_ppb": lambda: _cycle("peak to trough range"),
    "cycle.amp1": lambda: _cycle("harmonic 1 amplitude"),
    "cycle.amp2": lambda: _cycle("harmonic 2 amplitude"),
    "cycle.variance_explained": lambda: _cycle("variance explained within cells"),
    "cycle.residual_sd": lambda: _cycle("residual standard deviation"),
    "cycle.soundings": lambda: _cycle("soundings in the fit"),
    "cycle.cells": lambda: _cycle("cells in the fit"),
    "cycle.poorly_identified": lambda: _cycle("poorly identified cells"),
    "atten.var_x": lambda: _atten("Var(X), the GAIA cell fraction in use"),
    "atten.var_d": lambda: _atten("Var(D), GAIA minus GISA on the same cells"),
    "atten.corr": lambda: _atten("correlation of the two cell fractions"),
    "atten.var_share": lambda: _atten("Var(D) as a share of Var(X)"),
    # The prose speaks in percent where the artefact stores a share.
    "atten.var_share_pct": lambda: 100.0 * _atten("Var(D) as a share of Var(X)"),
    "atten.lambda_min": lambda: _atten("reliability ratio lower bound"),
    "atten.factor_max": lambda: _atten("maximum de-attenuation factor"),
    "atten.lambda_equal": lambda: _atten("reliability ratio, equal independent errors"),
    "atten.r2_bound_bu":
        lambda: _atten("held-out R2 upper bound, operational, spatial blocks, unweighted"),
    "atten.r2_bound_bw":
        lambda: _atten("held-out R2 upper bound, operational, spatial blocks, by sounding count"),
    "atten.r2_bound_blended_bu":
        lambda: _atten("held-out R2 upper bound, blended, spatial blocks, unweighted"),
    "atten.coef_bound":
        lambda: _atten("coefficient upper bound, operational, unweighted"),
    "atten.coef_bound_blended":
        lambda: _atten("coefficient upper bound, blended, unweighted"),
    # What the bound would have to be beaten by. Requirements, not measurements.
    "atten.need_share_bu": lambda: _atten(
        "error share needed to reach the null, operational, spatial blocks, unweighted"),
    "atten.need_share_bu_pct": lambda: 100.0 * _atten(
        "error share needed to reach the null, operational, spatial blocks, unweighted"),
    "atten.need_multiple_bu": lambda: _atten(
        "multiple of Var(D) needed to reach the null, operational, spatial blocks, unweighted"),
    "atten.need_multiple_bw": lambda: _atten(
        "multiple of Var(D) needed to reach the null, operational, spatial blocks, by sounding count"),
    "atten.need_multiple_blended_bu": lambda: _atten(
        "multiple of Var(D) needed to reach the null, blended, spatial blocks, unweighted"),
    # Added for queue item 10, the GAIA-GISA disagreement decomposition.
    "disagree.alloc_share_2018_cell":
        lambda: _disagree("2018", "0.25 degree cell", "allocation_share"),
    "disagree.alloc_share_2018_pixel":
        lambda: _disagree("2018", "868 m pixel", "allocation_share"),
    "disagree.alloc_2018_pixel_km2":
        lambda: _disagree("2018", "868 m pixel", "allocation_km2"),
    "disagree.quantity_2018_pixel_km2":
        lambda: _disagree("2018", "868 m pixel", "quantity_km2"),
    "disagree.quantity_2000_pixel_km2":
        lambda: _disagree("2000", "868 m pixel", "quantity_km2"),
    "disagree.alloc_2010_pixel_km2":
        lambda: _disagree("2010", "868 m pixel", "allocation_km2"),
    "disagree.alloc_share_2010_pixel":
        lambda: _disagree("2010", "868 m pixel", "allocation_share"),
    "range.block_ns_km": lambda: _range()["block_ns_km"],
    "range.block_ew_km": lambda: _range()["block_ew_km"],
    "range.operational_impervious_km":
        lambda: _range()["operational_impervious_km"],
    "range.blended_impervious_km": lambda: _range()["blended_impervious_km"],
    "range.operational_full_km": lambda: _range()["operational_full_km"],
    "range.operational_field_km": lambda: _range()["operational_field_km"],
    "range.blended_field_km": lambda: _range()["blended_field_km"],
    "range.too_small": lambda: _range()["too_small"],
    "range.models": lambda: _range()["models"],
    "loo.null_0km": lambda: _loo("spatial null", "0"),
    "loo.null_50km": lambda: _loo("spatial null", "50"),
    "loo.impervious_0km": lambda: _loo("OLS impervious", "0"),
    "loo.impervious_100km": lambda: _loo("OLS impervious", "100"),
    "loo.impervious_300km": lambda: _loo("OLS impervious", "300"),
    # Added for figures/buffered_decay. The held-out column rather than the
    # difference, for the three curves panel (a) draws: the null collapsing
    # and the constant's own baseline sliding away beneath it.
    "loo.null_0km_raw": lambda: _loo("spatial null", "0", "held_out_r2"),
    "loo.null_25km_raw": lambda: _loo("spatial null", "25", "held_out_r2"),
    "loo.null_50km_raw": lambda: _loo("spatial null", "50", "held_out_r2"),
    "loo.constant_0km_raw": lambda: _loo("constant", "0", "held_out_r2"),
    "loo.constant_500km_raw": lambda: _loo("constant", "500", "held_out_r2"),
    # Two keys per radius on purpose. The above-constant column is exactly
    # zero here -- beyond one cell the null *is* the constant -- so the
    # bracketing comparison against leave-one-province-out can only be made on
    # the raw column, which is the scale panel (a) draws.
    "loo.null_150km": lambda: _loo("spatial null", "150"),
    "loo.null_200km": lambda: _loo("spatial null", "200"),
    "loo.null_150km_raw": lambda: _loo("spatial null", "150", "held_out_r2"),
    "loo.null_200km_raw": lambda: _loo("spatial null", "200", "held_out_r2"),
    "loo.impervious_150km": lambda: _loo("OLS impervious", "150"),
    "loo.impervious_200km": lambda: _loo("OLS impervious", "200"),
    "dofs.days_median":
        lambda: _dofs("observation days per covered cell, median"),
    "dofs.retrievals_median":
        lambda: _dofs("retrievals per superobservation, median"),
    "dofs.at_5tg": lambda: _dofs("expected DOFS at 5 Tg/y domain prior"),
    "dofs.at_12tg": lambda: _dofs("expected DOFS at 12 Tg/y domain prior"),
    "dofs.at_3tg": lambda: _dofs("expected DOFS at 3 Tg/y domain prior"),
    # Added for figures/capability. Bisected on the sensitivity expression, not
    # interpolated between sweep points and not the next swept point above the
    # threshold, which is what an earlier record reported.
    "dofs.cross_half":
        lambda: _dofs("domain prior at which DOFS reaches 0.5"),
    "dofs.cross_one": lambda: _dofs("domain prior at which DOFS reaches 1"),
    "dofs.cross_two": lambda: _dofs("domain prior at which DOFS reaches 2"),
    "dofs.cell_median_5tg":
        lambda: _dofs("per-cell sensitivity median at 5 Tg/y"),
    "dofs.cell_max_5tg":
        lambda: _dofs("per-cell sensitivity maximum at 5 Tg/y"),
    "dofs.cell_median_12tg":
        lambda: _dofs("per-cell sensitivity median at 12 Tg/y"),
    "dofs.cell_p90_12tg":
        lambda: _dofs("per-cell sensitivity 90th percentile at 12 Tg/y"),
    "dofs.cell_max_12tg":
        lambda: _dofs("per-cell sensitivity maximum at 12 Tg/y"),
    # The same two prior-free thresholds the Tg resolvers above carry, in the
    # unit the figure draws them in: a cell-scale emission in Tg is three
    # leading zeros, so the caption and the panel both speak in Gg.
    "dofs.prior_free_median_gg":
        lambda: 1000.0 * _dofs("emission for a = 0.5, median cell"),
    "dofs.prior_free_best_gg":
        lambda: 1000.0 * _dofs("emission for a = 0.5, best-observed cell"),
    "dofs.cells_above_half": _dofs_cells_above_half,
    "grid.rows": lambda: len(_grid()),
    "grid.rice_rows": lambda: int(np.isfinite(_column("rice_fraction_single")).sum()),
    "grid.rows_without_rice":
        lambda: len(_grid()) - int(np.isfinite(_column("rice_fraction_single")).sum()),
    "grid.impervious_median": lambda: float(np.nanmedian(_column("impervious_fraction"))),
    "grid.impervious_zeros": lambda: int((_column("impervious_fraction") == 0).sum()),
    "grid.rice_single_median": lambda: float(np.nanmedian(_column("rice_fraction_single"))),
    "grid.rice_combined_median":
        lambda: float(np.nanmedian(_column("rice_fraction_combined"))),
    "grid.rice_coverage_median": lambda: float(np.nanmedian(_column("rice_coverage"))),
    # The threshold the paddy-rice-and-XCH4 exchange settled on, applied to this
    # lattice. The condition is stated at 0.5 degrees and is untested at 0.25.
    "grid.rice_above_ten_percent":
        lambda: int((_column("rice_fraction_single")[
            np.isfinite(_column("rice_fraction_single"))] > 0.10).sum()),
    "grid.rice_above_ten_of_rice_percent":
        lambda: 100.0 * (_column("rice_fraction_single")[
            np.isfinite(_column("rice_fraction_single"))] > 0.10).sum()
        / int(np.isfinite(_column("rice_fraction_single")).sum()),
    "grid.rice_above_ten_of_lattice_percent":
        lambda: 100.0 * (_column("rice_fraction_single")[
            np.isfinite(_column("rice_fraction_single"))] > 0.10).sum()
        / len(_grid()),
    "grid.rice_zero_rows":
        lambda: int((_column("rice_fraction_single")[
            np.isfinite(_column("rice_fraction_single"))] == 0).sum()),
    "grid.rice_coverage_below_99":
        lambda: int((_column("rice_coverage") < 0.99).sum()),
    "grid.straddling_cells":
        lambda: int(((_shares() > 1e-9).sum(axis=1) > 1).sum()),
    "grid.cells_outside_in_file":
        lambda: int((_shares().sum(axis=1) <= 1e-9).sum()),

    "cov.rows": lambda: len(_covariates()),
    "cov.albedo_negative":
        lambda: int((_cov_column("surface_albedo_SWIR_mean") < 0).sum()),
    "cov.eastward_wind_median": lambda: float(np.median(_cov_column("eastward_wind_mean"))),
    "cov.northward_wind_median": lambda: float(np.median(_cov_column("northward_wind_mean"))),
    "cov.northward_wind_max": lambda: float(_cov_column("northward_wind_mean").max()),
    "cov.albedo_swir_median": lambda: float(np.median(_cov_column("surface_albedo_SWIR_mean"))),
    "cov.albedo_nir_median": lambda: float(np.median(_cov_column("surface_albedo_NIR_mean"))),
    "cov.solar_zenith_median": lambda: float(np.median(_cov_column("solar_zenith_angle_mean"))),
    "cov.altitude_median": lambda: float(np.median(_cov_column("surface_altitude_mean"))),
    "cov.pressure_median": lambda: float(np.median(_cov_column("surface_pressure_mean"))),
}


def find_claims(text: str) -> list[tuple[str, str, int]]:
    """Every (quantity, literal, line number) marked in ``text``."""
    found = []
    for match in CLAIM.finditer(text):
        line = text.count("\n", 0, match.start()) + 1
        found.append((match.group(2), match.group(1), line))
    return found


def agrees(literal: str, value: float) -> bool:
    """Whether the written number matches the computed one at its own precision.

    The prose decides the precision. "90.52" is checked to two decimals and
    "926" to none, so rounding in the sentence is not treated as drift while a
    real change in the underlying value is.
    """
    plain = literal.replace(",", "")
    places = len(plain.split(".")[1]) if "." in plain else 0
    return round(float(plain), places) == round(float(value), places)


def check(paths=SCANNED) -> list[dict]:
    """Every marked claim, with what the prose says and what the data says."""
    results = []
    for name in paths:
        path = REPO / name
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for quantity, literal, line in find_claims(text):
            if quantity not in QUANTITIES:
                results.append(dict(file=name, line=line, quantity=quantity,
                                    written=literal, actual=None, ok=False,
                                    reason="unknown quantity"))
                continue
            value = QUANTITIES[quantity]()
            results.append(dict(file=name, line=line, quantity=quantity,
                                written=literal, actual=value,
                                ok=agrees(literal, value), reason=""))
    return results


def unmarked(paths=SCANNED) -> dict[str, int]:
    """Numbers with no marker, per file. The unchecked surface."""
    out = {}
    for name in paths:
        path = REPO / name
        if not path.exists():
            continue
        text = CLAIM.sub("", path.read_text(encoding="utf-8"))
        out[name] = len(re.findall(r"\d[\d,]*(?:\.\d+)?", text))
    return out


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--stale", action="store_true")
    parser.add_argument("--coverage", action="store_true")
    args = parser.parse_args(argv)

    results = check()
    if args.coverage:
        marked = len(results)
        print(f"  {marked} marked claims across {len(SCANNED)} files")
        print(f"  {'file':<40}{'marked':>8}{'unmarked numbers':>18}")
        counts = unmarked()
        for name in SCANNED:
            n = sum(1 for r in results if r["file"] == name)
            print(f"  {name:<40}{n:>8}{counts.get(name, 0):>18}")
        return 0

    shown = [r for r in results if not r["ok"]] if args.stale else results
    for r in shown:
        mark = "ok " if r["ok"] else "STALE"
        actual = "?" if r["actual"] is None else f"{r['actual']:g}"
        print(f"  {mark} {r['file']}:{r['line']:<5} {r['quantity']:<30} "
              f"prose {r['written']:>12}   data {actual:>12} {r['reason']}")
    bad = sum(1 for r in results if not r["ok"])
    print(f"\n  {len(results)} claims checked, {bad} stale")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
