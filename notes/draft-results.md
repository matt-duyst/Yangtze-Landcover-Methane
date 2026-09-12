# Results

Draft for a paper, companion to [`notes/draft-methods.md`](draft-methods.md).
Past tense, journal register, no interpretation: the mechanisms belong in a
discussion section that does not yet exist. Numbers carry markers for
[`scripts/verify_claims.py`](../scripts/verify_claims.py); the closing note lists
the ones that could not be sourced and the resolvers added for this draft.

**The order puts the observing system first.** Under this work's framing the
characterisation of what the record can constrain is the contribution, not
preliminary material, so §1 reports the observing system, §2 the field it
produced, §3 the land-cover association, §4 the confounds, §5 the
cross-validation diagnostics and §6 the capability assessment. That is close to
the reverse of a conventional results order, which would put the association
first and the observing system in a supplement. The association is reported
before the capability assessment rather than after it because the capability
assessment is what explains it, and a results section should not explain.

## 0. The primary field

Four column fields were carried (methods §2.4) and three have complete baseline
suites. **The operationally bias-corrected field is reported as primary**, with
the blended and deseasonalised fields reported alongside it throughout rather
than relegated to a supplement. The grounds are set out here because the choice
affects how every number in §3 should be read.

The four fields differ modestly in spread and substantially in what they are.
Between-cell standard deviations over the 926<!--#composite.covered_cells-->
covered cells are 14.40<!--#field.sd_raw--> ppb for the raw retrieval,
14.86<!--#field.sd_operational--> ppb operationally corrected,
15.90<!--#field.sd_blended--> ppb blended and
13.26<!--#field.sd_deseasonalised--> ppb deseasonalised. The unweighted
regression slope of the field on shortwave-infrared albedo is
203.9<!--#albedo.slope_raw--> ppb per unit albedo raw,
199.7<!--#albedo.slope_corrected--> ppb operationally corrected,
172.5<!--#albedo.slope_deseasonalised--> ppb deseasonalised and
232.8<!--#albedo.slope_blended--> ppb blended; **the operational
correction itself carries a slope of only
-4.2<!--#albedo.slope_correction--> ppb per unit albedo**, so it removes
almost none of the field's albedo dependence, and **the blended field's slope is
the steepest of the four**, 16.6<!--#albedo.blended_over_corrected_percent--> %
above the operationally corrected field's, with Pearson rising from
0.700<!--#albedo.pearson_corrected--> to
0.762<!--#albedo.pearson_blended-->. §4.1 reports that comparison and what it
does and does not mean. And held-out R² for impervious
fraction under the block scheme is 0.085<!--#suite.impervious_operational-->
operationally corrected, 0.065<!--#suite.impervious_blended--> blended and
0.095<!--#suite.impervious_deseasonalised--> deseasonalised, against a spatial
null of 0.332<!--#suite.null_operational-->,
0.414<!--#suite.null_blended--> and
0.337<!--#suite.null_deseasonalised--> respectively.

The operational field was chosen for two reasons. It is the product's own
recommended variable, so a reader comparing this work with any other TROPOMI
study is comparing like with like. And the land-cover result is not sensitive to
the choice: the three suites bracket the impervious figure within 0.03 of R², and
the sign and the ordering against the spatial null are identical on all three.

**A third reason was offered in an earlier draft and is withdrawn.** It held
that the operational field was the only one for which every diagnostic exists,
the blended field having no measured albedo slope. That was an argument from a
gap in this work rather than from the fields, and it was also wrong: the
measurement existed and was simply absent from the artefact that would have
made it quotable. It is now in the artefact, it is reported above and in §4.1,
and it does not favour the operational field — it goes the other way, as the next
paragraph records.

**What a reader loses under this choice** is that the blended field is the better
field by its authors' own measurement — single-retrieval precision of 11.9 ppb
against the operational product's 14.5 ppb, and a reduction in spatially variable
bias against GOSAT from 14.3 to 10.4 ppb at 0.25 × 0.3125° — and reporting it
second understates that. The mitigation is that it is reported everywhere the
operational field is, with the same models and the same schemes, so the
comparison is available in every table rather than inferable from one.

