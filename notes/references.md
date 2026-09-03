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

`notes/references.bib` carries the same fourteen entries as BibTeX. It is
**generated**, not typed: each entry comes from `https://doi.org` under content
negotiation for `application/x-bibtex`, so the two files cannot drift and no
transcription step exists between the registry and the repository. Regenerate it
rather than editing it.

This register does **not** include the 2023 thesis's own reference list, which
is in `writeup/Duyst_Thesis.pdf` and belongs to that document. Where the errata
discusses a work the thesis cites, the work appears here and its role says so.

## What could not be verified

Nothing failed to verify. All fourteen DOIs resolved: eight through Crossref and
six through DataCite, which is the registry that carries dataset DOIs and the
reason a Crossref-only lookup returns "not found" for five of them.

Two sources named in the repository carry no DOI and are therefore not in the
register. Natural Earth's admin-1 boundaries, cited in `data/manifest.json` as a
public-domain download from naturalearthdata.com, has no DOI to verify. And
`ERRATA.md` 5.2 and 5.3 refer to a published Matters Arising and to
waste-sector literature without naming either, so there is nothing to look up;
that is a gap in the errata rather than an unverifiable citation.

## Ordering

Grouped by role rather than alphabetically. Alphabetical order is conventional
and would be the right choice for a bibliography, but this is a register of what
the work rests on, and the question a reader arrives with is what kind of weight
each source bears. Within each group, alphabetical by first author.

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
this study area: GISA finds 19.9 percent *less* impervious surface here, in
every province. See `data/processed/README.md`.
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
Cited in `config/sources.yml`.

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
