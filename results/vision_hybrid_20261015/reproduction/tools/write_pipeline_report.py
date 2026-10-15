"""Write an audit/report from completed real measurements only."""
import argparse
import json
from pathlib import Path
import numpy as np


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--run',type=Path,required=True); p.add_argument('--validation',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    completion=json.loads((a.run/'completion.json').read_text()); check=json.loads(a.validation.read_text()); results=json.loads((a.run/'metrics.json').read_text())
    if completion['status']!='completed_declared_scope' or check['status']!='passed': raise ValueError('A completed validated run is required.')
    categories=list(dict.fromkeys((r['dataset'],r['category'],r['role']) for r in results))
    table=['| Dataset/category (role) | Method | Image AUROC k1 / k4 | Pixel AP k1 / k4 | Hybrid coverage k1 / k4 |','|---|---|---:|---:|---:|']
    for d,c,role in categories:
        for method in ['transparent_nn','anomalydino','subspacead','support_hybrid']:
            selected=[r for r in results if r['dataset']==d and r['category']==c and r['method']==method]
            def means(level,key):
                vals=[np.mean([r[level][key] for r in selected if r['shots']==k]) for k in [1,4]]
                return ' / '.join(format(v,'.4g' if key=='ap' else '.4f') for v in vals)
            coverage=' / '.join(f"{np.mean([r['selective_decision']['coverage'] for r in selected if r['shots']==k]):.1%}" for k in [1,4]) if method=='support_hybrid' else '—'
            table.append(f'| {d}/{c} ({role}) | {method} | {means("image","auroc")} | {means("pixel","ap")} | {coverage} |')
    hy=[r for r in results if r['method']=='support_hybrid']
    accepted=sum(r['selective_decision']['accepted'] for r in hy); correct=sum(r['selective_decision']['correct_accepted'] for r in hy); total=sum(r['queries'] for r in hy)
    stress=[r for r in hy if r['role']=='stress_final_public']
    stress_accepted=sum(r['selective_decision']['accepted'] for r in stress); stress_correct=sum(r['selective_decision']['correct_accepted'] for r in stress)
    bottle4=[r for r in hy if r['category']=='bottle' and r['shots']==4]
    bottle4_accepted=sum(r['selective_decision']['accepted'] for r in bottle4); bottle4_total=sum(r['queries'] for r in bottle4)
    native_maps_same=0; native_maps_total=0; pixels_global_envelope=0; total_pixels=0
    for metrics_file in (a.run/'episodes').rglob('support_hybrid/metrics.json'):
        for row in map(json.loads,(metrics_file.parent/'predictions.jsonl').read_text().splitlines()):
            with np.load(row['map'],allow_pickle=False) as z:
                native_maps_same+=int(np.array_equal(z['defect'],z['local'])); native_maps_total+=1
                pixels_global_envelope+=int((z['defect']>z['local']).sum()); total_pixels+=z['defect'].size
    text=f'''# Verified real-data framework run

The requested central runner and empirical hybrid are implemented and the declared strict pilot completed. This is tested research software, not validated production inspection or a reproduction of the papers' headline tables.

## What executed

- Physical verification of all {check['verified_real_images']:,} retained real images: MVTec AD 5,354; VisA 10,821; AD 2 public/train/validation 3,914. Masks, native dimensions and split content checked.
- Three baseline variants finished before hybrid evaluation: transparent multilayer NN; the official supported AnomalyDINO force_no_mask_no_rotation scoring variant; the official SubspaceAD linear PCA/reconstruction core with the declared common-backbone adapter.
- Frozen official pretrained DINOv2 ViT-B/14, pinned source/checkpoint, actual intermediate tokens; no random-weight substitution. Blocks 2/5/8/11, long-edge 224 aspect-preserving padding for the hybrid/NN. Exact geometry is in each prediction; baseline transforms follow their declared variants.
- k=1,2,4, three seeded nested training-normal support draws, strict support budgets, empty candidate registries and no acquisition. Five categories, four fixed stratified queries/category: {check['unique_evaluation_queries']} unique evaluation queries, {completion['evaluation_episodes']} query-group/method/support episodes, {completion['prediction_records']} evaluation prediction records. There are {check['unique_calibration_queries']} separate calibration queries and {check['all_prediction_records_including_calibration']-completion['prediction_records']} calibration prediction records. Reused queries/support draws are correlated.
- Main cutoffs use held-out normal training queries from reserved capsule/fryum categories, explicitly excluded from the calibration support banks. AD 2 cutoffs use reserved normal-only can validation images. All use mean+3std; four additional calibration normals per dataset are declared. No native-test defect labels are used for any default cutoffs or weights. Adequacy threshold 0.5 is predeclared; no target-label tuning. No probabilities fitted.
- Native float32 AUROC/AP/F1 metrics and offline F1-Max tables. Saved native maps use explicit float16 compression; scores are evaluated before compression. Test F1-Max is diagnostic and its maximizing cutoff never enters decisions.
- {check['official_real_public_exports']} actual AD 2 public TIFF/PNG pairs, each checked with the official dtype/binary code; TIFF values match saved defect evidence. The official full-submission check correctly rejects this incomplete public preview. No private images, predictions, server scores or upload are claimed.
- All 44 unit/contract tests passed, including explicit rejection of native-test defect labels in calibration. Every recorded decision, support budget, calibration origin, finite native map, adequacy bound and local evidence envelope passed real-output audit. {check['artifact_hashes_checked']} immutable artifact hashes checked.

## Method

Full definitions and source fidelity are in /workspace/tools/README.md. PCA retains 99% observed support variance. Positive-spectrum Shannon entropy is normalized by log(rank) and scaled by excess query density distance relative to a support 95th-percentile density bound. This is an empirical diagnostic in [0,1], not an adequacy probability or independent-reference sample-size estimate.

The evidence envelope is max(local L2 NN, global PCA orthogonal residual, nearest-token orthogonal residual). It preserves local evidence. Low mean adequacy triggers unresolved/reference-insufficient while retaining that raw evidence and its flag. This separation of outputs does not mathematically identify actual defects versus missing legitimate normal modes.

## Actual results

Values below are mean over the same queries across three support draws. They are feasibility measurements, not full-benchmark estimates or statistical population confidence intervals. All k2 values, native pixel AUROC, image/pixel AP, offline F1-Max and F1 at locked calibration cutoffs are retained in metrics.csv/json.

'''+ '\n'.join(table)+f'''

Hybrid accepted {accepted}/{total} query/support/shot inspections ({accepted/total:.1%}); {correct}/{accepted} accepted decisions were correct ({correct/accepted if accepted else float('nan'):.1%}). These counts reuse only {check['unique_evaluation_queries']} unique evaluation images and should not be interpreted as independent trials. They do not establish a reliability guarantee or a deployment false-alarm rate.

At the fixed adequacy cutoff, the hybrid accepted all {stress_accepted} AD 2 can inspections while only {stress_correct}/{stress_accepted} image decisions were correct. High diagnostic adequacy did not indicate correct inspection on this slice. It accepted {bottle4_accepted}/{bottle4_total} bottle inspections at k=4 despite mean image AUROC {np.mean([r['image']['auroc'] for r in bottle4]):.4f}. The proposed entropy/density rule therefore does not support reliable three-way classification in this pilot. This is not evidence of ground-truth support insufficiency: that event has not been annotated.

The saved hybrid envelope equals the saved local map exactly for {native_maps_same}/{native_maps_total} evaluation records; {pixels_global_envelope/total_pixels:.4%} of stored native pixels exceed local evidence. This comparison is at the explicitly stored float16 precision. A nearly unchanged envelope is a negative ablation finding; abstention is separate from raw localization.

The AD 2 stress slice and weak/variable capsule localization are material limitations. Coarse 224 inputs can lose very small defects. Calibration uses only tiny category-disjoint pilot samples, and transferred cutoffs can fail even when ranking AUROC is high. Review the plotted locked-cutoff F1 and coverage, rather than treating AUROC alone as inspection reliability. Unresolved cases are not automatically correct or safe.

The adequacy precision curves explicitly use the event "image decision correct at the locked detector cutoff". This is a correctness/coverage proxy, not ground-truth support adequacy. Future intervention validation must justify an adequacy event using declared validation/source data. No learned benefit predictor is fitted; the earlier source-only M2 targets and oracle separation remain available as separate tools.

## Reproduction and remaining scope

```bash
bash /workspace/tools/install_runtime.sh
cd /workspace/tools
/workspace/venvs/safe_iad/bin/python -m safe_iad.run_pipeline --config configs/experiment_plan.yaml --reproduce true
/workspace/venvs/safe_iad/bin/python /workspace/tools/validate_pipeline_run.py --run {a.run} --output /workspace/reports/hybrid_pipeline_validation.json
/workspace/venvs/safe_iad/bin/python /workspace/tools/plot_pipeline.py --run {a.run} --output /workspace/reports/hybrid_pipeline_summary.png
```

Repeated completed invocation re-verifies datasets, checks the immutable ledger and independently recomputes one actual query per method with feature cache bypass. This is not a new full rerun of all episodes; use --output with a new directory for that. The interrupted preprocessing audit attempt was preserved at /workspace/reports/hybrid_pipeline_preprocessing_audit_attempt; scientific settings were unchanged when preprocessing version provenance was completed. Interrupted-job recovery has not been fully validated.

The initial /workspace/reports/hybrid_pipeline run used category-disjoint native-test labels for cutoffs. It was retained as an exploratory variant and superseded by this strict calibration run to honor the latest literal native-test-label restriction. Its source implementation is preserved at /workspace/reports/hybrid_pipeline_implementation_snapshot. Scoring settings, support/query draws and maps were not tuned using its evaluation outcomes. Only the calibration protocol was corrected.

The full plan declares 2,871 queries over 20 reserved validation/final/public categories, excluding source/calibration categories. It has not been executed. Native float16 diagnostic maps alone project to about 1,067 GB before compression, excluding calibration, feature caches and public TIFFs; this 32 GB volume lacks suitable storage. The full plan uses bounded-memory float16 histogram pixel metrics explicitly exact for quantized scores, not original float32 scores, and has a disk preflight guard.

Faithful scoring-core parity tests do not establish published-table reproduction. AnomalyDINO's default ViT-S/14 448 agnostic preprocessing and SubspaceAD's published ViT-G/registers 672/30-augmentation recipe are distinct, unrun configurations. Full AD 2 lighting/private scenarios are unrun. These data/results do not justify novelty, state-of-the-art, production readiness or acceptance claims.

Tools remain standalone under /workspace/tools because the selected ennayriomar/ennayriomar checkout is a profile README. Its source was preserved. Research repository integration is still awaiting the repository identity.

Artifacts: immutable metrics.csv/json; split_manifest.json with all sampled support/query IDs, prior roles and byte fingerprints; runtime_versions.json; source_provenance.json; backbone.json; per-episode model/threshold/prediction/maps files; artifact_ledger.json; external real-output validation and plot files. Current environment startup/install instructions are saved separately as a draft for review/publishing.
'''
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(text)
    print(str(a.output))


if __name__=='__main__': main()
