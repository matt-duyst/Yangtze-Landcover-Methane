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

### What a reviewer would object to, and the answer

Added 14 September 2026, from the reviewer pass this file recorded as never
having been run. **Every earlier round followed what was interesting, which is a
more generous filter than a reviewer's and surfaces different literature.** Three
rounds asked instead what someone assigned to reject this paper would say. They
found one serious objection, two secondary ones, one unfounded worry, and — not
expected — the answer to the serious objection.

#### The serious objection: every component already exists

The novelty criterion is universal and it is written down. *Atmospheric Chemistry
and Physics*, the venue most of this project's methane literature sits in, gives
as its first principal review criterion **"Scientific significance — Does the
manuscript represent a substantial contribution to scientific progress within the
scope of Atmospheric Chemistry and Physics (substantial new concepts, ideas,
methods, or data)?"**, asks reviewers whether a paper "present[s] novel concepts,
ideas, tools, or data", requires authors to "clearly indicate their own
new/original contribution", and requires a revised manuscript to be rated "good
to outstanding" on every principal criterion to be accepted (ACP review
criteria, journal's own page, fetched 14 September 2026).

**Now apply it honestly, component by component.** Every part of this project's
central finding is already published somewhere:

* That local XCH4 variation over **Southeast China specifically** is driven more
  by advected than by locally emitted methane is Zeng et al. (2021), and
  [`notes/grounding-rice.md`](grounding-rice.md) records it as an adverse finding
  naming this region.
* The albedo dependence of the TROPOMI retrieval is documented by Lorente et al.
  and is the reason the blended product Balasus et al. built exists, both already
  in the register.
* A transport error of 12 ppb at 25 km with a 6-hour error correlation is
  Sheng et al. (2018), and [`notes/grounding-methods.md`](grounding-methods.md)
  carries it as the ceiling on the whole enterprise.
* That inversion cannot separate interspersed sources is Desjardins et al.,
  **and the same review says it of TROPOMI by name** — "not likely to be useful
  to separate the contributions of managed and unmanaged CH4 sources because of
  their coarse spatial resolution and their lack of sensitivity". That is an
  assertion, not a measurement, so the contribution is unchanged and the framing
  is: the field expected this and did not measure it. The introduction now says
  so rather than leaving a reviewer to raise it.
  (2018), quoted in this file's synthesis section.
* And that degrees of freedom for signal bound what an observing system can
  resolve is standard Rodgers optimal-estimation theory, which
  `notes/grounding-methods.md` records as the field's own information metric.

**So a reviewer can say, correctly, that the paper confirms known limitations in
a new place.** "We reproduced a null in a new region" does not survive the
criterion above, and it should not: a substantial contribution has to be more
than a fifth instance of a documented effect. **This is the objection to prepare
for, not a fatal problem**, and the section after next supplies what answers it.

#### Two secondary objections, both already in the queue

**One year of one instrument.** The comparable studies in this register use
multi-year records — three years for the Greater Bay Area inversion, four for
the urban-trend paper, two decades for the sub-national budget. A reviewer will
ask why not extend, and the answer has to be given rather than avoided: 2018 is
the first year of the TROPOMI record, it is the 2023 thesis's own analysis year,
and IMI's invertible archive begins one month before this project's first
granule. None of that is a reason not to extend; all of it is a reason the
single year is where the work started. **The paper must answer this question in
its own voice.**

**No validation and no accuracy assessment.** The Hefei TCCON comparison is nine
coincident days with no prior alignment, and no land-cover layer here has an
accuracy assessment at all. Both are already queued, and both are honest
limitations rather than oversights. *This passage previously said
`notes/grounding-methods.md` records "Olofsson's first three recommendations
apply and are unmet, and that no distributed reference data exists for the
impervious products". Both halves are now superseded and the record was
corrected on 13 September 2026 while this one was not.* Recommendation 1 does
not apply to a complete-coverage continuous-field comparison, so the
reproduction owes **2 and 3**; and reference products over this domain do exist
— four were verified — but every one is less accurate than the products it would
assess, so the debt is unpayable rather than unpaid.

#### The unfounded worry: publication bias against null results

This was carried as a background concern across several passes and it is weaker
than assumed, which is worth knowing rather than worrying about.

Mandatory trial registration cut the effect sharply in the one field where it has
been measured before and after. In anesthesia research, the odds ratio for
abstracts with positive results proceeding to publication over those with null
results was **"2.01 [95% confidence interval (CI): 1.52, 2.66; P < 0.001]"**
before mandatory registration and **"1.28 [95% confidence interval (CI): 0.97,
1.67; P = 0.076]"** after — not significant — becoming significant only under
adjustment for sample size and abstract quality, at **"OR 1.34; 95% CI: 1.02 to
1.76; P = 0.037"** (Chong, S. W., Imberger, G., Karahalios, A., Wang, A.,
Burggraf, M., Louis, M., Liskaser, G. M., Bianco, A., and Peyton, P. J., 2023,
*PLOS ONE* 18, e0282839, doi:10.1371/journal.pone.0282839).

And the computational-sciences literature argues the opposite way about vehicles
for negative findings. **"Comparison studies can be a good vehicle for negative
research findings"**, and **"the systematic exclusion of negative results from
publication might in some cases be misleading"** (Boulesteix, A.-L. and
Eugster, M. J. A., 2012, *A plea for neutral comparison studies in computational
sciences*, arXiv, doi:10.48550/arXiv.1208.2651). **That paper also supplies the
qualification, which is the more useful half**: it is "impossible (and
uninteresting anyway) to publish all negative results", and the authors'
recommendation is that "the publication of negative findings within large
well-designed comparison studies would be a sensible compromise in order to
diffuse negative findings without congesting the literature with negative
papers."

**State the conclusion, because it redirects the worry.** A null result is not
the obstacle; the novelty framing is. And the remedy the second source
recommends — carry the negative finding inside a larger, well-designed
assessment rather than as a paper of its own — is the framing the next section
adopts, arrived at from a completely different direction.

### Capability assessment is an established contribution with its own vocabulary

The answer to the objection is that this project's finding is not a null result
about land cover. It is a capability assessment, and capability assessment is a
recognised paper type in exactly the venues this work would go to.

**The type exists and is cited.** Turner, A. J., Jacob, D. J., Benmergui, J.,
Brandman, J., White, L., and Randles, C. A. (2018), *Assessing the capability of
different satellite observing configurations to resolve the distribution of
methane emissions at kilometer scales*, *Atmospheric Chemistry and Physics* 18,
8265–8278, doi:10.5194/acp-18-8265-2018, frames the question as one of
"limitations from instrument precision, pixel resolution, and measurement
frequency", and states that "the extent to which [dense observations] can provide
fine-scale information on methane sources has yet to be explored". It assesses
five configurations — TROPOMI at 7 × 7 km² and 11 ppb daily, three GeoCARB
variants, and a hypothetical 1.3 × 1.3 km² 1 ppb hourly instrument — **through an
observing system simulation experiment with WRF-STILT, not against real
observations.**

**And the type has a review that supplies the vocabulary.** Jacob, D. J.,
Varon, D. J., Cusworth, D. H., Dennison, P. E., Frankenberg, C., Gautam, R.,
Guanter, L., Kelley, J., McKeever, J., Ott, L. E., Poulter, B., Qu, Z.,
Thorpe, A. K., Worden, J. R., and Duren, R. M. (2022), *Atmospheric Chemistry
and Physics* 22, 9617–9646, doi:10.5194/acp-22-9617-2022: "We cover retrieval
methods, precision and accuracy requirements, inverse and mass balance methods
for inferring emissions, source detection thresholds, and **observing system
completeness**."

**The term and its content are worth quoting exactly, because the brief that
commissioned this pass had the wrong half of it.** Observing system completeness
is defined twice in that review, once per instrument class. For point-source
imagers it is the interplay of "detection threshold, spatial coverage, and return
time". For **area flux mappers**, which is what TROPOMI on a 25 km grid is, it is
the interplay of "pixel size, retrieval precision, observation density, fraction
of successful retrievals, and return times". **The second list is this project's
own measured quantities**, item for item: 0.25 degrees, the retrieval's
uncertainty, 110,920<!--#composite.soundings--> soundings over
926<!--#composite.covered_cells--> cells, and a coverage fraction that
`data/processed/README.md` documents. So the paper is not inventing a frame; it
is filling in one the field has already named for instruments of this class.

A third source is a preprint and is recorded as one. Montenegro, N.,
Berchet, A., Martinez, A., Thanwerdas, J., Bousquet, P., Pison, I., and
Saunois, M. (2025), *Capability of current observing systems to monitor CH4
emissions from the regional to the global scales*, EGUsphere,
doi:10.5194/egusphere-2025-5923, discussion opened 23 December 2025. It reports
that while "global-scale uncertainties in total CH4 emissions are relatively
small (±5%), they increase significantly at regional scales exceeding ±20% for
high latitudes", that "differences in satellite and in situ measurement
uncertainties, as well as variations in data density, further influence the
precision of CH4 flux estimates", and that the benefits of sectoral
disaggregation "are amplified in high-emission regions due to larger absolute
uncertainties and **more complex source mixtures**". That last phrase is this
project's domain described from the outside.

### What distinguishes this project's version, which is the novelty claim

This is what the paper rests on and it should be written carefully.

**The existing capability literature is simulations and surveys.** Turner et al.
is an OSSE: an observing system posited, a truth field posited, and the
recoverability of the second from the first computed. Jacob et al. is a review of
what instruments could do in principle. The Montenegro preprint works at
regional-to-global scale across an ensemble. **None of them is a capability
assessment of a real, sparse column record over one region whose sources
overlap.**

**And this project's assessment carries two limits where the literature's carry
one.** An OSSE measures information content: whether the observations can resolve
a posited flux field. It does not measure whether the resolved field could be
attributed to a sector, because in an OSSE the sectors are separate by
construction.

*The information-content limit.* Expected degrees of freedom for signal accrue
across many weakly constrained cells rather than a few well constrained ones, so
a regional total is constrainable and cell-level attribution is not.
[`notes/decisions.md`](decisions.md) holds the figures — 3.98 to 22.21 over the
5 to 12 Tg a⁻¹ band the literature supports for this domain — together with the
qualification that must travel with them: **they are a reimplementation of IMI's
own closed-form estimate evaluated locally, not an inversion run**, and no cell
in the swept range reaches an averaging-kernel sensitivity above 0.5.

*The identifiability limit.* Even where a total is constrained, sectoral
attribution comes from the prior's spatial distinctness rather than from the
observations — the synthesis section below establishes that from one inversion's
posterior error correlations, below 0.35 for coordinate-mapped landfills against
0.45 to 0.87 for three population-allocated sectors — and this domain's sources
are interspersed in every direction at once.

**The relation between them is the sharpest form of the claim.** Either limit
alone says the question is not answerable as asked. **Together they say why no
refinement of the same design would fix it**: more observations raise the degrees
of freedom and do nothing to the identifiability, and a better prior sharpens
attribution without adding information the observations do not carry. That
conjunction is what is new here, and it is new because it requires a real domain
with overlapping sources — which is precisely what an OSSE abstracts away.

### The transfer argument, because a single-region study has to earn its lesson

The standing objection to a one-region study is that the general lesson is
asserted rather than derived. Here it can be derived, and the reason is worth
stating plainly: **neither limit comes from anything particular to the Yangtze
River Delta.**

The degrees-of-freedom estimate uses IMI's own published formula with IMI's own
default parameters, and `notes/decisions.md` records the reimplementation and its
inputs. The transport-error ceiling, the interspersed-source limit and the
identifiability mechanism are general results taken from the literature rather
than measured here. **The region supplied the numbers; it did not supply the
structure.**

So the claim that travels is this: **any mixed-source region observed at 25 km
with comparable observation density faces both limits, and the region's
particulars set the magnitudes rather than the structure.** A region with denser
coverage moves the degrees of freedom and leaves the identifiability untouched. A
region whose sources are spatially separate moves the identifiability and leaves
the information content untouched. The Yangtze River Delta is unusual only in
having both problems at their most acute — three of nine Chinese sub-national
regions' worth of emissions on under a third of the land, with rice, aquaculture,
wetland, coal, waste and gas distribution interleaved across the same cells.

### The framing, chosen 14 September 2026

**This section previously recorded three candidate framings, ranked by how much
had to happen first, and chose between them explicitly not at all.** The reviewer
pass above closes that. The paragraph below chooses; the three candidates are
kept after it, marked, per this file's convention of leaving superseded reasoning
standing rather than deleting it.

