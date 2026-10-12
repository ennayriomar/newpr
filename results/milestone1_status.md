# Milestone 1 status and evidence

The datasets, standalone verification tools, actual pretrained backbone and a small internal baseline pilot are working in this machine. Milestone 1 is not fully integrated: the supplied research checkout is still a profile README, and the actual anomaly-localization repository URL has not been provided. No existing research architecture was rewritten.

## Repository/component audit

The initial supplied-checkout audit is preserved in milestone1_repository_audit.md. Current helper status follows; integration means a standalone CLI, not integration into the unavailable research repository.

| Component | File | Status | Integrated? | Synthetic-tested? | Real-data-tested? | Required action |
|---|---|---|---|---|---|---|
| Actual research repository | Not supplied | Unavailable; selected checkout has only README.md | No | No research tests available | No | Provide actual repository URL |
| Dataset acquisition | tools/acquire_public_data.py | Complete; 3 archive hashes verified | Standalone | Failure guards passed | Actual archives | Integrate without replacing existing loaders blindly |
| Dataset loaders/verifier | tools/safe_iad/verify_dataset.py | All retained files passed | Standalone | Guard tests passed | AD 5,354; VisA 10,821; AD2 public 3,914 | Add explicit experimental split manifests after integration |
| Pretrained frozen DINOv2 ViT-B/14 | tools/verify_dinov2.py; official source cache | Loaded; frozen/eval/grid/repeat checks passed | Standalone | Not substituted with fixtures | Actual checkpoint and real VisA image | Preserve source/checkpoint provenance |
| Internal patch NN and map restoration | tools/safe_iad/patch_nn.py | Implemented; original-resolution maps exported | Standalone | Geometry/distance/budget guards passed | 24 pilot episodes | Higher-resolution and representative-category checks before performance claims |
| Deterministic feature cache | tools/safe_iad/patch_nn.py | Dataset/split/category/image/checkpoint/preprocessing/layer/content keys | Standalone | Provenance invalidation passed | Cache reuse and resume checked | Keep experimental inputs fingerprinted |
| Fixed-shot pilot and typed predictions | tools/safe_iad/run_baseline_pilot.py | k=1,2,4,8; 3 support draws; no acquisition | Standalone | Shared budget/overlap guards passed | 192 records; 16 unique queries | Expand only after integration and protocol review |
| Plotting | tools/plot_pilot.py | PNG/PDF generated from actual episodes | Standalone | N/A | Actual pilot results | Do not interpret draw ranges as confidence intervals |
| AnomalyDINO/SubspaceAD/PatchCore/FastRef | Not implemented | No reproduction or adaptation claimed | No | No | No | Verify original methods before adding labels/results |
| Adequacy/benefit/acquisition | Not implemented | Later milestones pending | No | No | No | Establish counterfactual benefit feasibility first |
| Calibration/thresholds/category-disjoint training | Not implemented | No calibrated probabilities or selected thresholds | No | No | No | Separate training, validation, calibration and final test |
| Full benchmarks/ablation/statistics/private server | Not run | No results claimed | No | No | No | Need integrated protocols, larger-resource planning and explicit evaluation scope |

## Baseline method and assumptions

Let z_p be the final normalized DINOv2 patch descriptor, e_p = z_p / ||z_p||_2, and B(S) the patch descriptors from exactly k verified-normal training references. The internal detector computes m_p = min_{b in B(S)} ||e_p - b||_2. Its image score is the mean of the largest ceil(0.01 P) patch scores. Bilinear interpolation restores the 16×16 score grid to the original image dimensions.

Preprocessing is RGB, full-image 224×224 Pillow bicubic resize, float32 /255, and ImageNet channel mean/std. Aspect ratios may change. The coarse grid is a limitation for tiny defects. No crop, test-label tuning, adequacy multiplication, calibration, learned acquisition or normal-bank insertion of query patches is used. This is an **internal DINOv2 patch NN baseline**, not a faithful AnomalyDINO or PatchCore implementation.

Official source commit: `7764ea0f912e53c92e82eb78a2a1631e92725fc8`. Checkpoint SHA-256: `0b8b82f85de91b424aded121c7e1dcc2b7bc6d0adeea651bf73a13307fad8c73`. The checkpoint checksum is locally recorded provenance, not a claimed publisher-provided checksum. The official loader completed strict pretrained state loading; no random fallback was used. See real_weight_verification.json and dependency_versions.json.

