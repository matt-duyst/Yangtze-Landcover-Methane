# Discussion, draft

Draft prose for the paper's final section. Every factual claim comes from a
committed record or a committed artefact, and every quoted number carries an
inline resolver naming the artefact quantity it reads from, on the convention
`scripts/verify_claims.py` enforces.

**The ordering, and why it changed.** This section has six jobs in a fixed
order: say what the result is and is not (§1), show that the result was the
predicted one (§2), show that a signal of the predicted sign is nonetheless
present and below what the design resolves (§3), explain why extent would have
failed even had the signal been visible (§4 and §5), show that the explanation
is not an artefact (§6), and then generalise it — which is where the contribution
sits (§7). Only then does it locate the work against prior results (§8), say
what would answer the original question (§9), and close with limitations (§10).

**§2 comes first on purpose.** An earlier draft opened the explanation with the
mechanisms, on the reasoning that the mechanism explains this particular result
and the capability limits explain why no refinement would change it. That
ordering buried the simplest statement available: the signal sought is far below
the per-cell noise, which is one number rather than six literature passes, and
it is prior to every mechanism. The mechanisms are not displaced by it — they
answer a different question, and §4 says which — but they no longer carry the
explanation alone.

**§3 is new and it sits where it does because it is §2's empirical half.** §2 is
an arithmetic prediction: a land-cover contrast of the observed size should move
the column by a fraction of a part per billion. §3 is what the record shows when
it is asked in the season the prediction is about, and the answer is a trace of
the predicted sign that the design cannot resolve. It belongs after the
prediction and before the mechanisms, because a reader who has just been told
the signal should be invisible is owed the measurement that looked for it
anyway. **It displaces nothing.** The mechanisms, the artefact tests and the
capability limits are unchanged by it, and §6's sampling-composition test is
extended rather than replaced.

## 1. What the reproduction establishes, and what it does not

No association between land cover and the 2018 methane column field was detected
that survives correction for spatial dependence, control for surface albedo, or
evaluation under more than one held-out design. **That is a statement about a
failed detection, and it is the strongest form the evidence supports.**

**Equivalence bounds have since been set, and they separate the two
predictors.** Against a comparative bound at the spatial null's own performance,
|r| = 0.58<!--#equiv.bound_comparative-->, tested on a 90 percent interval with
effective degrees of freedom, **no combination of field, predictor and weighting
falls outside the bounds** — there is no positive result anywhere. For rice the
interval falls entirely within the bounds in all
24<!--#equiv.rice_rows--> combinations, which is evidence of no meaningful
effect. For impervious cover it does so in only
7<!--#equiv.impervious_within--> of 12<!--#equiv.impervious_rows-->, and spans
the bound in the rest, so there the weaker non-detection claim stands. **The
paper therefore makes the stronger claim for rice and the weaker one for
impervious cover**, and the asymmetry is a property of the evidence rather than
of the argument.

**What can also now be said is that measurement error in the impervious
predictor does not account for the result** — §6 gives the bound.

The reproduction's null is also not a finding that rice does not matter in this
domain. A tower inversion of this region in this study's own year found
agricultural soils to be the dominant driver of seasonal variability in
atmospheric methane. The two results are compatible and the difference between
them is the subject of this section: **a static annual land-cover fraction,
regressed against an annual column composite at 0.25 degrees, cannot recover
what a tower inversion recovers.** The question is why, and the answer has two
parts that are different in kind.

## 2. The result was the predicted one

Before any mechanism, there is an arithmetic question that the reproduction can
answer and that had not been asked: **how large a column signal should a
land-cover contrast of the observed size produce?**

The conversion is the same closed form §7 uses for information content, taken
from the operational inversion literature rather than constructed here: a column
enhancement is `k` times a surface flux, with
`k = α M_air L g / (M_CH4 U p)`, evaluated at this domain's own wind. Applying
it to the inventory's own rate for the sectors urban land proxies — landfill,
wastewater and gas distribution, at 28.82 Mg km⁻² a⁻¹ — gives a slope of
1.1995<!--#change.beta--> ppb per unit impervious fraction.

**Across the whole observed impervious range, from the 5th to the 95th
percentile, that is a column contrast of
0.410<!--#change.xsec_contrast--> ppb.** The field's between-cell standard
deviation is 14.86<!--#field.sd_operational--> ppb. So the entire land-cover
contrast available in this domain should move the column by
2.8<!--#change.xsec_share--> percent of the variation the field actually has,
for an implied R squared of 0.00007<!--#change.xsec_r2-->.

