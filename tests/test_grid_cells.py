"""Tests for the analysis-grid join.

Offline throughout. Rasters and province polygons are built in ``tmp_path`` with
geometry chosen so the right answer is known before the code runs.

The cases that carry the weight are the ones the recorded constraints exist for:
that a fraction divides by what the raster assessed rather than by the cell,
that an unmasked rice raster would be wrong and the mask fixes it, that a cell
straddling two provinces is attributed by area share rather than to a winner,
and that a cell with no methane cannot be built into a row at all.
"""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

from src.grid import cells as gc
from src.grid.cells import CellFraction, CellRow, UnobservedCell
from src.landcover import at_least, in_classes, zonal_area
from src.methane.grid import GridSpec

#: Two cells side by side, each half a degree, so hand-checking is easy.
TOY = GridSpec(west=0.0, south=0.0, east=1.0, north=0.5, resolution=0.5)


def write(path, array, *, west, north, pixel, dtype="uint8", nodata=None):
    height, width = array.shape
    profile = dict(driver="GTiff", height=height, width=width, count=1,
                   dtype=dtype, crs="EPSG:4326",
                   transform=from_origin(west, north, pixel, pixel))
    if nodata is not None:
        profile["nodata"] = nodata
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(array.astype(dtype), 1)
    return path


def only(fractions, row=0, col=0):
    return fractions[row][col]


# --------------------------------------------------------------------------
# the denominator
# --------------------------------------------------------------------------