**What a reader gains is the opposite of what was expected**, and it is the
reason the choice survives. On this composite the blended correction does not
reduce albedo-correlated structure; it increases it, on both albedo bands and at
both weightings. Those two statements are about different quantities — the
published reduction is measured against GOSAT as a reference, and the slope here
is fitted across an annual mean in which albedo is confounded with geography,
land cover and sampling season — so neither contradicts the other. §4.1 carries
the comparison and the caveat.

**One further consideration bears on how much this choice matters, and it cuts
toward "less than it appears."** This work's contribution is the
observing-system characterisation of §6, and that characterisation is largely
field-independent: expected degrees of freedom depend on observation counts and
geometry, transport error is a property of the model, and identifiability is a
property of the prior's spatial structure. None of the three depends on which
bias correction was applied to the retrieval. The primary-field decision
therefore bears on §3, the land-cover result the paper still has to report, and
barely on the headline claim. That asymmetry is the reason this section can be
short.

## 1. The observing system

### 1.1 Coverage

The 2018 composite rests on 110,920<!--#composite.soundings--> qualifying
soundings from 223<!--#composite.granules_with_data--> productive granules of
578<!--#composite.granules_gridded--> candidates. They cover
926<!--#composite.covered_cells--> of the 1,023<!--#composite.total_cells-->
lattice cells, 90.52<!--#composite.coverage_percent--> %. Per-cell sounding
counts run from 1<!--#composite.min_soundings--> to
410<!--#composite.max_soundings--> with a median of
74<!--#composite.median_soundings-->, a spread of more than two orders of
magnitude across cells whose areas differ by under 15 %.

Coverage saturates well before the end of the record. Cell coverage as a function
of granules processed rises steeply over the first weeks and then flattens: the
marginal granule adds soundings to cells already observed rather than new cells,
so the 97 uncovered cells are not uncovered for want of record length.

**Coverage is, however, the quantity this work measured, and it is not the
quantity that would characterise representativeness error.** Schutgens et al.
(2017) show that even after substantial averaging significant representation
errors may remain, larger than typical measurement errors, and state directly
that "observational coverage (a measure of how dense the spatio-temporal
sampling of the observations is) is not an effective metric to limit
representation errors". No representativeness-error estimate was computed for
this composite. The coverage statistics below therefore describe the sampling
and do not bound the error it induces.

### 1.2 Where the gaps are

The 97<!--#composite.uncovered_cells--> uncovered cells are not distributed at
random. 74<!--#composite.absent_on_land--> lie wholly on land, and their median
elevation is 502<!--#composite.absent_median_elevation--> m against
35<!--#composite.covered_median_elevation--> m for covered cells;
50<!--#composite.absent_above_500m--> sit above 500 m, against
24<!--#composite.covered_above_500m--> of the 926. They form
19<!--#composite.absent_components--> connected components, the largest of which
is 47<!--#composite.largest_absent_block--> cells over the mountains on the
southern edge of the domain.

Coverage is also weak, rather than absent, along the coast: the median sounding
count for cells with a substantial sea fraction is
6<!--#composite.coast_median_soundings--> against
133<!--#composite.land_median_soundings--> for cells that are wholly land. The
two effects are in opposite directions on the map and the same direction in
their consequence — the annual mean of a coastal cell and of an upland cell rest
on very different amounts of evidence from the annual mean of an inland lowland
cell.

### 1.3 Sampling through the year

The 2018 record is an eight-month record, beginning 30 April. Within those eight
months yield is strongly uneven and the unevenness runs against the rice growing
season: October alone carries more soundings than June, July, August and
September combined. These monthly counts are computed from per-granule
acquisition times retained in a gitignored checkpoint and are therefore
reproducible only where that file exists; they are stated in the region record
and are not marked here.

## 2. The methane field

### 2.1 Distribution

On the operationally corrected field the covered cells span
106.1<!--#baseline.observed_span_ppb--> ppb between their extreme values, with a
between-cell standard deviation of 14.86<!--#field.sd_operational--> ppb. The
operational correction raises the field by a mean of
11.64<!--#composite.bias_mean--> ppb relative to the raw retrieval.

