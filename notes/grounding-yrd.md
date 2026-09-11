# The Yangtze River Delta as a case study

Draft material for a paper's introduction and discussion. The target of this
work changed while it was under way: the 2023 thesis was submitted and cannot
be edited, so it becomes prior work that a paper cites rather than a document
to revise. What follows is therefore organised by what it establishes about the
region, not by which literature search found it, and not by which section of
the thesis it answers.

Every figure here was checked against its source before it was written. Where a
figure could not be verified it is named as unverified and the number is not
repeated; the closing section lists every such case, because a grounding
document that hides its gaps is worse than one that has none. Numbers taken
from this repository's own artefacts are marked for
[`scripts/verify_claims.py`](../scripts/verify_claims.py) where the artefact is
committed. Several are not: they come from
`data/interim/extent_2018.npz`, a gitignored checkpoint, and they are
reproducible only where that file exists. Those are stated as such at the point
of use rather than marked, which is the documented convention for a number the
mechanism cannot check.

## The region's methane budget, and why this is the right place to ask

The middle and lower reaches of the Yangtze — Hunan, Hubei, Jiangxi, Anhui,
Zhejiang, Jiangsu and Shanghai — account for approximately 38.4 percent of
China's national agricultural methane emissions, mainly because the region is
the country's largest rice-growing area (Duan et al., 2023, *Environmental
Science & Technology* 57, 13292–13303, doi:10.1021/acs.est.3c04209). That
figure is the strongest single justification for studying methane and rice
together here, and it needs one qualification carried with it every time it is
quoted: it describes seven provinces, and this study's domain is four. Hunan,
Hubei and Jiangxi lie outside the lattice entirely. The four provinces are a
subset of the region the 38.4 percent belongs to, so the figure motivates the
study area without describing it.

At national scale the sectoral composition is dominated by energy rather than
agriculture. In 2024 China's total methane emissions reached 61.69 Mt, with
energy contributing 52.36 percent, or 32.30 Mt, and agriculture 37.20 percent,
or 22.95 Mt; coal mining alone accounted for 30.42 Mt and was the largest
single source, while agricultural emissions were driven mainly by enteric
fermentation at 11.65 Mt and rice cultivation at 7.88 Mt (Zhang et al., 2026,
*Environmental Science & Technology* 60, 22323–22334,
doi:10.1021/acs.est.5c18654). Rice cultivation is therefore about 12.8 percent
of the national total, which is worth stating plainly because it sets the scale
of what a rice predictor could ever explain in a column field. The energy share
is concentrated in provinces this study does not cover, which is part of why
the regional agricultural share is as high as it is.

The same inventory supplies the one urban statement in this section that could
be verified. Waste-related emissions accounted for the majority of total
methane emissions in 38 cities, primarily in economically developed, densely
populated coastal agglomerations, and those cities include large parts of the
Yangtze River Delta with Shanghai and Suzhou named as representative examples
(Zhang et al., 2026). Both are inside this study's domain: Shanghai is one of
the four provinces and Suzhou is in Jiangsu. That is a narrower claim than the
one [`ERRATA.md`](../ERRATA.md) 5.3 once made and withdrew, and it is the
version the errata now carries.

## A local inversion reached a compatible conclusion by a method that supports it

The closest thing to a local answer for the study year is a tower-based
inversion of this exact region. Atmospheric CH4 measured at a 70 m tall tower
in the Yangtze River Delta was combined with a scale-factor Bayesian inverse
model to constrain seasonal variation in emissions, and in 2018 — this study's
own year — agricultural soils, meaning rice production, were the main driver of
seasonal variability in atmospheric CH4 concentration. The prior inventories
underestimated agricultural soil emissions, especially during the growing
seasons, and posterior emissions from agricultural soils accounted for 39
percent, or 4.58 Tg, using EDGAR v432, rising to 47 percent, or 5.21 Tg, using
EDGAR v5.0 (Huang et al., 2021, *Advances in Atmospheric Sciences* 38,
1537–1551, doi:10.1007/s00376-021-0383-9).

