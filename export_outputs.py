"""Render completed saved category results without rerunning the encoder."""
import argparse
from contextlib import redirect_stdout
from pathlib import Path
import sys

from evaluate import Tee
from outputs import export_evaluation
from utils import new_directory


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evaluation", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--data_path", type=Path)
    parser.add_argument("--no-visualize", action="store_true")
    parser.add_argument("--max-visualizations", type=int)
    args = parser.parse_args(argv)
    destination = new_directory(args.output)
    destination.mkdir()
    with (destination / "result.log").open("w") as log:
        with redirect_stdout(Tee(sys.stdout, log)):
            return export_evaluation(args.evaluation, args.run_dir, data_path=args.data_path,
                                     visualize=not args.no_visualize,
                                     max_visualizations=args.max_visualizations,
                                     destination=destination)


if __name__ == "__main__":
    main()
