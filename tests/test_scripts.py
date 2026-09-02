"""Tests for the script entry points.

These cover wiring, not arithmetic: argument handling, the output schema, the
row count, and that comparison mode writes nothing. The arithmetic underneath
is covered by tests/test_landcover.py against analytically known values.

Everything is synthetic and lives in ``tmp_path``. The scripts are loaded by
path because ``scripts/`` is deliberately not a package: it holds entry points,
not importable logic.
"""

from __future__ import annotations

import csv
import importlib.util
import json
from pathlib import Path

import numpy as np
import pytest
import rasterio
import xarray as xr
from rasterio.transform import from_origin

REPO = Path(__file__).resolve().parents[1]


def load_script(name):
    path = REPO / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"_script_{name}", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


urban = load_script("compute_urban_areas")
rice = load_script("compute_rice_areas")


# --------------------------------------------------------------------------
# shared fixtures
# --------------------------------------------------------------------------

def write_zones(path, boxes, name_field="name"):
    features = [
        {"type": "Feature",
         "properties": {name_field: name},
         "geometry": {"type": "Polygon", "coordinates": [[
             [w, s], [e, s], [e, n], [w, n], [w, s]]]}}
        for name, (w, s, e, n) in boxes.items()
    ]
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}))
    return path


ALL_FOUR = {
    "Shanghai": (120.10, 30.10, 120.30, 30.30),
    "Zhejiang": (120.40, 30.10, 120.60, 30.30),
    "Anhui": (120.10, 30.40, 120.30, 30.60),
    "Jiangsu": (120.40, 30.40, 120.60, 30.60),
}


# --------------------------------------------------------------------------
# compute_urban_areas
# --------------------------------------------------------------------------

def make_gaia_tile(directory, lon=120, lat=35, value=5, size=200):
    """A tile named as GAIA names them, filled with one value."""
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / f"GAIA_1985_2022_{lon}_{lat}.tif"
    pixel = 5.0 / size
    with rasterio.open(
        path, "w", driver="GTiff", height=size, width=size, count=1,
        dtype="int16", crs="EPSG:4326",
        transform=from_origin(float(lon), float(lat), pixel, pixel),
    ) as dst:
        dst.write(np.full((size, size), value, dtype="int16"), 1)
    return path


def test_tile_clip_bounds_comes_from_the_filename(tmp_path):
    path = make_gaia_tile(tmp_path / "gaia", lon=115, lat=40)
    assert urban.tile_clip_bounds(path) == (115.0, 35.0, 120.0, 40.0)


def test_urban_emits_the_expected_schema_and_row_count(tmp_path, capsys):
    gaia = tmp_path / "gaia"
    make_gaia_tile(gaia)
    zones = write_zones(tmp_path / "z.geojson", ALL_FOUR)
    out = tmp_path / "urban.csv"

    code = urban.main(["--gaia", str(gaia), "--zones", str(zones),
                       "--out", str(out), "--write"])
    assert code == 0
    rows = list(csv.DictReader(open(out, newline="")))
    # 37 years x 4 provinces, and no GADM rows because none were committed
    assert len(rows) == 37 * 4
    assert set(rows[0]) == set(urban.FIELDS)
    assert {r["boundary"] for r in rows} == {"natural_earth"}
    assert {r["source"] for r in rows} == {"GAIA"}


def test_urban_comparison_mode_writes_nothing(tmp_path):
    gaia = tmp_path / "gaia"
    make_gaia_tile(gaia)
    zones = write_zones(tmp_path / "z.geojson", ALL_FOUR)
    out = tmp_path / "urban.csv"

    assert urban.main(["--gaia", str(gaia), "--zones", str(zones),
                       "--out", str(out)]) == 0
    assert not out.exists()


