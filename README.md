# Urban expansion, paddy rice and atmospheric methane over the Yangtze River Delta

This repository holds a 2023 Yale School of the Environment MESc thesis and a
2026 reproduction of it. The thesis asked whether urban boundaries and paddy
rice extent over China's Yangtze River Delta could explain observed atmospheric
methane, and concluded that paddy rice was the dominant driver. The
reproduction rebuilds that question from the source data with a working
pipeline and does not reach the same conclusion.

The thesis itself is unchanged and preserved as submitted. It was never
published or submitted for publication. What is new here is the pipeline, the
reproduced data, an audit of the original document in [`ERRATA.md`](ERRATA.md) —
an *errata* being the list of a document's errors published alongside it, which
is what that file is and why nothing in the thesis was edited to match it — and
a reasoning record in [`notes/decisions.md`](notes/decisions.md).

## What the reproduction found

Land cover does not explain the methane field over the Yangtze River Delta at
0.25 degrees in 2018.

The test is whether a land-cover model beats a spatial null that predicts each
cell from the mean of its eight neighbours, excluding itself. That bar matters
because the methane field is smooth, and a model that only reproduces smoothness
has learned nothing about the surface. Under inverse-variance weighting no
land-cover model clears it anywhere: not on the raw retrieval, the operationally
corrected one or the seasonally corrected field, at either sample size, under
either cross-validation scheme. On the full 926<!--#composite.covered_cells--> cells held out by spatial
blocks, none clears it at either weighting: impervious fraction reaches held-out
R squared 0.095 against the spatial null's 0.337 on the seasonally corrected
field, and 0.085 against 0.346 on the operationally corrected composite. The
exceptions are all unweighted and all small, between 1.7 and 6.0 percent, and
they appear in the same places on every methane field and every predictor pair,
which is what makes them look like properties of the unweighted comparison
rather than of land cover.

The 2023 thesis identified paddy rice fields as the dominant driver of the
methane hotspots. The reanalysis does not support that. Rice fraction's
coefficient is +8.83 ppb per unit fraction counting cells equally and -3.20
weighting them by how well each was observed, and once wind is included it is
negative under both weightings. Its association with methane survives control
for surface albedo on no methane field at either weighting: the partial
correlations are -0.010, -0.065, +0.033 and -0.021, none of them distinguishable
from zero. A coefficient that changes sign when observations are weighted by
their own precision is not evidence of a relationship.

The one positive land-cover result is urban expansion, and its magnitude does
not reproduce. The thesis reports the four-province impervious total rising from
8,297<!--#urban.thesis_2000--> km² in 2000 to
49,725<!--#urban.thesis_2018--> km² in 2018, a factor of
6.0<!--#urban.thesis_factor-->. Recomputed from the current release of the same
product, GAIA gives 16,387<!--#urban.gaia_2000--> and
49,348<!--#urban.gaia_2018-->, a factor of 3.0<!--#urban.gaia_factor-->; GISA
gives 19,787<!--#urban.gisa_2000--> and 39,532<!--#urban.gisa_2018-->, a factor
of 2.0<!--#urban.gisa_factor-->. The 2018 extent reproduces to within 0.8
percent against the same product and the 2000 extent comes back at 1.98 times
the reported value, which is what a year-of-change product does when it is
reprocessed: the reconstruction moves at the historical end, where the satellite
record is sparsest, and holds at the recent one. Every account agrees the growth
was substantial and none of them agrees on how much. `ERRATA.md` 7.5 records it
and `figures/urban_change.png` draws it.

## Why the finding is not an artefact of measurement error

This is the objection a negative result has to answer, and answering it is the
reason the study can state one at all.

