"""The study area: four provinces on real terrain, in a country, at a scale.

A reference map, and a reference map has to do two things: put the reader
somewhere they can find, and make the analysis grid a size rather than a
number. The first version did neither. Land outside the four provinces was
near-white, so it read as absence rather than as land; nothing outside the
region was named; the lattice was drawn at full extent over sea and
out-of-region land, where sixty-six lines function as hatching rather than as
reference; and the locator inset sat over Zhejiang's coast and the Zhoushan
archipelago, covering data to save space the figure had.

What replaced each, and why
---------------------------

**Terrain, and terrain that earns its place.** The main panel is a shaded
relief from Copernicus DEM GLO-90 over every part of the frame, so land is
land. It is not decoration and the caption says so: 75 of the composite's 97
absent cells are on land, and the largest connected block of 47 sits over the
mountains of southern Zhejiang, which are the darkest thing in this panel. A
reader who has seen the terrain here understands the next figure's holes
without being told they are terrain.

Grey relief, not hypsometric colour, because overlays are drawn on it and the
colour budget belongs to data. The inset is the opposite case -- nothing
overlays it -- so the inset is hypsometric.

**The study region is carried by contrast, not by hue.** Relief is drawn twice
from one raster: veiled toward `land_outside` beyond the four provinces and
tinted toward `province_fill` inside them. The two bands are 0.16 apart in
luminance at flat ground, so the region survives a black and white print,
which a tint alone would not. Four separate province fills were not tried
again; six areal classes cannot separate, and the boundaries and the names
carry which province is which.

**Shanghai is labelled in place, and it takes no leader line.** The leader in
the first version was the tell that the encoding was wrong.

The constraint is real and was measured rather than eyeballed. At 8 pt the word
"Shanghai" occupies 0.99 by 0.21 degrees on this panel, and sliding that box
over the municipality's polygon at a fiftieth of a degree finds no position
where it fits entirely inside. The same test fits Anhui, Jiangsu and Zhejiang
easily. Shanghai's bounding box is 1.13 degrees wide, which is wider than the
label, but the municipality is an estuary lobe and a chain of islands rather
than a rectangle, so the bounding box is not the question.

The answer is not a smaller font or a better leader. Shanghai is also one of the
four provincial capitals, so its city label names the municipality too, and a
name beside its own marker is a label in place. One name does both jobs and no
line is drawn to anything.

**The lattice is gone from the main panel and is a detail box instead.** The
composite already shows the analysis resolution by drawing the cells as the
data, so drawing all 66 lines here was redundant and cost the whole panel a
layer of texture. The detail box shows six cells over the Yangtze mouth at
4.6 times the main panel's scale, with the same window outlined on the main
panel so the reader can see the true drawn size of a cell and a legible one
at once.

**The inset is outside the map frame**, in the right-hand column, where a
portrait map leaves 4.5 cm of page that would otherwise be white. It covers
nothing. It also asserts nothing: see :func:`_draw_inset`.

Everything geospatial comes from :mod:`~src.figures.geo` and every colour from
a role in :mod:`~src.figures.style`. Nothing about the projection, the extent
or the palette is decided here.
"""

from __future__ import annotations

import numpy as np

from . import geo, style
from .geo import Extent

#: Where each province's name is written. Every point is asserted to lie
#: inside its own polygon by the test suite, and each is placed away from its
#: capital: Hefei sits at 117.3, 31.9, which is where "Anhui" used to be.
#: Shanghai is absent on purpose -- its name is carried by its city label.
PROVINCE_LABELS = {
    "Anhui": (116.30, 33.40),
    "Jiangsu": (119.80, 33.60),
    "Zhejiang": (119.90, 28.80),
}

#: The inset covers mainland China with a little air around it. Matches
#: `scripts/build_map_reference.INSET`, which is the extent its raster was
#: warped onto.
INSET_EXTENT = Extent(west=72.0, east=136.0, south=17.0, north=54.5)

#: The detail box: three cells by two over the Yangtze mouth, on cell edges.
#: Chosen for its land fraction, which is 0.58 -- the box has to show a
#: coastline, and a window that is nearly all land or nearly all water shows
#: the reader a grid on a plain background instead.
DETAIL_WINDOW = Extent(west=121.30, east=122.05, south=31.45, north=31.95)

