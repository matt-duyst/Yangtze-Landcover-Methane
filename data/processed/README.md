# Processed data

Small derived tables, committed. Every file here should be regenerable from
committed inputs by committed code. The one file currently present is not, and
that is stated plainly below rather than left to be discovered.

## rice_area_by_province.csv

Rice physical area for the four study provinces, one row per product, year and
province, with the 2023 thesis PPPM value alongside wherever the thesis covers
that year. Columns are source, year, province, rice_area_km2 and
thesis_pppm_km2. The thesis column is empty for 2019, 2020 and 2021, which the
thesis does not cover. Thirty-two rows: twenty-four from GloRice spanning 2000,
2010 and 2018 through 2021, and eight from SPAM covering 2000 and 2010.

The products are GloRice (I) physical area, Extensive variant, figshare version
2 of doi 10.6084/m9.figshare.27965832, and SPAM in two releases, the 2000 data
at version 3.0.7 from Harvard Dataverse doi 10.7910/DVN/A50I2T and the 2010 data
at version 2.0 from doi 10.7910/DVN/PRFF8V. In both products the layer used is
physical area rather than harvested area, because harvested area counts a
double-cropped paddy twice and cannot be interpreted as ground extent. In SPAM
the technology suffix is A, meaning all technologies together.

Both products are distributed on the same global 5-arcmin grid, 2160 by 4320
cells in EPSG:4326, with cell values already expressed as areas in hectares.
Provincial totals were formed by intersecting that grid with
data/reference/yrd_provinces.geojson and taking, for each cell, the fraction of
its area lying inside the province. Fractions were measured in China Albers
Equal Area, PROJ string +proj=aea +lat_1=25 +lat_2=47 +lat_0=0 +lon_0=105
+x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs, so that cells are weighted by true
ground area rather than by degrees, which would over-weight the north of the
study area. The projection is used only for the weights. It is never used to
measure the rice area itself, since the source values are already areas. Cell
values were then multiplied by their fractions, summed per province, and divided
by one hundred to convert hectares to square kilometres. The derivation is in
scripts/recon_rice_provincial_areas.py.

GloRice must not be read as an independent observation of rice extent. Its
authors state that the annual maps were produced by allocating national and
subnational agricultural statistics to grid cells within each administrative
unit, and that in consequence the mapped totals match the statistical totals so
closely that they saw no need to validate the totals at all. For China the
subnational source is the China Agriculture Yearbook. GloRice is therefore a
spatial redistribution of official Chinese statistics, and comparing it against
a PPPM estimate that was itself checked against Chinese sown-area statistics
compares two views of the same underlying numbers. It belongs here as a
comparison series and as a spatial prior, not as ground truth.

SPAM rows are included for completeness and are not used in analysis. The
decision to exclude them is recorded here in prose rather than by deleting the
numbers, so that the exclusion is visible and arguable rather than silent. SPAM
is a downscaling model: it disaggregates statistical totals to pixels, and its
own file documentation records a per-pixel annotation naming the source used for
scaling as the FAO 2004 to 2006 average. That is a reasonable basis for a global
product and a poor one for a provincial series in a single delta two decades
away from the scaling window. The output shows it. SPAM puts Anhui at roughly
half the thesis value in both years, 10,746 km2 against 19,651 for 2000 and
11,549 against 22,977 for 2010, and it has rice area falling between 2000 and
2010 in three of the four provinces, Shanghai, Zhejiang and Jiangsu. Whatever
the correct provincial trajectory is, a series with those properties cannot
carry weight at this scale.

These numbers are not yet reproducible from a fresh clone. There is no fetch
layer, so nothing in the repository can obtain the source rasters, and the
rasters themselves were deleted after extraction under a download budget. The
GloRice archive is recorded in data/manifest.json with a null checksum, because
none was computed before deletion; it must be recorded on re-fetch. SPAM is
absent from the manifest because it is not used in analysis. Making this file
reproducible is work that belongs with src/fetch/ and src/landcover/, and until
that exists these values should be read as reconnaissance results with a visible
derivation, not as pipeline output.
