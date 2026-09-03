# Urban expansion, paddy rice and atmospheric methane over the Yangtze River Delta

This repository holds a 2023 Yale School of the Environment MESc thesis and a
2026 reproduction of it. The thesis asked whether urban boundaries and paddy
rice extent over China's Yangtze River Delta could explain observed atmospheric
methane, and concluded that paddy rice was the dominant driver. The
reproduction rebuilds that question from the source data with a working
pipeline and does not reach the same conclusion.

The thesis itself is unchanged and preserved as submitted. It was never
published or submitted for publication. What is new here is the pipeline, the
reproduced data, an audit of the original document in `ERRATA.md`, and a
reasoning record in `notes/decisions.md`.

## What the reproduction found

Land cover does not explain the methane field over the Yangtze River Delta at
0.25 degrees in 2018.

The test is whether a land-cover model beats a spatial null that predicts each
cell from the mean of its eight neighbours, excluding itself. That bar matters
because the methane field is smooth, and a model that only reproduces smoothness
has learned nothing about the surface. Under inverse-variance weighting no
land-cover model clears it anywhere: not on the raw retrieval, the operationally
corrected one or the seasonally corrected field, at either sample size, under
either cross-validation scheme. On the full 927 cells held out by spatial
blocks, none clears it at either weighting; impervious fraction reaches R
squared 0.096 against the spatial null's 0.343 on the corrected field. The
exceptions are all unweighted and all small: on the 532-cell subsample that has
a rice fraction, land-cover models edge past the null by 2 to 5 percent under
spatial blocks, and impervious fraction beats it by 2.9 percent under
leave-one-province-out on the raw retrieval. They appear in the same places on
all three methane fields, which is what makes them look like properties of the
unweighted comparison rather than of land cover. Rice does worse: its coefficient is +8.83 ppb per unit
fraction counting cells and -3.20 weighting them by how well each was observed,
and once wind is included it is negative under both weightings. A coefficient
that changes sign when cells are weighted by their own precision is not
evidence of a relationship.

That is the strong claim and it is defensible. Everything else the reproduction
turned up is provisional, and it points the same way: no positive association in
this data is attributable to anything in particular.

Surface albedo is the first reason. TROPOMI retrieves methane from reflected
light and fails preferentially over dark ground, and albedo is more strongly
associated with the methane field than either land-cover fraction is. Impervious
fraction and albedo are collinear at Spearman +0.761, and with albedo partialled
out the impervious association falls from Pearson +0.346 to +0.020, which is
indistinguishable from zero. This does not prove the land-cover signal is an
artefact, because cities really are bright and controlling for albedo removes
real urban variation too. It establishes that the data cannot separate the two.

None of that is a discovery. The albedo dependence is a documented property of
the retrieval and the operational product ships a correction for it, which this
composite already carries. The correction does not remove it: the corrected
variable retains a slope of 199.8 ± 6.7 ppb per unit albedo at R squared 0.49,
against 203.8 for the raw retrieval. That slope is an upper bound rather than a
measurement of instrument sensitivity, because a composite confounds albedo with
geography and season, but it is enough to say the composite carries an
albedo-correlated bias that nothing in this pipeline removes.

Sampling is the second and larger reason. Each cell's annual mean is taken over
whichever days happened to be observed there, and those days differ
systematically: per-cell mean day of year runs from 124 to 352, a range of 228
days, against a seasonal swing more than twice the spatial spread of the field
being analysed. A variable encoding nothing but when each cell was observed
reaches held-out R squared 0.426 and beats the spatial null. Fitting a shared
seasonal cycle at the sounding level and removing it, which is what
`src/methane/seasonal.py` does in a single streaming pass, removed 20.6 percent
of the between-cell variance and left every association essentially where it
was. The residual appears to be day-specific rather than seasonal: cells sampled
on few dates inherit those overpasses' synoptic conditions, which no function of
day-of-year can reach. Two competing explanations were ruled out and that one
was not, which is weaker than having confirmed it.

