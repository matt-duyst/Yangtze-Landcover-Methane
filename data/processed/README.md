# Processed data

Small derived tables, committed. Every file here should be regenerable from
committed inputs by committed code, and most rows now are: 148 of the 160 urban
rows and 28 of the 36 rice rows. Both tables regenerate from a clone with
nothing fetched, in four commands:

    python scripts/fetch_gaia.py --download
    python scripts/compute_urban_areas.py --write
    python scripts/fetch_glorice.py --download
    python scripts/compute_rice_areas.py --write

Each compute script compares against the committed values first, prints every
row differing by more than a tenth of a percent, and refuses to write when any
does. Run either without --write to compare and change nothing.

analysis_grid_2018.csv is the exception and regenerates all but one of its
columns; its section says which and why.

The rows that do not regenerate are named in each section below rather than
left to be discovered. Twelve urban rows need GADM, whose licence forbids
redistributing the boundary file, and eight rice rows need SPAM, for which no
fetch module exists. Both sets are carried forward unchanged when a table is
rewritten, and both scripts say so on every run.

## rice_area_by_province.csv

Rice physical area for the four study provinces, one row per product, year and
province, with the 2023 thesis PPPM value alongside wherever the thesis covers
that year. Columns are source, year, province, rice_area_km2 and
thesis_pppm_km2. The thesis column is empty for 2019, 2020 and 2021, which the
thesis does not cover. Thirty-six rows: twenty-eight from GloRice spanning
2000, 2010 and 2017 through 2021, and eight from SPAM covering 2000 and 2010.
The 2017 GloRice rows exist because 2017 is the first year of the NESDC rice
product, so the two are comparable from the start of their overlap.

The products are GloRice (I) physical area, Extensive variant, figshare version
2 of doi 10.6084/m9.figshare.27965832, published as Xie, H., Li, J., Li, T.,
Lu, X., Hu, Q., and Qin, Z. (2025), GloRice, a global rice database (v1.0): I.
Gridded paddy rice annual distribution from 1961 to 2021, Scientific Data 12,
182, doi:10.1038/s41597-025-04483-1, and SPAM in two releases, the 2000 data
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
by one hundred to convert hectares to square kilometres. That computation now
lives in src/landcover/, reached through scripts/compute_rice_areas.py;
scripts/recon_rice_provincial_areas.py is the superseded reconnaissance version
and is kept only as a record of how the committed numbers were first produced.

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

All twenty-eight GloRice rows regenerate. scripts/fetch_glorice.py --download
obtains the inputs, reading the DOI and the seven years from
config/sources.yml, verifying the archive against the MD5 figshare publishes,
extracting only those years and deleting the 148 MB archive afterwards.
scripts/compute_rice_areas.py then recomputes the rows from data/raw/glorice/
and data/reference/yrd_provinces.geojson, reporting any row differing from the
committed value by more than a tenth of a percent and writing nothing; --write
regenerates the file and refuses if anything differs. On the run that produced
the current table all twenty-four rows that already existed matched to within a
tenth of a percent and the four 2017 rows were added.

One thing about the method is worth stating because it differs from the urban
table. GloRice is not a categorical raster, so the computation uses
zonal_value_sum rather than zonal_area: cells hold hectares of rice, and at 5
arcmin a cell is roughly 9 km across, so each is apportioned by the fraction
lying inside the province rather than taken or dropped whole.

The eight SPAM rows do not regenerate and cannot be made to. There is no SPAM
fetch module, and the 2020 release sits behind a Dataverse guestbook form that
cannot be scripted; the 2000 and 2010 releases used here are anonymously
reachable, so this is a gap in the code rather than a hard barrier, but it is a
gap. Those rows are carried forward unchanged whenever the table is rewritten,
and the script says so each time it runs rather than letting them look
recomputed.

## urban_area_by_province.csv