Contamination of the target biases an association in an unknown direction, so it
could as easily be hiding a relationship as inventing one. Measurement error in a
predictor does something specific: it attenuates the association toward zero. So
predictor error, and only predictor error, is the failure mode that could
manufacture this result out of nothing, and both predictors carry documented
error. GAIA is reported to omit impervious surface relative to GISA, with a
producer's accuracy worse by 28.35 percent, in the paper describing the second
version of GISA (Huang et al., 2022, doi:10.1016/j.jag.2022.102787) — though our
own regional measurement runs the other way, with GISA finding about 20 percent
*less*
impervious surface than GAIA in 2018, in every province. That comparison holds
for the analysis year and not for the record: in 2000 GISA finds 20.7 percent
*more*, so the two products cross over and disagree about the history rather
than about the extent. The NESDC
rice rasters have pinned provincial totals, an unclassified region in northern
and western Anhui, and no declared nodata.

**And the objection is now answered by measurement rather than only by
construction.** Treating GISA as a second measurement of the same quantity
bounds how much error the GAIA fraction can carry: the two disagree by 13.2
percent of the predictor's variance, so the reliability ratio is at least 0.868
and measurement error can be deflating the coefficient by at most a factor of
1.15. That lifts the best impervious held-out R² from +0.085 to +0.098 against
the spatial null's +0.332. **For measurement error to close that gap, 74.5
percent of the variance in the impervious fraction would have to be error — 5.6
times what the two products' disagreement supports.**

The answer also had to be second products with different errors, so four
predictor pairs were built and the whole baseline suite run over each: GAIA or GISA for
impervious surface, NESDC or GloRice for rice. **Zero cases beat the spatial null
under inverse-variance weighting**, across all four pairs, both cross-validation
schemes and both sample sizes, out of 176 weighted opportunities. The two urban
products agree at Pearson +0.938 and Spearman +0.956 across all 926 cells, so
that test is a weak one in that GISA had little room to disagree. The two rice
products agree only at +0.579 and +0.654, so that test is a real one, and it
gives the same answer.

One result from that comparison is uninterpretable rather than null and should
not be read as support for rice. GloRice's raw correlation with methane is
+0.397 against the NESDC classification's +0.096, and its partial correlation
given albedo survives where NESDC's does not. Four things confound it: it runs on
926 cells against 531<!--#grid.rice_rows-->, it allocates official statistics through a model rather
than observing rice, it correlates with impervious fraction at Spearman +0.560 so
it partly measures developed land in general, and its NaN means no rice while the
NESDC blank means not assessed, so the 395 extra cells are precisely the ones
NESDC declined to assess and 368 of them lie entirely outside the four provinces.
A predictor that is zero across one coherent region and positive across another
will correlate with anything else that differs between them.

## What the reanalysis does not establish

That is the strong claim and it is defensible. Everything else the reproduction
turned up is provisional, and it points the same way: no positive association in
this data is attributable to anything in particular.

Surface albedo is the first reason. TROPOMI retrieves methane from reflected
light and fails preferentially over dark ground, and albedo is more strongly
associated with the methane field than either land-cover fraction is. Impervious
fraction and albedo are collinear at Spearman +0.761, and with albedo partialled
out the impervious association falls from Pearson +0.345 to +0.021, which is
indistinguishable from zero. That does not prove the land-cover signal is an
artefact, because cities really are bright and controlling for albedo removes
real urban variation too; it establishes that the data cannot separate the two.
None of it is a discovery either. The dependence is a documented property of the
retrieval and the operational product ships an a posteriori correction for it
(Lorente et al., 2021, Atmospheric Measurement Techniques 14, 665-684,
doi:10.5194/amt-14-665-2021), which this composite carries and which does not
remove it: the corrected variable retains a slope of
199.8 ± 6.7 ppb per unit albedo at R squared 0.49, against 203.8 raw.

