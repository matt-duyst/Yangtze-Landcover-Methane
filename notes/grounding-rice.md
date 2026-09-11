# The rice layer's grounding

Draft material for a paper's introduction and discussion, and the last of the
three layer records. [`notes/grounding-yrd.md`](grounding-yrd.md) establishes
what the region says about methane; [`notes/grounding-methods.md`](grounding-methods.md)
establishes how a study of this shape should be built and evaluated;
[`notes/grounding-urban.md`](grounding-urban.md) establishes what an impervious
fraction can and cannot inform. **The rice layer is the other half of this
project's predictor set and the subject of its first hypothesis, and until now
its findings lived scattered across the other two records** — the calendar and
the water regime in the region record, the emission-factor chain and the
reference polygons in the methods record — with no single account of what the
literature establishes about rice extent as a predictor of methane. This record
is that account.

Its conclusion, stated first because it governs how the layer should be
described: **rice extent is a weak predictor of rice methane by the field's own
explicit account, and the field says so in a review rather than leaving it to be
inferred.** Emissions vary by an order of magnitude at constant extent, the
things that move them are water regime, temperature, organic amendments and
cultivar, and none of them is visible in a map of where paddy is. What the
literature does support is narrower and still useful: a better rice *map*
improves a prior's spatial distribution, which is a different and documented
gain from improving its magnitude.

Every figure was checked against its source before it was written. Where a
figure could not be verified it is named as unverified and the number is not
written; the closing section lists every case, including four figures carried
into this pass that did not survive. Numbers from this repository's own
artefacts are marked for [`scripts/verify_claims.py`](../scripts/verify_claims.py)
where a resolver exists.

## The thesis's own method, and the maps that already exist

The 2023 thesis mapped paddy rice with the phenology- and pixel-based paddy rice
mapping algorithm of **Zhu, L., Liu, X., Wu, L., Liu, M., Lin, Y., Meng, Y.,
Ye, L., Zhang, Q., and Li, Y. (2021)**, *Detection of paddy rice cropping
systems in southern China with time series Landsat images and phenology-based
algorithms*, *GIScience & Remote Sensing* 58, 733–755,
`10.1080/15481603.2021.1943214`. `notes/decisions.md` records the
reimplementation route that was discussed and not taken.

**What that record did not establish is that the maps themselves already
exist.** The paper's contribution is to "improve the phenology- and pixel-based
paddy rice mapping (PPPM) algorithm by simultaneously considering the phenology
signatures in the rice transplanting and heading periods", and on that basis the
authors "generated annual maps of SCR and DCR in southern China with image
collection of Landsat 5, 7, and 8 from 1999 to 2019 using the Google Earth
Engine platform". Single- and double-cropping rice, annually, for twenty-one
years, by the algorithm the thesis used. Overall accuracies run from 81.0 to
98.1 percent depending on the area of interest, and total rice area falls from
208,614.6 km² in 2000 to 171,474.3 km² in 2019.

**One of the two open questions this record was expected to carry is answered by
the paper itself.** "Southern China" was thought possibly to exclude the
northern parts of Anhui and Jiangsu, which would matter because the
Huainan–Huaibei coalfield sits in northern Anhui and the committed NESDC raster
also stops there. It does not exclude them: the paper reports that "relatively
stable SCR mainly distributed in Anhui, Hubei, and Jiangsu provinces whereas DCR
occurred in Guangdong, Hunan and Jiangxi provinces". Anhui and Jiangsu are named
as the *core* of the stable single-cropping region, which is also what this
project's own grid says — single-season rice dominates both provinces almost
completely, with a double-cropped share of
0.00<!--#rice.double_share_jiangsu_percent--> percent in Jiangsu and
8.36<!--#rice.double_share_anhui_percent--> percent in Anhui.

**The second question is not answered and could not be.** Whether the maps are
distributed is unestablished. The article is paywalled, OpenAlex records no open
version and the DOAJ record's only full-text link is the publisher DOI, so no
data availability statement could be read. That is the question to settle before
a reimplementation is considered, because an obtainable map by the thesis's own
algorithm would close the historical-years gap that
[`notes/dataset-leads.md`](dataset-leads.md) records without writing any code.

## The product landscape, and how little of it reaches this domain

The candidate list carried into this pass held five rice products. **Three of
them do not cover the study area**, which is the single most useful thing this
section establishes, because each had been recorded as a lead.