Cumulative impervious area for the four study provinces from GAIA, with the
2023 thesis urban extent alongside wherever the thesis covers that year.
Columns are source, year, province, urban_area_km2, boundary and
thesis_urban_km2. One hundred and sixty rows: twelve under the GADM boundary
for 2000, 2010 and 2018, and the full annual series 1985 to 2021 under the
Natural Earth boundary, which already contains the twelve Natural Earth values
for those years. The thesis column is empty for the thirty-four years the
thesis does not cover.

The release used is GAIA as distributed on figshare at
doi:10.6084/m9.figshare.27245775.v1, licence CC BY 4.0. The archive is named
GAIA_1985_2022.zip and its readme is headed Version 2022, but the data stops at
2021: the readme's own temporal line reads 1985 to 2021, and the newest value
in the encoding decodes to 2021.

GAIA stores the year a pixel first became impervious, not extent per year, so
extent is recovered by thresholding. Year equals 2023 minus value, running
downward from the newest year, and cumulative extent for a year is value
greater than or equal to 2023 minus that year. The cutoffs used here are 23 for
2000, 13 for 2010 and 5 for 2018.

Nodata is minus 128, and the product readme documents no nodata at all: it
states only that values are 0 and 2 through 38. Value 1 is never used, across
the 3,105,244,301 pixels of the nine tiles checked. All 14,091 nodata pixels
fall outside the four provinces, so no provincial figure in this file is
affected by fill handling, but code written against the readme alone would not
know the fill existed.

GAIA ships its tiles with a 30 m merge buffer so that neighbours can be
mosaicked seamlessly, which means adjacent tiles overlap. Pixels were therefore
clipped by pixel centre to each tile's nominal five-degree extent before
counting. Without that clipping the nine tiles double-count their overlaps
along every shared edge.

Each pixel was weighted by its true ground area rather than counted, using the
exact equal-area cell area for its row on the authalic sphere. Summing those
weights over each province mask recovers the polygon area to within 0.13
percent, the residual being pixel-centre rasterisation at the boundary, which
is the validation that the weighting and the clipping are both right.

GADM 4.1 values are included as a boundary sensitivity check and not as a
second estimate. GADM itself cannot be committed, because its licence forbids
redistribution without permission, so it served as a check and nothing derived
from its geometry is stored here. Boundary choice moved two Zhejiang values by
more than 2 percent, 2000 by 2.87 percent and 2010 by 2.30 percent, because
GADM resolves 732 island parts against Natural Earth's 17 and those islands
carry urban pixels. Landlocked Anhui moved by under 0.3 percent in every year.

On the comparison with the thesis, no year reproduces at the provincial level.
For 2018 the thesis exceeds GAIA in Shanghai by 1,687 km2 and in Zhejiang by
3,481 km2, and falls short in Anhui by 1,352 km2 and in Jiangsu by 3,439 km2,
netting 377 km2. The four-province total therefore agrees to 0.8 percent, but
that agreement is the result of offsetting errors of one to three thousand
square kilometres in each direction and should not be read as agreement.

Two of the twelve thesis values cannot be produced by this release at any
cutoff. The thesis 2018 figures for Shanghai and Zhejiang exceed the total
impervious area GAIA records in those provinces through 2021, which is 3,567
km2 for Shanghai and 12,630 km2 for Zhejiang. No threshold reaches them because
the thesis value is larger than the whole product.

The Shanghai case is worth stating in fractions. The thesis 2018 value of 5,121
km2 implies that between 74 and 81 percent of the municipality is impervious,
depending on which boundary source supplies the denominator: 75.9 percent
against Natural Earth, 74.4 percent against GADM, and 80.8 percent against the
published provincial area. GAIA gives 51 percent. A figure in that range is a
reason to question the provincial masks used in 2023 rather than the product.

Fitting the relationship the other way does not rescue it. Searching for the
cutoff that best reproduces each thesis value gives offsets against the correct
cutoff scattered from minus 6 to plus 14, with a mean of plus 4.20 and a
standard deviation of 5.88. The offset varies with year within a province and
reverses sign between provinces, decreasing from plus 11 to plus 3 across Anhui
and from plus 14 to plus 4 across Jiangsu while running minus 1 to minus 6 in
Shanghai. No single decoding convention, and no single scale factor, relates
the thesis table to this release.

