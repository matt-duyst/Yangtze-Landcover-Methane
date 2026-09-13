# Dataset leads

Working material, not paper content. A checklist of every candidate dataset the
region searches turned up, so that the layer-by-layer passes that follow have
something to verify against rather than starting from a conversation. The
citations behind these entries are in [`notes/references.md`](references.md);
what is here is the route, the licence and the status.

**This file is expected to change.** Each layer pass verifies its own
candidates, so a status moves as work proceeds and the file is updated rather
than rewritten.

**On 13 September 2026 it became a verification task in its own right**, and
every entry below whose status was *unverified* or *documented only* was
attempted from this machine. What that pass found is recorded in
[`notes/decisions.md`](decisions.md); the short version is that the routes were
mostly better than recorded and the licences mostly more permissive, that five
deposits exist for entries recorded as having none, and that the two errors
found were both in this file's own figures rather than in the products.

**Dates in this file were forward-written.** The sections headed *added 13
September 2026* and *added 14 September 2026* were both committed on 11
September 2026 in `668ef80`, before the dates they carry. They are left as
written rather than silently re-dated, and no entry's content depends on them.

## The three statuses, and why they are strict

**Verified accessible** means a request was made and succeeded, from this
machine, without credentials unless the entry says otherwise. Nothing weaker
qualifies: a landing page that loads is not a file that downloads, and this
repository has already met a product whose documented download route was a dead
URL.

**Documented only** means a source describes the route and nothing was fetched.
Most entries here are this, and that is the honest state of an inventory built
from reading.

**Unverified** means the route itself is unknown or unconfirmed — the data are
described in a paper with no data availability statement, or with one naming a
host that was not tried.

## A fourth status, added 14 September 2026

The three above conflate two different kinds of open. **Most of the entries below
are open in the sense that anyone may register and download, not in the sense
that this repository's fetchers reach them without credentials**, and that
difference decides whether a dataset can enter the pipeline or only a person's
working directory.

**Open, anonymous** is the strong form: a request from this machine, with no
account and no key, returns the bytes. The blended TROPOMI+GOSAT product,
CCD-Rice through Science Data Bank, the CCD-Rice validation polygons, GISA-new
through the Zenodo API, APRA500 through the Zenodo API, and Landsat Collection 2
through the Planetary Computer are all in this class, and every one of them is
reachable by a `src/fetch/` module that exists or could be written in an
afternoon.

**Open, registered** is the weaker form and it is where most of the new entries
sit. ORNL DAAC requires a NASA Earthdata login. IMI's compute requires an AWS
account even though its input buckets are public. KIT's RADAR repository serves
files but its terms were not read. None of these is closed, and none of them is
fetchable by a script in this repository as it stands.

**The distinction matters for the dataset stage rather than for the reading.**
A status of "verified accessible" has meant, throughout this file, that a request
succeeded without credentials. That standard is kept. What is added is that
entries which would pass it *given an account* now say so, instead of sitting
unmarked among the genuinely unreachable. Where an entry below reads **open,
registered**, the obstacle is an account and not a permission.

**A third obstacle turned up on 13 September that is neither**, and it needs
naming because it is invisible from a status code. The MUSICA landing page
returns 200 and its licence is CC BY 4.0, but its download is a JavaScript
control carrying `data-terms-accepted` and the backend it calls returns 401
without a browser session. Nothing is closed and no account is needed; a person
must click. Entries in that position are marked **open, terms-gated**, because
a script cannot reach them and a reader of "open, registered" would go looking
for a login that does not exist.

### What verification required, as of 13 September 2026

A status of **verified accessible** now requires all of: a request that
succeeded from this machine; the route and its credential requirement recorded;
the licence read from the deposit rather than inferred from a badge or taken
from the article; the temporal coverage confirmed against the files themselves
rather than the landing page; and the encoding inspected far enough to know
what a fetcher would have to handle. **A resolving DOI is not verification** —
the register audit found five DOIs resolving to the wrong paper and one to
nothing, so every DOI below was checked for what it actually returns.

**The licence distinction that caught two entries: an article's licence is not
its data's licence.** The Underground WWTP paper and CMAB are both
CC-BY-NC-ND 4.0 as articles, and both deposit their data on figshare under
CC BY 4.0. Reading the article licence and recording it as the dataset's would
have imposed a non-commercial no-derivatives constraint that does not exist.

## Methane observations

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| Blended TROPOMI+GOSAT | Machine-learning-corrected XCH4, the product the composite's third field comes from | CaltechData record `etz11-jpg19` redirecting to `sdsc.osn.xsede.org`, HTTP-range readable through `src/methane/blended.py` | CC-BY-4.0 | 2018–2023 | Already used; the blended band of `methane_composite_2018.tif` | **verified accessible** |
| Hefei TCCON GGG2020.R1 | Ground-based FTS column-averaged XCH4, the reference network TROPOMI validation uses | CaltechData, anonymous, three files totalling 57.49 MB, one netCDF4 for the whole record | TCCON Data Use Policy — **contact the site PIs 4 to 6 weeks before submission, 1 to 2 weeks before a presentation; redistribution reserved** | 2015-11-02 to 2025-12-30; 2018 present but sparse, 2,767 retrievals on 44 days | The only in-domain measurement more accurate than the map. Nine days in 2018 have both a TROPOMI overpass of its cell and TCCON data | **verified accessible** |
| Xianghe TCCON | The other Chinese TCCON site | — | — | from 2018-06-14 | **Ruled out.** 39.75 N is 4.55 degrees, about 505 km, north of the lattice | considered and excluded |
| Lin'an WMO/GAW | In-situ surface CH4 at a regional background station in Zhejiang, inside the domain | **WDCGG tried 13 September 2026 and not resolved.** `gaw.kishou.go.jp` is reachable (200) and its station search page loads, but the listing is JavaScript-driven and three plausible API paths return 404, so no Lin'an record was reached and no file was downloaded. The route is neither confirmed nor refuted; what is established is that a scripted fetch needs the site's real API, which was not found from outside | unknown | long-running; 1,942 ppb annual mean in 2011 against Waliguan's 1,861 | A background reference the column field is embedded in, and a surface seasonal cycle | unverified |
| Suzhou three-station network | Surface CH4 at Wujiang, Xiangcheng and Zhangjiagang, all in Jiangsu | no deposit named, and **attempted 13 September 2026**: `10.1016/j.apr.2023.101830` resolves to the right paper and Crossref records **no Creative Commons licence**, so it is not open access and the data statement cannot be read | **not open**; no CC licence registered | 2020–2021 | The in-domain surface seasonal cycle, peaking mid-July and late August, which the composite's October sounding peak must be read against | unverified |
| **MUSICA IASI/TROPOMI fused CH4** | A merged TROPOMI–IASI product carrying three variables where this project has one: a total column, a tropospheric partial column for the lowermost 50 percent of the atmosphere, and an upper-troposphere/stratosphere column, combined by Kalman filter from about 444 million TROPOMI observations | KIT RADAR, `10.35097/wq583rnzpmd83m5g` v4.1. **Landing page 200 and the DOI resolves correctly.** Download is a JavaScript control with `data-terms-accepted`; the backend returns 401 without a browser session, so no `src/fetch/` module can reach it. **The deposit is a 181.7 MB archive holding two example netCDF days (20180101, 20180701) and a `ReadMe.pdf` describing how to get the complete 1,241-file set** — it is not the dataset | **CC BY 4.0**, read verbatim from the RADAR rights statement | January 2018 to June 2021, confirmed on the record; **covers the analysis year in full** | **The only lead in any pass that could raise an association rather than explain it.** A tropospheric column removes stratospheric variance no land-cover predictor could explain. Caveats: a beta-version TROPOMI input rather than 020400, sparser coverage than TROPOMI alone, and information content weakly above one degree of freedom. **Verified 13 September 2026**: licence is CC BY 4.0, not "not established", so the constraint that was feared is absent; what blocks it is a terms click and the fact that the deposit ships samples rather than the series | open, terms-gated |

A premise correction belongs here rather than in a status. It was assumed that
Lin'an might not be in WDCGG because the China Meteorological Administration's
greenhouse gas bulletin names only Waliguan and Shangdianzi. **The bulletin
names Lin'an**, and Lin'an is one of three WMO/GAW regional stations China
operates, with Shangdianzi in Beijing and Longfengshan in Heilongjiang. The
station's existence and its figures are not the uncertainty; the data route is.

