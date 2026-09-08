"""Venue standards for every figure, in one place, and the palette as roles.

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

Colour as roles, not as colours
-------------------------------

Every colour a figure may draw is a **role** in :data:`ROLES`: a name for a job
on the page, its colour, what kind of mark it is, and the other roles it has to
stay distinguishable from. A figure asks for ``style.role("sea")`` and gets the
one sea colour; it cannot introduce a colour of its own without adding a role
here, and `tests/test_figures_palette.py` enforces that by scanning the figure
modules for colour literals.

The reason for the structure, rather than a flat list of constants, is the
adjacency field. Fourteen roles cannot all sit 0.15 apart in luminance on a
zero-to-one scale; only seven can. But they do not all need to: a place marker
and a neighbouring province's boundary never have to be told apart by tone,
because one is a dot and the other is a line, while a coastline and the sea it
separates absolutely do. So each role declares what it is drawn **against**,
and :func:`greyscale_report` and :func:`cvd_report` check exactly those pairs.
A flat all-pairs check over fourteen roles is not a stricter test, it is an
impossible one, and an impossible test gets deleted.

Areal roles that carry a *range* rather than a value -- the relief -- are
handled as a band: see :func:`relief_band`. Sequential ramps are not roles at
all and are checked separately, for monotonicity and span, by
:func:`~src.figures.fields.ramp_luminances`; a minimum pairwise gap says
nothing about a ramp, whose adjacent samples are arbitrarily close by
construction.

The palette degrades rather than breaking: if `cmcrameri` is not installed the
module falls back to matplotlib's own perceptually uniform maps, which are a
weaker but honest substitute, and :data:`PALETTE_SOURCE` records which is in
use so a figure can never silently be drawn in the wrong scheme.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np

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

#: The greyscale member of Crameri's set, used for shaded relief. A hillshade
#: has to be grey rather than hypsometric wherever data is drawn over it, and
#: taking the grey from the same family keeps one perceptual standard across
#: the figure rather than mixing a scientific ramp with matplotlib's `gray`.
GREYSCALE = "grayC"

#: Crameri's **categorical** variant of the sequential map. Its entries are
#: ordered for maximum perceptual distinctness rather than by lightness, which
#: is what :func:`series` reorders. See :data:`SERIES`.
CATEGORICAL = "batlowS"

#: The luminance separation anything meaningful must hold, in every place this
#: module checks. Set once here so the convention has one definition.
MIN_LUMINANCE_GAP = 0.15

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


# --------------------------------------------------------------------------
# colour arithmetic
# --------------------------------------------------------------------------

def _mix(colour, white: float):
    """Lighten ``colour`` toward white by a fraction, keeping its hue."""
    return tuple(c * (1.0 - white) + white for c in colour[:3])


def _luminance(colour) -> float:
    """Relative luminance, the quantity a greyscale print preserves."""
    import matplotlib.colors as mcolors
    r, g, b = mcolors.to_rgb(colour)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def sequential(name: str = SEQUENTIAL):
    """The named scientific colour map, or the closest honest fallback."""
    if _crameri is not None:
        try:
            return getattr(_crameri, name)
        except AttributeError:
            pass
    return plt.get_cmap({"batlow": "viridis", "lajolla": "magma",
                         "davos": "cividis", "lipari": "plasma",
                         "grayC": "gray", "batlowS": "viridis"}.get(name,
                                                                    "viridis"))


def _hex(colour) -> str:
    import matplotlib.colors as mcolors
    return mcolors.to_hex(colour)


# --------------------------------------------------------------------------
# the ordered categorical series
# --------------------------------------------------------------------------

#: Ceiling on a series colour's luminance. A line at 0.85 on a white page is
#: not ink, it is a suggestion, and Crameri's categorical set contains two such
#: entries in its first eight because it is built for filled areas as well as
#: for lines. Entries above this are skipped rather than the set redesigned.
SERIES_LUMINANCE_CEILING = 0.78


def _build_series(n: int = 4) -> tuple[str, ...]:
    """The first ``n`` usable entries of Crameri's categorical map, by lightness.

    Two steps, and both matter. `batlowS` orders the same colours batlow holds
    so that **any prefix** is a maximally distinct set, which is the property
    that lets a three-series figure and a four-series figure share the first
    three colours instead of being recoloured against each other. Entries too
    light to work as line ink on white are skipped, which keeps the prefix
    property while dropping colours the page cannot hold.

    Then the prefix is sorted by luminance, because a *series* is ordered: a
    reader in black and white must be able to say which key is which, and
    `batlowS` order is chosen for hue distinctness, not for tone.
    """
    cmap = sequential(CATEGORICAL)
    picked: list[str] = []
    for i in range(cmap.N):
        colour = _hex(cmap(i / (cmap.N - 1)))
        if colour in picked or _luminance(colour) > SERIES_LUMINANCE_CEILING:
            continue
        picked.append(colour)
        if len(picked) == n:
            break
    return tuple(sorted(picked, key=_luminance))


#: Ordered categorical keys for line and bar figures. Four, and four is the
#: measured ceiling rather than a round number: Crameri's categorical set has
#: no five-colour subset below the line-ink ceiling that separates by 0.15 in
#: luminance, because 0.15 steps fit five slots into [0.10, 0.78] only if the
#: set happens to hold colours at those tones and this one does not. A figure
#: needing more than four series must separate them by something that is not
#: colour. See `notes/decisions.md`.
SERIES: tuple[str, ...] = _build_series(4)

#: Retained for the fixed-position sampling the earlier palette used. Kept only
#: so a reader of the history can find it; nothing draws from it.
CATEGORY_POSITIONS = (0.08, 0.38, 0.62, 0.86)


def series(n: int) -> list[str]:
    """``n`` ordered categorical keys. Refuses more than the set can hold."""
    if n > len(SERIES):
        raise ValueError(
            f"the categorical series holds {len(SERIES)} colours that separate "
            f"by {MIN_LUMINANCE_GAP} in luminance and {n} were asked for; a "
            f"figure needing more must distinguish them by something other "
            f"than colour")
    return list(SERIES[:n])


def categories(n: int, name: str = SEQUENTIAL) -> list:
    """Retained spelling of :func:`series`, kept for existing callers."""
    del name
    return series(n)


# --------------------------------------------------------------------------
# roles
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Role:
    """One job on the page, and what it has to stay distinguishable from.

    ``against`` is the whole point. It names the roles this one is actually
    drawn over or beside, so the greyscale and colour-vision checks test the
    pairs a reader has to separate rather than every pair that exists.
    """

    name: str
    colour: str
    kind: str          # areal | line | mark | text
    why: str
    against: frozenset = field(default_factory=frozenset)

    @property
    def luminance(self) -> float:
        return _luminance(self.colour)


def _at_luminance(colour, target: float):
    """``colour`` scaled to a stated relative luminance, hue held.

    Used for the ends of the relief ramp, whose tones are set by what the line
    palette needs to clear rather than by where the grey map happens to run.
    """
    import matplotlib.colors as mcolors
    rgb = np.array(mcolors.to_rgb(colour))
    current = _luminance(rgb)
    if current <= 1e-6:
        return (target, target, target)
    return tuple(np.clip(rgb * (target / current), 0.0, 1.0))


def _role(name, colour, kind, why, against=()):
    return Role(name=name, colour=_hex(colour), kind=kind, why=why,
                against=frozenset(against))


_BATLOW = sequential()
_GREY = sequential(GREYSCALE)

# The two ends of the relief ramp. The band is deliberately narrow and light:
# a hillshade drawn at full contrast under discrete overlays is a competing
# figure rather than a ground, and every line the map draws has to sit clear
# of the *darkest* tone the relief reaches. Widening the band by 0.1 at the
# dark end costs 0.1 of the range every line colour has to fit into.
RELIEF_LIGHT_LUMINANCE = 0.97
RELIEF_DARK_LUMINANCE = 0.74

_ROLE_LIST = (
    # -- ground tones. `land_outside` and `province_fill` are **tints**, not
    # fills: the relief is drawn under both and then veiled or tinted toward
    # them, so what a reader actually sees is a luminance *band*, not one of
    # these values. They are therefore checked by `relief_report()` against
    # the bands they produce, and appear in the pairwise graph only against
    # each other and the sea, which are the tones they meet at the frame.
    _role("sea", _at_luminance(_BATLOW(0.28), 0.50), "areal",
          "Flat water. Its tone is not chosen but solved for: it has to clear "
          "the darkest tone the veiled out-of-region relief reaches, because a "
          "coastline alone cannot carry the land/water distinction in a print "
          "with no colour, and it has to leave the lattice somewhere to live.",
          ("land_outside", "province_fill", "relief_dark", "boundary",
           "coastline", "lattice")),
    _role("land_outside", _at_luminance(_BATLOW(0.80), 0.66), "tint",
          "Land beyond the four provinces. Relief is drawn over it and then "
          "veiled toward this tone, so it reads as land with terrain rather "
          "than as absence, while staying recessive. The earlier palette put "
          "it at 0.96, which is why the first version of this map read as a "
          "study region floating in white.",
          ("sea", "province_fill")),
    _role("province_fill", _mix(_BATLOW(0.62), 0.72), "tint",
          "The four study provinces. A tint over the relief, not a fill: four "
          "distinguishable fills over shaded relief is six areal classes and "
          "they cannot all separate. The boundaries and the names carry the "
          "distinction between provinces, and the tone difference a reader "
          "sees between inside and outside is the veil on the outside, not "
          "this.",
          ("sea", "land_outside")),

    # -- the relief band's two ends. Every line drawn over land clears the
    # darker of these, which is the binding constraint on the line palette.
    _role("relief_dark", _at_luminance(_GREY(0.5), RELIEF_DARK_LUMINANCE),
          "areal",
          "The dark end of the shaded relief: shaded slopes in the mountains "
          "of southern Zhejiang and western Anhui, which is where the "
          "composite figure's largest hole sits.",
          ("sea", "boundary", "boundary_minor", "coastline", "lattice",
           "place_marker", "label_text")),
    _role("relief_light", (RELIEF_LIGHT_LUMINANCE,) * 3, "areal",
          "The light end of the shaded relief, and the flat delta ground that "
          "most of the study area is.",
          ("boundary", "boundary_minor", "coastline", "lattice",
           "place_marker", "label_text")),

    # -- the lattice as data, in the composite and its successors. There is no
    # basemap under the lattice -- measured at zero visible pixels -- so
    # absence is adjacent to the ramp and to its own outline and to nothing
    # else. The ramp is checked as a ramp, not as a role.
    _role("absent_fill", "#f7f7f7", "areal",
          "A lattice cell with no observation. Near-white, which is the "
          "literature's convention for missing, and outside the truncated "
          "value ramp by 0.19 in luminance.",
          ("absent_edge", "boundary", "coastline")),
    _role("absent_edge", "#808080", "line",
          "The outline that makes one absent cell a deliberate mark rather "
          "than a light patch in a light part of the ramp. A fill alone loses "
          "the eight singletons.",
          ("absent_fill",)),

    # -- lines
    _role("boundary", "#1f1f1f", "line",
          "A study province boundary, and every panel frame. The heaviest "
          "line on the map, because it is what the province fill no longer "
          "does.",
          ("sea", "relief_dark", "relief_light", "absent_fill",
           "boundary_minor", "coastline")),
    _role("boundary_minor", "#8a8a8a", "line",
          "A neighbouring province's boundary. Present so the study region "
          "sits in a country rather than in white, and lighter than the study "
          "boundary so a reader can see which four provinces are the subject "
          "without reading the names.",
          ("relief_dark", "relief_light", "boundary")),
    _role("coastline", "#3f4a52", "line",
          "Where land meets water in the main panel. It separates from both, "
          "which is a tighter constraint than any other line on the map has.",
          ("sea", "relief_dark", "relief_light", "absent_fill", "boundary")),
    _role("lattice", _at_luminance("#5c5c5c", 0.34), "line",
          "An analysis cell edge, drawn only in the detail box now. It sits "
          "over sea and over relief, so it carries the coastline's two-sided "
          "constraint -- and that is why the detail box does not stroke a "
          "coastline. Measured: with the relief band's floor at 0.74, no "
          "assignment puts sea, a coastline and a lattice line all 0.15 apart "
          "and all 0.15 below the band. The tone step from sea to lit relief "
          "is 0.47 at the size the detail box is drawn, so the stroke was the "
          "thing to drop.",
          ("sea", "relief_dark", "relief_light")),

    # -- non-map roles, for the line and bar figures
    _role("absent_span", _at_luminance("#e0e0e0", 0.84), "areal",
          "A shaded span over an interval that was never sampled, in a panel "
          "that is not a map. A zero bar and a missing bar look identical and "
          "mean opposite things, so absence is drawn as a span and labelled "
          "in place. The label sits inside it rather than in a legend, "
          "because a grey key for a grey span sits on the span it describes "
          "and is invisible; the first draft demonstrated that.",
          ("label_text", "page")),
    _role("page", "#ffffff", "areal",
          "The ground the figure is drawn on, and therefore also the fill of "
          "a legend box and the face of an open marker. Named as a role "
          "because a figure that writes `white` has made a colour decision "
          "and should have to say which one.",
          ("absent_span", "label_text")),

    # -- marks and text
    _role("place_marker", "#1f1f1f", "mark",
          "A populated place. Same ink as the study boundary: a dot and a "
          "line are not confusable by shape, so they need no tonal separation "
          "from each other and both want to be the darkest thing on the page.",
          ("relief_dark", "relief_light")),
    _role("label_text", "#000000", "text",
          "Every name on a map. Black, never coloured, which is the venue's "
          "rule and serves the same readers the colour map is chosen for.",
          ("relief_dark", "relief_light", "label_halo", "absent_span",
           "page")),
    _role("label_halo", "#ffffff", "text",
          "A white outline behind label text. Not decoration: without it a "
          "name crossing a boundary line is unreadable, and the alternative "
          "is moving the name off the thing it names.",
          ("label_text",)),
)

#: Every colour any figure in this repository may draw, by role.
ROLES: dict[str, Role] = {r.name: r for r in _ROLE_LIST}


def role(name: str) -> str:
    """The colour for a named role. Raises rather than guessing."""
    try:
        return ROLES[name].colour
    except KeyError:
        raise KeyError(
            f"no role named {name!r}; a figure may not introduce a colour "
            f"without adding a role to src/figures/style.py. Roles are: "
            f"{', '.join(sorted(ROLES))}") from None


#: Retained spellings, so the map figures and their tests keep reading. Each
#: is exactly ``role(...)`` and there is no second definition of any colour.
MAP_SEA = role("sea")
MAP_LAND = role("land_outside")
MAP_STUDY_FILL = role("province_fill")
MAP_LATTICE = role("lattice")
MAP_BOUNDARY = role("boundary")
MAP_COASTLINE = role("coastline")

#: Areal classes whose greyscale separation is asserted by the test suite.
MAP_AREAL_CLASSES = ("MAP_SEA", "MAP_LAND", "MAP_STUDY_FILL")


def map_luminances() -> dict:
    """Relative luminance of every map colour, for the greyscale check."""
    return {name: _luminance(globals()[name])
            for name in ("MAP_SEA", "MAP_LAND", "MAP_STUDY_FILL",
                         "MAP_LATTICE", "MAP_BOUNDARY", "MAP_COASTLINE")}


# --------------------------------------------------------------------------
# the relief band
# --------------------------------------------------------------------------

def relief_band() -> tuple[float, float]:
    """Luminance range the shaded relief is allowed to occupy.

    A continuous grey under discrete overlays is a new case for this
    convention, and the answer is to give the relief a **band** and then hold
    every overlay clear of the bottom of it. The band is narrow on purpose: it
    is a ground, not a layer of the figure, and every 0.01 the dark end
    descends is 0.01 taken from the range the line palette has to live in.
    """
    return (RELIEF_DARK_LUMINANCE, RELIEF_LIGHT_LUMINANCE)


def relief_cmap(name: str = GREYSCALE):
    """The grey ramp the hillshade is drawn through, compressed to the band.

    Built from Crameri's greyscale map rather than matplotlib's `gray` so the
    relief sits in the same perceptual family as everything drawn over it, and
    then rescaled so its luminance runs exactly across :func:`relief_band`.
    """
    from matplotlib.colors import LinearSegmentedColormap

    base = sequential(name)
    low, high = relief_band()
    rgb = np.array([base(x)[:3] for x in np.linspace(0.0, 1.0, 256)])
    lum = 0.2126 * rgb[:, 0] + 0.7152 * rgb[:, 1] + 0.0722 * rgb[:, 2]
    # What is taken from grayC is its **spacing**, which is the perceptually
    # uniform part, not its endpoints, which run from near black to near white
    # and would swamp everything drawn over them. Its luminance profile is
    # rescaled onto the band and emitted as neutral greys, whose luminance is
    # their channel value, so the ramp lands on the band exactly rather than
    # approximately. Scaling the channels instead fails at the dark end, where
    # dividing by a luminance near zero clips to black.
    span = lum.max() - lum.min()
    target = low + (lum - lum.min()) / max(span, 1e-9) * (high - low)
    return LinearSegmentedColormap.from_list(
        "relief", np.repeat(target[:, None], 3, axis=1))


def veil(colour, toward, alpha: float):
    """``colour`` composited under ``toward`` at ``alpha``. Straight alpha."""
    import matplotlib.colors as mcolors
    a = np.array(mcolors.to_rgb(colour))
    b = np.array(mcolors.to_rgb(toward))
    return tuple(a * (1 - alpha) + b * alpha)


#: How far out-of-region relief is pushed toward `land_outside`. The study
#: region is distinguished by **contrast**, not by hue, so the distinction
#: survives a black and white print; a tint alone would not.
LAND_VEIL_ALPHA = 0.55
#: How far in-region relief is tinted toward `province_fill`. Small, because
#: the relief has to stay readable underneath it -- the terrain is the reason
#: this figure has terrain.
REGION_TINT_ALPHA = 0.12


def veiled_band(toward: str, alpha: float) -> tuple[float, float]:
    """The relief band's luminance range after veiling toward a role."""
    low, high = relief_band()
    target = _luminance(role(toward))
    return (low * (1 - alpha) + target * alpha,
            high * (1 - alpha) + target * alpha)


