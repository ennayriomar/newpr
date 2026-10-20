"""Restore the declared Linux runtime and run existing unit gates only."""
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import time
import traceback

REPAIR=Path(__file__).resolve().parent
REPO=REPAIR.parents[1]
RUN=REPAIR/"ci_runs"/(os.environ.get("GITHUB_RUN_ID","manual")+"-"+os.environ.get("GITHUB_RUN_ATTEMPT","1"))


def save(name,value):
    (RUN/name).write_text(json.dumps(value,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def command(name,argv,env):
    t0=time.perf_counter();start=datetime.now(timezone.utc).isoformat()
    out=RUN/(name+".stdout.log");err=RUN/(name+".stderr.log")
    with out.open("wb") as stdout,err.open("wb") as stderr:
        result=subprocess.run(argv,cwd=REPO,env=env,stdout=stdout,stderr=stderr)
    record={"name":name,"argv":argv,"cwd":str(REPO),"started_utc":start,
        "finished_utc":datetime.now(timezone.utc).isoformat(),"elapsed_seconds":time.perf_counter()-t0,
        "returncode":result.returncode,"stdout":out.name,"stderr":err.name}
    with (RUN/"commands.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps(record)+"\n")
    print(json.dumps(record),flush=True)
    return result.returncode


def require_command(name,argv,env):
    code=command(name,argv,env)
    if code:raise RuntimeError(f"{name} exited {code}; see complete command logs")


def main():
    RUN.mkdir(parents=True,exist_ok=False)
    summary={"scope":"prerequisite repair unit gates only","gate_passed":False,
        "smoke_inference_run":False,"source_selection_run":False,"visa_evaluation_run":False,
        "model_settings_changed":False,"started_utc":datetime.now(timezone.utc).isoformat(),
        "github_run_id":os.environ.get("GITHUB_RUN_ID"),"github_sha":os.environ.get("GITHUB_SHA"),
        "runner_os":platform.platform(),"bootstrap_python":sys.version}
    env=os.environ.copy()
    env.update(PYTHONDONTWRITEBYTECODE="1",PYTHONUTF8="1",PYTHONIOENCODING="utf-8",
        LANG="C.UTF-8",LC_ALL="C.UTF-8",PYTHONPATH=str(REPO/"framework")+os.pathsep+str(REPO),
        OMP_NUM_THREADS="4",MKL_NUM_THREADS="4",OPENBLAS_NUM_THREADS="4",
        MPLCONFIGDIR=str(REPAIR/"runtime/mpl"),PIP_CACHE_DIR=str(REPAIR/"assets/pip-cache"))
    try:
        assert platform.system()=="Linux","The declared Linux runtime is required"
        assert sys.version_info[:3]==(3,12,14),"Do not silently substitute a Python patch version"
        # These host-side verification receipts are required before the test job
        # is published; unit gates do not load checkpoint tensors or score images.
        checkpoint=json.loads((REPAIR/"checkpoint_verification.json").read_text())
        source=json.loads((REPAIR/"encoder_source_verification.json").read_text())
        assert checkpoint["verified"] and checkpoint["actual_sha256"]=="36e4deffbaef061a2576705b0c36f93621e2ae20bf6274694821b0b492551b51"
        assert source["verified"] and source["required_source_commit"]=="7764ea0f912e53c92e82eb78a2a1631e92725fc8"
        protocol_path=REPO/"results/controlled_full_image_20261018/protocol.json"
        data=protocol_path.read_bytes()
        assert hashlib.sha256(data).hexdigest()=="dc078b5a681b8a44015dc02a227afb4b20f248e7ca70ac8e31a95f321aa2f408"
        protocol=json.loads(data)
        checks={name:{"expected":expected,"actual":hashlib.sha256((REPO/name).read_bytes()).hexdigest()}
                for name,expected in protocol["code_sha256"].items()}
        assert all(v["expected"]==v["actual"] for v in checks.values()),"Frozen code changed"
        assert hashlib.sha256((REPO/"configs/controlled_full_image_20261018.json").read_bytes()).hexdigest()==protocol["config_sha256"]
        save("frozen_code_check.json",checks)
        require_command("workspace_parent",["sudo","install","-d","-o",str(os.getuid()),"-g",str(os.getgid()),"/workspace"],env)
        link=Path("/workspace/tools")
        if link.exists() or link.is_symlink():
            assert link.resolve()==(REPO/"framework").resolve(),"Preserve unrelated /workspace/tools"
        else:link.symlink_to(REPO/"framework",target_is_directory=True)
        assert Path("/tmp").is_dir()
        save("documented_layout.json",{"workspace_tools":str(link),"resolved_target":str(link.resolve()),
            "acquisition_helper_present":(link/"acquire_public_data.py").is_file(),"tmp_exists":True,
            "test_assertions_changed":False})
        venv=REPAIR/"assets/linux-venv"
        require_command("create_venv",[sys.executable,"-m","venv",str(venv)],env)
        python=str(venv/"bin/python")
        require_command("install_declared_dependencies",[python,"-m","pip","install","--disable-pip-version-check",
            "--report",str(RUN/"pip_install_report.json"),"-r",str(REPO/"requirements.txt"),
            "-r",str(REPO/"framework/requirements-pipeline.txt")],env)
        probe="""import sys,json,platform,locale,inspect,tarfile,fcntl,importlib.metadata as m
import torch,numpy,PIL,sklearn,scipy,tifffile,cv2,faiss,yaml,torchvision,matplotlib,threadpoolctl
import safe_iad,utils
versions={n:m.version(n) for n in ['torch','torchvision','numpy','Pillow','scikit-learn','scipy','tifffile','opencv-python-headless','faiss-cpu','PyYAML','matplotlib','threadpoolctl','filelock','fsspec','Jinja2','MarkupSafe','networkx']}
expected={'torch':'2.7.1+cpu','torchvision':'0.22.1+cpu','numpy':'2.2.6','Pillow':'12.3.0','scikit-learn':'1.8.0','scipy':'1.17.0','tifffile':'2025.10.16','opencv-python-headless':'4.12.0.88','faiss-cpu':'1.12.0','PyYAML':'6.0.3','matplotlib':'3.10.8','threadpoolctl':'3.6.0','filelock':'3.32.3','fsspec':'2026.7.0','Jinja2':'3.1.6','MarkupSafe':'3.0.3','networkx':'3.6.1'}
assert versions==expected,(versions,expected)
assert sys.version_info[:3]==(3,12,14)
assert 'filter' in inspect.signature(tarfile.TarFile.extractall).parameters
print(json.dumps({'python':sys.version,'executable':sys.executable,'platform':platform.platform(),'versions':versions,'preferred_encoding':locale.getpreferredencoding(False),'fcntl_module':fcntl.__file__,'safe_iad_module':safe_iad.__file__,'utils_module':utils.__file__,'cuda_available':torch.cuda.is_available(),'model_instantiated':False},indent=2))
"""
        require_command("runtime_versions",[python,"-B","-c",probe],env)
        require_command("pip_freeze",[python,"-m","pip","freeze"],env)
        require_command("pip_check",[python,"-m","pip","check"],env)
        reports={}
        for suite,name in (("tests","root_tests"),("framework/tests","framework_tests")):
            output=RUN/(name+".json")
            code=command(name,[python,"-B",str(REPAIR/"run_existing_tests.py"),"--source",str(REPO),
                "--suite",suite,"--output",str(output)],env)
            reports[name]={"returncode":code,"report":json.loads(output.read_text()) if output.is_file() else None}
        summary["same_test_python_interpreter"]=python
        summary["gates"]=reports
        summary["gate_passed"]=all(r["returncode"]==0 and r["report"] and r["report"]["successful"]
            and not r["report"]["skipped"] and not r["report"]["expected_failures"]
            and not any(t.startswith("unittest.loader._FailedTest.") for t in r["report"]["test_ids"])
            for r in reports.values())
    except BaseException as exc:
        summary.update(exception=repr(exc),traceback=traceback.format_exc())
        print(summary["traceback"],file=sys.stderr,flush=True)
    finally:
        summary["finished_utc"]=datetime.now(timezone.utc).isoformat()
        save("gate_summary.json",summary)
        print(json.dumps(summary,indent=2),flush=True)
    raise SystemExit(0 if summary["gate_passed"] else 1)


if __name__=="__main__":main()
