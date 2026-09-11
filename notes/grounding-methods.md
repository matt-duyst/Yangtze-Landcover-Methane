# Methods grounding

Draft material for a paper's methods section and for the limitations paragraphs
of its discussion. The companion to [`notes/grounding-yrd.md`](grounding-yrd.md),
which records what the region establishes; this records what the methods
literature establishes about how a study of this shape should be built,
evaluated and reported.

Read it as a list of things this project does not do, with a citation for each.
Several entries are **corrections to what this repository currently claims**
rather than additions, and those are the ones that matter; they are flagged
where they occur and collected in
[`notes/decisions.md`](decisions.md) as work this implies.

**Amended on 11 September 2026, and the amendment changes the frame rather than
adding to it.** As first written this record presented prediction-powered
inference as the methodological answer for this project. The field's answer is
Bayesian inversion with closed-form posterior error characterisation, in which
uncertainty quantification happens inside the inference; prediction-powered
inference is a component for one sub-problem. The first five sections below are
new and set that frame, including a purpose-built open tool that answers for
free the question this project gated as infeasible. Every component in the
later sections stands as written; what changed is what sits at the top. The
companion [`notes/grounding-urban.md`](grounding-urban.md) was written on the
same day.

Every figure here was checked against its source before it was written, and
where a figure could not be verified it is named as unverified and the number is
not repeated. The closing section lists every such case. **Fifteen of the
premises carried into this pass failed** — thirteen about the literature and two
about what this repository itself says — including three DOIs that resolve to
unrelated papers, so the closing section is long by construction and is the
honest part of the document. Numbers from this repository's own artefacts are marked for
[`scripts/verify_claims.py`](../scripts/verify_claims.py) where a resolver
exists; where one does not, the source file is named at the point of use.

## The field's method is Bayesian inversion, and this record first said otherwise

**This section was added on 11 September 2026 and it corrects the frame of
everything below it.** The record as first written presented prediction-powered
inference as the methodological answer for this project. It is not. It is a
component for one sub-problem — the accuracy assessment of a land-cover layer.
**The field's own method for turning satellite methane columns into statements
about emissions is Bayesian inference with closed-form posterior error
characterisation, in which uncertainty quantification happens inside the
inference rather than as a set of corrections applied afterwards.**

The in-region literature makes this unambiguous. An inversion of 2019 TROPOMI
observations over China optimises emissions "with a Gaussian mixture model (GMM)
at up to 0.25° × 0.3125° resolution", where "the optimization is done
analytically assuming log-normally distributed errors on prior emissions" and
"errors and information content on the optimized estimates are obtained directly
from the analytical solution and also through a 36-member inversion ensemble".
Its best estimate for total anthropogenic emissions in China is 65.0 (57.7–68.4)
Tg a⁻¹, of which rice paddies are 11.9 (10.7–12.7) Tg a⁻¹ (Chen et al., 2022,
*Atmospheric Chemistry and Physics* 22, 10809–10826,
doi:10.5194/acp-22-10809-2022). Note the resolution: **0.25° × 0.3125° is this
project's own lattice**, so the comparison is not between a coarse method and a
fine one.

A second regional system takes the ensemble route rather than the analytical
one. RegGCAS-CH4 is built on WRF-CMAQ with an ensemble Kalman filter,
assimilating TROPOMI XCH4 to produce daily emissions across China; posterior
national emissions are 45.1 ± 3.8 Tg a⁻¹, 36.5 percent below EDGAR, with the
largest reductions in coal and waste (Feng et al., 2025, *Atmospheric Chemistry
and Physics* 25, 15121, doi:10.5194/acp-25-15121-2025). A third works at urban
scale, inverting methane over the Chengdu–Chongqing economic circle at 10 km and
daily resolution using ground-based observations and a dynamic error Bayesian
framework (Xia et al., 2026, *Journal of Cleaner Production* 557, 148229,
doi:10.1016/j.jclepro.2026.148229). Its reported improvement in correlation and
RMSE from dynamic error weighting could not be verified and is not quoted here.

**What follows from this for the paper.** Every component recorded in the
sections below remains what it is: the accuracy-assessment frame for a
fractional layer, the attenuation correction, the effective degrees of freedom,
the preprocessing chain, the representativeness problem. They are not
superseded. What changes is what sits at the top. This project asked a
different question from an inversion — whether a static land-cover fraction
correlates with an annual column field — and answered it with a regression
whose uncertainty is characterised afterwards, correction by correction. That is
a legitimate design for that question, and it is **not** the design the field
would recognise as quantifying methane emissions. A paper should say which
question it asked, and should not present a correction-by-correction treatment
as the field's uncertainty framework.

## Degrees of freedom for signal, the field's information metric

The metric the field reports is not R squared. The averaging kernel matrix **A**
describes the sensitivity of the posterior estimate to the true state; its
diagonal elements measure the ability of the inversion to quantify each state
vector element independently of the prior, "fully if a_ii = 1, not at all if
a_ii = 0"; and the trace of **A** is the degrees of freedom for signal,
"representing the number of independent pieces of information on the state vector
obtained from the inversion" (Estrada et al., 2025, doi:10.5194/gmd-18-3311-2025,
following Rodgers, 2000, already in this register for the prior-alignment work).

Reported values span two orders of magnitude and are not comparable across
studies, because each is a count out of a different state vector. Recorded with
that caveat: **295 for a global inversion of 2024, ranging from 256 to 426
across individual years "reflecting changes in satellite coverage"** (He et al.,
2026, *Science Advances* 12, doi:10.1126/sciadv.adz9007); **568** independent
pieces of information in a global fuel-exploitation inversion (Shen et al.,
2023, *Nature Communications* 14, doi:10.1038/s41467-023-40671-6); **151** for a
global TROPOMI inversion against **232** for GOSAT, which is the non-wetland
partition of totals of 155 and 238, as the resolution section below records;
**167 out of 600 Gaussian state vector elements** for the China inversion above;
and **134** for China when TROPOMI is combined with 17 ground-based sites, which
is only 19 percent above the 113 that TROPOMI constrains alone (Zhong et al.,
2026, *Atmospheric Measurement Techniques* 19, 4759,
doi:10.5194/amt-19-4759-2026). **That last figure is the most sobering of the
five**: adding every available ground station in East Asia buys a fifth more
information.

The metric also has an operational threshold. Weekly Permian Basin inversions
adopted DOFS above 0.5 as "a practical minimum to estimate total basin methane
emissions with 2σ error ≤ 30 %", met by 124 of 127 weekly inversions, and noted
that "inversions with low DOFS are mainly constrained by the prior emission
estimate and may introduce smoothing error" (Varon et al., 2023, *Atmospheric
Chemistry and Physics* 23, 7503, doi:10.5194/acp-23-7503-2023).

**This project reports held-out R squared against a spatial null. The field
reports degrees of freedom for signal, uncertainty reduction and information
content.** A reviewer in this field would expect the latter, and the honest
position is that they measure different things: R squared measures how much of a
field a predictor reproduces, and DOFS measures how much the observations tell
you about emissions independently of what you assumed. A paper that reports only
the first should say so rather than letting the second be assumed.

## A purpose-built open tool exists for the question the thesis asked

The Integrated Methane Inversion is "an open-access cloud computing tool
designed for researchers and non-expert users to obtain total sector-resolved
methane emissions worldwide at up to 0.25° × 0.3125° (≈ 25 × 25 km²) resolution
by analytical inversion of TROPOMI satellite observations with closed-form error
characterization" (Estrada et al., 2025, *Geoscientific Model Development* 18,
3311–3331, doi:10.5194/gmd-18-3311-2025). It runs on Amazon Web Services, "where
both TROPOMI data and the atmospheric transport model (GEOS-Chem) reside, thus
avoiding the need for local computing resources and instead bringing the
computing to the data".