* **APRA500**, annual paddy rice planting area and cropping intensity at 500 m
  for the Asian monsoon region, 2000 to 2020 (Han, J., Zhang, Z., Luo, Y.,
  Cao, J., Zhang, L., Zhuang, H., Cheng, F., Zhang, J., and Tao, F., 2022,
  *Agricultural Systems* 200, 103437, doi:10.1016/j.agsy.2022.103437). **In
  domain, and verified accessible**: the deposit is Zenodo record 5555721,
  `10.5281/zenodo.5555721`, CC-BY-4.0, twenty-eight files holding one GeoTIFF
  archive per year from 2000 to 2020 plus three-year composites, each about
  1.7 MB; the API returns the file listing and a request for
  `paddyRice2018.zip` returns HTTP 200. It covers all three of the thesis's
  years, which no product committed to this repository does.
* **EFSP**, single and double paddy rice and cropping intensity for China at
  30 m from 2014 to 2019 (Wei, J., Cui, Y., Luo, W., and Luo, Y., 2022,
  *Remote Sensing* 14, 759, doi:10.3390/rs14030759). **In domain, and it
  reaches 2018.** Its accuracies are given as "producer (user) accuracy and
  kappa coefficients ranging from 0.92 to 0.96 (0.76–0.87) and 0.67–0.80,
  respectively", with determination coefficients against statistics "higher
  than 0.88 from 2014 to 2019". **Producer's accuracy exceeding user's accuracy
  by that margin means over-detection**: most true paddy is found, and a
  substantial share of what the map calls paddy is not. For a project whose
  rice layer enters as a per-cell fraction that is the more damaging of the two
  directions, because it inflates the fraction rather than thinning it.
* **NESEA-Rice10**, annual paddy rice at 10 m for 2017 to 2019 (Han, J.,
  Zhang, Z., Luo, Y., Cao, J., Zhang, L., Cheng, F., Zhuang, H., Zhang, J., and
  Tao, F., 2021, *Earth System Science Data* 13, 5969–5986,
  doi:10.5194/essd-13-5969-2021). **Out of domain.** Its "Northeast Asia" is
  Liaoning, Jilin and Heilongjiang together with Korea and Japan, and its
  "Southeast Asia" is Indonesia, Thailand, Vietnam, Myanmar, the Philippines
  and Malaysia. The Yangtze River Delta is in neither. The resolution and the
  year coverage had made this the most attractive product on the list; the
  extent removes it.
* **A 30 m annual paddy rice dataset for 2000 to 2023**, `10.6084/m9.figshare.28407710`
  (Hou, D., Chen, J., Feng, J., Ji, C., Dong, J., Du, G., and Yang, L., 2025).
  **Out of domain**: its title names *Northeastern* China.
* **A 30 m South and Southeast Asia product for 1995 to 2024** (Zhao, Z.,
  Zhang, G., Dong, J., Yang, J., Fan, C., Liu, R., and Xiao, X., 2026, *Earth
  System Science Data* 18, 5583–5599, doi:10.5194/essd-18-5583-2026). **Out of
  domain**, and worth recording anyway because its first two authors are the
  authors of the paddy-rice-and-XCH4 Reply discussed below, so the group that
  established the 0.5-degree correlation has since built the high-resolution
  map that correlation called for — for a different continent.

**So the in-domain choice is APRA500 at 500 m or EFSP at 30 m**, and the
coarser one is the one whose known failure mode bites hardest here. A review of
twenty-five rice products, three global and twenty-two regional, finds that
"different products share low consistency in fragmented rice fields" and that
"the prevalence of clouds and complicated rice cropping patterns or diverse
growing environments in subtropical and tropical regions poses challenges to
accurate rice mapping" (Fang, H., Liang, S., Chen, Y., Ma, H., Li, W., He, T.,
Tian, F., and Zhang, F., 2024, *Science of Remote Sensing* 10, 100172,
doi:10.1016/j.srs.2024.100172). This study area is subtropical, monsoonal,
cloudy and farmed in small parcels, which is every one of those conditions at
once.

Two further statements from that review bear directly on decisions already
taken here. It concludes that "currently it still lacks paddy rice maps with
both large spatial coverage, high spatial resolution, and long time series",
which is exactly the trade this repository resolved by committing NESDC for
2017–2022 and CCD-Rice for 1990–2016 rather than one product for all three
years. And it states that "deficiency of ground-truth samples impedes product
development and validation" — the same conclusion `notes/grounding-methods.md`
reached about this project's own accuracy assessment, reached independently by a
review of the whole product literature.

**A pattern in the deposits is worth naming.** The products that are openly
deposited are the newer and finer ones: APRA500 on Zenodo, NESEA-Rice10 on
Zenodo, CCD-Rice on Science Data Bank with checksums. The two rasters this
repository actually depends on for the coarse historical picture — the NESDC
layer and the 500 m maps behind the region record's transition figures — have no
deposit route that has been verified, and the same research groups deposit their
later work openly. That is a reason to expect the older layers to be obtainable
by asking rather than to treat them as closed.

## The ten-percent condition, which is testable here and has never been tested

