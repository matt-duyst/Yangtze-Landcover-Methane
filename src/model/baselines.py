"""Constant, linear and spatial baselines over the analysis grid.

Five decisions here are choices rather than arithmetic, and each is stated at
the point it is made because each could reasonably have gone the other way.

**Weights are sounding counts.** A cell's methane value is the mean of between
1 and 410 soundings, so its variance is roughly sigma squared over n and the
inverse-variance weight is n itself. Fitting unweighted treats a cell built from
one sounding as evidence equal to a cell built from 410, which it is not. Every
result is reported both ways rather than one being chosen silently, because
weighting is not free: sounding count is not random over the study area, and the
well-observed cells are systematically the flat bright ones the instrument
retrieves from, so weighting also tilts the fit towards that terrain.

**Evaluation is spatial, never random.** Cells are contiguous and neighbouring
cells are not independent, so a random split puts a cell's own neighbours in the
training set and every model scores well by memorising the field. Both schemes
here hold out connected regions instead.

**R squared is measured against the evaluation set's own weighted mean.** That
is the usual convention and it is a harsh one out of sample: a model that
predicts the training mean is scored against the held-out mean, so a constant
model can and does score below zero when the held-out region sits away from the
overall mean. Below zero is informative here rather than a defect, since it says
the fold is genuinely elsewhere.

**Held-out metrics are pooled, not averaged over folds.** Every held-out
prediction from every fold is collected and scored once. Averaging fold metrics
would weight a fold of 40 cells equally with a fold of 400.

**Missing predictors are dropped or raised on, never imputed.** 395 of the 927
rows have no rice fraction because no rice raster reached them, which is an
absence of observation and not a value of zero. Imputing zero would assert that
those cells have no rice, which is exactly the claim the table is built to
avoid making. Every result therefore carries the sample size it was computed on
and results on different samples must not be compared without saying so.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np


class ModelError(RuntimeError):
    """Base class for failures this package raises deliberately."""


class MissingPredictor(ModelError):
    """A model was asked to fit rows where one of its predictors is absent."""


class DegenerateFold(ModelError):
    """A cross-validation fold left nothing to train on or nothing to test."""


#: Cells with no share of any study province. They are inside the bounding box
#: but outside all four, mostly sea and mostly the neighbouring provinces, and
#: they are kept as their own group rather than dropped: 368 of 927 rows is too
#: much of the field to discard for tidiness, and dropping them would quietly
#: restrict every metric to the provinces.
OUTSIDE = "Outside"

TARGET = "ch4_bias_corrected_ppb"
WEIGHT = "sounding_count"
PROVINCE_COLUMNS = ("share_anhui", "share_jiangsu", "share_shanghai",
                    "share_zhejiang")


# --------------------------------------------------------------------------
# metrics
# --------------------------------------------------------------------------

def weighted_mean(values: np.ndarray, weight: np.ndarray) -> float:
    total = float(np.sum(weight))
    if total <= 0:
        raise ModelError("weights sum to zero, so no mean is defined")
    return float(np.sum(weight * values) / total)


def rmse(actual: np.ndarray, predicted: np.ndarray, weight: np.ndarray) -> float:
    """Root mean squared error in the units of the target, here ppb."""
    total = float(np.sum(weight))
    if total <= 0:
        raise ModelError("weights sum to zero, so no error is defined")
    error = np.asarray(actual, "float64") - np.asarray(predicted, "float64")
    return float(np.sqrt(np.sum(weight * error * error) / total))


def r2(actual: np.ndarray, predicted: np.ndarray, weight: np.ndarray) -> float:
    """Share of variance explained, against this set's own weighted mean.

    Returns NaN when the target has no variance to explain, rather than
    dividing by zero and reporting an infinity as a result.
    """
    actual = np.asarray(actual, "float64")
    centre = weighted_mean(actual, weight)
    residual = np.sum(weight * (actual - np.asarray(predicted, "float64")) ** 2)
    total = np.sum(weight * (actual - centre) ** 2)
    if total <= 0:
        return float("nan")
    return float(1.0 - residual / total)


@dataclass(frozen=True)
class Metrics:
    """A fit's error and explained variance on one set of rows."""

    n: int
    rmse: float
    r2: float

    @classmethod
    def of(cls, actual, predicted, weight) -> "Metrics":
        return cls(n=int(np.size(actual)),
                   rmse=rmse(actual, predicted, weight),
                   r2=r2(actual, predicted, weight))


