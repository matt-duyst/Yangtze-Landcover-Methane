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
