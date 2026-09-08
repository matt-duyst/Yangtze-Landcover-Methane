"""Tests for drawing a per-cell value, and for drawing where there is none.

Offline, on constructed grids. The composite is read only where a test says so
and nothing is written.

The property that carries the weight is that absence is drawn, and drawn as
its own thing. 97 of 1,023 cells carry no sounding, and they are not one shape:
a 47-cell block over southern Zhejiang and eight isolated single cells, all
needing the same treatment. A value grid that quietly rendered a hole as a
number would be the same class of error as a composite that clipped soundings
into the wrong cell.
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # noqa: E402

import matplotlib.pyplot as plt
import numpy as np
import pytest
from matplotlib.collections import PatchCollection, QuadMesh
from matplotlib.colors import Normalize

from src.figures import fields, geo, style
from src.methane.grid import GridSpec

#: 4 rows by 5 columns, so a transposed value grid fails loudly.
SMALL = GridSpec(west=0.0, south=0.0, east=1.25, north=1.0, resolution=0.25)


@pytest.fixture
def axes():
    fig, ax = plt.subplots()
    yield ax
    plt.close(fig)


def test_the_ramp_is_monotone_in_luminance():
    """A greyscale reader must be able to order the values at all.

    A ramp is not a set of discrete colours, so a minimum pairwise gap says
    nothing: adjacent samples are arbitrarily close by construction. Monotone
    luminance over a wide enough range is the property that matters.
    """
    luminance = fields.ramp_luminances()

    assert np.all(np.diff(luminance) > -1e-6)
    assert luminance.max() - luminance.min() > 0.5


def test_the_ramp_leaves_room_for_absence():
    """Absence must not collide with the light end of the scale.

    Full batlow reaches 0.85 and absence is near-white at 0.97, a gap of 0.11
    against the project's 0.15 convention. Truncating the ramp is what buys the
    gap, so this pins the reason the truncation exists.
    """
    import matplotlib.colors as mcolors

    absent = mcolors.to_rgb(fields.ABSENT_FILL)
    absent_luminance = 0.2126 * absent[0] + 0.7152 * absent[1] + 0.0722 * absent[2]

    for name in (style.SEQUENTIAL, fields.COUNT_RAMP):
        top = fields.ramp_luminances(fields.field_cmap(name)).max()
        assert absent_luminance - top >= 0.15, name


def test_the_two_panels_use_different_ramps():
    """A colour must not mean one thing in panel (a) and another in panel (b).

    The high-methane cells and the high-count cells are not the same cells, so
    a shared ramp would invite a reading that is not merely unsupported but
    wrong.
    """
    assert fields.COUNT_RAMP != style.SEQUENTIAL

    a = fields.ramp_luminances(fields.field_cmap(style.SEQUENTIAL))
    b = fields.ramp_luminances(fields.field_cmap(fields.COUNT_RAMP))
    assert not np.allclose(a, b, atol=0.02)


def test_absent_cells_are_drawn_rather_than_left_to_the_background(axes):
    values = np.arange(20, dtype=float).reshape(4, 5)
    absent = np.zeros_like(values, dtype=bool)
    absent[0, 0] = absent[3, 4] = True  # opposite corners

    fields.draw_lattice_field(axes, values, SMALL, cmap=fields.field_cmap(),
                              norm=Normalize(0, 19), absent=absent)

    patch = fields.absence_artist(axes)
    assert patch is not None
    assert len(patch.get_paths()) == 2


def test_absent_cells_carry_an_outline_so_a_single_cell_still_reads(axes):
    """A fill alone loses the eight singletons; the outline is what saves them."""
    values = np.zeros((4, 5))
    absent = np.zeros_like(values, dtype=bool)
    absent[1, 2] = True

    fields.draw_lattice_field(axes, values, SMALL, cmap=fields.field_cmap(),
                              norm=Normalize(0, 1), absent=absent)

    patch = fields.absence_artist(axes)
    assert float(patch.get_linewidth()[0]) > 0


def test_no_absence_means_no_absence_artist(axes):
    values = np.zeros((4, 5))

    fields.draw_lattice_field(axes, values, SMALL, cmap=fields.field_cmap(),
                              norm=Normalize(0, 1),
                              absent=np.zeros_like(values, dtype=bool))

    assert fields.absence_artist(axes) is None


def test_a_non_finite_value_is_treated_as_absent_when_no_mask_is_given(axes):
    values = np.zeros((4, 5))
    values[2, 3] = np.nan

    fields.draw_lattice_field(axes, values, SMALL, cmap=fields.field_cmap(),
                              norm=Normalize(0, 1))

    patch = fields.absence_artist(axes)
    assert len(patch.get_paths()) == 1


def test_a_mask_of_the_wrong_shape_is_refused(axes):
    with pytest.raises(ValueError, match="absence mask is"):
        fields.draw_lattice_field(axes, np.zeros((4, 5)), SMALL,
                                  cmap=fields.field_cmap(),
                                  norm=Normalize(0, 1),
                                  absent=np.zeros((3, 3), dtype=bool))


def test_the_field_is_drawn_north_up(axes):
    """Row 0 is the northernmost, matching the composite rasters."""
    values = np.zeros((4, 5))
    absent = np.zeros_like(values, dtype=bool)
    absent[0, 0] = True

    fields.draw_lattice_field(axes, values, SMALL, cmap=fields.field_cmap(),
                              norm=Normalize(0, 1), absent=absent)

    patch = fields.absence_artist(axes)
    corners = patch.get_paths()[0].vertices
    assert corners[:, 1].max() == pytest.approx(SMALL.north)


def test_the_count_scale_is_classed_rather_than_continuous():
    """The literature masks below a sampling threshold rather than shading it.

    A linear ramp would put the median at a fifth of the range and render every
    sparse cell alike, which is where the finding is.
    """
    norm = fields.count_norm()

    assert list(fields.COUNT_EDGES[:3]) == [1, 4, 11]
    assert norm(1) != norm(4)
    assert norm(4) == norm(10)      # one class
    assert norm(100) != norm(316)


def test_the_classes_cover_the_observed_range():
    import rasterio

    with rasterio.open("data/processed/methane_composite_2018.tif") as src:
        counts = src.read(3)
    observed = counts[counts > 0]

    assert observed.min() >= fields.COUNT_EDGES[0]
    assert observed.max() < fields.COUNT_EDGES[-1]


def test_the_absence_key_matches_what_is_drawn():
    handle = fields.absence_handle()

    assert handle.get_facecolor()[:3] == pytest.approx(
        matplotlib.colors.to_rgb(fields.ABSENT_FILL))
    assert handle.get_label() == fields.ABSENT_LABEL
