"""Check public immutable tree, ZIP and all archive-part bytes."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import urllib.request
import zipfile

STAGE=Path('/tmp/safal_tuning_release_20261014')
publication=json.loads((STAGE/'PUBLICATION.json').read_text())
entries=json.loads((STAGE/'published_entries.json').read_text())
commit=publication['commit']
root='https://raw.githubusercontent.com/ennayriomar/newpr/'+commit+'/'

def get(url):
    request=urllib.request.Request(url,headers={'User-Agent':'SAFAL-artifact-verification'})
    with urllib.request.urlopen(request,timeout=60) as response:
        assert response.status==200
        return response.read()

tree=json.loads(get('https://api.github.com/repos/ennayriomar/newpr/git/trees/'+commit+'?recursive=1'))
assert not tree.get('truncated',False)
blobs={r['path']:r['sha'] for r in tree['tree'] if r['type']=='blob'}
assert all(blobs[e['path']]==e['sha'] for e in entries)
print('Public tree verified',len(entries),'uploaded blobs',flush=True)
package=json.loads((STAGE/'PACKAGE_VERIFICATION.json').read_text())
zip_data=get(publication['zip_url'])
assert len(zip_data)==package['compact_bytes']
assert hashlib.sha256(zip_data).hexdigest()==package['compact_sha256']
destination=STAGE/'public_verified_compact.zip'
destination.write_bytes(zip_data)
with zipfile.ZipFile(destination) as archive:
    assert archive.testzip() is None
    prefix='safal_tuned/'
    hashes=json.loads(archive.read(prefix+'MANIFEST.sha256.json'))
    assert all(hashlib.sha256(archive.read(prefix+n)).hexdigest()==h for n,h in hashes.items())
print('Public compact ZIP verified',len(zip_data),'bytes',flush=True)
manifest=json.loads(get(root+'results/safal_tuning_20261014_archive/manifest.json'))
assert manifest==json.loads((STAGE/'archive_metadata/manifest.json').read_text())
whole=hashlib.sha256();total=0

def part(index):
    item=manifest['parts'][index]
    data=get(root+'results/safal_tuning_20261014_archive/'+item['name'])
    assert len(data)==item['bytes'] and hashlib.sha256(data).hexdigest()==item['sha256']
    return data

with ThreadPoolExecutor(max_workers=4) as pool:
    pending={i:pool.submit(part,i) for i in range(min(8,len(manifest['parts'])))}
    for index,item in enumerate(manifest['parts']):
        data=pending.pop(index).result()
        assert item['offset']==total
        whole.update(data);total+=len(data)
        next_index=index+8
        if next_index<len(manifest['parts']):pending[next_index]=pool.submit(part,next_index)
        if (index+1)%8==0:print('Verified public parts',index+1,'/',len(manifest['parts']),flush=True)
assert total==manifest['bytes'] and whole.hexdigest()==manifest['sha256']
record=dict(status='passed',commit=commit,zip_url=publication['zip_url'],report_url=publication['report_url'],
            verified_tree_blobs=len(entries),public_zip_bytes=len(zip_data),public_zip_sha256=package['compact_sha256'],
            zip_crc_and_internal_manifest=True,public_archive_parts=len(manifest['parts']),
            public_archive_bytes=total,public_archive_sha256=whole.hexdigest(),
            archive_assembled_hash_verified_without_duplicate_disk_copy=True)
(STAGE/'PUBLIC_VERIFICATION.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record,indent=2),flush=True)