**The measured held-out R squared for impervious fraction is
0.085<!--#baseline.impervious_r2-->, three orders of magnitude larger than the
expectation.** Two things follow and they are different in kind.

**The null was the predicted outcome.** A predictor whose physical signal is
one part in three hundred of a field's variation is not expected to explain that
field, and no modelling choice recovers it. The sections that follow explain why
extent is a poor proxy and why the observing system cannot attribute; this
section says that even a perfect proxy and a perfect attribution would be
looking for something below the noise. That is prior to both.

**And the association that was measured cannot be the emission signal.** An
observed 0.085 against a permitted 0.00007 is not a weak version of the right
thing; it is a different thing. This is independent of the albedo and wind
results in §6 and agrees with them: it converts *the association does not
survive controls* into *the association could not have been the signal in the
first place*.

**What this does not say, and the distinction is the whole of it.** It does not
say that this observing system cannot see methane over this domain. It can. The
same conversion applied to the domain's largest sector — coal mining, which the
inventory puts at 2035.1<!--#change.coal_total--> Gg a⁻¹ across
22<!--#change.coal_cells--> cells, some 92.5 Gg a⁻¹ each — gives
5.80<!--#change.coal_enhancement--> ppb, or
2.9<!--#change.coal_multiple--> times the median per-cell standard error. **A
source of that size is visible; the differences land-cover extent proxies are
twenty to fifty times smaller.** The limit is a property of the signal, not of
the instrument, and it is why §9's routes are about better priors and targeted
observation rather than about more of the same observations.

Coal is also not an alternative explanation for the measured association, which
had to be checked rather than assumed: its correlation with impervious fraction
is +0.0366<!--#change.coal_vs_impervious-->, and only 2 of its 22 cells fall in
the top decile of impervious fraction.

**The bound's own limits, now measured rather than asserted.** This is a
bottom-up expectation. It says what the inventory's allocation implies, and the
urban sectors are allocated on a surface that tracks impervious area — so the
proportionality it rests on is partly induced by the allocation rather than
observed. **On this lattice that induction can be quantified.** The inventory's
landfill and wastewater grids rank-correlate with this work's own impervious
fraction at +0.84<!--#sector.landfill_vs_impervious--> and
+0.90<!--#sector.wastewater_vs_impervious--> over all 926 analysis cells, and
they share an allocation mask outright — identical nonzero cells, which is what
one surface carrying two per-unit factors looks like. Oil and gas follows at
+0.65<!--#sector.oilgas_vs_impervious-->, and coal, which is allocated on mine
locations, does not, at +0.19<!--#sector.coal_vs_impervious-->.

**So the bound in this section is a bound and not a test, and for the urban
sectors it could not be made into one with this inventory.** Testing impervious
fraction against a sector allocated on a near-monotone function of impervious
fraction measures the allocation, not the atmosphere. **The rice sector is the
exception and that is what makes this a finding rather than a complaint**: the
inventory's rice grid correlates with this work's rice fraction at only
+0.13<!--#sector.rice_vs_rice-->, lower than its coal grid does at
+0.38<!--#sector.coal_vs_rice-->, so a rice comparison measures something —
though the same figure says the two disagree substantially about where rice is,
which is a second finding and not a reassurance. It therefore cannot rule out an
emission the inventory does not carry. Aquaculture is the one such source
interleaved with a predictor here, and at the magnitude the literature supports
it stays below the noise too, but that is an estimate rather than a measurement
and it is recorded as one.

## 3. A seasonal signal of the predicted sign, below resolution

§2 says the signal should be invisible. This section reports what happens when
the record is asked in the season the question is about, which is the one
arrangement of these data that had not been tried.

**The annual composite is the wrong object for a seasonal source.** A flooded
paddy emits methane and a drained one does not, so an annual mean over a cell
averages the emitting and the non-emitting halves of the year together. An
annual null is therefore consistent with two seasonal associations of opposite
sign cancelling, and no annual number separates that case from an absence. The
distinction matters because the two support different conclusions: a
cancellation means the predictor is related to the field and the design cannot
see it seasonally; an absence means the predictor is unrelated.

