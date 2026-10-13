"""Immutable experiment files and provenance shared by the benefit pilot."""
from pathlib import Path
import hashlib
import json
import subprocess
import numpy as np


def sha256(path):
    with Path(path).open('rb') as fp:
        return hashlib.file_digest(fp, 'sha256').hexdigest()


def write_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(value, indent=2, allow_nan=False)+'\n'
    if path.exists() and path.read_text() != text:
        raise ValueError('Refusing to replace a different experiment artifact: '+str(path))
    if not path.exists():
        path.write_text(text)


def write_jsonl(path, rows):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    text = ''.join(json.dumps(row, allow_nan=False)+'\n' for row in rows)
    if path.exists() and path.read_text() != text:
        raise ValueError('Refusing to replace a different experiment artifact: '+str(path))
    if not path.exists():
        path.write_text(text)


def read_jsonl(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def implementation_hashes(names=None):
    """Fingerprint explicit dependencies; unrelated new modules need not matter."""
    root = Path(__file__).parent
    if names is None:
        names = [path.name for path in sorted(root.glob('*.py'))]
    return {str(name): sha256(root/Path(name)) for name in names}


def input_fingerprints(paths):
    # Keep the configured path rather than resolving symlinks: changing the
    # file reached through a dataset-root symlink must invalidate a resume.
    return {str(Path(path).absolute()): sha256(path) for path in paths}


def git_revision(directory):
    try:
        revision = subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'],
                                           text=True, stderr=subprocess.PIPE).strip()
        changed = subprocess.check_output(['git', '-C', str(directory), 'status', '--porcelain',
                                           '--untracked-files=no'], text=True, stderr=subprocess.PIPE).strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError('Cannot verify source revision: '+str(directory)) from exc
    if changed:
        raise ValueError('Cannot verify source revision with tracked local changes: '+str(directory))
    return revision


def _check_hash(path, expected, description):
    try:
        actual = sha256(path)
    except OSError as exc:
        raise ValueError(f'Completed-stage {description} is missing/unreadable: {path}. '
                         'Use a new output directory to rebuild.') from exc
    if actual != expected:
        raise ValueError(f'Completed-stage {description} changed: {path}. '
                         'Use a new output directory to rebuild.')


def _verify_dependencies(ledger, *, require_inputs=False, implementation_files=None):
    if require_inputs and (ledger.get('input_verification_version') != 1
                           or not ledger.get('input_sha256')
                           or not ledger.get('implementation_sha256')):
        raise ValueError('Legacy completion has no verified input/dependency fingerprints. '
                         'Use a new output directory to rebuild; artifact hashes alone are insufficient.')
    recorded = ledger.get('implementation_sha256', {})
    if implementation_files is not None and set(recorded) != {str(name) for name in implementation_files}:
        raise ValueError('Completed-stage implementation dependency set changed. '
                         'Use a new output directory to rebuild.')
    root = Path(__file__).parent
    for name, expected in recorded.items():
        _check_hash(root/Path(name), expected, 'implementation')
    for name, expected in ledger.get('input_sha256', {}).items():
        _check_hash(Path(name), expected, 'input')
    for directory, expected in ledger.get('git_revisions', {}).items():
        if git_revision(directory) != expected:
            raise ValueError('Completed-stage source revision changed: '+directory+
                             '. Use a new output directory to rebuild.')


def complete_stage(directory, names, extra=None):
    directory = Path(directory)
    ledger = {'files': {str(Path(name)): sha256(directory/name) for name in names},
              **(extra or {})}
    # Snapshots taken before feature extraction must still match at completion.
    _verify_dependencies(ledger)
    write_json(directory/'completion.json', ledger)


def verify_stage(directory, *, require_inputs=False, implementation_files=None):
    """Verify outputs plus every recorded input/code revision before cache reuse.

    Target builders set require_inputs=True to reject legacy output-only ledgers.
    Other callers can still explicitly use artifact-only stages without claiming
    input verification; any dependency fingerprints they record are checked.
    """
    directory = Path(directory)
    path = directory/'completion.json'
    if not path.exists():
        return False
    ledger = json.loads(path.read_text())
    for relative, expected in ledger['files'].items():
        _check_hash(directory/relative, expected, 'artifact')
    _verify_dependencies(ledger, require_inputs=require_inputs, implementation_files=implementation_files)
    return True


def save_maps(path, **fields):
    """Float16 export is explicit; evaluations use original float32 arrays."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    values = {key: np.asarray(value, dtype=np.float16) for key, value in fields.items()}
    if any(not np.isfinite(value).all() for value in values.values()):
        raise ValueError('Nonfinite map export')
    if path.exists():
        with np.load(path, allow_pickle=False) as old:
            if set(old.files) != set(values) or any(not np.array_equal(old[key], value) for key, value in values.items()):
                raise ValueError('Existing map differs: '+str(path))
    else:
        np.savez_compressed(path, **values)


def image_score(scores):
    import torch
    return float(torch.topk(scores, max(1, int(np.ceil(len(scores)*0.01)))).values.mean())
