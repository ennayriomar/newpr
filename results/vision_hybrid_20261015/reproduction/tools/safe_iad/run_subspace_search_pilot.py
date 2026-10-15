"""Paired validation of an independently implemented PCA/cosine-search hybrid.

This is an experimental method inspired by SubspaceAD and VisionAD. Neither
published recipe is reproduced. All cutoffs use normal calibration categories;
native validation labels are used only after inference for offline metrics.
"""
from dataclasses import asdict
import argparse
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image
import torch

from .dense_features import DenseDINOv2, restore_dense
from .experiment_io import (
    complete_stage, git_revision, implementation_hashes, input_fingerprints,
    read_jsonl, save_maps, verify_stage, write_json, write_jsonl,
)
from .research_metrics import localization_metrics, paired_crossed_bootstrap, thresholded_detection_metrics
from .splits import validate_category_roles
from .subspace_search import BranchCalibration, SubspaceSearch, fuse
from .verify_dataset import Sample, discover, inspect_sample


METHODS = ('search', 'subspace', 'hybrid')
CODE_FILES = ('run_subspace_search_pilot.py', 'subspace_search.py', 'dense_features.py',
              'patch_nn.py', 'verify_dataset.py', 'splits.py', 'experiment_io.py', 'research_metrics.py')


def validate_config(config, roles):
    if config['schema_version'] != 1 or config['scope'] != 'new_method_validation_pilot':
        raise ValueError('Only the declared validation pilot is implemented.')
    if config['support_views'] != ['identity']:
        raise ValueError('This pilot implements identity views; augmented experiments are separate future work.')
    if config['map_storage_dtype'] != 'float16':
        raise ValueError('This pilot exports explicit float16 maps and computes float32 metrics.')
    if (not config['shots'] or config['shots'] != sorted(set(config['shots']))
            or any(isinstance(k, bool) or not isinstance(k, int) or k < 1 for k in config['shots'])):
        raise ValueError('Shots must be distinct increasing positive integers.')
    if not config['seeds'] or len(config['seeds']) != len(set(config['seeds'])):
        raise ValueError('Distinct explicit support-draw seeds are required.')
    if any(isinstance(s, bool) or not isinstance(s, int) or s < 0 for s in config['seeds']):
        raise ValueError('Support-draw seeds must be nonnegative integers.')
    if config['queries_per_label'] < 2 or config['calibration_queries_per_draw'] < 2:
        raise ValueError('Nontrivial evaluation and normal calibration counts are required.')
    if not np.isfinite(config['calibration_standard_deviations']) or config['calibration_standard_deviations'] < 0:
        raise ValueError('Normal calibration multiplier must be finite and nonnegative.')
    for dataset in config['roots']:
        category = config['validation_categories'][dataset]
        calibration = config['calibration_categories'][dataset]
        if category not in roles[dataset]['validation'] or calibration not in roles[dataset]['calibration']:
            raise ValueError('Validation and normal-calibration categories must use their reserved roles.')


def _salt(dataset):
    return int.from_bytes(hashlib.sha256(dataset.encode()).digest()[:4], 'little')