#: Line, mark and text roles that are drawn over shaded relief.
OVER_RELIEF = ("boundary", "boundary_minor", "coastline", "lattice",
               "place_marker", "label_text")


def relief_report() -> dict:
    """What tones the relief occupies, and whether the overlays clear them.

    A continuous grey under discrete marks is not a pairwise problem, so it is
    not checked as one. There are two bands, because the same hillshade is
    drawn twice: tinted inside the study region and veiled outside it. Three
    things have to hold and all three are returned rather than asserted here.

    * Every overlay role sits at least :data:`MIN_LUMINANCE_GAP` **below** the
      darkest tone of both bands. Below, not merely apart: an overlay lighter
      than the relief would be invisible on lit slopes and legible on shaded
      ones, which is worse than either.
    * The two bands' flat-ground tones -- what the delta actually is, over most
      of its area -- separate by the same margin, so the study region is
      readable as a region in a print with no colour.
    * The sea clears the bottom of the veiled band, since sea meets
      out-of-region land along most of the frame.
    """
    inside = veiled_band("province_fill", REGION_TINT_ALPHA)
    outside = veiled_band("land_outside", LAND_VEIL_ALPHA)
    lum = {n: ROLES[n].luminance for n in OVER_RELIEF}
    clearance = {n: min(inside[0], outside[0]) - v for n, v in lum.items()}
    return {
        "inside_band": inside,
        "outside_band": outside,
        "flat_ground_gap": inside[1] - outside[1],
        "sea_clearance": outside[0] - ROLES["sea"].luminance,
        "overlay_clearance": clearance,
        "failures": (
            [(n, c) for n, c in clearance.items() if c < MIN_LUMINANCE_GAP]
            + ([("flat ground", inside[1] - outside[1])]
               if inside[1] - outside[1] < MIN_LUMINANCE_GAP else [])
            + ([("sea", outside[0] - ROLES["sea"].luminance)]
               if outside[0] - ROLES["sea"].luminance < MIN_LUMINANCE_GAP
               else [])),
    }


