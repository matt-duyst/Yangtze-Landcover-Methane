# The urban layer's grounding

Draft material for a paper's introduction and discussion, the third of three
grounding records. [`notes/grounding-yrd.md`](grounding-yrd.md) establishes what
the region says about methane and rice;
[`notes/grounding-methods.md`](grounding-methods.md) establishes how a study of
this shape should be built and evaluated. **Neither says anything about the
impervious layer, which is half of this project's predictor set and the subject
of its second hypothesis.** This record is that gap.

Its conclusion, stated first because it reframes the layer's role: urban methane
is dominated by landfills, landfills are point sources known by facility
coordinates, and an impervious *fraction* is the wrong instrument for the
dominant sector. Where the layer does have a documented role is in allocating a
known city total across a city's interior, which is a real and unfilled need.

Every figure was checked against its source before it was written. Where a
figure could not be verified it is named as unverified and the number is not
written; the closing section lists every case. Numbers from this repository's
own artefacts are marked for
[`scripts/verify_claims.py`](../scripts/verify_claims.py) where a resolver
exists.

## Urban methane is not a sector, which is the structural difference from rice

Rice has a clean counterpart in the inventories: EDGAR and the Integrated
Methane Inversion both carry rice cultivation as a named sector, so a better
rice map substitutes directly for a worse one and the gain is measurable, as
[`notes/grounding-methods.md`](grounding-methods.md) records.

**There is no urban emission category.** The inventories resolve landfill, solid
waste, wastewater, oil and gas, coal mining and stationary combustion
separately, and impervious surface is a proxy for none of them individually. The
nearest thing to an urban sector is a *bundle*, defined by allocation method
rather than by process: one study of US cities defines "urban emissions as those
from population-driven activities including downstream gas, landfills,
wastewater treatment, and stationary combustion" (Wang et al., 2026, *Science
Advances* 12, doi:10.1126/sciadv.adz9308).

That difference governs everything below. For rice the question is whether a
better map improves a prior. For urban extent the question is prior: **which
sectors, if any, can an impervious fraction inform at all.** The answer turns
out to be specific and limited, and it is not the dominant one.

## The scale of the urban prior error, which is larger than rice's

Inverting TROPOMI observations over twelve major US urban areas found total
emissions **80 percent higher** than the US Environmental Protection Agency's
greenhouse gas inventory: 1.8 (1.6 to 2.0) Tg per year against the inventory's
1.0. The correction is not uniform. It runs from **32 percent (27 to 38) and 37
percent (33 to 40) lower in Los Angeles and Cincinnati to 3.9 (3.5 to 4.2) times
higher in Houston** (Wang et al., 2026).

**Landfills are the principal cause of the underestimate**, and the mechanism is
gas collection. Examining individual landfills with collection systems, the study
found "gas collection efficiencies averaging 38 % (range: 5 to 90 %), much lower
than their reported average of 70 % (range: 40 to 87 %)". The exception is
instructive: "The nine Los Angeles landfills in our analysis show high collection
efficiencies averaging 85 % (78 to 92 %)", and "if the mean collection efficiency
for US landfills in our analysis were raised to the level achieved in Los
Angeles (from 38 to 85 %), urban landfill methane emissions would be reduced by a
factor of 4". A separate global study finds landfill methane emissions
differentially underestimated worldwide (Wang, Y., et al., 2024, *Nature
Sustainability* 7, doi:10.1038/s41893-024-01307-9).

The composition is what makes landfills the story. Across the twelve urban areas
the inventory attributes **59 percent to landfills, 25 percent to downstream gas,
9 percent to wastewater and 7 percent to other anthropogenic sources**; the
posterior estimate shifts that to 62, 23, 8 and 7. Downstream gas here "includes
distribution from city gates to consumers and post-meter end use", so the
post-meter component the thesis's vehicle argument would live near is inside a
quarter share, not a majority one. Per city the landfill contribution runs from
28 percent (23 to 31) in Washington to 84 percent (70 to 94) in Miami, and
downstream gas from 7 percent (5 to 9) in Miami to 44 percent (37 to 52) in
Boston — so **the composition is a city-level property, not a constant**, which
is itself a reason a single fractional proxy cannot carry it.

For scale against the rice case: the urban prior error is 80 percent at the
aggregate and a factor of four at the extreme, where EDGAR's Chinese rice total
is wrong by a factor of two. **The urban prior is the worse of the two**, which
makes it the more valuable to fix and the less tractable to fix with a fraction.

## The separability finding, which is what constrains an urban fraction

This is the decisive result for the layer and it is worth quoting at length.

