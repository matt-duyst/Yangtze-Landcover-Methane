# Reference register

Every source this repository cites, verified against the DOI registries on
3 September 2026, extended on 9 September 2026 when the figure set gained its
first diagrams, again on 10 September 2026 when nineteen literature
searches over the study region were recorded, and again on 14 September 2026
when the rice layer was given a grounding record and all three layers were given
review-level anchors, and extended the same day with the rice layer's second
literature block, the methane layer's record and the cross-layer synthesis. The register exists because
citations here were scattered
across `config/sources.yml`, `data/manifest.json`, `notes/decisions.md`,
`ERRATA.md` and three READMEs, in four different formats, so nobody could say
how many sources the work rested on without grepping for them.

Each entry carries the citation as the registry gives it, not as the depositing
platform gives it. That distinction is not pedantry: it has already produced two
errors, both recorded in `notes/decisions.md`. GloRice was cited as "Zhang et
al. (2025)" for a paper whose first author is Xie, read off a figshare record
listing two of six authors in reverse order. And a benchmark was attributed to
the TROPOMI/WFMD v2.0 paper, whose abstract describes quality filtering rather
than the albedo correction the benchmark was said to come from. A third
instance was met on 10 September 2026 and not acted on: the ChinaRiceCalendar
deposit's author field gives two of eleven authors with their given and family
names run together, and the paper's citation is carried instead.

`notes/references.bib` carries one hundred eighty-nine entries as BibTeX. It is
**generated**, not typed: each entry comes from `https://doi.org` under content
negotiation for `application/x-bibtex`, so the two files cannot drift and no
transcription step exists between the registry and the repository. Regenerate it
rather than editing it, with

    python scripts/build_references_bib.py --write

which was written on 10 September 2026. Until then the claim that the file was
generated rested on whoever last ran the negotiation by hand, which is the same
class of assertion this repository has twice found to be false elsewhere.
`tests/test_references.py` asserts, without touching the network, that the DOIs
in this file and the DOIs in the BibTeX are the same set.

Three entries in this register are **not** in the BibTeX and cannot be. ISO
5807:1985 is a standard and Chaudhuri (2020) is a textbook; neither has a DOI,
so no content negotiation produces them, and typing them by hand would break
the only guarantee that file makes. Both are under *The diagram sources* below.
**The third is new on 14 September 2026 and is a different case**: Zhang and
others (2026) in *Scientia Agricultura Sinica* has a DOI that resolves, but the
publisher answers a BibTeX content-negotiation request with HTML, so the
generator cannot produce an entry for a work that does have an identifier. Its
DOI is written without backticks so the generator does not claim it.

This register does **not** include the 2023 thesis's own reference list, which
is in `writeup/Duyst_Thesis.pdf` and belongs to that document. Where the errata
discusses a work the thesis cites, the work appears here and its role says so.

## What could not be verified

Nothing in the register failed to verify **as a work**. All one hundred
eighty-nine cited DOIs resolved: one hundred seventy-two through Crossref and
seventeen through DataCite, which is the registry that carries dataset and preprint DOIs
and the reason a Crossref-only lookup returns "not found" for them. **The
register now holds one preprint**, marked as one where it is cited; Copernicus
registers its discussion papers with Crossref, so it is not among the DataCite
seventeen.

**Five further DOIs appear in this register and are not citations.** They are
named to warn against them, and `scripts/build_references_bib.py` holds them in
a `NOT_CITATIONS` set with the reason for each, so they cannot acquire a BibTeX
entry by accident. Three resolve confidently to the wrong paper and two do
not resolve at all; all five were carried in as real citations, across four
consecutive passes. **The fifth is a new failure mode**: its article number is
correct and its *prefix* is wrong, so it resolves to nothing rather than to
something misleading, which is the safer of the two failures. **A resolving DOI is not a verified
citation**, and it is now the register's best-documented failure mode: three of
the four differ from the correct DOI only in the last digits of an identifier in
the same journal and year.

**A third failure mode was found on 14 September 2026 and it is the worst of the
three, because it is already committed.** Two entries written during the methods
grounding carry author lists and page ranges that do not match the registry:
Zhong and others (2026), whose author list read "Zhong, and others", and
Sicsik-Paré and others (2026), whose list put the fourth author third and dropped
the third entirely. Both were drafted from search phrasing rather than from
content negotiation, and **both were found only because a later pass happened to
need the same paper for something else.** The register should therefore be
assumed to hold more of them, and a systematic re-negotiation of the methods-pass
entries is worth a pass of its own. Neither is counted among the failures below,
because both are real citations of real papers that were written down wrongly
rather than sources that did not survive.

A second failure mode was met on 11 September 2026 and is recorded because it
nearly reached a commit. **Six author attributions drafted from search-result
phrasing named the wrong first author**, including a *Science Advances* paper
attributed to a mid-list author's surname and three where a later name was taken
for the first. All six were caught by content-negotiating every DOI for its
author list before writing the citation, which is the practice the preamble above
should be read as requiring and which no earlier pass performed
systematically. Two entries have no DOI to resolve and are
verified by other means, which the entries themselves state.

**Two sources did not survive verification for the thing they were cited for.**
The second is Zhu and Li (2025) and is set out under the region grounding below;
it is a real paper, it resolves, and none of the four figures attributed to it
could be confirmed from any accessible source, so none is written anywhere in
this repository. The first follows.
**Lodemann, T., Akçalı, E., and Fernandez, R. (2022)**, Process Modeling of
ABCDE Primary Survey in Trauma Resuscitations, *Simulation in Healthcare* 17,
425–432, `10.1097/SIH.0000000000000622`, is a real paper and resolves. It was
offered as a joint source of the flowchart design principles, and it is not
one: the protocol that names it beside Chaudhuri uses it for something else,
saying "flowchart construction will be adapted from a process modelling study
of the ABCDE primary survey in trauma resuscitation". That is a method for
eliciting a process from clinicians, which this repository does not perform. It
is recorded here and not cited.

The search for a diagramming convention also returned a **negative result worth
keeping**: there is no flowchart or workflow-diagram convention in remote
sensing or atmospheric science. The workflow figures the search returned are ad
hoc, one per paper. So the pipeline figure follows a documentation standard from
outside the field rather than imitating a discipline norm, and that is a choice
rather than a default.

Four things named in the repository are still not in the register. Natural
Earth's admin-1 boundaries, cited in `data/manifest.json` as a public-domain
download from naturalearthdata.com, has no DOI. The CSM-BSI protocol above is
a trial registration document rather than a citable work, and appears only in
the provenance note it belongs to. The Copernicus author
guidelines, which recommend Scientific colour maps and are the route by which
that recommendation reaches this field, are a web page rather than a citable
work; they are recorded beside the Crameri entry instead. `ERRATA.md` 5.3's
claim that waste treatment is the dominant anthropogenic methane source at city
scale in China could not be sourced on 3 September 2026, and was withdrawn.

**That withdrawal has since been partly reversed, which is worth recording as a
pattern.** On 10 September 2026 a city-scale source-resolved inventory supplied
the claim in a narrower and more relevant form: waste-related emissions are the
majority of total methane in 38 Chinese cities, and the examples named include
Shanghai and Suzhou, both inside this study's domain (Zhang et al., 2026,
`10.1021/acs.est.5c18654`). So the original claim was not wrong about the
mechanism; it was wrong about the scope, and stating it nationally made it
unsourceable while stating it for developed coastal cities makes it verifiable.
Withdrawing an unsourced claim was still the right action at the time, because
the narrower version was not in hand and could not have been assumed.

## Ordering

Grouped by role rather than alphabetically. Alphabetical order is conventional
and would be the right choice for a bibliography, but this is a register of what
the work rests on, and the question a reader arrives with is what kind of weight
each source bears. Within each group, alphabetical by first author.

The groups are: datasets used, methods applied, findings relied on — split
into the retrieval and the region, because two groups carried that heading until
11 September 2026 and a duplicate heading is not navigable — findings contested,
the rice-paddy exchange, the Yangtze River Delta grounding, accuracy assessment,
the methods grounding, the inversion frame with the urban layer, and coal with
building form. The last six are kept together for the same reason:
each is a single argument, and splitting its parts across the role groups would
misrepresent all of them.

The three grounding groups are the largest in the register and they pull in
different directions. The region grounding is nineteen findings and datasets
against three methods. The methods grounding is almost entirely method
literature, most of it borrowed from outside the earth sciences, and it moved the
register's method share from 18 to 34 percent. The inversion-and-urban group was
expected to move it back and moved it to 36 percent instead, because correcting a
methods record requires more method literature. Together the three are what a
paper's introduction, methods and discussion would draw on, and no one share is a
drift from the others.

---

## Datasets used

Each of these supplies data the analysis actually reads. Where a product has
both a paper and a deposit, both are listed, because the paper is the citation
and the deposit is the thing fetched, and they differ in authors and year.

**Gong, P., Li, X., Wang, J., Bai, Y., Chen, B., Hu, T., Liu, X., Xu, B.,
Yang, J., Zhang, W., and Zhou, Y. (2020).** Annual maps of global artificial
impervious area (GAIA) between 1985 and 2018. *Remote Sensing of Environment*
236, 111510.
`10.1016/j.rse.2019.111510` — peer-reviewed paper; describes a dataset used.
Cited in `config/sources.yml`, `data/manifest.json`.

**Gong, Peng (2024).** Global Artificial Impervious Area (GAIA). figshare.
`10.6084/m9.figshare.27245775.v1` — dataset record; the deposit fetched.
Cited in `config/sources.yml`, `data/manifest.json`, `data/processed/README.md`,
`notes/decisions.md`, `tests/test_fetch_gaia.py`.

**Huang, X., Li, J., Yang, J., Zhang, Z., Li, D., and Liu, X. (2021).** 30 m
global impervious surface area dynamics and urban expansion pattern observed by
Landsat satellites: From 1972 to 2019. *Science China Earth Sciences* 64,
1922–1933.
`10.1007/s11430-020-9797-9` — peer-reviewed paper; describes a dataset used, and
a finding contested. Its reported comparison against GAIA does not transfer to
this study area: GISA finds 19.9 percent *less* impervious surface here in
2018, in every province. That is the analysis year and not the record — in 2000
GISA finds 20.7 percent *more*, so the two products cross over. See
`data/processed/README.md` and `ERRATA.md` 7.5.
Cited in `config/sources.yml`.

**International Food Policy Research Institute (2019).** Global
Spatially-Disaggregated Crop Production Statistics Data for 2000, Version 3.0.7.
Harvard Dataverse.
`10.7910/DVN/A50I2T` — dataset record; supplies four committed rice rows, not
used in analysis.
Cited in `data/processed/README.md`, `scripts/recon_rice_provincial_areas.py`.

**International Food Policy Research Institute (2019).** Global
Spatially-Disaggregated Crop Production Statistics Data for 2010, Version 2.0.
Harvard Dataverse.
`10.7910/DVN/PRFF8V` — dataset record; supplies four committed rice rows, not
used in analysis.
Cited in `data/processed/README.md`, `scripts/recon_rice_provincial_areas.py`.

**Zhu, L., Liu, X., Wu, L., Liu, M., Lin, Y., Meng, Y., Ye, L., Zhang, Q., and
Li, Y. (2021).** Detection of paddy rice cropping systems in southern China with
time series Landsat images and phenology-based algorithms. *GIScience & Remote
Sensing* 58, 733–755.
`10.1080/15481603.2021.1943214` — peer-reviewed paper; **describes the method the
2023 thesis used and this reproduction did not.** The phenology- and pixel-based
paddy rice mapping algorithm, improved to use the transplanting and heading
signatures together, with annual single- and double-cropping rice maps for
southern China from Landsat 5, 7 and 8 over 1999 to 2019.

**This entry closes a gap rather than adding a source.** It is one of the 2023
thesis's two pillar methods and the origin of half its land-cover layers, and the
register held the other pillar — GAIA — from the start while this was missing
until 12 September 2026. `notes/decisions.md` records the reimplementation route
it would support and why that route was displaced.
Named in `legacy/Duyst-Yale-Thesis.md`; cited in `notes/decisions.md`,
`notes/paper-target.md`.

**Shen, R., Pan, B., Peng, Q., Dong, J., Chen, X., Zhang, X., Ye, T.,
Huang, J., and Yuan, W. (2023).** High-resolution distribution maps of
single-season rice in China from 2017 to 2022. *Earth System Science Data* 15,
3203–3222.
`10.5194/essd-15-3203-2023` — peer-reviewed paper; describes a dataset used.
The method and sensors were read off the article rather than assumed, because
`figures/landcover_native.png` states them beside a 30 m Landsat product and
the contrast is the caption's point: Sentinel-1A synthetic aperture radar and
Sentinel-2 optical imagery at 10 or 20 m, classified by time-weighted dynamic
time warping with translation and stretching, over a ranking-based fusion of
the SWIR1 optical band and the VH radar polarisation. The files this
repository reads measure 0.00008983 degrees per pixel, which is the 10 m
variant.
Cited in `config/sources.yml`, `figures/README_fragments.md`.

**Shen, R., Pan, B., Peng, Q., Dong, J., Chen, X., Zhang, X., and others
(2026).** High-resolution distribution maps of single-season rice in China from
2017 to 2022, V8. Science Data Bank.
`10.57760/sciencedb.06963` — dataset record; the deposit fetched, and the source
of the analysis grid's rice fractions.
Cited in `config/sources.yml`, `tests/test_fetch_scidb.py`,
`tests/test_fetch_figshare.py`.

**Xie, H., Li, J., Li, T., Lu, X., Hu, Q., and Qin, Z. (2025).** GloRice, a
global rice database (v1.0): I. Gridded paddy rice annual distribution from 1961
to 2021. *Scientific Data* 12, article 182.
`10.1038/s41597-025-04483-1` — peer-reviewed paper; describes a dataset used.
Cited in `config/sources.yml`, `data/manifest.json`,
`data/processed/README.md`, `notes/decisions.md`.

**Qin, Zhangcai and Xie, Hanzhi (2024).** GloRice(I): Gridded 5-arcmin paddy
rice annual distribution maps for the years 1961 to 2021. figshare.
`10.6084/m9.figshare.27965832.v2` — dataset record; the deposit fetched. Its
author field is the one that produced the "Zhang et al." error.
Cited in `config/sources.yml`, `data/manifest.json`,
`data/processed/README.md`, `scripts/recon_rice_provincial_areas.py`,
`src/fetch/figshare.py`, `tests/test_fetch_figshare.py`.

**European Space Agency (2021).** TROPOMI Level 2 Methane Total Column.
`10.5270/S5P-3lcdqiv` — dataset record; the methane product actually read. This
is the DOI the granules declare in `identifier_product_doi`, and it resolves to
the KNMI/SRON product page at tropomi.eu.
Cited in `data/manifest.json`, `notes/decisions.md`.

**European Space Agency (2019).** TROPOMI Level 2 Methane Total Column.
`10.5270/S5P-3p6lnwd` — dataset record; the same product under the ESA
Copernicus catalogue, resolving to sentinels.copernicus.eu. Recorded because the
manifest cited it until 3 September 2026 and a reader may meet it in the
history; it is not the DOI the files declare.
Not cited in any current file; retained here for the record.

## Findings relied on: the retrieval

**Lorente, A., Borsdorff, T., Butz, A., Hasekamp, O., aan de Brugh, J.,
Schneider, A., and 12 others (2021).** Methane retrieved from TROPOMI:
improvement of the data product and validation of the first 2 years of
measurements. *Atmospheric Measurement Techniques* 14, 665–684.
`10.5194/amt-14-665-2021` — peer-reviewed paper; a finding relied on, and a
method whose effect is tested. It documents the a posteriori albedo correction
the operational product carries; this repository measures that the correction
reduces the fitted albedo slope by 2.0 percent unweighted over this composite.
Cited in `notes/decisions.md`.

## Findings contested

**Schneising, O., Bovensmann, H., Buchwitz, M., Buschmann, M., and 25 others
(2026).** TROPOMI/WFMD v2.0: Improved retrievals of XCH4 and XCO with
XGBoost-based quality filtering. *Atmospheric Measurement Techniques* 19,
2407–2435.
`10.5194/amt-19-2407-2026` — peer-reviewed paper; a finding contested, in the
narrow sense that a benchmark was attributed to it that its abstract does not
support. The paper describes replacing a Random Forest classifier with XGBoost
for **quality filtering**, not an albedo correction. The residual-sensitivity
figures quoted against it in `notes/decisions.md` are recorded there as
unverified.
Cited in `notes/decisions.md`.

**He, K., Chen, X., Xie, S., Li, Y., Dollár, P., and Girshick, R. (2022).**
Masked Autoencoders Are Scalable Vision Learners. *2022 IEEE/CVF Conference on
Computer Vision and Pattern Recognition (CVPR)*.
`10.1109/CVPR52688.2022.01553` — peer-reviewed paper; a finding contested. This
is the thesis's citation, not the reproduction's: `ERRATA.md` 4.1 records that
Section 3.3 describes a masked autoencoder citing this work throughout, while the
implementation performs supervised segmentation with no masking anywhere. The
errata names it as "He et al. (2022)" without a DOI; the DOI here was resolved
for this register.
Named in `ERRATA.md`.

## Methods applied

Added 3 September 2026. Before that date the reproduction's methods carried no
citations at all; see `notes/decisions.md`.

**Roberts, D. R., Bahn, V., Ciuti, S., Boyce, M. S., Elith, J.,
Guillera-Arroita, G., Hauenstein, S., Lahoz-Monfort, J. J., Schröder, B.,
Thuiller, W., Warton, D. I., Wintle, B. A., Hartig, F., and Dormann, C. F.
(2017).** Cross-validation strategies for data with temporal, spatial,
hierarchical, or phylogenetic structure. *Ecography* 40, 913–929.
`10.1111/ecog.02881` — peer-reviewed paper; a method applied. The authority for
evaluating spatially structured data by blocking rather than random splits,
which is why this repository uses leave-one-province-out and spatial blocks. Its
abstract states the case directly: dependence structures in the data persist as
dependence structures in model residuals, and "block cross-validation, where
data are split strategically rather than randomly, can address these issues".
Belongs beside the evaluation design in `src/model/baselines.py` and
`data/processed/README.md`.

**Valavi, R., Elith, J., Lahoz-Monfort, J. J., and Guillera-Arroita, G.
(2019).** blockCV: An R package for generating spatially or environmentally
separated folds for k-fold cross-validation of species distribution models.
*Methods in Ecology and Evolution* 10, 225–232.
`10.1111/2041-210X.13107` — peer-reviewed paper; a method applied. Its
contribution here is the principle rather than the software: it provides tools
to measure the spatial autocorrelation range in the covariates and choose a
block size from it, which is the step that makes a block size defensible rather
than arbitrary. Cited with the print year 2019; Crossref's `issued` gives
2018-11-08, the online date. This is the same online-versus-print gap
`ERRATA.md` 6.3 raises against the thesis, and the convention taken here is the
print year, matching the volume and issue.

**Crameri, F., Shephard, G. E., and Heron, P. J. (2020).** The misuse of colour
in science communication. *Nature Communications* 11, article 5444.
`10.1038/s41467-020-19160-7` — peer-reviewed paper; a method applied, when
figures exist. No figure has been generated from the reproduced data yet, so
this is cited in advance of use. It reaches this field through the venue as well
as the literature: Copernicus, which publishes *Atmospheric Measurement
Techniques* and *Earth System Science Data*, recommends Scientific colour maps in
its own author guidelines, so following it is a venue standard here and not only
a borrowed visualisation preference.

**Correll, M., Moritz, D., and Heer, J. (2018).** Value-Suppressing Uncertainty
Palettes. *Proceedings of the 2018 CHI Conference on Human Factors in Computing
Systems*, 1–11.
`10.1145/3173574.3174216` — peer-reviewed paper; a method applied, when figures
exist. **Borrowed method literature, from human-computer interaction.** It is
the reference for encoding uncertainty by suppressing colour value, which is the
natural treatment for a composite whose per-cell sounding counts run from 1 to
410. Carried with a caveat rather than as settled practice: value-suppressing
palettes can flatten a spatial trend where uncertainty is high, which over this
composite would be exactly the sparsely sampled cells, so the palette could hide
the pattern in the cells the reader most needs to discount.

