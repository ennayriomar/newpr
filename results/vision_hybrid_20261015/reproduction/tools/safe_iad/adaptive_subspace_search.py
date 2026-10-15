"""Separate prototype: scale evidence by geometry of the current normal bank.

The raw PCA/search implementation is reused unchanged. Its two branches are
divided by different empirical normal-support scales before external normal
calibration. Neither scale estimates probabilities or guarantees transferred
normal-query calibration, accuracy, or defect preservation.
"""
from __future__ import annotations

import math

import torch

from .subspace_search import SubspaceSearch, image_top1


class SupportScaledSearch:
    """Bank-only scaling with the declared 8-neighbor/95%-quantile/99%-PCA defaults.

    Search geometry excludes only a token's own index. Other patches from its
    own image, and duplicate descriptors at other indices, remain eligible.
    Correlated patches are not independent image leave-one-out observations.
    """

    def __init__(self, memory, explained_variance=.99, chunk=256):
        self.base = SubspaceSearch(memory, explained_variance=explained_variance, chunk=chunk)
        if self.base.raw_memory.shape[0] < 9:
            raise ValueError('Support scaling requires at least 9 tokens for exactly 8 non-self neighbors.')
        retained = self.base.components.shape[0]
        if retained >= self.base.numerical_rank:
            raise ValueError('PCA support scale requires a positive unretained variance tail; '
                             'a full-rank or constant reconstruction has zero mathematical tail.')

        density_chunks = []
        unit_memory = self.base.normalized_memory
        with torch.no_grad():
            for start in range(0, len(unit_memory), chunk):
                stop = min(start + chunk, len(unit_memory))
                distances = (1 - unit_memory[start:stop] @ unit_memory.T).clamp_min(0)
                own_rows = torch.arange(stop - start, device=distances.device)
                own_columns = torch.arange(start, stop, device=distances.device)
                distances[own_rows, own_columns] = math.inf
                neighbors = distances.topk(8, dim=1, largest=False, sorted=False).values
                density_chunks.append(neighbors.mean(dim=1))
            support_density = torch.cat(density_chunks)
            self.search_scale = float(torch.quantile(support_density, .95, interpolation='linear'))
            raw_support = self.base.predict_raw(self.base.raw_memory)
            self.subspace_scale = float(raw_support['subspace'].mean())
        self.pca_scale = self.subspace_scale
        for name, value in [('search', self.search_scale), ('PCA', self.subspace_scale)]:
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f'{name} normal-support scale must be finite and strictly positive; '
                                 'degenerate support is rejected without epsilon or fallback.')

    def predict_raw(self, query):
        """Return bank-scaled branch tokens and their original patch aggregation."""
        original = self.base.predict_raw(query)
        search = original['search'] / self.search_scale
        subspace = original['subspace'] / self.subspace_scale
        # image_top1 verifies finite nonnegative scores, including scale overflow.
        return {'search': search, 'subspace': subspace,
                'image_search': image_top1(search), 'image_subspace': image_top1(subspace)}

    def metadata(self):
        return {
            'method': 'separate bank-scaled raw PCA plus cosine patch-search prototype',
            'base_method': self.base.metadata(),
            'search_scale': self.search_scale,
            'subspace_scale': self.subspace_scale,
            'scaling': {
                'search': '95th percentile (linear interpolation) of per-support-token mean '
                          '8-nearest cosine distances, excluding its own index',
                'subspace': 'mean raw squared PCA reconstruction residual over the same support tokens',
                'search_neighbors': 8,
                'search_quantile': .95,
                'query_search': 'raw cosine search evidence divided by positive support search scale',
                'query_subspace': 'raw squared PCA residual divided by positive support residual scale',
                'fit_data': 'current verified-normal support bank only; no query, candidate-pool, '
                            'external calibration or evaluation-label inputs',
                'additional_fitting_images': 0,
                'self_exclusion': 'same token index only; same-image patches remain eligible',
                'independent_image_leave_one_out': False,
                'degenerate_support': 'reject nonpositive/nonfinite scales or absent variance tail; '
                                      'no epsilon, clipped denominator or substitute scale',
                'computation': 'streamed chunk-by-support cosine matrices; no full token-by-token '
                               'distance matrix is retained',
            },
            'image_aggregation': 'mean largest max(1, floor(0.01 * query_tokens)) scaled branch scores',
            'external_calibration': 'fit separate source-normal image/pixel cutoffs after bank scaling',
            'limitation': 'Support residuals and correlated patch neighborhoods need not describe '
                          'held-out normal queries. Scaling does not guarantee calibrated '
                          'transfer, improved accuracy, or reliable inspection.',
        }
