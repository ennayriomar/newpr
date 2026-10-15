"""Package a completed audited study; stream the full archive into Git blobs."""
from pathlib import Path, PurePosixPath
import argparse
import gzip
import hashlib
import io
import json
import os
import subprocess
import tarfile
import zipfile

RUN=Path('/tmp/vision_hybrid_20261015')
TOOLS=Path('/workspace/tools')
STAGE=Path('/tmp/vision_hybrid_release_20261015')
GIT=Path('/tmp/safe_iad_publish_git')
VENDOR=Path('/tmp/safal_release_v050/safal_full_model/vendor/dinov2')
ARCHIVE='vision_hybrid_full_results_20261015.tar.gz'
PREFIX='vision_hybrid_results/'

def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,indent=2)+'\n')

def sha(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()

def git(*args,input=None):
    return subprocess.run(['git','-C',str(GIT),'-c','gc.auto=0',*args],input=input,
                          capture_output=True,check=True).stdout.decode().strip()

def blob(data):
    value=git('hash-object','-w','--stdin',input=data)
    assert value==hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    return value

def files(root):
    for p in sorted(root.rglob('*')):
        relative=p.relative_to(root)
        if any(v in {'.git','__pycache__','.pytest_cache'} or v.endswith('.egg-info') for v in relative.parts):continue
        if p.is_symlink():raise ValueError('Unexpected symlink: '+str(p))
        if p.is_file() and p.name!='.execution.lock':yield relative.as_posix(),p

def ready():
    assert json.loads((RUN/'artifact_audit.json').read_text())['status']=='passed'
    summary=json.loads((RUN/'summary.json').read_text())
    assert summary['unique_verification_images']==100 and summary['paired_cases']==200
    assert not summary['full_benchmark_completed']
    banks=list(RUN.glob('*/*/*/model.npz'))
    assert len(banks)==20,len(banks)
    assert len(list((RUN/'verification').glob('*/*/maps/*.npz')))==200
    return summary

class Sink:
    def __init__(self):
        self.buffer=bytearray();self.parts=[];self.whole=hashlib.sha256();self.total=0
    def writable(self):return True
    def write(self,data):
        self.buffer.extend(data)
        while len(self.buffer)>=8*1024*1024:self.emit(8*1024*1024)
        return len(data)
    def flush(self):pass
    def emit(self,size):
        data=bytes(self.buffer[:size]);del self.buffer[:size]
        part=dict(name=ARCHIVE+f'.part{len(self.parts):03d}',offset=self.total,bytes=len(data),
                  sha256=hashlib.sha256(data).hexdigest(),git_blob_sha1=blob(data))
        self.whole.update(data);self.total+=len(data);self.parts.append(part)
        print('ARCHIVE',len(self.parts),self.total,flush=True)
    def finish(self):
        if self.buffer:self.emit(len(self.buffer))

def archive():
    ready();metadata=STAGE/'archive_metadata';metadata.mkdir(parents=True,exist_ok=True)
    assert not (metadata/'manifest.json').exists(),'Archive already built; verify it rather than overwrite.'
    paths=list(files(RUN));hashes={};inode_hashes={}
    for name,p in paths:
        s=p.stat();key=(s.st_dev,s.st_ino,s.st_size)
        if key not in inode_hashes:inode_hashes[key]=sha(p)
        hashes[name]=inode_hashes[key]
    assert 'MANIFEST.sha256.json' not in hashes
    sink=Sink()
    with gzip.GzipFile(fileobj=sink,mode='wb',filename='',mtime=0,compresslevel=1) as compressed:
        with tarfile.open(fileobj=compressed,mode='w|',format=tarfile.PAX_FORMAT,dereference=False) as tar:
            for name,p in paths:
                info=tar.gettarinfo(str(p),arcname=PREFIX+name)
                info.mtime=0;info.uid=info.gid=0;info.uname=info.gname='';info.mode=0o644
                info.pax_headers={}
                if info.isfile():
                    with p.open('rb') as data:tar.addfile(info,data)
                else:
                    assert info.islnk();tar.addfile(info)
            data=(json.dumps(hashes,indent=2)+'\n').encode()
            info=tarfile.TarInfo(PREFIX+'MANIFEST.sha256.json');info.size=len(data);info.mode=0o644
            tar.addfile(info,io.BytesIO(data))
    sink.finish()
    manifest=dict(schema_version=1,archive=ARCHIVE,bytes=sink.total,sha256=sink.whole.hexdigest(),
                  compression='gzip; deterministic tar headers; internal hardlinks preserve bank aliases',
                  root=PREFIX.rstrip('/'),logical_files=len(hashes),primary_banks=20,selected_and_fit_npz_paths=40,
                  query_feature_probes=10,verification_maps=200,parts=sink.parts,
                  excludes=['raw dataset images','external foundation checkpoint','unlicensed VisionAD source'],
                  internal_manifest='MANIFEST.sha256.json')
    write(metadata/'manifest.json',manifest)
    (metadata/'README.md').write_text('''# Complete measured study archive

This contains all 20 one-shot fitted support banks (10 development and 10
verification), selected and unselected metadata, raw branch scores, 200 paired
baseline/hybrid maps, 10 feature probes, manifests, selection lock, tests,
audits and reproduction source. Model aliases are TAR hardlinks to their
matching feature banks. Dataset images and the external 1.22 GB DINOv2 weight
file are separate. Derived features retain the dataset licensing conditions.

Use `framework/download_vision_hybrid_results.py --ref PAYLOAD_COMMIT --extract`.
The release README records the immutable payload commit. Every part and the
whole compressed archive are SHA256 checked before safe extraction; the
internal manifest verifies extracted artifacts. The compact ZIP provides full
code and one fixed example bank. Preserve the original run's absolute paths
when resuming its ledgers; portable prediction uses explicit path overrides.
''')
    print(json.dumps({k:v for k,v in manifest.items() if k!='parts'}),flush=True)

class Reader:
    def __init__(self,parts):
        self.parts=iter(parts);self.buffer=memoryview(b'');self.h=hashlib.sha256();self.total=0
    def read(self,size=-1):
        if size<0:raise ValueError('Bounded streaming reads required.')
        chunks=[];remaining=size
        while remaining:
            if not self.buffer:
                try:item=next(self.parts)
                except StopIteration:break
                data=subprocess.run(['git','-C',str(GIT),'cat-file','blob',item['git_blob_sha1']],capture_output=True,check=True).stdout
                assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
                assert self.total==item['offset'];self.total+=len(data);self.h.update(data);self.buffer=memoryview(data)
            count=min(remaining,len(self.buffer));chunks.append(bytes(self.buffer[:count]));self.buffer=self.buffer[count:];remaining-=count
        return b''.join(chunks)

def verify_archive():
    manifest=json.loads((STAGE/'archive_metadata'/'manifest.json').read_text());reader=Reader(manifest['parts'])
    actual={};internal=None;hardlinks=0;seen=set()
    with gzip.GzipFile(fileobj=reader,mode='rb') as compressed:
        with tarfile.open(fileobj=compressed,mode='r|') as tar:
            for info in tar:
                name=PurePosixPath(info.name)
                assert not name.is_absolute() and '..' not in name.parts and '\\' not in info.name
                assert info.name.startswith(PREFIX) and info.name not in seen;seen.add(info.name)
                relative=info.name[len(PREFIX):]
                if info.islnk():
                    assert info.linkname in seen and info.linkname.startswith(PREFIX)
                    actual[relative]=actual[info.linkname[len(PREFIX):]];hardlinks+=1
                else:
                    assert info.isfile()
                    handle=tar.extractfile(info)
                    if relative=='MANIFEST.sha256.json':internal=json.load(handle)
                    else:actual[relative]=hashlib.file_digest(handle,'sha256').hexdigest()
        while compressed.read(1024*1024):pass  # Consume gzip trailer and validate CRC.
    assert actual==internal and len(actual)==manifest['logical_files']
    assert reader.total==manifest['bytes'] and reader.h.hexdigest()==manifest['sha256']
    for name,expected in actual.items():assert sha(RUN/name)==expected,name
    assert hardlinks==20,hardlinks
    write(STAGE/'ARCHIVE_VERIFICATION.json',dict(status='passed',files=len(actual),hardlink_aliases=hardlinks,
          bytes=reader.total,sha256=reader.h.hexdigest(),gzip_crc_verified=True,all_source_bytes_match=True))
    print('ARCHIVE VERIFIED',len(actual),hardlinks,flush=True)

def compact():
    summary=ready();STAGE.mkdir(parents=True,exist_ok=True)
    archive_path=STAGE/'vision_hybrid_20261015.zip';assert not archive_path.exists()
    entries={}
    for name,p in files(TOOLS):entries['vision_hybrid/tools/'+name]=p
    for name,p in files(VENDOR):entries['vision_hybrid/vendor/dinov2/'+name]=p
    for name,p in files(RUN):
        if p.suffix!='.npz':entries['vision_hybrid/reports/'+name]=p
    bank=RUN/'verification/mvtec_ad-bottle/mvtec_ad-bottle-k1-seed17'
    for name in ['model.json','model.npz']:entries['vision_hybrid/model/'+name]=bank/name
    b=summary['methods']['baseline'];h=summary['methods']['hybrid'];interval=summary['paired_image_auroc']['interval']
    readme=f'''# Register-DINO + PCA hybrid: completed CPU study

The new independent model uses real frozen DINOv2 ViT-L/14 with four registers,
392-pixel cropped inputs, raw mean blocks 4–18, six support augmentations and
three search slots. One original normal image fits each bank; zero extra
target calibration images. The selected global PCA retains 95% variance and
adds its normalized residual with strength 0.5. Local and gated controls were
eligible but did not win. No LLM or backbone fine-tuning is performed.
Parameter selection uses 50 normal and 50 anomalous development images and
their masks from five source categories. Normal-only refers to fitting each
target feature bank; the entire selection procedure is not label-free.

On 100 reserved image IDs across five categories outside current parameter
selection, repeated across two support draws (200 paired cases), baseline
image AUROC is {100*b['mean_image_auroc']:.2f}% and hybrid AUROC is
{100*h['mean_image_auroc']:.2f}%. The conditional paired difference interval is
[{100*interval[0]:+.2f}, {100*interval[1]:+.2f}] percentage points. Full measured
accuracy, localization, false alarms, category results and limitations are in
`reports/report.md`. This is a bounded study; full-paper superiority is not
established. Some categories have historical prototype exposure.

## Run the fixed example model

The included bottle/one-shot/seed17 bank was fixed by convention, not selected
for best performance. Full code, tests and licensed Meta source are included.
Install the pinned runtime, then fetch the separately distributed official
1.22 GB foundation checkpoint:

```bash
cd tools
bash install_safal.sh
source .venv/bin/activate
python prepare_vision_hybrid.py --destination ../assets --source-dir ../vendor/dinov2
python -m safe_iad.vision_hybrid_cli predict --model ../model/model \\
  --image /path/to/your/bottle.png --output ../new_prediction \\
  --source-dir ../vendor/dinov2 --checkpoint ../assets/dinov2_vitl14_reg4_pretrain.pth
```

The installer creates `tools/.venv`. Predictions use no labels
or masks. They return an image decision and a 256x256 center-ROI anomaly map;
outer borders are unscored. Scores are not probabilities. The baseline-derived
global development-normal cutoff has no target false-alarm guarantee. The
model verifies numerical versions, source and checkpoint SHA256.

All 20 fitted banks, all raw branches, 200 evaluation maps and complete audit
files are available in the separately published complete archive. Use
`tools/download_vision_hybrid_results.py --ref PAYLOAD_COMMIT --extract` with
the immutable commit recorded in the repository release README. Raw dataset
images and foundation checkpoint binaries are excluded from both packages.

See `tools/docs/vision_hybrid.md` for equations, selection rules, exact recipe,
reproduction stages and the provided full-reference benchmark driver. The full
27-category, five-seed, 1/2/4-shot benchmark has not been executed.
'''
    notice='''# Dataset-derived model artifact notice

MVTec AD derived feature banks retain the dataset's CC BY-NC-SA 4.0 conditions:
https://www.mvtec.com/company/research/datasets/mvtec-ad
Credit MVTec Software GmbH and Bergmann et al., MVTec AD (CVPR 2019).
The compact bank is derived from MVTec AD bottle and is for noncommercial use.
VisA derived banks in the complete archive retain CC BY 4.0 conditions:
https://github.com/amazon-science/spot-diff
Credit Zou et al., SPot-the-Difference (ECCV 2022), and the VisA creators.
No ownership of original dataset imagery is claimed. Foundation weights and
licensed Meta source retain their own accompanying notices. No inspected
unlicensed VisionAD repository files are redistributed.
'''
    extras={'vision_hybrid/README.md':readme.encode(),'vision_hybrid/MODEL_ARTIFACT_NOTICE.md':notice.encode()}
    hashes={name:sha(path) for name,path in entries.items()}
    hashes.update({name:hashlib.sha256(value).hexdigest() for name,value in extras.items()})
    extras['vision_hybrid/MANIFEST.sha256.json']=(json.dumps(hashes,indent=2)+'\n').encode()
    with zipfile.ZipFile(archive_path,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=1) as z:
        for name,p in sorted(entries.items()):z.write(p,name)
        for name,data in sorted(extras.items()):z.writestr(name,data)
    assert archive_path.stat().st_size<90*1024*1024
    with zipfile.ZipFile(archive_path) as z:
        assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
        expected=json.loads(z.read('vision_hybrid/MANIFEST.sha256.json'))
        for name,value in expected.items():assert hashlib.sha256(z.read(name)).hexdigest()==value,name
        for name,p in entries.items():assert hashlib.sha256(z.read(name)).hexdigest()==sha(p),name
    checksum=sha(archive_path)
    (STAGE/(archive_path.name+'.sha256')).write_text(checksum+'  '+archive_path.name+'\n')
    write(STAGE/'PACKAGE_VERIFICATION.json',dict(status='passed',zip=archive_path.name,bytes=archive_path.stat().st_size,
          sha256=checksum,files=len(hashes),crc_verified=True,current_source_bytes_match=True,
          example_bank='mvtec_ad-bottle-k1-seed17',full_dataset_images_included=False,foundation_checkpoint_included=False))
    print('ZIP VERIFIED',archive_path.stat().st_size,checksum,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('mode',choices=['archive','verify-archive','compact']);a=p.parse_args()
    {'archive':archive,'verify-archive':verify_archive,'compact':compact}[a.mode]()