**The direction of EDGAR's error in this region is not settled, and this record
carried only one side of it until 13 September 2026.** The same group, using the
same tower, reached the opposite conclusion for an earlier period. Hu et al.
(2019, *Journal of Geophysical Research: Biogeosciences* 124, 1148–1170,
doi:10.1029/2018JG004850) measured from June 2010 to April 2011, took **EDGAR
v4.3.2** as the a priori, and applied three top-down approaches — multiplicative
scaling factors, flux ratio, and scale-factor Bayesian inversion. Its abstract:
the three posterior estimates "were 30.2(±17.6)%, 31.5 (±5.6)%, and 30.8
(±27.4)% lower than the a priori ... v432 emission inventory estimate", and "the
**overestimate** was mainly caused by two source categories including fuel
exploitation and agricultural soil emissions (rice cultivation)", with posterior
agricultural soil 47.8 percent *below* the prior. Its total for the region was
6.52 (±1.59) Tg a⁻¹.

So for agricultural soil in this region, against the same inventory version, one
study found EDGAR 47.8 percent too high in 2010–11 and the other found it too
low in 2018. **The two are not compatible as flat statements and the record
should not carry either as "EDGAR's direction of error in the YRD".**

The reconciliation available is scope, and it is the scope each paper actually
claims. Hu et al.'s figures are **annual totals** — three estimates of a yearly
flux density, of which 30.8 percent is the least certain at ±27.4. Huang et
al.'s statement is about **seasonal shape**: the underestimate is "especially
during the growing seasons", and the paper's own supporting figure is that in
summer agricultural soil contributed 42 percent (v432) to 64 percent (v5.0) of
the concentration enhancement. A prior can be too high over a year and too low
in the flooded months if its seasonal amplitude is too flat, and EDGAR is a
plausible candidate for that: Hu et al. record that v4.2 carries annual values
with no monthly variation at all while v4.3.2 varies monthly, so the monthly
profile is recent and unvalidated here.

Two further differences may matter and neither paper tests them. The periods are
seven years apart, over which this record establishes that the region's rice
area fell. And the two regional totals differ by nearly a factor of two — Hu's
6.52 Tg a⁻¹ for 2010–11 against Huang's implied 11.7 Tg a⁻¹ for 2018, from 4.58
Tg of agricultural soil at 39 percent of the total.

**What this changes for how the rice-dominance finding is read.** Huang et al.'s
attribution of 2018 seasonal variability to agricultural soils stands; nothing
here touches it, and it remains the closest thing to a local answer for this
study's year. What does not stand is any inference that EDGAR systematically
underestimates rice in this region, which would have supported a
better-rice-prior argument more strongly than the evidence allows. The
better-prior argument in [`notes/grounding-methods.md`](grounding-methods.md)
rests on GRPI's finding that EDGAR overspreads rice spatially and on Liang et
al.'s measured 40 percent bias reduction over Heilongjiang, neither of which is
affected by this and both of which are about spatial distribution rather than
about magnitude.

**And one premise that reached this record from a citing paper is wrong.** The
Chengdu–Chongqing inversion paper attributes to Hu et al. (2019) a finding that
"EDGAR v7 overestimated methane emissions in the Yangtze River Delta region by
30.8 percent". The 30.8 percent is real and is in Hu et al. The version is not:
Hu et al. assessed **v4.3.2**, and EDGAR v7 was released years after that paper.
A 2019 paper cannot have assessed it. The figure is carried here from the
primary source and the version is corrected.

This is the paper's strongest positioning and it should be stated in exactly
these terms. **The reproduction's null result is not that rice does not
matter.** A tower inversion of this region in this year found rice dominant in
the seasonal signal. What the reproduction establishes is narrower and
different: a static annual land-cover fraction, regressed against an annual
column composite at 0.25 degrees, cannot recover what a tower inversion
recovers. The two findings are compatible, and the interesting question is what
separates them. The three sections that follow are three independent answers.

## The rice calendar, and what the composite's own sampling does to it

ChinaRiceCalendar extracts transplanting, heading and maturity dates for early-,
middle- and late-season rice across China from 2003 to 2022 from MODIS time
series, and validates them against field observations at Chinese agricultural
meteorological stations. The R² values between the dataset and station
observations for early-, middle- and late-season rice are 0.91, 0.94 and 0.90
respectively, with root mean squared errors of approximately 14 days (Li et al.,
2024, *Earth System Science Data* 16, 1689–1701,
doi:10.5194/essd-16-1689-2024). The dataset itself is deposited separately at
Harvard Dataverse (Liu et al., 2023, doi:10.7910/DVN/EUP8EY).