**It is a cancellation.** Results §3.4 composites the record over whole months —
free, because the compositing pass retained monthly partial sums — and the rice
association changes sign with the season. It is
+0.138<!--#seasonal.rice_growing--> in the June-to-September growing window and
-0.273<!--#seasonal.rice_off--> in November and December, against
-0.056<!--#seasonal.rice_annual--> for the year. The within-cell
flooded-minus-off-season contrast, which differences out every time-invariant
cell property, correlates with rice fraction at
+0.225<!--#seasonal.rice_contrast--> at a slope of
15.90<!--#seasonal.rice_contrast_slope--> ppb per unit fraction. The same
contrast against impervious fraction is
-0.095<!--#seasonal.impervious_contrast-->, so the seasonality is specific to
the predictor whose source is seasonal.

**The sign is the one the mechanism predicts**, and that is what makes it worth
reporting rather than filing as noise. §4 records that rice emission is set by
water regime, with three regimes on one soil spanning a factor of 13.7 in net
global warming potential. A predictor that is flooded in summer and dry in
winter should raise the column in summer and not in winter, and over these cells
it does.

**And the design cannot resolve it.** The contrast's nominal *p* is
0.00024<!--#seasonal.rice_contrast_p_nominal--> and its corrected *p* is
0.132<!--#seasonal.rice_contrast_p_corrected-->, at an effective sample size of
46.0<!--#seasonal.rice_contrast_effective_n--> cells of
262<!--#seasonal.rice_cells-->. Out of sample the contrast is worse than
useless: a held-out R² of
-0.052<!--#seasonal.predictor_r2_contrast--> against a constant, on the same
spatial-block design the annual analysis uses. Of
90<!--#seasonal.tests--> correlation tests across the seasonal table,
39<!--#seasonal.nominal_significant--> reach five percent nominally and
1<!--#seasonal.corrected_significant--> after correction, against
4.5<!--#seasonal.chance_expected--> expected by chance — **fewer than chance
alone would produce.**

**Two properties of the measurement point the same way as the tests.** The
contrast weakens as the sample grows, from +0.225 on 262 cells to
+0.070<!--#seasonal.contrast_pair5--> on
359<!--#seasonal.contrast_pair5_cells--> under a looser window definition; and
it is much weaker on the raw retrieval,
+0.081<!--#seasonal.raw_contrast-->, so it may be a property of the operational
bias correction, whose terms vary seasonally, rather than of the atmosphere.
Neither possibility can be excluded, because the retained sums carry monthly
means and no monthly variances, so a seasonal composite has no per-cell standard
error at all.

**What this section claims, stated narrowly.** The annual null is a cancellation
of two seasonal associations of opposite sign, neither resolvable at this
design's effective sample size. **That is not a positive result and it is not
nothing.** It does not license a claim that rice extent predicts column methane
seasonally — the corrected tests, the held-out score and the decay all refuse
that — and it does refine the negative result from "no association" to "no
resolvable association, in a record whose seasonal structure is consistent with
the mechanism". The refinement costs the paper nothing it was claiming, because
what it was claiming was a failed detection, and this is a more precise
description of the same failure.

**It also sharpens §7's limits rather than softening them.** §2 puts the column
signal a land-cover contrast should produce at an implied R² of
0.00007<!--#change.xsec_r2-->. A design that cannot resolve an association at
that magnitude is exactly a design in which a real seasonal relationship shows
up as an unresolvable trace, so finding one is weak confirmation that the
limits are the binding constraint rather than an artefact of the predictors.
The one arrangement of these data not previously tried has now been tried, and
it agrees with what preceded it.

## 4. Extent is a proxy for presence, not for management

The first part is a property of the predictor rather than of its quality. Across
seven sectors present in this domain, the recorded determinant of emission is a
management variable that leaves extent unchanged.

* **Rice** is set by water regime, not by planted area: three water regimes on
  one soil under one crop span a factor of 13.7 in net global warming potential.
* **Landfills** are set by gas collection efficiency and the
  landfill-versus-incineration split, not by site area. Measured collection
  efficiency averages 38 percent against a reported 70, while the Los Angeles
  sites in the same analysis average 85 — a factor of two in emission at
  constant footprint.
* **Gas distribution** is set by the age and material of the network rather than
  by the extent of the area served; underground steel pipelines and aboveground
  risers are the leak-prone components and leak density varies between cities.