One feature of the series should be weighed before any year after 2016 is used.
Year-on-year growth of the four-province total runs between 7.1 and 10.5 percent
across 2011 to 2016, then drops to between 1.9 and 2.6 percent from 2017
onward, and value 7, which decodes to 2016, carries the largest single-year
pixel share at 7.60 percent. That break coincides with the end of the original
1985 to 2018 release period, and the 2017 to 2021 extension may not be
comparable with the earlier years.

The hundred and forty-eight Natural Earth rows now regenerate from committed
inputs. Running scripts/compute_urban_areas.py with no arguments recomputes the
whole 1985 to 2021 series from data/raw/gaia/ and
data/reference/yrd_provinces.geojson, mosaicking the nine tiles with each
tile's nominal five-degree extent as a clip so the merge buffers are not
double-counted, and reports any row differing from the committed value by more
than a tenth of a percent; --write regenerates the file and refuses if anything
differs. As of this commit every one of the hundred and forty-eight matches to
better than one part in ten million.

The nine GAIA tiles are not committed and are fetched by
scripts/fetch_gaia.py --download, which reads the DOI and the nine tile names
from config/sources.yml, verifies the archive against the MD5 figshare
publishes, extracts only those nine members, deletes the 2.3 GB archive, and
records the archive's sha256 and each tile's in data/manifest.json. Extraction
goes to a staging directory and the tiles are hashed there and checked against
the digests already recorded before anything is moved into place, so a changed
distribution is reported rather than silently replacing verified files. On the
run that produced the current manifest all nine matched the digests from the
earlier manual extraction exactly, and the archive's sha256, which had been
null because the archive was deleted before one was computed, was filled in.

One property of the route is unavoidable and worth knowing before running it:
the archive is not internally addressable, so obtaining any single tile means
downloading all 2,302,456,975 bytes of it. The nine tiles that come out total
265 MB.

The twelve GADM rows cannot be regenerated from committed inputs and never
will be. GADM 4.1's licence forbids redistribution without permission, so the
boundary file cannot be committed here. Supplying your own copy with --gadm
recomputes them; without it the script carries them forward unchanged and says
so, so they are never mistaken for recomputed values. They are a boundary
sensitivity check rather than a second estimate, and nothing else in the
project depends on them.

## methane_composite_2018.tif and methane_coverage_2018.csv

Gridded TROPOMI methane over the study box for 2018, at 0.25 degrees, which is
33 by 31 cells. The raster carries three bands in one file rather than three
files, because the three arrays share one grid and have to be read together: a
mean without its sounding count is the thing src/methane exists to prevent, and
separate files invite reading one without the other. Band one is the
bias-corrected mean in ppb, band two the raw mean, band three the sounding
count. Everything is float32, counts included, since the largest count observed
is 410 and is exact in float32. Unobserved cells are NaN in bands one and two
and zero in band three, so the two encode the same fact and neither can be read
without the other contradicting it. The CSV holds one row per cell for all
1,023 cells, not only the populated ones, with centre latitude and longitude,
sounding count and both means; an unobserved cell has a zero count and blank
means.

The route is the anonymous MEEO S3 mirror at meeo-s5p.s3.amazonaws.com, which
serves the operational Sentinel-5P products over plain HTTPS with no
credentials. Copernicus Data Space carries the same granules but requires
authentication to download and so cannot run from a fresh clone. The mirror
publishes no usable content checksum: every S3 ETag observed is a multipart tag
with a minus-N suffix, which is an MD5 of the part MD5s rather than of the
object, and the part size is not published. Verification is therefore
structural, that the file opens as netCDF4 and holds a PRODUCT group with the
expected variables, and that is weaker than the MD5 verification the figshare
and Science Data Bank routes get. It catches a truncated body or an error page
served with HTTP 200; it would not catch a silently corrupted granule.

