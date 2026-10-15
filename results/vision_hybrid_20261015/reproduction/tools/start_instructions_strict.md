# Safe IAD v0.4.0 current status and retained startup history

Current repository: https://github.com/ennayriomar/newpr, with source under
`framework/`. Use Linux/Python 3.12 and restore the package as `/workspace/tools`.
The existing CPU installer clones exact official Git source revisions; the
bundled snapshots lack Git metadata. Datasets, real checkpoint and official AD2
utilities must occupy the documented workspace paths. Follow
`start_instructions.md` and the source ZIP's `BUNDLE_README.md` for current install/fresh-run
instructions. Fresh installation and arbitrary-path portability are unverified.

M3 learned-benefit fitting and paired validation are completed. The predeclared
gate is negative: mean utility improved, but four correlated detected-to-missed
inspection records and reduced defect-pixel recall failed preservation; matched
support-omission controls did not establish the proposed false-alarm effect.
No full learned-acquisition run followed the gate and no model/cutoff was retuned.

The fresh 97-test run passed. The real-output audit verified 39 stage ledgers,
1,903 unique outputs and 547 unique inputs, and read 672 native/diagnostic pairs
covering 576 records from 20 unique query images. This was an artifact/contract
audit, not a float32-metric or backbone rerun. Separate cache-bypassed probes on
one actual query per main dataset reproduced the saved features, selection,
scores and maps; they are not a complete independent evaluation rerun.
See `/tmp/safe_iad_milestone3/research_report.md`, `evaluation/gate.json`,
`validation.json` and `real_weight_reproduction.json` for actual scope.

## Legacy onboarding notes, superseded by the current startup above

These notes preserve the earlier prerequisites and research cautions. Historical
test totals, milestones and repository assumptions below refer to their time of
execution; they are not the current M3 status or instructions to advance.

Use the existing checkouts under /workspace. Each task is isolated; do not create a Git worktree unless the user explicitly requests one.

At onboarding, /workspace/ennayriomar was a profile README and the research repository was unknown. The user subsequently selected ennayriomar/newpr; preserve the profile checkout and prior archives.

Standalone dataset acquisition and verification helpers are in /workspace/tools. Use /workspace/venvs/safe_iad/bin/python and set PYTHONPATH=/workspace/tools for safe_iad commands. PyTorch 2.7.1+cpu is installed; no GPU has been verified. Use at most four verification workers. These commands require no background services.

Check /workspace/reports/dataset_downloads/download_manifest.json and extraction reports for actual retained roots and integrity status. Never use roots ending in .unverified. The acquisition helper keeps outputs staged until their archive SHA-256 is verified. Dataset processes do not survive publication; confirm completion from reports and restart only an incomplete job with explicit preservation of any unverified outputs.

Validate actual datasets using: PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.verify_dataset --dataset mvtec_ad|visa|mvtec_ad2 --root <verified-root> --output /workspace/reports/dataset_verification --workers 4. Select one dataset name rather than a literal pipe expression. Check the exit status, verification.json, images.jsonl and sample visual artifacts. Native-split checks do not establish experimental validation/calibration isolation; an experiment manifest is still required.

MVTec AD 2 local data intentionally excludes test_private and test_private_mixed to fit storage. Only public masks can be evaluated locally. Official loader and prediction-submission utilities are under /workspace/datasets/official_ad2_tools; no private-test result has been produced.

The DINOv2 checkpoint must load from the official verified HTTPS source with strict state-dict loading; never fall back to random weights. Check the current real_weight_verification.json report. No model pilot should be claimed completed unless its actual results are saved. The initial milestone order below is historical; the current M3 stopping gate takes precedence.


## Historical verified standalone workflow: M1
- MVTec AD: /workspace/datasets/mvtec_ad (15 categories, 5,354 images).
- VisA: /workspace/datasets/visa (12 categories, 10,821 images; use the original split_csv/1cls.csv).
- MVTec AD 2: /workspace/datasets/mvtec_ad2_public/mvtec_ad_2 (8 categories, 3,914 retained train/validation/public-test images; private splits excluded). All archive hashes and retained-file checks passed in this instance.
- Official DINOv2 source dependency: /workspace/.cache/dinov2-source, pinned to 7764ea0f912e53c92e82eb78a2a1631e92725fc8. Official ViT-B/14 checkpoint: /workspace/.cache/torch/hub/checkpoints/dinov2_vitb14_pretrain.pth. Its recorded SHA-256 is 0b8b82f85de91b424aded121c7e1dcc2b7bc6d0adeea651bf73a13307fad8c73; this is a locally recorded checksum, not a claimed publisher checksum.
- Real loading probe: /workspace/venvs/safe_iad/bin/python /workspace/tools/verify_dinov2.py --image /workspace/datasets/visa/candle/Data/Images/Normal/0000.JPG --report /workspace/reports/real_weight_verification.json. Frozen/eval state, 16x16 patch grid and repeated CPU extraction passed in this instance.
- Pilot: PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.run_baseline_pilot --config /workspace/tools/configs/baseline_pilot.json. It completed 24 strict fixed-shot episodes on bottle/capsules, with 8 fixed queries/category, k=1,2,4,8 and seeds 0,1,2. Maps use original image resolution. Image/mask fingerprints gate resume; changed inputs require a new output directory. It is an internal NN baseline, not a faithful AnomalyDINO, SubspaceAD or PatchCore reproduction.
- Synthetic helper tests: PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m unittest discover -s /workspace/tools/tests -p '*_synthetic.py' -v (14 passed). They do not substitute for pretrained real-data checks.
- Plot: /workspace/venvs/safe_iad/bin/python /workspace/tools/plot_pilot.py --results /workspace/reports/baseline_pilot/episodes.json --output /workspace/reports/baseline_pilot/pilot_summary.png. The plot uses workspace caches; support-draw ranges are descriptive, not confidence intervals.

