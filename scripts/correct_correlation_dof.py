#!/usr/bin/env python3
"""Recompute every reported correlation's significance under spatial dependence.

    python scripts/correct_correlation_dof.py
    python scripts/correct_correlation_dof.py --write

`data/processed/albedo_confounder_2018.csv` reports twenty-six correlations with
`n` set to the number of cells, 926 or 531. Both sides of every one of them are
strongly autocorrelated fields on a 0.25-degree lattice, so those `n` values
overstate the independent information by a large factor and the p-values beside
them are anti-conservative. `notes/grounding-methods.md` records the problem and
names the fix.

This script does not touch that file. It reads it, reconstructs each pair of
series, estimates the effective sample size with the modified t-test of
Clifford, Richardson and Hémon (1989) and Dutilleul, Clifford, Richardson and
Hémon (1993), and writes the corrected test beside the nominal one in
`data/processed/correlation_dof_2018.csv`. Keeping them separate means the
original artefact still reproduces byte for byte and a reader can see exactly
what the correction changed.

**It also extends the set.** The blended TROPOMI+GOSAT field's correlations are
reported in `data/processed/README.md` prose and in no artefact, so the same
relationships are computed on that field here and corrected the same way. That
closes a gap rather than adding a result: those numbers were only ever in a
paragraph.

**Three things are exact and two are approximations, and the output says
which.** The correction is exact for an unweighted Pearson correlation, which is
what Dutilleul's derivation covers. For a Spearman correlation the effective
sample size is estimated from the *ranks*, since Spearman is Pearson on ranks,
which is the right pair of series but not a case the derivation treats. For a
weighted correlation the spatial dependence is estimated from the same fields
but the weighted coefficient's own sampling distribution differs from the
unweighted one, so its corrected p-value is approximate. Partial correlations
have their effective sample size estimated from the residual series rather than
the raw ones, which is exact in the same sense as the zero-order case because a
partial correlation is a correlation between residuals.

**A calibration note, measured rather than assumed.** On two independent
white-noise fields at 400 locations the estimator returns an effective sample
size of about 0.87 of nominal rather than 1.0, because the binned correlogram
carries sampling noise that inflates the trace. The correction is therefore
mildly conservative even where there is no dependence to correct, and a
shrinkage of 0.87 should be read as "no detectable dependence" rather than as a
13 percent loss.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from scipy import stats

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model import spatial_dof as sd  # noqa: E402

PROCESSED = REPO / "data" / "processed"
CONFOUNDER = PROCESSED / "albedo_confounder_2018.csv"
GRID = PROCESSED / "analysis_grid_2018.csv"
COVARIATES = PROCESSED / "methane_covariates_2018.csv"
BLENDED = PROCESSED / "methane_blended_2018.csv"
OUT = PROCESSED / "correlation_dof_2018.csv"

#: The methane column each field name maps to in the analysis grid.
FIELDS = {"operational": "ch4_bias_corrected_ppb", "raw": "ch4_raw_ppb"}

#: Distance bins for the correlogram. Thirty over a domain about 1,150 km
#: across gives bins of roughly 38 km, which is wider than a cell and narrower
#: than the field's 102 km half-sill range, so the decay is resolved without
#: bins so thin that each carries only a handful of pairs.
BINS = 30


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def as_float(value: str) -> float:
    return float(value) if value not in ("", None) else float("nan")


def cell_key(row: dict) -> tuple[int, int]:
    """A join key that survives the three files' different decimal formats.

    `analysis_grid_2018.csv` writes centres as `35.075` and
    `methane_covariates_2018.csv` as `35.0750`, so joining on the strings
    silently matches nothing. Rounding to thousandths of a degree is exact for a
    0.25-degree lattice and immune to the formatting.
    """
    return (round(float(row["centre_lat"]) * 1000),
            round(float(row["centre_lon"]) * 1000))


def load_series() -> dict[str, np.ndarray]:
    """Every column the reported correlations use, on the 926-cell grid."""
    grid = read_csv(GRID)
    key = {cell_key(r): r for r in grid}

    cov = {cell_key(row): row for row in read_csv(COVARIATES)}
    blend = {cell_key(row): row for row in read_csv(BLENDED)}

    out: dict[str, list[float]] = {name: [] for name in (
        "centre_lat", "centre_lon", "sounding_count", "methane",
        "methane_raw", "methane_blended",
        "impervious_fraction", "rice_fraction_single",
        "rice_fraction_combined", "surface_albedo_SWIR", "surface_albedo_NIR",
        "solar_zenith_angle")}

    for k, row in key.items():
        c, b = cov.get(k), blend.get(k)
        out["centre_lat"].append(as_float(row["centre_lat"]))
        out["centre_lon"].append(as_float(row["centre_lon"]))
        out["sounding_count"].append(as_float(row["sounding_count"]))
        out["methane"].append(as_float(row[FIELDS["operational"]]))
        out["methane_raw"].append(as_float(row[FIELDS["raw"]]))
        out["methane_blended"].append(
            as_float(b["ch4_blended_ppb"]) if b else float("nan"))
        for name in ("impervious_fraction", "rice_fraction_single",
                     "rice_fraction_combined"):
            out[name].append(as_float(row[name]))
        # The covariate table names its columns with a `_mean` suffix and
        # carries a count beside each; the confounder script reads the means.
        for name in ("surface_albedo_SWIR", "surface_albedo_NIR",
                     "solar_zenith_angle"):
            out[name].append(as_float(c[f"{name}_mean"]) if c else float("nan"))

    return {name: np.asarray(values, dtype="float64")
            for name, values in out.items()}


def weighted_pearson(x: np.ndarray, y: np.ndarray, w: np.ndarray) -> float:
    """Weighted Pearson correlation, matching the confounder script's
    definition so that reported coefficients reproduce."""
    w = w / w.sum()
    mx, my = float(np.sum(w * x)), float(np.sum(w * y))
    cx, cy = x - mx, y - my
    cov = float(np.sum(w * cx * cy))
    return cov / float(np.sqrt(np.sum(w * cx * cx) * np.sum(w * cx * 0 + w * cy * cy)))


def partial(x: np.ndarray, y: np.ndarray, controls: list[np.ndarray],
            w: np.ndarray | None) -> tuple[float, np.ndarray, np.ndarray]:
    """Partial correlation and the two residual series it is computed from."""
    stack = np.column_stack([np.ones(len(x))] + list(controls))
    if w is None:
        def resid(v):
            beta, *_ = np.linalg.lstsq(stack, v, rcond=None)
            return v - stack @ beta
        rx, ry = resid(x), resid(y)
        return float(stats.pearsonr(rx, ry).statistic), rx, ry
    root = np.sqrt(w / w.sum())
    def wresid(v):
        beta, *_ = np.linalg.lstsq(stack * root[:, None], v * root, rcond=None)
        return v - stack @ beta
    rx, ry = wresid(x), wresid(y)
    return weighted_pearson(rx, ry, w), rx, ry


def build_rows(series: dict[str, np.ndarray]) -> list[dict]:
    lat, lon = series["centre_lat"], series["centre_lon"]
    weight = series["sounding_count"]
    reported = read_csv(CONFOUNDER)
    rows: list[dict] = []

    def emit(field: str, weighting: str, relationship: str, controlling: str,
             left: str, right: str, subset: np.ndarray, method: str,
             r_reported: float | None, p_reported: float | None) -> None:
        x, y = series[left][subset], series[right][subset]
        w = weight[subset] if weighting != "unweighted" else None
        controls = [series[c.strip()][subset]
                    for c in controlling.split(",") if c.strip()]

        # Spearman is Pearson on ranks, so rank-transform first and then run
        # exactly the same weighting and partialling path. Doing it the other
        # way round -- correlating raw values and then ranking for the degrees
        # of freedom -- silently reports an unweighted coefficient on a
        # weighted row, which an earlier version of this script did.
        if method == "spearman":
            x, y = stats.rankdata(x), stats.rankdata(y)
            controls = [stats.rankdata(c) for c in controls]

        if controls:
            r, sx, sy = partial(x, y, controls, w)
        elif w is None:
            r, sx, sy = float(stats.pearsonr(x, y).statistic), x, y
        else:
            r, sx, sy = weighted_pearson(x, y, w), x, y

        # **Where a coefficient was already reported, that is the one carried
        # forward and only the degrees of freedom are corrected.** This script
        # exists to fix the significance of published numbers, not to replace
        # them with its own. It matters for partial Spearman correlations,
        # where partialling ranks and partialling before ranking give different
        # coefficients and the confounder script's choice is the one on record.
        # The Pearson coefficients recomputed here do reproduce the reported
        # ones, which `tests/test_correlation_dof.py` asserts.
        recomputed = r
        if r_reported is not None and np.isfinite(r_reported):
            r = float(r_reported)

        test = sd.modified_t_test(sx, sy, lat[subset], lon[subset],
                                  bins=BINS, r=r)
        exactness = "exact" if (weighting == "unweighted"
                                and method == "pearson") else "approximate"
        rows.append({
            "field": field, "weighting": weighting,
            "relationship": relationship, "controlling_for": controlling,
            "method": method, "n": test.n,
            "effective_n": f"{test.effective_n:.1f}",
            "shrinkage": f"{test.shrinkage:.4f}",
            "coefficient": f"{r:+.4f}",
            "p_nominal": f"{test.p_nominal:.3e}",
            "p_corrected": f"{test.p_corrected:.3e}",
            "verdict": ("was significant, now is not" if test.changed_verdict
                        else "significant" if test.still_significant
                        else "not significant either way"),
            "correction": exactness,
            "coefficient_reported": ("" if r_reported is None
                                     else f"{r_reported:+.4f}"),
            "p_reported": "" if p_reported is None else f"{p_reported:.3e}",
            "coefficient_recomputed": f"{recomputed:+.4f}",
        })

    present = ~np.isnan(series["rice_fraction_single"])
    everything = np.ones(len(lat), dtype=bool)

    for row in reported:
        subset = present if int(row["n"]) == int(present.sum()) else everything
        left, right = [s.strip() for s in row["relationship"].split("~")]
        left = "methane" if left == "methane" else left
        for method in ("pearson", "spearman"):
            emit("operational", row["weighting"], row["relationship"],
                 row["controlling_for"], left, right, subset, method,
                 as_float(row[method]), as_float(row[f"{method}_p"]))

    # The blended and raw fields, whose correlations live only in prose. The
    # raw field matters as much as the blended one here: the albedo figure's
    # caption says the impervious association "survives control" on the raw
    # retrieval at p 4.0e-06, and that is a significance claim resting on an
    # uncorrected n.
    for field, column in (("blended", "methane_blended"),
                          ("raw", "methane_raw")):
        usable = ~np.isnan(series[column])
        for weighting in ("unweighted", "by sounding count"):
            for suffix, controlling in (
                    ("impervious_fraction", ""),
                    ("rice_fraction_single", ""),
                    ("surface_albedo_SWIR", ""),
                    ("impervious_fraction", "surface_albedo_SWIR"),
                    ("rice_fraction_single", "surface_albedo_SWIR")):
                relationship = f"{column} ~ {suffix}"
                subset = usable & (present if "rice" in suffix else everything)
                emit(field, weighting, relationship, controlling,
                     column, suffix, subset, "pearson", None, None)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT),
                        help="where to write; the recipe runner redirects it")
    args = parser.parse_args()

    rows = build_rows(load_series())

    header = (f"{'field':<12} {'weighting':<18} {'relationship':<46} "
              f"{'ctrl':<5} {'meth':<9} {'n':>5} {'M':>7} {'r':>8} "
              f"{'p nom':>10} {'p corr':>10}  verdict")
    print(header)
    print("-" * len(header))
    for r in rows:
        print(f"{r['field']:<12} {r['weighting']:<18} {r['relationship']:<46} "
              f"{('yes' if r['controlling_for'] else '-'):<5} "
              f"{r['method']:<9} {r['n']:>5} {r['effective_n']:>7} "
              f"{r['coefficient']:>8} {r['p_nominal']:>10} "
              f"{r['p_corrected']:>10}  {r['verdict']}")

    changed = [r for r in rows if r["verdict"] == "was significant, now is not"]
    print(f"\n  {len(rows)} correlations; {len(changed)} lose significance")
    shrink = np.array([float(r["shrinkage"]) for r in rows])
    print(f"  effective n as a fraction of nominal: median "
          f"{np.median(shrink):.4f}, range {shrink.min():.4f} to "
          f"{shrink.max():.4f}")
    for r in changed:
        print(f"    {r['field']:<12} {r['weighting']:<18} "
              f"{r['relationship']} "
              f"{'| ctrl ' + r['controlling_for'] if r['controlling_for'] else ''}"
              f" [{r['method']}] r={r['coefficient']} "
              f"p {r['p_nominal']} -> {r['p_corrected']}")

    if args.write:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nwrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