The strongest published claim that satellite methane columns track paddy rice
comes with a resolution condition attached, and this project satisfies it more
comfortably than the study that set it.

Zhang, G., Xiao, X., Dong, J., Xin, F., Zhang, Y., Qin, Y., Doughty, R. B., and
Moore, B. (2021), *Reply to: "Correlation between paddy rice growth and
satellite-observed methane column abundance does not imply causation"*, *Nature
Communications* 12, `10.1038/s41467-021-21437-4`, state their result's domain of
validity precisely: the "seasonal dynamics of XCH4 and paddy rice growth were
consistent across the 0.5° gridcells with moderate to high proportions of rice
paddy (area percentage >10% within gridcells)". **The correlation is asserted
for rice-dominated cells at half a degree, not for a region.**

Their three reasons for disagreeing with the Comment are all about scale, and
all three point the same way. On the size of the analysis unit: "Larger ROIs
have much lower proportions of rice paddy area... Statistically, average values
over very large ROIs would dampen localized seasonal variations", and "larger
gridcells would have lower proportions of rice paddy area... and would thus
diminish the local contribution of CH4 emission from rice paddy on the seasonal
cycle of XCH4". On the resolution of the transport calculation: "The GHGF-Flux
CH4 inversion used by Zeng et al. was carried out at 2° × 2.5° horizontal
spatial resolution, which is much coarser than the spatial resolution of the
XCH4 data from the SCIAMACHY sensors (0.5° × 0.5°)". And on the prior: "EDGAR's
use of agricultural statistical data at administrative levels... precludes
accurate resolution of the geographic (or spatial) distribution of different CH4
emission sources". Their summary is a single sentence: "The spatial heterogeneity
of CH4 emission sources cannot be captured using larger ROIs, coarser gridcells,
and inaccurate model inputs."

**Every one of those three objections is answered favourably by this project's
design, which is the most useful thing in this record for a paper's framing.**
Its cells are 0.25 degrees, finer than the 0.5 at which the condition was
established. Its rice layer is a 30 m classification rather than administrative
statistics. And it makes no transport calculation at all, so no coarse inversion
grid dilutes anything.

**And the condition itself is immediately testable on committed data, and has
never been tested.** Of the 926<!--#composite.covered_cells--> cells in the
lattice, 531<!--#grid.rice_rows--> carry a rice fraction — of which
18<!--#grid.rice_zero_rows--> are recorded zeros — with a median single-season
fraction of 0.1291<!--#grid.rice_single_median-->. That median sits just above
the threshold, and 304<!--#grid.rice_above_ten_percent--> cells exceed it:
57.3<!--#grid.rice_above_ten_of_rice_percent--> percent of the rice-bearing
cells and 32.8<!--#grid.rice_above_ten_of_lattice_percent--> percent of the
whole lattice. **So a third of this project's field satisfies the published
condition for the association it is testing, and the association has only ever
been reported over all 926 cells at once — which is precisely the ROI-dilution
the Reply warns against.** The test is a subset and a recomputation. It is
queued in [`notes/paper-target.md`](paper-target.md).

The Comment is recorded on its own terms rather than through the Reply. Zeng,
Z.-C., Byrne, B., Gong, F.-Y., He, Z., and Lei, L. (2021), *Nature
Communications* 12, `10.1038/s41467-021-21434-7`, decomposed the seasonal cycle
of XCH4 into locally emitted and externally transported contributions for four
regions and found that **transported fluxes contributed more than local ones in
Northeast China, Southeast China and Northwest India**, with the two comparable
only in North Bangladesh. Southeast China contains this study area. **That is an
adverse finding for this project and it should be written as one**: the
mechanism by which a correlation between rice extent and XCH4 could be spurious
is named, quantified by region, and the region named is this one. The Reply's
answer is not that transport is unimportant but that a 2° × 2.5° inversion
cannot resolve the local term it is being compared against. Both halves belong
in a paper.

## Water regime and temperature, which are the controls a map cannot carry

`notes/grounding-yrd.md` already records the water-regime factor of 13.7 from
Wu et al. (2018). Three further results sharpen it, and one of them sits inside
this project's lattice.

**Eddy covariance puts the water-regime effect at between two and twenty
times.** Measuring two fields over three years, "cumulative CH4 emissions in the
production season were in the range of 7.1 to 31.7 kg CH4-C ha⁻¹ for the AWD
treatment and in the range of 75.7–141.6 kg CH4-C ha⁻¹ for the DF (delayed
flood) treatments" (Runkle, B. R. K., Suvočarev, K., Reba, M. L., Reavis, C. W.,
Smith, S. F., Chiu, Y.-L., and Fong, B., 2019, *Environmental Science &
Technology* 53, 671–681, doi:10.1021/acs.est.8b05535). The two ranges do not
overlap and the ratio between them depends on which end is taken: 2.4 times at
the closest, 20 times at the extreme. **A single factor should not be quoted for
this**, and the two ranges should be. The site is in Arkansas rather than China,
which is a real limit on transfer; what it establishes is that the effect is
large enough to be measured by a flux tower rather than inferred from chambers.

