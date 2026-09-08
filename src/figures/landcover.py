"""Land cover at the resolution it was measured, and at the resolution used.

Everything else in this repository draws land cover as a fraction per 0.25
degree cell. The products underneath are 30 m impervious surface and 10 m rice
classification, and the reproduction has never shown either, so a reader sees
fractions and never sees the thing being fractioned. This figure is the only
place the data the 2023 thesis rests on appears as itself.

**The subject is the aggregation, not the window.** Four panels: two impervious
products at 30 m, one rice classification at 10 m, and the same ground as the
six numbers the analysis actually consumes. What the fourth panel discards is
the other three.

The window
----------

118.44 to 118.49 east, 31.3248 to 31.3582 north, on the eastern edge of Wuhu
in Anhui: 5.7 by 3.7 km, 23.9 percent impervious under GISA and 34.2 percent
rice, of which 4.9 points are double-season. `scripts/clip_landcover_window.py` records what
it had to satisfy and what was rejected. Two constraints are worth repeating
because they are the ones a reader would otherwise have to trust:

* **It lies wholly inside Anhui**, tested with ``contains`` rather than by eye.
  That matters more here than at cell scale: the NESDC rasters declare no
  nodata and 0 means both real non-rice land and out-of-province background, so
  a window across a boundary would draw two different things in one colour.
* **It lies wholly inside one analysis cell**, the one centred at 31.325 N,
  118.425 E. So the native pixels and the number they become are the same
  ground, and panel (d) can say which number.

**It is not a representative sample and the caption says so.** The window is
34.2 percent rice against 19.5 percent for the cell that contains it, and 23.9
percent impervious against 26.3. It is a place to see the resolution, not to
estimate anything from.

Why both impervious products
----------------------------

GISA and GAIA disagree about this window in the same direction and by nearly
the same amount as they disagree over the four provinces: 23.9 percent against
29.7, a ratio of 0.805 where the four-province 2018 ratio is 0.801. Drawing
both is what makes the disagreement in the change figure something a reader has
seen at 30 m rather than a number they are told. It is one extra panel and it
costs the figure nothing else, because the two share a window, a resolution and
a colour.

What cannot be drawn beside this
--------------------------------

There is no high-resolution methane panel and there cannot be one. TROPOMI's
footprint is 7 by 7 km at nadir, the analysis grid is 0.25 degrees because
coverage forced it there, and per-cell sounding counts run from 1 to 410. A
fine-resolution methane field from this data would be interpolation presented
as observation, which the literature separates from a display choice and which
this repository has already declined to do once, in the composite figure's
treatment of its 97 empty cells.
"""

from __future__ import annotations

import numpy as np

from . import geo, style
from .geo import Extent

#: Committed clips, at the products' own resolutions and pixel values.
PROCESSED = geo.REFERENCE_DIR.parents[0] / "processed"
IMPERVIOUS_GISA = PROCESSED / "landcover_window_impervious_gisa.tif"
IMPERVIOUS_GAIA = PROCESSED / "landcover_window_impervious_gaia.tif"
RICE_NESDC = PROCESSED / "landcover_window_rice_nesdc.tif"
GRID = PROCESSED / "analysis_grid_2018.csv"
GRID_GISA = PROCESSED / "impervious_gisa_2018.csv"

#: The native-resolution window. Matches `scripts/clip_landcover_window.py`.
WINDOW = Extent(west=118.44, east=118.49, south=31.3248, north=31.3582)

#: The 3 by 2 analysis cells panel (d) draws, on cell edges, with the window's
#: own cell in the middle of the lower row.
CELLS = Extent(west=118.05, east=118.80, south=31.20, north=31.70)

#: The year both products are drawn for. The analysis year throughout.
YEAR = 2018

#: GISA's cumulative extent through 2018 and GAIA's, as selector arguments.
#: Neither is written as a comparison here; see `src.landcover.selectors`.
GISA_2018_CODE = 36
GAIA_EPOCH = 2023

