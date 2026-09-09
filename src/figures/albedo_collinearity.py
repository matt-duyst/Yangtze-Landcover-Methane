"""Why the urban association cannot be attributed, rather than why it is false.

The reproduction's negative finding is that land cover does not explain the
observed methane field. The obvious objection is that the urban association is
real and the analysis is too blunt to find it. This figure answers that
objection, and the answer is not that the association is an artefact. It is
that **this data cannot separate the two explanations, even in principle**.

Three legs, one panel each, and a reader should be able to follow all three
without the caption.

**Impervious fraction and retrieved surface albedo co-vary**, at Spearman
+0.76 unweighted over 926 cells. Cities are brighter and drier than their
surroundings, which is a fact about cities and not about the retrieval.

**Albedo predicts retrieved methane**, at Pearson +0.70 on the bias-corrected
field and +0.74 on the raw one. That is a documented retrieval artefact with
the documented sign -- TROPOMI's methane retrieval needs light back from the
surface and overestimates over bright ground -- and the operational a
posteriori correction removes about 2 percent of the fitted slope unweighted.

**Controlling for albedo removes the impervious association.** On the
bias-corrected field the partial correlation falls from +0.35 to +0.02.

So there is a path from urban extent through surface brightness to retrieved
methane that has nothing to do with emissions, and the two ends of it are too
collinear here to be told apart.

What this figure does not claim
-------------------------------

**Not that the urban signal is an artefact.** At Spearman +0.76 there is not
enough independent variation to say which of the two is doing the work. A real
urban methane signal would produce this pattern too, because cities really are
brighter, so controlling for albedo over-controls by an unknown amount.
`ERRATA.md` 7.4 states this carefully and the caption matches its care rather
than exceeding it.

**Not that the partial correlation is the corrected estimate.** It is one of
two readings. The other is that the control is incomplete, and panel (e) is
where that reading is visible rather than hidden: on the **raw** retrieval the
impervious association survives control at +0.15, and the raw retrieval is the
field carrying the *larger* uncorrected albedo bias. Incomplete control is at
least as available a reading of that survival as a real urban signal, so the
figure draws all four field-by-weighting combinations and lets neither stand
for the answer.

**What would separate them** is a retrieval known to be albedo-unbiased, or
variation in urban extent at constant albedo. This region provides neither.
That is a limitation of the study design rather than of the analysis, and the
figure says so.

Negative albedo is not an error
-------------------------------

166 of the 926 cells carry a negative annual mean `surface_albedo_SWIR`. A
reflectance cannot be negative; this is not a reflectance. It is a parameter
fitted by the retrieval, and over dark surfaces the fit lands slightly below
zero. Those cells are the dark ones, mostly water and the wetter coastal
margin, which is exactly the population the question concerns, so dropping them
would remove 18 percent of the grid non-randomly and from precisely the wrong
place. `data/processed/README.md` records it and the figure points there.

A reference line over a ramp, which the palette had not met
-----------------------------------------------------------

Panel (a) draws methane through the sequential ramp and also draws a line at
albedo zero. **No single tone can clear a full sequential ramp by the palette's
0.15 convention.** The truncated ramp runs from luminance 0.097 to 0.771, so
clearing both ends would need a tone below -0.05 or above 0.921, and the second
is the page. `reference_line` at 0.099 clears the ramp's light end by 0.672 and
its dark end by 0.002.

The treatment is the relief band's rather than a pairwise one: the line is
drawn **beneath** the marks, so where it meets the darkest cells they occlude
it rather than blending with it, and it is legible across the rest of the
panel, which is where a reader looks for it. The y ticks carry the same
information independently. Panels (b) and (d) have no such problem: their marks
are `observation_mark` at 0.451, which clears `reference_line` by 0.35.

Nothing on this figure is a literal
-----------------------------------

Every correlation drawn or printed is recomputed at build time from
`analysis_grid_2018.csv` and `methane_covariates_2018.csv` through
`src.model.association`, the same module `scripts/test_albedo_confounder.py`
uses, and the module refuses to build unless the bias-corrected values
reproduce the committed `albedo_confounder_2018.csv`. The two slopes are read
from `albedo_correction_2018.csv` rather than refitted. A number written into a
figure module is a number that goes stale silently, and this repository has
already had that failure in prose.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from . import fields, geo, style
from .observed_predicted import mark_areas

REPO = Path(__file__).resolve().parents[2]
PROCESSED = geo.REFERENCE_DIR.parents[0] / "processed"
GRID = PROCESSED / "analysis_grid_2018.csv"
COVARIATES = PROCESSED / "methane_covariates_2018.csv"
CONFOUNDER = PROCESSED / "albedo_confounder_2018.csv"
CORRECTION = PROCESSED / "albedo_correction_2018.csv"

#: The albedo band. SWIR is the one the methane retrieval fits in, so it is the
#: one whose bias reaches the methane. NIR is measured too and behaves the same
#: way; `albedo_confounder_2018.csv` carries both.
ALBEDO = "surface_albedo_SWIR"
PREDICTOR = "impervious_fraction"

#: The two methane fields, by the column each is stored in. The panels draw the
#: bias-corrected one, which is what every other result in this repository uses;
#: panel (e) draws both, because the difference between them is the whole of the
#: second reading this figure has to keep open.
FIELDS = (("ch4_bias_corrected_ppb", "bias corrected"),
          ("ch4_raw_ppb", "raw retrieval"))
WEIGHTINGS = (("unweighted", False), ("by sounding count", True))

#: How closely a recomputed correlation must match the committed table before
#: the figure will build. The table is rounded to four places, so this is the
#: rounding and nothing more.
TOLERANCE = 5e-4

# Layout in centimetres.
FIG_WIDTH_CM = style.FULL_WIDTH_CM
LEFT_CM = 1.22
PANEL_GAP_CM = 0.78
RIGHT_CM = 0.60
#: Derived rather than typed, so the row cannot stop closing across the page.
#: The first draft carried it as a constant and it went stale by 0.06 cm.
PANEL_CM = (FIG_WIDTH_CM - LEFT_CM - 2 * PANEL_GAP_CM - RIGHT_CM) / 3.0
PANEL_H_CM = 3.86
BAR_DROP_CM = 0.92     # panel (a) bottom to the top of its colour bar
BAR_CM = 0.20
#: Row one's tick labels and axis label, then panel (a)'s colour bar and its
#: own label beneath them, then row two's title. The bar is what sets this: (b)
#: and (c) would close on 0.9 cm.
ROW_GAP_CM = 2.30
TITLE_CM = 0.40
TOP_CM = 0.14
NOTE_CM = 0.12
#: Row two's tick labels and axis label, measured off the rendered figure.
AXIS_LABEL_CM = 0.88
#: Row two's labels, then the note. Set from `note_height_cm` rather than by
#: eye: the note wraps to nine lines and the first draft budgeted for seven,
#: which put its top line through both axis labels.
BOTTOM_CM = 3.52

WIDTH_CM = FIG_WIDTH_CM

TITLES = (
    "cities are brighter",
    "brighter ground reads higher",
    "the association at issue",
    "albedo removed from both",
    "before and after control, four ways",
)

NOTE = (
    "Every number here is recomputed at build time from analysis_grid_2018.csv "
    "and methane_covariates_2018.csv, and the figure refuses to build unless "
    "the bias-corrected values reproduce albedo_confounder_2018.csv. "
    "Mark area is the sounding count on the composite figure's half-decade "
    "classes: a cell's value is a mean over {low} to {high} soundings and the "
    "correlations differ between weighted and unweighted, so (e) reports both. "
    "{negative} of the {cells} cells carry a negative mean SWIR albedo. That is "
"not an error and not a fill value: albedo here is a parameter the "
    "retrieval fits, not a reflectance it measures, and over dark surfaces the "
    "fit lands below zero; see data/processed/README.md for why those cells are "
    "kept. "
    "This does not show that the urban signal is an artefact. At Spearman "
    "{rho:+.2f} there is not enough independent variation to say which of the "
    "two is doing the work, and cities really are brighter, so controlling for "
    "albedo over-controls by an unknown amount. Nor is the partial correlation "
    "the corrected estimate: on the raw retrieval it survives at {raw:+.2f}, "
    "and that field carries the larger uncorrected bias, so incomplete control "
    "reads as well as a real signal. Separating them needs a retrieval known to "
    "be albedo-unbiased, or urban extent varying at constant albedo. This "
    "region provides neither, which is a limit of the study design rather than "
    "of the analysis. See ERRATA.md 7.4."
)


# --------------------------------------------------------------------------
# the numbers, all of them measured
# --------------------------------------------------------------------------

@dataclass(frozen=True)
class Cells:
    """The sample every panel draws, aligned and finite."""

    albedo: np.ndarray
    predictor: np.ndarray
    methane: dict
    weight: np.ndarray

    @property
    def n(self) -> int:
        return int(self.albedo.size)


def load_cells() -> Cells:
    """Albedo, impervious fraction, both methane fields and the counts."""
    from src.model.association import paired
    from src.model.baselines import load_table

    tables = {label: load_table(GRID, target=column, covariates=COVARIATES)
              for column, label in FIELDS}
    first = tables[FIELDS[0][1]]
    columns = [first.columns[ALBEDO], first.columns[PREDICTOR],
               first.weight.astype("float64")]
    columns += [tables[label].y for _, label in FIELDS]
    kept = paired(*columns)
    return Cells(albedo=kept[0], predictor=kept[1], weight=kept[2],
                 methane={label: kept[3 + index]
                          for index, (_, label) in enumerate(FIELDS)})


def associations(cells: Cells | None = None) -> dict:
    """Every correlation this figure draws, keyed by field and weighting.

    Computed here rather than read from `albedo_confounder_2018.csv` because
    that table carries only the bias-corrected field, and the second reading
    this figure must keep open lives in the raw one. The corrected values are
    checked against it; see :func:`reproduces_committed_table`.
    """
    from src.model.association import correlate, partial_correlation

    cells = load_cells() if cells is None else cells
    out: dict = {}
    for _, label in FIELDS:
        methane = cells.methane[label]
        for weighting, weighted in WEIGHTINGS:
            weight = cells.weight if weighted else None
            out[(label, weighting)] = {
                "albedo_predictor": correlate(
                    f"{ALBEDO} ~ {PREDICTOR}", cells.predictor, cells.albedo,
                    weight=weight),
                "methane_albedo": correlate(
                    f"methane ~ {ALBEDO}", cells.albedo, methane,
                    weight=weight),
                "methane_predictor": correlate(
                    f"methane ~ {PREDICTOR}", cells.predictor, methane,
                    weight=weight),
                "partial": partial_correlation(
                    f"methane ~ {PREDICTOR}", cells.predictor, methane,
                    [cells.albedo], [ALBEDO], weight=weight),
            }
    return out


def committed_confounder() -> dict:
    """What `albedo_confounder_2018.csv` says, for the reproduction check."""
    out: dict = {}
    with CONFOUNDER.open(newline="") as handle:
        for row in csv.DictReader(handle):
            key = (row["weighting"], row["relationship"],
                   row["controlling_for"])
            out[key] = {"pearson": float(row["pearson"]),
                        "spearman": float(row["spearman"]),
                        "n": int(row["n"])}
    return out


def reproduces_committed_table(computed: dict | None = None) -> list[str]:
    """Where a recomputed bias-corrected value disagrees with the table.

    The same gate `scripts/compute_baseline_predictions.py` applies to the
    held-out predictions, and for the same reason: a figure and a committed
    table that describe different computations are worse than either alone.
    """
    computed = associations() if computed is None else computed
    table = committed_confounder()
    out = []
    for weighting, _ in WEIGHTINGS:
        entry = computed[("bias corrected", weighting)]
        checks = (
            ("albedo_predictor", f"{ALBEDO} ~ {PREDICTOR}", ""),
            ("methane_albedo", f"methane ~ {ALBEDO}", ""),
            ("methane_predictor", f"methane ~ {PREDICTOR}", ""),
            ("partial", f"methane ~ {PREDICTOR}", ALBEDO),
        )
        for key, relationship, control in checks:
            want = table[(weighting, relationship, control)]
            got = entry[key]
            for statistic in ("pearson", "spearman"):
                gap = abs(getattr(got, statistic) - want[statistic])
                if gap > TOLERANCE:
                    out.append(f"{weighting} {relationship} {control} "
                               f"{statistic}: {getattr(got, statistic):.4f} "
                               f"against {want[statistic]:.4f}")
            if got.n != want["n"]:
                out.append(f"{weighting} {relationship}: n {got.n} against "
                           f"{want['n']}")
    return out


def slopes() -> dict:
    """The fitted ppb per unit albedo, from the committed correction table."""
    out: dict = {}
    with CORRECTION.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if row["albedo"] != ALBEDO:
                continue
            out[(row["series"], row["weighting"])] = {
                "slope": float(row["slope_ppb_per_unit_albedo"]),
                "standard_error": float(row["standard_error"]),
                "r2": float(row["r2"]),
            }
    return out


def correction_reduction(weighting: str = "unweighted") -> float:
    """How much of the albedo slope the operational correction removes."""
    fitted = slopes()
    raw = fitted[("raw retrieval", weighting)]["slope"]
    corrected = fitted[("bias corrected", weighting)]["slope"]
    return (raw - corrected) / raw


def negative_albedo(cells: Cells | None = None) -> int:
    cells = load_cells() if cells is None else cells
    return int((cells.albedo < 0).sum())


# --------------------------------------------------------------------------
# the figure
# --------------------------------------------------------------------------

def albedo_collinearity_figure(width_cm: float = WIDTH_CM):
    """Build and return the five-panel figure. Writes nothing."""
    cells = load_cells()
    computed = associations(cells)
    disagreements = reproduces_committed_table(computed)
    if disagreements:
        raise ValueError(
            "recomputed correlations disagree with "
            "albedo_confounder_2018.csv, so the figure and the table would "
            "describe different computations: " + "; ".join(disagreements))

    panel_cm = (width_cm - LEFT_CM - 2 * PANEL_GAP_CM - RIGHT_CM) / 3.0
    height_cm = (BOTTOM_CM + PANEL_H_CM + TITLE_CM + ROW_GAP_CM + PANEL_H_CM
                 + TITLE_CM + TOP_CM)

    fig = style.figure(width_cm=width_cm, height_cm=height_cm)
    top_y = (BOTTOM_CM + PANEL_H_CM + TITLE_CM + ROW_GAP_CM) / height_cm
    bottom_y = BOTTOM_CM / height_cm
    axes = []
    for column in range(3):
        x0 = (LEFT_CM + column * (panel_cm + PANEL_GAP_CM)) / width_cm
        axes.append(fig.add_axes((x0, top_y, panel_cm / width_cm,
                                  PANEL_H_CM / height_cm)))
    axes.append(fig.add_axes((LEFT_CM / width_cm, bottom_y,
                              panel_cm / width_cm, PANEL_H_CM / height_cm)))
    wide = 2 * panel_cm + PANEL_GAP_CM
    axes.append(fig.add_axes(
        ((LEFT_CM + panel_cm + PANEL_GAP_CM) / width_cm, bottom_y,
         wide / width_cm, PANEL_H_CM / height_cm)))

    entry = computed[("bias corrected", "unweighted")]
    areas = mark_areas(cells.weight)
    mesh = _panel_a(axes[0], cells, entry, areas)
    _panel_b(axes[1], cells, entry, areas)
    _panel_c(axes[2], cells, entry, areas)
    _panel_d(axes[3], cells, entry, areas)
    _panel_e(axes[4], computed)

    _colourbar(fig, axes[0], mesh, height_cm)
    for letter, label, ax in zip("abcde", TITLES, axes):
        _title(fig, ax, letter, label, height_cm)
    _note(fig, width_cm, height_cm, cells, computed)
    return fig


def _scatter(ax, x, y, areas, *, colour=None, values=None, norm=None):
    from matplotlib.colors import Normalize

    if values is None:
        return ax.scatter(x, y, s=areas, marker="o", linewidths=0,
                          color=style.role("observation_mark")
                          if colour is None else colour,
                          alpha=0.55, zorder=3, rasterized=False)
    norm = Normalize(*np.percentile(values, (2, 98))) if norm is None else norm
    return ax.scatter(x, y, s=areas, c=values, cmap=fields.field_cmap(),
                      norm=norm, marker="o", linewidths=0, alpha=0.9,
                      zorder=3, rasterized=False)


def _frame(ax, xlabel, ylabel) -> None:
    ax.set_xlabel(xlabel, fontsize=style.LABEL_SIZE - 0.5)
    ax.set_ylabel(ylabel, fontsize=style.LABEL_SIZE - 0.5)
    ax.tick_params(labelsize=style.TICK_SIZE - 0.5, length=2.2)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_linewidth(0.7)
        ax.spines[side].set_edgecolor(style.role("boundary"))


def _annotate(ax, text, corner="upper left") -> None:
    x, y, ha, va = {
        "upper left": (0.03, 0.97, "left", "top"),
        "lower right": (0.97, 0.03, "right", "bottom"),
    }[corner]
    ax.text(x, y, text, transform=ax.transAxes, ha=ha, va=va,
            fontsize=style.TICK_SIZE - 1.4, linespacing=1.3,
            color=style.role("label_text"))


def _panel_a(ax, cells, entry, areas):
    """Leg one, with methane as a third variable in the colour."""
    mesh = _scatter(ax, cells.predictor, cells.albedo, areas,
                    values=cells.methane["bias corrected"])
    # Beneath the marks, deliberately. See the module docstring: no tone clears
    # a full sequential ramp at both ends, so the line is occluded by the
    # darkest cells rather than blending into them.
    ax.axhline(0.0, color=style.role("reference_line"), linewidth=0.6,
               zorder=2, label="albedo-zero")
    _frame(ax, "Impervious fraction", "Surface albedo, SWIR")
    a = entry["albedo_predictor"]
    # Lower right, because the cloud fills the top of this panel: the bright
    # cells are the impervious ones, which is the panel's whole point.
    _annotate(ax, f"Spearman {a.spearman:+.3f}\nPearson {a.pearson:+.3f}",
              corner="lower right")
    return mesh


def _panel_b(ax, cells, entry, areas):
    """Leg two."""
    _scatter(ax, cells.albedo, cells.methane["bias corrected"], areas)
    ax.axvline(0.0, color=style.role("reference_line"), linewidth=0.6,
               zorder=2, label="albedo-zero")
    _frame(ax, "Surface albedo, SWIR", "Mean XCH$_4$ (ppb)")
    a = entry["methane_albedo"]
    _annotate(ax, f"Pearson {a.pearson:+.3f}\nSpearman {a.spearman:+.3f}")


def _panel_c(ax, cells, entry, areas):
    """The association the reproduction is asked to explain."""
    _scatter(ax, cells.predictor, cells.methane["bias corrected"], areas)
    _frame(ax, "Impervious fraction", "Mean XCH$_4$ (ppb)")
    a = entry["methane_predictor"]
    _annotate(ax, f"Pearson {a.pearson:+.3f}\np {a.pearson_p:.1e}")


def _panel_d(ax, cells, entry, areas):
    """The added-variable plot: what partial_correlation correlates.

    Drawn from `src.model.association.residuals`, the same function
    `partial_correlation` uses, so the cloud and the number cannot disagree
    about what was removed.
    """
    from src.model.association import residuals

    rx = residuals(cells.predictor, [cells.albedo])
    ry = residuals(cells.methane["bias corrected"], [cells.albedo])
    _scatter(ax, rx, ry, areas)
    ax.axhline(0.0, color=style.role("reference_line"), linewidth=0.6,
               zorder=2, label="residual-zero")
    _frame(ax, "Impervious fraction, albedo removed",
           "XCH$_4$ residual (ppb)")
    a = entry["partial"]
    _annotate(ax, f"Pearson {a.pearson:+.3f}\np {a.pearson_p:.2f}")


def _panel_e(ax, computed) -> None:
    """Before and after control, on both fields and both weightings.

    A slope chart rather than bars. The quantity is a change in one number, and
    a pair of bars asks a reader to compare two lengths where a line already is
    the comparison. It also keeps the four cases side by side, which is the
    point: on the raw field the association survives control, and the figure
    must not let either field stand for the answer.
    """
    from matplotlib.lines import Line2D

    colours = style.series(2)
    rows = []
    for index, (_, label) in enumerate(FIELDS):
        for weighting, _ in WEIGHTINGS:
            entry = computed[(label, weighting)]
            rows.append((label, weighting, colours[index],
                         entry["methane_predictor"].pearson,
                         entry["partial"].pearson,
                         entry["partial"].pearson_p))

    for position, (label, weighting, colour, before, after, p) in enumerate(
            rows):
        y = len(rows) - 1 - position
        ax.plot([after, before], [y, y], color=colour, linewidth=0.9,
                zorder=3, solid_capstyle="round", label=f"{label}-{weighting}")
        ax.plot([before], [y], marker="o", markersize=3.4, color=colour,
                markeredgecolor=colour, zorder=4, linestyle="none",
                label=f"{label}-{weighting}-before")
        # Open after control, filled before it, so the direction of the pair is
        # readable without following the line.
        ax.plot([after], [y], marker="o", markersize=3.4, zorder=5,
                linestyle="none", markeredgecolor=colour,
                markerfacecolor=style.role("page"), markeredgewidth=0.9,
                label=f"{label}-{weighting}-after")
        # Both texts hang off the *after* marker, which is always the left end,
        # so nothing is drawn outside the axes and no row label has to sit in
        # panel (d)'s gutter. The first draft put them there and they landed on
        # top of it.
        ax.text(after, y + 0.26, f"{label}, {weighting}", ha="left",
                va="bottom", fontsize=style.TICK_SIZE - 1.2,
                color=style.role("label_text"))
        p_text = f"p {p:.0e}" if p < 0.01 else f"p {p:.2f}"
        ax.text(after, y - 0.26, f"{before:+.3f} to {after:+.3f}, {p_text}",
                ha="left", va="top", fontsize=style.TICK_SIZE - 1.6,
                color=style.role("label_text"))

    ax.axvline(0.0, color=style.role("reference_line"), linewidth=0.6,
               zorder=2, label="no-association")
    ax.set_ylim(-0.92, len(rows) - 0.20)
    ax.set_yticks([])
    ax.set_xlim(-0.025, 0.50)
    _frame(ax, "Pearson correlation, methane against impervious fraction", "")
    ax.spines["left"].set_visible(False)
    handles = [
        Line2D([], [], marker="o", linestyle="-", markersize=3.4,
               linewidth=0.9, color=style.role("observation_mark"),
               markerfacecolor=style.role("observation_mark"),
               label="before control"),
        Line2D([], [], marker="o", linestyle="none", markersize=3.4,
               markeredgewidth=0.9,
               markeredgecolor=style.role("observation_mark"),
               markerfacecolor=style.role("page"), label="after control"),
    ]
    legend = ax.legend(handles=handles, loc="lower right", ncols=2,
                       labelcolor=style.role("label_text"), handlelength=1.6,
                       borderpad=0.3, frameon=False, columnspacing=1.2,
                       fontsize=style.TICK_SIZE - 1.6)
    legend.set_in_layout(False)


def _colourbar(fig, ax, mesh, height_cm) -> None:
    box = ax.get_position()
    cax = fig.add_axes((box.x0, box.y0 - (BAR_DROP_CM + BAR_CM) / height_cm,
                        box.width, BAR_CM / height_cm))
    bar = fig.colorbar(mesh, cax=cax, orientation="horizontal", extend="both")
    bar.set_label("Mean XCH$_4$ in (a) (ppb)", fontsize=style.LABEL_SIZE - 1.0)
    bar.ax.tick_params(labelsize=style.TICK_SIZE - 1.0, length=2.2)
    bar.outline.set_linewidth(0.6)


def _title(fig, ax, letter, label, height_cm) -> None:
    box = ax.get_position()
    fig.text(box.x0, box.y1 + 0.08 / height_cm, f"({letter}) {label}",
             ha="left", va="bottom", fontsize=style.LABEL_SIZE - 0.5,
             fontweight="bold", color=style.role("label_text"))


NOTE_SIZE = style.TICK_SIZE - 1.5


def note_text(cells: Cells | None = None, computed: dict | None = None,
              width_cm: float = WIDTH_CM) -> str:
    """The note, wrapped, with every number measured rather than typed."""
    from .framework_reproduction import wrap_to_cm

    cells = load_cells() if cells is None else cells
    computed = associations(cells) if computed is None else computed
    entry = computed[("bias corrected", "unweighted")]
    text = NOTE.format(
        low=int(cells.weight.min()), high=int(cells.weight.max()),
        negative=negative_albedo(cells), cells=cells.n,
        rho=entry["albedo_predictor"].spearman,
        raw=computed[("raw retrieval", "unweighted")]["partial"].pearson)
    return wrap_to_cm(text, width_cm - LEFT_CM - RIGHT_CM, NOTE_SIZE)


def note_height_cm(text: str | None = None) -> float:
    """How tall the wrapped note stands, so `BOTTOM_CM` can clear it."""
    lines = (note_text() if text is None else text).count("\n") + 1
    return lines * NOTE_SIZE * 1.4 / 72.0 * 2.54


def _note(fig, width_cm, height_cm, cells, computed) -> None:
    fig.text(LEFT_CM / width_cm, NOTE_CM / height_cm,
             note_text(cells, computed, width_cm),
             ha="left", va="bottom", fontsize=NOTE_SIZE,
             linespacing=1.4, color=style.role("label_text"))
