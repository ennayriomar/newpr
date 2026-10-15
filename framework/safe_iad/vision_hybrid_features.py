"""Independent register-DINO extraction for the inspected VisionAD recipe.

Only Meta's licensed pinned source is executed. No VisionAD source is imported
or distributed. Recipe constants are attributed to its pinned class-separated
implementation; the paper has inconsistent default/layer descriptions.
"""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import platform
import sys
import urllib.request

import numpy as np
from PIL import Image, __version__ as pillow_version
import torch
import torch.nn.functional as F

from .safal_features import verify_source, SOURCE_PIN, _sha256

WEIGHT_URL = 'https://dl.fbaipublicfiles.com/dinov2/dinov2_vitl14/dinov2_vitl14_reg4_pretrain.pth'
WEIGHT_SHA256 = '36e4deffbaef061a2576705b0c36f93621e2ae20bf6274694821b0b492551b51'
WEIGHT_BYTES = 1217607321
REFERENCE_PIN = '2d5e36f357409125ccd9646ba016824005599df4'
SLOTS = ('identity', 'vflip', 'clamp')
VIEWS = ('identity', 'rot90', 'rot180', 'rot270', 'vflip', 'hflip')


def preprocess(image, resize=448, crop=392):
    if type(resize) is not int or type(crop) is not int or resize < crop or crop < 14 or crop % 14:
        raise ValueError('Positive integer resize>=crop and patch-aligned crop are required.')
    image = image.convert('RGB').resize((resize, resize), Image.Resampling.BILINEAR)
    offset = (resize-crop)//2
    array = np.asarray(image.crop((offset, offset, offset+crop, offset+crop)), dtype=np.float32)/255.
    tensor = torch.from_numpy(array.copy()).permute(2, 0, 1).unsqueeze(0)
    return (tensor-tensor.new_tensor([.485, .456, .406]).view(1, 3, 1, 1))/tensor.new_tensor([.229, .224, .225]).view(1, 3, 1, 1)


