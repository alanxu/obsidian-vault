---
tags: [job-hunt, interview-prep, coding-practice, harness]
title: "Local Coding-Practice Harness"
purpose: "Run arbitrary practical/OO coding questions locally in an interview-like, level-by-level loop. Stdlib only (just Python)."
related: ["[[question-bank/practical-coding/README]]", "[[practical-coding-tools-platforms-2026-06-16]]"]
created: 2026-06-19
---

# Local Coding-Practice Harness

Practice **any** practical/OO coding question locally with the **CodeSignal-ICA loop**: write a class, run a test suite **level by level**, unlock the next level when the current passes. **Zero dependencies** — uses Python's built-in `unittest`, so all you need is a Python runtime.

## Setup (macOS) — one time
1. **Check Python (need 3.10+):**
   ```bash
   python3 --version
   ```
2. **If it's missing or too old**, pick one:
   - Xcode Command Line Tools (simplest): `xcode-select --install`
   - Homebrew: `brew install python`
   - Installer: https://www.python.org/downloads/macos/
3. **(Optional) virtual env** — not required since the harness is stdlib-only, but tidy if you'll `pip install` extras later:
   ```bash
   cd "/Users/alanxu/vault/My Vault/02 - Projects/Job Hunt/coding-practice"
   python3 -m venv .venv && source .venv/bin/activate
   ```
   `pytest` is **optional** (the harness also runs under pytest); install with `pip install pytest` if you prefer its output.

## Daily workflow
```bash
cd "/Users/alanxu/vault/My Vault/02 - Projects/Job Hunt/coding-practice"

# 1. start a problem (or use the seeded one, in-memory-db)
python3 new_problem.py banking-system

# 2. implement problems/<name>/solution.py  (in a PLAIN editor — Copilot/autocomplete OFF)

# 3. run the grader, level by level
python3 run.py in-memory-db 1      # just level 1
python3 run.py in-memory-db        # all levels
python3 run.py in-memory-db --ref  # see the reference pass (after you've tried!)
```

## Layout
```
coding-practice/
  run.py            # the runner (python3 run.py <problem> [level] [--ref])
  new_problem.py    # scaffold a new problem from the template
  problems/
    _template/      # copied by new_problem.py
    in-memory-db/   # seeded, fully working example (the canonical ICA problem)
      PROBLEM.md           # the 4-level spec
      solution.py          # YOU fill this in (stub raises NotImplementedError)
      reference_solution.py# worked solution — peek only after you try
      test_solution.py     # unittest: TestLevel1 … TestLevel4
```

## How to practice like the real OA (read this)
- **Bare editor, no AI/autocomplete** — the OA gives you a minimal in-browser editor; turn Copilot off.
- **90-minute timer** for a 4-level problem; aim to *unlock* level 4, not perfect level 1.
- **Run tests continuously** (`run.py <problem> <level>`) — the real ICA grades against hidden tests, so practice reasoning out edge cases yourself before you peek at the reference.
- **Pull problems from real sources** (see [[practical-coding-tools-platforms-2026-06-16]] §C): CodeSignal Practice, LibreSignal, LeetCode Discuss — copy a spec into a `new_problem.py` folder and write your own tests, or use ours.
- Study from the **digest** ([[question-bank/practical-coding/README]]); drill on this harness.

> Note: my (Claude's) sandbox can't reach PyPI, so this harness is deliberately **stdlib-only** and was verified by running `python3 run.py in-memory-db --ref` (all levels green).
