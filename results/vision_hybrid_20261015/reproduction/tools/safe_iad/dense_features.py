"""Frozen, provenance-keyed dense features with explicit spatial transforms."""
from dataclasses import dataclass
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, __version__ as pillow_version
import torch
import torch.nn.functional as F
import torchvision
from torchvision import transforms

from .patch_nn import FrozenDINOv2, cache_key


@dataclass
class DenseFeatures:
    tokens: torch.Tensor
    grid: tuple
    original_size: tuple
    resized_size: tuple
    padded_size: tuple
    mode: str
    key: str
    cache_hit: bool


def letterbox_geometry(size, resolution, stride=14):
    if resolution < stride or resolution % stride:
        raise ValueError('Resolution must be a positive multiple of patch stride.')
    w, h = size
    scale = resolution / max(w, h)
    rw, rh = max(1, round(w * scale)), max(1, round(h * scale))
    pw, ph = ((rw + stride - 1) // stride) * stride, ((rh + stride - 1) // stride) * stride
    return (rw, rh), (pw, ph)


def restore_dense(scores, bundle):
    if len(scores) != bundle.grid[0] * bundle.grid[1]:
        raise ValueError('Feature grid and map disagree.')
    x = scores.detach().float().reshape(1, 1, *bundle.grid)
    if bundle.mode == 'hybrid':
        pw, ph = bundle.padded_size
        rw, rh = bundle.resized_size
        x = F.interpolate(x, (ph, pw), mode='bilinear', align_corners=False)[:, :, :rh, :rw]
    w, h = bundle.original_size
    return F.interpolate(x, (h, w), mode='bilinear', align_corners=False)[0, 0].numpy()


class DenseDINOv2(FrozenDINOv2):
    def __init__(self, cache_root, resolution=224, layers=(2, 5, 8, 11)):
        super().__init__(cache_root)
        letterbox_geometry((10, 10), resolution)
        if sorted(set(layers)) != list(layers) or not layers or min(layers) < 0 or max(layers) > 11:
            raise ValueError('Expected distinct increasing ViT-B block indices in [0,11].')
        self.resolution, self.layers = resolution, tuple(layers)
        self.adino_transform = transforms.Compose([
            transforms.Resize(resolution, interpolation=transforms.InterpolationMode.BICUBIC, antialias=True),
            transforms.ToTensor(), transforms.Normalize((.485, .456, .406), (.229, .224, .225))])

    def extract_dense(self, dataset, sample, root, mode='hybrid', use_cache=True):
        if mode not in {'hybrid', 'anomalydino', 'subspacead'}:
            raise ValueError('Unknown feature transform.')
        path = Path(root) / sample.image
        with path.open('rb') as f:
            digest = hashlib.file_digest(f, 'sha256').hexdigest()
        meta = dict(dataset=dataset, category=sample.category, split=sample.split, image_id=sample.image,
                    image_sha256=digest, checkpoint_sha256=self.checkpoint_hash, source_commit=self.source_commit,
                    preprocessing_version='dense-native-geometry-v1', mode=mode, resolution=self.resolution,
                    layers=[11] if mode == 'anomalydino' else list(self.layers),
                    aggregation='normalized-concatenation' if mode == 'hybrid' else 'raw-mean' if mode == 'subspacead' else 'last-normalized',
                    torch_version=torch.__version__, numpy_version=np.__version__,
                    pillow_version=pillow_version, torchvision_version=torchvision.__version__, device='cpu')
        key = cache_key(meta)
        target = self.cache_root / (key + '.npz')
        metadata_json = json.dumps(meta, sort_keys=True)
        if target.exists() and use_cache:
            with np.load(target, allow_pickle=False) as saved:
                if str(saved['metadata'].item()) != metadata_json:
                    raise ValueError('Feature cache provenance mismatch.')
                tokens = torch.from_numpy(saved['tokens'].copy())
                geometry = {name: tuple(saved[name].tolist()) for name in ['grid', 'original_size', 'resized_size', 'padded_size']}
            expected_dim = 768 * len(self.layers) if mode == 'hybrid' else 768
            if tokens.shape != (np.prod(geometry['grid']), expected_dim) or not torch.isfinite(tokens).all():
                raise ValueError('Corrupt dense feature cache.')
            return DenseFeatures(tokens, **geometry, mode=mode, key=key, cache_hit=True)
        with Image.open(path) as im:
            im = im.convert('RGB')
            original = im.size
            if mode == 'anomalydino':
                x = self.adino_transform(im)
                rh, rw = x.shape[-2:]
                pw, ph = rw - rw % 14, rh - rh % 14
                x = x[:, :ph, :pw]
                resized = (rw, rh)
            else:
                resized, padded = letterbox_geometry(original, self.resolution) if mode == 'hybrid' else ((self.resolution,)*2, (self.resolution,)*2)
                rw, rh = resized
                pw, ph = padded
                pixels = np.array(im.resize(resized, Image.Resampling.BICUBIC), dtype=np.float32) / 255.
                pixels = np.pad(pixels, ((0, ph-rh), (0, pw-rw), (0, 0)), mode='edge')
                x = torch.from_numpy(pixels).permute(2, 0, 1)
                x = (x - torch.tensor([.485, .456, .406])[:, None, None]) / torch.tensor([.229, .224, .225])[:, None, None]
        assert not self.model.training and not any(p.requires_grad for p in self.model.parameters())
        with torch.inference_mode():
            outputs = self.model.get_intermediate_layers(x.unsqueeze(0), n=[11] if mode == 'anomalydino' else self.layers, norm=mode != 'subspacead')
            if mode == 'hybrid':
                tokens = torch.cat([F.normalize(t[0], dim=1) for t in outputs], dim=1) / np.sqrt(len(outputs))
            elif mode == 'subspacead':
                tokens = torch.stack([t[0] for t in outputs]).mean(dim=0)
            else:
                tokens = outputs[0][0]
            tokens = tokens.detach().cpu().contiguous()
        bundle = DenseFeatures(tokens, (ph//14, pw//14), original, resized, (pw, ph), mode, key, False)
        temporary = target.with_suffix('.tmp.npz')
        np.savez(temporary, tokens=tokens.numpy(), metadata=np.array(metadata_json), **{n: np.array(getattr(bundle, n)) for n in ['grid', 'original_size', 'resized_size', 'padded_size']})
        temporary.replace(target)
        return bundle