"In the gridded GHGI, landfill emissions are mapped on the basis of GHGRP
facility coordinates and are spatially distinct from other sectors. Posterior
error correlation coefficients r between landfills and other sectors are **below
0.35**, implying that less than 35 % of the correction attributed to landfills
could be obfuscated by other sectors. This gives us some confidence in
quantifying emissions from landfills. Emissions from downstream gas activities,
wastewater treatment, and stationary combustion ... are all **allocated on the
basis of population**, and this results in posterior error correlation
coefficients between these three sectors ranging from **0.45 to 0.87**. Our
ability to separate these three sectors in the inversion is therefore limited,
and their relative allocation is heavily weighted by the prior information" (Wang et al., 2026).

**The consequence for an impervious fraction is direct and unflattering.** The
sectors that can be quantified are the ones mapped on facility coordinates. The
sectors that cannot are the ones allocated by a population-like surface, and
they cannot be separated *from each other* precisely because they share that
surface. Impervious fraction is another population-like surface. Using it to
allocate downstream gas or wastewater adds a fourth correlated proxy to three
that already correlate at 0.45 to 0.87; it does not break the degeneracy, it
joins it.

**The route that works for the dominant sector is coordinates, not fractions.**
That is a finding about what data this project would need rather than about how
to analyse the data it has, and it points at the facility databases recorded in
[`notes/dataset-leads.md`](dataset-leads.md).

## Where impervious surface does have a documented role

The role is within-city allocation of a total that is already known, and there is
published precedent plus a measured reason to want it.

The precedent: an emissions dataset for Southeast Asia downscales EDGAR
administrative totals to 4,413 admin-3 units across eleven countries for 2000 to
2020 "by integrating nighttime lights, impervious surface information, and
urban–rural settlement distributions" (Chen and others, 2026, *Scientific Data*
13, doi:10.1038/s41597-026-07320-1). **That work downscales CO₂, not methane**,
and the difference matters: a proxy that tracks diffuse combustion need not track
point-like methane sources. It establishes that impervious surface is used for
this purpose, not that it works for this gas.

The measured reason to want it comes from the gas sector and is the sharpest
statement in this record. An inventory of China's oil and gas methane finds that
a widely used global product "allocated gas distribution emissions to grid cells
**only based on population densities without using an urban land cover map**,
which may misrepresent emission hotspots, particularly in rural China where the
gas distribution pipeline penetration rate remains low", and that because it
"disaggregated gas distribution emissions to both urban and rural areas based on
population density", it underestimates "emissions in urban areas with higher
populations" (Luo and others, 2025, *Nature Communications* 16,
doi:10.1038/s41467-025-58237-z). **The named deficiency is the absence of an
urban land cover map.** That is precisely what this project's impervious layer
is, and it is the clearest evidence anywhere in these three grounding records
that the layer answers a question the field has actually posed.

The limit is equally clear and comes from the point-source problem. Emissions
from point or line sources — landfills, wastewater plants, distribution leaks —
are spatially diluted over a large grid cell, and downscaling cannot recover the
original misallocation or supply a source the inventory omitted. **So urban
extent improves the allocation of a known total; it cannot recover a source the
inventory placed wrongly.** Since the US work establishes that misplaced and
under-reported landfills are the dominant urban error, the sector the layer can
help with is not the sector that needs help most.

## How the proxies actually compare, which favours this layer

The section above stands: impervious fraction is another population-like surface
and joins the degeneracy rather than resolving it. What it did not record is
**how the candidate proxies compare to one another**, and that comparison comes
out in the layer's favour. Each of the three fails differently, which is an
argument for combining them rather than for choosing one.

**Read this as a statement about the proxies' properties and not as support for
an association this repository can still claim.** Tier 0 changed the stakes. Of
seventy-two reported correlations, twenty-seven no longer reach significance
once degrees of freedom are corrected for spatial dependence, including **every
weighted land-cover association and every partial controlling for albedo on the
operational field**. So the argument below is that impervious fraction carries
information population grids do not. It is not an argument that this project
detected an urban methane signal.

### Population grids fail at change, which is what a historical series needs

Six time-series gridded population datasets — CnPop, GHS-POP, GlobPop, GPWv4,
LandScan and WorldPop — were evaluated against Chinese township-level census
data for 2010 and 2020. Most showed high cross-sectional accuracy, with
Pearson's r against census above 0.8, but **their ability to represent decadal
population change was severely limited**, with substantial inaccuracies in
identifying decline trends and weak performance on change magnitude (Li et al.,
2026, *Humanities and Social Sciences Communications*,
doi:10.1057/s41599-026-07688-w). The paper's own framing is that cross-sectional
accuracy does not imply reliability of change.

That is the property a 2000-to-2018 series needs and the one these products
lack. A prior allocated on a population grid for 2000 and again for 2018 would
carry the difference between two independently unreliable change estimates.

### And they underrepresent rural population systematically

Validated against reported resettlement from 307 large dam construction
projects in 35 countries, all the datasets examined showed significant negative
biases: **−53 percent for WorldPop, −65 for GWP, −67 for GRUMP, −68 for
LandScan and −84 percent for GHS-POP** (Láng-Ritter, Keskinen and Tenkanen,
2025, *Nature Communications*, doi:10.1038/s41467-025-56906-7). Even the most
accurate underestimates rural population by half.

