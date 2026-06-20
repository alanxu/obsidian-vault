#!/usr/bin/env python3
"""Scaffold a new practice problem from problems/_template/.

Usage:
    python3 new_problem.py <problem-slug>
Example:
    python3 new_problem.py banking-system
"""
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python3 new_problem.py <problem-slug>")
        return 2
    name = sys.argv[1]
    src = os.path.join(HERE, "problems", "_template")
    dst = os.path.join(HERE, "problems", name)
    if os.path.exists(dst):
        print(f"already exists: problems/{name}")
        return 1
    shutil.copytree(src, dst)
    print(f"created problems/{name}\n")
    print("next:")
    print(f"  1. read/write the spec  : problems/{name}/PROBLEM.md")
    print(f"  2. implement            : problems/{name}/solution.py")
    print(f"  3. add level tests      : problems/{name}/test_solution.py")
    print(f"  4. run                  : python3 run.py {name}        # all levels")
    print(f"                            python3 run.py {name} 1      # level 1 only")
    print(f"                            python3 run.py {name} --ref  # check the reference")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
