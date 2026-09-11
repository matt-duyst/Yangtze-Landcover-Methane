# Dataset leads

Working material, not paper content. A checklist of every candidate dataset the
region searches turned up, so that the layer-by-layer passes that follow have
something to verify against rather than starting from a conversation. The
citations behind these entries are in [`notes/references.md`](references.md);
what is here is the route, the licence and the status.

**This file is expected to change.** Each layer pass verifies its own
candidates, so a status moves as work proceeds and the file is updated rather
than rewritten. It is not a verification task in its own right, and nothing here
was verified beyond what a status claims.

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

## Methane observations

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| Blended TROPOMI+GOSAT | Machine-learning-corrected XCH4, the product the composite's third field comes from | CaltechData record `etz11-jpg19` redirecting to `sdsc.osn.xsede.org`, HTTP-range readable through `src/methane/blended.py` | CC-BY-4.0 | 2018–2023 | Already used; the blended band of `methane_composite_2018.tif` | **verified accessible** |
| Hefei TCCON GGG2020.R1 | Ground-based FTS column-averaged XCH4, the reference network TROPOMI validation uses | CaltechData, anonymous, three files totalling 57.49 MB, one netCDF4 for the whole record | TCCON Data Use Policy — **contact the site PIs 4 to 6 weeks before submission, 1 to 2 weeks before a presentation; redistribution reserved** | 2015-11-02 to 2025-12-30; 2018 present but sparse, 2,767 retrievals on 44 days | The only in-domain measurement more accurate than the map. Nine days in 2018 have both a TROPOMI overpass of its cell and TCCON data | **verified accessible** |
| Xianghe TCCON | The other Chinese TCCON site | — | — | from 2018-06-14 | **Ruled out.** 39.75 N is 4.55 degrees, about 505 km, north of the lattice | considered and excluded |
| Lin'an WMO/GAW | In-situ surface CH4 at a regional background station in Zhejiang, inside the domain | WDCGG not tried; the station's record is analysed in Shan et al. (2022) | unknown | long-running; 1,942 ppb annual mean in 2011 against Waliguan's 1,861 | A background reference the column field is embedded in, and a surface seasonal cycle | unverified |
| Suzhou three-station network | Surface CH4 at Wujiang, Xiangcheng and Zhangjiagang, all in Jiangsu | no deposit named in Guo et al. (2023) | unknown | 2020–2021 | The in-domain surface seasonal cycle, peaking mid-July and late August, which the composite's October sounding peak must be read against | unverified |

A premise correction belongs here rather than in a status. It was assumed that
Lin'an might not be in WDCGG because the China Meteorological Administration's
greenhouse gas bulletin names only Waliguan and Shangdianzi. **The bulletin
names Lin'an**, and Lin'an is one of three WMO/GAW regional stations China
operates, with Shangdianzi in Beijing and Longfengshan in Heilongjiang. The
station's existence and its figures are not the uncertainty; the data route is.

## Methane inventories

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| MMCP | Monthly methane emissions for 31 mainland provinces across eight sectors — coal mining, oil and gas systems, energy combustion, rice cultivation, livestock, solid waste, wastewater and wetlands — with rice split into single-season and double-season, the latter further into early and late | figshare `10.6084/m9.figshare.26806522.v1`; processing code at `github.com/KowComical/CM_Methane_Database` | **CC-BY-NC-ND 4.0** — non-commercial and no derivatives, which constrains reuse more than anything else in this inventory | January 2013 to December 2022; **2018 present** | The sectoral comparison this study has never had: a monthly provincial rice-methane series to set the composite's seasonality against | documented only |
| City-scale source-resolved inventory | Methane for 339 prefecture-level cities, resolved by source | Supporting Information PDF attached to the article; no separate data deposit found | article licence | 2018 to 2024 | The urban composition `ERRATA.md` 5.3 rests on, including the 38 cities where waste dominates | documented only |
| EDGAR | The global gridded anthropogenic inventory | already known | — | — | Known biased **in both directions here**: Huang et al. (2021) found it underestimating agricultural soils especially in growing seasons, and its v432 and v5.0 posteriors differ by eight points of regional share | known |
| Wastewater facility factors | Facility-level CH4 emission factors from atmospheric measurements at 105 treatment plants, including thirteen in Nanjing measured across three seasons | no deposit named | unknown | measurements to 2023 | The sector `ERRATA.md` 5.3 records the thesis as omitting entirely | unverified |

