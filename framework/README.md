# Safe IAD research framework v0.4.0

This package implements frozen DINOv2 feature extraction, transparent patch NN,
official AnomalyDINO and SubspaceAD scoring-core adapters, source-only signed
benefit learning, paired reference-acquisition pilots and an empirical
support-diagnostic hybrid. The research repository is
https://github.com/ennayriomar/newpr; executable source is provided under
`framework/`, with the source ZIP placing the same package under `tools/`.

The framework is research software with tested contracts and real-data pilots.
Full benchmark reproduction, deployment reliability, calibrated probabilities,
support-adequacy ground truth and production acceptance are not established.

## Current M3 result and verification

The completed learned-benefit feasibility pilot stopped at the predeclared
gate: `advance_to_full_experiments=false`. Learned acquisition's mean observed
loss benefit was 0.033191, compared with 0.031984 for the strongest simple
selector, nearest-global. Utility and harmful-intervention checks passed, but
defect preservation failed: four correlated detected-to-missed inspection
records occurred at locked cutoffs, and defect-pixel recall fell on every
dataset/shot slice. The matched omission/coverage controls did not establish a
consistent missing-support false-alarm effect. The model and cutoffs were not
retuned after this finding; full learned-acquisition experiments were stopped.

Read `/tmp/safe_iad_milestone3/research_report.md`, `evaluation/gate.json`,
`validation.json` and `real_weight_reproduction.json`, or their bundled copies.
In the GitHub repository, use the [M3 research report](../results/milestone3/research_report.md),
[artifact audit](../results/milestone3/validation.json),
[real-query probes](../results/milestone3/real_weight_reproduction.json) and
[stopping gate](../results/milestone3/evaluation/gate.json).
The run used real pretrained DINOv2 and the existing square-224, final-layer
normalized-patch NN detector. Source-only grouped cross-validation selected the
benefit model. Normal-only reserved calibration images set cutoffs; native
validation masks and the oracle were confined to offline evaluation. M3 does
not replace the earlier hybrid model or reproduce a new external detector.

The fresh 97-test run passed. These synthetic/unit/contract tests are distinct
from real-data evidence. The completed M3 artifact audit verified 39 stage
ledgers, 1,903 unique output files and 547 unique input files; it read 672 native
map exports and 672 diagnostic exports. It checked 576 inspection records from
20 unique query images, paired policies, reference budgets, source-only model
selection, normal-only cutoffs, oracle isolation and retained raw evidence.
This audit did not rerun backbone extraction or all float32 metrics.

Two independent real-query probes, one per main dataset, bypassed the feature
cache. Their recomputed float32 features, selected references, predicted
benefits, image scores, adequacy maps and stored pre/post maps matched exactly.
The VisA probe retained an actual detected-to-missed case. These two probes are
not a complete independent rerun of all episodes or an accuracy guarantee.

## Current startup and M3 commands

Use Linux, Python 3.12 and the documented `/workspace` layout. Restore this
package as `/workspace/tools`; obtain verified native datasets, the real
official checkpoint and AD2 utility source at their documented locations.
The installer clones the pinned official Git dependencies and requires network
access. Bundled vendor snapshots lack Git metadata and cannot replace those
checkouts unchanged. No CUDA runtime or arbitrary-path installation is claimed.
The source ZIP's top-level `BUNDLE_README.md` gives paths, licensing and fresh-run steps.

```bash
bash /workspace/tools/install_runtime.sh
cd /workspace/tools
source /workspace/venvs/safe_iad/bin/activate
python -m unittest discover -s tests -v
python -m safe_iad.build_benefit_targets --config configs/milestone3.json
python -m safe_iad.train_benefit --config configs/milestone3.json
python -m safe_iad.run_benefit_pilot --config configs/milestone3.json
python plot_benefit_pilot.py --results /tmp/safe_iad_milestone3/evaluation/episodes.json --output /tmp/safe_iad_milestone3/benefit_summary.png
```

The existing run uses `/tmp/safe_iad_milestone3`. For a fresh experiment, copy the
JSON configuration and set new `output`, `generated_root` and `feature_cache`
directories before invoking all three stages. Copied reports alone cannot
satisfy resume checks: ledgers verify absolute input paths, implementation
hashes, datasets, generated queries and checkpoint bytes. Preserve prior runs.
Do not advance to full experiments after the recorded negative gate. M1/M2
commands and the separate strict hybrid remain available as historical pilots;
their results do not validate M3 reliability.