Sampling is the second and larger reason. Each cell's annual mean is taken over
whichever days happened to be observed there, and those days differ
systematically: per-cell mean day of year runs from 124 to 352, a range of 228
days, against a seasonal swing more than twice the spatial spread of the field
being analysed. A variable encoding nothing but when each cell was observed
reaches held-out R squared 0.426 on the seasonally corrected field and 0.467 on
the composite, beating the spatial null on both. Fitting a shared seasonal cycle
at the sounding level and removing it, which is what [`src/methane/seasonal.py`](src/methane/seasonal.py)
does in a single streaming pass, removed 20.6 percent of the between-cell
variance and left every association where it was. The residual appears to be
day-specific rather than seasonal: cells sampled on few dates inherit those
overpasses' synoptic conditions, which no function of day-of-year can reach.
Two competing explanations were ruled out and that one was not, which is weaker
than having confirmed it.

The consequence is that the wind result, which looks like the reproduction's
best model at held-out R squared 0.650, is uninterpretable. It cannot be
separated from sampling season.

The pipeline also omits preprocessing the literature applies. It does not
destripe the across-track bias, does not clear cloud beyond the quality filter,
does not separate the boundary layer from the free troposphere, and does not
work with departures from a model forecast. [`notes/decisions.md`](notes/decisions.md) lists each with
what it would take: the first two are reachable with what is already read, the
second two need external reanalysis or a transport model.

The last is gated rather than abandoned. Subtracting the TM5 a priori that ships
inside every granule would remove background, season and synoptic structure at
once, and one granule established the prior is coarse enough to subtract safely:
its half-sill range is 117.4 km against a 27.8 km cell, contributing 1.4 percent
of the variation at cell scale. It was not pursued because the departure
inherits the albedo bias intact while removing only 3.5 percent of the variance,
which makes that problem worse as a share of what remains, and because one
granule holds no seasonal or synoptic variation to test the thing the approach
is for. [`src/methane/apriori.py`](src/methane/apriori.py) is committed and tested but uncalled, so
resuming it is a configuration change rather than a rebuild.

None of this weakens the negative finding, and some of it strengthens it. A
confound large enough to carry the wind and albedo associations through a
seasonal correction still does nothing for land cover. And correcting a
retrieval bias that is correlated with the predictor would remove signal from
the land-cover association rather than add it, so the uncorrected bias is not
hiding a relationship that a cleaner field would reveal.

`notes/decisions.md` carries the argument for each of these in full, with the
measurements they rest on.

## What is here and what runs

The pipeline is complete for everything except the model, which the baselines
now argue against building. Three fetch modules sit over a shared core that
resumes partial downloads, writes atomically, and verifies a digest where the
source publishes one: figshare exposes `computed_md5` per file and Science Data
Bank a public Croissant export. A fourth route, GISA, uses that core directly
rather than through a module of its own, because its whole distribution is one
882 MB bundle whose 257 tiles carry no version, year or coordinate in any
filename, so the tiles covering the study box are found by reading each member's
georeferencing out of the archive without extracting it.

[`src/landcover/`](src/landcover/) computes zonal statistics over provincial polygons with the
constraints enforced by the types rather than by convention: a fraction divides
by the area a raster actually assessed and never by the zone, because the rice
rasters are clipped and dividing by the zone would understate rice exactly where
the clipping is. [`src/grid/`](src/grid/) joins those fractions onto the methane lattice by
integer arithmetic rather than by rasterising a thousand cell polygons, and
refuses to construct a row for a cell with no soundings, so the 97<!--#composite.uncovered_cells--> unobserved
cells are excluded by the type instead of by a filter someone can forget.

[`src/methane/`](src/methane/) reads Sentinel-5P Level 2 granules with auto-masking off,
applying each variable's own fill value and scale factor, and streams a full
year one granule at a time: the 2018 composite is 28.9 GB processed at a peak
working-directory size of one granule, checkpointed atomically. [`src/model/`](src/model/)
holds the baselines and the association tests, with leave-one-province-out and
spatial-block cross-validation, because cells are contiguous and a random split
leaks a cell's own neighbours into its training set.

There are 495 tests in the default run, and all of them work offline on a clone
with nothing fetched:

    python -m pytest