#### The contribution statement

**The contribution is a capability assessment of a real satellite column record
over a region whose methane sources overlap, not a negative result about land
cover.** What is new is the pairing of two independent limits measured on the
same domain — an *information-content* limit, that expected degrees of freedom
for signal accrue across many weakly constrained cells so that a regional total
is constrainable while cell-level attribution is not, and an *identifiability*
limit, that sectoral attribution derives from the prior's spatial distinctness
rather than from the observations — together with the demonstration that the
second is untouched by any improvement to the first.

**Three things that statement must not be read as claiming**, because the work
that exists does not support them and the statement has to survive the novelty
test rather than merely sound like it does:

* **Not an inversion.** The degrees-of-freedom figures are a reimplementation of
  IMI's own closed-form estimate evaluated over this lattice, which
  `notes/decisions.md` states in the record, the script's docstring and the
  recipe note. The number that would settle it is still one free preview run.
* **Not a priority claim.** No survey established that nobody has done this; what
  is established is that the two papers and one preprint that define the paper
  type are simulations and reviews, and that an OSSE cannot measure
  identifiability because its sectors are separate by construction. The paper
  should say what distinguishes its version, not that it is first.
* **Not a validated result.** One year, one instrument, nine coincident TCCON
  days without prior alignment, and no accuracy assessment on any land-cover
  layer. The capability claim survives all three; a claim about the *size* of a
  land-cover effect would not.

**Reassessed on 14 September 2026, against what is now committed, and the
headline stands.** The statement was written before the attenuation bound
existed, when measurement error was queued as the one mechanism that could
manufacture the null rather than explain it. That mechanism is now excluded for
the impervious predictor with a measured margin: the error variance would have
to be 5.6 times the two products' disagreement to lift land cover to the spatial
null. **That strengthens the supporting null and does not change what is new**,
because the bound concerns the land-cover result and the contribution is the
pairing of the two observing-system limits. Adding it to the headline would
claim novelty for a standard errors-in-variables argument applied once.

Two amendments follow from it rather than to it.

* **The supporting null is now defended by measurement rather than by
  construction**, and the introduction and discussion should say so in one
  clause each. Before the bound, the answer to "could measurement error have
  produced this?" was four predictor pairs with different errors, which is
  evidence against the objection rather than a measurement of it. That is worth
  stating because it is the difference between a null a reviewer can doubt and
  one they have to argue with.
* **The third bullet's "no accuracy assessment" has a sharper form and the
  bullet is otherwise unchanged.** It is not an omission: no reference layer
  exists over this domain that is more accurate than the products it would
  assess, which four verified candidates establish. And the bullet's closing
  clause survives the bound intact — bounding how much attenuation *could* be
  present is not estimating the coefficient, so **a claim about the size of a
  land-cover effect still would not survive**, and the introduction must not
  imply otherwise.

#### Why capability and not reproduction

The reproduction framing is not wrong and it is not the headline. Its central
claim — no evidence that land cover explains the field — is a failed detection,
and a failed detection of a documented effect in a new region is what the
objection above says will not carry a paper on its own. **The capability framing
answers the objection with the same material**, because it reports what the
observing system can support rather than what one predictor pair failed to
explain, and "what can a 25 km column record over a mixed-source region
constrain" is a question nobody has answered against real observations.

The reproduction work becomes the supporting material, and it is *necessary*
supporting material rather than an appendix: the null is the evidence that the
information-content limit binds in practice and not only in arithmetic.

#### The three candidates, as previously recorded

Kept because the reasoning that produced them stands and only the choice changed.

**A reproduction paper.** Land cover does not explain the observed methane field
over the Yangtze River Delta at 0.25 degrees in 2018, established across two
urban products, two rice products, two cross-validation schemes and a published
bias-corrected field, with the diagnostic work as the contribution. **Writeable
now**, subject to the restatement below. *Now the supporting half of the chosen
framing rather than a framing of its own.*

**A methods paper on what a sparse column record can and cannot constrain at 25
km.** The same material framed as a capability statement rather than as a
negative finding about land cover. The methods grounding supplies most of what
this framing needs, including the transport-error ceiling of 12 ppb against a
between-cell spread of 14.9, and the degrees-of-freedom figures that say what
information the observing system carries. Writeable after the queue's first
tier. *This is the chosen framing, and the reviewer pass supplied the two things
it lacked: a named paper type in the field's own venues, and a second limit that
distinguishes it from an OSSE.*

**An emissions paper**, if a rice reimplementation or a GRPI-method inventory,
an improved prior and an inversion come together. Several rounds away, and the
IMI preview is the step that would say whether it is reachable at all.
*Unchanged, and still the one the IMI preview gates.*

#### What the framing changes in the remaining work

The queue below is not rewritten, because a capability paper needs most of the
same items. What changes is which items are **load-bearing** and which are
**strengthening**, and that distinction did not exist before.

**Load-bearing under this framing**, because they are the capability evidence:

* **The IMI preview run.** It converts the project's central number from a local
  reimplementation into the tool's own output, and it is free. Under a
  reproduction framing this was a nice-to-have; under a capability framing it is
  the single most valuable outstanding item in the whole queue.
* **The effective-degrees-of-freedom correction** (Tier 0, done). It is what
  makes the null a statement about information rather than about arithmetic:
  twenty-seven of seventy-two reported correlations lose significance once
  spatial dependence is accounted for.
* **The buffered leave-one-out decay curve** (Tier 0, done). It measures how
  predictive skill falls with distance from training data, which is the
  spatial-information claim in its most direct form.
* **Item 0c, the ten-percent rice-fraction test.** A null on the subset that
  satisfies the published condition for the association is a stronger
  information-content statement than a null on the whole field.

**Strengthening but no longer load-bearing**, because the claim is about what the
observing system can constrain rather than about a measured association's size:

* **The accuracy assessment** of the land-cover layers. It would bound the
  attenuation on an effect estimate. A capability claim does not rest on an
  effect estimate, so its absence is a stated limitation rather than a hole.
* **The TCCON validation.** Nine coincident days cannot validate a field; under
  the chosen framing they do not need to, because the field's uncertainty enters
  the capability calculation through the retrieval's own error budget, which
  `notes/grounding-methane.md` records.
* **The de-attenuation and equivalence-bound work.** Both are about the size of
  an effect. They become the route to a *second* paper rather than prerequisites
  for this one.

**Unmoved**: everything gated on new data — items 0e and 0f, the rice products,
the facility databases, the building-form layers. They serve whichever paper
comes next.

#### One thing the framing does not license

**The land-cover result still has to be reported in full.** It is what motivated
the assessment, and without it the paper is a methods note about an estimator
with no subject and no data. The negative finding stays — the same wording, the
same restatement constraint below, the same diagnostic work behind it. **It stops
being the headline and does not stop being a result.**

That is also the honest description of what happened intellectually: the
capability question was not the starting question. It is where the starting
question led, and a paper that hid the starting question would be
misrepresenting its own method.

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

## Tier 0 is done, and it reorders the rest

**Run on 12 September 2026.** All four Tier 0 items are complete and their
results are in `notes/decisions.md` under their queue numbers, with artefacts at
`data/processed/inversion_dofs_2018.csv`, `correlation_dof_2018.csv`,
`residual_range_2018.csv` and `buffered_loo_2018.csv`. The queue below is
annotated rather than rewritten: each item keeps its number so the records that
cite it stay valid.

**Item 1 changes the framing and it is the first of the three outcomes, not the
third.** The IMI preview could not be run — every route needs an account — but
its DOFS formula is closed-form and published, and evaluating it over this
lattice gives an expected DOFS of 3.98 to 22.21 over the 5 to 12 Tg a-1 band the
literature supports for this domain, against IMI's own marginal ceiling of 2.
**An emissions inversion here is feasible.** So the emissions framing is
reachable rather than several rounds away, and the Tier 3 items that would feed
a prior gain value.

Two qualifications hold it in place. No cell reaches a sensitivity above 0.5, so
the DOFS accumulates from many weakly constrained cells: an inversion could
constrain the region's total and could not attribute it cell by cell, which is
the question this project asked. And the median cell would need about 86 Gg a-1
for the observations to constrain it half independently of the prior, which is
larger than a large landfill.

**Item 2 changes what the paper may say about its own supporting analysis.**
Twenty-seven of seventy-two reported correlations lose significance, including
the one `data/processed/README.md` called negative and significant. The median
effective sample size is 45.5 of 926. The central negative result is untouched,
because held-out R squared against a spatial null is not a significance test.

**Items 3 and 4 partly undermine the cross-validation design and partly rescue
it.** The residual half-sill range of the impervious model is 96.1 km on the
operational field against a block 95 km across at its narrowest, and 134.5 km on
the blended field — so the blocks are marginal to too small for the one model
that carries the claim. But the decay curve shows the two cross-validation
schemes are two points on one curve, with leave-one-province-out matching a 150
to 200 km buffer, so neither is wrong and the bracketing reading is supported.

### What this reorders

**A new item, and it is now the highest-value one in the queue.** *Re-block the
spatial cross-validation at six cells and re-run the baseline suite.* Item 3
measured that four cells is too small for the impervious model on the blended
field by 40 percent, and the blended field is where the land-cover result is
weakest. Until that is re-run, the reported blocked figures overstate the
land-cover models' skill by an unknown amount on the field that matters most.
*Established by* item 3. *Cost:* low — the baselines run in minutes and need no
new data. **It goes above everything except the accuracy assessment.**

**Item 11, de-attenuation, gains a second reason and keeps its place.** Item 4
shows the impervious coefficient is not stable across the domain, so there are
now two reasons its small association might be understated or overstated:
measurement error attenuating it, and spatial non-stationarity meaning there is
no single coefficient to attenuate. The second is not a correction but a
limitation, and it belongs in the discussion beside the first.

**Item 18, equivalence bounds, moves up.** It was last because it needed the
de-attenuated effect size. Item 2 makes it more urgent instead: with
twenty-seven correlations no longer significant, the paper's supporting analysis
now says almost nothing either way, and "no evidence of an effect" is carrying
more weight than it used to. A named bound is what would convert that into a
statement.

**Tier 3 gains value from item 1 and keeps its cost.** A feasible inversion
needs a prior, the grounding records that a better rice prior demonstrably moves
an inversion's answer, and the five Tier 3 items still share one 28.9 GB pass.
The decision about that pass is now a decision about whether to pursue the
emissions framing, which is the right way round.

**Nothing moves down.** Item 1 is kept in the queue rather than marked done,
because what was run was the preview's arithmetic and not the preview, and one
free run by someone with an AWS account would still be worth having.

## The finding the three grounding records share

**Five independent instances of one pattern are now established and no file
stated it as a single finding.** It goes here rather than in a grounding record
because its consequence is a claim the paper may make, and this is the file that
governs those.

In every sector this project's domain contains, **the emission is determined by
something extent cannot see**:

* **Landfill methane** is determined by gas collection efficiency and the
  landfill-versus-incineration split, not by the area of the site. Measured
  collection efficiency averages 38 percent against a reported 70, and Los
  Angeles achieves 85 — a factor of two in emission at constant footprint.
  *Established by* [`notes/grounding-urban.md`](grounding-urban.md).
* **Gas distribution** is determined by pipeline age and material, not by the
  extent of the served area. Underground steel pipelines and aboveground risers
  are the leak-prone components, and leak density varies notably between cities.
  *Established by* the urban record.
* **Rice** is determined by water regime, not by area. Three water regimes on
  one soil under one crop span a factor of 13.7 in net global warming potential.
  *Established by* [`notes/grounding-yrd.md`](grounding-yrd.md).
* **Coal** is determined by gas content and seam depth, not by mine area.
  In-place gas content across one coalfield runs 8 to 16 m³ per tonne in Huaibei
  and 10 to 30 in Huainan. *Established by* the region record. *The "8 to 30"
  this entry carried until 14 September 2026 spanned the two mining areas'
  ranges as though they were one; the region record has them separately.*
* **Urban land** is determined by its residential-industrial composition, not by
  its paved area. A residential tower and a single-storey industrial shed have
  identical impervious footprints and different gas connections and waste
  generation. *Established by* the urban record.

Stated once: **extent is a proxy for the presence of a source and not for its
management, and in every sector here it is management that sets the emission
rate.** That is why a land-cover fraction can be an accurate map and still fail
to predict a methane field — the two are measuring different things, and the
failure is structural rather than a matter of map quality.

### The methodological consequence, with the qualification Tier 0 supplies

