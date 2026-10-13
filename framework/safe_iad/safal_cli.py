"""Train, evaluate and apply the complete independent SAFAL research model.

Only normal training images fit target support/cutoffs. Native test labels and
masks are opened after prediction, solely for descriptive evaluation. Optional
error probabilities are fitted on source normal/CutPaste proxy events; their
transfer to industrial defects is an empirical question, not a guarantee.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F

from .build_training_targets import synthetic_query
from .dense_features import restore_dense
from .experiment_io import (complete_stage, implementation_hashes, read_jsonl,
                            sha256, verify_stage, write_json, write_jsonl)
from .research_metrics import (localization_metrics, paired_crossed_bootstrap,
                               risk_coverage, thresholded_detection_metrics)
from .verify_dataset import discover

METHODS = ('search', 'subspace', 'fixed_avg', 'max', 'safal')
CODE_FILES = ('safal_cli.py', 'safal_model.py', 'safal_features.py',
              'safal_calibration.py', 'subspace_search.py', 'dense_features.py',
              'patch_nn.py', 'experiment_io.py', 'research_metrics.py',
              'verify_dataset.py', 'build_training_targets.py')


def _salt(value):
    return int.from_bytes(hashlib.sha256(value.encode()).digest()[:4], 'little')


def inventory(config, dataset):
    root = Path(config['roots'][dataset]).resolve(strict=True)
    if any(part.endswith('.unverified') for part in root.parts):
        raise ValueError('Unverified dataset staging may not be used.')
    rows, _, issues, _ = discover(root, dataset, None)
    if issues:
        raise ValueError(f'Dataset inventory has unresolved issues: {issues[:3]}')
    if len({s.image for s in rows}) != len(rows):
        raise ValueError('Duplicate native image IDs.')
    return root, {s.image: s for s in rows}


def validate_episode(episode, lookup):
    """Enforce original-image budgets before any image extraction."""
    groups = [episode[name] for name in ('support_ids', 'calibration_ids', 'query_ids')]
    if not groups[0] or not groups[1]:
        raise ValueError('Nonempty support and extra normal calibration are required.')
    if any(len(ids) != len(set(ids)) for ids in groups):
        raise ValueError('Duplicate image IDs within an episode.')
    if any(set(groups[i]) & set(groups[j]) for i in range(3) for j in range(i+1, 3)):
        raise ValueError('Support/calibration/evaluation image overlap.')
    if len(groups[0]) != episode['shots']:
        raise ValueError('Original-image shot budget violated.')
    if episode['k_plus_calibration'] != len(groups[0]) + len(groups[1]):
        raise ValueError('Total target-normal information budget is incorrect.')
    for identifier in sum(groups, []):
        if identifier not in lookup or lookup[identifier].category != episode['category']:
            raise ValueError('Unknown image or category mismatch.')
    for identifier in groups[0] + groups[1]:
        sample = lookup[identifier]
        if sample.split != 'train' or sample.label != 'normal':
            raise ValueError('Only normal native training images fit support/cutoffs.')
    for identifier in groups[2]:
        if lookup[identifier].split not in {'test', 'test_public'}:
            raise ValueError('Evaluation must use declared native public test images.')


def build_manifest(config, inventories):
    if config.get('schema_version') != 1:
        raise ValueError('Unsupported SAFAL configuration schema.')
    shots, seeds = config['shots'], config['seeds']
    if not shots or shots != sorted(set(shots)) or any(type(k) is not int or k < 1 for k in shots):
        raise ValueError('Shots must be distinct increasing positive integers.')
    if not seeds or len(set(seeds)) != len(seeds) or any(type(s) is not int or s < 0 for s in seeds):
        raise ValueError('Support seeds must be distinct nonnegative integers.')
    for key in ('normal_calibration_images', 'queries_per_label', 'source_fit_parents', 'source_cal_parents'):
        if type(config[key]) is not int or config[key] < 2:
            raise ValueError(f'{key} must be an integer >=2.')
    quantile = config['normal_calibration_quantile']
    if isinstance(quantile, bool) or not np.isfinite(quantile) or not 0 < quantile <= 1:
        raise ValueError('Normal quantile must lie in (0,1].')
    if not 0 <= config['abstain_error_probability'] <= 1:
        raise ValueError('Abstention probability cutoff must lie in [0,1].')
    source, episodes = [], []
    for dataset, (_, lookup) in inventories.items():
        roles = config['category_roles'][dataset]
        if any(set(roles[a]) & set(roles[b]) for a in roles for b in roles if a < b):
            raise ValueError('Category roles must be disjoint.')
        for category in config['source_categories'][dataset]:
            if category not in roles['meta_training']:
                raise ValueError('Source proxy fitting requires source categories.')
            bank = sorted(s.image for s in lookup.values() if s.category == category
                          and s.split == 'train' and s.label == 'normal')
            needed = 2 + config['normal_calibration_images'] + config['source_fit_parents'] + config['source_cal_parents']
            if len(bank) < needed:
                raise ValueError('Insufficient disjoint source normal images.')
            order = np.random.default_rng(config['partition_seed']+_salt(dataset+category)).permutation(len(bank))
            chosen = [bank[i] for i in order[:needed]]
            boundary = 2+config['normal_calibration_images']
            source.append(dict(dataset=dataset, category=category, support_ids=chosen[:2],
                               calibration_ids=chosen[2:boundary],
                               fit_parent_ids=chosen[boundary:boundary+config['source_fit_parents']],
                               heldout_parent_ids=chosen[boundary+config['source_fit_parents']:]))
        for category in config['validation_categories'][dataset]:
            if category not in roles['validation']:
                raise ValueError('Demo evaluates declared validation categories, never final categories.')
            bank = sorted(s.image for s in lookup.values() if s.category == category
                          and s.split == 'train' and s.label == 'normal')
            rng = np.random.default_rng(config['partition_seed']+_salt(dataset+category))
            if len(bank) < max(shots)+config['normal_calibration_images']:
                raise ValueError('Insufficient disjoint target normal images.')
            permutation = rng.permutation(len(bank))
            cal = [bank[i] for i in permutation[:config['normal_calibration_images']]]
            bank = [bank[i] for i in permutation[config['normal_calibration_images']:]]
            queries = []
            for label in ('normal', 'anomaly'):
                candidates = sorted(s.image for s in lookup.values() if s.category == category
                                    and s.split in {'test', 'test_public'} and s.label == label)
                if len(candidates) < config['queries_per_label']:
                    raise ValueError('Insufficient native evaluation queries.')
                queries += [candidates[i] for i in rng.choice(len(candidates), config['queries_per_label'], replace=False)]
            for seed in seeds:
                support = [bank[i] for i in np.random.default_rng(seed+_salt(dataset+category)).choice(len(bank), max(shots), replace=False)]
                for k in shots:
                    episode = dict(id=f'{dataset}-{category}-k{k}-seed{seed}', dataset=dataset,
                                   category=category, role='validation', seed=seed, shots=k,
                                   support_ids=support[:k], calibration_ids=cal, query_ids=queries,
                                   k_plus_calibration=k+len(cal), strict_k_image_few_shot=False,
                                   support_views=['identity'])
                    validate_episode(episode, lookup)
                    episodes.append(episode)
    return dict(schema_version=1, scope='safal_full_model_validation', source_episodes=source,
                episodes=episodes, category_roles=config['category_roles'],
                metric_geometry='256x256 bilinear score maps; nearest-neighbor native binary masks',
                calibration_domain='source normal plus CutPaste proxy error; native transfer unverified',
                protocol='support/cutoffs fitted on normal training images; evaluation labels accessed after scoring')


def make_encoder(config):
    from .safal_features import SAFALEncoder
    allowed = {'source_dir', 'checkpoint', 'cache_root', 'resolution', 'layers', 'threads', 'source_manifest'}
    settings = config['encoder'].get('runtime_config', config['encoder'])
    return SAFALEncoder(**{key: value for key, value in settings.items() if key in allowed})


def _check_encoder(model, encoder):
    expected = model.checkpoint_provenance.get('encoder')
    if expected is None:
        raise ValueError('Checkpoint has no verified encoder binding.')
    actual = encoder.metadata()
    keys = ('backbone', 'checkpoint_sha256', 'source_commit', 'source_manifest_sha256',
            'resolution', 'layers', 'preprocessing_version', 'aggregation', 'spatial_transform',
            'implementation_sha256', 'torch_version', 'numpy_version', 'pillow_version')
    if any(expected.get(key) != actual.get(key) for key in keys):
        raise ValueError('Inference encoder differs from the fitted checkpoint representation.')


def _fit(episode, lookup, root, encoder, quantile, output):
    from .safal_model import SAFALModel
    support = [encoder.extract(root/i).tokens for i in episode['support_ids']]
    model = SAFALModel(support, [episode['dataset']+':'+i for i in episode['support_ids']])
    normals = [encoder.extract(root/i).tokens for i in episode['calibration_ids']]
    model.calibrate(normals, [episode['dataset']+':'+i for i in episode['calibration_ids']], quantile=quantile)
    model.save(output/'model', provenance=dict(encoder=encoder.metadata(), dataset=episode['dataset'],
               category=episode['category'], support_images=len(support),
               extra_normal_calibration_images=len(normals),
               k_plus_calibration=len(support)+len(normals), support_views=['identity'],
               fitting_split='native train normal only'))
    write_json(output/'encoder.json', encoder.metadata())
    write_json(output/'episode.json', episode)
    return model


def error_features(prediction):
    return [abs(prediction['image_scores']['safal']-1.), prediction['A'],
            prediction['branch_disagreement'], prediction['U']]


def fit_proxy_calibration(config, manifest, inventories, encoder, output):
    from .safal_calibration import ERROR_FEATURE_NAMES, fit_error_calibrator
    rows, generated = [], output/'generated_source_queries'
    for episode in manifest['source_episodes']:
        root, lookup = inventories[episode['dataset']]
        folder = output/'source_models'/(episode['dataset']+'-'+episode['category'])
        folder.mkdir(parents=True, exist_ok=True)
        model = _fit(episode, lookup, root, encoder, config['normal_calibration_quantile'], folder)
        for role, ids in (('meta_training', episode['fit_parent_ids']), ('source_calibration', episode['heldout_parent_ids'])):
            for identifier in ids:
                parent = lookup[identifier]
                synthetic, _, provenance = synthetic_query(episode['dataset'], parent, root, generated, config['partition_seed'])
                for sample, path, is_synthetic in ((parent, root/identifier, False), (synthetic, generated/synthetic.image, True)):
                    bundle = encoder.extract(path)
                    prediction = model.predict(bundle.tokens)
                    predicted = prediction['image_scores']['safal'] >= 1.
                    rows.append(dict(dataset=episode['dataset'], category=episode['category'],
                                     query_id=sample.image, query_source_id=identifier,
                                     native_query_source_split='train', experiment_role=role,
                                     domain='source_normal_plus_cutpaste', target='prediction_error',
                                     query_kind='cutpaste' if is_synthetic else 'normal',
                                     error_label=int(predicted != is_synthetic), features=error_features(prediction),
                                     feature_names=list(ERROR_FEATURE_NAMES), support_ids=episode['support_ids'],
                                     calibration_ids=episode['calibration_ids'], synthetic_provenance=provenance if is_synthetic else None,
                                     feature_key=bundle.key, image_sha256=sha256(path),
                                     native_final_labels_used=False))
        print(json.dumps(dict(stage='source_proxy', dataset=episode['dataset'], category=episode['category'], rows=len(rows))), flush=True)
    write_jsonl(output/'source_calibration.jsonl', rows)
    calibrator, report = fit_error_calibrator([r for r in rows if r['experiment_role'] == 'meta_training'],
                                            [r for r in rows if r['experiment_role'] == 'source_calibration'],
                                            config['category_roles'], seed=config['partition_seed'])
    calibrator.save(output/'error_calibrator.json')
    write_json(output/'calibration_report.json', report)
    return calibrator


def _metric_map(tokens, grid):
    return F.interpolate(tokens.detach().float().reshape(1, 1, *grid), (256, 256),
                         mode='bilinear', align_corners=False)[0, 0].numpy()


def evaluate_episode(episode, model, root, lookup, encoder, calibrator, output, abstain_probability=.2):
    from .safal_calibration import probability_metrics
    output.mkdir(parents=True, exist_ok=True)
    _check_encoder(model, encoder)
    rows, truths, maps, scores = [], [], {m: [] for m in METHODS}, {m: [] for m in METHODS}
    labels, probabilities, errors, uncertainties = [], [], [], []
    for index, identifier in enumerate(episode['query_ids']):
        start = time.perf_counter()
        bundle = encoder.extract(root/identifier)
        prediction = model.predict(bundle.tokens)
        fields = {m: _metric_map(prediction['maps'][m], bundle.grid) for m in METHODS}
        fields.update({f'raw_{branch}': _metric_map(prediction['raw'][branch], bundle.grid)
                       for branch in ('search', 'subspace')})
        fields['adequacy'] = _metric_map(prediction['patch_adequacy'], bundle.grid)
        fields['uncertainty'] = _metric_map(prediction['patch_uncertainty'], bundle.grid)
        fields['search_weight'] = _metric_map(prediction['weights']['search'], bundle.grid)
        fields['branch_disagreement'] = _metric_map(prediction['patch_branch_disagreement'], bundle.grid)
        output_map = output/f'query-{index:03}.npz'
        if any(not np.isfinite(v).all() for v in fields.values()):
            raise ValueError('Nonfinite prediction export.')
        np.savez_compressed(output_map, **fields)
        # Preserve a small full-precision feature-only replay input per episode.
        if index == 0:
            np.savez_compressed(output/'probe.npz', query_tokens=bundle.tokens.numpy(),
                                grid=np.array(bundle.grid), original_size=np.array(bundle.original_size))
        probability = None if calibrator is None else float(calibrator.predict(
            np.array([error_features(prediction)]), domain='native_industrial_validation')[0])
        decision = prediction['image_scores']['safal'] >= 1.
        action = 'abstain' if probability is not None and probability > abstain_probability else ('anomaly' if decision else 'normal')
        inference_seconds = time.perf_counter()-start
        # Ground truth enters only this reporting block, after every prediction.
        sample = lookup[identifier]
        label = sample.label == 'anomaly'
        if sample.mask:
            with Image.open(root/sample.mask) as im:
                native_mask = np.asarray(im.convert('L')) > 0
            if native_mask.shape != (bundle.original_size[1], bundle.original_size[0]):
                raise ValueError('Native mask and image sizes disagree.')
            mask = np.array(Image.fromarray(native_mask).resize((256, 256), Image.Resampling.NEAREST), dtype=bool)
        else:
            mask = np.zeros((256, 256), dtype=bool)
        if bool(mask.any()) != label:
            raise ValueError('Metric-resolution mask lost the defect or native label is inconsistent.')
        truths.append(mask); labels.append(label); errors.append(int(decision != label)); uncertainties.append(prediction['U'])
        if probability is not None:
            probabilities.append(probability)
        for method in METHODS:
            score = float(prediction['image_scores'][method])
            scores[method].append(score); maps[method].append(fields[method])
            rows.append(dict(dataset=episode['dataset'], category=episode['category'], seed=episode['seed'],
                             shots=episode['shots'], role=episode.get('role', 'evaluation'), query_id=identifier,
                             label=int(label), method=method, image_score=score, predicted_anomaly=bool(score >= 1.),
                             A=prediction['A'], U=prediction['U'], branch_disagreement=prediction['branch_disagreement'],
                             raw_image_scores=prediction['raw_image_scores'],
                             image_leave_one_out_valid=bool(prediction['loo']['valid'].all()),
                             image_leave_one_out_missing_reason=prediction['loo']['missing_reason'],
                             image_leave_one_out_mean={branch: float(prediction['loo'][branch].mean())
                                 if prediction['loo'][branch] is not None else None for branch in ('search', 'subspace')},
                             search_weight=float(prediction['weights']['search'].mean()),
                             error_probability=probability if method == 'safal' else None,
                             error_domain='source_normal_plus_cutpaste; native transfer unverified' if probability is not None else None,
                             action=action if method == 'safal' else ('anomaly' if score >= 1. else 'normal'),
                             k_plus_calibration=episode['k_plus_calibration'], strict_k_image_few_shot=False,
                             feature_key=bundle.key, feature_cache_hit=bundle.cache_hit,
                             original_size=list(bundle.original_size), map_file=output_map.name,
                             map_shape=[256, 256], map_dtype='float32', map_space='resized_metric',
                             metric_grid=[256, 256], inference_seconds=inference_seconds,
                             label_access='offline after feature-only prediction'))
    metrics = {m: dict(detection=thresholded_detection_metrics(labels, scores[m], 1.),
                       localization=localization_metrics(truths, maps[m], 1., max_thresholds=128)) for m in METHODS}
    reliability = dict(diagnostic=risk_coverage(errors, 1.-np.array(uncertainties)),
                       probability_event='binary SAFAL image-decision error at locked threshold 1',
                       native_probability_calibration_claim=False)
    if probabilities:
        probability_array = np.array(probabilities)
        accepted = probability_array <= abstain_probability
        reliability.update(probability=probability_metrics(errors, probability_array),
                           selective=risk_coverage(errors, 1.-probability_array),
                           abstention_cutoff=abstain_probability, coverage=float(accepted.mean()),
                           accepted_error_rate=float(np.array(errors)[accepted].mean()) if accepted.any() else None)
    write_jsonl(output/'predictions.jsonl', rows)
    write_json(output/'metrics.json', metrics)
    write_json(output/'reliability.json', reliability)
    return rows, metrics, reliability


def used_inputs(manifest, inventories):
    memberships = {}
    for episode in manifest['source_episodes'] + manifest['episodes']:
        for key, role in (('support_ids', 'support'), ('calibration_ids', 'normal_calibration'),
                          ('query_ids', 'native_evaluation'), ('fit_parent_ids', 'source_proxy_fit_parent'),
                          ('heldout_parent_ids', 'source_proxy_cal_parent')):
            for identifier in episode.get(key, []):
                memberships.setdefault((episode['dataset'], identifier), set()).add(role)
    result = []
    for (dataset, identifier), roles in sorted(memberships.items()):
        root, lookup = inventories[dataset]
        sample = lookup[identifier]
        result.append(asdict(sample) | dict(dataset=dataset, roles=sorted(roles), path=str(root/identifier),
                      image_sha256=sha256(root/identifier),
                      mask_path=str(root/sample.mask) if sample.mask else None,
                      mask_sha256=sha256(root/sample.mask) if sample.mask else None))
    return result


def run_demo(config, output):
    if verify_stage(output, require_inputs=True, implementation_files=CODE_FILES):
        print(json.dumps(dict(status='verified_resume', output=str(output))), flush=True)
        return
    output.mkdir(parents=True, exist_ok=True)
    write_json(output/'config.json', config)
    inventories = {dataset: inventory(config, dataset) for dataset in config['roots']}
    manifest = build_manifest(config, inventories)
    write_json(output/'manifest.json', manifest)
    inputs = used_inputs(manifest, inventories)
    write_json(output/'used_inputs.json', inputs)
    fingerprints = {row['path']: row['image_sha256'] for row in inputs}
    fingerprints.update({row['mask_path']: row['mask_sha256'] for row in inputs if row['mask_path']})
    fingerprints[config['encoder']['checkpoint']] = sha256(config['encoder']['checkpoint'])
    for dataset, (root, _) in inventories.items():
        if dataset == 'visa':
            split = root/'split_csv/1cls.csv'
            fingerprints[str(split)] = sha256(split)
    code = implementation_hashes(CODE_FILES)
    encoder = make_encoder(config)
    encoder_metadata = encoder.metadata()
    source_dir = Path(config['encoder']['source_dir'])
    fingerprints.update({str(source_dir/name): digest for name, digest in encoder_metadata['source_files_sha256'].items()})
    calibrator = fit_proxy_calibration(config, manifest, inventories, encoder, output)
    for row in read_jsonl(output/'source_calibration.jsonl'):
        if row['query_kind'] == 'cutpaste':
            fingerprints[str(output/'generated_source_queries'/row['query_id'])] = row['image_sha256']
    all_rows, all_metrics = [], []
    for episode in manifest['episodes']:
        folder = output/'episodes'/episode['id']
        root, lookup = inventories[episode['dataset']]
        if verify_stage(folder, require_inputs=True, implementation_files=CODE_FILES):
            rows, metrics = read_jsonl(folder/'predictions.jsonl'), json.loads((folder/'metrics.json').read_text())
        else:
            folder.mkdir(parents=True, exist_ok=True)
            start = time.perf_counter()
            model = _fit(episode, lookup, root, encoder, config['normal_calibration_quantile'], folder)
            fit_seconds = time.perf_counter()-start
            rows, metrics, _ = evaluate_episode(episode, model, root, lookup, encoder, calibrator, folder,
                                                config['abstain_error_probability'])
            write_json(folder/'timing.json', dict(fit_including_features_seconds=fit_seconds))
            files = [p.relative_to(folder).as_posix() for p in folder.rglob('*') if p.is_file()]
            complete_stage(folder, files, dict(input_verification_version=1, input_sha256=fingerprints,
                                               implementation_sha256=code))
        all_rows += rows
        all_metrics.append(dict(episode=episode['id'], metrics=metrics))
        print(json.dumps(dict(stage='validation', episode=episode['id'], records=len(rows))), flush=True)
    write_jsonl(output/'predictions.jsonl', all_rows)
    mean_metrics = {}
    for method in METHODS:
        accuracies = [(r['metrics'][method]['detection']['tp']+r['metrics'][method]['detection']['tn'])/r['metrics'][method]['detection']['queries'] for r in all_metrics]
        mean_metrics[method] = dict(accuracy=float(np.mean(accuracies)),
            image_auroc=float(np.mean([r['metrics'][method]['detection']['auroc'] for r in all_metrics])),
            pixel_ap=float(np.mean([r['metrics'][method]['localization']['pixel_ap'] for r in all_metrics])))
    paired_values = {}
    for episode in manifest['episodes']:
        rows = [r for r in all_rows if r['dataset'] == episode['dataset'] and r['category'] == episode['category']
                and r['seed'] == episode['seed'] and r['shots'] == episode['shots']]
        lookup = {(r['query_id'], r['method']): r for r in rows}
        for q in episode['query_ids']:
            final, fixed = lookup[q, 'safal'], lookup[q, 'fixed_avg']
            # k uses nested subsets of the SAME draw. Average those dependent
            # conditions before bootstrapping the actual query x seed units.
            key = (episode['dataset'], episode['category'], q, episode['seed'])
            paired_values.setdefault(key, []).append(int(final['predicted_anomaly'] == final['label'])
                                                      -int(fixed['predicted_anomaly'] == fixed['label']))
    paired = [dict(dataset=key[0], category=key[1], query_id=key[2], seed=key[3],
                   paired_difference=float(np.mean(values))) for key, values in sorted(paired_values.items())]
    summary = dict(version='0.5.0', episodes=len(manifest['episodes']), prediction_records=len(all_rows),
                   unique_native_queries=len({(r['dataset'], r['query_id']) for r in all_rows}),
                   support_draws=len(config['seeds']), shots=config['shots'], mean_episode_metrics=mean_metrics,
                   paired_safal_minus_fixed_accuracy=paired_crossed_bootstrap(paired, n_bootstrap=1000, seed=917),
                   paired_shot_aggregation='average dependent nested-shot differences within each query/seed before crossed bootstrap',
                   tested_pretrained_encoder=True, published_recipes_reproduced=False,
                   strict_k_image_few_shot=False, full_benchmark_completed=False,
                   probability_calibration_domain='source normal/CutPaste proxy only; native transfer unverified',
                   adequacy_semantics='bounded query-relative branch-coverage diagnostic, not correctness probability',
                   claim='working research implementation and bounded validation; higher accuracy not established')
    write_json(output/'summary.json', summary)
    files = [p.relative_to(output).as_posix() for p in output.rglob('*')
             if p.is_file() and p != output/'completion.json' and 'generated_source_queries' not in p.parts]
    complete_stage(output, files, dict(input_verification_version=1, input_sha256=fingerprints,
                                       implementation_sha256=code))
    print(json.dumps(summary), flush=True)


def run_train(config, output):
    episode = config['episode']
    root, lookup = inventory(config, episode['dataset'])
    validate_episode(episode, lookup)
    if episode['query_ids']:
        raise ValueError('Train configuration must contain no evaluation queries.')
    output.mkdir(parents=True, exist_ok=True)
    write_json(output/'config.json', config)
    _fit(episode, lookup, root, make_encoder(config), config['normal_calibration_quantile'], output)
    print(json.dumps(dict(status='fitted', model=str(output/'model'), target_normals=episode['k_plus_calibration'])))


def run_evaluate(config, prefix, output, calibrator_path=None):
    from .safal_model import SAFALModel
    from .safal_calibration import ErrorCalibrator
    model = SAFALModel.load(prefix)
    episode = config['episode']
    root, lookup = inventory(config, episode['dataset'])
    validate_episode(episode, lookup)
    if model.support_ids != tuple(episode['dataset']+':'+i for i in episode['support_ids']):
        raise ValueError('Configuration support IDs differ from the fitted checkpoint.')
    if tuple(model.calibration.calibration_ids) != tuple(episode['dataset']+':'+i for i in episode['calibration_ids']):
        raise ValueError('Configuration calibration IDs differ from the fitted checkpoint.')
    calibrator = None if calibrator_path is None else ErrorCalibrator.load(calibrator_path)
    evaluate_episode(episode, model, root, lookup, make_encoder(config), calibrator, output,
                     config.get('abstain_error_probability', .2))


def run_predict(prefix, image, encoder_config, output, calibrator_path=None):
    from .safal_model import SAFALModel
    from .safal_calibration import ErrorCalibrator
    model = SAFALModel.load(prefix)
    encoder = make_encoder({'encoder': encoder_config})
    _check_encoder(model, encoder)
    bundle = encoder.extract(image)
    prediction = model.predict(bundle.tokens)
    output.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(output/'maps.npz', **{m: restore_dense(prediction['maps'][m], bundle) for m in METHODS},
                        adequacy=restore_dense(prediction['patch_adequacy'], bundle),
                        uncertainty=restore_dense(prediction['patch_uncertainty'], bundle))
    probability = None if calibrator_path is None else float(ErrorCalibrator.load(calibrator_path).predict(
        np.array([error_features(prediction)]), domain='deployment_unverified')[0])
    score = prediction['image_scores']['safal']
    record = dict(image=str(image), image_sha256=sha256(image), image_scores=prediction['image_scores'],
                  predicted_anomaly=bool(score >= 1), threshold=1., A=prediction['A'], U=prediction['U'],
                  adequacy_semantics='coverage diagnostic, not probability', error_probability=probability,
                  probability_transfer_verified=False, original_size=list(bundle.original_size),
                  encoder=encoder.metadata(), feature_key=bundle.key,
                  support_budget=dict(original_images=len(model.support_ids),
                      extra_normal_calibration_images=len(model.calibration.calibration_ids),
                      strict_k_image_few_shot=False))
    write_json(output/'prediction.json', record)
    print(json.dumps(record), flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    prepare = sub.add_parser('prepare', help='Download pinned source and checksum-verified pretrained weights')
    prepare.add_argument('--destination', type=Path, required=True)
    for command in ('train', 'demo', 'evaluate'):
        child = sub.add_parser(command)
        child.add_argument('--config', type=Path, required=True)
        child.add_argument('--output', type=Path, required=True)
        if command == 'evaluate':
            child.add_argument('--model', type=Path, required=True)
            child.add_argument('--error-calibrator', type=Path)
    predict = sub.add_parser('predict')
    predict.add_argument('--model', type=Path, required=True)
    predict.add_argument('--image', type=Path, required=True)
    predict.add_argument('--encoder-config', type=Path, required=True)
    predict.add_argument('--error-calibrator', type=Path)
    predict.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.command == 'prepare':
        from .safal_features import prepare_encoder
        print(json.dumps(prepare_encoder(args.destination), indent=2))
    elif args.command == 'predict':
        run_predict(args.model, args.image, json.loads(args.encoder_config.read_text()), args.output, args.error_calibrator)
    else:
        config = json.loads(args.config.read_text())
        if args.command == 'demo':
            run_demo(config, args.output)
        elif args.command == 'train':
            run_train(config, args.output)
        else:
            run_evaluate(config, args.model, args.output, args.error_calibrator)


if __name__ == '__main__':
    main()
