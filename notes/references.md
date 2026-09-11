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

`notes/references.bib` carries sixty-three entries as BibTeX. It is
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

Nothing in the register failed to verify **as a work**. All sixty-three DOIs
resolved: fifty-five through Crossref and eight through DataCite, which is the
registry that carries dataset DOIs and the reason a Crossref-only lookup returns
"not found" for the deposits. Two entries have no DOI to resolve and are
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

The groups are: datasets used, methods applied, findings relied on, findings
contested, the rice-paddy exchange, the Yangtze River Delta grounding, and
accuracy assessment. The last three are kept together for the same reason: each
is a single argument, and splitting its parts across the role groups would
misrepresent all of them. The grounding group is the largest in the register and
is the material a paper's introduction and discussion would draw on.

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

## Findings relied on

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

## Findings relied on

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
