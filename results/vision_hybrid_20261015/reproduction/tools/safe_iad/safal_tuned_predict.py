"""Portable image inference for a selected TunableSubspaceSearch checkpoint.

Encoder semantics are loaded from the trained checkpoint and verified against
the real pinned DINOv2 extractor. Runtime paths/CPU threads may be overridden;
the trained resolution, layers, feature aggregation and checkpoint cannot.
Outputs are detector evidence and operational diagnostics, not probabilities.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np

from .dense_features import restore_dense
from .safal_features import SAFALEncoder, validate_configuration
from .safal_tunable import TunableSubspaceSearch


ENCODER_SEMANTIC_FIELDS = (
    'backbone', 'checkpoint_sha256', 'source_commit', 'source_manifest_sha256',
    'resolution', 'layers', 'preprocessing_version', 'aggregation', 'spatial_transform',
    'device', 'dtype', 'pretrained_weights_loaded', 'frozen', 'evaluation_mode',
    'deterministic_algorithms', 'implementation_sha256',
)


def _sha256(path):
    with Path(path).open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def _prefix_paths(prefix):
    prefix = Path(prefix).expanduser().resolve()
    if prefix.suffix in {'.json', '.npz'}:
        prefix = prefix.with_suffix('')
    return Path(str(prefix)+'.json'), Path(str(prefix)+'.npz')


def _encoder_configuration(provenance, overrides):
    if not isinstance(provenance, dict) or not isinstance(provenance.get('encoder'), dict):
        raise ValueError('Trained checkpoint requires provenance.encoder from SAFALEncoder.metadata().')
    expected = provenance['encoder']
    missing = [name for name in ENCODER_SEMANTIC_FIELDS if name not in expected or expected[name] is None]
    if missing:
        raise ValueError('Checkpoint encoder metadata is incomplete: '+', '.join(missing))
    runtime = expected.get('runtime_config', {})
    if not isinstance(runtime, dict):
        raise ValueError('Checkpoint encoder runtime_config must be a dictionary.')
    config = {'resolution': expected['resolution'], 'layers': expected['layers']}
    for name, flag in [('source_dir', '--source-dir'), ('checkpoint', '--checkpoint'), ('cache_root', '--cache-root')]:
        value = overrides.get(name)
        value = runtime.get(name) if value is None else value
        if not isinstance(value, (str, Path)) or not str(value).strip():
            raise ValueError(f'Missing encoder runtime {name}; provide {flag}.')
        config[name] = Path(value).expanduser()
    threads = overrides.get('threads')
    config['threads'] = runtime.get('threads', 3) if threads is None else threads
    manifest = overrides.get('source_manifest')
    # A relocated source override must not inherit an old machine's manifest
    # path. The encoder auto-detects the trusted manifest in the new tree.
    if manifest is None and overrides.get('source_dir') is None:
        manifest = runtime.get('source_manifest')
    if manifest is not None:
        config['source_manifest'] = Path(manifest).expanduser()
    validate_configuration(config['resolution'], config['layers'], config['threads'])
    return expected, config


def _match_encoder(expected, actual):
    for name in ENCODER_SEMANTIC_FIELDS:
        if name not in actual or actual[name] != expected[name]:
            raise ValueError(f'Runtime encoder semantic field differs from trained checkpoint: {name}')


def run_inference(*, model, image, output, source_dir=None, checkpoint=None,
                  cache_root=None, threads=None, source_manifest=None):
    """Load a selected model and infer one image; accepts no masks or labels."""
    started = time.perf_counter()
    trained = TunableSubspaceSearch.load(model)
    expected, encoder_config = _encoder_configuration(
        trained.checkpoint_provenance,
        dict(source_dir=source_dir, checkpoint=checkpoint, cache_root=cache_root,
             threads=threads, source_manifest=source_manifest))
    encoder = SAFALEncoder(**encoder_config)
    encoder_metadata = encoder.metadata()
    _match_encoder(expected, encoder_metadata)
    encoder_seconds = time.perf_counter()-started
    image = Path(image).expanduser().resolve(strict=True)
    if not image.is_file():
        raise ValueError('Inference image must be a readable file.')
    tick = time.perf_counter()
    features = encoder.extract(image)
    feature_seconds = time.perf_counter()-tick
    tick = time.perf_counter()
    raw = trained.score_raw(features.tokens)
    prediction = trained.predict_from_raw(raw, trained.params, trained.calibration)
    score_seconds = time.perf_counter()-tick
    tick = time.perf_counter()
    selected_raw = prediction['rawpair']
    fields = {
        'defect_map': prediction['map'],
        'search_raw': selected_raw['search'],
        'subspace_raw': selected_raw['subspace'],
        'search_normalized': prediction['normalized_branches']['search'],
        'subspace_normalized': prediction['normalized_branches']['subspace'],
        'support_adequacy_diagnostic': prediction['patch_adequacy'],
        'uncertainty_diagnostic': prediction['patch_uncertainty'],
        'search_weight': prediction['weights']['search'],
        'subspace_weight': prediction['weights']['subspace'],
    }
    maps = {name: np.asarray(restore_dense(values, features), dtype=np.float32)
            for name, values in fields.items()}
    expected_shape = (features.original_size[1], features.original_size[0])
    if any(values.shape != expected_shape or not np.isfinite(values).all() for values in maps.values()):
        raise ValueError('Restored maps must be finite float32 arrays at the original image shape.')
    output = Path(output).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    map_path, prediction_path = output/'prediction_maps.npz', output/'prediction.json'
    if map_path.exists() or prediction_path.exists():
        raise ValueError('Inference output already exists; use a new output directory.')
    np.savez_compressed(map_path, **maps)
    restoration_seconds = time.perf_counter()-tick
    model_json, model_npz = _prefix_paths(model)
    cache_path = encoder.cache_root/(features.key+'.npz')
    result = {
        'schema_version': 1, 'image': str(image), 'image_sha256': _sha256(image),
        'image_score': prediction['image_score'], 'image_threshold': prediction['image_threshold'],
        'decision': 'defective' if prediction['image_alert'] else 'normal', 'pixel_threshold': 1.,
        'A': prediction['A'], 'U': prediction['U'], 'branch_disagreement': prediction['branch_disagreement'],
        'image_scores_branch': prediction['image_scores_branch'],
        'mean_weights': {name: float(values.mean()) for name, values in prediction['weights'].items()},
        'parameters': asdict(trained.params), 'parameters_id': trained.params.id,
        'support_ids': list(trained.support_ids), 'calibration': asdict(trained.calibration),
        'budget': {'initial_support_images': len(trained.support_ids), 'added_normal_references': 0,
                   'extra_normal_calibration_images': len(trained.calibration.calibration_ids)},
        'native_shape': list(expected_shape), 'grid': list(features.grid),
        'feature_tokens': features.tokens.shape[0], 'feature_dimension': features.tokens.shape[1],
        'feature_cache_key': features.key, 'feature_cache_hit': features.cache_hit,
        'map_dtype': 'float32', 'maps': str(map_path),
        'map_fields': list(maps), 'probabilities': False,
        'diagnostic_semantics': 'A/U are query-relative coverage and branch-disagreement diagnostics; '
                               'neither is correctness probability or a reliability guarantee.',
        'timing_seconds': {'load_model_and_encoder': encoder_seconds, 'extract_or_cache': feature_seconds,
                           'score': score_seconds, 'restore_export': restoration_seconds},
        'provenance': {
            'model_json_sha256': _sha256(model_json), 'model_npz_sha256': _sha256(model_npz),
            'map_npz_sha256': _sha256(map_path), 'feature_cache_sha256': _sha256(cache_path),
            'encoder_semantics': {name: encoder_metadata[name] for name in ENCODER_SEMANTIC_FIELDS},
            'encoder_runtime': encoder_metadata['runtime_config'],
            'runtime_versions': {name: encoder_metadata[name] for name in
                                 ['torch_version', 'numpy_version', 'pillow_version', 'python_version']},
            'trained_model_provenance': trained.checkpoint_provenance,
            'predictor_implementation_sha256': _sha256(Path(__file__)),
        },
    }
    prediction_path.write_text(json.dumps(result, indent=2, allow_nan=False)+'\n')
    return result


def main():
    parser = argparse.ArgumentParser(description='Infer one image with a verified selected tunable SAFAL model; no probability head.')
    parser.add_argument('--model', type=Path, required=True, help='Saved JSON/NPZ checkpoint prefix.')
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='New output directory for prediction JSON and float32 maps.')
    parser.add_argument('--source-dir', type=Path, help='Override the pinned DINOv2 source location.')
    parser.add_argument('--checkpoint', type=Path, help='Override the verified pretrained weights location.')
    parser.add_argument('--cache-root', type=Path, help='Override the feature-cache directory.')
    parser.add_argument('--threads', type=int, help='Override CPU threads; scoring semantics stay unchanged.')
    parser.add_argument('--source-manifest', type=Path, help='Trusted manifest for a source-only DINOv2 bundle.')
    args = parser.parse_args()
    result = run_inference(**vars(args))
    print(json.dumps({name: result[name] for name in ['decision', 'image_score', 'image_threshold', 'parameters_id', 'maps']}, indent=2))


if __name__ == '__main__':
    main()
