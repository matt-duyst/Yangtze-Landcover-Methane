# The Yangtze River Delta as a case study — verified draft

**This is a verification pass over a draft written from recall, not polished
prose.** Every claim carries a status tag so a later pass can act on it:

* `[record]` — verified against this repository's own grounding records
* `[source]` — verified against the cited source itself
* `[measured]` — measured here, over this domain, in this pass
* `[unverified]` — could not be verified from the records; kept and marked
  rather than dropped
* `[CORRECTED]` — the recalled draft said something the records contradict

Where a figure has a resolver it carries one, and the file is in
`scripts/verify_claims.py`'s `SCANNED` list so that those cannot drift.

## The region

The Yangtze River Delta comprises Shanghai municipality and the provinces of
Jiangsu, Zhejiang and Anhui `[record]`. The analysis lattice spans 26.95° to
35.2° north and 114.8° to 122.55° east `[record]`, which is
918 km north to south and 739 km east to west at the domain's centre
`[measured]`. The recalled draft's "some 750 kilometres" inland is right to
within two percent.

The region is not physiographically uniform. Northern Anhui and northern
Jiangsu lie on the Huai River plain, flat alluvial farmland at low elevation
`[unverified]` — geographically uncontroversial but stated in no record. The
centre is the lower Yangtze floodplain, paddy, canals, lakes and aquaculture
ponds, containing Lake Tai and the Yangtze's tidal reach `[unverified]`.
Southern Zhejiang rises into hills, and the satellite record's largest
continuous gap lies there: a connected block of 47 cells whose median elevation
is 552 m and which reaches 1,119 m `[record]`. The records place it on "the
southern edge of the domain" rather than naming the province, so the attribution
to southern Zhejiang is an inference from the geography `[record]`.

The four units differ in scale by more than an order of magnitude. Measured on
this project's own boundaries: Shanghai 6,746 km², Jiangsu 100,091 km²,
Zhejiang 101,337 km², Anhui 140,194 km² `[measured]`. **Anhui is 20.8 times
Shanghai** `[measured]`, so the recalled "more than twenty times" holds; but
"some six thousand square kilometres" for Shanghai understates it, and the
records elsewhere carry a published 6,341 km² against this 6,746, so the two
differ by boundary definition `[record]`.

Most Chinese statistics underpinning emission inventories are reported by
province `[unverified]`, so a provincial figure means something different in
Shanghai than in Anhui.

## Urbanisation

Impervious surface across the four provinces rose from
16,387<!--#urban.gaia_2000--> km² in 2000 to
49,348<!--#urban.gaia_2018--> km² in 2018 as reproduced from GAIA, and from
19,787<!--#urban.gisa_2000--> to
39,532<!--#urban.gisa_2018--> from GISA `[record]`. GISA is 19.9 percent
smaller in 2018 and 20.7 percent larger in 2000 `[record]`, and the growth
factors are 3.0<!--#urban.gaia_factor--> against
2.0<!--#urban.gisa_factor--> `[record]`. So the endpoints differ by about a
fifth and the factors by half, as the recalled draft said.

**`[CORRECTED]` The recalled draft said growth "concentrated along the
Shanghai–Suzhou–Nanjing corridor and around the provincial capitals" and
attributed it to "residential and industrial expansion driven by investment and
municipal land revenue rather than by population growth".** Neither claim
appears anywhere in the records: searching for the corridor, for land revenue
and for investment returns nothing. Both are `[unverified]` and the second is
an attribution to a literature this project has not read. The spatial claim is
cheaply measurable from the committed rasters and is not measured here.

That the *composition* of urban land matters for methane and is invisible in a
map of impervious extent is supported: the inventories allocate downstream gas,
wastewater treatment and stationary combustion on a single population surface,
so they cannot separate them by construction `[source]`.

## Rice

Rice is grown across the plains of all four provinces, predominantly as a single
mid-season crop in the north and centre, with double cropping persisting in
parts of Zhejiang and southern Anhui `[unverified]`. The distinction matters for
emission rather than for area, because a double-cropped field is flooded twice
`[unverified]`.

**`[unverified]`** The recalled cropping calendar — middle-season transplanting
between roughly day 130 and 180, maturity between day 240 and 280 — appears in
no record. It should be sourced or dropped.

