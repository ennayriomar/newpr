"""Paired one-step budgeted acquisition; oracle is offline evaluation only."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import shutil
import time

import numpy as np
from PIL import Image
from sklearn.metrics import average_precision_score, roc_auc_score
import torch

from .acquisition import InferenceInputs, add_reference, global_descriptor, select_reference
from .counterfactual import evaluation_oracle, inference_feature_vector, offline_loss, support_diagnostics
from .patch_nn import FrozenDINOv2, patch_nearest_neighbor, restore_map, validate_episode
from .run_baseline_pilot import Prediction
from .splits import validate_partition
from .verify_dataset import discover


POLICIES=['none','random','nearest_global','diversity','oracle']


def image_score(scores):
    return float(torch.topk(scores,max(1,int(np.ceil(len(scores)*.01)))).values.mean())


def save_diagnostics(path,diagnostics):
    fields={key:value.numpy() for key,value in diagnostics.items() if value is not None}
    np.savez_compressed(path,**fields)
    return {'path':str(path),'loo_defined':diagnostics['loo_sensitivity'] is not None,'loo_missing':'loo_sensitivity field absent with loo_valid=false' if diagnostics['loo_sensitivity'] is None else None,'dispersion_direction':'not assumed to imply adequacy'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    if config['initial_shots']!=1 or config['acquisition_budget']!=1:
        raise ValueError('This feasibility pilot validates only k=1, one-step b=1.')
    output=Path(config['output'])/'evaluation'
    output.mkdir(parents=True,exist_ok=True)
    saved_config=output/'config.json'
    if saved_config.exists() and json.loads(saved_config.read_text())!=config:
        raise ValueError('Output contains a different configuration.')
    saved_config.write_text(json.dumps(config,indent=2)+'\n')
    extractor=FrozenDINOv2(config['feature_cache'])
    results=[]
    for dataset,category in config['evaluation_categories'].items():
        if category not in config['category_roles'][dataset]['final_test']:
            raise ValueError('Evaluation category must be reserved for final evaluation.')
        root=Path(config['roots'][dataset])
        samples,_,issues,_=discover(root,dataset,None)
        if issues:
            raise ValueError('Dataset discovery failed.')
        lookup={s.image:s for s in samples}
        for seed in config['seeds']:
            baseline=Path(config['baseline_output'])/dataset/category/f'seed-{seed}_k-1'
            manifest=json.loads((baseline/'manifest.json').read_text())
            supports=[lookup[i] for i in manifest['support_ids']]
            queries=[lookup[i] for i in manifest['query_ids']]
            validate_episode(supports,queries,1)
            eligible=sorted([s for s in samples if s.category==category and s.split=='train' and s.label=='normal' and s.image not in manifest['support_ids']],key=lambda s:s.image)
            indices=np.random.default_rng(seed+777).choice(len(eligible),size=config['candidate_pool_size'],replace=False)
            candidates=[eligible[i] for i in indices]
            candidate_ids=[c.image for c in candidates]
            validate_partition(manifest['support_ids'],candidate_ids,manifest['query_ids'])
            episode=output/dataset/category/f'seed-{seed}_k-1_b-1'
            episode.mkdir(parents=True,exist_ok=True)
            episode_manifest={'dataset':dataset,'category':category,'seed':seed,'protocol':'B_budgeted_reference_acquisition','budget_unit':'per query inspection; reset to the same initial S for each query; no cumulative bank across queries','initial_support_ids':manifest['support_ids'],'candidate_ids':candidate_ids,'query_ids':manifest['query_ids'],'allowed_additional_references':1,'forced_acquisition_count':1,'loss_specification':config['loss'],'loss_choice':'predeclared before acquisition results; not tuned with evaluation labels','candidate_information':'Verified-normal training IDs, frozen patch features and mean-normalized-patch global descriptors; same pool for every policy. Unselected patches never enter the detector memory.','oracle_information':'Query masks/labels only for offline counterfactual losses; never for deployed policies or training targets.','base_detector_checkpoint_sha256':extractor.checkpoint_hash,'no_acquisition_baseline':'initial k=1 memory; pool scans excluded from detector memory; not a strict-k-shot claim for acquisition policies'}
            (episode/'manifest.json').write_text(json.dumps(episode_manifest,indent=2)+'\n')
            references=[extractor.extract(dataset,s,root)[0] for s in supports]
            extraction_start=time.perf_counter()
            candidate_data=[extractor.extract(dataset,c,root) for c in candidates]
            pool_seconds=time.perf_counter()-extraction_start
            candidate_features=[item[0] for item in candidate_data]
            candidate_globals=torch.stack([global_descriptor(f) for f in candidate_features])
            support_globals=torch.stack([global_descriptor(f) for f in references])
            baseline_predictions=[json.loads(line) for line in (baseline/'predictions.jsonl').read_text().splitlines()]
            accumulators={policy:{'predictions':[],'scores':[],'labels':[],'maps':[],'truth':[]} for policy in POLICIES}
            candidate_rows=[]
            for index,query in enumerate(queries):
                feature_start=time.perf_counter()
                features,size,cached,key=extractor.extract(dataset,query,root)
                feature_seconds=time.perf_counter()-feature_start
                opaque_id=hashlib.sha256(f'{dataset}:{query.image}'.encode()).hexdigest()
                inputs=InferenceInputs(global_descriptor(features),support_globals,candidate_globals,tuple(candidate_ids),seed,opaque_id)
                # All deployed selections occur before any query truth is opened.
                selected={policy:select_reference(policy,inputs,budget=0 if policy=='none' else 1) for policy in POLICIES if policy!='oracle'}
                diagnostics=support_diagnostics(features,references)
                before_scores=diagnostics['nearest_distance']
                before=restore_map(before_scores,(16,16),size)
                with np.load(baseline_predictions[index]['defect_map'],allow_pickle=False) as previous:
                    if not np.array_equal(before,previous['defect_map']):
                        raise ValueError('Base detector differs from the paired baseline.')
                diag_before=save_diagnostics(episode/f'query-{index:03d}_diagnostics_before.npz',diagnostics)
                probe_start=time.perf_counter()
                after_scores=[patch_nearest_neighbor(features,torch.cat(references+[candidate])) for candidate in candidate_features]
                probe_seconds=time.perf_counter()-probe_start
                vectors=[inference_feature_vector(features,references,candidate,diagnostics,score) for candidate,score in zip(candidate_features,after_scores)]
                # Offline evaluation begins here. Query truth cannot reach policy inputs.
                if query.mask:
                    with Image.open(root/query.mask) as mask:
                        truth=np.asarray(mask)>0
                else:
                    truth=np.zeros((size[1],size[0]),dtype=bool)
                before_loss=offline_loss(before,truth,config['loss'],image_score=image_score(before_scores))
                candidate_losses=[offline_loss(restore_map(score,(16,16),size),truth,config['loss'],image_score=image_score(score)) for score in after_scores]
                benefits=[before_loss-loss for loss in candidate_losses]
                selected['oracle']=evaluation_oracle(benefits)
                oracle_benefit=max(benefits)
                for candidate,vector,benefit in zip(candidates,vectors,benefits):
                    candidate_rows.append({'experiment_role':'final_evaluation_only','dataset':dataset,'category':category,'seed':seed,'query_id':query.image,'candidate_id':candidate.image,'offline_observed_benefit':benefit,'inference_only_features':vector,'never_use_for_training':True})
                for policy in POLICIES:
                    selection=selected[policy]
                    scores=before_scores if selection is None else after_scores[selection]
                    after=before if selection is None else restore_map(scores,(16,16),size)
                    support_ids=manifest['support_ids'] if selection is None else add_reference(manifest['support_ids'],candidate_ids[selection],budget=1)
                    selected_ids=[] if selection is None else [candidate_ids[selection]]
                    added=0 if selection is None else 1
                    if len(support_ids)!=1+added or added>1:
                        raise ValueError('Reference budget accounting failed.')
                    directory=episode/policy
                    directory.mkdir(exist_ok=True)
                    path=directory/f'query-{index:03d}.npz'
                    if shutil.disk_usage(directory).free-after.nbytes<2*1024**3:
                        raise OSError('Insufficient reserved disk space for acquisition maps.')
                    np.savez_compressed(path,defect_map=after)
                    post=diagnostics if selection is None else support_diagnostics(features,references+[candidate_features[selection]])
                    diag_post=save_diagnostics(directory/f'query-{index:03d}_diagnostics_after.npz',post)
                    benefit=0. if selection is None else benefits[selection]
                    loss=before_loss if selection is None else candidate_losses[selection]
                    prediction=asdict(Prediction(dataset,category,query.image,image_score(scores),str(path),{'before':diag_before,'after':diag_post},None,None,support_ids,selected_ids,{'defect_map':True,'reference_diagnostics':True,'support_adequacy':False,'predicted_intervention_benefit':False,'action':False}, {'query_feature_or_cache':feature_seconds,'shared_pool_feature_extraction':pool_seconds,'shared_offline_candidate_patch_probe':probe_seconds}))
                    prediction.update(policy=policy,seed=seed,initial_support_ids=manifest['support_ids'],budget_unit=episode_manifest['budget_unit'],image_score_before=image_score(before_scores),normal_image_score_drop=float(image_score(before_scores)-image_score(scores)) if not truth.any() else None,experiment_role='final_evaluation_only',offline_loss_before=before_loss,offline_loss_after=loss,offline_observed_benefit=benefit,oracle_gap=oracle_benefit-benefit if selection is not None else None,beneficial_intervention=benefit>1e-8,harmful_intervention=benefit<-1e-8,added_normal_references=added,candidate_pool_size=len(candidates),candidate_global_scans=0 if policy in {'none','random'} else len(candidates),deployment_candidate_patch_scans=0 if policy=='none' else (len(candidates) if policy=='oracle' else 1),offline_candidates_probed=len(candidates),pool_feature_cache_hits=sum(item[2] for item in candidate_data),query_feature_cache_hit=cached,feature_cache_key=key,original_size=list(size),query_label_used_for_selection=(policy=='oracle'))
                    if truth.any():
                        prediction['defect_region_score_before']=float(before[truth].mean())
                        prediction['defect_region_score_after']=float(after[truth].mean())
                        prediction['defect_region_score_drop']=prediction['defect_region_score_before']-prediction['defect_region_score_after']
                    else:
                        prediction['defect_region_score_before']=prediction['defect_region_score_after']=prediction['defect_region_score_drop']=None
                    accumulator=accumulators[policy]
                    accumulator['predictions'].append(prediction)
                    accumulator['scores'].append(prediction['image_anomaly_score'])
                    accumulator['labels'].append(query.label=='anomaly')
                    accumulator['maps'].append(after.ravel())
                    accumulator['truth'].append(truth.ravel())
            with (episode/'evaluation_candidates.jsonl').open('w') as f:
                for row in candidate_rows:
                    f.write(json.dumps(row)+'\n')
            for policy,accumulator in accumulators.items():
                rows=accumulator['predictions']
                truth=np.concatenate(accumulator['truth'])
                score=np.concatenate(accumulator['maps'])
                metrics={'dataset':dataset,'category':category,'seed':seed,'policy':policy,'initial_shots':1,'allowed_acquisition_budget':0 if policy=='none' else 1,'budget_unit':episode_manifest['budget_unit'],'candidate_pool_size':len(candidates),'queries':len(queries),'added_normal_references':sum(row['added_normal_references'] for row in rows),'image_auroc':float(roc_auc_score(accumulator['labels'],accumulator['scores'])),'image_ap':float(average_precision_score(accumulator['labels'],accumulator['scores'])),'pixel_auroc':float(roc_auc_score(truth,score)),'pixel_ap':float(average_precision_score(truth,score)),'mean_offline_benefit':float(np.mean([row['offline_observed_benefit'] for row in rows])),'harmful_interventions':sum(row['harmful_intervention'] for row in rows),'beneficial_interventions':sum(row['beneficial_intervention'] for row in rows),'oracle_is_deployable':False,'loss_specification':config['loss'],'scope':'Locked small feasibility evaluation; no threshold or model selection; no confidence interval.'}
                directory=episode/policy
                (directory/'metrics.json').write_text(json.dumps(metrics,indent=2)+'\n')
                with (directory/'predictions.jsonl').open('w') as f:
                    for row in rows:
                        f.write(json.dumps(row)+'\n')
                results.append(metrics)
                print(json.dumps(metrics),flush=True)
    (output/'episodes.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'completed_policy_episodes':len(results),'protocol':'B_one_step_budgeted','initial_shots':1,'additional_references':1}),flush=True)


if __name__=='__main__':
    main()
