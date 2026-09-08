#!/usr/bin/env python3
"""Build the terrain and place layers the study area map draws.

    python scripts/build_map_reference.py           # report what it would make
    python scripts/build_map_reference.py --write   # write into data/reference/

Run once by hand, like `extract_reference_geometry.py`, and not by the
pipeline. Four products, from two sources, and they serve different panels.

**The main panel's relief comes from Copernicus DEM GLO-90**, fetched by
`scripts/fetch_copernicus_dem.py` into the gitignored `data/raw/`, mosaicked
and shaded here. The committed output is the shaded relief, not the elevation:
the figure needs the shading and a 90 m elevation model over eight degrees is
half a gigabyte.

Three things about the DEM are worth stating because two of them were checked
against a claim that turned out to be about somewhere else.

* **Ocean areas have no tiles.** The bucket's readme says so and says height
  may be assumed zero there; measured, 20 of the 100 one-degree tiles over the
  padded study box are absent and all 20 are offshore. They are filled with
  zero, which is what the readme instructs and what a delta needs.
* **Pixels are square here.** The readme's table gives a longitude spacing that
  widens with *latitude*, from 1x in the 0-50 degree band to 10x above 85. The
  study area is at 26.9 to 35.3 N, so every tile is 1200 by 1200 at
  1/1200 degree in both axes; measured over all 80, there is no variation at
  all. The 1:5 ratio that motivates a cubic resampler in some derived products
  happens in the 80-85 degree band and is not reachable from here.
* **Cubic anyway, and the seams checked anyway.** Cubic is the right resampler
  for a 3.9x decimation regardless of pixel shape, and the seam check was run
  rather than skipped: over the rugged 27 to 29.5 N band, the mean second
  difference along tile-edge columns is 0.989 of its value elsewhere under
  cubic and 1.041 under bilinear. Neither shows a seam artefact. A ratio near
  one is the answer; a ratio well above one would have been the artefact.

The DEM is warped to a grid whose pixels are **square in ground metres** at the
study area's centre latitude, so `gdaldem`'s single `-s` scale is exact rather
than under-weighting east-west slope by 1/cos(31.075) = 17 percent. That is why
the longitude and latitude steps differ.

**The inset's terrain comes from Natural Earth's 50 m hypsometric raster**,
which is 10800 by 5400 for the globe, 30 pixels per degree. The inset is about
4.6 cm wide across 64 degrees, which is 543 pixels at 300 dpi, so 30 px/deg is
already three times what it needs and the committed clip is reduced to 16.

Natural Earth's 10 m raster is 21600 by 10800, 60 px/deg, which is 465 pixels
across the 7.75 degree study box. That is not enough for the main panel and is
far more than enough for the inset, which is why the two panels use different
sources. See `notes/decisions.md` for the measurement.

Licences differ and both are recorded in `data/manifest.json`. Natural Earth is
public domain. Copernicus DEM is free of charge for any use but **requires
attribution**, and the required notice is quoted verbatim below and in the
figure caption.
"""

from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

RAW_DEM = REPO / "data" / "raw" / "copernicus_dem"
RAW_NE = REPO / "data" / "raw" / "natural_earth"
REFERENCE = REPO / "data" / "reference"
CACHE = Path.home() / ".local/share/cartopy/shapefiles/natural_earth"

#: Article 6(b) of the Copernicus WorldDEM-90 licence, for adapted or modified
#: data, quoted exactly. A hillshade is adapted data, so this is the notice
#: that applies rather than the 6(a) one for the model itself. The licence's
#: own closing quotation mark is a curly one against a straight opener; the
#: text between them is reproduced unchanged.
DEM_NOTICE = ("produced using Copernicus WorldDEM™-90 © DLR e.V. "
              "2010-2014 and © Airbus Defence and Space GmbH 2014-2018 "
              "provided under COPERNICUS by the European Union and ESA; all "
              "rights reserved")

#: Article 6(c), which applies because this repository redistributes a derived
#: product rather than only displaying one.
DEM_LIABILITY = ("The organisations in charge of the Copernicus programme by "
                 "law or by delegation do not incur any liability for any use "
                 "of the Copernicus WorldDEM™-90")

# The relief covers the drawn extent with a small pad, so the hillshade's own
# edge effects fall outside the frame rather than on it.
RELIEF_WEST, RELIEF_EAST = 114.75, 122.60
RELIEF_SOUTH, RELIEF_NORTH = 26.90, 35.25