## Actual pilot results

There are 24 episodes: two categories × three support draws × four shot counts. Each category uses the same four normal and four anomalous test queries in every episode, selected by sorted path before scoring. Supports come only from normal training images, with nested prefixes of the same draw across k. Candidate-pool size and acquisition budget are zero. Labels/masks are used for offline metrics, not detector input or threshold selection.

The 192 prediction records reuse only 16 unique query images. Means below are descriptive across three support draws sharing queries; no confidence interval, independence assumption or significance claim is made.

| Dataset/category | k | Image AUROC | Image AP | Pixel AUROC | Pixel AP |
|---|---:|---:|---:|---:|---:|
| mvtec_ad/bottle | 1 | 1.0000 | 1.0000 | 0.9857 | 0.8547 |
| mvtec_ad/bottle | 2 | 1.0000 | 1.0000 | 0.9863 | 0.8594 |
| mvtec_ad/bottle | 4 | 1.0000 | 1.0000 | 0.9867 | 0.8630 |
| mvtec_ad/bottle | 8 | 1.0000 | 1.0000 | 0.9871 | 0.8647 |
| visa/capsules | 1 | 0.6875 | 0.7653 | 0.8028 | 0.0063 |
| visa/capsules | 2 | 0.7083 | 0.7754 | 0.8394 | 0.0085 |
| visa/capsules | 4 | 0.5833 | 0.6458 | 0.8543 | 0.0256 |
| visa/capsules | 8 | 0.5625 | 0.5976 | 0.8808 | 0.0246 |

What worked: actual pretrained extraction, deterministic caching, strict support budgets, restored maps, exact image/pixel AUROC/AP, original-map validation and resume. What failed: the first pilot startup used an unwritable default Torch cache; it was corrected to the workspace cache. A synthetic grid assertion required float32 tolerance; all 14 final synthetic tests passed. Both initial issues are preserved in the logs.

What the results show: the selected bottle subset scored strongly. Capsules pixel AP was low (about 0.006–0.026), and image AUROC decreased from 0.6875 at k=1 to 0.5625 at k=8. More randomly drawn normal references did not consistently improve detection ranking in this pilot. No benefit predictor or intervention claim follows from these data. The bottle anomaly subset is chosen by sorted path and does not cover every defect type. The 224-pixel input and tiny, reused query sets prevent full-benchmark conclusions.

Unverified: support adequacy, beneficial reference selection, defect-preservation interventions, calibrated events, F1/IoU thresholds, AU-PRO, category-disjoint validation, statistical confidence intervals and transfer. Novelty is undetermined. No private-test, state-of-the-art, acceptance, probability-calibration or theoretical-guarantee claim is made.

## Exact executed commands

```bash
bash /workspace/tools/install_runtime.sh
/workspace/venvs/safe_iad/bin/python /workspace/tools/verify_dinov2.py --image /workspace/datasets/visa/candle/Data/Images/Normal/0000.JPG --report /workspace/reports/real_weight_verification.json
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.run_baseline_pilot --config /workspace/tools/configs/baseline_pilot.json
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m unittest discover -s /workspace/tools/tests -p '*_synthetic.py' -v
/workspace/venvs/safe_iad/bin/python /workspace/tools/plot_pilot.py --results /workspace/reports/baseline_pilot/episodes.json --output /workspace/reports/baseline_pilot/pilot_summary.png
```

The pilot was rerun after adding actual image/mask fingerprints, producing identical metrics, then resumed successfully while checking all map artifacts. validation.json records the executed artifact/budget checks. Per-episode manifests, predictions.jsonl, metrics.json and original-resolution .npz maps are under baseline_pilot; episodes.json is the machine-readable aggregate.

No full-experiment command is claimed available or validated. Later protocols and faithful/adapted comparison methods are unimplemented; full localization metrics and storage/memory planning also remain. Do not launch an expensive full run from this pilot alone.

## Remaining external input and saved configuration

Provide the actual anomaly-localization repository URL to integrate the tested standalone tools and complete the required audit of existing interfaces. The selected /workspace/ennayriomar checkout remains unchanged. install_script, start_skill and required network additions are saved in the environment draft. Review/save settings, then publish through the environment UI; publication and restoration in a new task have not been verified.