**This finding is contested and the record should say so.** WorldPop's team
published a public rebuttal disputing the claim of systematic rural
underrepresentation. That is a live disagreement rather than a settled result,
and it is recorded the way this register records the rice-paddy exchange — both
sides named — rather than by picking the side that suits the argument.

Why it matters here even so: much of this study area is rural, and a prior
allocated on a surface that may underestimate rural population by half would
misplace emissions systematically, in the direction of under-attributing them to
the paddy landscape.

### But impervious alone fails in dense cores

A model estimating Chinese residential population from impervious surfaces
found Shanghai's downtown census at **6,008,068** persons against model
estimates ranging from **1,435,820 to 1,065,729** across fourteen grid
resolutions, and states that the population "was greatly underestimated in the
model without taking the vertical building information into consideration" (Wei
et al., 2021, *International Journal of Remote Sensing* 42, 2303–2326,
doi:10.1080/01431161.2020.1841322).

So the layer's failure mode is the opposite of the population grids': they lose
the countryside, it loses the vertical dimension of the city. A factor of four
to six in Shanghai's downtown is not a small correction, and Shanghai is one of
this project's four provinces.

### And nighttime lights, the incumbent proxy, fail across these years

DMSP-OLS covers 1992 to 2013 and VIIRS begins in 2013, so **an allocation across
2000, 2010 and 2018 crosses a sensor boundary**. The older instrument lacks
onboard calibration, carries 6-bit quantisation and coarse resolution, and
suffers saturation in bright cores and blooming into their surroundings; VIIRS
has onboard calibration and a much broader dynamic range. An intercalibration is
therefore required for any series spanning the boundary, which is a step this
project's years cannot avoid.

**One premise about the intercalibration products could not be verified** — that
one overestimates in urban cores while another underestimates there — and no
number is written for it. What is verified is that the coarse resolution of both
instruments cannot separate impervious surface from other features in the
transition between urban and suburban, which is the same peri-urban zone where
this study's land-cover gradients live.

### The synthesis, which is the argument for combining

Each proxy fails somewhere different: population grids at change and in the
countryside, impervious surface in the vertical, nighttime lights at the sensor
boundary and in the peri-urban transition. **That is an argument for using them
together rather than choosing between them**, and it is what the Southeast Asian
downscaling recorded above actually did — nighttime lights, impervious surface
information and urban–rural settlement distributions integrated in one
allocation (Chen and Ba, 2026, doi:10.1038/s41597-026-07320-1).

For this project the practical form of that conclusion is narrow: impervious
fraction is the right proxy for *where built surface changed between 2000 and
2018*, which is the question the thesis asked of it and the one the population
grids demonstrably cannot answer. It is the wrong proxy for how much methane
that built surface emits, for the reasons the separability section gives.

## Building volume, the dimension the layer does not have

The Shanghai underestimate above names the missing variable explicitly:
vertical building information. It exists, at this project's resolution, for all
three of its years.

**A 30 m annual building height dataset for China covering 1990 to 2019** was
published as Zhang et al. (2026), *Mapping three decades of urban growth in
China: a 30 m annual building height dataset (1990–2019)*, *Earth System Science
Data* 18, 5329, doi:10.5194/essd-18-5329-2026. Annual, 30 m, and its span
contains 2000, 2010 and 2018 — which no other building-height product manages.

The alternatives trade coverage against detail:

* **3D-GloBFP**, the first global three-dimensional building footprint dataset,
  covering 1.66 billion buildings and validated in China against CNBH (Che et
  al., 2024, *Earth System Science Data* 16, 5357,
  doi:10.5194/essd-16-5357-2024).
* **CNBH-10m**, Chinese building height at 10 m for 2020, with a root mean
  square error of **4.65 m** validated across **63 cities** (Wu et al., 2023,
  *Remote Sensing of Environment* 291, 113578, doi:10.1016/j.rse.2023.113578).
  One year only.
* **CMAB**, a national multi-attribute building dataset at building-instance
  level (Zhang, Zhao and Long, 2025, *Scientific Data* 12,
  doi:10.1038/s41597-025-04730-5).

**The trade-off they state is this project's own**: fine-granularity products
are cross-sectional, and the longitudinal ones are coarse. The annual 30 m
height dataset is the only candidate that resolves the study's three years, and
it carries height rather than the richer attributes.

### They disagree with each other, which is the GAIA–GISA problem again

CNBH is reported to underestimate heights in central business districts and
overestimate low-rise buildings in old urban areas, and a comparison found
another product misidentifying contiguous 20-to-36 m buildings as high-rise.
**Neither direction could be verified to a primary source in this pass** and so
neither is written as a number; what is recorded is that the products disagree
and that the disagreement is structured by urban form rather than random.

