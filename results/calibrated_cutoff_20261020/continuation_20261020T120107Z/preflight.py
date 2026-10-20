"""Read-only prerequisite audit. This script never performs model inference.

Run from anywhere with Python 3.11+. All outputs are beside this script.
The reference snapshot is exported from the recorded Git commit with exact
blob bytes, avoiding Windows checkout CRLF conversion. It is ignored by Git.
"""
from collections import Counter
import csv
import ctypes
import gzip
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import winreg

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[2]
REFERENCE = "05c0fcea1b3289f0daf2f658c56b08c2848b71e9"
SNAPSHOT = OUT / "reference_source"
EXPECTED_WEIGHT = "36e4deffbaef061a2576705b0c36f93621e2ae20bf6274694821b0b492551b51"
OLD = "results/controlled_full_image_20261018/"
RUNTIME = Path(r"C:\Users\ennay\Downloads\safe_iad_m1\safe_iad\venv\Scripts\python.exe")
ROOTS = {
    "mvtec_ad2": Path(r"C:\Users\ennay\Downloads\safe_iad_m1\safe_iad\data\mvtec_ad_2\mvtec_ad_2"),
    "mvtec_ad": Path(r"C:\Users\ennay\Downloads\mvtec_ad"),
    "visa": Path(r"C:\Users\ennay\Downloads\safe_iad_m1\safe_iad\data\visa"),
}
EXTENSIONS = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


def save(name, value):
    path = OUT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


_git_command_count = 0


def capture_command(argv, input_bytes=None):
    global _git_command_count
    _git_command_count += 1
    name = f"git_{_git_command_count:03d}"
    started = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()
    result = subprocess.run(argv, input=input_bytes, capture_output=True, timeout=60)
    (OUT/"logs"/(name+".stdout.log")).write_bytes(result.stdout)
    (OUT/"logs"/(name+".stderr.log")).write_bytes(result.stderr)
    if input_bytes is not None:
        (OUT/"logs"/(name+".stdin.log")).write_bytes(input_bytes)
    record = {"name":name,"argv":argv,"cwd":str(REPO),"started_utc":started,
              "elapsed_seconds":time.perf_counter()-t0,"returncode":result.returncode,
              "stdout":"logs/"+name+".stdout.log","stderr":"logs/"+name+".stderr.log"}
    if input_bytes is not None:
        record["stdin"] = "logs/"+name+".stdin.log"
    with (OUT/"commands.jsonl").open("a",encoding="utf-8") as f:
        f.write(json.dumps(record)+"\n")
    result.check_returncode()
    return result.stdout


def git(*args):
    return capture_command(["git", "-C", str(REPO), *args])


def blob(name):
    return git("show", REFERENCE + ":" + name)


