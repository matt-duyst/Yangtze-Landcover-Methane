# Methods

Draft for a paper. This file differs from the grounding records in kind: they
state what is known and why, this states what was done. It is written to be
read by someone who has never seen this repository, in the register a journal
methods section uses, and it makes no reference to the project's own history.
Numbers carry markers for [`scripts/verify_claims.py`](../scripts/verify_claims.py)
where a committed artefact holds them; the closing note lists the ones that do
not.

**The order follows the data rather than the argument.** The analysis lattice is
defined first because every later quantity is expressed per cell; then the column
observations and the composite that forms the target; then the predictors; then
the two analyses. The capability assessment comes last although the paper's
central claim rests on it, because it takes the preceding sections' outputs as
inputs and cannot be stated before them.

## 1. Study area and analysis lattice

The study area is the Yangtze River Delta region of eastern China, comprising
Shanghai municipality and the provinces of Jiangsu, Zhejiang and Anhui. Analysis
was carried out on a regular geographic lattice of 0.25° cells spanning 114.8°
to 122.55° east and 26.95° to 35.2° north, giving 31 columns by 33 rows and
1,023<!--#composite.total_cells--> cells in total. At 31.1° north, the centre of
the domain, one cell measures approximately 24 by 28 km.

The declared extent and the lattice coincide exactly. This is not automatic: a
lattice is built by rounding a declared extent to a whole number of cells, and
for a 7.75° by 8.25° box at 0.25° the rounding is exact only if the declared
bounds are themselves multiples of the cell size. The bounds above were chosen so
that they are, which makes the region a single object for both the column and the
land-cover processing paths rather than two definitions that differ at the edges
by a fraction of a cell.

The region is one of the more consequential places to pose this question.
Atmospheric inversion ensembles and process-based models coordinated through the
Global Carbon Project place approximately 60 % of China's national methane
emissions in three of nine sub-national regions — North, Southeast and Southwest
China — which together occupy under 30 % of the country's land area, with those
emissions dominated by the energy and agricultural sectors (Zhao et al., 2026).
The study area lies in Southeast China. Within it, paddy rice, municipal solid
waste, urban gas distribution and coal mining are all present, the last in the
Huainan–Huaibei coalfield of northern Anhui.

## 2. Satellite observations of atmospheric methane

### 2.1 Product and stream

Column-averaged dry-air methane mole fractions (XCH₄) were taken from the
Sentinel-5P TROPOMI Level 2 methane product (`L2__CH4___`), reprocessed stream
(RPRO), processor version 02.04.00. The Level 2 record for this product begins on
30 April 2018, so the 2018 analysis year is an eight-month year: no granules
exist for January through April, and the composite describes the days that exist
rather than the calendar year.

Every orbit is published more than once at different processor versions. For
2018 the archive listing returns 6,390 keys for 3,437 distinct orbits; only the
highest processor version of each orbit was retained, since gridding two
reconstructions of one overpass would count the same soundings twice and bias
each cell's mean toward whichever overpasses happen to be duplicated.

### 2.2 Granule candidacy

A granule filename encodes an orbit number and a UTC time window and carries no
geographic extent, so candidate granules were selected by orbital geometry rather
than by footprint. Sentinel-5P is sun-synchronous with a 13:30 local-time
descending node, which places the study area beneath the satellite at
approximately 05:19 to 05:50 UTC. That window, widened by 55 minutes to allow for
swath width and neighbouring orbits, selected 578<!--#composite.granules_gridded-->
of the 3,437 deduplicated granules. The filter is a superset and not an exact
test: whether a swath actually reached the domain is knowable only from a
granule's own latitude and longitude arrays, after download. Of the 578,
223<!--#composite.granules_with_data--> carried at least one in-domain sounding
and 355 carried none.

### 2.3 Quality filtering

Soundings were retained at `qa_value ≥ 0.75`. The product documentation
recommends 0.5. Over this domain and this processor version the two thresholds
select identical soundings, because `qa_value` is quantised to its top bin here;
the stricter threshold was therefore adopted as the stronger statement at no cost
in sample size. `qa_value` is stored as an unsigned byte with a scale factor of
0.01, so the comparison was made in stored units against 75. Fill values were
read from each variable's own `_FillValue` attribute rather than assumed.

The retained soundings number 110,920<!--#composite.soundings--> within the
domain.

### 2.4 Four methane fields, not one

Four column fields were carried through the analysis rather than one:

1. **The raw retrieval**, `methane_mixing_ratio`. Gridded and reported, but not
   used as a regression target.