def build_manifest(config, roles, inventories):
    validate_config(config, roles)
    episodes, query_manifests = [], []
    maximum = max(config['shots'])
    for dataset, samples in inventories.items():
        category = config['validation_categories'][dataset]
        cal_category = config['calibration_categories'][dataset]
        excluded = set(config['excluded_query_ids'].get(dataset, []))
        bank = sorted((s for s in samples if s.category == category and s.split == 'train'
                       and s.label == 'normal' and s.image not in excluded), key=lambda s: s.image)
        cal_bank = sorted((s for s in samples if s.category == cal_category and s.split == 'train'
                           and s.label == 'normal'), key=lambda s: s.image)
        reserved_count = len(config['seeds']) * config['calibration_queries_per_draw']
        if len(bank) < maximum or len(cal_bank) < maximum + reserved_count:
            raise ValueError('Insufficient normal training images for declared disjoint budgets.')
        ordering = np.random.default_rng(config['partition_seed'] + _salt(dataset)).permutation(len(cal_bank))
        reserved = [cal_bank[i] for i in ordering[:reserved_count]]
        cal_references = [cal_bank[i] for i in ordering[reserved_count:]]
        reserved_ids = {s.image for s in reserved}
        queries = []
        rng = np.random.default_rng(config['partition_seed'] + _salt(dataset) + 1)
        for label in ('normal', 'anomaly'):
            choices = sorted((s for s in samples if s.category == category and s.split == 'test'
                              and s.label == label and s.image not in excluded), key=lambda s: s.image)
            if len(choices) < config['queries_per_label']:
                raise ValueError('Not enough unused validation queries for the declared class counts.')
            indices = rng.choice(len(choices), config['queries_per_label'], replace=False)
            queries.extend(choices[i] for i in indices)
        query_manifests.append(dict(dataset=dataset, category=category, query_ids=[s.image for s in queries],
                                    excluded_prior_query_ids=sorted(excluded),
                                    fresh_image_ids=True, previously_inspected_categories=True))
        for index, seed in enumerate(config['seeds']):
            support_indices = np.random.default_rng(seed + _salt(dataset)).choice(len(bank), maximum, replace=False)
            cal_indices = np.random.default_rng(seed + _salt(dataset) + 1).choice(len(cal_references), maximum, replace=False)
            support = [bank[i] for i in support_indices]
            cal_support = [cal_references[i] for i in cal_indices]
            cal_queries = reserved[index * config['calibration_queries_per_draw']:(index + 1) * config['calibration_queries_per_draw']]
            assert not {s.image for s in cal_support} & reserved_ids
            for shots in config['shots']:
                episodes.append(dict(dataset=dataset, category=category, role='validation', seed=seed, shots=shots,
                                     support=[asdict(s) for s in support[:shots]], queries=[asdict(s) for s in queries],
                                     calibration_category=cal_category,
                                     calibration_support=[asdict(s) for s in cal_support[:shots]],
                                     calibration_queries=[asdict(s) for s in cal_queries],
                                     all_reserved_calibration_query_ids=sorted(reserved_ids),
                                     original_normal_support_images=shots, augmented_views_per_support=1,
                                     candidate_pool_size=0, acquisition_budget=0,
                                     thresholds_fit_using_validation_queries=False))
    return dict(scope=config['scope'], episodes=episodes, query_manifests=query_manifests,
                unique_validation_queries=sum(len(row['query_ids']) for row in query_manifests),
                shared_supports_and_queries_across_methods=True,
                calibration_role='normal training queries of separate reserved calibration categories',
                model_selection='No label-trained model, fusion weights, or post-evaluation tuning')


def _positive_cutoff(values, multiplier):
    values = np.asarray(values, dtype=np.float64)
    cutoff = float(values.mean() + multiplier * values.std(ddof=0))
    if not np.isfinite(cutoff) or cutoff <= 0:
        raise ValueError('Degenerate normal calibration has no positive finite cutoff; refusing denominator replacement.')
    return cutoff