The paper gives no province-level calendar in its text, so the figures used here
are its observed regional means for the Middle-Lower Yangtze, the agricultural
region containing Anhui and Jiangsu. There, mean transplanting dates are
approximately day of year 120 for early rice, 160 for middle rice and 200 for
late rice, and mean maturity dates approximately 210, 260 and 290 (Li et al.,
2024). Middle-season rice is the relevant season for this study, because the
rice layer the analysis grid carries is a single-season rice product (Shen et
al., 2023, doi:10.5194/essd-15-3203-2023). Its flooded-to-mature window is
therefore day of year 160 to 260, which in 2018 was 9 June to 17 September.

Against that window, the composite's own sampling is badly placed. The 2018
composite rests on 110,920<!--#composite.soundings--> soundings inside the study
box, and their distribution across the year is extremely uneven: 273 in April,
10,746 in May, 5,506 in June, 5,042 in July, 5,542 in August, 14,594 in
September, 34,182 in October, 17,313 in November and 17,722 in December, with
nothing at all before 30 April. Of those, 19,476, or 17.6 percent, fall inside
the middle-rice window; 82.4 percent fall outside it. October alone, with
34,182 soundings, carries more than June, July, August and September combined,
which together hold 30,684. November and December together hold 35,035, more
again than the whole of that four-month span. These counts and fractions are
computed from the per-granule acquisition times retained in
`data/interim/extent_2018.npz`, which is gitignored, and so are unmarked.

**The seasonality of the observations and the seasonality of the emissions are
anticorrelated, and this is independent of transport, retrieval bias and
sampling composition.** It is a property of when the instrument returned usable
soundings over this box, nothing more. Yield is strongly seasonal here and runs
against granule availability, which `data/processed/README.md` already records
for the coverage statistics; the consequence for the rice question had not been
drawn.

One further measurement complicates the simple version of that statement and
makes the finding stronger rather than weaker. Fitting the composite's shared
seasonal cycle from the harmonic accumulators in the same checkpoint puts its
peak at day of year 245.8, which is 2 September 2018, and its trough at day
144.7, 24 May. The peak sits **inside** the middle-rice window, three weeks
before maturity. So it is not the case that the column field carries no seasonal
signature timed like rice; it carries one. What the annual composite does is
average that signature against a sounding distribution weighted three to one
towards the days after it: 83,773 soundings, 75.5 percent of the total, fall
after day 245.8, against 27,147 on or before it. The amplitude of that fit must
not be quoted as an
estimate of the region's annual XCH4 cycle, for the reason
`data/processed/README.md` gives: there are no soundings before day 120, so the
fit extrapolates across a third of the year. The phase sits mid-window and is
the part of it that the sampling supports.

**This is not fixable from the existing checkpoint, and an earlier version of
this note said it was.** The accumulator holds one running sum and one count
per cell for the whole year, because sums compose across resumed runs and means
do not; the per-granule record retains acquisition time and a sounding count but
not the values. A mean over a subset of days cannot be recovered from an annual
sum, so a growing-season composite requires re-gridding the granules, which is
the 28.9 GB transfer the composite recipe already declares as on-demand. What
*is* available without any download is the fitted seasonal cycle evaluated at
any date, which is what the deseasonalised field already exposes, and which is
the cheaper form of the same question.

## Water management is the dominant control, which is why extent is a weak proxy

A long-term double-rice experiment in China measured net global warming
potentials of 22,497, 8,895 and 1,646 kg CO2-equivalent per hectare per year
under continuous flooding, flooding with midseason drainage, and irrigation for
flooding only at transplanting and tillering respectively; annual grain yields
were comparable between the first two and reduced significantly, by 13 percent,
under the third (Wu et al., 2018, *Scientific Reports* 8,
doi:10.1038/s41598-017-19110-2). The spread across three water regimes on the
same soil under the same crop is a factor of 13.7.

