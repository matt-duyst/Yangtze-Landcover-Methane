# The register read as a reference list

Audited 14 September 2026. `notes/references.md` is the register: what this
project consulted, grouped by role, 199<!--#register.entries--> entries. A manuscript's reference list
is a different object — what the paper cites — and nothing had ever measured
which subset that is. This file measures it, so the judgement conversation
about what the reference list *should* contain has something to work from.

The mechanical half regenerates: `data/processed/reference_use_2026.csv`, from
`scripts/audit_reference_use.py`, one row per entry with where it is cited. The
recipe is deliberately coupled to the drafts, so a draft gaining a citation
fails the byte comparison until the audit is regenerated.

**Nothing here proposes removing an entry.** Entries cited only in a grounding
record are the project's working literature and the record of what was
consulted is worth keeping whether or not a manuscript cites it.

---

## 1. The finding that matters: the drafts are almost entirely uncited

**Four drafts contain 12<!--#register.draft_cited--> formal citations between
them.** Not twelve per section — twelve in total, of which ten are in the
methods.

| draft | formal citations | named without a year |
|---|---|---|
| introduction | **0** | 0 |
| methods | 10 | Moran, Pontius and Millones |
| results | 1 | Moran, Clifford and others |
| discussion | 1 | Dutilleul |

No draft carries a DOI, a numeric citation, or a reference section. The
introduction — four sections of almost entirely external material — cites
nothing at all.

**This is not a formatting gap.** The drafts state literature findings in prose
and attribute them to nobody, so the sentences read as this project's own
claims. That is the defect most likely to reach a submission, because every
mechanism this repository has built checks *its own* numbers against *its own*
artefacts, and a claim about someone else's work is invisible to all of them.

### The twelve, with where they sit

| citation | register key | register section |
|---|---|---|
| methods:40 | `zhao2026subnational` | The region's synthesis anchor |
| methods:99 | `balasus2023blended` | The column field's own uncertainty |
| methods:230, 497 | `estrada2025imi2` | Information content |
| methods:245 | `gong2020gaia` | Datasets used |
| methods:247 | `huang2021gisa` | Datasets used |
| methods:287 | `xie2025glorice` | Datasets used |
| methods:420 | `clifford1989correlation` | Effective degrees of freedom |
| methods:421 | `dutilleul1993modifiedt` | Effective degrees of freedom |
| methods:554 | `wang2026usurban` | The urban layer |
| methods:568 | `desjardins2018reconciling` | The cross-layer synthesis |
| results:117 | `schutgens2017representativeness` | The column field's own uncertainty |
| discussion:269 | `zeng2021comment` | The rice-paddy exchange |

All twelve are **peer-reviewed papers**. No draft cites a preprint, a dataset
record, a standard, a manual or any other grey source — so the ACP constraints
in §3 below bind on the working literature and not, yet, on the paper.

### Two named without a year

`moran1950` (methods:416, results:169) and `pontius2011deathtokappa`
(methods:632) are named in prose — "Moran's *I*", "Pontius and Millones's
decomposition" — with no year. They are attributions already and a manuscript
must turn each into a citation.

---

## 2. The uncited claims, which is the list to work from

Grouped by draft. Each is a claim about something this project did not measure,
stated with no attribution. Where the register already holds the source, the fix
is mechanical; where it does not, a source has to be found.

### Introduction — every external claim, because it cites nothing

**Numeric:**

* the ≥30 percent spread between Chinese bottom-up inventories, and its ~15 Tg
  — register has it (`zhong2026groundvalue`)
* 60 percent of emissions in three sub-national regions on under 30 percent of
  the land — `zhao2026subnational`, which *is* cited in the methods and not here
* the assembled national prior: coal 21.0, rice 13.7, wastewater 9.5, livestock
  8.2, landfills 5.2, wetlands 2.0, lakes and aquaculture 1.3, against 64 Tg a⁻¹
  anthropogenic — `zhong2026groundvalue`
* 26 percent of China's aquaculture area in the four provinces — in the
  aquaculture section of the register, uncited in any draft
* posterior uncertainties of 53 to 69 percent for rice, lakes and wetlands
* the 0.5 averaging-kernel sensitivity threshold
* R² 0.98, R² 0.63 and RMSE 13.26 ppb for the Arabian Peninsula downscaling —
  `arabianpeninsula2025`

**Prose:**

* methane as the second-largest anthropogenic contributor to present-day
  warming, and the one with the shortest response time — **no register entry
  obviously supplies this**
* that column methane over rice regions correlates with paddy extent and has
  been read as evidence of rice emissions
* the transport-decomposition contest across four regions — `zeng2021comment`,
  cited in the discussion and not here
* the 2018 tower inversion finding agricultural soils dominant —
  `huang2021yrdinversion`, cited in no draft
