"""Report a frozen development-selected detector on paired held-out images.

This module fits nothing and never chooses parameters. Image decisions and
correctness are recomputed from recorded raw scores and method-specific locked
thresholds. Bootstrap units are paired original queries and support draws.
"""
import argparse
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path

import numpy as np

from .research_metrics import paired_crossed_bootstrap, thresholded_detection_metrics


METHODS = ('original', 'fixed_avg', 'selected')
PIXEL_METRICS = ('pixel_auroc', 'pixel_ap', 'au_pro', 'iou', 'pixel_f1')
PAIR_FIELDS = ('shots', 'support_count', 'calibration_count', 'k_plus_calibration',
               'support_ids', 'calibration_ids')


def _read_json(path):
    return json.loads(Path(path).read_text())


def _read_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def _binary(value, name):
    if isinstance(value, (bool, int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str) and value in ('normal', 'good', 'anomaly', 'defective'):
        return value in ('anomaly', 'defective')
    raise ValueError(f'{name} must be a binary event, not {value!r}.')


def _number(value, name):
    if isinstance(value, bool):
        raise ValueError(f'{name} must be a finite number.')
    try:
        result = float(value)
    except (TypeError, ValueError) as error:
        raise ValueError(f'{name} must be a finite number.') from error
    if not math.isfinite(result):
        raise ValueError(f'{name} must be a finite number.')
    return result


def _mean(values):
    values = [value for value in values if value is not None]
    return float(np.mean(values)) if values else None


def _macro(episode_rows, name):
    groups = defaultdict(list)
    for row in episode_rows:
        groups[(row['dataset'], row['category'])].append(row.get(name))
    return _mean([_mean(values) for values in groups.values()])


def _identity(row):
    identifiers = [row.get(name) for name in ('dataset', 'category', 'query_id', 'seed')]
    if any(value is None or str(value) == '' for value in identifiers):
        raise ValueError('Every row needs nonempty dataset/category/query_id/seed.')
    return str(identifiers[0]), str(identifiers[1]), str(identifiers[2]), str(identifiers[3])


def _query_name(key):
    return ':'.join(key[:3])


def _validated_cases(rows):
    cases = defaultdict(dict)
    labels, thresholds = {}, defaultdict(set)
    for original_row in rows:
        row = dict(original_row)
        method = row.get('method')
        if method not in METHODS:
            raise ValueError(f'Unknown method {method!r}; expected {METHODS}.')
        key = _identity(row)
        if method in cases[key]:
            raise ValueError('Duplicate query/support/method record.')
        row['label'] = _binary(row.get('label'), 'label')
        row['score'] = _number(row.get('score', row.get('image_score')), 'score')
        row['threshold'] = _number(row.get('threshold'), 'threshold')
        row['decision'] = row['score'] >= row['threshold']
        if _binary(original_row.get('decision'), 'decision') != row['decision']:
            raise ValueError('Recorded decision contradicts score>=threshold.')
        row['image_correct'] = row['decision'] == row['label']
        if _binary(original_row.get('image_correct'), 'image_correct') != row['image_correct']:
            raise ValueError('Recorded image_correct contradicts the raw decision.')
        if method == 'selected' and any(row.get(name) is not None for name in ('error_probability', 'probabilities')):
            raise ValueError('Changed selected detector must not reuse the old probability head.')
        if key[:3] in labels and labels[key[:3]] != row['label']:
            raise ValueError('A query label changes across support draws or methods.')
        labels[key[:3]] = row['label']
        thresholds[method].add(row['threshold'])
        cases[key][method] = row
    if not cases or any(set(case) != set(METHODS) for case in cases.values()):
        raise ValueError('Every query/support case must contain all three paired methods.')
    if any(len(values) != 1 for values in thresholds.values()):
        raise ValueError('Each method must have one globally locked image threshold.')
    for case in cases.values():
        for name in PAIR_FIELDS:
            present = [name in case[method] for method in METHODS]
            if any(present) and not all(present):
                raise ValueError(f'Paired methods inconsistently declare {name}.')
            if all(present) and any(case[method][name] != case['original'][name] for method in METHODS):
                raise ValueError(f'Paired methods have different {name}.')
    # An original query must be present for every support draw in its category.
    # The bootstrap independently resamples these complete grids within strata.
    grids = defaultdict(lambda: defaultdict(set))
    for dataset, category, query, support in cases:
        grids[(dataset, category)][support].add(query)
    for by_support in grids.values():
        sets = list(by_support.values())
        if any(values != sets[0] for values in sets[1:]):
            raise ValueError('Each category must have a complete query x support grid.')
    return dict(cases), {method: next(iter(values)) for method, values in thresholds.items()}


def _detection(rows):
    threshold = rows[0]['threshold']
    metric = thresholded_detection_metrics([row['label'] for row in rows],
                                           [row['score'] for row in rows], threshold)
    return {
        'records': len(rows), 'correct': metric['tp'] + metric['tn'],
        'accuracy': (metric['tp'] + metric['tn']) / len(rows),
        'tp': metric['tp'], 'fp': metric['fp'], 'fn': metric['fn'], 'tn': metric['tn'],
        'missed_defect_rate': metric['missed_defect_rate'],
        'false_alarm_rate': metric['false_alarm_rate'],
        'image_f1': metric['f1'], 'image_auroc': metric['auroc'], 'image_ap': metric['ap'],
        'image_threshold': threshold,
    }


def _episode_metrics(cases):
    grouped = defaultdict(list)
    for key, case in cases.items():
        for method in METHODS:
            grouped[(key[0], key[1], key[3], method)].append(case[method])
    return [dict(dataset=dataset, category=category, seed=seed, method=method,
                 **_detection(rows))
            for (dataset, category, seed, method), rows in sorted(grouped.items())]


def _localization(run, episodes):
    paths = [run/'verification'/name for name in
             ('episode_metrics.json', 'episodes.json', 'metrics.json')]
    path = next((path for path in paths if path.is_file()), None)
    if path is None:
        return {'available': False, 'source': None,
                'semantics': 'No saved per-episode localization metrics supplied; none invented.'}
    content = _read_json(path)
    rows = content if isinstance(content, list) else content.get('episodes', content.get('rows'))
    if not isinstance(rows, list):
        raise ValueError(f'{path} must contain a list of per-episode metric rows.')
    expected = {(row['dataset'], row['category'], str(row['seed']), row['method']) for row in episodes}
    seen, result = set(), []
    for row in rows:
        if row.get('method') not in METHODS:
            continue
        key = (str(row['dataset']), str(row['category']), str(row['seed']), row['method'])
        metrics = row.get('localization_metrics', row.get('localization', row))
        supplied = {name: metrics.get(name) for name in PIXEL_METRICS if name in metrics}
        if not supplied:
            continue
        if key not in expected or key in seen:
            raise ValueError('Localization row has a duplicate or unpaired episode identity.')
        seen.add(key)
        result.append(dict(dataset=key[0], category=key[1], seed=key[2], method=key[3],
                           **{name: None if value is None else _number(value, name)
                              for name, value in supplied.items()},
                           metric_metadata={name: metrics[name] for name in (
                               'pixel_threshold', 'pixels', 'images', 'overlap_aggregation',
                               'au_pro_fpr_limit', 'au_pro_connectivity', 'au_pro_semantics',
                               'au_pro_threshold_sampling', 'au_pro_threshold_count') if name in metrics}))
    return {'available': bool(result), 'source': str(path), 'episode_rows': result,
            'complete_episode_coverage': seen == expected,
            'semantics': 'Saved per-episode metrics, equal episode mean; no map/mask replay by this report.'}


def _grid_summary(run, lock):
    content = _read_json(run/'development'/'grid.json')
    candidates = content if isinstance(content, list) else content.get('candidates', content.get('grid'))
    if not isinstance(candidates, list) or not candidates:
        raise ValueError('development/grid.json must contain nonempty candidate rows.')
    ids = set()
    for row in candidates:
        identifier = str(row['id'])
        if identifier in ids:
            raise ValueError('Duplicate development candidate ID.')
        ids.add(identifier)
        for name in ('eligible', 'feasible'):
            if not isinstance(row.get(name), bool):
                raise ValueError(f'Development {name} must be a declared boolean.')
        if not isinstance(row.get('params'), dict):
            raise ValueError('Each development candidate needs its parameter dictionary.')
        if row.get('accuracy') is None:
            raise ValueError('Each development candidate needs measured accuracy.')
        for name in ('accuracy', 'mean_image_auroc'):
            if row.get(name) is not None:
                value = _number(row[name], name)
                if not 0 <= value <= 1:
                    raise ValueError(f'Development {name} outside [0,1].')
                row[name] = value
        for name in ('misses', 'false_positives', 'losses_vs_original', 'losses_vs_fixed'):
            value = _number(row.get(name), name)
            if value < 0 or int(value) != value:
                raise ValueError(f'Development {name} must be a nonnegative event count.')
            row[name] = int(value)
        if row['feasible'] and (row['losses_vs_original'] or row['losses_vs_fixed']):
            raise ValueError('Feasible development candidate has a detected-to-missed loss.')
    primary = [row for row in candidates if row['eligible'] and row['feasible']]
    if not primary:
        raise ValueError('No eligible preservation-feasible development candidate was recorded.')
    winner = lock.get('stage1_winner', lock.get('winner', {}))
    winner_id = lock.get('stage1_winner_id', winner.get('id') if isinstance(winner, dict) else winner)
    selected_candidate = next((row for row in candidates if str(row['id']) == str(winner_id)), None)
    if winner_id is not None and selected_candidate is None:
        raise ValueError('Locked stage1 candidate ID is absent from the development grid.')
    if selected_candidate is not None and not (selected_candidate['eligible'] and selected_candidate['feasible']):
        raise ValueError('Locked stage1 candidate fails declared primary eligibility or preservation.')
    return {'candidate_count': len(candidates), 'eligible_count': sum(row['eligible'] for row in candidates),
            'feasible_count': sum(row['feasible'] for row in candidates),
            'eligible_feasible_count': len(primary),
            'best_eligible_feasible_accuracy': max(row['accuracy'] for row in primary),
            'best_any_accuracy': max(row['accuracy'] for row in candidates),
            'locked_stage1_candidate': selected_candidate,
            'selection_lock': lock,
            'selection_scope': 'Native development labels selected parameters and image threshold; development estimates are post-selection.'}


def _transitions(cases, comparator):
    groups = {name: [] for name in ('detected_to_missed', 'missed_to_detected',
                                   'false_positives_removed', 'false_positives_added')}
    paired = []
    for key, case in sorted(cases.items()):
        before, after = case[comparator], case['selected']
        if after['label']:
            if before['decision'] and not after['decision']:
                groups['detected_to_missed'].append(key)
            elif not before['decision'] and after['decision']:
                groups['missed_to_detected'].append(key)
        elif before['decision'] and not after['decision']:
            groups['false_positives_removed'].append(key)
        elif not before['decision'] and after['decision']:
            groups['false_positives_added'].append(key)
        paired.append(dict(dataset=key[0], category=key[1], query_id=key[2], seed=key[3],
                           paired_difference=int(after['image_correct']) - int(before['image_correct'])))
    totals = {name: {'records': len(keys), 'unique_queries': len({_query_name(key) for key in keys}),
                     'query_ids': sorted({_query_name(key) for key in keys})}
              for name, keys in groups.items()}
    net = (len(groups['false_positives_removed']) - len(groups['false_positives_added'])
           + len(groups['missed_to_detected']) - len(groups['detected_to_missed']))
    if net != sum(row['paired_difference'] for row in paired):
        raise ValueError('Paired error transitions fail correctness reconciliation.')
    totals.update(net_correct_records=net, pooled_accuracy_difference=net/len(cases),
                  interpretation='Query/support records recur; unique lost/gained query sets may overlap across draws.')
    return totals, paired


def build_tuning_report(run_dir, *, n_bootstrap=2000, bootstrap_seed=20261014):
    """Return audited JSON data; no parameter or inference code is executed."""
    run = Path(run_dir)
    predictions_path = run/'verification'/'predictions.jsonl'
    lock = _read_json(run/'selection.lock.json')
    lock_hash = hashlib.sha256((run/'selection.lock.json').read_bytes()).hexdigest()
    if lock.get('verification_scores_seen') or lock.get('verification_masks_seen'):
        raise ValueError('Selection lock declares verification scores or masks were seen.')
    if lock.get('native_development_labels_used') is False:
        raise ValueError('Development search must acknowledge native label-based selection.')
    rows = _read_rows(predictions_path)
    cases, thresholds = _validated_cases(rows)
    for row in rows:
        if row.get('selection_lock_sha256') not in (None, lock_hash):
            raise ValueError('Prediction row refers to a different selection lock.')
        if row['method'] == 'selected' and 'parameters_id' in row and 'parameters_id' in lock:
            if row['parameters_id'] != lock['parameters_id']:
                raise ValueError('Selected prediction refers to different locked parameters.')
    if isinstance(lock.get('params'), dict) and 'image_threshold' in lock['params']:
        if thresholds['selected'] != _number(lock['params']['image_threshold'], 'locked image threshold'):
            raise ValueError('Selected decision threshold differs from the lock.')
    episodes = _episode_metrics(cases)
    localization = _localization(run, episodes)
    methods, categories = {}, []
    for method in METHODS:
        method_rows = [case[method] for case in cases.values()]
        metric = _detection(method_rows)
        # Pooled score ranking is deliberately not reported: category cutoffs
        # normalize different distributions. Episode rankings are comparable.
        metric.pop('image_auroc'); metric.pop('image_ap')
        method_episodes = [row for row in episodes if row['method'] == method]
        metric.update(macro_accuracy=_macro(method_episodes, 'accuracy'),
                      mean_image_auroc=_macro(method_episodes, 'image_auroc'),
                      mean_image_ap=_macro(method_episodes, 'image_ap'),
                      ranking_episode_count=len(method_episodes),
                      valid_auroc_episodes=sum(row['image_auroc'] is not None for row in method_episodes),
                      valid_ap_episodes=sum(row['image_ap'] is not None for row in method_episodes))
        if localization['available']:
            saved = [row for row in localization['episode_rows'] if row['method'] == method]
            metric['localization'] = {name: {'mean': _macro(saved, name),
                                            'valid_episodes': sum(row.get(name) is not None for row in saved)}
                                      for name in PIXEL_METRICS}
        methods[method] = metric
    for dataset, category in sorted({key[:2] for key in cases}):
        category_cases = {key: value for key, value in cases.items() if key[:2] == (dataset, category)}
        for method in METHODS:
            metric = _detection([case[method] for case in category_cases.values()])
            metric.pop('image_auroc'); metric.pop('image_ap')
            relevant = [row for row in episodes if (row['dataset'], row['category'], row['method']) == (dataset, category, method)]
            categories.append(dict(dataset=dataset, category=category, method=method,
                                   mean_image_auroc=_mean([row['image_auroc'] for row in relevant]),
                                   mean_image_ap=_mean([row['image_ap'] for row in relevant]), **metric))
    comparisons = {}
    for offset, comparator in enumerate(('original', 'fixed_avg')):
        transitions, paired = _transitions(cases, comparator)
        interval = paired_crossed_bootstrap(paired, n_bootstrap=n_bootstrap,
                                            seed=bootstrap_seed+offset)
        comparisons[comparator] = {'transitions': transitions, 'paired_accuracy': interval}
    query_labels = {key[:3]: case['selected']['label'] for key, case in cases.items()}
    unique_queries = len(query_labels)
    anomaly_records = sum(case['selected']['label'] for case in cases.values())
    strata = []
    for dataset, category in sorted({key[:2] for key in cases}):
        keys = [key for key in cases if key[:2] == (dataset, category)]
        strata.append(dict(dataset=dataset, category=category, unique_queries=len({key[2] for key in keys}),
                           support_draws=len({key[3] for key in keys}), paired_cases=len(keys)))
    evidence_paths = [predictions_path, run/'development'/'grid.json', run/'selection.lock.json']
    completion_path = run/'verification'/'completion.json'
    completion_checked = False
    if completion_path.is_file():
        completion = _read_json(completion_path)
        expected = {'unique_queries': unique_queries, 'paired_cases': len(cases), 'method_rows': len(rows)}
        for name, value in expected.items():
            if name in completion and completion[name] != value:
                raise ValueError(f'Verification completion count {name} differs from predictions.')
        if completion.get('selection_lock_sha256') not in (None, lock_hash):
            raise ValueError('Verification completion refers to a different selection lock.')
        if completion.get('masks_used_for_selection'):
            raise ValueError('Verification completion declares mask-based selection.')
        completion_checked = True
        evidence_paths.append(completion_path)
    if localization['source']:
        evidence_paths.append(Path(localization['source']))
    return {'schema_version': 1, 'run_dir': str(run),
            'counts': {'method_records': len(rows), 'paired_cases': len(cases),
                       'unique_queries': unique_queries, 'anomaly_cases': anomaly_records,
                       'normal_cases': len(cases)-anomaly_records,
                       'unique_anomalies': sum(query_labels.values()),
                       'unique_normals': unique_queries-sum(query_labels.values()), 'strata': strata},
            'thresholds': thresholds, 'methods': methods, 'category_metrics': categories,
            'episode_detection_metrics': episodes, 'comparisons': comparisons,
            'development': _grid_summary(run, lock), 'localization': localization,
            'declared_information_budgets': {name: [json.loads(value) for value in sorted({
                json.dumps(case['original'].get(name), sort_keys=True) for case in cases.values()})]
                for name in ('shots', 'support_count', 'calibration_count', 'k_plus_calibration')},
            'input_sha256': {str(path): hashlib.sha256(path.read_bytes()).hexdigest() for path in evidence_paths},
            'audit': {'paired_methods_complete': True, 'query_support_grids_complete': True,
                      'decisions_and_correctness_recomputed': True, 'paired_transition_counts_reconciled': True,
                      'selected_old_probability_head_reused': False,
                      'verification_completion_crosschecked': completion_checked,
                      'locked_before_verification_independently_proven_by_report': False},
            'caveats': [
                'Finite development search used native labels to select parameters and image threshold; development accuracy is post-selection.',
                'Verification checks new image IDs within previously development-exposed categories, not an unseen-category or pristine global benchmark.',
                'Accuracy reflects the observed normal/anomaly mixture; balanced sampling is not industrial defect prevalence.',
                'Queries recur across support draws. Method records, draws, pixels and candidates are not independent query samples.',
                'Intervals resample paired query IDs and support draws independently within fixed categories; few support draws limit reliability.',
                'Only additive paired correctness differences receive intervals. AUROC/AP are descriptive within-category/seed means.',
                'Zero development detection losses do not guarantee preservation on verification images or future defects.',
                'The prior error-probability head is omitted after changing the detector. No probability calibration or abstention claim is made.',
                'This reporting pass neither verifies lock chronology nor retrains or changes parameters; separate provenance must establish the lock.',
                'No GPU speed, full-benchmark superiority, SOTA or production guarantee is established.',
            ]}


def _fmt(value, percent=False):
    if value is None:
        return '—'
    return f'{100*value:.2f}%' if percent else f'{value:.4f}'


def _markdown(summary):
    counts, dev = summary['counts'], summary['development']
    lines = ['# Development-selected SAFAL verification', '',
             f"The locked comparison contains {counts['unique_queries']} unique images, {counts['paired_cases']} paired query/support cases and {counts['method_records']} method records. "
             f"There are {counts['unique_anomalies']} unique anomalous images and {counts['anomaly_cases']} anomalous cases. Repeated support cases are correlated.", '',
             f"The development grid recorded {dev['candidate_count']} candidates, {dev['eligible_count']} eligible hybrids and {dev['eligible_feasible_count']} eligible candidates with zero declared detected-to-missed losses against both controls. "
             'Native development labels selected the parameters and image threshold. This report evaluates the saved lock and does not select a winner.', '',
             f"The highest preservation-feasible hybrid development accuracy is {_fmt(dev['best_eligible_feasible_accuracy'], True)}; the highest accuracy among all grid cells, including controls and unsafe candidates, is {_fmt(dev['best_any_accuracy'], True)}. Both are post-selection development measurements.", '',
             'Locked recipe:', '', '```json',
             json.dumps({name: dev['selection_lock'][name] for name in ('params', 'feature')
                         if name in dev['selection_lock']}, indent=2, sort_keys=True), '```', '',
             '| Method | Accuracy | Missed-defect rate | False-alarm rate | Image AUROC | Image AP | Threshold |',
             '|---|---:|---:|---:|---:|---:|---:|']
    for method in METHODS:
        row = summary['methods'][method]
        lines.append(f"| {method} | {_fmt(row['macro_accuracy'], True)} | {_fmt(row['missed_defect_rate'], True)} | {_fmt(row['false_alarm_rate'], True)} | {_fmt(row['mean_image_auroc'])} | {_fmt(row['mean_image_ap'])} | {_fmt(row['image_threshold'])} |")
    lines += ['', 'Accuracy in the table is an equal category/seed episode mean; error rates use recorded class counts. Image AUROC/AP are computed within category/seed, then averaged. Differently normalized scores are never pooled for ranking. Raw count-based accuracy is retained separately in summary.json.', '',
              '| Selected versus | Accuracy difference (95% conditional interval) | Detected→missed cases / unique images | Missed→detected cases / unique images | False alarms removed / added |',
              '|---|---:|---:|---:|---:|']
    for comparator in ('original', 'fixed_avg'):
        entry = summary['comparisons'][comparator]
        ci, transitions = entry['paired_accuracy'], entry['transitions']
        loss, gain = transitions['detected_to_missed'], transitions['missed_to_detected']
        removed, added = transitions['false_positives_removed'], transitions['false_positives_added']
        lines.append(f"| {comparator} | {_fmt(ci['estimate'], True)} [{_fmt(ci['interval'][0], True)}, {_fmt(ci['interval'][1], True)}] | {loss['records']} / {loss['unique_queries']} | {gain['records']} / {gain['unique_queries']} | {removed['records']} / {added['records']} |")
    fixed_ci = summary['comparisons']['fixed_avg']['paired_accuracy']
    if fixed_ci['interval'][0] <= 0 <= fixed_ci['interval'][1]:
        conclusion = 'The conditional paired accuracy interval versus fixed averaging includes zero, so these observations do not establish an accuracy improvement.'
    elif fixed_ci['interval'][0] > 0:
        conclusion = 'Selected accuracy is higher than fixed averaging within this conditional image/support check; this result does not establish full-benchmark superiority.'
    else:
        conclusion = 'Selected accuracy is lower than fixed averaging within this conditional image/support check.'
    lines += ['', conclusion,
              'Detection losses must be read alongside false-alarm reductions; a higher overall accuracy alone does not establish better defect preservation. Unique lost/recovered image sets can overlap across support draws.', '',
              f"Intervals use {fixed_ci['n_bootstrap']} paired crossed query/support percentile resamples with fixed categories. Support multiplicities are sampled independently within each category. Three or fewer draws provide limited replication; no candidate-row, pixel or independent-record interval is used.", '',
              '## Category breakdown', '',
              '| Dataset/category | Method | Accuracy | Missed-defect rate | False-alarm rate | Image AUROC | Image AP |',
              '|---|---|---:|---:|---:|---:|---:|']
    for row in summary['category_metrics']:
        lines.append(f"| {row['dataset']}/{row['category']} | {row['method']} | {_fmt(row['accuracy'], True)} | {_fmt(row['missed_defect_rate'], True)} | {_fmt(row['false_alarm_rate'], True)} | {_fmt(row['mean_image_auroc'])} | {_fmt(row['mean_image_ap'])} |")
    if summary['localization']['available']:
        lines += ['', '## Saved localization metrics', '',
                  'These are supplied per-episode values, not a fresh score-map/mask recomputation. Missing values remain missing.', '',
                  '| Method | Pixel AP | AU-PRO | IoU | Pixel F1 |', '|---|---:|---:|---:|---:|']
        for method in METHODS:
            row = summary['methods'][method]['localization']
            lines.append(f"| {method} | {_fmt(row['pixel_ap']['mean'])} | {_fmt(row['au_pro']['mean'])} | {_fmt(row['iou']['mean'])} | {_fmt(row['pixel_f1']['mean'])} |")
    else:
        lines += ['', 'No per-episode localization metrics were supplied. No pixel measurements are inferred from detection records.']
    lines += ['', '## Scope and audit limits', '']
    lines.extend(f'- {value}' for value in summary['caveats'])
    lines += ['', 'The exact lock, candidate counts, class counts, transition image IDs, input hashes and report audit flags are recorded in summary.json.', '']
    return '\n'.join(lines)


def write_tuning_report(run_dir, **kwargs):
    """Write report.md and summary.json after all read-only audits succeed."""
    run = Path(run_dir)
    summary = build_tuning_report(run, **kwargs)
    json_path, report_path = run/'summary.json', run/'report.md'
    json_path.write_text(json.dumps(summary, indent=2, sort_keys=True, allow_nan=False)+'\n')
    report_path.write_text(_markdown(summary))
    return {'report': str(report_path), 'summary': str(json_path)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', required=True, type=Path)
    parser.add_argument('--bootstrap-samples', type=int, default=2000)
    parser.add_argument('--bootstrap-seed', type=int, default=20261014)
    args = parser.parse_args()
    paths = write_tuning_report(args.run_dir, n_bootstrap=args.bootstrap_samples,
                                bootstrap_seed=args.bootstrap_seed)
    print(json.dumps(paths, sort_keys=True))


if __name__ == '__main__':
    main()
