"""Render descriptive SAFAL pilot figures and a report from measured records."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

from safe_iad.experiment_io import read_jsonl, write_json
from safe_iad.research_metrics import risk_coverage
from safe_iad.safal_calibration import probability_metrics


def render(run, output):
    summary = json.loads((run/'summary.json').read_text())
    calibration = json.loads((run/'calibration_report.json').read_text())
    rows = read_jsonl(run/'predictions.jsonl')
    selected = [r for r in rows if r['method'] == 'safal']
    errors = np.array([r['predicted_anomaly'] != r['label'] for r in selected], dtype=int)
    probabilities = np.array([r['error_probability'] for r in selected])
    diagnostic = risk_coverage(errors, 1-np.array([r['U'] for r in selected]))
    proxy = risk_coverage(errors, 1-probabilities)
    accepted = np.array([r['action'] != 'abstain' for r in selected])
    derived = dict(native_binary_error_probability_metrics=probability_metrics(errors, probabilities),
                   diagnostic_risk_coverage=diagnostic, source_proxy_probability_risk_coverage=proxy,
                   accepted_inspections=int(accepted.sum()), inspections=len(selected),
                   accepted_error_rate=float(errors[accepted].mean()) if accepted.any() else None,
                   records_are_dependent=True, unique_images=summary['unique_native_queries'],
                   native_probability_calibration_claim=False,
                   statistical_scope='descriptive correlated inspection records, conditional on eight images and two draws')
    output.mkdir(parents=True, exist_ok=True)
    write_json(output/'descriptive_reliability.json', derived)
    figures = output/'figures'; figures.mkdir(exist_ok=True)
    methods = list(summary['mean_episode_metrics'])
    labels = ['Search', 'Subspace', 'Fixed avg', 'Max', 'SAFAL']
    fig, axes = plt.subplots(1, 2, figsize=(10, 3.6), layout='constrained')
    for ax, key, title in zip(axes, ['accuracy', 'pixel_ap'], ['Image accuracy at locked cutoffs', 'Pixel AP at 256 × 256']):
        values = [summary['mean_episode_metrics'][m][key] for m in methods]
        ax.bar(labels, values, color=['#8bb5d9', '#6f9d73', '#888888', '#c28c65', '#7467a7'])
        ax.set_ylim(0, 1); ax.set_title(title); ax.set_ylabel('Mean over 16 episodes')
        for i, value in enumerate(values):
            ax.text(i, value+.015, f'{value:.3f}', ha='center', fontsize=9)
    fig.suptitle('Small paired validation pilot: 8 unique images; no accuracy gain established', fontsize=11)
    for suffix in ('png', 'pdf'):
        fig.savefig(figures/f'comparison.{suffix}', dpi=180)
    plt.close(fig)
    fig, ax = plt.subplots(figsize=(6, 3.6), layout='constrained')
    for curve, label in ((diagnostic, 'Diagnostic uncertainty'), (proxy, 'Source proxy error model')):
        points = [p for p in curve['curve'] if p['risk'] is not None]
        ax.step([p['coverage'] for p in points], [p['risk'] for p in points], where='pre', label=label)
    ax.set(xlim=(0, 1), ylim=(0, max(.1, float(errors.mean())*2)), xlabel='Accepted coverage', ylabel='Image decision error rate',
           title='Descriptive risk–coverage: 64 dependent inspections / 8 images')
    ax.legend(); ax.grid(alpha=.2)
    for suffix in ('png', 'pdf'):
        fig.savefig(figures/f'risk_coverage.{suffix}', dpi=180)
    plt.close(fig)
    table = '\n'.join(f"| {m} | {summary['mean_episode_metrics'][m]['accuracy']:.6f} | {summary['mean_episode_metrics'][m]['image_auroc']:.6f} | {summary['mean_episode_metrics'][m]['pixel_ap']:.6f} |" for m in methods)
    report = f'''# Complete SAFAL implementation: measured validation pilot

SAFAL v0.5.0 executes frozen verified DINOv2 features, raw PCA and cosine-search branches, five paired fusion/control outputs, bounded compatibility/uncertainty diagnostics, separate source-proxy error estimation, model serialization and train/evaluate/predict commands. It is a working independent research prototype. Published recipes and full benchmarks have not been reproduced.

The adaptive method did **not** improve accuracy over fixed averaging in this run, and the subspace branch performed better. No parameters were retuned after reading these outcomes. The mean image AUROC and pixel AP also provide no general advantage for SAFAL.

| Method | Image accuracy | Image AUROC | Pixel AP |
| --- | ---: | ---: | ---: |
{table}

These are means over {summary['episodes']} episodes: hazelnut (MVTec AD), pcb2 (VisA), k=1/2/4/8, seeds 5/13. The {summary['prediction_records']} method records contain 64 correlated inspections of **eight unique images**, four normal and four anomalous. They are not 320 independent test images. Each inspection uses k original normal supports and four additional normal training calibration images; this is a k+4 target-normal information budget. Support banks and query sets are shared by all five methods. The sampled categories are held fixed. Nested k results are averaged within each query/seed before the descriptive crossed bootstrap; its zero interval here reflects identical observed accuracy decisions and does not establish population equivalence.

The extractor uses the actual checksum-verified frozen DINOv2 ViT-B/14 checkpoint, RGB square224, raw mean of zero-based blocks 2/5/8/11, identity support views. These adaptations differ from original SubspaceAD and VisionAD recipes. No unlicensed VisionAD source is copied. PCA fits raw normal support features and retains 99% explained variance. Four distinct normal empirical 95th-percentile cutoffs normalize branch image and patch evidence; a small calibration sample does not guarantee a false-alarm rate.

Native images are processed for features; evaluation maps are bilinearly restored to **256×256**, with masks resized by nearest neighbor. Evaluation AUROC/AP/AUPRO/IoU are therefore measured in that declared metric space. The predict command separately exports native-resolution maps. Image scores aggregate the top floor1% patch evidence. Every target label/mask enters reporting only after prediction. No final-category labels fit the model, cutoffs, weights or proxy error estimator.

The optional error estimator fits 48 source rows from 24 original normal-image parents and evaluates 16 untouched source rows from eight other parents. Each parent contributes a normal and a deterministic CutPaste sibling; four source categories are carpet/grid/candle/cashew. There were only {calibration['fit_class_counts']['1']} fitting error events and {calibration['calibration_class_counts']['1']} heldout proxy error events. This sparse supervision and synthetic/native domain shift prevent a native calibration claim. Adequacy A and uncertainty U remain bounded branch-compatibility diagnostics, not probabilities of correctness or validated missing-support causes. Leave-image-out sensitivity is explicitly missing at k=1. Weighted fusion can suppress branch evidence; raw branches and the max control remain available.

At the predeclared proxy-error abstention cutoff 0.2, {derived['accepted_inspections']}/{derived['inspections']} native inspection records were accepted, with observed accepted error rate {derived['accepted_error_rate']}. This is descriptive evidence over the same eight images, not a deployment risk bound. Full risk–coverage and probability-event metrics are in descriptive_reliability.json; figures retain these dependence limits.

Verification is reported separately in verification/: unit/contract tests, trained-model CLI replay, exact real-feature portability checks and the independent artifact/probe audit. Real checkpoint weights and datasets remain separate downloads. The ZIP contains two genuinely fitted k2/seed5 example normal-bank checkpoints plus all current source, configurations, licensed vendor sources and compact measured reports. Raw image data, feature caches and all native/intermediate map arrays are excluded. Copied reports are inspection evidence; a new benchmark requires its own verified inputs and new output directory.

Real-IAD, a full MVTec/VisA/AD2 benchmark, private AD2 server scoring, original large/register encoder recipes, broad shift tests and validated support-adequacy targets remain outstanding. The current CPU environment and available storage cannot establish those outcomes. Historical M3 negative results and all earlier public archives are preserved.
'''
    (output/'research_report.md').write_text(report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--run', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    render(args.run, args.output)