### 2.2 Spatial structure

The field is strongly spatially autocorrelated. Moran's *I* is
0.7085<!--#residual.observed_moran--> under a permutation test with
999<!--#residual.permutations--> permutations. An exponential semivariogram
fitted to the field itself gives a half-sill range of
103.2<!--#range.operational_field_km--> km on the operational field and
139.1<!--#range.blended_field_km--> km on the blended field.

Both ranges exceed the narrower dimension of the cross-validation block, which is
95.0<!--#range.block_ew_km--> km east-west against
111.2<!--#range.block_ns_km--> km north-south. The consequence for the
cross-validation is reported in §5.

### 2.3 Differences between the fields

The four fields agree on the field's large-scale structure and differ in their
residual artefact content. The blended field has the largest between-cell spread
of the four at 15.90<!--#field.sd_blended--> ppb and the deseasonalised field the
smallest at 13.26<!--#field.sd_deseasonalised--> ppb, which is the expected
ordering: a machine-learning correction trained against an independent instrument
adds variance where the operational product was over-smoothed, and removing a
seasonal cycle removes variance that the sampling calendar had imposed.

## 3. The land-cover association

### 3.1 Zero-order correlations and their effective degrees of freedom

Impervious fraction correlates with the operationally corrected field at
Pearson *r* = 0.345<!--#collinear.zero_order--> unweighted over all 926 cells,
and at 0.212<!--#collinear.zero_order_weighted--> when cells are weighted by
sounding count. On the raw retrieval the unweighted figure is
0.440<!--#collinear.zero_order_raw-->.

**Those coefficients rest on far fewer independent observations than 926.**
Correcting the degrees of freedom for spatial dependence by the modified *t*-test
of Clifford, Richardson and Hémon reduces the effective sample size across the
72<!--#dof.rows--> reported associations to a median of
53.4<!--#dof.effective_n_median--> cells, with a range from
11.4<!--#dof.effective_n_min--> to 185.7<!--#dof.effective_n_max--> — that is, to
between 2.0<!--#dof.shrinkage_min_percent--> and
25.2<!--#dof.shrinkage_max_percent--> % of nominal.

**27<!--#dof.verdict_changed--> of the 72 associations that reach significance at
the 5 % level on nominal degrees of freedom do not reach it after correction.**
Those 27 include every weighted land-cover association and every partial
correlation controlling for albedo on the operational field. The corrected test
changes no coefficient; it changes whether the coefficient can be distinguished
from zero.

### 3.2 Partial correlations controlling for albedo

Controlling for shortwave-infrared albedo removes almost all of the association.
The impervious–methane partial correlation is
0.021<!--#collinear.partial--> on the operational field, against a zero-order
0.345<!--#collinear.zero_order-->, with *p* =
0.53<!--#collinear.partial_p--> on corrected degrees of freedom. Weighted by
sounding count the partial is 0.032<!--#collinear.partial_weighted--> at *p* =
0.32<!--#collinear.partial_weighted_p-->. On the raw retrieval the partial is
larger, 0.151<!--#collinear.partial_raw-->, and retains nominal significance.

Control for albedo therefore removes
94.0<!--#collinear.partial_attenuation_percent--> % of the zero-order
coefficient on the unweighted operational field.

### 3.3 Held-out performance against the baselines

Held-out R² for the operationally corrected field, by scheme and weighting:

| Model | blocks, unweighted | blocks, weighted | province, unweighted | province, weighted |
|---|---|---|---|---|
| Impervious fraction | 0.085<!--#suite.impervious_operational--> | 0.024<!--#suite.impervious_operational_weighted--> | -0.117<!--#suite.impervious_operational_lopo--> | −0.162 |
| Rice fraction | -0.031<!--#baseline.rice_alone_r2--> | −0.093 | −0.067 | −0.414 |
| Both fractions | 0.017<!--#baseline.rice_plus_impervious_r2--> | −0.078 | −0.129 | -0.845<!--#suite.both_operational_lopo_weighted--> |
| Spatial null | 0.332<!--#suite.null_operational--> | 0.514 | −0.091 | 0.003 |
| Albedo (SWIR) | 0.476<!--#suite.albedo_operational--> | 0.316 | 0.290 | 0.066 |
| Wind (u, v, speed) | 0.653<!--#baseline.wind_r2--> | 0.563 | 0.633 | 0.311 |
| Global-mean constant | -0.008<!--#baseline.constant_r2--> | −0.003 | −0.172 | −0.085 |