* **Coal** is set by gas content and seam depth, not by mine area. In-place gas
  content across the Huainan–Huaibei coalfield runs 8 to 16 m³ per tonne in
  Huaibei and 10 to 30 in Huainan.
* **Urban land** is set by residential-industrial composition, not by paved
  area: a residential tower and a single-storey industrial shed have identical
  impervious footprints, different gas connections and different waste
  generation.
* **Aquaculture** is set by pond type, not pond area. Greenhouse-gas emission
  intensity per unit of fish production runs **197 times higher** in traditional
  earthen ponds than in in-pond raceway systems, measured in Jiangsu.
* **Rice straw** is set by whether residue is incorporated or burned, not by the
  area it grew on: four years of autumn incorporation produced a five-fold
  increase in growing-season methane, with no effect on yield — so nothing in an
  agricultural statistic records it.

Stated once: **extent is a proxy for the presence of a source and not for its
management, and in every sector here management sets the rate.** A land-cover
fraction can therefore be an accurate map and still fail to predict a methane
field, because the two are measuring different things.

**The last two instances sharpen this beyond a proxy problem.** Both are
*within-class* ratios: the same pond, the same paddy, the same area, a different
practice. A factor of 197 between two ways of farming the same water is not an
error better mapping could reduce. **This is the load-bearing form of the
argument, because it means the failure is structural rather than a matter of map
quality** — and it is why §9's routes are about priors, targeted observation and
isotopes rather than about better land-cover products.

## 5. What the predictors never contained

The second part is a different claim and should not be merged with the first.
§4 says a perfectly measured extent predictor would still fail. This section
says part of the field was never being predicted at all.

**Coal mine methane in northern Anhui.** The Huainan–Huaibei coalfield lies
inside the analysis lattice, and a gridded bottom-up inventory names Anhui among
the largest emitting provinces in eastern and northern China. Neither predictor
represents it: an impervious fraction does not see a colliery and a rice fraction
does not either. **And those are the same cells where the rice predictor has a
hole**, because the committed rice raster stops classifying north of 33.3462° N,
leaving an unclassified region in northern Anhui. The cells with an unrepresented
major source are the cells with a missing predictor, and the two defects coincide
rather than being independent.

**Aquaculture.** The region holds 26 percent of China's aquaculture area, ponds
are interleaved with paddy at the scale of the analysis cell, and the sector is
absent from the inventories this field uses as priors. With a within-class ratio
of 197 between pond types, a source of this size being both unmapped and
unpriored is a gap in the field rather than in this study.

**The wetland prior overlapping the rice prior.** WetCHARTs, the wetland
ensemble the Integrated Methane Inversion uses by default, states in its own
documenting paper that Chinese rice extents are only implicitly excluded, that
inundation retrievals cannot separate co-located agriculture from natural
wetland, and that the distinction "has yet to be consistently addressed". So the
two largest microbial sources in this domain are not separated in the prior that
would be used to attribute them.

## 6. Why the result is not an artefact

Five candidate explanations for a null that is not a real absence were each
tested rather than argued away. This is the structure a reviewer checks, so it is
stated in that form.

**Retrieval bias correlated with the predictor.** Impervious fraction and
retrieved surface albedo co-vary at Spearman
+0.761<!--#collinear.collinearity--> over 926<!--#grid.rows--> cells, and albedo
predicts retrieved methane on the bias-corrected field, so the zero-order
land-cover association is confounded by construction. Removing albedo from both
variables reduces the association to +0.021<!--#collinear.partial-->. The
operational a posteriori correction removes only
2.1<!--#collinear.reduction_percent--> percent of the fitted albedo slope, so the
test was repeated on the machine-learning-corrected blended product, built
specifically to suppress this dependence. **The land-cover result did not
improve on it**, which is the outcome a real association would not produce.

**That second test is weaker than it reads, and the reason is in the blended
product's own description.** Two of the 30 retrieval parameters its correction
is a function of are the shortwave-infrared and near-infrared surface albedos,
so the corrected field is by construction a function of albedo rather than a
field with albedo removed — which is also why its fitted albedo slope is the
steepest of the four rather than the shallowest. **The blended field is
therefore not an independent check on an albedo-confounded association**, and
the albedo control this test rests on is the partial correlation, which
conditions on measured albedo directly and is unaffected. The blended result
remains informative about whether the finding depends on the retrieval, which is
why it is still reported; it is not a second, independent removal of the
confound, and an earlier version of this paragraph treated it as one.