**The inversion route is appropriate for a reason that follows directly from
that finding.** An inversion estimates emission from the atmosphere and uses
extent only to place the prior. It never asks extent to predict emission; it
asks the observations what the emission was and uses extent to say where to look.
So the structural failure above is not a failure of the inversion route, which
is the method the field uses and which
[`notes/grounding-methods.md`](grounding-methods.md) records this project did
not take.

And [`notes/decisions.md`](decisions.md) now records that an inversion over this
domain is **feasible**. Expected degrees of freedom for signal run **3.98 to
22.21** over the 5 to 12 Tg a⁻¹ band the literature supports for this domain,
crossing IMI's minimum viability of 1 at about 3 Tg a⁻¹ and its marginal ceiling
of 2 at about 5, and that range is a **lower bound** because the sweep spreads
emissions uniformly while real concentration raises the sum. Those figures come
from a reimplementation of the Integrated Methane Inversion's own closed-form
DOFS estimate rather than from a preview run, which the script, the recipe note
and the record all state.

**But the qualification is the part that matters, and without it this
overclaims.** No cell in the swept range reaches a sensitivity above 0.5. The
DOFS accumulates from 926 cells each weakly constrained, which is what a
domain-total inversion needs and not what a per-cell attribution needs. **An
inversion here could constrain the region's total emission. It could not
attribute that total to land cover cell by cell.**

### What that means for the 2023 thesis's question

This is the sharpest statement this project can make and it should be stated
carefully.

The thesis asked **where methane comes from within this region, at cell
resolution, from land cover.** The field's own best method — analytical Bayesian
inversion with closed-form error characterisation, applied to the best available
observations for this domain — **can constrain the regional total and cannot
constrain the cell-level attribution.**

So the question is not answerable at the resolution it was asked, by any method
currently available for this domain. **That is a capability finding about the
observing system, not a limitation of the thesis's approach.** The thesis chose a
method that could not answer its question; the finding here is that no method
could, which is a different and more useful thing to report. It converts an
apparent methodological error into a statement about what a 25 km column record
over a 750-by-900 km domain can and cannot support — and that statement is
publishable in its own right, which is the second of the three framings this
file records.

Two boundaries on it, so it is not read as more than it is. It is a statement
about *this* domain, *this* instrument and *these* years, and the degrees of
freedom scale with observation density, so a longer record or a denser instrument
would move it. And the estimate is IMI's approximation evaluated locally rather
than an inversion actually run, so the number that would settle it is still one
free preview run by someone with an account.

## The cross-layer synthesis, added 14 September 2026

**This section exists because nothing held it, and it only became writable once
all four grounding records existed.** It goes here rather than in a fifth
grounding file for a structural reason worth stating: each grounding record is
about one thing — a region, a predictor, a predictor, a target — and this is
about the relation between them. A file named after a layer would be the wrong
container. And its conclusions are claims a paper may make, which is what this
file governs.

It is the strongest methodological statement this project can make, and it is
stronger than the capability finding above rather than a restatement of it.

### The field says the thing, in one sentence, and has said it since 2018

"**Inversion modelling is not capable of distinguishing interspersed sources from
different sectors. Overlapping grid level sources from different sectors are
typically grouped and treated as a single source**" (Desjardins, R. L.,
Worth, D. E., Pattey, E., VanderZaag, A., Srinivasan, R., Mauder, M.,
Worthy, D., Sweeney, C., and Metzger, S., 2018, *The challenge of reconciling
bottom-up agricultural methane emissions inventories with top-down measurements*,
*Agricultural and Forest Meteorology* 248, 48–59,
doi:10.1016/j.agrformet.2017.09.003).

Read that against what this project's domain contains. **It is an
interspersed-source region in every direction at once:**

* Rice and **aquaculture** occupy the same flooded lowland — same cells, same
  spectral signature, and the second unrepresented in every inventory.
  *Established by* [`notes/grounding-rice.md`](grounding-rice.md).
* Rice and **natural wetland** overlap in the priors by the wetland product's own
  admission, and a third or more of paddy emission may not be anthropogenic at
  all. *Established by* the rice record and
  [`notes/grounding-methane.md`](grounding-methane.md).
* Urban **waste, gas distribution, wastewater and stationary combustion** are
  four sectors sharing one allocation surface inside the same city cells.
  *Established by* [`notes/grounding-urban.md`](grounding-urban.md).
* **Coal** sits in northern Anhui, immediately adjacent to — and partly inside —
  the cells where the committed rice raster stops classifying. *Established by*
  [`notes/grounding-yrd.md`](grounding-yrd.md).

**So the method the field uses would group this project's two predictors' sources
together**, and the 2023 thesis's question was to tell them apart. That is not a
statement about the thesis's technique. It is a statement about the question.

### What separability actually depends on, which is not the observations

The decisive mechanism is already in the urban record and its generality was
not drawn out. Landfills are separable in a US inversion because they are mapped
on facility coordinates and are spatially distinct from everything else, giving
posterior error correlations below 0.35 with other sectors. Gas distribution,
wastewater treatment and stationary combustion are all allocated on population,
and correlate with one another at 0.45 to 0.87, so "our ability to separate these
three sectors in the inversion is therefore limited, and their relative
allocation is heavily weighted by the prior information".

**Stated generally: separability is a property of the prior's spatial
distinctness, not of the observations.** The same instrument, the same inversion
and the same domain separate one sector and fail to separate three, and the only
thing that differs is how each sector's prior was spatially allocated.

Two consequences follow, and they point in opposite directions for this
project's two predictors.

**It explains why an impervious fraction cannot help, conclusively rather than
suggestively.** A fraction is a smooth, population-like surface. Adding it to a
set of sectors already allocated on a smooth population-like surface adds
correlated information; it does not add distinctness. The urban record reached
that conclusion from one inversion's correlation coefficients; the general
principle is why it could not have come out otherwise.

**And it tells you what would work, which is the constructive half.** For the
urban sectors: facility coordinates, which
[`notes/dataset-leads.md`](dataset-leads.md) now carries leads for. For rice: a
genuinely distinct spatial distribution — which is exactly what a better rice map
provides, and exactly the gain the rice record establishes is real. **So the two
halves of this project's predictor set are not symmetric.** The rice layer
addresses the mechanism that governs separability; the impervious layer cannot.
That asymmetry is the most defensible thing a paper can say about why one half of
the predictor set has a future and the other has a narrower one.

### Isotopes, the fallback when sources overlap, and why they do not help here

When sources are interspersed, the field's answer is to separate them by
composition rather than by location. That works, and it does not work for this
project's particular comparison.

**The signatures overlap where this project needs them separated.** Biogenic
methane sources sit "in the −70 to −50‰ range for sources such as ruminants,
wetlands and rice fields", against thermogenic and pyrogenic sources "as
enriched as −15‰", and pooled literature gives "an average signature of
approximately **−61 ± 4‰** for all rice fields" (France, J. L., Fisher, R. E.,
Lowry, D., Allen, G., and twenty others, 2022, *δ13C methane source signatures
from tropical wetland and rice field emissions*, *Philosophical Transactions of
the Royal Society A* 380, doi:10.1098/rsta.2020.0449). Waste sources measured
atmospherically give a weighted average of **−56.1 ± 2.4‰** (Bakkaloglu, S.,
Lowry, D., Fisher, R. E., Menoud, M., Lanoisellé, M., Chen, H., Röckmann, T., and
Nisbet, E. G., 2022, *Atmospheric Environment* 276, 119021,
doi:10.1016/j.atmosenv.2022.119021).

**Rice at −61 ± 4 and waste at −56.1 ± 2.4 overlap within one standard
deviation.** Both sit inside the biogenic window. The mechanism is that both are
microbial: methane from wetlands, rice paddies, waste and enteric fermentation
shares the methanogenic pathway and is therefore all depleted in 13C, while
fossil methane is enriched. **So isotopes separate microbial from thermogenic,
not rice from landfill.**

For this domain that means something specific and usable. Isotopes would
separate **rice and waste together** from **coal and gas together** — which is
precisely the discrimination the northern Anhui coal question needs, and
precisely not the discrimination the 2023 thesis's comparison needs. The fallback
works for the confound the region record found and fails for the comparison the
thesis made.

**And the data gap lands on exactly the two sectors this project would need.**
NOAA's global δ13C source signature inventory carries spatially resolved
signatures for oil and natural gas, coal, biomass and biofuel burning, ruminants
and wild animals, with geological seeps and wetlands supplied from other work.
"For other CH4 sources, the current measurement sample sizes are insufficient to
develop spatial distributions", and globally averaged values are used instead —
the sources named being **waste and landfills, termites, and rice** (Sherwood,
O. A., Schwietzke, S., and Lan, X., 2020, `10.15138/qn55-e011`, documented in
Lan, X., Basu, S., Schwietzke, S., and fourteen others, 2021, *Global
Biogeochemical Cycles* 35, doi:10.1029/2021GB007000). **The two sectors this
project compares are the two without spatially resolved isotopic signatures.**
That is not a coincidence worth dwelling on, but it is a precise statement of
where the field's knowledge stops relative to this question.

**Then record the opening, because it is a genuine and dated research gap.** A
2026 South Asian campaign found regional signatures departing substantially from
global means: rice paddy methane "more enriched in δ13C compared to the global
mean", with Miller–Tans values of **−53.8 ± 0.8‰** in δ13C and **−311 ± 6‰** in
δ2H, the enrichment in both suggesting "multiple sources and/or pre-emission
oxidation"; and the conclusion that "**region-specific isotopic endmembers are
therefore critical for accurate source apportionment**" (Yao, P., Belec, K.,
Holmstrand, H., and thirteen others, 2026, *Atmospheric Chemistry and Physics*
26, 7765–7787, doi:10.5194/acp-26-7765-2026). A rice signature at −53.8 is
*enriched past* the waste average of −56.1 — **so a regional dual-isotope
campaign can separate what global means cannot**, and the equivalent campaign for
China has not been done. That is a concrete, fundable next study rather than a
lament, and this project's domain is where it would be worth doing.

### The shared mechanism, now seven instances

The five-instance finding above becomes seven with the second rice block, and
the two additions are the largest ratios in the set:

* **Aquaculture** is determined by pond management, not by pond area. Greenhouse
  gas emission intensity per unit of fish production runs **197 times higher** in
  traditional earthen ponds than in in-pond raceway systems. *Established by* the
  rice record's second block.
* **Rice straw** is determined by whether residue is incorporated or burned, not
  by the area it was grown on. Four years of autumn incorporation gave a
  **five-fold** increase in growing-season CH4 — with no effect on yield, so
  nothing in an agricultural statistic records it. *Established by* the rice
  record's second block.

**Seven sectors, seven times, the same structure.** And the two new instances
sharpen the general claim in a way the first five did not, because both are
*within-class* ratios: the same pond, the same paddy, the same area, a different
practice. A factor of 197 between two ways of farming the same water is not a
proxy problem that better mapping could reduce.

### The shared timing, which nothing recorded

All three layers change under policy during this project's study interval, and
the three years bracket three separate step changes. Nothing in the repository
put them in one place.

* **2008: the residue-burning ban**, with straw return becoming the standard
  alternative and a measured five-fold effect on growing-season rice emissions
  in the direction of more. *Held by* the rice record's second block.
* **2010 to 2019: urban gas distribution tripling**, "from 298.6 to 935.6 million
  meters" of urban supply pipeline, with leakage "not actively monitored". *Held
  by* the urban record.
* **2018: the waste policy pivot**, with greenhouse gas emissions from the sector
  peaking that year and an **84.7 percent** reduction in municipal solid waste
  methane in Chinese cities since 2017. *Held by* the urban record.

**The three years 2000, 2010 and 2018 therefore sample three different policy
regimes, and not one of the three step changes is visible in a land-cover
fraction.** 2018 is simultaneously the peak of the waste arc, nine years into a
rising straw-return effect, and the end of a decade of tripling gas
infrastructure. A monotonic impervious series and a declining rice series are
being asked to track three non-monotonic, policy-driven emission series, two of
which turn inside or just after the study window.

That is a discussion point rather than a result, and it is the one that most
directly limits what a cross-sectional 2018 analysis can be said to represent.

### What the synthesis establishes for the paper

**The three layers are not three separable predictors of one field.** They are
overlapping sources that the field's own best method groups together and treats
as one. That has been stated in the literature since 2018 and it describes this
domain exactly: rice with aquaculture and wetland, four urban sectors with one
another, coal with the cells where the rice classification stops.

