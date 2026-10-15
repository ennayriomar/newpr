"""Controlled register-DINO/search/local-PCA study and portable prediction.

plan -> develop -> evaluate are separate commands. Evaluation requires an
immutable selection lock and never selects parameters. No target calibration
images or target query labels fit a normal bank. Old experiments stay frozen.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import asdict
import fcntl
import hashlib
import json
import math
import os
from pathlib import Path
import random
import time

import numpy as np
from PIL import Image
from sklearn.metrics import average_precision_score,roc_auc_score
import torch

from .experiment_io import sha256,write_json,write_jsonl,read_jsonl,implementation_hashes
from .safal_cli import inventory
from .vision_hybrid_features import RegisterEncoder,SLOTS,roi_mask,WEIGHT_SHA256
from .vision_hybrid_model import VisionHybrid,HybridParameters,parameter_grid,fuse_raw,array_hash,source_hashes
from .research_metrics import thresholded_detection_metrics,localization_metrics,paired_crossed_bootstrap

CODE=['vision_hybrid_cli.py','vision_hybrid_model.py','vision_hybrid_features.py',
      'safal_features.py','safal_cli.py','safal_model.py','safal_calibration.py',
      'subspace_search.py','dense_features.py','patch_nn.py',
      'verify_dataset.py','experiment_io.py','research_metrics.py']


def read_json(path):return json.loads(Path(path).read_text())


def check_hashes(values):
    for path,h in values.items():
        if sha256(path)!=h:raise ValueError('Frozen input/artifact changed: '+path)


@contextmanager
def stage_lock(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    with (output/'.execution.lock').open('a+') as handle:
        try:fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise ValueError('Another stage is running in this output directory.')
        yield


def file_hashes(directory):
    return {str(p):sha256(p) for p in sorted(Path(directory).rglob('*')) if p.is_file()}


def _known_exposures(config):
    known=set(read_json(config['known_exposure'])['native_query_ids'])
    previous=read_json(config['previous_verification_lock'])
    known.update(e['dataset']+':'+i for e in previous['episodes'] for i in e['query_ids'])
    return known


def build_manifest(config,inventories):
    if config.get('schema_version')!=1 or config.get('shots')!=1 or config.get('seeds')!=[17,29]:
        raise ValueError('This declared pilot uses strict one-shot and two fixed support draws17/29.')
    previous=read_json(config['development_manifest'])
    development=[]
    for e in previous['episodes']:
        if e['shots']==4 and e['seed'] in config['seeds']:
            development.append(dict(id=e['id'].replace('-k4-','-k1-'),dataset=e['dataset'],category=e['category'],
                                    seed=e['seed'],shots=1,support_ids=e['support_ids'][:1],calibration_ids=[],
                                    query_ids=e['query_ids'],role='development'))
    if len(development)!=10:raise ValueError('Expected ten development bank episodes.')
    known=_known_exposures(config)
    known.update(e['dataset']+':'+i for e in development for i in e['query_ids'])
    rng=random.Random(config['query_sampling_seed']);verification=[]
    dev_categories={(e['dataset'],e['category']) for e in development}
    selected=[]
    for dataset,categories in sorted(config['verification_categories'].items()):
        root,lookup=inventories[dataset]
        for category in sorted(categories):
            if (dataset,category) in dev_categories:raise ValueError('Verification categories must differ from development categories.')
            ids=[]
            for label in ['normal','anomaly']:
                available=sorted(i for i,s in lookup.items() if s.category==category and s.split=='test' and s.label==label and dataset+':'+i not in known)
                if len(available)<config['queries_per_label']:raise ValueError('Not enough historically unmeasured images for '+dataset+':'+category+':'+label)
                ids.extend(rng.sample(available,config['queries_per_label']))
            normal=sorted(i for i,s in lookup.items() if s.category==category and s.split=='train' and s.label=='normal')
            for seed in config['seeds']:
                salt=int.from_bytes(hashlib.sha256(f'{dataset}:{category}:{seed}:strict-one-shot'.encode()).digest()[:8],'big')
                support=random.Random(salt).sample(normal,1)
                verification.append(dict(id=f'{dataset}-{category}-k1-seed{seed}',dataset=dataset,category=category,
                                         seed=seed,shots=1,support_ids=support,calibration_ids=[],query_ids=ids,
                                         role='verification'))
            selected.append(dict(dataset=dataset,category=category,query_ids=ids))
    if len(verification)!=10:raise ValueError('Expected ten verification bank episodes.')
    for episode in development+verification:
        _,lookup=inventories[episode['dataset']]
        if len(episode['support_ids'])!=1 or episode['calibration_ids'] or set(episode['support_ids'])&set(episode['query_ids']):
            raise ValueError('Strict one-shot budget or image-role disjointness violated.')
        for identifier in episode['support_ids']:
            sample=lookup[identifier]
            if sample.category!=episode['category'] or sample.split!='train' or sample.label!='normal':
                raise ValueError('Only a normal native training image may fit a target bank.')
        if len(set(episode['query_ids']))!=20:raise ValueError('Twenty unique native queries required per bank.')
        for identifier in episode['query_ids']:
            if lookup[identifier].category!=episode['category'] or lookup[identifier].split!='test':
                raise ValueError('Query is not in the declared native test category.')
    test_ids={e['dataset']+':'+i for e in verification for i in e['query_ids']}
    if len(test_ids)!=100 or test_ids&known:raise ValueError('Verification exposure exclusion failed.')
    return dict(schema_version=1,development=development,verification=verification,
                known_exposure_ids=sorted(known),selected_verification_queries=selected,
                known_history_overlap=0,development_unique_images=100,verification_unique_images=100,
                query_cases_per_fold=200,bank_episodes_per_fold=10,normal_target_budget=1,
                extra_target_calibration_images=0,query_sampling='Sorted dataset/category/label strata; random.Random predeclared seed; metadata only, no scores/mask inspection.',
                scope=config['claim_scope'],native_development_labels_and_masks_used_for_selection=True,
                verification_labels_and_masks_used_for_selection=False,
                evaluation_region='Center-cropped392 ROI mapped to256; image labels remain original native labels; masks use nearest interpolation, an explicit numerical-wrapper deviation from inspected default bilinear mask transform.')


def plan(config_path,output):
    output=Path(output);config=read_json(config_path)
    if (output/'plan.json').exists():
        validate_plan(config_path,output);return read_json(output/'manifest.json')
    inventories={d:inventory(config,d) for d in config['roots']}
    manifest=build_manifest(config,inventories)
    encoder=RegisterEncoder(**config['encoder'])
    paths=[Path(config_path).resolve(),Path(config['development_manifest']),Path(config['known_exposure']),
           Path(config['previous_verification_lock']),Path(config['encoder']['checkpoint'])]
    for dataset,(root,_) in inventories.items():
        if dataset=='visa':paths.extend([root/'split_csv/1cls.csv',*sorted(root.glob('*/image_anno.csv'))])
    for fold in ['development','verification']:
        for episode in manifest[fold]:
            root,lookup=inventories[episode['dataset']]
            paths.extend(root/i for i in episode['support_ids']+episode['query_ids'])
            if fold=='development':paths.extend(root/lookup[i].mask for i in episode['query_ids'] if lookup[i].mask)
    inputs={str(p):sha256(p) for p in sorted(set(paths))}
    inputs.update({str(Path(config['encoder']['source_dir'])/p):h for p,h in encoder.source_provenance['source_files_sha256'].items()})
    write_json(output/'manifest.json',manifest)
    write_json(output/'plan.json',dict(schema_version=1,config=config,manifest_sha256=sha256(output/'manifest.json'),
                                     input_sha256=inputs,implementation_sha256=implementation_hashes(CODE),
                                     encoder=encoder.metadata(),parameter_grid=[asdict(p)|{'id':p.id} for p in parameter_grid()],
                                     created_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
                                     verification_inference_started=False))
    print('PLAN LOCKED',manifest['scope'],flush=True)
    return manifest


def validate_plan(config_path,output):
    output=Path(output);record=read_json(output/'plan.json')
    if read_json(config_path)!=record['config']:raise ValueError('Run config changed.')
    if record['implementation_sha256']!=implementation_hashes(CODE):raise ValueError('Frozen implementation changed.')
    if sha256(output/'manifest.json')!=record['manifest_sha256']:raise ValueError('Frozen query/support manifest changed.')
    check_hashes(record['input_sha256'])
    return record


def save_raw(path,raw):
    if path.exists():raise ValueError('Refuse raw-score overwrite.')
    arrays={'search_'+s:raw['search'][s].numpy() for s in SLOTS}
    arrays.update({f'residual_{k}_{v}_{s}':values.numpy() for k,b in raw['residual'].items() for v,slots in b.items() for s,values in slots.items()})
    np.savez_compressed(path,**arrays)


def load_raw(path):
    with np.load(path,allow_pickle=False) as a:
        raw={'search':{s:torch.from_numpy(a['search_'+s].copy()) for s in SLOTS},'residual':{}}
        for key in a.files:
            if key.startswith('residual_'):
                _,k,v,s=key.split('_');raw['residual'].setdefault(k,{}).setdefault(v,{})[s]=torch.from_numpy(a[key].copy())
    return raw


def group_episodes(episodes):
    groups=defaultdict(list)
    for e in episodes:groups[e['dataset'],e['category']].append(e)
    return groups


def collect_fold(config_path,output,fold):
    output=Path(output);record=validate_plan(config_path,output);config=record['config'];manifest=read_json(output/'manifest.json')
    if fold=='verification':validate_selection(config_path,output)
    encoder=RegisterEncoder(**config['encoder'])
    inventories={d:inventory(config,d) for d in config['roots']}
    for (dataset,category),episodes in sorted(group_episodes(manifest[fold]).items()):
        directory=output/fold/(dataset+'-'+category)
        done=directory/'completion.json'
        if done.exists():
            completed=read_json(done)
            if completed['plan_sha256']!=sha256(output/'plan.json'):raise ValueError('Category completion has a different plan.')
            check_hashes(completed['artifact_sha256']);print('REUSED',fold,dataset,category,flush=True);continue
        if directory.exists() and any(directory.iterdir()):raise ValueError('Partial category exists. Preserve it under attempts before a clean retry: '+str(directory))
        directory.mkdir(parents=True,exist_ok=True)
        root,lookup=inventories[dataset]
        query_ids=episodes[0]['query_ids']
        if any(e['query_ids']!=query_ids for e in episodes):raise ValueError('Support draws must share exactly the same queries.')
        query_features=[]
        start=time.perf_counter()
        for i,identifier in enumerate(query_ids):
            print('FEATURES',fold,dataset,category,f'{i+1}/{len(query_ids)}',flush=True)
            query_features.append(encoder.query(root/identifier))
        np.savez_compressed(directory/'query_probe.npz',query_id=np.array(query_ids[0]),
                            **{s:query_features[0][s].numpy() for s in SLOTS})
        rows=[]
        for episode in episodes:
            bank=directory/episode['id'];bank.mkdir()
            print('SUPPORT',fold,episode['id'],flush=True)
            views,slot_indices=encoder.support(root/episode['support_ids'][0])
            t=time.perf_counter();model=VisionHybrid(views,slot_indices,episode['support_ids'],threads=config['encoder']['threads'])
            print('FITTED',episode['id'],'seconds',time.perf_counter()-t,flush=True)
            model.save(bank/'fit_model',HybridParameters(),0.,dict(encoder=encoder.metadata(),episode=episode,
                                                                 status='normal-only fitted bank; global hyperparameters not selected here',
                                                                 extra_target_calibration_images=0))
            case_records=[]
            for i,(identifier,query) in enumerate(zip(query_ids,query_features)):
                raw=model.raw(query);save_raw(bank/f'raw-{i:03d}.npz',raw)
                prediction=fuse_raw(raw,HybridParameters(),encoder.grid)
                # Native labels only annotate already-computed feature scores.
                sample=lookup[identifier]
                case=dict(dataset=dataset,category=category,seed=episode['seed'],query_id=identifier,
                          episode_id=episode['id'],label=int(sample.label!='normal'),
                          raw_file=str(bank/f'raw-{i:03d}.npz'),baseline_score=prediction['image_score'],
                          query_feature_hashes={s:array_hash(query[s].numpy()) for s in SLOTS},
                          original_support_images=1,extra_target_calibration_images=0)
                case_records.append(case);rows.append(case)
            write_json(bank/'cases.json',case_records)
            write_json(bank/'episode.json',episode)
        write_jsonl(directory/'cases.jsonl',rows)
        write_json(directory/'timing.json',dict(total_seconds=time.perf_counter()-start))
        write_json(done,dict(plan_sha256=sha256(output/'plan.json'),artifact_sha256=file_hashes(directory),
                             encoder=encoder.metadata(),fold=fold))
    return [r for p in sorted((output/fold).glob('*/cases.jsonl')) for r in read_jsonl(p)]


def case_mask(config,inventories,case):
    if not case['label']:return np.zeros((256,256),dtype=bool)
    root,lookup=inventories[case['dataset']];sample=lookup[case['query_id']]
    if not sample.mask:raise ValueError('Native anomaly mask missing.')
    with Image.open(root/sample.mask) as image:
        return roi_mask(image,config['encoder']['resize'],config['encoder']['crop'])


def metric_row(params,cases,scores,pixel_aps):
    groups=group_cases(cases)
    auc=[];ap=[]
    for _,indices in sorted(groups.items()):
        labels=[cases[i]['label'] for i in indices];values=[scores[i] for i in indices]
        auc.append(float(roc_auc_score(labels,values)));ap.append(float(average_precision_score(labels,values)))
    return dict(id=params.id,params=asdict(params),mean_image_auroc=float(np.mean(auc)),
                mean_image_ap=float(np.mean(ap)),mean_pixel_ap=float(np.mean(pixel_aps)),
                cases=len(cases),source_development_only=True)


def group_cases(cases):
    groups=defaultdict(list)
    for i,c in enumerate(cases):groups[c['dataset'],c['category'],c['seed']].append(i)
    return groups


def select_candidate(rows):
    baseline=next(r for r in rows if r['params']['strength']==0)
    feasible=[r for r in rows if r['mean_pixel_ap']+1e-12>=baseline['mean_pixel_ap']]
    return min(feasible,key=lambda r:(-r['mean_image_auroc'],-r['mean_pixel_ap'],r['params']['strength'],r['params']['clusters'],r['id']))


def finalize_bank(bank,params,threshold,pixel_threshold,decision_hash):
    original=bank/'fit_model.npz';target=bank/'model.npz';document=read_json(bank/'fit_model.json')
    if sha256(original)!=document['npz_sha256']:raise ValueError('Fitted support feature archive changed.')
    if not target.exists():os.link(original,target)
    if sha256(target)!=document['npz_sha256']:raise ValueError('Selected model feature archive changed.')
    document.update(params=asdict(params),parameters_id=params.id,threshold=threshold,pixel_threshold=pixel_threshold)
    document['provenance'].update(status='globally selected research candidate',decision_sha256=decision_hash)
    write_json(bank/'model.json',document)


def develop(config_path,output):
    output=Path(output)
    if (output/'selection.lock.json').exists():return validate_selection(config_path,output)
    record=validate_plan(config_path,output);config=record['config']
    cases=collect_fold(config_path,output,'development')
    inventories={d:inventory(config,d) for d in config['roots']}
    grid=parameter_grid();score_matrix=np.zeros((len(grid),len(cases)));pixel_aps=[[] for _ in grid];normal_pixels=[]
    for key,indices in sorted(group_cases(cases).items()):
        print('DEVELOPMENT METRICS',key,flush=True)
        truths=[case_mask(config,inventories,cases[i]) for i in indices]
        truth=np.concatenate([m.flatten() for m in truths])
        raws=[load_raw(cases[i]['raw_file']) for i in indices]
        for j,params in enumerate(grid):
            predictions=[fuse_raw(raw,params,config['encoder']['crop']//14) for raw in raws]
            score_matrix[j,indices]=[p['image_score'] for p in predictions]
            pixel_aps[j].append(float(average_precision_score(truth,np.concatenate([p['map'].flatten() for p in predictions]))))
            if j==0:normal_pixels.extend(p['map'].flatten().copy() for i,p in zip(indices,predictions) if not cases[i]['label'])
    rows=[metric_row(p,cases,score_matrix[j],pixel_aps[j]) for j,p in enumerate(grid)]
    baseline=rows[0]
    for row in rows:row['pixel_ap_guard_passed']=row['mean_pixel_ap']+1e-12>=baseline['mean_pixel_ap']
    winner=select_candidate(rows);params=HybridParameters(**winner['params'])
    normal_scores=score_matrix[0,np.array([not c['label'] for c in cases])]
    threshold=float(np.quantile(normal_scores,.95,method='linear'))
    pixel_threshold=float(np.quantile(np.concatenate(normal_pixels),.995,method='linear'))
    if not math.isfinite(threshold) or threshold<=0:raise ValueError('Invalid source-normal global image cutoff.')
    write_json(output/'development_cases.json',cases)
    write_json(output/'development_grid.json',rows)
    np.savez_compressed(output/'development_scores.npz',scores=score_matrix,ids=np.array([p.id for p in grid]))
    decision=dict(winner=winner,baseline=baseline,params=asdict(params),parameters_id=params.id,
                  image_threshold=threshold,pixel_threshold=pixel_threshold,
                  threshold_fit='Image95th percentile and pixel99.5th percentile of baseline development-normal scores; separate fixed source-derived cutoffs shared by both methods',
                  normal_calibration_unique_images=len({(c['dataset'],c['query_id']) for c in cases if not c['label']}),
                  threshold_target_extra_normal_images=0,verification_inference_seen=False,verification_masks_seen=False,
                  primary='Mean within-category/support-draw image AUROC',
                  pixel_guard='Mean within-category/support-draw cropped256x256 pixel AP >= baseline',
                  tie_break='Higher pixel AP, smaller correction strength, fewer subspaces, parameter SHA256')
    write_json(output/'development_decision.json',decision)
    for path in sorted((output/'development').glob('*/*/fit_model.json')):
        finalize_bank(path.parent,params,threshold,pixel_threshold,sha256(output/'development_decision.json'))
    artifacts=file_hashes(output/'development')
    for name in ['development_cases.json','development_grid.json','development_scores.npz','development_decision.json']:
        artifacts[str(output/name)]=sha256(output/name)
    lock=dict(schema_version=1,decision=decision,plan_sha256=sha256(output/'plan.json'),
              artifact_sha256=artifacts,implementation_sha256=implementation_hashes(CODE),
              locked_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),
              verification_inference_seen=False,verification_masks_seen=False)
    write_json(output/'selection.lock.json',lock)
    print('SELECTION LOCKED',json.dumps(decision),flush=True)
    return lock


def validate_selection(config_path,output):
    output=Path(output);validate_plan(config_path,output);lock=read_json(output/'selection.lock.json')
    if lock['plan_sha256']!=sha256(output/'plan.json') or lock['implementation_sha256']!=implementation_hashes(CODE):
        raise ValueError('Selection dependency mismatch.')
    check_hashes(lock['artifact_sha256'])
    if lock['verification_inference_seen'] or lock['verification_masks_seen']:raise ValueError('Verification leaked into selection.')
    p=HybridParameters(**lock['decision']['params'])
    if p.id!=lock['decision']['parameters_id']:raise ValueError('Locked parameter ID mismatch.')
    rows=read_json(output/'development_grid.json')
    if select_candidate(rows)!=lock['decision']['winner']:raise ValueError('Saved decision no longer matches complete grid.')
    for path in sorted((output/'development').glob('*/*/model.json')):
        model=read_json(path)
        if model['params']!=asdict(p) or model['parameters_id']!=p.id or model['threshold']!=lock['decision']['image_threshold'] or model['pixel_threshold']!=lock['decision']['pixel_threshold']:
            raise ValueError('Bank parameters/cutoff differ from the selection lock.')
    return lock


def evaluate(config_path,output):
    output=Path(output);lock=validate_selection(config_path,output)
    complete=output/'evaluation_completion.json'
    if complete.exists():
        old=read_json(complete)
        if old['selection_lock_sha256']!=sha256(output/'selection.lock.json'):raise ValueError('Evaluation belongs to another lock.')
        check_hashes(old['artifact_sha256']);check_hashes(old['mask_sha256']);return old
    cases=collect_fold(config_path,output,'verification');config=read_json(config_path)
    params=HybridParameters(**lock['decision']['params']);threshold=lock['decision']['image_threshold'];pixel_threshold=lock['decision']['pixel_threshold']
    inventories={d:inventory(config,d) for d in config['roots']}
    rows=[];episode_metrics=[];mask_hashes={};roi_empty=[]
    for key,indices in sorted(group_cases(cases).items()):
        print('VERIFICATION METRICS',key,flush=True)
        truths=[];labels=[];maps={'baseline':[],'hybrid':[]};scores={'baseline':[],'hybrid':[]}
        bank=Path(cases[indices[0]]['raw_file']).parent
        finalize_bank(bank,params,threshold,pixel_threshold,sha256(output/'development_decision.json'))
        map_dir=bank/'maps';map_dir.mkdir(exist_ok=True)
        for j,i in enumerate(indices):
            c=cases[i];raw=load_raw(c['raw_file'])
            predictions={'baseline':fuse_raw(raw,HybridParameters(),config['encoder']['crop']//14),
                         'hybrid':fuse_raw(raw,params,config['encoder']['crop']//14)}
            if predictions['hybrid']['image_score']<predictions['baseline']['image_score']:
                raise ValueError('Nonnegative-correction image-score invariant failed.')
            truth=case_mask(config,inventories,c);truths.append(truth);labels.append(c['label'])
            root,lookup=inventories[c['dataset']];sample=lookup[c['query_id']]
            if sample.mask:mask_hashes[str(root/sample.mask)]=sha256(root/sample.mask)
            if c['label'] and not truth.any():roi_empty.append(c['dataset']+':'+c['query_id'])
            arrays={'truth':truth.astype(np.uint8)}
            for name,p in predictions.items():
                maps[name].append(p['map']);scores[name].append(p['image_score']);arrays[name]=p['map']
                rows.append({k:v for k,v in c.items() if k!='raw_file'}|dict(method=name,score=p['image_score'],
                             threshold=threshold,decision=bool(p['image_score']>=threshold),
                             correct=bool((p['image_score']>=threshold)==c['label']),parameters_id=p['parameters_id'],
                             map_file=str(map_dir/f'query-{j:03d}.npz'),probabilities=False,
                             metric_region='center-cropped ROI,256x256',selection_lock_sha256=sha256(output/'selection.lock.json')))
            np.savez_compressed(map_dir/f'query-{j:03d}.npz',**arrays)
        for name in maps:
            # The separate source-normal pixel cutoff is shared unchanged by
            # both methods; it is not calibrated on target category queries.
            episode_metrics.append(dict(dataset=key[0],category=key[1],seed=key[2],method=name,
                                        detection=thresholded_detection_metrics(labels,scores[name],threshold),
                                        localization=localization_metrics(truths,maps[name],pixel_threshold,max_thresholds=128)))
    write_jsonl(output/'verification_predictions.jsonl',rows)
    write_json(output/'verification_metrics.json',episode_metrics)
    artifacts=file_hashes(output/'verification')
    for name in ['verification_predictions.jsonl','verification_metrics.json']:artifacts[str(output/name)]=sha256(output/name)
    record=dict(selection_lock_sha256=sha256(output/'selection.lock.json'),method_rows=len(rows),
                paired_cases=len(cases),unique_images=len({(c['dataset'],c['query_id']) for c in cases}),
                mask_sha256=mask_hashes,artifact_sha256=artifacts,
                native_anomalies_with_empty_cropped_mask=sorted(set(roi_empty)),
                verification_used_for_selection=False,old_probability_head_used=False)
    write_json(complete,record)
    return record


def paired_auc_interval(rows,n_bootstrap=2000,seed=20261015):
    """Paired crossed stratified query/support AUC bootstrap, fixed categories."""
    by_case=defaultdict(dict)
    for row in rows:by_case[row['dataset'],row['category'],row['seed'],row['query_id']][row['method']]=row
    grouped=defaultdict(list)
    for key,value in by_case.items():
        if set(value)!={'baseline','hybrid'}:raise ValueError('Incomplete paired methods.')
        grouped[key[:2]].append((key,value))
    rng=np.random.default_rng(seed);draws=[];points=[]
    for category,cases in sorted(grouped.items()):
        supports=sorted({key[2] for key,_ in cases});queries=sorted({key[3] for key,_ in cases})
        labels={key[3]:value['baseline']['label'] for key,value in cases}
        positive=[q for q in queries if labels[q]];negative=[q for q in queries if not labels[q]]
        lookup={(key[2],key[3]):v for key,v in cases}
        if len(cases)!=len(supports)*len(queries) or not positive or not negative:raise ValueError('Complete query/support grids with both classes required.')
        differences=[]
        for support in supports:
            matrices={}
            for method in ['baseline','hybrid']:
                pos=np.array([lookup[support,q][method]['score'] for q in positive])
                neg=np.array([lookup[support,q][method]['score'] for q in negative])
                matrices[method]=(pos[:,None]>neg[None,:]).astype(float)+.5*(pos[:,None]==neg[None,:])
            differences.append(matrices['hybrid']-matrices['baseline'])
        matrix=np.stack(differences);points.append(float(matrix.mean()))
        sc=rng.multinomial(len(supports),np.ones(len(supports))/len(supports),size=n_bootstrap)
        pc=rng.multinomial(len(positive),np.ones(len(positive))/len(positive),size=n_bootstrap)
        nc=rng.multinomial(len(negative),np.ones(len(negative))/len(negative),size=n_bootstrap)
        draws.append(np.einsum('bs,bp,spn,bn->b',sc,pc,matrix,nc)/(len(supports)*len(positive)*len(negative)))
    samples=np.mean(draws,axis=0)
    return dict(estimate=float(np.mean(points)),interval=np.quantile(samples,[.025,.975]).tolist(),
                n_bootstrap=n_bootstrap,seed=seed,scope='Conditional paired query/support bootstrap; positive and negative queries resampled separately; categories fixed; two support draws limit replication.')


def report(config_path,output):
    output=Path(output);validate_selection(config_path,output);config=read_json(config_path)
    complete=read_json(output/'evaluation_completion.json');check_hashes(complete['artifact_sha256']);check_hashes(complete['mask_sha256'])
    rows=read_jsonl(output/'verification_predictions.jsonl');metrics=read_json(output/'verification_metrics.json')
    by_case=defaultdict(dict)
    for row in rows:
        if row['decision']!=(row['score']>=row['threshold']) or row['correct']!=(row['decision']==row['label']):raise ValueError('Recorded decisions/correctness differ from raw scores.')
        by_case[row['dataset'],row['category'],row['seed'],row['query_id']][row['method']]=row
    methods={}
    for method in ['baseline','hybrid']:
        cases=[r for r in rows if r['method']==method];m=[r for r in metrics if r['method']==method]
        methods[method]=dict(accuracy=float(np.mean([r['correct'] for r in cases])),
                             misses=sum(r['label'] and not r['decision'] for r in cases),
                             false_positives=sum(not r['label'] and r['decision'] for r in cases),
                             mean_image_auroc=float(np.mean([r['detection']['auroc'] for r in m])),
                             mean_image_ap=float(np.mean([r['detection']['ap'] for r in m])),
                             localization={key:float(np.mean([r['localization'][key] for r in m if r['localization'][key] is not None]))
                                           for key in ['pixel_auroc','pixel_ap','au_pro','iou','pixel_f1']})
    paired=[];lost=[];recovered=[];fp_added=[];fp_removed=[]
    for key,values in by_case.items():
        if set(values)!={'baseline','hybrid'}:raise ValueError('Incomplete methods.')
        b,h=values['baseline'],values['hybrid'];identity=':'.join(map(str,key))
        paired.append(dict(dataset=key[0],category=key[1],seed=key[2],query_id=key[3],paired_difference=int(h['correct'])-int(b['correct'])))
        if b['label']:
            if b['decision'] and not h['decision']:lost.append(identity)
            if not b['decision'] and h['decision']:recovered.append(identity)
        else:
            if not b['decision'] and h['decision']:fp_added.append(identity)
            if b['decision'] and not h['decision']:fp_removed.append(identity)
    lock=read_json(output/'selection.lock.json');auc=paired_auc_interval(rows)
    summary=dict(schema_version=1,version='0.7.0',scope=config['claim_scope'],
                 unique_verification_images=complete['unique_images'],paired_cases=complete['paired_cases'],
                 method_rows=complete['method_rows'],shots=1,extra_target_calibration_images=0,
                 verification_support_draws=2,methods=methods,selected=lock['decision'],
                 paired_image_auroc=auc,
                 paired_accuracy=paired_crossed_bootstrap(paired,n_bootstrap=2000,seed=20261015),
                 transitions=dict(detected_to_missed=lost,missed_to_detected=recovered,
                                  false_positives_added=fp_added,false_positives_removed=fp_removed),
                 headline_paper_superiority_established=False,
                 matched_pilot_auc_gain_interval_above_zero=auc['interval'][0]>0,
                 native_anomalies_with_empty_cropped_mask=complete['native_anomalies_with_empty_cropped_mask'],
                 full_benchmark_completed=False,old_error_head_used=False,
                 selection_lock_sha256=sha256(output/'selection.lock.json'),
                 caveats=['Independent reconstruction of inspected class-separated scoring recipe, not a reproduced full paper benchmark.',
                          'Five verification categories differ from the five categories used for this study selection; historical category exposure may exist.',
                          'Verification IDs exclude the available prior local query history; no universal pristine-history claim.',
                          'Image metrics are averaged within category/reference draw; raw scores from differently fitted categories are not pooled.',
                          'All target banks use one original normal image with correlated augmented views; no extra target calibration images.',
                          'A global operational cutoff comes from separate development-category normals, and the same cutoff is retained for both methods.',
                          'Image labels remain native; segmentation metrics evaluate only the center-cropped ROI with nearest-resized masks.',
                          'Pixel IoU/F1 cutoff is the baseline development-normal pixel99.5th percentile; it carries no target false-alarm guarantee.',
                          'Correction is nonnegative, so fixed-cutoff search alerts are preserved; additional false positives remain possible.',
                          'Frozen foundation weights, no LLM or backbone fine-tuning; gates are heuristics and no probability head is attached.'])
    write_json(output/'summary.json',summary)
    lines=['# Register-DINO search and local-PCA correction: measured study','',config['claim_scope'],'',
           'This is a strict one-target-image support budget, with zero extra target calibration images. Development selection uses100 images in five other categories; verification uses100 available-history-excluded image IDs in five categories and two support draws (200 paired cases).','',
           '## Locked candidate','',json.dumps(lock['decision']['params'],indent=2),
           '',f"Global source-normal cutoff: {lock['decision']['image_threshold']:.8f}. Primary selection metric is mean image AUROC with a development pixel-AP non-regression guard. Zero correction remains an eligible baseline.",'',
           '| Method | Image AUROC | Accuracy | Misses /100 anomaly cases | False alarms /100 normal cases | Pixel AP | AU-PRO |',
           '|---|---:|---:|---:|---:|---:|---:|']
    for method,m in methods.items():lines.append(f"| {method} | {100*m['mean_image_auroc']:.2f}% | {100*m['accuracy']:.2f}% | {m['misses']} | {m['false_positives']} | {m['localization']['pixel_ap']:.4f} | {m['localization']['au_pro']:.4f} |")
    lines+=['',f"Paired hybrid-minus-baseline image AUROC: {100*auc['estimate']:+.2f} percentage points; conditional95% interval [{100*auc['interval'][0]:+.2f}, {100*auc['interval'][1]:+.2f}].",
            '',f"Detected-to-missed cases: {len(lost)}. Missed-to-detected cases: {len(recovered)}. Added/removed false alarms: {len(fp_added)}/{len(fp_removed)}.",'',
            'The published full MVTec AD/VisA scores are not matched by these category/sample/support-draw cohorts; this study cannot establish superiority over the paper.','',
            '## Category/reference-draw measurements','',
            '| Dataset/category | Draw | Method | Image AUROC | Pixel AP | AU-PRO |','|---|---:|---|---:|---:|---:|']
    for r in metrics:lines.append(f"| {r['dataset']}/{r['category']} | {r['seed']} | {r['method']} | {100*r['detection']['auroc']:.2f}% | {r['localization']['pixel_ap']:.4f} | {r['localization']['au_pro']:.4f} |")
    lines+=['','## Scope','']+['- '+c for c in summary['caveats']]+['']
    text='\n'.join(lines)
    if (output/'report.md').exists() and (output/'report.md').read_text()!=text:raise ValueError('Refuse report overwrite.')
    (output/'report.md').write_text(text)
    print(json.dumps({'methods':methods,'paired_image_auroc':auc}),flush=True)
    return summary


def predict(model_path,image_path,output,source_dir=None,checkpoint=None,device=None):
    model=VisionHybrid.load(model_path);expected=model.provenance['encoder'];runtime=expected['runtime']
    if model.provenance.get('status')!='globally selected research candidate' or model.pixel_threshold is None:
        raise ValueError('Prediction requires a selected model, not an unselected fitted-bank checkpoint.')
    encoder=RegisterEncoder(source_dir or runtime['source_dir'],checkpoint or runtime['checkpoint'],
                            device=device or expected['device'],threads=runtime['threads'],
                            resize=expected['resize'],crop=expected['crop'],layers=expected['layers'])
    actual=encoder.metadata()
    for key in ['backbone','checkpoint_sha256','source_manifest_sha256','crop','resize','layers','position_interpolation','implementation_sha256']:
        if actual[key]!=expected[key]:raise ValueError('Trained encoder semantics differ: '+key)
    query=encoder.query(image_path);result=model.predict(query)
    destination=Path(output)
    if destination.exists():raise ValueError('Choose a new prediction output directory.')
    destination.mkdir(parents=True)
    np.savez_compressed(destination/'cropped_roi_maps.npz',hybrid=result['map'])
    record=dict(image=str(Path(image_path).resolve()),image_sha256=sha256(image_path),
                image_score=result['image_score'],threshold=model.threshold,
                decision=bool(result['image_score']>=model.threshold),parameters=asdict(model.params),
                pixel_threshold=model.pixel_threshold,
                parameters_id=model.params.id,probabilities=False,region='Center-cropped392 ROI,256 metric pixels; outer border is unscored',
                support_ids=list(model.support_ids),extra_target_calibration_images=0,encoder=actual)
    write_json(destination/'prediction.json',record);print(json.dumps(record),flush=True)
    return record


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage',choices=['plan','develop','evaluate','report','predict'])
    parser.add_argument('--config');parser.add_argument('--output',required=True)
    parser.add_argument('--model');parser.add_argument('--image')
    parser.add_argument('--source-dir');parser.add_argument('--checkpoint');parser.add_argument('--device',choices=['cpu','cuda'])
    args=parser.parse_args()
    if args.stage=='predict':
        if not args.model or not args.image:parser.error('predict requires --model and --image')
        predict(args.model,args.image,args.output,args.source_dir,args.checkpoint,args.device);return
    if not args.config:parser.error('This stage requires --config')
    with stage_lock(args.output):
        {'plan':plan,'develop':develop,'evaluate':evaluate,'report':report}[args.stage](args.config,args.output)


if __name__=='__main__':main()
