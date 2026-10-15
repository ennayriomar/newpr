"""Record verified immutable downloads after public byte verification."""
from pathlib import Path
import hashlib
import json
import subprocess
import urllib.request

stage=Path('/tmp/vision_hybrid_release_20261015');directory=Path('/tmp/safe_iad_publish_git')
publication=json.loads((stage/'PUBLICATION.json').read_text())
verified=json.loads((stage/'PUBLIC_VERIFICATION.json').read_text())
assert verified['status']=='passed' and verified['commit']==publication['commit']
parent=publication['commit']

def git(*args,input=None):
    return subprocess.run(['git','-C',str(directory),'-c','gc.auto=0',*args],input=input,capture_output=True,check=True).stdout.decode().strip()

assert git('ls-remote','origin','refs/heads/main').split()[0]==parent
readme=git('show',parent+':README.md')
addition=f'''### Verified immutable downloads

- [Full code and example-model ZIP]({publication['zip_url']})
- [Measured study report]({publication['report_url']})
- [All banks, maps and audit outputs]({publication['archive_url']})

The public ZIP and every complete-archive part were downloaded and SHA256
verified. Download all banks without cloning the repository:

```bash
{publication['full_archive_download_command']}
```

The ZIP contains the same downloader at `tools/download_vision_hybrid_results.py`.
Run it from the ZIP's `tools` directory without the `framework/` prefix.
See `results/vision_hybrid_20261015/PUBLIC_VERIFICATION.json` for byte hashes.

'''
needle='All historical results and fitted-model artifact trees below are preserved.\n'
assert readme.count(needle)==1
readme=readme.replace(needle,addition+needle,1)
entries={'README.md':readme.encode(),
         'results/vision_hybrid_20261015/PUBLICATION.json':(stage/'PUBLICATION.json').read_bytes(),
         'results/vision_hybrid_20261015/PUBLIC_VERIFICATION.json':(stage/'PUBLIC_VERIFICATION.json').read_bytes()}
git('read-tree',parent);updates=[]
for name,data in entries.items():
    sha=git('hash-object','-w','--stdin',input=data)
    assert sha==hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
    updates.append(f'100644 {sha}\t{name}\n')
git('update-index','--index-info',input=''.join(updates).encode());tree=git('write-tree','--missing-ok')
commit=git('-c','user.name=OMAR ENNAYRI','-c','user.email=ennayyri.omar@gmail.com','commit-tree',tree,'-p',parent,
           input=b'Record verified public model downloads and immutable full-archive command\n')
git('-c','pack.threads=2','-c','pack.window=0','push','origin',commit+':refs/heads/main')
assert git('ls-remote','origin','refs/heads/main').split()[0]==commit
git('update-ref','refs/remotes/origin/main',commit)
for name,sha in publication['prior_tree_hashes'].items():assert git('rev-parse',commit+':'+name)==sha
for name,data in entries.items():
    url='https://raw.githubusercontent.com/ennayriomar/newpr/'+commit+'/'+name
    with urllib.request.urlopen(url,timeout=60) as response:assert response.status==200 and response.read()==data
record=publication|dict(status='published_and_publicly_verified',metadata_commit=commit,public_verification=verified,
                         environment_configuration='Startup draft saved; review/save and publish required for activation.')
(stage/'FINAL_PUBLICATION.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
