#!/usr/bin/env python3
"""Download, verify, and extract the complete published Safe IAD results."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
from pathlib import Path
import shutil
import tarfile
import tempfile
import time
import urllib.request

MANIFEST_URL = ('https://raw.githubusercontent.com/ennayriomar/newpr/main/'
                'results_archive/DOWNLOAD_MANIFEST.json')


def fetch(url, target):
    for attempt in range(3):
        try:
            request = urllib.request.Request(url, headers={'User-Agent': 'Safe-IAD-results-downloader'})
            with urllib.request.urlopen(request, timeout=180) as response:
                with target.open('wb') as output:
                    shutil.copyfileobj(response, output, length=1024*1024)
            return
        except Exception:
            target.unlink(missing_ok=True)
            if attempt == 2:
                raise
            time.sleep(2*(attempt+1))


class VerifiedParts:
    def __init__(self, parts, staging):
        self.parts = parts
        self.staging = staging
        self.index = 0
        self.fp = None
        self.hash = hashlib.sha256()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.pending = {}
        self.next_index = 0
        self.prefetch()

    def download_part(self, index):
        part = self.parts[index]
        path = self.staging/f'part-{index:04d}'
        fetch(part['url'], path)
        digest = hashlib.sha256()
        with path.open('rb') as fp:
            while data := fp.read(1024*1024):
                digest.update(data)
        if path.stat().st_size != part['bytes'] or digest.hexdigest() != part['sha256']:
            raise ValueError('Download checksum mismatch: '+part['name'])
        return path

    def prefetch(self):
        while self.next_index < len(self.parts) and len(self.pending) < 4:
            index = self.next_index
            self.pending[index] = self.executor.submit(self.download_part, index)
            self.next_index += 1

    def start_part(self):
        if self.index == len(self.parts):
            return False
        self.path = self.pending.pop(self.index).result()
        self.fp = self.path.open('rb')
        self.index += 1
        self.prefetch()
        if self.index % 10 == 0 or self.index == len(self.parts):
            print(f"Verified part {self.index}/{len(self.parts)}", flush=True)
        return True

    def read(self, size=-1):
        if size < 0:
            raise ValueError('Only bounded reads are supported')
        output = bytearray()
        while len(output) < size:
            if self.fp is None and not self.start_part():
                break
            data = self.fp.read(size-len(output))
            if data:
                self.hash.update(data)
                output.extend(data)
            else:
                self.fp.close()
                self.fp = None
                self.path.unlink()
        return bytes(output)

    def close(self):
        if self.fp is not None:
            self.fp.close()
        self.executor.shutdown(wait=True, cancel_futures=True)


def hash_file(path):
    digest = hashlib.sha256()
    with path.open('rb') as fp:
        while data := fp.read(1024*1024):
            digest.update(data)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', default='downloaded_results', help='Directory to extract into')
    parser.add_argument('--verify-only', action='store_true', help='Check every remote file without extracting')
    parser.add_argument('--manifest', default=MANIFEST_URL, help='Published download manifest URL')
    args = parser.parse_args()
    output = Path(args.output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='safe-iad-parts-') as temp:
        staging = Path(temp)
        fetch(args.manifest, staging/'manifest.json')
        manifest = json.loads((staging/'manifest.json').read_text())
        expected = {entry['path']: entry for entry in manifest['archive_entries']}
        if len(expected) != len(manifest['archive_entries']):
            raise ValueError('Duplicate paths in manifest')
        if not args.verify_only and shutil.disk_usage(output).free < manifest['original_result_bytes']+64*1024*1024:
            raise OSError('Extraction requires approximately 5 GB of free disk space; choose another --output')
        reader = VerifiedParts(manifest['parts'], staging)
        seen = set()
        try:
            with tarfile.open(fileobj=reader, mode='r|gz') as archive:
                for member in archive:
                    entry = expected.get(member.name)
                    if entry is None or member.name in seen or not member.isfile():
                        raise ValueError('Unexpected archive entry: '+member.name)
                    if member.size != entry['bytes']:
                        raise ValueError('Archive size mismatch: '+member.name)
                    target = (output/member.name).resolve()
                    try:
                        target.relative_to(output)
                    except ValueError:
                        raise ValueError('Unsafe archive path: '+member.name) from None
                    pending = None
                    destination = None
                    if not args.verify_only:
                        if target.exists():
                            if not target.is_file() or hash_file(target) != entry['sha256']:
                                raise FileExistsError('Existing file differs; choose another --output: '+str(target))
                        else:
                            target.parent.mkdir(parents=True, exist_ok=True)
                            pending = target.with_name(target.name+'.download-tmp')
                            destination = pending.open('wb')
                    digest = hashlib.sha256()
                    source = archive.extractfile(member)
                    assert source is not None
                    try:
                        while data := source.read(1024*1024):
                            digest.update(data)
                            if destination is not None:
                                destination.write(data)
                    finally:
                        source.close()
                        if destination is not None:
                            destination.close()
                    if digest.hexdigest() != entry['sha256']:
                        if pending is not None:
                            pending.unlink(missing_ok=True)
                        raise ValueError('Extracted checksum mismatch: '+member.name)
                    if pending is not None:
                        pending.replace(target)
                    seen.add(member.name)
                    if len(seen) % 500 == 0:
                        print(f'Verified {len(seen)}/{len(expected)} archive files', flush=True)
            while reader.read(1024*1024):
                pass
        finally:
            reader.close()
        if seen != set(expected):
            raise ValueError('Archive did not contain every expected file')
        if reader.hash.hexdigest() != manifest['archive_sha256']:
            raise ValueError('Complete archive checksum mismatch')
    print(f"Verified all {manifest['original_result_files']} original result files "
          f"and {len(manifest['parts'])} archive parts.", flush=True)
    if not args.verify_only:
        print('Results extracted to '+str(output/'safe_iad_full_results'))


if __name__ == '__main__':
    main()
