"""Paired report arithmetic and provenance checks, not industrial evidence."""
import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from safe_iad.safal_tuning_report import build_tuning_report, write_tuning_report


class SafalTuningReportTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='safal_report_test_')
        self.addCleanup(self.temporary.cleanup)
        self.run = Path(self.temporary.name)
        (self.run/'development').mkdir()
        (self.run/'verification').mkdir()
        chosen = dict(id='hybrid', params={'image_threshold': .75, 'fusion': 'fixed',
                                          'search_weight': .5},
                      eligible=True, feasible=True, accuracy=.8, mean_image_auroc=.9,
                      misses=1, false_positives=2, losses_vs_original=0, losses_vs_fixed=0)
        endpoint = dict(chosen, id='pure_branch', eligible=False, accuracy=.9,
                        params={'image_threshold': .75, 'fusion': 'fixed', 'search_weight': 0.})
        unsafe = dict(chosen, id='unsafe', feasible=False, accuracy=.95,
                      losses_vs_original=1, losses_vs_fixed=1)
        self.grid = [chosen, endpoint, unsafe]
        self.lock = dict(stage1_winner=chosen, params=chosen['params'], feature={'id': 'synthetic'},
                         native_development_labels_used=True,
                         verification_scores_seen=False, verification_masks_seen=False)
        self.save_json(self.run/'development/grid.json', self.grid)
        self.save_json(self.run/'selection.lock.json', self.lock)
        self.rows = []
        # Twenty-four cases reuse eight query identities across three draws.
        # Controls have six false alarms and six misses each. Selected removes
        # all false alarms, recovers those six misses, but loses one old detection.
        for category in ('a', 'b'):
            for seed in (17, 29, 43):
                for query, label in enumerate((0, 0, 1, 1)):
                    for method in ('original', 'fixed_avg', 'selected'):
                        threshold = .75 if method == 'selected' else 1.
                        score = ((.1, .2, 1.5, .75)[query] if method == 'selected'
                                 else (.2, 1.1, 1.2, .8)[query])
                        if method == 'selected' and category == 'a' and seed == 17 and query == 2:
                            score = .6
                        decision = score >= threshold
                        self.rows.append(dict(dataset='synthetic', category=category, seed=seed,
                                              query_id=f'{category}/query-{query}', label=label,
                                              method=method, score=score, threshold=threshold,
                                              decision=decision, image_correct=decision == bool(label),
                                              shots=4, k_plus_calibration=8, probabilities=None))
        self.save_rows(self.rows)

    @staticmethod
    def save_json(path, value):
        path.write_text(json.dumps(value))

    def save_rows(self, rows):
        (self.run/'verification/predictions.jsonl').write_text(
            ''.join(json.dumps(row)+'\n' for row in rows))

    def report(self):
        return build_tuning_report(self.run, n_bootstrap=200, bootstrap_seed=11)

    def test_nonunit_threshold_boundary_counts_and_unique_queries(self):
        report = self.report()
        self.assertEqual(report['counts']['paired_cases'], 24)
        self.assertEqual(report['counts']['method_records'], 72)
        self.assertEqual(report['counts']['unique_queries'], 8)
        self.assertEqual(report['counts']['unique_anomalies'], 4)
        self.assertEqual(report['counts']['anomaly_cases'], 12)
        selected = report['methods']['selected']
        self.assertEqual((selected['tp'], selected['fp'], selected['fn'], selected['tn']), (11, 0, 1, 12))
        self.assertAlmostEqual(selected['accuracy'], 23/24)
        self.assertAlmostEqual(selected['macro_accuracy'], 23/24)
        self.assertEqual(selected['image_threshold'], .75)
        self.assertAlmostEqual(selected['missed_defect_rate'], 1/12)
        self.assertEqual(selected['false_alarm_rate'], 0.)
        for method in ('original', 'fixed_avg'):
            self.assertEqual(report['methods'][method]['accuracy'], .5)

    def test_paired_transitions_reconcile_and_crossed_ci_uses_queries_draws(self):
        report = self.report()
        for comparator in ('original', 'fixed_avg'):
            result = report['comparisons'][comparator]
            transitions = result['transitions']
            self.assertEqual(transitions['detected_to_missed']['records'], 1)
            self.assertEqual(transitions['detected_to_missed']['unique_queries'], 1)
            self.assertEqual(transitions['missed_to_detected']['records'], 6)
            self.assertEqual(transitions['missed_to_detected']['unique_queries'], 2)
            self.assertEqual(transitions['false_positives_removed']['records'], 6)
            self.assertEqual(transitions['false_positives_removed']['unique_queries'], 2)
            self.assertEqual(transitions['false_positives_added']['records'], 0)
            self.assertEqual(transitions['net_correct_records'], 11)
            ci = result['paired_accuracy']
            self.assertAlmostEqual(ci['estimate'], 11/24)
            self.assertAlmostEqual(ci['estimate'], transitions['pooled_accuracy_difference'])
            self.assertEqual(ci['resampling_units'], ['query_id', 'seed'])
            self.assertFalse(ci['categories_resampled'])
            self.assertFalse(ci['pixels_or_candidates_resampled'])
            self.assertEqual(len(ci['groups']), 2)
            for group in ci['groups']:
                self.assertEqual(group['unique_queries'], 4)
                self.assertEqual(group['support_draws'], 3)
                self.assertEqual(group['paired_rows'], 12)
                self.assertTrue(group['limited_replication'])
            self.assertLessEqual(ci['interval'][0], ci['estimate'])
            self.assertGreaterEqual(ci['interval'][1], ci['estimate'])
        self.assertEqual(report['comparisons'], self.report()['comparisons'])

    def test_endpoint_and_unsafe_candidates_are_counted_without_selecting_them(self):
        development = self.report()['development']
        self.assertEqual(development['candidate_count'], 3)
        self.assertEqual(development['eligible_count'], 2)
        self.assertEqual(development['feasible_count'], 2)
        self.assertEqual(development['eligible_feasible_count'], 1)
        self.assertEqual(development['best_eligible_feasible_accuracy'], .8)
        self.assertEqual(development['best_any_accuracy'], .95)
        self.assertEqual(development['locked_stage1_candidate']['id'], 'hybrid')
        unsafe_lock = dict(self.lock, stage1_winner=self.grid[2])
        self.save_json(self.run/'selection.lock.json', unsafe_lock)
        with self.assertRaisesRegex(ValueError, 'fails declared primary eligibility'):
            self.report()

    def test_missing_duplicate_methods_and_incomplete_crossed_grid_rejected(self):
        variations = [self.rows[:-1], self.rows+[copy.deepcopy(self.rows[0])],
                      [row for row in self.rows if not (row['category'] == 'a' and row['seed'] == 17
                                                        and row['query_id'] == 'a/query-0')]]
        for rows in variations:
            self.save_rows(rows)
            with self.subTest(rows=len(rows)), self.assertRaises(ValueError):
                self.report()

    def test_stale_probability_head_rejected_for_changed_detector(self):
        for name, value in [('error_probability', .1), ('probabilities', {'prediction_error': .1})]:
            rows = copy.deepcopy(self.rows)
            next(row for row in rows if row['method'] == 'selected')[name] = value
            self.save_rows(rows)
            with self.subTest(field=name), self.assertRaisesRegex(ValueError, 'old probability head'):
                self.report()

    def test_invalid_events_scores_and_recorded_correctness_rejected(self):
        changes = [('label', 2), ('image_correct', 2), ('score', float('nan')),
                   ('decision', not self.rows[0]['decision']),
                   ('image_correct', not self.rows[0]['image_correct'])]
        for key, value in changes:
            rows = copy.deepcopy(self.rows)
            rows[0][key] = value
            self.save_rows(rows)
            with self.subTest(field=key, value=value), self.assertRaises(ValueError):
                self.report()

    def test_paired_information_budget_and_lock_threshold_mismatch_rejected(self):
        for name, value in [('shots', 1), ('k_plus_calibration', 5)]:
            rows = copy.deepcopy(self.rows)
            rows[0][name] = value
            self.save_rows(rows)
            with self.subTest(field=name), self.assertRaisesRegex(ValueError, 'different'):
                self.report()
        self.save_rows(self.rows)
        changed = copy.deepcopy(self.lock)
        changed['params']['image_threshold'] = .5
        self.save_json(self.run/'selection.lock.json', changed)
        with self.assertRaisesRegex(ValueError, 'threshold differs from the lock'):
            self.report()

    def test_completion_counts_and_lock_hash_are_checked(self):
        completion = dict(unique_queries=8, paired_cases=24, method_rows=72,
                          selection_lock_sha256=hashlib.sha256((self.run/'selection.lock.json').read_bytes()).hexdigest(),
                          masks_used_for_selection=False)
        path = self.run/'verification/completion.json'
        self.save_json(path, completion)
        self.assertTrue(self.report()['audit']['verification_completion_crosschecked'])
        for field, value in [('paired_cases', 999), ('selection_lock_sha256', 'wrong'),
                             ('masks_used_for_selection', True)]:
            self.save_json(path, dict(completion, **{field: value}))
            with self.subTest(field=field), self.assertRaises(ValueError):
                self.report()

    def test_localization_is_recorded_not_invented_and_outputs_are_serializable(self):
        self.assertFalse(self.report()['localization']['available'])
        rows = [dict(dataset='synthetic', category=category, seed=seed, method=method,
                     localization={'pixel_ap': .4, 'au_pro': .5, 'iou': .2, 'pixel_f1': 1/3,
                                   'pixel_threshold': 1., 'au_pro_fpr_limit': .3})
                for category in ('a', 'b') for seed in (17, 29, 43)
                for method in ('original', 'fixed_avg', 'selected')]
        self.save_json(self.run/'verification/episode_metrics.json', rows)
        report = self.report()
        self.assertTrue(report['localization']['complete_episode_coverage'])
        self.assertAlmostEqual(report['methods']['selected']['localization']['au_pro']['mean'], .5)
        self.assertIsNone(report['methods']['selected']['localization']['pixel_auroc']['mean'])
        paths = write_tuning_report(self.run, n_bootstrap=100, bootstrap_seed=11)
        saved = json.loads(Path(paths['summary']).read_text())
        self.assertEqual(saved['counts'], report['counts'])
        markdown = Path(paths['report']).read_text()
        self.assertIn('0.7500', markdown)
        self.assertIn('post-selection', markdown)
        self.assertIn('not a fresh score-map/mask recomputation', markdown)


if __name__ == '__main__':
    unittest.main()