# --------------------------------------------------------------------------
# the table
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Table:
    """The analysis grid as arrays, with lattice positions for the spatial work.

    ``columns`` may hold NaN. Nothing in this module fills one in; a model that
    needs a column either runs on the rows that have it or refuses.
    """

    y: np.ndarray
    weight: np.ndarray
    row: np.ndarray
    col: np.ndarray
    province: np.ndarray
    columns: Mapping[str, np.ndarray]

    @property
    def n(self) -> int:
        return int(self.y.size)

    @property
    def all_rows(self) -> np.ndarray:
        return np.arange(self.n)

    def complete(self, names: Sequence[str]) -> np.ndarray:
        """Rows where every named column is present."""
        keep = np.ones(self.n, dtype=bool)
        for name in names:
            if name not in self.columns:
                raise ModelError(f"no column named {name!r}")
            keep &= np.isfinite(self.columns[name])
        return keep

    def design(self, names: Sequence[str], index: np.ndarray,
               *, interaction: bool = False) -> np.ndarray:
        """Design matrix with an intercept, for the given rows."""
        parts = [np.ones(index.size)]
        parts.extend(self.columns[name][index] for name in names)
        if interaction:
            product = np.ones(index.size)
            for name in names:
                product = product * self.columns[name][index]
            parts.append(product)
        return np.column_stack(parts)


def dominant_province(shares: Mapping[str, float]) -> str:
    """The province holding most of a cell, or OUTSIDE when none does.

    A cell at 0.25 degrees is about 25 km across and 69 of them straddle a
    boundary, so a single label is a simplification. It is the right one for
    grouping: a fold has to be a set of whole cells, and splitting a cell's
    weight across two folds would put part of it in training and part in test.
    """
    best, share = OUTSIDE, 0.0
    for name, value in shares.items():
        if value > share:
            best, share = name, value
    return best


#: Covariates carried through from the composite, and the derived wind terms.
#:
#: Wind speed is ``hypot(eastward, northward)``. Direction is deliberately NOT
#: entered as a scalar bearing: a bearing is circular, so 359 and 1 degrees are
#: adjacent in the world and 358 apart in the arithmetic, and a linear
#: coefficient on it is meaningless. Direction enters through the components
#: instead. A linear model in ``wind_u`` and ``wind_v`` is exactly a linear
#: model in speed and direction jointly, expressed in coordinates where the
#: discontinuity does not exist, and ``wind_speed`` is added alongside because
#: it is a nonlinear function of the pair and so is not collinear with them.
WIND_COMPONENTS = ("eastward_wind", "northward_wind")
DERIVED_WIND = ("wind_u", "wind_v", "wind_speed")


