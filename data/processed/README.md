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

The yield for 2018 was 578 candidate granules, of which 223 carried any
in-box sounding and 355 carried none. Those 223 gave 110,920 soundings, which
covered 926 of the 1,023 cells, 90.52 percent, with a median of 74 soundings
per covered cell and a maximum of 410.

These figures moved when the declared box was reconciled with the lattice
extent. They were 222 granules, 110,928 soundings, 927 cells, 90.62 percent and
a median of 75 before that. The change is +151 soundings gained in the southern
row that had been discarded and -159 removed from the eastern column that had
been clipped in, over 49 cells; see notes/decisions.md. That is far more than an earlier
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
3.42 to plus 29.05, and it differs in all 926<!--#composite.covered_cells--> covered cells. Its 25.6 ppb
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
There are 926<!--#grid.rows--> of them and fifteen columns. `centre_lat` and `centre_lon` place
the cell; `sounding_count`, `ch4_bias_corrected_ppb` and `ch4_raw_ppb` come
straight from methane_composite_2018.tif; `impervious_fraction`,
`rice_fraction_single` and `rice_fraction_combined` are the land-cover
fractions; `impervious_coverage` and `rice_coverage` say how much of the cell
each fraction rests on; and `province_share_outside` together with four
`share_<province>` columns gives the cell's area split between the four study
provinces and everything else. Built by scripts/build_analysis_grid.py.

The lattice and the declared box are now the same region, and this paragraph
records that they were not, because the discrepancy reached the data.

**What was true until the extent was reconciled.** The box was declared as
114.8 to 122.6 east and 27.0 to 35.2 north. That is 31.2 columns and 32.8 rows
at 0.25 degrees, which `GridSpec` rounded to 31 and 33 -- **down on one axis and
up on the other**. The lattice therefore ended at 122.55, short of the declared
east edge, and at 26.95, past the declared south edge.

Land-cover pixels in the eastern strip were filtered out rather than clipped
into column 30, which was correct: a pixel outside the lattice belongs to no
cell, and folding it into the edge cell would inflate that cell's assessed area
with ground the cell does not cover, which would then appear in the denominator
of its fraction. But `GridSpec.cell_of` clipped soundings rather than filtering
them, and it tested them against the declared box rather than the lattice. So
soundings between 122.55 and 122.6 east were accepted and folded into column 30,
and soundings between 26.95 and 27.0 north were discarded although cells existed
there. The two statements in this paragraph -- that the lattice stops short in
longitude and runs long in latitude, and that `cell_of` clips -- were each
correct and were written three lines apart; their conjunction was the bug.

**What is true now.** `config/sources.yml` declares 26.95 and 122.55, so the
declared box is exactly the lattice, `cell_of` filters correctly against it, and
its clipping path is unreachable for any real coordinate. `lattice_edges` is
still called everywhere because nothing enforces that a future box or cell size
divides evenly. `tests/test_study_extent.py` asserts the two agree, with both
sides derived. The 2018 composite was rebuilt against the corrected extent; see
`notes/decisions.md` for what changed.

The 96 cells that received no soundings are absent from the table rather than
present and blank. That is enforced by construction: `CellRow` takes the
sounding count as a required field and refuses to build a row when it is zero,
so an uncovered cell cannot be created and then filtered out by a step someone
later forgets. The gap is a coherent one over mountainous southern Zhejiang and
along the coastline rather than scatter, which is our own measurement and is
visible in the composite. Interpolating across it would extrapolate from the
terrain that was observed into terrain that was not, and low-albedo scenes are
among the hardest for this retrieval (Lorente et al., 2021,
doi:10.5194/amt-14-665-2021). That the failure is specifically a function of
slope is not claimed here; only the albedo half is sourced.

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
visible in the coverage columns: impervious coverage exceeds 0.99 in all 926
rows, while rice coverage has a median of 0.341 and falls below 0.99 in 569.
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
`rice_fraction_combined`, in 190 of the 926 rows, by at most 0.164 and by 0.022
on average where it differs. Every other column is byte-identical, so a reader
with no grant regenerates all but one column exactly. notes/decisions.md carries
the pixel counts that establish this, and the equality was checked for 2018 only.

