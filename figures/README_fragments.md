# Figure captions

Self-contained captions for the figures in this directory, in the form the
README uses. Each is written to be read without the surrounding text.

Figures are generated, not drawn by hand. Each is produced by a module under
`src/figures/` and written through the verified export path in
`src/figures/output.py`, which refuses to write anything below 300 dpi or
narrower than 8 cm. Regenerate with the script named under each caption.

---

### Coverage saturation and monthly yield, 2018

![Coverage saturation and monthly yield for the 2018 methane composite](coverage_saturation_2018.png)

**Coverage of the analysis grid is a union statistic, so it saturates with the
number of granules that return data, and a small sample measures its own size
rather than the year's coverage.** Thirty-six productive granules reach 71.5
percent of the 1,023 cells and the remaining 187 add only 19.1 points to finish
at 90.52<!--#composite.coverage_percent--> percent. Soundings also arrive unevenly through the year, and the
unevenness runs opposite to the growing season: October alone carries 30.82
percent of the year's 110,920<!--#composite.soundings--> in-box soundings, while June, July and August
together carry 14.51 percent from three times as many granules.

Panel (a) is the cumulative count of grid cells that have received at least one
qualifying sounding, against productive granules in the order the streaming
loop handled them. Of 578<!--#composite.granules_gridded--> granules acquired over the box, 223<!--#composite.granules_with_data--> returned a
qualifying sounding and 355 returned none; a granule that returned none cannot
have covered a cell, so it is not a point on the axis. The curve is one
ordering of those 223 rather than an expected saturation curve, since a
different order reaches the same endpoint by a different path. The marked
sample size is the granule count of the 2018 reconnaissance, which reported
56.11 percent coverage; that figure is not a point on this curve, because those
thirty-six granules were drawn one per alternate month across seven years and
only six of them fall in 2018. Panels (b) and (c) share a month axis and are
stacked rather than drawn on twin axes, so neither series can be made to look
larger than the other by a choice of limits. January through March are shaded
because the reprocessed 2018 stream begins on 30 April; no granule was acquired
over the box in those months, which is a different fact from a month that was
sampled and yielded nothing. April is a single granule and 273 soundings,
labelled because at this scale its bar is otherwise indistinguishable from the
shaded absence beside it. Per-granule yield runs from 148 soundings in July to
1,103 in October, a factor of 7.4, and the July minimum coincides with both the
monsoon cloud cover that defeats the retrieval and the flooded-paddy season the
study is about. Coverage is computed on the 0.25 degree grid of 33 by 31 cells;
qualifying soundings are those with `qa_value` at or above 0.75.

Regenerate with `python scripts/make_coverage_figure.py`.

---

### Study area and analysis grid

![The four Yangtze River Delta provinces on shaded relief, with a locator, a detail box showing the 0.25 degree analysis cells, and the neighbouring provinces named](study_area.png)

**The four provinces of the Yangtze River Delta region, on the terrain that
explains where the methane composite has no data.** The analysis grid is 33
rows by 31 columns, 1,023<!--#composite.total_cells--> cells at 0.25 degrees,
spanning 114.8 to 122.55 east and 26.95 to 35.2 north. Those are the bounds the
cells actually occupy, not the declared box of 114.8 to 122.6 and 27.0 to 35.2:
the cell count rounds down in longitude and up in latitude, so the grid stops
0.05 degrees short of the declared east edge and runs 0.05 degrees past the
declared south edge.

The main panel is shaded relief from Copernicus DEM GLO-90 at 90 m, drawn over
all land in the frame and then veiled outside the four study provinces and
tinted inside them, so the study region is separated by tone as well as by its
heavier boundary and survives a print with no colour. The five provinces that
share the frame are named in italic; each is every admin-1 unit intersecting
the drawn extent, not a chosen list. Marked places are the four provincial
capitals, selected as Natural Earth's admin-1 capitals of the four study
provinces at scale rank 4 or better, which is the narrowest rule that returns
all four: Shanghai is rank 0, Nanjing and Hangzhou rank 2 and Hefei rank 4, and
a bare threshold reaching Hefei also reaches fourteen other places in the box.
Shanghai's name serves both the municipality and the city: at 8 pt the word
occupies 0.99 by 0.21 degrees here and no position inside the municipality's
polygon fits it, while the other three provinces each hold their name easily. The analysis lattice is **not** drawn
across the main panel, where 66 lines would be texture rather than reference and
where the composite figure already shows the resolution by drawing the cells as
the data; the detail box instead shows six cells over the Yangtze mouth at 4.6
times the main panel's scale, and the same six are outlined on the map at their
drawn size. One cell is 24 by 28 km at 31.7 north. The locator sits outside the
map frame rather than over Zhejiang's coast, and draws Natural Earth's admin-0
land boundary lines unfiltered, with no country named, filled or excluded; six
of the 59 lines in its extent are classed "Disputed (please verify)" by Natural
Earth itself, which also ships 33 per-country viewpoint fields, and this
repository takes no position on any of them.

