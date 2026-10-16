"""Audit saved baseline/hybrid maps, conditional intervals and rule-based figures.

This is offline reporting. It never fits a model, calibrates a threshold or
fills unscored borders. Record --prepare-protocol BEFORE running test.py.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil

import numpy as np
from PIL import Image
from scipy.ndimage import label as components

from outputs import image_roi, normalized_display
from utils import file_sha256, read_json, write_json

METHODS = ("baseline", "hybrid")
FIGURE_RULE = {
    "true_negative": "lowest hybrid score among native normals below locked cutoff",
    "false_positive": "highest hybrid score among native normals at/above locked cutoff",
    "smallest_defect": "smallest positive cropped mask pixel count among native anomalies",
    "miss": "lowest hybrid score among native anomalies below locked cutoff",
    "localization_failure": "lowest hybrid pixel IoU at locked pixel cutoff among native anomalies with nonempty cropped mask",
    "tie_break": "lexicographic sample ID; deduplicate rows but preserve all selection reasons; absent event explicitly reported",
}


def make_protocol(run_dir, data_path=None):
    from dataset import IndustrialDataset

    run_dir = Path(run_dir)
    training, model = read_json(run_dir / "training.json"), read_json(run_dir / "model.json")
    data = IndustrialDataset(data_path or training["data_path"], training["dataset"],
                             training["category"], phase="test")
    samples = data.queries()
    return {
        "schema_version": 1,
        "recorded_before_full_category_inference_utc": datetime.now(timezone.utc).isoformat(),
        "purpose": "Descriptive audit; no tuning or untouched-test claim",
        "model_json_sha256": file_sha256(run_dir / "model.json"),
        "model_npz_sha256": model["npz_sha256"], "parameters": model["params"],
        "image_threshold": model["threshold"], "pixel_threshold": model["pixel_threshold"],
        "support_ids": model["support_ids"], "queries": len(samples),
        "normal": sum(s.label == "normal" for s in samples),
        "anomalous": sum(s.label != "normal" for s in samples),
        "ordered_sample_ids": [s.image for s in samples], "figure_rule": FIGURE_RULE,
        "display_rule": "One shared range across both methods and all cases; delta uses a separate labeled range",
        "intervals": {
            "replicates": 2000, "seed": 20261016, "confidence": .95,
            "resampling_unit": "query image, stratified by native label, paired methods",
            "scope": "Conditional on fitted bank/support; excludes training, support and category uncertainty",
            "image_auroc": "exact rank statistic per replicate",
            "au_pro": "Fixed full-cohort 128 distinct-score rank grid plus +/-inf; pooled normal-pixel FPR, equal 8-connected region weight, FPR limit .3; image bootstrap reweights sufficient statistics on this fixed grid",
        },
        "metric_scope": "Native image labels, crop-derived image scores; pixel metrics only on center ROI; outer borders unscored",
        "no_retuning": True,
    }


def pro_statistics(truths, maps, max_thresholds=128):
    """Per-image sufficient statistics at the ORIGINAL cohort's score grid."""
    if len(truths) != len(maps) or not maps:
        raise ValueError("Nonempty matching truth/map lists required")
    for truth, score in zip(truths, maps):
        if (truth.ndim != 2 or truth.shape != score.shape or
                not np.isin(truth, [0, 1]).all() or not np.isfinite(score).all()):
            raise ValueError("Finite matching 2D maps and binary masks required")
    distinct = np.unique(np.concatenate([s.ravel() for s in maps]))
    ranks = np.unique(np.linspace(0, len(distinct)-1, min(max_thresholds, len(distinct))).astype(int))
    thresholds = np.r_[np.inf, distinct[ranks][::-1], -np.inf]
    fp, region_sum, normal_count, region_count = [], [], [], []
    for truth, score in zip(truths, maps):
        truth = truth.astype(bool)
        normal = np.sort(score[~truth])
        fp.append(len(normal) - np.searchsorted(normal, thresholds, side="left"))
        normal_count.append(len(normal))
        regions, count = components(truth, structure=np.ones((3, 3), int))
        region_count.append(count)
        total = np.zeros(len(thresholds))
        for region in range(1, count + 1):
            values = np.sort(score[regions == region])
            total += (len(values) - np.searchsorted(values, thresholds, side="left")) / len(values)
        region_sum.append(total)
    return dict(fp=np.array(fp), region_sum=np.array(region_sum),
                normal_count=np.array(normal_count), region_count=np.array(region_count),
                thresholds=thresholds)