**Liu, M., van der A, R., van Weele, M., Eskes, H., Lu, X., and 8 others
(2021).** A New Divergence Method to Quantify Methane Emissions Using
Observations of Sentinel-5P TROPOMI. *Geophysical Research Letters* 48, article
e2021GL094151.
`10.1029/2021GL094151` — peer-reviewed paper; a method **not** applied, recorded
because it is the standard route from column concentration to emissions and the
reproduction never took it. It is also in the 2023 thesis's own bibliography,
uncited in its text.

**A correction to this entry, made 12 September 2026.** Until then it said
`notes/decisions.md` "records the gate that established why the conversion is
not feasible on this composite". **It did not.** That file held one clause
mentioning the gate in passing and no section recording its reasoning, and two
later files inherited the claim and cross-referenced a section that was never
there. The gate is now recorded, marked as a reconstruction from conversation
rather than as a verified computation, under *What the grounding superseded*.

### The diagram sources, added 9 September 2026

Four entries added when the figure set gained its first two diagrams. All four
are **borrowed method literature**: none comes from atmospheric science, remote
sensing or the earth sciences at all. Two are documentation and diagramming
standards, one is a statistics grammar and one is a machine-learning taxonomy.
The search that found them also found what it did not find, which is recorded
below under *What could not be verified*.

**International Organization for Standardization (1985).** ISO 5807:1985,
Information processing — Documentation symbols and conventions for data,
program and system flowcharts, program network charts and system resources
charts. Geneva.
No DOI — a standard, not a paper; a method applied. **Borrowed method
literature, from information-processing documentation.** It defines the symbol
set `src/figures/diagram.py` declares and `figures/framework_pipeline` draws
from: terminal, process, predefined process, decision, data, stored data and
connector. Published February 1985 and confirmed current at ISO's 2019 review.

**The standard was not read.** It is paywalled and this repository holds no
copy, so nothing here quotes or cites a clause of it. What is claimed is the
symbol *names*, which every secondary account of the standard gives alike, and
the diagram module says so in its own docstring rather than implying more.

**Chaudhuri, A. B. (2020).** Flowchart and Algorithm Basics: The Art of
Programming. Mercury Learning and Information, Dulles, VA.
No DOI — a textbook; a method applied. **Borrowed method literature, from
programming pedagogy.** The named source of the six design principles the
pipeline figure follows: agree in advance a minimal set of design shapes and
use only shapes from that set; read top-down and left-right; one entry point
and one exit point per shape, the decision symbol excepted; label every
decision branch; show the information an event requires; show the resource an
event requires.

**This book was not read either, and the wording above is not its own.** The
principles were verified in Appendix 5 of the CSM-BSI study protocol
(clinicaltrials.gov NCT06271031, draft v1.0, October 2023), which states them
as "adapted from (Chaudhuri, 2020; Lodemann et al., 2022)" and adds that its
principles and shapes are "in accordance with the ISO standard 5807:1985"
where possible. The chain is recorded rather than collapsed, because collapsing
it is how this register's preamble records two earlier citations going wrong.
The protocol lists a seventh principle — consider re-entrant processes when
events are stochastic — which the pipeline figure does not use and which is
therefore not listed above.

**Patil, P., Peng, R. D., and Leek, J. T. (2019).** A visual tool for defining
reproducibility and replicability. *Nature Human Behaviour* 3, 650–652.
`10.1038/s41562-019-0629-z` — peer-reviewed paper; a method applied.
**Borrowed method literature, from statistics.** The grammar
`figures/framework_reproduction` follows: eleven stages of the scientific
process as rows, studies as columns, and one state per cell.

The paper is paywalled and, like the standard, was not read. The grammar was
taken from the authors' own reference implementation, the `scifigure` R package
on CRAN, whose source gives the eleven stage names in order — population,
question, hypothesis, experimental design, experimenter, data, analysis plan,
analyst, code, estimate, claim — and the four states a cell may take:
`observed`, `different`, `unobserved`, `incorrect`. Its difference mode uses
symbols "semantically close to the scenarios that they are encoding", a cross
for unobserved, a not-equals for different and an exclamation mark for
incorrect, and that is the mode this repository follows. Its default palette,
a red and a teal, is **not** followed: `src/figures/style.py` exists partly
because a red-green pair is unreadable to a substantial minority of readers.

**Desai, A., Abdelhamid, M., and Padalkar, N. R. (2025).** What is
reproducibility in artificial intelligence and machine learning research? *AI
Magazine* 46, article e70004.
`10.1002/aaai.70004` — peer-reviewed paper; a method applied. **Borrowed method
literature, from machine learning.** Its hierarchy is what lets the
reproduction figure say which *kind* of reproduction each component received.
Verbatim: "Dependent reproducibility involves using the original materials and
validating the correctness of the implementation as described in the study.
Independent reproducibility is achieved by reconstructing the experiment based
on the original study's methodology and similarly validating the
implementation's correctness." Recomputing the GAIA provincial areas from the
same product is the first; rebuilding the methane composite from Level 2
granules is the second.

## Findings relied on: the region

**Hu, C., Griffis, T. J., Liu, S., Xiao, W., Hu, N., Huang, W., Yang, D., and
Lee, X. (2019).** Anthropogenic Methane Emission and Its Partitioning for the
Yangtze River Delta Region of China. *Journal of Geophysical Research:
Biogeosciences* 124, 1148–1170.
`10.1029/2018JG004850` — peer-reviewed paper; a finding relied on. Sectoral
partitioning of anthropogenic methane for this study's own region.

**Huang, W., Griffis, T. J., Hu, C., Xiao, W., and Lee, X. (2021).** Seasonal
Variations of CH4 Emissions in the Yangtze River Delta Region of China Are
Driven by Agricultural Activities. *Advances in Atmospheric Sciences* 38,
1537–1551.
`10.1007/s00376-021-0383-9` — peer-reviewed paper; a finding relied on, and the
most directly relevant work in this register. A tower-based Bayesian inversion
of the Yangtze River Delta for 2018, this study's own year, attributing seasonal
variability to agricultural activity. It reaches a conclusion compatible with
the thesis's by a method that can support it, where the thesis used one that
cannot. `ERRATA.md` 7.1 makes that point and should carry this citation.

**Huang, W., Xiao, W., Zhang, M., Wang, W., Xu, J., and 4 others (2019).**
Anthropogenic CH4 Emissions in the Yangtze River Delta Based on A "Top-Down"
Method. *Atmosphere* 10, 185.
`10.3390/atmos10040185` — peer-reviewed paper; a finding relied on. A top-down
regional estimate for the same area.

**Da Pan, Tao, L., Sun, K., Golston, L. M., Miller, D. J., Zhu, T., Qin, Y.,
Zhang, Y., Mauzerall, D. L., and Zondlo, M. A. (2020).** Methane emissions from
natural gas vehicles in China. *Nature Communications* 11, 4588.
`10.1038/s41467-020-18141-0` — peer-reviewed paper; a finding contested. This is
the source the thesis cites for attributing urban methane to natural gas
vehicles. It measured heavy-duty vehicles at about 90 percent above their
emission limits and framed the problem as one of standards and enforcement; it
describes neither retrofitting nor faulty tailpipes, which is the thesis's
framing. See `ERRATA.md` 5.3. Crossref stores the first author as the literal
string "Da Pan" with no given name, which is the same name-order hazard recorded
in `notes/decisions.md` for the GloRice deposit, and the reason the DOI rather
than the name is the thing carried forward.
Cited in `ERRATA.md`.

**Zhao, S., Zhang, Y., Liang, R., Chen, W., Xie, X., Wang, R., Xia, Z.,
Shen, J., and 2 others (2024).** Low Methane Emissions from the Natural Gas
Distribution System Indicated by Mobile Measurements in a Chinese Megacity
Hangzhou. *ACS ES&T Air* 1, 1511–1518.
`10.1021/acsestair.4c00068` — peer-reviewed paper; a finding relied on, and a
finding that contests the thesis. Mobile measurements in a Yangtze River Delta
megacity find the natural gas distribution system to be a low emitter, which
bears directly on `ERRATA.md` 5.3: the thesis attributes urban methane to
natural gas vehicles, and this is the measurement in this region that the
attribution has to answer to. From 3 to 10 September 2026 it was the whole of
what section 5.3 could be supported by. It is now one of three measurements
there, and the one that locates the leakage in end use and transportation rather
than in distribution pipelines.

## The rice-paddy exchange

`ERRATA.md` 5.2 refers to this exchange without naming it. All three parts are
recorded, because the original and the response are each incomplete without the
other, and the reply is part of the published record.

**Zhang, Z., Xiao, X., Dong, J., Xin, F., Zhang, Y., and 3 others (2020).**
Fingerprint of rice paddies in spatial-temporal dynamics of atmospheric methane
concentration in monsoon Asia. *Nature Communications* 11, 554.
`10.1038/s41467-019-14155-5` — peer-reviewed paper; a finding contested. The
original claim that rice paddy dynamics are visible in satellite methane.

**Zeng, Z.-C., Byrne, B., Gong, F.-Y., He, Z., and Lei, L. (2021).** Correlation
between paddy rice growth and satellite-observed methane column abundance does
not imply causation. *Nature Communications* 12, 1163.
`10.1038/s41467-021-21434-7` — peer-reviewed paper; a finding relied on. The
Matters Arising `ERRATA.md` 5.2 refers to. Its argument, that local column
variation is driven by advected large-scale signals and that rice-methane
correlations are confounded by co-located sources, is the published form of what
this reproduction measured independently.

**Zhang, Z., Xiao, X., Dong, J., Zhang, Y., Xin, F., and 3 others (2021).**
Reply to: "Correlation between paddy rice growth and satellite-observed methane
column abundance does not imply causation". *Nature Communications* 12, 1189.
`10.1038/s41467-021-21437-4` — peer-reviewed paper; a finding contested. The
original authors' response, recorded so the exchange is not represented by one
side of it.


## Assessments and instrument documentation

Added 3 September 2026, when the errata's uncited claims were closed.

**Forster, P., Storelvmo, T., Armour, K., Collins, W., Dufresne, J.-L.,
Frame, D., Lunt, D. J., Mauritsen, T., Palmer, M. D., Watanabe, M., Wild, M.,
and Zhang, H. (2021).** The Earth's Energy Budget, Climate Feedbacks and
Climate Sensitivity. In *Climate Change 2021: The Physical Science Basis*,
923–1054. Cambridge University Press.
`10.1017/9781009157896.009` — book chapter; a finding relied on. Table 7.15 is
the current assessment of methane's global warming potential and the source for
the corrected figures in `ERRATA.md` 5.4. Crossref returns no author list for
this chapter and dates it 2023, the Cambridge print edition; the authors above
are read from the chapter itself and the report is 2021.

**Myhre, G., Shindell, D., Bréon, F.-M., Collins, W., Fuglestvedt, J.,
Huang, J., and 8 others (2013).** Anthropogenic and Natural Radiative Forcing.
In *Climate Change 2013: The Physical Science Basis*, 659–740. Cambridge
University Press.
`10.1017/CBO9781107415324.018` — book chapter; a finding contested. Table 8.7 is
the AR5 assessment, recorded because an earlier version of `ERRATA.md` 5.4
quoted approximately these values as current when AR6 had superseded them.

**Veefkind, J. P., Aben, I., McMullan, K., Förster, H., de Vries, J.,
Otter, G., Claas, J., Eskes, H. J., de Haan, J. F., and 13 others (2012).**
TROPOMI on the ESA Sentinel-5 Precursor: A GMES mission for global observations
of the atmospheric composition for climate, air quality and ozone layer
applications. *Remote Sensing of Environment* 120, 70–83.
`10.1016/j.rse.2011.09.027` — peer-reviewed paper; describes the instrument used.
The source for the 7 by 7 km design nadir ground pixel in `ERRATA.md` 2.4.

**Moran, P. A. P. (1950).** Notes on Continuous Stochastic Phenomena.
*Biometrika* 37, 17–23.
`10.1093/biomet/37.1-2.17` — peer-reviewed paper; a method whose properties are
relied on. The origin of Moran's I and the source for the statement in
`ERRATA.md` 6.2 that its standardised form depends on the number of units.

**Cohen, T. S., and Welling, M. (2016).** Group Equivariant Convolutional
Networks. arXiv.
`10.48550/arXiv.1602.07576` — preprint; a finding relied on. **Borrowed method
literature, from machine learning.** Establishes equivariance as the property
convolution actually has, which is the distinction `ERRATA.md` 4.2 rests on.

**Azulay, A., and Weiss, Y. (2018).** Why do deep convolutional networks
generalize so poorly to small image transformations? arXiv.
`10.48550/arXiv.1805.12177` — preprint; a finding relied on. **Borrowed method
literature, from machine learning.** Shows that invariance fails in practice
even for small translations and rescalings, which is the other half of 4.2.

## Reference data published since the thesis

Added 3 September 2026 to close `ERRATA.md` 5.1, which asserted these existed
without naming any of them. The first two can validate a rice layer; the second
two are emission products and cannot.

**Chen, Z., Lin, H., Balasus, N., Hardy, A., East, J. D., Zhang, Y.,
Runkle, B. R. K., Hancock, S. E., Taylor, C. A., Du, X., Sander, B. O., and
Jacob, D. J. (2025).** Global Rice Paddy Inventory (GRPI): A High-Resolution
Inventory of Methane Emissions From Rice Agriculture Based on Landsat Satellite
Inundation Data. *Earth's Future* 13, e2024EF005479.
`10.1029/2024EF005479` — peer-reviewed paper; describes a dataset not used. A
rice methane emission inventory at 0.1 degree and monthly resolution.

**Han, J., Zhang, Z., Luo, Y., Cao, J., Zhang, L., Zhuang, H., Cheng, F.,
Zhang, J., and Tao, F. (2022).** Annual paddy rice planting area and cropping
intensity datasets and their dynamics in the Asian monsoon region from 2000 to
2020. *Agricultural Systems* 200, 103437.
`10.1016/j.agsy.2022.103437` — peer-reviewed paper; describes a dataset not
used. Covers 2000 to 2020; the acronym APRA500 does not appear in its indexed
metadata and is not used here.

**Liang, R., Zhang, Y., Hu, Q., Li, T., Li, S., Yuan, W., Xu, J., Zhao, Y.,
Zhang, P., Chen, W., Zhuang, M., Shen, G., and Chen, Z. (2024).**
Satellite-Based Monitoring of Methane Emissions from China's Rice Hub.
*Environmental Science & Technology* 58, 23127–23137.
`10.1021/acs.est.4c09822` — peer-reviewed paper; a finding relied on. A regional
satellite constraint on rice methane, which is the kind of result the thesis
assumed was unavailable.

**Shen, R., Peng, Q., Li, X., Chen, X., and Yuan, W. (2025).** CCD-Rice: a
long-term paddy rice distribution dataset in China at 30 m resolution.
*Earth System Science Data* 17, 2193–2216.
`10.5194/essd-17-2193-2025` — peer-reviewed paper; describes a dataset not used.
Covers 1990 to 2016 at 30 m.

---

## The Yangtze River Delta grounding, added 10 September 2026

Nineteen literature searches over the region produced findings that existed
only in a conversation. [`notes/grounding-yrd.md`](grounding-yrd.md) records
them and these are its sources. The group is kept together for the same reason
*The rice-paddy exchange* is: it is one argument, and splitting it across the
role groups above would hide that the region grounding is a single body of
evidence rather than nineteen unrelated facts.

**Five figures quoted from these works in a search snippet did not survive
checking against the works themselves**, which is recorded in the grounding
document's own closing section and is the reason this group exists as a
verified register rather than as notes.

### The regional budget

**Duan, Y., Gao, Y., Zhao, J., Xue, Y., Zhang, W., Wu, W., Jiang, H., and
Cao, D. (2023).** Agricultural Methane Emissions in China: Inventories, Driving
Forces and Mitigation Strategies. *Environmental Science & Technology* 57,
13292–13303.
`10.1021/acs.est.3c04209` — peer-reviewed paper; a finding relied on, and the
single most load-bearing citation in the grounding. It supplies the 38.4 percent
share of national agricultural methane for the middle and lower Yangtze, the
seven-province definition of that region, and the livestock decoupling in
Jiangsu and Zhejiang. The article is paywalled; its figures were verified
through two independent searches returning the same wording, not by reading the
text, and the grounding says so.
Cited in `notes/grounding-yrd.md`.

**Zhang, L., Chen, Y., Wang, K., Guo, J., Liang, S., Wu, P., Zhang, H., Wu, J.,
Cui, Y., Lyu, C., Xu, H., Wang, Q., Cai, B., Wang, J., and Li, L. (2026).**
City-Scale, Source-Resolved Methane Inventories Reveal Drivers and Mitigation
Pathways Across China's Cities. *Environmental Science & Technology* 60,
22323–22334.
`10.1021/acs.est.5c18654` — peer-reviewed paper; a finding relied on, and
describes a dataset not used. Covers 339 prefecture-level cities from 2018 to
2024. It is the source of the verified 2024 national sectoral split that
replaces an unsourceable one, and of the statement that waste-related emissions
are the majority of total methane in 38 cities including Shanghai and Suzhou,
which is what `ERRATA.md` 5.3 now rests on. Open access through PubMed Central,
read directly.
Cited in `notes/grounding-yrd.md`, `ERRATA.md`, `notes/dataset-leads.md`.

### The rice calendar

**Li, H., Wang, X., Wang, S., Liu, J., Liu, Y., Liu, Z., Chen, S., Wang, Q.,
Zhu, T., Wang, L., and Wang, L. (2024).** ChinaRiceCalendar – seasonal crop
calendars for early-, middle-, and late-season rice in China. *Earth System
Science Data* 16, 1689–1701.
`10.5194/essd-16-1689-2024` — peer-reviewed paper; describes a dataset not used,
and a finding relied on. Supplies the Middle-Lower Yangtze transplanting and
maturity means the calendar-mismatch finding is measured against. **A premise
failed here**: its validated agreement for late-season rice is R² 0.90, not
0.96, and it gives no province-level calendar for Anhui in its text.
Cited in `notes/grounding-yrd.md`, `notes/dataset-leads.md`.

**Liu, J., Li, H., Wang, X., Wang, S., Liu, Y., Liu, Z., Chen, S., Wang, Q.,
Zhu, T., Wang, L., and Wang, L. (2023).** ChinaRiceCalendar. Harvard Dataverse.
`10.7910/DVN/EUP8EY` — dataset record; the deposit, not fetched. Its author
field reads "Jinyuan Liu, Hui Li", two of eleven authors with the given and
family names run together, which is the third instance of the platform-metadata
name hazard this register's preamble warns about. The citation above is the
paper's, not the deposit's.
Cited in `notes/grounding-yrd.md`, `notes/dataset-leads.md`.

### Water management, which is the mechanism the study has no layer for

**Wu, X., Wang, W., Xie, X., Yin, C., Hou, H., Yan, W., and Wang, G. (2018).**
Net global warming potential and greenhouse gas intensity as affected by
different water management strategies in Chinese double rice-cropping systems.
*Scientific Reports* 8, article 779.
`10.1038/s41598-017-19110-2` — peer-reviewed paper; a finding relied on. The
field experiment giving net global warming potentials of 22,497, 8,895 and
1,646 kg CO2-equivalent per hectare per year across three water regimes, a
factor of 13.7 on one soil under one crop. Cited with the print year 2018;
Crossref's `issued` gives January 2018 and the volume agrees.
Cited in `notes/grounding-yrd.md`.

**Minamikawa, K. (2025).** Climate-smart water management in rice paddies: a
meta-synthesis on greenhouse gas emissions and yield impacts. *Paddy and Water
Environment* 23, 525–532.
`10.1007/s10333-025-01045-4` — peer-reviewed paper; a finding relied on. A
review of eleven meta-analyses. The per-outcome counts matter and are carried:
the CH4 range of −31 to −62 percent rests on ten of them, the N2O range of +37
to +445 percent on seven, and the yield range on eight.
Cited in `notes/grounding-yrd.md`.

**Jiang, Y., Carrijo, D., Huang, S., Chen, J., Balaine, N., Zhang, W., van
Groenigen, K. J., and Linquist, B. (2019).** Water management to mitigate the
global warming potential of rice systems: A global meta-analysis. *Field Crops
Research* 234, 47–54.
`10.1016/j.fcr.2019.02.010` — peer-reviewed paper; a finding relied on. The
201-paired-observation meta-analysis underlying the synthesis above, and the
one that quantifies the net effect: a 44 percent reduction in combined global
warming potential, because N2O contributes only about 12 percent of it. First
author Yu Jiang, who is not the Min Jiang of the cropping-system paper below.
Cited in `notes/grounding-yrd.md`.

