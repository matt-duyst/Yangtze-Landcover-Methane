# Introduction, draft

Draft prose for the paper's opening section. Deliberately the shortest of the
four: an introduction motivates and states, it does not survey. Every factual
claim comes from a committed record or artefact, and every quoted number carries
an inline resolver.

**The order is motivate, locate, then state.** Why the question matters and why
here (§1), what has been tried and what each attempt establishes (§2), the gap
those attempts leave (§3), and what this paper does (§4). §3 carries the weight,
because the objection this paper has to survive is not that its result is
negative but that its components are individually known.

## 1. Why methane, and why this region

Methane is the second-largest anthropogenic contributor to present-day warming
and the one with the shortest response time, so the sectoral allocation of
national inventories is a policy quantity rather than only a scientific one. For
China, the largest emitter, the allocation is poorly known: national bottom-up
totals differ by at least 30 percent — about fifteen Tg a⁻¹, roughly one rice
sector — and the four most uncertain sectors include both of the land-cover
hypotheses this work tests.

**Emissions concentrate where this study looks.** Three sub-national regions,
including the Yangtze River Delta, carry about 60 percent of China's emissions on
under 30 percent of its land. An assembled national prior puts the sectoral
shape at coal mining 21.0 Tg a⁻¹, rice paddies 13.7, wastewater 9.5, livestock
8.2, landfills 5.2, wetlands 2.0, and lakes with aquaculture 1.3, against an
anthropogenic total of 64 Tg a⁻¹ — so **coal is the largest single anthropogenic
sector nationally, at more than half again the rice sector.**

**What makes this domain the right place to ask the question also makes it the
hard case.** Within these four provinces and at the scale of a satellite
retrieval cell, paddy rice, freshwater aquaculture, natural wetland, landfills,
wastewater treatment, urban gas distribution and coal mining are all present and
interleaved. The four provinces hold 26 percent of China's aquaculture area,
ponds sit in the same flooded lowland as paddy, and the Huainan–Huaibei
coalfield lies inside the domain. That co-location is the substantive difficulty:
a region where sources were spatially separated would be easier to attribute and
would not represent the places where attribution matters most.

The observing system adds its own constraint here. Shortwave-infrared retrievals
suffer frequent gaps under monsoon cloud, and rice, lakes and wetlands in
southern China carry posterior emission uncertainties of 53 to 69 percent for
that reason. The 2018 record over this lattice is an eight-month record beginning
30 April, with a median of 23.0<!--#dofs.days_median--> observation days per
covered cell.

## 2. What has been attempted

**Correlation between land cover and column methane, and the exchange it
provoked.** Satellite column methane over rice-growing regions correlates with
paddy extent and with the growing season, and that correlation has been read as
evidence of rice emissions. It was contested directly: decomposing the seasonal
cycle of column methane into locally emitted and externally transported
components across four regions found transported fluxes contributing more than
local ones in Northeast China, **Southeast China** — which contains this study
area — and Northwest India. The reply argued that coarse regions of interest,
coarse grid cells and inaccurate model inputs cannot capture the spatial
heterogeneity of methane sources. The exchange was not settled by further
measurement over this domain.

**Inversion, which can support the claim the correlation cannot.** A tower
inversion of this region in 2018 found agricultural soils to be the dominant
driver of seasonal variability in atmospheric methane. That is a positive local
result obtained by a method with a transport model and an optimised flux, and it
sets the standard against which a regression on static land cover has to be
judged.

**Downscaling, which establishes the difficulty.** Predicting column methane
from gridded predictors is an active method, and methane is the hard case: over
the Arabian Peninsula, gradient boosting with a carbon tracker, satellite land
products and reanalysis reached R² 0.98 for column carbon dioxide and **R² 0.63
with an RMSE of 13.26 ppb for column methane** on the same inputs, described by
its authors as moderate accuracy. An RMSE of 13.26 ppb is comparable to this
field's entire between-cell standard deviation of
14.86<!--#field.sd_operational--> ppb.

**And capability assessment, which is the paper type this work belongs to.**
Assessing what an observing configuration can resolve is an established
contribution with its own vocabulary — instrument precision, pixel resolution,
measurement frequency, and degrees of freedom for signal.

## 3. The gap

**The capability literature is simulations and reviews.** The works that define
the paper type assess configurations rather than records: they specify an
instrument, a prior and a set of sectors, and compute what could be recovered.
That is the right design for the question they ask and it forecloses one they do
not.

**An observing system simulation experiment cannot measure identifiability,
because its sectors are separate by construction.** The experiment builds a
truth field from sectors the modeller has defined, so whether two sectors can be
told apart is settled by how they were written down, not by how they sit on the
ground. **Identifiability is a property of the priors' spatial structure in a
real domain**, and a simulation supplies that structure rather than measuring
it. The consequence is that the limit which is hardest to escape is the one the
literature's dominant design cannot see.

