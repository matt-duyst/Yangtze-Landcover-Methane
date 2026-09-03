r"""The TM5 a priori methane column that ships inside every granule.

Every Sentinel-5P L2 CH4 granule carries the a priori profile the retrieval was
run against, as ``methane_profile_apriori`` and ``dry_air_subcolumns`` under
``PRODUCT/SUPPORT_DATA/INPUT_DATA``, both in mol m-2 over 12 layers. The column
mixing ratio is the ratio of their sums, which is a pressure-weighted column
mean because the dry-air subcolumns are the weights:

.. math::

    \mathrm{XCH_4^{prior}} = 10^{9} \times
        \frac{\sum_{\ell} \mathrm{CH_4}_\ell}{\sum_{\ell} \mathrm{air}_\ell}

This module exists because the departure -- retrieved minus prior -- is the one
remaining way to remove background, seasonal and synoptic structure from the
composite without external data, and if that is ever revisited it should be a
configuration change rather than a rebuild. It is not currently used by the
composite; see notes/decisions.md for why the approach was gated and not taken.

**Layer ordering.** The file stores layers top-of-atmosphere first. Measured on
granule 03019 of 14 May 2018, ``altitude_levels`` runs 63,037.6 m at index 0
down to 20.6 m at index 12. That is why the Harvard TROPOMI inversion code
reverses the layer axis when it reads both variables: it wants surface-first.
The ratio of sums is order-invariant, so :func:`column_apriori` is unaffected
and does no reversing. **Any per-layer operation added later must reverse
first**, and :func:`surface_first` is here so that it does not have to be
rediscovered.

**Fill handling.** Both variables declare ``_FillValue`` 9.96921e+36 and neither
declares a ``scale_factor`` or an ``add_offset``, but all three are read from
the variable's own attributes rather than assumed, and reads use
``set_auto_maskandscale(False)``. That is not defensive habit: earlier in this
project a throwaway script read ``qa_value`` without it, netCDF4 silently
applied the scale factor, a threshold comparison was never true, and a granule
reported zero soundings where the module reported 31.

A sounding with a fill in any layer of either profile is excluded whole and
counted, never given a partial sum. On the granule measured, every excluded
sounding was missing all twelve layers rather than some, so partial profiles may
not occur at all, but the code does not rely on that.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

#: Where the two profiles live in an L2 CH4 granule.
INPUT_DATA = ("PRODUCT", "SUPPORT_DATA", "INPUT_DATA")
PROFILE = "methane_profile_apriori"
DRY_AIR = "dry_air_subcolumns"
LEVELS = "altitude_levels"

#: Mole fraction to parts per billion.
PPB = 1e9


class AprioriError(RuntimeError):
    """Base class for failures this module raises deliberately."""


class ProfileShapeMismatch(AprioriError):
    """The two profiles disagree about how many soundings or layers there are."""


@dataclass(frozen=True)
class AprioriColumn:
    """A priori XCH4 per sounding, and what it rests on."""

    #: Column mixing ratio in ppb, NaN where the sounding was excluded.
    values: np.ndarray
    #: True where a value was computed.
    valid: np.ndarray
    #: Soundings excluded because a profile carried a fill value.
    excluded: int
    #: Of those, ones missing some layers rather than all of them.
    partial: int
    #: Layers in the profile, 12 in the operational product.
    layers: int

    @property
    def n(self) -> int:
        return int(self.values.size)

    def summary(self) -> dict:
        finite = self.values[self.valid]
        return {
            "soundings": self.n,
            "with_apriori": int(self.valid.sum()),
            "excluded_for_fill": self.excluded,
            "partial_profiles": self.partial,
            "layers": self.layers,
            "mean_ppb": float(finite.mean()) if finite.size else float("nan"),
            "sd_ppb": float(finite.std()) if finite.size else float("nan"),
            "min_ppb": float(finite.min()) if finite.size else float("nan"),
            "max_ppb": float(finite.max()) if finite.size else float("nan"),
        }


def read_profile(group, name: str) -> tuple[np.ndarray, float | None]:
    """One profile variable and its own fill value, without auto-masking.

    Returns the raw array reshaped to ``(soundings, layers)`` and the fill
    value read from the variable's attributes. Scale factor and add offset are
    applied if the variable declares them; in the operational product neither
    does, but that is a property of the file and not of the format.
    """
    var = group.variables[name]
    try:
        var.set_auto_maskandscale(False)
    except AttributeError:                      # a plain array in a test
        pass
    raw = np.asarray(var[:])
    attrs = {a: var.getncattr(a) for a in var.ncattrs()} if hasattr(var, "ncattrs") else {}

    def scalar(key):
        value = attrs.get(key)
        if isinstance(value, np.ndarray):
            value = value.item() if value.size == 1 else value[0]
        return value

    values = raw.astype("float64")
    scale, offset = scalar("scale_factor"), scalar("add_offset")
    if scale:
        values = values * scale
    if offset:
        values = values + offset
    layers = raw.shape[-1]
    return values.reshape(-1, layers), scalar("_FillValue"), raw.reshape(-1, layers)


def surface_first(profile: np.ndarray) -> np.ndarray:
    """Reverse the layer axis, turning the file's order into surface-first.

    Not used by :func:`column_apriori`, which is order-invariant. Provided so
    that the first per-layer operation someone adds does not have to rediscover
    which way round the file is.
    """
    return np.asarray(profile)[..., ::-1]


def column_apriori(methane, dry_air, *, methane_fill=None, dry_air_fill=None,
                   methane_raw=None, dry_air_raw=None) -> AprioriColumn:
    """A priori XCH4 in ppb, one value per sounding.

    ``methane`` and ``dry_air`` are ``(soundings, layers)`` in mol m-2. Fill
    values are compared against the raw stored arrays when those are given,
    because a scaled fill is no longer equal to the declared fill.
    """
    methane = np.atleast_2d(np.asarray(methane, dtype="float64"))
    dry_air = np.atleast_2d(np.asarray(dry_air, dtype="float64"))
    if methane.shape != dry_air.shape:
        raise ProfileShapeMismatch(
            f"{PROFILE} is {methane.shape} and {DRY_AIR} is {dry_air.shape}; "
            f"they must describe the same soundings and layers")

    m_raw = methane if methane_raw is None else np.atleast_2d(methane_raw)
    a_raw = dry_air if dry_air_raw is None else np.atleast_2d(dry_air_raw)

    bad = ~np.isfinite(methane) | ~np.isfinite(dry_air)
    if methane_fill is not None:
        bad |= m_raw == methane_fill
    if dry_air_fill is not None:
        bad |= a_raw == dry_air_fill

    any_bad, all_bad = bad.any(axis=1), bad.all(axis=1)
    partial = int((any_bad & ~all_bad).sum())

    air_total = np.where(any_bad, np.nan, dry_air.sum(axis=1))
    valid = ~any_bad & np.isfinite(air_total) & (air_total > 0)

    values = np.full(methane.shape[0], np.nan)
    values[valid] = (methane[valid].sum(axis=1) / air_total[valid]) * PPB
    return AprioriColumn(values=values, valid=valid, excluded=int(any_bad.sum()),
                         partial=partial, layers=int(methane.shape[1]))


def from_granule(path: str | Path) -> AprioriColumn:
    """A priori XCH4 for every sounding in one granule."""
    import netCDF4

    with netCDF4.Dataset(str(path), "r") as dataset:
        node = dataset
        for part in INPUT_DATA:
            groups = getattr(node, "groups", {})
            if part not in groups:
                raise AprioriError(f"{Path(path).name}: no group {part!r}")
            node = groups[part]
        for name in (PROFILE, DRY_AIR):
            if name not in node.variables:
                raise AprioriError(f"{Path(path).name}: no variable {name!r}")
        methane, m_fill, m_raw = read_profile(node, PROFILE)
        dry_air, a_fill, a_raw = read_profile(node, DRY_AIR)
    return column_apriori(methane, dry_air, methane_fill=m_fill,
                          dry_air_fill=a_fill, methane_raw=m_raw,
                          dry_air_raw=a_raw)


def departure(retrieved: np.ndarray, prior: AprioriColumn) -> np.ndarray:
    """Retrieved minus prior, NaN where either is absent.

    The quantity the departure approach would analyse. It removes whatever
    structure the prior contains and keeps whatever it does not, which includes
    the albedo bias in full; see notes/decisions.md before using it.
    """
    retrieved = np.asarray(retrieved, dtype="float64")
    if retrieved.shape != prior.values.shape:
        raise ProfileShapeMismatch(
            f"retrieved is {retrieved.shape} and the prior is "
            f"{prior.values.shape}")
    out = np.full(retrieved.shape, np.nan)
    usable = prior.valid & np.isfinite(retrieved)
    out[usable] = retrieved[usable] - prior.values[usable]
    return out
