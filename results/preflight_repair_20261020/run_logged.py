"""Execute repair commands with full separate stdout/stderr and exit records."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import time

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", required=True)
    parser.add_argument("--cwd", type=Path, default=REPO)
    parser.add_argument("--timeout", type=int, default=3600)
    parser.add_argument("--env", action="append", default=[])
    parser.add_argument("argv", nargs=argparse.REMAINDER)
    args = parser.parse_args()
    argv = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
    env = os.environ.copy()
    for name in ("tmp", "runtime/mpl", "assets/pip-cache"):
        (OUT/name).mkdir(parents=True, exist_ok=True)
    overrides = dict(TEMP=str(OUT/"tmp"),TMP=str(OUT/"tmp"),TMPDIR=str(OUT/"tmp"),
        PYTHONDONTWRITEBYTECODE="1",PYTHONIOENCODING="utf-8",PYTHONUTF8="1",
        MPLCONFIGDIR=str(OUT/"runtime/mpl"),PIP_CACHE_DIR=str(OUT/"assets/pip-cache"))
    for item in args.env:
        key,value=item.split("=",1);overrides[key]=value
    env.update(overrides)
    paths = {s:OUT/"logs"/(args.name+"."+s+".log") for s in ("stdout","stderr")}
    if any(p.exists() for p in paths.values()):
        raise FileExistsError("Preserve command logs; use a new command name")
    start = datetime.now(timezone.utc).isoformat(); t0=time.perf_counter()
    code=None; error=None
    with paths["stdout"].open("wb") as stdout, paths["stderr"].open("wb") as stderr:
        try:
            result=subprocess.run(argv,cwd=args.cwd,env=env,stdout=stdout,stderr=stderr,timeout=args.timeout)
            code=result.returncode
        except (OSError,subprocess.TimeoutExpired) as exc:
            error=repr(exc);stderr.write((error+"\n").encode())
    record={"name":args.name,"argv":argv,"cwd":str(args.cwd),"environment_overrides":overrides,
        "started_utc":start,"finished_utc":datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds":time.perf_counter()-t0,"returncode":code,"infrastructure_error":error,
        **{s:str(p.relative_to(OUT)).replace("\\","/") for s,p in paths.items()}}
    with (OUT/"commands.jsonl").open("a",encoding="utf-8") as f:f.write(json.dumps(record)+"\n")
    print(json.dumps(record),flush=True)
    raise SystemExit(code if code is not None else 124)


if __name__=="__main__":main()
