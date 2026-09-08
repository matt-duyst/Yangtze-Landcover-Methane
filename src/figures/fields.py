"""Drawing a value on the analysis lattice, and drawing where there is none.

Shared by every map that carries a per-cell quantity: the composite, the
predictor maps, the fold map and the sampling-artefact map. All of them have
the same 1,023 cells and the same 97 holes, so the treatment of absence is
inherited from here rather than decided again in each figure.

**Absence is drawn as absence.** 97 cells of 1,023 received no qualifying
sounding and must not read as a low value. The literature does this by
rendering missing data as blank rather than interpolating it, and filling gaps
is treated as a separate contribution that is stated and defended, never done
quietly inside a figure.

The treatment here is a flat near-white fill with a thin dark outline, and the
outline is the part that took iteration. The holes are not one shape: they run
from a 47-cell block over southern Zhejiang down to eight isolated single
cells, so the same treatment has to work at both. A fill alone loses the
singletons, which at 0.25 degrees on a 17 cm map are about 3.5 mm squares that
read as a light patch in a light part of the ramp. The outline makes a single
cell a deliberate mark rather than a gap in the paint.

**The ramp is truncated so that absence has somewhere to live.** Full batlow
runs from luminance 0.10 to 0.85, which leaves only 0.11 between its light end
and white; the project's own convention is that anything carrying meaning
separates by at least 0.15. Truncating the ramp at 0.88 of its range brings the
light end to 0.77 and opens a gap of 0.19. The cost is a slightly shorter ramp;
the alternative was an absence colour that collides with the top of the scale
in greyscale, which is the failure this whole convention exists to prevent.
"""

from __future__ import annotations

import numpy as np
from matplotlib.colors import BoundaryNorm, LinearSegmentedColormap

from . import style

#: How much of the sequential map to use. See the module docstring.
RAMP_TRUNCATION = 0.88

#: A second ramp, for a panel showing a different quantity beside a value
#: panel. Two panels drawn on one ramp invite a reader to read a colour across
#: them, and here that would be actively wrong: the high-methane cells and the
#: high-count cells are not the same cells. lipari is hue-distinct from batlow
#: and still leaves 0.18 of luminance between its light end and absence.
COUNT_RAMP = "lipari"

#: Cells with no observation. Near-white, which is the literature's convention
#: for missing, and outside the truncated ramp by 0.19 in luminance.
ABSENT_FILL = "#f7f7f7"
#: Without this a single absent cell is a pale square in a pale field. Set at
#: luminance 0.50 rather than darker so that it stays 0.22 clear of the
#: coastline; at 0.30 the two were 0.02 apart and indistinguishable in
#: greyscale, which is the failure the whole colour convention exists to catch.
ABSENT_EDGE = "#808080"
ABSENT_LABEL = "no qualifying sounding"
#: Artist label for the absence collection. A basemap layer is also a
#: PatchCollection, so anything looking for the holes must select by name
#: rather than by type.
ABSENT_ARTIST = "lattice-absence"


def field_cmap(name: str = style.SEQUENTIAL, truncate: float = RAMP_TRUNCATION):
    """The sequential map, truncated so its light end stays clear of absence."""
    base = style.sequential(name)
    return LinearSegmentedColormap.from_list(
        f"{name}_trunc", base(np.linspace(0.0, truncate, 256)))


#: Half-decade class edges for a sounding count. The upper edge is open.
COUNT_EDGES = (1, 4, 11, 32, 100, 316, 1_000_000)
COUNT_LABELS = ("1-3", "4-10", "11-31", "32-99", "100-315", "316 and above")


def count_norm(edges=COUNT_EDGES):
    """A classed scale for sounding counts, not a continuous one.

    The count runs 1 to 410 with a median of 74, so a linear scale puts the
    median at a fifth of the range and renders every sparse cell the same
    colour. That is where the finding is: the mixed-coast cells sit at a median
    of 6 soundings against 133 for land, and a linear ramp erases the
    distinction entirely.

    A continuous log scale keeps the sparse end but is hard to read off a
    legend and implies a precision the count does not carry. Classes are what
    the literature does, which masks below a sampling threshold rather than
    encoding count as a gradient, and a class boundary is a statement a caption
    can defend. These are half-decade steps, so each class is roughly three
    times the one below it.
    """
    return BoundaryNorm(list(edges), ncolors=256, clip=True)


def draw_lattice_field(ax, values, spec, *, cmap, norm, absent=None,
                       absent_fill=ABSENT_FILL, absent_edge=ABSENT_EDGE,
                       edge_width=0.25):
    """Draw one value per cell over ``spec``, with absence marked.

    ``values`` is (rows, cols) with row 0 northernmost, matching the composite
    rasters. ``absent`` is a boolean mask of the same shape; where it is None,
    non-finite values are taken to be absent.

    Returns the mesh, so a caller can build a colour bar from it.
    """
    from . import geo

    values = np.asarray(values, dtype="float64")
    if absent is None:
        absent = ~np.isfinite(values)
    absent = np.asarray(absent, dtype=bool)
    if absent.shape != values.shape:
        raise ValueError(f"absence mask is {absent.shape}, values are {values.shape}")

    lons, lats = geo.cell_edges(spec)
    # cell_edges runs south to north; the value grid runs north to south.
    mesh = ax.pcolormesh(lons, lats[::-1], np.ma.masked_where(absent, values),
                         cmap=cmap, norm=norm, shading="flat", zorder=2,
                         linewidth=0, rasterized=True)

    rows, cols = np.where(absent)
    if rows.size:
        from matplotlib.patches import Rectangle
        from matplotlib.collections import PatchCollection
        res = spec.resolution
        patches = [Rectangle((spec.west + c * res, spec.north - (r + 1) * res),
                             res, res) for r, c in zip(rows, cols)]
        ax.add_collection(PatchCollection(
            patches, facecolor=absent_fill, edgecolor=absent_edge,
            linewidth=edge_width, zorder=3, label=ABSENT_ARTIST))
    return mesh


def absence_artist(ax):
    """The absence collection on ``ax``, or None. Selected by label."""
    for collection in ax.collections:
        if collection.get_label() == ABSENT_ARTIST:
            return collection
    return None


def absence_handle(label: str = ABSENT_LABEL):
    """A legend key for absence, matching what `draw_lattice_field` draws."""
    from matplotlib.patches import Patch

    return Patch(facecolor=ABSENT_FILL, edgecolor=ABSENT_EDGE, linewidth=0.6,
                 label=label)


def ramp_luminances(cmap=None, samples: int = 64) -> np.ndarray:
    """Relative luminance along a ramp, for the greyscale check.

    A ramp is not a set of discrete colours, so a minimum pairwise gap says
    nothing about it: adjacent samples are arbitrarily close by construction.
    What matters is that the ramp is monotone in luminance, so that a greyscale
    reader can order values at all, and that its range is wide enough to
    resolve them.
    """
    cmap = field_cmap() if cmap is None else cmap
    rgb = np.array([cmap(x)[:3] for x in np.linspace(0, 1, samples)])
    return 0.2126 * rgb[:, 0] + 0.7152 * rgb[:, 1] + 0.0722 * rgb[:, 2]
