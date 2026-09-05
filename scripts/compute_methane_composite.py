#!/usr/bin/env python3
"""Build a gridded methane composite by streaming granules one at a time.

A thin wrapper over ``src.fetch.s5p`` and ``src.methane.grid``. All arithmetic
lives there.

    python scripts/compute_methane_composite.py                       # plan only
    python scripts/compute_methane_composite.py --run --max-granules 600
    python scripts/compute_methane_composite.py --run --max-hours 2

Download, grid, accumulate, delete, repeat. The alternative, fetching a year
and then computing, needs 28.9 GiB for 2018 alone and about 202 GiB for seven
years, against 29 GiB free. Streaming bounds peak disk at one granule.

**Peak disk.** At most one granule exists at a time, plus the checkpoint. The
bound is asserted rather than assumed: before each download the working
directory is checked to be empty, and after each granule it is checked to be
empty again, so a leak fails the run instead of filling the volume silently.

**Resumption.** Sums and counts accumulate, never means, because a mean cannot
be averaged with another mean. The accumulator plus the list of finished
granules is checkpointed every ``--checkpoint-every`` granules, default 10. The
grid is small, 33 by 31 cells, so a checkpoint is tens of kilobytes and costs
nothing measurable; 10 is a compromise that keeps the log readable rather than
one forced by cost. A crash therefore loses at most the granules since the last
checkpoint, roughly a minute of transfer. The write is atomic: a temporary file
is renamed into place, so a crash mid-write leaves the previous checkpoint
intact rather than a truncated one.

**Free space.** Checked before starting and before every download. Falling
below the floor stops the run cleanly with the accumulator checkpointed, so a
full disk costs the remaining granules rather than the hours already spent.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import shutil
import sys
import time
from pathlib import Path

import numpy as np
import yaml

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from src.fetch import s5p  # noqa: E402
from src.methane import grid as mg  # noqa: E402
from src.methane import seasonal as se  # noqa: E402
from src.methane.grid import Composite, GranuleContribution, GridSpec  # noqa: E402

#: Band order in the exported GeoTIFF. One file rather than three because the
#: three arrays share one grid and must be read together: a mean without its
#: count is exactly the thing src/methane exists to prevent, and separate files
#: invite reading one without the other.
BANDS = ("methane_mixing_ratio_bias_corrected mean, ppb",
         "methane_mixing_ratio mean, ppb",
         "sounding count")

#: Peak disk is one granule plus a checkpoint. The largest granule observed on
#: this mirror is 66 MB; the allowance is generous and the assertion below is
#: what actually enforces the bound.
PEAK_DISK_ALLOWANCE_BYTES = 256 * 1024 ** 2


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if abs(n) < 1024 or unit == "TB":
            return f"{n:,.1f} {unit}" if unit != "B" else f"{n:,.0f} B"
        n /= 1024.0
    return f"{n:,.1f} TB"


def as_date(value) -> dt.date:
    return value if isinstance(value, dt.date) else dt.date.fromisoformat(str(value))


class Accumulator:
    """Sums, counts, provenance and the saturation curve, checkpointed atomically.

    Holds sums rather than means so partial results compose: two runs over
    disjoint granules can be added, and a mean can be taken at the end.

    ``saturation`` records, for each granule as it is added, how many cells it
    covered that nothing had covered before and how many cells were covered in
    total afterwards. Two integers per granule, so the whole 2018 run is 578
    pairs and costs about 9 kB in the checkpoint.

    It exists because coverage is a union statistic and saturates, and a
    reconnaissance sample cannot be extrapolated to a year without knowing the
    shape of the curve. Six granules covering 1.04 percent of 2018 reached 50.4
    percent of cells, which was read at the time as an estimate of what the year
    would reach; the year reached 90.52 percent. The early granules each add
    many new cells and the late ones add almost none, so a small sample lands
    far up a curve that is still climbing and understates the ceiling badly. The
    record is what would let a reader see that shape instead of inferring it,
    and it is cheap enough that there is no reason not to keep it.

    It is written going forward only. The curve is a property of the order
    granules were added and cannot be recovered from a finished grid, so the
    committed 2018 composite has no record and re-running the year to obtain one
    would cost a 28.9 GB download to change no published number.
    """

    def __init__(self, spec: GridSpec, qa_threshold: float, variables,
                 covariates=(), harmonics: int = 2):
        self.spec = spec
        self.qa_threshold = qa_threshold
        self.variables = list(variables)
        self.covariates = list(covariates)
        self.counts = np.zeros(spec.shape, dtype="int64")
        self.sums = {v: np.zeros(spec.shape, dtype="float64") for v in self.variables}
        # Pre-sized so a covariate's sum and its count are created together and
        # can never be added to independently.
        self.covariate_sums = {c.name: np.zeros(spec.shape, dtype="float64")
                               for c in self.covariates}
        self.covariate_counts = {c.name: np.zeros(spec.shape, dtype="int64")
                                 for c in self.covariates}
        self.contributions: list[GranuleContribution] = []
        self.done: set[str] = set()
        #: One (newly covered, cumulative covered) pair per granule added, in
        #: the order they were added. See the class docstring.
        self.saturation: list[tuple[int, int]] = []
        #: The set of cells each granule touched, one packed bitmap per
        #: granule, in the same order as `contributions`.
        #:
        #: The saturation pair above cannot answer per-granule coverage: a
        #: newly-covered count of zero is recorded both by a granule that
        #: covered nothing and by one that covered three hundred cells another
        #: granule had already reached, and 141 of the 222 productive granules
        #: in the 2018 run recorded exactly zero. The cell *set* separates
        #: them. Packed to bits it is ceil(n_cells / 8) bytes per granule,
        #: 128 for this grid, so a full year costs about 74 kB against a
        #: 285 kB checkpoint, which is cheap enough not to need a decision.
        self.granule_cells: list[np.ndarray] = []
        #: Sufficient statistics for the shared seasonal fit. Accumulated at the
        #: sounding level so the cycle can be removed before the cell mean is
        #: taken, in one pass and without holding a sounding twice.
        self.harmonics = se.HarmonicStats(spec.shape, se.HarmonicBasis(harmonics))

    @property
    def covered(self) -> int:
        """Cells with at least one sounding so far."""
        return int((self.counts > 0).sum())

    def _pack_cells(self, row=None, col=None) -> np.ndarray:
        """One granule's touched cells as a packed bitmap over the flat grid."""
        flat = np.zeros(self.spec.n_cells, dtype=bool)
        if row is not None and len(row):
            flat[np.asarray(row) * self.spec.n_cols + np.asarray(col)] = True
        return np.packbits(flat)

    def add(self, soundings, contribution: GranuleContribution) -> None:
        before = self.covered
        self.contributions.append(contribution)
        self.done.add(contribution.granule)
        if not len(soundings):
            # An empty granule still gets a row, all zero, so that the cell
            # sets stay index-aligned with `contributions`. A shorter array
            # would silently reassign every later granule's set.
            self.granule_cells.append(self._pack_cells())
        else:
            row, col, _ = self.spec.cell_of(soundings.latitude, soundings.longitude)
            self.granule_cells.append(self._pack_cells(row, col))
            np.add.at(self.counts, (row, col), 1)
            for name in self.variables:
                np.add.at(self.sums[name], (row, col), soundings.values[name])
            mg.accumulate_covariates(soundings, row, col,
                                     self.covariate_sums, self.covariate_counts)
            day = soundings.day_of_year
            if np.isfinite(day).all():
                self.harmonics.add(row, col, soundings.values[mg.PRIMARY], day)
        after = self.covered
        self.saturation.append((after - before, after))

    def composite(self) -> Composite:
        return Composite(
            spec=self.spec, qa_threshold=self.qa_threshold,
            counts=self.counts.copy(),
            sums={k: v.copy() for k, v in self.sums.items()},
            contributions=tuple(self.contributions),
            covariate_sums={k: v.copy() for k, v in self.covariate_sums.items()},
            covariate_counts={k: v.copy()
                              for k, v in self.covariate_counts.items()})

    def save(self, path: Path) -> None:
        """Write atomically: a crash mid-write keeps the previous checkpoint."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp = path.with_suffix(path.suffix + ".tmp")
        payload = {
            "spec": [self.spec.west, self.spec.south, self.spec.east,
                     self.spec.north, self.spec.resolution],
            "qa_threshold": self.qa_threshold,
            "variables": self.variables,
            "counts": self.counts,
            "contributions": np.array(
                json.dumps([c.as_dict() for c in self.contributions])),
            "saturation": np.array(self.saturation, dtype="int64").reshape(-1, 2),
            # One row per granule, in contribution order, bit i set where the
            # granule reached flat cell i.
            "granule_cells": (np.array(self.granule_cells, dtype="uint8")
                              if self.granule_cells
                              else np.empty((0, (self.spec.n_cells + 7) // 8),
                                            dtype="uint8")),
            "covariates": np.array(json.dumps(
                [{"name": c.name, "group": c.group} for c in self.covariates])),
            # The seasonal sufficient statistics. Written as a block so a
            # partial set cannot be restored: solving from a mismatched subset
            # would give a plausible cycle from the wrong soundings.
            "harmonics": np.array(self.harmonics.basis.harmonics),
            "hs::n": self.harmonics.n,
            "hs::sum_y": self.harmonics.sum_y,
            "hs::sum_yy": self.harmonics.sum_yy,
            "hs::sum_d": self.harmonics.sum_d,
            "hs::sum_dd": self.harmonics.sum_dd,
            "hs::sum_x": self.harmonics.sum_x,
            "hs::sum_xx": self.harmonics.sum_xx,
            "hs::sum_yx": self.harmonics.sum_yx,
        }
        for name in self.variables:
            payload[f"sum::{name}"] = self.sums[name]
        # A covariate's sum and its count are written and read as a pair. There
        # is no code path that restores one without the other.
        for name in self.covariate_sums:
            payload[f"cvsum::{name}"] = self.covariate_sums[name]
            payload[f"cvcount::{name}"] = self.covariate_counts[name]
        # Pass an open handle: np.savez_compressed appends '.npz' to a path
        # that does not already end in it, which would write the temp file
        # somewhere other than where the rename below looks for it.
        with open(tmp, "wb") as handle:
            np.savez_compressed(handle, **payload)
        tmp.replace(path)

    @classmethod
    def load(cls, path: Path) -> "Accumulator":
        with np.load(path, allow_pickle=False) as data:
            spec = GridSpec(*[float(x) for x in data["spec"]])
            variables = [str(v) for v in data["variables"]]
            covariates = [mg.CovariateSpec(**record)
                          for record in json.loads(str(data["covariates"]))] \
                if "covariates" in data.files else []
            acc = cls(spec, float(data["qa_threshold"]), variables, covariates)
            acc.counts = data["counts"].astype("int64")
            for name in variables:
                acc.sums[name] = data[f"sum::{name}"].astype("float64")
            for covariate in covariates:
                name = covariate.name
                acc.covariate_sums[name] = data[f"cvsum::{name}"].astype("float64")
                acc.covariate_counts[name] = data[f"cvcount::{name}"].astype("int64")
            records = json.loads(str(data["contributions"]))
            # Checkpoints written before saturation was recorded have no such
            # key. The curve cannot be reconstructed from a finished grid, so
            # an older checkpoint loads with an empty record rather than a
            # fabricated one.
            saved = (data["saturation"].astype("int64")
                     if "saturation" in data.files else np.empty((0, 2), "int64"))
            # Checkpoints written before cell sets were retained have no such
            # key, and the sets cannot be reconstructed from a finished grid.
            # An older checkpoint loads with an empty record rather than a
            # fabricated one, exactly as the saturation curve does.
            acc.granule_cells = [row.copy() for row in
                                 data["granule_cells"].astype("uint8")] \
                if "granule_cells" in data.files else []
            if "hs::n" in data.files:
                acc.harmonics = se.HarmonicStats(
                    spec.shape, se.HarmonicBasis(int(data["harmonics"])),
                    n=data["hs::n"].astype("int64"),
                    sum_y=data["hs::sum_y"].astype("float64"),
                    sum_yy=data["hs::sum_yy"].astype("float64"),
                    sum_d=data["hs::sum_d"].astype("float64"),
                    sum_dd=data["hs::sum_dd"].astype("float64"),
                    sum_x=data["hs::sum_x"].astype("float64"),
                    sum_xx=data["hs::sum_xx"].astype("float64"),
                    sum_yx=data["hs::sum_yx"].astype("float64"))
        acc.saturation = [(int(a), int(b)) for a, b in saved]
        for record in records:
            acquired = (dt.datetime.fromisoformat(record["acquired"])
                        if record["acquired"] else None)
            acc.contributions.append(GranuleContribution(
                granule=record["granule"], acquired=acquired,
                soundings_read=record["soundings_read"],
                soundings_valid=record["soundings_valid"],
                soundings_in_box=record["soundings_in_box"],
                covariates_valid=record.get("covariates_valid", {}),
                covariates_missing=tuple(record.get("covariates_missing", ())),
                departure_mean=record.get("departure_mean"),
                departure_sd=record.get("departure_sd"),
                departure_n=record.get("departure_n", 0)))
            acc.done.add(record["granule"])
        return acc


def working_bytes(directory: Path) -> int:
    return sum(p.stat().st_size for p in Path(directory).glob("*") if p.is_file())


def assert_disk_bound(directory: Path, allowance: int = PEAK_DISK_ALLOWANCE_BYTES) -> int:
    """Fail loudly if the working directory holds more than one granule's worth."""
    used = working_bytes(directory)
    if used > allowance:
        raise RuntimeError(
            f"working directory {directory} holds {human(used)}, above the "
            f"{human(allowance)} bound. The streaming loop is leaking granules; "
            f"stopping rather than filling the volume.")
    return used