**Temperature moves emissions by comparable amounts, and the measurement is
in-domain.** At the Zhuanghang Experimental Station at 30°53′N, 121°23′E, "CH4
emissions from the NA100% plots by Huayou14 and Hanyou8 increased by 93% and
161% in the 'warm and dry' season of 2013, respectively, compared to the normal
season of 2014", with "the mean seasonal air temperature in 2013 was 2.3 °C
higher than that in 2014", while yield fell by 13 to 19 percent and 7 to 12
percent for the two cultivars (Sun, H., Zhou, S., Fu, Z., Chen, G., Zou, G., and
Song, X., 2016, *Scientific Reports* 6, doi:10.1038/srep28255). **That site
falls inside this project's field, in a cell the composite covers.** Its nearest
cell centre is 30.825°N, 121.425°E, which carries 34 soundings, an impervious
fraction of 0.359, a single-season rice fraction of 0.130 — within a thousandth
of the lattice median — and a 75 percent Shanghai share. So within one cell of
this study's own median rice fraction, a single warm dry season roughly doubled
to trebled emissions with extent unchanged, and did so in the direction opposite
to yield.

**The temperature response is not linear, which removes the last route by which
a static covariate might stand in for it.** Warming stimulates CH4 emissions
most strongly at a background flooded-stage air temperature near 26 °C, with
smaller responses both below and above, explained by divergent warming responses
of plant growth, methanogens and methanotrophs; 1 °C of warming is estimated to
raise Chinese paddy emissions by 12.6 percent, substantially more than leading
ecosystem models give (Qian, H., Zhang, N., Chen, J., Chen, C., Hungate, B. A.,
Ruan, J., Huang, S., Cheng, K., Song, Z., Hou, P., and eleven others, 2022,
*Environmental Science & Technology* 56, 4871–4881,
doi:10.1021/acs.est.2c00738). A parabolic response means the sign of the
sensitivity depends on where a site sits on the curve, so even a single
temperature covariate would not carry it, let alone a land-cover fraction.

## The diurnal cycle, and what it does to a 13:30 overpass

This is the newest finding in this pass and it bears on the instrument rather
than on the land surface, which is why it is reported first.

**Paddy methane flux has a strong daily cycle that peaks in the early
afternoon.** Over four cropping seasons of eddy covariance measurement — two dry
and two wet, in 2013 and 2014 — "CH4 fluxes were very low from 0000-0630H and
started to increase at around 0700H - 0830H, reached a peak at around 1330H -
1530H, and then decreased to low values again after 1900H" (Wassmann, R.,
Alberto, M. C., Tirol-Padre, A., Hoang, N. T., Romasanta, R., Centeno, C. A.,
and Sander, B. O., 2018, *PLOS ONE* 13, e0191352,
doi:10.1371/journal.pone.0191352). The same dataset gives "a very strong linear
relationship between nocturnal emissions (12-h periods) and the full 24-h
periods resulting in an R2-value of 0.8419 for all data points".

**TROPOMI's overpass is at about 13:30 local solar time, which puts it at the
opening of that peak window rather than in the middle of it.** Two consequences
follow and they run in opposite directions, so both have to be stated.

The first is a bias. The instrument samples the land surface within the daily
maximum, so a column enhancement read as representative of a daily mean flux is
read at the wrong point of the cycle, and in the direction that overstates. This
project does not convert columns to fluxes, so the consequence here is not a
quantified error but a constraint on interpretation: an enhancement measured at
13:30 over paddy cannot be compared with a daily or seasonal emission figure
without a diurnal correction, and none of this project's published comparisons
carries one.

The second is favourable and is the more useful of the two. The nocturnal-to-daily
relationship at R² 0.8419 means the daily total is recoverable from a partial
sampling of the cycle with most of its variance explained. **A satellite that
always samples the same hour is sampling a cycle whose shape is known and whose
integral is predictable from any one part of it.** A fixed-hour overpass is
therefore a systematic offset rather than an unquantifiable noise source, which
is the better of the two things a fixed sampling time can be.

