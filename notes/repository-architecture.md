# Repository architecture

Design for the rebuilt `Yale-Masters-Thesis` repository. Written before any
code, so that the structure follows from what the work needs rather than from
what accumulates.

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
│   ├── sources.yml            # dataset versions, URLs, spatial/temporal bounds
│   ├── pppm.yml               # rice algorithm parameters, each with a citation
│   └── model.yml              # architecture, training, augmentation settings
├── data/
│   ├── manifest.json          # checksums + versions for every fetched input
│   ├── raw/                   # gitignored, populated by fetch
│   ├── interim/               # gitignored
│   ├── processed/             # small derived tables, committed
│   └── reference/             # small committed inputs, not derived results
├── src/
│   ├── fetch/                 # one module per source
│   ├── landcover/             # urban zonal stats, rice reimplementation
│   ├── methane/               # TROPOMI L2 read, QA filter, gridding
│   ├── model/                 # dataset, architecture, training, inference
│   ├── validation/            # metrics, baselines, cross-product comparison
│   └── figures/               # one module per figure
├── scripts/                   # thin CLI entry points over src/
├── tests/
├── figures/                   # generated PNGs, committed
├── notes/                     # reasoning, decisions, audit trail
├── writeup/
│   └── Duyst_Thesis.pdf
└── legacy/
    ├── Duyst_Thesis_Final.ipynb
    └── README.md              # what this is and why it is preserved
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

| source | product | route | notes |
|---|---|---|---|
| GAIA | annual impervious area, 30 m, 1985–2018 | direct download | current distribution is a later version than the thesis used; version pinned in `sources.yml` and the difference expected |
| Landsat | TM / ETM+ / OLI composites | Earth Engine | required only for the rice reimplementation |
| TROPOMI | Sentinel-5P L2 CH4, 2018 | Copernicus Data Space | Earth Engine's L3 CH4 collection begins February 2019 and cannot serve the study year |
| CCD-Rice | 30 m paddy rice, China, 1990–2016 | direct download | independent reference for 2000 and 2010 |
| APRA500 | 500 m rice, Asian monsoon, 2000–2021 | direct download | independent reference for 2018, where CCD-Rice stops |
| NBS statistics | provincial sown area of rice | manual, committed as CSV | small, stable, and the only input that is genuinely a table |

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

**3. Rice reimplementation.** The largest piece of uncertainty. Requires
Earth Engine for Landsat time series. Every threshold in `config/pppm.yml`
with its citation. Validated against CCD-Rice for 2000 and 2010 and APRA500
for 2018, and compared against provincial sown-area statistics as the thesis
did. Expected to differ from the 2023 values; the difference is documented,
not reconciled away.

**4. Methane layer.** TROPOMI L2 in ppb, not a rendered image. QA filtering,
with the count of valid retrievals over the study area reported as a headline
number. That count is the honest measure of what any model can learn from
2018, and it belongs in the README rather than buried.

**5. Model.** Corrected implementation against the real methane field.
Pretrained backbone, augmentation applied jointly to input and target,
channel-appropriate preprocessing, seeded throughout. Baselines are not
optional: a constant predictor, a linear model on urban and rice fraction, and
a geographically weighted regression. If the network does not beat all three,
that is the finding and it gets reported.

**6. Figures.** Generated by `src/figures/`, one module per figure, outputs
committed to `figures/`. Captions follow the conventions established on the
previous project.

---

## Testing

Mirrors `src/`, one test module per source module, as peatland does.

Four categories worth naming, because they are not the same kind of test:

- **Unit.** Pure functions: index computation, threshold application,
  coordinate handling, area arithmetic.
- **Manifest.** Every fetched file matches its recorded checksum; every entry
  carries a version and a citation.
- **Reproduction.** Committed processed tables regenerate from committed
  inputs. This is what makes "every drawn number reproduces" enforceable
  rather than aspirational.
- **Figure.** Each figure module runs and produces an output of the expected
  shape, following peatland's `test_<figure>_figure.py` pattern.

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
