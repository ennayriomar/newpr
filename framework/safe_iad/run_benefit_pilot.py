"""Paired learned-reference feasibility with locked cutoffs and real-data safeguards."""
import argparse
from dataclasses import asdict
import json
from pathlib import Path
import shutil
import time

import numpy as np
from PIL import Image
from scipy.stats import spearmanr
import torch

from .acquisition import InferenceInputs,global_descriptor,select_reference,select_learned_reference
from .benefit_model import BenefitModel
from .counterfactual import FEATURE_NAMES,evaluation_oracle,inference_feature_vector,offline_loss,support_diagnostics
from .experiment_io import complete_stage,image_score,implementation_hashes,read_jsonl,save_maps,sha256,verify_stage,write_json,write_jsonl
from .missing_support import missing_support_plan
from .patch_nn import FrozenDINOv2,LAYER_CONFIGURATION,PREPROCESS_VERSION,patch_nearest_neighbor,restore_map,validate_episode
from .research_metrics import defect_preservation,localization_metrics,paired_crossed_bootstrap,risk_coverage,thresholded_detection_metrics
from .run_acquisition_pilot import save_diagnostics
from .run_baseline_pilot import Prediction
from .splits import validate_category_roles,validate_partition
from .support_decision import DEFAULT_SIGMOID,action,adequacy_field
from .verify_dataset import discover


POLICIES=['none','random','nearest_global','diversity','learned','oracle']


def validate_pilot_config(config):
    if config['acquisition_budget']!=1:
        raise ValueError('M3 is a validated one-step budget1 pilot; sequential budgets require a separate validated runner')
    shots=config['evaluation_shots']
    if not shots or any(isinstance(k,bool) or k not in {1,2,4,8} for k in shots) or len(set(shots))!=len(shots):
        raise ValueError('Unique positive declared few-shot sizes required')
    if len(config['seeds'])!=len(set(config['seeds'])) or not config['seeds']:
        raise ValueError('Unique support-draw seeds required')
    for dataset,category in config['validation_categories'].items():
        if category not in config['category_roles'][dataset]['validation']:
            raise ValueError('Pilot evaluation cannot relabel a final/calibration/source category as validation')


def load_samples(config):
    validate_pilot_config(config)
    data={}
    for dataset in config['validation_categories']:
        root=Path(config['roots'][dataset])
        samples,categories,issues,_=discover(root,dataset,None)
        if issues: raise ValueError('Dataset discovery failed: '+str(issues))
        validate_category_roles(config['category_roles'][dataset],categories)
        data[dataset]=(root,samples,{sample.image:sample for sample in samples})
    return data


def calibrate(config,extractor,data,input_paths):
    """Normal-only calibration categories; no benchmark test masks are opened."""
    all_cutoffs={}
    for dataset,category in config['calibration_categories'].items():
        if category not in config['category_roles'][dataset]['calibration']:
            raise ValueError('Detector cutoff data must have the calibration role')
        root,samples,_=data[dataset]
        normals=sorted([s for s in samples if s.category==category and s.split=='train' and s.label=='normal'],key=lambda s:s.image)
        order=np.random.default_rng(config['partition_seed']+9100).permutation(len(normals))
        needed=len(config['seeds'])*config['normal_calibration_queries']
        reserved=[normals[i] for i in order[:needed]]
        allowed=[normals[i] for i in order[needed:]]
        for draw,seed in enumerate(config['seeds']):
            supports=[allowed[i] for i in np.random.default_rng(seed+9100).choice(len(allowed),max(config['evaluation_shots']),replace=False)]
            queries=reserved[draw*config['normal_calibration_queries']:(draw+1)*config['normal_calibration_queries']]
            if len(queries)!=config['normal_calibration_queries']: raise ValueError('Insufficient normal calibration data')
            support_features=[extractor.extract(dataset,s,root)[0] for s in supports]
            for sample in supports+queries: input_paths.add(root/sample.image)
            for shots in config['evaluation_shots']:
                validate_partition([s.image for s in supports[:shots]],[],[s.image for s in reserved])
                scores=[];total=count=second=0.
                for query in queries:
                    features,size,_,_=extractor.extract(dataset,query,root)
                    patch=patch_nearest_neighbor(features,torch.cat(support_features[:shots]))
                    scores.append(image_score(patch))
                    native=restore_map(patch,(16,16),size).astype(np.float64)
                    total+=float(native.sum());second+=float(np.square(native).sum());count+=native.size
                mean=total/count;variance=max(0.,second/count-mean*mean)
                key=f'{dataset}:{seed}:{shots}'
                all_cutoffs[key]={'image_threshold':float(np.mean(scores)+3*np.std(scores)),
                                  'pixel_threshold':float(mean+3*np.sqrt(variance)),
                                  'dataset':dataset,'seed':seed,'shots':shots,'category':category,
                                  'support_ids':[s.image for s in supports[:shots]],
                                  'calibration_query_ids':[s.image for s in queries],
                                  'native_split':'train','experiment_role':'calibration_normal',
                                  'procedure':'held-out normal calibration mean+3std; fixed for pre/post interventions',
                                  'no_test_defect_labels_used':True,'is_probability_calibration':False,
                                  'extra_normal_calibration_images':len(queries),
                                  'transfer_scope':'dataset-level category-disjoint calibration; no false-alarm guarantee'}
    return all_cutoffs


