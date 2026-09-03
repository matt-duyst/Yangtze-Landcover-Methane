"""Tests for the land-cover zonal statistics module.

Every synthetic test builds its raster inside ``tmp_path`` and its polygons in
memory, so the suite runs offline on a clone with no data fetched.

The last test is the exception and the important one: it applies the module to
a real GAIA tile and checks it reproduces a value already committed to
``data/processed/urban_area_by_province.csv``. It skips with a message when
``data/raw/gaia/`` is absent, which it will be on a fresh clone, because a test
that cannot run is better than a suite that cannot pass.

Each constraint recorded in notes/decisions.md that this module exists to
enforce has a test here named for it.
"""

from __future__ import annotations

import csv
import math
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin
from shapely.geometry import box

from src.landcover import geometry as geo
from src.landcover import selectors as sel
from src.landcover.zonal import zonal_area

REPO = Path(__file__).resolve().parents[1]


# --------------------------------------------------------------------------
# fixtures
# --------------------------------------------------------------------------

def write_raster(path, array, *, west, north, pixel, nodata=None, dtype="uint8"):
    """Write a north-up EPSG:4326 raster and return its path."""
    height, width = array.shape
    profile = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 1,
        "dtype": dtype,
        "crs": "EPSG:4326",
        "transform": from_origin(west, north, pixel, pixel),
    }
    if nodata is not None:
        profile["nodata"] = nodata
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(array.astype(dtype), 1)
    return path


def analytic_area_km2(north, south, west, east):
    """Exact area of a latitude-longitude box on the authalic sphere."""
    r = geo.AUTHALIC_RADIUS_M
    return (
        r * r
        * math.radians(east - west)
        * (math.sin(math.radians(north)) - math.sin(math.radians(south)))
        / 1e6
    )


# --------------------------------------------------------------------------
# equal-area weighting
# --------------------------------------------------------------------------

def test_equal_area_weighting_matches_the_analytic_box_area(tmp_path):
    """A fully selected raster must equal the closed-form area of its box.

    Tolerance is 1e-9 relative: the method is the closed form, so anything
    larger would mean an arithmetic error rather than an approximation.
    """
    west, north, pixel, n = 100.0, 31.0, 0.01, 100
    raster = write_raster(tmp_path / "all.tif", np.ones((n, n), "uint8"),
                          west=west, north=north, pixel=pixel)
    south, east = north - n * pixel, west + n * pixel
    zones = {"box": box(west, south, east, north)}

    result = zonal_area(raster, zones, sel.in_classes([1]))[0]

    expected = analytic_area_km2(north, south, west, east)
    assert result.pixel_count == n * n
    assert result.area_km2 == pytest.approx(expected, rel=1e-9)


def test_row_areas_grow_as_rows_run_south_from_a_high_latitude():
    """Rows run southward from the top edge, so they move toward the equator."""
    areas = geo.row_pixel_areas_m2(60.0, 0.01, 0.01, 5)
    assert np.all(np.diff(areas) > 0)
    assert areas[-1] > areas[0]


def test_row_areas_are_smaller_nearer_the_pole():
    near_pole = geo.row_pixel_areas_m2(80.0, 0.01, 0.01, 1)[0]
    near_equator = geo.row_pixel_areas_m2(1.0, 0.01, 0.01, 1)[0]
    assert near_pole < near_equator
    assert near_pole == pytest.approx(near_equator * math.cos(math.radians(80.0)),
                                      rel=1e-3)


def test_pixels_are_weighted_not_counted(tmp_path):
    """Two equal pixel counts at different latitudes must give different areas."""
    pixel, n = 0.01, 40
    ones = np.ones((n, n), "uint8")
    low = write_raster(tmp_path / "low.tif", ones, west=100.0, north=5.0, pixel=pixel)
    high = write_raster(tmp_path / "high.tif", ones, west=100.0, north=65.0, pixel=pixel)
    zone_low = {"z": box(100.0, 5.0 - n * pixel, 100.0 + n * pixel, 5.0)}
    zone_high = {"z": box(100.0, 65.0 - n * pixel, 100.0 + n * pixel, 65.0)}

    a = zonal_area(low, zone_low, sel.in_classes([1]))[0]
    b = zonal_area(high, zone_high, sel.in_classes([1]))[0]

    assert a.pixel_count == b.pixel_count
    assert a.area_km2 > b.area_km2 * 2       # cos(60) halves it, and then some


# --------------------------------------------------------------------------
# coverage and the denominator
# --------------------------------------------------------------------------

def test_raster_smaller_than_the_zone_reports_partial_coverage(tmp_path):
    """Anhui's case: the denominator is the intersection, not the polygon."""
    pixel, n = 0.01, 100
    raster = write_raster(tmp_path / "half.tif", np.ones((n, n), "uint8"),
                          west=100.0, north=31.0, pixel=pixel)
    # zone is twice as wide as the raster
    zones = {"wide": box(100.0, 30.0, 102.0, 31.0)}

    result = zonal_area(raster, zones, sel.in_classes([1]))[0]

    assert result.coverage < 1.0
    assert result.coverage == pytest.approx(0.5, rel=0.01)
    assert result.covered_area_km2 < result.zone_area_km2
    # the fraction divides by what was seen, not by the whole zone
    assert result.fraction == pytest.approx(
        result.area_km2 / result.covered_area_km2, rel=1e-12)
    assert result.fraction > result.area_km2 / result.zone_area_km2


