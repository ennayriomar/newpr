"""Plot actual pilot results; support-draw ranges are descriptive, not confidence intervals."""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR', '/workspace/.cache/matplotlib')
os.environ.setdefault('XDG_CACHE_HOME', '/workspace/.cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    results = json.loads(args.results.read_text())
    figure, axes = plt.subplots(1, 2, figsize=(10, 4), constrained_layout=True)
    for (dataset, category) in sorted({(r['dataset'], r['category']) for r in results}):
        selected = [r for r in results if r['dataset'] == dataset and r['category'] == category]
        shots = sorted({r['shots'] for r in selected})
        for axis, metric, label in zip(axes, ['image_auroc', 'pixel_ap'], ['Image AUROC', 'Pixel AP']):
            values = [[r[metric] for r in selected if r['shots'] == k] for k in shots]
            axis.plot(shots, [np.mean(v) for v in values], marker='o', label=f'{dataset}/{category}')
            axis.fill_between(shots, [min(v) for v in values], [max(v) for v in values], alpha=.15)
            axis.set(xlabel='Normal reference images (strict fixed-shot)', ylabel=label, ylim=(-.02, 1.02), xticks=shots)
            axis.grid(alpha=.2)
    axes[0].legend(fontsize=8)
    figure.suptitle('Feasibility pilot: 8 fixed queries/category; mean and range over 3 support draws')
    args.output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(args.output, dpi=200)
    figure.savefig(args.output.with_suffix('.pdf'))


if __name__ == '__main__':
    main()
