"""Offline U(q,S,r) supervision from source-training normals/synthetic queries only."""
import argparse
import hashlib
import io
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageEnhance
import torch

from .counterfactual import FEATURE_NAMES, inference_feature_vector, offline_loss, support_diagnostics
from .patch_nn import FrozenDINOv2, LAYER_CONFIGURATION, PREPROCESS_VERSION, patch_nearest_neighbor, restore_map
from .splits import prepare_manifests, require_training_source, validate_partition
from .verify_dataset import Sample, discover


def write_preserving(path, image):
    buffer=io.BytesIO()
    image.save(buffer,format='PNG')
    data=buffer.getvalue()
    path.parent.mkdir(parents=True,exist_ok=True)
    if path.exists():
        if path.read_bytes()!=data:
            raise ValueError(f'Refusing to overwrite a different generated file: {path}')
    else:
        path.write_bytes(data)


def synthetic_query(dataset, source, root, generated_root, seed):
    """Deterministic cut/paste with rotated, contrast-adjusted source pixels.

    This is synthetic supervision, not a verified real industrial defect.
    """
    with Image.open(root/source.image) as original:
        image=original.convert('RGB')
    width,height=image.size
    box_width,box_height=max(2,width//6),max(2,height//6)
    salt=int.from_bytes(hashlib.sha256(source.image.encode()).digest()[:4],'little')
    rng=np.random.default_rng(seed+salt)
    sx,sy=int(rng.integers(width-box_width)),int(rng.integers(height-box_height))
    dx,dy=int(rng.integers(width-box_width)),int(rng.integers(height-box_height))
    patch=image.crop((sx,sy,sx+box_width,sy+box_height)).transpose(Image.Transpose.ROTATE_180)
    patch=ImageEnhance.Contrast(patch).enhance(1.5)
    modified=image.copy()
    modified.paste(patch,(dx,dy))
    mask=np.zeros((height,width),dtype=np.uint8)
    mask[dy:dy+box_height,dx:dx+box_width]=255
    stem=f'{Path(source.image).stem}_seed-{seed}_cutpaste-v1'
    relative=Path(dataset)/source.category/(stem+'.png')
    mask_relative=relative.with_name(stem+'_mask.png')
    write_preserving(generated_root/relative,modified)
    write_preserving(generated_root/mask_relative,Image.fromarray(mask))
    return Sample(source.category,'meta_train_synthetic','synthetic_anomaly',str(relative),str(mask_relative)), mask>0, {'synthetic_version':'cutpaste-v1','source_image_id':source.image,'source_rect':[sx,sy,box_width,box_height],'destination_rect':[dx,dy,box_width,box_height],'rotation':180,'contrast_factor':1.5}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',type=Path,required=True)
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    if config['initial_shots']!=1 or config['acquisition_budget']!=1:
        raise ValueError('Initial feasibility run is one-step from one reference.')
    output=Path(config['output'])/'training_targets'
    output.mkdir(parents=True,exist_ok=True)
    saved_config=output/'config.json'
    if saved_config.exists() and json.loads(saved_config.read_text())!=config:
        raise ValueError('Training-target output contains a different configuration.')
    saved_config.write_text(json.dumps(config,indent=2)+'\n')
    episodes=prepare_manifests(config)
    extractor=FrozenDINOv2(config['feature_cache'])
    output=Path(config['output'])/'training_targets'
    output.mkdir(parents=True,exist_ok=True)
    generated=Path(config['generated_root'])
    all_rows=[]
    for episode in episodes:
        dataset,root=episode['dataset'],Path(episode['root'])
        samples,_,_,_=discover(root,dataset,None)
        lookup={s.image:s for s in samples}
        supports=[lookup[i] for i in episode['support_ids']]
        candidates=[lookup[i] for i in episode['candidate_ids']]
        sources=[lookup[i] for i in episode['query_source_ids']]
        validate_partition(episode['support_ids'],episode['candidate_ids'],episode['all_reserved_query_source_ids'])
        references=[extractor.extract(dataset,s,root)[0] for s in supports]
        candidate_features=[extractor.extract(dataset,s,root)[0] for s in candidates]
        episode_rows=[]
        for source in sources:
            require_training_source(dataset,source,config)
            normal_features,size,_,_=extractor.extract(dataset,source,root)
            synthetic,mask,provenance=synthetic_query(dataset,source,root,generated,episode['seed'])
            synthetic_features,synthetic_size,_,_=extractor.extract(dataset,synthetic,generated)
            if synthetic_size!=size:
                raise ValueError('Synthetic image dimensions changed.')
            for query,features,truth,kind in [(source,normal_features,np.zeros((size[1],size[0]),dtype=bool),'real_normal_training_query'),(synthetic,synthetic_features,mask,'synthetic_cutpaste_training_query')]:
                diagnostics=support_diagnostics(features,references)
                before=restore_map(diagnostics['nearest_distance'],(16,16),size)
                image_score=lambda scores:float(torch.topk(scores,max(1,int(np.ceil(len(scores)*.01)))).values.mean())
                before_loss=offline_loss(before,truth,config['loss'],image_score=image_score(diagnostics['nearest_distance']))
                for candidate,candidate_feature in zip(candidates,candidate_features):
                    after_scores=patch_nearest_neighbor(features,torch.cat(references+[candidate_feature]))
                    vector=inference_feature_vector(features,references,candidate_feature,diagnostics,after_scores)
                    after=restore_map(after_scores,(16,16),size)
                    after_loss=offline_loss(after,truth,config['loss'],image_score=image_score(after_scores))
                    row={'dataset':dataset,'category':source.category,'experiment_role':'meta_training','native_query_source_split':'train','seed':episode['seed'],'query_kind':kind,'query_id':query.image,'query_source_id':source.image,'support_ids':episode['support_ids'],'candidate_pool_ids':episode['candidate_ids'],'candidate_id':candidate.image,'loss_before':before_loss,'loss_after':after_loss,'observed_benefit':before_loss-after_loss,'features':vector,'feature_names':FEATURE_NAMES,'loo_defined':False,'loo_missing_indicator':1,'checkpoint_sha256':extractor.checkpoint_hash,'source_commit':extractor.source_commit,'preprocessing_version':PREPROCESS_VERSION,'feature_layer_configuration':LAYER_CONFIGURATION,'loss_specification':config['loss'],'synthetic_provenance':provenance if kind.startswith('synthetic') else None,'final_test_labels_used':False}
                    if not np.isfinite(vector).all() or not np.isfinite(row['observed_benefit']):
                        raise ValueError('Nonfinite counterfactual supervision.')
                    episode_rows.append(row)
        destination=output/f"{dataset}_seed-{episode['seed']}.jsonl"
        with destination.open('w') as f:
            for row in episode_rows:
                f.write(json.dumps(row)+'\n')
        all_rows.extend(episode_rows)
        print(json.dumps({'dataset':dataset,'seed':episode['seed'],'targets':len(episode_rows)}),flush=True)
    summary={'targets':len(all_rows),'source_episodes':len(episodes),'real_normal_training_queries':len({(r['dataset'],r['query_id']) for r in all_rows if r['query_kind']=='real_normal_training_query'}),'synthetic_training_queries':len({(r['dataset'],r['query_id']) for r in all_rows if r['query_kind'].startswith('synthetic')}),'positive_benefit_targets':sum(r['observed_benefit']>1e-8 for r in all_rows),'negative_benefit_targets':sum(r['observed_benefit']<-1e-8 for r in all_rows),'source_categories':config['source_categories'],'loss_specification':config['loss'],'feature_names':FEATURE_NAMES,'final_test_labels_used':False,'independence_note':'Rows sharing a source image/support episode are dependent. Synthetic anomalies are supervision only, not benchmark performance evidence.'}
    (output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)


if __name__=='__main__':
    main()
