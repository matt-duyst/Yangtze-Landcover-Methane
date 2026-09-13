"""What the column record can constrain: the DOFS sweep and its two limits.

This is the figure for the claim the paper rests on, and its difficulty is that
the headline number is the one most likely to be quoted away from its
qualifications. So the qualifications are drawn rather than deferred to the
caption, and the figure is arranged so that the reassuring panel cannot be read
without the two that bound it.

**Panel (a): expected degrees of freedom against the assumed domain total.**
Sensitivity depends on how much is being emitted, which is not known for this
domain to better than a factor of two, so the quantity is swept rather than
stated. Three horizontal references mark the thresholds the operational
literature uses. The shaded vertical band is what the literature supports for
this domain's total — **an input to the sweep and not an output of it**, which
the axis label says in those words, because a reader who took the band for a
result would think this work had estimated the region's emissions.

**Panel (b): how that information is distributed across cells, which is the
finding rather than a caveat.** A DOFS total says how many independent pieces of
information the observations carry. It does not say whether any one cell is
constrained, and for this record none is: at the top of the literature band the
best-observed cell reaches a sensitivity of 0.065 against the 0.5 an operational
inversion treats as a practical minimum. The panel plots the median, the 90th
percentile and the maximum at both ends of the band against that threshold, on a
log axis because a linear one would put all six points on the floor. **The sweep
alone cannot carry this**: a DOFS of 22 is a large number and reads as capability
until the distribution behind it is visible.

**Panel (c): the same limit in emission units, which is the version a reader
remembers.** Inverting the sensitivity expression at a = 0.5 needs no prior at
all, because at fixed sensitivity it depends only on the observation counts. It
gives what a cell would have to emit for the observations to constrain it half
independently of the prior. Drawn against the range a large municipal landfill
emits, it says that a median cell's threshold sits above the whole of that
range, so no single landfill would half-constrain a typical cell.

**The best-observed cell is the exception and the panel shows it.** Its
threshold is 49 Gg/y, which falls *inside* the landfill range rather than above
it, so a landfill at the top of that range would just reach half-constraint --
in the one cell of 926 with the most observation days. That is the strongest
statement this record supports in the favourable direction, and it is one cell.
Everywhere else, individual large point sources sit below the threshold and
above zero: visible to an inversion as a partial constraint weighted toward the
prior, not as an independent measurement.

**Panels (b) and (c) are the same statement in two units** and both are here
because they fail differently. The sensitivity panel is exact and abstract; the
emission panel is concrete and requires the reader to accept a landfill figure
from the literature. Neither alone is as convincing as the pair.

**The estimate is a reimplementation, and the figure says so where the number
is.** No transport model was run and no emissions were optimised. The axis label
in panel (a) carries it, not only the caption, because that is the panel a
reader will photograph.

**And the sweep is a lower bound.** It spreads the assumed total uniformly over
covered cells, while real emissions concentrate; concentration raises the sum,
because sensitivity rises faster than linearly in the per-cell emission. Panel
(a) is annotated accordingly.

Every plotted value is read from `data/processed/inversion_dofs_2018.csv`.
Nothing here evaluates the sensitivity expression.
"""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path

from . import style

ARTEFACT = (Path(__file__).resolve().parents[2] / "data" / "processed"
            / "inversion_dofs_2018.csv")

#: The thresholds the operational literature uses, and where each comes from.
#: 0.5 is the per-inversion practical minimum the Permian weekly-monitoring work
#: adopts for estimating a basin total with 2-sigma error at or under 30 %; 1
#: and 2 are IMI's own stated minimum viability and marginal ceiling.
THRESHOLDS = ((0.5, "practical minimum"), (1.0, "minimum viability"),
              (2.0, "marginal ceiling"))

#: What a large municipal landfill emits, Gg/y. A literature scale rather than a
#: measurement from this work, and labelled as such on the panel.
LANDFILL_GG = (10.0, 50.0)