**Vo, T. B. T., Wassmann, R., Tirol-Padre, A., Cao, V. P., MacDonald, B.,
Espaldon, M. V. O., and Sander, B. O. (2018).** Methane emission from rice
cultivation in different agro-ecological zones of the Mekong river delta:
seasonal patterns and emission factors for baseline water management. *Soil
Science and Plant Nutrition* 64, 47–58.
`10.1080/00380768.2017.1413926` — peer-reviewed paper; a finding relied on. The
source for the statement that deltaic rice systems have hydrological conditions
specific enough that default emission factors may be erroneous, and for the
0.31 to 9.14 kg CH4 per hectare per day spread across four agro-ecological
zones of one delta. Cited with the print year 2018 matching volume 64 issue 1;
Crossref's `issued` gives December 2017, the online date, which is the same
convention taken for Valavi et al. above.
Cited in `notes/grounding-yrd.md`.

**Wang, Y., Tao, F., Chen, Y., and Yin, L. (2024).** Mapping irrigation regimes
in Chinese paddy lands through multi-source data assimilation. *Agricultural
Water Management* 304, 109083.
`10.1016/j.agwat.2024.109083` — peer-reviewed paper; describes a dataset not
used. The nearest thing found to the missing water-regime covariate: water-saving
against flooding irrigation at 500 m, by province-wise random forest over MODIS
and Sentinel-1, with an overall accuracy near 0.73 against ground samples and an
R² above 0.92 against city and provincial census area. The census assimilation
is the reason it needs care rather than adoption.
Cited in `notes/dataset-leads.md`.

**Huang, Y., Sass, R. L., and Fisher, F. M. Jr. (1998).** A semi-empirical model
of methane emission from flooded rice paddy soils. *Global Change Biology* 4,
247–268.
`10.1046/j.1365-2486.1998.00129.x` — peer-reviewed paper; a method not applied.
The origin of CH4MOD, which is the model the cropping-system study below runs
and the obvious route from a rice layer plus a water regime to an emission
estimate. Recorded because the route exists and this reproduction has not taken
it.
Cited in `notes/grounding-yrd.md`, `notes/dataset-leads.md`.

### The two transitions the thesis does not frame

**Jiang, M., Li, X., Xin, L., Tan, M., and Zhang, W. (2023).** Impacts of Rice
Cropping System Changes on Paddy Methane Emissions in Southern China. *Land* 12,
270.
`10.3390/land12020270` — peer-reviewed paper; a finding relied on. Double-crop
to single-crop conversion of 253.64 × 10⁴ hectares between 1990 and 2015,
reducing CH4 by 451.94 Gg or 8.4 percent of the Chinese paddy total, largest in
the Middle-Lower Yangtze plain. **A premise was refined here**: the projected
further reduction under urbanisation is 17.1 percent in the extreme scenario and
9.2 percent in the most likely, not 9.2 percent alone.
Cited in `notes/grounding-yrd.md`.

**Yuan, Y., Dai, X., Wang, H., Xu, M., Fu, X., and Yang, F. (2016).** Effects of
Land-Use Conversion from Double Rice Cropping to Vegetables on Methane and
Nitrous Oxide Fluxes in Southern China. *PLoS ONE* 11, e0155926.
`10.1371/journal.pone.0155926` — peer-reviewed paper; a finding relied on. The
measurement that paddy-to-vegetable conversion takes cumulative CH4 from 348.9
and 321.0 kg C per hectare per year to −0.4 and 1.4, which is a collapse to
approximately zero rather than a reduction, while N2O rises by an order of
magnitude.
Cited in `notes/grounding-yrd.md`.

**Li, C., Zhou, Z., Chen, X., Tang, Q., Zhang, Q., and Tang, J. (2026).**
Shifted microbial network characteristics govern soil N2O emission following
paddy-to-vegetable land conversion. *Frontiers in Microbiology* 17.
`10.3389/fmicb.2026.1750894` — peer-reviewed paper; a finding relied on, and
narrowly. It is cited for two things only: that the conversion is becoming
increasingly widespread, and that it has been studied in the Yangtze River Delta
specifically. Its own subject is soil microbial networks and N2O, which this
study does not address.
Cited in `notes/grounding-yrd.md`.

### Wetlands, urban gas and transport

**Yang, B., Li, X., Lin, S., Jiang, C., Xue, L., Wang, J., Liu, X.,
Espenberg, M., Pärn, J., and Mander, Ü. (2021).** Invasive Spartina
alterniflora changes the Yangtze Estuary salt marsh from CH4 sink to source.
*Estuarine, Coastal and Shelf Science* 252, 107258.
`10.1016/j.ecss.2021.107258` — peer-reviewed paper; a finding relied on. The
wetland term in this region does not have a fixed sign, which is a stronger
statement than that its magnitude is unknown, and it is the reason the
grounding treats wetlands as untestable here rather than as merely omitted.
Cited in `notes/grounding-yrd.md`.

**Zhao, Y., Zhang, Y., Zhang, Y., Xu, Z., Pei, X., Wang, Z., Xu, B., Xia, Z.,
Zou, Q., Zhao, W., Sun, Y., Wang, Q., Gao, Y., Wang, H., Huang, C., Wang, X.,
Wang, R., Qiu, B., Zhao, S., Wang, X., Zhou, Y., Shen, H., and Shen, G.
(2026).** Underestimated methane emissions from natural gas consumption in the
Yangtze River Delta cities of China. *Nature Cities*.
`10.1038/s44284-026-00504-1` — peer-reviewed paper; a finding relied on **for
its direction and its region only**. The work exists, resolves, and is about
this study's own domain, which is why it matters. Its numerical results are not
relied on: the article is paywalled, its abstract is not indexed by Crossref or
OpenAlex, and the leakage figures circulating for it come from a press summary.
`ERRATA.md` 5.3 and the grounding both say so at the point of use. One of its
authors, Youwen Sun, is also a Hefei TCCON principal investigator, which is
worth knowing if the leakage estimate is ever pursued.
Cited in `notes/grounding-yrd.md`, `ERRATA.md`.

**Shan, M., Xu, H., Han, L., Pang, Y., Ma, J., and Zhang, C. (2022).** Temporal
Variation and Source Analysis of Atmospheric CH4 at Different Altitudes in the
Background Area of Yangtze River Delta. *Atmosphere* 13, 1206.
`10.3390/atmos13081206` — peer-reviewed paper; a finding relied on. The
published analysis of the regional background methane record inside this study's
domain.
Cited in `notes/grounding-yrd.md`, `notes/dataset-leads.md`.

**Guo, N., Lin, H., Lin, Y., Wei, F., Zang, K., and Fang, S. (2023).** Temporal
patterns and determinants of atmospheric methane in Suzhou, the Yangtze River
Delta. *Atmospheric Pollution Research* 14, 101830.
`10.1016/j.apr.2023.101830` — peer-reviewed paper; a finding relied on. Three
stations inside the domain, an annual mean of 2,132.25 ppb at the northern one,
and a surface seasonal peak in mid-July and late August. It is the in-domain
measurement the composite's October sounding peak has to be read against.
Cited in `notes/grounding-yrd.md`, `notes/dataset-leads.md`.

**Wang, Y., Yuan, X., Yuan, T., Zhang, J., Tai, A. P. K., and Feng, Z. (2026).**
Impacts of land use/cover changes on local meteorology and air quality in the
Yangtze River Delta region of China (2001–2021). *Journal of Environmental
Sciences* 161, 707–717.
`10.1016/j.jes.2025.07.021` — peer-reviewed paper; a finding relied on. The
fourth confound on the urban association, and the only one that is physical
rather than statistical: impervious fraction is correlated with boundary-layer
depth and wind speed through a mechanism, in a direction this study cannot sign.
Cited in `notes/grounding-yrd.md`.

**Sun, C., Liu, Y., Ciais, P., Broquet, G., Zheng, B., Wang, H., and Chen, H.
(2026).** Measurement-based assessment reveals key drivers and mitigation
potential of methane emissions from China's wastewater treatment. *Science
Advances* 12, issue 15.
`10.1126/sciadv.aec0536` — peer-reviewed paper; describes a dataset not used.
Facility-level emission factors from atmospheric measurements at 105 wastewater
treatment plants, including thirteen in Nanjing measured in three seasons. It is
the sector `ERRATA.md` 5.3 records the thesis as omitting entirely, now with a
measurement behind it.
Cited in `notes/dataset-leads.md`.

### One work cited and not relied on

**Zhu, Y., and Li, H. (2025).** Methane emissions from rice paddies in the
Yangtze River Delta region of China: synthesis of new estimates. *International
Journal of Environmental Science and Technology* 22, 11011–11016.
`10.1007/s13762-024-06050-4` — peer-reviewed paper; **a source that could not
be verified for the thing it was cited for.** It is a real work and resolves. A
per-hectare emission factor rising from 146.02 to 252.17 kg per hectare between
the 2000s and the 2010s over 416 samples was attributed to it, and none of those
figures could be confirmed: the article is paywalled, no abstract is indexed by
Crossref or OpenAlex, and no accessible copy was found. It is recorded here and
its figures are not written anywhere in this repository. This is the second
entry in this register in that category, after Lodemann et al. (2022) above.
Named in `notes/grounding-yrd.md`.

---

## Accuracy assessment and the fractional-cover frame, added 10 September 2026

Two entries that close a gap `ERRATA.md` 6.5 leaves open. The errata faults the
thesis for reporting no classification accuracy; the reproduction reports none
either, and the reason is not symmetric, which needs the standard in the
register before it can be argued.

**Olofsson, P., Foody, G. M., Herold, M., Stehman, S. V., Woodcock, C. E., and
Wulder, M. A. (2014).** Good practices for estimating area and assessing
accuracy of land change. *Remote Sensing of Environment* 148, 42–57.
`10.1016/j.rse.2014.02.015` — peer-reviewed paper; a method **not** applied, and
the standard a reviewer will check this work against. Its five recommendations
are a probability sampling design, a response design using reference data more
accurate than the map, consistent analysis, an error matrix expressed as
proportions of area, and error-adjusted area estimates with confidence
intervals. **The first three apply to this study and are unmet; the last two do
not apply at all.** The paper contains no treatment of fractional cover: the
strings "fraction", "sub-pixel" and "subpixel" do not occur in it, and its
"proportion of area" always means the share of a region a discrete class
occupies. This study's layers are per-cell fractions, for which the next entry
is the frame.
Cited in `notes/dataset-leads.md`.

**Wickham, J., Stehman, S. V., Neale, A., and Mehaffey, M. (2020).** Accuracy
assessment of NLCD 2011 percent impervious cover for selected USA metropolitan
areas. *International Journal of Applied Earth Observation and Geoinformation*
84, 101955.
`10.1016/j.jag.2019.101955` — peer-reviewed paper; a method applicable and not
yet applied. **Borrowed method literature, from land-cover accuracy
assessment.** The frame for a continuous field rather than a categorical map:
mean deviation, mean absolute deviation and ordinary least squares regression
against a more accurate reference fraction, explicitly in contrast to techniques
for nominal class data that build an error matrix. It also measures the
aggregation effect this study depends on, across seven lattice cell sizes from
1 to 200 hectares, with mean absolute deviation at or below 5 percent for six of
the seven. This study's cells are 62,500 hectares.
Cited in `notes/dataset-leads.md`.

**Huang, X., Song, Y., Yang, J., Wang, W., Ren, H., Dong, M., Feng, Y., Yin, H.,
and Li, J. (2022).** Toward accurate mapping of 30-m time-series global
impervious surface area (GISA). *International Journal of Applied Earth
Observation and Geoinformation* 109, 102787.
`10.1016/j.jag.2022.102787` — peer-reviewed paper; a finding relied on, and the
correction of a misattribution. **This, not the 2021 GISA paper, is the source
of the 28.35 percent producer's-accuracy difference between GISA and GAIA**
that `README.md`, `data/processed/README.md` and `notes/decisions.md` quoted
against `10.1007/s11430-020-9797-9`. The string "28.35" does not occur in the
2021 paper. GISA 2.0 validates against 118,822 ZY-3 test samples and reports F1
scores of 0.935 for itself against 0.721 for GAIA. The sample count of 124,190
that accompanied the figure in this repository matches no published number in
either paper and has been removed rather than re-sourced.
Cited in `README.md`, `data/processed/README.md`, `notes/decisions.md`.

---

## The methods grounding, added 11 September 2026

Eleven literature searches on methods, recorded in
[`notes/grounding-methods.md`](grounding-methods.md). **This group is heavily
borrowed and heavily method-shaped by construction**, which moves the register's
subject-versus-method balance sharply back against the correction the region
grounding made to it a day earlier. That is not drift; it is what a methods pass
is, and the two passes together are the register the paper needs.

**Eleven premises carried into this pass failed, three of them DOIs that resolve
confidently to unrelated papers.** That failure mode is the one this register is
least protected against, because a resolving DOI looks verified. The grounding
document names all eleven; the three bad DOIs are recorded here as well, because
this is where a future reader would look.

**Three DOIs that must not be used.** `10.1016/j.rse.2025.114953` is a paper on
apple-tree disease spectral indices, not the prediction-powered inference work
four digits away at `10.1016/j.rse.2025.114949`. `10.1016/j.spasta.2025.100893`
is "A spatial autoregressive graphical model", not the spatially-lagged
errors-in-variables paper at `10.1016/j.spasta.2025.100909`. And
`10.1016/j.rse.2019.111199` does not resolve at all: 111199 is Stehman and
Foody's article number and their DOI is `10.1016/j.rse.2019.05.018`.

### The accuracy-assessment frame for a continuous field

**Riemann, R., Wilson, B. T., Lister, A., and Parks, S. (2010).** An effective
assessment protocol for continuous geospatial datasets of forest characteristics
using USFS Forest Inventory and Analysis (FIA) data. *Remote Sensing of
Environment* 114, 2337–2352.
`10.1016/j.rse.2010.05.010` — peer-reviewed paper; a method applicable and not
yet applied. **The primary methodological source for assessing a continuous
field**, which is what this project's layers are. It is the protocol the NLCD
percent-impervious assessment cites when it sets Olofsson aside, so it is the
citation at the root of the argument that recommendations 4 and 5 of the
good-practice standard do not apply here.
Cited in `notes/grounding-methods.md`.

**Wickham, J., Stehman, S. V., Sorenson, D., Gass, L., and Dewitz, J. (2023).**
Thematic accuracy assessment of the NLCD 2019 land cover for the conterminous
United States. *GIScience & Remote Sensing* 60.
`10.1080/15481603.2023.2181143` — peer-reviewed paper; a finding relied on, for
scale rather than for method. Level II overall accuracy of 77.5 percent with a
standard error of 1 percent, rising to 87.1 percent when a match to an alternate
reference label counts. It is here so that a reader knows what a normal
categorical land-cover accuracy looks like before judging any product this
project uses.
Cited in `notes/grounding-methods.md`.

### Prediction-powered inference

**Angelopoulos, A. N., Bates, S., Fannjiang, C., Jordan, M. I., and Zrnic, T.
(2023).** Prediction-powered inference. *Science* 382, 669–674.
`10.1126/science.adi6000` — peer-reviewed paper; a method not applied.
**Borrowed method literature, from statistics and machine learning.** The
framework that makes an accuracy assessment possible with a small reference set
and a large map: an estimate from all predictions, bias-corrected by a labelled
subset, valid whatever the model's quality.
Cited in `notes/grounding-methods.md`.

**Lu, K., Kluger, D. M., Bates, S., and Wang, S. (2025).** Regression
coefficient estimation from remote sensing maps. *Remote Sensing of Environment*
330, 114949.
`10.1016/j.rse.2025.114949` — peer-reviewed paper; a method not applied, and the
one that would make this project's reference data usable. Its own novelty claim
is narrower than the one attributed to it and is quoted in the grounding.
**A premise failed here**: its effective sample sizes range from 1.2× to 17.4×,
not 1.1 to 2.5, and the largest is an income coefficient, not slope. Its
separation condition — the calibration set "must be separate from the training
dataset used to train the machine learning model" — is the argument for using
the CCD-Rice polygons on the NESDC and GISA layers and not on CCD-Rice itself.
Cited in `notes/grounding-methods.md`, `notes/dataset-leads.md`.

**Kluger, D. M., Lu, K., Zrnic, T., Wang, S., and Bates, S. (2025).**
Prediction-Powered Inference with Imputed Covariates and Nonuniform Sampling.
arXiv.
`10.48550/arXiv.2501.18577` — preprint; a method not applied. The extension Lu
et al. rely on for weighted, stratified and clustered samples, recorded because
the canonical method's i.i.d. assumption is the thing that has to be relaxed for
spatial data.
Cited in `notes/grounding-methods.md`.

**Shirota, S. (2026).** Design-Based Prediction-Powered Inference for Spatial
Data. arXiv.
`10.48550/arXiv.2608.10356` — preprint; a method not applied, and **carried with
a warning about its own standing**. It is the only work found that recasts
prediction-powered inference for spatial labelling, and it is a single-author
preprint four weeks old. It is the source for the statement that canonical PPI
"starts from i.i.d. labelling, whereas spatial labels arrive through survey
designs or covariate-driven mechanisms, and map errors may be spatially
correlated". A preprint is thin ground for a central method and the grounding
says so rather than citing it as settled.
Cited in `notes/grounding-methods.md`.

### Errors-in-variables

**Nab, L., and Groenwold, R. H. H. (2021).** Sensitivity analysis for random
measurement error using regression calibration and simulation-extrapolation.
arXiv.
`10.48550/arXiv.2106.04285` — preprint; a method not applied. The comparison
that recommends regression calibration over simulation-extrapolation when no
validation data exist, which is this project's situation exactly. **Four figures
in one premise failed here**: reliability 0.2 to 0.9 not 0.05 to 0.91, sample
sizes 125 to 1,000 not 125 to 4,000, median bias 1.4 percent not 0.8, and −12.8
percent not −19.0. The 0.8 turned out to be the lower edge of an interquartile
range read as a point estimate.
Cited in `notes/grounding-methods.md`.

**Xu, Q., Li, B., McRoberts, R. E., and Næsset, E. (2026).** Incorporating
remote sensing measurement error for forest inventory. *Big Earth Data*.
`10.1080/20964471.2026.2660552` — peer-reviewed paper; a method not applied.
SIMEX-WLS, which corrects coefficient attenuation for measurement error and
non-constant residual variance together. The second half is not optional here: a
cell mean rests on between 1 and 410 soundings.
Cited in `notes/grounding-methods.md`.

**Masjkur, M., Saefuddin, A., Mangku, I., Folmer, H., Van der Vlist, A., and
Grzegorczyk, M. (2025).** Bias correction methods for spatially lagged
covariates measured with errors. *Spatial Statistics* 68, 100909.
`10.1016/j.spasta.2025.100909` — peer-reviewed paper; a method not applied.
Directly on point because this project's spatial null **is** a spatially lagged
covariate, so the benchmark the land-cover models are judged against is itself
measured with error. Of Monte Carlo expectation-maximisation, instrumental
variables and Bayesian analysis, it finds Bayesian analysis best.
Cited in `notes/grounding-methods.md`.

### Reliability, disagreement, and what not to report

**Pontius, R. G. Jr., and Millones, M. (2011).** Death to Kappa: birth of
quantity disagreement and allocation disagreement for accuracy assessment.
*International Journal of Remote Sensing* 32, 4407–4429.
`10.1080/01431161.2011.552923` — peer-reviewed paper; a method applicable and
not yet applied, and **a finding that contests this repository's own errata**.
Its two recommendations are to stop using kappa and to use disagreement
components. Quantity disagreement is the mismatch in class proportions and
allocation disagreement the mismatch in where they are put; only the second
attenuates a regression coefficient, which is why it is the right tool for the
GAIA–GISA comparison this repository reports as a single area difference.
Cited in `notes/grounding-methods.md`, `ERRATA.md`.

