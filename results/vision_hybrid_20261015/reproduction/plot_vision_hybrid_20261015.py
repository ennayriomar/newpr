"""Export measured category comparisons, without dataset imagery."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

run=Path('/tmp/vision_hybrid_20261015')
summary=json.loads((run/'summary.json').read_text())
measurements=json.loads((run/'verification_metrics.json').read_text())
categories=sorted({(r['dataset'],r['category']) for r in measurements})
fig,axes=plt.subplots(1,2,figsize=(11,4.8),layout='constrained')
x=np.arange(len(categories));width=.34;colors=['#62798d','#cc6329']
for axis,field,title in zip(axes,['auroc','pixel_ap'],['Image AUROC','Pixel average precision (cropped ROI)']):
    for j,method in enumerate(['baseline','hybrid']):
        values=[]
        for dataset,category in categories:
            rows=[r for r in measurements if (r['dataset'],r['category'],r['method'])==(dataset,category,method)]
            assert len(rows)==2
            values.append(100*np.mean([r['detection']['auroc'] if field=='auroc' else r['localization'][field] for r in rows]))
        axis.bar(x+(j-.5)*width,values,width,label='Search' if j==0 else 'Search + PCA',color=colors[j])
    axis.set(xticks=x,xticklabels=[c.replace('_',' ') for _,c in categories],ylim=(0,105),ylabel='Percent',title=title)
    axis.tick_params(axis='x',rotation=25);axis.grid(axis='y',alpha=.2);axis.set_axisbelow(True)
    axis.spines[['top','right']].set_visible(False)
axes[0].legend(loc='lower left',frameon=False)
auc=summary['paired_image_auroc']
fig.suptitle('Locked one-shot study: 100 image IDs, five reserved categories, two reference draws',fontsize=12)
fig.text(.5,-.04,f"Paired image AUROC change: {100*auc['estimate']:+.2f} pp; conditional 95% interval [{100*auc['interval'][0]:+.2f}, {100*auc['interval'][1]:+.2f}] pp. Full paper benchmark not run.",ha='center',fontsize=9)
for extension in ['png','pdf']:fig.savefig(run/('comparison.'+extension),dpi=180,bbox_inches='tight')
plt.close(fig)
print('Exported comparison.png and comparison.pdf',flush=True)