For the distributions as built: impervious fraction is present in all 926<!--#grid.rows--> rows
with a minimum of 0.0000, a median of 0.0595<!--#grid.impervious_median-->, a maximum of 0.8192 and 136<!--#grid.impervious_zeros--> exact
zeros. Single-season rice fraction is present in 531<!--#grid.rice_rows--> rows with a minimum of
0.0000, a median of 0.1291<!--#grid.rice_single_median-->, a maximum of 0.5480 and 18 exact zeros. Combined
rice fraction is present in the same 531 rows with a median of 0.1366<!--#grid.rice_combined_median--> and the
same minimum and maximum. Impervious coverage runs from 0.9986 to 1.0007 with a
median of 0.9996 and no row below 0.99; the excess above 1.0 is pixel-centre
quantisation, since a 30 m grid does not divide a 0.25 degree cell evenly and a
cell gains or loses up to about one pixel row. Rice coverage runs from 0.0000 to
1.0002 with a median of 0.3412<!--#grid.rice_coverage_median--> and 569<!--#grid.rice_coverage_below_99--> rows below 0.99. Of the 926 cells, 69<!--#grid.straddling_cells-->
straddle more than one province, 543 are partly outside all four and 368 are
entirely outside all four. A reader counting the file will find 370<!--#grid.cells_outside_in_file--> rather than
368 with every province share at zero, because the share columns are written to
four decimal places and two cells hold a provincial sliver below 0.00005 of
their area. The figure of 368 is what the intersection actually found; 370 is
what the file can express.

To regenerate every column except `rice_fraction_combined`, from a clone with
nothing fetched:

    python scripts/fetch_rice.py --download
    python scripts/fetch_gaia.py --download
    python scripts/build_analysis_grid.py --rice-source nesdc --write

`--rice-source nesdc` is what the committed table was built with, and it needs
the FTP rasters. A reader without that grant should use `--rice-source scidb`,
which reproduces every column exactly except `rice_fraction_combined`, in 190
rows, each of them lower because the anonymous product is single-season only.
Substituting scidb silently produces a plausible table, so the choice is worth
making deliberately.

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
and 0 for one offered only the 531 cells that have a rice fraction, even though
both end up running on 531. The `n` column is what to compare on.

Sample sizes differ and the metrics are not comparable across them. Any model
naming rice runs on the 531<!--#grid.rice_rows--> cells that have a rice fraction; the constants, the
spatial null and the impervious-only model could run on all 926. Every null is
therefore run twice, once on each sample, and a model is only ever compared
against a null fitted on the same rows. The 395 cells without rice are not a
random slice: they are disproportionately coastal and outside the four
provinces, so dropping them removes part of the field's spread rather than a
sample of it.

Evaluation is spatial and never random. Cells are contiguous and neighbouring
cells are not independent, so a random split puts a cell's own neighbours in
training and every model scores well by memorising the field. That is the
standard argument for blocked cross-validation (Roberts et al., 2017, Ecography
40, 913-929, doi:10.1111/ecog.02881), and the block size follows the measured
autocorrelation range as Valavi et al. (2019, Methods in Ecology and Evolution
10, 225-232, doi:10.1111/2041-210X.13107) prescribe: the methane field's
half-sill range is 102 km and a four-cell block is about 111 km across. Neither
scheme here buffers the seam between blocks; `notes/decisions.md` records why
that should if anything raise the bar rather than lower it. Leave-one-province
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
all 1,023 cells, with 926 covered and 110,920 soundings on both sides. The
re-run reproduces the committed composite exactly rather than approximately.

That check was re-established after the extent reconciliation. Against the
*previous* composite it deliberately does not hold: 49 cells changed, all of
them in the southernmost row or the easternmost column, with a maximum absolute
difference of 5.44 ppb in bias-corrected methane. Reproducing the superseded
composite is not the goal; reproducing the current one is.

Covariates do not gate a sounding. A sounding with no valid albedo still
contributes its methane, and folding albedo into the validity mask would have
been a one-word change that silently discarded most of the record. All seven
turn out to be valid on 110,920 of 110,920 soundings and to cover all 926 cells,
so in this composite every covariate count equals the sounding count. That is
not a licence to divide by the wrong one: it is a fact about 2018 at qa 0.75,
not a property of the product, and the count bands are there so a future year
does not have to assume it.

Reconnaissance had measured valid surface_albedo_SWIR on only 3.4 percent of
in-box soundings, which is correct and does not apply after quality filtering:
albedo is written where the retrieval got far enough, and qa_value >= 0.75
selects those same soundings. notes/decisions.md carries the argument.

Annual means over the 926<!--#cov.rows--> covered cells, for orientation:

| field | min | median | max |
|-------|-----|--------|-----|
| eastward_wind, m/s | -5.6341 | 0.0310<!--#cov.eastward_wind_median--> | 3.6959 |
| northward_wind, m/s | -5.4241 | -0.8562<!--#cov.northward_wind_median--> | 10.3949<!--#cov.northward_wind_max--> |
| surface_albedo_SWIR | -0.0480 | 0.0774<!--#cov.albedo_swir_median--> | 0.1566 |
| surface_albedo_NIR | -0.0072 | 0.2180<!--#cov.albedo_nir_median--> | 0.3051 |
| solar_zenith_angle, degrees | 12.6857 | 42.4004<!--#cov.solar_zenith_median--> | 56.6597 |
| surface_altitude, m | 0.0000 | 35.4619<!--#cov.altitude_median--> | 1041.0800 |
| surface_pressure, Pa | 89950.4 | 101159.0<!--#cov.pressure_median--> | 102642.0 |

