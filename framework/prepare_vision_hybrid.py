"""Prepare pinned Meta source and checksum-verified register ViT-L weights."""
from pathlib import Path
import argparse
import json
import os
import shutil
import subprocess
import tempfile

from safe_iad.safal_features import SOURCE_PIN,SOURCE_URL,verify_source,export_source_manifest
from safe_iad.vision_hybrid_features import prepare,WEIGHT_SHA256


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination',type=Path,required=True)
    parser.add_argument('--source-dir',type=Path,help='Reuse an existing pinned Git checkout or licensed source/manifest bundle.')
    args=parser.parse_args();destination=args.destination.resolve();destination.mkdir(parents=True,exist_ok=True)
    source=args.source_dir.resolve() if args.source_dir else destination/'dinov2-source'
    if not source.exists():
        if args.source_dir:raise ValueError('Explicit source path does not exist.')
        temporary=Path(tempfile.mkdtemp(prefix='.source-',dir=destination))
        try:
            for command in [['git','init',str(temporary)],['git','-C',str(temporary),'fetch','--depth','1',SOURCE_URL,SOURCE_PIN],
                            ['git','-C',str(temporary),'checkout','--detach','FETCH_HEAD']]:
                subprocess.run(command,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            verify_source(temporary);os.replace(temporary,source)
        finally:
            if temporary.exists():shutil.rmtree(temporary)
    verified=verify_source(source)
    if (source/'.git').exists():export_source_manifest(source)
    checkpoint=prepare(destination/'dinov2_vitl14_reg4_pretrain.pth')
    print(json.dumps({'source_dir':str(source),'checkpoint':str(checkpoint),'checkpoint_sha256':WEIGHT_SHA256,
                      'source_manifest_sha256':verified['source_manifest_sha256']},indent=2))


if __name__=='__main__':main()
