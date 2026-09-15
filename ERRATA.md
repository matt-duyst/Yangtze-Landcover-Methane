# Errata

Corrections to *Urban-Methane Transfers (2000 – 2018): A Convolutional Neural
Network (CNN) Approach at Forecasting Historical XCH4 Emissions through Urban
Boundaries and Paddied Rice Extents Along China's YRD* (Yale School of the
Environment, MESc, April 28, 2023).

The thesis was never published or submitted for publication. This document
records defects found during a 2026 audit undertaken to prepare the work for
publication. Items are grouped by whether they affect the written document, the
implementation, or claims that later literature has superseded.

Each item that was checked against the thesis PDF, the committed notebook or an
artefact committed here carries a *Verified by* line naming the method, so that
the check can be repeated rather than taken on trust. The four items in Section 5
carry no such line, and deliberately so: each rests on published literature
described in the item itself rather than on anything in this repository, and
asserting a method for them would claim more than was done.

No quantitative model result is retracted here, because the thesis reports
none. Section 5.2 states that mean squared error was calculated but gives no
value. The loss figures discussed below exist only in the notebook.

---

## 1. Figures

### 1.1 Figure 4.7 does not show model predictions

Figure 4.7(a) "XCH4 Predicted Boundaries (2000)" and Figure 4.7(b) "XCH4
Predicted Boundaries (2010)" are the same image as Figure 4.5(a) "Raw XCH4
emissions".

All three placements resolve to a single PDF object (object 180), placed once
on page 21 and twice on page 22. The decoded pixel arrays are byte-identical
across all three (SHA-256 `aef18140…`), as are their soft masks
(`97d90bf4…`). All three are 271 × 211, RGB, 8 bits per channel. All three
carry the same title block, rendered in the image itself:

> Raw TROPOMI XCH4 Concentrations (2018)

Section 4.7 therefore contains no result. The study's stated novel
contribution, described in Section 1.2 as the first encoder-decoder
architecture to predict historical XCH4 from urban and paddy rice extents, is
not evidenced anywhere in the document.

Three further artifacts are consistent with no prediction image having been
produced:

- The notebook cell that would generate the 2000 and 2010 predictions failed
  at runtime with `NameError: name 'data_2010' is not defined`, downstream of
  `OSError: [Errno 107] Transport endpoint is not connected` (a dropped
  Google Drive mount). The failure is preserved in the committed notebook's
  stored output.
- The repository README links to `/assets/XCH_4_Predicted_2000.png` and
  `/assets/XCH_4_Predicted_2010.png`. These are the only two image links in
  that file whose targets do not exist in the repository under any spelling.
- No model checkpoint (`.pth`, `.pt`, `.ckpt`) has ever existed in the
  repository's git history.

None of these establishes *why* the raw observation was placed three times. A
LaTeX include pointing at the wrong file produces this outcome, and so does
inserting a placeholder intended to be replaced. The PDF records what was
placed, not the intent behind it.

*Verified by:* extraction of all embedded images from the thesis PDF, with
per-image PDF object IDs and SHA-256 hashes of decoded pixel arrays.

### 1.2 The Figure 4.7 caption contradicts the method

The caption reads that the estimated boundaries are based on recorded urban
and paddied rice extents "in the year 2018". The section heading (4.7) and
Section 5.2 both state that the inputs were the recorded extents for 2000 and
2010. The caption is wrong; the method described in the body is correct.

*Verified by:* reading the Figure 4.7 caption in the thesis PDF against the
section heading and the input years stated in Section 5.2.

---

## 2. Numerical and arithmetic corrections

### 2.1 Zhejiang urban expansion multiplier

Section 5.1 states that Zhejiang experienced an urban expansion rate six times
greater than its recorded 2000 extent. Table 1 gives Zhejiang at 1,752 km² in
2000 and 6,731 km² in 2010, a factor of 3.84.

The neighbouring claims in the same paragraph do reproduce from Table 1: Anhui
doubles (2.04), Jiangsu triples (3.34), and the full-span Jiangsu figure of
more than sixfold (3,008 to 19,430, a factor of 6.46) is correct.

*Verified by:* recomputing each ratio from the provincial values in Table 1 of
the thesis PDF; 6,731 over 1,752 is 3.84 against the stated sixfold.

### 2.2 2010 YRD urban total

Section 5.1 gives the 2010 YRD total as 24,830 km². The four provincial values
in Table 1 sum to 24,831 (3,310 + 6,731 + 4,748 + 10,042). The derived change
figures reported downstream (16,533; 24,895; 41,428 km²) are internally
consistent with 24,830.

*Verified by:* summing the four provincial 2010 values in Table 1, which give
24,831 against the 24,830 reported in Section 5.1.

### 2.3 Yangtze River extent

Section 1.5 states that the Yangtze River "extends roughly 1.8 million km2".
A river's extent is a length and cannot be given in square kilometres, so the
figure and its units do not describe the same quantity. The value is of the
order usually quoted for the basin's drainage area rather than for the river
itself, but no citable source for the basin area was found for this correction,
so the claim here is confined to the unit mismatch, which is checkable from the
sentence alone. The thesis attributes the figure to Zhu et al. 2020; whether
that source gives it as a basin area, which would make the error one of
description rather than of number, was not established.

*Verified by:* reading the figure and its units in Section 1.5; 1.8 million km2
is an area, and the sentence attributes it to the river's extent.