Surface albedo is negative in 166<!--#cov.albedo_negative--> of the 926 cells. That is not a fill value
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
better over bright ground: low- and high-albedo scenes are the most challenging
for the retrieval algorithm, and the operational product carries an a posteriori
correction for the resulting bias (Lorente et al., 2021, Atmospheric Measurement
Techniques 14, 665-684, doi:10.5194/amt-14-665-2021). Rice paddies flood, which
moves their albedo on the same seasonal cycle as their methane. An earlier
version of this passage said the literature reports a *seasonal* albedo bias over
agricultural land specifically; that source was not found, and the seasonal
element is dropped rather than left standing on nothing. Cities are bright and
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

## baseline_results_2018.csv, with meteorology

The table now holds 88 rows: twenty-two models under two held-out schemes at two
weightings, regenerated by

    python scripts/run_baselines.py \
        --covariates data/processed/methane_covariates_2018.csv --write

Six models use the composite covariates, and two of the additions are controls
rather than candidates. The trend surface, a linear fit on cell latitude and
longitude, is there because the methane field is smooth and any smooth function
of position reproduces part of it; a covariate that beats the spatial null but
not the trend surface has only rediscovered where the cell is. The sampling
composition term is solar zenith angle with latitude regressed out, which
measures when each cell was observed and has no physical content at all.

Wind enters as components and speed, never as a bearing. A bearing is circular,
so 359 and 1 degrees are adjacent in the world and 358 apart in the arithmetic,
and a linear coefficient on it means nothing. A linear model in the eastward and
northward components is a linear model in speed and direction jointly, in
coordinates where that discontinuity does not exist, and speed is added
alongside because it is a nonlinear function of the pair.

The headline is that meteorology beats the spatial null and land cover still
does not, and that the sampling composition control beats it too. Read
notes/decisions.md before using any of these numbers: the sampling control has
no physics in it and reaches held-out R squared 0.467, which puts the whole
annual composite in question rather than the models fitted on it.

## methane_deseasonalised_2018.tif and methane_deseasonalised_2018.csv

The per-cell methane offset with a region-wide seasonal cycle removed **at the
sounding level**, plus the sampling-date diagnostics that say how much to trust
each value. Five bands: the deseasonalised mean, the sounding count it rests on,
the mean day of year, the standard deviation of day of year, and a flag for
cells whose sampling dates span less than 15 days. Written by
scripts/compute_methane_composite.py with --export-deseasonalised.

This is not the composite mean minus a cycle. By the time a cell mean exists the
information about which days contributed has been averaged away, and subtracting
a cycle evaluated at the cell's mean date does not recover it, because the mean
of a nonlinear function is not the function of the mean. The cycle is fitted to
every sounding individually, as a fixed-effects model with one offset per cell
and harmonic coefficients shared across the region, in a single streaming pass.
src/methane/seasonal.py carries the derivation: profiling the offsets out
reduces the problem to least squares on within-cell-centred variables, whose
normal equations are assembled from per-cell sums that a streaming loop can
accumulate. Twenty-three floats per cell, so the whole grid costs about 188 kB.

A separate companion again, for the same reason as the covariates: this field
has a different meaning from the composite mean and must not sit in a file where
a reader could take one for the other. The methane composite is left untouched
and reproduces exactly, which is what makes the comparison between the two
fields meaningful.

Read bands 4 and 5 with band 1. A cell's offset is separable from the seasonal
term only to the extent that its soundings span different dates. Over this
composite the sampling-date spread has a median of 54.76 days, but 34 cells were
sampled on a single date and 66 span less than 15 days; those offsets are the
cycle evaluated at one date and are not independent of it.

**The composite covers eight months, not twelve.** There are no soundings at all
before day 120, so January, February, March and most of April are absent, and
the fitted cycle is an extrapolation over that gap. Within the sampled window it
interpolates. The consequence is that the correction is sound for every cell in
this file, because every cell's soundings fall inside the window, while the
fitted amplitude is not a trustworthy estimate of the annual XCH4 seasonal cycle
over this region and should not be quoted as one. notes/decisions.md carries the
argument and the month-by-month sounding counts.

    python scripts/compute_methane_composite.py --run --max-hours 3 \
        --checkpoint data/interim/seasonal_2018.npz
    python scripts/compute_methane_composite.py \
        --checkpoint data/interim/seasonal_2018.npz \
        --verify-against data/processed/methane_composite_2018.tif \
        --export-deseasonalised data/processed/methane_deseasonalised_2018

