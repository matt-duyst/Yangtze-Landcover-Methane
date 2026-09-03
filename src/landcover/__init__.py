"""Provincial statistics from land-cover rasters.

Three modules, split so that each knows as little as possible about the others:

``geometry``
    Zones, the polygon-raster intersection, coverage, and equal-area pixel
    weights. Knows nothing about pixel values.

``selectors``
    Which pixel values count. Knows nothing about geography.

``zonal``
    Composes the two into per-zone areas. The only module that opens a raster
    and the only one that returns a result.

The split exists because the two datasets this must serve encode themselves
incompatibly. GAIA stores the year a pixel became impervious and needs
cumulative thresholding; the NESDC rice rasters store discrete classes and need
set membership. Neither is named anywhere in this package. A caller supplies a
selector, and adding a third dataset means adding a selector, not editing the
engine.
"""

from src.landcover.geometry import (  # noqa: F401
    AUTHALIC_RADIUS_M,
    CHINA_ALBERS,
    ZoneCoverage,
    coverage_for,
    fractional_weights,
    load_zones,
    raster_bounds_geometry,
    row_pixel_areas_m2,
)
from src.landcover.selectors import (  # noqa: F401
    Selector,
    at_least,
    at_most,
    between,
    in_classes,
)
from src.landcover.zonal import (  # noqa: F401
    ZonalHistogram,
    ZonalResult,
    zonal_area,
    zonal_histogram,
    zonal_value_sum,
)