_SWEEP = re.compile(r"expected DOFS at ([\d.]+) Tg/y domain prior")
_CROSS = re.compile(r"domain prior at which DOFS reaches ([\d.]+)")
_CELL = re.compile(r"per-cell sensitivity (median|90th percentile|maximum) "
                   r"at ([\d.]+) Tg/y")


@dataclass(frozen=True)
class Sweep:
    """Everything the artefact holds that this figure draws."""

    totals: tuple[float, ...]
    dofs: tuple[float, ...]
    crossings: dict[float, float]
    sensitivity: dict[tuple[str, float], float]
    prior_free_median_gg: float
    prior_free_best_gg: float
    band: tuple[float, float]
    cells: int


def from_artefact(path: Path | None = None) -> Sweep:
    """Read the sweep, the crossings and the two prior-free thresholds."""
    rows = list(csv.DictReader((path or ARTEFACT).open(newline="")))
    by = {r["quantity"]: r for r in rows}

    swept: list[tuple[float, float]] = []
    crossings: dict[float, float] = {}
    sens: dict[tuple[str, float], float] = {}
    for row in rows:
        if (m := _SWEEP.fullmatch(row["quantity"])):
            swept.append((float(m.group(1)), float(row["value"])))
        elif (m := _CROSS.fullmatch(row["quantity"])):
            crossings[float(m.group(1))] = float(row["value"])
        elif (m := _CELL.fullmatch(row["quantity"])):
            sens[(m.group(1), float(m.group(2)))] = float(row["value"])
    swept.sort()

    anchors = sorted({total for _, total in sens})
    if len(anchors) != 2:
        raise ValueError(f"expected two band ends, found {anchors}")

    return Sweep(
        totals=tuple(t for t, _ in swept),
        dofs=tuple(d for _, d in swept),
        crossings=crossings,
        sensitivity=sens,
        # Tg/y in the artefact, Gg/y on the panel: a cell-scale emission in Tg
        # is three leading zeros and unreadable.
        prior_free_median_gg=1000.0 * float(
            by["emission for a = 0.5, median cell"]["value"]),
        prior_free_best_gg=1000.0 * float(
            by["emission for a = 0.5, best-observed cell"]["value"]),
        band=(anchors[0], anchors[1]),
        cells=int(float(by["cells with at least one observation day"]["value"])),
    )


