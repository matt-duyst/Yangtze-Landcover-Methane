"""Urban extent in 2000, 2010 and 2018, from two products that disagree.

The reproduction's results are almost entirely null: land cover does not
explain the methane field, on any field, at either cross-validation scheme,
with either impervious product or either rice product. Urban expansion is the
one positive quantitative land-cover finding it has, it regenerates from
committed code, and until now there was no figure for it.

What the figure has to carry
----------------------------

Two things at once, and they want different treatments.

**Growth**, which is spatial: the delta's urban land is not a uniform swelling
but a set of cores along the Yangtze and the coast that join up. Two maps show
that in one look each, drawn as three nested classes by the year a pixel first
became impervious, which encodes all three dates in one panel instead of three
nearly identical ones.

**Disagreement**, which is quantitative and is the sharper finding. GAIA and
GISA differ by about 20 percent in 2018, which is known. They differ in the
*opposite direction* in 2000 -- GISA is the larger there -- so they disagree
about the growth factor far more than about the extent. Panel (c) carries that,
because a map cannot.

The maps show where, the numbers show how much
----------------------------------------------

A 30 m product cannot be drawn over 7.75 degrees at its own resolution, so the
maps are drawn from an aggregate at 1/128 degree and a cell is inked where at
least :data:`THRESHOLD` of it was impervious by that date. That threshold is
stated rather than hidden because it does not preserve area, and it does not
fail evenly: urban land in 2000 is more dispersed than in 2018, so at a quarter
of a cell the drawn 2000 class is 0.73 of its true area while the drawn 2018
class is 1.31 of its true area, which flatters growth by about four fifths.

**So area is read from panel (c) and never from the maps**, and the caption
says so. `scripts/make_urban_change_figure.py` prints the drawn-to-true ratio
for all six product-years on every build, so the distortion is on the record
rather than in a memory.

A threshold-free alternative was tried and rejected: shading each cell by its
fraction leaves the region nearly blank, because the median land cell in this
box is 2 percent impervious and only 14.8 percent of land cells reach a
quarter.

Why there is no rice panel
--------------------------

There is no defensible rice time series in this data and the caption says so
rather than leaving a reader to wonder. Four reasons, all recorded in
`notes/decisions.md`:

* NESDC covers 2017 to 2025 and the comparison years are 2000 and 2018. It
  reaches one of them.
* Shanghai's totals are pinned across 2019 to 2025 and Jiangsu's across 2020 to
  2025 and again over 2017 to 2018: the whole-raster count is held fixed while
  the mask relocates, 5,651,475 pixels gaining the label and 5,651,551 losing
  it between 2023 and 2024 alone. Half the study region cannot contribute a
  year-on-year value.
* Anhui's rasters classify only the part of the province south of 33.3462 N and
  east of 115.2682 E, in every year, which is 86.1 percent of it.
* GloRice reaches 2000 but allocates official statistics to grid cells through
  a model rather than observing extent, and correlates with impervious fraction
  at Spearman +0.5613, so a GloRice rice trend partly measures development.

What is left is two provinces over a window that misses both comparison years,
from a product whose other two provinces are pinned. That is not a time series.

And why there is no methane equivalent
--------------------------------------

A reader arriving at a land-cover change figure will expect a methane change
figure beside it, and there cannot be one. TROPOMI's footprint is 7 by 7 km at
nadir, the analysis grid is 0.25 degrees because coverage forced it there, and
the 2018 composite already leaves 97 of 1,023 cells with no sounding at all.
There is one year of usable methane, not three.
"""

from __future__ import annotations

import csv

import numpy as np

from . import geo, style

PROCESSED = geo.REFERENCE_DIR.parents[0] / "processed"
EXTENT_RASTERS = {
    "GAIA": PROCESSED / "urban_extent_gaia.tif",
    "GISA": PROCESSED / "urban_extent_gisa.tif",
}
TOTALS = PROCESSED / "urban_extent_totals.csv"
#: The thesis's own provincial figures travel in this file's last column.
THESIS_TABLE = PROCESSED / "urban_area_by_province.csv"

#: The years the maps draw. 2019 rather than 2018 because it is the last year
#: both products cover: GISA's values stop at 37, which is 2019, so a map going
#: further would drop GISA and lose the disagreement this figure is for.
MAP_YEARS = (2000, 2010, 2019)