* frequent shortwave-infrared gaps under monsoon cloud
* the capability literature's vocabulary — "instrument precision, pixel
  resolution, measurement frequency, and degrees of freedom for signal" — which
  is the paper type the framing claims membership in

### Methods

* the Level 2 record beginning 30 April 2018 and the product's own recommended
  variable — product documentation, which is grey
* the blended product's 11.9 ppb against 14.5 ppb single-retrieval precision —
  `balasus2023blended` is cited at line 99 and these figures appear later
  without re-attribution
* the published albedo floor of 0.05 and the blended-albedo ceiling, and the
  under-10 ppb precision filter — the preprocessing-chain section, uncited
* the buffered cross-validation and spatial-block literature — five register
  entries, none cited
* Olofsson's recommendations and the fractional-cover assessment frame — five
  entries across two sections, none cited

### Results

* the representativeness quotation and argument — `schutgens2017representativeness`
  *is* cited here, and it is the one place a draft quotation carries its source

### Discussion

* the tower inversion, twice more — `huang2021yrdinversion`
* the within-class ratio of 197 between pond types
* WetCHARTs' own documenting paper, including the quotation "has yet to be
  consistently addressed" — **an unattributed direct quotation**
* the closed-form averaging-kernel estimate and the 0.35 / 0.45–0.87 posterior
  correlation contrast — `estrada2025imi2` and `wang2026usurban` are cited in
  the methods for these and not here
* the Arabian Peninsula downscaling again
* the tip-and-cue published route — three entries, none cited
* the isotope endmembers: rice at about −61 ± 4‰ δ¹³C, waste at −56.1 ± 2.4‰,
  and the 2026 South Asian campaign's −53.8 ± 0.8‰ and −311 ± 6‰
* the published tool's free preview run

---

## 3. The ACP constraints

### Preprints — nine, and three have been published

ACP requires published, accepted, or a preprint with a DOI. All nine have DOIs,
so none is disqualified; three are **superseded**, and a superseded preprint
citation is a defect a reviewer notices.

| entry | status on 14 September 2026 |
|---|---|
| `nab2021sensitivity` | **published**: *Global Epidemiology* 3, 100067 (2021), `10.1016/j.gloepi.2021.100067` |
| `boulesteix2012plea` | **published**: *PLoS ONE* 8, e61562 (2013), `10.1371/journal.pone.0061562` — **and with three authors where the preprint entry carries two** |
| `lee2025multitab` | **published**: ACM SIGKDD proceedings, 9278–9289 (2026), `10.1145/3770855.3817455` |
| `cohen2016equivariant` | published at **ICML 2016**, which registers no Crossref DOI, so the arXiv DOI remains the only citable identifier |
| `azulay2018invariance` | published in **JMLR**, which registers no DOI either |
| `kluger2025nonuniform` | still a preprint |
| `shirota2026designppi` | still a preprint |
| `long2026urbanpreprint` | still an EGUsphere discussion paper |
| `montenegro2025capability` | still an EGUsphere discussion paper |

**None of the nine is cited in any draft**, so no preprint is load-bearing for
the paper *as drafted*. Two become load-bearing the moment the introduction is
cited properly: `montenegro2025capability` is the capability-literature anchor
that §3's gap argument rests on, and it is a discussion paper.

*One near-miss worth recording.* A title search for Cohen and Welling returns
`10.3390/sym18060983` in *Symmetry* — "Symmetry-Preserving Pruning of Group
Equivariant Convolutional Networks", by different authors, which **cites** the
preprint rather than being it. Accepting it would have been the wrong-paper
error this register was built to prevent.

### Grey literature — where no formal alternative exists

| grey entry | formal alternative? |
|---|---|
| ISO 5807:1985, flowchart symbols | **No.** A standard has no paper. Cited for the diagram convention; a manuscript would cite it as a standard or not at all |
| Chaudhuri (2020), textbook | **No**, but a textbook is formal literature, not grey |
| *Atmospheric Chemistry and Physics* review criteria | **No**, and it would not appear in a reference list — it is a policy page the framing has to satisfy, not a source |
| *Scientia Agricultura Sinica* (2026) | Not grey. A peer-reviewed paper whose publisher will not negotiate BibTeX |
| the S5P CH4 product specifications (`esa2019s5pch4`, `esa2021s5pch4`) | **Partly.** `lorente2021tropomi` and `schneising2026wfmd` describe the retrieval; neither describes the file format or the variable set the methods section relies on |
| the blended product's user manual | **No.** `balasus2023blended` describes the correction, not the product's file layout — as anticipated |
| IMI documentation | **Yes.** `estrada2025imi2` is the GMD paper for IMI 2.0 and is already the cited form in the methods — as anticipated |

