#!/usr/bin/env python3
"""Measure the autocorrelation range of the baseline models' residuals.

    python scripts/measure_residual_range.py
    python scripts/measure_residual_range.py --write

`notes/grounding-methods.md` records Roberts et al.'s rule that the minimum
blocking distance for spatial cross-validation should be the extent of
autocorrelation in the **model's residuals**, with blocks only as large as
required, and records that this project has never measured it. What it has is
Moran's I of one residual field, 0.646, which is a different quantity: Moran's I
says whether structure is present at one neighbourhood definition and says
nothing about the distance over which it decays.

The block size in use is 4 by 4 cells, about 111 km across, and
`data/processed/README.md` records that it was chosen against the **methane
field's** own half-sill range of 102 km. That is the target's range, not a
model's residual range, so the choice has never been justified on the terms the
literature sets.

**What is fitted here.** For each field and model, the model is fitted to all
covered cells and the in-sample residuals are taken. In-sample and not held-out:
Roberts' rule is about the residual structure a fitted model leaves behind, and
held-out residuals from a blocked scheme mix that structure with the fold
geometry, which would make the diagnostic depend on the choice it is meant to
inform.

An empirical semivariogram of those residuals is computed over great-circle lags
and an exponential model is fitted to it,

    gamma(h) = nugget + (sill - nugget) * (1 - exp(-h / a))

by least squares on the binned estimates weighted by pair count. Three ranges
are reported because the literature uses all three and they differ by a factor
of three: the fitted parameter `a`, the **practical range** `3a` at which the
model reaches 95 percent of its sill, and the **half-sill range** at which the
empirical variogram first reaches half its total variance, which is the
definition `data/processed/README.md` already uses for the 102 km figure and so
the one to compare against.
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import numpy as np
from scipy import optimize

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.model import spatial_dof as sd  # noqa: E402

PROCESSED = REPO / "data" / "processed"
OUT = PROCESSED / "residual_range_2018.csv"

#: Lag bins for the variogram. Twenty-five bins to 600 km gives 24 km bins,
#: just under one cell width, and stops short of the domain's 1,200 km extent
#: because the far bins rest on few, geometrically peculiar pairs -- opposite
#: corners of a rectangle -- and a variogram is conventionally fitted over
#: something like half the maximum lag for that reason.
N_BINS = 25
MAX_LAG_KM = 600.0

#: The block size in use, for comparison. Four cells at 0.25 degrees.
#:
#: **It has two widths and the repository has only ever quoted one.**
#: `data/processed/README.md` says "a four-cell block is about 111 km across",
#: which is the north-south width, since one degree of latitude is 111 km
#: everywhere. East-west it is narrower, because one degree of longitude
#: shrinks with the cosine of latitude: at this domain's mid-latitude of about
#: 31 degrees a four-cell span is 95 km. A block is therefore 111 by 95 km, and
#: the relevant figure for a range comparison is the **smaller** one, because
#: that is the shortest distance a block guarantees between a held-out cell and
#: the training data.
BLOCK_CELLS = 4

#: The upper bound on the fitted range parameter. When the fit lands on it the
#: variogram has not flattened inside the window and the range is not
#: identified; reporting `3a` then would be reporting the bound.
RANGE_BOUND_KM = MAX_LAG_KM * 5


def read_csv(path: Path) -> list[dict]:
    with path.open(newline="") as handle:
        return list(csv.DictReader(handle))


def cell_key(row: dict) -> tuple[int, int]:
    return (round(float(row["centre_lat"]) * 1000),
            round(float(row["centre_lon"]) * 1000))


def load() -> dict[str, np.ndarray]:
    grid = read_csv(PROCESSED / "analysis_grid_2018.csv")
    cov = {cell_key(r): r for r in read_csv(PROCESSED / "methane_covariates_2018.csv")}
    blend = {cell_key(r): r for r in read_csv(PROCESSED / "methane_blended_2018.csv")}

    def f(value: str) -> float:
        return float(value) if value not in ("", None) else float("nan")

    out: dict[str, list[float]] = {k: [] for k in (
        "lat", "lon", "row", "col", "operational", "blended", "impervious",
        "rice", "albedo_swir", "albedo_nir", "sza")}
    for r in grid:
        k = cell_key(r)
        c, b = cov.get(k), blend.get(k)
        out["lat"].append(f(r["centre_lat"]))
        out["lon"].append(f(r["centre_lon"]))
        out["operational"].append(f(r["ch4_bias_corrected_ppb"]))
        out["blended"].append(f(b["ch4_blended_ppb"]) if b else float("nan"))
        out["impervious"].append(f(r["impervious_fraction"]))
        out["rice"].append(f(r["rice_fraction_single"]))
        out["albedo_swir"].append(f(c["surface_albedo_SWIR_mean"]) if c else float("nan"))
        out["albedo_nir"].append(f(c["surface_albedo_NIR_mean"]) if c else float("nan"))
        out["sza"].append(f(c["solar_zenith_angle_mean"]) if c else float("nan"))
        out["row"].append(0.0)
        out["col"].append(0.0)
    return {k: np.asarray(v, dtype="float64") for k, v in out.items()}


def queen_neighbour_mean(values: np.ndarray, lat: np.ndarray,
                         lon: np.ndarray, *, resolution: float = 0.25
                         ) -> np.ndarray:
    """Mean of the eight surrounding cells, excluding the cell itself.

    The spatial null this repository reports. Cells with no covered neighbour
    fall back to the global mean, which is what the baseline module does.
    """
    key = {(round(a / resolution), round(o / resolution)): i
           for i, (a, o) in enumerate(zip(lat, lon))}
    out = np.full(len(values), np.nan)
    for i, (a, o) in enumerate(zip(lat, lon)):
        r, c = round(a / resolution), round(o / resolution)
        neighbours = [key[(r + dr, c + dc)]
                      for dr in (-1, 0, 1) for dc in (-1, 0, 1)
                      if (dr, dc) != (0, 0) and (r + dr, c + dc) in key]
        picked = [values[j] for j in neighbours if np.isfinite(values[j])]
        out[i] = np.mean(picked) if picked else np.nanmean(values)
    return out


def ols_residual(y: np.ndarray, predictors: list[np.ndarray]) -> np.ndarray:
    design = np.column_stack([np.ones(len(y))] + list(predictors))
    beta, *_ = np.linalg.lstsq(design, y, rcond=None)
    return y - design @ beta


def variogram(values: np.ndarray, lat: np.ndarray, lon: np.ndarray
              ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Binned empirical semivariogram: lag centres, gamma, pair counts."""
    d = sd.great_circle_km(lat, lon)
    diff = 0.5 * (values[:, None] - values[None, :]) ** 2
    iu = np.triu_indices(len(values), k=1)
    d, diff = d[iu], diff[iu]

    edges = np.linspace(0.0, MAX_LAG_KM, N_BINS + 1)
    index = np.digitize(d, edges) - 1
    lags, gammas, counts = [], [], []
    for b in range(N_BINS):
        mask = index == b
        if mask.sum() >= 30:
            lags.append(0.5 * (edges[b] + edges[b + 1]))
            gammas.append(float(diff[mask].mean()))
            counts.append(int(mask.sum()))
    return np.array(lags), np.array(gammas), np.array(counts)