def join_covariates(columns: dict, records, lat, lon, resolution: float) -> list[str]:
    """Add composite covariate means to a table's columns, matched by cell.

    Matching is on the cell centre printed to four decimal places, which is how
    both files write it, so the join is exact rather than a tolerance. A grid
    cell with no covariate row gets NaN, never zero: a covariate nobody measured
    is not a covariate of zero, and every model in this module drops or refuses
    on a NaN rather than filling it.
    """
    def key(a, b):
        return (f"{a:.4f}", f"{b:.4f}")

    by_cell = {key(float(r["centre_lat"]), float(r["centre_lon"])): r
               for r in records}
    names = sorted({name[: -len("_mean")] for name in records[0]
                    if name.endswith("_mean")})
    added = []
    for name in names:
        values = np.full(lat.size, np.nan)
        counts = np.zeros(lat.size)
        for i in range(lat.size):
            record = by_cell.get(key(lat[i], lon[i]))
            if record is None:
                continue
            raw = record.get(f"{name}_mean", "")
            if raw != "":
                values[i] = float(raw)
            counts[i] = float(record.get(f"{name}_count", 0) or 0)
        columns[name] = values
        columns[f"{name}_count"] = counts
        added.append(name)

    # Solar zenith angle at a fixed latitude is fixed by the date and time of the
    # overpass, so once latitude is removed what is left is a measure of WHEN
    # each cell was sampled. Over this composite latitude explains only 2.4
    # percent of the variance in mean solar zenith angle, so almost all of it is
    # sampling composition. That is available as a predictor in its own right,
    # and it is the control that matters most: an annual mean built from
    # different days in different cells can be predicted by anything that also
    # tracks the calendar, with no physics involved.
    if "solar_zenith_angle" in columns and "centre_lat" in columns:
        sza, lat = columns["solar_zenith_angle"], columns["centre_lat"]
        usable = np.isfinite(sza) & np.isfinite(lat)
        residual = np.full(sza.shape, np.nan)
        if usable.sum() > 2:
            design = np.column_stack([np.ones(int(usable.sum())), lat[usable]])
            coefficients, *_ = np.linalg.lstsq(design, sza[usable], rcond=None)
            residual[usable] = sza[usable] - design @ coefficients
        columns["sampling_season"] = residual
        added.append("sampling_season")

    if all(name in columns for name in WIND_COMPONENTS):
        u, v = columns["eastward_wind"], columns["northward_wind"]
        columns["wind_u"] = u
        columns["wind_v"] = v
        columns["wind_speed"] = np.hypot(u, v)
        added.extend(DERIVED_WIND)
    return added


def load_table(path: str | Path, *, target: str = TARGET,
               resolution: float = 0.25,
               covariates: str | Path | None = None) -> Table:
    """Read analysis_grid_2018.csv into arrays.

    Lattice row and column are recovered from the cell centres rather than
    stored, so the file stays readable as a table of places. The recovery is
    exact for a regular grid and is checked: a centre that does not land on the
    lattice is an error rather than something to round away.
    """
    records = list(csv.DictReader(open(path, newline="")))
    if not records:
        raise ModelError(f"{path} holds no rows")

    def numeric(name):
        return np.array([float(r[name]) if r[name] != "" else np.nan
                         for r in records], dtype="float64")

    lat, lon = numeric("centre_lat"), numeric("centre_lon")
    north, west = lat.max() + resolution / 2, lon.min() - resolution / 2
    raw_row = (north - lat) / resolution - 0.5
    raw_col = (lon - west) / resolution - 0.5
    if not (np.allclose(raw_row, np.round(raw_row), atol=1e-6)
            and np.allclose(raw_col, np.round(raw_col), atol=1e-6)):
        raise ModelError("cell centres do not lie on a regular lattice")

    provinces = []
    for record in records:
        shares = {name[len("share_"):].capitalize(): float(record[name])
                  for name in PROVINCE_COLUMNS
                  if record.get(name) not in (None, "")}
        provinces.append(dominant_province(shares))

    predictors = ("impervious_fraction", "rice_fraction_single",
                  "rice_fraction_combined", "impervious_coverage",
                  "rice_coverage")
    columns = {name: numeric(name) for name in predictors}
    # Position, always available, so a trend surface can be fitted as a control.
    # A smooth field can be reproduced by any smooth function of position, and a
    # covariate that beats the spatial null but not a trend surface has only
    # rediscovered where the cell is.
    columns["centre_lat"] = lat
    columns["centre_lon"] = lon
    if covariates is not None:
        joined = list(csv.DictReader(open(covariates, newline="")))
        if not joined:
            raise ModelError(f"{covariates} holds no rows")
        join_covariates(columns, joined, lat, lon, resolution)
    return Table(
        y=numeric(target),
        weight=numeric(WEIGHT),
        row=np.round(raw_row).astype("int64"),
        col=np.round(raw_col).astype("int64"),
        province=np.array(provinces, dtype=object),
        columns=columns)