#: Rows per degree of latitude in the committed relief.
#:
#: 200, which is 1.29 times what the main panel resolves at 300 dpi, and it was
#: set by measuring rather than by picking a round number. The first build used
#: 300 and the reason to come down is not the committed file, though that falls
#: from 2.13 MB to 0.92 MB: it is that a hillshade computed at twice the
#: resolution the page can show is half noise, and noise is exactly what a
#: deflate stream inside a PDF cannot compress. Measured, the figure's vector
#: form went from 1.76 MB to 1.66 MB against a 2 MB venue ceiling, and the
#: relief reads better because the detail that went is detail no reader could
#: resolve. Going further, to 150, saves more but puts the relief below the
#: panel's own resolution, which is the softness this whole exercise avoided.
RELIEF_ROWS_PER_DEGREE = 200

#: Centre latitude of the study area. The same constant `src/figures/geo.py`
#: uses for the display aspect, repeated here because gdal is being driven
#: through a subprocess and cannot import it.
CENTRE_LATITUDE = 31.075

#: The inset's extent, matching `study_area.INSET_EXTENT`.
INSET = (72.0, 17.0, 136.0, 54.5)
#: The equal-area conic the inset is drawn in, repeated from
#: `src/figures/geo.CHINA_ALBERS` because gdal is driven through a subprocess.
ALBERS = ("+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 "
          "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs")
#: Pixels per degree in the committed inset raster. See the module docstring.
INSET_PIXELS_PER_DEGREE = 16

#: The four study provinces, as Natural Earth names them.
STUDY_PROVINCES = ("Anhui", "Jiangsu", "Shanghai", "Zhejiang")

#: Provinces that share the frame with the study region. All five are Chinese
#: provinces and all five are drawn and named, so the study area sits in a
#: country rather than in white. Not a hand-picked list: it is every admin-1
#: unit whose geometry intersects the drawn extent and is not a study province.
#: Reported by this script rather than written down.

#: Everything the main panel needs, with half a degree of padding so a
#: neighbour's boundary reaches the frame instead of stopping short of it.
CLIP = (114.3, 26.45, 123.05, 35.7)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(*args) -> None:
    subprocess.run([str(a) for a in args], check=True,
                   stdout=subprocess.DEVNULL)


# --------------------------------------------------------------------------
# terrain
# --------------------------------------------------------------------------

def build_hillshade(work: Path, out: Path) -> dict:
    """Mosaic, warp and shade the GLO-90 tiles over the study box."""
    import math

    tiles = sorted(RAW_DEM.glob("*.tif"))
    if not tiles:
        raise SystemExit(
            f"no Copernicus DEM tiles in {RAW_DEM}; run "
            f"python scripts/fetch_copernicus_dem.py --download first")

    yres = 1.0 / RELIEF_ROWS_PER_DEGREE
    # Square in ground metres at the centre latitude, so gdaldem's single
    # vertical-to-horizontal scale is exact in both axes rather than in one.
    xres = yres / math.cos(math.radians(CENTRE_LATITUDE))

    vrt = work / "mosaic.vrt"
    dem = work / "dem.tif"
    run("gdalbuildvrt", "-q", "-overwrite", vrt, *tiles)
    # No -dstnodata: the twenty absent offshore tiles become zero, which is the
    # height the bucket's readme says to assume over ocean. Setting a nodata
    # value instead makes the sea a hole and gdaldem renders a hole as black.
    run("gdalwarp", "-q", "-overwrite", "-r", "cubic",
        "-te", RELIEF_WEST, RELIEF_SOUTH, RELIEF_EAST, RELIEF_NORTH,
        "-tr", xres, yres, "-ot", "Float32",
        "-co", "COMPRESS=DEFLATE", "-co", "PREDICTOR=3", vrt, dem)
    # 111120 m per degree is gdal's convention for a lat/lon model; it is exact
    # in latitude and, on this grid, in longitude too.
    #
    # Multidirectional rather than a single 315 degree light, because the delta
    # is flat and a single azimuth leaves whole ranges unlit; and because the
    # relief is a ground under overlays, where a softer shading competes less.
    # z 1.6 was chosen by rendering: at 1.0 the Zhejiang mountains that explain
    # the composite's largest hole do not read at 10 cm.
    run("gdaldem", "hillshade", "-q", "-s", 111120, "-multidirectional",
        "-z", 1.6, "-compute_edges",
        "-co", "COMPRESS=DEFLATE", "-co", "PREDICTOR=2", "-co", "TILED=YES",
        dem, out)
    return {"tiles": len(tiles), "xres": xres, "yres": yres}


