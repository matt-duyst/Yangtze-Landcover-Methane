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