2. **The operationally bias-corrected retrieval**,
   `methane_mixing_ratio_bias_corrected`, which is the product's own destriping-
   and albedo-corrected field. Over this domain it exceeds the raw field by a
   mean of 11.64<!--#composite.bias_mean--> ppb. This is the primary target.
3. **The blended TROPOMI+GOSAT product** of Balasus et al. (2023), in which a
   machine-learning correction trained against GOSAT removes the bulk of the
   operational product's artefacts. This field is restricted to `qa_value ≥ 0.5`
   by its authors, a restriction that costs nothing here for the reason given in
   §2.3. Its published improvements over the operational product are a
   single-retrieval precision of 11.9 against 14.5 ppb and a reduction in
   spatially variable bias against GOSAT from 14.3 to 10.4 ppb at 0.25 ×
   0.3125°.
4. **A deseasonalised field**, in which a region-wide seasonal cycle is removed
   *at the sounding level* rather than from the cell means. The cycle is fitted
   to every sounding individually as a fixed-effects model with one offset per
   cell and harmonic coefficients shared across the domain, in a single streaming
   pass. This is not the composite mean minus a cycle: once a cell mean exists,
   the information about which days contributed has been averaged away, and
   subtracting a cycle evaluated at the cell's mean sampling date does not
   recover it, because the mean of a nonlinear function is not the function of
   the mean. The field is accompanied by per-cell sampling-date diagnostics — mean
   day of year, its standard deviation, and a flag for cells whose sampling dates
   span under fifteen days — which state how far each value can be trusted.

**The full baseline suite of §5 was run independently against fields 2, 3 and
4**, giving three complete sets of 88 model-scheme-weighting results. Field 2 is
reported as the primary target and the other two as tests of whether the result
depends on the correction applied; the deseasonalised field specifically tests
whether the association is an artefact of uneven sampling through the year, since
sounding yield over this domain is strongly seasonal and runs against the rice
growing season.

Carrying four fields rather than one is a deliberate design choice and not
redundancy. The choice of retrieval is not neutral: assimilating three TROPOMI
methane products into one variational inversion over Europe for 2019 produced
emission budgets of +2 %, −1 % and −33 % relative to the same prior, with machine
learning attributing the differences principally to aerosol scattering and albedo
sensitivity (Sicsik-Paré et al., 2026). A result that holds on one retrieval and
not another is a statement about the retrieval.

### 2.5 Preprocessing steps not applied

Published TROPOMI inversion chains apply corrections this analysis does not, and
the omissions are stated here rather than deferred to a limitations section
because they characterise the field a reader is about to see results from.

* **No destriping was applied.** The operational destriping procedure was
  introduced for data from September 2024 onward and earlier orbits have not been
  reprocessed, so no official destriping exists for this processor version and
  year. Only a self-implemented correction would have been available.
* **No filter on retrieval precision** beyond the quality flag, and **no albedo
  floor**. Published chains variously require methane precision below 10 ppb, a
  shortwave-infrared aerosol optical thickness ceiling, and an albedo above a
  stated minimum.
* **No representativeness weighting.** Cells are weighted by sounding count where
  weighting is applied at all (§5.2), not by any measure of how representative
  their soundings are of the cell.

The blended product in §2.4 addresses albedo dependence, aerosol scattering and
across-track variability together, by construction rather than by filtering, and
it is the reason the first three omissions are partly mitigated rather than
simply absent. Every result reported on the blended field is therefore also a
test of whether the omissions matter.

**All four omissions have now been tested directly**, on quantities retained
during a re-run of the granule pass, and each is reported as a sensitivity
rather than adopted: the composite in §2.3 remains the primary field and
reproduces byte-identically after the re-run. `notes/decisions.md` records the
pass and `data/processed/preprocessing_sensitivity_2018.csv` holds the results,
six variants across seven models and all four cross-validation designs.

* **The precision filter is a no-op on this record.** Of the
  110,920<!--#quality.in_box_passed--> soundings that pass quality control,
  none has a retrieval precision above 10 ppb, so the published threshold would
  remove nothing. The quality flag already enforces it.
* **The albedo floor at 0.05 removes
  11,707<!--#sens.albedo_removed--> soundings and empties
  174<!--#sens.albedo_cells_lost--> of the 926 cells.** Compared on the
  752<!--#sens.albedo_cells--> cells that survive, no land-cover model
  overtakes the spatial null in any of the four designs.
* **Destriping is recoverable and was tested at first order.** The across-track
  detector column was retained during the re-run; the per-column offsets have a
  standard deviation of 5.09<!--#sens.stripe_sd--> ppb. Applying them raises
  every fit slightly and changes no ordering.
