"""Venue standards for every figure, in one place.

The target venues are Copernicus journals -- Atmospheric Chemistry and Physics,
Atmospheric Measurement Techniques, Earth System Science Data -- and what is
encoded here is their author guidance rather than anybody's preference.

**Colour comes from Crameri's scientific colour maps**, which Copernicus
recommends by name. The argument for them is not aesthetic: a colour map that is
not perceptually uniform encodes gradients that are not in the data and hides
gradients that are, and a red-green scheme is unreadable to a substantial
minority of readers. See Crameri, Shephard and Heron (2020),
doi:10.1038/s41467-020-19160-7, in notes/references.md.

The 2023 thesis figures fail exactly this test. Their red-orange-yellow-green
ramp flattens to near-identical greys at the two ends of the scale, which is
why `ERRATA.md` records that a figure identification made from them had to be
reversed after checking the PDF.

**No gridlines, no shadows, no patterns, no decorative marks.** Ticks are
present and every axis label carries its units. Legends sit inside the figure
with coloured keys and black text, never coloured text, because coloured text
fails for the same readers the colour map is chosen to serve.

The palette degrades rather than breaking: if `cmcrameri` is not installed the
module falls back to matplotlib's own perceptually uniform maps, which are a
weaker but honest substitute, and :data:`PALETTE_SOURCE` records which is in
use so a figure can never silently be drawn in the wrong scheme.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt

#: Which colour source resolved. Read it rather than assuming.
PALETTE_SOURCE: str

try:  # pragma: no cover - exercised by whichever branch the environment has
    from cmcrameri import cm as _crameri
    PALETTE_SOURCE = "cmcrameri"
except ImportError:  # pragma: no cover
    _crameri = None
    PALETTE_SOURCE = "matplotlib-fallback"

#: Sequential map for an ordered quantity. batlow is Crameri's default
#: sequential map and is readable in greyscale and under colour vision
#: deficiency; viridis is the closest matplotlib equivalent.
SEQUENTIAL = "batlow"

#: Categorical keys, taken at fixed positions along the sequential map so that
#: they keep a defined greyscale order rather than being chosen by eye.
CATEGORY_POSITIONS = (0.08, 0.38, 0.62, 0.86)

CM = 1 / 2.54

# Copernicus states one figure dimension and only one: "The width should not be
# less than 8 cm." ACP, AMT and ESSD all say exactly that and none of them
# gives a single-column or full-width figure size, so there is no target width
# to conform to, only a floor. The two sizes below are this project's, chosen
# to sit on the typeset page rather than quoted from any guideline.
#
#: The floor, quoted from the guidelines. Nothing may be narrower.
MIN_WIDTH_CM = 8.0
#: One column of the two-column typeset page. Measured from the layout, not
#: specified by the venue.
COLUMN_WIDTH_CM = 8.3
#: Full text width. **The project default**, because these figures are panelled
#: and a panelled figure squeezed into one column loses its panels before it
#: loses anything else. A single-panel figure should pass COLUMN_WIDTH_CM
#: deliberately rather than inherit this.
FULL_WIDTH_CM = 17.0

#: Retained spellings of the two widths above.
SINGLE_COLUMN_CM = COLUMN_WIDTH_CM
DOUBLE_COLUMN_CM = FULL_WIDTH_CM

#: Raster output must be at least this. Vector output carries no dpi.
MIN_DPI = 300

FONT_SIZE = 8.0
LABEL_SIZE = 8.0
TICK_SIZE = 7.0
PANEL_LABEL_SIZE = 9.0


def sequential(name: str = SEQUENTIAL):
    """The named scientific colour map, or the closest honest fallback."""
    if _crameri is not None:
        try:
            return getattr(_crameri, name)
        except AttributeError:
            pass
    return plt.get_cmap({"batlow": "viridis", "lajolla": "magma",
                         "davos": "cividis"}.get(name, "viridis"))


def categories(n: int, name: str = SEQUENTIAL) -> list:
    """``n`` distinguishable colours sampled along the sequential map.

    Sampled at fixed positions rather than chosen individually, so the set has
    a defined order in lightness and survives conversion to greyscale.
    """
    cmap = sequential(name)
    if n <= len(CATEGORY_POSITIONS):
        return [cmap(p) for p in CATEGORY_POSITIONS[:n]]
    return [cmap(0.08 + 0.78 * i / max(n - 1, 1)) for i in range(n)]


def apply() -> None:
    """Set the rcParams every figure in this repository is drawn under.

    Called by :func:`figure`, so a figure function does not have to remember.
    """
    mpl.rcParams.update({
        "figure.dpi": MIN_DPI,
        "savefig.dpi": MIN_DPI,
        "font.family": "sans-serif",
        "font.sans-serif": ["DejaVu Sans", "Helvetica", "Arial"],
        "font.size": FONT_SIZE,
        "axes.labelsize": LABEL_SIZE,
        "axes.titlesize": LABEL_SIZE,
        "xtick.labelsize": TICK_SIZE,
        "ytick.labelsize": TICK_SIZE,
        "legend.fontsize": TICK_SIZE,
        "axes.grid": False,              # the standard forbids gridlines
        "axes.spines.top": False,
        "axes.spines.right": False,
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.major.size": 3.0,
        "ytick.major.size": 3.0,
        "legend.frameon": False,
        "legend.handletextpad": 0.5,
        # Fonts must be embedded as real glyphs, not drawn as paths, so that a
        # typesetter can restyle them and a reader can select the text.
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "svg.fonttype": "none",
    })


def figure(width_cm: float = FULL_WIDTH_CM, height_cm: float = 8.0):
    """A figure at a stated physical size, with the conventions applied."""
    if width_cm < MIN_WIDTH_CM:
        raise ValueError(
            f"width {width_cm} cm is below the {MIN_WIDTH_CM} cm minimum the "
            f"venue standard requires")
    apply()
    return plt.figure(figsize=(width_cm * CM, height_cm * CM))


def panel_label(ax, letter: str, dx: float = -0.09, dy: float = 1.04) -> None:
    """Label a panel (a), (b), (c) in the convention the standard requires."""
    ax.text(dx, dy, f"({letter})", transform=ax.transAxes,
            fontsize=PANEL_LABEL_SIZE, fontweight="bold",
            va="bottom", ha="left")