**Attribution depends on the prior's spatial distinctness, not on the
observations.** The same inversion separates landfills, because they are mapped
on coordinates, and fails to separate three population-allocated sectors from one
another. That is why an impervious fraction cannot help — it is another smooth
surface joining a degeneracy — and why a better rice map can, because it supplies
the distinctness the mechanism requires.

**And the two sectors the 2023 thesis compared are the two for which no spatially
resolved isotopic signatures exist**, so the field's standard fallback for
overlapping sources is unavailable for exactly this comparison. It would work for
the coal question the region record raised, and a regional dual-isotope campaign
for China — which has not been done — would be the study that changed that.

**Read together with the capability finding above, this is the paper's
methodological core.** An inversion over this domain could constrain the regional
total and not the cell-level attribution; and even a perfect cell-level
attribution would be attributing to sectors the method groups together. **The
first is a statement about information content and the second about
identifiability, and they are independent.** Either alone would be enough to say
the thesis's question is not answerable as asked. Both together say why no
refinement of the same design would fix it, which is the more useful and the more
defensible claim.

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

**1. The IMI preview.** ✅ *Answered 12 September 2026 by reimplementing its
formula; the run itself is still worth having.* Establishes whether TROPOMI can constrain methane
emissions over these four provinces, by reporting the expected degrees of
freedom for signal over a user-selected domain. The tool runs at this project's
exact resolution and already ingests the blended field committed here, and its
own documentation says the preview "has no significant costs". *Established by*
[`notes/grounding-methods.md`](grounding-methods.md) and
[`notes/dataset-leads.md`](dataset-leads.md). *Gates* the emissions framing
entirely, and gates whether the paper may say the conversion is infeasible — the
thing a paper cannot leave as future work.

**2. Effective degrees of freedom on every reported correlation.** ✅ *Done 12
September 2026; 27 of 72 correlations lose significance.* Every Pearson
and partial correlation here is computed over 926<!--#composite.covered_cells--> cells with n treated as 926
while both fields are strongly autocorrelated, so every p-value is
anti-conservative. One function over the committed covariate table. *Established
by* the methods record. *Gates* every stated p-value, including the blended
field's partial correlation of −0.082 at p 0.013 that the repository currently
reads as over-control.

**3. The residual autocorrelation range.** ✅ *Done 12 September 2026; 96.1 km
on the operational field and 134.5 km on the blended, against a 95 km block.*
The block size has never been
justified from the data; the defensible choice is the autocorrelation range of
the model's residuals, and what exists is Moran's I of the residual field, a
different quantity. *Established by* the methods record. *Gates* item 4 and any
defence of the spatial-blocks design.

**4. A buffered leave-one-out decay curve.** ✅ *Done 12 September 2026; the
bracketing reading is supported.* Predictive power against increasing
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

**9. The accuracy assessment — BLOCKED, no reference layer exists.** Mean deviation, mean absolute deviation and
regression of the mapped fraction against a reference fraction built from the
polygons, which is the correct frame for a continuous field rather than an error
matrix. Prediction-powered inference is the route that makes a small reference
set usable. *Established by* the methods record. *Gated by* item 5, and by one
condition that must not be forgotten: the calibration set "must be separate from
the training dataset used to train the machine learning model", so **the
polygons are clean for the NESDC and GISA layers**.

**Unblocked and re-scoped on 13 September 2026**, when the deposit was opened
and read. The polygons are fetched, verified against their published MD5, and
their shape is committed as `data/processed/ccdrice_polygons_yrd_2026.csv`, so
this item no longer waits on a download. Three things it did not know:

* **777 polygons reach only 62 of the 926 cells**, Shanghai's 338 falling in
  six. Any per-cell assessment rests on 6.7 percent of the lattice, and a
  domain-wide claim from it is a claim about those 62 cells.
* **50 Jiangsu polygons sit north of 33.3462 N**, where the committed NESDC
  raster stops, leaving 727 usable against the rice layer this project carries.
* **The sample is purposive, not probabilistic.** The paper selected "only 2 to
  4 years in each provincial administrative region" because Google Earth's
  historical Chinese coverage is sparse and "early images tend to be for urban
  areas rather than for rural areas". So there are no inclusion probabilities,
  and **the design-based PPI extension this item was going to rely on needs
  sampling probabilities that do not exist.** Neither canonical i.i.d. PPI nor
  its unequal-probability extension applies as written; what is available is a
  clustered sample with unknown selection, and saying so is the honest form of
  this item rather than a reason to drop it.

**The route is settled and the item is blocked on an input, not on a method**,
as of 13 September 2026. `notes/grounding-methods.md` records the reasoning.
PPI is not the route; the route is the continuous-field, complete-coverage
comparison that record already contained — mean deviation, mean absolute
deviation and regression at a stated aggregation scale, after Riemann et al.
(2010) and Wickham et al. (2020) — which has **no sampling design to be valid
about** and so does not need recommendation 1 at all. What it needs is a
reference layer over the domain more accurate than the product, and neither
route to one is currently open:

* **Route A**, a certainty stratum of the 62 cells the polygons reach plus a
  probability sample of the remaining 864, is blocked on the very-high-resolution
  imagery terms question this repository already records as unresolved, and
  carries a response-design burden larger than the categorical literature's
  because the target is a fraction per cell rather than a label.
* **Route B**, a finer and more accurate reference product over the whole
  domain, is blocked on **year**. Every candidate is 2020 or later against
  layers for 2000, 2010 and 2018, in a region whose urban extent changed
  substantially over exactly that span.

**No deposited sample set rescues it either, and this is now measured.** Of the
three verified, LCMAP is a probability sample and US-only; the global land cover
validation samples are a stratified allocation over a non-probability frame and
put **124 points in the four provinces across 20 of 926 cells, of which 12 are
impervious surface**; and Globe230k is a deliberately disproportionate sample
covering about 0.59 annotated tiles per cell. See `notes/dataset-leads.md`.

**Both of the unblocking moves this item listed have now been tried and neither
works**, as of 13 September 2026. They are recorded here because a later pass
would otherwise attempt them again.

**Adding a 2020-or-later analysis year does not unblock Route B.** This item
recorded the year as the constraint. Opening the four candidate products
established that **none of them is more accurate than the products it would
validate** — SinoLC-1 at 73.61 percent overall, EcoVision at 83.6 percent,
ISA-1's impervious class at F1 75.53 with recall 61.76, and CISC at above 0.93
impervious F1 but at 30 m and so not finer — against GISA's impervious F-score
of 0.954. A perfectly year-matched candidate would still fail Olofsson's second
recommendation, so **the year was never the binding constraint** and a scope
change to a second year would not buy the assessment. See
`notes/dataset-leads.md`.

**Reading Google's terms does not open Route A at fine resolution either.** The
Geo Guidelines permit "research, education, film and nonprofit use without
needing permission" and separately prohibit using Google Earth output "to create
other content, products, or services", and do not say which governs a visually
interpreted reference dataset. Earth Engine's terms *are* clear and permissive —
§2.1(d) allows publishing derived data in research publications — but Earth
Engine does not serve the very-high-resolution basemap this literature
interprets. **Sentinel-2 is the finest imagery whose terms unambiguously permit
publishing a derived dataset**, under Regulation (EU) 1159/2013, at 10 m against
30 m products: a ratio of three where the NLCD model used thirty. See
`notes/grounding-methods.md`.

**So the state of the item is: Route B closed on accuracy, Route A open but
thin.** A Sentinel-2 response design is licensable and defensible; whether a
three-to-one resolution ratio supports a credible fractional reference is the
open question, and it is a methodological one rather than a data-availability
one. That is a change in the kind of obstacle, and it is progress.

**And the contamination clause above was wrong about the mechanism.** CCD-Rice's
thresholds were re-determined against filtered agricultural statistics, not
against the polygons, so the polygons are clean for CCD-Rice too. What is not
independent is CCD-Rice and NESDC: CCD-Rice's training labels were taken from
`10.57760/sciencedb.06963`, which is this project's own rice layer. See
`notes/decisions.md`. That bears on item 10's rice analogue and on item 11, not
on this item.

**10. Quantity and allocation disagreement between GAIA and GISA — DONE, 13
September 2026.** `data/processed/urban_disagreement_2018.csv`. Allocation is
about half the disagreement at the lattice scale in every year, and the
crossover this repository had recorded turns out to be a shift in the *quantity*
component sitting on top of a persistent disagreement about location. The
original statement of the item follows.

**10. Quantity and allocation disagreement between GAIA and GISA.** The
repository reports their difference as a single percentage of provincial area,
which is quantity disagreement alone and says nothing about whether the two put
impervious surface in the same places. Only allocation disagreement attenuates a
coefficient. *Established by* the methods record's reliability section. *Needs*
only the two committed products.

**10a. The paddy-pond confound, and it is blocked on one paywalled article.**
Overlaying a mapped aquaculture-pond layer on the committed rice fraction would
measure the overlap per cell for 2018, which is the largest single omission the
rice record identifies. **This item cannot start.** Both candidate products,
China_AP and the aquaculture-index mapping, name no deposit, and both articles
are unreadable from this network — ScienceDirect and Wiley return 403 to every
route tried, and neither registers a dataset relation in Crossref. China_AP's
article is gold open access under CC BY 4.0, so the obstacle is a publisher
block rather than a licence. *Needs* one email to a corresponding author, or
institutional access to one PDF. It is recorded as a queue item rather than
left as a dataset lead because the computation is already specified and only
the input is missing: `src.landcover` reduces a 10 m raster to a per-cell
fraction on this lattice, which is exactly the operation a pond layer needs.

**11. De-attenuation — DONE for the impervious layer, 13 September 2026, and
the null survives.** `data/processed/attenuation_bound_2018.csv`. The maximum
de-attenuation factor is 1.15, which lifts the best impervious held-out R² from
+0.085 to +0.098 against the spatial null's +0.332. **Reaching the null would
need 5.6 times the error variance the two products' disagreement supports.** The
rice half is structurally unbounded: no second rice product independent of NESDC
exists. The original statement of the item follows, with the correction it
needed.

**11. De-attenuation.** Regression calibration, or SIMEX-WLS where non-constant
residual variance matters — and it does, since a cell mean rests on between
1<!--#composite.min_soundings--> and 410<!--#composite.max_soundings--> soundings. **This is the most consequential item in the queue**, because
measurement error in a predictor is the only mechanism that could manufacture
this project's null, and building second predictors with different errors is
evidence against that rather than a measurement of it. *Established by* the
methods record. *Gated by* items 9 and 10, which supply the error variances: the
polygons for rice, the allocation disagreement for impervious surface as a lower
bound.

**Neither input comes from the accuracy assessment, and one is weaker than
recorded.** Found 13 September 2026. Item 9 is blocked, but **this item was
never gated on it for the urban half**: its impervious input was always item
10's allocation disagreement, which needs only the two committed products and is
unaffected. What the blocking does change is what that input can be. Allocation
disagreement is a **lower bound** on the pair's error variance — where GAIA and
GISA differ at least one is wrong, where they agree nothing is constrained — so
**de-attenuation here can produce a bound on the de-attenuated coefficient and
not a point estimate.** That is a weaker claim than this item was written for and
it is still the claim that matters, because a lower bound on the error variance
gives an upper bound on attenuation, and an upper bound on attenuation is
exactly what is needed to ask whether measurement error could manufacture the
null. **If the bound does not reach the observed coefficient, the null survives
the objection.**

For the rice half the polygons remain available and are not affected by item 9's
blocking: the assessment is blocked for want of a reference *layer*, and the
CCD-Rice polygons are reference *points*, still usable over the 62 cells they
reach, with the purposive-sample caveat that they carry no inclusion
probabilities and so support an estimate without a design-based interval.

**So item 11 is not blocked. It is reduced from estimation to bounding**, and its
gate is item 10 alone.

**And the direction of the bound recorded above was wrong, which computing it
exposed.** This passage said allocation disagreement gives a *lower* bound on
the error variance and therefore an upper bound on the de-attenuated
coefficient. Those do not follow from each other: a lower bound on the error
variance bounds the reliability ratio from above and the de-attenuated
coefficient from *below*. The usable bound comes from treating GISA as a second
*measurement* rather than a second reference — `Var(D) >= Var(e_GAIA)` under
independence — which bounds reliability from below and the coefficient from
above, as the question requires. See `notes/grounding-methods.md` and
`notes/decisions.md`.
The rice error variance was to come from a CCD-Rice-against-NESDC comparison in
the role GAIA and GISA play for impervious surface. GAIA and GISA were produced
independently; **CCD-Rice was trained on NESDC**, so their disagreement
understates the disagreement and an error variance from it understates the
error variance — biasing de-attenuation toward the null this item exists to
test. The rice error variance should come from the polygons, which are
independent of both, and the 62-cell reach recorded under item 9 is therefore a
constraint on this item too.