That single-site result is consistent with the synthesis literature. A
meta-synthesis of eleven recent meta-analyses reports that relative to
continuous flooding, methane emissions decreased by 31 to 62 percent across ten
of them and nitrous oxide emissions increased by 37 to 445 percent across seven,
with rice yield changing from −5.4 to +11 percent and a mean of +1.3 percent
across eight (Minamikawa, 2025, *Paddy and Water Environment* 23, 525–532,
doi:10.1007/s10333-025-01045-4). An underlying meta-analysis of 201 paired
observations from 52 studies gives the effect more precisely: non-continuous
flooding reduced CH4 by 53 percent and increased N2O by 105 percent while
decreasing yield by 3.6 percent, and because N2O contributes on average only 12
percent of the combined global warming potential, the net effect was a 44
percent reduction in GWP (Jiang et al., 2019, *Field Crops Research*,
doi:10.1016/j.fcr.2019.02.010).

**Two cells with identical rice fraction can differ by more than an order of
magnitude in methane emission depending on the water regime, and rice extent
cannot see the difference.** This is the strongest physical argument for the
negative finding and it was absent from this repository until now. It is not an
argument that the rice layer is wrong. It is an argument that the quantity the
rice layer measures — area under rice — is not the quantity that determines
emission, and that the missing variable has a larger dynamic range than the one
present.

## Coal, which no grounding pass had found and which is inside the lattice

**Four grounding passes over this region missed a major methane source in it.**
The Huainan–Huaibei coalfield lies in northern Anhui, inside the analysis
lattice, and until 13 September 2026 nothing in this repository mentioned coal
at all.

Its scale is not marginal. Raw coal production across the whole coalfield was
**131.45 Mt in 2010**, coalbed methane resources are **1.1 × 10¹² m³**, and net
accumulated thicknesses of all minable seams are **18 to 32 m in Huainan and 8
to 18 m in Huaibei** (Liu et al., 2009, *International Journal of Coal Geology*
79, 97–112, doi:10.1016/j.coal.2009.05.001). In-place gas content is generally 8
to 16 m³ per tonne in Huaibei and 10 to 30 in Huainan on the same source; a
mine-specific study of the deep area of Qi'Nan colliery in Huaibei measured
total gas content of **4.58 to 12.33 m³ per tonne, averaging 8.83**, with
methane at 92.83 to 99.22 percent of the gas (Wei et al., 2024, *Scientific
Reports* 14, doi:10.1038/s41598-024-79922-x).

**And the load-bearing claim is that this province leads its region.** A gridded
bottom-up inventory of Chinese coal mine methane states that "**Anhui and
Liaoning are the provinces that emit the most in the east and north,
respectively**" (Sheng et al., 2019, *Environmental Science & Technology
Letters* 6, doi:10.1021/acs.estlett.9b00294). Shanxi dominates nationally at
about 35 percent and the southwest accounts for 28, but among eastern provinces
Anhui is first — and Anhui is one of this study's four.

For national scale: 15.8 Tg of methane released per year by Chinese coal mining
in 2018, 11.8 Tg after deducting recycling, at a weighted emission factor of
6.77 m³ per tonne, with Shanxi at 8.43 billion m³ or **35.5 percent** of the
national total (Zhu et al., 2022, *International Journal of Environmental
Research and Public Health* 19, 7408, doi:10.3390/ijerph19127408). The two
independent Shanxi shares, 35 and 35.5 percent, agree.

### The prior-inventory finding, which matters for any inversion

Sheng et al.'s inventory is at **0.25 by 0.25 degrees — this project's own
resolution** — and was built from a public database of more than 10,000 Chinese
coal mines for 2011, which is **25 times more mines than EDGAR v4.2 carries and
2.5 times more than v4.3.2**. Its conclusion about the global inventories is
direct: "the spatial errors in the EDGAR v4.2 and v4.3.2 inventories remain on
the provincial level as their relative contributions of provinces to coal mine
methane emissions differ significantly from the gridded inventory results."

So the same inventory family that
[`notes/grounding-methods.md`](grounding-methods.md) records as overspreading
rice across all agricultural land also misallocates coal at provincial scale,
and the correction exists at the resolution an inversion of this domain would
use. Whether the gridded inventory is distributed could not be established: the
paper is paywalled, the publisher's page and the institutional repository copy
both refused, and no data availability statement was reached. It is recorded in
[`notes/dataset-leads.md`](dataset-leads.md) as unverified for that reason.

### The consequence, which is specific and now testable

**Northern Anhui cells carry coal mine methane from a source neither predictor
represents.** Impervious fraction does not see a colliery, and rice fraction
does not either.

