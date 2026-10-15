"""Synthetic missing-support partition tests; no real benchmark evidence."""
import json
import unittest

import numpy as np

from safe_iad.missing_support import missing_support_plan


class SyntheticMissingSupportTests(unittest.TestCase):
    def examples(self):
        ids = [f'category/train/good/{index:03d}.png' for index in range(18)]
        centers = np.asarray([[1., 0., 0.], [0., 1., 0.], [0., 0., 1.]])
        features = np.asarray([centers[index // 6] + np.asarray([.003 * index, .002 * index, .001])
                               for index in range(18)])
        return ids, features

    def test_synthetic_groups_omitted_without_query_reference_overlap(self):
        ids, features = self.examples()
        plan = missing_support_plan(ids, features, 9, shots=2, pool_size=8)
        support, candidate, query = [set(plan[key]) for key in
                                     ['initial_support_ids', 'candidate_ids', 'query_ids']]
        self.assertEqual((len(support), len(candidate), len(query)), (2, 8, 2))
        self.assertFalse(support & candidate or support & query or candidate & query)
        assignments, omitted = plan['cluster_assignments'], plan['omitted_group']
        self.assertTrue(all(assignments[identifier] != omitted for identifier in support))
        self.assertTrue(all(assignments[identifier] == omitted for identifier in query))
        self.assertTrue(any(assignments[identifier] == omitted for identifier in candidate))
        self.assertEqual(set(assignments), set(ids))
        self.assertEqual(plan['grouping_provenance']['global_feature_vectors_scanned'], len(ids))
        self.assertIn('proxy appearance groups', plan['grouping_provenance']['limitation'])
        json.dumps(plan)

    def test_synthetic_plan_repeats_and_ignores_input_enumeration_order(self):
        ids, features = self.examples()
        before = features.copy()
        plan = missing_support_plan(ids, features, 123)
        self.assertEqual(plan, missing_support_plan(ids, features, 123))
        self.assertEqual(plan, missing_support_plan(ids[::-1], features[::-1], 123))
        np.testing.assert_array_equal(features, before)

    def test_synthetic_minimal_one_reference_pool_has_omitted_group_reference(self):
        ids, features = self.examples()
        plan = missing_support_plan(ids, features, 2, pool_size=1)
        self.assertEqual(len(plan['candidate_ids']), 1)
        self.assertEqual(plan['cluster_assignments'][plan['candidate_ids'][0]], plan['omitted_group'])

    def test_synthetic_matched_control_changes_one_reference_at_nested_k1_k2(self):
        ids, features = self.examples()
        plan = missing_support_plan(ids, features, 9, shots=2, pool_size=8,
                                    with_control=True)
        omitted = plan['initial_support_ids']
        covered = plan['covered_support_ids']
        self.assertEqual(covered[1:], omitted[1:])
        self.assertNotEqual(covered[0], omitted[0])
        self.assertEqual(sum(a != b for a, b in zip(omitted, covered)), 1)
        assignments, group = plan['cluster_assignments'], plan['omitted_group']
        for shots in [1, 2]:
            self.assertEqual(len(omitted[:shots]), len(covered[:shots]))
            self.assertTrue(all(assignments[identifier] != group for identifier in omitted[:shots]))
            self.assertEqual(assignments[covered[:shots][0]], group)
        reference_union = set(omitted + covered)
        candidate, query = set(plan['candidate_ids']), set(plan['query_ids'])
        self.assertFalse(reference_union & candidate or reference_union & query or candidate & query)
        self.assertEqual(len(candidate), 8)
        self.assertTrue(any(assignments[identifier] == group for identifier in candidate))
        self.assertTrue(all(assignments[identifier] == group for identifier in query))
        control = plan['grouping_provenance']['matched_coverage_control']
        self.assertEqual(control['changed_support_positions'], [0])
        self.assertEqual(control['support_count_per_condition'], 2)
        self.assertTrue(control['same_query_ids'] and control['same_candidate_pool'])
        self.assertEqual(plan, missing_support_plan(ids[::-1], features[::-1], 9,
                                                    shots=2, pool_size=8, with_control=True))

    def test_synthetic_control_reserves_a_reference_without_changing_default_api(self):
        ids, features = self.examples()
        default = missing_support_plan(ids, features, 2, pool_size=1)
        self.assertNotIn('covered_support_ids', default)
        self.assertNotIn('matched_coverage_control', default['grouping_provenance'])
        self.assertEqual(default, missing_support_plan(ids, features, 2, pool_size=1,
                                                       with_control=False))
        controlled = missing_support_plan(ids, features, 2, pool_size=1, with_control=True)
        self.assertEqual(len(controlled['covered_support_ids']), 1)
        self.assertNotIn(controlled['covered_support_ids'][0], controlled['candidate_ids'])
        with self.assertRaisesRegex(ValueError, 'No feature group'):
            missing_support_plan(ids, features, 0, pool_size=1, queries_per_group=5,
                                 with_control=True)
        with self.assertRaisesRegex(ValueError, 'with_control'):
            missing_support_plan(ids, features, 0, with_control=1)

    def test_synthetic_insufficient_partition_and_degenerate_groups_rejected(self):
        ids, features = self.examples()
        with self.assertRaisesRegex(ValueError, 'Insufficient'):
            missing_support_plan(ids[:4], features[:4], 0)
        with self.assertRaisesRegex(ValueError, 'distinct'):
            missing_support_plan(ids, np.ones_like(features), 0)
        with self.assertRaisesRegex(ValueError, 'No feature group'):
            missing_support_plan(ids, features, 0, queries_per_group=6)

    def test_synthetic_duplicate_ids_and_invalid_feature_matrices_rejected(self):
        ids, features = self.examples()
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            missing_support_plan([ids[0]] + ids[:-1], features, 0)
        for invalid in [features[:-1], features.ravel(), np.full_like(features, np.nan),
                        np.zeros_like(features), np.full_like(features, np.inf)]:
            with self.subTest(shape=invalid.shape), self.assertRaises(ValueError):
                missing_support_plan(ids, invalid, 0)

    def test_synthetic_recognizable_native_test_and_anomaly_paths_rejected(self):
        ids, features = self.examples()
        for forbidden in ['test/good', 'test_public/good', 'test_private/good',
                          'validation/good', 'Data/Images/Anomaly']:
            with self.subTest(path=forbidden), self.assertRaisesRegex(ValueError, 'training images only'):
                missing_support_plan([f'category/{forbidden}/000.png'] + ids[1:], features, 0)

    def test_synthetic_invalid_budgets_and_label_input_rejected(self):
        ids, features = self.examples()
        for kwargs in [{'shots': 0}, {'pool_size': 0}, {'queries_per_group': 0},
                       {'clusters': 1}, {'shots': True}, {'pool_size': 1.5}]:
            with self.subTest(kwargs=kwargs), self.assertRaises(ValueError):
                missing_support_plan(ids, features, 0, **kwargs)
        for seed in [-1, True, 2 ** 32]:
            with self.subTest(seed=seed), self.assertRaises(ValueError):
                missing_support_plan(ids, features, seed)
        with self.assertRaises(TypeError):
            missing_support_plan(ids, features, 0, query_labels=np.zeros(len(ids)))


if __name__ == '__main__':
    unittest.main()