The consequence is that the wind result, which looks like the reproduction's
best model at held-out R squared 0.650, is uninterpretable. It cannot be
separated from sampling season. The negative land-cover result is the one
finding that survives all of this, and it is stronger for having done so: a
confound large enough to carry wind and albedo through a correction still does
nothing for land cover.

`notes/decisions.md` carries the argument for each of these in full, with the
measurements they rest on.

## What is here and what runs

The pipeline is complete for everything except the model, which the baselines
now argue against building. Three fetch modules sit over a shared core that
resumes partial downloads, writes atomically, and verifies a digest where the
source publishes one: figshare exposes `computed_md5` per file, Science Data
Bank exposes a public Croissant export, and the Sentinel-5P mirror publishes no
usable checksum at all, so verification there is structural instead and a
granule must open as netCDF4 with the expected group before it is accepted.

`src/landcover/` computes zonal statistics over provincial polygons with the
constraints enforced by the types rather than by convention: a fraction divides
by the area a raster actually assessed and never by the zone, because the rice
rasters are clipped and dividing by the zone would understate rice exactly where
the clipping is. `src/grid/` joins those fractions onto the methane lattice by
integer arithmetic rather than by rasterising a thousand cell polygons, and
refuses to construct a row for a cell with no soundings, so the 96 unobserved
cells are excluded by the type instead of by a filter someone can forget.

`src/methane/` reads Sentinel-5P Level 2 granules with auto-masking off,
applying each variable's own fill value and scale factor, and streams a full
year of them one at a time. The 2018 composite is 28.9 GB of granules processed
at a peak working-directory size of one granule, checkpointed atomically so a
crash costs a minute rather than an hour. `src/model/` holds the baselines and
the association tests: constant predictors, per-province constants, ordinary
least squares on the fractions and the covariates, the spatial null, and
leave-one-province-out and spatial-block cross-validation, because cells are
contiguous and a random split leaks a cell's own neighbours into its training
set.

There are 345 tests. All of them run offline on a clone with nothing fetched.

## Regenerating the results

Every committed table states its own provenance and cost in
`data/processed/README.md`, which is the place to look before running anything.
In outline:

| result | command | cost |
|---|---|---|
| provincial urban areas | `fetch_gaia.py --download` then `compute_urban_areas.py --write` | 265 MB, minutes |
| provincial rice areas | `fetch_glorice.py --download` then `compute_rice_areas.py --write` | 250 MB, minutes |
| 2018 methane composite | `compute_methane_composite.py --run --max-hours 3` | 28.9 GB, 61 to 66 minutes |
| analysis grid | `build_analysis_grid.py --rice-source scidb --write` | 1.7 GB rice download, minutes |
| baselines | `run_baselines.py --write` | seconds |
| albedo confounder test | `test_albedo_confounder.py --write` | seconds |
| deseasonalisation test | `test_deseasonalisation.py --write` | seconds |
| albedo correction test | `test_albedo_correction.py --write` | seconds |

The composite is the expensive one and it is the only one. It downloads,
grids and deletes each granule in turn, so it needs 28.9 GB of transfer but only
one granule of disk. The covariate and deseasonalised fields come from the same
pass; exporting them from an existing checkpoint costs nothing.

Each compute script compares against the committed values before writing and
refuses to overwrite a row that differs by more than a tenth of a percent, so
running one is a check as much as a regeneration.

## What cannot be regenerated

Three things, named here rather than left to be discovered.

Twelve of the 160 provincial urban rows use GADM 4.1 boundaries as a
sensitivity check against the Natural Earth boundaries used for the other 148.
GADM's licence forbids redistribution, so the boundary file cannot be committed
and those rows need a user-supplied copy. Eight of the 36 rice rows come from
SPAM, for which no fetch module exists; they are carried for completeness and
are not used in any analysis.

One column of the analysis grid, `rice_fraction_combined`, needs the National
Ecosystem Science Data Center rasters obtained over a personal-use FTP grant
that is deliberately not scripted. The cost is one column rather than the table:
for 2018 the anonymous Science Data Bank export is the same classification with
the double-season class folded into the background, verified identical to the
pixel, so `--rice-source scidb` reproduces every other column exactly and
differs only in that one, in 190 of 927 rows.