### 2.4 Spatial resolution notation

TROPOMI XCH4 spatial resolution is given throughout as "7km2 x 7km2". The
correct notation is 7 km × 7 km: the figure describes the dimensions of a
ground pixel, not an area, and squaring both terms states an area of 49 km2 as
though it were 7 km2 squared. The instrument's design nadir ground pixel for
the SWIR band is 7 × 7 km (Veefkind et al., 2012, Remote Sensing of Environment
120, 70-83, doi:10.1016/j.rse.2011.09.027), which is the correct figure for the
2018 study period.

An earlier version of this item added that the nadir resolution was refined to
approximately 7 × 5.5 km in August 2019. That refinement is described in mission
documentation rather than in a citable work, and no source for the date or the
exact dimensions was found, so the detail is withdrawn. It would in any case be
context rather than a correction, since any post-2018 change postdates the data
used here.

*Verified by:* full-text search of the thesis PDF for the resolution statement,
which uses the squared form throughout rather than at one occurrence.

---

## 3. Implementation defects

These concern the committed notebook rather than the written thesis. They were
found by static inspection; the notebook was not executed.

### 3.1 The model's target was a rendered figure, not a methane field

The training target is `XCH4_2018.jpg`, an 8-bit grayscale JPEG
(PIL mode `L`, 5950 × 4016). It is a colour-ramp choropleth flattened to
grayscale, not a concentration raster. Of its pixels, 81.5% hold the single
value 255, corresponding to white page background.

Two consequences follow. Grayscale conversion of a red-orange-yellow-green
colour ramp is not monotonic in the underlying quantity, so mean squared error
on these values does not correspond to error in parts per billion. And the
source is JPEG, so lossy compression introduces spurious intermediate values
at class boundaries in the dependent variable.

The urban and rice inputs are likewise near-binary masks read from JPEG
(urban: background 240, foreground 0; rice: background 255, foreground 0),
each carrying a compression fringe of 0.2% to 0.9% of pixels at ±1.

*Verified by:* opening the committed `legacy/data/XCH4_2018.jpg` and reading its
mode, dimensions and value histogram: PIL mode L, 5950 by 4016, and 81.5 percent
of pixels at 255.

### 3.2 Augmentation was applied to inputs but not targets

In the dataset class, the transform pipeline is applied to the stacked input
tensor only; the target is returned untransformed. The training pipeline
includes `RandomHorizontalFlip`, `RandomVerticalFlip`, and
`RandomRotation(30)`. Each training pair is therefore geometrically
misaligned between input and target.

The validation pipeline applies only `ToTensor` and `Normalize`, so validation
pairs remain aligned. This accounts for the otherwise anomalous ordering of
the stored losses, in which validation loss (2889.67) sits below final
training loss (4031.66).

*Verified by:* reading the dataset class and both transform pipelines in the
committed notebook, and comparing the stored training and validation losses.

### 3.3 The backbone was randomly initialised and then frozen

The model instantiates `models.resnet50()` with no weights argument, so the
encoder is randomly initialised rather than pretrained, and then applies
`requires_grad = False` to all parameters existing at that point, which is the
backbone. Only the ASPP module and decoder train.

Section 3.3, step 2, of the thesis states that backbone networks are usually
pretrained on a large-scale classification dataset such as ImageNet. The
implementation does not do this. Inputs are nonetheless normalised with
ImageNet channel statistics. Normalisation constants are chosen to match the
distribution a network was pretrained on, so carrying ImageNet's over to a
randomly initialised encoder applies a transformation with nothing to match it
to. This is a practitioner convention rather than a theorem and is stated here
as such; no citable source is offered for it, and the defect the item rests on
is the frozen random backbone above, which is checkable from the notebook.

*Verified by:* reading the model instantiation and the `requires_grad` loop in
the committed notebook, against the pretraining described in Section 3.3.

### 3.4 Colour augmentation applied to thematic channels

`ColorJitter` with saturation and hue adjustment is applied to a three-channel
input whose channels are basemap, urban mask, and rice mask. Hue rotation
mixes information between the urban and rice channels.

*Verified by:* reading the augmentation pipeline in the committed notebook
against the three channels the dataset class stacks.

### 3.5 Stored outputs cannot be attributed to the committed code

Every code cell in the notebook has `execution_count: null` while 22 cells
retain stored outputs. Nothing in the file establishes that any stored output
was produced by the source beside it.

This is demonstrable rather than merely possible: the dataset class returns a
tensor via `torch.from_numpy`, and the training cell then applies
`transforms.ToTensor()` to it. `ToTensor` raises `TypeError` on a tensor
input. The stored output nonetheless shows ten epochs completing. These
facts cannot all describe a single run.

Accordingly, the loss values in the notebook should not be cited as results
of the code as committed.

*Verified by:* parsing the committed notebook's JSON, which gives 37 code cells
with `execution_count` null and 22 retaining stored outputs; and tracing the
tensor the dataset class returns into `transforms.ToTensor()`.

### 3.6 Constant-predictor comparison

For context on the magnitude of the stored losses, the constant-predictor
baseline was computed on a reconstruction of the notebook's own crop sampling
(5,000 training crops and 1,000 testing crops, drawn under the same
province-inclusion and exclusion rules):

| | training crops | testing crops |
|---|---|---|
| best pooled constant | 217.94 | 208.30 |
| MSE of that constant | 3340.03 | 3198.57 |
| per-crop own-mean MSE, averaged | 2236.31 | 2113.14 |

