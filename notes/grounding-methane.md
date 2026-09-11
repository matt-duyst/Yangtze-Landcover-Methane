# The methane layer's grounding

Draft material for a paper's introduction and discussion, and the fourth
grounding record. The other three are organised by what they are about:
[`notes/grounding-yrd.md`](grounding-yrd.md) the region,
[`notes/grounding-urban.md`](grounding-urban.md) and
[`notes/grounding-rice.md`](grounding-rice.md) the two predictors.
[`notes/grounding-methods.md`](grounding-methods.md) holds how a study of this
shape should be built. **What none of them holds is the target variable as a
subject** — what an XCH4 column is, what can and cannot be done to it, and what
the field's own machinery for turning columns into emissions actually requires.
`notes/paper-target.md` recorded that gap and this record closes it.

Its conclusion, stated first: **the gap between what this project measured and
what its title implies is not a processing gap, it is a different method.** There
is no step that converts a column to a flux. The conversion is an inversion, and
an inversion needs a transport model, a prior, an optimisation and an error
characterisation — four things this repository has none of. That is not a defect
to be repaired but a boundary to be stated, and the literature below states it
precisely enough to quote.

Every figure was checked against its source before it was written. Where a figure
could not be verified it is named as unverified and the number is not written;
the closing section lists every case. Numbers from this repository's own
artefacts are marked for [`scripts/verify_claims.py`](../scripts/verify_claims.py)
where a resolver exists.

## What the target is, and what it is not

XCH4 is the column-averaged dry-air mole fraction of methane, integrated from the
top of the atmosphere to the surface and weighted by air mass. It is a
concentration, not a flux, and **there is no processing step that converts one
into the other.** Going from a column to an emission requires an atmospheric
transport model to relate emissions to concentrations, a prior emission estimate
to be corrected, an optimisation to find the correction, and an error
characterisation to say how much of the answer came from the observations rather
than from the prior. That is a Bayesian inversion, and
`notes/grounding-methods.md` establishes it as the field's method for this class
of problem.

**This has to be stated plainly because the 2023 thesis's title implies a
conversion that does not exist as a chain.** The thesis correlated a column field
against land-cover fractions, which is a defensible thing to do and is what this
reproduction reproduces. What it is not is emission estimation, and the
difference is not one of rigour or resolution but of method. A paper should say
so in its own voice rather than let a reader infer that the columns were
converted and the conversion was crude.

### The alternative target, which is the one finding that could raise the signal

Everything else in these four records explains the null result. This is the one
thing found in any pass that could plausibly *increase* an association, and it
works by removing a term from the target rather than by adding a predictor.

**A fused product separates the troposphere from everything above it.** The
MUSICA IASI / RemoTeC TROPOMI fused methane data set, version 4.1, is deposited
at `10.35097/wq583rnzpmd83m5g` on the Karlsruhe Institute of Technology's RADAR
repository (Shahzadi, K., Schneider, M., Lo, N. Y., and Borsdorff, T., 2026) and
documented in Shahzadi, K., Schneider, M., Lo, N. Y., Hase, F., Meyer, J.,
Cayoglu, U., Borsdorff, T., and Martinez-Velarte, M. C. (2026), *A multi-year
global methane data set obtained by merging observations from TROPOMI and IASI*,
*Earth System Science Data* 18, 2153–2177, doi:10.5194/essd-18-2153-2026.

It carries three variables rather than one. The paper defines them by atmospheric
mass: "we define the lowermost 50 % of the atmosphere as the troposphere and the
uppermost 50 % of the atmosphere as the upper troposphere/stratosphere", giving a
total column `XCH4`, a tropospheric `tro_XCH4` and an upper-troposphere/stratosphere
`uts_XCH4`. The combination is "realized by means of a Kalman filter that uses
the MUSICA IASI data as the background and the TROPOMI data as the new
observation", over "42 months (from January 2018 to June 2021)", built from
"about **444 million** individual and high-quality TROPOMI observations" and
yielding "about **289 million** individual data points".

**Why it matters for this project specifically.** A total column includes
stratospheric methane, whose variability over this domain is driven by
tropopause height, dynamics and transport from the tropics — none of which has
anything to do with a rice paddy or a road in Jiangsu. Any such variance enters
this project's target as noise that no land-cover predictor can explain and that
no amount of bias correction removes, because it is not a bias. `tro_XCH4`
removes it by construction. **Running the association on a tropospheric partial
column rather than a total column is therefore the one change to the analysis
that could raise the ceiling rather than explain why it is low**, and it is
queued in [`notes/paper-target.md`](paper-target.md).

