"""Synthetic signed-benefit/leakage contracts; not real-data performance evidence."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

import numpy as np

from safe_iad.benefit_model import BenefitModel, fit_benefit_models


ROLES = {'fixture': {'meta_training': ['source'], 'validation': ['val'],
                     'calibration': ['cal'], 'final_test': ['final']}}


def synthetic_rows():
    rows = []
    for index, signal in enumerate([-1., -.6, -.2, .2, .6, 1.]):
        source = f'source/train/good/{index}.png'
        for seed in [0, 1]:
            for synthetic in [False, True]:
                rows.append({
                    'dataset': 'fixture', 'category': 'source', 'experiment_role': 'meta_training',
                    'native_query_source_split': 'train', 'query_source_id': source,
                    'query_id': f'{source}_synthetic' if synthetic else source,
                    'query_kind': 'synthetic_fixture_training_query' if synthetic else 'real_normal_training_query',
                    'synthetic_provenance': {'source_image_id': source} if synthetic else None,
                    'seed': seed, 'support_ids': [f'reference-{seed}'], 'candidate_id': 'candidate',
                    'candidate_pool_ids': ['candidate'], 'final_test_labels_used': False,
                    'feature_names': ['signal', 'loo_sensitivity_imputed', 'loo_missing', 'constant'],
                    'features': [signal, 0., 1., 2.], 'loo_defined': False, 'loo_missing_indicator': 1,
                    'observed_benefit': .1 * signal + .01 * synthetic,
                    'checkpoint_sha256': '1' * 64, 'source_commit': '2' * 40,
                    'preprocessing_version': 'synthetic-fixture-v1',
                    'feature_layer_configuration': 'synthetic-features',
                    'loss_specification': {'type': 'synthetic_signed_loss', 'margin': 1.},
                })
    return rows


class SyntheticBenefitModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = synthetic_rows()
        cls.models, cls.report = fit_benefit_models(cls.rows, ROLES, seed=7)

    def test_signed_predictions_and_regression_quality(self):
        x = [row['features'] for row in self.rows]
        truth = np.array([row['observed_benefit'] for row in self.rows])
        for model in self.models.values():
            predictions = model.predict(x)
            self.assertLess(predictions.min(), 0.)
            self.assertGreater(predictions.max(), 0.)
            self.assertLess(float(np.mean((predictions - truth) ** 2)), 1e-4)

    def test_deterministic_training_and_selection(self):
        repeated, report = fit_benefit_models(self.rows, ROLES, seed=7)
        self.assertEqual(report, self.report)
        for name, model in self.models.items():
            np.testing.assert_array_equal(model.predict([r['features'] for r in self.rows]),
                                          repeated[name].predict([r['features'] for r in self.rows]))

    def test_derivatives_and_support_draws_share_one_cv_fold(self):
        assignments = {}
        folds = self.report['grouped_cv']['folds']
        for fold in folds:
            self.assertFalse(set(fold['train_source_groups']) & set(fold['held_out_source_groups']))
            for group in fold['held_out_source_groups']:
                self.assertNotIn(group, assignments)
                assignments[group] = fold['fold']
        self.assertEqual(len(assignments), 6)
        for row in self.rows:
            key = json.dumps([row['dataset'], row['category'], row['query_source_id']], separators=(',', ':'))
            self.assertIn(key, assignments)
        self.assertEqual(sum(fold['held_out_rows'] for fold in folds), len(self.rows))
        self.assertEqual(self.report['model_selection_role'], 'source_training_grouped_cv_only')
        self.assertFalse(self.report['validation_labels_used_for_model_selection'])

    def test_constant_and_independent_negative_groups_reported(self):
        self.assertEqual(set(self.report['constant_columns']),
                         {'loo_sensitivity_imputed', 'loo_missing', 'constant'})
        self.assertEqual(self.report['negative_targets'], 12)
        self.assertEqual(self.report['unique_negative_source_groups'], 3)

    def test_json_roundtrip_preserves_both_models(self):
        with tempfile.TemporaryDirectory() as temporary:
            for name, model in self.models.items():
                path = Path(temporary) / f'{name}.json'
                model.save(path)
                restored = BenefitModel.load(path)
                json.loads(path.read_text())
                self.assertEqual(restored.feature_names, model.feature_names)
                self.assertEqual(restored.provenance, model.provenance)
                np.testing.assert_array_equal(restored.predict([row['features'] for row in self.rows]),
                                              model.predict([row['features'] for row in self.rows]))

    def test_native_nontraining_and_reserved_roles_rejected(self):
        for change in [{'native_query_source_split': 'test'}, {'experiment_role': 'final_evaluation_only'},
                       {'experiment_role': 'validation'}, {'experiment_role': 'calibration'},
                       {'category': 'val'}, {'category': 'cal'}, {'category': 'final'},
                       {'native_query_source_label': 'anomaly'}]:
            rows = copy.deepcopy(self.rows)
            rows[-1].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                fit_benefit_models(rows, ROLES)

    def test_oracle_and_final_label_flags_rejected(self):
        for change in [{'never_use_for_training': True}, {'final_test_labels_used': True},
                       {'policy': 'oracle'}, {'oracle_labels_used': True},
                       {'query_label_used_for_selection': True}]:
            rows = copy.deepcopy(self.rows)
            rows[-1].update(change)
            with self.subTest(change=change), self.assertRaises(ValueError):
                fit_benefit_models(rows, ROLES)

    def test_mixed_provenance_and_feature_order_rejected(self):
        for field in ['checkpoint_sha256', 'source_commit', 'preprocessing_version',
                      'feature_layer_configuration', 'loss_specification', 'feature_names']:
            rows = copy.deepcopy(self.rows)
            if field == 'feature_names':
                rows[-1][field] = list(reversed(rows[-1][field]))
            elif field == 'loss_specification':
                rows[-1][field]['margin'] = 2.
            else:
                rows[-1][field] += '-changed'
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, 'mixed'):
                fit_benefit_models(rows, ROLES)

    def test_invalid_missingness_rejected(self):
        for vector in [[1., 0., .5, 2.], [1., .1, 1., 2.]]:
            with self.assertRaises(ValueError):
                self.models['ridge'].predict([vector])
        rows = copy.deepcopy(self.rows)
        rows[-1]['loo_defined'] = True
        with self.assertRaises(ValueError):
            fit_benefit_models(rows, ROLES)

    def test_no_query_truth_in_predict_api(self):
        with self.assertRaises(TypeError):
            self.models['ridge'].predict([self.rows[0]['features']], query_label=1)
        with self.assertRaises(TypeError):
            self.models['ridge'].predict([self.rows[0]['features']], query_mask=np.ones((2, 2)))
        rows = copy.deepcopy(self.rows)
        for row in rows:
            row['feature_names'][0] = 'query_label'
        with self.assertRaisesRegex(ValueError, 'not inference features'):
            fit_benefit_models(rows, ROLES)

    def test_inference_contract_and_shapes_rejected(self):
        model = self.models['ridge']
        wrong = dict(model.provenance, preprocessing_version='changed')
        with self.assertRaises(ValueError):
            model.predict([self.rows[0]['features']], feature_names=model.feature_names, provenance=wrong)
        with self.assertRaises(ValueError):
            model.predict([[1., 2.]])
        with self.assertRaises(ValueError):
            model.predict([[float('nan'), 0., 1., 2.]])

    def test_source_overlap_and_ungroupable_rows_rejected(self):
        for change in [{'support_ids': [self.rows[0]['query_source_id']]}, {'query_source_id': None}]:
            rows = copy.deepcopy(self.rows)
            rows[0].update(change)
            with self.assertRaises(ValueError):
                fit_benefit_models(rows, ROLES)
        with self.assertRaisesRegex(ValueError, 'two independent'):
            fit_benefit_models(self.rows[:4], ROLES)

    def test_malformed_json_model_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'model.json'
            self.models['mlp'].save(path)
            payload = json.loads(path.read_text())
            payload['parameters']['weight1'] = [[0.]]
            path.write_text(json.dumps(payload))
            with self.assertRaises(ValueError):
                BenefitModel.load(path)


if __name__ == '__main__':
    unittest.main()