# --------------------------------------------------------------------------
# fitted models
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class ConstantFit:
    """One value everywhere, or one value per group with a fallback.

    ``fallback`` is what a group absent from the training rows gets. Under
    leave-one-province-out that is every test row, by construction: the held-out
    province is precisely the group with no training data. The per-province
    constant therefore degenerates to the global constant under that scheme, and
    the identical numbers in the results table are that fact and not a bug.
    """

    fallback: float
    by_group: Mapping[str, float] = field(default_factory=dict)

    def predict(self, table: Table, index: np.ndarray) -> np.ndarray:
        if not self.by_group:
            return np.full(index.size, self.fallback)
        return np.array([self.by_group.get(table.province[i], self.fallback)
                         for i in index])


@dataclass(frozen=True)
class LinearFit:
    """Ordinary or weighted least squares, with the coefficients kept."""

    names: tuple[str, ...]
    coefficients: np.ndarray
    interaction: bool

    @property
    def terms(self) -> dict[str, float]:
        labels = ["intercept", *self.names]
        if self.interaction:
            labels.append(" x ".join(self.names))
        return dict(zip(labels, (float(c) for c in self.coefficients)))

    def predict(self, table: Table, index: np.ndarray) -> np.ndarray:
        matrix = table.design(self.names, index, interaction=self.interaction)
        return matrix @ self.coefficients


@dataclass(frozen=True)
class NeighbourFit:
    """Each cell predicted from the training cells adjacent to it."""

    values: Mapping[tuple[int, int], float]
    weights: Mapping[tuple[int, int], float]
    fallback: float
    offsets: tuple[tuple[int, int], ...]

    def predict(self, table: Table, index: np.ndarray) -> np.ndarray:
        out = np.empty(index.size)
        for position, i in enumerate(index):
            here = (int(table.row[i]), int(table.col[i]))
            total = weight_total = 0.0
            for dr, dc in self.offsets:
                key = (here[0] + dr, here[1] + dc)
                if key in self.values:
                    w = self.weights[key]
                    total += w * self.values[key]
                    weight_total += w
            out[position] = total / weight_total if weight_total > 0 else self.fallback
        return out

    def fallbacks_for(self, table: Table, index: np.ndarray) -> int:
        """How many cells had no training neighbour and took the fallback."""
        count = 0
        for i in index:
            here = (int(table.row[i]), int(table.col[i]))
            if not any((here[0] + dr, here[1] + dc) in self.values
                       for dr, dc in self.offsets):
                count += 1
        return count


# --------------------------------------------------------------------------
# models
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class GlobalMean:
    """One number for the whole field: the variance of the target, restated."""

    name: str = "constant (global mean)"
    requires: tuple[str, ...] = ()

    def fit(self, table: Table, train: np.ndarray, weight: np.ndarray) -> ConstantFit:
        return ConstantFit(fallback=weighted_mean(table.y[train], weight))


@dataclass(frozen=True)
class ProvinceMean:
    """One number per province, from a boundary file and nothing else.

    A stronger and more honest null than the global mean, because provincial
    identity is available for free and any model that cannot beat it has not
    used the imagery for anything a map could not have told you.
    """

    name: str = "constant (per province)"
    requires: tuple[str, ...] = ()

    def fit(self, table: Table, train: np.ndarray, weight: np.ndarray) -> ConstantFit:
        groups: dict[str, float] = {}
        for label in set(table.province[train]):
            rows = train[table.province[train] == label]
            mask = table.province[train] == label
            groups[label] = weighted_mean(table.y[rows], weight[mask])
        return ConstantFit(fallback=weighted_mean(table.y[train], weight),
                           by_group=groups)


@dataclass(frozen=True)
class LinearModel:
    """Least squares on the named fractions, optionally with their product."""

    names: tuple[str, ...]
    interaction: bool = False
    label: str | None = None

    @property
    def name(self) -> str:
        if self.label:
            return self.label
        joined = " + ".join(self.names)
        return f"OLS {joined}{' + interaction' if self.interaction else ''}"

    @property
    def requires(self) -> tuple[str, ...]:
        return self.names

    def fit(self, table: Table, train: np.ndarray, weight: np.ndarray) -> LinearFit:
        matrix = table.design(self.names, train, interaction=self.interaction)
        if not np.isfinite(matrix).all():
            raise MissingPredictor(
                f"{self.name} was given rows with an absent predictor. Rows "
                f"without a predictor are dropped or refused, never imputed: a "
                f"cell no raster reached has no fraction, which is not zero.")
        root = np.sqrt(weight)
        coefficients, *_ = np.linalg.lstsq(matrix * root[:, None],
                                           table.y[train] * root, rcond=None)
        return LinearFit(names=self.names, coefficients=coefficients,
                         interaction=self.interaction)