**Four caveats belong with it and none is fatal.** The TROPOMI input is not this
project's processing version: the paper describes a "beta version of the
operational S5P product" with "an updated fit of the surface reflectance spectral
dependency to a third-order polynomial fit", where this repository reads
processing version 020400. Coverage is the intersection of TROPOMI and IASI
sampling and so is sparser than TROPOMI alone, over a domain whose coverage is
already the thing `data/processed/README.md` documents as marginal. The
information content of the separation is small: the paper reports that for the
combined tropospheric product "DOFS values are weakly above 1.0 for almost all
locations around the globe", so the split yields barely more than one independent
piece of information — **which is materially less than the two distinct pieces
this pass was briefed to expect, and the smaller figure is the one written.** And
the definition of the tropospheric layer is a choice about atmospheric mass
fraction rather than a physical tropopause, so it is not comparable across
products that define their partial columns differently.

## Superobservations, and why this composite is the wrong shape for an inversion

The single most useful technical fact in this record is a definition, because it
shows that this project's central artefact is not an inversion input and cannot be
made into one.

**IMI 2.0 defines its observation vector by cell and by orbit.**
"Super-observations average all individual TROPOMI observations for a given
GEOS-Chem grid cell and TROPOMI orbit. We call them super-observations following
Eskes et al. (2003) because they have lower error than individual observations"
(Estrada et al., 2025, doi:10.5194/gmd-18-3311-2025, already in the register).
Per cell **per orbit** — so one number for each cell each time the satellite
passes over it, which over a year is hundreds of numbers per cell rather than one.

The justification is worth quoting because it bounds what is lost: "Loss of
information in this averaging of individual observations is negligible because
GEOS-Chem model values are the same for all observations being averaged, and
retrieval averaging kernels are similar." **Averaging within a cell and an orbit
is free. Averaging across orbits is not**, because the model values are then not
the same and the thing being averaged away is exactly the time variation the
inversion uses.

**State the consequence for this repository's own artefact.** The composite
averages 110,920<!--#composite.soundings--> soundings into
926<!--#composite.covered_cells--> annual cell means. It discards the temporal
dimension entirely. So the composite and an inversion's observation vector are
different objects at the level of what each one *is*, and no processing converts
the first into the second — the information was destroyed at construction, for
good reasons that had nothing to do with inversion. **This is not a criticism of
the composite**, which was built to answer a cross-sectional question and answers
it. It is the reason the emissions route in `notes/paper-target.md` is a new
computation rather than an extension of a committed one.

**And the per-granule bitmaps in the checkpoint may be closer to what is
needed.** `data/interim/extent_2018.npz` retains per-granule acquisition times
and cell coverage — the material `notes/grounding-yrd.md`'s monthly sounding
counts are computed from. A granule is not an orbit and a cell mean is not a
superobservation, but the temporal resolution an inversion needs exists there in
a form the committed composite does not have. That the file is gitignored is the
practical obstacle, and it is a smaller one than re-gridding from raw granules.

## The forward operator, which is why no processing step reaches a flux

An inversion does not transform observations into emissions. It runs the model
forward and compares.

**IMI's own description of the comparison step**, in the context of its
bias-correction archive: "For each observation, we apply the TROPOMI operator,
which describes the sensitivity of the observation to different vertical levels,
to the co-located GEOS-Chem vertical profile, giving us pairs of TROPOMI XCH4 and
simulated GEOS-Chem XCH4" (Estrada et al., 2025). So the modelled atmosphere is
put through the instrument's own averaging kernel to produce a *virtual*
observation — what TROPOMI would have seen, given the model's emissions and
transport — and that virtual observation is what the real one is differenced
against.

**The direction of the operator is the whole point.** Nothing is inverted
pointwise. The emissions are adjusted until the virtual observations match the
real ones, subject to the prior. **A column is therefore never converted into a
flux; a flux field is repeatedly converted into columns until it matches.** That
is what makes the transport model and the prior load-bearing rather than
auxiliary, and it is why "the thesis should have converted columns to emissions"
is not a coherent criticism of the 2023 work.

