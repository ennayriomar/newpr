# Preflight repair report

**Status: INCOMPLETE — see remaining blockers.** This work repairs prerequisites only. No smoke inference,
source selection, cutoff calibration, VisA evaluation or completed-study verdict
is part of this repair.

Started from `calibrated-cutoff-20261020` at
`08d5c7fc28af368a85c77dec8014d92e43b1989e`; new branch
`preflight-repair-20261020`. All earlier reports/results remain read-only. The only
runtime definition is saved as inactive evidence in `proposed_workflow.yml`.
No live workflow was installed or executed. No model implementation or existing
test assertion was edited.

## Checkpoint

**Failed verification.** The unchanged repository downloader raised `ValueError('Downloaded weight length/SHA256 mismatch.')`. It uses one combined length/digest guard and does not expose the actual final values in this exception. The exact failed subcondition is therefore **undetermined** from the retained evidence. The required digest was not verified, and no substitute or bypass was attempted.

Download started `2026-10-20T12:42:35.576194+00:00` and ended `2026-10-20T13:06:23.509820+00:00`. The downloader deleted its rejected partial file. No verified checkpoint remains at the requested persistent path. The user's STOP rule was applied; no further runtime installation, CI execution or full test-gate rerun followed.

The original repository function `safe_iad.vision_hybrid_features.prepare` downloads
from the official `https://dl.fbaipublicfiles.com/` URL, enforces the expected
1,217,607,321-byte length and SHA-256, and refuses a mismatch. The wrapper would
perform a second SHA-256 pass after success, but that pass did **not** run in this
failed attempt. No model was instantiated by this repair downloader.
See [checkpoint_verification.json](checkpoint_verification.json)
and `logs/official_checkpoint_download.*.log`.

The verified Git source remains in ignored persistent `assets/` storage. There
is no accepted checkpoint file. Verification receipts, rejection tracebacks and
reproduction commands are committed. The failed check is not proof that the
official artifact changed or that its digest alone was wrong; the downloader's
combined error does not establish either claim.

## Encoder source

**Verified.** Official commit `7764ea0f912e53c92e82eb78a2a1631e92725fc8`; canonical manifest SHA-256 `9ed9679525be8520b45cd087ce2bff1cd684f438ac82bc0d6080e36487adf340`; 158 required Python/license files passed the unchanged verifier.

Persistent host path: `C:\Users\ennay\Documents\Codex\2026-10-20\files-pasted-by-the-user-role\outputs\newpr\results\preflight_repair_20261020\assets\dinov2-source`.

The required DINOv2 revision and manifest were read from the frozen controlled
protocol, not inferred from the cached folder or the separate reference-recipe
commit. The official revision was fetched directly, checked out detached with LF
bytes, verified by the unchanged `verify_source`, and only then used to export a
trusted manifest. See [encoder_source_verification.json](encoder_source_verification.json)
and the complete source-fetch/checkout logs.
Source restoration completed while the independent checkpoint download was still
running; it was not a repair action taken after the checkpoint STOP condition.

## Diagnosis and corrections

All eleven prior failure/error tracebacks were read completely and retained in
[failure_diagnosis.json](failure_diagnosis.json), including exact exception/assertion,
root cause, classification, source evidence and proposed correction. A readable
case-by-case version is [failure_details.md](failure_details.md). The review
was written before implementation changes in [code_defect_review.md](code_defect_review.md).

| `test_visa_uses_original_csv_roles_and_masks` | implementation portability defect (metadata paths) | Not yet resolved by a passing required gate |
| `test_study_configuration_resolves_every_historical_input` | runtime/platform incompatibility (Linux path expectation) | Not yet resolved by a passing required gate |
| `test_synthetic_bad_checksum_never_publishes_data` | documented CLI path/layout mismatch | Not yet resolved by a passing required gate |
| `test_configured_symlink_target_change_invalidates_input` | runtime OS privilege/feature incompatibility | Not yet resolved by a passing required gate |
| `test_hybrid_pipeline` | missing declared dependency | Not yet resolved by a passing required gate |
| `test_json_reload_replays_exact_and_has_no_pickle` | runtime filesystem layout incompatibility | Not yet resolved by a passing required gate |
| `test_synthetic_checkpoint_without_pickle_reconstructs_identical_predictions` | runtime filesystem layout incompatibility | Not yet resolved by a passing required gate |
| `test_synthetic_save_load_replays_grid_scores_and_selected_inference` | runtime filesystem layout incompatibility | Not yet resolved by a passing required gate |
| `test_localization_is_recorded_not_invented_and_outputs_are_serializable` | runtime text encoding incompatibility | Not yet resolved by a passing required gate |
| `test_checked_download_and_hardlink_extraction` | Python runtime-version incompatibility | Not yet resolved by a passing required gate |
| `test_vision_hybrid_protocol` | runtime OS incompatibility (POSIX locking import) | Not yet resolved by a passing required gate |