* **Representativeness weighting changes neither the result nor the
  benchmark.** It is close to orthogonal to sounding-count weighting,
  correlation -0.03<!--#sens.weight_correlation-->, because the spatial term
  carries 97.5<!--#sens.spatial_share_pct--> percent of the per-cell variance
  and does not shrink with the number of soundings — so it is a genuinely
  different weighting rather than a rescaling of the same one. Under it
  impervious cover rises from
  0.0244<!--#sens.impervious_committed_weighted--> to
  0.1429<!--#sens.impervious_repweight--> under spatial blocks, and the spatial
  null rises too, from 0.5137<!--#sens.null_committed_weighted--> to
  0.5399<!--#sens.null_repweight-->. **The ordering is unchanged and the gap
  barely moves.** No land-cover model overtakes the null under any weighting.

**One preprocessing step remains untested and it is not one of these four.**
The aerosol optical thickness ceilings the same published chain applies were
not retained, because they are separate variables rather than a threshold on
something already read.

## 3. Compositing

Soundings were accumulated into the lattice by a single streaming pass over the
granules, maintaining per-cell running sums and counts rather than retaining
individual soundings, so that memory is independent of record length and a run
can resume. Each sounding contributes to the cell containing its centre
coordinate; contributions are equal-weighted, so a cell's value is the arithmetic
mean of the soundings that fell in it.

The resulting composite covers 926<!--#composite.covered_cells--> of the
1,023<!--#composite.total_cells--> cells, or
90.52<!--#composite.coverage_percent--> %, leaving
97<!--#composite.uncovered_cells--> cells with no qualifying sounding in 2018.
Per-cell counts run from 1<!--#composite.min_soundings--> to
410<!--#composite.max_soundings--> with a median of
74<!--#composite.median_soundings-->.

Coverage is not missing at random. Of the 97 uncovered cells,
74<!--#composite.absent_on_land--> lie wholly on land, and their median elevation
is 502<!--#composite.absent_median_elevation--> m against
35<!--#composite.covered_median_elevation--> m for the covered cells;
50<!--#composite.absent_above_500m--> sit above 500 m against
24<!--#composite.covered_above_500m--> of the 926. The largest connected gap is
47<!--#composite.largest_absent_block--> cells over the mountains on the southern
edge of the domain. Coverage is also weak along the coast, where the median
sounding count is 6<!--#composite.coast_median_soundings--> against
133<!--#composite.land_median_soundings--> for cells that are wholly land.

**The composite is an annual mean per cell, and this is not the same object as an
inversion's observation vector.** An analytical inversion of TROPOMI methane uses
*super-observations*: the average of all individual soundings within one model
grid cell **and one satellite orbit**, a construction justified on the grounds
that information loss is negligible because the model values are identical for
all soundings being averaged and their averaging kernels are similar (Estrada et
al., 2025). Averaging within a cell and an orbit is therefore nearly free;
averaging within a cell and a *year* is not, because the model values are not
identical across a year and what is averaged away is the time variation an
inversion uses. The composite and a super-observation set are different objects
and neither can be derived from the other. The capability assessment in §6
accordingly works from per-granule cell sets rather than from the composite.

## 4. Land cover and covariates

### 4.1 Urban extent

Impervious surface was taken from two independent products, used throughout in
parallel rather than one being selected:

* **GAIA**, the Global Artificial Impervious Area dataset (Gong et al., 2020), at
  30 m.
* **GISA**, the Global Impervious Surface Area dataset (Huang et al., 2021), at
  30 m.

Both are *year-of-change* products: a pixel's value encodes the year in which it
became impervious, so an extent for a given year is obtained by thresholding, and
**the two encodings count in opposite directions.** GAIA counts downward, with
`year = 2023 − value`, so an extent through a target year selects values at or
*above* the code for that year. GISA counts upward from 1972, so the same extent
is a closed interval from 1 to the code for that year — not a one-sided threshold,
because 0 denotes absence and an upper-bound-only selector would count every
non-impervious pixel as impervious.

Both encodings were measured against the rasters rather than taken from the
documentation: GISA over 5,507,866,225 pixels and GAIA over 3,105,244,301.
Applying the wrong convention yields a plausible-looking map of the wrong thing.
For GISA in 2018 the correct selector returns 202,830,997 pixels where the
one-sided form returns 9,468,801, a map of what was built in 2018 and 2019 alone.
Neither product declares a nodata value; GAIA's is −128 and is undocumented.