**Sampling composition.** Cell means rest on whichever days each cell was
observed, and mean day of year correlates with the operational field at
0.699<!--#deseason.doy_raw--> — a stronger association than either land-cover
predictor achieves. A deseasonalised field was therefore built by removing the
fitted seasonal cycle at the sounding level. The impervious association moved by
0.009<!--#deseason.impervious_change--> in Pearson correlation. **The calendar
does not explain the association's absence.**

**That test was a correction and §3 is the stronger version of it, a
composition.** Removing a fitted cycle from the soundings asks whether the
association survives once the calendar's smooth part is taken out; compositing
by season asks what the association is *within* a season, which does not depend
on the cycle being smooth or on its being the same in every cell. The two agree
for impervious cover, which is null in every window. **They disagree for rice,
and the composition is the more informative of the two**: the deseasonalised
annual field still shows nothing, while the seasonal composites show a sign
reversal that the annual field cannot express. Neither survives correction for
spatial dependence, so the artefact question is answered the same way — the
calendar is not what produced the null — but the second test establishes the
more specific thing, that for rice the annual null is a cancellation.

**Transport error.** A model transport error standard deviation of 12 ppb for
individual TROPOMI observations is comparable to this field's entire between-cell
standard deviation of 14.86<!--#field.sd_operational--> ppb. That is a reason a
column field at this resolution carries little recoverable local signal, and it
is a property of the atmosphere and the model rather than of the predictors.

**Effective sample size.** The 926<!--#grid.rows--> lattice cells are not 926
independent observations. The Dutilleul correction puts the median effective
sample size at 53.4<!--#dof.effective_n_median-->, so every nominal *p*-value in
the analysis is optimistic by roughly a factor of four in sample size, and the
reported results use the corrected values.

**Measurement error in the predictor, which is the only one that could
manufacture a null rather than explain one.** Measurement error in a predictor
attenuates its coefficient toward zero. Treating the second impervious product
as a second measurement of the same quantity bounds how much error the predictor
in use can carry: the two cell fractions differ with a variance
13.2<!--#atten.var_share_pct--> percent of the predictor's own, so under
independence of the two products' errors the reliability ratio is at least
0.868<!--#atten.lambda_min--> and **the largest factor by which measurement error
could be deflating the coefficient is
1.15<!--#atten.factor_max-->.** That lifts the best impervious held-out R² from
+0.085<!--#suite.impervious_operational--> to
+0.098<!--#atten.r2_bound_bu--> against a spatial null of
+0.332<!--#suite.null_operational--> on the same cross-validation scheme and
weighting.

**That bound covers the impervious predictor and not the rice predictor, and the
asymmetry is stated rather than left to be noticed.** The impervious bound works
because two independent products measure the same quantity over the same cells,
which is what converts their disagreement into an upper bound on error variance.
No second rice product measures the same quantity: the alternatives differ in
season definition as well as in error, so their disagreement is not an error
estimate. **So for rice, measurement error remains a candidate explanation that
this work does not exclude.** One specific mechanism is now boundable — paddy
and aquaculture ponds are spectrally similar flooded land, and a 10 m national
pond product reachable since September 2026 puts pond area inside this lattice
at most about 15 percent of the mapped rice area — but that is a ceiling on one
mechanism from an area ratio in neighbouring years, not a reliability ratio, and
it is recorded in `notes/grounding-rice.md` rather than reported here.

**Put as a requirement, which is the form that shows the margin: for measurement
error to lift land cover to the spatial null's performance,
74.5<!--#atten.need_share_bu_pct--> percent of the variance in the impervious
fraction would have to be error — 5.6<!--#atten.need_multiple_bu--> times what
the two products' disagreement supports**, and
7.2<!--#atten.need_multiple_bw--> times on the sounding-weighted combination.
The bound's assumptions are stated in the methods: independence of the two
products' errors, homoscedasticity, and non-differentiality. The second and third
are measurably violated in the unfavourable direction, and neither approaches the
factor the margin provides.

**The rice half of this question is unbounded and the asymmetry is structural.**
A bound of this form needs a second product whose errors are independent of the
first, and no independent second rice product exists: the only candidate took
its training samples from the same map this work uses. So measurement error is
excluded for the impervious predictor and not for the rice predictor, and the
paper should not imply symmetry.