**Load-bearing grey, meaning a draft claim rests on it:** the S5P product
specifications, for the methods' statements about the record's start date, the
recommended variable and the quality-flag semantics. Those are claims about the
product that no paper in the register makes. Everything else grey is either
cited only in a grounding record or, like the ACP policy page, would never be a
reference.

### Datasets and software — 15<!--#register.datasets--> entries for a data availability statement

`notes/paper-target.md` records the data availability statement as one of three
missing sections. These are what it should be written from, and **none is cited
in any draft**, which is correct: a dataset belongs in that statement, not in a
reference list.

Eight dataset records: `shen2023ricedata`, `xie2024gloricedata`,
`gong2024gaiadata`, `ifpri2019spam2000`, `ifpri2019spam2010`, `esa2021s5pch4`,
`esa2019s5pch4`, `liu2023ricecalendardata`. Two dataset papers:
`zhou2024wwtp`, `zhang2025cmab`. Five deposits: `han2021apra500data` (fetched),
and `hou2025nericedata`, `shahzadi2026fuseddata`, `bloom2021wetchartsdata`,
`sherwood2020signatures` (not fetched).

---

## 4. Shape

**Reference count as drafted: 12<!--#register.draft_cited-->.** A typical ACP article carries 40 to 80. The
gap is not a shortage of consulted literature — 197 entries — but that the
drafts do not cite it.

**Method-literature share.** The register is about 28 percent method literature
overall. Of the twelve draft citations, **three are method literature**:
`clifford1989correlation` and `dutilleul1993modifiedt`, both from *Biometrics*,
and `schutgens2017representativeness`. So the drafted share is about a quarter —
close to the register's, not lower. **Two of the twelve come from a biology and
statistics journal**, which is the borrowing a reviewer in this field would
notice, and it is the spatial-statistics correction rather than anything exotic.

The heavier borrowings the register carries — equivalence testing from biology,
prediction-powered inference from statistics, buffered cross-validation from
ecology, and four diagram sources from outside the earth sciences entirely — are
cited in **no draft**. They will be once the methods section is cited properly,
and that is the point at which the borrowing becomes visible.

**Subject areas with entries and no draft citation at all**, largest first: the
methane layer's target and observing chain (11), aquaculture (7), assessments
and instrument documentation (6), water management (6), wetlands and urban gas
and transport (6), model class and resolution (6), the rice products (6),
methods applied (5), findings relied on for the region (5), spatial
cross-validation (5), water regime and the diurnal cycle (5).

**The inversion of what the framing claims.** The paper presents itself as a
capability assessment, and the register's *Capability assessment as a paper type*
section holds three entries of which **none** is cited in any draft. The region
is cited thinly too: of the regional sections, only `zhao2026subnational` and
`zeng2021comment` appear. So as drafted the paper cites its statistical method
more thoroughly than either the literature it claims membership in or the region
it is about.

---

## 5. Entries cited nowhere

Three, verified by hand against prose, code and configuration:

* `correll2018vsup` — value-suppressing uncertainty palettes, from
  human–computer interaction. Considered for the figure set and not adopted.
* `dogniaux2025ghgsat` — the GHGSat global waste survey paper. Its plume deposit
  is in `notes/dataset-leads.md`; the paper is cited by no record.
* `huang2019yrdtopdown` — an earlier top-down study of this region, superseded in
  use by the 2021 tower inversion.

A first mechanical pass reported 42, then 8. The difference is that grounding
records and manifests often cite by bare DOI rather than by author, that code
cites the colour-map paper and no prose does, and that a capitalised ASCII key
cannot spell Milà or ESA. The script now searches DOIs and code paths and keeps
the hand-verified list as the authority, reporting any disagreement.

## The reference list the expanded claim set implies, 14 September 2026

The audit above asked which register entries the drafts cite. This section asks
the harder question the claim inventory made answerable: **if every claim that
needs a citation got one, how large would the reference list be, and what would
it be made of?**

**How the drawn set was derived, and why it is a floor.** Two inputs, both
committed: the 125 <!--#claims.cited--> numeric claims in
`data/processed/claim_inventory_2026.csv` that resolve to a literature figure
rather than to an artefact, and the prose claims this audit's own §2 listed as
needing support. Together they name **46** register entries. That is a floor
rather than a count, because it includes only entries some pass has already
named; a claim whose support has not yet been looked for adds to it. **These
derived counts are checked by review, not by a test** — the derivation is
stated so it can be redone, but no resolver produces it.

The 46 split in two, and the split matters because the two halves go to
different places in a submission:

| | Entries | Goes in |
|---|---|---|
| literature | 31 | the reference list |
| datasets and deposits | 15 <!--#register.datasets--> | the data availability statement |

So the **reference list would be about 31 entries**, against the
12 <!--#register.draft_cited--> the drafts cite today and
199 <!--#register.entries--> in the register. That is below what an ACP article
typically carries, and the reason is a property of the work rather than a
defect: this is a capability assessment resting on its own measurements, so most
of its numbers are measured and only 125 <!--#claims.cited--> of them are
quoted from anyone.

