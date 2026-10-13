"""Plot actual metrics across support draws, without population CI claims."""
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
    p=argparse.ArgumentParser(description=__doc__); p.add_argument('--run',type=Path,required=True); p.add_argument('--output',type=Path,required=True); a=p.parse_args()
    rows=json.loads((a.run/'metrics.json').read_text()); categories=list(dict.fromkeys((r['dataset'],r['category'],r['role']) for r in rows))
    methods={'transparent_nn':'Transparent NN','anomalydino':'AnomalyDINO core','subspacead':'SubspaceAD core','support_hybrid':'Hybrid'}
    colors=['#67727a','#3177ae','#db862c','#3c9774']
    fig,axes=plt.subplots(len(categories),3,figsize=(14,3*len(categories)),squeeze=False)
    for row,(d,c,role) in enumerate(categories):
        for column,(level,key,title) in enumerate([('image','auroc','Image AUROC'),('pixel','ap','Pixel AP'),('image','locked_f1','Image F1 at calibration cutoff')]):
            ax=axes[row,column]
            for (method,label),color in zip(methods.items(),colors):
                means,low,high=[],[],[]
                for k in [1,2,4]:
                    vals=[r[level][key] for r in rows if r['dataset']==d and r['category']==c and r['method']==method and r['shots']==k and r[level][key] is not None]
                    means.append(np.mean(vals)); low.append(min(vals)); high.append(max(vals))
                errors=np.maximum(np.array([np.array(means)-low,np.array(high)-means]),0)
                ax.errorbar([1,2,4],means,yerr=errors,label=label,color=color,marker='o',capsize=3,alpha=.85)
            ax.set_xticks([1,2,4]); ax.set_xlabel('Normal reference images k'); ax.set_title(f'{d}/{c} ({role})\n{title}',fontsize=10); ax.grid(alpha=.2)
            if column!=1: ax.set_ylim(-.03,1.03)
    handles,labels=axes[0,0].get_legend_handles_labels(); fig.legend(handles,labels,loc='upper center',ncol=4,bbox_to_anchor=(.5,.974))
    fig.suptitle('Real-data feasibility pilot: common ViT-B/14 at 224; four queries/category\nMean/range over three support draws; official core variants, not published-table reproductions',fontsize=12,y=.998)
    fig.tight_layout(rect=(0,0,1,.955)); a.output.parent.mkdir(parents=True,exist_ok=True); fig.savefig(a.output,dpi=150); fig.savefig(a.output.with_suffix('.pdf')); plt.close(fig)
    fig,axes=plt.subplots(1,len(categories),figsize=(4*len(categories),4),squeeze=False)
    for index,(d,c,role) in enumerate(categories):
        ax=axes[0,index]
        for k,color in zip([1,2,4],['#bd4a4a','#3177ae','#3c9774']):
            vals=[r for r in rows if r['dataset']==d and r['category']==c and r['method']=='support_hybrid' and r['shots']==k]
            for j,r in enumerate(vals):
                points=[p for p in r['adequacy_precision']['curve'] if p['precision_correct_decision'] is not None]
                ax.plot([p['coverage'] for p in points],[p['precision_correct_decision'] for p in points],marker='.',color=color,alpha=.5,label=f'k={k}' if j==0 else None)
        ax.set_title(f'{d}/{c}'); ax.set_xlim(-.02,1.02); ax.set_ylim(-.02,1.02); ax.set_xlabel('Accepted fraction'); ax.set_ylabel('Correct image decision fraction'); ax.grid(alpha=.2); ax.legend()
    fig.suptitle('Adequacy threshold curves: correctness at locked detector cutoff\nProxy event, not ground-truth adequacy; same four queries per curve',fontsize=12)
    fig.tight_layout(rect=(0,0,1,.85)); fig.savefig(a.output.with_name('adequacy_correctness_curves.png'),dpi=150); fig.savefig(a.output.with_name('adequacy_correctness_curves.pdf')); plt.close(fig)
    print(str(a.output))


if __name__=='__main__': main()