## Methane inventories

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| MMCP | Monthly methane emissions for 31 mainland provinces across eight sectors — coal mining, oil and gas systems, energy combustion, rice cultivation, livestock, solid waste, wastewater and wetlands — with rice split into single-season and double-season, the latter further into early and late | figshare `10.6084/m9.figshare.26806522.v1`, **one file, `MMCP-v1.xlsx`, 1,067,632 B, MD5 `e1233e5ae1abaf1ece4537cd0e2ce8d2`, fetched anonymously on the route `src/fetch/figshare.py` already handles** | **CC BY 4.0.** *This entry said CC-BY-NC-ND 4.0 and "constrains reuse more than anything else in this inventory". That was wrong in the worst direction: the deposit is the least restrictive licence here, not the most, and the reasoning built on its restrictiveness does not stand* | January 2013 to December 2022, **confirmed from the file**: 33,360 rows, 120 distinct months, 31 provinces, 2018 present | The sectoral comparison this study has never had. **Read from the file, 2018 four-province totals are Anhui 2,103.0, Jiangsu 1,979.6, Zhejiang 884.1 and Shanghai 416.2 Gg CH4, a domain total of 5.38 Tg, of which rice cultivation is 1.66 Tg (30.8 percent).** That total sits at the bottom edge of the 5-to-12 Tg literature band this project uses as the capability figure's input band. **The rice split this entry described is not in the deposit**: there is one `Rice cultivation` sector, with no single/double-season and no early/late breakdown | **verified accessible**, open anonymous |
| City-scale source-resolved inventory | Methane for 339 prefecture-level cities, resolved by source | Supporting Information PDF attached to the article; no separate data deposit found | article licence | 2018 to 2024 | The urban composition `ERRATA.md` 5.3 rests on, including the 38 cities where waste dominates | documented only |
| EDGAR | The global gridded anthropogenic inventory | already known | — | — | Known biased **in both directions here**: Huang et al. (2021) found it underestimating agricultural soils especially in growing seasons, and its v432 and v5.0 posteriors differ by eight points of regional share | known |
| Wastewater facility factors | Facility-level CH4 emission factors from atmospheric measurements at 105 treatment plants, including thirteen in Nanjing measured across three seasons | no deposit named | unknown | measurements to 2023 | The sector `ERRATA.md` 5.3 records the thesis as omitting entirely | unverified |
| **WetCHARTs v1.3.1** | The wetland methane emission ensemble IMI uses as its default prior, monthly at 0.5 degrees | ORNL DAAC, `10.3334/ORNLDAAC/1915`; **a NASA Earthdata login is required**, so not fetchable anonymously. **Verified 13 September 2026**: the landing page returns 200 and a direct data-file request returns **401**, so the credential requirement is confirmed rather than assumed | open data, registered access | 2001 to 2019 | **The prior that overlaps the rice prior in these cells.** Its own documenting paper states that Chinese rice extents are only implicitly excluded, that inundation retrievals cannot separate co-located agriculture from natural wetland, and that the distinction "has yet to be consistently addressed". It also carries a documented seasonal-phase defect, using air temperature rather than soil temperature | open, registered |
| IMI input buckets | The three public AWS buckets IMI reads: TROPOMI methane at `registry.opendata.aws/sentinel5p/`, the blended TROPOMI+GOSAT product at `registry.opendata.aws/blended-tropomi-gosat-methane/`, and GEOS-FP emissions, boundary conditions and meteorology at `registry.opendata.aws/geoschem-input-data/` | AWS Open Data Registry; the buckets are public and **the compute is not** — running IMI needs an AWS account. **Verified 13 September 2026, and two of the three bucket names here are registry slugs rather than buckets.** `blended-tropomi-gosat-methane` lists anonymously (200). The TROPOMI methane bucket is **`meeo-s5p`**, which is what `src/fetch/s5p.py` already uses; `sentinel5p` as a bucket returns 404. `geoschem-input-data` returns 404 as a bucket; the reachable IMI archive is **`imi-boundary-conditions`**, which lists anonymously | open data | **The boundary archive does begin 1 April 2018**, verified against the bucket: its earliest key is `restarts/GEOSChem.Restart.20180401_0000z.nc4` | **The boundary-condition archive is the part this project could not build for itself**, and it begins comfortably before this project's first granule. *This entry said "one day before"; the project's first granule is 2018-04-30, so the archive precedes it by 29 days, not one. The error is in the favourable direction — a month of spin-up rather than a day.* The second bucket holds the field already committed as the composite's third band | **buckets verified accessible and anonymous**; the compute is open, registered |

## Rice

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| CCD-Rice | Paddy rice distribution for China at 30 m, 27 annual GeoTIFFs totalling 5.37 GB | Science Data Bank `13e7fbb10ef343659ae4c91089584f12` through the Croissant route `src/fetch/scidb.py` already handles, with **MD5 on every file**. **Re-verified 13 September 2026**: the Croissant export returns 27 file records totalling **5,368,504,737 B**, MD5 on all 27, none with SHA-256, and the paper's own DOI `10.57760/sciencedb.15865` resolves to exactly this dataset id, so the hash recorded here and the DOI in the literature are one record | ODC-BY 1.0, read from the Croissant `license` field as `https://opendatacommons.org/licenses/by/1-0/` | 1990 to 2016, confirmed from the 27 filenames — **reaches 2000 and 2010, does not reach 2018** | The second rice product for the historical years, the role GISA plays for impervious surface | **verified accessible** |
| **CCD-Rice validation polygons** | Sample polygons visually interpreted from very-high-resolution Google Earth imagery, in GeoParquet, with `covertype`, `region` and `year` fields and six classes: non-cropland, single-season rice certain, double-season rice certain, rice of uncertain season, other crops, non-rice | figshare `10.6084/m9.figshare.25515019.v3`, a single 1,908,665 B file on the route `src/fetch/figshare.py` already handles; MD5 `927e517583c1999650b90a087db19ffb` **downloaded and verified** | **CC BY 4.0**, from the figshare record's own licence object | 3,619 polygons nationally over 2002 to 2016; **777 in the four provinces** — Shanghai 338, Jiangsu 167, Zhejiang 159, Anhui 113 — in the years 2003, 2004, 2011, 2013 and 2014. **Every figure in this cell was confirmed against the file on 13 September 2026 and every one was right** | **The best reference-data lead found anywhere in this work**: independent, published, openly licensed, in-domain, and more accurate than any map here. **What opening it added**, all of it in `data/processed/ccdrice_polygons_yrd_2026.csv`: the 777 reach only **62 of the 926 analysis cells**, Shanghai's 338 falling in six; **50 Jiangsu polygons sit north of 33.3462 N** where the committed NESDC raster stops, leaving 727 usable against it; the sample is **purposive, not probabilistic**, the paper selecting "only 2 to 4 years in each provincial administrative region" because Google Earth's historical Chinese coverage is sparse and "early images tend to be for urban areas rather than for rural areas", so there are no inclusion probabilities for a design-based estimator; **the deposit holds 3,619 where the paper reports 3,449**, the 170 difference being exactly the `covertype 3` season-uncertain class the paper's breakdown omits (1,825 + 838 + 786 = 3,449); and two encoding traps — every `region` value carries a **trailing space**, and **296 of the 777 are MultiPolygon** against a description that says polygons | **verified accessible**, open anonymous |
| CCD-Rice code | The product's own processing code | Zenodo `10.5281/zenodo.15468566`. **Unreachable: zenodo.org refuses this network at the application layer — see *The Zenodo block* below, which corrects the TCP diagnosis first recorded here.** DataCite carries the metadata and confirms the record is `shenrq/CCD-Rice: First release` | MIT, from the register; **not re-read, because the deposit could not be opened** | — | Reading how the thresholds were set. **This is now answered from the paper instead and the deposit is no longer needed for it**: §2.3.3 re-determines the rice-probability threshold from *filtered agricultural statistical areas*, not from the validation polygons, and §2.3.4 uses the polygons only to validate. So the polygons are clean of CCD-Rice's own calibration | documented only, route blocked |
| ChinaRiceCalendar | Transplanting, heading and maturity dates for early-, middle- and late-season rice | Harvard Dataverse `10.7910/DVN/EUP8EY`, **API 200 anonymously, version 9.0 released 2026-06-11, 91 files totalling 3,542,722,284 B, MD5 on every file, one file downloaded and opened** | **CC0 1.0** — public domain, the most permissive licence in this inventory. *This entry said "Dataverse terms, not checked"* | 2003 to 2022, confirmed from filenames: **five period means** (2003–2007, 2008–2012, 2013–2017, 2018–2022 and 2003–2022) across nine variables (early/middle/late rice × transplanting/heading/maturity), in two griddings — `rice_pixels` and `county_level`. **There are no annual rasters**; per-year data is only in `County-level Annual ChinaRiceCalendar.zip` | The calendar the growing-season argument rests on. **The resolutions in this entry were wrong**: a `rice_pixels` raster opened as 0.01° ≈ 1,113 m, EPSG:4326, float32, bounds 97.6–134.9 E and 18.3–53.1 N, so it covers all four provinces. There is no 250 m and no 10 km variant in the deposit; the `county_level` files are 70× larger and presumably finer, and 10 km appears nowhere | **verified accessible**, open anonymous |
| Irrigation regime maps | Water-saving against flooding irrigation across Chinese paddy lands at 500 m, from province-wise random forests over 123 MODIS and Sentinel-1 features | no deposit named in Wang et al. (2024), `10.1016/j.agwat.2024.109083`, and **attempted 13 September 2026**: the DOI resolves to the right paper and the article is open under CC-BY-NC 4.0, but Elsevier served a 892-byte interstitial rather than the text, so the data availability statement is still unread. Crossref registers no dataset relation | **CC-BY-NC 4.0**, from Crossref; *this entry said "unknown"* | **annual, and the start year is unestablished**; the end is 2022, so whether it reaches 2018 is not in doubt but whether it reaches 2000 or 2010 is | **The missing water-regime covariate**, which is the mechanism the grounding identifies as having a larger dynamic range than extent. Overall accuracy near 0.73, and an R² above 0.92 against city and provincial census area — the census assimilation is why it needs care rather than adoption | unverified |
| CH4MOD | The semi-empirical paddy methane model, as used by the cropping-system study | model, not data | — | — | The route from a rice layer plus a water regime to an emission estimate, which this reproduction has not taken | known, not applied |
| NESDC single-season rice | The rice layer the analysis grid carries | committed | — | 2017–2022 | in use | in use |
| GloRice | The second rice layer, at 5 arcmin | committed | — | 1961–2021 | in use | in use |
| **APRA500** | Annual paddy rice planting area and cropping intensity for the Asian monsoon region at 500 m, from MODIS and a phenology-based method | Zenodo `10.5281/zenodo.5555721`, twenty-eight files of about 1.7 MB each — one GeoTIFF archive per year plus three-year composites. The API returned the file listing and a `paddyRice2018.zip` request returned HTTP 200 when this was written. **The route recorded here no longer works: zenodo.org refuses this network at the application layer — see *The Zenodo block* below.** DataCite still serves the metadata and confirms the record | **CC-BY-4.0** | 2000 to 2020 — **the only satellite-classified rice product that covers all three thesis years**. GloRice covers them and is committed, but this file's own note records it as statistics allocated to grid cells rather than an observation | The historical-years gap, filled by one product and one method instead of NESDC plus CCD-Rice. At 500 m it is the coarsest candidate, and the rice-mapping review's finding that products lose consistency in fragmented fields bites hardest here | **verified accessible** |
| **EFSP** | Single and double paddy rice and cropping intensity for China at 30 m, from more than 684,000 Landsat scenes on Earth Engine | no deposit named in Wei et al. (2022), `10.3390/rs14030759`, and **attempted 13 September 2026**: MDPI returned 403 to this network, so the article text was not read. MDPI publishes everything CC BY 4.0, so the article is open and the obstacle is the block, not the licence | **CC BY 4.0** by MDPI's uniform policy, not read from the article | 2014 to 2019; **reaches 2018** | A 30 m in-domain alternative to the committed NESDC layer for the analysis year, with a published accuracy: producer 0.92–0.96 against user 0.76–0.87, kappa 0.67–0.80, R² above 0.88 against statistics. **Producer exceeding user by that margin is over-detection**, which inflates a per-cell fraction rather than thinning it, so it would need the GAIA–GISA treatment rather than substitution | unverified |
| Zhu et al. PPPM maps | Annual single- and double-cropping rice for southern China at 30 m by the algorithm the 2023 thesis used, from Landsat 5, 7 and 8 | **not established.** The article is paywalled, OpenAlex records no open version, and the DOAJ record's only full-text link is the publisher DOI, so no data availability statement was readable | unknown | 1999 to 2019; covers 2000, 2010 and 2018 | **The gating lead for the whole PPPM route.** If obtainable it supplies a single-method layer for all three thesis years and removes the coverage argument for a reimplementation. Its "southern China" explicitly includes Anhui and Jiangsu | unverified |
| 500 m irrigated cropland maps | Irrigated cropland for China at 500 m, from MODIS plus statistics and existing irrigation products | **Deposit found 13 September 2026 in the paper's own Data Records section, which this inventory had not read: figshare `10.6084/m9.figshare.19352501.v1`, 21 files totalling 86,930,189 B, MD5 on all, anonymous.** The files are `2000.tif` through `2019.tif` | **CC BY 4.0** (deposit and article both) | **2000 to 2019, confirmed from the 20 filenames — it reaches 2000, 2010 and 2018, all three thesis years.** Binary maps, 1 irrigated and 0 not, EPSG:4326 | A second irrigation layer beside the water-saving-against-flooding maps above, at the same resolution. **It assimilates statistics**, which is the same reason its neighbour needs care rather than adoption, and the two together would be the pair the GAIA–GISA lesson calls for. **This is now the reachable half of that pair**, and at 87 MB for all twenty years it is the cheapest covariate lead in this file | **verified accessible**, open anonymous |
| NESEA-Rice10 | Annual paddy rice at 10 m for Northeast and Southeast Asia | Zenodo `10.5281/zenodo.5645344`, not tried | — | 2017 to 2019 | **Ruled out on extent.** Its "Northeast Asia" is Liaoning, Jilin and Heilongjiang with Korea and Japan; its "Southeast Asia" is six countries to the south. The Yangtze River Delta is in neither, despite 10 m and 2018 having made it the most attractive product on the list | considered and excluded |
| 30 m Northeastern China rice | Annual paddy rice at 30 m, 2000 to 2023 | figshare `10.6084/m9.figshare.28407710` | CC-BY-4.0 | 2000 to 2023 | **Ruled out on extent**: Northeastern China. Recorded so the reason is on file, because the resolution and the twenty-four-year span would otherwise make it the best candidate here | considered and excluded |
| 30 m South and Southeast Asia rice | Paddy rice distribution and cropping intensity at 30 m, 1995 to 2024 | not established, from Zhao et al. (2026), `10.5194/essd-18-5583-2026` | unknown | 1995 to 2024 | **Ruled out on extent.** Kept because its first two authors are the authors of the paddy-rice-and-XCH4 Reply, so the group that established the 0.5-degree correlation built the high-resolution map it called for — for another continent | considered and excluded |
| Rice mapping product review | A consistency assessment of twenty-five rice products, three global and twenty-two regional, over China, Heilongjiang and Vietnam | `10.1016/j.srs.2024.100172`, open access | **CC-BY-NC-ND 4.0**, from Crossref. *This entry said CC-BY. It is the one licence correction in this pass that goes the restrictive way, and it matters only for quoting the review at length, not for using its findings* | published 2024 | **The map of this table's own territory.** It finds products losing consistency in fragmented fields, cloud and complex cropping challenging subtropical mapping, no product combining wide coverage with fine resolution and a long series, and ground-truth deficiency impeding validation — the last of which is this repository's own accuracy-assessment conclusion, reached independently | **verified accessible** |
| **China_AP** | The first 10 m annual aquaculture pond dataset for China, from 119,882 Sentinel-1 and 579,436 Sentinel-2 scenes, with individual-pond extraction accuracy above 90 percent | **Still no deposit, and now established rather than assumed.** Sun et al. (2025), `10.1016/j.jag.2025.104958`, is **gold open access under CC BY 4.0**, yet its full text could not be read from this network: ScienceDirect returns 403 to `curl` and to a page fetcher alike, `linkinghub` redirects to a permissions interstitial, and Unpaywall and OpenAlex list only the publisher URL and a DOAJ metadata record with no full text. Crossref registers **no dataset relation**. So the data availability statement remains unread and no repository copy exists to read it from | **CC BY 4.0** for the article, from Crossref. The dataset's own licence is unknown because the dataset was not found | 2016 to 2023 per the abstract; **covers 2018**, unconfirmed against files | **The test of the largest omission in the rice record.** Overlaying it on the committed rice layer would measure the paddy–pond overlap directly, per cell, for the analysis year. Its area totals could not be verified and are not used. **This is the one of the three gating datasets that verification did not move**, and the obstacle is not a licence or an account but a publisher blocking the article that names the route. The next step is not another search: it is one email to the corresponding author, or access to the PDF through an institutional subscription | unverified, and now for a recorded reason |
| Aquaculture pond index mapping | A second national aquaculture pond mapping, from a new aquaculture index with machine learning | *Earth's Future* `10.1029/2024EF005637`; **no deposit found, and the article is also unreadable from here** — Wiley returns 403. Crossref registers no dataset relation | **CC BY 4.0** for the article, from Crossref; *this entry said "article licence"* | published 2025 | **The pair China_AP needs under the GAIA–GISA rule**: two products with different errors beat one better product, and this file has applied that rule to impervious surface and to rice already. Also the clearest source for the paddy-versus-pond classification confound | unverified |

