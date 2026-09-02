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
not `Duyst-Yale-Thesis.md`. The two are not the same document and the markdown
is the weaker source.

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
for 2018. The full year gives 90.62 percent and 110,928 soundings from 578
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
result at 0.25 degrees is 90.62 percent. Extrapolating a saturation curve from
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
32.91 percent at 0.1 degrees. At 90.62 percent for a single year a finer grid may
now be defensible, and the question is worth reopening with the measured
saturation rather than the estimated one. Changing it would invalidate the
committed composite and the coverage table, so it is a decision to take
deliberately and not a correction to apply.
