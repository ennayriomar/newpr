"""Shared paths, frozen configuration and reproducibility helpers."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent
FRAMEWORK_ROOT = PROJECT_ROOT / "framework"


def use_local_framework() -> None:
    """Use this checkout's numerical engine, including in editable installs."""
    imported = sys.modules.get("safe_iad")
    if imported is not None:
        location = Path(imported.__file__).resolve()
        if not location.is_relative_to(FRAMEWORK_ROOT):
            raise RuntimeError("Another safe_iad checkout is imported; start a new Python process.")
    if str(FRAMEWORK_ROOT) not in sys.path:
        sys.path.insert(0, str(FRAMEWORK_ROOT))


def file_sha256(path: str | Path) -> str:
    with Path(path).open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def read_json(path: str | Path) -> dict:
    return json.loads(Path(path).read_text())


def write_json(path: str | Path, value: object) -> None:
    Path(path).write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")


def resolve_path(value: str | Path, base: Path) -> Path:
    path = Path(value).expanduser()
    return (base / path if not path.is_absolute() else path).resolve()


def model_config(path: str | Path, **overrides) -> tuple[dict, dict]:
    """Resolve paths and load the exact source-selected scoring decision."""
    config_path = Path(path).resolve(strict=True)
    config = read_json(config_path)
    encoder = dict(config["encoder"])
    for field in ("source_dir", "checkpoint"):
        value = overrides.get(field)
        encoder[field] = str(resolve_path(value, Path.cwd()) if value else
                             resolve_path(encoder[field], config_path.parent))
    if overrides.get("device"):
        encoder["device"] = overrides["device"]
    lock_path = resolve_path(config["selection"]["file"], config_path.parent)
    if file_sha256(lock_path) != config["selection"]["sha256"]:
        raise ValueError("Source selection lock checksum mismatch.")
    lock = read_json(lock_path)
    if lock["verification_inference_seen"] or lock["verification_masks_seen"]:
        raise ValueError("Selection lock includes reserved evaluation exposure.")
    lock["loaded_selection_sha256"] = file_sha256(lock_path)
    return encoder, lock


def interface_hashes() -> dict[str, str]:
    names = ("utils.py", "dataset.py", "models/uad.py", "models/vit_encoder.py",
             "train.py", "test.py", "predict.py")
    return {name: file_sha256(PROJECT_ROOT / name) for name in names}


def check_interface(expected: dict[str, str]) -> None:
    if expected != interface_hashes():
        raise ValueError("The training/evaluation interface changed since fitting this bank.")


def new_directory(path: str | Path) -> Path:
    destination = Path(path).resolve()
    if destination.exists():
        raise ValueError(f"Output already exists; choose a new directory: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    return destination
