"""Paddy rice across the four provinces, and what competes with it for land.

The gap the set was built around without containing. Rice is the study's
subject and what the 2023 thesis's own figures showed, and until now it
appeared here only inside a 5.7 by 3.7 km window in Wuhu.

What this figure is, and is not
-------------------------------

**One map of rice, and the numbers beside it.** Not two maps. Regional
impervious surface already has two maps in `urban_change.py`, drawn from the
same aggregate at the same resolution, so a third would add no information;
and the competition for land is not legible as two maps side by side at
1.4 km, where a cell can hold both. It is legible as numbers per province,
which panel (b) carries, and at 10 m in `landcover.py`, which shows the
abutment directly.

There is a second reason and it is a measured one. The areal palette cannot
hold rice's classes plus impervious plus the sea. Double-season paddy reaches
the Zhejiang coastline -- minimum distance 0.0 km, first percentile 0.3 km --
so both rice classes are adjacent to the sea, which is pinned at luminance
0.42 by the relief band in `study_area.py`. That leaves two narrow intervals
for areal fills, [0.228, 0.27] and [0.57, 0.769], with room for exactly three
tones. Rice takes two of them and the unclassified class takes the third.
Adding impervious would have put a fourth tone in one of the same bands, in a
panel beside the rice map, and the two would have been indistinguishable in a
black and white print.

The threshold, which rice pays differently from urban
-----------------------------------------------------

Same pattern as the urban figure: the 10 m product is aggregated to 1/128
degree, averaged to 1/64 for drawing because that is what the page resolves,
and a cell is inked where enough of it is rice. What is different is the price.

Urban is drawn at a quarter of a cell, a round number, and pays 0.73 to 1.31
across its three years because no threshold does better. Rice can do better,
because the map draws one quantity rather than three: :data:`THRESHOLD` is set
where the drawn area equals the true area, and at 0.35 the total inked rice is
**1.05** of the 50,042 km2 the provincial totals record. That is a rule rather
than a round number, and it is available here and not there.

**The two seasons cannot share a threshold.** Measured, single-season rice
area-matches at 0.35 and double-season at 0.17, because double-season paddy is
5.3 percent of the rice and interleaved with single rather than segregated
into blocks of its own. Inking each at its own threshold would make the two
colours mean different densities on one map, so instead one threshold decides
*whether* a cell is rice and the colour says *which season that cell's rice
mostly is*. The cost is stated: the double-season colour covers 1,191 km2
against a true 2,677, and panel (b) carries the true areas.

The brief's expectation was the opposite of what was measured. Paddy in a
delta is contiguous and was expected to make a threshold cheaper than it is
for dispersed rural impervious surface. For total rice it is cheaper -- 1.05
against 1.31. Split by season it is dearer: at a common 0.25 the two rice
classes come out at 1.70 and 0.43, a spread of 4.0 against urban's 1.8.

Absence has two meanings and the map draws both
-----------------------------------------------

The NESDC rasters declare no nodata and their 0 means non-rice land *and*
out-of-province background, so `unassessed` is a class here rather than a
footnote. Two causes, one meaning: land outside the four provinces, which the
product does not cover at all, and the part of Anhui the product does not
classify. Every annual raster terminates classification at 33.3462 N and
115.2682 E to within 22 metres, which is a processing boundary rather than an
absence of rice -- GloRice puts about 320 km2 of rice in it -- and
`scripts/compute_rice_extent.py` measures the assessed area at 0.8611 of the
Anhui polygon, independently reproducing the 86.1 percent already recorded.

Drawing that region as `land_flat` would have said northern Anhui grows no
rice. It is drawn dark instead, because the light end of the scale is taken
and because a blanked region should not read as an empty one.
"""

from __future__ import annotations

import csv

import numpy as np

from . import geo, style

PROCESSED = geo.REFERENCE_DIR.parents[0] / "processed"
RICE_EXTENT = PROCESSED / "rice_extent_2018.tif"
RICE_TOTALS = PROCESSED / "rice_extent_totals_2018.csv"
URBAN_TOTALS = PROCESSED / "urban_extent_totals.csv"

YEAR = 2018
PROVINCES = ("Shanghai", "Jiangsu", "Zhejiang", "Anhui")

#: A drawn cell is rice where at least this much of it is. Set where the drawn
#: area equals the true area, not chosen: see the module docstring.
THRESHOLD = 0.35

#: How many stored cells go into one drawn cell, per axis. Same reasoning as
#: `urban_change.DISPLAY_FACTOR`: 1/128 into a 9.3 cm panel would ask the page
#: for 0.90 pixels a cell and alias.
DISPLAY_FACTOR = 2