That is the same shape as the impervious problem this repository already has.
`ERRATA.md` 7.5 and `data/processed/README.md` record GAIA and GISA crossing
over — GISA finding 19.9 percent less impervious surface here in 2018 and 20.7
percent more in 2000 — and the lesson taken from it was that a second product
with different errors is worth more than a better single product. The same
lesson applies before any height layer is adopted: two of them, or none.

### Why volume matters for methane rather than for urban form

A residential tower and a single-storey industrial shed have **identical
impervious footprints and different gas connections and waste generation**. That
is the whole argument, and it is about composition rather than about density: the
sectors the urban bundle contains — downstream gas to households, municipal
waste, wastewater — scale with residents and their consumption, not with paved
area.

Height is an indirect route to that and **CMAB carries building function
directly**, which would separate residential from industrial without inferring
it from volume. For the specific question this project's second hypothesis asks
— whether urban methane tracks gas use — a function layer is closer to the
mechanism than either footprint or height.

## China's waste sector, where this project's years bracket the arc

The timing is unusually favourable to this project and unusually awkward for its
framing.

China launched the Waste-Free City initiative in 2018 and a national
waste-sorting campaign the following year. **An 84.7 percent reduction in
municipal solid waste methane emissions has been achieved in Chinese cities since
2017, with megacities and large cities accounting for 80 percent of those
gains**, driven by the shift from landfill to incineration and by gas recovery
(Gao et al., 2026, *Journal of Environmental Management* 398, 128450,
doi:10.1016/j.jenvman.2025.128450). Greenhouse gas emissions from the sector
peaked at 70.6 Tg CO₂-equivalent in 2018 and fell to 47.6 Tg by 2021 (Ma et al.,
2024, *Environmental Science & Technology* 58, 11316–11326,
doi:10.1021/acs.est.4c00408).

**2018 is the peak year, and 2018 is this project's analysis year.** The three
thesis years therefore straddle the whole arc: 2000 near the start of the rise,
2010 mid-rise, 2018 at the maximum. An impervious layer that grows monotonically
across those three years is tracking a waste-methane signal that rose and then
turned, so the two series diverge after the study period in a way a
cross-sectional analysis of 2018 cannot see and a paper should not imply.

A nationwide site-level study supports the arc with facility detail. It built "a
database of site-specific information for more than 300 major MSW landfills",
estimated emissions by IPCC first-order decay at 1.015 Mt in 2005 rising to a
peak of 2.161 Mt around 2015 and falling to 1.98 Mt by 2023, and compared its
inventory against hyperspectral satellite observations for three landfill sites,
finding that "satellite-detected instantaneous emissions consistently exceed
inventory-based averages", which quantifies a systematic bias in current IPCC
models that underestimate fugitive leaks (Zhang, S., et al., 2026, *Journal of
Environmental Management* 399, 128672,
doi:10.1016/j.jenvman.2026.128672).

**The collection-efficiency literature disagrees with itself and the
disagreement is not resolved here.** One account holds that large Chinese
landfills have HDPE covers and gas collection averaging around 80 percent;
another that collection systems in many landfills were inadequately equipped or
operated; and the US satellite work measured 38 percent against a reported 70.
Neither Chinese figure could be verified to a primary source in this pass, so
neither is written as a number. What can be said is that the one place where
collection efficiency was measured rather than reported, it was roughly half the
reported value, and that the same study notes US landfills measured at several
times their reported emissions.

One point source in this study area deserves naming. **Shanghai Laogang Phase
IV** sits on reclaimed land extending into the East China Sea in Pudong New
Area, 4.2 km by 800 m for a total of 361 hectares, with a capacity of 80 million
cubic metres and an expected life of 45 years, described by its operator as the
largest landfill in China by capacity and daily intake. Those figures come from
operator documentation rather than a peer-reviewed source and are recorded as
such. Its location matters twice over: it is inside the lattice, and it is on
reclaimed coastal land, which is exactly where this project's composite coverage
is worst — the coastline's median sounding count is
6<!--#composite.coast_median_soundings--> against
133<!--#composite.land_median_soundings--> for cells that are wholly land.
**China's largest landfill sits in the part of this project's field that the
instrument sees least.**

## The gas sector, which is hypothesis 2 and which the thesis got half right

The thesis attributes urban methane to natural gas vehicles. The attribution to
natural gas is well supported; the vehicle mechanism is not the one that grew.

