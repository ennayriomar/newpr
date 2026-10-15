"""Independent real-query float32 feature/image-score reproduction probe."""
import argparse
import json
from pathlib import Path
import numpy as np
import torch

from safe_iad.baselines import METHODS,FittedMethod
from safe_iad.dense_features import DenseDINOv2
from safe_iad.run_pipeline import immutable_json
from safe_iad.verify_dataset import Sample


def main():
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--run',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    c=json.loads((a.run/'config.json').read_text()); manifest=json.loads((a.run/'split_manifest.json').read_text()); e=next(x for x in manifest['episodes'] if x['role']!='calibration')
    extractor=DenseDINOv2(c['feature_cache'],c['resolution'],c['layers']); checks=[]; q=Sample(**e['queries'][0]); root=Path(c['roots'][e['dataset']])
    for method in METHODS:
        mode='anomalydino' if method=='anomalydino' else 'subspacead' if method=='subspacead' else 'hybrid'
        cached=extractor.extract_dense(e['dataset'],q,root,mode)
        independent=extractor.extract_dense(e['dataset'],q,root,mode,use_cache=False)
        if not torch.equal(cached.tokens,independent.tokens): raise ValueError('Real float32 features changed under cache bypass.')
        supports=[extractor.extract_dense(e['dataset'],Sample(**s),root,mode) for s in e['support']]
        result=FittedMethod(method,supports,c['models']).predict(independent)
        directory=a.run/'episodes'/e['role']/e['dataset']/e['category']/f"seed-{e['seed']}_k-{e['shots']}"/method
        prediction=json.loads((directory/'predictions.jsonl').read_text().splitlines()[0])
        if result['image_score']!=prediction['image_score']: raise ValueError('Raw image evidence changed from the completed run.')
        if result['mean_adequacy']!=prediction['mean_support_adequacy']: raise ValueError('Raw adequacy mean changed.')
        with np.load(prediction['map'],allow_pickle=False) as saved:
            if any(not np.array_equal(saved[k],v.astype(c['map_storage_dtype'])) for k,v in result['maps'].items()): raise ValueError('Stored native fields changed.')
        with np.load(Path(c['feature_cache'])/(cached.key+'.npz'),allow_pickle=False) as cache:
            meta=json.loads(str(cache['metadata'].item()))
        if not {'pillow_version','torchvision_version','numpy_version','torch_version','source_commit','checkpoint_sha256'}.issubset(meta): raise ValueError('Missing feature provenance.')
        checks.append(dict(method=method,image_id=q.image,float32_features_bitwise_equal=True,raw_image_score_exact_equal=True,raw_adequacy_mean_exact_equal=True,
                           stored_maps_bitwise_equal=True,preprocessing_library_versions_in_cache_key=True))
    report=dict(status='passed',scope='one independent real query per method; not a full new rerun of all episodes',checks=checks)
    immutable_json(a.output,report); print(json.dumps(report,indent=2))


if __name__=='__main__': main()