**Three of its thirteen version-2 developments are this project's own
situation.** It offers the blended TROPOMI+GOSAT dataset of Balasus et al.,
"removing most artifacts from the operational product", kept current on the AWS
cloud for the full TROPOMI record — the same field that is a committed band of
`methane_composite_2018.tif` here. It gives "improved error characterization
through use of super-observations that also better account for observational
error correlation", which is the correlated-error problem this record's
representativeness section identifies. And it achieves an order-of-magnitude
speed-up in Jacobian construction: "a 5-fold speed-up ... traded against a 60 %
increase in wall time", plus "an additional 2-fold speed-up" from precompiling
emissions, "for an overall 10-fold decrease in CPU cost".

**Access is free and the decisive step is cheap.** The documented routes are the
free IMI product on the AWS Marketplace, the source code from GitHub for running
on a local cluster, and the Integral Earth web interface. And the preview is
where this matters: "The IMI Preview has no significant costs, and we strongly
recommend using it to ensure that the proposed IMI configuration will lead to a
successful inversion." It reports the expected degrees of freedom for signal,
the dollar cost of the full run, and maps of mean concentrations, observation
density, prior emissions, estimated averaging kernel sensitivities and **SWIR
albedo** — the last being an artefact indicator, and this project has
166<!--#cov.albedo_negative--> cells with a negative annual mean SWIR albedo.

**State the consequence plainly.** Whether TROPOMI can constrain methane
emissions over this study area is answerable for free, by a preview run, in a
tool that already ingests the exact product this repository committed. That is
the question the flux-divergence gate recorded in `notes/decisions.md` could not
answer, and it has been answerable throughout.

The tool states its own cautions and they are this project's cautions too.
"Errors in the prior distribution of emissions propagate to bias in the
inversion results, and errors in the contributions from different sectors
propagate to errors in sectoral attribution." "Inversion results are sensitive
to the choice of prior error estimates and whether a normal or lognormal error
PDF is assumed." "Regional inversions require unbiased boundary conditions, as
biases in boundary conditions would propagate to the optimized emissions in the
inversion domain." And, most pointedly: **"Spatial error correlations in the
prior estimate are also certainly present but difficult to define and have been
ignored for now."** That is the same unresolved correlated-error problem this
project has met twice — once in the composite's sigma-over-root-n assumption and
once in the effective-degrees-of-freedom gap — and the field has not solved it
either.

## The prior inventory, which is where a land-cover layer has a legitimate role

An inversion needs a prior, and the prior is where a rice map or an impervious
map enters the field's own workflow. IMI 2.0's default global anthropogenic
prior is **EDGAR v8**, with fuel exploitation from the Global Fuel Exploitation
Inventory, monthly wetlands from the mean of the WetCHARTs ensemble, and daily
open fires from GFED4 (Estrada et al., 2025).

**EDGAR's rice representation is documented as wrong in three specific ways**,
and all three matter here. Verbatim: "EDGARv8 spreads emissions over all
agricultural land for many countries in South Asia (India, Bangladesh),
Southeast Asia (Thailand, Vietnam), and East Asia (China, Korea, Japan)". "The
seasonality in EDGARv8 is also uniform within individual countries. For example,
rice emissions in EDGARv8 peak in June everywhere over China". And its Chinese
total is "double the GRPI values for China and half for South Asia", because
"EDGARv8 used an outdated rice map for 2000, ignoring the changes in irrigation,
organic manure use, and rotational patterns, as well as the northward shift of
rice agriculture in China in the recent two decades" (Chen et al., 2025,
doi:10.1029/2024EF005479, already in the register). **The outdated map is for
2000, which is one of this project's own three years.** And the consequence for
attribution is stated directly: errors in the spatial distribution "compromise
the ability to separate rice emissions from other sectors such as coal in
southern China" — this study area.

The gain from fixing it has been measured twice, both times in or near this
region. Substituting an updated rice distribution over Heilongjiang gave 0.85 Tg
against EDGAR's 0.43, with large upward corrections in June to August and
model-observation mean biases reduced by 40 percent (Liang et al., 2024,
doi:10.1021/acs.est.4c09822, already in the register). And RegGCAS-CH4 found
that "emissions in Zhejiang, Fujian, and Jiangxi Provinces increased, mainly
attributed to emissions from rice paddies", naming EDGAR's reliance on "outdated
rice paddy maps" that "incorrectly overspread rice emissions across non-rice
agricultural grids" as the cause, and reporting that "rice paddy CH4 emissions
serve as the dominant emission source in East China" (Feng et al., 2025).
**Zhejiang is one of this project's four provinces.**

So the legitimate role for a rice layer in this field is not as a regression
predictor against a column field. It is as a spatial prior for an inversion,
where a better map demonstrably moves the answer and reduces model-observation
bias. That is a use this project's layers are fit for and have not been put to.

## From a rice map to an emissions estimate, which is a solved chain

The route exists and is published end to end. The Global Rice Paddy Inventory
uses Landsat at 30 m to map the global monthly distribution of rice paddy
fractional areas on a 0.1° grid "by optimizing an algorithm for flooded
vegetation and combining it with a 30-m global cropland database and
rice-specific data", then combines that map "with an extensive global dataset of
emission factors (EFs) per unit of rice paddy area". The result is 39.3 ± 4.7 Tg
a⁻¹ globally for 2022, with China at 8.2 ± 1.0 Tg a⁻¹, agreeing with the Global
Carbon Project mean and the UNFCCC report and a factor of two below EDGARv8.
Validation against an independent US rice database and FLUXNET-CH4 eddy flux
measurements gives "errors on rice area fraction of 31 % on the 0.1° × 0.1° grid
and 10 % regionally" (Chen et al., 2025).

Two properties of it bear on this project's years. The inventory is for 2022,
but the authors state the methods "can be readily applied to other years", and
that "interannual variability of emissions in Asia is found to be less than
8 %", while "decadal trends can be more important". This project's years are
2000, 2010 and 2018 — a span over which the decadal caveat, not the interannual
one, is the binding consideration.

The emission factors are themselves a published product. A global compilation of
**2,301 rice paddy field measurements** was used to fit a generalised additive
model estimating mean growing-season emission factors as a function of soil
texture, pre-season water status, growing-season water regime, planting method,
rice cultivar, organic amendment and climate zone; its global mean emission
factor is 1.97 kg ha⁻¹ d⁻¹ against the IPCC 2006 Tier 1 recommendation of 1.30.
Its conclusions are that continuously flooded paddies emit most and rainfed dry
season least, that soil texture, water and organic amendment strongly affect
emissions, and that a country-specific pre-season water baseline is vital
(Nikolaisen et al., 2023, *Journal of Cleaner Production* 409, 137245,
doi:10.1016/j.jclepro.2023.137245).

**Every variable in that model is a mechanism [`notes/grounding-yrd.md`](grounding-yrd.md)
already identifies**, and the model is the thing that turns extent into
emission. The region record establishes that water regime spans a factor of 13.7
at constant area; this is the published function that consumes it.

GRPI's uncertainty treatment is also the propagation framework this problem
needs, and it is simple enough to copy. Area-fraction error is handled
separately from emission-factor error. The first is "one standard deviation of
residuals between our product and the" reference; the second is "one standard
deviation of residuals between their generalized additive model and individual"
observations. Both are converted to relative uncertainties and assumed to apply
uniformly within a country. **That last assumption is the weak point for this
study area**, because the region record establishes that deltaic rice systems
have hydrological conditions specific enough that default emission factors may
be erroneous, and a country-uniform relative uncertainty cannot represent that.

## The accuracy assessment frame, and why Olofsson is the wrong standard here

Olofsson et al. (2014, *Remote Sensing of Environment* 148, 42–57,
doi:10.1016/j.rse.2014.02.015) is the field's reference for good practice in
estimating area and assessing accuracy of land change, and it was absent from
this repository's register until 10 September 2026. Its five recommendations
are a probability sampling design; a response design using reference data more
accurate than the map; consistent analysis; an error matrix expressed as
proportions of area, with overall, user's and producer's accuracy; and
error-adjusted area estimates with confidence intervals.

