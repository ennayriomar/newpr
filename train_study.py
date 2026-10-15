"""Reproduce the locked development-selection and reserved-evaluation study."""
from __future__ import annotations

import argparse
from pathlib import Path

from utils import PROJECT_ROOT, read_json, resolve_path, use_local_framework, write_json


def resolved_config(path, overrides):
    path = Path(path).resolve(strict=True)
    config = read_json(path)
    for name in ("development_manifest", "known_exposure", "previous_verification_lock"):
        config[name] = str(resolve_path(config[name], path.parent))
    for dataset in config["roots"]:
        override = overrides.get(dataset)
        config["roots"][dataset] = str(resolve_path(override, Path.cwd()) if override else
                                       resolve_path(config["roots"][dataset], path.parent))
    for name in ("source_dir", "checkpoint"):
        override = overrides.get(name)
        config["encoder"][name] = str(resolve_path(override, Path.cwd()) if override else
                                      resolve_path(config["encoder"][name], path.parent))
    if overrides.get("device"):
        config["encoder"]["device"] = overrides["device"]
    return config


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=["plan", "develop", "evaluate", "report"], default="develop")
    parser.add_argument("--config", type=Path, default=PROJECT_ROOT / "configs/study.json")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--mvtec-root", type=Path)
    parser.add_argument("--visa-root", type=Path)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--device", choices=["cpu", "cuda"])
    args = parser.parse_args(argv)
    use_local_framework()
    from safe_iad.vision_hybrid_cli import develop, evaluate, plan, report, stage_lock

    output = args.output.resolve()
    saved = output / "resolved_config.json"
    overrides = {"mvtec_ad": args.mvtec_root, "visa": args.visa_root,
                 "source_dir": args.source_dir, "checkpoint": args.checkpoint, "device": args.device}
    if args.stage in {"evaluate", "report"}:
        if any(value is not None for value in overrides.values()):
            parser.error("Evaluation uses the saved configuration; omit training overrides.")
        if not saved.is_file():
            parser.error("Run the plan/develop stage in this output directory first.")
    with stage_lock(output):
        if args.stage in {"plan", "develop"}:
            config = resolved_config(args.config, overrides)
            if saved.exists():
                if read_json(saved) != config:
                    raise ValueError("Study settings changed; choose a fresh output directory.")
            else:
                if any(p.name != ".execution.lock" for p in output.iterdir()):
                    raise ValueError("Output contains unrelated files; choose a fresh directory.")
                write_json(saved, config)
            plan(saved, output)
        if args.stage == "develop":
            return develop(saved, output)
        if args.stage == "evaluate":
            return evaluate(saved, output)
        if args.stage == "report":
            return report(saved, output)


if __name__ == "__main__":
    main()