def fit_exponential(lags: np.ndarray, gamma: np.ndarray, counts: np.ndarray
                    ) -> tuple[float, float, float]:
    """Least-squares exponential variogram, weighted by pair count.

    Returns nugget, sill and the range parameter `a`. The starting range is a
    third of the maximum lag, which is where an exponential model's practical
    range would sit if the structure filled the fitted window.
    """
    def model(h, nugget, partial, a):
        return nugget + partial * (1.0 - np.exp(-h / a))

    p0 = [gamma.min(), max(gamma.max() - gamma.min(), 1e-9), MAX_LAG_KM / 3.0]
    bounds = ([0.0, 0.0, 1.0], [gamma.max() * 2 + 1e-9, gamma.max() * 4 + 1e-9,
                                RANGE_BOUND_KM])
    popt, _ = optimize.curve_fit(model, lags, gamma, p0=p0, bounds=bounds,
                                 sigma=1.0 / np.sqrt(counts), maxfev=20000)
    nugget, partial, a = popt
    return float(nugget), float(nugget + partial), float(a)


def half_sill_range(lags: np.ndarray, gamma: np.ndarray,
                    total_variance: float) -> float:
    """First lag at which the empirical variogram reaches half the variance.

    The definition `data/processed/README.md` uses for the field's 102 km
    figure, kept so the two are comparable. Linearly interpolated between the
    bracketing bins; NaN when the variogram never gets there inside the fitted
    window, which is itself informative.
    """
    target = 0.5 * total_variance
    for i in range(len(lags)):
        if gamma[i] >= target:
            if i == 0:
                return float(lags[0])
            x0, x1 = lags[i - 1], lags[i]
            y0, y1 = gamma[i - 1], gamma[i]
            return float(x0 + (target - y0) * (x1 - x0) / (y1 - y0))
    return float("nan")


