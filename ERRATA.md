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
This is the drainage basin area, not the river's extent or length.

*Verified by:* reading the figure and its units in Section 1.5; 1.8 million km2
is an area, and the sentence attributes it to the river's extent.

### 2.4 Spatial resolution notation

TROPOMI XCH4 spatial resolution is given throughout as "7km2 x 7km2". The
correct notation is 7 km × 7 km (nadir resolution was refined to
approximately 7 × 5.5 km in August 2019, after the study year).

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
ImageNet channel statistics, which is only meaningful with an
ImageNet-pretrained encoder.

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
*equivariant*, and are not scale invariant. The resampling actually performed,
and the limitation it imposes, should be stated instead.

*Verified by:* reading the scale-invariance claim in Section 3.3 against the two
sensor resolutions as the thesis itself states them.

---

## 5. Claims superseded by subsequent literature

### 5.1 Availability of reference data

Section 5.2 states that validation would require reference data that, to the
author's knowledge, does not exist. Datasets published since 2023 provide
independent reference for the paddy rice layer at the study's own resolution,
including a 30 m paddy rice distribution dataset for China covering 1990 to
2016 and a 500 m Asian monsoon rice product covering 2000 to 2021. Rice
methane emission inventories at 0.1° monthly resolution, and regional TROPOMI
flux inversions, have also since been published.

### 5.2 Causal attribution of XCH4 to rice paddies

Section 5.1 states that the largest driver of XCH4 hotspots appears to be
paddy rice fields. A published Matters Arising responding to one of the
thesis's two pillar references argues that local XCH4 variation is driven
primarily by advected large-scale flux signals rather than local emission, and
that spatial correlations between rice extent and XCH4 are confounded by
cross-correlation with other sources sharing similar spatial structure. That
exchange is not cited in the thesis. Causal language in Section 5.1 should be
replaced with language describing spatial association.

### 5.3 Urban methane attributed to natural gas vehicles

Sections 1.1 and 1.5 attribute urban methane to natural gas vehicles, with a
framing of retrofitted vehicles and faulty tailpipes. The cited source
measured real-world emissions from heavy-duty natural gas vehicles and
attributed them to engine and aftertreatment behaviour; it does not support
the retrofitting framing. Separately, waste treatment (landfill, incineration,
sewage) is reported in the literature as the dominant anthropogenic methane
source at city scale in China. The thesis includes no waste layer and does not
mention the sector. Impervious surface should be described as a proxy for the
urban source bundle as a whole rather than for vehicle emissions.

### 5.4 Global warming potential

The 100-year global warming potential of methane is given as 25 to 30 times
that of CO2, citing a 2011 source. Current syntheses give approximately 28 to
36 over 100 years and 84 to 87 over 20 years. The horizon should be stated
explicitly wherever the figure appears.

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
value over a dense grid is arithmetically expected rather than informative,
and positive spatial autocorrelation in a column-concentration field follows
from atmospheric transport and from the retrieval's own spatial binning.

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

The study reports no classification accuracy metric for either the
GAIA-derived urban layer or the PPPM-derived paddied rice layer. No confusion
matrix, kappa coefficient, overall accuracy or per-class accuracy appears in
the thesis, in the notebook, or in any committed figure.

Section 5.1 is titled "Accuracy Assessment: Remotely sensed estimations versus
China's recorded estimations", but what it performs is not an accuracy
assessment. It sets the study's own remotely sensed areas beside China's
recorded agricultural statistics and compares the two totals. Both are
independent estimates of the same quantity, and neither is reference data for
the other, so agreement between them constrains nothing about how often a pixel
was classified correctly. A classification accuracy assessment requires labelled
reference samples the classifier did not see, and none were collected.

`legacy/figures/Accuracy_Assessment.png` compounds the confusion. It is a
rendered image of Table 1, listing urban extent, PPPM-derived paddied rice and
recorded sown area of rice by province and year. It carries no accuracy metric
of any kind, despite its filename.

*Verified by:* full-text search of the thesis PDF for confusion matrix, kappa,
overall accuracy, producer's and user's accuracy, precision, recall, F1 and
IoU, returning no standalone occurrence of any; the same search across the
notebook's source and stored outputs, returning none; and visual inspection of
the rendered Accuracy_Assessment.png.

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
better but not well: held-out R squared 0.096 against the spatial null's 0.343
on the seasonally corrected field, and its association with methane falls from
Pearson +0.346 to +0.020 once surface albedo is controlled for.

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
opportunities. The two urban products agree at Spearman +0.956 across all 927
cells; the two rice products agree only at +0.654, so the rice test is a genuine
one and gives the same answer.

*Verified by:* `data/processed/alternative_predictors_2018.csv`, 352 rows;
`predictor_comparison_2018.csv`. Regenerable by
`scripts/test_alternative_predictors.py`.

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
than an observation, correlation with impervious fraction at Spearman +0.561,
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