def paired_plans(config,data):
    plans=[]
    for dataset,category in config['validation_categories'].items():
        root,samples,_=data[dataset]
        normals=sorted([s for s in samples if s.category==category and s.split=='train' and s.label=='normal'],key=lambda s:s.image)
        queries=[]
        for label in ['normal','anomaly']:
            chosen=sorted([s for s in samples if s.category==category and s.split=='test' and s.label==label],key=lambda s:s.image)[:config['queries_per_label']]
            if len(chosen)!=config['queries_per_label']: raise ValueError('Insufficient native validation-category queries')
            queries.extend(chosen)
        for seed in config['seeds']:
            draw=np.random.default_rng(seed+1777).choice(len(normals),max(config['evaluation_shots'])+config['candidate_pool_size'],replace=False)
            supports=[normals[i] for i in draw[:max(config['evaluation_shots'])]]
            candidates=[normals[i] for i in draw[max(config['evaluation_shots']):]]
            validate_partition([s.image for s in supports],[s.image for s in candidates],[s.image for s in queries])
            plans.append({'dataset':dataset,'category':category,'seed':seed,'protocol':'paired_validation',
                          'support_ids':[s.image for s in supports],'candidate_ids':[s.image for s in candidates],
                          'query_ids':[s.image for s in queries],
                          'query_role':'reserved validation-category native test data; masks used for offline evaluation only',
                          'query_sampling':'first sorted normal/anomalous examples; descriptive feasibility subset',
                          'used_to_select_model_or_threshold':False})
    return plans


def omission_plans(config,extractor,data,input_paths):
    plans=[]
    for dataset,category in config['validation_categories'].items():
        root,samples,_=data[dataset]
        normals=sorted([s for s in samples if s.category==category and s.split=='train' and s.label=='normal'],key=lambda s:s.image)
        chosen=[normals[i] for i in np.random.default_rng(config['partition_seed']+8771).choice(len(normals),config['missing_support_normals'],replace=False)]
        descriptors=[]
        for sample in chosen:
            features,_,_,_=extractor.extract(dataset,sample,root)
            descriptors.append(global_descriptor(features).numpy());input_paths.add(root/sample.image)
        for seed in config['seeds']:
            plan=missing_support_plan([s.image for s in chosen],np.stack(descriptors),seed+8771,
                                      shots=max(config['evaluation_shots']),pool_size=config['candidate_pool_size'],
                                      queries_per_group=config['missing_support_queries'],clusters=3,with_control=True)
            common={'dataset':dataset,'category':category,'seed':seed,
                    'candidate_ids':plan['candidate_ids'],'query_ids':plan['query_ids'],
                    'query_role':'held-back normal training images','grouping':plan,
                    'used_to_select_model_or_threshold':False}
            plans.append({**common,'protocol':'missing_support',
                          'support_ids':plan['initial_support_ids'],'candidate_ids':plan['candidate_ids'],
                          'query_ids':plan['query_ids'],'query_role':'held-back normal training images',
                          'grouping':plan,'used_to_select_model_or_threshold':False})
            plans.append({**common,'protocol':'coverage_control','support_ids':plan['covered_support_ids'],
                          'support_condition':'one equal-budget initial reference covers the omitted proxy group'})
    return plans