def build_cell_elevation(work: Path, out: Path) -> dict:
    """Mean GLO-90 elevation per analysis cell, on the lattice exactly.

    Committed because it is what the study area figure's one real claim rests
    on, and because the DEM it comes from is 408 MB and gitignored. At 33 by 31
    cells this is a few kilobytes, and `scripts/verify_claims.py` reads it so
    the caption's elevations are checked against data rather than remembered.

    Averaged, not sampled: a cell is 24 by 28 km and a point elevation inside
    one says nothing about it.
    """
    import sys as _sys
    _sys.path.insert(0, str(REPO))
    from src.figures import geo

    tiles = sorted(RAW_DEM.glob("*.tif"))
    if not tiles:
        raise SystemExit(f"no Copernicus DEM tiles in {RAW_DEM}")
    spec = geo.study_spec()
    extent = geo.lattice_extent(spec)
    vrt = work / "elev.vrt"
    run("gdalbuildvrt", "-q", "-overwrite", vrt, *tiles)
    run("gdalwarp", "-q", "-overwrite", "-r", "average",
        "-te", extent.west, extent.south, extent.east, extent.north,
        "-tr", spec.resolution, spec.resolution, "-ot", "Float32",
        "-co", "COMPRESS=DEFLATE", vrt, out)
    import rasterio
    with rasterio.open(out) as src:
        data = src.read(1)
        shape = (src.height, src.width)
    return {"shape": shape, "median_m": round(float(__import__("numpy")
                                                   .median(data)), 1)}


def build_inset_raster(out: Path) -> dict:
    """Clip and reduce Natural Earth's hypsometric raster onto the inset.

    Warped into `CHINA_ALBERS`, the equal-area conic this project measures
    areas in, rather than left in degrees. The reason is the one already
    recorded for the inset's geometry: it spans most of China and an
    equirectangular map of that extent is badly stretched at its northern
    edge. Warping the raster here rather than at draw time means the figure
    does not carry a reprojection step and the two inset layers, terrain and
    boundaries, cannot end up in different projections.
    """
    source = RAW_NE / "hyp_50m" / "HYP_50M_SR_W.tif"
    if not source.exists():
        raise SystemExit(f"missing {source}; see the module docstring")
    west, south, east, north = INSET
    # Metres per pixel matching the requested pixels per degree at the
    # inset's centre latitude, so the reduction is the one intended.
    import math
    metres = 111_320 * math.cos(math.radians(0.5 * (south + north))) \
        / INSET_PIXELS_PER_DEGREE
    run("gdalwarp", "-q", "-overwrite", "-r", "average",
        "-t_srs", ALBERS, "-te_srs", "EPSG:4326",
        "-te", west, south, east, north, "-tr", metres, metres,
        "-co", "COMPRESS=DEFLATE", "-co", "PREDICTOR=2",
        source, out)
    return {"pixels_per_degree": INSET_PIXELS_PER_DEGREE,
            "metres_per_pixel": round(metres)}


# --------------------------------------------------------------------------
# places and neighbours
# --------------------------------------------------------------------------

def build_places(out: Path) -> dict:
    """The provincial capitals of the four study provinces.

    The selection rule, and why it is not a bare scale-rank threshold.

    Natural Earth's populated places layer carries `SCALERANK`, and the obvious
    rule is a threshold on it. Measured over the 57 places in the study box,
    that rule cannot produce the four capitals: Shanghai is rank 0, Nanjing and
    Hangzhou are rank 2, and **Hefei is rank 4**. A threshold that reaches Hefei
    also reaches fourteen other places, including Zaozhuang and Linyi in
    Shandong and Nanchang in Jiangxi, which is more than this map can label.

    So the rule is a threshold *and* two filters, all three from the layer's own
    fields: scale rank at or below 4, feature class an admin-1 capital, and the
    admin-1 unit one of the four study provinces. That yields exactly four, and
    it yields them because of what they are rather than because they were
    chosen.

    Suzhou, Wuxi and Ningbo are rank 4 and are left off. It is a crowding
    judgement and the numbers are these: Suzhou and Wuxi are 0.35 degrees
    apart, which is 4.6 mm on the drawn panel, and both sit inside the same
    1.5 degree cluster as Shanghai, whose label already needs the room. Three
    more names there would collide with each other before they collided with
    anything else.
    """
    import geopandas as gpd

    source = RAW_NE / "places" / "ne_10m_populated_places.shp"
    if not source.exists():
        raise SystemExit(f"missing {source}; see the module docstring")
    places = gpd.read_file(source)
    keep = places[(places.SCALERANK <= 4)
                  & (places.FEATURECLA == "Admin-1 capital")
                  & (places.ADM1NAME.isin(STUDY_PROVINCES))]
    keep = keep[["NAME", "ADM1NAME", "SCALERANK", "POP_MAX", "geometry"]]
    keep = keep.rename(columns={"NAME": "name", "ADM1NAME": "province",
                                "SCALERANK": "scalerank", "POP_MAX": "pop_max"})
    keep = keep.sort_values("name").reset_index(drop=True)
    keep.to_file(out, driver="GeoJSON")
    return {"places": list(keep["name"]),
            "considered": int((places.cx[114.8:122.55, 26.95:35.2]).shape[0])}