The stream is RPRO, the reprocessed one, which for 2018 is homogeneous at
processor version 020400. OFFL was not used for this year because it holds only
34 days of 2018 against RPRO's 246, and because its early-period granules sit
at processor version 010202, a different version family; mixing the two would
pool two reconstructions of the same record with no way afterwards to attribute
a cell to a released version. The stream table for every year is in
notes/decisions.md.

Every orbit is published more than once. A listing of 2018 returns 6,390 keys
for 3,437 distinct orbits, the same overpass at more than one processor
version. Only the highest version of each orbit is kept. Gridding both would
have counted the same soundings twice, inflating the per-cell counts and
biasing the mean toward whichever overpasses happen to be duplicated.

Candidate granules are chosen by orbital geometry rather than by footprint,
because a filename encodes an orbit number and a UTC time window and carries no
geographic extent at all. Sentinel-5P is sun-synchronous with a 13:30 local
descending node, so UTC is local time minus longitude over fifteen, which puts
the study box under the satellite at about 05:19 to 05:50 UTC. That window,
widened by 55 minutes for swath width and neighbouring orbits, selects 578 of
the 3,437 deduplicated granules. This is a superset and not an exact test:
whether the swath actually reached the box is knowable only from the granule's
own latitude and longitude arrays, after downloading it.

The quality threshold is 0.75. The recommended value is 0.5, and in this region
the two select identical soundings because qa_value is quantised to its top bin
here, so 0.75 costs nothing and is the stricter statement. qa_value is stored
as uint8 with a scale factor of 0.01, so the comparison is made in stored units
against 75; comparing the float 0.75 against the raw array would keep every
sounding. Fill values are read from each variable's own _FillValue attribute
and never assumed, which matters because the same code must not depend on
whether netCDF4, h5py or xarray opened the file.

The yield for 2018 was 578 candidate granules, of which 222 carried any
in-box sounding and 356 carried none. Those 222 gave 110,928 soundings, which
covered 927 of the 1,023 cells, 90.62 percent, with a median of 75 soundings
per covered cell and a maximum of 410. That is far more than an earlier
36-granule sample suggested, for reasons recorded in notes/decisions.md.

January through March are absent because the data does not exist. The public L2
CH4 record begins on 2018-04-30, and listings for 15 January, 15 February, 15
March and 15 April 2018 return a key count of zero in both RPRO and OFFL. 2018
is therefore an eight-month year for this product, and the composite describes
the days that exist rather than the calendar year.

Yield is strongly seasonal and runs against granule availability. June, July
and August give 4.6 to 5.0 percent of the year's soundings each despite
carrying the most granules, because the monsoon clouds them. October alone
gives 30.8 percent. Autumn and winter together carry 75.5 percent of the year's
soundings from 44 percent of its granules. Any analysis that treats the
composite as an annual mean is weighting autumn far above summer, and the
per-cell counts are what make that visible.

Both methane variables are provided because the choice between them is
substantive. The bias correction adds 11.64 ppb on average, ranging from plus
3.42 to plus 29.05, and it differs in all 927 covered cells. Its 25.6 ppb
spread across cells is nearly twice the field's own standard deviation of 14.9
ppb, so the correction is not a constant offset that cancels in a comparison.

