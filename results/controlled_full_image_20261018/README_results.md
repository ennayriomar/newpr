# Controlled full-image source-calibrated experiment

**no demonstrated benefit.** Frozen lambda: 0.25.

VisA: all12 native categories, all2162 native test images, one-shot supports at seeds17/29/43; the three methods use exactly the same support images and no additional target normals. Bottle is development evidence only and did not select any setting.

| Method | Image AUROC | Pixel AUROC | AU-PRO | Image FPR (macro) | Recall | Pixel IoU | Pixel F1 |
|---|---|---|---|---|---|---|---|
| baseline (internal baseline) | 0.9344 | 0.9799 | 0.9300 | 0.0000 | 0.0000 | 0.2486 | 0.3866 |
| hybrid (adapted implementation) | 0.9407 | 0.9817 | 0.9378 | 0.0000 | 0.0144 | 0.2600 | 0.4037 |
| lambda_zero (adapted implementation) | 0.9344 | 0.9799 | 0.9300 | 0.0000 | 0.0000 | 0.2486 | 0.3866 |

Realised pooled VisA hybrid false-alarm rate: **0.0000** (0/2886 correlated normal query/draw cases). The5% source calibration target is not a target-domain guarantee.

## Paired overall differences

| Metric | Hybrid minus baseline | 95% category-cluster interval |
|---|---|---|
| image_auroc | +0.00630 | [+0.00071, +0.01252] |
| pixel_auroc | +0.00179 | [+0.00044, +0.00341] |
| au_pro | +0.00781 | [+0.00537, +0.01051] |
| image_fpr | +0.00000 | [+0.00000, +0.00000] |
| recall | +0.01444 | [+0.00000, +0.03444] |
| balanced_accuracy | +0.00722 | [+0.00000, +0.01722] |
| pixel_iou | +0.01139 | [-0.00356, +0.02729] |
| pixel_f1 | +0.01715 | [-0.00202, +0.03718] |

Per-category paired intervals, seed variation, bootstrap multiplicities and sampled curves are saved. Gains with intervals containing zero are not demonstrated improvements. No new settings were tried after target inference.

Paired query-image stratified bootstrap conditional on fixed support banks; common image weights across support draws within category; category-cluster bootstrap averages draws before resampling12 categories. Pixel AUROC bootstrap uses4096-score-rank grid; its point metric is exact. AU-PRO uses128-score-rank grid, FPR0.3. Neither resamples pixels independently.

## Protocol and deviations

Cutoffs were fit separately for every lambda from160 AD2 train-normal images, disjoint by ID/resolved path from all supports, source selection queries and evaluation images. Strict `score > cutoff` handles calibration ties conservatively. Lambda used80 source-only AD2 public-test queries; the selection rule, candidate set and all settings were recorded before source inference, then the chosen lambda and configuration hash were sealed before target inference.

Image and full-image GT are resized to448x448, and maps have the same448x448 shape. The complete field is scored; native-resolution pixel metrics are not claimed. Any anomalies erased by GT downsampling are listed in summary.json and retain their native image labels.

- Internal baseline and adapted implementation; no claim of official VisionAD reproduction.
- Full448x448 image/maps instead of earlier448-resize392-center-crop256-maps.
- Only global PCA95%, uniform additive gate; lambda selected on AD2 only.
- Image and pixel cutoffs separately fit for each candidate from AD2 train normals; no extra target calibration images.
- AD2 public-test anomalies used only for source lambda selection, not cutoff calibration.
- One-shot only, three support draws, nested support prefixes; no full paper shot sweep.
- Frozen official DINOv2 ViT-L/14 register weights, mean zero-based blocks4–18, three slots and six support views as existing internal recipe.
- AU-PRO is sampled at128 raw-score rank thresholds; query-image bootstrap holds each original grid fixed.

## Figures

Fixed rule, one shared raw-score range across methods and all figures. Each figure has raw maps and native-ID metadata beside it. Selected cases are diagnostic examples, not random representatives. Missing false positives or misses are explicitly recorded.

