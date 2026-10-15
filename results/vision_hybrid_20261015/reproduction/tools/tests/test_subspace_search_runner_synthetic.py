"""Synthetic protocol fixtures; these are not real benchmark observations."""
import copy
import unittest

from safe_iad.run_subspace_search_pilot import build_manifest, validate_config, _positive_cutoff
from safe_iad.verify_dataset import Sample


class SubspaceSearchProtocolTests(unittest.TestCase):
    def setUp(self):
        self.roles = {'mvtec_ad': {'meta_training': ['source'], 'validation': ['cable'],
                                   'calibration': ['capsule'], 'final_test': ['bottle']}}
        self.config = dict(schema_version=1, scope='new_method_validation_pilot', roots={'mvtec_ad': '/unused'},
                           validation_categories={'mvtec_ad': 'cable'}, calibration_categories={'mvtec_ad': 'capsule'},
                           support_views=['identity'], map_storage_dtype='float16', shots=[1, 2, 4], seeds=[7, 11, 19],
                           queries_per_label=3, calibration_queries_per_draw=2, partition_seed=71,
                           calibration_standard_deviations=3., excluded_query_ids={'mvtec_ad': ['cable/test/good/000.png']})
        self.samples = []
        for category in ['cable', 'capsule']:
            self.samples += [Sample(category, 'train', 'normal', f'{category}/train/good/{i:03}.png', None) for i in range(20)]
        self.samples += [Sample('cable', 'test', label, f'cable/test/{folder}/{i:03}.png',
                                f'cable/ground_truth/{i:03}.png' if label == 'anomaly' else None)
                         for label, folder in [('normal', 'good'), ('anomaly', 'bad')] for i in range(6)]

    def test_final_category_cannot_be_used_for_validation(self):
        config = copy.deepcopy(self.config)
        config['validation_categories']['mvtec_ad'] = 'bottle'
        with self.assertRaisesRegex(ValueError, 'reserved roles'):
            validate_config(config, self.roles)

    def test_calibration_cannot_be_native_test_or_validation_category(self):
        config = copy.deepcopy(self.config)
        config['calibration_categories']['mvtec_ad'] = 'cable'
        with self.assertRaisesRegex(ValueError, 'reserved roles'):
            validate_config(config, self.roles)

    def test_nested_fixed_budgets_and_global_calibration_query_reservation(self):
        manifest = build_manifest(self.config, self.roles, {'mvtec_ad': self.samples})
        self.assertEqual(manifest['unique_validation_queries'], 6)
        for episode in manifest['episodes']:
            self.assertEqual(len(episode['support']), episode['shots'])
            self.assertTrue(all(s['split'] == 'train' and s['label'] == 'normal' for s in episode['support']))
            reserved = set(episode['all_reserved_calibration_query_ids'])
            self.assertFalse(reserved & {s['image'] for s in episode['calibration_support']})
            self.assertEqual(len(episode['calibration_queries']), 2)
        for seed in self.config['seeds']:
            episodes = [e for e in manifest['episodes'] if e['seed'] == seed]
            full = episodes[-1]['support']
            for episode in episodes:
                self.assertEqual(episode['support'], full[:episode['shots']])

    def test_fresh_balanced_query_selection_is_deterministic(self):
        first = build_manifest(self.config, self.roles, {'mvtec_ad': self.samples})
        second = build_manifest(self.config, self.roles, {'mvtec_ad': self.samples})
        self.assertEqual(first, second)
        query = first['episodes'][0]['queries']
        self.assertEqual(sum(s['label'] == 'normal' for s in query), 3)
        self.assertEqual(sum(s['label'] == 'anomaly' for s in query), 3)
        self.assertNotIn('cable/test/good/000.png', {s['image'] for s in query})

    def test_invalid_budget_or_unimplemented_views_are_rejected(self):
        for key, value in [('shots', [1, 1]), ('shots', [0]), ('seeds', [7, 7]), ('support_views', ['identity', 'flip'])]:
            config = copy.deepcopy(self.config); config[key] = value
            with self.assertRaises(ValueError):
                validate_config(config, self.roles)

    def test_degenerate_normal_cutoff_fails_instead_of_epsilon(self):
        with self.assertRaisesRegex(ValueError, 'Degenerate'):
            _positive_cutoff([0., 0.], 3.)
        self.assertEqual(_positive_cutoff([1., 3.], 3.), 5.)


if __name__ == '__main__':
    unittest.main()
