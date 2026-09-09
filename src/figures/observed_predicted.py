"""Observed methane against what four models produce, held out.

The reproduction's central result is negative and the figure set had no
diagnostic at all. This is the one the result deserves, because the finding is
a **shape** rather than a number: a model with held-out R squared near 0.09
predicts close to the mean everywhere, so its cloud lies flat while a model of
smoothness tracks the diagonal. That contrast is the result, and reporting it
as two R squared values in a table asks a reader to take on trust what a
picture can show.

Nothing here is a prediction of methane. Each panel shows the field a model
produces from its own predictors, drawn against what was observed, and the
point of the figure is the distance between them. `ERRATA.md` 7.1 records that
land cover does not explain the observed field; this is the demonstration of
that and not a walking back of it.

Held out, and it matters
------------------------

Every predicted value is out of fold: fitted on the training rows of a spatial
block and predicted onto rows the fit never saw, pooled across folds by
`src.model.baselines.held_out_predictions`. In-sample fitted values would have
been the most flattering mistake available here and the gap is not small --
the spatial null's in-sample R squared is 0.685 against a held-out 0.332, and
drawing the first would have made the smoothness bar look twice the bar it is.
`scripts/compute_baseline_predictions.py` refuses to write unless the metrics
recomputed from the pooled predictions reproduce the committed
`baseline_results_2018.csv`, which is what says the figure and the table
describe one fit.

Which four models, and why not the others
-----------------------------------------

The table holds 22 model families, not eight, over two schemes and two
weightings: 88 rows. Twelve of those families run on the 531 cells that carry a
rice fraction and ten on all 926, and `baselines.py` states the rule that
decides the rest -- results on different samples must not be compared without
saying so. Four panels side by side is a comparison whatever a caption says, so
every panel here is one of the ten on the 926-cell sample.

Chosen against the table rather than from expectation, they span its whole
range on that sample: a constant at -0.008, impervious fraction at 0.085, the
spatial null at 0.332 and wind at 0.653. The progression is no information,
then land cover, then smoothness, then meteorology, and the finding is where
land cover sits in it -- nearer the constant than the smoothness.

The wind panel is a reference and not an explanation. `ERRATA.md` 7.4 records
that the wind association is not attributable, because each cell's annual mean
is taken over whichever days it was observed on and those differ by up to 228
days. It is here because a reader needs to see what a cloud that does track the
diagonal looks like, drawn from this same data on this same axis.

Scheme, weighting, and the panel that stops them being a choice
---------------------------------------------------------------

The panels are spatial blocks, unweighted. Spatial blocks because it is the
only scheme in which the spatial null is a bar at all: under
leave-one-province-out a held-out province's interior has no training
neighbour, so the null falls to -0.091. It still beats the constant's -0.172
there, but a negative R squared means it explains none of the held-out
variance, so there is no diagonal-tracking cloud to set the flat ones against
and the contrast the figure exists for disappears. Unweighted because a scatter
draws one mark per cell, and a weighted metric printed beside an unweighted
picture would describe a fit the picture does not show.

Both of those are choices, and a figure that made them silently would be
hiding that the answer depends on them. Panel (e) draws the held-out R squared
of all four models under all four combinations of scheme and weighting, so the
dependence is on the page rather than in a sentence.

Weight is drawn, because it cannot be ignored
---------------------------------------------

A cell's observed value is the mean of between 1 and 410 soundings, so the
marks carry very different precision and a scatter that drew them alike would
misrepresent the fit. Mark **area** carries the count, on the same half-decade
classes the composite figure's legend uses. Size rather than opacity, because
opacity in a cloud of 926 marks confounds precision with overplotting, and
because size survives a black and white print on its own.
"""

from __future__ import annotations

import csv

import numpy as np

from . import fields, geo, style

PROCESSED = geo.REFERENCE_DIR.parents[0] / "processed"
PREDICTIONS = PROCESSED / "baseline_predictions_2018.csv"
RESULTS = PROCESSED / "baseline_results_2018.csv"

#: The scheme and weighting the panels draw. See the module docstring.
SCHEME = "spatial blocks"
WEIGHTING = "unweighted"

#: Panels in reading order, with the label each carries.
PANELS = (
    ("constant (global mean)", "constant"),
    ("OLS impervious_fraction", "impervious fraction"),
    ("spatial null (queen neighbour mean)", "spatial null"),
    ("OLS wind (u, v, speed)", "wind"),
)

#: Every scheme and weighting the summary panel reports.
COMBINATIONS = (
    ("spatial blocks", "unweighted"),
    ("spatial blocks", "by sounding count"),
    ("leave-one-province-out", "unweighted"),
    ("leave-one-province-out", "by sounding count"),
)

