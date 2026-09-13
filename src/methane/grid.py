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

**Covariates never gate a sounding, and each carries its own count.** The
support-data fields are produced on different subsets of the swath from the
methane retrieval: only 3.4 percent of in-box soundings carry a valid
``surface_albedo_SWIR``, because albedo is written only where the retrieval got
far enough. If a covariate joined the validity mask, adding albedo would throw
away 96.6 percent of the methane record, and the answer to "does land cover
explain methane" would silently become an answer about a different 3 percent of
the field. So the methane variables gate and the covariates do not: a covariate
is read on the soundings methane already selected, masked by its own
``_FillValue``, and accumulated into sums and counts of its own.

That is also how the structural guarantee survives the change. A mean is still
unreachable without the count it rests on, but now for every variable rather
than only for methane: :meth:`Composite.mean_of` looks up that variable's own
count through :meth:`Composite.count_of` and returns NaN wherever it is zero,
and :meth:`Composite.grids` hands back the pair. There is no path to a
covariate mean that does not go through its matching denominator, and a
covariate's denominator is never methane's.
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

#: The two covariates the published preprocessing filters are defined on. Named
#: here so the filter machinery refers to them by constant rather than by a
#: string literal repeated across two modules.
PRECISION = "methane_mixing_ratio_precision"
ALBEDO_SWIR = "surface_albedo_SWIR"


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


#: Group marker for a covariate that is computed rather than read. A spec
#: carrying it is not looked for in the file; `read_soundings` derives it.
DERIVED = "derived"
#: The TM5 a priori column, in ppb, from the profiles inside every granule.
APRIORI = "xch4_apriori"
#: Bias-corrected retrieved minus a priori, in ppb.
DEPARTURE = "xch4_departure"


@dataclass(frozen=True)
class CovariateSpec:
    """One support-data variable and the group it lives in.

    The path is configuration rather than a constant because these fields are
    spread over three different subgroups of PRODUCT: winds and surface
    geometry under SUPPORT_DATA/INPUT_DATA, albedo under
    SUPPORT_DATA/DETAILED_RESULTS, and viewing angles under
    SUPPORT_DATA/GEOLOCATIONS. Assuming one location would find some of them
    and silently miss the rest.
    """

    name: str
    group: str = "PRODUCT"

    @property
    def path(self) -> tuple[str, ...]:
        return tuple(part for part in self.group.split("/") if part)


def open_group(dataset, path: Sequence[str]):
    """Walk a netCDF group path, or raise saying where it stopped."""
    node = dataset
    for part in path:
        groups = getattr(node, "groups", {})
        if part not in groups:
            raise MissingVariable(
                f"no group {part!r} under {'/'.join(path[:path.index(part)]) or '/'}")
        node = groups[part]
    return node


@dataclass(frozen=True)
class Soundings:
    """Valid soundings from one granule, already filtered."""

    granule: str
    acquired: datetime | None
    latitude: np.ndarray
    longitude: np.ndarray
    values: Mapping[str, np.ndarray]
    qa_stored: np.ndarray
    #: Covariate values on the soundings methane already selected. Each is
    #: paired with a validity mask of the same length rather than being
    #: pre-filtered, because dropping a sounding here would drop its methane.
    covariates: Mapping[str, np.ndarray] = field(default_factory=dict)
    covariate_valid: Mapping[str, np.ndarray] = field(default_factory=dict)
    #: Per-cell counts of in-box soundings **before** any quality filtering,
    #: and of those carrying a retrieval at all.
    #:
    #: Gridded here rather than carried as per-sounding indices because the
    #: pre-filter set runs a few hundred times larger than the kept set -- on
    #: the design granule, 12,179 against 31 -- and only the per-cell total is
    #: wanted. They are counts, not sums: no value is averaged over them.
    prefilter_counts: np.ndarray | None = None
    retrieved_counts: np.ndarray | None = None
    #: Across-track detector column of each kept sounding, 0 to 214.
    #:
    #: Derived from the flat index rather than read, because the variables are
    #: shaped (time, scanline, ground_pixel) so the column is the flat index
    #: modulo the ground-pixel count. It costs no extra variable read.
    #:
    #: This is the axis destriping corrects along. Retaining it is what makes
    #: the one preprocessing omission this project called unrecoverable
    #: testable later without a second 28.9 GB pass.
    across_track: np.ndarray | None = None

    def __len__(self) -> int:
        return int(self.latitude.size)

    @property
    def day_of_year(self) -> np.ndarray:
        """Fractional day of year for each sounding, from the granule time.

        Constant within a granule. A granule covers about fifty minutes, so
        every sounding in one shares a date to within an hour, and the seasonal
        term moves by 2*pi/365 per day; the error this introduces in the
        harmonic is under a tenth of a percent of its amplitude. Using the
        per-sounding delta_time would be more exact and is not worth another
        variable read. Returns an empty array for an empty granule and NaN when
        the granule carries no time at all, so a granule with no date cannot
        silently be treated as 1 January.
        """
        if self.acquired is None:
            return np.full(len(self), np.nan)
        start = datetime(self.acquired.year, 1, 1)
        day = (self.acquired - start).total_seconds() / 86400.0 + 1.0
        return np.full(len(self), day, dtype="float64")


