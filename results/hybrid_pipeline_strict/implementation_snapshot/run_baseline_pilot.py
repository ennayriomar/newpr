"""Small real-data internal baseline pilot; no threshold selection or acquisition."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
import hashlib
import json
from pathlib import Path
import time

import numpy as np
from PIL import Image
from sklearn.metrics import average_precision_score, roc_auc_score
import torch

from .patch_nn import FrozenDINOv2, LAYER_CONFIGURATION, PREPROCESS_VERSION, cache_key, patch_nearest_neighbor, restore_map, validate_episode
from .verify_dataset import discover


@dataclass
class Prediction:
    dataset: str
    category: str
    image_id: str
    image_anomaly_score: float
    defect_map: str
    reference_diagnostics: dict
    predicted_intervention_benefit: float | None
    action: str | None
    support_ids: list[str]
    selected_reference_ids: list[str]
    valid_field_masks: dict
    timing_seconds: dict


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    output = Path(config['output'])
    output.mkdir(parents=True, exist_ok=True)
    config_path = output / 'config.json'
    if config_path.exists() and json.loads(config_path.read_text()) != config:
        raise ValueError('Run output contains a different configuration; use a new output directory.')
    config_path.write_text(json.dumps(config, indent=2) + '\n')
    extractor = FrozenDINOv2(config['feature_cache'])
    episode_results = []
    for benchmark in config['benchmarks']:
        dataset, category, root = benchmark['dataset'], benchmark['category'], Path(benchmark['root'])
        verification = json.loads(Path(benchmark['verification_report']).read_text())
        if verification['status'] != 'passed' or verification['root'] != str(root.resolve()):
            raise ValueError('Dataset verification must pass for the configured root.')
        samples, _, issues, _ = discover(root, dataset, None)
        if issues:
            raise ValueError(f'Dataset discovery errors: {issues}')
        train = sorted([s for s in samples if s.category == category and s.split == 'train' and s.label == 'normal'], key=lambda s: s.image)
        queries = []
        for label in ['normal', 'anomaly']:
            queries.extend(sorted([s for s in samples if s.category == category and s.split == 'test' and s.label == label], key=lambda s: s.image)[:config['queries_per_label']])
        if len(queries) != 2 * config['queries_per_label']:
            raise ValueError('Insufficient pilot queries.')
        input_hashes = {}
        def hash_input(relative):
            if relative is None:
                return None
            if relative not in input_hashes:
                with (root / relative).open('rb') as f:
                    input_hashes[relative] = hashlib.file_digest(f, 'sha256').hexdigest()
            return input_hashes[relative]
        for seed in config['seeds']:
            rng = np.random.default_rng(seed)
            drawn = [train[i] for i in rng.choice(len(train), size=max(config['shots']), replace=False)]
            for shots in config['shots']:
                supports = drawn[:shots]
                validate_episode(supports, queries, shots)
                episode = output / dataset / category / f'seed-{seed}_k-{shots}'
                episode.mkdir(parents=True, exist_ok=True)
                manifest = {'dataset': dataset, 'category': category, 'seed': seed, 'shots': shots, 'protocol': 'A_strict_fixed_shot', 'candidate_pool_size': 0, 'acquisition_budget': 0, 'support_ids': [s.image for s in supports], 'query_ids': [q.image for q in queries], 'checkpoint_sha256': extractor.checkpoint_hash, 'source_commit': extractor.source_commit, 'preprocessing': PREPROCESS_VERSION, 'layer_configuration': LAYER_CONFIGURATION, 'test_labels_used_for_tuning': False, 'validation_and_calibration': 'not used; no thresholds or calibration fitted', 'query_sampling': 'first sorted normal/anomaly test images; predeclared feasibility subset, not the full test set'}
                manifest['data_fingerprints'] = [{'image_id': s.image, 'image_sha256': hash_input(s.image), 'mask_sha256': hash_input(s.mask)} for s in supports + queries]
                signature = cache_key(manifest)
                complete = episode / 'metrics.json'
                if complete.exists():
                    previous = json.loads(complete.read_text())
                    if previous['manifest_signature'] != signature:
                        old_manifest = json.loads((episode / 'manifest.json').read_text())
                        without_fingerprints = {key: value for key, value in manifest.items() if key != 'data_fingerprints'}
                        if old_manifest != without_fingerprints:
                            raise ValueError('Cannot resume a mismatched episode or changed input data.')
                        # Upgrade the first pilot's manifest to fingerprint image and mask bytes.
                        # Preserve its metrics, then recompute rather than trusting legacy results.
                        legacy = episode / 'metrics_before_input_fingerprints.json'
                        if not legacy.exists():
                            legacy.write_text(complete.read_text())
                    else:
                        rows = [json.loads(line) for line in (episode / 'predictions.jsonl').read_text().splitlines()]
                        if len(rows) != len(queries):
                            raise ValueError('Incomplete resumed prediction records.')
                        for row in rows:
                            with np.load(row['defect_map'], allow_pickle=False) as data:
                                width, height = row['original_size']
                                if data['defect_map'].shape != (height, width):
                                    raise ValueError('Invalid resumed prediction map.')
                        episode_results.append(previous)
                        continue
                (episode / 'manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
                started = time.perf_counter()
                memory = torch.cat([extractor.extract(dataset, support, root)[0] for support in supports])
                predictions, image_scores, image_labels, pixel_scores, pixel_labels = [], [], [], [], []
                for index, query in enumerate(queries):
                    extraction_start = time.perf_counter()
                    features, original_size, cached, feature_key = extractor.extract(dataset, query, root)
                    extraction_seconds = time.perf_counter() - extraction_start
                    scoring_start = time.perf_counter()
                    scores = patch_nearest_neighbor(features, memory)
                    image_score = float(torch.topk(scores, k=max(1, int(np.ceil(len(scores) * 0.01)))).values.mean())
                    restored = restore_map(scores, (16, 16), original_size).astype(np.float32)
                    assert restored.shape == (original_size[1], original_size[0])
                    map_path = episode / f'query-{index:03d}.npz'
                    np.savez_compressed(map_path, defect_map=restored)
                    predictions.append(asdict(Prediction(dataset, category, query.image, image_score, str(map_path), {}, None, None, manifest['support_ids'], [], {'defect_map': True, 'support_adequacy': False, 'reference_diagnostics': False, 'predicted_intervention_benefit': False, 'action': False}, {'feature_extraction_or_cache': extraction_seconds, 'scoring_restore_export': time.perf_counter() - scoring_start})))
                    predictions[-1].update(feature_cache_hit=cached, feature_cache_key=feature_key, original_size=list(original_size))
                    # Labels/masks enter only offline evaluation, after inference.
                    image_labels.append(query.label == 'anomaly')
                    image_scores.append(image_score)
                    if query.mask:
                        with Image.open(root / query.mask) as mask:
                            truth = np.asarray(mask) > 0
                    else:
                        truth = np.zeros(restored.shape, dtype=bool)
                    if truth.shape != restored.shape:
                        raise ValueError('Mask/map shape mismatch.')
                    pixel_scores.append(restored.ravel())
                    pixel_labels.append(truth.ravel())
                truth, scores = np.concatenate(pixel_labels), np.concatenate(pixel_scores)
                metrics = {'dataset': dataset, 'category': category, 'seed': seed, 'shots': shots, 'queries': len(queries), 'image_auroc': float(roc_auc_score(image_labels, image_scores)), 'image_ap': float(average_precision_score(image_labels, image_scores)), 'pixel_auroc': float(roc_auc_score(truth, scores)), 'pixel_ap': float(average_precision_score(truth, scores)), 'manifest_signature': signature, 'elapsed_seconds': time.perf_counter()-started, 'scope': 'small real-data feasibility pilot; one category; no performance/generalization claim', 'unrun_metrics': ['AU-PRO', 'thresholded F1/IoU', 'calibration/reliability', 'acquisition', 'statistical confidence intervals']}
                with (episode / 'predictions.jsonl').open('w') as f:
                    for prediction in predictions:
                        f.write(json.dumps(prediction) + '\n')
                complete.write_text(json.dumps(metrics, indent=2) + '\n')
                episode_results.append(metrics)
                print(json.dumps(metrics), flush=True)
                del truth, scores, pixel_labels, pixel_scores
    (output / 'episodes.json').write_text(json.dumps(episode_results, indent=2) + '\n')
    print(json.dumps({'completed_episodes': len(episode_results), 'method': 'DINOv2 patch NN internal baseline'}), flush=True)


if __name__ == '__main__':
    main()