The two products disagree, and the disagreement is structured. Over the four
provinces GISA gives 19,786.9<!--#urban.gisa_2000--> km² of impervious surface in
2000 against GAIA's 16,387.1<!--#urban.gaia_2000--> km², and
39,532.2<!--#urban.gisa_2018--> km² in 2018 against GAIA's
49,348.0<!--#urban.gaia_2018--> km². **GISA is therefore 20.7 % larger in 2000
and 19.9 % smaller in 2018**, so the products disagree about the growth factor far
more than about the extent: 2.0<!--#urban.gisa_factor--> against
3.0<!--#urban.gaia_factor--> over 2000 to 2018. Both are year-of-change products
whose release history redates transitions across the whole archive when
reprocessed, which moves the historical end of the series and leaves the recent
end alone. Historical figures from either product should not be read as
independent measurements of the same quantity.

### 4.2 Rice extent

Paddy rice was taken from two products:

* **A 30 m single-season rice product for China** covering 2017 onward,
  distributed through the National Ecosystem Science Data Center, carrying
  single-season and double-season classes per pixel.
* **GloRice (I)**, gridded annual paddy rice distribution at 5 arcmin for 1961 to
  2021 (Xie et al., 2025).

GloRice is *not* an independent observation of rice extent and is not treated as
one: its authors produce the annual maps by allocating national and sub-national
agricultural statistics to grid cells within each administrative unit, so its
totals match the statistical totals by construction.

Two limitations of the 30 m product bear directly on interpretation and are
reported with every result that uses it. **Anhui's rasters classify only the
86.11<!--#rice.anhui_coverage_percent--> % of the province that lies south of 33.3462° N
and east of 115.2682° E**, so the northern part of the province — which contains
the coalfield named in §1 — is unclassified rather than classified as
non-rice. And **Shanghai's and Jiangsu's provincial totals are pinned across
parts of the record**: Shanghai's single-season count is stable to 0.03 % across
2019 to 2025 while only 52.69 % of pixels labelled rice in 2019 are still so
labelled in 2025, a Jaccard index of 0.3577; between 2023 and 2024, 5,651,475
pixels gained the label and 5,651,551 lost it. A stable total over a relocating
classification is a property of the product, not of the landscape.

### 4.3 Aggregation to fractional cover

Both land-cover classes enter the analysis as per-cell fractions rather than as
categories. For each cell, the fraction is the assessed impervious or rice area
divided by the area actually assessed within that cell. Areas are measured in an
Albers Equal Area projection with standard parallels at 25° and 47° north and a
central meridian at 105° east, rather than by counting pixels, because pixel
count is not proportional to ground area across eight degrees of latitude. A
separate coverage column records what share of each cell was assessed, so that a
fraction is never formed against a denominator the product does not cover.

Across the 926 covered cells the median impervious fraction is
0.0595<!--#grid.impervious_median--> with
136<!--#grid.impervious_zeros--> cells at zero.
531<!--#grid.rice_rows--> cells carry a rice fraction, of which
18<!--#grid.rice_zero_rows--> are recorded zeros, with a median single-season
fraction of 0.1291<!--#grid.rice_single_median--> and a median combined
single-and-double fraction of 0.1366<!--#grid.rice_combined_median-->. Rice
coverage has a median of 0.3412<!--#grid.rice_coverage_median--> and falls below
0.99 in 569<!--#grid.rice_coverage_below_99--> cells, which is the quantitative
form of the Anhui limitation above. 69<!--#grid.straddling_cells--> cells
straddle a provincial boundary and carry a per-province share for each province
they intersect.

### 4.4 Covariates

Seven quantities carried by the retrieval itself were gridded onto the same
lattice by the same streaming accumulator, as per-cell means with independent
per-cell counts:

| Covariate | Role |
|---|---|
| Surface albedo, shortwave infrared | The retrieval's principal artefact axis; co-retrieved with XCH₄ |
| Surface albedo, near infrared | The second co-retrieved albedo band |
| Solar zenith angle | Light-path length; correlates with season and latitude |
| Surface altitude | Column length, and the axis along which coverage is missing |
| Surface pressure | Column mass, and the denominator of a dry-air mole fraction |
| Eastward wind at 10 m | Advective transport, the alternative explanation for a column gradient |
| Northward wind at 10 m | As above |

A covariate does not gate a sounding: a sounding with no valid covariate still
contributes its methane, so each covariate is valid on its own subset of the
record and carries its own count. Over this domain all seven are valid on all
110,920 soundings and cover all 926 cells.

