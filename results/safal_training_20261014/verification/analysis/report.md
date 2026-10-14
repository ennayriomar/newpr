# Executed SAFAL training and development-validation results

SAFAL raw mean image accuracy was 0.7667, compared with fixed_avg at 0.7617. An accuracy improvement over that comparator is not established by this conditional comparison. These are actual outcomes on 100 unique development-validation images, not dataset-wide or deployment performance. Paired evidence: search: delta=0.0283, conditional95%CI=[-0.0050,0.0650]; subspace: delta=0.0267, conditional95%CI=[-0.0075,0.0642]; fixed_avg: delta=0.0050, conditional95%CI=[-0.0167,0.0300]; max: delta=0.0267, conditional95%CI=[-0.0175,0.0709]. No threshold, fusion weight or head hyperparameter was tuned from this run.

Training comprises frozen pretrained DINOv2 feature extraction, normal-reference/PCA fits and logistic error-head learning on 320 source error events from 160 original image parents. The untouched current-fit source audit has 80 rows from 40 parents. This is not LLM or DINO backbone fine-tuning. The source mixture is real normal images plus explicitly synthetic CutPaste derivatives.

There are 60 reference-fit episodes, 3 support-draw seeds, k=[1, 2, 4, 8], 5 sampled reserved-validation categories, 1200 paired query/support/k cases and 6000 method records. Repeated cases do not create 6000 independent images. Overall metric means weight sampled categories equally after averaging their support/shot episodes. Accuracy describes the deliberately balanced normal/anomaly query mixture. Image AUC/AP are computed per category/seed/k, not pooled across category fits.

The information budget is k initial target normal reference images plus 4 extra disjoint target normal calibration images. This is not strict k-image few-shot. Score cutoffs use the predeclared empirical normal quantile 0.95; the fixed source-error abstention cutoff is 0.2. A small empirical normal quantile is not a guaranteed target false-alarm rate.

**Actual method means.**

| Method | Accuracy | Image AUC | Image AP | Pixel AP | AU-PRO | IoU | Miss rate | False-alarm rate | Accepted coverage | Accepted accuracy |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| fixed_avg | 0.7617 | 0.8530 | 0.8735 | 0.3477 | 0.7720 | 0.1506 | 0.2917 | 0.1850 | 1.0000 | 0.7617 |
| max | 0.7400 | 0.8625 | 0.8775 | 0.3508 | 0.7705 | 0.1148 | 0.2317 | 0.2883 | 1.0000 | 0.7400 |
| safal | 0.7667 | 0.8603 | 0.8791 | 0.3486 | 0.7756 | 0.1512 | 0.3283 | 0.1383 | 0.5250 | 0.8714 |
| search | 0.7383 | 0.8498 | 0.8672 | 0.3134 | 0.7271 | 0.1420 | 0.3433 | 0.1800 | 1.0000 | 0.7383 |
| subspace | 0.7400 | 0.8335 | 0.8592 | 0.3551 | 0.7892 | 0.1336 | 0.3117 | 0.2083 | 1.0000 | 0.7400 |

**Per-category/shot outcomes.** Values average the actual support draws. Full precision is in summary_by_category_shot.csv.

