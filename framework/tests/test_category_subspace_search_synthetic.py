"""Synthetic protocol tests for explicitly counted target normal calibration."""
import copy
import unittest

from safe_iad.run_category_subspace_search_pilot import build_manifest, validate_config
from safe_iad.verify_dataset import Sample


class TargetNormalCalibrationTests(unittest.TestCase):
    def setUp(self):
        self.roles = {'mvtec_ad': {'meta_training': ['source'], 'validation': ['cable'],
                                   'calibration': ['capsule'], 'final_test': ['bottle']}}
        self.config = dict(schema_version=1, scope='new_method_validation_pilot',
                           prototype='target_normal_calibrated_subspace_search',
                           calibration_mode='extra_target_normal_training_images', roots={'mvtec_ad': '/unused'},
                           validation_categories={'mvtec_ad': 'cable'}, calibration_categories={'mvtec_ad': 'cable'},
                           support_views=['identity'], map_storage_dtype='float16', shots=[1, 2, 4], seeds=[7, 11, 19],
                           queries_per_label=3, calibration_queries_per_draw=2, partition_seed=72,
                           calibration_standard_deviations=3., excluded_query_ids={'mvtec_ad': []})
        self.samples = [Sample('cable', 'train', 'normal', f'cable/train/good/{i:03}.png', None) for i in range(20)]
        self.samples += [Sample('cable', 'test', label, f'cable/test/{folder}/{i:03}.png',
                                f'cable/ground_truth/{i:03}.png' if label == 'anomaly' else None)
                         for label, folder in [('normal', 'good'), ('anomaly', 'bad')] for i in range(6)]

    def test_extra_target_normal_observations_are_counted_not_called_strict_k_shot(self):
        plan = build_manifest(self.config, self.roles, {'mvtec_ad': self.samples})
        for episode in plan['episodes']:
            self.assertFalse(episode['strict_k_image_few_shot'])
            self.assertEqual(episode['target_normal_calibration_images'], 2)
            self.assertEqual(episode['total_target_normal_observations_per_inspection'], episode['shots'] + 2)
            self.assertEqual(len(episode['support']), episode['shots'])

    def test_all_target_calibration_queries_are_train_normal_and_globally_excluded(self):
        plan = build_manifest(self.config, self.roles, {'mvtec_ad': self.samples})
        for episode in plan['episodes']:
            reserved = set(episode['all_reserved_calibration_query_ids'])
            self.assertFalse(reserved & {s['image'] for s in episode['support']})
            self.assertFalse(reserved & {s['image'] for s in episode['calibration_support']})
            self.assertEqual(episode['support'], episode['calibration_support'])
            self.assertTrue(all(s['split'] == 'train' and s['label'] == 'normal' for s in episode['calibration_queries']))
            self.assertFalse(reserved & {s['image'] for s in episode['queries']})

    def test_original_source_only_configuration_cannot_be_silently_reused(self):
        wrong = copy.deepcopy(self.config); wrong['calibration_mode'] = 'source_category_only'
        with self.assertRaisesRegex(ValueError, 'extra target-normal'):
            validate_config(wrong, self.roles)
        wrong = copy.deepcopy(self.config); wrong['calibration_categories']['mvtec_ad'] = 'capsule'
        with self.assertRaises(ValueError):
            validate_config(wrong, self.roles)

    def test_final_category_cannot_be_adapted_using_this_validation_protocol(self):
        wrong = copy.deepcopy(self.config)
        wrong['validation_categories']['mvtec_ad'] = wrong['calibration_categories']['mvtec_ad'] = 'bottle'
        with self.assertRaisesRegex(ValueError, 'reserved validation'):
            validate_config(wrong, self.roles)


if __name__ == '__main__':
    unittest.main()
