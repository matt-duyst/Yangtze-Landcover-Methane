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
