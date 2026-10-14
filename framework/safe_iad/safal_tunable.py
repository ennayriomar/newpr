"""Independent tunable SAFAL prototype; all legacy checkpoint sources stay frozen.

One raw-support SVD supplies the declared variance grid. Normal-only branch
calibration is separate from selecting fusion/decision settings on permitted
development data. Coverage/uncertainty are diagnostics, not probabilities.
Geometry and map smoothing belong to the runner, not this scoring module.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
import torch

from .subspace_search import BranchCalibration, _features, _scores, image_top1


def _number(value, name, lower, upper=None, *, lower_closed=False):
    if isinstance(value, bool):
        raise ValueError(f'{name} must be a finite number in its declared range.')
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f'{name} must be a finite number in its declared range.') from exc
    if not math.isfinite(value) or (value < lower if lower_closed else value <= lower) or (upper is not None and value > upper):
        raise ValueError(f'{name} must be a finite number in its declared range.')
    return value


@dataclass(frozen=True, slots=True)
class Parameters:
    explained_variance: float = .99
    normal_quantile: float = .95
    aggregation: str = 'top1'
    fusion: str = 'adaptive_original'
    search_weight: float = .5
    image_threshold: float = 1.

    def __post_init__(self):
        for name, lower, upper, closed in [('explained_variance', 0., 1., False),
                                           ('normal_quantile', 0., 1., False),
                                           ('search_weight', 0., 1., True),
                                           ('image_threshold', 0., None, False)]:
            object.__setattr__(self, name, _number(getattr(self, name), name, lower, upper,
                                                 lower_closed=closed))
        if self.aggregation not in {'top1', 'max'}:
            raise ValueError('aggregation must be top1 or max.')
        if self.fusion not in {'adaptive_original', 'adaptive_reversed', 'fixed', 'max'}:
            raise ValueError('Unknown declared fusion setting.')

    @property
    def id(self):
        data = json.dumps(asdict(self), sort_keys=True, separators=(',', ':'), allow_nan=False).encode()
        return hashlib.sha256(data).hexdigest()

    @property
    def identifier(self):
        return self.id


def _ids(values, expected, name):
    if isinstance(values, (str, bytes)):
        raise ValueError(f'{name} must be a sequence of image IDs.')
    try:
        values = tuple(values)
    except TypeError as exc:
        raise ValueError(f'{name} must be a sequence of image IDs.') from exc
    if len(values) != expected or any(not isinstance(value, str) or not value.strip() for value in values):
        raise ValueError(f'{name} must contain one nonempty image ID per tensor.')
    if len(set(values)) != len(values):
        raise ValueError(f'{name} image IDs must be unique.')
    return values


def _array_hash(values):
    array = values.detach().to(dtype=torch.float64).cpu().numpy().astype('<f8', copy=False)
    digest = hashlib.sha256(json.dumps(list(array.shape), separators=(',', ':')).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def _implementation_hashes():
    root = Path(__file__).parent
    return {name: hashlib.sha256((root/name).read_bytes()).hexdigest()
            for name in ['safal_tunable.py', 'subspace_search.py']}


def _aggregate(values, aggregation):
    values = _scores(values, 'image aggregation')
    return image_top1(values) if aggregation == 'top1' else float(values.max())


def _pixel_ratio(values, cutoff):
    ratio = values/cutoff
    one = torch.ones((), dtype=ratio.dtype, device=ratio.device)
    below = torch.nextafter(one, torch.full_like(one, -math.inf))
    ratio = torch.where((values < cutoff) & (ratio >= 1), below, ratio)
    ratio = torch.where((values >= cutoff) & (ratio < 1), one, ratio)
    if not torch.isfinite(ratio).all():
        raise ValueError('Branch calibration produced a nonfinite normalized map.')
    return ratio


def _image_ratio(value, cutoff):
    ratio = value/cutoff
    if not math.isfinite(ratio):
        raise ValueError('Branch calibration produced a nonfinite normalized image score.')
    if value < cutoff and ratio >= 1:
        ratio = math.nextafter(1., -math.inf)
    elif value >= cutoff and ratio < 1:
        ratio = 1.
    return ratio


class TunableSubspaceSearch:
    """Raw support PCA grid and cosine search; no labels enter any score fit."""

    def __init__(self, support_images, support_ids, variances=(.90, .95, .99, .995), chunk=256):
        images = tuple(support_images)
        if not images:
            raise ValueError('At least one normal support image is required.')
        self.support_ids = _ids(support_ids, len(images), 'Support')
        self.support_images = tuple(_features(image, 'support image', minimum_rows=2).clone() for image in images)
        if len({(image.shape[1], image.device) for image in self.support_images}) != 1:
            raise ValueError('Support images must have matching dimensions and devices.')
        if isinstance(chunk, bool) or not isinstance(chunk, int) or chunk <= 0:
            raise ValueError('chunk must be a positive integer.')
        self.chunk = chunk
        self.variances = tuple(_number(value, 'variance grid value', 0., 1.) for value in variances)
        if not self.variances or len(set(self.variances)) != len(self.variances):
            raise ValueError('The variance grid must be nonempty and unique.')
        self.memory = torch.cat(self.support_images)
        self.mean = self.memory.mean(0)
        self.normalized_memory = self.memory/torch.linalg.vector_norm(self.memory, dim=1, keepdim=True)
        centered = self.memory-self.mean
        if not torch.isfinite(centered).all():
            raise ValueError('Raw support centering produced nonfinite values.')
        with torch.no_grad():
            _, singular, vectors = torch.linalg.svd(centered, full_matrices=False)
        if not torch.isfinite(singular).all() or not torch.isfinite(vectors).all():
            raise ValueError('Raw support SVD produced nonfinite values.')
        tolerance = float(singular.max())*max(centered.shape)*torch.finfo(torch.float64).eps
        self.numerical_rank = int((singular > tolerance).sum())
        self.vectors = vectors.clone()
        self.retained_ranks = {}
        self.retained_variance = {}
        if self.numerical_rank:
            energies = singular[:self.numerical_rank].square()
            if not torch.isfinite(energies).all() or not torch.isfinite(energies.sum()):
                raise ValueError('Support variance is outside finite float64 range.')
            cumulative = energies.cumsum(0)/energies.sum()
            for variance in self.variances:
                requested = torch.tensor(variance, dtype=cumulative.dtype, device=cumulative.device)
                rank = min(self.numerical_rank, int(torch.searchsorted(cumulative, requested))+1)
                self.retained_ranks[str(variance)] = rank
                self.retained_variance[str(variance)] = float(cumulative[rank-1])
        else:
            self.retained_ranks = {str(variance): 0 for variance in self.variances}
            self.retained_variance = {str(variance): None for variance in self.variances}
        self.params = None
        self.calibration = None
        self.calibration_metadata = None
        self.checkpoint_provenance = {}
        self._calibration_records = {}

    def _params(self, params):
        if not isinstance(params, Parameters):
            raise ValueError('A validated Parameters object is required.')
        if str(params.explained_variance) not in self.retained_ranks:
            raise ValueError('Parameters select a variance absent from the fitted support grid.')
        return params

    def score_raw(self, query):
        """Return one search vector and a raw squared-residual vector per variance."""
        query = _features(query, 'query')
        if query.shape[1] != self.memory.shape[1] or query.device != self.memory.device:
            raise ValueError('Query/support feature dimensions and devices must match.')
        searches, residuals = [], {key: [] for key in self.retained_ranks}
        with torch.no_grad():
            for raw in query.split(self.chunk):
                unit = raw/torch.linalg.vector_norm(raw, dim=1, keepdim=True)
                searches.append((1-(unit@self.normalized_memory.T).max(1).values).clamp_min(0))
                centered = raw-self.mean
                for key, rank in self.retained_ranks.items():
                    components = self.vectors[:rank]
                    reconstructed = (centered@components.T)@components
                    residuals[key].append((centered-reconstructed).square().sum(1))
        return {'search': _scores(torch.cat(searches), 'search'),
                'subspace': {key: _scores(torch.cat(values), 'subspace') for key, values in residuals.items()}}

    def _rawpair(self, raw, params):
        self._params(params)
        try:
            search = _scores(raw['search'], 'search')
            subspace = _scores(raw['subspace'][str(params.explained_variance)], 'subspace')
        except (KeyError, TypeError) as exc:
            raise ValueError('Raw search and selected-variance subspace fields are required.') from exc
        if search.shape != subspace.shape or search.device != subspace.device:
            raise ValueError('Raw branch token shapes and devices must match.')
        return {'search': search, 'subspace': subspace}

    def calibration_from_raw(self, normal_raws, ids, params):
        """Use caller-declared normal queries only; no defect-label argument exists."""
        self._params(params)
        normal_raws = tuple(normal_raws)
        if not normal_raws:
            raise ValueError('Nonempty declared-normal calibration data are required.')
        ids = _ids(ids, len(normal_raws), 'Calibration')
        if set(ids) & set(self.support_ids):
            raise ValueError('Support/calibration image IDs must be disjoint.')
        pairs = [self._rawpair(raw, params) for raw in normal_raws]
        thresholds = {}
        for branch in ['search', 'subspace']:
            images = torch.tensor([_aggregate(pair[branch], params.aggregation) for pair in pairs], dtype=torch.float64)
            pixels = torch.cat([pair[branch].cpu() for pair in pairs])
            thresholds['image_'+branch] = float(torch.quantile(images, params.normal_quantile, interpolation='linear'))
            thresholds['pixel_'+branch] = float(torch.quantile(pixels, params.normal_quantile, interpolation='linear'))
        calibration = BranchCalibration(**thresholds, calibration_ids=ids)
        self._calibration_records[params.id] = {
            'parameters_id': params.id, 'calibration_ids': list(ids),
            'normal_quantile': params.normal_quantile, 'aggregation': params.aggregation,
            'explained_variance': params.explained_variance,
            'raw_normal_score_sha256': {identifier: {branch: _array_hash(pair[branch]) for branch in pair}
                                        for identifier, pair in zip(ids, pairs)},
            'procedure': 'Separate branch-image and pooled-raw-token normal quantiles; linear interpolation',
            'extra_normal_calibration_images': len(ids), 'support_overlap': 0,
            'caller_declared_normal': True, 'query_labels_accepted': False,
            'probability_calibration': False,
            'domain_semantics': 'Caller must bind normal score vectors to dataset/image roles; '
                                'pooled patch observations are correlated.',
        }
        return calibration

    def predict_from_raw(self, raw, params, calibration):
        pair = self._rawpair(raw, params)
        if not isinstance(calibration, BranchCalibration):
            raise ValueError('A validated BranchCalibration is required.')
        if set(calibration.calibration_ids) & set(self.support_ids):
            raise ValueError('Support/calibration image IDs must be disjoint.')
        search = _pixel_ratio(pair['search'], calibration.pixel_search)
        subspace = _pixel_ratio(pair['subspace'], calibration.pixel_subspace)
        adequacy = .5*(1/(1+search)+1/(1+subspace))
        total = search+subspace
        disagreement = (search-subspace).abs()/torch.where(total > 0, total, torch.ones_like(total))
        uncertainty = (.5*disagreement+.5*(1-adequacy)).clamp(0, 1)
        images = {branch: _image_ratio(_aggregate(pair[branch], params.aggregation), getattr(calibration, 'image_'+branch))
                  for branch in ['search', 'subspace']}
        if params.fusion == 'fixed':
            weight = torch.full_like(search, params.search_weight)
            image_score = params.search_weight*images['search']+(1-params.search_weight)*images['subspace']
        elif params.fusion == 'max':
            weight = torch.where(search > subspace, torch.ones_like(search),
                                 torch.where(search < subspace, torch.zeros_like(search), torch.full_like(search, .5)))
            image_score = max(images.values())
        else:
            weight = (.9-.8*adequacy if params.fusion == 'adaptive_original' else .1+.8*adequacy).clamp(.1, .9)
            image_score = _aggregate(weight*(pair['search']/calibration.image_search)
                                     +(1-weight)*(pair['subspace']/calibration.image_subspace), params.aggregation)
        score_map = torch.maximum(search, subspace) if params.fusion == 'max' else weight*search+(1-weight)*subspace
        if not torch.isfinite(score_map).all() or not math.isfinite(image_score):
            raise ValueError('Fusion produced nonfinite evidence.')
        return {
            'image_score': image_score, 'image_scores_branch': images, 'image_alert': image_score >= params.image_threshold,
            'image_threshold': params.image_threshold, 'pixel_threshold': 1.,
            'map': score_map, 'weights': {'search': weight, 'subspace': 1-weight},
            'patch_adequacy': adequacy, 'patch_uncertainty': uncertainty,
            'A': float(adequacy.mean()), 'U': float(uncertainty.mean()),
            'branch_disagreement': float(disagreement.mean()), 'rawpair': pair,
            'normalized_branches': {'search': search, 'subspace': subspace},
            'parameters_id': params.id,
            'valid_fields': {'raw_branches': True, 'patch_adequacy': True, 'patch_uncertainty': True,
                             'calibrated_probabilities': False, 'image_leave_one_out': False},
        }

    def metadata(self):
        return {
            'method': 'Independent tunable SAFAL raw PCA/cosine hybrid; no unlicensed VisionAD code',
            'support_ids': list(self.support_ids), 'support_images': len(self.support_images),
            'support_tokens': self.memory.shape[0], 'support_tokens_per_image': [image.shape[0] for image in self.support_images],
            'feature_dimension': self.memory.shape[1], 'arithmetic_dtype': 'torch.float64', 'device': str(self.memory.device),
            'support_feature_sha256': {identifier: _array_hash(image) for identifier, image in zip(self.support_ids, self.support_images)},
            'variances': list(self.variances), 'retained_ranks': self.retained_ranks,
            'retained_variance': self.retained_variance, 'numerical_rank': self.numerical_rank,
            'support_svd_fits': 1, 'chunk': self.chunk,
            'pca_math': 'Raw centered-support SVD; squared orthogonal reconstruction residual using each retained prefix',
            'search_math': 'max(0, 1-max cosine similarity) of separately unit-normalized query/support tokens',
            'coverage_math': 'A=mean(1/(1+search/pixel_cutoff),1/(1+subspace/pixel_cutoff)); '
                             'defects and absent legitimate support modes can both lower it',
            'adaptive_weights': 'original=clip(.9-.8*A,.1,.9); reversed=clip(.1+.8*A,.1,.9); both unverified heuristics',
            'fixed_weight': 'search_weight only applies to fixed fusion; endpoints are branch controls',
            'image_aggregation': 'top1 means floor top1% (minimum1 token); max means highest token; '
                                 'adaptive aggregates patch-weighted image-scaled branches, fixed combines aggregated branches',
            'geometry_and_smoothing': 'External runner; this module preserves token order',
            'probabilities': False, 'params': asdict(self.params) if self.params else None,
            'calibration': asdict(self.calibration) if self.calibration else None,
            'calibration_metadata': self.calibration_metadata,
            'implementation_sha256': _implementation_hashes(), 'checkpoint_provenance': self.checkpoint_provenance,
        }

    def save(self, prefix, params, calibration, provenance=None):
        self._params(params)
        if not isinstance(calibration, BranchCalibration) or set(calibration.calibration_ids) & set(self.support_ids):
            raise ValueError('Validated disjoint normal calibration is required to save a model.')
        self.params, self.calibration = params, calibration
        self.calibration_metadata = self._calibration_records.get(params.id)
        self.checkpoint_provenance = json.loads(json.dumps(provenance or {}, allow_nan=False))
        prefix = Path(prefix)
        if prefix.suffix in {'.json', '.npz'}:
            prefix = prefix.with_suffix('')
        json_path, npz_path = Path(str(prefix)+'.json'), Path(str(prefix)+'.npz')
        arrays = {f'support_{index:03d}': image.cpu().numpy() for index, image in enumerate(self.support_images)}
        buffer = io.BytesIO()
        np.savez_compressed(buffer, **arrays)
        npz_bytes = buffer.getvalue()
        document = {
            'schema_version': 1, 'kind': 'TunableSubspaceSearch', 'support_ids': list(self.support_ids),
            'support_array_keys': list(arrays), 'variances': list(self.variances), 'chunk': self.chunk,
            'params': asdict(params), 'parameters_id': params.id, 'calibration': asdict(calibration),
            'calibration_metadata': self.calibration_metadata, 'provenance': self.checkpoint_provenance,
            'support_feature_sha256': self.metadata()['support_feature_sha256'],
            'implementation_sha256': _implementation_hashes(), 'npz_sha256': hashlib.sha256(npz_bytes).hexdigest(),
        }
        payloads = [(npz_path, npz_bytes), (json_path, (json.dumps(document, indent=2, allow_nan=False)+'\n').encode())]
        for path, data in payloads:
            path.parent.mkdir(parents=True, exist_ok=True)
            if path.exists() and path.read_bytes() != data:
                raise ValueError(f'Refusing to overwrite a different tuned checkpoint: {path}')
            if not path.exists():
                path.write_bytes(data)
        return {'json': str(json_path), 'npz': str(npz_path)}

    @classmethod
    def load(cls, prefix):
        prefix = Path(prefix)
        if prefix.suffix in {'.json', '.npz'}:
            prefix = prefix.with_suffix('')
        json_path, npz_path = Path(str(prefix)+'.json'), Path(str(prefix)+'.npz')
        document = json.loads(json_path.read_text())
        if document.get('schema_version') != 1 or document.get('kind') != 'TunableSubspaceSearch':
            raise ValueError('Unsupported tuned checkpoint schema.')
        if document['implementation_sha256'] != _implementation_hashes():
            raise ValueError('Tuned checkpoint implementation source changed.')
        if hashlib.sha256(npz_path.read_bytes()).hexdigest() != document['npz_sha256']:
            raise ValueError('Tuned checkpoint NPZ checksum mismatch.')
        with np.load(npz_path, allow_pickle=False) as archive:
            if set(archive.files) != set(document['support_array_keys']):
                raise ValueError('Tuned checkpoint support schema mismatch.')
            images = [torch.from_numpy(archive[key].copy()) for key in document['support_array_keys']]
        model = cls(images, document['support_ids'], tuple(document['variances']), document['chunk'])
        if model.metadata()['support_feature_sha256'] != document['support_feature_sha256']:
            raise ValueError('Tuned checkpoint support features changed.')
        model.params = model._params(Parameters(**document['params']))
        if model.params.id != document['parameters_id']:
            raise ValueError('Tuned checkpoint parameter fingerprint mismatch.')
        model.calibration = BranchCalibration(**document['calibration'])
        if set(model.calibration.calibration_ids) & set(model.support_ids):
            raise ValueError('Saved support/calibration IDs overlap.')
        model.calibration_metadata = document['calibration_metadata']
        model.checkpoint_provenance = document['provenance']
        return model