# Layout, in centimetres, measured across the page rather than in axes
# fractions, because the panels have to line up with each other and with the
# map's own aspect. They sum to FIG_WIDTH by construction and a test says so.
FIG_WIDTH_CM = style.FULL_WIDTH_CM
LEFT_CM = 1.15      # latitude tick labels
MAP_WIDTH_CM = 10.20
GUTTER_CM = 0.55
COLUMN_CM = 4.55    # inset, detail box, legend
RIGHT_CM = 0.55
BOTTOM_CM = 1.00    # longitude tick labels
TOP_CM = 0.30

#: Retained: the figure now takes the project default because the right-hand
#: column is what stops a portrait map from sitting in a band of white. The
#: previous version was 11.4 cm and had no column.
WIDTH_CM = FIG_WIDTH_CM


def study_area_figure(spec, width_cm: float = WIDTH_CM,
                      height_cm: float | None = None):
    """Build and return the study area map. Writes nothing."""
    provinces = geo.read_layer(geo.PROVINCES)
    land = geo.read_layer(geo.LAND)
    neighbours = geo.read_layer(geo.NEIGHBOURS)
    places = geo.read_layer(geo.PLACES)

    extent = geo.lattice_extent(spec)
    map_width = width_cm - (LEFT_CM + GUTTER_CM + COLUMN_CM + RIGHT_CM)
    map_height = map_width * geo.display_ratio(extent)
    if height_cm is None:
        height_cm = map_height + BOTTOM_CM + TOP_CM
    fig = style.figure(width_cm=width_cm, height_cm=height_cm)

    def axes(x_cm, y_cm, w_cm, h_cm):
        return fig.add_axes((x_cm / width_cm, y_cm / height_cm,
                             w_cm / width_cm, h_cm / height_cm))

    ax = axes(LEFT_CM, BOTTOM_CM, map_width, map_height)
    _draw_main(ax, extent, provinces, land, neighbours, places)

    # The right-hand column, laid out downward from the top of the map. Every
    # gap is stated in centimetres rather than tuned as an axes fraction,
    # because a fraction of a figure whose height is derived is not a length.
    column_x = LEFT_CM + map_width + GUTTER_CM
    cursor = BOTTOM_CM + map_height

    inset_height = COLUMN_CM * _inset_ratio()
    inset = axes(column_x, cursor - inset_height, COLUMN_CM, inset_height)
    _draw_inset(inset, extent)
    cursor -= inset_height
    _column_note(fig, column_x, cursor - 0.20, width_cm, height_cm,
                 INSET_NOTE, style.TICK_SIZE - 1.5)
    cursor -= 1.15

    detail_height = COLUMN_CM * geo.display_ratio(DETAIL_WINDOW)
    detail = axes(column_x, cursor - detail_height, COLUMN_CM, detail_height)
    _draw_detail(detail, spec, land)
    cursor -= detail_height
    _column_note(fig, column_x, cursor - 0.18, width_cm, height_cm,
                 _detail_note(spec), style.TICK_SIZE - 1.0)
    cursor -= 1.75

    # The keys sit in the middle of what is left rather than at the top of it,
    # so the column's unavoidable white space is split above and below them
    # instead of pooling in one block at the foot of the figure.
    notice_top = BOTTOM_CM + 1.65
    _column_legend(fig, column_x, 0.5 * (cursor + notice_top) + 1.0,
                   width_cm, height_cm)
    _column_note(fig, column_x, BOTTOM_CM - 0.05, width_cm, height_cm,
                 DEM_NOTICE, style.TICK_SIZE - 2.0, va="bottom")
    return fig


# --------------------------------------------------------------------------
# the main panel
# --------------------------------------------------------------------------

