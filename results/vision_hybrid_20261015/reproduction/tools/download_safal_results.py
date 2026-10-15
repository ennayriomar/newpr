"""Download and verify every part of the complete published SAFAL result archive."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request


def digest(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def download(destination, ref='main'):
    base = f'https://raw.githubusercontent.com/ennayriomar/newpr/{ref}/results/safal_full_model_archive/'
    destination.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(base+'manifest.json', timeout=60) as response:
        manifest = json.load(response)
    if manifest.get('schema_version') != 1:
        raise ValueError('Unsupported result archive manifest.')
    for part in manifest['parts']:
        name = part['name']
        if Path(name).name != name:
            raise ValueError('Unsafe archive part filename.')
        target = destination/name
        if not target.exists() or digest(target) != part['sha256']:
            temporary = target.with_suffix(target.suffix+'.download')
            with urllib.request.urlopen(base+name, timeout=60) as response, temporary.open('wb') as handle:
                shutil.copyfileobj(response, handle, length=1024*1024)
            if temporary.stat().st_size != part['bytes'] or digest(temporary) != part['sha256']:
                raise ValueError('Archive part checksum/size mismatch: '+name)
            temporary.replace(target)
        print('Verified '+name, flush=True)
    if Path(manifest['archive']).name != manifest['archive']:
        raise ValueError('Unsafe archive filename.')
    archive = destination/manifest['archive']
    if not archive.exists() or digest(archive) != manifest['sha256']:
        temporary = archive.with_suffix('.zip.download')
        with temporary.open('wb') as handle:
            for part in manifest['parts']:
                with (destination/part['name']).open('rb') as source:
                    shutil.copyfileobj(source, handle, length=1024*1024)
        if temporary.stat().st_size != manifest['bytes'] or digest(temporary) != manifest['sha256']:
            raise ValueError('Reassembled archive checksum/size mismatch.')
        temporary.replace(archive)
    print('Verified complete archive: '+str(archive), flush=True)
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--ref', default='main', help='Git commit or branch to download; use published commit for immutability')
    args = parser.parse_args()
    download(args.destination, args.ref)
