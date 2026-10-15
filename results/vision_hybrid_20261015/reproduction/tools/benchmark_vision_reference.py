"""Full class-separated reference benchmark, without fitting hybrid parameters.

Defaults cover both official datasets, k1/2/4 and five reference draws. This
driver is provided for a practical GPU benchmark; the bounded CPU study is a
separate run. No published scores are substituted for measured outputs.
"""
from __future__ import annotations
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score,average_precision_score

from safe_iad.safal_cli import inventory
from safe_iad.experiment_io import sha256,write_json,write_jsonl,read_jsonl,implementation_hashes
from safe_iad.vision_hybrid_features import RegisterEncoder,SLOTS,metric_map,image_score,roi_mask
from safe_iad.research_metrics import localization_metrics


def patch_search(query,memory,device='cpu',chunk=128):
    query=torch.as_tensor(query,dtype=torch.float32,device=device)
    memory=torch.as_tensor(memory,dtype=torch.float32,device=device)
    if query.ndim!=2 or memory.ndim!=2 or query.shape[1]!=memory.shape[1] or not len(query) or not len(memory):
        raise ValueError('Matching nonempty query/reference patch matrices required.')
    if not torch.isfinite(query).all() or not torch.isfinite(memory).all() or (query.norm(dim=1)==0).any() or (memory.norm(dim=1)==0).any():
        raise ValueError('Finite nonzero descriptors required.')
    query=F.normalize(query,dim=1);memory=F.normalize(memory,dim=1)
    return torch.cat([(1-(q@memory.T).max(1).values).clamp_min(0) for q in query.split(chunk)]).cpu()


def reference_map(query,memories,grid,device='cpu'):
    combined=torch.zeros(grid*grid,dtype=torch.float64)
    for slot in SLOTS:
        values=patch_search(query[slot],memories[slot],device)
        if slot=='vflip':values=values.reshape(grid,grid).flip(0).flatten()
        combined+=values.double()
    return metric_map(combined,grid)


