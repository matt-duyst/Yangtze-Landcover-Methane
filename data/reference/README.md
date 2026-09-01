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

The Shanghai discrepancy is the one to watch. It is most likely a matter of
boundary treatment rather than error, since Shanghai's extent depends on how
reclaimed land along the estuary and the whole of Chongming Island are handled,
and different sources draw those differently at different dates. The Jiangsu
shortfall may have a related cause along the same coast. Neither has been run
down. Before provincial areas are used as denominators, for an impervious
fraction or a rice fraction or anything else normalised by land area, these
boundaries should be cross-checked against a second source, because a 6 percent
error in the denominator is larger than several of the differences this project
is trying to measure.

One further caution about reproducibility. The exact Natural Earth release
bundled in the cartopy cache is not recorded anywhere in the shapefile, so the
manifest entry describes where the file came from rather than naming a version
number. A future re-extraction from a different Natural Earth release could
yield slightly different geometries and therefore slightly different areas.
