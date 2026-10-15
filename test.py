"""Evaluate a fitted category bank without selecting parameters or cutoffs."""
from __future__ import annotations

import argparse
from pathlib import Path

from utils import (check_interface, file_sha256, new_directory, read_json,
                   use_local_framework, write_json)


def evaluate(args, expected_dataset=None):
    use_local_framework()
    import numpy as np
    from dataset import IndustrialDataset
    from models import Encoder, HybridParameters, SAFAL
    from models.uad import fuse_raw
    from safe_iad.research_metrics import localization_metrics, thresholded_detection_metrics

    run_dir = args.run_dir.resolve(strict=True)
    training = read_json(run_dir / "training.json")
    check_interface(training["interface_sha256"])
    if expected_dataset and training["dataset"] != expected_dataset:
        raise ValueError("This dataset-specific script does not match the fitted bank.")
    if file_sha256(run_dir / "model.json") != training["model_json_sha256"]:
        raise ValueError("Fitted model metadata changed.")
    output = new_directory(args.output or run_dir / "evaluation")
    data = IndustrialDataset(args.data_path or training["data_path"], training["dataset"],
                             training["category"], phase="test")
    for identifier, expected in training["support_sha256"].items():
        if file_sha256(data.root / identifier) != expected:
            raise ValueError("A normal training reference changed.")
    samples = data.queries(args.max_images)
    model = SAFAL.load(run_dir / "model")
    expected_encoder = model.provenance["encoder"]
    runtime = expected_encoder["runtime"]
    encoder = Encoder(args.source_dir or runtime["source_dir"],
                      args.checkpoint or runtime["checkpoint"],
                      device=args.device or expected_encoder["device"], threads=runtime["threads"],
                      resize=expected_encoder["resize"], crop=expected_encoder["crop"],
                      layers=expected_encoder["layers"])
    actual_encoder = encoder.metadata()
    for field in ("backbone", "checkpoint_sha256", "source_manifest_sha256", "crop", "resize",
                  "layers", "position_interpolation", "implementation_sha256"):
        if actual_encoder[field] != expected_encoder[field]:
            raise ValueError(f"Trained encoder semantics changed: {field}")
    output.mkdir()
    rows, labels, truths = [], [], []
    scores = {"baseline": [], "hybrid": []}
    maps = {method: [] for method in scores}
    inputs = {}
    empty_roi = []
    for index, sample in enumerate(samples):
        print(f"QUERY {index + 1}/{len(samples)} {sample.image}", flush=True)
        image_path = data.root / sample.image
        before = file_sha256(image_path)
        query = encoder.query(image_path)
        if file_sha256(image_path) != before:
            raise ValueError("A query image changed during extraction.")
        inputs[sample.image] = before
        raw = model.raw(query)
        predictions = {"baseline": fuse_raw(raw, HybridParameters(), model.grid),
                       "hybrid": fuse_raw(raw, model.params, model.grid)}
        # Native labels and masks enter only after both scores are computed.
        label = int(sample.label != "normal")
        labels.append(label)
        if args.localization or args.save_maps:
            truth = data.mask(sample, resize=expected_encoder["resize"], crop=expected_encoder["crop"])
            if sample.mask:
                inputs[sample.mask] = file_sha256(data.root / sample.mask)
            if label and not truth.any():
                empty_roi.append(sample.image)
            if args.localization:
                truths.append(truth)
        arrays = {}
        for method, prediction in predictions.items():
            score = prediction["image_score"]
            scores[method].append(score)
            if args.localization:
                maps[method].append(prediction["map"])
            if args.save_maps:
                arrays[method] = prediction["map"]
            rows.append({"sample_id": sample.image, "label": label, "method": method,
                         "score": score, "threshold": model.threshold,
                         "decision": score >= model.threshold, "probabilities": False})
        if args.save_maps:
            arrays["truth"] = truth.astype(np.uint8)
            np.savez_compressed(output / f"map-{index:05d}.npz", **arrays)
    metrics = {}
    for method, values in scores.items():
        detection = thresholded_detection_metrics(labels, values, model.threshold)
        detection["accuracy"] = (detection["tp"] + detection["tn"]) / detection["queries"]
        metrics[method] = {"detection": detection}
        if args.localization:
            metrics[method]["localization"] = localization_metrics(
                truths, maps[method], model.pixel_threshold, max_thresholds=128)
    summary = {
        "schema_version": 1, "dataset": training["dataset"], "category": training["category"],
        "shots": training["shots"], "seed": training["seed"], "queries": len(samples),
        "subset": len(samples) < len(data), "max_images_requested": args.max_images,
        "full_paper_benchmark": False, "parameters_selected_on_these_queries": False,
        "methods": metrics, "input_sha256": inputs,
        "model_json_sha256": file_sha256(run_dir / "model.json"),
        "normal_support_ids": training["support_ids"], "extra_target_calibration_images": 0,
        "native_anomalies_with_empty_cropped_mask": empty_roi,
        "metric_region": "Center-cropped ROI at 256x256; outer image border unscored",
        "cohort": "Native category test split; no claim of exclusion from prior research history",
        "threshold_scope": "Unchanged source-category cutoff; no target FPR guarantee",
        "source_selection_supervision": training["source_selection_supervision"],
    }
    write_json(output / "metrics.json", summary)
    with (output / "predictions.jsonl").open("w") as handle:
        import json
        for row in rows:
            handle.write(json.dumps(row, allow_nan=False) + "\n")
    print(f"Saved measured results: {output / 'metrics.json'}", flush=True)
    return summary


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--data_path", type=Path, help="Override the native dataset root")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-images", type=int, help="Balanced-order smoke subset; results marked as subset")
    parser.add_argument("--localization", action="store_true")
    parser.add_argument("--save-maps", action="store_true")
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--device", choices=["cpu", "cuda"])
    return parser


def main(argv=None, expected_dataset=None):
    return evaluate(build_parser().parse_args(argv), expected_dataset)


if __name__ == "__main__":
    main()
