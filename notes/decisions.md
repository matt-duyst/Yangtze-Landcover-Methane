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
over the sampled days is 35.67 ppb with a peak on day 245.8, early September.
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
110,920, productive granules from 222 to 223. Earlier sections have been updated
to the current values rather than left to contradict the data. Where an argument
in this file turns on the gap between a reconnaissance estimate and the measured
year, the gap is unchanged to within a tenth of a percent and the argument
stands as written.


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