Eight more verify the regeneration recipes that need `data/raw/` or
`data/interim/`, both gitignored. They take about six minutes, mostly rebuilding
the analysis grid from 1.7 GB of rice rasters, so they are excluded by default
and skip themselves with a reason where the data is absent:

    python -m pytest -m slow

## Regenerating the results

Every committed table states its own provenance and cost in
[`data/processed/README.md`](data/processed/README.md), which is the place to look before running anything.
In outline:

<!-- BEGIN GENERATED RECIPE TABLE -->
| result | command | cost | verified |
|---|---|---|---|
| 2018 methane composite | `compute_methane_composite.py --checkpoint data/interim/extent_2018.npz --export data/processed/methane_composite_2018 --export-csv data/processed/methane_coverage_2018.csv` | 28.9 GB and about two hours to build the checkpoint; seconds to export from it | on demand |
| attenuation bound on the land-cover coefficient | `bound_attenuation.py --write` | about ten seconds | continuously |
| GAIA-GISA quantity and allocation disagreement | `decompose_urban_disagreement.py --write` | about ten seconds over two 992 by 1056 rasters | continuously |
| CCD-Rice validation polygon counts for the four provinces | `summarise_ccdrice_polygons.py --download` | a 1.9 MB download and a parquet read, a few seconds | on demand |
| composite coverage table | `compute_methane_composite.py --checkpoint data/interim/extent_2018.npz --export data/processed/methane_composite_2018 --export-csv data/processed/methane_coverage_2018.csv` | seconds from the checkpoint | on demand |
| covariate companion | `compute_methane_composite.py --checkpoint data/interim/extent_2018.npz --export-covariates data/processed/methane_covariates_2018` | seconds from the checkpoint | on demand |
| covariate table | `compute_methane_composite.py --checkpoint data/interim/extent_2018.npz --export-covariates data/processed/methane_covariates_2018` | seconds from the checkpoint | on demand |
| deseasonalised field | `compute_methane_composite.py --checkpoint data/interim/extent_2018.npz --export-deseasonalised data/processed/methane_deseasonalised_2018` | seconds from the checkpoint | on demand |
| deseasonalised table | `compute_methane_composite.py --checkpoint data/interim/extent_2018.npz --export-deseasonalised data/processed/methane_deseasonalised_2018` | seconds from the checkpoint | on demand |
| analysis grid | `build_analysis_grid.py --rice-source nesdc --write` | about 3 minutes over the local rice and urban rasters | on local |
| GISA impervious layer | `build_analysis_grid.py --urban-source gisa --impervious-only --write --out data/processed/impervious_gisa_2018.csv` | about 3 minutes over the local GISA rasters | on local |
| provincial urban areas | `compute_urban_areas.py --write` | about 20 seconds over the local GAIA tiles | on local |
| provincial rice areas | `compute_rice_areas.py --write` | a few seconds over the local GloRice files | on local |
| baselines | `run_baselines.py --covariates data/processed/methane_covariates_2018.csv --write` | under a second | continuously |
| baselines, deseasonalised | `run_baselines.py --target ch4_deseasonalised_ppb --target-from data/processed/methane_deseasonalised_2018.csv --covariates data/processed/methane_covariates_2018.csv --out data/processed/baseline_results_deseasonalised_2018.csv --write` | under a second | continuously |
| deseasonalisation test | `test_deseasonalisation.py --write` | under a second | continuously |
| expected inversion DOFS | `estimate_inversion_dofs.py --write` | about ten seconds | on local |
| albedo confounder test | `test_albedo_confounder.py --write` | under a second | continuously |
| buffered leave-one-out decay curve | `buffered_loo_curve.py --write` | about two seconds | continuously |
| residual autocorrelation ranges | `measure_residual_range.py --write` | about fifteen seconds | continuously |
| correlations corrected for spatial dependence | `correct_correlation_dof.py --write` | about twenty seconds | continuously |
| albedo correction test | `test_albedo_correction.py --write` | under a second | continuously |
| predictor robustness | `test_alternative_predictors.py --write` | a second, over four prebuilt grids | on local |
| predictor comparison | `test_alternative_predictors.py --write` | a second, over four prebuilt grids | on local |
| study area figure | `make_study_area_figure.py` | about a second | continuously |
| study area figure, vector | `make_study_area_figure.py` | about a second | continuously |
| coverage figure | `make_coverage_figure.py` | under a second | on local |
| coverage figure, vector | `make_coverage_figure.py` | under a second | on local |
| methane composite figure | `make_composite_figure.py` | about a second | continuously |
| methane composite figure, vector | `make_composite_figure.py` | about a second | continuously |
| urban extent grid, GAIA | `compute_urban_extent.py --write` | about a minute over 900 MB of gitignored impervious rasters | on local |
| urban extent grid, GISA | `compute_urban_extent.py --write` | about a minute over 900 MB of gitignored impervious rasters | on local |
| urban extent provincial totals | `compute_urban_extent.py --write` | about a minute over 900 MB of gitignored impervious rasters | on local |
| native window, GISA | `clip_landcover_window.py --write` | seconds, from gitignored raw rasters | on local |
| native window, GAIA | `clip_landcover_window.py --write` | seconds, from gitignored raw rasters | on local |
| native window, NESDC rice | `clip_landcover_window.py --write` | seconds, from gitignored raw rasters | on local |
| native land cover figure | `make_landcover_figure.py` | about a second | continuously |
| native land cover figure, vector | `make_landcover_figure.py` | about a second | continuously |
| urban change figure | `make_urban_change_figure.py` | about a second | continuously |
| urban change figure, vector | `make_urban_change_figure.py` | about a second | continuously |
| rice extent grid | `compute_rice_extent.py --write` | about three minutes over 3.5 GB of gitignored rice rasters | on local |
| rice extent provincial totals | `compute_rice_extent.py --write` | about three minutes over 3.5 GB of gitignored rice rasters | on local |
| regional land cover figure | `make_landcover_regional_figure.py` | about a second | continuously |
| regional land cover figure, vector | `make_landcover_regional_figure.py` | about a second | continuously |
| held-out baseline predictions | `compute_baseline_predictions.py --write` | about ten seconds over the committed grid and covariates | continuously |
| buffered decay curve figure | `make_buffered_decay_figure.py` | about two seconds | continuously |
| buffered decay curve figure, vector | `make_buffered_decay_figure.py` | about two seconds | continuously |
| capability assessment figure | `make_capability_figure.py` | about two seconds | continuously |
| capability assessment figure, vector | `make_capability_figure.py` | about two seconds | continuously |
| observed against predicted figure | `make_observed_predicted_figure.py` | about two seconds | continuously |
| observed against predicted figure, vector | `make_observed_predicted_figure.py` | about two seconds | continuously |
| model field and residual figure | `make_residual_field_figure.py` | about eight seconds | continuously |
| model field and residual figure, vector | `make_residual_field_figure.py` | about eight seconds | continuously |
| pipeline framework figure | `make_framework_pipeline_figure.py` | about two seconds | continuously |
| pipeline framework figure, vector | `make_framework_pipeline_figure.py` | about two seconds | continuously |
| reproduction status framework figure | `make_framework_reproduction_figure.py` | about three seconds | continuously |
| reproduction status framework figure, vector | `make_framework_reproduction_figure.py` | about three seconds | continuously |
| albedo collinearity figure | `make_albedo_collinearity_figure.py` | about four seconds | continuously |
| albedo collinearity figure, vector | `make_albedo_collinearity_figure.py` | about four seconds | continuously |
| blended TROPOMI+GOSAT composite | `compute_blended_composite.py --write` | about seven minutes and 336 MB of transfer | on demand |
| blended composite, per-cell table | `compute_blended_composite.py --write` | about seven minutes and 336 MB of transfer | on demand |
| baselines on the blended field | `run_baselines.py --target ch4_blended_ppb --target-from data/processed/methane_blended_2018.csv --covariates data/processed/methane_covariates_2018.csv --out data/processed/baseline_results_blended_2018.csv --write` | about a minute | continuously |
<!-- END GENERATED RECIPE TABLE -->