**Land cover's held-out skill is positive in one of the four scheme-weighting
combinations and negative in three.** Where it is positive it is below the
spatial null by a factor of four and below wind by a factor of eight. Adding rice
fraction to impervious fraction lowers held-out skill in every combination.
Root mean squared error for the impervious model is
14.2<!--#baseline.impervious_rmse--> ppb against a field spread of
106.1<!--#baseline.observed_span_ppb--> ppb, and its predictions span
42.7<!--#baseline.impervious_span_ppb--> ppb.

The same pattern holds on the other two fields (§0): impervious fraction reaches
0.065<!--#suite.impervious_blended--> on the blended field and
0.095<!--#suite.impervious_deseasonalised--> on the deseasonalised field under
blocks and no weighting, in both cases well below that field's spatial null.

### 3.4 The form of the negative result

**No association between land cover and the methane field was detected that
survives correction for spatial dependence, control for albedo, or held-out
evaluation under more than one scheme.** That is a statement about a failed
detection and it is the strongest form the evidence supports.

It is not a statement that no association exists. A claim in favour of a null
hypothesis requires equivalence testing against a named smallest effect size of
interest, and no equivalence bounds were set in this work; conventional *p*-value
analysis can argue against a null hypothesis and not in favour of one. Setting
such bounds is queued and not done, so no result here should be read as
establishing the absence of an effect.

## 4. Confounds, each with its measurement

### 4.1 Albedo collinearity

The albedo–methane relationship is stronger than the land-cover relationship, and
albedo is itself correlated with the predictor. Shortwave-infrared albedo
correlates with the operational field at
0.700<!--#collinear.methane_albedo--> unweighted and with impervious fraction at
0.475; near-infrared albedo correlates with the field at 0.746. The albedo model
alone reaches held-out R² 0.476<!--#suite.albedo_operational--> under blocks and
no weighting, five times the impervious model's.

**The field carries a residual albedo dependence after the operational
correction, and the correction is not what removes it.** The raw field's slope on
shortwave-infrared albedo is 203.9<!--#albedo.slope_raw--> ppb per unit albedo
and the corrected field's is 199.7<!--#albedo.slope_corrected-->; the correction
itself has a slope of -4.2<!--#albedo.slope_correction--> ppb per unit albedo, so
it reduces the field's albedo dependence by
2.1<!--#collinear.reduction_percent--> % unweighted and
31.3<!--#collinear.reduction_weighted_percent--> % weighted by sounding
count.

**Applying the blended correction to this composite increases the dependence
rather than reducing it.** Its shortwave-infrared slope is
232.8<!--#albedo.slope_blended--> ppb per unit albedo unweighted, which is
16.6<!--#albedo.blended_over_corrected_percent--> % above the operationally
corrected field's, with Pearson rising from
0.700<!--#albedo.pearson_corrected--> to
0.762<!--#albedo.pearson_blended-->; the near-infrared band behaves the same way
and both weightings agree in sign. The association survives correction for
spatial dependence, at an effective sample size of 18.5 cells of 926.

**That is a statement about this composite and not about the product, and the
distinction has to be held.** The published claim for the blended dataset is a
reduction in spatially variable bias measured against GOSAT as a reference, which
is a different quantity from a slope fitted across an annual mean in which albedo
is confounded with geography, land cover and sampling season. The slope reported
here absorbs everything that varies spatially with albedo and is an upper bound
on residual albedo sensitivity rather than a measurement of it. What can be said
without qualification is narrower: a per-sounding correction referenced to a
sparse instrument is not obliged to reduce the between-cell variance of an annual
composite, and on this composite it does the opposite.
166<!--#cov.albedo_negative--> cells, 17.9<!--#collinear.negative_percent--> % of
the covered lattice, carry a negative annual-mean shortwave-infrared albedo,
which is unphysical.

