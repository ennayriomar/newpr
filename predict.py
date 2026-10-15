"""Predict one image using a selected SAFAL feature bank."""
import argparse
from pathlib import Path

from utils import use_local_framework


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", type=Path, required=True, help="Checkpoint prefix, without .json/.npz")
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--source-dir", type=Path)
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument("--device", choices=["cpu", "cuda"])
    args = parser.parse_args(argv)
    use_local_framework()
    from safe_iad.vision_hybrid_cli import predict
    return predict(args.model, args.image, args.output, args.source_dir, args.checkpoint, args.device)


if __name__ == "__main__":
    main()
