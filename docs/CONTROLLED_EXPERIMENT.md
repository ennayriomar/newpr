# Controlled source-calibrated full-image experiment

This workflow compares an **internal baseline** (DINOv2 patch search), an
**adapted implementation** (search plus a global PCA residual), and an
**adapted implementation** with lambda zero as an exact control. It does not
import the official VisionAD implementation or claim paper reproduction.
Historical cropped-map figures and results are not reused.

`controlled_experiment.py` has separate `prepare`, `source` and `evaluate`
commands. `controlled_report.py` reports completed native cohorts only. Every
stage writes its real command output and machine-readable progress to disk.

## Data and frozen model

- Source: MVTec AD 2, eight public categories. Only `train/good` normal images
  calibrate cutoffs. AD2 public-test images are source-selection queries, not
  target evaluation images.
- Development check: all83 native MVTec AD bottle test images, one support
  image at seed17. This known category cannot select a parameter or cutoff.
- Actual target: all2162 native VisA test images, all12 categories, support
  seeds17/29/43. The official `split_csv/1cls.csv` defines native roles.
- One original normal target support image per draw; exactly the same image
  serves all three methods. The support draw uses a deterministic ordered
  prefix. There is no extra target calibration image and no optimizer epoch.
- Official frozen DINOv2 ViT-L/14 register weights, float32 CPU, raw mean of
  zero-based blocks4–18, three query slots and six support views per slot.

Images are resized to448x448, with `crop=448`: the crop operation is the
identity. Score maps interpolate directly from the32x32 patch grid to448x448.
Full-image GT is resized using nearest interpolation to448x448; every saved
map must match its GT shape. This covers the full field, including borders,
but does not constitute native-resolution pixel evaluation. Native anomalous
images keep their anomaly label even if nearest GT downsampling erases a tiny
defect; any empty resulting masks are explicitly listed.

## Source roles, calibration and lambda selection

`prepare` records all permitted IDs before inference. It fails on overlap by
ID or resolved file path between support, calibration, source-query and
evaluation roles. Calibration records must be unique AD2 train normals.
Repeated target query IDs across support draws are explicitly permitted
within the same evaluation role, never as calibration images.

The fixed source design uses one support image per AD2 category,20 separate
calibration normals per category (160 unique images), and five normal plus
five anomalous public-test queries per category (80 source-selection queries).
AD2 anomaly labels are used only for source selection, never for cutoffs.

For each lambda in `{0, 0.1, 0.25, 0.5}`, image and pixel cutoffs are fit
separately from the same source-normal cohort, each targeting5% false alarms.
They are upper empirical quantiles with strict `score > cutoff` decisions.
Ties are conservative. The realised source rates and exact cutoffs are saved;
there is no target false-alarm or independent-pixel coverage guarantee.

Lambda maximizes mean source-category balanced accuracy at those cutoffs.
Ties use source image AUROC and then smaller lambda. Global PCA95% variance
and the uniform additive gate remain fixed prototype constants. The selected
lambda, config hash, source selection evidence, data roles and scoring-code
hashes are sealed in `protocol.json` **before target inference**. Evaluation
fails if those files change.

## Commands

Create a fresh run directory and `experiment_config.json` with the dataset
roots, pinned encoder source/checkpoint, fixed settings and selection rules.
The recorded configuration for the18 October run is delivered with its results.

```bash
python controlled_experiment.py prepare --run RUN_DIR > RUN_DIR/prepare.log 2>&1
python controlled_experiment.py source --run RUN_DIR > RUN_DIR/source.log 2>&1
python controlled_experiment.py evaluate --run RUN_DIR > RUN_DIR/evaluate.log 2>&1
python controlled_report.py --run RUN_DIR > RUN_DIR/report.log 2>&1
```

Run each command only after the preceding one succeeds. A source stage
cannot substitute a different backbone if official weights are absent or
fail checksum verification. No synthetic images stand in for source or
target inference. Unit tests use small arrays exclusively to test logic.

The full CPU experiment requires several hours. The encoder runs once per
target image; its descriptors are shared across the three support banks.
`progress.jsonl` records completed native images and actual support-draw
metrics. File names and logs distinguish source selection, bottle development
and VisA target evaluation.

## Metrics and uncertainty

Metrics include image AUROC, pixel AUROC over **all native test images**,
AU-PRO at FPR0.3, realised image FPR and recall, balanced accuracy, and pixel
IoU/F1 at each method's own source-calibrated pixel cutoff.

The2,000 paired bootstrap replicates resample query images, stratified by
native normal/anomalous label. Methods share every sampled image weight.
Support draws within each category share query bootstrap weights, so averaging
draws never treats a repeated image as an independent new query. Intervals
are conditional on the three fitted support banks; seed-to-seed variation is
reported separately.

Pixel AUROC point metrics are exact. Its bootstrap uses a fixed4096-score-rank
ROC grid, explicitly saved with its grid point; intervals therefore have a
sampled-grid approximation. AU-PRO uses128 raw distinct-score rank thresholds,
eight-connected defect regions, pooled normal-pixel FPR and equal region
weight. Its bootstrap holds the original grid fixed. Pixels are not resampled
independently.

Overall differences first average support draws within category, then weight
categories equally. A category-level cluster bootstrap resamples the12 VisA
categories. The primary stop criterion is the overall image-AUROC paired
interval: it must exclude zero in the positive direction, and calibrated
balanced accuracy must also improve. Otherwise the report says **no demonstrated
benefit**, and the experiment ends without searching more settings. All12
VisA categories and three draws run before this rule is applied.

## Figures and artifacts

Figures select a true negative, strongest normal false positive, lowest-score
miss, smallest positive full-field mask and worst localization IoU for each
category/draw. Ties use native ID. Duplicate cases retain every reason; absent
events are recorded. These are diagnostic examples, not random representatives.

Panels show image, GT, actual baseline, actual hybrid and hybrid-minus-baseline.
One literal raw-score range is shared across both methods and all plotted
cohorts. Differences have their own shared labeled range. Raw NPZ maps and
native-ID metadata are placed beside each figure. If selected lambda is zero,
identical maps and zero difference are explicitly reported as the real outcome.

The results directory contains `per_image.jsonl`, `per_category.csv`,
`per_draw.csv`, `protocol.json`, calibration IDs/cutoffs, paired bootstrap
arrays, category-cluster bootstrap arrays, seed variation, reproducibility
checks, all metric points and `README_results.md`. The latter reports the
actual VisA false-alarm rate and applies the stop rule without retuning.

MVTec-derived data retain CC BY-NC-SA4.0; VisA-derived data retain CC BY4.0.
The datasets have prior prototype exposure. This is a controlled known-dataset
comparison, not an untouched-data generalization or state-of-the-art claim.