**It is a framework for categorical maps of discrete classes, and this project's
layers are not that.** A full-text search of the paper returns zero occurrences
of "fraction", "sub-pixel" or "subpixel", and its "proportion of area" always
means the share of a region that a discrete class occupies, never a per-pixel
or per-cell value. The layers here feed a fractional cover per 0.25-degree
cell. **Recommendations 4 and 5 are therefore the wrong standard to hold this
work to, and citing them as unmet would be a category error.** Recommendations
1 to 3 apply in full and are what this project lacks: it has no probability
sample, no reference data more accurate than the map, and so no analysis to be
consistent about.

The correct frame for a continuous field is stated explicitly, and by a paper
that names Olofsson as the contrast. The NLCD percent-impervious assessment
writes that its assessment "is of a continuous variable, %IC. As such, the
accuracy assessment employs methods of analysis specifically designed for
application to continuous field data (Riemann et al., 2010) such as describing
agreement using metrics such as mean deviation and mean absolute deviation.
This is in contrast to techniques appropriate for nominal class data which
focus on creating an error matrix and estimating class-specific omission and
commission error rates (e.g., Olofsson et al., 2014)" (Wickham et al., 2020,
*International Journal of Applied Earth Observation and Geoinformation* 84,
101955, doi:10.1016/j.jag.2019.101955). The protocol it points to is Riemann et
al. (2010, *Remote Sensing of Environment* 114, 2337–2352,
doi:10.1016/j.rse.2010.05.010), an assessment protocol for continuous
geospatial datasets evaluated against forest inventory plots, and that is the
primary methodological citation for what this project would have to do.

Two further features of that assessment matter here. It used **complete-coverage
reference data**, writing that "we do not estimate agreement from a sample, but
rather calculate agreement directly from the full coverage data" — which is the
same situation as a complete lattice, and removes the sampling-design question
that dominates the categorical literature. And it measured the aggregation
effect directly, across seven lattice cell sizes from 1 to 200 hectares: **mean
absolute deviation was 5.68 percent at 1 hectare and 3.09 percent at 200
hectares**, and "MAD decreased and R² increased as the lattice cell size
increased. The largest changes in R² and MAD occurred as the lattice cell size
increased from 1 ha to 5 ha with progressively smaller changes as cell size
increased further" (Wickham et al., 2020). This project's cells are about 62,500
hectares, two and a half orders of magnitude beyond where that curve had
flattened, so aggregation works in its favour and the error in a per-cell
fraction is smaller than the error in a pixel.

Two benchmarks are worth carrying for scale. An independent assessment of the
NLCD 2011 tree canopy cover map on 16,607 forest inventory observations gave a
weighted root mean square deviation of 12.8 percent and a weighted mean absolute
error of 8.0 percent at conterminous-US scale, as documented by the
Multi-Resolution Land Characteristics Consortium for the v2021.4 product; and
NLCD 2019's Level II land cover overall accuracy was 77.5 percent with a
standard error of 1 percent when agreement required a match to the primary
reference label, rising to 87.1 percent when a match to either the primary or an
alternate label was allowed (Wickham et al., 2023, *GIScience & Remote Sensing*
60, doi:10.1080/15481603.2023.2181143). A fractional layer with a mean absolute
error near 8 percent is a good one, and a categorical layer at 77.5 percent
overall accuracy is a normal one. Neither is the near-perfect input a reader
unfamiliar with the field might assume.

## Prediction-powered inference, one component and not the route

**Read this section as being about the accuracy assessment of a land-cover
layer, which is the sub-problem it solves.** An earlier version of this record
presented it as the methodological answer for the project as a whole; the
section above corrects that.

Prediction-powered inference computes an estimate from a large set of model
predictions and then uses a small labelled subset to measure and correct the
predictions' bias, so that the resulting confidence interval is valid whatever
the model's quality and narrower than labels alone whenever the model carries
signal (Angelopoulos, Bates, Fannjiang, Jordan and Zrnic, 2023, *Science* 382,
669–674, doi:10.1126/science.adi6000). A `ppi-py` package implements it.

The remote sensing application is Lu, Kluger, Bates and Wang (2025, *Remote
Sensing of Environment* 330, 114949, doi:10.1016/j.rse.2025.114949). Its own
novelty claim is narrower than a summary might suggest: it is "the first work to
estimate remote sensing regression coefficients without assumptions on the
structure of map product errors". Four of its results bear on this project.
Area estimation is handled as a special case of mean estimation. **PPI for area
estimation produces confidence intervals similar to those of the post-stratified
estimator** that the categorical accuracy literature uses, and the paper proves
they converge as the number of map points grows, so PPI is not a competitor to
the Olofsson machinery for area but a generalisation of it that also handles
regression coefficients. Stratified PPI weights each ground-truth value and its
paired prediction by `w_i = A_k · n / n_k`, where `k` is the stratum a point
falls in, `A_k` its area proportion and `n_k` the number of ground-truth units
in it. And effective sample size is defined as

    n_effective = n · (w / w')²

where `w` is the interval width from ground truth alone and `w'` the width from
the new method; in their experiments "the PPI effective sample sizes range from
1.2× to 17.4× the ground truth calibration set size", the largest being the
income coefficient in a poverty-mapping example.

**The one condition is the argument for using the CCD-Rice polygons, and it turns
on a distinction worth stating carefully.** The paper is explicit: "This
calibration set of n points is a simple or stratified random sample over the
region of interest, and it must be separate from the training dataset used to
train the machine learning model", and elsewhere that "the criterion for this
holdout set is that the model, including during hyperparameter tuning, was not
trained on it". The CCD-Rice validation polygons recorded in
[`notes/dataset-leads.md`](dataset-leads.md) validated CCD-Rice, and
`notes/grounding-yrd.md` records that CCD-Rice re-determined its thresholds
against filtered rice areas, so those polygons may have entered CCD-Rice's own
calibration. **They are therefore contaminated for validating CCD-Rice and clean
for validating the NESDC rice layer and the GISA impervious layer that this
project actually uses**, neither of which has ever seen them. That is the whole
case, and it depends on not confusing the product whose samples they are with
the products they would be used on.

The assumption problem is real and its treatment is thin. Canonical PPI theory
"starts from i.i.d. labelling, whereas spatial labels arrive through survey
designs or covariate-driven mechanisms, and map errors may be spatially
correlated" (Shirota, 2026, *Design-Based Prediction-Powered Inference for
Spatial Data*, arXiv:2608.10356, 11 August 2026). That work recasts PPI in a
design-based frame, derives exact design variances under simple and stratified
sampling, and develops sandwich inference for estimated propensities when
selection depends on the map; on Estonian land-use survey data, design-matched
tuning reduced standard errors by about 10 percent. Extensions to nonuniform
sampling and imputed covariates exist (Kluger, Lu and others, *Prediction-Powered
Inference with Imputed Covariates and Nonuniform Sampling*, arXiv:2501.18577),
and Lu et al. rely on a percentile-bootstrap construction because it "can be
modified to apply to weighted, stratified, and clustered samples". **But the
spatial extension is a single-author preprint four weeks old at the time of
writing, and a preprint is thin ground for a central method.** If this route is
taken, the honest framing is canonical PPI with an acknowledged i.i.d.-labelling
assumption, not a design-based treatment this project is in a position to
implement.

## Errors-in-variables, the one mechanism that could manufacture the null

Measurement error in a predictor attenuates its regression coefficient toward
zero, and the ratio of the naive coefficient to the corrected one approximates
the reliability ratio — the share of variance in the measured predictor that
comes from the true signal. Error in one predictor also biases the coefficients
of other predictors correlated with it, which matters here because impervious
fraction and rice fraction are not independent.

Two corrections need no validation data. **Regression calibration** replaces the
error-prone predictor with its conditional expectation given the observed value,
which for linear regression is exact. **Simulation-extrapolation** adds
increasing artificial error, models how the coefficient degrades and
extrapolates back to zero error. A simulation study compared them under the
condition that applies here — "it was assumed that no validation data were
available about the error-free measures, while measurement error variance was
correctly estimated" — over reliability from 0.2 to 0.9, sample sizes from 125
to 1,000, 2 to 10 replicates and R² from 0.03 to 0.75, and found that
"regression calibration was unbiased while simulation-extrapolation was biased:
median bias was 1.4% (interquartile range (IQR): 0.8;2%), and −12.8% (IQR:
−13.2;−11.0%), respectively". Confidence interval coverage was at the nominal
95 percent for regression calibration and a median 92 percent for
simulation-extrapolation, while simulation-extrapolation was marginally more
efficient. The recommendation is unambiguous: "In the absence of validation
data, the use of regression calibration is recommended for sensitivity analysis
for measurement error" (Nab and Groenwold, 2021, arXiv:2106.04285).