Every result in §3 is therefore a result from a field with a known, unremoved
albedo dependence, and the partial correlations of §3.2 are the measurement of
how much of the association that dependence accounts for. Methods §2.5 records
that no albedo floor and no retrieval-precision filter were applied; the blended
field is the only one of the four that addresses albedo by construction, and the
association is weaker on it than on the operational field.

### 4.2 Sampling composition

Cell means rest on whichever days each cell was observed, and those differ. Mean
day of year correlates with the operational field at
0.699<!--#deseason.doy_raw--> unweighted — a stronger association than either
land-cover predictor achieves. Solar zenith angle, which is partly a proxy for
the same thing, correlates at 0.695.

### 4.3 Whether the calendar explains the association

The deseasonalised field answers this directly, and it is the first use made of
that field. Removing a region-wide seasonal cycle at the sounding level reduces
mean day of year's own correlation with the field from
0.699<!--#deseason.doy_raw--> to 0.629<!--#deseason.doy_mu-->, so the procedure
does remove part of the calendar signal.

**It does not change the land-cover association.** Impervious fraction's
correlation with the field moves from 0.345<!--#deseason.impervious_raw--> to
0.354<!--#deseason.impervious_mu-->, a change of
+0.009<!--#deseason.impervious_change-->. Rice fraction's moves from
0.096<!--#deseason.rice_raw--> by
-0.0052<!--#deseason.rice_change-->. The land-cover association is neither
created nor removed by the sampling calendar, and the held-out figures in §3.3
are correspondingly similar on the two fields.

## 5. Cross-validation diagnostics

### 5.1 Residual autocorrelation against block size

Exponential semivariograms were fitted to each model's residuals on each field,
and the half-sill range compared with the block dimensions of
111.2<!--#range.block_ns_km--> by 95.0<!--#range.block_ew_km--> km. Of the
10<!--#range.models--> model-field combinations,
4<!--#range.too_small--> leave residuals still correlated at a block width.

The impervious model's residual half-sill range is
96.1<!--#range.operational_impervious_km--> km on the operational field and
134.5<!--#range.blended_impervious_km--> km on the blended field. Models that
include the albedo covariates decorrelate far sooner, at
22.5<!--#range.operational_full_km--> km or less on the operational field.
**So the block scheme is too small for the land-cover models and ample for the
covariate models**, and no single block size is correct for both.

### 5.2 The buffered decay curve

Held-out R² was recomputed with each cell withheld together with every cell
within a radius of it, from 0 to 500 km, and reported as skill above a constant
fitted on the same training data.

The spatial null behaves as a spatial predictor must: its advantage over a
constant falls from +0.687<!--#loo.null_0km--> at no buffer to
0.000<!--#loo.null_50km--> at 50 km, once the buffer exceeds one cell and its
neighbours are all excluded.

**Land cover does not behave as a non-spatial predictor should.** A model using
no spatial information ought to be indifferent to how far its training data lie
from the withheld cell. Instead the impervious model's advantage decays steadily:
+0.118<!--#loo.impervious_0km--> at no buffer,
+0.089<!--#loo.impervious_100km--> at 100 km,
+0.007<!--#loo.impervious_300km--> at 300 km, and negative beyond. On the blended
field it reaches zero by 200 km. **The impervious coefficient is therefore not
stable across the domain**: what skill it has is local, and it disappears when
the training data are more than about 300 km away.

### 5.3 The two schemes bracket

Leave-one-province-out and 1° spatial blocks give systematically different
figures for the same model, and the decay curve places the land-cover model's
skill between them at the radii the two schemes correspond to. The two schemes
are therefore reported separately throughout and neither is preferred; the
difference between them is a measurement of the model's spatial instability
rather than a disagreement about its skill.

## 6. Capability of the observing system

### 6.1 Expected degrees of freedom for signal

