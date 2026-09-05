r"""Removing a shared seasonal cycle at the sounding level, in one pass.

The problem this solves is that a cell's annual mean is taken over whichever
days happened to be observed there, and those days differ systematically
between cells. Mean solar zenith angle per cell runs from 12.69 to 56.67
degrees over this study area, and latitude explains only 2.4 percent of that
variance, so nearly all of it is calendar. XCH4 has a strong seasonal cycle, so
a cell sampled mostly in October and a cell sampled mostly in June differ in
their annual mean for reasons that have nothing to do with emissions.

Subtracting a seasonal cycle from the *cell means* cannot fix this, because by
then the information about which days contributed has already been averaged
away. It has to come off at the sounding level. That normally means either
holding every sounding in memory, which is 110,920 soundings for one year and
does not stream, or two passes over 28.9 GB. Neither is necessary.

THE MODEL
---------

For sounding :math:`i` falling in cell :math:`j(i)` on fractional day-of-year
:math:`d_i`, with :math:`P = 365.25`:

.. math::

    y_i = \mu_{j(i)} + \sum_{k=1}^{K} \left[
        a_k \sin(2\pi k d_i / P) + b_k \cos(2\pi k d_i / P)\right] + e_i

The harmonic coefficients are shared by every cell; the offsets
:math:`\mu_j` are per cell and are what we want. Write
:math:`x_{i} = (x_{i1}, \dots, x_{iT})` for the :math:`T = 2K` harmonic terms
evaluated at :math:`d_i`, and :math:`\beta` for their coefficients.

THE DERIVATION
--------------

This is a fixed-effects model with one dummy per cell, and it is solved by the
standard within transformation rather than by forming a 1,025-column design.

For any fixed :math:`\beta`, the least-squares offset for cell :math:`j` is the
mean residual in that cell:

.. math::

    \hat\mu_j(\beta) = \bar y_j - \beta^\top \bar x_j

Substituting that back into the sum of squares profiles the offsets out, and
what is left depends only on within-cell deviations:

.. math::

    S(\beta) = \sum_j \sum_{i \in j}
        \left[(y_i - \bar y_j) - \beta^\top (x_i - \bar x_j)\right]^2

which is ordinary least squares of within-cell-centred :math:`y` on
within-cell-centred :math:`x`, with no intercept. Its normal equations are
:math:`A\beta = r` with

.. math::

    A_{k\ell} = \sum_j \left[ \textstyle\sum_{i \in j} x_{ik} x_{i\ell}
        - \frac{(\sum_i x_{ik})(\sum_i x_{i\ell})}{n_j} \right], \quad
    r_k = \sum_j \left[ \textstyle\sum_{i \in j} y_i x_{ik}
        - \frac{(\sum_i y_i)(\sum_i x_{ik})}{n_j} \right]

**Every quantity on the right is a sum over soundings.** Nothing needs a
sounding twice, nothing needs them in order, and nothing needs them in memory.
Accumulating :math:`n_j`, :math:`\sum y`, :math:`\sum y^2`, :math:`\sum x_k`,
:math:`\sum x_k x_\ell` and :math:`\sum y x_k` per cell is sufficient, and
:math:`A` and :math:`r` are assembled from them afterwards. :math:`A` is
:math:`T \times T` -- four by four for two harmonics -- however many soundings
there were.

The residual sum of squares follows from the same statistics:

.. math::

    \mathrm{RSS} = T_{yy} - \beta^\top r, \qquad
    T_{yy} = \sum_j \left[\textstyle\sum_i y_i^2 - (\sum_i y_i)^2 / n_j\right]

on :math:`N - J - T` degrees of freedom, where :math:`J` counts cells with at
least one sounding, since each consumes one offset.

WHAT A SINGLETON CELL CONTRIBUTES
---------------------------------

A cell with one sounding has :math:`x_i - \bar x_j = 0` and
:math:`y_i - \bar y_j = 0`, so it contributes exactly zero to both :math:`A`
and :math:`r`. It does not bias the seasonal fit; it simply carries no
information about it, and it still consumes a degree of freedom. It does get a
:math:`\mu_j`, but that offset is the single sounding with the fitted cycle
subtracted at that one date, so it is not separable from the cycle by anything
in the data. :class:`SeasonalFit` flags such cells rather than dropping them,
because a caller deciding what to do with them should be told, not obeyed.

More generally the same is true of any cell whose sampling dates are tightly
clustered. Separability is a matter of degree, and
:meth:`HarmonicStats.date_spread` reports it per cell so the caller can set a
threshold in days rather than guess.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Sequence

import numpy as np

#: Tropical year in days. The choice barely matters over a single year but is
#: stated so a multi-year fit does not silently drift against the calendar.
DEFAULT_PERIOD = 365.25


class SeasonalError(RuntimeError):
    """Base class for failures this module raises deliberately."""


class NotEnoughSeasonalSpread(SeasonalError):
    """No cell was sampled over enough of the year to identify a cycle."""


@dataclass(frozen=True)
class HarmonicBasis:
    """The shared seasonal terms, evaluated at a day of year."""

    harmonics: int = 2
    period: float = DEFAULT_PERIOD

    def __post_init__(self):
        if self.harmonics < 1:
            raise SeasonalError("a harmonic basis needs at least one harmonic")

    @property
    def n_terms(self) -> int:
        return 2 * self.harmonics

    @property
    def labels(self) -> tuple[str, ...]:
        out = []
        for k in range(1, self.harmonics + 1):
            out += [f"sin{k}", f"cos{k}"]
        return tuple(out)

    def design(self, day: np.ndarray) -> np.ndarray:
        """``(n_soundings, n_terms)`` of harmonic values."""
        day = np.atleast_1d(np.asarray(day, dtype="float64"))
        columns = []
        for k in range(1, self.harmonics + 1):
            angle = 2.0 * np.pi * k * day / self.period
            columns += [np.sin(angle), np.cos(angle)]
        return np.column_stack(columns)

    def evaluate(self, day, coefficients) -> np.ndarray:
        """The fitted cycle at each day."""
        return self.design(day) @ np.asarray(coefficients, dtype="float64")


@dataclass
class HarmonicStats:
    """Per-cell sufficient statistics for the fixed-effects harmonic fit.

    A fixed number of floats per cell regardless of how many soundings land in
    it: for two harmonics that is 23 per cell, so the whole 33 by 31 grid costs
    about 188 kB against a checkpoint already holding three float64 grids.
    """

    shape: tuple[int, int]
    basis: HarmonicBasis = field(default_factory=HarmonicBasis)
    n: np.ndarray = field(default=None)
    sum_y: np.ndarray = field(default=None)
    sum_yy: np.ndarray = field(default=None)
    sum_d: np.ndarray = field(default=None)
    sum_dd: np.ndarray = field(default=None)
    sum_x: np.ndarray = field(default=None)
    sum_xx: np.ndarray = field(default=None)
    sum_yx: np.ndarray = field(default=None)

    def __post_init__(self):
        t = self.basis.n_terms
        if self.n is None:
            self.n = np.zeros(self.shape, dtype="int64")
        for name in ("sum_y", "sum_yy", "sum_d", "sum_dd"):
            if getattr(self, name) is None:
                setattr(self, name, np.zeros(self.shape, dtype="float64"))
        if self.sum_x is None:
            self.sum_x = np.zeros((t, *self.shape), dtype="float64")
        if self.sum_yx is None:
            self.sum_yx = np.zeros((t, *self.shape), dtype="float64")
        if self.sum_xx is None:
            self.sum_xx = np.zeros((t, t, *self.shape), dtype="float64")

    # -- accumulation ---------------------------------------------------

    def add(self, row, col, y, day) -> None:
        """Add a batch of soundings. Order and batching do not matter."""
        row = np.atleast_1d(np.asarray(row, dtype="int64"))
        col = np.atleast_1d(np.asarray(col, dtype="int64"))
        y = np.atleast_1d(np.asarray(y, dtype="float64"))
        day = np.atleast_1d(np.asarray(day, dtype="float64"))
        if day.size == 1 and y.size > 1:
            day = np.repeat(day, y.size)
        if not (row.size == col.size == y.size == day.size):
            raise SeasonalError("row, col, y and day must be the same length")
        if not y.size:
            return

        design = self.basis.design(day)
        np.add.at(self.n, (row, col), 1)
        np.add.at(self.sum_y, (row, col), y)
        np.add.at(self.sum_yy, (row, col), y * y)
        np.add.at(self.sum_d, (row, col), day)
        np.add.at(self.sum_dd, (row, col), day * day)
        for k in range(self.basis.n_terms):
            np.add.at(self.sum_x[k], (row, col), design[:, k])
            np.add.at(self.sum_yx[k], (row, col), y * design[:, k])
            for l in range(k, self.basis.n_terms):
                product = design[:, k] * design[:, l]
                np.add.at(self.sum_xx[k, l], (row, col), product)
                if l != k:
                    np.add.at(self.sum_xx[l, k], (row, col), product)

    # -- reporting ------------------------------------------------------

    @property
    def covered(self) -> np.ndarray:
        return self.n > 0

    def date_mean(self) -> np.ndarray:
        """Mean day of year per cell, NaN where nothing was observed."""
        out = np.full(self.shape, np.nan)
        ok = self.covered
        out[ok] = self.sum_d[ok] / self.n[ok]
        return out

    def truncated(self, harmonics: int) -> "HarmonicStats":
        """The same statistics restricted to the first ``harmonics`` harmonics.

        The basis is ordered sin1, cos1, sin2, cos2, so a lower-order fit uses
        the leading block of every accumulated array and needs no second pass.
        One accumulation therefore answers the question of whether the second
        harmonic is worth having, by fitting both and comparing them on exactly
        the same soundings.
        """
        if harmonics > self.basis.harmonics:
            raise SeasonalError(
                f"cannot fit {harmonics} harmonics from statistics accumulated "
                f"for {self.basis.harmonics}")
        t = 2 * harmonics
        return HarmonicStats(
            self.shape, HarmonicBasis(harmonics, self.basis.period),
            n=self.n, sum_y=self.sum_y, sum_yy=self.sum_yy,
            sum_d=self.sum_d, sum_dd=self.sum_dd,
            sum_x=self.sum_x[:t], sum_xx=self.sum_xx[:t, :t],
            sum_yx=self.sum_yx[:t])

    def date_spread(self) -> np.ndarray:
        """Population standard deviation of day of year per cell.

        The separability diagnostic. A cell with a spread of zero was sampled on
        one date and its offset cannot be told from the seasonal term; a cell
        spanning most of the year constrains its offset well.
        """
        out = np.full(self.shape, np.nan)
        ok = self.covered
        mean = self.sum_d[ok] / self.n[ok]
        variance = self.sum_dd[ok] / self.n[ok] - mean * mean
        out[ok] = np.sqrt(np.maximum(variance, 0.0))
        return out


@dataclass(frozen=True)
class SeasonalFit:
    """The fitted cycle, the deseasonalised field, and what it rests on."""

    basis: HarmonicBasis
    coefficients: np.ndarray
    mu: np.ndarray
    counts: np.ndarray
    residual_sd: float
    residual_ss: float
    total_ss: float
    n_soundings: int
    n_cells: int
    degrees_of_freedom: int
    poorly_identified: np.ndarray
    condition_number: float = float("nan")

    @property
    def terms(self) -> dict[str, float]:
        return dict(zip(self.basis.labels,
                        (float(c) for c in self.coefficients)))

    @property
    def amplitudes(self) -> list[float]:
        """Amplitude of each harmonic, in ppb."""
        return [float(np.hypot(self.coefficients[2 * k], self.coefficients[2 * k + 1]))
                for k in range(self.basis.harmonics)]

    @property
    def phases(self) -> list[float]:
        """Phase of each harmonic in radians, as ``A sin(theta + phi)``."""
        return [float(np.arctan2(self.coefficients[2 * k + 1],
                                 self.coefficients[2 * k]))
                for k in range(self.basis.harmonics)]

    def curve(self, day) -> np.ndarray:
        return self.basis.evaluate(day, self.coefficients)

    @property
    def peak_day(self) -> float:
        """Day of year at which the fitted cycle is largest.

        Found numerically rather than in closed form: with more than one
        harmonic the maximum of the sum is not the maximum of either term.
        """
        grid = np.linspace(0.0, self.basis.period, 20000, endpoint=False)
        return float(grid[int(np.argmax(self.curve(grid)))])

    @property
    def trough_day(self) -> float:
        grid = np.linspace(0.0, self.basis.period, 20000, endpoint=False)
        return float(grid[int(np.argmin(self.curve(grid)))])

    @property
    def peak_to_trough(self) -> float:
        """Full seasonal range in ppb, which is twice the amplitude only for K=1."""
        grid = np.linspace(0.0, self.basis.period, 20000, endpoint=False)
        values = self.curve(grid)
        return float(values.max() - values.min())

    @property
    def variance_explained(self) -> float:
        """Share of the within-cell variance the cycle accounts for."""
        if self.total_ss <= 0:
            return float("nan")
        return float(1.0 - self.residual_ss / self.total_ss)


def _within(stats: HarmonicStats):
    """Within-cell centred cross products, summed over cells.

    This is the whole derivation in six lines: every term is a sum of
    per-cell sufficient statistics minus a product of two of them over the
    cell count, which is what centring within a cell reduces to.
    """
    t = stats.basis.n_terms
    ok = stats.covered
    n = stats.n[ok].astype("float64")
    sy = stats.sum_y[ok]
    sx = np.stack([stats.sum_x[k][ok] for k in range(t)])

    A = np.empty((t, t), dtype="float64")
    for k in range(t):
        for l in range(t):
            A[k, l] = np.sum(stats.sum_xx[k, l][ok] - sx[k] * sx[l] / n)
    r = np.array([np.sum(stats.sum_yx[k][ok] - sy * sx[k] / n) for k in range(t)])
    total = float(np.sum(stats.sum_yy[ok] - sy * sy / n))
    return A, r, total


def solve(stats: HarmonicStats, *, spread_threshold: float = 1.0) -> SeasonalFit:
    """Fit the shared cycle and return the deseasonalised cell offsets.

    ``spread_threshold`` is in days and only affects the ``poorly_identified``
    flag; it changes no number. Cells whose sampling dates are clustered inside
    it have offsets that are barely distinguishable from the seasonal term.
    """
    A, r, total_ss = _within(stats)
    n_soundings = int(stats.n.sum())
    if not np.isfinite(A).all():
        raise NotEnoughSeasonalSpread("the within-cell design is not finite")

    # The identifiability test has to be absolute, not relative. Every entry of
    # A is a sum over soundings of products of terms bounded by 1, so A scales
    # with the number of soundings. When every sounding shares a date the
    # within-cell deviations are exactly zero and A is a matrix of rounding
    # noise around 1e-17; numpy.linalg.matrix_rank would call that full rank,
    # because its tolerance is relative to the matrix's own largest singular
    # value, and the solve would return a cycle fitted to floating-point dust.
    singular = np.linalg.svd(A, compute_uv=False)
    floor = 1e-6 * max(n_soundings, 1)
    if singular.min() <= floor:
        raise NotEnoughSeasonalSpread(
            f"the within-cell design is rank deficient: smallest singular value "
            f"{singular.min():.3g} against a floor of {floor:.3g} for "
            f"{n_soundings} soundings. No cell was sampled on enough distinct "
            f"dates to separate the seasonal terms from the per-cell offsets; a "
            f"composite of one day cannot be deseasonalised.")
    coefficients = np.linalg.solve(A, r)

    ok = stats.covered
    n = stats.n[ok].astype("float64")
    offsets = stats.sum_y[ok].copy()
    for k in range(stats.basis.n_terms):
        offsets -= coefficients[k] * stats.sum_x[k][ok]
    mu = np.full(stats.shape, np.nan)
    mu[ok] = offsets / n

    residual_ss = float(total_ss - coefficients @ r)
    n_cells = int(ok.sum())
    df = n_soundings - n_cells - stats.basis.n_terms
    residual_sd = float(np.sqrt(residual_ss / df)) if df > 0 else float("nan")

    spread = stats.date_spread()
    poorly = np.zeros(stats.shape, dtype=bool)
    poorly[ok] = spread[ok] < spread_threshold

    return SeasonalFit(
        basis=stats.basis, coefficients=coefficients, mu=mu,
        counts=stats.n.copy(), residual_sd=residual_sd,
        residual_ss=residual_ss, total_ss=total_ss,
        n_soundings=n_soundings, n_cells=n_cells, degrees_of_freedom=df,
        poorly_identified=poorly,
        condition_number=float(singular.max() / singular.min()))