Water regime is the central control. A long-term double-rice experiment in China
measured net global warming potentials of 22,497, 8,895 and 1,646 kg CO₂-e per
hectare per year under continuous flooding, flooding with midseason drainage,
and irrigation for flooding only at transplanting and tillering — **a spread of
13.7 across three regimes on the same soil under the same crop** `[record]`.

**`[CORRECTED]` and this is the draft's most serious error.** The recalled draft
attributed the eddy-covariance ranges — 7 to 32 against 76 to 142 kg CH₄-C per
hectare — to "Chinese paddy". They are Runkle et al. (2019) and **the site is in
Arkansas**, which the register records explicitly "as a limit on transfer"
`[record]`. The draft also called the difference "roughly an order of
magnitude"; the register declines to state a single ratio because **"the ratio
between them runs from 2.4 to 20 depending on which ends are taken"** `[record]`.
Both the country and the ratio must change.

Two further management terms move emissions comparably. Straw incorporation
raises them **five-fold** against burning `[record]`, and China banned open
residue burning in 2008 with straw return becoming the standard alternative
`[record]`. Nitrogen application is non-monotonic, raising methane at low rates
and suppressing it at higher ones `[record]`.

The region has been changing in ways that oppose each other. From 1990 to 2015
the sown area of double-cropping rice in southern China decreased by
61,054.5 km² while single-cropping increased by 20,110.7 km², the multiple
cropping index fell from 148.3 to 129.3 percent, and "the most dramatic changes
occurred in the Middle-Lower Yangtze Plain" `[record]`. **These are sown areas,
which the rice record distinguishes from planted area** `[record]` — a
distinction the recalled draft dropped. **`[CORRECTED]`** An earlier version of this file
reported a synthesis of 416 field samples giving 252.17 against 146.02 kg per
hectare, tagged `[record]`. That was verified against `notes/grounding-yrd.md`,
which carries the figures, while `notes/references.md` records the same source
as "a source that could not be verified for the thing it was cited for" — the
article is closed, no abstract is indexed, and the entry states its figures
**are not written anywhere in this repository**. Confirmed closed again on 17
September 2026. **The figures are removed rather than retagged**, and what
survives is only the direction: per-hectare emissions are reported to have risen
between the 2000s and the 2010s, from a source this project cannot verify
`[unverified]`. Area fell and
intensity rose, and the literature reporting the second does not explain it
`[record]`.

## The other sources

Six further sources sit in this domain, making seven with rice `[record]`. The
inventory this project holds carries eight sectors nationally `[record]`.

**Coal** is the largest by inventory. The Huainan–Huaibei coalfields occupy
northern Anhui `[record]`. In domain the inventory places
2035.1<!--#change.coal_total--> Gg a⁻¹ across
22<!--#change.coal_cells--> cells `[measured]`, and mine coordinates are
published — 116 located mines in domain with monthly 2018 emissions `[record]`.

**`[CORRECTED]`** The recalled draft put coal at "approaching forty percent of
the domain's inventoried total". The measured 39.59 percent is its share of the
**five sectors aggregated onto the lattice**, not of the whole inventory, which
carries eight `[measured]`. The denominator has to be stated.

**Aquaculture** is the source no inventory carries `[record]`. Chinese
freshwater aquaculture ponds emit **1.60 ± 0.62 Tg CH₄ a⁻¹** `[record]`, so the
recalled "on the order of two teragrams" is high; the recorded figure rounds to
1.6. Ponds are interleaved with paddy, spectrally similar, and mapped at 10 m in
a national product `[record]`.

**`[CORRECTED]`** The recalled draft said the region holds "roughly a quarter of
the national pond area", which is the cited 26 percent figure. **This project
measured 35.6 percent of national pond area inside the four provinces** from the
pond product on disk `[record]`. The measurement should replace the citation,
and the gap between them is a third.

On pond management the record gives a sharper and differently-denominated
figure than the draft: GHG emission intensity **per unit of fish production** in
traditional earthen ponds was **197 times** that of in-pond raceway systems
`[record]`. The recalled "two orders of magnitude" is roughly right but the
denominator is production, not area, and the draft's surrounding text is about
area.

