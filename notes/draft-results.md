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
fraction, under spatial blocks without weighting, is
0.085<!--#suite.impervious_operational--> operationally corrected,
0.065<!--#suite.impervious_blended--> blended and
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

**The result is reported as the range across those four combinations rather
than as any one of them**, because the spread is a property of the evaluation:
impervious fraction's four-way range is
0.247<!--#spread.impervious--> of R², the smallest of any predictor in the
suite, against 0.342<!--#spread.wind--> for wind,
0.410<!--#spread.albedo--> for albedo,
0.605<!--#spread.null--> for the spatial null and
0.708<!--#spread.sampling--> for sampling composition. Where a single figure is
quoted it is the spatial-blocks unweighted combination, which §5.1 establishes is
the optimistic end of the bracket.

**So land cover's held-out skill on the primary field lies between
-0.162 and +0.085 across four defensible evaluation designs.** Raw held-out R² is
positive in one of the four; above a constant fitted on the same training data it
is positive in three, at
+0.093<!--#above.impervious_bu-->, +0.028<!--#above.impervious_bw-->,
+0.055<!--#above.impervious_pu--> and
-0.077<!--#above.impervious_pw-->, the difference being that
leave-one-province-out penalises the constant itself by −0.172. Adding rice
fraction to impervious fraction lowers held-out skill in every combination.
Root mean squared error for the impervious model is
14.2<!--#baseline.impervious_rmse--> ppb against a field spread of
106.1<!--#baseline.observed_span_ppb--> ppb, and its predictions span
42.7<!--#baseline.impervious_span_ppb--> ppb.

**No land-cover model achieves positive held-out skill where the spatial null
also does**, on any of the three fields under any of the four combinations.
Three of the twelve field-scheme-weighting combinations show a land-cover model
above the null on the above-constant metric, all three under
leave-one-province-out without weighting, and in all three both models are
negative in raw held-out R²: on the primary field rice fraction combined reaches
-0.059<!--#suite.rice_combined_pu--> against the null's
-0.091<!--#suite.null_operational_pu-->.

The same pattern holds on the other two fields (§0): impervious fraction reaches
0.065<!--#suite.impervious_blended--> on the blended field and
0.095<!--#suite.impervious_deseasonalised--> on the deseasonalised field under
blocks and no weighting, in both cases well below that field's spatial null.

### 3.4 The association on seasonal composites

The three subsections above measure an annual composite. **An annual mean is the
wrong object for a seasonal source**, and paddy methane is seasonal: a flooded
paddy emits and a drained one does not. An annual null is therefore consistent
with two seasonal signals of opposite sign cancelling, and no annual number
distinguishes that case from an absence. This subsection distinguishes them.

Composites were formed over whole months from the monthly partial sums the
compositing pass retained (methods §3), so no re-gridding was required. Five
windows were taken: the year, a flooded window of May to August, a growing
window of June to September, October alone — which carries
34,182<!--#seasonal.october_soundings--> of the year's soundings — and an
off-season window of November and December. The growing-season composite covers
870<!--#seasonal.growing_cells--> cells on
30,684<!--#seasonal.growing_soundings--> soundings with a between-cell standard
deviation of 23.23<!--#seasonal.growing_sd--> ppb, against
7.84<!--#seasonal.off_sd--> ppb in the off-season window.

**The comparison is made on cells common to every window**, because a cell
observed in October and not in June would otherwise contribute to one window
and not another, making a between-window difference partly a difference between
samples. Requiring at least fifteen soundings in every window leaves
366<!--#seasonal.impervious_cells--> cells, of which
262<!--#seasonal.rice_cells--> carry a rice fraction.

**The rice association changes sign with the season and the impervious
association does not.**

| window | rice fraction | impervious fraction |
|---|---|---|
| year | -0.056<!--#seasonal.rice_annual--> | +0.064<!--#seasonal.impervious_annual--> |
| May–August, flooded | +0.093<!--#seasonal.rice_flooded--> | −0.067 |
| June–September, growing | +0.138<!--#seasonal.rice_growing--> | −0.022 |
| October | -0.194<!--#seasonal.rice_october--> | +0.097 |
| November–December, off-season | -0.273<!--#seasonal.rice_off--> | +0.072 |