The terrain is the finding, thin as a reference map's finding must be. The 97<!--#composite.uncovered_cells-->
cells of the lattice that received no qualifying sounding in 2018 are not
scattered evenly over it: 74<!--#composite.absent_on_land--> of them lie wholly
on land, and their median elevation is 502<!--#composite.absent_median_elevation-->
m against 35<!--#composite.covered_median_elevation--> m for the 926<!--#composite.covered_cells-->
cells that were observed. 50<!--#composite.absent_above_500m--> of the 97 sit
above 500 m, against 24<!--#composite.covered_above_500m--> of the 926. The
largest connected group, 47<!--#composite.largest_absent_block--> cells of the
19<!--#composite.absent_components--> the absent cells form, covers the
mountains along the southern edge of the box, 35 of its 47 cells falling mostly
in Zhejiang and 11 in Fujian, at a median 552 m and reaching 1,119 m. That block
is the darkest terrain in this panel, and it is the hole in the middle of the
composite figure's southern edge. Which cells those are is the composite
figure's subject and is deliberately not drawn here.

Boundaries, coastline, populated places and the inset relief are Natural Earth
and are public domain; the province and land layers are 10 m and the inset
boundaries 50 m. Shanghai's outline is the one caveat worth naming at this size:
Natural Earth resolves the municipality with 213 vertices across four parts
where GADM 4.1 uses 1,925 across 112, and at 1.5 cm of drawn width the
difference is not visible, appearing as straight segments along the coast only
above roughly three times magnification. Shaded relief is derived data and its
licence requires the notice carried on the figure: produced using Copernicus
WorldDEM™-90 © DLR e.V. 2010–2014 and © Airbus Defence and Space GmbH 2014–2018
provided under COPERNICUS by the European Union and ESA; all rights reserved.
The organisations in charge of the Copernicus programme by law or by delegation
do not incur any liability for any use of the Copernicus WorldDEM™-90. The main
map is equirectangular with its standard parallel at 31.075 north, the centre of
the study area, so a degree of longitude is drawn 0.857 times as long as a
degree of latitude and the analysis cells stay rectangular; scale is exact only
at that parallel, running 3.9 percent small at the southern edge and 4.8 percent
large at the northern, and area is not preserved. Nothing in this study is
measured from a map, since areas are computed analytically on the authalic
sphere, so the projection is a display choice throughout. The locator is drawn
in the China Albers equal-area conic, which is why the study box appears rotated
in it.

Regenerate with `python scripts/make_study_area_figure.py`. The relief and place
layers it reads are built once by `python scripts/build_map_reference.py --write`
from tiles fetched by `python scripts/fetch_copernicus_dem.py --download`.

---

### The 2018 methane composite

![Mean bias-corrected XCH4 and sounding count per cell over the analysis lattice](methane_composite_2018.png)

**The methane field is smooth at the scale of the analysis lattice, and 9.5<!--#composite.uncovered_percent-->
percent of the lattice is not observed at all.** Cell means run from 1,840 to
1,947 ppb, but the middle 96 percent of them span only 59 ppb, and neighbouring
cells rarely differ by more than a few. The unobserved part is not scattered
noise: 97<!--#composite.uncovered_cells--> of the 1,023<!--#composite.total_cells--> cells
carry no qualifying sounding, and they fall into 19<!--#composite.absent_components-->
connected groups of which the largest holds 47<!--#composite.largest_absent_block-->
cells over mountainous southern Zhejiang. Where the field is observed it rests
on very unequal evidence, from 1<!--#composite.min_soundings--> sounding to
410<!--#composite.max_soundings--> with a median of 74<!--#composite.median_soundings-->.