| Dataset/category | k | Method | Accuracy | Image AUC | Image AP | Pixel AP | AU-PRO |
| --- | --- | --- | --- | --- | --- | --- | --- |
| mvtec_ad/cable | 1 | fixed_avg | 0.6333 | 0.8233 | 0.8752 | 0.4545 | 0.8229 |
| mvtec_ad/cable | 1 | max | 0.6833 | 0.8200 | 0.8697 | 0.4614 | 0.8295 |
| mvtec_ad/cable | 1 | safal | 0.5833 | 0.8233 | 0.8793 | 0.4560 | 0.8243 |
| mvtec_ad/cable | 1 | search | 0.5833 | 0.7500 | 0.7936 | 0.3792 | 0.7357 |
| mvtec_ad/cable | 1 | subspace | 0.6667 | 0.8433 | 0.8881 | 0.4765 | 0.8513 |
| mvtec_ad/cable | 2 | fixed_avg | 0.6667 | 0.8300 | 0.8647 | 0.4438 | 0.8147 |
| mvtec_ad/cable | 2 | max | 0.6833 | 0.8300 | 0.8546 | 0.4497 | 0.8177 |
| mvtec_ad/cable | 2 | safal | 0.6500 | 0.8133 | 0.8573 | 0.4435 | 0.8151 |
| mvtec_ad/cable | 2 | search | 0.6500 | 0.8000 | 0.8212 | 0.3800 | 0.7522 |
| mvtec_ad/cable | 2 | subspace | 0.6667 | 0.8067 | 0.8607 | 0.4598 | 0.8302 |
| mvtec_ad/cable | 4 | fixed_avg | 0.7833 | 0.8367 | 0.8757 | 0.4675 | 0.8115 |
| mvtec_ad/cable | 4 | max | 0.7667 | 0.8467 | 0.8759 | 0.4727 | 0.8148 |
| mvtec_ad/cable | 4 | safal | 0.7667 | 0.8233 | 0.8636 | 0.4696 | 0.8122 |
| mvtec_ad/cable | 4 | search | 0.7333 | 0.8233 | 0.8461 | 0.4156 | 0.7530 |
| mvtec_ad/cable | 4 | subspace | 0.7667 | 0.8200 | 0.8732 | 0.4803 | 0.8283 |
| mvtec_ad/cable | 8 | fixed_avg | 0.7833 | 0.8433 | 0.8927 | 0.4669 | 0.8117 |
| mvtec_ad/cable | 8 | max | 0.7333 | 0.8667 | 0.8957 | 0.4700 | 0.8125 |
| mvtec_ad/cable | 8 | safal | 0.8000 | 0.8467 | 0.8921 | 0.4711 | 0.8122 |
| mvtec_ad/cable | 8 | search | 0.7667 | 0.8433 | 0.8531 | 0.4275 | 0.7571 |
| mvtec_ad/cable | 8 | subspace | 0.7500 | 0.8233 | 0.8911 | 0.4751 | 0.8225 |
| mvtec_ad/hazelnut | 1 | fixed_avg | 0.8833 | 0.9933 | 0.9939 | 0.6462 | 0.9246 |
| mvtec_ad/hazelnut | 1 | max | 0.8167 | 0.9867 | 0.9893 | 0.6231 | 0.9152 |
| mvtec_ad/hazelnut | 1 | safal | 0.9167 | 0.9800 | 0.9859 | 0.6582 | 0.9260 |
| mvtec_ad/hazelnut | 1 | search | 0.8500 | 0.9867 | 0.9893 | 0.6610 | 0.9385 |
| mvtec_ad/hazelnut | 1 | subspace | 0.8667 | 0.9900 | 0.9923 | 0.6256 | 0.8931 |
| mvtec_ad/hazelnut | 2 | fixed_avg | 0.9000 | 1.0000 | 1.0000 | 0.6439 | 0.9464 |
| mvtec_ad/hazelnut | 2 | max | 0.8500 | 0.9967 | 0.9970 | 0.6255 | 0.9364 |
| mvtec_ad/hazelnut | 2 | safal | 0.9167 | 0.9967 | 0.9970 | 0.6541 | 0.9490 |
| mvtec_ad/hazelnut | 2 | search | 0.8500 | 0.9933 | 0.9939 | 0.6453 | 0.9557 |
| mvtec_ad/hazelnut | 2 | subspace | 0.9333 | 0.9967 | 0.9970 | 0.6300 | 0.9307 |
| mvtec_ad/hazelnut | 4 | fixed_avg | 0.9000 | 1.0000 | 1.0000 | 0.6667 | 0.9311 |
| mvtec_ad/hazelnut | 4 | max | 0.8333 | 1.0000 | 1.0000 | 0.6551 | 0.9133 |
| mvtec_ad/hazelnut | 4 | safal | 0.9500 | 1.0000 | 1.0000 | 0.6760 | 0.9339 |
| mvtec_ad/hazelnut | 4 | search | 0.9000 | 1.0000 | 1.0000 | 0.6641 | 0.9434 |
| mvtec_ad/hazelnut | 4 | subspace | 0.9000 | 0.9933 | 0.9944 | 0.6578 | 0.9120 |
| mvtec_ad/hazelnut | 8 | fixed_avg | 0.9000 | 1.0000 | 1.0000 | 0.6743 | 0.9287 |
| mvtec_ad/hazelnut | 8 | max | 0.8167 | 1.0000 | 1.0000 | 0.6689 | 0.9133 |
| mvtec_ad/hazelnut | 8 | safal | 0.9333 | 1.0000 | 1.0000 | 0.6813 | 0.9323 |
| mvtec_ad/hazelnut | 8 | search | 0.9333 | 1.0000 | 1.0000 | 0.6645 | 0.9428 |
| mvtec_ad/hazelnut | 8 | subspace | 0.8500 | 1.0000 | 1.0000 | 0.6702 | 0.9115 |
| mvtec_ad/transistor | 1 | fixed_avg | 0.5333 | 0.5333 | 0.5596 | 0.3963 | 0.6074 |
| mvtec_ad/transistor | 1 | max | 0.5167 | 0.5400 | 0.5552 | 0.3961 | 0.5939 |
| mvtec_ad/transistor | 1 | safal | 0.5833 | 0.5733 | 0.5775 | 0.4000 | 0.6068 |
| mvtec_ad/transistor | 1 | search | 0.5667 | 0.6267 | 0.6438 | 0.3540 | 0.6071 |
| mvtec_ad/transistor | 1 | subspace | 0.4333 | 0.4800 | 0.4981 | 0.3995 | 0.5825 |
| mvtec_ad/transistor | 2 | fixed_avg | 0.5500 | 0.6333 | 0.6211 | 0.4295 | 0.6290 |
| mvtec_ad/transistor | 2 | max | 0.5500 | 0.6733 | 0.6558 | 0.4339 | 0.6154 |
| mvtec_ad/transistor | 2 | safal | 0.5500 | 0.6633 | 0.6505 | 0.4328 | 0.6291 |
| mvtec_ad/transistor | 2 | search | 0.5833 | 0.7100 | 0.7210 | 0.3858 | 0.6306 |
| mvtec_ad/transistor | 2 | subspace | 0.5500 | 0.5767 | 0.5570 | 0.4379 | 0.6026 |
| mvtec_ad/transistor | 4 | fixed_avg | 0.6667 | 0.7933 | 0.7785 | 0.4727 | 0.6489 |
| mvtec_ad/transistor | 4 | max | 0.6667 | 0.8200 | 0.8107 | 0.4873 | 0.6383 |
| mvtec_ad/transistor | 4 | safal | 0.6833 | 0.8300 | 0.8251 | 0.4703 | 0.6493 |
| mvtec_ad/transistor | 4 | search | 0.6833 | 0.8600 | 0.8766 | 0.4144 | 0.6520 |
| mvtec_ad/transistor | 4 | subspace | 0.5667 | 0.6933 | 0.6904 | 0.4928 | 0.6256 |
| mvtec_ad/transistor | 8 | fixed_avg | 0.7167 | 0.8333 | 0.8148 | 0.4927 | 0.6599 |
| mvtec_ad/transistor | 8 | max | 0.8000 | 0.8433 | 0.8153 | 0.5114 | 0.6514 |
| mvtec_ad/transistor | 8 | safal | 0.7167 | 0.8633 | 0.8485 | 0.4887 | 0.6604 |
| mvtec_ad/transistor | 8 | search | 0.8000 | 0.9167 | 0.9024 | 0.4383 | 0.6645 |
| mvtec_ad/transistor | 8 | subspace | 0.6500 | 0.7533 | 0.7487 | 0.5145 | 0.6384 |
| visa/macaroni2 | 1 | fixed_avg | 0.6500 | 0.7200 | 0.7750 | 0.0116 | 0.5795 |
| visa/macaroni2 | 1 | max | 0.6167 | 0.7567 | 0.7919 | 0.0114 | 0.5816 |
| visa/macaroni2 | 1 | safal | 0.6833 | 0.7300 | 0.7865 | 0.0120 | 0.5898 |
| visa/macaroni2 | 1 | search | 0.6833 | 0.7433 | 0.7908 | 0.0093 | 0.5052 |
| visa/macaroni2 | 1 | subspace | 0.6167 | 0.7100 | 0.7751 | 0.0122 | 0.6514 |
| visa/macaroni2 | 2 | fixed_avg | 0.7167 | 0.7700 | 0.8422 | 0.0170 | 0.6270 |
| visa/macaroni2 | 2 | max | 0.6333 | 0.7833 | 0.8350 | 0.0170 | 0.6317 |
| visa/macaroni2 | 2 | safal | 0.7500 | 0.8100 | 0.8623 | 0.0169 | 0.6374 |
| visa/macaroni2 | 2 | search | 0.6667 | 0.7500 | 0.8102 | 0.0111 | 0.5372 |
| visa/macaroni2 | 2 | subspace | 0.6833 | 0.7567 | 0.8296 | 0.0180 | 0.6975 |
| visa/macaroni2 | 4 | fixed_avg | 0.7833 | 0.8500 | 0.8914 | 0.0212 | 0.6416 |
| visa/macaroni2 | 4 | max | 0.7500 | 0.8567 | 0.8832 | 0.0213 | 0.6432 |
| visa/macaroni2 | 4 | safal | 0.8333 | 0.8833 | 0.9151 | 0.0211 | 0.6554 |
| visa/macaroni2 | 4 | search | 0.7333 | 0.8567 | 0.8732 | 0.0140 | 0.5437 |
| visa/macaroni2 | 4 | subspace | 0.7667 | 0.8000 | 0.8618 | 0.0229 | 0.7258 |
| visa/macaroni2 | 8 | fixed_avg | 0.8000 | 0.8333 | 0.8949 | 0.0234 | 0.6574 |
| visa/macaroni2 | 8 | max | 0.7333 | 0.8367 | 0.8856 | 0.0235 | 0.6551 |
| visa/macaroni2 | 8 | safal | 0.8333 | 0.8833 | 0.9188 | 0.0236 | 0.6743 |
| visa/macaroni2 | 8 | search | 0.7500 | 0.8500 | 0.8798 | 0.0169 | 0.5524 |
| visa/macaroni2 | 8 | subspace | 0.7667 | 0.8067 | 0.8708 | 0.0249 | 0.7484 |
| visa/pcb2 | 1 | fixed_avg | 0.8000 | 0.9100 | 0.9199 | 0.1191 | 0.8376 |
| visa/pcb2 | 1 | max | 0.8500 | 0.9300 | 0.9471 | 0.1478 | 0.8506 |
| visa/pcb2 | 1 | safal | 0.7500 | 0.8800 | 0.8930 | 0.1069 | 0.8392 |
| visa/pcb2 | 1 | search | 0.6333 | 0.7633 | 0.8035 | 0.0557 | 0.7395 |
| visa/pcb2 | 1 | subspace | 0.8500 | 0.9467 | 0.9616 | 0.1529 | 0.8732 |
| visa/pcb2 | 2 | fixed_avg | 0.8167 | 0.9267 | 0.9320 | 0.1532 | 0.8554 |
| visa/pcb2 | 2 | max | 0.8167 | 0.9400 | 0.9519 | 0.1736 | 0.8665 |
| visa/pcb2 | 2 | safal | 0.7667 | 0.9033 | 0.9169 | 0.1450 | 0.8570 |
| visa/pcb2 | 2 | search | 0.7667 | 0.8733 | 0.8835 | 0.0947 | 0.7581 |
| visa/pcb2 | 2 | subspace | 0.8000 | 0.9400 | 0.9514 | 0.1765 | 0.8889 |
| visa/pcb2 | 4 | fixed_avg | 0.8667 | 0.9633 | 0.9685 | 0.1693 | 0.8454 |
| visa/pcb2 | 4 | max | 0.8167 | 0.9533 | 0.9628 | 0.1819 | 0.8547 |
| visa/pcb2 | 4 | safal | 0.8167 | 0.9433 | 0.9507 | 0.1633 | 0.8466 |
| visa/pcb2 | 4 | search | 0.8000 | 0.9167 | 0.9252 | 0.1083 | 0.7776 |
| visa/pcb2 | 4 | subspace | 0.8333 | 0.9667 | 0.9716 | 0.1850 | 0.8751 |
| visa/pcb2 | 8 | fixed_avg | 0.8833 | 0.9667 | 0.9704 | 0.1838 | 0.8586 |
| visa/pcb2 | 8 | max | 0.8667 | 0.9700 | 0.9737 | 0.1850 | 0.8757 |
| visa/pcb2 | 8 | safal | 0.8500 | 0.9600 | 0.9625 | 0.1818 | 0.8626 |
| visa/pcb2 | 8 | search | 0.8333 | 0.9333 | 0.9369 | 0.1293 | 0.7965 |
| visa/pcb2 | 8 | subspace | 0.8833 | 0.9667 | 0.9716 | 0.1889 | 0.8951 |

