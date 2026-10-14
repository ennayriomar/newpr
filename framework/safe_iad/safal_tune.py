"""Finite development-only parameter selection, followed by a locked image check.

No verification scores or masks enter tune(). Existing checkpoint sources stay
unchanged. Native development labels explicitly select one global parameter set.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import itertools
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image
from sklearn.metrics import roc_auc_score
import torch
import torch.nn.functional as F

from .experiment_io import sha256, write_json, write_jsonl, read_jsonl, implementation_hashes
from .safal_cli import inventory, validate_episode
from .safal_features import SAFALEncoder
from .safal_tunable import Parameters, TunableSubspaceSearch
from .research_metrics import localization_metrics, thresholded_detection_metrics

CODE = ['safal_tune.py', 'safal_tunable.py', 'safal_features.py',
        'subspace_search.py', 'safal_cli.py', 'safal_model.py',
        'dense_features.py', 'patch_nn.py', 'verify_dataset.py',
        'experiment_io.py', 'research_metrics.py']


def parameter_grid(config):
    g = config['grid']
    settings = [('fixed', w) for w in g['fixed_search_weights']]
    settings += [(f, .5) for f in g['other_fusions']]
    result = [Parameters(v, q, a, f, w, t) for v, a, q, (f, w), t in
              itertools.product(g['explained_variance'], g['aggregation'],
                                g['normal_quantiles'], settings, g['image_thresholds'])]
    if len(result) != 768 or len({p.id for p in result}) != 768:
        raise ValueError('The predeclared protocol requires 768 unique cells.')
    return result


def eligible(p):
    return not (p.fusion == 'fixed' and p.search_weight in (0., 1.))


def changed_count(p):
    original = asdict(Parameters())
    return sum(value != original[key] for key, value in asdict(p).items())


def selection_key(row):
    return (-row['accuracy'], -row['mean_image_auroc'], row['false_positives'],
            row['changed_parameters'], row.get('feature_changes', 0), row['id'],
            row.get('feature_id', ''))


def select_candidate(rows):
    feasible = [r for r in rows if r['eligible'] and r['feasible']]
    if not feasible:
        raise ValueError('No hybrid preserves both baseline detection sets on development.')
    return min(feasible, key=selection_key)


def candidate_metrics(params, scores, cases, baselines, feature_id, feature_changes=0):
    scores = np.asarray(scores, dtype=np.float64)
    labels = np.array([c['label'] for c in cases], dtype=bool)
    decisions = scores >= params.image_threshold
    losses = {name: int(np.count_nonzero(labels & (np.asarray(values) >= 1.) & ~decisions))
              for name, values in baselines.items()}
    groups = sorted({c['episode_id'] for c in cases})
    aucs = []
    for group in groups:
        indices = [i for i, c in enumerate(cases) if c['episode_id'] == group]
        aucs.append(float(roc_auc_score(labels[indices], scores[indices])))
    return dict(id=params.id, params=asdict(params), eligible=eligible(params),
                feasible=all(v == 0 for v in losses.values()),
                accuracy=float(np.mean(decisions == labels)),
                correct=int(np.count_nonzero(decisions == labels)), cases=len(cases),
                misses=int(np.count_nonzero(labels & ~decisions)),
                false_positives=int(np.count_nonzero(~labels & decisions)),
                losses_vs_original=losses['original'], losses_vs_fixed=losses['fixed_avg'],
                mean_image_auroc=float(np.mean(aucs)),
                changed_parameters=changed_count(params), feature_id=feature_id,
                feature_changes=feature_changes)


def _json(path):
    return json.loads(Path(path).read_text())


def _check_hashes(values):
    for path, expected in values.items():
        if sha256(path) != expected:
            raise ValueError('Frozen input/artifact changed: '+path)


def _encoder(config, feature):
    encoder = dict(config['encoder'])
    encoder.update({k: feature[k] for k in ['resolution', 'layers', 'cache_root']})
    return SAFALEncoder(**encoder)


def _inventory(config):
    return {name: inventory(config, name) for name in config['roots']}


def preflight(config_path, output):
    config = _json(config_path)
    grid = parameter_grid(config)
    if sum(eligible(p) for p in grid) != 576:
        raise ValueError('Hybrid/control counts changed.')
    manifest = _json(config['development_manifest'])
    episodes = [e for e in manifest['episodes'] if e['shots'] == 4]
    lock = _json(config['verification_query_lock'])
    exposure = _json(config['known_exposure'])
    if sha256(config['verification_query_lock']) != config['verification_query_lock_sha256']:
        raise ValueError('Prelocked verification IDs changed.')
    if sha256(config['known_exposure']) != lock['known_exposure_sha256']:
        raise ValueError('Known exposure inventory changed.')
    if sha256(config['development_manifest']) != lock['existing_development_manifest_sha256']:
        raise ValueError('Development manifest changed.')
    if len(episodes) != 15 or len(lock['episodes']) != 15:
        raise ValueError('Expected 15 matched k4 bank episodes.')
    inventories = _inventory(config)
    known = set(exposure['native_query_ids'])
    dev_ids = set()
    check_ids = set()
    inputs = {str(Path(config_path).resolve()): sha256(config_path)}
    for key in ['development_manifest', 'verification_query_lock', 'known_exposure']:
        inputs[config[key]] = sha256(config[key])
    # Completion/resume checks must cover encoder and label-role inputs even
    # when no new encoder is constructed by the resumed command.
    checked_encoder = _encoder(config, config['feature_configs'][0])
    encoder_meta = checked_encoder.metadata()
    inputs[config['encoder']['checkpoint']] = sha256(config['encoder']['checkpoint'])
    for relative, digest in encoder_meta['source_files_sha256'].items():
        inputs[str(Path(config['encoder']['source_dir'])/relative)] = digest
    if config['encoder'].get('source_manifest'):
        path = config['encoder']['source_manifest']
        inputs[path] = sha256(path)
    for dataset, (root, _) in inventories.items():
        if dataset == 'visa':
            # discover() uses the official one-class split and all annotation
            # inventories; these assign labels/roles before any score fit.
            for path in [root/'split_csv/1cls.csv', *sorted(root.glob('*/image_anno.csv'))]:
                inputs[str(path)] = sha256(path)
    for dev, check in zip(episodes, lock['episodes']):
        for key in ['id', 'dataset', 'category', 'seed', 'shots', 'support_ids', 'calibration_ids']:
            if dev[key] != check[key]:
                raise ValueError('Development/check banks must be identical.')
        root, lookup = inventories[dev['dataset']]
        for e, destination in [(dev, dev_ids), (check, check_ids)]:
            validate_episode(e, lookup)
            for identifier in e['query_ids']:
                destination.add(e['dataset']+':'+identifier)
            for identifier in e['support_ids']+e['calibration_ids']+e['query_ids']:
                # Image hashes only: no verification masks or scores are read in tune.
                path = str(root/identifier)
                inputs[path] = sha256(path)
        previous = Path(config['previous_run'])/'episodes'/dev['id']/'predictions.jsonl'
        inputs[str(previous)] = sha256(previous)
    if len(dev_ids) != 100 or len(check_ids) != 100 or dev_ids & check_ids or known & check_ids:
        raise ValueError('Expected disjoint 100-image development/check partitions.')
    record = dict(schema_version=1, config=config, input_sha256=inputs,
                  implementation_sha256=implementation_hashes(CODE),
                  scope=lock['scope'], development_images=100, verification_images=100,
                  cases_per_partition=300, bank_episodes=15, grid_cells=768,
                  eligible_hybrids=576, endpoint_controls=192,
                  label_roles={'development': 'native labels permitted for global selection',
                               'verification': 'stratified IDs only before selection lock; no score/mask selection'},
                  old_error_head_used=False, pixel_threshold=1., smoothing='not run')
    write_json(output/'preflight.json', record)
    return config, episodes, lock['episodes'], inventories, record


def _save_raw(path, raw, bundle):
    path.parent.mkdir(parents=True, exist_ok=True)
    arrays = {'search': raw['search'].cpu().numpy(),
              **{'subspace_'+k: v.cpu().numpy() for k, v in raw['subspace'].items()}}
    np.savez_compressed(path, **arrays)
    return dict(path=str(path), sha256=sha256(path), feature_key=bundle.key,
                grid=list(bundle.grid), original_size=list(bundle.original_size),
                raw_dtype='float64')


def collect_development(config, episodes, inventories, feature, output):
    encoder = _encoder(config, feature)
    result, cases, baselines = [], [], {'original': [], 'fixed_avg': []}
    for e in episodes:
        root, lookup = inventories[e['dataset']]
        print('development', feature['id'], e['id'], flush=True)
        support = [encoder.extract(root/i).tokens for i in e['support_ids']]
        model = TunableSubspaceSearch(support, e['support_ids'], tuple(config['grid']['explained_variance']))
        calibration_raw, queries, records = [], [], []
        for index, identifier in enumerate(e['calibration_ids']+e['query_ids']):
            bundle = encoder.extract(root/identifier)
            raw = model.score_raw(bundle.tokens)
            raw_path = output/'development'/feature['id']/e['id']/f'raw-{index:03d}.npz'
            record = _save_raw(raw_path, raw, bundle)
            record.update(image_id=identifier, role='normal_calibration' if index < 4 else 'development_query')
            records.append(record)
            if index < 4:
                calibration_raw.append(raw)
            else:
                queries.append(raw)
                cases.append(dict(dataset=e['dataset'], category=e['category'], seed=e['seed'],
                                  episode_id=e['id'], query_id=identifier,
                                  label=int(lookup[identifier].label != 'normal')))
        old_rows = read_jsonl(Path(config['previous_run'])/'episodes'/e['id']/'predictions.jsonl')
        for name, legacy in [('original', 'safal'), ('fixed_avg', 'fixed_avg')]:
            by_id = {r['query_id']: r for r in old_rows if r['method'] == legacy}
            baselines[name].extend(by_id[i]['image_score'] for i in e['query_ids'])
        write_json(output/'development'/feature['id']/e['id']/'raw_manifest.json', records)
        result.append(dict(episode=e, model=model, normals=calibration_raw, queries=queries,
                           encoder=encoder.metadata()))
    return result, cases, baselines


def score_development(banks, params):
    values = []
    for bank in banks:
        model = bank['model']
        calibration = model.calibration_from_raw(bank['normals'], bank['episode']['calibration_ids'], params)
        values.extend(model.predict_from_raw(raw, params, calibration)['image_score'] for raw in bank['queries'])
    return np.asarray(values, dtype=np.float64)


def _freeze_models(banks, params, feature, output):
    for bank in banks:
        e, model = bank['episode'], bank['model']
        calibration = model.calibration_from_raw(bank['normals'], e['calibration_ids'], params)
        model.save(output/'models'/e['id']/'model', params, calibration,
                   dict(encoder=bank['encoder'], feature_id=feature['id'], episode=e,
                        k_plus_calibration=8, strict_k_image_few_shot=False,
                        parameter_selection='Native development labels; one global config, zero losses against both controls',
                        error_head=None, probabilities=False))


def tune(config_path, output):
    output = Path(output)
    if (output/'selection.lock.json').exists():
        verify_lock(config_path, output)
        return _json(output/'selection.lock.json')
    config, episodes, _, inventories, pre = preflight(config_path, output)
    features = config['feature_configs']
    banks, cases, baselines = collect_development(config, episodes, inventories, features[0], output)
    original = score_development(banks, Parameters())
    fixed = score_development(banks, Parameters(fusion='fixed'))
    deltas = {name: float(np.max(np.abs(scores-np.asarray(baselines[name]))))
              for name, scores in [('original', original), ('fixed_avg', fixed)]}
    if max(deltas.values()) > 1e-12:
        raise ValueError('Legacy k4 score parity failed: '+str(deltas))
    if not all(np.array_equal(scores >= 1, np.asarray(baselines[name]) >= 1)
               for name, scores in [('original', original), ('fixed_avg', fixed)]):
        raise ValueError('Legacy decisions changed.')
    labels = np.array([c['label'] for c in cases])
    correct_counts = {n: int(np.count_nonzero((np.asarray(s) >= 1) == labels)) for n, s in baselines.items()}
    if correct_counts != {'original': 243, 'fixed_avg': 240}:
        raise ValueError('Matched baseline counts changed.')
    write_json(output/'development'/'baseline_parity.json', dict(max_abs_score_delta=deltas, correct=correct_counts,
                                                               matched_shots=4, total_cases=300))
    fallback_p = Parameters(fusion='max', image_threshold=.5)
    fallback_scores = score_development(banks, fallback_p)
    fallback = candidate_metrics(fallback_p, fallback_scores, cases, baselines, features[0]['id'])
    if not fallback['feasible']:
        raise ValueError('Empirical max threshold .5 fallback is not feasible.')
    write_json(output/'development'/'fallback.json', fallback)
    grid, score_arrays = [], []
    params_grid = parameter_grid(config)
    cached_scores = {}
    for index, p in enumerate(params_grid):
        # Threshold changes the decision only; preserve exactly the same score.
        key = (p.explained_variance, p.normal_quantile, p.aggregation, p.fusion, p.search_weight)
        if key not in cached_scores:
            cached_scores[key] = score_development(banks, p)
        scores = cached_scores[key]
        grid.append(candidate_metrics(p, scores, cases, baselines, features[0]['id']))
        score_arrays.append(scores)
        if (index+1) % 64 == 0:
            print('grid', index+1, '/', len(params_grid), flush=True)
    winner = select_candidate(grid)
    params = Parameters(**winner['params'])
    write_json(output/'development'/'cases.json', cases)
    write_json(output/'development'/'grid.json', grid)
    np.savez_compressed(output/'development'/'grid_scores.npz', scores=np.stack(score_arrays),
                        ids=np.array([p.id for p in params_grid]),
                        original=np.array(baselines['original']), fixed_avg=np.array(baselines['fixed_avg']))
    write_json(output/'development'/'stage1_selection.json',
               dict(winner=winner, unconstrained_best=min([r for r in grid if r['eligible']], key=selection_key),
                    best_endpoint_control=min([r for r in grid if not r['eligible']], key=selection_key),
                    feasible_hybrids=sum(r['eligible'] and r['feasible'] for r in grid)))
    print('stage1 winner', json.dumps(winner), flush=True)
    comparisons = [winner]
    best_banks, best_feature, best_scores = banks, features[0], cached_scores[
        (params.explained_variance, params.normal_quantile, params.aggregation, params.fusion, params.search_weight)]
    for feature in features[1:]:
        new_banks, new_cases, new_baselines = collect_development(config, episodes, inventories, feature, output)
        if new_cases != cases or new_baselines != baselines:
            raise ValueError('Feature ablation lost matched cases.')
        scores = score_development(new_banks, params)
        row = candidate_metrics(params, scores, cases, baselines, feature['id'], 1)
        comparisons.append(row)
        if row['feasible'] and selection_key(row) < selection_key(select_candidate(comparisons[:-1])):
            best_banks, best_feature, best_scores = new_banks, feature, scores
    final = select_candidate(comparisons)
    if final['feature_id'] != best_feature['id']:
        raise ValueError('Feature selection bookkeeping failed.')
    write_json(output/'development'/'feature_comparison.json', comparisons)
    write_jsonl(output/'development'/'selected_predictions.jsonl',
                [c | dict(method='selected', score=float(s), threshold=params.image_threshold,
                          decision=bool(s >= params.image_threshold),
                          image_correct=bool((s >= params.image_threshold) == c['label']))
                 for c, s in zip(cases, best_scores)])
    _freeze_models(best_banks, params, best_feature, output)
    frozen = {str(p): sha256(p) for subdir in ['development', 'models']
              for p in sorted((output/subdir).rglob('*')) if p.is_file()}
    lock = dict(schema_version=1, winner=final, stage1_winner=winner, params=asdict(params),
                parameters_id=params.id, feature=best_feature, selection_key_definition=
                'max accuracy, max mean episode AUROC, min FP, min changed scalar params, min feature changes, parameter ID, feature ID',
                constraint='zero per-case detected-to-missed transitions vs BOTH original SAFAL and fixed average on development anomalies',
                scope=pre['scope'], native_development_labels_used=True,
                verification_scores_seen=False, verification_masks_seen=False,
                preflight_sha256=sha256(output/'preflight.json'), artifact_sha256=frozen,
                locked_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()))
    write_json(output/'selection.lock.json', lock)
    print('LOCKED', json.dumps(final), flush=True)
    return lock


def verify_lock(config_path, output):
    output = Path(output)
    lock = _json(output/'selection.lock.json')
    if sha256(output/'preflight.json') != lock['preflight_sha256']:
        raise ValueError('Selection preflight changed.')
    pre = _json(output/'preflight.json')
    if _json(config_path) != pre['config']:
        raise ValueError('Run config changed after selection.')
    if pre['implementation_sha256'] != implementation_hashes(CODE):
        raise ValueError('Scoring/selection implementation changed after selection.')
    _check_hashes(pre['input_sha256'])
    _check_hashes(lock['artifact_sha256'])
    if lock['verification_scores_seen'] or lock['verification_masks_seen']:
        raise ValueError('Invalid selection label/score roles.')
    return lock


def _metric_map(values, bundle):
    # Identical 256x256 metric geometry for every feature variant and control.
    tensor = values.detach().float().reshape(1, 1, *bundle.grid)
    return F.interpolate(tensor, (256, 256), mode='bilinear', align_corners=False)[0, 0].numpy()


def _mask(root, sample):
    if sample.label == 'normal':
        return np.zeros((256, 256), dtype=bool)
    if not sample.mask:
        raise ValueError('Anomalous native sample has no localization mask.')
    with Image.open(root/sample.mask) as image:
        return np.array(image.convert('L').resize((256, 256), Image.Resampling.NEAREST)) > 0


def verify(config_path, output):
    output = Path(output)
    lock = verify_lock(config_path, output)
    destination = output/'verification'
    if (destination/'completion.json').exists():
        complete = _json(destination/'completion.json')
        if complete['selection_lock_sha256'] != sha256(output/'selection.lock.json'):
            raise ValueError('Verification completion belongs to a different selection lock.')
        if complete['implementation_sha256'] != implementation_hashes(CODE):
            raise ValueError('Verification completion scoring implementation changed.')
        _check_hashes(complete['artifact_sha256'])
        _check_hashes(complete['mask_input_sha256'])
        return complete
    if destination.exists() and any(destination.iterdir()):
        raise ValueError('Partial verification exists; do not retune or silently reuse a partial check.')
    config = _json(config_path)
    episodes = _json(config['verification_query_lock'])['episodes']
    inventories = _inventory(config)
    base_encoder = _encoder(config, config['feature_configs'][0])
    selected_encoder = base_encoder if lock['feature']['id'] == config['feature_configs'][0]['id'] else _encoder(config, lock['feature'])
    params = Parameters(**lock['params'])
    rows, episodes_metrics, masks = [], [], {}
    for e in episodes:
        print('verification', e['id'], flush=True)
        root, lookup = inventories[e['dataset']]
        selected_model = TunableSubspaceSearch.load(output/'models'/e['id']/'model')
        base_model = TunableSubspaceSearch([base_encoder.extract(root/i).tokens for i in e['support_ids']],
                                          e['support_ids'], variances=(.99,))
        base_normals = [base_model.score_raw(base_encoder.extract(root/i).tokens) for i in e['calibration_ids']]
        base_params = Parameters()
        base_cal = base_model.calibration_from_raw(base_normals, e['calibration_ids'], base_params)
        method_maps = {name: [] for name in ['original', 'fixed_avg', 'selected']}
        truths, scores = [], {name: [] for name in method_maps}
        labels = []
        episode_path = destination/e['id']
        episode_path.mkdir(parents=True, exist_ok=True)
        for index, identifier in enumerate(e['query_ids']):
            bundle = base_encoder.extract(root/identifier)
            raw = base_model.score_raw(bundle.tokens)
            original = base_model.predict_from_raw(raw, base_params, base_cal)
            fixed = base_model.predict_from_raw(raw, Parameters(fusion='fixed'), base_cal)
            tuned_bundle = bundle if selected_encoder is base_encoder else selected_encoder.extract(root/identifier)
            tuned_raw = selected_model.score_raw(tuned_bundle.tokens)
            selected = selected_model.predict_from_raw(tuned_raw, params, selected_model.calibration)
            predictions = {'original': (original, bundle, 1.), 'fixed_avg': (fixed, bundle, 1.),
                           'selected': (selected, tuned_bundle, params.image_threshold)}
            # All feature-only predictions are complete before reading the offline mask.
            sample = lookup[identifier]
            truth = _mask(root, sample)
            if sample.mask:
                masks[str(root/sample.mask)] = sha256(root/sample.mask)
            label = int(sample.label != 'normal')
            if bool(truth.any()) != bool(label):
                raise ValueError('Metric mask lost the defect or native label is inconsistent.')
            labels.append(label)
            truths.append(truth)
            arrays = {'truth': truth.astype(np.uint8)}
            for name, (prediction, geometry, threshold) in predictions.items():
                score_map = _metric_map(prediction['map'], geometry)
                method_maps[name].append(score_map)
                scores[name].append(prediction['image_score'])
                arrays[name] = score_map.astype(np.float32)
                rows.append(dict(dataset=e['dataset'], category=e['category'], seed=e['seed'],
                                 episode_id=e['id'], query_id=identifier, label=label, method=name,
                                 score=prediction['image_score'], threshold=threshold,
                                 decision=bool(prediction['image_score'] >= threshold),
                                 image_correct=bool((prediction['image_score'] >= threshold) == label),
                                 A=prediction['A'], U=prediction['U'],
                                 search_weight=float(prediction['weights']['search'].mean()),
                                 parameters_id=prediction['parameters_id'],
                                 shots=4, k_plus_calibration=8, probabilities=None,
                                 feature_key=geometry.key, map_file=str(episode_path/f'query-{index:03d}.npz'),
                                 metric_geometry=[256, 256], pixel_threshold=1., map_dtype='float32',
                                 selection_lock_sha256=sha256(output/'selection.lock.json')))
            np.savez_compressed(episode_path/f'query-{index:03d}.npz', **arrays)
            _save_raw(episode_path/f'raw-selected-{index:03d}.npz', tuned_raw, tuned_bundle)
            if index == 0:
                np.savez_compressed(episode_path/'replay_probe.npz', tokens=tuned_bundle.tokens.numpy(),
                                    grid=np.array(tuned_bundle.grid),
                                    expected_score=np.array(selected['image_score']),
                                    expected_map=selected['map'].numpy(), query_id=np.array(identifier))
        for name in method_maps:
            threshold = params.image_threshold if name == 'selected' else 1.
            episodes_metrics.append(dict(dataset=e['dataset'], category=e['category'], seed=e['seed'],
                                         episode_id=e['id'], method=name,
                                         detection=thresholded_detection_metrics(labels, scores[name], threshold),
                                         localization=localization_metrics(truths, method_maps[name], 1., max_thresholds=128)))
    write_jsonl(destination/'predictions.jsonl', rows)
    write_json(destination/'episode_metrics.json', episodes_metrics)
    complete = dict(selection_lock_sha256=sha256(output/'selection.lock.json'), unique_queries=100,
                    paired_cases=300, method_rows=900, masks_used_for_selection=False,
                    mask_input_sha256=masks,
                    artifact_sha256={str(p): sha256(p) for p in sorted(destination.rglob('*')) if p.is_file()},
                    verification_label_role='offline metrics only; no retuning permitted',
                    implementation_sha256=implementation_hashes(CODE))
    write_json(destination/'completion.json', complete)
    return complete


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=['tune', 'verify'])
    parser.add_argument('--config', required=True)
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    (tune if args.stage == 'tune' else verify)(args.config, args.output)


if __name__ == '__main__':
    main()