### The second-year question, a decision awaiting a choice

It was queued as a possible scope change: add a 2020-or-later analysis year so
that a year-matched finer product could serve as reference. **The measurements
that decision was waiting on were taken on 13 September 2026 and they settle it
in the negative for that purpose.** No candidate product at any year clears the
accuracy bar, so a second year does not deliver the assessment. **Item 9 is
therefore blocked rather than pending**, and the assessment-only option below is
eliminated outright.

**The question survives on a justification independent of the assessment, and
that justification is the stronger of the two it now has.**

* **A two-year capability estimate bears on the paper's central claim.**
  `figures/capability.png` reports expected DOFS for 2018 alone, and the whole
  capability argument is about what a column record can constrain. **That answer
  is a function of observation density, which is not constant across years** —
  the 2018 record is an eight-month record beginning 30 April, and a full year
  would carry more observation days per cell, which is the exact input the
  sensitivity expression takes. Computing it for a second year would show
  whether the conclusion is a property of the instrument over this domain or a
  property of 2018's coverage. **That is a claim about the contribution, not an
  error bar on it**, and it is the reason to take Option 3 if any reason is.
* **It answers the single-year objection this file already anticipates**, which
  is the weaker reason because it is defensive. A reviewer's standing complaint
  about a one-year association is that the year might be atypical; running the
  analysis in a second year and reporting whether the null holds in both answers
  it with evidence rather than argument, and depends on no reference product.

**The order matters.** The capability comparison is a positive result the paper
would not otherwise have; the replicated null is an answer to an objection.
Raised under the assessment, this question was about error bars. It survives as
a question about the contribution.

**What a second year costs in this repository**, so the trade is visible:

* **The composite is the dominant cost.** `config/recipes.yml` records the 2018
  checkpoint as "28.9 GB and about two hours to build", network-tier and
  on-demand. A second year is another 28.9 GB transfer and another two hours,
  plus a second `data/interim/extent_YYYY.npz`.
* **Impervious layers exist for the new year.** GISA runs to 2019 and GISA-new
  to 2021; CISC covers 2020 and 2022 at 30 m. So the urban half is servable.
* **The rice layer would be weaker in the new year than in 2018, and this is
  the constraint that bites.** NESDC covers 2017 to 2025, but
  `notes/decisions.md` records that **Shanghai's single-season total is pinned
  across 2019 to 2025** — stable to 0.03 percent while 8.6 million pixels
  changed class, Jaccard 0.3577 — and **Jiangsu's shows the same signature from
  2020 onward**. In 2018 Shanghai is outside the pinned window and Jiangsu's
  2018-to-2020 transitions move freely. **So a 2021 year would have both
  Shanghai and Jiangsu pinned where 2018 has neither**, and the rice half of a
  second year would rest on a weaker layer than the year it was meant to
  corroborate.
* **What would have to be redrawn or amended**: the composite figure, the
  observed-predicted and residual-field figures, the capability figure, every
  baseline suite artefact, and the results draft's §1 to §3. The figure module's
  recipes are byte-compared, so each would regenerate rather than need
  rewriting.

### The decision, in the form a decision needs

**This is a choice awaiting a decision, not a task awaiting execution**, and it
is recorded here in that form because the measurements it was waiting on are in.

**Option 1 — no second year.** Costs nothing. The single-year objection is
answered in prose: the year is defended as representative by argument rather
than by evidence. Buys nothing. **This is the status quo and it is defensible**,
because the paper's claim is about what a column record can constrain over one
year and it does not assert that 2018 is typical.

**Option 2 — an assessment-only year.** Composite a later year, assess its
land-cover layers against a reference, apply the resulting error estimate to the
2018 layers on the stated assumption that product accuracy is stable across
years. **This option is eliminated by the 13 September 2026 measurements**, and
its elimination is a real simplification rather than a loss: no reference layer
exists over this domain at any year, so there is nothing to assess the later
year against. It was the only option whose value depended on the accuracy
assessment, and it is gone.

**Option 3 — a full second analysis year, justified by capability.** Run
everything twice and test the null in both.

*Costs*, all of them already measured: **28.9 GB and about two hours** to build
a second composite checkpoint, on the network tier; a second
`data/interim/extent_YYYY.npz`; and a regeneration of the composite,
observed-predicted, residual-field and capability figures, every baseline suite
artefact, and results §1 to §3. **The redraw is recipe-driven and byte-compared,
so it regenerates rather than needing rewriting** — the cost is machine time,
not authorship.

*Buys*: a two-year capability estimate and a replicated null. See below for why
the first is the stronger reason.

*And it carries one cost that cuts against it, recorded here rather than
discovered later.* **The rice half of a second year would be weaker than the
first.** NESDC covers 2017 to 2025, but `notes/decisions.md` records that
**Shanghai's single-season total is pinned across 2019 to 2025** — stable to
0.03 percent while 8.6 million pixels changed class, Jaccard 0.3577 — and
**Jiangsu's shows the same signature from 2020 onward**. In 2018 Shanghai sits
outside the pinned window and Jiangsu's 2018-to-2020 transitions move freely.
**So a 2021 or 2022 year would have both Shanghai and Jiangsu pinned where 2018
has neither.** A replicated null would be replicated on a weaker rice layer, and
a reader entitled to ask whether the replication tested the analysis or the
product would be right to ask.

**What makes the options different** is not cost but what they are evidence
about. Option 1 asserts representativeness; Option 3 measures it. Option 2
measured something that cannot be measured.

### Which year, if Option 3 is taken

**Undetermined, and what would determine it is which property matters more.**

* **2021** aligns with GISA-new, the only impervious product reaching that year,
  and with SinoLC-1's and ISA-1's reference year — which matters not at all for
  the assessment, since neither can serve as reference, but would matter if
  EcoVision's full text or CISC's validation points later changed that.
* **2022** aligns with CISC, which covers 2020 and 2022 at 30 m and is the
  strongest-accuracy impervious product found anywhere in this work at F1 above
  0.93, and it carries more TROPOMI record, so its capability estimate rests on
  more observation days — which is the whole point of the comparison.

**On the capability argument alone, 2022 is the better year**, because the
capability estimate is a function of observation density and a later year has
more of it, and because CISC gives the impervious layer its best available
product for that year. On rice, both years are pinned in two provinces and
neither is better. **No decision is taken here.**

**12a. Commit the fitted seasonal cycle's parameters.** The column field's
fitted seasonal peak at day of year 245.8 appears in `notes/decisions.md` and
`notes/grounding-rice.md` as prose and in no committed artefact, so it cannot
carry a resolver. It is load-bearing in the discussion — it is what makes
EDGAR's uniform June peak roughly ten weeks early over this domain — and it is
the only number in that section that could not be marked.
`deseasonalisation_2018.csv` holds the correlation table and not the cycle's
amplitude, phase or peak. *Needs* only a row or two added to an existing script,
since the cycle is already fitted in order to remove it. **Found by drafting the
discussion, 14 September 2026.**

**12b. The three sections that do not exist.** Four narrative sections are
drafted and `paper-target.md` names five; the conclusion is missing, so nothing
states what the paper establishes in its own voice at the end. **And two
apparatus sections exist nowhere.** No abstract — the section a reviewer reads
first, and the one this file's own publication-bias material identifies as where
null results get filtered. No data availability statement, which the target
venue requires and which this repository could write almost mechanically from
74<!--#pipeline.recipes--> registered recipes, a byte-comparison runner and
per-artefact provenance. **And the reference audit has now established the list
it should be written from**: fifteen dataset and deposit entries in the
register, none of them cited in any draft, which is correct — a dataset belongs
in that statement and not in a reference list. `notes/reference-audit.md` §3
names all fifteen. *Needs* no new analysis. **Found by looking at the drafts as
a set, 14 September 2026.**

**12d. The claim audit's fix lists, batch 1 of three.** `notes/claim-audit.md`
and `data/processed/claim_inventory_2026.csv`. Three blocks of work, in cost
order. **38 `unresolved` numbers** sit in a committed artefact with no marker;
each needs one comment, and clearing them before the captions are rewritten is
cheaper than deciding each number twice. **102 unsupported numbers in the figure
captions**, which is the largest single block the audit found and which exists
because the captions were never in an audit's scope. And **197 unsupported
numbers overall**, of which the captions are half and the methods a third.
*Needs* no new analysis. **The introduction needs none of this: it has zero.**

**12e. Four claims where a citation should become a measurement.** The
interspersed-source claim, which rests on a US inversion and is now measured
locally. Results §1's statement that no representativeness estimate was computed
for this composite, which is false since Tier 3 — the median within-cell spread
is 18.94 ppb against a between-cell 14.86. The Arabian Peninsula analogue, which
this work's own 14.21 ppb RMSE makes locally. And the cited 26 percent
aquaculture share, against a measured 35.6 percent of national pond area inside
the four provinces. *Established by* the claim audit.

**12f. One sentence to qualify.** The introduction's "all present and
interleaved" is true of presence and false of interleaving for the largest
sector: coal holds 39.59<!--#sector.coal_share--> percent of the domain's
inventoried emissions in 22<!--#sector.coal_cells--> cells and shares
1<!--#sector.rice_coal_pair--> cell with rice. The correction sharpens the
identifiability argument rather than weakening it, since coal is then the one
sector distinct enough to be attributable and also the one neither predictor
represents.

**12c. Citations. The four drafts contain twelve between them.** Ten are in the
methods; the introduction cites nothing at all, and no draft carries a DOI or a
reference section. Against a register of
199<!--#register.entries--> entries and an ACP article's typical forty to
eighty, **the paper's reference count as drafted is twelve.** This is the
largest writing gap in the queue and it is not mechanical: the drafts state
literature findings in prose and attribute them to nobody, so those sentences
read as this project's own claims. `notes/reference-audit.md` §2 lists the
uncited claims by draft. **Found 14 September 2026 by reading the register as a
reference list rather than as a log.**

*Two properties make it worse than it sounds.* Every guard this repository has
checks its own assertions against its own evidence, so **an uncited external
claim is invisible to all of them** — there is no artefact to compare it with
and no target file to find it in. And the drafts cite the statistical method
more thoroughly than either the region or the capability literature the framing
claims membership in: the register's *Capability assessment as a paper type*
section holds three entries and none is cited anywhere in the drafts.

### Tier 3 — one re-gridding pass over the granules, shared by five items

**These five share a single 28.9 GB transfer and should be done together or not
at all.** That is the whole reason for grouping them: each alone would cost the
same as all five.

**DONE. The pass ran and all five were collected together**, 578 granules and
28.9 GB in 53 minutes. `notes/decisions.md` records it and three artefacts hold
the results: `granule_quality_2018.csv`, `cell_quality_2018.csv` and
`preprocessing_sensitivity_2018.csv`. The committed composite reproduces
byte-identically, so nothing downstream of it moves.

**What the pass reordered, which is more than it settled.**

* **Item 14 was never a gate.** Within-cell variance was already recoverable
  from the seasonal accumulator's `hs::sum_yy`, so **item 17 — representativeness
  weighting, the widest-reaching item in the queue — was unblocked before this
  pass began** and had been for as long as the harmonic statistics existed.
  It is now not merely unblocked but tested, and the result is item 17's
  answer rather than its precondition.
* **Item 16 changes character.** Destriping was queued as an implementation
  task on the grounds that the omission was unrecoverable. It is recoverable:
  the across-track column was retained at no extra variable read, and a
  first-order correction is already measured. What remains is a per-orbit
  correction on de-meaned residuals, which is a smaller and better-specified
  job than "implement destriping".
* **Item 12 is closed rather than done.** The precision filter removes nothing:
  no sounding passing quality control has a precision above 10 ppb. There is no
  filter to apply and no decision to make.
* **Item 15 is unblocked, not answered.** Monthly partial sums were accumulated
  rather than a two-way growing/fallow split, because the record reframed the
  question — the fallow season may carry most of a paddy's annual emission — and
  monthly contains every two-way split while leaving the cut date to be chosen
  after the fact. Forming and interpreting the seasonal contrast is still to do.

**One item was added to the pass that was not in the queue**, on the queue's own
logic that the marginal cost inside a transfer-bound pass is minutes and outside
it is two hours: the across-track detector column, which is what made item 16
tractable.