- [mvtec_ad / bottle / seed17](mvtec_ad/bottle/seed-17/figures/cases.png)
- [visa / candle / seed17](visa/candle/seed-17/figures/cases.png)
- [visa / candle / seed29](visa/candle/seed-29/figures/cases.png)
- [visa / candle / seed43](visa/candle/seed-43/figures/cases.png)
- [visa / capsules / seed17](visa/capsules/seed-17/figures/cases.png)
- [visa / capsules / seed29](visa/capsules/seed-29/figures/cases.png)
- [visa / capsules / seed43](visa/capsules/seed-43/figures/cases.png)
- [visa / cashew / seed17](visa/cashew/seed-17/figures/cases.png)
- [visa / cashew / seed29](visa/cashew/seed-29/figures/cases.png)
- [visa / cashew / seed43](visa/cashew/seed-43/figures/cases.png)
- [visa / chewinggum / seed17](visa/chewinggum/seed-17/figures/cases.png)
- [visa / chewinggum / seed29](visa/chewinggum/seed-29/figures/cases.png)
- [visa / chewinggum / seed43](visa/chewinggum/seed-43/figures/cases.png)
- [visa / fryum / seed17](visa/fryum/seed-17/figures/cases.png)
- [visa / fryum / seed29](visa/fryum/seed-29/figures/cases.png)
- [visa / fryum / seed43](visa/fryum/seed-43/figures/cases.png)
- [visa / macaroni1 / seed17](visa/macaroni1/seed-17/figures/cases.png)
- [visa / macaroni1 / seed29](visa/macaroni1/seed-29/figures/cases.png)
- [visa / macaroni1 / seed43](visa/macaroni1/seed-43/figures/cases.png)
- [visa / macaroni2 / seed17](visa/macaroni2/seed-17/figures/cases.png)
- [visa / macaroni2 / seed29](visa/macaroni2/seed-29/figures/cases.png)
- [visa / macaroni2 / seed43](visa/macaroni2/seed-43/figures/cases.png)
- [visa / pcb1 / seed17](visa/pcb1/seed-17/figures/cases.png)
- [visa / pcb1 / seed29](visa/pcb1/seed-29/figures/cases.png)
- [visa / pcb1 / seed43](visa/pcb1/seed-43/figures/cases.png)
- [visa / pcb2 / seed17](visa/pcb2/seed-17/figures/cases.png)
- [visa / pcb2 / seed29](visa/pcb2/seed-29/figures/cases.png)
- [visa / pcb2 / seed43](visa/pcb2/seed-43/figures/cases.png)
- [visa / pcb3 / seed17](visa/pcb3/seed-17/figures/cases.png)
- [visa / pcb3 / seed29](visa/pcb3/seed-29/figures/cases.png)
- [visa / pcb3 / seed43](visa/pcb3/seed-43/figures/cases.png)
- [visa / pcb4 / seed17](visa/pcb4/seed-17/figures/cases.png)
- [visa / pcb4 / seed29](visa/pcb4/seed-29/figures/cases.png)
- [visa / pcb4 / seed43](visa/pcb4/seed-43/figures/cases.png)
- [visa / pipe_fryum / seed17](visa/pipe_fryum/seed-17/figures/cases.png)
- [visa / pipe_fryum / seed29](visa/pipe_fryum/seed-29/figures/cases.png)
- [visa / pipe_fryum / seed43](visa/pipe_fryum/seed-43/figures/cases.png)

## Attribution

MVTec AD / AD2: MVTec Software GmbH, Bergmann et al. (CVPR2019), Heckler-Kram et al. (arXiv2503.21622,2025); derived MVTec figures/maps retain CC BY-NC-SA4.0. VisA: Zou et al., SPot-the-Difference (ECCV2022); derived VisA figures/maps retain CC BY4.0. Meta DINOv2 source/weights retain their original licensing. This is an internal baseline and adapted implementation, not an official paper reproduction.

| Item | Status |
|---|---|
| Experiment code and leakage checks | unit-tested |
| Official frozen DINOv2 weights | real-weights verified |
| AD2 source selection and calibration | real-dataset verified |
| Bottle development check | benchmark evaluated |
| All12 VisA categories and three support draws | benchmark evaluated |