Three of the four products this pass examined for the first time turned out to be
out of domain, which is the most useful thing the pass established for this file.
**A product's resolution and year coverage are the attributes a lead is recorded
on, and its spatial extent is the one that disqualifies it**, so extent should be
checked before either. All three were recorded as leads on the strength of
resolution and years.

## Urban

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| GISA-new | Impervious surface as a first-year-of-imperviousness encoding in 20-degree tiles, 99 files totalling 5.82 GB with a `.vrt` mosaic index | Zenodo `10.5281/zenodo.14848113`. **The route recorded here no longer works: zenodo.org refuses this network at the application layer — see *The Zenodo block* below** — so the "API returns 200" this entry records is no longer true and nothing can be downloaded. Two alternatives were tried and neither serves it: the Wuhan University server that does serve GISA (`irsip.whu.edu.cn/resv2/`) has a browsable index carrying `GISA_tif.zip` and `GISA_tif/` but no GISA-new bundle under any obvious name, and its own resources page lists only GISA1 and GISA2. DataCite serves the metadata | **Unverified, and the claim in this cell is not supported by anything reachable.** DataCite's record for this DOI carries **no rights field at all**, so "CC-BY-4.0, open" cannot be confirmed while Zenodo is down. The GEE community catalog states CC BY 4.0 for the GISA family, which is corroboration and not verification | **The discrepancy is resolved and it was a conflation of two products.** There is no GISA product covering 1972 to 2021. GISA1 and GISA2 cover **1972 to 2019** — Wuhan University's own resources page says so for both — and **GISA-new covers 1985 to 2021**, which the authors' abstract on the deposit states in those words. The 1972 belongs to the older products, whose encoding `data/processed/README.md` already documents as values 1 to 37 over [1972, 1978, 1985, 1986, … 2019]; the 2021 belongs to GISA-new. The deposit is registered `IsVersionOf` the GISA 1.0 record, which is the likely route by which the older naming reached this entry. **GISA-new therefore reaches 2000, 2010 and 2019, but its year lookup table could not be read from the files** | A fourth impervious product covering all three thesis years, which no other candidate does. **Blocked on the Zenodo network block, which is the same block `data/processed/README.md` already records for GISA's per-tile links** | documented only, route blocked |
| GISA 1.0 and 2.0 validation samples | 120,777 sites from 270 cities, 88,822 ZY-3 samples from 45 cities, 118,822 ZY-3 test samples | **not distributed, re-checked 13 September 2026 and still not.** The `irsip.whu.edu.cn/resv2/` index is browsable and was read in full: 30 entries, of which the only GISA data are `GISA_tif.zip` and the `GISA_tif/` tile directory. Its two other data directories, `DATA_res/` and `GBD_data/`, hold shell scripts and two PNGs. No sample file under any name | — | — | Would have been urban reference data; is not available. **A useful by-product of looking**: the 257 GISA tiles are individually downloadable from that directory, which corrects a claim in `data/processed/README.md` | not distributed |
| GAIA validation samples | 3,500 global samples | not distributed | — | — | — | not distributed |
| GHSL | Global Human Settlement Layer built-up surface | — | — | — | **Rejected**: no layer consistent with 2018, so it cannot answer the analysis year | rejected |
| Natural-gas-vehicle supplementary table | Per-vehicle measurements behind the 90-percent-above-limits finding | **Deposit found 13 September 2026 in the paper's data availability statement: DataSpace at Princeton University, `10.34770/t009-7064`, which resolves (200) and is registered with DataCite.** The article itself is open and carries the same data as Supplementary Data 1 | **CC BY 4.0** for the article, from Crossref; the DataSpace record registers no rights statement | 2015–2019 | The urban attribution `ERRATA.md` 5.3 discusses | **route verified**, deposit located and resolving, contents not opened |
| YRD gas leakage estimate | Ethane-tracer inversion of natural gas leakage in this region's cities | paywalled; abstract not indexed | — | 2012 to 2021 | Would quantify the urban source the thesis attributes; **its figures could not be verified and are not used** | unverified |