**The area-weighting detail carried into this pass could not be verified** — that
where several model cells overlap one TROPOMI pixel their profiles are
area-weighted — and is not written. The vertical remapping and the averaging-kernel
application are verified and written.

### The correlated-error problem, in its third appearance, and how IMI handles it

This repository has now met the same problem three times: in the composite's
standard-error-of-the-mean assumption, in the effective-degrees-of-freedom gap
that Tier 0 corrected, and here.

IMI states it exactly: "Using individual observations in the inversion with a
diagonal observational error correlation matrix assumes that errors in individual
observations are uncorrelated. In fact, **transport errors for individual TROPOMI
observations within a GEOS-Chem grid cell are perfectly correlated**, and
retrieval errors may be correlated as well" (Estrada et al., 2025).

**IMI's response is a treatment, not a fudge, and this pass was briefed
otherwise.** Super-observations *are* the treatment: collapsing the perfectly
correlated set within a cell and orbit into one observation, with its error
variance derived by the residual error method of Heald et al. (2004) as applied by
Chen et al. (2023). What remains after that is handled by a regularisation
parameter — "γ ∈ [0, 1] is a regularization parameter to compensate for
unaccounted error covariances in the observational system" — **chosen by a
chi-square criterion rather than by an L-curve corner**: "users can choose an
optimal value of γ such that (x̂ − xA)ᵀ SA⁻¹ (x̂ − xA) ≈ n ± √(2n) ... corresponding
to the expected value of the chi-square distribution". The L-curve framing
carried into this pass is not what this source does and is not written.

What is still unsolved is the *prior* side, and `notes/grounding-methods.md`
already records IMI's admission on that: "spatial error correlations in the prior
estimate are also certainly present but difficult to define and have been ignored
for now."

## Boundary conditions, which are favourable for this domain

A regional inversion has to specify what flows in at its edges, and a bias there
propagates into the emissions. For this domain the sensitivity has been measured
and it is small.

**The measurement is for East Asia and this study area is its most sensitive
part.** Sensitivity inversions with varied fixed eastern boundary conditions
"find relatively small effects on quantifying annual emissions as expected from
prevailing westerlies in midlatitudes": a positive bias of 10 ppbv "would result
in a reduction of annual methane emissions by **3.3 Tg a−1 (∼2 %)** over the East
Asia domain, **1.8 Tg a−1 (∼2 %)** over China, and **0.75 Tg a−1 (∼3 %)** over
eastern China (EC), the most affected region" (Liang, R., Zhang, Y., Chen, W.,
Zhang, P., Liu, J., Chen, C., Mao, H., Shen, G., Qu, Z., Chen, Z., Zhou, M.,
Wang, P., Parker, R. J., Boesch, H., Lorente, A., Maasakkers, J. D., and
Aben, I., 2023, *Atmospheric Chemistry and Physics* 23, 8039–8057,
doi:10.5194/acp-23-8039-2023).

**Record both halves of that.** Eastern China is named as the most
boundary-sensitive region in the domain, so this study area is the worst case;
and even in the worst case a 10 ppbv boundary bias moves the answer by about 3
percent. The mechanism is geometry: the eastern boundary is downwind of the
midlatitude westerlies, so errors introduced there advect out of the domain
rather than into it. **For a project whose whole difficulty is that it sits in
eastern China, this is the one structural feature of the region that is
favourable.**

The same authors are the authors of the Heilongjiang rice inversion already in
the register, so the boundary result and the rice result come from the same
group and the same modelling system.

### The tooling exists to check this before running anything

A preview metric for boundary-induced error was published specifically to be run
in advance. Nesser, H., Bowman, K. W., Thill, M. D., Varon, D. J.,
Randles, C. A., Tewari, A., Cardoso-Saldaña, F. J., Reidy, E., Maasakkers, J. D.,
and Jacob, D. J. (2025), *Predicting and correcting the influence of boundary
conditions in regional inverse analyses*, *Geoscientific Model Development* 18,
9279–9291, doi:10.5194/gmd-18-9279-2025, provides a predictive metric to support
domain specification before an inversion and a diagnostic metric to assess the
influence afterwards. **So the question "is this domain's boundary a problem" is
answerable before any inversion is run**, which puts it in the same class as the
IMI preview's DOFS estimate: a cheap gate rather than a result.

### And IMI's own handling, with its two standard fallbacks

