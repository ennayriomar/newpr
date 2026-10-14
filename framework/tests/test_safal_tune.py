import json
from pathlib import Path
import unittest

from safe_iad.safal_tune import parameter_grid, eligible, candidate_metrics, select_candidate
from safe_iad.safal_tunable import Parameters


class SelectionTests(unittest.TestCase):
    def test_declared_search_budget(self):
        config = json.loads((Path(__file__).parents[1]/'configs/safal_tuning_20261014.json').read_text())
        grid = parameter_grid(config)
        self.assertEqual(len(grid), 768)
        self.assertEqual(sum(eligible(p) for p in grid), 576)

    def test_per_case_constraint_rejects_equal_miss_swap(self):
        cases = [dict(label=v, episode_id='one') for v in [1, 1, 0, 0]]
        baselines = {'original': [2., .5, .2, .2], 'fixed_avg': [2., .5, .2, .2]}
        # Same miss count as baseline, but loses a previously detected defect.
        row = candidate_metrics(Parameters(), [.5, 2., .1, .1], cases, baselines, 'mixed224')
        self.assertFalse(row['feasible'])
        self.assertEqual(row['losses_vs_original'], 1)
        with self.assertRaises(ValueError):
            select_candidate([row])

    def test_control_cannot_win_and_feasible_accuracy_selects(self):
        cases = [dict(label=v, episode_id='one') for v in [1, 1, 0, 0]]
        baseline = {'original': [2., .5, .2, .2], 'fixed_avg': [2., .5, .2, .2]}
        good = candidate_metrics(Parameters(fusion='fixed'), [2., 2., .1, .1], cases, baseline, 'mixed224')
        control = candidate_metrics(Parameters(fusion='fixed', search_weight=1), [2., 2., .1, .1], cases, baseline, 'mixed224')
        bad = candidate_metrics(Parameters(), [.5, 2., .1, .1], cases, baseline, 'mixed224')
        self.assertEqual(select_candidate([control, bad, good]), good)


if __name__ == '__main__':
    unittest.main()