def pro_from_weights(stats, weights, limit=.3):
    """Integrate with repeated-FPR vertical segments preserved, like the engine."""
    if not 0 < limit <= 1:
        raise ValueError("FPR limit must lie in (0,1]")
    weights = np.atleast_2d(np.asarray(weights, float))
    if weights.shape[1] != len(stats["normal_count"]) or np.any(weights < 0):
        raise ValueError("Nonnegative image multiplicities required")
    normals, regions = weights @ stats["normal_count"], weights @ stats["region_count"]
    if np.any(normals <= 0) or np.any(regions <= 0):
        raise ValueError("Each replicate needs a normal pixel and a defect component")
    fprs = (weights @ stats["fp"]) / normals[:, None]
    pros = (weights @ stats["region_sum"]) / regions[:, None]
    result = []
    for fpr, pro in zip(fprs, pros):
        stop = int(np.searchsorted(fpr, limit, side="right"))
        x, y = fpr[:stop], pro[:stop]
        if x[-1] < limit:
            boundary = y[-1] + (pro[stop]-y[-1]) * (limit-x[-1]) / (fpr[stop]-x[-1])
            x, y = np.r_[x, limit], np.r_[y, boundary]
        result.append(float(np.trapezoid(y, x) / limit))
    return np.array(result)


def stratified_weights(labels, replicates, seed):
    labels = np.asarray(labels)
    if not np.isin(labels, [0, 1]).all() or set(labels.tolist()) != {0, 1}:
        raise ValueError("Both native classes required")
    rng = np.random.default_rng(seed)
    weights = np.zeros((replicates, len(labels)), dtype=np.int64)
    for group in (np.flatnonzero(labels == 0), np.flatnonzero(labels == 1)):
        draws = rng.choice(group, size=(replicates, len(group)), replace=True)
        for i, draw in enumerate(draws):
            weights[i] += np.bincount(draw, minlength=len(labels))
    return weights


def weighted_auroc(labels, scores, weights):
    labels, scores = np.asarray(labels), np.asarray(scores)
    neg, pos = labels == 0, labels == 1
    kernel = ((scores[pos, None] > scores[None, neg]).astype(float) +
              .5 * (scores[pos, None] == scores[None, neg]))
    weights = np.atleast_2d(weights)
    return np.einsum("bi,ij,bj->b", weights[:, pos], kernel, weights[:, neg]) / (
        weights[:, pos].sum(axis=1) * weights[:, neg].sum(axis=1))


def select_cases(rows, threshold):
    """Apply the recorded rules, stable ties; never substitute a nonexistent miss."""
    normal = [r for r in rows if not r["label"]]
    defect = [r for r in rows if r["label"] and r["truth_pixels"] > 0]
    groups = {
        "true_negative": ([r for r in normal if r["hybrid_score"] < threshold], "hybrid_score", 1),
        "false_positive": ([r for r in normal if r["hybrid_score"] >= threshold], "hybrid_score", -1),
        "smallest_defect": (defect, "truth_pixels", 1),
        "miss": ([r for r in rows if r["label"] and r["hybrid_score"] < threshold], "hybrid_score", 1),
        "localization_failure": (defect, "hybrid_pixel_iou", 1),
    }
    return {reason: (min(group, key=lambda r: (direction*r[key], r["sample_id"]))["sample_id"]
                     if group else None) for reason, (group, key, direction) in groups.items()}