The missing acquisition report was diagnosed by observing its real subprocess:
Python exited 2 because `C:\workspace\tools\acquire_public_data.py` was absent.
It never reached archive validation. Two neighboring tests also passed while
their helper failed to launch; those earlier passes did not establish their
intended behavior. The repair restores the documented `/workspace/tools` layout
and reruns the original assertions. The probes are saved in
[acquisition_failure_probe.json](acquisition_failure_probe.json) and
[runtime_assumption_probes.json](runtime_assumption_probes.json).

The Unicode failure was reproduced as a runtime encoding issue; the targeted
unchanged test passed with `PYTHONUTF8=1`. That targeted probe on the old interpreter
is not counted as the required repaired-runtime gate.

The Windows VisA discrepancy is a metadata path-canonicalization portability
defect, with no evidence of a numerical scoring defect. The selected repair uses
the repository's declared Linux contract instead of editing the frozen metadata
implementation or weakening the Linux-specific tests. POSIX `fcntl`, symlinks,
`/tmp`, UTF-8, Python 3.12's extraction filter and the pinned `tifffile` dependency
address distinct observed causes.

## Runtime and required gates

The compatible Linux runtime definition was prepared but **not installed or executed** because checkpoint verification failed. No root/framework gate rerun on a repaired interpreter is claimed.

The host runtime left in place is: `3.11.0 (main, Oct 24 2022, 18:26:48) [MSC v.1933 64 bit (AMD64)]`; interpreter `C:\Users\ennay\Downloads\safe_iad_m1\safe_iad\venv\Scripts\python.exe`. Observed package versions:

- torch: `2.11.0+cu128`
- torchvision: `0.26.0+cu128`
- numpy: `2.4.6`
- Pillow: `12.3.0`
- scikit-learn: `1.9.0`
- scipy: `1.17.1`
- matplotlib: `3.11.1`
- threadpoolctl: `3.6.0`
- PyYAML: `6.0.3`
- tifffile: `None`

No repaired-runtime suite result is available.

No failing test is skipped or assertion weakened. Imported-module placeholders
are not accepted as successful discovery. The gate requires both complete suites
to exit zero, with no skipped or expected-failure cases. Complete discovery IDs,
stdout, stderr, exit codes, installed package reports and timings are under the
selected `ci_runs/` directory. The runtime definition uses pinned official
[checkout](https://github.com/actions/checkout),
[setup-python](https://github.com/actions/setup-python) and
[upload-artifact](https://github.com/actions/upload-artifact) revisions, resolved
and saved in the action-pin logs. Exact Python 3.12.14 availability was verified
against the official Actions Python build manifest before selecting it.

The proposed compatible gate runtime is Linux CI, not a conversion of this Windows
host. It was not executed. The host's old Windows environment was preserved. The
source is persistent, but the checkpoint prerequisite failed. The targeted
diagnostic tests used their existing synthetic fixtures; no real encoder was
instantiated for image inference. A future repair must first obtain and verify
the exact checkpoint before proceeding to runtime installation and both full
gates. This repair does not authorize or perform a cutoff study.

## Remaining blockers

- Original official checkpoint downloader rejected the download with ValueError('Downloaded weight length/SHA256 mismatch.'); required SHA-256 was not verified. Actual final byte count/digest were not exposed by the combined guard.
- Compatible Linux/Python 3.12.14 and declared dependencies were not installed after the checkpoint STOP; the existing Windows environment remains in place.
- The required root and framework gates have not both passed in the declared compatible runtime.

All repair results are summarized in [repair_summary.json](repair_summary.json).
Observed per-test resolutions are in [failure_resolutions.json](failure_resolutions.json).
Commands and full logs are saved in [commands.jsonl](commands.jsonl) and `logs/`;
CI has a separate command ledger in its run directory. No operating-point or
model-reproduction outcome is claimed.
