"""Audit and summarize an executed SAFAL development-validation training run.

No model, cutoff, fusion weight or abstention rule is changed. Paired accuracy
intervals resample original query IDs and shared support-draw seeds. Nested k
comparisons are averaged within query/seed before the overall bootstrap.
"""
import argparse
from collections import defaultdict
import csv
import hashlib
import json
import math
import os
from pathlib import Path
import re
import tempfile

os.environ.setdefault('MPLCONFIGDIR', str(Path(tempfile.gettempdir())/'safal_matplotlib'))
os.environ.setdefault('XDG_CACHE_HOME', str(Path(tempfile.gettempdir())/'safal_cache'))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from safe_iad.research_metrics import paired_crossed_bootstrap, risk_coverage, thresholded_detection_metrics
from safe_iad.safal_calibration import ErrorCalibrator, calibration_feature_vector, probability_metrics


POINT_METRICS = ('accuracy', 'balanced_accuracy', 'image_auroc', 'image_ap', 'image_f1',
                 'missed_defect_rate', 'false_alarm_rate', 'pixel_auroc', 'pixel_ap',
                 'au_pro', 'iou', 'pixel_f1', 'aurc')
METHOD_ORDER = ('search', 'subspace', 'fixed_avg', 'max', 'safal')
CAPTION = ('Development validation; fixed sampled categories and fitted head. '
           'Queries recur across support draws and nested k. No independent-row or pixel confidence intervals.')


def read_json(path):
    return json.loads(Path(path).read_text())


def read_rows(path):
    return [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]


def dump(path, value):
    Path(path).write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False)+'\n')


def save_csv(path, rows):
    if not rows:
        return
    fields = list(dict.fromkeys(key for row in rows for key in row))
    with Path(path).open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader(); writer.writerows(rows)


def finite_mean(values):
    values = [float(value) for value in values if value is not None]
    if not values:
        return None
    if not np.isfinite(values).all():
        raise ValueError('Nonfinite recorded metric; refusing to silently discard it.')
    return float(np.mean(values))


def case_key(row):
    return row['dataset'], row['category'], int(row['seed']), int(row['shots']), row['query_id']


def is_correct(row):
    return bool(row['predicted_anomaly']) == bool(row['label'])


def is_accepted(row):
    return row['action'] in {'normal', 'anomaly', 'defective'}


def confidence(row):
    if row.get('error_probability') is not None:
        return 1-float(row['error_probability'])
    return -float(row['U'])  # diagnostic rank, not an invented probability


