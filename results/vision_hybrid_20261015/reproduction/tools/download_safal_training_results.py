"""Download the complete trained SAFAL banks, replay probes and score maps."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import urllib.request


def sha256(path):
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def download(destination, ref='main'):
    base = f'https://raw.githubusercontent.com/ennayriomar/newpr/{ref}/results/safal_training_20261014_archive/'
    destination.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(base+'manifest.json', timeout=60) as response:
        manifest = json.load(response)
    if manifest.get('schema_version') != 1 or Path(manifest['archive']).name != manifest['archive']:
        raise ValueError('Invalid training-result archive manifest.')
    archive = destination/manifest['archive']
    if archive.is_file() and archive.stat().st_size == manifest['bytes'] and sha256(archive) == manifest['sha256']:
        print('Verified existing complete archive: '+str(archive), flush=True)
        return archive
    temporary = archive.with_suffix('.zip.download')
    # Stream directly into one archive instead of retaining a duplicate part set.
    overall, count = hashlib.sha256(), 0
    with temporary.open('wb') as output:
        for part in manifest['parts']:
            if Path(part['name']).name != part['name']:
                raise ValueError('Unsafe archive-part name.')
            part_hash, part_bytes = hashlib.sha256(), 0
            with urllib.request.urlopen(base+part['name'], timeout=60) as response:
                while block := response.read(1024*1024):
                    output.write(block)
                    part_hash.update(block); overall.update(block)
                    part_bytes += len(block); count += len(block)
            if part_bytes != part['bytes'] or part_hash.hexdigest() != part['sha256']:
                raise ValueError('Training archive part checksum/size mismatch: '+part['name'])
            print('Verified '+part['name'], flush=True)
    if count != manifest['bytes'] or overall.hexdigest() != manifest['sha256']:
        raise ValueError('Complete training archive checksum/size mismatch.')
    temporary.replace(archive)
    (destination/'manifest.json').write_text(json.dumps(manifest, indent=2)+'\n')
    print('Verified complete archive: '+str(archive), flush=True)
    return archive


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--destination', type=Path, required=True)
    parser.add_argument('--ref', default='main', help='Branch or immutable published commit')
    args = parser.parse_args()
    download(args.destination, args.ref)
