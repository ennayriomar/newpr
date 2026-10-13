"""Synthetic math/union tests; performance improvement needs a real-data pilot."""
import json
import unittest

import numpy as np
from sklearn.decomposition import PCA
import torch

from safe_iad.subspace_search import BranchCalibration, SubspaceSearch, fuse, image_top1


class SyntheticSubspaceSearchTests(unittest.TestCase):
    def calibration(self, **changes):
        fields = dict(image_search=.5, image_subspace=2., pixel_search=.25,
                      pixel_subspace=4., calibration_ids=('calibration:normal-a', 'calibration:normal-b'))
        return BranchCalibration(**(fields | changes))

    def test_synthetic_raw_amplitude_defect_retained_by_pca_when_cosine_zero(self):
        memory = torch.tensor([[1., 0., 0.], [1., .2, 0.], [1., -.2, 0.]])
        raw = SubspaceSearch(memory).predict_raw(torch.tensor([[2., 0., 0.]]))
        self.assertAlmostEqual(raw['image_search'], 0., places=12)
        self.assertAlmostEqual(raw['image_subspace'], 1., places=12)
        fused = fuse(raw, self.calibration(image_subspace=.5))
        self.assertFalse(fused['search_alert'])
        self.assertTrue(fused['subspace_alert'] and fused['hybrid_alert'])

    def test_synthetic_raw_pca_matches_independent_sklearn_projector_and_residual(self):
        rng = np.random.default_rng(6)
        memory = rng.normal(size=(24, 6)) * np.asarray([5., 2., .5, .1, .05, .01]) + 3
        query = rng.normal(size=(11, 6)) + 2
        model = SubspaceSearch(torch.tensor(memory), explained_variance=.97, chunk=3)
        independent = PCA(n_components=.97, svd_solver='full').fit(memory)
        np.testing.assert_allclose(model.mean.numpy(), independent.mean_, atol=1e-12)
        np.testing.assert_allclose((model.components.T @ model.components).numpy(),
                                   independent.components_.T @ independent.components_, atol=1e-10)
        expected = np.square(query-independent.inverse_transform(independent.transform(query))).sum(axis=1)
        raw = model.predict_raw(torch.tensor(query))
        np.testing.assert_allclose(raw['subspace'].numpy(), expected, atol=1e-10)
        unit_q = query / np.linalg.norm(query, axis=1, keepdims=True)
        unit_m = memory / np.linalg.norm(memory, axis=1, keepdims=True)
        np.testing.assert_allclose(raw['search'].numpy(), np.maximum(0, 1-(unit_q @ unit_m.T).max(axis=1)), atol=1e-12)

    def test_synthetic_scaled_maps_preserve_each_branch_and_image_alert(self):
        raw = {'search': torch.tensor([.125, .5, .0]), 'subspace': torch.tensor([4., .5, 8.])}
        fused = fuse(raw, self.calibration())
        torch.testing.assert_close(fused['normalized_search'], torch.tensor([.5, 2., 0.], dtype=torch.float64))
        torch.testing.assert_close(fused['normalized_subspace'], torch.tensor([1., .125, 2.], dtype=torch.float64))
        self.assertTrue(torch.all(fused['hybrid'] >= fused['normalized_search']))
        self.assertTrue(torch.all(fused['hybrid'] >= fused['normalized_subspace']))
        self.assertTrue(fused['search_alert'] and fused['subspace_alert'] and fused['hybrid_alert'])
        self.assertEqual(fused['image_hybrid'], 4.)
        self.assertEqual(image_top1(fused['hybrid']), 2.)

    def test_synthetic_union_includes_ties_and_uses_separate_image_cutoffs(self):
        for search, subspace in [(.5, 0.), (0., 2.), (.5, 2.), (.25, 1.)]:
            raw = {'search': torch.tensor([search], dtype=torch.float64),
                   'subspace': torch.tensor([subspace], dtype=torch.float64)}
            fused = fuse(raw, self.calibration())
            self.assertEqual(fused['hybrid_alert'], search >= .5 or subspace >= 2.)
        fused = fuse({'search': torch.tensor([.4]), 'subspace': torch.tensor([1.])}, self.calibration())
        self.assertGreater(float(fused['hybrid'][0]), 1.)  # Pixel cutoff differs from image cutoff.
        self.assertFalse(fused['hybrid_alert'])

    def test_synthetic_native_pixel_fields_use_explicit_raw_patch_image_scores(self):
        native = {'search': torch.tensor([10., 9.]), 'subspace': torch.tensor([20., 19.])}
        fused = fuse(native, self.calibration(), image_scores=(.1, .2))
        self.assertFalse(fused['search_alert'] or fused['subspace_alert'] or fused['hybrid_alert'])
        self.assertAlmostEqual(fused['image_search'], .2)
        self.assertAlmostEqual(fused['image_subspace'], .1)
        self.assertTrue(torch.all(fused['hybrid'] >= 1))
        self.assertTrue(fuse(native, self.calibration())['hybrid_alert'])
        for invalid in [(), (.1,), (.1, .2, .3), '.1,.2', (-.1, .2),
                        (float('nan'), .2), (.1, float('inf')), (True, .2)]:
            with self.subTest(scores=invalid), self.assertRaises(ValueError):
                fuse(native, self.calibration(), image_scores=invalid)

    def test_synthetic_pixel_alert_union_is_preserved_at_ieee_boundaries(self):
        cutoff = np.nextafter(1., 2.)
        raw = torch.tensor([np.nextafter(cutoff, 0.), cutoff, np.nextafter(cutoff, np.inf)],
                           dtype=torch.float64)
        fused = fuse({'search': raw, 'subspace': torch.zeros_like(raw)},
                     self.calibration(pixel_search=cutoff))
        self.assertTrue(torch.equal(fused['hybrid'] >= 1, raw >= cutoff))
        self.assertFalse(bool(fused['normalized_search'][0] >= 1))
        self.assertTrue(bool(fused['normalized_search'][1] >= 1))

    def test_synthetic_image_aggregation_floors_fraction_and_chunks_do_not_change_scores(self):
        self.assertEqual(image_top1(torch.arange(199, dtype=torch.float64)), 198.)
        self.assertEqual(image_top1(torch.arange(200, dtype=torch.float64)), 198.5)
        memory = torch.tensor([[1., 0.], [1., .2], [1., -.2]])
        query = torch.tensor([[2., 0.], [1., .3], [1., .2]])
        first = SubspaceSearch(memory, chunk=1).predict_raw(query)
        second = SubspaceSearch(memory, chunk=256).predict_raw(query)
        for branch in ['search', 'subspace']:
            torch.testing.assert_close(first[branch], second[branch])

    def test_synthetic_constant_support_has_no_invented_components_and_keeps_raw_mean(self):
        memory = torch.tensor([[1., 0.], [1., 0.]])
        model = SubspaceSearch(memory)
        raw = model.predict_raw(torch.tensor([[2., 0.]]))
        self.assertEqual(model.metadata()['pca']['numerical_rank'], 0)
        self.assertEqual(model.metadata()['pca']['retained_components'], 0)
        self.assertEqual(raw['image_subspace'], 1.)
        json.dumps(model.metadata(), allow_nan=False)
        memory[0] = 10  # Fit stores an independent support snapshot.
        self.assertEqual(model.predict_raw(torch.tensor([[2., 0.]]))['image_subspace'], 1.)

    def test_synthetic_invalid_calibration_values_and_provenance_rejected(self):
        for field in ['image_search', 'image_subspace', 'pixel_search', 'pixel_subspace']:
            for value in [0., -1., float('nan'), float('inf'), True]:
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    self.calibration(**{field: value})
        for ids in [(), ('',), ('a', 'a'), 'single-string', None]:
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                self.calibration(calibration_ids=ids)

    def test_synthetic_invalid_features_parameters_and_fusion_rejected(self):
        invalid = [torch.tensor([1., 2.]), torch.ones(1, 2), torch.ones(2, 0),
                   torch.ones(2, 2, dtype=torch.int64), torch.zeros(2, 2),
                   torch.full((2, 2), float('nan')), torch.full((2, 2), float('inf'))]
        for value in invalid:
            with self.subTest(shape=value.shape), self.assertRaises(ValueError):
                SubspaceSearch(value)
        memory = torch.tensor([[1., 0.], [1., .2]])
        for variance in [0., -1., 1.1, float('nan'), True]:
            with self.subTest(variance=variance), self.assertRaises(ValueError):
                SubspaceSearch(memory, explained_variance=variance)
        for chunk in [0, -1, True, 1.5]:
            with self.subTest(chunk=chunk), self.assertRaises(ValueError):
                SubspaceSearch(memory, chunk=chunk)
        model = SubspaceSearch(memory)
        for query in [torch.ones(2, 3), torch.zeros(2, 2), torch.ones(0, 2)]:
            with self.subTest(query=query.shape), self.assertRaises(ValueError):
                model.predict_raw(query)
        for fields in [{}, {'search': torch.tensor([1.]), 'subspace': torch.tensor([1., 2.])},
                       {'search': torch.tensor([-1.]), 'subspace': torch.tensor([1.])},
                       {'search': torch.tensor([float('nan')]), 'subspace': torch.tensor([1.])}]:
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                fuse(fields, self.calibration())
        with self.assertRaises(ValueError):
            fuse({'search': torch.tensor([1.]), 'subspace': torch.tensor([1.])}, {})


if __name__ == '__main__':
    unittest.main()
