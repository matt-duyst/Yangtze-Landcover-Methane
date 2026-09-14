# Audit decisions

Decisions taken during the 2026 audit that are not obvious from the code, with
the reasoning that produced them. Recorded so a later pass does not undo one by
mistake or rediscover it by paying for it.

## History will not be rewritten

`legacy/data/` holds nine source images totalling 44.4 MB, and adding them cost
the object store nothing: the pack stayed at 85.60 MiB and the object count at
205, because git is content-addressed and those blobs were already present from
before commit `b0778b8` removed the `JPGs/` paths. Re-adding identical bytes
under a new path creates a tree entry, not a second copy.

That saving depends entirely on the old paths remaining reachable in history. A
rewrite to purge `JPGs/` would delete the only copies the pack holds, at which
point `legacy/data/` becomes the sole copy and the same 44.4 MB has to be stored
for real. A cleanup intended to shrink the repository would grow it. There is a
second reason on the same side: rewriting changes every commit hash downstream
of the earliest edit, and a signed root commit makes that the whole history.

## The PDF is the document of record

For any question about what the thesis says, read `writeup/Duyst_Thesis.pdf`,
not `legacy/Duyst-Yale-Thesis.md`. The two are not the same document and the
markdown is the weaker source.

The markdown numbers its figures sequentially, Figure 1 through Figure 18, with
no chapter-decimal number anywhere; the PDF uses the chapter-decimal scheme the
text refers to, Figure 1.1, 3.1 and 4.1 through 4.7. So a figure number means
different things in the two files and cannot be carried between them. The
markdown also carries its own eighteen images embedded as base64 data URIs
rather than referencing the committed figures, so its pictures are not
necessarily the repository's pictures. And it has no abstract, results or
discussion section at all: it contains no heading above the third level and
none named for any of them.

A figure identification made in this audit was wrong and had to be reversed
after checking the PDF. That is the reason for the rule rather than an
illustration of it.

The markdown was moved from the repository root to `legacy/` on 3 September
2026, so that its status is legible from its location rather than only from
this note. It sat directly above `Duyst_Thesis_Final.ipynb` in the root
listing, where a visitor exploring the repository met it first and found the
weaker of the two documents; and at 6,625,368 bytes it is past the size GitHub
will render, so clicking it returned a size refusal rather than any content.
The rule above is why it is not at the root; the render limit is why leaving it
there was worse than useless.

## Provincial_Graph.png is the published figure

`legacy/figures/Provincial_Graph.png` is the figure published as Figure 4.6.
It was confirmed by extracting the embedded image from page 21 of the PDF and
comparing: the same title, the same peach, light green and dark green palette,
the same bars, and the same legend along the bottom. It is also byte-identical
to the `Prov_Stats.png` blob `f1769763`, deleted twice in 2023, so it is the
long-lived file under a later name.

`legacy/figures/Provincial-Stats.png` is a later restyle that does not appear in
the thesis. It carries a different title, a beige, mint and teal palette, a
legend moved to the top and bars grouped by year. It is the more polished of the
two, which is presumably why it keeps being taken for the original. It was
identified incorrectly before being settled against the PDF.

## Urban figure colour is a year label, not a quantity

The three urban figures use a different thematic colour for each year: pale
green for 2000, pink for 2010, and pale blue-violet for 2018. This matches how
the thesis text describes them. The three rice figures do the opposite, using
one green across all years, and all six share the same basemap, extent and
framing.

Urban colour therefore encodes which year is being shown, not how much of
anything there is. Reading it as a thematic quantity, or comparing urban colours
across the three panels as though they were on one scale, produces nonsense.

## h5py applies no fill masking

Reading a grouped netCDF through xarray, with either the `netcdf4` or the
`h5netcdf` engine, masks the fill value to NaN by default; the two engines agree
with each other exactly. Reading the same file through h5py directly does not:
the fill cell comes back as its raw sentinel value.

This matters because the failure is silent. A mean or a sum computed over an
unmasked array is pulled toward the sentinel rather than raising, and a large
negative sentinel over a sparse granule can move a result by orders of magnitude
while still returning a plausible-looking number. Any code that drops to h5py
for speed has to mask the fill itself. The sentinel TROPOMI Level 2 actually
uses should be read from the granule's own `_FillValue` attribute rather than
assumed.

## Year-of-change products are version-dependent

GAIA does not store urban extent per year. It stores, in a single band, the year
each pixel first became impervious, and the extent for any year is recovered by
thresholding that band. This makes the product unusually sensitive to
reprocessing. A later release re-runs the change detection over the whole
archive, so a pixel that one version dates to 2004 another may date to 1996.
Nothing about the file signals that a transition has moved; the raster looks the
same and decodes cleanly under either version.

The versions in play here are not the same. The thesis used the 1985 to 2018
release. The archive currently reachable on figshare is 1985 to 2021, and Star
Cloud distributes a later version again, described on the figshare record as
Version 2024. So a reproduction is comparing two different reconstructions of
the same history, not two computations of the same data.

The provincial totals show exactly the shape that implies. Summed across the
four provinces, the current release agrees with the thesis to 0.8 percent for
2018, but differs by a factor of 1.98 for 2000. The recent end, where least
reprocessing separates the two versions, matches closely; the historical end,
where the reconstruction has been redone, does not. A reproduction of the 2018
extent is therefore meaningful. A reproduction of the 2000 or 2010 extent
against a different version is not, and a disagreement there should not be read
as an error in either computation.

The same caution applies to GISA, which is also a year-of-change product and has
its own release history, and it applies with an extra hazard because the two
products encode the year in opposite directions.

Both conventions are recorded here explicitly, because getting one backwards
does not fail loudly. It inverts the urbanisation history, turning the oldest
urban core into the newest expansion, and still produces a plausible-looking
map.

GAIA counts downward from the newest year. Its readme states that pixel values
represent urban frequency over 0 and 2 to 38, with 0 non-urban, 2 newly expanded
in 2021, and 38 existing in 1985 and before. So year equals 2023 minus value,
and cumulative extent for a year is value greater than or equal to 2023 minus
that year: 2000 is value >= 23, 2010 is value >= 13, 2018 is value >= 5. Source:
ReadMe-GAIA.txt, distributed alongside the data at
https://doi.org/10.6084/m9.figshare.27245775.v1.

GISA counts upward from the oldest year. The Wuhan University distribution page
states that values range 0 to 37, zero meaning non-impervious, and pairs the
years 1972, 1978, 1985, 1986 and so on through 2019 with the values 1, 2, 3, 4
and so on through 37. So 2000 is value >= 18, 2010 is value >= 28, and 2018 is
value >= 36. Source: http://irsip.whu.edu.cn/resv2/dataweb.php.

## The NESDC rice rasters carry no nodata

All thirty-six NESDC rice GeoTIFFs, four provinces across 2017 to 2025, return
None when asked for their nodata value. The field is simply not set. The product
documents three pixel values, 0 for non-rice, 1 for single-season rice and 2 for
double-season rice, and those are the only three values that occur; there is no
fourth value acting as an undeclared fill.

The consequence is that 0 carries two meanings at once. Each file is a plain
rectangular raster covering the province's bounding box, not a raster clipped to
the province polygon, so every pixel outside the province but inside the box is
also written as 0. Real non-rice land inside the province and territory that
belongs to a neighbouring province are indistinguishable in the file.

The scale of that is not marginal. Measured in an equal-area projection,
Shanghai's raster box encloses 13,914 km2 around a province of 6,746 km2, so 52
percent of the zeros in the Shanghai file are not Shanghai at all. Zhejiang is
the same proportion, its box enclosing 209,840 km2 around 101,337 km2. Jiangsu
is worse at 60 percent, with a box of 252,380 km2 around 100,091 km2. Anhui is
the tightest and still has 23 percent of its box outside the province.

Any rice fraction computed as class 1 or 2 divided by the raster extent, rather
than against the province polygon, will therefore be wrong, and wrong by roughly
a factor of two for three of the four provinces. Nothing in the file signals it:
there is no mask band, no nodata value, and no metadata field that distinguishes
background from genuine non-rice. Every provincial statistic from these rasters
must be taken through data/reference/yrd_provinces.geojson, and the pixel counts
recorded during characterisation are whole-file counts that must not be used as
provincial totals.

## NESDC rice totals are pinned for Shanghai and Jiangsu

Shanghai's single-season rice count is stable to 0.03 percent across 2019 to
2025, on a raster of 163,194,340 pixels. That stability is not stability of the
rice itself. Between 2019 and 2025, 8,619,817 pixels changed class, and only
4,800,822 pixels are rice in both years, which is 52.69 percent of 2019's rice
and a Jaccard index of 0.3577. Just over half the land labelled rice at the
start is still labelled rice at the end, while the total barely moves.

The 2023 to 2024 pair is the clearest single case. Between those two years
5,651,475 pixels gained the rice label and 5,651,551 lost it, a difference of 76
out of more than five and a half million in each direction. Two independent
classifications of a changing landscape do not balance to seventy-six pixels.

Zhejiang is the control and it rules out the obvious alternative explanation.
Zhejiang relocates just as heavily, between 78 and 117 percent of its rice
changing class each year, but its net moves by millions of pixels. Heavy
relocation is therefore a property of this product everywhere, and the feature
that distinguishes Shanghai is the pinned total rather than the movement.

Jiangsu shows the same signature from 2020 onward, and also across 2017 to 2018,
where the net is plus 38,589 against a rice count of 265 million while 281.6
million pixels changed class. Jiangsu's transitions across 2018 to 2020 move
freely, so the pinning there is not continuous.

This is not file duplication. All thirty-six files have distinct sha256 values,
and all nine of Shanghai's decoded pixel arrays have distinct sha256 values, so
no year is a copy of another at either the file or the pixel level.

What the pixels cannot show is what the total is pinned to. They establish that
the count is held fixed; they do not establish whether the target is a
statistical sown-area figure, a prior year's output, or something else. The
product's documentation does not ship on the FTP route, so there is nothing on
that route to consult.

One further measurement constrains the mechanism and is the sharpest number
here. The rice area computed inside the Shanghai province polygon varies by
1.450 percent across 2019 to 2025, while the whole-file count varies by 0.03
percent, fifty times less. The pinning therefore operates on the whole-raster
count and not on the within-province count, which means the target is defined on
the classifier's own processing extent rather than on the province.

The consequence is a hard constraint. For Shanghai 2019 to 2025 and Jiangsu 2020
to 2025, the annual totals are not independent observations. They must not be
used as a time series, must not be regressed against anything, and must not be
compared year on year against the 2023 thesis PPPM estimates, because any such
comparison would measure the pinning rather than the rice. The per-pixel maps
remain usable for a single year, but the same cell changes label between years
for reasons that are not observations, so no temporal feature can be built from
them for those two provinces.

As a caveat on the boundary of that rule, 2018 is a defensible single-year
snapshot for Shanghai, where the 2017 to 2018 net of minus 288,392 is an order
of magnitude above the later noise. It sits at the boundary for Jiangsu, whose
transition from 2017 is pinned while its transition to 2019 is not.

## Anhui's rice rasters are clipped, and the clipped region is unclassified

Anhui's raster does not contain the province in seven of the nine years. The
2017 to 2020 rasters omit 13.675 percent of the polygon, cutting 1.2966 degrees
off the north and 0.3923 off the west. The 2021 to 2023 rasters omit 8.138
percent, having fixed almost all of the western cut but only a quarter of the
northern one, still losing 1.0553 degrees off the top. Only 2024 and 2025
contain the province, and then with a residual 2.9 km2 sliver on the western
edge that is negligible.

The rice counts are comparable across all nine years, which is not obvious and
had to be checked rather than assumed. Every one of the 963 million pixels added
by the box growth is class 0. That was verified directly: the northern strip
holds 772,361,075 pixels and the western strip 190,261,806, and in both the only
value present is 0. The 2024 rice count is 274,422,562 whether computed over the
full raster or restricted to either of the earlier boxes, so the 2023 to 2024
rise of 4,058,040 pixels is entirely real change on common ground and none of it
is the box moving.

The question of whether that region is rice-free or simply unclassified was open
and is now settled: it is unclassified. Five annual products, produced across
three different raster extents, all terminate their classification at latitude
33.3462 to within 22 metres. The northernmost class-1 pixel in the 2024 raster
sits at 33.346144 against a 2017 to 2020 raster edge of 33.3462, a difference of
6.1 metres on a 10 metre grid. The 2021 to 2023 rasters extend 27 km north of
that line and classify nothing there; the 2024 and 2025 rasters extend 143 km
north of it and classify nothing there either. The classifications otherwise
differ from one another year to year, so this is not one output copied forward.
A boundary reproduced to sub-pixel precision across five separately produced
files is a processing boundary, and no agricultural explanation accounts for it.

The same cutoff exists on the western edge. The westernmost class-1 pixel in the
2024 raster is at longitude 115.268428 against the 2017 to 2020 western edge of
115.2682, an offset of 21.4 metres, with every longitudinal band from 114.87 to
115.26 holding hundreds of thousands of in-polygon pixels and no rice at all.
The classification footprint in every year is therefore the 2017 to 2020 box
exactly, on both edges, whatever canvas the file is written on. That footprint
covers 120,754 km2 of the province and omits 19,440 km2, of which 18,459 km2 is
north of 33.3462 and 981 km2 west of 115.2682.

How this was nearly missed is worth recording, because the same mistake is
available in any profile. At 0.1 degree resolution the latitudinal band profile
supports the rice-free reading: class-1 density declines smoothly from 34.2
percent at 32.4 degrees to 3.4 percent at 33.2, which reads as an ordinary
agricultural gradient running out. Only refining to 0.001 degrees shows the
decline continuing to 0.0014 percent in the band containing the old edge and
then hitting exactly zero immediately after it. Check the resolution of a
profile before concluding anything from its shape.

The magnitude of the omission is small, which matters more for use than the
binary answer. GloRice puts about 320 km2 of rice in the region, 1.44 percent of
Anhui's rice on 13.2 percent of its land, at roughly a tenth of the southern
density. Extrapolating instead at the density of the covered part gives 3,645
km2, which would put Anhui's 2018 total at 26,239 km2 against a provincial sown
area statistic of 25,450, so uniform density is ruled out arithmetically. On the
region where both products look, they agree to 2.7 percent: 22,594.7 km2 from
this product against 22,007.6 from GloRice for 2018.

GloRice bounds that estimate without establishing it. It allocates official
statistics to grid cells through an allocation model, so its distribution within
a province is modelled rather than observed, and its northern share being
constant at 1.44 percent across all five years is itself the signature of a
fixed allocation weight rather than five annual observations.

The earlier judgement that the count is sound is therefore amended. Anhui's
totals cover the province south of 33.3462 and east of 115.2682, not Anhui, with
a known omission on the order of 1.4 percent of the province's rice. The
nine-year series nevertheless remains internally comparable, because the same
region is excluded from every year that covers it and absent from every year
that does not, so year-to-year differences are unaffected.

That distinction decides usability, and it is worth stating against the other
two provinces explicitly. Anhui's defect is a fixed, quantified, spatially
bounded omission with a known sign: the totals are low by a small amount, always
in the same places, in every year. Shanghai's and Jiangsu's defect is a pinned
total, which destroys the information content of the series itself. Anhui
retains a usable nine-year series and those two do not.

A separate constraint follows from the extent, independent of the count
question. Anhui 2017 to 2023 must not be used for any area-normalised statistic.
The raster covers only 86.1 percent of the province in 2017 to 2020 and 91.9
percent in 2021 to 2023, while a polygon denominator covers 100 percent, so a
rice fraction or a rice density for those seven years is wrong even though the
underlying count behaves as described above.

## Rice fractions must be computed against the raster-polygon intersection

The denominator for any rice fraction from this product is the intersection of
the province polygon with that year's raster extent, not the polygon area. Where
the two differ, the coverage fraction must be recorded per province-year, so a
reader can see which figures rest on partial coverage rather than having to
rediscover it.

This compounds with the missing nodata recorded above. Because these rasters are
plain rectangles around each province rather than clipped to the polygon, and
because 0 means both non-rice land and out-of-province background, a fraction
computed against raster extent rather than against the polygon is wrong by
roughly a factor of two for three of the four provinces.

The measured figures are these. Shanghai's raster box encloses 13,914 km2 around
a province of 6,746 km2, so 52 percent of the box is outside the province.
Zhejiang is the same proportion, 209,840 km2 of box around 101,337 km2. Jiangsu
is the worst at 60 percent, 252,380 km2 around 100,091 km2. Anhui is the
tightest and still has 23 percent of its box outside the province.

Masking is not a fixed correction that can be applied once and reused. Only 94.1
to 95.5 percent of Shanghai's class-1 pixels fall inside the province polygon,
and that fraction varies from year to year, so the mask has to be applied to
each raster rather than absorbed into a per-province constant.

## Repository author fields are not citations

The GloRice entry in the manifest cited "Zhang et al. (2025)" for a paper whose
first author is Xie. The correct citation is Xie, H., Li, J., Li, T., Lu, X.,
Hu, Q., and Qin, Z. (2025), Scientific Data 12, article 182,
doi:10.1038/s41597-025-04483-1, confirmed against Crossref.

The mechanism is worth recording because it will recur. The figshare record for
GloRice lists two authors, Zhangcai Qin and Hanzhi Xie, where the paper has six,
and it lists them last author first. Reading a first author off that field
therefore gets the wrong person twice over: the wrong end of the list, and a
given name, Zhangcai, that reads as the surname Zhang to anyone scanning
quickly. The GAIA record on the same platform lists a single author, Gong Peng,
in the opposite name order again.

A repository author field records who deposited the files, in whatever order and
completeness the depositor chose. It is not a citation and must not be used as
one. Every citation in this repository is to be verified against Crossref or the
publisher's own record before it is written, and the DOI is the thing to carry
forward, since it survives the ambiguity that names do not.

## Sentinel-5P stream coverage is not uniform across years

The MEEO mirror carries the L2 CH4 product under both a reprocessed stream,
RPRO, and an operational one, OFFL, and neither covers the whole study period.
Listing both for every year from 2018 to 2024, restricted to orbits that could
see the study box, took 40 minutes and gave this.

| year | RPRO candidates | RPRO days | RPRO processors | OFFL candidates | OFFL days | OFFL processors |
|---|---|---|---|---|---|---|
| 2018 | 578 | 246 | 020400 | 75 | 34 | 010202 |
| 2019 | 868 | 365 | 020400 | 871 | 365 | 010202, 010300, 010301, 010302 |
| 2020 | 870 | 366 | 020400 | 870 | 366 | 010302, 010400 |
| 2021 | 865 | 364 | 020400 | 867 | 365 | 010400, 020200, 020301 |
| 2022 | 507 | 215 | 020400, 020600 | 867 | 365 | 020301, 020400 |
| 2023 | 24 | 12 | 020600 | 875 | 365 | 020400, 020500, 020600 |
| 2024 | 10 | 12 | 020600, 020800 | 864 | 366 | 020600, 020701, 020800 |

Two patterns run in opposite directions. RPRO is homogeneous, a single
processor version for each of 2018 to 2021, but its coverage collapses after
2021: 215 days in 2022 and twelve days in each of 2023 and 2024. OFFL covers
2019 to 2024 completely, every day of every year, but never at a single
processor version; 2019 spans four.

The practical assignment that follows is RPRO for 2018 through 2021 and OFFL
for 2022 through 2024. No year needs both, and no year should get both.

Mixing streams inside one composite is not safe and is the same hazard
latest_per_orbit exists to avoid, one level up. That function keeps a single
processor version per orbit because two versions of one overpass are two
reconstructions of the same measurement rather than two measurements. RPRO and
OFFL are two reconstructions of the whole record, on different processor
version families entirely: RPRO sits at 020400 for the early years while OFFL
is still at 010202 to 010400 for the same dates. Pooling them would average
across algorithm versions with no way afterwards to tell which cell came from
which, and the resulting field would not be attributable to any released
version of the product. The same caution is already recorded here for GAIA
under year-of-change products being version-dependent; this is that principle
applied to a stream rather than a release.

Mixing cannot be avoided entirely, and where it cannot the composite must say
so. Every OFFL year spans several processor versions internally, so a 2022 to
2024 composite is unavoidably mixed no matter what is done, and the per-granule
provenance the gridding module carries is what makes that visible rather than
hidden.

One further limitation is worth stating because it bears directly on the thesis
year. 2018 is not fully covered by either stream. RPRO holds 246 days of it and
OFFL only 34, so even taking both there is no complete year of 2018 on this
mirror, and any 2018 composite describes the days that exist rather than the
year.

## Coverage cannot be extrapolated from a small granule sample

The reconnaissance estimate of TROPOMI coverage was badly low and the reason is
worth recording, because the mistake is available to any sampling design and the
obvious explanation for it turns out to be the wrong one.

Reconnaissance sampled one granule on the fourteenth or fifteenth of alternate
months, thirty-six granules across seven years, six of them in 2018. It reported
56.11 percent of cells covered at 0.25 degrees and 1,004 valid in-box soundings
for 2018. The full year gives 90.52 percent and 110,920 soundings from 578
candidate granules.

The natural explanation is that the sample landed in the wrong months. Yield is
strongly seasonal here: June to August give 4.6 to 5.0 percent of the year's
soundings each despite carrying the most granules, while October alone gives
30.8 percent, and the 2018 sample missed October. That explanation does not
survive contact with the numbers. The six sampled granules are 1.04 percent of
the year's 578 and produced 0.91 percent of its soundings, a ratio of 0.87, and
their mean of 167 soundings per granule sits 13 percent below the full year's
192. Missing October cost the sample something, but sampling November and
December, which together carry 31.6 percent, gave most of it back. The sample
was close to proportional and it estimated per-granule yield roughly correctly.

What it could not estimate is coverage, because coverage is not an average. It
is the size of a union of sets, and a union saturates: each new granule adds
only the cells no earlier granule reached, so the count rises steeply at first
and then flattens. A small sample sits on the steep part of that curve and
reports a number that says more about the sample size than about the data. Worse,
fitting a saturating model to the small sample and extrapolating did not rescue
it. A free-asymptote fit to sixteen productive granules put the ceiling at 50.4
percent of cells at 0.1 degrees and was reported as an upper bound; the measured
result at 0.25 degrees is 90.52 percent. Extrapolating a saturation curve from
data that has barely begun to saturate estimates the curvature, not the ceiling.

The general rule that follows is that any statistic which is a union, an extent,
a count of distinct things reached, or anything else that saturates with sample
size, must be measured at the sample size it will be used at. It cannot be
estimated from a pilot and it cannot be extrapolated with a fitted asymptote. A
mean can be estimated from a small sample; a coverage fraction cannot.

The separate seasonal caution still stands on its own terms even though it was
not the cause here. A stratified sample of a seasonally driven quantity must be
stratified on the season, and a uniform sample across months will mislead in
proportion to the seasonality. In this record autumn and winter carry 75.5
percent of the year's soundings from 44 percent of its granules, so any
per-granule statistic that is later weighted by soundings will be dominated by
months a uniform sample under-represents.

One decision rests on the understated figure and should be revisited rather than
changed now. The 0.25 degree analysis grid was chosen partly because 56 percent
coverage at that resolution looked like the most the data would support, against
32.91 percent at 0.1 degrees. At 90.52 percent for a single year a finer grid may
now be defensible, and the question is worth reopening with the measured
saturation rather than the estimated one. Changing it would invalidate the
committed composite and the coverage table, so it is a decision to take
deliberately and not a correction to apply.

## The SciDB rice product is the FTP product with one class removed

The rice rasters reached this repository by two routes. The Science Data Bank
route is anonymous and scriptable and is what `scripts/fetch_rice.py` uses. The
National Ecosystem Science Data Center FTP route required a personal-use grant,
is deliberately not scripted, and carries a `-rice-` rather than a
`-middle_rice-` name. The obvious reading is that these are two products and
that choosing between them trades reproducibility against completeness.

They are not two products. For 2018 the two routes deliver rasters with byte
-identical transforms, shapes, CRS, nodata and dtypes in all four provinces, and
their class histograms are related exactly:

| province | FTP class 1 | SciDB class 1 | FTP class 2 | SciDB 0 minus FTP 0 |
|----------|-------------|---------------|-------------|---------------------|
| Anhui    | 245,179,405 | 245,179,405   | 22,133,916  | 22,133,916          |
| Jiangsu  | 265,368,077 | 265,368,077   | 0           | 0                   |
| Shanghai | 9,199,769   | 9,199,769     | 0           | 0                   |
| Zhejiang | 48,697,595  | 48,697,595    | 9,185,464   | 9,185,464           |

The single-season class is identical to the pixel, and the SciDB zero count is
the FTP zero count plus the FTP class-2 count. The SciDB export is the same
classification with the double-season class folded back into the background.
Jiangsu and Shanghai have no double-season pixels at all in 2018, so for those
two provinces the two files are the same file.

The consequence is that the reproducibility problem is confined to one column.
Building the analysis grid from each source and differencing the tables, the
only column that differs is `rice_fraction_combined`, in 190 of 927 rows, by at
most 0.164 and by 0.022 on average where it differs. Every other column,
`rice_fraction_single` and `rice_coverage` included, is byte-identical. A reader
with no FTP grant can regenerate all but one column of the committed table
exactly, and that is worth more than either source alone would have given.

This is why the committed table is built from the FTP rasters rather than the
reproducible ones. The choice costs nothing in reproducibility that the SciDB
build would have recovered, because the two agree everywhere the SciDB product
has an opinion, and it gains the double-season column. The reverse choice would
have discarded a real distinction to buy reproducibility that was already there.

The equality is asserted for 2018 only. It was not checked for other years and
should not be assumed for them.

## The two land-cover fractions have different denominators on purpose

Two recorded constraints conflict on the analysis grid and cannot both be
followed. Fractions must be computed against the raster-polygon intersection
rather than the cell, and rice rasters must be masked by province before any
fraction is taken because their zero means both non-rice land and
out-of-province background. Applied to GAIA the second rule is wrong: GAIA is a
global product whose zero means non-urban everywhere, including over sea, and
masking it to the four provinces would silently redefine impervious fraction as
a share of provincial land rather than of the cell.

The resolution is to mask rice and not to mask GAIA, and to publish a coverage
column for each so the differing denominators are visible rather than inferred.
Impervious coverage is above 0.99 in all 927 rows; rice coverage has a median of
0.335 and is below 0.99 in 570. Comparing the two fractions within a cell
compares a share of the whole cell against a share of the provincial land in it,
and the coverage columns are what make that legible.

The rice mask must further be the province each file is named for and not the
union of the four. The distributed rasters are one per province and their
bounding boxes overlap, so a union mask assesses the shared ground once per file.
Built that way one cell reached an assessed area 2.94 times its own, and the
median single-season fraction came out at 0.079 against a correct 0.129.

## Coverage saturation is recorded per granule, going forward only

The reconnaissance sample put 2018 coverage at 50.4 percent of cells. The
measured year is 90.52 percent. The gap is not sampling noise and it is not a
seasonal bias in which granules were sampled: the six reconnaissance granules
were 1.04 percent of the year's granules and carried 0.91 percent of its
soundings, a ratio of 0.87, so they were very slightly poorer than average in
soundings and nowhere near poor enough to explain a factor of 1.8 in cells.

The cause is that coverage is a union statistic and saturates. Each granule
covers cells, and the union grows fast at first and then barely at all, because
almost every cell a late granule touches has already been touched. A small
sample therefore sits high on a curve that is still climbing steeply, and
reading its value as an estimate of the endpoint understates the endpoint by
however much of the climb remains. Any statistic of this shape has the same
problem, and the sample size does not tell you where on the curve you are.

What tells you is the curve itself, so the accumulator now records it: for each
granule, the number of cells it covered that nothing had covered before, and the
number covered in total afterwards. Two integers per granule. For the 2018 run
that is 578 pairs, about 9 kB in the checkpoint, against a checkpoint already
holding three float64 grids. There is no reason to economise on it.

The record is written going forward only, and the committed 2018 composite has
none. The curve depends on the order granules were added and cannot be
reconstructed from a finished counts grid, which knows how many soundings each
cell received but not which granule first reached it. Recovering it for 2018
would mean re-running the year: a 28.9 GB download and about an hour, to produce
a diagnostic and change no published number. The composite, the coverage table
and the analysis grid all stay as they are. The next run of any year will carry
the record, and that is when the shape becomes visible.

The one decision this bears on is the grid resolution, which was chosen partly
because 56 percent coverage at 0.25 degrees looked like the most the data would
support against 32.91 percent at 0.1 degrees. Both figures come from the same
understated sample and both are too low, so the comparison between them may
survive even though neither number does. Reopening it needs a measured curve at
each resolution, not another sample.

## Covariates never gate a sounding, and each carries its own count

The composite grids seven support-data fields alongside methane: the two wind
components, the two surface albedos, solar zenith angle, surface altitude and
surface pressure. The decision that shapes the code is that none of them takes
part in deciding whether a sounding is used.

The alternative is the obvious one and it is wrong. `read_soundings` already
drops a sounding when any requested variable is at its fill value, so adding
albedo to that list would have been a one-word change. Reconnaissance had
measured that only 3.4 percent of in-box soundings carried a valid
`surface_albedo_SWIR`, so that change would silently have reduced the composite
to 3.4 percent of itself, and the study's question would have quietly become a
question about a different and much smaller part of the field. Methane variables
gate; covariates are read afterwards on the soundings methane already selected,
each masked by its own `_FillValue`, and accumulated into sums and counts of
their own.

The structural guarantee is preserved by giving every variable its own
denominator rather than by sharing methane's. `Composite.count_of` returns the
count belonging to the variable asked for, `mean_of` divides by that and returns
NaN where it is zero, and `grids` hands back the matching pair. There is no path
to a covariate mean that does not go through its own count. The covariate grids
are written to a companion file rather than as extra bands on
`methane_composite_2018.tif` for the same reason: that file's third band is the
sounding count, and a reader finding fifteen bands in it would reasonably divide
any of them by that band.

## The 3.4 percent albedo figure does not survive quality filtering

The reconnaissance figure is correct and does not apply here. Measured over the
full 2018 composite, all nine covariates are valid on 110,920 of 110,920
soundings and cover all 927 cells: 100.00 percent, not 3.4 percent.

The two figures are not in conflict because they count different things. The 3.4
percent was over all in-box soundings, before the quality filter. Albedo is
written only where the retrieval got far enough to fit it, and `qa_value >= 0.75`
selects very nearly the same soundings for the same reason, so among
quality-filtered soundings albedo is essentially always present. The two
conditions are close to the same condition.

This is load-bearing rather than incidental. The albedo confounder test was
expected to run on a few percent of cells with correspondingly little power. It
runs on all 927, which is the full sample every other result in the repository
uses, so its conclusion carries the same weight as the results it is testing.

## Surface albedo is a fitted parameter and can be negative

167 of the 927 covered cells have a negative annual mean `surface_albedo_SWIR`,
with a minimum of -0.0480 against a median of +0.0773. A reflectance cannot be
negative and this is not a fill value leaking through: the fill was read from the
variable's own attribute and excluded.

`surface_albedo_SWIR` is a parameter fitted by the retrieval, not a measured
reflectance, and over dark surfaces the fit can land slightly below zero. The
affected cells are the dark ones, mostly water and the wetter coastal margin,
which is exactly where the retrieval is weakest. Treating negative values as
invalid and dropping them would have removed 18 percent of cells non-randomly and
precisely from the population the confounder test is about, so they are kept and
this note records why a reader will find them.

## Surface albedo accounts for the whole land-cover association

This is the result the study turns on, and it is negative.

Both legs of the confounding path are wide open. Albedo reaches methane:
`surface_albedo_SWIR` against composite methane is Pearson +0.702 unweighted and
+0.599 weighted, `surface_albedo_NIR` +0.748 and +0.710, `solar_zenith_angle`
+0.697 and +0.707. Every one of those is a stronger association with the methane
field than either land-cover fraction achieves. Albedo also reaches the land
cover: SWIR albedo against impervious fraction is Pearson +0.475 with Spearman
+0.761 unweighted, and +0.319 with Spearman +0.609 weighted.

With albedo partialled out of both sides, the land-cover association is gone.
Methane against impervious fraction falls from Pearson +0.346 to +0.020
(p = 0.55) unweighted and from +0.216 to +0.033 (p = 0.32) weighted: 5.7 and 15.3
percent of its magnitude, and in neither case distinguishable from zero. Methane
against rice fraction falls from +0.101 to -0.010 (p = 0.82) unweighted and stays
negative and insignificant weighted. Both weightings agree, on all 927 cells and
on the 532 with a rice fraction respectively.

**What this does and does not establish.** It does not prove the land-cover
signal is an artefact. Albedo and impervious fraction are physically related:
cities are bright and dry, so a real urban methane signal would also show this
pattern. Controlling for albedo therefore removes genuine land-cover variation
along with any retrieval bias, and is an over-control to an unknown degree. What
it establishes is that the two cannot be separated in this data. At Spearman
+0.761 between albedo and impervious fraction there is not enough independent
variation to say which is doing the work, and a paper claiming an urban methane
signal from this field would have no answer to a reviewer who proposed the
retrieval instead.

The direction of the albedo relationship is what makes the artefact reading
plausible rather than merely available. Retrieved methane is *higher* over
brighter surfaces, which is the sign a light-path bias predicts, and it holds
across two independent albedo bands and the solar zenith angle. That is three
retrieval-geometry variables all pointing the same way and all beating the
predictor of interest.

The sample is not the limitation. The confounder test was expected to run on a
few percent of cells; it runs on all 927, the same cells as every other result
in the repository. Its conclusion carries the same weight as what it tests.

## The annual composite is confounded by when each cell was sampled

Adding meteorology to the baselines produced a large apparent improvement, and
chasing it down turned up something that matters more than the improvement.

Wind alone reaches held-out R squared 0.653 under spatial blocks unweighted
against the spatial null's 0.346, the first thing in this repository to beat the
smoothness bar on all 927 cells. That looked like transport, which is the
physically sensible reading. It is not safe to read it that way.

Solar zenith angle at a fixed latitude is fixed by the date and time of the
overpass. Across these cells, latitude explains **2.4 percent** of the variance
in mean solar zenith angle. The remaining 97.6 percent is composition: which
days, in which seasons, contributed to each cell's annual mean. Cell means of
solar zenith angle run from 12.69 to 56.67 degrees, close to the full seasonal
range at this latitude, so some cells are effectively summer means and others
are effectively winter means.

That composition axis, which has no physical content whatever, correlates with
everything:

| against the sampling-composition axis | Pearson |
|---------------------------------------|---------|
| composite methane                      | +0.686  |
| surface_albedo_SWIR                    | +0.859  |
| northward_wind                         | -0.745  |
| wind_speed                             | -0.737  |
| eastward_wind                          | +0.603  |

Entered as a predictor on its own it reaches held-out R squared 0.467 under
spatial blocks unweighted, beating the spatial null. A single scalar encoding
*when a cell was looked at* outperforms the smoothness model, and it is not a
measurement of the atmosphere at all.

So the honest reading of the wind result is that the covariates and the target
share a common cause in the sampling calendar, and the composite cannot separate
transport from season. It also reframes the albedo confounder result in the
previous section: albedo correlates with the sampling axis at +0.859, so part of
why albedo predicts methane is that both track the calendar.

The trend surface rules out the simplest alternative rather than this one. A
linear trend in latitude and longitude reaches 0.242 and a quadratic trend 0.358,
both well below wind's 0.653, so wind is not merely a smooth function of
position. It is a smooth function of position *and time*, and it is the time
part that is unaccounted for.

**What follows.** The 0.25 degree annual composite is not a sound object for
this question, and no model fitted on it can be trusted to be about land cover,
because per-cell means are taken over different and systematically different
subsets of days. Fixing this is a change to the composite, not to the model: the
candidates are compositing within season so that cells are compared over
comparable periods, or carrying day-of-year as a covariate and controlling for
it, or requiring a minimum sampling spread per cell and dropping those that fail
it. All three cost coverage, which is why the choice is not obvious and is not
being made here.

This was found by adding a control that had no reason to work. It is recorded
because the result it undermines is one this repository would otherwise have
reported as its main positive finding.

## The sampling-composition artefact, and why deseasonalising did not fix it

### How it was found

`solar_zenith_angle` was gridded as a minor covariate, added to the composite
because it was cheap and might say something about retrieval quality. It was
never expected to be the diagnostic. When the meteorological baselines came back
with wind at held-out R squared 0.653 against the spatial null's 0.346, the
obvious reading was transport, and the check that undermined it was almost an
afterthought: solar zenith angle at a fixed latitude is fixed by the date and
time of the overpass, so regressing it on latitude leaves a variable that
measures nothing but *when* a cell was looked at.

Latitude explains **2.4 percent** of the variance in mean solar zenith angle
across these cells. The remaining 97.6 percent is calendar. That residual, which
has no physical content whatever, correlates with composite methane at +0.686,
with `surface_albedo_SWIR` at +0.859, with northward wind at -0.745 and with
wind speed at -0.737, and entered as a lone predictor it reaches held-out R
squared 0.467, beating the spatial null.

The composite now carries the sampling dates directly, so the artefact no longer
has to be measured through a proxy. Mean day of year per cell runs from 124.17
to 352.18, a range of **228 days**. Some cells are effectively May means and
others are effectively December means, and they are being compared as if they
were the same quantity.

### The magnitude

| statistic | value |
|-----------|-------|
| range of per-cell mean day of year | 228.01 days |
| median per-cell sampling spread | 54.76 days |
| cells sampled on a single date | 34 (3.7%) |
| cells with spread below 15 days | 66 (7.1%) |
| cells with spread below 60 days | 528 (57.0%) |
| fitted seasonal range over sampled days | 35.67 ppb |
| standard deviation of the raw composite | 14.87 ppb |

The seasonal swing is more than twice the spatial spread of the field being
analysed. That is the whole problem in one comparison.

### The four fixes, and why the harmonic one

Compositing within season, carrying day-of-year as a covariate, and requiring a
minimum sampling spread per cell all cost coverage, and coverage at 90.52
percent was expensive to reach. The fourth costs none: remove a fitted seasonal
cycle at the **sounding** level, before the cell mean is taken.

It also looked free of the obvious objection. Subtracting a cycle from cell
means cannot work, because by then the information about which days contributed
has been averaged away and the mean of a nonlinear function is not the function
of the mean. Fitting at the sounding level avoids that, and a fixed-effects
model with per-cell offsets and shared harmonics reduces, once the offsets are
profiled out, to least squares on within-cell-centred variables, whose normal
equations are built from per-cell sums. That makes it a one-pass streaming
computation costing 23 floats per cell. The derivation is in
`src/methane/seasonal.py`.

### What it changed: almost nothing

The cycle is real and strongly identified. Two harmonics beat one at
F(2, 109,997) = 4,128, p below floating-point resolution, and the fitted range
over the sampled days is 35.77 ppb with a peak on day 245.8, early September.
*Corrected from 35.67 on 14 September 2026, when queue item 12a computed the
cycle into `data/processed/seasonal_cycle_2018.csv`: the range is 35.767, which
rounds to 35.77, on the full period and on the sampled window alike. The digit
was transposed, and this file is excluded from the claim checker so nothing
would have caught it. The peak day reproduces exactly.*
The correction was applied and the composite still reproduces the committed
methane exactly.

It did not remove the artefact.

| relationship | raw | deseasonalised |
|--------------|-----|----------------|
| methane ~ mean day of year | +0.701 | +0.631 |
| methane ~ solar zenith angle | +0.697 | +0.673 |
| methane ~ surface_albedo_SWIR | +0.702 | +0.680 |
| methane ~ northward wind | -0.785 | -0.761 |
| methane ~ impervious fraction | +0.346 | +0.355 |

Removing the cycle took out 20.6 percent of the between-cell variance and left
every association essentially where it was. The sampling-composition model still
reaches held-out R squared 0.426 on the corrected field and still beats the
spatial null's 0.343. Fitting one harmonic instead of two fails identically, so
the conclusion does not depend on the model order, even though the two orders
disagree by up to 15.7 ppb about individual cells.

### Why it did not work

Three things were checked and two of them exonerate the model.

The shared-cycle assumption holds: fitting the northern and southern halves of
the grid separately gives amplitudes of 6.99 and 12.75 ppb against 5.75 and
13.36, and peaks on day 244.9 against 249.1. The cycle really is regional.

The sampling date is only partly geography: mean day of year regressed on
latitude and longitude gives R squared 0.385, so a third of it is spatial
structure that no deseasonalisation should remove, but two thirds is not.
Controlling for position, the corrected field still tracks sampling date at
+0.488 against the raw field's +0.579.

What is left is that **the smooth annual cycle is not the dominant part of the
sampling effect**. The harmonic fit explains 26.7 percent of within-cell
variance at the sounding level; the residual standard deviation is 16.60 ppb,
which is close to the per-sounding retrieval precision and far larger than the
seasonal term. A cell sampled on a handful of dates inherits the synoptic
conditions of those particular overpasses, and cells sharing overpasses share
those anomalies. That is a day-specific effect, not a seasonal one, and no
function of day-of-year alone can reach it.

### One premise that did not survive

The composite covers **eight months, not twelve**. There are no soundings at all
before day 120: January, February, March and most of April are empty, and 30.75
percent of the year's soundings fall in October alone.

| month | soundings | share |
|-------|-----------|-------|
| Jan-Mar | 0 | 0.00% |
| Apr | 290 | 0.26% |
| May | 10,778 | 9.72% |
| Jun | 5,513 | 4.97% |
| Jul | 5,079 | 4.58% |
| Aug | 5,574 | 5.02% |
| Sep | 14,585 | 13.15% |
| Oct | 34,115 | 30.75% |
| Nov | 17,286 | 15.58% |
| Dec | 17,708 | 15.96% |

The consequence is a distinction worth keeping. The *correction* is sound for
every cell, because every cell's soundings fall inside the sampled window and
the fit interpolates there. The *amplitude* is not a measurement of the annual
XCH4 cycle over this region, because a third of that cycle is extrapolated from
no data, and it should not be quoted as one. It is also why the two-harmonic fit
has a second harmonic larger than its first, which no smooth annual cycle has.

### What this leaves

The negative land-cover result is unchanged and is now on firmer ground: a
confound large enough to carry wind and albedo, and which survives correction,
still does nothing for land cover. The positive wind result remains
uninterpretable, and the fix for it is not a better model but a different
composite. The three coverage-costing options are back on the table, and the
honest reading is that a sound answer needs seasonal compositing rather than
seasonal correction.

## The albedo dependence is a known artefact, and the operational correction does not remove it here

### It was never a discovery

The albedo association this repository measured is a documented property of the
TROPOMI methane retrieval, not a finding. Lorente et al. (2021, *Atmospheric
Measurement Techniques* 14, 665-684, doi:10.5194/amt-14-665-2021) describe the
operational product's a posteriori correction for underestimation at low surface
albedo and overestimation at high albedo. That is exactly the sign measured
here: retrieved methane higher over brighter ground. The confounder section
above should be read as having rediscovered a known instrument effect, which
does not weaken its consequence for the land-cover result but does change who
is owed the credit.

### Which variable every reported figure used

Every correlation reported anywhere in this repository was computed on the
bias-corrected variable. `src/model/baselines.py` line 68 sets
`TARGET = "ch4_bias_corrected_ppb"`, `load_table` takes it as the default, and
both `scripts/test_albedo_confounder.py` and `scripts/test_deseasonalisation.py`
call `load_table` without a target argument. The deseasonalised field is the
same variable: `scripts/compute_methane_composite.py` passes
`soundings.values[mg.PRIMARY]` to the harmonic accumulator, and `PRIMARY` is
`methane_mixing_ratio_bias_corrected`. The raw retrieval was gridded from the
first run and never analysed until now. So the figures on record are all
post-correction figures, and consistently so; no report used a different
variable from another.

### The correction test

Both variables are gridded, so the correction is available as their difference.
It is positive in all 927 covered cells, averaging +11.64 ppb with a standard
deviation of 4.97 and a range of 25.63 ppb from +3.42 to +29.05.

Against `surface_albedo_SWIR`, in ppb per unit albedo:

| series | unweighted | weighted |
|--------|-----------|----------|
| raw retrieval | 203.80 ± 6.10 (R² 0.547) | 183.87 ± 4.38 (R² 0.656) |
| bias corrected | 199.82 ± 6.67 (R² 0.493) | 127.80 ± 5.61 (R² 0.359) |
| the correction itself | -3.98 ± 3.12 (R² 0.002) | -56.08 ± 2.86 (R² 0.293) |

The correction reduces the slope by 2.0 percent unweighted and 30.5 percent
weighted. Against `surface_albedo_NIR` it makes the slope 11.1 percent *worse*
unweighted, 117.34 to 130.35.

The correction's own relationship to albedo is the direct test of whether it is
an albedo correction, and it splits. Unweighted, the correction is not a
detectable function of SWIR albedo at all: a slope of -3.98 against a standard
error of 3.12, R² 0.002. Weighted by sounding count it clearly is, at -56.08 ±
2.86, R² 0.293, and negative, meaning a larger correction over darker surfaces,
which is the documented direction. The most likely reading is that the
correction operates per sounding and the well-observed cells are where the
per-cell mean of it is estimated precisely enough to show through; that is a
hypothesis, not a result.

### The benchmark comparison, and its limits

The residual sensitivity of the corrected variable is **199.82 ± 6.67 ppb per
unit albedo at R² 0.4926** unweighted, and 127.80 ± 5.61 at R² 0.3594 weighted.
Deseasonalising reduces it to 172.36 and 107.69 without changing the picture.

A residual of order 1 ppb per unit albedo at R² near zero was offered as the
benchmark from the TROPOMI/WFMD v2.0 product (Schneising et al., 2026,
*Atmospheric Measurement Techniques* 19, 2407-2435,
doi:10.5194/amt-19-2407-2026). Both references verify against Crossref. The
specific benchmark figures do not: they were not checked against the paper's
text, and its abstract describes the v2.0 change as replacing a Random Forest
Classifier with XGBoost for *quality filtering*, not as an albedo correction.
The characterisation should be treated as unverified.

The comparison is in any case not like for like, and the difference matters more
than the ratio. A published residual sensitivity is measured after correction
against reference data, sounding by sounding. The slope here is fitted across an
annual composite in which albedo is confounded with geography, land cover and
sampling season, so it absorbs everything that varies spatially with albedo.
**It is an upper bound on residual albedo sensitivity, not a measurement of it.**
What can be said without qualification is narrower and still enough: the
operational correction does not remove the albedo dependence from this
composite, so the composite carries an albedo-correlated bias of unknown size
that no step in this pipeline removes.

### What the granule says: nothing

Searched exhaustively, the retained granule
`S5P_RPRO_L2__CH4____20180514T042147_..._020400_20221109T092730.nc` names no
bias correction anywhere. No global attribute mentions one. `METADATA/`
`ALGORITHM_SETTINGS` records `configuration.version.algorithm = '1.5.0'` and
`configuration.version.framework = '1.2.0'` and the input and output
configuration, and nothing about a bias or albedo correction or its
coefficients. The only attributes matching bias, correct or albedo anywhere in
the file are unrelated: an AAI scene albedo filter count, a sun glint correction
count and setting, and `processing.correct_surface_pressure_for_altitude`.

The variable's own comment is worse than absent. Verbatim:

> `long_name = 'corrected column-averaged dry-air mole fraction of methane'`
> `comment = 'This value will be filled with data after the commissioning phase, this is known to be empty for now'`

That comment is a stale commissioning placeholder and it is false in this file:
the variable differs from the raw retrieval in every one of the 927 covered
cells. A reader trusting the metadata would conclude the field is empty and
discard it.

So the correction this composite carries **cannot be identified from the data**.
It has to be inferred from `processor_version = '2.4.0'`,
`algorithm_version = '1.5.0'`, `product_version = '1.5.0'` and the product DOI
`10.5270/S5P-3lcdqiv`, matched against the literature. That inference is not
made here, because a correction identified by version-number archaeology is not
a correction whose behaviour can be relied upon.

### The land-cover result does not depend on the variable

Recomputed on the raw retrieval, the corrected one and the deseasonalised field,
the negative finding holds on all three. Under inverse-variance weighting no
land-cover model beats the queen-neighbour spatial null on any field, at either
sample size, under either scheme. On the full 927 cells under spatial blocks,
none beats it on any field at either weighting.

The exceptions are narrow, unweighted, and identical in kind across all three
variables, which is what makes them uninteresting: on the 532-cell rice
subsample under spatial blocks unweighted, land-cover models edge past the null
by 2 to 5 percent on every field; and under leave-one-province-out unweighted,
impervious fraction beats it by 2.9 percent on the raw field and 0.3 percent on
the deseasonalised one. No exception survives weighting.

One difference between the variables is worth recording rather than folding in.
Controlling for SWIR albedo, the impervious association survives on the **raw**
retrieval at Pearson +0.150 (p = 4.3e-06) unweighted and +0.125 (p = 1.3e-04)
weighted, where on the corrected variable it does not, at +0.020 (p = 0.55) and
+0.033 (p = 0.32). The raw retrieval is the one carrying the larger uncorrected
albedo bias, so the reading that a partial correlation survives there because the
control is incomplete is at least as available as the reading that there is a
real urban signal the correction destroys. Either way it does not change the
headline, because the spatial-null test fails on the raw variable too.

## Preprocessing this pipeline does not do

Recorded so the gap is on record rather than discovered later. None of these is
implemented and none is claimed.

**Destriping.** TROPOMI XCH4 carries an across-track bias that varies by ground
pixel index and is routinely removed by subtracting a per-row median or fitting
a low-order function of the row index. This pipeline does not. It is fully
reachable with what is already read: the granule carries the ground pixel index
implicitly in the array shape, and the streaming loop could accumulate per-row
statistics at the cost of a few floats per row. This is the cheapest of the four
and the most clearly missing.

**Cloud clearing beyond the qa filter.** The only cloud screening here is
`qa_value >= 0.75`, which bundles cloud with every other quality condition.
Studies commonly add an explicit cloud-fraction threshold from the co-located
cloud product. Reachable: cloud fraction sits in the same SUPPORT_DATA groups
the covariates were taken from and would cost one more variable in the existing
covariate list.

**Boundary-layer separation.** The column-averaged mixing ratio mixes the
boundary layer, where local emission shows, with the free troposphere, where it
does not. The standard treatment subtracts the modelled column above the
planetary boundary layer using reanalysis profiles, typically CAMS EAC4. Not
reachable with what is here: it needs external reanalysis data on a vertical
grid, and both CAMS and ERA5 return 401 to an unauthenticated request, which is
already recorded in `config/sources.yml`.

**Departures from a model forecast rather than absolute values.** Rather than
analysing XCH4 itself, the common approach analyses the difference between the
observation and a chemical transport model's forecast for the same time and
place, so that advected large-scale structure cancels and what remains is closer
to local emission. Not reachable without a model field. **This is the standard
answer to the synoptic residual the harmonic fit could not reach**, and it is
the specific thing that would make this composite analysable: a per-sounding
model departure removes both the seasonal cycle and the day-specific synoptic
anomaly, which is precisely the residual left after deseasonalising failed.

The order of value here is roughly the reverse of the order of cost. Destriping
and cloud clearing are cheap and would tidy the field. Boundary-layer separation
and model departures are expensive, need external data, and are the two that
would actually change what the field means.

## The negative finding survives independently built predictors

### Why predictor error is the threat that mattered

The study's one firm claim is negative, and a negative claim is not threatened
by the same things a positive one is. Contamination of the target biases an
association in an unknown direction, so it could as easily be hiding a
relationship as inventing one. Measurement error in a predictor does something
specific: it attenuates the association toward zero. So predictor error, and
only predictor error, is the failure mode that could manufacture this study's
result out of nothing.

Both predictors carry documented error. GAIA is reported to omit impervious
surface relative to GISA, with a producer's accuracy worse by 28.35 percent on
124,190 validation samples. The NESDC rice rasters have totals pinned for
Shanghai and Jiangsu across several years, an unclassified region beyond
33.3462 north and 115.2682 east in Anhui, and no declared nodata. Both of those
are recorded in their own sections above. Neither can be argued away, so the
answer had to be a second product with different errors.

### The result

Four predictor pairs were built and the full baseline suite run over each:
GAIA or GISA for impervious surface, NESDC or GloRice for rice.

**Zero cases beat the queen-neighbour spatial null under inverse-variance
weighting**, across all four pairs, both cross-validation schemes and both
sample sizes. Not one, out of 88 opportunities.

Eight unweighted cases beat it, and they appear on every pair, which is what
makes them a property of the unweighted comparison rather than of any product.
Six are on the 532-cell rice subsample under spatial blocks, at margins of 1.74
to 2.55 percent, near-identical between GAIA and GISA. Two are impervious plus
rice under leave-one-province-out on the GloRice grids, at 4.34 and 5.97
percent. A finding that survives when observations are weighted by their own
precision and fails only when a badly observed cell counts as much as a well
observed one is not a finding.

The two urban products agree closely: Pearson +0.9379 and Spearman +0.9559
across all 927 cells. The two rice products agree less: Pearson +0.5790 and
Spearman +0.6537 on the 532 cells where both exist. So the urban test is a weak
one, in that GISA had little room to disagree, while the rice test is a genuine
one, and both give the same answer.

### Why GloRice does not strengthen the case for rice

GloRice's raw correlation with methane is +0.3983 against the NESDC
classification's +0.1014, and its partial correlation given surface albedo
survives at +0.1652 (p = 4.3e-07) where NESDC's does not, at -0.0098 (p = 0.82).
Read alone, that looks like the rice signal the study set out to find, emerging
once a better rice product is used. It is not, and four things confound it.

It runs on 927 cells against NESDC's 532. It allocates official statistics to
grid cells through a model rather than observing rice, so it inherits the
statistics' accuracy and the allocation's assumptions and cannot be an
independent observation of extent. It correlates with impervious fraction at
Spearman +0.5613, so it partly measures developed land in general rather than
paddy in particular. And its NaN means no rice while the NESDC blank means not
assessed, so the 395 extra cells are precisely the ones NESDC declined to
assess, of which 368 lie entirely outside the four provinces.

That last point is the one that settles it. A predictor which is zero across a
coherent region and positive across another will correlate with anything else
that differs between those two regions, and the methane field differs between
them for reasons this repository has already documented at length. The
comparison is not rice against no-rice; it is inside-the-provinces against
outside, wearing a rice label.

### What this establishes

The negative finding is not an artefact of predictor measurement error. Two
independently built impervious products agreeing at Spearman +0.956 give the
same answer, and a rice product with an entirely different error structure gives
the same answer under weighting. This is the strongest support the negative
result has, and it is the reason it can be stated without the qualifications
every positive result in this repository carries.

## The TM5 prior is coarse enough to subtract, and subtracting it was not pursued

### The gate

The remaining way to clean the methane field without external data was to work
with departures, retrieved XCH4 minus the TM5 a priori that ships inside every
granule, on the reasoning that the prior contains background, seasonal cycle and
synoptic structure together. The objection is that the prior also carries an
emissions inventory, so subtracting it could remove the land-cover signal by
construction. Whether it does depends entirely on the prior's spatial scale
relative to the 0.25 degree cell, which the literature did not settle and which
is measurable from one granule already on disk.

Measured on granule 03019 of 14 May 2018. The a priori column averages 1797.82
ppb over the 84,116 soundings that carry one, and 1848.53 ppb over the 408 in
the study box, which is a plausible methane column and confirms the units and
the computation. The prior's in-box half-sill range, the separation at which its
semivariogram reaches half its variance, is **117.4 km against a 27.8 km
analysis cell, a ratio of 4.7**. At 20 to 25 km separation the prior differs by
**0.49 ppb RMS against the retrieval's 34.17**, so it contributes 1.4 percent of
the variation at the scale analysed. Across the whole study box the prior holds
**0.175 percent** of the retrieved field's variance.

So subtracting the prior would act as a high-pass filter with a cutoff near 100
km, well above the cell, and would not remove a land-cover signal. On the
question the gate was set to answer, the approach is safe.

### Why it was not pursued anyway

The gate passes and the approach was still not taken, and this half matters
more.

The departure inherits the albedo bias essentially intact. In-box it moves the
correlation with `surface_albedo_SWIR` from +0.4496 to +0.4499 while removing
3.53 percent of the variance. The bias lives entirely in the retrieved term and
the prior has no albedo dependence, so the departure keeps the whole bias and
discards real variance, which makes the problem worse as a share of what
remains rather than better.

And a single granule is a single instant. It contains no seasonal variation and
no day-to-day synoptic variation, which are exactly what the departure was
proposed to remove. The gate therefore confirmed the approach is safe for the
land-cover question while leaving entirely unestablished that it fixes the
problem it was proposed for. Establishing that needs TM5's day-to-day variation
compared against the retrieved field's across many overpasses, which is the 28.9
GB run itself. The gate cannot be completed cheaply, and the cheap half came
back neutral at best.

### What could not be determined

Whether TM5 reproduces the day-specific synoptic variation over this region.
That is the question the departure stands or falls on and one granule cannot
answer it.

TM5's native grid resolution. The prior is interpolated onto sounding locations
rather than sampled nearest-neighbour, so it gives **76,749 distinct values from
84,116 soundings** and shows no plateaus at all. The interpolation destroys the
block structure that would have revealed the model grid, so the resolution had
to be inferred from the variogram rather than read off the data.

### An incidental finding worth keeping

The a priori exists on 408 of 12,175 in-box soundings, **3.4 percent**. That is
the same fraction as `surface_albedo_SWIR` availability, and for the same
reason: both are written only where the retrieval got far enough, and that is
very nearly the same condition as `qa_value >= 0.75`. So a departure would be
computable on essentially the whole quality-filtered composite rather than on a
subset of it. Whatever else is wrong with the approach, sample size is not the
objection.

### What was committed

`src/methane/apriori.py`, with the fill handling and the layer-order handling
and tests, though nothing currently calls it. It is a reusable computation and
the departure work is now one configuration change away rather than a rebuild,
which is the right state for a line of work that is gated rather than closed.

Its docstring records that `altitude_levels` runs 63,037.6 m at index 0 down to
20.6 m at index 12, so the file is stored top-of-atmosphere first, which is why
the Harvard TROPOMI inversion code reverses the layer axis on reading. The ratio
of sums is order-invariant so the column computation is unaffected, and a test
asserts that explicitly, so that nobody adds a per-layer step assuming the same
protection. `surface_first()` is provided for when one is added.

## Task instructions are hypotheses, not specifications

Across this project the briefs directing the work have supplied figures,
conventions and factual premises that did not survive being checked against the
data. That happened often enough, and in a consistent enough shape, that the
pattern is worth recording as a working practice rather than as a list of
corrections.

### The pattern

Three failure modes recur.

**A figure recalled from an earlier report loses its qualifiers.** A number that
was stated with a scope, a projection or a sample attached comes back without
them and is then wrong, or right about something else. Provincial areas quoted
without the projection they were measured in. A count of duplicates that had
been two reported as four. A correlation attached to the wrong methane variable.
Two retrieved means off by about 1 ppb because they had been rounded once and
re-rounded. The figures are rarely invented; they are usually true of something
adjacent.

**A convention explained correctly can still be applied backwards in the same
breath.** The clearest instance is the GISA selector. The brief stated that GISA
counts upward from the oldest year and that GAIA counts downward, warned in
terms that getting this backwards inverts the urbanisation history and fails
silently, and then in the next sentence specified `value >= 36`, which is GAIA's
rule. Understanding a distinction and applying it are separate acts and the
first does not protect the second.

**A globally reported property does not transfer to a region.** GAIA is reported
to omit impervious surface relative to GISA, with a producer's accuracy worse by
28.35 percent over 124,190 global validation samples. In these four provinces
GISA finds 19.9 percent *less* impervious surface than GAIA, and the direction is
reversed in every one of them. A validation statistic is an average over a
sample that may not include the place being studied.

### The instances

Recorded compactly as evidence for the pattern. A rice CSV specification that
produced duplicate rows; four provincial areas quoted in the wrong projection; a
duplicate count of four when two was correct; a colour convention generalised
from one figure to a set; a figure identification reversed twice; a citation
taken from a repository author field that named the wrong person; a Shanghai
raster box estimated in degrees rather than projected, with only one province
checked when the worst case was elsewhere; a claim that a README cited an author
when it cited only a DOI; an assertion that a `conftest.py` existed when it did
not; a WFMD benchmark attributed to a paper whose abstract describes something
else; a GISA filename convention that does not ship; the GISA selector above;
the direction of GAIA's regional bias; a plateau shortcut that found no
plateaus; and the two retrieved means.

### The practice

A factual claim in a brief is treated as a hypothesis to verify against the
data, not as an instruction to implement, and the verification is reported
whether or not it agrees. That costs a few minutes per claim and it caught every
instance above. Where a premise fails, the work proceeds on the measurement and
the failure is stated rather than quietly routed around, because a brief whose
premises are silently corrected teaches nobody anything and the same premise
returns in the next one.

The corollary is that agreement is worth reporting too. Most premises did
survive: the GISA archive's byte count and digest, its pixel census to the
digit, the encoding table, the count of unweighted exceptions, every figure in
the prior gate. Reporting only the failures would misrepresent the base rate and
make the checking look more adversarial than it is.

### The one that mattered

The inverted GISA selector. Applied as written it would have computed impervious
fraction from 9,468,801 pixels instead of 202,830,997, a factor of 21.4 too
small, across a study area where impervious fraction is the strongest land-cover
predictor available. The resulting association with methane would have been
approximately zero.

That is the study's expected answer. The error would have produced a result
agreeing with the conclusion already reached, on a robustness check whose entire
purpose was to test that conclusion against a second product, and it would have
been reported as confirmation. Nothing downstream would have looked wrong: the
fractions would have been small but plausible, the models would have run, the
null would have won. A wrong number that contradicts the expectation gets
caught; a wrong number that confirms it does not.

## The repository was renamed, and two references do not follow it

`Yale-Masters-Thesis` became `Yangtze-Landcover-Methane` on 3 September 2026.

The old name described where the work came from rather than what it contains. It
was accurate in 2023, when the repository held a thesis and its notebook. It is
no longer the substance: what is here now is a reproduction that reaches a
different conclusion from the thesis, with the thesis preserved beside it as the
thing being reproduced. A reader searching for a study of land cover and methane
over the Yangtze Delta would not have found it under a name that identified only
the degree-granting institution, and a reader who did find it would have been
told the wrong thing about what it was for.

GitHub redirects the old URL permanently, so links and clones keep working, and
the pinned entry on the profile follows the rename because pins are stored by
repository identifier rather than by name. Three references in this repository
did not follow it and were updated by hand: `repository-code` and the leading
identifier of `title` in `CITATION.cff`, and the opening line of
`notes/repository-architecture.md`. That last one now names both the old and the
new name, because it is a document about what was believed before any code
existed and silently swapping the name would have falsified the record it keeps.

**`CITATION.cff` carries the name twice, in a URL and in a title, and both go
stale silently.** Nothing validates a `repository-code` against a live URL and
nothing checks a title against anything, so a future rename breaks both without
any test failing. `cffconvert --validate` passes on a file pointing at a
repository that no longer exists under that name. That is the specific failure
to check for next time rather than to rediscover.

The redirect does not reach outside this repository. The profile README in
`matt-duyst/matt-duyst` refers to the project as `Yale-Masters-Thesis` in plain
prose, not as a link, so GitHub cannot redirect it and no test here can see it.
It needs a manual edit in that repository. Two other things about that README are
worth the same visit: it describes the thesis as "training a segmentation
network... and running it backward through the decades", which `ERRATA.md` 1.1
and 3.5 record is not evidenced in the thesis and which the reproduction does not
support, and it describes the repository as holding "data, model, and figures"
when there is no model and no figures directory.

## The register's finding was not format drift, it was that the methods were uncited

`notes/references.md` was built to fix inconsistent citation formatting across
four files. It did that, and found four errors worth fixing: the GAIA title
pluralised, the GISA title miscapitalised after its colon, a Sentinel-5P DOI the
granules do not declare, and He et al. 2022 named without a DOI.

None of that was the useful finding. The useful finding was the count. Before
this pass the register held fourteen sources, of which **thirteen were subject
literature and one was method literature** — and that one was the thesis's
citation of a masked-autoencoder paper, reported in the errata as a defect,
not something the reproduction used. So the reproduction's own methods were
cited **zero** times.

That is not a small omission. The evaluation design that carries the study's
central negative result is spatial cross-validation, chosen because random
splits leak through spatial autocorrelation, and it rested on no reference. The
semivariograms that closed the TM5 prior gate, the partial correlations that
carried the albedo confounder test, the fixed-effects harmonic fit, and the
flux-divergence conversion that was gated and declined were all applied without
one. A reader in atmospheric science would have found a repository citing its
data thoroughly and its methods not at all.

After this pass the register holds twenty-six sources: **twenty-one subject and
five method**, of which one, the value-suppressing uncertainty palette, is
explicitly borrowed from human-computer interaction and labelled as such.

**The practice.** A method applied without a citation is not checkable. A reader
cannot tell whether the choice is standard, contested, or invented here, and
cannot find the argument for it. Scattered citations hide this, because no file
is obviously incomplete; a register makes it arithmetic, and the arithmetic was
13 to 1. That is why the register earns its place beyond tidiness, and why the
count is worth recomputing whenever it is regenerated.

**One thing the register could not fix.** `ERRATA.md` 5.3 claims that waste
treatment is the dominant anthropogenic methane source at city scale in China.
Repeated searches found landfill and wastewater studies for other regions and
nothing supporting that claim for Chinese cities as stated. It is left in place
unsourced and flagged here rather than quietly cut, because the section's other
half — that the cited source does not support the retrofitting framing — is
sound and now carries Zhao et al. 2024, a mobile-measurement study finding the
natural gas distribution system of a Yangtze River Delta megacity to be a low
emitter. If 5.3 is narrowed, that is what it narrows to.

## Our spatial blocks are unbuffered, and the block size is the reason it may not matter

Recorded as a known limitation rather than acted on.

The spatial cross-validation literature splits data into blocks so that training
and validation are not drawn from the same dependence structure, and its variants
exclude observations within a buffer of the validation set for the same reason.
Neither of this repository's schemes buffers. The spatial blocks are 4 by 4 cells
in five folds with no exclusion zone, so a cell on one side of a block seam and
a cell on the other sit in training and test at 25 km separation.

What the literature supports is the principle rather than a quantification.
Roberts et al. (2017, doi:10.1111/ecog.02881) establish that dependence in the
data persists as dependence in the residuals and that random splits are
over-optimistic in consequence. Valavi et al. (2019,
doi:10.1111/2041-210X.13107) supply the operational step: measure the spatial
autocorrelation range in the covariates and choose the block size from it.
Neither abstract quantifies what an unbuffered seam costs, and the full texts
were not read for this, so no figure is claimed here.

This repository's own measurements bear on it in both directions. The methane
field's half-sill range over the 927 cells is **102 km**, and a 4 by 4 block at
0.25 degrees is about **111 km** across, so the block size is well matched to the
correlation length, which is what Valavi's procedure asks for. But at 25 km
separation the semivariogram shows methane has expressed only about **24 percent**
of its variance, so cells facing each other across a seam are strongly dependent,
and every block has a perimeter.

The direction of the resulting bias is what makes this worth recording. Seam
pairs help a model that predicts a cell from its neighbours, which is the spatial
null, more than they help a model that predicts from land cover, which has no
neighbour term. So an unbuffered scheme should if anything **inflate the bar** the
land-cover models fail to clear. The negative finding is therefore not threatened
by this, and might be understated by it. Buffering would be the way to find out
and is not done here.

## The errata made the error the errata documents

The reference register's second useful finding was an unsourced claim, and it
was found by trying to cite the claim rather than by reviewing it.

`ERRATA.md` 5.3 asserted that waste treatment, meaning landfill, incineration
and sewage, is the dominant anthropogenic methane source at city scale in China,
and used that to argue the thesis's attribution of urban methane to natural gas
vehicles was misplaced. Four rounds of searching returned landfill and
wastewater studies for other regions and nothing supporting the claim for
Chinese cities as stated. Nobody had reviewed the section and doubted it; the
claim only failed when someone tried to put a DOI next to it.

**The symmetry is exact and worth stating plainly.** `ERRATA.md` 5.3 criticises
the thesis for describing a mechanism its own cited source does not report: the
thesis frames urban methane as retrofitted vehicles and faulty tailpipes, while
Da Pan et al. (2020, doi:10.1038/s41467-020-18141-0) measured heavy-duty
vehicles against emission standards and described neither. The errata then did
the same thing one paragraph later, asserting a sectoral dominance no source it
could name supported. A document whose purpose is to catch claims stated more
strongly than their sources allow made that error itself, in public, and kept it
until the register forced the question.

5.3 now says only what is sourced: that the cited source does not report the
thesis's mechanism, that a mobile-measurement study in this region finds the gas
distribution system a low emitter, and that a regional inversion puts
agricultural soil largest at 29.6 percent. The absence of a waste layer in the
thesis is recorded as an omission from its source inventory rather than as a
claim about how large waste is, because that is the difference between what can
and cannot be supported.

**Why the register sits beside the claims.** A claim about the world is only as
good as the citation beside it, and a citation in `notes/references.md` that
nobody reads while reading the claim is barely better than none. That is why the
method citations were placed in `ERRATA.md` and `data/processed/README.md` at the
point of use rather than only in the register. The register's value is that it
makes the arithmetic visible; the citation's value is that it is where the reader
already is.

## Twelve more claims about the world are uncited

An audit prompted by 5.3 went through `ERRATA.md`, `README.md` and
`data/processed/README.md` looking for the same shape of claim: an assertion
about the world rather than about the thesis, the notebook, or a committed
artefact. Claims of the first kind are checkable against a file; claims of the
second are not, and are the ones at risk.

There are twelve, which is more than a handful and so a larger problem than one
section. **Nine have no source anywhere:**

| where | claim |
|-------|-------|
| ERRATA 2.3 | 1.8 million km2 is the Yangtze's drainage basin area, not its extent |
| ERRATA 2.4 | TROPOMI nadir resolution was refined to about 7 by 5.5 km in August 2019 |
| ERRATA 3.3 | ImageNet channel statistics are only meaningful with an ImageNet-pretrained encoder |
| ERRATA 4.2 | convolutional networks are approximately translation equivariant and are not scale invariant |
| ERRATA 5.1 | four categories of post-2023 reference dataset exist; none is named or cited |
| ERRATA 5.4 | current syntheses give methane GWP as 28 to 36 over 100 years and 84 to 87 over 20 |
| ERRATA 6.2 | a Moran's z-score scales with feature count, and column autocorrelation follows from transport and retrieval binning |
| processed README | the literature reports a seasonal surface-albedo bias in TROPOMI methane over agricultural land |
| processed README | the instrument is known to fail over dark steep terrain |

**Three have a source in the register but no citation at the point of claim:**
the GAIA omission error and its 28.35 percent producer's-accuracy figure, in
`README.md` and `data/processed/README.md`, which come from the GISA paper
(doi:10.1007/s11430-020-9797-9); the documented albedo dependence and its
operational correction in `README.md`, which is Lorente et al.
(doi:10.5194/amt-14-665-2021); and the claim that the reference data the thesis
said did not exist has since been published, which is partly Shen et al.
(doi:10.5194/essd-15-3203-2023) but names two other products that are still
uncited.

None of these is fixed here, deliberately. The list is recorded first because
the pattern is the point: the errata and the READMEs accumulated background
assertions that read as common knowledge and were never tested, exactly as 5.3
did. Several will be easy, some are textbook facts that still need a textbook,
and ERRATA 5.1 may need narrowing rather than citing, as 5.3 did.

## The errata's own correction was wrong, which makes two

The twelve uncited claims were closed on 3 September 2026. Ten now carry a
verified citation; five were narrowed to what could be sourced. One turned out
not to be uncited but wrong, and that is the finding worth keeping.

**ERRATA 5.4 corrected the thesis using a figure more dated than the thesis's.**
It criticised the thesis for giving methane's global warming potential as 25 to
30 from a 2011 source, and offered "approximately 28 to 36 over 100 years and 84
to 87 over 20 years" as the current values. Read directly from the chapter PDFs,
IPCC AR6 Table 7.15 gives GWP-100 as 29.8 ± 11 for fossil methane and 27.0 ± 11
for non-fossil, and GWP-20 as 82.5 and 79.7. The errata's figures are
approximately AR5 of 2013, whose Table 8.7 gives 28 and 34 for GWP-100 and 84
and 86 for GWP-20; neither 36 nor 87 is in that table either.

**Both AR6 central values fall inside the thesis's range of 25 to 30. The
errata's range excludes one of them.** The correction was further from the
current assessment than the thing it corrected, and it was published as a
criticism for as long as the errata has existed. What survives is the
substantive point, which was always the real one: a GWP figure without a time
horizon means nothing, and AR6 additionally distinguishes fossil from
non-fossil methane, which neither the thesis nor the earlier errata did.

**Two instances is a pattern about how this errata was written.** The unsourced
waste claim in 5.3 and the dated GWP figures in 5.4 arrived the same way: from a
search snippet, plausible on its face, written into a public document criticising
someone else's sourcing, and never checked. The errata is careful wherever it
checks the thesis against the thesis, because that is checkable and was checked;
it was careless wherever it reached outside for a comparison, because nothing in
the writing process forced a citation. The register is what forces it now.

## What could not be sourced, and was narrowed instead

Five claims had no citable source and were narrowed rather than left standing.
Recorded so the narrowing is visible as a decision rather than as an edit.

`ERRATA.md` 2.3 said 1.8 million km2 is the Yangtze's drainage basin area. No
citable source for the basin area was found, so the item now rests only on the
unit mismatch, which is checkable from the sentence: an extent is a length and
cannot be given in square kilometres. Whether the thesis's own cited source
gives the figure as a basin area, which would make the error descriptive rather
than numerical, was not established.

`ERRATA.md` 2.4 said TROPOMI's nadir resolution was refined to about 7 by 5.5 km
in August 2019. That change is in mission documentation rather than a citable
work and no source for the date or dimensions was found, so it is withdrawn. The
7 by 7 km design figure is now cited to the instrument paper, and is in any case
the right figure for 2018.

`ERRATA.md` 3.3 said ImageNet channel statistics are only meaningful with an
ImageNet-pretrained encoder. That is a practitioner convention, not a theorem,
and is now stated as one. The item's weight rests on the frozen random backbone,
which is checkable from the notebook.

`data/processed/README.md` said the literature reports a *seasonal* surface-albedo
bias in TROPOMI methane over agricultural land. Lorente et al. support the albedo
dependence and the correction but say nothing about seasonality, so the seasonal
element is dropped.

The same file said the uncovered cells are "dark steep terrain where the
instrument is known to fail". That bundled our own measurement with a claim about
the literature. The terrain description is ours and stands; the retrieval
difficulty is now cited for low albedo only, and the slope half is not claimed.

## Figures are built by a module that returns them and an exporter that verifies

Every figure in this repository is drawn by a function that returns a figure
object and writes nothing. Writing is done by one exporter, which produces the
vector and the raster from the same object in a single call and verifies both
before either reaches its destination.

The separation is what makes the venue standard testable rather than
aspirational. Because a figure function only returns, a figure can be built and
asserted on in memory with no filesystem at all; because the exporter knows
nothing about content, its refusal to write an out-of-spec figure is tested
with a blank one. If figures wrote as a side effect, neither test could exist
and the standard would be a comment in a docstring.

The exporter writes to temporary paths in the destination directory, measures
what it wrote, and moves the files into place only once every check passes. The
checks are resolution, width, and byte size, and the resolution is recovered
from the PNG header rather than trusted from the request. The reason for the
temporaries is specific: a failed export that leaves a partial file behind is
worse than one that leaves nothing, because on the next run a stale file looks
like a current one. A figure that is out of spec produces an error and no file.

Generated figures go to `figures/` at the repository root, which is where
`notes/repository-architecture.md` said they would go before any existed and
where the README already points. The destination is overridable through
`FIGURES_DIR` so that tests never write into the working tree.

## The scientific colour maps install, so the fallback is not load-bearing

`cmcrameri` installs cleanly here and is pinned at 1.10. Crameri's maps are
what the target venues ask for by name, and the reason is not aesthetic: a
colour map that is not perceptually uniform shows gradients that are not in the
data and hides gradients that are.

The 2023 thesis figures fail this test, and the failure already cost something.
Their red-orange-yellow-green ramp flattens to nearly the same grey at both
ends, which is why an identification made from those figures had to be reversed
after checking the PDF, as `ERRATA.md` records.

The palette module keeps a fallback to matplotlib's perceptually uniform maps
for an environment without `cmcrameri`, and exposes `PALETTE_SOURCE` saying
which resolved. The fallback is a weaker substitute, not an equivalent, so the
point of naming the source is that a figure can never be drawn in the wrong
scheme without the fact being recoverable.

## The first figure: what the saturation curve is allowed to claim

The saturation curve is plotted against **productive granules**, not granules
processed. Processing order is arbitrary, so on an axis of granules processed
the position of any mark means whatever the streaming loop happened to do
first. Of 578 granules acquired, 356 returned no qualifying sounding, and a
granule that returned none cannot have covered a cell, so those rows are flat
by construction and put more than half the axis under segments carrying no
information.

Replotting changed the curve's **shape** much less than expected. The area
under the normalised curve moves from 0.7840 to 0.7916, under one percent. The
knee, taken as the point of maximum vertical distance above the chord, is the
same granule on both axes and sits at the same coverage, 66.57 percent; only
its relative position along the axis moves, from 10.2 to 7.2 percent. The
reason is that unproductive granules are spread nearly uniformly through the
processing order, so removing them is close to a uniform rescaling by
578/222 = 2.60, and a uniform rescaling cannot change the shape of a curve read
against a normalised axis. The ratio of granules needed to reach a threshold is
2.56 to 2.61 across the upper range and only rises at the very start, which is
what moves the knee left.

So the change is justified by what the axis *means*, not by what it looks like.
The honest claim is that a mark at *n* is now a sample of *n* granules that
returned data, comparable to a sampling design, rather than an artefact of
order.

A related premise also failed. Most of the flatness is not caused by
unproductive granules. Only 81 granules of the 578 ever added a cell, so 86.0
percent of steps are flat on the processed axis and 63.5 percent are still flat
on the productive axis. The flatness is saturation, which is the panel's whole
subject, not an artefact to be removed.

The endpoint is not marked. It is the endpoint and the axis already says where
it is.

## The reconnaissance number is not a point on any single year's curve

The mark at 36 granules is the reconnaissance's **sample size**. It is not the
reconnaissance's coverage result, and the two must not be read against each
other, because the reconnaissance sampled one granule on the fourteenth or
fifteenth of alternate months across **seven years**, thirty-six granules of
which only six fall in 2018. Its 56.11 percent is the union over that
seven-year pool. A 2018 curve has no point that corresponds to it.

For completeness, the 2018 curve reaches 54.45 percent at six productive
granules, which is the reconnaissance's 2018 sample size and lands within 1.7
points of what it reported. That closeness is suggestive and it is not offered
as more: both numbers remain one ordering of one sample, and thirty granules
from six other years apparently bought the reconnaissance almost nothing, which
would be worth a separate measurement rather than an inference here.

The 50.4 percent free-asymptote fit is still **not drawn**, for the reason
recorded earlier: it was fitted on the 0.1 degree grid of 6,396 cells and this
figure is the 0.25 degree grid of 1,023. Coverage fractions are not comparable
across cell sizes, since a coarser cell is easier to hit.

## Panel (c) keeps granule counts and annotates the yield

The finding in the monthly panels is the ratio: 154 soundings per granule in
July against 1,100 in October, a factor of 7.2, with the minimum landing on the
flooded-paddy season the study is about.

Panel (c) still plots productive granule counts rather than yield, because the
count is the **control**. The summer sounding shortfall only means something
once it is clear the satellite passed over more often in summer, not less. Plot
yield alone and a reader can reasonably conclude there were simply fewer
overpasses in July, which is the opposite of the truth: June to August carry 92
productive granules against October's 31.

Plotting counts and stacking the panels makes the ratio derivable but leaves it
uncomputed, so the two extreme months are annotated with their yield in italic,
with one in-figure line defining what the italic numbers are. Two annotations
rather than a number on every bar, and the two chosen are the minimum and the
maximum, so they bound the range. This is the venue's own preference, which is
that a legend clarifies symbols inside the figure rather than in caption prose.

## Figure width: the venues specify a floor and nothing else

ACP, AMT and ESSD all state one figure dimension, in identical wording: "The
width should not be less than 8 cm." None of them gives a single-column or a
full-width figure size. There is therefore no venue width to conform to, only a
minimum, and the question of whether a figure is single-column or full-width is
this project's to decide.

The project default is full width at 17.0 cm, set in `src/figures/style.py` as
`FULL_WIDTH_CM` so the other eight figures inherit it from one place.
`COLUMN_WIDTH_CM` is 8.3 cm and exists for figures that should be narrow; the
choice is per-figure and deliberate rather than a number repeated nine times.
Both are measured from the typeset two-column page and neither is quoted from a
guideline, which the comment beside them says.

This figure does not work at column width, and it was rendered at 8.3 cm and
looked at rather than reasoned about. Three panels across 8.3 cm give each
about 4 cm, and panel (a)'s legend is wider than that on its own, so the legend
runs off the plot, the y-axis label collides with the neighbouring panel and
the yield annotations overprint each other. Making it work would need a
different arrangement, three panels stacked in one column and taller than it is
wide, not an adjustment. Full width for a panelled figure is the standard here.

The same research corrected the export path. Copernicus sets two size limits,
not one: individual PDF figures must not exceed 2 MB while other formats must
not exceed 5 MB. The exporter had been applying 5 MB to both, so the vector
form is now held to the tighter ceiling.

## Absent months, and the mark that must not be clamped

January through March are shaded and labelled in place rather than drawn as
zero-height bars, because a zero bar and a missing bar look identical and mean
opposite things. April, at one granule and 290 soundings, is annotated with its
count for the same reason: its bar is a fraction of a millimetre at this scale
and would otherwise read as part of the absence beside it. The same distinction
will be needed for the 96 cells the composite never covered, and it should be
made the same way there.

The shading is labelled with text placed inside it rather than through a legend
key. A grey key for a grey span sits on the span it describes and is invisible,
which the first draft demonstrated.

The sample-size mark is **not drawn at all** on a curve too short to reach it,
rather than clamped onto the last point. A mark at the reconnaissance sample
size says "this is what a sample that size reaches"; slid onto the endpoint of
a shorter curve it would say the sample reached everything, which is the
opposite. The first implementation clamped, and a test on a short record caught
it.

Reading the checkpoint now refuses two disagreements rather than absorbing
them. The saturation record and the contribution record must have the same
number of granules in the same order, and no granule without an in-box sounding
may have increased coverage. Either would mean the curve was being built from
records that do not describe the same run, and dropping rows would make it
silently wrong instead of obviously wrong.

## The map projection, and why it is not an equal-area one

Every map in this repository is drawn equirectangular with its standard
parallel at the centre of the study area. Coordinates stay in degrees and the
axes aspect is set to cos(31.075) = 0.8565, so a degree of longitude is drawn
0.8565 times as long as a degree of latitude, which is what it is on the ground
there. The constant lives in `src/figures/geo.py`, not in any figure, because
seven more figures need it.

Three facts decided it, all of them already in the repository.

The analysis lattice is defined in geographic coordinates, so in this
projection its cells stay axis-aligned rectangles and a reader can count them
against the boundaries. In a conic projection the same lattice fans and curves.
That is honest about the geometry and much harder to read, and reading it is
the whole purpose of drawing it.

The projection carries no analytical weight. Areas here are computed
analytically on the authalic sphere and were validated that way to within 0.13
percent; nothing is ever measured off a map. An equal-area projection would buy
accuracy in a quantity no figure reports.

And the easy default is wrong in a way worth naming. Plate carree without the
aspect correction draws this study area **16.8 percent too wide** east to west.

What it distorts, stated rather than hidden: scale is exact only at the
standard parallel, running 3.9 percent small at the southern edge of the box
and 4.8 percent large at the northern. Area is not preserved, and because every
drawn cell is the same size while a cell at 26.95 N covers 9.1 percent more
ground than one at 35.2 N, the map slightly overstates the north. None of it
reaches a number.

This is not the 2023 choice. `ERRATA.md` 2.4 records those figures as
ESRI:102029, Asia South Equidistant Conic, standard parallels 7 N and 32 S for
a study area at 31 N, in which a one degree box here measures 26.89 percent
larger than the geodesic truth.

The locator inset is the exception and uses `CHINA_ALBERS`, the equal-area
conic this project already uses for area measurement. An inset spans most of
China and an equirectangular map of that extent is badly stretched at its
northern edge. Two projections in one figure is a cost; a locator that
misrepresents the country it locates against is a worse one.

## The declared study box and the drawn one differ on two edges

`GridSpec` rounds its shape, and for this grid it rounds in **both** axes and
in **opposite directions**. Longitude: 7.8 degrees is 31.2 cells, rounded down
to 31, so the lattice stops short of the declared east edge and ends at 122.55
rather than 122.6. Latitude: 8.2 degrees is 32.8 cells, rounded up to 33, so
the lattice runs *past* the declared south edge and ends at 26.95 rather than
27.0.

The east edge was already known and is recorded in `src/grid/cells.py`. The
south edge was not, and it is the more dangerous of the two because it extends
beyond the declared box rather than falling short of it.

`geo.lattice_extent()` derives all four edges from the grid specification, and
every map uses it. A map drawn to the declared bounds would disagree with its
own data by one cell at two of four edges, and the disagreement would be
invisible to inspection.

## Map colours are set for greyscale first

A study-area map has three areal classes, and a black and white print has to
keep them apart, so `style.py` fixes sea, land and study-provinces at
luminances of 0.62, 0.96 and 0.80, a minimum pairwise gap of 0.16. They are
derived from batlow by mixing toward white rather than picked by eye, so maps
and data panels stay in one colour family.

The lattice line is much darker than any fill it crosses, at 0.35. An earlier
draft used a mid grey within 0.03 luminance of the study fill: it looked
correct in colour and disappeared entirely in greyscale. Both constraints are
now asserted by tests rather than left to the next person's judgement.

Provinces are distinguished by boundary and by name, not by four separate
fills. Four fills plus land and sea is six areal classes, and six classes
cannot all be 0.15 apart in luminance on a zero-to-one scale without some of
them being too dark to read a label on. The names carry the identity, which is
what names are for.

## The study area map shows the grid extent and not the coverage

The map does not distinguish the 927 cells that carry methane from the 96 that
do not. That was a real choice and it cuts both ways: showing the analysis
extent without saying that 9.4 percent of it is unobserved overstates the
coverage, but drawing the coverage mask here would pre-empt the composite
figure, whose central problem it is, and split one argument across two figures.

The resolution is that the caption states the fraction and names the figure
that shows which cells. A reference map's job is to orient, and a reader who
learns the coverage number in the caption is not misled by a map that does not
draw it.

## The lattice is drawn at every cell edge, weighted in two grades

Sixty-six lines will fight the province boundaries if they are all drawn alike.
Cell edges are drawn as light as a 300 dpi raster will hold and every fourth
line, which is a whole degree, slightly heavier, so the reader gets the grid as
a texture and the graticule as structure from one set of lines rather than two
overlaid. There is no separate background graticule; the venue standard forbids
gridlines and the lattice is the only grid on the map.

## The map is not full width, and that is the point of having a default

`style.py` sets `FULL_WIDTH_CM` as the project default and says that a figure
which should be narrow passes its own width deliberately. This is the first
figure to do so. Its extent draws 1.24 times taller than wide, so at 17 cm the
map would have sat in a band of white with the drawing itself no larger, and
the figure is 11.4 cm instead.

The height is not chosen at all. `geo.figure_height_cm()` derives it from the
extent and the width, so a map fills its figure rather than being fitted into
one whose proportions were picked first. The remaining map figures inherit
that, and the first draft of this one showed why: at a hand-picked 17 by 11.4
cm the map occupied about two thirds of the width.

## What the map leaves out

No north arrow: the map is north-up and the graticule says so. No scale bar:
the graticule carries scale, and a scale bar on an equirectangular map is only
correct along one parallel, so it would assert a precision the projection does
not have. No coordinate-system caption baked into the image, which every 2023
ArcGIS export in `legacy/figures/` carries. No drop shadows, no decorative
elements, no background gridlines.

The one piece of non-data ink is a white halo behind each province name. It is
not decoration: without it a name crossing a boundary line is unreadable, and
the alternative is moving the name off its own province.

## The declared box and the lattice were two different objects

**A note on the figures throughout this file.** The 2018 composite was rebuilt
against the reconciled extent, and the headline numbers moved with it: coverage
from 927 cells and 90.62 percent to 926 and 90.52, soundings from 110,928 to
110,920, productive granules from 222 to 223, the rice subsample from 532 cells
to 531.

**This file is not maintained against those figures, and should not be.** It is
a decision log: each section records what was measured and believed when a
decision was taken, and the reasoning that followed. Rewriting those numbers to
today's values would destroy the thing the file exists to preserve. Sections
written before the reconciliation therefore still quote 927 cells and a 532-cell
rice subsample in places, and that is correct as a record even though it is not
the current value.

An earlier version of this note claimed the opposite, that "earlier sections
have been updated to the current values". That was inaccurate in both directions:
some coverage figures had been updated and several sample sizes had not, so the
file was neither a clean record nor a current one. The policy is now the first
of those. Current values live in `data/processed/README.md`, where they are
marked and checked by `tests/test_prose_claims.py`; this file is excluded from
that check deliberately.


The study box was declared as 114.8 to 122.6 east, 27.0 to 35.2 north. The
lattice built from it occupied 114.8 to 122.55 and 26.95 to 35.2. The two were
never the same region, and the rounding that separated them ran in **opposite
directions on the two axes**.

Longitude: 7.8 degrees is 31.2 cells at 0.25 degrees, rounded **down** to 31,
so the lattice stopped 0.05 degrees **short** of the declared east edge.
Latitude: 8.2 degrees is 32.8 cells, rounded **up** to 33, so the lattice ran
0.05 degrees **past** the declared south edge. One edge fell inside the
declared box and the other outside it, which is why noticing the first did not
lead to the second.

Two modules then disagreed about where the study area was. `src/grid/cells.py`
filtered land-cover pixels against `lattice_edges` and dropped anything
outside, which is correct. `GridSpec.cell_of` filtered soundings against the
declared box and then clipped the row and column into range. The consequences
were opposite at the two edges:

* **East.** Soundings between 122.55 and 122.6 passed the filter, computed
  column 31, and were clipped into column 30, a cell they do not lie in. The
  composite's easternmost column carried soundings from 0.30 degrees of ground
  in a 0.25 degree cell.
* **South.** Soundings between 26.95 and 27.0 failed the filter and were
  discarded, although cells existed there. The southernmost row was sampled
  over 0.20 of its 0.25 degrees.

The measured containment: 59 of 927 covered cells touched, 1,683 soundings or
1.52 percent, but **53 of those 59 cells lie entirely outside the four study
provinces**. Only 6 of the 557 province-weighted cells were affected, 1.1
percent, with a median province share of 0.0000 against 0.5820 for the table as
a whole. The east edge carried the visible artefact: column 30 exceeded column
29 by a factor of 1.168 against the 1.20 predicted by absorbing a 0.05 degree
strip, and the excess was broad and uniform, 1.167 as a median across the 31
rows where both columns had data, rather than concentrated.

## The fix is in the configuration, not in the binning code

The box now declares 26.95 and 122.55, the extent the lattice occupies.
`round((122.55 - 114.8) / 0.25)` is 31 and `round((35.2 - 26.95) / 0.25)` is 33
exactly, so declared and derived are one object and `cell_of`'s existing filter
is correct as written, with its clipping path unreachable for any real
coordinate.

Teaching `cell_of` to filter against `lattice_edges` would have worked equally
well at the east edge and been equally correct. It was rejected because it
leaves the configuration declaring a region the data does not occupy, so every
caption, README line and future filter that quotes the box would still be
quoting the wrong thing, and the next module to read the config would face the
same choice again. A discrepancy that has to be worked around in every consumer
is worse than one removed at the source.

## How it was found, which is the more transferable lesson

Both constituent facts were already written down, in `data/processed/README.md`,
**three lines apart**. Line 366: "Clipping is what `GridSpec.cell_of` does to
soundings." Line 371: "The same rounding applies to the southern edge, where 33
rows reach 26.95 rather than the declared 27.0." Neither statement was wrong.
Neither was even incomplete. Their **conjunction** was a bug, and nobody had put
them together, including whoever wrote them in the same paragraph.

It surfaced only when a figure had to draw the extent. Prose can hold two
compatible-sounding sentences indefinitely; a map has to put a line somewhere,
and choosing where forces the question of which number is right. **Drawing a
thing forces a decision that prose can leave ambiguous**, and that is a
different discovery mechanism from review. It is worth reaching for
deliberately: rendering a quantity is a cheap way to find out whether the
repository actually agrees with itself about what the quantity is.

Review would not have found this. Every individual statement passes review.

## A declared extent and a derived lattice are different objects

The general caution, because it will recur. A lattice built by rounding a
declared extent to a cell size **will not in general occupy that extent**. The
two coincide only when the extent divides evenly, which is a property of the
numbers and not something the code enforces or the reader can assume.

So any figure, caption, filter or selection that quotes the declared box is
quoting a region the data may not occupy. Derive the extent from the cell count
and use that everywhere, and if the declared and derived values are meant to be
the same, assert it. `tests/test_study_extent.py` does exactly that, with both
sides derived, so a future change to the box or the cell size fails loudly
instead of reintroducing the gap.

The same applies to any quantity obtained by rounding a continuous
specification to a discrete one: the rounded object is not the thing it was
rounded from, and code that treats them as interchangeable is correct only by
coincidence.

## What the re-run changed

The 2018 composite was rebuilt against the reconciled extent rather than the
fix being left to apply only to future runs, because this repository's argument
is that everything regenerates from committed code against one definition, and
a composite built under a superseded extent undercuts that more than an hour of
transfer costs. The pass took 122.7 minutes at 4.0 MB/s for 28.9 GB.

**49 cells changed, and nothing outside the two edge strips changed at all.**
19 in the southern row and 30 in the eastern column, 0 elsewhere. The maximum
absolute difference is 5.44 ppb in bias-corrected methane and 5.62 ppb in raw,
over 48 cells; one cell changed only in its count.

The soundings decompose exactly as the diagnosis predicted, with each edge
moving in one direction only:

* southern row 32: **+151 gained, none lost**, across 19 cells
* eastern column 30: **-159 removed, none gained**, across 30 cells
* everywhere else: **zero**

Net -8 soundings, 110,928 to 110,920. Coverage fell from 927 cells to 926,
because the cell at 30.325 N, 122.425 E held exactly one sounding and that
sounding came from the 122.55 to 122.6 strip, so it was never inside the cell.
Productive granules rose from 222 to 223, because one July granule's only in-box
soundings lay in the southern strip and had been discarded whole, leaving it
recorded as barren. The rice sample fell from 532 cells to 531 with the dropped
cell; the 395 cells with no rice fraction are unchanged.

**The negative land-cover finding is unaffected: still zero of 176 weighted
opportunities.** Unweighted exceptions rose from 8 to 12 of 176, still spread
across all four predictor pairs and still small, with the largest margin below
the null falling from 5.97 to 5.44 percent. That the unweighted count moves
while the weighted count does not is what one would expect: the cells that
changed carry few soundings, so they weigh almost nothing under inverse-variance
weighting and comparatively much unweighted.

The study-area figure is byte-identical before and after, which is the
confirmation that it was drawing the true lattice all along and that only the
declaration was wrong.

## Two committed artefacts whose stated recipe does not reproduce them

Found while propagating the re-run, and worth recording because both would waste
someone's afternoon.

`impervious_gisa_2018.csv` carries four columns, but
`scripts/build_analysis_grid.py` has no flag that produces four; it always
writes the full grid. The committed file was reduced afterwards and the
reduction was never written down. Running the documented command overwrites it
with a fifteen-column file that every consumer still reads, so nothing fails.

`analysis_grid_2018.csv` is documented as regenerable with `--rice-source
scidb`, which is the reproducible anonymous product, but the committed table was
built with `--rice-source nesdc` from the FTP rasters for the double-season
class. Building it the documented way changes `rice_fraction_combined` in 190
of the rows, every one a decrease, and changes nothing else. The script's own
docstring records this and the README's recipe did not, so following the README
silently downgrades the table. The recipe now says which command reproduces the
committed file and which reproduces everything except that one column.

The general point: a regeneration recipe that is *nearly* right is worse than
none, because the output looks plausible and no test fails. Both of these were
caught by diffing every regenerated file against a snapshot of the committed
one, column by column, rather than by checking that the scripts ran.

## Regeneration recipes drift, because nothing was checking them

Three recipes in this repository did not produce the artefacts they claimed to,
and a fourth artefact had no recipe at all. None of it made a test fail.

`impervious_gisa_2018.csv` is committed with four columns. The documented
command wrote fifteen. The committed file had been reduced by hand and the
reduction was never written down, so anyone following the README got a
different file, and every consumer kept working because nothing reads the extra
columns. Fixed by adding `--impervious-only`, which makes the reduction part of
the script rather than part of somebody's shell history.

`analysis_grid_2018.csv` was documented as regenerable with `--rice-source
scidb`. The committed table was built with `--rice-source nesdc` from the FTP
rasters. Both sources are legitimate and the difference is confined to
`rice_fraction_combined`, in 190 rows, every one lower because the anonymous
product folds the double-season class into background. Neither side is wrong,
so the fix was neither: the documentation now says which source produced the
committed file and what the other one costs.

`urban_area_by_province_gisa.csv` is produced by nothing. It was committed in
f6b1b0c alongside `impervious_gisa_2018.csv`, a commit that added two artefacts
and no code for either. It is now registered as `unregenerable` with its
provenance, which is a declaration rather than an omission.

And README.md claimed that "each compute script compares against the committed
values before writing and refuses to overwrite a row that differs by more than a
tenth of a percent". That is true of two scripts out of eleven. It is the
property that would have caught the rice-source substitution, and believing the
repository had it is part of why nobody looked.

## The mechanism: recipes as data, documentation generated from it

`config/recipes.yml` holds every recipe as a record: the artefact, the exact
command, its measured cost, whether its inputs are committed or gitignored, how
the output is compared, and which verification tier it sits in.
`tests/test_recipes.py` executes it. The regeneration table in README.md is
generated from it by `scripts/verify_recipes.py --update-readme`, and a test
asserts the committed README still matches, so the command a reader is shown and
the command that is tested cannot diverge.

Three tiers, and the repository says which is which rather than implying
everything is equally verified:

* **continuously**, seven artefacts whose every input is committed. They run in
  the default suite, in about a second each, on a fresh clone.
* **on_local**, eight that need `data/raw/` or `data/interim/`, both gitignored.
  Marked `slow`, excluded from the default run, invoked with `pytest -m slow`,
  and skipping with a stated reason where the data is absent. About six minutes,
  nearly all of it rebuilding the analysis grid.
* **on_demand**, six composite outputs behind a 28.9 GB transfer. A checksum is
  recorded and asserted, which catches a stale or hand-edited artefact but **not**
  a drifted recipe, and the registry records the date each was last verified by
  actually running the command. That limitation is named in the tier's own name.

A fourth category, `unregenerable`, exists for the one artefact nothing
produces, so that the honest case and the forgotten case do not look alike.

Two smaller things fell out. PDF figures were not byte-reproducible, because
matplotlib stamps `/CreationDate`; dropping it makes both figure formats
comparable, and without that a test could only check the raster. And
`test_every_committed_artefact_has_a_recipe` now fails if an artefact is added
without one, which is the specific hole that let the GISA files in.

## A recipe is a claim, and an unchecked claim drifts

The transferable point. A regeneration command in a README is a claim about the
repository: run this, get that file. This repository's whole argument is that
its results regenerate from committed code, and that argument is worth exactly
as much as its weakest recipe. A claim nothing executes will drift, and it will
drift silently, because the failure mode is a plausible file rather than an
error.

Worth noting how both of this project's structural findings surfaced. The extent
discrepancy appeared when a figure had to draw the study area, forcing a
decision that two compatible-sounding sentences of prose had left open. The
recipe drift appeared when a re-run regenerated everything downstream and the
outputs were diffed column by column against a snapshot. **Both were found by
doing rather than by reading**, and neither would have been caught by review,
because every individual statement involved was true. Review checks whether
each claim is defensible; it does not check whether the claims still describe
the artefacts. Only executing them does that.

The corollary is that the diff was the instrument, not the re-run. Re-running
produced the outputs; comparing them column by column against the committed
ones is what turned "the scripts ran" into "the scripts reproduce". Checking
that a pipeline runs is not checking that it reproduces, and the two are easy
to confuse because both end in a green result.

## Prose goes stale when the artefact under it moves

The third drift class. Recipes drifting from artefacts is closed by
`config/recipes.yml`. Artefacts drifting from the sentences that quote them was
closed by nothing, and it had already happened: the extent re-run moved values
in every regenerated table, and eight figures in README.md and ERRATA.md went
stale. They were caught by a manual sweep minutes before a push. A fuller sweep
afterwards found twenty more in `data/processed/README.md`, which the first
sweep never reached, including every median in the covariate table.

Each was correct when written. That is what makes this class hard: nothing is
wrong at the moment of writing, and the failure is introduced later by an
unrelated action somewhere else.

### Three classes of number, and only one may be checked

A blanket correction would be wrong, not merely noisy.

**Derived from a committed artefact.** These are the drift risk and the only
ones worth watching. Cell counts, sample sizes, medians, correlations.

**Stable properties of external things.** A DOI, a granule's byte count, the
twelve layers of a TROPOMI profile, an accuracy figure from a cited paper, a
year. These never change and need no mechanism. A checker that touched them
would be pure cost. Two live examples of why a find-and-replace on a bare
number is unsafe: `10.1017/CBO9781107415324.018` contains the string 532, and
a provincial table holds the total 39,532.2.

**Historical records.** `notes/decisions.md` is full of these by design; each
section states what was measured when a decision was taken. Updating them would
destroy the record and, worse, would silently rewrite the evidence an argument
rests on. `data/processed/README.md` also carries one such sentence on purpose,
stating the composite's figures before the reconciliation, and it is left
unmarked so the check leaves it alone.

### The mechanism, and what it does not do

A claim is marked where it lives, in the sentence: the number is followed
immediately by an HTML comment naming the quantity, of the form `<!--` then
`#grid.rows` then `-->`. It is written here in pieces because a decision log
must not contain anything that reads as a live marker, to a tool or to a person.
The comment renders as nothing, so a reader sees only the number, and it travels
with the sentence, so it cannot drift from its claim. `scripts/verify_claims.py` computes each named
quantity from the artefact; `tests/test_prose_claims.py` asserts the written
number and the computed one agree at the precision the sentence itself chose,
so a rounded figure is not treated as drift.

The alternative was a table of claims maintained beside the prose. That is
precisely the failure this repository already had, in the README regeneration
table, and repeating it here would have been the same mistake in a new place.

**It errs toward false negatives, deliberately.** An unmarked number is not
checked, and 38 claims are marked against roughly 1,400 unmarked numbers in the
scanned files. The reasoning is the cost asymmetry, read the other way round
from the obvious: a check that fires on DOIs, years and the historical record
would produce thousands of failures that must never be "fixed", and a check
that noisy does not have a high false-positive rate, it has a short life. It
gets suppressed, and then the false negative rate is one hundred percent. A
narrower check that survives is worth more than a broad one that does not.

The consequence is stated rather than hidden: `verify_claims.py --coverage`
reports the unmarked count per file, and a test asserts that at least thirty
claims are marked, so the check cannot pass by having quietly found nothing.
Marking a figure is a judgement made once, at writing time, which is also the
only moment anyone knows which of the three classes it belongs to.

What fails, and when: regenerate a table, and the default test suite fails
immediately on `test_every_marked_claim_matches_the_data`, naming the file, the
line, the quantity, what the prose says and what the data says.

### Verifying a published correction needs the content, not a signal that it changed

A caution in its own right, from the push that preceded this. Every substitution
in that correction happened to be the same character length: 0.096 to 0.095,
+0.561 to +0.560, 927 to 926. The file's byte count was identical before and
after, and so was its length on the CDN.

The raw endpoint then served a cached pre-correction copy. Nothing about size or
modification time could have distinguished the corrected file from the stale one,
because nothing about them differed except the digits. Only fetching the content
at an explicit commit ref and reading the passage settled it.

So: a published correction is verified by reading what it now says, at a pinned
ref, not by observing that something changed. "The file is different now" is not
evidence, and for a same-length edit it is not even available.

## A grep that finds nothing looks exactly like a grep that found nothing wrong

The most transferable thing the push turned up, and it is not about credentials.

The credential gate before that push ran a scan over every blob in the object
database and reported zero matches for the NESDC username and host. It also
reported zero for the control string. The intermediate file had been written to
`/tmp`, which is sandboxed in this environment, so the scan read an empty input
and matched nothing. A sweep that searched nothing and a sweep that passed
produce identical output: zero.

Re-run against the scratchpad it worked, and the numbers are worth recording as
the shape of a real result: **276 `authalic` pairs in tracked content across all
refs, and 40 matches across 108 MB of blob content**, against zero for every
credential pattern.

Every grep-based check from here carries a positive control: a string known to
be present, asserted to be found, in the same invocation as the thing being
looked for. Without it, "no matches" is not a finding, it is the absence of one,
and the two are indistinguishable from the output alone.

This generalises past credentials to any check whose passing condition is an
empty result. A test that silently collects zero items passes; a linter pointed
at no files reports no problems; a verification that skips everything reports
nothing wrong. `tests/test_prose_claims.py` and `tests/test_recipes.py` both
carry a minimum-count assertion for this reason.

## Drawing a field with holes in it

The composite figure had two design problems and neither had an obvious answer.

### Absence at map scale

97 cells of 1,023 carry no sounding and must read as absent rather than as a
low value. The coverage figure's solution, a shaded span labelled in place, does
not transfer: absence there was one contiguous block of three months, and here
it is 19 connected groups running from a 47-cell block over southern Zhejiang
down to eight isolated single cells. The same treatment has to work at both.

What was tried and rejected. **Leaving the cells unfilled** so the basemap shows
through: this gives absence two appearances, pale over land and dark over sea,
for one meaning. **Hatching and stippling**: a 0.25 degree cell is about 3.5 mm
on a 17 cm figure, which is two or three hatch lines, and at that size a hatch
is a texture the eye reads as a shade. **Outline only**, no fill: too weak
against a coloured field, and the 47-cell block becomes a grid of empty boxes
rather than a hole. **A mid grey fill**: collides with the middle of any
sequential ramp in greyscale.

What was kept is a near-white fill with a thin outline. Near-white is the
literature's convention for missing, and the outline is what makes a single
cell read as a deliberate mark rather than a light patch in a light part of the
ramp. The fill alone loses the eight singletons.

This forced a change to the ramp. Full batlow runs to luminance 0.85, leaving
only 0.11 between its light end and white, against this project's own
convention of 0.15 for anything carrying meaning. The ramp is therefore
truncated at 0.88 of its range, which brings the light end to 0.77 and opens a
gap of 0.20. The cost is a slightly shorter ramp; the alternative was an
absence colour indistinguishable from the top of the scale in a black and white
print, which is exactly what the colour convention exists to prevent.

### The count scale, 1 to 410

A linear scale puts the median of 74 at a fifth of the range and renders every
sparse cell the same colour, which is where the sampling structure lives: the
mixed-coast cells sit at a median of 6 soundings against 133 for land. A
continuous log scale keeps that distinction but is hard to read off a legend
and implies a precision a count of 2 does not carry.

What was kept is half-decade classes, 1-3, 4-10, 11-31, 32-99, 100-315 and 316
and above, with the legend drawn as equal boxes and the numbers at the class
edges rather than centred in them. That follows what the literature does, which
masks below a sampling threshold rather than encoding count as a gradient, and
a class boundary is a statement a caption can defend where a gradient position
is not. Six centred range labels also do not fit across half a 17 cm figure.

### Two panels, two ramps, and no third panel

The panels use different ramps. A shared ramp invites reading a colour across
them, and here that reading would be actively wrong: the high-methane cells and
the high-count cells are not the same cells.

The value panel is clipped to the middle 96 percent of cell means. The full
range is 106 ppb and that middle spans 59, so an unclipped ramp gives nearly
half its length to four percent of cells -- and those cells are the least
reliable in the composite, with a median count of 2 soundings in the top two
percent of values and 12 in the bottom, against 74 overall. The bar carries
arrow caps so the clipping is declared rather than hidden.

A third panel was rejected. The deseasonalised field is a candidate, since
removing the seasonal cycle changed no association and that is a finding, but
it is a finding about a *comparison* of model results and not about a map: two
nearly identical fields side by side show a reader almost nothing, and the
result already has a table. The coastal count contrast belongs with the
coverage figure, which is about sampling. Two panels well drawn beat three
cramped, and the panel that would have been added is the one whose message a
map carries worst.

### The basemap was drawn and never seen

Measured, not assumed: rendering the figure with the basemap set to a loud
colour produced **zero** visible pixels of it. The lattice covers all 1,023
cells of the extent, 926 in the mesh and 97 as absence, so a land and sea fill
beneath it is drawn and then entirely hidden. It was removed, which also cut
the vector file by a quarter. Ink that carries nothing is not free: it would
have told a later reader that the sea tone means something here.

That probe is worth keeping as a habit. A figure element can be present in the
code, correct in isolation, and contribute nothing to the image, and no test of
the code will say so.


## The palette is a set of roles, and a role knows what it is drawn against

Three figures existed and each had picked its own colours: the coverage curve
sampled four fixed positions along batlow, the composite used batlow and lipari
as ramps, and the study area map carried six constants named `MAP_*`. Nothing
was wrong with any of them individually and there was no shared language, with
six more figures to come.

`src/figures/style.py` now holds 16 **roles**. A role is a job on the page --
`sea`, `coastline`, `absent_fill`, `label_halo` -- carrying its colour, what
kind of mark it is, why it exists, and, the part that matters, the set of other
roles it is actually drawn **against**. A figure calls `style.role("sea")` and
cannot name a colour of its own; `tests/test_figures_palette.py` walks each
figure module's syntax tree and fails on any colour-shaped string literal, with
a positive control so that a scan finding nothing is distinguishable from a
scan that searched nothing.

### Why adjacency, and not a flat list

The obvious structure is a dictionary of names to colours and a test that every
pair separates by 0.15 in luminance. That test cannot pass and it is worth
being precise about why: 0.15 steps fit seven values into a zero-to-one scale,
and there are 16 roles. The first attempt at this section was going to record
which pairs "failed"; what it actually recorded was that the test was wrong.

Adjacency is the fix. A place marker and a neighbouring province's boundary
never have to be told apart by tone, because one is a dot and the other is a
line. A coastline and the sea it separates absolutely do. So each role names
what it meets, the graph's symmetry is asserted -- an adjacency one side claims
and the other does not is a bug in the declaration, and two such bugs were
caught this way -- and the checks run over 28 declared pairs.

The numbers: minimum luminance gap over the declared pairs
**0.157**, at `lattice` against `sea`. Minimum over
*all* pairs 0.000, at `absent_fill` against `relief_light`, which is reported
and deliberately not asserted: those two are near-white and are drawn in
different figures, so they never meet.

### The over-constrained corner, which changed a design

The relief band takes the top of the luminance scale, so every line on the map
has to fit below it. Measured, with the band's floor at 0.74, there is **no
assignment** that puts the sea, a coastline and a lattice line all 0.15 apart
from each other and all 0.15 below the band. Four classes need 0.45 of range
and the constraint leaves less.

That is a finding about the figure, not about the palette. The lattice and the
coastline only ever meet in the detail box, so the detail box does not stroke a
coastline: at the size it is drawn the tone step from sea to lit relief is 0.47,
which is three times what a stroke would add. The constraint was measured and
then a design decision was taken; it was not worked around by relaxing the
convention.

### Colour vision deficiency, which was never checked before

The repository had greyscale checks in two test files and **no colour-vision
check anywhere**. The brief that asked for these to be "moved" was describing a
consolidation of one thing and the creation of another.

`style.simulate_cvd` implements the Vienot-Brettel-Mollon dichromat simulation
directly rather than taking a dependency, because a figure standard that rests
on an unpinned package is not a standard, and because a simulation that quietly
returned its input would pass every test written against it -- so one test
asserts that the simulation changes colours at all. Minimum CIE76 distance over
the declared pairs: protanopia **14.4**, deuteranopia **14.4**,
tritanopia **14.4**, against a stated convention of 10. That
threshold is this project's, roughly ten just-noticeable differences, and is
labelled as such rather than borrowed as though it were published.

### What the role check does not cover

A sequential ramp is not a discrete role and a minimum pairwise gap says
nothing about one: its adjacent samples are arbitrarily close by construction.
The ramps keep the separate test they already had, for monotonicity in
luminance and for span, in `tests/test_figures_fields.py`. The relief is a
third case again -- a continuous grey under discrete overlays -- and is checked
as a **band**: every overlay must sit clear *below* the darkest tone it
reaches, which is a directional constraint a pairwise test cannot express.

### The categorical series stops at four, and that is measured

`style.SERIES` is Crameri's `batlowS`, the categorical variant of batlow, whose
defining property is that **any prefix** is a maximally distinct set. That is
what lets a three-series figure and a four-series figure share three colours
instead of being recoloured against each other; the previous scheme, four fixed
positions along the ramp, moved every colour when one was added.

Two modifications, both stated where they are made. Entries above luminance
0.78 are skipped, because a line at 0.85 on a white page is not ink.
And the prefix is sorted by luminance, because `batlowS` orders for hue
distinctness and a *series* is ordered.

The set holds four. `batlowS` has no five-colour subset below the ink ceiling
that separates by 0.15 in luminance, so `series(5)` raises rather than
returning something that fails the convention silently. A figure needing five
series has to distinguish them by something that is not colour.

### What changed in the two existing figures

**The composite is byte-identical.** Its four colours -- coastline, boundary,
absence fill, absence outline -- were already the values the roles now carry,
so the retrofit replaced literals with `style.role()` calls and the recipe test
reproduced the committed PNG and PDF exactly. That is the useful outcome: the
consolidation was a renaming there, not a redesign.

**The coverage figure moved three colours and one grey.** Its series went from
batlow sampled at 0.08, 0.38 and 0.62 -- luminances 0.189, 0.410, 0.574 -- to
the first three of `SERIES` at 0.096, 0.325 and 0.487. All three are darker,
which suits line and bar ink on white, and the minimum pairwise gap is 0.162
against the old 0.164, so nothing was given up. The absent-months span moved
from 0.88 to 0.84, because at 0.88 it sat 0.12 from the white page and
the convention is 0.15; that was a real failure the old per-figure check had no
reason to look for.


## The study area map was rebuilt, not adjusted

Three figures were looked at together for the first time and this one did not
survive it. The verdict was that it had no geography in it: land outside the
four provinces was near-white and so read as absence rather than as land,
nothing outside the study region was named, and a reader who does not already
know eastern China learned nothing from it about where this is. Four provinces
shared one fill and were distinguished only by their boundaries; Shanghai
needed a leader line to a sliver, which is the tell that an encoding is not
working; the inset sat over Zhejiang's coast and the Zhoushan archipelago,
covering data; and the lattice was drawn at full extent over sea and
out-of-region land, where 66 lines are hatching rather than reference.

### The relief is the argument, not the decoration

The map now has shaded relief because of a number, not because relief looks
good. Measured on the committed per-cell elevation: the composite's 97 absent
cells have a **median elevation of 502 m** against **35 m** for the 926
observed ones, 50 of the 97 sit above 500 m against 24 of the 926, and the
largest connected block of 47 has a median of 552 m and reaches 1,119 m. That
block is 35 cells falling mostly in Zhejiang and 11 in Fujian, along the
southern edge of the box.

So the terrain is why the next figure has holes, and a reader who has seen it
here does not have to be told. That is what makes a reference map earn its
place rather than orient and stop.

One premise from the brief did not survive the check and is worth stating
because it is a definition problem, not an arithmetic one. "75 of the 97 absent
cells are on land" is not a single number: 93 of the 97 touch land at all, 83
have their centre on land, 81 are more than half land and **74** are entirely
land. Four defensible readings, four different answers, none of them 75. The
caption says which it means.

### Two terrain sources, and the resolution claim that half held

The brief predicted that Natural Earth's 10 m raster would be visibly soft in
the main panel: 21,600 by 10,800 is 60 px/deg, the study box is 7.75 degrees
wide, so 465 pixels against a 2,007-pixel target at 17 cm and 300 dpi, a 4.3
times upscale.

The arithmetic is exactly right and the conclusion was checked by rendering
rather than accepted. Two corrections came out of it. The map panel is not the
figure: at 10.2 cm of drawn width it wants 1,205 pixels, so the upscale is
**2.8 times, not 4.3**. And at 2.8 times the Natural Earth raster does not look
obviously soft. It looks, if anything, more contrasty than a naive GLO-90
hillshade, because it is a cartographically tuned product with its own
exaggeration and generalisation baked in.

What is measurable is structure rather than softness: upscaled to the panel's
width, the Natural Earth raster carries a mean absolute gradient of 1.84 DN per
pixel against 5.48 for GLO-90 downsampled to the same width, so it holds about
a third of the local detail. And there is a better reason than sharpness for
preferring the DEM, which the softness argument obscures: an elevation model is
a measurement this repository can quote numbers from and check a claim against,
while a shaded-relief image is a rendering. The 502 m and 35 m above could not
have come from the Natural Earth raster at all.

Natural Earth is used for the inset, where 30 px/deg against about 8 needed is
ample and where hypsometric tints cost nothing because nothing is drawn over
them.

### What the DEM's readme actually warns about

Both cautions were checked rather than carried over.

**Ocean areas have no tiles.** True, and it matters for a delta: 20 of the 100
one-degree tiles over the padded box are absent and all 20 are offshore. They
are filled with zero, which the readme instructs, and the sea is then painted
over anyway.

**The non-square pixel warning does not reach this study area.** The readme's
table gives a longitude spacing that widens with **latitude** -- 1x from 0 to
50 degrees, 1.5x to 60, and reaching 10x above 85 -- not with longitude. At
26.9 to 35.3 N every one of the 80 tiles is 1200 by 1200 at 1/1200 degree in
both axes, measured across all of them with no variation. The 1:5
height-to-width ratio that motivates cubic resampling elsewhere occurs in the
80 to 85 degree band. Nothing about southern Zhejiang being rugged brings it
closer.

Cubic was used anyway, because it is the right resampler for a 3.9x decimation
whatever the pixel shape, and the seams were checked anyway rather than skipped
on the strength of the above. Over the rugged 27 to 29.5 N band the mean second
difference along tile-edge columns is **0.989** of its value elsewhere under
cubic and **1.041** under bilinear. A ratio near one is the answer. A ratio
well above one would have been the artefact.

The bucket is `copernicus-dem-90m`. The brief named `copernicus-dem-30m`, which
serves GLO-30 and a **byte-identical readme**, so the readme can be read from
the wrong bucket without any sign of it. In a tile name, `10` is GLO-30's arc
second spacing and `30` is GLO-90's, which is the reverse of the bucket names.

### Square in metres, not square in degrees

`gdaldem` takes one vertical-to-horizontal scale and applies it to both axes,
so a hillshade computed on a lat/lon grid under-weights east-west slope by
1/cos(latitude), which is 17 percent here. The DEM is therefore warped onto a
grid whose pixels are square in **ground metres** at 31.075 N, the same centre
latitude the display aspect uses, after which `-s 111120` is exact in both
axes. That is why the committed relief's longitude step is larger than its
latitude step.

### The relief's resolution was set by what a PDF can hold

200 rows per degree, which is 1.29 times what the panel resolves at 300 dpi.
The first build used 300 and the reason to come down is not the committed file,
though that falls from 2.13 MB to 0.92 MB. It is that a hillshade computed at
twice the resolution a page can show is half noise, and noise is exactly what a
deflate stream inside a PDF cannot compress.

The route to that finding is worth recording because two intermediate steps
were wrong. Downsampling the array before `imshow` barely moved the file, and
quantising its colours made it **larger**. Both because matplotlib resamples an
image to the output device's resolution when it writes a vector file: the
embedded image is about 1,205 pixels wide whatever is handed to it, so the only
levers are the device resolution, which the venue fixes, and how compressible
the content is at that size. Quantising a source that is then bilinearly
resampled produces more distinct values, not fewer.

What did work was reducing the source's own detail. 300 rows per degree gave a
1.76 MB vector against a 2 MB ceiling; 200 gives 1.66 MB; 150 gives 1.49 MB and
was rejected because it puts the relief below the panel's own resolution, which
is the softness this whole exercise was about avoiding.

Two smaller savings came from the same audit. The relief was being drawn as two
full-extent images with two clip paths, one veiled and one tinted, each hidden
wherever the other was visible; compositing them against a rasterised province
mask draws one. And the detail box was drawing the whole eight-degree raster
into a 0.75 degree panel and clipping it, which is five million pixels to show
forty thousand.

### The cities are a threshold and two filters, because a threshold alone fails

Natural Earth's populated places layer carries `SCALERANK`, and the brief's
expectation was that a threshold on it would be a rule rather than a hand-picked
list. It would be, and it cannot produce the set this map needs: **Natural Earth
does not rank the four provincial capitals together.** Shanghai is rank 0,
Nanjing and Hangzhou are rank 2, and **Hefei is rank 4**. A threshold reaching
Hefei also reaches fourteen other places among the 57 in the study box,
including Zaozhuang and Linyi in Shandong and Nanchang in Jiangxi, which is more
than an 11 cm panel can label.

The rule adopted is still a rule and still comes entirely from the layer's own
fields: scale rank 4 or better, feature class `Admin-1 capital`, admin-1 unit
one of the four study provinces. Four places, and they are there because of what
they are.

Suzhou, Wuxi and Ningbo are rank 4 and are left off. The crowding numbers:
Suzhou and Wuxi are 0.35 degrees apart, 4.6 mm on the drawn panel, and both sit
in the same cluster as Shanghai, whose label already needs the room. The panel
carries 12 pieces of text as it is.

**The populated places layer was not in the cartopy cache**, unlike the province
and land layers. The cache on this machine holds 14 layers, all physical or
administrative boundaries, and no populated places at any scale. The habit of
checking the cache first is still right; this time it returned nothing and the
layer was fetched, which is the better outcome anyway because the archive
carries a `VERSION.txt` and the cached shapefiles do not.

### Shanghai is labelled by its own city marker

At this scale the word "Shanghai" is about 1.2 degrees wide and the municipality
is 0.9, so it cannot sit inside its own polygon and the first version drew a
leader line to it. The answer is not a smaller font or a better leader: Shanghai
is also one of the four provincial capitals, so its city label names the
municipality too, and a name beside its own marker is a label in place. The map
therefore carries three province names and four city names rather than four and
four, and no line is drawn from any name to anything. A test asserts that every
line on the main panel is a marker.

### The study region is carried by contrast, and the sea paid for it

Four distinguishable fills over relief was not attempted again; the earlier
finding stands that six areal classes cannot separate. What replaced it is one
raster drawn twice: veiled toward `land_outside` beyond the four provinces and
tinted toward `province_fill` inside them.

The veil rather than the tint is what does the work, and the reason is
greyscale. A hue difference between inside and outside vanishes in a black and
white print; a **contrast and lightness** difference does not. Flat ground reads
at 0.849 inside and 0.692 outside, a gap of 0.156, which is the convention.

That gap was expensive and the price fell on the sea. Every line on the map has
to sit 0.15 below the darkest tone the veiled relief reaches, which is 0.573, so
the whole line palette lives below 0.42; and the sea has to clear the same
floor, which puts it at 0.42 rather than the 0.96-adjacent tone the old palette
had room for. The map is darker than it was and that is the cost of the region
being legible without colour.

### The lattice became a detail box, and the detail box lost its coastline

The lattice is gone from the main panel. The composite figure already shows the
analysis resolution by drawing the cells as the data, so 66 lines here were
redundant and cost the panel a layer of texture over ground that is now
carrying terrain.

What replaced it is six cells over the Yangtze mouth at 4.6 times the main
panel's scale, in the right-hand column where it covers nothing, **with the same
six outlined on the main panel at their drawn size**. The pair is the point: the
enlargement is legible and the rectangle is honest about how big a cell actually
is on this page, and neither alone answers "what does 0.25 degrees mean".

The window is 121.30 to 122.05 east, 31.45 to 31.95 north, chosen for a land
fraction of 0.58. A window that is nearly all land or nearly all water shows a
grid on a plain background.

The detail box draws **no coastline stroke**, and that is a measured decision.
A lattice line there crosses both sea and relief, so it carries the coastline's
two-sided constraint as well as its own, and with the relief band's floor where
it is there is no assignment that holds the sea, a coastline and a lattice line
all 0.15 apart and all clear of the band. The tone step from sea to lit relief
is 0.47 at the size the box is drawn, three times what a stroke would add, so
the stroke is what was dropped.

There is still no scale bar. What the detail box carries instead is a statement
about one cell at one stated latitude -- 24 by 28 km at 31.7 N, computed on the
authalic sphere this project measures areas on -- because a scale bar on an
equirectangular map is correct along one parallel only, and a claim about a
named latitude survives being read off the wrong part of the map.

### The inset asserts nothing, and that took finding out what it used to assert

The inset is out of the frame, in the right-hand column. A portrait map at full
width leaves 4.5 cm of page and the inset now occupies it rather than covering
Zhejiang's coast.

The boundary question was raised deliberately rather than inherited. The old
inset outlined the 31 admin-1 units filed under `admin = "China"` in Natural
Earth's 50 m layer, and both this file and `data/reference/README.md` recorded
that Taiwan, Hong Kong and Macau were therefore excluded because Natural Earth
carries them separately. The conclusion was right and **the mechanism was
wrong**: the 50 m admin-1 layer has no Taiwan, Hong Kong or Macau features at
all. Only the 10 m layer carries them, as 21, 1 and 1 units against China's 32.
Nothing was excluded, because there was nothing to exclude.

The inset now draws terrain, which has no opinion, and over it every admin-0
land boundary line Natural Earth files in the extent -- 59 of them, unfiltered,
with no country named or filled. Taiwan appears as its coastline does, like
Hainan and Kyushu. Hong Kong and Macau are not distinguished, because that layer
carries no feature for either. Natural Earth classes six of the 59 as `Disputed
(please verify)` and ships 33 per-country viewpoint fields, `FCLASS_CN` and
`FCLASS_TW` among them, which is the source saying in its own data that the
classification depends on who is asked. The figure carries a line saying whose
lines these are and the caption says this repository takes no position.

### The figure is full width now, which reverses an earlier decision

`notes/decisions.md` recorded that this map was 11.4 cm and that "the map is not
full width, and that is the point of having a default": its extent draws 1.24
times taller than wide, so at 17 cm it would have sat in a band of white.

That reasoning was correct for a figure that was only a map. It is now a map and
a column -- locator, detail box, keys, source notice -- and the column is
precisely the band of white the earlier decision was avoiding. The map itself is
10.2 cm wide, slightly narrower than the 11.4 it had; what changed is that the
page beside it is doing something.

The keys moved into that column too. They used to sit in the map's lower-left
corner, and off the map they cover no geography at all. That is the same
reasoning that moved the inset, applied to the other thing that was sitting on
the data.

### The attribution is on the figure, which the standard does not forbid

`What the map leaves out` still holds: no north arrow, no scale bar, no drop
shadows, no coordinate-system stamp of the kind every 2023 ArcGIS export in
`legacy/figures/` carries.

The Copernicus notice is not that stamp. A coordinate caption is a machine's
default, printed because nobody turned it off; this is a licence condition,
Article 6(b), and it is on the image because a figure travels away from its
caption and the obligation attaches to the image. Article 6(c)'s liability
sentence goes in the caption and in `data/reference/README.md`, since it is
about redistribution rather than display.

## Two figures for land cover, and one of them is about resolution

The set had a hole: every land-cover figure drew a fraction per 0.25 degree
cell, so a reader saw fractions and never saw the thing being fractioned, and
the 30 m and 10 m products the 2023 thesis rests on were invisible in a
repository about that thesis.

### A native-resolution figure cannot also be a cell-scale figure

The first thing measured was the arithmetic, and it rules out the obvious
layout. A 10 m pixel needs at least one drawn pixel to be a pixel rather than a
smudge, so at 300 dpi a panel of *n* centimetres can show 118*n* metres of
ground per drawn pixel: a 6.9 cm panel covers 5.7 km. A 0.25 degree cell is 24
by 28 km. **The two scales are 2,800 to 1 apart in area and cannot share a
panel.**

So the figure is a window at native resolution *and* a separate panel of six
cells, with the window marked inside the cell it belongs to. That is the
detail-box pattern the study area figure established, applied to a ratio four
times larger.

Measured drawn pixels per source pixel, printed on every build: 4.37 for the
30 m products and **1.46** for the 10 m rice. The second is the binding one and
it is why the panel is 6.875 cm and not smaller. `interpolation="nearest"` is
asserted by a test rather than left as a setting, because any other value
invents intermediate values between classes that have no intermediate, and
because it would still look like a figure.

### The window was searched for, not chosen

Four constraints, and the second eliminated half the study region.

Both classes had to be present and abundant. Double-season rice had to be
present, and only two of the four provinces carry the class at all: measured on
the 2018 rasters, Anhui 1.0 percent of pixels and Zhejiang 0.4, against zero in
Jiangsu and Shanghai. The window had to lie wholly inside one province, because
the NESDC rasters declare no nodata and 0 means both real non-rice land and
out-of-province background, so a window across a boundary draws two different
things in one colour. And it had to lie wholly inside one analysis cell, so
that the native pixels and the number they become are the same ground.

Seven cities across Anhui and Zhejiang were scored on the balance of the three
classes. Wuhu won: 23.9 percent impervious under GISA, 29.4 percent
single-season rice, 4.9 percent double.

The study area figure's detail window was considered and does not serve. It was
chosen for a land fraction of 0.58 because that figure needed a land-water
boundary; this one needs an urban-rice boundary, it sits in Jiangsu and
Shanghai where there is no double-season class, and at 0.75 degrees it is
thirteen times too wide to draw a 10 m pixel.

Its height was then set so that all four panels draw in one proportion, 0.782,
which is the shape of the three-by-two block of cells beside them. Four panels
on one grid rather than one of them standing 0.9 cm taller.

### Numbers rather than two more colour panels

Panel (d) writes both impervious fractions and the rice fraction into each of
six cells rather than drawing two more ramps. A ramp would show a reader that
the fraction varies across six cells, which the three panels above already
show. What a ramp cannot recover is the value, and the value is what the model
was fitted on.

### The window is not a sample and the figure says so

34.2 percent rice against 19.5 for the cell that contains it, and 23.9 percent
impervious against 26.3. Both are on the figure. A window chosen for the
balance of its classes is by construction unrepresentative, and a figure that
did not say so would invite exactly the inference it was chosen to prevent.

## The urban change figure, and the finding it turned up

### The maps show where and the numbers show how much

A 30 m product cannot be drawn over 7.75 degrees at native resolution, so
`data/processed/urban_extent_*.tif` carries the impervious fraction per 1/128
degree cell and the figure inks a cell where at least a quarter of it had
become impervious. The threshold is stated because it does not preserve area
and, measured, it does not fail evenly: urban land in 2000 is more dispersed
than in 2018, so the drawn 2000 class is **0.73** of its true area while the
drawn 2018 class is **1.31**. A reader measuring the maps would over-state
growth by about four fifths.

The answer is not a better threshold, because there is none: swept from 0.05 to
0.40 no single value brings all six product-years within 10 percent of truth.
The answer is a division of labour, stated on the figure and asserted by a
test: area comes from panel (c) and the maps carry the pattern.

A threshold-free alternative was tried and rejected. Shading each cell by its
fraction is area-honest and leaves the region nearly blank: the median land
cell in this box is 2 percent impervious and only 14.8 percent of land cells
reach a quarter.

### The stored grid and the drawn grid are not the same grid

The first draft drew the stored 1/128 degree cells directly into a 5.2 cm panel
and got stipple, because that asks the page for 0.62 pixels per cell and
isolated cells then survive or vanish according to where they fall. The figure
now averages two stored cells per axis to 1/64 degree, about 1.4 km, 1.24 drawn
pixels each.

The averaging happens on the **fractions**, before the threshold. Thresholding
first and then asking whether any sub-cell passed would be a looser statement
wearing the same words, and a test asserts the order.

### The finding is not the one the brief expected

The known disagreement is that GISA finds about 20 percent less impervious
surface here than GAIA in 2018, against a global validation that predicts the
opposite. Computing both products for 2000 and 2010 as well turned up something
sharper: **the products cross over.** GISA is 20.7 percent larger than GAIA in
2000 and 19.9 percent smaller in 2018.

So the three available accounts give three growth factors over the same
eighteen years and the same four provinces: the 2023 thesis 6.0, GAIA 3.0,
GISA 2.0. They agree far better about the 2018 extent than about the history,
which is exactly the signature this file already records for year-of-change
products: a reprocessing redates transitions across the whole archive, moving
the historical end and leaving the recent end alone.

That is why panel (c) is a line and not bars. Three lines that fan out at 2000
and converge at 2018 say "they disagree about the history, not the extent" in
one look, which is the opposite of what a reader expects.

### GISA now has a regenerable provincial series, and the old file is left alone

`urban_area_by_province_gisa.csv` carries 2018 alone and is registered
`unregenerable`, having been committed with no code that makes it.
`urban_extent_totals.csv` is a new table with both products across all three
years, computed by the same `zonal_histogram` route the GAIA table took, and it
does not replace the old one. It states its agreement with it instead: sixteen
overlapping rows, worst relative difference **1.3e-05**.

That agreement is the check that both products' opposite conventions were
applied the right way round, which is the failure mode this repository has
already been bitten by once. It is not a formality: the inverted GISA selector
would have drawn a plausible map of 9,468,801 pixels instead of 202,830,997.

### No rice time series exists, and that is the finding

Four constraints, each already recorded above, and together they leave nothing
to draw.

NESDC covers 2017 to 2025 and the comparison years are 2000 and 2010; it
reaches neither. Shanghai's totals are pinned across 2019 to 2025 and Jiangsu's
across 2020 to 2025 and again over 2017 to 2018, so half the study region
cannot contribute a year-on-year value. Anhui's rasters classify only the 86.8
percent of the province south of 33.3462 N and east of 115.2682 E. And GloRice,
which does reach 2000, allocates official statistics through a model rather
than observing extent and correlates with impervious fraction at Spearman
+0.5613, so a GloRice rice trend partly measures development.

What is left is two provinces over a window that misses both comparison years,
from a product whose other two provinces are pinned. That is not a time series,
and drawing one would have been the most defensible-looking mistake available
in this whole exercise: nine years, four provinces, a plausible shape, and
nothing in the picture to say that two of the four lines are measuring a
constraint rather than a landscape.

The absence is stated on the urban figure and in its caption rather than left
for a reader to wonder about.

### And no methane equivalent

A reader arriving at a land-cover change figure expects a methane change figure
beside it. TROPOMI's footprint is 7 by 7 km at nadir, the analysis grid is 0.25
degrees because coverage forced it there, and the 2018 composite already leaves
97 of 1,023 cells with no qualifying sounding and runs from 1 to 410 per cell.
There is one year of usable methane, not three. A fine-resolution methane field
from this data would be interpolation presented as observation, which is the
distinction the composite figure's treatment of absence already turns on.

## Seven roles, and a second basemap style with a reason

The palette went from sixteen roles to twenty-three. Six of the seven are
categorical land-cover classes -- `impervious`, `rice_single`, `rice_double`
and the three urban vintages -- and the seventh, `land_flat`, is a second
basemap style, which needs justifying because the set already has one.

**Relief is drawn where the land surface is the subject, and not otherwise.**
In the study area figure the terrain explains the composite's holes and is the
figure's argument. In an urban-extent map it would be a competing signal: urban
land follows the plains, so relief under it invites a reader to see a
terrain-urbanisation relationship the figure is not testing. A flat ground is
the neutral choice. It is also much cheaper, a relief image costing about
1.2 MB of a 2 MB vector ceiling, but that is a consequence and not the reason.

`land_flat` does double duty as the observed-negative class in a categorical
raster: ground that was looked at and is not the thing being mapped. One tone,
because it is one statement. It is distinct from `absent_fill`, which means the
opposite.

**The three urban vintages were solved, not chosen.** Each has to clear the
boundary line at 0.078, the sea at 0.42 and the flat land at 0.925, all by
0.15, which leaves the intervals [0.228, 0.27] and [0.57, 0.775] and exactly
room for three. Adding a coastline at 0.26 to the set makes it infeasible, so
the urban maps do not stroke one -- the same arithmetic that removed the
coastline from the study area figure's detail box, arrived at independently
from a different starting point. The land-to-sea tone step is 0.505 without it.

Minimum luminance gap over the role set is unchanged at 0.159 and the three
colour-vision minima are unchanged at 14.4, because the new roles were fitted
into the gaps the existing ones left rather than allowed to move them.

## The regional rice figure, and the palette move it forced

Rice is the study's subject and the set had no picture of it. It appeared only
inside a 5.7 by 3.7 km window in Wuhu, because the regional predictor maps were
sequenced after the statistical figures on the assumption that they would
inherit the geospatial conventions. They do inherit them. Sequencing them last
still meant the largest figure in the set was the one that did not exist.

### The threshold is cheaper here, and the reason is arithmetic rather than agronomy

The urban figure inks a 1/64 degree cell at a quarter and pays 0.73 to 1.31
across its three years, because no threshold serves all three. Rice is drawn at
**0.35**, which is the value where the drawn area equals the true area, and
pays **1.06** of 50,042 km2.

The difference is not that paddy is more contiguous than impervious surface,
which was the expectation going in. It is that this map draws **one** quantity
where the urban map draws three. A single quantity can always be
threshold-matched to its own area; three cannot be matched simultaneously
unless they happen to share a spatial distribution, and 2000 urban land and
2018 urban land do not.

Split by season, rice is **dearer** than urban, which is the opposite of the
expectation. At a common quarter the two rice classes come out at 1.70 and
0.43, a spread of 4.0 against urban's 1.8 across three years. Single-season
rice area-matches at 0.35 and double-season at 0.17, because double-season
paddy is 5.3 percent of the rice and is interleaved with single-season at
1.4 km rather than segregated into blocks of its own.

Inking each class at its own threshold was rejected. Two colours on one map
inked at different densities would let a reader compare their extents and be
wrong, and no legend fixes that. What the figure does instead is let one
threshold decide **whether** a cell is rice and let the colour report which
season that cell's rice mostly is. The cost is stated on the figure: the
double-season colour covers 1,191 km2 of a true 2,677, and the bar panel
carries the areas.

### Double-season rice reaches the coast, and the palette had to move

The rice roles were set when the only figure drawing them was a window with no
water in it. `rice_single` sat at 0.62 and `rice_double` at 0.40, and the sea
is at 0.42.

Measured before assuming: Zhejiang's class-2 pixels reach the coastline at a
minimum distance of **0.0 km**, with a first percentile of 0.3 km. Anhui's are
inland, at a minimum of 96.7 km. So the adjacency is real for one of the two
provinces that carry the class, and 0.40 was unusable the moment rice was drawn
regionally.

The sea cannot move. It is pinned at 0.42 by the relief band in the study area
figure, needing to clear the veiled band's floor of 0.573 by 0.15. So the rice
pair moved instead, to **0.76 and 0.60**, keeping the ordering that
double-cropping is the darker of the two.

That change reaches back into the native-resolution figure, which is the right
outcome: a role is one colour everywhere, and a constraint discovered in one
figure applies to every figure that draws the role. The native figure was
regenerated and its own tightest pair, `rice_single` against `land_flat`, sits
at 0.159 -- which is now the minimum over the whole role set, replacing
`coastline` against `sea` at the same value.

### Four areal classes is the ceiling, and it decided the layout

The obvious figure is rice and impervious side by side, because the thesis's
framing is urban expansion encroaching on paddy. It is not what was drawn, for
two reasons and the second is the binding one.

Regional impervious surface already has two maps in the urban figure, from the
same aggregate at the same resolution. And the competition for land is not
legible as two maps at 1.4 km, where a single cell holds both; it is legible as
numbers per province, which the bar panel carries, and at 10 m in the native
figure, which shows the abutment directly.

The binding reason is that the palette cannot hold it. With both rice classes
adjacent to the sea, the areal fills have to fit into the two intervals the
convention leaves -- [0.228, 0.27] and [0.57, 0.769] -- which hold exactly three
tones. Rice takes two and `unassessed` takes the third. A fourth areal role for
impervious would have landed in one of the same two bands, in a panel beside
the rice map, and the two would have been indistinguishable in a black and
white print. Impervious therefore appears as a number and not as a fill.

### `unassessed` is a class because absence here has two meanings

The NESDC rasters declare no nodata and their 0 means both real non-rice land
and ground the product never covered. At window scale inside one province that
ambiguity does not bite. At regional scale it is most of the frame.

So the figure draws four classes: rice by majority season, ground the product
classified and found no rice in, and ground the product did not classify. The
last has two causes and one meaning -- the other provinces, which the product
does not cover at all, and the part of Anhui north of 33.3462 N and west of
115.2682 E.

Drawing that region as ordinary non-rice land would have said northern Anhui
grows no rice. It grows some: GloRice puts about 320 km2 there, and the
boundary is a processing artefact, five annual products across three raster
extents all terminating classification within 22 m of the same latitude.

`unassessed` is **dark**, at 0.25, which is the opposite of the usual
convention for missing data. The light end of the scale is taken by
`land_flat`, and the interval arithmetic above leaves nothing between. It reads
correctly anyway: a blanked region should not look like an empty one.

### The masking check earns its place immediately

Each of the four rasters is masked by the province it is named for, through
`src.grid.cells.accumulate_fraction`, and never by the union of the four. The
union failure is recorded in this file already: it assesses shared ground once
per file and produced a cell at 2.94 times its own area.

`scripts/compute_rice_extent.py` refuses to write until it has compared the
assessed area against the province polygons. Shanghai 1.0001, Zhejiang 1.0012,
Jiangsu 1.0005, **Anhui 0.8611**. Three at their polygon area and one short is
the shape a correct mask produces; a ratio above one is the shape the union
mask produces, and the check refuses at 1.02.

Two independent reproductions fell out of it. Anhui's 0.8611 is the 86.1
percent classification footprint this file already recorded, arrived at from
the raster extents rather than from a grid. And the totals table's Anhui rice
of 22,594.6 km2 reproduces the 22,594.7 recorded here for 2018. Neither number
was used to build the other.

## The urban figure's maps end at 2019, and its legend had a category error

### 2019, because that is where the two products stop agreeing to exist

The maps drew 2000, 2010 and 2018 and now draw 2000, 2010 and 2019. The reason
is not that 2019 is better but that it is the last year both products cover:
GISA's values run to 37 and 37 decodes to 2019, verified on the rasters rather
than from the documentation -- 37 is both the code for 2019 and the largest
value the files contain. The fetched GAIA release runs to 2021. A map at 2020
or 2021 would therefore have to drop GISA, and dropping GISA loses the product
disagreement, which is the figure's sharpest finding.

The selectors are the documented ones and were checked, not assumed: GAIA
counts down from 2023, so 2019 is `at_least(4)`; GISA counts up with 1972 as 1
and annual from 1985, so 2019 is `between(1, 37)`.

**2019 carries a caveat and the caption says so.** It is the first year past
GAIA's original 1985 to 2018 release. It also sits inside the stretch
`data/processed/README.md` already flags: year-on-year growth of the
four-province total runs 7.1 to 10.5 percent across 2011 to 2016 and then drops
to 1.9 to 2.6 percent from 2017 onward. Worth being exact about what that
means: 2018, which the figure was already drawing, is the *second* year of that
stretch, so 2019 does not enter new territory so much as go one year further
into territory the figure was already in.

The committed aggregate now carries four years rather than three, because the
maps and the totals panel want different ones. That created a hazard worth
naming: a figure reading bands by position would have silently drawn 2018 as
2019 the moment the fourth band was added. `display_fractions` now selects by
year from the raster's own `years` tag and a test asserts it.

### A study is not a data source

Panel (c) listed "thesis 2023" beside "GAIA" and "GISA" as though the three
were three datasets. They are not. The thesis's impervious figures came from
GAIA, so the legend implied three independent measurements where there are two,
one of them measured twice.

The fix is an encoding rather than a relabelling. **Source takes the colour and
computation takes the dash**: GAIA navy and GISA teal, the 2026 recomputation
solid and the 2023 report dashed. Two navy lines then diverge at 2000 and
converge at 2018, which is the comparison the old layout was hiding -- the same
product recomputed holds 2018 to 0.8 percent and moves 2000 by a factor of two.

That is not a fact about this figure and it is now a convention rather than one
fixed legend. `style.source_computation_styles` implements it, in
`src/figures/style.py` where the conventions live, and its docstring carries
the rule: *a figure showing values from more than one source must distinguish
the source from the computation, and must never place a study in a list of
datasets.* Colour is the stronger channel and takes the stronger distinction;
the dash is a weaker channel and survives greyscale on its own. The helper
refuses more computations than it has patterns that separate, rather than
silently reusing one, and a test asserts the refusal.

The role rename followed: `urban_2018` became `urban_2019`, because a role's
name should say what it is and the class now runs to 2019. **The tone did not
move.** The three vintages were solved into the gaps the other roles leave --
each clearing `boundary` at 0.078, `sea` at 0.42 and `land_flat` at 0.925 by
0.15, which leaves [0.228, 0.27] and [0.57, 0.775] with room for exactly three
-- and none of those constraints depends on which year a class ends in. Checked
rather than assumed: the role set's minimum luminance gap and its three
colour-vision minima are unchanged.

## The model diagnostics, and the prediction that had to be held out

The figure set had no model diagnostic at all, which was a sequencing mistake:
the reproduction's central result is negative, a negative result is carried by
a *shape* rather than a number, and the set reported the shape as two R squared
values in a table.

### Held out, and the check that says so

`baseline_results_2018.csv` carries metrics and not predictions, so a figure
drawing observed against predicted had nothing to read. The predictions now
come from `held_out_predictions`, added to `src/model/baselines.py`, which runs
the same loop `evaluate` runs and returns the predictions instead of discarding
them.

In-sample fitted values were the mistake available here and it is not a small
one: the spatial null's in-sample R squared is **0.685** against a held-out
**0.332**. A figure drawing the first would have shown a smoothness bar twice
the bar it is, looked entirely plausible, and failed no test.

So `scripts/compute_baseline_predictions.py` refuses to write unless the
metrics recomputed from the pooled predictions reproduce the committed table.
Worst gap over sixteen comparisons, four models by four metrics: **4.97e-05**.
That is the only cheap way to tell a held-out prediction from a fitted one
after the fact, and a test asserts it as well.

### The table is not what the brief for this figure described

Eight model families over 176 rows was the expectation. Measured: **22 families
and 88 rows**, twelve of the families on the 531-cell rice sample and ten on
all 926. The distinction matters more than the count, because `baselines.py`
already records the rule -- results on different samples must not be compared
without saying so -- and four panels side by side is a comparison whatever a
caption says.

That rules out the fourth panel the brief proposed. "OLS full covariates + both
fractions" runs on 531 cells, so it cannot sit beside three models fitted on
926. The panel is `OLS wind (u, v, speed)` instead, which is on the full sample
and reaches 0.653.

The four are a progression across the whole range the table holds on that
sample: constant -0.008, impervious 0.085, spatial null 0.332, wind 0.653. The
finding is where land cover sits in it, which is nearer the constant than the
smoothness, and the ranges say the same thing: the observed field spans 106
ppb, the field impervious fraction produces spans 43, and a constant spans 1.4.

### One scheme drawn and four reported

Spatial blocks and unweighted, and a fifth panel exists so that is not hidden.
It draws all four models under both schemes and both weightings, colour for the
scheme and fill for the weighting, which is the same separation
`source_computation_styles` makes for lines.

Spatial blocks because it is the only scheme in which the spatial null is a bar
at all. Under leave-one-province-out a held-out province's interior has no
training neighbour, so the null falls to **-0.091**: below zero, so it explains
none of the held-out variance and there is no diagonal-tracking cloud to set
the flat ones against.

**A claim of mine failed its own test here and is worth recording.** The first
draft of this section, of the module docstring and of the script's comment all
said the null "falls below the constant" under that scheme. It does not: -0.091
beats the constant's -0.172. What is true is that it falls below zero. The test
that caught it was one I had written to assert the wrong thing, which is the
useful part -- an assertion made from a remembered number rather than a read
one fails as soon as it meets the file.

### Weight is drawn, because it cannot be argued away

A cell's observed value is the mean of between 1 and 410 soundings. Mark area
carries the count on the same half-decade classes the composite figure's legend
uses, so a reader who has met one has met the other.

Area rather than opacity, and the reason is specific: opacity in a cloud of 926
marks confounds precision with overplotting, so a dense region of poorly
observed cells would look like a well observed one. Area also survives a black
and white print without a second channel.

### Two new roles

`observation_mark` at 0.45 and `reference_line` at 0.10. The first is
mid-toned rather than dark because 926 marks at 0.10 read as a solid block
wherever they overlap, and the shape of the cloud is the whole finding.

`reference_line` is deliberately **not** declared against `label_text`, which
is 0.099 away. They do not meet: the annotations sit in a fixed corner and the
line runs through the data, and a line and a word are not confusable by shape
in any case. Declaring an adjacency that does not exist would have forced one
of the two to a tone neither wants, which is the failure mode the adjacency
graph exists to avoid.


## The field a land-cover model produces, and the ramp that had to carry a sign

`ERRATA.md` 1.1 records that the thesis's Figure 4.7, captioned "XCH4 Predicted
Boundaries", is the same embedded image as Figure 4.5(a). The comparison it
claimed to draw was never drawn. This is that figure: observed, the field a
land-cover fit produces, and the difference.

Nothing in it is a prediction of methane. Panel (b) is the field one covariate
produces and is drawn so the distance to panel (a) can be read cell by cell.
That is the demonstration of `ERRATA.md` 7.1 rather than a retreat from it.

### Which model, and the second kind of absence

Impervious fraction alone, not impervious with rice. The rice fraction exists
for **531 of the 926** cells, so a two-covariate field would be blank over 395
more, and this figure would then carry two kinds of absence — "no sounding" and
"no rice raster" — in the same near-white, in the same panels. The absence
treatment is the part of this figure that has to be unambiguous.

The rice numbers argue the same way, but not as cleanly as the first draft of
the module docstring said. On its own 531 cells, impervious alone reaches
**0.018** and impervious with an additive rice term reaches **0.017**, which is
backwards. **With an interaction term it reaches 0.033**, which is forwards,
and the docstring did not say so until a test made it. Forwards from 0.018 to
0.033 is still three percent of held-out variance on 57 percent of the cells,
which does not buy a second absence.

### One scale, and a departure from the composite

Panels (a) and (b) share one scale over the observed field's full range,
**1840 to 1947 ppb**, unclipped. The composite clips its value panel to the 2nd
and 98th percentiles and this figure deliberately does not.

The composite's reason is good and does not apply here. There the job is to
read one field well, and the outer four percent of cells have median sounding
counts of 2 and 12. Here the job is to compare two spans — the observed field
covers **106 ppb** and the model field **43** — and clipping would cut the
observed span shown to 59 while leaving the model field almost untouched. It
would shrink the contrast the figure exists for, in the direction that flatters
the model.

### An unobserved cell has no residual

Zero is the most meaningful value on a diverging scale: it is the centre, and
it means the model was right. Filling the 97 holes with zero would draw the
model's 97 best cells exactly where it has no cells. So the same 97 are absent
in all three panels, and the residual panel masks rather than zeroes.

That has a colour consequence. A sequential ramp keeps clear of absence by
truncation, because the tone that collides sits at an end — `RAMP_TRUNCATION`
buys 0.19 that way. **A diverging ramp's colliding tone is its centre**, which
no truncation reaches, and which is where most cells sit. Raw vik centres at
luminance 0.90 against absence at 0.97: a gap of 0.07 where the convention is
0.15.

The fix is to rescale the ramp's luminance rather than truncate it, the way
`relief_cmap` rescales grayC onto the relief band. Each sample's luminance is
mapped linearly from the ramp's darkest tone toward a centre of **0.80** and
the channels are scaled to hit it, which preserves hue and saturation exactly
and cannot clip, because the tone is being lowered. Measured after the fact:
centre 0.799, **gap to absence 0.170**, limb spans 0.721 and 0.722, no channel
clipped.

### A role for a tone of a ramp, which the palette had refused before

`style.py` carries a comment saying absence is adjacent to the ramp and to its
own outline and to nothing else, because a ramp is checked as a ramp. That
comment now has an exception, `residual_zero`, and the exception is the point:
naming the centre tone as a role is what puts this collision in front of the
adjacency machinery instead of leaving it in a comment. The role set is 27 with
66 declared adjacencies; the minimum luminance gap is unchanged at 0.159 and
the three colour-vision minima are unchanged at 14.4.

### What a diverging ramp needs that a sequential one does not

Three things, and the second is an admission rather than a pass.

**Per-limb monotonicity and span.** Worst non-monotone step 0.0033, which is
vik's own wobble at its dark blue end and survives the rescale unchanged;
ceiling set at 0.005. Limb spans 0.72 each.

**Symmetry, which costs the sign in greyscale.** Equal errors of opposite sign
must read as equally large, so the limbs are matched in luminance —
asymmetry 0.056 against a **ceiling** of 0.08, the only ceiling in the module
where every other number is a floor. Matched limbs cannot separate in
greyscale, so **a greyscale print of the residual panel shows how large each
error is and not which way it points**. The alternative buys the sign back by
drawing equal errors as unequal, which is a worse figure. The figure says this
in its own text and the test asserts it is false rather than pretending
otherwise.

**Sign under colour vision deficiency, which is now the only carrier.** For
every magnitude beyond a tenth of the scale, the colours for `+t` and `-t` are
compared under each simulated dichromacy. vik holds **15.0, 18.5 and 16.2**
CIE76 against a convention of 10.

That is most of what chose it, measured over Crameri's diverging set rather
than assumed. Five of the ten are dark-centred — berlin, lisbon, tofino,
vanimo, managua — and are outside what this rescale can do at all, since it
divides by the centre's height above the ramp's floor; `diverging()` now
refuses them by name rather than emitting noise, which is what it did while I
was measuring and briefly made all five look like catastrophic failures of the
sign test. Of the five light-centred ones, **broc (3.4), cork (1.1) and bam
(4.5) lose the sign under tritanopia**, because green against brown is the pair
tritanopia collapses.

That leaves vik and **roma**, and roma is better on two of the four measures:
it separates the signs further (21.4, 24.6, 14.7) and its limbs are more nearly
matched (0.030 against 0.056). It loses on the two that decided it. Its limbs
are the shortest of the five, 0.62 against vik's 0.72. And it centres on a
light green — **CIE chroma 24 against vik's 3.6** — so zero, which on this
scale means the model was right, would be drawn as a hue and read as a third
category rather than as the absence of one. `centre_chroma` is in the report
because it is the number that separated them.

### Moran's I, with its weights, because 6.2

`ERRATA.md` 6.2 records that the thesis reported a Moran's I without stating
its weights, which makes the number unreproducible. So the weights are on the
figure, in the caption and in the test: **queen contiguity among observed
cells on the 0.25 degree analysis lattice, row standardised, self excluded, no
distance decay.** The eight offsets are the same stencil the spatial null uses.

One cell has no observed queen neighbour. It is dropped and counted rather than
given a weight of zero, which would quietly read as a cell whose neighbours all
agreed with it.

The reference distribution is 999 permutations of the values over the same
cells on a fixed seed, not the analytic normal approximation, because residuals
from a fit do not satisfy what that approximation needs. The seed is fixed so
the number in the caption is the number the recipe reproduces byte for byte.

**The result: 0.646 for the residual against 0.709 for the observed field.**
The fit removes **8.8 percent** of the observed field's spatial
autocorrelation. Whatever organises this field at the scale of a few cells, one
land-cover covariate is not it.

### The set, and the figure that was cancelled

The planned baseline comparison — held-out R squared as bars with the spatial
null as a reference line — is **cancelled, not deferred**. It reports the
finding without showing it, and panel (e) of `observed_predicted` already
carries every model under both schemes and both weightings, which is more than
the bars would have held.

Which exposed a gap. The README has said "of a planned nine" since the set was
three, and **the membership of that nine was written down nowhere** — three of
the missing figures were named only in passing, inside the module docstring of
`src/figures/fields.py`. A planned set that is only a number cannot be checked.
`figures/README.md` now inventories the set: eight built, three planned — the
predictor maps, the fold map and the sampling-artefact map, which are the three
`fields.py` names — and every one of the 2023 thesis's eighteen figures mapped
to its equivalent or to the reason it has none. **The nine could not be
reconciled with anything.** Seven built plus these two is nine, but `fields.py`
names three unbuilt figures and the baseline comparison was a fourth, so the
planned set was never nine on any reading. The README now says eight of eleven.

### One artist drawn and never seen, twice

The visibility probe reports two artists contributing zero pixels, where the
convention is none. Both are matplotlib's own empty `LineCollection` of colour
bar dividers, one per bar, and `methane_composite_2018` has reported one of the
same thing since it was built. The probe now prints each artist's class name
alongside its label, because "collection _child0" contributing nothing is only
actionable if a reader can tell whose it is.

## A shape vocabulary, and the two standards behind it

The figure set had eight figures and no diagram. It also had, until now, **no
literature grounding for diagrams at all**: every other convention in
`src/figures/style.py` is traceable to Copernicus author guidance or to
Crameri, and the diagrams had nothing.

### What the two searches actually returned

**ISO 5807:1985** verifies exactly as named — *Information processing —
Documentation symbols and conventions for data, program and system flowcharts,
program network charts and system resources charts*, published February 1985,
confirmed current at ISO's 2019 review. It is **paywalled and was not read**,
so nothing here cites a clause. What is claimed is the symbol names, which
every secondary account gives alike, and `src/figures/diagram.py` says so in
its own docstring.

**The six design principles did not come from where I was told.** They were
offered as "a citable set of principles accompanying the standard, attributed
to Chaudhuri 2020 and Lodemann et al. 2022". Three corrections:

* They are not a companion to the standard. They are Appendix 5 of a clinical
  trial protocol (CSM-BSI, clinicaltrials.gov NCT06271031, October 2023), whose
  own wording is that its principles and shapes are "in accordance with the ISO
  standard 5807:1985" *where possible*.
* **Lodemann et al. 2022 is not a source of them.** It is a real paper and
  resolves, but the protocol cites it for something else entirely: "flowchart
  construction will be adapted from a process modelling study of the ABCDE
  primary survey in trauma resuscitation". That is a method for eliciting a
  process from clinicians, which this repository does not perform. Recorded in
  the register and not cited.
* There are **seven** principles, not six. The seventh — consider re-entrant
  processes when events are stochastic — is not used here and is not claimed.

So the citation is ISO 5807 for the symbols and Chaudhuri (2020) for the
principles, with the protocol recorded as the proximate source of the wording
and both books recorded as **not read**. The register's preamble already
records two citations that went wrong by collapsing exactly this kind of chain.

**The search's negative result is worth as much as its positive one.** There is
no flowchart or workflow convention in remote sensing or atmospheric science;
the workflow figures the search returned are ad hoc, one per paper. Following a
documentation standard from outside the field is therefore a choice, and it is
recorded as one rather than passed off as the field's practice.

**Patil, Peng and Leek (2019)** verifies: *Nature Human Behaviour* 3, 650–652,
`10.1038/s41562-019-0629-z`. Paywalled, so the grammar was taken from the
authors' own reference implementation, the `scifigure` package on CRAN. Eleven
stages as rows, studies as columns, four states — `observed`, `different`,
`unobserved`, `incorrect` — and a difference mode using symbols "semantically
close to the scenarios that they are encoding". Its default palette is a red
and a teal, which this repository does not follow, for the reason `style.py`
exists.

**Desai, Abdelhamid and Padalkar (2025)** verifies, and its definitions are
verbatim what the brief said they were: "Dependent reproducibility involves
using the original materials and validating the correctness of the
implementation as described in the study. Independent reproducibility is
achieved by reconstructing the experiment based on the original study's
methodology and similarly validating the implementation's correctness."

### The vocabulary lives beside the palette, not inside it

`src/figures/diagram.py`, a sibling of `style.py` rather than a section of it.
`style.py` encodes what a mark may look like *anywhere* in the set — venue
standards, the colour roles, the ramps — and every one of the ten figures reads
it. A shape vocabulary is narrower: it is what a **diagram** may contain, and
only two figures may contain one. It also carries a standard from outside the
venue's guidance, which is a different kind of authority from the one
`style.py` holds.

The mechanism is deliberately identical. A shape is declared with its grammar,
the standard's own name for it, why it exists, and what it is drawn **against**
— the same `against` field the colour roles carry, checked the same way. There,
by luminance gap; here by **outline**, as a radius profile resampled by angle
and normalised by its own mean, so it measures form rather than size.

Twelve shapes, eleven declared pairs, minimum difference **0.051** at
`terminator` against `process`. That number is also the caveat: at the aspect a
flowchart box is drawn, a stadium's rounding is confined to its ends and is a
small share of its perimeter, so the measure understates a difference that is
obvious on the page. The floor is 0.04, which is what it is for — catching a
shape added as a near-duplicate — and not for adjudicating close calls.

**One pair cannot be separated by outline and is named rather than scored.**
ISO distinguishes `process` from `predefined process` by two bars *inside* a
shared rectangle. `outline_report` excludes the pair and lists it under
`separated_by_decoration`, because scoring it zero and failing would be
punishing the module for following the standard.

Two failures found while building the measure, both recorded because both
produced a passing check that meant nothing. Comparing at 1:1 makes a stadium
*into* a circle, so `terminator` and `connector` scored identical; the
comparison is now at the aspect the figure draws. And resampling a rectangle
from its four corners interpolates radius linearly where the true edge follows
a secant, which collapsed the rectangle's profile to a constant and made it
identical to a circle; outlines are densified before the profile is taken.

### The graph is data, which is what makes the checks possible

Nodes and edges are dataclasses in a list and the drawing code reads them. Four
things follow that a hand-placed diagram cannot have.

One entry point and one exit point per shape, the decision excepted. The rule
is about the *point*, not the line: a branch may fan out past the box, so what
is checked is that every line into a node arrives on one side and every line out
of a non-decision leaves from one side. Two labelled outcomes per decision, each
leaving its own side. A reading order, top-down and left-right, with any line
running against it required to say so. And **every box names the repository
paths it stands for, so a test can open them** — which is the check a diagram
needs and nothing else in this suite provides.

Each of those has a positive control in `tests/test_figures_diagram.py`, because
a rule that cannot fail is not a rule.

### A test that could only fail after the mistake was committed

`tests/test_recipes.py` asserts every tracked file under `figures/` names a
recipe. `figures/README.md`, added in the previous commit, is prose and needed
adding to the exclusion list — and the suite run *before* that commit passed,
because `git ls-files` cannot see an untracked file. The check is sound and its
timing is not; the exclusion list now says so.

## The pipeline figure, and the one check a diagram needs

### Two panels, decided by rendering

Panel (a) reads top-down over six columns because acquisition forks: five
sources, one manifest gate, two aggregation branches, one join. Panel (b) reads
left-right in one row because modelling is a single chain and drawing a chain
down the page would double the figure's height to say the same thing. ISO reads
both ways, so the standard is satisfied either way and the choice is legibility.

Measured rather than argued. As one top-down frame the chart is eleven rows and
**23.4 cm** tall at 17 cm wide, which is the whole usable height of a
Copernicus page; as two panels it is **19.0**.

### ISO conformance, and where it needed interpreting

Seven of the twelve declared shapes, all from ISO 5807: terminal, process,
predefined process, decision, data, stored data, connector. Twenty-five boxes,
twenty-five flowlines, **zero structural violations**.

Two of the principles needed a reading before they could be checked, and both
readings are recorded because a check nobody can question is a check nobody has
thought about.

**"One entry point and one exit point, the decision symbol excepted."** Read as
a claim about the *point*, not the line. A flowline may leave a box once and
fork at a junction beyond it, and lines routinely merge before entering one —
five sources enter the manifest gate here. So what is checked is that every
line into a node arrives on the same side and every line out of a non-decision
leaves from the same side. Read as "at most one outgoing line" the pipeline
would need merge nodes that no code performs, which is a worse diagram.

**"All decision branches must be well-labelled."** A *branch*, not an edge: the
manifest's "yes" fans out to two aggregation modules, which is one branch going
two places. So a decision must have exactly two labelled outcomes, each leaving
its own side, and each outcome must leave from one side only.

The remaining two principles are about content rather than structure and are
asserted in the figure's own test file. Every process and decision must be
reached by at least one flowline, or the diagram asserts a step that runs on
nothing; all nine are. And no departure from the standard was needed elsewhere.

### The check that only a declared graph can have

**Every box names the repository paths it stands for — thirty of them — and the
test opens each one.** A box naming a module that was renamed, or a step the
code stopped performing, is the diagram equivalent of a stale prose figure, and
nothing else in this suite would catch it.

The test goes further where it can, because a path that exists is weak evidence
that a diamond's text is true. It asserts that `fill_archive_digest` really
returns `MISMATCH` and leaves the existing digest in place; that both area
scripts really default to a 0.001 tolerance; that `COVERAGE_CEILING` is really
1.02 and `COVERAGE_FLOOR` really 0.80; and that `export` really raises below
300 dpi and below 8 cm. The drawing script refuses to write if any path is
missing.

### What the brief said about the tiering, and what the register says

The brief gave the tiering as seven recipes on a fresh clone, eight needing
local data and six needing a network run. The register says **22, 16 and 6 of
45**. The network count is right and the other two are roughly a third of the
truth; the numbers were true of a much earlier commit. The figure reads them
from `config/recipes.yml` at build time rather than carrying them as text, so
the recipe that rebuilds it reproduces any change — including the change
registering a new figure makes to the count of figures the figure itself
quotes.

### What it does not draw

No box mentions a network, an architecture, a backbone or an epoch, and a test
asserts that. The 2023 thesis's Figure 3.1 is a DeepLabv3+ diagram, and
`ERRATA.md` 4.1 and 3.3 record that it depicts an architecture that was neither
described accurately nor implemented as described. A faithful redrawing would
have to choose which of the two to be faithful to, so this figure draws the
system that was actually built instead and says on its own face that it is not
that diagram.

## The reproduction status figure, and the state the source did not have

`ERRATA.md` records twenty-eight findings across seven sections, and read
straight through it is a list. A list of defects is the wrong shape for what
the reproduction established: most of the study is intact, four parts are not,
and the reasons differ in kind.

### Four adaptations to a cited grammar

The grammar is Patil, Peng and Leek's — stages as rows, studies as columns, one
state per cell — taken from the authors' own `scifigure` package because the
paper is paywalled. A departure from a cited grammar is a decision, so all four
are on the figure's own face as well as here.

**A fifth state, and it is not redundant.** `ERRATA.md` 3.5 is not `incorrect`,
which asserts a value is wrong: the errata deliberately declines to say the
stored losses are wrong, only that they "should not be cited as results of the
code as committed". It is not `unobserved`, which asserts nothing was recorded:
22 cells retain stored outputs. What cannot be established is the **link**, and
neither of the two states it sits between says that. A test asserts the errata's
own wording rather than trusting the reading — including that the word *wrong*
does not appear in 3.5.

It is used in exactly one cell, which is the right number. The state exists
because the finding does, not to fill a legend.

**A findings column that is not a study.** The source's columns are studies and
this figure has two, because there is one study and one reproduction. The text
on the right is row annotation, the mirror of the stage names on the left. It
carries what a two-column grid cannot: which section establishes each state and
which kind of reproduction produced it.

**The unchanged case is not de-emphasised.** The source's difference mode fades
cells where both studies agree, because across nine columns that is noise. Here
it is signal. Four of the eleven stages are unchanged in both columns and five
of the eleven cells in the 2023 column are unchanged or absent; drawing them
faintly would produce the page of failures the errata's preamble is careful not
to write.

**All eleven stages are kept, and one is `unobserved` rather than dropped.**
Neither study collected data — both read published satellite products — so
`Experimenter` belongs to third parties in both columns. The grammar has a state
for a stage that is not present, and using it says something; dropping the row
would silently change a cited grammar's row set and say nothing.

### No colour, because five tones do not exist here

The source's palette is a red and a teal, which `style.py` exists partly to
refuse. It is not replaced either: five states would need five tones separating
by 0.15 in luminance, and `style.SERIES` already records the measurement that
Crameri's categorical set has no such five-colour subset below the line-ink
ceiling. **No new role was added.**

So the glyph carries the state and the figure is **achromatic**: red, green and
blue are equal at every one of its 4,034,070 pixels. Greyscale and all three
dichromat simulations return the same image to within one level of 255, which
is the sRGB round trip's rounding. Both are asserted — the channel equality
exactly, the renders to that tolerance. An earlier draft of the caption said
"pixel-identical", which the measurement does not support.

### Desai's hierarchy maps onto the errata's own sections

Dependent reproducibility uses the original materials; independent rebuilds from
the methodology. Sections 1 to 6 of `ERRATA.md` read the thesis PDF, the
committed notebook and the repository's history. Section 7 rebuilds the
composite from Level 2 granules, joins the lattice and runs the baselines. The
errata says as much in section 7's own preamble — the six sections above record
what reading found, and this one is "different in kind".

Neither document was written with the other in mind, so the mapping is asserted
rather than described: a test derives each row's kind from the chapter numbers
it cites and compares it with the declared kind.

One case sits on the boundary and is marked as both. 7.5 recomputes the
provincial urban areas from the same product, which is dependent in method, but
from a later release, which is not the original material. That is the finding
rather than a technicality.

### The architecture test, in a different form

The pipeline figure carries a test asserting no box names a network, a backbone
or an epoch. Applying it literally here would fail, and correctly so: this
figure's subject includes `ERRATA.md` 3.3, so the word *backbone* appears in a
finding about the original. Naming a defect is not depicting an architecture.

So the assertion is on **structure** instead. The row set must be the grammar's
eleven stages, so no row can be an architecture component, and wherever such a
word appears in a finding, that finding must cite an errata section.

Also verified rather than assumed while doing this: the DeepLabv3+ diagram is
**Figure 3.1** in the thesis PDF, captioned on page 15. Three captions and a
figure note already said so on the strength of a brief; `ERRATA.md` never gives
that number.

## A drift class the prose-claims mechanism does not cover

`tests/test_prose_claims.py` verifies every **number** quoted in prose against
the artefact it comes from. It is a strong check and it is the wrong one for
this: a sentence naming a file is not a number.

A stopped task left four committed references to `framework_reproduction` — in
`src/figures/diagram.py`'s docstring, in `scripts/verify_figure.py`'s
`VECTOR_ONLY`, in the Patil entry in `notes/references.md`, and in
`figures/README.md`'s Figure 3.1 entry — while no such figure existed. None was
a broken reference in any mechanical sense. The inventory promised a figure and
the suite passed.

`tests/test_figure_inventory.py` closes it, in both directions and beyond the
inventory itself. Every stem the *What exists* table names must have a PNG and a
PDF; every PNG must have a row; every stem in `verify_figure`'s `BUILDERS`,
`VECTOR_ONLY` and `NATIVE` must be a built figure; every `figures/<token>` path
in any committed markdown must resolve; and every bare backticked token in
`figures/README.md` must be a known figure. Confirmed against `dd99b30`: three
of those five would have failed there, each on `framework_reproduction`.

**A planned figure is distinguished structurally, not by phrasing.** A built one
is a backticked stem under *What exists*; a planned one is plain prose with no
backticks under *What is planned and does not exist*. So the guard never has to
guess which a row is, and the two section headings are matched verbatim, so
renaming one fails rather than silently disabling half the check.

The counts are checked too, because a count that is only prose drifts. The
inventory has already said "a planned eleven" above a table of twelve, in the
previous commit, and nothing caught it.

**One member of this class is still unguarded and is recorded rather than
papered over.** A prose mention of a figure inside a module docstring — the
first of the four — is not reachable by any rule that does not also flag every
other backticked word in that docstring. What guards it in practice is the
closure between the inventory, the recipes and `verify_figure`; what would not
be caught is a docstring naming a figure nobody has started.

## The albedo collinearity figure, and a reference line over a ramp

The reproduction's negative finding is that land cover does not explain the
observed methane field, and the obvious objection is that the association is
real and the analysis is too blunt to find it. This figure answers that
objection. **The answer is not that the association is false.** It is that this
data cannot separate the two explanations even in principle, and `ERRATA.md`
7.4 already says so carefully; the figure has to match its care rather than
exceed it.

### Five panels, because three of the legs are different shapes

Two of the three legs are bivariate relationships and the third is a change in
one number. Forcing them into one frame would have served neither.

Rejected: **a single scatter of impervious against albedo with methane as the
colour**. It carries the first leg and hints at the second, and it cannot carry
the third at all. It survives as panel (a), which is the right size for it.

Rejected: **three panels**, one per leg. The third leg is "the association
falls from +0.345 to +0.021", and a reader cannot see a fall without seeing
where it fell from. So (c) draws the association at issue and (d) draws the
same association with albedo removed from both variables. Those two panels are
the comparison, and the number is only their caption.

Panel (d) is an added-variable plot, drawn from
`src.model.association.residuals` -- the same function `partial_correlation`
uses, made public for this. A figure that computed its own residuals could show
a cloud whose slope was not the number printed beside it. A test asserts the
correlation through the drawn cloud equals the reported partial to 1e-9.

Panel (e) is a slope chart of before and after control, on both methane fields
and both weightings. A pair of bars would ask a reader to compare two lengths
where a line already is the comparison.

### The asymmetry is the reason panel (e) exists

On the raw retrieval the impervious association survives control at
**+0.151** (p 4.0e-06); on the bias-corrected field it does not, at **+0.021**
(p 0.53). Drawing only the corrected field would imply the partial correlation
is the corrected estimate, which it is not: the raw retrieval carries the
*larger* uncorrected albedo bias, so incomplete control reads as well as a real
urban signal. All four combinations are drawn and the note gives that reading,
so neither field stands for the answer.

Weighting is the more conservative throughout and is reported for that reason:
the collinearity falls from Spearman +0.761 to +0.607, the zero-order
association from +0.345 to +0.212, the partial from +0.021 to +0.032 on the
corrected field and +0.151 to +0.125 on the raw. The correction removes 2.1
percent of the albedo slope unweighted and 31.3 percent weighted.

### A reference line over a ramp: a case the palette has no answer for

Panel (a) draws methane through the truncated sequential ramp and also draws a
line at albedo zero, because 166 of 926 cells sit below it and a reader meeting
a negative albedo will think it is an error.

**No single tone can clear a full sequential ramp by the 0.15 convention.** The
ramp runs from luminance 0.097 to 0.771, so a clearing tone would have to sit
below -0.05 or above 0.921, and 0.921 is indistinguishable from the page.
`reference_line` at 0.099 clears the light end by 0.672 and the dark end by
0.002.

The treatment is the relief band's rather than a pairwise one. The line is
drawn **beneath** the marks, so where it meets the darkest cells they occlude
it instead of blending with it, and it stays legible across the rest of the
panel, which is where a reader looks for it; the y ticks carry the same
information independently. Panels (b) and (d) have no such problem, because
their marks are `observation_mark` at 0.451 and clear `reference_line` by 0.35.
A test asserts the ordering rather than leaving it to a redraw.

The other new case is the ramp carrying a **third** variable. It separates from
the page by 0.229 at its light end, which is the requirement that matters when
a scatter is drawn on paper rather than over a map. What it cannot do is carry
a *value*: the smallest sounding class is a mark 0.050 cm across, under six
pixels at the export resolution, and nobody reads a concentration off six
pixels against a bar. So the colour in (a) carries order, and panel (b) exists
partly because magnitude needs an axis.

### Where the brief's numbers came from, and why three were slightly off

Several figures in the brief traced to the albedo section of this file rather
than to the committed tables, and this file is a **log**: its numbers are
as-measured-at-the-time and `scripts/verify_claims.py` excludes it by design,
because a mechanism that corrected them would destroy what they record. They
predate an extent change from 927 cells to 926.

So methane against albedo is **+0.700** and not +0.702 on the corrected field,
and **+0.738** and not +0.740 on the raw; the partial's p is **0.53** and not
0.55. The brief's slope figures came from the committed table instead and are
exact. Nothing here needs correcting: the log is right about what was measured
then, and the figure is right about what is measured now, which is the split
that mechanism was built to keep.

## The blended TROPOMI+GOSAT field, and what it did not fix

The reproduction's negative land-cover finding rested on a methane field with a
documented albedo bias that the operational correction removes about two
percent of unweighted, and impervious fraction correlates with albedo at
Spearman +0.761. So the obvious threat was that a properly bias-corrected field
would show the urban association the reproduction failed to find. Balasus et
al. (2023, doi:10.5194/amt-16-3787-2023) publish exactly such a field: a
machine-learned correction for SWIR albedo, aerosol and cirrus scattering, and
across-track striping, referenced to GOSAT.

It is now built on the same lattice. **The threat did not materialise, and the
reason it did not is more interesting than the answer.**

### The composite is like for like in the strongest available sense

Not merely the same cell count: **the per-cell sounding counts are identical in
all 1,023 cells**, 926 covered against 926 and 110,920 soundings against
110,920. Three things had to hold and each was checked rather than assumed.

The blended files carry the operational rows unaltered — for orbit 03019 the
maximum absolute difference against the retained operational granule was
exactly zero on latitude, longitude, both operational methane variables and
SWIR albedo across all 64,891 soundings. `qa_value` in this product takes only
{0, 16, 40, 100} across all 578 candidate granules of 2018, so the product's
`== 1.0` restriction and this project's `>= 0.75` select the same soundings.
And every one of the 223 orbits that carried an in-box sounding has a blended
counterpart, as do all 578 candidates.

### The albedo dependence rose

This is the finding, and it was not one of the two outcomes anyone expected.

| field | SWIR slope, unweighted | weighted |
|---|---|---|
| raw retrieval | 203.85 | 183.73 |
| bias corrected | 199.66 | 126.24 |
| deseasonalised | 172.47 | 106.45 |
| **blended** | **232.78** | **156.22** |

Up 17 percent unweighted and 24 percent weighted, with Pearson rising from
+0.700 to +0.762. NIR the same, 130.22 to 150.94. Every retrieval-geometry
predictor improves on the blended field: albedo's held-out R squared goes
+0.316 to +0.412 under spatial blocks weighted, sampling composition +0.418 to
+0.467, wind +0.563 to +0.592, the trend surface +0.258 to +0.366, and the
spatial null itself +0.514 to +0.562. The field's between-cell spread widens,
15.91 ppb against 14.86.

**That is a statement about this composite and not about the product**, and the
distinction has to be held. The paper's own claim is a reduction in spatially
variable bias *against GOSAT* from 14.3 to 10.4 ppb at 0.25 by 0.3125 degrees.
That is a different quantity measured against a reference this repository does
not have. The slope measured here is fitted across an annual mean in which
albedo is confounded with geography, land cover and sampling season, so it
absorbs everything that varies spatially with albedo; the same caveat already
recorded for the operational figure applies unchanged. It is an upper bound on
residual albedo sensitivity, not a measurement of it.

What can be said without qualification is narrower and still enough: **applying
the blended correction to this composite does not reduce its albedo-correlated
structure, it increases it.** A per-sounding correction referenced to a sparse
instrument is not obliged to reduce the between-cell variance of an annual
composite, and here it does the opposite.

The paper flags corrections exceeding 10 ppb over persistently cloudy regions,
and the YRD is one. The mean correction here is -12.31 ppb per cell. But the
qa census found the box retrieves *better* than the global average, 6.55
percent at qa 1.0 in-box against 4.65 percent globally, so "persistently
cloudy" is not straightforwardly the explanation and is not offered as one.

### The land-cover finding strengthened

Held-out R squared under spatial blocks, by sounding count: impervious fraction
goes from **+0.024 to -0.005**, below a constant. **Zero land-cover models beat
the spatial null under inverse-variance weighting on either field.** The
unweighted exceptions on the blended field are two rice models under
leave-one-province-out where both they and the null are negative.

The zero-order association falls, Pearson +0.345 to +0.315 unweighted and
+0.212 to +0.136 weighted. And controlling for SWIR albedo now takes it
**negative and significant**: +0.021 at p 0.53 becomes **-0.082 at p 0.013**
unweighted and -0.103 at p 0.002 weighted.

That last number should not be read as a negative urban effect. It is what
over-control produces on a field whose albedo dependence has increased:
partialling out albedo now removes more than the urban signal ever was. The
collinearity that made attribution impossible is unchanged — albedo against
impervious fraction is still Spearman +0.761 — so the figure's caption stands
as written, and the blended field does not rescue attribution. It removes the
last available reading under which a real urban signal was being hidden by an
uncorrected bias.

### What this means for the 54 GB rebuild: it is not needed

The covariate-preserving rebuild was to recover `eastward_wind`,
`northward_wind` and `solar_zenith_angle`, which the blended granules do not
carry. **It turns out the analysis never needed them from those files.**
`methane_covariates_2018.csv` already holds all three, averaged over the
identical soundings, so the full baseline suite — including the
sampling-composition control that `ERRATA.md` 7.4 rests on — runs against the
blended target unchanged. The rebuild would recover nothing the committed
covariate table does not already provide, and it is now confirmatory at most.

### One method note worth keeping

Reading four variables out of 223 remote granules cost 335.6 MB in 1,385 range
requests and seven minutes, against 23.08 GiB for the year. The AWS bucket
answers `Accept-Ranges: bytes` and h5py accepts a file-like object, so HDF5
fetches only the chunks it needs. Validated before use on the largest and
smallest in-box contributors, where a range read and a whole-file read returned
bit-identical arrays.

That is the same method the qa census used and it has now paid for itself
twice. The general point: for any question that needs one variable out of many
granules, the transfer cost is a property of how the file is read rather than
of how large it is.

## The GISA accuracy figure was attributed to the wrong paper for seven days

Three sections above quote GAIA as having a producer's accuracy 28.35 percent
worse than GISA, and the last of them records that figure as *sourced*, to the
2021 GISA paper at `doi:10.1007/s11430-020-9797-9`. **It is not in that paper.**
The string "28.35" does not occur in it. The figure comes from the 2022 paper
describing GISA 2.0, `doi:10.1016/j.jag.2022.102787`, which validates against
118,822 ZY-3 test samples and reports F1 scores of 0.935 for GISA 2.0 against
0.721 for GAIA.

The sample count that travelled with the figure is worse. "124,190 global
validation samples" **matches no published number in either paper.** GISA 1.0
reports 120,777 sites from 270 cities and a second set of 88,822 ZY-3 samples
from 45 cities; GISA 2.0 reports 118,822. Nothing in the literature gives
124,190, and repeated searches did not find it. It has been removed from
`README.md` and `data/processed/README.md` rather than re-sourced, because a
figure that cannot be traced to a source should not be carried on the assumption
that one exists.

**The three mentions above are left as they were written**, which is this file's
standing convention: its figures are as-measured-at-the-time and rewriting them
destroys the record of what was believed when a decision was taken. The
correction lives here, at the point in the sequence where it was found, and the
two live claims in the READMEs are the ones that were changed.

### Why this is the same failure the twelve uncited claims were

The section above on the twelve uncited claims lists this figure under "three
have a source in the register but no citation at the point of claim", and closes
it by naming the GISA paper. That closure was itself a background assertion:
the register held a GISA paper, the figure was about GISA, and the two were
joined without checking that the paper contained the figure. The pattern the
twelve-claims section identifies — an assertion that reads as common knowledge
and was never tested — reproduced itself inside the mechanism built to catch it,
one level up.

What would have caught it is cheap and was not done: a full-text search of the
paper for the number. That is now the standard for any figure attributed to a
work in this repository, and it is why the region grounding recorded on the same
day names five of its own premises as failed rather than presenting forty
verified ones.

### A second attribution hazard, met and not acted on

`notes/references.md` warns twice that a citation must come from the registry
and not from the depositing platform, and gives two instances. A third was met
while recording the region grounding: the ChinaRiceCalendar deposit at
`doi:10.7910/DVN/EUP8EY` lists its author field as "Jinyuan Liu, Hui Li", which
is two of the paper's eleven authors with their given and family names run
together. The paper's citation is carried instead and the deposit's is recorded
beside it. Three instances of one hazard, from three different platforms —
figshare, figshare again and Harvard Dataverse — is enough to treat reading an
author list off a deposit as a defect rather than a shortcut.

## The work the methods grounding implies

Eight items, recorded on 11 September 2026 from
[`notes/grounding-methods.md`](grounding-methods.md), with what each would cost.
**None is implemented here and none is claimed.** They are listed in roughly
ascending order of cost, which is close to descending order of how badly the
absence would read to a reviewer.

**Filter on the precision variable.** `methane_mixing_ratio_precision` is in
every Level 2 granule, carries the random error from the spectral fit, and this
pipeline neither grids it nor filters on it. A published precedent filters at
under 10 ppb (Schuit et al., 2023, doi:10.5194/acp-23-9071-2023). Cost: one more
variable in the existing covariate list and a re-run, which is the 28.9 GB
transfer the composite recipe already declares on-demand. Reachable with what is
already read in the sense that no new source is needed; not reachable without
re-gridding.

**Apply the albedo floor and the blended-albedo ceiling.** A SWIR albedo floor
of 0.05 and a blended-albedo ceiling of 0.75 outside summer preserve 69 percent
of high-quality retrievals and reduce seasonal regional biases by 7 to 21
percent (Nesser et al., 2024, doi:10.5194/acp-24-5069-2024). Surface albedo is
negative in 166 of the 926 covered cells here, which is not merely below the
floor but below zero, and a reflectance cannot be negative. Cost: the same
re-run as above, and both filters should go in the same one. The blended field
already addresses this for its own band, which is part of why it was added.

**Weight by representativeness rather than by sounding count.** Coverage "is not
an effective metric to limit representation errors" (Schutgens et al., 2017,
doi:10.5194/acp-17-9761-2017), and this project uses it as the composite's
quality metric in a figure, a raster band and every model weighting. The
implementable alternative is a spatial representativeness uncertainty equal to
the within-cell standard deviation scaled by the uncovered fraction, with
temporal weighting by that quantity rather than by count (Glissenaar et al.,
2025, doi:10.5194/essd-17-4627-2025). Cost: the within-cell variance is not in
the checkpoint, which holds sums and counts only, so this needs the same re-run;
after that it is arithmetic. **This is the item with the widest reach**, because
it would change the weighting of every baseline in the repository.

**Effective degrees of freedom on every reported correlation.** Every Pearson
and partial correlation here is computed over 926 cells with n treated as 926,
and both fields are strongly autocorrelated, so every p-value is
anti-conservative (Dutilleul et al., 1993, doi:10.2307/2532625; Afyouni et al.,
2019, doi:10.1016/j.neuroimage.2019.05.011). Cost: **the lowest of the eight.**
No new data, no re-run, one function over the committed covariate table, and it
would change several stated p-values. The Moran's I permutation test is the only
statistic in the repository that already handles its own dependence.

**De-attenuate the coefficients.** Regression calibration is unbiased where
simulation-extrapolation is not when no validation data exist, and needs only an
assumption about the measurement error variance (Nab and Groenwold, 2021,
arXiv:2106.04285); SIMEX-WLS handles measurement error and non-constant residual
variance together, which matters because a cell mean rests on 1 to 410 soundings
(Xu et al., 2026, doi:10.1080/20964471.2026.2660552). The variance is estimable
per layer without fieldwork: rice from the CCD-Rice polygons, impervious surface
from the GAIA-GISA allocation disagreement as a lower bound, methane from the
per-sounding precision. Cost: moderate, and no new download. **This is the most
consequential item in the list**, because attenuation is the only mechanism that
could manufacture this project's null result, and building second predictors
with different errors is evidence against it rather than a measurement of it.

**Set equivalence bounds for the central claim.** The claim that land cover does
not explain the methane field is a statement in favour of the null, which
p-values cannot support (Halsey, 2025, doi:10.1098/rsbl.2025.0506). Two
one-sided tests against a named smallest effect size of interest would support
it; the region grounding supplies a basis for naming the bound. Cost: low in
computation and high in judgement, because the bound has to be defended rather
than chosen. Until it exists the paper should claim that no association was
detected.

**Align priors before any Hefei comparison becomes a validation.** A satellite
and a TCCON retrieval use different a priori profiles and sensitivities, and the
correction adjusts both to a common prior using the satellite averaging kernel
(Rodgers and Connor, 2003, as applied by Balasus et al., 2023,
doi:10.5194/amt-16-3787-2023). The nine-day comparison already run gave a
blended bias of -5.74 ppb with a standard deviation of 5.79 and was computed
without it, so part of that figure is an artefact of comparing differently
constructed quantities. The second correction step, adjusting TCCON with
satellite kernels, has published precedent for being skipped as negligible.
Cost: moderate, and it needs the TCCON prior profiles as well as the granules'.
Also note the collocation rule: 1 hour and 100 km with a 250 m elevation limit
for satellite-to-TCCON, not the 1 hour and 5 km that paper uses for
satellite-to-satellite.

**Measure the residual autocorrelation range and draw a buffered decay curve.**
The block size here has never been justified from the data; the defensible
choice is the autocorrelation range of the model's residuals, and what the
repository has is Moran's I of the residual field, which is a different
quantity (Valavi et al., 2019, already in the register). Neither
cross-validation scheme buffers, while the literature's variants do, and the
recommended diagnostic is buffered leave-one-out across increasing radii so that
the decay of predictive power with distance from training data is visible as a
shape rather than asserted at one buffer (Wadoux et al., 2021,
doi:10.1016/j.ecolmodel.2021.109692). Cost: low, no new data, and it would also
settle whether the gap between this project's two schemes -- a spatial null of
0.332 under blocks against -0.091 under leave-one-province-out -- is the
extrapolation effect that literature predicts.

### Why this list is ordered by cost and not by value

Because the two orders agree here, which is unusual and worth noticing. The
cheapest items -- effective degrees of freedom, the residual range, the decay
curve -- are also the ones whose absence a reviewer would notice first, since
they need no new data and so have no excuse. The expensive items all share one
cost, a re-gridding run, and they should therefore be done together or not at
all: filtering on precision, applying the albedo bounds and computing within-cell
variance for representativeness weighting are three uses of one pass over the
granules.

**One item is deliberately not on the list.** Kappa is not to be computed. Two
independent authorities call correction for chance agreement bad practice
(Stehman and Foody, 2019, doi:10.1016/j.rse.2019.05.018; Pontius and Millones,
2011, doi:10.1080/01431161.2011.552923), and `ERRATA.md` 6.5 has been corrected
accordingly rather than left asking for it.

## The PPPM route, discussed repeatedly and recorded nowhere until now

`notes/repository-architecture.md` step 3 records that the rice reimplementation
was **not done, and deliberately**, with published products substituted for it.
That is the decision and it is recorded. What was never recorded is the
alternative it displaced, which has been discussed at length across sessions and
existed only in conversation. This section is that record. **Nothing is
implemented and no choice is made here.**

### What the thesis did

The 2023 thesis mapped paddy rice with the phenology- and pixel-based paddy rice
mapping algorithm of **Zhu, L., Liu, X., Wu, L., Liu, M., Lin, Y., Meng, Y.,
Ye, L., Zhang, Q., and Li, Y. (2021)**, *Detection of paddy rice cropping
systems in southern China with time series Landsat images and phenology-based
algorithms*, *GIScience & Remote Sensing* 58, 733–755,
`10.1080/15481603.2021.1943214`. **That citation was not in
`notes/references.md` and has been added.** Its absence is worth noting: the
register held the thesis's other pillar method, GAIA, from the start, while the
method that produced half the thesis's land-cover layers was missing.

The paper's own contribution is to "improve the phenology- and pixel-based paddy
rice mapping (PPPM) algorithm by simultaneously considering the phenology
signatures in the rice transplanting and heading periods", and it generated
**annual maps of single-cropping and double-cropping rice across southern China
from Landsat 5, 7 and 8 for 1999 to 2019 on Google Earth Engine.** The thesis
describes applying the algorithm with EVI, NDVI and LSWI, phenological windows
from the Ministry of Agriculture of China, and validation against National
Bureau of Statistics provincial sown area.

The implementation ran in Earth Engine scripts behind a Yale account that is no
longer accessible, so the code and outputs are unrecoverable. **One premise
needs correcting here**: `ERRATA.md` 6.1 does *not* record the thesis's script
links as dead. It records that "their current resolvability has not been
established" and that "they were not dereferenced, which is why no claim is made
about whether they still resolve." The inaccessibility is of the account, not a
demonstrated 404.

### Why a reimplementation would be worth doing

Two reasons, and the first is the one that matters for a paper.

**It would test the thesis's own method rather than replace it.** As things
stand the reproduction substitutes published products for the thesis's
algorithm, which closes the question of what rice extent is and leaves open the
question of whether the thesis's method produced the extent it reported. Those
are different claims, and the current arrangement reads as a substitution rather
than a reproduction of the rice half. `ERRATA.md` and the architecture note both
say so; neither says what the alternative would have been.

**It would produce a rice layer for 2000 and 2010.** The committed NESDC product
covers 2017 to 2022 and reaches none of the thesis's historical years. CCD-Rice
reaches 1990 to 2016 and so covers 2000 and 2010 but not 2018. A PPPM
reimplementation would cover all three from one method, which no combination of
published products does.

### What it needs, and what is established about each

**Landsat Collection 2 Level-2 surface reflectance.** `notes/dataset-leads.md`
records this as **verified accessible** through the Microsoft Planetary Computer
STAC API, HTTP 200 anonymously with no key, with the licence recorded as it
reads: the collection's `license` field says `proprietary`, which is the STAC
convention for "see the link", and its licence link is titled *Public Domain*, pointing
at the USGS data policy.

**The sensors covering the three years.** Landsat 5 TM for 2000 and 2010, and
Landsat 8 OLI for 2018. **A premise needs narrowing here**: Landsat 5 acquired
imagery until **November 2011**, when the Thematic Mapper failed, and was
decommissioned on 5 June 2013 — so "Landsat 5 TM to 2012" overstates the record
by about a year. It is immaterial for 2000 and 2010 and would matter for any
year after 2011. Landsat 8 launched 11 February 2013. Landsat 7 ETM+ spans all
three years and carries scan-line-corrector striping from 2003, which is why the
thesis's own description names TM, ETM+ and OLI together.

**SWIR1**, which is band 5 on Landsat 5 TM and Landsat 7 ETM+ and **band 6 on
Landsat 8 OLI** at 1.57 to 1.65 micrometres. The band index changes between
sensors and a reimplementation spanning 2000 to 2018 crosses that boundary,
which is the kind of detail that silently produces a wrong layer. LSWI, the
index PPPM uses for the flooding signal, is computed from NIR and SWIR1, so the
same boundary applies to NIR.

**The QA band** for cloud masking, which is the next paragraph's subject.

### The constraint, which is the finding rather than an obstacle

Phenology-based rice mapping in southern China is limited by cloud, and the
limit has been quantified. CCD-Rice states it directly: "in southern China,
where rice is extensively cultivated, annual averages of cloud-free Landsat
observations were **fewer than eight between 1984 and 2017**", and that "such
sparse observations pose challenges to rice mapping studies, especially when
employing phenology-based methods, for which the impact of clouds on the
classification accuracy cannot be ignored" (Shen et al., 2025,
`10.5194/essd-17-2193-2025`, already in the register). It also states that the
limitation "hinders the application of both methods, especially for
phenology-based methods that rely on irrigation signals during the transplanting
period". **CCD-Rice attributes the count to Zhou et al. rather than measuring
it**, so the primary source is one step further away and is not in the register.

Fewer than eight cloud-free observations a year, against an algorithm that needs
to catch a transplanting flood and a heading peak inside specific windows, is
the mechanism. **So a faithful reimplementation would very likely reproduce the
thesis's own Shanghai underestimate**, and demonstrating why is a stronger
result than noting that it happened. That reframes the reimplementation from a
repair into an experiment: the question it would answer is not whether the
thesis's rice layer was right but whether its method could have been right given
the imagery available.

### The alternative the grounding surfaced, which may be better

`notes/grounding-methods.md` records the GRPI method: Landsat at 30 m to
identify flooded vegetation, combined with a 30 m global cropland database and
country-specific emission factors, giving monthly emissions on a 0.1 degree
grid, with the authors stating the method "can be readily applied to other
years" and that interannual variability in Asia is under 8 percent while
"decadal trends can be more important" (Chen et al., 2025,
`10.1029/2024EF005479`, already in the register).

**The two routes produce different things and that is the choice, not their
relative quality.**

* **A PPPM reimplementation tests the thesis's method.** Its output is an extent
  map for 2000, 2010 and 2018 from one algorithm, directly comparable to the
  thesis's Table 1, and its most likely finding is why the method underestimated
  where it did.
* **A GRPI-method inventory produces something usable as an inversion prior.**
  Its output is emissions rather than extent, on the grid the field's inversions
  use, and `notes/grounding-methods.md` establishes that a better rice prior
  demonstrably moves an inversion's answer and cut model-observation bias by 40
  percent when done for Heilongjiang.

The second serves the emissions framing in `notes/paper-target.md` and the first
serves the reproduction framing. **Neither is chosen here**, and the decision
should wait on the IMI preview, because if TROPOMI cannot constrain emissions
over this domain then the prior-building route has no destination and the
method-testing route is the only one with a purpose.

One thing both share: they need the same Landsat access, the same sensor-boundary
care, and they meet the same cloud limit. The constraint is a property of the
imagery over this region, not of either algorithm.

### The maps already exist, which changes what a reimplementation is for

Added 14 September 2026, from the rice grounding pass. The section above was
written as though the PPPM maps for this region were something only a
reimplementation could produce. **They are not. Zhu et al. (2021) generated
them and says so.** Verbatim, the authors "generated annual maps of SCR and DCR
in southern China with image collection of Landsat 5, 7, and 8 from 1999 to 2019
using the Google Earth Engine platform", with overall accuracies from 81.0 to
98.1 percent depending on the area of interest, and a total rice area falling
from 208,614.6 km squared in 2000 to 171,474.3 km squared in 2019. Single- and
double-cropping rice, annually, twenty-one years, by the thesis's own algorithm,
covering all three of its years.

That does not make the reimplementation pointless, and it changes what it would
be for. The experiment framed above — establishing whether the method could have
been right given fewer than eight cloud-free observations a year — is unaffected,
because it needs the algorithm run rather than its output read. What it removes
is the *coverage* argument. A reimplementation was listed above as the only route
to a single-method layer spanning 2000, 2010 and 2018; if these maps are
obtainable, reading them is that route, and it costs a download rather than a
reimplementation.

**Two questions were carried into the rice grounding as open. One is now
answered and one is not.**

The answered one was whether "southern China" includes the northern parts of
Anhui and Jiangsu, which matters because the Huainan-Huaibei coalfield sits in
northern Anhui and the committed NESDC raster stops classifying there. **It
does.** The paper reports that "relatively stable SCR mainly distributed in
Anhui, Hubei, and Jiangsu provinces whereas DCR occurred in Guangdong, Hunan and
Jiangxi provinces", which names Anhui and Jiangsu as the core of the stable
single-cropping region rather than as its margin. This project's own regional
table agrees on the cropping system: both provinces are almost entirely
single-cropped.

The open one is whether the maps are distributed. It could not be settled. The
article is paywalled, OpenAlex records no open version, and the DOAJ record's
only full-text link is the publisher DOI, so no data availability statement was
readable. **That is now the gating question for the whole PPPM route** and it is
one email or one library request away, which is why it is queued in
`notes/paper-target.md` rather than left here.

## The reported cross-validation combination, decided 16 September 2026

Queue item 0i. Four combinations of two schemes and two weightings give four
answers for the same model on the same data, and every record in this repository
quoted one of them without saying which, because that is the combination the
diagnostic figure uses. This records the grid, the reasoning and the decision.

### The grid, which no record held

Held-out R squared, and in parentheses the same figure above that combination's
own constant. B = spatial blocks, P = leave-one-province-out, u = unweighted,
w = weighted by sounding count. Operationally corrected field.

| model | B/u | B/w | P/u | P/w |
|---|---|---|---|---|
| impervious fraction | +0.085 (+0.093) | +0.024 (+0.028) | −0.117 (+0.055) | −0.162 (−0.077) |
| rice, single | −0.031 (−0.023) | −0.092 (−0.089) | −0.067 (+0.105) | −0.414 (−0.329) |
| rice, combined | −0.032 (−0.024) | −0.092 (−0.089) | −0.059 (+0.114) | −0.406 (−0.320) |
| both fractions | +0.017 (+0.025) | −0.077 (−0.074) | −0.129 (+0.043) | −0.845 (−0.760) |
| both plus interaction | +0.033 (+0.041) | −0.042 (−0.039) | −0.077 (+0.095) | −0.796 (−0.711) |
| spatial null | +0.332 (+0.341) | +0.514 (+0.517) | −0.091 (+0.081) | +0.003 (+0.088) |
| albedo, SWIR | +0.476 (+0.485) | +0.316 (+0.319) | +0.290 (+0.462) | +0.066 (+0.151) |
| wind | +0.653 (+0.661) | +0.563 (+0.566) | +0.633 (+0.806) | +0.311 (+0.396) |
| sampling composition | +0.463 (+0.472) | +0.418 (+0.421) | +0.265 (+0.437) | −0.244 (−0.159) |
| trend surface | +0.240 (+0.248) | +0.258 (+0.261) | −0.286 (−0.114) | −0.077 (+0.008) |
| constant, global mean | −0.008 | −0.003 | −0.172 | −0.085 |
| constant, per province | +0.103 (+0.111) | +0.056 (+0.059) | −0.172 (+0.000) | −0.085 (+0.000) |

**The above-constant column changes the picture and nothing had computed it
across all four.** On raw held-out R squared impervious fraction is positive in
one combination of four. Above a constant fitted on the same training data it is
positive in three, because under leave-one-province-out the constant itself
scores −0.172: a province's mean differs from the domain's, so withholding a
whole province penalises every model including the one that has no predictors.
Reporting "positive in one of four" is true of the raw metric and misleading
about the model.

### What is known about each scheme, and the connection nobody had drawn

`notes/grounding-methods.md` records the relevant properties and they are not
restated here. Three bear on this decision.

Neither scheme buffers and the literature's variants do. Leave-one-province-out
is the most extrapolative design available on this lattice, which is where the
pessimism Wadoux and others document bites hardest. And the buffered decay curve
indicates the two schemes bracket rather than disagree, with the spatial null's
province-out value matching its buffered value at a radius comparable to a
province's width.

**The connection that had not been made is between the residual range and which
end of the bracket is which.** The impervious model's residual half-sill range is
96.1 km on the operational field; the block is 95.0 km at its narrowest. **The
block is marginal against the residual range by about one percent**, so residual
structure persists across a block boundary and the block scheme's figures are the
optimistic end of the bracket rather than a neutral midpoint. Province-out is the
pessimistic end. That ordering is now established rather than assumed, and it is
what makes a range reportable: the two ends are known-imperfect in known and
opposite directions.

### What is known about the weighting, which is that neither is right

`notes/grounding-methods.md` records two distinct objections to sounding-count
weighting: this repository's own, that it tilts fits toward flat bright terrain
because that is where the retrieval succeeds, and the literature's, that count
does not bound the error that actually matters. The implementable alternative,
representativeness weighting, is queued and blocked behind the accumulator change
that queue item 0g also needs.

**So the choice is between two known-imperfect options and not between a right
and a wrong one**, and whatever the paper reports has to say so. Unweighted
treats a cell resting on one sounding as equal to a cell resting on 410;
count-weighted treats count as a proxy for reliability that the literature says
it is not.

### The decision: report the range, with a named reference point

**The land-cover result is reported as a range across the four combinations, with
all four tabulated, and with spatial blocks unweighted named as the reference
point wherever a single figure is needed — labelled as the optimistic end of the
bracket rather than as the answer.**

Three reasons, in order of weight.

**First, the spread is a property of the evaluation and not of land cover**, which
Part 3b of this pass established and which no record had. Across the four
combinations on the operational field the range for impervious fraction is 0.247
of R squared. For wind it is 0.342, for albedo 0.410, for the trend surface 0.544,
for the spatial null 0.605, for sampling composition 0.708, and for the two
fractions together 0.862. **Land cover has the smallest four-way spread of any
predictor in the suite.** Attributing that spread to land cover, by quoting one
combination as though it characterised the model, would assign to the predictor
something that belongs to the design.

**Second, the two ends are known-imperfect in opposite directions and the decay
curve says they bracket.** A range between a design that is marginally too
optimistic and one that is structurally too pessimistic is a more accurate report
of what was measured than either end alone.

**Third, the range is itself the result.** That a model's apparent skill moves by
a quarter of an R squared under defensible changes to the evaluation is a
statement about how weakly the association is constrained, and it is the
statement the capability framing predicts. Collapsing it to one number discards
the finding.

**What the paper loses** is a single quotable number, which makes the result
harder to state in a sentence and harder to compare against papers that quote
one. The mitigation is the named reference point: block/unweighted is quoted
where one figure is needed, always with its label, so a reader comparing against
another study has a defined figure rather than a range they must collapse
themselves.

**And two rules follow that apply everywhere in this repository.** No land-cover
R squared is written without its scheme and weighting. No figure showing one
combination omits which combination it shows.

### What the decision does not change

**The central conclusion holds under all four combinations and is strengthened by
saying so.** No land-cover model achieves positive held-out skill where the
spatial null also achieves it — on any of the three fields, under any of the four
combinations.

There are three combinations of twelve in which a land-cover model scores above
the null on the above-constant metric, and all three are leave-one-province-out
unweighted, one per field. **In all three, both models are negative in raw
held-out R squared**: on the operational field rice-combined is −0.059 against
the null's −0.091, on the blended field −0.065 against −0.125, and on the
deseasonalised field the two fractions together give −0.077 against −0.110. So
the exception is "everything fails and land cover fails slightly less", not "land
cover wins". Stated precisely: **land cover never beats the null where the null
has positive skill, and beats it only where neither does.**

The claim about where the exceptions fall is unaffected: `README.md` already
scopes its exception count to spatial blocks at both weightings.

## What drafting the results section exposed, 15 September 2026

The methods draft's return was a fourth field found inside a list of three and
twenty-four unreachable artefact numbers. The results draft's return is smaller
in count and sharper in kind: **the decisions it forced are all about scope**,
because a results section has to say not only what a number is but under which
conditions it holds.

### The decisions the records left open

**Which scheme and weighting the reported figure comes from was never decided,
and it is the most consequential open decision this project has had.** Held-out
R² for impervious fraction on the primary field is +0.085 under spatial blocks
with no weighting, +0.024 under blocks weighted by sounding count, −0.117 under
leave-one-province-out unweighted and −0.162 under leave-one-province-out
weighted. **The same model on the same field spans a quarter of an R² across the
four combinations, and no record states which one a paper reports.** Every
grounding record quotes 0.085 or a figure near it, because that is the
combination the diagnostic figure uses, and none of them says so where the number
appears. Writing a results table put all four in one place for the first time and
made the omission unmissable. The draft reports all four in a table and names the
combination in every sentence that quotes one.

**The negative result's scope was never stated either.** The records say "no
evidence that land cover explains the field", which is the right *form* — a failed
detection rather than a claim in favour of the null — and it is silent on extent.
The honest scope, now written, is that land cover's held-out skill is positive in
one of four scheme-weighting combinations and negative in three, and that where
positive it is a quarter of the spatial null's and an eighth of wind's.

**The zero-order-to-partial attenuation had no number anywhere.** A resolver
existed named `collinear.reduction_percent` and it measures something else: how
much the operational bias correction reduces the field's albedo slope, which is
2.1 % unweighted. The obvious sentence in a results section — how much of the
impervious association survives control for albedo — needed a quantity nothing
had computed, which is 94.0 %. **Both numbers belong in the section and they were
one resolver away from being confused for each other**, and a first draft did
confuse them. The claim checker caught it only because the two values differ by
two orders of magnitude; had the correction removed 90 % of the albedo slope
rather than 2 %, the substitution would have passed.

**The coverage saturation curve has no scalar summary.** The figure holds the
shape and the draft describes it qualitatively, because nothing records the answer
to the question a results section asks: after how many granules did coverage
reach, say, 95 % of its final value. That is a one-line computation against an
artefact that already exists.

### Work not done, as distinct from not decided

**The blended field has no measured albedo slope *in the artefact*.**
`albedo_correction_2018.csv` computes the slope on shortwave-infrared and
near-infrared albedo for the raw retrieval, the operationally corrected field,
the correction itself and the deseasonalised field — and not for the blended
field. So nothing could resolve it, and the results draft could not quote it.

**This paragraph was wrong when first written on 15 September 2026 and is
corrected here rather than deleted.** It said the project "has never measured"
the blended field's albedo dependence. It had. The measurement is recorded in
this file under *The albedo dependence rose* and in `data/processed/README.md`,
with the same figures a re-run produced on 16 September: a shortwave-infrared
slope of 232.78 ppb per unit albedo unweighted against the operationally
corrected field's 199.66, and Pearson rising from +0.700 to +0.762. **The gap
was between the decision log and the artefact, not in the work.** That is a
smaller defect and a different one, and mistaking the second for the first
produced a false justification in the results draft, which
`notes/draft-results.md` now no longer carries.

**No representativeness-error estimate exists for the composite.** The methods
record carries the literature's statement that observational coverage is not an
effective metric for representation error, and this project measured coverage.
Nothing measured the error. Queue item 17 proposes representativeness weighting
in place of sounding-count weighting, and `notes/paper-target.md` records that the
per-cell spread such an estimate needs is not recoverable from the current
accumulator — so this is blocked behind the same change as queue item 0g rather
than merely unstarted.

**Equivalence bounds remain unset**, which is why §3.4 of the draft reports a
failed detection and not an absence. Already queued as item 18.

### Two figures the contribution needs and nobody planned

`figures/README.md` records eleven figures built and three planned. The results
draft cites six of the eleven and neither of two results that are now central:

* **The buffered decay curve**, which is the direct measurement of the impervious
  coefficient's spatial instability, and which exists only as a ten-row table per
  field.
* **The DOFS sweep and the prior-free threshold**, which are the capability claim
  itself, and which exist only as a twenty-row table.

Under the framing in place when the figure set was planned neither was a
headline. Under the capability framing both are, and **a reader of the two
sections the paper rests on has nothing to look at.** Both are line plots over a
swept parameter and neither needs new data, which puts them ahead of the three
planned figures on value and level with them on cost.

**And five of the eleven existing figures have no place in a results section.**
Three — the native-resolution land cover, the urban change series and the
provincial breakdown — document the predictors' provenance and their
disagreements, which is methods and errata material. Two document the pipeline
and the reproduction's structure and belong in neither. That is not an argument
for removing any of them; it is an argument for knowing, before the remaining
three are drawn, that the figure set was built to answer the 2023 thesis's
figures rather than this paper's results.

### The general point, which differs from the methods draft's

The methods draft exposed **unreachable numbers**: artefacts committed with no way
to quote them. The results draft exposed **unscoped numbers**: quantities quoted
throughout the records without the conditions under which they hold. Those are
different failures with the same cause — a record can state a number in
isolation, and a continuous section has to place it among its alternatives.

**Six grounding passes quoted 0.085 and none reported that the same model gives
−0.162 under a different scheme.** Nothing was hidden and nothing was wrong; the
figure simply never had to sit next to its siblings. That is what a results table
does and what a record does not.

## What drafting the methods section exposed, 15 September 2026

`notes/paper-target.md` recorded the absence of prose as the largest single gap.
Writing [`notes/draft-methods.md`](draft-methods.md) closed part of it and, as
the figure work did with the study extent, **drafting turned out to be a
different test from recording.** A methods section has to be continuous: every
sentence has to follow the last, every quantity has to have a value, and every
step has to be described in an order. Six grounding passes never required any of
those things, and what follows is what the requirement surfaced.

### Decisions the records left open, which a continuous section cannot leave open

**Which field is the primary target was never decided.** Four methane fields are
carried — raw, operationally bias-corrected, blended, and deseasonalised — and
three of them have complete 88-row baseline suites. No record states which one a
paper's headline number comes from, because no record ever had to write a single
sentence containing one. The draft names the operationally bias-corrected field
as primary and the other two as tests of whether the result depends on the
correction. **That is a decision made while drafting, not one recovered from the
record**, and it is defensible for a stated reason — it is the product's own
recommended field — rather than because anything here chose it.

**The number of methane fields was wrong in the brief and in my own first
draft.** Both said three. There are four. The deseasonalised field has its own
composite, its own five-band raster, its own 88-row baseline suite and its own
22-row diagnostic table, and it is the only one of the four that tests whether
the association is an artefact of the sampling calendar — which, given that
sounding yield over this domain runs against the rice growing season, is the
single most relevant robustness check in the set. **It was omitted from a draft
written by someone who had read every record in this repository**, which says
something about how a fourth item in a list of three survives six passes.

**The covariates have no recorded roles.** Seven are gridded and every record
treats albedo as an artefact axis and wind as an alternative explanation. None
says what solar zenith angle, surface altitude or surface pressure are *for*. A
methods table needs a role column, so the draft assigns one to each — light-path
length, column length, column mass — and those three assignments are inferences
made at the keyboard. They are defensible and they are not sourced.

**The cell size in kilometres is stated nowhere at the domain centre.**
`figures/README_fragments.md` gives 24 by 28 km at 31.7° north, which is the
latitude of the detail box over the Yangtze mouth rather than of the domain,
whose centre is 31.075° north. Both latitudes round to the same figure, so
nothing is wrong; but the number a methods section needs had to be recomputed
rather than quoted.

**Neither the model count nor the fit count is recorded anywhere.** The baseline
suite holds 22 model specifications and 88 fitted model-scheme-weighting
combinations per target field. Both had to be counted from the artefact. A
methods section states both in its first sentence about the analysis.

### Things the draft could not state because the work was not done

These are distinct from the above: not undecided, but absent.

**The composite records no pre-filter sounding count.** The accumulator retains
per-cell sums and counts after filtering, so the number of soundings *read* from
the 223 productive granules, and the number rejected by the quality filter, are
not recoverable from any artefact. The standard methods formulation — "N
soundings were read, of which M passed quality control" — **cannot be written.**
Every count in the draft is post-filter. This is a queue item and it is cheap:
the accumulator would need one more counter.

**No accuracy assessment exists for either land-cover product**, which the draft
states as a limitation on effect-size claims rather than on the capability
claims. Already queued.

**No prior-profile alignment exists for the TCCON comparison**, so the nine
coincident days support a feasibility statement and nothing else. Already queued.

**No inversion has been run**, so the capability section reports a
reimplementation of a published closed-form estimate rather than a tool's own
output. Already queued as the IMI preview, and `notes/paper-target.md` now ranks
it the most valuable outstanding item precisely because the draft made the
dependence visible: the paper's central number is currently the only major figure
in it that no external tool has confirmed.

### The mechanical gap drafting exposed, which was the largest

**Tier 0 committed four artefacts and none of them could be quoted from prose.**
The effective-degrees-of-freedom table, the residual range table, the buffered
decay curve and the DOFS sweep had no resolvers in
`scripts/verify_claims.py`, so every number the capability section rests on would
have entered the draft unchecked and stayed unchecked. Under the earlier framing
that was tolerable, because those artefacts supported a robustness argument.
Under the capability framing they *are* the argument. Twenty-four resolvers were
added for them.

**The general point is about when a verification mechanism gets extended.** This
repository's claim checker covers what someone thought to mark, and what gets
marked is what gets written about. The Tier 0 artefacts were recorded, tested for
reproducibility, and discussed at length in three files — and none of that
required quoting a number from them in scanned prose, so none of it exposed the
gap. **Drafting did, immediately, because a methods section cannot describe a
computation without stating its result.**

### Three errors of my own, caught before the commit

Recorded because their detection method differs and that is the useful part. A
fraction written as a percent was caught by the claim checker on the first run.
Two negative R-squared values written with a Unicode minus sign were caught by
the same run, because the marker's number pattern matches an ASCII hyphen and
silently captured the digits without the sign — **a marked claim can be wrong in
a way the marker does not see, if the character before the digits is not the one
the pattern expects.** And the GAIA and GISA year-of-change directions were
stated backwards, caught only by reading `config/sources.yml` before committing;
the claim checker cannot see a prose statement with no number in it.

## The register audit of 14 September 2026, and the general point it makes

Two defects in committed register entries were found on 13 September, both by
accident: a later pass needed the same paper for something else and noticed the
citation was wrong. Zhong and others had an author list reading "Zhong, and
others" and a page range off by one; Sicsik-Paré and others had the fourth author
placed third and the third dropped entirely. Both had been written during the
methods grounding pass, and both were written from search-result phrasing rather
than from the DOI's own metadata.

**Two accidental finds in one file are a sample, not a pair of incidents.** This
section records the audit that followed.

### Establishing the suspect population

Content negotiation for every DOI's author list was adopted partway through, on
11 September, during the pass that recorded the inversion frame and the urban
layer — the pass in which six wrong first authors were caught in a single
sitting before any of them reached a commit. Everything the register held before
that point was written without it.

**Provenance was not recorded per entry**, so which entries those were had to be
reconstructed from git history: walk the commits that touched
`notes/references.md` in order, diff the set of backticked DOIs at each, and
attribute each DOI to the commit that introduced it. That gives twelve commits
and a clean partition.

| Commit | Pass | DOIs introduced | Negotiated? |
|---|---|---|---|
| `baa7db5` | the register's creation | 14 | no |
| `d647fd4` | citing the reproduction's methods | 12 | no |
| `07a9f28` | narrowing the waste claim | 1 | no |
| `91a656f` | citing the errata's uncited claims | 10 | no |
| `e135018` | the diagram sources | 3 | no |
| `0de7113` | the region grounding | 23 | no |
| `3b2fc4f` | the methods grounding | 40 | no |
| `8a292ee` | the inversion frame and urban layer | 25 | yes, from here |
| `55a864a` | the PPPM and GRPI routes | 1 | yes |
| `929e5e0` | queue, inventory, fourteen sources | 15 | yes |
| `0814759` | queue, inventory, twenty-two sources | 22 | yes |
| `668ef80` | inventory, queue, twenty-nine sources | 28 | yes |

**One hundred entries of one hundred eighty-nine were suspect** — not the
methods pass alone, which is what the brief that commissioned this audit
expected, but everything up to and including it. The conservative reading is the
right one here: an entry that cannot be demonstrated to have been negotiated has
to be treated as though it was not, because the defect is invisible to reading.

In the event all one hundred eighty-nine were re-negotiated, because once the
comparison was scripted the marginal cost of the other eighty-nine was a few
minutes of network time. That turned out to matter: **eleven of the twenty-three
defective entries were in the negotiated half**, including two of my own from
the two preceding passes.

### What was wrong

Twenty-three entries, thirty-one fields, in six classes.

**An author list belonging to a different paper, with every other field
correct.** This is the worst single case and the one that would most certainly
have reached a submission. `10.5194/amt-11-6379-2018` is Sheng and others
(2018), *Comparative analysis of low-Earth orbit (TROPOMI) and geostationary
(GeoCARB, GEO-CAPE) satellite instruments*. The register had the correct title,
DOI, journal, volume, page range and year — and the eight-author list of
`10.5194/acp-18-6483-2018`, the same group's companion Southeast US inversion
paper, same first author, same year, same region. Four of the names are not on
the paper cited and one author of five is missing. **Nothing a reader could check
by eye was wrong.**

**Names imported from elsewhere.** Ploton and others carried four wrong surnames
at positions seven to ten; Passafaro and others carried four at positions two to
five. In both cases the substituted names are plausible co-authors of the same
first author's other work.

**A wrong first author**, the seventh instance this register has now produced: the
MultiTab preprint was entered as Kim where the paper is Lee, with Kim appearing
at positions four and six.

**Four entries had no author list at all.** The bold citation head held the
journal, volume and article number — "**Atmospheric Research 308, 107542
(2024).**" — which reads as a citation head at a glance and contains no author.

**Seven truncations that hid what the citation was for**, of which three were a
bare surname plus "and others" and four were an uncounted "and others" after one
or two names. Two further entries dropped trailing authors with no marker at all.

**Ten stated truncation counts were wrong**, which is the largest class and the
one no earlier pass had thought to check: "and 21 others" for a thirteen-author
paper, "and 10 others" for eleven, "and 9 others" for nine. Two were mine.

**Seven page ranges were wrong**, including one that was wrong entirely
(11316–11326 for 11342–11351) and three that carried only a first page where the
journal has a range. And **three entries used the online-publication year where
the print year differs**, which contradicts this register's own stated convention
and is the same inconsistency `ERRATA.md` 6.3 faults the 2023 thesis for.

### What was not wrong, which took most of the effort to establish

A first scripted comparison flagged sixty-six entries. A second, after fixing the
comparison's own handling of surname particles and hyphenated initials, flagged
twenty-three. **The difference is entirely artefacts of the checking**, and
working through them is where the audit's time went:

* Crossref HTML-escapes ampersands, so every *Environmental Science & Technology*
  looked like a mismatch — sixteen entries.
* Surnames with lowercase particles ("van der A", "aan de Brugh", "de Leeuw")
  and hyphenated or particled initials ("Z.-C.", "M. del M.", "Md. A.") break a
  naive split on commas — about eighteen entries.
* Seventeen entries have registry records that cannot supply their citation at
  all: literal institutional author strings, transposed or mis-cased deposit
  fields, two IPCC chapters for which Crossref returns no authors, one paper for
  which it returns one author of four, and two JSTOR records carrying a start
  page where the register gives the range.

**That last group is now recorded** in `scripts/build_references_bib.py` as
`PROVENANCE`, precisely so the next audit does not have to rediscover that
flagging them is wrong.

### The general point, which is the transferable one

**A citation assembled from a search result looks correct and is not checkable by
reading it.** That is the whole finding, and this project has now demonstrated it
three times in three different fields of the same records:

* **Five DOIs** that resolved — four to the wrong paper, one to nothing — and
  were carried as real citations across four consecutive passes.
* **Six wrong first authors** drafted from search phrasing in a single sitting,
  caught only because a pass began negotiating every DOI before writing.
* **Twenty-three entries** wrong in thirty-one fields, found here, of which the
  worst had every checkable field right and the author list of another paper.

The mechanism is the same each time. A search result contains a title, a year, a
journal and some author surnames, arranged so that assembling a citation from
them feels like reading rather than inference. What it does not contain is the
binding between them. **Only negotiation against the registry establishes which
metadata belongs to which identifier**, and no amount of care in reading
substitutes for it, because the failure leaves nothing on the page to notice.

The corollary is about where to spend effort. Three of these defect classes were
found by scripted comparison in an afternoon; none was found by reading, over
eleven passes of writing and re-reading these same entries. **The register was
read many times and audited once.**

### What now guards against recurrence

`tests/test_register_authors.py`, which runs offline in the default suite,
because `notes/references.bib` is generated by content negotiation and committed
beside the register — so the authoritative record is already in the repository
and the comparison needs no network. It asserts that no author list is truncated
without a count, that a truncated list still names at least three authors, that
every citation head contains something shaped like an author list, that the first
author matches the negotiated record, and that named authors plus the stated
remainder equal the registry's count. The seventeen `PROVENANCE` entries are
exempted **by name rather than by heuristic**, because
`notes/grounding-methods.md` records this project's own reasoning that a check
firing on things that are fine is a check that gets turned off.

**What it does not guard.** A page range is checked only for running forwards,
which caught none of the seven wrong ranges because all seven were ordered. A
title or journal substitution would not be caught, because the register's prose
formats both differently from the registry and a fuzzy comparison there would
produce the false positives the paragraph above warns against. And the
print-against-online year cannot be checked offline, because the BibTeX carries
one year rather than both.

## What the grounding superseded, marked rather than rewritten

Four grounding records were written between 10 and 11 September 2026. Several
statements taken before them are now **superseded rather than wrong**: the
reasoning that produced them stands, and a cheaper or better route has since
appeared. This file's standing convention is to state both rather than falsify
the record, and these are the instances found.

### The flux-divergence gate, which was never actually written down

**This is the most awkward finding of the pass, because the gap is of this
repository's own making.** `notes/references.md` says of Liu et al. (2021),
`10.1029/2021GL094151`, that "`notes/decisions.md` records the gate that
established why the conversion is not feasible on this composite." It does not.
The only trace in this file is one clause in the uncited-methods section, which
lists "the flux-divergence conversion that was gated and declined" among methods
applied without a citation. **There is no section recording the gate's
reasoning.**

Worse, two files written in the last two passes —
`notes/grounding-methods.md` and `notes/dataset-leads.md` — refer three times to
"the flux-divergence gate recorded in `notes/decisions.md`". Those are
cross-references to something that was never here, added by work that assumed
the register's own description of this file was accurate. That is the same
failure mode the register records for citations: an assertion about a source
that was never checked against it.

What the gate's reasoning was, as far as it can be recovered: the conversion was
declined because the divergence method needs daily wind and concentration fields
at the cell scale, the daily fields are not recoverable from the committed
checkpoint, and both the concentration term and the wind term carry the sampling
artefact that `ERRATA.md` 7.4 records — so the quotient would inherit it twice.
**That account is recorded here as a reconstruction from conversation, not as a
verified computation**, and it is marked as such because nothing in the
repository demonstrates it.

**The gate is not reopened by the grounding and the reasoning still stands.**
What changed is that the question has a cheaper route. `notes/grounding-methods.md`
records that the IMI preview reports the expected degrees of freedom for signal
over a user-selected domain, costs nothing, and runs at this project's exact
resolution on the blended field already committed here. So the question "can
TROPOMI constrain methane emissions over these four provinces" no longer needs a
flux-divergence feasibility test to answer it, and `notes/paper-target.md` puts
that preview first in the queue.

### No accuracy assessment is possible

`notes/grounding-methods.md` states, of Olofsson's first three recommendations,
that this project "has no probability sample, **no reference data more accurate
than the map**, and so no analysis to be consistent about". That was written on
10 September 2026 and was true when written.

**It was superseded the next day by this repository's own inventory.** The
CCD-Rice validation polygons are published, openly licensed, 1.9 MB, verified
accessible, and carry 777 polygons inside the four provinces across six cover
classes — reference data visually interpreted from very-high-resolution imagery
and checked by three experts, which is more accurate than any map here. Together
with prediction-powered inference, which makes a small reference set usable
against a large map, an accuracy assessment of the rice layer is possible. The
statement in the methods record should be read as describing the position before
the polygons were found, and `notes/paper-target.md` records the assessment as
queue item 9 with the polygons as its prerequisite.

One qualification survives and is not superseded: the polygons are clean for the
NESDC and GISA layers and **contaminated for CCD-Rice itself**, whose thresholds
were re-determined against filtered rice areas. So the assessment is possible for
the layers this project uses and not for the product the polygons came from.

### Sounding count as the composite's quality metric

`data/processed/README.md` argues that "a cell's value is the mean of between 1
and 410 soundings, so its variance is roughly sigma squared over n and the
inverse-variance weight is the sounding count itself; on that argument the
weighted numbers are the ones to fit on", and then qualifies it: "sounding count
is not random over the study area, and the well-observed cells are
systematically the flat bright ones the instrument retrieves from, so weighting
also tilts every fit towards that terrain."

**That qualification is real and it is not the objection the grounding
raises.** `notes/grounding-methods.md` records a stronger one: coverage "is not
an effective metric to limit representation errors", and "even after substantial
averaging of data significant representation errors may remain, larger than
typical measurement errors" (Schutgens et al., 2017,
`10.5194/acp-17-9761-2017`). The repository's own objection is that count-based
weighting tilts the fit toward particular terrain. The literature's objection is
that count does not bound the error that matters at all, whichever terrain it
comes from.

Both stand and they are different. The implementable alternative — weighting by
within-cell spread scaled by the uncovered fraction, following the Level 3
formulation the methods record cites — is queue item 17, and it is gated by a
re-gridding pass because the checkpoint holds sums and counts without variance.

### Two smaller ones

**`notes/repository-architecture.md` step 6 says "one figure exists so far, of
nine planned".** Eleven exist and fourteen are planned, and
`figures/README.md` records the reconstruction of that count and why "nine" was
never backed by a list. The architecture note is a plan taken at a point in
time and its other steps carry struck-through text with the outcome beside them;
this one was not updated when the figure set grew. Left as it stands with the
correction recorded here, consistent with how the rest of that file treats its
own superseded plan.

**`notes/repository-architecture.md` step 3 says the rice reimplementation is
"not done, and deliberately".** That remains accurate, and it is now
accompanied: the section above on the PPPM route records what the displaced
alternative was, what it would need, and the cloud constraint that makes its
most likely outcome a finding rather than a failure. The decision is unchanged;
what was missing was the record of what it decided against.

### What was checked and found not to be superseded

The TM5 a priori departure gate, which was declined on the grounds that the
departure inherits the albedo bias intact while removing only 3.5 percent of the
variance. Nothing in the grounding changes that arithmetic.

`ERRATA.md` 5.1, which names four post-2023 reference products against the
thesis's claim that none existed. The grounding added a fifth route and
strengthened the item rather than superseding it.

The destriping entry in this file, which calls a self-implemented per-row
correction "the cheapest of the four and the most clearly missing". Still true
of the implementation. The methods grounding adds that the *official* correction
will never arrive for 2018 data, which removes the option of waiting rather than
changing the assessment of the option that exists.

## Queue item 1: the inversion feasibility question, answered by arithmetic

`notes/paper-target.md` put the IMI preview first in the queue because it gates
the paper's framing and costs nothing. **It could not be run, and the question
it would answer has been answered anyway.**

### Why it could not be run

Three access routes are documented and all three need an account this session
must not create. The free IMI product on the AWS Marketplace needs an AWS
account, which needs a payment method even where the product is free. The source
route from GitHub can be built locally in a container, but the IMI is a
GEOS-Chem driver: a local run needs the meteorological archive, the prior
inventory stack and the TROPOMI collection, which is the input volume the cloud
route exists to avoid moving. And the Integral Earth web interface is by
request. **The preview specifically is not a lighter path around this**, because
it reads the same prior and observation inputs as the full run; setting
`DoPreview: true` stops the pipeline after the preview rather than shrinking what
it needs.

### What was done instead

**The preview's DOFS estimate is closed-form and its inputs are almost all held
here.** `src/inversion_scripts/imi_preview.py` in
`geoschem/integrated_methane_inversion` computes an estimated averaging kernel
sensitivity per state vector element as

    a = sA^2 / (sA^2 + (s_superO / k)^2 / m_super)

with `k = alpha (M_air L g) / (M_CH4 U p)`, the superobservation error from
Chen et al. (2023), `sA` the prior error in kg m-2 s-1, and `m_super` the number
of days on which the cell carried at least one successful retrieval. The DOFS is
the sum of `a` over elements. `scripts/estimate_inversion_dofs.py` evaluates
that expression over this lattice with IMI's own defaults —
`PriorError = 0.5`, `ObsError = 15` ppb, `Res = "0.25x0.3125"` so `L = 25` km,
`alpha = 0.4`, `U = 5` km/h, `r_retrieval = 0.55`, `s_transport = 4.5` ppb — and
writes `data/processed/inversion_dofs_2018.csv`.

**This is a reimplementation of the preview's formula and not a preview run**,
and it is labelled that way in the script, the recipe note and the artefact.
The distinction matters because IMI's preview also reports observation maps, a
dollar cost and a SWIR albedo panel, none of which this reproduces, and because
a real preview would use a gridded prior where this uses an assumed total.

One input had to be derived. `m_super` is the count of observation *days* per
cell, and no committed artefact holds it: the composite records sounding counts,
not the number of distinct dates they came from. The checkpoint's per-granule
cell bitmaps do, one packed bitmap per granule over the flat grid, and
unpacking them against the granules' acquisition dates gives the count directly.
Over the 926 covered cells it is a **median of 23 observation days, mean 24.51,
maximum 65**, with a median of 4.40 retrievals per observation day. That is the
first time this repository has had that number.

### What it says

`k` is 1.25903 kg-1 m2 s for this resolution. Two results follow.

**The prior-free one, which is the one to quote.** Setting `a = 0.5` and solving
for emission needs no prior at all, because it depends only on the observation
counts. A median cell in this composite would need **0.0862 Tg a-1 — about 86 Gg
a-1 from a single 625 km2 cell — for the inversion to constrain it half
independently of the prior.** The best-observed cell, with 65 observation days,
needs 0.0492 Tg a-1. For scale, a large municipal landfill emits on the order of
10 to 50 Gg a-1, so **individual large point sources in this domain sit below
`a = 0.5` and above zero**: visible to an inversion as a partial constraint, not
as an independent measurement.

**The domain total, swept because the prior is not held here.** Expected DOFS
crosses the Permian work's practical minimum of 0.5 at 1.767 Tg a-1, IMI's own
minimum viability of 1 at 2.500 Tg a-1, and its marginal ceiling of 2 at 3.539
Tg a-1. *Corrected on 13 September 2026, and the original figures are worth
keeping visible: this paragraph said "about 2", "about 3" and "about 5", which
were the nearest swept points at or above each threshold rather than the
crossings. The script's own console line said "crossed at or below" and this
paragraph read it as the crossing. Sensitivity is very nearly quadratic in
emission at these magnitudes -- 0.160 at 1 Tg, 0.640 at 2, 1.439 at 3, 3.979 at
5, all of them 0.16 times the square -- so the nearest swept point above a
threshold overstates the crossing by 13 to 41 percent, and linear interpolation
between sparse points overstates it too. The sweep in
`scripts/estimate_inversion_dofs.py` was densified from eleven points to
twenty-three, the three crossings are bisected on the sensitivity expression and
written to the artefact, and the console now prints the bisected value. A
crossing claim now reads from a file instead of being eyeballed off a table.* Against the band the literature already in `notes/references.md`
supports for this domain — 5 to 12 Tg a-1, from Huang et al.'s 2018 Yangtze
River Delta inversion implying about 11.7 Tg a-1 for its domain and Duan et al.'s
seven-province agricultural share implying less than that for four provinces —
**expected DOFS runs 3.98 to 22.21.**

**And that band is a lower bound.** The sweep spreads each total uniformly over
926 cells. At small `a` the sensitivity goes as the square of a cell's emission,
so concentrating the same total into fewer cells raises the sum, and real
emissions are concentrated. A uniform prior is the least favourable arrangement
of any given total.

### What this implies, which is the first of the three outcomes and not the third

`notes/paper-target.md` set out three outcomes. This is the first: **an emissions
inversion over this domain is feasible, comfortably above threshold, and the
paper's framing is not forced to the reproduction reading.** The expected DOFS
at a defensible prior is between two and twenty times IMI's marginal ceiling.

Three qualifications belong with that, and none of them reverses it.

**Feasible is not free.** The DOFS says an inversion would extract information;
it says nothing about the 28.9 GB re-grid, the prior that would have to be built,
or the transport model. The methods grounding's transport-error ceiling of 12 ppb
against this field's 14.9 ppb spread is unchanged by this result.

**Feasible at the domain scale is not feasible per cell.** No cell in the swept
range reaches `a > 0.5`. The DOFS accumulates from 926 cells each weakly
constrained, which is what a domain-total inversion needs and not what a
per-cell attribution needs. So an inversion here could constrain the region's
emission; it could not attribute it to land cover cell by cell, which is the
question this project actually asked.

**And this is the preview's arithmetic, not the preview.** The number that would
settle it is one free run by someone with an AWS account, and
`notes/paper-target.md` keeps that as the item rather than marking it done.

### The correction this makes to the record

`notes/decisions.md` records the flux-divergence conversion as gated, and the
supersession section above records that the gate's reasoning was never written
down and that the IMI preview offered a cheaper route to the same question. **The
cheaper route turned out to be cheaper still than that**: not a preview run but
the preview's published formula, evaluated locally in about ten seconds against
observation counts this repository already had. The question was answerable
without an account, without a download, and without the gate.

## Queue item 2: twenty-seven of seventy-two correlations lose significance

`notes/grounding-methods.md` recorded that every Pearson and partial
correlation here is computed over 926 cells with `n` treated as 926, that both
sides of every one is a strongly autocorrelated field, and that the p-values
are therefore anti-conservative. **The correction has been applied and it is
larger than expected.**

### The choice of estimator, and why not the other one

Two are in the register. Afyouni, Smith and Nichols (2019) correct the
effective degrees of freedom of a correlation between two **time series**,
accounting for autocorrelation in each and for cross-correlation at lags. That
construction is ordered: it needs a lag index, and a two-dimensional lattice has
no lag ordering to use without inventing one. Clifford, Richardson and Hémon
(1989) and Dutilleul, Clifford, Richardson and Hémon (1993) correct the same
quantity for two **spatial** processes, using distance instead of lag. So
Dutilleul, and **the choice is about this data's geometry rather than about the
two methods' quality.**

`src/model/spatial_dof.py` implements it. Under the null the variance of the
sample correlation is approximately `tr(R_X R_Y) / n^2`, so the effective sample
size is `M = 1 + n^2 / tr(R_X R_Y)` and the modified t statistic runs on `M - 2`
degrees of freedom. The two correlation matrices are estimated from binned
empirical correlograms over great-circle distances — great-circle because the
lattice spans eight degrees of latitude and a planar approximation would be
wrong by percent at the edges.

**Calibration, measured rather than assumed.** On two independent white-noise
fields at 400 scattered locations the estimator returns `M` at about 0.87 of
nominal rather than 1.0, because the binned correlogram carries sampling noise
that inflates the trace. So the correction is mildly conservative even with
nothing to correct, and a shrinkage near 0.87 means "no dependence detected".
The estimator is also capped at `n + 1`: without the cap a noisy correlogram can
return more information than the data contain, which would make a corrected
p-value *smaller* than the nominal one and is the most misleading failure
available.

### How much independent information 926 cells carry

**A median effective sample size of 45.5 out of 926**, a shrinkage of 0.049.
Across all 72 correlations the median shrinkage is 0.0576 with a range of 0.0200
to 0.2517. On the 531-cell rice subset the median effective `n` is 77.9 of 531.

That is the finding in its own right and it deserves a sentence in the paper:
**this lattice carries roughly the independent information of fifty
observations, not of nine hundred.** Which is not a defect of the composite. It
is what a smooth field on a fine grid is, and it is the same property that makes
the spatial null hard to beat.

### What changed

`scripts/correct_correlation_dof.py` writes
`data/processed/correlation_dof_2018.csv`: 72 correlations with the nominal and
corrected tests side by side. It reads `albedo_confounder_2018.csv` and **carries
its coefficients forward unchanged**, correcting only the degrees of freedom,
because this exists to fix the significance of published numbers rather than to
replace them. The Pearson coefficients it recomputes reproduce the reported ones
to the last digit, over all 26 rows, and a test asserts it — without that the
correction would be meaningless, since the dependence would have been estimated
from different data than the coefficient.

It also **extends the set to the blended and raw fields**, whose correlations
existed only in prose and in no artefact.

**27 of 72 lose significance. 28 remain significant. 17 were never
significant.**

What survives, and it is the pattern the grounding predicted: every
albedo-to-methane relationship, at corrected p from 2.1e-04 to 2.6e-02;
albedo against impervious fraction; and the zero-order methane-against-impervious
association at +0.3452, corrected p 8.9e-03. The blended field's zero-order
impervious association survives too, at +0.3154 and p 2.9e-02.

What does not, and this is the consequential part:

* **Every partial correlation of methane on impervious fraction controlling for
  albedo**, on the operational field. The three-covariate partial of +0.1413
  goes from p 1.6e-05 to **p 0.116**.
* **Methane against rice fraction**, +0.0960, from p 0.027 to **p 0.293**.
* **Every weighted land-cover association.** Methane against impervious
  fraction weighted, +0.2124, from p 6.6e-11 to **p 0.115**.
* And the one `data/processed/README.md` called **"negative and significant"**:
  the blended field's partial of -0.0815 controlling for SWIR albedo, from p
  0.013 to **p 0.54**, and its weighted counterpart of -0.1031 from p 0.0017 to
  **p 0.45**.

### Two corrections to committed prose

`data/processed/README.md` reported that blended partial as significant at p
0.013 and 0.002. **Those p-values are withdrawn** and the file now says so. The
reading does not change — it was already over-control rather than a negative
urban effect — and the corrected test removes the need to explain a significant
negative at all.

`figures/README_fragments.md` said of the raw retrieval that "the impervious
association survives control, falling only from +0.440 to +0.151 at p 4.0e-06".
**The survival is real and much thinner than that**: corrected, p is 0.040,
still under 0.05 and no longer by a margin, while the weighted counterpart at
+0.125 goes from p 1.3e-04 to p 0.094 and does not survive. The caption now
says so, and the second reading it offered is weaker than it looked.

`notes/decisions.md`'s own earlier statements of these figures are left as
written, which is this file's standing convention.

### What it does not do

It corrects significance, not size. **No coefficient changed.** A correlation
that fell from significant to non-significant has not shrunk; the claim that it
differs from zero has lost its support. And the study's central negative result
is untouched in the direction that matters: the held-out R squared comparisons
against the spatial null are not significance tests and this correction does not
reach them. What it reaches is the supporting apparatus — the albedo confounder
test's partials, and the blended field's negative — and in both the correction
makes the repository's own cautious reading more clearly right rather than less.

## Queue items 3 and 4: the residual range, and the decay curve it gates

### Item 3: the block size has a different answer for each model

`scripts/measure_residual_range.py` fits an empirical semivariogram to each
model's in-sample residuals and writes `data/processed/residual_range_2018.csv`.
In-sample and not held-out, because Roberts' rule is about the structure a
fitted model leaves behind, and held-out residuals from a blocked scheme mix
that with the fold geometry — which would make the diagnostic depend on the
choice it is meant to inform.

**The method agrees with the earlier one.** The variogram of the methane field
itself gives a half-sill range of **103.2 km** against the 102 km
`data/processed/README.md` already records, computed in a different session by
different code. That is the check that matters before anything downstream is
trusted.

**The block has two widths and only one was ever quoted.**
`data/processed/README.md` says "a four-cell block is about 111 km across",
which is the north-south width. East-west a four-cell span at this domain's
mid-latitude is **95.0 km**, because a degree of longitude shrinks with the
cosine of latitude. For a range comparison the narrower figure is the one that
matters, since it is the shortest separation a block guarantees.

**And the answer depends on the model, which is the finding:**

| model | half-sill range, operational | blended |
|---|---|---|
| the field itself | 103.2 km | 139.1 km |
| OLS impervious fraction | **96.1 km** | **134.5 km** |
| OLS full covariates | 22.5 km | 12.0 km |
| OLS impervious plus covariates | 19.8 km | 12.0 km |
| spatial null | 12.0 km | 12.0 km |

So the block is **ample** for every model that includes albedo, whose residuals
decorrelate inside one cell, and **marginal to too small** for the one model
that carries the central claim. On the operational field the impervious model's
residual half-sill of 96.1 km sits just above the block's narrow width of 95.0
km. On the blended field it is 134.5 km, which is 40 percent wider than the
block.

A fitted exponential range is reported too, but for four of the ten rows it is
**not identified**: the variogram does not flatten inside the 600 km fitting
window, so the fit lands on its bound and reporting `3a` would be reporting the
bound. Those rows say "not identified" rather than quoting a number, and the
half-sill range is the comparable quantity throughout.

**What follows for the paper.** The spatial-blocks design is defensible for the
covariate models and understates the optimism of the impervious model, mildly on
the operational field and clearly on the blended one. If the paper uses the
blended field — and `data/processed/README.md` records that the blended field is
the one where the land-cover result is weakest — the block should be six cells
rather than four. That is a change to a published design and it is recorded here
rather than made.

### Item 4: the decay curve, and it supports the bracketing reading

`scripts/buffered_loo_curve.py` holds out each cell in turn, excludes everything
within a radius from training, refits and predicts, at ten radii from 0 to 500
km. **The radii are chosen from item 3's measured ranges**, which is why item 3
gated item 4: they have to resolve below a cell, across the 96 to 135 km
residual ranges, and out to the distance from a held-out province's interior to
the nearest training cell. `data/processed/buffered_loo_2018.csv` holds the
result.

**Read `r2_above_constant` and not `held_out_r2`.** A constant predictor's
held-out skill also falls as the buffer grows, from −0.002 at 0 km to −0.407 at
500 km, because the training mean drifts away from the held-out cell's
neighbourhood. Every curve slopes down for that reason whether or not the model
is degrading, and the difference removes the common term. Missing this would
have read the whole exercise as land cover degrading when most of it is the
target's own structure.

**The spatial null collapses exactly where it should.** 0.685 at no buffer,
0.664 at 25 km, and **−0.015 at 50 km**. A cell is 27.8 km across, so the null
loses everything the moment the buffer exceeds one cell, and past that point it
is numerically identical to the constant — which is the designed fallback when
every neighbour is excluded, now visible rather than inferred.

**Land cover is not flat, and that was the interesting outcome rather than the
expected one.** A model that uses no spatial information should not care how far
away its training data are. Its advantage over a constant decays steadily
instead: **+0.118 at no buffer, +0.089 at 100 km, +0.063 at 150 km, +0.041 at
200 km, +0.007 at 300 km, and negative beyond.** On the blended field it reaches
zero by 200 km. So the impervious coefficient is not stable across this domain:
the small skill it has is local, and it disappears when the training data are
more than about 300 km away. That is consistent with what the repository already
records about the exceptions recurring in the same places, and it is the first
direct measurement of it.

**And the bracketing reading is supported.**
`notes/grounding-methods.md` offers the reading that this project's two
cross-validation schemes may bracket the truth, since leave-one-province-out is
maximally extrapolative, and says the decay curve is the measurement that would
show it. The spatial null's leave-one-province-out held-out R squared is
**−0.091**. Buffered, it is **−0.084 at 150 km and −0.112 at 200 km** on the
operational field, and **−0.099 at 150 km** on the blended one. **So the
leave-one-province-out figure falls between two adjacent points of the null's
own buffered curve, and the two schemes are measuring the same thing at two
points on one curve rather than disagreeing.** The spatial-blocks value of
0.332 and the leave-one-province-out value of −0.091 are both on that curve,
and neither is wrong.

*Amended on 13 September 2026, while building the decay figure.* This paragraph
originally continued: "A held-out province's interior sits roughly 150 to 200 km
from the nearest training cell", and concluded that the leave-one-province-out
figure is "what a 150 to 200 km buffer gives". **That distance was never
measured.** A scratch calculation against the fold assignment committed in
`baseline_predictions_2018.csv` -- five folds, the four provinces and Outside --
puts the median cell about 56 km from its nearest training cell, the 90th
percentile at about 146 km, roughly 4 percent of cells inside the 150-to-200 km
range and about three quarters within 100 km. The per-fold medians run from
28 km for Shanghai to 74 km for Outside.

So the bracketing conclusion stands and its stated reason does not. The
province-out value does lie between two adjacent points of the buffered curve;
it lies there at a radius two to three times the typical fold distance, which
says that **leave-one-province-out is more extrapolative than its geometry alone
accounts for.** That is not surprising on reflection -- withholding a province
withholds a region of the predictor and response distribution, not just a
neighbourhood -- but it is an open question rather than a result, and it is the
question the planned fold map would answer. None of these scratch numbers is
quoted anywhere in the repository, because no registered script produces them;
`src/figures/buffered_decay.py` shades the bracketing interval derived from the
committed table and says in its own docstring that the interval is not a claim
about fold geometry.

`figures/buffered_decay` is built from this, as of 13 September 2026. The fold
map slot is still planned and is now the most necessary of the three.

## The two figures the results section needed, 13 September 2026

The figure audit found that the two results the contribution now rests on had
no figure and that neither had ever been planned. Both are built.
`figures/README_fragments.md` carries the captions and `figures/README.md` the
inventory; what is recorded here is the four decisions that were not obvious
and the four things that went wrong in the making.

### The decay curve plots two metrics, not one

`scripts/buffered_loo_curve.py` already recorded that `r2_above_constant` is
the readable column and `held_out_r2` is not, because a constant fitted on the
training data is itself a model and its held-out skill slides from −0.002 at no
buffer to −0.407 at 500 km. Every raw curve therefore slopes down whether or
not the model is degrading.

The obvious figure plots the difference alone. That is wrong here, and the
reason is worth stating: **the fact that the baseline moves is itself one of
the three things the figure has to show.** A reader who sees only the difference
learns that land cover decays, but not that the decay had to be separated from
a sliding floor to be seen at all, and so has no way to judge whether the
separation was legitimate. A reader who sees only the raw metric would conclude
that all three models decay, which is false.

So panel (a) is the raw metric for all three models including the constant, and
exists to show the floor move. Panel (b) is the difference for the two models
with predictors, and is where the conclusions come from. A reader who looks
only at (b) is not misled; a reader who looks only at (a) would be.

**A second reason settled it.** The bracketing result compares the null's
buffered curve against its leave-one-province-out value, and a
leave-one-province-out fold reports a raw held-out R squared. There is no
above-constant number for it — the null's advantage over a constant is exactly
zero at every radius past 50 km, because past one cell the null *is* the
constant — and no radius for it to sit at. Without panel (a) the bracketing
cannot be drawn at all, which a first version of the module discovered by
putting the marker on panel (b), where the plot call was a no-op.

### The block width and the residual range are one line, not a band

The brief asked for the residual half-sill range, 96.1 km, and the block width,
95.0 km, marked on the axis. They are 1.1 km apart on a 500 km axis: about two
pixels at the committed size. A band between them renders as a line, and a band
that a reader cannot see as a band claims a visible distinction the measurement
does not support.

One line is drawn, at the 95.55 km midpoint, and the caption carries both
numbers with their resolvers. **The point the two numbers make together is that
the block is marginal against the range it would have to exceed**, and that
point survives being made in prose; a two-pixel band would not have made it
better.

### The per-cell distribution is a panel because it is the finding

The capability figure's risk is that its headline travels without its
qualifications. Two of the three are annotations — the estimate is a
reimplementation and not an inversion, and the sweep is a lower bound. The
third is not a qualification at all: **no cell reaches a sensitivity of 0.5,
and the DOFS total conceals that completely.** A total of 22 reads as
capability. It accumulates from 926 weakly constrained cells.

The artefact had no per-cell distribution, only the count above 0.5, which is
zero and says nothing about how far below. So the script now writes the median,
the 90th percentile and the maximum at both ends of the literature band, and
panel (b) draws them on a log axis against the 0.5 line. The strongest
statement this supports is much stronger than the count was: at the top of the
band the *best* cell reaches 0.065, an order of magnitude below the threshold.

The prior-free threshold went into the same figure as panel (c) rather than its
own. Panels (b) and (c) are the same statement in two units, and both are there
because they fail differently — (b) is exact and abstract, (c) is concrete and
asks the reader to accept a landfill figure from the literature. Neither alone
is as convincing as the pair.

**Drawing (c) corrected a claim in this file.** The paragraph above under *the
prior-free one* says individual large point sources in this domain sit below
`a = 0.5`, which is true of a median cell, whose threshold of 86 Gg a-1 is
above the whole 10-to-50 Gg landfill range. It is not true of the
best-observed cell, whose threshold is 49 Gg a-1 and falls *inside* that range,
so a landfill at the top of the range would just reach half-constraint in the
one cell of 926 with the most observation days. The figure draws both points
against the band, which is how the exception was noticed;
`notes/draft-results.md` §6.2 now states it.

### Reference lines carry values, not names

Three placements of the DOFS threshold names in panel (a) were clipped by the
rising curve, and the geometry says they always will be. The lowest line is
reached at 1.77 Tg, which leaves about 1.2 decades of clear axis on either side
of the crossing, and 1.2 decades holds roughly thirteen characters at caption
size. No useful name fits. Placing a name to the right of the crossing and
below the line is clear of the curve in principle and still clips it where the
curve approaches the line.

So the lines carry their values, which is three characters and cannot be
reached, and the caption names what each threshold is. **The names are
editorial gloss; the values are the data**, and the y axis already says they
are DOFS.

### Four mistakes, three of which a guard caught

**The wrong interpreter recoloured a committed figure, and no guard caught
it.** `cmcrameri` is installed in `.venv` and absent from the bare pyenv
`python3`. Running a figure script under the latter made
`style.sequential("batlowS")` fall back to viridis *silently*, and `series(3)`
returned three colours 0.004 apart in luminance against a declared floor of
0.15. The figure rewritten under that fallback was
`figures/observed_predicted.png`, restored with `git checkout`. For some
minutes the conclusion on hand was that the palette was broken.

The fallback was the whole problem: a missing dependency that changes every
colour in the repository should not be a warning-free substitution. Three tests
were added to `tests/test_figures_palette.py` — that `style._crameri` is not
`None`, that the categorical series is ordered by tone with consecutive
luminance gaps at or above `MIN_LUMINANCE_GAP`, and that every pair in the
series clears `MIN_CVD_DISTANCE` under all three simulated deficiencies. Any
one of them fails under the fallback.

**`plt.subplots` bypasses the style module.** A first version of the decay
figure used it and produced a PDF with outlined rather than embedded fonts,
because `style.figure()` is what applies `pdf.fonttype: 42`. `export()` does
report `fonts_embedded: False`, so the guard worked; the module comment now
says why the indirection exists, since the failure is invisible on screen.

**Registering a recipe changes a committed figure.**
`src/figures/framework_pipeline.py` reads `config/recipes.yml` and prints the
recipe counts in its own note text, so the four new recipe entries changed that
diagram's bytes. `tests/test_recipes.py` caught it as a byte mismatch on
`framework_pipeline.png` and `.pdf`, and `figures/README.md` now records the
dependency beside that figure. The recipe table in the repository README needed
`verify_recipes.py --update-readme` for the same reason, and the three prose
files quoting the recipe counts were caught by the claim checker.

**The shaded band in the decay figure meant the wrong thing**, which is
recorded in full under item 4 above. It was shaded as the distance from a
held-out province's interior to the nearest training cell, a figure this file
asserted and no script ever measured. It is now derived from the committed
table by `buffered_decay._bracket()` and a test asserts the derivation.

## Verifying the dataset inventory, 13 September 2026

`notes/dataset-leads.md` was built across five grounding passes from search
results and reading. This is the first time any of it was opened. Every entry
whose status was *unverified* or *documented only* was attempted from this
machine, under a 5 GB download budget of which about 48 MB was used, and
everything fetched was deleted except the one committed artefact.

The file itself carries the per-entry results. What belongs here is the pattern,
because the pattern is the reusable finding and it is not the one an inventory
built from reading would predict.

### Twenty-seven entries attempted: the tally

**Nine moved to verified accessible**, all of them open and anonymous: MMCP, the
CCD-Rice validation polygons re-verified in depth, the CCD-Rice maps
re-verified, ChinaRiceCalendar, the 500 m irrigated cropland maps, China's oil
and gas CH4 inventory, the underground wastewater plants, the 30 m annual
building heights, and CMAB. Two more were re-confirmed where they already stood,
Landsat Collection 2 and the IMI input buckets.

**Six were established as genuinely unreachable, with the obstacle named rather
than assumed.** China_AP, the MSW landfill database, the Shaoxing UAV record and
the gridded coal inventory are behind paywalls that block the article naming the
route. WetCHARTs returns 401 to an anonymous data request, confirming its
Earthdata requirement. The Lin'an WDCGG route was attempted and not found: the
host is reachable and its station listing is JavaScript-driven, so a scripted
fetch needs an API that could not be discovered from outside.

**Four regressed**, all on one cause: zenodo.org is unreachable from this
network, a TCP timeout on every endpoint with DNS resolving normally. That
blocks GISA-new, APRA500, the CCD-Rice code and the GHGSat plume set. Two of the
four had been recorded *verified accessible* on the strength of a request that
succeeded when it was made.

### What the pattern says

**The routes were better than recorded and the licences more permissive.** That
is the opposite of the usual direction of error and it has one cause: the
inventory was built by reading landing pages and abstracts, and a landing page
is the worst available description of a deposit. Five deposits exist for entries
that recorded none, and **all five were named in the papers' own data
availability or Data Records sections.** Four of those five entries were marked
*documented only*, which in this file has meant "a source describes the route" —
but the source had described the route and nobody had read that paragraph.

This is the CCD-Rice polygon lesson a second time. That entry records it
already: "a product's reference data and its product data need not live on the
same platform, and checking one is not checking the other". The generalisation
is simpler and should replace it: **read the article's data availability
statement.** It is one paragraph, it is in the open-access HTML, and it is where
the answer is.

**Eight licences were verified as CC BY 4.0 or CC0 where the file held
"unknown", "article licence" or "not established".** One moved the restrictive
way: the rice-mapping review is CC-BY-NC-ND, not CC-BY. And **two entries
deposit under a different licence than their article carries** — the underground
wastewater plants and CMAB are both CC-BY-NC-ND as articles and CC BY 4.0 as
data. Recording the article licence as the dataset's would have imposed a
non-commercial no-derivatives constraint that does not exist. The inventory now
states the distinction.

**Both factual errors found were in the inventory, not in the products**, which
is worth saying plainly because it is the same class as the CCD-Rice count error
that motivated this pass, and that error had already been corrected in the file
before this pass began. MMCP's licence was recorded as CC-BY-NC-ND 4.0 and
described as constraining reuse "more than anything else in this inventory"; the
deposit is CC BY 4.0, the least restrictive licence in the file. The IMI
boundary archive was recorded as beginning "one day before this project's first
granule"; it begins 1 April 2018 against a first granule of 30 April 2018, so
29 days. Every other count, size, date and coverage figure checked against a
file held — including all four CCD-Rice province counts, the 5.37 GB and 27-file
CCD-Rice total, and the 201-and-2,464 wastewater premise the file had itself
flagged as unverified.

**One recorded obstacle was not real.** `data/processed/README.md` said GISA's
per-tile links go through Zenodo and that "the whole 882 MB bundle is the only
reachable route". The same Wuhan University server that serves the bundle serves
all 257 tiles individually from a browsable index at about 8.7 MB each. The four
this study needed are about 35 MB, so the bundle was 25 times more transfer than
the work required. That record is corrected.

### CCD-Rice was trained on the rice layer this project carries

This is the finding with consequences beyond the inventory, and it came from
reading the CCD-Rice paper rather than from any status.

`notes/paper-target.md` item 9 carries a gating condition: the CCD-Rice polygons
are "clean for the NESDC and GISA layers and contaminated for CCD-Rice itself,
whose thresholds were re-determined against filtered rice areas". **The first
half holds and the second half is wrong about which mechanism contaminates
what.**

The polygons did not calibrate CCD-Rice. Its §2.3.3 re-determines the
rice-probability threshold from *filtered agricultural statistical areas*, and
its §2.3.4 uses the polygons only to validate. So the polygons are clean for
CCD-Rice too, on the separation condition as stated.

**What is not independent is CCD-Rice and NESDC.** Its §2.2.2 states that "the
training samples used in this study were extracted from two rice distribution
maps for recent years: the distribution map of single-season rice in China from
2017 to 2022 produced by Shen et al. (2023a, b)" and a double-season map from
Pan et al. That first product is `10.57760/sciencedb.06963`, which
`notes/references.md` records as "the source of the analysis grid's rice
fractions". **CCD-Rice's labels came from this project's own rice layer.**

The years do not overlap — CCD-Rice ends in 2016 and NESDC begins in 2017 — so
the two are never compared in the same year, and the 2000 and 2010 maps this
project would use are a model trained on 2017-to-2022 NESDC labels and
transferred backwards. The dependence is therefore not a double-counting in one
year; it is that the historical layer inherits the label characteristics of the
layer it would be checked against.

**The consequence is for the pairing rule, not for the accuracy assessment.**
`notes/dataset-leads.md` describes CCD-Rice as "the second rice product for the
historical years, the role GISA plays for impervious surface". GISA and GAIA
were produced independently; CCD-Rice and NESDC were not. So a CCD-Rice-against-
NESDC disagreement understates disagreement, and an error variance taken from it
understates the error variance — which is exactly the input queue item 11 wants
from queue item 10's analogue for rice. The GAIA–GISA rule this file applies
repeatedly is "two products with different errors beat one better product", and
the errors here are not different enough to assume.

### The status vocabulary gained a fifth term

**Open, terms-gated**, for MUSICA. Its landing page returns 200 and its rights
statement reads CC BY 4.0, but the download is a JavaScript control carrying
`data-terms-accepted` whose backend returns 401 without a browser session.
Nothing is closed and no account exists to create. A reader of "open,
registered" would go looking for a login there is none of, and a reader of
"verified accessible" would expect a fetcher to work.

MUSICA also turned out to be a smaller thing than recorded: the 181.7 MB deposit
holds **two example netCDF days and a ReadMe describing how to obtain the
complete 1,241-file set**, not the series. Its licence being CC BY 4.0 rather
than "not established" is the good news; that the deposit is a sample is the
bad.

## The accuracy assessment route, and the Zenodo block behind it, 13 September 2026

Tier 1 left the accuracy assessment blocked: the CCD-Rice polygons are a
purposive sample with no inclusion probabilities, which forecloses the
design-based inference the route depended on. This pass settled what is
possible instead, and diagnosed the network obstacle sitting in front of six
candidate reference sets.

### The Zenodo block is an application-layer refusal, and the Tier 1 diagnosis was wrong

Tier 1 recorded "zenodo.org times out at the TCP level over IPv4 with DNS
resolving normally, on every endpoint". Only the DNS half survives. DNS returns
six A and six AAAA records; **TCP connects to every one of them in under a
second**; **TLS completes**, negotiating TLSv1.3 with a valid `CN=*.zenodo.org`
certificate over IPv6; and then nginx returns **403 Forbidden in under half a
second** on every path including the REST API and OAI-PMH.

The 403 body names the cause: *"Access to this resource has been restricted due
to unusual traffic from your network"*, with a reference id and a timestamp. So
it is a deliberate Zenodo-side restriction keyed to this egress network, and the
remedy is an email quoting the reference rather than anything technical.

**The reusable lesson is about how the wrong diagnosis happened.** The filter
drops a default-`curl` User-Agent silently *after* the TLS handshake, so the
connection hangs and the client reports a timeout; a browser User-Agent gets the
403 in 0.47 seconds. Tier 1 used the default UA. **A hang after a successful
connection is an application-layer refusal until proven otherwise, and the
User-Agent is the first variable to try.** `notes/dataset-leads.md` carries the
full layer-by-layer measurement, the class test that shows
`sandbox.zenodo.org`, `cern.ch` and `home.cern` all respond normally, and the
seven entries it blocks as distinct from the entries blocked by paywalls,
publisher 403s, an Earthdata login and a terms click.

### A finer-resolution product is not automatically a better reference

This is the finding most likely to be assumed away by a later pass, so it is
stated as a rule. **Reference quality is accuracy against the thing being
measured, not pixel size.** SinoLC-1 is the counter-example and the numbers are
verified from its ESSD paper: 1 m resolution, **overall accuracy 73.61 percent
and kappa 0.6595** on 106,344 counted validation points. That is below
GLC_FCS30's 82.5 percent at 30 m and below NLCD 2019's 77.5 percent. A 1 m
product with 73.61 percent overall accuracy cannot serve as reference data
"more accurate than the map" for the 30 m products it would validate, which is
Olofsson's second recommendation, and using it would import more error than it
measured.

### No deposited sample set satisfies the recommendations over this domain

Three were verified. **LCMAP** (`10.5066/P9ZWOXJ7`, USGS ScienceBase, anonymous,
use constraints "None.") is the only probability sample among them and is
US-only; 25,000 plots, 874,836 annual rows, 1984 to 2018 read from its FGDC
metadata, class labels and no fractions. **The global land cover validation
samples** were fetched during an open window in the Zenodo filter and hold
**44,514 points for 24 classes, against the 44,043 the GLC_FCS30 paper reports**
— a 471-point difference neither source explains. Their *allocation* is a
textbook stratified design, the Cochran formula with `W_i` the global per-class
area proportion, but their *frame* is eight donor reference datasets with points
"randomly collected from each polygon", so the first-stage inclusion probability
is unknown. The shapefile carries three fields — label, longitude, latitude — so
the per-sample source code its own description document describes is absent and
provenance cannot be recovered. They are points, so class labels and not
fractions.

**And the four-province count is the number that ends the discussion: 124.**
Jiangsu 112, Zhejiang 7, Anhui 4, Shanghai 1, reaching 20 of 926 cells, of
which **107 are irrigated cropland and 12 are impervious surface**. Twelve
points cannot assess an impervious fraction over this domain, and this is the
best deposited candidate there is. **Globe230k** fails on density: 232,819 tiles of 512 × 512 at 1 m
is 61,032 km², 0.041 percent of global land, and against a 625 km² cell one tile
is 0.042 percent of a cell, so tiling one cell needs 2,384 tiles and the four
provinces would receive about **0.59 tiles per cell**. Dense annotation gives a
fraction within a tile footprint, which is a sample of the cell rather than the
cell's value, and so returns to the sampling problem it was supposed to solve.

### The route was already in the record and was not recognised

`notes/grounding-methods.md` had established, before this pass, that the correct
frame for a fractional layer is the continuous-field protocol of Riemann et al.
(2010) as used by the NLCD percent-impervious assessment, and that the NLCD work
used **complete-coverage reference data**: "we do not estimate agreement from a
sample, but rather calculate agreement directly from the full coverage data".

**A complete-coverage comparison has no sampling design to be valid about**, so
Olofsson's first recommendation does not apply to it — for the same reason, and
with the same force, as the record's existing finding that his fourth and fifth
do not apply to a fractional layer. That reframes the problem from "obtain a
probability sample", which is foreclosed, to "obtain a reference layer over the
domain more accurate than the product", which is not foreclosed but is currently
blocked.

**The two routes fail differently and that is the useful part.** Route A, the
certainty-stratum framework, keeps the purposive polygons as a fully observed
stratum over the 62 cells they reach and draws a probability sample from the
other 864; it is blocked on the very-high-resolution imagery terms question this
repository already lists as unresolved, and it carries a response-design burden
larger than the categorical literature's because a fraction per cell needs many
points or a delineation rather than one label. Route B, a finer reference
product, is blocked on **year**: SinoLC-1 is 2021, CISC is 2020 and 2022,
EcoVision is 2025, the 1 m Yangtze River Economic Belt product is 2026, and this
project's layers are 2000, 2010 and 2018. In a region that urbanised as fast as
this one over exactly that span, a 2021 reference against a 2018 map confounds
map error with real change, and `figures/urban_change.png` exists because that
change is large.

Route B would become viable if the project added a 2020-or-later analysis year.
That is a change to the paper rather than to the code, and it is the cheapest
path to an assessment that this pass found.

### The interpreter problem is smaller than the record held it

Three verifications moved it from an open limitation to a variance component.
Pengra et al. (2020) report **88 percent overall interpreter agreement, 46
percent for Disturbed to 94 percent for Water** — and, more usefully, they
computed it on a **simple random subsample of 2,952** of their 11,900
interpreted pixels, excluding purposively chosen duplicates, "thus ensuring that
these estimates were produced from a probability sample". That separation is
exactly the discipline this project's reference data lack and exactly the model
for reporting an agreement figure honestly. Powell et al. (2004) give the
pessimistic end, five interpreters disagreeing on almost 30 percent of samples.
And Stehman et al. (doi:10.1016/j.rse.2021.112806) publish a method for
incorporating interpreter variability into the total variance, so the
disagreement is propagatable rather than disqualifying.

**And the field admits it usually ignores this.** Reference data are typically
assumed error-free and the process of obtaining them is seldom discussed (Sun,
Chen and Zhou, 2017; Foody, 2010). **So stating this project's reference error
explicitly puts it ahead of the norm rather than behind it.** An assessment that
says "the reference is a purposive sample of 777 polygons reaching 62 of 926
cells, interpreted once, and here is what that does to the interval" is more
honest than most published assessments, which say nothing.

## Route B is closed, and the reason is accuracy rather than year, 13 September 2026

The previous pass recorded that Route B — using a finer-resolution product as
the reference layer for a continuous-field assessment — was "blocked on year",
because every candidate was 2020 or later against layers for 2000, 2010 and
2018, and that the cheapest fix was a scope change to a second analysis year.
**This pass opened the products and that conclusion was wrong about which
constraint binds.**

### None of the four candidates is more accurate than the products it would validate

The bar is GISA's impervious F-score of **0.954** and GISA-new's **93.12
percent** overall accuracy. Measured against it:

| Candidate | Resolution | Accuracy | Verdict |
|---|---|---|---|
| SinoLC-1 | 1.07 m | 73.61 % overall, kappa 0.6595 | fails, widely |
| EcoVision | ~0.5 m | 83.6 % overall, urban areas only | fails |
| ISA-1 | 1 m | impervious F1 **75.53**, recall **61.76** | fails |
| CISC2020/2022 | 30 m | impervious F1 > 0.93 | not clearly better, and not finer |

**Three of the four are between two and sixty times finer than the products they
would assess and every one of them is less accurate.** So a year-matched
candidate would still fail Olofsson's second recommendation, and **the year gap
is real but second in line**. Route B is closed on accuracy.

`notes/dataset-leads.md` records where the four accuracy figures are not
comparable, which is most of them: a multi-class overall accuracy is not a
single-class impervious F-score, and the validation populations run from global
to 42 urban cores. The two that *are* comparable to GISA are ISA-1 and CISC,
and the finer of those two is the one that loses.

**One number in that table is a trap worth keeping.** ISA-1's abstract reports
85.71 percent, which is the mean over its two classes; the impervious class
alone is F1 75.53 with **recall 61.76**, so it misses about two impervious
pixels in five while the easy non-impervious majority class carries the mean to
85.71. Quoting the headline would have overstated the best in-domain candidate
by ten points.

### A finer product is still not a better reference, now on four cases instead of one

The previous pass recorded this rule from SinoLC-1 alone. It now has four
instances and one of them is instructive in a new way: **ISA-1 is
super-resolved from the same 10 m Sentinel-2 imagery that a Route A response
design would interpret directly.** A 1 m product generated from 10 m inputs
cannot carry more information than the 10 m inputs; it redistributes it. That is
visible in its own numbers, and its paper says as much about a competitor in
this project's own cities: 10 m ESA WorldCover "demonstrates relatively higher
accuracy and provides more refined ISA delineation in developed urban areas such
as Nanjing, Suzhou, and Nantong". **Resolution is not information.**

### Distribution is a second, independent obstacle

Of the four, only ISA-1's deposit could be opened at all. It holds one file,
`ISA-1-Some-examples.rar`, and the name is accurate: **seven prefecture-city
rasters, not the 2.2-million-square-kilometre product** its paper says "will be
publicly available". Two of the seven are in domain, Nanjing and Shanghai, and
they fully contain **20 of the 926 analysis cells**. EcoVision has no
established route and is absent even from its own authors' distribution server.
SinoLC-1 and CISC sit behind a Zenodo service that refused this network for the
whole pass.

**And `10.5281/zenodo.7707461`, the DOI SinoLC-1's own data availability
statement gives, is the user-guide record rather than the data.** The data are in
sibling version records, as provincial zips of city tiles. A data availability
statement pointing at the wrong record of its own deposit is a new failure mode
for this repository's register and worth remembering.

### What the ISA-1 examples did establish, which is a real if narrow gain

Verified from the rasters rather than the paper: 1 m exactly, EPSG:4326, uint8,
one band, **binary 0 non-ISA and 1 ISA**. That makes it the only candidate whose
encoding maps directly onto this project's target, because averaging a binary
1 m ISA raster over a lattice cell *is* an impervious fraction — no class
crosswalk, no fractional interpretation. **Nodata is undeclared and 0 means both
non-impervious and outside the city**, which is the same trap CISC states for
itself and the same class as the GAIA and GISA year directions and the NESDC
silent zeros.

So a 20-cell pilot comparison against the committed GISA and GAIA fractions is
cheap and available. **It was deliberately not run in this pass**, because 20
cells is 2.2 percent of the lattice and a number computed on it would be quoted
as an assessment.

### The imagery licence question is answered and it closes the fine-resolution half of Route A

Carried as open since the region grounding. `notes/grounding-methods.md` now
holds the terms as quoted. The short form:

**Google's Geo Guidelines contain both a permission and a prohibition and do not
say which governs.** Research use is allowed "without needing permission"; using
Google Earth output "to create other content, products, or services" is
prohibited. A visually interpreted reference dataset is both. Street View, by
contrast, prohibits "digitizing or tracing information from the imagery" in
those words — so Google writes the prohibition explicitly where it means it, and
that sentence does not appear for the satellite basemap.

**Earth Engine's terms are clear and permissive and do not cover the imagery in
question.** §2.1(d) permits publishing "data, diagrams, charts, figures created
by use of the Services in research or educational publications"; §4.1 gives the
user ownership of Customer Data. But Earth Engine's catalogue is Landsat,
Sentinel and similar — **it does not include the Google Earth
very-high-resolution basemap** that CCD-Rice, SinoLC-1, Globe230k and the global
land-cover evaluations all interpreted.

**Sentinel-2 is the finest imagery whose terms unambiguously permit the whole
chain.** The Copernicus Sentinel Data Legal Notice, under Regulation (EU) No
377/2014 and Commission Delegated Regulation (EU) No 1159/2013, grants
reproduction, distribution, communication to the public and adaptation, subject
only to the notice "Contains modified Copernicus Sentinel data [Year]".

**So Route A is licensable at 10 m and not clearly licensable at 1 m.** Against
30 m products that is a ratio of three, where the NLCD assessment this project
takes as its model used 1 m against 30 m, a ratio of thirty. **A factor of three
is thin**, and the open question has changed character: it is no longer whether
reference data can be obtained or licensed, but whether a 10 m interpretation
can support a credible fractional reference for a 30 m product.

**The field's position, recorded without resolving it.** Every product examined
here interpreted Google Earth imagery and none of the papers cites a licence for
doing so. Either the research-use sentence is what everyone relies on, or the
practice is unexamined. This repository cannot resolve what Google has left
open, and the useful consequence is a design choice rather than a legal opinion:
a Sentinel-2 response design needs no such resolution.

### Why recording a closed route is the point

Route B took eight literature rounds and two verification passes, and it ends in
a table of four numbers none of which clears 0.954. That is worth the same
prominence as an open route. The specific saving is a scope change that was
being seriously considered — a second analysis year, costing another 28.9 GB
transfer and two hours of compositing, plus every figure and baseline artefact
regenerated — **on the strength of an assumption about products nobody had
opened.** The measurements cost one afternoon and one 1.16 GB download.

The second-year question survives for two reasons that have nothing to do with
the assessment, and `notes/paper-target.md` now records them there: it answers
the single-year reviewer objection, and it would let the capability estimate be
computed for two years. It also carries a cost this pass quantified: **the rice
layer would be weaker in a 2021 year than in 2018**, because NESDC's totals are
pinned for Shanghai from 2019 and for Jiangsu from 2020, so a 2021 year would
have both provinces pinned where 2018 has neither.

## The accuracy assessment is blocked, and the sampling question never arose

13 September 2026. This settles the status of an item that has been open since
the methods grounding and records a research failure alongside it.

### The finding, which is about the region rather than about this project

**No reference layer exists over the Yangtze River Delta that is both more
accurate than the 30 m products this project uses and available for a year this
project analyses.** `notes/grounding-methods.md` records the four candidates
individually, with the reason each fails, because a later pass will otherwise
reopen them one at a time. The short form: against GISA's impervious F-score of
0.954, SinoLC-1 is 73.61 percent overall, ISA-1's impervious class is F1 75.53
with recall 61.76, EcoVision is 83.6 percent and urban-only, and CISC is 30 m
and therefore a fourth product rather than a reference.

The distinction between "the products over this region cannot support it" and
"this project did not do it" is not cosmetic. It decides whether the paper
reports an absence in its methods section as a property of the available data,
or in a limitations paragraph as a debt. **It goes in methods**, on the same
reasoning that put the preprocessing omissions there, and
`notes/draft-methods.md` §7 now states it with the four candidates and their
numbers.

### The research failure, which is the more useful half

**Eight literature rounds went to the sampling-design question and it was the
wrong question.** Probability samples, stratified prediction-powered inference,
its design-based extension, the certainty-stratum framework, and three deposited
sample sets: all of it addressed to Olofsson's first recommendation, a
probability sampling design.

**That recommendation does not apply to the protocol this project had already
adopted.** The continuous-field frame for a fractional layer — Riemann et al.
(2010), as used by the NLCD percent-impervious assessment — compares a product
against **complete-coverage** reference data, and says so in its own words: "we
do not estimate agreement from a sample, but rather calculate agreement directly
from the full coverage data". A complete-coverage comparison has no sampling
design to be valid about. This record had already made exactly that argument for
Olofsson's fourth and fifth recommendations, which concern error matrices and
do not apply to fractional cover. **The same argument covers the first and
nobody extended it.**

So the problem was never *obtain a probability sample*. It was *obtain a
reference layer more accurate than the product* — a different problem, a harder
one, and the one with no solution here. **The sampling literature was answering
a question this project had already ruled out of scope for itself**, and the
scope was stated in the same section of this repository that established the
protocol.

**The rule worth keeping, because it is transferable and cheap:** when a
protocol is adopted, read what it does about sampling before searching for
samples. A protocol that assesses complete coverage and a protocol that assesses
a sample ask for different things, and the difference is in the first paragraph
of each. The cost of not reading it was eight rounds.

`ERRATA.md` 6.5 is corrected a second time for the same reason. It said the
reproduction owes Olofsson's first three recommendations; it owes the second and
third.

### What the project can say instead, and what it cannot

**Product-against-product disagreement**, which this project already reports as
a single percentage of provincial area and which the Pontius and Millones
decomposition splits into a quantity component and an allocation component. That
is queue item 10, it needs only the two committed products, and it is now the
live item where the assessment was.

**What it cannot say is either product's error.** Two layers can agree closely
and both be wrong the same way. So there is no absolute accuracy for either
layer and therefore no reliability ratio in the errors-in-variables sense.

### The consequence for de-attenuation, which is a reduction and not a block

Queue item 11 was gated on items 9 and 10. **Item 9 is blocked and item 11 is
not**, because item 11's impervious input was always item 10's allocation
disagreement rather than a reference assessment. What changes is what that input
can be:

* Allocation disagreement is a **lower bound** on the pair's joint error
  variance — where GAIA and GISA differ at least one is wrong; where they agree
  nothing is constrained.
* A lower bound on error variance gives an **upper bound on attenuation**.
* So item 11 produces a **bound on the de-attenuated coefficient, not a point
  estimate** — and that bound is the thing actually needed, because the question
  is whether measurement error *could* manufacture the null. **If the upper
  bound on attenuation does not reach the observed coefficient, the null
  survives the objection.**

The rice half is unaffected: the assessment is blocked for want of a reference
*layer*, and the CCD-Rice polygons are reference *points*, still usable over the
62 cells they reach, with the purposive-sample caveat that they carry no
inclusion probabilities and so support an estimate without a design-based
interval.

**So item 11 is reduced from estimation to bounding and its gate is item 10
alone.** `notes/draft-results.md` §3.4 now says what follows for the negative
result: measurement error has not been excluded, the bound that would exclude it
is queued and not computed, and the second predictors built here are evidence
against it rather than a measurement of it.

### What would reopen this, recorded as files rather than hopes

ISA-1's claimed biennial 2017 and 2019 maps, none deposited, which would fix the
year and not the accuracy. EcoVision's full text, unread behind a publisher 403
and absent from its own authors' server, whose impervious-class F-score could
exceed 0.954 even at 83.6 percent overall because built-up is among the easiest
classes. And **CISC's expert-interpreted validation points**, produced on a
stated entropy-guided stratified design, which would be reference data even
though its product is not, and whose existence as a file is unestablished
because Zenodo refused this network throughout the verification pass. **That
third is the most valuable unresolved item**, because expert-interpreted points
on a stated design over China is what every other candidate lacks.

## The null survives the measurement-error objection, 13 September 2026

Queue items 10 and 11. This is the critical path to the strongest statement the
project can make about its central result, because measurement error in a
predictor attenuates its coefficient toward zero and so is the one confound that
could manufacture a null rather than explain one.

**The answer: measurement error in the impervious layer is excluded, with a
margin of 5.6.** For the de-attenuated land-cover coefficient to reach the
spatial null's performance, 74.5 percent of the variance in the impervious
fraction would have to be error, against the 13.2 percent the two products'
disagreement supports.

### The direction of the bound was wrong in this record and computing it exposed that

This repository recorded the chain as: allocation disagreement bounds the pair's
error variance from *below*, so the reliability ratio is bounded from above, so
the de-attenuated coefficient is bounded from above. **The last step does not
follow from the second.** With `beta_true = beta_obs / lambda`, bounding
`lambda` from above bounds `beta_true` from **below**, which answers nothing:
the question is whether measurement error *could* have manufactured the null,
and that needs the largest true coefficient the data permit, not the smallest.

The usable bound comes from a different reading of the second product. GISA as a
second **reference** gives a lower bound on error — the locations where the two
differ are locations where at least one is wrong. GISA as a second
**measurement** gives an upper bound: `Var(D) = Var(e_1) + Var(e_2) >= Var(e_1)`
when the two errors are independent of each other, so `Var(e_GAIA) <= Var(D)`
and `lambda >= 1 - Var(D)/Var(X)`. **The same artefact, read two ways, bounds
the quantity in opposite directions, and only one of them answers the
question.**

Had the error stood, the paper would have carried a limitation it does not have:
that measurement error could not be excluded. It is excluded.

### The decomposition, and what it says about the crossover

`data/processed/urban_disagreement_2018.csv`. **The method needed a decision
first**, because Pontius and Millones (2011) — in this register already, for the
kappa correction — defines quantity and allocation disagreement on a
cross-tabulation built with a Boolean operator over hard-classified pixels, and
these layers are fractional. Its soft-classified companion, **Pontius and Cheuk
(2006)**, is the correct citation and is closed access, so its Composite
operator could not be read. What is computed is the two-class fractional
specialisation, exact and needing no cross-tabulation: `D = Q + A` with
`Q = |sum w·a − sum w·b|` and `A = D − Q`, both non-negative.

**Unit of analysis: both, and the reason is the soft method's own point.** The
committed 868 m percent grid describes the products; the 0.25 degree lattice
describes what survives into the regression, because misallocation within a cell
cancels when the cell mean is taken. **The native 30 m comparison the method was
designed for is not available** — only windows are committed and the full
products are a 1-to-2 GB refetch — which is a limit on this decomposition worth
stating.

Allocation is 69.2 percent of the disagreement in 2000 and 82.2 in 2010 at
868 m, falling to 41.6 in 2018; at the lattice it is 44.8, 53.3 and 50.8
percent. **So allocation is roughly half the disagreement at the scale that
matters, in every year.**

And it re-reads a finding this repository already had. GISA is 20.7 percent
larger than GAIA in 2000 and 19.9 percent smaller in 2018, both verified against
`urban_extent_totals.csv` to the decimal. **The crossover is a shift in the
quantity component** — 3,421 km² in 2000 rising to 9,828 in 2018 — **sitting on
top of a persistent disagreement about location** that stays between 7,000 and
10,000 km² throughout. The products do not agree about extent in any year; what
changes across the record is how much they disagree about the total.

### What complicates the bound, and by how much

`notes/paper-target.md` asked whether allocation disagreement correlates with
anything already measured, and singled out albedo, because error correlated with
the confound is not handled by the standard correction. It does, and the
complication is smaller than the margin.

* **The disagreement scales with the predictor.** `|D|` correlates with the GAIA
  fraction at Pearson +0.730 and Spearman +0.856, and the standard deviation of
  `D` rises from 0.0021 in the lowest quartile of the fraction to 0.0650 in the
  highest — **a factor of 31.** The error is strongly heteroscedastic, which
  classical regression calibration assumes away and which is why
  `notes/grounding-methods.md` records SIMEX-WLS as the variant handling
  non-constant variance.
* **Albedo is implicated but mostly through the fraction.** `|D|` correlates
  with SWIR albedo at +0.430 Pearson and +0.717 Spearman, but the **partial
  correlation controlling for the impervious fraction is +0.139.** So the
  measurement error is not independent of the albedo confound, weakly.
* **The error is mildly differential.** The partial correlation of the signed
  `D` with methane, given the fraction, is **−0.118**. Classical error assumes
  zero. This is the assumption whose violation would most directly bias a
  correction.
* **Two of the checks that were asked for cannot be made.** Buffering
  instability is a domain-level diagnostic in this repository, not a per-cell
  quantity — `buffered_loo_2018.csv` is indexed by radius — so there is no
  per-cell instability to correlate against. And there are no coalfield cells to
  test: the gridded coal inventory was never obtained, being paywalled with two
  refused open routes.

**All three violations push toward more attenuation than the bound allows**, so
the bound is reported with a sensitivity sweep over error variances up to six
times the observed disagreement rather than as a single number. **None of the
violations is of the size the margin requires.** A factor of 31 in
heteroscedasticity and a partial correlation of −0.118 do not produce a
five-and-a-half-fold understatement of total error variance, and the sweep shows
the bound failing to reach the null at every multiple up to five.

### What is not bounded

**The rice half, structurally rather than pending.** A bound of this form needs a
second product whose errors are independent of the first, and there is none:
CCD-Rice, the only candidate, took its training samples from the same NESDC map
this project uses, which the Tier 1 pass established. What exists is 777 visually
interpreted polygons reaching 62 of the 926 cells, which could support a local
error estimate without a design-based interval and cannot support a domain-wide
bound. **The paper says so rather than implying symmetry between the two
predictors.**

### A figure would carry this better than a table, and is not built here

The sensitivity sweep is the part a reader needs and a table hides: the useful
image is the de-attenuated coefficient against the assumed error variance, with
the observed disagreement marked, the spatial null as a horizontal reference and
the crossing at 5.6 times visible as a distance rather than a number. That is
the same shape as the capability figure's panel (a) and would make a third
figure in that family. `figures/README.md` records the set; this is a candidate
for it and was deliberately not built in this pass.

## What drafting the discussion exposed, 14 September 2026

`notes/draft-discussion.md` is written. Drafting has twice before surfaced things
recording missed, and it did again. This is that list, and it is the task's most
useful output.

### Decisions the records left open, which continuous prose forced

**Where the mechanism argument sits relative to the capability argument.** Both
explain the null and the records keep them in separate files, so nothing had ever
decided which comes first. Prose cannot defer it. **Mechanism first**: it explains
the particular result, while the capability limits explain why no refinement of
the same design would change it, and the second is only interesting once the
first is established. Putting capability first would make the paper read as an
instrument study that happens to contain a null, which is not the contribution
statement `notes/paper-target.md` settled on.

**Whether the seven mechanism instances are one argument or two.** The records
list them together, and writing them out showed that two of the seven —
aquaculture at 197 to one and rice straw at five to one — are *within-class*
ratios: the same pond, the same paddy, the same area, a different practice. The
other five compare across classes. **Only the within-class pair establishes that
better mapping cannot help**, which is the claim the discussion actually needs,
so the draft states the pattern once and then separates the two that carry it.
The records had the instances and not that distinction.

**Whether §3's absent sources are part of the mechanism argument or a separate
one.** They are separate and the brief was right to insist on it: §2 says a
perfectly measured extent predictor would still fail, §3 says part of the field
was never being predicted. Merging them would have produced a single vaguer
claim. Nothing in the records had drawn that line.

**How to state the relation to the tower inversion.** `notes/grounding-yrd.md`
says the reproduction's null "is not that rice does not matter" and that the two
findings are compatible, but does not say what the paper should therefore claim.
The draft states it as a boundary between two designs — the signal a tower
inversion recovers is not recoverable from an annual column composite regressed
on static extent — which is a positive statement rather than a disclaimer.

### What could not be stated because it was never established

**The fitted seasonal peak has no artefact.** Day of year 245.8 appears in
`notes/decisions.md` and `notes/grounding-rice.md` as prose and in no committed
table. It is load-bearing in the discussion's §7, because it is what makes
EDGAR's uniform June peak "roughly ten weeks early here", and it is the one
number in the section that could not be given a resolver.
`deseasonalisation_2018.csv` holds the correlation table and not the fitted
cycle's parameters. **Queued.**

**Two corrections to `notes/paper-target.md`, both found by going to it for
material.** Its reviewer-objection section still said the record holds that
"Olofsson's first three recommendations apply and are unmet, and that no
distributed reference data exists for the impervious products". Both halves were
superseded on 13 September and that file was not updated with the record it
cites: the reproduction owes recommendations **2 and 3**, and reference products
do exist while being less accurate than what they would assess. **A cross-file
citation went stale because the correction was applied to the cited record and
not to the citing one.** Corrected in place with what it said.

And its coal instance gave in-place gas content as "8 to 30 m³ per tonne across
one coalfield", which compresses two mining areas' separate ranges — 8 to 16 in
Huaibei and 10 to 30 in Huainan — into one span as though it were a single
measurement. `notes/grounding-yrd.md` has them separately. Corrected.

### Grounding findings that did not earn a place, and why that is informative

Six passes produced more than a discussion can carry. What fell out says which
findings were load-bearing and which were interesting.

* **The whole MSW composition dispute** — 52 against 85 percent incineration,
  kitchen waste at 52.8 to 65.3 percent of waste — which the urban record itself
  could not verify to primary sources. The *qualitative* shift from landfill to
  incineration is verified and is what the discussion uses; the shares are not
  and are not written.
* **The 84.7 percent reduction in Chinese municipal waste methane since 2017**,
  with megacities carrying 80 percent of the gain. Verified and striking, and it
  concerns a trend after this analysis year, so it bears on a second-year design
  rather than on interpreting 2018.
* **Building height and building function as the missing vertical dimension.**
  The urban record's own conclusion is that a fractional layer lacks volume, and
  two products now exist. But nothing here measured it, so it is a route rather
  than a finding, and §7 has three routes with measured precedents already.
* **The Shanghai Tower and Shaoxing UAV in-domain observations.** Both inside
  the lattice, both outside the analysis year, and the first measures carbon
  dioxide rather than methane. Recorded in the inventory, not in the argument.
* **The pipeline length series** — threefold growth from 298.6 to 935.6 million
  metres over 2010 to 2019 — which supports the gas-distribution mechanism but
  adds nothing the age-and-material claim does not already carry.
* **The Lin'an background station running 81 ppb above the national global
  station.** It establishes that the domain is high-signal, which §1 needs in one
  clause and which the results section already states.
* **The coincidence that rice's sectoral total and the water-regime ratio are
  both 13.7.** The region record flags it as a coincidence. Writing either number
  beside the other would invite a reader to connect them, so the draft uses the
  ratio and not the total.

**The pattern in what fell out:** unverifiable shares, findings outside the
analysis year, and routes without measured precedents. Every one of the seven
mechanism instances earned its place, which is the clearest signal that the
mechanism sections were the load-bearing part of six grounding passes.

### What the section cannot state because the work was not done

Three items, distinct from things not decided, and all three are queued already
or added here.

* **The paddy–pond overlap is not measured**, so §3 says aquaculture is
  interleaved with paddy at the scale of the analysis cell and cannot say by how
  much. Queue item 10a, blocked on a publisher refusing the article that names
  the route.
* **Equivalence bounds are not set**, so §1 cannot say the association is absent
  and says a failed detection instead. Already queued.
* **The rice half of the attenuation question is unbounded** for want of an
  independent second rice product, so §4 is asymmetric between the two
  predictors. Structural rather than pending.

### A figure the discussion wants and does not have

The attenuation sweep, recorded as a candidate last pass, belongs in the
discussion rather than in results: §4's conclusion is a margin, and the
de-attenuated coefficient against assumed error variance — with the observed
product disagreement marked, the spatial null as a horizontal reference and the
crossing at 5.6 times visible as a distance — would replace a paragraph with a
distance. Not built.

**And the figure audit's expectation was wrong.** It anticipated that a
discussion would reach the five figures no results section cites, particularly
the two framework diagrams and the land-cover provenance figures. It does not:
the diagrams are repository documentation rather than argument, and the
provenance figures belong to methods and errata. **The five-figure count stands
and the reason is now established rather than assumed.**

## The stale cross-reference class, surveyed and partly guarded, 14 September 2026

The previous pass found `notes/paper-target.md` citing
`notes/grounding-methods.md` as holding two claims superseded three passes
earlier, and named the failure mode: the correction was applied to the cited
record and not to the citing one. **That is a fourth drift class.** The other
three have mechanisms — recipes against artefacts, prose numbers against
artefacts, the figure inventory against the files it names. This one had none.

### The survey, which changes the verdict

**133 places where one record characterises another's content**, across
thirteen files: `notes/decisions.md` 33, `notes/paper-target.md` 27,
`notes/grounding-methane.md` 14, `README.md` 12, and the rest in single digits.
`notes/references.md` is excluded from the count; its several hundred file
mentions are "Cited in" pointers rather than characterisations, and a pointer
cannot go stale in this way.

**127 of the 133 paraphrase and 6 quote.** That split is the whole finding,
because **a paraphrase cannot be checked mechanically**: prose about prose has
no artefact to compare against, and deciding whether a paraphrase is faithful is
what a reader does. A quotation is a substring.

**Of the 6 quotable claims, 0 are genuinely stale.** One fails a literal match —
the Olofsson claim in `notes/paper-target.md` — and it fails because the
correction made last pass **quotes the superseded text beside the correction**,
which is this repository's convention. The words are meant to be absent from the
target. A hand sample of 14 of the 127 paraphrases found no errors either;
six were verified in depth and all six hold.

**So on today's evidence this is one historical instance, already corrected, and
not a live defect.** The brief asked whether that warrants a guard or a note.
The answer taken is: a note on the 127, and a guard on the 6, because the guard
also establishes the convention that makes the class checkable at all.

### What was built, and what it costs

`tests/test_cross_references.py`. Where a cross-file claim quotes its target,
the quotation must still be present in the file named. Three tests: the
quotation check, a guard that the survey pattern still matches anything at all,
and a guard that the historical exemption is exercised rather than being dead
code.

**The convention it establishes:** where a cross-file claim *can* quote, it
should, because a quotation is the only form of this claim a test can verify.
That is the cheaper of the two designs considered.

**The design rejected, and why.** A marker naming the target section with a
content hash would cover paraphrases too. It was rejected on the rule this
repository already records about checks: a hash over prose fires on **every**
edit to the target file, including edits nowhere near the claim, and a check
that fires on things that are fine gets suppressed and then catches nothing. A
quotation check fires only when the quoted words are gone.

**What it does not do**, so nobody reads more into it: nothing for the 127
paraphrases, no judgement about whether a quotation is used in the sense the
source intended, and it binds new claims only when they quote.

### Three false-positive classes, and the reason they are worth recording

The first three versions of the check reported 6 of 6 stale, then 2 of 6, then
1 of 6. **Every one of those was the check's fault.** Had the first version
shipped it would have fired on everything and been suppressed within a day,
which is the exact failure the rejected design was rejected for — and it would
have been suppressed on the evidence of its own output rather than on a
judgement about prose.

* **Hard-wrapped prose.** Both records wrap near 80 columns, so a quoted phrase
  crosses a line break at a different position in the quote than in the source.
  Whitespace is normalised on both sides.
* **Sentence case.** A quotation dropped mid-sentence is lower-cased where the
  source capitalises: "one figure exists so far" against "One figure exists so
  far", which is `notes/decisions.md` citing
  `notes/repository-architecture.md` and is **accurate**.
* **Deliberate historical quotation.** The correction convention means a
  corrected passage contains a quotation legitimately absent from its target.
  Exempted by a superseded marker near the claim.

**The guard was verified by mutation** rather than by passing: altering the
quoted sentence in `notes/grounding-methods.md` makes it fail with the citing
file, line and quotation named, and restoring the sentence makes it pass.

## The four drafts as a set, 14 September 2026

With the introduction written, all four sections `notes/paper-target.md` names
exist in draft: introduction, methods, results, discussion. This is the first
look at them as a set.

### Consistency across the drafts

**No claim appears in inconsistent form.** 73 resolvers are quoted in more than
one draft, and every one agrees. Five appear at **different precision**, which
is not the same thing and is worth recording because a copy-editor will flag it:
`baseline.constant_r2` as −0.0084 in methods and −0.008 in results,
`baseline.rice_alone_r2` as −0.0314 against −0.031,
`baseline.rice_plus_impervious_r2` as 0.0169 against 0.017,
`baseline.wind_r2` as 0.6527 against 0.653, and `dofs.cell_max_12tg` as 0.0649
in results against 0.065 in the discussion. The claim checker verifies each at
its own written precision, so all ten are correct; a paper would normally use
one precision per quantity. **Left as they stand**, because methods reports to
four places throughout and results to three, and the difference is a per-section
convention rather than an error.

**And two findings are stated at deliberately different strength**, which was
checked rather than assumed. The land-cover result is a "failed detection" in
all three sections that mention it, never an absence. The capability estimate
carries "not an inversion" in methods, results, discussion and introduction —
four times, which is the intended redundancy rather than an oversight.

### What the set does not cover

Four sections exist. **`notes/paper-target.md` names five**, and the missing one
is the conclusion: the discussion closes on §8 Limitations, so there is nothing
that states what the paper establishes in its own voice at the end.

**And two required sections exist nowhere.** No abstract, which is the section a
reviewer reads first and the one the publication-bias literature this file
already records identifies as where null results are filtered. No data
availability statement, which the target venue requires and which is the one
section this repository could write almost mechanically — 65 registered
recipes, a byte-comparison runner, and every artefact's provenance recorded.

So the honest state is **four of five narrative sections drafted, plus two
apparatus sections absent**. Recorded rather than assumed complete, and queued.

### Claim counts

277 marked claims across the four drafts and 680 unmarked: methods 80 and 287,
results 165 and 193, discussion 24 and 140, introduction 8 and 60. The unmarked
majority is literature figures, which resolve by citation rather than by
artefact, and each draft's own notes list its exemptions.

**All four are now in the claim checker's scanned set, and that is a test rather
than a habit.** `tests/test_drafts_are_scanned.py` asserts that every
`notes/draft-*.md` is in `verify_claims.SCANNED`, because a draft outside it
carries markers that are never evaluated — the checker passes, reports a count
excluding the file, and every number in it is unverified while looking verified.
The discussion draft spent a day in that state. A third test asserts each
scanned draft actually carries markers, since being in the tuple is necessary
and not sufficient.
## 15 September 2026 — the 0.1 degree grid, measured rather than estimated

**What reopened it.** This file closed the finer grid on a pilot estimate of
32.91 percent annual coverage at 0.1 degrees, and recorded in the same place
that the estimate came from an understated granule sample, that a free-asymptote
fit put the ceiling at 50.4 percent, and that "Reopening it needs a measured
curve at each resolution, not another sample." That curve now exists as
`data/processed/grid_resolution_2018.csv`, built by
`scripts/measure_grid_resolution.py` from the committed analysis grid.

**The verdict is that 0.1 degrees is not viable, and the measurement that says
so is not coverage.** Coverage was the wrong thing to have closed the question
on. Two other measurements decide it, and they point the same way.

### The effective sample size does not move

The assumption worth naming, because it is the one this file would have made:
that degrees of freedom grow with cell count. They do not. Dutilleul's effective
n is set by the domain's extent relative to the autocorrelation length, and
regridding changes neither. On a spherical model correlogram at the measured
operational half-sill of 103.2 km, the full lattice carries **30.9 effective
observations at 0.25 degrees and 30.6 at 0.1 degrees** — 6.17 times the cells
for no gain, and the small difference is model noise rather than signal. The
model is calibrated: `src/model/spatial_dof.py`'s empirical estimator gives
**32.8** on the committed field at 0.25 degrees, within 8 percent of the model's
30.9, and the ratio between resolutions held to within 1 percent across
exponential, Gaussian and spherical correlation forms that disagree by 27
percent on the absolute level.

The physical reading is that the domain is 739 by 918 km and holds roughly 33
independent patches about 144 km across. That count is a property of the region
and the atmosphere. **No gridding choice can create independent information, and
a finer grid subdivides the same 33 patches into more cells.**

*The model is used in one direction only.* Going finer, cells shrink further
below the correlation length and the point approximation improves. Going
coarser it fails: real aggregation averages within cells and changes the
support, and the empirical estimator falls to 20.4 at 0.5 degrees where the
point model predicts 28.7. So no coarsening claim is made from it. The
asymmetry favours the question actually asked.

### The per-cell standard error doubles

TCCON gives a single-retrieval precision of 14.5 ppb for the operational
product, and the mission's recommended error multiplication factor of 2 puts a
single sounding at 29 ppb. Against the field's between-cell standard deviation
of 14.9 ppb — the whole spatial signal a cell has to resolve — the median
covered cell's standard error is **3.37 ppb at 0.25 degrees, 23 percent of the
signal, and 7.49 ppb at 0.1 degrees, 50 percent of it.** Cells whose standard
error exceeds the entire field spread go from **63 to 1,015**. Cells below 30
soundings go from 278 to 3,786.

So the trade is explicit: 6.17 times the cells, no additional independent
observations, and twice the noise in each cell.

### The gaps fragment rather than concentrate

At 0.25 degrees the 97 uncovered cells form 28 components with 43.3 percent of
them in the largest, which is a describable feature — predominantly inland, over
rugged southern terrain. Projected to 0.1 degrees they become **107 components
with only 36.1 percent in the largest and 62 single-cell holes**, up from 17. A
coherent limitation with a terrain explanation becomes scattered speckle with
none. That is worse for the paper than a larger gap would be.

### What could not be measured, and what the cheapest measurement would cost

**Coverage at 0.1 degrees cannot be measured from anything this repository
holds.** Sounding coordinates are not retained. The checkpoint's
`granule_cells` bitset is 1024 bits per granule *over the 0.25 degree lattice*,
so it records which coarse cell a granule touched and **a cell set recorded at
0.25 degrees cannot be subdivided**; `data/interim/alt_grids/` holds alternative
predictor products rather than alternative resolutions, despite its name; and
`data/raw/s5p` retains one of the 578 granules. Neither route exists without
re-reading granules, which this pass did not do.

So the fine rows in the artefact are **projections, not measurements**, and the
`basis` column says so. They allocate each coarse cell's soundings to fine cells
by area overlap under a uniform-within-cell assumption. TROPOMI soundings arrive
in along-track swaths, and clustering can only concentrate the same soundings
into fewer fine cells, so **every projected coverage figure is an upper bound
and every count-below-threshold figure is a lower bound.** The verdict rests on
figures that are already unfavourable at their most favourable.

*The cheapest real measurement* is a second gridding accumulator inside the
existing granule pass. That pass took 122.7 minutes at 4.0 MB/s for 28.9 GB, so
it is transfer-bound: the marginal cost of a second resolution alongside a
0.25 degree pass is accumulator arithmetic and about 11 MB of memory rather than
another transfer. Done later as a separate pass it costs another 28.9 GB and
about two hours. **The asymmetry is roughly two hours against a few minutes,
which is the argument for deciding the resolution before the pass and not
after.**

### Three premises that did not survive

* **6,396 cells is not the 0.1 degree lattice.** Neither 7.75 nor 8.25 degrees
  divides by 0.1 — they give 77.5 and 82.5 cells, both half-integers. Whole
  cells from the southwest corner give **77 by 82 = 6,314**, and rounding both
  up gives 78 by 83 = 6,474. The recorded 6,396 is 78 by 82: longitude rounded
  up and latitude rounded down. This is the same failure as the 0.25 degree
  lattice's extent diverging from its declared box on both axes in opposite
  directions, and it is the reason the artefact reports the remainder rather
  than hiding it — at 0.1 degrees the lattice ends 0.05 degrees short on both
  axes.
* **32.91 percent was far too low**, as this file suspected without being able
  to show it. The full-year counts bound 0.1 degree coverage at **84.7 percent
  or below**, and the 50.4 percent free-asymptote ceiling is below that bound
  too. The pilot understated coverage badly enough that the number should never
  have closed a question. *It did not matter*: coverage turns out not to be the
  binding constraint, so the estimate was both wrong and beside the point.
* **"Roughly 53 of 926 effective observations" is not the field's effective n.**
  53.4 is `dof.effective_n_median`, a median across correlations. The field
  against itself gives **32.8**, which is the comparable figure and the one used
  above.

### Where this leaves the study

Two recorded statements bracket it. That 0.25 by 0.3125 degrees is the field's
working resolution because error correlations mean higher density does not buy
proportionate information — which this measurement now confirms on this domain
in the strong form, that it buys none. And that finer-scale regional inversions
would better exploit TROPOMI — which remains true and is not what this study is.
The distinction is that an inversion propagates information through a transport
model, so its fine cells are constrained by observations elsewhere; a per-cell
composite has no such mechanism and each cell is on its own. **A finer grid
helps a method this study does not use.**

So the resolution goes in the paper's discussion of resolution, and it
**strengthens the capability claim rather than weakening it**: the working
resolution was a constraint the observations impose, measured, and not a
convenience chosen and left unexamined. Tier 3 produces 0.25 degrees only.

*One gap this raised and did not close.* No committed record states TROPOMI's
ground pixel size, which is the quantity that would say how close 0.1 degrees
comes to the native retrieval footprint — the point at which gridding stops
averaging. It is worth recording, and it is not recorded here on the strength
of recollection.
## The Tier 3 retention pass, and what it settled

The five Tier 3 items shared one granule read, and that read is transfer-bound:
120 of its 122.7 minutes are download. So everything needing a granule was
collected in one pass — 578 granules, 28.9 GB, 53.2 minutes at 9.3 MB/s, into
`data/interim/extent_2018_extended.npz` rather than over the committed
checkpoint.

**The committed composite reproduces exactly.** `--verify-against` reports max
absolute difference of 0 in the bias-corrected band, 0 in the raw band and 0 in
the counts; `methane_composite_2018.tif` and `methane_coverage_2018.csv` both
reproduce byte-identically from the new checkpoint; zero granules failed. The
covariate artefacts do change, because a covariate was added — two columns
appear, **no existing value moves in any of the 1023 rows**, and the GeoTIFF
gains two bands. Nothing here reads that raster by band index and every
covariate consumer joins the CSV by column name, so the band shift breaks
nothing, but it is a real hazard for anything outside this repository.

### Two of the six items were already satisfied, which the queue did not know

**Within-cell variance was already recoverable.** Queue item 14 said the
checkpoint "holds sums and counts only, so the spread a representativeness
estimate needs is not recoverable from it". It was recoverable the whole time:
the seasonal accumulator's `hs::sum_yy` with `hs::n`, and `hs::n` equals
`counts` exactly. Tier 4's item 17 was recorded as gated by item 14 and was
therefore never gated. The pass collected an explicit `sumsq::` anyway — it
covers the secondary field, which the harmonic block does not, and it
cross-checks the primary. **The two agree bit for bit**, which is the strongest
validation available that the new accumulator is wired correctly.

**The ground pixel size needed no pass at all.** It is a global attribute on
every granule: `7.0x7.0 km2`. The previous pass recorded it as a gap and
declined to state it from recollection, which was right, but it was one file
read away rather than a 29 GB one.

### The rejection rate over this domain is two numbers

Of **2,098,671** soundings inside the box across the year, **221,686** carry a
retrieval and **110,920** pass quality control. So **89.44 percent of in-box
soundings are lost to no retrieval** — cloud, geometry — which the quality
threshold does not reject because there is nothing there to reject, and
**49.97 percent of the retrievals that do exist are removed by the threshold**,
almost exactly half.

Reporting a single "95 percent rejected" would attribute monsoon cloud to a
quality decision. The brief asked for the rejection rate as though it were one
number; it is two, and the distinction is the interesting part.

**The threshold removes whole bins.** The year's `qa_value` takes four values —
0, 0.16, 0.4 and 1.0 — so a cut at 0.75 keeps the 1.0 bin and discards the 0.4
bin entire. Moving the threshold anywhere between 0.4 and 1.0 changes nothing.

### A gridded covariate cannot test a filter, which the pass design turned on

The instruction was to grid `methane_mixing_ratio_precision` as a covariate
because "gridding it makes the filter testable afterwards". It does not. A
covariate gives a cell's **mean** precision; the filter's effect needs the sum
of methane over the **surviving soundings**, which is a conditional quantity no
marginal sum can supply. The same was already true of albedo, which had been
gridded for months without making its floor testable.

So the pass accumulated methane **binned by** precision and by SWIR albedo with
the published thresholds falling on bin edges, plus a joint slot for both
filters together, which the marginal histograms cannot give. About 500 kB. Had
the brief been followed literally, the pass would have cost 29 GB and left both
filters exactly as untestable as before.

### What the four omissions turn out to be worth

**The precision filter is a no-op, provably rather than approximately.** Of the
110,920 soundings passing quality control, 99.89 percent have precision under
5 ppb and 0.11 percent fall between 5 and 10. **None exceeds 10 ppb.** The
quality flag already enforces the published threshold.

**The albedo floor at 0.05 removes 11,707 soundings and empties 174 of 926
cells**, shifting the domain mean +0.78 ppb. Compared on the 752 surviving
cells — the committed target re-run on exactly those cells, because an R
squared on 752 is not comparable with one on 926 — **no land-cover model
overtakes the spatial null in any of the four designs.**

**Destriping is recoverable.** `notes/draft-methods.md` called it "not
recoverable without implementing one", and the reason given was true of what
had been kept rather than of what could be: nothing retained the across-track
detector column. The column is the flat index modulo the ground-pixel count, so
retaining it cost no extra variable read, and because destriping subtracts a
constant per column the per-cell per-column **counts alone** suffice to apply
it afterwards — about 880 kB instead of several megabytes. The offsets span
-15.27 to +12.77 ppb with a standard deviation of 5.09 ppb over the 200 columns
carrying soundings, which is a third of the between-cell signal. **Tested at
first order only**: the accumulator holds each column's sum over the whole
domain and year, so the offset is measured against the domain mean and absorbs
any column-to-geography relationship. It bounds what destriping would remove.

**Representativeness weighting changes neither the result nor the benchmark**,
and the corrected figures are below. The weighting is the Level 3 literature's
own inverse-variance weight with the spatial term at its low-coverage limit; it
is better conditioned than the weighting it replaces, spanning 69x against
205x; and it is close to orthogonal to sounding count, correlation -0.03,
because the spatial term carries 97.5 percent of the per-cell variance and does
not shrink with n.

Under spatial blocks, impervious cover rises from 0.0244 to 0.1429 and the
spatial null rises from 0.5137 to 0.5399. **The ordering is unchanged, the gap
barely moves, and no land-cover model overtakes the null under any weighting.**

### CORRECTED 13 September 2026: the collapse this entry reported was a bug

**This passage previously said** that "impervious cover overtakes the spatial
null in **two of the four scheme-weighting combinations**" and that "the
reversal is the benchmark collapsing, not land cover improving", with the null
falling "from 0.5137 to -0.125". **All of that was an artefact of the test, not
a property of the weighting.**

`test_preprocessing_omissions.write_grid_with_weight` substituted the
representativeness weight into the grid's `sounding_count` column **where a
weight existed and left the raw count where one did not**. Twenty-one cells
have a single sounding, so no within-cell spread and no representativeness
weight, and they kept their count of 1 in a column where every other cell now
held a value near 0.0026. Each of those 21 cells therefore carried 382 times a
typical cell's weight, and together they held **88.6 percent of all weight in
the fit.** The "representativeness weighting" variant was in substance a fit on
21 cells observed once each, which no spatial model can predict — hence a
spatial null that appeared to collapse.

**Two things made it look like a finding rather than a bug.** It had a ready
mechanism — the Level 3 literature does say count weighting measures the wrong
thing, so a result where count weighting flattered the null fitted the
expectation. And the diagnostics run against it were the wrong ones: the weight
range, the share of weight on sparse cells and the correlation with count were
all computed from `cell_quality_2018.csv`, which holds only the 905 cells that
*have* a weight, so none of them could see the 21 cells that did the damage.

The fix drops cells with no weight instead of leaving them, which changes the
sample, so the variant now carries a matched reference on the same 905 cells.
**The general lesson is the one this file keeps relearning**: a column that
means two different things in different rows will not announce itself, and a
diagnostic computed on the well-behaved subset cannot find the rows that are
not in it.

### What remains unresolvable without another read

* **Destriping beyond first order.** A proper correction estimates the stripe
  per orbit from a field with its spatial structure removed. That needs the
  column retained alongside the residual, per granule, which this accumulator
  does not hold.
* **The aerosol optical thickness ceilings** the same published chain applies.
  They are separate variables rather than thresholds on something already read,
  and they were not on the list.
* **A filter's effect on the covariates.** The sensitivities hold the
  predictors at their unfiltered values, deliberately, so the target's change
  is not confounded with the predictors'. The jointly filtered version would
  need the covariates binned the same way.
* **Anything at a threshold that is not a bin edge.** The histograms make
  10 ppb, 0.02 and 0.05 exact and everything else interpolated.

### Three failures worth recording

**The mirror listing had no retry and it killed a two-hour run in its first
minute.** One `SSL: UNEXPECTED_EOF_WHILE_READING` on a single day's prefix, out
of about 245 listing requests, and the same prefix answered HTTP 200 in half a
second three times immediately afterwards. The listing runs *before* the loop
that tolerates per-granule failures, so it had no protection at all. Bounded
retries were added there and to the download, the latter because a granule lost
to a flaky socket would leave the composite resting on a different sounding set
and the reproduction check would then report a difference whose cause was the
network.

**A latitude formula mirrored the grid and every join still succeeded.** The
checkpoint's row 0 is the **north** edge, and the analysis scripts were written
with `south + (row + 0.5) * res`. The lattice is symmetric in shape, so all 926
cells matched and the values were attached to the wrong places. It was caught
only by requiring the harness to reproduce the committed baseline results
before trusting it, which it then did for 84 of 88 rows — the other four
differing in the fourth decimal because six cells' 2 dp means round differently
in `analysis_grid_2018.csv` than recomputing them from sums does.

**A weight substitution silently did nothing.** The grid stores `35.075` and the
lattice key is `35.0750`; comparing the raw strings matched almost nothing, so
the representativeness variant was the committed run under another name and
reported deltas of zero. It looked like a finding — "weighting changes nothing"
— and was a formatting bug.

### One count in this file was wrong

This file records "Of 578 granules acquired, 356 returned no qualifying
sounding", which gives 222 productive granules. Both the committed checkpoint
and the re-run say **355 and 223**. The re-run reproduces the committed
composite exactly, so this is an arithmetic slip in the record rather than a
difference between the runs.
## Tier 5, and the two decisions it forced

### The weighting, decided

**Sounding-count weighting stays primary for the fits. The equivalence claim is
stated at the level the least favourable defensible weighting supports.** Those
are two decisions and separating them is the whole point.

*The case for representativeness weighting.* `notes/grounding-methods.md`
records that coverage "is not an effective metric to limit representation
errors" and that density does not bound the error that matters, which is an
argument that count weighting measures the wrong thing. This repository holds
its own separate objection, that count weighting tilts fits toward flat bright
terrain — retrieval succeeds there, so those cells accumulate soundings and
therefore weight. And the measured weight is better conditioned than the one it
would replace, spanning 69x against 205x, and close to orthogonal to it at
-0.03.

*The case against.* It is what four drafts, thirteen figures and every baseline
artefact use. It is **undefined on 21 cells** — a single sounding gives no
within-cell spread — so adopting it silently drops them. And its spread term is
unreliable exactly where it matters: a cell with two soundings has a spread
estimated from two points, which can be near zero by chance and then attracts
large weight. The error diagnostic shows it: 25 cells carry 48 percent of the
weighted squared error and the worst offenders have 2, 3, 10 and 12 soundings.
The spatial term is also at its low-coverage *limit* rather than a measured
within-cell coverage, which the accumulator cannot produce.

*What the evidence says, after the correction.* Nothing turns on it for the
fits. Impervious rises from 0.0244 to 0.1429 under spatial blocks and the
spatial null rises too, 0.5137 to 0.5399; the ordering holds in all four
designs under both weightings. **The earlier report that the null collapsed was
a bug and is corrected above.**

*So the decision for the fits is continuity, and it is labelled as continuity
rather than dressed as science.* Switching would touch every artefact and
change no conclusion. That is a sufficient reason only because the evidence
shows the choice does not matter; if it had mattered, continuity would not have
been enough, and the better-grounded weighting would have had to win.

### The part where it does matter, and where continuity is not allowed to win

**The weighting decides whether the stronger equivalence claim can be made for
impervious cover.** Against the comparative bound, impervious clears it in
**4 of 4 fields under sounding-count weighting, 3 of 4 unweighted, and 0 of 4
under representativeness weighting.**

So the weighting this project already uses, and which the literature
criticises, is the one under which the paper would be entitled to say more.
**Choosing it for that reason would be choosing the weighting that flatters the
conclusion**, which is the failure mode the equivalence exercise exists to
prevent.

The claim is therefore stated at the weakest defensible weighting's level: **no
meaningful rice effect, and for impervious cover a failed detection only.** The
drafts say which is which and why. Rice needs no such care — it clears the
bound in all 24 combinations, under every weighting and every field.

### What the equivalence test licenses, and what it does not

The bound is comparative: the spatial null's own held-out performance expressed
as a correlation, |r| = 0.5765. It was chosen because the paper's claim is
already comparative, so a comparative bound introduces no arbitrary fraction and
tests the sentence the paper actually wants to write.

**The policy bound this file and the region grounding both point to could not
be set, and that is a finding.** The factor of 13.7 for water regime, and the
tens of percent for variety, straw and nitrogen, all bound *emissions*. This
study measures a *column mixing ratio*. Converting between them needs a
transport model, which is the tool the capability claim is built on not having.
The most defensible basis in the record is out of reach from inside the study,
and substituting a number would have hidden that.

**What a reader loses**: an effect smaller than the spatial benchmark's but
still physically substantial passes as equivalent. The claim licensed is
"smaller than the benchmark this paper reports against", not "small enough not
to matter". Nothing available here licenses the second.

### The specification curve

126 specifications. **None is both positive and beats its own spatial null.**
Fifteen beat the null and every one of them does so at a negative held-out R
squared, where the model and the benchmark both fail and land cover fails less.
The best land-cover result anywhere is +0.1429, against that specification's
null of 0.5399.

The curve also measures what this file had asserted without measuring: the
spread belongs to the evaluation. As the range of medians across each axis,
cross-validation scheme moves the result 0.1764, predictor set 0.0943,
weighting 0.0517, preprocessing 0.0444, and the methane field 0.0131. **The
choice of held-out design moves the result almost twice as much as the choice
of predictor and fourteen times as much as the choice of field.**

*One claim in this file did not survive the check.* It says land cover "has the
smallest four-way spread of any predictor in the suite". It has the smallest of
the seven it lists, and 0.247 is correct, but `OLS wind + trend surface` spans
0.115 and `constant (global mean)` 0.169. The quantifier is wrong; the argument
it supports is not.

### TCCON, and why it is not computable here

**The alignment needs two things this repository does not hold.** The Rodgers
correction needs the satellite averaging kernel, both prior profiles and the
dry-air subcolumns *per layer*; the granules carry all three as
`(1, 2905, 215, 12)` arrays, and the checkpoint carries none of them — only
`xch4_apriori` as a gridded column scalar. And **no TCCON data is on disk at
all**: `notes/dataset-leads.md` lists Hefei GGG2020.R1 as verified accessible
on CaltechData at 57.49 MB, and it was fetched, used and deleted under the
delete-what-you-fetch rule, so the recorded -5.74 ppb bias with a standard
deviation of 5.79 exists as a number and not as a reproducible artefact.

**The cost is far below a pass, which is the useful part.** The station's cell
is touched by **32 granules on 32 distinct days** carrying 162 soundings, and
only the nine days with TCCON coincidence are needed. At the mirror's mean
granule size that is roughly 480 MB and about a minute of transfer, plus the
57.49 MB TCCON re-fetch — not another 28.9 GB. It is queued, not run.

**And the licence does not bind, because nothing rests on it.** Both drafts
already say so in terms: "no result in this work rests on that comparison".
TCCON's terms require contacting the site's listed individuals four to six weeks
before submission with co-authorship normally expected *where the data is
essential*. It is not essential here, so the comparison can be dropped or kept
as supplement without starting that clock. If it were ever promoted to a
validation the clock would start at submission minus six weeks — and that is
Matt's call, not one this pass makes.
