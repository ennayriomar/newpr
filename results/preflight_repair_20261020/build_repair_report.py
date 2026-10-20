"""Render an evidence-only repair report; unrun gates never become successes."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

OUT=Path(__file__).resolve().parent
REPO=OUT.parents[1]


def read(name,default=None):
    p=OUT/name
    return json.loads(p.read_text(encoding="utf-8-sig")) if p.is_file() else default


def main():
    diagnosis=read("failure_diagnosis.json")
    checkpoint=read("checkpoint_verification.json",{"verified":False})
    source=read("encoder_source_verification.json",{"verified":False})
    probes=read("runtime_assumption_probes.json",{})
    summaries=sorted((OUT/"ci_runs").glob("*/gate_summary.json")) if (OUT/"ci_runs").is_dir() else []
    latest=summaries[-1] if summaries else None
    gate=json.loads(latest.read_text()) if latest else None
    passed=bool(gate and gate.get("gate_passed"))
    required_assets=checkpoint.get("verified",False) and source.get("verified",False)
    resolutions=[]
    for issue in diagnosis["issues"]:
        r={k:v for k,v in issue.items() if k!="complete_traceback"}
        r["resolved_in_required_gate"]=False;r["observed_resolution"]="Compatible-runtime gates have not passed."
        if issue["method"]=="test_localization_is_recorded_not_invented_and_outputs_are_serializable":
            r["targeted_utf8_probe_passed"]=bool(probes.get("utf8_correction_probe",{}).get("successful"))
        if gate and gate.get("gates"):
            key="root_tests" if issue["suite"]=="root" else "framework_tests"
            result=gate["gates"].get(key,{}).get("report")
            if result:
                method=issue["method"]
                matches=[n for n in result["test_ids"] if (n.startswith(method+".") if method in ("test_hybrid_pipeline","test_vision_hybrid_protocol") else n.endswith("."+method))]
                bad=set(result["failures"]+result["errors"]+[x["id"] for x in result["skipped"]])
                r["matched_current_test_ids"]=matches
                r["resolved_in_required_gate"]=bool(matches and not bad.intersection(matches))
                if r["resolved_in_required_gate"]:
                    r["observed_resolution"]="Passed unchanged in the declared Linux/Python runtime and documented filesystem layout; see the current test IDs and full logs."
        resolutions.append(r)
    (OUT/"failure_resolutions.json").write_text(json.dumps(resolutions,indent=2)+"\n",encoding="utf-8")
    details=["# Prior test failure diagnoses and observed repair status\n",
        "All eleven complete original tracebacks remain in failure_diagnosis.json. No missing gate result is imputed.\n"]
    for issue,resolution in zip(diagnosis["issues"],resolutions):
        details += ["## "+issue["test"],"\nClassification: "+issue["classification"],
            "\nExact exception/assertion:\n\n```text\n"+issue["exact_exception_or_assertion"]+"\n```",
            "\nRoot cause: "+issue["root_cause"],"\nEvidence: `"+issue["source_evidence"]+"`.",
            "\nProposed correction: "+issue["proposed_correction"],
            "\nObserved status: "+resolution["observed_resolution"]]
        if resolution.get("targeted_utf8_probe_passed"):
            details.append("\nA targeted unchanged test passed under PYTHONUTF8=1. The complete repaired-runtime gate remains unrun, so this does not close the gate.")
        details.append("")
    (OUT/"failure_details.md").write_text("\n".join(details)+"\n",encoding="utf-8")
    blockers=[]
    if not checkpoint.get("verified"):
        blockers.append("Original official checkpoint downloader rejected the download with ValueError('Downloaded weight length/SHA256 mismatch.'); required SHA-256 was not verified. Actual final byte count/digest were not exposed by the combined guard.")
    if not source.get("verified"):blockers.append("Pinned official source has not passed repository provenance verification.")
    if gate is None:blockers.append("Compatible Linux/Python 3.12.14 and declared dependencies were not installed after the checkpoint STOP; the existing Windows environment remains in place.")
    if not passed:blockers.append("The required root and framework gates have not both passed in the declared compatible runtime.")
    state={"recorded_utc":datetime.now(timezone.utc).isoformat(),"scope":"prerequisite repair only",
        "start_branch":"calibrated-cutoff-20261020","start_commit":"08d5c7fc28af368a85c77dec8014d92e43b1989e",
        "repair_branch":"preflight-repair-20261020","checkpoint_verified":checkpoint.get("verified",False),
        "encoder_source_verified":source.get("verified",False),"required_unit_gates_passed":passed,
        "repair_gate_complete":bool(required_assets and passed),"remaining_blockers":blockers,
        "gate_evidence":str(latest.relative_to(OUT)).replace("\\","/") if latest else None,
        "smoke_inference_run":False,"source_selection_run":False,"visa_evaluation_run":False,
        "real_encoder_inference_run":False,"frozen_model_or_test_assertions_changed":False,
        "native_windows_runtime_converted_to_linux":False,
        "checkpoint_stop_rule_applied":bool(checkpoint.get("exception")),
        "compatible_dependencies_installed":False if gate is None else None,
        "full_root_framework_gates_rerun":bool(gate and gate.get("gates")),
        "active_ci_workflow_installed":False,
        "remaining_old_test_failures_are_not_claimed_resolved":not passed}
    (OUT/"repair_summary.json").write_text(json.dumps(state,indent=2)+"\n",encoding="utf-8")
    checkpoint_text=(f"**Verified.** `{checkpoint['actual_bytes']:,}` bytes; SHA-256 `{checkpoint['actual_sha256']}`.\n\nPersistent host path: `{checkpoint['destination']}`.\n" if checkpoint.get("verified") else f"**Failed verification.** The unchanged repository downloader raised `{checkpoint.get('exception')}`. It uses one combined length/digest guard and does not expose the actual final values in this exception. The exact failed subcondition is therefore **undetermined** from the retained evidence. The required digest was not verified, and no substitute or bypass was attempted.\n\nDownload started `{checkpoint.get('started_utc')}` and ended `{checkpoint.get('finished_utc')}`. The downloader deleted its rejected partial file. No verified checkpoint remains at the requested persistent path. The user's STOP rule was applied; no further runtime installation, CI execution or full test-gate rerun followed.\n")
    source_text=(f"**Verified.** Official commit `{source['required_source_commit']}`; canonical manifest SHA-256 `{source['required_manifest_sha256']}`; {len(source['verification']['source_files_sha256'])} required Python/license files passed the unchanged verifier.\n\nPersistent host path: `{source['destination']}`.\n" if source.get("verified") else "**Not yet verified.**\n")
    table="\n".join(f"| `{r['method']}` | {r['classification']} | {'Passed unchanged in repaired gate' if r['resolved_in_required_gate'] else 'Not yet resolved by a passing required gate'} |" for r in resolutions)
    test_table="No repaired-runtime suite result is available."
    runtime="The compatible Linux runtime definition was prepared but **not installed or executed** because checkpoint verification failed. No root/framework gate rerun on a repaired interpreter is claimed."
    current=read("current_runtime_versions.json")
    if current:
        runtime+="\n\nThe host runtime left in place is: `"+current["python"]+"`; interpreter `"+current["executable"]+"`. Observed package versions:\n\n"+"\n".join(f"- {k}: `{v}`" for k,v in current["versions"].items())
    if gate:
        rows=[]
        for k,v in gate.get("gates",{}).items():
            r=v.get("report")
            if r:
                count=r["run"]
                passed_count=count-len(r["errors"])-len(r["failures"])-len(r["skipped"])-len(r["expected_failures"])
                rows.append(f"| {k} | {r['discovered']} | {count} | {passed_count} | {len(r['failures'])} | {len(r['errors'])} | {len(r['skipped'])} | {v['returncode']} |")
        test_table="| Suite | Discovered | Run | Passed | Failures | Errors | Skipped | Exit |\n|---|---:|---:|---:|---:|---:|---:|---:|\n"+"\n".join(rows)
        versions_path=latest.parent/"runtime_versions.stdout.log"
        if versions_path.is_file() and versions_path.stat().st_size:
            versions=json.loads(versions_path.read_text())
            runtime=f"Actual platform: `{versions['platform']}`. Python: `{versions['python']}`.\n\nBoth suites used `{gate.get('same_test_python_interpreter')}`.\n\n"+"\n".join(f"- {k}: `{v}`" for k,v in versions["versions"].items())
        else:runtime="Runtime bootstrap failed before version verification; inspect the gate summary and dependency logs."
    status="COMPLETE — verified assets and passing required gates" if state["repair_gate_complete"] else "INCOMPLETE — see remaining blockers"
    report=f"""# Preflight repair report