def export(composite: Composite, stem: Path,
           csv_path: Path | None = None) -> tuple[Path, Path]:
    """Write the composite as a three-band GeoTIFF and a complete per-cell CSV.

    Everything is float32, counts included, so one file can hold all three
    bands; the largest count observed is 410, exact in float32. Unobserved
    cells are NaN in both mean bands and 0 in the count band, so the two encode
    the same fact and neither can be read without the other contradicting it.

    The CSV carries every cell, not only the populated ones, so it describes
    the grid rather than the subset that happened to be observed.
    """
    import csv as _csv
    import rasterio
    from rasterio.transform import from_origin

    spec = composite.spec
    counts = composite.counts
    primary = composite.mean_of(mg.PRIMARY)
    secondary = composite.mean_of(mg.SECONDARY)

    tif = stem.with_suffix(".tif")
    stem.parent.mkdir(parents=True, exist_ok=True)
    transform = from_origin(spec.west, spec.north, spec.resolution, spec.resolution)
    with rasterio.open(
        tif, "w", driver="GTiff", height=spec.shape[0], width=spec.shape[1],
        count=3, dtype="float32", crs="EPSG:4326", transform=transform,
        nodata=float("nan"), compress="deflate",
    ) as dst:
        dst.write(primary.astype("float32"), 1)
        dst.write(secondary.astype("float32"), 2)
        dst.write(counts.astype("float32"), 3)
        for i, description in enumerate(BANDS, start=1):
            dst.set_band_description(i, description)
        dst.update_tags(
            qa_threshold=str(composite.qa_threshold),
            granules_gridded=str(len(composite.contributions)),
            granules_with_data=str(sum(
                1 for c in composite.contributions if c.soundings_in_box)),
            soundings=str(int(counts.sum())),
            note="Unobserved cells are NaN in bands 1 and 2 and 0 in band 3.",
        )

    csv_path = Path(csv_path) if csv_path else stem.with_suffix(".csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with open(csv_path, "w", newline="") as handle:
        writer = _csv.writer(handle)
        writer.writerow(["centre_lat", "centre_lon", "sounding_count",
                         "ch4_bias_corrected_ppb", "ch4_raw_ppb"])
        for row in range(spec.shape[0]):
            lat = spec.north - (row + 0.5) * spec.resolution
            for col in range(spec.shape[1]):
                lon = spec.west + (col + 0.5) * spec.resolution
                n = int(counts[row, col])
                writer.writerow([
                    f"{lat:.4f}", f"{lon:.4f}", n,
                    "" if n == 0 else f"{primary[row, col]:.2f}",
                    "" if n == 0 else f"{secondary[row, col]:.2f}",
                ])
    return tif, csv_path


def export_covariates(composite: Composite, stem: Path) -> tuple[Path, Path]:
    """Write the covariate grids as a companion file, not as extra bands.

    A companion rather than an extension of methane_composite_2018.tif, for a
    reason that is the whole point of the covariate work: every covariate has
    its own denominator. The methane file's third band is the sounding count,
    and a reader who found fifteen bands in it would reasonably divide any of
    them by that band. Albedo is valid on a few percent of those soundings, so
    that division would be wrong by a factor of thirty and would look fine.
    Here each covariate's mean is immediately followed by its own count, and
    the file contains no count that belongs to anything else.

    The committed methane composite is also left byte-for-byte alone, which
    keeps the reproduction check meaningful and every test that reads it valid.
    """
    import csv as _csv
    import rasterio
    from rasterio.transform import from_origin

    spec = composite.spec
    names = composite.covariates
    if not names:
        raise SystemExit("no covariates in this composite; nothing to export")

    tif = stem.with_suffix(".tif")
    stem.parent.mkdir(parents=True, exist_ok=True)
    transform = from_origin(spec.west, spec.north, spec.resolution, spec.resolution)
    with rasterio.open(
        tif, "w", driver="GTiff", height=spec.shape[0], width=spec.shape[1],
        count=2 * len(names), dtype="float32", crs="EPSG:4326",
        transform=transform, nodata=float("nan"), compress="deflate",
    ) as dst:
        for i, name in enumerate(names):
            mean, count = composite.grids(name)
            dst.write(mean.astype("float32"), 2 * i + 1)
            dst.write(count.astype("float32"), 2 * i + 2)
            dst.set_band_description(2 * i + 1, f"{name} mean")
            dst.set_band_description(2 * i + 2, f"{name} count")
        dst.update_tags(
            qa_threshold=str(composite.qa_threshold),
            covariates=",".join(names),
            soundings=str(int(composite.counts.sum())),
            note=("Each mean band is followed by ITS OWN count band. Do not "
                  "divide these by the sounding count in the methane file: a "
                  "covariate is valid on a different subset of soundings."),
        )

    csv_path = stem.with_suffix(".csv")
    with open(csv_path, "w", newline="") as handle:
        writer = _csv.writer(handle)
        header = ["centre_lat", "centre_lon", "sounding_count"]
        for name in names:
            header += [f"{name}_mean", f"{name}_count"]
        writer.writerow(header)
        grids = {name: composite.grids(name) for name in names}
        for row in range(spec.shape[0]):
            lat = spec.north - (row + 0.5) * spec.resolution
            for col in range(spec.shape[1]):
                lon = spec.west + (col + 0.5) * spec.resolution
                record = [f"{lat:.4f}", f"{lon:.4f}",
                          int(composite.counts[row, col])]
                for name in names:
                    mean, count = grids[name]
                    n = int(count[row, col])
                    record += [("" if n == 0 else f"{mean[row, col]:.6g}"), n]
                writer.writerow(record)
    return tif, csv_path


def report_seasonal(stats, spread_threshold: float = 15.0):
    """Fit the shared cycle at one and two harmonics and report both.

    Both come from the same accumulated statistics, so the comparison is on
    exactly the same soundings and the only difference is the model.
    """
    fits = {}
    print("\n  seasonal fit, shared across all cells, fitted at the sounding level")
    print(f"    {'model':<14}{'terms':<46}{'amplitude':>10}{'peak day':>10}"
          f"{'range':>9}{'resid sd':>10}{'R2 within':>11}")
    for harmonics in (1, stats.basis.harmonics):
        if harmonics in fits:
            continue
        try:
            fit = se.solve(stats.truncated(harmonics),
                           spread_threshold=spread_threshold)
        except se.NotEnoughSeasonalSpread as failure:
            # A partial checkpoint can easily hold one date. Say so and carry
            # on rather than failing the whole export.
            print(f"    K={harmonics}: cannot be fitted. {failure}")
            continue
        fits[harmonics] = fit
        terms = "; ".join(f"{k} {v:+.4f}" for k, v in fit.terms.items())
        amplitude = " / ".join(f"{a:.3f}" for a in fit.amplitudes)
        print(f"    K={harmonics:<12}{terms:<46}{amplitude:>10}"
              f"{fit.peak_day:>10.1f}{fit.peak_to_trough:>9.3f}"
              f"{fit.residual_sd:>10.4f}{fit.variance_explained:>11.4f}")
    return fits


def compare_harmonics(fits) -> None:
    """Is the second harmonic warranted? Answer with an F test, not taste."""
    if 1 not in fits or 2 not in fits:
        return
    one, two = fits[1], fits[2]
    extra = one.residual_ss - two.residual_ss
    f = (extra / 2.0) / (two.residual_ss / two.degrees_of_freedom)
    from scipy import stats as sps
    p = float(sps.f.sf(f, 2, two.degrees_of_freedom))
    print(f"\n    second harmonic: residual sum of squares falls from "
          f"{one.residual_ss:,.0f} to {two.residual_ss:,.0f}")
    print(f"    F(2, {two.degrees_of_freedom:,}) = {f:,.1f}, p = {p:.3g}; "
          f"residual sd {one.residual_sd:.4f} -> {two.residual_sd:.4f} ppb")
    print(f"    peak day moves {one.peak_day:.1f} -> {two.peak_day:.1f}, "
          f"seasonal range {one.peak_to_trough:.2f} -> {two.peak_to_trough:.2f} ppb")


def report_sampling_dates(stats, spread_threshold: float = 15.0) -> None:
    """The artefact, measured directly instead of through solar zenith angle."""
    ok = stats.covered
    mean, spread = stats.date_mean(), stats.date_spread()
    print(f"\n  sampling dates over {int(ok.sum())} covered cells")
    print(f"    mean day of year   min {mean[ok].min():7.2f}  "
          f"median {np.median(mean[ok]):7.2f}  max {mean[ok].max():7.2f}  "
          f"range {mean[ok].max() - mean[ok].min():7.2f} days")
    print(f"    spread in days     min {spread[ok].min():7.2f}  "
          f"median {np.median(spread[ok]):7.2f}  max {spread[ok].max():7.2f}")
    for threshold in (1.0, 15.0, 30.0, 60.0):
        below = int((spread[ok] < threshold).sum())
        print(f"    cells with spread below {threshold:5.1f} days: {below:>4} "
              f"({100 * below / int(ok.sum()):5.1f}%)")
    print(f"    the flag uses {spread_threshold:.0f} days: roughly one month, "
          f"below which a cell's offset is poorly separable from the cycle")


def export_deseasonalised(fit, stats, spec, stem: Path) -> tuple[Path, Path]:
    """Write the deseasonalised field and the diagnostics that qualify it.

    A separate companion again, for the same reason as the covariates: this
    field has a different meaning from the composite mean and must not sit in
    the same file where a reader could take one for the other. Bands follow the
    established pattern, each mean immediately before its own count, and the two
    sampling-date bands are here rather than elsewhere because a deseasonalised
    value cannot be read without knowing how separable it was.
    """
    import csv as _csv
    import rasterio
    from rasterio.transform import from_origin

    mean_day, spread = stats.date_mean(), stats.date_spread()
    layers = [
        ("deseasonalised methane mean, ppb", fit.mu),
        ("sounding count", fit.counts.astype("float64")),
        ("mean day of year", mean_day),
        ("day of year standard deviation", spread),
        ("poorly identified flag", fit.poorly_identified.astype("float64")),
    ]

    tif = stem.with_suffix(".tif")
    stem.parent.mkdir(parents=True, exist_ok=True)
    transform = from_origin(spec.west, spec.north, spec.resolution, spec.resolution)
    with rasterio.open(
        tif, "w", driver="GTiff", height=spec.shape[0], width=spec.shape[1],
        count=len(layers), dtype="float32", crs="EPSG:4326",
        transform=transform, nodata=float("nan"), compress="deflate",
    ) as dst:
        for i, (description, array) in enumerate(layers, start=1):
            dst.write(np.asarray(array, dtype="float32"), i)
            dst.set_band_description(i, description)
        dst.update_tags(
            harmonics=str(fit.basis.harmonics),
            coefficients=", ".join(f"{k} {v:+.6f}" for k, v in fit.terms.items()),
            seasonal_amplitude_ppb=", ".join(f"{a:.4f}" for a in fit.amplitudes),
            peak_day_of_year=f"{fit.peak_day:.2f}",
            seasonal_range_ppb=f"{fit.peak_to_trough:.4f}",
            residual_sd_ppb=f"{fit.residual_sd:.4f}",
            note=("Band 1 is the per-cell offset with a region-wide seasonal "
                  "cycle removed at the SOUNDING level. It is not the composite "
                  "mean minus a cycle. Read bands 4 and 5 with it: a cell "
                  "sampled over a narrow window has an offset barely separable "
                  "from the cycle."),
        )

    csv_path = stem.with_suffix(".csv")
    with open(csv_path, "w", newline="") as handle:
        writer = _csv.writer(handle)
        writer.writerow(["centre_lat", "centre_lon", "sounding_count",
                         "ch4_deseasonalised_ppb", "mean_day_of_year",
                         "day_of_year_sd", "poorly_identified"])
        for row in range(spec.shape[0]):
            lat = spec.north - (row + 0.5) * spec.resolution
            for col in range(spec.shape[1]):
                lon = spec.west + (col + 0.5) * spec.resolution
                n = int(fit.counts[row, col])
                writer.writerow([
                    f"{lat:.4f}", f"{lon:.4f}", n,
                    "" if n == 0 else f"{fit.mu[row, col]:.4f}",
                    "" if n == 0 else f"{mean_day[row, col]:.3f}",
                    "" if n == 0 else f"{spread[row, col]:.3f}",
                    int(fit.poorly_identified[row, col]) if n else "",
                ])
    return tif, csv_path


def verify_methane(composite: Composite, reference: Path) -> dict:
    """Compare a rebuilt composite's methane against a committed one.

    Comparison is in float32, the precision the reference is stored at, so an
    exact reproduction gives exactly zero rather than a rounding residue that
    has to be argued about.
    """
    import rasterio

    with rasterio.open(reference) as src:
        ref_primary, ref_secondary, ref_counts = src.read(1), src.read(2), src.read(3)

    new_primary = composite.mean_of(mg.PRIMARY).astype("float32")
    new_secondary = composite.mean_of(mg.SECONDARY).astype("float32")
    new_counts = composite.counts.astype("float32")

    def difference(a, b):
        both_nan = np.isnan(a) & np.isnan(b)
        if (np.isnan(a) != np.isnan(b)).any():
            return float("inf")
        delta = np.where(both_nan, 0.0, np.abs(np.nan_to_num(a) - np.nan_to_num(b)))
        return float(delta.max())

    return {
        "bias_corrected": difference(new_primary, ref_primary),
        "raw": difference(new_secondary, ref_secondary),
        "counts": difference(new_counts, ref_counts),
        "covered_cells_new": int((composite.counts > 0).sum()),
        "covered_cells_reference": int((ref_counts > 0).sum()),
        "soundings_new": int(composite.counts.sum()),
        "soundings_reference": int(ref_counts.sum()),
    }


def report_covariate_coverage(composite: Composite) -> None:
    """Per-covariate coverage, which is far below methane's for albedo."""
    total_cells = composite.spec.n_cells
    methane_cells = int((composite.counts > 0).sum())
    soundings = int(composite.counts.sum())
    print(f"\n  covariate coverage (methane: {methane_cells}/{total_cells} cells, "
          f"{soundings:,} soundings)")
    print(f"    {'covariate':<24}{'cells':>7}{'% cells':>9}"
          f"{'soundings':>12}{'% of methane':>14}")
    for name in composite.covariates:
        count = composite.count_of(name)
        cells = int((count > 0).sum())
        total = int(count.sum())
        print(f"    {name:<24}{cells:>7}{100 * cells / total_cells:>8.2f}%"
              f"{total:>12,}{100 * total / soundings if soundings else 0:>13.2f}%")
    missing: dict[str, int] = {}
    for contribution in composite.contributions:
        for name in contribution.covariates_missing:
            missing[name] = missing.get(name, 0) + 1
    if missing:
        print(f"    granules missing a covariate entirely: {missing}")
    else:
        print("    every granule contained every requested covariate")


def build_argparser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--config", default=str(REPO / "config" / "sources.yml"))
    parser.add_argument("--source", default="s5p")
    parser.add_argument("--stream", default=None, help="override the configured stream")
    parser.add_argument("--start", default=None)
    parser.add_argument("--end", default=None)
    parser.add_argument("--work", default=None,
                        help="scratch directory for the one granule at a time")
    parser.add_argument("--checkpoint", default=None)
    parser.add_argument("--checkpoint-every", type=int, default=10)
    parser.add_argument("--min-free-gb", type=float, default=2.0,
                        help="abort cleanly if free space falls below this")
    parser.add_argument("--max-granules", type=int, default=None)
    parser.add_argument("--max-hours", type=float, default=None)
    parser.add_argument("--export-csv", default=None,
                        help="path for the per-cell CSV; defaults to the export stem")
    parser.add_argument("--export", default=None,
                        help="write GeoTIFF and CSV from an existing checkpoint "
                             "to this path stem, then exit without fetching")
    parser.add_argument("--export-covariates", default=None,
                        help="path stem for the covariate GeoTIFF and CSV")
    parser.add_argument("--verify-against", default=None,
                        help="committed composite to check the methane bands "
                             "against before writing anything")
    parser.add_argument("--export-deseasonalised", default=None,
                        help="path stem for the deseasonalised field")
    parser.add_argument("--export-harmonics", type=int, default=None,
                        help="which harmonic order to export; defaults to the "
                             "highest accumulated")
    parser.add_argument("--spread-threshold", type=float, default=15.0,
                        help="days below which a cell's offset is flagged as "
                             "poorly separable from the seasonal cycle")
    parser.add_argument("--no-covariates", action="store_true",
                        help="ignore the configured covariate list")
    parser.add_argument("--run", action="store_true",
                        help="actually download and grid; without it, plan only")
    parser.add_argument("--timeout", type=float, default=s5p.DEFAULT_TIMEOUT)
    return parser


def main(argv=None) -> int:
    args = build_argparser().parse_args(argv)
    config = yaml.safe_load(Path(args.config).read_text(encoding="utf-8"))[args.source]
    box = config["bounding_box"]
    stream = args.stream or config["stream"]
    start = as_date(args.start or config["start_date"])
    end = as_date(args.end or config["end_date"])
    work = Path(args.work) if args.work else REPO / "data" / "interim" / "s5p_work"
    checkpoint = Path(args.checkpoint) if args.checkpoint else \
        REPO / "data" / "interim" / f"methane_composite_{start:%Y%m%d}_{end:%Y%m%d}.npz"

    spec = GridSpec(box["west"], box["south"], box["east"], box["north"],
                    config["grid_resolution_deg"])
    variables = (mg.PRIMARY, mg.SECONDARY)
    covariates = () if args.no_covariates else tuple(
        mg.CovariateSpec(name=c["name"], group=c["group"])
        for c in config.get("covariates", []))

    if (args.export or args.export_covariates or args.verify_against
            or args.export_deseasonalised):
        if not checkpoint.exists():
            raise SystemExit(f"no checkpoint at {checkpoint}; nothing to export")
        accumulator = Accumulator.load(checkpoint)
        composite = accumulator.composite()
        coverage = mg.coverage_of(composite)
        print(f"  loaded {checkpoint.name}: {len(accumulator.done)} granules, "
              f"{int(composite.counts.sum()):,} soundings")
        print(f"  coverage {coverage.covered_cells}/{coverage.n_cells} "
              f"({100 * coverage.fraction:.2f}%)")
        if composite.covariates:
            report_covariate_coverage(composite)

        fits = {}
        if int(accumulator.harmonics.n.sum()) > 0:
            report_sampling_dates(accumulator.harmonics, args.spread_threshold)
            fits = report_seasonal(accumulator.harmonics, args.spread_threshold)
            compare_harmonics(fits)

        # The check runs BEFORE anything is written. A composite that does not
        # reproduce the committed methane is not a composite of the same thing,
        # and its covariates would be joined to a field that had moved.
        if args.verify_against:
            check = verify_methane(composite, Path(args.verify_against))
            print(f"\n  methane reproduction against {Path(args.verify_against).name}")
            for key in ("bias_corrected", "raw", "counts"):
                print(f"    max |difference| in {key:<16} {check[key]:.10g}")
            print(f"    covered cells {check['covered_cells_new']} "
                  f"vs {check['covered_cells_reference']}")
            print(f"    soundings     {check['soundings_new']:,} "
                  f"vs {check['soundings_reference']:,}")
            if any(check[k] != 0.0 for k in ("bias_corrected", "raw", "counts")):
                print("\n  STOPPING: the methane grids differ from the committed "
                      "composite. Nothing written.")
                return 3
            print("    identical; the re-run reproduces the committed methane exactly")

        if args.export:
            tif, csv_path = export(composite, Path(args.export),
                                   Path(args.export_csv) if args.export_csv else None)
            print(f"\n  wrote {tif}  ({tif.stat().st_size:,} B)")
            print(f"  wrote {csv_path}  ({csv_path.stat().st_size:,} B, "
                  f"{composite.spec.n_cells} rows plus a header)")
        if args.export_deseasonalised:
            if not fits:
                raise SystemExit("this checkpoint holds no seasonal statistics")
            order = args.export_harmonics or max(fits)
            if order not in fits:
                raise SystemExit(f"no fit at {order} harmonics; have {sorted(fits)}")
            chosen = fits[order]
            tif, csv_path = export_deseasonalised(
                chosen, accumulator.harmonics, composite.spec,
                Path(args.export_deseasonalised))
            flagged = int(chosen.poorly_identified.sum())
            print(f"\n  wrote {tif}  ({tif.stat().st_size:,} B, "
                  f"{len(chosen.terms) and 5} bands)")
            print(f"  wrote {csv_path}  ({csv_path.stat().st_size:,} B, "
                  f"{composite.spec.n_cells} rows plus a header)")
            print(f"  {flagged} cells flagged as poorly identified at "
                  f"{args.spread_threshold:.0f} days")
        if args.export_covariates:
            tif, csv_path = export_covariates(composite,
                                              Path(args.export_covariates))
            print(f"\n  wrote {tif}  ({tif.stat().st_size:,} B, "
                  f"{2 * len(composite.covariates)} bands)")
            print(f"  wrote {csv_path}  ({csv_path.stat().st_size:,} B, "
                  f"{composite.spec.n_cells} rows plus a header)")
        return 0

    print(f"stream      {stream}/{config['product_type']}")
    print(f"dates       {start} to {end}")
    print(f"grid        {spec.shape[0]} x {spec.shape[1]} = {spec.n_cells} cells "
          f"at {spec.resolution} degrees")
    print(f"qa          >= {config['qa_threshold']}")
    print(f"work dir    {work}   (holds ONE granule at a time)")
    print(f"checkpoint  {checkpoint}")
    print()

    print("  listing the mirror ...", flush=True)
    every = s5p.list_range(start, end, stream=stream,
                           product=config["product_type"],
                           base_url=config["base_url"], timeout=args.timeout)
    latest = s5p.latest_per_orbit(every)
    candidates = [g for g in latest
                  if s5p.intersects_box(g, box["west"], box["east"])]
    total_bytes = s5p.volume(candidates)
    print(f"  {len(every)} keys -> {len(latest)} after latest_per_orbit -> "
          f"{len(candidates)} candidates (SUPERSET; the filename carries no footprint)")
    print(f"  candidate volume {total_bytes:,} B ({human(total_bytes)})")

    if checkpoint.exists():
        accumulator = Accumulator.load(checkpoint)
        print(f"  resuming from {checkpoint.name}: {len(accumulator.done)} granules "
              f"already gridded, {int(accumulator.counts.sum()):,} soundings")
    else:
        accumulator = Accumulator(spec, float(config["qa_threshold"]), variables,
                                  covariates)
        print("  no checkpoint; starting from empty")
    if covariates:
        print(f"  gridding {len(covariates)} covariates alongside methane: "
              f"{', '.join(c.name for c in covariates)}")
        print("  covariates do not gate: a sounding with no albedo still "
              "contributes its methane")

    remaining = [g for g in candidates if g.name not in accumulator.done]
    if args.max_granules is not None:
        remaining = remaining[:args.max_granules]
    print(f"  {len(remaining)} granules to process this run")
    free = shutil.disk_usage(REPO).free
    print(f"  free space {human(free)}, floor {args.min_free_gb} GB")
    print(f"  peak disk bound: one granule plus the checkpoint, "
          f"asserted at {human(PEAK_DISK_ALLOWANCE_BYTES)}")

    if not args.run:
        print("\nplan only: nothing downloaded, nothing written. Pass --run with "
              "--max-granules or --max-hours to build.")
        return 0
    if args.max_granules is None and args.max_hours is None:
        print("\nrefusing to run without --max-granules or --max-hours. A full "
              "year is hundreds of granules and hours of transfer; the bound is "
              "required so an accidental invocation cannot start it.")
        return 2

    work.mkdir(parents=True, exist_ok=True)
    floor = args.min_free_gb * 1024 ** 3
    deadline = time.time() + args.max_hours * 3600 if args.max_hours else None

    t0 = time.perf_counter()
    done = with_data = 0
    fetched_bytes = 0
    peak_disk = 0
    stop_reason = "all granules processed"

    for index, granule in enumerate(remaining, 1):
        if deadline and time.time() > deadline:
            stop_reason = "time budget reached"
            break
        free = shutil.disk_usage(REPO).free
        if free < floor:
            stop_reason = f"free space {human(free)} below the {args.min_free_gb} GB floor"
            break

        peak_disk = max(peak_disk, assert_disk_bound(work))
        target = work / granule.name
        try:
            s5p.download_granule(granule, target, base_url=config["base_url"],
                                 timeout=args.timeout)
            fetched_bytes += granule.size
            soundings, contribution = mg.read_soundings(
                target, spec, qa_threshold=accumulator.qa_threshold,
                variables=variables, covariates=accumulator.covariates)
            accumulator.add(soundings, contribution)
            if contribution.soundings_in_box:
                with_data += 1
        except Exception as exc:                       # noqa: BLE001
            print(f"  [{index}/{len(remaining)}] {granule.name}: FAILED ({exc})",
                  flush=True)
        finally:
            if target.exists():
                target.unlink()
            part = target.with_suffix(target.suffix + ".part")
            if part.exists():
                part.unlink()

        peak_disk = max(peak_disk, assert_disk_bound(work))
        done += 1

        if done % args.checkpoint_every == 0 or index == len(remaining):
            accumulator.save(checkpoint)
        if done % 25 == 0 or index == len(remaining):
            elapsed = time.perf_counter() - t0
            rate = fetched_bytes / elapsed if elapsed else 0
            left = (len(remaining) - index) * (elapsed / max(index, 1))
            covered = int((accumulator.counts > 0).sum())
            print(f"  [{index}/{len(remaining)}] {done} done, {with_data} with data, "
                  f"{covered}/{spec.n_cells} cells ({100 * covered / spec.n_cells:.1f}%), "
                  f"{human(rate)}/s, elapsed {elapsed / 60:.1f} min, "
                  f"~{left / 60:.0f} min left", flush=True)

    accumulator.save(checkpoint)
    elapsed = time.perf_counter() - t0
    composite = accumulator.composite()
    coverage = mg.coverage_of(composite)

    print(f"\nstopped: {stop_reason}")
    print(f"  granules processed this run   {done}")
    print(f"  with in-box soundings         {with_data}")
    print(f"  downloaded                    {fetched_bytes:,} B ({human(fetched_bytes)})")
    print(f"  elapsed                       {elapsed / 60:.1f} min")
    if elapsed:
        print(f"  mean rate                     {human(fetched_bytes / elapsed)}/s")
    print(f"  peak working-directory bytes  {peak_disk:,} ({human(peak_disk)})")
    print(f"  checkpoint                    {checkpoint}")
    print(f"\n  coverage {coverage.covered_cells}/{coverage.n_cells} cells "
          f"({100 * coverage.fraction:.2f}%), median "
          f"{coverage.median_per_covered_cell} max {coverage.max_per_covered_cell}")
    print(f"  soundings by year: {coverage.soundings_by_year}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