The within-cell contrast is the cleaner statistic, because differencing two
windows in the same cell removes every time-invariant cell property —
position, elevation, mean albedo, province, and the sampling composition of
§4.2 insofar as it is fixed. **The flooded-minus-off-season contrast correlates
with rice fraction at +0.225<!--#seasonal.rice_contrast--> at a slope of
15.90<!--#seasonal.rice_contrast_slope--> ppb per unit fraction, and with
impervious fraction at -0.095<!--#seasonal.impervious_contrast-->.** The
contrast is therefore specific to the rice predictor and absent for the urban
one. Both rice definitions give it: `rice_fraction_single` yields
+0.204<!--#seasonal.rice_single_contrast-->.

**No window and no contrast survives correction for spatial dependence.** The
contrast's nominal *p* is
0.00024<!--#seasonal.rice_contrast_p_nominal--> and its corrected *p* is
0.132<!--#seasonal.rice_contrast_p_corrected-->, at an effective sample size of
46.0<!--#seasonal.rice_contrast_effective_n--> cells of 262. The
growing-minus-off contrast gives
0.17<!--#seasonal.rice_growing_contrast_p_corrected--> and the off-season level
0.079<!--#seasonal.rice_off_p_corrected-->, the closest any test comes. Every
impervious test is null in every window, the contrast at *p* =
0.53<!--#seasonal.impervious_contrast_p_corrected-->.

**Stated as the table's own summary, which is the form that prevents
over-reading it: of 90<!--#seasonal.tests--> correlation tests,
39<!--#seasonal.nominal_significant--> reach the 5 percent level on nominal
degrees of freedom and 1<!--#seasonal.corrected_significant--> does after
correction, against 4.5<!--#seasonal.chance_expected--> expected by chance at
that level.** Fewer survive than chance alone would produce, and the one that
does is a flooded-window impervious association on the raw retrieval, which is
not a reported field.

**Nor does the contrast predict out of sample.** Evaluated as a target under the
same design §3.3 uses — spatial blocks, unweighted — the rice model on the
contrast reaches a held-out R² of
-0.052<!--#seasonal.predictor_r2_contrast-->, below a constant, against the
spatial null's +0.188<!--#seasonal.null_r2_contrast--> on the same cells. For
impervious fraction the figures are
-0.032<!--#seasonal.predictor_r2_contrast_impervious--> against
+0.306<!--#seasonal.null_r2_contrast_impervious-->. So the ordering of §3.3 is
reproduced on the seasonal estimand: the predictor is beaten by smoothness, and
by a constant.

**Two properties bound how far the sign reversal can be read, and both go
against it.**

*It decays as the sample grows.* Relaxing the requirement from every window to
the two windows the contrast uses takes it from +0.225 on 262 cells to
+0.122<!--#seasonal.contrast_pair10--> on
315<!--#seasonal.contrast_pair10_cells--> cells at ten soundings a window, and
to +0.070<!--#seasonal.contrast_pair5--> on
359<!--#seasonal.contrast_pair5_cells--> at five. A result that strengthens on
more cells would be more credible; this one weakens.

*It is much weaker on the raw retrieval.* The same contrast on the raw field is
+0.081<!--#seasonal.raw_contrast--> at *p* =
0.56<!--#seasonal.raw_contrast_p_corrected-->, against +0.225 on the
operationally corrected field. The operational correction's terms vary
seasonally, so the contrast may be a property of the correction rather than of
the atmosphere. **That possibility is not excluded.**

**And the precision that would settle both is not available.** The retained
sums include monthly sums of the field and not monthly sums of squares, so a
seasonal composite carries a mean and **no per-cell standard error**. There is
no within-cell variance by month, so no per-cell significance, and no
inverse-variance weighting — which is why this subsection reports corrected
correlations rather than the held-out R² of §3.3, whose weighted schemes
require per-cell precision. The decay in the paragraph above has two readings —
the contrast is partly noise, or the cells added by a weaker window definition
have window means too noisy to carry it — and **the same missing quantity is
what prevents distinguishing them.**

### 3.5 The form of the negative result

**No association between land cover and the methane field was detected that
survives correction for spatial dependence, control for albedo, or evaluation
under more than one held-out design.** That is a statement about a failed
detection and it is the strongest form the evidence supports.