## Earlier strict hybrid pilot: run and verification scope

Use the existing datasets and official pretrained checkpoint. Run the tested
environment installer with `bash /workspace/tools/install_runtime.sh`. It pins
the CPU runtime and three official dependency sources; it does not redownload
the large datasets. No CUDA device is present.

```bash
cd /workspace/tools
/workspace/venvs/safe_iad/bin/python -m safe_iad.run_pipeline --config configs/experiment_plan.yaml --reproduce true
/workspace/venvs/safe_iad/bin/python -m unittest discover -s tests -v
```

The runner physically verifies all three roots, pairs native masks, loads the
real frozen checkpoint, fits/calibrates/evaluates all three baselines, and then
fits/calibrates/evaluates the hybrid. Verification errors, mismatched source
pins, changed input fingerprints, overwritten metrics, nonfinite evidence and
exceeded disk/memory limits stop the run. It never substitutes random weights
or silently removes query images. It uses the explicit category/image roles
from the earlier source-supervision manifest.

`--reproduce true` enables the audited deterministic run. A repeated completed
invocation re-verifies the physical datasets, checks the artifact SHA256 ledger
and recomputes a real query for every method with backbone cache bypassed.
This is an integrity/resume check, not an independent rerun of every episode.
Use `--output /workspace/reports/another_run` for another complete evaluation.
Changing code/config/data requires a new output directory. Interrupted-run
behavior refuses conflicting artifacts and recomputes existing episode maps;
an interrupted-run restart has not been validated as a full recovery test.

The default plan is a feasibility pilot: five categories (two category-disjoint
validation categories, two locked final slices and one public AD 2 stress
category), four queries per category, three support draws and k=1,2,4. The same
queries are reused across draws; they are not independent populations. Support
sets contain exactly k training normals, are nested within a draw, and have
empty candidate pools and zero acquisition budgets. AD 2 private images/masks
are absent. Lighting-specific robustness is not established by this slice.

`configs/experiment_full.yaml` declares the full native queries in all reserved
validation/final categories and all eight AD 2 public categories. Meta-training
and calibration categories retain their roles and are excluded from the final
aggregate. This plan is not the full published benchmark recipe. It has not
been executed, and native map output would require more storage. Its pixel
metrics are exact for explicitly quantized float16 scores using constant-size
histograms; they are not described as exact float32 metrics. The default pilot
uses exact float32 native-pixel metrics with explicitly float16 saved maps.

## Earlier strict hybrid pilot: method and interpretation

The common backbone is the official pretrained DINOv2 ViT-B/14, frozen and in
eval mode. For the hybrid/transparent NN, blocks 2,5,8,11 (zero-based) are
normalized per layer and concatenated with scale 1/sqrt(4). Images resize by
their long edge to 224, with edge padding only to a multiple of 14. Native maps
are reconstructed on the padded canvas, trimmed to the resized content, then
interpolated to original size. No original-image region is cropped. The small
resolution can miss tiny defects; padding/patch interpolation can introduce
boundary effects. Exact transform geometry and cache keys are recorded.

Let q and s be unit patch descriptors, mu the support mean, P=VV^T the fitted
PCA projector retaining 99% of observed variance, and s* the nearest support
token. The fields are:

- Local evidence: M_local = min_s ||q-s||_2.
- Global evidence: M_global = ||(I-P)(q-mu)||_2.
- Nearest orthogonal evidence: M_orth = ||(I-P)(q-s*)||_2.
- Defect evidence envelope: M_defect = max(M_local,M_global,M_orth).

The envelope prevents suppression of local evidence in this implementation;
it does not prove that either residual identifies actual defects. With nearly
complete PCA support reconstruction it may reduce to local NN. No map is
multiplied by adequacy. Reconstruction residuals also respond to legitimate
missing support modes, so defect/insufficiency remain empirically ambiguous.

For positive support covariance eigenvalues lambda_i, define p_i=lambda_i/sum
lambda, H=-sum p_i log p_i, h=H/log(r) for r>1 (zero for a degenerate spectrum).
Let d(q) be mean 8-nearest support-token distance, and rho the 95th percentile
of support-token density with each token's self match excluded. The diagnostic
is A_support(q)=clip(h exp(-max(0,d(q)/rho-1)),0,1). rho has an explicit 1e-6
floor. These patch observations are correlated; token counts are not numbers
of independent normal images. Entropy/diversity is not proven adequacy and
no calibration as a probability is claimed.

