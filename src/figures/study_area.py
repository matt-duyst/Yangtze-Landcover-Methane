"""The study area: four provinces, the analysis lattice, and a locator inset.

A reference map. It exists so that every later figure can be read against a
geography the reader has already seen, and so that the 0.25 degree lattice is
shown once, at size, rather than described in words in eight captions.

Everything geospatial comes from :mod:`~src.figures.geo`: the projection, the
lattice extent, the tick formatting and the committed boundary layers. Nothing
about the map is decided here.

**The lattice is drawn at its measured extent, not its declared one.**
``GridSpec`` rounds its shape in both axes and in opposite directions, so the
grid stops short of the declared east edge at 122.55 and runs past the declared
south edge to 26.95. Drawing the declared box would put the map and the data
one cell apart at two of four edges.

The map does **not** distinguish the 927 cells that carry methane from the 96
that do not. That is the composite figure's subject and splitting it across two
figures would weaken both. The caption says the fraction rather than the figure
implying full coverage.
"""

from __future__ import annotations

import numpy as np

from . import geo, style
from .geo import Extent

#: Where each province's name is written, and where it points if it must be
#: placed off the polygon. Shanghai is too small at this scale to hold a label,
#: so its name sits offshore with a leader line to the municipality.
PROVINCE_LABELS = {
    "Anhui": (117.0, 32.1, None),
    "Jiangsu": (119.4, 33.5, None),
    "Zhejiang": (119.9, 29.2, None),
    "Shanghai": (122.48, 30.72, (121.62, 31.08)),
}

#: The inset covers mainland China with a little air around it.
INSET_EXTENT = Extent(west=72.0, east=136.0, south=17.0, north=54.5)


#: This figure is one panel and its extent draws portrait, so it does not take
#: the project's full width. `style.py` says a figure that should be narrow
#: passes its own width deliberately rather than inheriting the default, and
#: this is one. The height is derived from the extent so the map fills it.
WIDTH_CM = 11.4


def study_area_figure(spec, width_cm: float = WIDTH_CM,
                      height_cm: float | None = None):
    """Build and return the study area map. Writes nothing."""
    provinces = geo.read_layer(geo.PROVINCES)
    land = geo.read_layer(geo.LAND)
    china = geo.read_layer(geo.CHINA)

    extent = geo.lattice_extent(spec)
    if height_cm is None:
        height_cm = geo.figure_height_cm(extent, width_cm)
    fig = style.figure(width_cm=width_cm, height_cm=height_cm)

    left = 1.05 / width_cm
    bottom = 0.85 / height_cm
    ax = fig.add_axes((left, bottom, 0.985 - left, 0.985 - bottom))

    _draw_main(ax, spec, extent, provinces, land)
    inset = fig.add_axes((0.665, bottom + 0.006, 0.315, 0.315 / geo.display_ratio(extent)))
    _draw_inset(inset, china, extent)
    return fig


def _draw_main(ax, spec, extent: Extent, provinces, land) -> None:
    # Sea first, as the ground colour, then land over it. Drawing the sea as a
    # filled rectangle rather than as ocean polygons means the panel has no
    # gaps where a coastline is open.
    ax.set_facecolor(style.MAP_SEA)
    land.plot(ax=ax, facecolor=style.MAP_LAND, edgecolor="none", zorder=1)
    provinces.plot(ax=ax, facecolor=style.MAP_STUDY_FILL, edgecolor="none",
                   zorder=2)
    land.boundary.plot(ax=ax, color=style.MAP_COASTLINE, linewidth=0.5, zorder=4)
    provinces.boundary.plot(ax=ax, color=style.MAP_BOUNDARY, linewidth=0.7,
                            zorder=5)

    _draw_lattice(ax, spec, extent)
    _label_provinces(ax, provinces)

    geo.apply_projection(ax, extent)
    xticks, yticks = geo.graticule(extent, step=2.0)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.xaxis.set_major_formatter(geo.degree_formatter("x"))
    ax.yaxis.set_major_formatter(geo.degree_formatter("y"))
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(True)
    for spine in ax.spines.values():
        spine.set_linewidth(0.7)
        spine.set_edgecolor(style.MAP_BOUNDARY)

    _legend(ax, spec)


