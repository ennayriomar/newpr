"""Download checksum-verified controlled results without cloning old archives."""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path, PurePosixPath
import tempfile
from urllib.parse import quote
from urllib.request import Request, urlopen

PREFIX="results/controlled_full_image_20261018/"


def request(url):
    return urlopen(Request(url,headers={"User-Agent":"SAFAL-controlled-results-verifier"}),timeout=60)


def safe_destination(root,name):
    relative=PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts or "\\" in name:
        raise ValueError("Unsafe result path")
    dest=(root/name).resolve()
    if not dest.is_relative_to(root.resolve()):raise ValueError("Result path escapes destination")
    return dest


def download(base,root,entry):
    path=safe_destination(root,entry["path"])
    if path.exists():
        with path.open("rb") as handle:actual=hashlib.file_digest(handle,"sha256").hexdigest()
        if actual==entry["sha256"] and path.stat().st_size==entry["bytes"]:return
        raise ValueError(f"Existing result fails checksum; preserve it and use a fresh destination: {path}")
    path.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(prefix=path.name+".",suffix=".partial",dir=path.parent,delete=False) as handle:
        partial=Path(handle.name)
        try:
            digest=hashlib.sha256();size=0
            with request(base+quote(PREFIX+entry["path"],safe="/")) as response:
                if response.status!=200:raise ValueError("Expected a complete HTTP200 response")
                while data:=response.read(1024*1024):
                    digest.update(data);size+=len(data);handle.write(data)
            handle.flush()
            if size!=entry["bytes"] or digest.hexdigest()!=entry["sha256"]:
                raise ValueError("Downloaded result size/SHA256 mismatch: "+entry["path"])
            partial.replace(path)
        finally:
            if partial.exists():partial.unlink()


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ref",required=True,help="Immutable40-character Git commit from the published report")
    parser.add_argument("--destination",type=Path,required=True)
    parser.add_argument("--scope",choices=["report","complete"],default="report",
                        help="report: figures, selected raw maps, scores and bootstrap data; complete: also all cohort/source maps and fitted support descriptors")
    parser.add_argument("--workers",type=int,default=4)
    parser.add_argument("--dry-run",action="store_true")
    args=parser.parse_args()
    if len(args.ref)!=40 or any(c not in "0123456789abcdef" for c in args.ref):parser.error("Use the immutable full Git commit hash")
    if not 1<=args.workers<=8:parser.error("--workers must be between1 and8")
    base=f"https://raw.githubusercontent.com/ennayriomar/newpr/{args.ref}/"
    with request(base+PREFIX+"DOWNLOAD_MANIFEST.json") as response:manifest_bytes=response.read()
    manifest=json.loads(manifest_bytes)
    entries=[entry for entry in manifest["files"] if args.scope=="complete" or entry["report_bundle"]]
    for entry in entries:safe_destination(args.destination,entry["path"])
    print(json.dumps({"scope":args.scope,"files":len(entries),"bytes":sum(e["bytes"] for e in entries),
                      "source_commit":args.ref,"native_images_and_foundation_weights_included":False}),flush=True)
    if args.dry_run:return
    args.destination.mkdir(parents=True,exist_ok=True)
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(lambda entry:download(base,args.destination,entry),entries))
    (args.destination/"DOWNLOAD_MANIFEST.json").write_bytes(manifest_bytes)
    print("All requested files passed size and SHA256 verification.",flush=True)


if __name__=="__main__":main()