**Missed defects and selective decisions.** Raw accuracy includes every inspection, including unresolved actions. Accepted accuracy is conditional on retained actions and must accompany coverage; rejected defects remain explicitly unresolved, not successes. Counts below are repeated query/support/k records.

| Method | Raw missed defects | Raw false alarms | Accepted misses | Accepted false alarms | Unresolved defects | Unresolved normals |
| --- | --- | --- | --- | --- | --- | --- |
| fixed_avg | 175 | 111 | 175 | 111 | 0 | 0 |
| max | 139 | 173 | 139 | 173 | 0 | 0 |
| safal | 197 | 83 | 68 | 13 | 271 | 299 |
| search | 206 | 108 | 206 | 108 | 0 | 0 |
| subspace | 187 | 125 | 187 | 125 | 0 | 0 |

Compared with fixed_avg, SAFAL has 22 additional raw missed-defect records and 28 fewer raw false-alarm records. Missed-defect rates are 0.3283 versus 0.2917; false-alarm rates are 0.1383 versus 0.1850. Direct pairing identifies 24 detected-to-missed records touching 14 unique anomaly images, and 2 missed-to-detected records touching 2 unique anomaly images. Normal false alarms were removed in 29 records and added in 1. These are repeated support/shot inspection events. Fewer false alarms must not be described as better defect preservation.

