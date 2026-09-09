"""The field a land-cover model produces, drawn beside what was observed.

Three panels on the analysis lattice, cell for cell: the observed 2018 methane
composite, the field an OLS fit on impervious fraction produces out of fold,
and the difference. The figure exists for the third panel, and the first two
exist to make the third readable.

**Nothing here is a prediction of methane.** Panel (b) is the field a land
cover model produces from one covariate; it is drawn beside the observation so
a reader can see how far apart they are. `ERRATA.md` 7.1 records that land
cover does not explain the observed methane field, and this figure is the
demonstration of that rather than a walking back of it. `ERRATA.md` 1.1 records
that the thesis's Figure 4.7, captioned as this comparison, was the same
embedded image as Figure 4.5(a) -- the comparison was never drawn. This is the
figure that was meant to be there.

The model
---------

OLS on `impervious_fraction` alone, held out under spatial blocks, unweighted:
the same fit panel (b) of the observed-against-predicted figure draws, from the
same committed predictions, so the two figures cannot describe different fits.

Impervious **alone**, and not impervious with rice, which was the other
candidate. Rice fraction exists for 531 of the 926 cells, so a two-covariate
field would be blank over 395 more cells and this figure would carry two kinds
of absence -- one meaning "no sounding" and one meaning "no rice raster" --
drawn in the same near-white in the same panels. The absence treatment is the
part of this figure that has to be unambiguous. The rice model also has little to
add: on its own 531 cells impervious alone reaches 0.018 and impervious with an
additive rice term reaches 0.017, so that covariate moves the fit backwards.
With an interaction term it moves forwards, to 0.033 -- which is stated because
it is the one direction that argues against this choice, and it argues weakly:
three percent of held-out variance on 57 percent of the cells is not worth a
map with two kinds of absence in it.

One scale over two panels
-------------------------

Panels (a) and (b) share one colour scale and one pair of ends. Two
autoscaled panels would render a field spanning 106 ppb and a field spanning 43
through the same ink, and the difference in span is a large part of the
finding. The ends are the observed field's own full range, 1840.5 to 1946.6
ppb, which contains the model field entirely.

The composite figure clips its value panel to the 2nd and 98th percentiles and
this one does not, which is a deliberate difference and not an oversight. There
the job is to read one field well, and the outer four percent are cells with a
median of 2 and 12 soundings. Here the job is to compare two spans, and
clipping would cut the observed span shown from 106 ppb to 59 while leaving the
model field almost untouched -- it would shrink the very contrast the figure is
drawn for, in the direction that flatters the model.

Absence
-------

97 cells of the 1,023 received no qualifying sounding. They are absent in all
three panels, drawn as `fields.py` draws absence everywhere in this repository.

In panel (c) that is a statement rather than an inheritance: **an unobserved
cell has no residual, not a residual of zero.** Zero is the most meaningful
value on a diverging scale -- it is the centre, and it means the model was
right -- so filling 97 holes with it would draw the model's 97 best cells
exactly where it has no cells at all. The scale's centre is held clear of the
absence tone by 0.17 in luminance for the same reason; see
`style.DIVERGING_CENTRE_LUMINANCE`.

What the residual has left in it
--------------------------------

Moran's I of the residual is 0.646 against 0.709 for the observed field: the
fit removes about a tenth of the spatial structure and leaves the rest. The
weights are queen contiguity among observed cells on the 0.25 degree analysis
lattice, row standardised, self excluded, with no distance decay -- stated
because `ERRATA.md` 6.2 records that the thesis reported a Moran's I without
saying what its weights were, which makes the number unreproducible. One cell
has no observed queen neighbour and is dropped from the statistic.
"""

from __future__ import annotations

import csv

import numpy as np

from . import fields, geo, style

PROCESSED = geo.REFERENCE_DIR.parents[0] / "processed"
PREDICTIONS = PROCESSED / "baseline_predictions_2018.csv"
RESULTS = PROCESSED / "baseline_results_2018.csv"

