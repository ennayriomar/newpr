"""Empirical support diagnostic and evidence-preserving subspace/NN hybrid.

Entropy is a diagnostic of observed spectral diversity, not adequacy truth or a
probability. Orthogonal residuals cannot identify defect versus missing normals.
"""
from dataclasses import dataclass
import math

import torch
import torch.nn.functional as F


def distances(query, memory, chunk=256):
    query, memory = F.normalize(query.float(), dim=1), F.normalize(memory.float(), dim=1)
    for start in range(0, len(query), chunk):
        yield (2 - 2 * query[start:start+chunk] @ memory.T).clamp_min(0).sqrt()


@dataclass(frozen=True)
class DecisionThresholds:
    image_defect: float
    pixel_defect: float
    adequacy: float
    calibration_ids: tuple

    def __post_init__(self):
        if not all(math.isfinite(v) for v in (self.image_defect, self.pixel_defect, self.adequacy)):
            raise ValueError('Decision thresholds must be finite.')
        if not 0 <= self.adequacy <= 1 or not self.calibration_ids:
            raise ValueError('Adequacy threshold and calibration provenance are required.')


def decide(image_score, mean_adequacy, thresholds):
    if not math.isfinite(image_score) or not 0 <= mean_adequacy <= 1:
        raise ValueError('Invalid decision input.')
    # Low support always triggers review, even if raw evidence is high; retain
    # the evidence flag and map for that review. Never relabel it as normal.
    evidence = image_score >= thresholds.image_defect
    if mean_adequacy < thresholds.adequacy:
        return 'unresolved/reference-insufficient', evidence
    return ('defective' if evidence else 'normal'), evidence


class SupportHybrid:
    def __init__(self, memory, explained_variance=.99, density_neighbors=8, density_quantile=.95):
        if memory.ndim != 2 or len(memory) < 2 or not torch.isfinite(memory).all():
            raise ValueError('Finite normal-support patch descriptors required.')
        if not 0 < explained_variance < 1 or not 0 < density_quantile < 1 or density_neighbors < 1:
            raise ValueError('Invalid PCA/density settings.')
        self.memory = F.normalize(memory.float(), dim=1)
        self.mean = self.memory.mean(dim=0)
        centered = self.memory - self.mean
        # Exact dual PCA avoids a feature_dim^2 covariance for concatenated layers.
        gram = centered.double() @ centered.double().T / (len(memory)-1)
        eigenvalues, u = torch.linalg.eigh(gram)
        eigenvalues, u = eigenvalues.flip(0).clamp_min(0), u.flip(1)
        positive = eigenvalues > max(float(eigenvalues[0]) * 1e-10, 1e-14)
        spectrum = eigenvalues[positive]
        if len(spectrum):
            p = spectrum / spectrum.sum()
            self.spectral_entropy = float(-(p * p.log()).sum())
            self.normalized_entropy = self.spectral_entropy / math.log(len(p)) if len(p) > 1 else 0.
            rank = min(len(spectrum), int(torch.searchsorted(p.cumsum(0), torch.tensor(explained_variance, dtype=p.dtype)))+1)
            vectors = centered.double().T @ u[:, :rank] / torch.sqrt(eigenvalues[:rank] * (len(memory)-1))
            self.components = vectors.float()
            self.retained_variance = float(p[:rank].sum())
        else:
            self.components = centered.new_zeros((centered.shape[1], 0))
            self.spectral_entropy = self.normalized_entropy = self.retained_variance = 0.
        self.eigenvalues = spectrum.float()
        self.neighbors = min(density_neighbors, len(memory)-1)
        density = []
        for start, d in zip(range(0, len(memory), 256), distances(self.memory, self.memory)):
            ids = torch.arange(len(d))
            d[ids, ids+start] = torch.inf  # exclude self, retain other support patches
            density.append(d.topk(self.neighbors, largest=False).values.mean(dim=1))
        self.density_bound = max(float(torch.quantile(torch.cat(density), density_quantile)), 1e-6)

    def predict(self, query):
        q = F.normalize(query.float(), dim=1)
        local, density, indices = [], [], []
        for d in distances(q, self.memory):
            nearest, idx = d.min(dim=1)
            local.append(nearest); indices.append(idx)
            density.append(d.topk(self.neighbors, largest=False).values.mean(dim=1))
        local, density = torch.cat(local), torch.cat(density)
        centered = q - self.mean
        residual = centered - (centered @ self.components) @ self.components.T
        global_map = residual.norm(dim=1)
        delta = q - self.memory[torch.cat(indices)]
        orthogonal = (delta - (delta @ self.components) @ self.components.T).norm(dim=1)
        # Evidence envelope: low adequacy can never lower local anomaly evidence.
        defect = torch.maximum(local, torch.maximum(global_map, orthogonal))
        adequacy = (self.normalized_entropy * torch.exp(-(density / self.density_bound - 1).clamp_min(0))).clamp(0, 1)
        return dict(defect=defect, local=local, global_residual=global_map, orthogonal_residual=orthogonal, adequacy=adequacy, local_density=density)

    def metadata(self):
        return dict(pca_components=self.components.shape[1], retained_variance=self.retained_variance,
                    spectral_entropy=self.spectral_entropy, normalized_entropy=self.normalized_entropy,
                    density_bound=self.density_bound, density_neighbors=self.neighbors,
                    adequacy_semantics='empirical spectral-diversity/density diagnostic; not probability',
                    gating='max(local_L2, global_orthogonal_L2, nearest_delta_orthogonal_L2)',
                    support_patch_dependence='patches are correlated; token count is not independent-image sample size')