The composite is the expensive one and it is the only one. It downloads,
grids and deletes each granule in turn, so it needs 28.9 GB of transfer but only
one granule of disk. The covariate and deseasonalised fields come from the same
pass; exporting them from an existing checkpoint costs nothing.

Two of these scripts compare against the committed values before writing and
refuse to overwrite a row that differs by more than a tenth of a percent:
`compute_urban_areas.py` and `compute_rice_areas.py`. The rest overwrite
whatever is there. This README previously said all of them did, which is how a
recipe that produced a different analysis grid went unnoticed for a month.

What checks the others is `config/recipes.yml`, which records every recipe as
data, and `tests/test_recipes.py`, which runs each one into a temporary
directory and compares the result against the committed file. The table above
is generated from that registry, so the command shown and the command tested
cannot differ. Regenerate it with `python scripts/verify_recipes.py
--update-readme`, and run the verification directly with `python
scripts/verify_recipes.py`.

The `verified` column says how each artefact is checked. `continuously` means
every input is committed and the recipe runs in the default test suite.
`on local` means it needs `data/raw/` or `data/interim/`, which are gitignored;
those run under `python -m pytest -m slow` where the data exists and skip with a
reason where it does not. `on demand` means the composite, which needs 28.9 GB
of transfer: its checksum is asserted, which catches a stale file but not a
drifted recipe, and `config/recipes.yml` records the date it was last verified
by actually running it.

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
differs only in that one, in 190 of 926<!--#grid.rows--> rows.

