"""Summarize only the saved preflight evidence; never synthesize study results."""
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
REPO = OUT.parents[1]


def read(name):
    return json.loads((OUT/name).read_text(encoding="utf-8"))


def save(name, value):
    (OUT/name).write_text(json.dumps(value, indent=2, allow_nan=False)+"\n", encoding="utf-8")


def main():
    env, data, integrity, weights = (read(n) for n in ("environment.json", "dataset_inventory.json", "integrity_check.json", "checkpoint_check.json"))
    root_tests, framework_tests = read("root_tests.json"), read("framework_tests.json")
    commands = [json.loads(line) for line in (OUT/"commands.jsonl").read_text(encoding="utf-8-sig").splitlines() if line.strip()]
    source_commands = [r for r in commands if r["name"] == "source_dependency_check"]
    source_ok = bool(source_commands and source_commands[-1]["returncode"] == 0)
    blockers = []
    if not weights["verified"]: blockers.append("Required DINOv2 ViT-L/14 register checkpoint not located or SHA-256 verified in accessible searched locations.")
    if not source_ok: blockers.append("Available DINOv2 hub source rejected: missing pinned source SHA-256 manifest; configured original Linux source path is unavailable on this host.")
    if not root_tests["successful"]: blockers.append("Existing root unit suite failed on this Windows runtime (one assertion failure and one dataset-path error).")
    if not framework_tests["successful"]: blockers.append("Existing framework suite has errors, including two module-import failures; not all tests could be discovered.")
    if not integrity["all_recorded_hashes_match_git_blobs"]: blockers.append("Frozen repository artifact hashes do not match the recorded Git blobs.")
    tests = {}
    for name, r in (("root",root_tests),("framework",framework_tests)):
        tests[name] = {"discovered_entries":r["discovered"],"run_entries":r["run"],
            "passed":r["run"]-len(r["failures"])-len(r["errors"])-len(r["skipped"]),
            "failures":len(r["failures"]),"errors":len(r["errors"]),"skipped":len(r["skipped"]),
            "failed_import_placeholders":sum(i.startswith("unittest.loader._FailedTest.") for i in r["test_ids"]),
            "successful":r["successful"]}
    summary = {"recorded_utc":datetime.now(timezone.utc).isoformat(),"scope":"preflight audit only",
        "repository":"ennayriomar/newpr","branch":"calibrated-cutoff-20261020","base_commit":integrity["base_commit"],
        "preflight_passed":not blockers,"infrastructure_or_prerequisite_failure":True,"blockers":blockers,
        "frozen_repository_hashes_verified":integrity["all_recorded_hashes_match_git_blobs"],"tests":tests,
        "dataset_counts":{k:v.get("total_images") for k,v in data.items()},
        "dataset_verification_scope":"Native category/split metadata and file existence only. No image decoding, archive verification, or image-content leakage audit.",
        "study_implementation_written":False,"new_cutoff_unit_test_gate_passed":False,
        "real_weights_verified":weights["verified"],"real_dataset_verified":False,
        "smoke_images_run":0,"source_calibration_run":False,"source_rule_selection_run":False,
        "new_protocol_frozen":False,"target_inference_run":False,"target_query_images_scored":0,
        "benchmark_evaluated":False,"operating_point_results":None,"bootstrap_intervals":None,
        "stop_rule_verdict":None,"verdict_reason":"Study incomplete at prerequisite gate; no completed-study verdict is issued.",
        "target_pixels_masks_scores_read":False,
        "supported_statuses":["written"],"supported_status_scope":"Preflight audit and report only; the requested cutoff study was not implemented."}
    save("summary.json",summary)
    save("leakage_check.json",{"passed":None,"executed":False,"reason":"No new source/support calibration plan was created because preflight failed.",
        "native_metadata_path_check":"See dataset_inventory.json", "id_path_content_hash_experimental_role_audit":"not performed",
        "support_reuse_declared":None,"target_query_scores_used_for_selection":False})
    stages=[{"stage":"preflight","completed":True,"passed":not blockers,"evidence":["integrity_check.json","checkpoint_check.json","dataset_inventory.json","root_tests.json","framework_tests.json"]}]
    for name in ("cutoff implementation and unit-test gate","five AD2-normal image smoke test","source calibration, rule selection and protocol-freeze commit","VisA k=1, 12 categories, five draws","VisA k=2, 12 categories, five draws","VisA k=4, 12 categories, five draws","paired category-cluster bootstrap and figures"):
        stages.append({"stage":name,"completed":False,"executed":False,"reason":"Preflight stop"})
    save("stage_completion.json",{"study_complete":False,"stages":stages})
    versions=read("logs/runtime_versions.stdout.log")
    counts=[]
    for dataset,r in data.items():
        c=Counter()
        for x in r["counts"]: c[x["split"]+"/"+x["label"]]+=x["count"]
        counts.append(f"| {dataset} | {len(r['categories'])} | {r['total_images']:,} | "+"; ".join(f"{k}: {v:,}" for k,v in sorted(c.items()))+" |")
    ram=lambda n:f"{n/1024**3:.2f} GiB"
    test_rows="\n".join(f"| {k} | {r['run_entries']} | {r['passed']} | {r['failures']} | {r['errors']} | {r['skipped']} |" for k,r in tests.items())
    report=f"""# Calibrated-cutoff study: stopped at preflight

This is an executed prerequisite audit, not a completed anomaly-detection study.
The required register ViT-L/14 checkpoint was unavailable in the accessible
searched locations, the available encoder source failed provenance verification,
and the existing test gates failed on this Windows runtime. The user's required
preflight stop was applied before any model inference. This is an infrastructure
and prerequisite failure, not evidence of model-reproduction failure or benefit.

Repository: `ennayriomar/newpr`; branch: `calibrated-cutoff-20261020`.
Audited base: `{integrity['base_commit']}` (`controlled-full-image-20261018`).
Every new audit file is under `results/calibrated_cutoff_20261020/`.
No historical result, scoring source, or existing user checkout was changed.
No `AGENTS.md` exists in the audited Git tree. Relevant workflow instructions
were read in `docs/CONTROLLED_EXPERIMENT.md`, README and retained startup notes.

## Model definitions actually inspected

The frozen experiment is an independent experimental SAFAL hybrid, with a frozen
DINOv2 ViT-L/14 encoder and four register tokens. It averages raw zero-based blocks
4–18 without final encoder normalization. Inputs use PIL bilinear square resize
448 and crop 448 (identity crop), ImageNet normalization, a 32×32 patch grid,
and position interpolation antialias=False, offset=0.1. The three scoring slots
are identity, vertical flip and nonnegative clamp. Each support image contributes
six views per slot: identity, 90/180/270-degree rotations, vertical and horizontal
flip; exactly identical tensor inputs are deduplicated for extraction while
retaining the slot/view references.

The baseline sums slot-aligned nearest-normal-patch cosine distances. The hybrid
adds lambda=0.25 times the existing normalized PCA residual in each slot, with a
uniform gate. A single global PCA retains 95% variance; the squared residual is
divided by mean total centered normal-feature energy. The full map is bilinearly
interpolated directly to 448×448. Image scoring averages the largest
`max(1, floor(0.01*N))` map values: 2,007 values for a 448×448 map. There is no
gradient training, optimizer or epoch loop.

The original experiment has k=1 and seeds 17/29/43, not the requested five-draw
k=1/2/4 study. Its source image cutoffs are baseline **1.9804482460021973** and
hybrid **2.343151807785034**, each from 160 AD2 calibration normals with strict
`score > cutoff`. These are inspected historical calibration constants, not new
measurements. No k=2 or k=4 budget-specific cutoff exists in that frozen protocol;
none was invented or assigned here. The root README describes an older preset,
so the controlled protocol and frozen code were used as the authority.

## Integrity and missing assets

All nine recorded scoring/source-file hashes match their exact Git blob bytes.
The original protocol SHA-256 is
`dc078b5a681b8a44015dc02a227afb4b20f248e7ca70ac8e31a95f321aa2f408`.
Protocol, configuration, source-plan, source-selection and calibration-ID hashes
all match their recorded values. See [integrity_check.json](integrity_check.json)
and [the copied original protocol](provenance/original_protocol.json.gz) (gzip).

Git initially converted this new Windows checkout to CRLF, which changes byte
hashes. Checks therefore used exact Git objects, and existing tests ran from an
unchanged byte-exact source export inside this new results directory. Its manifest
is [reference_source_manifest.json](reference_source_manifest.json); the temporary
source export is ignored by Git and can be recreated by the audit script.

Required checkpoint: `dinov2_vitl14_reg4_pretrain.pth`, 1,217,607,321 bytes,
SHA-256 `{weights['required_sha256']}`.
The search found only DINOv2 small and base PTH files; neither hash matches.
No checkpoint was loaded, downloaded or substituted. The search covers the
accessible Downloads, Documents/Codex, .cache and D: trees. `D:\\System Volume
Information` was inaccessible, so the absence claim is scoped, not a whole-device
proof. Full search output and candidate hashes are in
[checkpoint_check.json](checkpoint_check.json) and `logs/checkpoint_search.*.log`.

The available Torch hub DINOv2 source has no trusted pinned SHA-256 manifest and
was rejected by the unchanged `verify_source` function. The original Linux path
is unavailable. The repository also retains a historical vendor bundle, but that
was not restored or validated as an inference dependency after this stop.
See `logs/source_dependency_check.stderr.log`.

## Actual environment

- Windows build 26200; {env['cpu']}; {env['logical_cpus']} logical CPUs.
- RAM: {ram(env['ram_bytes'])} total; {ram(env['available_ram_bytes'])} available at the recorded audit snapshot.
- Free disk: C: {ram(env['disk_bytes']['C:/']['free'])}; D: {ram(env['disk_bytes']['D:/']['free'])}.
- GPU: NVIDIA GeForce RTX 3060 Laptop GPU, 6,144 MiB VRAM; CUDA available to Torch.
- Existing test runtime: Python 3.11.0, Torch {versions['torch']}, NumPy {versions['numpy']},
  Pillow {versions['pillow']}, scikit-learn {versions['sklearn']}, SciPy {versions['scipy']}.
- Original protocol runtime: Python 3.12.14, Torch 2.7.1+cpu, NumPy 2.2.6, Pillow 12.3.0.

This is not the original numerical runtime. Version/package, GPU, CPU, RAM and
disk evidence are saved in [environment.json](environment.json),
`logs/runtime_versions.stdout.log`, `logs/packages.stdout.log` and `logs/gpu.stdout.log`.
The default system Python lacks Torch; a pre-existing environment was used only
for the existing test audit. No existing environment was modified.

## Native data inventories

| Dataset | Categories | Images | Native split/label counts |
|---|---:|---:|---|
{chr(10).join(counts)}

Per-category counts are in [native_counts.csv](native_counts.csv); exact native
IDs, resolved paths and declared masks are in
[native_image_inventory.jsonl.gz](native_image_inventory.jsonl.gz) (gzip).
The VisA official `split_csv/1cls.csv` and per-category annotations agree with
the native image filenames. Its test cohort contains 2,162 images. AD2 private
and private-mixed folders were excluded from this public-source inventory.
No referenced image or mask path was missing and no duplicate native ID or
path escape was found. This is filename/split metadata and existence checking,
not archive authentication, image decoding, or experimental-role content-hash
verification. Target pixels, masks and score arrays were not opened.
The **real-dataset verified** status is consequently not assigned.

## Existing tests actually executed

| Suite | Entries run | Passed | Failures | Errors | Skipped |
|---|---:|---:|---:|---:|---:|
{test_rows}

The framework count includes two `_FailedTest` import placeholders, so it is
not a claim that every test in those two modules was discovered or executed.
The root failures concern Windows path separators in native VisA discovery
and a Linux absolute-path expectation. Framework errors include unavailable
`fcntl` and `tifffile`, symlink privilege, hardcoded `/tmp` paths, an absent
acquisition report, cp1252 Unicode encoding, and Python 3.11.0's unsupported
`tarfile.extractall(filter=...)` argument. Full tracebacks are preserved, without
patching or skipping the frozen tests. These are test/environment results,
not benchmark or model-performance measurements.

Machine-readable IDs/outcomes: [root_tests.json](root_tests.json) and
[framework_tests.json](framework_tests.json). Full output:
[root stdout](logs/root_tests.stdout.log), [root stderr](logs/root_tests.stderr.log),
[framework stdout](logs/framework_tests.stdout.log),
[framework stderr](logs/framework_tests.stderr.log).
Small arrays and fixture images created by these existing unit tests were used
only for unit tests, never as benchmark substitutes.

## Study status, operating point and verdict

No new cutoff rule, multi-shot study driver or new unit-test gate was implemented
after the failed prerequisites. The five-image AD2 smoke test, source calibration,
source-only rule selection and all three VisA stages are unrun. No new support
draws or calibration assignments were frozen. No experimental ID/path/content-hash
leakage audit passed; [leakage_check.json](leakage_check.json) explicitly records
that it was not executed. No normalized statistics, leave-one-out cutoffs,
query-feature cache, oracle, maps or qualitative figures were fabricated.

There are **no new operating-point results or uncertainty intervals**. Recall,
false-alarm rate, balanced accuracy, AUROC differences and bootstrap intervals
are unavailable. No numerical success criteria or selected rule were frozen,
and no new `protocol.json`/freeze commit is represented as complete. The copied
historical protocol is provenance only. The final stop-rule verdict is
**not issued because the comparison is incomplete**.

The requested `per_image.jsonl`, `per_draw.csv`, `per_category.csv`, new source
selection/calibration records, paired bootstrap arrays, prediction maps and
figure metadata do not exist because their producing stages did not run.
See [summary.json](summary.json) and [stage_completion.json](stage_completion.json).

## Reproduction and publication

Run `python -B results/calibrated_cutoff_20261020/preflight.py` from the repository
using the recorded local roots/runtime, or adapt those paths in a fresh audit
directory. It reconstructs source from the fixed base commit, audits metadata,
searches checkpoint candidates and executes existing tests. It performs no model
inference. Every audit subprocess has an argument vector, working directory,
timing, exit code and separate complete stdout/stderr in
[commands.jsonl](commands.jsonl) and `logs/`. The first source-export attempt was
interrupted before inventory/tests; its empty logs and interruption record are
retained. Audit-process exit zero in the original log means evidence collection
finished, not that prerequisites passed. `summary.json:preflight_passed=false`
is the gate; the finalized script exits 2 on failed prerequisites.

Before resuming the requested study, supply the exact checkpoint, a verified
pinned encoder source and a compatible passing runtime. Then implement and test
the full cutoff-only study, perform the smoke/source stages, and freeze and
commit all selection definitions, success criteria and role/content hashes
before any target inference. This audit makes no completed-study verdict.

The audit is published on the requested new branch. Publication evidence is
recorded separately in [commit_records.json](commit_records.json); only the
audited new results directory may be changed by those commits.

| Status | Supported by this audit |
|---|---|
| written | Preflight scripts, evidence and report only |
| unit-tested | No passing study gate; existing suites failed |
| smoke-tested | No |
| real-weights verified | No |
| real-dataset verified | No; native metadata inventory only |
| benchmark evaluated | No |
"""
    (OUT/"README_results.md").write_text(report,encoding="utf-8")
    print(json.dumps({"preflight_passed":not blockers,"blockers":blockers,"tests":tests,"report":"README_results.md"}),flush=True)
    return not blockers


if __name__ == "__main__":
    raise SystemExit(0 if main() else 2)
