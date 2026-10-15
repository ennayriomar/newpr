"""Deterministic verified-data baseline/hybrid runner with immutable artifacts."""
import argparse
from collections import Counter
import csv
from dataclasses import asdict
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

os.environ.setdefault('MPLCONFIGDIR', '/workspace/.cache/matplotlib')
os.environ.setdefault('XDG_CACHE_HOME', '/workspace/.cache')

import numpy as np
from PIL import Image
import torch
import yaml

from .baselines import METHODS, FittedMethod, verify_sources
from .dense_features import DenseDINOv2
from .hybrid import DecisionThresholds, decide
from .official_ad2 import export_map
from .pipeline_metrics import PixelHistogram, adequacy_precision_curve, calibrate, metrics
from .splits import validate_partition, validate_category_roles
from .verify_dataset import Sample, discover


def sha256(path):
    with Path(path).open('rb') as f:
        return hashlib.file_digest(f, 'sha256').hexdigest()


def immutable_bytes(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != value:
            raise ValueError(f'Immutable artifact differs: {path}; use a new output directory.')
    else:
        tmp = path.with_suffix(path.suffix + '.tmp')
        tmp.write_bytes(value)
        tmp.replace(path)


def immutable_json(path, value):
    immutable_bytes(path, (json.dumps(value, sort_keys=True, indent=2, allow_nan=False)+'\n').encode())


def immutable_maps(path, maps):
    if Path(path).exists():
        with np.load(path, allow_pickle=False) as previous:
            if set(previous.files) != set(maps) or any(not np.array_equal(previous[k], v) for k, v in maps.items()):
                raise ValueError('Immutable prediction maps changed.')
        return
    stream = io.BytesIO()
    np.savez_compressed(stream, **maps)
    immutable_bytes(path, stream.getvalue())


def truth_map(root, sample, shape):
    if sample.mask:
        with Image.open(root/sample.mask) as im:
            truth = np.asarray(im) > 0
        if truth.shape != shape:
            raise ValueError('Native mask and prediction shape disagree.')
        return truth
    return np.zeros(shape, dtype=bool)


def choose_queries(samples, category, split, per_label, seed, normal_only=False):
    chosen = []
    for label in ['normal'] if normal_only else ['normal', 'anomaly']:
        candidates = sorted([s for s in samples if s.category == category and s.split == split and s.label == label], key=lambda s:s.image)
        count = len(candidates) if per_label is None else per_label
        if count > len(candidates) or not count:
            raise ValueError(f'Insufficient declared {category}/{split}/{label} queries.')
        order = np.random.default_rng(seed).permutation(len(candidates))[:count]
        chosen.extend(candidates[i] for i in order)
    return chosen


def require_calibration_role(episode):
    if episode['role'] != 'calibration' or episode.get('final_query_labels_used_for_tuning'):
        raise ValueError('Threshold fitting is allowed only on reserved calibration queries.')
    if any(q['split'] not in {'train','validation'} or q['label']!='normal' for q in episode.get('queries',[])):
        raise ValueError('Native-test images/defect labels cannot enter threshold fitting.')


def build_episodes(config, inventories):
    m2_config = json.loads(Path(config['role_config']).read_text())
    roles = m2_config['category_roles']
    prior_roles = {r['image_id']: r['experiment_role'] for r in map(json.loads, Path(config['role_manifest']).read_text().splitlines())}
    for dataset in roles:
        validate_category_roles(roles[dataset], sorted({s.category for s in inventories[dataset]}))
    episodes, fingerprints, query_roles = [], {}, {}

    def add(dataset, category, role, seed, queries, supports):
        validate_partition([s.image for s in supports], [], [q.image for q in queries])
        if any(s.split != 'train' or s.label != 'normal' for s in supports):
            raise ValueError('Only verified training normals can fit model support.')
        if role == 'calibration':
            for q in queries:
                original_role = prior_roles[f'{dataset}:{q.image}']
                if original_role not in {'calibration_support_candidate_pool', 'stress_calibration_normal'} or q.label!='normal' or q.split not in {'train','validation'}:
                    raise ValueError('Calibration uses an image outside the prior reserved role.')
        for q in queries:
            image_id = f'{dataset}:{q.image}'
            if image_id in query_roles and query_roles[image_id] != role:
                raise ValueError('Query reused between calibration, validation and final roles.')
            query_roles[image_id] = role
        for q in queries + supports:
            root = Path(config['roots'][dataset])
            fingerprints[f'{dataset}:{q.image}'] = dict(image_sha256=sha256(root/q.image), mask_sha256=sha256(root/q.mask) if q.mask else None)
        support_hashes = {fingerprints[f'{dataset}:{s.image}']['image_sha256'] for s in supports}
        query_hashes = {fingerprints[f'{dataset}:{q.image}']['image_sha256'] for q in queries}
        if support_hashes & query_hashes:
            raise ValueError('Exact image-content leakage between support and query.')
        for k in config['shots']:
            episodes.append(dict(dataset=dataset, category=category, role=role, seed=seed, shots=k,
                                 support=[asdict(s) for s in supports[:k]], queries=[asdict(q) for q in queries],
                                 candidate_pool_ids=[], acquisition_budget=0, protocol='A_strict_fixed_shot',
                                 final_query_labels_used_for_tuning=False))

    for dataset, category in config['calibration_categories'].items():
        samples = inventories[dataset]
        if dataset in roles and category not in roles[dataset]['calibration']:
            raise ValueError('Calibration category overlaps other declared roles.')
        if dataset == 'mvtec_ad2':
            candidates = [s for s in samples if s.category == category and prior_roles[f'{dataset}:{s.image}'] == 'stress_calibration_normal']
            candidates.sort(key=lambda s:s.image)
            n = config['ad2_calibration_normals'] or len(candidates)
            if len(candidates) < n:
                raise ValueError('Too few reserved AD2 calibration normals.')
            queries = [candidates[i] for i in np.random.default_rng(config['query_seed']).permutation(len(candidates))[:n]]
        else:
            queries = choose_queries(samples, category, 'train', config['calibration_normal_queries'], config['query_seed'], normal_only=True)
        query_ids={q.image for q in queries}
        train = sorted([s for s in samples if s.category == category and s.split == 'train' and s.label == 'normal' and s.image not in query_ids], key=lambda s:s.image)
        indices = np.random.default_rng(config['calibration_seed']).choice(len(train), max(config['shots']), replace=False)
        add(dataset, category, 'calibration', config['calibration_seed'], queries, [train[i] for i in indices])
    for spec in config['benchmarks']:
        dataset, category, role = spec['dataset'], spec['category'], spec['role']
        if role not in {'validation', 'final_test', 'stress_final_public'}:
            raise ValueError('Unknown evaluation role.')
        if dataset in roles and category not in roles[dataset].get(role, []):
            raise ValueError('Evaluation category disagrees with reserved category roles.')
        samples = inventories[dataset]
        queries = choose_queries(samples, category, 'test_public' if dataset == 'mvtec_ad2' else 'test', config['queries_per_label'], config['query_seed'])
        train = sorted([s for s in samples if s.category == category and s.split == 'train' and s.label == 'normal'], key=lambda s:s.image)
        for seed in config['seeds']:
            indices = np.random.default_rng(seed).choice(len(train), max(config['shots']), replace=False)
            add(dataset, category, role, seed, queries, [train[i] for i in indices])
    # Also check exact content across category-disjoint query roles.
    by_hash = {}
    for image_id, role in query_roles.items():
        digest = fingerprints[image_id]['image_sha256']
        if digest in by_hash and by_hash[digest] != role:
            raise ValueError('Identical image content occurs in distinct experimental query roles.')
        by_hash[digest] = role
    all_support_ids = {f"{e['dataset']}:{s['image']}" for e in episodes for s in e['support']}
    if all_support_ids & set(query_roles):
        raise ValueError('A support image is registered as an experimental query.')
    all_support_hashes = {fingerprints[image_id]['image_sha256'] for image_id in all_support_ids}
    if all_support_hashes & set(by_hash):
        raise ValueError('Exact content overlap between global support and query registries.')
    return dict(episodes=episodes, data_fingerprints=fingerprints, category_roles=roles,
                queries_by_role=dict(Counter(query_roles.values())),
                role_config_sha256=sha256(config['role_config']), role_manifest_sha256=sha256(config['role_manifest']),
                query_sampling='predeclared stratified native-label subset with fixed query seed; all if queries_per_label=null; no metric-guided selection',
                public_test_history='bottle/capsules had earlier feasibility evaluation; this is not a claim of a newly untouched test set')


def run_episode(episode, method, extractor, config, output, thresholds=None):
    dataset = episode['dataset']; root = Path(config['roots'][dataset])
    mode = 'anomalydino' if method == 'anomalydino' else 'subspacead' if method == 'subspacead' else 'hybrid'
    directory = output/'episodes'/episode['role']/dataset/episode['category']/f"seed-{episode['seed']}_k-{episode['shots']}"/method
    supports = [Sample(**s) for s in episode['support']]
    queries = [Sample(**q) for q in episode['queries']]
    if thresholds is None:
        require_calibration_role(episode)
    fitted = FittedMethod(method, [extractor.extract_dense(dataset, s, root, mode) for s in supports], config['models'])
    immutable_json(directory/'model.json', fitted.metadata)
    image_truth, image_scores, pixel_truth, pixel_scores, predictions, adequate = [], [], [], [], [], []
    histogram = PixelHistogram() if config['pixel_metric_representation'] == 'native_float16_histogram' else None
    pixels = 0
    for index, q in enumerate(queries):
        b = extractor.extract_dense(dataset, q, root, mode)
        result = fitted.predict(b)
        maps, score = result['maps'], result['image_score']
        pixels += maps['defect'].size
        if histogram is None and pixels > config['max_metric_pixels_per_episode']:
            raise MemoryError('Exact native metrics exceed the declared memory limit; choose a smaller scope or increase the limit with adequate resources.')
        native_truth = truth_map(root, q, maps['defect'].shape)  # offline only, after inference
        map_file = directory/f'query-{index:03d}.npz'
        # Metrics use the declared representation before artifact compression.
        # Float16 native-map storage is explicit, never described as float32.
        storage_maps = {name:value.astype(config['map_storage_dtype']) for name,value in maps.items()}
        if any(not np.isfinite(value).all() for value in storage_maps.values()):
            raise ValueError('Map storage conversion overflows; select float32 in a new plan.')
        if shutil.disk_usage(output).free < 256*1024**2:
            raise OSError('Less than 256 MiB remains; stopping before filling the dataset volume.')
        immutable_maps(map_file, storage_maps)
        action, evidence = (None, None)
        if thresholds is not None:
            if method == 'support_hybrid':
                action, evidence = decide(score, result['mean_adequacy'], thresholds)
            else:
                evidence = score >= thresholds.image_defect
                action = 'defective' if evidence else 'normal'
        record = dict(dataset=dataset, category=q.category, role=episode['role'], image_id=q.image,
                      seed=episode['seed'], shots=episode['shots'], method=method, image_score=score,
                      mean_support_adequacy=result['mean_adequacy'], action=action, raw_defect_evidence_flag=evidence,
                      threshold_origin='reserved calibration only' if thresholds else None,
                      map=str(map_file), original_size=list(b.original_size), grid=list(b.grid),
                      feature_key=b.key, support_ids=[s.image for s in supports], candidate_pool_ids=[],
                      map_storage_dtype=config['map_storage_dtype'], pixel_metric_representation=config['pixel_metric_representation'],
                      selected_reference_ids=[], acquisition_budget=0,
                      valid_fields=dict(defect_map=True, support_adequacy=method == 'support_hybrid',
                                        predicted_acquisition_benefit=False, discrete_decision=thresholds is not None))
        if dataset == 'mvtec_ad2' and method == 'support_hybrid' and thresholds is not None:
            export = export_map(directory/'ad2_local_export', q.image, maps['defect'], thresholds.pixel_defect)
            record['official_format_export'] = export
        predictions.append(record)
        image_truth.append(q.label == 'anomaly'); image_scores.append(score)
        if histogram is not None:
            histogram.update(native_truth, maps['defect'])
        else:
            pixel_truth.append(native_truth.ravel()); pixel_scores.append(maps['defect'].ravel())
        if method == 'support_hybrid':
            adequate.append(result['mean_adequacy'])
    immutable_bytes(directory/'predictions.jsonl', ''.join(json.dumps(r, sort_keys=True, allow_nan=False)+'\n' for r in predictions).encode())
    py, ps = (None, None) if histogram is not None else (np.concatenate(pixel_truth), np.concatenate(pixel_scores))
    if thresholds is None:
        require_calibration_role(episode)
        if histogram is not None:
            from .pipeline_metrics import best_f1
            if any(image_truth) or histogram.positive.sum():
                raise ValueError('Normal-only calibration received defect labels.')
            values = dict(image_threshold=float(np.mean(image_scores)+3*np.std(image_scores)),
                          pixel_threshold=histogram.normal_threshold(),
                          procedure='reserved held-out training normals / AD2 normal validation only; mean+3std; native float16 histogram pixel cutoff',
                          calibration_pixel_representation='native_float16_histogram')
        else:
            values = calibrate(image_truth, image_scores, py, ps, normal_only=True)
        values.update(dataset=dataset, category=episode['category'], shots=episode['shots'], method=method,
                      calibration_ids=[f'{dataset}:{q.image}' for q in queries],
                      calibration_support_ids=[f'{dataset}:{s.image}' for s in supports],
                      adequacy_threshold=config['adequacy_threshold'], final_labels_used=False,
                      native_test_defect_labels_used=False, calibration_native_splits=sorted({q.split for q in queries}),
                      additional_calibration_normal_images=len(queries))
        immutable_json(directory/'thresholds.json', values)
        return values
    summary = dict(dataset=dataset, category=episode['category'], role=episode['role'], seed=episode['seed'], shots=episode['shots'], method=method,
                   queries=len(queries), image=metrics(image_truth, image_scores, thresholds.image_defect),
                   pixel=histogram.metrics(thresholds.pixel_defect) if histogram is not None else metrics(py, ps, thresholds.pixel_defect),
                   actions=dict(Counter(p['action'] for p in predictions)),
                   calibration_ids=list(thresholds.calibration_ids),
                   unique_query_count=len(queries), query_repeat_semantics='same locked queries across methods/k/support draws; draws are not independent query populations')
    if method == 'support_hybrid':
        summary['adequacy_precision'] = adequacy_precision_curve(adequate, image_truth, image_scores, thresholds.image_defect)
        accepted = np.array([p['action'] != 'unresolved/reference-insufficient' for p in predictions])
        correct = (np.asarray(image_scores) >= thresholds.image_defect) == np.asarray(image_truth)
        summary['selective_decision'] = dict(coverage=float(accepted.mean()), accepted=int(accepted.sum()), correct_accepted=int(correct[accepted].sum()), accuracy_accepted=float(correct[accepted].mean()) if accepted.any() else None,
                                            adequacy_threshold=thresholds.adequacy, semantics='empirical accepted-decision correctness; no guarantee')
    immutable_json(directory/'metrics.json', summary)
    print(json.dumps({k:summary[k] for k in ['dataset','category','role','seed','shots','method','queries']}), flush=True)
    return summary


def validate_artifact_ledger(output):
    ledger = json.loads((output/'artifact_ledger.json').read_text())
    for relative, expected in ledger.items():
        if sha256(output/relative) != expected:
            raise ValueError(f'Immutable run artifact was modified: {relative}')
    return len(ledger)


def reproduction_probe(output, manifest, extractor, config):
    episode = next(e for e in manifest['episodes'] if e['role'] != 'calibration')
    q = Sample(**episode['queries'][0]); root = Path(config['roots'][episode['dataset']])
    checks = []
    for method in METHODS:
        mode = 'anomalydino' if method == 'anomalydino' else 'subspacead' if method == 'subspacead' else 'hybrid'
        supports = [extractor.extract_dense(episode['dataset'], Sample(**s), root, mode) for s in episode['support']]
        independent = extractor.extract_dense(episode['dataset'], q, root, mode, use_cache=False)
        result = FittedMethod(method, supports, config['models']).predict(independent)
        previous = output/'episodes'/episode['role']/episode['dataset']/episode['category']/f"seed-{episode['seed']}_k-{episode['shots']}"/method/'query-000.npz'
        with np.load(previous, allow_pickle=False) as saved:
            if any(not np.array_equal(saved[k], v.astype(config['map_storage_dtype'])) for k, v in result['maps'].items()):
                raise ValueError('Independent real-image deterministic reproduction failed.')
        checks.append(dict(method=method, maps_bitwise_equal=True, image_id=q.image, cache_bypassed=True))
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    parser.add_argument('--reproduce', choices=['true', 'false'], default='true')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    config = yaml.safe_load(args.config.read_text())
    if args.output:
        config['output'] = str(args.output.resolve())
    if config['schema_version'] != 1 or config['shots'] != [1, 2, 4] or not config['seeds']:
        raise ValueError('This fixed-shot plan requires schema 1, k=1/2/4 and explicit seeds.')
    if config['pixel_metric_representation'] not in {'native_float16_histogram', 'native_float32_exact'}:
        raise ValueError('Unknown pixel metric representation.')
    if config['map_storage_dtype'] not in {'float16','float32'}:
        raise ValueError('Native-map storage must explicitly be float16 or float32.')
    if config['calibration_mode']!='normal_training_and_reserved_ad2_validation_only':
        raise ValueError('Calibration must exclude all native-test defect labels.')
    output = Path(config['output']); output.mkdir(parents=True, exist_ok=True)
    immutable_json(output/'config.json', config)
    sources = verify_sources()
    code = {str(p.relative_to(Path(__file__).parent)):sha256(p) for p in Path(__file__).parent.glob('*.py')}
    immutable_json(output/'source_provenance.json', dict(baselines=sources, safe_iad_code_sha256=code))
    for name in code:
        immutable_bytes(output/'implementation_snapshot'/name,(Path(__file__).parent/name).read_bytes())
    packages = ['torch','torchvision','numpy','Pillow','scipy','scikit-learn','opencv-python-headless','faiss-cpu','PyYAML','tifffile','tqdm','matplotlib']
    immutable_json(output/'runtime_versions.json', {name:importlib.metadata.version(name) for name in packages})
    # Reverify actual bytes/decoding/masks/native split contents before model work.
    for dataset, root in config['roots'].items():
        subprocess.run([sys.executable, '-m', 'safe_iad.verify_dataset', '--dataset', dataset, '--root', root,
                        '--output', str(output/'verification'), '--workers', str(config['verification_workers'])], check=True)
    inventories = {}
    for dataset, root in config['roots'].items():
        samples, _, issues, _ = discover(Path(root), dataset, None)
        if issues:
            raise ValueError(f'Dataset discovery errors: {issues}')
        inventories[dataset] = samples
    manifest = build_episodes(config, inventories)
    immutable_json(output/'split_manifest.json', manifest)
    upper_pixels = 0
    for episode in manifest['episodes']:
        for q in episode['queries']:
            with Image.open(Path(config['roots'][episode['dataset']])/q['image']) as im:
                upper_pixels += im.width*im.height
    # Three one-map baselines + six hybrid diagnostic maps, before compression.
    upper_bytes = upper_pixels*9*np.dtype(config['map_storage_dtype']).itemsize
    if not (output/'artifact_ledger.json').exists() and upper_bytes > 4*shutil.disk_usage(output).free:
        raise OSError(f'Configured native-map volume is {upper_bytes/1e9:.1f} GB before compression, exceeding the current disk preflight limit. Use adequate storage for this scope; do not silently drop images or outputs.')
    extractor = DenseDINOv2(config['feature_cache'], config['resolution'], config['layers'])
    immutable_json(output/'backbone.json', dict(checkpoint_sha256=extractor.checkpoint_hash, source_commit=extractor.source_commit,
                   eval_mode=not extractor.model.training, frozen=not any(p.requires_grad for p in extractor.model.parameters()),
                   resolution=config['resolution'], layers=config['layers'], torch_version=torch.__version__, numpy_version=np.__version__, device='cpu'))
    if (output/'artifact_ledger.json').exists():
        verified = validate_artifact_ledger(output)
        probes = reproduction_probe(output, manifest, extractor, config) if args.reproduce == 'true' else []
        print(json.dumps(dict(status='completed_run_integrity_verified', artifacts=verified, independent_real_image_checks=probes)), flush=True)
        return
    results = []
    # All three baseline fits/evaluations finish before the hybrid stage begins.
    for method in METHODS:
        thresholds = {}
        for episode in manifest['episodes']:
            if episode['role'] == 'calibration':
                values = run_episode(episode, method, extractor, config, output)
                thresholds[(episode['dataset'], episode['shots'])] = DecisionThresholds(values['image_threshold'], values['pixel_threshold'], values['adequacy_threshold'], tuple(values['calibration_ids']))
        for episode in manifest['episodes']:
            if episode['role'] != 'calibration':
                values = thresholds[(episode['dataset'], episode['shots'])]
                query_ids = {f"{episode['dataset']}:{q['image']}" for q in episode['queries']}
                if query_ids & set(values.calibration_ids):
                    raise ValueError('Calibration/final query overlap.')
                results.append(run_episode(episode, method, extractor, config, output, values))
    immutable_json(output/'metrics.json', results)
    rows = []
    for r in results:
        rows.append({k:r[k] for k in ['dataset','category','role','seed','shots','method','queries']} | {f'{level}_{key}':r[level][key] for level in ['image','pixel'] for key in ['auroc','ap','f1_max_offline','locked_f1','locked_threshold']} | dict(unresolved=r['actions'].get('unresolved/reference-insufficient',0)))
    stream = io.StringIO(newline='')
    writer = csv.DictWriter(stream, fieldnames=list(rows[0])); writer.writeheader(); writer.writerows(rows)
    immutable_bytes(output/'metrics.csv', stream.getvalue().encode())
    immutable_json(output/'completion.json', dict(status='completed_declared_scope', scope=config['scope'],
                   evaluation_episodes=len(results), prediction_records=sum(r['queries'] for r in results),
                   verification_images=sum(len(v) for v in inventories.values()),
                   private_submission='blocked: private images absent; real public/validation exports use official paths and per-file checks, not a complete server submission',
                   baseline_fidelity='official scoring-core variants at declared common backbone/settings; published full benchmark recipes have not been reproduced',
                   adequacy='bounded empirical diagnostic; no support-adequacy ground truth, calibrated probability or theoretical reliability guarantee',
                   configured_adequacy_threshold=config['adequacy_threshold'],
                   native_test_defect_labels_used_for_calibration=False,
                   reproducibility='deterministic CPU algorithms, pinned sources/weights, fingerprinted data and immutable maps/metrics; repeated completed invocation validates integrity and independently recomputes one real query per method',
                   full_benchmarks_run=False if config['scope'].startswith('feasibility') else True))
    ledger = {str(p.relative_to(output)):sha256(p) for p in output.rglob('*') if p.is_file() and 'verification' not in p.relative_to(output).parts}
    immutable_json(output/'artifact_ledger.json', ledger)
    print(json.dumps(json.loads((output/'completion.json').read_text())), flush=True)


if __name__ == '__main__':
    main()
