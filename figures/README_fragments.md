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
number of granules processed and a small sample measures its own size rather
than the year's coverage.** The first 36 granules reach 56.0 percent of the
1,023 cells, and the remaining 542 add only 34.6 points to finish at 90.62
percent, so a reconnaissance-sized sample lands on the steep part of a curve
that has barely begun to flatten. Soundings are also distributed unevenly
through the year, and the unevenness runs opposite to the growing season:
October alone carries 30.75 percent of the year's 110,928 in-box soundings from
31 productive granules, while June, July and August together carry 14.57
percent from 92.

Panel (a) is the cumulative count of grid cells that have received at least one
qualifying sounding, plotted against granules processed in the order the
streaming loop handled them, over 578 granules of which 222 contributed. Panels
(b) and (c) share a month axis and are stacked rather than drawn on twin axes,
so that neither series can be made to look larger than the other by a choice of
limits. January through March are shaded because the reprocessed 2018 stream
begins on 30 April; no granule was acquired over the study box in those months,
which is a different fact from a month that was sampled and yielded nothing.
April is a single granule and 290 soundings, labelled because at this scale its
bar is otherwise indistinguishable from the shaded absence beside it. Yield per
granule ranges from 154 soundings in July to 1,100 in October, a factor of 7.2,
and the July minimum coincides with both the monsoon cloud cover that defeats
the retrieval and the flooded-paddy season the study is about. Coverage is
computed on the 0.25 degree grid of 33 by 31 cells; qualifying soundings are
those with `qa_value` at or above 0.75.

Regenerate with `python scripts/make_coverage_figure.py`.
