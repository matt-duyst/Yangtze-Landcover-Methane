"""Which pixel values count.

The two datasets this package serves encode themselves in incompatible ways and
neither is named here.

GAIA stores the year a pixel first became impervious, counting downward from
the newest year, so extent for a year is every pixel at or above a threshold:
:func:`at_least`. The NESDC rice rasters store discrete classes, 1 for
single-season and 2 for double-season, so rice extent is set membership:
:func:`in_classes`.

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
