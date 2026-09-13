"""Held-out skill against buffer radius, for the decay curve the schemes imply.

The figure answers three questions that `notes/draft-results.md` §5.2 states in
prose and that no figure carried.

**Does the spatial null collapse?** It must, and seeing it collapse is what
licenses reading the rest. A model whose only predictor is its neighbours has
nothing left once the neighbours are excluded, so its advantage over a constant
has to fall to zero as soon as the buffer exceeds one cell. It does, between 25
and 50 km, and beyond that the null is numerically identical to the constant.

**Does land cover stay flat?** It should. A model using no spatial information
cannot care how far its training data lie from the cell it is predicting, so its
advantage over a constant ought to be a horizontal line. It is not. It decays
steadily and crosses zero between 300 and 400 km, which says the impervious
coefficient is not one number over this domain: the small skill it has is local.

**Do the two committed cross-validation schemes bracket or disagree?** They
bracket. The null's leave-one-province-out value falls between two adjacent
points of its own buffered curve, so the province-out fold is somewhere on the
buffered continuum rather than off it, and reporting a range across the two
schemes is legitimate.

**The shaded band is that bracketing interval and nothing more.** An earlier
version of this module shaded it as "the distance from a held-out province's
interior to the nearest training cell", which this repository has never
measured. A scratch calculation against the committed fold assignment in
`baseline_predictions_2018.csv` puts the median cell 56 km from its nearest
training cell and only about 4 percent of cells in the 150-to-200 km range, so
that reading was wrong and would have been wrong in the caption too. What the
band is, and all it is, is the interval within which the buffered curve attains
the province-out value, read off the committed table. That the interval is
*wider* than the median fold distance is a real and unexplained finding --
leave-one-province-out is more extrapolative than the geometry alone accounts
for -- and the figure that would settle it is the planned fold map. See
`notes/decisions.md`.

**Why two panels and not one, which is the figure's one real design decision.**
`scripts/buffered_loo_curve.py` records that ``r2_above_constant`` is the
readable column and ``held_out_r2`` is not, because a constant's own held-out
skill falls from -0.002 at no buffer to -0.407 at 500 km: the training mean
drifts away from the withheld cell's neighbourhood, so *every* curve slopes down
whether or not the model is degrading. Plotting the raw metric alone would show
three falling lines and invite the reading that all three models decay. Plotting
only the difference would hide that the baseline moves at all, which is the fact
that makes the difference the right metric.

So panel (a) plots the raw metric for all three models including the constant,
and exists to show the baseline falling. Panel (b) plots the difference for the
two models that have predictors, on both methane fields, and is the panel the
conclusions come from. A reader who looks only at (b) is not misled; a reader
who looks only at (a) would be.

**Every plotted value is read from the committed artefact.** Nothing here
recomputes a fold, for the reason `figures/README.md` records: a figure that
computes its own numbers can disagree with the table beside it, and this
repository has had that happen.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from . import style

ARTEFACT = (Path(__file__).resolve().parents[2] / "data" / "processed"
            / "buffered_loo_2018.csv")

#: The artefact's own model labels, shortened for the legend. The constant is
#: drawn in panel (a) only: in panel (b) it is the reference and would be a
#: flat line at zero by construction.
MODELS = {
    "spatial null (queen neighbour mean)": "spatial null",
    "OLS impervious fraction": "impervious fraction",
    "constant (training mean)": "constant",
}

#: Where the residual semivariogram range and the cross-validation block width
#: fall, in km, from `data/processed/residual_range_2018.csv`. They are 1.1 km
#: apart, which is the point: the block is marginal against the range it would
#: have to exceed, so the block scheme's figures are the optimistic end of the
#: reported range rather than a neutral midpoint. Drawn as one band because two
#: lines 1 % apart would read as one line anyway and labelling them separately
#: would imply a distinction the measurement does not support.
BLOCK_EW_KM = 95.0
RESIDUAL_RANGE_KM = 96.1

#: The two adjacent swept radii that straddle the null's leave-one-province-out
#: value, from the committed table and not assumed: the buffered null is
#: -0.0840 at 150 km and -0.1118 at 200 km against -0.0912 under
#: leave-one-province-out. `_bracket()` derives it rather than trusting these
#: numbers, and a test asserts the two agree, so a re-run of the curve that
#: moved the crossing would fail rather than mislabel the band.
BRACKET_FALLBACK_KM = (150.0, 200.0)


@dataclass(frozen=True)
class Curve:
    """One model on one field: radii in km against both metrics."""

    field: str
    model: str
    radii: tuple[float, ...]
    held_out: tuple[float, ...]
    above_constant: tuple[float, ...]


def from_artefact(path: Path | None = None) -> dict[tuple[str, str], Curve]:
    """Every curve the artefact holds, keyed by (field, model)."""
    rows = list(csv.DictReader((path or ARTEFACT).open(newline="")))
    keys = {(r["field"], r["model"]) for r in rows}
    out: dict[tuple[str, str], Curve] = {}
    for field, model in sorted(keys):
        picked = sorted((r for r in rows
                         if r["field"] == field and r["model"] == model),
                        key=lambda r: float(r["radius_km"]))
        out[(field, model)] = Curve(
            field=field, model=model,
            radii=tuple(float(r["radius_km"]) for r in picked),
            held_out=tuple(float(r["held_out_r2"]) for r in picked),
            above_constant=tuple(float(r["r2_above_constant"]) for r in picked))
    return out


def _province_out_null() -> float:
    """The null's leave-one-province-out held-out R squared, for the marker.

    Read from the baseline table rather than from this figure's own artefact,
    because it is the other scheme's number and the whole point of drawing it
    here is that it comes from somewhere else.
    """
    results = (ARTEFACT.parent / "baseline_results_2018.csv")
    for row in csv.DictReader(results.open(newline="")):
        if (row["model"] == "spatial null (queen neighbour mean)"
                and row["scheme"] == "leave-one-province-out"
                and row["weighting"] == "unweighted"):
            return float(row["held_out_r2"])
    raise KeyError("no province-out row for the spatial null")


def _bracket(curve: Curve, value: float) -> tuple[float, float]:
    """The adjacent radii whose held-out R squared straddle ``value``.

    Derived from the artefact so that the shaded band cannot claim an interval
    the table does not support. Raises if the value falls outside the curve
    entirely, because then there is no bracketing to draw and the figure's
    third question has a different answer.
    """
    for left, right, lo, hi in zip(curve.radii, curve.radii[1:],
                                   curve.held_out, curve.held_out[1:]):
        if hi <= value <= lo:
            return (left, right)
    raise ValueError(f"{value} is not bracketed by {curve.model}")


def decay_figure(curves: dict[tuple[str, str], Curve], *,
                 province_out: float | None = None):
    """Draw both panels and return the figure. Writes nothing."""
    if province_out is None:
        province_out = _province_out_null()

    # style.figure() applies the repository's rcParams, which is what embeds
    # the fonts; plt.subplots() bypasses it and a first version of this module
    # did, producing a PDF with outlined text.
    fig = style.figure(style.FULL_WIDTH_CM, 7.6)
    left, right = fig.subplots(1, 2)

    null_key = "spatial null (queen neighbour mean)"
    imp_key = "OLS impervious fraction"
    null_colour, imp_colour, constant_colour = style.series(3)


    # ---- panel (a): the raw metric, which exists to show the baseline move,
    # and which is the only scale on which the other scheme's value can be
    # drawn, because leave-one-province-out reports a raw held-out R squared.
    band = _bracket(curves[("operational", null_key)], province_out)
    left.axvspan(*band, color=style.role("residual_zero"),
                 linewidth=0, zorder=0)
    for model, colour in ((null_key, null_colour), (imp_key, imp_colour),
                          ("constant (training mean)", constant_colour)):
        curve = curves[("operational", model)]
        left.plot(curve.radii, curve.held_out, color=colour, linewidth=1.4,
                  marker="o", markersize=2.6, solid_joinstyle="round",
                  markerfacecolor=style.role("page"), markeredgewidth=1.1,
                  label=MODELS[model])
    left.axhline(0.0, color=style.role("reference_line"), linewidth=0.7,
                 zorder=0)
    province_line = left.axhline(province_out,
                                 color=style.role("reference_line"),
                                 linewidth=0.9, zorder=1)
    province_line.set_dashes((2.4, 1.8))
    # Two short labels rather than one explaining sentence. The sentence was
    # tried and overran the panel into the curves; what each mark *means* is
    # the caption's job, and the panel only has to say which is which.
    left.annotate("province-out", xy=(4, province_out + 0.015),
                  fontsize=6.6, color=style.role("label_text"),
                  ha="left", va="bottom")
    left.annotate("bracketing\ninterval", xy=(sum(band) / 2.0, 0.30),
                  fontsize=6.6, color=style.role("label_text"),
                  ha="center", va="bottom")
    left.set_xlabel("buffer radius excluded from training (km)")
    left.set_ylabel("held-out $R^2$")
    left.legend(loc="upper right", frameon=False, fontsize=7.2,
                labelcolor=style.role("label_text"))
    style.panel_label(left, "a")

    # ---- panel (b): the difference, which is where the conclusions are.
    #
    # The block width and the residual range are 95.0 and 96.1 km, which is
    # 1.1 km on a 500 km axis: a band between them would be two pixels wide
    # and a reader would see one line. So one line is what is drawn, at the
    # midpoint, and the caption carries both numbers. Drawing a band and
    # calling it a band would claim a visible distinction that is not there.
    marker_km = (BLOCK_EW_KM + RESIDUAL_RANGE_KM) / 2.0
    right.axvline(marker_km, color=style.role("absent_edge"), linewidth=0.9,
                  zorder=0)
    for model, colour in ((null_key, null_colour), (imp_key, imp_colour)):
        for field, dashes in (("operational", None), ("blended", (3.2, 1.6))):
            curve = curves[(field, model)]
            line, = right.plot(curve.radii, curve.above_constant, color=colour,
                               linewidth=1.4, solid_joinstyle="round",
                               marker="o" if field == "operational" else "s",
                               markersize=2.6,
                               markerfacecolor=style.role("page"),
                               markeredgewidth=1.1,
                               label=f"{MODELS[model]}, {field}")
            if dashes:
                line.set_dashes(dashes)
    right.axhline(0.0, color=style.role("reference_line"), linewidth=0.7,
                  zorder=0)
    right.annotate("block width and\nresidual range",
                   xy=(marker_km, 0.60), xytext=(128, 0.66),
                   fontsize=6.6, color=style.role("label_text"),
                   ha="left", va="top",
                   arrowprops=dict(arrowstyle="-", linewidth=0.6,
                                   color=style.role("label_text")))
    right.set_xlabel("buffer radius excluded from training (km)")
    right.set_ylabel("held-out $R^2$ above a constant\nfitted on the same data")
    right.legend(loc="center right", frameon=False, fontsize=7.0,
                 labelcolor=style.role("label_text"))
    style.panel_label(right, "b")

    for axis in (left, right):
        axis.set_xlim(-18, 518)
        axis.tick_params(labelsize=7.4, colors=style.role("label_text"))
        for side in ("top", "right"):
            axis.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            axis.spines[side].set_color(style.role("label_text"))
            axis.spines[side].set_linewidth(0.7)

    fig.tight_layout(pad=0.7)
    return fig
