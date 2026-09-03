"""Descriptive association, including partial association given a control.

Nothing here is a model and nothing here supports a causal reading. It exists
for one question: whether an apparent land-cover signal in the methane field is
instead a retrieval artefact.

The reason to ask is specific. TROPOMI's methane retrieval depends on how much
light comes back, so it fails preferentially over dark surfaces; reconnaissance
over this study area measured a median ``surface_albedo_SWIR`` of 0.1058 on
valid soundings against 0.0621 on invalid ones. The literature reports a
seasonal surface-albedo bias in TROPOMI methane over agricultural land. And rice
paddies flood, which changes their albedo on the same seasonal cycle as their
methane emission. So albedo is correlated with the land cover *and* plausibly
with the retrieved value, which is the exact shape of a confounder.

If methane correlates with albedo, and albedo correlates with a land-cover
fraction, then part of any methane-to-land-cover association is the retrieval
looking at itself. That has to be reported whichever way the land-cover result
goes, and it has to be reported before the predictor results rather than after.

Partial correlation here is the residual method: regress both variables on the
control and correlate what is left. For Spearman the variables are rank
transformed first, which is the usual construction and measures monotone rather
than linear association. Weighted forms use the same weights as the models in
``src.model.baselines``, so a partial correlation and a fit describe the same
cells with the same emphasis.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


class AssociationError(RuntimeError):
    """Base class for failures this module raises deliberately."""


@dataclass(frozen=True)
class Association:
    """One correlation, with the sample it rests on."""

    name: str
    n: int
    pearson: float
    pearson_p: float
    spearman: float
    spearman_p: float
    controls: tuple[str, ...] = ()

    def as_dict(self) -> dict:
        return {
            "relationship": self.name,
            "controlling_for": ", ".join(self.controls),
            "n": self.n,
            "pearson": round(self.pearson, 4),
            "pearson_p": f"{self.pearson_p:.3e}",
            "spearman": round(self.spearman, 4),
            "spearman_p": f"{self.spearman_p:.3e}",
        }


def paired(*arrays) -> tuple[np.ndarray, ...]:
    """The rows where every array is finite, aligned."""
    arrays = [np.asarray(a, dtype="float64") for a in arrays]
    if len({a.shape for a in arrays}) != 1:
        raise AssociationError("arrays must be the same length to be paired")
    keep = np.ones(arrays[0].shape, dtype=bool)
    for array in arrays:
        keep &= np.isfinite(array)
    return tuple(a[keep] for a in arrays)


def _residuals(values: np.ndarray, controls: np.ndarray,
               weight: np.ndarray) -> np.ndarray:
    """What is left of ``values`` after removing what the controls explain."""
    design = np.column_stack([np.ones(values.size), controls])
    root = np.sqrt(weight)
    coefficients, *_ = np.linalg.lstsq(design * root[:, None], values * root,
                                       rcond=None)
    return values - design @ coefficients


def _p_from_r(r: float, n: int, k: int) -> float:
    """Two-sided p for a correlation with ``k`` controls partialled out."""
    df = n - 2 - k
    if df <= 0 or not np.isfinite(r) or abs(r) >= 1.0:
        return float("nan")
    t = r * np.sqrt(df / (1.0 - r * r))
    return float(2 * stats.t.sf(abs(t), df))


def correlate(name: str, x, y, *, weight=None) -> Association:
    """Pearson and Spearman on the rows where both are observed."""
    if weight is None:
        x, y = paired(x, y)
        w = np.ones(x.size)
    else:
        x, y, w = paired(x, y, weight)
    if x.size < 3:
        raise AssociationError(f"{name}: only {x.size} paired observations")
    if weight is None:
        pearson, pearson_p = stats.pearsonr(x, y)
        spearman, spearman_p = stats.spearmanr(x, y)
        return Association(name, int(x.size), float(pearson), float(pearson_p),
                           float(spearman), float(spearman_p))
    # Weighted: correlate on the values themselves and on their ranks, using
    # the weighted covariance, so the weighting means the same thing here as it
    # does in the fits.
    pearson = _weighted_corr(x, y, w)
    spearman = _weighted_corr(stats.rankdata(x), stats.rankdata(y), w)
    n = int(x.size)
    return Association(name, n, pearson, _p_from_r(pearson, n, 0),
                       spearman, _p_from_r(spearman, n, 0))


def _weighted_corr(x, y, w) -> float:
    total = w.sum()
    mx, my = (w * x).sum() / total, (w * y).sum() / total
    cov = (w * (x - mx) * (y - my)).sum() / total
    vx = (w * (x - mx) ** 2).sum() / total
    vy = (w * (y - my) ** 2).sum() / total
    if vx <= 0 or vy <= 0:
        return float("nan")
    return float(cov / np.sqrt(vx * vy))


@dataclass(frozen=True)
class Sensitivity:
    """A fitted slope in the units of y per unit of x.

    A correlation says how tightly two things move together; a slope says by
    how much. For an instrument bias the slope is the quantity that can be
    compared against a published one, because it does not depend on how much
    the predictor happened to vary in this particular sample.
    """

    name: str
    n: int
    slope: float
    standard_error: float
    intercept: float
    r2: float

    @property
    def t(self) -> float:
        if self.standard_error <= 0:
            return float("nan")
        return self.slope / self.standard_error

    def as_dict(self) -> dict:
        return {
            "relationship": self.name,
            "n": self.n,
            "slope": round(self.slope, 4),
            "standard_error": round(self.standard_error, 4),
            "r2": round(self.r2, 6),
        }


def sensitivity(name: str, y, x, *, weight=None) -> Sensitivity:
    """Least-squares slope of y on x, with its standard error and R squared.

    Weighted by ``weight`` if given, using the same weights as everything else
    in this package so a slope and a correlation describe the same cells.
    """
    if weight is None:
        y, x = paired(y, x)
        w = np.ones(x.size)
    else:
        y, x, w = paired(y, x, weight)
    if x.size < 3:
        raise AssociationError(f"{name}: only {x.size} paired observations")

    design = np.column_stack([np.ones(x.size), x])
    root = np.sqrt(w)
    coefficients, *_ = np.linalg.lstsq(design * root[:, None], y * root, rcond=None)
    residual = y - design @ coefficients
    dof = x.size - 2
    variance = float(np.sum(w * residual ** 2) / dof)
    covariance = variance * np.linalg.inv((design * w[:, None]).T @ design)
    centre = float(np.sum(w * y) / w.sum())
    total = float(np.sum(w * (y - centre) ** 2))
    explained = 1.0 - float(np.sum(w * residual ** 2)) / total if total > 0 else float("nan")
    return Sensitivity(name=name, n=int(x.size), slope=float(coefficients[1]),
                       standard_error=float(np.sqrt(covariance[1, 1])),
                       intercept=float(coefficients[0]), r2=explained)


def partial_correlation(name: str, x, y, controls, control_names,
                        *, weight=None) -> Association:
    """Correlation between x and y with the controls removed from both.

    Both variables are regressed on the controls and the residuals correlated.
    A partial correlation near zero where the raw correlation was not says the
    control accounts for the association; a partial correlation that survives
    says the association is not only the control.
    """
    controls = np.column_stack([np.asarray(c, dtype="float64") for c in controls])
    columns = [x, y] + [controls[:, i] for i in range(controls.shape[1])]
    if weight is not None:
        columns.append(weight)
    kept = paired(*columns)
    x, y = kept[0], kept[1]
    control_matrix = np.column_stack(kept[2:2 + controls.shape[1]])
    w = kept[-1] if weight is not None else np.ones(x.size)

    k = control_matrix.shape[1]
    if x.size < k + 4:
        raise AssociationError(
            f"{name}: {x.size} observations cannot support {k} controls")

    rx = _residuals(x, control_matrix, w)
    ry = _residuals(y, control_matrix, w)
    pearson = _weighted_corr(rx, ry, w)

    # Spearman: rank first, then partial, which is the standard construction.
    sx = _residuals(stats.rankdata(x), control_matrix, w)
    sy = _residuals(stats.rankdata(y), control_matrix, w)
    spearman = _weighted_corr(sx, sy, w)

    n = int(x.size)
    return Association(name, n, pearson, _p_from_r(pearson, n, k),
                       spearman, _p_from_r(spearman, n, k),
                       controls=tuple(control_names))
