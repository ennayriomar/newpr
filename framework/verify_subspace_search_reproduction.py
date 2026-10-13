"""Two actual-query cache-bypass checks for a completed PCA/search pilot.

This checks one anomaly query per dataset, including exact CPU feature/score
and float16 map agreement. It is not a full independent benchmark rerun.
"""
import argparse
import json
from pathlib import Path

import numpy as np
import torch

from safe_iad.adaptive_subspace_search import SupportScaledSearch
from safe_iad.dense_features import DenseDINOv2, restore_dense
from safe_iad.experiment_io import write_json
from safe_iad.subspace_search import BranchCalibration, SubspaceSearch, fuse
from safe_iad.verify_dataset import Sample


def verify(run, report):
    run = Path(run)
    if not (run / 'completion.json').is_file():
        raise ValueError('Finish the pilot before testing its recorded outcomes.')
    config = json.loads((run / 'config.json').read_text())
    manifest = json.loads((run / 'split_manifest.json').read_text())
    records = [json.loads(line) for line in (run / 'predictions.jsonl').read_text().splitlines()]
    extractor = DenseDINOv2(run / 'reproduction_cache', config['resolution'], config['layers'])
    factory = SupportScaledSearch if config.get('prototype') in {
        'support_scaled_subspace_search', 'target_normal_calibrated_subspace_search'
    } else SubspaceSearch
    checks = []
    for dataset in config['roots']:
        episode = next(e for e in manifest['episodes'] if e['dataset'] == dataset and e['shots'] == 2)
        query = Sample(**next(q for q in episode['queries'] if q['label'] == 'anomaly'))
        root = Path(config['roots'][dataset])
        query_bundle = extractor.extract_dense(dataset, query, root, 'subspacead', use_cache=False)
        old_cache = Path(config['feature_cache']) / (query_bundle.key + '.npz')
        with np.load(old_cache, allow_pickle=False) as saved:
            feature_equal = np.array_equal(query_bundle.tokens.numpy(), saved['tokens'])
        if not feature_equal:
            raise ValueError('Newly recomputed real features differ from the original cache.')
        memory = []
        for item in episode['support']:
            bundle = extractor.extract_dense(dataset, Sample(**item), root, 'subspacead')
            # Fresh support features must also match the original bank features.
            with np.load(Path(config['feature_cache']) / (bundle.key + '.npz'), allow_pickle=False) as saved:
                if not np.array_equal(bundle.tokens.numpy(), saved['tokens']):
                    raise ValueError('Newly recomputed support features differ from original bank.')
            memory.append(bundle.tokens)
        model = factory(torch.cat(memory), explained_variance=config['explained_variance'])
        directory = run / 'episodes' / dataset / f"seed-{episode['seed']}_k-{episode['shots']}"
        calibration_record = json.loads((directory / 'calibration/calibration.json').read_text())
        calibration = BranchCalibration(**calibration_record['cutoffs'])
        raw = model.predict_raw(query_bundle.tokens)
        native = {name: restore_dense(raw[name], query_bundle).astype('float32') for name in ('search', 'subspace')}
        fused = fuse({name: torch.from_numpy(value.ravel()) for name, value in native.items()}, calibration,
                     image_scores=(raw['image_search'], raw['image_subspace']))
        native['hybrid'] = fused['hybrid'].numpy().reshape(native['search'].shape).astype('float32')
        prior = [r for r in records if r['dataset'] == dataset and r['query_id'] == query.image
                 and r['shots'] == episode['shots'] and r['seed'] == episode['seed']]
        if len(prior) != 3:
            raise ValueError('Recorded paired probe case is incomplete.')
        score = dict(search=raw['image_search'], subspace=raw['image_subspace'], hybrid=fused['image_hybrid'])
        for row in prior:
            if row['image_score'] != score[row['method']]:
                raise ValueError('Recomputed real image scores differ from recorded metrics.')
        with np.load(prior[0]['map_path'], allow_pickle=False) as saved:
            if any(not np.array_equal(saved[name], native[name].astype('float16')) for name in native):
                raise ValueError('Fresh real-query native maps differ from original float16 exports.')
        checks.append(dict(dataset=dataset, query_id=query.image, seed=episode['seed'], shots=episode['shots'],
                           query_and_support_backbone_cache_bypassed=True, float32_features_bitwise_equal=True,
                           branch_and_hybrid_image_scores_exact_equal=True, all_three_float16_maps_bitwise_equal=True,
                           total_fresh_images=1 + episode['shots']))
    record = dict(status='passed', checkpoint_sha256=extractor.checkpoint_hash, source_commit=extractor.source_commit,
                  prototype=config.get('prototype', 'raw_subspace_search'), real_query_probes=checks,
                  scope='One actual anomaly query per dataset, with freshly extracted query and support features; no full independent rerun or cross-hardware guarantee.')
    write_json(report, record)
    print(json.dumps(record, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    args = parser.parse_args()
    verify(args.run, args.report)


if __name__ == '__main__':
    main()
