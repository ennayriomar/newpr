"""Join/check 8 MiB result parts from a local directory or public HTTPS base URL."""
import argparse, hashlib, json, os
from pathlib import Path
import urllib.parse, urllib.request

def safe_name(name):
    if not isinstance(name,str) or not name or Path(name).name!=name or "\\" in name:
        raise ValueError("Unsafe archive/part filename")
    return name

def digest(path):
    with path.open("rb") as fp:return hashlib.file_digest(fp,"sha256").hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest",type=Path,default=Path(__file__).with_name("manifest.json"))
    p.add_argument("--parts-dir",type=Path)
    p.add_argument("--base-url",help="Public HTTPS directory containing the named parts")
    p.add_argument("--destination",type=Path)
    a=p.parse_args();m=json.loads(a.manifest.read_text())
    destination=a.destination or Path(safe_name(m["archive"]))
    if destination.exists():
        if destination.stat().st_size==m["bytes"] and digest(destination)==m["sha256"]:
            print("Verified existing archive:",destination);return
        raise ValueError("Destination exists with different bytes; choose another path")
    if a.base_url and urllib.parse.urlparse(a.base_url).scheme!="https":raise ValueError("HTTPS base URL required")
    source=a.parts_dir or a.manifest.parent
    destination.parent.mkdir(parents=True,exist_ok=True)
    temporary=destination.with_name(destination.name+".partial")
    if temporary.exists():raise ValueError("A partial download already exists; use a new destination")
    total=0;whole=hashlib.sha256()
    try:
        with temporary.open("xb") as out:
            for part in m["parts"]:
                name=safe_name(part["name"])
                if part["offset"]!=total:raise ValueError("Noncontiguous part offsets")
                if a.base_url:
                    url=a.base_url.rstrip("/")+"/"+urllib.parse.quote(name,safe="")
                    handle=urllib.request.urlopen(url,timeout=60)
                    if urllib.parse.urlparse(handle.url).scheme!="https":raise ValueError("Non-HTTPS redirect")
                else:handle=(source/name).open("rb")
                count=0;h=hashlib.sha256()
                with handle:
                    while True:
                        block=handle.read(1024*1024)
                        if not block:break
                        count+=len(block)
                        if count>part["bytes"]:raise ValueError("Part exceeded declared length")
                        h.update(block);whole.update(block);out.write(block)
                if count!=part["bytes"] or h.hexdigest()!=part["sha256"]:raise ValueError("Part checksum mismatch: "+name)
                total+=count;print("Verified",name,flush=True)
        if total!=m["bytes"] or whole.hexdigest()!=m["sha256"]:raise ValueError("Assembled ZIP checksum mismatch")
        os.replace(temporary,destination);print("Verified complete archive:",destination)
    except Exception:
        if temporary.exists():temporary.unlink()
        raise

if __name__=="__main__":main()