def _draw_main(ax, extent: Extent, provinces, land, neighbours, places) -> None:
    ax.set_facecolor(style.role("sea"))
    _draw_relief(ax, land, provinces)

    # Neighbours first and lighter, so the study boundary reads as the heavier
    # of two weights rather than as the only line on the map.
    neighbours.boundary.plot(ax=ax, color=style.role("boundary_minor"),
                             linewidth=0.4, zorder=4)
    land.boundary.plot(ax=ax, color=style.role("coastline"), linewidth=0.5,
                       zorder=5)
    provinces.boundary.plot(ax=ax, color=style.role("boundary"),
                            linewidth=0.8, zorder=6)

    _outline_detail_window(ax)
    _label_neighbours(ax, neighbours, extent)
    _label_provinces(ax, provinces)
    _draw_places(ax, places)

    geo.apply_projection(ax, extent)
    xticks, yticks = geo.graticule(extent, step=2.0)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.xaxis.set_major_formatter(geo.degree_formatter("x"))
    ax.yaxis.set_major_formatter(geo.degree_formatter("y"))
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.7)
        spine.set_edgecolor(style.role("boundary"))


#: How many pixels of committed relief to keep per pixel the panel can show.
#: 1.25 rather than 1.0 because a resampler wants a little more than it draws,
#: and rather than 1.66, which is what the committed raster holds and what the
#: first rebuild embedded: measured, drawing it at its stored resolution put
#: 1.6 MB of image into a vector file whose venue ceiling is 2 MB, for detail
#: no reader can resolve. Downsampling here rather than committing a smaller
#: raster keeps the reference product usable by a figure drawn at another size.
RELIEF_SUPERSAMPLE = 1.15


def relief_image(land, provinces, hillshade=None, extent=None,
                 window: Extent | None = None,
                 panel_width_cm: float | None = None):
    """The composited relief, its extent, and the path that clips it to land.

    **One image, not two.** The first rebuild drew the veiled relief and the
    tinted relief as two full-extent images with two clip paths, which put
    ten million pixels into the vector file to show five million: each image
    was hidden wherever the other was visible. Compositing them here against a
    rasterised province mask draws one image, and measured, it took the PDF
    from 1.63 MB to well under half of the venue's 2 MB ceiling.

    Both treatments are clipped to the land polygons, so no relief is drawn
    under water. That is not tidiness: the DEM has no tiles over ocean and its
    zeros there shade as a flat plain, which would be ink asserting something
    untrue about the sea floor.

    Returned rather than drawn so a test can measure what it covers without
    rendering, and so the detail box reuses the composition instead of
    restating it.
    """
    import rasterio
    from rasterio.features import geometry_mask

    if hillshade is None:
        with rasterio.open(geo.HILLSHADE) as src:
            if window is None:
                hillshade, transform = src.read(1), src.transform
                bounds = src.bounds
            else:
                # Read only the window. Drawing the whole eight-degree raster
                # into a 0.75 degree panel and clipping it puts five million
                # pixels in the file to show forty thousand; measured, that
                # alone was 0.9 MB of the vector output.
                from rasterio.windows import from_bounds
                pad = 0.05
                box = from_bounds(window.west - pad, window.south - pad,
                                  window.east + pad, window.north + pad,
                                  src.transform)
                hillshade = src.read(1, window=box)
                transform = src.window_transform(box)
                bounds = rasterio.windows.bounds(box, src.transform)
                bounds = type("B", (), dict(zip(
                    ("left", "bottom", "right", "top"), bounds)))
            extent = (bounds.left, bounds.right, bounds.bottom, bounds.top)
    else:
        west, east, south, north = extent
        transform = rasterio.transform.from_bounds(
            west, south, east, north, hillshade.shape[1], hillshade.shape[0])

    if panel_width_cm is not None:
        hillshade, transform = _reduce(hillshade, transform, panel_width_cm)

    base = style.relief_cmap()(style.relief_normalise(hillshade))[..., :3]
    inside_mask = ~geometry_mask(provinces.geometry, out_shape=hillshade.shape,
                                 transform=transform, invert=False)

    def composite(role_name, alpha):
        import matplotlib.colors as mcolors
        target = np.array(mcolors.to_rgb(style.role(role_name)))
        return base * (1.0 - alpha) + target * alpha

    rgb = composite("land_outside", style.LAND_VEIL_ALPHA)
    rgb[inside_mask] = composite("province_fill",
                                 style.REGION_TINT_ALPHA)[inside_mask]

    # Everything outside the land polygons is clipped away when drawn, so what
    # it holds is invisible -- but it is still encoded into the vector file,
    # and a hillshade compresses badly. Flattening it to one colour costs
    # nothing visible and made the embedded image markedly smaller, because a
    # constant region is what a deflate stream is good at.
    import matplotlib.colors as mcolors
    land_mask = ~geometry_mask(land.geometry, out_shape=hillshade.shape,
                               transform=transform, invert=False)
    rgb[~land_mask] = np.array(mcolors.to_rgb(style.role("sea")))

    return {"rgb": rgb, "extent": extent,
            "land_path": geo.polygon_path(land.geometry),
            "land_fraction": float(land_mask.mean()),
            "inside_fraction": float(inside_mask.mean())}