#: The fit this figure draws. See the module docstring for why not the rice one.
MODEL = "OLS impervious_fraction"
SCHEME = "spatial blocks"
WEIGHTING = "unweighted"

#: The queen stencil, the same eight offsets `src.model.baselines` uses for the
#: spatial null. Repeated rather than imported because this module reads a
#: committed CSV and must not depend on the model package to draw a figure.
QUEEN = tuple((dr, dc) for dr in (-1, 0, 1) for dc in (-1, 0, 1)
              if (dr, dc) != (0, 0))

#: Permutations behind the pseudo p value, and the seed. Fixed, so the number
#: in the caption is the number the figure draws.
PERMUTATIONS = 999
PERMUTATION_SEED = 0

# Layout in centimetres.
FIG_WIDTH_CM = style.FULL_WIDTH_CM
LEFT_CM = 1.00
PANEL_GAP_CM = 0.60
RIGHT_CM = 0.25
PANEL_CM = (FIG_WIDTH_CM - LEFT_CM - 2 * PANEL_GAP_CM - RIGHT_CM) / 3.0
NOTE_CM = 0.12
BAR_DROP_CM = 0.62   # map bottom to the top of the colour bar
BAR_CM = 0.22
BOTTOM_CM = 3.72     # x tick labels, then the bars, then six lines of note
TITLE_CM = 0.78      # two lines: no one-line title fits 4.85 cm at 8 point
TOP_CM = 0.14

WIDTH_CM = FIG_WIDTH_CM

NOTE = (
    "(b) is the field one land-cover covariate produces, held out -- fitted on "
    "the training rows of a spatial block and predicted onto rows the fit never "
    "saw -- and is not a prediction of methane; its held-out R squared is "
    "{r2:.3f}. "
    "(a) and (b) share one unclipped scale, {low:.0f} to {high:.0f} ppb: the "
    "observed field spans {observed_span:.1f} ppb and the model field "
    "{model_span:.1f}. "
    "(c) is symmetric about zero at plus or minus {limit:.0f} ppb with arrow "
    "caps; {clipped} of {n} cells run past an end. "
    "{absent} cells received no qualifying sounding and are absent in all three "
    "panels: an unobserved cell has no residual, not a residual of zero. "
    "The two limbs of (c) are matched in luminance so that equal errors of "
    "either sign read as equal, so the sign is carried by hue alone and a "
    "greyscale print of (c) shows the size of an error and not its direction. "
    "Moran's I of the residual {residual_i:.3f}, against {observed_i:.3f} for "
    "the observed field, under queen contiguity among observed cells, row "
    "standardised, self excluded, no distance decay; pseudo p {p} over "
    "{permutations} permutations, {isolated} cell with no observed queen "
    "neighbour dropped. See ERRATA.md 7.1 and 1.1."
)


# --------------------------------------------------------------------------
# the fields
# --------------------------------------------------------------------------

def load_field(model: str = MODEL):
    """Observed, model field and residual on the lattice, plus absence.

    Three arrays shaped (rows, cols) with row 0 northernmost, matching what
    `fields.draw_lattice_field` expects and what the composite raster carries.
    The absence mask is one mask, shared by all three: a cell either has an
    observation and therefore a value in every panel, or it has none and is
    absent in every panel including the residual.
    """
    spec = geo.study_spec()
    shape = (int(round((spec.north - spec.south) / spec.resolution)),
             int(round((spec.east - spec.west) / spec.resolution)))
    observed = np.full(shape, np.nan)
    predicted = np.full(shape, np.nan)

    with PREDICTIONS.open(newline="") as handle:
        for entry in csv.DictReader(handle):
            if entry["model"] != model:
                continue
            r, c = int(entry["row"]), int(entry["col"])
            observed[r, c] = float(entry["observed_ppb"])
            predicted[r, c] = float(entry["predicted_ppb"])

    absent = ~np.isfinite(observed)
    if np.any(absent != ~np.isfinite(predicted)):
        raise ValueError("the observed and model fields disagree about absence")
    return observed, predicted, observed - predicted, absent