The 96 uncovered cells are a coherent systematic gap, not scatter. Just under
half of them, 47 cells, form a single connected block spanning 26.95 to 28.95
north and 118.05 to 121.30 east, the mountainous interior of southern Zhejiang,
which is 95 percent land. Ocean is not the explanation for the gap in presence
terms: the mean ocean fraction of uncovered cells, 0.151, is lower than that of
covered cells, 0.204. Water shows up in the counts instead of in the coverage.
Cells that are 25 to 99 percent sea, which is to say the coastline, have a
median of 2 to 3 soundings and are uncovered 24 percent of the time, against a
median of 108 and 9.8 percent for pure-land cells and 26.5 and 2.6 percent for
open sea. A single retained granule gives consistent, weak support for the
albedo mechanism: soundings falling in cells that the annual composite never
covered have a median surface_albedo_SWIR of 0.0161 against 0.0673 for
soundings in covered cells, a factor of 4.2, though on only twelve soundings in
the uncovered group. Those cells should be reported as missing and excluded
from any model that consumes this field. They should not be interpolated: the
gap is where the instrument systematically fails, so an interpolated value
there would be an extrapolation from brighter, flatter terrain into darker,
steeper terrain, and it would carry no warning that it had been invented.

Regenerating this costs a 28.9 GB download and about 64 minutes at the observed
7.8 MB/s. The command is scripts/compute_methane_composite.py with --run, a
granule cap and a date range; it streams one granule at a time, gridding and
deleting each before fetching the next, so peak disk is one granule rather than
the 28.9 GB the year would otherwise need. Exporting the raster and the table
from an existing checkpoint costs nothing and is the --export flag.

## analysis_grid_2018.csv

One row is one covered methane cell of the 2018 composite at 0.25 degrees.
There are 927 of them and fifteen columns. `centre_lat` and `centre_lon` place
the cell; `sounding_count`, `ch4_bias_corrected_ppb` and `ch4_raw_ppb` come
straight from methane_composite_2018.tif; `impervious_fraction`,
`rice_fraction_single` and `rice_fraction_combined` are the land-cover
fractions; `impervious_coverage` and `rice_coverage` say how much of the cell
each fraction rests on; and `province_share_outside` together with four
`share_<province>` columns gives the cell's area split between the four study
provinces and everything else. Built by scripts/build_analysis_grid.py.

The lattice is slightly smaller than the box the configuration declares, and
the difference matters at the eastern edge. The declared box runs from 114.8 to
122.6 east, which is 31.2 columns at 0.25 degrees, and the grid rounds that to
31. The easternmost cell therefore ends at 122.55 and the last 0.05 degrees of
the declared box has no column at all. Land-cover pixels that fall in that strip
are filtered out rather than clipped into column 30. Clipping is what
`GridSpec.cell_of` does to soundings, but it is wrong for area: a pixel outside
the lattice belongs to no cell, and folding it into the edge cell would inflate
that cell's assessed area with ground the cell does not cover, which would then
appear in the denominator of its fraction. The same rounding applies to the
southern edge, where 33 rows reach 26.95 rather than the declared 27.0.

The 96 cells that received no soundings are absent from the table rather than
present and blank. That is enforced by construction: `CellRow` takes the
sounding count as a required field and refuses to build a row when it is zero,
so an uncovered cell cannot be created and then filtered out by a step someone
later forgets. The gap is a coherent one over mountainous southern Zhejiang and
along the coastline rather than scatter, and interpolating across it would
extrapolate from bright flat terrain into dark steep terrain where the
instrument is known to fail.

The two fractions do not share a denominator, and the two coverage columns are
what say so. Rice is masked by the province each raster is named for. Its zero
is ambiguous: the rasters declare no nodata, so a zero pixel means both genuine
non-rice land and out-of-province background, and an unmasked rice fraction is
wrong by roughly a factor of two. The mask has to be the individual province
rather than the union of the four, because the distributed rasters come one per
province and their bounding boxes overlap. GAIA is left unmasked. It is a global
product whose zero means non-urban everywhere, including over sea, so masking it
to the four provinces would quietly change impervious fraction from a share of
the cell into a share of the provincial land in the cell. The consequence is
visible in the coverage columns: impervious coverage exceeds 0.99 in all 927
rows, while rice coverage has a median of 0.335 and falls below 0.99 in 570.
Comparing the two fractions within a cell compares a share of the whole cell
against a share of the provincial land in it, and that has to be read with the
coverage alongside.