Panel (a) is the mean of the bias-corrected retrieval, which is the
operationally corrected product and the variable the reproduction's analysis
used throughout; it is not interchangeable with the raw retrieval, since the
correction averages +11.64<!--#composite.bias_mean--> ppb and varies across
cells by more than the field's own standard deviation. The correction does not
remove the field's dependence on surface albedo, which is 199.7<!--#albedo.slope_corrected-->
ppb per unit albedo after correction against 203.9<!--#albedo.slope_raw--> before.
The scale is clipped to the middle 96 percent of cell means, with the arrow caps
marking values beyond it; the excluded tails sit in the least-sampled cells,
whose median count is 2 soundings at the high end and 12 at the low against
74 overall, so they are thin sampling rather than methane. Panel (b) is the
number of qualifying soundings each cell mean rests on, classed in half-decade
steps rather than shaded continuously, because a linear scale would render
every sparse cell alike and the sparse cells are where the sampling structure
is. Both panels share one frame and one lattice of 33 by 31 cells at 0.25
degrees, so a cell in one is the same cell in the other. Coverage is
90.52<!--#composite.coverage_percent--> percent of the lattice over
110,920<!--#composite.soundings--> in-box soundings; qualifying means a
`qa_value` at or above 0.75. Boundaries and coastline are Natural Earth.

Regenerate with `python scripts/make_composite_figure.py`.
---

### Land cover at the resolution it was measured

![Impervious surface at 30 m from GISA and GAIA, rice at 10 m from NESDC, and the six 0.25 degree cell fractions those become](landcover_native.png)

**Every other land-cover figure in this repository shows a fraction per
0.25 degree cell; this is what the fractions are made of.** The window is 5.7
by 3.7 km on the eastern edge of Wuhu, in Anhui, at 118.44 to 118.49 east and
31.3248 to 31.3582 north. Panels (a) and (b) draw impervious surface at 30 m,
186<!--#window.impervious_columns--> pixels across, from GISA and from GAIA;
panel (c) draws the NESDC rice classification at 10 m,
557<!--#window.rice_columns--> pixels across. Each panel gives at least one
drawn pixel to every source pixel, 4.4 for the 30 m products and 1.5 for the
10 m one, so nothing here has been resampled into a smoother picture of itself.

Panel (d) is the same ground as the analysis reads it: three by two cells of
0.25 degrees, about 24 by 28 km each, with the impervious fraction from both
products and the combined rice fraction written in each. The window of panels
(a) to (c) is the small rectangle in the lower middle cell. All six cells have
complete coverage from both products, so none of the numbers rests on a partial
raster.

**The window is not a representative sample and is not offered as one.** It is
34.2 percent rice against 19.5<!--#window.cell_rice_combined_percent--> percent for the
cell that contains it, and 23.9<!--#window.impervious_gisa_percent--> percent
impervious against 26.3<!--#window.cell_impervious_gisa_percent-->. It is a place to
see the resolution.

What the aggregation discards is visible by comparing the panels: the
interdigitation of paddy blocks and built land at a few hundred metres, which
is the scale at which this landscape is organised, becomes one number per
24 by 28 km cell. Of the window, 29.4<!--#window.rice_single_percent--> percent
is single-season rice and 4.9<!--#window.rice_double_percent--> percent is
double-season; the second class exists in only two of the four study provinces,
Anhui and Zhejiang, and Jiangsu and Shanghai have none of it, so the window was
chosen in Anhui in order to show a distinction the study region really carries.
Because the window lies wholly inside Anhui, every 0 in the rice raster here is
real non-rice land; the product declares no nodata and 0 elsewhere also means
out-of-province background, which is why that containment was tested rather
than assumed.

**The two impervious products are not interchangeable at pixel scale either.**
GISA calls 23.9<!--#window.impervious_gisa_percent--> percent of this window
impervious and GAIA calls 29.7<!--#window.impervious_gaia_percent--> percent,
a ratio of 0.81, which is close to the ratio of 0.80 they reach over the four
provinces as a whole.

