"""Discover and execute the existing tests unchanged; save exact outcomes."""
import argparse
import json
from pathlib import Path
import sys
import time
import unittest


def flatten(suite):
    for item in suite:
        if isinstance(item, unittest.TestSuite):
            yield from flatten(item)
        else:
            yield item


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--suite", choices=["tests", "framework/tests"], required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    sys.path[:0] = [str(args.source), str(args.source / "framework")]
    suite = unittest.defaultTestLoader.discover(str(args.source / args.suite))
    ids = [case.id() for case in flatten(suite)]
    started = time.perf_counter()
    print(json.dumps({"discovered": len(ids), "test_ids": ids}), flush=True)
    result = unittest.TextTestRunner(stream=sys.stdout, verbosity=2).run(suite)
    report = {
        "suite": args.suite, "test_ids": ids, "discovered": len(ids),
        "run": result.testsRun, "failures": [t.id() for t, _ in result.failures],
        "errors": [t.id() for t, _ in result.errors],
        "skipped": [{"id": t.id(), "reason": r} for t, r in result.skipped],
        "expected_failures": [t.id() for t, _ in result.expectedFailures],
        "unexpected_successes": [t.id() for t in result.unexpectedSuccesses],
        "successful": result.wasSuccessful(), "elapsed_seconds": time.perf_counter() - started,
        "source": str(args.source), "python": sys.version,
        "note": "Existing tests only. No new cutoff implementation or real inference is certified.",
    }
    args.output.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    raise SystemExit(0 if result.wasSuccessful() else 1)


if __name__ == "__main__":
    main()