**Stehman, S. V., and Foody, G. M. (2019).** Key issues in rigorous accuracy
assessment of land cover products. *Remote Sensing of Environment* 231, 111199.
`10.1016/j.rse.2019.05.018` — peer-reviewed paper; a method applicable and not
yet applied, and **the source of a correction to `ERRATA.md` 6.5**. It names
"three examples of bad practice that are widespread": "the universal application
of 85% target accuracy, normalization of the error matrix, and correction for
chance agreement". The third is kappa, which the errata had been asking for. It
also supplies the six good-practice criteria, the requirement that reference
data be more accurate than the map, and the quality-assurance criterion of two
or more independent interpreters that this project cannot meet.
Verified from the authors' own published highlights sheet hosted by NASA's
Carbon Cycle and Ecosystems office, which cites the DOI directly; the article
itself is paywalled.
Cited in `notes/grounding-methods.md`, `ERRATA.md`.

### Spatial cross-validation, both sides

**Wadoux, A. M. J.-C., Heuvelink, G. B. M., de Bruin, S., and Brus, D. J.
(2021).** Spatial cross-validation is not the right way to evaluate map
accuracy. *Ecological Modelling* 457, 109692.
`10.1016/j.ecolmodel.2021.109692` — peer-reviewed paper; a finding contested, in
the sense that it contests the design this project implemented. Buffered
leave-one-out severely overestimated RMSE in all cases, caused by
over-representation of environmental conditions distinct from those at the
calibration points. It also names the condition under which standard
cross-validation fails — clustered calibration samples — which this project does
not have, and that asymmetry is why the grounding treats the two schemes as
possibly bracketing the truth.
Cited in `notes/grounding-methods.md`.

**Milà, C., Mateu, J., Pebesma, E., and Meyer, H. (2022).** Nearest neighbour
distance matching leave-one-out cross-validation for map validation. *Methods in
Ecology and Evolution* 13, 1304–1316.
`10.1111/2041-210X.13851` — peer-reviewed paper; a method not applied. The
leave-one-out original. **A premise was corrected here**: the k-fold extension
below is Linnenbrink et al., not Milà et al., and the two are a year and a
method apart.
Cited in `notes/grounding-methods.md`.

**Linnenbrink, J., Milà, C., Ludwig, M., and Meyer, H. (2024).** kNNDM CV:
k-fold nearest-neighbour distance matching cross-validation for map accuracy
estimation. *Geoscientific Model Development* 17, 5897–5912.
`10.5194/gmd-17-5897-2024` — peer-reviewed paper; a method not applied. The
prediction-oriented synthesis of the controversy: match the distribution of
nearest-neighbour distances between test and training locations to the
distribution between prediction and training locations, so that validation
"creates predictive conditions during CV that are comparable to what is required
when predicting a defined area". Its own framing of the field as "currently the
subject of controversy" is the honest way to introduce the question in a paper.
Cited in `notes/grounding-methods.md`.

**Ploton, P., Mortier, F., Réjou-Méchain, M., Barbier, N., Picard, N.,
Rossi, V., Dormann, C., Cornu, G., Viennois, G., Bayol, N., and 3 others
(2020).** Spatial validation reveals poor predictive performance of large-scale
ecological mapping models. *Nature Communications* 11, article 4540.
`10.1038/s41467-020-18321-y` — peer-reviewed paper; a finding relied on. The
demonstration that nonspatial validation suggested more than half the variance
explained while spatial validation revealed quasi-null predictive power, and —
the part that matters for this repository's diagnostics — that after random
10-fold cross-validation "the residual structure was completely absorbed" into
the predictions, so residual diagnostics would not have detected the problem.
Cited in `notes/grounding-methods.md`.

**Hawinkel, S., De Meyer, S., and Maere, S. (2022).** Spatial Regression Models
for Field Trials: A Comparative Study and New Ideas. *Frontiers in Plant Science*
13, article 858711.
`10.3389/fpls.2022.858711` — peer-reviewed paper; a finding relied on. The other
half of the residual-diagnostic warning: "the absence of spatial autocorrelation
(SAC) in the model residuals should not be taken as a sign of a good fit, since
it may result from overfitting the spatial trend". Taken with Ploton et al., it
makes residual spatial structure a weak diagnostic in both directions.
**Borrowed method literature, from plant breeding.**
Cited in `notes/grounding-methods.md`.

### Effective degrees of freedom

**Clifford, P., Richardson, S., and Hémon, D. (1989).** Assessing the
Significance of the Correlation between Two Spatial Processes. *Biometrics* 45,
123–134.
`10.2307/2532039` — peer-reviewed paper; a method not applied. The original
correction to the degrees of freedom of a correlation between two autocorrelated
spatial fields, based on a variance approximation.
Cited in `notes/grounding-methods.md`.

**Dutilleul, P., Clifford, P., Richardson, S., and Hémon, D. (1993).** Modifying
the t Test for Assessing the Correlation Between Two Spatial Processes.
*Biometrics* 49, 305–314.
`10.2307/2532625` — peer-reviewed paper; a method not applied. The exact
solution where the 1989 procedure approximates, and the standard citation for an
effective sample size under spatial autocorrelation. Crossref lists all four
authors, which is worth noting because the method is usually called Dutilleul's
alone.
Cited in `notes/grounding-methods.md`.

**Afyouni, S., Smith, S. M., and Nichols, T. E. (2019).** Effective degrees of
freedom of the Pearson's correlation coefficient under autocorrelation.
*NeuroImage* 199, 609–625.
`10.1016/j.neuroimage.2019.05.011` — peer-reviewed paper; a method not applied.
**Borrowed method literature, from neuroimaging.** The clearest modern statement
of the problem: under autocorrelation the effective degrees of freedom are
reduced, the standard error of the sample correlation is biased, and Fisher's
transformation fails to stabilise the variance. Every Pearson and partial
correlation this repository reports over 926 cells is affected.
Cited in `notes/grounding-methods.md`.

### The column field's own uncertainty

**Balasus, N., Jacob, D. J., Lorente, A., Maasakkers, J. D., Parker, R. J.,
Boesch, H., Chen, Z., Kelp, M. M., Nesser, H., and Varon, D. J. (2023).** A
blended TROPOMI+GOSAT satellite data product for atmospheric methane using
machine learning to correct retrieval biases. *Atmospheric Measurement
Techniques* 16, 3787–3807.
`10.5194/amt-16-3787-2023` — peer-reviewed paper; describes a dataset used, and
a method relied on. **This entry closes a gap rather than adding a source.** The
blended field has been a committed band of `methane_composite_2018.tif` since 9
September 2026 and its paper was never entered here, which is the exact omission
this register exists to prevent. It supplies the single-retrieval precisions of
14.5 ppb operational against 11.9 ppb blended, the prior-alignment procedure,
and the two collocation rules the grounding disentangles: 1 h and 5 km for
satellite-to-satellite, 1 h and 100 km with a 250 m elevation limit for
satellite-to-TCCON.
Cited in `notes/grounding-methods.md`, `notes/dataset-leads.md`,
`data/processed/README.md`, `notes/decisions.md`.

**Schutgens, N., Tsyro, S., Gryspeerdt, E., Goto, D., Weigum, N., Schulz, M.,
and Stier, P. (2017).** On the spatio-temporal representativeness of
observations. *Atmospheric Chemistry and Physics* 17, 9761–9780.
`10.5194/acp-17-9761-2017` — peer-reviewed paper; **a finding that contests this
project's central quality metric.** Coverage "is not an effective metric to limit
representation errors", and even after substantial averaging significant
representation errors may remain, larger than typical measurement errors. Its
range of 300 to 50 km and semi-annual to sub-daily brackets this project's
regime, and it names emission sources and orography as the hardest cases, both
of which this study area has.
Cited in `notes/grounding-methods.md`.

**Rijsdijk, P., Eskes, H., Dingemans, A., Boersma, K. F., Sekiya, T.,
Miyazaki, K., and Houweling, S. (2025).** Quantifying uncertainties in satellite
NO2 superobservations for data assimilation and model evaluation. *Geoscientific
Model Development* 18, 483–509.
`10.5194/gmd-18-483-2025` — peer-reviewed paper; a method not applied. The
uncorrelated-plus-correlated decomposition of a superobservation's uncertainty:
the uncorrelated part tends to zero as observations accumulate, the correlated
part does not. This project's composite assumes the whole error behaves like the
first term.
Cited in `notes/grounding-methods.md`.

**Glissenaar, I., Boersma, K. F., Anglou, I., Rijsdijk, P., Verhoelst, T., and
5 others (2025).** TROPOMI Level 3 tropospheric NO2 dataset with
advanced uncertainty analysis from the ESA CCI+ ECV precursor project. *Earth
System Science Data* 17, 4627–4650.
`10.5194/essd-17-4627-2025` — peer-reviewed paper; a method not applied, and the
source of an implementable alternative to weighting by sounding count. It
supplies a temporal error correlation of 30 percent in both the stratospheric
and air-mass-factor uncertainties for the analogous NO2 product, a definition of
spatial representativeness uncertainty computable from within-cell spread, and a
temporal weighting by representativeness rather than by count. **A premise was
corrected here**: the weighting factor is called *f* and is high where
representativeness uncertainty is large, not "1 minus g".
Cited in `notes/grounding-methods.md`.

### The preprocessing chain

**Schuit, B. J., Maasakkers, J. D., Bijl, P., Mahapatra, G., van den Berg, A.-W.,
Pandey, S., Lorente, A., Borsdorff, T., Houweling, S., Varon, D. J., and
8 others (2023).** Automated detection and monitoring of methane super-emitters
using satellite data. *Atmospheric Chemistry and Physics* 23, 9071–9098.
`10.5194/acp-23-9071-2023` — peer-reviewed paper; a method not applied. The
seven-filter preprocessing chain in publication order — albedo-bias-corrected
data, then filtering, then destriping, then scene splitting — including the
methane-precision threshold of 10 ppb that this project's unused precision
variable would support, and the mixed-albedo formula. It also records the
trade this project made silently: looser quality filtering "provides more
coverage but also retains more biased retrievals, especially at the borders of
clouds or along coasts".
Cited in `notes/grounding-methods.md`.

**Nesser, H., Jacob, D. J., Maasakkers, J. D., Lorente, A., Chen, Z., Lu, X.,
Shen, L., Qu, Z., Sulprizio, M. P., and 6 others (2024).** High-resolution US
methane emissions inferred from an inversion of 2019 TROPOMI satellite data:
contributions from individual states, urban areas, and landfills. *Atmospheric
Chemistry and Physics* 24, 5069–5091.
`10.5194/acp-24-5069-2024` — peer-reviewed paper; a method not applied. The only
source found that gives albedo filters *with their measured effect*: a blended
albedo ceiling of 0.75 outside summer and a SWIR albedo floor of 0.05 preserve
69 percent of high-quality retrievals and reduce seasonal regional biases by 7
to 21 percent. This project has 166 cells below that floor and below zero.
Cited in `notes/grounding-methods.md`.

**Sicsik-Paré, A., Fortems-Cheiney, A., Pison, I., Broquet, G., Opler, A.,
Potier, E., Martinez, A., Schneising, O., Buchwitz, M., Maasakkers, J. D.,
Borsdorff, T., and Berchet, A. (2026).** Assessment of the differences in
European CH4 emission estimates from three TROPOMI products. *Atmospheric
Chemistry and Physics* 26, 10423–10454.
`10.5194/acp-26-10423-2026` — peer-reviewed paper; a finding relied on, and the
source of a hard constraint. "A destriping procedure (Borsdorff et al., 2024) is
applied to new XCH4 data from 2024/09/07 (v2.07), but older orbits have not been
reprocessed." This project's 2018 granules are processor version 020400, so the
official destriping cannot be inherited and only a self-implemented one is
available.

**Two defects in this entry were found on 14 September 2026 and are fixed above**,
the second instance of the same failure in an entry committed during the methods
pass. The author list read "Sicsik-Paré, A., Fortems-Cheiney, A., Broquet, G., and
others", which puts the fourth author third and drops Pison entirely; and the page
range read 10423–10450 where the registry gives 10423–10454.

**And the same paper is the methane grounding's retrieval-choice section.**
Assimilating three TROPOMI products into one variational inversion for 2019 over
Europe gives emission budgets of "+2 %" for SRON, "−1 %" for the blended product
and "−33 %" for WFMD against the prior, with a surface-based inversion at "−9 %" —
a 35-point spread from the choice of retrieval alone. "Machine learning
predictions of XCH4 differences point to aerosol scattering and albedo
sensitivity as the largest contributors to the differences." And the mechanism is
structural: TROPOMI "uses the full-physics algorithm RemoTeC and simultaneously
retrieves XCH4, surface albedo and atmospheric scattering properties", so albedo
is a co-retrieved parameter rather than an external contaminant — which is a more
precise statement of this project's own bias-correction limit than "the
correction is incomplete".
Cited in `notes/grounding-methods.md`, `notes/grounding-methane.md`.

### Model class and resolution

**Bourached, A., Bonkhoff, A. K., Schirmer, M. D., Regenhardt, R. W.,
Bretzner, M., and 11 others (2023).** Scaling behaviours of deep learning and
linear algorithms for the prediction of stroke severity. *Brain Communications*
6, article fcae007.
`10.1093/braincomms/fcae007` — peer-reviewed paper; a finding relied on.
**Borrowed method literature, from clinical neuroscience.** The crossover
evidence at sample sizes bracketing this project's: linear regression
significantly better at 100, indistinguishable at 300, deep learning
significantly better at 900.
Cited in `notes/grounding-methods.md`.

**Alwosheel, A., van Cranenburgh, S., and Chorus, C. G. (2018).** Is your
dataset big enough? Sample size requirements when using artificial neural
networks for discrete choice analysis. *Journal of Choice Modelling* 28,
167–182.
`10.1016/j.jocm.2018.07.002` — peer-reviewed paper; a finding relied on.
**Borrowed method literature, from transport choice modelling.** The source for
the ten-times-the-number-of-weights rule of thumb as the most widely used one.
**A premise failed alongside it**: no source could be found for the claim that
successful applications had at least 70,000 observations, and it is not written.
Cited in `notes/grounding-methods.md`.

**Passafaro, T. L., Lopes, F. B., Dórea, J. R. R., Craven, M., Breen, V., and
2 others (2020).** Would large dataset sample size unveil the
potential of deep neural networks for improved genome-enabled prediction of
complex traits? The case for body weight in broilers. *BMC Genomics* 21, article
905.
`10.1186/s12864-020-07181-x` — peer-reviewed paper; a finding relied on, and a
mixed one. A deep network had superior prediction correlation only up to 3
percent of a 63,526-observation training set, and poorer correlation after that,
while having the lowest mean squared error of prediction and lower bias at every
size. Recorded as mixed rather than as supporting one conclusion.
Cited in `notes/grounding-methods.md`.

**Lee, K., Eo, M., Cho, H.-S., Kim, D., and 4 others (2025).** MultiTab: A
Comprehensive Benchmark Suite for Multi-Dimensional Evaluation in Tabular
Domains. arXiv.
`10.48550/arXiv.2505.14312` — preprint; **a finding that contests the convenient
conclusion** about model class. In small-sample regimes most algorithms perform
similarly within overlapping confidence intervals and high-capacity networks
remain competitive, which "challenge[s] the common belief that neural networks
require large datasets to be effective". It is cited because a methods section
that quoted only the crossover evidence would be selective.
Cited in `notes/grounding-methods.md`.

**Sheng, J.-X., Jacob, D. J., Maasakkers, J. D., Zhang, Y., and
Sulprizio, M. P. (2018).** Comparative analysis of
low-Earth orbit (TROPOMI) and geostationary (GeoCARB, GEO-CAPE) satellite
instruments for constraining methane emissions on fine regional scales:
application to the Southeast US. *Atmospheric Measurement Techniques* 11,
6379–6388.
`10.5194/amt-11-6379-2018` — peer-reviewed paper; a finding relied on, and the
ceiling on this whole enterprise. A model transport error standard deviation of
12 ppb, "larger than the instrument errors when aggregated on the 25 km model
grid scale", with a 6 h temporal error correlation — against this project's
between-cell spread of 14.9 ppb, at this project's resolution.
Cited in `notes/grounding-methods.md`.

**Qu, Z., Jacob, D. J., Shen, L., Lu, X., Zhang, Y., Scarpelli, T. R.,
Nesser, H., Sulprizio, M. P., Maasakkers, J. D., and 4 others (2021).** Global
distribution of methane emissions: a comparative inverse analysis of
observations from the TROPOMI and GOSAT satellite instruments. *Atmospheric
Chemistry and Physics* 21, 14159–14175.
`10.5194/acp-21-14159-2021` — peer-reviewed paper; a finding relied on. GOSAT
achieved 232 degrees of freedom for signal for non-wetland emissions against
TROPOMI's 151 despite about 100 times fewer observations, because error
correlation on the inversion grid and spatial inhomogeneity in observation
counts make density less useful than it looks; and its counterweight, that
"finer-scale regional inversions would take better advantage of the TROPOMI data
density". **A premise was refined here**: 232 and 151 are the non-wetland
partition, and the totals including wetlands and OH are 238 and 155.
Cited in `notes/grounding-methods.md`.

### Reporting a negative result

**Halsey, L. G. (2025).** Saying 'no' with confidence: statistical approaches to
test for the absence of an effect. *Biology Letters* 21, article 20250506.
`10.1098/rsbl.2025.0506` — peer-reviewed paper; a method not applied, and **the
one that constrains what this project's paper may claim.** Conventional p-value
analysis "can only argue against the null hypothesis, never in favour of it",
and "around half of scientific research papers falsely report non-significant
results as indicating no effect". Equivalence tests and confidence intervals
address the absence of a meaningful effect; likelihood ratios and Bayes factors
address the absence of any effect. This project's central claim is a statement
in favour of the null and is currently supported by neither.
Cited in `notes/grounding-methods.md`.

### The gap-filling literature, cited as a pattern

Four works cited for what they have in common rather than individually: every
published machine-learning treatment of sparse satellite column fields found by
this search is gap-filling or downscaling, and every one uses meteorology, a
model prior or both as predictors. **None predicts a column from land cover.**
That absence is the strongest available statement about the 2023 thesis's
framing, and it needs the set rather than any one member.

**Qu, Y., Shi, X., Fan, Y., Wang, Z., and Wei, J. (2026).** Reconstructing
two-decade daily high-resolution seamless global land XCO2 records using a hybrid
Transformer–BiLSTM model. *Earth System Science Data* 18, 4279–4301.
`10.5194/essd-18-4279-2026` — peer-reviewed paper; a method not applied.
Predictors include precursor gases, meteorological reanalysis, surface features
and spatiotemporal encodings.

**Cui, L., Yang, H., Qiao, Y., Huang, X., Feng, G., Lv, Q., and
Fan, H. (2024).** Estimating high spatio-temporal resolution XCO2 using spatial
features deep fusion model. *Atmospheric Research* 308, 107542.
`10.1016/j.atmosres.2024.107542` — peer-reviewed paper; a method not applied.

**Xiao, Q., Wan, Y., Han, G., Liu, Y., Liu, Y., Li, X., and Zhou, H. (2026).**
Gap-filled spatiotemporal reconstruction of XCH4 data and analysis of methane
emission patterns. *Atmospheric Pollution Research* 17, 102918.
`10.1016/j.apr.2026.102918` — peer-reviewed paper; a method not applied. The
closest published analogue to anything this project might do with its 97 absent
cells.

**Alcibahy, M., Gafoor, F. A., Mustafa, F., El Fadel, M., Al Hashemi, H.,
Al Hammadi, A., and Al Shehhi, M. R. (2025).** Improved estimation of carbon
dioxide and methane using machine learning with satellite observations over the
Arabian Peninsula. *Scientific Reports* 15.
`10.1038/s41598-024-84593-9` — peer-reviewed paper; a finding relied on.
Gradient boosting with CarbonTracker, MODIS Terra and ERA-5 inputs reached R²
0.98 and RMSE 0.58 ppm for XCO2 but only R² 0.63 and RMSE 13.26 ppb for XCH4,
described there as moderate accuracy. **Methane is the hard one even with the
right predictors**, and that RMSE is comparable to this project's entire
between-cell spread.

All four cited in `notes/grounding-methods.md`.

---

## The inversion frame and the urban layer, added 11 September 2026

Twelve literature rounds after the methods grounding was written. Seven changed
that record's central claim and five are the urban layer's grounding, which had
existed nowhere.

**This group was expected to move the register's balance back toward subject
literature, and it does not.** Of its nineteen role lines, nine are methods,
eight are findings and two are datasets, so the register's method share rises
from 34 to 36 percent rather than falling. The reason is that the correction to
the methods record is itself method literature: the inversion frame, the
information metric, the inversion tool, the emission-factor model and the four
alternatives to prediction-powered inference are nine method entries, and the
urban layer's eight findings do not outweigh them. The expectation was reasonable
and the count settles it the other way.

