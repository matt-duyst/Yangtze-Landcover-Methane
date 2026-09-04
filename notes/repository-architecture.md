# Repository architecture

Design for the rebuilt repository, named `Yale-Masters-Thesis` when this was
written and `Yangtze-Landcover-Methane` since. Written before any code, so that
the structure follows from what the work needs rather than from what
accumulates.

The reference point is the peatland repository (`Visiting-Scholar-Research`),
which reached the standard this project is aiming for. Two of its choices are
deliberately not carried over, and those are marked below.

---

## Principles

**Raw data is fetched, not committed.** The pack is already 85.6 MiB before
any new data. GitHub rejects individual files above 100 MB. The 2018 TROPOMI
granules alone would exceed everything currently in the repository. Inputs are
acquired by script and verified against a manifest.

**Every drawn number reproduces from a fresh computation.** This is reachable
for the land-cover analysis. It is not reachable for the 2023 model results,
which have no checkpoint and no attributable outputs. Where it is not
reachable, the repository says so rather than implying otherwise.

**Numbers carry provenance labels.** Two sets of values will coexist: the 2023
thesis figures and the 2026 reproduction. Every table states which it is. The
2023 values are never silently replaced.

**Parameters are named, defaulted, and cited.** Every threshold in the rice
algorithm traces to a published source in a config file. A threshold with no
citation is a threshold nobody can defend.

**The notebook is not the pipeline.** Code lives in `src/`. Notebooks, if any,
demonstrate; they do not compute results.

---

## Layout

```
.
├── README.md
├── ERRATA.md
├── LICENSE
├── CITATION.cff
├── requirements.txt
├── .gitignore
├── config/
│   └── sources.yml            # dataset versions, URLs, bounds, covariates
│                              # pppm.yml and model.yml were NOT BUILT: there
│                              # is no rice algorithm and no model to configure
├── data/
│   ├── manifest.json          # checksums + versions for every fetched input
│   ├── raw/                   # gitignored, populated by fetch
│   ├── interim/               # gitignored
│   ├── processed/             # small derived tables, committed
│   └── reference/             # small committed inputs, not derived results
├── src/
│   ├── fetch/                 # one module per source
│   ├── landcover/             # urban zonal stats, rice zonal stats
│   ├── grid/                  # NOT PREDICTED: joins land cover onto the
│   │                          # methane lattice; see the note below
│   ├── methane/               # TROPOMI L2 read, QA filter, gridding, seasonal
│   ├── model/                 # AS BUILT: baselines and association tests.
│   │                          # No dataset, architecture, training or
│   │                          # inference; see the note below
│   ├── validation/            # NOT BUILT: absorbed into model/
│   └── figures/               # AS BUILT: style, output, one module per
│                              # figure. One figure so far.
├── scripts/                   # thin CLI entry points over src/
├── tests/
├── figures/                   # AS BUILT: generated PDF and PNG pairs,
│                              # committed, with captions in
│                              # README_fragments.md
├── notes/                     # reasoning, decisions, audit trail
├── writeup/
│   └── Duyst_Thesis.pdf
└── legacy/                    # AS BUILT: data/, figures/ and output/, each
                               # with a README. The notebook stayed at the
                               # repository root.
```

`data/reference/` holds small inputs that are committed rather than fetched,
and that are not derived from anything else in the repository. The provincial
boundary file is the example: it is public domain, a few hundred kilobytes, and
needed by almost every analysis, so fetching and verifying it would cost more
than it saves.

Two departures from the peatland layout, both upgrades:

- Peatland has no fetch script; acquisition is manual and documented in prose.
  That was adequate for one AmeriFlux archive. It is not adequate for five
  sources across three platforms, one of which has already changed version.
- Peatland records checksums as prose in a notes file. Here the manifest is
  machine-readable and verified by a test.

One departure that is a downgrade to accept: peatland has 32 test files
against 2 modules in `src/validation/`. Here validation is a first-class
concern and its module count will be closer to its test count.

---

## The fetch layer

One module per source, each exposing the same interface: report what it would
fetch, fetch it, verify it against the manifest.

This table is the plan. What was built is in the right-hand column, and it
differs enough that the plan should be read as a record of intent rather than a
description.