def test_full_coverage_reports_one(tmp_path):
    pixel, n = 0.01, 50
    raster = write_raster(tmp_path / "full.tif", np.ones((n, n), "uint8"),
                          west=100.0, north=31.0, pixel=pixel)
    zones = {"z": box(100.1, 30.6, 100.4, 30.9)}       # well inside the raster
    result = zonal_area(raster, zones, sel.in_classes([1]))[0]
    assert result.coverage == pytest.approx(1.0, rel=1e-6)


def test_every_result_carries_a_coverage_fraction(tmp_path):
    pixel, n = 0.01, 30
    raster = write_raster(tmp_path / "r.tif", np.ones((n, n), "uint8"),
                          west=100.0, north=31.0, pixel=pixel)
    zones = {
        "inside": box(100.05, 30.75, 100.2, 30.95),
        "straddling": box(100.2, 30.7, 100.5, 31.2),
        "elsewhere": box(10.0, 10.0, 11.0, 11.0),
    }
    results = zonal_area(raster, zones, sel.in_classes([1]))
    assert len(results) == 3
    for result in results:
        assert hasattr(result, "coverage")
        assert result.coverage is not None
        assert 0.0 <= result.coverage <= 1.0 + 1e-9
        assert "coverage" in result.as_dict()
    disjoint = next(r for r in results if r.zone == "elsewhere")
    assert disjoint.coverage == 0.0
    assert disjoint.area_km2 == 0.0


def test_pixels_outside_the_zone_are_excluded(tmp_path):
    """The whole reason statistics go through the polygon and not the extent."""
    pixel, n = 0.01, 100
    raster = write_raster(tmp_path / "wide.tif", np.ones((n, n), "uint8"),
                          west=100.0, north=31.0, pixel=pixel)
    whole = {"whole": box(100.0, 30.0, 101.0, 31.0)}
    left = {"left": box(100.0, 30.0, 100.5, 31.0)}

    all_pixels = zonal_area(raster, whole, sel.in_classes([1]))[0]
    half_pixels = zonal_area(raster, left, sel.in_classes([1]))[0]

    assert all_pixels.pixel_count == n * n
    assert half_pixels.pixel_count == pytest.approx(n * n / 2, rel=0.02)
    assert half_pixels.area_km2 == pytest.approx(all_pixels.area_km2 / 2, rel=0.02)


# --------------------------------------------------------------------------
# selectors
# --------------------------------------------------------------------------

def stripe_raster(tmp_path):
    """Rows 0..5 hold the values 0..5, ten columns wide."""
    array = np.repeat(np.arange(6, dtype="uint8")[:, None], 10, axis=1)
    return write_raster(tmp_path / "stripes.tif", array,
                        west=100.0, north=31.0, pixel=0.01)


def test_cumulative_and_discrete_selection_on_the_same_fixture(tmp_path):
    raster = stripe_raster(tmp_path)
    zones = {"z": box(100.0, 31.0 - 6 * 0.01, 100.1, 31.0)}

    cumulative = zonal_area(raster, zones, sel.at_least(3))[0]
    discrete = zonal_area(raster, zones, sel.in_classes([1, 2]))[0]
    single = zonal_area(raster, zones, sel.in_classes([5]))[0]

    assert cumulative.pixel_count == 30        # values 3, 4, 5
    assert discrete.pixel_count == 20          # values 1, 2
    assert single.pixel_count == 10
    assert cumulative.selection == "value >= 3"
    assert discrete.selection == "value in {1, 2}"


def test_at_most_mirrors_at_least(tmp_path):
    raster = stripe_raster(tmp_path)
    zones = {"z": box(100.0, 31.0 - 6 * 0.01, 100.1, 31.0)}
    assert zonal_area(raster, zones, sel.at_most(2))[0].pixel_count == 30


def test_in_classes_rejects_an_empty_set():
    with pytest.raises(ValueError):
        sel.in_classes([])


# --------------------------------------------------------------------------
# nodata
# --------------------------------------------------------------------------

def test_absent_nodata_is_not_inferred(tmp_path):
    """The NESDC rasters declare no nodata; nothing may be treated as fill."""
    array = np.zeros((10, 10), "uint8")
    array[0, :] = 1                      # rice
    array[1, :] = 255                    # would be an obvious fill sentinel
    raster = write_raster(tmp_path / "nonodata.tif", array,
                          west=100.0, north=31.0, pixel=0.01, nodata=None)
    with rasterio.open(raster) as src:
        assert src.nodata is None

    zones = {"z": box(100.0, 30.9, 100.1, 31.0)}

    rice = zonal_area(raster, zones, sel.in_classes([1]))[0]
    assert rice.pixel_count == 10        # 255 is not silently swept in

    # and 255 is counted when, and only when, the caller asks for it
    sentinel = zonal_area(raster, zones, sel.in_classes([255]))[0]
    assert sentinel.pixel_count == 10