### What the list is made of

Of the 31 literature entries, **22 are peer-reviewed papers and 9 are not** —
29 percent. That is the number a handling editor will notice, and §4 below
takes it apart.

**Method literature is 10 of the 31, 32 percent**, against 23 percent of the
register as a whole: `arabianpeninsula2025`, `boulesteix2012plea`,
`clifford1989correlation`, `correll2018vsup`, `dutilleul1993modifiedt`,
`kluger2025nonuniform`, `lee2025multitab`, `nab2021sensitivity`,
`pontius2011deathtokappa`, `shirota2026designppi`. The drawn set is therefore
*more* method-heavy than the register it comes from, which is the opposite of
what a register built mostly from domain reading would suggest. It follows from
what the paper argues: the load-bearing choices here are the effective degrees
of freedom, the disagreement decomposition and the errors-in-variables bound,
and each needs its own citation.

### Concentration, and the entries that carry it alone

The 119 cited claims resolve to only **37 distinct literature figures**, and the
distribution is skewed: the **top four figures carry 57 of the 124**. The
largest, at 21 claims, is the introduction's inventory-spread figure of at least
30 percent; then the published precision filter under 10 ppb at 14, the
averaging-kernel sensitivity threshold at 12, and the transport error standard
deviation at 6.

**14 of the 37 are quoted once**, and each is a single point of failure — if the
source is misread, one sentence is wrong and nothing else catches it. Eleven of
the 14 are a single block: the national prior's per-sector shares (coal,
livestock, landfills, wastewater, wetlands, lakes and aquaculture) and the
posterior uncertainty bounds, all in the introduction. They come from the same
small number of works, so the single-quotation risk is concentrated in one
passage rather than spread, which makes it cheap to check and worth checking
once carefully.

### Entries bearing on claims nobody made

Three register entries are cited nowhere and support no claim in any draft:
`correll2018vsup`, `dogniaux2025ghgsat` and `huang2019yrdtopdown`. Two of the
three are not waste. `correll2018vsup` is method literature for a figure
technique, and it appears in the method-literature list above because the
drawn set needs it if the technique is used. `dogniaux2025ghgsat` documents a
wastewater plume near Shanghai that was filtered from its own analysis, which
is a fact about an instrument's coverage that the discussion could use and does
not. `huang2019yrdtopdown` is a top-down study of this exact domain and its
absence from the drafts is the one that should be explained or fixed.

## 4. Preprints and grey literature under the expanded list

ACP allows a preprint to be cited when it carries a DOI, and grey literature
only where no formal alternative exists. The 9 non-peer-reviewed entries in the
drawn set are three different situations and only one of them is a problem.

**Superseded, and the published version must be cited (3).** All three were
checked and corrected on 14 September 2026 and the register records the
replacement:

| Entry | Published as |
|---|---|
| `boulesteix2012plea` | *PLoS ONE* 8, e61562 (2013), `10.1371/journal.pone.0061562` |
| `lee2025multitab` | *Proc. 32nd ACM SIGKDD*, 9278–9289 (2026), `10.1145/3770855.3817455` |
| `nab2021sensitivity` | *Global Epidemiology* 3, 100067 (2021), `10.1016/j.gloepi.2021.100067` |

One of these carries a second defect worth keeping in view: the published
`boulesteix2012plea` has **three authors where the preprint entry has two**,
Boulesteix, Lauer and Eugster. A truncated author list survives a DOI check,
because the DOI resolves correctly to the preprint.

**Preprints with a DOI, in open discussion (2).** `long2026urbanpreprint`
(`10.5194/egusphere-2026-2570`, CC-BY-4.0, discussion opened 20 May 2026) and
`montenegro2025capability` (`10.5194/egusphere-2025-5923`, discussion opened
23 December 2025). Both are ACP-admissible as cited. `long2026urbanpreprint`
supplies two statements found peer-reviewed nowhere, so it also meets the
narrower grey-literature test of no formal alternative existing.

**arXiv only, with no supersession check (4).** `azulay2018invariance`,
`cohen2016equivariant`, `kluger2025nonuniform` and `shirota2026designppi` are
labelled `preprint` with no replacement recorded. **The supersession sweep was
incomplete.** It resolved the three entries above and did not run over these
four, and age is the reason to care: `kluger2025nonuniform` is from January 2025
and `shirota2026designppi` is weeks old, so an arXiv-only record is unsurprising
for both, but `cohen2016equivariant` and `azulay2018invariance` are eight and
ten years old and both are well-known machine-learning papers. **An arXiv-only
entry that old is far more likely to have a published version than not.** This
was not verified here, which needs a network check the audit could not make, and
it is the one open defect in the reference list rather than in the data.