#: Mark area in points squared, one per half-decade sounding class. The classes
#: are `fields.COUNT_EDGES`, so a reader who has met the composite figure's
#: legend has met these. Area rather than diameter, because area is what the
#: eye reads as quantity.
MARK_AREAS = (1.6, 3.0, 5.2, 8.6, 14.0, 22.0)

#: How solid a mark is. Fixed, not varied: opacity that carried the count would
#: confound precision with overplotting, and 926 marks overplot heavily.
MARK_ALPHA = 0.55

# Layout in centimetres.
FIG_WIDTH_CM = style.FULL_WIDTH_CM
LEFT_CM = 1.30
PANEL_CM = 4.95
PANEL_GAP_CM = 0.45
COLUMN_GAP_CM = 0.90
SUMMARY_CM = 3.70
RIGHT_CM = 0.75      # the summary panel's rightmost tick label sits here
NOTE_CM = 0.12
LEGEND_CM = 1.42
BOTTOM_CM = 2.70     # legend, then the bottom row's tick and axis labels
ROW_GAP_CM = 0.55    # only the lower row's title: the upper row has no ticks
TITLE_CM = 0.40
TOP_CM = 0.20

WIDTH_CM = FIG_WIDTH_CM


def load_predictions() -> dict:
    """Held-out predictions per model, from the committed table."""
    out: dict = {}
    with PREDICTIONS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            entry = out.setdefault(row["model"], {"observed": [],
                                                  "predicted": [],
                                                  "count": []})
            entry["observed"].append(float(row["observed_ppb"]))
            entry["predicted"].append(float(row["predicted_ppb"]))
            entry["count"].append(int(row["sounding_count"]))
    return {name: {key: np.asarray(values) for key, values in entry.items()}
            for name, entry in out.items()}


def load_metrics() -> dict:
    """Held-out RMSE and R squared for every model, scheme and weighting."""
    out: dict = {}
    with RESULTS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            out[(row["model"], row["scheme"], row["weighting"])] = {
                "r2": float(row["held_out_r2"]),
                "rmse": float(row["held_out_rmse_ppb"]),
                "n": int(row["n"]),
            }
    return out


def shared_limits(predictions) -> tuple[float, float]:
    """One pair of limits for every panel, from the observed field.

    Shared, and this is not a nicety. Each panel autoscaled would stretch a
    model that predicts a two-ppb range across the same box as one that
    predicts a hundred, and the flatness that is the whole finding would be
    invisible. The limits come from the observed field because that is the
    quantity all four panels have in common.
    """
    observed = next(iter(predictions.values()))["observed"]
    low, high = float(observed.min()), float(observed.max())
    pad = 0.04 * (high - low)
    return (low - pad, high + pad)


def observed_predicted_figure(width_cm: float = WIDTH_CM,
                              height_cm: float | None = None):
    """Build and return the observed-against-predicted figure. Writes nothing."""
    if height_cm is None:
        height_cm = (BOTTOM_CM + 2 * PANEL_CM + ROW_GAP_CM + TITLE_CM
                     + TOP_CM)
    fig = style.figure(width_cm=width_cm, height_cm=height_cm)

    def axes(x_cm, y_cm, w_cm, h_cm):
        return fig.add_axes((x_cm / width_cm, y_cm / height_cm,
                             w_cm / width_cm, h_cm / height_cm))

    predictions = load_predictions()
    metrics = load_metrics()
    limits = shared_limits(predictions)

    right_x = LEFT_CM + PANEL_CM + PANEL_GAP_CM
    top_y = BOTTOM_CM + PANEL_CM + ROW_GAP_CM
    positions = ((LEFT_CM, top_y), (right_x, top_y),
                 (LEFT_CM, BOTTOM_CM), (right_x, BOTTOM_CM))

    letters = "abcd"
    for (name, label), (x_cm, y_cm), letter in zip(PANELS, positions, letters):
        ax = axes(x_cm, y_cm, PANEL_CM, PANEL_CM)
        _draw_panel(ax, predictions[name], metrics[(name, SCHEME, WEIGHTING)],
                    limits, bottom_row=y_cm == BOTTOM_CM,
                    left_column=x_cm == LEFT_CM)
        _title(fig, ax, letter, label, height_cm)

    summary_x = LEFT_CM + 2 * PANEL_CM + PANEL_GAP_CM + COLUMN_GAP_CM
    summary_h = 2 * PANEL_CM + ROW_GAP_CM - TITLE_CM
    ax_summary = axes(summary_x, BOTTOM_CM, SUMMARY_CM, summary_h)
    _draw_summary(ax_summary, metrics)
    _title(fig, ax_summary, "e", "all four fits", height_cm)

    _keys(fig, width_cm, height_cm)
    return fig