Against these, the stored training loss of 4031.66 is worse than both
baselines, and the stored validation loss of 2889.67 is worse than the
per-crop baseline and 9.7% better than the pooled one.

This is a comparison of numbers, not a verdict on the model, for the reason
given in 3.5. It is recorded because the stored losses are otherwise easy to
read as evidence of fit.

*Verified by:* recomputing the constant-predictor baselines on a reconstruction
of the notebook's own crop sampling, under its province-inclusion rules.

---

## 4. Method description inconsistent with implementation

### 4.1 Section 3.3 describes a masked autoencoder

Section 3.3 describes the network as randomly masking patches of the urban and
rice inputs and reconstructing them, citing He et al. (2022,
doi:10.1109/CVPR52688.2022.01553) throughout,
including that work's Transformer-block encoder and its loss computed on
masked patches.

The implementation performs supervised segmentation: DeepLabv3+ with a
ResNet50 backbone, one output channel, no final activation, and `nn.MSELoss`
against an XCH4 target. No masking occurs anywhere in the notebook. The
implementation is the more defensible artifact; the description should be
rewritten to match it.

*Verified by:* reading Section 3.3 of the thesis PDF against the model, the loss
and the absence of any masking step in the committed notebook.

### 4.2 Scale invariance claim

Section 3.3 states that the resolution difference between Landsat (30 m) and
Sentinel-5P (approximately 7 km) can be ignored because CNNs are scale and
translation invariant. Convolutional networks are approximately translation
*equivariant*, and are not scale invariant. The distinction is the whole of the
objection: equivariance means a shifted input produces a correspondingly shifted
feature map, which is a property of the convolution itself (Cohen and Welling,
2016, doi:10.48550/arXiv.1602.07576), while invariance means the output does not
change at all, which convolutional networks achieve only approximately and
which fails even for small translations and rescalings (Azulay and Weiss, 2018,
doi:10.48550/arXiv.1805.12177). Neither property licenses ignoring a
two-order-of-magnitude difference in ground sampling distance. The resampling
actually performed, and the limitation it imposes, should be stated instead.

*Verified by:* reading the scale-invariance claim in Section 3.3 against the two
sensor resolutions as the thesis itself states them.

---

## 5. Claims superseded by subsequent literature

### 5.1 Availability of reference data

Section 5.2 states that validation would require reference data that, to the
author's knowledge, does not exist. Four products published since the thesis
provide it, and they validate different things, which matters because
conflating them would repeat the category error this reproduction spent
considerable effort establishing.

Two are rice maps and can validate a rice layer directly. CCD-Rice gives paddy
rice distribution for China at 30 m from 1990 to 2016 (Shen et al., 2025, Earth
System Science Data 17, 2193-2216, doi:10.5194/essd-17-2193-2025). Han et al.
give annual paddy rice planting area and cropping intensity for the Asian
monsoon region from 2000 to 2020 (2022, Agricultural Systems 200, 103437,
doi:10.1016/j.agsy.2022.103437).