**Those are the same cells where the rice predictor has a hole.**
`notes/decisions.md` records that the NESDC raster stops classifying north of
33.3462 north, leaving an unclassified region in northern Anhui. So the part of
the lattice with an unrepresented major source is also the part with a missing
predictor, and the two defects coincide rather than being independent.

Tier 0 makes this measurable in a way it was not before. The buffered decay
curve established that the impervious coefficient is **not stable across the
domain**, its advantage over a constant falling from +0.118 at no buffer to
+0.007 at 300 km, and `notes/decisions.md` records that as the first direct
measurement of something the repository had only noticed — that the exceptions
recur in the same places.

**The question this raises is recorded rather than answered.** Whether the
coalfield's cells are among those where the coefficient behaves differently, and
whether excluding them changes the land-cover association, is a computation over
the artefacts Tier 0 already committed. It needs no new data and it is in
[`notes/paper-target.md`](paper-target.md)'s queue. It is not answered here
because answering it inside a literature pass would mean reporting a result
without the tests and recipe an artefact in this repository requires.

### And it makes a recorded separability problem concrete

`notes/grounding-methods.md` carries GRPI's finding that errors in rice spatial
distribution "compromise the ability to separate rice emissions from other
sectors such as coal in southern China". That was recorded as a general caution
about a region. **This study area contains both sectors in adjacent cells** —
paddy across the Yangtze plain and collieries in northern Anhui — so the caution
is not general here. It is the specific reason an inversion over this domain
would struggle to attribute a northern Anhui enhancement between rice and coal,
and the reason a better rice map has a value here beyond rice.

## Emission factors, and the reason a delta is a special case

Deltaic rice production systems are characterised by very specific hydrological
conditions compared with other rice-growing environments, so the application of
default emission factors may be erroneous, and only a few studies have been
published on methane from rice grown in such environments. Measurements across
four agro-ecological zones of the Mekong River Delta — alluvial soils, salinity
intrusion, deep flood, and acid sulfate soils — gave mean emission rates ranging
from 0.31 to 9.14 kg CH4 per hectare per day, and the weighted zone means were
offered as zone-specific emission factors for an IPCC Tier 2 approach (Vo et
al., 2018, *Soil Science and Plant Nutrition* 64, 47–58,
doi:10.1080/00380768.2017.1413926). The range within one delta is a factor of
29, wider than the water-regime spread above, and it is the reason an
emission-factor approach applied to the Yangtze delta with default factors
would be building on sand. **No equivalent agro-ecological zonation for the
Yangtze River Delta was found.**

A synthesis of new methane emission estimates for rice paddies in this region
exists (Zhu and Li, 2024, *International Journal of Environmental Science and
Technology* 22, 11011–11016, doi:10.1007/s13762-024-06050-4). Its figures could
not be verified: the article is paywalled, no abstract is indexed by Crossref or
OpenAlex, and no accessible copy was found. Its content is therefore not quoted
here, and the consequence it would support for the thesis's first hypothesis —
that rice area fell while per-hectare intensity rose, so the two oppose each
other — is recorded as a claim awaiting a source rather than as a finding.

## Three land-use transitions, not one

The thesis frames the land-cover story as urban expansion encroaching on paddy.
The literature adds two more transitions, both reducing methane, and neither
visible in an impervious-versus-rice framing.

The first is double-crop to single-crop conversion. Incorporating
high-resolution rice cropping system maps into the CH4MOD model, a total
planting area of 253.64 × 10⁴ hectares was converted from double-crop to
single-crop rice across southern China between 1990 and 2015, which reduced CH4
emissions by 451.94 Gg, or 8.4 percent of emissions from Chinese paddies in
2015; the largest reduction was in the Middle-Lower Yangtze plain, attributed to
high labour pressures, and as urbanisation continues the authors project total
emissions falling by between 17.1 and 9.2 percent under further conversion, in
their extreme and most likely scenarios respectively (Jiang et al., 2023, *Land*
12, 270, doi:10.3390/land12020270). The model is CH4MOD, the semi-empirical
paddy methane model of Huang et al. (1998, *Global Change Biology* 4, 247–268,
doi:10.1046/j.1365-2486.1998.00129.x).

