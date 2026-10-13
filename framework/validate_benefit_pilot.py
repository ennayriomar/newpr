"""Audit a completed real benefit pilot without fitting models or using labels to tune.

Checks stored float16 exports against the saved float32 patch diagnostics. This
does not independently re-extract DINO features or reproduce float32 metrics.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path

import numpy as np
from PIL import Image
import torch

from safe_iad.benefit_model import BenefitModel, _source_rows
from safe_iad.counterfactual import FEATURE_NAMES
from safe_iad.experiment_io import image_score, read_jsonl, verify_stage, write_json
from safe_iad.patch_nn import restore_map
from safe_iad.splits import validate_category_roles, validate_partition
from safe_iad.support_decision import DEFAULT_SIGMOID, action, adequacy_field
from safe_iad.verify_dataset import discover


POLICIES = {'none', 'random', 'nearest_global', 'diversity', 'learned', 'oracle'}
PROTOCOLS = {'paired_validation', 'missing_support', 'coverage_control'}


def require(condition, description):
    if not condition:
        raise ValueError(description)


def close(actual, expected, description, tolerance=1e-7):
    require(np.isfinite(actual) and np.isfinite(expected)
            and abs(float(actual)-float(expected)) <= tolerance, description)


def case_key(row):
    return (row['protocol'], row['dataset'], row['category'], row['seed'], row['shots'], row['image_id'])


def validate(run):
    run = Path(run).absolute()
    evaluation = run/'evaluation'
    require((evaluation/'completion.json').is_file(), 'Complete evaluation/completion.json before auditing this pilot.')
    config = json.loads((evaluation/'config.json').read_text())
    ledger_checks = Counter()
    output_paths, input_paths, checked_ledgers = set(), set(), set()

    def stage(directory):
        directory = Path(directory).absolute()
        if directory in checked_ledgers:
            return
        require(verify_stage(directory, require_inputs=True), 'Missing stage completion: '+str(directory))
        ledger = json.loads((directory/'completion.json').read_text())
        checked_ledgers.add(directory)
        ledger_checks['output_hash_checks'] += len(ledger['files'])
        ledger_checks['input_hash_checks'] += len(ledger['input_sha256'])
        ledger_checks['implementation_hash_checks'] += len(ledger['implementation_sha256'])
        output_paths.update((directory/name).absolute() for name in ledger['files'])
        input_paths.update(Path(name).absolute() for name in ledger['input_sha256'])

    for name in ['targets', 'models', 'evaluation']:
        stage(run/name)
    require(json.loads((run/'targets/config.json').read_text()) == config, 'Target/evaluation configurations differ.')
    source = read_jsonl(run/'targets/training.jsonl')
    source_rows, _, _, source_groups, names, source_contract = _source_rows(source, config['category_roles'])
    require(names == FEATURE_NAMES, 'Unexpected deployed benefit feature schema.')
    training_report = json.loads((run/'models/training_report.json').read_text())
    require(training_report['model_selection_role'] == 'source_training_grouped_cv_only', 'Primary model was not source-CV-selected.')
    for key in ['final_test_labels_used', 'validation_labels_used_for_model_selection', 'calibration_labels_used',
                'validation_data_used_for_primary_selection']:
        require(training_report.get(key) is False, 'Unsafe/undeclared model-selection flag: '+key)
    scores = training_report['grouped_cv']['source_group_balanced_mse']
    primary = min(scores, key=lambda name: (scores[name], name != 'ridge'))
    require(primary == training_report['primary_model'], 'Primary model does not match source-CV selection.')
    seen_groups = set()
    actual_groups = set(source_groups)
    for fold in training_report['grouped_cv']['folds']:
        train, held = set(fold['train_source_groups']), set(fold['held_out_source_groups'])
        require(not train & held and train | held == actual_groups, 'Source derivatives/support draws leak across CV partitions.')
        require(not seen_groups & held, 'Source image appears in multiple held-out folds.')
        seen_groups.update(held)
    require(seen_groups == actual_groups, 'CV did not hold out every source image exactly once.')
    require(training_report['grouped_cv']['oof_source_groups'] == source_groups.tolist(), 'OOF source grouping does not match training rows.')
    model = BenefitModel.load(run/'models'/(primary+'.json'))
    model.check_contract(names, source_contract)
    provenance = json.loads((evaluation/'provenance.json').read_text())
    actual_contract = {**provenance, 'loss_specification': config['loss']}
    model.check_contract(FEATURE_NAMES, actual_contract)
    require(provenance['private_test_data_or_results'] is False and provenance['final_categories_evaluated'] == []
            and provenance['native_test_labels_used_for_model_or_threshold_selection'] is False,
            'Evaluation provenance claims private/final evaluation or native-label tuning.')

    lookups, sizes = {}, {}
    for dataset, root in config['roots'].items():
        if dataset not in config['category_roles']:
            continue
        samples, categories, issues, _ = discover(Path(root), dataset, None)
        require(not issues, 'Dataset discovery issues: '+dataset)
        validate_category_roles(config['category_roles'][dataset], categories)
        lookups[dataset] = {sample.image: sample for sample in samples}

    def sample(dataset, identifier, *, normal_train=False):
        require(identifier in lookups[dataset], 'Undiscovered image ID: '+identifier)
        result = lookups[dataset][identifier]
        if normal_train:
            require(result.split == 'train' and result.label == 'normal', 'Reference/cutoff source is not normal native-train: '+identifier)
        path = (Path(config['roots'][dataset])/identifier).absolute()
        require(path in input_paths, 'Used native input lacks a verified fingerprint: '+str(path))
        return result

    def original_size(dataset, identifier):
        key = (dataset, identifier)
        if key not in sizes:
            with Image.open(Path(config['roots'][dataset])/identifier) as image:
                sizes[key] = list(image.size)
        return sizes[key]

    for row in source_rows:
        sample(row['dataset'], row['query_source_id'], normal_train=True)
        for identifier in row['support_ids']+row['candidate_pool_ids']:
            sample(row['dataset'], identifier, normal_train=True)
        if row['query_kind'].startswith('synthetic'):
            generated = (Path(config['generated_root'])/row['query_id']).absolute()
            mask = generated.with_name(generated.stem+'_mask.png')
            require(generated in input_paths and mask in input_paths, 'Synthetic training image/mask lacks verified fingerprints.')
    validation_targets = read_jsonl(run/'targets/validation.jsonl')
    for row in validation_targets:
        require(row['experiment_role'] == 'validation_source_normal_or_synthetic'
                and row['category'] in config['category_roles'][row['dataset']]['validation']
                and row['native_query_source_split'] == 'train' and row['final_test_labels_used'] is False,
                'Validation targets have unsafe origin/role flags.')
        model.check_contract(row['feature_names'], row)
        sample(row['dataset'], row['query_source_id'], normal_train=True)

    cutoffs = json.loads((evaluation/'calibration.json').read_text())
    reserved_calibration = defaultdict(set)
    for key, cutoff in cutoffs.items():
        dataset, seed, shots = cutoff['dataset'], cutoff['seed'], cutoff['shots']
        require(key == f'{dataset}:{seed}:{shots}' and cutoff['category'] in config['category_roles'][dataset]['calibration'],
                'Cutoff role/key mismatch.')
        require(cutoff['native_split'] == 'train' and cutoff['experiment_role'] == 'calibration_normal'
                and cutoff['no_test_defect_labels_used'] is True and cutoff['is_probability_calibration'] is False,
                'Cutoff uses unsupported label/probability-calibration provenance.')
        require(np.isfinite([cutoff['image_threshold'], cutoff['pixel_threshold']]).all(), 'Nonfinite locked cutoff.')
        require(len(cutoff['support_ids']) == shots, 'Cutoff support budget differs from k.')
        validate_partition(cutoff['support_ids'], [], cutoff['calibration_query_ids'])
        for identifier in cutoff['support_ids']+cutoff['calibration_query_ids']:
            found = sample(dataset, identifier, normal_train=True)
            require(found.category == cutoff['category'], 'Cutoff input belongs to another category.')
        reserved_calibration[dataset].update(cutoff['calibration_query_ids'])
    for cutoff in cutoffs.values():
        require(not set(cutoff['support_ids']) & reserved_calibration[cutoff['dataset']], 'Calibration support overlaps a reserved query in another draw.')

    diagnostics_seen, maps_seen = set(), set()
    counts = Counter()

    def diagnostics(reference, support_count):
        path = Path(reference['path']).absolute()
        with np.load(path, allow_pickle=False) as file:
            arrays = {key: file[key].copy() for key in file.files}
        diagnostics_seen.add(path)
        require(all(np.isfinite(value).all() for value in arrays.values()), 'Nonfinite saved diagnostics: '+str(path))
        require(arrays['nearest_distance'].shape == (256,) and arrays['loo_valid'].shape == (256,)
                and arrays['loo_valid'].dtype == np.bool_, 'Diagnostic grid/missingness-mask mismatch.')
        if support_count == 1:
            require(reference['loo_defined'] is False and not arrays['loo_valid'].any()
                    and 'loo_sensitivity' not in arrays, 'Undefined k=1 LOO represented as stability.')
        else:
            require(reference['loo_defined'] is True and arrays['loo_valid'].all()
                    and arrays['loo_sensitivity'].shape == (256,), 'Multi-reference LOO missing/invalid.')
        result = {key: torch.from_numpy(value) for key, value in arrays.items()}
        result.setdefault('loo_sensitivity', None)
        return result

    def native_map(path, shape, expected, adequacy=None):
        path = Path(path).absolute()
        with np.load(path, allow_pickle=False) as file:
            fields = {key: file[key] for key in file.files}
            expected_keys = {'defect_map'} | ({'support_adequacy_diagnostic'} if adequacy is not None else set())
            require(set(fields) == expected_keys, 'Unexpected native prediction fields: '+str(path))
            for value in fields.values():
                require(value.shape == shape and value.dtype == np.float16 and np.isfinite(value).all(),
                        'Native shape/dtype/finiteness violation: '+str(path))
            require(np.array_equal(fields['defect_map'], expected.astype(np.float16)),
                    'Defect export differs from raw saved NN evidence: '+str(path))
            if adequacy is not None:
                field = fields['support_adequacy_diagnostic']
                require(((field >= 0) & (field <= 1)).all() and np.array_equal(field, adequacy.astype(np.float16)),
                        'Adequacy export invalid/different: '+str(path))
        maps_seen.add(path)

    aggregate = read_jsonl(evaluation/'predictions.jsonl')
    require(aggregate, 'Empty completed evaluation predictions.')
    grouped = defaultdict(list)
    for row in aggregate:
        grouped[case_key(row)].append(row)
    expected_predictions = []
    episode_paths = sorted(path.parent for path in evaluation.rglob('all_predictions.jsonl'))
    expected_episode_count = len(config['validation_categories'])*len(config['seeds'])*len(config['evaluation_shots'])*len(PROTOCOLS)
    require(len(episode_paths) == expected_episode_count, 'Completed paired/stress episode count differs from configuration.')
    for episode in episode_paths:
        stage(episode)
        manifest = json.loads((episode/'manifest.json').read_text())
        dataset, category, shots = manifest['dataset'], manifest['category'], manifest['shots']
        require(manifest['protocol'] in PROTOCOLS and category in config['category_roles'][dataset]['validation'], 'Unexpected evaluation protocol/category role.')
        require(manifest['native_test_labels_for_model_selection'] is False and manifest['used_to_select_model_or_threshold'] is False,
                'Native evaluation queries used for tuning.')
        initial, pool, query_ids = manifest['initial_support_ids'], manifest['candidate_ids'], manifest['query_ids']
        require(len(initial) == shots and len(pool) == config['candidate_pool_size'] and manifest['acquisition_budget'] == 1,
                'Manifest reference budget mismatch.')
        validate_partition(initial, pool, query_ids)
        for identifier in initial+pool:
            found = sample(dataset, identifier, normal_train=True)
            require(found.category == category, 'Cross-category reference bank.')
        cutoff = cutoffs[f"{dataset}:{manifest['seed']}:{shots}"]
        require(manifest['cutoffs'] == cutoff, 'Episode cutoff differs from locked calibration record.')
        candidate_rows = read_jsonl(episode/'candidate_evaluation.jsonl')
        candidates_by_query = defaultdict(list)
        for candidate in candidate_rows:
            require(candidate['experiment_role'] == 'validation_evaluation_only' and candidate['never_use_for_training'] is True
                    and candidate['used_for_model_selection'] is False and candidate['oracle_is_deployable'] is False,
                    'Offline candidate row lacks oracle/model isolation.')
            candidates_by_query[candidate['query_id']].append(candidate)
        require(set(candidates_by_query) == set(query_ids), 'Candidate-evaluation query set mismatch.')
        episode_rows = read_jsonl(episode/'all_predictions.jsonl')
        expected_predictions.extend(episode_rows)
        for query_index, identifier in enumerate(query_ids):
            found = sample(dataset, identifier, normal_train=manifest['protocol'] != 'paired_validation')
            require(found.category == category and (found.split == 'test' if manifest['protocol'] == 'paired_validation' else True), 'Query native split/role mismatch.')
            if found.mask:
                require((Path(config['roots'][dataset])/found.mask).absolute() in input_paths, 'Native offline mask lacks verified fingerprint.')
            size = original_size(dataset, identifier)
            shape = (size[1], size[0])
            key = (manifest['protocol'], dataset, category, manifest['seed'], shots, identifier)
            rows = grouped[key]
            require(len(rows) == 6 and {row['policy'] for row in rows} == POLICIES, 'Six-policy paired case missing/duplicated.')
            by_policy = {row['policy']: row for row in rows}
            candidate_set = candidates_by_query[identifier]
            require([row['candidate_id'] for row in candidate_set] == pool, 'Candidate order/pool differs across policies.')
            predicted = model.predict([row['features'] for row in candidate_set], feature_names=FEATURE_NAMES, provenance=actual_contract)
            require(np.allclose(predicted, [row['predicted_benefit'] for row in candidate_set], atol=1e-12, rtol=1e-10), 'Saved learned candidate predictions do not match frozen model.')
            observed = np.asarray([row['observed_benefit'] for row in candidate_set])
            require(np.isfinite(observed).all(), 'Nonfinite observed candidate benefit.')
            require(by_policy['learned']['selected_reference_ids'] == [pool[int(predicted.argmax())]], 'Learned selector differs from label-free predicted argmax.')
            require(by_policy['oracle']['selected_reference_ids'] == [pool[int(observed.argmax())]], 'Offline oracle differs from observed-benefit argmax.')
            base = diagnostics(by_policy['none']['reference_diagnostics']['before'], shots)
            before = restore_map(base['nearest_distance'], (16, 16), size)
            native_map(episode/f'query-{query_index:03d}_before.npz', shape, before)
            for row in rows:
                policy = row['policy']
                require(row['initial_support_ids'] == initial and row['candidate_pool_ids'] == pool
                        and row['candidate_pool_size'] == len(pool) and row['original_size'] == size,
                        'Paired support/pool/query/preprocessing fields differ.')
                selected = row['selected_reference_ids']
                require(len(selected) <= 1 and set(selected).issubset(pool) and row['support_ids'] == initial+selected
                        and row['added_normal_references'] == len(selected), 'Added-reference accounting failed.')
                require(len(selected) == (0 if policy == 'none' else 1), 'Forced one-step acquisition count differs from declared pilot.')
                require(row['query_label_used_for_selection'] == (policy == 'oracle'), 'Query-label access outside offline oracle.')
                require(row['never_use_for_training'] is True and row['experiment_role'] == 'validation_evaluation_only'
                        and row['model_selected_using_these_queries'] is False and row['thresholds_selected_using_these_queries'] is False,
                        'Evaluation predictions violate model/threshold isolation.')
                expected_probes = len(pool) if policy in {'learned', 'oracle'} else len(selected)
                require(row['deployment_candidate_patch_probes'] == expected_probes and row['shared_offline_candidate_probes'] == len(pool), 'Candidate patch-probe accounting failed.')
                require(row['candidate_global_scans'] == (0 if policy in {'none', 'random'} else len(pool)), 'Global pool-scan accounting failed.')
                require(row['decision_threshold_origin'] == cutoff, 'Prediction uses a different locked cutoff.')
                before_diagnostics = diagnostics(row['reference_diagnostics']['before'], shots)
                require(torch.equal(before_diagnostics['nearest_distance'], base['nearest_distance']), 'Policies have different initial defect evidence.')
                post = diagnostics(row['reference_diagnostics']['after'], shots+len(selected))
                close(row['initial_image_score'], image_score(base['nearest_distance']), 'Initial image score differs from raw patch evidence.')
                close(row['image_anomaly_score'], image_score(post['nearest_distance']), 'Image score differs from raw post-acquisition evidence.')
                require(torch.all(post['nearest_distance'] <= base['nearest_distance']+2e-6), 'NN evidence unexpectedly increases after adding reference.')
                adequate = adequacy_field(post, manifest['adequacy'])
                adequate_mean = None if adequate is None else float(adequate.mean())
                if adequate_mean is None:
                    require(row['mean_support_adequacy'] is None, 'Disabled adequacy was represented numerically.')
                else:
                    close(row['mean_support_adequacy'], adequate_mean, 'Mean adequacy differs from saved diagnostics.')
                expected_action, evidence = action(row['image_anomaly_score'], adequate_mean, cutoff['image_threshold'], manifest['adequacy']['adequacy_threshold'])
                require(row['action'] == expected_action and row['raw_defect_evidence'] == evidence, 'Three-way action erased/misreported raw defect evidence.')
                native_map(row['defect_map'], shape, restore_map(post['nearest_distance'], (16, 16), size),
                           None if adequate is None else restore_map(adequate, (16, 16), size))
                require(row['valid_field_masks']['defect_map'] is True and row['valid_field_masks']['action'] is True
                        and row['valid_field_masks']['predicted_patch_benefit'] is False
                        and row['valid_field_masks']['support_adequacy'] == (adequate is not None), 'Prediction validity-field contract mismatch.')
                require(row['native_truth_is_anomalous'] == (found.label == 'anomaly'), 'Native truth event differs from dataset discovery.')
                preserved = row['preservation']
                require(preserved['anomalous_query'] == row['native_truth_is_anomalous'], 'Defect-preservation event mismatch.')
                if preserved['anomalous_query']:
                    missed_before = row['initial_image_score'] < cutoff['image_threshold']
                    missed_after = row['image_anomaly_score'] < cutoff['image_threshold']
                    require(preserved['missed_defect_before'] == missed_before and preserved['missed_defect_after'] == missed_after
                            and preserved['detected_to_missed'] == (not missed_before and missed_after), 'Locked-threshold missed-defect flags differ from raw evidence.')
                benefit = 0. if not selected else float(observed[pool.index(selected[0])])
                close(row['observed_benefit'], benefit, 'Selected observed benefit differs from offline candidate record.', 1e-12)
                require(row['harmful_intervention'] == (benefit < -1e-8) and row['beneficial_intervention'] == (benefit > 1e-8), 'Signed intervention event flags differ.')
                counts['records'] += 1
                counts['reference_additions'] += len(selected)
                counts['oracle_label_access_records'] += int(policy == 'oracle')
                counts['unresolved_records_retaining_positive_raw_evidence'] += int(evidence and row['action'] == 'unresolved/reference-insufficient')
            counts['paired_query_cases'] += 1
            counts['offline_candidate_records'] += len(candidate_set)
        for policy in POLICIES:
            expected_rows = [row for row in episode_rows if row['policy'] == policy]
            require(read_jsonl(episode/policy/'predictions.jsonl') == expected_rows, 'Per-policy prediction file differs from episode aggregate.')
    require(sorted(json.dumps(row, sort_keys=True) for row in expected_predictions)
            == sorted(json.dumps(row, sort_keys=True) for row in aggregate), 'Top-level predictions differ from complete episode records.')
    require(set(path.absolute() for path in evaluation.rglob('*.npz')) == maps_seen | diagnostics_seen, 'Some export maps/diagnostics were unreferenced or unread.')
    protocol_counts = Counter(row['protocol'] for row in aggregate)
    return {'status': 'passed', 'run': str(run), **dict(counts), **dict(ledger_checks),
            'completed_stage_ledgers_checked': len(checked_ledgers), 'unique_output_files_hash_verified': len(output_paths),
            'unique_input_files_hash_verified': len(input_paths), 'native_map_exports_read': len(maps_seen),
            'diagnostic_exports_read': len(diagnostics_seen), 'source_training_rows': len(source),
            'source_original_image_groups': len(actual_groups), 'source_negative_image_groups': training_report['unique_negative_source_groups'],
            'validation_source_target_rows': len(validation_targets), 'unique_query_images': len({(row['dataset'], row['image_id']) for row in aggregate}),
            'unique_queries_by_protocol': {protocol: len({(row['dataset'], row['image_id']) for row in aggregate if row['protocol'] == protocol}) for protocol in sorted(PROTOCOLS)},
            'prediction_records_by_protocol': dict(protocol_counts), 'protocols': sorted(protocol_counts),
            'support_budgets_verified': True, 'six_policy_pairing_verified': True, 'source_only_model_selection_verified': True,
            'normal_only_category_disjoint_cutoffs_verified': True, 'oracle_label_isolation_verified': True,
            'native_fields_float16_finite_verified': True, 'loo_missingness_verified': True,
            'raw_defect_maps_and_evidence_flags_preserved': True, 'no_private_results_or_final_category_evaluation': True,
            'scope': 'Completed artifact/provenance/contract audit; no backbone re-extraction, float32 metric rerun, calibrated-probability or reliability guarantee.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    report = validate(args.run)
    write_json(args.output, report)
    print(json.dumps(report, allow_nan=False))


if __name__ == '__main__':
    main()