def evaluate_plan(config,plan,shots,extractor,model,cutoff,data,output,input_paths):
    dataset,category,seed=plan['dataset'],plan['category'],plan['seed']
    root,_,lookup=data[dataset]
    supports=[lookup[i] for i in plan['support_ids'][:shots]]
    candidates=[lookup[i] for i in plan['candidate_ids']]
    queries=[lookup[i] for i in plan['query_ids']]
    validate_episode(supports,queries,shots)
    validate_partition([s.image for s in supports],[s.image for s in candidates],[s.image for s in queries])
    if any(s.split!='train' or s.label!='normal' for s in candidates): raise ValueError('Candidate must be verified-normal training data')
    episode=output/plan['protocol']/dataset/category/f'seed-{seed}_k-{shots}_b-1'
    episode.mkdir(parents=True,exist_ok=True)
    if verify_stage(episode,require_inputs=True):
        cached_metrics=[json.loads((episode/policy/'metrics.json').read_text()) for policy in POLICIES]
        cached_predictions=read_jsonl(episode/'all_predictions.jsonl')
        ledger=json.loads((episode/'completion.json').read_text())
        input_paths.update(Path(path) for path in ledger['input_sha256'])
        print(json.dumps({'resumed_episode':str(episode),'verified_prediction_records':len(cached_predictions)}),flush=True)
        return cached_metrics,cached_predictions
    write_json(episode/'manifest.json',{**plan,'shots':shots,'initial_support_ids':[s.image for s in supports],
                                      'candidate_pool_size':len(candidates),'acquisition_budget':1,
                                      'budget_unit':'per query inspection, reset initial support for each query',
                                      'information':'same verified-normal pool for all policies; learned/oracle probe every candidate patch memory',
                                      'model':model.name,'cutoffs':cutoff,'adequacy':config.get('adequacy',DEFAULT_SIGMOID),
                                      'defect_evidence':'raw NN before/after, never multiplied by diagnostics',
                                      'native_test_labels_for_model_selection':False})
    start=time.perf_counter();references=[extractor.extract(dataset,s,root)[0] for s in supports]
    support_seconds=time.perf_counter()-start
    start=time.perf_counter();candidate_data=[extractor.extract(dataset,s,root) for s in candidates]
    pool_seconds=time.perf_counter()-start
    candidate_features=[row[0] for row in candidate_data]
    candidate_globals=torch.stack([global_descriptor(features) for features in candidate_features])
    support_globals=torch.stack([global_descriptor(features) for features in references])
    for sample in supports+candidates+queries:
        input_paths.add(root/sample.image)
        if sample.mask: input_paths.add(root/sample.mask)
    accumulators={policy:{'rows':[],'maps':[],'truths':[],'labels':[],'scores':[],'adequacy':[]} for policy in POLICIES}
    candidate_records=[];all_predictions=[]
    actual_contract={'checkpoint_sha256':extractor.checkpoint_hash,'source_commit':extractor.source_commit,
                     'preprocessing_version':PREPROCESS_VERSION,'feature_layer_configuration':LAYER_CONFIGURATION,
                     'loss_specification':config['loss']}
    for index,query in enumerate(queries):
        started=time.perf_counter();features,size,cached,key=extractor.extract(dataset,query,root)
        feature_seconds=time.perf_counter()-started
        diagnostics=support_diagnostics(features,references)
        before_scores=diagnostics['nearest_distance'];before=restore_map(before_scores,(16,16),size)
        image_before=image_score(before_scores)
        save_maps(episode/f'query-{index:03d}_before.npz',defect_map=before)
        diagnostic_before=save_diagnostics(episode/f'query-{index:03d}_diagnostics_before.npz',diagnostics)
        inputs=InferenceInputs(global_descriptor(features),support_globals,candidate_globals,
                               tuple(s.image for s in candidates),seed,query.image)
        selections={'none':None}
        selection_times={}
        for policy in ['random','nearest_global','diversity']:
            tick=time.perf_counter();selections[policy]=select_reference(policy,inputs,budget=1)
            selection_times[policy]=time.perf_counter()-tick
        tick=time.perf_counter();after_patches=[];vectors=[];probe_times=[]
        for candidate in candidate_features:
            t=time.perf_counter();scores=patch_nearest_neighbor(features,torch.cat(references+[candidate]))
            vectors.append(inference_feature_vector(features,references,candidate,diagnostics,scores))
            after_patches.append(scores);probe_times.append(time.perf_counter()-t)
        probes_seconds=time.perf_counter()-tick
        tick=time.perf_counter()
        selections['learned'],predicted=select_learned_reference(inputs,vectors,model,budget=1,
                                                               feature_names=FEATURE_NAMES,provenance=actual_contract)
        selection_times['learned']=time.perf_counter()-tick
        # All deployable selections are now fixed. Labels enter only below.
        if query.mask:
            with Image.open(root/query.mask) as mask: truth=np.asarray(mask)>0
        else:
            truth=np.zeros(before.shape,dtype=bool)
        if truth.shape!=before.shape: raise ValueError('Native mask/map shape mismatch')
        before_loss=offline_loss(before,truth,config['loss'],image_score=image_before)
        candidate_losses=[]
        for scores in after_patches:
            native=restore_map(scores,(16,16),size)
            candidate_losses.append(offline_loss(native,truth,config['loss'],image_score=image_score(scores)))
        benefits=[before_loss-loss for loss in candidate_losses]
        selections['oracle']=evaluation_oracle(benefits)
        for candidate,vector,estimate,observed in zip(candidates,vectors,predicted,benefits):
            candidate_records.append({'dataset':dataset,'category':category,'seed':seed,'shots':shots,
                                      'query_id':query.image,'candidate_id':candidate.image,'features':vector,
                                      'predicted_benefit':estimate,'observed_benefit':observed,
                                      'experiment_role':'validation_evaluation_only','never_use_for_training':True,
                                      'used_for_model_selection':False,'oracle_is_deployable':False})
        for policy in POLICIES:
            tick=time.perf_counter();selected=selections[policy]
            scores=before_scores if selected is None else after_patches[selected]
            after=before if selected is None else restore_map(scores,(16,16),size)
            bank=references if selected is None else references+[candidate_features[selected]]
            post=diagnostics if selected is None else support_diagnostics(features,bank)
            adequate=adequacy_field(post,config.get('adequacy',DEFAULT_SIGMOID))
            mean_adequacy=None if adequate is None else float(adequate.mean())
            native_adequacy=None if adequate is None else restore_map(adequate,(16,16),size)
            selected_ids=[] if selected is None else [candidates[selected].image]
            support_ids=[s.image for s in supports]+selected_ids
            if len(support_ids)!=shots+len(selected_ids) or len(selected_ids)>1 or len(set(support_ids))!=len(support_ids):
                raise ValueError('Acquisition budget/uniqueness violation')
            directory=episode/policy;directory.mkdir(exist_ok=True)
            path=directory/f'query-{index:03d}.npz'
            if shutil.disk_usage(directory).free < after.nbytes*4+256*1024**2:
                raise OSError('Insufficient disk for pilot map exports')
            fields={'defect_map':after}
            if native_adequacy is not None: fields['support_adequacy_diagnostic']=native_adequacy
            save_maps(path,**fields)
            diagnostic_after=save_diagnostics(directory/f'query-{index:03d}_diagnostics_after.npz',post)
            image_after=image_score(scores)
            decision,evidence=action(image_after,mean_adequacy,cutoff['image_threshold'],
                                     config.get('adequacy',DEFAULT_SIGMOID)['adequacy_threshold'])
            prediction=asdict(Prediction(dataset,category,query.image,image_after,str(path),
                                         {'before':diagnostic_before,'after':diagnostic_after,
                                          'adequacy_kind':config.get('adequacy',DEFAULT_SIGMOID)['kind']},
                                         0. if selected is None else predicted[selected],decision,
                                         support_ids,selected_ids,
                                         {'defect_map':True,'reference_diagnostics':True,'support_adequacy':adequate is not None,
                                          'predicted_intervention_benefit':True,'predicted_patch_benefit':False,'action':True},
                                         {'query_feature_or_cache':feature_seconds,'shared_support_features':support_seconds,
                                          'shared_pool_features':pool_seconds,'shared_all_candidate_patch_probes':probes_seconds,
                                          'selector':selection_times.get(policy),'selected_reference_scoring':0. if selected is None else probe_times[selected],
                                          'post_update_diagnostics_restore_export':time.perf_counter()-tick}))
            benefit=0. if selected is None else benefits[selected]
            preservation=defect_preservation(before,after,truth,image_before,image_after,
                                             cutoff['image_threshold'],cutoff['pixel_threshold'])
            prediction.update(policy=policy,protocol=plan['protocol'],seed=seed,shots=shots,
                              initial_support_ids=[s.image for s in supports],candidate_pool_ids=[s.image for s in candidates],
                              candidate_pool_size=len(candidates),added_normal_references=len(selected_ids),
                              initial_image_score=image_before,mean_support_adequacy=mean_adequacy,raw_defect_evidence=evidence,
                              observed_benefit=benefit,offline_loss_before=before_loss,
                              harmful_intervention=benefit < -1e-8,beneficial_intervention=benefit>1e-8,
                              oracle_gap=float(max(benefits)-benefit),preservation=preservation,
                              native_truth_is_anomalous=bool(truth.any()),query_label_used_for_selection=policy=='oracle',
                              experiment_role='validation_evaluation_only',never_use_for_training=True,
                              model_selected_using_these_queries=False,thresholds_selected_using_these_queries=False,
                              candidate_global_scans=0 if policy in {'none','random'} else len(candidates),
                              deployment_candidate_patch_probes=len(candidates) if policy in {'learned','oracle'} else int(selected is not None),
                              shared_offline_candidate_probes=len(candidates),feature_cache_hit=cached,feature_cache_key=key,
                              original_size=list(size),map_storage='explicit float16; metrics use float32 native maps',
                              selected_memory_bytes=sum(ref.numel()*ref.element_size() for ref in bank),
                              predicted_benefit_semantics='signed scalar loss reduction; no spatial benefit or calibrated probability',
                              efficiency_scope='shared pilot timings; not isolated policy deployment benchmarks',
                              decision_threshold_origin=cutoff,adequacy_threshold_origin='predeclared untrained diagnostic; no validated adequacy event')
            accumulator=accumulators[policy]
            accumulator['rows'].append(prediction);accumulator['maps'].append(after);accumulator['truths'].append(truth)
            accumulator['labels'].append(bool(truth.any()));accumulator['scores'].append(image_after)
            accumulator['adequacy'].append(mean_adequacy)
            all_predictions.append(prediction)
        print(json.dumps({'scored_protocol':plan['protocol'],'dataset':dataset,'seed':seed,'shots':shots,
                          'query_index':index,'query_count':len(queries)}),flush=True)
    episode_metrics=[]
    for policy,accumulator in accumulators.items():
        image=thresholded_detection_metrics(accumulator['labels'],accumulator['scores'],cutoff['image_threshold'])
        pixel=localization_metrics(accumulator['truths'],accumulator['maps'],cutoff['pixel_threshold'],
                                  fpr_limit=config['pixel_fpr_limit'],max_thresholds=256)
        rows=accumulator['rows']
        errors=(np.asarray(accumulator['scores'])>=cutoff['image_threshold'])!=np.asarray(accumulator['labels'])
        confidence=np.asarray([1. if value is None else value for value in accumulator['adequacy']])
        reliability=risk_coverage(errors,confidence)
        if any(value is None for value in accumulator['adequacy']):
            reliability['constant_ranking_fallback']='diagnostic combination disabled; constant confidence, no learned reliability ranking'
        metric={'dataset':dataset,'category':category,'seed':seed,'shots':shots,'protocol':plan['protocol'],'policy':policy,
                'query_count':len(rows),'image_metrics':image,'localization_metrics':pixel,'risk_coverage':reliability,
                'mean_observed_benefit':float(np.mean([row['observed_benefit'] for row in rows])),
                'harmful_interventions':sum(row['harmful_intervention'] for row in rows),
                'detected_to_missed':sum(row['preservation']['detected_to_missed'] for row in rows),
                'added_reference_events':sum(row['added_normal_references'] for row in rows),
                'coverage':sum(row['action']!='unresolved/reference-insufficient' for row in rows)/len(rows),
                'candidate_pool_size':len(candidates),'acquisition_budget':0 if policy=='none' else 1,
                'oracle_is_deployable':False,'probability_calibration_evaluated':False}
        write_json(episode/policy/'metrics.json',metric)
        write_jsonl(episode/policy/'predictions.jsonl',rows)
        episode_metrics.append(metric)
    write_jsonl(episode/'candidate_evaluation.jsonl',candidate_records)
    write_jsonl(episode/'all_predictions.jsonl',all_predictions)
    dependencies={str(path):sha256(path) for path in sorted(input_paths)}
    files=[str(path.relative_to(episode)) for path in sorted(episode.rglob('*')) if path.is_file() and path.name!='completion.json']
    complete_stage(episode,files,{'input_sha256':dependencies,'input_verification_version':1,
                                  'implementation_sha256':implementation_hashes(),
                                  'git_revisions':{'/workspace/.cache/dinov2-source':extractor.source_commit}})
    return episode_metrics,all_predictions