**§3.4 adds 90 tests to that statement and does not change it.** The seasonal
composites yield a rice association of the predicted sign in the predicted
window, and no window and no contrast survives the correction for spatial
dependence, and the contrast is beaten by a constant out of sample. The one
addition the seasonal work makes to the *form* of the result is that **the
annual null is a cancellation rather than a flat absence** — two seasonal
associations of opposite sign, each unresolvable — which is a more specific
description of the same non-detection and not a weaker one.

**Equivalence bounds were set, and they license more for rice than for
impervious cover.** A claim in favour of a null requires equivalence testing
against a named smallest effect size of interest, because conventional analysis
can argue against a null and not in favour of one. The bound taken here is
comparative — the spatial null's held-out performance expressed as a
correlation, |r| = 0.58<!--#equiv.bound_comparative--> — because this paper's
claim is comparative and a comparative bound introduces no arbitrary fraction.
Two one-sided tests are assessed on a 90 percent interval with effective
degrees of freedom throughout.

Across 36<!--#equiv.rows--> combinations of field, predictor and weighting,
**0<!--#equiv.outside_comparative--> fall outside the bounds**, so no
specification yields a positive result.
31<!--#equiv.within_comparative--> fall entirely within them and
5<!--#equiv.spanning_comparative--> span a bound.

The split is not even between the predictors, and the difference is the
result. **For rice, all 24<!--#equiv.rice_within--> of
24<!--#equiv.rice_rows--> combinations fall entirely within the bounds**: the
rice association is smaller than the spatial benchmark's in every field and
every weighting, which is evidence of no meaningful effect rather than a failure
to detect one. **For impervious cover only
7<!--#equiv.impervious_within--> of 12<!--#equiv.impervious_rows--> do**, and
the other 5<!--#equiv.impervious_spans--> span the bound, so for impervious the
data cannot distinguish an effect the size of the benchmark's from none, and the
weaker non-detection claim is what stands.

**The bounds were computed on the annual estimand, and the seasonal estimand of
§3.4 is a second one.** Whether the equivalence statement extends to it is a
real question, because a within-cell seasonal contrast is a different quantity
on a smaller sample and was not among the 36 combinations. It was therefore
tested the same way, with the bound reconstructed on the contrast itself as
well as taken from the annual field.

**It extends, with one exception at the margin.** Of twelve verdicts — two
contrasts × three predictors × two bounds — eleven fall within the bounds.
Against the annual bound of |r| =
0.58<!--#seasonal.equiv_bound_annual--> every contrast is equivalent. Against
the bound reconstructed on the contrast field, |r| =
0.43<!--#seasonal.equiv_bound_seasonal--> for the flooded-minus-off contrast,
the combined rice fraction's 90 percent interval reaches +0.446 and **spans**,
so for that one combination the data cannot distinguish an effect the size of
the seasonal benchmark's from none. The single-season rice definition on the
same contrast falls within at +0.428, and both rice definitions on the
growing-minus-off contrast fall within.

**So the rice half of the equivalence claim is annual, and the paper should say
so.** For the annual field the stronger statement stands, in all 24
combinations. For the seasonal contrast it stands in five of six and the sixth
is a non-detection rather than evidence of absence. That is a narrower change
than it might appear — no verdict moves outside the bounds, so no specification
in either estimand yields a positive result — but the scope of the word
"equivalent" now has to name which estimand it is about.

**What the bound does not license.** An effect smaller than the spatial
benchmark's but still physically substantial would pass as equivalent. The
policy-relevant bound — what a land-cover effect would have to be to matter for
an inventory — could not be set, because the literature bounds *emissions* and
converting an emission change to a column change needs the transport model this
work does not run.

**The one mechanism that could manufacture this result is measurement error in
the predictors, and for the impervious layer it is now bounded and excluded.**
Measurement error in a predictor attenuates its coefficient toward zero, so it
is the only confound that could produce a null from a real association rather
than explain the absence of one.

No accuracy assessment of either layer was performed, because no reference layer
over this domain is more accurate than the products used (methods §7), so
neither layer's error variance is known directly. The two independently produced
impervious products supply it as a bound instead. With the GAIA cell fraction as
the predictor in use and the GISA fraction as a second measurement of the same
quantity, their difference has variance
0.002066<!--#atten.var_d-->, which is
13.2<!--#atten.var_share_pct--> % of the predictor's own variance of
0.015631<!--#atten.var_x-->; the two correlate at
0.938<!--#atten.corr-->. If the two products' errors are independent of each
other, that difference variance is an **upper bound** on the error variance of
either, so the reliability ratio is at least
0.868<!--#atten.lambda_min--> and **the largest factor by which measurement
error could be deflating the coefficient is
1.15<!--#atten.factor_max-->.**