def shared_ends(observed, predicted) -> tuple[float, float]:
    """One pair of ends for panels (a) and (b). See the module docstring."""
    values = np.concatenate([observed[np.isfinite(observed)],
                             predicted[np.isfinite(predicted)]])
    return float(np.floor(values.min())), float(np.ceil(values.max()))


def spans(observed, predicted) -> dict:
    """What each field covers, which is the number the caption quotes."""
    return {
        "observed": float(np.nanmax(observed) - np.nanmin(observed)),
        "model": float(np.nanmax(predicted) - np.nanmin(predicted)),
        "residual_low": float(np.nanmin(observed - predicted)),
        "residual_high": float(np.nanmax(observed - predicted)),
    }


# --------------------------------------------------------------------------
# what the residual has left in it
# --------------------------------------------------------------------------

def queen_weights(absent):
    """Row-standardised queen contiguity among the observed cells.

    Returned as the neighbour list itself rather than a matrix, so a reader can
    see exactly what is being claimed: eight offsets, self excluded, a cell
    counted only where it carries an observation, every row divided by its own
    neighbour count so that a coastal cell with three neighbours does not carry
    less weight than an interior cell with eight. No distance decay and no
    kernel: at 0.25 degrees the stencil is the neighbourhood.

    Cells with no observed queen neighbour have an empty row. A row of zeros
    has no defined row-standardisation, so those cells are dropped from the
    statistic and counted, rather than being given a weight of zero -- which
    would quietly treat them as cells whose neighbours all agreed with them.
    """
    rows, cols = np.where(~absent)
    index = {(int(r), int(c)): i for i, (r, c) in enumerate(zip(rows, cols))}
    neighbours = [[index[(int(r) + dr, int(c) + dc)] for dr, dc in QUEEN
                   if (int(r) + dr, int(c) + dc) in index]
                  for r, c in zip(rows, cols)]
    return neighbours, rows, cols


def moran_i(values, neighbours, *, permutations: int = PERMUTATIONS,
            seed: int = PERMUTATION_SEED) -> dict:
    """Moran's I under row-standardised queen contiguity, with a permutation p.

    Under row standardisation the sum of all weights is the number of cells
    that have any neighbour, so the leading n/S0 is not one and is written out
    rather than dropped.

    The reference distribution is a permutation of the values over the same
    cells, which asks the question that matters here -- is this much structure
    more than these values in any arrangement would give -- and does not lean
    on the normality assumption the analytic variance needs, which residuals
    from a fit do not satisfy.
    """
    values = np.asarray(values, dtype="float64")
    keep = np.array([len(row) > 0 for row in neighbours])
    n = int(values.size)
    total_weight = float(keep.sum())

    def statistic(z):
        centred = z - z.mean()
        lagged = np.array([centred[row].mean() if row else 0.0
                           for row in neighbours])
        return (n / total_weight) * float(centred @ lagged) / float(
            centred @ centred)

    observed = statistic(values)
    expected = -1.0 / (n - 1)
    result = {"i": observed, "expected": expected, "n": n,
              "isolated": int((~keep).sum()), "permutations": permutations}
    if permutations:
        rng = np.random.default_rng(seed)
        null = np.array([statistic(rng.permutation(values))
                         for _ in range(permutations)])
        extreme = int(np.sum(np.abs(null - expected) >= abs(observed - expected)))
        result["p"] = (extreme + 1) / (permutations + 1)
        result["z"] = float((observed - expected) / null.std(ddof=1))
    return result


def structure_report(observed=None, residual=None, absent=None) -> dict:
    """Moran's I of the observed field and of the residual, on one weighting."""
    if observed is None:
        observed, _, residual, absent = load_field()
    neighbours, rows, cols = queen_weights(absent)
    return {
        "observed": moran_i(observed[rows, cols], neighbours),
        "residual": moran_i(residual[rows, cols], neighbours),
        "weights": ("queen contiguity among observed cells on the 0.25 degree "
                    "analysis lattice, row standardised, self excluded, "
                    "no distance decay"),
    }