def _title(fig, ax, letter, label, height_cm) -> None:
    box = ax.get_position()
    fig.text(box.x0, box.y1 + 0.09 / height_cm, f"({letter}) {label}",
             ha="left", va="bottom", fontsize=style.LABEL_SIZE,
             fontweight="bold", color=style.role("label_text"))


# --------------------------------------------------------------------------
# a panel
# --------------------------------------------------------------------------

def mark_areas(counts) -> np.ndarray:
    """Mark area per cell, by the composite figure's half-decade classes."""
    edges = np.asarray(fields.COUNT_EDGES[:-1], dtype="float64")
    index = np.clip(np.searchsorted(edges, np.asarray(counts), side="right") - 1,
                    0, len(MARK_AREAS) - 1)
    return np.asarray(MARK_AREAS)[index]


def _draw_panel(ax, data, metric, limits, *, bottom_row, left_column) -> None:
    ax.plot(limits, limits, color=style.role("reference_line"),
            linewidth=0.7, zorder=2, solid_capstyle="butt", label="one-to-one")
    ax.scatter(data["observed"], data["predicted"],
               s=mark_areas(data["count"]),
               color=style.role("observation_mark"), alpha=MARK_ALPHA,
               linewidths=0, zorder=3, label="cell")

    ax.set_xlim(*limits)
    ax.set_ylim(*limits)
    ax.set_aspect("equal")
    ticks = [1850, 1875, 1900, 1925]
    ax.set_xticks(ticks)
    ax.set_yticks(ticks)
    ax.tick_params(length=2.5, labelsize=style.TICK_SIZE - 0.5)
    if not bottom_row:
        ax.set_xticklabels([])
    else:
        ax.set_xlabel("Observed XCH$_4$ (ppb)", fontsize=style.LABEL_SIZE)
    if not left_column:
        ax.set_yticklabels([])
    else:
        ax.set_ylabel("Model field (ppb)", fontsize=style.LABEL_SIZE)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    for name in ("left", "bottom"):
        ax.spines[name].set_linewidth(0.7)
        ax.spines[name].set_edgecolor(style.role("boundary"))

    # The numbers go on the panel, in the corner the cloud never reaches,
    # because the geometry gives the shape and only a number gives the size.
    ax.text(0.03, 0.97,
            f"held-out $R^2$ {metric['r2']:+.3f}\nRMSE {metric['rmse']:.2f} ppb",
            transform=ax.transAxes, ha="left", va="top",
            fontsize=style.TICK_SIZE - 0.5, linespacing=1.4,
            color=style.role("label_text"))


# --------------------------------------------------------------------------
# the summary panel
# --------------------------------------------------------------------------

def summary_rows(metrics) -> list:
    """Held-out R squared for every panel model under every combination."""
    out = []
    for name, label in PANELS:
        entry = {"label": label, "values": {}}
        for scheme, weighting in COMBINATIONS:
            entry["values"][(scheme, weighting)] = metrics[
                (name, scheme, weighting)]["r2"]
        out.append(entry)
    return out


def _draw_summary(ax, metrics) -> None:
    """One row per model, four marks each: two schemes by two weightings.

    Scheme takes the colour and weighting takes the fill, which is the same
    separation `style.source_computation_styles` makes for lines: two
    different things, two channels, the stronger one to the stronger
    distinction. An open mark is the weighted fit throughout.
    """
    rows = summary_rows(metrics)
    colours = dict(zip(("spatial blocks", "leave-one-province-out"),
                       style.series(2)))
    offsets = {"unweighted": 0.13, "by sounding count": -0.13}

    # Over the model rows only, not the whole panel: the reference is a
    # statement about the marks, and drawn full height it runs through the
    # scheme key below them.
    ax.vlines(0.0, -0.55, len(rows) - 0.75,
              color=style.role("reference_line"), linewidth=0.7, zorder=2,
              label="no skill")
    for index, entry in enumerate(rows):
        base = index
        for (scheme, weighting), value in entry["values"].items():
            filled = weighting == "unweighted"
            ax.plot([value], [base + offsets[weighting]], marker="o",
                    markersize=4.0, zorder=3,
                    markerfacecolor=(colours[scheme] if filled
                                     else style.role("page")),
                    markeredgecolor=colours[scheme], markeredgewidth=1.0,
                    linestyle="none")

    # The model names go inside the panel. Outside, they are long enough to
    # reach back across the gutter and land on the scatter panels, which the
    # first draft demonstrated.
    for index, entry in enumerate(rows):
        ax.text(-0.33, index - 0.34, entry["label"], ha="left", va="center",
                fontsize=style.TICK_SIZE - 0.5,
                color=style.role("label_text"))
    ax.set_yticks([])
    # Room under the last row for the scheme key.
    ax.set_ylim(-0.6, len(rows) + 0.55)
    ax.invert_yaxis()
    ax.set_xlim(-0.35, 0.78)
    ax.set_xticks([-0.25, 0.0, 0.25, 0.5, 0.75])
    ax.set_xlabel("Held-out $R^2$", fontsize=style.LABEL_SIZE)
    ax.tick_params(length=2.5, labelsize=style.TICK_SIZE - 0.5)

    # The scheme key lives inside this panel. It is the only place two schemes
    # appear, and the figure legend below already carries the weighting.
    from matplotlib.lines import Line2D
    ax.legend(handles=[
        Line2D([], [], marker="o", linestyle="none", markersize=3.6,
               markerfacecolor=colours[scheme], markeredgecolor=colours[scheme],
               label=label)
        for scheme, label in (("spatial blocks", "spatial blocks"),
                              ("leave-one-province-out", "one province out"))],
        loc="lower left", bbox_to_anchor=(-0.02, 0.015), frameon=False,
        handlelength=1.0, handletextpad=0.4, borderpad=0.0, borderaxespad=0.0,
        labelspacing=0.35, fontsize=style.TICK_SIZE - 1.0,
        labelcolor=style.role("label_text"))

    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_linewidth(0.7)
    ax.spines["bottom"].set_edgecolor(style.role("boundary"))


