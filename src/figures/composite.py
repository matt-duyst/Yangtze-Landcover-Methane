"""The 2018 methane composite: the field, and where there is no field.

Two panels sharing one geographic frame, so a reader can move between them cell
by cell: the bias-corrected mean XCH4 per cell, and the number of soundings the
cell's mean rests on.

**The variable is the bias-corrected retrieval**, which is the operationally
corrected product and what the reproduction's analysis used throughout. It is
not a neutral default: the correction averages +11.64 ppb and ranges +3.42 to
+29.05, a spread across cells of 25.6 against the field's own standard
deviation of 14.9, so the two fields are not interchangeable. It also does not
remove the albedo dependence it is sometimes assumed to, which the caption
says.

**A third panel was considered and rejected**; see the caption and
notes/decisions.md. Absence and the count scale are inherited from
:mod:`~src.figures.fields`, because the predictor maps, the fold map and the
sampling-artefact map all share these 97 holes.
"""

from __future__ import annotations

import numpy as np

from . import fields, geo, style

#: The composite raster: band 1 bias-corrected, band 2 raw, band 3 counts.
COMPOSITE = "data/processed/methane_composite_2018.tif"

WIDTH_CM = style.FULL_WIDTH_CM


def read_composite(path=None):
    """Bias-corrected mean, sounding count, and the absence mask."""
    import rasterio

    from .geo import REFERENCE_DIR

    target = REFERENCE_DIR.parents[1] / (path or COMPOSITE)
    with rasterio.open(target) as src:
        corrected, counts = src.read(1), src.read(3)
    absent = counts == 0
    return corrected, counts.astype("int64"), absent


def composite_figure(spec=None, corrected=None, counts=None, absent=None,
                     width_cm: float = WIDTH_CM):
    """Build and return the two-panel composite figure. Writes nothing."""
    spec = geo.study_spec() if spec is None else spec
    if corrected is None:
        corrected, counts, absent = read_composite()

    extent = geo.lattice_extent(spec)
    ratio = geo.display_ratio(extent)
    panel = (width_cm - 1.9) / 2.0
    height_cm = panel * ratio + 3.05

    fig = style.figure(width_cm=width_cm, height_cm=height_cm)
    left, bottom = 0.055, 0.175
    gap, top = 0.055, 0.962
    each = (0.985 - left - gap) / 2.0
    axes = []
    for i in range(2):
        axes.append(fig.add_axes((left + i * (each + gap), bottom, each,
                                  top - bottom)))

    provinces = geo.read_layer(geo.PROVINCES)
    land = geo.read_layer(geo.LAND)

    mesh_a = _draw_value_panel(axes[0], spec, extent, corrected, absent,
                               provinces, land)
    mesh_b = _draw_count_panel(axes[1], spec, extent, counts, absent,
                               provinces, land)

    _colourbar(fig, axes[0], mesh_a, "Mean XCH$_4$, bias corrected (ppb)")
    _class_bar(fig, axes[1], "Soundings in the cell (count)",
               int(counts[~absent].max()))

    style.panel_label(axes[0], "a", dx=-0.05, dy=1.012)
    style.panel_label(axes[1], "b", dx=-0.05, dy=1.012)
    return fig


# There is deliberately no basemap. The lattice covers all 1,023 cells of the
# extent, 926 in the mesh and 97 as absence, so a land or sea fill beneath it
# is drawn and then entirely hidden: measured at zero visible pixels. Leaving
# it in would be ink that carries nothing, and worse, would imply to a later
# reader that the sea tone means something here. The coastline is still drawn,
# over the field, because it locates the geography.


def _overlay(ax, spec, extent, provinces, land) -> None:
    """Boundaries and frame, drawn over the field so the geography stays read."""
    land.boundary.plot(ax=ax, color=style.MAP_COASTLINE, linewidth=0.45, zorder=4)
    provinces.boundary.plot(ax=ax, color=style.MAP_BOUNDARY, linewidth=0.6,
                            zorder=5)
    geo.apply_projection(ax, extent)
    xticks, yticks = geo.graticule(extent, step=2.0)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.xaxis.set_major_formatter(geo.degree_formatter("x"))
    ax.yaxis.set_major_formatter(geo.degree_formatter("y"))
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.7)
        spine.set_edgecolor(style.MAP_BOUNDARY)


