# Reference data

Small committed inputs that are not derived results. Nothing in this directory
is computed by the pipeline; it is here so that analysis has a fixed, versioned
starting point rather than reaching into a machine-local cache.

## yrd_provinces.geojson

The four study provinces of the Yangtze River Delta region: Anhui, Zhejiang,
Jiangsu and Shanghai. The source is Natural Earth's 10 m admin-1 states and
provinces layer, the variant with lakes, extracted from the cartopy shapefile
cache on the machine where this repository was rebuilt. Natural Earth is public
domain. No attribution is required and there is no restriction on
redistribution or on derivative works, which is why the file can simply be
committed here rather than fetched and verified like every other input.

The file is EPSG:4326 GeoJSON. The original shapefile carries 121 attribute
fields; 115 of them are dropped and six are kept, being name, name_en, name_zh,
adm1_code, iso_3166_2 and type_en. Anhui is a single polygon; Jiangsu, Shanghai
and Zhejiang are multipolygons, Zhejiang with seventeen parts because of its
offshore islands.

From here on this committed file is the boundary source. The cartopy cache is
not read at analysis time again, because a cache is not a version and cannot be
verified by anyone else.

Measured in the China Albers Equal Area projection used throughout this project
(+proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105), the four features enclose
Anhui 140,194 km2, Zhejiang 101,337 km2, Jiangsu 100,091 km2 and Shanghai
6,746 km2. Published provincial areas are roughly 140,100, 101,800, 102,600 and
6,341 km2 respectively. Anhui agrees to better than a tenth of a percent and
Zhejiang to about half a percent, but Jiangsu comes out about 2 percent low and
Shanghai about 6 percent high.

The Shanghai discrepancy is the one to watch, and it has now been cross-checked
against GADM 4.1, which resolves the same municipality with 1,925 vertices
across 112 parts where Natural Earth uses 213 across 4. If the excess were an
artefact of a coarse outline, the higher-fidelity source should sit closer to
the published figure. It does not. GADM gives Shanghai 6,883 km2, further above
the published 6,341 than Natural Earth's 6,746.

| province | Natural Earth km2 | GADM 4.1 km2 | published km2 | NE / published | GADM / published |
|---|---|---|---|---|---|
| Anhui | 140,194 | 140,306 | 140,100 | 1.0007 | 1.0015 |
| Zhejiang | 101,337 | 102,775 | 101,800 | 0.9955 | 1.0096 |
| Jiangsu | 100,091 | 101,698 | 102,600 | 0.9755 | 0.9912 |
| Shanghai | 6,746 | 6,883 | 6,341 | 1.0639 | 1.0855 |

Two independent boundary sets therefore agree that Shanghai is larger than the
published figure, and the more detailed of the two agrees less. That points at
what the published figure measures rather than at how well either polygon is
drawn. The likely candidate, offered as a hypothesis and not as a finding, is
that the published area excludes estuarine water and reclaimed ground that both
polygon sets enclose. This has not been run down. Jiangsu behaves differently
again: Natural Earth is about 2 percent low but GADM only about 1 percent low,
so the two sources disagree with each other as well as with the published
value.

The practical caution stands but should be read more broadly than before.
Before provincial areas are used as denominators, for an impervious fraction or
a rice fraction or anything else normalised by land area, the question to settle
is not only which polygon is used but what the denominator is meant to measure,
because a 6 percent error in it is larger than several of the differences this
project is trying to measure.

GADM cannot be committed here. Its licence forbids redistribution without
permission, so it served as a check and nothing derived from its geometry is
stored in this repository.

One further caution about reproducibility. The exact Natural Earth release
bundled in the cartopy cache is not recorded anywhere in the shapefile, so the
manifest entry describes where the file came from rather than naming a version
number. A future re-extraction from a different Natural Earth release could
yield slightly different geometries and therefore slightly different areas.

## yrd_land.geojson

Natural Earth 10 m land polygons, clipped to the study box with half a degree
of padding, for the land and sea of the map figures. Seven features, 2,677
exterior vertices, EPSG:4326 GeoJSON, all attributes dropped because only the
geometry is used. Public domain, like the province file.

The padding exists so that the coastline reaches the edge of a drawn panel
rather than stopping short of it, leaving a sliver of sea colour over land.

## china_admin1_dissolved.geojson

The outline of Natural Earth's 31 China admin-1 units, dissolved into one
geometry, for the locator inset. Taken from the **50 m** variant rather than
the 10 m one used everywhere else: the inset is about 3 cm across, where 10 m
detail is finer than the line width, so the coarser variant is the honest
choice and the smaller file.