#: The eight cells sharing an edge or a corner. At 0.25 degrees a cell is about
#: 25 km across, which is the scale transport smooths over; a wider stencil
#: would start to encode the regional mean rather than local smoothness, and
#: would make the null harder to beat for a reason that has nothing to do with
#: land cover.
QUEEN = tuple((dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
              if (dr, dc) != (0, 0))


@dataclass(frozen=True)
class NeighbourMean:
    """Predict each cell from the mean of its neighbours, excluding itself.

    The bar that matters. The field is spatially autocorrelated by transport,
    so a great deal of it is predictable from position alone, and a model that
    beats only the constants may have learned nothing except that methane is
    smooth. Self is excluded or it is not a prediction. Neighbours are taken
    from the training rows only, so under a held-out scheme a test cell is
    predicted from cells the model was allowed to see, and a cell in the
    interior of a held-out region correctly has nothing to lean on.
    """

    offsets: tuple[tuple[int, int], ...] = QUEEN
    name: str = "spatial null (queen neighbour mean)"
    requires: tuple[str, ...] = ()

    def fit(self, table: Table, train: np.ndarray, weight: np.ndarray) -> NeighbourFit:
        values, weights = {}, {}
        for position, i in enumerate(train):
            key = (int(table.row[i]), int(table.col[i]))
            values[key] = float(table.y[i])
            weights[key] = float(weight[position])
        return NeighbourFit(values=values, weights=weights,
                            fallback=weighted_mean(table.y[train], weight),
                            offsets=self.offsets)


# --------------------------------------------------------------------------
# cross-validation schemes
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Fold:
    name: str
    train: np.ndarray
    test: np.ndarray


def leave_one_province_out(table: Table, index: np.ndarray) -> list[Fold]:
    """Hold out one province at a time, including the cells outside all four.

    The design the 2023 thesis used, and the one that matches the study's
    intent: it asks whether a relationship learned in three provinces transfers
    to a fourth, which is the claim a land-cover model implicitly makes.
    """
    folds = []
    labels = sorted(set(table.province[index]))
    for label in labels:
        held = table.province[index] == label
        test, train = index[held], index[~held]
        if not test.size or not train.size:
            raise DegenerateFold(f"province {label!r} leaves one side empty")
        folds.append(Fold(name=label, train=train, test=test))
    return folds


def spatial_blocks(table: Table, index: np.ndarray, *, block: int = 4,
                   folds: int = 5, seed: int = 0) -> list[Fold]:
    """Hold out square blocks of the lattice, assigned to folds at random.

    Blocks are ``block`` by ``block`` cells, so at 0.25 degrees the default is a
    one-degree square, comfortably wider than the queen stencil the spatial null
    uses. That is the point: a held-out block has an interior whose neighbours
    are also held out, so the spatial null cannot simply read the answer off the
    training set across a one-cell seam. Blocks are assigned to folds by a seeded
    permutation, so each fold is a scatter of blocks across the study area rather
    than one contiguous region, and no fold is entirely coastal or entirely
    inland. The seed is fixed so the split is a property of the code.
    """
    if block < 1 or folds < 2:
        raise ModelError("need a block of at least one cell and at least two folds")
    keys = np.stack([table.row[index] // block, table.col[index] // block], axis=1)
    unique, inverse = np.unique(keys, axis=0, return_inverse=True)
    assignment = np.arange(unique.shape[0]) % folds
    np.random.default_rng(seed).shuffle(assignment)
    fold_of = assignment[inverse]

    out = []
    for k in range(folds):
        held = fold_of == k
        test, train = index[held], index[~held]
        if not test.size or not train.size:
            raise DegenerateFold(f"block fold {k} leaves one side empty")
        out.append(Fold(name=f"block fold {k}", train=train, test=test))
    return out


SCHEMES = {
    "leave-one-province-out": leave_one_province_out,
    "spatial blocks": spatial_blocks,
}


# --------------------------------------------------------------------------
# evaluation
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class BaselineResult:
    model: str
    scheme: str
    weighting: str
    n: int
    dropped: int
    in_sample: Metrics
    held_out: Metrics
    folds: tuple[str, ...] = ()
    detail: str = ""

    def as_dict(self) -> dict:
        return {
            "model": self.model,
            "scheme": self.scheme,
            "weighting": self.weighting,
            "n": self.n,
            "dropped_missing": self.dropped,
            "in_sample_rmse_ppb": round(self.in_sample.rmse, 4),
            "in_sample_r2": round(self.in_sample.r2, 4),
            "held_out_rmse_ppb": round(self.held_out.rmse, 4),
            "held_out_r2": round(self.held_out.r2, 4),
            "detail": self.detail,
        }


def rows_for(table: Table, model, index: np.ndarray | None = None, *,
             on_missing: str = "drop") -> np.ndarray:
    """The rows a model can honestly run on.

    ``on_missing="raise"`` refuses instead of narrowing the sample. Neither
    option fills anything in.
    """
    index = table.all_rows if index is None else index
    if not model.requires:
        return index
    complete = table.complete(model.requires)
    if on_missing == "raise":
        if not complete[index].all():
            raise MissingPredictor(
                f"{model.name} needs {list(model.requires)} and "
                f"{int((~complete[index]).sum())} of {index.size} rows lack one")
        return index
    if on_missing != "drop":
        raise ModelError(f"on_missing must be 'drop' or 'raise', not {on_missing!r}")
    return index[complete[index]]


def evaluate(table: Table, model, *, scheme: str, weighted: bool,
             index: np.ndarray | None = None, on_missing: str = "drop",
             **scheme_kwargs) -> BaselineResult:
    """Fit in sample and under a held-out scheme, and score both.

    The two are reported side by side so the gap is visible. A model whose
    in-sample fit is good and whose held-out fit is not has fitted the study
    area rather than a relationship.
    """
    if scheme not in SCHEMES:
        raise ModelError(f"unknown scheme {scheme!r}")
    requested = table.all_rows if index is None else index
    rows = rows_for(table, model, requested, on_missing=on_missing)
    dropped = int(requested.size - rows.size)
    if rows.size < 3:
        raise ModelError(f"{model.name} has {rows.size} usable rows")

    def weights_for(subset):
        return table.weight[subset] if weighted else np.ones(subset.size)

    fitted = model.fit(table, rows, weights_for(rows))
    in_sample = Metrics.of(table.y[rows], fitted.predict(table, rows),
                           weights_for(rows))

    folds = SCHEMES[scheme](table, rows, **scheme_kwargs)
    actual, predicted, weight = [], [], []
    fallbacks = 0
    for fold in folds:
        fold_fit = model.fit(table, fold.train, weights_for(fold.train))
        prediction = fold_fit.predict(table, fold.test)
        if isinstance(fold_fit, NeighbourFit):
            fallbacks += fold_fit.fallbacks_for(table, fold.test)
        actual.append(table.y[fold.test])
        predicted.append(prediction)
        weight.append(weights_for(fold.test))

    held_out = Metrics.of(np.concatenate(actual), np.concatenate(predicted),
                          np.concatenate(weight))
    detail = ""
    if isinstance(fitted, LinearFit):
        detail = "; ".join(f"{k} {v:+.4f}" for k, v in fitted.terms.items())
    elif fallbacks:
        detail = f"{fallbacks} test cells had no training neighbour"
    elif isinstance(fitted, ConstantFit) and fitted.by_group:
        detail = f"groups: {len(fitted.by_group)}"

    return BaselineResult(
        model=model.name, scheme=scheme,
        weighting="by sounding count" if weighted else "unweighted",
        n=int(rows.size), dropped=dropped,
        in_sample=in_sample, held_out=held_out,
        folds=tuple(f.name for f in folds), detail=detail)