@dataclass(frozen=True)
class GranuleContribution:
    """What one granule gave to a composite."""

    granule: str
    acquired: datetime | None
    soundings_read: int
    soundings_valid: int
    soundings_in_box: int
    #: Soundings inside the box **before any quality filtering**, and those of
    #: them that carry a retrieval at all.
    #:
    #: These exist because ``soundings_in_box`` is post-filter, so a quality
    #: threshold could be reported without reporting what it removed. Two
    #: numbers rather than one because the domain has two different losses and
    #: quoting a single "rejection rate" conflates them: most in-box soundings
    #: carry **no retrieval** (cloud, geometry) and so are not rejected by the
    #: threshold, there is simply nothing to reject; of those that do carry one,
    #: the threshold removes a further share. On the granule used to design
    #: this, 12,179 soundings were in box, 410 carried a retrieval, and 31
    #: passed -- 96.6 percent lost to no-retrieval and 92.4 percent of the
    #: remainder lost to the threshold.
    soundings_in_box_total: int = 0
    soundings_in_box_retrieved: int = 0
    #: The granule's declared ground pixel size, verbatim from the file's
    #: ``spatial_resolution`` global attribute. Recorded per granule rather
    #: than assumed constant because the footprint changed in August 2019, so a
    #: multi-year composite would mix two of them.
    pixel_size: str | None = None
    #: In-box soundings carrying a valid value, per covariate. Far below
    #: ``soundings_in_box`` for albedo, which is the point of recording it.
    covariates_valid: Mapping[str, int] = field(default_factory=dict)
    #: Covariates the granule does not contain at all. A granule missing one is
    #: still gridded for everything else rather than being discarded.
    covariates_missing: tuple[str, ...] = ()
    #: Mean and spread of the in-box departure for this granule, and the count
    #: they rest on. Recorded per granule rather than only per cell so that a
    #: swath sitting systematically high or low against the prior is
    #: identifiable as a synoptic anomaly instead of being averaged into the
    #: cells it crossed.
    departure_mean: float | None = None
    departure_sd: float | None = None
    departure_n: int = 0

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
            "soundings_in_box_total": self.soundings_in_box_total,
            "soundings_in_box_retrieved": self.soundings_in_box_retrieved,
            "pixel_size": self.pixel_size,
            "covariates_valid": dict(self.covariates_valid),
            "covariates_missing": list(self.covariates_missing),
            "departure_mean": self.departure_mean,
            "departure_sd": self.departure_sd,
            "departure_n": self.departure_n,
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
    #: Covariate sums and the counts each rests on. Separate from ``counts``
    #: because a covariate is valid on a different, usually much smaller, set of
    #: soundings than methane, and dividing one by the other would be wrong by
    #: whatever that difference is.
    covariate_sums: Mapping[str, np.ndarray] = field(default_factory=dict)
    covariate_counts: Mapping[str, np.ndarray] = field(default_factory=dict)

    @property
    def variables(self) -> list[str]:
        return sorted(self.sums)

    @property
    def covariates(self) -> list[str]:
        return sorted(self.covariate_sums)

    @property
    def all_variables(self) -> list[str]:
        return sorted([*self.sums, *self.covariate_sums])

    def count_of(self, variable: str) -> np.ndarray:
        """The denominator this variable's mean must be divided by.

        Methane variables share the sounding count. Every covariate has its
        own, because it was valid on its own subset of those soundings.
        """
        if variable in self.sums:
            return self.counts
        if variable in self.covariate_counts:
            return self.covariate_counts[variable]
        raise KeyError(
            f"{variable!r} not in this composite; have {self.all_variables}")

    def mean_of(self, variable: str) -> np.ndarray:
        """Mean value per cell, NaN where nothing valid fell.

        Always divided by :meth:`count_of` for the same variable, so a
        covariate observed on 3 percent of soundings is averaged over the cells
        and soundings that actually carried it and is NaN elsewhere.
        """
        if variable in self.sums:
            numerator = self.sums[variable]
        elif variable in self.covariate_sums:
            numerator = self.covariate_sums[variable]
        else:
            raise KeyError(
                f"{variable!r} not in this composite; have {self.all_variables}")
        denominator = self.count_of(variable)
        out = np.full(self.spec.shape, np.nan, dtype="float64")
        covered = denominator > 0
        out[covered] = numerator[covered] / denominator[covered]
        return out

    def grids(self, variable: str) -> tuple[np.ndarray, np.ndarray]:
        """``(mean, count)``. The pair is the unit of use, not the mean alone.

        The count returned is this variable's own, never methane's, so the pair
        is self-consistent for a covariate as well as for methane.
        """
        return self.mean_of(variable), self.count_of(variable).copy()

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


