"""Tests for the model field and residual figure.

Offline, reading only committed artefacts. The figure is built and asserted on
in memory; nothing is written.

Four things carry this figure.

**One scale over two panels.** A field spanning 106 ppb and a field spanning 43
drawn through two autoscaled ramps would look like the same field twice, and
the difference in span is most of the finding.

**Absence is absence in all three panels.** Zero is the most meaningful value
on a diverging scale -- it is the centre and it means the model was right -- so
a residual panel that filled its 97 holes with zero would draw the model's best
cells exactly where it has no cells. The panel must mask them, and the ramp's
centre must not collide with the colour absence is drawn in.

**The diverging ramp is not a sequential ramp with more colours.** It carries a
sign, and the sign is carried by hue alone, because the two limbs are matched
in luminance so that equal errors of either sign read as equal. That trade is
deliberate and is asserted in both directions: the limbs must stay matched, and
the hue must survive every simulated deficiency.

**The residual keeps its spatial structure.** Moran's I of the residual is
0.646 against 0.709 for the observed field, so the fit removes under a tenth of
it. The weights are asserted, not just the number: `ERRATA.md` 6.2 records that
the thesis reported a Moran's I whose weights were never stated, which makes it
unreproducible, and a test that pinned only the value would repeat that.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.figure import Figure

from src.figures import fields, geo, style
from src.figures import residual_field as rf
from src.figures.residual_field import residual_field_figure


@pytest.fixture(scope="module")
def loaded():
    return rf.load_field()


@pytest.fixture(scope="module")
def figure():
    fig = residual_field_figure()
    yield fig
    plt.close(fig)


def test_the_figure_function_returns_a_figure_and_writes_nothing(tmp_path):
    before = set(tmp_path.iterdir())

    fig = residual_field_figure()
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


# --------------------------------------------------------------------------
# the model, and the sample it runs on
# --------------------------------------------------------------------------

def test_the_field_is_the_one_the_scatter_figure_draws():
    """Two figures, one fit. They read the same committed predictions."""
    from src.figures import observed_predicted as op

    assert rf.MODEL in dict(op.PANELS)
    assert (rf.SCHEME, rf.WEIGHTING) == (op.SCHEME, op.WEIGHTING)
    assert rf.PREDICTIONS == op.PREDICTIONS


def test_the_model_runs_on_every_observed_cell_and_the_rice_one_would_not():
    """Why impervious alone. A rice covariate would add a second absence."""
    from src.figures import observed_predicted as op

    metrics = op.load_metrics()
    assert metrics[(rf.MODEL, rf.SCHEME, rf.WEIGHTING)]["n"] == 926
    for name in ("OLS impervious_fraction + rice_fraction_single",
                 "OLS impervious_fraction + rice_fraction_single + interaction",
                 "OLS rice_fraction_single"):
        assert metrics[(name, rf.SCHEME, rf.WEIGHTING)]["n"] == 531


def test_the_rice_covariate_buys_nothing_worth_a_second_kind_of_absence():
    """The other half of the model choice, stated at its strongest against me.

    Added on its own the rice fraction moves the fit backwards, 0.018 to 0.017.
    Added with an interaction it moves it forwards, to 0.033, which an earlier
    draft of this module's docstring did not say. Forwards from 0.018 to 0.033
    is still a fit explaining three percent of held-out variance on 531 of the
    926 cells, which is not worth drawing a map that carries two kinds of
    absence in one near-white.
    """
    from src.figures import observed_predicted as op

    metrics = op.load_metrics()
    r2 = {name: metrics[(name, rf.SCHEME, rf.WEIGHTING)]["r2"] for name in (
        "OLS impervious_fraction [rice sample]",
        "OLS impervious_fraction + rice_fraction_single",
        "OLS impervious_fraction + rice_fraction_single + interaction")}

    alone = r2["OLS impervious_fraction [rice sample]"]
    assert r2["OLS impervious_fraction + rice_fraction_single"] < alone
    assert alone < r2[
        "OLS impervious_fraction + rice_fraction_single + interaction"] < 0.05


def test_the_three_fields_are_on_the_analysis_lattice(loaded):
    observed, predicted, residual, absent = loaded
    spec = geo.study_spec()
    rows = int(round((spec.north - spec.south) / spec.resolution))
    cols = int(round((spec.east - spec.west) / spec.resolution))

    for field in (observed, predicted, residual, absent):
        assert field.shape == (rows, cols)
    assert observed.size == 1023


# --------------------------------------------------------------------------
# one scale over two panels
# --------------------------------------------------------------------------

def test_the_two_value_panels_share_one_norm(figure):
    meshes = [figure.axes[i].collections[0] for i in (0, 1)]
    a, b = (mesh.norm for mesh in meshes)

    assert (a.vmin, a.vmax) == (b.vmin, b.vmax)
    assert meshes[0].cmap.name == meshes[1].cmap.name


def test_the_shared_scale_holds_both_fields_without_clipping(loaded):
    observed, predicted, _, _ = loaded
    low, high = rf.shared_ends(observed, predicted)

    for field in (observed, predicted):
        assert low <= np.nanmin(field) and np.nanmax(field) <= high


def test_the_model_field_covers_well_under_half_the_observed_span(loaded):
    """The finding, as a number. The picture is the same statement."""
    observed, predicted, _, _ = loaded
    extent = rf.spans(observed, predicted)

    assert extent["observed"] > 100.0
    assert extent["model"] < 0.5 * extent["observed"]


def test_the_value_panels_are_not_clipped_the_way_the_composite_is(loaded):
    """A deliberate difference from the composite, so it is pinned.

    Clipping to the 2nd and 98th percentiles would cut the observed span shown
    from 106 ppb to 59 and leave the model field almost untouched, which
    shrinks the contrast the figure is drawn for in the direction that flatters
    the model.
    """
    observed, predicted, _, _ = loaded
    low, high = rf.shared_ends(observed, predicted)
    finite = observed[np.isfinite(observed)]

    assert low <= np.percentile(finite, 2)
    assert high >= np.percentile(finite, 98)
    assert (high - low) > 1.5 * (np.percentile(finite, 98)
                                 - np.percentile(finite, 2))


def test_the_residual_scale_is_symmetric_about_zero():
    norm = fields.residual_norm()

    assert norm(0.0) == pytest.approx(0.5)
    assert norm.vmin == -norm.vmax


def test_the_residual_scale_clips_few_cells_and_says_so(loaded, figure):
    _, _, residual, absent = loaded
    values = residual[~absent]
    clipped = int(np.sum(np.abs(values) > fields.RESIDUAL_LIMIT))

    assert 0 < clipped <= 0.01 * values.size
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)
    assert f"{clipped} of {values.size} cells run past an end" in flat
    assert figure.axes[2].collections[0].colorbar.extend == "both"


# --------------------------------------------------------------------------
# absence in every panel, including the residual
# --------------------------------------------------------------------------

def test_the_same_ninety_seven_cells_are_absent_in_all_three_panels(loaded):
    observed, predicted, residual, absent = loaded

    assert int(absent.sum()) == 97
    for field in (observed, predicted, residual):
        assert np.array_equal(~np.isfinite(field), absent)


def test_an_unobserved_cell_has_no_residual_rather_than_a_residual_of_zero(
        loaded, figure):
    """Zero is the centre of the scale and means the model was right."""
    _, _, residual, absent = loaded

    assert np.all(np.isnan(residual[absent]))
    mesh = figure.axes[2].collections[0]
    assert np.array_equal(np.ma.getmaskarray(mesh.get_array()).reshape(
        residual.shape), absent)


def test_every_panel_draws_the_absent_cells_as_marked_absence(figure):
    for index in range(3):
        collection = fields.absence_artist(figure.axes[index])
        assert collection is not None, index
        assert len(collection.get_paths()) == 97, index


def test_the_ramp_centre_does_not_collide_with_the_colour_absence_is_drawn_in():
    """The reason the diverging ramp is rescaled at all."""
    centre = style._luminance(style.role("residual_zero"))
    absent = style._luminance(style.role("absent_fill"))

    assert abs(absent - centre) >= style.MIN_LUMINANCE_GAP
    assert ("absent_fill", "residual_zero") in [
        tuple(sorted(pair)) for pair in style._pairs()]


def test_the_role_is_the_tone_the_ramp_actually_draws_zero_in():
    """A role that drifted from its ramp would check the wrong colour."""
    import matplotlib.colors as mcolors

    drawn = fields.residual_cmap()(fields.residual_norm()(0.0))[:3]
    declared = mcolors.to_rgb(style.role("residual_zero"))

    assert style._luminance(drawn) == pytest.approx(
        style._luminance(declared), abs=0.01)


# --------------------------------------------------------------------------
# what a diverging ramp needs that a sequential one does not
# --------------------------------------------------------------------------

def test_each_limb_is_monotone_in_luminance_and_wide_enough():
    report = style.diverging_report()

    for wobble in report["wobble"]:
        assert wobble <= style.MAX_LUMINANCE_WOBBLE
    for span in report["limb_span"]:
        assert span > 0.5


def test_the_two_limbs_are_matched_in_luminance_on_purpose():
    """Capped, not floored, and the only such number in the palette module.

    Equal errors of opposite sign must read as equally large. That forces the
    limbs together in luminance, which is what makes the greyscale test below
    an admission rather than a pass.
    """
    report = style.diverging_report()

    assert report["asymmetry"] <= style.MAX_LIMB_ASYMMETRY
    assert report["asymmetry"] < style.MIN_LUMINANCE_GAP


def test_greyscale_carries_the_size_of_an_error_and_not_its_sign(figure):
    """Asserted as false, and stated on the figure, rather than left implied."""
    report = style.diverging_report()

    assert report["greyscale_separates_sign"] is False
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)
    assert "greyscale print of (c) shows the size of an error" in flat


def test_the_sign_survives_every_simulated_deficiency():
    """Hue is the only carrier left, so this is where the check has to bite."""
    report = style.diverging_report()

    assert report["sign_failures"] == []
    for kind, entry in report["sign_under_cvd"].items():
        assert entry["min_distance"] >= style.MIN_CVD_DISTANCE, kind


def test_three_of_the_light_centred_maps_lose_the_sign_under_tritanopia():
    """Which is what chose vik, and it is a measurement rather than a taste.

    Green against brown is the pair tritanopia collapses, and three of
    Crameri's five light-centred diverging maps are built on it.
    """
    for name in ("broc", "cork", "bam"):
        report = style.diverging_report(style.diverging(name))
        assert report["sign_under_cvd"]["tritanopia"]["min_distance"] < (
            style.MIN_CVD_DISTANCE), name
    assert style.diverging_report()["sign_failures"] == []


def test_the_one_map_that_also_passed_draws_zero_as_a_colour():
    """roma separates the signs better than vik and is more symmetric.

    It centres on a light green at chroma 24 against vik's near-neutral 4. Zero
    on this scale means the model was right, and a centre with a hue draws that
    as a third category rather than as the absence of one. It also has the
    shortest limbs of the five.
    """
    chosen = style.diverging_report()
    other = style.diverging_report(style.diverging("roma"))

    assert other["sign_under_cvd"]["tritanopia"]["min_distance"] >= (
        style.MIN_CVD_DISTANCE)
    assert other["asymmetry"] < chosen["asymmetry"]
    assert other["centre_chroma"] > 5 * chosen["centre_chroma"]
    assert min(other["limb_span"]) < min(chosen["limb_span"])


def test_a_dark_centred_diverging_map_is_refused_rather_than_mangled():
    """The rescale divides by the centre's height above the floor."""
    for name in ("berlin", "lisbon", "tofino", "vanimo", "managua"):
        with pytest.raises(ValueError, match="dark-centred"):
            style.diverging(name)