| source | product | planned route | as built |
|---|---|---|---|
| GAIA | annual impervious area, 30 m | direct download | built, via figshare; distributed version reaches 2021, not 2018 |
| Landsat | TM / ETM+ / OLI composites | Earth Engine | **not built.** No Earth Engine code exists anywhere in the repository |
| TROPOMI | Sentinel-5P L2 CH4, 2018 | Copernicus Data Space | built, but against the anonymous MEEO S3 mirror; Copernicus Data Space requires authentication and cannot run from a fresh clone |
| CCD-Rice | 30 m paddy rice, 1990–2016 | direct download | **not used** |
| APRA500 | 500 m rice, 2000–2021 | direct download | **not used** |
| NBS statistics | provincial sown area of rice | manual CSV | **not used** |
| GloRice | gridded paddy rice, 2017–2021 | *unplanned* | built, via figshare; supplies 28 of the 36 rice rows |
| Science Data Bank rice | classified rice, 10 m, by province | *unplanned* | built, anonymous Croissant route; supplies the analysis grid |
| GISA | global impervious surface, 30 m, 1972–2019 | *unplanned* | built, direct WHU bundle; the independent urban product the robustness test needed |
| SPAM | rice area | *unplanned* | committed as 8 rows, no fetch module |

The rice reimplementation this plan was built around never happened. Rice extent
comes from published products rather than from a Landsat reimplementation, which
removed the Earth Engine dependency and with it the parameter file the next
section describes.

Every fetch writes to `data/raw/`, which is gitignored, and appends to
`data/manifest.json`. Nothing downstream reads `data/raw/` without first
verifying the manifest.

### Manifest schema

```json
{
  "gaia_2018": {
    "product": "GAIA annual artificial impervious area",
    "version": "2024",
    "citation": "Gong et al. (2020), Remote Sensing of Environment 236, 111510",
    "url": "...",
    "retrieved": "2026-09-04",
    "files": [
      {"path": "gaia/GAIA_1985_2018.tif", "bytes": 0, "sha256": "..."}
    ],
    "notes": "Version distributed in 2026. The 2023 study used an earlier version; provincial areas are expected to differ."
  }
}
```

The version and citation fields are not decoration. GAIA's redistribution
under a later version is the specific mechanism by which a reproduction can
disagree with the thesis for reasons that are nobody's error, and the manifest
is where that is recorded.

A test asserts that every file present in `data/raw/` matches its manifest
entry, and that every manifest entry names a version and a citation.

**Not built.** No such test exists. Digests are verified at fetch time by
`src/fetch/common.py` where the source publishes one, which is the more useful
half, but nothing checks the manifest's own completeness and two entries
consequently carry no licence field. The Science Data Bank rice product, which
the analysis grid is built from, has no manifest entry at all.

---

## Order of work

Sequenced by certainty, highest first, so that early work is verifiable and
late work builds on settled ground.

**1. Scaffolding.** Structure, `LICENSE`, `CITATION.cff`, pinned
`requirements.txt`, `.gitignore`, `ERRATA.md`, thesis PDF into `writeup/`.
Restore the nine source `.jpg` files from git history into `legacy/`. Remove
the two 1-byte web-UI placeholders and the browser-collision filename.
Reconcile the two overlapping image directories.

**2. Urban reproduction.** Local, deterministic, no Earth Engine. GAIA raster
clipped to provincial boundaries, zonal statistics by province by year.
Reproduces the 12 urban values in Table 1. This is the smallest piece and the
one most likely to reproduce closely, which is why it goes first.

**3. Rice reimplementation.** ~~The largest piece of uncertainty. Requires
Earth Engine for Landsat time series. Every threshold in `config/pppm.yml`
with its citation. Validated against CCD-Rice for 2000 and 2010 and APRA500
for 2018, and compared against provincial sown-area statistics as the thesis
did.~~

**Not done, and deliberately.** Published rice products now exist at the
study's own resolution, so rice extent is taken from GloRice and from the
Science Data Bank 10 m classification rather than reimplemented from Landsat.
That removed the Earth Engine dependency, the parameter file, and the largest
piece of uncertainty in the plan, at the cost of no longer being a
reimplementation of the thesis's own method. The tradeoff is recorded in
`notes/decisions.md`; the constraints the published rasters carry, which the
plan did not anticipate, take up four of its sections.

