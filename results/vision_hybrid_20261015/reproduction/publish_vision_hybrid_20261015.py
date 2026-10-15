"""Publish verified completed artifacts without replacing historical results."""
from pathlib import Path
import hashlib
import json
import subprocess

STAGE=Path('/tmp/vision_hybrid_release_20261015')
RUN=Path('/tmp/vision_hybrid_20261015')
TOOLS=Path('/workspace/tools')
GIT=Path('/tmp/safe_iad_publish_git')
PREFIX='results/vision_hybrid_20261015_archive/'

def git(*args,input=None):
    return subprocess.run(['git','-C',str(GIT),'-c','gc.auto=0',*args],input=input,
                          capture_output=True,check=True).stdout.decode().strip()

def blob(data):
    value=git('hash-object','-w','--stdin',input=data)
    assert value==hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    return value

def save(name,value):
    (STAGE/name).write_text(json.dumps(value,indent=2)+'\n')

def commit_push(updates,parent,message):
    assert git('ls-remote','origin','refs/heads/main').split()[0]==parent,'Remote main moved; preserve and inspect before retry.'
    git('read-tree',parent)
    git('update-index','--index-info',input=''.join(f'{mode} {sha}\t{path}\n' for path,sha,mode in updates).encode())
    tree=git('write-tree','--missing-ok')
    commit=git('-c','user.name=OMAR ENNAYRI','-c','user.email=ennayyri.omar@gmail.com',
               'commit-tree',tree,'-p',parent,input=(message+'\n').encode())
    git('-c','pack.threads=2','-c','pack.window=0','push','origin',commit+':refs/heads/main')
    assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
    git('update-ref','refs/remotes/origin/main',commit)
    return commit

for name in ['PACKAGE_VERIFICATION.json','ARCHIVE_VERIFICATION.json','PORTABLE_INFERENCE_VERIFICATION.json']:
    assert json.loads((STAGE/name).read_text())['status']=='passed',name
assert json.loads((RUN/'artifact_audit.json').read_text())['status']=='passed'
git('-c','protocol.version=2','fetch','--depth=1','--filter=blob:none','origin','main')
parent=git('rev-parse','refs/remotes/origin/main')
assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
progress_path=STAGE/'PUBLICATION_PROGRESS.json'
if progress_path.exists():
    progress=json.loads(progress_path.read_text());assert progress['parent']==parent
else:
    preserve=['results_archive','results/safal_full_model_archive','results/safal_training_20261014_archive',
              'results/safal_training_20261014','trained_models/safal_20261014','safal_trained_20261014.zip',
              'safal_full_model_v0.5.0.zip','safe_iad_full_code_v0.4.0.zip','results/safal_full_model',
              'results/milestone3','results/safal_tuning_20261014_archive','results/safal_tuning_20261014',
              'trained_models/safal_tuned_20261014','safal_tuned_20261014.zip']
    progress=dict(initial_parent=parent,parent=parent,push_commits=[],parts_uploaded=0,published=[],
                  prior_tree_hashes={name:git('rev-parse',parent+':'+name) for name in preserve})
    save('PUBLICATION_PROGRESS.json',progress)
manifest=json.loads((STAGE/'archive_metadata/manifest.json').read_text())
for start in range(progress['parts_uploaded'],len(manifest['parts']),16):
    updates=[]
    for part in manifest['parts'][start:start+16]:
        path=PREFIX+part['name'];sha=part['git_blob_sha1']
        assert git('cat-file','-s',sha)==str(part['bytes'])
        updates.append((path,sha,'100644'))
        progress['published'].append(dict(path=path,sha=sha,sha256=part['sha256'],bytes=part['bytes']))
    parent=commit_push(updates,parent,f'Upload complete register-DINO hybrid archive through part {start+len(updates)-1:03d}')
    progress['parent']=parent;progress['parts_uploaded']=start+len(updates);progress['push_commits'].append(parent)
    save('PUBLICATION_PROGRESS.json',progress);print('PUBLISHED PARTS',progress['parts_uploaded'],parent,flush=True)

entries=[]
for path in sorted(TOOLS.rglob('*')):
    relative=path.relative_to(TOOLS)
    if any(x in {'.git','__pycache__','.pytest_cache'} or x.endswith('.egg-info') for x in relative.parts):continue
    if path.is_file():entries.append(('framework/'+relative.as_posix(),path))
for path in sorted(RUN.rglob('*')):
    if path.is_file() and path.suffix!='.npz' and path.name!='.execution.lock':
        entries.append(('results/vision_hybrid_20261015/'+path.relative_to(RUN).as_posix(),path))
for path in sorted((STAGE/'archive_metadata').glob('*')):entries.append((PREFIX+path.name,path))
for name in ['vision_hybrid_20261015.zip','vision_hybrid_20261015.zip.sha256','PACKAGE_VERIFICATION.json',
             'ARCHIVE_VERIFICATION.json','PORTABLE_INFERENCE_VERIFICATION.json']:
    entries.append((name if name.startswith('vision_') else 'VISION_HYBRID_'+name,STAGE/name))
