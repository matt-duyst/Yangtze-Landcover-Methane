"""Per-cell land-cover fractions on a regular analysis grid.

Every constraint encoded here was measured and is recorded in
notes/decisions.md. Four of them shape the arithmetic.

**The denominator is never the cell.** It is the part of the cell the raster
actually assessed. Anhui's rice rasters cover 86.1 percent of the province in
2017 to 2020 and 91.9 percent in 2021 to 2023, so a fraction taken over cell
area would understate rice in exactly the cells where the raster was clipped,
and would do so silently. :class:`CellFraction` therefore carries the assessed
area alongside the selected area and computes the ratio from those two, and
``coverage`` reports the assessed area as a share of the cell so a reader can
see which figures rest on partial assessment.

**Rice rasters must be masked by province first.** They declare no nodata and
their 0 means both genuine non-rice land and out-of-province background, and
between 23 and 60 percent of each file's zeros fall outside the province it is
named for. An unmasked rice fraction is wrong by roughly a factor of two.
:func:`accumulate_fraction` takes an optional mask geometry for this, and
``fraction_over_grid`` requires the caller to pass one explicitly rather than
defaulting to none, so the decision is visible at every call site. The mask
must be the province a file is named for and not the union of all four: the
rasters' bounding boxes overlap, so a union mask assesses the shared ground
once per file and inflates both the numerator and the denominator.

**Pixels are weighted by ground area, not counted.** Same authalic-sphere row
areas as ``src.landcover``: a pixel at 35 north covers less ground than one at
27 north and a count would silently weight the north of the box too heavily.

**A cell with no methane cannot become a row.** The 96 uncovered cells are a
coherent systematic gap over mountainous southern Zhejiang and the coastline,
not scatter, and interpolating them would extrapolate from bright flat terrain
into dark steep terrain where the instrument is known to fail. :class:`CellRow`
takes the sounding count as a required field and refuses to construct with a
count of zero, so an excluded cell cannot be built and then filtered out later.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np
import rasterio
from rasterio.windows import Window
from shapely.geometry import box
from shapely.geometry.base import BaseGeometry

from src.landcover.geometry import (
    CHINA_ALBERS,
    row_pixel_areas_m2,
    zone_mask,
)
from src.landcover.selectors import Selector
from src.methane.grid import GridSpec

DEFAULT_BLOCK_ROWS = 1024


class GridError(RuntimeError):
    """Base class for failures this package raises deliberately."""


class UnobservedCell(GridError):
    """A row was requested for a cell with no methane soundings."""


@dataclass(frozen=True)
class CellFraction:
    """A selected area within one cell, and the area that was assessed.

    ``fraction`` divides by ``assessed_km2`` and never by the cell, because the
    raster may not have covered the whole cell. ``coverage`` is what says so.
    """

    selected_km2: float
    assessed_km2: float
    cell_km2: float

    @property
    def fraction(self) -> float | None:
        """Selected over assessed. None when nothing was assessed."""
        if self.assessed_km2 <= 0:
            return None
        return self.selected_km2 / self.assessed_km2

    @property
    def coverage(self) -> float:
        """Assessed area as a share of the cell."""
        if self.cell_km2 <= 0:
            return 0.0
        return self.assessed_km2 / self.cell_km2


@dataclass(frozen=True)
class CellRow:
    """One covered methane cell with its land-cover fractions.

    Construction fails for a cell with no soundings. That is the exclusion of
    the 96 uncovered cells, enforced by the type rather than by a filter that
    someone can forget to apply.
    """

    row: int
    col: int
    centre_lat: float
    centre_lon: float
    sounding_count: int
    ch4_bias_corrected: float
    ch4_raw: float
    impervious: CellFraction
    rice_single: CellFraction
    rice_combined: CellFraction
    province_shares: Mapping[str, float]

    def __post_init__(self):
        if self.sounding_count <= 0:
            raise UnobservedCell(
                f"cell ({self.row}, {self.col}) has {self.sounding_count} soundings. "
                f"Uncovered methane cells are a systematic gap and are excluded, "
                f"not interpolated; a row cannot be built for one.")

    @property
    def province_total(self) -> float:
        return float(sum(self.province_shares.values()))

    @property
    def outside_provinces(self) -> float:
        return max(0.0, 1.0 - self.province_total)

    def as_dict(self) -> dict:
        out = {
            "centre_lat": round(self.centre_lat, 4),
            "centre_lon": round(self.centre_lon, 4),
            "sounding_count": self.sounding_count,
            "ch4_bias_corrected_ppb": round(self.ch4_bias_corrected, 2),
            "ch4_raw_ppb": round(self.ch4_raw, 2),
            "impervious_fraction": _r(self.impervious.fraction, 6),
            "impervious_coverage": round(self.impervious.coverage, 4),
            "rice_fraction_single": _r(self.rice_single.fraction, 6),
            "rice_fraction_combined": _r(self.rice_combined.fraction, 6),
            "rice_coverage": round(self.rice_single.coverage, 4),
            "province_share_outside": round(self.outside_provinces, 4),
        }
        for name, share in sorted(self.province_shares.items()):
            out[f"share_{name.lower()}"] = round(share, 4)
        return out


def _r(value, digits):
    return "" if value is None else round(value, digits)


def accumulate_fraction(
    raster: str | Path,
    spec: GridSpec,
    selector: Selector,
    *,
    mask_geometry: BaseGeometry | None,
    clip_bounds: tuple[float, float, float, float] | None = None,
    block_rows: int = DEFAULT_BLOCK_ROWS,
    selected: np.ndarray | None = None,
    assessed: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Add one raster's contribution to per-cell selected and assessed areas.

    Returns ``(selected_m2, assessed_m2)``, both on the analysis grid, so
    several rasters can be accumulated into the same pair before any division.
    Dividing per raster and averaging afterwards would weight a raster that
    assessed a sliver of a cell equally with one that assessed all of it.

    ``mask_geometry`` restricts what counts as assessed. Pass the province
    union for products whose zero means both a real absence and out-of-area
    background; pass None only for a product where zero is meaningful
    everywhere, and say which in the caller.
    """
    selected_m2 = np.zeros(spec.shape, dtype="float64") if selected is None else selected
    assessed_m2 = np.zeros(spec.shape, dtype="float64") if assessed is None else assessed

    with rasterio.open(raster) as source:
        transform = source.transform
        height, width = source.height, source.width
        pixel_w, pixel_h = abs(transform.a), abs(transform.e)
        row_areas = row_pixel_areas_m2(transform.f, pixel_h, pixel_w, height)

        centre_x = transform.c + (np.arange(width) + 0.5) * transform.a
        centre_y = transform.f + (np.arange(height) + 0.5) * transform.e

        # Cell indices are arithmetic, not rasterised: the analysis grid is a
        # regular lattice, so a pixel's cell follows from its centre.
        col_index = np.floor((centre_x - spec.west) / spec.resolution).astype("int64")
        row_index = np.floor((spec.north - centre_y) / spec.resolution).astype("int64")
        east, south = lattice_edges(spec)
        col_ok = (centre_x >= spec.west) & (centre_x < east)
        row_ok = (centre_y > south) & (centre_y <= spec.north)
        if clip_bounds is not None:
            col_ok &= (centre_x >= clip_bounds[0]) & (centre_x < clip_bounds[2])
            row_ok &= (centre_y > clip_bounds[1]) & (centre_y <= clip_bounds[3])
        if not col_ok.any() or not row_ok.any():
            return selected_m2, assessed_m2

        keep_cols = np.flatnonzero(col_ok)
        c0, c1 = int(keep_cols[0]), int(keep_cols[-1]) + 1
        cols_in = col_index[c0:c1]

        for start in range(0, height, block_rows):
            rows = min(block_rows, height - start)
            if not row_ok[start:start + rows].any():
                continue
            window = Window(c0, start, c1 - c0, rows)
            data = source.read(1, window=window)
            valid_rows = row_ok[start:start + rows]

            if mask_geometry is not None:
                window_transform = rasterio.windows.transform(window, transform)
                inside = zone_mask(mask_geometry, (rows, c1 - c0), window_transform)
            else:
                inside = np.ones((rows, c1 - c0), dtype=bool)
            inside &= valid_rows[:, None]
            if not inside.any():
                continue

            areas = np.broadcast_to(row_areas[start:start + rows, None],
                                    (rows, c1 - c0))
            cell_rows = np.broadcast_to(row_index[start:start + rows, None],
                                        (rows, c1 - c0))
            cell_cols = np.broadcast_to(cols_in[None, :], (rows, c1 - c0))

            np.add.at(assessed_m2, (cell_rows[inside], cell_cols[inside]),
                      areas[inside])
            picked = selector(data) & inside
            if picked.any():
                np.add.at(selected_m2, (cell_rows[picked], cell_cols[picked]),
                          areas[picked])
    return selected_m2, assessed_m2


