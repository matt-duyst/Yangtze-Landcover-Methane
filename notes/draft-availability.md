# The submission apparatus, drafted

The availability statements first, then the journal sections ACP requires. Both
are drafts.

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

**Hefei TCCON GGG2020.R1.** CaltechDATA, `10.14291/tccon.ggg2020.hefei01.R1`,
57.49 MB, registered in `data/manifest.json` and **not committed**. Its licence
is the strictest in this project and the only one that forbids redistribution:
clause 4 of the TCCON Data License reads "All other rights, including
redistribution, display, and publishing adaptations are reserved". So
`data/processed/tccon_hefei_2018.csv` carries counts derived from the record and
a network-tier recipe fetches the record itself.

Its clause 5 is an obligation on whoever submits: the individuals listed on the
DOI landing page must be contacted, with a description of the intended
publication, **at a minimum of four to six weeks before a manuscript is
submitted** and one to two weeks before a presentation. That applies to any work
including TCCON data. Only the co-authorship expectation is conditioned on the
data being essential, which it is not here. Clause 5 also provides that if the
individuals do not respond to three emails over a ten-week period, the data
falls under CC BY 4.0.

A newer release exists, GGG2020.1.R1 (`10.14291/tccon.ggg2020p1.hefei01.R1`,
2026). The committed counts are from R1 and reproduce from R1; which release a
submission cites is a decision.

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

**NESDC China Rice 10 m/20 m.** *This was recorded here as the gap and it is
now closed.* The grant that carried these files covers the FTP access address
and not the data, so this was never a licensing problem, and the data is
published openly under **CC BY 4.0** in two dataset papers by one group: Shen et
al. (2023) for the single-season class, `10.5194/essd-15-3203-2023`, and **Pan
et al. (2021) for the double-season class**, `10.3390/rs13224609`, which is the
class the anonymous export folds away and therefore the citation for
`rice_fraction_combined`. Both are now in `config/sources.yml` under
`nesdc_rice`, which deliberately carries no fetch route: scripting it would
redistribute the credential, which is what the grant actually forbids. The
original text of this entry follows, because the substitution it describes is
still the right thing for the statement to say.

The committed
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
`config/recipes.yml` registers **74 <!--#pipeline.recipes--> recipes**, and `scripts/verify_recipes.py`
regenerates an artefact and compares it against the committed bytes.

What a reader can actually reproduce, by tier:

| Tier | Recipes | What it needs |
|---|---|---|
| committed inputs, verified continuously | 41 <!--#pipeline.recipes_committed--> | a clone and the test suite |
| local inputs, verified on local data | 22 <!--#pipeline.recipes_local--> | the raw datasets above, about 6 GB |
| network inputs, verified on demand | 10 <!--#pipeline.recipes_network--> | a live route to the source |
| unregenerable | 1 | nothing reproduces it |

The **41 <!--#pipeline.recipes_committed-->** are verified on every run of the default suite. The **22 <!--#pipeline.recipes_local-->** need the
raw data; of those, the ones resting on the NESDC rasters carry the substitution
described above. The **10 <!--#pipeline.recipes_network-->** depend on a third-party route staying up, and three
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

**Licence: MIT**, in `LICENSE`, tracked since 3 September 2026, with the same
licence recorded in `CITATION.cff`. An earlier version of this file said the
repository carried no `LICENSE` file at all. **That was wrong**, and the cause is
worth recording because it is a mechanical trap rather than a lapse of
attention: the check was `ls LICENSE* LICENCE* COPYING*`, and zsh aborts a
command when any glob fails to match, so the unmatched British spelling meant
`ls` never ran and the fallback message fired on a shell error.

What was genuinely missing is the **scope**, which `README.md` now states. MIT
governs `src/`, `scripts/`, `tests/`, `config/` and the documentation, MIT's own
text covering "associated documentation files". It does not govern the 2023
thesis, which is the author's own work, and it does not govern the committed
data artefacts, whose sources' terms travel with them. Nothing is vendored and
no source file carries a licence header, so the choice was never constrained.

