# SAFAL paper-informed parameter tuning

Project: **Support-Adequacy-Aware Few-Shot Anomaly Localization for Reliable
Industrial Inspection**. This protocol searches for a better global SAFAL
configuration under a declared development-set defect-preservation constraint.
It does not promise higher accuracy, faithful paper reproduction or reliable
deployment. Results must come from completed artifacts, not this specification.

The work adds separate tuning/inference modules. Earlier SAFAL core sources,
serialized checkpoints, training results and negative findings remain preserved.

## Paper guidance and implementation differences

The verified [SubspaceAD source](https://github.com/CLendering/SubspaceAD) models
normal raw features with PCA and squared reconstruction residuals. Its benchmark
recipe uses a giant/registers DINOv2 encoder, resolution 672, 99% explained
variance and a 3×3 Gaussian map filter with sigma 4. The verified
[VisionAD research method](https://github.com/Qiqigeww/VisionAD),
[*Search is All You Need for Few-shot Anomaly Detection*](https://arxiv.org/abs/2504.11895),
uses a large/registers backbone, resize 448/crop 392, six support views and
multilayer normalized patch matching. Its inspected evaluation also combines
three query/support transformations. Exact recipes and source limitations are
documented in [literature_review.md](literature_review.md).

This tuning experiment uses the existing actual frozen ViT-B/14 checkpoint,
independent raw-PCA/cosine-search scoring, identity views and full-image square
resize. No unlicensed VisionAD code is copied. The verified ideas motivate
variance, scale, aggregation, layer/resolution and localization controls; they
do not establish the chosen grid as authors' recommended optimum. Gaussian
smoothing here operates on a 256×256 metric map and does not reproduce the
full official SubspaceAD scoring pipeline.

The current runtime is CPU with three inference threads and no available GPU.
The larger published backbones/augmentation recipes are not silently replaced
and then described as reproduced. The selected settings are conditional on this
small controlled backbone and measured dataset scope.

## Development population and matched controls

Stage 1 uses the existing k=4 development slice: 100 unique native query images
across five reserved validation categories, with support draws 17, 29 and 43.
That is 300 paired query/support cases, not 300 independent images. Each category
has ten normal and ten anomalous queries. The categories are MVTec AD `cable`,
`hazelnut`, `transistor`, and VisA `macaroni2`, `pcb2`.

Every candidate uses the same four original normal support images per bank and
four extra disjoint normal calibration images. The information budget is eight
target-category normal images, not a strict four-image experiment. PCA/search
fits and score scales use normal training data; development labels may select
parameters under this explicit validation protocol. Masks and labels never
enter query feature extraction or label-free inference. This extends the earlier
fixed-rule experiments into supervised development-set model selection and
must be reported as such.

The matched original SAFAL control has accuracy 0.81 on these k=4 cases; its
fixed-average control has accuracy 0.80. The earlier 0.7667 SAFAL mean combined
k=1,2,4,8 and therefore is not the correct comparator for this tuning slice.
Keep the original controls' per-case predictions fixed during candidate scoring.

## Stage 1: 768 scoring configurations

One support SVD per bank supplies the declared variance choices; reuse does not
alter their mathematical fits. Raw PCA residuals and exact normalized cosine
search share the same 224-pixel raw mean of zero-based blocks `(2,5,8,11)`.

| Parameter | Declared choices |
| --- | --- |
| Retained PCA variance | 0.90, 0.95, 0.99, 0.995 |
| Normal calibration quantile | 0.90, 0.95, 0.99 |
| Image aggregation | Mean of the highest `max(1,floor(1% × patch_count))` scores; maximum patch score |
| Fusion | Five fixed search weights 0, 0.25, 0.5, 0.75, 1; original adaptive; reversed adaptive; max control |
| Image decision threshold T | 0.5, 0.75, 1, 1.25 |

The full Cartesian product has `4 × 3 × 2 × 8 × 4 = 768` configurations.
Fixed search weight 0 is the PCA-only endpoint and weight 1 is search-only.
These endpoints are scored as controls but cannot be selected as a winning
hybrid. There are 576 eligible hybrid configurations and 192 endpoint-control
configurations before the preservation constraint.

For each branch and aggregation, fit image cutoffs from the four held-out normal
image scores and patch cutoffs from their pooled patch scores, using the declared
empirical quantile with linear interpolation. Normal patch observations remain
correlated. Cutoffs must be strictly finite and positive; no hidden epsilon or
evaluation-set normalization is allowed. Changing the normal quantile is not
equivalent to guaranteeing a target false-alarm rate.

Fixed fusion uses `alpha × search + (1 − alpha) × PCA`. The original adaptive
search weight is `clip(0.9 − 0.8 × A, 0.1, 0.9)`; its reversed control uses the
complement. `A` remains a bounded branch-compatibility diagnostic, not a verified
normal-mode coverage event or correctness probability. Image and patch score
normalization stay separate. The decision is anomalous when the fused image
score is at least T. Pixel score thresholds are handled separately below.

### Selection and preservation rule

A selectable hybrid must cause **zero detected-to-missed transitions against
both the matched original SAFAL and original fixed-average controls** on the
development cases. Each comparator's previously detected anomalous case must
remain detected. This does not mean zero total missed defects: cases missed by
both controls may still be missed. Nor does it guarantee preservation on new
images or permit concealed false-alarm increases.

Among eligible candidates, choose the largest development accuracy. Resolve
ties deterministically by:

1. Higher mean per-episode image AUROC.
2. Fewer false-positive decisions.
3. Fewer scalar parameter changes relative to the original configuration.
4. The canonical parameter identifier.

Save every candidate's values, counts, metrics, eligibility and rejection reason.
Do not choose a category-specific winner after inspecting outcomes. If no
eligible hybrid exists, report the failed search; do not relabel an endpoint
control as a hybrid or relax the gate after seeing results.

## Stage 2: isolated feature comparisons

Keep the Stage 1 winner's scoring/fusion/decision parameters fixed. Compare the
original representation against exactly two isolated alternatives:

| Representation | Resolution | Zero-based blocks |
| --- | ---: | --- |
| Original mixed-layer mean | 224 | 2, 5, 8, 11 |
| Higher-resolution mixed-layer mean | 336 | 2, 5, 8, 11 |
| Late-layer mean | 224 | 8, 9, 10, 11 |

All use the same frozen ViT-B/14, raw arithmetic layer mean, same original
support/calibration/query IDs and identity views. The 336-pixel comparison has
more patches; it does not add independent support images. There is no new
768-configuration search per representation and no combined 336/late variant.

Refit normal banks and recalibrate the four normal images in the changed
representation; do not carry incompatible numeric cutoffs across feature spaces.
Use the same preservation constraints and accuracy/AUROC/false-positive ordering
as Stage 1. The exact Stage 2 ordering is: descending accuracy, descending
mean per-episode image AUROC, ascending false positives, ascending changed
scalar parameters, ascending feature changes, parameter identifier, then
feature identifier. Thus feature-change preference precedes the identifier
tie-breakers. The original representation remains a candidate.
Save raw branches, normalization, weights and diagnostics for interpretation.

## Unexecuted localization-only smoothing proposal

The implemented configuration records smoothing as **not run**. Current
localization outputs use unsmoothed, bilinearly restored 256×256 metric maps;
native query masks are opened only for offline evaluation and resized with
nearest-neighbor interpolation. No Gaussian-control result is available from
this protocol.

A possible separately declared follow-up would compare unsmoothed maps with
a fixed 3×3 Gaussian filter of sigma 4 at the same metric resolution. It would
require recalibrating each processing path's normal pixel cutoff using the
four calibration images before inspecting localization outcomes. Image scores/
decisions would remain unchanged, so smoothing would not select or improve an
image-accuracy winner. Report both paths if that comparison is actually run;
do not infer a result from the paper's filter setting.

This proposal is neither another image-parameter search nor permission to
select pixel thresholds from evaluation masks. Offline F1-max remains an oracle
diagnostic; its optimizing threshold does not enter prediction. The present
metric-resolution outputs are not a full native-resolution benchmark claim.

## Freeze before independent image verification

Write the global chosen scoring parameters and representation to
`selection.lock.json` before the verification command. Verification uses 100
preselected native images excluded from the available known historical query
IDs and current development queries. Their lock records the exposure audit,
selection algorithm, hashes and balanced normal/anomaly counts. The same five
already-studied categories, support seeds and k+4 information budget remain.

This is a **conditional image holdout in development-exposed categories**. The
known-history exclusion does not prove a universally untouched dataset history
or pristine category-level generalization. Label metadata may balance cohort
selection; the held-out scores, masks and decision errors must not choose PCA
variance, normal quantiles, fusion, threshold, representation or a new search.

After locking, evaluate the chosen configuration and both original controls on
the identical verification cases. Report accuracy, false alarms, missed defects,
per-case detection losses/gains and conditional paired uncertainty. Keep query
IDs and shared support draws as resampling units; repeated method/shot cases and
pixels are not independent samples. If the winner fails to improve or loses
defect detections, report that result without retuning on this verification set.

## New inference interface and probability limits

The old error head estimates correctness of a different locked SAFAL decision
and feature/score regime. Changed fusion, representation, calibration or T
changes its event and covariates. It is omitted from the tuned prototype rather
than presented as calibrated new confidence. Compatibility/uncertainty remain
diagnostics. A future error head would require independently declared source
fitting and outcome-calibration data for the selected decision rule.

Use the existing Python 3.12 CPU installation and verified encoder/data assets.
The tuning JSON specifies the development run, normal inputs, reserved image
lock and permitted representation alternatives. Keep all output separate from
earlier trained artifacts.

```bash
python -m safe_iad.safal_tune tune --config configs/safal_tuning_20261014.json --output /tmp/safal_tuning_20261014
python -m safe_iad.safal_tune verify --config configs/safal_tuning_20261014.json --output /tmp/safal_tuning_20261014
```

The independent tuned prediction command accepts the new model prefix and real
query image, with explicit verified encoder asset paths:

```bash
python -m safe_iad.safal_tuned_predict --model /path/to/tuned/model --image /path/to/query.png --output /path/to/new/prediction --source-dir /path/to/dinov2-source --checkpoint /path/to/dinov2_vitb14_pretrain.pth --cache-root /path/to/feature_cache --threads 3
```

Use the new serialized model with this command; do not overwrite an older
checkpoint or feed it into the old inference path while claiming equivalent
semantics. The model carries chosen parameters, cutoff provenance, support IDs,
feature/encoder bindings and implementation hashes. Dataset images and frozen
DINOv2 weights remain separate from a code/fitted-bank download.

The report generator, `safal_tuning_report`, summarizes completed machine-readable
outputs. Exact selected values, run commands, test/probe scope and observed
development/verification outcomes belong in the final report after execution.
This protocol does not claim a gain before those checks, and “best” means the
best eligible configuration in this declared development search—not a global
optimum, SOTA result, production guarantee or faithful published benchmark.

## Completed development search and locked verification

The executed search recorded all 768 configurations, including 576 eligible
hybrids. Of those hybrids, 294 met the zero-development-detection-loss gate.
The highest eligible feasible development accuracy was **81.33%**; the best
accuracy among every grid cell, including endpoint controls and rejected
candidates, was 81.67%. These are post-selection development measurements.

The locked global recipe retained the original 224-pixel mixed-layer features:

| Setting | Selected value |
| --- | --- |
| PCA explained variance | 0.99 |
| Normal empirical quantile | 0.90 |
| Image aggregation | Top 1% patch-score mean |
| Fusion | Fixed weighted average |
| Search / PCA weights | 0.75 / 0.25 |
| Image threshold | 1.0 |
| Resolution / zero-based blocks | 224 / `(2,5,8,11)` |

The selected recipe is fixed fusion, not an adequacy-conditioned winner. Neither
isolated representation alternative displaced it under the recorded ordering
and preservation constraint. Smoothing remained unexecuted. The selected
development recipe produced 244 correct decisions in 300 repeated cases,
compared with 243 for original SAFAL and 240 for fixed averaging.

After locking, the independent image check evaluated 100 native images across
the same five previously studied categories, with three support draws. It
produced 300 paired cases and 900 method records. Its recorded outcomes were:

| Method | Verification accuracy | Missed-defect rate | False-alarm rate |
| --- | ---: | ---: | ---: |
| Original SAFAL | 76.33% | 24.67% | 22.67% |
| Original fixed average | 77.67% | 20.00% | 24.67% |
| Selected recipe | 77.33% | 20.00% | 25.33% |

Selected-minus-original accuracy was +1.00 percentage point, with a conditional
95% crossed-bootstrap interval of **[−2.33, +4.33]** points. Selected-minus-fixed
accuracy was −0.33 point, with interval **[−3.33, +3.00]**. Both include zero;
**an accuracy improvement is not established by this verification**.

Against original SAFAL, the selected detector lost no recorded detections and
recovered seven missed-defect cases affecting seven images, while adding four
false alarms. Against fixed averaging, it lost three detected-defect cases
affecting three images and recovered three cases affecting three images; it
added two false alarms and removed one. These are dependent query/support
events, and lost/recovered image sets may overlap across draws. The development
preservation constraint therefore did not guarantee preservation against fixed
averaging on the verification images.

The report and figures preserve these outcomes without further parameter
selection from verification. Their scope is conditional image verification in
five development-exposed categories, not full-benchmark generalization,
calibrated reliability or deployment acceptance. Machine-readable `summary.json`,
`selection.lock.json` and verification predictions contain the full precision,
case identities, cutoffs, chronology evidence and comparison assumptions.
