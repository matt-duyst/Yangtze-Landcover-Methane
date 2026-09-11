"""Effective degrees of freedom for a correlation between two spatial fields.

Every Pearson and partial correlation this repository reports is computed over
926 lattice cells with `n` treated as 926, and both variables are strongly
autocorrelated: Moran's I of the methane field is 0.709 and of impervious
fraction higher still. The nominal p-value is therefore anti-conservative,
sometimes by orders of magnitude, and `notes/grounding-methods.md` records that
the Moran's I permutation test is the only statistic in the repository that
handles its own dependence.

**Why Dutilleul's route and not Afyouni's.** Two corrections are in the
register. Afyouni, Smith and Nichols (2019, `10.1016/j.neuroimage.2019.05.011`)
correct the effective degrees of freedom of a correlation between two *time
series*, accounting for autocorrelation in each and for instantaneous and lagged
cross-correlation. Their construction is ordered: it needs a lag index, and on a
two-dimensional lattice with irregular gaps there is no lag ordering to use
without inventing one. Clifford, Richardson and Hémon (1989,
`10.2307/2532039`) and Dutilleul, Clifford, Richardson and Hémon (1993,
`10.2307/2532625`) correct the same quantity for two *spatial* processes, using
distance rather than lag, which is the structure this lattice actually has. So
Dutilleul, and the choice is about the data's geometry rather than about the
methods' quality.

**The estimator.** Under the null hypothesis of no correlation between X and Y,
the variance of the sample correlation is approximately

    Var(r) ~ tr(R_X R_Y) / n^2

where `R_X` and `R_Y` are the two fields' spatial correlation matrices. Writing
that as a sum over pairs,

    tr(R_X R_Y) = sum_i sum_j rho_X(d_ij) rho_Y(d_ij)

so the effective sample size is

    M = 1 + n^2 / tr(R_X R_Y)

and the modified t statistic is `t = r sqrt((M - 2) / (1 - r^2))` on `M - 2`
degrees of freedom. When neither field is autocorrelated, `R_X` and `R_Y` are
identity matrices, `tr(R_X R_Y) = n`, and `M = n + 1`: the correction reduces to
the nominal test, which is the property to check it against.

`rho(d)` is estimated by binning pair distances and taking the empirical
correlation within each bin, which is the correlogram estimator the published
implementations use. Distances are great-circle on the cell centres, because
the lattice spans eight degrees of latitude and planar distance would be wrong
by several percent at the edges.

**What this does not do.** It corrects the significance of a correlation, not
its value. A coefficient that falls from significant to non-significant here has
not changed size; the claim that it differs from zero has lost its support.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats

EARTH_RADIUS_KM = 6371.0088


@dataclass(frozen=True)
class ModifiedTTest:
    """A correlation with both the nominal and the corrected test beside it."""

    r: float
    n: int
    effective_n: float
    p_nominal: float
    p_corrected: float
    bins: int

    @property
    def shrinkage(self) -> float:
        """Effective n as a fraction of nominal n. Lower means more dependence."""
        return self.effective_n / self.n

    @property
    def still_significant(self) -> bool:
        return self.p_corrected < 0.05

    @property
    def changed_verdict(self) -> bool:
        """Significant at 5 percent nominally and not after correction."""
        return self.p_nominal < 0.05 and not self.still_significant


def great_circle_km(lat: np.ndarray, lon: np.ndarray) -> np.ndarray:
    """Pairwise great-circle distances in km, as a full square matrix."""
    phi = np.radians(np.asarray(lat, dtype="float64"))
    lam = np.radians(np.asarray(lon, dtype="float64"))
    dphi = phi[:, None] - phi[None, :]
    dlam = lam[:, None] - lam[None, :]
    a = (np.sin(dphi / 2.0) ** 2
         + np.cos(phi)[:, None] * np.cos(phi)[None, :] * np.sin(dlam / 2.0) ** 2)
    return 2.0 * EARTH_RADIUS_KM * np.arcsin(np.sqrt(np.clip(a, 0.0, 1.0)))


def correlogram(values: np.ndarray, distance: np.ndarray,
                edges: np.ndarray) -> np.ndarray:
    """Empirical spatial correlation per distance bin, as a pair matrix.

    Returns a matrix the same shape as `distance` holding, for each pair, the
    estimated correlation at that pair's separation. The diagonal is 1 by
    construction. Bins with no pairs get 0, which is the conservative choice:
    it lowers `tr(R_X R_Y)` and so raises the effective sample size, so a sparse
    bin cannot manufacture an aggressive correction.
    """
    z = np.asarray(values, dtype="float64")
    z = z - z.mean()
    var = float(np.mean(z * z))
    if var <= 0:
        raise ValueError("a constant field has no correlogram")

    products = np.outer(z, z) / var
    out = np.zeros_like(distance, dtype="float64")
    index = np.digitize(distance, edges) - 1
    for b in range(len(edges) - 1):
        mask = index == b
        if mask.any():
            out[mask] = products[mask].mean()
    np.fill_diagonal(out, 1.0)
    return out


def effective_sample_size(x: np.ndarray, y: np.ndarray, lat: np.ndarray,
                          lon: np.ndarray, *, bins: int = 30) -> float:
    """Dutilleul's effective sample size for corr(x, y) on a spatial lattice."""
    distance = great_circle_km(lat, lon)
    upper = float(distance.max())
    if upper <= 0:
        raise ValueError("all locations coincide")
    edges = np.linspace(0.0, upper * (1.0 + 1e-9), bins + 1)

    rx = correlogram(x, distance, edges)
    ry = correlogram(y, distance, edges)
    trace = float(np.sum(rx * ry))          # tr(R_X R_Y) for symmetric R
    n = len(x)
    if trace <= 0:
        return float(n + 1)
    return 1.0 + n * n / trace


