# Repository audit before Milestone 3

All 44 existing tests were executed again and passed. Those unit/contract tests use synthetic tensors/fixtures; historical real-data runs are separate evidence. Existing source, interfaces, strict pilot results, and published archives are preserved.

| Component | File | Status | Integrated? | Synthetic-tested? | Real-data-tested? | Required action |
|---|---|---|---|---|---|---|
| Dataset loaders/physical verification | safe_iad/verify_dataset.py | implemented | yes | yes | historical all 20089 real images | Use verified roots; record new pilot inputs and byte hashes |
| Real frozen backbone/cache | safe_iad/patch_nn.py | implemented | yes | yes | actual pretrained ViT-B/14 verified | Preserve M2 final-layer square224 contract; verify provenance on loading |
| Strict fixed-shot baselines | safe_iad/run_pipeline.py; baselines.py | implemented scoring cores | yes | yes | five-category strict pilot | Preserve adapters and fidelity limits; full benchmark remains unrun |
| Counterfactual training | safe_iad/build_training_targets.py | implemented | yes | yes | 384 source-only rows | Broaden categories/support sizes; harmful supervision has one independent group |
| Reference policies/budgets | safe_iad/acquisition.py | implemented b0/1 | yes | yes | M2 paired real pilot | Add label-free learned policy; charge all candidate patch probes |
| Benefit prediction | safe_iad/counterfactual.py feature summaries | disconnected inputs; no learner | no | no | not evaluated | Fit small signed-benefit model with grouped source selection |
| Support adequacy/decision | safe_iad/hybrid.py | implemented heuristic; separate from acquisition | partial | yes | negative reliability pilot | Do not equate adequacy or utility with correctness; preserve raw evidence |
| Defect preservation | safe_iad/run_acquisition_pilot.py | score-drop diagnostic only | partial | yes | real score drops recorded | Add locked-cutoff missed defects/false alarms/IoU and harmful intervention checks |
| Calibration/reliability/statistics | safe_iad/pipeline_metrics.py | cutoffs and ranking metrics; several requested metrics missing | partial | yes | strict pilot cutoffs | Add bounded AU-PRO/risk coverage and paired dependent statistics; probability calibration stays separate |
| Missing-support stress | no integrated command | absent | no | no | not evaluated | Build proxy normal-feature groups from allowed training normals only |
| Official AD2 export | safe_iad/official_ad2.py | implemented public preview/checks | yes | yes | 36 public TIFF/PNG pairs | No private results; lighting/full stress deferred until feasibility gate |
| Test execution | tests/ | 44 existing tests passed freshly | yes | synthetic/contract | historical real pilots separate | Add focused leakage/grouping/metrics/learner tests; never call synthetic tests real-data evidence |

## Research gate

The existing source target set has 380 positive and four negative benefits; all negative rows share one carpet source image/support draw. Adding NN references can only reduce distances, so normal-query loss benefit does not establish adequacy separation. Decreased true-defect scores can accompany positive declared utility. The old final bottle/capsules pilot has already been inspected and published.

Next: broaden source-only training over declared meta-training categories and k=1/2, select model settings using grouped source folds and permitted normal/synthetic validation data, then run paired real-query evaluation on reserved validation categories. Detector thresholds use separate calibration normal data; native test defect labels never select models or thresholds. Deployed selection occurs before masks are opened. Learned selection scans every candidate patch memory and reports that cost.

Stop expansion if learned acquisition does not exceed the strongest simple selector on held-out validation utility, if harmful/missed-defect behavior worsens, or if source-negative coverage remains inadequate. Any stop produces complete code, pilot artifacts, and an explicit negative report. Full benchmark/AD2 lighting/private protocols and probability calibration cannot be declared complete without execution.