The sharpest case in that scope is **GISA**, which states no licence anywhere:
four committed artefacts are named for it and five more carry GISA-derived
columns, and all nine rest on no stated grant.

**What a reader still cannot cite.** ACP requires code to be deposited with a
DOI and cited in the reference list. `CITATION.cff` names a GitHub URL, which is
not a DOI, and its ORCID field is a TODO. A Zenodo release supplies both.

## Outstanding, and each waits on a decision

Rewritten on 14 September 2026. Four of the six items below are new and three of
the originals are gone: the licence existed, the TCCON counts are recovered, and
the NESDC product turned out to be citable.

**Two provider contacts, both with clocks.**

1. **The Hefei TCCON site's listed individuals**, at a minimum of four to six
   weeks before submission, per clause 5 of the TCCON Data License. This is the
   only dated obligation in the project and it sets the earliest possible
   submission date. An earlier record in `notes/decisions.md` said this licence
   "does not bind, because nothing rests on it"; that read the co-authorship
   sentence as the whole obligation and is corrected.
2. **The author of the blended TROPOMI+GOSAT product**, whose terms ask to be
   told before publication. Undated but explicit, and still not done.

**Three things only Matt can supply.**

3. **Financial support.** The reproduction was unfunded as far as this
   repository records; whether the 2023 thesis was supported is not something
   any file here can answer, and ACP wants grant numbers rather than a sentence.
4. **Authorship.** Whether this is a single-author paper at all, given the 2023
   thesis was advised.
5. **The AI usage disclosure.** ACP requires one, this work needs a substantial
   one, and its wording is the author's.

**One thing that is a ten-minute job on Matt's account.**

6. **A Zenodo release**, for the DOI that ACP requires code to be cited by, and
   an ORCID for `CITATION.cff`'s TODO.

**And one that may have no answer.** GISA states no licence and nine committed
artefacts derive from it. Seeking written permission is the thorough course;
citing the paper's "freely available for research" description is what the
field does in practice. Worth a decision rather than a default.

---

# The journal sections, drafted

ACP's own submission page is the authority for what a manuscript must carry and
in what order, and it was read on 14 September 2026 rather than recalled. Its
back matter runs: code availability, data availability, interactive computing
environment, sample availability, video supplement, supplement link, team list,
author contribution, competing interests, statement on inclusion in global
research, disclaimer, special issue statement, acknowledgements, financial
support, review statement. Copernicus inserts the copyright statement, the
supplement link, the special issue statement and the review statement itself.

**The apparatus audit named three missing sections. ACP's list has five that
apply here**, and one of the two it missed is the more consequential.

## Author contribution

Required, placed before the acknowledgements. ACP recommends the CRediT
taxonomy. Draft, on the assumption of single authorship:

> MD designed the study, wrote the analysis code, performed the analysis and
> prepared the manuscript.

**What only Matt can supply.** Whether this is a single-author paper. The 2023
thesis was advised by Xuhui Lee, and whether that advisory role becomes
co-authorship on a 2026 paper reworking the thesis is not a question the
repository can answer. If it does, this statement and the author list both
change. A second authorship question is live and separate: the Hefei TCCON
licence says co-authorship "would normally be expected" where a site's data is
essential to the work. It is not essential here and the drafts say so, so the
expectation does not arise — but it arises immediately if the comparison is ever
promoted to a validation.

## Competing interests

Required even when there are none, and ACP gives the wording to use:

> The authors declare that they have no conflict of interest.

**What only Matt can supply.** Confirmation that this is true. The repository
records no funding, no commercial relationship and no editorial board
membership, but absence of a record is not a declaration.

## Financial support