def _draw_value_panel(ax, spec, extent, corrected, absent, provinces, land):
    from matplotlib.colors import Normalize

    finite = corrected[~absent]
    # Clipped to the 2nd and 98th percentiles, with the bar carrying arrow caps
    # so the reader is told values run past it. The full range is 106 ppb and
    # the middle 96 percent occupies 59, so an unclipped ramp spends nearly
    # half its length on four percent of cells -- and those cells are the least
    # reliable in the composite. The median count in the lowest two percent of
    # values is 12 soundings and in the highest two percent it is 2, against 74
    # overall, so the tails are thin sampling rather than a methane signal.
    norm = Normalize(vmin=np.floor(np.percentile(finite, 2)),
                     vmax=np.ceil(np.percentile(finite, 98)))
    mesh = fields.draw_lattice_field(ax, corrected, spec,
                                     cmap=fields.field_cmap(), norm=norm,
                                     absent=absent)
    _overlay(ax, spec, extent, provinces, land)
    ax.legend(handles=[fields.absence_handle()], loc="lower left",
              labelcolor="black", handlelength=1.2, borderpad=0.35,
              frameon=True, facecolor="white", edgecolor="none",
              framealpha=0.92)
    return mesh


def _draw_count_panel(ax, spec, extent, counts, absent, provinces, land):
    mesh = fields.draw_lattice_field(ax, counts.astype("float64"), spec,
                                     cmap=fields.field_cmap(fields.COUNT_RAMP),
                                     norm=fields.count_norm(), absent=absent)
    _overlay(ax, spec, extent, provinces, land)
    return mesh


def _colourbar(fig, ax, mesh, label) -> None:
    box = ax.get_position()
    cax = fig.add_axes((box.x0, box.y0 - 0.098, box.width, 0.022))
    bar = fig.colorbar(mesh, cax=cax, orientation="horizontal", extend="both")
    bar.set_label(label, fontsize=style.LABEL_SIZE)
    bar.ax.tick_params(labelsize=style.TICK_SIZE, length=2.5)
    bar.outline.set_linewidth(0.6)


def _class_bar(fig, ax, label, top: int) -> None:
    """A classed legend, drawn as equal boxes with ticks at the class edges.

    A colour bar under a BoundaryNorm still reads as a gradient, which is the
    thing the classes exist to avoid, so the classes are drawn as what they
    are: equal-width boxes. The numbers sit at the boundaries rather than
    centred in each box, because a boundary is the statement being made and
    because six centred range labels do not fit across half a 17 cm figure.
    """
    from matplotlib.patches import Rectangle

    box = ax.get_position()
    cax = fig.add_axes((box.x0, box.y0 - 0.098, box.width, 0.022))
    cmap = fields.field_cmap(fields.COUNT_RAMP)
    edges = list(fields.COUNT_EDGES[:-1]) + [top]
    n = len(edges) - 1
    for i in range(n):
        cax.add_patch(Rectangle((i / n, 0), 1 / n, 1,
                                facecolor=cmap((i + 0.5) / n), edgecolor="none"))
    cax.set_xlim(0, 1)
    cax.set_ylim(0, 1)
    cax.set_xticks([i / n for i in range(n + 1)])
    cax.set_xticklabels([str(e) for e in edges])
    cax.tick_params(labelsize=style.TICK_SIZE, length=2.5)
    cax.set_yticks([])
    for spine in cax.spines.values():
        spine.set_linewidth(0.6)
        spine.set_edgecolor(style.MAP_BOUNDARY)
    cax.set_xlabel(label, fontsize=style.LABEL_SIZE, labelpad=3)
