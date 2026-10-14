"""Package completed SAFAL tuning; invoke only after root confirms all audits.

Creates one compact code/example-model ZIP and one complete result ZIP. Parts
are described by offsets/hashes without a second on-disk copy; publication can
stream each 8 MiB range from the retained complete archive.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import stat
import sys
import zipfile


TOOLS = Path('/workspace/tools')
VENDOR = Path('/tmp/safal_release_v050/safal_full_model/vendor')
RUN = Path('/tmp/safal_tuning_20261014')
STAGE = Path('/tmp/safal_tuning_release_20261014')
PART_SIZE = 8*1024**2
COMPACT_LIMIT = 90*1024**2
EXCLUDED = {'__pycache__', '.git', '.venv', 'venv', 'build', 'dist', '.aws', '.codex', '.agents'}
REPORT_EXTENSIONS = {'.json', '.jsonl', '.csv', '.md', '.txt', '.log', '.html', '.png', '.pdf', '.svg', '.py'}
SELECTED = (
    'mvtec_ad-cable-k4-seed17', 'mvtec_ad-hazelnut-k4-seed17',
    'mvtec_ad-transistor-k4-seed17', 'visa-macaroni2-k4-seed17', 'visa-pcb2-k4-seed17',
)


def digest(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def write_json(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def permitted(relative):
    return (not any(part in EXCLUDED or part.endswith('.egg-info') for part in relative.parts)
            and relative.suffix not in {'.pyc', '.pyo'}
            and not any(part == '.env' or part.startswith('.env.') for part in relative.parts))


def files_under(root):
    for path in sorted(root.rglob('*')):
        relative = path.relative_to(root)
        if not permitted(relative):
            continue
        if path.is_symlink():
            raise ValueError('Release inputs must not contain symlinks: '+str(path))
        if path.is_file():
            yield path, relative


def copy_file(path, destination):
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(path, destination)


def path_audit(name):
    path = PurePosixPath(name)
    if path.is_absolute() or '..' in path.parts or '\\' in name or not permitted(path):
        raise ValueError('Unsafe archive path: '+name)


def zip_info(name, executable=False):
    path_audit(name)
    info = zipfile.ZipInfo(name, date_time=(2026, 10, 14, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = (stat.S_IFREG | (0o755 if executable else 0o644)) << 16
    return info


def make_archive(destination, entries, prefix, manifest):
    with zipfile.ZipFile(destination, 'w', compression=zipfile.ZIP_DEFLATED,
                         compresslevel=6, allowZip64=True) as archive:
        for path, name in entries:
            info = zip_info(prefix+'/'+name, executable=path.suffix == '.sh')
            with path.open('rb') as source, archive.open(info, 'w', force_zip64=True) as output:
                shutil.copyfileobj(source, output, length=1024**2)
        archive.writestr(zip_info(prefix+'/MANIFEST.sha256.json'),
                         json.dumps(manifest, indent=2, sort_keys=True)+'\n')


def verify_archive(path, prefix, manifest):
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)):
            raise ValueError('Duplicate ZIP paths: '+str(path))
        for info in archive.infolist():
            path_audit(info.filename)
            if stat.S_ISLNK(info.external_attr >> 16):
                raise ValueError('ZIP contains a symlink: '+info.filename)
        expected_names = {prefix+'/'+name for name in manifest} | {prefix+'/MANIFEST.sha256.json'}
        if set(names) != expected_names or archive.testzip() is not None:
            raise ValueError('ZIP schema or CRC verification failed: '+str(path))
        for name, expected in manifest.items():
            with archive.open(prefix+'/'+name) as handle:
                actual = hashlib.file_digest(handle, 'sha256').hexdigest()
            if actual != expected:
                raise ValueError('ZIP internal SHA256 mismatch: '+name)
        archived_manifest = json.loads(archive.read(prefix+'/MANIFEST.sha256.json'))
        if archived_manifest != manifest:
            raise ValueError('ZIP manifest differs from packaged file inventory.')


def require_ready(run, audit_paths):
    for name in ['selection.lock.json', 'verification/completion.json', 'summary.json', 'report.md', 'unit_tests.log']:
        if not (run/name).is_file():
            raise ValueError('Completed audited result required before packaging: '+name)
    if not audit_paths:
        raise ValueError('Supply at least one passed artifact audit with --audit-json.')
    audits = []
    for path in audit_paths:
        document = json.loads(path.read_text())
        if document.get('status') != 'passed':
            raise ValueError('Required independent artifact audit did not pass: '+str(path))
        audits.append({'path': str(path), 'sha256': digest(path), 'status': 'passed'})
    complete = json.loads((run/'verification/completion.json').read_text())
    if (complete.get('unique_queries'), complete.get('paired_cases'), complete.get('method_rows')) != (100, 300, 900):
        raise ValueError('Verification scope is incomplete or differs from the declared 100/300/900 run.')
    if complete.get('selection_lock_sha256') != digest(run/'selection.lock.json'):
        raise ValueError('Verification completion refers to a different selection lock.')
    models = sorted((run/'models').glob('*/model.npz'))
    probes = sorted((run/'verification').glob('*/replay_probe.npz'))
    maps = sorted((run/'verification').glob('*/query-*.npz'))
    if (len(models), len(probes), len(maps)) != (15, 15, 300):
        raise ValueError('Expected all15 fitted models,15 replay probes and300 metric map files.')
    for episode in SELECTED:
        for extension in ['json', 'npz']:
            if not (run/'models'/episode/('model.'+extension)).is_file():
                raise ValueError('Fixed k4/seed17 example model is missing: '+episode)
        document = json.loads((run/'models'/episode/'model.json').read_text())
        if document.get('kind') != 'TunableSubspaceSearch' or len(document.get('support_ids', [])) != 4:
            raise ValueError('Unexpected selected model type or support budget: '+episode)
    return audits


NOTICE = '''# Data-derived fitted-bank notice

MVTec AD (MVTec Software GmbH) data-derived cable/hazelnut/transistor banks:
CC BY-NC-SA 4.0, https://www.mvtec.com/research-teaching/datasets/mvtec-ad .
VisA (Amazon Science) data-derived macaroni2/pcb2 banks: CC BY 4.0,
https://github.com/amazon-science/spot-diff . Respect applicable attribution,
noncommercial and share-alike terms. Dataset images are excluded.

Pinned DINOv2/SubspaceAD/AnomalyDINO/AD2 snapshots retain upstream licenses.
No unlicensed VisionAD repository code is included. The new method is an
independent modified research implementation, not a faithful paper recipe.
The pretrained DINOv2 weight binary remains a separate verified download.
'''


README = '''# Development-selected SAFAL — 14 October 2026

Read reports/report.md and reports/summary.json for the measured outcome,
including defect losses, conditional paired intervals and limitations.
The chosen parameters were selected with native development labels, locked,
then compared on100 prelocked verification images within five previously
development-exposed categories. This is not a pristine-category final test,
full benchmark, probability-calibration result, SOTA claim or production proof.

The framework is under tools/. Five category-specific fitted normal banks
are in models/, chosen by fixed k4/seed17 rather than model performance.
Every model uses four support images and four extra normal calibration images;
it is not a strict four-image information budget. The15 primary fitted banks,
300 metric map files,15 replay probes, development raw scores, locks, full grid
and audits are preserved in the separately published complete result archive.
That archive also preserves superseded attempt banks and logs under attempts/;
they are historical outputs, not additional primary evaluation runs. Exact
total and superseded model-bank counts are recorded in its manifest. No old
probability/error head is attached to the changed decision rule.

## Portable prediction

Use Python3.12 and the pinned CPU setup. The bundled official DINOv2 source
includes its trusted source_manifest.sha256.json. Prepare the separately
verified pretrained weights once (the command also prepares another clean
source checkout); existing verified assets can be reused instead:

```bash
cd tools
bash install_safal.sh
source .venv/bin/activate
python -m safe_iad.safal_features prepare --destination ../safal_assets
python -m safe_iad.safal_tuned_predict --model ../models/mvtec_ad-hazelnut-k4-seed17/model --image /absolute/path/YOUR_IMAGE.png --output ../new_prediction --source-dir ../vendor/dinov2 --source-manifest ../vendor/dinov2/source_manifest.sha256.json --checkpoint ../safal_assets/dinov2_vitb14_pretrain.pth --cache-root ../feature_cache --threads 3
```

Choose the bank matching the image's category. Runtime paths in archived
metadata describe the original cloud machine; explicit path overrides make
inference portable while retaining encoder source/weight hashes, resolution,
layers and preprocessing. Native float32 maps differ from the declared256×256
evaluation maps. A/U and weights are empirical diagnostics, not probabilities.

## Reproduction and archived inputs

Inference needs only this compact bank/code bundle plus the frozen weights.
Reproducing parameter search additionally needs actual MVTec AD/VisA datasets
and the prior fitted-run manifest/predictions. That prior historical complete
result archive is approximately3GB and was published separately in
ennayriomar/newpr. Update previous_run/development_manifest, data roots,
verification-lock/exposure paths and encoder/cache paths in
tools/configs/safal_tuning_20261014.json to local copies; use a new output.
Do not treat copied absolute-path completion ledgers as a verified local resume.
Exact search/verification commands and selection rules are documented in
tools/docs/parameter_tuning.md. Legacy sources/checkpoints remain separate.

Raw datasets, pretrained weights, external feature caches and large prediction
arrays are omitted from this compact ZIP. The complete new-run archive includes
all run-derived arrays/models/reports (and preserved attempt logs), while raw
dataset images and encoder weights remain separate. MANIFEST.sha256.json
records every bundled file except itself. Read MODEL_ARTIFACT_NOTICE.md and
vendor licenses before reusing these data-derived banks.
'''


JOIN_SCRIPT = r'''"""Join/check 8 MiB result parts from a local directory or public HTTPS base URL."""
import argparse, hashlib, json, os
from pathlib import Path
import urllib.parse, urllib.request

def safe_name(name):
    if not isinstance(name,str) or not name or Path(name).name!=name or "\\" in name:
        raise ValueError("Unsafe archive/part filename")
    return name

def digest(path):
    with path.open("rb") as fp:return hashlib.file_digest(fp,"sha256").hexdigest()

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--manifest",type=Path,default=Path(__file__).with_name("manifest.json"))
    p.add_argument("--parts-dir",type=Path)
    p.add_argument("--base-url",help="Public HTTPS directory containing the named parts")
    p.add_argument("--destination",type=Path)
    a=p.parse_args();m=json.loads(a.manifest.read_text())
    destination=a.destination or Path(safe_name(m["archive"]))
    if destination.exists():
        if destination.stat().st_size==m["bytes"] and digest(destination)==m["sha256"]:
            print("Verified existing archive:",destination);return
        raise ValueError("Destination exists with different bytes; choose another path")
    if a.base_url and urllib.parse.urlparse(a.base_url).scheme!="https":raise ValueError("HTTPS base URL required")
    source=a.parts_dir or a.manifest.parent
    destination.parent.mkdir(parents=True,exist_ok=True)
    temporary=destination.with_name(destination.name+".partial")
    if temporary.exists():raise ValueError("A partial download already exists; use a new destination")
    total=0;whole=hashlib.sha256()
    try:
        with temporary.open("xb") as out:
            for part in m["parts"]:
                name=safe_name(part["name"])
                if part["offset"]!=total:raise ValueError("Noncontiguous part offsets")
                if a.base_url:
                    url=a.base_url.rstrip("/")+"/"+urllib.parse.quote(name,safe="")
                    handle=urllib.request.urlopen(url,timeout=60)
                    if urllib.parse.urlparse(handle.url).scheme!="https":raise ValueError("Non-HTTPS redirect")
                else:handle=(source/name).open("rb")
                count=0;h=hashlib.sha256()
                with handle:
                    while True:
                        block=handle.read(1024*1024)
                        if not block:break
                        count+=len(block)
                        if count>part["bytes"]:raise ValueError("Part exceeded declared length")
                        h.update(block);whole.update(block);out.write(block)
                if count!=part["bytes"] or h.hexdigest()!=part["sha256"]:raise ValueError("Part checksum mismatch: "+name)
                total+=count;print("Verified",name,flush=True)
        if total!=m["bytes"] or whole.hexdigest()!=m["sha256"]:raise ValueError("Assembled ZIP checksum mismatch")
        os.replace(temporary,destination);print("Verified complete archive:",destination)
    except Exception:
        if temporary.exists():temporary.unlink()
        raise

if __name__=="__main__":main()
'''


def package(run, stage, audit_paths, *, omit_compact_figures=False):
    audits = require_ready(run, audit_paths)
    if stage.exists():
        raise ValueError('Preserve previous outputs; choose a new --stage directory.')
    source_files, vendor_files, run_files = list(files_under(TOOLS)), list(files_under(VENDOR)), list(files_under(run))
    if not (VENDOR/'dinov2/source_manifest.sha256.json').is_file():
        raise ValueError('Pinned portable DINOv2 source manifest is missing.')
    input_bytes = sum(path.stat().st_size for path, _ in run_files)
    required_free = input_bytes+COMPACT_LIMIT+256*1024**2
    if shutil.disk_usage(stage.parent).free < required_free:
        raise OSError('Insufficient disk for one complete ZIP plus compact staging; free bytes='+
                      str(shutil.disk_usage(stage.parent).free)+', conservative requirement='+str(required_free))
    stage.mkdir(parents=True)
    bundle = stage/'safal_tuned'
    for path, relative in source_files:
        copy_file(path, bundle/'tools'/relative)
    for path, relative in vendor_files:
        copy_file(path, bundle/'vendor'/relative)
    for episode in SELECTED:
        for extension in ['json', 'npz']:
            copy_file(run/'models'/episode/('model.'+extension), bundle/'models'/episode/('model.'+extension))
    for path, relative in run_files:
        if relative.parts[0] == 'models' or path.suffix not in REPORT_EXTENSIONS:
            continue
        if omit_compact_figures and path.suffix in {'.png', '.pdf', '.svg'}:
            continue
        copy_file(path, bundle/'reports'/relative)
    # Include separately supplied audit files even if they live outside RUN.
    for path in audit_paths:
        if not path.resolve().is_relative_to(run.resolve()):
            copy_file(path, bundle/'reports/external_audits'/path.name)
    (bundle/'BUNDLE_README.md').write_text(README)
    (bundle/'MODEL_ARTIFACT_NOTICE.md').write_text(NOTICE)
    compact_entries = [(path, relative.as_posix()) for path, relative in files_under(bundle)]
    compact_manifest = {name: digest(path) for path, name in compact_entries}
    write_json(bundle/'MANIFEST.sha256.json', compact_manifest)
    compact = stage/'safal_tuned_20261014.zip'
    make_archive(compact, compact_entries, 'safal_tuned', compact_manifest)
    verify_archive(compact, 'safal_tuned', compact_manifest)
    if compact.stat().st_size >= COMPACT_LIMIT:
        write_json(stage/'COMPACT_TOO_LARGE.json', {'status': 'failed', 'bytes': compact.stat().st_size,
                   'limit_bytes': COMPACT_LIMIT, 'action': 'Use a new stage with --omit-compact-figures; preserve allfive models.'})
        raise ValueError('Compact ZIP is >=90MiB; size failure recorded, no large full ZIP created.')
    # Exact source bytes are rechecked against the archive snapshot manifest.
    if any(digest(path) != compact_manifest['tools/'+relative.as_posix()] for path, relative in source_files):
        raise ValueError('Framework source changed during packaging.')
    (stage/(compact.name+'.sha256')).write_text(digest(compact)+'  '+compact.name+'\n')

    full_entries = [(path, relative.as_posix()) for path, relative in run_files]
    full_entries += [(bundle/'MODEL_ARTIFACT_NOTICE.md', 'MODEL_ARTIFACT_NOTICE.md'),
                     (bundle/'BUNDLE_README.md', 'BUNDLE_README.md')]
    for path in audit_paths:
        if not path.resolve().is_relative_to(run.resolve()):
            full_entries.append((path, 'external_audits/'+path.name))
    if len({name for _, name in full_entries}) != len(full_entries):
        raise ValueError('Complete archive has colliding input names.')
    full_manifest = {name: digest(path) for path, name in full_entries}
    primary_banks = [name for name in full_manifest if name.startswith('models/') and name.endswith('/model.npz')]
    superseded_banks = [name for name in full_manifest if name.startswith('attempts/') and name.endswith('/model.npz')]
    total_model_files = [name for name in full_manifest if name.endswith('/model.npz')]
    full = stage/'safal_tuning_full_results_20261014.zip'
    make_archive(full, full_entries, 'safal_tuning_results', full_manifest)
    verify_archive(full, 'safal_tuning_results', full_manifest)
    full_sha = digest(full)
    (stage/(full.name+'.sha256')).write_text(full_sha+'  '+full.name+'\n')
    parts = []
    with full.open('rb') as handle:
        offset = 0
        while data := handle.read(PART_SIZE):
            parts.append({'name': full.name+f'.part{len(parts):03d}', 'offset': offset,
                          'bytes': len(data), 'sha256': hashlib.sha256(data).hexdigest()})
            offset += len(data)
    downloads = stage/'archive_metadata'
    record = {'schema_version': 1, 'archive': full.name, 'bytes': full.stat().st_size,
              'sha256': full_sha, 'part_size': PART_SIZE, 'parts': parts,
              'archive_files': len(full_manifest)+1, 'fitted_model_banks': len(primary_banks),
              'fitted_model_bank_scope': 'primary completed run only; superseded attempts counted separately',
              'primary_fitted_model_banks': len(primary_banks),
              'total_model_npz_files': len(total_model_files),
              'superseded_model_banks': len(superseded_banks),
              'superseded_model_paths': superseded_banks, 'replay_probes': 15,
              'metric_map_files': 300, 'native_dataset_images_or_pretrained_weights': False,
              'parts_stored_locally': False,
              'publication_note': 'Stream each listed offset/length from the retained ZIP; physical parts are not duplicated locally.'}
    write_json(downloads/'manifest.json', record)
    (downloads/'join.py').write_text(JOIN_SCRIPT)
    (downloads/'README.md').write_text('''# Complete measured tuning outputs

The15 primary fitted banks,15 replay probes,300 three-method metric map files,
development raw scores, full parameter grid, frozen selection/query locks,
reports and audits are in this complete archive. Superseded attempt banks and
logs are also retained under attempts/ and explicitly counted separately in
manifest.json; these are not additional primary runs. Original run files and the
assembled ZIP are retained in the cloud workspace. Raw dataset images,
external feature caches and pretrained backbone weights are separate.

Download this folder's manifest.json and join.py, then assemble/check public
parts without retaining a second part copy:

```bash
python join.py --base-url https://raw.githubusercontent.com/ennayriomar/newpr/PUBLISHED_COMMIT/ARCHIVE_DIRECTORY --destination safal_tuning_full_results_20261014.zip
```

Replace PUBLISHED_COMMIT/ARCHIVE_DIRECTORY with the published immutable location.
For already downloaded local parts, use --parts-dir /path/to/parts. Every part
and the assembled ZIP SHA256 is checked. The ZIP's internal manifest checks
each uncompressed file; read the measured report and artifact license notice.
Copied cloud paths do not claim a new-machine verified resume.
''')
    verification = {
        'status': 'passed', 'compact_archive': compact.name, 'compact_bytes': compact.stat().st_size,
        'compact_sha256': digest(compact), 'compact_files': len(compact_manifest)+1,
        'compact_models': list(SELECTED), 'compact_model_choice': 'fixed k4/seed17 per category, not performance',
        'full_archive': full.name, 'full_bytes': full.stat().st_size, 'full_sha256': full_sha,
        'full_files': len(full_manifest)+1, 'full_parts': len(parts),
        'part_files_duplicated': False, 'source_bytes_identical': True,
        'zip_crc_path_and_all_internal_file_hashes_verified': True, 'audits': audits,
        'fitted_model_banks': len(primary_banks),
        'fitted_model_bank_scope': 'primary completed run only; superseded attempts counted separately',
        'primary_fitted_model_banks': len(primary_banks),
        'total_model_npz_files': len(total_model_files), 'superseded_model_banks': len(superseded_banks),
        'replay_probes': 15, 'metric_map_files': 300,
        'omitted_from_compact': ['raw datasets', 'backbone binary', 'external caches',
                                'development raw NPZ', 'verification raw/maps/probes', 'other10 fitted banks'],
    }
    write_json(stage/'PACKAGE_VERIFICATION.json', verification)
    print(json.dumps(verification, indent=2), flush=True)
    return verification


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=RUN)
    parser.add_argument('--stage', type=Path, default=STAGE)
    parser.add_argument('--audit-json', type=Path, action='append', required=True)
    parser.add_argument('--confirm-ready', action='store_true', help='Root has confirmed final results and audits are complete.')
    parser.add_argument('--omit-compact-figures', action='store_true')
    args = parser.parse_args()
    if not args.confirm_ready:
        parser.error('Preparation only: pass --confirm-ready after final results/audits are confirmed.')
    try:
        package(args.run, args.stage, args.audit_json, omit_compact_figures=args.omit_compact_figures)
    except Exception as exc:
        print(json.dumps({'status': 'failed', 'error': str(exc)}), file=sys.stderr, flush=True)
        raise


if __name__ == '__main__':
    main()
