"""Synthetic release split/map contracts; no real-data performance evidence."""
import copy
import unittest

import numpy as np

from verify_safal_release import check_map_fields, validate_manifest


def fixture():
    roles = {'fixture': {'meta_training': ['source'], 'validation': ['target'], 'calibration': ['cal'], 'final_test': ['final']}}
    source = {'dataset': 'fixture', 'category': 'source', 'support_ids': ['s1', 's2'], 'calibration_ids': ['sc'],
              'fit_parent_ids': ['fit'], 'heldout_parent_ids': ['held']}
    target = {'id': 'case', 'dataset': 'fixture', 'category': 'target', 'role': 'validation', 'shots': 1,
              'support_ids': ['t1'], 'calibration_ids': ['tc'], 'query_ids': ['q'], 'k_plus_calibration': 2,
              'strict_k_image_few_shot': False, 'support_views': ['identity']}
    manifest = {'schema_version': 1, 'scope': 'safal_full_model_validation', 'category_roles': roles,
                'source_episodes': [source], 'episodes': [target]}
    entries = [('s1', 'source', 'support'), ('s2', 'source', 'support'), ('sc', 'source', 'normal_calibration'),
               ('fit', 'source', 'source_proxy_fit_parent'), ('held', 'source', 'source_proxy_cal_parent'),
               ('t1', 'target', 'support'), ('tc', 'target', 'normal_calibration'), ('q', 'target', 'native_evaluation')]
    used = [{'dataset': 'fixture', 'image': image, 'category': category, 'roles': [role],
             'split': 'test' if image == 'q' else 'train', 'label': 'anomaly' if image == 'q' else 'normal',
             'mask': 'q_mask.png' if image == 'q' else None} for image, category, role in entries]
    return manifest, used


def fields():
    values = {'search': 2., 'subspace': 4., 'fixed_avg': 3., 'max': 4., 'safal': 3.,
              'adequacy': .5, 'uncertainty': .35, 'branch_disagreement': .2,
              'raw_search': 1., 'raw_subspace': 2., 'search_weight': .5}
    return {name: np.full((256, 256), value, dtype=np.float32) for name, value in values.items()}


class SyntheticSAFALReleaseTests(unittest.TestCase):
    def test_source_parent_and_target_budget_fixture(self):
        manifest, used = fixture()
        groups, queries = validate_manifest(manifest, used)
        self.assertEqual(groups['meta_training'], {('fixture', 'source', 'fit')})
        self.assertEqual(queries, {('fixture', 'q')})

    def test_source_normal_synthetic_parent_leak_rejected(self):
        manifest, used = fixture()
        manifest['source_episodes'][0]['heldout_parent_ids'] = ['fit']
        with self.assertRaisesRegex(ValueError, 'leakage'):
            validate_manifest(manifest, used)

    def test_native_test_input_cannot_fit_support(self):
        manifest, used = fixture()
        next(row for row in used if row['image'] == 't1')['split'] = 'test'
        with self.assertRaisesRegex(ValueError, 'native-train normals'):
            validate_manifest(manifest, used)

    def test_k_plus_calibration_must_not_be_called_strict(self):
        for change in [{'k_plus_calibration': 1}, {'strict_k_image_few_shot': True}, {'shots': 2}]:
            manifest, used = fixture()
            manifest['episodes'][0].update(change)
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'budget'):
                validate_manifest(manifest, used)

    def test_used_input_role_mismatch_rejected(self):
        manifest, used = fixture()
        used[-1]['roles'] = ['support']
        with self.assertRaisesRegex(ValueError, 'role memberships'):
            validate_manifest(manifest, used)

    def test_valid_metric_diagnostics_and_evidence(self):
        check_map_fields(fields())

    def test_nonfinite_wrong_precision_and_probability_range_rejected(self):
        for kind in ['nan', 'float16', 'out_of_range']:
            maps = fields()
            if kind == 'nan':
                maps['safal'][0, 0] = np.nan
            elif kind == 'float16':
                maps['safal'] = maps['safal'].astype(np.float16)
            else:
                maps['adequacy'][0, 0] = 1.1
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                check_map_fields(maps)

    def test_maximum_comparator_must_keep_branches(self):
        maps = fields()
        maps['max'][:] = 1.
        with self.assertRaisesRegex(ValueError, 'loses branch evidence'):
            check_map_fields(maps)


if __name__ == '__main__':
    unittest.main()