# --------------------------------------------------------------------------
# the checks, run once over the role set
# --------------------------------------------------------------------------

def _pairs() -> list[tuple[str, str]]:
    """Every declared adjacency, once each, sorted."""
    seen = set()
    for name, r in ROLES.items():
        for other in r.against:
            seen.add(tuple(sorted((name, other))))
    return sorted(seen)


def asymmetric_adjacencies() -> list[tuple[str, str]]:
    """Declared adjacencies that only one side names. Should be empty.

    Adjacency is a property of two marks meeting on the page, so if one role
    claims it and the other does not, one of the two declarations is wrong.
    """
    bad = []
    for name, r in ROLES.items():
        for other in r.against:
            if name not in ROLES[other].against:
                bad.append((name, other))
    return sorted(bad)


def greyscale_report() -> dict:
    """Luminance separation over the role set, checked pair by pair.

    Reports the minimum over the **declared** adjacencies, which is the number
    the convention is about, and the minimum over all pairs, which is reported
    only so nobody mistakes the first for the second. All pairs cannot separate
    by 0.15: fourteen roles do not fit into seven slots.
    """
    lum = {name: r.luminance for name, r in ROLES.items()}
    adjacent = [(a, b, abs(lum[a] - lum[b])) for a, b in _pairs()]
    names = sorted(ROLES)
    allpairs = [(a, b, abs(lum[a] - lum[b]))
                for i, a in enumerate(names) for b in names[i + 1:]]
    worst = min(adjacent, key=lambda t: t[2])
    worst_all = min(allpairs, key=lambda t: t[2])
    return {
        "luminance": lum,
        "adjacent_pairs": len(adjacent),
        "min_adjacent_gap": worst[2],
        "min_adjacent_pair": (worst[0], worst[1]),
        "failures": [(a, b, g) for a, b, g in adjacent
                     if g < MIN_LUMINANCE_GAP],
        "min_any_gap": worst_all[2],
        "min_any_pair": (worst_all[0], worst_all[1]),
    }


