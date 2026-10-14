"""Publish completed tuning artifacts, preserving all historical Git trees."""
from pathlib import Path
import hashlib
import json
import subprocess

STAGE=Path('/tmp/safal_tuning_release_20261014')
RUN=Path('/tmp/safal_tuning_20261014')
BUNDLE=STAGE/'safal_tuned'
GIT=Path('/tmp/safe_iad_publish_git')
PREFIX='results/safal_tuning_20261014_archive/'

def git(*args,input=None):
    p=subprocess.run(['git','-C',str(GIT),'-c','gc.auto=0',*args],input=input,capture_output=True,check=True)
    return p.stdout.decode().strip()

def blob(data):
    sha=git('hash-object','-w','--stdin',input=data)
    assert sha==hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    return sha

def commit_push(updates,parent,message):
    git('read-tree',parent)
    git('update-index','--index-info',input=''.join(f'{mode} {sha}\t{name}\n' for name,sha,mode in updates).encode())
    tree=git('write-tree','--missing-ok')
    commit=git('-c','user.name=OMAR ENNAYRI','-c','user.email=ennayyri.omar@gmail.com',
               'commit-tree',tree,'-p',parent,input=(message+'\n').encode())
    git('-c','pack.threads=2','-c','pack.window=0','push','origin',commit+':refs/heads/main')
    assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
    git('update-ref','refs/remotes/origin/main',commit)
    return commit

assert json.loads((STAGE/'PACKAGE_VERIFICATION.json').read_text())['status']=='passed'
assert json.loads((STAGE/'INDEPENDENT_PACKAGE_AUDIT.json').read_text())['status']=='passed'
git('-c','protocol.version=2','fetch','--depth=1','--filter=blob:none','origin','main')
parent=git('rev-parse','refs/remotes/origin/main')
assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
initial=parent
preserve=['results_archive','results/safal_full_model_archive','results/safal_training_20261014_archive',
          'results/safal_training_20261014','trained_models/safal_20261014','safal_trained_20261014.zip',
          'safal_full_model_v0.5.0.zip','safe_iad_full_code_v0.4.0.zip','results/safal_full_model','results/milestone3']
old={name:git('rev-parse',parent+':'+name) for name in preserve}
manifest=json.loads((STAGE/'archive_metadata/manifest.json').read_text())
published=[];updates=[];commits=[]
with (STAGE/manifest['archive']).open('rb') as handle:
    for index,part in enumerate(manifest['parts']):
        assert handle.tell()==part['offset']
        data=handle.read(part['bytes'])
        assert hashlib.sha256(data).hexdigest()==part['sha256']
        name=PREFIX+part['name'];sha=blob(data)
        updates.append((name,sha,'100644'))
        published.append(dict(path=name,sha=sha,sha256=part['sha256'],bytes=len(data)))
        if len(updates)==64:
            parent=commit_push(updates,parent,f'Upload complete SAFAL tuning archive through part {index:03d}')
            commits.append(parent);updates=[]
entries=[]
for root,prefix in [(BUNDLE/'tools','framework'),(BUNDLE/'reports','results/safal_tuning_20261014'),
                    (RUN/'models','trained_models/safal_tuned_20261014'),
                    (STAGE/'archive_metadata',PREFIX.rstrip('/'))]:
    for p in sorted(root.rglob('*')):
        if p.is_file():entries.append((prefix+'/'+p.relative_to(root).as_posix(),p))
for name in ['safal_tuned_20261014.zip','safal_tuned_20261014.zip.sha256','PACKAGE_VERIFICATION.json','INDEPENDENT_PACKAGE_AUDIT.json']:
    entries.append((name if name.startswith('safal_') else 'SAFAL_TUNING_'+name,STAGE/name))
entries.append(('trained_models/safal_tuned_20261014/MODEL_ARTIFACT_NOTICE.md',BUNDLE/'MODEL_ARTIFACT_NOTICE.md'))
summary=json.loads((RUN/'summary.json').read_text())
m=summary['methods']
params=json.loads((RUN/'selection.lock.json').read_text())['params']
intro=f'''# SAFAL: measured parameter tuning and trained vision models

## Paper-informed tuning — 14 October 2026

[Download updated code and five example banks](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safal_tuned_20261014.zip) · [Measured report](results/safal_tuning_20261014/report.md) · [Parameter guide](framework/docs/parameter_tuning.md) · [All 15 primary model banks](trained_models/safal_tuned_20261014) · [Complete archive](results/safal_tuning_20261014_archive)

The new independent module evaluated 768 scoring configurations, selected one global hybrid using 100 development images and a zero detected-to-missed constraint against both k4 controls, then compared two isolated feature changes. One hundred separate, prelocked image IDs were checked after the configuration was frozen. Both cohorts use five previously studied categories, three support draws, four original normal references plus four extra normal calibration images. The encoder is real frozen DINOv2 ViT-B/14 on CPU; this is computer-vision parameter selection, not LLM or backbone fine-tuning.

The selected configuration retains 99% PCA variance, uses a 90th-percentile normal cutoff, top1% image aggregation and fixed 75% cosine-search /25% raw-PCA fusion at image threshold 1. The 224-pixel mixed-layer representation remained selected; the late-layer and 336-pixel variants lost previously detected development cases and were rejected. Adequacy/uncertainty remain diagnostics, and the old probability head is omitted.

Development accuracy is 81.33% versus 81.00% original SAFAL and 80.00% fixed averaging. Verification accuracy is 77.33% for the tuned hybrid, 76.33% for original SAFAL and 77.67% for fixed averaging. The paired 95% accuracy intervals include zero: improvement is not established. The tuned model recovers seven previously missed original-SAFAL anomaly cases with zero original-SAFAL detection losses, but adds four false alarms; versus fixed averaging it loses 3 detections and recovers 3. Class counts, localization and conditional intervals are in the measured report. These are 100 unique images repeated across support draws, not 300 independent images. This conditional image check within development-exposed categories does not establish a full benchmark, production reliability or SOTA. The compact ZIP containsfixed k4/seed17 example banks, while all 15 primary banks and full raw-score/map audit outputs are retained separately. Superseded development-only attempts are preserved with notices in the complete archive. Dataset images and pretrained backbone binaries are separate.

'''
(STAGE/'README.md').write_text(intro+git('show',parent+':README.md')+'\n')
entries.append(('README.md',STAGE/'README.md'))
for name,path in entries:
    data=path.read_bytes();sha=blob(data)
    updates.append((name,sha,'100755' if path.suffix=='.sh' else '100644'))
    published.append(dict(path=name,sha=sha,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
parent=commit_push(updates,parent,'Publish paper-informed SAFAL tuning, locked image verification and all primary banks')
commits.append(parent)
for name,sha in old.items():assert git('rev-parse',parent+':'+name)==sha
record=dict(status='published',repository='ennayriomar/newpr',commit=parent,initial_parent=initial,
            push_commits=commits,uploaded_files=len(published),prior_artifacts_preserved=True,
            prior_tree_hashes=old,force_push=False,
            zip_url=f'https://github.com/ennayriomar/newpr/raw/{parent}/safal_tuned_20261014.zip',
            report_url=f'https://github.com/ennayriomar/newpr/blob/{parent}/results/safal_tuning_20261014/report.md',
            archive_url=f'https://github.com/ennayriomar/newpr/tree/{parent}/results/safal_tuning_20261014_archive')
(STAGE/'PUBLICATION.json').write_text(json.dumps(record,indent=2)+'\n')
(STAGE/'published_entries.json').write_text(json.dumps(published,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
