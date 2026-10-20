"""Retrieve and verify exactly the encoder source pinned by the frozen protocol."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import traceback

OUT=Path(__file__).resolve().parent
REPO=OUT.parents[1]
sys.path[:0]=[str(REPO/"framework")]
from safe_iad.safal_features import SOURCE_PIN,SOURCE_URL,SOURCE_FILES_SHA256,verify_source,export_source_manifest


def call(name,argv):
    print(json.dumps({"name":name,"argv":argv}),flush=True)
    result=subprocess.run(argv,capture_output=True)
    (OUT/"logs"/(name+".stdout.log")).write_bytes(result.stdout)
    (OUT/"logs"/(name+".stderr.log")).write_bytes(result.stderr)
    with (OUT/"commands.jsonl").open("a",encoding="utf-8") as f:
        f.write(json.dumps({"name":name,"argv":argv,"returncode":result.returncode,
            "stdout":"logs/"+name+".stdout.log","stderr":"logs/"+name+".stderr.log"})+"\n")
    result.check_returncode()
    return result.stdout


def main():
    data=call("frozen_protocol_git_blob",["git","-C",str(REPO),"show","05c0fcea1b3289f0daf2f658c56b08c2848b71e9:results/controlled_full_image_20261018/protocol.json"])
    protocol=json.loads(data)
    assert protocol["encoder"]["source_commit"]==SOURCE_PIN
    assert protocol["encoder"]["source_manifest_sha256"]==SOURCE_FILES_SHA256
    destination=OUT/"assets/dinov2-source"
    record={"started_utc":datetime.now(timezone.utc).isoformat(),"verified":False,
        "protocol_sha256":hashlib.sha256(data).hexdigest(),"required_source_commit":SOURCE_PIN,
        "required_manifest_sha256":SOURCE_FILES_SHA256,"official_source_url":SOURCE_URL,
        "destination":str(destination),"model_instantiated":False,"inference_run":False}
    try:
        if destination.exists():raise FileExistsError("Preserve source destination; use a new attempt if it already exists")
        call("encoder_source_git_init",["git","init",str(destination)])
        call("encoder_source_git_config",["git","-C",str(destination),"config","core.autocrlf","false"])
        call("encoder_source_git_fetch",["git","-C",str(destination),"fetch","--depth","1",SOURCE_URL,SOURCE_PIN])
        call("encoder_source_git_checkout",["git","-C",str(destination),"checkout","--detach","FETCH_HEAD"])
        verification=verify_source(destination)
        manifest=export_source_manifest(destination)
        # The exported manifest is derived only after the unchanged verifier
        # establishes the trusted pinned Git source and canonical file digest.
        replay=verify_source(destination)
        assert replay==verification
        record.update(verified=True,verification=verification,exported_manifest=str(manifest),
            exported_manifest_sha256=hashlib.sha256(manifest.read_bytes()).hexdigest())
    except BaseException as exc:
        record.update(exception=repr(exc),traceback=traceback.format_exc())
        raise
    finally:
        record["finished_utc"]=datetime.now(timezone.utc).isoformat()
        (OUT/"encoder_source_verification.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(record),flush=True)


if __name__=="__main__":main()