def lattice_edges(spec: GridSpec) -> tuple[float, float]:
    """The east and south edges the grid's cells actually reach.

    ``GridSpec`` rounds its shape, so a box whose width is not a whole number
    of cells has a lattice that does not occupy its declared bounds. The study
    grid used to be one: 122.6 minus 114.8 is 31.2 cells at 0.25 degrees,
    rounded to 31, so the easternmost cell ended at 122.55 and the last 0.05
    degrees of the declared box had no column. The configuration now declares
    122.55 and 26.95 so the live grid has no remainder, and this function
    returns the declared edges unchanged. It is kept and still called because
    nothing enforces that a future box or cell size divides evenly. ``GridSpec.cell_of`` clips soundings there into the last
    column; this package filters instead, because a land-cover pixel outside
    the lattice belongs to no cell and folding it into the edge cell would
    inflate that cell's assessed area with ground it does not cover.
    """
    return (spec.west + spec.n_cols * spec.resolution,
            spec.north - spec.n_rows * spec.resolution)


def cell_areas_m2(spec: GridSpec) -> np.ndarray:
    """Ground area of every cell, on the same authalic sphere."""
    return np.repeat(
        row_pixel_areas_m2(spec.north, spec.resolution, spec.resolution,
                           spec.shape[0])[:, None],
        spec.shape[1], axis=1)