The second is paddy to upland vegetable conversion. Converting double rice
cropping to vegetables in southern China took cumulative CH4 emissions from
348.9 and 321.0 kg C per hectare per year under fertilised and unfertilised rice
to −0.4 and 1.4 kg C per hectare per year under the corresponding vegetable
fields, while cumulative N2O went the other way, from 1.27 and 0.56 to 19.2 and
8.5 kg N per hectare per year (Yuan et al., 2016, *PLoS ONE* 11,
doi:10.1371/journal.pone.0155926). Methane does not merely fall; it goes to
approximately zero, and in the fertilised case slightly negative. The conversion
is described as becoming increasingly widespread, and has been studied
specifically in the Yangtze River Delta (Li et al., 2026, *Frontiers in
Microbiology* 17, doi:10.3389/fmicb.2026.1750894).

**The consequence for this analysis is specific.** A cell that loses paddy to
vegetables shows no change in impervious fraction and a fall in rice fraction,
which in these two layers is indistinguishable from a cell that loses paddy to
urban. The methane consequences differ: paving removes a rice source and adds an
urban one, while planting vegetables removes the rice source and adds nothing
that either predictor represents. Two transitions with different methane
signatures therefore produce the same signature in the predictors, which is a
confounding mechanism rather than a measurement error, and it cannot be fixed by
improving either layer.

## Livestock and wetlands, both favourable to the thesis's omissions

Regions of high livestock methane emission are mainly in northwestern and
southwestern China, contributing 6.05 Tg in 2020 and accounting for 44 percent
of China's livestock emissions, while eastern coastal provinces including
Jiangsu and Zhejiang show decoupling of economic growth from livestock CH4,
driven by urbanisation and livestock relocation (Duan et al., 2023). The
thesis's omission of livestock is therefore defensible for this region rather
than merely convenient, and the mechanism is worth stating because it runs
against the intuition the thesis works from: here urbanisation reduces a methane
source by displacing animals out of the region, not by paving paddy.

Wetlands are a real source and they are coastal and estuarine, around Chongming
Dongtan and Hangzhou Bay. Their behaviour is not static: invasive *Spartina
alterniflora* changed a Yangtze Estuary salt marsh from a CH4 sink to a CH4
source (Yang et al., 2021, *Estuarine, Coastal and Shelf Science* 252, 107258,
doi:10.1016/j.ecss.2021.107258), so the sign of the wetland term is not even
fixed, let alone its magnitude.

These are also the cells the composite handles worst, and the repository can put
a number on it. Over the 926<!--#composite.covered_cells--> covered cells,
those between 25 and 99 percent sea — the coastline — have a median of
6<!--#composite.coast_median_soundings--> soundings against
133<!--#composite.land_median_soundings--> for cells that are wholly land. Both
figures are over covered cells only, and that restriction matters: taken over
all 1,023 cells with the uncovered counted as zero, the same two populations
give medians of 2 to 3 and about 108, which is the pair
`data/processed/README.md` quotes. Both are true of the same composite and they
answer different questions. So the wetland source sits where the observations
are thinnest by a factor of more than twenty, and a wetland term could not be
tested against this field even if a layer for it existed.

## Urban methane, where the thesis does better than the errata said

The thesis attributes urban methane to natural gas, and that attribution has
substantial support which the errata did not credit.

The strongest evidence is regional. A study using ethane as a fossil tracer over
ten years of atmospheric measurements, from 2012 to 2021, finds methane
emissions from natural gas consumption in the Yangtze River Delta cities of
China to be underestimated (Zhao et al., 2026, *Nature Cities*,
doi:10.1038/s44284-026-00504-1). The title, authorship, journal and DOI are
verified through Crossref. Its numerical results — a mean leakage rate near 3.5
percent against a value near 0.2 percent used in Chinese inventories — are
**not** verified here: the article is paywalled, its abstract is not indexed,
and the only source for those figures was a press summary. They are therefore
named as unverified and not quoted as findings. What can be stated from the
verified record is the direction and the region, and that is enough to matter:
the region is this study's own.

Against a large leakage estimate stands a direct measurement. Mobile
measurements in Hangzhou, a Yangtze River Delta megacity, found the natural gas
distribution system there to be a low emitter (Zhao et al., 2024, *ACS ES&T
Air* 1, 1511–1518, doi:10.1021/acsestair.4c00068). The two reconcile if the
leakage is in end use and in transportation rather than in distribution
pipelines, which is consistent with the third strand: real-world measurements of
heavy-duty natural gas vehicles in China found them emitting about 90 percent
above the applicable emission limits (Da Pan et al., 2020, *Nature
Communications* 11, 4588, doi:10.1038/s41467-020-18141-0).

