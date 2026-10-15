"""Plot executed acquisition summaries without claiming statistical confidence."""
import argparse
import json
import os
from pathlib import Path

os.environ.setdefault('MPLCONFIGDIR','/workspace/.cache/matplotlib')
os.environ.setdefault('XDG_CACHE_HOME','/workspace/.cache')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--results',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    results=json.loads(args.results.read_text())
    policies=['none','random','nearest_global','diversity','oracle']
    labels=['None\nb=0','Random\nb=1','Nearest\nb=1','Diversity\nb=1','Oracle*\nb=1']
    figure,axes=plt.subplots(2,3,figsize=(12,7),constrained_layout=True)
    for row,dataset in enumerate(['mvtec_ad','visa']):
        selected=[r for r in results if r['dataset']==dataset]
        for axis,metric,title in zip(axes[row],['image_auroc','pixel_ap','mean_offline_benefit'],['Image AUROC','Pixel AP','Declared-loss benefit']):
            values=[[r[metric] for r in selected if r['policy']==policy] for policy in policies]
            means=np.array([np.mean(v) for v in values])
            errors=np.array([means-np.array([min(v) for v in values]),np.array([max(v) for v in values])-means])
            axis.bar(range(len(policies)),means,yerr=errors,capsize=3,color=['gray','steelblue','seagreen','darkorange','mediumpurple'])
            axis.set(xticks=range(len(policies)),xticklabels=labels,title=f'{dataset}: {title}')
            axis.grid(axis='y',alpha=.2)
    figure.suptitle('One added reference per query; same 16-image pool. Bars: mean/range across 3 support draws.\n*Oracle uses evaluation labels and is unattainable at deployment; benefit is not an AUROC oracle.')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    figure.savefig(args.output,dpi=200)
    figure.savefig(args.output.with_suffix('.pdf'))


if __name__=='__main__':
    main()