def fraction_over_grid(
    rasters: Iterable[str | Path],
    spec: GridSpec,
    selector: Selector,
    *,
    mask_geometry,
    clip_bounds_of=None,
    block_rows: int = DEFAULT_BLOCK_ROWS,
) -> list[list[CellFraction]]:
    """Per-cell fractions from a set of rasters covering the grid.

    ``mask_geometry`` is a geometry, None, or a callable mapping a raster path
    to one of those. The callable form is what the rice rasters need: they are
    distributed one per province and their bounding boxes overlap, so masking
    every file by the union of the four provinces would assess the overlaps
    twice and can push a cell's assessed area to nearly three times the cell.
    Each file must be masked by the province it is named for.

    ``clip_bounds_of`` is an optional callable mapping a raster path to the
    bounds its pixels should be restricted to, for products that ship
    overlapping tiles. GAIA writes a 30 m merge buffer around every tile, so
    without this the shared edges are counted twice. It solves the same problem
    for a product whose overlaps are rectangular and known from the filename;
    the rice rasters need a polygon and so use the mask instead.
    """
    selected = np.zeros(spec.shape, dtype="float64")
    assessed = np.zeros(spec.shape, dtype="float64")
    for raster in rasters:
        clip = clip_bounds_of(raster) if clip_bounds_of else None
        mask = mask_geometry(raster) if callable(mask_geometry) else mask_geometry
        selected, assessed = accumulate_fraction(
            raster, spec, selector, mask_geometry=mask,
            clip_bounds=clip, block_rows=block_rows,
            selected=selected, assessed=assessed)
    cell_km2 = cell_areas_m2(spec) / 1e6
    return [
        [CellFraction(selected_km2=selected[r, c] / 1e6,
                      assessed_km2=assessed[r, c] / 1e6,
                      cell_km2=float(cell_km2[r, c]))
         for c in range(spec.shape[1])]
        for r in range(spec.shape[0])
    ]


