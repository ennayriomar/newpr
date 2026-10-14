"""Synthetic tunable-SAFAL math, isolation and serialization tests."""
from dataclasses import replace
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from sklearn.decomposition import PCA
import torch

from safe_iad.safal_model import SAFALModel
from safe_iad.safal_tunable import Parameters, TunableSubspaceSearch
from safe_iad.subspace_search import BranchCalibration


class SyntheticTunableSAFALTests(unittest.TestCase):
    def features(self):
        rng = np.random.default_rng(92)
        return [torch.tensor(rng.normal(size=(24, 6))*np.asarray([3., 1., .3, .1, .05, .01])
                             +np.asarray([2., 1., .5, 3., 1., 1.])) for _ in range(4)]

    def model(self):
        images = self.features()
        return TunableSubspaceSearch(images[:2], ['support:1', 'support:2']), images

    def calibration(self):
        return BranchCalibration(2., 4., 1., 2., ('cal:1',))

    def test_synthetic_one_svd_grid_matches_independent_sklearn_pca(self):
        images = self.features()
        original = torch.linalg.svd
        with patch('torch.linalg.svd', wraps=original) as fitted:
            model = TunableSubspaceSearch(images[:2], ['support:1', 'support:2'])
        self.assertEqual(fitted.call_count, 1)
        raw = model.score_raw(images[3])
        memory, query = torch.cat(images[:2]).numpy(), images[3].numpy()
        for variance in model.variances:
            independent = PCA(n_components=variance, svd_solver='full').fit(memory)
            residual = np.square(query-independent.inverse_transform(independent.transform(query))).sum(1)
            np.testing.assert_allclose(raw['subspace'][str(variance)].numpy(), residual, atol=1e-10)

    def test_synthetic_original_variant_matches_frozen_legacy_safal(self):
        model, images = self.model()
        legacy = SAFALModel(images[:2], ['support:1', 'support:2'])
        params = Parameters()
        cal = model.calibration_from_raw([model.score_raw(images[2])], ['cal:1'], params)
        old_cal = legacy.calibrate([images[2]], ['cal:1'])
        self.assertEqual(cal, old_cal)
        new = model.predict_from_raw(model.score_raw(images[3]), params, cal)
        old = legacy.predict(images[3])
        torch.testing.assert_close(new['map'], old['maps']['safal'], rtol=0, atol=0)
        torch.testing.assert_close(new['patch_adequacy'], old['patch_adequacy'], rtol=0, atol=0)
        self.assertEqual(new['image_score'], old['image_scores']['safal'])

    def test_synthetic_fixed_endpoints_and_max_preserve_branch_controls(self):
        model, images = self.model()
        raw = model.score_raw(images[3])
        for alpha, branch in [(0., 'subspace'), (1., 'search')]:
            params = Parameters(fusion='fixed', search_weight=alpha)
            result = model.predict_from_raw(raw, params, self.calibration())
            torch.testing.assert_close(result['map'], result['normalized_branches'][branch])
            self.assertEqual(result['image_score'], result['image_scores_branch'][branch])
        result = model.predict_from_raw(raw, Parameters(fusion='max'), self.calibration())
        self.assertEqual(result['image_alert'], any(score >= 1 for score in result['image_scores_branch'].values()))
        for branch in result['normalized_branches'].values():
            self.assertTrue(bool((result['map'] >= branch).all()))

    def test_synthetic_adaptive_direction_is_explicit_and_weights_bounded(self):
        model, images = self.model()
        raw = model.score_raw(images[3])
        first = model.predict_from_raw(raw, Parameters(), self.calibration())
        reverse = model.predict_from_raw(raw, Parameters(fusion='adaptive_reversed'), self.calibration())
        torch.testing.assert_close(first['weights']['search']+reverse['weights']['search'],
                                   torch.ones_like(first['map']))
        for result in [first, reverse]:
            self.assertTrue(bool(((result['weights']['search'] >= .1) & (result['weights']['search'] <= .9)).all()))
            self.assertFalse(result['valid_fields']['calibrated_probabilities'])

    def test_synthetic_disjoint_patch_peaks_keep_image_combination_distinct(self):
        model, _ = self.model()
        raw = {'search': torch.tensor([2., 0.]), 'subspace': {'0.99': torch.tensor([0., 4.])}}
        fixed = model.predict_from_raw(raw, Parameters(aggregation='max', fusion='fixed'), self.calibration())
        adaptive = model.predict_from_raw(raw, Parameters(aggregation='max'), self.calibration())
        maximum = model.predict_from_raw(raw, Parameters(aggregation='max', fusion='max'), self.calibration())
        self.assertEqual(fixed['image_score'], 1.)
        self.assertLess(adaptive['image_score'], 1.)
        self.assertEqual(maximum['image_score'], 1.)
        # Image threshold is a decision parameter; it does not alter map scale.
        strict = model.predict_from_raw(raw, Parameters(aggregation='max', fusion='fixed', image_threshold=1.25), self.calibration())
        self.assertFalse(strict['image_alert'])
        torch.testing.assert_close(strict['map'], fixed['map'])

    def test_synthetic_calibration_disjointness_quantile_and_finite_cutoffs(self):
        model, images = self.model()
        raw = model.score_raw(images[2])
        with self.assertRaisesRegex(ValueError, 'disjoint'):
            model.calibration_from_raw([raw], ['support:1'], Parameters())
        with self.assertRaises(ValueError):
            model.calibration_from_raw([], [], Parameters())
        with self.assertRaises(TypeError):
            model.calibration_from_raw([raw], ['cal:1'], Parameters(), labels=[1])
        with self.assertRaisesRegex(ValueError, 'disjoint'):
            model.predict_from_raw(raw, Parameters(), BranchCalibration(1., 1., 1., 1., ('support:1',)))
        degenerate = {'search': torch.zeros(3), 'subspace': {'0.99': torch.zeros(3)}}
        with self.assertRaisesRegex(ValueError, 'strictly positive'):
            model.calibration_from_raw([degenerate], ['cal:1'], Parameters())

    def test_synthetic_save_load_replays_grid_scores_and_selected_inference(self):
        model, images = self.model()
        params = Parameters(explained_variance=.95, fusion='fixed', search_weight=.25, aggregation='max')
        cal = model.calibration_from_raw([model.score_raw(images[2])], ['cal:1'], params)
        expected_raw = model.score_raw(images[3])
        expected = model.predict_from_raw(expected_raw, params, cal)
        with tempfile.TemporaryDirectory(dir='/tmp') as directory:
            prefix = Path(directory)/'selected'
            paths = model.save(prefix, params, cal, provenance={'synthetic': True})
            with np.load(paths['npz'], allow_pickle=False) as archive:
                self.assertFalse(any(archive[key].dtype.hasobject for key in archive.files))
            loaded = TunableSubspaceSearch.load(prefix)
            actual_raw = loaded.score_raw(images[3])
            for key in expected_raw['subspace']:
                torch.testing.assert_close(actual_raw['subspace'][key], expected_raw['subspace'][key], rtol=0, atol=0)
            actual = loaded.predict_from_raw(actual_raw, loaded.params, loaded.calibration)
            torch.testing.assert_close(actual['map'], expected['map'], rtol=0, atol=0)
            self.assertEqual(actual['image_score'], expected['image_score'])
            self.assertEqual(loaded.variances, model.variances)
            with Path(paths['npz']).open('ab') as handle:
                handle.write(b'changed')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                TunableSubspaceSearch.load(prefix)

    def test_synthetic_invalid_parameters_support_and_raw_fields(self):
        for kwargs in [{'explained_variance': 0.}, {'normal_quantile': float('nan')}, {'search_weight': -1.},
                       {'image_threshold': 0.}, {'aggregation': 'mean'}, {'fusion': 'guess'}, {'search_weight': True}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                Parameters(**kwargs)
        self.assertEqual(Parameters().id, Parameters().identifier)
        self.assertNotEqual(Parameters().id, replace(Parameters(), aggregation='max').id)
        model, images = self.model()
        for supports, ids in [([], []), ([images[0], images[1]], ['same', 'same']),
                              ([torch.zeros(3, 6)], ['a'])]:
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                TunableSubspaceSearch(supports, ids)
        constant = TunableSubspaceSearch([torch.ones(3, 6)], ['a'])
        raw = constant.score_raw(torch.full((2, 6), 2.))
        self.assertTrue(bool(torch.isfinite(raw['subspace']['0.99']).all()))
        self.assertEqual(constant.metadata()['numerical_rank'], 0)
        with self.assertRaisesRegex(ValueError, 'absent'):
            model.predict_from_raw(model.score_raw(images[3]), Parameters(explained_variance=.8), self.calibration())
        with self.assertRaises(ValueError):
            model.predict_from_raw({'search': torch.ones(2), 'subspace': {'0.99': torch.ones(3)}},
                                   Parameters(), self.calibration())


if __name__ == '__main__':
    unittest.main()
