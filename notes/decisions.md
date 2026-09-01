# Audit decisions

Decisions taken during the 2026 audit that are not obvious from the code, with
the reasoning that produced them. Recorded so a later pass does not undo one by
mistake or rediscover it by paying for it.

## History will not be rewritten

`legacy/data/` holds nine source images totalling 44.4 MB, and adding them cost
the object store nothing: the pack stayed at 85.60 MiB and the object count at
205, because git is content-addressed and those blobs were already present from
before commit `b0778b8` removed the `JPGs/` paths. Re-adding identical bytes
under a new path creates a tree entry, not a second copy.

That saving depends entirely on the old paths remaining reachable in history. A
rewrite to purge `JPGs/` would delete the only copies the pack holds, at which
point `legacy/data/` becomes the sole copy and the same 44.4 MB has to be stored
for real. A cleanup intended to shrink the repository would grow it. There is a
second reason on the same side: rewriting changes every commit hash downstream
of the earliest edit, and a signed root commit makes that the whole history.

## The PDF is the document of record

For any question about what the thesis says, read `writeup/Duyst_Thesis.pdf`,
not `Duyst-Yale-Thesis.md`. The two are not the same document and the markdown
is the weaker source.

The markdown numbers its figures sequentially, Figure 1 through Figure 18, with
no chapter-decimal number anywhere; the PDF uses the chapter-decimal scheme the
text refers to, Figure 1.1, 3.1 and 4.1 through 4.7. So a figure number means
different things in the two files and cannot be carried between them. The
markdown also carries its own eighteen images embedded as base64 data URIs
rather than referencing the committed figures, so its pictures are not
necessarily the repository's pictures. And it has no abstract, results or
discussion section at all: it contains no heading above the third level and
none named for any of them.

A figure identification made in this audit was wrong and had to be reversed
after checking the PDF. That is the reason for the rule rather than an
illustration of it.

## Provincial_Graph.png is the published figure

`legacy/figures/Provincial_Graph.png` is the figure published as Figure 4.6.
It was confirmed by extracting the embedded image from page 21 of the PDF and
comparing: the same title, the same peach, light green and dark green palette,
the same bars, and the same legend along the bottom. It is also byte-identical
to the `Prov_Stats.png` blob `f1769763`, deleted twice in 2023, so it is the
long-lived file under a later name.

`legacy/figures/Provincial-Stats.png` is a later restyle that does not appear in
the thesis. It carries a different title, a beige, mint and teal palette, a
legend moved to the top and bars grouped by year. It is the more polished of the
two, which is presumably why it keeps being taken for the original. It was
identified incorrectly before being settled against the PDF.

## Urban figure colour is a year label, not a quantity

The three urban figures use a different thematic colour for each year: pale
green for 2000, pink for 2010, and pale blue-violet for 2018. This matches how
the thesis text describes them. The three rice figures do the opposite, using
one green across all years, and all six share the same basemap, extent and
framing.

Urban colour therefore encodes which year is being shown, not how much of
anything there is. Reading it as a thematic quantity, or comparing urban colours
across the three panels as though they were on one scale, produces nonsense.

## h5py applies no fill masking

Reading a grouped netCDF through xarray, with either the `netcdf4` or the
`h5netcdf` engine, masks the fill value to NaN by default; the two engines agree
with each other exactly. Reading the same file through h5py directly does not:
the fill cell comes back as its raw sentinel value.

This matters because the failure is silent. A mean or a sum computed over an
unmasked array is pulled toward the sentinel rather than raising, and a large
negative sentinel over a sparse granule can move a result by orders of magnitude
while still returning a plausible-looking number. Any code that drops to h5py
for speed has to mask the fill itself. The sentinel TROPOMI Level 2 actually
uses should be read from the granule's own `_FillValue` attribute rather than
assumed.

## Year-of-change products are version-dependent

GAIA does not store urban extent per year. It stores, in a single band, the year
each pixel first became impervious, and the extent for any year is recovered by
thresholding that band. This makes the product unusually sensitive to
reprocessing. A later release re-runs the change detection over the whole
archive, so a pixel that one version dates to 2004 another may date to 1996.
Nothing about the file signals that a transition has moved; the raster looks the
same and decodes cleanly under either version.

The versions in play here are not the same. The thesis used the 1985 to 2018
release. The archive currently reachable on figshare is 1985 to 2021, and Star
Cloud distributes a later version again, described on the figshare record as
Version 2024. So a reproduction is comparing two different reconstructions of
the same history, not two computations of the same data.

The provincial totals show exactly the shape that implies. Summed across the
four provinces, the current release agrees with the thesis to 0.8 percent for
2018, but differs by a factor of 1.98 for 2000. The recent end, where least
reprocessing separates the two versions, matches closely; the historical end,
where the reconstruction has been redone, does not. A reproduction of the 2018
extent is therefore meaningful. A reproduction of the 2000 or 2010 extent
against a different version is not, and a disagreement there should not be read
as an error in either computation.

The same caution applies to GISA, which is also a year-of-change product and has
its own release history, and it applies with an extra hazard because the two
products encode the year in opposite directions.

Both conventions are recorded here explicitly, because getting one backwards
does not fail loudly. It inverts the urbanisation history, turning the oldest
urban core into the newest expansion, and still produces a plausible-looking
map.

GAIA counts downward from the newest year. Its readme states that pixel values
represent urban frequency over 0 and 2 to 38, with 0 non-urban, 2 newly expanded
in 2021, and 38 existing in 1985 and before. So year equals 2023 minus value,
and cumulative extent for a year is value greater than or equal to 2023 minus
that year: 2000 is value >= 23, 2010 is value >= 13, 2018 is value >= 5. Source:
ReadMe-GAIA.txt, distributed alongside the data at
https://doi.org/10.6084/m9.figshare.27245775.v1.

GISA counts upward from the oldest year. The Wuhan University distribution page
states that values range 0 to 37, zero meaning non-impervious, and pairs the
years 1972, 1978, 1985, 1986 and so on through 2019 with the values 1, 2, 3, 4
and so on through 37. So 2000 is value >= 18, 2010 is value >= 28, and 2018 is
value >= 36. Source: http://irsip.whu.edu.cn/resv2/dataweb.php.