def _reduce(hillshade, transform, panel_width_cm: float):
    """Decimate the relief to what the panel can actually show."""
    from PIL import Image
    import rasterio

    target = int(round(panel_width_cm * style.MIN_DPI / 2.54
                       * RELIEF_SUPERSAMPLE))
    if hillshade.shape[1] <= target:
        return hillshade, transform
    scale = target / hillshade.shape[1]
    size = (target, max(int(round(hillshade.shape[0] * scale)), 1))
    reduced = np.asarray(Image.fromarray(hillshade).resize(size, Image.BOX))
    return reduced, transform * rasterio.Affine.scale(
        hillshade.shape[1] / size[0], hillshade.shape[0] / size[1])


def _reduce_rgb(image, panel_width_cm: float):
    """Decimate a three-band image to what its panel can show. See `_reduce`."""
    from PIL import Image

    target = int(round(panel_width_cm * style.MIN_DPI / 2.54
                       * RELIEF_SUPERSAMPLE))
    if image.shape[1] <= target:
        return image
    size = (target, max(int(round(image.shape[0] * target / image.shape[1])), 1))
    return np.asarray(Image.fromarray(image).resize(size, Image.BOX))


#: Artist label for the relief image, so a check for invisible layers can
#: select it by name rather than by type; an inset raster is an AxesImage too.
RELIEF_ARTIST = "relief"


def _draw_relief(ax, land, provinces, layers=None) -> None:
    layers = (relief_image(land, provinces, panel_width_cm=MAP_WIDTH_CM)
              if layers is None else layers)
    image = ax.imshow(layers["rgb"], extent=layers["extent"], origin="upper",
                      interpolation="bilinear", zorder=1, aspect="auto",
                      rasterized=True)
    image.set_clip_path(layers["land_path"], transform=ax.transData)
    image.set_label(RELIEF_ARTIST)


def _outline_detail_window(ax) -> None:
    """The detail box's window, at its true drawn size, on the main panel.

    This is what makes the detail box honest. Enlarged to 4.6 times it is
    legible; the rectangle here is what six cells actually measure on this
    page, and the two together answer "how big is 0.25 degrees" in a way
    neither does alone.
    """
    from matplotlib.patches import Rectangle

    window = DETAIL_WINDOW
    ax.add_patch(Rectangle(
        (window.west, window.south), window.east - window.west,
        window.north - window.south, facecolor="none",
        edgecolor=style.role("boundary"), linewidth=0.6, zorder=8,
        label="detail-window"))


def _label_provinces(ax, provinces) -> None:
    for _, row in provinces.iterrows():
        name = row.get("name_en") or row.get("name")
        if name not in PROVINCE_LABELS:
            continue
        lon, lat = PROVINCE_LABELS[name]
        ax.text(lon, lat, name, ha="center", va="center", zorder=9,
                fontsize=style.LABEL_SIZE, color=style.role("label_text"),
                path_effects=_halo())


def _label_neighbours(ax, neighbours, extent: Extent) -> None:
    """Name every province that shares the frame, at a point inside the frame.

    The point is the clipped polygon's representative point, not its centroid:
    a centroid can fall outside a concave province or outside the frame, and
    both happen here. Nothing is hand-placed, so adding or removing a
    neighbour does not need a new coordinate.
    """
    from shapely.geometry import box

    frame = box(extent.west, extent.south, extent.east, extent.north)
    for _, row in neighbours.iterrows():
        inside = row.geometry.intersection(frame)
        if inside.is_empty:
            continue
        point = inside.representative_point()
        ax.text(point.x, point.y, row["name"], ha="center", va="center",
                zorder=7, fontsize=style.TICK_SIZE - 0.5, style="italic",
                color=style.role("label_text"), path_effects=_halo(1.5))


