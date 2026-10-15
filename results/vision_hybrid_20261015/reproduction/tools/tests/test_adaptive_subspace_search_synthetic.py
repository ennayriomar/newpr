"""Synthetic support-scale math tests; no accuracy or transfer evidence."""
import json
import unittest

import numpy as np
import torch

from safe_iad.adaptive_subspace_search import SupportScaledSearch
from safe_iad.subspace_search import SubspaceSearch, image_top1


class SyntheticSupportScaledSearchTests(unittest.TestCase):
    def data(self):
        rng = np.random.default_rng(29)
        memory = rng.normal(size=(32, 4)) * np.asarray([3., .4, .08, .02]) + np.asarray([2., -1., .5, 3.])
        query = rng.normal(size=(7, 4)) + np.asarray([2., -1., .5, 3.])
        return torch.tensor(memory), torch.tensor(query)

    def test_synthetic_common_amplitude_scales_raw_pca_but_not_normalized_evidence(self):
        memory, query = self.data()
        amplitude = 7.3
        original = SupportScaledSearch(memory)
        scaled = SupportScaledSearch(memory * amplitude)
        raw = SubspaceSearch(memory).predict_raw(query)
        raw_scaled = SubspaceSearch(memory * amplitude).predict_raw(query * amplitude)
        torch.testing.assert_close(raw_scaled['subspace'], raw['subspace'] * amplitude ** 2,
                                   rtol=1e-10, atol=1e-10)
        self.assertAlmostEqual(scaled.subspace_scale / original.subspace_scale, amplitude ** 2, places=9)
        before = original.predict_raw(query)
        after = scaled.predict_raw(query * amplitude)
        torch.testing.assert_close(after['search'], before['search'], rtol=1e-10, atol=1e-10)
        torch.testing.assert_close(after['subspace'], before['subspace'], rtol=1e-10, atol=1e-10)

    def test_synthetic_cosine_scale_matches_independent_nonself_reference(self):
        memory, _ = self.data()
        model = SupportScaledSearch(memory, chunk=5)
        values = memory.numpy()
        unit = values / np.linalg.norm(values, axis=1, keepdims=True)
        distance = np.maximum(0, 1-unit @ unit.T)
        np.fill_diagonal(distance, np.inf)
        mean_eight = np.sort(distance, axis=1)[:, :8].mean(axis=1)
        expected = np.quantile(mean_eight, .95, method='linear')
        self.assertAlmostEqual(model.search_scale, expected, places=12)
        independent_raw = SubspaceSearch(memory).predict_raw(memory)
        self.assertAlmostEqual(model.subspace_scale, float(independent_raw['subspace'].mean()), places=12)

    def test_synthetic_predictions_match_branch_scaling_and_repeat_across_chunks(self):
        memory, query = self.data()
        first = SupportScaledSearch(memory, chunk=3)
        second = SupportScaledSearch(memory, chunk=256)
        original = first.base.predict_raw(query)
        prediction = first.predict_raw(query)
        repeat = second.predict_raw(query)
        torch.testing.assert_close(prediction['search'], original['search'] / first.search_scale)
        torch.testing.assert_close(prediction['subspace'], original['subspace'] / first.subspace_scale)
        for branch in ['search', 'subspace']:
            torch.testing.assert_close(prediction[branch], repeat[branch], rtol=1e-11, atol=1e-11)
            self.assertEqual(prediction['image_' + branch], image_top1(prediction[branch]))
        metadata = first.metadata()
        self.assertEqual(metadata['scaling']['additional_fitting_images'], 0)
        self.assertFalse(metadata['scaling']['independent_image_leave_one_out'])
        self.assertIn('same-image patches remain eligible', metadata['scaling']['self_exclusion'])
        self.assertIn('does not guarantee', metadata['limitation'])
        json.dumps(metadata, allow_nan=False)

    def test_synthetic_degenerate_and_insufficient_support_rejected_without_fallback(self):
        with self.assertRaisesRegex(ValueError, 'variance tail'):
            SupportScaledSearch(torch.ones(12, 4))
        memory, _ = self.data()
        with self.assertRaisesRegex(ValueError, 'at least 9'):
            SupportScaledSearch(memory[:8])
        with self.assertRaisesRegex(ValueError, 'variance tail'):
            SupportScaledSearch(memory, explained_variance=1.)
        # Different raw amplitudes with one shared direction have zero search
        # geometry; retaining only part of their scalar variance cannot invent it.
        directions = torch.arange(1, 13, dtype=torch.float64).reshape(-1, 1).repeat(1, 3)
        with self.assertRaises(ValueError):
            SupportScaledSearch(directions)

    def test_synthetic_wrapper_rejects_invalid_query_and_owns_support_snapshot(self):
        memory, query = self.data()
        model = SupportScaledSearch(memory)
        before = model.predict_raw(query)
        memory.fill_(9.)
        after = model.predict_raw(query)
        torch.testing.assert_close(before['search'], after['search'])
        torch.testing.assert_close(before['subspace'], after['subspace'])
        for invalid in [torch.zeros(3, 4), torch.ones(3, 5), torch.full((3, 4), float('nan'))]:
            with self.subTest(shape=invalid.shape), self.assertRaises(ValueError):
                model.predict_raw(invalid)


if __name__ == '__main__':
    unittest.main()