**A fourth DOI that resolves to the wrong paper.**
`10.1016/j.jclepro.2023.137100` is "Accuracy design optimization of a CNC
grinding machine towards low-carbon manufacturing". The rice emission-factor
paper is `10.1016/j.jclepro.2023.137245` — 145 apart, same journal, same year.
It joins the three found in the methods pass in `NOT_CITATIONS`.

**Six author attributions in the drafts of this pass were wrong before they were
committed**, all of them first-author slips from search-result phrasing rather
than from a registry. They were caught by content-negotiating every DOI for its
author list before writing the citations, which is now the practice this
register's preamble should be read as requiring.

### The inference frame

**Chen, Z., Jacob, D. J., Nesser, H., Sulprizio, M. P., Lorente, A.,
Varon, D. J., Lu, X., Shen, L., Qu, Z., Penn, E., and Yu, Z. (2022).**
Methane emissions from China: a high-resolution inversion of TROPOMI satellite
observations. *Atmospheric Chemistry and Physics* 22, 10809–10826.
`10.5194/acp-22-10809-2022` — peer-reviewed paper; a method **not** applied, and
the work that corrects this repository's methodological framing. It optimises
emissions analytically with a Gaussian mixture model at up to 0.25° × 0.3125° —
this project's own lattice — with log-normal prior errors and information content
obtained from the analytical solution. Its total for China is 65.0 (57.7–68.4)
Tg a⁻¹ with rice paddies at 11.9 (10.7–12.7). **A premise failed here**: the 600
is a state vector size, not a mixture-model member count, and the inversion's
DOFS is 167.
Cited in `notes/grounding-methods.md`.

**Feng, S., Jiang, F., Zhang, Y., Chen, H., Zhuang, H., and 4 others (2025).**
High-resolution regional inversion reveals
overestimation of anthropogenic methane emissions in China. *Atmospheric
Chemistry and Physics* 25, 15121–15143.
`10.5194/acp-25-15121-2025` — peer-reviewed paper; a method not applied, and a
finding relied on twice. RegGCAS-CH4, built on WRF-CMAQ with an ensemble Kalman
filter, giving 45.1 ± 3.8 Tg a⁻¹, 36.5 percent below EDGAR. It also supplies the
regional rice finding: emissions in **Zhejiang**, Fujian and Jiangxi increased,
attributed mainly to rice paddies, with EDGAR faulted for "outdated rice paddy
maps" that "incorrectly overspread rice emissions across non-rice agricultural
grids".
Cited in `notes/grounding-methods.md`.

**Xia, Z., Zhao, W., Xu, Y., Li, C., Dong, R., and Yang, S. (2026).**
High-resolution inversion of urban methane emissions
in the Chengdu–Chongqing economic circle using ground-based observations and a
dynamic error Bayesian framework. *Journal of Cleaner Production* 557, 148229.
`10.1016/j.jclepro.2026.148229` — peer-reviewed paper; a method not applied,
**cited for its existence and design only**. It inverts urban methane at 10 km
and daily resolution. The improvement figures attributed to its dynamic error
weighting could not be verified — the article is paywalled and no abstract
carrying them is indexed — and no number from it is written anywhere here.
Cited in `notes/grounding-methods.md`.

### Information content

**Estrada, L. A., Varon, D. J., Sulprizio, M., Nesser, H., Chen, Z.,
Balasus, N., Hancock, S. E., and 12 others (2025).** Integrated Methane
Inversion (IMI) 2.0: an improved research and stakeholder tool for monitoring
total methane emissions with high resolution worldwide using TROPOMI satellite
observations. *Geoscientific Model Development* 18, 3311–3330.
`10.5194/gmd-18-3311-2025` — peer-reviewed paper; **describes a tool not used,
and it is the most consequential entry added in this pass.** A free open-access
inversion facility at exactly this project's resolution which already ingests the
blended TROPOMI+GOSAT field committed here, whose preview "has no significant
costs" and reports the expected degrees of freedom for signal over a
user-selected domain. It answers for free the feasibility question
`notes/decisions.md` records as gated. It is also the source for the averaging
kernel definition and for four cautions this project shares, including that
"spatial error correlations in the prior estimate are also certainly present but
difficult to define and have been ignored for now". **A premise failed here**:
its default anthropogenic prior is EDGAR v8, not v6.
Cited in `notes/grounding-methods.md`, `notes/dataset-leads.md`.

**He, M., Jacob, D. J., and others (2026).** Attributing 2019–2024 methane
growth using TROPOMI satellite observations. *Science Advances* 12.
`10.1126/sciadv.adz9007` — peer-reviewed paper; a finding relied on. The source
for a global inversion's degrees of freedom for signal of 295 in 2024, "ranging
from 256 to 426 for individual years, reflecting changes in satellite coverage".
Cited in `notes/grounding-methods.md`.

**Shen, L., and others (2023).** National quantifications of methane emissions
from fuel exploitation using high resolution inversions of satellite
observations. *Nature Communications* 14.
`10.1038/s41467-023-40671-6` — peer-reviewed paper; a finding relied on. "Our
inversion can constrain 568 pieces of independent information in the global
spatial distribution of methane emissions."
Cited in `notes/grounding-methods.md`.

**Zhong, H., Shen, L., Wan, F., Qu, M., and Qin, K. (2026).** The added value of
new ground-based observations in improving China's methane emission
quantification. *Atmospheric Measurement Techniques* 19, 4759–4778.
`10.5194/amt-19-4759-2026` — peer-reviewed paper; a finding relied on, and the
most sobering figure in the methods record. TROPOMI alone constrains 113
independent pieces of information over China; adding 17 ground-based sites —
every available in-situ and column station in East Asia — raises that to 134, an
increase of 19 percent.

**Two defects in this entry were found on 14 September 2026 and are fixed above.**
The author list read "Zhong, and others", which is not a citation, and the page
range read 4759–4779 where the registry gives 4759–4778. The paper had been
carried through the methods pass on a search-phrasing citation rather than a
content-negotiated one, which is the failure the register's preamble now warns
against, and it is the first instance found in an entry already committed rather
than in one being drafted.

**And the same paper supplies the region grounding's synthesis anchor**, which is
why it is extended here rather than entered twice. It records that SWIR sensors
"suffer from frequent data gaps due to cloud cover (particularly in southern
China during the monsoon season)" and that "sectoral emission estimates for rice
paddies, lakes, and wetlands – predominantly located in southern China – exhibit
large posterior uncertainties (53 %–69 %), coinciding with low satellite data
availability driven by monsoon-related cloudiness" — the latter attributed to the
authors' own earlier paper, which is not registered because it was not read. It
supplies China's share of the global budget, "nearly 14 % (53 [34–66] Tg a⁻¹ out
of 369 [350–391] Tg a⁻¹)", attributed to the Global Methane Budget and likewise
not registered; the bottom-up disagreement, "at least 30 % ... (e.g., 63 Tg a⁻¹
in EDGARv6 ... versus 48 Tg a⁻¹ from Peking University CH4 version 2
inventory)"; and a national sectoral prior with "coal mining 21.0 Tg a⁻¹ ... rice
paddies 13.7 Tg a⁻¹". **Two alignments with this repository are worth naming**:
the capability statement it reaches for the whole country, that TROPOMI "can
effectively constrain China's total methane emissions" while "estimating
individual sources remains challenging", is this project's own Tier 0 finding at
national scale; and it reads the blended TROPOMI+GOSAT product, which is the
composite's own third band.
Cited in `notes/grounding-methods.md`, `notes/grounding-yrd.md`,
`notes/dataset-leads.md`.

**Varon, D. J., and others (2023).** Continuous weekly monitoring of methane
emissions from the Permian Basin by inversion of TROPOMI satellite observations.
*Atmospheric Chemistry and Physics* 23, 7503–7520.
`10.5194/acp-23-7503-2023` — peer-reviewed paper; a method not applied. The
operational threshold: DOFS above 0.5 as "a practical minimum to estimate total
basin methane emissions with 2σ error ≤ 30 %", met by 124 of 127 weekly
inversions, with low-DOFS inversions "mainly constrained by the prior emission
estimate".
Cited in `notes/grounding-methods.md`.

### The rice emission chain

**Nikolaisen, M., Cornulier, T., Hillier, J., Smith, P., Albanito, F., and
Nayak, D. (2023).** Methane emissions from rice paddies globally: A quantitative
statistical review of controlling variables and modelling of emission factors.
*Journal of Cleaner Production* 409, 137245.
`10.1016/j.jclepro.2023.137245` — peer-reviewed paper; a method not applied.
The generalised additive model over 2,301 field measurements that turns rice
extent into an emission factor, as a function of soil texture, pre-season water
status, growing-season water regime, planting method, cultivar, organic
amendment and climate zone. **Every predictor in it is a mechanism
`notes/grounding-yrd.md` identifies.** Its global mean emission factor is 1.97
kg ha⁻¹ d⁻¹ against the IPCC 2006 Tier 1 value of 1.30.
Cited in `notes/grounding-methods.md`, `notes/dataset-leads.md`.

### The alternatives to prediction-powered inference

**Lee, C. J., Symanski, E., Rammah, A., Kang, D. H., Hopke, P. K., and
Park, E. S. (2024).** A scalable two-stage Bayesian approach accounting for
exposure measurement error in environmental epidemiology. *Biostatistics* 26,
article kxae038.
`10.1093/biostatistics/kxae038` — peer-reviewed paper; a method not applied.
**Borrowed method literature, from environmental epidemiology.** Bayesian
hierarchical models "do not require decomposition of the measurement error into
the classical- and Berkson-type errors", which both regression calibration and
simulation-extrapolation do, and they handle measurement error and spatial
misalignment in one structure — formally this project's problem.
Cited in `notes/grounding-methods.md`.

**VanderWeele, T. J., and Li, Y. (2019).** Simple Sensitivity Analysis for
Differential Measurement Error. *American Journal of Epidemiology* 188,
1823–1829.
`10.1093/aje/kwz133` — peer-reviewed paper; a method **not applicable**, and
recorded for why. **Borrowed method literature, from epidemiology.** It bounds
how strong *differential* measurement error would have to be to explain away an
estimate. This project's error is nondifferential — a land-cover product's
classification error does not depend on the methane column — so the machinery
does not apply, and what matters instead is the direction: nondifferential error
biases toward the null.
Cited in `notes/grounding-methods.md`.

**Cinelli, C., and Hazlett, C. (2020).** Making Sense of Sensitivity: Extending
Omitted Variable Bias. *Journal of the Royal Statistical Society Series B:
Statistical Methodology* 82, 39–67.
`10.1111/rssb.12348` — peer-reviewed paper; a method not applied. **Borrowed
method literature, from econometrics.** The robustness value: how strongly an
unobserved confounder must be associated with both treatment and outcome to
overturn a conclusion.
Cited in `notes/grounding-methods.md`.

**Simonsohn, U., Simmons, J. P., and Nelson, L. D. (2020).** Specification curve
analysis. *Nature Human Behaviour* 4, 1208–1214.
`10.1038/s41562-020-0912-z` — peer-reviewed paper; a method not applied.
**Borrowed method literature, from psychology's replication reform.** The
reporting frame for a result that varies across defensible specifications. This
project has three methane fields, four predictor pairs, two cross-validation
schemes and two weightings, which is forty-eight specifications and therefore a
curve rather than a table.
Cited in `notes/grounding-methods.md`.

### The urban layer

**Wang, X., Jacob, D. J., Nesser, H., Balasus, N., Estrada, L. A.,
Sulprizio, M. P., Cusworth, D. H., Scarpelli, T. R., Chen, Z., East, J. D., and
Varon, D. J. (2026).** Quantifying urban and landfill methane emissions in the
United States using TROPOMI satellite data. *Science Advances* 12.
`10.1126/sciadv.adz9308` — peer-reviewed paper; **the load-bearing citation of
the urban grounding.** Twelve US urban areas 80 percent above the EPA inventory,
landfills the principal cause, gas collection efficiencies averaging 38 percent
against a reported 70. And the separability finding that constrains what an
impervious fraction can do: landfills mapped on facility coordinates correlate
below 0.35 with other sectors, while the three sectors allocated on population
correlate at 0.45 to 0.87 with one another and cannot be separated. **Two
premises failed here**: it is in *Science Advances* rather than *Science*, and
the sector composition attributed to it (landfills 40 percent, gas 9, wastewater
6) is not its; it gives 59 / 25 / 9 / 7 in the inventory and 62 / 23 / 8 / 7 in
the posterior.
Cited in `notes/grounding-urban.md`, `notes/grounding-methods.md`.

**Wang, Y., Fang, M., Lou, Z., He, H., Guo, Y., Pi, X., Wang, Y., Yin, K., and
Fei, X. (2024).** Methane emissions from landfills differentially underestimated
worldwide. *Nature Sustainability* 7.
`10.1038/s41893-024-01307-9` — peer-reviewed paper; a finding relied on **for
its direction only**. The magnitude attributed to it — up to 200 percent
underestimation for individual landfills — was read from a citing paper rather
than from this one, and is not written.
Cited in `notes/grounding-urban.md`, `notes/grounding-methods.md`.

**Luo, J., Wang, H., Li, H., and Zheng, B. (2025).** Structural shifts in
China's oil and gas CH4 emissions with implications for mitigation efforts.
*Nature Communications* 16.
`10.1038/s41467-025-58237-z` — peer-reviewed paper; a finding relied on, and
**the clearest evidence in any of the three grounding records that this
project's impervious layer answers a question the field has posed.** It faults a
global fuel-exploitation product for allocating gas distribution emissions "only
based on population densities without using an urban land cover map", and
records China's oil and gas methane rising about sevenfold from 0.5 to 4.0 Tg
a⁻¹ between 1990 and 2022. Its claimed coverage of 347 prefecture-level cities
could not be verified.
Cited in `notes/grounding-urban.md`, `notes/dataset-leads.md`.

**Chen, X., and Ba, Y. (2026).** City-level carbon emissions data in Southeast
Asia from 2000 to 2020. *Scientific Data* 13.
`10.1038/s41597-026-07320-1` — peer-reviewed paper; describes a dataset not
used. The published precedent for downscaling administrative emission totals
using impervious surface information alongside nighttime lights and urban–rural
settlement distributions, across 4,413 admin-3 units. **It downscales CO₂, not
methane**, and the grounding says so, because a proxy that tracks diffuse
combustion need not track point-like methane sources.
Cited in `notes/grounding-urban.md`.

**Gao, Y., Duan, Y., Zhang, W., Zhao, N., Wang, Y., Ding, Z., Wu, W., Cao, D.,
and Jiang, H. (2026).** Mitigating methane emissions from municipal solid waste
in Chinese cities. *Journal of Environmental Management* 398, 128450.
`10.1016/j.jenvman.2025.128450` — peer-reviewed paper; a finding relied on. The
84.7 percent reduction in municipal solid waste methane in Chinese cities since
2017, with megacities and large cities accounting for 80 percent of the gains.
Shares a second author with the region grounding's agricultural methane paper.
Cited in `notes/grounding-urban.md`.

**Ma, S., Deng, N., Zhao, C., Wang, P., Zhou, C., Sun, C., Guan, D., Wang, Z.,
and Meng, J. (2024).** Decreasing Greenhouse Gas Emissions from the Municipal
Solid Waste Sector in Chinese Cities. *Environmental Science & Technology* 58,
11342–11351.
`10.1021/acs.est.4c00408` — peer-reviewed paper; a finding relied on, and the
one that makes this project's analysis year the pivot. Greenhouse gas emissions
from the sector peaked at 70.6 Tg CO₂-equivalent in **2018** and fell to 47.6 Tg
by 2021.
Cited in `notes/grounding-urban.md`.

**Zhang, S., Huang, X., Lei, M., Zhou, Y., Fei, X., Zhan, L., Chen, Y., and
Zhang, Y. (2026).** Integrating inventory models and satellite observations for
site-level methane emission quantification from MSW landfills in China. *Journal
of Environmental Management* 399, 128672.
`10.1016/j.jenvman.2026.128672` — peer-reviewed paper; describes a dataset whose
distribution is unknown, and **the highest-value urban candidate in
`notes/dataset-leads.md`**. Site-specific information for more than 300 major
landfills, IPCC first-order-decay emissions from 1.015 Mt in 2005 to a peak of
2.161 Mt around 2015 and 1.98 Mt in 2023, and the finding that satellite-detected
instantaneous emissions consistently exceed inventory averages. **A premise was
corrected here**: the provincial series attributed to this work (1.0 Mt in 2003,
1.8 in 2019, 1.6 in 2021) is not its series.
Cited in `notes/grounding-urban.md`, `notes/dataset-leads.md`.

**Dogniaux, M., Maasakkers, J. D., Girard, M., Jervis, D., McKeever, J.,
Schuit, B. J., Sharma, S., Lopez-Noreña, A., Varon, D. J., and Aben, I.
(2025).** Global satellite survey reveals uncertainty in landfill methane
emissions. *Nature*.
`10.1038/s41586-025-09683-8` — peer-reviewed paper; describes a dataset not
used. 1,447 clear-sky GHGSat observations of 151 waste disposal sites across 130
urban areas in 47 countries, 2021–2022, totalling 2.8 Mt CH4 a⁻¹. It includes an
example plume from a wastewater treatment plant near Shanghai, **filtered from
the analysis**, so an illustration rather than a quantified in-domain emission.
Cited in `notes/grounding-urban.md`, `notes/dataset-leads.md`.

**Wang, F., Maksyutov, S., Janardanan, R., Tsuruta, A., Ito, A., Morino, I.,
Yoshida, Y., Tohjima, Y., Kaiser, J. W., Lan, X., Zhang, Y., Mammarella, I.,
Lavric, J. V., and Matsunaga, T. (2022).** Atmospheric observations suggest
methane emissions in north-eastern China growing with natural gas use.
*Scientific Reports* 12.
`10.1038/s41598-022-19462-4` — peer-reviewed paper; a finding relied on, and the
source of the urban grounding's strongest statement about the gas sector's
growth. Urban gas pipelines grew roughly threefold from 298.6 to 935.6 million
metres between 2010 and 2019, "82 % in the city and 18 % in the county seat", and
"the CH4 leakage from those pipelines is not actively monitored". Its inversion
attributes 0.77 of China's 0.87 Tg CH4 yr⁻¹ growth rate to the north-east,
"largely attributable to the growth in natural gas use".
Cited in `notes/grounding-urban.md`.

**Lu, H., Xi, D., Xiang, Y., Su, Z., and Cheng, Y. F. (2025).** Vehicle–canine
collaboration for urban pipeline methane leak detection. *Nature Cities*.
`10.1038/s44284-024-00183-w` — peer-reviewed paper; a finding relied on. Roughly
4,000 km of distribution pipelines surveyed across 20 Chinese cities, with
detection vehicles identifying 220 leak areas and canines pinpointing 432
individual release sources; underground steel pipelines and aboveground risers
were particularly prone, and leak density varied notably between cities.
Cited in `notes/grounding-urban.md`.

**Zhou, S., Gong, H., Chen, X., Wang, X., Wang, H., Zhang, Y., Zhu, D.,
Cao, X., Li, S., and Dai, X. (2024).** A Dataset of Distribution and
Characterization of Underground Wastewater Treatment Plants in China.
*Scientific Data* 11.
`10.1038/s41597-024-03815-x` — dataset paper; describes a dataset not used.
Facility-level coverage of one of the three population-allocated sectors, in a
class of plant noted as preferring southeastern coastal locations, which is this
domain. **A premise was narrowed here**: the record's title names underground
plants, and the aboveground count of 2,464 attributed to it is unverified.
Cited in `notes/dataset-leads.md`.

---

## Coal, building form and the proxy comparison, added 13 September 2026

Ten literature rounds after the urban grounding, with the Tier 0 computation
between them. **Most of this group is subject literature rather than method, and
it does what the urban pass was expected to do and did not**: the register's
method share falls from 36 to 34 percent and its dataset share rises from 18 to
20, on fourteen new entries of which two are methods. That is the first move
back toward subject literature since the region pass.