## Rice

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| CCD-Rice | Paddy rice distribution for China at 30 m, 27 annual GeoTIFFs totalling 5.37 GB | Science Data Bank `13e7fbb10ef343659ae4c91089584f12` through the Croissant route `src/fetch/scidb.py` already handles, with **MD5 on every file** | ODC-BY 1.0 | 1990 to 2016 — **reaches 2000 and 2010, does not reach 2018** | The second rice product for the historical years, the role GISA plays for impervious surface | **verified accessible** |
| **CCD-Rice validation polygons** | Sample polygons visually interpreted from very-high-resolution Google Earth imagery, in GeoParquet, with `covertype`, `region` and `year` fields and six classes: non-cropland, single-season rice certain, double-season rice certain, rice of uncertain season, other crops, non-rice | figshare `10.6084/m9.figshare.25515019.v3`, a single 1.9 MB file on the route `src/fetch/figshare.py` already handles; MD5 `927e517583c1999650b90a087db19ffb` confirmed against the deposit | **CC-BY-4.0** | 3,619 polygons nationally over 2002 to 2016; **777 in the four provinces** — Shanghai 338, Jiangsu 167, Zhejiang 159, Anhui 113 — in the years 2003, 2004, 2011, 2013 and 2014 | **The best reference-data lead found anywhere in this work**: independent, published, openly licensed, in-domain, and more accurate than any map here | **verified accessible** |
| CCD-Rice code | The product's own processing code | Zenodo `10.5281/zenodo.15468566` | MIT | — | Reading how the thresholds were set, which matters because they were re-determined against statistical areas | documented only |
| ChinaRiceCalendar | Transplanting, heading and maturity dates for early-, middle- and late-season rice, as raster at 250 m, 1 km and 10 km | Harvard Dataverse `10.7910/DVN/EUP8EY` | Dataverse terms, not checked | 2003 to 2022, with five period means | The calendar the growing-season argument rests on, and the input to any seasonal recompositing | documented only |
| Irrigation regime maps | Water-saving against flooding irrigation across Chinese paddy lands at 500 m, from province-wise random forests over 123 MODIS and Sentinel-1 features | no deposit named in Wang et al. (2024) | unknown | **annual, and the start year is unestablished**; the end is 2022, so whether it reaches 2018 is not in doubt but whether it reaches 2000 or 2010 is | **The missing water-regime covariate**, which is the mechanism the grounding identifies as having a larger dynamic range than extent. Overall accuracy near 0.73, and an R² above 0.92 against city and provincial census area — the census assimilation is why it needs care rather than adoption | unverified |
| CH4MOD | The semi-empirical paddy methane model, as used by the cropping-system study | model, not data | — | — | The route from a rice layer plus a water regime to an emission estimate, which this reproduction has not taken | known, not applied |
| NESDC single-season rice | The rice layer the analysis grid carries | committed | — | 2017–2022 | in use | in use |
| GloRice | The second rice layer, at 5 arcmin | committed | — | 1961–2021 | in use | in use |
| **APRA500** | Annual paddy rice planting area and cropping intensity for the Asian monsoon region at 500 m, from MODIS and a phenology-based method | Zenodo `10.5281/zenodo.5555721`, twenty-eight files of about 1.7 MB each — one GeoTIFF archive per year plus three-year composites. The API returns the file listing and a `paddyRice2018.zip` request returns HTTP 200 from this machine | **CC-BY-4.0** | 2000 to 2020 — **the only rice product of any kind that covers all three thesis years** | The historical-years gap, filled by one product and one method instead of NESDC plus CCD-Rice. At 500 m it is the coarsest candidate, and the rice-mapping review's finding that products lose consistency in fragmented fields bites hardest here | **verified accessible** |
| **EFSP** | Single and double paddy rice and cropping intensity for China at 30 m, from more than 684,000 Landsat scenes on Earth Engine | no deposit named in Wei et al. (2022) | unknown | 2014 to 2019; **reaches 2018** | A 30 m in-domain alternative to the committed NESDC layer for the analysis year, with a published accuracy: producer 0.92–0.96 against user 0.76–0.87, kappa 0.67–0.80, R² above 0.88 against statistics. **Producer exceeding user by that margin is over-detection**, which inflates a per-cell fraction rather than thinning it, so it would need the GAIA–GISA treatment rather than substitution | unverified |
| Zhu et al. PPPM maps | Annual single- and double-cropping rice for southern China at 30 m by the algorithm the 2023 thesis used, from Landsat 5, 7 and 8 | **not established.** The article is paywalled, OpenAlex records no open version, and the DOAJ record's only full-text link is the publisher DOI, so no data availability statement was readable | unknown | 1999 to 2019; covers 2000, 2010 and 2018 | **The gating lead for the whole PPPM route.** If obtainable it supplies a single-method layer for all three thesis years and removes the coverage argument for a reimplementation. Its "southern China" explicitly includes Anhui and Jiangsu | unverified |
| 500 m irrigated cropland maps | Irrigated cropland for China at 500 m over twenty years, from MODIS plus statistics and existing irrigation products | no deposit route established from Zhang, Dong and Ge (2022), `10.1038/s41597-022-01522-z` | unknown | twenty years to about 2020 | A second irrigation layer beside the water-saving-against-flooding maps above, at the same resolution. **It assimilates statistics**, which is the same reason its neighbour needs care rather than adoption, and the two together would be the pair the GAIA–GISA lesson calls for | unverified |
| NESEA-Rice10 | Annual paddy rice at 10 m for Northeast and Southeast Asia | Zenodo `10.5281/zenodo.5645344`, not tried | — | 2017 to 2019 | **Ruled out on extent.** Its "Northeast Asia" is Liaoning, Jilin and Heilongjiang with Korea and Japan; its "Southeast Asia" is six countries to the south. The Yangtze River Delta is in neither, despite 10 m and 2018 having made it the most attractive product on the list | considered and excluded |
| 30 m Northeastern China rice | Annual paddy rice at 30 m, 2000 to 2023 | figshare `10.6084/m9.figshare.28407710` | CC-BY-4.0 | 2000 to 2023 | **Ruled out on extent**: Northeastern China. Recorded so the reason is on file, because the resolution and the twenty-four-year span would otherwise make it the best candidate here | considered and excluded |
| 30 m South and Southeast Asia rice | Paddy rice distribution and cropping intensity at 30 m, 1995 to 2024 | not established, from Zhao et al. (2026), `10.5194/essd-18-5583-2026` | unknown | 1995 to 2024 | **Ruled out on extent.** Kept because its first two authors are the authors of the paddy-rice-and-XCH4 Reply, so the group that established the 0.5-degree correlation built the high-resolution map it called for — for another continent | considered and excluded |
| Rice mapping product review | A consistency assessment of twenty-five rice products, three global and twenty-two regional, over China, Heilongjiang and Vietnam | `10.1016/j.srs.2024.100172`, open access | CC-BY | published 2024 | **The map of this table's own territory.** It finds products losing consistency in fragmented fields, cloud and complex cropping challenging subtropical mapping, no product combining wide coverage with fine resolution and a long series, and ground-truth deficiency impeding validation — the last of which is this repository's own accuracy-assessment conclusion, reached independently | **verified accessible** |