def feasibility_gate(config,predictions):
    real=[row for row in predictions if row['protocol']=='paired_validation']
    by_case={}
    for row in real:
        key=(row['dataset'],row['category'],row['seed'],row['shots'],row['image_id'])
        by_case.setdefault(key,{})[row['policy']]=row
    policy_means={policy:float(np.mean([case[policy]['observed_benefit'] for case in by_case.values()]))
                  for policy in ['random','nearest_global','diversity','learned','oracle']}
    strongest=max(['random','nearest_global','diversity'],key=policy_means.get)
    harm={policy:sum(case[policy]['harmful_intervention'] for case in by_case.values()) for policy in ['random','nearest_global','diversity','learned']}
    lost=sum(case['learned']['preservation']['detected_to_missed'] for case in by_case.values())
    utility_pass=policy_means['learned']>0 and policy_means['learned']>policy_means[strongest]+config['gate']['utility_margin']
    harm_pass=config['gate']['allow_increased_harm'] or harm['learned']<=harm[strongest]
    preservation_pass=config['gate']['allow_new_missed_defects'] or lost==0
    strata=[]
    for dataset in config['validation_categories']:
        for shots in config['evaluation_shots']:
            cases=[case for key,case in by_case.items() if key[0]==dataset and key[3]==shots]
            means={policy:float(np.mean([case[policy]['observed_benefit'] for case in cases])) for policy in ['random','nearest_global','diversity','learned','oracle']}
            best=max(['random','nearest_global','diversity'],key=means.get)
            harmful={policy:sum(case[policy]['harmful_intervention'] for case in cases) for policy in ['random','nearest_global','diversity','learned']}
            anomaly=[case for case in cases if case['learned']['native_truth_is_anomalous']]
            recall_changes=[case['learned']['preservation']['defect_pixel_recall_after']-case['learned']['preservation']['defect_pixel_recall_before'] for case in anomaly]
            iou_changes=[case['learned']['preservation']['iou_change'] for case in anomaly if case['learned']['preservation']['iou_change'] is not None]
            stratum_utility=means['learned']>0 and means['learned']>means[best]+config['gate']['utility_margin']
            stratum_harm=config['gate']['allow_increased_harm'] or harmful['learned']<=harmful[best]
            new_misses=sum(case['learned']['preservation']['detected_to_missed'] for case in cases)
            base_detected=sum(case['none']['raw_defect_evidence'] for case in anomaly)
            stratum_preserved=(new_misses==0 and base_detected>0 and
                                all(change>=-1e-12 for change in recall_changes) and
                                (not iou_changes or np.mean(iou_changes)>=-1e-12))
            strata.append({'dataset':dataset,'shots':shots,'mean_observed_benefit':means,'strongest_simple':best,
                           'harmful_interventions':harmful,'utility_pass':stratum_utility,'harm_pass':stratum_harm,
                           'preservation_pass':stratum_preserved,'baseline_detected_anomalous_inspections':base_detected,
                           'learned_detected_to_missed':new_misses,
                           'mean_defect_pixel_recall_change':float(np.mean(recall_changes)) if recall_changes else None,
                           'mean_defect_iou_change':float(np.mean(iou_changes)) if iou_changes else None})
    utility_pass=utility_pass and all(row['utility_pass'] for row in strata)
    harm_pass=harm_pass and all(row['harm_pass'] for row in strata)
    preservation_pass=preservation_pass and all(row['preservation_pass'] for row in strata)
    stress={}
    for row in predictions:
        if row['protocol'] in {'missing_support','coverage_control'}:
            key=(row['dataset'],row['category'],row['seed'],row['shots'],row['image_id'])
            stress.setdefault(key,{})[(row['protocol'],row['policy'])]=row
    missing_checks=[]
    for dataset in config['validation_categories']:
        for shots in config['evaluation_shots']:
            cases=[case for key,case in stress.items() if key[0]==dataset and key[3]==shots]
            omitted=sum(case[('missing_support','none')]['raw_defect_evidence'] for case in cases)
            covered=sum(case[('coverage_control','none')]['raw_defect_evidence'] for case in cases)
            acquired=sum(case[('missing_support','learned')]['raw_defect_evidence'] for case in cases)
            missing_checks.append({'dataset':dataset,'shots':shots,'normal_inspections':len(cases),
                                   'omitted_support_false_alarms':omitted,'covered_support_false_alarms':covered,
                                   'after_learned_acquisition_false_alarms':acquired,
                                   'omission_increased_false_alarms':omitted>covered,
                                   'acquisition_reduced_omission_false_alarms':acquired<omitted,
                                   'matched_control_budget':'same k, pool, query, seed; exactly one initial reference replaced'})
    missing_pass=all(row['omission_increased_false_alarms'] and row['acquisition_reduced_omission_false_alarms'] for row in missing_checks)
    comparisons={}
    for comparator in ['random','nearest_global','diversity']:
        comparisons[comparator]={}
        for shots in config['evaluation_shots']:
            paired=[]
            for (dataset,category,seed,k,query),case in by_case.items():
                if k==shots:
                    paired.append({'dataset':dataset,'category':category,'seed':seed,'query_id':query,
                                   'paired_difference':case['learned']['observed_benefit']-case[comparator]['observed_benefit']})
            comparisons[comparator][str(shots)]=paired_crossed_bootstrap(paired,n_bootstrap=config['bootstrap_samples'],seed=0)
    reasons=[]
    if not utility_pass: reasons.append('Learned acquisition did not exceed the strongest simple selector on declared mean loss benefit')
    if not harm_pass: reasons.append('Learned acquisition increased harmful intervention count versus the strongest simple selector')
    if not preservation_pass: reasons.append('The locked-cutoff image/pixel sensitivity, overlap, or nonzero-baseline-detection preservation gate failed')
    if not missing_pass: reasons.append('Matched missing-support slices did not all show both increased false alarms from omission and reduction from learned acquisition')
    return {'advance_to_full_experiments':utility_pass and harm_pass and preservation_pass and missing_pass,
            'mean_observed_benefit':policy_means,'strongest_simple_selector':strongest,'harmful_interventions':harm,
            'learned_detected_to_missed':lost,'utility_gate_pass':utility_pass,'harm_gate_pass':harm_pass,
            'defect_preservation_gate_pass':preservation_pass,'stop_reasons':reasons,
            'per_dataset_shot_gates':strata,'missing_support_gate_pass':missing_pass,'matched_missing_support_checks':missing_checks,
            'preservation_definition':'no new image misses, nonzero baseline detection, no defect pixel recall loss, and no mean defect IoU deterioration',
            'paired_crossed_bootstrap':comparisons,'tuning_after_gate':False,
            'scope':'small fixed validation categories, reused queries/support draws; descriptive evidence only'}


