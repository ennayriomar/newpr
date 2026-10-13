"""Synthetic geometry/budget/cache tests, not real-dataset performance evidence."""
import copy
import unittest

import numpy as np
import torch

from safe_iad.patch_nn import cache_key, patch_nearest_neighbor, restore_map, validate_episode
from safe_iad.verify_dataset import Sample


class SyntheticPatchNNTests(unittest.TestCase):
    def test_synthetic_normalized_euclidean_distance(self):
        query = torch.tensor([[7., 0.], [0., 4.]])
        memory = torch.tensor([[2., 0.]])
        actual = patch_nearest_neighbor(query, memory)
        np.testing.assert_allclose(actual.numpy(), [0., np.sqrt(2)], atol=1e-6)

    def test_synthetic_grid_restoration_preserves_corners_and_size(self):
        actual = restore_map(torch.tensor([0., 1., 2., 3.]), (2, 2), (8, 6))
        self.assertEqual(actual.shape, (6, 8))
        self.assertAlmostEqual(float(actual[0, 0]), 0., places=6)
        self.assertAlmostEqual(float(actual[-1, -1]), 3., places=6)

    def test_synthetic_invalid_grid_rejected(self):
        with self.assertRaises(ValueError):
            restore_map(torch.zeros(3), (2, 2), (8, 6))

    def test_synthetic_support_query_overlap_rejected(self):
        support = Sample('cat', 'train', 'normal', 'same.png', None)
        query = Sample('cat', 'test', 'normal', 'same.png', None)
        with self.assertRaisesRegex(ValueError, 'overlap'):
            validate_episode([support], [query], 1)

    def test_synthetic_fixed_shot_budget_rejected(self):
        support = Sample('cat', 'train', 'normal', 'support.png', None)
        query = Sample('cat', 'test', 'normal', 'query.png', None)
        with self.assertRaisesRegex(ValueError, 'budget'):
            validate_episode([support], [query], 2)

    def test_synthetic_cache_invalidates_provenance_changes(self):
        metadata = {'dataset': 'mvtec_ad', 'split': 'train', 'category': 'cat', 'image_id': '001.png', 'checkpoint_sha256': 'abc', 'preprocessing_version': 'v1', 'layer_configuration': 'last'}
        original = cache_key(metadata)
        for field in ['dataset', 'split', 'category', 'image_id', 'checkpoint_sha256', 'preprocessing_version', 'layer_configuration']:
            changed = copy.deepcopy(metadata)
            changed[field] += '-changed'
            self.assertNotEqual(cache_key(changed), original, field)


if __name__ == '__main__':
    unittest.main()