def test_the_ramp_keeps_crameris_spacing_and_only_moves_its_centre():
    """Channels are scaled, so hue and saturation are untouched."""
    import matplotlib.colors as mcolors

    base = style.sequential(style.DIVERGING)
    moved = style.diverging()
    for x in (0.05, 0.25, 0.5, 0.75, 0.95):
        before = mcolors.rgb_to_hsv(base(x)[:3])
        after = mcolors.rgb_to_hsv(moved(x)[:3])
        assert after[0] == pytest.approx(before[0], abs=0.01)
        assert after[1] == pytest.approx(before[1], abs=0.02)
        assert after[2] <= before[2] + 1e-9


# --------------------------------------------------------------------------
# what the residual has left in it
# --------------------------------------------------------------------------

def test_the_weights_are_queen_contiguity_among_observed_cells(loaded):
    """The definition, asserted rather than described. See ERRATA.md 6.2."""
    _, _, _, absent = loaded
    neighbours, rows, cols = rf.queen_weights(absent)
    index = {(int(r), int(c)): i for i, (r, c) in enumerate(zip(rows, cols))}

    assert len(neighbours) == int((~absent).sum()) == 926
    assert max(len(row) for row in neighbours) == 8
    for position, (r, c) in enumerate(zip(rows, cols)):
        assert position not in neighbours[position]          # self excluded
        expected = [index[(int(r) + dr, int(c) + dc)] for dr, dc in rf.QUEEN
                    if (int(r) + dr, int(c) + dc) in index]
        assert sorted(neighbours[position]) == sorted(expected)