**That is not enough to reach the reference the result is judged against.** On
the combination where land cover performs best — the operational field, spatial
blocks, unweighted — the impervious model's held-out R² of
+0.085<!--#suite.impervious_operational--> bounds upward to
+0.098<!--#atten.r2_bound_bu-->, against the spatial null's
+0.332<!--#suite.null_operational--> on the same combination. The coefficient
bounds from 41.0 ppb per unit fraction to
47.3<!--#atten.coef_bound-->. On the blended field the bound is
+0.075<!--#atten.r2_bound_blended_bu--> against a null of
+0.414<!--#suite.null_blended-->. Under leave-one-province-out the impervious
held-out R² is negative and de-attenuation does not apply at all, a negative
held-out R² not being a squared correlation.

**Put inversely, which is the form that shows the margin: for measurement error
to lift the land-cover coefficient to the spatial null's performance, 74.5
percent of the variance in the impervious fraction would have to be error** —
5.6 times what the two products' disagreement supports, and 7.2 times on the
sounding-weighted combination.

So measurement error in the impervious layer is excluded as an explanation for
the reported null, to within the assumptions stated in methods §4.3: that the
two products' errors are independent of each other, and that the error is
homoscedastic and non-differential. **The second and third are measurably
violated and in the unfavourable direction**, the error's standard deviation
rising thirty-one-fold from the lowest to the highest quartile of the fraction,
with a partial correlation of −0.118 against methane given the fraction. Neither
violation approaches the factor of 5.6 the margin provides.

**The rice half is not bounded and the paper should not imply that it is.**
There is no second rice product independent of the layer in use: CCD-Rice, the
only candidate, took its training samples from the same NESDC map. What exists
is 777 visually interpreted polygons reaching 62 of the 926 cells, which could
support a local error estimate without a design-based interval and cannot
support a domain-wide bound.

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

**Which end of the bracket is which is decidable from §5.1.** The impervious
model's residual half-sill range is
96.1<!--#range.operational_impervious_km--> km against a block
95.0<!--#range.block_ew_km--> km at its narrowest, so residual structure
persists across a block boundary and the block scheme's figures are the
optimistic end. Leave-one-province-out, the most extrapolative design available
on this lattice, is the pessimistic end. Neither weighting is correct either:
sounding count is not a bound on the error that matters, and leaving cells
unweighted treats a cell resting on one sounding as equal to a cell resting on
410<!--#composite.max_soundings-->.

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

The sweep crosses the threshold one weekly basin study adopted, 0.5, at
1.77<!--#dofs.cross_half--> Tg a⁻¹, IMI's stated minimum viability of 1 at
2.50<!--#dofs.cross_one--> and its marginal ceiling of 2 at
3.54<!--#dofs.cross_two-->. Those crossings are bisected on the sensitivity
expression rather than interpolated between swept points or taken as the
nearest swept point above the threshold; sensitivity is very nearly quadratic
in emission at these magnitudes, so both of those approximations overstate a
crossing. **The sweep is a lower bound** in any case, because it spreads the
assumed total uniformly over covered cells while real emissions concentrate,
and a cell's sensitivity rises faster than linearly in its own emission.

**At no point in the sweep does any cell reach an averaging-kernel sensitivity
above 0.5** — the count is 0<!--#dofs.cells_above_half--> at every prior
magnitude tested. The DOFS total accumulates from 926 weakly constrained cells
rather than from a few well constrained ones, and the margin is not narrow. At
5 Tg a⁻¹ the median cell's sensitivity is
0.0039<!--#dofs.cell_median_5tg--> and the best-observed cell reaches
0.0119<!--#dofs.cell_max_5tg-->; at 12 Tg a⁻¹, the top of the band, the median
is 0.0221<!--#dofs.cell_median_12tg--> and the best cell
0.0649<!--#dofs.cell_max_12tg-->. **The most favourable cell under the most
favourable assumed total is an order of magnitude below the threshold.** This
is the distribution behind the total, and the total alone conceals it: a DOFS
of 22 reads as capability until the per-cell figures are beside it.