Three of the four products this pass examined for the first time turned out to be
out of domain, which is the most useful thing the pass established for this file.
**A product's resolution and year coverage are the attributes a lead is recorded
on, and its spatial extent is the one that disqualifies it**, so extent should be
checked before either. All three were recorded as leads on the strength of
resolution and years.

## Urban

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| GISA-new | Impervious surface as a first-year-of-imperviousness encoding in 20-degree tiles, 99 files totalling 5.82 GB with a `.vrt` mosaic index | Zenodo `10.5281/zenodo.14848113`. **The landing page returns 403 from this network and the API returns 200**, and a file `HEAD` returns 200 with a content length, so downloads work | CC-BY-4.0, open | filenames say 1972 to 2021 while the record description says 1985 to 2021, **a discrepancy to resolve before use**; covers 2000, 2010 and 2018 | A fourth impervious product covering all three thesis years, which no other candidate does | **verified accessible** |
| GISA 1.0 and 2.0 validation samples | 120,777 sites from 270 cities, 88,822 ZY-3 samples from 45 cities, 118,822 ZY-3 test samples | **not distributed.** The GISA 1.0 Zenodo record holds 922 files, 2.88 GB, of which 921 are GeoTIFF tiles and one is a README. The paper's stated route at `irsip.whu.edu.cn` returns 404 | — | — | Would have been urban reference data; is not available | not distributed |
| GAIA validation samples | 3,500 global samples | not distributed | — | — | — | not distributed |
| GHSL | Global Human Settlement Layer built-up surface | — | — | — | **Rejected**: no layer consistent with 2018, so it cannot answer the analysis year | rejected |
| Natural-gas-vehicle supplementary table | Per-vehicle measurements behind the 90-percent-above-limits finding | supplementary material to Da Pan et al. (2020) | article licence | 2015–2019 | The urban attribution `ERRATA.md` 5.3 discusses | unverified |
| YRD gas leakage estimate | Ethane-tracer inversion of natural gas leakage in this region's cities | paywalled; abstract not indexed | — | 2012 to 2021 | Would quantify the urban source the thesis attributes; **its figures could not be verified and are not used** | unverified |