The image evidence is the mean of the floor top 1% of patch scores (at least
one). If native mean adequacy is below the predeclared 0.5 threshold, the action
is `unresolved/reference-insufficient`; otherwise the locked image cutoff
chooses `normal` or `defective`. Unresolved outputs preserve the raw evidence
flag and all maps for review. The acquisition boundary is exposed; M2 contains
separate one-step acquisition tools. This strict hybrid pipeline does not fit
the benefit learner introduced by the separate M3 experiment.

## Earlier strict hybrid pilot: baseline fidelity

- Transparent NN is an internal exact normalized patch-NN baseline; it is not
  called a complete PatchCore reproduction.
- [AnomalyDINO](https://github.com/dammsi/AnomalyDINO), commit
  b9d1c2648e3a5247437d4d953d907a8f3d994457: supported
  `force_no_mask_no_rotation` variant. Uses final normalized tokens, official
  short-edge resize/stride crop, FAISS exact normalized L2 squared/2 cosine
  scores, official image aggregation and native Gaussian-smoothed maps.
  Backbone/resolution/support draws are declared common settings. This is not
  the paper's ViT-S/14 448 agnostic preprocessing benchmark.
- [SubspaceAD](https://github.com/CLendering/SubspaceAD), commit
  ef56d5c8ab2f1feb7dda1c93b25cc3f73f0960d7: directly imports official float64
  streaming PCA, squared reconstruction scorer, map postprocessing and image
  aggregation. Uses square 224 inputs, raw mean features from the common
  ViT-B blocks, 99% variance and aug_count=0. Its common official backbone
  adapter replaces the upstream HuggingFace extractor. This is not the
  published ViT-G/registers 672/30-augmentation recipe. Independent PCA and
  reconstruction tests validate the scoring core, not complete paper parity.

Both dependencies retain their Apache-2.0 licenses. Read source_provenance.json
and per-episode model.json before comparing results. No reported paper numbers
are substituted for measurements from this pipeline.

## Earlier strict hybrid pilot: calibration, metrics and official export

Main-dataset detector cutoffs use held-out normal training images of reserved
capsule (MVTec AD) and fryum (VisA) calibration categories. Those query images
are explicitly excluded from calibration support banks. AD 2 uses only its
previously reserved normal validation calibration images. All cutoffs use
mean+3std, following the official utility's suggested normal-only baseline.
No native-test defect labels enter any default cutoff, feature weight or model
hyperparameter. The pilot has four calibration normals per dataset, in addition
to the k support images used for each calibration model; this extra normal data
is declared, and the AD 2 validation images are target-category normals. The
pilot sets are tiny and the procedure guarantees neither a false-alarm rate nor
a calibrated defect probability.

The retained initial exploratory run under /workspace/reports/hybrid_pipeline
used category-disjoint native-test labels for calibration and does not satisfy
the latest request's literal native-test-label restriction. The strict default
plan writes /workspace/reports/hybrid_pipeline_strict. Its scientific scoring
settings and evaluation queries/supports are unchanged; only the calibration
protocol was corrected. The initial implementation was preserved separately.

Immutable CSV/JSON tables contain image/pixel AUROC, AP, offline F1-Max and F1
at locked calibration cutoffs. Test F1-Max is an oracle diagnostic: its cutoff
never enters predictions/export/decision code. The adequacy precision curve
uses the explicitly named event "image decision correct at locked cutoff";
it is a correctness/coverage proxy, not ground-truth support adequacy. A true
adequacy precision measure requires an externally justified reference event.

Native AD 2 TIFF maps are float16, and thresholded PNGs are binary 0/255. Paths
are taken from the official loader convention, e.g.
`anomaly_images/can/test_public/bad/000.tiff`. Every exported file runs the
official utility's dtype/binary check. Public/validation examples are marked
local-only. Never rename them as private-test outputs.

For actual complete private predictions, this validator directly uses the
official all-category, all-file checks:

```bash
/workspace/venvs/safe_iad/bin/python -m safe_iad.official_ad2 --submission /path/to/actual_complete_submission
```

It correctly rejects a public subset. Private server scores are never guessed
or simulated; no upload is performed. Dataset rights remain MVTec's
CC BY-NC-SA 4.0 and VisA's CC BY 4.0. Commercial deployment is not established
by this research setup.