## Reference data and method

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| Landsat Collection 2 Level-2 | Surface-reflectance scenes at 30 m | Planetary Computer STAC API, `collections/landsat-c2-l2`, **HTTP 200 anonymously with no key, re-verified 13 September 2026** | The collection's `license` field reads `proprietary`, which is the STAC convention for "see the link"; its licence **link** is titled *Public Domain* and points at the USGS data policy. Cite `10.5066/P9IAXOVV`, `10.5066/P9C7I13B` or `10.5066/P9OGBGM6` by sensor | 1982-08-22 onward | Reimplementing the thesis's per-pixel proxy method from imagery rather than from a product, which is the only route to a reproduction that does not inherit a product's errors | **verified accessible** |
| Very-high-resolution imagery for visual interpretation | The standard response design in this literature | — | **An open question, not an assumption.** Every product here interpreted Google Earth imagery; none of the papers read addresses whether its terms permit publishing a derived accuracy assessment | — | Constructing reference data where none is distributed | unresolved |
| Olofsson et al. (2014) | The good-practice standard for area estimation and accuracy assessment | in the register | — | — | The standard a reviewer will check against. **Its first three recommendations apply here and are unmet; its last two do not apply at all**, because it contains no treatment of fractional cover | in the register |
| **Global land cover validation samples** | **44,514 point samples** carrying one of 24 fine land-cover labels, global, from the group behind GLC_FCS30 | Zenodo `10.5281/zenodo.3551995` (version) under concept `10.5281/zenodo.3551994`. **Fetched 13 September 2026 during an open window in the Zenodo filter**: two files, 945,869 B total, `GLC_ValidationSampleSet_v1.rar` at 928,968 B with MD5 `9b83f28f35ead5893cbd796041a73df9` verified, plus a `Data description.docx`. **DOI and citation verified before anything else and both are correct**: *A Dataset of Global Land Cover Validation Samples*, Liangyun Liu, Yuan Gao, Xiao Zhang, Xidong Chen and Shuai Xie, Zenodo 2019, v1 | **CC-BY-4.0, read from the deposit's own `license` field**, with `access: open`. *This row briefly recorded the licence as OpenAIRE-harvested corroboration; it is now read from the record itself* | **44,514 samples in the file against 44,043 in the GLC_FCS30 paper, a difference of 471 that neither source explains.** Nominal year 2015 per the paper; **the file carries no year field**, so per-sample timing is not recoverable. **124 samples fall inside the four provinces** — Jiangsu 112, Zhejiang 7, Anhui 4, Shanghai 1 — reaching **20 of the 926 analysis cells** | **The design is a stratified allocation over a non-probability frame, and the deposit confirms the frame.** The paper gives the Cochran sample-size formula with `W_i` the global per-class area proportion, which is a textbook stratified allocation; the description document lists the frame as **eight donor datasets** — GLCNMO 2008, VIIRS, STEP, FROM_GLC, croplands.org, GLWD and two NDVI/NDSI time series — with points "randomly collected from each polygon". Randomisation inside donor polygons is not a probability sample of this domain and the first-stage inclusion probability of a donor polygon is unknown. **The shapefile has three fields only — `sample_lab`, `lon`, `lat` — so the per-sample source code the description describes is not in the file and provenance is not recoverable.** Points, EPSG:4326, so **class labels and no fractional cover**. For this project's two layers the counts are decisive: 107 irrigated cropland and 1 rainfed against a rice layer, and **12 impervious-surface points across all four provinces** against an impervious layer | **verified accessible**, open anonymous |
| **Globe230k** | 232,819 densely annotated image tiles of 512 × 512 at 1 m in 10 first-level categories, RGB plus NDVI, DEM, VV and VH | Zenodo, concept `10.5281/zenodo.8429199` with **three versions** — `8429200` (the one this task named), `10279734` and `10435661`, the last from 2024-01-04. **The record and its small files were fetched during the open window**: the 716,079 B user guide and the 1,877,447 B training split were taken; the imagery was not, because `image_patch.zip` is **11,503,450,247 B** and the deposit totals **12.23 GB**, four times this task's budget. The multimodal DEM, NDVI and VVVH layers are not on Zenodo at all but on Baidu Wangpan, at 1.91 GB, 164 GB and 372 GB. DOI and citation verified: Qian Shi, Da He, Zhengyu Liu, Xiaoping Liu and Jingqian Xue | **CC-BY-4.0, read from the deposit's own `license` field**, `access: open` | 232,819 tiles, **total coverage over 60,000 km²** — the abstract's own figure, which 232,819 × 0.2621 km² reproduces at 61,032 km². That is **0.041 percent of global land** | **Dense annotation cannot yield a per-cell fraction at this lattice, and the arithmetic settles it.** One tile is 0.2621 km²; one 0.25-degree cell is about 625 km², so a tile is 0.042 percent of a cell and **tiling one cell would need 2,384 tiles**. Uniform on land, the four provinces would receive about **547 tiles, 0.59 per cell, covering 0.025 percent of each cell's area**. Dense annotation gives an exact fraction *within a tile footprint*, which is a sample of the cell and not the cell's value — so it returns to the probability-sampling problem it was meant to solve, at under one tile per cell. **The sampling is not uniform and the user guide says so outright**, which is a different and larger departure than the quality-screening this task described: *"in order to ensure the category balance, we intentionally give more chance to the rare categories to be sampled, such as wetland, ice/snow, etc."* That is a deliberate disproportionate design with **no stated selection probabilities, so inclusion probabilities are not recoverable**. The guide still does not say how many candidate regions were rejected or on what basis. **And the geographic distribution cannot be determined at any sane cost**: the split files name tiles `data_3`, `data_5`, `data_6` and so on, carrying no georeference, so locating tiles would mean downloading 11.5 GB of imagery or the 164-to-372 GB modality layers. The class scheme is 10 values, 1 cropland through 10 ice/snow, with 8 impervious; the split is 7:1:2 | **verified accessible**, open anonymous; the imagery is out of budget |
| **LCMAP CONUS reference data** | 25,000 plots across the conterminous United States, each carrying annual land use, land cover and change-process attributes for every year 1984–2018 | **USGS ScienceBase, `10.5066/P9ZWOXJ7`, fetched anonymously with no credential.** Item `5e42e54be4b0edb47be84535`, four files; the data are `LCMAP_CU_20211117_V01_REF.zip`, 29,903,304 B, which unpacks to a plot shapefile, a 66.6 MB CSV and a 31.2 MB XLSX of the same content, plus FGDC metadata. Version 1.2, November 2021 | **Use constraints, verbatim from the FGDC metadata: "None. Users are advised to read the dataset's metadata thoroughly to understand appropriate use and data limitations."** Access constraints likewise "None." A US federal work | **1984-01-01 to 2018-12-31, read from the FGDC `begdate` and `enddate` rather than the landing page.** 874,836 rows over 25,000 distinct plot ids, which is 35 years per plot less a few gaps | **US-only, so it cannot serve as reference data here**, and it is recorded because it is the published model for how such a product is structured and because `notes/grounding-methods.md` cites its interpreter-agreement results. Encoding: 13 columns — `plotid`, `x`, `y`, `image_year`, dominant and secondary land use with notes, dominant and second land cover, change process with notes, and `LCMAP`; coordinates in the CONUS Albers projected system. **Class labels only, no fractional cover** | **verified accessible**, open anonymous |
| **SinoLC-1** | The first national land-cover map of China at **1.07 m**, from the L2HNet deep-learning framework over free imagery | Zenodo. **`10.5281/zenodo.7707461`, the DOI the ESSD paper's data statement gives, is the *user guide* record and not the data** — its title ends "(User guide V2.4)". The data sit in sibling version records, of which `8103779` is "Update data (June 30, 2023)" and `7708740` is "Northwest of China". Structure, from the paper: city tiles named `G_P_C.tif` for geographical region, province and city — so `East_Jiangsu_Nanjing.tif` — **packaged in provincial `.zip` files**, which means the four provinces are four archives. **Zenodo refused this network throughout this pass** (403 to browser signatures, silent drop to `curl`, 504 once), so no file was opened and no size was read | **Not established.** DataCite carries **no rights field** for the record, and the deposit's own `license` could not be read. The paper is CC BY 4.0; that governs the article | **Reference year about 2021**, verbatim from the paper: "Most of the images were acquired around the year 2021", with earlier frames on the northern frontier and in the northwest, so the year is **uneven across the domain** | **11 classes, and there is no single impervious class**: "Tree cover", "Shrubland", "Grassland", "Cropland", **"Building"**, **"Traffic route"**, "Barren and sparse vegetation", "Snow and ice", "Water", "Wetland", "Moss and lichen". Where every 10 m product it compares itself against has one built-up class, SinoLC-1 splits it, so mapping onto this project's impervious fraction means **summing Building and Traffic route**. Accuracy re-verified verbatim: **overall 73.61 percent, kappa 0.6595**, on 106,344 counted validation points. Volume for the four provinces, estimated from 350,000 km² at 1.07 m and an 11-class raster, is of the order of **10 GB compressed** and 306 GB uncompressed | documented only, route refused |
| **EcoVision** | Submeter land cover over the **urban areas of 42 major Chinese cities**, at about **0.5 m** in 8 classes | *Journal of Remote Sensing* `10.34133/remotesensing.0811`, 2025, Encheng Zhang, Xin Huang, Jiayi Li and Jiawei Zhou. **No route established.** The full text returns 403 to this network from `spj.science.org` to both a page fetcher and `curl`, and the DOAJ record's only full-text link is that same URL, so the data availability statement, the city list and the licence were not read. **It is also absent from its own authors' distribution server**: `irsip.whu.edu.cn/resv2/resources_en_v2.php` — the IRSIP page that does serve GISA — lists "China's first sub-meter building footprints" and a nationwide 0.5 m urban construction-site model for 2020 marked "The data will be released soon", and nothing named EcoVision | **Not established.** Crossref registers no Creative Commons licence for the article | **Not established.** The abstract gives no year | **Overall accuracy 83.6 percent**, on "23,850,000 randomly sampled validation pixels in 42 cities", from the abstract. **Urban areas only**, which is an asymmetry worth naming: it could serve this project's impervious layer in city cells and cannot serve the rice layer at all. **Its comparative claim about SinoLC-1 could not be verified** because the text is unreachable, but the factual half of it is confirmed from SinoLC-1's own paper: SinoLC-1 carries Building and Traffic route and no other impervious class. Whether that omits other impervious types, as EcoVision is said to claim, is unread | documented only, publisher 403 |
| **ISA-1, Yangtze River Economic Belt** | 1 m impervious surface area for the YREB, **super-resolved from 10 m Sentinel-2** by the JointSeg framework | arXiv `2505.05367`, 8 May 2025, Jie Deng, Danfeng Hong, Chenyu Li and Naoto Yokoya; published as `10.1080/15481603.2025.2610548`. **The deposit exists and was downloaded: figshare `10.6084/m9.figshare.28490204.v2`, one file, `ISA-1-Some-examples.rar`, 1,162,772,636 B, MD5 `717ce96f4b35d80c5f43c4cd52dcb50c` verified.** **It is not the product.** The paper's data statement uses the future tense — the product "will be publicly available in the Figshare data repository" — and what is there is seven prefecture-city rasters: Wuhan, Yueyang, Deqen, Jiujiang, Kunming, **Nanjing and Shanghai** | **CC BY 4.0, read from the figshare record's own licence object** | **Reference year 2021.** The paper also claims "biennial ISA maps from 2017 to 2023", but for "representative cities" rather than the whole belt, and none of those years is in the deposit | **Verified from the files, and it is the only candidate whose encoding maps directly onto this project's target.** 1 m exactly (8.983e-06 degrees), EPSG:4326, uint8, one band, **binary: 0 non-ISA, 1 ISA** — so averaging it over a lattice cell *is* an impervious fraction. **Nodata is undeclared**, and 0 means both non-impervious and outside the city, which is the same trap as CISC below. Nanjing is 97,753 × 153,782 px over 118.359–119.237 E and 31.230–32.612 N; Shanghai 116,272 × 130,009 px over 120.858–121.903 E and 30.682–31.850 N. **The two in-domain cities fully contain 20 of the 926 analysis cells and partly overlap 31 more**, so the deposited examples could produce a per-cell fraction for **2.2 percent of the lattice**. Accuracy: **the headline F1 of 85.71 percent is the mean over ISA and non-ISA; the impervious class alone is F1 75.53, precision 99.73 and recall 61.76**, so it misses about 38 percent of impervious area. The paper's own in-domain observations are worth carrying: 10 m ESA WorldCover "demonstrates relatively higher accuracy and provides more refined ISA delineation in developed urban areas such as Nanjing, Suzhou, and Nantong", and SinoLC-1 "tends to overestimate ISA in large developed cities like Suzhou". Its area is given as 2.2 million km² in the abstract and 2.4 million in the body | **examples verified accessible**, open anonymous; the product is not distributed |
| **CISC2020 and CISC2022** | Improved 30 m impervious surface for China for 2020 and 2022, from fusing 2 m imagery with Landsat composites and SRTM | Zenodo `10.5281/zenodo.15004180`, Ranyu Yin, Guojin He, Guizhou Wang, Kaiyuan Zheng, Chengjuan Gong and Tengfei Long, 2025, described by *Scientific Data* `10.1038/s41597-026-06619-3`. **Zenodo refused this network throughout, so the file listing and sizes were not read**; everything below is from the deposit's own description as harvested by DataCite. Files named there: `cisc_2020.tif`, `cisc_2022.tif`, `valid_mask_2020.tif`, `valid_mask_2022.tif` and `source_date_dissovle.zip`, the last a shapefile of the 2 m source acquisition date per location | **Not established.** DataCite carries no rights field; the article is CC-BY-NC-ND 4.0 | **2020 and 2022** | **Cloud Optimised GeoTIFF in an Albers projection**, values 0 bare land or other, 1 impervious, 2 vegetation, 3 water. **The encoding carries a trap the description states plainly: areas outside China, and areas inside it lacking 2 m coverage, "are regarded as invalid pixels and assigned value 0" — the same value as bare land.** The valid masks are therefore mandatory, not optional. The auxiliary classes' "reliability is not guaranteed". Accuracy: "Spatially Averaged F1-score > 0.93 for the impervious surface class", from "independent, expert-interpreted validation points" produced by "entropy-guided stratified sampling". **Those points are the reference data this project actually wants, and the description does not list a file containing them**; whether they are deposited could not be settled while Zenodo refused | documented only, route refused |
| NLCD percent-impervious assessment | Mean deviation, mean absolute deviation and OLS regression against a more accurate reference fraction | in the register | — | — | **The correct frame for this study's layers**, which are per-cell fractions rather than a categorical map, and the measurement of how error falls as the aggregation unit grows | in the register |