*The result that needed a decision, and the decision it turned out not to
need.* This entry previously said that under representativeness weighting the
spatial null's advantage disappears. **That was wrong, and the cause was a
defect in the test rather than a property of the weighting.** The weighting
variant left 21 single-sounding cells carrying their raw sounding count in a
column otherwise holding representativeness weights, and those 21 cells took
88.6 percent of all weight. Corrected, the null rises under representativeness
weighting rather than collapsing, impervious rises too, and the ordering is
unchanged. The weighting decision is therefore low-stakes on the evidence and
is recorded in `notes/decisions.md`.

**The pass produces 0.25 degrees only, decided 15 September 2026 by
measurement.** This was an open question in the queue and it is now closed
against the finer grid, which removes a branch from Tier 3's scope rather than
adding one. `data/processed/grid_resolution_2018.csv` measures it and
`notes/decisions.md` records the reasoning. The short form: a 0.1 degree lattice
holds 6,314<!--#resolution.cells_01--> cells against
1,023<!--#resolution.cells_025--> at 0.25 degrees, and carries **no more
independent information** — the modelled effective sample size is
30.9<!--#resolution.effective_n_025--> at 0.25 degrees and
30.6<!--#resolution.effective_n_01--> at 0.1, because effective n is set by the
domain's extent against the autocorrelation length and regridding changes
neither. Meanwhile the median cell's standard error doubles, from
3.37<!--#resolution.se_025--> ppb to 7.49<!--#resolution.se_01--> ppb against a
between-cell signal of 14.9 ppb, and the number of cells whose error exceeds the
entire field spread rises from 63<!--#resolution.over_spread_025--> to
1,015<!--#resolution.over_spread_01-->. **Six times the cells, no additional
information, twice the noise.**

*Two consequences for the items below.* Item 14's within-cell variance
accumulator is unaffected, since it is per-cell at whatever resolution is
chosen. Item 15's growing-season composite gains nothing from a finer grid and
would lose from one, because a seasonal subset already cuts each cell's count
and the finer grid cuts it again — the two multiply.

*And one for the paper rather than the queue.* The resolution belongs in the
discussion of resolution, where it **strengthens the capability claim**: the
working resolution is a constraint the observations impose, now measured, rather
than a convenience adopted without examination. It is also the one place the
paper can say that a finer grid would help a method it does not use — an
inversion propagates information through a transport model, so its fine cells
are constrained by observations elsewhere, where a per-cell composite leaves
each cell on its own.

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

### Tier 4 — DONE, and it was never gated

**Item 14 was not a gate.** The within-cell spread this item needs was already
in the seasonal accumulator's `hs::sum_yy`, so item 17 was available for as
long as the harmonic statistics existed. It is now measured, tested and
decided.

**17. DONE and decided: sounding-count weighting stays primary, with
representativeness reported beside it.** The first test of it was wrong — it
left 21 single-sounding cells carrying raw counts in a column of
representativeness weights, and those cells took 88.6 percent of all weight,
producing a spurious collapse of the spatial null. Corrected, both the model and
the null rise and the ordering holds in all four designs, so nothing about the
fits turns on the choice and it is made on continuity. **Where it does turn on
the choice is the equivalence claim**, and there continuity is not allowed to
decide: impervious clears the bound in 4 of 4 fields under count weighting and
0 of 4 under representativeness, so the claim is stated at the weaker level.
`notes/decisions.md` records both decisions and why they are separate.

*What remains, and it is a new item rather than this one.* The weight is
undefined on the 21 single-sounding cells and its spread term is unreliable
below about ten soundings. A better version would shrink the spread estimate
toward the pooled value and use a measured within-cell spatial coverage rather
than the low-coverage limit — and the second of those needs sub-cell sounding
positions the accumulator does not retain.

**17 (superseded framing). Representativeness weighting in place of
sounding-count weighting.**
Coverage "is not an effective metric to limit representation errors", and this
project uses it in a figure, a raster band and every model weighting. The
implementable alternative weights by within-cell spread scaled by the uncovered
fraction. *Established by* the methods record. *Gated by* item 14. **This item
has the widest reach in the queue**: it changes the weighting of every baseline
in the repository, so everything downstream of the baseline suite moves with it.

### Tier 5 — two done, one queued at a cost far below a pass

**18. DONE.** `data/processed/equivalence_bounds_2018.csv`. Of 36 combinations
none falls outside the bounds; rice clears them in all 24 and impervious in 7 of
12. **The gate on item 11 did not bind**: the bound is comparative rather than
an effect size on the predictor's own scale, so the de-attenuated coefficient is
not what it is set against. The policy bound the record proposed could not be
set at all — it bounds emissions, and reaching the column needs the transport
model this work does not run.

**19. PARTLY DONE, 14 September 2026, and cheaper than this said.** The three
feasibility counts are recovered and reproduce exactly:
2,767<!--#tccon.retrievals--> retrievals on 44<!--#tccon.days--> days and
9<!--#tccon.coincident_days--> coincident days, now in
`data/processed/tccon_hefei_2018.csv` behind a network-tier recipe. **It cost
57.5 MB, not the 480 MB this item priced**, because the checkpoint already holds
a packed cell bitmap per granule beside each granule's filename and acquisition
time, so no granules had to be fetched at all.

What remains queued is the **alignment**, which is the part that would make the
comparison a validation rather than a feasibility measurement. That still needs
the averaging kernel and both priors *per layer*, which live in granules and not
in the checkpoint. **And the licence does bind**: clause 5 requires contacting
the site's listed individuals four to six weeks before submission for any work
including TCCON data, which is now the earliest date this paper can be
submitted. Only co-authorship turns on essentiality.

**20. DONE.** `data/processed/specification_curve_2018.csv`, 126 specifications
rather than the forty-eight this item anticipated, because the preprocessing
variants and a third weighting were added after it was written. None is both
positive and beats its own spatial null.

**18 (original). Equivalence bounds for the central claim.** Two one-sided tests against a
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

### Added 13 September 2026, from the coal and urban amendments

**0a. Whether the coalfield's cells behave differently in the decay curve, and
whether excluding them changes the association.** *Gated by nothing* — the
decay curve and the per-cell predictions already exist as committed artefacts,
and northern Anhui is identifiable from the lattice geometry. [`notes/grounding-yrd.md`](grounding-yrd.md)
establishes that the Huainan–Huaibei coalfield sits inside the lattice in the
province a national gridded inventory names as the largest eastern emitter, that
neither predictor represents it, and that its cells coincide with the region
where the rice raster stops classifying. Item 4 established that the impervious
coefficient is not stable across the domain. **This is the cheapest item in the
whole queue and it tests a specific hypothesis about where the instability comes
from.** It belongs with Tier 0's free items rather than below them.

**0b. Re-block at six cells and re-run the baselines, if the paper uses the
blended field.** Already recorded above as the highest-value cheap item; noted
again here because it and 0a are the two items that need only what is committed.
`notes/decisions.md` records the residual half-sill range at 134.5 km on the
blended field against a block 95.0 km at its narrowest.

**6a. Two building-volume or building-function layers, or none.** *Gated by*
verifying the datasets in [`notes/dataset-leads.md`](dataset-leads.md). The 30 m
annual building height dataset is the only candidate resolving 2000, 2010 and
2018; CMAB carries building function, which is closer to the gas-and-waste
mechanism than height. **The GAIA–GISA lesson applies before either is adopted**:
the height products disagree in ways structured by urban form, so a single one
would import an unquantified error the way a single impervious product would
have. This sits beside item 6 rather than above it, because it is a new
covariate rather than a correction to an existing one.

### Added 14 September 2026, from the rice grounding

**0c. Test the published ten-percent condition on the subset that satisfies it.**
*Gated by nothing.* [`notes/grounding-rice.md`](grounding-rice.md) establishes
that the strongest published claim of a rice–XCH4 association states its own
domain of validity — "the 0.5° gridcells with moderate to high proportions of
rice paddy (area percentage >10% within gridcells)" — and that
304<!--#grid.rice_above_ten_percent--> of this lattice's cells satisfy it,
57.3<!--#grid.rice_above_ten_of_rice_percent--> percent of the rice-bearing cells
and 32.8<!--#grid.rice_above_ten_of_lattice_percent--> percent of the whole
field. **Every association this repository reports is computed over all
926<!--#composite.covered_cells--> cells, which is precisely the ROI dilution the
Reply warns against.** The test is a subset and a recomputation of the existing
correlations and baselines, with the degrees-of-freedom correction applied on the
subset's own geometry. It belongs with the free items and it is the cheapest
remaining item in the queue after 0a.

Two things make it more than a robustness check. This project's cells are
0.25 degrees, *finer* than the 0.5 at which the condition was established, so a
null on the subset is a stronger negative result than a null on the whole field.
And if the association does appear there, the published condition is the reason
to expect it, which converts a post-hoc subset into a pre-registered one.

**0d. Redo the thesis's rice validation against planted area for Zhejiang.**
*Gated by nothing.* The rice record establishes that the thesis compared its PPPM
extents to **sown** area and treated the statistics as truth, that the
definitional gap requires double cropping, and that Shanghai and Jiangsu are
0.00<!--#rice.double_share_shanghai_percent--> percent double-cropped in the
committed table — so the gap cannot explain the thesis's largest discrepancy and
the thesis's own explanation, urban density confusing the classifier, survives.
**Zhejiang at 16.27<!--#rice.double_share_zhejiang_percent--> percent is where
the definitional gap can contribute**, and Anhui at
8.36<!--#rice.double_share_anhui_percent--> percent to a lesser degree. The item
is to divide the reported sown area by the cropping index implied by the
committed single-and-double split and re-compare. **It cannot produce a
correction to the thesis**, which is submitted; it produces a sentence in a paper
about how much of a published discrepancy is definitional rather than
methodological.

**1a. Establish whether Zhu et al.'s PPPM maps are obtainable.** *Gated by
nothing but network access, and it is the gating question for a whole route.*
`notes/decisions.md` now records that the maps the thesis's own algorithm
produces already exist — annual single- and double-cropping rice for southern
China from Landsat 5, 7 and 8, 1999 to 2019, over a southern China that
explicitly includes Anhui and Jiangsu. Whether they are distributed could not be
settled: the article is paywalled, OpenAlex records no open version, and no data
availability statement was readable. **If they are obtainable, reading them
replaces the coverage argument for a PPPM reimplementation entirely** and
supplies a single-method rice layer for all three thesis years, which no
combination of committed products does. It sits in Tier 1 because it is one
request rather than a computation, and it should be first in that tier because
of what it gates.

### Added 14 September 2026, from the second rice block and the methane record

**0e. Test the rice–aquaculture confound by overlaying China_AP on the rice
layer.** *Gated by* fetching China_AP, which has no named deposit, so by one
request rather than by a computation.
[`notes/grounding-rice.md`](grounding-rice.md) establishes that freshwater
aquaculture is 1.6 to 2.5 Tg CH4 per year in China against 13.7 Tg for rice
paddies in a national prior, that it is absent from every inventory, that this
region holds 26 percent of China's aquaculture area, and that ponds and paddy are
spectrally similar flooded land whose confusion is a named problem in the mapping
literature. China_AP is 10 m, annual, and covers 2018.

**The test is a per-cell overlap fraction and it has three possible outcomes,
all of them worth having.** If the overlap is negligible, the confound is
dismissed cheaply and the rice fraction is what it claims to be. If it is
substantial, the rice predictor is partly measuring an unrepresented source, and
the association's interpretation changes rather than its value. And if the
overlap correlates with the residual, that is a positive finding about a source
nobody has mapped into an inventory. **This is the highest-value item added in
this pass**, because it is the only one that could change what the existing
association means rather than how confidently it is stated.

**0f. Run the association on a tropospheric partial column rather than a total
column.** *Gated by* fetching the MUSICA IASI/TROPOMI fused product, which needs
a registration rather than a credential this project lacks.
[`notes/grounding-methane.md`](grounding-methane.md) establishes that a total
column carries stratospheric variability driven by tropopause height and
large-scale dynamics, which no land-cover predictor over four Chinese provinces
could ever explain, and that `tro_XCH4` removes it by construction. **This is the
only item in the whole queue that could raise the association rather than explain
it.**

Its caveats are recorded with it so the item is not oversold. The product's
TROPOMI input is a beta version rather than this project's 020400, so the
comparison would not be like-for-like against the committed field. Coverage is
the TROPOMI–IASI intersection and therefore sparser, over a domain whose coverage
is already marginal. And the paper reports the combined tropospheric product's
degrees of freedom as "weakly above 1.0", so the separation carries barely more
than one independent piece of information. **A null on the tropospheric column
would be a stronger negative result than the null already in hand**; a positive
would need the coverage difference ruled out before it could be believed.