The historical /workspace/reports/milestone1_status.md recorded weak capsules localization and inconsistent image-ranking improvement from added references. At that stage, adequacy/benefit prediction, acquisition and calibrated decisions were absent. Those historical omissions do not describe the current M3 implementation; full benchmarks and private-server evaluation remain unrun. Do not use locked final-test results for tuning or claim fresh-task verification from old reports. Repository selection is now resolved as ennayriomar/newpr.


## Historical completed Milestone 2: source-only counterfactual targets and one-step acquisition
Read /workspace/reports/milestone2/report.md and /workspace/reports/milestone2/validation.json for the retained earlier pilot. Tools ran under /workspace/tools before integration into the now-known ennayriomar/newpr repository.

Tested commands:
```bash
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.build_training_targets --config /workspace/tools/configs/milestone2.json
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m safe_iad.run_acquisition_pilot --config /workspace/tools/configs/milestone2.json
PYTHONPATH=/workspace/tools /workspace/venvs/safe_iad/bin/python -m unittest discover -s /workspace/tools/tests -p 'test_acquisition_synthetic.py' -v
/workspace/venvs/safe_iad/bin/python /workspace/tools/plot_acquisition_pilot.py --results /workspace/reports/milestone2/evaluation/episodes.json --output /workspace/reports/milestone2/acquisition_summary.png
```
Runs completed with actual frozen pretrained DINOv2 features. Source targets: 384 candidate interventions from 12 source-training normal parents and their 12 synthetic versions; 380 positive and 4 negative under the declared loss. The source queries and their parents are globally excluded from supports/candidate pools. Category roles and image-level split manifests are recorded. Source native test images are excluded from target supervision. No final evaluation labels enter selectors or training.

Acquisition pilot: 16 unique locked bottle/capsules test queries, 3 support draws, one initial reference and shared 16-normal-image pool. This yields 240 query-policy inspection records across none/random/nearest-global/diversity/offline oracle. The budget is one added reference per independent query, reset for each inspection. The oracle uses evaluation masks and optimizes the declared loss, not AUROC/AP. The 768 evaluation candidate rows are explicitly final_evaluation_only/never_use_for_training. Actual before maps match Milestone 1; leave-one-reference-out is missing at k=1 and valid at k=2. Thirteen new synthetic policy and leakage tests passed, alongside actual output checks.

Mean capsule image AUROC drops from 0.6875 to 0.625 for nearest-global, although pixel AP rises from 0.00634 to 0.01970; 3/24 query/support interventions worsen the declared loss. Diversity worsens it in 4/24. True-defect score drops are recorded but are not measured missed-defect rates. No calibrated probabilities, learned benefit predictor or three-way decisions have been fitted. Check utility and defect-preservation criteria on declared validation categories and broaden source-only harmful-intervention supervision before Milestone 3. Never tune from locked final evaluation slices or their oracle rows.

This pilot covers k=1 and one-step b=0/1 only. Sequential b=2/4, full benchmarks and AD2 stress experiments remain unrun. Interrupted-job resume for M2 has not been validated; changing config requires a new output directory. Preserve all downloaded datasets, generated source supervision, real checkpoint, feature provenance and reports.


## Historical strict hybrid pipeline: tested v0.3 default, retained separately
Read /workspace/tools/README.md, /workspace/reports/hybrid_framework_report.md, /workspace/reports/hybrid_strict_validation.json and /workspace/reports/hybrid_strict_reproduction_precision.json. This separate strict hybrid remains available under /workspace/tools and is distinct from the M3 learned-benefit pilot; the selected profile repository is preserved.

The complete tested installer is /workspace/tools/install_runtime.sh. It prepares the CPU venv, exact pipeline dependencies, editable package, and pinned official DINOv2/AnomalyDINO/SubspaceAD dependency caches. Actual current datasets and pretrained checkpoint were verified; fresh-task restoration has not been independently tested.

