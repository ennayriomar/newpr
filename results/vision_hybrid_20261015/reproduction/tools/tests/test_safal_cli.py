"""Protocol checks for the full-model runner without expensive encoder loads."""
import copy
import unittest
from pathlib import Path

from safe_iad.safal_cli import build_manifest, validate_episode
from safe_iad.verify_dataset import Sample


class SAFALProtocolTests(unittest.TestCase):
    def setUp(self):
        self.lookup = {}
        for category in ('source', 'validation', 'final'):
            for i in range(25):
                image = f'{category}/train/good/{i}.png'
                self.lookup[image] = Sample(category, 'train', 'normal', image, None)
            for label in ('normal', 'anomaly'):
                for i in range(4):
                    image = f'{category}/test/{label}/{i}.png'
                    self.lookup[image] = Sample(category, 'test', label, image,
                                               f'{category}/mask/{i}.png' if label == 'anomaly' else None)
        self.config = dict(schema_version=1, shots=[1, 2, 4, 8], seeds=[5, 13], partition_seed=917,
                           normal_calibration_images=4, normal_calibration_quantile=.95,
                           queries_per_label=2, source_fit_parents=6, source_cal_parents=2,
                           abstain_error_probability=.2, source_categories={'mvtec_ad': ['source']},
                           validation_categories={'mvtec_ad': ['validation']},
                           category_roles={'mvtec_ad': {'meta_training': ['source'],
                                           'validation': ['validation'], 'final_test': ['final']}})
        self.inventories = {'mvtec_ad': (Path('/unused'), self.lookup)}

    def test_nested_shared_draws_and_globally_disjoint_extra_calibration(self):
        result = build_manifest(self.config, self.inventories)
        self.assertEqual(len(result['episodes']), 8)
        for seed in (5, 13):
            rows = [e for e in result['episodes'] if e['seed'] == seed]
            bank = rows[-1]['support_ids']
            for e in rows:
                self.assertEqual(e['support_ids'], bank[:e['shots']])
                self.assertEqual(e['query_ids'], rows[0]['query_ids'])
                self.assertEqual(e['k_plus_calibration'], e['shots']+4)
                self.assertFalse(e['strict_k_image_few_shot'])
                self.assertFalse(set(bank) & set(e['calibration_ids']))
        source = result['source_episodes'][0]
        groups = [set(source[k]) for k in ('support_ids', 'calibration_ids', 'fit_parent_ids', 'heldout_parent_ids')]
        self.assertEqual(sum(map(len, groups)), len(set.union(*groups)))

    def test_final_categories_cannot_fit_or_enter_demo(self):
        for key in ('source_categories', 'validation_categories'):
            bad = copy.deepcopy(self.config)
            bad[key]['mvtec_ad'] = ['final']
            with self.assertRaises(ValueError):
                build_manifest(bad, self.inventories)

    def test_rejects_query_leak_and_anomalous_support(self):
        episode = build_manifest(self.config, self.inventories)['episodes'][0]
        bad = copy.deepcopy(episode)
        bad['query_ids'][0] = bad['support_ids'][0]
        with self.assertRaises(ValueError):
            validate_episode(bad, self.lookup)
        bad = copy.deepcopy(episode)
        bad['support_ids'][0] = next(k for k, s in self.lookup.items() if s.category == 'validation' and s.label == 'anomaly')
        with self.assertRaises(ValueError):
            validate_episode(bad, self.lookup)

    def test_declared_budget_cannot_hide_extra_observations(self):
        bad = build_manifest(self.config, self.inventories)['episodes'][0]
        bad['k_plus_calibration'] = bad['shots']
        with self.assertRaises(ValueError):
            validate_episode(bad, self.lookup)


if __name__ == '__main__':
    unittest.main()
