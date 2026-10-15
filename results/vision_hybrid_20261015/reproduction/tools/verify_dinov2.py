"""Attempt actual pretrained DINOv2 loading and a real-image extraction.

This standalone probe is not an anomaly detector or benchmark pilot.
"""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import time

import numpy as np
from PIL import Image
import torch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--image', type=Path, required=True)
    parser.add_argument('--report', type=Path, required=True)
    args = parser.parse_args()
    source = Path('/workspace/.cache/dinov2-source')
    commit = subprocess.check_output(['git', '-C', str(source), 'rev-parse', 'HEAD'], text=True).strip()
    torch.hub.set_dir('/workspace/.cache/torch/hub')
    torch.set_num_threads(4)
    torch.manual_seed(0)
    torch.use_deterministic_algorithms(True)
    report = {
        'status': 'pretrained_loading_in_progress', 'backbone': 'DINOv2 ViT-B/14',
        'source_repository': 'https://github.com/facebookresearch/dinov2', 'source_commit': commit,
        'checkpoint_url': 'https://dl.fbaipublicfiles.com/dinov2/dinov2_vitb14/dinov2_vitb14_pretrain.pth',
        'torch': torch.__version__, 'cuda_available': torch.cuda.is_available(), 'device': 'cpu',
        'pretrained_weights_loaded': False, 'random_fallback_used': False,
        'frozen_parameters_verified': False, 'eval_mode_verified': False,
        'patch_grid_verified': False, 'real_data_model_pilot_run': False,
        'image': str(args.image), 'phase': 'load_pretrained',
    }
    try:
        # The official loader loads its pretrained state dictionary strictly.
        # Any download/loading exception aborts this probe; no fallback model is used.
        model = torch.hub.load(str(source), 'dinov2_vitb14', source='local', pretrained=True)
        report['pretrained_weights_loaded'] = True
        checkpoint = Path(torch.hub.get_dir()) / 'checkpoints/dinov2_vitb14_pretrain.pth'
        with checkpoint.open('rb') as f:
            report['checkpoint_sha256'] = hashlib.file_digest(f, 'sha256').hexdigest()
        report['checksum_scope'] = 'Recorded checksum of the artifact obtained by the official HTTPS loader; no publisher-provided checksum is asserted.'
        model.eval()
        model.requires_grad_(False)
        report['frozen_parameters_verified'] = not any(p.requires_grad for p in model.parameters())
        report['eval_mode_verified'] = not model.training
        report['phase'] = 'real_image_extraction'
        with Image.open(args.image) as image:
            original = list(image.size)
            array = np.array(image.convert('RGB').resize((224, 224), Image.Resampling.BICUBIC), dtype=np.float32) / 255.0
        x = torch.from_numpy(array).permute(2, 0, 1).unsqueeze(0)
        mean = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
        std = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)
        x = (x - mean) / std
        started = time.perf_counter()
        with torch.inference_mode():
            first = model.forward_features(x)['x_norm_patchtokens']
            second = model.forward_features(x)['x_norm_patchtokens']
        assert tuple(first.shape) == (1, 256, 768), tuple(first.shape)
        assert torch.equal(first, second), 'Repeated CPU extraction is not bitwise identical.'
        report.update(status='verified', phase='complete', patch_grid_verified=True, patch_grid=[16, 16], feature_shape=list(first.shape), deterministic_repeat_verified=True, original_image_size=original, two_extractions_seconds=time.perf_counter()-started, preprocessing='RGB; full-image resize to 224x224 with Pillow bicubic (aspect ratio may change); float32 /255; ImageNet mean/std; final normalized patch tokens. Pilot preprocessing, not a claimed faithful AnomalyDINO reproduction.')
        result = 0
    except Exception as exc:
        report.update(status='failed', error=f'{type(exc).__name__}: {exc}')
        result = 2
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))
    raise SystemExit(result)


if __name__ == '__main__':
    main()