Executed commands:
```bash
bash /workspace/tools/install_runtime.sh
cd /workspace/tools
/workspace/venvs/safe_iad/bin/python -m safe_iad.run_pipeline --config configs/experiment_plan.yaml --reproduce true
/workspace/venvs/safe_iad/bin/python -m unittest discover -s /workspace/tools/tests -v
/workspace/venvs/safe_iad/bin/python /workspace/tools/validate_pipeline_run.py --run /workspace/reports/hybrid_pipeline_strict --output /workspace/reports/hybrid_strict_validation.json
/workspace/venvs/safe_iad/bin/python /workspace/tools/verify_pipeline_reproduction.py --run /workspace/reports/hybrid_pipeline_strict --output /workspace/reports/hybrid_strict_reproduction_precision.json
/workspace/venvs/safe_iad/bin/python /workspace/tools/plot_pipeline.py --run /workspace/reports/hybrid_pipeline_strict --output /workspace/reports/hybrid_strict_summary.png
```

The default is a completed real-data feasibility pilot, not a full benchmark: five categories, 20 unique evaluation queries, k=1/2/4 and three nested support draws, 180 evaluation episodes, 720 predictions plus 144 calibration predictions. It physically reverified all 20,089 retained images, preserves exactly k normal training references with zero candidate pools/acquisitions, and exports 36 actual AD2 public TIFF/binary-PNG pairs checked by official per-file utilities. All 44 contract tests passed. Real-output audits checked 1,607 immutable artifacts and every support budget, native map, locked cutoff, bounded adequacy field and local evidence envelope.

Calibration must use only held-out normal training queries of the reserved calibration categories (excluded from calibration supports), plus the previously reserved AD2 normal validation calibration images. Four extra calibration normals per dataset are declared. All cutoffs use mean+3std. No native-test defect labels may fit thresholds, feature weights or hyperparameters. Test F1-Max is an offline diagnostic; its optimizing cutoff never drives decisions. Adequacy threshold 0.5 is predeclared. The archived /workspace/reports/hybrid_pipeline run used native-test calibration-category labels and is exploratory only; its implementation is preserved under /workspace/reports/hybrid_pipeline_implementation_snapshot. The active default writes /workspace/reports/hybrid_pipeline_strict. All 180 episode ranking metrics remained identical across this calibration protocol correction.

The hybrid uses frozen actual DINOv2 ViT-B/14 intermediate blocks 2/5/8/11, normalized concatenation, aspect-preserving long-edge 224 resize/stride padding, dense patch NN and support-only PCA. Entropy/density adequacy is a bounded empirical diagnostic. The defect envelope max(local,global orthogonal,nearest orthogonal) preserves local evidence; low mean adequacy produces unresolved while retaining raw evidence. Saved native maps are explicitly float16; pilot native-pixel metrics are computed in float32 before compression. Official baseline scoring cores run with fully declared common-backbone variants; published AnomalyDINO and SubspaceAD headline recipes have not been reproduced.

The scientific result is negative for reliable classification: hybrid accepted 165/180 repeated inspections, only 88/165 correct; all 36 AD2 can inspections were accepted but only 16 correct. At k=4 all 12 bottle inspections were unresolved despite image AUROC 1.0. These counts reuse 20 images and do not establish population rates. Entropy-based adequacy is not proven reference sufficiency, correctness confidence or a probability. Do not claim production readiness, reliable three-way classification, novelty, SOTA or theoretical guarantees.

A completed repeated invocation re-verifies data, validates the artifact ledger and independently recomputes one real query per method with cache bypass. That check passed; additional probes verified bitwise equal float32 features, exactly equal raw image scores/adequacy means and stored maps. This is not a full independent rerun of all episodes. Use a new --output directory for a full rerun; changing config/code/data requires new output. Interrupted recovery is not fully validated.

The full reserved-role plan is configs/experiment_full.yaml (2,871 queries, 20 categories), with bounded-memory native float16 histogram metrics explicitly exact for quantized scores. It is unrun: diagnostic maps alone project to about 1,067 GB before compression, beyond this 32 GB volume. Respect disk/memory preflight guards, preserve datasets and existing results, and obtain suitable storage before full runs. AD2 private data/scenarios and server scores are absent. Public previews must fail complete private-submission validation; never rename them to fabricate private predictions or scores. The exporter utility safe_iad.official_ad2 follows actual official paths/dtypes and validates a complete real private submission when available. No server upload was performed.

Continue changes and method-selection studies only with declared source/validation/calibration roles, never by tuning these locked evaluation results. The retained M2 acquisition utilities do not fit a model; the separate M3 learner now exists and its negative feasibility gate stops full-experiment expansion.