def calibrate(episode, extractor, config, output):
    dataset, root = episode['dataset'], Path(config['roots'][episode['dataset']])
    support = [Sample(**row) for row in episode['calibration_support']]
    queries = [Sample(**row) for row in episode['calibration_queries']]
    if any(s.split != 'train' or s.label != 'normal' for s in support + queries):
        raise ValueError('Only original normal training images may fit cutoffs.')
    if {s.image for s in support} & set(episode['all_reserved_calibration_query_ids']):
        raise ValueError('Reserved normal calibration queries overlap calibration support.')
    bundles = [extractor.extract_dense(dataset, s, root, 'subspacead') for s in support]
    model = SubspaceSearch(torch.cat([b.tokens for b in bundles]), explained_variance=config['explained_variance'])
    image_values = {name: [] for name in METHODS[:2]}
    moments = {name: dict(count=0, total=0., squared=0.) for name in METHODS[:2]}
    records = []
    for index, sample in enumerate(queries):
        bundle = extractor.extract_dense(dataset, sample, root, 'subspacead')
        raw = model.predict_raw(bundle.tokens)
        native = {name: restore_dense(raw[name], bundle).astype('float32') for name in METHODS[:2]}
        for name in METHODS[:2]:
            image_values[name].append(raw['image_' + name])
            flat = native[name].astype(np.float64)
            moments[name]['count'] += flat.size
            moments[name]['total'] += float(flat.sum())
            moments[name]['squared'] += float(np.square(flat).sum())
        save_maps(output / f'normal-{index:03}.npz', **native)
        records.append(dict(image_id=sample.image, category=sample.category, split=sample.split, label=sample.label,
                            image_search=raw['image_search'], image_subspace=raw['image_subspace'],
                            feature_key=bundle.key, feature_cache_hit=bundle.cache_hit))
    multiplier = config['calibration_standard_deviations']
    pixel = {}
    for name, m in moments.items():
        mean = m['total'] / m['count']
        variance = max(0., m['squared'] / m['count'] - mean * mean)
        # Lock an exactly representable float32 pixel cutoff, matching the
        # native branch maps used by both comparators and the ratio union.
        pixel[name] = float(np.float32(mean + multiplier * np.sqrt(variance)))
        if not np.isfinite(pixel[name]) or pixel[name] <= 0:
            raise ValueError('Normal pixel cutoff is nonpositive/nonfinite; no silent epsilon is permitted.')
    calibration = BranchCalibration(
        image_search=_positive_cutoff(image_values['search'], multiplier),
        image_subspace=_positive_cutoff(image_values['subspace'], multiplier),
        pixel_search=pixel['search'], pixel_subspace=pixel['subspace'],
        calibration_ids=tuple(f'{dataset}:{s.image}' for s in queries),
    )
    record = dict(dataset=dataset, seed=episode['seed'], shots=episode['shots'],
                  category=episode['calibration_category'], support_ids=[s.image for s in support],
                  queries=records, cutoffs=asdict(calibration), calibration_model=model.metadata(),
                  threshold_method='normal mean + multiplier * population std; pixel stats pooled at native resolution',
                  multiplier=multiplier, target_labels_accessed=False)
    write_json(output / 'calibration.json', record)
    return calibration, record


