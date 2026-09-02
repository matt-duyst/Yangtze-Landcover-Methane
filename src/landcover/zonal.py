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