def test_an_absent_cell_is_never_anyones_neighbour(loaded):
    _, _, _, absent = loaded
    _, rows, cols = rf.queen_weights(absent)

    assert not absent[rows, cols].any()


def test_a_cell_with_no_observed_neighbour_is_dropped_and_counted(loaded):
    """Not given a weight of zero, which would read as neighbours agreeing."""
    _, _, residual, absent = loaded
    neighbours, rows, cols = rf.queen_weights(absent)
    result = rf.moran_i(residual[rows, cols], neighbours, permutations=0)

    assert sum(1 for row in neighbours if not row) == result["isolated"] == 1


def test_the_fit_leaves_almost_all_the_spatial_structure_behind(loaded):
    """The finding of panel (c), as a number."""
    observed, _, residual, absent = loaded
    report = rf.structure_report(observed, residual, absent)

    assert report["observed"]["i"] == pytest.approx(0.709, abs=0.002)
    assert report["residual"]["i"] == pytest.approx(0.646, abs=0.002)
    assert report["residual"]["i"] > 0.85 * report["observed"]["i"]


def test_the_residual_structure_is_not_something_any_arrangement_would_give(
        loaded):
    observed, _, residual, absent = loaded
    report = rf.structure_report(observed, residual, absent)

    assert report["residual"]["p"] <= 1.0 / (rf.PERMUTATIONS + 1) + 1e-12
    assert report["residual"]["z"] > 20.0