Expected degrees of freedom for signal were computed from the closed-form
estimate published for the Integrated Methane Inversion's preview facility, with
that tool's defaults, and per-cell observation counts derived from the granule
record: a median of 23.0<!--#dofs.days_median--> observation days per covered
cell and 4.4<!--#dofs.retrievals_median--> retrievals per super-observation.
**These are reimplemented estimates and not inversion output**: no transport
model was run, no Jacobian was constructed and no emissions were optimised.

Expected DOFS over the domain is 1.44<!--#dofs.at_3tg--> at a 3 Tg a⁻¹ prior,
3.98<!--#dofs.at_5tg--> at 5 Tg a⁻¹ and
22.21<!--#dofs.at_12tg--> at 12 Tg a⁻¹.

**At no point in the sweep does any cell reach an averaging-kernel sensitivity
above 0.5** — the count is 0<!--#dofs.cells_above_half--> at every prior
magnitude tested. The DOFS total accumulates from 926 weakly constrained cells
rather than from a few well constrained ones.

### 6.2 The prior-free threshold

The sensitivity expression can be inverted without assuming any prior, because at
a given sensitivity it depends only on the observation counts. **A median cell in
this composite would need 0.0862<!--#dofs.prior_free_median--> Tg a⁻¹ — about
86 Gg a⁻¹ from a single 625 km² cell — for the observations to constrain it half
independently of the prior.** The best-observed cell, with 65 observation days,
would need 0.0492<!--#dofs.prior_free_best--> Tg a⁻¹.

For scale, a large municipal landfill emits on the order of 10 to 50 Gg a⁻¹.
**Individual large point sources in this domain therefore sit below a
sensitivity of 0.5 and above zero**: visible to an inversion as a partial
constraint weighted toward the prior, not as an independent measurement. This is
the most concrete available statement of the information-content limit, and it is
prior-free, so it does not inherit the factor-of-two uncertainty in the domain's
emission total.

### 6.3 Identifiability

Information content bounds how much can be recovered from the observations. It
does not bound whether what is recovered can be attributed to a sector.

The evidence that attribution derives from the prior rather than from the
observations is a contrast within a single published inversion. Where a sector's
prior is allocated on facility coordinates and is spatially distinct — landfills
in the US gridded inventory — posterior error correlations with other sectors
fall below 0.35 and the sector can be quantified. Where sectors' priors share a
population allocation surface — downstream gas, wastewater treatment and
stationary combustion — posterior error correlations among them run 0.45 to 0.87
and their separation is limited and weighted by the prior. The same instrument,
inversion and domain separate one sector and fail to separate three, and the only
difference is the priors' spatial structure.

The sources in this domain are interspersed at the scale of the analysis cell.
Paddy rice and freshwater aquaculture occupy the same flooded lowland; rice and
natural wetland overlap in the wetland priors by those products' own account;
four urban sectors share one population-like surface inside the same city cells;
and coal mining in northern Anhui lies adjacent to and partly inside the cells
where the rice classification stops, which is
86.11<!--#rice.anhui_coverage_percent--> % of that province.

**The two limits are independent.** Additional observations raise expected
degrees of freedom and do not make a prior more spatially distinct; a better
prior sharpens attribution and adds no information the observations do not carry.

### 6.4 Relation to §3

The land-cover result of §3 is the empirical counterpart of §6.1. A record whose
degrees of freedom accumulate from uniformly weak per-cell sensitivity is a
record in which per-cell predictors should fail, and §3 reports that they do
across two urban products, two rice products, two cross-validation schemes, two
weightings and three target fields. No causal inference is drawn here; the
correspondence is reported and its interpretation belongs in a discussion.

## 7. Reproducibility of the reported figures

56<!--#pipeline.recipes--> derived artefacts are registered with the command that
produces them and a verification tier.
30<!--#pipeline.recipes_committed--> regenerate from a fresh clone with no network
and no local data and are re-executed and compared byte for byte on every test
run; 17<!--#pipeline.recipes_local--> require local raw data;
8<!--#pipeline.recipes_network--> require a network fetch. Every numeric claim in
this section carries an inline marker naming the artefact quantity it comes from,
and a test recomputes each from the artefact.