def build_neighbours(out: Path) -> dict:
    """Provinces that share the frame but are not part of the study region."""
    import geopandas as gpd
    from shapely.geometry import box

    source = CACHE / "cultural" / "ne_10m_admin_1_states_provinces_lakes.shp"
    if not source.is_dir() and not source.exists():
        raise SystemExit(f"no cartopy cache at {source}")
    admin1 = gpd.read_file(source)
    frame = box(114.8, 26.95, 122.55, 35.2)
    near = admin1[(admin1["admin"] == "China")
                  & admin1.geometry.intersects(frame)
                  & ~admin1["name_en"].isin(STUDY_PROVINCES)]
    near = gpd.clip(near, box(*CLIP))[["name_en", "geometry"]]
    near = near.rename(columns={"name_en": "name"})
    near = near.sort_values("name").reset_index(drop=True)
    near.to_file(out, driver="GeoJSON")
    return {"neighbours": list(near["name"])}


def build_inset_boundaries(out: Path) -> dict:
    """Natural Earth's admin-0 land boundary lines across the inset extent.

    **Drawn as Natural Earth draws them and filtered by nothing.** The previous
    inset outlined the 31 admin-1 units filed under `admin = "China"` in the
    50 m layer, which excluded Taiwan, Hong Kong and Macau. That exclusion was
    inherited rather than chosen, and it was not even the mechanism it was
    documented as: the 50 m admin-1 layer has no Taiwan, Hong Kong or Macau
    features to exclude. Only the 10 m layer carries them, as 21, 1 and 1
    units against China's 32.

    So the inset asserts nothing. It draws terrain, which has no opinion, and
    over it every admin-0 land boundary line in the extent, unedited and with
    no country named or filled. Taiwan and Hainan appear as their coastlines
    do, like Kyushu; Hong Kong and Macau are not distinguished, because this
    layer carries no feature for either. Natural Earth classes six of the
    lines in the extent as `Disputed (please verify)` and carries per-country
    viewpoint fields -- `FCLASS_CN`, `FCLASS_TW`, `FCLASS_IN` and twenty-eight
    more -- which is the source's own statement that the classification depends
    on who is asked. The caption says whose lines these are.
    """
    import geopandas as gpd
    from shapely.geometry import box

    source = CACHE / "cultural" / "ne_50m_admin_0_boundary_lines_land.shp"
    lines = gpd.read_file(source)
    west, south, east, north = INSET
    frame = box(west, south, east, north)
    near = gpd.clip(lines[lines.geometry.intersects(frame)], frame)
    classes = sorted(set(near["FEATURECLA"].dropna()))
    near = near[["FEATURECLA", "geometry"]].rename(
        columns={"FEATURECLA": "featurecla"}).reset_index(drop=True)
    near.to_file(out, driver="GeoJSON")
    return {"lines": len(near), "classes": classes}


PRODUCTS = (
    ("yrd_hillshade.tif", build_hillshade),
    ("yrd_cell_elevation.tif", build_cell_elevation),
    ("china_hypsometric.tif", build_inset_raster),
    ("yrd_places.geojson", build_places),
    ("yrd_neighbours.geojson", build_neighbours),
    ("inset_boundaries.geojson", build_inset_boundaries),
)


def main(argv=None) -> int:
    import tempfile

    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--write", action="store_true",
                        help="write into data/reference/ rather than reporting")
    args = parser.parse_args(argv)

    destination = REFERENCE if args.write else Path(tempfile.mkdtemp())
    destination.mkdir(parents=True, exist_ok=True)
    print(f"writing into {destination}")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        for name, builder in PRODUCTS:
            out = destination / name
            detail = (builder(work, out)
                      if builder in (build_hillshade, build_cell_elevation)
                      else builder(out))
            print(f"  {name}")
            for key, value in detail.items():
                print(f"    {key:16s} {value}")
            print(f"    bytes            {out.stat().st_size:,}")
            print(f"    sha256           {digest(out)}")
    print()
    print("Copernicus DEM attribution, required by Article 6(b):")
    print(f'  "{DEM_NOTICE}".')
    print("and by Article 6(c), for redistribution:")
    print(f'  "{DEM_LIABILITY}".')
    print("Natural Earth is public domain and requires no attribution.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