## Reference data and method

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| Landsat Collection 2 Level-2 | Surface-reflectance scenes at 30 m | Planetary Computer STAC API, `collections/landsat-c2-l2`, **HTTP 200 anonymously with no key** | The collection's `license` field reads `proprietary`, which is the STAC convention for "see the link"; its licence **link** is titled *Public Domain* and points at the USGS data policy. Cite `10.5066/P9IAXOVV`, `10.5066/P9C7I13B` or `10.5066/P9OGBGM6` by sensor | 1982-08-22 onward | Reimplementing the thesis's per-pixel proxy method from imagery rather than from a product, which is the only route to a reproduction that does not inherit a product's errors | **verified accessible** |
| Very-high-resolution imagery for visual interpretation | The standard response design in this literature | — | **An open question, not an assumption.** Every product here interpreted Google Earth imagery; none of the papers read addresses whether its terms permit publishing a derived accuracy assessment | — | Constructing reference data where none is distributed | unresolved |
| Olofsson et al. (2014) | The good-practice standard for area estimation and accuracy assessment | in the register | — | — | The standard a reviewer will check against. **Its first three recommendations apply here and are unmet; its last two do not apply at all**, because it contains no treatment of fractional cover | in the register |
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
| **IMI 2.0** | Open-access cloud tool giving sector-resolved methane emissions at up to 0.25° × 0.3125° by analytical inversion of TROPOMI with closed-form error characterisation — the same resolution as this project's lattice, and it ingests the blended TROPOMI+GOSAT field already committed here | Three documented routes: the free IMI product on the AWS Marketplace, the source from GitHub for a local cluster, and the Integral Earth web interface | open access; the paper is CC-BY | TROPOMI record from 2018, with the blended dataset kept current on AWS | **The preview answers, for free, whether TROPOMI can constrain emissions over this domain** — the question the flux-divergence gate could not answer. "The IMI Preview has no significant costs, and we strongly recommend using it." It reports expected DOFS, the dollar cost of a full run, and SWIR albedo as an artefact indicator | documented only |
| GRPI emission factors | The global compilation of 2,301 rice paddy field measurements behind a generalised additive model of growing-season emission factors, as a function of soil texture, pre-season water status, water regime, planting method, cultivar, organic amendment and climate zone | deposit route not established; the paper is paywalled | unknown | global, by country | **The function that turns a rice map into an emission estimate.** Every predictor in the model is a mechanism `notes/grounding-yrd.md` already identifies | unverified |
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
| Underground wastewater treatment plants | A dataset of the distribution and characterisation of underground wastewater treatment plants in China, with spatial distribution, process and discharge standards; underground plants are noted as preferring southeastern coastal locations, which is this domain | Scientific Data record, `10.1038/s41597-024-03815-x` | article licence, deposit terms not checked | published 2024 | Facility coordinates for one of the three population-allocated sectors, in the region where they concentrate. **The premise carried into this entry said 201 underground and 2,464 aboveground plants; the record's title names underground plants only** and the aboveground count is unverified | documented only |
| MSW landfill site database | Site-specific information for more than 300 major municipal solid waste landfills in China, with emissions by IPCC first-order decay from 1.015 Mt in 2005 to a peak of 2.161 Mt around 2015 and 1.98 Mt in 2023, compared against hyperspectral satellite observations at three sites | no deposit named in the paper, `10.1016/j.jenvman.2026.128672` | unknown | 2005–2023 | **The highest-value urban candidate.** Facility coordinates for the sector that dominates urban methane and that the separability finding says is the only one quantifiable. Whether the database is distributed is the thing to establish | unverified |
| China oil and gas CH4 database | Methane emissions from China's oil and gas systems 1990–2022, about sevenfold growth from 0.5 to 4.0 Tg per year, with 80 percent of emissions tracked as refineries, facilities, pipelines and field sources, and city-level distribution pipeline lengths | Nature Communications, `10.1038/s41467-025-58237-z`; deposit route not established | article licence | 1990–2022, annual | City totals for gas distribution, which is the sector whose published global product is faulted for allocating "only based on population densities without using an urban land cover map". **That named deficiency is what this project's impervious layer is.** The claim that pipeline lengths cover 347 prefecture-level cities is unverified | documented only |
| GHGSat global waste survey | 1,447 clear-sky observations from GHGSat C1–C5 of 151 waste disposal sites across 130 urban areas in 47 countries over six continents, 2021–2022, totalling 2.8 Mt CH4 per year | Nature, `10.1038/s41586-025-09683-8` | article licence | 2021–2022 | Point-source quantification of the dominant sector. It includes an example plume from a wastewater treatment plant near Shanghai, **which was filtered from the analysis** and so is an illustration rather than a quantified emission. TROPOMI plumes were detected for 46 of the 130 urban areas | documented only |