def run(config,max_episodes=None):
    validate_pilot_config(config)
    if not verify_stage(Path(config['output'])/'targets',require_inputs=True) or not verify_stage(Path(config['output'])/'models',require_inputs=True):
        raise ValueError('Verified source targets and fitted models must precede evaluation')
    output=Path(config['output'])/'evaluation';output.mkdir(parents=True,exist_ok=True)
    write_json(output/'config.json',config)
    if verify_stage(output,require_inputs=True):
        print(json.dumps({'resume':'completed artifact verification','gate':json.loads((output/'gate.json').read_text())}),flush=True)
        return
    report=json.loads((Path(config['output'])/'models/training_report.json').read_text())
    model_path=Path(config['output'])/'models'/(report['primary_model']+'.json')
    model=BenefitModel.load(model_path)
    extractor=FrozenDINOv2(config['feature_cache'])
    data=load_samples(config);input_paths={model_path,
                                         Path('/workspace/.cache/torch/hub/checkpoints/dinov2_vitb14_pretrain.pth'),
                                         Path('/workspace/reports/real_weight_verification.json'),
                                         Path(config['output'])/'models/training_report.json',
                                         Path(config['output'])/'targets/completion.json'}
    cutoffs=calibrate(config,extractor,data,input_paths)
    write_json(output/'calibration.json',cutoffs)
    plans=paired_plans(config,data)+omission_plans(config,extractor,data,input_paths)
    write_json(output/'split_manifest.json',plans)
    metrics=[];predictions=[]
    completed=0
    for plan in plans:
        for shots in config['evaluation_shots']:
            m,p=evaluate_plan(config,plan,shots,extractor,model,cutoffs[f"{plan['dataset']}:{plan['seed']}:{shots}"],
                               data,output,input_paths)
            metrics.extend(m);predictions.extend(p)
            completed+=1
            print(json.dumps({'completed_dataset':plan['dataset'],'protocol':plan['protocol'],'seed':plan['seed'],'shots':shots,
                              'policy_episodes':len(m)}),flush=True)
            if max_episodes is not None and completed>=max_episodes:
                print(json.dumps({'checkpoint_stop':True,'completed_verified_episodes':completed,
                                  'continue':'rerun without --max-episodes; completed episodes are hash/input/code verified'}),flush=True)
                return
    gate=feasibility_gate(config,predictions)
    write_json(output/'episodes.json',metrics);write_jsonl(output/'predictions.jsonl',predictions)
    write_json(output/'gate.json',gate)
    write_json(output/'provenance.json',{'checkpoint_sha256':extractor.checkpoint_hash,'source_commit':extractor.source_commit,
                                       'preprocessing_version':PREPROCESS_VERSION,'feature_layer_configuration':LAYER_CONFIGURATION,
                                       'implementation_sha256':implementation_hashes(),'model_name':model.name,'device':'cpu',
                                       'final_categories_evaluated':[],'private_test_data_or_results':False,
                                       'native_test_labels_used_for_model_or_threshold_selection':False})
    inputs={str(path):sha256(path) for path in sorted(input_paths)}
    names=[str(path.relative_to(output)) for path in sorted(output.rglob('*')) if path.is_file() and path.name!='completion.json']
    complete_stage(output,names,{'input_sha256':inputs,'input_verification_version':1,
                                'implementation_sha256':implementation_hashes(),
                                'git_revisions':{'/workspace/.cache/dinov2-source':extractor.source_commit}})
    print(json.dumps({'completed_prediction_records':len(predictions),'gate':gate}),flush=True)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    parser.add_argument('--max-episodes',type=int,help='Stop at an episode checkpoint; used to verify safe continuation')
    args=parser.parse_args()
    if args.max_episodes is not None and args.max_episodes<1: raise ValueError('Positive checkpoint count required')
    run(json.loads(args.config.read_text()),max_episodes=args.max_episodes)


if __name__=='__main__':
    main()