## The region's observing constraint, added 14 September 2026

One entry rather than a table, because it is a finding about every methane row
above rather than a candidate.

[`notes/grounding-yrd.md`](grounding-yrd.md) now records that SWIR sensors
"suffer from frequent data gaps due to cloud cover (particularly in southern
China during the monsoon season)", and that rice paddies, lakes and wetlands in
southern China consequently carry posterior emission uncertainties of 53 to 69
percent (Zhong et al., 2026, `10.5194/amt-19-4759-2026`). **That is the same
physical cause that limits rice mapping here to fewer than eight clear Landsat
observations a year**, which this file's rice rows are all constrained by, acting
on the other end of the same inference chain.

The practical consequence for this inventory is that **a ground-based row is
worth more here than its resolution suggests**. The same paper puts current
TROPOMI plus every in-situ and ground-column site in East Asia at a DOFS of 134
for China, against 113 for TROPOMI alone — a fifth of the information from
seventeen stations. The Hefei TCCON and Lin'an GAW rows above are the in-domain
instances of that, and the Lin'an route remains the one unresolved lead among
them.

## The inversion route, added 11 September 2026

[`notes/grounding-methods.md`](grounding-methods.md) establishes that the field
solves this class of problem by Bayesian inversion rather than by regression with
corrections, and that a purpose-built open tool exists. These are the candidates
that route implies. **The layer pass that should verify them is a new one**, an
inversion feasibility pass, because none of them belongs to the rice or urban
layer.

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| **IMI 2.0** | Open-access cloud tool giving sector-resolved methane emissions at up to 0.25° × 0.3125° by analytical inversion of TROPOMI with closed-form error characterisation — the same resolution as this project's lattice, and it ingests the blended TROPOMI+GOSAT field already committed here | Three documented routes: the free IMI product on the AWS Marketplace, the source from GitHub for a local cluster, and the Integral Earth web interface. **Its input buckets were verified anonymously on 13 September 2026** — see the corrected bucket names in the inventories table above — and the boundary archive's 1 April 2018 start was confirmed against `imi-boundary-conditions` | open access; the paper is CC-BY | TROPOMI record from 2018, with the blended dataset kept current on AWS | **The preview answers, for free, whether TROPOMI can constrain emissions over this domain** — the question the flux-divergence gate could not answer. "The IMI Preview has no significant costs, and we strongly recommend using it." It reports expected DOFS, the dollar cost of a full run, and SWIR albedo as an artefact indicator | documented only |
| GRPI emission factors | The global compilation of 2,301 rice paddy field measurements behind a generalised additive model of growing-season emission factors, as a function of soil texture, pre-season water status, water regime, planting method, cultivar, organic amendment and climate zone | deposit route still not established. **The paper is not paywalled, which this entry had wrong**: `10.1029/2024EF005479` carries CC-BY-NC-ND 4.0 in Crossref, so it is open access, and the obstacle is Wiley returning 403 to this network rather than a subscription wall | **CC-BY-NC-ND 4.0**, from Crossref; *this entry said "unknown" and described the paper as paywalled* | global, by country | **The function that turns a rice map into an emission estimate.** Every predictor in the model is a mechanism `notes/grounding-yrd.md` already identifies | unverified |
| 30 m global cropland database | The cropland layer GRPI combines with its flooded-vegetation algorithm | not established | unknown | global, 30 m | The second half of GRPI's rice-area method, and a possible independent check on the NESDC layer | unverified |

## Urban and waste facilities, added 11 September 2026

