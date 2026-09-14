# What set the paper needs

Assessed 14 September 2026, read-only. Thirteen figures exist, built in two
phases under two framings, and nobody had asked what set the *paper* needs.
This inverts the question: not which planned figures to build, but which
findings need seeing, and what would show them. Existing figures are candidates
on the same footing as unbuilt ones, and some lose.

Assessed against the capability paper. Emissions work is a separate project and
nothing here is judged against it.

`figures/README.md` remains the inventory — what exists, what is planned, what
each answers to in the 2023 thesis. This file is the judgement.

---

## 1. The findings, and whether they need seeing

The test: does the finding have a **shape** — a distribution, a spatial
pattern, a relationship, a trajectory, a comparison across many cases. A
finding that is one number or a short ordered list does not need a figure
however important it is.

### Needs seeing, and has a figure that shows the finding

| finding | figure |
|---|---|
| Coverage saturates: 36 granules reach 71.5 % of cells, 187 more add 19.1 points | `coverage_saturation_2018` |
| The field's spatial pattern, and where the 97 holes are | `methane_composite_2018`, `study_area` |
| **A land-cover fit produces a flat field**: the observed field spans 106.1 ppb and impervious's field 42.7 on one scale | `residual_field` (a) vs (b) |
| **The residual keeps its spatial structure**: Moran's *I* 0.646 against 0.709 observed | `residual_field` (c) |
| The fits' shapes: impervious's cloud is flat where wind's is diagonal | `observed_predicted` (a)–(d) |
| Impervious and albedo co-vary at Spearman +0.761 and the association survives no control | `albedo_collinearity` |
| Held-out skill decays with buffer radius, and the null dies at 50 km where its neighbours go | `buffered_decay` |
| **No cell approaches an averaging-kernel sensitivity of 0.5 at any tested magnitude** | `capability` (b) |
| Expected DOFS against assumed domain total, with the threshold crossings | `capability` (a) |

### Needs seeing, and the figure shows something adjacent — §1c's middle category

**This is the category that matters, and it has four members.**

1. **The GAIA–GISA disagreement.** `urban_change` panels (a) and (b) are the two
   products as categorical maps. The finding is that they disagree; two
   similar-looking maps cannot show disagreement. Panel (c) shows it as
   trajectories and is the only panel that does. See §2d.
2. **The field's distribution.** §2.1 reports a 106.1 ppb span and a 14.86 ppb
   between-cell standard deviation, and the results table cites
   `methane_composite_2018` for "§2 the field". That figure shows the field's
   *map*, not its distribution. The distribution is three numbers and **needs no
   figure** — so this is a citation to fix in prose, not a figure to build.
3. **The sampling-composition confound.** §4.2 rests on observation days
   differing by up to 228 across cells. `methane_composite_2018` panel (b) shows
   sounding *counts*, which is adjacent: a cell with 200 soundings on 12 days is
   not a cell with 200 soundings on 200 days. The count map is read as if it
   were the day map.
4. **The capability claim's per-cell distribution.** `capability` panel (b)
   summarises 926 cells as three points — median, 90th, best. The finding is
   that *no* cell reaches 0.5, and three points at a decade below the line carry
   it, but the distribution behind it is not drawn.

### Needs seeing, and has no figure at all