## deseasonalisation_2018.csv and baseline_results_deseasonalised_2018.csv

Whether removing the seasonal cycle removed the sampling artefact. The first
holds 22 rows, eleven relationships under two weightings, each computed on the
raw composite mean and on the deseasonalised field over the same cells, so the
change is visible in one line. The second is the full baseline suite re-run with
the deseasonalised field as the target, 88 rows matching
baseline_results_2018.csv model for model.

The answer is no. The association between the field and the mean sampling date
falls from Pearson +0.701 to +0.631, and every other contaminated relationship
moves as little. A variable that measures only when each cell was observed still
reaches held-out R squared 0.426 on the corrected field and still beats the
spatial null. Removing the cycle took out 20.6 percent of the between-cell
variance and left the structure of the problem intact. Fitting one harmonic
rather than two fails in the same way.

The land-cover associations are unchanged, at +0.355 for impervious fraction and
+0.096 for rice, and land cover still does not beat the spatial null on the
corrected field. That is the same negative finding as before, and correcting for
season neither rescued nor weakened it.

notes/decisions.md carries why the correction failed: the shared-cycle
assumption holds, the sampling date is only a third geography, and what remains
is day-specific synoptic variation rather than anything a function of
day-of-year can reach.

    python scripts/test_deseasonalisation.py --write
    python scripts/run_baselines.py \
        --target ch4_deseasonalised_ppb \
        --target-from data/processed/methane_deseasonalised_2018.csv \
        --covariates data/processed/methane_covariates_2018.csv \
        --out data/processed/baseline_results_deseasonalised_2018.csv --write

## albedo_correction_2018.csv

Whether Sentinel-5P's operational bias correction removes the albedo dependence
this repository measured. Sixteen rows: four series against two albedo bands at
two weightings, each with Pearson, Spearman, and a fitted slope in ppb per unit
albedo with its standard error and R squared. Written by
scripts/test_albedo_correction.py from committed tables only.

The four series are the raw retrieval `methane_mixing_ratio`, the operational
`methane_mixing_ratio_bias_corrected`, the correction itself as the difference
between them, and the deseasonalised field. Both methane variables have been
gridded since the first composite, so the correction is available without
re-reading a granule. It is positive in all 926<!--#composite.covered_cells--> covered cells and averages
+11.64<!--#composite.bias_mean--> ppb.

Slopes are reported alongside correlations because only a slope can be set
beside a published figure: a correlation depends on how much albedo happened to
vary in this sample. The slope here is still an upper bound rather than a
measurement of instrument sensitivity, because an annual composite confounds
albedo with geography, land cover and sampling season.

The answer is that the correction reduces the SWIR slope by 2.0 percent
unweighted and 30.5 percent weighted, and makes the NIR slope 11.1 percent worse
unweighted, leaving the corrected variable at 199.8 ± 6.7 ppb per unit albedo at
R squared 0.49. notes/decisions.md carries the argument, the granule metadata
that names no correction at all, and the references.

    python scripts/test_albedo_correction.py --write

## impervious_gisa_2018.csv and urban_area_by_province_gisa.csv

An independently built impervious-surface layer, used to test whether the
negative land-cover finding is an artefact of GAIA's measurement error rather
than a property of the methane field. Measurement error in a predictor
attenuates an association toward zero, so it is the threat that bears on a
negative claim, and answering it needs a second product rather than a better
argument. The per-cell file carries GISA impervious fraction and its coverage
on the same 926<!--#grid.rows--> cells as analysis_grid_2018.csv; the provincial file carries
the four 2018 totals beside GAIA's and the thesis's.

Two companion files rather than columns added to existing ones, for a specific
reason. The rest of a GISA analysis grid would be identical to
analysis_grid_2018.csv by construction, since methane, rice and province shares
do not depend on which urban product is used, so a second full grid would be
ninety percent duplication and an invitation for the two to drift apart. And
urban_area_by_province.csv cannot take GISA rows at all:
scripts/compute_urban_areas.py keys rows by year, province and boundary with no
source component, so GISA rows would collide with GAIA's on the same key and
break the comparison the script performs before it writes.

The route is the direct bundle from Wuhan University at
http://irsip.whu.edu.cn/resv2/GISA_tif.zip, 882,324,389 bytes, sha256
0f5476e39ec7762cea39dbcfd0ccdbd9474db32dc83666e12d284e1227da9a82. GISA's
documented per-tile links go through Zenodo, which is unreachable from this
host — it returned 403 when this was written and now times out at the TCP
level for every endpoint, landing page and API alike.

