# 2023 figure outputs

`legacy/output/raw/` holds bare classification rasters. They carry no basemap,
no title, no legend, no scale bar and no annotation of any kind: each is the
classification itself, written straight out of the notebook. `legacy/figures/`
holds the styled cartographic figures built from those same classifications,
with the sea, the provincial boundaries, the legend and the surrounding
furniture drawn in. The two directories are the same work at two stages rather
than two sets of results.

Four filenames appear in both directories, and they do not all mean the same
thing. `Rice_2000.png` and `Rice_2010.png` differ between the two, which is what
the two-stage relationship predicts: the styled version is larger and carries
the map furniture the raw one lacks. `XCH4_2018.png` and `XCH4_2018_Hotspot.png`
are byte-identical across the two directories, verified by SHA-256, so those two
are literal duplicates of one file rather than a raw and a styled version of it.

Colour use is consistent within a series but not across all of them. The three
rice figures share one green thematic colour for every year, and all six mapped
figures share the same basemap, extent and framing, down to near-identical pixel
counts for the sea and boundary greys. The three urban figures deliberately do
the opposite, taking a different colour per year: pale green for 2000, pink for
2010, and pale blue-violet for 2018, which is how the thesis text describes them.
Anyone reading urban colour as a thematic quantity rather than as a year label
will misread these.

Two filenames mislead about their contents. `legacy/figures/Accuracy_Assessment.png`
is a rendered image of the thesis Table 1, listing urban extent, PPPM-derived
paddied rice and recorded sown area of rice by province and year. It contains no
classification accuracy metric at all: no confusion matrix, no overall or
per-class accuracy, no kappa. And of the two provincial bar charts,
`Provincial_Graph.png` is the figure of record, appearing in the thesis as
Figure 4.6 with the same title, bars and legend; `Provincial-Stats.png` is a
restyled variant, carrying a different title, a different palette and a
different grouping, that does not appear in the thesis.
