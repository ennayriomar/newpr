"""Portable, checksum-verified frozen DINOv2 features for SAFAL.

The extractor always loads the real pinned ViT-B/14 checkpoint. Source-only
copies require a manifest anchored to the pinned official Python-file digest.
No datasets, historical reports, or workstation-specific paths are required.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.parse
import urllib.request

import numpy as np
from PIL import Image, __version__ as pillow_version
import torch

from .dense_features import DenseFeatures


SOURCE_PIN = '7764ea0f912e53c92e82eb78a2a1631e92725fc8'
SOURCE_URL = 'https://github.com/facebookresearch/dinov2.git'
CHECKPOINT_URL = 'https://dl.fbaipublicfiles.com/dinov2/dinov2_vitb14/dinov2_vitb14_pretrain.pth'
CHECKPOINT_SHA256 = '0b8b82f85de91b424aded121c7e1dcc2b7bc6d0adeea651bf73a13307fad8c73'
# Canonical sorted JSON of SHA256 entries for every tracked *.py and LICENSE
# at SOURCE_PIN, independently derived from the verified official checkout.
SOURCE_FILES_SHA256 = '9ed9679525be8520b45cd087ce2bff1cd684f438ac82bc0d6080e36487adf340'
SOURCE_MANIFEST_NAME = 'source_manifest.sha256.json'
PREPROCESS_VERSION = 'safal-rgb-square-pillow-bicubic-imagenet-raw-block-mean-v1'


def _sha256(path: Path) -> str:
    with path.open('rb') as handle:
        return hashlib.file_digest(handle, 'sha256').hexdigest()


def _canonical(value) -> str:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def _manifest_digest(files: dict) -> str:
    return hashlib.sha256(_canonical(files).encode()).hexdigest()


def validate_configuration(resolution: int, layers, threads: int = 3) -> tuple[int, ...]:
    if type(resolution) is not int or resolution < 14 or resolution % 14:
        raise ValueError('Resolution must be a positive integer multiple of 14.')
    layers = tuple(layers)
    if not layers or any(type(i) is not int or not 0 <= i <= 11 for i in layers):
        raise ValueError('ViT-B layers must be integer block indices in [0,11].')
    if list(layers) != sorted(set(layers)):
        raise ValueError('Layers must be distinct and increasing.')
    if type(threads) is not int or threads < 1:
        raise ValueError('A positive integer CPU thread count is required.')
    return layers


def _git(source: Path, *args) -> str:
    try:
        return subprocess.check_output(['git', '-C', str(source), *args], text=True,
                                       stderr=subprocess.PIPE).strip()
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        raise ValueError('Cannot verify the pinned DINOv2 Git checkout.') from exc


def verify_source(source_dir, source_manifest=None) -> dict:
    source = Path(source_dir).expanduser().resolve()
    if not source.is_dir():
        raise ValueError('The pinned official DINOv2 source directory is missing.')
    if (source / '.git').exists():
        if _git(source, 'rev-parse', 'HEAD') != SOURCE_PIN:
            raise ValueError('DINOv2 Git HEAD does not match the required source pin.')
        if _git(source, 'status', '--porcelain', '--untracked-files=no'):
            raise ValueError('DINOv2 tracked files are modified; a clean source is required.')
        paths = _git(source, 'ls-files').splitlines()
        files = {p: _sha256(source / p) for p in paths if p.endswith('.py') or p == 'LICENSE'}
        kind = 'clean-pinned-git-checkout'
    else:
        manifest_path = Path(source_manifest) if source_manifest is not None else source / SOURCE_MANIFEST_NAME
        if not manifest_path.is_file():
            raise ValueError('Bundled DINOv2 source requires its pinned source SHA256 manifest.')
        manifest = json.loads(manifest_path.read_text())
        if manifest.get('source_commit') != SOURCE_PIN or not isinstance(manifest.get('files'), dict):
            raise ValueError('Bundled source manifest does not identify the required source pin.')
        files = manifest['files']
        if manifest.get('file_manifest_sha256') != SOURCE_FILES_SHA256:
            raise ValueError('Bundled source manifest digest is not the trusted pinned digest.')
        kind = 'pinned-manifest-verified-bundle'
    if _manifest_digest(files) != SOURCE_FILES_SHA256:
        raise ValueError('DINOv2 source file manifest differs from the pinned official source.')
    for relative, expected in files.items():
        p = Path(relative)
        if p.is_absolute() or '..' in p.parts:
            raise ValueError('Unsafe source manifest path.')
        target = source / p
        if target.is_symlink() or not target.is_file() or _sha256(target) != expected:
            raise ValueError(f'Pinned DINOv2 source file failed SHA256 verification: {relative}')
    present_python = {p.relative_to(source).as_posix() for p in source.rglob('*.py')
                      if '.git' not in p.relative_to(source).parts}
    expected_python = {p for p in files if p.endswith('.py')}
    if present_python != expected_python:
        raise ValueError('Unexpected or missing Python files in the DINOv2 source directory.')
    return dict(source_commit=SOURCE_PIN, source_verification=kind,
                source_files_sha256=files, source_manifest_sha256=SOURCE_FILES_SHA256)


def export_source_manifest(source_dir, destination=None) -> Path:
    """Export a trusted manifest from a clean pinned checkout for code bundles."""
    source = Path(source_dir).expanduser().resolve()
    if not (source / '.git').exists():
        raise ValueError('Manifest export requires the clean pinned official Git checkout.')
    verified = verify_source(source)
    target = Path(destination) if destination is not None else source / SOURCE_MANIFEST_NAME
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(dict(source_commit=SOURCE_PIN,
                                    file_manifest_sha256=SOURCE_FILES_SHA256,
                                    files=verified['source_files_sha256']), indent=2, sort_keys=True) + '\n')
    return target


def preprocess_rgb(image: Image.Image, resolution: int = 224) -> torch.Tensor:
    validate_configuration(resolution, (11,))
    pixels = np.array(image.convert('RGB').resize((resolution, resolution), Image.Resampling.BICUBIC),
                      dtype=np.float32) / 255.0
    x = torch.from_numpy(pixels).permute(2, 0, 1).unsqueeze(0)
    mean = x.new_tensor([.485, .456, .406]).view(1, 3, 1, 1)
    std = x.new_tensor([.229, .224, .225]).view(1, 3, 1, 1)
    return (x - mean) / std


def feature_cache_key(metadata: dict) -> str:
    return hashlib.sha256(_canonical(metadata).encode()).hexdigest()


def _validate_tokens(tokens: np.ndarray, resolution: int):
    expected = ((resolution // 14) ** 2, 768)
    if tokens.dtype != np.float32 or tokens.shape != expected or not np.isfinite(tokens).all():
        raise ValueError('Feature cache requires finite float32 ViT-B patch descriptors of the declared shape.')


def _read_cache(path: Path, metadata: dict, resolution: int, original_size: tuple) -> DenseFeatures:
    with np.load(path, allow_pickle=False) as cached:
        required = {'tokens', 'metadata', 'grid', 'original_size', 'resized_size', 'padded_size'}
        if set(cached.files) != required:
            raise ValueError('Feature cache schema mismatch.')
        saved_meta = cached['metadata']
        if saved_meta.shape != () or saved_meta.dtype.kind != 'U' or saved_meta.item() != _canonical(metadata):
            raise ValueError('Feature cache provenance mismatch.')
        tokens = cached['tokens'].copy()
        _validate_tokens(tokens, resolution)
        geometry = {}
        for name in ['grid', 'original_size', 'resized_size', 'padded_size']:
            value = cached[name]
            if value.shape != (2,) or value.dtype.kind not in 'iu' or np.any(value <= 0):
                raise ValueError('Feature cache geometry is corrupt.')
            geometry[name] = tuple(int(v) for v in value)
    expected_grid = (resolution // 14, resolution // 14)
    if (geometry['grid'] != expected_grid or geometry['original_size'] != original_size or
            geometry['resized_size'] != (resolution, resolution) or
            geometry['padded_size'] != (resolution, resolution)):
        raise ValueError('Feature cache geometry disagrees with the declared preprocessing.')
    return DenseFeatures(torch.from_numpy(tokens), **geometry, mode='subspacead',
                         key=feature_cache_key(metadata), cache_hit=True)


class SAFALEncoder:
    def __init__(self, source_dir, checkpoint, cache_root, resolution=224,
                 layers=(2, 5, 8, 11), threads=3, *, source_manifest=None):
        self.layers = validate_configuration(resolution, layers, threads)
        self.resolution, self.threads = resolution, threads
        self.source_dir = Path(source_dir).expanduser().resolve()
        self.checkpoint = Path(checkpoint).expanduser().resolve()
        self.cache_root = Path(cache_root).expanduser().resolve()
        self.source_manifest = (Path(source_manifest).expanduser().resolve() if source_manifest is not None
                                else self.source_dir / SOURCE_MANIFEST_NAME if not (self.source_dir / '.git').exists()
                                else None)
        self.source_provenance = verify_source(self.source_dir, source_manifest)
        if not self.checkpoint.is_file() or _sha256(self.checkpoint) != CHECKPOINT_SHA256:
            raise ValueError('The real pretrained DINOv2 ViT-B/14 checkpoint failed SHA256 verification.')
        # Python caches imported packages. Reject a previously imported DINOv2
        # implementation from another tree instead of silently executing it.
        for name, module in list(sys.modules.items()):
            if name == 'dinov2' or name.startswith('dinov2.'):
                filename = getattr(module, '__file__', None)
                if filename is not None and not Path(filename).resolve().is_relative_to(self.source_dir):
                    raise ValueError('A different DINOv2 source tree is already imported; use a fresh Python process.')
        torch.set_num_threads(threads)
        torch.manual_seed(0)
        torch.use_deterministic_algorithms(True)
        self.model = torch.hub.load(str(self.source_dir), 'dinov2_vitb14', source='local', pretrained=False)
        state = torch.load(self.checkpoint, map_location='cpu', weights_only=True)
        self.model.load_state_dict(state, strict=True)
        self.model.to('cpu').eval().requires_grad_(False)
        if self.model.embed_dim != 768 or self.model.patch_size != 14:
            raise ValueError('Loaded backbone is not the required official DINOv2 ViT-B/14.')
        self.cache_root.mkdir(parents=True, exist_ok=True)
        self._metadata = dict(backbone='dinov2_vitb14', checkpoint_sha256=CHECKPOINT_SHA256,
                              **self.source_provenance, resolution=resolution, layers=list(self.layers),
                              preprocessing_version=PREPROCESS_VERSION,
                              aggregation='raw-mean-of-declared-zero-based-blocks; norm=False',
                              spatial_transform='RGB square resize; no crop or padding',
                              device='cpu', dtype='float32', cpu_threads=threads,
                              deterministic_algorithms=True, torch_version=str(torch.__version__),
                              numpy_version=np.__version__, pillow_version=pillow_version,
                              python_version=platform.python_version(), machine=platform.machine(),
                              pretrained_weights_loaded=True,
                              implementation_sha256=_sha256(Path(__file__)))

    def metadata(self) -> dict:
        result = json.loads(_canonical(self._metadata))
        result.update(frozen=not any(p.requires_grad for p in self.model.parameters()),
                      evaluation_mode=not self.model.training,
                      runtime_config=dict(source_dir=str(self.source_dir), checkpoint=str(self.checkpoint),
                                          cache_root=str(self.cache_root), resolution=self.resolution,
                                          layers=list(self.layers), threads=self.threads,
                                          source_manifest=str(self.source_manifest) if self.source_manifest is not None else None))
        return result

    def extract(self, image: Path, use_cache=True) -> DenseFeatures:
        if self.model.training or any(p.requires_grad for p in self.model.parameters()):
            raise RuntimeError('The pretrained feature extractor must stay frozen in evaluation mode.')
        image = Path(image)
        raw = image.read_bytes()
        with Image.open(io.BytesIO(raw)) as pil_image:
            original_size = pil_image.size
            # Physical installation/cache paths are reusable startup settings,
            # not feature semantics; identical verified files can be relocated.
            metadata = dict(self._metadata, frozen=True, evaluation_mode=True,
                            image_sha256=hashlib.sha256(raw).hexdigest(),
                            original_size=list(original_size))
            key = feature_cache_key(metadata)
            target = self.cache_root / (key + '.npz')
            if use_cache and target.is_file():
                return _read_cache(target, metadata, self.resolution, original_size)
            x = preprocess_rgb(pil_image, self.resolution)
        with torch.inference_mode():
            outputs = self.model.get_intermediate_layers(x, n=self.layers, norm=False)
            tokens = torch.stack([t[0] for t in outputs]).mean(dim=0).cpu().float().contiguous()
        _validate_tokens(tokens.numpy(), self.resolution)
        geometry = dict(grid=(self.resolution // 14,) * 2, original_size=original_size,
                        resized_size=(self.resolution,) * 2, padded_size=(self.resolution,) * 2)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(dir=self.cache_root, prefix=key + '.', suffix='.npz', delete=False) as handle:
                temporary = Path(handle.name)
                np.savez(handle, tokens=tokens.numpy(), metadata=np.array(_canonical(metadata)),
                         **{name: np.array(value, dtype=np.int64) for name, value in geometry.items()})
            os.replace(temporary, target)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
        return DenseFeatures(tokens, **geometry, mode='subspacead', key=key, cache_hit=False)


def prepare_encoder(destination) -> dict:
    """Download pinned official source and checksum-verified weights once."""
    destination = Path(destination).expanduser().resolve()
    destination.mkdir(parents=True, exist_ok=True)
    source = destination / 'dinov2-source'
    checkpoint = destination / 'dinov2_vitb14_pretrain.pth'
    if not source.exists():
        temporary = Path(tempfile.mkdtemp(prefix='.dinov2-source-', dir=destination))
        try:
            for args in [('init', str(temporary)), ('-C', str(temporary), 'fetch', '--depth', '1', SOURCE_URL, SOURCE_PIN),
                         ('-C', str(temporary), 'checkout', '--detach', 'FETCH_HEAD')]:
                subprocess.run(['git', *args], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            verify_source(temporary)
            os.replace(temporary, source)
        finally:
            if temporary.exists():
                shutil.rmtree(temporary)
    verify_source(source)
    manifest = export_source_manifest(source)
    if checkpoint.exists():
        if _sha256(checkpoint) != CHECKPOINT_SHA256:
            raise ValueError('Existing checkpoint checksum is invalid; supply a verified checkpoint.')
    else:
        temporary = None
        try:
            request = urllib.request.Request(CHECKPOINT_URL, headers={'User-Agent': 'SAFAL-verified-encoder/1.0'})
            with urllib.request.urlopen(request, timeout=60) as response:
                if urllib.parse.urlparse(response.url).scheme != 'https':
                    raise ValueError('Checkpoint download must remain on HTTPS.')
                with tempfile.NamedTemporaryFile(dir=destination, prefix='.checkpoint-', delete=False) as handle:
                    temporary = Path(handle.name)
                    shutil.copyfileobj(response, handle, length=1024 * 1024)
            if _sha256(temporary) != CHECKPOINT_SHA256:
                raise ValueError('Downloaded pretrained checkpoint failed SHA256 verification.')
            os.replace(temporary, checkpoint)
        finally:
            if temporary is not None and temporary.exists():
                temporary.unlink()
    return dict(source_dir=str(source), checkpoint=str(checkpoint), source_manifest=str(manifest),
                source_commit=SOURCE_PIN, checkpoint_sha256=CHECKPOINT_SHA256)


def main():
    parser = argparse.ArgumentParser(description='Prepare the real verified frozen SAFAL encoder; no datasets are downloaded.')
    parser.add_argument('command', choices=['prepare'])
    parser.add_argument('--destination', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(prepare_encoder(args.destination), indent=2))


if __name__ == '__main__':
    main()
