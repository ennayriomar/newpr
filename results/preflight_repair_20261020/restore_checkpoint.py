"""Use the unchanged repository checksum-verifying official downloader only."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sys
import threading
import traceback

OUT=Path(__file__).resolve().parent
REPO=OUT.parents[1]
sys.path[:0]=[str(REPO/"framework")]
from safe_iad.vision_hybrid_features import prepare, WEIGHT_SHA256, WEIGHT_BYTES, WEIGHT_URL


def main():
    expected="36e4deffbaef061a2576705b0c36f93621e2ae20bf6274694821b0b492551b51"
    assert WEIGHT_SHA256==expected
    path=OUT/"assets/checkpoints/dinov2_vitl14_reg4_pretrain.pth"
    done=threading.Event()
    def progress():
        while not done.wait(20):
            partial=path.with_suffix(path.suffix+".partial")
            print(json.dumps({"stage":"official_checkpoint_download","bytes_written":partial.stat().st_size if partial.exists() else 0,"expected_bytes":WEIGHT_BYTES}),flush=True)
    thread=threading.Thread(target=progress,daemon=True);thread.start()
    record={"started_utc":datetime.now(timezone.utc).isoformat(),"url":WEIGHT_URL,"expected_sha256":expected,
        "expected_bytes":WEIGHT_BYTES,"destination":str(path),"downloader":"safe_iad.vision_hybrid_features.prepare",
        "downloader_source_git_path":"framework/safe_iad/vision_hybrid_features.py",
        "model_instantiated":False,"inference_run":False,"verified":False}
    try:
        prepare(path)
        with path.open("rb") as f: actual=hashlib.file_digest(f,"sha256").hexdigest()
        assert actual==expected and path.stat().st_size==WEIGHT_BYTES
        record.update(verified=True,actual_sha256=actual,actual_bytes=path.stat().st_size)
    except BaseException as exc:
        record.update(exception=repr(exc),traceback=traceback.format_exc())
        raise
    finally:
        done.set();record["finished_utc"]=datetime.now(timezone.utc).isoformat()
        (OUT/"checkpoint_verification.json").write_text(json.dumps(record,indent=2)+"\n",encoding="utf-8")
        print(json.dumps(record),flush=True)


if __name__=="__main__":main()