The union mask was tried first and was wrong in an instructive way, so it is
recorded rather than quietly fixed. Masking all four rice rasters by the union
of the four provinces let each file assess the ground it shared with its
neighbours, so overlapping ground was counted once per file that saw it. One
cell finished with an assessed area 2.94 times its own, which is arithmetically
impossible and is what exposed the error, and the median single-season fraction
came out at 0.079 against a correct 0.129. Both the numerator and the
denominator were inflated, so the fraction was wrong without any single number
looking obviously wrong except the coverage.

A blank rice fraction means no rice raster reached that cell, which is not the
same as a cell with no rice. There are 395 such rows. In 368 of them the cell
lies outside all four provinces entirely. The other 27 lie inside Anhui, and 11
of those lie wholly inside it, because the 2018 Anhui raster stops at 33.3462
north and 115.2682 east while the province does not. That reproduces the
clipping finding recorded in notes/decisions.md from the opposite direction and
without being looked for, and it shows both edges rather than only the northern
one. Those cells are blank rather than zero for the same reason the 96
uncovered cells are absent: nobody looked there, and an absence of observation
is not an observation of absence.

The rice columns come from the National Ecosystem Science Data Center rasters
obtained over FTP, which carry the double-season class the Science Data Bank
export does not. That route needed a personal-use grant and is deliberately not
scripted, so the file is not fully regenerable from a clone. The cost is one
column rather than the table. For 2018 the two products are the same
classification: identical transforms, shapes, CRS, nodata and dtypes, identical
single-season pixel counts in all four provinces, and a Science Data Bank zero
count equal to the FTP zero count plus the FTP double-season count exactly. The
Science Data Bank export is the same classification with the double-season class
folded back into the background. Building the grid from each source and
differencing the tables, the only column that differs is
`rice_fraction_combined`, in 190 of the 927 rows, by at most 0.164 and by 0.022
on average where it differs. Every other column is byte-identical, so a reader
with no grant regenerates all but one column exactly. notes/decisions.md carries
the pixel counts that establish this, and the equality was checked for 2018 only.

For the distributions as built: impervious fraction is present in all 927 rows
with a minimum of 0.0000, a median of 0.0595, a maximum of 0.8192 and 136 exact
zeros. Single-season rice fraction is present in 532 rows with a minimum of
0.0000, a median of 0.1289, a maximum of 0.5480 and 18 exact zeros. Combined
rice fraction is present in the same 532 rows with a median of 0.1363 and the
same minimum and maximum. Impervious coverage runs from 0.9986 to 1.0007 with a
median of 0.9996 and no row below 0.99; the excess above 1.0 is pixel-centre
quantisation, since a 30 m grid does not divide a 0.25 degree cell evenly and a
cell gains or loses up to about one pixel row. Rice coverage runs from 0.0000 to
1.0002 with a median of 0.3354 and 570 rows below 0.99. Of the 927 cells, 69
straddle more than one province, 544 are partly outside all four and 368 are
entirely outside all four. A reader counting the file will find 370 rather than
368 with every province share at zero, because the share columns are written to
four decimal places and two cells hold a provincial sliver below 0.00005 of
their area. The figure of 368 is what the intersection actually found; 370 is
what the file can express.

To regenerate every column except `rice_fraction_combined`, from a clone with
nothing fetched:

    python scripts/fetch_rice.py --download
    python scripts/fetch_gaia.py --download
    python scripts/build_analysis_grid.py --rice-source scidb --write

Reproducing `rice_fraction_combined` as committed additionally requires the FTP
rasters in data/raw/nesdc_rice/ and `--rice-source nesdc`, which is the form the
committed file was built with.

The correlations the build script prints are descriptive and are not a model.
Cells are contiguous and so are not independent observations, the two fractions
have different denominators, and the 96 excluded cells are a terrain-driven gap
rather than a random sample. Nothing causal follows from them. What must be
beaten before any of it means anything is in data/processed/baseline_results_2018.csv.

## baseline_results_2018.csv