def _draw_lattice(ax, spec, extent: Extent) -> None:
    """Every cell edge, faintly, plus a heavier line each whole degree.

    Sixty-six lines will fight the boundaries if they are all drawn alike, so
    the cell edges are as light as a 300 dpi raster will hold and every fourth
    line, which is a whole degree, is drawn slightly heavier. The reader gets
    the grid as a texture and the graticule as structure, from one set of
    lines rather than two overlaid.
    """
    lons, lats = geo.cell_edges(spec)
    for values, plot, limits in ((lons, ax.axvline, (extent.south, extent.north)),
                                 (lats, ax.axhline, (extent.west, extent.east))):
        for value in values:
            whole = abs(value - round(value)) < 1e-9
            plot(value, color=style.MAP_LATTICE, zorder=3,
                 linewidth=0.45 if whole else 0.18,
                 alpha=0.85 if whole else 0.55)
        del limits


def _label_provinces(ax, provinces) -> None:
    for _, row in provinces.iterrows():
        name = row.get("name_en") or row.get("name")
        if name not in PROVINCE_LABELS:
            continue
        lon, lat, anchor = PROVINCE_LABELS[name]
        align = "right" if anchor is not None else "center"
        ax.text(lon, lat, name, ha=align, va="center", zorder=7,
                fontsize=style.LABEL_SIZE, color=style.role("label_text"),
                path_effects=_halo())
        if anchor is not None:
            ax.plot([lon - 0.72, anchor[0]], [lat + 0.10, anchor[1]],
                    color=style.role("label_text"), linewidth=0.5, zorder=6)


def _halo():
    """A white outline behind label text, so a name stays readable on a fill.

    Not decoration. Without it a province name crossing a boundary line is
    unreadable, and moving the name somewhere emptier would put it off its
    own province.
    """
    from matplotlib import patheffects
    return [patheffects.withStroke(linewidth=1.8, foreground=style.role("label_halo"))]


def _legend(ax, spec) -> None:
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    handles = [
        Patch(facecolor=style.MAP_STUDY_FILL, edgecolor=style.MAP_BOUNDARY,
              linewidth=0.7, label="study provinces"),
        Patch(facecolor=style.MAP_LAND, edgecolor=style.MAP_COASTLINE,
              linewidth=0.5, label="land outside the study region"),
        Patch(facecolor=style.MAP_SEA, edgecolor="none", label="sea"),
        Line2D([], [], color=style.MAP_LATTICE, linewidth=0.45,
               label=f"analysis grid, {spec.resolution:g}° cells"),
    ]
    # Lower left: the south-west corner is land outside the study region and
    # carries the least information on the map, and the inset takes the
    # opposite corner.
    ax.legend(handles=handles, loc="lower left",
              labelcolor=style.role("label_text"), handlelength=1.4,
              borderpad=0.45, framealpha=0.92, frameon=True,
              facecolor=style.role("page"), edgecolor="none")


def _draw_inset(ax, china, extent: Extent) -> None:
    """A locator in the project's equal-area conic.

    The inset spans most of China, and an equirectangular map of that extent
    is stretched badly at its northern edge, so it uses `CHINA_ALBERS` rather
    than the main panel's projection. Two projections in one figure is a cost;
    a locator that misrepresents the country it locates against is a worse one.
    """
    ax.set_facecolor(style.role("page"))
    for collection in china.geometry:
        parts = (collection.geoms if collection.geom_type == "MultiPolygon"
                 else [collection])
        for part in parts:
            lon, lat = np.asarray(part.exterior.coords).T
            x, y = geo.to_albers(lon, lat)
            ax.fill(x, y, facecolor=style.MAP_LAND,
                    edgecolor=style.MAP_BOUNDARY, linewidth=0.4, zorder=1)

    corners_lon = [extent.west, extent.east, extent.east, extent.west, extent.west]
    corners_lat = [extent.south, extent.south, extent.north, extent.north,
                   extent.south]
    x, y = geo.to_albers(corners_lon, corners_lat)
    ax.fill(x, y, facecolor=style.MAP_STUDY_FILL, edgecolor=style.role("label_text"),
            linewidth=0.8, zorder=2)

    xs, ys = geo.to_albers([INSET_EXTENT.west, INSET_EXTENT.east],
                           [INSET_EXTENT.south, INSET_EXTENT.north])
    ax.set_xlim(float(np.min(xs)), float(np.max(xs)))
    ax.set_ylim(float(np.min(ys)), float(np.max(ys)))
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.6)
        spine.set_edgecolor(style.MAP_BOUNDARY)