What the outline contains is the extent of those 31 units, which are the
provinces, autonomous regions and municipalities Natural Earth files under
`admin = "China"` at 50 m.

**A correction to what this file used to say.** It said that Natural Earth
carries Taiwan, Hong Kong and Macau separately, so none of the three is in this
geometry. The conclusion was right and the mechanism was not. Checked across
the three admin-1 variants in the cache: the **10 m** layer carries `Taiwan`
(21 units), `Hong Kong S.A.R.` (1) and `Macau S.A.R` (1) beside `China` (32);
the **50 m** layer, which is the one this file is built from, has only `China`
(31 units) and no features for the other three at all; the 110 m layer has no
Chinese admin-1 units of any kind. So nothing was excluded by the
`admin == "China"` filter here, because there was nothing for it to exclude.

That distinction matters because it is the difference between a choice and an
inheritance, and this outline is no longer used by any figure. The study area
map's locator now draws Natural Earth's admin-0 land boundary lines across its
whole extent, unfiltered; see `inset_boundaries.geojson`. This file is retained
because it is committed and because a reader may meet it in the history.

Both files were extracted by `scripts/extract_reference_geometry.py`, which is
run once by hand and not by the pipeline, on the same principle as the province
file: a cache is not a version and cannot be verified by anyone else, so the
committed file is the source from here on.


## yrd_hillshade.tif

Shaded relief over the study box, from Copernicus DEM GLO-90 at 90 m. This is
the main panel's ground in `figures/study_area.png`, and it is there to be
read rather than to decorate: the composite figure's 97 unobserved cells have a
median elevation of 502 m against 35 m for the 926 observed ones, and the
largest connected block of 47 sits on the mountains along the southern edge of
the box.

Byte, EPSG:4326, 1,345 by 1,670 at 200 rows per degree of latitude, covering
114.75 to 122.60 east and 26.90 to 35.25 north. The longitude step is larger
than the latitude step on purpose: the grid is square in **ground metres** at
31.075 N, the study area's centre latitude, so `gdaldem`'s single
vertical-to-horizontal scale is exact in both axes. Warped with `-r cubic` and
shaded with `gdaldem hillshade -s 111120 -multidirectional -z 1.6
-compute_edges` at GDAL 3.11.4.

200 rows per degree is 1.29 times what the figure's main panel resolves at
300 dpi, and it was chosen by measuring. A hillshade computed at twice the
resolution a page can show is half noise, and noise is what a deflate stream
inside a PDF cannot compress: at 300 rows per degree this file was 2.13 MB and
the figure's vector form 1.76 MB against a 2 MB venue ceiling; at 200 they are
0.92 MB and 1.66 MB, and the relief reads better because what went was detail
no reader could resolve.

**Licence: attribution is required**, unlike everything else in this directory.
Copernicus DEM is free of charge for any use, worldwide and without limit in
time, including modification and redistribution, but Article 6(b) of the
WorldDEM-90 licence requires this notice for adapted data, quoted verbatim:

> produced using Copernicus WorldDEM™-90 © DLR e.V. 2010-2014 and © Airbus
> Defence and Space GmbH 2014-2018 provided under COPERNICUS by the European
> Union and ESA; all rights reserved

and Article 6(c) requires this one, because a derived product is redistributed
here rather than only displayed:

> The organisations in charge of the Copernicus programme by law or by
> delegation do not incur any liability for any use of the Copernicus
> WorldDEM™-90

Both are carried on the figure itself as well as in its caption, because a
figure travels away from its caption and the obligation attaches to the image.

Two cautions from the bucket's readme, both checked rather than taken on trust.
Ocean areas have no tiles and height may be assumed zero there: 20 of the 100
one-degree tiles over the padded box are absent and all 20 are offshore, and
they are filled with zero, which is why the sea shades flat and is then hidden
under the sea fill anyway. And pixel spacing varies with **latitude**, not with
longitude, and only above 50 degrees: at 26.9 to 35.3 N all 80 tiles are 1200
by 1200 at 1/1200 degree in both axes, measured, so the 1:5 height-to-width
ratio that motivates a cubic resampler in some derived products cannot occur
here. Cubic was used regardless, being right for a 3.9x decimation, and the
tile seams were checked regardless: over the rugged 27 to 29.5 N band, the mean
second difference along tile-edge columns is 0.989 of its value elsewhere under
cubic and 1.041 under bilinear, so neither shows a seam artefact.

## yrd_cell_elevation.tif

Mean GLO-90 elevation per analysis cell, 33 by 31, on the composite's own grid
exactly. Three kilobytes, and it exists so that the study area figure's one
substantive claim can be checked: `scripts/verify_claims.py` computes the
absent-cell and covered-cell median elevations from it, and
`tests/test_prose_claims.py` asserts the caption's numbers against them. The
DEM those come from is 408 MB and gitignored, so without this file the claim
would be unverifiable on a fresh clone.

