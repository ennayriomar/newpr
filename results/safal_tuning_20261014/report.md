# Development-selected SAFAL verification

The locked comparison contains 100 unique images, 300 paired query/support cases and 900 method records. There are 50 unique anomalous images and 150 anomalous cases. Repeated support cases are correlated.

The development grid recorded 768 candidates, 576 eligible hybrids and 294 eligible candidates with zero declared detected-to-missed losses against both controls. Native development labels selected the parameters and image threshold. This report evaluates the saved lock and does not select a winner.

The highest preservation-feasible hybrid development accuracy is 81.33%; the highest accuracy among all grid cells, including controls and unsafe candidates, is 81.67%. Both are post-selection development measurements.

Locked recipe:

```json
{
  "feature": {
    "cache_root": "/tmp/safal_training_20261014_feature_cache",
    "id": "mixed224",
    "layers": [
      2,
      5,
      8,
      11
    ],
    "resolution": 224
  },
  "params": {
    "aggregation": "top1",
    "explained_variance": 0.99,
    "fusion": "fixed",
    "image_threshold": 1.0,
    "normal_quantile": 0.9,
    "search_weight": 0.75
  }
}
```

| Method | Accuracy | Missed-defect rate | False-alarm rate | Image AUROC | Image AP | Threshold |
|---|---:|---:|---:|---:|---:|---:|
| original | 76.33% | 24.67% | 22.67% | 0.8587 | 0.8617 | 1.0000 |
| fixed_avg | 77.67% | 20.00% | 24.67% | 0.8647 | 0.8683 | 1.0000 |
| selected | 77.33% | 20.00% | 25.33% | 0.8613 | 0.8614 | 1.0000 |

Accuracy in the table is an equal category/seed episode mean; error rates use recorded class counts. Image AUROC/AP are computed within category/seed, then averaged. Differently normalized scores are never pooled for ranking. Raw count-based accuracy is retained separately in summary.json.

| Selected versus | Accuracy difference (95% conditional interval) | Detected→missed cases / unique images | Missed→detected cases / unique images | False alarms removed / added |
|---|---:|---:|---:|---:|
| original | 1.00% [-2.33%, 4.33%] | 0 / 0 | 7 / 7 | 0 / 4 |
| fixed_avg | -0.33% [-3.33%, 3.00%] | 3 / 3 | 3 / 3 | 1 / 2 |

The conditional paired accuracy interval versus fixed averaging includes zero, so these observations do not establish an accuracy improvement.
Detection losses must be read alongside false-alarm reductions; a higher overall accuracy alone does not establish better defect preservation. Unique lost/recovered image sets can overlap across support draws.

Intervals use 2000 paired crossed query/support percentile resamples with fixed categories. Support multiplicities are sampled independently within each category. Three or fewer draws provide limited replication; no candidate-row, pixel or independent-record interval is used.

## Category breakdown

| Dataset/category | Method | Accuracy | Missed-defect rate | False-alarm rate | Image AUROC | Image AP |
|---|---|---:|---:|---:|---:|---:|
| mvtec_ad/cable | original | 83.33% | 20.00% | 13.33% | 0.9500 | 0.9434 |
| mvtec_ad/cable | fixed_avg | 83.33% | 20.00% | 13.33% | 0.9467 | 0.9409 |
| mvtec_ad/cable | selected | 86.67% | 13.33% | 13.33% | 0.9500 | 0.9434 |
| mvtec_ad/hazelnut | original | 91.67% | 3.33% | 13.33% | 0.9933 | 0.9936 |
| mvtec_ad/hazelnut | fixed_avg | 93.33% | 0.00% | 13.33% | 0.9967 | 0.9970 |
| mvtec_ad/hazelnut | selected | 91.67% | 0.00% | 16.67% | 0.9933 | 0.9936 |
| mvtec_ad/transistor | original | 80.00% | 23.33% | 16.67% | 0.9300 | 0.8993 |
| mvtec_ad/transistor | fixed_avg | 78.33% | 20.00% | 23.33% | 0.9200 | 0.8875 |
| mvtec_ad/transistor | selected | 78.33% | 20.00% | 23.33% | 0.9267 | 0.8957 |
| visa/macaroni2 | original | 63.33% | 36.67% | 36.67% | 0.6900 | 0.7111 |
| visa/macaroni2 | fixed_avg | 68.33% | 26.67% | 36.67% | 0.7167 | 0.7280 |
| visa/macaroni2 | selected | 63.33% | 33.33% | 40.00% | 0.6900 | 0.7036 |
| visa/pcb2 | original | 63.33% | 40.00% | 33.33% | 0.7300 | 0.7612 |
| visa/pcb2 | fixed_avg | 65.00% | 33.33% | 36.67% | 0.7433 | 0.7882 |
| visa/pcb2 | selected | 66.67% | 33.33% | 33.33% | 0.7467 | 0.7707 |

## Saved localization metrics

These are supplied per-episode values, not a fresh score-map/mask recomputation. Missing values remain missing.

| Method | Pixel AP | AU-PRO | IoU | Pixel F1 |
|---|---:|---:|---:|---:|
| original | 0.4086 | 0.8679 | 0.1651 | 0.2595 |
| fixed_avg | 0.4118 | 0.8668 | 0.1642 | 0.2584 |
| selected | 0.3999 | 0.8476 | 0.1114 | 0.1860 |

## Scope and audit limits

- Finite development search used native labels to select parameters and image threshold; development accuracy is post-selection.
- Verification checks new image IDs within previously development-exposed categories, not an unseen-category or pristine global benchmark.
- Accuracy reflects the observed normal/anomaly mixture; balanced sampling is not industrial defect prevalence.
- Queries recur across support draws. Method records, draws, pixels and candidates are not independent query samples.
- Intervals resample paired query IDs and support draws independently within fixed categories; few support draws limit reliability.
- Only additive paired correctness differences receive intervals. AUROC/AP are descriptive within-category/seed means.
- Zero development detection losses do not guarantee preservation on verification images or future defects.
- The prior error-probability head is omitted after changing the detector. No probability calibration or abstention claim is made.
- This reporting pass neither verifies lock chronology nor retrains or changes parameters; separate provenance must establish the lock.
- No GPU speed, full-benchmark superiority, SOTA or production guarantee is established.

The exact lock, candidate counts, class counts, transition image IDs, input hashes and report audit flags are recorded in summary.json.