**5a. Sensitivity inversions varying the coal and wetland priors, if an inversion
is ever run.** *Gated by* the inversion itself, so it sits in Tier 5 with the
items that consume everything above. The template is Liang et al.'s Heilongjiang
rice inversion, which substituted the prior inventories for coal and for wetlands
to assess how those priors affected the rice estimate. IMI makes it cheap by
construction — "once K has been constructed, any ensemble of analytical
inversions exploring the sensitivity to different inversion parameters can be
easily and rapidly generated" — so the marginal cost is one Jacobian and the
ensemble is free.

**Record why this is not optional here.** The cross-layer synthesis above
establishes that attribution depends on the prior's spatial distinctness, and
this domain has coal in northern Anhui where the rice raster stops classifying
and a wetland prior whose own authors say it may include co-located rice. **Those
are the two priors whose substitution would most change a rice answer**, and an
inversion reported without that ensemble would be reporting a number whose
sensitivity to its own assumptions was never tested.

### Added 15 September 2026, from drafting the methods section

**0g. Record a pre-filter sounding count in the composite accumulator.** *Gated
by nothing;* one additional counter in a streaming loop, and a re-run of a
recipe that already regenerates from a fresh clone.
[`notes/draft-methods.md`](draft-methods.md) cannot write the standard
formulation — *N soundings were read, of which M passed quality control* —
because the accumulator retains counts only after filtering. Every sounding count
in this repository is post-filter, so the quality filter's rejection rate over
this domain is unknown. **This is the cheapest item in the queue and the only one
that a reviewer would certainly ask about**, since a methods section that reports
a quality threshold without reporting what it removed is reporting half a filter.

**0h. Name the primary target field, or justify reporting three.** *Gated by
nothing*, because it is a decision rather than a computation. Four fields are
carried and three have complete baseline suites; no record chose between them,
and the draft chose the operationally bias-corrected field for a stated reason
while noting that the choice was made at the keyboard. Either that choice gets
ratified in the record, or the paper reports all three as co-primary and says
why. **What it cannot do is leave the question implicit**, which is what six
grounding passes did.

**The draft also reorders one item already in the queue.** The IMI preview run
was ranked most valuable by the capability reframing. Drafting sharpens the
reason: the paper's central number — expected degrees of freedom for signal over
this lattice — is now the only major figure in the methods section that no
external tool has confirmed. Everything else is either a committed artefact with
a resolver or a quotation from the literature. **That asymmetry is visible in the
draft in a way it was not visible in the records**, and it is the strongest
argument yet for spending the one free run.

### Added 15 September 2026, from drafting the results section

**0i is decided, 16 September 2026, and this entry records the outcome.** The
land-cover result is reported as a **range across the four scheme-weighting
combinations**, with all four tabulated and spatial blocks unweighted named as
the reference point wherever one figure is needed — labelled as the optimistic
end of the bracket rather than as the answer.
[`notes/decisions.md`](decisions.md) carries the grid and the reasoning. The
deciding fact is that the four-way spread belongs to the evaluation and not to
land cover: impervious fraction's spread is
0.247<!--#spread.impervious--> of R², against
0.342<!--#spread.wind--> for wind,
0.410<!--#spread.albedo--> for albedo,
0.544<!--#spread.trend--> for the trend surface,
0.605<!--#spread.null--> for the spatial null and
0.708<!--#spread.sampling--> for sampling composition. **Land cover has the
smallest four-way spread of any predictor in the suite**, so quoting one
combination as characterising the model would attribute the design's variance to
the predictor.

Two rules follow and apply repository-wide: no land-cover R² is written without
its scheme and weighting, and no figure showing one combination omits which. The
sweep for unscoped figures is queue item 0l below.

**0j. Compute the blended field's albedo slope.** *Gated by nothing;* one series
added to a script that already computes the same quantity for four others.
`albedo_correction_2018.csv` covers the raw retrieval, the operationally
corrected field, the correction itself and the deseasonalised field. **The
blended field — the one that addresses albedo by construction — is the one whose
residual albedo dependence has never been measured**, which is why the
primary-field justification currently rests partly on diagnostic availability
rather than only on field quality. Fixing it may change that justification, which
is the point of doing it.

**0k. Summarise the coverage saturation curve as a scalar.** *Gated by nothing.*
The figure holds the shape and nothing records the number a results section asks
for — after how many granules coverage reached a stated fraction of its final
value. One line against a committed artefact.

**And two figures move to the front of the figure queue.** The buffered decay
curve and the DOFS sweep are the two results the capability framing makes
central, and neither has a figure or was planned to have one; both exist only as
small tables, both are line plots over a swept parameter, and neither needs new
data. `notes/decisions.md` records the audit. They rank ahead of the three
planned figures — predictor maps, fold map, sampling-artefact map — which answer
to the 2023 thesis's figure set rather than to this paper's results.

**SUPERSEDED 14 September 2026 by a full assessment of the set.** Both were
built. The figure queue is now `figures/figure-assessment.md`, which asked what
set the paper needs rather than which planned figures to build, and the three
planned figures all survive — the fold map for a reason this entry got wrong,
since `buffered_decay` turned out to be the argument *for* it rather than a
substitute: that figure's caption states the fold distance "has never been
measured in this repository".

### The figure set, assessed 14 September 2026

**Proposed: eleven in the main text and seven in the supplement**, against the
eight to twelve an ACP capability paper carries.

*Main text, in order*: `study_area`; **predictor maps (new)**;
`coverage_saturation_2018`; `methane_composite_2018` **plus one new
observation-day panel**; `observed_predicted`; `residual_field`;
**the specification curve (new)**; `albedo_collinearity`; `buffered_decay`;
`capability`; **a source map (new)**.

*Supplement*: `landcover_native`, `landcover_regional`, `urban_change` panel (c)
rebuilt standalone, `framework_pipeline`, `framework_reproduction`, the fold map
and a semivariogram-range figure.

**The build list, in cost order.** The specification curve, predictor maps and
the semivariogram ranges plot committed artefacts and are drawing rather than
analysis. The fold map needs a registered distance computation first — the
~56 km median it would show is a scratch calculation quoted nowhere. The source
map is partly blocked: four of six sectors come from committed artefacts, and
the wastewater coordinates and coalfield extent need a fetch, the coal layer
through the request form `notes/dataset-leads.md` records.

**Five existing figures need rebuilding for one shared reason**: nine of the
thirteen modules render their explanatory paragraph *inside* the image with
`figtext` — `residual_field` bakes seven lines — and in a manuscript that text
belongs in the caption. `study_area`, `observed_predicted`, `residual_field`,
`albedo_collinearity` and `urban_change` are affected in the main text.

**Two panels are dropped and nothing else is.** `urban_change` (a) and (b) are
two categorical maps of two products whose finding is that they disagree, which
is the one form that cannot show it. Panel (c) carries both of that figure's
findings. *Needs* no new analysis.

**One gap in the figure sequence has no figure and should not get one.** The
contribution's pairing — that the identifiability limit is untouched by any
improvement to the information limit — is an argument rather than a
measurement, and a schematic would lend it the appearance of one. A reader
looking only at figures will not get it, and prose has to carry it.

### Added 16 September 2026, from settling 0i and 0j

**0j is done.** The blended field's albedo slope is computed and in the
artefact, and the answer reversed a justification rather than supporting it: the
blended field's slope is the steepest of the four,
232.8<!--#albedo.slope_blended--> ppb per unit albedo against the operationally
corrected field's 199.7<!--#albedo.slope_corrected-->. The results draft's
primary-field argument from diagnostic availability is withdrawn, and
`notes/decisions.md` records that the measurement had existed in the decision log
all along and was missing only from the artefact.

**0l. Sweep the repository for land-cover figures written without their scheme
and weighting.** *Gated by nothing.* Four places carry one: the methods record's
sample-size argument, the observed-predicted figure's panel descriptions and the
sentence that refers back to them, and the methods draft's baseline paragraph.
`README.md`, `data/processed/README.md` and the results draft's table are already
scoped. **This is the same class as the prose-claim audit** — a number that is
correct and unscoped is not checkable — and it is why the two rules above are
recorded as rules rather than as a one-off fix.

**And one thing 0i's grid settled that was not asked.** The claim that no
land-cover model beats the spatial null holds under all twelve field-scheme-weighting
combinations in the sense that matters, and the three apparent exceptions are all
leave-one-province-out unweighted, where both models score below zero: on the
primary field rice-combined reaches
-0.059<!--#suite.rice_combined_pu--> against the null's
-0.091<!--#suite.null_operational_pu-->. **Land cover never beats the null where
the null has positive skill**, which is a stronger statement than the records
previously made and should replace the unscoped version wherever it appears.

### What gates what, in one paragraph

**As of 13 September 2026 Tier 0 is complete and three items sit above or beside
it.** Item 0b, re-blocking at six cells, is the highest-value cheap item. Item
0a, testing the coalfield's cells against the decay curve, is the cheapest and
needs only committed artefacts. Item 6a, a building-volume or building-function
covariate, is gated on verification rather than on any other item. The paragraph
below describes the original structure and still holds for items 5 to 20.

**And one thing the 13 September amendments reorder.** The region record now
carries an omission rather than only confounds: part of the domain has an
unrepresented major source and a missing predictor in the same cells. That makes
item 0a a prerequisite for interpreting items 9 and 11 rather than an aside — an
accuracy assessment and a de-attenuation computed over a domain containing cells
whose emission neither predictor represents would attribute to measurement error
what is actually omitted-variable bias.


Item 1 gates the paper's framing and costs nothing, so it is first on both
counts. Items 2 to 4 are free and change reported statistics, with 3 gating 4.
Item 5 gates 9, which with 10 gates 11, which gates 18 — that is the critical
path to the strong form of the central claim, and it runs four deep. Tier 3 is a
single decision about one transfer, and within it 14 gates 17, which is the item
that moves every number downstream of the baselines. Item 20 is last by
construction. Items 6, 7, 8 and 19 sit off the critical path and can be done
whenever.

## The honest state of the grounding, 14 September 2026

The last of the planned passes is done, so this records what the whole exercise
came to, including the two things it got systematically wrong.

### What was built

Five records, written between 10 and 14 September 2026, from round counts as the
commissioning briefs stated them: nineteen rounds on the region, fifteen on the
urban layer, eleven on methods, fourteen on rice across two blocks, eleven on the
methane layer, three cross-layer searches and three reviewer rounds. **Round
count and value turn out to be unrelated**, and the clearest evidence is the
register: the twelve commits that touched it introduced 14, 12, 1, 10, 3, 23, 40,
25, 1, 15, 22 and 28 citations, and the three-round reviewer pass — the smallest
of them, five entries — is the one that changed what the paper is.

What each pass changed, in one line apiece:

* **The region** established that this is the right place to ask, and later that
  Southeast China is one of three sub-national regions carrying 60 percent of
  China's emissions on under a third of its land.
* **Methods** established that the field's method for this problem is Bayesian
  inversion and that a free tool exists, which reframed the whole project from a
  regression exercise into a capability question without anyone noticing at the
  time.
* **Urban** established that an impervious fraction is the wrong instrument for
  the dominant sector, and that it is nonetheless the best available proxy for
  the thing the thesis used it for.
* **Rice** established that extent is a weak predictor by the field's own
  explicit account, and found aquaculture — an unrepresented source in the same
  cells as the predictor.
* **Methane** established that there is no processing step from a column to a
  flux, which is the boundary the thesis's title implies away.
* **The synthesis** established that the three layers are not three predictors
  but overlapping sources the field's own method groups together.
* **The reviewer pass** established that all of that is a capability assessment
  rather than a null result, and that capability assessment is a paper type.

### The two systematic weaknesses the passes exposed about themselves

**Citations written from search phrasing were defective at about one in eight,
and adopting content negotiation fixed only what it checked.** The audit of
13–14 September re-negotiated all 189 entries and found 23 wrong in 31 fields,
with four more found while writing the guard. The split is the finding: twelve of
the defective entries were in the hundred written before negotiation was adopted
and eleven were in the eighty-nine written after — **the same rate either side.**

