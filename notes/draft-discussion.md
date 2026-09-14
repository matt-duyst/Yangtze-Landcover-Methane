# Discussion, draft

Draft prose for the paper's final section. Every factual claim comes from a
committed record or a committed artefact, and every quoted number carries an
inline resolver naming the artefact quantity it reads from, on the convention
`scripts/verify_claims.py` enforces.

**The ordering, and why.** The results section reports a failed detection and an
observing-system assessment. This section has four jobs in a fixed order: say
what the result is and is not (§1), explain why it came out that way (§2 and §3),
show that the explanation is not an artefact (§4), and then generalise it — which
is where the contribution sits (§5). Only then does it locate the work against
prior results (§6) and say what would answer the original question (§7), closing
with limitations (§8). Mechanism precedes capability deliberately: the mechanism
explains this particular result, the capability limits explain why no refinement
of the same design would change it, and the second is only interesting once the
first is established.

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
predictor does not account for the result** — §4 gives the bound.

The reproduction's null is also not a finding that rice does not matter in this
domain. A tower inversion of this region in this study's own year found
agricultural soils to be the dominant driver of seasonal variability in
atmospheric methane. The two results are compatible and the difference between
them is the subject of this section: **a static annual land-cover fraction,
regressed against an annual column composite at 0.25 degrees, cannot recover
what a tower inversion recovers.** The question is why, and the answer has two
parts that are different in kind.

## 2. Extent is a proxy for presence, not for management

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
quality** — and it is why §7's routes are about priors, targeted observation and
isotopes rather than about better land-cover products.

## 3. What the predictors never contained

The second part is a different claim and should not be merged with the first.
§2 says a perfectly measured extent predictor would still fail. This section
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

## 4. Why the result is not an artefact

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

**Sampling composition.** Cell means rest on whichever days each cell was
observed, and mean day of year correlates with the operational field at
0.699<!--#deseason.doy_raw--> — a stronger association than either land-cover
predictor achieves. A deseasonalised field was therefore built by removing the
fitted seasonal cycle at the sounding level. The impervious association moved by
0.009<!--#deseason.impervious_change--> in Pearson correlation. **The calendar
does not explain the association's absence.**

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

## 5. What the observing system can and cannot constrain

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

## 6. Relation to prior results

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

## 7. What would be required to answer the original question

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
project has the tip and not the cue**, and §5's prior-free threshold is the
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

## 8. Limitations

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
rice product whose errors are independent of the layer in use, as §4 states.

**And the capability figures are a reimplementation rather than an inversion**,
bounded to this domain, this instrument and this period. The single free preview
run of the published tool would settle what this work estimates.

---

## Drafting notes, not part of the section

### Numbers not marked, and why

24 of this section's numbers carry resolvers; 81 do not. The unmarked ones fall
into four classes and only the last is a defect.

* **Section and year references** — §1 to §8, 2018, 2023, 0.25 degrees.
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
  accuracy figures in §8.
* **Figures derivable from marked ones or already exempted in the methods
  draft**, which lists them: the Anhui raster bound 33.3462° N, and the 20.7 and
  19.9 percent product differences. The Hefei counts were on this list and are
  now marked and resolved against `data/processed/tccon_hefei_2018.csv`.
* **One number that should be resolvable and is not**, reported rather than
  quietly dropped: **the fitted seasonal peak of the column field at day of year
  245.8**. It appears in `notes/decisions.md` and `notes/grounding-rice.md` as
  prose and in no committed artefact, so it cannot be marked. It is load-bearing
  in §7 — it is what makes EDGAR's uniform June peak "roughly ten weeks early
  here" — and it should have a row in `deseasonalisation_2018.csv`, which
  currently holds only the correlation table. Queued.

### Resolvers added for this draft

**Five**, all for `attenuation_bound_2018.csv`, because the two figures that
carry §4's conclusion had no way to be quoted. The artefact held the reliability
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
`figures/capability.png` for §5's two limits, and
`figures/albedo_collinearity.png` for §4's first test. It also leans on
`figures/buffered_decay.png` for §2's structural claim, though the citation sits
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
here rather than in results. §4's conclusion is a margin — the de-attenuated
coefficient against assumed error variance, with the observed product
disagreement marked, the spatial null as a horizontal reference, and the crossing
at 5.6 times visible as a distance. A reader who sees the distance does not need
the paragraph. It is a third figure in the capability family and it is not built.