**Source error-head learning.** Both events mean prediction correctness at the locked classifier cutoff: 0=correct, 1=incorrect; they do not mean normal versus anomalous.

| Source role | Rows | Original parents | Correct events | Error events | Parents with errors |
| --- | --- | --- | --- | --- | --- |
| meta_training | 320 | 160 | 277 | 43 | 43 |
| source_calibration | 80 | 40 | 72 | 8 | 8 |

Fitting and held-out original-parent overlap is zero. Normal/CutPaste siblings stay in the same split. Logistic C=1, class_weight=None and feature normalization fitted only on source fitting rows are preserved. Sparse independent error parents limit probability evidence. Detailed category/kind counts are in source_error_counts.csv.

| Source split | Brier | ECE | NLL |
| --- | --- | --- | --- |
| meta_training | 0.098448 | 0.039859 | 0.312971 |
| source_calibration | 0.080791 | 0.035626 | 0.269773 |

These source metrics were recomputed from the saved plain-JSON head. The held-out metrics match the stored training report; native probabilities also pass JSON-head replay. This source audit is not native industrial calibration evidence.

**Native error-probability audit by shot.** The same source head was fitted at k=2. Native-domain transfer and transfer to other shot counts are unverified. These metrics evaluate actual wrong/correct image events after inference; sigmoid values are not asserted calibrated.

