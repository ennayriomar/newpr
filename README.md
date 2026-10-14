# SAFAL: measured parameter tuning and trained vision models

## Paper-informed tuning — 14 October 2026

[Download updated code and five example banks](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safal_tuned_20261014.zip) · [Measured report](results/safal_tuning_20261014/report.md) · [Parameter guide](framework/docs/parameter_tuning.md) · [All 15 primary model banks](trained_models/safal_tuned_20261014) · [Complete archive](results/safal_tuning_20261014_archive)

The new independent module evaluated 768 scoring configurations, selected one global hybrid using 100 development images and a zero detected-to-missed constraint against both k4 controls, then compared two isolated feature changes. One hundred separate, prelocked image IDs were checked after the configuration was frozen. Both cohorts use five previously studied categories, three support draws, four original normal references plus four extra normal calibration images. The encoder is real frozen DINOv2 ViT-B/14 on CPU; this is computer-vision parameter selection, not LLM or backbone fine-tuning.

The selected configuration retains 99% PCA variance, uses a 90th-percentile normal cutoff, top1% image aggregation and fixed 75% cosine-search /25% raw-PCA fusion at image threshold 1. The 224-pixel mixed-layer representation remained selected; the late-layer and 336-pixel variants lost previously detected development cases and were rejected. Adequacy/uncertainty remain diagnostics, and the old probability head is omitted.

Development accuracy is 81.33% versus 81.00% original SAFAL and 80.00% fixed averaging. Verification accuracy is 77.33% for the tuned hybrid, 76.33% for original SAFAL and 77.67% for fixed averaging. The paired 95% accuracy intervals include zero: improvement is not established. The tuned model recovers seven previously missed original-SAFAL anomaly cases with zero original-SAFAL detection losses, but adds four false alarms; versus fixed averaging it loses 3 detections and recovers 3. Class counts, localization and conditional intervals are in the measured report. These are 100 unique images repeated across support draws, not 300 independent images. This conditional image check within development-exposed categories does not establish a full benchmark, production reliability or SOTA. The compact ZIP containsfixed k4/seed17 example banks, while all 15 primary banks and full raw-score/map audit outputs are retained separately. Superseded development-only attempts are preserved with notices in the complete archive. Dataset images and pretrained backbone binaries are separate.

# SAFAL research: trained models and measured results

## Training and evaluation — 14 October 2026

[Download trained model ZIP](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safal_trained_20261014.zip) · [Checksum](safal_trained_20261014.zip.sha256) · [Measured report](results/safal_training_20261014/verification/analysis/report.md) · [Trained example banks](trained_models/safal_20261014) · [All fitted banks and maps](results/safal_training_20261014_archive)

The actual run fitted 60 target-reference/PCA configurations plus 10 source configurations and learned a logistic error-estimation head on 320 source normal/CutPaste rows from 160 original parents. Another 80 rows from 40 separate parents were held out from fitting. The real DINOv2 encoder stayed frozen; this was SAFAL computer-vision training, not LLM fine-tuning.

Development validation used 100 unique real MVTec AD/VisA images across five categories, k1/2/4/8 and three draws. These produce 1,200 correlated inspections and 6,000 five-method records. Native labels did not fit model parameters or cutoffs. Eighteen query IDs appeared in the audited earlier runs; no pristine final-test claim is made. Per-category/shot metrics, uncertainty intervals, calibration limits and actual trained-artifact audits are linked above. This is not a full dataset benchmark or production reliability guarantee.

Mean episode image accuracy: SAFAL 0.766667, fixed average 0.761667, subspace 0.740000. Read the full report for paired comparisons, localization and coverage. Five compact k4/seed17 models were selected by a predeclared support count/draw, not by validation performance. The complete result archive retains all 70 fitted banks, 60 probes and 1,200 metric-map arrays. Raw images, feature caches and pretrained backbone binaries are separate.

# SAFAL industrial anomaly research

## Full model v0.5.0

[Download the complete model/code ZIP](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safal_full_model_v0.5.0.zip) · [SHA256 checksum](safal_full_model_v0.5.0.zip.sha256) · [Full model guide](framework/docs/full_model.md) · [Measured research report](results/safal_full_model/research_report.md) · [Complete checkpoint/map outputs](results/safal_full_model_archive)

The runnable implementation includes a verified frozen DINOv2 encoder, raw PCA and cosine-search branches, fixed/max/adaptive fusion, support diagnostics, uncertainty, separate source-proxy error calibration, JSON/NPZ checkpoints and train/evaluate/predict commands. The ZIP includes two genuinely fitted k2 examples, all source/configurations/tests, pinned licensed vendor sources and compact measured reports. Pretrained encoder weights and datasets are separate checksum-verified downloads. Read BUNDLE_README.md after extraction.