Two are emission products and cannot validate a rice map or a concentration
field, only an emission estimate. The Global Rice Paddy Inventory gives methane
emissions from rice at 0.1 degree and monthly resolution (Chen et al., 2025,
Earth's Future 13, e2024EF005479, doi:10.1029/2024EF005479). And a satellite
inversion of methane over China's principal rice-growing region demonstrates the
regional constraint the thesis assumed impossible (Liang et al., 2024,
Environmental Science & Technology 58, 23127-23137,
doi:10.1021/acs.est.4c09822).

A paddy rice map validates a rice layer. An emission inventory validates neither
a rice map nor a column concentration field, because it is a different quantity
from either.

### 5.2 Causal attribution of XCH4 to rice paddies

Section 5.1 states that the largest driver of XCH4 hotspots appears to be
paddy rice fields. A published Matters Arising responding to one of the
thesis's two pillar references argues that local XCH4 variation is driven
primarily by advected large-scale flux signals rather than local emission, and
that spatial correlations between rice extent and XCH4 are confounded by
cross-correlation with other sources sharing similar spatial structure. That
exchange is not cited in the thesis. Causal language in Section 5.1 should be
replaced with language describing spatial association.

The exchange is Zhang et al. (2020, Nature Communications 11, 554,
doi:10.1038/s41467-019-14155-5), the pillar reference; Zeng et al. (2021,
Nature Communications 12, 1163, doi:10.1038/s41467-021-21434-7), the Matters
Arising; and Zhang et al. (2021, Nature Communications 12, 1189,
doi:10.1038/s41467-021-21437-4), the reply. All three are in
`notes/references.md`.

**A second and independent objection, added 15 September 2026, and it concerns
magnitude rather than causality.** The reproduction has since converted an
emission to a column enhancement, using the closed form the operational
inversion literature uses and this domain's own wind, and the result bears on
this item directly.

The inventory's rice emission for this domain, spread over the cells that carry
rice, implies a column enhancement of
0.119<!--#change.rice_enhancement--> ppb per cell. The whole 5th-to-95th
percentile range of impervious fraction implies
0.410<!--#change.xsec_contrast--> ppb. The composite's median per-cell standard
error is 1.98<!--#change.se_median--> ppb and the field's between-cell standard
deviation is 14.86<!--#field.sd_operational--> ppb. **So the emission signal
that land-cover extent proxies over this domain is between a fifth and a
twentieth of the noise on a single cell, and the largest correlation it could
produce is |r| = 0.0084<!--#change.r_max-->.**

What that adds to the item is a statement about what was achievable rather than
about what was done: **a spatial association between land-cover extent and the
column field at this resolution could not have been the emission signal, at any
level of care in the analysis.** It is therefore not only that causal language
should become associational language; the association itself, had it been
measured soundly, would have been too small to detect.

**Three qualifications, because this is a bound and not a measurement.** It is
a bottom-up expectation, computed from an inventory whose urban sectors are
allocated on population rather than on urban land, so the rate it rests on
expresses what an inventory predicts and not what the atmosphere does. It does
not say the observing system is insensitive: the same conversion gives
5.80<!--#change.coal_enhancement--> ppb for a cell of the inventory's coal
sector, which is 2.9<!--#change.coal_multiple--> times the per-cell error, so a
concentrated source of that size is plainly visible. And it is independent of
items 3.1 through 3.6 above, which concern what the thesis's model was actually
fitted to; those stand on their own and this neither replaces nor strengthens
them.

### 5.3 Urban methane attributed to natural gas vehicles

Sections 1.1 and 1.5 attribute urban methane to natural gas vehicles, with a
framing of retrofitted vehicles and faulty tailpipes. **The attribution has
substantial support and the mechanism does not.** Those are separate claims and
an earlier version of this item did not separate them.

*The attribution.* Three independent measurements bear on it and they are
consistent with one another. The source the thesis cites measured real-world
emissions from heavy-duty natural gas vehicles in China and found them about 90
percent above the applicable emission limits, concluding that switching to
natural gas vehicles has produced a net increase in greenhouse gas emissions
since 2000 (Da Pan et al., 2020, Nature Communications 11, 4588,
doi:10.1038/s41467-020-18141-0). Mobile measurements in Hangzhou, a Yangtze
River Delta megacity, found the natural gas distribution system there to be a
low emitter (Zhao et al., 2024, ACS ES&T Air 1, 1511-1518,
doi:10.1021/acsestair.4c00068). And an ethane-tracer study of ten years of
atmospheric measurements finds methane emissions from natural gas consumption in
the Yangtze River Delta cities of China to be underestimated (Zhao et al., 2026,
Nature Cities, doi:10.1038/s44284-026-00504-1). The three reconcile if the
leakage is in end use and in transportation rather than in distribution
pipelines, which is the reading the Hangzhou measurement and the vehicle
measurement jointly support. So the thesis's second hypothesis is not the weak
one; the urban signal being a natural gas signal has evidence behind it,
including evidence specific to this region.

*The mechanism.* The cited source frames the problem as emission standards and
their enforcement. It describes neither retrofitting nor faulty tailpipes, so
the thesis's mechanism is not the one its own source reports, and that remains
the defect. It should be restated as a standards-and-enforcement problem, which
is both what the source says and a claim the later work supports.

*The omission.* The thesis includes no waste layer and does not mention the
sector. That omission is now quantifiable rather than merely notable. A
city-scale source-resolved inventory of 339 Chinese prefecture-level cities from
2018 to 2024 finds that waste-related emissions accounted for the majority of
total methane emissions in 38 cities, primarily in economically developed,
densely populated coastal agglomerations, and it names Shanghai and Suzhou among
its representative examples (Zhang et al., 2026, Environmental Science &
Technology 60, 22323-22334, doi:10.1021/acs.est.5c18654). Both are inside this
study's domain: Shanghai is one of the four provinces and Suzhou is in Jiangsu.
The sector also has facility-level measurements behind it now, from atmospheric
measurement at 105 Chinese wastewater treatment plants including thirteen in
Nanjing (Sun et al., 2026, Science Advances 12, doi:10.1126/sciadv.aec0536).

For the region as a whole, a Bayesian inversion of this region's methane budget
found agricultural soil to be the largest single contributor at 29.6 percent
(Hu et al., 2019, Journal of Geophysical Research: Biogeosciences 124,
1148-1170, doi:10.1029/2018JG004850). What that paper reports for the urban and
waste sectors specifically could not be established from its abstract and is not
claimed here.

Impervious surface should therefore be described as a proxy for the urban source
bundle as a whole rather than for vehicle emissions in particular, and the
bundle should be named: gas in end use and transportation, landfill, and
wastewater. In the cities this study's most urban cells contain, the largest
component of that bundle is the one the thesis does not mention.

**Two corrections to earlier versions of this item, and the second reverses the
first.** Until 3 September 2026 this item asserted that waste treatment is the
dominant anthropogenic methane source at city scale in China. That assertion was
withdrawn as unsourced, and `notes/references.md` recorded that repeated
searches had returned nothing supporting it for Chinese cities. On 10 September
2026 the city-scale inventory above supplied it in a narrower form: not
nationally dominant, but the majority in 38 named cities, two of which are in
this domain. **The original claim was wrong about its scope, not about its
mechanism**, and stating it nationally is what made it unsourceable. Withdrawing
it was still correct at the time, because the narrower version was not in hand.
The sequence is recorded rather than collapsed because it is the second instance
in this document of a correction that itself needed correcting, after 5.4.

*Verified by:* the abstract of Da Pan et al. resolved through Crossref, which
names heavy-duty vehicle measurements and emission standards and contains no
mention of retrofitting; the abstract of Zhao et al. (2024); the Hu et al.
(2019) partitioning figure; and the full text of Zhang et al. (2026) through
PubMed Central, read directly, from which the 38-city statement and the named
examples are quoted. **One work here is cited for its direction and region
only.** Zhao et al. (2026) resolves through Crossref and its title, authorship
and journal are verified, but the article is paywalled, its abstract is not
indexed by Crossref or OpenAlex, and the leakage percentages circulating for it
come from a press summary rather than the paper. No number from it is quoted
here or anywhere in this repository.

### 5.4 Global warming potential

The thesis gives the global warming potential of methane as 25 to 30 times that
of CO2, citing a 2011 source, without stating a time horizon. **The horizon is
the defect.** A GWP figure is meaningless without one, and the thesis's range is
otherwise defensible.

The current assessment is IPCC AR6 Working Group I, Table 7.15, which
distinguishes fossil from non-fossil methane, a distinction the thesis does not
make and an earlier version of this item did not make either:

| | GWP-20 | GWP-100 |
|---|---|---|
| CH4 fossil | 82.5 ± 25.8 | 29.8 ± 11 |
| CH4 non-fossil | 79.7 ± 25.8 | 27.0 ± 11 |

Both AR6 central values for GWP-100, 27.0 and 29.8, fall **inside** the thesis's
stated range of 25 to 30. Against the assessment current when a 2011 source was
written, AR4's GWP-100 of 25, the lower bound is also the standard value. So the
number is not the problem; the missing horizon is, and it should be stated
wherever the figure appears, along with whether fossil or non-fossil methane is
meant.

**A correction to an earlier version of this item.** Until 3 September 2026 this
section asserted that "current syntheses give approximately 28 to 36 over 100
years and 84 to 87 over 20 years" and used that to criticise the thesis's figure
as dated. Those numbers are not current. They are approximately the AR5
assessment of 2013, whose Table 8.7 gives methane GWP-20 as 84 without and 86
with climate-carbon feedbacks, and GWP-100 as 28 and 34 respectively; neither 36
nor 87 appears in that table either. So this document criticised the thesis for
using a dated figure while quoting a dated figure of its own, and its range
excluded AR6's non-fossil value of 27.0 that the thesis's range contains. The
correction was further from the current assessment than the thing it corrected.

*Verified by:* IPCC AR6 WG1 Chapter 7 Table 7.15, read directly from the
chapter PDF (Forster et al., 2021, doi:10.1017/9781009157896.009); and IPCC AR5
WG1 Chapter 8 Table 8.7, read the same way (Myhre et al., 2013,
doi:10.1017/CBO9781107415324.018), to establish that the withdrawn figures were
AR5-era rather than current.

---

## 6. Reproducibility and citation

### 6.1 Section 5.3 code links

Section 5.3 lists two Google Earth Engine script links and one Google Colab
notebook link as the study's open-source code availability statement. Their
current resolvability has not been established. This repository is intended to
supersede that statement.

*Verified by:* reading the three links listed in Section 5.3. They were not
dereferenced, which is why no claim is made about whether they still resolve.

### 6.2 Spatial statistics are not reproducible as reported

Section 5.1 reports a Global Moran's I of 0.46 and a z-score of 276.31 for
XCH4 in 2018. The spatial weights definition, distance band or contiguity
rule, and standardisation are not reported, so the statistic cannot be
reproduced. The z-score also scales with the number of features, so a large
value over a dense grid is arithmetically expected rather than informative: the
standardised statistic is the deviation of Moran's I from its expectation
divided by its standard deviation, and that standard deviation shrinks as the
number of units grows (Moran, 1950, Biometrika 37, 17-23,
doi:10.1093/biomet/37.1-2.17). Positive spatial autocorrelation in a column
concentration field is also expected on physical grounds rather than
informative about local sources, since column variation at these scales is
driven substantially by advected large-scale signal (Zeng et al., 2021, Nature
Communications 12, 1163, doi:10.1038/s41467-021-21434-7).

*Verified by:* full-text search of the thesis PDF for a spatial weights
definition, distance band, contiguity rule or standardisation, returning none.

### 6.3 Citation years

Two in-text citations disagree with the reference list: the GAIA reference is
cited in text as 2019 and listed as 2020, and the TROPOMI XCH4 reference is
cited in text as 2023 and listed as 2022. Both reflect the online-versus-print
gap; one convention should be applied throughout.

*Verified by:* cross-checking both in-text citation years against the entries in
the thesis reference list.

### 6.4 Auxiliary data described but not used

Section 1.3 describes four auxiliary datasets as compiled: Global Methane
Initiative emissions, provincial population and natural gas statistics,
provincial sown area of rice, and World Bank climatology. Only the sown area
of rice appears in the Results. The others should be removed or their use
described.

*Verified by:* full-text search of the thesis Results for each of the four
auxiliary datasets named in Section 1.3; only the sown area of rice appears.

### 6.5 No classification accuracy is reported

The study reports no accuracy assessment of any kind for either the GAIA-derived
urban layer or the PPPM-derived paddied rice layer. No error matrix, overall
accuracy, per-class accuracy, or agreement statistic of any sort appears in the
thesis, in the notebook, or in any committed figure. **That is the substantive
point and it stands.**

Section 5.1 is titled "Accuracy Assessment: Remotely sensed estimations versus
China's recorded estimations", but what it performs is not an accuracy
assessment. It sets the study's own remotely sensed areas beside China's
recorded agricultural statistics and compares the two totals. Both are
independent estimates of the same quantity, and neither is reference data for
the other, so agreement between them constrains nothing about how often a pixel
was classified correctly. An accuracy assessment requires reference data more
accurate than the map, which the field states as essential (Stehman and Foody,
2019, Remote Sensing of Environment 231, 111199,
doi:10.1016/j.rse.2019.05.018), and none was collected.

`legacy/figures/Accuracy_Assessment.png` compounds the confusion. It is a
rendered image of Table 1, listing urban extent, PPPM-derived paddied rice and
recorded sown area of rice by province and year. It carries no accuracy metric
of any kind, despite its filename.

**What should have been reported depends on what the layer is, and this item
previously got that wrong in two ways.**

For the thesis's own layers, which are categorical, the field's good-practice
standard asks for a probability sampling design, a response design using
reference data more accurate than the map, consistent analysis, and an error
matrix expressed as proportions of area with overall, user's and producer's
accuracy (Olofsson et al., 2014, Remote Sensing of Environment 148, 42-57,
doi:10.1016/j.rse.2014.02.015). None of the four is present. Where two products
are compared rather than a product against reference data, the informative
decomposition is quantity disagreement against allocation disagreement (Pontius
and Millones, 2011, International Journal of Remote Sensing 32, 4407-4429,
doi:10.1080/01431161.2011.552923), because a layer can have the right totals and
the wrong locations and only the second kind of error attenuates a regression
coefficient.

**A correction to an earlier version of this item.** Until 11 September 2026
this section listed the "kappa coefficient" among the missing metrics. **The
field's own guidance names correction for chance agreement as bad practice**,
and does so twice over. Stehman and Foody (2019) identify "three examples of
bad practice that are widespread": "the universal application of 85% target
accuracy, normalization of the error matrix, and correction for chance
agreement". Pontius and Millones (2011) is titled "Death to Kappa" and its two
recommendations are to stop using kappa and to use disagreement components
instead. So this document was faulting the thesis for omitting a statistic the
field discourages, which is the third instance recorded here of the errata
importing an assumption it had not tested -- after 5.3's waste-dominance claim
and 5.4's superseded global warming potentials. The request is removed and the
substantive point, that no accuracy assessment of any kind was reported, is
unchanged.

**A note on what this reproduction does and does not owe.** The reproduction
reports no accuracy assessment either, and the asymmetry is worth stating
because it is not hypocrisy. The thesis classified imagery and so produced a map
whose accuracy is a property of its own work. The reproduction classifies
nothing: it consumes published products whose accuracies are published, and
aggregates them to a fraction per 0.25-degree cell. For a fractional layer the
error-matrix machinery does not apply -- Olofsson et al. contains no treatment
of fractional cover, and the appropriate frame is mean deviation, mean absolute
deviation and regression against a more accurate reference fraction (Wickham et
al., 2020, International Journal of Applied Earth Observation and Geoinformation
84, 101955, doi:10.1016/j.jag.2019.101955; Riemann et al., 2010, Remote Sensing
of Environment 114, 2337-2352, doi:10.1016/j.rse.2010.05.010). What the
reproduction owes is Olofsson's recommendations **2 and 3** — reference data more
accurate than the map, and analysis consistent with it.

**A second correction to this item, on 13 September 2026, and it changes what
the reproduction owes rather than what the thesis owes.** Until this date the
sentence above read "the first three of Olofsson's five recommendations rather
than the last two". Recommendation 1, a probability sampling design, **does not
apply to the reproduction either**, for the same reason 4 and 5 do not: the
continuous-field protocol it adopted for a fractional layer assesses agreement
against complete-coverage reference data and states that it does not estimate
agreement from a sample, so there is no sampling design in it to be valid about.
The reproduction owes two recommendations, not three.

**And the remaining debt is now established as unpayable over this domain, which
is a stronger statement than "has not paid".** `notes/grounding-methods.md`
records the measurements: every candidate reference product over the Yangtze
River Delta is less accurate than the 30 m products it would assess — SinoLC-1
at 73.61 percent overall accuracy, ISA-1's impervious class at F1 75.53,
EcoVision at 83.6 percent and urban-only, and CISC at 30 m and so not a
reference at all — against GISA's impervious F-score of 0.954. **Recommendation
2 cannot be met with anything that exists**, so recommendation 3 cannot follow.

That sharpens the asymmetry this note exists to state rather than softening it.
The thesis reported no accuracy assessment **and reported a number as one**:
Section 5.1 is titled "Accuracy Assessment" and compares two independent
estimates of the same quantity. The reproduction reports no accuracy assessment
**and says so, in its methods section, with the reason and the measurements
behind it**. The asymmetry is not that one has an excuse and the other does not.
It is that one names the absence and the other named its absence an assessment.

*Verified by:* full-text search of the thesis PDF for confusion matrix, kappa,
overall accuracy, producer's and user's accuracy, precision, recall, F1 and
IoU, returning no standalone occurrence of any; the same search across the
notebook's source and stored outputs, returning none; visual inspection of the
rendered Accuracy_Assessment.png; the three bad practices read from Stehman and
Foody's published highlights, which cite the DOI directly; and a full-text
search of Olofsson et al. for "fraction", "sub-pixel" and "subpixel", returning
zero occurrences of each.

---

## 7. Claims tested against reproduced data

The six sections above record defects found by reading the thesis, the notebook
and the repository's history. This one is different in kind: it records what
happened when the study's central claim was rebuilt from source data and tested.
It is kept apart from Section 5 because that section records claims superseded
by other people's published work, whereas these are first-party results with
their own limits, and the two should not be read as carrying equal weight.

The reproduction is described in `README.md`, its reasoning in
`notes/decisions.md`, and the tables it rests on are committed under
`data/processed/`.

### 7.1 The rice attribution is not supported by the reproduced data

Section 5.1 identifies paddy rice fields as the largest driver of XCH4 hotspots,
and Section 5.2 of this document already notes that published work argues such
correlations are confounded. The reproduction tests the claim directly and does
not support it.

Over the four study provinces at 0.25 degrees for 2018, no land-cover model
beats a spatial null that predicts each cell from the mean of its eight
neighbours, under inverse-variance weighting, at either sample size, under
either cross-validation scheme. Rice fraction's fitted coefficient is +8.83 ppb
per unit fraction when cells are counted equally and -3.20 when they are
weighted by the number of soundings each rests on, and it is negative under both
weightings once wind is included. Its association with methane survives control
for surface albedo on no methane field at either weighting: the partial
correlations are -0.010, -0.065, +0.033 and -0.021.

Impervious fraction, which the thesis treats as the secondary driver, behaves
better but not well: held-out R squared 0.095 against the spatial null's 0.337
on the seasonally corrected field, and its association with methane falls from
Pearson +0.345 to +0.021 once surface albedo is controlled for.

A tower-based Bayesian inversion of this study's own region and year reaches a
compatible conclusion by a method that can support it: Huang et al. (2021,
Advances in Atmospheric Sciences 38, 1537-1551, doi:10.1007/s00376-021-0383-9)
attribute seasonal CH4 variability in the Yangtze River Delta to agricultural
activity. The difference is the inference, not the answer. That study constrains
emissions with a transport model and tower observations; the thesis inferred
them from a spatial correlation with land cover, which cannot support the claim
however the correlation comes out.

*Verified by:* `data/processed/baseline_results_2018.csv` and
`baseline_results_deseasonalised_2018.csv`, 88 rows each;
`albedo_confounder_2018.csv`; `predictor_comparison_2018.csv`. Regenerable by
`scripts/run_baselines.py` and `scripts/test_albedo_confounder.py`.

### 7.2 The negative result survives independently built predictors

This is the part that makes 7.1 worth stating rather than merely arguable, and
it was established after the rest of this section's substance.

Measurement error in a predictor attenuates an association toward zero, so it is
the failure mode that could produce a negative result out of nothing, and both
land-cover predictors carry documented error. The finding was therefore
recomputed against second products with different error structures: GISA in
place of GAIA for impervious surface, GloRice in place of the NESDC
classification for rice, in all four combinations.

Zero cases beat the spatial null under inverse-variance weighting across all
four pairs, both schemes and both sample sizes, out of 176 weighted
opportunities. The two urban products agree at Spearman +0.956 across all 926<!--#grid.rows-->
cells; the two rice products agree only at +0.654, so the rice test is a genuine
one and gives the same answer.

**Added 13 September 2026: the attenuation is now bounded rather than argued
around.** Second products with different errors are evidence that measurement
error is not producing the result; they are not a measurement of how much error
there is. Treating GISA as a second *measurement* of the impervious fraction
supplies that. The two cell fractions differ with a variance 13.2 percent of the
predictor's own, so under independence of the two products' errors the
reliability ratio is at least 0.868 and the largest possible de-attenuation
factor is 1.15 — which lifts the best impervious held-out R² from +0.085 to
+0.098 against a spatial null of +0.332. **Reaching the null would require 5.6
times the error variance the disagreement supports.** The bound's assumptions,
two of which are measurably violated in the unfavourable direction, are stated
in `data/processed/README.md`; the margin exceeds both violations.

*Verified by:* `data/processed/alternative_predictors_2018.csv`, 352 rows;
`predictor_comparison_2018.csv`. Regenerable by
`scripts/test_alternative_predictors.py`. The bound is
`data/processed/attenuation_bound_2018.csv`, regenerable by
`scripts/bound_attenuation.py --write`; the Spearman +0.956 above recomputes to
0.9558 in that script's cross-check.

### 7.3 The reference data Section 5.2 requires now exists and was used

Section 5.1 of this document records that datasets published since 2023 provide
independent reference for the paddy rice layer. Those datasets have now been
used: provincial rice areas in `data/processed/rice_area_by_province.csv` come
from GloRice, and the analysis grid's rice fractions from a 10 m provincial
classification distributed through Science Data Bank. The claim that validation
was impossible for want of reference data is superseded in practice and not only
in principle.

*Verified by:* `data/processed/rice_area_by_province.csv`, whose 28 GloRice rows
carry their source, and the rice fractions in `analysis_grid_2018.csv`.
Regenerable by `scripts/compute_rice_areas.py` and
`scripts/build_analysis_grid.py`.

### 7.4 The reproduction's own positive results are not attributable

Recorded so that 7.1 is not read as stronger than it is, and so that nobody
cites the reproduction for a claim it does not support.

The reproduction found associations between the methane field and surface
albedo, wind, and a variable encoding only when each cell was observed, all
stronger than anything land cover achieves. None is attributable. Impervious
fraction and surface albedo are collinear at Spearman +0.761, so a retrieval
bias and a genuine urban signal cannot be separated in this data. Wind cannot be
separated from sampling season, because each cell's annual mean is taken over
whichever days were observed there and those differ across cells by up to 228
days. Removing a fitted seasonal cycle at the sounding level took out 20.6
percent of the between-cell variance and changed no association materially,
because the residual is day-specific rather than seasonal.

One further result is uninterpretable rather than null and should not be read
either way. GloRice's rice association is stronger than the NESDC
classification's and survives control for albedo where that one does not, but it
is confounded four ways: a different sample of cells, an allocation model rather
than an observation, correlation with impervious fraction at Spearman +0.560,
and 368 of its 395 extra cells lying entirely outside the four provinces.

The negative result in 7.1 depends on none of this, which is why it is stated
without qualification and these are not. It is also mildly strengthened by it: a
confound large enough to carry albedo and wind through a seasonal correction
still does nothing for land cover, and correcting a retrieval bias correlated
with the predictor would remove signal from the land-cover association rather
than add it.

*Verified by:* `data/processed/deseasonalisation_2018.csv`,
`albedo_correction_2018.csv`, and the corresponding sections of
`notes/decisions.md`.

### 7.5 The headline urban expansion is not reproduced by either product

This is the largest correction in this section and the only one that touches a
number the thesis reports rather than an inference it draws.

Section 5.1 gives the four-province urban total as 8,297 km² in 2000 and
49,725 km² in 2018, a factor of 6.0 and an expansion of 41,428 km². Recomputed
from the current release of the same product, GAIA gives 16,387 km² and
49,348 km², a factor of 3.0 and an expansion of 32,961 km². GISA, an
independently built impervious product, gives 19,787 km² and 39,532 km², a
factor of 2.0 and an expansion of 19,745 km².

| account | 2000 km² | 2018 km² | factor | expansion km² |
|---------|---------|---------|--------|---------------|
| GAIA, as reported 2023 | 8,297 | 49,725 | 6.0 | 41,428 |
| GAIA, reproduced 2026 | 16,387 | 49,348 | 3.0 | 32,961 |
| GISA, reproduced 2026 | 19,787 | 39,532 | 2.0 | 19,745 |

**The 2018 extent reproduces and the 2000 extent does not.** Against the same
product, 2018 comes back 0.8 percent low while 2000 comes back 1.98 times high
and 2010 1.15 times high. The disagreement is concentrated entirely at the
historical end, and it is large enough that the growth factor is not reproduced
by either product: three accounts, three factors, spanning a factor of three.

The mechanism matters more than the discrepancy, because it is what makes this a
finding about the data rather than a disagreement between computations. GAIA
does not store urban extent per year. It stores, in a single band, the year each
pixel first became impervious, and an extent for any year is recovered by
thresholding that band. A reprocessing therefore re-runs change detection over
the whole archive: with more training years and better cloud handling, a pixel
one release dates to 2004 another may date to 1996. The effect is largest in the
earliest years, where the Landsat record is sparsest and a single added
observation can move a transition by a decade. Nothing in the file signals it,
and the raster decodes cleanly under either version.

The thesis used the 1985–2018 release. The archive reachable now is 1985–2021,
and Star Cloud distributes a later version again. So the two computations are
not two computations of the same data; they are two reconstructions of the same
history, and the sentence above about where they disagree is the shape that
implies.

What this does and does not undermine, stated separately because they are
different:

* **Urban extent grew substantially between 2000 and 2018, and every account
  agrees on that.** The smallest of the three still has extent doubling and
  adding 19,745 km², which is larger than Shanghai and Zhejiang's 2000 extents
  combined under any of them. No correction here touches the direction or the
  substantial character of the growth.
* **The magnitude does not reproduce.** The thesis's expansion of 41,428 km² and
  its sixfold factor rest on a GAIA release whose historical reconstruction has
  since changed, and neither figure is recoverable from the current release of
  that product or from an independent one.
* **This is not an arithmetic error.** Section 2.1 and Section 2.2 above record
  two of those, in the Zhejiang multiplier and the 2010 total, and this is not a
  third. The thesis's numbers are internally consistent with the data it had.
  What has changed is the data.

The version dependence is a general property of year-of-change products and
applies to GISA as well, which has its own release history. It is recorded at
length in `notes/decisions.md` under "Year-of-change products are
version-dependent"; it is repeated here because the claim it bears on is made
here.

A second disagreement sits underneath and is recorded for completeness. The two
products cross over: GISA finds 20.7 percent *more* impervious surface than GAIA
in 2000 and 19.9 percent *less* in 2018. So they disagree about the history far
more than about the extent, which is the same signature by a different route,
and it is why 7.2's use of GISA as an independent predictor is unaffected — that
test runs on 2018, where the two agree to a fifth.

*Verified by:* `data/processed/urban_extent_totals.csv`, twenty-four rows over
two products, four years and four provinces, computed with
`src.landcover.zonal_histogram` on the Natural Earth boundaries; its twenty rows
that overlap `urban_area_by_province.csv` and `urban_area_by_province_gisa.csv`
reproduce them to a worst relative difference of 1.3e-05. The thesis figures are
the `thesis_urban_km2` column of `urban_area_by_province.csv`, transcribed from
Table 1 of the thesis PDF. Regenerable by `scripts/compute_urban_extent.py
--write`, and drawn in `figures/urban_change.png`.
