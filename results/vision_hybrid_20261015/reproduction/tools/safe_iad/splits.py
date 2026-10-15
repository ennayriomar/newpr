"""Declared experiment roles; no inferred calibration or final-label tuning."""
from collections import Counter
import hashlib
import json
from pathlib import Path

import numpy as np

from .verify_dataset import discover


def validate_category_roles(roles, categories):
    assigned = [category for group in roles.values() for category in group]
    if len(assigned) != len(set(assigned)):
        raise ValueError('Category roles overlap.')
    if set(assigned) != set(categories):
        raise ValueError('Category roles must cover the actual discovered categories exactly.')
    if set(roles) != {'meta_training', 'validation', 'calibration', 'final_test'}:
        raise ValueError('Four explicit category roles are required.')


def validate_partition(support_ids, candidate_ids, query_source_ids):
    groups = [support_ids, candidate_ids, query_source_ids]
    if any(len(group) != len(set(group)) for group in groups):
        raise ValueError('Duplicate IDs in a partition.')
    for left, right in [(0, 1), (0, 2), (1, 2)]:
        if set(groups[left]) & set(groups[right]):
            raise ValueError('Support/candidate/query partition overlap.')


def require_training_source(dataset, sample, config):
    if sample.category not in config['category_roles'][dataset]['meta_training']:
        raise ValueError('Counterfactual training targets cannot use validation/calibration/final categories.')
    if sample.split != 'train' or sample.label != 'normal':
        raise ValueError('Training targets require original normal training images only.')


def prepare_manifests(config):
    output = Path(config['output'])
    output.mkdir(parents=True, exist_ok=True)
    source_episodes, records = [], []
    for dataset, root_string in config['roots'].items():
        root = Path(root_string)
        samples, categories, issues, _ = discover(root, dataset, None)
        if issues:
            raise ValueError(f'Dataset discovery failed: {issues}')
        source_query_ids = set()
        if dataset in config['category_roles']:
            roles = config['category_roles'][dataset]
            validate_category_roles(roles, categories)
            source_category = config['source_categories'][dataset]
            if source_category not in roles['meta_training']:
                raise ValueError('Source category is not meta-training.')
            normal = sorted([s for s in samples if s.category == source_category and s.split == 'train' and s.label == 'normal'], key=lambda s:s.image)
            needed = len(config['seeds']) * config['source_queries_per_seed']
            rng = np.random.default_rng(config['partition_seed'])
            ordering = rng.permutation(len(normal))
            source_query_ids = {normal[i].image for i in ordering[:needed]}
            query_partition = [normal[i] for i in ordering[:needed]]
            reference_partition = [normal[i] for i in ordering[needed:]]
            for index, seed in enumerate(config['seeds']):
                chosen = np.random.default_rng(seed).choice(len(reference_partition), size=config['initial_shots']+config['candidate_pool_size'], replace=False)
                supports = [reference_partition[i] for i in chosen[:config['initial_shots']]]
                candidates = [reference_partition[i] for i in chosen[config['initial_shots']:]]
                queries = query_partition[index*config['source_queries_per_seed']:(index+1)*config['source_queries_per_seed']]
                for sample in supports+candidates+queries:
                    require_training_source(dataset, sample, config)
                validate_partition([s.image for s in supports], [s.image for s in candidates], list(source_query_ids))
                source_episodes.append({'dataset':dataset,'category':source_category,'seed':seed,'root':str(root),'support_ids':[s.image for s in supports],'candidate_ids':[s.image for s in candidates],'query_source_ids':[s.image for s in queries],'all_reserved_query_source_ids':sorted(source_query_ids)})
            role_for_category = {cat:role for role,cats in roles.items() for cat in cats}
            for sample in samples:
                category_role = role_for_category[sample.category]
                if category_role == 'meta_training':
                    role = ('meta_training_query_normal' if sample.image in source_query_ids else 'meta_training_reference_normal') if sample.split=='train' else 'excluded_source_native_test'
                elif sample.split=='train':
                    role = category_role + '_support_candidate_pool'
                else:
                    role = category_role + '_query'
                records.append({'image_id':f'{dataset}:{sample.image}','dataset':dataset,'category':sample.category,'native_split':sample.split,'experiment_role':role,'image':sample.image})
        else:
            # AD 2 is a robustness benchmark, not a source of M2 predictor targets.
            # Native defect-free validation is partitioned for distinct roles.
            calibration_ids = set()
            for category in categories:
                validation = sorted([s.image for s in samples if s.category==category and s.split=='validation'])
                salt = int.from_bytes(hashlib.sha256(category.encode()).digest()[:4], 'little')
                order = np.random.default_rng(config['partition_seed']+salt).permutation(len(validation))
                calibration_ids.update(validation[i] for i in order[:len(validation)//2])
            for sample in samples:
                if sample.split=='train':
                    role='stress_support_candidate_pool'
                elif sample.split=='validation':
                    role='stress_calibration_normal' if sample.image in calibration_ids else 'stress_validation_normal'
                else:
                    role='stress_final_public_query'
                records.append({'image_id':f'{dataset}:{sample.image}','dataset':dataset,'category':sample.category,'native_split':sample.split,'experiment_role':role,'image':sample.image})
    if len({r['image_id'] for r in records}) != len(records):
        raise ValueError('Duplicate global image IDs.')
    with (output/'split_manifest.jsonl').open('w') as f:
        for record in records:
            f.write(json.dumps(record)+'\n')
    summary = {'partition_seed':config['partition_seed'],'category_roles':config['category_roles'],'counts':dict(Counter(r['experiment_role'] for r in records)),'images_assigned':len(records),'source_episodes':source_episodes,'policy':'Native test images of declared validation/calibration categories are reserved for those roles, not final evaluation. Source native-test images are excluded from target construction. AD2 private data is absent. Native AD2 validation is normal-only; no defect-probability calibration is implied.'}
    (output/'split_manifest.json').write_text(json.dumps(summary,indent=2)+'\n')
    return source_episodes
