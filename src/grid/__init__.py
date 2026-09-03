"""Joining land cover onto the methane analysis grid.

The methane grid is the target: 0.25 degrees, 33 by 31 cells. Land cover comes
from 10 m and 30 m rasters, so the join is an aggregation of tens of millions of
pixels into a thousand cells.

This is a different shape of problem from ``src.landcover``, which aggregates
into four province polygons, and it needs different machinery rather than the
same machinery called more times. A province is an arbitrary polygon and must
be rasterised to be used. A grid cell is not arbitrary: the analysis grid is a
regular lattice aligned to whole fractions of a degree, and the rasters are
regular lattices in the same coordinate system, so the cell a pixel belongs to
is integer arithmetic on its coordinates. Rasterising 1,023 cell polygons
against every block of every raster would cost a thousand rasterisations per
block; computing ``floor((north - lat) / resolution)`` costs one subtraction.
That is the whole reason this package exists separately.

What is reused rather than rewritten: ``GridSpec.cell_of`` for the binning,
``row_pixel_areas_m2`` for equal-area weighting, ``zone_mask`` for the province
masking, and the selector protocol from ``src.landcover.selectors`` so
cumulative thresholding and class membership work here exactly as they do
there.
"""

from src.grid.cells import (  # noqa: F401
    CellFraction,
    CellRow,
    accumulate_fraction,
    fraction_over_grid,
    lattice_edges,
    province_shares,
    value_sum_over_grid,
)
