"""SAFAL: normal-calibrated search/PCA evidence with operational coverage diagnostics.

Coverage measures query compatibility with declared normal-cutoff scales. It
conflates actual defects and legitimate appearances absent from support; it is
not correctness probability, calibrated support trust, or an identified cause.
The bounded weighted fusion is an unverified heuristic and can suppress a
branch alert. Raw branches and the evidence-preserving maximum remain exposed.
"""
from __future__ import annotations

from dataclasses import asdict
import hashlib
import io
import json
import math
from pathlib import Path

import numpy as np
import torch

from .subspace_search import BranchCalibration, SubspaceSearch, _features, fuse, image_top1


def _ids(values, expected, description):
    if isinstance(values, (str, bytes)):
        raise ValueError(f'{description} must be a sequence of distinct image IDs.')
    try:
        ids = tuple(values)
    except TypeError as exc:
        raise ValueError(f'{description} must be a sequence of distinct image IDs.') from exc
    if len(ids) != expected or any(not isinstance(value, str) or not value.strip() for value in ids):
        raise ValueError(f'{description} must contain one nonempty ID per image.')
    if len(set(ids)) != len(ids):
        raise ValueError(f'{description} image IDs must be distinct.')
    return ids


def _feature_hash(features):
    array = features.detach().to(dtype=torch.float64).cpu().numpy().astype('<f8', copy=False)
    digest = hashlib.sha256()
    digest.update(json.dumps(list(array.shape), separators=(',', ':')).encode())
    digest.update(array.tobytes())
    return digest.hexdigest()


def _implementation_hashes():
    root = Path(__file__).parent
    return {name: hashlib.sha256((root/name).read_bytes()).hexdigest()
            for name in ['safal_model.py', 'subspace_search.py']}


def _checkpoint_paths(prefix):
    prefix = Path(prefix)
    if prefix.suffix in {'.json', '.npz'}:
        prefix = prefix.with_suffix('')
    return Path(str(prefix)+'.json'), Path(str(prefix)+'.npz')


def _write_preserving(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f'Refusing to overwrite a different SAFAL checkpoint: {path}')
    else:
        path.write_bytes(data)


