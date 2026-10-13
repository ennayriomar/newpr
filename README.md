# SAFAL industrial anomaly research

## Full model v0.5.0

[Download the complete model/code ZIP](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safal_full_model_v0.5.0.zip) · [SHA256 checksum](safal_full_model_v0.5.0.zip.sha256) · [Full model guide](framework/docs/full_model.md) · [Measured research report](results/safal_full_model/research_report.md) · [Complete checkpoint/map outputs](results/safal_full_model_archive)

The runnable implementation includes a verified frozen DINOv2 encoder, raw PCA and cosine-search branches, fixed/max/adaptive fusion, support diagnostics, uncertainty, separate source-proxy error calibration, JSON/NPZ checkpoints and train/evaluate/predict commands. The ZIP includes two genuinely fitted k2 examples, all source/configurations/tests, pinned licensed vendor sources and compact measured reports. Pretrained encoder weights and datasets are separate checksum-verified downloads. Read BUNDLE_README.md after extraction.

All **159 unit/contract tests passed**. The actual pretrained pilot completed 16 episodes and 320 method records from **eight unique native images**, with k1/2/4/8, two draws and k+4 normal-information budgets. All20 serialized models were audited;16 query replays reproduced image scores and11 metric-map fields exactly. Two cache-bypassed real-feature probes and separate freshGit/plainvendor checks passed. Train/evaluate/nativepredict/verifiedresume commands passed. These are current-instance checks, not a full published benchmark or a fresh environment restoration.

SAFAL accuracy matched fixed averaging (0.9375) and fell below the PCA branch (0.96875). **Higher accuracy is not established.** Adequacy/uncertainty are bounded compatibility diagnostics. Error estimates are fitted on source normal/CutPaste proxy events; native reliability and calibration are unverified. Evaluation maps are resized256x256; the predict command exports native maps.

The separate result archive retains every fitted source/target bank, query replay probe and metric score-map array, with SHA256-verified8MiB parts and an automatic downloader. Earlier uploads remain preserved below. Real-IAD, full MVTec/VisA/AD2 benchmarks and private AD2 server scoring remain unrun.

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