What changed was the *kind*. Every substituted name — a name belonging to a
different paper, including one whole author list grafted from a companion study
where every other field checked out — is in the pre-negotiation population. The
negotiated population's author defects are omissions rather than substitutions, a
transcription slip rather than a mis-binding. And its other defects are page
ranges, truncation counts and publication years: **fields nobody was checking,
because the practice adopted was "negotiate the author list" rather than
"negotiate the record".** The lesson generalises past citations. A verification
habit protects exactly the field it names and creates the impression of
protecting the record.

**And findings held only in conversation are where the premises failed.** Every
brief that commissioned these passes carried figures from earlier conversation
rather than from a file, and every pass reported several that did not survive:
the region pass several, the methods pass eleven premises of roughly sixty
figures, the urban amendment eight, the rice blocks eight and nine, the methane
record nine, this pass two of four. **The pattern is not carelessness in the
briefs.** It is that a number which has been repeated across sessions acquires
the texture of something checked, and nothing in a conversation distinguishes a
figure that was verified once from a figure that was asserted once. The
repository's answer is mechanical and partial — `scripts/verify_claims.py` for
its own artefacts, `tests/test_register_authors.py` for its citations — and
covers only what someone thought to mark.

**The honest summary of the grounding is therefore two-sided.** It established
the paper's frame, its contribution, its limits and most of its literature, and
it did so at a defect rate in its own records of roughly one in eight until that
was measured and fixed. Both halves belong in the account, because the second is
what makes the first believable.

## What is still ungrounded

Recorded so that the gap is visible rather than assumed closed.

**The rice layer's record was written on 14 September 2026 and this entry is
kept as a closed gap rather than deleted.** Its findings had been scattered
through the region record — the calendar, the water regime, the cropping-system
transitions — and through the methods record, which holds the emission-factor
chain and the reference polygons. [`notes/grounding-rice.md`](grounding-rice.md)
now holds them, together with the layer's own conclusion: extent is a weak
predictor of rice methane by the field's explicit account, and what a better map
buys is spatial distribution rather than magnitude. **All three layers are now
recorded to the same standard**, and the same pass gave each a review-level
synthesis anchor, which is what an introduction can be written from.

**The methane layer's record was written on 14 September 2026 and this entry is
kept as a closed gap too.** The composite's own properties are documented at
length in `data/processed/README.md`, and the methods record holds the
retrieval's uncertainty, the preprocessing chain and the representativeness
problem. What none of them held was the target variable as a subject.
[`notes/grounding-methane.md`](grounding-methane.md) now does, and its conclusion
is the boundary a paper has to state in its own voice: **there is no processing
step from a column to a flux**, so the distance between what this project
measured and what the 2023 thesis's title implies is a difference of method
rather than of rigour. It also carries the one finding in any pass that could
raise an association rather than explain it — a tropospheric partial column from
a fused TROPOMI–IASI product, which removes stratospheric variance no land-cover
predictor could explain.

**All four records now exist.** What remains ungrounded is listed below rather
than by layer.

### What remains ungrounded after four records, 14 September 2026

**Two methane threads were not touched by the eleven rounds, and both stay open
deliberately.** Updated 14 September 2026, after the capability framing, which
changes what each is worth.

The first is future instruments — MethaneSAT, GOSAT-GW, CO2M and the Chinese
missions — which bear directly on whether this project's question becomes
answerable later rather than on whether it is answerable now. **Under the
capability framing this becomes more interesting and no more urgent.** A paper
whose contribution is what a 25 km column record can constrain invites the
question of what a finer or denser record would constrain, and the transfer
argument already answers its structure: more observations move the
information-content limit and leave the identifiability limit untouched. So the
thread belongs in a discussion paragraph — one that names the instruments and
says which limit each would and would not move — rather than in the analysis. It
is a paragraph to write, not a pass to run. [`notes/grounding-methane.md`](grounding-methane.md)
establishes that the degrees of freedom scale with observation density, so a
denser instrument moves the capability finding, and no pass has asked by how
much or when. The second is fetching the WFMD product and comparing it against
this project's own field. The European three-product comparison now covers that
question in principle — [`notes/grounding-methane.md`](grounding-methane.md)
records budgets of plus 2 percent for SRON, minus 1 for the blended product and
minus 33 for WFMD from three retrievals of the same quantity, with albedo and
aerosol scattering named as the largest contributors — so **the question is
answered in structure and only the local magnitude is unmeasured.** That is why
it stays open rather than closing: a 35-point spread from retrieval choice is
worth knowing the local size of, and it is worth less than it was when the
spread itself was unknown. It is a deferred check, not a gap.

**The reviewer pass was run on 14 September 2026 and is closed.** It is recorded
above, under *What a reviewer would object to, and the answer*. The prediction
that the two filters would produce different reading lists held: three rounds
produced five register entries, none of which any earlier round had found, and
one of them — capability assessment as a named paper type with its own
vocabulary — reframed the contribution. **It also found that the worry those
rounds were expected to confirm was unfounded**: publication bias against null
results is weaker than assumed, and the obstacle is the novelty framing instead.
The pass cost three rounds and changed what the paper is. It should have been run
first.

**The satellite question has not been asked at all.** Whether other instruments
or validation sources have been overlooked — GOSAT and GOSAT-2 in their own
right rather than as the blended product's other half, Sentinel-2 or EMIT or
PRISMA for point sources, EM27/SUN campaigns, aircraft or tower records beyond
the two already ruled out — has never been searched. The region record ruled out
the in-domain column and tower options it knew of, and the urban record notes
that hyperspectral instruments have been used against Chinese landfills, but no
pass has gone looking systematically. **This is the largest unexamined area and
it is not in the planned sequence**, which is why it is recorded here.

## The apparatus, audited 14 September 2026

The data and code availability statements now exist as drafts in
`notes/draft-availability.md`, assembled from the three registers that hold
provenance and from the recipe registry. The reference-list half of the same
audit is in `notes/reference-audit.md`. Two things belong in this document
rather than in either of those.

**The reference list will be short, and that is a property of the work.** If
every claim needing a citation got one, the list would run to about 31 entries
against the 12 <!--#register.draft_cited--> the drafts cite today. Only
124 <!--#claims.cited--> of the inventoried numbers are quoted from anyone; the
rest are measured here. This is below what an ACP article typically carries, so
it is worth stating in the cover letter rather than leaving a reviewer to read
it as thin scholarship. The drawn set is also more method-heavy than the
register it comes from, 32 percent against 23, which follows from the
load-bearing choices being methodological.

**Six things now wait on a decision rather than on work.** They are recorded in
full in `notes/decisions.md`; in brief, and in the order they would block a
submission:

1. The blended product's terms ask that its author be contacted before
   publication. Not done, and the only unmet provider condition in the project.
2. ~~No `LICENSE` file.~~ **Wrong; it is MIT and always was.** What was
   missing was the scope, now stated in `README.md`. What is still missing is a
   DOI: ACP requires code to be cited by one and `CITATION.cff` names a GitHub
   URL.
3. The Hefei TCCON counts appear in four documents, have no artefact, and
   support the "not a validated result" framing. Roughly 480 MB regenerates
   them; the alternative is to cut the sentences and lose the argument.
4. The committed analysis grid's rice input came under a personal-use grant
   with no DOI. Keep it and document the 190-row substitution, or rebuild on
   the Science Data Bank product and lose `rice_fraction_combined`.
5. GISA's download page states no licence terms. (The S5P route was listed here
   too and should not have been: the Copernicus Sentinel Data Legal Notice
   governs it, and its required notice is now carried.)
6. **Author contributions, competing interests and financial support are absent
   from every file here.** A submission needs all three, none is analysis, and
   no pass over the apparatus has noticed because nothing can fail a test.

**What the audit found in good order**, recorded because the negative result is
worth as much here: 41 <!--#pipeline.recipes_committed--> of the
74 <!--#pipeline.recipes--> recipes verify from a clone alone on every run of
the suite; the Copernicus attribution notice is asserted verbatim against the
rendered figure, so a rebuild cannot drop it; and the one unregenerable
artefact feeds no published figure and resolves no prose number.

## What remains before writing, 14 September 2026

The apparatus is no longer what blocks a draft. Four defects were named as
submission-stopping; three are fixed and the fourth never existed. The
availability statements, the journal sections and the licence scope are drafted
in `notes/draft-availability.md` and `README.md`, the Hefei counts are behind a
recipe, and the one restricted data column is citable.

**The earliest submission date is now set by a licence, not by the work.**
Clause 5 of the TCCON Data License requires contacting the Hefei site's listed
individuals a minimum of four to six weeks before a manuscript is submitted, for
any work including TCCON data. That clock has not started. If the intent is to
submit, starting it is the first action, and it is independent of everything
else on this list. The author of the blended TROPOMI+GOSAT product should be
contacted in the same pass.

**Three things no file here can supply**, all Matt's: whether the paper is
single-authored, given the 2023 thesis was advised; whether the thesis was
funded, since ACP reports grant numbers to FundRef; and the wording of the AI
usage disclosure ACP requires, which for this work is substantial rather than
formal.

**One ten-minute job on Matt's account**: a Zenodo release, for the code DOI ACP
requires and an ORCID for `CITATION.cff`.

**What is left that is actually work**, in the order it would be done:

1. **The figure set.** Thirteen of a planned sixteen exist. This is the largest
   remaining build and it is assessed in `figures/figure-assessment.md`.
2. **The errata audit**, deferred from this sequence on the sound ground that
   auditing a supporting document against an unwritten paper means auditing
   against an unknown target. It comes after a draft exists, not before.
3. **The TCCON prior alignment**, still queued and still optional. It is what
   would turn the feasibility measurement into a validation, and it is the one
   item whose completion would change the co-authorship position under the TCCON
   licence.
4. **The satellite question**, which remains the largest unexamined area and is
   still not in the planned sequence.

**And one thing to decide rather than do.** GISA states no licence and nine
committed artefacts derive from it. Every other source in this project has terms
that can be quoted; this one has a sentence in a paper describing the product as
freely available for research. Seeking written permission is thorough; relying
on the description is what the field does. It is worth choosing deliberately,
because it is the only place where redistributing this repository rests on a
reading rather than on a grant.

## What the primary-source re-read changed, 15 September 2026

Two items moved from statement to decision, and one obligation appeared.

**1. The prose cannot be reused, and this is the largest change to the plan in
this document.** ACP's AI policy states that "Generative AI must not be used for
text or interpretations." The drafts in `notes/` were written by an AI
assistant, so they cannot be the manuscript's text and their arguments cannot be
its interpretations. Assistive use needs no declaration and illustrations and
schematics are permitted with the tool named, but this category has no
disclosure route. **The writing is therefore work still to be done, not work
already done.** What the drafts remain is a complete record of what was found
and why, and everything needed to write from — the artefacts, the guards and
`notes/decisions.md` — is in place. An earlier record here treated this as a
disclosure to be worded, which understated it.

One reading this rests on and cannot settle alone: that analysis code is not
manuscript text, so the pipeline is disclosed through code availability rather
than prohibited. That should be put to an editor before submission, because the
whole submission depends on it.

**2. A required attribution notice was owed and is now carried.** Eight
committed methane artefacts are modified Copernicus Sentinel data, and the
Sentinel Data Legal Notice requires "Contains modified Copernicus Sentinel data
2018" on distributed adaptations. This repository already had that notice text
on file, correct and fully sourced, recorded for Sentinel-2 and never applied to
Sentinel-5P. Any figure that draws the composite should carry it in its caption
too, which is a build decision rather than a text one and is not yet done.

**3. The availability statement's placement is specified.** ACP requires it "as
the last paragraph of each article", not as a back-matter section placed
wherever it fits, and datasets and code are additionally linked by DOI in the
assets tab. That makes GISA's want of a DOI a second problem beyond its licence.

**And one claim got stronger rather than weaker.** The capability assessment's
central threshold was resting on a DOFS cut-off whose attribution does not hold.
Its originators' actual criterion — better than 30 % at 2σ above 0.2–0.5 Tg a⁻¹
and 5,000 observations a⁻¹ — applies to this domain directly and is met by a
wide margin, so the claim that this record can constrain a domain total is now
better founded than it was. The method itself was checked line by line against
the inversion facility's own source and reproduces it exactly.

### The practice this establishes

A load-bearing claim about an external thing should cite **the passage** it rests
on, not the work. A paraphrase written from a search result, an abstract or a
paper's summary of another paper is provisional until the source is opened, and
should be marked as such until it is. This pass found that every claim which
turned out wrong had been read from an intermediary and every claim that held
had been read from the source, which makes reading-provenance the thing worth
recording — because it is what predicts error, and it is cheap to record at the
moment the note is written and expensive to reconstruct later.