#: The years the totals panel draws. 2018 rather than 2019 because that is the
#: year the 2023 thesis reported, and comparing against it is half of what the
#: panel is for.
TOTALS_YEARS = (2000, 2010, 2018)

#: Every year the committed aggregate carries.
YEARS = (2000, 2010, 2018, 2019)

#: A display cell is inked for a year when at least this much of it had become
#: impervious by then. A quarter, and see the module docstring for what it
#: costs and why the alternative is worse.
THRESHOLD = 0.25

#: How many stored cells go into one drawn cell, per axis.
#:
#: The committed aggregate is 1/128 degree, which is 992 cells across the box.
#: A 4.95 cm panel at 300 dpi is 585 pixels, so drawing it cell for cell asks
#: the page for 0.59 pixels per cell and gets aliasing: isolated inked cells
#: survive or vanish according to where they fall, and the map reads as
#: stipple rather than as cities. The first draft did exactly that.
#:
#: Two stored cells per axis gives 1/64 degree, 496 across the box, 1.18 drawn
#: pixels each. The averaging happens on the **fractions**, before the
#: threshold, so a drawn cell is inked when a quarter of its own 1.4 km square
#: was impervious -- which is the same statement at a coarser scale, not a
#: different one.
DISPLAY_FACTOR = 2

#: Which role draws which class. The keys are the year a class runs *to*.
CLASS_ROLES = {2000: "urban_2000", 2010: "urban_2010", 2019: "urban_2019"}
CLASS_LABELS = {2000: "impervious by 2000", 2010: "first 2001–2010",
                2019: "first 2011–2019"}

#: Panel (c)'s three lines, as (source, computation) and in legend order.
#:
#: **Not three sources.** GAIA and GISA are data; the 2023 thesis is a prior
#: study whose impervious figures came from GAIA, so listing "thesis" beside
#: the two products would imply three independent measurements where there are
#: two, one of them measured twice. `style.source_computation_styles` gives the
#: source the colour and the computation the dash, and the comparison that
#: layout makes visible is the one that matters: the same product recomputed
#: holds 2018 to 0.8 percent and moves 2000 by a factor of two.
SERIES_PAIRS = (("GAIA", "as reported 2023"),
                ("GAIA", "reproduced 2026"),
                ("GISA", "reproduced 2026"))

#: Which computation takes the solid line. The current one.
COMPUTATION_ORDER = ("reproduced 2026", "as reported 2023")

# Layout in centimetres. Two maps and a numbers panel across the full width.
FIG_WIDTH_CM = style.FULL_WIDTH_CM
LEFT_CM = 1.15
MAP_CM = 4.95
MAP_GAP_CM = 0.35
PANEL_GAP_CM = 1.30
NUMBERS_CM = 3.55
RIGHT_CM = 0.75
NOTE_CM = 0.12
LEGEND_CM = 1.75
TICKS_CM = 0.50
TITLE_CM = 0.40
BOTTOM_CM = LEGEND_CM + 0.95 + TICKS_CM
TOP_CM = 0.18

WIDTH_CM = FIG_WIDTH_CM