## 7. What the observing system can and cannot constrain

This is the contribution, and it is two limits measured on one domain.

**The information-content limit.** Expected degrees of freedom for signal over
this domain, from the closed-form averaging-kernel estimate the Integrated
Methane Inversion applies to TROPOMI, evaluated on this work's own observation
counts, run from 3.98<!--#dofs.at_5tg--> to
22.21<!--#dofs.at_12tg--> across the range the literature supports for the
domain's total emission. **The qualification is the finding rather than a
caveat**: at no point in the sweep does any cell reach an averaging-kernel
sensitivity above 0.5 — the count is
0<!--#dofs.cells_above_half--> at every magnitude tested — and at the top of the
range the best-observed cell of 926 reaches
0.065<!--#dofs.cell_max_12tg-->, an order of magnitude below the threshold at
which a cell is half constrained by the observations rather than by the prior.
**So a regional total is constrainable while cell-level attribution is not**, and
the total accrues from many weakly constrained cells rather than from a few well
constrained ones. In emission units, a median cell would have to emit about
86<!--#dofs.prior_free_median_gg--> Gg a⁻¹ for the observations to constrain it
half independently of the prior, which is above the whole range a large municipal
landfill emits.

**This is a reimplementation of a published closed-form estimate over this
lattice, not an inversion.** No transport model was run, no Jacobian was
constructed and no emissions were optimised, and the figures are bounded to this
domain, this instrument and this period.

**The identifiability limit.** Information content bounds how much can be
recovered; it does not bound whether what is recovered can be attributed to a
sector. The evidence that attribution derives from the prior rather than from the
observations is a contrast inside a single published inversion: where a sector's
prior is allocated on facility coordinates and is spatially distinct, posterior
error correlations with other sectors fall below 0.35 and the sector can be
quantified; where sectors share a population-like allocation surface, those
correlations run 0.45 to 0.87 and separation is limited and prior-weighted. The
same instrument, inversion and domain separate one sector and fail to separate
three, and the only difference is the priors' spatial structure. **In this domain
the sources are interspersed at the scale of the analysis cell** — paddy and
freshwater aquaculture occupy the same flooded lowland, rice and natural wetland
overlap in the wetland priors by those products' own account, four urban sectors
share one population-like surface inside the same city cells, and coal in
northern Anhui lies adjacent to and partly inside the cells where the rice
classification stops.

**The two limits are independent, and that pairing is what the contribution
rests on.** Additional observations raise expected degrees of freedom and do not
make a prior more spatially distinct; a better prior sharpens attribution and
adds no information the observations do not carry. **Either limit alone would say
the question is not answerable as asked. Together they say why no refinement of
the same design would fix it**, which is a stronger and more transferable claim
than a null result in one region.

## 8. Relation to prior results

**The mechanism this work measured has been reached independently by a different
method, and that strengthens rather than weakens it.** Decomposing the seasonal
cycle of column methane into locally emitted and externally transported
contributions across four regions, Zeng et al. (2021) found transported fluxes
contributing more than local ones in Northeast China, Southeast China and
Northwest India. **Southeast China contains this study area.** Their route was a
transport decomposition and this project's was a held-out regression against
land-cover fractions, and both conclude that local column variation here is not
dominated by local emission. **What this work adds is the observing-system
account of why**: a measured information-content limit and a measured
identifiability limit over the same domain, where the published comparison
argued from transport alone.

**The positive local result stands and bounds the claim.** A tower inversion of
this region in this study year found agricultural soils dominant in seasonal
variability, by a method that can support that claim. This work does not
contradict it and cannot reproduce it; **what it establishes is the boundary
between the two designs** — that the signal a tower inversion recovers is not
recoverable from an annual column composite regressed on static extent.

**And the difficulty is not specific to this domain.** Downscaling column
methane with gradient boosting over the Arabian Peninsula, using a carbon
tracker, satellite land products and reanalysis as inputs, reached R² 0.63 with
an RMSE of 13.26 ppb, described by its authors as moderate accuracy — against
R² 0.98 for column carbon dioxide with the same method and inputs. **Methane is
the hard one even with the right predictors**, and an RMSE of 13.26 ppb is
comparable to this field's entire between-cell spread of
14.86<!--#field.sd_operational--> ppb. That is a comparator from another region
rather than a bound on what is achievable here, and it is cited as the former.

