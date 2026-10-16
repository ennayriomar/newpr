# VisionAD-style outputs

The dataset-specific entry points now save diagnostic PNGs and print the
reference repository's seven metric names in four-decimal form:

```text
bottle: I-Auroc:..., I-AP:..., I-F1:..., P-AUROC:..., P-AP:..., P-F1:..., P-AUPRO:...
Mean: I-Auroc:..., I-AP:..., I-F1:..., P-AUROC:..., P-AP:..., P-F1:..., P-AUPRO:...
```

Values are fractions on a 0–1 scale. NA means a metric is unavailable, rather
than a placeholder zero. Baseline and hybrid each get their own block.
I-F1 and P-F1 are descriptive **evaluation F1-max**, as in benchmark reporting.
They do not change the model's source-derived operating cutoffs. Accuracy,
false-alarm rate and F1 at those fixed cutoffs remain separately reported in
`metrics.json`, `results.json` and the console log.

## Run evaluation

```bash
python hybrid_mvtec_test.py --run-dir runs/bottle \
  --save_dir saved_results --save_name bottle_run

python hybrid_visa_test.py --run-dir runs/capsules \
  --save_dir saved_results --save_name capsules_run
```

`evaluate.py` is the generic entry point with the same presentation.
Localization, raw map saving and visualizations are enabled by default in
these commands. Use `--no-visualize` to omit PNGs, and `--no-localization` to
omit pixel metric computation. Existing `test.py` retains its original raw
JSON interface and checkpoint compatibility.

For a quick explicitly marked smoke subset:

```bash
python hybrid_mvtec_test.py --run-dir runs/bottle --max-images 2 \
  --save_dir saved_results --save_name bottle_smoke
```

## Files

```text
saved_results/bottle_run/
  result.log
  metrics.csv
  metrics.md
  metrics.json             # Original fixed-cutoff evaluation
  predictions.jsonl
  results.json             # Presentation and descriptive F1-max
  map-00000.npz            # Unchanged raw scores and cropped truth
  vis_compound_1/
    bottle/
      broken_large/
        000__<id>_ori.png
        000__<id>_gt.png
        000__<id>_global.png
        000__<id>_local.png
        000__<id>_gt_red.png
        000__<id>_compound.png
        000__<id>_raw.npz
        000__<id>_metadata.json
```

The short ID avoids collisions between native filenames. Healthy images are
also exported, with an empty ground-truth mask. `--max-visualizations N`
limits rendered cases without changing which images are scored or the
normalization range.

The five individual images match the reference's output types. The compound
PNG places them in a labeled row. Every panel uses the **same scored center
crop**, resized to 256×256; maps are not stretched over unscored image borders.
Global heatmaps use the raw hybrid map range across this category/draw's
evaluated images. Local heatmaps use each image's own display range. Global
and local refer to visualization scaling, not different PCA models. Neither
normalization changes raw maps, metric calculations, decisions or probabilities.
High local color contrast alone does not establish an anomaly.
The compound labels now say **Hybrid: shared scale** and **Hybrid: image
contrast**. The legacy `_global` and `_local` filenames remain compatible.
Both panels display the same hybrid map. Each figure now has an unchanged
raw NPZ with baseline/hybrid/truth and metadata containing its native image
ID, hashes, predictions, cutoff and display bounds.

## Checkable category audit

Record the rules **before** starting a complete category evaluation. Use a
new directory and the same fitted bank throughout:

```bash
mkdir -p saved_results/bottle_audit
python audit_outputs.py --run-dir runs/bottle \
  --prepare-protocol saved_results/bottle_audit/protocol.json
python test.py --run-dir runs/bottle --localization --save-maps \
  --output saved_results/bottle_audit/evaluation
python audit_outputs.py --run-dir runs/bottle \
  --evaluation saved_results/bottle_audit/evaluation \
  --protocol saved_results/bottle_audit/protocol.json \
  --output saved_results/bottle_audit/report
```

The audit requires every native test ID, matching model/cutoff/input hashes
and the original ROI masks. It compares **search baseline vs hybrid**
numerically on every image (max/mean absolute difference), separately from
the difference between display scalings. Figures use one raw score scale
across both methods and normal/defective images; a separate colorbar labels
the additive correction. Each selected image has raw maps and native-ID
metadata beside the figure.

The recorded figure rule picks the lowest-score true-negative normal,
highest-score normal false alarm, smallest positive cropped defect, lowest-score
miss, and lowest cropped-mask IoU. Ties use native IDs. Duplicate cases
retain all selection reasons; an absent event is reported as absent. These
are outcome-selected diagnostic examples, not a random sample.

Image AUROC and ROI AU-PRO receive 95% percentile intervals from 2,000
paired, native-label-stratified **query-image** bootstrap replicates. AU-PRO
uses 8-connected equal-weight regions, pooled normal-pixel FPR and a 0.3 FPR
limit. The original cohort's 128-score-rank grid is fixed in the bootstrap,
so its interval is a sampled-grid approximation. Sufficient statistics,
thresholds and image multiplicities are saved for replay. Intervals are
conditional on this fitted bank and support image; they do not include
support-draw, fitting or category variability.

All native image labels enter image AUROC, but their scores are crop-derived.
Pixel metrics cover only the 392/448 center crop resized to 256×256, not
full-image segmentation. The audit also counts native defect pixels outside
the crop by original pixel-center coordinates. It leaves those borders
unscored and does not fill them with zero-valued predictions.

The [full bottle audit](https://github.com/ennayriomar/newpr/tree/main/heatmap_audit_20261016/report) uses the
previously exposed bottle category and one fixed fitted bank. It does not
retune cutoffs or establish a full-dataset paper comparison.

## Reformat existing saved results

No encoder rerun is needed when the saved raw maps are available:

```bash
python export_outputs.py --run-dir runs/bottle \
  --evaluation runs/bottle/evaluation --output saved_results/bottle_export
```

Existing evaluations need `--save-maps` for image rendering and pixel F1-max.
Without saved maps, `--no-visualize` can export the available tables and pixel
F1-max remains NA. `--data_path` can override a relocated native dataset root;
image SHA256 values must still match the scored inputs.

## Category and mean tables

```bash
python summarize.py --results runs/*/evaluation/results.json \
  --output saved_results/category_summary
```

Collect the files actually produced by `evaluate.py` or the dataset scripts;
adjust the glob if `--save_dir` was used. The summary first averages support
draws within each category, then weights categories equally. Datasets and
methods remain separate. Duplicate cohorts and mixed shot budgets are
rejected. Smoke subsets require an explicit `--include-subsets` flag.
A Mean row represents only the listed categories, not a full-paper result.

[Real visualization examples](output_examples/README.md) are included for
MVTec AD and VisA. They illustrate formatting and do not constitute a new
accuracy experiment. Existing model scores and scientific conclusions remain
unchanged.