| k | Method | Repeated events | Observed error rate | Brier | ECE | NLL | AURC |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | safal | 300 | 0.296667 | 0.204568 | 0.087519 | 0.593250 | 0.187321 |
| 2 | safal | 300 | 0.273333 | 0.184089 | 0.080638 | 0.537938 | 0.135831 |
| 4 | safal | 300 | 0.190000 | 0.135667 | 0.030438 | 0.419652 | 0.074986 |
| 8 | safal | 300 | 0.173333 | 0.128711 | 0.034813 | 0.402777 | 0.072477 |

Brier/NLL/ECE aggregate actual probabilities and error events. Risk is locked-cutoff 0/1 classification error; whole tied-confidence groups are accepted together and AURC uses right-step integration. Curves are descriptive, correlated observations, not independent risk guarantees. Other methods use negative U as a diagnostic confidence rank, not a fabricated probability.

**Paired uncertainty.** paired_accuracy_intervals.json stores each-k and overall SAFAL-minus-comparator intervals. Overall differences first average dependent nested-k results within each query/seed. Crossed resampling then independently weights query IDs and shared support-draw seeds within category. Sampled categories, the fitted head, training sample and cutoffs remain fixed. With only 3 draw units, these are limited-replication conditional percentile intervals; they do not capture head-training uncertainty, unsampled categories or a pristine final-test population. No AUROC interval is manufactured from repeated episode values and no pixels are resampled.

