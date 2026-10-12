> Archived exploratory variant: this run used category-disjoint native-test labels for calibration. It does not satisfy the latest literal prohibition on native-test defect labels in hyperparameters. The default normal-only calibration run is /workspace/reports/hybrid_pipeline_strict; retain these earlier results for audit.

# Verified real-data framework run

The requested central runner and empirical hybrid are implemented and the declared pilot completed. This is tested research software, not validated production inspection or a reproduction of the papers' headline tables.

## What executed

- Physical verification of all 20,089 retained real images: MVTec AD 5,354; VisA 10,821; AD 2 public/train/validation 3,914. Masks, native dimensions and split content checked.
- Three baseline variants finished before hybrid evaluation: transparent multilayer NN; the official supported AnomalyDINO force_no_mask_no_rotation scoring variant; the official SubspaceAD linear PCA/reconstruction core with the declared common-backbone adapter.
- Frozen official pretrained DINOv2 ViT-B/14, pinned source/checkpoint, actual intermediate tokens; no random-weight substitution. Blocks 2/5/8/11, long-edge 224 aspect-preserving padding for the hybrid/NN. Exact geometry is in each prediction; baseline transforms follow their declared variants.
- k=1,2,4, three seeded nested training-normal support draws, strict support budgets, empty candidate registries and no acquisition. Five categories, four fixed stratified queries/category: 20 unique evaluation queries, 180 query-group/method/support episodes, 720 evaluation prediction records. There are 12 separate calibration queries and 144 calibration prediction records. Reused queries/support draws are correlated.
- Main cutoffs from reserved capsule/fryum calibration roles only. AD 2 cutoffs from reserved normal-only can validation images using mean+3std. Adequacy threshold 0.5 is predeclared; no target-label tuning. No probabilities fitted.
- Native float32 AUROC/AP/F1 metrics and offline F1-Max tables. Saved native maps use explicit float16 compression; scores are evaluated before compression. Test F1-Max is diagnostic and its maximizing cutoff never enters decisions.
- 36 actual AD 2 public TIFF/PNG pairs, each checked with the official dtype/binary code; TIFF values match saved defect evidence. The official full-submission check correctly rejects this incomplete public preview. No private images, predictions, server scores or upload are claimed.
- All 43 unit/contract tests passed. Every recorded decision, support budget, calibration origin, finite native map, adequacy bound and local evidence envelope passed real-output audit. 1592 immutable artifact hashes checked.

## Method

Full definitions and source fidelity are in /workspace/tools/README.md. PCA retains 99% observed support variance. Positive-spectrum Shannon entropy is normalized by log(rank) and scaled by excess query density distance relative to a support 95th-percentile density bound. This is an empirical diagnostic in [0,1], not an adequacy probability or independent-reference sample-size estimate.

The evidence envelope is max(local L2 NN, global PCA orthogonal residual, nearest-token orthogonal residual). It preserves local evidence. Low mean adequacy triggers unresolved/reference-insufficient while retaining that raw evidence and its flag. This separation of outputs does not mathematically identify actual defects versus missing legitimate normal modes.

## Actual results

Values below are mean over the same queries across three support draws. They are feasibility measurements, not full-benchmark estimates or statistical population confidence intervals. All k2 values, native pixel AUROC, image/pixel AP, offline F1-Max and F1 at locked calibration cutoffs are retained in metrics.csv/json.

| Dataset/category (role) | Method | Image AUROC k1 / k4 | Pixel AP k1 / k4 | Hybrid coverage k1 / k4 |
|---|---|---:|---:|---:|
| mvtec_ad/cable (validation) | transparent_nn | 1.0000 / 1.0000 | 0.5271 / 0.6021 | — |
| mvtec_ad/cable (validation) | anomalydino | 1.0000 / 1.0000 | 0.5445 / 0.5974 | — |
| mvtec_ad/cable (validation) | subspacead | 1.0000 / 1.0000 | 0.6073 / 0.6363 | — |
| mvtec_ad/cable (validation) | support_hybrid | 1.0000 / 1.0000 | 0.5271 / 0.6021 | 100.0% / 100.0% |
| visa/macaroni2 (validation) | transparent_nn | 0.7500 / 0.8333 | 0.002119 / 0.007293 | — |
| visa/macaroni2 (validation) | anomalydino | 0.3333 / 0.5000 | 0.0405 / 0.07933 | — |
| visa/macaroni2 (validation) | subspacead | 0.5000 / 0.4167 | 0.0336 / 0.06744 | — |
| visa/macaroni2 (validation) | support_hybrid | 0.7500 / 0.8333 | 0.002119 / 0.007293 | 100.0% / 100.0% |
| mvtec_ad/bottle (final_test) | transparent_nn | 1.0000 / 1.0000 | 0.8561 / 0.8664 | — |
| mvtec_ad/bottle (final_test) | anomalydino | 1.0000 / 1.0000 | 0.8195 / 0.8291 | — |
| mvtec_ad/bottle (final_test) | subspacead | 1.0000 / 1.0000 | 0.7312 / 0.7647 | — |
| mvtec_ad/bottle (final_test) | support_hybrid | 1.0000 / 1.0000 | 0.8561 / 0.8664 | 100.0% / 0.0% |
| visa/capsules (final_test) | transparent_nn | 0.8333 / 0.9167 | 0.05239 / 0.1123 | — |
| visa/capsules (final_test) | anomalydino | 0.6667 / 1.0000 | 0.4232 / 0.4644 | — |
| visa/capsules (final_test) | subspacead | 1.0000 / 1.0000 | 0.2193 / 0.1767 | — |
| visa/capsules (final_test) | support_hybrid | 0.8333 / 0.9167 | 0.05239 / 0.1123 | 100.0% / 100.0% |
| mvtec_ad2/can (stress_final_public) | transparent_nn | 0.0833 / 0.6667 | 1.342e-05 / 1.755e-05 | — |
| mvtec_ad2/can (stress_final_public) | anomalydino | 0.1667 / 0.3333 | 1.263e-05 / 7.656e-05 | — |
| mvtec_ad2/can (stress_final_public) | subspacead | 0.5000 / 0.2500 | 1.189e-05 / 1.799e-05 | — |
| mvtec_ad2/can (stress_final_public) | support_hybrid | 0.0833 / 0.6667 | 1.346e-05 / 1.754e-05 | 100.0% / 100.0% |