def test_urban_refuses_to_write_when_a_row_differs(tmp_path, capsys):
    gaia = tmp_path / "gaia"
    make_gaia_tile(gaia, value=5)
    zones = write_zones(tmp_path / "z.geojson", ALL_FOUR)
    out = tmp_path / "urban.csv"
    urban.main(["--gaia", str(gaia), "--zones", str(zones), "--out", str(out), "--write"])
    before = out.read_text()

    # a committed file that disagrees
    rows = list(csv.DictReader(open(out, newline="")))
    rows[0]["urban_area_km2"] = "999999.9"
    with open(out, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=urban.FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    tampered = out.read_text()

    code = urban.main(["--gaia", str(gaia), "--zones", str(zones),
                       "--out", str(out), "--write"])
    assert code == 1
    assert out.read_text() == tampered != before
    assert "refusing to write" in capsys.readouterr().out


def test_urban_carries_gadm_rows_forward_and_says_so(tmp_path, capsys):
    gaia = tmp_path / "gaia"
    make_gaia_tile(gaia)
    zones = write_zones(tmp_path / "z.geojson", ALL_FOUR)
    out = tmp_path / "urban.csv"
    with open(out, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=urban.FIELDS)
        writer.writeheader()
        writer.writerow({"source": "GAIA", "year": "2000", "province": "Shanghai",
                         "urban_area_km2": "1131.5", "boundary": "gadm",
                         "thesis_urban_km2": "1211"})

    urban.main(["--gaia", str(gaia), "--zones", str(zones), "--out", str(out)])
    printed = capsys.readouterr().out
    assert "carried forward unchanged, NOT regenerated" in printed
    assert "licence forbids redistribution" in printed


def test_urban_reports_a_missing_tile_directory(tmp_path):
    zones = write_zones(tmp_path / "z.geojson", ALL_FOUR)
    with pytest.raises(SystemExit):
        urban.main(["--gaia", str(tmp_path / "absent"), "--zones", str(zones),
                    "--out", str(tmp_path / "o.csv")])


# --------------------------------------------------------------------------
# compute_rice_areas
# --------------------------------------------------------------------------

def make_glorice(directory, year, hectares=100.0, size=40):
    directory.mkdir(parents=True, exist_ok=True)
    pixel = 0.05
    lon = 120.0 + np.arange(size) * pixel
    lat = 31.0 - np.arange(size) * pixel
    data = np.full((size, size), hectares, dtype="float32")
    dataset = xr.Dataset({"area": (("lat", "lon"), data)},
                         coords={"lat": lat, "lon": lon})
    path = directory / f"exten_phsc_{year}.nc"
    dataset.to_netcdf(path)
    return path


def write_rice_config(path, destination, years):
    path.write_text(
        "glorice:\n"
        f"  destination: {destination}\n"
        "  years:\n" + "".join(f"    - {y}\n" for y in years)
    )
    return path


def test_transform_of_reads_the_grid_spacing(tmp_path):
    make_glorice(tmp_path / "g", 2000)
    with xr.open_dataset(tmp_path / "g" / "exten_phsc_2000.nc") as dataset:
        transform = rice.transform_of(dataset)
    assert transform.a == pytest.approx(0.05)
    assert transform.e == pytest.approx(-0.05)
    assert transform.c == pytest.approx(120.0)
    assert transform.f == pytest.approx(31.0)


def test_rice_emits_the_expected_schema_and_row_count(tmp_path):
    glorice = tmp_path / "g"
    for year in (2000, 2010):
        make_glorice(glorice, year)
    config = write_rice_config(tmp_path / "sources.yml", glorice, [2000, 2010])
    zones = write_zones(tmp_path / "z.geojson", ALL_FOUR)
    out = tmp_path / "rice.csv"

    code = rice.main(["--config", str(config), "--glorice", str(glorice),
                      "--zones", str(zones), "--out", str(out), "--write"])
    assert code == 0
    rows = list(csv.DictReader(open(out, newline="")))
    assert len(rows) == 2 * 4
    assert set(rows[0]) == set(rice.FIELDS)
    assert {r["source"] for r in rows} == {"GloRice"}


def test_rice_comparison_mode_writes_nothing(tmp_path):
    glorice = tmp_path / "g"
    make_glorice(glorice, 2000)
    config = write_rice_config(tmp_path / "sources.yml", glorice, [2000])
    zones = write_zones(tmp_path / "z.geojson", ALL_FOUR)
    out = tmp_path / "rice.csv"
    assert rice.main(["--config", str(config), "--glorice", str(glorice),
                      "--zones", str(zones), "--out", str(out)]) == 0
    assert not out.exists()


def test_rice_carries_non_glorice_rows_forward_and_says_so(tmp_path, capsys):
    glorice = tmp_path / "g"
    make_glorice(glorice, 2000)
    config = write_rice_config(tmp_path / "sources.yml", glorice, [2000])
    zones = write_zones(tmp_path / "z.geojson", ALL_FOUR)
    out = tmp_path / "rice.csv"
    with open(out, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=rice.FIELDS)
        writer.writeheader()
        writer.writerow({"source": "SPAM", "year": "2000", "province": "Anhui",
                         "rice_area_km2": "10746.3", "thesis_pppm_km2": "19651"})

    rice.main(["--config", str(config), "--glorice", str(glorice),
               "--zones", str(zones), "--out", str(out), "--write"])
    printed = capsys.readouterr().out
    assert "carried forward unchanged, NOT regenerated" in printed
    assert "SPAM" in printed
    rows = list(csv.DictReader(open(out, newline="")))
    assert any(r["source"] == "SPAM" for r in rows)


def test_rice_reports_a_missing_year_file(tmp_path):
    glorice = tmp_path / "g"
    make_glorice(glorice, 2000)
    config = write_rice_config(tmp_path / "sources.yml", glorice, [2000, 1999])
    zones = write_zones(tmp_path / "z.geojson", ALL_FOUR)
    with pytest.raises(SystemExit):
        rice.main(["--config", str(config), "--glorice", str(glorice),
                   "--zones", str(zones), "--out", str(tmp_path / "o.csv")])


def test_rice_values_are_summed_not_counted(tmp_path):
    """Cells hold hectares; doubling the value must double the area."""
    a, b = tmp_path / "a", tmp_path / "b"
    make_glorice(a, 2000, hectares=100.0)
    make_glorice(b, 2000, hectares=200.0)
    zones = write_zones(tmp_path / "z.geojson", ALL_FOUR)
    rows_a = rice.glorice_rows(a, zones, [2000])
    rows_b = rice.glorice_rows(b, zones, [2000])
    for one, two in zip(rows_a, rows_b):
        assert float(two["rice_area_km2"]) == pytest.approx(
            2 * float(one["rice_area_km2"]), rel=1e-6)
