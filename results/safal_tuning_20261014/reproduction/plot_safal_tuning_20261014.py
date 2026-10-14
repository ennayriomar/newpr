#!/usr/bin/env python3
"""Plot completed SAFAL tuning evidence without fitting or selecting anything.

Requires verification/completion.json and the audited safal_tuning_report
summary. This standalone helper writes only figures and their input metadata.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/tmp/safal_tuning_plot_cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np


METHOD_LABELS = {'original': 'Original SAFAL', 'fixed_avg': 'Fixed average',
                 'selected': 'Selected'}
METHOD_COLORS = {'original': '#475569', 'fixed_avg': '#D18B2C',
                 'selected': '#087E8B'}


def read_json(path):
    return json.loads(path.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def number(value, description):
    value = float(value)
    if not np.isfinite(value):
        raise ValueError(f'Nonfinite {description}.')
    return value


def load_completed(run):
    # This guard precedes every verification/report read.
    completion_path = run / 'verification' / 'completion.json'
    if not completion_path.is_file():
        raise ValueError('Finish verification before creating this figure.')
    summary_path = run / 'summary.json'
    if not summary_path.is_file():
        raise ValueError('Generate the audited safal_tuning_report summary first.')
    paths = {'completion': completion_path, 'summary': summary_path,
             'lock': run / 'selection.lock.json',
             'grid': run / 'development' / 'grid.json',
             'development_cases': run / 'development' / 'cases.json'}
    completion, summary = read_json(completion_path), read_json(summary_path)
    lock = read_json(paths['lock'])
    if completion['selection_lock_sha256'] != digest(paths['lock']):
        raise ValueError('Verification completion does not bind this selection lock.')
    if not summary['audit']['verification_completion_crosschecked']:
        raise ValueError('Report did not cross-check verification completion.')
    if summary['development']['selection_lock'] != lock:
        raise ValueError('Report and plotted selection locks differ.')
    if lock.get('verification_scores_seen') or lock.get('verification_masks_seen'):
        raise ValueError('Selection lock admits verification outcome access.')
    counts = summary['counts']
    if (counts['unique_queries'], counts['paired_cases'], counts['method_records']) != (100, 300, 900):
        raise ValueError('This figure expects the declared 100-image/300-case protocol.')
    strata = counts['strata']
    if len(strata) != 5 or any(row['support_draws'] != 3 for row in strata):
        raise ValueError('This figure expects five fixed categories and three support draws.')
    for key in ('unique_queries', 'paired_cases', 'method_rows'):
        expected = counts['method_records'] if key == 'method_rows' else counts[key]
        if key in completion and completion[key] != expected:
            raise ValueError(f'Completion count differs from report: {key}.')
    content = read_json(paths['grid'])
    grid = content if isinstance(content, list) else content.get('candidates', content.get('grid'))
    if not isinstance(grid, list) or len(grid) != 768 or len({row['id'] for row in grid}) != 768:
        raise ValueError('Expected 768 distinct recorded Stage 1 configurations.')
    cases = read_json(paths['development_cases'])
    if len(cases) != 300:
        raise ValueError('Expected 300 paired development cases.')
    for row in grid:
        if not isinstance(row['eligible'], bool) or not isinstance(row['feasible'], bool):
            raise ValueError('Grid eligibility and feasibility must be explicit booleans.')
        accuracy = number(row['accuracy'], 'development accuracy')
        if not 0 <= accuracy <= 1 or row['misses'] < 0:
            raise ValueError('Invalid development accuracy/miss count.')
        if row['feasible'] and (row['losses_vs_original'] or row['losses_vs_fixed']):
            raise ValueError('Feasible grid cell records preservation losses.')
    # Bind chart data to the report's checked inputs; copied reports retain paths.
    for relative in ('selection.lock.json', 'development/grid.json',
                     'verification/completion.json'):
        expected = [value for key, value in summary['input_sha256'].items()
                    if key.replace('\\', '/').endswith('/' + relative)]
        if len(expected) != 1 or expected[0] != digest(run / relative):
            raise ValueError(f'Report input digest differs: {relative}.')
    return summary, lock, grid, cases, paths


def style_axis(ax):
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(labelsize=8)
    ax.grid(axis='y', color='#D9E0E6', linewidth=.6, alpha=.7)
    ax.set_axisbelow(True)


def draw_development(ax, lock, grid, cases):
    style_axis(ax)
    categories = [
        ('Endpoint controls', [row for row in grid if not row['eligible']],
         '#89939F', '^', .34, 19),
        ('Rejected hybrids', [row for row in grid if row['eligible'] and not row['feasible']],
         '#BE5E60', 'x', .45, 17),
        ('Feasible hybrids', [row for row in grid if row['eligible'] and row['feasible']],
         '#087E8B', 'o', .65, 22),
    ]
    for label, rows, color, marker, alpha, size in categories:
        if rows:
            ax.scatter([row['misses'] for row in rows],
                       [100 * row['accuracy'] for row in rows],
                       c=color, marker=marker, s=size, alpha=alpha,
                       linewidths=.7, label=f'{label} ({len(rows)})')
    stage1, final = lock['stage1_winner'], lock['winner']
    different_feature = stage1['feature_id'] != final['feature_id']
    if different_feature:
        ax.scatter(stage1['misses'], 100 * stage1['accuracy'], s=105,
                   facecolors='none', edgecolors='#183B48', marker='D',
                   linewidths=1.3, zorder=5, label='Stage 1 winner')
    ax.scatter(final['misses'], 100 * final['accuracy'], s=155,
               c='#6A4C93', edgecolors='white', marker='*', linewidths=.7,
               zorder=6, label='Locked global winner')
    anomalous = sum(bool(row['label']) for row in cases)
    ax.set_xlabel(f'Missed defect inspections (of {anomalous})', fontsize=9)
    ax.set_ylabel('Development accuracy (%)', fontsize=9)
    ax.set_title('a  Development search: 768 settings', loc='left', fontsize=10, fontweight='bold')
    ax.legend(loc='lower left', fontsize=6.9, frameon=True, framealpha=.9,
              edgecolor='#E4E7EB', markerscale=.85)
    note = 'Points overlap; development estimates follow selection.'
    if different_feature:
        note += '\nGlobal star adds the locked Stage 2 representation.'
    ax.text(.01, 1.02, note, transform=ax.transAxes, fontsize=6.8, color='#475569')


def draw_categories(ax, summary):
    style_axis(ax)
    rows = summary['category_metrics']
    groups = sorted({(row['dataset'], row['category']) for row in rows})
    table = {(row['dataset'], row['category'], row['method']): row for row in rows}
    locations = np.arange(len(groups))
    for offset, method in enumerate(('original', 'fixed_avg', 'selected')):
        values = [100 * number(table[dataset, category, method]['accuracy'], 'category accuracy')
                  for dataset, category in groups]
        positions = locations + (offset - 1) * .24
        bars = ax.bar(positions, values, .23, color=METHOD_COLORS[method],
                      label=METHOD_LABELS[method], edgecolor='white', linewidth=.4)
        for bar, value in zip(bars, values):
            ax.text(bar.get_x() + bar.get_width()/2, value + 1.0, f'{value:.1f}',
                    ha='center', va='bottom', fontsize=6.4)
    dataset_labels = {'mvtec_ad': 'MVTec', 'visa': 'VisA'}
    ax.set_xticks(locations, [f'{dataset_labels.get(dataset, dataset)}\n{category}'
                             for dataset, category in groups], fontsize=7)
    ax.set_ylim(0, 108)
    ax.set_ylabel('Verification accuracy (%)', fontsize=9)
    ax.set_title('b  Verification in five seen categories', loc='left', fontsize=10, fontweight='bold')
    ax.legend(loc='lower left', fontsize=7, frameon=True, framealpha=.9,
              edgecolor='#E4E7EB')


def draw_comparisons(forest, count_ax, summary):
    style_axis(forest)
    comparators = ('original', 'fixed_avg')
    extents = [0.]
    transition_rows, evidence = [], {}
    for position, comparator in zip((1, 0), comparators):
        entry = summary['comparisons'][comparator]
        interval = entry['paired_accuracy']
        if not np.isclose(interval['confidence_level'], .95):
            raise ValueError('The figure labels 95% intervals; report confidence differs.')
        estimate = 100 * number(interval['estimate'], 'paired gain')
        lower, upper = [100 * number(value, 'paired interval') for value in interval['interval']]
        if lower > upper:
            raise ValueError('Reversed paired interval.')
        # Draw point and endpoints independently: percentile intervals need not
        # contain the point estimate, and negative errorbar lengths are invalid.
        forest.hlines(position, lower, upper, color=METHOD_COLORS['selected'], linewidth=2)
        forest.vlines((lower, upper), position - .075, position + .075,
                      color=METHOD_COLORS['selected'], linewidth=1)
        forest.plot(estimate, position, 'o', color=METHOD_COLORS['selected'], markersize=6)
        forest.text(estimate, position + .19,
                    f'{estimate:+.2f} [{lower:+.2f}, {upper:+.2f}]',
                    fontsize=7.5, ha='center', color='#334155')
        extents.extend([lower, upper, estimate])
        lost = entry['transitions']['detected_to_missed']
        gained = entry['transitions']['missed_to_detected']
        transition_rows.append([METHOD_LABELS[comparator],
                                f"{lost['records']} cases\n{lost['unique_queries']} images",
                                f"{gained['records']} cases\n{gained['unique_queries']} images"])
        evidence[comparator] = {'estimate': interval['estimate'],
                                'interval': interval['interval'],
                                'detected_to_missed': lost,
                                'missed_to_detected': gained}
    lower, upper = min(extents), max(extents)
    padding = max(1., .15 * (upper - lower))
    forest.set_xlim(lower - padding, upper + padding)
    forest.axvline(0, color='#64748B', linestyle='--', linewidth=.9)
    forest.set_yticks([1, 0], [f'vs {METHOD_LABELS[name]}' for name in comparators], fontsize=8)
    forest.set_ylim(-.4, 1.6)
    forest.set_xlabel('Selected accuracy gain (percentage points)', fontsize=8.5)
    forest.set_title('c  Paired gain and detection transitions', loc='left',
                     fontsize=10, fontweight='bold')
    forest.text(.02, 1.02, '95% conditional query/support bootstrap intervals',
                transform=forest.transAxes, fontsize=6.8, color='#475569')
    count_ax.set_axis_off()
    table = count_ax.table(cellText=transition_rows,
                           colLabels=['Comparator', 'Detected→missed', 'Missed→detected'],
                           cellLoc='center', colLoc='center', bbox=[0, .05, 1, .90],
                           colWidths=[.36, .32, .32])
    table.auto_set_font_size(False)
    table.set_fontsize(7)
    for (row, column), cell in table.get_celld().items():
        cell.set_edgecolor('#D9E0E6')
        cell.set_linewidth(.6)
        if row == 0:
            cell.set_facecolor('#EFF3F6')
            cell.set_text_props(fontweight='bold')
    count_ax.text(0, -.18, 'Cases repeat across draws; lost/restored image sets may overlap.',
                  transform=count_ax.transAxes, fontsize=6.5, color='#475569')
    return evidence


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run-dir', type=Path, required=True)
    parser.add_argument('--output-prefix', type=Path,
                        help='Default: RUN/figures/safal_tuning_overview')
    args = parser.parse_args()
    run = args.run_dir.expanduser().resolve()
    summary, lock, grid, cases, paths = load_completed(run)
    prefix = args.output_prefix or run/'figures'/'safal_tuning_overview'
    prefix.parent.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9,
                         'pdf.fonttype': 42, 'ps.fonttype': 42,
                         'axes.titlepad': 22, 'figure.facecolor': 'white'})
    fig = plt.figure(figsize=(16, 6.8))
    layout = GridSpec(1, 3, figure=fig, width_ratios=[1.05, 1.12, 1.05],
                      left=.055, right=.985, top=.80, bottom=.25, wspace=.36)
    development_ax = fig.add_subplot(layout[0, 0])
    categories_ax = fig.add_subplot(layout[0, 1])
    comparison_layout = layout[0, 2].subgridspec(2, 1, height_ratios=[2.1, 1.4], hspace=.45)
    forest_ax = fig.add_subplot(comparison_layout[0])
    counts_ax = fig.add_subplot(comparison_layout[1])
    draw_development(development_ax, lock, grid, cases)
    draw_categories(categories_ax, summary)
    comparisons = draw_comparisons(forest_ax, counts_ax, summary)
    fig.suptitle('SAFAL: development search and locked image verification',
                 x=.055, ha='left', y=.97, fontsize=15, fontweight='bold')
    fig.text(.055, .92,
             'Five development-exposed categories · 100 verification images · '
             '3 support draws · k=4 + 4 normal calibration images',
             fontsize=9, color='#475569')
    fixed_interval = summary['comparisons']['fixed_avg']['paired_accuracy']['interval']
    if fixed_interval[0] <= 0 <= fixed_interval[1]:
        fig.text(.055, .875,
                 'The conditional accuracy interval versus fixed averaging includes zero; an accuracy improvement is not established.',
                 fontsize=8.5, color='#6B3D44')
    fig.text(.055, .105,
             'Development labels selected one global recipe. Verification uses unused known-history image IDs '
             'within the same categories; it is not a pristine category holdout.\n'
             'Repeated inspections are dependent. Intervals are conditional on sampled categories and observed '
             'query/support units. No source-error probability head is applied.',
             fontsize=8, linespacing=1.5, color='#475569')
    png, pdf = Path(str(prefix)+'.png'), Path(str(prefix)+'.pdf')
    fig.savefig(png, dpi=300, facecolor='white', bbox_inches='tight')
    fig.savefig(pdf, facecolor='white', bbox_inches='tight',
                metadata={'Title': 'SAFAL development search and locked image verification',
                          'Subject': 'Conditional validation in five development-exposed categories',
                          'Creator': 'Standalone Matplotlib evidence plotting helper'})
    plt.close(fig)
    metadata = {'figure_png': str(png), 'figure_pdf': str(pdf),
                'input_sha256': {str(path): digest(path) for path in paths.values()},
                'helper_sha256': digest(Path(__file__)), 'grid_cells': len(grid),
                'verification_counts': summary['counts'],
                'development_stage1_winner': lock['stage1_winner'],
                'global_locked_winner': lock['winner'], 'comparisons': comparisons,
                'parameters_fitted_or_selected_by_plotter': False,
                'scope': 'Recorded development search and conditional held-out-image comparison; no full-benchmark, SOTA or production claim.'}
    metadata_path = Path(str(prefix)+'.metadata.json')
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True, allow_nan=False)+'\n')
    print(json.dumps({'png': str(png), 'pdf': str(pdf), 'metadata': str(metadata_path)}, indent=2))


if __name__ == '__main__':
    main()
