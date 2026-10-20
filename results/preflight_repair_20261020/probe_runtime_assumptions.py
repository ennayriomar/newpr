"""Observe runtime causes without changing or weakening existing assertions."""
import importlib.util
import inspect
import io
import json
import locale
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import unittest
from unittest.mock import patch

OUT=Path(__file__).resolve().parent
REPO=OUT.parents[1]
sys.path[:0]=[str(REPO),str(REPO/"framework"),str(REPO/"framework/tests")]


def main():
    report={"python":sys.version,"executable":sys.executable,"os_name":os.name,
        "fcntl_present":importlib.util.find_spec("fcntl") is not None,
        "tifffile_present":importlib.util.find_spec("tifffile") is not None,
        "tar_extractall_signature":str(inspect.signature(tarfile.TarFile.extractall)),
        "explicit_linux_tmp_exists":Path("/tmp").is_dir(),
        "documented_helper_exists":Path("/workspace/tools/acquire_public_data.py").is_file(),
        "locale_encoding":locale.getencoding(),"utf8_mode":sys.flags.utf8_mode,
        "test_assertions_modified":False}
    encoding_path=OUT/"tmp/encoding_probe.txt"
    with encoding_path.open("w") as f:
        report["actual_default_text_file_encoding"]=f.encoding
        f.write("arrow: \u2192\n")
    from safe_iad import safal_tuning_report
    import test_safal_tuning_report as tuning_tests
    stream=io.StringIO()
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(unittest.TestSuite([
        tuning_tests.SafalTuningReportTests("test_localization_is_recorded_not_invented_and_outputs_are_serializable")]))
    report["utf8_correction_probe"]={"successful":result.wasSuccessful(),"complete_output":stream.getvalue(),
        "correction":"PYTHONUTF8=1 applied by run_logged.py; presentation code and assertions unchanged",
        "scope":"Targeted diagnostic on the old Python runtime, not a full repaired-runtime gate"}
    import test_dataset_tools_synthetic as fixture
    observed=[]; actual=subprocess.run
    def capture(*args,**kwargs):
        completed=actual(*args,**kwargs)
        observed.append({"argv":args[0],"returncode":completed.returncode,"stdout":completed.stdout,"stderr":completed.stderr})
        return completed
    suite=unittest.TestSuite([fixture.SyntheticDatasetToolTests(name) for name in (
        "test_synthetic_unsafe_archive_never_escapes_staging","test_synthetic_existing_data_is_preserved")])
    stream=io.StringIO()
    with patch.object(fixture.subprocess,"run",capture):
        result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    report["neighboring_path_assumptions"]={"successful":result.wasSuccessful(),"complete_output":stream.getvalue(),
        "observed_subprocesses":observed,"interpretation":"If subprocess stderr says the helper cannot be opened, a passing assertion does not demonstrate that archive extraction/checksum handling ran. The documented CLI path must be restored before accepting the gate."}
    (OUT/"runtime_assumption_probes.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__=="__main__":main()