Averaged rather than sampled. A cell is 24 by 28 km and a point elevation
inside one says nothing about it.

Same licence and same required notices as `yrd_hillshade.tif`.

## china_hypsometric.tif

Natural Earth's 50 m cross-blended hypsometric tints with shaded relief,
clipped to the locator extent and warped to the project's China Albers
equal-area conic. Natural Earth raster 2.0.0. Public domain.

Hypsometric here and grey in the main panel, because nothing is drawn over the
inset and the reason the main panel's relief is grey does not apply.

The 10 m raster was measured rather than assumed, since the choice between the
two turns on it: it is 21,600 by 10,800, which is 60 pixels per degree exactly,
and the study box is 7.75 degrees wide, so it offers 465 pixels where the main
panel draws 1,205 at 300 dpi. That is why the main panel uses a DEM and the
inset uses Natural Earth. The 50 m raster is 30 px/deg and the inset needs
about 8, so the committed clip is reduced to 16.

## yrd_places.geojson

The provincial capitals of the four study provinces: Hangzhou, Hefei, Nanjing,
Shanghai. From Natural Earth's 10 m populated places, vector release 5.1.2.
Public domain.

The rule is `SCALERANK <= 4` and `FEATURECLA == "Admin-1 capital"` and
`ADM1NAME` in the four study provinces. It is a threshold and two filters
rather than a threshold alone, and the reason is measured: Natural Earth does
not rank the four capitals together. Shanghai is scale rank 0, Nanjing and
Hangzhou are 2, and **Hefei is 4**, so any bare threshold that reaches Hefei
also reaches fourteen other places among the 57 in the study box, including
Zaozhuang and Linyi in Shandong and Nanchang in Jiangxi.

Suzhou, Wuxi and Ningbo are also rank 4 and are deliberately not here. That is
a crowding judgement and these are its numbers: Suzhou and Wuxi are 0.35
degrees apart, which is 4.6 mm on the drawn panel, and both sit in the same
1.5 degree cluster as Shanghai, whose label already needs the space.

**This layer was not in the cartopy cache.** The province and land layers were,
and the habit of checking the cache first is why that is worth recording: the
cache on this machine holds 14 layers, all physical or administrative
boundaries, and no populated places at any scale. It was fetched from the
Natural Earth CDN and the archive's own `VERSION.txt` gives the release, which
is more than the cached shapefiles record about themselves.

## yrd_neighbours.geojson

The five Chinese provinces that share the study area map's frame without being
part of the study region: Fujian, Henan, Hubei, Jiangxi, Shandong. From the
10 m admin-1 layer in the cartopy cache, clipped to the padded box. Public
domain.

Selected by intersection with the drawn extent, not listed by hand, so the set
follows the extent if the extent moves. They are drawn and named so that the
study region sits in a country rather than in white, which is what the first
version of that figure did.

## inset_boundaries.geojson

Every feature of Natural Earth's 50 m admin-0 land boundary lines that
intersects the locator's extent: 59 lines, **unfiltered**. Public domain.

This layer replaces `china_admin1_dissolved.geojson` in the study area figure
and the replacement is a deliberate position rather than a tidy-up. The old
inset drew one country's outline and therefore made a claim about that
country's extent, by inheritance rather than by choice. This one draws the
lines the source draws, names no country, fills no country, and excludes none.

What that means concretely, since a Chinese study region deserves it stated
rather than left to be inferred. The layer carries no Hong Kong and no Macau
feature at all, so neither is distinguished from Guangdong. Taiwan has no land
boundary and so appears only as a coastline in the hypsometric raster, exactly
as Hainan and Kyushu do. Natural Earth classes six of the 59 lines in the
extent as `Disputed (please verify)`, two as `Indefinite (please verify)`, two
as `Indeterminant frontier` and four as `Line of control (please verify)`, and
ships 34 per-country viewpoint fields, `FCLASS_CN` and `FCLASS_TW` among them,
which is the source's own statement that the classification depends on who is
asked. This repository takes no position on any of them and the caption says
so.

## How these were built

`scripts/fetch_copernicus_dem.py --download` fetches the 80 GLO-90 tiles into
the gitignored `data/raw/copernicus_dem/`, and
`scripts/build_map_reference.py --write` turns those and the Natural Earth
archives into everything above. Both are run once by hand and not by the
pipeline, on the same principle as `extract_reference_geometry.py`: a cache is
not a version and a download is not a record, so the committed file is the
source from here on. Sizes and checksums are in `data/manifest.json`.