def run(args):
    output=Path(args.output);output.mkdir(parents=True,exist_ok=True)
    shots=sorted(set(args.shots));seeds=list(args.seeds)
    if not shots or min(shots)<1 or not seeds or min(seeds)<0 or len(set(seeds))!=len(seeds):raise ValueError('Positive shots and distinct nonnegative seeds required.')
    if args.limit_queries is not None and args.limit_queries<1:raise ValueError('Query limit must be positive; omit it for all queries.')
    roots={'mvtec_ad':args.mvtec_ad,'visa':args.visa}
    if not any(roots.values()):raise ValueError('At least one dataset root required.')
    inventories={d:inventory({'roots':{d:p}},d) for d,p in roots.items() if p}
    encoder=RegisterEncoder(args.source_dir,args.checkpoint,device=args.device,threads=args.threads)
    source_hashes={str(Path(__file__).resolve()):sha256(__file__)}
    metadata_paths=[p for d,(root,_) in inventories.items() if d=='visa' for p in [root/'split_csv/1cls.csv',*sorted(root.glob('*/image_anno.csv'))]]
    settings=dict(shots=shots,seeds=seeds,encoder=encoder.metadata(),localization=args.localization,
                  dataset_roots={d:str(root) for d,(root,_) in inventories.items()},
                  dataset_metadata_sha256={str(p):sha256(p) for p in metadata_paths},
                  driver_sha256=source_hashes[str(Path(__file__).resolve())],
                  implementation_sha256=implementation_hashes(['vision_hybrid_features.py','safal_features.py','safal_cli.py','verify_dataset.py','research_metrics.py','experiment_io.py']),
                  sample_limit=args.limit_queries,category_filter=args.categories,
                  recipe='Independent reconstruction of pinned VisionAD class-separated cosine search and augmentations',
                  masks='Nearest in matched cropped ROI, explicit deviation from inspected bilinear mask default',
                  draw_rule='torch.randperm(sorted normal train paths), per-category generator seeded by draw; nested shot prefixes; author support IDs not published')
    write_json(output/'settings.json',settings)
    all_metrics=[]
    for dataset,(root,lookup) in inventories.items():
        categories=sorted({s.category for s in lookup.values()})
        if args.categories:categories=[c for c in categories if c in args.categories]
        for category in categories:
            normal=sorted(i for i,s in lookup.items() if s.category==category and s.split=='train' and s.label=='normal')
            queries=sorted(i for i,s in lookup.items() if s.category==category and s.split=='test')
            if args.limit_queries:queries=queries[:args.limit_queries]
            if len(normal)<max(shots):raise ValueError('Insufficient original normal references.')
            support_ids={seed:[normal[i] for i in torch.randperm(len(normal),generator=torch.Generator().manual_seed(seed))[:max(shots)].tolist()] for seed in seeds}
            directory=output/(dataset+'-'+category);completion=directory/'completion.json'
            if completion.exists():
                done=json.loads(completion.read_text())
                if done['settings_sha256']!=sha256(output/'settings.json') or done['driver_sha256']!=source_hashes[str(Path(__file__).resolve())]:raise ValueError('Completed benchmark settings/source changed.')
                for p,h in done['input_sha256'].items():
                    if sha256(p)!=h:raise ValueError('Completed benchmark image/mask changed.')
                for name,h in done['artifacts'].items():
                    if sha256(directory/name)!=h:raise ValueError('Completed benchmark artifact changed.')
                all_metrics.extend(json.loads((directory/'metrics.json').read_text()));continue
            if directory.exists() and any(directory.iterdir()):raise ValueError('Preserve partial category before restarting: '+str(directory))
            directory.mkdir(parents=True)
            fingerprints={str(root/i):sha256(root/i) for i in queries+list({i for values in support_ids.values() for i in values})}
            features=[];truths=[];labels=[]
            for index,identifier in enumerate(queries):
                print('REFERENCE FEATURES',dataset,category,index+1,'/',len(queries),flush=True)
                features.append(encoder.query(root/identifier));sample=lookup[identifier];labels.append(int(sample.label!='normal'))
                if args.localization:
                    if sample.mask:
                        fingerprints[str(root/sample.mask)]=sha256(root/sample.mask)
                        with Image.open(root/sample.mask) as image:truths.append(roi_mask(image))
                    else:truths.append(np.zeros((256,256),bool))
            support_cache={};rows=[];measurements=[]
            for seed in seeds:
                for identifier in support_ids[seed]:
                    if identifier not in support_cache:support_cache[identifier]=encoder.support(root/identifier)
                for k in shots:
                    memories={s:[] for s in SLOTS}
                    for identifier in support_ids[seed][:k]:
                        values,indices=support_cache[identifier]
                        for slot in SLOTS:memories[slot].extend(values[i] for i in indices[slot])
                    memories={s:torch.cat(v).to(args.device) for s,v in memories.items()}
                    maps=[];scores=[]
                    for identifier,query,label in zip(queries,features,labels):
                        score_map=reference_map(query,memories,encoder.grid,args.device);score=image_score(score_map);scores.append(score)
                        if args.localization:maps.append(score_map)
                        rows.append(dict(dataset=dataset,category=category,seed=seed,shots=k,query_id=identifier,
                                         label=label,score=score,support_ids=support_ids[seed][:k],extra_target_calibration_images=0))
                    measurement=dict(dataset=dataset,category=category,seed=seed,shots=k,queries=len(queries),
                                     image_auroc=float(roc_auc_score(labels,scores)) if len(set(labels))==2 else None,
                                     image_ap=float(average_precision_score(labels,scores)) if any(labels) else None)
                    if args.localization:
                        raw=localization_metrics(truths,maps,0.,max_thresholds=128)
                        measurement['localization']={name:value for name,value in raw.items() if name in ('pixel_auroc','pixel_ap','au_pro') or name.startswith('au_pro_')}
                        measurement['operating_point_metrics_reported']=False
                    measurements.append(measurement);print(json.dumps(measurement),flush=True)
            write_jsonl(directory/'predictions.jsonl',rows);write_json(directory/'metrics.json',measurements)
            write_json(completion,dict(settings_sha256=sha256(output/'settings.json'),driver_sha256=source_hashes[str(Path(__file__).resolve())],
                                       input_sha256=fingerprints,artifacts={n:sha256(directory/n) for n in ['predictions.jsonl','metrics.json']}))
            all_metrics.extend(measurements)
    if not all_metrics:raise ValueError('No dataset/category measurements were executed or verified.')
    grouped=defaultdict(list)
    for row in all_metrics:grouped[row['dataset'],row['shots']].append(row)
    means=[]
    for (dataset,k),values in sorted(grouped.items()):
        per_seed=defaultdict(list)
        for value in values:
            if value['image_auroc'] is not None:per_seed[value['seed']].append(value['image_auroc'])
        averages=[float(np.mean(v)) for v in per_seed.values()]
        means.append(dict(dataset=dataset,shots=k,mean_image_auroc=float(np.mean(averages)) if averages else None,
                          support_draw_std=float(np.std(averages,ddof=0)) if averages else None,
                          categories=sorted({r['category'] for r in values}),draws=len(per_seed)))
    write_json(output/'summary.json',dict(measurements=means,full_category_benchmark=not args.categories and not args.limit_queries,
                                        backbone_frozen=True,hybrid_parameters_fitted=False,operating_point_accuracy_not_reported=True))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source-dir',required=True);p.add_argument('--checkpoint',required=True)
    p.add_argument('--mvtec-ad');p.add_argument('--visa');p.add_argument('--output',required=True)
    p.add_argument('--device',choices=['cpu','cuda'],default='cpu');p.add_argument('--threads',type=int,default=3)
    p.add_argument('--shots',type=int,nargs='+',default=[1,2,4]);p.add_argument('--seeds',type=int,nargs='+',default=[1,2,3,4,5])
    p.add_argument('--categories',nargs='+');p.add_argument('--limit-queries',type=int)
    p.add_argument('--localization',action='store_true')
    run(p.parse_args())


if __name__=='__main__':main()
