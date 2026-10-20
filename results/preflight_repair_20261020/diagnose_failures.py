"""Retain all prior tracebacks and diagnose their distinct causes."""
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from unittest.mock import patch

OUT=Path(__file__).resolve().parent
REPO=OUT.parents[1]
PRIOR=REPO/"results/calibrated_cutoff_20261020/continuation_20261020T120107Z"

DIAGNOSES={
"test_visa_uses_original_csv_roles_and_masks":(
    "implementation portability defect (metadata paths)",
    "verify_dataset.discover uses str(Path.relative_to(...)), producing Windows backslashes, while official VisA CSV paths use forward slashes. The traceback lists the same existing fixture images as both unlisted and missing under different separators.",
    "Use the declared Linux runtime for the unchanged implementation. If Windows support is later required, separately change native relative-path serialization to as_posix and retain all assertions; no scoring mathematics needs to change.",
    "framework/safe_iad/verify_dataset.py: discovery actual/listed and mask path sets"),
"test_study_configuration_resolves_every_historical_input":(
    "runtime/platform incompatibility (Linux path expectation)",
    "The test explicitly expects /tmp/custom-mvtec; Windows pathlib resolves that POSIX-style absolute input to C:\\tmp\\custom-mvtec. This is a platform-specific assertion, not a missing dataset or anomaly-score defect.",
    "Run this unchanged Linux-oriented gate in the documented Linux filesystem layout. Do not relax the expected assertion.",
    "tests/test_repository_interface.py:114-119; train_study.resolved_config"),
"test_synthetic_bad_checksum_never_publishes_data":(
    "documented CLI path/layout mismatch; nested stderr probe required",
    "Pending direct observation of the acquisition subprocess; its test helper hardcodes /workspace/tools/acquire_public_data.py.",
    "Establish the nested subprocess exception, then restore the documented /workspace/tools layout in the compatible runtime. Do not create a fake acquisition report.",
    "framework/tests/test_dataset_tools_synthetic.py: acquire helper and failing method"),
"test_configured_symlink_target_change_invalidates_input":(
    "runtime OS privilege/feature incompatibility",
    "os.symlink raised WinError 1314 before the actual invalidation check: this Windows process lacks permission for the requested symlink. This is not evidence that cache invalidation is defective.",
    "Run unchanged tests in a Linux runtime that provides normal symlink semantics; do not mock symlinks or skip the assertion.",
    "framework/tests/test_experiment_io_synthetic.py:112; full WinError 1314 traceback"),
"test_hybrid_pipeline":(
    "missing declared dependency",
    "Importing safe_iad.official_ad2 failed at import tifffile; the current interpreter has no tifffile module. The pipeline test module therefore did not finish discovery.",
    "Install tifffile==2025.10.16 from framework/requirements-pipeline.txt in the same interpreter used by both test gates, then rediscover the complete module.",
    "framework/safe_iad/official_ad2.py:10; framework/requirements-pipeline.txt"),
"test_json_reload_replays_exact_and_has_no_pickle":(
    "runtime filesystem layout incompatibility",
    "The unchanged test passes dir='/tmp' explicitly to TemporaryDirectory. On this Windows host that directory does not exist; TEMP/TMPDIR overrides do not replace an explicit dir argument.",
    "Provide the documented Linux /tmp directory; keep serialization/replay assertions intact.",
    "framework/tests/test_safal_calibration.py:107"),
"test_synthetic_checkpoint_without_pickle_reconstructs_identical_predictions":(
    "runtime filesystem layout incompatibility",
    "TemporaryDirectory(dir='/tmp') failed before any checkpoint replay assertion because the explicit Linux directory is absent on Windows.",
    "Provide the documented Linux /tmp directory and rerun unchanged replay/tamper tests.",
    "framework/tests/test_safal_model.py:88"),
"test_synthetic_save_load_replays_grid_scores_and_selected_inference":(
    "runtime filesystem layout incompatibility",
    "TemporaryDirectory(dir='/tmp') failed before the save/load assertions because the explicit Linux directory is absent on Windows.",
    "Use the documented Linux filesystem and keep the grid-score and selected-inference equality assertions unchanged.",
    "framework/tests/test_safal_tunable.py:115"),
"test_localization_is_recorded_not_invented_and_outputs_are_serializable":(
    "runtime text encoding incompatibility",
    "Path.write_text used the Windows cp1252 default when rendering a Markdown arrow U+2192. The traceback is UnicodeEncodeError, not an invalid metric or JSON serialization result.",
    "Use a UTF-8 Linux locale/UTF-8 Python mode in the isolated runtime. If portability is needed later, document explicit encoding='utf-8' as a separate presentation-only code change.",
    "framework/safe_iad/safal_tuning_report.py:449; cp1252 traceback"),
"test_checked_download_and_hardlink_extraction":(
    "Python runtime-version incompatibility",
    "Python 3.11.0's TarFile.extractall does not accept filter='data'; the error occurs after fixture archive checksums were successfully verified.",
    "Use the declared Python 3.12.14 runtime, retaining the safe data extraction filter and all archive integrity/hardlink assertions.",
    "framework/download_vision_hybrid_results.py:71; TypeError traceback"),
"test_vision_hybrid_protocol":(
    "runtime OS incompatibility (POSIX locking import)",
    "The test module cannot import because safe_iad.vision_hybrid_cli imports POSIX fcntl, which is unavailable in native Windows Python. Its protocol assertions were not executed.",
    "Run with POSIX fcntl in the documented Linux runtime. Do not fake fcntl, disable stage locks or skip the module.",
    "framework/safe_iad/vision_hybrid_cli.py:12"),
}