# Layout in centimetres, and every panel is the same shape. Panel width is
# what sets the drawn pixels per native pixel, so it is stated rather than
# derived: at 6.875 cm and 300 dpi a panel is 812 pixels, which is 1.46 drawn
# pixels for each of the 557 native rice pixels across the window and 4.37 for
# each of the 186 impervious ones. Both above one, which is the whole claim,
# and `scripts/make_landcover_figure.py` prints them.
#
# The window's height was chosen so that all four panels draw in one
# proportion, 0.782, which is the shape of the three-by-two block of analysis
# cells. Four panels on one grid rather than one of them standing 0.9 cm
# taller than the rest.
FIG_WIDTH_CM = style.FULL_WIDTH_CM
LEFT_CM = 1.25        # a latitude label here reads "31.35°N", not "35°N"
PANEL_CM = 6.875
GUTTER_CM = 0.75
RIGHT_CM = 1.25       # the right column's tick labels sit outside its frame
LEGEND_CM = 1.02      # keys, then the source note below them
TICKS_CM = 0.48       # room under a panel for its longitude labels
TITLE_CM = 0.40       # room over a panel for its name
BOTTOM_CM = LEGEND_CM + 0.42 + TICKS_CM
TOP_CM = 0.18

WIDTH_CM = FIG_WIDTH_CM


def landcover_figure(width_cm: float = WIDTH_CM, height_cm: float | None = None):
    """Build and return the native-resolution land cover figure. Writes nothing.

    Four panels on a two by two grid: two impervious products at 30 m, the rice
    classification at 10 m, and the six numbers those become.
    """
    panel_h = PANEL_CM * geo.display_ratio(WINDOW)
    row2 = BOTTOM_CM
    row1 = row2 + panel_h + TITLE_CM + TICKS_CM
    if height_cm is None:
        height_cm = row1 + panel_h + TITLE_CM + TOP_CM
    fig = style.figure(width_cm=width_cm, height_cm=height_cm)

    def axes(x_cm, y_cm, w_cm, h_cm):
        return fig.add_axes((x_cm / width_cm, y_cm / height_cm,
                             w_cm / width_cm, h_cm / height_cm))

    right_x = LEFT_CM + PANEL_CM + GUTTER_CM
    ax_gisa = axes(LEFT_CM, row1, PANEL_CM, panel_h)
    ax_gaia = axes(right_x, row1, PANEL_CM, panel_h)
    ax_rice = axes(LEFT_CM, row2, PANEL_CM, panel_h)
    ax_cells = axes(right_x, row2, PANEL_CM, panel_h)

    _draw_impervious(ax_gisa, IMPERVIOUS_GISA, "gisa")
    _draw_impervious(ax_gaia, IMPERVIOUS_GAIA, "gaia")
    _draw_rice(ax_rice)
    _draw_cells(ax_cells)

    # The right column's latitude labels go on its right, outside the figure's
    # own gutter. Left of the frame they land on the neighbouring panel, which
    # the first draft demonstrated.
    for ax in (ax_gaia, ax_cells):
        ax.yaxis.tick_right()

    for ax, letter in ((ax_gisa, "a"), (ax_gaia, "b"), (ax_rice, "c"),
                       (ax_cells, "d")):
        _title(fig, ax, letter, height_cm)
    _keys(fig, width_cm, height_cm)
    return fig


def _title(fig, ax, letter: str, height_cm) -> None:
    """The panel letter and its name, over the panel, as one string.

    One string rather than `style.panel_label` plus a separate title, because
    the two were drawn at the same point and overprinted.
    """
    box = ax.get_position()
    fig.text(box.x0, box.y1 + 0.09 / height_cm, f"({letter}) {TITLES[letter]}",
             ha="left", va="bottom", fontsize=style.LABEL_SIZE,
             fontweight="bold", color=style.role("label_text"))

# --------------------------------------------------------------------------
# the native panels
# --------------------------------------------------------------------------

def impervious_mask(path, product: str):
    """The impervious pixels of a committed window clip, and its extent.

    The selector comes from :mod:`src.landcover.selectors`, so the rule that
    decides what counts is the same object here, in the provincial totals and
    in the display-grid aggregation. The two products encode the year in
    opposite directions and getting one backwards does not fail loudly: it
    inverts the urbanisation history and still draws a plausible map.
    """
    from src.landcover.selectors import at_least, between

    values, extent = geo.read_raster(path)
    selector = (between(1, GISA_2018_CODE) if product == "gisa"
                else at_least(GAIA_EPOCH - YEAR))
    return selector(values), extent, selector.description


def _draw_impervious(ax, path, product: str) -> None:
    mask, extent, _ = impervious_mask(path, product)
    _draw_classes(ax, mask.astype("uint8"),
                  [style.role("land_flat"), style.role("impervious")],
                  extent, f"impervious-{product}")
    _frame_window(ax)