[`notes/grounding-urban.md`](grounding-urban.md) establishes that the dominant
urban methane sector is landfills, that landfills are quantifiable because they
are mapped on facility coordinates, and that population-like fractional proxies
cannot separate the sectors allocated by them. **These are therefore the
candidates that matter for the urban layer, and the urban layer pass should
verify them.** None is a raster; all are facility inventories, which is the
point.

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| Underground wastewater treatment plants | A dataset of the distribution and characterisation of underground wastewater treatment plants in China, with spatial distribution, process and discharge standards; underground plants are noted as preferring southeastern coastal locations, which is this domain | **Deposit found and downloaded 13 September 2026: figshare `10.6084/m9.figshare.26085265.v2`, one file of 243,218 B with MD5, anonymous.** The paper's Data Records section names it; this inventory had recorded "deposit route not checked" | **CC BY 4.0 for the deposit**, against CC-BY-NC-ND 4.0 for the article. The deposit's licence is the one that governs reuse of the data and it is the permissive one | published 2024; **construction years 2012 to 2025 for the underground plants, of which 9 of the 28 in this domain were built by 2018** | Facility coordinates for one of the three population-allocated sectors, in the region where they concentrate. **The premise this entry flagged as unverified is confirmed exactly: 201 underground and 2,464 aboveground.** The workbook has two sheets, `U-WWTP` with 201 rows and `A-WWTP` with 2,464, so the title names underground plants only but the file carries both. Fourteen columns including `Local_lon` and `Local_lat`. **In the four provinces: 28 underground (Zhejiang 10, Jiangsu 8, Shanghai 6, Anhui 4) and 394 aboveground (Jiangsu 163, Anhui 118, Zhejiang 62, Shanghai 51), and all 422 carry usable coordinates inside the lattice box** | **verified accessible**, open anonymous |
| MSW landfill site database | Site-specific information for more than 300 major municipal solid waste landfills in China, with emissions by IPCC first-order decay from 1.015 Mt in 2005 to a peak of 2.161 Mt around 2015 and 1.98 Mt in 2023, compared against hyperspectral satellite observations at three sites | No deposit found. `10.1016/j.jenvman.2026.128672` resolves correctly — to *Integrating inventory models and satellite observations for site-level methane emissions from municipal solid waste landfills in China* — but Crossref lists **only Elsevier's TDM and `policy-004` licences and no Creative Commons licence**, so the article is not open access and its full text is unreadable from this network. Crossref registers no dataset relation | **not open**; Elsevier user licence only | 2005–2023 | **The highest-value urban candidate.** Facility coordinates for the sector that dominates urban methane and that the separability finding says is the only one quantifiable. **Verification established the obstacle rather than the route: the paper is paywalled, so whether the database is distributed still cannot be read.** The GHGSat entry below is now the reachable substitute for part of this | unverified, paywalled |
| China oil and gas CH4 database | Methane emissions from China's oil and gas systems 1990–2022, about sevenfold growth from 0.5 to 4.0 Tg per year, with 80 percent of emissions tracked as refineries, facilities, pipelines and field sources, and city-level distribution pipeline lengths | **Deposit found 13 September 2026 in the paper's own data availability statement: figshare `10.6084/m9.figshare.27186936.v1`, 75 files totalling 108,661,045 B, MD5 on all, anonymous.** It holds gridded annual emissions as netCDF and the infrastructure sources as shapefiles — `Point_Refinery_CH4`, `Point_Storage_CH4` and others | **CC BY 4.0** for both article and deposit; *this entry said "article licence"* | 1990–2022, annual, per the deposit description | City totals for gas distribution, which is the sector whose published global product is faulted for allocating "only based on population densities without using an urban land cover map". **That named deficiency is what this project's impervious layer is.** The claim that pipeline lengths cover 347 prefecture-level cities remains unverified — the shapefiles were listed but not downloaded. **At 109 MB the whole deposit is cheap enough to settle that in one fetch** | **verified accessible**, open anonymous |
| GHGSat global waste survey | 1,447 clear-sky observations from GHGSat C1–C5 of 151 waste disposal sites across 130 urban areas in 47 countries over six continents, 2021–2022, totalling 2.8 Mt CH4 per year | **Deposit found 13 September 2026 in the paper's data availability statement: the GHGSat-detected plumes are on Zenodo, `10.5281/zenodo.16641834`, with analysis code on Code Ocean capsule 2078268.** This inventory recorded "no separate data deposit found". **The Zenodo route is blocked from this network**, so the deposit is located but not opened | **CC BY 4.0**, from Crossref; *this entry said "article licence"* | 2021–2022 | Point-source quantification of the dominant sector. It includes an example plume from a wastewater treatment plant near Shanghai, **which was filtered from the analysis** and so is an illustration rather than a quantified emission. TROPOMI plumes were detected for 46 of the 130 urban areas. **This is now the most reachable facility-level lead for the landfill sector**, subject to the Zenodo block, and it is the substitute for the paywalled MSW database above | documented only, deposit located, route blocked |

## Coal, building form and in-domain observation, added 13 September 2026

The coal entry exists because four grounding passes missed the sector entirely;
[`notes/grounding-yrd.md`](grounding-yrd.md) now records it. The building-form
entries exist because the urban record identifies vertical information as the
dimension an impervious fraction lacks. The last two are in-domain observations
and are the first entries in this file that are neither products nor
inventories.

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| Gridded Chinese coal mine methane | Bottom-up inventory at **0.25 by 0.25 degrees — this project's own resolution** — from a public database of more than 10,000 mines for 2011, which is 25 times more than EDGAR v4.2 and 2.5 times more than v4.3.2, with provincial emission factors. It finds provincial contributions differing significantly from EDGAR's, and names Anhui as the largest eastern emitter | No deposit reached, re-attempted 13 September 2026 with the same result. The paper is paywalled; the publisher's page and an institutional repository copy both refused, and no data availability statement was read | unknown | 2011, annual | **The prior for the one major source in this domain that neither predictor represents.** Whether it is distributed is the thing to establish, and it is the single question that would most change an inversion prior for northern Anhui | unverified |
| 30 m annual building height, China | Building height at 30 m, **annual from 1990 to 2019**, so it contains 2000, 2010 and 2018 — which no other height product does | **Deposit found 13 September 2026 in the paper's data availability statement: figshare `10.6084/m9.figshare.29918978.v6`, 255 files totalling 20,259,386,448 B, MD5 on all, anonymous.** Tiles are named `LON_LAT.tif` for the lower-left corner at 2° steps; **the 22 tiles covering this lattice total 5,410,190,009 B, so the subset is 5.4 GB of a 20.3 GB deposit** | **CC BY 4.0** for both article and deposit | 1990–2019, annual, 30 m. **The encoding is a 30-band stack per tile and the band order is descending: band 1 is 2019 and band 30 is 1990**, which is the same trap class as the GAIA and GISA year directions this repository has already been caught by once | The vertical dimension the Shanghai underestimate names as missing. **Adopt with a second product or not at all**, per the GAIA–GISA lesson — and CMAB below is now reachable, so the pair exists | **verified accessible**, open anonymous |
| CMAB | National multi-attribute building dataset at building-instance level, carrying function among its attributes | **Deposit found 13 September 2026 in the paper's Data Records section: figshare `10.6084/m9.figshare.27992417`, now at v7 where the article cites v2, 37 files totalling 16,973,214,343 B, MD5 on all, anonymous.** Organised by province and natural city as GIS polygons in WGS84, each rooftop carrying height, function, age and quality | **CC BY 4.0 for the deposit**, against CC-BY-NC-ND 4.0 for the article — the second entry in this file where those differ | one epoch. **At 17.0 GB it is the largest deposit in this inventory and exceeds the 5 GB budget this pass worked under**, so nothing was downloaded | **Building function, which is closer to the gas-and-waste mechanism than either footprint or height.** It would separate residential from industrial without inferring it from volume. **A province-organised deposit means the four provinces can be taken without the other 27**, which is what makes 17 GB tractable | **verified accessible**, open anonymous |
| Shaoxing UAV methane record | A portable CH4 detector on unmanned aerial vehicles and electric bicycles, observing vertical and spatiotemporal CH4 distribution over Shaoxing from April 2022 to February 2023, estimating annual emissions near 69 t km⁻² yr⁻¹ and describing that as higher than other cities worldwide | *Journal of Environmental Sciences* `10.1016/j.jes.2024.03.045`; no deposit named, and **the DOI resolves to the right paper but Crossref lists only Elsevier's TDM licence, so it is not open access and the full text is unreadable from this network** | **not open**; Elsevier user licence only | April 2022 to February 2023 | **In-domain city-scale methane observation in Zhejiang**, and the only one in this file that measures methane in a city inside the lattice. Its period does not overlap 2018 | unverified |
| Shanghai urban canopy layer GHG site | Nearly two years of continuous high-precision in-situ measurement from the 632 m Shanghai Tower at 121.51 E, 31.23 N, April 2021 to March 2023, by cavity ring-down spectrometer | *Atmospheric Chemistry and Physics* `10.5194/acp-26-5477-2026`, **PDF downloaded and read; no data deposit is named in it** | **CC BY 4.0** | April 2021 to March 2023 | **It measures CO2 and CO, not methane**, which is why it is recorded rather than pursued. It is noted because the site, the instrument and the tower exist inside the lattice, and a methane channel on the same platform would be the in-domain urban observation this project lacks | unverified |

## The highest-value unverified items

The brief that produced this file named three: the CCD-Rice polygons for rice
reference data, the irrigation regime maps for the missing covariate, and MMCP
for a sectoral comparison. **One of the three is no longer unverified.**

The CCD-Rice polygons turned out to be published, openly licensed and 1.9 MB,
on a figshare DOI distinct from the Science Data Bank record that holds the
maps. An earlier reconnaissance in this repository concluded that CCD-Rice "does
not publish" its validation data; that conclusion was wrong, and it was wrong
because it searched the maps' deposit and not the paper's data availability
statement. The lesson is worth keeping: a product's reference data and its
product data need not live on the same platform, and checking one is not
checking the other.

So the three that remain are the **irrigation regime maps**, because the water
regime is the largest missing covariate the grounding identifies and no deposit
is named for it; **MMCP**, because a monthly provincial rice series is the
cheapest available check on the seasonality argument and its licence is the most
restrictive here, so the constraint needs establishing before work depends on
it; and the **in-domain surface records** at Lin'an and Suzhou, because they are
the only independent measurements of this region's methane seasonality and
neither has a known route.

**Two of those three are settled as of 13 September 2026, and the reasoning for
one of them was wrong.** MMCP is fetched, read and CC BY 4.0 — not
CC-BY-NC-ND 4.0, so the licence constraint this paragraph treats as the reason
to verify it first does not exist. The irrigation regime maps remain without a
deposit, but **their pair does not**: the 500 m irrigated cropland maps are on
figshare under CC BY 4.0, 87 MB for 2000 to 2019, covering all three thesis
years, which is the reachable half of the pair the GAIA–GISA rule asks for. The
Lin'an and Suzhou records are still unrouted and are now the only items on this
list of three that verification did not move.

## What the 13 September 2026 verification changed, in one place

Every entry that was *unverified* or *documented only* was attempted. The
pattern is worth stating because it is the opposite of what an inventory built
from reading would predict.