So the thesis's second hypothesis, that the urban signal is a natural gas
signal, has support from three directions. **The defect that remains is the
mechanism, not the attribution.** The thesis frames the problem as retrofitted
vehicles and faulty tailpipes; its own cited source frames it as emission
standards and their enforcement, and describes neither. `ERRATA.md` 5.3 records
that, and now records the support as well.

## Transport, background, and the meteorological feedback

Lin'an, in Zhejiang, is a WMO/GAW regional background station inside this
study's domain, and it is one of three regional stations China operates along
with Shangdianzi in Beijing and Longfengshan in Heilongjiang. In 2011 its
annually averaged CH4 mole fraction was 1,942 ppb against 1,861 ppb at
Waliguan, China's global station, a difference of 81 ppb that is the regional
enhancement this study's field is embedded in (China Meteorological
Administration, *China Greenhouse Gas Bulletin*, released January 2013). Its
methane record has been analysed for source attribution at several altitudes
(Shan et al., 2022, *Atmosphere* 13, 1206, doi:10.3390/atmos13081206).

Surface measurements in the domain give the seasonal contrast that matters most
for the calendar argument above. Atmospheric CH4 was observed at three sites in
Suzhou — Wujiang, Xiangcheng and Zhangjiagang — and the annual mean at
Zhangjiagang, in the north of the city, was 2,132.25 ppb, higher than Wujiang
and Xiangcheng by 17.31 and 4.66 ppb. All three followed a similar pattern,
concentration rising through spring and summer, peaking in mid-July in 2020 and
at the end of August in 2021, and falling towards winter (Guo et al., 2023,
*Atmospheric Pollution Research* 14, 101830, doi:10.1016/j.apr.2023.101830).

Surface concentration in this region therefore peaks during the flooded season.
The composite's soundings peak in October, after it. The composite's fitted
concentration cycle, however, peaks on 2 September, which is much closer to the
surface record than to the sounding distribution. Read together these say that
the column field and the surface record agree about when methane is high, and
that the annual composite's sounding distribution agrees with neither.

The last confound on the urban association is a physical one and it is the
subtlest. Two decades of urban expansion and forestation with cropland
reduction altered surface energy exchange across the Yangtze River Delta between
2001 and 2021, raising 2 m temperature and planetary boundary layer height and
reducing relative humidity and wind speed in urban areas, with maximum changes
reaching 0.2 °C, 31.1 m, −1.3 percent and −0.3 m/s, more pronounced at night
than during the day (Wang et al., 2026, *Journal of Environmental Sciences*,
doi:10.1016/j.jes.2025.07.021). A deeper boundary layer dilutes a surface source
and a slower wind concentrates it, so the sign of the net effect on a column is
not obvious and this study does not determine it. What matters is that
impervious fraction is correlated with the transport that dominates the field,
through a physical mechanism rather than through a sampling artefact, and in an
unknown direction. The urban coefficient in any model here is therefore not
cleanly interpretable as an emission signal even where it is non-zero.

## What the grounding establishes

The Yangtze River Delta is a high-signal region for this question. It sits
inside the seven provinces that carry 38.4 percent of China's agricultural
methane, its background station runs 81 ppb above the national global station,
and a tower inversion of the region in this study's own year found agricultural
soils to be the dominant driver of seasonal variability in atmospheric CH4.
There was a signal to find.

Three independent mechanisms nonetheless predict that a static land-cover
fraction would fail to explain an annual column field here, and none of them is
a defect in either predictor. The **water regime** determines emission with a
dynamic range larger than extent does, and no layer in this study represents it.
The **calendar** puts 82 percent of the composite's soundings outside the season
when the modelled crop is flooded, while the field's own fitted cycle peaks
inside it, so the annual mean averages a real seasonal signature against a
sounding distribution weighted against it. And the **meteorological feedback**
makes impervious fraction a proxy for boundary-layer depth and wind speed as
well as for emission, in a direction this study cannot sign. Three quarters of
the composite's soundings fall after the field's own seasonal peak.