def inspect_run(run):
    if not (run/'completion.json').is_file():
        raise ValueError('Run is not completed: completion.json is required before reporting.')
    config, manifest = read_json(run/'config.json'), read_json(run/'manifest.json')
    predictions = read_rows(run/'predictions.jsonl')
    methods = sorted({row['method'] for row in predictions}, key=lambda name: (METHOD_ORDER.index(name) if name in METHOD_ORDER else len(METHOD_ORDER), name))
    if not predictions or 'safal' not in methods:
        raise ValueError('Completed predictions must include SAFAL and its actual comparators.')
    cases = defaultdict(dict)
    for row in predictions:
        if row.get('role') != 'validation' or row['label'] not in [0, 1]:
            raise ValueError('Only declared development-validation binary labels may be summarized.')
        score = float(row['image_score'])
        if not math.isfinite(score) or bool(row['predicted_anomaly']) != (score >= 1):
            raise ValueError('Prediction flag differs from its locked score>=1 decision.')
        action = row['action']
        if action not in {'normal', 'anomaly', 'defective', 'abstain', 'unresolved/reference-insufficient'}:
            raise ValueError('Unknown action; cannot silently interpret retained coverage.')
        if (action == 'normal' and row['predicted_anomaly']) or (action in {'anomaly', 'defective'} and not row['predicted_anomaly']):
            raise ValueError('Resolved action contradicts the retained raw defect flag.')
        key = case_key(row)
        if row['method'] in cases[key]:
            raise ValueError('Duplicate query/support/k/method record.')
        cases[key][row['method']] = row
    if any(set(case) != set(methods) for case in cases.values()):
        raise ValueError('Every query/support/k case must contain the same paired methods.')
    episode_rows, risk_rows, metric_checks = [], [], 0
    for plan in manifest['episodes']:
        metric_file = run/'episodes'/plan['id']/'metrics.json'
        recorded = read_json(metric_file)
        for method in methods:
            rows = [cases[(plan['dataset'], plan['category'], int(plan['seed']), int(plan['shots']), query)][method]
                    for query in plan['query_ids']]
            truth = [row['label'] for row in rows]
            scores = [row['image_score'] for row in rows]
            detection = thresholded_detection_metrics(truth, scores, 1.)
            previous = recorded[method]['detection']
            for name in ['tp', 'fp', 'fn', 'tn', 'auroc', 'ap', 'f1', 'missed_defect_rate', 'false_alarm_rate']:
                actual, saved = detection[name], previous[name]
                if (actual is None) != (saved is None) or (actual is not None and not np.isclose(actual, saved, atol=1e-12, rtol=1e-12)):
                    raise ValueError(f'Recomputed {name} differs from {metric_file}: {method}')
                metric_checks += 1
            if detection['queries'] != len(rows):
                raise ValueError('Episode query count differs from prediction rows.')
            errors = [not is_correct(row) for row in rows]
            risk = risk_coverage(errors, [confidence(row) for row in rows])
            locator = recorded[method]['localization']
            row = dict(dataset=plan['dataset'], category=plan['category'], seed=int(plan['seed']),
                       shots=int(plan['shots']), method=method, query_records=len(rows),
                       accuracy=float(np.mean(np.logical_not(errors))),
                       balanced_accuracy=((1-detection['missed_defect_rate'])+(1-detection['false_alarm_rate']))/2
                           if detection['missed_defect_rate'] is not None and detection['false_alarm_rate'] is not None else None,
                       image_auroc=detection['auroc'], image_ap=detection['ap'], image_f1=detection['f1'],
                       missed_defect_rate=detection['missed_defect_rate'], false_alarm_rate=detection['false_alarm_rate'],
                       pixel_auroc=locator['pixel_auroc'], pixel_ap=locator['pixel_ap'],
                       au_pro=locator['au_pro'], iou=locator['iou'], pixel_f1=locator['pixel_f1'], aurc=risk['aurc'],
                       au_pro_fpr_limit=locator['au_pro_fpr_limit'],
                       risk_confidence='one_minus_source_error_estimate' if all(x.get('error_probability') is not None for x in rows) else 'negative_U_diagnostic_rank',
                       **{name:detection[name] for name in ['tp', 'fp', 'fn', 'tn']})
            episode_rows.append(row)
            risk_rows.append({key:row[key] for key in ['dataset', 'category', 'seed', 'shots', 'method', 'risk_confidence']} | risk)
    expected = sum(len(plan['query_ids'])*len(methods) for plan in manifest['episodes'])
    if expected != len(predictions):
        raise ValueError('Manifest and prediction record totals differ.')
    return config, manifest, predictions, methods, cases, episode_rows, risk_rows, metric_checks


def accepted_counts(rows):
    accepted = [row for row in rows if is_accepted(row)]
    rejected = [row for row in rows if not is_accepted(row)]
    counts = {name:sum(bool(row['label']) == label and bool(row['predicted_anomaly']) == pred for row in accepted)
              for name, label, pred in [('accepted_tp', True, True), ('accepted_fp', False, True),
                                       ('accepted_fn', True, False), ('accepted_tn', False, False)]}
    positives = counts['accepted_tp']+counts['accepted_fn']
    negatives = counts['accepted_fp']+counts['accepted_tn']
    return counts | dict(accepted_records=len(accepted), unresolved_records=len(rejected),
                         unresolved_defect_records=sum(bool(row['label']) for row in rejected),
                         unresolved_normal_records=sum(not bool(row['label']) for row in rejected),
                         acceptance_coverage=len(accepted)/len(rows),
                         accepted_accuracy=float(np.mean([is_correct(row) for row in accepted])) if accepted else None,
                         accepted_missed_defect_rate=counts['accepted_fn']/positives if positives else None,
                         accepted_false_alarm_rate=counts['accepted_fp']/negatives if negatives else None)


def aggregate(episodes, predictions, keys):
    groups = defaultdict(list)
    for row in episodes:
        groups[tuple(row[key] for key in keys)].append(row)
    summaries = []
    for values, group in sorted(groups.items()):
        match = dict(zip(keys, values))
        native = [row for row in predictions if all(row[key] == value for key, value in match.items())]
        categories = defaultdict(list)
        for row in group:
            categories[(row['dataset'], row['category'])].append(row)
        result = match | dict(sampled_categories=len(categories), episodes=len(group),
                              support_draws=len({row['seed'] for row in group}),
                              unique_query_images=len({(row['dataset'], row['category'], row['query_id']) for row in native}),
                              query_support_k_records=len(native),
                              aggregation='mean support/shot episodes within category, then equal sampled-category means')
        for metric in POINT_METRICS:
            result[metric] = finite_mean([finite_mean([row[metric] for row in category]) for category in categories.values()])
        for name in ['tp', 'fp', 'fn', 'tn']:
            result[name] = sum(row[name] for row in group)
        result.update(accepted_counts(native))
        summaries.append(result)
    return summaries