**Seven deposits exist for entries that recorded none**, and all seven were
found in the papers' own data availability or Data Records sections rather than
by searching: the 500 m irrigated cropland maps, China's oil and gas CH4
inventory, the underground wastewater plants, the 30 m building heights, CMAB,
the GHGSat plume set (on Zenodo, which is blocked) and the natural-gas-vehicle
measurements (DataSpace at Princeton). **The lesson is the one the CCD-Rice
polygons already taught and it was not applied: read the article's data
statement, not the product's landing page.** Five of these seven entries were
marked *documented only* or *unverified* on the strength of having read the
abstract.

**Licences were more permissive than recorded, not less.** Eight entries gained
a verified CC BY 4.0 or CC0 where they had held "unknown", "article licence" or
"not established". One moved the other way: the rice-mapping review is
CC-BY-NC-ND, not CC-BY. And **two entries deposit under a different licence
than their article carries** — the underground wastewater plants and CMAB are
both NC-ND as articles and CC BY 4.0 as data.

**The two factual errors found were both in this file, not in the products.**
MMCP's licence was recorded as the most restrictive here and is the least. The
IMI boundary archive was recorded as beginning one day before this project's
first granule and begins 29 days before it. Every count, size and date checked
against a file otherwise held, including all four CCD-Rice province counts and
the 201-and-2,464 wastewater premise this file had flagged as unverified.

**Four entries were blocked by publishers rather than by licences**, which is
worth separating from being closed. China_AP, the aquaculture-index mapping,
the irrigation regime maps and EFSP are all open-access articles — CC BY 4.0,
CC BY 4.0, CC-BY-NC 4.0 and MDPI's uniform CC BY 4.0 — whose text this network
could not retrieve, because ScienceDirect, Wiley and MDPI return 403 and
Elsevier serves an interstitial. Their data statements are readable in
principle by anyone with a browser and are unread here. **Two entries are
genuinely not open**: the MSW landfill database and the Suzhou network register
no Creative Commons licence at all. The inventory had described GRPI as
paywalled; it is CC-BY-NC-ND and open, and only the fetch failed.

**One route regressed.** zenodo.org refuses this network, which blocks
GISA-new, APRA500, the CCD-Rice code and the GHGSat plumes. *The mechanism
recorded here on 13 September — a TCP timeout — was wrong, and* The Zenodo
block *below has the correct diagnosis.* Two of those four were
recorded as *verified accessible* on the strength of a request that succeeded
when it was made. `data/processed/README.md` already recorded the same host
refusing GISA's per-tile links, so this is a standing condition of the network
rather than news, and the honest form of a status is that it describes a moment.

**And one recorded obstacle was not real.** The GISA tiles are individually
downloadable from Wuhan University, 257 of them at about 8.7 MB, where
`data/processed/README.md` said the 882 MB bundle was the only reachable route.
Four tiles, about 35 MB, is what this study needed.

**On 11 September 2026 a fourth joined them and it outranks all three.** The
**IMI 2.0 preview** is free, is documented as strongly recommended before any
full run, ingests the exact blended product this repository committed, and
reports the expected degrees of freedom for signal over a user-chosen domain. It
answers whether TROPOMI can constrain methane emissions over these four
provinces at all — a question that was gated on a flux-divergence feasibility
test which could not answer it, and whose reasoning `notes/decisions.md` records
only from 12 September 2026 and only as a reconstruction. It is the cheapest
unverified item in this file and the one with the largest consequence for what
the project can claim.

Behind it, the **MSW landfill site database** is the highest-value urban
candidate, because the urban grounding establishes that landfills dominate urban
methane and that they are quantifiable only through facility coordinates, which
is the one thing a fractional layer cannot supply.

**Added 13 September 2026: the gridded coal inventory now sits beside it.** Four
grounding passes missed the sector; the inventory exists at this project's exact
resolution, it corrects EDGAR's provincial allocation for the one major source in
this domain that neither predictor represents, and whether it is distributed
could not be established because the paper is paywalled and two open routes
refused. It is the second-highest-value unverified item and the one whose answer
is a single successful request away.

## Reference-data candidates found while verifying, 13 September 2026

Deposits and products that bear on the accuracy assessment and were not in this
file. None of them is a probability sample of this domain; they are recorded so
a later pass does not re-find them.

| Candidate | What it is | Route | Licence | Why it is here |
|---|---|---|---|---|
| **SinoLC-1** | The first 1 m national land-cover map of China, from a deep-learning framework over free imagery | Zenodo `10.5281/zenodo.7707461`, **blocked**. The paper is ESSD `10.5194/essd-15-4749-2023`, CC BY 4.0, and was read in full | **CC BY 4.0** for the paper; the deposit's own terms not read | **The case that finer is not better.** Verified verbatim from the paper: an overall accuracy of **73.61 percent** and a kappa of **0.6595** on 106,344 counted validation points. That is below GLC_FCS30's 82.5 percent at 30 m and below NLCD 2019's 77.5 percent, so a 1 m product here fails Olofsson's second recommendation against the 30 m products it would validate. Its imagery was "acquired around the year 2021", unevenly, with older frames in the north and northwest |
| **CISC2020 / CISC2022** | Enhanced 30 m impervious surfaces for China from 2 m and 30 m fusion | *Scientific Data* `10.1038/s41597-026-06619-3`, 2026; deposit route not established | **CC-BY-NC-ND 4.0** for the article, from Crossref | **Not a finer product, which the framing of this task assumed.** It is 30 m built from finer inputs, so it is a fourth impervious product in the GISA and GAIA role rather than reference data. Years **2020 and 2022 only** |
| **1 m impervious surface, Yangtze River Economic Belt** | Joint super-resolution and segmentation for 1 m impervious surface area mapping | *GIScience & Remote Sensing* `10.1080/15481603.2025.2610548`, 2026; deposit route not established | **CC-BY-NC 4.0** for the article, from Crossref | In-domain and at 1 m, which no other impervious candidate is. Its accuracy was not read, so whether it clears the SinoLC-1 bar is unknown, and a super-resolved product inherits its own generator's error |
| **EcoVision** | Submeter land cover over China's 42 major cities | *Journal of Remote Sensing* `10.34133/remotesensing.0811`, 2025; no CC licence in Crossref; deposit route not established | not established | City-only coverage, so it can serve urban cells and not rice cells. The asymmetry matters: the impervious layer could be assessed where the rice layer could not |
| **UGS-1m** | Fine-grained urban green space at 1 m for 34 major Chinese cities | ESSD `10.5194/essd-2022-75` | **CC BY 4.0** | Found while searching for EcoVision. Green space rather than impervious surface or rice, so it serves neither layer directly, and it is recorded only so the 1 m Chinese urban family is complete in this file |
| **Xing, Stehman, Foody and Pengra (2021)** | Simple averaging against latent class modelling for estimating land-cover area when the reference data contain error | *Land* `10.3390/land10010035`, MDPI, so CC BY 4.0; `www.mdpi.com` returns 403 to this network so the text was not read | **CC BY 4.0** | The method paper for the situation this project is actually in: reference data that are not error-free. It is a method and not data, and it belongs in the register rather than here, but it was found in this search |

**The pattern is the one this file already records for products and it now holds
for reference data too: the sample sets are class-label point sets, and this
project's layers are fractional.** Neither of the two deposited sets in the
table above carries a fraction, LCMAP does not either, and the one candidate
that could in principle yield a fraction, Globe230k, covers 0.59 tiles per cell.

### Whether any of them satisfies Olofsson's recommendations 1 to 3

| | Probability sampling design | Reference more accurate than the map | Consistent analysis |
|---|---|---|---|
| CCD-Rice polygons | **No.** Purposive; the paper selected "only 2 to 4 years in each provincial administrative region" on imagery availability | Yes, very-high-resolution visual interpretation | Not reachable, because 1 fails |
| Global LC validation samples | **Partly, and not in the sense required.** The *allocation* is a textbook stratified design — the Cochran sample-size formula with `W_i` the global area proportion per class — but the *frame* is eight donor reference datasets with points "randomly collected from each polygon". Randomisation inside donor polygons is not a probability sample of this domain and the donor polygons' inclusion probability is unknown. **The file also drops the per-sample source code, so which donor a point came from cannot be recovered** | Yes | No, and now on measured grounds: **124 points in the four provinces over 20 of 926 cells, of which 12 are impervious surface**, carrying class labels against a fractional map |
| Globe230k | **No.** The user guide states the sampling deliberately favours rare classes — "we intentionally give more chance to the rare categories to be sampled" — with no stated probabilities, so it is a disproportionate design whose inclusion probabilities are not recoverable. It still does not report how many candidates were rejected | Yes, 1 m dense annotation | No. 0.59 tiles per cell cannot form a cell fraction, and the tile names carry no georeference so even locating them costs 11.5 GB |
| LCMAP | **Yes** — and it is the only one here that is. But US-only | Yes | Not applicable outside CONUS |
| SinoLC-1 | Its own validation used "over 100 000 random samples", not distributed separately | **No. 73.61 percent overall accuracy fails recommendation 2** against the 30 m products it would validate | No |

**So no deposited sample set satisfies all three over this domain, and this is
now measured rather than inferred.** LCMAP satisfies them and is in the wrong
country; the global validation samples come closest and fail on the frame, on
carrying labels rather than fractions, and on a four-province count of 124 that
includes only 12 impervious points; Globe230k fails on a deliberately
disproportionate design and on density; SinoLC-1 fails on accuracy. That is the finding, and
it is what makes the two routes in `notes/grounding-methods.md` necessary rather
than optional.

## Whether any finer product is more accurate than the products it would validate

Verified 13 September 2026, and this is the test that decides whether Route B in
[`notes/grounding-methods.md`](grounding-methods.md) can work at all.

**The bar.** A reference layer has to beat the product it assesses. This
project's impervious layers report **GISA at an F-score of 0.954** and
**GISA-new at 93.12 percent overall accuracy**.