**So what is missing is both limits measured on one real domain**: how much
information the observations carry, and whether what they constrain can be
attributed to a sector, with the same instrument, the same period and the same
interleaved sources. Each limit alone says the question is not answerable as
asked. Together they say something stronger, which §4 states.

This paper extends a 2023 master's thesis that asked whether urban expansion and
paddy rice explain the methane field over these four provinces; an accompanying
errata document records what that study did and did not establish, and this paper
does not revisit it further.

## 4. What this paper does

**The contribution is a capability assessment of a real satellite column record
over a region whose methane sources overlap, not a negative result about land
cover.** What is new is the pairing of two independent limits measured on the
same domain:

* an **information-content** limit — expected degrees of freedom for signal
  accrue across many weakly constrained cells, so a regional total is
  constrainable while cell-level attribution is not. Over the range the
  literature supports for this domain's emissions the estimate runs from
  3.98<!--#dofs.at_5tg--> to 22.21<!--#dofs.at_12tg-->, and **no cell reaches an
  averaging-kernel sensitivity above 0.5 at any magnitude tested** — the count is
  0<!--#dofs.cells_above_half-->;
* an **identifiability** limit — sectoral attribution derives from the priors'
  spatial distinctness rather than from the observations, which in a domain with
  interleaved sources bounds attribution independently of how many observations
  there are;

together with the demonstration that **the second is untouched by any
improvement to the first.** More observations raise degrees of freedom and do
not make a prior more spatially distinct; a better prior sharpens attribution
and adds no information the observations do not carry.

**Three things that claim is not.** It is not an inversion: the
degrees-of-freedom figures reimplement a published closed-form estimate over
this lattice, with no transport model run and no emissions optimised, and they
are bounded to this domain, instrument and period. It is not a priority claim.
And it is not a validated result — one year, one instrument, nine coincident
ground-based column days without prior alignment, and no accuracy assessment on
either land-cover layer, the last because no reference layer over this domain is
more accurate than the products it would assess.

**The land-cover result is reported as the assessment's occasion and as
supporting evidence**, not as the contribution. No association survives
correction for spatial dependence, control for surface albedo, or evaluation
under more than one held-out design. **The one confound that could manufacture
such a result rather than explain it — measurement error in a predictor, which
attenuates its coefficient toward zero — is measured and excluded for the
impervious layer**: using the second impervious product as a second measurement
of the same quantity bounds the de-attenuation factor at
1.15<!--#atten.factor_max-->, and reaching the spatial null's performance would
require 74.5<!--#atten.need_share_bu_pct--> percent of the predictor's variance
to be error, which is 5.6<!--#atten.need_multiple_bu--> times what the two
products' disagreement supports. **That bounds how much attenuation could be
present; it does not estimate the coefficient, and no claim about the size of a
land-cover effect is made anywhere in this paper.**

---

## Drafting notes, not part of the section

### What drafting the introduction forced

**The contribution statement was reassessed rather than inherited**, as Part 3a
of the brief required, and `notes/paper-target.md` records the reassessment. The
headline stands: the bound concerns the land-cover result, and the contribution
is the pairing of the two observing-system limits, so promoting the bound would
claim novelty for a standard errors-in-variables argument applied once. Two
amendments follow from it — that the supporting null is now defended by
measurement rather than by construction, which §4 states in one clause, and that
"no accuracy assessment" has the sharper form "no reference layer exists", which
§4 also states.

**One sentence had to be cut for being unsupported.** A first draft of §1 said
methane's sectoral allocation "is contested in China more than elsewhere". No
record establishes a comparison between countries; what the records establish is
that China's own bottom-up totals differ by at least 30 percent. The comparative
claim is gone.

**The 60-percent figure needed its qualifier kept.** The record says *three*
sub-national regions including this one carry 60 percent on under 30 percent of
the land. Writing "this region carries 60 percent" would have been a
four-fold overstatement of the most quotable number in the section.

**And the sectoral budget forced a decision about coal.** The national prior puts
coal at 21.0 Tg a⁻¹ against rice at 13.7, so coal is the largest anthropogenic
sector nationally. That is in the introduction because the domain contains a
coalfield that neither predictor represents, and it would be strange to reach §3
of the discussion before the reader learns that the largest national sector is
present and unmodelled. The records had the figure in the region grounding and
nothing had decided whether it was introduction or discussion material.

### Numbers not marked

Six of this section's numbers carry resolvers. The unmarked ones are literature
figures resolved by citation — the 30 percent inventory spread and its fifteen
Tg, the 60-and-30 percent regional concentration, the seven sectoral totals, the
26 percent aquaculture share, the 53-to-69 percent posterior uncertainties, the
0.5 sensitivity threshold, and the R² 0.98, R² 0.63 and 13.26 ppb downscaling
figures — together with the year 2018, the date 30 April and the section
numbers. **The eight-month record length and the 30 April start are derivable
from the composite and are exempted in the methods draft's own list**, which is
where that convention is set.

### What the introduction does not do

It states no result that belongs to the abstract, reviews no literature beyond
what §3's gap argument needs, and gives the 2023 thesis one sentence and a
pointer.
