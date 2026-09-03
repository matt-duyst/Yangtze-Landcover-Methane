"""Per-zone areas from a land-cover raster.

The one entry point is :func:`zonal_area`. It returns :class:`ZonalResult`
objects and nothing else, which is how the coverage requirement is enforced
rather than merely documented: there is no way to obtain an area from this
module without also obtaining the coverage fraction that says how much of the
zone the raster actually saw.

The raster is read in row blocks, so a three-gigapixel provincial file is
processed without loading it, and the zone mask is rasterised block by block to
match.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import numpy as np
import rasterio
from rasterio.windows import Window
from shapely.geometry.base import BaseGeometry

from src.landcover.geometry import (
    CHINA_ALBERS,
    ZoneCoverage,
    coverage_for,
    row_pixel_areas_m2,
    zone_mask,
)
from src.landcover.selectors import Selector

DEFAULT_BLOCK_ROWS = 2048


@dataclass(frozen=True)
class ZonalResult:
    """A selected area within one zone, with the coverage it rests on.

    ``area_km2`` is the ground area of the selected pixels inside the zone.
    ``covered_area_km2`` is the part of the zone the raster saw, and is the
    denominator of ``fraction``. ``coverage`` is that part over the whole zone.

    A result with ``coverage`` well below 1.0 is not wrong, but it describes
    less than the zone, and ``fraction`` is a fraction of what was seen rather
    than of the zone.
    """

    zone: str
    selection: str
    area_km2: float
    pixel_count: int
    zone_area_km2: float
    covered_area_km2: float

    @property
    def coverage(self) -> float:
        if self.zone_area_km2 <= 0:
            return 0.0
        return self.covered_area_km2 / self.zone_area_km2

    @property
    def fraction(self) -> float:
        """Selected area over the area the raster actually saw.

        Deliberately not over ``zone_area_km2``. Dividing by the whole zone
        when the raster covers 86 percent of it understates the fraction by
        the part that was never observed.
        """
        if self.covered_area_km2 <= 0:
            return 0.0
        return self.area_km2 / self.covered_area_km2

    def as_dict(self) -> dict:
        return {
            "zone": self.zone,
            "selection": self.selection,
            "area_km2": self.area_km2,
            "pixel_count": self.pixel_count,
            "zone_area_km2": self.zone_area_km2,
            "covered_area_km2": self.covered_area_km2,
            "coverage": self.coverage,
            "fraction": self.fraction,
        }


def zonal_area(
    raster: str | Path,
    zones: Mapping[str, BaseGeometry],
    selector: Selector,
    *,
    clip_bounds: tuple[float, float, float, float] | None = None,
    block_rows: int = DEFAULT_BLOCK_ROWS,
    area_crs: str = CHINA_ALBERS,
) -> list[ZonalResult]:
    """Ground area of the selected pixels within each zone.

    ``zones`` maps a name to a polygon in EPSG:4326. ``selector`` states which
    pixel values count; nothing is inferred from the raster's nodata, which for
    some of these products is not set at all.

    ``clip_bounds`` restricts counting to pixels whose centres fall inside a
    given ``(left, bottom, right, top)``. Some products ship overlapping tiles
    on purpose: GAIA writes a 30 m buffer around each tile so neighbours
    mosaic seamlessly, which means summing whole tiles double-counts every
    shared edge. Passing each tile's nominal extent removes the overlap. The
    effective extent, and therefore the coverage denominator, is the raster
    bounds intersected with these.

    Zones that do not intersect the raster are returned with zero area and zero
    coverage rather than omitted, so a caller iterating years gets one row per
    zone per year whether or not that year's raster reached the zone.
    """
    raster = Path(raster)
    with rasterio.open(raster) as source:
        transform = source.transform
        height, width = source.height, source.width
        bounds = tuple(source.bounds)
        if clip_bounds is not None:
            bounds = (
                max(bounds[0], clip_bounds[0]),
                max(bounds[1], clip_bounds[1]),
                min(bounds[2], clip_bounds[2]),
                min(bounds[3], clip_bounds[3]),
            )

        coverages: dict[str, ZoneCoverage] = {
            name: coverage_for(name, geometry, bounds, crs=area_crs)
            for name, geometry in zones.items()
        }

        pixel_height = abs(transform.e)
        pixel_width = abs(transform.a)
        row_areas = row_pixel_areas_m2(transform.f, pixel_height, pixel_width, height)

        # Pixel centres, used both for the clip and for nothing else; the zone
        # mask does its own centre test via rasterize(all_touched=False).
        centre_x = transform.c + (np.arange(width) + 0.5) * transform.a
        centre_y = transform.f + (np.arange(height) + 0.5) * transform.e
        if clip_bounds is not None:
            keep_col = (centre_x >= clip_bounds[0]) & (centre_x < clip_bounds[2])
            keep_row = (centre_y > clip_bounds[1]) & (centre_y <= clip_bounds[3])
        else:
            keep_col = np.ones(width, dtype=bool)
            keep_row = np.ones(height, dtype=bool)

        totals_m2 = {name: 0.0 for name in zones}
        counts = {name: 0 for name in zones}

        active = [
            name for name, cover in coverages.items() if cover.covered_area_km2 > 0
        ]

        for start in range(0, height, block_rows):
            rows = min(block_rows, height - start)
            if not keep_row[start:start + rows].any():
                continue
            window = Window(0, start, width, rows)
            block = source.read(1, window=window)
            chosen = selector(block)
            chosen &= keep_row[start:start + rows, None] & keep_col[None, :]
            if not chosen.any():
                continue
            window_transform = rasterio.windows.transform(window, transform)
            areas = np.broadcast_to(
                row_areas[start:start + rows, None], (rows, width)
            )
            for name in active:
                mask = zone_mask(zones[name], (rows, width), window_transform)
                if not mask.any():
                    continue
                picked = chosen & mask
                if not picked.any():
                    continue
                totals_m2[name] += float(areas[picked].sum())
                counts[name] += int(picked.sum())

    return [
        ZonalResult(
            zone=name,
            selection=selector.description,
            area_km2=totals_m2[name] / 1e6,
            pixel_count=counts[name],
            zone_area_km2=coverages[name].zone_area_km2,
            covered_area_km2=coverages[name].covered_area_km2,
        )
        for name in zones
    ]


def zonal_value_sum(
    values: np.ndarray,
    transform,
    zones: Mapping[str, BaseGeometry],
    *,
    unit_scale: float = 1.0,
    label: str = "sum",
    area_crs: str = CHINA_ALBERS,
) -> list[ZonalResult]:
    """Area-weighted sum of cell values within each zone.

    For products whose cell values are already areas rather than class codes.
    GloRice stores hectares of rice per 5-arcmin cell, so a provincial total is
    the sum of those values apportioned by the share of each cell inside the
    province, not a count of cells and not an area computed from the grid.

    ``unit_scale`` converts the summed values to square kilometres: hectares
    are 0.01 km2 each. ``values`` may contain NaN, which is treated as zero,
    because GloRice writes NaN where there is no rice rather than declaring a
    fill value.

    Returns the same :class:`ZonalResult` type as :func:`zonal_area`, so a
    coverage fraction accompanies every figure here too. ``pixel_count`` is the
    number of cells contributing a non-zero value, which for a fractional
    weighting is a diagnostic rather than an area.
    """
    from src.landcover.geometry import fractional_weights

    values = np.asarray(values, dtype="float64")
    height, width = values.shape
    left, top = transform.c, transform.f
    right = left + width * abs(transform.a)
    bottom = top - height * abs(transform.e)
    bounds = (left, bottom, right, top)

    finite = np.nan_to_num(values, nan=0.0, posinf=0.0, neginf=0.0)

    results = []
    for name, geometry in zones.items():
        cover = coverage_for(name, geometry, bounds, crs=area_crs)
        rows, cols, share = fractional_weights(geometry, transform, (height, width),
                                               crs=area_crs)
        if rows.size == 0:
            total, count = 0.0, 0
        else:
            picked = finite[rows, cols]
            total = float((picked * share).sum())
            count = int((picked != 0).sum())
        results.append(
            ZonalResult(
                zone=name,
                selection=label,
                area_km2=total * unit_scale,
                pixel_count=count,
                zone_area_km2=cover.zone_area_km2,
                covered_area_km2=cover.covered_area_km2,
            )
        )
    return results


@dataclass(frozen=True)
class ZonalHistogram:
    """Ground area of every distinct pixel value within one zone.

    A year-of-change product encodes a whole time series in one band, so a
    37-year series would otherwise mean 37 passes over the same raster. One
    histogram answers every threshold: cumulative extent for a year is the sum
    of the entries at or above that year's cutoff.

    ``area_km2_by_value`` and ``count_by_value`` are keyed by the raw pixel
    value. Coverage travels with the histogram for the same reason it travels
    with :class:`ZonalResult`.
    """

    zone: str
    area_km2_by_value: dict[int, float]
    count_by_value: dict[int, int]
    zone_area_km2: float
    covered_area_km2: float

    @property
    def coverage(self) -> float:
        if self.zone_area_km2 <= 0:
            return 0.0
        return self.covered_area_km2 / self.zone_area_km2

    def area_where(self, selector: Selector) -> float:
        """Area of the values this selector accepts."""
        if not self.area_km2_by_value:
            return 0.0
        values = np.array(sorted(self.area_km2_by_value), dtype="int64")
        chosen = selector(values)
        return float(sum(self.area_km2_by_value[int(v)] for v in values[chosen]))

    def result_for(self, selector: Selector) -> ZonalResult:
        """The :class:`ZonalResult` a selector would have produced."""
        values = np.array(sorted(self.area_km2_by_value), dtype="int64")
        chosen = selector(values) if values.size else np.zeros(0, dtype=bool)
        picked = values[chosen] if values.size else values
        return ZonalResult(
            zone=self.zone,
            selection=selector.description,
            area_km2=float(sum(self.area_km2_by_value[int(v)] for v in picked)),
            pixel_count=int(sum(self.count_by_value[int(v)] for v in picked)),
            zone_area_km2=self.zone_area_km2,
            covered_area_km2=self.covered_area_km2,
        )


def zonal_histogram(
    raster: str | Path,
    zones: Mapping[str, BaseGeometry],
    *,
    clip_bounds: tuple[float, float, float, float] | None = None,
    block_rows: int = DEFAULT_BLOCK_ROWS,
    area_crs: str = CHINA_ALBERS,
) -> dict[str, ZonalHistogram]:
    """Area of every distinct pixel value within each zone, in one pass.

    Same masking, clipping and equal-area weighting as :func:`zonal_area`; the
    difference is only that nothing is selected here, so one read serves any
    number of later selections.
    """
    raster = Path(raster)
    with rasterio.open(raster) as source:
        transform = source.transform
        height, width = source.height, source.width
        bounds = tuple(source.bounds)
        if clip_bounds is not None:
            bounds = (
                max(bounds[0], clip_bounds[0]), max(bounds[1], clip_bounds[1]),
                min(bounds[2], clip_bounds[2]), min(bounds[3], clip_bounds[3]),
            )

        coverages = {
            name: coverage_for(name, geometry, bounds, crs=area_crs)
            for name, geometry in zones.items()
        }
        row_areas = row_pixel_areas_m2(
            transform.f, abs(transform.e), abs(transform.a), height)

        centre_x = transform.c + (np.arange(width) + 0.5) * transform.a
        centre_y = transform.f + (np.arange(height) + 0.5) * transform.e
        if clip_bounds is not None:
            keep_col = (centre_x >= clip_bounds[0]) & (centre_x < clip_bounds[2])
            keep_row = (centre_y > clip_bounds[1]) & (centre_y <= clip_bounds[3])
        else:
            keep_col = np.ones(width, dtype=bool)
            keep_row = np.ones(height, dtype=bool)

        areas: dict[str, dict[int, float]] = {n: {} for n in zones}
        counts: dict[str, dict[int, int]] = {n: {} for n in zones}
        active = [n for n, c in coverages.items() if c.covered_area_km2 > 0]

        for start in range(0, height, block_rows):
            rows = min(block_rows, height - start)
            if not keep_row[start:start + rows].any():
                continue
            window = Window(0, start, width, rows)
            block = source.read(1, window=window)
            window_transform = rasterio.windows.transform(window, transform)
            in_clip = keep_row[start:start + rows, None] & keep_col[None, :]
            row_area = np.broadcast_to(row_areas[start:start + rows, None], (rows, width))
            for name in active:
                mask = zone_mask(zones[name], (rows, width), window_transform) & in_clip
                if not mask.any():
                    continue
                vals = block[mask]
                ars = row_area[mask]
                for value in np.unique(vals):
                    key = int(value)
                    hit = vals == value
                    areas[name][key] = areas[name].get(key, 0.0) + float(ars[hit].sum())
                    counts[name][key] = counts[name].get(key, 0) + int(hit.sum())

    return {
        name: ZonalHistogram(
            zone=name,
            area_km2_by_value={k: v / 1e6 for k, v in areas[name].items()},
            count_by_value=dict(counts[name]),
            zone_area_km2=coverages[name].zone_area_km2,
            covered_area_km2=coverages[name].covered_area_km2,
        )
        for name in zones
    }
