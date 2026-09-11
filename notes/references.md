# Reference register

Every source this repository cites, verified against the DOI registries on
3 September 2026, extended on 9 September 2026 when the figure set gained its
first diagrams, and again on 10 September 2026 when nineteen literature
searches over the study region were recorded. The register exists because
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

`notes/references.bib` carries one hundred entries as BibTeX. It is
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

Two entries in this register are **not** in the BibTeX and cannot be. ISO
5807:1985 is a standard and Chaudhuri (2020) is a textbook; neither has a DOI,
so no content negotiation produces them, and typing them by hand would break
the only guarantee that file makes. Both are under *The diagram sources* below.

This register does **not** include the 2023 thesis's own reference list, which
is in `writeup/Duyst_Thesis.pdf` and belongs to that document. Where the errata
discusses a work the thesis cites, the work appears here and its role says so.

## What could not be verified

Nothing in the register failed to verify **as a work**. All one hundred cited
DOIs resolved: eighty-eight through Crossref and twelve through DataCite, which
is the registry that carries dataset and preprint DOIs and the reason a
Crossref-only lookup returns "not found" for them.

**Three further DOIs appear in this register and are not citations.** They are
named to warn against them, and `scripts/build_references_bib.py` holds them in
a `NOT_CITATIONS` set with the reason for each, so they cannot acquire a BibTeX
entry by accident. Two resolve confidently to the wrong paper and one does not
resolve at all; all three were carried into the methods pass as real citations.
**A resolving DOI is not a verified citation**, and this is the register's
newest failure mode. Two entries have no DOI to resolve and are
verified by other means, which the entries themselves state.

**Two sources did not survive verification for the thing they were cited for.**
The second is Zhu and Li (2024) and is set out under the region grounding below;
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
and the methods grounding. The last four are kept together for the same reason:
each is a single argument, and splitting its parts across the role groups would
misrepresent all of them.

The two grounding groups are the largest in the register and they pull in
opposite directions. The region grounding is nineteen findings and datasets
against three methods. The methods grounding is almost entirely method
literature, most of it borrowed from outside the earth sciences. Together they
are what a paper's introduction, methods and discussion would draw on, and
neither share is a drift from the other.

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
uncited in its text. `notes/decisions.md` records the gate that established why
the conversion is not feasible on this composite.

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

**Yang, B., Li, X., Lin, S., Jiang, C., Xue, L., Wang, J., Liu, X., and
Espenberg, M. (2021).** Invasive Spartina alterniflora changes the Yangtze
Estuary salt marsh from CH4 sink to source. *Estuarine, Coastal and Shelf
Science* 252, 107258.
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

**Zhu, Y., and Li, H. (2024).** Methane emissions from rice paddies in the
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
Rossi, V., Dauzat, J., Bedeau, C., Bénédet, F., Betrancourt, F., and 21 others
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

**Glissenaar, I. A., Boersma, K. F., Rijsdijk, P., van Geffen, J.,
Eskes, H., and 4 others (2025).** TROPOMI Level 3 tropospheric NO2 dataset with
advanced uncertainty analysis from the ESA CCI+ ECV precursor project. *Earth
System Science Data* 17, 4627–4653.
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
7 others (2023).** Automated detection and monitoring of methane super-emitters
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
Shen, L., Qu, Z., Sulprizio, M. P., and 9 others (2024).** High-resolution US
methane emissions inferred from an inversion of 2019 TROPOMI satellite data:
contributions from individual states, urban areas, and landfills. *Atmospheric
Chemistry and Physics* 24, 5069–5091.
`10.5194/acp-24-5069-2024` — peer-reviewed paper; a method not applied. The only
source found that gives albedo filters *with their measured effect*: a blended
albedo ceiling of 0.75 outside summer and a SWIR albedo floor of 0.05 preserve
69 percent of high-quality retrievals and reduce seasonal regional biases by 7
to 21 percent. This project has 166 cells below that floor and below zero.
Cited in `notes/grounding-methods.md`.