## The thesis and the errata

The thesis PDF is in [`writeup/`](writeup/), and [`ERRATA.md`](ERRATA.md) records what a 2026 audit found
in it. One item should be read before the thesis itself: Figure 4.7, captioned
as the model's predicted XCH4 boundaries for 2000 and 2010, is the same image as
Figure 4.5(a), the raw TROPOMI observations. All three placements resolve to a
single PDF object with byte-identical decoded pixels, and all three carry the
title "Raw TROPOMI XCH4 Concentrations (2018)" rendered into the image. Section
4.7 therefore contains no result, and the study's stated novel contribution is
not evidenced anywhere in the document. The notebook cell that would have
generated those predictions is preserved in [`Duyst_Thesis_Final.ipynb`](Duyst_Thesis_Final.ipynb) with its
runtime failure intact.

The errata also records that the thesis's causal attribution of methane hotspots
to paddy rice should be spatial-association language, that the reference data
Section 5.2 says does not exist has since been published and is now named in
ERRATA.md 5.1, and that the
reproduction has now tested the attribution directly and does not support it.

## Data sources

[`data/manifest.json`](data/manifest.json) carries the version, citation, retrieval date and file
digests for the four sources whose fetch scripts write to it. In brief:

| source | product | licence as recorded |
|---|---|---|
| GAIA | annual global artificial impervious area, 30 m, 1985–2021 | CC BY 4.0 |
| GloRice | gridded paddy rice annual distribution, 2017–2021 | not recorded |
| Sentinel-5P TROPOMI | Level 2 methane, RPRO stream, processor 020400 | Copernicus open and free data policy |
| Natural Earth | 10 m admin-1 provinces | public domain |
| Science Data Bank rice | classified single-season rice, 10 m, by province | not in the manifest |
| GISA | global impervious surface area, 30 m, 1972–2019 | not stated on the download page |
| NESDC rice | classified single and double season rice, 10 m | personal-use grant, not scripted |
| SPAM, GADM | rice area, provincial boundaries | not redistributed, see above |

Two sources publish no usable checksum. Every S3 ETag on the Sentinel-5P mirror
is a multipart tag, an MD5 of the part MD5s with an unpublished part size, so
verification there is structural: a granule must open as netCDF4 and hold a
PRODUCT group with the expected variables. GISA's bundle publishes no digest
either, so its sha256 was computed on first download and pinned in
[`config/sources.yml`](config/sources.yml), and a changed distribution stops the fetch.

