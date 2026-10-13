# Complete SAFAL implementation: measured validation pilot

SAFAL v0.5.0 executes frozen verified DINOv2 features, raw PCA and cosine-search branches, five paired fusion/control outputs, bounded compatibility/uncertainty diagnostics, separate source-proxy error estimation, model serialization and train/evaluate/predict commands. It is a working independent research prototype. Published recipes and full benchmarks have not been reproduced.

The adaptive method did **not** improve accuracy over fixed averaging in this run, and the subspace branch performed better. No parameters were retuned after reading these outcomes. The mean image AUROC and pixel AP also provide no general advantage for SAFAL.

| Method | Image accuracy | Image AUROC | Pixel AP |
| --- | ---: | ---: | ---: |
| search | 0.875000 | 0.968750 | 0.281660 |
| subspace | 0.968750 | 1.000000 | 0.317101 |
| fixed_avg | 0.937500 | 0.984375 | 0.307248 |
| max | 0.890625 | 1.000000 | 0.325080 |
| safal | 0.937500 | 0.968750 | 0.301433 |

These are means over 16 episodes: hazelnut (MVTec AD), pcb2 (VisA), k=1/2/4/8, seeds 5/13. The 320 method records contain 64 correlated inspections of **eight unique images**, four normal and four anomalous. They are not 320 independent test images. Each inspection uses k original normal supports and four additional normal training calibration images; this is a k+4 target-normal information budget. Support banks and query sets are shared by all five methods. The sampled categories are held fixed. Nested k results are averaged within each query/seed before the descriptive crossed bootstrap; its zero interval here reflects identical observed accuracy decisions and does not establish population equivalence.

The extractor uses the actual checksum-verified frozen DINOv2 ViT-B/14 checkpoint, RGB square224, raw mean of zero-based blocks 2/5/8/11, identity support views. These adaptations differ from original SubspaceAD and VisionAD recipes. No unlicensed VisionAD source is copied. PCA fits raw normal support features and retains 99% explained variance. Four distinct normal empirical 95th-percentile cutoffs normalize branch image and patch evidence; a small calibration sample does not guarantee a false-alarm rate.

Native images are processed for features; evaluation maps are bilinearly restored to **256×256**, with masks resized by nearest neighbor. Evaluation AUROC/AP/AUPRO/IoU are therefore measured in that declared metric space. The predict command separately exports native-resolution maps. Image scores aggregate the top floor1% patch evidence. Every target label/mask enters reporting only after prediction. No final-category labels fit the model, cutoffs, weights or proxy error estimator.

The optional error estimator fits 48 source rows from 24 original normal-image parents and evaluates 16 untouched source rows from eight other parents. Each parent contributes a normal and a deterministic CutPaste sibling; four source categories are carpet/grid/candle/cashew. There were only 2 fitting error events and 1 heldout proxy error events. This sparse supervision and synthetic/native domain shift prevent a native calibration claim. Adequacy A and uncertainty U remain bounded branch-compatibility diagnostics, not probabilities of correctness or validated missing-support causes. Leave-image-out sensitivity is explicitly missing at k=1. Weighted fusion can suppress branch evidence; raw branches and the max control remain available.

At the predeclared proxy-error abstention cutoff 0.2, 64/64 native inspection records were accepted, with observed accepted error rate 0.0625. This is descriptive evidence over the same eight images, not a deployment risk bound. Full risk–coverage and probability-event metrics are in descriptive_reliability.json; figures retain these dependence limits.

Verification is reported separately in verification/: unit/contract tests, trained-model CLI replay, exact real-feature portability checks and the independent artifact/probe audit. Real checkpoint weights and datasets remain separate downloads. The ZIP contains two genuinely fitted k2/seed5 example normal-bank checkpoints plus all current source, configurations, licensed vendor sources and compact measured reports. Raw image data, feature caches and all native/intermediate map arrays are excluded. Copied reports are inspection evidence; a new benchmark requires its own verified inputs and new output directory.

Real-IAD, a full MVTec/VisA/AD2 benchmark, private AD2 server scoring, original large/register encoder recipes, broad shift tests and validated support-adequacy targets remain outstanding. The current CPU environment and available storage cannot establish those outcomes. Historical M3 negative results and all earlier public archives are preserved.