IMI "maintains a global 3-D archive of bias-corrected GEOS-Chem fields (called
smoothed TROPOMI fields) to serve as unbiased boundary conditions for any
TROPOMI inversion domain or period. The archive is produced by correcting a
global continuous GEOS-Chem simulation at **4° × 5°** resolution with smoothed
TROPOMI concentrations (**12° × 15°** spatially and **±15 d** temporally) and
applying zonal mean corrections over the oceans" (Estrada et al., 2025). **The
global simulation is 4° × 5°, not the 2° × 2.5° carried into this pass**, and the
correction is applied to all 47 vertical layers.

The initialisation runs deep: the archived simulation "starts on 1 April 2018
(1 month before the start of the TROPOMI record) with ICs from a separate
GEOS-Chem simulation initialized in 1985", and "this multidecadal spin-up
simulation uses **monthly interpolated** global surface observations of methane
concentrations from the NOAA GLOBALVIEW flask dataset as BCs" — interpolated, not
kriged, which is what this pass was briefed. The purpose is stated: transporting
surface boundary conditions through the atmosphere "takes years for the
stratosphere", so the long spin-up produces an initial condition "consistent with
both long-term trends in tropospheric methane and stratospheric transport".

**The date coincidence is exact and worth recording.** IMI's global archive begins
1 April 2018, one month before the TROPOMI record. `data/processed/README.md`
records that this project's own CH4 record "begins on 2018-04-30". So this
project's first granule falls on the last day of IMI's spin-up month: the
archive is ready exactly when this study's data starts, with no gap and no
overlap to discard.

Where bias remains after all that, the field's two standard fixes are to optimise
boundary concentrations as part of the state vector, or to let buffer cells
surrounding the domain absorb it — "in IMI 1.0, boundary conditions are further
corrected in the inversion using buffer grid cell clusters surrounding the region
of interest" — or both.

### Two practical facts that lower the barrier more than they look like they do

**All the inputs sit in public buckets.** The paper's data availability names
three: TROPOMI methane at `registry.opendata.aws/sentinel5p/`, the blended
TROPOMI+GOSAT product at `registry.opendata.aws/blended-tropomi-gosat-methane/`,
and "the GEOS-FP emission fields, boundary condition fields, and meteorological
fields" at `registry.opendata.aws/geoschem-input-data/`. The second of those is
the field this repository already committed as the composite's third band.

**And the inversion domain need not be a box.** IMI 2.0 accepts a domain
specified "by providing a shapefile with any geometry", where IMI 1.0 took a
regional rectilinear domain. This project's study area is four provinces, which
is a shapefile and not a rectangle, and `notes/decisions.md` records the
rectilinear lattice as a choice made for griddability. **The tool would accept
the provinces directly.**

## Transport error, which is the ceiling

`notes/grounding-methods.md` already holds the load-bearing figure and it is not
repeated as a claim here: a model transport error standard deviation of 12 ppb at
25 km with a 6-hour temporal error correlation, against this composite's
between-cell spread of 14.9 ppb. That section should be read as part of this
record.

Three further results sharpen it, and two of them are specific to China.

**GEOS-Chem has a named, mechanistic methane bias over China.** "The model bias
over China, we argue, was caused by weakened vertical advective transport as a
result of a combination of regridding the winds and the strong surface emissions
in China that resulted in CH4 being partly trapped in the boundary layer over the
continent" (Stanevich, I., Jones, D. B. A., Strong, K., Parker, R. J.,
Boesch, H., Wunch, D., Notholt, J., Petri, C., Warneke, T., Sussmann, R.,
Schneider, M., Hase, F., Kivi, R., Deutscher, N. M., Velazco, V. A.,
Walker, K. A., and Deng, F., 2020, *Geoscientific Model Development* 13,
3839–3862, doi:10.5194/gmd-13-3839-2020). **Strong surface emissions are a
precondition of the bias**, which means the bias is largest where the signal is —
and this domain is one of the three sub-national regions carrying 60 percent of
China's emissions.

**The resolution dependence is quantified, and not at the resolutions this pass
was briefed with.** The comparison in that paper is 4° × 5° against 2° × 2.5°,
not 0.25° × 0.3125° against 2° × 2.5°: "at 4°×5° there is up to a **40 %
reduction** in the tracer concentrations in the middle and upper troposphere
relative to 2°×2.5°, with a noticeable increase in the tracer concentrations in
the lower troposphere ranging from **10 % to 25 %**". So the effect is a
redistribution in the vertical — too much below, too little above — and it is
measured between two coarse grids rather than between a coarse grid and IMI's
operating resolution. **The written figures are the ones the source gives**, and
the direction is the one that matters here: a coarse model traps methane in the
boundary layer over China, which inflates simulated surface concentrations and
deflates the column aloft.