# --------------------------------------------------------------------------
# the figure
# --------------------------------------------------------------------------

def residual_field_figure(width_cm: float = WIDTH_CM):
    """Build and return the three-panel figure. Writes nothing."""
    observed, predicted, residual, absent = load_field()
    spec = geo.study_spec()
    extent = geo.lattice_extent(spec)

    panel_cm = (width_cm - LEFT_CM - 2 * PANEL_GAP_CM - RIGHT_CM) / 3.0
    map_cm = panel_cm * geo.display_ratio(extent)
    height_cm = BOTTOM_CM + map_cm + TITLE_CM + TOP_CM

    fig = style.figure(width_cm=width_cm, height_cm=height_cm)
    provinces = geo.read_layer(geo.PROVINCES)
    land = geo.read_layer(geo.LAND)

    axes = []
    for column in range(3):
        x0 = (LEFT_CM + column * (panel_cm + PANEL_GAP_CM)) / width_cm
        axes.append(fig.add_axes((x0, BOTTOM_CM / height_cm,
                                  panel_cm / width_cm, map_cm / height_cm)))

    low, high = shared_ends(observed, predicted)
    from matplotlib.colors import Normalize
    value_norm = Normalize(vmin=low, vmax=high)

    value_mesh = None
    for ax, field in zip(axes[:2], (observed, predicted)):
        value_mesh = fields.draw_lattice_field(
            ax, field, spec, cmap=fields.field_cmap(), norm=value_norm,
            absent=absent)
        _overlay(ax, extent, provinces, land)

    residual_mesh = fields.draw_lattice_field(
        axes[2], residual, spec, cmap=fields.residual_cmap(),
        norm=fields.residual_norm(), absent=absent)
    _overlay(axes[2], extent, provinces, land)

    axes[0].legend(handles=[fields.absence_handle()], loc="lower left",
                   labelcolor=style.role("label_text"), handlelength=1.2,
                   borderpad=0.35, frameon=True,
                   facecolor=style.role("page"), edgecolor="none",
                   framealpha=0.92)

    for index, (letter, label, ax) in enumerate(zip("abc", TITLES, axes)):
        _title(fig, ax, letter, label, height_cm)
        if index:
            # One set of latitude labels for three panels on one frame.
            # Repeating them puts a number in every gutter, and the gutter is
            # where the eye crosses from one panel to the next.
            ax.set_yticklabels([])

    _value_bar(fig, axes[0], axes[1], value_mesh, height_cm)
    _residual_bar(fig, axes[2], residual_mesh, height_cm)
    _note(fig, width_cm, height_cm, observed, predicted, residual, absent)
    return fig


#: Panel titles, two lines each. None says prediction, and (b) names whose
#: field it is. Two lines because no wording that says what (b) actually is
#: fits 4.85 cm at 8 point, and the alternative was to shorten it into "the
#: model", which is the ambiguity the whole framing exists to close.
TITLES = (
    "observed methane,\n2018 annual mean",
    "the field impervious\nfraction produces",
    "observed minus\nthat field",
)


def _overlay(ax, extent, provinces, land) -> None:
    """The same overlay the composite draws, over the field and not under it."""
    land.boundary.plot(ax=ax, color=style.role("coastline"), linewidth=0.45,
                       zorder=4)
    provinces.boundary.plot(ax=ax, color=style.role("boundary"),
                            linewidth=0.6, zorder=5)
    geo.apply_projection(ax, extent)
    xticks, yticks = geo.graticule(extent, step=3.0)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    ax.xaxis.set_major_formatter(geo.degree_formatter("x"))
    ax.yaxis.set_major_formatter(geo.degree_formatter("y"))
    ax.tick_params(labelsize=style.TICK_SIZE - 0.5, length=2.0)
    for spine in ax.spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.7)
        spine.set_edgecolor(style.role("boundary"))