**A 2024 study complicates the shape in a way that matters for this region.**
Li, H., Peng, C., Helbig, M., Zhao, M., Guo, H., and Zhao, B. (2024), *Nocturnal
peak methane flux diel patterns in rice paddy fields*, *Agricultural and Forest
Meteorology* 358, 110238, doi:10.1016/j.agrformet.2024.110238, finds a
pronounced single daytime peak at 13:30–14:30 in the early rice stage, but
daytime emissions showing no peak and running much lower than night-time levels
during the reproductive stage, under water limitation and high temperature. Its
own framing is that the diel pattern is generally regarded as peaking in
daytime, and that under the water-limited and hot conditions rice widely
experiences, the pattern is unclear. **So the overpass lands on the maximum
early in the season and can land near a minimum later in it, at the same site.**
Read against the sampling asymmetry the region record already carries — 82.4
percent of soundings falling outside the middle-rice window, and the fitted
seasonal peak at day of year 245.8 — this means the instrument's temporal
sampling is misaligned with rice emission at two scales at once, seasonal and
diurnal, and the diurnal misalignment changes sign within the season.

## Sown area is not planted area, and neither side is reference data

The thesis validated its rice maps against provincial statistics and treated the
statistics as truth. Its own section heading says which statistic: *PPPM-Derived
Paddied Rice vs. Sown Area of Rice Statistics*.

**Sown area and planted area are different quantities.** Sown area counts each
cropping of a field, so in a double-cropped landscape it exceeds the physical
area under rice, while a satellite classification of where paddy exists
recovers the physical area. Comparing one to the other therefore produces an
apparent underestimate wherever double cropping occurs, with no classification
error required. The convention in the mapping literature is explicit about the
absence of the quantity a map would naturally be compared with: "China's
Statistical Yearbooks do not contain a category for 'total paddy area';
therefore, researchers compare classifier results to the reported Sown Area with
the largest extent to minimize errors arising from multi-cropping."

**The brief this record was written from proposed that trap as the explanation
for the thesis's largest discrepancy, and the committed data refutes it.** The
thesis reports that for Shanghai, "PPPM-derived estimates and recorded
statistics were nearly identical in 2000 (1,123 km² vs. 1,130 km²)" but that by
2010 and 2018 the algorithm "captured only half of the sown area", which it
attributes to "Shanghai's small geographic area and high urban density, which
complicates spectral classification". The definitional gap cannot account for
that, because it requires double cropping and **Shanghai's double-cropped share
of paddy area in the committed regional table is
0.00<!--#rice.double_share_shanghai_percent--> percent**. With no second
cropping, sown area equals planted area and the two definitions coincide. The
same holds for Jiangsu at
0.00<!--#rice.double_share_jiangsu_percent--> percent, which is the province the
thesis reports the algorithm performing *well* in.

Where the trap can contribute is Zhejiang, at
16.27<!--#rice.double_share_zhejiang_percent--> percent double-cropped, and to a
lesser degree Anhui at 8.36<!--#rice.double_share_anhui_percent--> percent. The
thesis reports underestimation in Zhejiang too, attributing it to "mixed-use
landscapes, where agriculture and urbanization overlap". **A sixth of Zhejiang's
paddy being cropped twice is a competing explanation for part of that gap that
requires no classification error at all**, and it is the one testable without
new data. That is a specific, bounded correction to the thesis's reading rather
than a general one.

**The deeper point is that neither side is reference data for the other**, and
the thesis's framing assumes one is. A Landsat classification underestimates
double cropping, because the second crop's flooding signal is short and often
cloud-obscured; agricultural statistics overestimate planted area wherever sown
area is used as a proxy for it, by construction. Two measurements with opposite
known biases cannot validate each other, and an agreement between them is as
likely to mean the biases cancelled as to mean both are right — which is what
the near-identity of Shanghai's 2000 figures, 1,123 against 1,130 km², should be
read as rather than as evidence of accuracy. The consequence for this project is
the one `notes/grounding-methods.md` already draws from Olofsson: the CCD-Rice
validation polygons are the only in-domain reference data here that is
independent of both.

## The cropping-system transition, which is a third land-use change

`notes/grounding-yrd.md` records the CH4MOD-based conversion estimate. The map
underlying that literature is worth recording in its own right, because its
numbers are extent changes rather than modelled emissions and its named hotspot
is this study area.

From 1990 to 2015 across southern China, "the sown area of double cropping rice
(DCR) in Southern China decreased by 61054.5 km2, the sown area of single
cropping rice (SCR) increased by 20,110.7 km2, the index of multiple cropping
decreased from 148.3% to 129.3%, and the proportion of DCR decreased by 20%",
with a "double rice shrinking and single rice expanding" pattern running north to
south and **"the most dramatic changes occurred in the Middle-Lower Yangtze
Plain"** (Jiang, M., Xin, L., Li, X., Tan, M., and Wang, R., 2018, *Decreasing
Rice Cropping Intensity in Southern China from 1990 to 2015*, *Remote Sensing*
11, 35, doi:10.3390/rs11010035).