**Landfill** dominates urban methane where measured: **59 to 62 percent** of the
total in US cities and the principal cause of an 80 percent underestimate
`[record]`, with gas collection averaging 38 percent against a reported 70
`[source]`. China's waste sector shifted from landfill toward incineration —
52 percent landfill against 45 percent incineration `[record]` — and China
launched the Waste-Free City initiative in 2018 `[record]`. Landfills are point
sources but no open dataset gives their positions in this domain `[record]`.

**Wastewater** is smaller and better located: 422 plant coordinates lie inside
the lattice `[record]`. The recalled draft said "for the four provinces"; the
record says inside the lattice, which is not the same boundary.

**Urban gas distribution** pipeline length grew roughly threefold nationally,
from 298.6 to 935.6 million metres over 2010 to 2019 `[record]`, and length is
published for 347 prefecture-level cities `[record]`.

**`[CORRECTED]`** The recalled draft said ethane-tracer measurements "suggest
urban leakage rates several times higher than inventories assume". What is
verified is that the study finds YRD urban natural-gas methane **underestimated**
`[record]`. The magnitudes behind "several times" — 3.5 percent against 0.2
percent — are recorded as **not verified**, the article being paywalled and the
only source a press summary `[record]`. The direction may be stated; the
magnitude may not.

**`[CORRECTED]` Natural wetland.** The recalled draft said it "cannot currently
be located in this domain at all". The records locate it: coastal and estuarine,
around Chongming Dongtan and Hangzhou Bay `[record]`. What is unfixed is not the
position but the sign — invasive *Spartina alterniflora* turned a Yangtze
Estuary salt marsh **from a CH₄ sink into a source**, so "the sign of the wetland
term is not even fixed, let alone its magnitude" `[record]`. That is a stronger
and more useful statement than the one recalled.

## Meteorology, and why the season matters twice

The region has a monsoon climate with persistent summer cloud `[unverified]`.

**That cloud governs the satellite record, and it is measured here.** Of the
110,920 soundings this study grids, June yields 4.96 percent, July 4.55 and
August 5.00, while **October alone yields 30.82 percent** `[measured]`. January
through March yield nothing at all, the record beginning 30 April `[record]`. So
the season when rice emits most is the season the instrument sees least, and the
recalled "under five percent each" and "roughly thirty percent" both hold.

Wind governs how emission appears as concentration. At the domain's median
wind of 1.41 m s⁻¹ air crosses a 25 km cell in about five hours `[measured]`,
so "a few hours" holds at the low end; the committed covariates are vector
means, which understate the speed `[record]`.

Urban expansion across the region between 2001 and 2021 raised 2 m temperature
and planetary boundary layer height and reduced wind speed `[record]`, changing
how a given emission appears in a column independently of the emission.

## What has been measured here

**`[CORRECTED]` on two counts.** A **tower-based Bayesian inversion** of the
Yangtze River Delta for 2018 attributed **seasonal variability** to agricultural
activity `[record]`. The recalled draft said it found "agricultural soils the
largest single contributor", which is a different and stronger claim — a
contribution to the total rather than a driver of its seasonality — and it said
the tower is in Nanjing, which **no record states** `[unverified]`.

Lin'an in Zhejiang is a WMO/GAW **regional background** station and **one of
three** such stations China operates, with Shangdianzi and Longfengshan
`[record]`. Its 2011 annual mean of 1,942 ppb ran 81 ppb above Waliguan, China's
global station `[record]` — a figure the recalled draft omitted and which
establishes the domain as high-signal.

Three surface stations operate around Suzhou `[record]`. The Hefei TCCON station
is the only column station in the domain, Xianghe being 505 km north of the
lattice `[record]`.

**`[unverified]`** and worth dropping: the recalled claim that "the region is
better instrumented than most of China". Nothing in the records compares this
region's instrumentation to other regions.

**`[record]` and omitted by the draft:** Sun et al. (2016) at the Zhuanghang
Experimental Station, 30°53′N 121°23′E, is **the only in-domain flux measurement
in any of the three grounding records**. A background section on what has been
measured here should not leave out the one flux measurement inside the lattice.

## What is not known

No landfill locations are openly published for this domain `[record]`. No
emission factor per unit pond area is established for aquaculture `[record]`.
Water regime, the term that moves rice emissions most, is not mapped for this
region `[record]`. The inventories allocate three urban sectors on a single
population surface and cannot distinguish them by construction `[source]`. And
the wetland term's sign is not fixed `[record]`.