def value_sum_over_grid(
    values: np.ndarray,
    transform,
    spec: GridSpec,
    *,
    unit_scale: float = 1.0,
    crs: str = CHINA_ALBERS,
) -> list[list[CellFraction]]:
    """Per-cell fractions from a product whose values are already areas.

    GloRice stores hectares of rice per 5-arcmin cell rather than a class code,
    so its contribution to an analysis cell is a share of a value, not a count
    of pixels. At 5 arcmin one source cell is about 9 km across against a 25 km
    analysis cell, so roughly nine of them fall in each cell and the ones on the
    edge are cut. Binning by source-cell centre, which is what
    :func:`accumulate_fraction` does and which is right at 10 and 30 m, would
    quantise each analysis cell to whole ninths and misplace up to a third of a
    cell's width at every edge. Each source cell is therefore apportioned by the
    share of its ground area inside the analysis cell, measured in an equal-area
    projection, reusing ``fractional_weights``.

    NaN is treated as zero. In GloRice it means no rice rather than no
    measurement, which is a value and not an absence, so a cell of open sea
    correctly gets a rice fraction of zero rather than a blank. That differs
    from the NESDC rasters, where zero is ambiguous and a blank is the honest
    answer, and it is why the two rice sources cover different numbers of cells.
    """
    from src.landcover.geometry import fractional_weights

    values = np.nan_to_num(np.asarray(values, dtype="float64"),
                           nan=0.0, posinf=0.0, neginf=0.0)
    height, width = values.shape
    left, top = transform.c, transform.f
    right = left + width * abs(transform.a)
    bottom = top - height * abs(transform.e)
    extent = box(left, bottom, right, top)

    cell_km2 = cell_areas_m2(spec) / 1e6
    out: list[list[CellFraction]] = []
    for r in range(spec.shape[0]):
        north = spec.north - r * spec.resolution
        row: list[CellFraction] = []
        for c in range(spec.shape[1]):
            west = spec.west + c * spec.resolution
            cell = box(west, north - spec.resolution, west + spec.resolution, north)
            overlap = cell.intersection(extent)
            whole = float(cell_km2[r, c])
            if overlap.is_empty:
                row.append(CellFraction(0.0, 0.0, whole))
                continue
            rows_i, cols_i, share = fractional_weights(overlap, transform,
                                                       (height, width), crs=crs)
            selected = (float((values[rows_i, cols_i] * share).sum()) * unit_scale
                        if rows_i.size else 0.0)
            assessed = whole * (overlap.area / cell.area) if cell.area else 0.0
            row.append(CellFraction(selected_km2=selected, assessed_km2=assessed,
                                    cell_km2=whole))
        out.append(row)
    return out


def province_shares(
    spec: GridSpec,
    provinces: Mapping[str, BaseGeometry],
    *,
    crs: str = CHINA_ALBERS,
) -> list[list[dict[str, float]]]:
    """Share of each cell lying inside each province.

    A cell at 0.25 degrees is roughly 25 km across and provincial boundaries
    run through many of them, so attribution is by area share rather than by a
    single winning province. Shares are measured in an equal-area projection
    and need not sum to one: the remainder is sea, or a province outside the
    study set, and is reported by ``CellRow.outside_provinces``.
    """
    import geopandas as gpd

    cells, index = [], []
    for r in range(spec.shape[0]):
        north = spec.north - r * spec.resolution
        for c in range(spec.shape[1]):
            west = spec.west + c * spec.resolution
            cells.append(box(west, north - spec.resolution,
                             west + spec.resolution, north))
            index.append((r, c))
    grid = gpd.GeoSeries(cells, crs="EPSG:4326").to_crs(crs)
    whole = grid.area.values

    shares = [[dict() for _ in range(spec.shape[1])] for _ in range(spec.shape[0])]
    for name, geometry in provinces.items():
        projected = gpd.GeoSeries([geometry], crs="EPSG:4326").to_crs(crs).iloc[0]
        overlap = grid.intersection(projected).area.values
        part = np.where(whole > 0, overlap / whole, 0.0)
        for (r, c), value in zip(index, part):
            if value > 0:
                shares[r][c][name] = float(value)
    return shares
