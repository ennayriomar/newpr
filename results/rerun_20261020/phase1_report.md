# Phase 1 — preflight stopped

Final verdict: **not reproduced**.

This verdict means the requested rerun could not be performed because required inputs were absent at the configured paths. It does not mean a numerical mismatch was measured.

## Scope and evidence

Source repository: ennayriomar/newpr. Source branch: controlled-full-image-20261018. Source commit: 05c0fcea1b3289f0daf2f658c56b08c2848b71e9. Destination branch: rerun-20261020. This report and its evidence are saved only under results/rerun_20261020/. The source results were not modified, regenerated or overwritten.

The source branch read, its full response, and the protocol read request/response are saved in logs/source_branch_read.json and logs/protocol_read.json. The protocol read covers original lines 1–103, not the complete file. Branch creation request/response is saved in logs/branch_creation.json.

The only Python operation was a preflight filesystem probe, with conditional checkpoint hashing that could not execute because the checkpoint was absent. Its exact command is commands/preflight.sh. Its full combined command output is logs/preflight.stdout.txt; process metadata and output are also saved in logs/preflight.execution.json. The process exit code was 0 because the probe caught and reported filesystem errors; this is not a successful model execution or a passing reproduction check.

## Missing required inputs

Every row below returned FileNotFoundError, errno 2. Evidence: logs/preflight.stdout.txt, lines 1–7, respectively.

| Required input | Exact path checked | Evidence line |
|---|---|---|
| DINOv2 checkpoint | /tmp/safal_controlled_assets/dinov2_vitl14_reg4_pretrain.pth | 1 |
| DINOv2 source directory | /workspace/.cache/dinov2-source | 2 |
| AD2 source/calibration dataset root | /workspace/datasets/mvtec_ad2_public/mvtec_ad_2 | 3 |
| MVTec AD bottle dataset root | /workspace/datasets/mvtec_ad | 4 |
| VisA dataset root | /workspace/datasets/visa | 5 |
| Local experiment entry point at working-directory root | /workspace/scratch/87bcf964428f/controlled_experiment.py | 6 |
| Local saved per-image reference at working-directory-relative path | /workspace/scratch/87bcf964428f/results/controlled_full_image_20261018/per_image.jsonl | 7 |

The first five paths come from protocol.json lines 9–10 and 36–38, preserved in logs/protocol_read.json. The final two checks establish only absence at the listed local paths: they do not establish that repository code or per_image.jsonl is absent from GitHub. No claim is made that these inputs are unavailable everywhere or that another machine has the same filesystem. No clone, data download, substitute checkpoint, setting change or model run was attempted after the missing-input finding. This follows the instruction to stop if weights, data or code are missing.

## Frozen configuration and checkpoint

The inspected protocol records checkpoint SHA-256 36e4deffbaef061a2576705b0c36f93621e2ae20bf6274694821b0b492551b51 (original line 8), config SHA-256 de82b811f771708dfb8fa2f14eefb71cc7842a5241fb4365a3678b7c89320990 (line 4), and frozen lambda 0.25 (line 3). Evidence: logs/protocol_read.json.

These are values read from the saved protocol, not freshly verified hashes. The checkpoint was not readable because it was absent; its hash is therefore **not verified**. The config hash was **not recomputed or verified**. The complete config hashing procedure/code was not inspected, and no configuration was passed into an experiment. The requirement that the config hash match remains unmet.

## Requested checks and actual work

| Request | Actual outcome | Evidence / reason |
|---|---|---|
| a. Verify checkpoint SHA-256 | Not performed | Missing checkpoint; preflight output line 1 |
| b. Extract features, fit PCA, score bottle/candle/capsules/cashew | Not performed | Missing configured checkpoint, encoder source and datasets; lines 1–5 |
| c. Run each twice with identical seed | Not performed | No first run |
| d. Maximum/mean absolute score and raw-map differences | Not computed | No new scores or maps; no differences represented as zero |
| e. Read per_image.jsonl locally and recompute role leakage by ID/resolved path | Not performed | Local reference absent at checked path; line 7; no full role enumeration |
| f. Recompute AD2 image/pixel cutoffs and realised per-category false-alarm rates | Not performed | AD2 root missing; line 3 |
| g. VisA normal/anomaly score ranges and fractions above cutoff | Not computed | VisA root missing; line 5; no inference or calibration |

No quantitative rerun result is available. Max/mean differences, identical-score checks, leakage counts, realised calibration rates and score ranges are **unavailable**, rather than zero. No claim that prior recall values have been explained or reproduced is made. No test images or labels were loaded or used to select settings. No tuning was performed. No recommendation to change any number is made.

## Final status table

Status cells use only the requested vocabulary. Only documents/logs qualify for a status in this attempt; no unit-test, smoke-test, weight verification, dataset verification or benchmark status was earned.

| Deliverable | Status | Evidence |
|---|---|---|
| Phase 1 preflight report | written | phase1_report.md |
| Phase 2 non-execution report | written | phase2_report.md |
| Exact preflight command and full output | written | commands/preflight.sh; logs/preflight.stdout.txt; logs/preflight.execution.json |
| Source/config read and branch-creation records | written | logs/source_branch_read.json; logs/protocol_read.json; logs/branch_creation.json |

Phase 2 was not started. Final verdict for Phase 1: **not reproduced**.
