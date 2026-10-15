"""Fit a normal-reference SAFAL bank with a frozen source-selected preset."""
from __future__ import annotations

import argparse
from pathlib import Path

from utils import (PROJECT_ROOT, file_sha256, interface_hashes, model_config,
                   new_directory, use_local_framework, write_json)


def fit(args):
    use_local_framework()
    from dataset import IndustrialDataset
    from models import Encoder, HybridParameters, SAFAL
    from safe_iad.vision_hybrid_features import SLOTS

    output = new_directory(args.output)
    data = IndustrialDataset(args.data_path, args.dataset, args.category, phase="train")
    support_ids = data.support_ids(args.shots, args.seed, args.support_id)
    support_hashes = {identifier: file_sha256(data.root / identifier)
                      for identifier in support_ids}
    encoder_settings, lock = model_config(
        args.config, source_dir=args.source_dir, checkpoint=args.checkpoint, device=args.device)
    encoder = Encoder(**encoder_settings)
    decision = lock["decision"]
    params = HybridParameters(**decision["params"])
    features, slots = [], {slot: [] for slot in SLOTS}
    for identifier in support_ids:
        print(f"SUPPORT {identifier}", flush=True)
        values, indices = encoder.support(data.root / identifier)
        offset = len(features)
        features.extend(values)
        for slot in SLOTS:
            slots[slot].extend(offset + index for index in indices[slot])
    model = SAFAL(features, slots, support_ids, threads=encoder_settings["threads"])
    if any(file_sha256(data.root / identifier) != expected
           for identifier, expected in support_hashes.items()):
        raise ValueError("A normal reference changed during fitting.")
    provenance = {
        "status": "globally selected research candidate",
        "encoder": encoder.metadata(),
        "selection": "Frozen 2026-10-15 source-category decision; no query fitting",
        "selection_lock_sha256": lock["loaded_selection_sha256"],
        "episode": {"dataset": args.dataset, "category": args.category,
                    "shots": args.shots, "seed": args.seed, "support_ids": support_ids,
                    "calibration_ids": []},
    }
    output.mkdir()
    model.save(output / "model", params, decision["image_threshold"], provenance,
               pixel_threshold=decision["pixel_threshold"])
    manifest = {
        "schema_version": 1, "dataset": args.dataset, "category": args.category,
        "data_path": str(data.root), "shots": args.shots, "seed": args.seed,
        "support_ids": support_ids, "extra_target_calibration_images": 0,
        "support_sha256": support_hashes,
        "source_config_sha256": file_sha256(args.config),
        "parameters_id": params.id, "model_json_sha256": file_sha256(output / "model.json"),
        "interface_sha256": interface_hashes(),
        "source_selection_supervision": "50 normal and 50 anomalous source images plus masks",
        "cutoff_scope": "Source-category cutoff; target false-alarm rate is not guaranteed",
        "support_draw_rule": "random.Random(seed).sample(sorted native normal train IDs)",
        "previous_pilot_accuracy_improved": False,
    }
    write_json(output / "training.json", manifest)
    print(f"Saved normal-reference bank: {output / 'model.npz'}", flush=True)
    return manifest


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", choices=["mvtec_ad", "visa"], required=True)
    parser.add_argument("--data_path", type=Path, required=True)
    parser.add_argument("--category", required=True)
    parser.add_argument("--shots", type=int, default=1)
    parser.add_argument("--seed", type=int, default=17)
    parser.add_argument("--support-id", action="append", help="Explicit normal native train image ID")
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs/hybrid.json")
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--device", choices=["cpu", "cuda"])
    parser.add_argument("--output", type=Path, required=True)
    return parser


def main(argv=None):
    return fit(build_parser().parse_args(argv))


if __name__ == "__main__":
    main()