All **159 unit/contract tests passed**. The actual pretrained pilot completed 16 episodes and 320 method records from **eight unique native images**, with k1/2/4/8, two draws and k+4 normal-information budgets. All 20 serialized models were audited; 16 query replays reproduced image scores and 11 metric-map fields exactly. Two cache-bypassed real-feature probes and separate fresh Git and plain vendor checks passed. Train/evaluate/nativepredict/verifiedresume commands passed. These are current-instance checks, not a full published benchmark or a fresh environment restoration.

SAFAL accuracy matched fixed averaging (0.9375) and fell below the PCA branch (0.96875). **Higher accuracy is not established.** Adequacy/uncertainty are bounded compatibility diagnostics. Error estimates are fitted on source normal/CutPaste proxy events; native reliability and calibration are unverified. Evaluation maps are resized 256x256; the predict command exports native maps.

The separate result archive retains every fitted source/target bank, query replay probe and metric score-map array, with SHA256-verified 8 MiB parts and an automatic downloader. Earlier uploads remain preserved below. Real-IAD, full MVTec/VisA/AD2 benchmarks and private AD2 server scoring remain unrun.

## Historical SAFAL Phase A foundation audit

[Read the Phase A report](framework/docs/phase_a_report.md) · [Literature review](framework/docs/literature_review.md) · [Research gap](framework/docs/research_gap.md) · [Staged implementation plan](framework/docs/implementation_plan.md) · [Download the audit documents](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safal_phase_a_docs.zip)

The historical Phase A audit documents official recipes, source versions, licenses, dataset availability, hardware and prior experimental limits. It preceded the executable full-model release above. Earlier code and complete result archives remain preserved; preliminary variants did not establish a robust accuracy gain or faithful published-method reproduction.

## Historical Safe IAD research framework v0.4.0

The research repository is `ennayriomar/newpr`. Executable Python source,
configuration plans, tests and the CPU-runtime installer are under
[`framework/`](framework/). The existing code bundle and complete result archive
remain available; this framework addition preserves those earlier artifacts.

[Download the full v0.4.0 source ZIP](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safe_iad_full_code_v0.4.0.zip). This bundle
includes the M1 fixed-shot baseline, M2 source-only counterfactual/acquisition
tools, M3 learned-benefit feasibility tools, the strict normal-calibration hybrid
pipeline, pinned official source snapshots, licenses and research documentation.

Use Linux and Python 3.12 with the documented `/workspace` layout. Restore
`framework/` as `/workspace/tools`, obtain the separate datasets and actual
pretrained checkpoint, then run `bash /workspace/tools/install_runtime.sh`.
Read the bundled installation guide before running an experiment. Copied reports
are inspection artifacts; a fresh run needs verified inputs and a new output
directory.

This is research software. The M3 feasibility gate failed: improved mean utility
was accompanied by four correlated newly missed defect inspections and reduced
defect-pixel recall; matched omission controls did not establish the proposed
false-alarm effect. Full experiments were stopped. All 97 unit/contract tests
passed; actual artifact audit and two real-query reproduction probes are
reported separately. No private AD 2 score, full benchmark
completion or reliable production-inspection claim is implied by this upload.

## Earlier Safe IAD code bundle

[Download the full code ZIP](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safe_iad_full_code.zip)

The ZIP contains the framework, configs, tests, setup scripts, documentation, measured reports, and pinned dependency sources with their licenses. Datasets and pretrained weights are separate downloads. The included pilot results do not establish production reliability.

Verify the download and extract it:

```bash
sha256sum -c safe_iad_full_code.zip.sha256
unzip safe_iad_full_code.zip
```

Download the [SHA256 checksum](safe_iad_full_code.zip.sha256) into the same directory before running the verification command. Start with `safe_iad_full_code/BUNDLE_README.md` after extraction.

## Full results

[Browse reports and plots](results/README.md) · [Download reports and figures ZIP](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safe_iad_reports.zip) · [Download the complete results archive](https://github.com/ennayriomar/newpr/tree/main/results_archive)

The complete archive contains 4,580 result files (4.91 GB before compression), including raw anomaly maps and public prediction TIFFs. Use the automatic downloader, or download all numbered parts and verify the checksum file. Follow [the extraction instructions](results/RESULTS_README.md).

The earlier strict hybrid run is a five-category pilot with 20 unique evaluation queries. The full 20-category and private AD 2 evaluations have not been run.
