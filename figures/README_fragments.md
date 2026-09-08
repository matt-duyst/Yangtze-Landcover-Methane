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

![The four Yangtze River Delta provinces with the 0.25 degree analysis grid, and a locator inset](study_area.png)

**The four provinces of the Yangtze River Delta region, with the 0.25 degree
analysis grid that every later figure in this repository is drawn on.** The
grid is 33 rows by 31 columns, 1,023 cells, spanning 114.8 to 122.55 east and
26.95 to 35.2 north. Those are the bounds the cells actually occupy, not the
declared box of 114.8 to 122.6 and 27.0 to 35.2: the cell count rounds down in
longitude and up in latitude, so the grid stops 0.05 degrees short of the
declared east edge and runs 0.05 degrees past the declared south edge.

All boundaries are Natural Earth, 10 m for the provinces and coastline and
50 m for the inset outline, which is the extent of the 31 units Natural Earth
files under China and so excludes Taiwan, Hong Kong and Macau. The main map is
equirectangular with its standard parallel at 31.075 north, the centre of the
study area, so a degree of longitude is drawn 0.857 times as long as a degree
of latitude and the analysis cells stay rectangular; scale is exact only at
that parallel, running 3.9 percent small at the southern edge and 4.8 percent
large at the northern, and area is not preserved. Nothing in this study is
measured from a map, since areas are computed analytically on the authalic
sphere, so the projection is a display choice throughout. The inset is drawn
in the China Albers equal-area conic, which is why the study box appears
rotated in it. Of the 1,023<!--#composite.total_cells--> cells, 926<!--#composite.covered_cells--> received at least one qualifying
methane sounding in 2018 and 97<!--#composite.uncovered_cells--> received none; which cells those are is the
subject of the composite figure and is deliberately not shown here. Natural
Earth resolves Shanghai with 213 vertices across four parts where GADM 4.1
uses 1,925 across 112, and that difference is not visible at the size drawn
here, appearing as straight segments along the coast only above roughly three
times magnification.

Regenerate with `python scripts/make_study_area_figure.py`.

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