**A finer grid now exists and has been demonstrated over this exact domain.**
"0.125° × 0.15625° (≈12 km × 12 km) resolution" is available for global
GEOS-Chem "by exploiting a new GEOS advection data archive (grid-scale winds)",
and the demonstration is here: "nested-grid simulations are conducted over
eastern China (**100–125° E, 17–45° N**) at both 0.125° × 0.15625° and 0.25° ×
0.3125° resolutions", with "application to the Integrated Methane Inversion (IMI)
show[ing] regional-scale results consistent with a 25 km inversion but higher
information content and greater spatial detail" (Wang, X., Sulprizio, M. P.,
Zhuge, Y., Martin, R. V., and Jacob, D. J., 2026, *Atmospheric Chemistry and
Physics* 26, 6857–6867, doi:10.5194/acp-26-6857-2026). **That nested domain
contains this project's lattice entirely**, which makes the demonstration a
directly usable precedent rather than an analogy.

### The sharpest bound on the emissions route

An observing system simulation experiment sets the limit, and the limit is
conditional in a way that lands badly for this project.

"4D-Var analysis of the TROPOMI data can improve monthly emission estimates at
25 km even with a spatially biased prior or model transport errors (**42 %–93 %**
domain-wide bias reduction; R increases from 0.51 up to 0.73). **However, when
both errors are present, no single inversion framework can successfully improve
both the overall bias and spatial distribution of fluxes relative to the prior**
on the 25 km model grid." In that case "the ensemble-mean optimized fluxes have a
domain-wide bias of 77 Gg d−1 (comparable to that in the prior), with spurious
source adjustments compensat[ing]" (Yu, X., Millet, D. B., and Henze, D. K.,
2021, *Geoscientific Model Development* 14, 7775–7793,
doi:10.5194/gmd-14-7775-2021).

**This project's situation has both errors.** The prior is spatially biased —
that is the finding [`notes/grounding-rice.md`](grounding-rice.md) records for
EDGAR's rice distribution, and the urban record's for population-allocated
sectors. And the transport error over China is the mechanistic bias named above.
So the OSSE's "both errors present" case is the applicable one, and its verdict
is that the inversion recovers neither the total nor the pattern reliably. The
experiment is over North America, which is a limit on transfer; the two error
sources it combines are both documented here specifically.

**Read that as the ceiling on what the emissions route could deliver, not as a
reason not to take it.** A 42-to-93 percent bias reduction is what is available
when one error dominates; when both do, the honest deliverable is a regional
total with an error bar and not a cell-level attribution. That is the same
conclusion this project's own Tier 0 arithmetic reached, and the same one
`notes/grounding-yrd.md` records a national study reaching for all of China.

## The sink, which is the one thing that does not complicate the picture

Methane's chemical loss is dominated by reaction with the hydroxyl radical, and
the lifetime is long. "From the methyl chloroform proxy, one infers a
tropospheric lifetime of methane of τCH4OH = **11.2 ± 1.3 years** for 2000", while
"atmospheric chemistry models find a methane lifetime of τCH4OH = **9.7 ±
1.5 years**" (Penn, E., Jacob, D. J., Chen, Z., East, J. D., Sulprizio, M. P.,
Bruhwiler, L., Maasakkers, J. D., Nesser, H., Qu, Z., Zhang, Y., and Worden, J.,
2025, *Atmospheric Chemistry and Physics* 25, 2947–2965,
doi:10.5194/acp-25-2947-2025). Those two figures disagree by more than their
stated uncertainties, which is why replacing the methyl chloroform proxy is the
paper's subject.

**For this domain the disagreement does not matter, and the arithmetic says why.**
The lattice is roughly 750 km across. At the 5 km/h mean wind speed the IMI
preview's own default assumes — the value `notes/grounding-methods.md` records in
the DOFS formula — air crosses it in about six days; at a more typical
mid-latitude 5 m/s, in under two. Against a lifetime of order ten years, the
fraction of methane destroyed while crossing the domain is of order one part in a
thousand. **So chemical loss inside this domain is negligible, and an inversion
here can prescribe OH without that choice propagating into the answer.** That is
a genuine simplification and it is the only place in these four records where the
regional scale makes something easier rather than harder.