def transform(tensor, name):
    if name == 'identity': return tensor
    if name == 'vflip': return tensor.flip(-2)
    if name == 'hflip': return tensor.flip(-1)
    if name == 'clamp': return tensor.clamp_min(0)
    if name in ('rot90', 'rot180', 'rot270'):
        return tensor.rot90(int(name[3:])//90, (-2, -1))
    raise ValueError('Unknown fixed recipe view: '+str(name))


def support_inputs(tensor):
    """Deduplicate identical tensor inputs; retain all six views in each slot."""
    unique, index, slots = [], {}, {}
    for slot in SLOTS:
        slots[slot] = []
        for view in VIEWS:
            value = transform(transform(tensor, slot), view).contiguous()
            key = hashlib.sha256(value.numpy().tobytes()).hexdigest()
            if key not in index:
                index[key] = len(unique)
                unique.append(value)
            slots[slot].append(index[key])
    return unique, slots


def roi_mask(image, resize=448, crop=392, grid=256):
    """Nearest binary-mask geometry, declared numerical-wrapper deviation."""
    original = np.array(image.convert('L')) > 0
    offset = (resize-crop)//2
    pil = Image.fromarray(original.astype(np.uint8)*255).resize((resize, resize), Image.Resampling.NEAREST)
    roi = pil.crop((offset, offset, offset+crop, offset+crop))
    return np.array(roi.resize((grid, grid), Image.Resampling.NEAREST)) > 0


def metric_map(values, grid):
    value = torch.as_tensor(values, dtype=torch.float32).reshape(1, 1, grid, grid)
    return F.interpolate(value, (256, 256), mode='bilinear', align_corners=False)[0, 0].numpy()


def image_score(score_map):
    values = torch.as_tensor(score_map).flatten()
    if not torch.isfinite(values).all() or not len(values):
        raise ValueError('A finite nonempty map is required.')
    return float(values.topk(max(1, int(.01*len(values)))).values.mean())


class RegisterEncoder:
    def __init__(self, source_dir, checkpoint, *, device='cpu', threads=3,
                 resize=448, crop=392, layers=tuple(range(4, 19)), source_manifest=None):
        if type(threads) is not int or threads < 1:
            raise ValueError('Positive CPU thread count required.')
        layers = tuple(layers)
        if not layers or sorted(set(layers)) != list(layers) or any(type(i) is not int or i < 0 or i > 23 for i in layers):
            raise ValueError('Distinct increasing zero-based ViT-L blocks in [0,23] required.')
        preprocess(Image.new('RGB', (1, 1)), resize, crop)
        if device not in ('cpu', 'cuda') or (device == 'cuda' and not torch.cuda.is_available()):
            raise ValueError('Requested device is unavailable; no silent CPU/model fallback.')
        self.source = Path(source_dir).resolve()
        self.checkpoint = Path(checkpoint).resolve()
        self.source_provenance = verify_source(self.source, source_manifest)
        if not self.checkpoint.is_file() or _sha256(self.checkpoint) != WEIGHT_SHA256:
            raise ValueError('Official register ViT-L checkpoint SHA256 mismatch.')
        for name, module in list(sys.modules.items()):
            if name == 'dinov2' or name.startswith('dinov2.'):
                filename = getattr(module, '__file__', None)
                if filename and not Path(filename).resolve().is_relative_to(self.source):
                    raise ValueError('Another DINO source tree is imported; use a new process.')
        torch.set_num_threads(threads)
        torch.manual_seed(0)
        torch.use_deterministic_algorithms(True)
        if device == 'cuda':
            os.environ.setdefault('CUBLAS_WORKSPACE_CONFIG', ':4096:8')
            torch.backends.cuda.matmul.allow_tf32 = False
        self.model = torch.hub.load(str(self.source), 'dinov2_vitl14_reg', source='local', pretrained=False)
        state = torch.load(self.checkpoint, map_location='cpu', weights_only=True, mmap=True)
        self.model.load_state_dict(state, strict=True, assign=True)
        del state
        # These are the inspected VisionAD encoder's position-interpolation
        # settings. Meta's register hub defaults are antialias=True, offset=0.
        self.model.interpolate_antialias = False
        self.model.interpolate_offset = .1
        self.model.to(device).eval().requires_grad_(False)
        if (self.model.embed_dim, self.model.patch_size, self.model.num_register_tokens) != (1024, 14, 4):
            raise ValueError('Wrong backbone architecture.')
        self.device, self.resize, self.crop, self.layers = device, resize, crop, layers
        self.grid = crop//14

    def metadata(self):
        return dict(backbone='dinov2_vitl14_reg', feature_dimension=1024,
                    registers=4, resize=self.resize, crop=self.crop, grid=self.grid,
                    layers=list(self.layers), norm=False, aggregation='raw arithmetic block mean, then branch-specific normalization',
                    interpolation='PIL bilinear square resize, center crop',
                    position_interpolation=dict(antialias=False, offset=.1),
                    checkpoint_sha256=WEIGHT_SHA256, reference_commit=REFERENCE_PIN,
                    source_commit=SOURCE_PIN, source_manifest_sha256=self.source_provenance['source_manifest_sha256'],
                    device=self.device, dtype='float32', frozen=True, evaluation_mode=True,
                    torch_version=str(torch.__version__), numpy_version=np.__version__,
                    pillow_version=pillow_version, python_version=platform.python_version(),
                    implementation_sha256=_sha256(Path(__file__)),
                    runtime=dict(source_dir=str(self.source), checkpoint=str(self.checkpoint), threads=torch.get_num_threads()))

    def extract_tensor(self, tensor):
        if tensor.shape != (1, 3, self.crop, self.crop) or not torch.isfinite(tensor).all():
            raise ValueError('A single finite normalized image with trained geometry is required.')
        if self.model.training or any(p.requires_grad for p in self.model.parameters()):
            raise ValueError('Encoder must remain frozen/eval.')
        with torch.inference_mode():
            value = self.model.prepare_tokens_with_masks(tensor.to(self.device))
            selected = []
            for i, block in enumerate(self.model.blocks):
                if i > self.layers[-1]: break
                value = block(value)
                if i in self.layers: selected.append(value)
            raw = torch.stack(selected, dim=1).mean(dim=1)[0, 5:].float().cpu().contiguous()
        if raw.shape != (self.grid*self.grid, 1024) or not torch.isfinite(raw).all():
            raise ValueError('Invalid pretrained patch descriptors.')
        return raw

    def support(self, image_path):
        with Image.open(image_path) as image:
            tensor = preprocess(image, self.resize, self.crop)
        inputs, slots = support_inputs(tensor)
        features = [self.extract_tensor(x) for x in inputs]
        return features, slots

    def query(self, image_path):
        with Image.open(image_path) as image:
            tensor = preprocess(image, self.resize, self.crop)
        return {slot: self.extract_tensor(transform(tensor, slot)) for slot in SLOTS}


def prepare(destination):
    """Pinned, streaming official checkpoint download; TLS and SHA enforced."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if _sha256(destination) != WEIGHT_SHA256: raise ValueError('Existing weight checksum mismatch.')
        return destination
    partial = destination.with_suffix(destination.suffix+'.partial')
    if partial.exists(): raise ValueError('Partial download exists; preserve it and choose another destination.')
    h = hashlib.sha256(); count = 0
    try:
        with urllib.request.urlopen(WEIGHT_URL, timeout=60) as response, partial.open('xb') as out:
            if not response.url.startswith('https://dl.fbaipublicfiles.com/'):
                raise ValueError('Unexpected official weight origin.')
            while data := response.read(1024*1024):
                h.update(data); count += len(data); out.write(data)
        if count != WEIGHT_BYTES or h.hexdigest() != WEIGHT_SHA256:
            raise ValueError('Downloaded weight length/SHA256 mismatch.')
        os.replace(partial, destination)
    except Exception:
        if partial.exists(): partial.unlink()
        raise
    return destination