Three things follow. The changes are in **sown** area, which is the quantity the
section above distinguishes from planted area, so a net loss of 40,943.8 km² of
sown area is consistent with a much smaller change in the area physically under
paddy — the transition is partly a change in how often a field is cropped rather
than in whether it is. The multiple cropping index falling from 148.3 to 129.3
percent is a nineteen-point fall in croppings per field, and since methane is
emitted per flooded season rather than per hectare of paddy, that is a direct
reduction in emissions invisible to any measurement of extent. And the hotspot
is named as the Middle-Lower Yangtze Plain, which is this project's domain, over
an interval that contains two of its three years.

## What inversions have found about rice priors, which is not one direction

This is the section whose framing a previous pass corrected, and the correction
holds. **There is no support for the proposition that EDGAR systematically
underestimates rice methane in this region.** `notes/grounding-methods.md`
already records the primary finding: EDGAR v8's Chinese rice total is "double
the GRPI values for China and half for South Asia" (Chen et al., 2025,
doi:10.1029/2024EF005479). The Chinese total is too *high*. What is wrong with
it is where it puts the emissions and when.

Two sub-regional inversions in China make the point by disagreeing about
direction, and their disagreement is the finding.

**Upward, in the northeast.** A high-resolution TROPOMI inversion over
Heilongjiang for 2021 found rice emissions of "0.85 (0.69–1.03) Tg a⁻¹" from
the province, or "an emission factor of 22.0 (17.8–26.6) g m⁻² a⁻¹" normalised
by paddy area, against a prior of 0.43 Tg a⁻¹ from EDGAR v6.0 and inventory
emission factors of 4.8 to 10.0 g m⁻² a⁻¹, and describes "a 2 to 4 times lower
bias in widely used global and national inventories" (Liang, R., Zhang, Y.,
Hu, Q., Li, T., Li, S., Yuan, W., Xu, J., Zhao, Y., Zhang, P., Chen, W., and
others, 2024, *Environmental Science & Technology* 58, 23127–23137,
doi:10.1021/acs.est.4c09822). **The paper attributes the bias to a distribution
error, not to a magnitude assumption**: "EDGAR v6.0 uses a static global rice
distribution for 2000" and so "cannot capture the rapid increase of rice
cultivation in the Sanjiang Plain since 2000". The prior is wrong in
Heilongjiang because the rice moved there after the map was made.

**Downward, in the south.** A three-year TROPOMI inversion over the Greater Bay
Area at 0.25° × 0.3125° reduced the uncertainty of the posterior total by 57
percent — from a prior range of 1.77 to 3.04 Tg a⁻¹, or 72 percent, to a
posterior of 2.43 to 2.80 Tg a⁻¹, or 15 percent — and identified waste treatment
at 1.13 Tg a⁻¹ as the largest anthropogenic source. **In doing so it "corrects
the overestimated rice emissions over the Pearl River Estuary, where satellite
observations reveal limited rice paddies"** (He, C., Lu, X., Li, S., Huang, X.,
Xiao, H., Song, C., Li, T., Yuan, W., and Fan, S., 2026, *ACS ES&T Air* 3,
1097–1109, doi:10.1021/acsestair.5c00446).

**Read together, the two say the same thing twice with opposite signs.** Where
the prior's rice map placed paddy that is no longer there, the inversion took
rice emissions down; where it missed paddy that had appeared, the inversion put
them up. Both corrections are corrections to a *distribution*, and neither
supports a claim that the inventory's rice emission factor is biased one way.
**The argument for a better rice map is therefore an argument about spatial
allocation, and it should be made that way and not as an argument that rice
methane is being missed.**

The seasonal half of the same story is recorded in the methods record and its
consequence belongs here. EDGAR v8's rice seasonality "is also uniform within
individual countries. For example, rice emissions in EDGARv8 peak in June
everywhere over China" (Chen et al., 2025). One month, applied to every Chinese
rice cell regardless of cropping system or latitude. Liang et al.'s inversion
independently puts Heilongjiang's peak in June, at tillering, against a prior
that "shows a sustained methane emission throughout the growing season". **But
Heilongjiang is a single-cropped northern province transplanted in late spring,
and this project's own fitted seasonal peak in the XCH4 field is at day of year
245.8, which is 2 September.** A uniform June peak is roughly ten weeks early
here. That is a seasonality error in the prior, of a size this project can
already state from its own artefact, and it is a third distributional defect
rather than a magnitude one.

## The field's own account: extent is a weak predictor

The three sections above each show extent failing to carry something. This one
records that the field states the conclusion directly, in review papers, which
means a paper here can cite it rather than argue it.