**The sector's growth over this project's study interval is large and
documented.** China's methane emissions from oil and gas systems "increased by
about 7 times" from roughly 0.5 Tg per year in 1990 to about 4.0 Tg in 2022, in
a database with 80 percent of emissions tracked as refineries, facilities,
pipelines and field sources (Luo and others, 2025). The distribution
infrastructure grew in step: "from 2010 to 2019, the length of the gas supply
pipelines in the urban areas of China has increased approximately threefold from
298.6 to 935.6 million meters including 82 % in the city and 18 % in the county
seat", and "the CH₄ leakage from those pipelines is not actively monitored"
(Wang, F., et al., 2022, *Scientific Reports* 12,
doi:10.1038/s41598-022-19462-4). The same study's inversion finds that
north-eastern China "contributes the most to the growth rate (0.77 Tg CH₄ yr⁻¹)
of the methane emission growth rate of China (0.87 Tg CH₄ yr⁻¹) and is largely
attributable to the growth in natural gas use".

**The leaks have been found and characterised.** A measurement campaign across
roughly 4,000 km of natural gas distribution pipelines in 20 Chinese cities used
detection vehicles to identify 220 leak areas, within which sniffer canines
pinpointed 432 individual release sources; underground steel pipelines and
aboveground risers were particularly prone, and leak density varied notably
between cities (Lu et al., 2025, *Nature Cities*,
doi:10.1038/s44284-024-00183-w). In this region specifically, mobile
measurements in Hangzhou found the distribution system to be a low emitter
(Zhao et al., 2024, already in the register).

**The vehicle numbers are the part the thesis leaned on, and they do not carry
the growth.** Heavy-duty natural gas vehicles in China were measured at about 90
percent above their applicable emission limits, and the same work's life-cycle
analysis gives a well-to-pump methane leakage rate of 1.65 ± 1.05 percent of
natural gas consumed — "about the same as the CH₄ emission factor of light-duty
NGVs and ... 40 % lower than the CH₄ emission factor of heavy-duty NGVs" (Da Pan
et al., 2020, already in the register). So vehicle emissions are real and above
standard, but they are of the same order as the leakage that occurs before the
gas reaches a vehicle at all, and the threefold infrastructure growth over this
project's interval happened in pipelines rather than in tailpipes.

**State the conclusion for hypothesis 2 plainly: right in direction, wrong in
mechanism.** Urban methane from natural gas in this region is real, large, and
growing across 2000 to 2018. But the growth is in distribution infrastructure,
the leakage in it is not actively monitored, and the thesis's stated mechanism of
retrofitted vehicles and faulty tailpipes is neither what its cited source
reports nor where the growth occurred. `ERRATA.md` 5.3 already records the
mechanism defect; this record supplies the alternative mechanism that the
evidence supports.

## What the urban grounding establishes

**Urban methane is a landfill problem before it is anything else.** In the one
place where twelve cities have been inverted against an inventory, landfills are
59 to 62 percent of the total and the principal cause of an 80 percent
underestimate, with measured gas collection at roughly half its reported
efficiency.

**The dominant sector needs facility coordinates, not fractions.** Landfills are
quantifiable precisely because they are mapped on facility coordinates and so
have posterior error correlations below 0.35 with everything else. The sectors
allocated on population correlate at 0.45 to 0.87 with one another and cannot be
separated; an impervious fraction is another such surface and joins that
degeneracy rather than resolving it.

**Impervious extent has a documented role, and it is within-city allocation of a
known total.** The clearest evidence is a named deficiency in a global gas
inventory: it allocated distribution emissions by population density "without
using an urban land cover map". That is a question this project's layer could
answer. It is not the question the thesis asked of it.

**2018 is the pivot year for Chinese waste methane**, the peak of a rise that has
since fallen 84.7 percent in cities, with 80 percent of the fall in the largest
ones. This project's three years bracket the arc, and a monotonic impervious
series tracks a non-monotonic emission series.

**And the gas sector supports hypothesis 2 through a different mechanism than the
thesis proposed** — unmonitored leakage from a distribution network that tripled
in length between 2010 and 2019, rather than vehicles, whose emission factors are
comparable to the upstream leakage rate.

The honest summary for a paper is that the urban half of this project's predictor
set is a defensible proxy for the urban source *bundle*, as `ERRATA.md` 5.3 now
says, but that the bundle is dominated by a sector whose spatial structure a
fraction cannot represent. That is a stronger and more specific statement than
"impervious surface is a crude proxy", and it is the one the literature supports.

**Four things were added on 13 September 2026 and two of them change the
summary.** Impervious fraction turns out to be the *best available* proxy for
where built surface changed across these years, because population grids fail at
exactly that and nighttime lights cross a sensor boundary inside the study
period — so the layer is better than its alternatives at the thing it was used
for, while remaining wrong for the thing it was asked to predict. And the
detectability question has a number: a single large landfill sits below the
threshold at which this composite could constrain it independently of the prior,
so the dominant urban sector is not merely spatially unrepresentable by a
fraction but individually invisible to this field.

The other two are a missing dimension and a caution. Building height exists
annually at 30 m for all three of this project's years, and building *function*
exists at instance level, which is closer to the gas-and-waste mechanism than
either footprint or height. And the gas share of urban methane is
method-dependent by a factor of two to four, with the ethane-tracer method that
produces the highest shares being the one with the narrowest spatial scope —
which is the method behind this region's own 3.5 percent leakage figure.