def test_a_cell_wholly_covered_gives_the_expected_fraction(tmp_path):
    """Left half of the cell is rice, so the fraction is one half."""
    n = 40
    a = np.zeros((n, n), "uint8"); a[:, : n // 2] = 1
    raster = write(tmp_path / "r.tif", a, west=0.0, north=0.5, pixel=0.5 / n)
    got = only(gc.fraction_over_grid([raster], TOY, in_classes([1]),
                                     mask_geometry=None))
    assert got.coverage == pytest.approx(1.0, rel=1e-6)
    assert got.fraction == pytest.approx(0.5, rel=1e-6)


def test_a_raster_covering_part_of_the_cell_divides_by_what_it_assessed(tmp_path):
    """Anhui's case: the denominator is the intersection, not the cell.

    The raster is 0.25 degrees wide and the full 0.5 tall, so it assesses the
    west half of the cell: 80 rows by 40 columns at 0.00625 degrees.
    """
    pixel = 0.5 / 80
    a = np.ones((80, 40), "uint8")          # all rice, over the west half only
    raster = write(tmp_path / "r.tif", a, west=0.0, north=0.5, pixel=pixel)
    got = only(gc.fraction_over_grid([raster], TOY, in_classes([1]),
                                     mask_geometry=None))
    assert got.coverage == pytest.approx(0.5, rel=0.02), "half the cell assessed"
    assert got.fraction == pytest.approx(1.0, rel=1e-6), \
        "all of what was assessed is rice, so the fraction is 1, not 0.5"
    assert got.assessed_km2 < got.cell_km2


def test_nothing_assessed_gives_a_none_fraction_not_a_zero(tmp_path):
    a = np.ones((4, 4), "uint8")
    raster = write(tmp_path / "r.tif", a, west=50.0, north=50.0, pixel=0.1)
    got = only(gc.fraction_over_grid([raster], TOY, in_classes([1]),
                                     mask_geometry=None))
    assert got.assessed_km2 == 0.0
    assert got.fraction is None, "unassessed is not the same as zero rice"
    assert got.coverage == 0.0


# --------------------------------------------------------------------------
# the province mask
# --------------------------------------------------------------------------

def test_masking_by_province_changes_the_answer(tmp_path):
    """The rice rasters' zero means both non-rice and out-of-province."""
    n = 40
    a = np.zeros((n, n), "uint8"); a[:, : n // 2] = 1   # rice in the west half
    raster = write(tmp_path / "r.tif", a, west=0.0, north=0.5, pixel=0.5 / n)
    province = box(0.0, 0.0, 0.25, 0.5)                # only the west half

    unmasked = only(gc.fraction_over_grid([raster], TOY, in_classes([1]),
                                          mask_geometry=None))
    masked = only(gc.fraction_over_grid([raster], TOY, in_classes([1]),
                                        mask_geometry=province))
    assert unmasked.fraction == pytest.approx(0.5, rel=1e-6)
    assert masked.fraction == pytest.approx(1.0, rel=1e-6)
    assert masked.coverage == pytest.approx(0.5, rel=0.02)


def test_pixels_outside_the_mask_are_not_assessed(tmp_path):
    n = 20
    a = np.ones((n, n), "uint8")
    raster = write(tmp_path / "r.tif", a, west=0.0, north=0.5, pixel=0.5 / n)
    half = only(gc.fraction_over_grid([raster], TOY, in_classes([1]),
                                      mask_geometry=box(0.0, 0.0, 0.25, 0.5)))
    whole = only(gc.fraction_over_grid([raster], TOY, in_classes([1]),
                                       mask_geometry=None))
    assert half.assessed_km2 == pytest.approx(whole.assessed_km2 / 2, rel=0.03)


# --------------------------------------------------------------------------
# selectors
# --------------------------------------------------------------------------

def test_cumulative_and_class_selection_on_one_fixture(tmp_path):
    """GAIA needs value >= k; rice needs membership. Same raster, both work."""
    n = 40
    a = np.zeros((n, n), "uint8")
    a[: n // 4, :] = 1
    a[n // 4: n // 2, :] = 2
    a[n // 2: 3 * n // 4, :] = 7
    raster = write(tmp_path / "r.tif", a, west=0.0, north=0.5, pixel=0.5 / n)

    cumulative = only(gc.fraction_over_grid([raster], TOY, at_least(5),
                                            mask_geometry=None))
    single = only(gc.fraction_over_grid([raster], TOY, in_classes([1]),
                                        mask_geometry=None))
    combined = only(gc.fraction_over_grid([raster], TOY, in_classes([1, 2]),
                                          mask_geometry=None))
    assert cumulative.fraction == pytest.approx(0.25, abs=0.01)
    assert single.fraction == pytest.approx(0.25, abs=0.01)
    assert combined.fraction == pytest.approx(0.50, abs=0.01)
    assert combined.fraction > single.fraction


def test_several_rasters_accumulate_before_dividing(tmp_path):
    """Two half-cell rasters must give the same answer as one whole-cell one."""
    pixel = 0.5 / 80                        # each raster is a full-height half
    west = write(tmp_path / "w.tif", np.ones((80, 40), "uint8"),
                 west=0.0, north=0.5, pixel=pixel)
    east = write(tmp_path / "e.tif", np.zeros((80, 40), "uint8"),
                 west=0.25, north=0.5, pixel=pixel)
    got = only(gc.fraction_over_grid([west, east], TOY, in_classes([1]),
                                     mask_geometry=None))
    assert got.coverage == pytest.approx(1.0, rel=0.02)
    assert got.fraction == pytest.approx(0.5, rel=0.02), \
        "one raster all rice and one all not, assessed equally, gives one half"


# --------------------------------------------------------------------------
# province attribution
# --------------------------------------------------------------------------

def test_a_cell_straddling_two_provinces_is_split_by_area():
    provinces = {"West": box(0.0, 0.0, 0.25, 0.5), "East": box(0.25, 0.0, 0.5, 0.5)}
    shares = gc.province_shares(TOY, provinces)[0][0]
    assert set(shares) == {"West", "East"}
    assert shares["West"] == pytest.approx(0.5, rel=0.02)
    assert shares["East"] == pytest.approx(0.5, rel=0.02)
    assert sum(shares.values()) == pytest.approx(1.0, rel=0.02)


def test_a_cell_partly_outside_every_province_reports_the_remainder():
    provinces = {"West": box(0.0, 0.0, 0.125, 0.5)}
    shares = gc.province_shares(TOY, provinces)[0][0]
    assert shares["West"] == pytest.approx(0.25, rel=0.02)
    row = CellRow(0, 0, 0.25, 0.25, 10, 1900.0, 1890.0,
                  CellFraction(0, 1, 1), CellFraction(0, 1, 1),
                  CellFraction(0, 1, 1), shares)
    assert row.province_total == pytest.approx(0.25, rel=0.02)
    assert row.outside_provinces == pytest.approx(0.75, rel=0.02)


def test_a_cell_entirely_outside_every_province_has_no_shares():
    shares = gc.province_shares(TOY, {"Far": box(40.0, 40.0, 41.0, 41.0)})[0][0]
    assert shares == {}
    row = CellRow(0, 0, 0.25, 0.25, 5, 1900.0, 1890.0,
                  CellFraction(0, 1, 1), CellFraction(0, 1, 1),
                  CellFraction(0, 1, 1), shares)
    assert row.outside_provinces == pytest.approx(1.0)


# --------------------------------------------------------------------------
# the exclusion, enforced by the type
# --------------------------------------------------------------------------

def test_a_cell_with_no_soundings_cannot_be_constructed():
    """The 96 uncovered cells are excluded structurally, not by a later filter."""
    empty = CellFraction(0.0, 1.0, 1.0)
    with pytest.raises(UnobservedCell, match="not interpolated"):
        CellRow(0, 0, 31.0, 118.0, 0, float("nan"), float("nan"),
                empty, empty, empty, {})


def test_a_cell_with_soundings_constructs_and_serialises():
    row = CellRow(3, 4, 31.0, 118.0, 42, 1900.0, 1888.0,
                  CellFraction(2.0, 10.0, 10.0),
                  CellFraction(1.0, 8.0, 10.0),
                  CellFraction(3.0, 8.0, 10.0),
                  {"Anhui": 0.6, "Jiangsu": 0.3})
    assert row.impervious.fraction == pytest.approx(0.2)
    assert row.rice_single.fraction == pytest.approx(0.125)
    assert row.rice_combined.fraction == pytest.approx(0.375)
    assert row.rice_single.coverage == pytest.approx(0.8)
    d = row.as_dict()
    assert d["sounding_count"] == 42
    assert d["share_anhui"] == pytest.approx(0.6)
    assert d["province_share_outside"] == pytest.approx(0.1)


def test_cell_areas_shrink_toward_the_pole():
    spec = GridSpec(0.0, 0.0, 1.0, 60.0, 0.25)
    areas = gc.cell_areas_m2(spec)
    assert areas[0, 0] < areas[-1, 0]
    assert areas[0, 0] == areas[0, 1], "cells in one row have equal area"


# --------------------------------------------------------------------------
# the lattice is not always the declared box
# --------------------------------------------------------------------------

#: The real study grid. Its width is 31.2 cells, which GridSpec rounds to 31.
STUDY = GridSpec(114.8, 27.0, 122.6, 35.2, 0.25)


def test_the_lattice_stops_short_of_a_box_that_is_not_a_whole_number_of_cells():
    east, south = gc.lattice_edges(STUDY)
    assert STUDY.shape == (33, 31)
    assert east == pytest.approx(122.55), "31 cells from 114.8, not 122.6"
    assert south == pytest.approx(26.95), "33 cells down from 35.2, not 27.0"
    assert east < STUDY.east and south < STUDY.south


def test_pixels_beyond_the_lattice_are_dropped_not_folded_into_the_edge_cell(tmp_path):
    """A pixel in the 0.05 degrees the grid does not reach belongs to no cell."""
    pixel = 0.05
    a = np.ones((4, 4), "uint8")            # 122.5 to 122.7, straddling the edge
    raster = write(tmp_path / "edge.tif", a, west=122.5, north=35.0, pixel=pixel)
    got = gc.fraction_over_grid([raster], STUDY, in_classes([1]),
                                mask_geometry=None)                 # no IndexError
    edge = got[0][30]
    assert edge.selected_km2 > 0, "the pixel at 122.525 is inside the last column"
    # One of the four columns of pixels lies west of 122.55; three lie east.
    whole = only(gc.fraction_over_grid(
        [write(tmp_path / "in.tif", np.ones((4, 1), "uint8"),
               west=122.5, north=35.0, pixel=pixel)],
        STUDY, in_classes([1]), mask_geometry=None), row=0, col=30)
    assert edge.assessed_km2 == pytest.approx(whole.assessed_km2, rel=1e-9), \
        "the three columns past 122.55 must not be folded into column 30"


# --------------------------------------------------------------------------
# overlapping per-province rasters
# --------------------------------------------------------------------------

def test_a_union_mask_over_overlapping_rasters_assesses_the_overlap_twice(tmp_path):
    """The rice product ships one file per province and the boxes overlap."""
    n, pixel = 40, 0.5 / 40
    west = write(tmp_path / "west.tif", np.ones((n, n), "uint8"),
                 west=0.0, north=0.5, pixel=pixel)
    east = write(tmp_path / "east.tif", np.ones((n, n), "uint8"),
                 west=0.0, north=0.5, pixel=pixel)     # same footprint: full overlap
    union = box(0.0, 0.0, 0.5, 0.5)
    doubled = only(gc.fraction_over_grid([west, east], TOY, in_classes([1]),
                                         mask_geometry=union))
    assert doubled.coverage == pytest.approx(2.0, rel=0.02), \
        "a union mask counts the shared ground once per file"


def test_a_per_raster_mask_keeps_the_overlap_counted_once(tmp_path):
    """Each file masked by its own province, as the rice build does."""
    n, pixel = 40, 0.5 / 40
    west = write(tmp_path / "west.tif", np.ones((n, n), "uint8"),
                 west=0.0, north=0.5, pixel=pixel)
    east = write(tmp_path / "east.tif", np.zeros((n, n), "uint8"),
                 west=0.0, north=0.5, pixel=pixel)
    own = {"west.tif": box(0.0, 0.0, 0.25, 0.5), "east.tif": box(0.25, 0.0, 0.5, 0.5)}
    got = only(gc.fraction_over_grid([west, east], TOY, in_classes([1]),
                                     mask_geometry=lambda p: own[Path(p).name]))
    assert got.coverage == pytest.approx(1.0, rel=0.02), "each half assessed once"
    assert got.fraction == pytest.approx(0.5, rel=0.02), \
        "the west file is all rice inside its own province, the east file none"


# --------------------------------------------------------------------------
# agreement with the older, tested path
# --------------------------------------------------------------------------

def test_grid_totals_match_the_zonal_path_on_the_same_raster(tmp_path):
    """Two independent aggregations of one raster must give one answer.

    ``src.landcover.zonal_area`` rasterises the zone polygon; ``src.grid``
    bins by arithmetic and sums the cells afterwards. They share the row-area
    weighting and nothing else, so agreement is a real check on the binning.
    On the 2018 rice rasters the two agree to about 1e-11 relative.
    """
    n, pixel = 60, 0.5 / 60
    a = np.zeros((n, n), "uint8")
    a[::3, :] = 1                                   # a pattern, not a block
    a[:, ::4] = 1
    raster = write(tmp_path / "r.tif", a, west=0.0, north=0.5, pixel=pixel)
    zone = box(0.05, 0.05, 0.95, 0.45)              # cuts across both cells

    selected, _ = gc.accumulate_fraction(raster, TOY, in_classes([1]),
                                         mask_geometry=zone)
    grid_km2 = selected.sum() / 1e6
    zonal_km2 = zonal_area(raster, {"z": zone}, in_classes([1]))[0].area_km2
    assert grid_km2 == pytest.approx(zonal_km2, rel=1e-9)
    assert grid_km2 > 0