def source_audit(run, predictions):
    rows = read_rows(run/'source_calibration.jsonl')
    report = read_json(run/'calibration_report.json')
    groups = defaultdict(list)
    for row in rows:
        if row['domain'] != 'source_normal_plus_cutpaste' or row['target'] != 'prediction_error' or row['error_label'] not in [0, 1]:
            raise ValueError('Unexpected source error-calibration domain/event.')
        groups[(row['experiment_role'], row['dataset'], row['category'], row['query_kind'])].append(row)
    table = []
    for (role, dataset, category, kind), items in sorted(groups.items()):
        table.append(dict(role=role, dataset=dataset, category=category, query_kind=kind,
                          rows=len(items), correct_events=sum(row['error_label'] == 0 for row in items),
                          error_events=sum(row['error_label'] == 1 for row in items),
                          original_parents=len({row['query_source_id'] for row in items}),
                          error_parents=len({row['query_source_id'] for row in items if row['error_label'] == 1})))
    totals = []
    parents = {}
    for role in sorted({row['experiment_role'] for row in rows}):
        items = [row for row in rows if row['experiment_role'] == role]
        parent = lambda row:(row['dataset'], row['category'], row['query_source_id'])
        parents[role] = {parent(row) for row in items}
        totals.append(dict(role=role, rows=len(items), original_parents=len(parents[role]),
                           correct_events=sum(row['error_label'] == 0 for row in items),
                           error_events=sum(row['error_label'] == 1 for row in items),
                           error_parents=len({parent(row) for row in items if row['error_label'] == 1})))
    overlap = parents.get('meta_training', set()) & parents.get('source_calibration', set())
    if overlap:
        raise ValueError('Source fitting and held-out audit parents overlap.')
    for role, row_key, group_key in [('meta_training', 'fit_rows', 'fit_groups'), ('source_calibration', 'calibration_rows', 'calibration_groups')]:
        matching = next(row for row in totals if row['role'] == role)
        if report[row_key] != matching['rows'] or report[group_key] != matching['original_parents']:
            raise ValueError('Calibrator report differs from actual source rows/groups.')
    model = ErrorCalibrator.load(run/'error_calibrator.json')
    replay = {}
    for role in ['meta_training', 'source_calibration']:
        selected = [row for row in rows if row['experiment_role'] == role]
        probability = model.predict([row['features'] for row in selected],
                                    feature_names=model.feature_names, domain=model.source_domain)
        replay[role] = probability_metrics([row['error_label'] for row in selected], probability)
    for key in ['brier', 'nll', 'ece']:
        if not np.isclose(replay['source_calibration'][key], report['heldout_metrics'][key], atol=1e-12, rtol=1e-12):
            raise ValueError('Saved source held-out probability metric fails JSON-model replay.')
    native = [row for row in predictions if row.get('error_probability') is not None]
    if native:
        probability = model.predict([calibration_feature_vector(row['image_score'], row['A'],
                                                                row['branch_disagreement'], row['U']) for row in native],
                                    feature_names=model.feature_names, domain='deployment_unverified')
        if not np.allclose(probability, [row['error_probability'] for row in native], atol=1e-12, rtol=1e-12):
            raise ValueError('Recorded native error probabilities fail saved JSON-head replay.')
    return dict(totals=totals, by_category_kind=table, parent_overlap=0, fitted_head_report=report,
                replayed_probability_metrics=replay, native_probability_replay_checks=len(native))


def probability_audits(predictions):
    selected = [row for row in predictions if row.get('error_probability') is not None]
    table, details = [], []
    for keys in [('dataset', 'category', 'shots', 'method'), ('dataset', 'shots', 'method'), ('shots', 'method')]:
        groups = defaultdict(list)
        for row in selected:
            groups[tuple(row[key] for key in keys)].append(row)
        for values, rows in sorted(groups.items()):
            match = dict(zip(keys, values))
            errors = [not is_correct(row) for row in rows]
            result = probability_metrics(errors, [row['error_probability'] for row in rows])
            metadata = match | dict(scope='category' if 'category' in keys else 'dataset' if 'dataset' in keys else 'all_sampled_categories',
                                    records=len(rows), unique_queries=len({(row['dataset'], row['query_id']) for row in rows}),
                                    error_domain=';'.join(sorted({row['error_domain'] for row in rows})),
                                    domain_transfer_verified=False,
                                    source_head_shot_transfer='source head fitted at k=2; other-shot transfer unverified')
            table.append(metadata | {key:result[key] for key in ['observed_error_rate', 'brier', 'nll', 'ece']} |
                         dict(aurc=result['risk_coverage']['aurc'], error_detection_auroc=result['risk_coverage']['error_detection_auroc']))
            details.append(metadata | result)
    return table, details