## The synthesis anchor, which is the field's own statement of its state

Added 14 September 2026. Everything above this point is built from primary
studies, which is the right way to build it and leaves one thing missing: **a
review-level statement of where the field is**, of the kind a paper's
introduction needs and cannot assemble from twelve individual inversions. This
section is that statement, and it says three things — that the field's central
problem is credibility rather than measurement, that urban methane is
underestimated by a factor rather than a percentage, and that the underestimate
is growing.

### The credibility problem, which is named as such

The framing statement is eight years old and has not been superseded. Reviewing
approaches to measuring, monitoring and inventorying anthropogenic methane in
the United States at the request of four federal agencies, the National Academies
concluded that "**verifiability is the bedrock upon which inventories should be
built if they are to be widely applicable to policy needs**", and that as
constructed the national inventory does not have it: "it is very challenging to
test the GHGI against top-down estimates (i.e., verify the GHGI) owing to its
high degree of spatial (national) and temporal (annual) aggregation" (National
Academies of Sciences, Engineering, and Medicine, 2018, *Improving
Characterization of Anthropogenic Methane Emissions in the United States*,
National Academies Press, doi:10.17226/24987). The report also records that "in
some cases, top-down estimates of emissions and bottom-up inventories have
significantly differed, leading to reexamination of estimates from both
approaches".

**Read that as the reason this whole class of work exists.** The problem is not
that nobody has measured urban methane; it is that an inventory aggregated to a
nation and a year cannot be checked against the atmosphere at all, so a
disagreement cannot be localised to a sector or a city. Every finding in this
record — the twelve-city inversion, the gas-collection efficiencies, the
separability coefficients — is an instance of the verification the 2018 report
said was missing, arriving at city scale because that is the scale at which the
check becomes possible.

The current state of that verification has a number. A review of city-scale
top-down methane inversion covering inventories, observations, transport models
and assimilation methods "highlights the significant discrepancy between top-down
inversion results and bottom-up inventory estimates at the city scale, with
**inversion uncertainties ranging from 11% to 28%**" (Li, X., Zhang, Y.,
de Leeuw, G., Yao, X., He, Z., Wu, H., and Yang, Z., 2025, *A Review of
City-Scale Methane Flux Inversion Based on Top-Down Methods*, *Remote Sensing*
17, 3152, doi:10.3390/rs17183152). **Eleven to twenty-eight percent is the
inversion's own uncertainty**, not the discrepancy it measures, so it is the
floor below which a city-scale disagreement cannot be resolved by this method.

Two framing statements from the same review bear on findings already in this
record. The first: the top-down approach "enables higher spatiotemporal
resolution and the evaluation of prior inventories **but struggles to attribute
emissions to specific categories**". That is the separability finding stated as a
general property of the method rather than as a result of one US inversion, and
the review's proposed remedy — "applying isotopic analysis to distinguish CH4
sources" — is a measurement this project has no access to and which no
fractional proxy substitutes for. The second: **agricultural soil activity, with
its seasonal and monthly variability, is the largest source of uncertainty in
anthropogenic methane inversions.** For a project whose two predictors are urban
extent and rice extent, the review names the agricultural half as the larger
uncertainty, which is the opposite of the ordering the urban record's own
prior-error comparison suggested.

### The inventory gap, which runs opposite to rice

**Field studies of urban methane find inventories low by a factor, and the
factor is consistent across studies.** "Field studies quantifying methane
emissions in urban areas have found that official bottom-up inventories can
**underestimate methane emissions by a factor of 2 to 3**", with three separate
campaigns cited for it, and the implication drawn is that "there are substantial
unexplained urban sources of methane" (Long, H., Tsivlidou, M., Ricketts, H.,
and Allen, G., 2026, *Satellite-based global monitoring of urban-scale methane
emissions*, EGUsphere preprint, doi:10.5194/egusphere-2026-2570).

**That source is a preprint and is recorded as one.** Discussion opened 20 May
2026; it is CC-BY-4.0 and not peer-reviewed. It is used here because the factor
of two to three is a summary of three cited field campaigns rather than the
preprint's own result, and because the preprint's own result qualifies it
usefully. Testing an advanced mass-balance approach on three megacities for 2021
to 2023, the authors find satellite-derived emissions "corresponding to factors
of approximately 0.1-2.0, 0.3-2.1, and 5.1-9.2 times the inventory estimates" for
London, Los Angeles and New York respectively. **The ratio is not even
consistently above one.** So "two to three times" is the field's central
tendency and not a property of any particular city, which is the same lesson the
twelve-city composition figures teach: the discrepancy is a city-level property.