**A fifth DOI that does not resolve, and a new failure mode.** The
population-change evaluation was carried as `10.1038/s41599-026-07688-w`, which
returns nothing. The article number is right and the **prefix is wrong**:
*Humanities and Social Sciences Communications* registers under 10.1057. The
four earlier bad DOIs resolved confidently to the wrong paper; this one resolves
to nothing at all, which is the safer failure and still one the register has to
record.

### Coal, the sector four grounding passes missed

**Sheng, J., Song, S., Zhang, Y., Prinn, R. G., and Janssens-Maenhout, G.
(2019).** Bottom-Up Estimates of Coal Mine Methane Emissions in China: A Gridded
Inventory, Emission Factors, and Trends. *Environmental Science & Technology
Letters* 6, 473–478.
`10.1021/acs.estlett.9b00294` — peer-reviewed paper; **describes a dataset not
used, and supplies the load-bearing claim of the coal finding.** At 0.25 by 0.25
degrees, this project's own resolution, from a public database of more than
10,000 Chinese mines for 2011 — 25 times more than EDGAR v4.2 and 2.5 times more
than v4.3.2 — it states that "Anhui and Liaoning are the provinces that emit the
most in the east and north, respectively", and that EDGAR's provincial
contributions "differ significantly from the gridded inventory results". Anhui
is one of this study's four provinces. Whether the inventory is distributed could
not be established: the paper is paywalled and two open routes refused.
Cited in `notes/grounding-yrd.md`, `notes/dataset-leads.md`.

**Liu, D., Yao, Y., Tang, D., Tang, S., Che, Y., and Huang, W. (2009).** Coal
reservoir characteristics and coalbed methane resource assessment in Huainan and
Huaibei coalfields, Southern North China. *International Journal of Coal
Geology* 79, 97–112.
`10.1016/j.coal.2009.05.001` — peer-reviewed paper; a finding relied on. The
coalfield's physical scale: 131.45 Mt of raw coal in 2010, 1.1 × 10¹² m³ of
coalbed methane, minable seam thicknesses of 18 to 32 m in Huainan and 8 to 18 m
in Huaibei, and in-place gas content of 8 to 16 and 10 to 30 m³ per tonne. It is
in northern Anhui, inside the analysis lattice.
Cited in `notes/grounding-yrd.md`.

**Wei, Q., Chen, S., Yi, W., Gui, H., Jiang, W., Li, F., and Li, S. (2024).**
Gas content, geochemical characteristics and implications of coalbed methane
from the Deep Area of Qi'Nan Coalmine in Huaibei Coalfield. *Scientific Reports*
14.
`10.1038/s41598-024-79922-x` — peer-reviewed paper; a finding relied on. A
mine-specific measurement inside the coalfield: total gas content 4.58 to 12.33
m³ per tonne averaging 8.83, with methane at 92.83 to 99.22 percent of the gas.
Recorded beside the coalfield-scale figures because the two are different
quantities and were nearly conflated.
Cited in `notes/grounding-yrd.md`.

**Zhu, A., Wang, Q., Liu, D., and Zhao, Y. (2022).** Analysis of the
Characteristics of CH4 Emissions in China's Coal Mining Industry and Research on
Emission Reduction Measures. *International Journal of Environmental Research
and Public Health* 19, 7408.
`10.3390/ijerph19127408` — peer-reviewed paper; a finding relied on, for
national scale. 15.8 Tg of methane released per year by Chinese coal mining in
2018, 11.8 after deducting recycling, a weighted emission factor of 6.77 m³ per
tonne, and Shanxi at 35.5 percent of the national total. Its Shanxi share agrees
independently with Sheng et al.'s 35 percent, which is why both are kept.
Cited in `notes/grounding-yrd.md`.

### The proxy comparison

**Li, L., Fu, S., Zhou, X., Xiao, K., Cao, X., Zhang, B., Li, F., Li, H.,
Lu, Y., Liang, C., Liu, Q., Yuan, Y., and Deng, F. (2026).** Cross-sectional
accuracy does not imply the reliability of population change in gridded
population datasets of China. *Humanities and Social Sciences Communications*.
`10.1057/s41599-026-07688-w` — peer-reviewed paper; a finding relied on, and
**the reason impervious fraction is the better proxy for this project's
question.** Six time-series population datasets show cross-sectional Pearson's r
against Chinese township census data above 0.8 and severely limited ability to
represent decadal change, with substantial inaccuracies in identifying decline
trends. **The prefix is 10.1057 and not 10.1038**; see above.
Cited in `notes/grounding-urban.md`.

**Láng-Ritter, J., Keskinen, M., and Tenkanen, H. (2025).** Global gridded
population datasets systematically underrepresent rural population. *Nature
Communications* 16.
`10.1038/s41467-025-56906-7` — peer-reviewed paper; **a finding relied on and
contested.** Validated against reported resettlement from 307 large dam projects
in 35 countries, it reports negative biases of −53 percent for WorldPop through
−84 for GHS-POP. WorldPop's team has published a rebuttal disputing the claim of
systematic rural underrepresentation, and the grounding names both sides rather
than choosing — the same treatment this register gives the rice-paddy exchange.
Cited in `notes/grounding-urban.md`.

**Wei, S., Lin, Y., Zhang, H., Wan, L., Lin, H., and Wu, Z. (2021).** Estimating
Chinese residential populations from analysis of impervious surfaces derived
from satellite images. *International Journal of Remote Sensing* 42, 2303–2326.
`10.1080/01431161.2020.1841322` — peer-reviewed paper; **a finding contested, in
the sense that it contests this project's own predictor.** Shanghai downtown's
census of 6,008,068 against model estimates of 1,065,729 to 1,435,820 across
fourteen grid resolutions, "greatly underestimated in the model without taking
the vertical building information into consideration". Shanghai is one of the
four provinces.
Cited in `notes/grounding-urban.md`.

### Building form

**Zhang, Y., Wang, Y., Dong, Q., Chen, X.-J., Zhang, F., Li, X., and Liu, Y.
(2026).** Mapping three decades of urban growth in China: a 30 m annual building
height dataset (1990–2019). *Earth System Science Data* 18, 5329–5355.
`10.5194/essd-18-5329-2026` — peer-reviewed paper; describes a dataset not used.
**The only building-height product whose span contains 2000, 2010 and 2018**,
annual and at 30 m.
Cited in `notes/grounding-urban.md`, `notes/dataset-leads.md`.

**Che, Y., Li, X., Liu, X., Wang, Y., Liao, W., Zheng, X., Zhang, X., Xu, X.,
Shi, Q., Zhu, J., Zhang, H., Yuan, H., and Dai, Y. (2024).** 3D-GloBFP: the
first global three-dimensional building footprint dataset. *Earth System Science
Data* 16, 5357–5374.
`10.5194/essd-16-5357-2024` — peer-reviewed paper; describes a dataset not used.
1.66 billion buildings, validated in China against CNBH.
Cited in `notes/grounding-urban.md`.

**Wu, W.-B., Ma, J., Banzhaf, E., Meadows, M. E., Yu, Z.-W., Guo, F.-X.,
Sengupta, D., Cai, X.-X., and Zhao, B. (2023).** A first Chinese building height
estimate at 10 m resolution (CNBH-10 m) using multi-source earth observations
and machine learning. *Remote Sensing of Environment* 291, 113578.
`10.1016/j.rse.2023.113578` — peer-reviewed paper; describes a dataset not used.
10 m for 2020, root mean square error 4.65 m validated across 63 cities. One
epoch only, which is the cross-sectional half of the trade-off the building-form
literature states.
Cited in `notes/grounding-urban.md`.

**Zhang, Y., Zhao, H., and Long, Y. (2025).** CMAB: A Multi-Attribute Building
Dataset of China. *Scientific Data* 12.
`10.1038/s41597-025-04730-5` — dataset paper; describes a dataset not used, and
**the one carrying the attribute closest to the mechanism.** Building-instance
level with function among its attributes, which would separate residential from
industrial without inferring it from volume — the distinction the urban record
identifies as what an impervious footprint cannot make.
Cited in `notes/grounding-urban.md`, `notes/dataset-leads.md`.

### Tip-and-cue, and two in-domain observations

**Maasakkers, J. D., Varon, D. J., Elfarsdóttir, A., McKeever, J., Jervis, D.,
Mahapatra, G., Pandey, S., Lorente, A., Borsdorff, T., Foorthuis, L. R.,
Schuit, B. J., Tol, P., van Kempen, T. A., van Hees, R., and Aben, I. (2022).**
Using satellites to uncover large methane emissions from landfills. *Science
Advances* 8.
`10.1126/sciadv.abn9683` — peer-reviewed paper; a method not applied. The
published tip-and-cue route: TROPOMI identifies the hotspot, a targeted
instrument resolves the facility. Landfills in Buenos Aires, Delhi, Lahore and
Mumbai emitting 3 to 29 t h⁻¹, city emissions 1.4 to 2.6 times inventory, and
landfills contributing 6 to 50 percent. **This project has the tip and not the
cue**, and Tier 0 establishes that its own tip lacks the sensitivity to
constrain a single large landfill independently of the prior.
Cited in `notes/grounding-urban.md`.

**Pang, X., Shang, Q., Chen, L., Sun, S., Zhao, G., and 6 others (2025).**
Study of spatiotemporal variation and annual
emission of CH4 in Shaoxing Yangtze River Delta, China, using a portable CH4
detector on the UAV. *Journal of Environmental Sciences* 151, 140–149.
`10.1016/j.jes.2024.03.045` — peer-reviewed paper; describes a dataset not used.
**In-domain city-scale methane observation in Zhejiang**, April 2022 to February
2023, estimating roughly 69 t km⁻² yr⁻¹ and describing that as higher than other
cities worldwide. Its period does not overlap 2018.
Cited in `notes/dataset-leads.md`.

**Fu, S., Qing, X., Zang, K., Lin, Y., Liu, S., and 5 others (2026).**
Observational insights into atmospheric CO2 and CO at
the urban canopy layer top in Metropolitan Shanghai, China. *Atmospheric
Chemistry and Physics* 26, 5477–5496.
`10.5194/acp-26-5477-2026` — peer-reviewed paper; describes a dataset **not
used and not usable for this question**, which is why it is registered. Nearly
two years of continuous in-situ measurement from the 632 m Shanghai Tower inside
the lattice, by cavity ring-down spectrometer — of CO2 and CO, not methane. It
is recorded because the platform exists in the right place and a methane channel
on it would be the in-domain urban observation this project lacks.
Cited in `notes/dataset-leads.md`.

---

## The rice grounding and the three synthesis anchors, added 14 September 2026

Eight rounds of literature on rice and three review-level searches, one for each
layer. **This group is almost entirely subject literature**, which is what the
pass was for: of twenty-three new entries, six describe datasets, one describes
a body of methods, and sixteen are findings relied on. That continues the move
back toward subject literature that the coal-and-urban pass began.

**One entry is a preprint and is marked as one.** Long and others (2026) is an
EGUsphere discussion paper, not peer-reviewed, and it is cited for a figure it
summarises from three other studies rather than for its own result. The register
has not held a preprint before; this one is kept because the figure it supplies —
urban inventories low by a factor of two to three — could not be sourced anywhere
peer-reviewed and because the preprint's own three-city result usefully qualifies
it.

**Two deposits carry mangled author metadata and it comes through unaltered.**
The APRA500 Zenodo record gives four of eight authors as single braced strings
with given and family names run together, and the figshare Northeastern China
record lower-cases three given names and mis-cases a fourth. Both are what the
registry returns and both are carried as returned, which is the same treatment
`scripts/build_references_bib.py` documents for the "Da Pan" string and the
authorless AR6 chapter. The ChinaRiceCalendar precedent applies: where a deposit
and a paper disagree about authorship, the paper's citation is the one used in
prose.

**Two figures attributed to registered works are one citation step from their
primary sources**, and the entries say so. Zhong and others (2026) attribute
China's share of the global budget to the Global Methane Budget and the 53-to-69
percent posterior uncertainties to their own earlier paper; neither primary source
is registered, because neither was read.

### The rice products

**Han, J., Zhang, Z., Luo, Y., Cao, J., Zhang, L., Cheng, F., Zhuang, H.,
Zhang, J., and Tao, F. (2021).** NESEA-Rice10: high-resolution annual paddy rice
maps for Northeast and Southeast Asia from 2017 to 2019. *Earth System Science
Data* 13, 5969–5986.
`10.5194/essd-13-5969-2021` — peer-reviewed paper; **describes a dataset not
used, and the entry exists to record why.** 10 m, annual, 2017 to 2019, which
would have made it the best-resolved product covering this project's analysis
year. Its "Northeast Asia" is Liaoning, Jilin and Heilongjiang with Korea and
Japan, and its "Southeast Asia" is Indonesia, Thailand, Vietnam, Myanmar, the
Philippines and Malaysia. **The Yangtze River Delta is in neither.** Reported
against subnational statistics at R² 0.80 to 0.97.
Cited in `notes/grounding-rice.md`, `notes/dataset-leads.md`.

**Han, J., Zhang, Z., Luo, Y., Cao, J., Zhang, L., Cheng, F., Zhuang, H., and
Zhang, J. (2021).** APRA500: a 500 m annual paddy rice dataset for monsoon Asia
using multisource remote sensing data. Zenodo.
`10.5281/zenodo.5555721` — the deposit, fetched. CC-BY-4.0, twenty-eight files:
one GeoTIFF archive per year from 2000 to 2020 plus three-year composites, about
1.7 MB each. The API returns the file listing and a request for
`paddyRice2018.zip` returns HTTP 200 from this machine, so the status in
`notes/dataset-leads.md` is **verified accessible**. It is the deposit for Han
and others (2022), already in the register, and it is the only rice product of
any kind that covers all three of the thesis's years.
Cited in `notes/grounding-rice.md`, `notes/dataset-leads.md`.

**Wei, J., Cui, Y., Luo, W., and Luo, Y. (2022).** Mapping Paddy Rice
Distribution and Cropping Intensity in China from 2014 to 2019 with Landsat
Images, Effective Flood Signals, and Google Earth Engine. *Remote Sensing* 14,
759.
`10.3390/rs14030759` — peer-reviewed paper; **describes a dataset not used, and
in domain.** The EFSP method: single and double paddy rice and cropping intensity
for China at 30 m, 2014 to 2019, from more than 684,000 Landsat scenes on Earth
Engine. Its accuracies are "producer (user) accuracy and kappa coefficients
ranging from 0.92 to 0.96 (0.76–0.87) and 0.67–0.80, respectively", with
determination coefficients against statistics "higher than 0.88". **Producer's
accuracy exceeding user's by that margin is over-detection**, which is the
damaging direction for a per-cell fraction.
Cited in `notes/grounding-rice.md`, `notes/dataset-leads.md`.

**Fang, H., Liang, S., Chen, Y., Ma, H., Li, W., He, T., Tian, F., and
Zhang, F. (2024).** A comprehensive review of rice mapping from satellite data:
Algorithms, product characteristics and consistency assessment. *Science of
Remote Sensing* 10, 100172.
`10.1016/j.srs.2024.100172` — peer-reviewed review; **describes a body of methods
and twenty-five products, and supplies three findings relied on.** It assesses
consistency among 3 global and 22 regional products for China, Heilongjiang and
Vietnam, and concludes that "different products share low consistency in
fragmented rice fields", that subtropical and tropical cloud and complex cropping
patterns challenge accurate mapping, that "currently it still lacks paddy rice
maps with both large spatial coverage, high spatial resolution, and long time
series", and that "deficiency of ground-truth samples impedes product development
and validation". The last of those is the conclusion this repository reached
independently about its own accuracy assessment.
Cited in `notes/grounding-rice.md`, `notes/dataset-leads.md`.

**Hou, D., Chen, J., Feng, J., Ji, C., Dong, J., Du, G., and Yang, L. (2025).**
A 30-m annual paddy rice dataset in Northeastern China during period 2000-2023.
figshare.
`10.6084/m9.figshare.28407710` — the deposit, not fetched; **describes a dataset
not used, and out of domain.** Registered so that the reason is on record: the
title names *Northeastern* China. Its deposit metadata lower-cases three given
names and mis-cases a fourth, and the BibTeX carries that unaltered.
Cited in `notes/grounding-rice.md`, `notes/dataset-leads.md`.

**Zhao, Z., Zhang, G., Dong, J., Yang, J., Fan, C., Liu, R., and Xiao, X.
(2026).** Mapping paddy rice distribution and cropping intensity in South and
Southeast Asia (1995–2024) at 30 m resolution. *Earth System Science Data* 18,
5583–5599.
`10.5194/essd-18-5583-2026` — peer-reviewed paper; **describes a dataset not
used, and out of domain.** Kept because of its authorship: Zhang and Xiao are
the first and second authors of the paddy-rice-and-XCH4 Reply below, so the group
that established the 0.5-degree correlation has since built the high-resolution
map that correlation called for — for South and Southeast Asia rather than for
China.
Cited in `notes/grounding-rice.md`, `notes/dataset-leads.md`.

### Water regime, temperature and the diurnal cycle

**Runkle, B. R. K., Suvočarev, K., Reba, M. L., Reavis, C. W., Smith, S. F.,
Chiu, Y.-L., and Fong, B. (2019).** Methane Emission Reductions from the
Alternate Wetting and Drying of Rice Fields Detected Using the Eddy Covariance
Method. *Environmental Science & Technology* 53, 671–681.
`10.1021/acs.est.8b05535` — peer-reviewed paper; a finding relied on. The
water-regime effect measured by flux tower rather than chamber: "cumulative CH4
emissions in the production season were in the range of 7.1 to 31.7 kg CH4-C
ha⁻¹ for the AWD treatment and in the range of 75.7–141.6 kg CH4-C ha⁻¹ for the
DF (delayed flood) treatments", over two fields and three years. **Both ranges
are quoted rather than a single ratio**, because the ratio between them runs from
2.4 to 20 depending on which ends are taken. The site is in Arkansas, which is
recorded as a limit on transfer.
Cited in `notes/grounding-rice.md`.

**Sun, H., Zhou, S., Fu, Z., Chen, G., Zou, G., and Song, X. (2016).** A two-year
field measurement of methane and nitrous oxide fluxes from rice paddies under
contrasting climate conditions. *Scientific Reports* 6.
`10.1038/srep28255` — peer-reviewed paper; **a finding relied on, and the only
in-domain flux measurement in any of the three grounding records.** At the
Zhuanghang Experimental Station, 30°53′N 121°23′E, "CH4 emissions ... increased
by 93% and 161% in the 'warm and dry' season of 2013 ... compared to the normal
season of 2014" for two cultivars, with mean seasonal air temperature 2.3 °C
higher, while yield fell 13 to 19 and 7 to 12 percent. The site's nearest cell
centre in this project's lattice is 30.825°N, 121.425°E, a covered cell with 34
soundings whose single-season rice fraction is within a thousandth of the lattice
median.
Cited in `notes/grounding-rice.md`.

**Qian, H., Zhang, N., Chen, J., Chen, C., Hungate, B. A., Ruan, J., Huang, S.,
Cheng, K., Song, Z., Hou, P., and twelve others (2022).** Unexpected Parabolic
Temperature Dependency of CH4 Emissions from Rice Paddies. *Environmental
Science & Technology* 56, 4871–4881.
`10.1021/acs.est.2c00738` — peer-reviewed paper; a finding relied on. Warming
stimulates paddy CH4 most strongly at a background flooded-stage air temperature
near 26 °C and less both below and above, explained by divergent responses of
plant growth, methanogens and methanotrophs; 1 °C of warming is estimated to
raise Chinese paddy emissions by 12.6 percent, more than leading ecosystem models
give. **A parabolic response is why no single temperature covariate would carry
the effect either**, which is the argument's second step.
Cited in `notes/grounding-rice.md`.

**Wassmann, R., Alberto, M. C., Tirol-Padre, A., Hoang, N. T., Romasanta, R.,
Centeno, C. A., and Sander, B. O. (2018).** Increasing sensitivity of methane
emission measurements in rice through deployment of 'closed chambers' at
nighttime. *PLOS ONE* 13, e0191352.
`10.1371/journal.pone.0191352` — peer-reviewed paper; **a finding relied on, and
the one this pass was asked to report first.** Over four cropping seasons of eddy
covariance, "CH4 fluxes were very low from 0000-0630H and started to increase at
around 0700H - 0830H, reached a peak at around 1330H - 1530H, and then decreased
to low values again after 1900H", with "a very strong linear relationship between
nocturnal emissions (12-h periods) and the full 24-h periods resulting in an
R2-value of 0.8419". **The hours are the paper's and not the ones carried into
this pass**, which had them as 0800H and 1300–1500H.
Cited in `notes/grounding-rice.md`.

