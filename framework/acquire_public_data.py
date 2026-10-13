"""Extract verified research datasets outside the application checkout.

AD 2 can be streamed without retaining its 32.74 GB compressed archive.
Outputs stay in a staging directory until the complete checksum is verified.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import time
from pathlib import Path, PurePosixPath


class HashedStream:
    def __init__(self, stream):
        self.stream = stream
        self.digest = hashlib.sha256()
        self.bytes = 0
        self.last_log = time.monotonic()

    def read(self, size=-1):
        data = self.stream.read(size)
        self.digest.update(data)
        self.bytes += len(data)
        now = time.monotonic()
        if now - self.last_log >= 30:
            print(json.dumps({'downloaded_bytes': self.bytes}), flush=True)
            self.last_log = now
        return data


def extract_members(archive, staging, *, public_only, reserve_bytes):
    inventory = []
    extracted_bytes = 0
    for member in archive:
        path = PurePosixPath(member.name)
        if path.is_absolute() or '..' in path.parts:
            raise ValueError(f'Unsafe archive path: {member.name}')
        if not (member.isdir() or member.isfile()):
            raise ValueError(f'Unsupported archive member: {member.name}')
        retained = not (public_only and any(p in {'test_private', 'test_private_mixed'} for p in path.parts))
        inventory.append({'path': member.name, 'bytes': member.size, 'retained': retained, 'file': member.isfile()})
        if not retained:
            continue
        if member.isfile() and shutil.disk_usage(staging).free - member.size < reserve_bytes:
            raise OSError('Extraction would consume the reserved free disk space; staged data remains unverified.')
        archive.extract(member, staging, filter='data')
        if member.isfile():
            extracted_bytes += member.size
    return inventory, extracted_bytes


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument('--archive', type=Path)
    source.add_argument('--stream-url')
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    parser.add_argument('--public-only', action='store_true')
    parser.add_argument('--reserve-gib', type=float, default=3)
    args = parser.parse_args()
    if args.root.exists():
        raise FileExistsError(f'Refusing to overwrite existing data: {args.root}')
    staging = args.root.with_name(args.root.name + '.unverified')
    staging.mkdir(parents=True, exist_ok=False)
    process = None
    started = time.monotonic()
    report = {'status': 'unverified', 'source': args.stream_url or str(args.archive), 'expected_sha256': args.sha256, 'public_only': args.public_only}
    args.report.parent.mkdir(parents=True, exist_ok=True)
    try:
        if args.archive:
            with args.archive.open('rb') as src:
                actual_hash = hashlib.file_digest(src, 'sha256').hexdigest()
            if actual_hash != args.sha256:
                raise ValueError('Archive SHA-256 does not match the reference checksum.')
            with tarfile.open(args.archive, 'r:*') as archive:
                inventory, extracted_bytes = extract_members(archive, staging, public_only=args.public_only, reserve_bytes=int(args.reserve_gib * 1024**3))
            source_bytes = args.archive.stat().st_size
        else:
            process = subprocess.Popen(['curl', '--fail', '--location', '--connect-timeout', '30', '--speed-time', '120', '--speed-limit', '1024', '--silent', '--show-error', args.stream_url], stdout=subprocess.PIPE)
            reader = HashedStream(process.stdout)
            with tarfile.open(fileobj=reader, mode='r|gz', bufsize=1024 * 1024) as archive:
                inventory, extracted_bytes = extract_members(archive, staging, public_only=args.public_only, reserve_bytes=int(args.reserve_gib * 1024**3))
            while reader.read(8 * 1024**2):
                pass
            process.stdout.close()
            if process.wait() != 0:
                raise RuntimeError('curl failed; streamed archive integrity is unverified.')
            actual_hash = reader.digest.hexdigest()
            source_bytes = reader.bytes
            if actual_hash != args.sha256:
                raise ValueError('Stream SHA-256 does not match the reference checksum.')
        # No staged images may be used until archive integrity is established.
        staging.rename(args.root)
        report.update(status='verified_and_extracted', actual_sha256=actual_hash, source_bytes=source_bytes, extracted_bytes=extracted_bytes, elapsed_seconds=time.monotonic() - started, inventory=inventory)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
        print(json.dumps({k: v for k, v in report.items() if k != 'inventory'}), flush=True)
    except BaseException as exc:
        if process is not None and process.poll() is None:
            process.terminate()
            process.wait()
        report.update(status='failed_unverified', error=str(exc), staged_root=str(staging), elapsed_seconds=time.monotonic() - started)
        args.report.write_text(json.dumps(report, indent=2) + '\n')
        raise


if __name__ == '__main__':
    main()