#: Below this share of a cell classified, the cell is drawn as unassessed. Low
#: rather than a half, because a coastal cell can be four-fifths sea and still
#: have every scrap of its land classified, and a half would draw a one-cell
#: fringe of false absence all along the coast.
ASSESSED_FLOOR = 0.20

#: Which impervious product panel (b) quotes. GAIA is what the analysis grid
#: carries; GISA differs by a fifth in 2018 and the urban figure is where that
#: is drawn out.
IMPERVIOUS_PRODUCT = "GAIA"

# Layout in centimetres.
FIG_WIDTH_CM = style.FULL_WIDTH_CM
LEFT_CM = 1.15
MAP_CM = 9.30
PANEL_GAP_CM = 1.15
BARS_CM = 4.80
RIGHT_CM = 0.60
NOTE_CM = 0.12
LEGEND_CM = 1.55
TICKS_CM = 0.50
TITLE_CM = 0.40
BOTTOM_CM = LEGEND_CM + 0.95 + TICKS_CM
TOP_CM = 0.18

WIDTH_CM = FIG_WIDTH_CM


def landcover_regional_figure(width_cm: float = WIDTH_CM,
                              height_cm: float | None = None):
    """Build and return the regional land cover figure. Writes nothing."""
    extent = geo.lattice_extent(geo.study_spec())
    map_h = MAP_CM * geo.display_ratio(extent)
    if height_cm is None:
        height_cm = BOTTOM_CM + map_h + TITLE_CM + TOP_CM
    fig = style.figure(width_cm=width_cm, height_cm=height_cm)

    def axes(x_cm, y_cm, w_cm, h_cm):
        return fig.add_axes((x_cm / width_cm, y_cm / height_cm,
                             w_cm / width_cm, h_cm / height_cm))

    ax_map = axes(LEFT_CM, BOTTOM_CM, MAP_CM, map_h)
    ax_bars = axes(LEFT_CM + MAP_CM + PANEL_GAP_CM, BOTTOM_CM, BARS_CM, map_h)

    _draw_rice_map(ax_map, extent)
    _draw_shares(ax_bars)

    titles = {"a": f"NESDC rice, {YEAR}", "b": "share of each province"}
    for ax, letter in ((ax_map, "a"), (ax_bars, "b")):
        box = ax.get_position()
        fig.text(box.x0, box.y1 + 0.09 / height_cm,
                 f"({letter}) {titles[letter]}", ha="left", va="bottom",
                 fontsize=style.LABEL_SIZE, fontweight="bold",
                 color=style.role("label_text"))
    _keys(fig, width_cm, height_cm)
    return fig


# --------------------------------------------------------------------------
# the map
# --------------------------------------------------------------------------