## Coal, building form and in-domain observation, added 13 September 2026

The coal entry exists because four grounding passes missed the sector entirely;
[`notes/grounding-yrd.md`](grounding-yrd.md) now records it. The building-form
entries exist because the urban record identifies vertical information as the
dimension an impervious fraction lacks. The last two are in-domain observations
and are the first entries in this file that are neither products nor
inventories.

| Candidate | What it is | Route | Licence | Coverage | What it serves | Status |
|---|---|---|---|---|---|---|
| Gridded Chinese coal mine methane | Bottom-up inventory at **0.25 by 0.25 degrees — this project's own resolution** — from a public database of more than 10,000 mines for 2011, which is 25 times more than EDGAR v4.2 and 2.5 times more than v4.3.2, with provincial emission factors. It finds provincial contributions differing significantly from EDGAR's, and names Anhui as the largest eastern emitter | No deposit reached. The paper is paywalled; the publisher's page and an institutional repository copy both refused, and no data availability statement was read | unknown | 2011, annual | **The prior for the one major source in this domain that neither predictor represents.** Whether it is distributed is the thing to establish, and it is the single question that would most change an inversion prior for northern Anhui | unverified |
| 30 m annual building height, China | Building height at 30 m, **annual from 1990 to 2019**, so it contains 2000, 2010 and 2018 — which no other height product does | ESSD article `10.5194/essd-18-5329-2026`; deposit route not established | article is CC-BY; deposit terms not checked | 1990–2019, annual, 30 m | The vertical dimension the Shanghai underestimate names as missing. **Adopt with a second product or not at all**, per the GAIA–GISA lesson | documented only |
| CMAB | National multi-attribute building dataset at building-instance level, carrying function among its attributes | *Scientific Data* `10.1038/s41597-025-04730-5`; deposit route not established | unknown | one epoch | **Building function, which is closer to the gas-and-waste mechanism than either footprint or height.** It would separate residential from industrial without inferring it from volume | documented only |
| Shaoxing UAV methane record | A portable CH4 detector on unmanned aerial vehicles and electric bicycles, observing vertical and spatiotemporal CH4 distribution over Shaoxing from April 2022 to February 2023, estimating annual emissions near 69 t km⁻² yr⁻¹ and describing that as higher than other cities worldwide | *Journal of Environmental Sciences* `10.1016/j.jes.2024.03.045`; no deposit named | unknown | April 2022 to February 2023 | **In-domain city-scale methane observation in Zhejiang**, and the only one in this file that measures methane in a city inside the lattice. Its period does not overlap 2018 | unverified |
| Shanghai urban canopy layer GHG site | Nearly two years of continuous high-precision in-situ measurement from the 632 m Shanghai Tower at 121.51 E, 31.23 N, April 2021 to March 2023, by cavity ring-down spectrometer | *Atmospheric Chemistry and Physics* `10.5194/acp-26-5477-2026`; no deposit named | unknown | April 2021 to March 2023 | **It measures CO2 and CO, not methane**, which is why it is recorded rather than pursued. It is noted because the site, the instrument and the tower exist inside the lattice, and a methane channel on the same platform would be the in-domain urban observation this project lacks | unverified |

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

## What this file is for

Each layer pass verifies its own candidates rather than there being a standalone
verification task, so this is a checklist whose statuses change as work
proceeds. Three properties make it worth keeping as a file rather than as a
conversation: it separates what was tried from what was read, it records the
licence beside the route so that a constraint is met before work depends on it,
and it records rejections and their reasons so a candidate is not reconsidered
from scratch.