What a model of this study's question has to beat, established before there is
a model with an interest in where the bar sits. Forty-eight rows: twelve models,
each under two held-out schemes at two weightings. Written by
scripts/run_baselines.py, which reads only analysis_grid_2018.csv.

Each row carries the model, the scheme, the weighting, the number of cells it
ran on, how many it dropped for a missing predictor, in-sample RMSE and R
squared, held-out RMSE and R squared, and a detail column holding the fitted
coefficients for a linear model or the number of fallbacks for the spatial null.
Errors are in ppb. The `dropped_missing` column counts rows removed from what
the model was asked for, so it is 395 for a rice model offered the whole grid
and 0 for one offered only the 532 cells that have a rice fraction, even though
both end up running on 532. The `n` column is what to compare on.

Sample sizes differ and the metrics are not comparable across them. Any model
naming rice runs on the 532 cells that have a rice fraction; the constants, the
spatial null and the impervious-only model could run on all 927. Every null is
therefore run twice, once on each sample, and a model is only ever compared
against a null fitted on the same rows. The 395 cells without rice are not a
random slice: they are disproportionately coastal and outside the four
provinces, so dropping them removes part of the field's spread rather than a
sample of it.

Evaluation is spatial and never random. Cells are contiguous and neighbouring
cells are not independent, so a random split puts a cell's own neighbours in
training and every model scores well by memorising the field. Leave-one-province
-out holds out each of the four provinces and, as a fifth fold, the cells inside
the bounding box but outside all four; it asks whether a relationship learned in
three provinces transfers to a fourth, which is the claim a land-cover model
implicitly makes. Spatial blocks hold out one-degree squares of the lattice,
four cells on a side, assigned to five folds by a seeded permutation so no fold
is entirely coastal or entirely inland. Held-out metrics pool every held-out
prediction and score once rather than averaging fold metrics, which would weight
a fold of 13 cells equally with a fold of 370.

Two properties of the table look like errors and are not. The global and
per-province constants have identical held-out numbers under
leave-one-province-out, because the held-out province is by construction the
group with no training data and the per-province constant falls back to the
global mean for every held-out cell; that scheme cannot evaluate a per-province
null. And R squared is frequently negative out of sample, because it is measured
against the evaluation set's own weighted mean, so a model predicting the
training mean scores below zero whenever the held-out region sits away from the
overall mean. Below zero is informative rather than broken.

Both weightings are reported and neither is chosen for the reader. A cell's
value is the mean of between 1 and 410 soundings, so its variance is roughly
sigma squared over n and the inverse-variance weight is the sounding count
itself; on that argument the weighted numbers are the ones to fit on. But
sounding count is not random over the study area, and the well-observed cells
are systematically the flat bright ones the instrument retrieves from, so
weighting also tilts every fit towards that terrain. The weighted errors are
roughly half the unweighted ones throughout, which is the size of that effect
and not an improvement in any model.

    python scripts/run_baselines.py --write

## methane_covariates_2018.tif and methane_covariates_2018.csv

Seven Sentinel-5P support-data fields gridded on exactly the same 33 by 31
lattice as the methane composite, from exactly the same 578 granules: the two
wind components, the two surface albedos, solar zenith angle, surface altitude
and surface pressure. Written by scripts/compute_methane_composite.py with
--export-covariates.

A companion file rather than extra bands on methane_composite_2018.tif, and the
reason is the point of the whole covariate exercise. That file's third band is
the sounding count, and a reader who found fifteen bands in it would reasonably
divide any of them by that band. A covariate is valid on its own subset of
soundings, so that division can be wrong by an arbitrary factor and still look
sensible. Here each covariate's mean band is immediately followed by its own
count band, fourteen bands in all, and the file contains no count belonging to
anything else. Leaving the methane composite untouched also keeps the
reproduction check below meaningful.

The methane grids were verified cell by cell against the committed composite
before anything here was written. Maximum absolute difference is 0 for
bias-corrected methane, 0 for raw methane and 0 for the sounding counts, over
all 1,023 cells, with 927 covered and 110,928 soundings on both sides. The
re-run reproduces the committed composite exactly rather than approximately.

