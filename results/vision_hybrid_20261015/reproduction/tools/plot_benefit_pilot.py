"""Plot executed paired benefit-pilot episodes without independence or probability claims."""
import argparse
from collections import defaultdict
import csv
import json
import math
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/workspace/.cache/matplotlib')
os.environ.setdefault('XDG_CACHE_HOME', '/workspace/.cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


POLICY_ORDER = ['none', 'random', 'nearest_global', 'diversity', 'linear', 'mlp',
                'learned_linear', 'learned_mlp', 'oracle']
SUPPORT_CONDITIONS = {
    'paired_validation': 'native paired validation',
    'missing_support': 'initial support omits the query appearance group',
    'coverage_control': 'matched control replaces one initial reference with a query-group reference',
}
CAPTION = ('Small, correlated pilot: queries recur across paired support draws. '
           'Bars show recorded descriptive summaries; no independent-row confidence intervals '
           'or calibrated probability claims. Category means receive equal weight.')
METRICS = {
    'image_auroc': ('image_metrics', 'auroc'),
    'image_ap': ('image_metrics', 'ap'),
    'image_f1': ('image_metrics', 'f1'),
    'missed_defect_rate': ('image_metrics', 'missed_defect_rate'),
    'false_alarm_rate': ('image_metrics', 'false_alarm_rate'),
    'pixel_ap': ('localization_metrics', 'pixel_ap'),
    'au_pro': ('localization_metrics', 'au_pro'),
    'iou': ('localization_metrics', 'iou'),
    'pixel_f1': ('localization_metrics', 'pixel_f1'),
    'mean_observed_benefit': (None, 'mean_observed_benefit'),
}


def numeric(value):
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError('Metric values must be finite numbers or null.')
    value = float(value)
    if not math.isfinite(value):
        raise ValueError('Metric values must be finite numbers or null.')
    return value


def summarize(episodes):
    """Average draws within category, then categories; count repeated inspections."""
    if not isinstance(episodes, list) or not episodes:
        raise ValueError('Results must contain a nonempty JSON list of executed episodes.')
    groups = defaultdict(list)
    for episode in episodes:
        for key in ['dataset', 'category', 'seed', 'shots', 'protocol', 'policy', 'query_count']:
            if key not in episode:
                raise ValueError(f'Episode is missing {key}.')
        if episode['protocol'] not in SUPPORT_CONDITIONS:
            raise ValueError(f"Unknown protocol: {episode['protocol']}")
        if int(episode['shots']) != episode['shots'] or episode['shots'] < 1:
            raise ValueError('Shots must be a positive integer.')
        count = episode['query_count']
        if isinstance(count, bool) or int(count) != count or count < 1:
            raise ValueError('Query counts must be positive integers for executed episodes.')
        groups[(episode['protocol'], str(episode['dataset']), int(episode['shots']), str(episode['policy']))].append(episode)
    summary = []
    for (protocol, dataset, shots, policy), rows in sorted(groups.items()):
        categories = sorted({str(row['category']) for row in rows})
        result = dict(protocol=protocol, dataset=dataset, shots=shots, policy=policy,
                      support_condition=SUPPORT_CONDITIONS[protocol],
                      categories=';'.join(categories), category_count=len(categories),
                      episodes=len(rows), unique_seed_count=len({str(row['seed']) for row in rows}),
                      query_count=sum(row['query_count'] for row in rows),
                      aggregation='equal category means after mean across their support-draw episodes',
                      counts_semantics='summed query/support inspection records; repeated queries are correlated')
        for output_key, (section, input_key) in METRICS.items():
            category_means = []
            recorded = 0
            for category in categories:
                values = []
                for row in rows:
                    if str(row['category']) != category:
                        continue
                    value = numeric(row.get(section, {}).get(input_key) if section else row.get(input_key))
                    if value is not None:
                        values.append(value)
                        recorded += 1
                if values:
                    category_means.append(float(np.mean(values)))
            result[output_key] = float(np.mean(category_means)) if category_means else None
            result[output_key+'_recorded_episodes'] = recorded
        for key in ['harmful_interventions', 'detected_to_missed']:
            values = [numeric(row.get(key)) for row in rows]
            present = [value for value in values if value is not None]
            if any(value < 0 or int(value) != value for value in present):
                raise ValueError(f'{key} counts must be nonnegative integers.')
            result[key] = int(sum(present)) if present else None
            result[key+'_recorded_episodes'] = len(present)
        summary.append(result)
    return summary


def policy_order(rows):
    present = {row['policy'] for row in rows}
    return [policy for policy in POLICY_ORDER if policy in present] + sorted(present-set(POLICY_ORDER))


def grouped_bars(axis, rows, policies, metric, title, colors, bounded=False, show_conditions=False):
    if show_conditions:
        condition_order = {'missing_support': 0, 'coverage_control': 1}
        groups = sorted({(row['dataset'], row['shots'], row['protocol']) for row in rows},
                        key=lambda group: (group[0], group[1], condition_order[group[2]]))
        lookup = {(row['dataset'], row['shots'], row['protocol'], row['policy']): row for row in rows}
    else:
        groups = sorted({(row['dataset'], row['shots']) for row in rows})
        lookup = {(row['dataset'], row['shots'], row['policy']): row for row in rows}
    x = np.arange(len(groups), dtype=float)
    width = .82/max(1, len(policies))
    any_value = False
    for index, policy in enumerate(policies):
        values = [lookup.get((*group, policy), {}).get(metric) for group in groups]
        available = np.array([value is not None for value in values])
        any_value |= bool(available.any())
        positions = x-.41+width*(index+.5)
        heights = np.array([value if value is not None else np.nan for value in values], dtype=float)
        axis.bar(positions[available], heights[available], width=width,
                 color=colors[policy], label=policy.replace('_', ' '))
    if show_conditions:
        conditions = {'missing_support': 'Group\nomitted', 'coverage_control': 'One matching\nreference'}
        labels = [f'{dataset}\nk={shots}\n{conditions[protocol]}' for dataset, shots, protocol in groups]
    else:
        labels = [f'{dataset}\nk={shots}' for dataset, shots in groups]
    axis.set_xticks(x, labels)
    axis.set_title(title)
    axis.grid(axis='y', alpha=.2)
    axis.set_axisbelow(True)
    if bounded:
        axis.set_ylim(0, 1)
    if not any_value:
        axis.text(.5, .5, 'No recorded values', ha='center', va='center', transform=axis.transAxes)
    axis.axhline(0, linewidth=.7, color='black')


def save_figure(figure, stem):
    png, pdf = stem.with_suffix('.png'), stem.with_suffix('.pdf')
    figure.savefig(png, dpi=180)
    figure.savefig(pdf)
    plt.close(figure)
    return [str(png), str(pdf)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True, help='Executed evaluation/episodes.json list.')
    parser.add_argument('--output', type=Path, required=True, help='PNG path or output stem; also writes PDF and CSV.')
    args = parser.parse_args()
    summary = summarize(json.loads(args.results.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    stem = args.output.with_suffix('') if args.output.suffix.lower() in {'.png', '.pdf', '.csv'} else args.output
    csv_path = stem.with_suffix('.csv')
    with csv_path.open('w', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=list(summary[0]))
        writer.writeheader()
        writer.writerows(summary)
    policies = policy_order(summary)
    palette = plt.get_cmap('tab20')
    colors = {policy: palette(index % 20) for index, policy in enumerate(policies)}
    generated = [str(csv_path)]
    native = [row for row in summary if row['protocol'] == 'paired_validation']
    if native:
        figure, axes = plt.subplots(2, 2, figsize=(max(12, 1.8*len({(row['dataset'], row['shots']) for row in native})), 8.8))
        specs = [
            ('mean_observed_benefit', 'Paired validation: mean declared-loss benefit', False),
            ('pixel_ap', 'Paired validation: pixel AP', True),
            ('harmful_interventions', 'Harmful interventions: count across repeated inspections', False),
            ('missed_defect_rate', 'Paired validation: missed-defect rate at locked cutoff', True),
        ]
        for axis, (metric, title, bounded) in zip(axes.ravel(), specs):
            grouped_bars(axis, native, policies, metric, title, colors, bounded)
        handles, labels = axes.ravel()[0].get_legend_handles_labels()
        figure.legend(handles, labels, loc='upper center', ncol=min(5, len(policies)), bbox_to_anchor=(.5, .98))
        figure.text(.5, .02, CAPTION+' Missing values are omitted, never replaced with zero.', ha='center', va='bottom', wrap=True, fontsize=9)
        figure.subplots_adjust(top=.85, bottom=.15, hspace=.4, wspace=.25)
        generated += save_figure(figure, stem)
    missing = [row for row in summary if row['protocol'] in {'missing_support', 'coverage_control'}]
    if missing:
        figure, axis = plt.subplots(figsize=(max(10, 1.8*len({(row['dataset'], row['shots'], row['protocol']) for row in missing})), 6.2))
        grouped_bars(axis, missing, policies, 'false_alarm_rate',
                     'Missing-support and matched-control normal-query false alarms at locked cutoff',
                     colors, bounded=True, show_conditions=True)
        handles, labels = axis.get_legend_handles_labels()
        figure.legend(handles, labels, loc='upper center', ncol=min(5, len(policies)), bbox_to_anchor=(.5, .99))
        figure.text(.5, .015, CAPTION+' Normal-feature groups are proxy appearance groups.\n'
                    'Matched controls keep the query, candidate pool, seed and k; exactly one initial reference changes.',
                    ha='center', va='bottom', wrap=True, fontsize=9)
        figure.subplots_adjust(top=.79, bottom=.27)
        generated += save_figure(figure, stem.with_name(stem.name+'_missing_support'))
    print(json.dumps(dict(episode_summaries=len(summary), artifacts=generated,
                         scope='Recorded small-pilot descriptive plots; no independent-row CIs or calibrated probabilities.')))


if __name__ == '__main__':
    main()