def main():
    issues=[]
    for label in ("root","framework"):
        text=(PRIOR/"logs"/(label+"_tests.stdout.log")).read_text(encoding="utf-8")
        for block in text.split("======================================================================")[1:]:
            if not block.lstrip().startswith(("ERROR:","FAIL:")):continue
            block=block.split("\n----------------------------------------------------------------------\nRan ",1)[0].strip()
            header=block.splitlines()[0]
            method=header.split(": ",1)[1].split(" ",1)[0]
            kind,cause,correction,evidence=DIAGNOSES[method]
            exception="\n".join(line for line in block.splitlines() if re.match(r"^(?:\w+(?:Error|Exception)|ImportError|AssertionError):",line))
            issues.append({"test":header,"method":method,"suite":label,"exact_exception_or_assertion":exception,
                "complete_traceback":block,"classification":kind,"root_cause":cause,"proposed_correction":correction,
                "source_evidence":evidence,"resolution_status":"proposed; not yet rerun"})
    assert len(issues)==11,len(issues)
    sys.path[:0]=[str(REPO/"framework"),str(REPO/"framework/tests")]
    import test_dataset_tools_synthetic as fixture
    actual_run=subprocess.run; captured=[]
    def observed_run(*args,**kwargs):
        result=actual_run(*args,**kwargs)
        captured.append({"argv":args[0] if args else kwargs.get("args"),"returncode":result.returncode,
                         "stdout":result.stdout,"stderr":result.stderr})
        return result
    stream=io.StringIO()
    suite=unittest.TestSuite([fixture.SyntheticDatasetToolTests("test_synthetic_bad_checksum_never_publishes_data")])
    with patch.object(fixture.subprocess,"run",observed_run):
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    probe={"test_result":stream.getvalue(),"captured_subprocesses":captured,"successful":result.wasSuccessful(),
           "assertions_modified":False,"synthetic_fixture_only":True}
    (OUT/"acquisition_failure_probe.json").write_text(json.dumps(probe,indent=2)+"\n",encoding="utf-8")
    acquisition=next(i for i in issues if i["method"]=="test_synthetic_bad_checksum_never_publishes_data")
    if captured and "can't open file" in (captured[0]["stderr"] or ""):
        acquisition["classification"]="documented CLI path/layout mismatch"
        acquisition["root_cause"]="Observed subprocess exit "+str(captured[0]["returncode"])+": "+captured[0]["stderr"].strip()+". The acquisition helper never ran, so it could not create acquisition.json."
    else:
        acquisition["root_cause"]="Nested subprocess evidence is saved in acquisition_failure_probe.json; inspect it before deciding a correction."
    document={"prior_audit_commit":"08d5c7fc28af368a85c77dec8014d92e43b1989e","failure_error_count":len(issues),
        "complete_prior_tracebacks_read":True,"issues":issues,"scoring_code_changed":False,
        "missing_assets_separate_from_test_failures":{
            "checkpoint":"Required register ViT-L checkpoint missing in prior search; these existing logic tests do not validate real weights.",
            "encoder_source":"Cached source lacks a trusted pinned manifest; separate from fcntl/tifffile import errors."}}
    (OUT/"failure_diagnosis.json").write_text(json.dumps(document,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(document,indent=2),flush=True)
    print(json.dumps(probe,indent=2),flush=True)


if __name__=="__main__":main()
