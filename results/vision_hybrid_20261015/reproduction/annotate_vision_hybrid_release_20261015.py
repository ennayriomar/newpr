"""Add release context without changing frozen selection or measured values."""
from pathlib import Path
import json
import shutil

run=Path('/tmp/vision_hybrid_20261015');tools=Path('/workspace/tools')
summary=json.loads((run/'summary.json').read_text());a=summary['methods']['baseline'];b=summary['methods']['hybrid']
auc=summary['paired_image_auroc'];marker='## Completed study — 15 October 2026'
guide=tools/'docs/vision_hybrid.md';text=guide.read_text();assert marker not in text
text+=f'''

{marker}

The frozen winner is the global PCA control: one cluster, 95% retained
variance, correction strength 0.5 and a uniform gate. Local and gated variants
were eligible but did not win. Development image AUROC is 93.00% for search
and 93.30% for the winner; development pixel AP is 0.4416 and 0.4565.

Reserved-image measurements (100 unique image IDs, five other categories,
two reference draws, 200 paired cases):

| Metric | Same-feature search | Selected search + PCA |
|---|---:|---:|
| Mean image AUROC | {100*a['mean_image_auroc']:.2f}% | {100*b['mean_image_auroc']:.2f}% |
| Accuracy at shared source cutoff | {100*a['accuracy']:.2f}% | {100*b['accuracy']:.2f}% |
| Mean cropped-ROI pixel AP | {a['localization']['pixel_ap']:.4f} | {b['localization']['pixel_ap']:.4f} |
| Mean cropped-ROI AU-PRO | {a['localization']['au_pro']:.4f} | {b['localization']['au_pro']:.4f} |
| Missed anomaly cases (100) | {a['misses']} | {b['misses']} |
| False alarms (100 normal cases) | {a['false_positives']} | {b['false_positives']} |

Paired hybrid-minus-search image AUROC: {100*auc['estimate']:+.2f} percentage
points, with conditional 95% interval [{100*auc['interval'][0]:+.2f},
{100*auc['interval'][1]:+.2f}]. Categories are fixed and two support draws limit
replication. {'The interval excludes zero within this bounded cohort.' if auc['interval'][0]>0 else 'The interval includes zero; an AUROC gain is not established.'}
There are {len(summary['transitions']['detected_to_missed'])} lost baseline
anomaly alerts, {len(summary['transitions']['missed_to_detected'])} recovered
anomaly cases and {len(summary['transitions']['false_positives_added'])} added
false alarms. No parameters were changed using these outcomes.

The source selection budget is 50 normal plus 50 anomalous development
images and masks; it is additional supervision beyond fitting each target
bank with one normal. Original image labels are retained even if the center
crop removes a defect. This is not the full paper benchmark and does not
establish paper superiority. Prior SAFAL pilot scores used different cohorts
and support budgets and are not matched comparisons to this study.

The compact ZIP includes complete code, licensed Meta source and the fixed
bottle/seed17 bank. All 20 fitted banks, branch outputs, 10 feature probes and
200 map archives are distributed in the complete TAR.GZ archive. Use
`download_vision_hybrid_results.py --ref PAYLOAD_COMMIT --extract`, with the
immutable payload commit recorded in the repository publication record.
'''
guide.write_text(text)
report=run/'report.md';text=report.read_text()
text=text.replace('# Register-DINO search and local-PCA correction: measured study',
                  '# Register-DINO search with the selected global PCA correction')
text=text.replace('uses100','uses 100').replace('conditional95%','conditional 95%')
text+='''

## Selection supervision and release checks

The selected correction is global (one cluster), with a uniform gate. Local
and gated controls were eligible but did not win. Selection uses 50 normal
and 50 anomalous development images plus masks from five source categories;
normal-only refers to each target bank's fitting budget. This source
supervision must be declared when comparing methods.

All 198 unit and contract tests passed. The pretrained encoder's early-stop
features were bitwise equal to pinned official intermediate features in a
real-image parity check. The separate artifact audit records fitted-model
and feature-probe replays, 200 map/score replays, native-mask checks and
metric recomputation. These checks are not a complete independent rerun or a
full-dataset benchmark. Raw datasets and external weights are separate.

![Measured category comparison](comparison.png)
'''
report.write_text(text)
shutil.copy2(guide,run/'reproduction/tools/docs/vision_hybrid.md')
for name in ['evaluation','development','plan','pre_audit','prepare_replay','release_unit_tests']:
    source=Path('/tmp')/f'vision_hybrid_20261015_{name}.log'
    if source.exists():shutil.copy2(source,run/(name+'.log'))
for source in sorted(Path('/tmp').glob('*vision_hybrid*20261015.py')):
    if source.is_file():shutil.copy2(source,run/'reproduction'/source.name)
print('Annotated measured report and completed-study guide; frozen numerical outputs unchanged.',flush=True)
