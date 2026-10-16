"""Scientific reporting checks against direct duplicated-image metrics."""
import unittest

import numpy as np
from sklearn.metrics import roc_auc_score

from audit_outputs import (pro_from_weights, pro_statistics, select_cases,
                           stratified_weights, weighted_auroc)
from utils import use_local_framework

use_local_framework()
from safe_iad.research_metrics import localization_metrics


class AuditTests(unittest.TestCase):
    def test_pro_image_multiplicities_match_direct_duplicate_images(self):
        # Unequal connected-region counts/sizes and tied native scores exercise
        # region weighting, normal-pixel pooling and vertical FPR segments.
        truths = [np.zeros((4, 5), np.uint8),
                  np.array([[1, 0, 0, 0, 1], [1, 0, 0, 0, 0],
                            [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], np.uint8),
                  np.array([[0, 0, 1, 1, 0], [0, 0, 1, 0, 0],
                            [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]], np.uint8)]
        rng = np.random.default_rng(42)
        maps = [rng.integers(0, 5, size=t.shape).astype(np.float32) for t in truths]
        stats = pro_statistics(truths, maps, max_thresholds=128)
        weights = np.array([[1, 1, 1], [3, 2, 1], [1, 0, 3]])
        before = [s.copy() for s in maps]
        for weight, actual in zip(weights, pro_from_weights(stats, weights)):
            indices = np.repeat(np.arange(3), weight)
            expected = localization_metrics([truths[i] for i in indices],
                                            [maps[i] for i in indices], 2., max_thresholds=128)
            self.assertAlmostEqual(actual, expected["au_pro"], places=12)
        for score, original in zip(maps, before):
            np.testing.assert_array_equal(score, original)

    def test_pro_preserves_vertical_segments_and_rejects_empty_replicates(self):
        truths = [np.array([[0, 0], [1, 1]], np.uint8)]
        perfect = pro_statistics(truths, [np.array([[0., 0.], [1., 1.]])])
        reverse = pro_statistics(truths, [np.array([[1., 1.], [0., 0.]])])
        self.assertAlmostEqual(pro_from_weights(perfect, [1])[0], 1.)
        self.assertAlmostEqual(pro_from_weights(reverse, [1])[0], 0.)
        with self.assertRaises(ValueError):pro_from_weights(perfect, [0])
        with self.assertRaises(ValueError):pro_from_weights(perfect, [-1])

    def test_paired_stratified_image_bootstrap_and_exact_auc_with_ties(self):
        labels, scores = np.array([0, 0, 1, 1, 1]), np.array([.1, .5, .5, .2, .8])
        weights = stratified_weights(labels, 40, 123)
        np.testing.assert_array_equal(weights, stratified_weights(labels, 40, 123))
        np.testing.assert_array_equal(weights[:, :2].sum(axis=1), 2)
        np.testing.assert_array_equal(weights[:, 2:].sum(axis=1), 3)
        for weight, actual in zip(weights, weighted_auroc(labels, scores, weights)):
            indices = np.repeat(np.arange(5), weight)
            self.assertAlmostEqual(actual, roc_auc_score(labels[indices], scores[indices]))
        with self.assertRaises(ValueError):stratified_weights([1, 1], 4, 1)

    def test_selection_is_stable_includes_failures_and_does_not_invent_misses(self):
        rows = [dict(sample_id="normal-b", label=0, hybrid_score=.2, truth_pixels=0, hybrid_pixel_iou=None),
                dict(sample_id="normal-a", label=0, hybrid_score=.2, truth_pixels=0, hybrid_pixel_iou=None),
                dict(sample_id="false-alarm", label=0, hybrid_score=2., truth_pixels=0, hybrid_pixel_iou=None),
                dict(sample_id="small", label=1, hybrid_score=1.5, truth_pixels=1, hybrid_pixel_iou=.6),
                dict(sample_id="large", label=1, hybrid_score=1.8, truth_pixels=10, hybrid_pixel_iou=.1)]
        selected = select_cases(rows, 1.)
        self.assertEqual(selected, select_cases(list(reversed(rows)), 1.))
        self.assertEqual(selected["true_negative"], "normal-a")
        self.assertEqual(selected["false_positive"], "false-alarm")
        self.assertEqual(selected["smallest_defect"], "small")
        self.assertEqual(selected["localization_failure"], "large")
        self.assertIsNone(selected["miss"])
        rows[-1]["hybrid_score"] = .9
        self.assertEqual(select_cases(rows, 1.)["miss"], "large")


if __name__ == "__main__":
    unittest.main()