# --------------------------------------------------------------------------
# keys and the note
# --------------------------------------------------------------------------

NOTE = (
    "Every predicted value is out of fold, fitted on training blocks and "
    "predicted onto cells the fit never saw; in-sample values would be far more "
    "flattering, the spatial null's in-sample R² being {in_sample:.3f} against its "
    "held-out {held_out:.3f}. Panels share one pair of axis limits, so the flat "
    "clouds are flat and not merely stretched. Mark area is the sounding count on "
    "the composite figure's half-decade classes, because a cell's observed value "
    "is the mean of between {low:.0f} and {high:.0f} soundings. Land cover does "
    "not explain the observed field; see ERRATA.md 7.1. Wind is a reference and "
    "not an explanation: ERRATA.md 7.4 records that it is not attributable.")


def _keys(fig, width_cm, height_cm) -> None:
    from matplotlib.lines import Line2D

    counts = (2, 20, 200)
    handles = [
        Line2D([], [], marker="o", linestyle="none",
               markersize=np.sqrt(mark_areas([count])[0]) * 1.9,
               markerfacecolor=style.role("observation_mark"),
               markeredgewidth=0, alpha=MARK_ALPHA,
               color=style.role("observation_mark"),
               label=f"{count} soundings")
        for count in counts]
    handles.append(Line2D([], [], color=style.role("reference_line"),
                          linewidth=0.7, label="one to one"))
    handles.append(Line2D([], [], marker="o", linestyle="none", markersize=4.0,
                          markerfacecolor=style.series(2)[0],
                          markeredgecolor=style.series(2)[0],
                          label="(e) unweighted"))
    handles.append(Line2D([], [], marker="o", linestyle="none", markersize=4.0,
                          markerfacecolor=style.role("page"),
                          markeredgecolor=style.series(2)[0],
                          markeredgewidth=1.0,
                          label="(e) weighted by count"))
    legend = fig.legend(
        handles=handles, loc="lower left", ncols=6,
        bbox_to_anchor=(LEFT_CM / width_cm, LEGEND_CM / height_cm),
        labelcolor=style.role("label_text"), handlelength=1.2, borderpad=0.0,
        borderaxespad=0.0, frameon=False, columnspacing=1.4,
        handletextpad=0.4)
    legend.set_in_layout(False)

    metrics = load_metrics()
    null = metrics[("spatial null (queen neighbour mean)", SCHEME, WEIGHTING)]
    in_sample = _in_sample_r2("spatial null (queen neighbour mean)")
    counts = next(iter(load_predictions().values()))
    text = NOTE.format(in_sample=in_sample, held_out=null["r2"],
                       low=counts["count"].min(), high=counts["count"].max())
    fig.text(LEFT_CM / width_cm, NOTE_CM / height_cm, _wrap(text, 132),
             ha="left", va="bottom", fontsize=style.TICK_SIZE - 1.5,
             linespacing=1.4, color=style.role("label_text"))


def _in_sample_r2(model: str) -> float:
    with RESULTS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if (row["model"] == model and row["scheme"] == SCHEME
                    and row["weighting"] == WEIGHTING):
                return float(row["in_sample_r2"])
    raise KeyError(model)


def _wrap(text: str, width: int) -> str:
    import textwrap
    return "\n".join(textwrap.wrap(text, width))