**The magnitude review.** A synthesis of global estimates made between 1963 and
2025 puts their range at 10 to 280 Tg per year, with recent estimates differing
by about 4 Tg and a coefficient of variation of 13 percent, and finds that both
top-down and bottom-up approaches still depend largely on emission factors and
census data, with roughly 67 percent of available global estimates bottom-up and
33 percent top-down (Mehla, M. K., Singh, A., Jeong, J., and Ran, L., 2026,
*Global methane emissions from rice paddies are now increasingly quantifiable*,
*Communications Earth & Environment* 7, doi:10.1038/s43247-026-03902-4). The
title's claim is that the quantity is *becoming* quantifiable, and the figures
are what that means: a factor-of-28 historical spread narrowing to a 13 percent
coefficient of variation. **A 13 percent coefficient of variation across
independent recent estimates is the ceiling on how well any single predictor can
be expected to do**, and it is reached with emission factors and census data
rather than with maps.

**The mechanism review, which is the one that states the finding.** Qian, H.,
Zhu, X., Huang, S., Linquist, B., Kuzyakov, Y., Wassmann, R., Minamikawa, K.,
Martinez-Eixarch, M., Yan, X., Zhou, F., and eleven others (2023), *Greenhouse
gas emissions and mitigation in rice agriculture*, *Nature Reviews Earth &
Environment* 4, 716–732, doi:10.1038/s43017-023-00482-1, opens with the
statement this project's first hypothesis has to be written against: emissions
"vary markedly, primarily reflecting the impact of management practices. In
particular, organic matter additions and continuous flooding of paddies both
stimulate CH4 emissions, whereas fertilizer N application rate is the most
important driver of N2O emissions". **The variance is attributed to management,
in a review of the field, in its abstract.**

The mitigation figures quantify how much management moves: "new rice variety
selection, non-continuous flooding and straw removal strategies reduce GHG
emissions by 24%, 44% and 46% on average, respectively". **Those are cultivar,
water regime and residue management — three variables, none of which changes
rice extent by a hectare, together spanning nearly half the emission.** The
review also gives the global mean the numbers scale against, 283 kg CH4 ha⁻¹,
and puts global rice CH4 at 22 Tg per year in 1980–1989, 23 in 2000–2009 and 24
in 2010–2019, while yield-scaled emissions fell 38 to 55 percent from the 1980s
to the 2010s. A near-flat total with a halved intensity is an extent-and-yield
story that no extent measurement alone would reveal.

**The nitrogen finding is the sharpest single argument against a linear
extent-based predictor.** "The effect of N input on CH4 emissions is generally
positive at low N rates, but decreases and becomes negative with increasing N
rate, whereas N2O emissions from rice paddies increase exponentially with
increasing N application rates" (Qian et al., 2023). Non-monotonic in the
driver, and opposite in sign to the other greenhouse gas it co-varies with. A
regression of methane on rice fraction assumes that more paddy means more
methane, monotonically; the field's account of the dominant management input is
that the relationship changes sign partway along.

**State the conclusion for hypothesis 1 plainly.** Rice extent is a weak
predictor of rice methane, and this is the field's own explicit finding rather
than an inference from this project's null result. The variance lives in water
regime, temperature, residue, cultivar and nitrogen, all of which vary within a
mapped hectare of paddy and none of which a fraction represents. That makes the
2023 thesis's failure to find a strong association **the expected result rather
than a defect of its method**, which is a considerably stronger thing for a
paper to be able to say than that the association was not detected.

## What the rice grounding establishes

**Extent is the wrong variable and the field says so.** A review of rice
greenhouse gases attributes the variance to management practices in its
abstract, quantifies three management levers at 24, 44 and 46 percent, and
reports the dominant nitrogen input as non-monotonic. A separate review puts the
coefficient of variation among recent global estimates at 13 percent, reached
from emission factors and census data.

**What a better map buys is distribution, not magnitude.** EDGAR's Chinese rice
total is double GRPI's, so it is not systematically low here. Two Chinese
sub-regional inversions correct rice in opposite directions — up in Heilongjiang
where a static 2000 map missed new paddy, down in the Pearl River Estuary where
the prior placed paddy the satellite does not see — and both corrections are
spatial. EDGAR v8's June peak for all of China is about ten weeks early against
this project's own fitted seasonal maximum at day of year 245.8.

**The published condition for the rice–XCH4 association is satisfied by a third
of this lattice and has never been tested on it.**
304<!--#grid.rice_above_ten_percent--> cells exceed the 10 percent rice fraction
the Reply states its result for, and this project's 0.25-degree cells, 30 m rice
layer and absence of any transport inversion answer all three of the Reply's
scale objections favourably. Testing it costs a subset and a recomputation.

