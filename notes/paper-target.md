# The target, the queue, and what is still ungrounded

The plan file. It records what this project is now for, what has to happen
before that output exists, and what the four grounding records have not covered.
It adds no literature; everything it cites is already in
[`notes/references.md`](references.md).

It exists because the target changed and was written down nowhere. Four
grounding records now exist — [region](grounding-yrd.md),
[methods](grounding-methods.md), [urban](grounding-urban.md) and the
[dataset inventory](dataset-leads.md) — and each implies work that none of them
collects.

## The output is a paper, not a thesis revision

The 2023 thesis was submitted, cannot be edited, and **becomes prior work that
the paper cites.** `writeup/Duyst_Thesis.pdf` is preserved as submitted for that
reason, and [`ERRATA.md`](../ERRATA.md) is an errata rather than a set of edits
for the same reason: nothing in the thesis was changed to match it.

That reframing is already visible in the repository — the three grounding
records call themselves draft material for a paper's sections — but it had never
been stated as the project's target.

### The shape

Most thesis sections survive, compressed. An introduction carrying background
and the case study, then methods, results, discussion and conclusion. **The
literature review stops being a chapter and becomes citations inside the
introduction**, which is what the three grounding records are for: the region
record is introduction and discussion material, the methods record is methods
and limitations, the urban record is both.

Three things a paper needs that a thesis does not, and that this project
currently lacks:

**A contribution statement.** What is new. Candidates exist — an independently
rebuilt composite, a negative result that survives four predictor pairs, a
sampling-artefact diagnosis — but none is written as a claim of contribution.

**A comparison to prior work.** The register now holds the material for one, and
the comparison the paper most needs is to the rice-paddy exchange it already
cites: Zhang et al. (2020) found a rice fingerprint in satellite methane, Zeng
et al. (2021) argued the correlation does not imply causation, and this work
measured the same thing independently over a different domain. That is a
three-way comparison and it is not written.

**Every claim carrying a number a reviewer can check.** Closer than the other
two. `scripts/verify_claims.py` already ties the numbers in the prose to the
artefacts they came from, which is more than most papers do — but the marked
numbers are in READMEs and grounding records, not in paper prose, because there
is no paper prose.

And one thing a paper cannot do that a thesis can: **say "future work would
include".** A paper either does the thing or explains why it cannot be done.
That is why the emissions feasibility question matters, and why the first item
in the queue below is the free preview that answers it.

### The candidate framings, in the order they are currently defensible

**A reproduction paper.** Land cover does not explain the observed methane field
over the Yangtze River Delta at 0.25 degrees in 2018, established across two
urban products, two rice products, two cross-validation schemes and a published
bias-corrected field, with the diagnostic work as the contribution. **Writeable
now**, subject to the restatement below.

**A methods paper on what a sparse column record can and cannot constrain at 25
km.** The same material framed as a capability statement rather than as a
negative finding about land cover. The methods grounding supplies most of what
this framing needs, including the transport-error ceiling of 12 ppb against a
between-cell spread of 14.9, and the degrees-of-freedom figures that say what
information the observing system carries. Writeable after the queue's first
tier.

**An emissions paper**, if a rice reimplementation or a GRPI-method inventory,
an improved prior and an inversion come together. Several rounds away, and the
IMI preview is the step that would say whether it is reachable at all.

These are not ranked by value and no choice is made here. They are ranked by how
much has to happen first.

### The first framing's central claim needs restating

This is the one constraint on the framing that is already settled.
[`notes/grounding-methods.md`](grounding-methods.md) records that conventional
p-value analysis "can only argue against the null hypothesis, never in favour of
it", and that around half of papers falsely report non-significant results as
indicating no effect (Halsey, 2025, doi:10.1098/rsbl.2025.0506). Held-out R
squared comparisons and non-significant partial correlations cannot support a
claim in favour of the null, however many of them are reported.

So the wording matters and the difference is not cosmetic:

* **"Land cover does not explain the methane field"** is a claim in favour of the
  null. It needs equivalence bounds — two one-sided tests against a named
  smallest effect size of interest — and the bound has to be defended rather
  than chosen.
* **"We find no evidence that land cover explains the methane field"** is a claim
  about a failed detection. It needs nothing further and is supportable today.

The paper should use the second unless and until the equivalence work in the
queue is done. The region grounding supplies a basis for naming a bound if it
is: if water regime carries a factor of 13.7 in emission at constant rice area
and rice extent explains none of it, the smallest land-cover effect worth
detecting can be set at what a policy-relevant effect would have to be.

### The state of the writing, which is the largest single gap

Eleven figures, a repository README, an errata, four grounding records, a
decision log of nearly four thousand lines, and **no prose that reads as a
paper.** The methods live in a pipeline diagram and a decision log rather than
in sentences. The results live in a README's headline paragraphs and in figure
captions.

**That gap is ahead of the remaining three figures in importance.** The figure
inventory in [`figures/README.md`](../figures/README.md) records eleven built of
a planned fourteen, and the three unbuilt ones — predictor maps, a fold map, a
sampling-artefact map — are all drawing rather than analysis. None of them is
between the project and a draft. The absence of connected prose is.

