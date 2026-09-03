"""Which pixel values count.

The two datasets this package serves encode themselves in incompatible ways and
neither is named here.

GAIA stores the year a pixel first became impervious, counting downward from
the newest year, so extent for a year is every pixel at or above a threshold:
:func:`at_least`. GISA stores the same quantity counting *upward* from the
oldest year, and separately uses 0 for non-impervious, so its extent is a
closed interval: :func:`between`. The NESDC rice rasters store discrete
classes, 1 for single-season and 2 for double-season, so rice extent is set
membership: :func:`in_classes`.

The two impervious products being mirror images of each other is the reason
these are separate named helpers rather than inline comparisons. Applying
GAIA's rule to GISA selects the newest construction instead of the accumulated
extent, and the result is a plausible-looking raster of the wrong thing.

Selection is always explicit. None of these helpers consults a raster's nodata
value, and that is deliberate rather than an oversight: the NESDC rasters
declare no nodata at all, and 0 in them means both genuine non-rice land and
out-of-province background. A selector that quietly treated some value as fill
would be guessing. The caller states which values count and nothing else is
counted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable

import numpy as np


@dataclass(frozen=True)
class Selector:
    """A named test over pixel values.

    ``description`` travels with results so a table can say what was counted
    without the reader having to find the call site.
    """

    description: str
    predicate: Callable[[np.ndarray], np.ndarray]

    def __call__(self, values: np.ndarray) -> np.ndarray:
        mask = self.predicate(values)
        if mask.dtype != np.bool_:
            raise TypeError(
                f"selector {self.description!r} returned {mask.dtype}, not bool"
            )
        return mask


def at_least(threshold: int) -> Selector:
    """Pixels whose value is >= ``threshold``.

    Cumulative thresholding, for products that encode a year of change.
    """
    return Selector(
        description=f"value >= {threshold}",
        predicate=lambda a: a >= threshold,
    )


def at_most(threshold: int) -> Selector:
    """Pixels whose value is <= ``threshold``.

    The mirror of :func:`at_least`, for products that count upward from the
    oldest year rather than downward from the newest.
    """
    return Selector(
        description=f"value <= {threshold}",
        predicate=lambda a: a <= threshold,
    )


def between(low: int, high: int) -> Selector:
    """Pixels whose value lies in ``[low, high]``, both ends included.

    Needed for a product that counts upward from the oldest year and also uses
    0 for absence, where neither :func:`at_least` nor :func:`at_most` says the
    right thing on its own. GISA is the case: values 1 to 37 are the years 1972
    to 2019 in ascending order and 0 is non-impervious, so extent as of 2018 is
    ``between(1, 36)``. ``at_most(36)`` would count every non-impervious pixel
    as impervious, and ``at_least(36)`` would count only what was built in the
    last two years, which is the inversion this module's docstring warns about.
    """
    if low > high:
        raise ValueError(f"between() needs low <= high, got {low} > {high}")
    return Selector(
        description=f"{low} <= value <= {high}",
        predicate=lambda a: (a >= low) & (a <= high),
    )


def in_classes(classes: Iterable[int]) -> Selector:
    """Pixels whose value is one of ``classes``.

    Discrete class membership, for categorical products.
    """
    wanted = sorted({int(c) for c in classes})
    if not wanted:
        raise ValueError("in_classes() needs at least one class value")
    array = np.asarray(wanted)
    return Selector(
        description="value in {" + ", ".join(str(c) for c in wanted) + "}",
        predicate=lambda a: np.isin(a, array),
    )