One sentence on the prior work this extends: the 2023 thesis asked whether urban
expansion and paddy rice explain the methane field over these four provinces,
and the errata document accompanying this reproduction records what that study
did and did not establish. This section does not relitigate it.

## 9. What would be required to answer the original question

Three routes, each specific, each with a measured or published precedent. None
of them is a better land-cover product.

**A better prior, used as a prior rather than as a regressor.** The legitimate
role for a rice map in this field is spatial prior to an inversion, and the gain
from improving one has been measured twice in or near this domain. EDGAR spreads
rice emissions across non-rice agricultural grids using a year-2000 paddy
geography — one of this project's own three analysis years — and applies a
uniform June seasonal peak to every Chinese rice cell. Against that, this
project's own fitted seasonal peak in the column field falls at day of year
245.8, which is 2 September, so a uniform June peak is roughly ten weeks early
here. Substituting an updated rice distribution over Heilongjiang raised the
sectoral estimate from 0.43 to 0.85 Tg and **reduced model-observation mean
biases by 40 percent**; a separate regional inversion attributed increases in
Zhejiang, Fujian and Jiangxi to rice paddies and named EDGAR's outdated maps as
the cause. **This project's layers are fit for that use and have not been put to
it.**

**Tip-and-cue, where the column identifies and a targeted instrument resolves.**
The published route uses TROPOMI to locate a hotspot and a facility-scale
instrument to quantify it; applied to landfills in four cities it found sites
emitting 3 to 29 t h⁻¹ and city emissions 1.4 to 2.6 times inventory. **This
project has the tip and not the cue**, and §7's prior-free threshold is the
quantitative statement of why the tip alone is insufficient: no single facility
in this domain emits enough for the column to constrain it half independently of
the prior.

**A regional isotopic campaign, which is the one genuine research opening.**
Where sources are interspersed, the field's fallback is to separate them by
composition. Against global mean signatures that does not help here: pooled
literature puts rice fields at about −61 ± 4‰ in δ¹³C and atmospherically
measured waste sources at −56.1 ± 2.4‰, which overlap within one standard
deviation, so isotopes separate microbial from thermogenic rather than rice from
landfill. **But regional endmembers are not global means.** A 2026 South Asian
campaign found rice paddy methane notably more enriched than the global mean,
with Miller–Tans values of −53.8 ± 0.8‰ in δ¹³C and −311 ± 6‰ in δ²H, and
concluded that region-specific isotopic endmembers are critical for accurate
source apportionment. A rice signature at −53.8 is enriched *past* the waste
average of −56.1, so a regional dual-isotope campaign can separate what global
means cannot. **No equivalent campaign exists for China**, and the global
δ¹³C source-signature inventory has no spatially resolved signatures for waste
or for rice — the two sectors this project's question compares. That is a
concrete and fundable next study, and this domain is where it would be worth
doing.

## 10. Limitations

**One year of one instrument.** 2018 is the first full year of the TROPOMI
record and the 2023 thesis's own analysis year, and the record here is an
eight-month year beginning 30 April. Nothing in this work establishes that 2018
is typical. A second analysis year is recorded as a decision awaiting a choice
rather than as work merely undone, and its strongest justification is that it
would let the capability estimate be computed twice and show whether the
conclusion is a property of the instrument over this domain or of 2018's
coverage.

**No validation against ground-based column measurement.** The nearest Total
Carbon Column Observing Network station lies inside the domain, and
9<!--#tccon.coincident_days--> days in
2018 carry both a TROPOMI overpass of its cell and station data. Nine coincident
days, without the a-priori profile alignment a station–satellite comparison
requires, cannot validate a field, and no result here rests on that comparison.

**No accuracy assessment of either land-cover layer, and the reason is a
property of the region.** The assessment frame for a fractional layer compares a
product against complete-coverage reference data more accurate than the product.
Four candidate reference products over this domain were verified and every one is
less accurate than the 30 m products it would assess, the closest being a 1 m
national land-cover map at 73.61 percent overall accuracy against an impervious
F-score of 0.954 for the layer in use. So the absence is not an omission that
effort would close.

**Four preprocessing steps not applied.** The retrieval's own precision variable
is neither gridded nor filtered on; the published albedo floor and blended-albedo
ceiling are not applied; within-cell variance is not accumulated, so no
representativeness estimate is recoverable from the committed checkpoint; and
destriping is absent, official destriping having been applied only from
September 2024 to orbits this analysis year will never include. Each is recorded
with its cost, and each would require a second pass over the granule archive.