## The work queue

Drawn from all four grounding records rather than from any brief, and **ordered
by what gates what rather than by ease.** Per-item cost and citation detail for
the methods-derived items is in `notes/decisions.md` under *The work the methods
grounding implies*; this is the ordering and the dependency structure, which
that section does not give.

Nothing here is implemented and nothing is claimed.

### Tier 0 — free, no dependencies, and each changes what can be claimed

These need no new data and no re-run. **They are first because they have no
excuse**, and because two of them gate the framing rather than the analysis.

**1. The IMI preview.** Establishes whether TROPOMI can constrain methane
emissions over these four provinces, by reporting the expected degrees of
freedom for signal over a user-selected domain. The tool runs at this project's
exact resolution and already ingests the blended field committed here, and its
own documentation says the preview "has no significant costs". *Established by*
[`notes/grounding-methods.md`](grounding-methods.md) and
[`notes/dataset-leads.md`](dataset-leads.md). *Gates* the emissions framing
entirely, and gates whether the paper may say the conversion is infeasible — the
thing a paper cannot leave as future work.

**2. Effective degrees of freedom on every reported correlation.** Every Pearson
and partial correlation here is computed over 926<!--#composite.covered_cells--> cells with n treated as 926
while both fields are strongly autocorrelated, so every p-value is
anti-conservative. One function over the committed covariate table. *Established
by* the methods record. *Gates* every stated p-value, including the blended
field's partial correlation of −0.082 at p 0.013 that the repository currently
reads as over-control.

**3. The residual autocorrelation range.** The block size has never been
justified from the data; the defensible choice is the autocorrelation range of
the model's residuals, and what exists is Moran's I of the residual field, a
different quantity. *Established by* the methods record. *Gates* item 4 and any
defence of the spatial-blocks design.

**4. A buffered leave-one-out decay curve.** Predictive power against increasing
buffer radius, so the decay with distance from training data is visible as a
shape rather than asserted at one buffer. *Established by* the methods record's
spatial cross-validation section. *Gated by* item 3. *Would settle* whether the
gap between this project's two schemes — a spatial null of 0.332<!--#baseline.null_r2--> under blocks
against −0.091 under leave-one-province-out — is the extrapolation effect Wadoux
et al. predict.

### Tier 1 — one small download each, no re-gridding

**5. The CCD-Rice validation polygons.** 1.9 MB of GeoParquet under CC-BY-4.0,
already verified accessible, with 777 polygons inside the four provinces across
six cover classes. *Established by* [`notes/dataset-leads.md`](dataset-leads.md).
**This is the prerequisite for the accuracy assessment and there is no
substitute**, because it is the only independent reference data more accurate
than the map that this project has found anywhere.

**6. CCD-Rice itself, and GISA-new.** A second rice product reaching 2000 and
2010, which the committed NESDC product does not, and a fourth impervious
product covering all three thesis years, which no other candidate does. 5.37 GB
and 5.82 GB, both verified accessible. *Established by* the dataset inventory.
*Gates* any statement about the historical years that rests on more than one
product.

**7. The irrigation regime maps.** Water-saving against flooding irrigation at
500 m, which is the largest missing covariate the region record identifies — the
mechanism with a factor of 13.7 in emission at constant rice area. No deposit is
named, so the route is the thing to establish. *Established by* the region
record and the inventory.

**8. MMCP.** Monthly provincial methane by sector with rice split into single
and double season, 2013 to 2022. Its licence is CC-BY-NC-ND, the most
restrictive in the inventory, so **the constraint has to be established before
work depends on it.** *Established by* the inventory. *Would check* the region
record's seasonality argument against an independent sectoral series.

### Tier 2 — gated by Tier 1

**9. The accuracy assessment.** Mean deviation, mean absolute deviation and
regression of the mapped fraction against a reference fraction built from the
polygons, which is the correct frame for a continuous field rather than an error
matrix. Prediction-powered inference is the route that makes a small reference
set usable. *Established by* the methods record. *Gated by* item 5, and by one
condition that must not be forgotten: the calibration set "must be separate from
the training dataset used to train the machine learning model", so **the
polygons are clean for the NESDC and GISA layers and contaminated for CCD-Rice
itself**, whose thresholds were re-determined against filtered rice areas.

**10. Quantity and allocation disagreement between GAIA and GISA.** The
repository reports their difference as a single percentage of provincial area,
which is quantity disagreement alone and says nothing about whether the two put
impervious surface in the same places. Only allocation disagreement attenuates a
coefficient. *Established by* the methods record's reliability section. *Needs*
only the two committed products.

**11. De-attenuation.** Regression calibration, or SIMEX-WLS where non-constant
residual variance matters — and it does, since a cell mean rests on between
1<!--#composite.min_soundings--> and 410<!--#composite.max_soundings--> soundings. **This is the most consequential item in the queue**, because
measurement error in a predictor is the only mechanism that could manufacture
this project's null, and building second predictors with different errors is
evidence against that rather than a measurement of it. *Established by* the
methods record. *Gated by* items 9 and 10, which supply the error variances: the
polygons for rice, the allocation disagreement for impervious surface as a lower
bound.