def command(name, argv, cwd=None, env=None, timeout=900):
    start = datetime.now(timezone.utc).isoformat()
    t0 = time.perf_counter()
    logs = OUT / "logs"
    logs.mkdir(exist_ok=True)
    with (logs / (name + ".stdout.log")).open("wb") as stdout, (logs / (name + ".stderr.log")).open("wb") as stderr:
        try:
            completed = subprocess.run(argv, cwd=cwd, env=env, stdout=stdout, stderr=stderr, timeout=timeout)
            code, error = completed.returncode, None
        except (subprocess.TimeoutExpired, OSError) as exc:
            code, error = None, repr(exc)
            stderr.write((repr(exc) + "\n").encode())
    record = {
        "name": name, "argv": [str(a) for a in argv], "cwd": str(cwd or REPO),
        "started_utc": start, "elapsed_seconds": time.perf_counter() - t0,
        "returncode": code, "infrastructure_error": error,
        "stdout": "logs/" + name + ".stdout.log", "stderr": "logs/" + name + ".stderr.log",
        "environment_overrides": {k: env[k] for k in ("TEMP", "TMP", "TMPDIR", "MPLCONFIGDIR", "PYTHONDONTWRITEBYTECODE", "PYTHONPATH") if env and k in env},
    }
    with (OUT / "commands.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(record) + "\n")
    print(json.dumps(record), flush=True)
    return record


def source_snapshot():
    names = git("ls-tree", "-r", "--name-only", REFERENCE).decode().splitlines()
    selected = [n for n in names if
                ("/" not in n and (n.endswith((".py", ".sh")) or n in ("README.md", "requirements.txt")))
                or n.startswith(("framework/", "models/", "tests/", "configs/", "prepare_data/"))
                or (n.startswith("docs/") and n.endswith(".md"))]
    # Use only materialized source paths. Asking git archive for an absent
    # path in a partial clone may initiate an unbounded promisor fetch.
    materialized = {line[2:] for line in git("ls-files", "-t").decode().splitlines() if line.startswith("H ")}
    selected = sorted(set(selected) & materialized)
    request = "".join(REFERENCE + ":" + n + "\n" for n in selected).encode()
    exported = capture_command(["git", "-C", str(REPO), "cat-file", "--batch"], request)
    manifest = {}
    SNAPSHOT.mkdir(exist_ok=True)
    position = 0
    for name in selected:
        end = exported.index(b"\n", position)
        header = exported[position:end].split()
        if len(header) != 3 or header[1] != b"blob":
            raise ValueError("Missing source blob: " + name)
        size = int(header[2]); position = end + 1
        data = exported[position:position + size]; position += size + 1
        path = SNAPSHOT / name
        if not path.resolve().is_relative_to(SNAPSHOT.resolve()):
            raise ValueError("Unsafe Git source path")
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        manifest[name] = digest(data)
    save("reference_source_manifest.json", {"commit": REFERENCE, "files": manifest,
         "batch_export_sha256": digest(exported), "exact_git_blob_bytes": True,
         "recreate": "python results/calibrated_cutoff_20261020/continuation_20261020T120107Z/preflight.py",
         "no_scoring_code_modified": True})
    agents = [n for n in names if Path(n).name == "AGENTS.md"]
    protocol_bytes = blob(OLD + "protocol.json")
    protocol = json.loads(protocol_bytes)
    protocol_expected = blob(OLD + "protocol.json.sha256").decode().split()[0]
    checks = {}
    for name, expected in protocol["code_sha256"].items():
        canonical = blob(name)
        working = (REPO / name).read_bytes()
        checks[name] = {"expected": expected, "git_blob_sha256": digest(canonical),
                        "git_blob_match": digest(canonical) == expected,
                        "working_tree_sha256": digest(working),
                        "checkout_crlf_only": working.replace(b"\r\n", b"\n") == canonical}
    additional = {"config": ("configs/controlled_full_image_20261018.json", protocol["config_sha256"]),
                  "source_plan": (OLD + "source_plan.json", protocol["source_plan_sha256"]),
                  "source_selection": (OLD + "source_selection.json", protocol["source_selection_sha256"]),
                  "calibration_ids": (OLD + "calibration_ids.json", protocol["calibration_ids_sha256"])}
    for key, (name, expected) in additional.items():
        data = blob(name)
        checks[key] = {"path": name, "expected": expected, "git_blob_sha256": digest(data), "git_blob_match": digest(data) == expected}
    config = json.loads(blob("configs/controlled_full_image_20261018.json"))
    checks["protocol"] = {"expected": protocol_expected, "git_blob_sha256": digest(protocol_bytes), "git_blob_match": digest(protocol_bytes) == protocol_expected}
    save("integrity_check.json", {"base_commit": REFERENCE, "AGENTS_files_in_repository": agents,
        "checks": checks, "all_recorded_hashes_match_git_blobs": all(x["git_blob_match"] for x in checks.values()),
        "windows_checkout_conversion": "Initial checkout uses CRLF; tests use byte-exact Git export under the NEW results directory. Historical files are never edited.",
        "settings_confirmed": {"backbone": config["backbone"], "lambda": protocol["frozen_lambda"],
            "resize": config["resize"], "crop": config["crop"], "layers": config["layers"],
            "variance": config["variance"], "clusters": config["clusters"], "gate": config["gate"],
            "original_shots": config["shots"], "original_target_seeds": config["target_seeds"]},
        "old_image_cutoffs_provenance_only": {"baseline_k1": protocol["calibration"]["0.0"]["image"],
            "hybrid_k1": protocol["calibration"]["0.25"]["image"],
            "k2_k4": "No original budget-specific calibration exists. No new cutoff was fitted or assigned."}})
    (OUT / "provenance").mkdir(exist_ok=True)
    (OUT / "provenance/original_protocol.json").write_bytes(protocol_bytes)
    (OUT / "provenance/original_protocol.json.gz").write_bytes(gzip.compress(protocol_bytes, mtime=0))
    (OUT / "provenance/original_protocol.json.sha256").write_bytes(blob(OLD + "protocol.json.sha256"))
    return protocol


def datasets():
    records, reports = [], {}
    for dataset, root in ROOTS.items():
        if not root.is_dir():
            reports[dataset] = {"root": str(root), "located": False}
            continue
        rows = []
        if dataset == "visa":
            split = root / "split_csv/1cls.csv"
            rows = list(csv.DictReader(split.open(newline="", encoding="utf-8")))
            samples = [(r["object"], r["split"], r["label"], r["image"], r["mask"] or None) for r in rows]
            categories = sorted({r[0] for r in samples})
            native = {p.relative_to(root).as_posix() for cat in categories for p in (root/cat/"Data/Images").rglob("*") if p.is_file() and p.suffix.lower() in EXTENSIONS}
            listed = {r[3] for r in samples}
            annotation_mismatch = []
            for cat in categories:
                annotation = list(csv.DictReader((root/cat/"image_anno.csv").open(newline="", encoding="utf-8")))
                a = {r["image"] for r in annotation}
                b = {r[3] for r in samples if r[0] == cat}
                if a != b:
                    annotation_mismatch.append({"category": cat, "annotations_only": sorted(a-b), "split_only": sorted(b-a)})
        else:
            categories = sorted(p.name for p in root.iterdir() if p.is_dir() and (p/"train").is_dir())
            samples = []
            splits = ("train", "test") if dataset == "mvtec_ad" else ("train", "validation", "test_public")
            for cat in categories:
                for split in splits:
                    for p in (root/cat/split).rglob("*"):
                        if not p.is_file() or p.suffix.lower() not in EXTENSIONS or "ground_truth" in p.relative_to(root/cat/split).parts:
                            continue
                        label = "normal" if p.parent.name == "good" else "anomaly"
                        mask = None
                        if label == "anomaly":
                            mask = (root/cat/"ground_truth"/p.parent.name/(p.stem+"_mask.png")) if dataset == "mvtec_ad" else (root/cat/split/"ground_truth"/p.parent.name/(p.stem+"_mask.png"))
                        samples.append((cat, split, label, p.relative_to(root).as_posix(), mask.relative_to(root).as_posix() if mask else None))
            listed = native = {r[3] for r in samples}
            annotation_mismatch = []
        counts = Counter((cat, split, label) for cat, split, label, _, _ in samples)
        missing_images, missing_masks, escapes = [], [], []
        for cat, split, label, image, mask in samples:
            p = root / image
            if not p.is_file(): missing_images.append(image)
            if mask and not (root/mask).is_file(): missing_masks.append(mask)
            if not p.resolve().is_relative_to(root.resolve()): escapes.append(image)
            records.append({"dataset": dataset, "category": cat, "split": split, "label": label,
                            "image_id": dataset + ":" + image, "resolved_path": str(p.resolve()),
                            "native_image": image, "native_mask": mask, "pixels_read": False})
        reports[dataset] = {"root": str(root), "located": True, "categories": categories,
            "total_images": len(samples), "counts": [{"category": c, "split": s, "label": l, "count": n} for (c,s,l),n in sorted(counts.items())],
            "missing_images": missing_images, "missing_masks": missing_masks,
            "listed_not_native": sorted(listed-native), "native_not_listed": sorted(native-listed),
            "duplicate_image_ids": len(samples)-len(listed), "path_escapes": escapes,
            "annotation_mismatch": annotation_mismatch,
            "split_csv_sha256": digest((root/"split_csv/1cls.csv").read_bytes()) if dataset == "visa" else None,
            "scope": "Native filename, split metadata and path existence only; no target pixels, score arrays or masks decoded.",
            "archive_checksum_verified": False, "image_decoding_verified": False, "content_hash_leakage_checked": False,
            "excluded_splits": ["test_private", "test_private_mixed"] if dataset == "mvtec_ad2" else []}
        print(json.dumps({"dataset": dataset, "total_images": len(samples), "categories": len(categories), "missing_images":len(missing_images), "missing_masks":len(missing_masks)}), flush=True)
    save("dataset_inventory.json", reports)
    with (OUT/"native_image_inventory.jsonl").open("w", encoding="utf-8") as f:
        for row in records: f.write(json.dumps(row)+"\n")
    (OUT/"native_image_inventory.jsonl.gz").write_bytes(gzip.compress((OUT/"native_image_inventory.jsonl").read_bytes(), mtime=0))
    with (OUT/"native_counts.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["dataset", "category", "split", "label", "count"])
        writer.writeheader()
        for dataset, report in reports.items():
            writer.writerows({"dataset":dataset, **r} for r in report.get("counts", []))


def main():
    if git("rev-parse", "HEAD").decode().strip() != REFERENCE:
        # A publication commit may follow the audited base; raw source is still pinned.
        git("cat-file", "-e", REFERENCE + "^{commit}")
    protocol = source_snapshot()
    datasets()
    candidates = []
    search_roots = [Path(r"C:\Users\ennay"), Path("D:/")]
    search_roots += [p for p in map(Path, ("C:/tmp", "C:/workspace", "C:/datasets", "C:/checkpoints")) if p.is_dir()]
    search = command("checkpoint_search", ["rg", "--files", "--hidden", "-g", "*dinov2*.pth", "-g", "*vitl14*", "-g", "!**/node_modules/**", "-g", "!**/site-packages/**", "-g", "!**/.git/**", *map(str, search_roots)], timeout=180)
    paths = (OUT/search["stdout"]).read_text(encoding="utf-8", errors="replace").splitlines()
    for name in paths:
        p = Path(name)
        if p.is_file() and p.suffix == ".pth":
            with p.open("rb") as f: h = hashlib.file_digest(f,"sha256").hexdigest()
            candidates.append({"path": str(p), "bytes":p.stat().st_size, "sha256":h, "matches_required":h == EXPECTED_WEIGHT})
    save("checkpoint_check.json", {"required_filename":"dinov2_vitl14_reg4_pretrain.pth", "required_sha256":EXPECTED_WEIGHT,
        "required_bytes":1217607321, "search_roots":list(map(str,search_roots)), "candidates":candidates,
        "verified":any(c["matches_required"] for c in candidates), "no_checkpoint_loaded":True,
        "search_command":search, "limitation":"Unreadable directories are reported in stderr; absence is scoped to accessible searched locations.",
        "no_download_or_substitution":True})
    env = os.environ.copy()
    for name in ("tmp", "runtime", "runtime/mpl"): (OUT/name).mkdir(parents=True, exist_ok=True)
    env.update(TEMP=str(OUT/"tmp"),TMP=str(OUT/"tmp"),TMPDIR=str(OUT/"tmp"),MPLCONFIGDIR=str(OUT/"runtime/mpl"),PYTHONDONTWRITEBYTECODE="1",PYTHONPATH=str(SNAPSHOT)+os.pathsep+str(SNAPSHOT/"framework"),PYTHONIOENCODING="utf-8")
    version_code = "import sys,torch,numpy,PIL,sklearn,scipy,matplotlib,threadpoolctl,json;print(json.dumps({'python':sys.version,'executable':sys.executable,'torch':torch.__version__,'cuda_available':torch.cuda.is_available(),'cuda_runtime':torch.version.cuda,'numpy':numpy.__version__,'pillow':PIL.__version__,'sklearn':sklearn.__version__,'scipy':scipy.__version__,'matplotlib':matplotlib.__version__,'threadpoolctl':threadpoolctl.__version__},indent=2))"
    command("runtime_versions", [str(RUNTIME),"-B","-c",version_code], REPO, env)
    command("gpu", ["nvidia-smi"], REPO, env)
    command("packages", [str(RUNTIME),"-B","-m","pip","freeze"], REPO, env)
    command("source_dependency_check", [str(RUNTIME),"-B","-c","from safe_iad.safal_features import verify_source; print(verify_source(r'C:\\Users\\ennay\\.cache\\torch\\hub\\facebookresearch_dinov2_main'))"], SNAPSHOT, env)
    for suite, label in (("tests","root_tests"),("framework/tests","framework_tests")):
        command(label, [str(RUNTIME),"-B",str(OUT/"run_existing_tests.py"),"--source",str(SNAPSHOT),"--suite",suite,"--output",str(OUT/(label+".json"))], SNAPSHOT, env)
    class Memory(ctypes.Structure):
        _fields_ = [("length",ctypes.c_ulong),("load",ctypes.c_ulong)] + [(n,ctypes.c_ulonglong) for n in ("total_physical","available_physical","total_page","available_page","total_virtual","available_virtual","available_extended")]
    memory = Memory(); memory.length=ctypes.sizeof(memory)
    memory_ok = bool(ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory)))
    with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r"HARDWARE\DESCRIPTION\System\CentralProcessor\0") as key:
        cpu=winreg.QueryValueEx(key,"ProcessorNameString")[0].strip()
    save("environment.json", {"recorded_utc":datetime.now(timezone.utc).isoformat(),"platform":platform.platform(),
        "audit_python":sys.version,"audit_python_executable":sys.executable,"study_runtime_candidate":str(RUNTIME),
        "cpu":cpu,"logical_cpus":os.cpu_count(),"memory_api_success":memory_ok,
        "ram_bytes":memory.total_physical if memory_ok else None,"available_ram_bytes":memory.available_physical if memory_ok else None,
        "disk_bytes":{p:shutil.disk_usage(p)._asdict() for p in ("C:/","D:/")},
        "required_original_versions":{k:protocol["encoder"].get(k) for k in ("python_version","torch_version","numpy_version","pillow_version")},
        "no_inference_run":True})
    from finalize_report import main as finalize
    passed = finalize()
    print("Preflight evidence saved; no model or target inference run.",flush=True)
    raise SystemExit(0 if passed else 2)


if __name__ == "__main__":
    main()
