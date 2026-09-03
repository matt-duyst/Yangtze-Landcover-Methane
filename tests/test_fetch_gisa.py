"""Tests for the GISA fetch entry point.

Offline. No test reaches the network or reads data/raw/.

The thing worth testing here is tile selection. GISA's filenames carry no
version, no year and no coordinate, so the only way to know which of its 257
tiles covers a box is to read each one's georeferencing. That is a real
behaviour with a real failure mode, and it is exercised against a small zip of
synthetic GeoTIFFs built in tmp_path.
"""

from __future__ import annotations

import importlib.util
import zipfile
from pathlib import Path

import numpy as np
import pytest
import rasterio
from rasterio.transform import from_origin

REPO = Path(__file__).resolve().parents[1]


def load_script():
    path = REPO / "scripts" / "fetch_gisa.py"
    spec = importlib.util.spec_from_file_location("_fetch_gisa", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def tile(path, *, west, north, size=1.0, pixels=8):
    profile = dict(driver="GTiff", height=pixels, width=pixels, count=1,
                   dtype="uint8", crs="EPSG:4326",
                   transform=from_origin(west, north, size / pixels, size / pixels))
    with rasterio.open(path, "w", **profile) as dst:
        dst.write(np.zeros((pixels, pixels), "uint8"), 1)
    return path


def archive_of(tmp_path, tiles):
    """A zip whose member names say nothing about where the tiles are."""
    made = []
    for i, (west, north) in enumerate(tiles, start=1):
        made.append(tile(tmp_path / f"urban_{i}.tif", west=west, north=north))
    out = tmp_path / "GISA_tif.zip"
    with zipfile.ZipFile(out, "w") as z:
        for path in made:
            z.write(path, f"GISA_tif/{path.name}")
    return out


def test_tiles_are_selected_by_georeferencing_not_by_name(tmp_path):
    module = load_script()
    # urban_1 is far away, urban_2 covers the box, urban_3 touches its corner.
    archive = archive_of(tmp_path, [(0.0, 1.0), (120.0, 32.0), (121.0, 31.0)])
    got = module.tiles_covering(archive, 120.2, 31.2, 120.8, 31.8)
    assert got == ["GISA_tif/urban_2.tif"], "only the tile that actually covers it"


def test_several_tiles_can_cover_one_box(tmp_path):
    module = load_script()
    archive = archive_of(tmp_path, [(120.0, 32.0), (121.0, 32.0)])
    got = module.tiles_covering(archive, 120.5, 31.2, 121.5, 31.8)
    assert sorted(got) == ["GISA_tif/urban_1.tif", "GISA_tif/urban_2.tif"]


def test_a_box_outside_every_tile_selects_nothing(tmp_path):
    module = load_script()
    archive = archive_of(tmp_path, [(120.0, 32.0)])
    assert module.tiles_covering(archive, -50.0, -50.0, -49.0, -49.0) == []


def test_a_tile_that_only_touches_the_edge_is_excluded(tmp_path):
    """Strict intersection, so a shared boundary is not a covering tile."""
    module = load_script()
    archive = archive_of(tmp_path, [(120.0, 32.0)])          # 120-121 E, 31-32 N
    assert module.tiles_covering(archive, 121.0, 31.0, 122.0, 32.0) == []


def test_the_configured_tiles_match_what_the_config_says_about_the_box():
    """The four tiles are 10 degrees square and the box needs exactly those."""
    import yaml

    config = yaml.safe_load((REPO / "config" / "sources.yml").read_text())
    entry, box = config["gisa"], config["s5p"]["bounding_box"]
    assert sorted(entry["tiles"]) == ["urban_205.tif", "urban_206.tif",
                                      "urban_217.tif", "urban_218.tif"]
    # 110-130 E and 20-40 N in two 10-degree steps each contains the box.
    assert 110 <= box["west"] and box["east"] <= 130
    assert 20 <= box["south"] and box["north"] <= 40


def test_the_config_records_the_ascending_encoding_and_the_right_selector():
    """The inversion this product invites is pinned in configuration."""
    import yaml

    entry = yaml.safe_load((REPO / "config" / "sources.yml").read_text())["gisa"]
    assert entry["year_values_ascend"] is True
    assert entry["extent_2018_selector"] == "between(1, 36)"
    assert entry["nodata"] is None
    assert entry["pixel_size_deg"] == pytest.approx(0.00026949458523585647)