def urban_change_figure(width_cm: float = WIDTH_CM,
                        height_cm: float | None = None):
    """Build and return the urban change figure. Writes nothing."""
    spec = geo.study_spec()
    extent = geo.lattice_extent(spec)
    map_h = MAP_CM * geo.display_ratio(extent)
    if height_cm is None:
        height_cm = BOTTOM_CM + map_h + TITLE_CM + TOP_CM
    fig = style.figure(width_cm=width_cm, height_cm=height_cm)

    def axes(x_cm, y_cm, w_cm, h_cm):
        return fig.add_axes((x_cm / width_cm, y_cm / height_cm,
                             w_cm / width_cm, h_cm / height_cm))

    land = geo.read_layer(geo.LAND)
    provinces = geo.read_layer(geo.PROVINCES)

    ax_gaia = axes(LEFT_CM, BOTTOM_CM, MAP_CM, map_h)
    ax_gisa = axes(LEFT_CM + MAP_CM + MAP_GAP_CM, BOTTOM_CM, MAP_CM, map_h)
    numbers_x = LEFT_CM + 2 * MAP_CM + MAP_GAP_CM + PANEL_GAP_CM
    ax_numbers = axes(numbers_x, BOTTOM_CM, NUMBERS_CM, map_h)

    _draw_extent_map(ax_gaia, "GAIA", extent, land, provinces)
    _draw_extent_map(ax_gisa, "GISA", extent, land, provinces)
    # The second map's latitude labels would land on the first map; it shares
    # the frame and the graticule with it, so it needs none of its own.
    ax_gisa.set_yticklabels([])
    _draw_numbers(ax_numbers)

    titles = {"a": "GAIA, first impervious", "b": "GISA, first impervious",
              "c": "four-province total"}
    for ax, letter in ((ax_gaia, "a"), (ax_gisa, "b"), (ax_numbers, "c")):
        box = ax.get_position()
        fig.text(box.x0, box.y1 + 0.09 / height_cm,
                 f"({letter}) {titles[letter]}", ha="left", va="bottom",
                 fontsize=style.LABEL_SIZE, fontweight="bold",
                 color=style.role("label_text"))
    _keys(fig, width_cm, height_cm)
    return fig


# --------------------------------------------------------------------------
# the maps
# --------------------------------------------------------------------------

def stored_years(product: str) -> tuple[int, ...]:
    """The years the committed aggregate carries, read from its own tags.

    Read rather than assumed, so that adding a year to the artefact cannot
    silently renumber the bands a figure draws. That is not hypothetical: the
    maps moved from 2018 to 2019 while the totals panel kept 2018, and a
    positional read would have quietly drawn one as the other.
    """
    import rasterio
    with rasterio.open(EXTENT_RASTERS[product]) as src:
        tags = src.tags()
    return tuple(int(year) for year in tags["years"].split(","))