**Status: {status}.** This work repairs prerequisites only. No smoke inference,
source selection, cutoff calibration, VisA evaluation or completed-study verdict
is part of this repair.

Started from `calibrated-cutoff-20261020` at
`08d5c7fc28af368a85c77dec8014d92e43b1989e`; new branch
`preflight-repair-20261020`. All earlier reports/results remain read-only. The only
runtime definition is saved as inactive evidence in `proposed_workflow.yml`.
No live workflow was installed or executed. No model implementation or existing
test assertion was edited.

## Checkpoint

{checkpoint_text}
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

{source_text}
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

{table}

The missing acquisition report was diagnosed by observing its real subprocess:
Python exited 2 because `C:\\workspace\\tools\\acquire_public_data.py` was absent.
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

{runtime}

{test_table}

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

{chr(10).join('- '+b for b in blockers) if blockers else 'No remaining blocker to the prerequisite gates in the validated Linux runtime. The native Windows runtime remains outside that contract, and no future inference run has been approved.'}

All repair results are summarized in [repair_summary.json](repair_summary.json).
Observed per-test resolutions are in [failure_resolutions.json](failure_resolutions.json).
Commands and full logs are saved in [commands.jsonl](commands.jsonl) and `logs/`;
CI has a separate command ledger in its run directory. No operating-point or
model-reproduction outcome is claimed.
"""
    (OUT/"preflight_repair_report.md").write_text(report,encoding="utf-8")
    print(json.dumps(state),flush=True)


if __name__=="__main__":main()