**The direction is the contrast with rice, and it is the sharpest single reason
to treat this project's two predictors asymmetrically.**
[`notes/grounding-rice.md`](grounding-rice.md) establishes that EDGAR's Chinese
rice total is double GRPI's — too high, not too low — and that the two Chinese
sub-regional inversions correct rice in opposite directions depending on where
the prior's map put the paddy. Urban has no such ambiguity: every campaign
summarised above finds the inventory low, the twelve-city inversion finds it 80
percent low in aggregate, and the cause is identified as missing and
under-reported landfill emissions. **So the urban prior is biased and the rice
prior is misplaced**, and those are different defects needing different
remedies. A better rice map fixes allocation; nothing about an urban extent map
fixes a missing source.

### And the gap is growing, measured over this project's own satellite record

The most recent and most directly comparable result tracks the discrepancy in
time rather than at one moment. Using a tracer–tracer approach on TROPOMI
methane and carbon monoxide, Whiting, E., Plant, G., Kort, E. A., Aben, I.,
Biener, K. J., Leguijt, G., and Maasakkers, J. D. (2026), *Space-based
observation of global increase in urban methane emissions from 2019–2023*,
*Proceedings of the National Academy of Sciences* 123(16),
doi:10.1073/pnas.2504211123, measure "methane emissions of 92 global cities,
including their broader metropolitan area", finding "aggregate emissions of 31.2
Tg CH4/y (95%CI: 22.3, 40.4 Tg CH4/y) in 2023, equivalent to ~10% of the global
anthropogenic methane budget".

**Seventy-two of those cities have enough data to track**, 51 in the C40 network
and 21 outside it. Their emissions "weakly declined in 2020 followed by steady
growth, with a 2.3 Tg aggregate increase over 4 y", and the growth from 2020 to
2023 is 10 percent (95 percent CI 2 to 17) for C40 cities against 12 percent (CI
−1.5 to 25) for non-C40 cities — **statistically indistinguishable, in a set of
cities that "have largely pledged 34% reductions by 2030"**. The authors'
conclusion is the one this section exists to record: "**Inventories fail to
capture observed growth, suggesting urban emissions are not well characterized,
and mitigation approaches may not be optimally designed.**"

Two qualifications belong with it, both from the paper itself. The growth
"contributes minimally to the recent atmospheric methane surge", so this is a
policy-relevant finding rather than a global-budget one. And the detectability
claim is explicit: "Emission reductions of this magnitude would be detectable
with the space-based approach used in this work" — reductions of 34 percent, at
city scale, by the tracer–tracer method. Read against this record's own
detectability finding, that a single large landfill sits below the threshold at
which this composite could constrain it, the two are consistent: a whole city's
third is detectable where one facility is not.

**The observational geography is the last piece, and it is unfavourable to this
domain.** The same preprint that supplies the factor of two to three states that
"in poorly observed regions (e.g. India, China), where most of the global
population resides, measurement-led validation of national emissions is even
more challenging" (Long et al., 2026). The field's verification effort has
happened where the observations are, which is North America and Western Europe;
the cities where most people live are the ones least checked. **This project's
domain is in the second group**, which is an argument for the work and a warning
about what can be claimed from it in the same sentence.

### What the anchor adds to the layer's conclusion

Nothing above changes the separability finding or the conclusion that an
impervious fraction is the wrong instrument for the dominant sector. What it adds
is the reason the question is worth asking at all, in the field's own words: an
inventory that cannot be verified is the acknowledged problem, city scale is
where verification becomes possible, urban methane is low in inventories by a
factor of two to three, the gap is growing at about 10 percent over four years
against pledges of 34 percent reductions, and the regions where most people live
are the least observed. **A paper's introduction can be written from those five
sentences**, and this record could not previously supply them.

## What could not be verified

Eight premises carried into this record did not survive checking, in addition to
the seven recorded in the methods grounding's own amendment section. **Three
more failed in the 13 September 2026 amendment and are listed at the end.**

**The sector composition of an average US city** — landfills 40 percent, gas
distribution 9 percent including 4 percent post-meter, wastewater 6 percent —
appears in no form in the paper it was attributed to, which gives 59 / 25 / 9 / 7
in the inventory and 62 / 23 / 8 / 7 in the posterior for the twelve urban areas
together. The verified figures are used and the direction of the premise is
confirmed more strongly than it claimed.

**"Up to 200 percent underestimations for individual landfills worldwide"** is
not that paper's finding. It is cited there to Wang, Y., and others (2024, *Nature
Sustainability* 7), whose title confirms the direction. The magnitude is not
written here because it was not read in its own source.

**The paper is in *Science Advances*, not *Science*.**

**The Southeast Asian downscaling is of CO₂, not methane**, and the claim that
gradient boosting gave the best out-of-fold fit could not be verified. The use
of nighttime lights, impervious surface information and urban–rural settlement
distributions is verified and written.

