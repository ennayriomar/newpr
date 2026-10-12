# Milestone 2: counterfactual reference feasibility

Implemented and executed using the standalone safe_iad tools. The original research repository is still unavailable; the selected checkout remains a profile README. No claim of integration into that repository is made.

## Protocol and loss

Each query is an independent inspection episode for budgeting: begin with the same k=1 support used in Milestone 1, use the same 16 verified-normal training candidates for all policies, and add exactly one normal reference for random/nearest/diversity/oracle. Reset S for the next query. The no-acquisition control adds zero. Eight queries share a support/pool draw solely for paired reporting; these groups aggregate eight reference-use events rather than asserting a category-level budget of one. This is Protocol B, not strict 2-shot learning.

The fixed loss is class-balanced pixel margin MSE, with margin 1.0 in uncalibrated L2-score units. For normal pixels, loss is m²; for defect pixels it is max(0,1−m)². An anomalous image averages its normal- and defect-region mean losses with equal weights; a normal image uses its normal-region mean. U = L(before) − L(after). Positive U means this declared loss decreased, not necessarily that detection ranking, missed-defect rate or inspection reliability improved. An image-level variant accepts the actual detector image score rather than redefining its aggregation.

Global-reference selectors use the normalized mean of normalized patch descriptors, not a claimed faithful CLS-based external method. Random, nearest-global and diversity inputs contain features, opaque query IDs, candidate IDs and seeds only. Their choices occur before query masks are opened. Oracle is isolated to offline evaluation and chooses the best forced single-reference U; it is unattainable at deployment and is not an AUROC/AP oracle.

## Source-only target construction

Generated 384 target rows from 12 real normal queries and 12 deterministic cut/paste queries, all derived from carpet/candle normal training data. References and candidates exclude every reserved query source image globally within each category. Exact source-query/reference file-hash overlap was checked and is zero. No final-test defect labels construct these targets.

Only 4 of 384 rows have negative benefit; 380 have positive benefit. This tiny, correlated source set underrepresents harmful interventions. Cut/paste changes were verified to be nonzero, but realism as industrial defects is unverified. Do not balance this set with final evaluation labels.

The category-role manifest covers all 20,089 retained images. Main-benchmark meta-training, validation, calibration and final categories are disjoint. Source native-test images are excluded from training targets. Native test images of designated validation/calibration categories are reserved for those roles; they are not final-query data. AD 2 remains a stress benchmark; its defect-free validation is partitioned into 154 validation and 148 calibration images, with no positive-class probability calibration claimed.

Nineteen inference-only feature summaries were saved, including nearest/mean-five-nearest distances, distinct-reference contribution, population covariance trace, leave-one-reference-out sensitivity, global support distance and candidate effects. At k=1, LOO sensitivity is absent and loo_valid=false. Its numeric feature slot is explicitly imputed with a separate missingness indicator, not represented as perfect stability. After one addition, k=2 LOO sensitivity is defined. Dispersion direction is not assumed to imply adequacy. M_defect remains raw nearest-neighbor evidence; A_support and predicted U_ref are not trained or claimed.

## Real-query paired results

Thirty policy/support-draw summaries contain 240 query/policy inspections: 48 per policy, with only 16 unique query images reused across three support draws. All pre-acquisition maps exactly matched the corresponding Milestone 1 baseline. These small descriptive means have no confidence intervals or significance claims.

