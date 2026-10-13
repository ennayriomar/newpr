"""Synthetic SAFAL contracts/math checks; reliability requires actual data."""
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np
import torch

from safe_iad.safal_model import SAFALModel
from safe_iad.subspace_search import BranchCalibration


class SyntheticSAFALTests(unittest.TestCase):
    def features(self):
        rng = np.random.default_rng(44)
        return [torch.tensor(rng.normal(size=(12, 4))+np.asarray([2., 1., .5, 3.])) for _ in range(4)]

    def calibration(self):
        return BranchCalibration(.4, 2., .3, 1.5, ('normal-cal:1', 'normal-cal:2'))

    def test_synthetic_branch_fusion_shapes_and_operational_coverage(self):
        support, _, query, _ = self.features()
        model = SAFALModel([support], ['support:1'])
        prediction = model.predict(query, self.calibration())
        self.assertEqual(set(prediction['maps']), {'search', 'subspace', 'fixed_avg', 'max', 'safal'})
        for field in prediction['maps'].values():
            self.assertEqual(field.shape, (12,))
            self.assertTrue(bool(torch.isfinite(field).all()))
        expected_search = 1/(1+prediction['maps']['search'])
        expected_subspace = 1/(1+prediction['maps']['subspace'])
        torch.testing.assert_close(prediction['coverage']['search'], expected_search)
        torch.testing.assert_close(prediction['patch_adequacy'], .5*(expected_search+expected_subspace))
        for value in [prediction['A'], prediction['U'], prediction['branch_disagreement']]:
            self.assertTrue(0 <= value <= 1)
        weight = prediction['weights']['search']
        self.assertTrue(bool(((weight >= .1) & (weight <= .9)).all()))
        torch.testing.assert_close(weight+prediction['weights']['subspace'], torch.ones_like(weight))
        torch.testing.assert_close(prediction['maps']['safal'], weight*prediction['maps']['search']
                                   +(1-weight)*prediction['maps']['subspace'])
        self.assertTrue(torch.all(prediction['maps']['max'] >= prediction['maps']['search']))
        self.assertFalse(prediction['metadata']['probabilities'])
        json.dumps(prediction['metadata'], allow_nan=False)

    def test_synthetic_lower_coverage_favors_search_without_claiming_correctness(self):
        support, _, _, _ = self.features()
        model = SAFALModel([support], ['support:1'])
        covered = model.predict(support, self.calibration())
        distant = model.predict(support+100., self.calibration())
        self.assertLess(distant['A'], covered['A'])
        self.assertGreater(distant['metadata']['mean_search_weight'], covered['metadata']['mean_search_weight'])
        self.assertIn('defects', distant['metadata']['coverage_semantics'])

    def test_synthetic_k1_image_leave_one_out_is_missing_and_k2_is_defined(self):
        first, second, query, _ = self.features()
        one = SAFALModel([first], ['support:1']).predict(query, self.calibration())
        self.assertIsNone(one['loo']['search'])
        self.assertIsNone(one['loo']['subspace'])
        self.assertFalse(bool(one['loo']['valid'].any()))
        self.assertIsNone(one['loo']['per_image_search'])
        self.assertFalse(one['metadata']['valid_fields']['image_leave_one_out'])
        two = SAFALModel([first, second], ['support:1', 'support:2']).predict(query, self.calibration())
        self.assertTrue(bool(two['loo']['valid'].all()))
        self.assertEqual(two['loo']['search'].shape, (12,))
        self.assertEqual(two['loo']['per_image_search'].shape, (2, 12))
        torch.testing.assert_close(two['loo']['search'], two['loo']['per_image_search'].max(dim=0).values)
        self.assertTrue(bool(torch.isfinite(two['loo']['subspace']).all()))

    def test_synthetic_normal_calibration_is_separate_and_has_explicit_extra_budget(self):
        first, second, third, query = self.features()
        model = SAFALModel([first], ['support:1'])
        calibration = model.calibrate([second, third], ['normal-cal:1', 'normal-cal:2'])
        self.assertGreater(calibration.image_search, 0)
        prediction = model.predict(query)
        self.assertEqual(prediction['metadata']['initial_support_images'], 1)
        self.assertEqual(prediction['metadata']['extra_normal_calibration_images'], 2)
        self.assertEqual(prediction['metadata']['additional_selected_references'], 0)
        with self.assertRaisesRegex(ValueError, 'disjoint'):
            model.calibrate([second], ['support:1'])
        with self.assertRaises(TypeError):
            model.predict(query, labels=np.ones(12))

    def test_synthetic_checkpoint_without_pickle_reconstructs_identical_predictions(self):
        first, second, third, query = self.features()
        model = SAFALModel([first, second], ['support:1', 'support:2'])
        model.calibrate([third], ['normal-cal:1'])
        expected = model.predict(query)
        with tempfile.TemporaryDirectory(dir='/tmp') as directory:
            prefix = Path(directory)/'model'
            paths = model.save(prefix, provenance={'checkpoint_sha256': 'declared-test-hash', 'synthetic': True})
            with np.load(paths['npz'], allow_pickle=False) as archive:
                self.assertEqual(set(archive.files), {'support_000', 'support_001'})
                self.assertFalse(any(archive[key].dtype.hasobject for key in archive.files))
            loaded = SAFALModel.load(prefix)
            actual = loaded.predict(query)
            for name in expected['maps']:
                torch.testing.assert_close(actual['maps'][name], expected['maps'][name], rtol=0, atol=0)
            self.assertEqual(actual['image_scores'], expected['image_scores'])
            self.assertEqual(actual['A'], expected['A'])
            self.assertEqual(actual['U'], expected['U'])
            self.assertEqual(loaded.metadata()['support_feature_sha256'], model.metadata()['support_feature_sha256'])
            with Path(paths['npz']).open('ab') as handle:
                handle.write(b'changed')
            with self.assertRaisesRegex(ValueError, 'checksum'):
                SAFALModel.load(prefix)

    def test_synthetic_invalid_support_calibration_and_prediction_rejected(self):
        first, second, _, query = self.features()
        for images, ids in [([], []), ([first], []), ([first, second], ['same', 'same']),
                            ([torch.zeros(12, 4)], ['a']), ([torch.ones(1, 4)], ['a']),
                            ([first, torch.ones(12, 3)], ['a', 'b'])]:
            with self.subTest(ids=ids), self.assertRaises(ValueError):
                SAFALModel(images, ids)
        model = SAFALModel([first], ['support:1'])
        with self.assertRaisesRegex(ValueError, 'calibration'):
            model.predict(query)
        for quantile in [0, 1.1, float('nan'), True]:
            with self.subTest(quantile=quantile), self.assertRaises(ValueError):
                model.calibrate([second], ['cal:1'], quantile=quantile)
        with self.assertRaises(ValueError):
            model.calibrate([], [])
        with self.assertRaisesRegex(ValueError, 'disjoint'):
            model.predict(query, BranchCalibration(.4, 2., .3, 1.5, ('support:1',)))


if __name__ == '__main__':
    unittest.main()