Two variants are on point. A remote sensing method combines the two corrections
this project needs at once: **SIMEX-WLS**, "an errors-in-variables modeling
approach that corrects coefficient attenuation by incorporating both measurement
errors and non-constant residual variances" (Xu, Li, McRoberts and Næsset, 2026,
*Big Earth Data*, doi:10.1080/20964471.2026.2660552). Non-constant residual
variance is not an optional extra here: a cell mean rests on between
1<!--#composite.min_soundings--> and 410<!--#composite.max_soundings-->
soundings, so its variance differs by more than two orders of magnitude across
the lattice, and the repository already weights by sounding count for exactly
that reason. And a spatial variant addresses the case where the mismeasured
covariate is spatially lagged, comparing Monte Carlo expectation-maximisation,
instrumental variables and Bayesian analysis and finding Bayesian analysis best
(Masjkur, Saefuddin, Mangku, Folmer, Van der Vlist and Grzegorczyk, 2025,
*Spatial Statistics* 68, 100909, doi:10.1016/j.spasta.2025.100909). **That is
directly on point because this project's spatial null is a spatially lagged
covariate** — each cell predicted from the mean of its eight neighbours — so the
benchmark the land-cover models are measured against is itself a variable
measured with error.

The measurement error variance each correction needs is estimable per layer
without new fieldwork. For rice, from the CCD-Rice polygons. For impervious
surface, from the GAIA–GISA disagreement, which gives a lower bound rather than
an estimate, because two products agreeing does not mean either is right. For
methane, from the per-sounding precision discussed below.

**De-attenuation is the most consequential remaining test in this study.** Every
other confound identified in either grounding document either leaves the
association alone or explains its genuine absence. This one shrinks a real
association toward zero, and it is the only mechanism that could manufacture
this project's headline result out of nothing. The repository has answered it by
building second predictors with different errors and finding the null survives,
which is good evidence and not the same thing as measuring the attenuation.

## The alternatives to prediction-powered inference, which were not examined

The first version of this record over-indexed on prediction-powered inference
because the alternatives had not been looked at. Three families exist and they
do different jobs.

**Bayesian hierarchical models** handle measurement error and spatial
misalignment in one structure. They "offer a coherent probabilistic framework
for evaluating associations between environmental exposures and health effects,
which take into account exposure measurement errors introduced by uncertainty in
the estimated exposure as well as spatial misalignment between the exposure and
health outcome data", and — the property that matters against the corrections
recorded below — they "do not require decomposition of the measurement error
into the classical- and Berkson-type errors", which both regression calibration
and simulation-extrapolation do (Lee et al., 2024, *Biostatistics* 26,
kxae038, doi:10.1093/biostatistics/kxae038). That paper's own contribution is a
scalable two-stage version for when fully joint estimation is infeasible, which
is the practical case here. **Borrowed from environmental epidemiology**, where
the structure of the problem — an exposure field estimated with error,
misaligned with an outcome measured on a different support — is formally the same
as a land-cover fraction against a column field.

**Sensitivity analysis** asks how strong the error would have to be rather than
correcting for it. VanderWeele and Li (2019, *American Journal of Epidemiology*
188, 1823–1829, doi:10.1093/aje/kwz133) give formulas under which "the true
effect ... must be at least as large as the observed association between the
mis-measured exposure measurement and the outcome divided by the maximum
strength of differential measurement error", so that a reader can judge whether
error could explain away an estimate without the analyst committing to its
magnitude in advance. **But it is for *differential* error and this project's
error is not differential.** A land-cover product's classification error does not
depend on the methane column, so the error here is nondifferential, and
nondifferential error biases toward the null. That asymmetry is the important
one: **a null cannot be manufactured from a real positive by any other
direction, but a real positive can be attenuated into a null by this
mechanism.** It is why the errors-in-variables section below is the most
consequential remaining test, and it is also why the differential-error
sensitivity machinery does not apply and is recorded here rather than adopted.

For robustness to omitted variables rather than to measurement error, the
robustness value of Cinelli and Hazlett (2020, *Journal of the Royal Statistical
Society Series B* 82, 39–67, doi:10.1111/rssb.12348) reports how strongly an
unobserved confounder would have to be associated with both treatment and
outcome to overturn a conclusion. **Borrowed from econometrics.**

**Specification curve analysis** is the reporting frame, not a correction
(Simonsohn, Simmons and Nelson, 2020, *Nature Human Behaviour* 4, 1208–1214,
doi:10.1038/s41562-020-0912-z). **Borrowed from psychology's replication
literature.** It visualises how a result varies across every defensible
analytical specification rather than across the one the analyst chose. This
project has three methane fields, four predictor pairs, two cross-validation
schemes and two weightings. **That is forty-eight specifications, which is a
specification curve and not a table**, and the repository currently reports it
as a table with the exceptions described in prose.

**So the methods answer is not one method.** Prediction-powered inference for
the accuracy assessment of a layer against reference polygons; a Bayesian
hierarchical model or regression calibration for the association itself;
sensitivity analysis for robustness where a correction is not available; and
specification curve analysis as the frame in which all of it is reported. Each
addresses a different one of this project's four open problems, and presenting
any one of them as the answer — as this record first did with the first of them
— misdescribes the shape of what is missing.

## Reliability estimation, and three bad practices

Where a layer's error must be characterised rather than assumed, disagreement
between two products decomposes usefully. Pontius and Millones (2011,
*International Journal of Remote Sensing* 32, 4407–4429,
doi:10.1080/01431161.2011.552923) separate **quantity disagreement**, the
mismatch in the proportions each class occupies, from **allocation
disagreement**, the mismatch in where those classes are put. That is the right
tool for the GAIA–GISA comparison this repository already reports as a single
percentage difference in provincial area, which is quantity disagreement alone
and says nothing about whether the two products put impervious surface in the
same places. **Allocation disagreement is the component that bears on the
reliability ratio**, because a layer can have the right total and the wrong
locations, and only the second attenuates a coefficient.

That paper's title is "Death to Kappa", and its two recommendations are to stop
using kappa and to use disagreement components instead. It is not alone.
Stehman and Foody (2019, *Remote Sensing of Environment* 231, 111199,
doi:10.1016/j.rse.2019.05.018) survey half a century of accuracy assessment and
name "three examples of bad practice that are widespread": "the universal
application of 85% target accuracy, normalization of the error matrix, and
**correction for chance agreement**". The third is kappa.

**This repository's errata faulted the 2023 thesis for reporting no kappa, which
means it cited as a deficiency a statistic two independent authorities in the
field call bad practice.** That is corrected; `ERRATA.md` 6.5 now asks for what
the field asks for.

The same paper gives six good-practice criteria — "map relevant; statistically
rigorous; quality assured; reliable; transparent; and reproducible" — and states
the response-design requirement in the form that governs everything in
`notes/dataset-leads.md`: "it is essential that the reference dataset be more
accurate than the map to be evaluated."

Its quality-assurance criterion has a consequence for this project that is worth
stating plainly. Reference labelling should be checked by having two or more
interpreters independently label a randomly chosen subset, so that consistency
between them speaks to the reliability of the labels. **This project has one
interpreter.** Any visual-interpretation reference set built here would
therefore carry labelling error that cannot be quantified, and a reviewer would
be right to say so. That is a further argument for the CCD-Rice polygons, whose
own paper records that its samples were checked by three experts, over anything
this project could interpret for itself.

## Spatial cross-validation, an active controversy with one side implemented