def _title(fig, ax, letter, label, height_cm) -> None:
    box = ax.get_position()
    fig.text(box.x0, box.y1 + 0.07 / height_cm, f"({letter}) {label}",
             ha="left", va="bottom", fontsize=style.LABEL_SIZE - 0.5,
             fontweight="bold", linespacing=1.25,
             color=style.role("label_text"))


def _bar_axes(fig, left_ax, right_ax, height_cm):
    left, right = left_ax.get_position(), right_ax.get_position()
    drop = (BAR_DROP_CM + BAR_CM) / height_cm
    return fig.add_axes((left.x0, left.y0 - drop, right.x1 - left.x0,
                         BAR_CM / height_cm))


def _value_bar(fig, first, second, mesh, height_cm) -> None:
    """One bar under both value panels, because they are one scale.

    Drawn spanning the two rather than repeated under each. A bar under each
    would be two bars carrying identical numbers, which invites exactly the
    reading the shared scale exists to prevent: that the two panels might be
    scaled differently and a reader should check.
    """
    cax = _bar_axes(fig, first, second, height_cm)
    bar = fig.colorbar(mesh, cax=cax, orientation="horizontal")
    bar.set_label("Mean XCH$_4$, bias corrected (ppb): one scale over (a) and "
                  "(b)", fontsize=style.LABEL_SIZE - 0.5)
    bar.ax.tick_params(labelsize=style.TICK_SIZE, length=2.5)
    bar.outline.set_linewidth(0.6)


def _residual_bar(fig, ax, mesh, height_cm) -> None:
    cax = _bar_axes(fig, ax, ax, height_cm)
    bar = fig.colorbar(mesh, cax=cax, orientation="horizontal", extend="both")
    bar.set_label("Observed minus model field (ppb)",
                  fontsize=style.LABEL_SIZE - 0.5)
    bar.ax.tick_params(labelsize=style.TICK_SIZE, length=2.5)
    bar.outline.set_linewidth(0.6)
    bar.set_ticks([-fields.RESIDUAL_LIMIT, -fields.RESIDUAL_LIMIT / 2, 0.0,
                   fields.RESIDUAL_LIMIT / 2, fields.RESIDUAL_LIMIT])


def _note(fig, width_cm, height_cm, observed, predicted, residual,
          absent) -> None:
    low, high = shared_ends(observed, predicted)
    extent = spans(observed, predicted)
    values = residual[~absent]
    structure = structure_report(observed, residual, absent)
    r2 = held_out_r2()

    text = NOTE.format(
        low=low, high=high,
        observed_span=extent["observed"], model_span=extent["model"],
        limit=fields.RESIDUAL_LIMIT,
        clipped=int(np.sum(np.abs(values) > fields.RESIDUAL_LIMIT)),
        n=int(values.size), absent=int(absent.sum()),
        residual_i=structure["residual"]["i"],
        observed_i=structure["observed"]["i"],
        p=_p_text(structure["residual"]["p"], PERMUTATIONS),
        permutations=PERMUTATIONS,
        isolated=structure["residual"]["isolated"],
        r2=r2)
    fig.text(0.25 / width_cm, NOTE_CM / height_cm, _wrap(text, 166),
             ha="left", va="bottom", fontsize=style.TICK_SIZE - 1.5,
             linespacing=1.4, color=style.role("label_text"))


def _p_text(p: float, permutations: int) -> str:
    """A pseudo p at its floor is a bound, and is written as one."""
    floor = 1.0 / (permutations + 1)
    return f"<= {floor:.3f}" if p <= floor + 1e-12 else f"{p:.3f}"


def held_out_r2(model: str = MODEL) -> float:
    with RESULTS.open(newline="") as handle:
        for row in csv.DictReader(handle):
            if (row["model"] == model and row["scheme"] == SCHEME
                    and row["weighting"] == WEIGHTING):
                return float(row["held_out_r2"])
    raise KeyError(model)


def _wrap(text: str, width: int) -> str:
    import textwrap
    return "\n".join(textwrap.wrap(text, width))
