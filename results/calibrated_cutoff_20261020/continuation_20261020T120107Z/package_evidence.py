"""Package this continuation's complete logs without altering parent evidence."""
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
PARENT = OUT.parent


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    manifest = json.loads((PARENT/"artifact_manifest.sha256.json").read_text())
    bad = [name for name,h in manifest["sha256"].items() if sha((PARENT/name).read_bytes()) != h]
    if bad:
        raise ValueError("Parent audit changed: " + repr(bad))
    records = [json.loads(line) for line in (OUT/"commands.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    compressed = {}
    for path in sorted((OUT/"logs").glob("git_*.stdout.log")):
        if path.stat().st_size <= 65536:
            continue
        data = path.read_bytes()
        relative = path.relative_to(OUT).as_posix()
        packed = relative + ".gz"
        (OUT/packed).write_bytes(gzip.compress(data, mtime=0))
        compressed[relative] = {"path":packed,"uncompressed_bytes":len(data),"uncompressed_sha256":sha(data),"gzip_sha256":sha((OUT/packed).read_bytes())}
    for record in records:
        if record.get("stdout") in compressed:
            original = record["stdout"]
            record["stdout"] = compressed[original]["path"]
            record["stdout_encoding"] = "lossless gzip; decompress to recover the exact executed-command stdout"
            record["stdout_uncompressed_sha256"] = compressed[original]["uncompressed_sha256"]
    (OUT/"commands.jsonl").write_text("".join(json.dumps(r)+"\n" for r in records),encoding="utf-8")
    ignore = (OUT/".gitignore").read_text()
    for name in compressed:
        line = "/" + name
        if line not in ignore.splitlines():
            ignore += line + "\n"
    (OUT/".gitignore").write_text(ignore,encoding="utf-8")
    (OUT/"log_compression.json").write_text(json.dumps(compressed,indent=2)+"\n",encoding="utf-8")
    report = (OUT/"README_results.md").read_text(encoding="utf-8")
    note = """This continuation reran preflight on 20 October 2026; the fresh audit finished
at 20:05 Asia/Shanghai. Earlier audit files were preserved and independently
checked against their 47-file manifest. The expanded checkpoint search still
found no required weight file. All Git subprocess inputs, stdout and stderr are
saved. Large stdout files are stored as lossless gzip, with exact uncompressed
hashes in `log_compression.json` and their paths in `commands.jsonl`.
No runtime/storage estimate for full inference is available because the required
five-image smoke test did not run. No cutoff implementation or benchmark stage
was advanced after the failed prerequisite gate.

"""
    if note not in report:
        report = report.replace("# Calibrated-cutoff study: stopped at preflight\n\n", "# Calibrated-cutoff study: stopped at preflight\n\n" + note)
    (OUT/"README_results.md").write_text(report,encoding="utf-8")
    receipt = {
        "recorded_utc":datetime.now(timezone.utc).isoformat(),"branch":"calibrated-cutoff-20261020",
        "source_base_commit":"05c0fcea1b3289f0daf2f658c56b08c2848b71e9",
        "parent_published_audit_commit":"fca2c04a1f86a459892297eedda12017c93f9973",
        "continuation_commit":"Resolve the commit containing this file from the branch history.",
        "parent_manifest_files_verified":len(manifest["sha256"]),"parent_hash_mismatches":bad,
        "parent_results_modified":False,"study_protocol_freeze_commit":None,"inference_stage_commits":[],
        "scope":"Fresh failed-preflight evidence only; no completed-study verdict."
    }
    (OUT/"commit_records.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"parent_manifest_matches":True,"compressed_logs":len(compressed),"raw_log_bytes_preserved":sum(v["uncompressed_bytes"] for v in compressed.values()),"preflight_passed":False}))


if __name__ == "__main__":
    main()
