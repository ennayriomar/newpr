# Checkable SAFAL bottle audit — 16 October 2026

[Results, conditional intervals and failure figure](report/README.md) · [Raw metrics](evaluation/metrics.json) · [Validation evidence](VALIDATION.json)

This audit scores every native MVTec AD bottle test image: **83 images, 20 normal and 63 anomalous**, with one normal support image (`bottle/train/good/038.png`, seed 17). Parameters, support bank and source-derived cutoffs are unchanged. The category has prior research exposure; this is descriptive evaluation of one fitted bank.

- `protocol.json` and `protocol.sha256`: rules/IDs/interval settings recorded before full-category inference; the figure rule chooses diagnostic successes and failures, not a random sample.
- `evaluation/`: all 83 raw NPZs (`baseline`, `hybrid`, `truth`, each 256×256); paired native-ID predictions; input image/mask hashes and original metrics. Map order follows first occurrence in predictions.jsonl and ordered_sample_ids in the protocol.
- `report/`: per-image numerical branch comparisons, shared-scale normal/failure figure, raw selected-case arrays and native-ID metadata beside it, conditional bootstrap intervals, multiplicities and replayable PRO statistics.
- `tables/`: original seven-column output style; F1-max columns are descriptive only and never alter operating cutoffs. Mean covers this one category.
- `provenance/`: fitted-bank metadata and training-interface hashes. The unchanged model NPZ and external encoder weights are separate downloads.
- `smoke_export_check/`: a two-image formatting/preservation check, not the full category result.
- `root_tests.log`, `subset_guard_check.json`, `smoke_raw_preservation_check.json`: validation evidence. Nineteen root tests pass; an attempt to present a smoke subset as a complete category is rejected.

The old “Global/Local” heatmaps are shared/per-image display scalings of the same hybrid map. The new figure compares actual search and hybrid raw maps with shared bounds, with a separately labeled additive-difference scale.

**Pixel metrics cover only the center crop, 76.56% of resized image area.** Four native masks have 15,668 defect pixels outside that crop. Image AUROC uses every native label, but image scores are also crop-derived. No full-image segmentation claim is made. Query-image bootstrap intervals are conditional on this fitted bank; AU-PRO intervals use the original fixed sampled threshold grid.

[Current source ZIP](https://github.com/ennayriomar/newpr/raw/refs/heads/main/safal_visionad_style_code.zip) contains audit_outputs.py and the documented prepare/evaluate/audit workflow in docs/OUTPUTS.md.
[Unchanged fixed bottle bank download](https://github.com/ennayriomar/newpr/raw/0d0b1db6c0133d3876bd18cc9920f930dfeb2519/vision_hybrid_20261015.zip): `vision_hybrid/model/model.npz` has SHA256 `78eceb8a82304b328d7dd2ed5e724dff4d7e1ae4501f58cba92326d47c689e17`. The 1.22 GB DINOv2 checkpoint and native dataset images are external assets. They are not duplicated in this audit bundle.

MVTec Software GmbH; Bergmann et al., *MVTec AD*, CVPR 2019. Derived images, masks and score maps retain **CC BY-NC-SA 4.0**. [Dataset](https://www.mvtec.com/research-teaching/datasets/mvtec-ad) · [License](https://creativecommons.org/licenses/by-nc-sa/4.0/). Derived image modifications: center crop/resize, raw-map color overlays, GT panels and labels. Existing code licensing is unchanged.
