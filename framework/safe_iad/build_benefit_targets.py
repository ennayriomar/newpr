"""Broaden signed benefit supervision using permitted normal-training images."""
import argparse
import hashlib
import json
from pathlib import Path
import numpy as np
import torch

from .build_training_targets import synthetic_query
from .counterfactual import FEATURE_NAMES, inference_feature_vector, offline_loss, support_diagnostics
from .experiment_io import (complete_stage, image_score, implementation_hashes,
                            input_fingerprints, sha256, verify_stage, write_json, write_jsonl)
from .patch_nn import FrozenDINOv2, LAYER_CONFIGURATION, PREPROCESS_VERSION, patch_nearest_neighbor, restore_map
from .splits import validate_category_roles, validate_partition
from .verify_dataset import discover


TARGET_IMPLEMENTATIONS = ('build_benefit_targets.py', 'build_training_targets.py',
                         'counterfactual.py', 'acquisition.py', 'experiment_io.py',
                         'patch_nn.py', 'splits.py', 'verify_dataset.py')


def build(config):
    output = Path(config['output'])/'targets'
    output.mkdir(parents=True, exist_ok=True)
    write_json(output/'config.json', config)
    if verify_stage(output, require_inputs=True, implementation_files=TARGET_IMPLEMENTATIONS):
        return json.loads((output/'summary.json').read_text())
    implementations = implementation_hashes(TARGET_IMPLEMENTATIONS)
    inputs = input_fingerprints([output/'config.json',
                                '/workspace/reports/real_weight_verification.json',
                                '/workspace/.cache/torch/hub/checkpoints/dinov2_vitb14_pretrain.pth'])

    def record_inputs(paths):
        for path in paths:
            absolute = str(Path(path).absolute())
            if absolute not in inputs:
                inputs[absolute] = sha256(path)

    extractor = FrozenDINOv2(config['feature_cache'])
    rows = {'training': [], 'validation': []}
    episodes = []
    synthetic_checks = []
    for dataset, root_string in config['roots'].items():
        if dataset not in config['source_categories']:
            continue
        root = Path(root_string)
        samples, categories, issues, split_csv = discover(root, dataset, None)
        if issues:
            raise ValueError('Dataset discovery errors: '+str(issues))
        if split_csv is not None:
            record_inputs([split_csv])
        validate_category_roles(config['category_roles'][dataset], categories)
        for phase, categories_selected, per_seed in [
            ('training', config['source_categories'][dataset], config['source_queries_per_seed']),
            ('validation', [config['validation_categories'][dataset]], config['validation_queries_per_seed'])]:
            required_role = 'meta_training' if phase == 'training' else 'validation'
            for category in categories_selected:
                if category not in config['category_roles'][dataset][required_role]:
                    raise ValueError('Target category has the wrong experiment role')
                normals = sorted([s for s in samples if s.category == category and s.split == 'train' and s.label == 'normal'], key=lambda s:s.image)
                needed = len(config['seeds'])*per_seed
                salt = int.from_bytes(hashlib.sha256(f'{dataset}:{category}'.encode()).digest()[:4], 'little')
                order = np.random.default_rng(config['partition_seed']+salt).permutation(len(normals))
                queries = [normals[i] for i in order[:needed]]
                references_allowed = [normals[i] for i in order[needed:]]
                reserved = [s.image for s in queries]
                max_shots = max(config['target_shots'])
                if len(references_allowed) < max_shots+config['candidate_pool_size']:
                    raise ValueError('Not enough disjoint normal references')
                for index, seed in enumerate(config['seeds']):
                    draw = np.random.default_rng(seed).choice(len(references_allowed), max_shots+config['candidate_pool_size'], replace=False)
                    supports = [references_allowed[i] for i in draw[:max_shots]]
                    candidates = [references_allowed[i] for i in draw[max_shots:]]
                    sources = queries[index*per_seed:(index+1)*per_seed]
                    validate_partition([s.image for s in supports], [s.image for s in candidates], reserved)
                    record_inputs([root/sample.image for sample in supports+candidates+sources])
                    support_features = [extractor.extract(dataset, s, root)[0] for s in supports]
                    candidate_features = [extractor.extract(dataset, s, root)[0] for s in candidates]
                    for source in sources:
                        normal_features, size, _, normal_key = extractor.extract(dataset, source, root)
                        synthetic, mask, synthetic_provenance = synthetic_query(dataset, source, root, Path(config['generated_root']), seed)
                        record_inputs([Path(config['generated_root'])/synthetic.image,
                                       Path(config['generated_root'])/synthetic.mask])
                        edited_features, edited_size, _, synthetic_key = extractor.extract(dataset, synthetic, Path(config['generated_root']))
                        if edited_size != size:
                            raise ValueError('Synthetic geometry changed')
                        from PIL import Image
                        with Image.open(root/source.image) as a, Image.open(Path(config['generated_root'])/synthetic.image) as b:
                            changed = int(np.count_nonzero(np.any(np.asarray(a.convert('RGB')) != np.asarray(b.convert('RGB')), axis=2)))
                        if changed == 0:
                            raise ValueError('Synthetic edit did not change source pixels')
                        synthetic_checks.append({'dataset': dataset, 'source_id': source.image, 'synthetic_id': synthetic.image, 'changed_pixels': changed})
                        for query, features, truth, kind, key in [
                            (source, normal_features, np.zeros((size[1],size[0]), dtype=bool), 'real_normal_training_query', normal_key),
                            (synthetic, edited_features, mask, 'synthetic_cutpaste_training_query', synthetic_key)]:
                            for shots in config['target_shots']:
                                bank = support_features[:shots]
                                diagnostics = support_diagnostics(features, bank)
                                before_scores = diagnostics['nearest_distance']
                                before = restore_map(before_scores, (16,16), size)
                                loss_before = offline_loss(before, truth, config['loss'], image_score=image_score(before_scores))
                                for candidate, candidate_feature in zip(candidates, candidate_features):
                                    after_scores = patch_nearest_neighbor(features, torch.cat(bank+[candidate_feature]))
                                    vector = inference_feature_vector(features, bank, candidate_feature, diagnostics, after_scores)
                                    after = restore_map(after_scores, (16,16), size)
                                    loss_after = offline_loss(after, truth, config['loss'], image_score=image_score(after_scores))
                                    row = {'dataset': dataset, 'category': category,
                                           'experiment_role': 'meta_training' if phase == 'training' else 'validation_source_normal_or_synthetic',
                                           'native_query_source_split': 'train', 'query_kind': kind,
                                           'seed': seed, 'shots': shots, 'query_id': query.image,
                                           'query_source_id': source.image, 'support_ids': [s.image for s in supports[:shots]],
                                           'candidate_pool_ids': [s.image for s in candidates], 'candidate_id': candidate.image,
                                           'loss_before': loss_before, 'loss_after': loss_after,
                                           'observed_benefit': loss_before-loss_after,
                                           'features': vector, 'feature_names': FEATURE_NAMES,
                                           'loo_defined': shots > 1, 'loo_missing_indicator': int(shots == 1),
                                           'checkpoint_sha256': extractor.checkpoint_hash, 'source_commit': extractor.source_commit,
                                           'preprocessing_version': PREPROCESS_VERSION, 'feature_layer_configuration': LAYER_CONFIGURATION,
                                           'feature_cache_key': key, 'loss_specification': config['loss'],
                                           'synthetic_provenance': synthetic_provenance if kind.startswith('synthetic') else None,
                                           'final_test_labels_used': False, 'candidate_patch_probes': len(candidates)}
                                    if not np.isfinite(vector).all() or not np.isfinite(row['observed_benefit']):
                                        raise ValueError('Nonfinite supervision')
                                    rows[phase].append(row)
                    episodes.append({'phase': phase, 'dataset': dataset, 'category': category, 'seed': seed,
                                     'nested_support_ids': [s.image for s in supports],
                                     'candidate_ids': [s.image for s in candidates], 'query_source_ids': [s.image for s in sources],
                                     'globally_reserved_query_source_ids': reserved})
                    print(json.dumps({'targets_phase': phase, 'dataset': dataset, 'category': category, 'seed': seed,
                                      'rows_so_far': len(rows[phase])}), flush=True)
    for phase in rows:
        write_jsonl(output/f'{phase}.jsonl', rows[phase])
    write_json(output/'split_manifest.json', {'episodes': episodes, 'category_roles': config['category_roles'],
                                             'native_test_masks_opened': False, 'all_training_references_are_normal_train': True})
    write_json(output/'synthetic_checks.json', synthetic_checks)
    summary = {phase: {'rows': len(items),
                       'unique_source_images': len({(r['dataset'],r['query_source_id']) for r in items}),
                       'negative_rows': sum(r['observed_benefit'] < -1e-8 for r in items),
                       'negative_source_images': len({(r['dataset'],r['query_source_id']) for r in items if r['observed_benefit'] < -1e-8}),
                       'normal_query_benefit_is_monotone_nn_loss_property': True}
               for phase, items in rows.items()}
    summary.update(checkpoint_sha256=extractor.checkpoint_hash, source_commit=extractor.source_commit,
                   feature_names=FEATURE_NAMES, preprocessing_version=PREPROCESS_VERSION,
                   synthetic_edits_are_not_real_defect_evidence=True, final_test_labels_used=False)
    write_json(output/'summary.json', summary)
    complete_stage(output, ['training.jsonl','validation.jsonl','split_manifest.json','synthetic_checks.json','summary.json','config.json'],
                   {'implementation_sha256': implementations, 'input_sha256': inputs,
                    'input_verification_version': 1,
                    'git_revisions': {'/workspace/.cache/dinov2-source': extractor.source_commit}})
    print(json.dumps(summary), flush=True)
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    build(json.loads(args.config.read_text()))


if __name__ == '__main__':
    main()