**Three of five candidate rice products do not cover this domain**, which leaves
APRA500 at 500 m — verified accessible on Zenodo under CC-BY-4.0, covering all
three thesis years — and EFSP at 30 m for 2014 to 2019, whose producer's
accuracy exceeding user's accuracy by 0.92–0.96 against 0.76–0.87 means it
over-detects paddy. And the maps from the thesis's own algorithm exist, annually,
for 1999 to 2019, over a "southern China" that explicitly includes Anhui and
Jiangsu; whether they are obtainable is unestablished.

**The sown-against-planted trap is real, and it is not the explanation for the
thesis's Shanghai discrepancy.** Shanghai and Jiangsu are
0.00<!--#rice.double_share_shanghai_percent--> percent double-cropped in the
committed table, so sown and planted area coincide there. Zhejiang at
16.27<!--#rice.double_share_zhejiang_percent--> percent is where the definitional
gap can contribute, and the thesis reports underestimation there too. The general
point stands regardless: two measurements with opposite known biases cannot
validate each other, and the thesis treated one of them as truth.

**And the instrument's sampling is misaligned with rice emission at two scales.**
Flux peaks at 1330H–1530H against a roughly 13:30 overpass, so the satellite
samples the opening of the daily maximum; and in the reproductive stage under
heat and water limitation the daytime peak disappears and night-time flux
exceeds it, so the sign of the diurnal misalignment changes within the season.
The nocturnal-to-daily R² of 0.8419 is the mitigating fact: a fixed-hour
overpass samples a cycle whose integral is largely predictable from any part of
it, which makes it a systematic offset rather than noise.

## What could not be verified

**Zhu and Li (2024) still does not close, and this pass tried hardest.** The
four figures attributed to it — 416 samples, a 2010–2018 mean of 252.17 kg ha⁻¹
against 146.02 for 2000–2009, a ratio of 1.52 and p < 0.01 — were retrieved this
pass from the publisher's abstract page as read by a search engine, matching on
all four and adding a qualification the query did not contain, namely that air
temperature and water-saving practices were "not likely the reason for the
increase after 2009". **That is suggestive and it is not verification.** The
article is paywalled; a direct fetch of the Springer page returns an
authentication redirect; Crossref, OpenAlex and Semantic Scholar all hold no
abstract for the DOI. A search engine's rendering of a paywalled abstract, in
answer to a query containing the numbers, is the same class of evidence that
produced six wrong first authors in an earlier pass. **The figures are therefore
not written, and `notes/references.md`'s "awaiting a source" status stands.**
Closing it needs the article itself.

**The MODIS 500 m fragmentation figures could not be traced to one source.** That
coarse-resolution rice maps suffer more severely from mixed pixels given
farmland fragmentation in China, that most paddies are smaller than a MODIS
pixel, and that this produces underestimation in fragmented and mountainous
terrain, are all statements that recur across the rice mapping literature, but
the specific sentences carried into this pass belong to several different papers
and none was read in its own source. What is written instead is the review
finding that "different products share low consistency in fragmented rice
fields" (Fang et al., 2024), verified in that review's abstract.

**The Guangdong 2015 example did not exist to be found.** The claim that neither
statistics nor classification is reference data for the other was carried with a
specific worked example from Guangdong in 2015 attached. No such example could
be located. The general claim is written because both biases are separately
documented and because the thesis's own figures illustrate it; **the Guangdong
example is not written**.

**The urban-methane ratio of two to three times inventory is verified, and it
was verified somewhere other than where it was expected.** It appears in the
urban record rather than here, and its source is a preprint — recorded as such.

**Four figures from the brief were wrong in detail and are corrected above.**
The diurnal peak is 1330H–1530H with the rise starting at 0700H–0830H, not
1300–1500H from 0800H. The eddy-covariance water-regime effect is two ranges
spanning a factor of 2.4 to 20, not a single tenfold factor. The cropping-system
paper is Jiang et al. **2018**, in *Remote Sensing* volume 11, despite the
2019 issue year its volume implies. And Qian et al.'s 24, 44 and 46 percent are
**greenhouse gas** reductions attached to **cultivar selection, non-continuous
flooding and straw removal** specifically, not the practices they had been
attributed to.

**Two of this record's own computed figures corrected numbers produced earlier in
the same pass.** Provincial double-cropped shares were first computed from the
analysis grid weighted by province share, giving Anhui 7.9, Jiangsu 0.1,
Shanghai 0.0 and Zhejiang 15.3 percent. The committed regional table, which is
what the published figure draws and what now carries resolvers, gives
8.36<!--#rice.double_share_anhui_percent-->,
0.00<!--#rice.double_share_jiangsu_percent-->,
0.00<!--#rice.double_share_shanghai_percent--> and
16.27<!--#rice.double_share_zhejiang_percent--> percent. The committed
definition is the one used throughout, and Jiangsu is exactly zero rather than
nearly zero, which strengthens the argument the section makes.
