"""Tests for the 2018 methane composite figure.

Offline, reading only committed artefacts. The figure is built and asserted on
in memory; nothing is written.

The check worth having is that the figure draws the number of cells the data
has. A map that silently drops or duplicates cells is exactly the class of
quiet error this project has spent weeks finding, and it is not visible by
looking: 926 coloured cells and 927 coloured cells are the same picture.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.collections import PatchCollection, QuadMesh
from matplotlib.figure import Figure

from src.figures import fields, geo, style
from src.figures.composite import composite_figure, read_composite

SPEC = geo.study_spec()
CORRECTED, COUNTS, ABSENT = read_composite()


def map_panels(figure):
    """The two map axes.

    Selected by carrying both a mesh and an absence collection, because a
    horizontal colour bar is itself a QuadMesh and would otherwise be counted
    as a third panel.
    """
    return [ax for ax in figure.axes
            if any(isinstance(c, QuadMesh) for c in ax.collections)
            and fields.absence_artist(ax) is not None]


@pytest.fixture(scope="module")
def figure():
    fig = composite_figure(SPEC, CORRECTED, COUNTS, ABSENT)
    yield fig
    plt.close(fig)


def test_the_figure_function_returns_a_figure_and_writes_nothing(tmp_path):
    before = set(tmp_path.iterdir())

    fig = composite_figure(SPEC, CORRECTED, COUNTS, ABSENT)
    try:
        assert isinstance(fig, Figure)
        assert set(tmp_path.iterdir()) == before
    finally:
        plt.close(fig)


def test_the_data_holds_the_cell_counts_the_caption_quotes():
    assert CORRECTED.shape == COUNTS.shape == (SPEC.n_rows, SPEC.n_cols)
    assert COUNTS.size == 1023
    assert int((~ABSENT).sum()) == 926
    assert int(ABSENT.sum()) == 97


def test_every_cell_is_drawn_exactly_once(figure):
    """1,023 cells: 926 in the mesh and 97 as absence, in both panels.

    Asserted rather than eyeballed. The mesh carries one quad per cell with the
    absent ones masked, and the absence collection carries one patch per hole,
    so the two must sum to the lattice and the second must equal the mask.
    """
    panels = map_panels(figure)
    assert len(panels) == 2

    for ax in panels:
        mesh = next(c for c in ax.collections if isinstance(c, QuadMesh))
        holes = fields.absence_artist(ax)
        drawn = mesh.get_array()

        assert drawn.size == SPEC.n_cells == 1023
        assert int(np.ma.count_masked(drawn)) == 97
        assert int(drawn.count()) == 926
        assert len(holes.get_paths()) == 97
        assert int(drawn.count()) + len(holes.get_paths()) == 1023


def test_the_absent_cells_drawn_are_the_absent_cells_in_the_data(figure):
    """Not merely the right number of holes, but the right holes."""
    ax = map_panels(figure)[0]
    holes = fields.absence_artist(ax)

    res = SPEC.resolution
    drawn = set()
    for path in holes.get_paths():
        west, south = path.vertices[:, 0].min(), path.vertices[:, 1].min()
        col = int(round((west - SPEC.west) / res))
        row = int(round((SPEC.north - (south + res)) / res))
        drawn.add((row, col))

    expected = {(int(r), int(c)) for r, c in zip(*np.where(ABSENT))}
    assert drawn == expected


def test_both_panels_share_one_geographic_frame(figure):
    """A reader moves between the panels cell by cell, so they must align."""
    extent = geo.lattice_extent(SPEC)
    for ax in map_panels(figure):
        assert ax.get_xlim() == pytest.approx((extent.west, extent.east))
        assert ax.get_ylim() == pytest.approx((extent.south, extent.north))
        assert ax.get_aspect() == pytest.approx(
            1.0 / geo.geographic_aspect(extent.centre_latitude))


def test_the_value_panel_is_clipped_to_the_robust_range(figure):
    """The tails are thin sampling, not methane, so they do not set the scale.

    Median count is 2 soundings in the highest two percent of values and 12 in
    the lowest, against 74 overall. The bar carries arrow caps to say so.
    """
    mesh = next(c for c in map_panels(figure)[0].collections
                if isinstance(c, QuadMesh))
    finite = CORRECTED[~ABSENT]

    assert mesh.norm.vmin > finite.min()
    assert mesh.norm.vmax < finite.max()
    assert mesh.norm.vmin == pytest.approx(np.floor(np.percentile(finite, 2)))


def test_the_panels_do_not_share_a_colour_scale(figure):
    meshes = [next(c for c in ax.collections if isinstance(c, QuadMesh))
              for ax in map_panels(figure)]

    assert len(meshes) == 2
    assert meshes[0].cmap.name != meshes[1].cmap.name


def test_absence_is_named_in_a_legend_with_black_text(figure):
    import matplotlib.colors as mcolors

    legends = [ax.get_legend() for ax in figure.axes if ax.get_legend()]
    assert legends

    texts = {t.get_text() for lg in legends for t in lg.get_texts()}
    assert fields.ABSENT_LABEL in texts
    for lg in legends:
        for text in lg.get_texts():
            assert mcolors.to_rgba(text.get_color()) == (0.0, 0.0, 0.0, 1.0)


def test_there_is_no_background_grid_beyond_the_lattice(figure):
    for ax in figure.axes:
        assert not any(line.get_visible() for line in ax.get_xgridlines())
        assert not any(line.get_visible() for line in ax.get_ygridlines())


def test_every_axis_label_names_its_units_in_parentheses(figure):
    labels = [ax.get_xlabel() for ax in figure.axes if ax.get_xlabel()]

    assert labels
    for label in labels:
        assert "(" in label and ")" in label, label


def test_the_figure_is_at_least_the_venue_minimum_width(figure):
    assert figure.get_figwidth() / style.CM >= style.MIN_WIDTH_CM
