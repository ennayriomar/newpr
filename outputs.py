"""Measured result tables and ROI-aligned VisionAD-style visualizations.

Color normalization affects displayed PNGs only. Evaluation scores, maps and
the frozen image/pixel decision thresholds are never modified here.
"""
from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path, PurePosixPath

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from sklearn.metrics import precision_recall_curve

from utils import file_sha256, read_json, write_json

METRICS = ("I-Auroc", "I-AP", "I-F1", "P-AUROC", "P-AP", "P-F1", "P-AUPRO")


def maximum_f1(labels, scores):
    """Descriptive benchmark F1-max; never returns a deployment threshold."""
    labels, scores = np.asarray(labels).ravel(), np.asarray(scores).ravel()
    if not len(labels) or labels.shape != scores.shape or not np.isin(labels, [0, 1]).all():
        raise ValueError("Matching nonempty binary labels and scores are required.")
    if not np.isfinite(scores).all():
        raise ValueError("Scores must be finite.")
    if not labels.any():
        return None
    precision, recall, _ = precision_recall_curve(labels, scores)
    denominator = precision + recall
    values = np.divide(2 * precision * recall, denominator,
                       out=np.zeros_like(denominator), where=denominator > 0)
    return float(values.max())


def normalized_display(score_map, minimum=None, maximum=None):
    values = np.array(score_map, dtype=np.float64, copy=True)
    if values.ndim != 2 or not values.size or not np.isfinite(values).all():
        raise ValueError("A finite nonempty 2D display map is required.")
    minimum = float(values.min()) if minimum is None else float(minimum)
    maximum = float(values.max()) if maximum is None else float(maximum)
    if not np.isfinite([minimum, maximum]).all() or maximum < minimum:
        raise ValueError("Invalid display bounds.")
    if maximum == minimum:
        return np.zeros_like(values)
    return np.clip((values - minimum) / (maximum - minimum), 0, 1)


def heatmap_overlay(image, normalized):
    from matplotlib import colormaps

    rgb = np.asarray(image, dtype=np.float64)
    if rgb.shape != normalized.shape + (3,):
        raise ValueError("Image and display map geometries differ.")
    colors = colormaps["jet"](normalized)[..., :3] * 255
    return Image.fromarray(np.round(.5 * rgb + .5 * colors).astype(np.uint8))


def image_roi(path, resize=448, crop=392):
    with Image.open(path) as original:
        image = original.convert("RGB").resize((resize, resize), Image.Resampling.BILINEAR)
    offset = (resize - crop) // 2
    return image.crop((offset, offset, offset + crop, offset + crop)).resize(
        (256, 256), Image.Resampling.BILINEAR)


def render_case(image_path, score_map, truth, destination, *, stem, global_bounds,
                resize=448, crop=392, title="", score=None):
    """Save five reference-style panels and a labeled five-panel compound PNG."""
    destination = Path(destination)
    if not stem or stem in {".", ".."} or "/" in stem or "\\" in stem:
        raise ValueError("Unsafe output basename.")
    raw, truth = np.asarray(score_map), np.asarray(truth)
    if raw.shape != (256, 256) or truth.shape != raw.shape or not np.isin(truth, [0, 1]).all():
        raise ValueError("Expected a 256x256 map and matching binary ROI mask.")
    image = image_roi(image_path, resize, crop)
    mask = truth.astype(bool)
    red = np.array(image, copy=True)
    red[mask] = [255, 0, 0]
    panels = {
        "ori": image,
        "gt": Image.fromarray(mask.astype(np.uint8) * 255).convert("RGB"),
        "global": heatmap_overlay(image, normalized_display(raw, *global_bounds)),
        "local": heatmap_overlay(image, normalized_display(raw)),
        "gt_red": Image.fromarray(red),
    }
    names = {kind: destination / f"{stem}_{kind}.png" for kind in (*panels, "compound")}
    if any(path.exists() for path in names.values()):
        raise ValueError("Visualization output exists; choose a new destination.")
    destination.mkdir(parents=True, exist_ok=True)
    for kind, panel in panels.items():
        panel.save(names[kind])
    gap, padding = 8, 12
    canvas = Image.new("RGB", (5 * 256 + 4 * gap + 2 * padding, 340), "white")
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=14)
    subtitle = f"{title} | score={score:.4f}" if score is not None else title
    draw.text((padding, 8), subtitle, fill="black", font=font)
    labels = ("Image (center ROI)", "Ground truth", "Hybrid: shared scale", "Hybrid: image contrast", "Ground truth in red")
    for i, ((_, panel), label) in enumerate(zip(panels.items(), labels)):
        x = padding + i * (256 + gap)
        draw.text((x, 33), label, fill="black", font=font)
        canvas.paste(panel, (x, 54))
    draw.text((padding, 316), "Same hybrid map in both heatmaps; display scaling only. Center ROI; outer borders unscored.",
              fill="#555555", font=font)
    canvas.save(names["compound"])
    return {kind: str(path) for kind, path in names.items()}


