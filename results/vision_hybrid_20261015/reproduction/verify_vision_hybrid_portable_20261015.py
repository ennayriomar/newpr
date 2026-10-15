"""Replay a fixed real image using the extracted release source and model."""
from pathlib import Path,PurePosixPath
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
import numpy as np

stage=Path('/tmp/vision_hybrid_release_20261015');run=Path('/tmp/vision_hybrid_20261015')
destination=stage/'portable';assert not destination.exists();destination.mkdir(parents=True)
with zipfile.ZipFile(stage/'vision_hybrid_20261015.zip') as archive:
    for name in archive.namelist():
        p=PurePosixPath(name);assert not p.is_absolute() and '..' not in p.parts and p.parts[0]=='vision_hybrid'
    assert archive.testzip() is None;archive.extractall(destination)
bundle=destination/'vision_hybrid';tools=bundle/'tools';source=bundle/'vendor/dinov2'
config=json.loads((run/'plan.json').read_text())['config']
rows=[json.loads(line) for line in (run/'verification_predictions.jsonl').read_text().splitlines()]
expected=next(row for row in rows if row['method']=='hybrid' and row['episode_id']=='mvtec_ad-bottle-k1-seed17')
image=Path(config['roots'][expected['dataset']])/expected['query_id'];output=stage/'portable_prediction'
environment=os.environ.copy();environment['PYTHONPATH']=str(tools)
check=subprocess.run([sys.executable,'-c','import safe_iad.vision_hybrid_cli as m; print(m.__file__)'],
                     cwd=tools,env=environment,capture_output=True,text=True,check=True)
import_path=Path(check.stdout.strip());assert import_path.is_relative_to(tools)
command=[sys.executable,'-m','safe_iad.vision_hybrid_cli','predict','--model',str(bundle/'model/model'),
         '--image',str(image),'--output',str(output),'--source-dir',str(source),
         '--checkpoint',config['encoder']['checkpoint'],'--device','cpu']
with (stage/'portable_prediction.log').open('wb') as log:
    subprocess.run(command,cwd=tools,env=environment,stdout=log,stderr=subprocess.STDOUT,check=True)
actual=json.loads((output/'prediction.json').read_text());error=abs(actual['image_score']-expected['score'])
assert error<=1e-7 and actual['decision']==expected['decision']
assert actual['image_sha256']==hashlib.sha256(image.read_bytes()).hexdigest()
assert actual['parameters_id']==expected['parameters_id'] and actual['threshold']==expected['threshold']
assert actual['encoder']['runtime']['source_dir']==str(source.resolve()) and actual['probabilities'] is False
with np.load(output/'cropped_roi_maps.npz',allow_pickle=False) as predicted,np.load(expected['map_file'],allow_pickle=False) as original:
    difference=float(np.max(np.abs(predicted['hybrid']-original['hybrid'])))
    assert difference<=1e-6 and predicted['hybrid'].dtype==np.float32 and predicted['hybrid'].shape==(256,256)
record=dict(status='passed',fixed_example_bank='mvtec_ad-bottle-k1-seed17',query_id=expected['query_id'],
            query_sha256=actual['image_sha256'],image_score=actual['image_score'],expected_score=expected['score'],
            score_absolute_error=error,map_max_absolute_error=difference,decision_matches=True,
            package_source_import=str(import_path),package_source_used=True,bundled_meta_source_used=True,
            checkpoint_sha256=actual['encoder']['checkpoint_sha256'],real_encoder_forward=True,
            cached_query_features_used=False,labels_or_masks_given_to_prediction=False,
            probabilities=False,scope='One fixed real-image replay from extracted ZIP; not a full independent benchmark rerun.')
(stage/'PORTABLE_INFERENCE_VERIFICATION.json').write_text(json.dumps(record,indent=2)+'\n')
shutil.copy2(stage/'PORTABLE_INFERENCE_VERIFICATION.json',run/'portable_inference_verification.json')
shutil.copy2(stage/'portable_prediction.log',run/'portable_prediction.log')
print(json.dumps(record,indent=2),flush=True)