The albedo covariates are not nuisance variables. TROPOMI's methane retrieval
uses a full-physics algorithm that retrieves XCH₄, surface albedo and atmospheric
scattering properties simultaneously from one spectrum (Sicsik-Paré et al.,
2026), so albedo is a co-retrieved parameter rather than an external
contaminant, and error in one is error in the other by construction. A
post-hoc regression against albedo can remove the linear, stationary part of that
coupling and cannot remove the rest. 166<!--#cov.albedo_negative--> cells carry a
negative annual-mean shortwave-infrared albedo, which is unphysical and is an
artefact indicator rather than a measurement.

## 5. Statistical analysis

### 5.1 Baseline suite

Land-cover predictors were evaluated against a suite of baselines rather than
against a null of no effect, so that any skill attributed to land cover is skill
above what geography alone supplies. The suite comprises: a global-mean constant;
a per-province constant; a spatial null, being the mean of each cell's eight
queen-adjacent neighbours; a latitude-longitude trend surface; wind components;
the albedo covariates; each land-cover fraction alone; the two fractions
together, with and without an interaction; and combinations of wind and trend
surface with the fractions. Twenty-two model specifications were fitted in total.

**No held-out figure in this work is reported without the scheme and weighting
it was produced under**, because the four combinations of two schemes and two
weightings give materially different answers for the same model: impervious
fraction on the primary field ranges over
0.247<!--#spread.impervious--> of R² across them. Where one figure is quoted it
is the spatial-blocks unweighted combination, which is the optimistic end of the
bracket for the reason §5.4 gives.

Under spatial blocks without weighting, on the operationally corrected field,
held-out R² is
0.0847<!--#baseline.impervious_r2--> for impervious fraction alone,
-0.0314<!--#baseline.rice_alone_r2--> for rice fraction alone and
0.0169<!--#baseline.rice_plus_impervious_r2--> for the two together, against
-0.0084<!--#baseline.constant_r2--> for a global-mean constant,
0.3324<!--#baseline.null_r2--> for the spatial null and
0.6527<!--#baseline.wind_r2--> for wind components. The observed field spans
106.1<!--#baseline.observed_span_ppb--> ppb between its extreme cells; the
impervious model's predictions span
42.7<!--#baseline.impervious_span_ppb--> ppb and its root mean squared error is
14.2<!--#baseline.impervious_rmse--> ppb.

### 5.2 Cross-validation and weighting

Two held-out schemes were used, each reported separately: **leave-one-province-out**,
in which each province in turn is withheld entirely, and **spatial blocks** of
one degree by one degree, giving blocks of
111.2<!--#range.block_ns_km--> km north-south by
95.0<!--#range.block_ew_km--> km east-west at this latitude. Each model was
fitted both unweighted and weighted by sounding count, giving 88 fitted
model-scheme-weighting combinations.

**Neither scheme buffers, and the spatial cross-validation literature's variants
do.** Buffered leave-one-out — withholding not only the test unit but every unit
within a stated radius of it — is the standard prescription where residual
autocorrelation extends beyond the test unit, and it was not applied. §5.4
measures what that omission costs.

### 5.3 Effective degrees of freedom

Both land-cover fractions and the methane field are strongly spatially
autocorrelated, so the nominal degrees of freedom of a correlation over 926 cells
overstate the information available and the nominal *p*-value is
anti-conservative. Moran's *I* of the methane field is
0.7085<!--#residual.observed_moran--> under a permutation test with
999<!--#residual.permutations--> permutations.

Significance was therefore corrected by the modified *t*-test of Clifford,
Richardson and Hémon (1989) as extended by Dutilleul et al. (1993), in which the
effective sample size is

    M = 1 + n² / tr(R_X R_Y),     tr(R_X R_Y) = ΣᵢΣⱼ ρ_X(d_ij) ρ_Y(d_ij)

with each field's spatial correlation ρ(d) estimated by binning pair distances
into 30 bins and taking the empirical correlation within each bin. Distances are
great-circle on cell centres, because the domain spans eight degrees of latitude
and a planar approximation would be wrong by several percent at the edges. The
effective sample size is capped at n + 1, since a noisy correlogram can otherwise
return a value that would make a corrected *p* smaller than the nominal one.
The correction adjusts the significance of a correlation and not its value.

Applied to the 72<!--#dof.rows--> correlations reported for this domain, the
correction reduces the effective sample size to between
0.0200<!--#dof.shrinkage_min--> and
0.2517<!--#dof.shrinkage_max--> of nominal — that is, to between
11.4<!--#dof.effective_n_min--> and
185.7<!--#dof.effective_n_max--> independent observations in place of 926 — and
27<!--#dof.verdict_changed--> of the 72 correlations that reach significance at
the 5 % level nominally do not reach it after correction. The estimator was
calibrated against synthetic fields: on independent white-noise fields it returns
between 0.75 and 1.0 of nominal, so a shrinkage near 0.87 is read as "no
dependence detected" rather than as a real loss, and on fields with a 150 km
correlation range it returns under 0.2.