def metric_line(name, values):
    formatted = ", ".join(f"{key}:{'NA' if values[key] is None else format(values[key], '.4f')}"
                          for key in METRICS)
    return f"{name}: {formatted}"


def save_tables(records, destination, context):
    """Write per-method category rows and equal-category macro means."""
    destination = Path(destination)
    rows = []
    datasets = sorted({r["dataset"] for r in records})
    for dataset in datasets:
        methods = sorted({r["method"] for r in records if r["dataset"] == dataset})
        for method in methods:
            categories = sorted({r["category"] for r in records
                                 if r["dataset"] == dataset and r["method"] == method})
            category_rows = []
            print(f"Dataset: {dataset} | Method: {method} | Categories: {len(categories)}")
            for category in categories:
                group = [r for r in records if (r["dataset"], r["method"], r["category"]) ==
                         (dataset, method, category)]
                values = {key: (float(np.mean([r[key] for r in group]))
                                if all(r[key] is not None for r in group) else None)
                          for key in METRICS}
                row = {"dataset": dataset, "method": method, "category": category,
                       "draws": len(group), **values}
                category_rows.append(row)
                print(metric_line(category, values))
            rows.extend(category_rows)
            mean = {key: (float(np.mean([r[key] for r in category_rows]))
                          if all(r[key] is not None for r in category_rows) else None)
                    for key in METRICS}
            rows.append({"dataset": dataset, "method": method, "category": "Mean",
                         "draws": None, **mean})
            print(metric_line("Mean", mean))
    headers = ("dataset", "method", "category", "draws", *METRICS)
    with (destination / "metrics.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    lines = ["# Measured category results", "", context, "",
             "I-F1/P-F1 are descriptive evaluation F1-max. Operational cutoffs remain unchanged.", "",
             "| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
    for row in rows:
        values = ["NA" if row[key] is None else
                  (f"{row[key]:.4f}" if key in METRICS else str(row[key])) for key in headers]
        lines.append("| " + " | ".join(values) + " |")
    (destination / "metrics.md").write_text("\n".join(lines) + "\n")
    return rows


def export_evaluation(evaluation, run_dir, *, data_path=None, visualize=True,
                      max_visualizations=None, destination=None):
    """Present a completed category evaluation without rerunning the model."""
    evaluation, run_dir = Path(evaluation), Path(run_dir)
    destination = Path(destination) if destination is not None else evaluation
    if max_visualizations is not None and max_visualizations < 1:
        raise ValueError("--max-visualizations must be positive.")
    if (destination / "results.json").exists():
        raise ValueError("Presentation outputs already exist.")
    summary = read_json(evaluation / "metrics.json")
    training = read_json(run_dir / "training.json")
    encoder = read_json(run_dir / "model.json")["provenance"]["encoder"]
    root = Path(data_path or training["data_path"]).resolve(strict=visualize)
    with (evaluation / "predictions.jsonl").open() as handle:
        predictions = [json.loads(line) for line in handle]
    cases = {}
    for row in predictions:
        case = cases.setdefault(row["sample_id"], {})
        if row["method"] in case:
            raise ValueError("Duplicate method/image prediction.")
        case[row["method"]] = row
    methods = set(summary["methods"])
    if len(cases) != summary["queries"] or any(set(case) != methods for case in cases.values()):
        raise ValueError("Incomplete saved prediction pairs.")
    if any(len({row["label"] for row in case.values()}) != 1 for case in cases.values()):
        raise ValueError("Paired methods have different native image labels.")
    have_maps = all((evaluation / f"map-{i:05d}.npz").is_file() for i in range(len(cases)))
    if visualize and not have_maps:
        raise ValueError("Saved maps are missing; evaluate with --save-maps or export with --no-visualize.")
    records = []
    for method, measured in summary["methods"].items():
        detection = measured["detection"]
        localization = measured.get("localization", {})
        values = {"I-Auroc": detection["auroc"], "I-AP": detection["ap"],
                  "I-F1": maximum_f1([case[method]["label"] for case in cases.values()],
                                      [case[method]["score"] for case in cases.values()]),
                  "P-AUROC": localization.get("pixel_auroc"), "P-AP": localization.get("pixel_ap"),
                  "P-F1": None, "P-AUPRO": localization.get("au_pro")}
        if localization and have_maps:
            truths, maps = [], []
            for i in range(len(cases)):
                with np.load(evaluation / f"map-{i:05d}.npz", allow_pickle=False) as arrays:
                    truths.append(arrays["truth"].ravel())
                    maps.append(arrays[method].ravel())
            values["P-F1"] = maximum_f1(np.concatenate(truths), np.concatenate(maps))
        records.append({"dataset": summary["dataset"], "category": summary["category"],
                        "method": method, "shots": summary["shots"], "seed": summary["seed"], **values})
    context = (f"{summary['queries']} native image IDs; shots={summary['shots']}; seed={summary['seed']}; "
               f"subset={summary['subset']}. Mean covers only the listed categories. "
               "All values use a 0–1 scale; NA means unavailable.")
    print(context)
    print("I-F1/P-F1: evaluation F1-max only; fixed-source metrics remain in metrics.json.")
    table_rows = save_tables(records, destination, context)
    operational = {}
    for method, measured in summary["methods"].items():
        detection = measured["detection"]
        operational[method] = {"image_threshold": detection["threshold"],
                               "image_f1": detection["f1"], "accuracy": detection["accuracy"],
                               "false_alarm_rate": detection["false_alarm_rate"],
                               "pixel_f1": measured.get("localization", {}).get("pixel_f1")}
        accuracy = detection["accuracy"]
        print(f"{method} fixed-source cutoff: Accuracy:{accuracy:.4f}, I-F1:{detection['f1']}, "
              f"FPR:{detection['false_alarm_rate']}")
    visualizations, bounds = [], None
    if visualize:
        minimum, maximum = np.inf, -np.inf
        for i in range(len(cases)):
            with np.load(evaluation / f"map-{i:05d}.npz", allow_pickle=False) as arrays:
                minimum = min(minimum, float(arrays["hybrid"].min()))
                maximum = max(maximum, float(arrays["hybrid"].max()))
        bounds = [minimum, maximum]
        for i, (identifier, case) in enumerate(cases.items()):
            if max_visualizations is not None and i >= max_visualizations:
                break
            relative = PurePosixPath(identifier)
            if relative.is_absolute() or ".." in relative.parts or "\\" in identifier:
                raise ValueError("Unsafe native image ID.")
            image_path = (root / identifier).resolve(strict=True)
            if not image_path.is_relative_to(root) or file_sha256(image_path) != summary["input_sha256"][identifier]:
                raise ValueError("Visualization image differs from the scored input.")
            # Include a short native-ID digest to prevent equal-stem collisions.
            stem = relative.stem + "__" + hashlib.sha256(identifier.encode()).hexdigest()[:8]
            image_destination = destination / "vis_compound_1" / summary["category"] / relative.parent.name
            with np.load(evaluation / f"map-{i:05d}.npz", allow_pickle=False) as arrays:
                files = render_case(image_path, arrays["hybrid"], arrays["truth"], image_destination,
                                    stem=stem, global_bounds=bounds, resize=encoder["resize"],
                                    crop=encoder["crop"], title=f"{summary['category']} / {identifier}",
                                    score=case["hybrid"]["score"])
            # Keep the scored arrays and native ID beside each figure, without
            # recomputing, rescaling or casting any score.
            import shutil
            raw_path = image_destination / f"{stem}_raw.npz"
            shutil.copyfile(evaluation / f"map-{i:05d}.npz", raw_path)
            metadata_path = image_destination / f"{stem}_metadata.json"
            write_json(metadata_path, {
                "sample_id": identifier, "image_sha256": summary["input_sha256"][identifier],
                "model_json_sha256": summary["model_json_sha256"], "predictions": case,
                "raw_map": raw_path.name, "raw_map_sha256": file_sha256(raw_path),
                "arrays": "baseline, hybrid and truth; raw 256x256 scored ROI",
                "shared_display_bounds": bounds,
                "display_semantics": "global/local are shared/per-image scaling of the SAME hybrid map",
                "metric_region": summary["metric_region"],
            })
            files.update(raw=str(raw_path), metadata=str(metadata_path))
            visualizations.append({"sample_id": identifier,
                                   "files": {kind: str(Path(path).relative_to(destination))
                                             for kind, path in files.items()}})
        print(f"We have saved the predicted images: {destination / 'vis_compound_1'}")
    cohort = hashlib.sha256(json.dumps(cases, sort_keys=True).encode()).hexdigest()
    result = {"schema_version": 1, "records": records, "table_rows": table_rows,
              "dataset": summary["dataset"], "category": summary["category"],
              "shots": summary["shots"], "seed": summary["seed"], "subset": summary["subset"],
              "queries": summary["queries"], "cohort_sha256": cohort,
              "model_json_sha256": summary["model_json_sha256"],
              "f1_semantics": "Evaluation F1-max; no deployment threshold selected",
              "operational_metrics": operational,
              "operational_thresholds_changed": False, "raw_maps_changed": False,
              "visualization_global_bounds": bounds,
              "global_normalization_scope": "Hybrid maps of this evaluated category/draw only; no labels",
              "visualization_region": summary["metric_region"], "visualizations": visualizations}
    result["source_metrics_sha256"] = file_sha256(evaluation / "metrics.json")
    result["source_predictions_sha256"] = file_sha256(evaluation / "predictions.jsonl")
    write_json(destination / "results.json", result)
    return result
