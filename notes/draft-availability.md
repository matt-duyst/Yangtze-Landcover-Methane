# Data and code availability, drafted

Two statements a submission needs and this repository did not have in any
publishable form. **Both are drafts.** The data statement is assembled from
three registers that already exist and disagree in convention; the code
statement rests on the recipe registry. Neither is final text, because several
entries wait on a decision rather than on work, and those are listed last.

**Why this is not in `notes/paper-target.md`.** The target document holds what
the paper will argue. These are statements about the apparatus, they are long,
and they change whenever a dataset is added, so they sit in their own file and
the target document points here.

**What is guarded here and what is not.** This file is in
`scripts/verify_claims.py`'s `SCANNED` list, because the recipe tier counts
below drift every time a recipe is added and that is exactly the class of
number this repository guards; they are marked and resolved against the
registry. The rest are identifiers, byte counts, checksums and dates quoted
from `config/sources.yml` and `data/manifest.json`, which are registers rather
than artefacts and have no resolvers. The cost is stated rather than hidden:
**the provenance numbers below are checked by review, not by a test.**

## Where provenance currently lives, and why that is the first problem

Three registers, three conventions, no single list:

| Register | Holds | Machine-readable | Naming |
|---|---|---|---|
| `config/sources.yml` | 5 fetchable sources with DOI, licence and citation | yes | `gaia`, `gisa`, `glorice`, `s5p`, `scidb_rice` |
| `data/manifest.json` | 11 fetched artefacts with checksums and licence text | yes | `gaia_1985_2022`, `s5p_l2_ch4_2018`, … |
| `notes/dataset-leads.md` | the sources found in September 2026, as prose | no | prose table |

The two machine-readable registers overlap on three datasets under different
keys, and neither is complete. **One dataset the committed analysis uses
appears in none of them**, which is the defect recorded in the outstanding
list below.

## Data availability

### The methane observations

**Sentinel-5P TROPOMI Level 2 methane, 2018, RPRO stream.** Fetched from the
MEEO mirror at `https://meeo-s5p.s3.amazonaws.com`, which serves the
operational products over plain HTTPS with no credentials; Copernicus Data
Space carries the same granules but requires authentication and so cannot run
from a fresh clone. **No licence is stated on this route** and none is recorded
in either register. **There is no usable checksum**: every S3 ETag observed is
a multipart tag whose part size is not published, so verification is
structural — the file must open as netCDF4 and hold a `PRODUCT` group with the
expected variables. That is weaker than the MD5 verification the figshare and
Science Data Bank routes get, and it is the weakest verification in this
project.

**Blended TROPOMI+GOSAT XCH4.** Balasus et al. (2023), `10.5194/amt-16-3787-2023`.
The deposit's own terms, quoted from `data/manifest.json`: "There are no
restrictions on the use of this data, but please contact
nicholasbalasus@g.harvard.edu before its use in a publication." **That contact
has not been made.** It is a precondition of publication stated by the data
provider, not a courtesy, and it is the first item in the outstanding list.
Reproducibility caveat: **1,182 of 3,436 keys carry multipart ETags**, so no
content checksum is available for 34 percent of this source and verification is
structural for that part; the threshold is exactly 8 MiB.

**Hefei TCCON.** Fetched, used and deleted. No artefact, no manifest entry, and
no recipe. The three column counts that reached four documents therefore rest
on data this repository cannot produce. See the outstanding list.

### Land cover

**GAIA annual global artificial impervious area, 30 m.** figshare
`10.6084/m9.figshare.27245775.v1`, **CC BY 4.0**. Gong et al. (2020),
`10.1016/j.rse.2019.111510`. Nine 5-degree tiles; the 2.3 GB archive is not
internally addressable over the figshare route, so the whole archive must be
fetched to reach any tile.

**GISA global impervious surface area, 30 m, 1972–2019.** Fetched from Wuhan
University at `http://irsip.whu.edu.cn/resv2/GISA_tif.zip`, 882,324,389 bytes,
sha256 recorded in `config/sources.yml`. GISA's documented per-tile links go
through Zenodo, which returns 403 at the network level from this host, so this
is the only route found. Huang et al. (2021), `10.1007/s11430-020-9797-9`.
**Licence: not stated on the download page**; the product is described in the
paper as freely available for research. Four 10-degree tiles cover the box.

**Copernicus WorldDEM-90.** Used for the study-area figure's terrain. Its
licence requires an attribution notice, which is set in the figure itself at
`src/figures/study_area.py` and asserted verbatim by
`tests/test_figures_study_area.py`, so a rebuild cannot silently drop it.

**Natural Earth.** Public domain; five derived selections are registered in
`data/manifest.json`.

### Rice

**NESDC China Rice 10 m/20 m.** **This is the gap.** The committed
`data/processed/analysis_grid_2018.csv` was built with `--rice-source nesdc`
from rasters obtained over an FTP route under a personal-use grant that cannot
be scripted, and the dataset appears in **no** register: no DOI, no licence, no
citation, no fetch script. What makes this survivable rather than fatal is that
the repository already measured the alternative: the Science Data Bank product
is the same classification for 2018 with the double-season class removed, and
rebuilding the grid from it changes only `rice_fraction_combined`, in 190 of
927 rows. A reader without the grant regenerates every other column exactly.