def evaluate(episode, calibration, extractor, config, output):
    dataset, root = episode['dataset'], Path(config['roots'][episode['dataset']])
    support = [Sample(**row) for row in episode['support']]
    queries = [Sample(**row) for row in episode['queries']]
    if len(support) != episode['shots'] or len({s.image for s in support}) != len(support):
        raise ValueError('Strict original-image support budget violated.')
    if {s.image for s in support} & {s.image for s in queries} or any(s.split != 'train' or s.label != 'normal' for s in support):
        raise ValueError('Normal support/query isolation violated.')
    bundles = [extractor.extract_dense(dataset, s, root, 'subspacead') for s in support]
    start = time.perf_counter()
    model = SubspaceSearch(torch.cat([b.tokens for b in bundles]), explained_variance=config['explained_variance'])
    fit_seconds = time.perf_counter() - start
    write_json(output / 'model.json', model.metadata() | dict(support_ids=[s.image for s in support]))
    score_lists = {name: [] for name in METHODS}
    maps = {name: [] for name in METHODS}
    masks, labels, rows, pixels = [], [], [], 0
    for index, sample in enumerate(queries):
        start = time.perf_counter()
        bundle = extractor.extract_dense(dataset, sample, root, 'subspacead')
        raw = model.predict_raw(bundle.tokens)
        # Restore both raw fields before pixel fusion. Image aggregation remains
        # from patch scores and uses separate normal image cutoffs.
        native = {name: restore_dense(raw[name], bundle).astype('float32') for name in METHODS[:2]}
        native_fields = {name: torch.from_numpy(value.ravel()) for name, value in native.items()}
        native_fields.update(image_search=raw['image_search'], image_subspace=raw['image_subspace'])
        fused = fuse(native_fields, calibration, image_scores=(raw['image_search'], raw['image_subspace']))
        native['hybrid'] = fused['hybrid'].numpy().reshape(native['search'].shape).astype('float32')
        scores = dict(search=raw['image_search'], subspace=raw['image_subspace'], hybrid=fused['image_hybrid'])
        cutoffs = dict(search=calibration.image_search, subspace=calibration.image_subspace, hybrid=1.)
        pixel_cutoffs = dict(search=calibration.pixel_search, subspace=calibration.pixel_subspace, hybrid=1.)
        predicted = {name: scores[name] >= cutoffs[name] for name in METHODS}
        if predicted['hybrid'] != (predicted['search'] or predicted['subspace']):
            raise AssertionError('Image alert union failed.')
        union = (native['search'] >= calibration.pixel_search) | (native['subspace'] >= calibration.pixel_subspace)
        if not np.array_equal(native['hybrid'] >= 1., union):
            raise AssertionError('Native pixel alert union failed.')
        inference_seconds = time.perf_counter() - start
        save_maps(output / f'query-{index:03}.npz', **native)
        # First mask access occurs after all scores, fusion and decisions.
        label = sample.label == 'anomaly'
        if sample.mask:
            with Image.open(root / sample.mask) as mask_image:
                mask = np.array(mask_image.convert('L')) > 0
        else:
            mask = np.zeros(native['search'].shape, dtype=bool)
        if mask.shape != native['search'].shape or bool(mask.any()) != label:
            raise ValueError('Native ground-truth mask/label mismatch.')
        labels.append(label); masks.append(mask); pixels += mask.size
        if pixels > config['max_metric_pixels_per_episode']:
            raise ValueError('Exact native metric pixel budget exceeded; choose adequate resources/new plan.')
        for name in METHODS:
            score_lists[name].append(scores[name]); maps[name].append(native[name])
            detected_pixels = native[name] >= pixel_cutoffs[name]
            rows.append(dict(dataset=dataset, category=sample.category, role='validation', seed=episode['seed'],
                             shots=episode['shots'], query_id=sample.image, method=name, label=int(label),
                             image_score=scores[name], image_cutoff=cutoffs[name], predicted_defect=predicted[name],
                             correct=predicted[name] == label, pixel_cutoff=pixel_cutoffs[name],
                             defect_pixel_recall=float(detected_pixels[mask].mean()) if label else None,
                             normal_pixel_false_alarm_rate=float(detected_pixels[~mask].mean()),
                             map_path=str((output / f'query-{index:03}.npz').resolve()), map_field=name,
                             support_ids=[s.image for s in support], base_normal_images=len(support),
                             augmented_views_per_support=1, calibration_ids=list(calibration.calibration_ids),
                             calibration_category=episode['calibration_category'], candidate_pool_size=0,
                             acquisition_budget=0, feature_key=bundle.key, feature_cache_hit=bundle.cache_hit,
                             inference_seconds=inference_seconds, shared_three_branch_inference_timing=True,
                             image_and_pixel_alert_union_verified=True, metrics_map_dtype='float32', export_map_dtype='float16',
                             mask_access='offline after features, scores and locked decisions'))
    results = []
    for name in METHODS:
        image = thresholded_detection_metrics(labels, score_lists[name], cutoffs[name])
        image['accuracy'] = (image['tp'] + image['tn']) / image['queries']
        image['sensitivity'] = image['tp'] / (image['tp'] + image['fn'])
        image['specificity'] = image['tn'] / (image['tn'] + image['fp'])
        image['balanced_accuracy'] = (image['sensitivity'] + image['specificity']) / 2
        pixel = localization_metrics(masks, maps[name], pixel_cutoffs[name], max_thresholds=256)
        results.append(dict(dataset=dataset, category=episode['category'], role='validation', seed=episode['seed'],
                            shots=episode['shots'], method=name, queries=len(queries), image=image, pixel=pixel,
                            support_ids=[s.image for s in support], calibration=asdict(calibration),
                            image_score_semantics='max of separately cutoff-normalized raw branch top1% scores' if name == 'hybrid' else 'floor top1% raw patch scores, minimum one',
                            pixel_score_semantics='native pointwise max of branch/pixel-cutoff ratios' if name == 'hybrid' else 'raw branch restored by bilinear interpolation',
                            fit_seconds=fit_seconds, feature_dim=bundles[0].tokens.shape[1]))
    write_json(output / 'metrics.json', results)
    write_jsonl(output / 'predictions.jsonl', rows)
    return results, rows