def display_bands(factor: int = DISPLAY_FACTOR):
    """The committed fractions, averaged to what the page resolves.

    Three bands: single-season, double-season, and the share of the cell the
    product classified. Averaging happens on the fractions, before any
    threshold, so a drawn cell is a statement about its own 1.4 km square
    rather than about whether any of four sub-cells passed.
    """
    bands, extent = geo.read_raster(RICE_EXTENT)
    fractions = np.moveaxis(np.asarray(bands), -1, 0) / 100.0
    if factor > 1:
        n, rows, cols = fractions.shape
        fractions = fractions[:, :rows // factor * factor,
                              :cols // factor * factor]
        fractions = fractions.reshape(
            n, fractions.shape[1] // factor, factor,
            fractions.shape[2] // factor, factor).mean(axis=(2, 4))
    return fractions, extent


def rice_classes(threshold: float = THRESHOLD, factor: int = DISPLAY_FACTOR):
    """Class per drawn cell, and the extent.

    0 unassessed, 1 assessed with no rice above the threshold, 2 rice mostly
    single-season, 3 rice mostly double-season. One threshold decides whether
    a cell is rice; the season only decides which of the two rice colours it
    takes, because the two cannot share a threshold and must not be inked at
    different densities on one map.
    """
    fractions, extent = display_bands(factor)
    single, double, assessed = fractions
    classes = np.zeros(single.shape, dtype="uint8")
    classes[assessed >= ASSESSED_FLOOR] = 1
    rice = (assessed >= ASSESSED_FLOOR) & (single + double >= threshold)
    classes[rice & (single >= double)] = 2
    classes[rice & (double > single)] = 3
    return classes, extent


def drawn_area_ratio(threshold: float = THRESHOLD) -> dict:
    """Inked area over true area, inside the four provinces.

    The number the caption rests on. Reported for the map's own statement --
    total rice -- and for the double-season colour, which under-draws and says
    so rather than being quietly wrong.
    """
    import rasterio.transform as transform_module
    from rasterio.features import geometry_mask

    provinces = geo.read_layer(geo.PROVINCES)
    classes, extent = rice_classes(threshold)
    west, east, south, north = extent
    transform = transform_module.from_bounds(west, south, east, north,
                                             classes.shape[1], classes.shape[0])
    inside = ~geometry_mask(provinces.geometry, out_shape=classes.shape,
                            transform=transform, invert=False)
    radius = 6371.0072
    step = 1.0 / (128 / DISPLAY_FACTOR)
    latitudes = np.array([north - (row + 0.5) * step
                          for row in range(classes.shape[0])])
    cell_km2 = ((np.radians(step) * radius)
                * (np.radians(step) * radius
                   * np.cos(np.radians(latitudes))))
    truth = provincial_rice()
    total_true = sum(v["single"] + v["double"] for v in truth.values())
    double_true = sum(v["double"] for v in truth.values())

    def area(mask):
        return float((mask * cell_km2[:, None] * inside).sum())

    return {"total": area(classes >= 2) / total_true,
            "double": area(classes == 3) / double_true,
            "total_true_km2": total_true, "double_true_km2": double_true,
            "total_drawn_km2": area(classes >= 2),
            "double_drawn_km2": area(classes == 3)}


def _draw_rice_map(ax, extent) -> None:
    import matplotlib.colors as mcolors

    classes, raster_extent = rice_classes()
    ax.set_facecolor(style.role("sea"))

    colours = [style.role("unassessed"), style.role("land_flat"),
               style.role("rice_single"), style.role("rice_double")]
    rgba = np.zeros(classes.shape + (4,), dtype="float64")
    for value, colour in enumerate(colours):
        mask = classes == value
        rgba[mask, :3] = mcolors.to_rgb(colour)
        rgba[mask, 3] = 1.0
    image = ax.imshow(rgba, extent=raster_extent, origin="upper",
                      interpolation="nearest", aspect="auto", zorder=1)
    land = geo.read_layer(geo.LAND)
    image.set_clip_path(geo.polygon_path(land.geometry),
                        transform=ax.transData)
    image.set_label("rice-classes")

    # No coastline stroke, on the same arithmetic as the urban maps: the
    # areal fills already occupy both narrow intervals the palette leaves,
    # and a stroke at 0.26 would sit 0.01 from the unassessed class.
    provinces = geo.read_layer(geo.PROVINCES)
    provinces.boundary.plot(ax=ax, color=style.role("boundary"),
                            linewidth=0.55, zorder=3)

    geo.apply_projection(ax, extent)
    xticks, yticks = geo.graticule(extent, step=2.0)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.xaxis.set_major_formatter(geo.degree_formatter("x"))
    ax.yaxis.set_major_formatter(geo.degree_formatter("y"))
    ax.tick_params(length=2.5)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.7)
        spine.set_edgecolor(style.role("boundary"))


# --------------------------------------------------------------------------
# the numbers
# --------------------------------------------------------------------------

def provincial_rice() -> dict:
    """Rice area by province and season, with the two denominators beside it."""
    out: dict = {}
    with RICE_TOTALS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            entry = out.setdefault(row["province"], {})
            entry[row["season"]] = float(row["rice_area_km2"])
            entry["assessed_km2"] = float(row["assessed_km2"])
            entry["polygon_km2"] = float(row["polygon_km2"])
            entry["assessed_over_polygon"] = float(row["assessed_over_polygon"])
    return out


def provincial_impervious(product: str = IMPERVIOUS_PRODUCT,
                          year: int = YEAR) -> dict:
    """Impervious area by province, from the urban figure's own table."""
    out: dict = {}
    with URBAN_TOTALS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row["source"] != product or int(row["year"]) != year:
                continue
            out[row["province"]] = float(row["urban_area_km2"])
    return out


def provincial_shares() -> dict:
    """Each quantity as a share of the province polygon, not of assessment.

    One denominator for all three bars, because bars in one panel with two
    denominators cannot be compared and a reader will compare them anyway.
    The cost falls on Anhui, whose rice is a lower bound because the product
    did not look at 13.9 percent of the province, and the panel marks it.
    """
    rice = provincial_rice()
    impervious = provincial_impervious()
    out = {}
    for province in PROVINCES:
        entry = rice[province]
        polygon = entry["polygon_km2"]
        out[province] = {
            "rice_single": entry["single"] / polygon,
            "rice_double": entry["double"] / polygon,
            "impervious": impervious[province] / polygon,
            "partial": entry["assessed_over_polygon"] < 0.99,
            "assessed_over_polygon": entry["assessed_over_polygon"],
        }
    return out


def _draw_shares(ax) -> None:
    """Three bars per province, as a share of the province's own area."""
    shares = provincial_shares()
    order = [("rice_single", "rice, single season"),
             ("rice_double", "rice, double season"),
             ("impervious", f"impervious, {IMPERVIOUS_PRODUCT}")]
    height = 0.26
    for index, province in enumerate(PROVINCES):
        base = index
        for offset, (key, _) in enumerate(order):
            value = 100.0 * shares[province][key]
            # The y axis is inverted, so a larger offset sits lower: this
            # is what puts the bars in the order the keys list them.
            ax.barh(base + (offset - 1) * height, value, height=height,
                    color=style.role(key), edgecolor=style.role("boundary"),
                    linewidth=0.4, zorder=3)
            ax.text(value + 0.8, base + (offset - 1) * height,
                    f"{value:.1f}", va="center", ha="left",
                    fontsize=style.TICK_SIZE - 1.0,
                    color=style.role("label_text"))
        if shares[province]["partial"]:
            ax.text(0.6, base - 2.05 * height,
                    f"rice is a lower bound: "
                    f"{shares[province]['assessed_over_polygon']:.0%} classified",
                    va="center", ha="left", fontsize=style.TICK_SIZE - 1.5,
                    fontstyle="italic", color=style.role("label_text"))

    ax.set_yticks(list(range(len(PROVINCES))))
    ax.set_yticklabels(PROVINCES, fontsize=style.TICK_SIZE)
    ax.set_ylim(-0.55, len(PROVINCES) - 0.25)
    # Listed order runs down the panel, so the panel reads in the order the
    # module declares rather than upside down.
    ax.invert_yaxis()
    # Shanghai is 50.9 percent impervious, which is the largest bar and the
    # one a reader will not have expected, so the axis is set to hold it
    # rather than clipping it and losing its label.
    ax.set_xlim(0, 58)
    ax.set_xticks([0, 20, 40])
    ax.set_xlabel("Percent of province area", fontsize=style.LABEL_SIZE)
    ax.tick_params(length=2.5)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for name in ("left", "bottom"):
        ax.spines[name].set_linewidth(0.7)
        ax.spines[name].set_edgecolor(style.role("boundary"))


# --------------------------------------------------------------------------
# keys and the notes that belong on the image
# --------------------------------------------------------------------------

NOTE = (
    "A 1/64° cell, about 1.4 km, is inked where at least {threshold:.0%} of it is "
    "rice, the threshold at which drawn area equals true area: {total:.2f} of "
    "{total_true:,.0f} km². The season colour says which season a cell's rice mostly "
    "is, not how much — the two cannot share a threshold, area-matching at 0.35 and "
    "0.17 — so the double colour covers {double_drawn:,.0f} km² of a true "
    "{double_true:,.0f}; panel (b) has the areas. Unclassified is the product's own "
    "footprint: it does not cover the other provinces, and in Anhui it stops at "
    "33.3462° N and 115.2682° E, a processing boundary and not an absence of rice.")


def _keys(fig, width_cm, height_cm) -> None:
    from matplotlib.patches import Patch

    handles = [
        Patch(facecolor=style.role("rice_single"),
              edgecolor=style.role("boundary"), linewidth=0.5,
              label="mostly single season"),
        Patch(facecolor=style.role("rice_double"),
              edgecolor=style.role("boundary"), linewidth=0.5,
              label="mostly double season"),
        Patch(facecolor=style.role("land_flat"),
              edgecolor=style.role("boundary"), linewidth=0.5,
              label="classified, below 35%"),
        Patch(facecolor=style.role("unassessed"),
              edgecolor=style.role("boundary"), linewidth=0.5,
              label="not classified"),
        Patch(facecolor=style.role("sea"), edgecolor=style.role("boundary"),
              linewidth=0.5, label="sea"),
    ]
    legend = fig.legend(
        handles=handles, loc="lower left", ncols=5,
        bbox_to_anchor=(LEFT_CM / width_cm, LEGEND_CM / height_cm),
        labelcolor=style.role("label_text"), handlelength=1.3, borderpad=0.0,
        borderaxespad=0.0, frameon=False, columnspacing=1.5,
        handletextpad=0.5)
    legend.set_in_layout(False)

    ratios = drawn_area_ratio()
    text = NOTE.format(threshold=THRESHOLD, total=ratios["total"],
                       total_true=ratios["total_true_km2"],
                       double_drawn=ratios["double_drawn_km2"],
                       double_true=ratios["double_true_km2"])
    fig.text(LEFT_CM / width_cm, NOTE_CM / height_cm, _wrap(text, 132),
             ha="left", va="bottom", fontsize=style.TICK_SIZE - 1.5,
             linespacing=1.4, color=style.role("label_text"))


def _wrap(text: str, width: int) -> str:
    import textwrap
    return "\n".join(textwrap.wrap(text, width))