**Single-season rice in China, 2017–2022.** Science Data Bank
`10.57760/sciencedb.06963`, version V8, **CC BY 4.0**, anonymous Croissant
export. Shen et al. (2023), `10.5194/essd-15-3203-2023`. This is the
reproducible substitute for the NESDC product above.

**GloRice (I) gridded paddy rice annual distribution, physical area,
Extensive.** figshare `10.6084/m9.figshare.27965832.v2`, **CC BY 4.0**. Xie et
al. (2025), `10.1038/s41597-025-04483-1`.

### Inventories and source locations

**CHN-CH4 gridded per-sector anthropogenic methane emissions for China.**
Zenodo `10.5281/zenodo.15107383`, **CC BY 4.0**, five sector archives at
25.0 MB, fetched 14 September 2026. Version caveat, which matters: **the latest
version holds only a national comparison table and not the grids**, so the
grids must be taken from an earlier version. Five of the domain's seven sectors
are present; aquaculture and natural wetland have none, an anthropogenic
inventory having no sector for either. Input to
`data/processed/sector_composition_2018.csv` and
`data/processed/inversion_dofs_2018.csv`.

**Coal mine-level methane, 2018–2024.** Zenodo `10.5281/zenodo.21483131`,
**CC BY 4.0**. **Gridded coal mine methane, 2011–2019.** Zenodo
`10.5281/zenodo.10884855`, **CC BY 4.0**. **Underground wastewater treatment
plants in China.** figshare `10.6084/m9.figshare.26085265.v2`, **CC BY 4.0**.
**Aquaculture ponds.** Fetched. These four were located to bound confounds and
to support the case-study section; not all of them feed a committed artefact,
and the statement should name only those that do once the figure set is final.

## Code availability

All analysis code is in this repository. It is organised so that every
committed artefact names the command that produces it:
`config/recipes.yml` registers **73 <!--#pipeline.recipes--> recipes**, and `scripts/verify_recipes.py`
regenerates an artefact and compares it against the committed bytes.

What a reader can actually reproduce, by tier:

| Tier | Recipes | What it needs |
|---|---|---|
| committed inputs, verified continuously | 41 <!--#pipeline.recipes_committed--> | a clone and the test suite |
| local inputs, verified on local data | 22 <!--#pipeline.recipes_local--> | the raw datasets above, about 6 GB |
| network inputs, verified on demand | 9 <!--#pipeline.recipes_network--> | a live route to the source |
| unregenerable | 1 | nothing reproduces it |

The **41 <!--#pipeline.recipes_committed-->** are verified on every run of the default suite. The **22 <!--#pipeline.recipes_local-->** need the
raw data; of those, the ones resting on the NESDC rasters carry the substitution
described above. The **9 <!--#pipeline.recipes_network-->** depend on a third-party route staying up, and three
of those routes were found to apply request-signature filters that changed
between September passes, so a failure there is not evidence of a broken
pipeline.

The **one unregenerable** artefact is
`data/processed/urban_area_by_province_gisa.csv`, written by hand in commit
f6b1b0c with no code that produces it. It is registered `unregenerable` with
comparison disabled, which is a declaration rather than an omission. It is used
only as an agreement column against the regenerable
`data/processed/urban_extent_totals.csv`, and the claim checker resolves no
prose number from it, so no published figure or number depends on it.

**Licence: none.** This repository carries no `LICENSE` file, so the code is
under default copyright and a reader has no grant to run or modify it. This
blocks the code availability statement and is a decision, not work.

## Outstanding, and each waits on a decision

1. **Contact Balasus before publication.** The blended product's own terms ask
   for it. Not done. Nothing else in this project has an unmet provider
   condition.
2. **Choose a code licence.** No `LICENSE` file exists.
3. **The Hefei TCCON sentences.** Three counts — 2,767 retrievals, 44 days,
   nine coincident days — appear in `notes/draft-methods.md`,
   `notes/draft-introduction.md`, `notes/draft-discussion.md` and
   `notes/paper-target.md`, are unmarked, and have no artefact behind them. The
   drafts' own unresolved lists already name them. Either regenerate them, which
   `notes/paper-target.md` prices at roughly 480 MB because only the nine
   coincident days are needed, or cut the sentences. They are load-bearing for
   the "not a validated result" framing, so cutting them costs an argument.
4. **The NESDC rice product.** Either keep the committed grid and state the
   grant and the 190-row substitution in the paper, or rebuild the grid from the
   Science Data Bank product so that the whole chain is anonymous and citable
   and lose `rice_fraction_combined`.
5. **Two unstated licences.** The S5P mirror route and the GISA download page
   state no terms. Decide whether to seek written permission or to cite the
   primary distributor instead.
6. **Three sections a submission needs and no document drafts.** Author
   contributions, competing interests, and financial support. None appears in
   any file here.
