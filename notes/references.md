# Reference register

Every source this repository cites, verified against the DOI registries on
3 September 2026. The register exists because citations here were scattered
across `config/sources.yml`, `data/manifest.json`, `notes/decisions.md`,
`ERRATA.md` and three READMEs, in four different formats, so nobody could say
how many sources the work rested on without grepping for them.

Each entry carries the citation as the registry gives it, not as the depositing
platform gives it. That distinction is not pedantry: it has already produced two
errors, both recorded in `notes/decisions.md`. GloRice was cited as "Zhang et
al. (2025)" for a paper whose first author is Xie, read off a figshare record
listing two of six authors in reverse order. And a benchmark was attributed to
the TROPOMI/WFMD v2.0 paper, whose abstract describes quality filtering rather
than the albedo correction the benchmark was said to come from.

`notes/references.bib` carries the same thirty-seven entries as BibTeX. It is
**generated**, not typed: each entry comes from `https://doi.org` under content
negotiation for `application/x-bibtex`, so the two files cannot drift and no
transcription step exists between the registry and the repository. Regenerate it
rather than editing it.

This register does **not** include the 2023 thesis's own reference list, which
is in `writeup/Duyst_Thesis.pdf` and belongs to that document. Where the errata
discusses a work the thesis cites, the work appears here and its role says so.

## What could not be verified

Nothing in the register failed to verify. All thirty-seven DOIs resolved: twenty-nine
through Crossref and six through DataCite, which is the registry that carries
dataset DOIs and the reason a Crossref-only lookup returns "not found" for the
deposits.

Three things named in the repository are still not in the register. Natural
Earth's admin-1 boundaries, cited in `data/manifest.json` as a public-domain
download from naturalearthdata.com, has no DOI. The Copernicus author
guidelines, which recommend Scientific colour maps and are the route by which
that recommendation reaches this field, are a web page rather than a citable
work; they are recorded beside the Crameri entry instead. And `ERRATA.md` 5.3's
claim that waste treatment is the dominant anthropogenic methane source at city
scale in China could not be sourced: repeated searches returned landfill and
wastewater studies for other regions but nothing supporting the claim as the
errata states it, for Chinese cities. What that section can support is narrower
and is set out under Zhao et al. below.

## Ordering

Grouped by role rather than alphabetically. Alphabetical order is conventional
and would be the right choice for a bibliography, but this is a register of what
the work rests on, and the question a reader arrives with is what kind of weight
each source bears. Within each group, alphabetical by first author.

The groups are: datasets used, methods applied, findings relied on, findings
contested, and the rice-paddy exchange, which is kept together because its three
parts are a single argument and splitting them across the other groups would
misrepresent all three.

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
attribution has to answer to. It is what section 5.3 can actually be supported
by, in place of the unsourced waste-dominance claim.

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