**Li, H., Peng, C., Helbig, M., Zhao, M., Guo, H., and Zhao, B. (2024).**
Nocturnal peak methane flux diel patterns in rice paddy fields. *Agricultural and
Forest Meteorology* 358, 110238.
`10.1016/j.agrformet.2024.110238` — peer-reviewed paper; a finding relied on, and
one that complicates the finding above rather than confirming it. A pronounced
single daytime peak at 13:30–14:30 in the early rice stage, but daytime emissions
with no peak and below night-time levels during the reproductive stage under water
limitation and high temperature. **So the sign of the diurnal misalignment with a
13:30 overpass changes within a season at one site.**
Cited in `notes/grounding-rice.md`.

### The cropping-system transition, measured as extent

**Jiang, M., Xin, L., Li, X., Tan, M., and Wang, R. (2018).** Decreasing Rice
Cropping Intensity in Southern China from 1990 to 2015. *Remote Sensing* 11, 35.
`10.3390/rs11010035` — peer-reviewed paper; a finding relied on. From 1990 to
2015 the sown area of double-cropping rice in southern China "decreased by
61054.5 km2", single-cropping "increased by 20,110.7 km2", the multiple cropping
index fell "from 148.3% to 129.3%", the double-cropping proportion fell by 20
percent, and "the most dramatic changes occurred in the Middle-Lower Yangtze
Plain" — this project's domain. **The quantities are sown area**, which is the
distinction the rice record draws from planted area, and a nineteen-point fall in
croppings per field is an emission reduction invisible to any measurement of
extent. Volume 11 with a 2018 issue date; it had been carried as 2019.
Cited in `notes/grounding-rice.md`.

### The inversion precedents, in two directions

**He, C., Lu, X., Li, S., Huang, X., Xiao, H., Song, C., Li, T., Yuan, W., and
Fan, S. (2026).** Reconciling Bottom–Up and Top–Down Approaches to Quantify
Sub-Regional Methane Emissions with Improved Inventory and Three-Year
High-Resolution Satellite Measurements. *ACS ES&T Air* 3, 1097–1109.
`10.1021/acsestair.5c00446` — peer-reviewed paper; **a finding relied on, and the
counterweight to the Heilongjiang inversion already in the register.** Over the
Greater Bay Area at 0.25° × 0.3125°, the same resolution as this project's
lattice, it reduces the posterior total's uncertainty by 57 percent — from a prior
range of 1.77 to 3.04 Tg a⁻¹, or 72 percent, to 2.43 to 2.80, or 15 percent —
and puts waste treatment at 1.13 Tg a⁻¹ as the largest anthropogenic source. It
"corrects the overestimated rice emissions over the Pearl River Estuary, where
satellite observations reveal limited rice paddies". **A Chinese sub-regional
inversion revising rice emissions downward, where the Heilongjiang one revised
them up**, and both for spatial rather than magnitude reasons.
Cited in `notes/grounding-rice.md`.

### The rice layer's synthesis anchor

**Mehla, M. K., Singh, A., Jeong, J., and Ran, L. (2026).** Global methane
emissions from rice paddies are now increasingly quantifiable. *Communications
Earth & Environment* 7.
`10.1038/s43247-026-03902-4` — peer-reviewed review; a finding relied on, for
scale. Global estimates made between 1963 and 2025 range from 10 to 280 Tg per
year, recent estimates differ by about 4 Tg with a coefficient of variation of 13
percent, and roughly 67 percent of available global estimates are bottom-up
against 33 percent top-down, with both still depending largely on emission factors
and census data. **A 13 percent coefficient of variation is the ceiling on how
well any single predictor can be expected to do.**
Cited in `notes/grounding-rice.md`.

**Qian, H., Zhu, X., Huang, S., Linquist, B., Kuzyakov, Y., Wassmann, R.,
Minamikawa, K., Martinez-Eixarch, M., Yan, X., Zhou, F., and eleven others
(2023).** Greenhouse gas emissions and mitigation in rice agriculture. *Nature
Reviews Earth & Environment* 4, 716–732.
`10.1038/s43017-023-00482-1` — peer-reviewed review; **a finding relied on, and
the load-bearing citation for this project's first hypothesis.** Its abstract
states that emissions "vary markedly, primarily reflecting the impact of
management practices", naming organic matter additions and continuous flooding
for CH4; that "new rice variety selection, non-continuous flooding and straw
removal strategies reduce GHG emissions by 24%, 44% and 46% on average,
respectively" — cultivar, water and residue, none of which changes extent; and
that "the effect of N input on CH4 emissions is generally positive at low N
rates, but decreases and becomes negative with increasing N rate". It also gives
the global means the figures scale against, 283 kg CH4 ha⁻¹, and 22, 23 and 24 Tg
per year for the 1980s, 2000s and 2010s against a 38 to 55 percent fall in
yield-scaled emissions. **The 24, 44 and 46 percent had been attributed to
different practices when carried into this pass.**
Cited in `notes/grounding-rice.md`, `notes/grounding-yrd.md`.

### The urban layer's synthesis anchor

**National Academies of Sciences, Engineering, and Medicine (2018).** Improving
Characterization of Anthropogenic Methane Emissions in the United States.
National Academies Press.
`10.17226/24987` — consensus study report; a finding relied on, for framing.
"Verifiability is the bedrock upon which inventories should be built if they are
to be widely applicable to policy needs", and "it is very challenging to test the
GHGI against top-down estimates (i.e., verify the GHGI) owing to its high degree
of spatial (national) and temporal (annual) aggregation". **It is 2018, not
recent**, and the age is recorded because an eight-year-old unsuperseded statement
that the inventory cannot be verified is a stronger claim about the field than a
new one. Crossref returns no author list for it, as for the AR6 chapter, and the
BibTeX carries that unaltered.
Cited in `notes/grounding-urban.md`.

**Li, X., Zhang, Y., de Leeuw, G., Yao, X., He, Z., Wu, H., and Yang, Z.
(2025).** A Review of City-Scale Methane Flux Inversion Based on Top-Down
Methods. *Remote Sensing* 17, 3152.
`10.3390/rs17183152` — peer-reviewed review; a finding relied on. It "highlights
the significant discrepancy between top-down inversion results and bottom-up
inventory estimates at the city scale, with inversion uncertainties ranging from
11% to 28%", states that the top-down approach "struggles to attribute emissions
to specific categories", names agricultural soil activity as the largest source
of uncertainty in anthropogenic methane inversions, and proposes isotopic analysis
among four advancements. **It is 2025; it had been carried as 2026.**
Cited in `notes/grounding-urban.md`.

**Whiting, E., Plant, G., Kort, E. A., Aben, I., Biener, K. J., Leguijt, G., and
Maasakkers, J. D. (2026).** Space-based observation of global increase in urban
methane emissions from 2019–2023. *Proceedings of the National Academy of
Sciences* 123, issue 16.
`10.1073/pnas.2504211123` — peer-reviewed paper; a finding relied on. A
tracer–tracer approach on TROPOMI methane and carbon monoxide over 92 global
cities gives "aggregate emissions of 31.2 Tg CH4/y (95%CI: 22.3, 40.4 Tg CH4/y)
in 2023, equivalent to ~10% of the global anthropogenic methane budget"; 72
cities are tracked from 2019, with growth of 10 percent (CI 2 to 17) for C40
cities and 12 percent (CI −1.5 to 25) for others against pledged 34 percent
reductions, and "inventories fail to capture observed growth". **The widely
reported figures of 6 percent above 2019 and inventories at 1.7 to 3.7 percent
are from a press release rather than the paper and are not written.**
Cited in `notes/grounding-urban.md`.

**Long, H., Tsivlidou, M., Ricketts, H., and Allen, G. (2026).** Satellite-based
global monitoring of urban-scale methane emissions. EGUsphere preprint.
`10.5194/egusphere-2026-2570` — **preprint, not peer-reviewed**; a finding relied
on, and the register's first preprint. Discussion opened 20 May 2026, CC-BY-4.0.
It supplies two statements not found peer-reviewed anywhere: that "field studies
quantifying methane emissions in urban areas have found that official bottom-up
inventories can underestimate methane emissions by a factor of 2 to 3", citing
three campaigns; and that "in poorly observed regions (e.g. India, China), where
most of the global population resides, measurement-led validation of national
emissions is even more challenging". Its own result qualifies the first: for
London, Los Angeles and New York it finds "factors of approximately 0.1-2.0,
0.3-2.1, and 5.1-9.2 times the inventory estimates", so the ratio is not
consistently above one.
Cited in `notes/grounding-urban.md`.

### The region's synthesis anchor

**Zhao, P., Zhang, Z., Huang, G., Wang, Z., Canadell, J. G., Ciais, P., Chen, H.,
Chen, S., Cohen, J. B., Dai, F., Gong, P., Jackson, R. B., and fourteen others
(2026).** Two decades of methane budgets at the sub-national scale in China.
*Science Bulletin* 71, 3731–3741.
`10.1016/j.scib.2026.06.019` — peer-reviewed paper; **a finding relied on, and
the hotspot statement this project's domain needed.** Inversion ensembles and
process-based models, both contributed through the Global Carbon Project, for
2000 to 2019: "approximately 60% of national CH4 emissions come from three of the
nine sub-national regions (North China, Southeast China, and Southwest China),
which together account for <30% of China's land area", "dominated by the energy
and agricultural sectors"; "natural sources contribute 9%–16% of the total CH4
budget, but they have the largest relative uncertainties, reaching approximately
150%–170% of their estimated magnitudes"; and decadal anthropogenic increases of
"10.4 [2.7–16.9] Tg CH4 a⁻¹ (BU) and 6.1 [−2.6–10.7] Tg CH4 a⁻¹ (TD)". **This
study area is in Southeast China**, one of the three named regions.
Cited in `notes/grounding-yrd.md`.

**Khanna, N., Lin, J., Liu, X., and Wang, W. (2024).** An assessment of China's
methane mitigation potential and costs and uncertainties through 2060. *Nature
Communications* 15.
`10.1038/s41467-024-54038-y` — peer-reviewed paper; a finding relied on. It names
the sectors whose 2017 emissions are most uncertain as **coal mining, rice
cultivation, wastewater, and enteric fermentation**, and carries "uncertainties
about the coal mine methane emission factor in the range of ±80%", an IPCC range
of "−40% to +70% for the emission factor for rice cultivation", and for industrial
wastewater "−56% to +103% ... in activity data, with 30% uncertainty in maximum
methane-producing capacity and −50% to +100% uncertainty in methane correction
factor". **It does not quantify the spread between inventories**, which is what it
had been carried as supplying.
Cited in `notes/grounding-yrd.md`.

### One dataset for the inventory

**Zhang, C., Dong, J., and Ge, Q. (2022).** Mapping 20 years of irrigated
croplands in China using MODIS and statistics and existing irrigation products.
*Scientific Data* 9.
`10.1038/s41597-022-01522-z` — peer-reviewed paper; describes a dataset not used.
Irrigated cropland for China at 500 m across twenty years. Recorded because the
rice record establishes water regime as the dominant control and
`notes/dataset-leads.md` already carries the water-saving-against-flooding
irrigation maps with no deposit route; this is a second, published, irrigation
layer at the same resolution, and it assimilates statistics, which is the same
care its neighbour entry needs.
Cited in `notes/dataset-leads.md`.

---

## The rice second block, the methane layer and the synthesis, added 14 September 2026

The largest single addition the register has taken: twenty-nine entries from
fifteen rice rounds, eleven methane rounds and three cross-layer searches, of
which twenty-eight are in the BibTeX and one cannot be.

**The balance was expected to shift back toward method and did not.** Under one
consistent classification of the role lines, methods fall from 32.7 to 28.9
percent, findings rise from 45.3 to 48.7, and datasets hold at about 22. The
prediction was that a record about an instrument and a modelling chain would be
method-heavy; what the methane pass actually produced was mostly *findings about*
that chain — a boundary sensitivity, a transport bias, an OSSE limit, a retrieval
spread — rather than methods to apply. Only three of the twenty-nine are methods
not applied. **The register's method share has now fallen in three consecutive
passes**, which is the right direction for a project whose remaining gap is
subject knowledge rather than technique, and it happened for a different reason
than the one predicted.

**A second already-committed entry was found defective and is fixed rather than
duplicated.** Sicsik-Paré and others (2026) carried an author list that put the
fourth author third and dropped the third entirely, and a page range four pages
short. With the Zhong entry fixed in the previous pass, that is two of the
entries drafted during the methods grounding found to have been written from
search phrasing rather than from content negotiation. **Both were found only
because a later pass happened to need the same paper for something else**, which
means the register should be assumed to hold more of them and a systematic
re-negotiation of the methods-pass entries is worth a pass of its own.

**One entry is a Chinese-language journal** and is carried as the registry gives
it, in the journal's own English title and transliterated author names.

**Two entries are deposits whose papers are also registered**, which the register
has done before for GloRice and CCD-Rice: the MUSICA fused product and WetCHARTs
v1.3.1. In both cases the deposit is the thing that would be fetched and the
paper is the thing that documents it.

### Aquaculture, the unrepresented source

**Zhang, L., Wang, X., Huang, L., Wang, C., Gao, Y., Peng, S., Canadell, J. G.,
and Piao, S. (2024).** Inventory of methane and nitrous oxide emissions from
freshwater aquaculture in China. *Communications Earth & Environment* 5.
`10.1038/s43247-024-01699-8` — peer-reviewed paper; **a finding relied on, and
the largest omission any grounding pass has found.** "Total CH4 and N2O emissions
were 2.5 (0.6-4.2) Tg CH4 yr-1 and 18.3 (3.8-32.2) Gg N2O yr-1, respectively,
with 75% coming from ponds and paddy fields", effluxes "5 and 2 times higher than
the average from other inland water bodies", and the framing sentence: the
contribution "remains highly uncertain because **the source has been neglected in
global and national greenhouse gas inventories**". Aquaculture "accounts for half
of the national inland water emissions, and outweighs the land soil methane
sink".
Cited in `notes/grounding-rice.md`, `notes/dataset-leads.md`.

**Dong, B., Xi, Y., Cui, Y., and Peng, S. (2023).** Quantifying Methane Emissions
from Aquaculture Ponds in China. *Environmental Science & Technology* 57,
1576–1583.
`10.1021/acs.est.2c05218` — peer-reviewed paper; a finding relied on, and the
independent bracket on the entry above. From "a database of 55 field
observations", "the total CH4 emission from aquaculture ponds is 1.60 ± 0.62 Tg
CH4 yr–1, with an average growth rate of ~0.03 Tg CH4 yr–2 during the period
2008–2019", and aquaculture species show "a lower (63%) emission intensity" per
unit of animal protein than major livestock. Two estimates by different methods
bracket the source at 1.6 to 2.5 Tg per year.
Cited in `notes/grounding-rice.md`.

**Zhao, J., Zhang, M., Xiao, W., Jia, L., Zhang, X., Wang, J., Zhang, Z.,
Xie, Y., Pu, Y., Liu, S., Feng, Z., and Lee, X. (2021).** Large methane emission
from freshwater aquaculture ponds revealed by long-term eddy covariance
observation. *Agricultural and Forest Meteorology* 308–309, 108600.
`10.1016/j.agrformet.2021.108600` — peer-reviewed paper; **a finding relied on,
and in-domain.** "CH4 flux was measured continuously for four years with eddy
covariance (EC) in an aquaculture pond complex in the Yangtze River Delta,
China": daily flux "0.1 to 16.7 μg m−2 s−1, with an average value of 4.10 ± 3.08
µg m−2 s−1", water temperature the primary driver at every timescale, and
ebullition "the main transport way accounting for 70% ± 4% of the total CH4
flux". Four years of flux tower measurement inside this study region, for a
source neither predictor represents.
Cited in `notes/grounding-rice.md`, `notes/dataset-leads.md`.

**Zhao, J., Zhang, M., Pu, Y., Jia, L., Xiao, W., Zhang, Z., Ge, P., Shi, J.,
Xiao, Q., and Lee, X. (2025).** Dynamic and high methane emission flux in pond
and lake aquaculture. *Journal of Hydrology* 653, 132765.
`10.1016/j.jhydrol.2025.132765` — peer-reviewed paper; a finding relied on, for
regional scale. The Yangtze River Delta "accounts for 26% of China's total
aquaculture area", with both pond and lake aquaculture practised, and pond flux
running well above lake flux.
Cited in `notes/grounding-rice.md`.

**Li, Y., Wang, H., Zeng, Q., Jeppesen, E., Gu, X., and Yan, J. (2026).** Insight
into greenhouse gas emission in freshwater aquaculture ponds in Jiangsu Province:
Variation due to species used and ponds management practice. *Journal of
Environmental Sciences* 160, 732–744.
`10.1016/j.jes.2025.03.042` — peer-reviewed paper; **a finding relied on, and one
of the two largest within-class ratios in this repository.** "The highest CH4 and
N2O fluxes were found in the Crucian carp (Carassius auratus) pond with up to
16,512 ± 3015 µmol/(m2·h)"; "CH4 was the primary contributor to the global
warming potential in traditional earthen ponds, accounting for an average
contribution rate of 87.7" percent; and "the GHG emission intensity per unit of
fish production in traditional earthen ponds was **197 times higher** than that
in-pond raceway systems". All ponds are in Jiangsu, one of this project's four
provinces.
Cited in `notes/grounding-rice.md`, `notes/paper-target.md`.

**Sun, Z., Luo, J., Cao, Z., Shen, M., Qi, T., Gu, X., Yuan, W., and Duan, H.
(2025).** Nationwide spatial distribution of aquaculture ponds in China: Inland
surpassing coastal areas revealed by Satellite remote sensing. *International
Journal of Applied Earth Observation and Geoinformation* 145, 104958.
`10.1016/j.jag.2025.104958` — peer-reviewed paper; **describes a dataset not
used, and the one that would settle the rice–aquaculture confound.** China_AP,
the first 10 m annual aquaculture pond dataset for China for 2016 to 2023, from
119,882 Sentinel-1 and 579,436 Sentinel-2 scenes with individual-pond extraction
accuracy above 90 percent. It covers 2018. **Its 2023 area total and inland share
could not be verified and are not written**; the inland-surpassing-coastal
direction is the paper's own title.
Cited in `notes/grounding-rice.md`, `notes/dataset-leads.md`.

**Chen, J., Lin, C., Xue, K., Song, K., Cao, Z., Ma, R., Ma, D., and
Tong, Y. (2025).** Mapping China Aquaculture Ponds: Integrating a New
Aquaculture Index With Machine Learning. *Earth's Future* 13.
`10.1029/2024EF005637` — peer-reviewed paper; describes a dataset not used. A
second national aquaculture pond mapping, registered as the pair China_AP would
need under the GAIA–GISA rule that two products with different errors are worth
more than one better product. It is also the clearest source in this group for
the classification confound, naming misclassification against salt fields and
rice paddies at national scale; **no sentence from it is quoted, because the
article could not be fetched and the confound is recorded as a direction
only**.
Cited in `notes/dataset-leads.md`.

### Straw, the fallow season, and paddy as wetland

**Bossio, D. A., Horwath, W. R., Mutters, R. G., and van Kessel, C. (1999).**
Methane pool and flux dynamics in a rice field following straw incorporation.
*Soil Biology and Biochemistry* 31, 1313–1322.
`10.1016/S0038-0717(99)00050-4` — peer-reviewed paper; **a finding relied on, and
the best-fitting candidate any pass has found for an unexplained trend.** "A
5-fold increase in total CH4 emissions over the rice growing season was observed
in plots in which rice straw had been incorporated each fall for 4 yr. Total
cumulative CH4 flux, 1 May–1 October 1997, was 8.87 g C m−2 in incorporated,
winter flooded plots ... 1.63 g C m−2 in burned, winter flooded plots". Two
further details matter: "rice yields in this study have not been affected by
straw incorporation", so the effect has no yield signature; and "methane
emissions peaked between 22.00 and 23.00 h", a nocturnal diurnal peak. The site
is in California. **Crossref returns the author list as "Bossio, D" alone**; the
full list is taken from the article's own title page and is recorded here for
that reason.
Cited in `notes/grounding-rice.md`, `notes/paper-target.md`.