def rice_classes():
    """The rice class raster of the committed window clip, and its extent.

    Returned as read. 0 is non-rice, 1 single-season, 2 double-season, and no
    nodata is declared; inside this window every 0 is real non-rice land,
    because the window is wholly inside the province the raster is for.
    """
    return geo.read_raster(RICE_NESDC)


def _draw_rice(ax) -> None:
    values, extent = rice_classes()
    _draw_classes(ax, values,
                  [style.role("land_flat"), style.role("rice_single"),
                   style.role("rice_double")], extent, "rice-nesdc")
    _frame_window(ax)


def _draw_classes(ax, values, colours, extent, label: str) -> None:
    """A small categorical raster, at its own resolution, nothing resampled.

    ``interpolation="nearest"`` is the point of the figure rather than a
    default: any other setting invents intermediate values between classes that
    have no intermediate, and would draw a 10 m pixel as a smudge.
    """
    from matplotlib.colors import BoundaryNorm, ListedColormap

    cmap = ListedColormap(colours)
    norm = BoundaryNorm(np.arange(len(colours) + 1) - 0.5, len(colours))
    image = ax.imshow(values, extent=extent, origin="upper", cmap=cmap,
                      norm=norm, interpolation="nearest", aspect="auto",
                      zorder=1)
    image.set_label(label)


def _frame_window(ax) -> None:
    geo.apply_projection(ax, WINDOW)
    ticks = np.arange(118.45, WINDOW.east, 0.02)
    ax.set_xticks(ticks)
    ax.set_yticks(np.arange(31.33, WINDOW.north, 0.02))
    ax.xaxis.set_major_formatter(geo.degree_formatter("x"))
    ax.yaxis.set_major_formatter(geo.degree_formatter("y"))
    ax.tick_params(length=2.5)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.7)
        spine.set_edgecolor(style.role("boundary"))


# --------------------------------------------------------------------------
# what the analysis consumes
# --------------------------------------------------------------------------

def cell_values():
    """The committed per-cell fractions for the cells panel (d) draws.

    Read from the analysis grid and the GISA companion rather than recomputed,
    so the numbers on the figure are the numbers the baselines were fitted on.
    """
    import csv

    def read(path, keys):
        out = {}
        with open(path, newline="") as handle:
            for row in csv.DictReader(handle):
                key = (round(float(row["centre_lat"]), 3),
                       round(float(row["centre_lon"]), 3))
                out[key] = {k: (float(row[k]) if row.get(k) not in ("", None)
                                else float("nan")) for k in keys}
        return out

    grid = read(GRID, ("impervious_fraction", "rice_fraction_single",
                       "rice_fraction_combined", "rice_coverage",
                       "impervious_coverage"))
    gisa = read(GRID_GISA, ("impervious_fraction",))
    spec = geo.study_spec()
    out = {}
    lat = CELLS.north - spec.resolution / 2
    while lat > CELLS.south:
        lon = CELLS.west + spec.resolution / 2
        while lon < CELLS.east:
            key = (round(lat, 3), round(lon, 3))
            if key in grid:
                out[key] = dict(grid[key],
                                impervious_gisa=gisa[key]["impervious_fraction"])
            lon += spec.resolution
        lat -= spec.resolution
    return out


