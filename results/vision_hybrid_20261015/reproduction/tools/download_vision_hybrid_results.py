"""Download and verify the published complete study archive without Git cloning."""
from pathlib import Path,PurePosixPath
import argparse
import hashlib
import json
import os
import re
import tarfile
import urllib.parse
import urllib.request


def safe_relative(value):
    p=PurePosixPath(value)
    if not value or p.is_absolute() or '..' in p.parts or '\\' in value:
        raise ValueError('Unsafe archive-relative path.')
    return p


def digest(path):
    with path.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()


def download(ref,destination,extract=False):
    if not re.fullmatch(r'[0-9a-f]{40}',ref):
        raise ValueError('Use the immutable40-character publication commit from the release README.')
    base='https://raw.githubusercontent.com/ennayriomar/newpr/'+ref+'/results/vision_hybrid_20261015_archive/'
    with urllib.request.urlopen(base+'manifest.json',timeout=60) as response:manifest=json.load(response)
    destination=Path(destination);destination.parent.mkdir(parents=True,exist_ok=True)
    if destination.exists():
        if destination.stat().st_size!=manifest['bytes'] or digest(destination)!=manifest['sha256']:
            raise ValueError('Destination exists with different bytes; choose a new destination.')
    else:
        partial=destination.with_name(destination.name+'.partial')
        if partial.exists():raise ValueError('A previous partial file exists; preserve it and choose another destination.')
        total=0;whole=hashlib.sha256()
        try:
            with partial.open('xb') as out:
                for item in manifest['parts']:
                    name=str(safe_relative(item['name']))
                    if '/' in name or item['offset']!=total:raise ValueError('Noncontiguous/unsafe part manifest.')
                    h=hashlib.sha256();count=0
                    with urllib.request.urlopen(base+urllib.parse.quote(name,safe=''),timeout=60) as response:
                        if not response.url.startswith('https://raw.githubusercontent.com/'):
                            raise ValueError('Unexpected download origin.')
                        while data:=response.read(1024*1024):
                            count+=len(data)
                            if count>item['bytes']:raise ValueError('Part exceeded declared length.')
                            h.update(data);whole.update(data);out.write(data)
                    if count!=item['bytes'] or h.hexdigest()!=item['sha256']:
                        raise ValueError('Part hash/length mismatch: '+name)
                    total+=count;print('Verified',name,flush=True)
            if total!=manifest['bytes'] or whole.hexdigest()!=manifest['sha256']:
                raise ValueError('Complete archive hash/length mismatch.')
            os.replace(partial,destination)
        except Exception:
            if partial.exists():partial.unlink()
            raise
    print('Verified archive:',destination,flush=True)
    if extract:
        folder=destination.with_name(destination.name.removesuffix('.tar.gz')+'_extracted')
        if folder.exists():raise ValueError('Extraction destination already exists.')
        with tarfile.open(destination,'r:gz') as archive:
            for member in archive.getmembers():
                path=safe_relative(member.name)
                if path.parts[0]!='vision_hybrid_results' or member.issym() or not (member.isfile() or member.isdir() or member.islnk()):
                    raise ValueError('Unexpected archive member type/root.')
                if member.islnk():
                    target=safe_relative(member.linkname)
                    if target.parts[0]!='vision_hybrid_results':raise ValueError('Hardlink leaves archive root.')
            folder.mkdir();archive.extractall(folder,filter='data')
        root=folder/'vision_hybrid_results';files=json.loads((root/'MANIFEST.sha256.json').read_text())
        cache={}
        for name,expected in files.items():
            relative=safe_relative(name);p=root/str(relative)
            if p.is_symlink() or not p.is_file():raise ValueError('Missing or unsafe extracted artifact.')
            st=p.stat();key=(st.st_dev,st.st_ino,st.st_size)
            if key not in cache:cache[key]=digest(p)
            if cache[key]!=expected:raise ValueError('Extracted file SHA256 mismatch: '+name)
        print('Verified extracted files:',len(files),'at',root,flush=True)
    return destination


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--ref',required=True,help='Immutable40-character payload commit')
    p.add_argument('--destination',type=Path,default=Path('vision_hybrid_full_results_20261015.tar.gz'))
    p.add_argument('--extract',action='store_true')
    a=p.parse_args();download(a.ref,a.destination,a.extract)


if __name__=='__main__':main()