def advancement_gate(results, rows, config):
    lookup = {(row['dataset'], row['category'], row['shots'], row['seed'], row['query_id'], row['method']): row for row in rows}
    bootstrap = {}
    for shots in config['shots']:
        bootstrap[str(shots)] = {}
        for comparator in METHODS[:2]:
            paired = []
            for row in rows:
                if row['shots'] == shots and row['method'] == 'hybrid':
                    other = lookup[(row['dataset'], row['category'], shots, row['seed'], row['query_id'], comparator)]
                    paired.append(dict(dataset=row['dataset'], category=row['category'], query_id=row['query_id'],
                                       seed=row['seed'], difference=int(row['correct']) - int(other['correct'])))
            bootstrap[str(shots)][comparator] = paired_crossed_bootstrap(paired, value_key='difference', n_bootstrap=2000, seed=0)
    strata = []
    for dataset in config['roots']:
        for shots in config['shots']:
            selected = [r for r in results if r['dataset'] == dataset and r['shots'] == shots]
            means = {method: {key: float(np.mean([r[level][key] for r in selected if r['method'] == method]))
                              for level, key in [('image', 'accuracy'), ('image', 'false_alarm_rate'), ('image', 'missed_defect_rate'), ('pixel', 'pixel_ap')]}
                     for method in METHODS}
            no_extra_fp = all(means['hybrid']['false_alarm_rate'] <= means[m]['false_alarm_rate'] for m in METHODS[:2])
            no_pixel_ap_loss = all(means['hybrid']['pixel_ap'] >= means[m]['pixel_ap'] for m in METHODS[:2])
            strata.append(dict(dataset=dataset, shots=shots, mean_metrics=means,
                               no_extra_false_alarms_vs_both_branches=no_extra_fp,
                               no_pixel_ap_loss_vs_both_branches=no_pixel_ap_loss))
    accuracy = all(report['interval'][0] > 0 for by_method in bootstrap.values() for report in by_method.values())
    errors = all(row['no_extra_false_alarms_vs_both_branches'] and row['no_pixel_ap_loss_vs_both_branches'] for row in strata)
    return dict(advance_to_full_experiments=accuracy and errors, paired_accuracy_bootstrap=bootstrap,
                positive_accuracy_intervals_against_both_branches_all_k=accuracy,
                false_alarm_and_pixel_ap_gate=errors, per_dataset_shot=strata,
                new_detected_to_missed_vs_either_branch=0,
                preservation='Image and native pixel alert union checked for every actual float32 prediction; recall cannot decrease relative to either branch at these fixed cutoffs.',
                reliability='Alert union can increase false alarms and does not guarantee improved accuracy or reliable classification.',
                tuning_after_evaluation=False, full_benchmarks_run=False,
                scope='Conditional descriptive validation pilot; balanced samples, previously inspected categories, only three support draws')


