"""Independent real-weight cache-bypass check of two completed query episodes."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch

from safe_iad.acquisition import InferenceInputs,global_descriptor,select_learned_reference
from safe_iad.benefit_model import BenefitModel
from safe_iad.counterfactual import FEATURE_NAMES,inference_feature_vector,support_diagnostics
from safe_iad.experiment_io import image_score,read_jsonl,write_json
from safe_iad.patch_nn import FrozenDINOv2,LAYER_CONFIGURATION,PREPROCESS_VERSION,patch_nearest_neighbor,restore_map
from safe_iad.support_decision import DEFAULT_SIGMOID,adequacy_field
from safe_iad.verify_dataset import discover


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--cache',type=Path,required=True,help='New empty directory: every feature must be recomputed')
    args=parser.parse_args()
    if args.cache.exists() and any(args.cache.iterdir()):
        raise ValueError('Use a new empty cache to prove backbone recomputation')
    config=json.loads((args.run/'evaluation/config.json').read_text())
    rows=read_jsonl(args.run/'evaluation/predictions.jsonl')
    primary=json.loads((args.run/'models/training_report.json').read_text())['primary_model']
    model=BenefitModel.load(args.run/'models'/(primary+'.json'))
    extractor=FrozenDINOv2(args.cache)
    checks=[]
    for dataset in config['validation_categories']:
        eligible=[row for row in rows if row['dataset']==dataset and row['protocol']=='paired_validation'
                  and row['policy']=='learned' and row['native_truth_is_anomalous']]
        transitioned=[row for row in eligible if row['preservation']['detected_to_missed']]
        row=(transitioned or eligible)[0]
        root=Path(config['roots'][dataset])
        samples,_,issues,_=discover(root,dataset,None)
        if issues:raise ValueError('Dataset discovery failed')
        lookup={sample.image:sample for sample in samples}
        def fresh(identifier):
            features,size,cached,key=extractor.extract(dataset,lookup[identifier],root)
            if cached:raise ValueError('Independent probe unexpectedly hit its new cache')
            with np.load(Path(config['feature_cache'])/(key+'.npz'),allow_pickle=False) as old:
                if not np.array_equal(features.numpy(),old['features']):
                    raise ValueError('Fresh pretrained features differ from evaluated float32 features')
            return features,size
        references=[fresh(identifier)[0] for identifier in row['initial_support_ids']]
        candidate_features=[fresh(identifier)[0] for identifier in row['candidate_pool_ids']]
        query,size=fresh(row['image_id'])
        diagnostics=support_diagnostics(query,references)
        before_scores=diagnostics['nearest_distance']
        vectors=[];scores=[]
        for candidate in candidate_features:
            after=patch_nearest_neighbor(query,torch.cat(references+[candidate]))
            scores.append(after)
            vectors.append(inference_feature_vector(query,references,candidate,diagnostics,after))
        inputs=InferenceInputs(global_descriptor(query),torch.stack([global_descriptor(ref) for ref in references]),
                               torch.stack([global_descriptor(ref) for ref in candidate_features]),
                               tuple(row['candidate_pool_ids']),row['seed'],row['image_id'])
        contract={'checkpoint_sha256':extractor.checkpoint_hash,'source_commit':extractor.source_commit,
                  'preprocessing_version':PREPROCESS_VERSION,'feature_layer_configuration':LAYER_CONFIGURATION,
                  'loss_specification':config['loss']}
        selection,estimated=select_learned_reference(inputs,vectors,model,budget=1,feature_names=FEATURE_NAMES,provenance=contract)
        if row['selected_reference_ids']!=[row['candidate_pool_ids'][selection]]:
            raise ValueError('Fresh learned selection changed')
        after_scores=scores[selection]
        if image_score(before_scores)!=row['initial_image_score'] or image_score(after_scores)!=row['image_anomaly_score']:
            raise ValueError('Fresh float32 image scores changed')
        if estimated[selection]!=row['predicted_intervention_benefit']:
            raise ValueError('Fresh signed-benefit estimate changed')
        episode=Path(row['defect_map']).parent.parent
        manifest=json.loads((episode/'manifest.json').read_text())
        index=manifest['query_ids'].index(row['image_id'])
        with np.load(episode/f'query-{index:03d}_before.npz',allow_pickle=False) as saved:
            if not np.array_equal(restore_map(before_scores,(16,16),size).astype(np.float16),saved['defect_map']):
                raise ValueError('Fresh pre-intervention map changed')
        with np.load(row['defect_map'],allow_pickle=False) as saved:
            if not np.array_equal(restore_map(after_scores,(16,16),size).astype(np.float16),saved['defect_map']):
                raise ValueError('Fresh post-intervention map changed')
            post=support_diagnostics(query,references+[candidate_features[selection]])
            adequate=adequacy_field(post,config.get('adequacy',DEFAULT_SIGMOID))
            if adequate is not None and not np.array_equal(restore_map(adequate,(16,16),size).astype(np.float16),saved['support_adequacy_diagnostic']):
                raise ValueError('Fresh diagnostic field changed')
        checks.append({'dataset':dataset,'image_id':row['image_id'],'seed':row['seed'],'shots':row['shots'],
                       'backbone_cache_bypassed':True,'float32_features_bitwise_equal':True,
                       'pre_post_float16_maps_bitwise_equal':True,'image_scores_exact_equal':True,
                       'selected_reference_and_benefit_exact_equal':True,'adequacy_map_bitwise_equal':True,
                       'retained_detected_to_missed_case':row['preservation']['detected_to_missed']})
        print(json.dumps(checks[-1]),flush=True)
    report={'status':'passed','checkpoint_sha256':extractor.checkpoint_hash,'source_commit':extractor.source_commit,
            'model':model.name,'real_query_probes':checks,
            'scope':'one actual anomalous query per main dataset with newly recomputed features; not a full independent episode rerun'}
    write_json(args.output,report)


if __name__=='__main__':
    main()