## The thesis and the errata

The thesis PDF is in `writeup/`, and `ERRATA.md` records what a 2026 audit found
in it. One item should be read before the thesis itself: Figure 4.7, captioned
as the model's predicted XCH4 boundaries for 2000 and 2010, is the same image as
Figure 4.5(a), the raw TROPOMI observations. All three placements resolve to a
single PDF object with byte-identical decoded pixels, and all three carry the
title "Raw TROPOMI XCH4 Concentrations (2018)" rendered into the image. Section
4.7 therefore contains no result, and the study's stated novel contribution is
not evidenced anywhere in the document. The notebook cell that would have
generated those predictions is preserved in `Duyst_Thesis_Final.ipynb` with its
runtime failure intact.

The errata also records that the thesis's causal attribution of methane hotspots
to paddy rice should be spatial-association language, that the reference data
Section 5.2 says does not exist has since been published, and that the
reproduction has now tested the attribution directly and does not support it.

## Data sources

`data/manifest.json` carries the version, citation, retrieval date and file
digests for the four sources whose fetch scripts write to it. In brief:

| source | product | licence as recorded |
|---|---|---|
| GAIA | annual global artificial impervious area, 30 m, 1985–2021 | CC BY 4.0 |
| GloRice | gridded paddy rice annual distribution, 2017–2021 | not recorded |
| Sentinel-5P TROPOMI | Level 2 methane, RPRO stream, processor 020400 | Copernicus open and free data policy |
| Natural Earth | 10 m admin-1 provinces | public domain |
| Science Data Bank rice | classified single-season rice, 10 m, by province | not in the manifest |
| SPAM, GADM | rice area, provincial boundaries | not redistributed, see above |

Two gaps are worth naming. The Science Data Bank rice product has a fetch
module but its script does not write a manifest entry, so the product the
analysis grid is built from is not recorded there. And two entries carry no
licence field. The manifest is the right place for both and neither is fixed.

The GAIA archive is named for 2022 and its readme is headed Version 2022, but
the data stops at 2021; the manifest records that the name overstates the
coverage by one year.

## What this repository does not claim

Four of these were decided before any code was written, in
`notes/repository-architecture.md`, and are carried forward unchanged.

It does not claim that the 2023 model results are reproduced. They cannot be: no
checkpoint exists and the stored outputs cannot be attributed to the committed
code. It does not claim that predicted XCH4 fields represent emissions; they
would represent a learned spatial association with land cover, and the
distinction is stated wherever a prediction appears. It does not present the
2026 numbers as corrections to the 2023 numbers; they are a second computation
under documented conditions, reported alongside. And it does not report a
validation metric against a dataset measuring a different quantity, so
comparisons against emission inventories are directional consistency checks and
are labelled as such.

To those the reproduction adds one more. It does not claim that any positive
association in this data is attributable. The urban association cannot be
separated from a surface-albedo retrieval bias, the wind association cannot be
separated from sampling season, and the composite's dominant axis of variation
is when each cell was observed rather than where it is. The negative result is
the only claim here that does not depend on resolving those, which is why it is
the only one stated without qualification.

## Layout

`src/` holds the pipeline, one package per concern, with `scripts/` as thin CLI
entry points over it and `tests/` mirroring both. `config/sources.yml` carries
dataset versions, bounds, thresholds and the covariate list, each with the
reasoning that fixed it. `data/processed/` holds the small derived tables,
committed, with their own README; `data/raw/` and `data/interim/` are
gitignored. `notes/` holds the decision record and the architecture design.
`writeup/` holds the thesis PDF. `legacy/` holds the 2023 notebook outputs and
the ArcGIS figure exports, whose provenance is documented but which no code in
this repository produces.

There is no `figures/` directory. Nothing has been generated from the reproduced
data yet, and the 2023 exports in `legacy/figures/` are not a substitute for it,
so the directory is absent rather than misleadingly empty.

## Licence and citation

MIT, in `LICENSE`, for the code. The thesis text and figures are the author's
own work and are not covered by it. `CITATION.cff` carries the citation metadata
for the repository; cite the thesis itself from `writeup/`.