def _draw_cells(ax) -> None:
    """Six analysis cells, with the numbers rather than two more colour panels.

    The choice, stated because it was a choice. Two more colour panels would
    show a reader that the fraction varies across six cells, which they can
    already see from the three panels above. What they cannot recover is the
    value, and the value is what the model was fitted on. Six cells with a
    number in each is the whole of what the analysis consumes over this ground,
    written out; a ramp would be a picture of it.
    """
    from matplotlib.patches import Rectangle

    spec = geo.study_spec()
    ax.set_facecolor(style.role("land_flat"))
    for (lat, lon), values in cell_values().items():
        west = lon - spec.resolution / 2
        south = lat - spec.resolution / 2
        ax.add_patch(Rectangle(
            (west, south), spec.resolution, spec.resolution, facecolor="none",
            edgecolor=style.role("lattice"), linewidth=0.6, zorder=3,
            label="analysis-cell"))
        rice = values["rice_fraction_combined"]
        text = (f"GISA {values['impervious_gisa']:.3f}\n"
                f"GAIA {values['impervious_fraction']:.3f}\n"
                f"rice {rice:.3f}")
        # High in the cell rather than centred: the native window sits on
        # this cell's centre, which is where the text used to be.
        ax.text(lon, lat + 0.072, text, ha="center", va="center", zorder=5,
                fontsize=style.TICK_SIZE - 1.0, linespacing=1.35,
                color=style.role("label_text"), path_effects=_halo())

    ax.add_patch(Rectangle(
        (WINDOW.west, WINDOW.south), WINDOW.east - WINDOW.west,
        WINDOW.north - WINDOW.south, facecolor=style.role("impervious"),
        edgecolor=style.role("boundary"), linewidth=0.7, zorder=4,
        label="native-window"))
    # Named on the panel, because an unlabelled rectangle inside a cell is a
    # reader's problem and the caption is not where they will look first.
    ax.text(WINDOW.east + 0.012, 0.5 * (WINDOW.south + WINDOW.north),
            "(a)–(c)", ha="left", va="center", zorder=5,
            fontsize=style.TICK_SIZE - 1.0, color=style.role("label_text"),
            path_effects=_halo())

    geo.apply_projection(ax, CELLS)
    ax.set_xticks(np.arange(118.05, CELLS.east + 1e-9, 0.25))
    ax.set_yticks(np.arange(31.20, CELLS.north + 1e-9, 0.25))
    ax.xaxis.set_major_formatter(geo.degree_formatter("x"))
    ax.yaxis.set_major_formatter(geo.degree_formatter("y"))
    ax.tick_params(length=2.5)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.7)
        spine.set_edgecolor(style.role("boundary"))


def _halo(width: float = 2.0):
    from matplotlib import patheffects
    return [patheffects.withStroke(linewidth=width,
                                   foreground=style.role("label_halo"))]


# --------------------------------------------------------------------------
# titles, keys and the notes the caption cannot carry
# --------------------------------------------------------------------------

TITLES = {
    "a": "GISA impervious, 30 m",
    "b": "GAIA impervious, 30 m",
    "c": "NESDC rice, 10 m",
    "d": "what the analysis reads: 0.25° cells",
}

#: The source asymmetry, on the figure because it is a caution about reading
#: the two panels against each other and a reader meets the panels first.
SOURCE_NOTE = (
    "GISA and GAIA are 30 m from Landsat; NESDC rice is 10 m from Sentinel-1 "
    "and Sentinel-2 by time-weighted dynamic time warping. The rice grid is "
    "three times finer and that buys the analysis nothing: both are averaged "
    "into the same 0.25° cell, about 24 by 28 km here.")


def _keys(fig, width_cm, height_cm) -> None:
    """The four classes, then the source note, both across the full width."""
    from matplotlib.patches import Patch

    handles = [
        Patch(facecolor=style.role("impervious"),
              edgecolor=style.role("boundary"), linewidth=0.5,
              label="impervious surface"),
        Patch(facecolor=style.role("rice_single"),
              edgecolor=style.role("boundary"), linewidth=0.5,
              label="rice, single season"),
        Patch(facecolor=style.role("rice_double"),
              edgecolor=style.role("boundary"), linewidth=0.5,
              label="rice, double season"),
        Patch(facecolor=style.role("land_flat"),
              edgecolor=style.role("boundary"), linewidth=0.5,
              label="neither, and looked at"),
    ]
    legend = fig.legend(
        handles=handles, loc="lower left", ncols=4,
        bbox_to_anchor=(LEFT_CM / width_cm, LEGEND_CM / height_cm),
        labelcolor=style.role("label_text"), handlelength=1.3, borderpad=0.0,
        borderaxespad=0.0, frameon=False, columnspacing=2.4,
        handletextpad=0.5)
    legend.set_in_layout(False)

    fig.text(LEFT_CM / width_cm, 0.12 / height_cm, _wrap(SOURCE_NOTE, 124),
             ha="left", va="bottom", fontsize=style.TICK_SIZE - 1.5,
             linespacing=1.4, color=style.role("label_text"))


def _wrap(text: str, width: int) -> str:
    """Break a note into lines that fit the column it is written into.

    Written out rather than left to matplotlib's ``wrap``, which measures
    against the figure and not against the space the text was given, and ran
    the study area figure's first draft off the right-hand edge.
    """
    import textwrap
    return "\n".join(textwrap.wrap(text, width))
