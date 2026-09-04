#!/usr/bin/env python
"""Extract the map layers the figures need from the local cartopy cache.

    python scripts/extract_reference_geometry.py

Writes two public-domain Natural Earth layers into `data/reference/` so that
figures never read a machine-local cache at draw time. This is the same route
`yrd_provinces.geojson` took and it is run once, not by the pipeline: a cache
is not a version and cannot be verified by anyone else, so the committed file
is the source from here on.

Two layers, at two generalisations, chosen to match the scale each is drawn at:

* `yrd_land.geojson`, from the 10 m land polygons clipped to the study box
  with half a degree of padding, for the land and sea of the main panel.
* `china_admin1_dissolved.geojson`, from the 50 m admin-1 layer, for the
  locator inset. The inset is about 3 cm across, where 10 m detail is smaller
  than the line width, so the coarser variant is the honest one to use.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

import geopandas as gpd
from shapely.geometry import box

CACHE = Path.home() / ".local/share/cartopy/shapefiles/natural_earth"
REFERENCE = Path(__file__).resolve().parents[1] / "data" / "reference"

#: The study lattice with half a degree of padding, so the coastline reaches
#: the panel edge instead of stopping short of it.
CLIP = box(114.3, 26.45, 123.05, 35.7)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> int:
    if not CACHE.is_dir():
        print(f"no cartopy cache at {CACHE}", file=sys.stderr)
        return 1
    REFERENCE.mkdir(parents=True, exist_ok=True)

    land = gpd.read_file(CACHE / "physical" / "ne_10m_land.shp")
    land = gpd.clip(land, CLIP)[["geometry"]].reset_index(drop=True)
    land_path = REFERENCE / "yrd_land.geojson"
    land.to_file(land_path, driver="GeoJSON")

    admin1 = gpd.read_file(CACHE / "cultural" / "ne_50m_admin_1_states_provinces_lakes.shp")
    china = admin1[admin1["admin"] == "China"]
    outline = china.dissolve()[["geometry"]].reset_index(drop=True)
    outline_path = REFERENCE / "china_admin1_dissolved.geojson"
    outline.to_file(outline_path, driver="GeoJSON")

    for path, source, count in ((land_path, "ne_10m_land", len(land)),
                                (outline_path, "ne_50m_admin_1 (China)", len(china))):
        print(f"  {path.name}")
        print(f"    from    {source}, {count} input features")
        print(f"    bytes   {path.stat().st_size:,}")
        print(f"    sha256  {digest(path)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