| Dataset/category | Policy | Added/query | Image AUROC | Pixel AP | Mean U | Harmful / 24 | Mean true-defect score drop |
|---|---|---:|---:|---:|---:|---:|---:|
| mvtec_ad/bottle | none | 0 | 1.0000 | 0.8547 | 0.00000 | 0 | 0.00000 |
| mvtec_ad/bottle | random | 1 | 1.0000 | 0.8570 | 0.00963 | 0 | 0.01421 |
| mvtec_ad/bottle | nearest_global | 1 | 1.0000 | 0.8661 | 0.02370 | 0 | 0.04976 |
| mvtec_ad/bottle | diversity | 1 | 1.0000 | 0.8654 | 0.01006 | 0 | 0.04169 |
| mvtec_ad/bottle | oracle | 1 | 1.0000 | 0.8676 | 0.02449 | 0 | 0.04852 |
| visa/capsules | none | 0 | 0.6875 | 0.0063 | 0.00000 | 0 | 0.00000 |
| visa/capsules | random | 1 | 0.7083 | 0.0088 | 0.01725 | 1 | 0.01593 |
| visa/capsules | nearest_global | 1 | 0.6250 | 0.0197 | 0.02768 | 3 | 0.01986 |
| visa/capsules | diversity | 1 | 0.6250 | 0.0174 | 0.01111 | 4 | 0.01523 |
| visa/capsules | oracle | 1 | 0.7083 | 0.0240 | 0.03129 | 0 | 0.00461 |

A harmful case means U<−1e−8 under the declared loss. True-defect score drops are measured only on the 12 anomalous query/support cases per dataset/policy. They flag possible explanation-away behavior, not demonstrated missed defects: no validation-selected threshold, missed-defect rate or IoU has been evaluated.

What worked: source-only target construction, deterministic label-free selectors, explicit per-query reference counts, original-resolution pre/post maps, diagnostics and oracle separation. Thirteen new synthetic policy/leakage/missingness tests passed; they supplement the real-query runs.

What limits progress: capsules localization remains weak. Nearest-global improves mean pixel AP from 0.00634 to 0.01970 while image AUROC decreases from 0.6875 to 0.625, and 3/24 interventions worsen the loss. Diversity worsens it in 4/24 cases. Even loss-beneficial choices can reduce true-defect region scores. A learned predictor of this loss should not be presented as a reliability guarantee.

Before Milestone 3: check utility/defect-preservation criteria on the declared validation categories and broaden source-only supervision to represent harmful interventions. Use training and validation data for changes; do not tune from these locked final evaluation slices or feed their oracle rows into training. A small signed-benefit regression/ranker is the appropriate first learned model; harmful-event classification/calibration would need better-supported negative examples. No learned predictor, calibrated output, adequacy combination or reliable three-way decision is completed.

## Information and computation accounting

The candidate pool has 16 complete normal images. Pool backbone extraction/cache use is shared and logged. Random uses no global ranking scan, nearest/diversity scan 16 global descriptors, and each non-oracle selected detector uses one candidate patch memory. The offline oracle probes all 16 candidate patch memories and uses query truth. All 16 counterfactual probes are computed for offline comparison; they are never inserted together into a detector bank. Shared-probe times are not controlled per-policy deployment latency measurements. Every acquired reference-use event is recorded in predictions.jsonl.

## Executed commands

```bash
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.build_training_targets --config /workspace/tools/configs/milestone2.json
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.run_acquisition_pilot --config /workspace/tools/configs/milestone2.json
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m unittest discover -s /workspace/tools/tests -p 'test_acquisition_synthetic.py' -v
/workspace/venvs/safe_iad/bin/python /workspace/tools/plot_acquisition_pilot.py --results /workspace/reports/milestone2/evaluation/episodes.json --output /workspace/reports/milestone2/acquisition_summary.png
```

Artifacts: split_manifest.json/jsonl; training_targets/*.jsonl and summary.json; evaluation/* manifests, candidate rows, predictions, diagnostics, original-resolution maps and metrics; validation.json; synthetic_training_quality.json; acquisition_summary.png/pdf. Evaluation candidate rows are marked final_evaluation_only/never_use_for_training.

This milestone supports only k=1 and one-step b=0/1. Sequential b=2/4, learned benefit selection, category-wide cumulative acquisition budgets, AD 2 robustness experiments and full benchmarks are unimplemented/unrun. The M1 pilot has validated resume; interrupted-job resume for these M2 commands has not been validated. Configuration and source provenance are recorded; changing a configuration requires a new output directory. No private-server result, novelty, state-of-the-art or acceptance claim is made.
