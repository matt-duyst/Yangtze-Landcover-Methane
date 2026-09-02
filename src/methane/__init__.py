"""Gridding Sentinel-5P Level 2 methane onto the analysis grid.

Level 2 is a swath product: irregular soundings along an orbit track, not a
grid. Turning it into one is a binning problem, and the thing that matters most
about the result is not the mean but how many soundings produced it.

Coverage is therefore a first-class output here, in the same way that
``src.landcover`` makes an area inseparable from the coverage fraction it rests
on. A mean methane grid cannot be obtained from this package without the
per-cell sounding count that goes with it, because over this study area the two
are not independent: of 36 granules sampled during reconnaissance only 16
carried any valid in-box sounding at all, and the annual yield ran from 2,533
valid soundings in 2023 down to 4 in 2020. A composite that pools years without
reporting what each contributed is measuring cloud cover.
"""

from src.methane.grid import (  # noqa: F401
    Composite,
    Coverage,
    GranuleContribution,
    GridSpec,
    Soundings,
    coverage_of,
    grid_granules,
    read_soundings,
)
