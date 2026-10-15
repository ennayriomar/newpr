"""Verify the public immutable tree, ZIP and complete archive bytes."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import io
import json
import time
import urllib.request
import zipfile

STAGE=Path('/tmp/vision_hybrid_release_20261015')
publication=json.loads((STAGE/'PUBLICATION.json').read_text())
entries=json.loads((STAGE/'published_entries.json').read_text())
commit=publication['commit'];root='https://raw.githubusercontent.com/ennayriomar/newpr/'+commit+'/'

def get(url):
    for attempt in range(4):
        try:
            request=urllib.request.Request(url,headers={'User-Agent':'SAFAL-artifact-verification'})
            with urllib.request.urlopen(request,timeout=60) as response:
                assert response.status==200
                return response.read()
        except Exception:
            if attempt==3:raise
            time.sleep(2**attempt)

tree=json.loads(get('https://api.github.com/repos/ennayriomar/newpr/git/trees/'+commit+'?recursive=1'))
assert not tree.get('truncated',False)
blobs={r['path']:r['sha'] for r in tree['tree'] if r['type']=='blob'}
assert all(blobs[e['path']]==e['sha'] for e in entries)
print('PUBLIC TREE VERIFIED',len(entries),flush=True)
package=json.loads((STAGE/'PACKAGE_VERIFICATION.json').read_text())
data=get(publication['zip_url']);assert len(data)==package['bytes']
assert hashlib.sha256(data).hexdigest()==package['sha256']
with zipfile.ZipFile(io.BytesIO(data)) as archive:
    assert archive.testzip() is None
    hashes=json.loads(archive.read('vision_hybrid/MANIFEST.sha256.json'))
    assert all(hashlib.sha256(archive.read(name)).hexdigest()==value for name,value in hashes.items())
report=get(root+'results/vision_hybrid_20261015/report.md')
assert report==(Path('/tmp/vision_hybrid_20261015')/'report.md').read_bytes()
print('PUBLIC ZIP VERIFIED',len(data),flush=True)
manifest=json.loads(get(root+'results/vision_hybrid_20261015_archive/manifest.json'))
assert manifest==json.loads((STAGE/'archive_metadata/manifest.json').read_text())
whole=hashlib.sha256();total=0

def part(index):
    item=manifest['parts'][index]
    value=get(root+'results/vision_hybrid_20261015_archive/'+item['name'])
    assert len(value)==item['bytes'] and hashlib.sha256(value).hexdigest()==item['sha256']
    return value

with ThreadPoolExecutor(max_workers=4) as pool:
    pending={i:pool.submit(part,i) for i in range(min(8,len(manifest['parts'])))}
    for index,item in enumerate(manifest['parts']):
        value=pending.pop(index).result();assert item['offset']==total
        whole.update(value);total+=len(value)
        next_index=index+8
        if next_index<len(manifest['parts']):pending[next_index]=pool.submit(part,next_index)
        if (index+1)%8==0:print('PUBLIC PARTS VERIFIED',index+1,'/',len(manifest['parts']),flush=True)
assert total==manifest['bytes'] and whole.hexdigest()==manifest['sha256']
record=dict(status='passed',commit=commit,zip_url=publication['zip_url'],report_url=publication['report_url'],
            verified_tree_blobs=len(entries),public_zip_bytes=len(data),public_zip_sha256=package['sha256'],
            zip_crc_and_internal_manifest=True,public_archive_parts=len(manifest['parts']),
            public_archive_bytes=total,public_archive_sha256=whole.hexdigest(),
            archive_assembled_hash_verified_without_duplicate_disk_copy=True,public_report_exact_bytes=True)
(STAGE/'PUBLIC_VERIFICATION.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