Roberts et al. (2017) and Valavi et al. (2019), both already in the register,
establish that random cross-validation on spatially clustered data overestimates
accuracy, and that the blocking distance should follow the autocorrelation range
of the model's residuals with blocks only as large as required. That is the side
of the argument this project implemented.

The other side is Wadoux, Heuvelink, de Bruin and Brus (2021, *Ecological
Modelling* 457, 109692, doi:10.1016/j.ecolmodel.2021.109692), whose title is
"Spatial cross-validation is not the right way to evaluate map accuracy". Its
findings, verbatim: "The two spatial cross-validation methods are too
pessimistic, with B-LOO CV severely overestimating the RMSE in all cases"; "The
pessimistic results of the spatial cross-validation methods are likely caused by
over-representation of environmental conditions distinct from the environmental
conditions at the calibration points, and under-representation of environmental
conditions similar to those at the calibration locations"; and in conclusion,
"spatial cross-validation strategies resulted in a grossly pessimistic map
accuracy assessment, and gave no improvement over standard cross-validation.
Both standard and spatial cross-validation methods may provide biased estimates
of map accuracy."

The synthesis is prediction-oriented validation. Nearest-neighbour distance
matching leave-one-out cross-validation was proposed by Milà et al. (2022) and
extended to k-fold by Linnenbrink, Milà, Ludwig and Meyer (2024, *Geoscientific
Model Development* 17, 5897–5912, doi:10.5194/gmd-17-5897-2024): the method
matches the distribution of nearest-neighbour distances between test and
training locations to the distribution between prediction and training
locations, so that it "creates predictive conditions during CV that are
comparable to what is required when predicting a defined area". The CAST package
in R implements it. The same paper describes the state of the field as one where
"the appropriateness of such approaches is currently the subject of
controversy", which is the honest way to introduce it in a paper.

**How this project stands, and it is not straightforwardly on either side.** The
controversy concerns estimating the accuracy of a *map* interpolated from
scattered calibration points. This project has a complete lattice with no
interpolation and no clustered calibration sample, and Wadoux et al. name the
clustering explicitly as the condition under which standard cross-validation
goes wrong — "Standard K-fold CV was too optimistic in case of clustered
sampling because each validation point had nearby calibration points, while most
points in the map did not." Here every cell has nearby cells in the data, so
that mechanism is weak. But leave-one-province-out is the most extrapolative
design available, and extrapolation is exactly where Wadoux's pessimism
mechanism bites hardest. **That may be the explanation for the gap this
repository reports between its two schemes**: the spatial null reaches held-out
R squared 0.332<!--#baseline.null_r2--> under spatial blocks and falls to −0.091
under leave-one-province-out, a figure `figures/README_fragments.md` already
attributes to a held-out province's interior having no training neighbour. The
implication for the paper is that **the two schemes may bracket the truth rather
than one of them being correct**, and reporting both, as the repository does, is
better than choosing.

Two gaps follow. **Neither scheme buffers**, while the literature's variants do,
and the buffer radius is the parameter the whole argument turns on. And the
block size has never been justified from the data: the defensible choice is the
autocorrelation range of the model's *residuals*, which has never been measured
here — only Moran's I of the residual field, which is a different quantity. The
diagnostic the literature recommends is a buffered leave-one-out curve across a
range of increasing radii, so that the decay of predictive power with distance
from training data is visible as a shape rather than asserted at one arbitrary
buffer.

Two warnings apply to this project's own diagnostics and they point in opposite
directions. A forest biomass study found that "a standard nonspatial validation
method suggests that the model predicts more than half of the forest biomass
variation, while spatial validation methods accounting for SAC reveal quasi-null
predictive power", and — the part that matters for diagnostics — that "even
after a random 10-fold CV, the residual structure was completely absorbed in
[the model]'s predictions", so residual diagnostics would not have detected the
problem (Ploton et al., 2020, *Nature Communications* 11,
doi:10.1038/s41467-020-18321-y). Conversely, "the absence of spatial
autocorrelation (SAC) in the model residuals should not be taken as a sign of a
good fit, since it may result from overfitting the spatial trend" (Hawinkel, De
Meyer and Maere, 2022, *Frontiers in Plant Science* 13,
doi:10.3389/fpls.2022.858711). Taken together, **residual spatial structure is a
weak diagnostic in both directions**: its absence can mean overfitting and its
presence can be absorbed away by a flexible model. This project's residual
Moran's I of 0.646<!--#residual.residual_moran--> against
0.709<!--#residual.observed_moran--> for the observed field should be read as
describing what the fit did not remove, not as evidence about fit quality.

## Effective degrees of freedom, which every correlation here needs

Correlations between two autocorrelated spatial fields have fewer independent
observations than they have data points, and the standard test does not know it.
Clifford and Richardson (1989) and Dutilleul, Clifford, Richardson and Hémon
(1993, *Biometrics* 49, 305, doi:10.2307/2532625) introduced a modified t
statistic correcting both the sample covariance and the degrees of freedom,
introducing an effective sample size that is the number of equivalent
independent observations given the spatial covariance structure of each process;
the 1989 procedure rests on a variance approximation and the 1993 one is exact.
Stated generally: "if the time series are themselves dependent (i.e. exhibit
temporal autocorrelation), the effective degrees of freedom (EDF) are reduced,
the standard error of the sample correlation coefficient is biased, and Fisher's
transformation fails to stabilise the variance" (Afyouni, Smith and Nichols,
2019, *NeuroImage* 199, doi:10.1016/j.neuroimage.2019.05.011), which is the same
statement in a temporal setting and the clearest modern version of it.

**The consequence for this project is unambiguous and unaddressed.** It reports
Pearson and partial correlations over 926<!--#composite.covered_cells--> cells
with n treated as 926, and both the methane field and the impervious field are
strongly autocorrelated — Moran's I of the observed methane field is
0.709<!--#residual.observed_moran-->. The p-values on every one of those
correlations are therefore anti-conservative, and the effect is largest exactly
where the correlation is weakest, because that is where a p-value is doing the
work. The one statistic in the repository that handles its own dependence
properly is the Moran's I permutation test. Nothing else does. An effective
sample size on the reported correlations is cheap, needs no new data, and would
change several stated p-values.

## The methane field's own uncertainty, never quantified here

The mission's own guidance is that "for overall uncertainty estimates, it is
suggested that users apply an error multiplication factor of 2 to the single
sounding precision values", a factor that reflects the scatter of single-sounding
errors seen in TCCON validation. Validation against TCCON gives a
single-retrieval precision of 14.5 ppb for the operational TROPOMI product and
11.9 ppb for the blended TROPOMI+GOSAT product (Balasus et al., 2023,
*Atmospheric Measurement Techniques* 16, 3787–3807,
doi:10.5194/amt-16-3787-2023). Applying the recommended factor gives an
effective per-sounding uncertainty near 29 and 24 ppb respectively. **The
between-cell standard deviation of the composite is 14.9 ppb**, which
`data/processed/README.md` records. So a single sounding is roughly twice as
uncertain as the entire spatial signal the analysis is trying to explain, and
the composite's ability to say anything at all rests on averaging.

The variable to average is available and unused. `methane_mixing_ratio_precision`
is present in the Level 2 granules and carries the random error from the spectral
fit; this pipeline neither grids it nor filters on it. A published precedent for
filtering on it exists at a threshold of **under 10 ppb** (Schuit et al., 2023,
*Atmospheric Chemistry and Physics* 23, 9071, doi:10.5194/acp-23-9071-2023).

**The most consequential result of this pass concerns whether averaging is
enough, and the answer is that density is the wrong thing to measure.**
Schutgens et al. (2017, *Atmospheric Chemistry and Physics* 17, 9761–9780,
doi:10.5194/acp-17-9761-2017) estimate representation error across timescales and
length scales from semi-annual down to sub-daily and 300 to 50 km — a range that
brackets this project's 0.25-degree, annual regime — and "show that even after
substantial averaging of data significant representation errors may remain,
larger than typical measurement errors". Then, directly: "We show that
observational coverage (a measure of how dense the spatio-temporal sampling of
the observations is) **is not an effective metric to limit representation
errors**." They assess strategies for constructing gridded Level 3 data and find
"temporal averaging of spatially aggregated observations (super-observations) is
found to be the best, although it still allows for significant representation
errors", and warn that "emission sources and orography can lead to
representation errors that are very hard to reduce, even with substantial
temporal averaging".