def modified_t_test(x: np.ndarray, y: np.ndarray, lat: np.ndarray,
                    lon: np.ndarray, *, bins: int = 30,
                    r: float | None = None) -> ModifiedTTest:
    """Pearson correlation with Dutilleul's corrected significance.

    `r` may be supplied when the coefficient was computed elsewhere -- a partial
    or weighted correlation, say -- so that only the degrees of freedom are
    corrected. The effective sample size is then estimated from the two residual
    or raw series passed in, which is the correct pair to estimate it from: the
    dependence that inflates the test is the dependence in what was correlated.
    """
    x = np.asarray(x, dtype="float64")
    y = np.asarray(y, dtype="float64")
    n = len(x)
    coefficient = float(stats.pearsonr(x, y).statistic) if r is None else float(r)

    m = effective_sample_size(x, y, lat, lon, bins=bins)
    m = min(m, float(n + 1))                # the correction cannot add information

    def p_from(df_plus_two: float) -> float:
        df = df_plus_two - 2.0
        if df <= 0 or abs(coefficient) >= 1.0:
            return float("nan")
        t = coefficient * np.sqrt(df / (1.0 - coefficient ** 2))
        return float(2.0 * stats.t.sf(abs(t), df))

    return ModifiedTTest(r=coefficient, n=n, effective_n=m,
                         p_nominal=p_from(float(n)),
                         p_corrected=p_from(m), bins=bins)


def partial_residuals(target: np.ndarray, predictor: np.ndarray,
                      controls: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Both sides of a partial correlation, with the controls regressed out.

    Returned so that the effective sample size is estimated from the residual
    series rather than from the raw ones. A partial correlation is a correlation
    between residuals, and those are the fields whose spatial dependence sets
    the test's degrees of freedom.
    """
    design = np.column_stack([np.ones(len(target)), np.asarray(controls,
                                                               dtype="float64")])
    def residual(v: np.ndarray) -> np.ndarray:
        v = np.asarray(v, dtype="float64")
        beta, *_ = np.linalg.lstsq(design, v, rcond=None)
        return v - design @ beta
    return residual(target), residual(predictor)
