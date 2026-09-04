"""The declared study box and the lattice it produces must be the same object.

This is the guard that could not be written before the decision was taken. A
lattice is built by rounding a declared extent to a whole number of cells, and
a rounded lattice does not in general occupy the extent it was rounded from.
For this grid the rounding used to run in **opposite directions on the two
axes**: 7.8 degrees of longitude is 31.2 cells, rounded down, so the lattice
stopped short of the declared east edge; 8.2 degrees of latitude is 32.8
cells, rounded up, so it ran past the declared south edge.

Two modules then disagreed about where the study area was. `src/grid/cells.py`
filtered land-cover pixels against the lattice; `GridSpec.cell_of` filtered
soundings against the declared box and clipped the overflow into the edge
column. Soundings between 122.55 and 122.6 east were folded into a column they
do not lie in, and soundings between 26.95 and 27.0 north were discarded
although cells existed there.

The config now declares the lattice extent, so the two coincide and `cell_of`
is correct as written. These tests exist so that a change to either the box or
the cell size fails here rather than silently reintroducing the gap.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from src.methane.grid import GridSpec

CONFIG = Path(__file__).resolve().parents[1] / "config" / "sources.yml"

#: Floating point puts the derived south edge at 26.950000000000003 against a
#: declared 26.95. The two are the same number; the comparison needs a
#: tolerance far below a cell, not exact equality.
TOLERANCE = 1e-9


@pytest.fixture(scope="module")
def spec() -> GridSpec:
    config = yaml.safe_load(CONFIG.read_text(encoding="utf-8"))["s5p"]
    box = config["bounding_box"]
    return GridSpec(box["west"], box["south"], box["east"], box["north"],
                    config["grid_resolution_deg"])


def test_the_declared_box_is_exactly_the_lattice_it_produces(spec):
    """Both sides derived, neither hardcoded.

    A change to the box or to the cell size that reintroduces a remainder
    fails here, whatever the new numbers are.
    """
    east = spec.west + spec.n_cols * spec.resolution
    south = spec.north - spec.n_rows * spec.resolution

    assert east == pytest.approx(spec.east, abs=TOLERANCE)
    assert south == pytest.approx(spec.south, abs=TOLERANCE)
    assert spec.west + spec.n_cols * spec.resolution <= spec.east + TOLERANCE
    assert spec.north - spec.n_rows * spec.resolution >= spec.south - TOLERANCE


def test_the_box_is_a_whole_number_of_cells_on_both_axes(spec):
    columns = (spec.east - spec.west) / spec.resolution
    rows = (spec.north - spec.south) / spec.resolution

    assert columns == pytest.approx(round(columns), abs=1e-6)
    assert rows == pytest.approx(round(rows), abs=1e-6)
    assert (spec.n_rows, spec.n_cols) == (33, 31)
    assert spec.n_cells == 1023


def test_the_figure_layer_derives_the_same_extent(spec):
    """The map and the data must not be able to disagree about the edges."""
    from src.figures.geo import lattice_extent

    extent = lattice_extent(spec)

    assert extent.west == pytest.approx(spec.west, abs=TOLERANCE)
    assert extent.east == pytest.approx(spec.east, abs=TOLERANCE)
    assert extent.south == pytest.approx(spec.south, abs=TOLERANCE)
    assert extent.north == pytest.approx(spec.north, abs=TOLERANCE)


def test_cell_of_excludes_rather_than_clips_outside_the_lattice(spec):
    """The clipping path exists but is now unreachable for real coordinates.

    `cell_of` still calls np.clip on the row and column, which is what folded
    122.56 east into column 30 under the old box. With declared and lattice
    coincident, anything the clip would move is already excluded by the mask,
    so the clipped index is never used. These are the three coordinates the
    diagnosis tested.
    """
    for lat, lon in ((27.01, 122.56), (35.19, 122.59), (30.0, 122.5999)):
        _row, _col, inside = spec.cell_of([lat], [lon])
        assert not bool(inside[0]), (lat, lon)

    # And the strip that used to be discarded is now inside, in the last row.
    row, _col, inside = spec.cell_of([26.96], [114.80])
    assert bool(inside[0])
    assert int(row[0]) == spec.n_rows - 1


def test_every_accepted_coordinate_lands_in_a_cell_that_contains_it(spec):
    """The property clipping broke: a sounding belongs to the cell it is in."""
    import numpy as np

    rng = np.random.default_rng(0)
    lat = rng.uniform(spec.south - 0.3, spec.north + 0.3, 4000)
    lon = rng.uniform(spec.west - 0.3, spec.east + 0.3, 4000)

    row, col, inside = spec.cell_of(lat, lon)

    north = spec.north - row[inside] * spec.resolution
    west = spec.west + col[inside] * spec.resolution
    assert np.all(lat[inside] <= north + TOLERANCE)
    assert np.all(lat[inside] > north - spec.resolution - TOLERANCE)
    assert np.all(lon[inside] >= west - TOLERANCE)
    assert np.all(lon[inside] < west + spec.resolution + TOLERANCE)
    assert inside.sum() > 0