def render_audit(rows, maps, truths, data_root, destination, bounds, delta_bounds, image_threshold,
                 *, resize=448, crop=392):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.colors import Normalize

    fig, axes = plt.subplots(len(rows), 5, figsize=(16, 3.4*len(rows)), squeeze=False)
    for i, row in enumerate(rows):
        baseline, hybrid = maps[row["index"]]
        image = image_roi(data_root / row["sample_id"], resize, crop)
        axes[i, 0].imshow(image)
        axes[i, 1].imshow(truths[row["index"]], cmap="gray", vmin=0, vmax=1)
        for j, score in ((2, baseline), (3, hybrid)):
            axes[i, j].imshow(image)
            axes[i, j].imshow(score, cmap="jet", alpha=.5, vmin=bounds[0], vmax=bounds[1])
        delta = axes[i, 4].imshow(hybrid-baseline, cmap="magma", vmin=delta_bounds[0], vmax=delta_bounds[1])
        for j, title in enumerate(("Scored center ROI", "Ground truth", "Search baseline", "Hybrid", "Hybrid - baseline")):
            axes[i, j].set_title(title, fontsize=10)
            axes[i, j].set_xticks([]);axes[i, j].set_yticks([])
        status = "defective" if row["hybrid_score"] >= image_threshold else "normal"
        axes[i, 0].set_ylabel(" / ".join(row["selection_reasons"]), fontsize=9)
        axes[i, 0].set_xlabel(row["sample_id"], fontsize=8)
        axes[i, 2].set_xlabel(f"image score {row['baseline_score']:.4f}")
        axes[i, 3].set_xlabel(f"score {row['hybrid_score']:.4f} / cutoff {image_threshold:.4f}: {status}")
        iou = "NA" if row["hybrid_pixel_iou"] is None else f"{row['hybrid_pixel_iou']:.3f}"
        axes[i, 1].set_xlabel(f"hybrid ROI IoU={iou}; FP pixels={row['hybrid_false_positive_pixels']}", fontsize=8)
    fig.subplots_adjust(left=.08, right=.98, top=.94, bottom=.12, hspace=.4, wspace=.1)
    bar = fig.add_axes([.20, .045, .29, .012])
    fig.colorbar(plt.cm.ScalarMappable(norm=Normalize(*bounds), cmap="jet"), cax=bar,
                 orientation="horizontal").set_label("Shared raw score (both methods, all rows)")
    bar = fig.add_axes([.63, .045, .25, .012])
    fig.colorbar(delta, cax=bar, orientation="horizontal").set_label("Raw additive difference")
    fig.suptitle("Fixed bank and cutoffs; rule-selected cases; outer image borders unscored", fontsize=13)
    fig.savefig(destination, dpi=120)
    plt.close(fig)