def _draw_places(ax, places) -> None:
    """The four provincial capitals, one per study province.

    Shanghai's label carries the municipality's name as well as the city's,
    which is why the map has three province labels and four city labels rather
    than four and four. Offsets put each name on the side with room; Shanghai's
    runs east over the sea, which is the only direction that is empty.
    """
    offsets = {"Shanghai": (0.16, 0.0, "left"),
               "Nanjing": (-0.16, 0.02, "right"),
               "Hangzhou": (0.16, -0.06, "left"),
               "Hefei": (-0.16, 0.02, "right")}
    for _, row in places.iterrows():
        name = row["name"]
        ax.plot([row.geometry.x], [row.geometry.y], marker="o", markersize=2.6,
                color=style.role("place_marker"), linestyle="none", zorder=9,
                label="place-marker")
        dx, dy, align = offsets[name]
        ax.text(row.geometry.x + dx, row.geometry.y + dy, name, ha=align,
                va="center", zorder=9, fontsize=style.TICK_SIZE,
                color=style.role("label_text"), path_effects=_halo())


def _halo(width: float = 1.8):
    """A white outline behind label text, so a name stays readable on relief.

    Not decoration. Without it a name crossing a boundary line or a shaded
    slope is unreadable, and the alternative is moving the name off the thing
    it names.
    """
    from matplotlib import patheffects
    return [patheffects.withStroke(linewidth=width,
                                   foreground=style.role("label_halo"))]


def _legend(ax) -> None:
    """Retained so a caller can still put the keys on the map itself."""
    ax.legend(handles=_legend_handles(), loc="lower left",
              labelcolor=style.role("label_text"), handlelength=1.4,
              borderpad=0.45, framealpha=0.92, frameon=True,
              facecolor=style.role("page"), edgecolor="none")


def _legend_handles():
    """Keys for the four areal and point classes the main panel draws.

    The two land keys carry the relief tone at the flat-ground position of the
    band rather than a flat colour, because flat is what most of the map is
    and a key showing a tone the map does not hold is worse than no key.
    """
    from matplotlib.lines import Line2D
    from matplotlib.patches import Patch

    flat = style.relief_cmap()(style.RELIEF_FLAT_POSITION)[:3]
    inside = style.veil(flat, style.role("province_fill"),
                        style.REGION_TINT_ALPHA)
    outside = style.veil(flat, style.role("land_outside"),
                         style.LAND_VEIL_ALPHA)
    return [
        Patch(facecolor=inside, edgecolor=style.role("boundary"),
              linewidth=0.8, label="study provinces"),
        Patch(facecolor=outside, edgecolor=style.role("boundary_minor"),
              linewidth=0.4, label="neighbouring provinces"),
        Patch(facecolor=style.role("sea"), edgecolor=style.role("coastline"),
              linewidth=0.5, label="sea"),
        Line2D([], [], marker="o", markersize=2.6, linestyle="none",
               color=style.role("place_marker"), label="provincial capital"),
    ]


def _column_legend(fig, x_cm, top_cm, width_cm, height_cm) -> None:
    """The keys, in the right-hand column rather than on the map.

    They used to sit in the map's lower-left corner. Off the map they cover no
    geography at all, and the column has the room because a portrait map
    leaves it: this is the same reasoning that moved the inset out of the
    frame, applied to the other thing that was sitting on the data.
    """
    legend = fig.legend(handles=_legend_handles(),
                        loc="upper left",
                        bbox_to_anchor=(x_cm / width_cm, top_cm / height_cm),
                        labelcolor=style.role("label_text"), handlelength=1.4,
                        borderpad=0.0, borderaxespad=0.0, frameon=False,
                        labelspacing=0.55, handletextpad=0.6)
    legend.set_in_layout(False)


# --------------------------------------------------------------------------
# the detail box
# --------------------------------------------------------------------------