**Three claims carried into this pass about the global contrast could not be
verified and are not written**: that posterior uncertainty in global OH induces no
significant correlated error in the spatial distribution of emissions; that
inversion-based global methane emissions range from 518 to 757 Tg per year across
ten OH fields; and that almost all global chemistry models calculate about 15
percent too much OH. The paper searched for them is the one that would most
plausibly carry them and does not. The qualitative point that the same machinery
carries a large OH-driven spread globally and essentially none regionally is
**supported by the arithmetic above rather than by a citation**, and it is written
that way.

## Wetlands as a prior, which overlap the rice prior in the same cells

The wetland prior is where the rice confound reappears from the other side, and
the product's own authors document it.

**WetCHARTs excludes Chinese rice extents and says the exclusion is incomplete.**
"Rice paddies likely amount to < 20 % of wetland CH4 emissions, and the majority
of rice paddy areas are **implicitly** excluded from our analysis. GLOBCOVER
distinguishes between natural and irrigated water bodies, and **GLWD explicitly
excludes rice paddy extents in China** (which alone account for a large portion of
global rice paddy CH4 emissions). However, **satellite-based inundation fraction
retrievals are unable to distinguish the temporal variability in co-located
agriculture and natural wetland inundation extent.** Moreover, a 0.5° × 0.5°
carbon cycle model resolution may be insufficient to resolve spatial differences
in wetland and agricultural C cycling. **The inadvertent inclusion of co-located
rice CH4 emissions is therefore a potential source of bias in our approach.** We
note that **the distinction between wetland and rice CH4 emissions has yet to be
consistently addressed** in global wetland CH4 emission quantification efforts"
(Bloom, A. A., Bowman, K. W., Lee, M., Turner, A. J., Schroeder, R.,
Worden, J. R., Weidner, R., McDonald, K. C., and Jacob, D. J., 2017,
*Geoscientific Model Development* 10, 2141–2156, doi:10.5194/gmd-10-2141-2017).

**Two corrections to how that was carried into this pass.** It is GLWD — the
Global Lakes and Wetlands Database, one of WetCHARTs' inputs — that excludes
Chinese rice extents, not WetCHARTs itself; and the exclusion of rice areas is
described as *implicit*. Both make the caveat stronger rather than weaker.

**And the same passage names the aquaculture problem before anyone was looking
for it.** It continues: "the quantitative distinction of CH4 emissions from
wetland and non-wetland freshwater extent remains challenging with the current
spatial resolution (∼ 25 km) of surface inundation retrievals", and it lists
"very small ponds" first among the non-wetland freshwater bodies whose emissions
are unresolved. That is the same source
[`notes/grounding-rice.md`](grounding-rice.md) records as absent from every
inventory, identified as a resolution problem in a wetland product's own
discussion in 2017.

**The product and its role.** IMI's wetland default is "WetCHARTs v1.3.1 (Bloom
et al., 2021)", and "the IMI uses as default monthly wetland emissions from the
mean of the WetCHARTs ensemble, but users can replace this default with
WetCHARTs or LPJ-wsl climatologies" (Estrada et al., 2025). The version in use is
1.3.1 rather than the 1.0 the 2017 paper documents, distributed through ORNL
DAAC; `notes/dataset-leads.md` carries the route.

**One defect in that prior is a seasonality defect, which is the rice story
again.** In IMI's own CONUS demonstration, "the seasonal offset from July to
September is largely driven by wetlands, which may be explained by WetCHARTs' use
of **air temperature rather than soil temperature** to predict wetlands
emissions" (Estrada et al., 2025). So the two priors that overlap in this
project's cells — rice and wetland — each carry a documented seasonal-phase error,
EDGAR's a uniform June peak for all of China and WetCHARTs' a temperature-driver
substitution. **A seasonal inversion over this domain would be correcting two
mistimed priors at once, in the same cells.**

### The co-location warning, generalised

