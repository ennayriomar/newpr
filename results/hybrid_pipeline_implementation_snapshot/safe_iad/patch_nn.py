"""Transparent frozen-DINOv2 patch nearest-neighbor internal baseline."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F


PREPROCESS_VERSION = 'rgb-resize224-pillow-bicubic-imagenet-v1'
LAYER_CONFIGURATION = 'final-x_norm_patchtokens; l2-normalized-for-scoring'


def cache_key(metadata):
    return hashlib.sha256(json.dumps(metadata, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def restore_map(patch_scores, grid, original_size):
    if patch_scores.numel() != grid[0] * grid[1]:
        raise ValueError('Patch count does not match the specified grid.')
    width, height = original_size
    return F.interpolate(patch_scores.reshape(1, 1, *grid), size=(height, width), mode='bilinear', align_corners=False)[0, 0].numpy()


def patch_nearest_neighbor(query, memory):
    """Accept feature tensors only; labels/masks never enter this scorer.

    Euclidean distance between L2-normalized patch descriptors.
    """
    if query.ndim != 2 or memory.ndim != 2 or query.shape[1] != memory.shape[1] or not len(memory):
        raise ValueError('Expected a nonempty patch memory and matching feature dimensions.')
    query, memory = F.normalize(query, dim=1), F.normalize(memory, dim=1)
    # The square root restores Euclidean distance, rather than a squared score.
    return (2 - 2 * (query @ memory.T).max(dim=1).values).clamp_min(0).sqrt()


def validate_episode(supports, queries, shots):
    if len(supports) != shots:
        raise ValueError('Strict fixed-shot support budget violated.')
    support_ids = [s.image for s in supports]
    query_ids = [q.image for q in queries]
    if len(set(support_ids)) != len(support_ids) or len(set(query_ids)) != len(query_ids):
        raise ValueError('Duplicate image IDs in an episode.')
    if set(support_ids) & set(query_ids):
        raise ValueError('Support/query overlap.')
    if any(s.split != 'train' or s.label != 'normal' for s in supports):
        raise ValueError('Supports must be verified-normal training images.')


class FrozenDINOv2:
    def __init__(self, cache_root):
        self.cache_root = Path(cache_root)
        self.cache_root.mkdir(parents=True, exist_ok=True)
        provenance = json.loads(Path('/workspace/reports/real_weight_verification.json').read_text())
        if provenance['status'] != 'verified' or not provenance['pretrained_weights_loaded']:
            raise RuntimeError('Pretrained DINOv2 verification has not succeeded.')
        checkpoint = Path('/workspace/.cache/torch/hub/checkpoints/dinov2_vitb14_pretrain.pth')
        with checkpoint.open('rb') as f:
            self.checkpoint_hash = hashlib.file_digest(f, 'sha256').hexdigest()
        if self.checkpoint_hash != provenance['checkpoint_sha256']:
            raise ValueError('Checkpoint changed since real-weight verification.')
        self.source_commit = provenance['source_commit']
        actual_commit = subprocess.check_output(['git', '-C', '/workspace/.cache/dinov2-source', 'rev-parse', 'HEAD'], text=True).strip()
        if actual_commit != self.source_commit:
            raise ValueError('DINOv2 source revision changed since verification.')
        torch.hub.set_dir('/workspace/.cache/torch/hub')
        torch.set_num_threads(3)
        torch.manual_seed(0)
        torch.use_deterministic_algorithms(True)
        self.model = torch.hub.load('/workspace/.cache/dinov2-source', 'dinov2_vitb14', source='local', pretrained=True, weights=str(checkpoint))
        self.model.eval().requires_grad_(False)
        assert not self.model.training and not any(p.requires_grad for p in self.model.parameters())

    def extract(self, dataset, sample, root):
        path = root / sample.image
        with path.open('rb') as f:
            image_hash = hashlib.file_digest(f, 'sha256').hexdigest()
        metadata = {'dataset': dataset, 'split': sample.split, 'category': sample.category, 'image_id': sample.image, 'image_sha256': image_hash, 'backbone': 'dinov2_vitb14', 'checkpoint_sha256': self.checkpoint_hash, 'source_commit': self.source_commit, 'preprocessing_version': PREPROCESS_VERSION, 'layer_configuration': LAYER_CONFIGURATION, 'torch_version': torch.__version__, 'device': 'cpu'}
        key = cache_key(metadata)
        target = self.cache_root / (key + '.npz')
        metadata_json = json.dumps(metadata, sort_keys=True)
        if target.is_file():
            with np.load(target, allow_pickle=False) as cached:
                if str(cached['metadata'].item()) != metadata_json:
                    raise ValueError('Feature-cache metadata mismatch.')
                features = cached['features'].copy()
                original_size = tuple(cached['original_size'].tolist())
            if features.shape != (256, 768):
                raise ValueError('Corrupt feature-cache shape.')
            return torch.from_numpy(features), original_size, True, key
        with Image.open(path) as image:
            original_size = image.size
            pixels = np.array(image.convert('RGB').resize((224, 224), Image.Resampling.BICUBIC), dtype=np.float32) / 255
        x = torch.from_numpy(pixels).permute(2, 0, 1).unsqueeze(0)
        x = (x - torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)) / torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
        with torch.inference_mode():
            features = self.model.forward_features(x)['x_norm_patchtokens'][0].cpu()
        if tuple(features.shape) != (256, 768):
            raise ValueError(f'Unexpected DINOv2 patch grid: {features.shape}')
        temporary = target.with_suffix('.tmp.npz')
        np.savez(temporary, features=features.numpy(), original_size=np.array(original_size), metadata=np.array(metadata_json))
        temporary.replace(target)
        return features, original_size, False, key