def _draw_detail(ax, spec, land) -> None:
    """Six analysis cells over a real coastline, enlarged so they read.

    **No coastline stroke**, which is a measured decision rather than an
    omission. A lattice line here crosses both sea and relief, so it carries
    the coastline's two-sided constraint as well as its own; with the relief
    band's floor at 0.74 there is no assignment that holds sea, a coastline
    and a lattice line all 0.15 apart in luminance and all clear of the band.
    The tone step from sea to lit relief is 0.47 at this size, which is three
    times what a stroke would add, so the stroke is what was dropped. See
    `src/figures/style.py`.
    """
    window = DETAIL_WINDOW
    ax.set_facecolor(style.role("sea"))

    # The whole detail window lies inside Jiangsu and Shanghai, so the study
    # region's treatment is the right one everywhere in it; `land` is passed
    # as the province layer to say exactly that.
    _draw_relief(ax, land, land,
                 relief_image(land, land, window=window,
                              panel_width_cm=COLUMN_CM))

    lons, lats = geo.cell_edges(spec)
    for value in lons[(lons >= window.west - 1e-9) & (lons <= window.east + 1e-9)]:
        ax.plot([value, value], [window.south, window.north],
                color=style.role("lattice"), linewidth=0.5, zorder=3)
    for value in lats[(lats >= window.south - 1e-9) & (lats <= window.north + 1e-9)]:
        ax.plot([window.west, window.east], [value, value],
                color=style.role("lattice"), linewidth=0.5, zorder=3)

    geo.apply_projection(ax, window)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.7)
        spine.set_edgecolor(style.role("boundary"))


def cell_kilometres(spec, latitude: float) -> tuple[float, float]:
    """One cell's east-west and north-south extent in km at ``latitude``.

    On the authalic sphere this project measures areas on, so the number in
    the figure and the numbers in the tables come from one definition of the
    Earth. A scale bar was rejected -- it is correct along one parallel only
    on this projection -- and this is what replaces it: a statement about one
    cell at one stated latitude, which is a claim that survives being read off
    the wrong part of the map.
    """
    radius = 6371.0072  # authalic mean radius, km
    metre = np.radians(1.0) * radius
    return (spec.resolution * metre * float(np.cos(np.radians(latitude))),
            spec.resolution * metre)


# --------------------------------------------------------------------------
# the inset
# --------------------------------------------------------------------------

def _inset_ratio() -> float:
    """Drawn height over drawn width for the inset, from its own raster."""
    _, (west, east, south, north) = geo.read_raster(geo.INSET_RELIEF)
    return (north - south) / (east - west)


def _draw_inset(ax, extent: Extent) -> None:
    """A locator, off the data, that asserts nothing about any boundary.

    It sits in the right-hand column rather than in a corner of the map. The
    first version covered Zhejiang's coast and the Zhoushan archipelago, which
    is data, to save space the figure was not short of.

    **What it draws, and what it deliberately does not.** Natural Earth's 50 m
    hypsometric relief across the whole extent, which has no opinion about
    anyone's borders; over it, every admin-0 land boundary line Natural Earth
    files in that extent, unfiltered and with no country named or filled; and
    the study box.

    The previous inset outlined the 31 admin-1 units filed under
    ``admin = "China"`` in Natural Earth's 50 m layer, which excluded Taiwan,
    Hong Kong and Macau. That exclusion was inherited rather than chosen, and
    it was not even the mechanism it was documented as: the 50 m admin-1 layer
    has no Taiwan, Hong Kong or Macau features to exclude. Only the 10 m layer
    carries them, as 21, 1 and 1 units against China's 32.

    So nothing is filtered here. Taiwan and Hainan appear as their coastlines
    do, like Kyushu. Hong Kong and Macau are not distinguished, because the
    boundary-lines layer carries no feature for either. Natural Earth classes
    six of the lines in this extent as "Disputed (please verify)" and ships
    per-country viewpoint fields -- `FCLASS_CN`, `FCLASS_TW`, `FCLASS_IN` and
    thirty more -- which is the source's own statement that the
    classification depends on who is asked. The caption says whose lines these
    are and that this repository takes no position on any of them.

    Hypsometric rather than grey, because nothing is drawn over the inset and
    the reason the main panel's relief is grey does not apply.
    """
    relief, bounds = geo.read_raster(geo.INSET_RELIEF)
    relief = _reduce_rgb(relief, COLUMN_CM)
    west, east, south, north = bounds
    ax.imshow(relief, extent=(west, east, south, north), origin="upper",
              zorder=1, aspect="auto", interpolation="bilinear",
              rasterized=True, label="inset-relief")

    lines = geo.read_layer(geo.INSET_BOUNDARIES).to_crs(geo.CHINA_ALBERS)
    lines.plot(ax=ax, color=style.role("boundary"), linewidth=0.35, zorder=2)

    corners = _study_box_in_albers(extent)
    ax.plot(corners[0], corners[1], color=style.role("boundary"),
            linewidth=1.1, zorder=3, solid_joinstyle="miter",
            path_effects=_halo(2.4))

    ax.set_xlim(west, east)
    ax.set_ylim(south, north)
    ax.set_aspect("auto")
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.7)
        spine.set_edgecolor(style.role("boundary"))