A caution about resolution that the panels invite and the analysis does not
support: the rice grid is three times finer than the impervious one, and that
buys nothing here. GISA and GAIA are 30 m products derived from Landsat; the
NESDC classification is 10 m, derived from Sentinel-1 and Sentinel-2 by a
time-weighted dynamic time warping method. They are different kinds of product
with different error structures, and both are averaged into the same 0.25
degree cell before anything is fitted. Extent is selected by
`src.landcover.selectors`, `1 <= value <= 36` for GISA and `value >= 5` for
GAIA, which are the two products' opposite year-of-change conventions.

Regenerate with `python scripts/make_landcover_figure.py`. The window clips it
reads are cut once by `python scripts/clip_landcover_window.py --write`.

---

### Urban expansion, 2000 to 2019, from two products

![Cumulative urban extent by year of first imperviousness for GAIA and GISA to 2019, and four-province totals for the thesis's GAIA figures against both products recomputed](urban_change.png)

**Urban extent in these four provinces grew several-fold between 2000 and 2018,
and the three available accounts of it disagree about the growth factor by a
factor of three.** This is the reproduction's one positive quantitative
land-cover finding.

Panel (c) separates the **source** from the **computation**, because there are
two sources and not three. GAIA and GISA are datasets; the 2023 thesis is a
prior study whose impervious figures came from GAIA, so the colour names the
product and the dash names the computation. GAIA as reported in 2023 gives
8,297<!--#urban.thesis_2000--> km2 in 2000 and
49,725<!--#urban.thesis_2018--> km2 in 2018, a factor of
6.0<!--#urban.thesis_factor-->. GAIA recomputed here in 2026 gives
16,387<!--#urban.gaia_2000--> and 49,348<!--#urban.gaia_2018-->, a factor of
3.0<!--#urban.gaia_factor-->. GISA recomputed gives
19,787<!--#urban.gisa_2000--> and 39,532<!--#urban.gisa_2018-->, a factor of
2.0<!--#urban.gisa_factor-->.

That layout makes the sharper comparison visible. **The same product recomputed
holds 2018 to within 0.8 percent and moves 2000 by a factor of two.** A
year-of-change product stores the year each pixel first became impervious, so a
reprocessing with more training years and better cloud handling redates earlier
transitions, and the effect is largest in the earliest years where observations
are sparsest. The disagreement is a property of the product's release history
and not an error in either computation.

The two products also cross over. GISA's 2018 total is
0.80<!--#urban.gisa_over_gaia_2018--> of GAIA's, a difference of about a fifth
in the direction opposite to what the global validation predicts, since GAIA is
the product reported to omit impervious surface. But GISA is the **larger** of
the two in 2000, so the products disagree about the history rather than about
the extent.

Panels (a) and (b) show where the growth is, in three nested classes by the year
a pixel first became impervious. They run to 2019 and not to 2018 because 2019
is the last year both products cover: GISA's pixel values stop at 37, which
decodes to 2019, so a map going further would drop GISA and lose the
disagreement. GAIA reaches 50,348<!--#urban.gaia_2019--> km2 in 2019 and GISA
40,452<!--#urban.gisa_2019-->. **2019 carries a caveat**: it is the first year
past GAIA's original 1985 to 2018 release, and it sits inside a stretch whose
year-on-year growth of the four-province total drops from 7.1 to 10.5 percent
across 2011 to 2016 to between 1.9 and 2.6 percent from 2017 onward. Panel (c)
keeps 2018, which is the year the thesis reported and the only year a
comparison against it can be made.

**Area must not be read from the maps.** A cell is inked where at least a
quarter of it had become impervious by that date, drawn at 1/64 degree, about
1.4 km, from an aggregate at 1/128. That threshold does not preserve area and
does not fail evenly: urban land in 2000 is more dispersed than in 2019, so the
drawn 2000 class is 0.73 of its true area while the drawn 2019 class is 1.30,
which flatters growth by about four fifths. Panel (c) carries the magnitudes and
the maps carry the pattern.

Totals are for the four provinces on the Natural Earth boundaries and come from
`data/processed/urban_extent_totals.csv`, whose twenty overlapping rows
reproduce the two older provincial tables to 1.3e-05; that agreement is the
check that the two products' opposite year conventions were both applied the
right way round. GAIA counts down from 2023, so 2019 is `value >= 4`; GISA
counts up from 1972, so 2019 is `1 <= value <= 37`. Inverting GISA's would
select only what was built in the last two years, 9,468,801 pixels against
202,830,997, and would still draw a plausible map.

Rice is drawn in its own figure. There is no methane equivalent and that is
where a reader will most expect one: TROPOMI's footprint is 7 by 7 km at nadir,
the analysis grid is 0.25 degrees because coverage forced it there, and the 2018
composite leaves 97<!--#composite.uncovered_cells--> of its
1,023<!--#composite.total_cells--> cells with no qualifying sounding at all,
with per-cell counts running from 1<!--#composite.min_soundings--> to
410<!--#composite.max_soundings-->. There is one year of usable methane, not
three, and a fine-resolution methane field from this data would be interpolation
presented as observation.

Regenerate with `python scripts/make_urban_change_figure.py`. The aggregate and
the totals are built once by `python scripts/compute_urban_extent.py --write`.

---

### Paddy rice across the four provinces, 2018

![Single and double season rice per 1.4 km cell across the four Yangtze River Delta provinces, with the unclassified part of Anhui marked, and rice and impervious surface as a share of each province](landcover_regional.png)

**Rice is the study's subject and this is where it is, in the year the methane
composite covers.** Panel (a) draws the NESDC classification on a 1/64 degree
cell, about 1.4 km. Panel (b) puts rice beside the impervious surface it
competes with, as a share of each province's own area.

The map's threshold is chosen by a rule rather than by eye: a cell is inked
where at least 35 percent of it is rice, which is the value at which the drawn
area equals the true area. Measured, the inked total is 1.06 of the
50,042<!--#rice.total_km2--> km2 the provincial totals record, against 0.73 to
1.31 for the urban figure at its own threshold. Rice can be drawn area-honestly
and impervious surface cannot, because this map draws one quantity where that
one draws three.

**The season colour says which season a cell's rice mostly is, not how much.**
The two cannot share a threshold: single-season rice area-matches at 0.35 and
double-season at 0.17, because double-season paddy is 5.3 percent of the rice
and interleaved with single rather than segregated. So one threshold decides
whether a cell is rice and the colour reports the majority season, at the cost
that the double-season colour covers 1,191 km2 of a true
2,677<!--#rice.double_km2-->. Panel (b) carries the areas.

That distinction is a real property of the region and not a nuance. Only two of
the four provinces grow double-season rice at all:
1,890<!--#rice.double_anhui_km2--> km2 in Anhui and
788<!--#rice.double_zhejiang_km2--> km2 in Zhejiang, against none in Jiangsu
and none in Shanghai.

**Unclassified is drawn, because absence here has two meanings.** The NESDC
rasters declare no nodata and their 0 means both real non-rice land and ground
the product never covered, so the map separates the two. The dark class is
land the classification does not reach: the other provinces, which the product
does not cover at all, and the part of Anhui north of 33.3462 north and west of
115.2682 east. That northern boundary is a processing artefact and not an
absence of rice — five annual products across three raster extents all
terminate classification within 22 m of the same latitude, and GloRice puts
about 320 km2 of rice in the region — so drawing it as ordinary non-rice land
would have said northern Anhui grows none. Each of the four rasters is masked
by the province it is named for and never by their union, because the files'
boxes overlap and a union mask assesses shared ground once per file; the
committed totals record the assessed area at 0.861<!--#rice.anhui_coverage-->
of the Anhui polygon and within 0.2 percent of the polygon for the other three.

Anhui's rice bars in panel (b) are therefore a lower bound, and are marked as
one: the denominator throughout the panel is the province polygon, so that
three bars in one group can be compared, and Anhui's rice is measured over the
86 percent of it the product classified. The comparison the panel is for is
this: Shanghai is 50.9<!--#urban.share_shanghai_percent--> percent impervious
and 11.0<!--#rice.share_shanghai_percent--> percent rice, while Jiangsu is
22.8<!--#urban.share_jiangsu_percent--> percent impervious and
21.8<!--#rice.share_jiangsu_percent--> percent rice. Impervious areas are
GAIA's, which is the product the analysis grid carries; GISA finds about a
fifth less in 2018 and the urban change figure draws that disagreement out.

Regenerate with `python scripts/make_landcover_regional_figure.py`. The rice
grid it reads is built once by `python scripts/compute_rice_extent.py --write`.
---

### Observed methane against the fields four models produce

![Observed methane against the held-out field produced by a constant, impervious fraction, a spatial null and wind, with a summary of every scheme and weighting](observed_predicted.png)

**A land-cover model predicts close to the mean everywhere, so its cloud lies
flat; a model of smoothness tracks the diagonal. That contrast is the
reproduction's central result, and it is a shape rather than a number.** None
of these panels is a prediction of methane. Each shows the field a model
produces from its own predictors, drawn against what was observed, and the
figure is about the distance between them; `ERRATA.md` 7.1 records that land
cover does not explain the observed field and this is the demonstration of
that.

Panel (a) is a constant, which has no information and reaches held-out R
squared -0.008<!--#baseline.constant_r2-->. Panel (b) is impervious fraction,
the thesis's own predictor, at 0.085<!--#baseline.impervious_r2--> and an RMSE
of 14.21<!--#baseline.impervious_rmse--> ppb; its cloud is a thickened version
of the constant's rather than a rotated one. Panel (c) is the spatial null,
which predicts each cell from the mean of its eight neighbours and knows
nothing about the surface, at 0.332<!--#baseline.null_r2-->. Panel (d) is wind,
at 0.653<!--#baseline.wind_r2-->, and it is a reference and not an
explanation: `ERRATA.md` 7.4 records that the wind association is not
attributable, because each cell's annual mean is taken over whichever days it
was observed on and those differ across cells by up to 228 days.

The same finding in ranges. The observed field spans
106<!--#baseline.observed_span_ppb--> ppb across the 926 cells. The field
impervious fraction produces spans 43<!--#baseline.impervious_span_ppb-->, the
spatial null's spans 67<!--#baseline.null_span_ppb-->, and the constant's spans
1.4<!--#baseline.constant_span_ppb-->, which is five folds each predicting
their own training mean. Land cover sits nearer the constant than the
smoothness on every measure the figure carries.

**Every predicted value is out of fold**, fitted on training blocks and
predicted onto cells the fit never saw. That distinction is not decoration: the
spatial null's in-sample R squared is 0.685<!--#baseline.null_in_sample_r2-->
against its held-out 0.332<!--#baseline.null_r2-->, so a figure drawing fitted
values would have shown a smoothness bar twice the bar it is. All four panels
share one pair of axis limits, so a flat cloud is flat rather than stretched,
and mark area carries the sounding count on the composite figure's half-decade
classes, because a cell's observed value is the mean of between
1<!--#composite.min_soundings--> and 410<!--#composite.max_soundings-->
soundings.

The panels are one scheme and one weighting, spatial blocks and unweighted, and
panel (e) is there so that is not a hidden choice: it draws the held-out R
squared of all four models under both schemes and both weightings, with the
scheme in the colour and the weighting in the fill. Spatial blocks because it
is the only scheme in which the spatial null is a bar at all — under
leave-one-province-out a held-out province's interior has no training
neighbour, so the null falls to -0.091, which still beats the constant's -0.172
but is below zero and so explains none of the held-out variance.

All four models run on the 926<!--#composite.covered_cells--> cells that carry
a methane value. The rice models are absent because they run on 531 cells and
the table's own rule is that results on different samples must not be compared
without saying so; four panels side by side is a comparison whatever a caption
says. Their numbers, on the same scheme and weighting: rice alone reaches
-0.031<!--#baseline.rice_alone_r2-->, impervious on that same sample reaches
0.018<!--#baseline.impervious_rice_sample_r2-->, and adding rice to impervious
moves it to 0.017<!--#baseline.rice_plus_impervious_r2-->, which is down rather
than up.

Regenerate with `python scripts/make_observed_predicted_figure.py`. The
held-out predictions it reads are built by
`python scripts/compute_baseline_predictions.py --write`, which refuses to
write unless the metrics recomputed from them reproduce
`data/processed/baseline_results_2018.csv`.

---

### The field a land-cover model produces, and what is left over

![The observed 2018 methane field, the held-out field an OLS fit on impervious fraction produces on one shared colour scale, and the difference between them on a diverging scale](residual_field.png)

**The field a land-cover model produces is not the observed field, and the
difference is not noise: it has almost all of the observed field's spatial
structure still in it.** Panel (b) is not a prediction of methane. It is the
field one land-cover covariate produces, drawn beside the observation so the
distance between them can be read cell by cell; `ERRATA.md` 7.1 records that
land cover does not explain the observed methane field, and this figure is the
demonstration of that. `ERRATA.md` 1.1 records that the thesis's Figure 4.7,
captioned as this comparison, was the same embedded image as Figure 4.5(a), so
the comparison was never actually drawn.

Panels (a) and (b) share one colour scale,
1840<!--#residual.scale_low_ppb--> to 1947<!--#residual.scale_high_ppb--> ppb,
which is the observed field's own full range and is not clipped. Under it the
observed field spans 106<!--#baseline.observed_span_ppb--> ppb and the field
the model produces spans 43<!--#baseline.impervious_span_ppb-->, four tenths as
much, which is the same finding the scatter figure draws as a flat cloud. The
composite figure clips its value panel to the 2nd and 98th percentiles and this
one deliberately does not: there the job is to read one field well, here it is
to compare two spans, and clipping would cut the observed span shown by nearly
half while leaving the model field almost untouched.

Panel (c) is the residual, symmetric about zero at plus or minus
45<!--#residual.scale_limit_ppb--> ppb with arrow caps;
4<!--#residual.clipped_cells--> of the 926<!--#residual.observed_cells--> cells
run past an end, the residuals themselves running from
-48<!--#residual.residual_low_ppb--> to
60<!--#residual.residual_high_ppb--> ppb with a standard deviation of
14.2<!--#residual.residual_sd_ppb-->. The structure in it is the point:
Moran's I of the residual is
0.646<!--#residual.residual_moran-->, against
0.709<!--#residual.observed_moran--> for the observed field, so the fit removes
8.8<!--#residual.moran_removed_percent--> percent of the observed field's
spatial autocorrelation and leaves the rest. **The weights are queen contiguity
among observed cells on the 0.25 degree analysis lattice, row standardised,
self excluded, with no distance decay**, stated because `ERRATA.md` 6.2 records
that the thesis reported a Moran's I without saying what its weights were,
which makes a number of that kind unreproducible.
1<!--#residual.isolated_cells--> cell has no observed queen neighbour and is
dropped from the statistic rather than given a weight of zero; the pseudo p is
at its floor of 0.001 over 999<!--#residual.permutations--> permutations of the
residual over the same cells.

**Every value in panel (b) is out of fold**, fitted on the training rows of a
spatial block and predicted onto rows the fit never saw, from the same
committed predictions the observed-against-predicted figure draws, so the two
figures cannot be describing different fits. The model is impervious fraction
alone rather than impervious with rice: rice exists for only 531 of the
926<!--#residual.observed_cells--> cells, so a two-covariate field would be
blank over 395 more of them and this figure would carry two kinds of absence in
the same near-white, which is the one thing it cannot afford.

97<!--#residual.absent_cells--> cells received no qualifying sounding and are
absent in all three panels, drawn as this repository draws absence everywhere:
a near-white fill with a thin outline, so a single isolated cell reads as a
deliberate mark. In panel (c) that is a statement and not an inheritance —
**an unobserved cell has no residual, not a residual of zero**, and zero is the
most meaningful value on a diverging scale, so filling those cells with it
would draw the model's 97 best cells exactly where it has no cells at all. The
scale's centre is held 0.17 clear of the absence tone in luminance for the same
reason.

One property of the diverging scale is worth stating rather than leaving to be
discovered. Its two limbs are matched in luminance, so that errors of equal
size and opposite sign read as equally large, which means the sign is carried
by hue alone: a greyscale print of panel (c) shows how large each error is and
not which way it points. The alternative — limbs of unequal luminance — buys
the sign back by drawing equal errors as unequal, which is the worse figure.
Because hue is the only carrier left, the two limbs are checked against each
other under simulated protanopia, deuteranopia and tritanopia, and hold at
least 15 CIE76 units apart everywhere beyond a tenth of the scale.

Regenerate with `python scripts/make_residual_field_figure.py`. It reads the
same `data/processed/baseline_predictions_2018.csv` as the
observed-against-predicted figure.