# Viénot, Brettel and Mollon's dichromat simulation, in the linear-RGB form
# that is standard for protanopia and deuteranopia, with the Brettel two-plane
# construction for tritanopia. Written out rather than taken from a dependency
# because the check must not itself be able to fail silently, and because a
# figure standard that depends on an unpinned package is not a standard.
_LMS_FROM_LINEAR = np.array([
    [0.31399022, 0.63951294, 0.04649755],
    [0.15537241, 0.75789446, 0.08670142],
    [0.01775239, 0.10944209, 0.87256922]])
_LINEAR_FROM_LMS = np.linalg.inv(_LMS_FROM_LINEAR)

_DICHROMAT = {
    "protanopia": np.array([[0.0, 1.05118294, -0.05116099],
                            [0.0, 1.0, 0.0],
                            [0.0, 0.0, 1.0]]),
    "deuteranopia": np.array([[1.0, 0.0, 0.0],
                              [0.9513092, 0.0, 0.04866992],
                              [0.0, 0.0, 1.0]]),
    "tritanopia": np.array([[1.0, 0.0, 0.0],
                            [0.0, 1.0, 0.0],
                            [-0.86744736, 1.86727089, 0.0]]),
}

CVD_KINDS = tuple(_DICHROMAT)


def _to_linear(rgb):
    rgb = np.asarray(rgb, dtype=float)
    return np.where(rgb <= 0.04045, rgb / 12.92, ((rgb + 0.055) / 1.055) ** 2.4)


