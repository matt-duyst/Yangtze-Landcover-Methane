"""Environment verification.

Every test builds what it needs inside ``tmp_path``. Nothing here reads
``data/``, the repository, or any other location on disk, so the suite runs
offline and a failure means the environment is wrong rather than the data.

These exist because ``pip install`` reporting success is not evidence the
stack works: h5netcdf installs and imports without h5py and then fails at
the point of opening a file, and a broken PROJ data path produces plausible
wrong areas rather than an error.
"""

from __future__ import annotations

import importlib

import numpy as np
import pytest

#: Packages imported directly by this project, as import names.
DIRECT_IMPORTS = [
    "numpy", "pandas",
    "rasterio", "geopandas", "shapely", "pyproj", "fiona",
    "xarray", "rioxarray", "netCDF4", "h5netcdf", "h5py",
    "sklearn", "scipy",
    "matplotlib",
    "pytest",
    "yaml", "requests", "tqdm",
]

#: Shanghai, People's Square. Inside UTM zone 51N, which covers the YRD.
LON, LAT = 121.4737, 31.2304

#: A one-degree box at this latitude, projected to UTM 51N, in square metres.
#: A silent identity transform returns roughly 1 instead, which is what this
#: number is here to catch.
BOX_AREA_KM2 = 10_540.0

FILL = -9999.0


@pytest.mark.parametrize("module", DIRECT_IMPORTS)
def test_direct_imports_are_available(module):
    assert importlib.import_module(module) is not None


def test_geotiff_round_trips(tmp_path):
    import rasterio
    from rasterio.transform import from_origin

    values = np.arange(64 * 64, dtype="uint8").reshape(64, 64)
    path = tmp_path / "probe.tif"
    transform = from_origin(120.0, 32.0, 0.001, 0.001)
    with rasterio.open(path, "w", driver="GTiff", height=64, width=64,
                       count=1, dtype="uint8", crs="EPSG:4326",
                       transform=transform) as dst:
        dst.write(values, 1)

    with rasterio.open(path) as src:
        assert src.crs.to_epsg() == 4326
        assert src.bounds.left == pytest.approx(120.0)
        assert src.bounds.top == pytest.approx(32.0)
        assert src.bounds.right == pytest.approx(120.064)
        assert src.bounds.bottom == pytest.approx(31.936)
        assert np.array_equal(src.read(1), values)


def test_geojson_round_trips(tmp_path):
    import geopandas as gpd
    from shapely.geometry import Point, Polygon

    path = tmp_path / "probe.geojson"
    frame = gpd.GeoDataFrame(
        {"name": ["point", "box"]},
        geometry=[Point(LON, LAT),
                  Polygon([(120, 31), (121, 31), (121, 32), (120, 32)])],
        crs="EPSG:4326",
    )
    frame.to_file(path, driver="GeoJSON")

    back = gpd.read_file(path)
    assert len(back) == 2
    assert back.crs.to_epsg() == 4326
    assert sorted(back.geom_type) == ["Point", "Polygon"]
    assert list(back["name"]) == ["point", "box"]


def _write_grouped_netcdf(path):
    """A TROPOMI-shaped file: root, PRODUCT, and PRODUCT/SUPPORT_DATA."""
    import netCDF4

    values = np.arange(12, dtype="float32").reshape(4, 3) + 1800.0
    values[0, 0] = FILL
    with netCDF4.Dataset(path, "w", format="NETCDF4") as ds:
        ds.title = "synthetic TROPOMI-like probe"
        product = ds.createGroup("PRODUCT")
        product.createDimension("scanline", 4)
        product.createDimension("ground_pixel", 3)
        variable = product.createVariable(
            "methane_mixing_ratio", "f4",
            ("scanline", "ground_pixel"), fill_value=FILL)
        variable.units = "ppb"
        variable[:, :] = values
        support = product.createGroup("SUPPORT_DATA")
        altitude = support.createVariable(
            "surface_altitude", "f4", ("scanline", "ground_pixel"))
        altitude.units = "m"
        altitude[:, :] = np.full((4, 3), 12.5, dtype="float32")
    return values


def _assert_product_group_round_trips(path, engine, expected):
    import xarray as xr

    with xr.open_dataset(path, engine=engine, group="PRODUCT") as ds:
        variable = ds["methane_mixing_ratio"]
        assert dict(ds.sizes) == {"scanline": 4, "ground_pixel": 3}
        assert variable.dtype == np.float32
        assert variable.attrs["units"] == "ppb"
        seen = variable.values
        # The fill cell is masked to NaN; every other cell must survive intact.
        assert np.isnan(seen[0, 0])
        assert np.array_equal(seen[1:], expected[1:])

    with xr.open_dataset(path, engine=engine, group="PRODUCT",
                         mask_and_scale=False) as raw:
        assert raw["methane_mixing_ratio"].values[0, 0] == pytest.approx(FILL)


def test_grouped_netcdf_round_trips_via_netcdf4(tmp_path):
    path = tmp_path / "tropomi_like.nc"
    expected = _write_grouped_netcdf(path)
    _assert_product_group_round_trips(path, "netcdf4", expected)


def test_grouped_netcdf_round_trips_via_h5netcdf(tmp_path):
    path = tmp_path / "tropomi_like.nc"
    expected = _write_grouped_netcdf(path)
    _assert_product_group_round_trips(path, "h5netcdf", expected)


def test_h5py_sees_the_group_hierarchy(tmp_path):
    import h5py

    path = tmp_path / "tropomi_like.nc"
    _write_grouped_netcdf(path)
    with h5py.File(path, "r") as handle:
        assert isinstance(handle["PRODUCT"], h5py.Group)
        assert isinstance(handle["PRODUCT/SUPPORT_DATA"], h5py.Group)
        assert handle["PRODUCT/methane_mixing_ratio"].shape == (4, 3)
        assert handle["PRODUCT/SUPPORT_DATA/surface_altitude"].shape == (4, 3)


def test_pyproj_round_trips_a_coordinate():
    from pyproj import Transformer

    forward = Transformer.from_crs("EPSG:4326", "EPSG:32651", always_xy=True)
    inverse = Transformer.from_crs("EPSG:32651", "EPSG:4326", always_xy=True)
    easting, northing = forward.transform(LON, LAT)
    # Sanity on magnitude before the round trip: UTM eastings are metres.
    assert 100_000 < easting < 900_000
    assert 3_000_000 < northing < 4_000_000

    lon_back, lat_back = inverse.transform(easting, northing)
    assert lon_back == pytest.approx(LON, abs=1e-6)
    assert lat_back == pytest.approx(LAT, abs=1e-6)


def test_projected_area_is_not_an_identity_transform():
    """A one-degree box must come back in square metres, not square degrees."""
    import geopandas as gpd
    from shapely.geometry import box

    boxes = gpd.GeoSeries([box(120, 31, 121, 32)], crs="EPSG:4326")
    area_km2 = boxes.to_crs("EPSG:32651").area.iloc[0] / 1e6
    assert area_km2 == pytest.approx(BOX_AREA_KM2, rel=0.01)