class SAFALModel:
    """Frozen normal support search/PCA with separate normal image/pixel cutoffs.

    Each support image contributes its own patch tensor. Reference-image LOO
    removes a complete image, never just a token. External pretrained backbone
    provenance belongs to the caller and can be recorded in ``save``.
    """

    def __init__(self, support_images, support_ids, explained_variance=.99, chunk=256):
        images = tuple(support_images)
        if not images:
            raise ValueError('At least one normal support image is required.')
        self.support_ids = _ids(support_ids, len(images), 'Support')
        validated = []
        for image in images:
            if not isinstance(image, torch.Tensor) or image.ndim != 2 or image.shape[0] < 2:
                raise ValueError('Each support image needs a 2D tensor with at least two patch tokens.')
            # Reuse base validation without fitting redundant per-image PCAs.
            validated.append(_features(image, 'support image', minimum_rows=2).clone())
        if len({(image.shape[1], image.device) for image in validated}) != 1:
            raise ValueError('Support images must share feature dimensions and device.')
        self.support_images = tuple(validated)
        self.explained_variance = float(explained_variance)
        self.chunk = chunk
        self.base = SubspaceSearch(torch.cat(self.support_images), explained_variance=explained_variance, chunk=chunk)
        self.loo_models = tuple(
            SubspaceSearch(torch.cat([image for index, image in enumerate(self.support_images) if index != omitted]),
                           explained_variance=explained_variance, chunk=chunk)
            for omitted in range(len(images))
        ) if len(images) > 1 else ()
        self.calibration = None
        self.calibration_metadata = None
        self.checkpoint_provenance = {}

    def calibrate(self, normal_queries, ids, quantile=.95):
        """Fit four separate empirical normal quantiles; labels are not accepted.

        Pixel quantiles pool normal calibration tokens; tokens are correlated,
        not independent images. Source support/calibration IDs must be disjoint.
        Zero cutoffs are rejected without an epsilon or alternate denominator.
        """
        queries = tuple(normal_queries)
        if not queries:
            raise ValueError('Nonempty declared-normal calibration queries are required.')
        calibration_ids = _ids(ids, len(queries), 'Calibration')
        if set(calibration_ids) & set(self.support_ids):
            raise ValueError('Calibration and support image IDs must be disjoint.')
        if isinstance(quantile, bool):
            raise ValueError('Calibration quantile must lie in (0, 1].')
        try:
            quantile = float(quantile)
        except (TypeError, ValueError) as exc:
            raise ValueError('Calibration quantile must lie in (0, 1].') from exc
        if not math.isfinite(quantile) or not 0 < quantile <= 1:
            raise ValueError('Calibration quantile must lie in (0, 1].')
        raw = [self.base.predict_raw(query) for query in queries]
        cutoffs = {}
        for branch in ['search', 'subspace']:
            images = torch.tensor([entry['image_'+branch] for entry in raw], dtype=torch.float64)
            pixels = torch.cat([entry[branch].cpu() for entry in raw])
            cutoffs['image_'+branch] = float(torch.quantile(images, quantile, interpolation='linear'))
            cutoffs['pixel_'+branch] = float(torch.quantile(pixels, quantile, interpolation='linear'))
        self.calibration = BranchCalibration(**cutoffs, calibration_ids=calibration_ids)
        self.calibration_metadata = {
            'procedure': 'separate empirical normal image and pooled-token quantiles, linear interpolation',
            'quantile': quantile,
            'calibration_ids': list(calibration_ids),
            'calibration_feature_sha256': {identifier: _feature_hash(query)
                                           for identifier, query in zip(calibration_ids, queries)},
            'extra_normal_calibration_images': len(calibration_ids),
            'support_calibration_overlap': 0,
            'caller_declared_normal': True,
            'query_labels_accepted': False,
            'independent_calibration_units': 'images; pooled pixel tokens remain dependent',
            'domain_semantics': 'Caller-declared normal calibration domain; image IDs and feature hashes '
                                'must be bound to actual dataset splits by the runner.',
            'probability_calibration': False,
        }
        return self.calibration

    def _calibration(self, calibration):
        calibration = self.calibration if calibration is None else calibration
        if not isinstance(calibration, BranchCalibration):
            raise ValueError('Fit normal calibration or pass a validated BranchCalibration before prediction.')
        if set(calibration.calibration_ids) & set(self.support_ids):
            raise ValueError('Calibration and support image IDs must be disjoint.')
        return calibration

    def predict(self, query, calibration=None):
        """Infer without labels; all maps retain the input patch-token ordering."""
        calibration = self._calibration(calibration)
        raw = self.base.predict_raw(query)
        normalized = fuse(raw, calibration)
        search, subspace = normalized['normalized_search'], normalized['normalized_subspace']
        search_coverage, subspace_coverage = 1/(1+search), 1/(1+subspace)
        adequacy = .5*(search_coverage+subspace_coverage)
        search_weight = (.9-.8*adequacy).clamp(.1, .9)
        subspace_weight = 1-search_weight
        total = search+subspace
        disagreement = (search-subspace).abs()/torch.where(total > 0, total, torch.ones_like(total))
        uncertainty = (.5*disagreement+.5*(1-adequacy)).clamp(0, 1)
        maps = {
            'search': search,
            'subspace': subspace,
            'fixed_avg': .5*(search+subspace),
            'max': normalized['hybrid'],
            'safal': search_weight*search+subspace_weight*subspace,
        }
        image_scores = {
            'search': normalized['image_search'],
            'subspace': normalized['image_subspace'],
            'fixed_avg': .5*(normalized['image_search']+normalized['image_subspace']),
            'max': normalized['image_hybrid'],
            'safal': image_top1(search_weight*(raw['search']/calibration.image_search)
                               +subspace_weight*(raw['subspace']/calibration.image_subspace)),
        }
        valid = torch.full_like(search, bool(self.loo_models), dtype=torch.bool)
        if self.loo_models:
            leave_out = [model.predict_raw(query) for model in self.loo_models]
            per_image = {branch: torch.stack([(prediction[branch]-raw[branch]).abs()
                                             for prediction in leave_out])
                         for branch in ['search', 'subspace']}
            loo = {branch: values.max(dim=0).values for branch, values in per_image.items()}
            loo.update(per_image_search=per_image['search'], per_image_subspace=per_image['subspace'])
        else:
            loo = {'search': None, 'subspace': None, 'per_image_search': None, 'per_image_subspace': None}
        loo.update(valid=valid, per_image_valid=[bool(self.loo_models)]*len(self.support_ids),
                   support_ids=self.support_ids, missing_reason=None if self.loo_models else
                   'Image leave-one-out is undefined at k=1; no zero-stability imputation.')
        metadata = {
            'support_ids': list(self.support_ids), 'initial_support_images': len(self.support_ids),
            'additional_selected_references': 0, 'extra_normal_calibration_images': len(calibration.calibration_ids),
            'calibration_ids': list(calibration.calibration_ids),
            'mean_search_weight': float(search_weight.mean()), 'mean_subspace_weight': float(subspace_weight.mean()),
            'image_and_pixel_decision_threshold': 1.,
            'coverage_semantics': 'Query-relative compatibility with normal cutoff scales; defects and '
                                  'missing legitimate support appearances can both lower it.',
            'weighted_fusion_semantics': 'Unverified bounded heuristic favoring search under low coverage; '
                                         'may suppress branch alerts and must be evaluated for missed defects.',
            'probabilities': False,
            'valid_fields': {'raw_search': True, 'raw_subspace': True, 'patch_adequacy': True,
                             'patch_uncertainty': True, 'scalar_A': True, 'scalar_U': True,
                             'image_leave_one_out': bool(self.loo_models), 'probabilities': False},
        }
        return {'raw': {'search': raw['search'], 'subspace': raw['subspace']},
                'raw_image_scores': {'search': raw['image_search'], 'subspace': raw['image_subspace']},
                'maps': maps, 'A': float(adequacy.mean()), 'U': float(uncertainty.mean()),
                'patch_adequacy': adequacy, 'patch_uncertainty': uncertainty,
                'coverage': {'search': search_coverage, 'subspace': subspace_coverage},
                'weights': {'search': search_weight, 'subspace': subspace_weight},
                'branch_disagreement': float(disagreement.mean()), 'patch_branch_disagreement': disagreement,
                'loo': loo, 'image_scores': image_scores,
                'image_alerts': {name: score >= 1 for name, score in image_scores.items()}, 'metadata': metadata}

    def metadata(self):
        return {
            'method': 'SAFAL empirical normal-coverage-weighted search/PCA prototype',
            'base': self.base.metadata(),
            'support_ids': list(self.support_ids), 'support_images': len(self.support_ids),
            'feature_dimension': self.base.raw_memory.shape[1],
            'support_tokens_per_image': [image.shape[0] for image in self.support_images],
            'support_feature_sha256': {identifier: _feature_hash(image)
                                      for identifier, image in zip(self.support_ids, self.support_images)},
            'explained_variance': self.explained_variance, 'chunk': self.chunk,
            'calibration': asdict(self.calibration) if self.calibration else None,
            'calibration_metadata': self.calibration_metadata,
            'extra_normal_calibration_images': len(self.calibration.calibration_ids) if self.calibration else 0,
            'image_leave_one_out_valid': bool(self.loo_models),
            'coverage': 'C_search=1/(1+search/pixel_search_cutoff); C_pca=1/(1+subspace/pixel_subspace_cutoff); '
                        'A=(C_search+C_pca)/2. Compatibility diagnostic, not correctness probability.',
            'weights': 'w_search=clip(0.9-0.8*A,0.1,0.9); w_pca=1-w_search; heuristic direction unverified',
            'uncertainty': 'U=(abs(normalized_search-normalized_pca)/(normalized_search+normalized_pca) '
                           '+1-A)/2; zero disagreement when both branches zero; diagnostic only',
            'image_aggregation': 'branch raw patch top1% divided by image cutoffs; avg/max combine those '
                                 'image branches; safal aggregates patch-weighted image-scaled raw branches',
            'pixel_aggregation': 'calibrated pixel branches combined in the original patch grid; runner restores maps',
            'decision_threshold': 1., 'probabilities': False,
            'implementation_sha256': _implementation_hashes(),
            'checkpoint_provenance': self.checkpoint_provenance,
        }

    def save(self, prefix, provenance=None):
        """Save raw support tensors and declared cutoffs without Python/Torch pickle."""
        json_path, npz_path = _checkpoint_paths(prefix)
        if provenance is not None:
            # Require JSON-serializable finite metadata; never serialize secret env state.
            self.checkpoint_provenance = json.loads(json.dumps(provenance, allow_nan=False))
        arrays = {f'support_{index:03d}': image.cpu().numpy() for index, image in enumerate(self.support_images)}
        buffer = io.BytesIO()
        np.savez_compressed(buffer, **arrays)
        npz_bytes = buffer.getvalue()
        document = {
            'schema_version': 1, 'kind': 'SAFALModel', 'support_ids': list(self.support_ids),
            'support_array_keys': list(arrays), 'explained_variance': self.explained_variance, 'chunk': self.chunk,
            'calibration': asdict(self.calibration) if self.calibration else None,
            'calibration_metadata': self.calibration_metadata,
            'support_feature_sha256': self.metadata()['support_feature_sha256'],
            'implementation_sha256': _implementation_hashes(),
            'npz_sha256': hashlib.sha256(npz_bytes).hexdigest(), 'provenance': self.checkpoint_provenance,
        }
        json_bytes = (json.dumps(document, indent=2, allow_nan=False)+'\n').encode()
        _write_preserving(npz_path, npz_bytes)
        _write_preserving(json_path, json_bytes)
        return {'json': str(json_path), 'npz': str(npz_path)}

    @classmethod
    def load(cls, prefix):
        """Verify artifact/source hashes and reconstruct the frozen model on CPU."""
        json_path, npz_path = _checkpoint_paths(prefix)
        document = json.loads(json_path.read_text())
        if document.get('schema_version') != 1 or document.get('kind') != 'SAFALModel':
            raise ValueError('Unsupported SAFAL checkpoint schema.')
        if document['implementation_sha256'] != _implementation_hashes():
            raise ValueError('SAFAL checkpoint implementation provenance changed.')
        if hashlib.sha256(npz_path.read_bytes()).hexdigest() != document['npz_sha256']:
            raise ValueError('SAFAL checkpoint NPZ checksum mismatch.')
        with np.load(npz_path, allow_pickle=False) as archive:
            if set(archive.files) != set(document['support_array_keys']):
                raise ValueError('SAFAL checkpoint support-array schema mismatch.')
            images = [torch.from_numpy(archive[key].copy()) for key in document['support_array_keys']]
        model = cls(images, document['support_ids'], document['explained_variance'], document['chunk'])
        if model.metadata()['support_feature_sha256'] != document['support_feature_sha256']:
            raise ValueError('SAFAL checkpoint support feature provenance mismatch.')
        if document['calibration'] is not None:
            model.calibration = model._calibration(BranchCalibration(**document['calibration']))
        model.calibration_metadata = document['calibration_metadata']
        model.checkpoint_provenance = document['provenance']
        return model