**A fourth mechanism was added on 13 September 2026 and it is not a confound but
an omission.** A major coal mine methane source sits inside the lattice in
northern Anhui, in the province a gridded national inventory names as the
largest eastern emitter, and neither predictor represents it. It occupies the
same cells where the rice raster stops classifying. So part of the domain has an
unrepresented source and a missing predictor in the same place, which is a
different kind of problem from the three above: those explain why a
well-measured predictor would fail, and this one says part of the field was
never being predicted at all.

A negative result explained by three mechanisms and one omission is a different
kind of finding from a negative result left unexplained, and it is the form the
paper should take. The reproduction's own contribution is the measurement that the null
survives independently built predictors and both cross-validation schemes; this
grounding is what makes that measurement interpretable rather than merely
discouraging.

## What could not be verified

Eight premises carried into this note did not survive checking, and they are
listed so that the next person to meet them in a search snippet knows they were
tested.

The claim that the region holds about 16 percent of China's population could not
be sourced. Figures found ranged from 11 percent for a 150 million definition to
roughly 15.6 percent for a 220 million one, varying with where the region's
boundary is drawn, and no authority giving 16 percent was located. The number is
not used.

A national sectoral split of energy 44.8 percent, agriculture 40.2 and waste
11.85 could not be sourced to any primary work, and the figures found in its
place disagree with it and with each other. The 2024 split from Zhang et al.
(2026) is used instead because it comes from the inventory that reports it.

A claim that over 50 percent of China's methane emissions originate from urban
areas could not be sourced. The narrower and verified statement about waste
dominating in 38 named cities is used instead.

ChinaRiceCalendar's validated agreement for late-season rice is **0.90, not
0.96**. The paper's figures are 0.91, 0.94 and 0.90 for early, middle and late
season.

ChinaRiceCalendar's province-level day-of-year ranges for Anhui could not be
verified. The paper's text gives national generic windows and observed regional
means; its provincial classification table was not reachable. The Middle-Lower
Yangtze regional means are used, which is the right grain for this study and is
read from the paper.

Jiang et al. (2023) project a **17.1 to 9.2 percent** reduction from further
conversion under urbanisation, in extreme and most likely scenarios. The single
figure of 9.2 percent is the most likely scenario, not the only projection.

Zhu and Li (2024) exists and resolves but **none of its figures could be
verified**: 416 samples, 252.17 against 146.02 kg per hectare, and a factor of
1.52 are all unconfirmed and none is written above.

Zhao et al. (2026) exists and resolves, and its **numerical results could not be
verified**: a leakage rate of 3.5 percent with a range of 2.5 to 4.3, against
0.2 percent in inventories, comes from a press summary and not from the paper.

One figure in this note's own first draft understated itself and is corrected
here rather than silently: the sounding distribution is weighted **three** to
one towards the days after the field's fitted seasonal peak, not two to one.
75.5 percent of the soundings fall after day 245.8. The error was in the
direction of weakening the finding.

**Premises checked on 13 September 2026, when coal was added.** Verified: the
coalfield's 131.45 Mt of 2010 raw coal production, its 1.1 × 10¹² m³ of coalbed
methane, the 18-to-32 and 8-to-18 m minable seam thicknesses, the Qi'Nan gas
content of 4.58 to 12.33 m³ per tonne averaging 8.83, the national 15.8 and 11.8
Tg with a 6.77 m³ per tonne weighted factor and Shanxi at 35.5 percent, and the
gridded inventory's 0.25-degree resolution, 10,000-mine database, 25-fold and
2.5-fold comparisons against EDGAR, and its statement that Anhui and Liaoning
lead the east and north. Not verified: whether that inventory is distributed,
which could not be established because the paper is paywalled and two open
routes refused.

One premise was verified and is recorded here because the repository states it
two ways. The coastline's median sounding count against pure land's is 6 against
133 over covered cells, as `notes/decisions.md` says, and 2 to 3 against about
108 over all cells including the uncovered, as `data/processed/README.md` says.
Both are correct for different populations and neither file said which; this one
does, and the two quantities now have resolvers.

And one premise of this note's own earlier drafting failed. A growing-season
composite is **not** buildable from the existing checkpoint without a new
download, because the accumulator holds annual sums rather than per-granule
grids. The seasonal cycle is available; a growing-season mean is not.