def _from_linear(rgb):
    rgb = np.clip(np.asarray(rgb, dtype=float), 0.0, 1.0)
    return np.where(rgb <= 0.0031308, rgb * 12.92,
                    1.055 * rgb ** (1 / 2.4) - 0.055)


def simulate_cvd(colour, kind: str):
    """``colour`` as a dichromat of ``kind`` sees it, as an sRGB triple."""
    import matplotlib.colors as mcolors
    linear = _to_linear(mcolors.to_rgb(colour))
    lms = _LMS_FROM_LINEAR @ linear
    seen = _DICHROMAT[kind] @ lms
    return tuple(_from_linear(_LINEAR_FROM_LMS @ seen))


def _lab(rgb):
    """CIE L*a*b* under D65, for a perceptual distance between two colours."""
    linear = _to_linear(rgb)
    xyz = np.array([[0.4124564, 0.3575761, 0.1804375],
                    [0.2126729, 0.7151522, 0.0721750],
                    [0.0193339, 0.1191920, 0.9503041]]) @ linear
    white = np.array([0.95047, 1.0, 1.08883])
    t = xyz / white
    f = np.where(t > 0.008856, np.cbrt(t), 7.787 * t + 16 / 116)
    return np.array([116 * f[1] - 16, 500 * (f[0] - f[1]), 200 * (f[1] - f[2])])


#: The CIE76 distance two roles must keep under every simulated deficiency.
#: Not a published threshold: it is roughly ten times a just-noticeable
#: difference, which is what two marks a few millimetres apart on a printed
#: page actually need, and it is stated here as this project's convention
#: rather than borrowed as if it were a standard.
MIN_CVD_DISTANCE = 10.0


def cvd_report() -> dict:
    """Distance between every declared adjacency under each deficiency."""
    out = {}
    for kind in CVD_KINDS:
        seen = {name: _lab(simulate_cvd(r.colour, kind))
                for name, r in ROLES.items()}
        distances = [(a, b, float(np.linalg.norm(seen[a] - seen[b])))
                     for a, b in _pairs()]
        worst = min(distances, key=lambda t: t[2])
        out[kind] = {
            "min_distance": worst[2],
            "min_pair": (worst[0], worst[1]),
            "failures": [(a, b, d) for a, b, d in distances
                         if d < MIN_CVD_DISTANCE],
        }
    return out


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
            va="bottom", ha="left", color=role("label_text"))