def test_declared_nodata_is_also_not_applied_behind_the_callers_back(tmp_path):
    """Selection is explicit even when the raster does declare a nodata."""
    array = np.zeros((10, 10), "uint8")
    array[0, :] = 7
    raster = write_raster(tmp_path / "withnodata.tif", array,
                          west=100.0, north=31.0, pixel=0.01, nodata=7)
    zones = {"z": box(100.0, 30.9, 100.1, 31.0)}
    result = zonal_area(raster, zones, sel.in_classes([7]))[0]
    assert result.pixel_count == 10


# --------------------------------------------------------------------------
# tile overlap
# --------------------------------------------------------------------------

def test_clip_bounds_excludes_a_tile_buffer(tmp_path):
    """GAIA ships overlapping tiles; without clipping the overlap is counted twice."""
    pixel, n = 0.01, 100
    raster = write_raster(tmp_path / "buffered.tif", np.ones((n, n), "uint8"),
                          west=100.0, north=31.0, pixel=pixel)
    zones = {"z": box(100.0, 30.0, 101.0, 31.0)}

    unclipped = zonal_area(raster, zones, sel.in_classes([1]))[0]
    clipped = zonal_area(raster, zones, sel.in_classes([1]),
                         clip_bounds=(100.0, 30.0, 100.5, 31.0))[0]

    assert unclipped.pixel_count == n * n
    assert clipped.pixel_count == pytest.approx(n * n / 2, rel=0.02)
    assert clipped.covered_area_km2 < unclipped.covered_area_km2


# --------------------------------------------------------------------------
# regression against committed values
# --------------------------------------------------------------------------

def committed_urban(year, province, boundary="natural_earth"):
    path = REPO / "data" / "processed" / "urban_area_by_province.csv"
    with open(path, newline="") as handle:
        for row in csv.DictReader(handle):
            if (row["year"] == str(year) and row["province"] == province
                    and row["boundary"] == boundary):
                return float(row["urban_area_km2"])
    raise AssertionError(f"no committed value for {province} {year}")


@pytest.mark.parametrize("year,cutoff", [(2000, 23), (2010, 13), (2018, 5)])
def test_reproduces_committed_gaia_values_for_shanghai(year, cutoff):
    """Not synthetic: the module against a real tile, versus a committed number.

    Shanghai lies entirely inside the GAIA tile whose nominal extent is
    120-125E, 30-35N, so one tile settles it without mosaicking. GAIA encodes
    the year of first imperviousness counting downward from the newest year, so
    cumulative extent for a year is value >= 2023 minus that year.
    """
    tile = REPO / "data" / "raw" / "gaia" / "GAIA_1985_2022_120_35.tif"
    if not tile.exists():
        pytest.skip(
            "data/raw/gaia/ is absent, as it is on a fresh clone. Run the GAIA "
            "fetch to enable this regression test; the synthetic tests above "
            "cover the arithmetic."
        )
    zones = geo.load_zones(REPO / "data" / "reference" / "yrd_provinces.geojson")
    shanghai = {"Shanghai": zones["Shanghai"]}

    result = zonal_area(tile, shanghai, sel.at_least(cutoff),
                        clip_bounds=(120.0, 30.0, 125.0, 35.0))[0]

    expected = committed_urban(year, "Shanghai")
    assert result.area_km2 == pytest.approx(expected, rel=0.005)
    assert result.coverage == pytest.approx(1.0, abs=0.01)


# --------------------------------------------------------------------------
# the bounded selector, for a product that counts upward and uses 0 for absence
# --------------------------------------------------------------------------

def test_between_includes_both_ends():
    from src.landcover import between

    values = np.array([0, 1, 2, 35, 36, 37, 255], dtype="uint8")
    got = between(1, 36)(values)
    assert got.tolist() == [False, True, True, True, True, False, False]


def test_between_describes_itself():
    from src.landcover import between

    assert between(1, 36).description == "1 <= value <= 36"


def test_between_refuses_an_inverted_range():
    from src.landcover import between

    with pytest.raises(ValueError, match="low <= high"):
        between(36, 1)


def test_between_is_not_at_most_because_zero_means_absence():
    """at_most(36) would count every non-impervious pixel as impervious."""
    from src.landcover import at_most, between

    values = np.array([0, 0, 0, 5, 36, 37], dtype="uint8")
    assert int(between(1, 36)(values).sum()) == 2
    assert int(at_most(36)(values).sum()) == 5


def test_between_is_not_at_least_which_would_invert_the_history():
    """The failure the selector exists to prevent, stated as a test.

    GISA counts upward from 1972, so extent as of 2018 is 1 to 36. Applying
    GAIA's downward rule selects only what was built in 2018 and 2019.
    """
    from src.landcover import at_least, between

    values = np.array([0, 1, 18, 30, 36, 37], dtype="uint8")
    extent = between(1, 36)(values)
    inverted = at_least(36)(values)
    assert int(extent.sum()) == 4, "everything built by 2018"
    assert int(inverted.sum()) == 2, "only the newest two years"
    assert not (extent & inverted).all()