def test_morans_i_is_zero_ish_on_a_field_with_no_structure(loaded):
    """The statistic, checked against something whose answer is known."""
    _, _, _, absent = loaded
    neighbours, _, _ = rf.queen_weights(absent)
    noise = np.random.default_rng(7).normal(size=len(neighbours))
    result = rf.moran_i(noise, neighbours, permutations=0)

    assert abs(result["i"]) < 0.08
    assert result["expected"] == pytest.approx(-1.0 / (len(neighbours) - 1))


def test_the_figure_states_the_weights_beside_the_number(figure):
    """A Moran's I without its weights is not reproducible. ERRATA.md 6.2."""
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "queen contiguity among observed cells" in flat
    assert "row standardised" in flat
    assert "self excluded" in flat
    assert "no distance decay" in flat


# --------------------------------------------------------------------------
# layout and what the figure says
# --------------------------------------------------------------------------

def test_the_layout_closes_across_the_page(figure):
    total = (rf.LEFT_CM + 3 * rf.PANEL_CM + 2 * rf.PANEL_GAP_CM + rf.RIGHT_CM)

    assert total == pytest.approx(rf.FIG_WIDTH_CM, abs=1e-9)
    assert figure.get_figwidth() / style.CM == pytest.approx(rf.FIG_WIDTH_CM)


def test_every_axes_sits_inside_the_figure(figure):
    for index, ax in enumerate(figure.axes):
        box = ax.get_position()
        assert 0.0 <= box.x0 and box.x1 <= 1.0, index
        assert 0.0 <= box.y0 and box.y1 <= 1.0, index


def test_the_three_panels_carry_one_projection_and_one_extent(figure):
    extent = geo.lattice_extent(geo.study_spec())

    for index in range(3):
        ax = figure.axes[index]
        assert ax.get_xlim() == pytest.approx((extent.west, extent.east))
        assert ax.get_ylim() == pytest.approx((extent.south, extent.north))
        assert ax.get_aspect() == pytest.approx(
            1.0 / geo.geographic_aspect(extent.centre_latitude))


def test_one_colour_bar_serves_both_value_panels(figure):
    """Two bars carrying identical numbers invite the reading a shared scale
    exists to prevent: that a reader should check whether they match."""
    bars = [ax for ax in figure.axes if getattr(ax, "_colorbar", None)
            is not None or ax not in figure.axes[:3]]
    assert len(bars) == 2                      # three panels, two scales

    bar = figure.axes[1].collections[0].colorbar
    assert bar.norm is figure.axes[0].collections[0].norm
    assert bar.norm is not figure.axes[2].collections[0].norm
    box = bar.ax.get_position()
    assert box.x0 == pytest.approx(figure.axes[0].get_position().x0)
    assert box.x1 == pytest.approx(figure.axes[1].get_position().x1)


def test_no_panel_is_titled_as_a_prediction_of_methane(figure):
    """The framing constraint. Panel (b) is a model field, not a forecast."""
    titles = [t.get_text() for t in figure.texts
              if t.get_fontweight() == "bold"]

    assert len(titles) == 3
    for title in titles:
        assert "predict" not in title.lower()
    assert "impervious" in titles[1]


def test_the_figure_says_what_the_model_field_is_and_is_not(figure):
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "is not a prediction of methane" in flat
    assert "held out" in flat
    assert "ERRATA.md 7.1 and 1.1" in flat


def test_the_figure_reports_both_ranges_of_the_shared_scale(figure, loaded):
    observed, predicted, _, _ = loaded
    extent = rf.spans(observed, predicted)
    flat = " ".join(" ".join(t.get_text().split()) for t in figure.texts)

    assert "share one unclipped scale" in flat
    assert f"spans {extent['observed']:.1f} ppb" in flat
    assert f"model field {extent['model']:.1f}" in flat