def _scaled(raw, fill, scale, offset):
    """Physical values and a validity mask, from one variable's own attributes."""
    value = raw.astype("float64")
    if scale:
        value = value * scale
    if offset:
        value = value + offset
    valid = np.isfinite(value)
    if fill is not None:
        valid &= raw != fill
    return value, valid


def read_soundings(
    path: str | Path,
    spec: GridSpec,
    *,
    qa_threshold: float = 0.75,
    variables: Sequence[str] = (PRIMARY, SECONDARY),
    covariates: Sequence[CovariateSpec] = (),
    group_name: str = "PRODUCT",
) -> tuple[Soundings, GranuleContribution]:
    """Read one granule and return the soundings that survive filtering.

    Filtering is, in order: drop the fill value of each variable read from that
    variable's own ``_FillValue``; drop soundings whose ``qa_value`` is the qa
    fill; drop those below the quality threshold, compared in stored units; and
    finally restrict to the grid's bounding box.

    ``covariates`` take no part in that. They are read afterwards, on the
    soundings already selected, each masked by its own ``_FillValue`` and its
    own attributes. A covariate that is absent from the granule is recorded in
    the contribution and skipped; it does not fail the granule, because one
    missing support field is not a reason to discard a swath of methane.

    A covariate whose group is :data:`DERIVED` is computed rather than read.
    The two that exist are the TM5 a priori column and the departure of the
    bias-corrected retrieval from it, both in ppb. They travel as ordinary
    covariates so that each carries its own count and neither can be separated
    from the denominator it was averaged over.
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

        wanted = [c for c in covariates if c.group != DERIVED]
        derived = [c for c in covariates if c.group == DERIVED]

        read_values = {}
        good = np.ones(lat.shape, dtype=bool)
        across_track_width = None
        for name in variables:
            raw = group.variables[name]
            if raw.dimensions and raw.dimensions[-1] == "ground_pixel":
                across_track_width = int(raw.shape[-1])
            value, valid = _scaled(*_read_variable(group, name))
            good &= valid
            read_values[name] = value

        total = int(lat.size)

        if lat_fill is not None:
            good &= lat != lat_fill
        if lon_fill is not None:
            good &= lon != lon_fill
        if qa_fill is not None:
            good &= qa_raw != qa_fill

        # Everything except the quality cut. Held separately so the threshold's
        # effect over the domain is measurable rather than inferred: without
        # this, the only in-box count is the post-filter one and "N read, M
        # passed" cannot be written for this region. See
        # `GranuleContribution.soundings_in_box_retrieved`.
        retrieved = good.copy()

        cutoff = stored_threshold(qa_threshold, qa_scale, qa_offset)
        good &= qa_raw >= cutoff
        valid = int(good.sum())

        row, col, inside = spec.cell_of(lat, lon)
        keep = good & inside
        in_box_total = int(inside.sum())
        in_box_retrieved = int((inside & retrieved).sum())

        prefilter_counts = np.zeros(spec.shape, dtype="int64")
        retrieved_counts = np.zeros(spec.shape, dtype="int64")
        np.add.at(prefilter_counts, (row[inside], col[inside]), 1)
        in_retrieved = inside & retrieved
        np.add.at(retrieved_counts, (row[in_retrieved], col[in_retrieved]), 1)

        # Covariates are read on `keep` and never fold into it.
        covariate_values, covariate_masks = {}, {}
        missing: list[str] = []
        for covariate in wanted:
            try:
                source = open_group(dataset, covariate.path)
                raw, fill, scale, offset = _read_variable(source, covariate.name)
            except MissingVariable:
                missing.append(covariate.name)
                continue
            if raw.size != lat.size:
                missing.append(covariate.name)
                continue
            value, ok = _scaled(raw, fill, scale, offset)
            covariate_values[covariate.name] = value[keep]
            covariate_masks[covariate.name] = ok[keep]

        departure_stats = (None, None, 0)
        if derived:
            departure_stats = _derive_apriori(
                dataset, path, derived, read_values.get(PRIMARY), keep,
                covariate_values, covariate_masks, missing)

        acquired = _acquired_from(dataset, path)
        # Verbatim from the file rather than from the mission documentation, so
        # the record is a read value and not a recollection.
        pixel_size = getattr(dataset, "spatial_resolution", None)
        pixel_size = str(pixel_size) if pixel_size is not None else None
        soundings = Soundings(
            granule=path.name,
            acquired=acquired,
            latitude=np.asarray(lat)[keep].astype("float64"),
            longitude=np.asarray(lon)[keep].astype("float64"),
            values={k: v[keep] for k, v in read_values.items()},
            qa_stored=np.asarray(qa_raw)[keep],
            covariates=covariate_values,
            covariate_valid=covariate_masks,
            prefilter_counts=prefilter_counts,
            retrieved_counts=retrieved_counts,
            across_track=(
                (np.arange(lat.size)[keep] % across_track_width).astype("int64")
                if across_track_width else None),
        )
    contribution = GranuleContribution(
        granule=path.name, acquired=acquired, soundings_read=total,
        soundings_valid=valid, soundings_in_box=len(soundings),
        soundings_in_box_total=in_box_total,
        soundings_in_box_retrieved=in_box_retrieved,
        pixel_size=pixel_size,
        covariates_valid={k: int(m.sum()) for k, m in covariate_masks.items()},
        covariates_missing=tuple(missing),
        departure_mean=departure_stats[0], departure_sd=departure_stats[1],
        departure_n=departure_stats[2],
    )
    return soundings, contribution


def _derive_apriori(dataset, path, derived, retrieved, keep,
                    values, masks, missing) -> tuple:
    """Compute the a priori column and the departure for one open granule.

    Done here, on the dataset the caller already has open, rather than through
    ``apriori.from_granule``, which would reopen and re-read a 58 MB file for
    quantities the streaming loop is holding anyway.

    Returns the granule's mean, spread and count of in-box departure. A
    granule with no usable prior yields ``(None, None, 0)`` and is not a
    failure: one missing support field is not a reason to discard a swath.
    """
    from src.methane import apriori as ap

    names = {c.name for c in derived}
    unknown = names - {APRIORI, DEPARTURE}
    if unknown:
        raise MissingVariable(f"unknown derived covariate(s) {sorted(unknown)}")

    try:
        node = open_group(dataset, ap.INPUT_DATA)
        # The variables are checked before either is read. A granule that has
        # the group but not the profiles must be recorded as missing them, not
        # raise: one absent support field is not a reason to discard a swath of
        # methane, which is the same contract the read covariates keep.
        for name in (ap.PROFILE, ap.DRY_AIR):
            if name not in node.variables:
                raise MissingVariable(f"no variable {name!r} in {'/'.join(ap.INPUT_DATA)}")
        methane, m_fill, m_raw = ap.read_profile(node, ap.PROFILE)
        dry_air, a_fill, a_raw = ap.read_profile(node, ap.DRY_AIR)
    except (MissingVariable, ap.AprioriError, KeyError):
        missing.extend(sorted(names))
        return (None, None, 0)

    column = ap.column_apriori(methane, dry_air, methane_fill=m_fill,
                               dry_air_fill=a_fill, methane_raw=m_raw,
                               dry_air_raw=a_raw)

    if APRIORI in names:
        values[APRIORI] = column.values[keep]
        masks[APRIORI] = column.valid[keep]

    if DEPARTURE not in names:
        return (None, None, 0)
    if retrieved is None:
        missing.append(DEPARTURE)
        return (None, None, 0)

    gap = ap.departure(np.asarray(retrieved, dtype="float64"), column)
    ok = np.isfinite(gap)
    values[DEPARTURE] = gap[keep]
    masks[DEPARTURE] = ok[keep]

    inbox = gap[keep][ok[keep]]
    if not inbox.size:
        return (None, None, 0)
    return (float(inbox.mean()), float(inbox.std()), int(inbox.size))


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


def accumulate_covariates(soundings: Soundings, row, col, sums, counts) -> None:
    """Add a granule's covariates into pre-sized sums and counts of their own.

    Shared by :func:`grid_granules` and the streaming accumulator so the two
    cannot drift apart. A covariate is added only where its own mask is true and
    its count is incremented on exactly those soundings, so the sum and its
    denominator are built from the same set by construction rather than by two
    pieces of code agreeing. A covariate with no pre-sized grid is ignored: the
    caller decides what it is accumulating, not the granule.
    """
    for name, values in soundings.covariates.items():
        if name not in sums:
            continue
        mask = soundings.covariate_valid[name]
        if not mask.any():
            continue
        np.add.at(sums[name], (row[mask], col[mask]), values[mask])
        np.add.at(counts[name], (row[mask], col[mask]), 1)


def grid_granules(
    paths: Iterable[str | Path],
    spec: GridSpec,
    *,
    qa_threshold: float = 0.75,
    variables: Sequence[str] = (PRIMARY, SECONDARY),
    covariates: Sequence[CovariateSpec] = (),
) -> Composite:
    """Bin every granule onto the grid, averaging where cells receive several.

    Returns a :class:`Composite`, which carries the counts alongside the sums
    and records what each granule contributed. Covariates accumulate into their
    own sums and counts and never touch the methane ones.
    """
    counts = np.zeros(spec.shape, dtype="int64")
    sums = {name: np.zeros(spec.shape, dtype="float64") for name in variables}
    covariate_sums = {c.name: np.zeros(spec.shape, dtype="float64")
                      for c in covariates}
    covariate_counts = {c.name: np.zeros(spec.shape, dtype="int64")
                        for c in covariates}
    contributions: list[GranuleContribution] = []

    for path in paths:
        soundings, contribution = read_soundings(
            path, spec, qa_threshold=qa_threshold, variables=variables,
            covariates=covariates)
        contributions.append(contribution)
        if not len(soundings):
            continue
        row, col, _ = spec.cell_of(soundings.latitude, soundings.longitude)
        np.add.at(counts, (row, col), 1)
        for name in variables:
            np.add.at(sums[name], (row, col), soundings.values[name])
        accumulate_covariates(soundings, row, col, covariate_sums, covariate_counts)

    return Composite(spec=spec, qa_threshold=qa_threshold, counts=counts,
                     sums=sums, contributions=tuple(contributions),
                     covariate_sums=covariate_sums,
                     covariate_counts=covariate_counts)


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