### Tier 3 — one re-gridding pass over the granules, shared by five items

**These five share a single 28.9 GB transfer and should be done together or not
at all.** That is the whole reason for grouping them: each alone would cost the
same as all five.

**12. Grid and filter on the precision variable.** `methane_mixing_ratio_precision`
is in every granule, carries the random error from the spectral fit, and is
neither gridded nor filtered on. Published precedent filters under 10 ppb.
*Established by* the methods record.

**13. Apply the albedo floor and the blended-albedo ceiling.** A SWIR albedo
floor of 0.05 and a blended-albedo ceiling of 0.75 outside summer preserve 69
percent of high-quality retrievals and cut seasonal regional biases by 7 to 21
percent. This project retains 166<!--#cov.albedo_negative--> cells whose annual mean SWIR albedo is
below zero. *Established by* the methods record.

**14. Accumulate within-cell variance.** The checkpoint holds sums and counts
only, so the spread a representativeness estimate needs is not recoverable from
it. *Established by* the methods record. *Gates* item 16.

**15. A growing-season composite.** The region record establishes that 82.4
percent of the composite's soundings fall outside the middle-rice window while
the field's own fitted cycle peaks inside it. **The region record also
establishes that this is not free**: the accumulator holds annual sums, and a
mean over a subset of days cannot be recovered from one, so this needs the
re-grid rather than being a cheap recomputation. *Established by* the region
record.

**16. Destriping.** Official destriping is applied only from 7 September 2024 in
v2.07 and older orbits have not been reprocessed, so this project's 2018 data
will never have it and a self-implemented per-row correction is the only route.
`notes/decisions.md` records it as the cheapest of four missing preprocessing
steps, which remains true of the implementation and not of the transfer.
*Established by* the methods record.

### Tier 4 — gated by Tier 3

**17. Representativeness weighting in place of sounding-count weighting.**
Coverage "is not an effective metric to limit representation errors", and this
project uses it in a figure, a raster band and every model weighting. The
implementable alternative weights by within-cell spread scaled by the uncovered
fraction. *Established by* the methods record. *Gated by* item 14. **This item
has the widest reach in the queue**: it changes the weighting of every baseline
in the repository, so everything downstream of the baseline suite moves with it.

### Tier 5 — last, because they consume everything above

**18. Equivalence bounds for the central claim.** Two one-sided tests against a
named smallest effect size of interest. Low in computation and high in
judgement. *Established by* the methods record. *Gated by* item 11, because the
effect size to bound is the de-attenuated one, not the attenuated one.

**19. Prior alignment, and only then a TCCON comparison.** Adjusting satellite
and TCCON retrievals to a common prior using the satellite averaging kernel.
The nine-day Hefei comparison already run was computed without it and is a
feasibility measurement rather than a validation. *Established by* the methods
and region records. *Independent of* the rest of the queue, which is why it can
run in parallel, but it is last in value because it constrains the field's
precision rather than the paper's claim.

**20. Specification curve analysis as the reporting frame.** Three methane
fields, four predictor pairs, two schemes and two weightings is forty-eight
specifications, which is a curve and not a table. *Established by* the methods
record. **Necessarily last**, because it reports the final specification set and
every item above changes what that set contains.

### What gates what, in one paragraph

Item 1 gates the paper's framing and costs nothing, so it is first on both
counts. Items 2 to 4 are free and change reported statistics, with 3 gating 4.
Item 5 gates 9, which with 10 gates 11, which gates 18 — that is the critical
path to the strong form of the central claim, and it runs four deep. Tier 3 is a
single decision about one transfer, and within it 14 gates 17, which is the item
that moves every number downstream of the baselines. Item 20 is last by
construction. Items 6, 7, 8 and 19 sit off the critical path and can be done
whenever.

## What is still ungrounded

Recorded so that the gap is visible rather than assumed closed.

**The rice layer has no grounding record of its own.** Its findings are
scattered through the region record — the calendar, the water regime, the
cropping-system transitions — and through the methods record, which holds the
emission-factor chain and the reference polygons. The urban layer got a record
on 11 September 2026 precisely because that scattering was judged a gap; the
rice layer has the same gap and has not been given the same treatment. It is in
the planned sequence and has not been done.

**The methane layer likewise.** The composite's own properties are documented at
length in `data/processed/README.md`, and the methods record holds the
retrieval's uncertainty, the preprocessing chain and the representativeness
problem. But there is no single record that says what the literature establishes
about this instrument over this kind of domain, in the way the region record does
for the region. Also in the planned sequence, also not done.

**The satellite question has not been asked at all.** Whether other instruments
or validation sources have been overlooked — GOSAT and GOSAT-2 in their own
right rather than as the blended product's other half, Sentinel-2 or EMIT or
PRISMA for point sources, EM27/SUN campaigns, aircraft or tower records beyond
the two already ruled out — has never been searched. The region record ruled out
the in-domain column and tower options it knew of, and the urban record notes
that hyperspectral instruments have been used against Chinese landfills, but no
pass has gone looking systematically. **This is the largest unexamined area and
it is not in the planned sequence**, which is why it is recorded here.
