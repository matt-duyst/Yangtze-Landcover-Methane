"""Zones, coverage, and equal-area pixel weights.

Two measured facts from this project's data drive everything here.

First, these rasters are plain rectangles around each province, not clipped to
the province. Between 23 and 60 percent of the zeros in an NESDC rice file fall
outside the province it is named for, so a statistic taken over the raster
extent is wrong by roughly a factor of two for three of the four study
provinces. Every count must therefore pass through a polygon mask.

Second, the polygon is not always the right denominator either. Anhui's rice
rasters cover 86.1 percent of the province in 2017 to 2020 and 91.9 percent in
2021 to 2023, so dividing by the polygon area understates a fraction by the
part of the province the raster never saw. The denominator is the intersection
of the polygon with that year's raster extent, and the ratio of the two is
reported so a reader can see which figures rest on partial coverage.

Areas are computed on the authalic sphere rather than by projecting, because a
raster in geographic coordinates has rows of constant latitude span and the
exact area of such a row is analytic. For a row between latitudes p1 and p2
spanning dlon of longitude, one pixel covers

    R^2 * dlon * (sin(p2) - sin(p1))

which is exact for a sphere of equal surface area to the ellipsoid. This is the
method that recovered the four provincial polygon areas to within 0.13 percent
from 30 m GAIA rasters.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

import geopandas as gpd
import numpy as np
from shapely.geometry import box
from shapely.geometry.base import BaseGeometry

#: Radius of the sphere with the same surface area as the WGS84 ellipsoid.
#: The standard choice for equal-area work; EPSG:6933 and friends use it.
AUTHALIC_RADIUS_M = 6371007.181

#: China Albers Equal Area, used for polygon-versus-polygon area comparisons.
#: Not used to measure pixels; those are done analytically on the sphere.
CHINA_ALBERS = (
    "+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 "
    "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
)


@dataclass(frozen=True)
class ZoneCoverage:
    """How much of a zone a raster actually sees.

    ``zone_area_km2`` is the whole polygon. ``covered_area_km2`` is the part
    inside the raster extent, and is the denominator for any fraction.
    ``coverage`` is their ratio, carried so partial coverage is visible rather
    than silently folded into a result.
    """

    zone: str
    zone_area_km2: float
    covered_area_km2: float

    @property
    def coverage(self) -> float:
        if self.zone_area_km2 <= 0:
            return 0.0
        return self.covered_area_km2 / self.zone_area_km2


def load_zones(path: str | Path, *, name_field: str = "name") -> dict[str, BaseGeometry]:
    """Read zone polygons from a vector file, keyed by ``name_field``."""
    frame = gpd.read_file(path)
    if name_field not in frame.columns:
        raise KeyError(
            f"{path} has no field {name_field!r}; available: {list(frame.columns)}"
        )
    return {row[name_field]: row.geometry for _, row in frame.iterrows()}


def _equal_area_km2(geometry: BaseGeometry, *, crs: str = CHINA_ALBERS) -> float:
    if geometry.is_empty:
        return 0.0
    return gpd.GeoSeries([geometry], crs="EPSG:4326").to_crs(crs).area.iloc[0] / 1e6


def raster_bounds_geometry(bounds) -> BaseGeometry:
    """The raster's extent as a polygon in EPSG:4326."""
    left, bottom, right, top = bounds
    return box(left, bottom, right, top)


def coverage_for(
    zone: str,
    geometry: BaseGeometry,
    bounds,
    *,
    crs: str = CHINA_ALBERS,
) -> ZoneCoverage:
    """Measure how much of ``geometry`` lies inside a raster's ``bounds``."""
    extent = raster_bounds_geometry(bounds)
    return ZoneCoverage(
        zone=zone,
        zone_area_km2=_equal_area_km2(geometry, crs=crs),
        covered_area_km2=_equal_area_km2(geometry.intersection(extent), crs=crs),
    )


def row_pixel_areas_m2(
    top_lat: float,
    pixel_height_deg: float,
    pixel_width_deg: float,
    n_rows: int,
    *,
    radius_m: float = AUTHALIC_RADIUS_M,
) -> np.ndarray:
    """Ground area of one pixel in each raster row, in square metres.

    ``pixel_height_deg`` is positive downward, matching a north-up raster.
    Returns one value per row: within a row every pixel has the same area, and
    between rows the area shrinks toward the poles.
    """
    if n_rows <= 0:
        return np.zeros(0, dtype="float64")
    rows = np.arange(n_rows, dtype="float64")
    upper = np.radians(top_lat - rows * pixel_height_deg)
    lower = np.radians(top_lat - (rows + 1.0) * pixel_height_deg)
    dlon = np.radians(abs(pixel_width_deg))
    return (radius_m ** 2) * dlon * (np.sin(upper) - np.sin(lower))


def zone_mask(geometry: BaseGeometry, shape, transform) -> np.ndarray:
    """Boolean mask of the pixels whose centres fall inside ``geometry``."""
    from rasterio.features import rasterize

    return rasterize(
        [(geometry, 1)],
        out_shape=shape,
        transform=transform,
        fill=0,
        dtype="uint8",
        all_touched=False,
    ).astype(bool)


def fractional_weights(
    geometry: BaseGeometry,
    transform,
    shape,
    *,
    crs: str = CHINA_ALBERS,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fraction of each grid cell that lies inside ``geometry``.

    Returns ``(rows, cols, fractions)`` for the cells with a non-zero share.

    A centre-in-polygon mask is adequate at 10 or 30 m, where a boundary pixel
    is a rounding error, and inadequate at 5 arcmin, where one cell is roughly
    9 km across and a province boundary cuts through many of them. Products
    whose values are already areas, such as GloRice's hectares per cell, must
    be apportioned by the share of the cell inside the zone rather than counted
    whole or dropped whole.

    Shares are measured in an equal-area projection so that a cell straddling
    the boundary contributes in proportion to ground area, not to degrees.
    """
    height, width = shape
    left, top = transform.c, transform.f
    pixel_w, pixel_h = abs(transform.a), abs(transform.e)

    minx, miny, maxx, maxy = geometry.bounds
    col0 = max(0, int(np.floor((minx - left) / pixel_w)))
    col1 = min(width, int(np.ceil((maxx - left) / pixel_w)))
    row0 = max(0, int(np.floor((top - maxy) / pixel_h)))
    row1 = min(height, int(np.ceil((top - miny) / pixel_h)))
    if col1 <= col0 or row1 <= row0:
        empty = np.zeros(0, dtype="int64")
        return empty, empty, np.zeros(0, dtype="float64")

    cells, rows, cols = [], [], []
    for row in range(row0, row1):
        cell_top = top - row * pixel_h
        cell_bottom = cell_top - pixel_h
        for col in range(col0, col1):
            cell_left = left + col * pixel_w
            cells.append(box(cell_left, cell_bottom, cell_left + pixel_w, cell_top))
            rows.append(row)
            cols.append(col)

    grid = gpd.GeoSeries(cells, crs="EPSG:4326").to_crs(crs)
    zone = gpd.GeoSeries([geometry], crs="EPSG:4326").to_crs(crs).iloc[0]
    whole = grid.area.values
    inside = grid.intersection(zone).area.values
    share = np.where(whole > 0, inside / whole, 0.0)

    keep = share > 0
    return (
        np.asarray(rows)[keep],
        np.asarray(cols)[keep],
        share[keep],
    )