### 5.4 Residual autocorrelation and the buffered decay curve

Whether a cross-validation block is wide enough is decidable from the range at
which model residuals decorrelate. Exponential semivariograms of the form
γ(h) = nugget + (sill − nugget)(1 − exp(−h/a)) were fitted to the residuals of
each model on each field, and the half-sill range — the separation at which the
semivariogram reaches half its sill — was taken as the comparable definition,
because the conventional practical range is not identified for several of these
fits.

Of the 10<!--#range.models--> model-field combinations,
4<!--#range.too_small--> have residuals still correlated at the block width. The
impervious model's residual half-sill range is
96.1<!--#range.operational_impervious_km--> km on the operationally corrected
field and 134.5<!--#range.blended_impervious_km--> km on the blended field,
against a block 95.0 km at its narrowest; models that include the albedo
covariates decorrelate well inside a block, at
22.5<!--#range.operational_full_km--> km or less. **So the block scheme is too
small for the land-cover models and ample for the covariate models**, and a
single block size cannot be right for both.

To bound what the absence of buffering costs, held-out R² was recomputed with
each cell withheld together with every cell within a radius r of it, for r from 0
to 500 km. Because a constant predictor's held-out skill also falls as r grows —
the training mean drifts away from the withheld cell's neighbourhood — skill is
reported as the difference from a constant fitted on the same training set. The
spatial null's skill above a constant falls from
0.687<!--#loo.null_0km--> at r = 0 to
0.000<!--#loo.null_50km--> at r = 50 km, which is the expected collapse for a
predictor that has nothing but neighbours. The impervious model's falls from
0.118<!--#loo.impervious_0km--> at r = 0 to
0.089<!--#loo.impervious_100km--> at 100 km and
0.007<!--#loo.impervious_300km--> at 300 km.

**The curve indicates that the two cross-validation schemes bracket rather than
disagree.** Leave-one-province-out is the more pessimistic scheme and the 1° block
the more optimistic, and the decay curve places the land-cover model's skill
between them at the radii those schemes correspond to. The two schemes were
reported separately throughout for this reason, rather than one being preferred.

## 6. Capability assessment of the observing system

This section is the analysis rather than a preliminary to it. It asks what the
observing record can constrain, independently of what any predictor explains, and
it produces two limits.

### 6.1 Information content

Expected degrees of freedom for signal (DOFS) were computed from the closed-form
estimate published for the Integrated Methane Inversion's preview facility
(Estrada et al., 2025), which gives a per-cell averaging-kernel sensitivity

    a = s_A² / (s_A² + (s_super/k)²/m_super),     k = α M_air L g / (M_CH4 U p)

and DOFS = Σᵢ aᵢ, evaluated with that tool's published defaults: prior error
0.5, observation error 15 ppb, length scale 25 km, α = 0.4, wind speed 5 km h⁻¹,
retrieval error correlation 0.55 and transport error 4.5 ppb.

The two observation inputs were derived from the granule record rather than from
the composite, for the reason given in §3. Per-cell **observation days**,
m_super, were counted as the number of distinct days on which a cell received at
least one qualifying sounding, giving a median of
23.0<!--#dofs.days_median--> days per covered cell; the number of retrievals
per super-observation has a median of
4.4<!--#dofs.retrievals_median-->.

Sensitivity depends on the prior emission magnitude, which is not known for this
domain to better than a factor of two, so DOFS was evaluated across the range the
literature supports. Expected DOFS is
1.44<!--#dofs.at_3tg--> at a 3 Tg a⁻¹ domain prior,
3.98<!--#dofs.at_5tg--> at 5 Tg a⁻¹ and
22.21<!--#dofs.at_12tg--> at 12 Tg a⁻¹.

**Two qualifications travel with those figures and neither is optional.**

First, **no cell reaches an averaging-kernel sensitivity above 0.5 at any point in
the sweep** — the count is 0<!--#dofs.cells_above_half--> in every case. The DOFS
total accumulates from 926 weakly constrained cells rather than from a few well
constrained ones. That is the profile a domain-total estimate needs and not the
profile a per-cell attribution needs: a regional total is constrainable by this
record and a cell-level attribution is not. The operational literature treats
DOFS above 0.5 as a practical minimum for estimating a total with a 2σ error of
30 % or less, and reports that low-DOFS inversions are mainly constrained by the
prior rather than by the observations.