---

## Drafting notes, not part of the section

### Figures this section would cite

| Result | Figure | State |
|---|---|---|
| §1.1 coverage saturation | `coverage_saturation_2018` | exists; the only figure whose subject is the observing system |
| §1.2 where the gaps are | `study_area` | exists; carries the terrain and the absent-cell block |
| §2 the field | `methane_composite_2018` | exists |
| §3.3 held-out performance | `observed_predicted` | exists |
| §3.3, §5 residual structure | `residual_field` | exists |
| §4.1 albedo collinearity | `albedo_collinearity` | exists |
| §3 land-cover predictors on the lattice | **none** | planned, not built: predictor maps |
| §5.1–5.3 the fold geometry | **none** | planned, not built: fold map |
| §4.2 sampling composition | **none** | planned, not built: sampling-artefact map |
| §5.2 the buffered decay curve | **none** | not planned; this is the new gap |
| §6.1–6.2 the DOFS sweep and the prior-free threshold | **none** | not planned; this is the second new gap |

**Two results central to the contribution have no figure and none is planned.**
The buffered decay curve is the direct measurement of the impervious
coefficient's spatial instability and exists only as a ten-row table per field.
The DOFS sweep and the prior-free threshold are the capability claim itself and
exist only as a twenty-row table. Under the earlier framing neither was a
headline; under this one both are, and a reader of §5.2 and §6 has nothing to
look at. Both are line plots over a swept parameter and neither needs new data.

**Three figures the set holds that this section does not cite.**
`landcover_native`, `urban_change` and `landcover_regional` answer to the 2023
thesis's land-cover figures. They document the predictors' provenance and
disagreements, which is methods material and errata material rather than
results. `framework_pipeline` and `framework_reproduction` are documentation of
the pipeline and of the reproduction's structure and belong in neither section.
**That is five of eleven figures with no place in a results section**, which is
not an argument for deleting them — three are the predictors' own record — but is
an argument for building the two missing capability figures before the three
planned ones.

### Numbers without a resolver

* The monthly sounding distribution, computed from a gitignored checkpoint.
* The coverage saturation curve's shape, described qualitatively because the
  figure holds it and no scalar summarises it.
* The albedo–impervious and albedo–NIR zero-order correlations (0.475, 0.746) and
  the solar-zenith correlation (0.695), which are in
  `albedo_confounder_2018.csv` and have no resolver.
* Six cells of the §3.3 table, being the weighted and leave-one-province-out
  figures for rice and for both fractions; the eleven marked cells cover the
  reported claims and the rest are read from the artefact.
* The blended field's single-retrieval precision figures, 11.9 against 14.5 ppb,
  which come from the product's paper rather than from this work.
* All literature figures in §6.3, and the 10-to-50 Gg landfill scale in §6.2.

### Resolvers added for this draft

**Thirty**, for artefacts whose numbers the results section needs and which had
none: the four fields' between-cell spreads; the albedo slopes for the
deseasonalised series and for the correction itself; ten cells of the
three-suite baseline comparison; the seven deseasonalisation comparisons; the
median effective sample size and the two shrinkage bounds as percentages; the
two prior-free emission thresholds; the two field-level semivariogram ranges;
and the attenuation of the impervious coefficient under control for albedo.

**That last one was added because a first draft attached a sentence to the wrong
existing quantity.** `collinear.reduction_percent` measures how much the
operational bias correction reduces the field's albedo slope, which is 2.1 %
unweighted. The draft used it for how much control for albedo reduces the
impervious coefficient, which is 94.0 %. Both numbers belong in the section and
they are not the same measurement; the claim checker caught the substitution
because the value it resolved to was two orders of magnitude from the one
written.

**One resolver was attempted, removed, and then added on 16 September 2026**,
after the blended series was added to `albedo_correction_2018.csv`. The
measurement had existed in the decision log throughout; what was missing was a
row in the artefact, so nothing could resolve it. That distinction matters
because a first draft of §0 mistook the second for the first and built a
primary-field justification on it, which is now withdrawn.
