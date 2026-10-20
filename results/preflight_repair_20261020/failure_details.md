# Prior test failure diagnoses and observed repair status

All eleven complete original tracebacks remain in failure_diagnosis.json. No missing gate result is imputed.

## ERROR: test_visa_uses_original_csv_roles_and_masks (test_repository_interface.RepositoryInterfaceTests.test_visa_uses_original_csv_roles_and_masks)

Classification: implementation portability defect (metadata paths)

Exact exception/assertion:

```text
ValueError: Dataset inventory has unresolved issues: [{'kind': 'unlisted_or_missing_images', 'unlisted': ['capsules\\Data\\Images\\Anomaly\\002.JPG', 'capsules\\Data\\Images\\Normal\\000.JPG', 'capsules\\Data\\Images\\Normal\\001.JPG'], 'missing': ['capsules/Data/Images/Anomaly/002.JPG', 'capsules/Data/Images/Normal/000.JPG', 'capsules/Data/Images/Normal/001.JPG']}, {'kind': 'mask_inventory_mismatch', 'orphan_masks': ['capsules\\Data\\Masks\\Anomaly\\002.png'], 'missing_masks': ['capsules/Data/Masks/Anomaly/002.png']}]
```

Root cause: verify_dataset.discover uses str(Path.relative_to(...)), producing Windows backslashes, while official VisA CSV paths use forward slashes. The traceback lists the same existing fixture images as both unlisted and missing under different separators.

Evidence: `framework/safe_iad/verify_dataset.py: discovery actual/listed and mask path sets`.

Proposed correction: Use the declared Linux runtime for the unchanged implementation. If Windows support is later required, separately change native relative-path serialization to as_posix and retain all assertions; no scoring mathematics needs to change.

Observed status: Compatible-runtime gates have not passed.

## FAIL: test_study_configuration_resolves_every_historical_input (test_repository_interface.RepositoryInterfaceTests.test_study_configuration_resolves_every_historical_input)

Classification: runtime/platform incompatibility (Linux path expectation)

Exact exception/assertion:

```text
AssertionError: 'C:\\tmp\\custom-mvtec' != '/tmp/custom-mvtec'
```

Root cause: The test explicitly expects /tmp/custom-mvtec; Windows pathlib resolves that POSIX-style absolute input to C:\tmp\custom-mvtec. This is a platform-specific assertion, not a missing dataset or anomaly-score defect.

Evidence: `tests/test_repository_interface.py:114-119; train_study.resolved_config`.

Proposed correction: Run this unchanged Linux-oriented gate in the documented Linux filesystem layout. Do not relax the expected assertion.

Observed status: Compatible-runtime gates have not passed.

## ERROR: test_synthetic_bad_checksum_never_publishes_data (test_dataset_tools_synthetic.SyntheticDatasetToolTests.test_synthetic_bad_checksum_never_publishes_data)

Classification: documented CLI path/layout mismatch

Exact exception/assertion:

```text
FileNotFoundError: [Errno 2] No such file or directory: 'C:\\Users\\ennay\\Documents\\Codex\\2026-10-20\\files-pasted-by-the-user-role\\outputs\\newpr\\results\\calibrated_cutoff_20261020\\continuation_20261020T120107Z\\tmp\\tmpjmi7id0k\\acquisition.json'
```

Root cause: Observed subprocess exit 2: C:\Users\ennay\AppData\Local\Programs\Python\Python311\python.exe: can't open file 'C:\\workspace\\tools\\acquire_public_data.py': [Errno 2] No such file or directory. The acquisition helper never ran, so it could not create acquisition.json.

Evidence: `framework/tests/test_dataset_tools_synthetic.py: acquire helper and failing method`.

Proposed correction: Establish the nested subprocess exception, then restore the documented /workspace/tools layout in the compatible runtime. Do not create a fake acquisition report.

Observed status: Compatible-runtime gates have not passed.

## ERROR: test_configured_symlink_target_change_invalidates_input (test_experiment_io_synthetic.SyntheticExperimentIOTests.test_configured_symlink_target_change_invalidates_input)

Classification: runtime OS privilege/feature incompatibility

Exact exception/assertion:

```text
OSError: [WinError 1314] A required privilege is not held by the client: 'C:\\Users\\ennay\\Documents\\Codex\\2026-10-20\\files-pasted-by-the-user-role\\outputs\\newpr\\results\\calibrated_cutoff_20261020\\continuation_20261020T120107Z\\tmp\\tmp1pgsf2lp\\original' -> 'C:\\Users\\ennay\\Documents\\Codex\\2026-10-20\\files-pasted-by-the-user-role\\outputs\\newpr\\results\\calibrated_cutoff_20261020\\continuation_20261020T120107Z\\tmp\\tmp1pgsf2lp\\configured'
```

Root cause: os.symlink raised WinError 1314 before the actual invalidation check: this Windows process lacks permission for the requested symlink. This is not evidence that cache invalidation is defective.

Evidence: `framework/tests/test_experiment_io_synthetic.py:112; full WinError 1314 traceback`.

Proposed correction: Run unchanged tests in a Linux runtime that provides normal symlink semantics; do not mock symlinks or skip the assertion.

Observed status: Compatible-runtime gates have not passed.

## ERROR: test_hybrid_pipeline (unittest.loader._FailedTest.test_hybrid_pipeline)

Classification: missing declared dependency

Exact exception/assertion:

```text
ImportError: Failed to import test module: test_hybrid_pipeline
ModuleNotFoundError: No module named 'tifffile'
```

Root cause: Importing safe_iad.official_ad2 failed at import tifffile; the current interpreter has no tifffile module. The pipeline test module therefore did not finish discovery.

Evidence: `framework/safe_iad/official_ad2.py:10; framework/requirements-pipeline.txt`.

Proposed correction: Install tifffile==2025.10.16 from framework/requirements-pipeline.txt in the same interpreter used by both test gates, then rediscover the complete module.

Observed status: Compatible-runtime gates have not passed.

## ERROR: test_json_reload_replays_exact_and_has_no_pickle (test_safal_calibration.SafalCalibrationTests.test_json_reload_replays_exact_and_has_no_pickle)

Classification: runtime filesystem layout incompatibility

Exact exception/assertion:

```text
FileNotFoundError: [WinError 3] The system cannot find the path specified: '/tmp\\tmpes566kus'
```

Root cause: The unchanged test passes dir='/tmp' explicitly to TemporaryDirectory. On this Windows host that directory does not exist; TEMP/TMPDIR overrides do not replace an explicit dir argument.

Evidence: `framework/tests/test_safal_calibration.py:107`.

Proposed correction: Provide the documented Linux /tmp directory; keep serialization/replay assertions intact.

Observed status: Compatible-runtime gates have not passed.

## ERROR: test_synthetic_checkpoint_without_pickle_reconstructs_identical_predictions (test_safal_model.SyntheticSAFALTests.test_synthetic_checkpoint_without_pickle_reconstructs_identical_predictions)

Classification: runtime filesystem layout incompatibility

Exact exception/assertion:

```text
FileNotFoundError: [WinError 3] The system cannot find the path specified: '/tmp\\tmp9qnghh42'
```

Root cause: TemporaryDirectory(dir='/tmp') failed before any checkpoint replay assertion because the explicit Linux directory is absent on Windows.

Evidence: `framework/tests/test_safal_model.py:88`.

Proposed correction: Provide the documented Linux /tmp directory and rerun unchanged replay/tamper tests.

Observed status: Compatible-runtime gates have not passed.

## ERROR: test_synthetic_save_load_replays_grid_scores_and_selected_inference (test_safal_tunable.SyntheticTunableSAFALTests.test_synthetic_save_load_replays_grid_scores_and_selected_inference)

Classification: runtime filesystem layout incompatibility

Exact exception/assertion:

```text
FileNotFoundError: [WinError 3] The system cannot find the path specified: '/tmp\\tmpoae5k3x9'
```

Root cause: TemporaryDirectory(dir='/tmp') failed before the save/load assertions because the explicit Linux directory is absent on Windows.

Evidence: `framework/tests/test_safal_tunable.py:115`.

Proposed correction: Use the documented Linux filesystem and keep the grid-score and selected-inference equality assertions unchanged.

Observed status: Compatible-runtime gates have not passed.

## ERROR: test_localization_is_recorded_not_invented_and_outputs_are_serializable (test_safal_tuning_report.SafalTuningReportTests.test_localization_is_recorded_not_invented_and_outputs_are_serializable)

Classification: runtime text encoding incompatibility

Exact exception/assertion:

```text
UnicodeEncodeError: 'charmap' codec can't encode character '\u2192' in position 1666: character maps to <undefined>
```

Root cause: Path.write_text used the Windows cp1252 default when rendering a Markdown arrow U+2192. The traceback is UnicodeEncodeError, not an invalid metric or JSON serialization result.

Evidence: `framework/safe_iad/safal_tuning_report.py:449; cp1252 traceback`.

Proposed correction: Use a UTF-8 Linux locale/UTF-8 Python mode in the isolated runtime. If portability is needed later, document explicit encoding='utf-8' as a separate presentation-only code change.

Observed status: Compatible-runtime gates have not passed.

A targeted unchanged test passed under PYTHONUTF8=1. The complete repaired-runtime gate remains unrun, so this does not close the gate.

## ERROR: test_checked_download_and_hardlink_extraction (test_vision_hybrid_download.DownloadTests.test_checked_download_and_hardlink_extraction)

Classification: Python runtime-version incompatibility

Exact exception/assertion:

```text
TypeError: TarFile.extractall() got an unexpected keyword argument 'filter'
```

Root cause: Python 3.11.0's TarFile.extractall does not accept filter='data'; the error occurs after fixture archive checksums were successfully verified.

Evidence: `framework/download_vision_hybrid_results.py:71; TypeError traceback`.

Proposed correction: Use the declared Python 3.12.14 runtime, retaining the safe data extraction filter and all archive integrity/hardlink assertions.

Observed status: Compatible-runtime gates have not passed.

## ERROR: test_vision_hybrid_protocol (unittest.loader._FailedTest.test_vision_hybrid_protocol)

Classification: runtime OS incompatibility (POSIX locking import)

Exact exception/assertion:

```text
ImportError: Failed to import test module: test_vision_hybrid_protocol
ModuleNotFoundError: No module named 'fcntl'
```

Root cause: The test module cannot import because safe_iad.vision_hybrid_cli imports POSIX fcntl, which is unavailable in native Windows Python. Its protocol assertions were not executed.

Evidence: `framework/safe_iad/vision_hybrid_cli.py:12`.

Proposed correction: Run with POSIX fcntl in the documented Linux runtime. Do not fake fcntl, disable stage locks or skip the module.

Observed status: Compatible-runtime gates have not passed.

