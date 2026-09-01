#!/usr/bin/env python3
"""Provincial rice physical area from GloRice and SPAM, 5-arcmin grids.

RECONNAISSANCE SCRIPT. This is not part of the pipeline and will be superseded
by src/landcover/. It is preserved so that the numbers in
data/processed/rice_area_by_province.csv have a visible derivation, not so that
anyone runs it.

IT CANNOT RUN FROM A FRESH CLONE. Two reasons, both structural:

  1. There is no fetch layer yet. src/fetch/ does not exist, so nothing in the
     repository knows how to obtain the source rasters. The paths below point
     into a scratch directory that a clone will not have.
  2. The source rasters were deleted after the numbers were extracted, under a
     download budget that did not allow keeping them. GloRice-phsc-Ex.zip
     (148.8 MB), spam2000_phys.zip (88.6 MB) and spam2010_phys.zip (143.5 MB)
     are gone from this machine. data/manifest.json records where to re-fetch
     GloRice; SPAM is not in the manifest because it is not used in analysis.

PROVENANCE NOTE. The original computation was executed as inline heredocs
during a reconnaissance session on 2026-09-01, not as a saved file. This script
is a reconstruction of those heredocs, written afterwards from the session
record. It reproduces the same logic and the same constants, but it is not a
byte-for-byte copy of something that was run, because no such file existed.

Sources as used:
  GloRice v1.0, figshare 10.6084/m9.figshare.27965832.v2, GloRice-phsc-Ex.zip,
    exten_phsc_{year}.nc, variable "area", hectares per cell, NaN outside rice.
  SPAM 2000 v3.0.7, Harvard Dataverse doi:10.7910/DVN/A50I2T,
    spam2000V3r107_global_P_RICE_A.tif (physical area, all technologies).
  SPAM 2010 v2.0,   Harvard Dataverse doi:10.7910/DVN/PRFF8V,
    spam2010V2r0_global_A_RICE_A.tif (physical area, all technologies).

Both products share an identical global 5-arcmin grid: 2160 x 4320 cells,
-180..180 by 90..-90, EPSG:4326. Cell values are already areas in hectares, so
the equal-area projection is used only to compute how much of each cell falls
inside each province, never to measure the rice area itself.
"""

import json
import pickle

import geopandas as gpd
import numpy as np
import rasterio
import xarray as xr
from shapely.geometry import box

# China Albers Equal Area. Used for the cell/province intersection weights only.
AEA = (
    "+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105 "
    "+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs"
)

RES = 1 / 12.0  # 5 arcmin
PROVINCES = ["Shanghai", "Zhejiang", "Anhui", "Jiangsu"]

# Scratch paths from the reconnaissance session. They do not exist in a clone.
SCRATCH = "/tmp/lc_recon"
BOUNDARIES = "data/reference/yrd_provinces.geojson"


def cell_bounds(i, j):
    """Geographic bounds of cell (row i from north, column j from -180)."""
    return (-180 + j * RES, 90 - (i + 1) * RES, -180 + (j + 1) * RES, 90 - i * RES)


def build_weights(boundaries=BOUNDARIES):
    """Fraction of each 5-arcmin cell falling inside each province.

    The fraction is the ratio of intersection area to whole-cell area, both
    measured in China Albers Equal Area, so that cells are weighted by true
    ground area rather than by degrees.
    """
    provinces = gpd.read_file(boundaries)
    weights = {}
    for _, row in provinces.iterrows():
        name = row["name"]
        minx, miny, maxx, maxy = row.geometry.bounds
        j0, j1 = int(np.floor((minx + 180) / RES)), int(np.ceil((maxx + 180) / RES))
        i0, i1 = int(np.floor((90 - maxy) / RES)), int(np.ceil((90 - miny) / RES))

        cells, ii, jj = [], [], []
        for i in range(i0, i1):
            for j in range(j0, j1):
                cells.append(box(*cell_bounds(i, j)))
                ii.append(i)
                jj.append(j)

        cells_aea = gpd.GeoSeries(cells, crs="EPSG:4326").to_crs(AEA)
        province_aea = gpd.GeoSeries([row.geometry], crs="EPSG:4326").to_crs(AEA).iloc[0]

        intersected = cells_aea.intersection(province_aea).area.values
        whole = cells_aea.area.values
        frac = np.where(whole > 0, intersected / whole, 0.0)

        keep = frac > 0
        weights[name] = (np.array(ii)[keep], np.array(jj)[keep], frac[keep])
    return weights


def summarise(array, weights, nodata=None):
    """Weighted sum of a 5-arcmin hectare grid within each province."""
    a = np.asarray(array, dtype="float64")
    if nodata is not None:
        a = np.where(a == nodata, 0.0, a)
    a = np.nan_to_num(a, nan=0.0)
    return {p: float((a[ii, jj] * fr).sum()) for p, (ii, jj, fr) in weights.items()}


def main():
    weights = build_weights()
    with open(f"{SCRATCH}/weights.pkl", "wb") as fh:
        pickle.dump(weights, fh)

    results = {}

    with rasterio.open(f"{SCRATCH}/ex/spam2000V3r107_global_P_RICE_A.tif") as src:
        results[("SPAM", "2000")] = summarise(src.read(1), weights, src.nodata)
    with rasterio.open(f"{SCRATCH}/ex/spam2010V2r0_global_A_RICE_A.tif") as src:
        results[("SPAM", "2010")] = summarise(src.read(1), weights, src.nodata)

    for year in ["2000", "2010", "2018", "2019", "2020", "2021"]:
        ds = xr.open_dataset(f"{SCRATCH}/ex/GloRice-phsc-Ex/exten_phsc_{year}.nc")
        results[("GloRice", year)] = summarise(ds["area"].values, weights)
        ds.close()

    # Source values are hectares; divide by 100 for square kilometres.
    for (product, year), value in sorted(results.items()):
        line = "".join(f"{value[p] / 100.0:>12,.0f}" for p in PROVINCES)
        print(f"{product:<9}{year:<7}{line}")

    with open(f"{SCRATCH}/province_rice_ha.json", "w") as fh:
        json.dump({f"{a}_{b}": c for (a, b), c in results.items()}, fh, indent=1)


if __name__ == "__main__":
    main()