Two gaps are worth naming. The Science Data Bank rice product has a fetch
module but its script does not write a manifest entry, so the product the
analysis grid is built from is not recorded there. And two entries carry no
licence field. The manifest is the right place for both and neither is fixed.

The GAIA archive is named for 2022 and its readme is headed Version 2022, but
the data stops at 2021; the manifest records that the name overstates the
coverage by one year.

## What this repository does not claim

Four of these were decided before any code was written, in
[`notes/repository-architecture.md`](notes/repository-architecture.md), and are carried forward unchanged.

It does not claim that the 2023 model results are reproduced: no checkpoint
exists and the stored outputs cannot be attributed to the committed code. It
does not claim that predicted XCH4 fields represent emissions; they would
represent a learned spatial association with land cover. It does not present the
2026 numbers as corrections to the 2023 numbers; they are a second computation
under documented conditions, reported alongside. And it does not report a
validation metric against a dataset measuring a different quantity.

To those the reproduction adds two more. It does not claim that any positive
association in this data is attributable. The urban association cannot be
separated from a surface-albedo retrieval bias, the wind association cannot be
separated from sampling season, and the composite's dominant axis of variation
is when each cell was observed rather than where it is. The negative result is
the only claim here that does not depend on resolving those, which is why it is
the only one stated without qualification.

And it does not claim that GloRice's stronger rice association is evidence for
rice. That result is confounded four ways, as set out above, and is
uninterpretable rather than positive or null.

## Layout

[`src/`](src/) holds the pipeline, one package per concern, with [`scripts/`](scripts/) as thin CLI
entry points over it and [`tests/`](tests/) mirroring both. One module,
[`src/methane/apriori.py`](src/methane/apriori.py), is committed and tested but called by nothing: it is
the gated departure work, kept so that resuming it costs a configuration change
rather than a rebuild. [`config/sources.yml`](config/sources.yml) carries
dataset versions, bounds, thresholds and the covariate list, each with the
reasoning that fixed it. [`data/processed/`](data/processed/) holds the small derived tables,
committed, with their own README; `data/raw/` and `data/interim/` are
gitignored. [`notes/`](notes/) holds the decision record and the architecture design.
[`writeup/`](writeup/) holds the thesis PDF. [`legacy/`](legacy/) holds the 2023 notebook outputs and
the ArcGIS figure exports, whose provenance is documented but which no code in
this repository produces.

[`figures/`](figures/) holds the generated figures, committed as a PDF and PNG pair each,
with their captions in [`figures/README_fragments.md`](figures/README_fragments.md). Thirteen of a planned sixteen
exist, inventoried in [`figures/README.md`](figures/README.md) against the 2023 thesis's own eighteen. Every colour any of them draws is a named role in
[`src/figures/style.py`](src/figures/style.py), checked once over the whole role set for greyscale and
colour-vision separation; a figure module may not name a colour, and a test
scans for it. The 2023 exports in [`legacy/figures/`](legacy/figures/) are not a substitute and are kept
only as a record of the original document.

One committed input carries an attribution obligation: the shaded relief in
[`data/reference/yrd_hillshade.tif`](data/reference/yrd_hillshade.tif) is derived from Copernicus DEM GLO-90,
whose licence requires a stated notice for adapted data and for redistribution.
Both notices are quoted verbatim in [`data/reference/README.md`](data/reference/README.md), in
[`data/manifest.json`](data/manifest.json), on the study area figure itself and in its caption.
Everything else in [`data/reference/`](data/reference/) is Natural Earth and public domain.

## Licence and citation

MIT, in [`LICENSE`](LICENSE), for the code. The thesis text and figures are the author's
own work and are not covered by it. [`CITATION.cff`](CITATION.cff) carries the citation metadata
for the repository; cite the thesis itself from [`writeup/`](writeup/).