**Sicsik-Paré, A., Fortems-Cheiney, A., Broquet, G., and others (2026).**
Assessment of the differences in European CH4 emission estimates from three
TROPOMI products. *Atmospheric Chemistry and Physics* 26, 10423–10450.
`10.5194/acp-26-10423-2026` — peer-reviewed paper; a finding relied on, and the
source of a hard constraint. "A destriping procedure (Borsdorff et al., 2024) is
applied to new XCH4 data from 2024/09/07 (v2.07), but older orbits have not been
reprocessed." This project's 2018 granules are processor version 020400, so the
official destriping cannot be inherited and only a self-implemented one is
available.
Cited in `notes/grounding-methods.md`.

### Model class and resolution

**Bourached, A., Bonkhoff, A. K., Schirmer, M. D., Regenhardt, R. W.,
Bretzner, M., and 9 others (2023).** Scaling behaviours of deep learning and
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

**Passafaro, T. L., Fragomeni, B. O., Lourenco, D. A. L., Rekaya, R., and
Aguilar, I. and others (2020).** Would large dataset sample size unveil the
potential of deep neural networks for improved genome-enabled prediction of
complex traits? The case for body weight in broilers. *BMC Genomics* 21, article
905.
`10.1186/s12864-020-07181-x` — peer-reviewed paper; a finding relied on, and a
mixed one. A deep network had superior prediction correlation only up to 3
percent of a 63,526-observation training set, and poorer correlation after that,
while having the lowest mean squared error of prediction and lower bias at every
size. Recorded as mixed rather than as supporting one conclusion.
Cited in `notes/grounding-methods.md`.

**Kim, K., Lee, J., and others (2025).** MultiTab: A Comprehensive Benchmark
Suite for Multi-Dimensional Evaluation in Tabular Domains. arXiv.
`10.48550/arXiv.2505.14312` — preprint; **a finding that contests the convenient
conclusion** about model class. In small-sample regimes most algorithms perform
similarly within overlapping confidence intervals and high-capacity networks
remain competitive, which "challenge[s] the common belief that neural networks
require large datasets to be effective". It is cited because a methods section
that quoted only the crossover evidence would be selective.
Cited in `notes/grounding-methods.md`.

**Sheng, J.-X., Jacob, D. J., Turner, A. J., Maasakkers, J. D., Sulprizio, M. P.,
Bloom, A. A., Andrews, A. E., and Wunch, D. (2018).** Comparative analysis of
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
Nesser, H., Sulprizio, M. P., Maasakkers, J. D., and 5 others (2021).** Global
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

**Earth System Science Data 18, 4279–4301 (2026).** Reconstructing two-decade
daily high-resolution seamless global land XCO2 records using a hybrid
Transformer–BiLSTM model.
`10.5194/essd-18-4279-2026` — peer-reviewed paper; a method not applied.
Predictors include precursor gases, meteorological reanalysis, surface features
and spatiotemporal encodings.

**Atmospheric Research 308, 107542 (2024).** Estimating high spatio-temporal
resolution XCO2 using spatial features deep fusion model.
`10.1016/j.atmosres.2024.107542` — peer-reviewed paper; a method not applied.

**Atmospheric Pollution Research 17, 102918 (2026).** Gap-filled spatiotemporal
reconstruction of XCH4 data and analysis of methane emission patterns.
`10.1016/j.apr.2026.102918` — peer-reviewed paper; a method not applied. The
closest published analogue to anything this project might do with its 97 absent
cells.

**Scientific Reports 15 (2025).** Improved estimation of carbon dioxide and
methane using machine learning with satellite observations over the Arabian
Peninsula.
`10.1038/s41598-024-84593-9` — peer-reviewed paper; a finding relied on.
Gradient boosting with CarbonTracker, MODIS Terra and ERA-5 inputs reached R²
0.98 and RMSE 0.58 ppm for XCO2 but only R² 0.63 and RMSE 13.26 ppb for XCH4,
described there as moderate accuracy. **Methane is the hard one even with the
right predictors**, and that RMSE is comparable to this project's entire
between-cell spread.

All four cited in `notes/grounding-methods.md`.

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