*Corrected on 13 September 2026.* This paragraph continued "so the whole 882 MB
bundle is the only reachable route", and that was wrong. The same Wuhan
University server that serves the bundle also serves the tiles individually:
`http://irsip.whu.edu.cn/resv2/GISA_tif/` is a browsable Apache index of all
257 tiles, `urban_1.tif` through `urban_257.tif`, about 8.7 MB each, and a
`HEAD` on one returns 200 with `Content-Type: image/tiff`. The four tiles this
study needs are about 35 MB, so the bundle was 25 times more download than the
work required. The 882 MB route is what was used and the digest above describes
it; the cheaper route is recorded so a re-run does not repeat the cost.

Nothing in the archive says which release it is. It holds 257 tiles named
urban_1.tif through urban_257.tif inside a GISA_tif/ directory, and no filename
carries a version, a year or a coordinate. Tiles are ten degrees square, not the
five GAIA uses, and the four covering the study box were therefore selected by
reading each member's georeferencing through GDAL's zip virtual filesystem
without extracting anything, which costs a header read per tile and no disk.
The release cannot be identified from the archive, and this is recorded rather
than resolved.

The encoding was confirmed against the documentation over 5,507,866,225 pixels
in those four tiles. Values 0 to 37 are present and nothing above 37. Zero is
non-impervious at 96.235 percent of pixels. Values 1 to 37 are the year a pixel
first became impervious, counting upward through [1972, 1978, 1985, 1986, ...
2018, 2019], which is the reverse of GAIA, where year = 2023 - value. Nodata is
undeclared, as it is for GAIA and for the NESDC rice rasters.

Cumulative extent through 2018 is therefore 1 <= value <= 36, which is
src.landcover.between(1, 36), and not value >= 36. The inverted form selects
only what was built in 2018 and 2019: 9,468,801 pixels against the correct
202,830,997, a factor of 21.4. It would have produced an impervious fraction
twenty-one times too small, and a land-cover association of essentially zero
that appeared to confirm the study's finding while measuring nothing.

| province | GISA 2018 | GAIA 2018 | thesis | GISA/GAIA |
|----------|-----------|-----------|--------|-----------|
| Shanghai | 2,682.2 | 3,433.6 | 5,121 | 0.781 |
| Zhejiang | 9,003.6 | 11,476.3 | 14,957 | 0.785 |
| Anhui | 11,010.6 | 11,568.7 | 10,217 | 0.952 |
| Jiangsu | 16,835.8 | 22,869.4 | 19,430 | 0.736 |
| total | 39,532.2 | 49,348.0 | 49,725 | 0.801 |

GISA finds 19.9 percent less impervious surface than GAIA across the four
provinces **in 2018**, but not uniformly: Jiangsu is 26.4 percent lower, Shanghai 21.9 and
Zhejiang 21.5, while Anhui is only 4.8 percent lower. The direction is the
opposite of what the global validation predicts. GAIA is reported to omit
impervious surface relative to GISA, with a producer's accuracy worse by 28.35
percent, in the paper describing the second version of GISA (Huang et al., 2022,
International Journal of Applied Earth Observation and Geoinformation 109,
102787, doi:10.1016/j.jag.2022.102787), which validates against 118,822 ZY-3
test samples and reports F1 scores of 0.935 for GISA against 0.721 for GAIA;
that would make GISA the larger here. It is the smaller in every
province.

**Two corrections to this paragraph, both made on 10 September 2026.** Until
then it attributed the 28.35 percent figure to the 2021 GISA paper
(doi:10.1007/s11430-020-9797-9), which does not contain it: the string "28.35"
does not occur in that paper, and the figure is from the 2022 paper describing
GISA 2.0. And it quoted the difference as holding "over 124,190 global
validation samples", a count that matches no published figure in either paper --
GISA 1.0 reports 120,777 sites from 270 cities and a second set of 88,822 ZY-3
samples from 45 cities, and GISA 2.0 reports 118,822 -- so it has been removed
rather than re-sourced. Neither correction touches the direction of the finding
this paragraph reports, which is our own measurement and unaffected. Whatever holds globally does not transfer to this region, and the
attenuation argument that motivated fetching GISA does not apply in the
direction assumed.

    python scripts/fetch_gisa.py --download
    python scripts/build_analysis_grid.py --urban-source gisa --impervious-only \
        --write --out data/processed/impervious_gisa_2018.csv

`--impervious-only` writes the four columns this file is committed with. Without
it the script writes the full fifteen-column grid, whose other eleven columns
duplicate analysis_grid_2018.csv and give them a second place to drift. The flag
was added after the omission was found: the committed file had been reduced by
hand and the reduction was never written down, so the documented command
produced a different file and nothing noticed. `config/recipes.yml` now records
this recipe and `tests/test_recipes.py` runs it.

The four-way baseline comparison built on this layer is in
alternative_predictors_2018.csv, and the descriptive comparison between the
products in predictor_comparison_2018.csv.

