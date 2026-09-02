"""Binning Level 2 methane soundings onto a regular grid.

Three decisions here were forced by measurement rather than taste.

**Nothing is auto-masked.** netCDF4 will apply ``_FillValue`` and
``scale_factor`` on read if asked to, and this module asks it not to, reading
both attributes itself. That is deliberate: ``notes/decisions.md`` records that
h5py applies no fill masking at all while xarray does, so code that leaves the
behaviour to the library gets a different answer depending on which library it
happens to be using. Reading the attributes explicitly makes the treatment the
same however the file is opened, and makes it testable.

**The quality threshold is applied in stored units.** ``qa_value`` is stored as
``uint8`` with ``scale_factor`` 0.01, so a threshold of 0.75 is a stored 75. A
float comparison against the raw array would keep everything, since every
stored value from 0 to 100 exceeds 0.75. The conversion happens once, here, and
a test pins it.

**A cell with no soundings is not a cell with zero methane.** Empty cells come
back as NaN in the mean grid and 0 in the count grid, and the two must be read
together. Over this study area most cells are empty in any single granule: the
median covered cell at 0.25 degree received 6 soundings pooled over 36
granules, and 44 percent of cells received none at all.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np

#: The two methane variables. Both are carried through separately so the effect
#: of the bias correction is visible rather than chosen silently; over the 36
#: granules sampled they selected identical soundings and differed only in
#: value.
PRIMARY = "methane_mixing_ratio_bias_corrected"
SECONDARY = "methane_mixing_ratio"


class MethaneError(RuntimeError):
    """Base class for failures this package raises deliberately."""


class MissingVariable(MethaneError):
    """A granule lacks a variable the gridding needs."""


@dataclass(frozen=True)
class GridSpec:
    """A regular lat/lon grid, north-up, defined by its bounds and resolution."""

    west: float
    south: float
    east: float
    north: float
    resolution: float

    @property
    def n_cols(self) -> int:
        return int(round((self.east - self.west) / self.resolution))

    @property
    def n_rows(self) -> int:
        return int(round((self.north - self.south) / self.resolution))

    @property
    def shape(self) -> tuple[int, int]:
        return (self.n_rows, self.n_cols)

    @property
    def n_cells(self) -> int:
        return self.n_rows * self.n_cols

    def cell_of(self, lat, lon):
        """Row and column indices for each sounding, and an in-box mask.

        Row 0 is the northernmost. Soundings outside the box are flagged rather
        than clipped, so nothing lands in an edge cell it does not belong to.
        """
        lat = np.asarray(lat, dtype="float64")
        lon = np.asarray(lon, dtype="float64")
        inside = ((lat >= self.south) & (lat < self.north)
                  & (lon >= self.west) & (lon < self.east))
        row = np.clip(
            np.floor((self.north - lat) / self.resolution).astype("int64"),
            0, self.n_rows - 1)
        col = np.clip(
            np.floor((lon - self.west) / self.resolution).astype("int64"),
            0, self.n_cols - 1)
        return np.atleast_1d(row), np.atleast_1d(col), np.atleast_1d(inside)


@dataclass(frozen=True)
class Soundings:
    """Valid soundings from one granule, already filtered."""

    granule: str
    acquired: datetime | None
    latitude: np.ndarray
    longitude: np.ndarray
    values: Mapping[str, np.ndarray]
    qa_stored: np.ndarray

    def __len__(self) -> int:
        return int(self.latitude.size)


@dataclass(frozen=True)
class GranuleContribution:
    """What one granule gave to a composite."""

    granule: str
    acquired: datetime | None
    soundings_read: int
    soundings_valid: int
    soundings_in_box: int

    @property
    def year(self) -> int | None:
        return self.acquired.year if self.acquired else None

    def as_dict(self) -> dict:
        return {
            "granule": self.granule,
            "acquired": self.acquired.isoformat() if self.acquired else None,
            "year": self.year,
            "soundings_read": self.soundings_read,
            "soundings_valid": self.soundings_valid,
            "soundings_in_box": self.soundings_in_box,
        }


@dataclass(frozen=True)
class Coverage:
    """How much of the grid a composite actually observed."""

    n_cells: int
    covered_cells: int
    median_per_covered_cell: float
    max_per_covered_cell: int
    soundings_by_year: Mapping[int, int]
    contributing_granules: int
    empty_granules: int

    @property
    def fraction(self) -> float:
        return self.covered_cells / self.n_cells if self.n_cells else 0.0

    def as_dict(self) -> dict:
        return {
            "n_cells": self.n_cells,
            "covered_cells": self.covered_cells,
            "fraction": self.fraction,
            "median_per_covered_cell": self.median_per_covered_cell,
            "max_per_covered_cell": self.max_per_covered_cell,
            "soundings_by_year": dict(self.soundings_by_year),
            "contributing_granules": self.contributing_granules,
            "empty_granules": self.empty_granules,
        }


@dataclass(frozen=True)
class Composite:
    """Gridded methane and the counts it rests on.

    ``mean`` is not reachable without ``count``: both come from the same object
    and :meth:`mean_of` returns NaN wherever the count is zero. An empty cell is
    an absence of observation, not a methane value of zero, and the two must
    never collapse into each other.
    """

    spec: GridSpec
    qa_threshold: float
    counts: np.ndarray
    sums: Mapping[str, np.ndarray]
    contributions: Sequence[GranuleContribution] = field(default_factory=tuple)

    @property
    def variables(self) -> list[str]:
        return sorted(self.sums)

    def mean_of(self, variable: str) -> np.ndarray:
        """Mean value per cell, NaN where no sounding fell."""
        if variable not in self.sums:
            raise KeyError(f"{variable!r} not in this composite; have {self.variables}")
        out = np.full(self.spec.shape, np.nan, dtype="float64")
        covered = self.counts > 0
        out[covered] = self.sums[variable][covered] / self.counts[covered]
        return out

    def grids(self, variable: str) -> tuple[np.ndarray, np.ndarray]:
        """``(mean, count)``. The pair is the unit of use, not the mean alone."""
        return self.mean_of(variable), self.counts.copy()

    @property
    def total_soundings(self) -> int:
        return int(self.counts.sum())


def _read_variable(group, name: str):
    """Read one variable without auto-masking, with its own fill and scale."""
    if name not in group.variables:
        raise MissingVariable(f"PRODUCT has no variable {name!r}")
    var = group.variables[name]
    try:
        var.set_auto_maskandscale(False)
    except AttributeError:
        pass
    # Flatten to one entry per sounding. The product shape is
    # (time, scanline, ground_pixel); squeezing instead collapses a
    # single-sounding granule to a 0-d array, which then breaks indexing.
    raw = np.asarray(var[:]).reshape(-1)
    attrs = {k: var.getncattr(k) for k in var.ncattrs()}
    fill = attrs.get("_FillValue")
    if isinstance(fill, np.ndarray):
        fill = fill.item() if fill.size == 1 else fill[0]
    scale = attrs.get("scale_factor")
    if isinstance(scale, np.ndarray):
        scale = scale.item() if scale.size == 1 else scale[0]
    offset = attrs.get("add_offset")
    if isinstance(offset, np.ndarray):
        offset = offset.item() if offset.size == 1 else offset[0]
    return raw, fill, scale, offset


def stored_threshold(threshold: float, scale_factor: float | None,
                     add_offset: float | None = None) -> float:
    """Convert a threshold in physical units to the units actually stored.

    ``qa_value`` is uint8 with ``scale_factor`` 0.01, so 0.75 is a stored 75.
    Comparing 0.75 against the raw array would keep every sounding, since the
    smallest non-zero stored value is 1.
    """
    if not scale_factor:
        return threshold
    return (threshold - (add_offset or 0.0)) / scale_factor


def read_soundings(
    path: str | Path,
    spec: GridSpec,
    *,
    qa_threshold: float = 0.75,
    variables: Sequence[str] = (PRIMARY, SECONDARY),
    group_name: str = "PRODUCT",
) -> tuple[Soundings, GranuleContribution]:
    """Read one granule and return the soundings that survive filtering.

    Filtering is, in order: drop the fill value of each variable read from that
    variable's own ``_FillValue``; drop soundings whose ``qa_value`` is the qa
    fill; drop those below the quality threshold, compared in stored units; and
    finally restrict to the grid's bounding box.
    """
    import netCDF4

    path = Path(path)
    with netCDF4.Dataset(path, "r") as dataset:
        group = dataset.groups.get(group_name)
        if group is None:
            raise MissingVariable(f"{path.name}: no {group_name!r} group")

        lat, lat_fill, _, _ = _read_variable(group, "latitude")
        lon, lon_fill, _, _ = _read_variable(group, "longitude")
        qa_raw, qa_fill, qa_scale, qa_offset = _read_variable(group, "qa_value")

        read_values = {}
        good = np.ones(lat.shape, dtype=bool)
        for name in variables:
            raw, fill, scale, offset = _read_variable(group, name)
            value = raw.astype("float64")
            if scale:
                value = value * scale
            if offset:
                value = value + offset
            if fill is not None:
                good &= raw != fill
            good &= np.isfinite(value)
            read_values[name] = value

        total = int(lat.size)

        if lat_fill is not None:
            good &= lat != lat_fill
        if lon_fill is not None:
            good &= lon != lon_fill
        if qa_fill is not None:
            good &= qa_raw != qa_fill

        cutoff = stored_threshold(qa_threshold, qa_scale, qa_offset)
        good &= qa_raw >= cutoff
        valid = int(good.sum())

        row, col, inside = spec.cell_of(lat, lon)
        keep = good & inside

        acquired = _acquired_from(dataset, path)
        soundings = Soundings(
            granule=path.name,
            acquired=acquired,
            latitude=np.asarray(lat)[keep].astype("float64"),
            longitude=np.asarray(lon)[keep].astype("float64"),
            values={k: v[keep] for k, v in read_values.items()},
            qa_stored=np.asarray(qa_raw)[keep],
        )
    contribution = GranuleContribution(
        granule=path.name, acquired=acquired, soundings_read=total,
        soundings_valid=valid, soundings_in_box=len(soundings),
    )
    return soundings, contribution


def _acquired_from(dataset, path: Path) -> datetime | None:
    """Acquisition time, from the filename if the attributes do not give one."""
    from src.fetch.s5p import parse_granule_name

    fields = parse_granule_name(path.name)
    if fields:
        return fields["start"]
    for attr in ("time_coverage_start", "time_reference"):
        if attr in dataset.ncattrs():
            try:
                return datetime.fromisoformat(
                    str(dataset.getncattr(attr)).replace("Z", "+00:00")).replace(
                        tzinfo=None)
            except ValueError:
                continue
    return None


def grid_granules(
    paths: Iterable[str | Path],
    spec: GridSpec,
    *,
    qa_threshold: float = 0.75,
    variables: Sequence[str] = (PRIMARY, SECONDARY),
) -> Composite:
    """Bin every granule onto the grid, averaging where cells receive several.

    Returns a :class:`Composite`, which carries the counts alongside the sums
    and records what each granule contributed.
    """
    counts = np.zeros(spec.shape, dtype="int64")
    sums = {name: np.zeros(spec.shape, dtype="float64") for name in variables}
    contributions: list[GranuleContribution] = []

    for path in paths:
        soundings, contribution = read_soundings(
            path, spec, qa_threshold=qa_threshold, variables=variables)
        contributions.append(contribution)
        if not len(soundings):
            continue
        row, col, _ = spec.cell_of(soundings.latitude, soundings.longitude)
        np.add.at(counts, (row, col), 1)
        for name in variables:
            np.add.at(sums[name], (row, col), soundings.values[name])

    return Composite(spec=spec, qa_threshold=qa_threshold, counts=counts,
                     sums=sums, contributions=tuple(contributions))


def coverage_of(composite: Composite) -> Coverage:
    """Report what a composite actually observed.

    The per-year breakdown is not optional. Annual yield over this study area
    ranged from 2,533 valid soundings in 2023 to 4 in 2020, so a composite that
    pools years without saying what each gave is reporting cloud cover as
    though it were signal.
    """
    counts = composite.counts
    covered = counts[counts > 0]
    by_year: dict[int, int] = {}
    for contribution in composite.contributions:
        if contribution.year is None:
            continue
        by_year[contribution.year] = (
            by_year.get(contribution.year, 0) + contribution.soundings_in_box)
    return Coverage(
        n_cells=composite.spec.n_cells,
        covered_cells=int((counts > 0).sum()),
        median_per_covered_cell=float(np.median(covered)) if covered.size else 0.0,
        max_per_covered_cell=int(covered.max()) if covered.size else 0,
        soundings_by_year=dict(sorted(by_year.items())),
        contributing_granules=sum(
            1 for c in composite.contributions if c.soundings_in_box > 0),
        empty_granules=sum(
            1 for c in composite.contributions if c.soundings_in_box == 0),
    )