Second, **this is a reimplementation of the published estimate evaluated over
this lattice, not an inversion.** No transport model was run, no Jacobian was
constructed and no emissions were optimised. The estimate is the tool's own
closed-form approximation with the tool's own defaults and this domain's
observation counts, and the figure that would settle the question is a preview run
of the tool itself.

### 6.2 Identifiability

Information content bounds how much can be recovered. It does not bound whether
what is recovered can be attributed to a sector, and for this domain the second
limit is the binding one.

**Sectoral attribution in an inversion derives from the spatial distinctness of
the prior rather than from the observations.** The evidence is a contrast within a
single published inversion. Where a sector's prior is allocated on facility
coordinates and is therefore spatially distinct from every other sector — as
landfills are in the US gridded greenhouse gas inventory — posterior error
correlations with other sectors fall below 0.35, and the sector's emissions can be
quantified. Where sectors' priors are allocated on a common population surface —
as downstream gas, wastewater treatment and stationary combustion are — posterior
error correlations among them run from 0.45 to 0.87, and their separation is, in
that study's own words, limited and heavily weighted by the prior (Wang et al.,
2026). The same instrument, the same inversion and the same domain separate one
sector and fail to separate three; the only thing that differs is how each
sector's prior was spatially distributed.

**The sources in this domain are interspersed in every direction.** Paddy rice
and freshwater aquaculture occupy the same flooded lowland and are spectrally
similar; rice and natural wetland overlap in the wetland priors by those
products' own account; four urban sectors share one population-like allocation
surface within the same city cells; and coal mining in northern Anhui sits
adjacent to, and partly inside, the cells where the rice classification stops
(§4.2). The methodological literature states the consequence directly: inversion
modelling is not capable of distinguishing interspersed sources from different
sectors, and overlapping grid-level sources from different sectors are typically
grouped and treated as a single source (Desjardins et al., 2018).

**The two limits are independent, and that is the point.** Additional
observations raise the information content and leave the identifiability
untouched, because they do not make a prior more spatially distinct. A better
prior sharpens attribution and adds no information the observations do not carry.
Either limit alone establishes that emissions in this domain cannot be
attributed to land cover cell by cell from this record; together they establish
that no refinement of the same design would change that.

### 6.3 Relation to the association analysis

The association analysis of §5 is the empirical counterpart of §6.1 rather than a
separate result. A record whose DOFS accumulates from uniformly weak per-cell
sensitivity is a record in which per-cell predictors should fail, and §5 reports
that they do, on two urban products, two rice products, two cross-validation
schemes, two weightings and three target fields. The negative result is
evidence that the information-content limit binds in practice and not only in
arithmetic.

## 7. Validation

A comparison against ground-based column measurement was attempted and is
reported as a feasibility measurement rather than as a validation. The nearest
Total Carbon Column Observing Network station, Hefei, lies inside the domain and
its 2018 record is sparse: 2,767 retrievals on 44 days. Nine days in 2018 carry
both a TROPOMI overpass of the station's cell and TCCON data. **Nine coincident
days, without the a-priori profile alignment that a TCCON–satellite comparison
requires, cannot validate a field**, and no result in this work rests on that
comparison. It establishes that the comparison is possible and bounds how much of
it is available.

**No accuracy assessment of either land-cover product was performed, and this is
a methods statement rather than a limitation**, on the same reasoning that puts
the preprocessing omissions here: it is a property of what was done and of what
could be done, established by measurement, not a caveat appended to a result.

The assessment frame for a fractional layer is agreement of a continuous field —
mean deviation, mean absolute deviation and regression against a more accurate
reference fraction — rather than an error matrix, because the good-practice
standard for categorical area estimation contains no treatment of fractional
cover, which is the form both predictors take here (§4.3). That frame compares a
product against **complete-coverage** reference data and does not sample, so it
requires no sampling design. **What it requires is a reference layer over the
domain more accurate than the product, and no such layer exists.**

Four candidates were verified against the four provinces. The impervious layers
this work uses report an F-score of 0.954 (GISA) and 93.12 percent overall
accuracy (GISA-new). A 1 m national land-cover map of China reports 73.61
percent overall accuracy with a kappa of 0.6595, and splits impervious surface
across two classes. A 1 m impervious product for the Yangtze River Economic
Belt reports an impervious-class F1 of 75.53 with a recall of 61.76, is
super-resolved from 10 m imagery, and is deposited as seven example cities. A
submeter product over 42 cities reports 83.6 percent overall accuracy and covers
urban areas only. A 30 m product for 2020 and 2022 reports an impervious F1
above 0.93 and is the same resolution as the layers it would assess, so it is a
fourth product rather than a reference. **Every candidate is less accurate than
what it would validate, and each is 2020 or later against analysis years of
2000, 2010 and 2018.** So the absence is a property of the products available
over this region, not of effort.