## urban_extent_gaia.tif, urban_extent_gisa.tif and urban_extent_totals.csv

**Four years, not three.** 2000, 2010, 2018 and 2019, because the figure's maps
and its totals panel want different ones. The maps run to 2019, the last year
both products cover -- GISA's values stop at 37, which decodes to 2019 -- and
the totals panel keeps 2018, the year the 2023 thesis reported. A figure reading
bands by position would have drawn one as the other when the fourth band was
added, so `src.figures.urban_change` selects bands by year from the raster's own
`years` tag.

Built for `figures/urban_change.png`, and the totals table is useful on its own
because it is the first regenerable GISA series this repository has had.

The two rasters carry the impervious **fraction** of each 1/128 degree cell in
2000, 2010 and 2018, one band per year, as a uint8 percentage. 992 by 1056
cells over the analysis lattice. 1/128 degree because it divides the 0.25
degree analysis cell exactly, 32 to a side, so a display cell is a subdivision
of the unit the analysis consumes rather than an unrelated grid.

A fraction rather than a class, deliberately. A 30 m product cannot be drawn
over 7.75 degrees at native resolution -- 880 million pixels against a panel
that resolves about a million -- so something must be aggregated, and storing
the fraction keeps the aggregation reversible and leaves the display threshold
in the figure, where display decisions belong. Storing a class would bake a
cartographic choice into a data product.

Aggregation is exact rather than resampled: each display cell is read at 32 by
32 sub-samples aligned to its own bounds, nearest-neighbour so no value is
invented, the selector is applied, and the mean taken.

`urban_extent_totals.csv` carries the **exact** provincial areas, by
`src.landcover.zonal_histogram`, which is the same route
`urban_area_by_province.csv` took. Twenty-four rows: two products, three years,
four provinces, on the Natural Earth boundaries.

| source | 2000 | 2010 | 2018 | 2018/2000 |
|--------|------|------|------|-----------|
| thesis 2023 | 8,297 | 24,831 | 49,725 | 6.0 |
| GAIA | 16,387.1 | 28,565.6 | 49,348.0 | 3.0 |
| GISA | 19,786.9 | 30,713.2 | 39,532.2 | 2.0 |

Sixteen of the twenty-four rows overlap tables already in this directory, and
they reproduce them to a worst relative difference of **1.3e-05**. That number
is the check that matters here, because it is what says the two products'
opposite year-of-change conventions were both applied the right way round.
GISA's extent through 2018 is `1 <= value <= 36`; the inverted `value >= 36`
selects only 2018 and 2019 construction, 9,468,801 pixels against 202,830,997,
and produces a plausible-looking map of the wrong thing.

The table does **not** replace `urban_area_by_province_gisa.csv`, which is
registered `unregenerable` and carries 2018 alone. It sits beside it, states
its agreement with it in a `relative_difference` column, and leaves the older
file's provenance record intact.

**The products cross over.** GISA is 19.9 percent smaller than GAIA in 2018 and
20.7 percent larger in 2000, so they disagree about the growth factor far more
than about the extent. Both are year-of-change products whose release history
redates transitions across the whole archive when reprocessed, which moves the
historical end and leaves the recent end alone; see `notes/decisions.md`,
"Year-of-change products are version-dependent". The 2000 and 2010 figures are
therefore not reproductions of the thesis's and should not be read as such.

    python scripts/compute_urban_extent.py --write

About a minute over the 900 MB of gitignored impervious rasters. Registered in
`config/recipes.yml` in the `on_local` tier.

## landcover_window_impervious_gisa.tif, landcover_window_impervious_gaia.tif and landcover_window_rice_nesdc.tif

Three clips of one 5.7 by 3.7 km window, at the products' own resolutions and
carrying the products' own pixel values, for `figures/landcover_native.png`.
118.44 to 118.49 east, 31.3248 to 31.3582 north, on the eastern edge of Wuhu in
Anhui. 186 by 124 pixels at 30 m for each impervious product and 557 by 372 at
10 m for the rice classification.

The values are the products' own year codes and class codes, not a boolean
mask. That is the point: the figure applies `src.landcover.selectors` to them,
so the rule that decides what counts is the same object in the figure, in the
provincial totals and in the display-grid aggregation. A committed boolean
would move that decision into a file nobody re-examines.

The window had four constraints and each was tested rather than eyeballed.

* **All three classes present and none marginal.** 23.9 percent impervious
  under GISA, 29.7 under GAIA, 29.4 percent single-season rice and 4.9 percent
  double-season. A window that is nearly all one thing shows a texture rather
  than a boundary.
* **Double-season rice present**, which restricted the search to two provinces:
  measured on the 2018 rasters, Anhui carries class 2 on 1.0 percent of its
  pixels and Zhejiang on 0.4, while Jiangsu and Shanghai have none at all.
  Seven cities across both provinces were scored and Wuhu won on the balance of
  the three classes.
