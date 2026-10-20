"""Read-only export of this audit's publishable files for the GitHub connector."""
import argparse
import base64
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[2]
PREFIX = OUT.relative_to(REPO).as_posix() + "/"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--file")
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--length", type=int, default=24000)
    parser.add_argument("--text", action="store_true")
    args = parser.parse_args()
    if args.list:
        names = subprocess.check_output(["git", "-C", str(REPO), "ls-files", "--others", "--exclude-standard", "--", PREFIX]).decode().splitlines()
        tracked = subprocess.check_output(["git", "-C", str(REPO), "ls-files", "--", PREFIX]).decode().splitlines()
        result=[]
        for name in sorted(set(names+tracked)):
            p=REPO/name
            if p.is_file():
                result.append({"path":name,"bytes":p.stat().st_size,"base64_characters":4*((p.stat().st_size+2)//3)})
        print(json.dumps(result))
    else:
        path=(REPO/args.file).resolve(strict=True)
        if not path.is_relative_to(OUT) or not args.file.startswith(PREFIX):
            raise ValueError("Publication path must be within the new audit directory")
        if args.text:
            print(json.dumps({"content":path.read_bytes().decode("utf-8")}))
        else:
            value=base64.b64encode(path.read_bytes()).decode()
            print(value[args.offset:args.offset+args.length])


if __name__ == "__main__":
    main()
