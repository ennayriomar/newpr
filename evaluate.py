"""Evaluate SAFAL with reference-style logs, tables and diagnostic images."""
from __future__ import annotations

import argparse
from contextlib import redirect_stdout
from pathlib import Path
import sys
import tempfile

from test import build_parser, evaluate
from utils import read_json


class Tee:
    def __init__(self, *streams):
        self.streams = streams

    def write(self, text):
        for stream in self.streams:
            stream.write(text)
        return len(text)

    def flush(self):
        for stream in self.streams:
            stream.flush()


def main(argv=None, expected_dataset=None):
    parser = build_parser()
    parser.description = __doc__
    parser.set_defaults(localization=True)
    parser.add_argument("--no-localization", dest="localization", action="store_false")
    parser.add_argument("--visualize", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--max-visualizations", type=int)
    parser.add_argument("--save_dir", type=Path, help="Reference-style output parent")
    parser.add_argument("--save_name", help="Reference-style run name")
    args = parser.parse_args(argv)
    if args.max_visualizations is not None and args.max_visualizations < 1:
        parser.error("--max-visualizations must be positive")
    if args.output and (args.save_dir or args.save_name):
        parser.error("Choose --output or --save_dir/--save_name")
    if args.save_name and (Path(args.save_name).name != args.save_name or args.save_name in {".", ".."}):
        parser.error("--save_name must be a single directory name")
    if args.save_dir or args.save_name:
        args.output = (args.save_dir or Path("saved_results")) / (args.save_name or args.run_dir.name)
    args.save_maps = args.save_maps or args.visualize or args.localization
    training = read_json(args.run_dir / "training.json")
    from outputs import export_evaluation

    with tempfile.TemporaryFile(mode="w+") as log:
        with redirect_stdout(Tee(sys.stdout, log)):
            print(f"dataset: {training['dataset']}")
            print(f"shots: {training['shots']}")
            print(f"seed: {training['seed']}")
            summary = evaluate(args, expected_dataset)
            destination = Path(args.output or args.run_dir / "evaluation").resolve()
            result = export_evaluation(destination, args.run_dir, data_path=args.data_path,
                                       visualize=args.visualize, max_visualizations=args.max_visualizations)
        log.seek(0)
        (destination / "result.log").write_text(log.read())
    return summary, result


if __name__ == "__main__":
    main()