* **Wholly inside one province**, tested with `contains`. The NESDC rasters
  declare no nodata and 0 means both real non-rice land and out-of-province
  background, so a window across a boundary would draw two different things in
  one colour.
* **Wholly inside one analysis cell**, the one centred at 31.325 N, 118.425 E,
  so the native pixels and the number they become are the same ground.

The window is **not** a representative sample and the caption says so: it is
34.2 percent rice against 19.5 percent for the cell that contains it, and 23.9
percent impervious against 26.3.

    python scripts/clip_landcover_window.py --write

Seconds, from the gitignored raw rasters. `on_local` in `config/recipes.yml`.

## rice_extent_2018.tif and rice_extent_totals_2018.csv

Built for `figures/landcover_regional.png`, and the totals table is the first
per-province NESDC rice series this repository has carried; `rice_area_by_province.csv`
holds only GloRice and SPAM.

The raster carries three bands per 1/128 degree cell: single-season rice as a
percentage of the cell, double-season as a percentage of the cell, and the
percentage of the cell the product actually classified. 992 by 1056 cells over
the analysis lattice, on the same grid as `urban_extent_*.tif` and for the same
reason: 1/128 degree divides the 0.25 degree analysis cell exactly, 32 to a
side.

**The third band is not a convenience.** These rasters declare no nodata and
their 0 means both real non-rice land and ground the product never covered, so
a fraction with the cell as its denominator would report ground nobody looked
at as rice-free. The band is what lets the figure draw the two apart.

**Each raster is masked by the province it is named for.** Not by the union of
the four: the files' bounding boxes overlap, between 23 and 60 percent of each
box lies outside its own province, and a union mask assesses shared ground once
per file. That failure has happened, and produced a cell at 2.94 times its own
area with a median single-season fraction of 0.079 against a correct 0.129. The
mask goes in through `src.grid.cells.accumulate_fraction`, one province per
file, and the script refuses to write until it has checked the assessed area
back against the province polygons:

| province | assessed km2 | polygon km2 | ratio |
|----------|--------------|-------------|-------|
| Shanghai | 6,746.6 | 6,746.1 | 1.0001 |
| Zhejiang | 101,456.1 | 101,337.3 | 1.0012 |
| Anhui | 120,720.6 | 140,193.8 | **0.8611** |
| Jiangsu | 100,141.8 | 100,090.9 | 1.0005 |

Anhui is legitimately short and the other three are not, which is the shape a
correct mask produces. A ratio above one is the shape an incorrect one
produces, and the check refuses at 1.02. Anhui's 0.8611 reproduces the 86.1
percent classification footprint recorded in `notes/decisions.md` by an
entirely separate route, and the totals table's Anhui rice of 22,594.6 km2
reproduces the 22,594.7 recorded there for 2018.

The totals:

| province | single km2 | double km2 |
|----------|-----------|------------|
| Shanghai | 741.2 | 0.0 |
| Zhejiang | 4,053.7 | 787.7 |
| Anhui | 20,704.9 | 1,889.7 |
| Jiangsu | 21,865.2 | 0.0 |

Double-season rice exists in two of the four provinces and not in the other
two, which is a real property of the region and is why the figure draws the
seasons apart rather than summing them as the 2023 thesis did.

    python scripts/compute_rice_extent.py --write

About three minutes over the 3.5 GB of gitignored rice rasters, eight passes:
one per raster per season, with the second season's pass used as a free check
that the two agree about which ground was assessed. `on_local` in
`config/recipes.yml`.


## methane_blended_2018.tif, methane_blended_2018.csv and baseline_results_blended_2018.csv

The same 926 cells, from the blended TROPOMI+GOSAT product of Balasus et al.
(2023, `doi:10.5194/amt-16-3787-2023`), which applies a machine-learned
correction for SWIR surface albedo, aerosol and cirrus scattering, and
across-track striping to the operational retrieval, referenced to GOSAT.

Written as a **third field** beside the raw and bias-corrected ones, in its own
file rather than as extra bands on `methane_composite_2018.tif`. The effect of
the correction then stays visible instead of being chosen silently, and a
reader who found four bands in the methane file would reasonably divide any of
them by the count band — right here, but the mistake the covariate file exists
to prevent. Band 1 is the blended mean and band 2 is its own sounding count.

**The comparison is like for like, and it is asserted rather than assumed.**
926 covered cells against 926, 110,920 soundings against 110,920, and the
per-cell counts are **identical in every one of the 1,023 cells**. That
follows from three things and each was checked: the blended files hold the
operational file's `qa_value == 1.0` rows unaltered; `qa_value` in this
product takes only the raw bytes {0, 16, 40, 100} across all 578 candidate
granules of 2018, so `>= 0.75` and `== 1.0` select the same soundings; and all
223 orbits that carried an in-box sounding have a blended counterpart.