The problem is not specific to China. "Tropical wetlands are co-located with
other sectors such as livestock and oil and gas production in Africa and South
America, and rice paddies in South Asia, which means inverse analyses are subject
to source misattribution" (Chen, Z., Jacob, D. J., Lin, H., Balasus, N.,
Hancock, S. E., Estrada, L. A., East, J. D., Zhang, Y., Wang, X., He, M.,
Liu, M., and Varon, D. J., 2026, *Environmental Science & Technology* 60,
21159–21167, doi:10.1021/acs.est.6c05412). **The first author is GRPI's first
author**, so the same group built the Landsat-inundation rice inventory and the
Landsat-inundation tropical wetland inventory and states the co-location problem
in both.

### And the template for handling it already exists in this register

Liang et al.'s Heilongjiang rice inversion ran "sensitivity inversions" that
substituted the prior inventories for coal and for wetlands, in order to assess
how those priors affect the rice estimate. IMI 2.0 makes the same move cheap by
construction: "once K has been constructed, any ensemble of analytical inversions
exploring the sensitivity to different inversion parameters can be easily and
rapidly generated", and the paper's own discussion proposes exactly that —
"differences could be investigated in the IMI with sensitivity inversions swapping
prior emissions, observational products, and inversion parameters". **So if an
inversion is ever run here, the confound-handling is an ensemble rather than an
argument**, and it costs one Jacobian.

## Retrieval choice, which bounds what any single-product study can claim

The last section is the one that most directly limits this project's own field,
because it says that the answer depends on which TROPOMI product you read.

**Three products, one inversion, three different answers.** Assimilating three
TROPOMI methane products into the same variational inversion for 2019 over Europe
gives emission budgets of "+2 %" for SRON, "−1 %" for the blended product and
"**−33 %**" for WFMD relative to the prior, against "−9 %" for a surface-based
inversion (Sicsik-Paré, A., Fortems-Cheiney, A., Pison, I., Broquet, G.,
Opler, A., Potier, E., Martinez, A., Schneising, O., Buchwitz, M.,
Maasakkers, J. D., Borsdorff, T., and Berchet, A., 2026, *Atmospheric Chemistry
and Physics* 26, 10423–10454, doi:10.5194/acp-26-10423-2026). **A 35-point spread
in a continental emission budget, from the choice of retrieval alone.**

**And the cause is the thing this project measured.** "Machine learning
predictions of XCH4 differences point to **aerosol scattering and albedo
sensitivity** as the largest contributors to the differences" (Sicsik-Paré et al.,
2026). This repository has an albedo dependence in its own field, a bias
correction for it, and a Tier 0 result showing that every partial correlation
controlling for albedo on the operational field loses significance. That
dependence is not a local artefact of this domain; it is the leading term in the
disagreement between retrievals at continental scale.

**The mechanism is structural to the retrieval, which is why a correction removes
only part of it.** TROPOMI's methane retrieval "uses the full-physics algorithm
RemoTeC and simultaneously retrieves XCH4, surface albedo and atmospheric
scattering properties" (Sicsik-Paré et al., 2026). Three quantities from one
spectrum: the albedo is not an external covariate that contaminates the methane,
it is a co-retrieved parameter, so error in one is error in the other by
construction. **A post-hoc regression against albedo can remove the part of that
coupling that is linear and stationary and cannot remove the part that is not**,
which is a more precise statement of the limitation `ERRATA.md` records for the
bias correction than "the correction is incomplete". The further claim carried
into this pass, that aliasing between these parameters produces artifacts that
bias the inference of methane emissions, **could not be verified in this source
and is not written as a quotation**; what is written is the co-retrieval, which
is stated plainly and carries the same implication.

**The validation gap belongs here and it cuts in this project's favour.** TCCON
does not sample regions with SWIR albedo above 0.4, where the largest TROPOMI
biases relative to GOSAT are found — **this claim could not be verified to a
primary source in this pass and is not written as a figure.** What
`notes/grounding-methods.md` does record from the blended product's own paper is
the albedo-dependent bias structure that motivated the blending, and what this
project's own covariate table records is that its domain's SWIR albedo is low. The
qualitative point that this domain sits in the better-validated part of the albedo
range is consistent with both and is written as such.

## What the methane grounding establishes

**There is no processing step from a column to a flux**, and the thesis's title
implies one. The conversion is a Bayesian inversion requiring a transport model,
a prior, an optimisation and an error characterisation. A paper should state that
boundary in its own voice.

**The composite is the wrong shape for an inversion and cannot be reshaped.**
IMI's observation vector is one number per cell per orbit; the composite is one
number per cell per year. The temporal dimension an inversion uses was discarded
at construction, for reasons that were correct for the question the composite was
built to answer. The per-granule checkpoint is closer to what would be needed.