| Candidate | Resolution | Reported accuracy | Beats the bar? |
|---|---|---|---|
| SinoLC-1 | 1.07 m | overall **73.61 %**, kappa 0.6595, 11 classes | **No**, and by a wide margin |
| EcoVision | ~0.5 m | overall **83.6 %**, 8 classes, urban areas only | **No** |
| ISA-1 | 1 m | impervious-class **F1 75.53**, recall 61.76; two-class mean F1 85.71 | **No** |
| CISC2020/2022 | **30 m** | impervious-class spatially averaged **F1 > 0.93** | **Not clearly**, and it is not finer |

**So the answer is no, for all four**, and the reason is not resolution. Three
of the four are between two and sixty times finer than the products they would
validate and every one of them is less accurate.

### Where the comparison is not clean, stated rather than glossed

The four numbers above are not the same quantity and a reader should not treat
the table as a ranking.

* **Overall accuracy across eleven classes is not an impervious F-score.** A
  product can be poor overall and good on built-up surfaces, which are among
  the easiest classes to separate. SinoLC-1's 73.61 percent and EcoVision's
  83.6 percent are multi-class overall accuracies; GISA's 0.954 is a
  single-class F-score for impervious surface. **They are not comparable**, and
  the honest statement is that neither SinoLC-1 nor EcoVision publishes an
  impervious-class F-score that could be compared.
* **The two that are comparable are the two that matter, and the finer one
  loses.** ISA-1's impervious-class F1 of 75.53 and CISC's spatially averaged
  impervious F1 above 0.93 are both single-class impervious F-measures, so both
  can be set against GISA's 0.954. ISA-1 is far below it. CISC is close to it
  and below it, and CISC is not finer.
* **The populations differ.** GISA's F-score is global; CISC's is national;
  EcoVision's is over 42 cities' urban cores, where impervious surface is
  abundant and easy, which inflates an overall accuracy relative to a national
  figure. ISA-1's is over the Yangtze River Economic Belt, which is the closest
  population to this study area of any of them.
* **A headline mean can hide the class of interest, and ISA-1 is the case.**
  Its abstract reports 85.71 percent; that is the mean of the impervious class
  at 75.53 and the non-impervious class at 95.89, and non-impervious is the
  majority class. **Its impervious recall is 61.76 percent**, so it misses
  roughly two impervious pixels in five. Quoting 85.71 as its accuracy would
  overstate what it can validate.

### The consequence, which corrects this repository's previous conclusion

`notes/decisions.md` recorded on 13 September 2026 that Route B "is blocked on
**year**", every candidate being 2020 or later against layers for 2000, 2010
and 2018. **That was true and it was not the binding constraint.** Opening the
products shows that **no candidate at any year is more accurate than GISA**, so
even a perfectly year-matched candidate would fail Olofsson's second
recommendation. The year gap is real and it is second in line.

**A second and independent obstacle is distribution.** Of the four, one is
deposited as seven example cities rather than as a product (ISA-1), one has no
established route at all (EcoVision), and two sit behind a Zenodo service that
refused this network for the whole of this pass (SinoLC-1, CISC). **Only
ISA-1's examples were opened**, and they cover 20 of 926 cells.

## The Zenodo block, diagnosed 13 September 2026

Six entries in this file are blocked by one obstacle, so it is diagnosed here
once rather than re-guessed per entry.

**It is not a network failure and the earlier diagnosis in this file was
wrong.** The Tier 1 pass recorded "zenodo.org times out at the TCP level from
this network over IPv4 with DNS resolving normally, on every endpoint". Only
the DNS half of that is right. Measured layer by layer:

* **DNS resolves fully.** `zenodo.org` returns six A records
  (137.138.153.219, 188.185.43.153, 188.184.103.118, 188.184.98.114,
  188.185.48.75, 137.138.52.235) and six AAAA records in `2001:1458:d00::/48`.
* **TCP connects immediately.** A connect to port 443 on each of those
  addresses succeeds in under a second. There is no timeout at this layer.
* **TLS completes.** An `openssl s_client` handshake negotiates TLSv1.3 with
  `TLS_AES_256_GCM_SHA384` and presents a valid certificate for
  `CN=*.zenodo.org`, over IPv6 by default.
* **HTTP is refused.** The server answers **403 Forbidden** from `nginx`, in
  under half a second, on every path tried: `/`, `/records/<id>`,
  `/record/<id>`, `/api/records/<id>`, `/api/records/<id>/files` and `/oai2d`.

**The 403 body says what it is**, and it is worth quoting: *"Access to this
resource has been restricted due to unusual traffic from your network. If you
believe this is a mistake, please contact our support line and we will look
into your request."* It carries a reference id and a timestamp.

### It is transient and keyed to the request, not a standing ban on this network

**Retested 90 minutes later, as this task required, and the result reversed.**
At 16:53 UTC a default-`curl` request to `zenodo.org/` returned **200** and
`api/records/3551995` returned **the full record JSON**, while the browser
User-Agent that had worked before now returned the 403. The landing page that
came back explains it in Zenodo's own words: *"Zenodo is currently experiencing
slowness and intermittent outages due to heavy automated traffic from bots and
AI crawlers. We are aware of the pro[blem]"*.

So the correct characterisation is **an aggressive and fluctuating
bot-mitigation filter, keyed on request signature and changing over time**, not
a durable per-network block. The "unusual traffic from your network" wording is
the filter's generic message and should not be read as a standing ban. Two
consequences, and the second is the one that matters:

* **Which User-Agent works is not stable.** A browser string worked at 16:32
  and was refused at 16:53; the default `curl` string was dropped at 15:50 and
  served at 16:53. Retrying with a different UA, and retrying later, are both
  worth doing before concluding anything is unreachable.
* **The window was used.** Both blocked sample sets were fetched during it and
  are verified below from their files. The rows no longer rest on their papers.

**Why it looked like a timeout.** The filter treats a default `curl`
User-Agent differently from a browser one. With `curl`'s own UA the request is
**silently dropped after the TLS handshake** — the connection stays open and no
bytes ever arrive, so a client with a 20-second timeout reports a timeout and
nothing else. With a browser UA the same request returns the 403 above in 0.47
seconds. The Tier 1 pass used the default UA, saw the hang, and attributed it
to TCP. **The lesson generalises past Zenodo: a hang after a successful
connection is an application-layer refusal until proven otherwise, and the UA
is the first thing to vary.**

### It is Zenodo specifically, not a class

| Host | Result | What it rules out |
|---|---|---|
| `zenodo.org`, all paths | 403 | — |
| `www.zenodo.org` | 301 to the above | — |
| `sandbox.zenodo.org`, root and `/api/records` | **200** | Not Zenodo's software, not its certificate, not its CERN hosting |
| `cern.ch` | 302 | Not CERN infrastructure |
| `home.cern` | 200 | Not CERN infrastructure |
| `api.openaire.eu` | responds (400 to a malformed query, 200 to a valid one) | Not the European research-infrastructure class |
| `explore.openaire.eu` | 403 | An unrelated filter on a different host; its API works |
| `api.figshare.com`, `api.datacite.org`, `doi.org` | 200, 200, 302 | Not this network's outbound HTTPS |

Zenodo's own sandbox, on the same domain and the same wildcard certificate,
serves this network normally. The restriction is scoped to the production
service.

### No route reaches a record's files

Metadata is reachable and files are not. **DataCite** serves the full record
metadata for any Zenodo DOI, but its `contentUrl`, `sizes` and `formats` fields
are empty for the records checked, and its `rights` field is empty too, so it
cannot substitute for reading a deposit's licence. **OpenAIRE** serves the
harvested record including an access-rights and licence field, which is one
step better and still second-hand. Everything else fails: the DOI resolver
redirects to `zenodo.org` and lands on the 403; the legacy `/record/` path,
the REST API and OAI-PMH are all 403; and `data.zenodo.org` and
`files.zenodo.org` do not resolve, so there is no separate file host to try. No
mirror was found for any of the six records.

**This was established without a VPN and without any credential.** The
metadata routes above remain the reliable fallback when the filter is closed;
during an open window the REST API serves records and files normally.

### The six entries it blocks, as distinct from entries blocked for other reasons

| Entry | Where it is | Blocked by |
|---|---|---|
| GISA-new | Urban table | **the Zenodo block** |
| APRA500 | Rice table | **the Zenodo block** |
| CCD-Rice code | Rice table | **the Zenodo block**, though the question it was wanted for is now answered from the paper |
| GHGSat plume set | Urban and waste facilities | **the Zenodo block** |
| SinoLC-1 | Reference data and method | **the Zenodo block** (`10.5281/zenodo.7707461`) |
| Global land cover validation samples | Reference data and method | **the Zenodo block** |
| Globe230k | Reference data and method | **the Zenodo block** |

That is seven, not the six the task assumed, because SinoLC-1's product deposit
is on Zenodo as well and this file had not recorded where it lived. **Three of
the seven were fetched during the 16:53 window** — the two validation sample
sets and Globe230k's small files — so "blocked" describes the filter's state at
a moment and not the deposits.

**Entries blocked for other reasons, which this obstacle does not explain:**
China_AP and the aquaculture-index mapping are blocked by publishers returning
403 to the *articles* that name their routes; the MSW landfill database, the
Suzhou network and the Shaoxing UAV record are behind paywalls with no
Creative Commons licence at all; the gridded coal inventory is paywalled; the
irrigation regime maps and EFSP are open-access articles whose text Elsevier
and MDPI would not serve; WetCHARTs needs a NASA Earthdata login; MUSICA needs
a terms click. **Confusing any of those with the Zenodo block would send a
future pass to the wrong remedy.**

## What this file is for

Each layer pass verifies its own candidates rather than there being a standalone
verification task, so this is a checklist whose statuses change as work
proceeds. Three properties make it worth keeping as a file rather than as a
conversation: it separates what was tried from what was read, it records the
licence beside the route so that a constraint is met before work depends on it,
and it records rejections and their reasons so a candidate is not reconsidered
from scratch.