def _study_box_in_albers(extent: Extent):
    """The study box as a closed ring, densified before projecting.

    A four-point rectangle projected corner to corner draws straight lines
    where the projection bends them, and at this extent the error is visible.
    Twenty-five points a side is enough that it is not.
    """
    steps = 25
    west = np.full(steps, extent.west)
    east = np.full(steps, extent.east)
    south = np.full(steps, extent.south)
    north = np.full(steps, extent.north)
    lons = np.linspace(extent.west, extent.east, steps)
    lats = np.linspace(extent.south, extent.north, steps)
    ring_lon = np.concatenate([lons, east, lons[::-1], west])
    ring_lat = np.concatenate([south, lats, north, lats[::-1]])
    ring_lon = np.append(ring_lon, ring_lon[0])
    ring_lat = np.append(ring_lat, ring_lat[0])
    return geo.to_albers(ring_lon, ring_lat)


# --------------------------------------------------------------------------
# the column's text
# --------------------------------------------------------------------------

#: Required by Article 6(b) of the Copernicus WorldDEM-90 licence, for data
#: that have been adapted or modified, and quoted verbatim. It is on the figure
#: as well as in the caption because a figure travels away from its caption and
#: the obligation attaches to the image. This is not the coordinate-system
#: stamp the standard forbids; that is a machine's default, this is a licence
#: condition.
DEM_NOTICE = (
    "Relief: produced using Copernicus WorldDEM\u2122-90\n"
    "\u00a9 DLR e.V. 2010\u20132014 and \u00a9 Airbus Defence and\n"
    "Space GmbH 2014\u20132018 provided under COPERNICUS\n"
    "by the European Union and ESA; all rights reserved.\n"
    "Boundaries, places and inset relief: Natural Earth,\n"
    "public domain.")

#: What the inset does and does not claim, said on the figure rather than only
#: in the caption, for the same reason as the licence notice: an inset that
#: draws national boundaries and says nothing about them is read as asserting
#: them.
INSET_NOTE = ("Locator. Boundary lines as Natural\n"
              "Earth draws them; no country named,\n"
              "filled or excluded.")


def _detail_note(spec) -> str:
    east_west, north_south = cell_kilometres(
        spec, DETAIL_WINDOW.centre_latitude)
    return (f"Analysis cells, {spec.resolution:g}\u00b0, at "
            f"{_detail_scale():.1f}\u00d7 the main\n"
            f"panel. One cell is {east_west:.0f} by {north_south:.0f} km at "
            f"{DETAIL_WINDOW.centre_latitude:g}\u00b0N.\n"
            f"The same six are outlined on the map\n"
            f"at their drawn size.")


def _column_note(fig, x_cm, y_cm, width_cm, height_cm, text, size,
                 va: str = "top") -> None:
    """A block of small text in the column, at a stated place on the page.

    Line breaks are written into the string rather than left to matplotlib's
    ``wrap``, which measures against the figure and not against the column and
    ran the first draft's detail caption off the right-hand edge.
    """
    fig.text(x_cm / width_cm, y_cm / height_cm, text, ha="left", va=va,
             fontsize=size, color=style.role("label_text"), linespacing=1.35)


def _detail_scale() -> float:
    """How many times larger the detail box draws a degree than the map does."""
    spec = geo.study_spec()
    extent = geo.lattice_extent(spec)
    map_width = FIG_WIDTH_CM - (LEFT_CM + GUTTER_CM + COLUMN_CM + RIGHT_CM)
    main = (extent.east - extent.west) / map_width
    detail = (DETAIL_WINDOW.east - DETAIL_WINDOW.west) / COLUMN_CM
    return main / detail