**One change could raise the association rather than explain it.** A fused
TROPOMI–IASI product supplies a tropospheric partial column, removing
stratospheric variance that no land-cover predictor could ever explain. Its
caveats are a beta-version input, sparser coverage, a mass-fraction rather than
physical layer definition, and information content weakly above one degree of
freedom.

**The boundary is the one structural feature of this region that is favourable.**
Eastern China is the most boundary-sensitive part of the East Asian domain, and
even there a 10 ppbv bias moves annual emissions by about 3 percent, because the
eastern edge is downwind. A predictive metric for boundary influence exists and
can be run before an inversion.

**Transport error is the ceiling and it is worse here than generically.**
GEOS-Chem's methane bias over China is mechanistic — regridded winds plus strong
surface emissions trapping methane in the boundary layer — so the bias is largest
where the signal is. A 12 km capability exists and has been demonstrated over a
nested domain that contains this lattice. And the governing OSSE result is that
with both a spatially biased prior and transport errors present, no framework
improves both the total and the pattern; this project has both.

**Chemical loss inside the domain is negligible** — of order one part in a
thousand across a 750 km domain against a decadal lifetime — so OH can be
prescribed. That is the only simplification the regional scale grants.

**The wetland prior overlaps the rice prior in these cells, and its own authors
said so in 2017.** Chinese rice extents are only implicitly excluded, inundation
retrievals cannot separate co-located agriculture from natural wetland, and the
distinction "has yet to be consistently addressed". Both priors also carry
documented seasonal-phase errors, so a seasonal inversion here would be
correcting two mistimed priors in the same cells.

**And the answer depends on which retrieval you read.** Three TROPOMI products in
one European inversion span 35 points of emission budget, with albedo and aerosol
scattering named as the largest contributors — and TROPOMI co-retrieves albedo
with methane, so the coupling is structural rather than a contamination a
regression can fully remove.

## What could not be verified

Nine claims carried into this pass did not survive, in addition to the
corrections recorded inline above.

**Three OH claims.** That posterior uncertainty in global OH induces no
significant correlated error in the spatial distribution of emissions; that
inversion-based global emissions span 518 to 757 Tg per year across ten OH
fields; and that global chemistry models compute about 15 percent too much OH.
None is in the paper they were attributed to, which is the one most likely to
carry them. The regional-negligibility conclusion they were to support is instead
derived from the domain's own dimensions and a stated wind speed.

**Two lifetime figures.** An OH lifetime of 9.6 years and a net lifetime of 8.4
to 9.25 years do not match the source read, which gives 11.2 ± 1.3 years from the
methyl chloroform proxy and 9.7 ± 1.5 from chemistry models. The source's figures
are written. The 9.6 and 8.4 values appear to belong to the IPCC Third Assessment
Report, which was not read.

**The forward operator's area-weighting step** — that profiles from several model
cells overlapping one pixel are area-weighted — could not be verified and is not
written.

**The aliasing sentence.** That aliasing between co-retrieved albedo, scattering
and methane produces artifacts biasing emission inference is not written as a
quotation. The simultaneous retrieval of all three is verified and carries the
same implication.

**The TCCON albedo-sampling gap.** That TCCON does not sample SWIR albedo above
0.4, where TROPOMI's largest biases against GOSAT are found, could not be
verified to a primary source. No figure is written.

**And the fused product's degrees of freedom.** A DOFS of about 2.4 with two
distinct pieces of information is not what the paper reports; it reports DOFS
"weakly above 1.0 for almost all locations" for the combined tropospheric
product. The smaller figure is written, and it materially weakens the case for the
tropospheric target without removing it.

Four figures were **corrected rather than dropped**, and each correction came from
reading the source rather than from a second search. IMI's global boundary-condition
simulation is 4° × 5°, not 2° × 2.5°. Its multidecadal spin-up interpolates the
GLOBALVIEW flask record monthly rather than kriging it. Its regularisation
parameter is chosen by a chi-square criterion, not an L-curve corner — and
super-observations are a genuine treatment of the correlated-error problem rather
than the absence of one. And the GEOS-Chem resolution sensitivity is measured
between 4° × 5° and 2° × 2.5°, giving up to a 40 percent *reduction* aloft and a
10-to-25 percent increase below, not a 40 percent surface overestimate against
IMI's operating grid.