def block_widths_km(lat: np.ndarray) -> tuple[float, float]:
    """North-south and east-west great-circle widths of a four-cell block."""
    mid = float(np.mean(lat))
    span = BLOCK_CELLS * 0.25
    north_south = float(sd.great_circle_km(np.array([mid, mid + span]),
                                           np.array([0.0, 0.0]))[0, 1])
    east_west = float(sd.great_circle_km(np.array([mid, mid]),
                                         np.array([0.0, span]))[0, 1])
    return north_south, east_west


def rows() -> list[dict]:
    data = load()
    out: list[dict] = []
    north_south, east_west = block_widths_km(data["lat"])

    for field in ("operational", "blended"):
        y = data[field]
        ok = np.isfinite(y) & np.isfinite(data["albedo_swir"])
        lat, lon = data["lat"][ok], data["lon"][ok]
        yv = y[ok]

        models = {
            "the field itself (no model)": yv - yv.mean(),
            "OLS impervious fraction": ols_residual(yv, [data["impervious"][ok]]),
            "spatial null (queen neighbour mean)":
                yv - queen_neighbour_mean(y, data["lat"], data["lon"])[ok],
            "OLS full covariates (albedo SWIR, NIR, SZA)":
                ols_residual(yv, [data["albedo_swir"][ok],
                                  data["albedo_nir"][ok], data["sza"][ok]]),
            "OLS impervious plus full covariates":
                ols_residual(yv, [data["impervious"][ok], data["albedo_swir"][ok],
                                  data["albedo_nir"][ok], data["sza"][ok]]),
        }

        for name, residual in models.items():
            residual = residual[np.isfinite(residual)]
            if len(residual) != len(lat):
                keep = np.isfinite(models[name])
                rl, ro = lat[keep], lon[keep]
            else:
                rl, ro = lat, lon
            lags, gamma, counts = variogram(residual, rl, ro)
            total = float(np.var(residual, ddof=1))
            nugget, sill, a = fit_exponential(lags, gamma, counts)
            half = half_sill_range(lags, gamma, total)
            identified = a < RANGE_BOUND_KM * 0.98
            out.append({
                "field": field, "model": name, "n": len(residual),
                "residual_sd_ppb": f"{np.std(residual, ddof=1):.3f}",
                "nugget": f"{nugget:.2f}", "sill": f"{sill:.2f}",
                "nugget_fraction": f"{nugget / sill:.3f}" if sill else "",
                "range_a_km": f"{a:.1f}" if identified else "not identified",
                "practical_range_km": f"{3 * a:.1f}" if identified else "",
                "half_sill_range_km": ("" if np.isnan(half) else f"{half:.1f}"),
                "block_ns_km": f"{north_south:.1f}",
                "block_ew_km": f"{east_west:.1f}",
                "verdict": verdict(half, east_west),
            })
    return out


def verdict(half: float, narrow_width: float) -> str:
    """Whether the block in use clears the residual's half-sill range.

    Judged against the block's **narrower** width, which is the shortest
    separation it guarantees. The half-sill range is used rather than the
    fitted practical range because the fitted range is unidentified for several
    of these models: their variograms do not flatten inside the 600 km window,
    so the exponential fit lands on its bound and `3a` would report the bound
    rather than a range.
    """
    if np.isnan(half):
        return "half-sill not reached inside the fitted window"
    if half <= narrow_width * 0.5:
        return "residual decorrelates well inside a block; block is ample"
    if half <= narrow_width:
        return "residual decorrelates inside a block; block is adequate"
    return "residual still correlated at a block width; block is too small"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--out", default=str(OUT),
                        help="where to write; the recipe runner redirects it")
    args = parser.parse_args()

    table = rows()
    print(f"{'field':<12} {'model':<44} {'sd':>7} {'nug/sill':>9} "
          f"{'a':>7} {'3a':>8} {'half':>7}  verdict")
    print("-" * 132)
    for r in table:
        print(f"{r['field']:<12} {r['model']:<44} {r['residual_sd_ppb']:>7} "
              f"{r['nugget_fraction']:>9} {r['range_a_km']:>7} "
              f"{r['practical_range_km']:>8} {r['half_sill_range_km']:>7}  "
              f"{r['verdict']}")
    print(f"\n  block in use: {BLOCK_CELLS} by {BLOCK_CELLS} cells, "
          f"{table[0]['block_ns_km']} km north-south by "
          f"{table[0]['block_ew_km']} km east-west")

    if args.write:
        target = Path(args.out)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(table[0]))
            writer.writeheader()
            writer.writerows(table)
        print(f"\nwrote {target}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