def capability_figure(sweep: Sweep):
    """Draw the three panels and return the figure. Writes nothing."""
    fig = style.figure(style.FULL_WIDTH_CM, 7.0)
    left, middle, right = fig.subplots(1, 3)

    curve_colour, band_colour, mark_colour = style.series(3)

    # ---- (a) the sweep
    lo, hi = sweep.band
    left.axvspan(lo, hi, color=style.role("residual_zero"), linewidth=0,
                 zorder=0)
    for value, label in THRESHOLDS:
        left.axhline(value, color=style.role("reference_line"), linewidth=0.7,
                     zorder=1)
        # **The value alone, at the left edge.** Three placements of the
        # threshold *names* were crossed by the curve, and the geometry says
        # they always will be: the lowest line is reached at 1.77 Tg, which
        # leaves about 1.2 decades of clear axis on either side of the
        # crossing, and 1.2 decades holds roughly thirteen characters at this
        # size. No useful name fits. A name placed to the right of the
        # crossing, below the line, is clear of the curve in principle and
        # still clips it where the curve approaches the line.
        #
        # So the lines carry their values, which is three characters and
        # cannot be reached, and the caption names what each threshold is.
        # The names are editorial gloss; the values are the data, and the y
        # axis already says they are DOFS.
        left.annotate(f"{value:g}", xy=(0.105, value),
                      xytext=(0, 2), textcoords="offset points",
                      fontsize=6.6, color=style.role("label_text"),
                      ha="left", va="bottom")
    left.plot(sweep.totals, sweep.dofs, color=curve_colour, linewidth=1.5,
              solid_joinstyle="round", zorder=3)
    for value, _ in THRESHOLDS:
        if value in sweep.crossings:
            left.plot([sweep.crossings[value]], [value], marker="o",
                      markersize=3.4, color=mark_colour,
                      markerfacecolor=style.role("page"), markeredgewidth=1.3,
                      zorder=4)
    left.set_xscale("log")
    left.set_yscale("log")
    left.set_xlabel("assumed domain total (Tg a$^{-1}$)")
    left.set_ylabel("expected DOFS (closed-form estimate,\nnot an inversion)")
    left.annotate("shaded band: an input,\nnot a result",
                  xy=(0.03, 0.97), xycoords="axes fraction", fontsize=6.4,
                  color=style.role("label_text"), va="top")
    style.panel_label(left, "a")

    # ---- (b) the distribution behind the total
    names = ("median", "90th percentile", "maximum")
    offsets = {lo: -0.16, hi: 0.16}
    for total, marker in ((lo, "o"), (hi, "s")):
        xs = [i + offsets[total] for i in range(len(names))]
        ys = [sweep.sensitivity[(n, total)] for n in names]
        middle.plot(xs, ys, marker=marker, markersize=4.0, linewidth=0,
                    color=band_colour, markerfacecolor=style.role("page"),
                    markeredgewidth=1.4, label=f"{total:g} Tg a$^{{-1}}$")
    middle.axhline(0.5, color=style.role("reference_line"), linewidth=0.9,
                   zorder=1)
    middle.annotate("0.5: half constrained by\nthe observations",
                    xy=(-0.52, 0.56), fontsize=6.4,
                    color=style.role("label_text"), ha="left", va="bottom")
    middle.set_xticks(range(len(names)))
    middle.set_xticklabels(["median\ncell", "90th\npercentile", "best\ncell"],
                           fontsize=6.8)
    middle.set_yscale("log")
    middle.set_ylim(1e-3, 1.6)
    middle.set_xlim(-0.6, len(names) - 0.4)
    middle.set_ylabel("per-cell averaging kernel sensitivity")
    middle.legend(loc="lower right", frameon=False, fontsize=6.8,
                  labelcolor=style.role("label_text"),
                  title="assumed total", title_fontsize=6.8)
    style.panel_label(middle, "b")

    # ---- (c) the same limit in emission units
    right.axhspan(LANDFILL_GG[0], LANDFILL_GG[1],
                  color=style.role("absent_span"), linewidth=0, zorder=0)
    bars = ("median\ncell", "best-observed\ncell")
    values = (sweep.prior_free_median_gg, sweep.prior_free_best_gg)
    for i, (label, value) in enumerate(zip(bars, values)):
        right.plot([i], [value], marker="D", markersize=4.6,
                   color=mark_colour, markerfacecolor=style.role("page"),
                   markeredgewidth=1.5, zorder=3)
        right.annotate(f"{value:.0f}", xy=(i, value), xytext=(0, 7),
                       textcoords="offset points", fontsize=7.0,
                       color=style.role("label_text"), ha="center")
    right.annotate("a large municipal\nlandfill emits this",
                   xy=(-0.52, LANDFILL_GG[1] - 2), fontsize=6.4,
                   color=style.role("label_text"), ha="left", va="top")
    right.set_xticks(range(len(bars)))
    right.set_xticklabels(bars, fontsize=6.8)
    right.set_xlim(-0.6, len(bars) - 0.4)
    right.set_ylim(0, 1.15 * max(values))
    right.set_ylabel("emission needed for the observations to\n"
                     "constrain a cell half independently (Gg a$^{-1}$)")
    style.panel_label(right, "c")

    for axis in (left, middle, right):
        axis.tick_params(labelsize=7.0, colors=style.role("label_text"))
        for side in ("top", "right"):
            axis.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            axis.spines[side].set_color(style.role("label_text"))
            axis.spines[side].set_linewidth(0.7)

    fig.tight_layout(pad=0.7)
    return fig