| finding | shape |
|---|---|
| **The spread belongs to the evaluation, not the predictor** — 126 specifications, 0 both positive and beating their own null, scheme moving the result 0.1764 against the predictor's 0.0943 | an ordered curve over 126 cases with membership beneath |
| **The sources are interspersed at the cell scale** — seven sectors in the same cells, which is the identifiability limit's whole basis (the count said six until 14 September 2026; the drafts say seven) | a spatial pattern, six layers on one lattice |
| **Residual autocorrelation against block size** — 10 model-field half-sill ranges against a 111.2 × 95.0 km block, 4 still correlated at a block width (verified against the artefact's own verdict column) | 10 values against two reference lines |
| **Fold geometry** — which cells fall in which block and province, and how far each held-out cell sits from its nearest training cell | a spatial pattern; and `buffered_decay`'s caption says explicitly that it cannot answer this |
| The seasonal cycle against the monthly sounding distribution and the rice calendar | three series on one time axis |

### Important, and needs no figure — stated so it is not built later

* **The attenuation bound.** Its headline is a margin of 5.6. I checked whether
  the sweep behind it has a shape: the artefact carries λ_min, the factor, the
  required error share and the multiple — **four scalars and no swept curve**.
  There is nothing to plot. A sensitivity curve of R²-bound against assumed
  error share could be drawn, but it would be a straight-ish line through a
  point already stated, and the finding is the *margin*, which is a number.
* **The equivalence result.** 0 of 36 outside the bounds, rice 24 of 24 within,
  impervious 7 of 12. That is a table (§4c).
* **The grid-resolution verdict.** Five resolutions by six quantities. A table.
* **The preprocessing sensitivities.** Precision removes nothing; the albedo
  floor drops 174 cells; destriping offsets span −15.27 to +12.77 ppb. A table,
  and the one number with a shape — the 200 per-column offsets — is a
  first-order estimate the record deliberately declines to lean on.
* **Effective degrees of freedom** — 32.8 of 926. One number.
* **The pre-filter rejection rates** — 89.44 % no-retrieval, 49.97 % threshold.
  Two numbers.
* **The reference audit** — 12 citations of 197. A number and a list.
* **Reproducibility** — 71 recipes, byte comparison. Documentation, and
  `framework_pipeline` already draws it.

---

## 2. The thirteen, individually

`shows what the caption says` is a correctness check; `paper needs it` is
against the capability paper; `belongs` is the section.

| figure | caption correct | paper needs it | belongs | density |
|---|---|---|---|---|
| `study_area` | yes | yes — the domain, terrain and the absent-cell block | methods | 991-word block; lead 21 words is fine |
| `coverage_saturation_2018` | yes | yes — the only figure whose subject is the observing system | results §1 | fine |
| `methane_composite_2018` | yes | yes | results §2 | fine, the lightest of the set |
| `landcover_native` | yes | **no, for the main text** — provenance, not a result | supplement | 2 baked text blocks |
| `urban_change` | yes, but see §2d | **panel (c) only** | errata / supplement | 4 baked lines |
| `landcover_regional` | yes | **no, for the main text** — provincial breakdown and the unclassified Anhui | supplement | 2 baked blocks |
| `observed_predicted` | yes | **yes — the central results figure** | results §3.3 | 5 baked lines; too dense for a results figure |
| `residual_field` | yes | **yes** | results §3.3 | **7 baked lines; the densest in the set** |
| `framework_pipeline` | yes | no | supplement | documentation, density appropriate there |
| `framework_reproduction` | yes | no | supplement | 917-word block, appropriate there |
| `albedo_collinearity` | yes | yes — the confound the result must survive | results §4.1 | lead is **52 words**, the longest; 2 baked blocks |
| `buffered_decay` | **yes, and carefully** — it disclaims the geometric reading of its own shaded band in four sentences | yes | results §5.2 | the disclaimer is necessary and long |
| `capability` | yes | **yes — the contribution's own figure** | results §6 | fine; (a)'s "an input, not a result" label is exemplary |

**One systematic density property.** Nine of the thirteen modules call
`figtext`, so the explanatory paragraph is **rendered inside the image**:
`residual_field` bakes seven lines, `observed_predicted` five,
`urban_change` four. In a manuscript that text belongs in the caption, where a
copy-editor can set it and a reader can enlarge it. **This is a rebuild
property, not a relocation one**, and it applies to every figure going to the
main text.

**One structural defect in the caption file.** `buffered_decay` and `capability`
have captions but **no `###` heading** — they were appended into the
`albedo_collinearity` section, which is why that section reads as 2,418 words.
The inventory test checks figures against tables and does not check that each
figure has a caption heading, so nothing caught it.

### 2d. `urban_change`

**The judgement asked for, and it agrees with the brief on the diagnosis and
splits rather than drops.**

Panels (a) and (b) are the two products drawn as first-year-of-imperviousness
classes. At four-province extent both are overwhelmingly the "land below 25 %"
class with city cores picked out, and they look the same. **The finding is that
they disagree — GAIA reproduced reaching 49.3 × 10³ km² in 2018 against GISA's
39.5, and growing ×3.01 against ×2.00 from 2000 — and side-by-side categorical
maps are the one form that cannot show it.** A reader must flick between panels and hold the difference in memory,
which is the definition of a figure whose finding has to be interpreted for
them.

Panel (c) carries **two** findings and both are real shapes: the thesis's
reported ×6.0 growth against the reproduced ×3.0, which is the errata's central
quantitative correction, and the GAIA–GISA divergence as two trajectories
that start with GISA higher and end with GAIA higher. The crossing the figure
draws near 2011 is where its straight 2010-to-2018 segments intersect and is
not a measured date; the products have no year between those two.

The threshold's cost — the 1/64° inking rule drawing the 2000 class at 0.73 of
true area and the 2019 class at 1.30 — is in the baked footnote. **That is a
quantitative caveat on panels (a) and (b) specifically**, and it is carried in
prose because the panels cannot carry it.

**Split.** Promote panel (c) to a standalone figure in the errata material,
where the ×6.0-against-×3.0 correction belongs. **Drop panels (a) and (b).**
Their only remaining function is showing where urban land is, which
`landcover_native` does at native resolution and the proposed predictor maps
would do on the analysis lattice. If the disagreement needs seeing it needs a
**difference** map — per-cell GAIA minus GISA fraction — and that is a different
figure, drawable from committed artefacts (`impervious_gisa_2018.csv` and the
grid's `impervious_fraction`). It is not on the build list below because the
disagreement's magnitude is already carried by panel (c) and decomposed in
`urban_disagreement_2018.csv`, and a paper does not need both.

---

## 3. The build list, derived

### Survives assessment and should be built

**A. The specification curve.** 126 specifications ordered by held-out R², with
membership dots beneath on five axes. Shows that **no specification is both
positive and beats its own spatial null**, and that the cross-validation scheme
moves the result nearly twice as much as the predictor. Reading it is
insufficient because the claim is about the *distribution over defensible
choices*, and a range quoted as "−1.04 to +0.14" invites the reader to pick an
end. Results §3.4. **Plots a committed artefact** —
`specification_curve_2018.csv` — so this is drawing, not analysis.

**B. The source map.** Where the seven sectors sit on one lattice: paddy,
aquaculture, wetland, landfill and wastewater points, urban gas as the
population surface, and the Huainan–Huaibei coalfield. Shows the
interspersed-source premise the identifiability limit rests on, which the paper
currently asserts in prose in both the introduction and the discussion.
Discussion §3. **Needs assembly, not fetching**: rice and impervious are
committed; the wastewater coordinates and coalfield extent are in the lead
register and not on disk, so a first version can draw four of six sectors and
say which two are named rather than drawn.

**C. The fold map.** Which cells fall in which block and province, and each
held-out cell's distance to its nearest training cell. Not redundant with
`buffered_decay` — that figure's caption states the distance "has never been
measured in this repository" and that the fold map is what would settle it. The
scratch figure of ~56 km median, with ~4 % of cells in the 150–200 km range, is
quoted nowhere because no registered script produces it. Supplement, or results
§5 if §5.3's bracketing is kept. **Needs new computation**: a distance
calculation and a registered script.

**D. The semivariogram ranges.** Ten model-field half-sill ranges against the
111.2 × 95.0 km block, showing the four that leave residuals correlated at a
block width. Reading it is insufficient because the finding is *which side of
the block width each model falls on* — a comparison across ten cases against a
reference. Supplement. **Plots a committed artefact**, `residual_range_2018.csv`.

**E. Predictor maps.** Impervious and rice fraction on the analysis lattice
beside the field. The one figure that shows what the association is a regression
*of*, and the results section currently opens §3 with no picture of its
predictors. Results §3, or methods. **Plots committed artefacts.**

### Assessed and not recommended

* **The seasonal cycle against the monthly distribution and rice calendar.**
  Carries three findings at once and they are all real — peak day 245.8, the
  October sounding spike, the middle-rice window. But **it serves the emissions
  question, not the capability claim**: the capability paper's use of the cycle
  is to deseasonalise, and §4.3 reports that doing so moved the association by
  0.009. A figure whose payoff is "and this changed nothing" earns a sentence.
  Build it in the emissions project.
* **A rice change series for 2000 and 2010.** Now possible with CCD-Rice. It
  answers the 2023 thesis's change question, and this paper is not a
  reproduction of that question — the errata is. Errata material at most.
* **The urban–rice overlay.** The 2023 thesis's central visual argument, never
  drawn regionally. **And it should stay undrawn in this paper**: the overlay
  asserts co-location as an explanation, and this paper's finding is that
  co-location does not produce a detectable association. Drawing the thesis's
  argument gives it visual force the analysis withdraws.
* **A land-change delta.** Where cover changed rather than what it was. Real,
  and it belongs to the change question this paper does not ask.
* **The hotspot analysis** (thesis Objective 3, never attempted). **Not a figure
  decision**: the reproduction has no hotspot analysis to draw, so this is an
  analysis proposal in a figure brief's clothing. If it were done it would bear
  on the emissions project, and the capability finding — that no cell is
  individually constrained — is an argument against hotspot attribution at this
  resolution rather than for drawing one.
* **The sampling-artefact map** (planned). Its count dimension is already
  `methane_composite_2018` panel (b). Its unique content is the **observation-day**
  dimension, which §4.2 needs and nothing shows. Worth building as a single
  day-count panel, supplement — but as a panel added to the composite figure
  rather than a figure of its own.

### 3c. The three still-planned figures

| planned | verdict |
|---|---|
| predictor maps | **survives** — item E above, and promoted from "drawing rather than analysis" to a main-text candidate |
| fold map | **survives** — item C. The brief's suspicion that it is redundant with `buffered_decay` does not hold, and `buffered_decay`'s own caption is why |
| sampling artefact map | **survives in reduced form** — one day-count panel, because the count panel already exists |

---

## 4. The proposed set

**Eleven in the main text**, inside the eight-to-twelve an ACP capability paper
carries.

| # | figure | section | state |
|---|---|---|---|
| 1 | `study_area` | methods | exists; rebuild to move baked text to caption |
| 2 | predictor maps | methods | **new (E)** |
| 3 | `coverage_saturation_2018` | results §1 | exists |
| 4 | `methane_composite_2018` + a day-count panel | results §2 | exists; **add one panel** |
| 5 | `observed_predicted` | results §3.3 | exists; rebuild for density |
| 6 | `residual_field` | results §3.3 | exists; rebuild for density |
| 7 | specification curve | results §3.4 | **new (A)** |
| 8 | `albedo_collinearity` | results §4.1 | exists; rebuild, shorten the 52-word lead |
| 9 | `buffered_decay` | results §5.2 | exists |
| 10 | `capability` | results §6 | exists |
| 11 | source map | discussion §3 | **new (B)** |

**The marginal two, named rather than left for someone else to cut.** If the
set must reach nine, drop **#3 `coverage_saturation_2018`** — its finding is a
saturation curve, which is a shape, but the paper's use of it is the single
number 90.52 % and a sentence about why a six-granule sample understated it —
and **#2 predictor maps**, which is orientation rather than evidence. Cutting
either weakens the paper; cutting anything else removes a finding.

### Supplement

`landcover_native`, `landcover_regional`, `urban_change` panel (c) rebuilt
standalone, `framework_pipeline`, `framework_reproduction`, the fold map (C) and
the semivariogram ranges (D). Seven.

### 4b. What the proposal costs

**Dropped: two panels.** `urban_change` (a) and (b). Nothing else is dropped —
the four figures leaving the main text go to the supplement, where three of them
already serve a reader who wants provenance rather than a result.

**Rebuilt: five**, all for the same reason — moving baked `figtext` into the
caption: `study_area`, `observed_predicted`, `residual_field`,
`albedo_collinearity`, and `urban_change` reduced to panel (c). Each is a
change to one module's text handling, not to its analysis, so each is hours
rather than days and none moves a number.

**New: four.**

| new figure | cost |
|---|---|
| A. specification curve | **lowest.** Plots `specification_curve_2018.csv` unchanged. One module, one recipe |
| E. predictor maps | **low.** Plots the analysis grid's two fraction columns on the lattice `fields.py` already draws |
| D. semivariogram ranges | **low.** Plots `residual_range_2018.csv` |
| C. fold map | **medium.** Needs a registered distance computation before anything is drawn; the number it would show is currently a scratch calculation quoted nowhere |
| B. source map | **medium, and partly blocked.** Four of six sectors from committed artefacts; the wastewater coordinates and coalfield extent need a fetch, and the coal layer needs a form submission recorded in `notes/dataset-leads.md`. Draw four, name two |

**One panel added**: an observation-day count beside the composite's sounding
count.

### 4c. Better as tables

* **The equivalence bounds.** 36 rows of field × predictor × weighting with
  three outcomes. The finding is the rice-impervious asymmetry, which a table
  states in two lines and a figure would make a reader count.
* **The grid-resolution comparison.** Five resolutions by six quantities, and
  the point is that effective *n* does not move while everything else worsens.
  A table shows the flat column; a figure would draw five points on a line.
* **The preprocessing sensitivities.** 168 rows. The finding is which of four
  omissions changes anything, which is a four-row summary table.
* **The baseline suite.** Already a table and should stay one —
  `observed_predicted` panel (e) carries the shape and the table carries the
  numbers, which is the right division.

### 4d. Does the set tell the argument in order

Read as captions alone, the sequence is: this is the domain → these are the
predictors → this is what the instrument delivered → this is the field → a
land-cover fit produces a flat field and its residual keeps its structure → no
defensible specification changes that → the obvious confound is measured and
does not explain it → the cross-validation schemes bracket rather than
disagree → the observations cannot constrain a cell at any plausible magnitude →
and the sources are interleaved, so a better prior is what attribution would
need.

**That follows.** Two gaps in it, both named:

1. **The identifiability limit's independence from the information limit** is the
   contribution's own pairing — "the second is untouched by any improvement to
   the first" — and **no figure carries it.** Figures 10 and 11 each carry one
   limit; nothing shows that they are independent. I considered proposing a
   schematic and rejected it: the independence is an argument, not a
   measurement, and a schematic would give it the appearance of one. **It has to
   be carried by prose, and a reader looking only at figures will not get it.**
   That is the honest statement of the gap.
2. **Nothing in the main-text sequence shows the 2023 thesis's result being
   corrected.** `urban_change` panel (c) does, and it is in the supplement under
   this proposal. That is the right place for a reproduction's errata, but it
   means the figure sequence does not tell the reader this paper revises
   anything — which matches the framing, where the land-cover result is the
   assessment's occasion rather than its contribution.
---

# The case study section, assessed 14 September 2026

The set is being worked section by section and this is the first. Part 1 of the
brief was locatability, because the design depends on it, and it changed the
design substantially.

## What can be located, and at what precision

**Seven sectors, not six.** `notes/draft-discussion.md` says "seven sectors
present in this domain" and the introduction lists them: paddy rice, freshwater
aquaculture, natural wetland, landfills, wastewater treatment, urban gas
distribution and coal mining. The "six" in §3 of this file above was wrong and
is corrected here.

**Two tiers of evidence, and they must not share a map.** A facility coordinate
and an inventory's 10 km allocation are different objects, and drawing them
together would imply a precision that does not exist.

### Tier A — measured extent or facility location

| sector | form | resolution | year | state |
|---|---|---|---|---|
| paddy rice | area | 30 m | 2018 | on disk (NESDC, CCD-Rice, GloRice) |
| aquaculture | area, polygons | 10 m | **2015 and 2020, not 2018** | on disk |
| urban gas | area, **proxy only** | 30 m | 2018 | on disk (GAIA, GISA, GISA-new). Impervious surface is a proxy for gas distribution, not the sector |
| coal mining | **points** | per mine | **2018** | **fetched 14 September 2026**: 116 mines inside the lattice box with per-mine monthly 2018 emissions |
| wastewater | **points** | per plant | mixed | **fetched**: 422 in the four provinces, 28 underground and 394 aboveground |
| landfills | — | — | — | **not located** |
| natural wetland | — | — | — | **not located** |

*Five of seven, with two caveats that bear on the drawing.* The pond product
brackets 2018 rather than covering it. And the wastewater file's
`Construction_Year` is populated for the 201 underground plants and **empty for
all 2,464 aboveground rows**, so of the 422 in-domain plants only the
underground ones can be filtered to 2018 — 11 of the 35 in the lattice box were
built by then. **A 2018-framed figure cannot honestly draw all 422.**

### Tier B — one inventory prior, one resolution

CHN-CH4, per-sector gridded emissions for China, CC BY 4.0, fetched
14 September 2026. It covers **five of the seven**: rice, coal, oil and natural
gas (the urban-gas proxy), landfills and wastewater. **The two it omits are
aquaculture and wetland** — which are exactly the two the drafts already name as
absent from the priors this field uses.

In-domain 2018, as a share of the national total: rice 32.7 %, wastewater
33.6 %, landfills 18.8 %, coal 13.6 %, oil and gas 1.1 %. Within the domain the
five split coal 36.9 %, rice 30.6 %, landfills 15.7 %, wastewater 15.7 %, oil
and gas 1.0 %.

**Union of both tiers: six of seven locatable in some form. Only wetland is
absent from both, and landfill exists only as a prior.**

## What a reader must know first, and whether it needs seeing

Derived from the drafts rather than from the brief.

| must know | needs | why |
|---|---|---|
| where it is | **seeing** | a reader cannot place four Chinese provinces from a name |
| what the terrain does | **seeing** | relief explains the composite's 97 holes, and the holes are a result |
| that seven sources overlap **in the same cells** | **seeing** | it is a spatial property and the identifiability limit's whole basis |
| why methane here — 60 % of emissions on under 30 % of land | **reading**, with an inset at most | two numbers about the country, not a property of the domain. It is national context and it belongs in a sentence |
| that the domain is 26 % of China's aquaculture area | **reading** | one number |
| the eight-month record and the 30 April start | **reading** | already in the methods |

**The one item argued down**: the national-context claim. It is the paper's
reason for choosing the region and it is two numbers. An inset showing the three
sub-national regions would be honest but it would occupy a panel to carry a
sentence, and the figure it would sit in is already the densest in the set.
**Reading, not seeing** — and if it is drawn at all it is a locator inset, which
`study_area` already has.

## The proposal: two figures

### Figure 1 — `study_area`, rebuilt and reduced

**Keeps**: relief, province boundaries, the coastline, the locator inset, and
the analysis-cell detail box. **Sheds**: the four city labels, which are
orientation a reader gets from the provinces, and the baked explanatory
paragraph, which moves to the caption. That is the density rebuild §2 of this
file already called for, and nothing from the source distribution belongs in it
— adding sources would put a 10 km inventory and a 30 m raster on a relief map
and make three claims in one frame.

Methods, or introduction if the section is written as a case study.

### Figure 2 — the source distribution, drawn as a prior and labelled as one

**Not a map of where the sources are. A map of where an inventory puts them**,
which is the honest object and, more importantly, **the object the paper's
argument is actually about**: the identifiability limit says attribution derives
from the prior's spatial distinctness. So drawing the prior is drawing the thing
the limit is about, rather than an approximation to it.

Five sectors from CHN-CH4 on one 10 km grid, with the two it omits named in the
caption and **not drawn**. Coal's 116 mine points and the underground
wastewater plants existing in 2018 can be overplotted as a second tier if the
panel can carry it without implying the grid is that precise; if not, they go in
a supplementary panel.

**And the figure carries a measured result rather than only a depiction.**
Landfill and wastewater in this inventory have an **identical non-zero footprint**
— the same 6,416 in-domain cells — and correlate at **+0.80**, because both are
allocated on the same population surface. Every one of the 4,797 in-domain rice
cells also carries landfill emissions. Meanwhile landfill against rice
correlates at −0.06 and against coal at −0.21. **So the sectors share support
almost completely while their magnitudes vary independently**, which is a
sharper statement than "interspersed" and is the mechanism that makes
attribution hard: a cell's mix cannot be read from any one proxy.

## 2e. Where the source map sits

**The introduction, as the brief proposes, and the reason is not the one
offered.** My earlier assessment put it in the discussion because that is where
the identifiability argument is made. The better argument for the introduction
is that **the figure is now a measurement and not an illustration.** It shows
that two sectors in a real prior share a footprint at r = 0.80 — which is
evidence, and evidence that the introduction needs, because §3's gap argument
asserts that identifiability is a property of real priors that a simulation
cannot supply. That assertion currently has nothing behind it in the paper.

The discussion then refers back rather than drawing again, which is the
ordinary use of an introduction figure.

*One thing this changes upstream.* §3 of this file listed the source map as
discussion material and "partly blocked, draw four, name two". Both are
superseded: it is introduction material, and it draws five of seven from one
consistent source with two named.

## What the section cannot establish

* **Natural wetland cannot be drawn at all.** WetCHARTs needs a NASA Earthdata
  login and CHN-CH4 has no wetland sector, being an anthropogenic inventory.
  The paper's claim that rice and wetland priors overlap therefore rests on
  WetCHARTs' own documenting paper and cannot be shown over this domain.
* **Landfill cannot be drawn as locations.** No deposited Chinese landfill
  location dataset was found on Zenodo, figshare, Science Data Bank or via
  OpenAlex; the 300-site database stays paywalled; the GHGSat plumes are 2021
  and 2022 with none in 2018; and Shanghai Laogang is named in
  `notes/grounding-urban.md` **without coordinates**, from operator
  documentation. So the brief's "a single point" is optimistic — there is no
  point.
* **Aquaculture cannot be drawn for 2018**, only bracketed by 2015 and 2020.
* **The urban gas sector is drawn by proxy**, as impervious surface or as the
  inventory's oil-and-gas grid, and neither is gas distribution.

### What a computation could establish instead

The interleaving claim is the case in point. It is currently a literature-backed
assertion — "interspersed at the scale of the analysis cell" — and it is
**measurable over this domain from what is now on disk**: the footprint overlap
and the magnitude correlations above are that measurement, and they say something
the literature does not, because they are about this prior over these cells.
Two further quantities are computable and are not yet: each sector's share of
in-domain emissions aggregated to the **0.25 degree analysis lattice** rather
than the 10 km inventory grid, and the number of analysis cells carrying more
than one sector above a stated threshold. **That second number is the
interspersed-source claim as a single statistic**, and it would replace a
citation with a measurement.