summary=json.loads((RUN/'summary.json').read_text());m=summary['methods'];auc=summary['paired_image_auroc']
b=m['baseline'];h=m['hybrid']
intro=f'''# SAFAL research: register-DINO search with a measured PCA correction

## New completed hybrid study — 15 October 2026

[Download code and fixed example model](https://github.com/ennayriomar/newpr/raw/refs/heads/main/vision_hybrid_20261015.zip) · [Measured report](results/vision_hybrid_20261015/report.md) · [Method and commands](framework/docs/vision_hybrid.md) · [All banks and raw outputs](results/vision_hybrid_20261015_archive)

This independent implementation uses real frozen DINOv2 ViT-L/14 with four
registers, 392-pixel crops, the raw mean of blocks 4–18, six normal support
augmentations and three search slots. Each target bank uses **one original
normal image and zero extra target calibration images**. The finite 25-cell
development search considered global/local PCA and uniform/residual gates;
the winner is **one global PCA, 95% retained variance, strength 0.5, uniform
gate**. Search and normalized PCA residual are added. The foundation model is
frozen; this is not LLM training.
Parameter selection uses 50 normal and 50 anomalous source-category development
images and masks; target-bank fitting uses only the single target normal.

The parameters were frozen before evaluation on 100 available-history-excluded
image IDs from five categories outside this study's selection categories,
repeated across two support draws (200 paired cases). Some categories have
historical prototype exposure. Mean within-category/draw image AUROC is
**{100*b['mean_image_auroc']:.2f}% search → {100*h['mean_image_auroc']:.2f}% hybrid**;
the paired conditional 95% difference interval is
[{100*auc['interval'][0]:+.2f}, {100*auc['interval'][1]:+.2f}] percentage points.
Accuracy at the same source-category cutoff is {100*b['accuracy']:.2f}% →
{100*h['accuracy']:.2f}%; pixel AP is {b['localization']['pixel_ap']:.4f} →
{h['localization']['pixel_ap']:.4f}. There are
{len(summary['transitions']['detected_to_missed'])} lost baseline anomaly alerts,
{len(summary['transitions']['missed_to_detected'])} recovered anomaly cases and
{len(summary['transitions']['false_positives_added'])} added false alarms.
**The accuracy-improvement goal was not met.** A higher ranking score does not
resolve the large false-alarm increase at the shared cutoff; the AUROC interval
includes zero. This candidate is a research result, not an accuracy upgrade.
Maps and localization metrics cover only the center crop. Scores are not
probabilities, and the source-normal cutoff carries no target FPR guarantee.

This bounded CPU study does **not** establish superiority over the paper's
full-dataset AUROC. The full 27-category, five-seed, 1/2/4-shot benchmark was
not run. A standalone reference benchmark driver is provided for that work.
The selected stronger feature pipeline must not be numerically compared to
older SAFAL pilots as if their images and support budgets matched.

The ZIP contains complete code, tests, licensed Meta source and the fixed
bottle/seed17 example bank. The complete archive contains all 20 fitted banks,
raw branches, feature probes, 200 maps, frozen manifests and audit/reproduction
code. Dataset images and the external 1.22 GB checkpoint are separate. Follow
the ZIP README for setup and portable inference. Complete archive downloads
use `framework/download_vision_hybrid_results.py --ref PAYLOAD_COMMIT --extract`;
the immutable payload commit is recorded in the publication record.

All historical results and fitted-model artifact trees below are preserved.

'''
(STAGE/'README.md').write_text(intro+git('show',progress['initial_parent']+':README.md')+'\n')
entries.append(('README.md',STAGE/'README.md'))
updates=[]
for name,path in entries:
    data=path.read_bytes();sha=blob(data);updates.append((name,sha,'100755' if path.suffix=='.sh' else '100644'))
    progress['published'].append(dict(path=name,sha=sha,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
parent=commit_push(updates,parent,'Publish strict one-shot register-DINO PCA study, model and audited outputs')
progress['push_commits'].append(parent)
for name,sha in progress['prior_tree_hashes'].items():assert git('rev-parse',parent+':'+name)==sha,name
record=dict(status='published',repository='ennayriomar/newpr',commit=parent,initial_parent=progress['initial_parent'],
            push_commits=progress['push_commits'],uploaded_files=len(progress['published']),
            prior_artifacts_preserved=True,prior_tree_hashes=progress['prior_tree_hashes'],force_push=False,
            zip_url=f'https://github.com/ennayriomar/newpr/raw/{parent}/vision_hybrid_20261015.zip',
            report_url=f'https://github.com/ennayriomar/newpr/blob/{parent}/results/vision_hybrid_20261015/report.md',
            archive_url=f'https://github.com/ennayriomar/newpr/tree/{parent}/results/vision_hybrid_20261015_archive',
            full_archive_download_command=f'python framework/download_vision_hybrid_results.py --ref {parent} --extract')
save('PUBLICATION.json',record);save('published_entries.json',progress['published'])
print(json.dumps(record,indent=2),flush=True)