### 6.2 The prior-free threshold

The sensitivity expression can be inverted without assuming any prior, because at
a given sensitivity it depends only on the observation counts. **A median cell in
this composite would need 0.0862<!--#dofs.prior_free_median--> Tg a⁻¹ — about
86<!--#dofs.prior_free_median_gg--> Gg a⁻¹ from a single 625 km² cell — for the observations to constrain it half
independently of the prior.** The best-observed cell, with 65 observation days,
would need 0.0492<!--#dofs.prior_free_best--> Tg a⁻¹, or
49<!--#dofs.prior_free_best_gg--> Gg a⁻¹.

For scale, a large municipal landfill emits on the order of 10 to 50 Gg a⁻¹.
**A median cell's threshold therefore sits above that whole range**: no single
landfill would half-constrain a typical cell. The best-observed cell is the
exception, and it is worth stating precisely because the figure draws it. Its
threshold falls *inside* the range rather than above it, so a landfill at the
top of the range would just reach half-constraint — in the one cell of 926 with
the most observation days. Everywhere else **individual large point sources in
this domain sit below a sensitivity of 0.5 and above zero**: visible to an
inversion as a partial constraint weighted toward the prior, not as an
independent measurement. This is
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

### 6.4 The expected signal against the noise

The preceding two limits concern what the observations can constrain. This one
concerns how large the signal being sought is, and it is computed from the same
closed form as §6.1 with the same wind.

Applying the inventory's own rate for the sectors urban land proxies —
28.82<!--#change.rate_urban--> Mg km⁻² a⁻¹, the through-origin slope of its
landfill, wastewater and gas emissions on impervious area — gives an expected
slope of 1.1995<!--#change.beta--> ppb per unit impervious fraction. Across the
observed impervious range, 5th to 95th percentile, the implied column contrast
is 0.410<!--#change.xsec_contrast--> ppb, which is
2.8<!--#change.xsec_share--> percent of the field's
14.86<!--#field.sd_operational--> ppb between-cell standard deviation, for an
implied R squared of 0.00007<!--#change.xsec_r2-->. The largest correlation this
permits is |r| = 0.0084<!--#change.r_max-->.

Two reference points make the number interpretable rather than merely small.
The median per-cell standard error of the composite is
1.98<!--#change.se_median--> ppb, so the whole land-cover contrast is a fifth of
the error on a single cell. And the same conversion applied to the inventory's
coal sector — 2035.1<!--#change.coal_total--> Gg a⁻¹ over
22<!--#change.coal_cells--> cells — gives
5.80<!--#change.coal_enhancement--> ppb per coal cell, which is
2.9<!--#change.coal_multiple--> times that error. **An emission of the coal
sector's per-cell size is well above the noise; the contrast land-cover extent
proxies is well below it.**

This is a bottom-up expectation from an inventory whose urban sectors are
allocated on population, and §6.5 and the discussion state what that does and
does not license.

### 6.5 Relation to §3

The land-cover result of §3 is the empirical counterpart of §6.1. A record whose
degrees of freedom accumulate from uniformly weak per-cell sensitivity is a
record in which per-cell predictors should fail, and §3 reports that they do
across two urban products, two rice products, two cross-validation schemes, two
weightings and three target fields. No causal inference is drawn here; the
correspondence is reported and its interpretation belongs in a discussion.

## 7. Reproducibility of the reported figures

76<!--#pipeline.recipes--> derived artefacts are registered with the command that
produces them and a verification tier.
41<!--#pipeline.recipes_committed--> regenerate from a fresh clone with no network
and no local data and are re-executed and compared byte for byte on every test
run; 24<!--#pipeline.recipes_local--> require local raw data;
10<!--#pipeline.recipes_network--> require a network fetch. Every numeric claim in
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
| §5.1–5.3 the fold geometry | **none** | planned, not built: fold map. **The most necessary of the three**, and more so than before: `buffered_decay` shades an interval and cannot say what it means about the folds |
| §4.2 sampling composition | **none** | planned, not built: sampling-artefact map |
| §5.2–5.3 the buffered decay curve and the bracketing | `buffered_decay` | exists; built for this section, and it carries §5.3 as well as §5.2 |
| §6.1–6.3 the sweep, the per-cell distribution and the prior-free threshold | `capability` | exists; built for this section, and its panel (b) is §6.3's information-content result |