**4. Methane layer.** TROPOMI L2 in ppb, not a rendered image. QA filtering,
with the count of valid retrievals over the study area reported as a headline
number. That count is the honest measure of what any model can learn from
2018, and it belongs in the README rather than buried.

**5. Model.** ~~Corrected implementation against the real methane field.
Pretrained backbone, augmentation applied jointly to input and target,
channel-appropriate preprocessing, seeded throughout.~~ Baselines are not
optional: a constant predictor, a linear model on urban and rice fraction, and
a geographically weighted regression. If the network does not beat all three,
that is the finding and it gets reported.

**The baselines were built first and the model was not built at all.** That
last sentence turned out to be the operative one. Under inverse-variance
weighting no land-cover model beats a queen-neighbour spatial null anywhere:
not on any of the three methane fields, at either sample size, under either
cross-validation scheme, with either of two independently built urban products
or either of two rice products. The exceptions are all unweighted and between
1.7 and 6.0 percent, and they recur in the same places on every field and every
predictor pair. Meanwhile a variable encoding only when each cell was observed
beats the null comfortably, so there is nothing for a network to improve on and
no sound field to fit it to.
The geographically weighted regression was replaced by a queen-neighbour
spatial null, which tests the same thing more directly. The finding is in the
README and the argument is in `notes/decisions.md`.

**6. Figures.** Generated by `src/figures/`, one module per figure, outputs
committed to `figures/`.

**Correct, and now built, with one addition the plan did not anticipate.** The
plan had figure modules and an output directory but no place for the things
every figure shares, so `src/figures/` holds two modules that are not figures:
`style.py`, carrying the venue standard, and `output.py`, which writes the
vector and raster forms from one figure object and verifies both before either
reaches its destination. A figure module returns a figure and never writes,
which is what makes the standard testable rather than aspirational.

One figure exists so far, of nine planned. The 2023 ArcGIS exports in
`legacy/figures/` remain what they were and are not a substitute, since their
source projects are gone and there is no vector form to recover.

---

## Testing

Mirrors `src/`, one test module per source module, as peatland does.

Four categories worth naming, because they are not the same kind of test:

- **Unit.** Pure functions: index computation, threshold application,
  coordinate handling, area arithmetic.
- **Manifest.** Every fetched file matches its recorded checksum; every entry
  carries a version and a citation. *Not built; see the fetch section above.*
- **Reproduction.** Committed processed tables regenerate from committed
  inputs. This is what makes "every drawn number reproduces" enforceable
  rather than aspirational. *Built, and it is the largest category: the
  committed composite, analysis grid, baselines and confounder tables each
  have a test module reading them back.*
- **Figure.** Each figure module runs and produces an output of the expected
  shape. *Built, and it turned out to be two categories rather than one. A
  figure module is tested by building a figure from constructed data and
  asserting on the object, with no filesystem involved. The export path is
  tested by its refusals: each venue limit is checked by the failure it is
  supposed to cause and by the absence of any file afterwards.*

Two categories the plan did not anticipate turned out to matter more than the
figure tests it did. **Structural** tests assert that a constraint cannot be
violated rather than that it happens not to be: that a cell with no soundings
cannot be constructed, that a covariate mean is unreachable without its own
count, that a missing predictor is dropped or raised on and never imputed.
**Negative-result** tests pin findings that a later change could quietly
reverse into something more flattering, and make it argue with a test first.

Fixtures are built in memory. No test reads from `data/raw/`, so the suite
runs on a clone with no data fetched.

---

## What the repository will not claim

Recorded here so it is decided once rather than argued at the end.

It will not claim that the 2023 model results are reproduced. They cannot be:
no checkpoint exists, and the stored outputs cannot be attributed to the
committed code.

It will not claim that predicted XCH4 fields represent emissions. They
represent a learned spatial association with land cover, and the distinction
is stated wherever a prediction appears.

It will not present the 2026 numbers as corrections to the 2023 numbers. They
are a second computation under documented conditions, reported alongside.

It will not report a validation metric against a dataset measuring a different
quantity. Comparisons against emission inventories are directional
consistency checks and are labelled as such.
