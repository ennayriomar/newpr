# newpr

## SAFAL: Phase A foundation audit

[Read the Phase A report](framework/docs/phase_a_report.md) · [Literature review](framework/docs/literature_review.md) · [Research gap](framework/docs/research_gap.md) · [Staged implementation plan](framework/docs/implementation_plan.md) · [Download the audit documents](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safal_phase_a_docs.zip)

The latest research brief limits this step to Phase A. Official method recipes, source versions, licenses, dataset availability, hardware and prior experimental limits are documented. The existing v0.4.0 source and complete results archives remain preserved. The preliminary variants do not establish a robust accuracy gain or a faithful published SubspaceAD/VisionAD reproduction; no later SAFAL phase is claimed complete.

## Safe IAD research framework v0.4.0

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