**This project uses coverage as the composite's quality metric throughout** — in
a whole figure, in a raster band, and in the inverse-variance weighting of every
baseline — and the literature says density does not bound the error that
matters. The strategy this project follows is the one Schutgens et al.
recommend, and it still admits significant representation error. Its own study
area has both of the features they name as hardest: concentrated emission
sources, and the mountainous interior of southern Zhejiang.

Two further results say what to do instead. The uncorrelated-plus-correlated
decomposition of a superobservation is explicit: "the observational uncertainty
is a combination of an uncorrelated part and a correlated part. The uncorrelated
part tends towards zero as the number of observations increases because the
square of the standardized weights decreases. On the other hand, the correlated
part does not change much when adding more observations" (Rijsdijk, Eskes,
Dingemans and others, 2025, *Geoscientific Model Development* 18, 483,
doi:10.5194/gmd-18-483-2025). **This project's composite assumes the whole error
cancels as sigma over root n**, which is the uncorrelated part only. How large
the correlated part is for methane is unestablished and should be said rather
than assumed small; for the analogous NO2 product it is substantial, with "the
temporal error correlation in both the stratospheric uncertainty and the air
mass factor uncertainty" found "to be 30 %" (Glissenaar, Boersma and others,
2025, *Earth System Science Data* 17, 4627,
doi:10.5194/essd-17-4627-2025).

The same Level 3 work supplies an implementable alternative to counting
soundings. Its spatial representativeness uncertainty "accounts for incomplete
sampling of the cell by the observations available"; it is zero when the cell is
fully covered, and when only a small fraction is covered it "is equal to the
standard deviation of the tropospheric vertical columns within the cell: large
for areas with strong spatial variability ... and smaller for regions with
similar values". Temporal averages are then weighted so that "superobservations
with a low representativeness uncertainty obtain more weight in the temporal
average than superobservations with a high representativeness uncertainty". That
is a weighting by how representative a cell-day is, not by how many soundings it
has, and the difference is the whole point: two cells with the same count can
have very different within-cell spread.

## The preprocessing chain, gestured at and never specified

Two independently published sequences agree on the order, which is worth knowing
because it is not obvious that bias correction precedes filtering.

The super-emitter detection study uses "albedo–bias-corrected data with a quality
assurance value (QA) ≥ 0.4, methane precision < 10 ppb, SWIR aerosol optical
depth < 0.13, near-infrared (NIR) aerosol optical depth < 0.30, SWIR surface
albedo > 0.02, mixed albedo (2.4 · NIR surface albedo − 1.13 · SWIR surface
albedo) < 0.95, and SWIR cloud fraction < 0.02", after which "the methane data
are destriped, following the approach introduced by Borsdorff et al. (2018)", and
the whole preprocessing "consists of filtering, destriping the XCH4 channel, and
splitting up the data into 32×32 scenes" (Schuit et al., 2023). It also records
the trade this project made without naming it: "the loosened filtering compared
to the recommended QA = 1 filter provides more coverage but also retains more
biased retrievals, **especially at the borders of clouds or along coasts**" —
which is where this repository's own coverage gap and sparse-coastline problem
live. The European three-product comparison follows the same order, reprocessed
albedo-bias-corrected data at a quality flag above 0.5 and then destriping
(Sicsik-Paré and others, 2026, *Atmospheric Chemistry and Physics* 26, 10423,
doi:10.5194/acp-26-10423-2026).

A third sequence gives filters with their measured effect, which is rarer and
more useful. The 2019 US inversion removes scenes with a blended albedo greater
than 0.75 in non-summer seasons, and scenes with SWIR albedo below 0.05
following de Gouw et al., these two together accounting for most of the
remaining unphysical TROPOMI observations with methane below 1700 ppb. The
filters "preserve 69% of the high-quality retrievals" and "seasonal regional
biases decrease by between 7% and 21%" (Nesser et al., 2024, *Atmospheric
Chemistry and Physics* 24, 5069, doi:10.5194/acp-24-5069-2024).

**What this project does is fetch, filter at `qa_value >= 0.75`, grid, and
average annually. That is two steps of seven.** And the albedo floor is not a
cosmetic omission: surface albedo is negative in
166<!--#cov.albedo_negative--> of the 926<!--#composite.covered_cells--> covered
cells, which is not merely below the 0.05 floor the US inversion applies but
below zero, and a reflectance cannot be negative. Those cells are retained.

**Destriping is not available for this project's year and will not become
available.** "A destriping procedure (Borsdorff et al., 2024) is applied to new
XCH4 data from 2024/09/07 (v2.07), but older orbits have not been reprocessed"
(Sicsik-Paré and others, 2026). This project's 2018 granules are processor
version 020400. So the official correction cannot be inherited; only a
self-implemented one is available, which `notes/decisions.md` already records as
the cheapest of its four missing preprocessing steps and which remains true.

The blended product addresses surface albedo, aerosol and across-track
variability together through its machine-learning correction, which covers
three of the missing steps at once and is the reason it was worth adding.

## Prior alignment, which any TCCON comparison requires

A satellite retrieval and a TCCON retrieval do not measure the same functional
of the atmosphere: they use different a priori profiles and have different
vertical sensitivities, so a difference between them mixes a real bias with an
artefact of the two retrievals' construction. The correction adjusts both to a
common prior using the satellite averaging kernel and the two prior profiles,
following Rodgers and Connor (2003). Balasus et al. (2023) did this, "adjusting
all retrievals to common vertical profiles and averaging kernel sensitivities".

The second correction step — adjusting the TCCON result using the retrieved TCCON
profile scaling factors together with the satellite averaging kernels — has
published precedent for being skipped: "this second correction step is omitted
in the present analysis for the sake of simplicity, as it became apparent in the
past that this adjustment is negligible in the validation of TROPOMI/WFMD"
(Schneising et al., 2026, already in the register). So one correction is required
and the second is optional with a citation.

**Balasus et al. use two different collocation rules and this settles which
applies where**, because the repository has quoted one of them in the wrong
place. For satellite-to-satellite co-location, used to build the
TROPOMI–GOSAT training pairs, "co-location criteria are observation times within
1 h and pixel centers within 5 km". For satellite-to-TCCON evaluation, which is
the comparison this project would make, "when evaluating TROPOMI or the blended
TROPOMI + GOSAT product, satellite and TCCON pairs are defined to be those
within 1 h and 100 km of each other and a surface elevation difference of no
more than 250 m", against 2 h and 500 km for GOSAT, with a reduced 50 km radius
for the Edwards station. They find 632,683 TROPOMI–TCCON pairs.

**The consequence is that the nine-day Hefei comparison already run is not a
validation and cannot be reported as one.** It gave a blended bias of −5.74 ppb
with a standard deviation of 5.79 over nine coincident days, and it was computed
without prior alignment, so part of that number is an artefact of comparing two
differently constructed quantities. It is a feasibility measurement, which is
what `notes/grounding-yrd.md` calls it, and prior alignment is the step that
would change its status.

## Model class, and what the 2023 thesis's method would have required

The thesis described a neural network. The reproduction built none, and the
literature on where the crossover lies supports that choice without settling it.

A study of stroke severity prediction subsampled its training set to 100, 300 and
900 patients and trained both a regularised linear regression and an
eight-layered network on each. Linear regression was significantly better at
100; at 300 the two were indistinguishable, with overlapping confidence
intervals; and deep learning began to significantly outperform only at 900. Mean
performance rose from R² 0.279 ± 0.005 at 100 to 0.337 ± 0.006 at 900, an
improvement of about 20 percent for a ninefold increase in data (Bourached et
al., 2023, *Brain Communications* 6, doi:10.1093/braincomms/fcae007). **This
project's lattice is 926<!--#composite.covered_cells--> cells, and
531<!--#grid.rice_rows--> of them carry a rice fraction** — between the 300 and
900 of that study, which is the region where it found no difference.