def paired_intervals(cases, methods, shots, samples, seed):
    result = {'by_shot': {}, 'overall_nested_shots': {},
              'scope':'Conditional on sampled categories, queries, draw seeds and the fixed fitted head/cutoffs; three draws are limited replication.',
              'overall_rule':'Average dependent nested-k differences within each query/seed before crossed resampling.',
              'auroc_intervals':'Not constructed from replicated episode scalars.',
              'comparison_event':'Raw locked-cutoff image correctness; unresolved cases remain in the denominator.'}
    for comparator in methods:
        if comparator == 'safal':
            continue
        nested = defaultdict(list)
        for k in shots:
            paired = []
            for (dataset, category, draw, actual_k, query), case in cases.items():
                if actual_k != k:
                    continue
                delta = int(is_correct(case['safal']))-int(is_correct(case[comparator]))
                paired.append(dict(dataset=dataset, category=category, seed=draw, query_id=query, paired_difference=delta))
                nested[(dataset, category, draw, query)].append((k, delta))
            result['by_shot'].setdefault(str(k), {})[comparator] = paired_crossed_bootstrap(paired, n_bootstrap=samples, seed=seed)
        paired = []
        for (dataset, category, draw, query), values in nested.items():
            if {k for k, _ in values} != set(shots) or len(values) != len(shots):
                raise ValueError('Incomplete nested-shot pairing; cannot construct overall accuracy interval.')
            paired.append(dict(dataset=dataset, category=category, seed=draw, query_id=query,
                               paired_difference=float(np.mean([value for _, value in values]))))
        result['overall_nested_shots'][comparator] = paired_crossed_bootstrap(paired, n_bootstrap=samples, seed=seed)
    return result


def save_figure(figure, path):
    figure.savefig(path.with_suffix('.png'), dpi=180)
    figure.savefig(path.with_suffix('.pdf'))
    plt.close(figure)


def plot_results(output, shot_summary, probability_details, methods):
    palette = plt.get_cmap('tab10')
    colors = {method:palette(index) for index, method in enumerate(methods)}
    figure, axes = plt.subplots(2, 2, figsize=(11.5, 8))
    for axis, (metric, title) in zip(axes.ravel(), [('accuracy', 'Raw image accuracy'), ('image_auroc', 'Image AUROC'), ('pixel_ap', 'Pixel AP'), ('au_pro', 'AU-PRO')]):
        for method in methods:
            rows = sorted([row for row in shot_summary if row['method'] == method], key=lambda row:row['shots'])
            axis.plot([row['shots'] for row in rows], [row[metric] for row in rows], marker='o', label=method, color=colors[method])
        axis.set(title=title, xlabel='Initial references k', ylim=(0, 1))
        axis.set_xticks(sorted({row['shots'] for row in shot_summary})); axis.grid(alpha=.2)
    handles, labels = axes[0, 0].get_legend_handles_labels()
    figure.legend(handles, labels, loc='upper center', ncol=len(methods))
    figure.text(.5, .015, CAPTION, ha='center', fontsize=9, wrap=True)
    figure.subplots_adjust(top=.89, bottom=.13, hspace=.35)
    save_figure(figure, output/'detection_localization_by_shot')
    figure, axes = plt.subplots(1, 3, figsize=(14, 4.8))
    for axis, (metric, title) in zip(axes[:2], [('missed_defect_rate', 'Raw missed-defect rate'), ('false_alarm_rate', 'Raw false-alarm rate')]):
        for method in methods:
            rows = sorted([row for row in shot_summary if row['method'] == method], key=lambda row:row['shots'])
            axis.plot([row['shots'] for row in rows], [row[metric] for row in rows], marker='o', label=method, color=colors[method])
        axis.set(title=title, xlabel='k', ylim=(0, 1)); axis.grid(alpha=.2)
    rows = sorted([row for row in shot_summary if row['method'] == 'safal'], key=lambda row:row['shots'])
    axes[2].plot([row['shots'] for row in rows], [row['acceptance_coverage'] for row in rows], marker='o', label='Accepted coverage')
    axes[2].plot([row['shots'] for row in rows], [row['accepted_accuracy'] for row in rows], marker='s', label='Accuracy among accepted')
    axes[2].set(title='SAFAL selective decisions', xlabel='k', ylim=(0, 1)); axes[2].legend(); axes[2].grid(alpha=.2)
    handles, labels = axes[0].get_legend_handles_labels()
    figure.legend(handles, labels, loc='upper center', ncol=len(methods))
    figure.text(.5, .01, CAPTION+' Accepted accuracy always accompanies retained coverage.', ha='center', fontsize=8, wrap=True)
    figure.subplots_adjust(top=.8, bottom=.18, wspace=.3)
    save_figure(figure, output/'misses_false_alarms_and_coverage')
    pooled = [row for row in probability_details if row['scope'] == 'all_sampled_categories' and row['method'] == 'safal']
    if pooled:
        figure, axes = plt.subplots(1, 2, figsize=(11, 4.8))
        for row in sorted(pooled, key=lambda row:row['shots']):
            curve = [point for point in row['risk_coverage']['curve'] if point['risk'] is not None]
            axes[0].plot([point['coverage'] for point in curve], [point['risk'] for point in curve], label=f"k={row['shots']}")
            bins = [point for point in row['reliability_diagram'] if point['count']]
            axes[1].plot([point['mean_error_probability'] for point in bins], [point['observed_error_rate'] for point in bins], marker='o', label=f"k={row['shots']}")
        axes[0].set(title='SAFAL native error risk–coverage', xlabel='Accepted fraction', ylabel='Raw classification-error risk', xlim=(0, 1), ylim=(0, 1))
        axes[1].plot([0, 1], [0, 1], '--', color='gray'); axes[1].set(title='Empirical error-probability reliability', xlabel='Estimated error probability', ylabel='Observed error frequency', xlim=(0, 1), ylim=(0, 1))
        for axis in axes:axis.legend(); axis.grid(alpha=.2)
        figure.text(.5, .015, 'Source normal/CutPaste head; native-domain and other-shot probability transfer unverified.\n'+CAPTION, ha='center', fontsize=8, wrap=True)
        figure.subplots_adjust(bottom=.2, wspace=.3)
        save_figure(figure, output/'native_probability_reliability')


