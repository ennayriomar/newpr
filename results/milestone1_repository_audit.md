# Milestone 1 repository audit

Research objective: Support-Adequacy-Aware Few-Shot Anomaly Localization for Reliable Industrial Inspection.

## Scope and evidence

The supplied checkout is `/workspace/ennayriomar`, on the task branch `work`, at commit `5696650dba716a7e12bc09b152dc59d8ef6f38a3` (the previously verified `main` tip). Its entire tracked tree contains one file: `README.md`, a GitHub profile. This is not the anomaly-localization repository described in the request. Findings below apply to this checkout; they do not establish the implementation status of the intended, unavailable repository.

Executed inspection: recursive workspace file discovery excluding credential/configuration directories and Git internals; Git checkout discovery; `git ls-tree -r --name-only HEAD`; `git status --short --untracked-files=all`; repository README inspection; Python module availability checks; resource-location and GPU-tool discovery. No application tests were run because the supplied checkout has no code or tests. The working tree was clean. No repository files were changed.

## Component audit

| Component | File | Status in supplied checkout | Integrated? | Synthetic-tested? | Real-data-tested? | Required action |
|---|---|---|---|---|---|---|
| Repository documentation | `README.md` | GitHub profile, not setup or method documentation | N/A | N/A | N/A | Provide intended research repository |
| Configurations and entry points | None found | Unavailable | No | Not run | Not run | Inspect actual code before selecting commands |
| Test suite | None found | Unavailable | No | Not run | Not run | Run actual repository tests after access is supplied |
| MVTec AD loader and verification | None found | Unavailable | No | Not run | Not run | Supply code and inspect real dataset files |
| VisA loader and verification | None found | Unavailable | No | Not run | Not run | Supply code and inspect real dataset files |
| MVTec AD 2 loader and verification | None found | Unavailable | No | Not run | Not run | Inspect public/private split and public masks using actual data |
| DINOv2 ViT-B/14 extraction and preprocessing | None found | Unavailable; pretrained weights unverified | No | Not run | Not run | Verify actual pretrained loading, frozen/eval state, patch grid and map restoration |
| Feature caching | None found | Unavailable | No | Not run | Not run | Audit cache provenance and invalidation in actual repository |
| Patch nearest-neighbor baseline | None found | Unavailable | No | Not run | Not run | Implement or verify internal baseline after repository audit |
| Split manifest and leakage controls | None found | Unavailable | No | Not run | Not run | Verify separate support, candidate, validation, calibration and test roles |
| Scoring, calibration and metrics | None found | Unavailable | No | Not run | Not run | Audit actual implementation; select thresholds without final-test labels |
| AnomalyDINO and SubspaceAD adaptations | None found | Unavailable | No | Not run | Not run | Compare actual implementation with verified sources and document deviations |

There is no supplied code to classify as working, disconnected, placeholder, or synthetic-only. No claim is made about those classes in the intended repository.

## Runtime prerequisites

- Execution is available: Python 3.12.14 and Git 2.52.0.
- NumPy 2.3.5, Pillow 12.3.0 and scikit-learn 1.8.0 are installed.
- PyTorch, torchvision, timm, pytest and OpenCV were not found during module discovery.
- `nvidia-smi` is unavailable. GPU execution is unverified; this does not independently prove hardware is absent.
- About 29.83 GiB of disk space was available during inspection.
- The container has a 32 GiB memory limit and a four-CPU quota; five CPUs appear in its affinity set. Full experiments should not be scheduled before pilot feasibility and resource requirements are established.
- No datasets or model checkpoints were found among the workspace files. `/data` and `/datasets` do not exist, and `/mnt` is empty. No resource variables matching DATASET, MVTEC, VISA, DINO or CHECKPOINT were found. These observations do not rule out resources reachable through paths or remote services that have not been supplied.

Dependencies were not installed speculatively because the intended repository's manifests and version pins are unavailable. No random-weight fallback, synthetic pilot, new architecture, or fabricated result was introduced.

## Milestone status

| Milestone 1 requirement | Outcome |
|---|---|
| Audit supplied checkout | Completed; repository mismatch identified |
| Audit intended anomaly-localization code | Blocked: repository location/access missing |
| Run existing research tests | Unrun: no tests in supplied checkout |
| Verify three datasets and loaders | Unrun: code and real data unavailable |
| Verify actual pretrained DINOv2 weights | Unrun: extractor and checkpoint unavailable |
| MVTec AD real-data baseline pilot | Unrun |
| VisA real-data baseline pilot | Unrun |

Milestone 1 is incomplete. No detection, localization, acquisition, calibration, or performance claims are supported by this audit.

## Required inputs and resumption

Provide the anomaly-localization repository's GitHub URL or existing local path, plus paths or authorized download sources for MVTec AD, VisA and MVTec AD 2. Secret values must not be shared in chat. Existing platform Git authentication should be tried before requesting additional credentials.

Once those resources are accessible: inspect the actual repository and run its tests; verify the three real dataset layouts; install pinned dependencies; load and verify pretrained DINOv2 ViT-B/14; validate the patch baseline and caching; run small paired real-data MVTec AD and VisA pilots before advancing to later milestones. Exact runnable pilot/full-experiment commands depend on the actual code and are not claimed here.