The conventional rule of thumb is more demanding: "the most widely used
rule-of-thumb is that the sample size needs to be at least a factor of 10 times
the number of weights in the network" (Alwosheel, van Cranenburgh and Chorus,
2018, *Journal of Choice Modelling* 28, 167–182,
doi:10.1016/j.jocm.2018.07.002). And a genomic prediction study on 63,526
broiler observations found a deep network showing "superior prediction
correlation using up to 3% of training set, but poorer prediction correlation
after that" than Bayesian ridge regression, though it also had the lowest mean
squared error of prediction and lower bias across all dataset sizes (Passafaro
et al., 2020, *BMC Genomics* 21, doi:10.1186/s12864-020-07181-x). That is a
mixed result, not a clean one, and should be reported as such.

**And the complication has to be reported honestly, because it cuts against the
convenient conclusion.** A recent tabular benchmark finds that "in small-sample
regimes, most algorithms perform similarly within overlapping confidence
intervals", that high-capacity networks "remain competitive ... despite the
limited data", and that these "results challenge the common belief that neural
networks require large datasets to be effective, and emphasize the importance of
using statistical testing rather than relying solely on mean scores" (*MultiTab*,
arXiv:2505.14312). So the defensible statement is **not** that a network could
not have been fitted at this sample size. It is that at this sample size a
network would be expected to perform comparably to the linear baselines, which
reach held-out R squared 0.085<!--#baseline.impervious_r2--> against the spatial
null's 0.332<!--#baseline.null_r2-->, and that a comparable performance to a
model that explains nothing is not a reason to build one.

## What the field actually builds for this class of problem

This is the strongest available statement about the 2023 thesis's framing, and it
is a statement about absence.

Every published machine-learning approach to sparse satellite column fields that
this search found is **gap-filling or downscaling**, not segmentation: a hybrid
Transformer–BiLSTM reconstructing daily global land XCO2 at 0.1 degrees from 2003
to 2022 (*Earth System Science Data* 18, 4279–4301, 2026,
doi:10.5194/essd-18-4279-2026); a spatial-features deep fusion model for XCO2
(*Atmospheric Research* 308, 107542, 2024,
doi:10.1016/j.atmosres.2024.107542); a gap-filled spatiotemporal reconstruction
of XCH4 (*Atmospheric Pollution Research* 17, 102918, 2026,
doi:10.1016/j.apr.2026.102918); a signal-domain masked spatio-temporal fusion of
TROPOMI and GEOS-Chem for XCO and XCH4, using a residual U-Net refined with
meteorological drivers and model output (*Earth System Science Data*
preprint essd-2025-817); and gradient boosting for downscaling.

**Every one of them uses meteorology, a model prior, or both as predictors.**
CarbonTracker, MODIS land surface temperature and vegetation indices, ERA-5
temperature and wind, GEOS-Chem output, CAMS, precursor gases. **None of them
predicts a column from land cover.** The 2023 thesis's design is not a variant
of what the field does; it is a different question, asked with the predictor set
the field does not use for it.

The direct comparison is instructive about difficulty. Downscaling XCO2 and XCH4
over the Arabian Peninsula with gradient boosting, using CarbonTracker, MODIS
Terra and ERA-5 as inputs, achieved R² 0.98 and RMSE 0.58 ppm for XCO2 and R²
0.63 and RMSE 13.26 ppb for XCH4, the latter described as moderate accuracy
(*Scientific Reports* 15, 2025, doi:10.1038/s41598-024-84593-9). **Methane is the
hard one even with the right predictors**, and an RMSE of 13.26 ppb is
comparable to this project's entire between-cell spread of 14.9 ppb.

One warning applies to any gap-filling this project might attempt. Under
persistent cloud, both the satellite retrieval and the MODIS predictors are
unavailable, and both are then filled from coarser model fields — so the
predictor and the target share a common source exactly where the target is
missing, which is circularity rather than prediction. The Yangtze River Delta is
persistently cloudy, and `data/processed/README.md` already records that the
composite's largest coverage gap is a connected block in southern Zhejiang.

## Resolution, which settles the 0.1-degree question

0.25 by 0.3125 degrees is the field's working resolution for regional TROPOMI
methane inversions: it is the GEOS-Chem grid used by the Southeast US observing
system simulation experiment (Sheng et al., 2018, *Atmospheric Measurement
Techniques* 11, 6379, doi:10.5194/amt-11-6379-2018), by the 2019 US inversion
(Nesser et al., 2024) and by the Integrated Methane Inversion framework. This
project's 0.25-degree lattice is therefore standard rather than coarse, and the
question of whether to refine it has an answer in the literature.

The answer has two halves and they pull in opposite directions. A global
comparative inversion found that a GOSAT inversion achieved **232 degrees of
freedom for signal for non-wetland emissions against TROPOMI's 151** — 238 and
155 including wetlands and OH — despite TROPOMI having about 100 times more
observations, because "error correlation on the 2° × 2.5° scale of the inversion
and large spatial inhomogeneity in the number of observations make it less useful
than GOSAT for quantifying emissions at that resolution" (Qu et al., 2021,
*Atmospheric Chemistry and Physics* 21, 14159). GOSAT observes 10.5 km spots
separated by 250 km. **So density does not buy information when errors are
correlated on the grid scale.** But the same paper's counterweight is explicit:
"finer-scale regional inversions would take better advantage of the TROPOMI data
density." The gain from a finer grid is therefore smaller than a cell count
suggests rather than absent, and it is bounded by the error correlation rather
than by the number of soundings.

**What bounds it absolutely is transport error, and that is the ceiling on this
whole enterprise.** Comparing the transport model against TCCON columns gives "a
model transport error standard deviation of 12 ppb, larger than the instrument
errors when aggregated on the 25 km model grid scale, and with a temporal error
correlation of 6 h" (Sheng et al., 2018). Against a between-cell spread of 14.9
ppb, **transport error alone is comparable to the entire signal this project is
trying to explain, at exactly this project's resolution.** That is not a reason
the study should not have been done; it is the reason a null result at this
resolution is the expected outcome rather than a surprising one, and it belongs
in the discussion as such.

## How to report a negative result, which changes what the paper may claim

"Regrettably, and despite the null hypothesis being simple, elegant and often
underpinned by evidenced or reasoned convictions, conventional p-value analysis
can only argue against the null hypothesis, never in favour of it."
"Unfortunately, around half of scientific research papers falsely report
non-significant results as indicating no effect" (Halsey, 2025, *Biology
Letters* 21, doi:10.1098/rsbl.2025.0506).

**This project's central claim is a statement in favour of the null.** "Land
cover does not explain the methane field over the Yangtze River Delta at 0.25
degrees in 2018" asserts absence. Held-out R² comparisons against a spatial null
and non-significant partial correlations cannot support that assertion, however
many of them are reported. **What is currently supportable is that no
association was detected**, which is a weaker and different claim, and the paper
should say the weaker one unless it does the work for the stronger.

The work for the stronger claim is specified. For the absence of a *meaningful*
effect, equivalence testing: two one-sided tests against non-nil nulls at plus
and minus a predetermined smallest effect size of interest, where failing to
reject the nil null while also rejecting both non-nil nulls is evidence of
equivalence, and where "because the equivalence test is based on two one-sided
tests, a 90% confidence interval is appropriate when those tests are assessed
against the 5% alpha level". For the absence of *any* effect, likelihood ratios
and Bayes factors. Tooling exists — the TOSTER package in R, or Jamovi and JASP
(Halsey, 2025).

**The bounds are a scientific judgement that must be named and defended, and the
region grounding supplies a basis for naming them.** If the water regime carries
a factor of 13.7 in emission at constant rice area, and rice extent explains
none of that, then the smallest land-cover effect worth detecting can be set at
what a policy-relevant effect would have to be — an effect large enough that a
land-cover intervention would change the column field measurably. That is a
defensible bound rather than an arbitrary one, and it is the argument a reviewer
would want.

