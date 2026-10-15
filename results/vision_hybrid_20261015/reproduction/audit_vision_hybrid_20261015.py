"""Read-only numerical/artifact audit; pre mode never loads verification masks."""
from pathlib import Path
import argparse
import hashlib
import json
import sys

import numpy as np
from PIL import Image
from sklearn.metrics import average_precision_score,roc_auc_score
import torch

sys.path.insert(0,'/workspace/tools')
from safe_iad.vision_hybrid_cli import (read_json,validate_plan,validate_selection,check_hashes,
    group_cases,case_mask,load_raw,select_candidate,paired_auc_interval)
from safe_iad.vision_hybrid_model import HybridParameters,VisionHybrid,fuse_raw,parameter_grid,array_hash,source_hashes
from safe_iad.vision_hybrid_features import SLOTS,roi_mask
from safe_iad.safal_cli import inventory
from safe_iad.experiment_io import sha256,read_jsonl,write_json
from safe_iad.research_metrics import thresholded_detection_metrics,localization_metrics


def equal(a,b,atol=1e-11):
    if a is None or b is None:
        assert a is None and b is None
    else:assert np.isclose(a,b,rtol=0,atol=atol),(a,b)


def audit_pre(config_path,run):
    run=Path(run);plan=validate_plan(config_path,run);lock=validate_selection(config_path,run)
    config=plan['config'];manifest=read_json(run/'manifest.json')
    torch.set_num_threads(config['encoder']['threads'])
    development=manifest['development'];verification=manifest['verification']
    assert {(e['dataset'],e['category']) for e in development}.isdisjoint({(e['dataset'],e['category']) for e in verification})
    test_ids={e['dataset']+':'+i for e in verification for i in e['query_ids']}
    assert len(test_ids)==100 and test_ids.isdisjoint(manifest['known_exposure_ids'])
    assert len(manifest['known_exposure_ids'])>=310
    assert all(len(e['support_ids'])==1 and e['calibration_ids']==[] for e in development+verification)
    cases=read_json(run/'development_cases.json');grid=parameter_grid();records=read_json(run/'development_grid.json')
    assert len(grid)==len(records)==25 and len(cases)==200
    with np.load(run/'development_scores.npz',allow_pickle=False) as saved:
        scores=saved['scores'].copy();ids=saved['ids'].tolist()
    assert ids==[p.id for p in grid] and scores.shape==(25,200)
    inventories={d:inventory(config,d) for d in config['roots']}
    aucs=[[] for _ in grid];aps=[[] for _ in grid];pixel_aps=[[] for _ in grid];normal_pixels=[]
    for key,indices in sorted(group_cases(cases).items()):
        print('AUDIT DEVELOPMENT',key,flush=True)
        raws=[load_raw(cases[i]['raw_file']) for i in indices]
        truth=np.concatenate([case_mask(config,inventories,cases[i]).flatten() for i in indices])
        labels=[cases[i]['label'] for i in indices]
        for j,p in enumerate(grid):
            predictions=[fuse_raw(raw,p,config['encoder']['crop']//14) for raw in raws]
            actual=np.array([v['image_score'] for v in predictions]);np.testing.assert_array_equal(actual,scores[j,indices])
            aucs[j].append(float(roc_auc_score(labels,actual)));aps[j].append(float(average_precision_score(labels,actual)))
            pixel_aps[j].append(float(average_precision_score(truth,np.concatenate([v['map'].flatten() for v in predictions]))))
            if j==0:normal_pixels.extend(v['map'].flatten() for i,v in zip(indices,predictions) if not cases[i]['label'])
    for j,row in enumerate(records):
        assert row['id']==grid[j].id and row['params']==grid[j].__dict__
        equal(row['mean_image_auroc'],np.mean(aucs[j]));equal(row['mean_image_ap'],np.mean(aps[j]));equal(row['mean_pixel_ap'],np.mean(pixel_aps[j]))
        assert row['pixel_ap_guard_passed']==(row['mean_pixel_ap']+1e-12>=records[0]['mean_pixel_ap'])
    assert select_candidate(records)==lock['decision']['winner']
    equal(lock['decision']['image_threshold'],np.quantile(scores[0,[not c['label'] for c in cases]],.95,method='linear'))
    equal(lock['decision']['pixel_threshold'],np.quantile(np.concatenate(normal_pixels),.995,method='linear'))
    params=HybridParameters(**lock['decision']['params']);models_checked=0;probe_replays=0
    for path in sorted((run/'development').glob('*/*/model.json')):
        doc=read_json(path);episode=doc['provenance']['episode']
        assert doc['params']==params.__dict__ and doc['parameters_id']==params.id
        assert doc['source_hashes']==source_hashes() and sha256(path.with_suffix('.npz'))==doc['npz_sha256']
        assert doc['provenance']['encoder']==plan['encoder']
        assert episode['support_ids']==doc['support_ids'] and episode['calibration_ids']==[]
        assert doc['model_metadata']['extra_target_calibration_images']==0
        assert doc['model_metadata']['original_support_images']==1
        model=VisionHybrid.load(path.with_suffix(''));models_checked+=1
        probe=path.parent.parent/'query_probe.npz'
        with np.load(probe,allow_pickle=False) as data:
            query={s:torch.from_numpy(data[s].copy()) for s in SLOTS};identifier=str(data['query_id'].item())
        c=next(c for c in cases if c['episode_id']==episode['id'] and c['query_id']==identifier)
        assert c['query_feature_hashes']=={s:array_hash(query[s].numpy()) for s in SLOTS}
        actual=model.raw(query);expected=load_raw(c['raw_file'])
        for slot in SLOTS:
            np.testing.assert_allclose(actual['search'][slot],expected['search'][slot],rtol=0,atol=1e-7)
            for k in ['1','4']:
                for v in ['0.95','0.99']:
                    np.testing.assert_allclose(actual['residual'][k][v][slot],expected['residual'][k][v][slot],rtol=0,atol=1e-10)
        probe_replays+=1
    assert models_checked==probe_replays==10
    result=dict(status='passed',mode='pre-verification',selection_lock_sha256=sha256(run/'selection.lock.json'),
                development_cases_checked=200,grid_cells_recomputed=25,serialized_models_checked=models_checked,
                feature_probe_replays=probe_replays,strict_original_target_normal_budget=1,extra_target_calibration_images=0,
                different_verification_categories=True,verification_unique_ids=100,known_exposure_overlap=0,
                verification_masks_loaded=False,verification_inference_performed=False,
                winner=lock['decision']['winner'],normal_source_cutoffs_recomputed=True,
                input_hashes_checked=len(plan['input_sha256']))
    write_json(run/'development_audit.json',result)
    return result


def audit_complete(config_path,run):
    run=Path(run);plan=validate_plan(config_path,run);lock=validate_selection(config_path,run)
    pre=read_json(run/'development_audit.json');assert pre['status']=='passed' and pre['selection_lock_sha256']==sha256(run/'selection.lock.json')
    complete=read_json(run/'evaluation_completion.json');check_hashes(complete['artifact_sha256']);check_hashes(complete['mask_sha256'])
    assert complete['selection_lock_sha256']==sha256(run/'selection.lock.json')
    rows=read_jsonl(run/'verification_predictions.jsonl');measurements=read_json(run/'verification_metrics.json');summary=read_json(run/'summary.json')
    manifest=read_json(run/'manifest.json');config=plan['config'];inventories={d:inventory(config,d) for d in config['roots']}
    params=HybridParameters(**lock['decision']['params']);threshold=lock['decision']['image_threshold'];pixel_threshold=lock['decision']['pixel_threshold']
    cases={};seen=set();transitions={'detected_to_missed':[],'missed_to_detected':[],'false_positives_added':[],'false_positives_removed':[]}
    for row in rows:
        key=(row['dataset'],row['category'],row['seed'],row['query_id']);identity=key+(row['method'],)
        assert identity not in seen;seen.add(identity);cases.setdefault(key,{})[row['method']]=row
        assert row['threshold']==threshold and row['selection_lock_sha256']==sha256(run/'selection.lock.json')
        assert row['decision']==(row['score']>=threshold) and row['correct']==(row['decision']==row['label'])
        assert row['probabilities'] is False and row['extra_target_calibration_images']==0 and row['original_support_images']==1
        _,lookup=inventories[row['dataset']];sample=lookup[row['query_id']]
        assert row['label']==int(sample.label!='normal') and sample.category==row['category'] and sample.split=='test'
    assert len(rows)==400 and len(cases)==200 and all(set(v)=={'baseline','hybrid'} for v in cases.values())
    raw_replays=0;map_files=0;models=0;probe_replays=0;computed=[]
    for episode in manifest['verification']:
        directory=run/'verification'/(episode['dataset']+'-'+episode['category'])
        bank=directory/episode['id'];model=VisionHybrid.load(bank/'model');models+=1
        assert model.params==params and model.threshold==threshold and model.pixel_threshold==pixel_threshold
        assert model.support_ids==tuple(episode['support_ids']) and len(model.support_ids)==1
        with np.load(directory/'query_probe.npz',allow_pickle=False) as probe:
            query={s:torch.from_numpy(probe[s].copy()) for s in SLOTS};identifier=str(probe['query_id'].item())
        expected_cases=read_json(bank/'cases.json');first=next(c for c in expected_cases if c['query_id']==identifier)
        actual_raw=model.raw(query);saved_raw=load_raw(first['raw_file'])
        for slot in SLOTS:
            np.testing.assert_allclose(actual_raw['search'][slot],saved_raw['search'][slot],rtol=0,atol=1e-7)
            for k in ['1','4']:
                for v in ['0.95','0.99']:
                    np.testing.assert_allclose(actual_raw['residual'][k][v][slot],saved_raw['residual'][k][v][slot],rtol=0,atol=1e-10)
        probe_replays+=1;truths=[];scores={'baseline':[],'hybrid':[]};maps={m:[] for m in scores};labels=[]
        for i,c in enumerate(expected_cases):
            key=(c['dataset'],c['category'],c['seed'],c['query_id']);assert set(cases[key])==set(scores)
            raw=load_raw(c['raw_file']);predictions={'baseline':fuse_raw(raw,HybridParameters(),28),'hybrid':fuse_raw(raw,params,28)}
            truth=case_mask(config,inventories,c)
            with np.load(bank/'maps'/f'query-{i:03d}.npz',allow_pickle=False) as saved:
                assert set(saved.files)=={'truth','baseline','hybrid'}
                np.testing.assert_array_equal(saved['truth'],truth.astype(np.uint8))
                for method in scores:
                    assert saved[method].dtype==np.float32 and saved[method].shape==(256,256) and np.isfinite(saved[method]).all()
                    np.testing.assert_array_equal(saved[method],predictions[method]['map'])
                    equal(cases[key][method]['score'],predictions[method]['image_score'],atol=0)
                    maps[method].append(saved[method].copy());scores[method].append(cases[key][method]['score'])
                assert (saved['hybrid']>=saved['baseline']).all()
            assert predictions['hybrid']['image_score']>=predictions['baseline']['image_score']
            b,h=cases[key]['baseline'],cases[key]['hybrid'];name=':'.join(map(str,key))
            if b['label']:
                if b['decision'] and not h['decision']:transitions['detected_to_missed'].append(name)
                if not b['decision'] and h['decision']:transitions['missed_to_detected'].append(name)
            else:
                if not b['decision'] and h['decision']:transitions['false_positives_added'].append(name)
                if b['decision'] and not h['decision']:transitions['false_positives_removed'].append(name)
            truths.append(truth);labels.append(c['label']);raw_replays+=1;map_files+=1
        for method in scores:
            detection=thresholded_detection_metrics(labels,scores[method],threshold)
            localization=localization_metrics(truths,maps[method],pixel_threshold,max_thresholds=128)
            saved=next(m for m in measurements if m['dataset']==episode['dataset'] and m['category']==episode['category'] and m['seed']==episode['seed'] and m['method']==method)
            for name in ['auroc','ap','tp','fp','fn','tn']:equal(detection[name],saved['detection'][name])
            for name in ['pixel_auroc','pixel_ap','au_pro','iou','pixel_f1']:equal(localization[name],saved['localization'][name])
            computed.append(saved)
    assert models==probe_replays==10 and raw_replays==map_files==200
    for method in ['baseline','hybrid']:
        mr=[r for r in rows if r['method']==method];me=[r for r in computed if r['method']==method];saved=summary['methods'][method]
        equal(saved['accuracy'],np.mean([r['correct'] for r in mr]));equal(saved['mean_image_auroc'],np.mean([m['detection']['auroc'] for m in me]));equal(saved['mean_image_ap'],np.mean([m['detection']['ap'] for m in me]))
        assert saved['misses']==sum(r['label'] and not r['decision'] for r in mr)
        assert saved['false_positives']==sum(not r['label'] and r['decision'] for r in mr)
        for name,value in saved['localization'].items():equal(value,np.mean([m['localization'][name] for m in me if m['localization'][name] is not None]))
    assert {k:sorted(v) for k,v in summary['transitions'].items()}=={k:sorted(v) for k,v in transitions.items()}
    assert transitions['detected_to_missed']==[] and transitions['false_positives_removed']==[]
    assert paired_auc_interval(rows)==summary['paired_image_auroc']
    result=dict(status='passed',mode='complete',selection_lock_sha256=sha256(run/'selection.lock.json'),
                inherited_development_audit_sha256=sha256(run/'development_audit.json'),
                verification_cases=200,method_rows=400,verification_unique_images=100,
                serialized_models_checked=models,feature_probe_replays=probe_replays,
                raw_score_and_map_replays=raw_replays,float32_map_archives_checked=map_files,
                native_mask_files_checked=len(complete['mask_sha256']),metrics_independently_recomputed=True,
                paired_auc_interval_recomputed=True,methods=summary['methods'],transitions={k:len(v) for k,v in transitions.items()},
                strict_target_normal_budget=1,extra_target_calibration_images=0,
                verification_used_for_selection=False,full_paper_benchmark_completed=False,
                caveats=['Two support draws and five fixed evaluation categories limit the conditional interval.',
                         'Accuracy reflects a balanced normal/anomaly image cohort, not industrial prevalence.',
                         'Classification labels are native; localization is center-croppedROI only.',
                         'No global or full-paper SOTA claim follows from this bounded matched comparison.'])
    write_json(run/'artifact_audit.json',result)
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',choices=['pre','complete'],required=True)
    p.add_argument('--config',default='/workspace/tools/configs/vision_hybrid_20261015.json');p.add_argument('--run',default='/tmp/vision_hybrid_20261015')
    a=p.parse_args();result=(audit_pre if a.mode=='pre' else audit_complete)(a.config,a.run);print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