**Both were gaps and both are now built.** The buffered decay curve was the
direct measurement of the impervious coefficient's spatial instability and
existed only as a ten-row table per field; the capability figure was the
contribution's own claim and existed only as a twenty-row table, since
densified to forty-one rows. Drawing them changed three things in this section.

**§5.3's bracketing is on the raw held-out scale, not the above-constant
scale.** The null's advantage over a constant is exactly zero at every radius
past 50 km, because past one cell the null *is* the constant, so the comparison
against the leave-one-province-out value can only be made on `held_out_r2`:
-0.084<!--#loo.null_150km_raw--> at 150 km and
-0.112<!--#loo.null_200km_raw--> at 200 km against
-0.091<!--#suite.null_operational_pu--> under leave-one-province-out.

**And the reason §5.3 gave for that being the corresponding radius does not
hold.** The claim was that a held-out province's interior sits roughly 150 to
200 km from the nearest training cell. That distance is not measured anywhere
in this repository. A scratch calculation against the fold assignment in
`baseline_predictions_2018.csv` — five folds, the four provinces and Outside —
puts the median cell about 56 km from its nearest training cell, with roughly
4 percent of cells in the 150-to-200 km range and about three quarters inside
100 km. So the bracketing interval is much wider than the typical fold
distance, and **leave-one-province-out is more extrapolative than its geometry
alone accounts for.** The bracketing itself stands: the province-out value does
fall between two adjacent points of the buffered curve, and that is all the
figure claims. Why it falls where it does is open, and the fold map is what
would settle it. No number from that scratch calculation is quoted in the
repository, because it has no registered script behind it.

**§6.1's threshold crossings were wrong.** They were the nearest swept point at
or above each threshold. Sensitivity is very nearly quadratic in emission at
these magnitudes, so that overstates a crossing and so does linear
interpolation. The sweep was densified from eleven points to twenty-three and
the crossings are now bisected on the sensitivity expression itself and written
to the artefact.

**Three figures the set holds that this section does not cite.**
`landcover_native`, `urban_change` and `landcover_regional` answer to the 2023
thesis's land-cover figures. They document the predictors' provenance and
disagreements, which is methods material and errata material rather than
results. `framework_pipeline` and `framework_reproduction` are documentation of
the pipeline and of the reproduction's structure and belong in neither section.
**That is five of thirteen figures with no place in a results section**, which
is not an argument for deleting them — three are the predictors' own record —
and the argument it did make, for building the two missing capability figures
before the three planned ones, has now been acted on. `figures/README.md`
records the five and what each serves instead.

### Numbers without a resolver

* The monthly sounding distribution, computed from a gitignored checkpoint.
* The coverage saturation curve's shape, described qualitatively because the
  figure holds it and no scalar summarises it.
* The albedo–impervious and albedo–NIR zero-order correlations (0.475, 0.746) and
  the solar-zenith correlation (0.695), which are in
  `albedo_confounder_2018.csv` and have no resolver.
* Six cells of the §3.3 table, being the weighted and leave-one-province-out
  figures for rice and for both fractions; the marked cells cover every reported
  claim and the rest are read from the artefact. **The table's column headers
  name all four scheme-weighting combinations**, which is the rule
  `notes/decisions.md` records: no land-cover R² appears here without its
  combination.
* The blended field's single-retrieval precision figures, 11.9 against 14.5 ppb,
  which come from the product's paper rather than from this work.
* All literature figures in §6.3, and the 10-to-50 Gg landfill scale in §6.2.

### Resolvers added for this draft

**Thirty for the first draft and twenty more on 16 September 2026**, when the
primary-field and cross-validation decisions settled. The first thirty were for
artefacts whose numbers the results section needs and which had none: the four fields' between-cell spreads; the albedo slopes for the
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

**The twenty added later** cover the blended field's albedo slope and Pearson
correlation and their ratio to the operational field's; the four-way
above-constant grid for impervious fraction, plus the null and rice-combined
values under leave-one-province-out; and the eight four-way spreads that settle
whether the spread belongs to the predictor or to the evaluation design.
