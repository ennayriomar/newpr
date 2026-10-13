"""Held-out synthetic probability tests; not native industrial calibration evidence."""
import copy
from pathlib import Path
import tempfile
import unittest

import numpy as np

from safe_iad.safal_calibration import (
    ERROR_FEATURE_NAMES, ErrorCalibrator, calibration_feature_vector,
    error_probability_metrics, fit_error_calibrator, predict_error_probability,
)


class SafalCalibrationTests(unittest.TestCase):
    roles = {'source_dataset': {'meta_training': ['source_category'], 'validation': ['val'],
                                'calibration': ['cal'], 'final_test': ['final']}}

    def rows(self, count, start, role, rng):
        x = np.column_stack([rng.uniform(0, 4, count), rng.uniform(0, 1, count),
                             rng.uniform(0, 1, count), rng.uniform(0, 1, count)])
        logits = 2.8-2*x[:, 0]-2*x[:, 1]+1.4*x[:, 2]+1.2*x[:, 3]
        probability = 1/(1+np.exp(-logits))
        labels = (rng.random(count) < probability).astype(int)
        return [dict(dataset='source_dataset', category='source_category',
                     query_source_id=f'train/source-{start+index//2}', experiment_role=role,
                     native_query_source_split='train', domain='source_normal_plus_cutpaste',
                     target='prediction_error', features=vector.tolist(),
                     feature_names=list(ERROR_FEATURE_NAMES), error_label=int(label))
                for index, (vector, label) in enumerate(zip(x, labels))]

    def fixture(self):
        rng = np.random.default_rng(12)
        return self.rows(600, 0, 'meta_training', rng), self.rows(300, 1000, 'source_calibration', rng)

    def test_heldout_statistical_relationship_beats_constant_source_prevalence(self):
        fit, held = self.fixture()
        model, report = fit_error_calibrator(fit, held, self.roles)
        labels = np.array([row['error_label'] for row in held])
        source_rate = np.mean([row['error_label'] for row in fit])
        baseline = np.mean((labels-source_rate)**2)
        self.assertLess(report['heldout_metrics']['brier'], baseline-.02)
        probability = model.predict([row['features'] for row in held], domain='native_industrial_validation')
        self.assertTrue(np.isfinite(probability).all())
        self.assertTrue(((probability >= 0) & (probability <= 1)).all())
        self.assertEqual(report['group_overlap'], 0)
        self.assertEqual(report['fit_groups'], 300)
        self.assertEqual(report['calibration_groups'], 150)
        self.assertFalse(report['heldout_used_for_fitting'])
        self.assertFalse(report['probability_calibration_claim'])
        self.assertTrue(model.prediction_metadata('native_industrial_validation')['domain_shift'])
        self.assertFalse(model.prediction_metadata('native_industrial_validation')['calibration_transfer_verified'])

    def test_scaler_uses_only_fit_rows_and_holdout_does_not_change_coefficients(self):
        fit, held = self.fixture()
        model, _ = fit_error_calibrator(fit, held, self.roles)
        np.testing.assert_array_equal(model.feature_mean, np.mean([row['features'] for row in fit], axis=0))
        altered = copy.deepcopy(held)
        for row in altered:
            row['features'][0] += 100
            row['error_label'] = 1-row['error_label']
        other, _ = fit_error_calibrator(fit, altered, self.roles)
        np.testing.assert_array_equal(model.coefficients, other.coefficients)
        np.testing.assert_array_equal(model.feature_scale, other.feature_scale)
        self.assertEqual(model.intercept, other.intercept)

    def test_normal_synthetic_sibling_group_overlap_rejected(self):
        fit, held = self.fixture()
        held[0]['query_source_id'] = fit[0]['query_source_id']
        with self.assertRaisesRegex(ValueError, 'disjoint'):
            fit_error_calibrator(fit, held, self.roles)

    def test_final_category_target_domain_and_wrong_event_rejected(self):
        fit, held = self.fixture()
        for key, value in [('category', 'final'), ('domain', 'native_industrial_validation'),
                           ('target', 'defect_presence'), ('native_query_source_split', 'test'),
                           ('target_test_labels_used', True), ('experiment_role', 'final_test')]:
            changed = copy.deepcopy(fit)
            changed[0][key] = value
            with self.subTest(key=key), self.assertRaises(ValueError):
                fit_error_calibrator(changed, held, self.roles)
        changed = copy.deepcopy(held)
        changed[0]['domain'] = 'native_industrial_validation'
        with self.assertRaises(ValueError):
            fit_error_calibrator(fit, changed, self.roles)

    def test_binary_both_class_fit_requirement_and_one_class_holdout(self):
        fit, held = self.fixture()
        changed = copy.deepcopy(fit)
        changed[0]['error_label'] = 2
        with self.assertRaisesRegex(ValueError, 'binary'):
            fit_error_calibrator(changed, held, self.roles)
        for row in changed:
            row['error_label'] = 0
        with self.assertRaisesRegex(ValueError, 'both correct and incorrect'):
            fit_error_calibrator(changed, held, self.roles)
        for row in held:
            row['error_label'] = 0
        _, report = fit_error_calibrator(fit, held, self.roles)
        self.assertFalse(report['heldout_has_both_error_classes'])
        self.assertIsNone(report['heldout_metrics']['risk_coverage']['error_detection_auroc'])

    def test_json_reload_replays_exact_and_has_no_pickle(self):
        fit, held = self.fixture()
        model, _ = fit_error_calibrator(fit, held, self.roles)
        features = [row['features'] for row in held]
        with tempfile.TemporaryDirectory(dir='/tmp') as directory:
            path = Path(directory)/'calibrator.json'
            model.save(path)
            restored = ErrorCalibrator.load(path)
            np.testing.assert_array_equal(model.predict(features), restored.predict(features))
            self.assertEqual(model.prediction_metadata('native_industrial_validation'),
                             restored.prediction_metadata('native_industrial_validation'))
            self.assertIn('"standardization_fit_scope": "fit_rows_only"', path.read_text())

    def test_observable_feature_order_and_missing_calibrator(self):
        self.assertEqual(calibration_feature_vector(.7, .8, .2, .4), [abs(.7-1), .8, .2, .4])
        self.assertIsNone(predict_error_probability(None, [[.1, .5, .2, .3]], domain='native_industrial_validation'))
        fit, held = self.fixture()
        model, _ = fit_error_calibrator(fit, held, self.roles)
        with self.assertRaisesRegex(ValueError, 'feature order'):
            model.predict([[.1, .5, .2, .3]], feature_names=tuple(reversed(ERROR_FEATURE_NAMES)))
        with self.assertRaises(ValueError):
            calibration_feature_vector(1, 1.1, 0, 0)
        fit[0]['feature_names'][0] = 'error_label'
        with self.assertRaises(ValueError):
            fit_error_calibrator(fit, held, self.roles)

    def test_actual_error_probability_metrics_and_ties(self):
        result = error_probability_metrics([0, 1], [.2, .8], n_bins=2)
        self.assertAlmostEqual(result['brier'], .04)
        self.assertAlmostEqual(result['ece'], .2)
        self.assertAlmostEqual(result['nll'], -np.log(.8))
        self.assertEqual(result['risk_coverage']['error_detection_auroc'], 1.)
        tie_a = error_probability_metrics([0, 1], [.5, .5])
        tie_b = error_probability_metrics([1, 0], [.5, .5])
        self.assertEqual(tie_a, tie_b)
        with self.assertRaises(ValueError):
            error_probability_metrics([0, 2], [.2, .8])
        with self.assertRaises(ValueError):
            error_probability_metrics([0, 1], [.2, 1.2])


if __name__ == '__main__':
    unittest.main()
