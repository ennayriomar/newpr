"""Check every real pipeline artifact; never substitute tests for performance."""
import argparse
from collections import Counter
import json
from pathlib import Path

import numpy as np
import tifffile

from safe_iad.official_ad2 import official_checker, validate_complete_submission
from safe_iad.run_pipeline import immutable_json, validate_artifact_ledger


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--run',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    complete=json.loads((a.run/'completion.json').read_text()); config=json.loads((a.run/'config.json').read_text())
    manifest=json.loads((a.run/'split_manifest.json').read_text()); calibration_ids=set(); evaluation_ids=set()
    for e in manifest['episodes']:
        ids={f"{e['dataset']}:{q['image']}" for q in e['queries']}
        (calibration_ids if e['role']=='calibration' else evaluation_ids).update(ids)
    if calibration_ids & evaluation_ids:
        raise ValueError('Calibration query overlaps evaluation.')
    rows=0; maps=0; exports=0; roles=Counter(); native_pixels=0; actions=Counter(); example_export=None
    for table in sorted((a.run/'episodes').rglob('predictions.jsonl')):
        records=[json.loads(x) for x in table.read_text().splitlines()]
        for r in records:
            rows+=1; roles[r['role']]+=1
            if len(r['support_ids'])!=r['shots'] or len(set(r['support_ids']))!=r['shots'] or r['image_id'] in r['support_ids']:
                raise ValueError('Support budget/overlap error.')
            if r['candidate_pool_ids'] or r['selected_reference_ids'] or r['acquisition_budget']:
                raise ValueError('Strict-shot evaluation has an undeclared reference pool.')
            w,h=r['original_size']
            with np.load(r['map'],allow_pickle=False) as saved:
                values={k:saved[k].copy() for k in saved.files}
            if any(v.shape!=(h,w) or v.dtype!=np.dtype(r['map_storage_dtype']) or not np.isfinite(v).all() for v in values.values()):
                raise ValueError('Native map shape/dtype/finite error.')
            maps+=len(values); native_pixels+=h*w
            if r['method']=='support_hybrid':
                if ((values['adequacy']<0)|(values['adequacy']>1)).any():
                    raise ValueError('Adequacy not bounded.')
                if (values['defect']<values['local']).any():
                    raise ValueError('Local defect evidence was suppressed.')
            if r['role']!='calibration':
                cut=a.run/'episodes'/'calibration'/r['dataset']/config['calibration_categories'][r['dataset']]/f"seed-{config['calibration_seed']}_k-{r['shots']}"/r['method']/'thresholds.json'
                cut=json.loads(cut.read_text())
                if cut['final_labels_used'] or not set(cut['calibration_ids']).issubset(calibration_ids):
                    raise ValueError('Invalid calibration origin.')
                if cut.get('native_test_defect_labels_used') is not False or not set(cut['calibration_native_splits']).issubset({'train','validation'}):
                    raise ValueError('Strict calibration must exclude native-test labels.')
                evidence=r['image_score']>=cut['image_threshold']
                if evidence!=r['raw_defect_evidence_flag']:
                    raise ValueError('Evidence flag changed independently of detector score.')
                expected='unresolved/reference-insufficient' if r['method']=='support_hybrid' and r['mean_support_adequacy']<cut['adequacy_threshold'] else 'defective' if evidence else 'normal'
                if r['action']!=expected:
                    raise ValueError('Classification does not follow locked thresholds.')
                actions[r['action']]+=1
            if 'official_format_export' in r:
                ex=r['official_format_export']; checker=official_checker()
                checker._check_ad_images(Path(ex['path'])); checker._check_thresholded_ad_images(Path(ex['thresholded_path']))
                if not np.array_equal(tifffile.imread(ex['path']),values['defect'].astype('float16')):
                    raise ValueError('Export differs from recorded defect evidence.')
                exports+=1; example_export=Path(ex['path']).parents[4]
    artifacts=validate_artifact_ledger(a.run)
    reports={d:json.loads((a.run/'verification'/d/'verification.json').read_text()) for d in config['roots']}
    if any(r['status']!='passed' for r in reports.values()):
        raise ValueError('Dataset verification failed.')
    # The local preview must fail the full private-server checker. This is an
    # expected completeness rejection, never a fabricated valid submission.
    private_status='not_run'
    export_dirs=sorted((a.run/'episodes').rglob('ad2_local_export'))
    if export_dirs:
        try:
            validate_complete_submission(export_dirs[0])
        except Exception as e:
            if type(e).__name__!='SubmissionException':
                raise
            private_status='correctly_rejected_incomplete_public_preview: '+str(e).splitlines()[0]
        else:
            raise ValueError('Public preview unexpectedly passed private submission completeness.')
    result=dict(status='passed',verified_real_images=sum(r['total_images'] for r in reports.values()),
                evaluation_prediction_records=complete['prediction_records'],all_prediction_records_including_calibration=rows,
                unique_evaluation_queries=len(evaluation_ids),unique_calibration_queries=len(calibration_ids),
                stored_native_maps=maps,official_real_public_exports=exports,artifact_hashes_checked=artifacts,
                prediction_roles=dict(roles),actions_across_all_methods=dict(actions),
                calibration_evaluation_overlap=0,strict_shots_and_zero_pools_checked=True,
                all_native_map_shapes_dtypes_finite=True,hybrid_adequacy_bounded_and_local_evidence_preserved=True,
                all_decisions_use_locked_calibration_cutoffs=True,official_export_file_checks='passed',
                native_test_defect_labels_used_for_calibration=False,
                private_submission_completeness=private_status,
                map_storage='explicit float16; pilot metric computation used float32 native scores',
                production_ready=False,full_paper_reproductions_validated=False)
    immutable_json(a.output,result); print(json.dumps(result,indent=2))


if __name__=='__main__': main()