The correction is large and negative here. Per cell, blended minus operational
bias-corrected is **-12.31 ppb** on average with a standard deviation of 4.47,
running from -31.17 to +20.48; the median is -11.80 and 99 percent of cells
are corrected downward. The field's own spread is slightly **wider** than the
operational one, 15.91 ppb against 14.86, over a range of 111.47 against
106.09.

### What it did to the albedo dependence, which is not what was expected

The correction targets SWIR albedo, and on this composite the albedo
dependence **rose**:

| field | SWIR slope, unweighted | weighted |
|---|---|---|
| raw retrieval | 203.85 | 183.73 |
| bias corrected | 199.66 | 126.24 |
| deseasonalised | 172.47 | 106.45 |
| **blended** | **232.78** | **156.22** |

That is +17 percent unweighted and +24 percent weighted against the
operational bias-corrected field, and the correlation rises with it, Pearson
+0.700 to +0.762. Surface albedo NIR behaves the same way, 130.22 to 150.94
unweighted.

This is a statement about a cell-scale annual mean and not about the product.
The paper's own figure is a reduction in spatially variable bias against GOSAT
from 14.3 to 10.4 ppb at 0.25 by 0.3125 degrees, which is a different quantity
measured against a reference this repository does not have. The slope here is
fitted across an annual composite in which albedo is confounded with geography,
land cover and sampling season, so it absorbs everything that varies spatially
with albedo, and it is an upper bound on residual albedo sensitivity rather
than a measurement of it — the same caveat the operational figure carries.

### What it did to the land-cover finding: strengthened it

Every retrieval-geometry and meteorological predictor gets **better** on the
blended field, and land cover gets **worse**. Held-out R squared under spatial
blocks, by sounding count:

| model | operational | blended |
|---|---|---|
| spatial null (queen neighbour mean) | +0.514 | +0.562 |
| OLS wind (u, v, speed) | +0.563 | +0.592 |
| OLS sampling composition | +0.418 | +0.467 |
| OLS albedo (SWIR) | +0.316 | +0.412 |
| OLS trend surface (lat, lon) | +0.258 | +0.366 |
| **OLS impervious_fraction** | **+0.024** | **-0.005** |

Impervious fraction falls below a constant. **Zero land-cover models beat the
spatial null under inverse-variance weighting on either field**, and the
unweighted exceptions on the blended field are two rice models under
leave-one-province-out where both they and the null are negative.

The zero-order association falls too, Pearson +0.345 to +0.315 unweighted and
+0.212 to +0.136 weighted. And controlling for SWIR albedo now takes it
**negative**: +0.021 on the operational field becomes -0.082 unweighted and
-0.103 weighted. That is over-control, and it is what a field made more
albedo-dependent would produce; it is not evidence of a negative urban effect.

**The p-values that accompanied those two figures have been withdrawn.** They
were reported as 0.013 and 0.002, which is significant at any conventional
level, and they were computed with `n` set to the number of cells. Correcting
for spatial dependence puts them at **0.54 and 0.45**, so neither differs
detectably from zero. `data/processed/correlation_dof_2018.csv` carries both
tests for every correlation this repository reports, and the reading above does
not change: it was already that over-control rather than a negative urban
effect was the explanation, and the corrected test removes the need to explain
a significant negative at all.

### Route, cost and terms

Read from the AWS Registry of Open Data bucket `blended-tropomi-gosat-methane`
in us-west-2, anonymously, partitioned by orbit in monthly folders. Only the
223 orbits that carried an in-box sounding were read, and only four variables
from each, over HTTP range requests: **335.6 MB in 1,385 requests and about
seven minutes**, against 23.08 GiB for the full year and the operational
composite's 28.9 GB and 122.7 minutes.

Three of the seven covariates this project grids are absent from the blended
files — `eastward_wind`, `northward_wind` and `solar_zenith_angle`. That costs
the analysis nothing: `methane_covariates_2018.csv` already carries them,
averaged over the identical soundings, so the full baseline suite and the
sampling-composition control run unchanged.

Terms, from the AWS registry entry verbatim: "There are no restrictions on the
use of this data, but please contact nicholasbalasus@g.harvard.edu before its
use in a publication." The product user manual asks more broadly to be
contacted before use in research. **The author has not been contacted.** Cite
Balasus et al. (2023).

    python scripts/compute_blended_composite.py --write
    python scripts/run_baselines.py --target ch4_blended_ppb \
        --target-from data/processed/methane_blended_2018.csv \
        --covariates data/processed/methane_covariates_2018.csv \
        --out data/processed/baseline_results_blended_2018.csv --write