**What only Matt can supply, and this one is entirely his.** ACP lists support
funds and grant agreement numbers as specified at manuscript registration and
reports them to FundRef, so a number is wanted, not a sentence. The repository
records no funding for the 2026 reproduction. The 2023 MESc thesis may have been
supported — a Yale School of the Environment fellowship, a departmental award,
or a grant supporting the advisor's group whose resources the thesis used — and
any of those may need acknowledging even though the reproduction itself was
unfunded. Nothing in this repository can settle it.

If there was none, ACP's convention is to say so rather than omit the section.

## Acknowledgements

Distinct from the above, and ACP asks for more in it than gratitude: it asks
authors to name **research infrastructure they benefitted from**, giving field
stations and marine laboratories as examples. For this work that means the data
infrastructure, which is unusually load-bearing here because the whole argument
is about what public products can support. Candidates, in the order they would
appear:

* **The data providers whose terms request acknowledgement.** The Hefei TCCON
  site and its listed individuals, once contacted, and the author of the blended
  TROPOMI+GOSAT product, whose terms ask to be told before publication so that
  proper acknowledgement can be made. Both contacts are outstanding.
* **The infrastructure.** TCCON as a network; the Copernicus programme and ESA
  for Sentinel-5P; the MEEO mirror, which is the only anonymous route to the
  2018 L2 methane record and without which this work could not run from a fresh
  clone; CaltechDATA, Science Data Bank, figshare and Zenodo as the deposits
  that made the land-cover and inventory products reachable.
* **The Copernicus DEM notice.** It belongs in the figure and its caption, where
  it already is, because the licence requires it on the adapted product itself.
  Repeating it in the acknowledgements is not required and would read as
  gratitude for something that is a licence condition; it belongs in the data
  availability statement instead, where it now is.
* **The advisor**, if he is not a co-author.

## AI usage, which is the section nobody had noticed

**This is the item the apparatus audit missed entirely and the brief did not
ask for.** ACP's submission page states that where AI tools were used to
generate parts of a manuscript, the usage must be described, in either the
methods section or the acknowledgements. It is not optional and it is not
covered by any of the three sections the audit named.

It applies here more than to most submissions. The 2026 reproduction — the
pipeline, the artefacts, the guards, the drafts and these statements — was
written in collaboration with an AI assistant across many sessions, and
`notes/decisions.md` is the record of that work. A description is therefore
required, it is not a formality, and it cannot be written as a disclaimer of
something marginal.

**What only Matt can supply.** The wording, and where it goes. The honest
version is specific rather than general: it says which parts were AI-written,
what was verified and how, and who is accountable for the result. This
repository is unusually well placed to make that statement checkable, because
the drift guards exist precisely so that no number in the prose is taken on
trust — which is the substance of what such a disclosure should convey.

## Interactive computing environment

ACP has a section for this and the repository has a reasonable claim on it: the
2023 thesis is a Jupyter notebook, `Duyst_Thesis_Final.ipynb`, committed and
preserved as submitted, and the 2026 pipeline is a scripted repository with a
registry of regeneration commands. ACP's data policy wants code deposited with a
DOI and cited in the reference list, which is the next item below.

## What is still needed and is not a section

**A deposit with a DOI.** ACP requires that code be deposited and cited in the
reference list using the received DOI, and a GitHub URL is not that.
`CITATION.cff` names `https://github.com/matt-duyst/Yangtze-Landcover-Methane`
and carries no DOI, and its ORCID field is a TODO. A Zenodo release of the
repository would supply both, and it is a ten-minute job that nothing in the
repository blocks — but it is Matt's account and Matt's release, so it is
recorded here rather than done.

**Not applicable, recorded so the list is complete.** Sample availability
(no physical samples), video supplement, team list, and the special issue
statement.

**Optional and worth a decision.** ACP invites a statement on inclusion in
global research, up to 100 words, where research used samples or data collected
in another country. This work analyses Chinese territory entirely through
Chinese and European public datasets, with no fieldwork and no local
collaboration, which is exactly the situation that statement exists to make
visible. Declining it is defensible; declining it without noticing is not.
