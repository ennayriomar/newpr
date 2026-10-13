"""Audit a completed SAFAL research release, including serialized inference.

This audit distinguishes resized float32 metric maps from native localization,
and source-proxy error estimates from verified native-domain calibration.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import tempfile

import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F

from safe_iad.experiment_io import read_jsonl, verify_stage, write_json
from safe_iad.research_metrics import paired_crossed_bootstrap
from safe_iad.safal_calibration import ERROR_FEATURE_NAMES, ErrorCalibrator, _source_rows
from safe_iad.safal_cli import CODE_FILES, METHODS
from safe_iad.safal_features import CHECKPOINT_SHA256, SOURCE_PIN, SOURCE_FILES_SHA256, SAFALEncoder
from safe_iad.safal_model import SAFALModel
from safe_iad.verify_dataset import discover


def require(condition, description):
    if not condition:
        raise ValueError(description)


def near(actual, expected, description, tolerance=1e-11):
    require(np.isfinite(actual) and np.isfinite(expected)
            and abs(float(actual)-float(expected)) <= tolerance*max(1., abs(float(expected))), description)


def validate_manifest(manifest, used):
    """Pure split/budget/lineage checks, also usable with synthetic fixtures."""
    require(manifest['schema_version'] == 1 and manifest['scope'] == 'safal_full_model_validation', 'Unsupported release manifest.')
    table = {(row['dataset'], row['image']): row for row in used}
    require(len(table) == len(used), 'Duplicate used-input image IDs.')
    source_groups = {'meta_training': set(), 'source_calibration': set()}
    evaluation_ids = set()
    reserved = defaultdict(set)
    memberships = defaultdict(set)
    def origin(dataset, category, identifier, normal=False):
        require((dataset, identifier) in table, 'Fitting/evaluation image missing from used_inputs: '+identifier)
        row = table[dataset, identifier]
        require(row['category'] == category, 'Image belongs to another category.')
        if normal:
            require(row['split'] == 'train' and row['label'] == 'normal' and row['mask'] is None, 'Only native-train normals may fit supports/cutoffs/proxy parents.')
        return row
    for episode in manifest['source_episodes']:
        dataset, category = episode['dataset'], episode['category']
        require(category in manifest['category_roles'][dataset]['meta_training'], 'Source calibration uses reserved target categories.')
        groups = [episode[key] for key in ['support_ids', 'calibration_ids', 'fit_parent_ids', 'heldout_parent_ids']]
        for identifiers, role in zip(groups, ['support', 'normal_calibration', 'source_proxy_fit_parent', 'source_proxy_cal_parent']):
            for identifier in identifiers:
                memberships[dataset, identifier].add(role)
        require(all(group and len(group) == len(set(group)) for group in groups), 'Empty/duplicate source partitions.')
        require(all(not set(groups[a]) & set(groups[b]) for a in range(4) for b in range(a+1, 4)), 'Source parent/support/calibration leakage.')
        for identifier in sum(groups, []):
            origin(dataset, category, identifier, normal=True)
        for role, key in [('meta_training', 'fit_parent_ids'), ('source_calibration', 'heldout_parent_ids')]:
            source_groups[role].update((dataset, category, identifier) for identifier in episode[key])
    require(not source_groups['meta_training'] & source_groups['source_calibration'], 'Fit/heldout original parent overlap.')
    ids = set()
    for episode in manifest['episodes']:
        dataset, category = episode['dataset'], episode['category']
        require(episode['id'] not in ids, 'Duplicate model configuration ID.')
        ids.add(episode['id'])
        require(category in manifest['category_roles'][dataset]['validation'] and episode['role'] == 'validation', 'Final/native target categories used for model selection.')
        groups = [episode[key] for key in ['support_ids', 'calibration_ids', 'query_ids']]
        for identifiers, role in zip(groups, ['support', 'normal_calibration', 'native_evaluation']):
            for identifier in identifiers:
                memberships[dataset, identifier].add(role)
        require(all(group and len(group) == len(set(group)) for group in groups), 'Duplicate/empty target partitions.')
        require(all(not set(groups[a]) & set(groups[b]) for a in range(3) for b in range(a+1, 3)), 'Support/calibration/evaluation overlap.')
        require(len(groups[0]) == episode['shots'] and episode['k_plus_calibration'] == len(groups[0])+len(groups[1])
                and episode['strict_k_image_few_shot'] is False and episode['support_views'] == ['identity'], 'Original-normal k+calibration information budget incorrect.')
        for identifier in groups[0]+groups[1]:
            origin(dataset, category, identifier, normal=True)
        for identifier in groups[2]:
            row = origin(dataset, category, identifier)
            require(row['split'] in {'test', 'test_public'}, 'Evaluation query not from a declared native public test split.')
            evaluation_ids.add((dataset, identifier))
        reserved[dataset, category].update(groups[1])
    for episode in manifest['episodes']:
        require(not set(episode['support_ids']) & reserved[episode['dataset'], episode['category']], 'Reserved target calibration query appears in another support draw.')
    source_ids = {(dataset, identifier) for groups in source_groups.values() for dataset, _, identifier in groups}
    require(not source_ids & evaluation_ids, 'Native evaluation entered source proxy fitting.')
    require(set(memberships) == set(table) and all(set(table[key]['roles']) == roles for key, roles in memberships.items()), 'Used-input role memberships differ from fitting/evaluation manifest.')
    return source_groups, evaluation_ids


def metric_map(tokens, grid):
    return F.interpolate(tokens.detach().float().reshape(1, 1, *grid), (256, 256), mode='bilinear', align_corners=False)[0, 0].numpy()


def check_map_fields(fields):
    expected = set(METHODS) | {'adequacy', 'uncertainty', 'raw_search', 'raw_subspace', 'search_weight', 'branch_disagreement'}
    require(set(fields) == expected, 'Incomplete/unexpected SAFAL metric-map fields.')
    require(all(value.shape == (256, 256) and value.dtype == np.float32 and np.isfinite(value).all()
                and (value >= 0).all() for value in fields.values()), 'Metric map dtype/shape/nonfinite/negative values.')
    for name in ['adequacy', 'uncertainty', 'branch_disagreement']:
        require((fields[name] <= 1).all(), 'Bounded diagnostic outside [0,1]: '+name)
    require(((fields['search_weight'] >= .1-1e-7) & (fields['search_weight'] <= .9+1e-7)).all(), 'Branch weights outside declared bounds.')
    require(np.allclose(fields['fixed_avg'], .5*(fields['search']+fields['subspace']), rtol=2e-6, atol=2e-6), 'Fixed average export inconsistent.')
    tolerance = 2e-6*np.maximum(1., fields['max'])
    require(((fields['max']+tolerance >= fields['search']) & (fields['max']+tolerance >= fields['subspace'])).all(), 'Maximum comparator loses branch evidence.')
    require(np.allclose(fields['search_weight'], .9-.8*fields['adequacy'], atol=2e-6, rtol=2e-6), 'Coverage/weight maps inconsistent.')
    require(np.allclose(fields['uncertainty'], .5*(fields['branch_disagreement']+1-fields['adequacy']), atol=2e-6, rtol=2e-6), 'Uncertainty map inconsistent.')


def validate(run, fresh_features=0):
    run = Path(run).absolute()
    require((run/'completion.json').is_file(), 'Finish the real pilot before auditing its release.')
    config = json.loads((run/'config.json').read_text())
    manifest = json.loads((run/'manifest.json').read_text())
    used = json.loads((run/'used_inputs.json').read_text())
    source_groups, evaluation_ids = validate_manifest(manifest, used)
    torch.set_num_threads(config['encoder'].get('threads', 3))
    torch.use_deterministic_algorithms(True)
    counts = Counter()
    output_files, input_hashes = set(), {}
    def stage(directory):
        require(verify_stage(directory, require_inputs=True, implementation_files=CODE_FILES), 'Missing completed SAFAL stage.')
        ledger = json.loads((directory/'completion.json').read_text())
        counts['stage_ledgers_checked'] += 1
        counts['output_hash_checks'] += len(ledger['files'])
        counts['input_hash_checks'] += len(ledger['input_sha256'])
        output_files.update((directory/name).absolute() for name in ledger['files'])
        for path, digest in ledger['input_sha256'].items():
            require(Path(path).is_absolute() and (path not in input_hashes or input_hashes[path] == digest), 'Inconsistent/nonabsolute input fingerprints.')
            input_hashes[path] = digest
    stage(run)
    require(input_hashes[config['encoder']['checkpoint']] == CHECKPOINT_SHA256, 'Actual pretrained checkpoint is not the verified DINOv2 checkpoint.')
    native_lookup = {}
    for dataset, root in config['roots'].items():
        samples, _, issues, _ = discover(Path(root), dataset, None)
        require(not issues, 'Native dataset inventory has unresolved issues.')
        native_lookup[dataset] = {sample.image: sample for sample in samples}
    for row in used:
        actual = native_lookup[row['dataset']][row['image']]
        require(all(row[key] == getattr(actual, key) for key in ['category', 'split', 'label', 'mask']), 'Used-input metadata differs from native split inventory.')
        require(input_hashes[row['path']] == row['image_sha256'], 'Original image fingerprint missing/different.')
        if row['mask']:
            require(input_hashes[row['mask_path']] == row['mask_sha256'], 'Offline native mask fingerprint missing/different.')

    proxy_rows = read_jsonl(run/'source_calibration.jsonl')
    fit = [row for row in proxy_rows if row['experiment_role'] == 'meta_training']
    held = [row for row in proxy_rows if row['experiment_role'] == 'source_calibration']
    require(len(fit)+len(held) == len(proxy_rows), 'Unexpected proxy calibration roles.')
    x, y, fit_groups, domain = _source_rows(fit, config['category_roles'], 'meta_training', ERROR_FEATURE_NAMES)
    _, held_y, held_groups, held_domain = _source_rows(held, config['category_roles'], 'source_calibration', ERROR_FEATURE_NAMES)
    require(domain == held_domain == 'source_normal_plus_cutpaste', 'Proxy fitting domain/event mixture changed.')
    require(set(fit_groups) == source_groups['meta_training'] and set(held_groups) == source_groups['source_calibration'], 'Proxy parent groups differ from source manifest.')
    calibrator = ErrorCalibrator.load(run/'error_calibrator.json')
    require(set(calibrator.fit_group_ids) == set(fit_groups) and set(calibrator.calibration_group_ids) == set(held_groups), 'Saved error calibrator group leakage.')
    require(np.array_equal(calibrator.feature_mean, x.mean(axis=0)), 'Calibration scaler mean used non-fitting data.')
    scale = x.std(axis=0); scale[scale < 1e-12] = 1.
    require(np.array_equal(calibrator.feature_scale, scale), 'Calibration scaler scale used non-fitting data.')
    report = json.loads((run/'calibration_report.json').read_text())
    require(report['group_overlap'] == 0 and report['heldout_used_for_fitting'] is False
            and report['domain_transfer_verified'] is False and report['probability_calibration_claim'] is False, 'Calibration scope/heldout/transfer claim invalid.')
    sibling_kinds = defaultdict(set)
    for row in proxy_rows:
        require(row['native_query_source_split'] == 'train' and row['native_final_labels_used'] is False, 'Native test labels entered source calibration.')
        key = (row['dataset'], row['query_source_id'])
        sibling_kinds[key].add(row['query_kind'])
        if row['query_kind'] == 'normal':
            path = Path(config['roots'][row['dataset']])/row['query_source_id']
        else:
            require(row['query_kind'] == 'cutpaste' and row['synthetic_provenance']['source_image_id'] == row['query_source_id'], 'Synthetic proxy parent ancestry invalid.')
            path = run/'generated_source_queries'/row['query_id']
        require(input_hashes[str(path)] == row['image_sha256'], 'Source proxy query lacks a bound input fingerprint.')
    require(all(kinds == {'normal', 'cutpaste'} for kinds in sibling_kinds.values()), 'Normal/synthetic proxy siblings missing.')

    def encoder_contract(metadata):
        require(metadata['backbone'] == 'dinov2_vitb14' and metadata['checkpoint_sha256'] == CHECKPOINT_SHA256
                and metadata['source_commit'] == SOURCE_PIN and metadata['source_manifest_sha256'] == SOURCE_FILES_SHA256,
                'Encoder does not identify actual pinned DINOv2 weights/source.')
        require(metadata['pretrained_weights_loaded'] is True and metadata['frozen'] is True and metadata['evaluation_mode'] is True
                and metadata['device'] == 'cpu' and metadata['dtype'] == 'float32', 'Actual pretrained/frozen/eval encoder contract invalid.')
        require(metadata['resolution'] == config['encoder']['resolution'] and metadata['layers'] == config['encoder']['layers'], 'Encoder preprocessing/layer configuration mismatch.')
        for name, digest in metadata['source_files_sha256'].items():
            require(input_hashes[str(Path(config['encoder']['source_dir'])/name)] == digest, 'Pinned encoder source file lacks an input fingerprint.')

    def load_bound_model(folder, episode):
        metadata = json.loads((folder/'encoder.json').read_text())
        encoder_contract(metadata)
        document = json.loads((folder/'model.json').read_text())
        require(document['provenance']['encoder'] == metadata and document['provenance']['fitting_split'] == 'native train normal only', 'Standalone model is not bound to its actual encoder/fitting split.')
        expected_support = [episode['dataset']+':'+identifier for identifier in episode['support_ids']]
        expected_cal = [episode['dataset']+':'+identifier for identifier in episode['calibration_ids']]
        require(document['support_ids'] == expected_support and document['calibration']['calibration_ids'] == expected_cal, 'Serialized model support/cutoff IDs differ from manifest.')
        with np.load(folder/'model.npz', allow_pickle=False) as arrays:
            require(arrays.files == document['support_array_keys'] and len(arrays.files) == len(expected_support), 'Serialized support-array budget/schema mismatch.')
            for value in (arrays[key] for key in arrays.files):
                require(value.dtype == np.float64 and value.shape == ((metadata['resolution']//14)**2, 768)
                        and np.isfinite(value).all(), 'Serialized raw support feature dimensions/values invalid.')
        model = SAFALModel.load(folder/'model')
        require(model.calibration_metadata['calibration_ids'] == expected_cal
                and model.calibration_metadata['support_calibration_overlap'] == 0
                and model.calibration_metadata['query_labels_accepted'] is False
                and model.calibration_metadata['probability_calibration'] is False, 'Normal-cutoff calibration state mismatched or overclaimed.')
        counts['serialized_models_checked'] += 1
        return model

    for episode in manifest['source_episodes']:
        load_bound_model(run/'source_models'/(episode['dataset']+'-'+episode['category']), episode)
    aggregate, all_maps, fresh_candidates = [], set(), []
    seed_pairs = defaultdict(list)
    for episode in manifest['episodes']:
        folder = run/'episodes'/episode['id']
        stage(folder)
        require(json.loads((folder/'episode.json').read_text()) == episode, 'Saved episode differs from authoritative manifest.')
        model = load_bound_model(folder, episode)
        rows = read_jsonl(folder/'predictions.jsonl')
        aggregate.extend(rows)
        by_query = defaultdict(list)
        for row in rows:
            by_query[row['query_id']].append(row)
        require(set(by_query) == set(episode['query_ids']), 'Model configuration does not contain the declared query set.')
        for query_index, identifier in enumerate(episode['query_ids']):
            case = by_query[identifier]
            require(len(case) == 5 and {row['method'] for row in case} == set(METHODS), 'Missing/duplicate paired method records.')
            lookup = {row['method']: row for row in case}
            main = lookup['safal']
            for row in case:
                require((row['dataset'], row['category'], row['seed'], row['shots']) == (episode['dataset'], episode['category'], episode['seed'], episode['shots'])
                        and row['role'] == 'validation' and row['query_id'] == identifier, 'Paired episode identity differs.')
                require(row['k_plus_calibration'] == episode['k_plus_calibration'] and row['strict_k_image_few_shot'] is False, 'Prediction information budget incorrectly labelled strict k-shot.')
                require(row['map_shape'] == row['metric_grid'] == [256, 256] and row['map_space'] == 'resized_metric'
                        and row['map_dtype'] == 'float32' and row['label_access'] == 'offline after feature-only prediction', 'Metric geometry/label-use declaration invalid.')
                require(row['predicted_anomaly'] == (row['image_score'] >= 1.) and np.isfinite(row['image_score']) and row['image_score'] >= 0, 'Image decision is not at the locked threshold.')
                require(row['label'] == int(native_lookup[episode['dataset']][identifier].label == 'anomaly'), 'Offline image label differs from native inventory.')
                for name in ['A', 'U', 'branch_disagreement']:
                    require(np.isfinite(row[name]) and 0 <= row[name] <= 1 and row[name] == main[name], 'Paired bounded diagnostic differs/invalid: '+name)
                require(.1-1e-12 <= row['search_weight'] <= .9+1e-12, 'Unbounded branch weighting.')
                valid = episode['shots'] > 1
                require(row['image_leave_one_out_valid'] == valid, 'Image LOO validity disagrees with k.')
                for branch in ['search', 'subspace']:
                    value = row['image_leave_one_out_mean'][branch]
                    require((value is None) if not valid else (np.isfinite(value) and value >= 0), 'Undefined k=1 LOO encoded as stability.')
                require((row['image_leave_one_out_missing_reason'] is not None) if not valid else row['image_leave_one_out_missing_reason'] is None, 'LOO missingness reason invalid.')
            near(main['U'], .5*(main['branch_disagreement']+1-main['A']), 'Uncertainty scalar formula differs.')
            near(main['search_weight'], .9-.8*main['A'], 'Coverage weighting scalar formula differs.')
            near(lookup['fixed_avg']['image_score'], .5*(lookup['search']['image_score']+lookup['subspace']['image_score']), 'Fixed branch image combination differs.')
            near(lookup['max']['image_score'], max(lookup['search']['image_score'], lookup['subspace']['image_score']), 'Maximum branch image combination differs.')
            probability = float(calibrator.predict([[abs(main['image_score']-1.), main['A'], main['branch_disagreement'], main['U']]], domain='native_industrial_validation')[0])
            near(main['error_probability'], probability, 'Serialized source-proxy error probability differs.')
            require('unverified' in main['error_domain'] and calibrator.prediction_metadata('native_industrial_validation')['calibration_transfer_verified'] is False, 'Native error calibration transfer is incorrectly asserted.')
            expected_action = 'abstain' if probability > config['abstain_error_probability'] else ('anomaly' if main['predicted_anomaly'] else 'normal')
            require(main['action'] == expected_action, 'Source-proxy abstention action differs from declared cutoff.')
            require(all(row['error_probability'] is None for row in case if row['method'] != 'safal'), 'Error probability belongs to another method/event.')
            require(len({row['map_file'] for row in case}) == len({row['feature_key'] for row in case}) == 1, 'Methods use unequal query features/maps.')
            path = folder/main['map_file']
            with np.load(path, allow_pickle=False) as archive:
                fields = {name: archive[name] for name in archive.files}
            check_map_fields(fields)
            for branch in ['search', 'subspace']:
                cutoff = getattr(model.calibration, 'pixel_'+branch)
                require(np.allclose(fields['raw_'+branch], fields[branch]*cutoff, rtol=5e-6, atol=2e-6*max(1., cutoff)), 'Raw/normalized branch evidence inconsistent.')
            all_maps.add(path)
            counts['query_support_cases'] += 1
            key = (episode['dataset'], episode['category'], identifier, episode['seed'])
            seed_pairs[key].append(int(main['predicted_anomaly'] == main['label'])-int(lookup['fixed_avg']['predicted_anomaly'] == lookup['fixed_avg']['label']))
        with np.load(folder/'probe.npz', allow_pickle=False) as archive:
            require(set(archive.files) == {'query_tokens', 'grid', 'original_size'}, 'Feature-only replay probe schema invalid.')
            tokens = archive['query_tokens'].copy(); grid = tuple(archive['grid'].tolist()); original = archive['original_size'].tolist()
        require(tokens.dtype == np.float32 and tokens.shape == ((config['encoder']['resolution']//14)**2, 768)
                and np.isfinite(tokens).all() and grid == (config['encoder']['resolution']//14,)*2, 'Real feature probe shape/dtype invalid.')
        replay = model.predict(torch.from_numpy(tokens))
        first = {row['method']: row for row in by_query[episode['query_ids'][0]]}
        for method in METHODS:
            near(first[method]['image_score'], replay['image_scores'][method], 'Serialized model image inference does not reproduce: '+method, 1e-10)
            near(first[method]['A'], replay['A'], 'Serialized adequacy does not reproduce.')
            near(first[method]['U'], replay['U'], 'Serialized uncertainty does not reproduce.')
            require(first[method]['original_size'] == original, 'Probe original size differs from prediction.')
        expected_fields = {method: metric_map(replay['maps'][method], grid) for method in METHODS}
        expected_fields.update(adequacy=metric_map(replay['patch_adequacy'], grid), uncertainty=metric_map(replay['patch_uncertainty'], grid),
                               raw_search=metric_map(replay['raw']['search'], grid), raw_subspace=metric_map(replay['raw']['subspace'], grid),
                               search_weight=metric_map(replay['weights']['search'], grid), branch_disagreement=metric_map(replay['patch_branch_disagreement'], grid))
        with np.load(folder/first['safal']['map_file'], allow_pickle=False) as saved:
            require(all(np.array_equal(saved[name], value) for name, value in expected_fields.items()), 'Serialized full-precision metric-map inference does not reproduce.')
        require(bool(replay['loo']['valid'].all()) == (episode['shots'] > 1), 'Serialized LOO validity differs.')
        counts['serialized_query_replays'] += 1
        fresh_candidates.append((episode, tokens, original))
    require(read_jsonl(run/'predictions.jsonl') == aggregate, 'Global prediction rows differ from paired episode records.')
    require(set(run.glob('episodes/*/query-*.npz')) == all_maps, 'Unread/unreferenced exported query maps.')
    summary = json.loads((run/'summary.json').read_text())
    require(summary['prediction_records'] == len(aggregate) and summary['unique_native_queries'] == len(evaluation_ids)
            and summary['episodes'] == len(manifest['episodes']) and summary['support_draws'] == len(config['seeds']), 'Summary confuses repeated records with unique queries/support draws.')
    require(summary['full_benchmark_completed'] is False and summary['strict_k_image_few_shot'] is False
            and summary['published_recipes_reproduced'] is False, 'Unverified research scope labelled complete/faithful/strict.')
    pairs = [dict(dataset=key[0], category=key[1], query_id=key[2], seed=key[3], paired_difference=float(np.mean(values))) for key, values in sorted(seed_pairs.items())]
    require(all(len(values) == len(config['shots']) for values in seed_pairs.values()), 'Nested-shot accuracy pairing incomplete.')
    require(paired_crossed_bootstrap(pairs, n_bootstrap=1000, seed=917) == summary['paired_safal_minus_fixed_accuracy'], 'Accuracy interval incorrectly treats nested shots as independent support draws.')
    fresh_reports = []
    if fresh_features:
        require(fresh_features == 2 and len(config['roots']) == 2, 'This supplementary probe supports exactly one query in each of two datasets.')
        selected = {}
        for episode, tokens, original in fresh_candidates:
            selected.setdefault(episode['dataset'], (episode, tokens, original))
        with tempfile.TemporaryDirectory(prefix='safal-release-fresh-') as temporary:
            parameters = dict(config['encoder'], cache_root=temporary)
            encoder = SAFALEncoder(**parameters)
            for dataset, (episode, tokens, original) in selected.items():
                identifier = episode['query_ids'][0]
                result = encoder.extract(Path(config['roots'][dataset])/identifier, use_cache=False)
                require(np.array_equal(result.tokens.numpy(), tokens) and list(result.original_size) == original, 'Actual checkpoint-backed fresh features differ from serialized query probe.')
                fresh_reports.append(dict(dataset=dataset, query_id=identifier, checkpoint_sha256=encoder.metadata()['checkpoint_sha256'],
                                          source_commit=encoder.metadata()['source_commit'], cached_features_used=False, float32_features_bitwise_equal=True))
    return dict(status='passed', run=str(run), **dict(counts), prediction_records=len(aggregate),
                unique_native_queries=len(evaluation_ids), original_input_images=len(used),
                unique_output_files_hash_verified=len(output_files), unique_input_files_hash_verified=len(input_hashes),
                source_proxy_fit_rows=len(fit), source_proxy_fit_parent_groups=len(fit_groups),
                source_proxy_heldout_rows=len(held), source_proxy_heldout_parent_groups=len(held_groups),
                original_support_and_calibration_budgets_verified=True, source_parent_and_evaluation_isolation_verified=True,
                resized_metric_maps_shape=[256, 256], native_resolution_localization_replayed=False,
                source_proxy_error_probability_transfer_verified=False, nested_shots_counted_as_independent_draws=False,
                real_feature_probes=fresh_reports,
                limitations=['A/U and weighting are empirical diagnostics, not identified support adequacy or reliability guarantees.',
                             'Weighted SAFAL may suppress branch alerts; raw branches and maximum comparator remain exposed.',
                             'Error probabilities are source-normal/CutPaste estimates; native transfer remains unverified.',
                             'Replayed one query per serialized target model; the metric maps are resized256x256, not native resolution.',
                             'A completed audit does not establish greater accuracy, full-benchmark reproduction or novelty.'])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, default=Path('/tmp/safal_full_model_v050_final'))
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--fresh-features', type=int, choices=[0, 2], default=0)
    parser.add_argument('--fresh-features2', dest='fresh_features', action='store_const', const=2)
    args = parser.parse_args()
    result = validate(args.run, args.fresh_features)
    write_json(args.output, result)
    print(json.dumps(result, allow_nan=False))


if __name__ == '__main__':
    main()