Hybrid accepted 165/180 query/support/shot inspections (91.7%); 107/165 accepted decisions were correct (64.8%). These counts reuse only 20 unique evaluation images and should not be interpreted as independent trials. They do not establish a reliability guarantee or a deployment false-alarm rate.

At the fixed adequacy cutoff, the hybrid accepted all 36 AD 2 can inspections while only 16/36 image decisions were correct. High diagnostic adequacy did not indicate correct inspection on this slice. It accepted 0/12 bottle inspections at k=4 despite mean image AUROC 1.0000. The proposed entropy/density rule therefore does not support reliable three-way classification in this pilot. This is not evidence of ground-truth support insufficiency: that event has not been annotated.

The saved hybrid envelope equals the saved local map exactly for 117/180 evaluation records; 2.9759% of stored native pixels exceed local evidence. This comparison is at the explicitly stored float16 precision. A nearly unchanged envelope is a negative ablation finding; abstention is separate from raw localization.

The AD 2 stress slice and weak/variable capsule localization are material limitations. Coarse 224 inputs can lose very small defects. Calibration uses only tiny category-disjoint pilot samples, and transferred cutoffs can fail even when ranking AUROC is high. Review the plotted locked-cutoff F1 and coverage, rather than treating AUROC alone as inspection reliability. Unresolved cases are not automatically correct or safe.

The adequacy precision curves explicitly use the event "image decision correct at the locked detector cutoff". This is a correctness/coverage proxy, not ground-truth support adequacy. Future intervention validation must justify an adequacy event using declared validation/source data. No learned benefit predictor is fitted; the earlier source-only M2 targets and oracle separation remain available as separate tools.

## Reproduction and remaining scope

```bash
bash /workspace/tools/install_runtime.sh
cd /workspace/tools
/workspace/venvs/safe_iad/bin/python -m safe_iad.run_pipeline --config configs/experiment_plan.yaml --reproduce true
/workspace/venvs/safe_iad/bin/python /workspace/tools/validate_pipeline_run.py --run /workspace/reports/hybrid_pipeline --output /workspace/reports/hybrid_pipeline_validation.json
/workspace/venvs/safe_iad/bin/python /workspace/tools/plot_pipeline.py --run /workspace/reports/hybrid_pipeline --output /workspace/reports/hybrid_pipeline_summary.png
```

Repeated completed invocation re-verifies datasets, checks the immutable ledger and independently recomputes one actual query per method with feature cache bypass. This is not a new full rerun of all episodes; use --output with a new directory for that. The interrupted preprocessing audit attempt was preserved at /workspace/reports/hybrid_pipeline_preprocessing_audit_attempt; scientific settings were unchanged when preprocessing version provenance was completed. Interrupted-job recovery has not been fully validated.

The full plan declares 2,871 queries over 20 reserved validation/final/public categories, excluding source/calibration categories. It has not been executed. Native float16 diagnostic maps alone project to about 1,067 GB before compression, excluding calibration, feature caches and public TIFFs; this 32 GB volume lacks suitable storage. The full plan uses bounded-memory float16 histogram pixel metrics explicitly exact for quantized scores, not original float32 scores, and has a disk preflight guard.

Faithful scoring-core parity tests do not establish published-table reproduction. AnomalyDINO's default ViT-S/14 448 agnostic preprocessing and SubspaceAD's published ViT-G/registers 672/30-augmentation recipe are distinct, unrun configurations. Full AD 2 lighting/private scenarios are unrun. These data/results do not justify novelty, state-of-the-art, production readiness or acceptance claims.

Tools remain standalone under /workspace/tools because the selected ennayriomar/ennayriomar checkout is a profile README. Its source was preserved. Research repository integration is still awaiting the repository identity.

Artifacts: immutable metrics.csv/json; split_manifest.json with all sampled support/query IDs, prior roles and byte fingerprints; runtime_versions.json; source_provenance.json; backbone.json; per-episode model/threshold/prediction/maps files; artifact_ledger.json; external real-output validation and plot files. Current environment startup/install instructions are saved separately as a draft for review/publishing.
