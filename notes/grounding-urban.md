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

## What could not be verified

Eight premises carried into this record did not survive checking, in addition to
the seven recorded in the methods grounding's own amendment section.

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
