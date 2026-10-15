"""Collect category/draw presentation results into reference-style means."""
import argparse
from contextlib import redirect_stdout
from pathlib import Path
import sys

from evaluate import Tee
from outputs import save_tables
from utils import new_directory, read_json, write_json


def collect_results(paths, include_subsets=False):
    records, seen, sources = [], set(), []
    shot_counts = set()
    for path in paths:
        path = Path(path).resolve(strict=True)
        result = read_json(path)
        if result["subset"] and not include_subsets:
            raise ValueError("Subset results require --include-subsets and are not full-category benchmarks.")
        key = (result["dataset"], result["category"], result["shots"], result["seed"],
               result["model_json_sha256"], result["cohort_sha256"])
        if key in seen:
            raise ValueError("Duplicate category/draw/cohort result.")
        seen.add(key)
        shot_counts.add(result["shots"])
        records.extend(result["records"])
        sources.append(str(path))
    if len(shot_counts) != 1 or not records:
        raise ValueError("Collect a nonempty set with one shared shot budget.")
    return records, sources


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results", type=Path, nargs="+", required=True,
                        help="results.json files from evaluated category/draw runs")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--include-subsets", action="store_true")
    args = parser.parse_args(argv)
    records, sources = collect_results(args.results, args.include_subsets)
    destination = new_directory(args.output)
    destination.mkdir()
    context = (f"{len(sources)} category/draw results. Means give each category equal weight. "
               f"Subset inclusion allowed: {args.include_subsets}. Only listed categories are represented.")
    with (destination / "result.log").open("w") as log:
        with redirect_stdout(Tee(sys.stdout, log)):
            print(context)
            rows = save_tables(records, destination, context)
    write_json(destination / "summary.json", {"sources": sources, "rows": rows,
                                             "includes_subsets_allowed": args.include_subsets,
                                             "full_paper_benchmark_established": False})
    return rows


if __name__ == "__main__":
    main()