One more requirement, from the systematic-review guidance rather than the
statistics literature: "if a 'positive' but statistically non-significant trend
is described as 'promising', then a 'negative' effect of the same magnitude
should be described as a 'warning sign'", and reviews should not "confuse 'no
evidence of an effect' with 'evidence of no effect'" (*Environmental Evidence*,
guidance for authors, section 9, *Interpreting findings and reporting conduct*).
**This project read the blended field's partial correlation of −0.082 at p 0.013
as over-control rather than as a negative urban effect.** That reading is
probably right — a negative urban methane effect has no physical mechanism — but
it has not been given the balanced treatment the guidance requires, and a
paragraph explaining why a significant negative coefficient is being set aside
is owed to the reader rather than optional.

## What could not be verified

Fifteen premises carried into this pass did not survive checking: thirteen about
the literature and two about this repository's own text. They are listed because
the next person to meet one in a search snippet should know it was tested, and
because three of them are DOIs that resolve confidently to the wrong paper,
which is the most dangerous failure mode in a register that verifies by DOI.

Two further premises were refined rather than failed, and are at the end.

**Three DOIs resolve to unrelated papers.** `10.1016/j.rse.2025.114953` is a
paper on disease spectral indices of apple trees; the prediction-powered
inference paper is `10.1016/j.rse.2025.114949`, four digits away.
`10.1016/j.spasta.2025.100893` is "A spatial autoregressive graphical model"; the
spatially-lagged errors-in-variables paper is
`10.1016/j.spasta.2025.100909`. And `10.1016/j.rse.2019.111199` does not exist:
111199 is Stehman and Foody's page number, and the DOI is
`10.1016/j.rse.2019.05.018`. **A resolving DOI is not a verified citation**, and
these three would all have passed a "does it resolve" check.

**Lu et al.'s effective sample size range is 1.2× to 17.4×, not 1.1 to 2.5**, and
the largest improvement is for an income coefficient, not for slope. The figures
near 1.1 to 2.5 in that paper belong to the stratified area-estimation appendix,
which is a different quantity.

**Lu et al.'s novelty claim is narrower than "first to apply PPI to remote
sensing".** Verbatim, it is "the first work to estimate remote sensing regression
coefficients without assumptions on the structure of map product errors".

**No statement that PPI does not require ground truth sampled according to a
pre-determined stratification map could be found** in that paper, which in fact
uses such a map in its Amazon case study. Not written.

**Nab and Groenwold's simulation ranges and results are all different from the
premise.** Reliability 0.2 to 0.9, not 0.05 to 0.91; sample sizes 125 to 1,000,
not 125 to 4,000; regression calibration median bias 1.4 percent with an
interquartile range of 0.8 to 2 percent, not 0.8 percent; simulation-extrapolation
median bias −12.8 percent, not −19.0 percent. Four wrong figures in one premise,
and the 0.8 is the lower edge of an interquartile range read as a point estimate.

**The reliability-ratio thresholds could not be sourced to a peer-reviewed
work.** That a ratio below 0.8 warrants correction and below 0.5 is severe was
found only in software documentation. The attenuation mechanism and the
naive-to-corrected ratio are textbook and are written; the thresholds are not.

**Bartlett's assertion could not be verified and the year is wrong.** The
literature on effective degrees of freedom names Bartlett (1946), not 1935, and
no source was found for the claim that lack of independence is a bigger challenge
than non-Gaussianity. Not written.

**kNNDM is Linnenbrink, Milà, Ludwig and Meyer (2024), not Milà et al.** Milà et
al. (2022) is the leave-one-out predecessor, NNDM. Both are cited above and the
attribution is now right.

**The claim that overoptimism is dramatic for k-nearest neighbours and random
forest but not for linear methods, because they are not expressive enough to
overfit, could not be located in any of the four papers it was plausibly
attributed to.** It is not in Ploton et al., not in Hawinkel et al., not in
Deppner and Cajias, and not in Mahoney et al. Not written — which is a loss,
because it was the finding most favourable to this project's choice not to build
a network.

**The Level 3 representativeness weighting is not "1 minus g".** The factor is
called `f`, and it is *high* for cells with large representativeness
uncertainty; the weighting gives more weight to cells with *low*
representativeness uncertainty. The mechanism is as described and the notation
is not.

**No source was found for "successful applications had at least 70,000
observations"** as a neural network sample size benchmark. Not written. The 10×
weights rule is sourced and written.

**Two premises about this repository's own text were wrong, and both are worth
recording because they were premises about what needed correcting.** The
repository has never carried a figure of 0.2 ppb as destriping's worth — the
string does not occur anywhere, and `notes/decisions.md` describes destriping
without any quantitative claim. And no file states that error-adjusted area with
confidence intervals is a standard this project fails to meet: the only two
places the standard is mentioned,
[`notes/dataset-leads.md`](dataset-leads.md) and
[`notes/references.md`](references.md), already say that recommendations 1 to 3
apply and 4 and 5 do not. **So there was nothing to correct for that item**, and
the correction the pass did find was elsewhere: the errata's request for a kappa
coefficient.

**Two premises were refined rather than failed.** The degrees-of-freedom pair 232
against 151 is correct **for the non-wetland emissions partition**; the totals
including wetlands and OH are 238 and 155, and a paper should say which it means.
And the destriping approach the super-emitter study follows is attributed there
to Borsdorff et al. (2018), while the operational procedure applied from
September 2024 is Borsdorff et al. (2024) — two different references a year and a
method apart.

### The 11 September amendment's own failures

Seven more premises failed when the inversion frame was added, and they are kept
separate from the fifteen above because they belong to a different pass.

**A fourth bad DOI.** `10.1016/j.jclepro.2023.137100` resolves to "Accuracy
design optimization of a CNC grinding machine towards low-carbon manufacturing".
The rice emission-factor paper is `10.1016/j.jclepro.2023.137245`, 145 apart in
the same journal and year. That makes four DOIs in this register that resolve
confidently to the wrong paper, and `scripts/build_references_bib.py` now holds
all four.

**IMI 2.0's default anthropogenic prior is EDGAR v8, not v6.** Verbatim from the
paper: "updated global anthropogenic emissions from EDGAR v8". Version 6 was
IMI 1.0's default. Getting this wrong would misdate every criticism of the
prior by two releases.

**The China inversion's 600 is a state vector size, not a mixture-model member
count, and its DOFS is 167.** Verbatim: "167 independent pieces of information
(DOFS) out of the 600 Gaussian state vector elements". The figure of 134 is a
different paper entirely — Zhong et al. (2026) on the value of ground stations —
and the two are not comparable because each counts out of a different state
vector.

**The Chengdu–Chongqing improvement figures could not be verified.** A
correlation rising from 0.41 to 0.62 and an RMSE falling from 127.51 to 78.80
ppb under dynamic error weighting are not confirmed: the article is paywalled and
no abstract carrying them is indexed. The paper, its method and its resolution
are verified and written; the numbers are not.

**The US urban paper is in *Science Advances*, not *Science*.** Its DOI is
`10.1126/sciadv.adz9308`.

**The urban sector composition figures do not match that paper.** A composition
of landfills 40 percent, gas distribution 9 percent including 4 percent
post-meter, and wastewater 6 percent was carried into the urban pass. The paper
gives, for the 12 urban areas together, 59 percent landfills, 25 percent
downstream gas, 9 percent wastewater and 7 percent other anthropogenic in the
inventory, and 62 / 23 / 8 / 7 in the posterior. **The direction is the same and
stronger**: landfills dominate by more than the premise claimed.
[`notes/grounding-urban.md`](grounding-urban.md) uses the verified figures.

**The "up to 200 percent" landfill underestimate belongs to a different
paper.** It is the finding of Wang, Y., and others (2024, *Nature Sustainability* 7,
doi:10.1038/s41893-024-01307-9), cited by the US urban paper rather than found
by it.

Two premises were refined. The Southeast Asian downscaling that uses impervious
surface downscales **CO₂**, not methane, which matters because a proxy that works
for diffuse combustion need not work for point-like methane sources. And
Nikolaisen et al.'s volume is 409, not 406.