def run(config_path):
    config_path = Path(config_path)
    config = json.loads(config_path.read_text())
    roles = json.loads(Path(config['role_config']).read_text())['category_roles']
    validate_config(config, roles)
    output = Path(config['output']); output.mkdir(parents=True, exist_ok=True)
    if verify_stage(output, require_inputs=True, implementation_files=CODE_FILES):
        print(json.dumps(dict(status='completed_run_integrity_verified', gate=json.loads((output / 'gate.json').read_text()))), flush=True)
        return
    write_json(output / 'config.json', config)
    inventories = {}
    for dataset, root in config['roots'].items():
        samples, categories, issues, _ = discover(Path(root), dataset, None)
        if issues:
            raise ValueError('Dataset discovery issues: ' + str(issues))
        validate_category_roles(roles[dataset], categories)
        inventories[dataset] = samples
    manifest = build_manifest(config, roles, inventories)
    write_json(output / 'split_manifest.json', manifest)
    selected = {}
    for episode in manifest['episodes']:
        for key in ('support', 'queries', 'calibration_support', 'calibration_queries'):
            for item in episode[key]:
                selected[(episode['dataset'], item['image'])] = Sample(**item)
    inputs = [config_path, Path(config['role_config']), Path('/workspace/reports/real_weight_verification.json'),
              Path('/workspace/.cache/torch/hub/checkpoints/dinov2_vitb14_pretrain.pth')]
    inspected = []
    for (dataset, _), sample in selected.items():
        root = Path(config['roots'][dataset])
        inspection = inspect_sample(root, dataset, sample)
        if inspection['errors']:
            raise ValueError('Selected input failed physical verification: ' + str(inspection))
        inspected.append(inspection)
        inputs.append(root / sample.image)
        if sample.mask:
            inputs.append(root / sample.mask)
    if 'visa' in config['roots']:
        root = Path(config['roots']['visa'])
        inputs.append(root / 'split_csv/1cls.csv')
        inputs.extend(root / category / 'image_anno.csv' for category in sorted({s.category for s in inventories['visa']}))
    dependencies = dict(input_verification_version=1, input_sha256=input_fingerprints(sorted(set(inputs))),
                        implementation_sha256=implementation_hashes(CODE_FILES),
                        git_revisions={'/workspace/.cache/dinov2-source': git_revision('/workspace/.cache/dinov2-source')})
    write_json(output / 'input_verification.json', dict(status='passed', selected_original_images=len(inspected), records=inspected))
    extractor = DenseDINOv2(config['feature_cache'], config['resolution'], config['layers'])
    write_json(output / 'provenance.json', dict(
        checkpoint_sha256=extractor.checkpoint_hash, source_commit=extractor.source_commit,
        pretrained_weights_loaded=True, frozen=True, device='cpu', torch_version=torch.__version__,
        raw_features='unnormalized mean of declared DINOv2 blocks; square224 RGB bicubic',
        subspacead_inspiration='https://github.com/CLendering/SubspaceAD',
        visionad_inspiration='https://github.com/Qiqigeww/VisionAD',
        visionad_reference_revision='2d5e36f357409125ccd9646ba016824005599df4',
        scoring_implementation='independent PCA/SVD and cosine search; no VisionAD source copied',
        published_recipes_reproduced=False, augmentation='identity only',
        images_not_used_previously=manifest['unique_validation_queries'],
        categories_not_pristine=True, probability_calibration=False,
        exact_native_metrics=True, map_storage_dtype='float16', no_final_or_private_evaluation=True,
    ))
    results, rows, calibrations = [], [], []
    for index, episode in enumerate(manifest['episodes']):
        directory = output / 'episodes' / episode['dataset'] / f"seed-{episode['seed']}_k-{episode['shots']}"
        if verify_stage(directory, require_inputs=True, implementation_files=CODE_FILES):
            episode_results = json.loads((directory / 'metrics.json').read_text())
            episode_rows = read_jsonl(directory / 'predictions.jsonl')
            cal_record = json.loads((directory / 'calibration/calibration.json').read_text())
            print(json.dumps(dict(resumed_episode=index + 1, dataset=episode['dataset'], shots=episode['shots'], seed=episode['seed'])), flush=True)
        else:
            directory.mkdir(parents=True, exist_ok=True)
            calibration, cal_record = calibrate(episode, extractor, config, directory / 'calibration')
            episode_results, episode_rows = evaluate(episode, calibration, extractor, config, directory)
            files = [p.relative_to(directory) for p in directory.rglob('*') if p.is_file()]
            complete_stage(directory, files, dependencies | dict(status='completed_paired_episode'))
            print(json.dumps(dict(completed_episode=index + 1, total_episodes=len(manifest['episodes']),
                                  dataset=episode['dataset'], shots=episode['shots'], seed=episode['seed'],
                                  accuracies={r['method']: r['image']['accuracy'] for r in episode_results})), flush=True)
        results.extend(episode_results); rows.extend(episode_rows); calibrations.append(cal_record)
    write_json(output / 'metrics.json', results)
    write_jsonl(output / 'predictions.jsonl', rows)
    write_json(output / 'calibration.json', calibrations)
    gate = advancement_gate(results, rows, config)
    write_json(output / 'gate.json', gate)
    write_json(output / 'summary.json', dict(status='completed_validation_pilot', unique_validation_queries=manifest['unique_validation_queries'],
                                             paired_query_support_cases=len(rows) // len(METHODS), prediction_records=len(rows),
                                             original_input_images=len(inspected), methods=list(METHODS),
                                             supports=sorted(set(config['shots'])), support_draws=len(config['seeds']),
                                             full_benchmarks_run=False, calibration_images_are_extra_reserved_source_normals=True,
                                             outcome='advance' if gate['advance_to_full_experiments'] else 'stop_before_full_experiments'))
    files = [p.relative_to(output) for p in output.rglob('*') if p.is_file() and 'feature_cache' not in p.relative_to(output).parts
             and p.suffix in {'.json', '.jsonl', '.npz'} and p.name != 'completion.json']
    complete_stage(output, files, dependencies | dict(status='completed_validation_pilot'))
    print(json.dumps(json.loads((output / 'summary.json').read_text())), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    run(args.config)


if __name__ == '__main__':
    main()