What the layers' disagreement supports instead is a bound, and for the
impervious layer the bound is computed. The two products' difference is
decomposed into quantity and allocation components following the two-class
fractional specialisation of Pontius and Millones's decomposition, at the 868 m
grid on which both are committed and at the 0.25 degree lattice the association
consumes; allocation — the component that attenuates a coefficient — is about
half the disagreement at the lattice scale in every year.

**Treating the second product as a second measurement of the same quantity turns
that into an upper bound on the predictor's error variance, under the assumption
that the two products' errors are independent of each other.** The difference
variance is 13.2<!--#atten.var_share_pct--> % of the predictor's own variance,
so the reliability ratio is at least 0.868<!--#atten.lambda_min--> and the
de-attenuation factor is at most 1.15<!--#atten.factor_max-->. Results §3.4
reports what that does to the reported coefficients.

**Three assumptions are stated because two of them are violated.** Independence
of the two products' errors is not testable here and is questionable: both are
built from the Landsat archive by related algorithms. Homoscedasticity fails
measurably — the difference's standard deviation rises thirty-one-fold from the
lowest to the highest quartile of the fraction. Non-differentiality fails mildly,
the signed difference correlating at −0.118 with methane once the fraction is
controlled. Both failures act in the direction of more attenuation than the bound
allows, so the bound is reported alongside a sensitivity sweep over error
variances up to six times the observed disagreement rather than as a single
figure.

**The rice layer has no equivalent and the absence is structural rather than
pending.** A bound of this kind needs a second product whose errors are
independent of the first, and no independent second rice product exists: the only
candidate, CCD-Rice, took its training samples from the same NESDC map this work
uses. So no statement about the *size* of a rice effect is de-attenuated or
bounded. None of the capability statements of §6 depends on either.

## 8. Reproducibility

Every derived artefact is registered in a machine-readable recipe register giving
the command that produces it and the verification tier it belongs to.
70<!--#pipeline.recipes--> artefacts are registered across four tiers:
39<!--#pipeline.recipes_committed--> regenerate from a fresh clone with no
network and no local data and are verified on every test run;
21<!--#pipeline.recipes_local--> require local raw data and are verified where it
exists; 9<!--#pipeline.recipes_network--> require a network fetch and are verified
on demand; and the remainder are recorded as unregenerable, with the reason
stated per artefact.

Verification is executed rather than asserted: the register's runner invokes each
recipe with output redirected to a temporary path and compares the result byte for
byte against the committed artefact. Numeric claims in the prose carry inline
markers naming the artefact quantity they come from, and a test recomputes each
from the artefact and fails on disagreement, so a regenerated table cannot move
under a sentence that quotes it.

---

## Drafting notes, not part of the section

**Numbers without an artefact behind them.** The following appear above and carry
no marker, because no committed artefact holds them. They are the claims a
reviewer could not check against this repository and the ones most likely to go
stale.

* The lattice bounds, 114.8/122.55/26.95/35.2, and the 31 × 33 shape. Declared in
  `config/sources.yml` and asserted by `tests/test_study_extent.py`, but no
  resolver exposes them.
* The archive listing counts, 6,390 keys and 3,437 distinct orbits, and the
  05:19–05:50 UTC window with its 55-minute widening.
* The 355 empty granules, which is 578 − 223 and could be resolved.
* The qa threshold 0.75 and the recommended 0.5.
* The GISA selector counts, 9,468,801 against 202,830,997 pixels.
* The Anhui raster bounds 33.3462° N and 115.2682° E; the Shanghai pinning
  figures (0.03 %, 52.69 %, Jaccard 0.3577, 5,651,475 and 5,651,551 pixels).
* The 20.7 % and 19.9 % product differences, which are derivable from four marked
  figures but are not themselves resolved.
* The correlogram bin count, the n + 1 cap, and the white-noise calibration
  bounds 0.75–1.0 and 0.2.
* Every IMI default in §6.1, and the DOFS formula's constants.
* The Hefei TCCON counts, 2,767 retrievals on 44 days and nine coincident days.
* All figures attributed to the literature: the 60 %/30 % regional shares, the
  +2/−1/−33 % retrieval spread, the 0.35 and 0.45–0.87 posterior error
  correlations, and the 0.5 DOFS operational threshold.

**Twenty-four resolvers were added for this draft** — for the effective
degrees-of-freedom table, the residual range table, the buffered decay curve and
the DOFS sweep — because those four artefacts were committed with no way to quote
them from prose, and the capability section quotes all four.