def audit(evaluation, run_dir, protocol_path, destination, data_path=None):
    from dataset import IndustrialDataset
    from safe_iad.vision_hybrid_features import image_score

    evaluation, run_dir, destination = map(Path, (evaluation, run_dir, destination))
    if destination.exists():
        raise ValueError("Use a fresh audit output directory")
    protocol = read_json(protocol_path)
    summary, model = read_json(evaluation / "metrics.json"), read_json(run_dir / "model.json")
    training = read_json(run_dir / "training.json")
    if (protocol["model_json_sha256"] != file_sha256(run_dir / "model.json") or
            summary["model_json_sha256"] != protocol["model_json_sha256"] or
            model["threshold"] != protocol["image_threshold"] or
            model["pixel_threshold"] != protocol["pixel_threshold"] or
            model["params"] != protocol["parameters"] or
            file_sha256(run_dir / "model.npz") != protocol["model_npz_sha256"] or
            not protocol["no_retuning"]):
        raise ValueError("Protocol/model/cutoff mismatch")
    if protocol["figure_rule"] != FIGURE_RULE:
        raise ValueError("Unsupported figure selection rule")
    data = IndustrialDataset(data_path or training["data_path"], training["dataset"], training["category"], "test")
    resize, crop = (model["provenance"]["encoder"][k] for k in ("resize", "crop"))
    samples = data.queries()
    cases = {}
    for line in (evaluation / "predictions.jsonl").read_text().splitlines():
        row = json.loads(line)
        case = cases.setdefault(row["sample_id"], {})
        if row["method"] in case:
            raise ValueError("Duplicate prediction")
        case[row["method"]] = row
    ids = list(cases)
    if (ids != protocol["ordered_sample_ids"] or ids != [s.image for s in samples] or
            summary["subset"] or len(ids) != summary["queries"] or len(ids) != protocol["queries"]):
        raise ValueError("Expected the complete native test category in recorded order")
    maps, truths, rows = [], [], []
    bounds, delta_bounds = [np.inf, -np.inf], [0., 0.]
    for i, (identifier, sample) in enumerate(zip(ids, samples)):
        case = cases[identifier]
        if set(case) != set(METHODS):
            raise ValueError("Missing paired method")
        for method in METHODS:
            p = case[method]
            if (p["threshold"] != model["threshold"] or p["label"] != int(sample.label != "normal") or
                    p["decision"] != (p["score"] >= model["threshold"])):
                raise ValueError("Prediction label/decision/cutoff mismatch")
        with np.load(evaluation / f"map-{i:05d}.npz", allow_pickle=False) as arrays:
            baseline, hybrid, truth = (arrays[k].copy() for k in (*METHODS, "truth"))
        if (baseline.shape != (256, 256) or hybrid.shape != baseline.shape or
                not np.isfinite(baseline).all() or not np.isfinite(hybrid).all()):
            raise ValueError("Invalid saved score-map geometry or values")
        for method, score_map in zip(METHODS, (baseline, hybrid)):
            if not np.isclose(image_score(score_map), case[method]["score"], atol=1e-7, rtol=1e-6):
                raise ValueError("Saved image score does not match the raw map's top-1% score")
        if not np.array_equal(truth, data.mask(sample, resize=resize, crop=crop)):
            raise ValueError("Saved ROI mask differs from native mask")
        for native_id in (sample.image, sample.mask):
            if native_id and file_sha256(data.root / native_id) != summary["input_sha256"][native_id]:
                raise ValueError("Native input SHA mismatch")
        maps.append((baseline, hybrid)); truths.append(truth)
        bounds = [min(bounds[0], float(baseline.min()), float(hybrid.min())),
                  max(bounds[1], float(baseline.max()), float(hybrid.max()))]
        diff = hybrid.astype(float)-baseline.astype(float)
        delta_bounds = [min(delta_bounds[0], float(diff.min())), max(delta_bounds[1], float(diff.max()))]
        predicted = hybrid >= model["pixel_threshold"]
        truth_bool = truth.astype(bool)
        union = (predicted | truth_bool).sum()
        native_pixels = outside = 0
        if sample.mask:
            with Image.open(data.root / sample.mask) as image:
                mask = np.asarray(image.convert("L")) > 0
            native_pixels = int(mask.sum())
            # Crop footprint in native coordinates, using pixel centers. This
            # counts original GT pixels, not interpolated 256x256 mask pixels.
            offset = (resize-crop)//2
            ys = (np.arange(mask.shape[0])+.5)*resize/mask.shape[0]
            xs = (np.arange(mask.shape[1])+.5)*resize/mask.shape[1]
            covered = ((ys >= offset) & (ys < offset+crop))[:, None] & ((xs >= offset) & (xs < offset+crop))[None, :]
            outside = int((mask & ~covered).sum())
        rows.append({"index": i, "sample_id": identifier, "label": case["hybrid"]["label"],
                     "image_sha256": summary["input_sha256"][identifier],
                     "baseline_score": case["baseline"]["score"], "hybrid_score": case["hybrid"]["score"],
                     "max_abs_branch_difference": float(np.abs(diff).max()),
                     "mean_abs_branch_difference": float(np.abs(diff).mean()),
                     "branch_maps_bitwise_identical": bool(np.array_equal(baseline, hybrid)),
                     "truth_pixels": int(truth.sum()), "native_truth_pixels": native_pixels,
                     "native_truth_pixels_outside_crop": outside,
                     "hybrid_false_positive_pixels": int((predicted & ~truth_bool).sum()),
                     "hybrid_pixel_iou": float((predicted & truth_bool).sum()/union) if union else None,
                     "raw_map": f"map-{i:05d}.npz", "raw_map_sha256": file_sha256(evaluation / f"map-{i:05d}.npz")})
    global_hybrid = (min(float(h.min()) for _, h in maps), max(float(h.max()) for _, h in maps))
    for row, (_, hybrid) in zip(rows, maps):
        row["max_abs_shared_vs_image_display_difference"] = float(np.abs(
            normalized_display(hybrid, *global_hybrid)-normalized_display(hybrid)).max())
    destination.mkdir(parents=True)
    weights = stratified_weights([r["label"] for r in rows], protocol["intervals"]["replicates"], protocol["intervals"]["seed"])
    boot, intervals = {}, {}
    for j, method in enumerate(METHODS):
        scores = [cases[k][method]["score"] for k in ids]
        labels = [r["label"] for r in rows]
        stats = pro_statistics(truths, [m[j] for m in maps])
        point = float(pro_from_weights(stats, np.ones(len(rows)))[0])
        if not np.isclose(point, summary["methods"][method]["localization"]["au_pro"], atol=1e-12, rtol=0):
            raise ValueError("AU-PRO sufficient-statistic point differs from evaluation")
        boot[method+"_image_auroc"] = weighted_auroc(labels, scores, weights)
        boot[method+"_au_pro"] = pro_from_weights(stats, weights)
        intervals[method] = {}
        for metric, value in (("image_auroc", summary["methods"][method]["detection"]["auroc"]), ("au_pro", point)):
            alpha = (1-protocol["intervals"]["confidence"])/2
            intervals[method][metric] = {"point": value, "percentile_interval": np.quantile(boot[method+"_"+metric], [alpha, 1-alpha]).tolist()}
        # Save grid/statistics for independent replay, retaining native dtype maps.
        np.savez_compressed(destination / f"{method}_pro_statistics.npz", **stats)
    paired_intervals = {}
    for metric in ("image_auroc", "au_pro"):
        delta = boot["hybrid_"+metric]-boot["baseline_"+metric]
        paired_intervals[metric] = {"point": intervals["hybrid"][metric]["point"]-intervals["baseline"][metric]["point"],
                                    "percentile_interval": np.quantile(delta, [alpha, 1-alpha]).tolist()}
    np.savez_compressed(destination / "bootstrap.npz", image_multiplicities=weights, **boot)
    chosen = select_cases(rows, model["threshold"])
    selected = []
    for row in rows:
        reasons = [reason for reason, identifier in chosen.items() if identifier == row["sample_id"]]
        if reasons:
            selected.append(dict(row, selection_reasons=reasons))
    # Normal examples first, then anomaly examples, with stable native-ID order.
    selected.sort(key=lambda r: (r["label"], r["sample_id"]))
    for row in selected:
        stem = hashlib.sha256(row["sample_id"].encode()).hexdigest()[:12]
        raw_name = stem+"_raw.npz"
        shutil.copyfile(evaluation / row["raw_map"], destination / raw_name)
        metadata = dict(row, raw_map=raw_name, image_sha256=summary["input_sha256"][row["sample_id"]],
                        model_json_sha256=summary["model_json_sha256"], predictions=cases[row["sample_id"]],
                        shared_display_bounds=bounds, delta_display_bounds=delta_bounds,
                        metric_region=summary["metric_region"], protocol_sha256=file_sha256(protocol_path))
        write_json(destination / (stem+"_metadata.json"), metadata)
        row["figure_metadata"] = stem+"_metadata.json"
    render_audit(selected, maps, truths, data.root, destination / "shared_scale_failures.png", bounds, delta_bounds, model["threshold"], resize=resize, crop=crop)
    report = {
        "schema_version": 1, "queries": len(rows), "normal": sum(not r["label"] for r in rows),
        "anomalous": sum(r["label"] for r in rows), "metric_region": summary["metric_region"],
        "image_metric_scope": "All native test labels; image scores derived from center crop",
        "whole_image_segmentation_evaluated": False,
        "scored_area_fraction_before_256_resize": (crop/resize)**2,
        "native_defect_pixels_outside_crop": sum(r["native_truth_pixels_outside_crop"] for r in rows),
        "native_defect_pixels_total": sum(r["native_truth_pixels"] for r in rows),
        "images_with_defect_pixels_outside_crop": sum(r["native_truth_pixels_outside_crop"] > 0 for r in rows),
        "coverage_affected_images": [{"sample_id": r["sample_id"],
                                      "native_defect_pixels_outside_crop": r["native_truth_pixels_outside_crop"],
                                      "native_defect_pixels_total": r["native_truth_pixels"]}
                                     for r in rows if r["native_truth_pixels_outside_crop"] > 0],
        "native_anomalies_with_empty_cropped_mask": summary["native_anomalies_with_empty_cropped_mask"],
        "identical_baseline_hybrid_maps": sum(r["branch_maps_bitwise_identical"] for r in rows),
        "shared_score_display_bounds": bounds, "delta_display_bounds": delta_bounds,
        "display_panel_correction": "Old Global/Local panels are two display scalings of ONE hybrid map, never model branches",
        "previous_example_selection": "broken_large/000 was first anomaly in a two-image smoke check; not a prospectively selected representative figure",
        "reviewed_example": next((dict(r, image_threshold=model["threshold"],
                                       same_model_as_reported_cutoff=True)
                                  for r in rows if r["sample_id"] == "bottle/test/broken_large/000.png"), None),
        "intervals": intervals, "paired_hybrid_minus_baseline_intervals": paired_intervals,
        "interval_definition": protocol["intervals"], "figure_selection": chosen, "selected_cases": selected,
        "operational_metrics": {m: summary["methods"][m]["detection"] for m in METHODS},
        "source_metrics_sha256": file_sha256(evaluation / "metrics.json"),
        "source_predictions_sha256": file_sha256(evaluation / "predictions.jsonl"),
        "model_json_sha256": file_sha256(run_dir / "model.json"),
        "protocol_sha256": file_sha256(protocol_path), "thresholds_changed": False, "raw_maps_changed": False,
        "reporter_sha256": file_sha256(__file__),
        "history": "Known, previously exposed bottle category; one fitted support draw; no full-paper or held-out superiority claim",
    }
    write_json(destination / "report.json", report)
    with (destination / "per_image.jsonl").open("w") as handle:
        for row in rows:
            handle.write(json.dumps(row, allow_nan=False)+"\n")
    lines = ["# Full bottle category audit", "", f"{len(rows)} native test images: {report['normal']} normal, {report['anomalous']} anomalous. One normal support image, seed 17.", "",
             "Global/Local in the old figure meant two display scalings of the same hybrid map. They did not compare branches.",
             "The original large-defect figure was the first anomaly in a two-image smoke check, not a representative benchmark selection.", "",
             f"Image metrics use every native test label but crop-derived scores. Pixel metrics use the center {crop}/{resize} ROI only ({100*(crop/resize)**2:.2f}% of resized image area); outer borders are unscored.",
             f"Native GT pixels outside the crop: {report['native_defect_pixels_outside_crop']} across {report['images_with_defect_pixels_outside_crop']} images (native pixel-center crop footprint).", "",
             "| Method | Image AUROC (95% interval) | ROI AU-PRO (95% interval) | Accuracy at fixed cutoff | FP / normal | FN / anomaly |",
             "|---|---|---|---|---|---|"]
    for method in METHODS:
        values = intervals[method];d = report["operational_metrics"][method]
        def cell(key):
            v=values[key];lo,hi=v["percentile_interval"];return f"{v['point']:.4f} [{lo:.4f}, {hi:.4f}]"
        lines.append(f"| {method} | {cell('image_auroc')} | {cell('au_pro')} | {d['accuracy']:.4f} | {d['fp']} / {report['normal']} | {d['fn']} / {report['anomalous']} |")
    lines += ["", "Paired hybrid-minus-baseline differences (95% conditional intervals):"]
    for metric, value in paired_intervals.items():
        lo, hi = value["percentile_interval"]
        lines.append(f"- {metric}: {value['point']:+.4f} [{lo:+.4f}, {hi:+.4f}]")
    lines += ["", "Intervals: 2,000 paired, native-label-stratified query-image bootstrap replicates, conditional on this fitted bank. They exclude support/training/category uncertainty. AU-PRO uses the original cohort's fixed 128-score-rank threshold grid, 8-connected regions and FPR limit 0.3; its interval is a sampled-grid approximation. Bootstrap arrays and sufficient statistics are saved for replay.", "",
              f"Baseline/hybrid maps identical: {report['identical_baseline_hybrid_maps']} / {len(rows)}. See per_image.jsonl for raw max/mean absolute differences and separate display-scaling differences.", "",
              f"Locked image cutoff: {model['threshold']}; pixel cutoff: {model['pixel_threshold']}. Neither was optimized on this category.", "",
              "## Fixed-rule examples", "", "![Shared raw scale normal and defect examples](shared_scale_failures.png)", "",
              "Selection was recorded in protocol.json before full-category inference. Outcome-selected failure illustrations are diagnostic examples, not a random sample.", ""]
    for reason, identifier in chosen.items():
        lines.append(f"- {reason}: `{identifier}`" if identifier else f"- {reason}: none observed at the locked cutoff")
    lines += ["", "## Defect coverage excluded by the crop", ""]
    for case in report["coverage_affected_images"]:
        lines.append(f"- `{case['sample_id']}`: {case['native_defect_pixels_outside_crop']} / {case['native_defect_pixels_total']} native GT pixels outside the crop.")
    lines += ["", "Each selected case has a native-ID metadata JSON and an unchanged raw NPZ beside the figure. All 83 maps, native input hashes and paired scores are in ../evaluation. Heatmaps share one raw-score scale across methods and cases; additive differences have a separate labeled scale.", "",
              "These results describe the known bottle category and one fitted bank. They do not establish full-image segmentation performance, generalization across support draws, or superiority to a published full-dataset benchmark.", "",
              "Dataset attribution: MVTec Software GmbH; Bergmann et al., CVPR 2019. Derived images and GT masks retain MVTec AD's CC BY-NC-SA 4.0 license. Code licensing is unchanged."]
    (destination / "README.md").write_text("\n".join(lines)+"\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--data_path", type=Path)
    parser.add_argument("--prepare-protocol", type=Path)
    parser.add_argument("--evaluation", type=Path)
    parser.add_argument("--protocol", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.prepare_protocol:
        if args.prepare_protocol.exists():
            parser.error("Protocol already exists; never overwrite a recorded protocol")
        write_json(args.prepare_protocol, make_protocol(args.run_dir, args.data_path))
        print(f"Recorded protocol SHA256: {file_sha256(args.prepare_protocol)}")
    elif all((args.evaluation, args.protocol, args.output)):
        report = audit(args.evaluation, args.run_dir, args.protocol, args.output, args.data_path)
        print(json.dumps(report["intervals"], indent=2))
    else:
        parser.error("Use --prepare-protocol, or --evaluation/--protocol/--output together")


if __name__ == "__main__":
    main()
