"""Read-only validation of repair evidence after the checkpoint STOP."""
import ast
import hashlib
import json
from pathlib import Path
import subprocess

OUT=Path(__file__).resolve().parent
REPO=OUT.parents[1]


def digest(path):
    with path.open("rb") as f:return hashlib.file_digest(f,"sha256").hexdigest()


def main():
    prior={}
    for name in ("results/calibrated_cutoff_20261020","results/calibrated_cutoff_20261020/continuation_20261020T120107Z"):
        root=REPO/name
        manifest=json.loads((root/"artifact_manifest.sha256.json").read_text())
        mismatches=[p for p,h in manifest["sha256"].items() if digest(root/p)!=h]
        assert not mismatches,mismatches
        prior[name]={"files_checked":len(manifest["sha256"]),"mismatches":mismatches}
    source=json.loads((OUT/"encoder_source_verification.json").read_text())
    assert source["verified"]
    source_root=Path(source["destination"])
    source_bad=[p for p,h in source["verification"]["source_files_sha256"].items() if digest(source_root/p)!=h]
    assert not source_bad,source_bad
    frozen=json.loads(subprocess.check_output(["git","show","08d5c7fc28af368a85c77dec8014d92e43b1989e:results/controlled_full_image_20261018/protocol.json"]))
    code={name:hashlib.sha256(subprocess.check_output(["git","show","HEAD:"+name])).hexdigest()==h for name,h in frozen["code_sha256"].items()}
    assert all(code.values())
    for p in OUT.glob("*.py"):ast.parse(p.read_text(encoding="utf-8"))
    checkpoint=json.loads((OUT/"checkpoint_verification.json").read_text())
    summary=json.loads((OUT/"repair_summary.json").read_text())
    assert not checkpoint["verified"] and not summary["repair_gate_complete"]
    assert summary["checkpoint_stop_rule_applied"] and not summary["full_root_framework_gates_rerun"]
    assert not summary["active_ci_workflow_installed"]
    assert not (REPO/".github/workflows/preflight-repair.yml").exists()
    changes=subprocess.check_output(["git","diff","--name-only"]).decode().splitlines()
    assert not changes,changes
    report={"validation_scope":"Saved evidence only; no repair step, test gate or inference run",
        "prior_evidence":prior,"persistent_encoder_source_files_checked":len(source["verification"]["source_files_sha256"]),
        "encoder_source_file_mismatches":source_bad,"frozen_git_code_hash_matches":code,
        "checkpoint_file_present":Path(checkpoint["destination"]).is_file(),
        "checkpoint_partial_present":Path(checkpoint["destination"]+".partial").is_file(),
        "checkpoint_verification_passed":False,"full_gates_executed":False,"active_ci_workflow":False,
        "prior_tracked_file_changes":changes,"repair_summary_is_incomplete":True}
    (OUT/"evidence_validation.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(report,indent=2))


if __name__=="__main__":main()