**Jiang, Y., Qian, H., Huang, S., Zhang, X., Wang, L., Zhang, L., Shen, M.,
Xiao, X., Chen, F., Zhang, H., and six others (2019).** Acclimation of methane
emissions from rice paddy fields to straw addition. *Science Advances* 5.
`10.1126/sciadv.aau9038` — peer-reviewed paper; a finding relied on, and the
qualification on the entry above. "On average, the IPCC Tier 1 methodology
estimated a 193% increase in CH4 emissions due to long-term straw incorporation
for the studies in our dataset. Yet, long-term straw incorporation stimulated the
CH4 emissions by only 101%" — 48 percent lower than the IPCC estimate — because
"long-term straw incorporation increased soil methanotrophic abundance and rice
root size, suggesting an increase in CH4 oxidation rates through improved O2
transport into the rhizosphere". Its first two authors are the last and first
authors of the rice review already in the register.
Cited in `notes/grounding-rice.md`.

**Martínez-Eixarch, M., Alcaraz, C., Viñas, M., Noguerol, J., Aranda, X.,
Prenafeta-Boldú, F. X., Saldaña-De la Vega, J. A., Català, M. del M., and
Ibáñez, C. (2018).** Neglecting the fallow season can significantly underestimate
annual methane emissions in Mediterranean rice fields. *PLOS ONE* 13, e0198081.
`10.1371/journal.pone.0198081` — peer-reviewed paper; **a finding relied on, and
the one that corrects a committed record.** "Estimated cumulative CH4 emissions
from May to December were 314.1 kg CH4 ha−1", "of which *ca.* 70% were emitted
during the fallow season", following "a bimodal distribution pattern with the
first peak in August (5.0 ± 0.7 mg C-CH4 m−2 h−1) and the second one in October
(20.2 ± 4.2 mg C-CH4 m−2 h−1)" — **the October peak four times the August one.**
Ebre Delta, Catalonia; Mediterranean water management, so it disqualifies the
region record's dilution framing without establishing a Chinese value.
Cited in `notes/grounding-rice.md`, `notes/grounding-yrd.md`.

**Martínez-Eixarch, M., Alcaraz, C., Viñas, M., Noguerol, J., Aranda, X.,
Prenafeta-Boldú, F.-X., Català-Forner, M., Fennessy, M. S., and Ibáñez, C.
(2021).** The main drivers of methane emissions differ in the growing and flooded
fallow seasons in Mediterranean rice fields. *Plant and Soil* 460, 211–227.
`10.1007/s11104-020-04809-5` — peer-reviewed paper; a finding relied on, and the
same group's independent confirmation. "Two thirds of the CH4 is emitted in the
fallow season. Edaphic factors exert more influence during the growing season
whereas agronomic factors have a higher impact in the fallow." **The seasonal
sign reversals carried into this pass are not in the abstract and are not
written.**
Cited in `notes/grounding-rice.md`, `notes/grounding-yrd.md`.

**Zhang, W., Yan, S., Shang, Z., Tang, Z., Wu, L., Li, J., Chen, H., Deng, A.,
Zhang, J., Zhang, X., Zheng, C., and Song, Z. (2026).** Methane Emissions from
Paddy Fields: Not Entirely Attributable to Rice Cultivation. *Scientia
Agricultura Sinica* 59, 824–833, doi:10.3864/j.issn.0578-1752.2026.04.009.
**The DOI is written here without backticks, and that is deliberate.** It
resolves, but the publisher serves HTML in answer to
`Accept: application/x-bibtex`, so content negotiation cannot produce an entry
and `scripts/build_references_bib.py` records it in `EXCLUDED` for the same
reason it records the standard and the textbook. It is the register's first
citation that has a DOI and still cannot be generated. Peer-reviewed paper; **a finding relied
on, and the one that undercuts the attribution itself.** "Paddy CH₄ emissions
were found to be approximately 72.2% to 123.6% of those from their adjacent
natural wetlands"; "estimates based on machine learning models suggest that
natural emissions constitute more than 36% of total paddy CH₄ fluxes"; and yet
"in compiling paddy CH₄ emission inventories, the entirety of CH₄ emitted from
rice paddies is currently accounted for as anthropogenic contribution from rice
cultivation". Two of its authors are co-authors of the rice review in this
register. The journal is Chinese-language and the citation is carried in its own
English title.
Cited in `notes/grounding-rice.md`.

### The methane layer's target and observing chain

**Shahzadi, K., Schneider, M., Lo, N. Y., Hase, F., Meyer, J., Cayoglu, U.,
Borsdorff, T., and Martinez-Velarte, M. C. (2026).** A multi-year global methane
data set obtained by merging observations from TROPOMI and IASI. *Earth System
Science Data* 18, 2153–2177.
`10.5194/essd-18-2153-2026` — peer-reviewed paper; **describes a dataset not
used, and the only finding in any pass that could raise an association rather
than explain it.** Three variables where this project has one: "we define the
lowermost 50 % of the atmosphere as the troposphere and the uppermost 50 % of the
atmosphere as the upper troposphere/stratosphere", giving a total column, a
`tro_XCH4` and a `uts_XCH4`, combined "by means of a Kalman filter that uses the
MUSICA IASI data as the background and the TROPOMI data as the new observation"
over "42 months (from January 2018 to June 2021)", from "about 444 million
individual and high-quality TROPOMI observations" yielding "about 289 million
individual data points". **The information content is smaller than this pass was
briefed to expect**: for the combined tropospheric product "DOFS values are
weakly above 1.0 for almost all locations around the globe", not about 2.4. The
TROPOMI input is a "beta version of the operational S5P product", not this
project's 020400.
Cited in `notes/grounding-methane.md`, `notes/dataset-leads.md`.

**Shahzadi, K., Schneider, M., Lo, N. Y., and Borsdorff, T. (2026).** MUSICA
IASI / TROPOMI RemoTeC fused CH4 data set (version 4.1). Karlsruhe Institute of
Technology.
`10.35097/wq583rnzpmd83m5g` — the deposit, not fetched; the dataset the entry
above documents, on KIT's RADAR repository. Registered because it is the object a
fetch would target and because the tropospheric-column item in the queue depends
on it.
Cited in `notes/grounding-methane.md`, `notes/dataset-leads.md`.

**Liang, R., Zhang, Y., Chen, W., Zhang, P., Liu, J., Chen, C., Mao, H.,
Shen, G., Qu, Z., Chen, Z., Zhou, M., Wang, P., Parker, R. J., Boesch, H.,
Lorente, A., Maasakkers, J. D., and Aben, I. (2023).** East Asian methane
emissions inferred from high-resolution inversions of GOSAT and TROPOMI
observations: a comparative and evaluative analysis. *Atmospheric Chemistry and
Physics* 23, 8039–8057.
`10.5194/acp-23-8039-2023` — peer-reviewed paper; **a finding relied on, and the
one structural feature of this region that is favourable.** A positive boundary
bias of 10 ppbv "would result in a reduction of annual methane emissions by
3.3 Tg a−1 (∼2 %) over the East Asia domain, 1.8 Tg a−1 (∼2 %) over China, and
0.75 Tg a−1 (∼3 %) over eastern China (EC), the most affected region", with the
small effects "as expected from prevailing westerlies in midlatitudes". So this
study area is the worst case in East Asia and the worst case is about 3 percent.
Its first two authors are the first two of the Heilongjiang rice inversion
already in the register.
Cited in `notes/grounding-methane.md`.

**Nesser, H., Bowman, K. W., Thill, M. D., Varon, D. J., Randles, C. A.,
Tewari, A., Cardoso-Saldaña, F. J., Reidy, E., Maasakkers, J. D., and
Jacob, D. J. (2025).** Predicting and correcting the influence of boundary
conditions in regional inverse analyses. *Geoscientific Model Development* 18,
9279–9291.
`10.5194/gmd-18-9279-2025` — peer-reviewed paper; a method not applied. A
predictive metric for boundary-induced error to support domain specification
before an inversion, and a diagnostic metric to assess it afterwards. It puts the
boundary question in the same class as the IMI preview's DOFS estimate: a cheap
gate rather than a result.
Cited in `notes/grounding-methane.md`.

**Stanevich, I., Jones, D. B. A., Strong, K., Parker, R. J., Boesch, H.,
Wunch, D., Notholt, J., Petri, C., Warneke, T., Sussmann, R., Schneider, M.,
Hase, F., Kivi, R., Deutscher, N. M., Velazco, V. A., Walker, K. A., and
Deng, F. (2020).** Characterizing model errors in chemical transport modeling of
methane: impact of model resolution in versions v9-02 of GEOS-Chem and v35j of
its adjoint model. *Geoscientific Model Development* 13, 3839–3862.
`10.5194/gmd-13-3839-2020` — peer-reviewed paper; **a finding relied on, and the
one that makes transport error worse here than generically.** "The model bias
over China, we argue, was caused by weakened vertical advective transport as a
result of a combination of regridding the winds and the strong surface emissions
in China that resulted in CH4 being partly trapped in the boundary layer over the
continent" — so strong emissions are a *precondition* of the bias, which puts it
where the signal is. "At 4°×5° there is up to a 40 % reduction in the tracer
concentrations in the middle and upper troposphere relative to 2°×2.5°, with a
noticeable increase in the tracer concentrations in the lower troposphere ranging
from 10 % to 25 %." **The comparison is between two coarse grids**, not between a
coarse grid and IMI's operating resolution, which is how it was carried into this
pass.
Cited in `notes/grounding-methane.md`.

**Wang, X., Sulprizio, M. P., Zhuge, Y., Martin, R. V., and Jacob, D. J.
(2026).** Technical note: 12 km resolution capability for the global GEOS-Chem
model of atmospheric composition. *Atmospheric Chemistry and Physics* 26,
6857–6867.
`10.5194/acp-26-6857-2026` — peer-reviewed paper; **a method not applied, and
demonstrated over a domain containing this one.** "0.125° × 0.15625° (≈12 km ×
12 km) resolution by exploiting a new GEOS advection data archive (grid-scale
winds)", with "nested-grid simulations ... over eastern China (100–125° E,
17–45° N)" and "application to the Integrated Methane Inversion (IMI) show[ing]
regional-scale results consistent with a 25 km inversion but higher information
content and greater spatial detail". This project's lattice sits entirely inside
that nested domain.
Cited in `notes/grounding-methane.md`.

**Yu, X., Millet, D. B., and Henze, D. K. (2021).** How well can inverse analyses
of high-resolution satellite data resolve heterogeneous methane fluxes? Observing
system simulation experiments with the GEOS-Chem adjoint model (v35).
*Geoscientific Model Development* 14, 7775–7793.
`10.5194/gmd-14-7775-2021` — peer-reviewed paper; **a finding relied on, and the
sharpest bound on the emissions route.** "4D-Var analysis of the TROPOMI data can
improve monthly emission estimates at 25 km even with a spatially biased prior or
model transport errors (42 %–93 % domain-wide bias reduction; R increases from
0.51 up to 0.73). However, when both errors are present, no single inversion
framework can successfully improve both the overall bias and spatial distribution
of fluxes relative to the prior on the 25 km model grid." **This project's
situation has both errors.** The experiment is over North America.
Cited in `notes/grounding-methane.md`.

**Penn, E., Jacob, D. J., Chen, Z., East, J. D., Sulprizio, M. P., Bruhwiler, L.,
Maasakkers, J. D., Nesser, H., Qu, Z., Zhang, Y., and Worden, J. (2025).** What
can we learn about tropospheric OH from satellite observations of methane?
*Atmospheric Chemistry and Physics* 25, 2947–2965.
`10.5194/acp-25-2947-2025` — peer-reviewed paper; a finding relied on, for the
sink. "From the methyl chloroform proxy, one infers a tropospheric lifetime of
methane of τCH4OH = 11.2 ± 1.3 years for 2000" while "atmospheric chemistry
models find a methane lifetime of τCH4OH = 9.7 ± 1.5 years". **Three claims
attributed to this paper are not in it** and are named in the methane record's
closing section; the two lifetime figures written anywhere in this repository are
these.
Cited in `notes/grounding-methane.md`.

**Bloom, A. A., Bowman, K. W., Lee, M., Turner, A. J., Schroeder, R.,
Worden, J. R., Weidner, R., McDonald, K. C., and Jacob, D. J. (2017).** A global
wetland methane emissions and uncertainty dataset for atmospheric chemical
transport models (WetCHARTs version 1.0). *Geoscientific Model Development* 10,
2141–2156.
`10.5194/gmd-10-2141-2017` — peer-reviewed paper; **describes a dataset not used,
and states this project's central confound in its own discussion, in 2017.**
"Rice paddies likely amount to < 20 % of wetland CH4 emissions, and the majority
of rice paddy areas are implicitly excluded from our analysis ... GLWD explicitly
excludes rice paddy extents in China ... However, satellite-based inundation
fraction retrievals are unable to distinguish the temporal variability in
co-located agriculture and natural wetland inundation extent ... The inadvertent
inclusion of co-located rice CH4 emissions is therefore a potential source of
bias in our approach. We note that the distinction between wetland and rice CH4
emissions has yet to be consistently addressed." The same passage names "very
small ponds" among unresolved non-wetland freshwater sources — the aquaculture
source above, identified as a resolution problem nine years earlier.
Cited in `notes/grounding-methane.md`, `notes/dataset-leads.md`.

**Bloom, A. A., Bowman, K. W., Lee, M., Turner, A. J., Schroeder, R.,
Worden, J. R., Weidner, R. J., McDonald, K. C., and Jacob, D. J. (2021).** CMS:
Global 0.5-deg Wetland Methane Emissions and Uncertainty (WetCHARTs v1.3.1).
ORNL DAAC.
`10.3334/ORNLDAAC/1915` — the deposit, not fetched; the version IMI uses as its
wetland default, where the paper above documents version 1.0. Registered because
it is the object a fetch would target and because the wetland prior overlaps the
rice prior in this project's cells.
Cited in `notes/grounding-methane.md`, `notes/dataset-leads.md`.

**Chen, Z., Jacob, D. J., Lin, H., Balasus, N., Hancock, S. E., Estrada, L. A.,
East, J. D., Zhang, Y., Wang, X., He, M., Liu, M., and Varon, D. J. (2026).**
Tropical Wetland Methane Emissions and Trends (2004–2023) Inferred from
Landsat-Based Inundated Vegetation Data. *Environmental Science & Technology* 60,
21159–21167.
`10.1021/acs.est.6c05412` — peer-reviewed paper; a finding relied on, for the
co-location warning generalised: "tropical wetlands are co-located with other
sectors such as livestock and oil and gas production in Africa and South America,
and rice paddies in South Asia, which means inverse analyses are subject to
source misattribution". **Its first author is GRPI's first author**, so the same
group built the Landsat-inundation rice inventory and the Landsat-inundation
wetland inventory and states the co-location problem in both.
Cited in `notes/grounding-methane.md`.

### The cross-layer synthesis

**Desjardins, R. L., Worth, D. E., Pattey, E., VanderZaag, A., Srinivasan, R.,
Mauder, M., Worthy, D., Sweeney, C., and Metzger, S. (2018).** The challenge of
reconciling bottom-up agricultural methane emissions inventories with top-down
measurements. *Agricultural and Forest Meteorology* 248, 48–59.
`10.1016/j.agrformet.2017.09.003` — peer-reviewed paper; **a finding relied on,
and the synthesis in one sentence.** "Inversion modelling is not capable of
distinguishing interspersed sources from different sectors. Overlapping grid
level sources from different sectors are typically grouped and treated as a
single source." Crossref dates it 2018 in volume 248; **it was carried into this
pass as 2017**, which is its online-first year.
Cited in `notes/paper-target.md`.

**France, J. L., Fisher, R. E., Lowry, D., Allen, G., Andrade, M. F.,
Bauguitte, S. J.-B., Bower, K., Broderick, T. J., Daly, M. C., Forster, G., and
fourteen others (2022).** δ13C methane source signatures from tropical wetland
and rice field emissions. *Philosophical Transactions of the Royal Society A*
380.
`10.1098/rsta.2020.0449` — peer-reviewed paper; a finding relied on, for the
isotopic overlap. "Biogenic sources are depleted in 13C, with δ13CCH4 signatures
in the −70 to −50‰ range for sources such as ruminants, wetlands and rice
fields", against thermogenic and pyrogenic sources "as enriched as −15‰", and
pooled literature giving "an average signature of approximately −61 ± 4‰ for all
rice fields". **The ranges carried into this pass — −65 to −55 overall and −63 to
−58 for Asian rice fields — are not this paper's figures and are not written.**
Cited in `notes/paper-target.md`.

**Bakkaloglu, S., Lowry, D., Fisher, R. E., Menoud, M., Lanoisellé, M., Chen, H.,
Röckmann, T., and Nisbet, E. G. (2022).** Stable isotopic signatures of methane
from waste sources through atmospheric measurements. *Atmospheric Environment*
276, 119021.
`10.1016/j.atmosenv.2022.119021` — peer-reviewed paper; a finding relied on, and
the other half of the overlap. The weighted average δ13C for waste sources is
−56.1 ± 2.4‰, measured atmospherically, predominantly in the UK. Against rice at
−61 ± 4‰ the two overlap within one standard deviation, which is why isotopes
separate microbial from thermogenic rather than rice from landfill.
Cited in `notes/paper-target.md`.

**Sherwood, O. A., Schwietzke, S., and Lan, X. (2020).** Global d13C CH4 source
signature inventory 2020. NOAA GML.
`10.15138/qn55-e011` — the deposit, not fetched; **describes a dataset not used,
and the data gap lands on this project's two sectors.** Spatially resolved source
signatures exist for oil and natural gas, coal, biomass and biofuel burning,
ruminants and wild animals, with geological seeps and wetlands from other work;
"for other CH4 sources, the current measurement sample sizes are insufficient to
develop spatial distributions", the sources named being waste and landfills,
termites, and rice. **Two readings of the record's sample counts disagreed and no
count is written.**
Cited in `notes/paper-target.md`.

**Lan, X., Basu, S., Schwietzke, S., Bruhwiler, L. M. P., Dlugokencky, E. J.,
Michel, S. E., Sherwood, O. A., Tans, P. P., Thoning, K., Etiope, G., Zhuang, Q.,
Liu, L., Oh, Y., Miller, J. B., and three others (2021).** Improved Constraints
on Global Methane Emissions and Sinks Using δ13C-CH4. *Global Biogeochemical
Cycles* 35.
`10.1029/2021GB007000` — peer-reviewed paper; describes the dataset above and is
the citation the NOAA record itself asks for. Registered for that reason rather
than for a figure of its own.
Cited in `notes/paper-target.md`.

**Yao, P., Belec, K., Holmstrand, H., Balacky, J., Salam, A., Budhavant, K.,
Manoj, M. R., Joy, K. S., Hossain, Md. A., Singh, A., and six others (2026).**
Distinct dual-isotopic signatures of major methane sources in South Asia.
*Atmospheric Chemistry and Physics* 26, 7765–7787.
`10.5194/acp-26-7765-2026` — peer-reviewed paper; **a finding relied on, and the
one genuine research opening in the synthesis.** South Asian rice paddy methane
is "notably more enriched in δ13C compared to the global mean", with Miller–Tans
values of "−53.8±0.8‰ and −311±6‰", the enrichment in both suggesting "multiple
sources and/or pre-emission oxidation", and the conclusion that "region-specific
isotopic endmembers are therefore critical for accurate source apportionment". A
rice signature at −53.8 is enriched past the waste average of −56.1, so regional
dual-isotope work can separate what global means cannot. **The equivalent
campaign for China has not been done**, and this domain is where it would be
worth doing.
Cited in `notes/paper-target.md`.

---

## The two Sentinel-5P DOIs, resolved

The methane product carries two ESA DOIs and both resolve, to identical titles
and publisher, differing only in registration year and landing page.
`10.5270/S5P-3p6lnwd`, registered 2019, resolves to the ESA Copernicus
data-products catalogue at sentinels.copernicus.eu. `10.5270/S5P-3lcdqiv`,
registered 2021, resolves to the KNMI/SRON mission page at tropomi.eu. Neither
is wrong; they are the same product registered by two parts of the same
programme.

The granules settle it. Every one declares `identifier_product_doi =
'10.5270/S5P-3lcdqiv'` with `identifier_product_doi_authority = 'http://dx.doi.org/'`,
so that is what the files we actually read say they are, and it is what the
manifest now carries. `data/manifest.json` records both and the reason for the
choice in its `doi_note` field.