def display(value, precision=4):
    return 'null' if value is None else f'{float(value):.{precision}f}'


def table(headers, rows):
    return '\n'.join(['| '+' | '.join(headers)+' |', '| '+' | '.join(['---']*len(headers))+' |']+
                     ['| '+' | '.join(map(str, row))+' |' for row in rows])


def write_report(output, run, config, manifest, predictions, methods, cases, overall, category, probability, source, intervals, audit, exposure, test_log):
    total = len(predictions); unique = len({(row['dataset'], row['query_id']) for row in predictions})
    draws = len({row['seed'] for row in predictions}); categories = len({(row['dataset'], row['category']) for row in predictions})
    source_rows = {row['role']:row for row in source['totals']}
    fit, held = source_rows['meta_training'], source_rows['source_calibration']
    safal = next(row for row in overall if row['method'] == 'safal')
    ci = intervals['overall_nested_shots']
    comparator = 'fixed_avg' if 'fixed_avg' in methods else max((row for row in overall if row['method'] != 'safal'), key=lambda row:row['accuracy'])['method']
    reference = next(row for row in overall if row['method'] == comparator)
    primary = ci[comparator]
    if primary['interval'][0] <= 0 <= primary['interval'][1]:
        conclusion = 'An accuracy improvement over that comparator is not established by this conditional comparison.'
    elif primary['interval'][0] > 0:
        conclusion = 'The conditional paired interval is positive on these sampled development categories; it does not establish dataset-wide or deployment superiority.'
    else:
        conclusion = 'The conditional paired interval favors the comparator on these sampled development categories.'
    evidence = '; '.join(f"{method}: delta={value['estimate']:.4f}, conditional95%CI=[{value['interval'][0]:.4f},{value['interval'][1]:.4f}]" for method, value in ci.items())
    lines = ['# Executed SAFAL training and development-validation results\n',
             f"SAFAL raw mean image accuracy was {display(safal['accuracy'])}, compared with {comparator} at {display(reference['accuracy'])}. {conclusion} These are actual outcomes on {unique} unique development-validation images, not dataset-wide or deployment performance. Paired evidence: {evidence}. No threshold, fusion weight or head hyperparameter was tuned from this run.\n",
             f"Training comprises frozen pretrained DINOv2 feature extraction, normal-reference/PCA fits and logistic error-head learning on {fit['rows']} source error events from {fit['original_parents']} original image parents. The untouched current-fit source audit has {held['rows']} rows from {held['original_parents']} parents. This is not LLM or DINO backbone fine-tuning. The source mixture is real normal images plus explicitly synthetic CutPaste derivatives.\n",
             f"There are {len(manifest['episodes'])} reference-fit episodes, {draws} support-draw seeds, k={sorted({row['shots'] for row in predictions})}, {categories} sampled reserved-validation categories, {len(cases)} paired query/support/k cases and {total} method records. Repeated cases do not create {total} independent images. Overall metric means weight sampled categories equally after averaging their support/shot episodes. Accuracy describes the deliberately balanced normal/anomaly query mixture. Image AUC/AP are computed per category/seed/k, not pooled across category fits.\n",
             f"The information budget is k initial target normal reference images plus {config['normal_calibration_images']} extra disjoint target normal calibration images. This is not strict k-image few-shot. Score cutoffs use the predeclared empirical normal quantile {config['normal_calibration_quantile']}; the fixed source-error abstention cutoff is {config['abstain_error_probability']}. A small empirical normal quantile is not a guaranteed target false-alarm rate.\n",
             '**Actual method means.**\n',
             table(['Method', 'Accuracy', 'Image AUC', 'Image AP', 'Pixel AP', 'AU-PRO', 'IoU', 'Miss rate', 'False-alarm rate', 'Accepted coverage', 'Accepted accuracy'],
                   [[row['method']]+[display(row[key]) for key in ['accuracy', 'image_auroc', 'image_ap', 'pixel_ap', 'au_pro', 'iou', 'missed_defect_rate', 'false_alarm_rate', 'acceptance_coverage', 'accepted_accuracy']] for row in overall])+'\n',
             '**Per-category/shot outcomes.** Values average the actual support draws. Full precision is in summary_by_category_shot.csv.\n',
             table(['Dataset/category', 'k', 'Method', 'Accuracy', 'Image AUC', 'Image AP', 'Pixel AP', 'AU-PRO'],
                   [[row['dataset']+'/'+row['category'], row['shots'], row['method']]+[display(row[key]) for key in ['accuracy', 'image_auroc', 'image_ap', 'pixel_ap', 'au_pro']] for row in category])+'\n',
             '**Missed defects and selective decisions.** Raw accuracy includes every inspection, including unresolved actions. Accepted accuracy is conditional on retained actions and must accompany coverage; rejected defects remain explicitly unresolved, not successes. Counts below are repeated query/support/k records.\n',
             table(['Method', 'Raw missed defects', 'Raw false alarms', 'Accepted misses', 'Accepted false alarms', 'Unresolved defects', 'Unresolved normals'],
                   [[row['method']]+[row[key] for key in ['fn', 'fp', 'accepted_fn', 'accepted_fp', 'unresolved_defect_records', 'unresolved_normal_records']] for row in overall])+'\n',
             '**Source error-head learning.** Both events mean prediction correctness at the locked classifier cutoff: 0=correct, 1=incorrect; they do not mean normal versus anomalous.\n',
             table(['Source role', 'Rows', 'Original parents', 'Correct events', 'Error events', 'Parents with errors'],
                   [[row[key] for key in ['role', 'rows', 'original_parents', 'correct_events', 'error_events', 'error_parents']] for row in source['totals']])+'\n',
             'Fitting and held-out original-parent overlap is zero. Normal/CutPaste siblings stay in the same split. Logistic C=1, class_weight=None and feature normalization fitted only on source fitting rows are preserved. Sparse independent error parents limit probability evidence. Detailed category/kind counts are in source_error_counts.csv.\n',
             table(['Source split', 'Brier', 'ECE', 'NLL'],
                   [[role]+[display(metric[key],6) for key in ['brier', 'ece', 'nll']]
                    for role,metric in source['replayed_probability_metrics'].items()])+'\n',
             'These source metrics were recomputed from the saved plain-JSON head. The held-out metrics match the stored training report; native probabilities also pass JSON-head replay. This source audit is not native industrial calibration evidence.\n',
             '**Native error-probability audit by shot.** The same source head was fitted at k=2. Native-domain transfer and transfer to other shot counts are unverified. These metrics evaluate actual wrong/correct image events after inference; sigmoid values are not asserted calibrated.\n',
             table(['k', 'Method', 'Repeated events', 'Observed error rate', 'Brier', 'ECE', 'NLL', 'AURC'],
                   [[row['shots'], row['method'], row['records']]+[display(row[key],6) for key in ['observed_error_rate', 'brier', 'ece', 'nll', 'aurc']]
                    for row in probability if row['scope']=='all_sampled_categories'])+'\n',
             'Brier/NLL/ECE aggregate actual probabilities and error events. Risk is locked-cutoff 0/1 classification error; whole tied-confidence groups are accepted together and AURC uses right-step integration. Curves are descriptive, correlated observations, not independent risk guarantees. Other methods use negative U as a diagnostic confidence rank, not a fabricated probability.\n',
             '**Paired uncertainty.** paired_accuracy_intervals.json stores each-k and overall SAFAL-minus-comparator intervals. Overall differences first average dependent nested-k results within each query/seed. Crossed resampling then independently weights query IDs and shared support-draw seeds within category. Sampled categories, the fitted head, training sample and cutoffs remain fixed. With only '+str(draws)+' draw units, these are limited-replication conditional percentile intervals; they do not capture head-training uncertainty, unsampled categories or a pristine final-test population. No AUROC interval is manufactured from repeated episode values and no pixels are resampled.\n',
             '**Metric geometry and audit.** '+manifest['metric_geometry']+'. Localized score maps and masks use the recorded metric grid; these localization values are not new original-resolution benchmark results. AU-PRO follows saved connected-region/FPR settings, with its sampled threshold integration limit in episode_metrics.csv. Reporting recomputed image decision counts, AUC/AP/F1 and risk curves from serialized predictions, checked them against recorded episode detection metrics, and retained recorded localization values without pretending to rerun all pixel maps. reporting_audit.json records '+str(audit['detection_metric_checks'])+' matching detection checks. Model and runtime files were read only.\n']
    lost, gained, removed, added = [], [], [], []
    for key, case in cases.items():
        before, after = case[comparator], case['safal']
        if before['label']:
            if before['predicted_anomaly'] and not after['predicted_anomaly']:lost.append(key)
            if not before['predicted_anomaly'] and after['predicted_anomaly']:gained.append(key)
        else:
            if before['predicted_anomaly'] and not after['predicted_anomaly']:removed.append(key)
            if not before['predicted_anomaly'] and after['predicted_anomaly']:added.append(key)
    tradeoff = (f"Compared with {comparator}, SAFAL has {safal['fn']-reference['fn']} additional raw missed-defect records "
                f"and {reference['fp']-safal['fp']} fewer raw false-alarm records. Missed-defect rates are "
                f"{display(safal['missed_defect_rate'])} versus {display(reference['missed_defect_rate'])}; false-alarm rates are "
                f"{display(safal['false_alarm_rate'])} versus {display(reference['false_alarm_rate'])}. Direct pairing identifies "
                f"{len(lost)} detected-to-missed records touching {len({(key[0],key[4]) for key in lost})} unique anomaly images, "
                f"and {len(gained)} missed-to-detected records touching {len({(key[0],key[4]) for key in gained})} unique anomaly images. "
                f"Normal false alarms were removed in {len(removed)} records and added in {len(added)}. "
                'These are repeated support/shot inspection events. Fewer false alarms must not be described as better defect preservation.\n')
    position = next(index for index, line in enumerate(lines) if line.startswith('**Source error-head learning.**'))
    lines.insert(position, tradeoff)
    runner_summary = read_json(run/'summary.json') if (run/'summary.json').is_file() else {}
    runner_ci = runner_summary.get('paired_safal_minus_fixed_accuracy') if comparator == 'fixed_avg' else None
    if runner_ci and runner_ci.get('n_bootstrap') != primary['n_bootstrap']:
        lines.append(f"The runtime summary used {runner_ci['n_bootstrap']} bootstrap resamples and stored interval {runner_ci['interval']}; "
                     f"this derived report uses {primary['n_bootstrap']} resamples and interval {primary['interval']}. "
                     'Finite Monte Carlo resampling changes the interval endpoints; neither fit nor decision parameters were changed.\n')
    artifact_path = output.parent/'artifact_audit.json'
    if artifact_path.is_file():
        artifact = read_json(artifact_path)
        if artifact['status'] != 'passed':raise ValueError('Independent artifact audit has not passed.')
        lines.append(f"The independent completed-artifact audit passed: {artifact['serialized_models_checked']} serialized models, "
                     f"{artifact['serialized_query_replays']} cached query replays, {artifact['stage_ledgers_checked']} ledgers, "
                     f"{artifact['unique_output_files_hash_verified']} unique output files and {artifact['unique_input_files_hash_verified']} unique input files hash-verified. "
                     'It does not establish native-resolution localization or source-proxy probability transfer. See artifact_audit.json.\n')
    if exposure:
        overlap = exposure['overlap_summary']
        lines.append(f"**Prior exposure.** The separate named-run audit found {overlap['prior_measured_validation_query_ids_reused']} current query IDs previously measured and {overlap['query_ids_not_identified_in_these_five_runs']} not identified in those five runs. This is not proof of an untouched history. It found {overlap['current_source_parents_used_as_prior_source_queries']} prior source-query parents, including {overlap['current_heldout_parent_reuse']} current held-out parent; current fit/held-out identity separation remains zero. This is broader development validation, not a pristine unseen final benchmark. See prior_exposure_audit.json.\n")
    if test_log and test_log.is_file():
        text = test_log.read_text(); matches = re.findall(r'Ran (\d+) tests', text)
        if matches and text.rstrip().endswith('OK'):
            lines.append(f"The supplied unit/contract test log records {matches[-1]} passing tests at {test_log}. These tests are separate from the actual training/validation run and the reporting recomputation audit.\n")
    lines.append('Published full recipes, dataset-wide benchmarks, private-server evaluation, LLM fine-tuning, production reliability, calibration guarantees and novelty/state-of-the-art claims are not established. The sampled validation outcomes and comparison intervals above determine the actual gain statements; source or target labels were not used to revise parameters after evaluation.\n')
    (output/'report.md').write_text('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='Directory for derived CSV/JSON/report and PNG/PDF figures.')
    parser.add_argument('--bootstrap-samples', type=int, default=2000)
    parser.add_argument('--seed', type=int, default=917)
    parser.add_argument('--test-log', type=Path)
    args = parser.parse_args()
    config, manifest, predictions, methods, cases, episodes, risks, checks = inspect_run(args.run)
    args.output.mkdir(parents=True, exist_ok=True)
    category = aggregate(episodes, predictions, ['dataset', 'category', 'shots', 'method'])
    dataset = aggregate(episodes, predictions, ['dataset', 'shots', 'method'])
    by_shot = aggregate(episodes, predictions, ['shots', 'method'])
    overall = aggregate(episodes, predictions, ['method'])
    source = source_audit(args.run, predictions)
    probability, details = probability_audits(predictions)
    shots = sorted({row['shots'] for row in predictions})
    intervals = paired_intervals(cases, methods, shots, args.bootstrap_samples, args.seed)
    audit = dict(status='passed', prediction_records=len(predictions), paired_cases=len(cases),
                 unique_query_images=len({(row['dataset'], row['query_id']) for row in predictions}),
                 methods=methods, reference_fit_episodes=len(manifest['episodes']), detection_metric_checks=checks,
                 score_flag_and_complete_method_pairing_verified=True, source_fit_heldout_parent_overlap=0,
                 native_json_head_probability_replay_checks=source['native_probability_replay_checks'],
                 localization_metrics='Recorded pixel metrics retained; not a fresh pixel-map recomputation.',
                 scientific_code_changed=False, parameters_tuned=False,
                 inputs={name:hashlib.sha256((args.run/name).read_bytes()).hexdigest() for name in
                         ['completion.json', 'config.json', 'manifest.json', 'predictions.jsonl', 'source_calibration.jsonl', 'calibration_report.json']})
    exposure_path = args.output.parent/'prior_exposure_audit.json'
    exposure = read_json(exposure_path) if exposure_path.is_file() else None
    for name, rows in [('episode_metrics.csv', episodes), ('summary_by_category_shot.csv', category),
                       ('summary_by_dataset_shot.csv', dataset), ('summary_by_shot.csv', by_shot),
                       ('summary_overall.csv', overall), ('source_error_counts.csv', source['by_category_kind']),
                       ('source_error_totals.csv', source['totals']), ('native_probability_metrics.csv', probability)]:
        save_csv(args.output/name, rows)
    for name, obj in [('source_head_audit.json', source), ('native_probability_details.json', details),
                      ('risk_coverage_per_episode.json', risks), ('paired_accuracy_intervals.json', intervals),
                      ('reporting_audit.json', audit)]:
        dump(args.output/name, obj)
    plot_results(args.output, by_shot, details, methods)
    test_log = args.test_log if args.test_log is not None else args.output.parent/'unit_tests.log'
    write_report(args.output, args.run, config, manifest, predictions, methods, cases, overall, category,
                 probability, source, intervals, audit, exposure, test_log)
    print(json.dumps(dict(status='completed_actual_result_summary', unique_query_images=audit['unique_query_images'],
                          prediction_records=len(predictions), output=str(args.output),
                          method_means={row['method']:{key:row[key] for key in ['accuracy', 'image_auroc', 'pixel_ap', 'au_pro', 'acceptance_coverage']} for row in overall}), allow_nan=False))


if __name__ == '__main__':
    main()