Covariates do not gate a sounding. A sounding with no valid albedo still
contributes its methane, and folding albedo into the validity mask would have
been a one-word change that silently discarded most of the record. All seven
turn out to be valid on 110,928 of 110,928 soundings and to cover all 927 cells,
so in this composite every covariate count equals the sounding count. That is
not a licence to divide by the wrong one: it is a fact about 2018 at qa 0.75,
not a property of the product, and the count bands are there so a future year
does not have to assume it.

Reconnaissance had measured valid surface_albedo_SWIR on only 3.4 percent of
in-box soundings, which is correct and does not apply after quality filtering:
albedo is written where the retrieval got far enough, and qa_value >= 0.75
selects those same soundings. notes/decisions.md carries the argument.

Annual means over the 927 covered cells, for orientation:

| field | min | median | max |
|-------|-----|--------|-----|
| eastward_wind, m/s | -5.6341 | 0.0305 | 3.6959 |
| northward_wind, m/s | -5.4241 | -0.8553 | 10.4711 |
| surface_albedo_SWIR | -0.0480 | 0.0773 | 0.1566 |
| surface_albedo_NIR | -0.0072 | 0.2178 | 0.3051 |
| solar_zenith_angle, degrees | 12.6857 | 42.3981 | 56.6597 |
| surface_altitude, m | 0.0000 | 35.3966 | 1041.0800 |
| surface_pressure, Pa | 89950.4 | 101161.0 | 102642.0 |

Surface albedo is negative in 167 of the 927 cells. That is not a fill value
leaking through; it is a fitted retrieval parameter rather than a measured
reflectance, and over dark surfaces the fit can land below zero. Those cells are
kept, because dropping them would remove 18 percent of the grid non-randomly and
from exactly the dark surfaces the confounder test is about.

An unmeasured covariate is blank in the CSV and NaN in the raster, never zero,
and its count band is 0. Regenerating costs the same 28.9 GB download and 66
minutes as the methane composite, since it is the same pass over the same
granules:

    python scripts/compute_methane_composite.py --run --max-hours 3 \
        --checkpoint data/interim/covariates_2018.npz
    python scripts/compute_methane_composite.py \
        --checkpoint data/interim/covariates_2018.npz \
        --verify-against data/processed/methane_composite_2018.tif \
        --export-covariates data/processed/methane_covariates_2018

## albedo_confounder_2018.csv

Whether the land-cover signal in the methane field is a retrieval artefact.
Twenty-six rows: thirteen relationships under each of the two weightings.
Written by scripts/test_albedo_confounder.py. Columns are the weighting, the
relationship, what was controlled for if anything, the sample size, and Pearson
and Spearman with their p-values.

TROPOMI's methane retrieval needs light back from the surface, so it works
better over bright ground; the literature reports a seasonal surface-albedo bias
in TROPOMI methane over agricultural land; and rice paddies flood, which moves
their albedo on the same seasonal cycle as their methane. Cities are bright and
dry year round. So albedo is plausibly connected to both the land cover and the
retrieved value, which is the shape of a confounder rather than a nuisance.

Both legs are open and the conclusion is negative. Albedo is more strongly
associated with the methane field than either land-cover fraction is, and once
it is partialled out of both sides the land-cover association is not
distinguishable from zero, under both weightings. notes/decisions.md carries the
numbers and, more importantly, the limits: albedo and impervious fraction are
collinear at Spearman +0.761, so controlling for one removes real variation in
the other. The result is that the two cannot be separated in this data, not that
the land-cover signal has been shown to be false.

Partial correlation here is the residual method: both variables are regressed on
the control and the residuals correlated, with the variables rank transformed
first for the Spearman form. A row's controlled association is computed on
exactly the cells its raw association used, and a test pins that.

    python scripts/test_albedo_confounder.py --write
