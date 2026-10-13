"""Synthetic metric-definition tests; not real-data or performance evidence."""
import unittest

import numpy as np

from safe_iad.research_metrics import (
    defect_preservation, localization_metrics, paired_crossed_bootstrap,
    risk_coverage, thresholded_detection_metrics,
)


class SyntheticResearchMetricTests(unittest.TestCase):
    def test_detection_locked_cutoff_and_class_rates(self):
        result = thresholded_detection_metrics([0, 0, 1, 1], [.1, .7, .2, .8], .5)
        self.assertEqual((result['tp'], result['fp'], result['fn'], result['tn']), (1, 1, 1, 1))
        self.assertEqual(result['f1'], .5)
        self.assertEqual(result['missed_defect_rate'], .5)
        self.assertEqual(result['false_alarm_rate'], .5)
        self.assertEqual(result['threshold'], .5)

    def test_absent_class_metrics_are_null(self):
        result = thresholded_detection_metrics([0, 0], [.1, .2], .5)
        self.assertIsNone(result['missed_defect_rate'])
        self.assertIsNone(result['auroc'])
        self.assertIsNone(result['f1'])

    def test_perfect_and_reversed_au_pro_preserve_vertical_segments(self):
        truth = np.array([[1, 0], [0, 0]], dtype=bool)
        perfect = localization_metrics([truth], [truth.astype('float32')], .5)
        reverse = localization_metrics([truth], [(~truth).astype('float32')], .5)
        self.assertEqual(perfect['au_pro'], 1.)
        self.assertEqual(perfect['iou'], 1.)
        self.assertEqual(perfect['pixel_f1'], 1.)
        self.assertEqual(reverse['au_pro'], 0.)
        self.assertEqual(reverse['iou'], 0.)
        self.assertEqual(reverse['au_pro_curve'][-1]['fpr'], .3)

    def test_au_pro_equal_region_weight_and_boundary_interpolation(self):
        # A one-pixel region is detected; a three-pixel region is not. Equal
        # component weight gives PRO=.5, rather than pixel-weighted recall=.25.
        truth = np.array([[1, 0, 0, 1, 1, 1]], dtype=bool)
        score = np.array([[3., 2., 2., 0., 0., 0.]])
        result = localization_metrics([truth], [score], 2.5, fpr_limit=.3)
        self.assertEqual(result['au_pro_num_regions'], 2)
        self.assertAlmostEqual(result['au_pro'], .5)
        self.assertEqual(result['au_pro_connectivity'], 8)

    def test_localization_undefined_pro_and_invalid_inputs(self):
        result = localization_metrics([np.zeros((2, 2), bool)], [np.zeros((2, 2))], .5)
        self.assertIsNone(result['au_pro'])
        self.assertIsNone(result['iou'])
        with self.assertRaises(ValueError):
            localization_metrics([np.ones((2, 2), bool)], [np.zeros((2, 3))], .5)
        with self.assertRaises(ValueError):
            localization_metrics([np.ones((2, 2), bool)], [np.zeros((2, 2))], .5, fpr_limit=0)

    def test_preservation_reports_explained_away_defect_without_mutation(self):
        truth = np.array([[1, 0], [0, 0]], dtype=bool)
        before = truth.astype('float32')
        after = np.zeros((2, 2), dtype='float32')
        original_before, original_after = before.copy(), after.copy()
        result = defect_preservation(before, after, truth, .9, .1, .5, .5)
        self.assertTrue(result['detected_to_missed'])
        self.assertEqual(result['miss_transition'], 'detected_to_missed')
        self.assertEqual(result['defect_region_score_drop'], 1.)
        self.assertEqual(result['iou_change'], -1.)
        np.testing.assert_array_equal(before, original_before)
        np.testing.assert_array_equal(after, original_after)

    def test_risk_coverage_right_step_and_unfavorable_tie_order_ignored(self):
        result = risk_coverage([0, 1], [.9, .1])
        self.assertEqual(result['aurc'], .25)
        self.assertEqual(result['error_detection_auroc'], 1.)
        tie_a = risk_coverage([0, 1], [.5, .5])
        tie_b = risk_coverage([1, 0], [.5, .5])
        self.assertEqual(tie_a, tie_b)
        self.assertEqual(tie_a['aurc'], .5)
        self.assertEqual(len(tie_a['curve']), 2)
        self.assertIsNone(risk_coverage([0, 0], [.9, .1])['error_detection_auroc'])

    def test_crossed_bootstrap_is_paired_deterministic_and_category_conditional(self):
        records = [dict(dataset='d', category='a', query_id=q, seed=s, paired_difference=2.)
                   for q in ['q1', 'q2'] for s in [0, 1]]
        records += [dict(dataset='d', category='b', query_id=q, seed=s, paired_difference=4.)
                    for q in ['q1', 'q2', 'q3'] for s in [0, 1, 2]]
        first = paired_crossed_bootstrap(records, n_bootstrap=50, seed=7)
        self.assertEqual(first, paired_crossed_bootstrap(records, n_bootstrap=50, seed=7))
        self.assertEqual(first['estimate'], 3.)
        self.assertEqual(first['interval'], [3., 3.])
        self.assertFalse(first['categories_resampled'])
        self.assertFalse(first['pixels_or_candidates_resampled'])

    def test_crossed_bootstrap_resamples_shared_support_and_shared_query(self):
        records = [dict(dataset='d', category='a', query_id=q, seed=s, paired_difference=value)
                   for q, s, value in [('q1', 0, 0.), ('q1', 1, 2.), ('q2', 0, 4.), ('q2', 1, 6.)]]
        result = paired_crossed_bootstrap(records, n_bootstrap=500, seed=1)
        self.assertEqual(result['estimate'], 3.)
        self.assertLess(result['interval'][0], 3.)
        self.assertGreater(result['interval'][1], 3.)
        self.assertEqual(result['groups'][0]['support_draws'], 2)
        self.assertEqual(result['groups'][0]['unique_queries'], 2)

    def test_bootstrap_rejects_candidate_duplicates_and_incomplete_crossing(self):
        row = dict(dataset='d', category='a', query_id='q', seed=0, paired_difference=1.)
        with self.assertRaisesRegex(ValueError, 'Duplicate'):
            paired_crossed_bootstrap([row, row], n_bootstrap=10)
        with self.assertRaisesRegex(ValueError, 'complete'):
            paired_crossed_bootstrap([row, row | dict(query_id='q2', seed=1)], n_bootstrap=10)

    def test_binary_finite_validation(self):
        with self.assertRaises(ValueError):
            thresholded_detection_metrics([0, 2], [.1, .2], .5)
        with self.assertRaises(ValueError):
            risk_coverage([0, 1], [.1, np.nan])


if __name__ == '__main__':
    unittest.main()