**The Chinese provincial framework integrating nine proxies** including
impervious surface area, road networks and points of interest could not be
located, and neither could the ODIAC nighttime-light saturation figures — median
differences of 47 to 84 percent against bottom-up at 1 km, and whole-city
differences from −1.5 percent in the Los Angeles Basin to +20.8 percent in Salt
Lake City. None is written. The qualitative point that a nighttime-light-only
proxy saturates is plausible and unsourced here.

**The provincial landfill methane series** — 1.0 Mt in 2003 rising to 1.8 Mt in
2019 then falling to 1.6 Mt by 2021 — could not be verified. A different and
verified series exists from the site-level study: 1.015 Mt in 2005, a peak of
2.161 Mt around 2015, and 1.98 Mt in 2023. The two are not the same series and
the verified one is used.

**The MSW treatment composition** — 52 percent landfill, 45 percent incineration
and 3 percent composting on one account against 85 percent incineration on
another, and kitchen waste at 52.8 to 65.3 percent of MSW with over 50 percent
moisture — could not be verified to primary sources. The qualitative shift from
landfill to incineration is verified and written; the shares are not.

**The Chinese gas-collection efficiency figures** of around 80 percent for large
landfills with HDPE covers, and the contrary claim of inadequate equipment and
operation, could not be verified to primary sources. The disagreement is
recorded without numbers.

Two premises were refined rather than failed. The oil and gas database's
coverage of **347 prefecture-level cities** from the China Urban Construction
Statistical Yearbook could not be confirmed, though the database, its 1990 to
2022 span, its roughly sevenfold growth from 0.5 to 4.0 Tg, and its
population-density disaggregation all were. And the GHGSat waste survey covers
**130 urban areas in 47 countries** over six continents with 1,447 clear-sky
observations of 151 sites, of which the Shanghai wastewater plume is verified as
present — but it was "filtered from the analysis", so it is an example in the
dataset rather than a quantified emission.

### The 13 September 2026 amendment's own failures

**A fifth bad DOI, and a new failure mode.** The population-change evaluation
was carried as `10.1038/s41599-026-07688-w`. That does not resolve at all: the
article number is right and the **prefix is wrong**, since *Humanities and
Social Sciences Communications* registers under 10.1057 rather than 10.1038.
The correct DOI is `10.1057/s41599-026-07688-w`. Four earlier bad DOIs resolved
confidently to the wrong paper; this one resolves to nothing, which is the safer
of the two failures and still a failure.

**The nighttime-light intercalibration disagreement could not be verified.**
That one intercalibration product overestimates in urban cores while another
underestimates there is not written. The sensor discontinuity, the older
instrument's saturation and blooming, and both instruments' inability to
separate impervious surface in the peri-urban transition are verified and
written.

**The building-height products' disagreement could not be verified to a primary
source.** That CNBH underestimates in central business districts and
overestimates low-rise buildings in old urban areas, and that another product
misidentified contiguous 20-to-36 m buildings as high-rise, are recorded as
directions without numbers. What is written is that the products disagree and
that the disagreement is structured by urban form.

Two further items were verified and are recorded with a qualification rather
than as settled. The rural-underrepresentation finding is **contested**: WorldPop
published a rebuttal disputing it, and both sides are named above. And *Evolving
Cityscape*, offered as a building dataset covering 106 Chinese cities for 2018 to
2023, could not be located at all and is not recorded anywhere.

### The 14 September 2026 synthesis anchor's own corrections

Nothing in the anchor failed outright, and three things needed correcting before
they could be written.

**The credibility report is 2018, not 2024.** It was carried as a recent
National Academies statement. The report is *Improving Characterization of
Anthropogenic Methane Emissions in the United States*, published July 2018,
`10.17226/24987`. Its framing has not been superseded and the age is recorded
rather than hidden, because an eight-year-old statement that the inventory cannot
be verified is a stronger claim about the field than a fresh one would be.

**The city-scale inversion review is 2025, not 2026**, which an earlier pass had
already found and this one confirms: `10.3390/rs17183152` is *Remote Sensing* 17,
3152, dated 2025.

**Two different papers were conflated in the search results and both are now
separated.** The 92-city measurement and the 72-city trend belong to Whiting et
al. (2026) in *PNAS*; the factor of two to three and the poorly-observed-regions
statement belong to Long et al. (2026), a Copernicus preprint on three megacities.
A search for the trend returned the preprint's text as though it were the *PNAS*
paper's, which would have attributed a three-city mass-balance study's figures to
a 92-city tracer–tracer study. Both are cited, separately, with the preprint
marked as a preprint.

**One figure from the trend paper is not written.** That 2023 urban emissions
were 6 percent above 2019 and 10 percent above 2020 while inventories rose only
1.7 to 3.7 percent since 2020 appears in the university's press release and in
secondary coverage, not in the paper's abstract, which gives the 2020-to-2023
growth as 10 percent for C40 cities and 12 percent for non-C40. **The abstract's
figures are written and the press release's are not**, which is the same rule
this record applied to the sector-composition premise that turned out not to be
in its paper.
