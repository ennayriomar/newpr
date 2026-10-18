"""Full-field geometry and source-only calibration for the controlled experiment."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image
from sklearn.metrics import roc_auc_score

from audit_outputs import pro_from_weights, pro_statistics, stratified_weights, weighted_auroc
from utils import file_sha256, use_local_framework, write_json

use_local_framework()
from safe_iad.research_metrics import localization_metrics
from safe_iad.vision_hybrid_features import image_score
from safe_iad.vision_hybrid_model import HybridParameters, fuse_raw

LAMBDAS = (0., .1, .25, .5)
METRICS = ("image_auroc", "pixel_auroc", "au_pro", "image_fpr", "recall", "balanced_accuracy", "pixel_iou", "pixel_f1")
LABELS = {"baseline": "internal baseline", "hybrid": "adapted implementation", "lambda_zero": "adapted implementation"}


def canonical_hash(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def save_sealed(path, value):
    path = Path(path)
    if path.exists():
        raise ValueError(f"Refuse to overwrite sealed file: {path}")
    write_json(path, value)
    path.with_name(path.name+".sha256").write_text(file_sha256(path)+"  "+path.name+"\n")


def validate_roles(roles):
    """Global ID and resolved-path check, before loading any scoring images."""
    groups, paths = {}, {}
    for role, rows in roles.items():
        groups[role] = {r["image_id"] for r in rows}
        paths[role] = {str(Path(r["path"]).resolve(strict=True)) for r in rows}
    names = list(groups)
    for i, left in enumerate(names):
        for right in names[i+1:]:
            if groups[left] & groups[right] or paths[left] & paths[right]:
                raise ValueError(f"ID/path leakage between {left} and {right}")
    calibration = roles["calibration"]
    if not calibration or len(groups["calibration"]) != len(calibration):
        raise ValueError("Unique nonempty calibration image IDs required")
    if any(r["dataset"] != "mvtec_ad2" or r["split"] != "train" or r["label"] != "normal"
           for r in calibration):
        raise ValueError("Only SOURCE AD2 native train normals may calibrate")
    return {"passed": True, "role_unique_counts": {k: len(v) for k, v in groups.items()},
            "id_overlaps": 0, "resolved_path_overlaps": 0,
            "repeated_query_ids_across_support_draws": "Permitted; same evaluation role only"}


def full_truth(image_path, mask_path=None, size=448):
    with Image.open(image_path) as image:
        native_size = image.size
    if mask_path:
        with Image.open(mask_path) as mask:
            if mask.size != native_size:
                raise ValueError("Native GT and image shapes differ")
            truth = np.asarray(mask.convert("L").resize((size, size), Image.Resampling.NEAREST)) > 0
    else:
        truth = np.zeros((size, size), bool)
    return truth


def full_prediction(raw, strength, grid, size=448):
    import torch
    from torch.nn import functional as F

    params = HybridParameters() if strength == 0 else HybridParameters(1, .95, strength, "uniform")
    result = fuse_raw(raw, params, grid)
    # Interpolate directly from the patch grid, avoiding the old intermediate
    # 256x256 center-ROI map. The complete field is scored, including borders.
    score_map = F.interpolate(result["raw_sum"].float().reshape(1, 1, grid, grid),
                             (size, size), mode="bilinear", align_corners=False)[0, 0].numpy()
    if score_map.shape != (size, size) or not np.isfinite(score_map).all():
        raise ValueError("Invalid full-field map")
    return score_map, image_score(score_map)


def normal_cutoff(values, alpha):
    """Upper empirical quantile, strict > decisions handle ties conservatively.

    This controls the realised calibration fraction only. It offers no target
    domain-shift guarantee, nor an independent-pixel confidence claim.
    """
    values = np.asarray(values).ravel()
    if not len(values) or not np.isfinite(values).all() or not 0 < alpha < 1:
        raise ValueError("Finite normal scores and 0<alpha<1 required")
    rank = int(np.ceil((1-alpha)*len(values)))-1
    threshold = float(np.partition(values, rank)[rank])
    return {"cutoff": threshold, "decision": "score > cutoff", "target_fpr": alpha,
            "realised_calibration_fpr": float((values > threshold).mean()), "observations": len(values),
            "target_fpr_guaranteed": False, "source_normal_only": True}


def measured_metrics(truths, maps, labels, scores, cutoffs):
    labels, scores = np.asarray(labels), np.asarray(scores)
    decision = scores > cutoffs["image"]["cutoff"]
    normal, anomaly = labels == 0, labels == 1
    fpr = float(decision[normal].mean())
    recall = float(decision[anomaly].mean())
    # Ranking functions use raw maps. Count metrics explicitly use strict >;
    # no dtype-dependent rounding of an artificial nextafter threshold.
    localization = localization_metrics(truths, maps, cutoffs["pixel"]["cutoff"], max_thresholds=128)
    tp = fp = fn = tn = 0
    for truth, score_map in zip(truths, maps):
        if truth.shape != score_map.shape:
            raise ValueError("Saved map/GT shape mismatch")
        truth, predicted = truth.astype(bool), score_map > cutoffs["pixel"]["cutoff"]
        tp += int((truth & predicted).sum());fp += int((~truth & predicted).sum())
        fn += int((truth & ~predicted).sum());tn += int((~truth & ~predicted).sum())
    return {"image_auroc": float(roc_auc_score(labels, scores)),
            "pixel_auroc": localization["pixel_auroc"], "au_pro": localization["au_pro"],
            "image_fpr": fpr, "recall": recall, "balanced_accuracy": (recall+1-fpr)/2,
            "pixel_iou": tp/(tp+fp+fn) if tp+fp+fn else None,
            "pixel_f1": 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,
            "image_fp": int(decision[normal].sum()), "image_fn": int((~decision[anomaly]).sum()),
            "normal_images": int(normal.sum()), "anomalous_images": int(anomaly.sum()),
            "pixel_counts": dict(tp=tp, fp=fp, fn=fn, tn=tn),
            "metric_region": "Whole input field, GT and score map both448x448; no center crop",
            "native_resolution_metrics": False, "au_pro_max_thresholds": 128,
            "cutoff_decision": "strict >", "cutoffs": cutoffs}


def paired_bootstrap(truths, maps_by_method, rows, cutoffs, replicates, seed):
    labels = np.array([r["label"] for r in rows])
    weights = stratified_weights(labels, replicates, seed)
    result = {"image_multiplicities": weights}
    for method in ("baseline", "hybrid"):
        scores = np.array([r["scores"][method] for r in rows])
        result[method+"_image_auroc"] = weighted_auroc(labels, scores, weights)
        stats = pro_statistics(truths, maps_by_method[method])
        result[method+"_au_pro"] = pro_from_weights(stats, weights)
        pred = scores > cutoffs[method]["image"]["cutoff"]
        neg, pos = labels == 0, labels == 1
        fpr = (weights[:, neg] @ pred[neg]) / weights[:, neg].sum(axis=1)
        recall = (weights[:, pos] @ pred[pos]) / weights[:, pos].sum(axis=1)
        result[method+"_image_fpr"], result[method+"_recall"] = fpr, recall
        result[method+"_balanced_accuracy"] = (recall+1-fpr)/2
        counts = []
        for truth, score_map in zip(truths, maps_by_method[method]):
            prediction, truth = score_map > cutoffs[method]["pixel"]["cutoff"], truth.astype(bool)
            counts.append([int((truth & prediction).sum()), int((~truth & prediction).sum()), int((truth & ~prediction).sum())])
        tp, fp, fn = (weights @ np.asarray(counts)).T
        result[method+"_pixel_iou"] = tp / (tp+fp+fn)
        result[method+"_pixel_f1"] = 2*tp / (2*tp+fp+fn)
        # Image-resampled pixel ROC on a fixed dense grid. Exact pixel AUROC
        # remains the reported point metric; this approximation is explicitly
        # labeled in the protocol and saved with its grid point for checking.
        distinct = np.unique(np.concatenate([m.ravel() for m in maps_by_method[method]]))
        ranks = np.unique(np.linspace(0, len(distinct)-1, min(4096, len(distinct))).astype(int))
        thresholds = np.r_[np.inf, distinct[ranks][::-1], -np.inf]
        positives, negatives, counts_pos, counts_neg = [], [], [], []
        for truth, score_map in zip(truths, maps_by_method[method]):
            positive, negative = np.sort(score_map[truth.astype(bool)]), np.sort(score_map[~truth.astype(bool)])
            positives.append(len(positive)-np.searchsorted(positive, thresholds, side="left"))
            negatives.append(len(negative)-np.searchsorted(negative, thresholds, side="left"))
            counts_pos.append(len(positive));counts_neg.append(len(negative))
        tp_grid, fp_grid = np.asarray(positives), np.asarray(negatives)
        tpr = (weights @ tp_grid) / (weights @ counts_pos)[:, None]
        fpr_grid = (weights @ fp_grid) / (weights @ counts_neg)[:, None]
        result[method+"_pixel_auroc"] = np.trapezoid(tpr, fpr_grid, axis=1)
        result[method+"_pixel_auroc_grid_point"] = np.trapezoid(tp_grid.sum(axis=0)/sum(counts_pos), fp_grid.sum(axis=0)/sum(counts_neg))
        result[method+"_pixel_roc_thresholds"] = thresholds
        for key, value in stats.items():
            result[method+"_pro_"+key] = value
    for metric in METRICS:
        result["paired_"+metric] = result["hybrid_"+metric]-result["baseline_"+metric]
    return result


def cluster_bootstrap(category_draw_values, replicates, seed):
    """Categories, after averaging draws; a draw is not a new category."""
    means = np.array([np.mean(values) for _, values in sorted(category_draw_values.items())])
    rng = np.random.default_rng(seed)
    indices = rng.integers(0, len(means), size=(replicates, len(means)))
    return means[indices].mean(axis=1), indices


def select_figures(rows, threshold):
    groups = {
        "true_negative": ([r for r in rows if not r["label"] and r["scores"]["hybrid"] <= threshold], lambda r: r["scores"]["hybrid"]),
        "false_positive": ([r for r in rows if not r["label"] and r["scores"]["hybrid"] > threshold], lambda r: -r["scores"]["hybrid"]),
        "miss": ([r for r in rows if r["label"] and r["scores"]["hybrid"] <= threshold], lambda r: r["scores"]["hybrid"]),
        "smallest_defect": ([r for r in rows if r["label"] and r["truth_pixels"]], lambda r: r["truth_pixels"]),
        "localization_failure": ([r for r in rows if r["label"] and r["truth_pixels"]], lambda r: r["hybrid_pixel_iou"]),
    }
    return {reason: min(group, key=lambda r: (key(r), r["image_id"]))["image_id"] if group else None
            for reason, (group, key) in groups.items()}