def display_fractions(product: str, factor: int = DISPLAY_FACTOR,
                      years=None):
    """The committed fractions, averaged to the resolution the page resolves.

    ``years`` selects bands by year rather than by position; it defaults to
    the map's years.
    """
    wanted = MAP_YEARS if years is None else tuple(years)
    stored = stored_years(product)
    bands, extent = geo.read_raster(EXTENT_RASTERS[product])
    fractions = np.moveaxis(np.asarray(bands), -1, 0) / 100.0
    fractions = np.stack([fractions[stored.index(year)] for year in wanted])
    if factor > 1:
        n, rows, cols = fractions.shape
        fractions = fractions[:, :rows // factor * factor,
                              :cols // factor * factor]
        fractions = fractions.reshape(
            n, fractions.shape[1] // factor, factor,
            fractions.shape[2] // factor, factor).mean(axis=(2, 4))
    return fractions, extent


def extent_classes(product: str, threshold: float = THRESHOLD,
                   factor: int = DISPLAY_FACTOR):
    """Year-class per drawn cell, and the extent.

    Class 0 is never inked, 1 is impervious by 2000, 2 first impervious in
    2001 to 2010, 3 in 2011 to 2018. The classes nest because the fractions
    are monotone in year, so a cell is given the **earliest** class it
    qualifies for and no cell can belong to two.
    """
    fractions, extent = display_fractions(product, factor)
    classes = np.zeros(fractions.shape[1:], dtype="uint8")
    for index in reversed(range(len(MAP_YEARS))):
        classes[fractions[index] >= threshold] = index + 1
    return classes, extent


def drawn_area_ratio(product: str, threshold: float = THRESHOLD) -> dict:
    """Inked area over true area, per year, inside the four provinces.

    The number the caption rests on when it tells a reader not to measure the
    maps. Computed here rather than remembered, and printed on every build.
    """
    import rasterio
    from rasterio.features import geometry_mask
    from rasterio.transform import from_bounds

    provinces = geo.read_layer(geo.PROVINCES)
    fractions, extent = display_fractions(product)
    shape = fractions.shape[1:]
    transform = from_bounds(extent[0], extent[2], extent[1], extent[3],
                            shape[1], shape[0])
    inside = ~geometry_mask(provinces.geometry, out_shape=shape,
                            transform=transform, invert=False)
    step = 1.0 / (128 / DISPLAY_FACTOR)
    radius = 6371.0072
    latitudes = np.array([transform.f + (row + 0.5) * transform.e
                          for row in range(shape[0])])
    cell_km2 = ((np.radians(step) * radius)
                * (np.radians(step) * radius
                   * np.cos(np.radians(latitudes))))
    truth = provincial_totals()
    out = {}
    for index, year in enumerate(MAP_YEARS):
        drawn = float(((fractions[index] >= threshold)
                       * cell_km2[:, None] * inside).sum())
        out[year] = drawn / sum(truth[product][year].values())
    return out


def _draw_extent_map(ax, product: str, extent, land, provinces) -> None:
    classes, raster_extent = extent_classes(product)
    ax.set_facecolor(style.role("sea"))

    image = ax.imshow(np.zeros(classes.shape), extent=raster_extent,
                      origin="upper", cmap=_flat_cmap(), vmin=0, vmax=1,
                      interpolation="nearest", aspect="auto", zorder=1)
    image.set_clip_path(geo.polygon_path(land.geometry),
                        transform=ax.transData)
    image.set_label(f"land-{product}")

    ax.imshow(_class_rgba(classes), extent=raster_extent, origin="upper",
              interpolation="nearest", aspect="auto", zorder=2,
              label=f"extent-{product}")

    # No coastline stroke. Three urban classes have to clear the boundary at
    # 0.078, the sea at 0.42 and the flat land at 0.925 by 0.15 each, which
    # leaves exactly room for three; adding a coastline at 0.26 to the set
    # makes it infeasible. The land-to-sea tone step is 0.505 without one.
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


def _flat_cmap():
    """A one-colour map, so the land layer is an image and can be clipped."""
    from matplotlib.colors import ListedColormap
    return ListedColormap([style.role("land_flat")])


def _class_rgba(classes):
    """The three year classes as RGBA, transparent where nothing is inked."""
    import matplotlib.colors as mcolors

    rgba = np.zeros(classes.shape + (4,), dtype="float64")
    for index, year in enumerate(MAP_YEARS, start=1):
        mask = classes == index
        rgba[mask, :3] = mcolors.to_rgb(style.role(CLASS_ROLES[year]))
        rgba[mask, 3] = 1.0
    return rgba


# --------------------------------------------------------------------------
# the numbers
# --------------------------------------------------------------------------

def provincial_totals() -> dict:
    """Committed provincial areas, by product, year and province.

    From `urban_extent_totals.csv`, which is regenerable and whose sixteen
    overlapping rows reproduce the two older tables to 1.3e-05. It does not
    replace `urban_area_by_province_gisa.csv`, which is registered
    `unregenerable` and carries 2018 alone.
    """
    out: dict = {}
    with TOTALS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            product = row["source"]
            year = int(row["year"])
            out.setdefault(product, {}).setdefault(year, {})[
                row["province"]] = float(row["urban_area_km2"])
    return out


def thesis_totals() -> dict:
    """The 2023 thesis's own provincial figures, summed, by year."""
    out: dict = {}
    with THESIS_TABLE.open(newline="") as handle:
        for row in csv.DictReader(handle):
            value = row.get("thesis_urban_km2")
            if not value or row["boundary"] != "gadm":
                continue
            out[int(row["year"])] = out.get(int(row["year"]), 0.0) + float(value)
    return out


def series() -> dict:
    """Total urban area over the four provinces, by (source, computation).

    Keyed by the pair rather than by a name, because the pair is the thing:
    "GAIA" alone does not say whether the number is the 2023 report or the
    2026 recomputation, and those differ by a factor of two in 2000.
    """
    totals = provincial_totals()
    out = {("GAIA", "as reported 2023"): thesis_totals()}
    for product in ("GAIA", "GISA"):
        out[(product, "reproduced 2026")] = {
            year: sum(totals[product][year].values()) for year in YEARS}
    return out


def growth_factors() -> dict:
    """2018 over 2000, per (source, computation). The figure's sharpest number."""
    values = series()
    return {pair: values[pair][2018] / values[pair][2000] for pair in values}


def _draw_numbers(ax) -> None:
    """Three sources, three years, and the factor each one implies.

    A line rather than bars, because what a reader has to see is that the
    three converge at 2018 and fan out at 2000: the sources agree about the
    extent and disagree about the history, which is the opposite of what a
    reader expects and is the whole point of the panel.
    """
    values = series()
    factors = growth_factors()
    styles = style.source_computation_styles(
        SERIES_PAIRS, computation_order=COMPUTATION_ORDER)
    for pair, line in zip(SERIES_PAIRS, styles):
        source, computation = pair
        points = [values[pair][year] / 1000.0 for year in TOTALS_YEARS]
        # The growth factor goes in the key rather than beside the 2018
        # point. Three annotations at the right-hand end of three converging
        # lines land on each other, which the first draft demonstrated.
        ax.plot(TOTALS_YEARS, points, linewidth=1.3, marker="o",
                markersize=3.0, markeredgewidth=0, zorder=3,
                markerfacecolor=line["color"],
                label=f"{source}, {computation}  ×{factors[pair]:.1f}",
                **line)

    ax.set_xlim(1997, 2021)
    ax.set_ylim(0, 55)
    ax.set_xticks(list(TOTALS_YEARS))
    ax.set_xticklabels([str(year) for year in TOTALS_YEARS],
                       fontsize=style.TICK_SIZE - 1)
    ax.set_yticks([0, 10, 20, 30, 40, 50])
    ax.tick_params(length=2.5)
    ax.set_ylabel("Impervious area (10$^3$ km$^2$)",
                  fontsize=style.LABEL_SIZE)
    ax.legend(loc="upper left", handlelength=1.1, borderpad=0.25,
              labelspacing=0.35, handletextpad=0.5, borderaxespad=0.2,
              fontsize=style.TICK_SIZE - 0.5,
              labelcolor=style.role("label_text"))
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for name in ("left", "bottom"):
        ax.spines[name].set_linewidth(0.7)
        ax.spines[name].set_edgecolor(style.role("boundary"))


# --------------------------------------------------------------------------
# keys and the notes that belong on the image
# --------------------------------------------------------------------------

NOTE = (
    "Maps show where, not how much: a 1/64° cell, about 1.4 km, is inked where at "
    "least {threshold:.0%} of it had become impervious, which draws the 2000 class at "
    "{r2000:.2f} of its true area and the 2019 class at {r2019:.2f}, so area is read "
    "from (c). Maps run to 2019, the last year both products cover; 2019 is the first "
    "year past GAIA's original 1985–2018 release and sits inside a stretch whose "
    "year-on-year growth drops from 7.1–10.5 % to 1.9–2.6 %, so it inherits that "
    "doubt. (c) keeps 2018, the year the thesis reported. Rice is drawn in its own "
    "figure; there is no methane equivalent, TROPOMI's footprint being 7 by 7 km with "
    "one usable year.")


def _keys(fig, width_cm, height_cm) -> None:
    from matplotlib.patches import Patch

    handles = [Patch(facecolor=style.role(CLASS_ROLES[year]),
                     edgecolor=style.role("boundary"), linewidth=0.5,
                     label=CLASS_LABELS[year])
               for year in MAP_YEARS]
    handles.append(Patch(facecolor=style.role("land_flat"),
                         edgecolor=style.role("boundary"), linewidth=0.5,
                         label="land below 25%"))
    handles.append(Patch(facecolor=style.role("sea"),
                         edgecolor=style.role("boundary"), linewidth=0.5,
                         label="sea"))
    legend = fig.legend(
        handles=handles, loc="lower left", ncols=5,
        bbox_to_anchor=(LEFT_CM / width_cm, LEGEND_CM / height_cm),
        labelcolor=style.role("label_text"), handlelength=1.3, borderpad=0.0,
        borderaxespad=0.0, frameon=False, columnspacing=1.6,
        handletextpad=0.5)
    legend.set_in_layout(False)

    ratios = drawn_area_ratio("GAIA")
    text = NOTE.format(threshold=THRESHOLD, r2000=ratios[2000],
                       r2019=ratios[2019])
    fig.text(LEFT_CM / width_cm, NOTE_CM / height_cm, _wrap(text, 132),
             ha="left", va="bottom", fontsize=style.TICK_SIZE - 1.5,
             linespacing=1.4, color=style.role("label_text"))


def _wrap(text: str, width: int) -> str:
    import textwrap
    return "\n".join(textwrap.wrap(text, width))