**The rice half of the attenuation question is unbounded**, for want of a second
rice product whose errors are independent of the layer in use, as §6 states.

**And the capability figures are a reimplementation rather than an inversion**,
bounded to this domain, this instrument and this period. The single free preview
run of the published tool would settle what this work estimates.

---

## Drafting notes, not part of the section

### Numbers not marked, and why

24 of this section's numbers carry resolvers; 81 do not. The unmarked ones fall
into four classes and only the last is a defect.

* **Section and year references** — §1 to §10, 2018, 2023, 0.25 degrees.
* **Every figure attributed to the literature**, which comes from a paper rather
  than from an artefact and is resolved by its citation instead: the 13.7 water
  regime ratio, the 197 aquaculture ratio, the five-fold straw increase, the
  38/70/85 percent collection efficiencies, the 8–16 and 10–30 m³ per tonne coal
  gas contents, the 26 percent aquaculture share, the 0.35 and 0.45–0.87
  posterior error correlations, the 0.5 sensitivity threshold, the R² 0.63 and
  RMSE 13.26 ppb downscaling figures, the 12 ppb transport error, the isotopic
  signatures −61 ± 4, −56.1 ± 2.4, −53.8 ± 0.8 and −311 ± 6, the 40 percent bias
  reduction and the 0.43/0.85 Tg Heilongjiang pair, the 3–29 t h⁻¹ landfill
  rates and the 1.4–2.6 inventory multiples, and the 73.61 percent and 0.954
  accuracy figures in §10.
* **Figures derivable from marked ones or already exempted in the methods
  draft**, which lists them: the Anhui raster bound 33.3462° N, and the 20.7 and
  19.9 percent product differences. The Hefei counts were on this list and are
  now marked and resolved against `data/processed/tccon_hefei_2018.csv`.
* **One number that should be resolvable and is not**, reported rather than
  quietly dropped: **the fitted seasonal peak of the column field at day of year
  245.8**. It appears in `notes/decisions.md` and `notes/grounding-rice.md` as
  prose and in no committed artefact, so it cannot be marked. It is load-bearing
  in §9 — it is what makes EDGAR's uniform June peak "roughly ten weeks early
  here" — and it should have a row in `deseasonalisation_2018.csv`, which
  currently holds only the correlation table. Queued.

### Resolvers added for this draft

**Five**, all for `attenuation_bound_2018.csv`, because the two figures that
carry §6's conclusion had no way to be quoted. The artefact held the reliability
bound and the R² bounds but expressed "what it would take to overturn this" only
in a free-text `note` column, which no resolver reads. Added:
`atten.need_share_bu` and its percent form, and
`atten.need_multiple_bu`, `atten.need_multiple_bw` and
`atten.need_multiple_blended_bu`. **The 74.5 percent and 5.6 figures that the
last pass reported and that this brief restated were, until now, unresolvable
prose.**

`notes/draft-discussion.md` is added to the claim checker's `SCANNED` tuple.
Without that the file's markers would have been inert — the checker would have
passed while verifying nothing in it.

### Figures this section cites

The discussion cites **two** figures directly and neither is new:
`figures/capability.png` for §7's two limits, and
`figures/albedo_collinearity.png` for §6's first test. It also leans on
`figures/buffered_decay.png` for §4's structural claim, though the citation sits
more naturally in results.

**That leaves the two framework diagrams and the three land-cover provenance
figures still uncited by any section.** The figure audit had expected a
discussion to reach them; it does not. `framework_pipeline` and
`framework_reproduction` document the pipeline and the reproduction's structure,
which is repository material rather than argument, and `landcover_native`,
`urban_change` and `landcover_regional` are the predictors' provenance, which
belongs to methods and errata. **So the audit's expectation was wrong and the
five-figure count stands.**

### A figure this section wants and does not have

**The attenuation sweep**, recorded as a candidate in the previous pass, belongs
here rather than in results. §6's conclusion is a margin — the de-attenuated
coefficient against assumed error variance, with the observed product
disagreement marked, the spatial null as a horizontal reference, and the crossing
at 5.6 times visible as a distance. A reader who sees the distance does not need
the paragraph. It is a third figure in the capability family and it is not built.