**Metric geometry and audit.** 256x256 bilinear score maps; nearest-neighbor native binary masks. Localized score maps and masks use the recorded metric grid; these localization values are not new original-resolution benchmark results. AU-PRO follows saved connected-region/FPR settings, with its sampled threshold integration limit in episode_metrics.csv. Reporting recomputed image decision counts, AUC/AP/F1 and risk curves from serialized predictions, checked them against recorded episode detection metrics, and retained recorded localization values without pretending to rerun all pixel maps. reporting_audit.json records 2700 matching detection checks. Model and runtime files were read only.

The runtime summary used 1000 bootstrap resamples and stored interval [-0.016666666666666663, 0.02833333333333334]; this derived report uses 2000 resamples and interval [-0.016666666666666666, 0.03]. Finite Monte Carlo resampling changes the interval endpoints; neither fit nor decision parameters were changed.

The independent completed-artifact audit passed: 70 serialized models, 60 cached query replays, 61 ledgers, 1848 unique output files and 906 unique input files hash-verified. It does not establish native-resolution localization or source-proxy probability transfer. See artifact_audit.json.

**Prior exposure.** The separate named-run audit found 18 current query IDs previously measured and 82 not identified in those five runs. This is not proof of an untouched history. It found 5 prior source-query parents, including 1 current held-out parent; current fit/held-out identity separation remains zero. This is broader development validation, not a pristine unseen final benchmark. See prior_exposure_audit.json.

The supplied unit/contract test log records 159 passing tests at /tmp/safal_training_20261014_verification/unit_tests.log. These tests are separate from the actual training/validation run and the reporting recomputation audit.

Published full recipes, dataset-wide benchmarks, private-server evaluation, LLM fine-tuning, production reliability, calibration guarantees and novelty/state-of-the-art claims are not established. The sampled validation outcomes and comparison intervals above determine the actual gain statements; source or target labels were not used to revise parameters after evaluation.
