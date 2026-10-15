# Register-DINO search with a local-PCA correction

This is an independent executable research implementation of the inspected
class-separated VisionAD scoring recipe, with a new experimental normal-only
local-subspace correction. It does not import or redistribute the VisionAD
repository, whose code license was unresolved during inspection. It uses the
licensed official Meta DINOv2 source and public pretrained weights. It does not
fine-tune the foundation model or train an LLM.

The reference is [Search is All You Need for Few-shot Anomaly Detection](https://arxiv.org/abs/2504.11895),
with inspected source revision `Qiqigeww/VisionAD@2d5e36f357409125ccd9646ba016824005599df4`.
The paper has inconsistent default-backbone/layer descriptions. The executable
recipe here follows that revision's class-separated large-model scripts:

| Component | Implemented setting |
|---|---|
| Frozen encoder | Actual DINOv2 ViT-L/14 with four register tokens; 1024-dimensional descriptors |
| Image preprocessing | RGB, Pillow bilinear resize 448, center crop 392, ImageNet normalization |
| Feature aggregation | Raw arithmetic mean of zero-based blocks 4 through 18; no final layer norm; discard CLS and registers |
| Positional interpolation | Antialias false, offset 0.1, matching the inspected wrapper rather than Meta's register-hub defaults |
| Support augmentation | Identity, 90/180/270-degree rotation, vertical flip, horizontal flip |
| Query/support slots | Identity; paired vertical flip with map flipped back; clamp already normalized tensors below 0 |
| Search | Unit-normalized descriptors, exact cosine nearest-neighbour patch distance, sum aligned slot maps |
| Image score | Highest floor 1% of the bilinearly resized 256x256 map, averaged |

Identical transformed support tensors are deduplicated computationally. A
typical original image needs 14 unique forwards across the three slots, while
each slot retains all six declared support views. This does not change the
number of original reference images. Query features are streamed per category
and shared across support draws, limiting disk use.

The original advertised numerical evaluation function returned placeholder
zeros in the inspected revision. This project computes real metrics with its
own wrapper. It uses nearest-neighbour binary-mask resizing in matching cropped
coordinates; the inspected repository's default mask transform used bilinear
resizing before binarization. This is an explicit localization-metric deviation.
Image labels remain original native labels even when cropping removes a defect;
those cases are counted separately. The outer image border is unscored, not
classified as normal by the segmentation output.

## Experimental correction

One normal original image per category fits every target bank. No extra target
normal calibration images are used. All unique augmented normal descriptors
fit either one global PCA or four local PCAs. Clusters are fitted to normalized
descriptor directions; their PCAs use raw descriptors and centered float64
covariance. Residuals are divided by the cluster's mean total centered normal
feature energy, not by an artificially tiny in-sample residual quantile.

The candidate map in each slot is `search + strength * gate * relative_residual`.
The gate is either 1 or `relative_residual/(relative_residual+search)` with a
defined 0 value for 0/0. These are heuristics, not correctness probabilities.
The correction is nonnegative. At the same fixed cutoff, search alerts are
preserved; additional false alarms can still occur. Pixel ranking can improve
or worsen, so it must be measured.

The finite grid has 25 unique configurations: the unchanged search baseline,
plus clusters 1/4 × PCA variance 0.95/0.99 × strength 0.1/0.25/0.5 × two gates.
Native development labels and masks select one global configuration by mean
within-category/reference-draw image AUROC, subject to mean development pixel
AP at 256x256 not declining. Ties prefer higher pixel AP, lower strength, fewer
subspaces, then parameter SHA256. The unchanged baseline is eligible to win.
The selection budget is 50 normal and 50 anomalous source-category images with
masks. Target-bank fitting is normal-only; the entire selection procedure is
not label-free. This extra source supervision must be declared in paper
comparisons.

Separate global image/pixel operational cutoffs are the baseline development
normal-score 95th/99.5th percentiles. They use development categories, remain
unchanged for the hybrid, and provide no target-domain false-alarm guarantee.
No old probability/error head is transferred.

## Run the declared CPU study

Use the existing pinned Python 3.12 CPU environment or run `bash install_safal.sh`.
Prepare the actual 1.22GB checkpoint and pinned source:

```bash
python prepare_vision_hybrid.py --destination ../vision_hybrid_assets
```

Bundled releases can reuse their licensed source with
`--source-dir ../vendor/dinov2`. SHA256 is enforced for every weight load:
`36e4deffbaef061a2576705b0c36f93621e2ae20bf6274694821b0b492551b51`.
The initial official download was also checked against the publisher's S3
multipart checksum and length. Source pin and per-file digests are verified.

Edit paths in a copy of `configs/vision_hybrid_20261015.json` before starting:

```bash
python -m safe_iad.vision_hybrid_cli plan --config configs/vision_hybrid_20261015.json --output /tmp/vision_hybrid_20261015
python -m safe_iad.vision_hybrid_cli develop --config configs/vision_hybrid_20261015.json --output /tmp/vision_hybrid_20261015
python -m safe_iad.vision_hybrid_cli evaluate --config configs/vision_hybrid_20261015.json --output /tmp/vision_hybrid_20261015
python -m safe_iad.vision_hybrid_cli report --config configs/vision_hybrid_20261015.json --output /tmp/vision_hybrid_20261015
```

Planning freezes image IDs, support IDs, source, weights, input hashes and the
entire finite protocol before extraction. Development writes an immutable
selection lock before verification extraction. An OS file lock prevents
concurrent stages. Completed categories can resume only after hash checks;
preserve incomplete category outputs under `attempts/` before a clean retry.

This declared pilot uses one original target normal, draws 17/29, 100 development
images in five categories, and 100 available-history-excluded verification
images in five different categories: MVTec AD bottle/metal_nut/pill and VisA
capsules/pcb4. Some categories have historical prototype exposure, so this is
not a universally untouched test. The 200 verification query/draw cases are
correlated. Categories remain fixed in the conditional paired bootstrap.

The feature encoder supports CPU/CUDA explicitly. The present environment has
four CPU cores of quota and no GPU. Its real 392-pixel forward took about 2.5s
per view. CUDA operation is not established by a CPU check. The declared runner
is a bounded one-shot study, not all 27 categories, five draws and 1/2/4 shots
from the published benchmarks. A full-paper superiority claim requires a
matched full benchmark; no such claim follows from a subset result.
The released banks enforce their recorded numerical versions, including the
CPU Torch build. A CUDA study needs a suitable GPU Torch installation and
fresh banks fitted in that environment; the CPU installer does not install
CUDA support.

## Use a selected model

```bash
python -m safe_iad.vision_hybrid_cli predict \
  --model /path/to/selected/model \
  --image /path/to/image.png \
  --output /path/to/new_prediction \
  --source-dir /path/to/vendor/dinov2 \
  --checkpoint /path/to/dinov2_vitl14_reg4_pretrain.pth
```

Prediction accepts no labels or masks. It checks trained encoder semantics,
source/weight/support hashes and numerical software versions, then writes a
decision and cropped-region float32 map. Model NPZs contain normal-support
features, not the external foundation weight binary or original photographs.
Respect the dataset-derived artifact notice distributed with results.

Legacy SAFAL files and checkpoint source hashes remain unchanged. The new
modules are `vision_hybrid_features.py`, `vision_hybrid_model.py` and
`vision_hybrid_cli.py`. Measured outcomes belong in the completed run's report;
this design does not promise a gain.

## Full reference benchmark driver

`benchmark_vision_reference.py` provides the full class-separated reference
benchmark for all official MVTec AD/VisA categories, one/two/four shots and
five support draws. It computes measured image AUROC/AP; localization is
optional. This full driver has not been run as part of the bounded CPU study.
It streams per-category features in memory and supports GPU cosine search as
well as GPU feature extraction. Use a new output directory:

```bash
python benchmark_vision_reference.py \
  --source-dir /path/to/vendor/dinov2 \
  --checkpoint /path/to/dinov2_vitl14_reg4_pretrain.pth \
  --mvtec-ad /path/to/mvtec_ad --visa /path/to/visa \
  --shots 1 2 4 --seeds 1 2 3 4 5 --device cuda \
  --localization --output /path/to/reference_full_run
```

Support draws use sorted paths and seeded `torch.randperm`, with nested shot
prefixes. The authors' exact reference IDs were not published; do not promise
identical headline scores. A `--categories` or `--limit-queries` run is explicitly
a subset smoke check. Baseline-only benchmark output does not establish a
hybrid improvement. Hyperparameters selected on development categories must
be assessed on separate data rather than relabeling development examples as
untouched tests.


## Completed study — 15 October 2026

The frozen winner is the global PCA control: one cluster, 95% retained
variance, correction strength 0.5 and a uniform gate. Local and gated variants
were eligible but did not win. Development image AUROC is 93.00% for search
and 93.30% for the winner; development pixel AP is 0.4416 and 0.4565.

Reserved-image measurements (100 unique image IDs, five other categories,
two reference draws, 200 paired cases):

| Metric | Same-feature search | Selected search + PCA |
|---|---:|---:|
| Mean image AUROC | 97.80% | 98.70% |
| Accuracy at shared source cutoff | 78.50% | 75.50% |
| Mean cropped-ROI pixel AP | 0.4705 | 0.5020 |
| Mean cropped-ROI AU-PRO | 0.8841 | 0.9080 |
| Missed anomaly cases (100) | 43 | 1 |
| False alarms (100 normal cases) | 0 | 48 |

Paired hybrid-minus-search image AUROC: +0.90 percentage
points, with conditional 95% interval [-0.50,
+3.00]. Categories are fixed and two support draws limit
replication. The interval includes zero; an AUROC gain is not established.
There are 0 lost baseline
anomaly alerts, 42 recovered
anomaly cases and 48 added
false alarms. No parameters were changed using these outcomes.

The source selection budget is 50 normal plus 50 anomalous development
images and masks; it is additional supervision beyond fitting each target
bank with one normal. Original image labels are retained even if the center
crop removes a defect. This is not the full paper benchmark and does not
establish paper superiority. Prior SAFAL pilot scores used different cohorts
and support budgets and are not matched comparisons to this study.

The compact ZIP includes complete code, licensed Meta source and the fixed
bottle/seed17 bank. All 20 fitted banks, branch outputs, 10 feature probes and
200 map archives are distributed in the complete TAR.GZ archive. Use
`download_vision_hybrid_results.py --ref PAYLOAD_COMMIT --extract`, with the
immutable payload commit recorded in the repository publication record.
