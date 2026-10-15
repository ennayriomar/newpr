"""Raw support PCA plus normalized patch search, with separate calibrated scales.

This is an independently implemented SubspaceAD-inspired scoring combination,
not a reproduction of a published recipe. No VisionAD repository code is used.
The hybrid is the union of branch alerts after normal-only cutoff scaling; it
does not estimate calibrated probabilities or guarantee inspection reliability.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import math

import torch


def _features(value, name, *, minimum_rows=1):
    if not isinstance(value, torch.Tensor) or value.ndim != 2:
        raise ValueError(f'{name} must be a 2D torch feature tensor.')
    if not value.is_floating_point() or value.is_complex():
        raise ValueError(f'{name} must contain real floating-point features.')
    if value.shape[0] < minimum_rows or value.shape[1] < 1:
        raise ValueError(f'{name} must contain at least {minimum_rows} nonempty feature rows.')
    if not torch.isfinite(value).all():
        raise ValueError(f'{name} features must be finite.')
    value = value.detach().to(dtype=torch.float64)
    norms = torch.linalg.vector_norm(value, dim=1)
    if not torch.isfinite(norms).all() or (norms <= 0).any():
        raise ValueError(f'{name} features require finite nonzero norms for cosine search.')
    return value


def _scores(value, name):
    if not isinstance(value, torch.Tensor) or value.ndim != 1 or not value.numel():
        raise ValueError(f'{name} must be a nonempty 1D torch score tensor.')
    if not value.is_floating_point() or not torch.isfinite(value).all():
        raise ValueError(f'{name} scores must be finite floating-point values.')
    if (value < 0).any():
        raise ValueError(f'{name} scores must be nonnegative.')
    return value.detach().to(dtype=torch.float64)


def image_top1(scores):
    """Mean of the largest max(1, floor(0.01 * tokens)) raw token scores."""
    scores = _scores(scores, 'image aggregation')
    count = max(1, scores.numel() // 100)
    result = float(torch.topk(scores, count, sorted=False).values.mean())
    if not math.isfinite(result):
        raise ValueError('Image aggregation produced a nonfinite score.')
    return result


class SubspaceSearch:
    """Fit centered RAW-feature PCA and an independent normalized search bank.

    Parameters stay on the supplied memory device. Query tensors must use that
    device; no implicit CPU/GPU fallback occurs. PCA and search arithmetic use
    float64. Raw feature magnitudes are retained by PCA, including its centroid.
    """

    def __init__(self, memory, explained_variance=.99, chunk=256):
        raw = _features(memory, 'memory', minimum_rows=2)
        if isinstance(explained_variance, bool):
            raise ValueError('explained_variance must lie in (0, 1].')
        try:
            explained_variance = float(explained_variance)
        except (TypeError, ValueError) as exc:
            raise ValueError('explained_variance must lie in (0, 1].') from exc
        if not math.isfinite(explained_variance) or not 0 < explained_variance <= 1:
            raise ValueError('explained_variance must lie in (0, 1].')
        if isinstance(chunk, bool) or not isinstance(chunk, int) or chunk < 1:
            raise ValueError('chunk must be a positive integer.')
        self.raw_memory = raw.clone()
        self.input_dtype = str(memory.dtype)
        self.explained_variance = explained_variance
        self.chunk = chunk
        self.mean = self.raw_memory.mean(dim=0)
        self.normalized_memory = self.raw_memory / torch.linalg.vector_norm(self.raw_memory, dim=1, keepdim=True)
        centered = self.raw_memory - self.mean
        if not torch.isfinite(centered).all():
            raise ValueError('Raw support centering produced nonfinite values.')
        with torch.no_grad():
            _, singular, vectors = torch.linalg.svd(centered, full_matrices=False)
        if not torch.isfinite(singular).all() or not torch.isfinite(vectors).all():
            raise ValueError('Raw support PCA produced nonfinite values.')
        tolerance = float(singular.max()) * max(centered.shape) * torch.finfo(torch.float64).eps
        self.numerical_rank = int((singular > tolerance).sum())
        if self.numerical_rank:
            energies = singular[:self.numerical_rank].square()
            if not torch.isfinite(energies).all() or not torch.isfinite(energies.sum()):
                raise ValueError('Raw support PCA variance exceeds finite float64 range.')
            cumulative = energies.cumsum(0) / energies.sum()
            requested = torch.tensor(explained_variance, dtype=cumulative.dtype, device=cumulative.device)
            retained = min(self.numerical_rank, int(torch.searchsorted(cumulative, requested)) + 1)
            self.components = vectors[:retained].clone()
            self.retained_variance = float(cumulative[retained - 1])
        else:
            self.components = vectors[:0].clone()
            self.retained_variance = None

    def predict_raw(self, query):
        """Return raw search/PCA token evidence and separately aggregated images."""
        query = _features(query, 'query')
        if query.shape[1] != self.raw_memory.shape[1]:
            raise ValueError('Query and support feature dimensions must match.')
        if query.device != self.raw_memory.device:
            raise ValueError('Query and support must share a device; no implicit device fallback.')
        search_chunks, subspace_chunks = [], []
        with torch.no_grad():
            for raw in query.split(self.chunk):
                unit = raw / torch.linalg.vector_norm(raw, dim=1, keepdim=True)
                search = (1 - (unit @ self.normalized_memory.T).max(dim=1).values).clamp_min(0)
                centered = raw - self.mean
                reconstructed = (centered @ self.components.T) @ self.components
                subspace = (centered - reconstructed).square().sum(dim=1)
                search_chunks.append(search)
                subspace_chunks.append(subspace)
        search = _scores(torch.cat(search_chunks), 'search')
        subspace = _scores(torch.cat(subspace_chunks), 'subspace')
        return {'search': search, 'subspace': subspace,
                'image_search': image_top1(search), 'image_subspace': image_top1(subspace)}

    def metadata(self):
        raw_hash = hashlib.sha256(self.raw_memory.cpu().numpy().astype('<f8', copy=False).tobytes()).hexdigest()
        return {
            'method': 'independent SubspaceAD-inspired raw PCA plus normalized patch search',
            'published_recipe_reproduced': False,
            'visionad_repository_code_used': False,
            'support_tokens': self.raw_memory.shape[0],
            'feature_dimension': self.raw_memory.shape[1],
            'raw_support_features_sha256': raw_hash,
            'input_dtype': self.input_dtype,
            'arithmetic_dtype': 'torch.float64',
            'device': str(self.raw_memory.device),
            'query_chunk_size': self.chunk,
            'pca': {
                'fit': 'SVD of raw support features centered by their raw support mean',
                'feature_normalization_before_pca': False,
                'requested_explained_variance': self.explained_variance,
                'retained_explained_variance': self.retained_variance,
                'numerical_rank': self.numerical_rank,
                'retained_components': self.components.shape[0],
                'rank_tolerance': 'max(singular value) * max(tokens, dimensions) * float64 epsilon',
                'constant_support_case': 'zero-dimensional PCA; squared distance to raw support mean',
                'score': 'sum_j ((q-mu) - ((q-mu) V^T) V)_j^2',
            },
            'search': {'normalization': 'unit L2 norm for query/support patch descriptors only',
                       'score': 'max(0, min_s (1 - normalized_q dot normalized_s))'},
            'image_aggregation': 'mean largest max(1, floor(0.01 * query_tokens)) branch token scores',
            'fusion': 'separate calibrated image/pixel cutoff scaling; elementwise/branch maximum',
            'calibration_fit': 'external, separate from support PCA/search and final evaluation',
            'claims': 'Branch-alert union after scaling; no probability or reliability guarantee.',
        }


@dataclass(frozen=True, slots=True)
class BranchCalibration:
    image_search: float
    image_subspace: float
    pixel_search: float
    pixel_subspace: float
    calibration_ids: tuple[str, ...]

    def __post_init__(self):
        for name in ['image_search', 'image_subspace', 'pixel_search', 'pixel_subspace']:
            value = getattr(self, name)
            if isinstance(value, bool):
                raise ValueError(f'{name} cutoff must be finite and strictly positive.')
            try:
                value = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError(f'{name} cutoff must be finite and strictly positive.') from exc
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f'{name} cutoff must be finite and strictly positive; no epsilon fallback.')
            object.__setattr__(self, name, value)
        if isinstance(self.calibration_ids, (str, bytes)):
            raise ValueError('Nonempty calibration image-ID provenance is required.')
        try:
            ids = tuple(self.calibration_ids)
        except TypeError as exc:
            raise ValueError('Nonempty calibration image-ID provenance is required.') from exc
        if not ids or any(not isinstance(identifier, str) or not identifier.strip() for identifier in ids):
            raise ValueError('Nonempty calibration image-ID provenance is required.')
        if len(set(ids)) != len(ids):
            raise ValueError('Calibration image IDs must be unique.')
        object.__setattr__(self, 'calibration_ids', ids)


def _normalized_image(raw, cutoff):
    normalized = raw / cutoff
    if not math.isfinite(normalized):
        raise ValueError('Calibration scaling produced a nonfinite image score.')
    # IEEE division can round a value just below its cutoff to 1. Preserve the
    # exact raw >= cutoff decision at this single representational boundary.
    if raw < cutoff and normalized >= 1:
        normalized = math.nextafter(1., -math.inf)
    elif raw >= cutoff and normalized < 1:
        normalized = 1.
    return normalized


def _normalized_pixels(raw, cutoff):
    normalized = raw / cutoff
    one = torch.ones((), dtype=normalized.dtype, device=normalized.device)
    below_one = torch.nextafter(one, torch.full_like(one, -math.inf))
    normalized = torch.where((raw < cutoff) & (normalized >= 1), below_one, normalized)
    normalized = torch.where((raw >= cutoff) & (normalized < 1), one, normalized)
    return normalized


def fuse(rawfields, calibration, *, image_scores=None):
    """Return maximum scaled evidence with exact branch-image alert union.

    Image evidence aggregates each raw branch independently before its image
    cutoff division. It is deliberately separate from aggregating the fused
    pixel map, whose branches use their distinct pixel cutoffs.

    When pixel fields have already been restored to native resolution, pass
    ``image_scores=(raw_patch_image_search, raw_patch_image_subspace)`` to keep
    the original patch aggregation. Without it, each supplied branch field is
    aggregated by ``image_top1``. Existing dictionary image fields are not used
    implicitly, so a changed score vector cannot inherit stale image evidence.
    """
    if not isinstance(calibration, BranchCalibration):
        raise ValueError('A validated BranchCalibration with provenance is required.')
    try:
        search, subspace = _scores(rawfields['search'], 'search'), _scores(rawfields['subspace'], 'subspace')
    except (KeyError, TypeError) as exc:
        raise ValueError('Raw search and subspace score fields are required.') from exc
    if search.shape != subspace.shape or search.device != subspace.device:
        raise ValueError('Raw branch fields must have identical token shapes and devices.')
    normalized_search = _normalized_pixels(search, calibration.pixel_search)
    normalized_subspace = _normalized_pixels(subspace, calibration.pixel_subspace)
    hybrid = torch.maximum(normalized_search, normalized_subspace)
    if not torch.isfinite(hybrid).all():
        raise ValueError('Calibration scaling produced a nonfinite pixel map.')
    if image_scores is None:
        image_search_raw, image_subspace_raw = image_top1(search), image_top1(subspace)
    else:
        if not isinstance(image_scores, (tuple, list)) or len(image_scores) != 2:
            raise ValueError('image_scores must contain exactly two finite nonnegative raw patch image scores.')
        values = []
        for value in image_scores:
            if isinstance(value, bool):
                raise ValueError('Explicit raw patch image scores must be finite nonnegative numbers.')
            try:
                value = float(value)
            except (TypeError, ValueError) as exc:
                raise ValueError('Explicit raw patch image scores must be finite nonnegative numbers.') from exc
            if not math.isfinite(value) or value < 0:
                raise ValueError('Explicit raw patch image scores must be finite nonnegative numbers.')
            values.append(value)
        image_search_raw, image_subspace_raw = values
    image_search = _normalized_image(image_search_raw, calibration.image_search)
    image_subspace = _normalized_image(image_subspace_raw, calibration.image_subspace)
    image_hybrid = max(image_search, image_subspace)
    search_alert = image_search_raw >= calibration.image_search
    subspace_alert = image_subspace_raw >= calibration.image_subspace
    hybrid_alert = image_hybrid >= 1
    if hybrid_alert != (search_alert or subspace_alert):
        raise RuntimeError('Hybrid image alert violated the branch-union invariant.')
    pixel_union = (search >= calibration.pixel_search) | (subspace >= calibration.pixel_subspace)
    if not torch.equal(hybrid >= 1, pixel_union):
        raise RuntimeError('Hybrid pixel alerts violated the branch-union invariant.')
    return {
        'normalized_search': normalized_search, 'normalized_subspace': normalized_subspace,
        'hybrid': hybrid, 'image_search': image_search, 'image_subspace': image_subspace,
        'image_hybrid': image_hybrid, 'search_alert': search_alert,
        'subspace_alert': subspace_alert, 'hybrid_alert': hybrid_alert,
    }
