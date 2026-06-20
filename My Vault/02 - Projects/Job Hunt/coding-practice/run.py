#!/usr/bin/env python3
"""Local interview-practice runner (stdlib only — no pip installs needed).

Usage:
    python3 run.py <problem>            # run all levels
    python3 run.py <problem> 1          # run only level 1
    python3 run.py <problem> --ref      # run tests against reference_solution.py (sanity-check)

Examples:
    python3 run.py in-memory-db
    python3 run.py in-memory-db 3
    python3 run.py in-memory-db --ref
"""
import argparse
import importlib
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    ap = argparse.ArgumentParser(description="Run a practice problem's tests.")
    ap.add_argument("problem", help="problem folder name under problems/")
    ap.add_argument("level", nargs="?", default=None, help="optional level number, e.g. 1")
    ap.add_argument("--ref", action="store_true",
                    help="test the reference_solution instead of your solution.py")
    args = ap.parse_args()

    pdir = os.path.join(HERE, "problems", args.problem)
    if not os.path.isdir(pdir):
        print(f"No such problem: problems/{args.problem}")
        print("Available:", ", ".join(sorted(
            d for d in os.listdir(os.path.join(HERE, "problems"))
            if not d.startswith("_") and os.path.isdir(os.path.join(HERE, "problems", d)))))
        return 2

    # Make the problem folder importable as top-level modules (solution, test_solution, ...).
    sys.path.insert(0, pdir)

    # Optionally swap the reference in as `solution` BEFORE importing the tests.
    if args.ref:
        ref = importlib.import_module("reference_solution")
        sys.modules["solution"] = ref
        print(">>> running against reference_solution.py\n")

    tests = importlib.import_module("test_solution")
    loader = unittest.TestLoader()
    if args.level:
        try:
            suite = loader.loadTestsFromName(f"TestLevel{args.level}", tests)
        except Exception as e:  # noqa: BLE001
            print(f"Could not load level {args.level}: {e}")
            return 2
    else:
        suite = loader.loadTestsFromModule(tests)

    result = unittest.TextTestRunner(verbosity=2).run(suite)
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    raise SystemExit(main())
