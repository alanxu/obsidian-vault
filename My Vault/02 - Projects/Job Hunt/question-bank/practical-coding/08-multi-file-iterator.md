---
title: Multi-File Iterator (up to 6 progressive parts)
slug: multi-file-iterator
type: multi-level-stateful
leetcode: null
companies: [OpenAI, Anthropic, Stripe-data, Databricks, Snowflake, "data eng roles broadly"]
difficulty: ★★★★☆
frequency: high
formats: [Live, Take-home]
levels: 6
time-box: live 45–60 min
time-box-take-home: 4–6 hours
tags: [oo-design, iterator-protocol, resumable-state, async, generators, n-dimensional]
related: ["[[openai-interview-guide]]", "[[10-api-log-parser-token-aggregator]]"]
---

# Multi-File Iterator ⭐

Iterate lines across many files as one stream — then **resumable**, then **async**, then 2D/3D. Tests the **iterator protocol** and clean state management across up to 6 progressive parts. Pace yourself: the parts are designed to fit in 5–10 minutes each.

## Problem (by part)

1. **Basic** — given a list of file paths, yield lines across all paths in order, **skip empty/missing files**.
2. **Resumable** — `get_state() / set_state(state)` save and restore the iterator's position.
3. **ResumableMultiFileIterator class** — same as Part 2, wrapped in a class.
4. **Async** — `__aiter__ / __anext__`, `aiofiles` for non-blocking I/O.
5. **2D** — files of files (directories → files → lines).
6. **3D** — directories → directories → files → lines.

Spec wording varies: "skip empty" can mean (a) files with no lines, (b) zero-byte files, or (c) files that don't exist. **Clarify at L1.**

## Core approach (format-agnostic)

The control flow is **identical** at every part — just swap blocking I/O for async, or one dimension for two. Get Part 1 right and the rest bolt on.

**Control flow:**
- Hold `file_idx` and an open file handle.
- `_advance()` opens the next non-empty file (catch `OSError`); increments `file_idx`.
- `__next__` reads a line. If empty, call `_advance()` and retry. If no more files, `raise StopIteration`.
- Resumable state = `(file_idx, fh.tell())`. To restore, close current handle, reopen path at `file_idx`, seek to saved position.
- Async = identical control flow + `await` on every I/O.

### Worked Python solution (Parts 1, 2, 4)

```python
import os

class MultiFileIterator:
    def __init__(self, paths, skip_missing=True, skip_empty_content=True):
        self._paths = paths
        self._file_idx = 0
        self._fh = None
        self._skip_missing = skip_missing
        self._skip_empty_content = skip_empty_content
        self._advance()

    def _advance(self):
        if self._fh:
            self._fh.close()
            self._fh = None
        while self._file_idx < len(self._paths):
            path = self._paths[self._file_idx]
            self._file_idx += 1
            try:
                fh = open(path, "r")
            except OSError:
                continue                # skip missing / unreadable
            # "skip empty" — check both zero-byte and zero-content
            if self._skip_empty_content:
                first = fh.readline()
                if first:
                    self._fh = fh
                    self._pending = first
                    return
                fh.close()
                continue                # file exhausted; move on
            else:
                self._fh = fh
                return
        # no more files

    def __iter__(self):
        return self

    def __next__(self):
        if not hasattr(self, "_pending") and self._fh is None:
            raise StopIteration
        if hasattr(self, "_pending"):
            line, self._pending = self._pending, None
            return line.rstrip("\n")
        line = self._fh.readline()
        if line:
            return line.rstrip("\n")
        self._advance()
        if self._fh is None:
            raise StopIteration
        return self.__next__()

    # ---------- Part 2: Resumable ----------
    def get_state(self):
        pos = self._fh.tell() if self._fh else None
        # Adjust for any pending line we haven't returned yet
        if hasattr(self, "_pending") and self._pending is not None:
            # pending line was already consumed from the file; back up by len+newline
            pos = max(0, pos - len(self._pending) - 1)
        return {"file_idx": self._file_idx, "pos": pos}

    def set_state(self, state):
        if self._fh:
            self._fh.close()
        self._file_idx = state["file_idx"]
        # Re-open the file at file_idx - 1 (the file currently being read)
        if 0 < self._file_idx <= len(self._paths):
            self._fh = open(self._paths[self._file_idx - 1], "r")
            if state["pos"]:
                self._fh.seek(state["pos"])
            self._pending = None

# ---------- Part 4: Async ----------
import aiofiles

class AsyncMultiFileIterator:
    def __init__(self, paths):
        self._paths = paths
        self._idx = 0
        self._fh = None
        self._advance()

    async def _advance(self):
        if self._fh:
            await self._fh.close()
            self._fh = None
        while self._idx < len(self._paths):
            try:
                self._fh = await aiofiles.open(self._paths[self._idx], "r")
                self._idx += 1
                return
            except OSError:
                self._idx += 1

    def __aiter__(self):
        return self

    async def __anext__(self):
        while self._fh is not None:
            line = await self._fh.readline()
            if line:
                return line.rstrip("\n")
            await self._advance()
        raise StopAsyncIteration
```

**Complexity.** All parts: O(total lines) work, O(1) state per dimension.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** Part 1 fast (~10 min), then parts added one at a time. Total session 45–60 min.
- **Follow-ups (real, reported):**
  - The parts themselves (resumable → async → 2D → 3D).
  - **Lazy open** — don't open all files up front; only the current one.
  - **Parallel prefetch** — open the next file in a background thread while you read the current one (Part 4 only).
  - **Filtering / transformation** — `Iterator(paths, predicate=...)` only yields matching lines.
  - **Glob / recursive directory traversal** — accept a directory, walk it; respects Part 5/6.
  - **Encoding handling** — `open(path, "r", encoding="utf-8")` + `errors="replace"`.
  - **Cancellation** — `__anext__` checks a `cancel_event` between yields.
  - **Stats** — `lines_yielded`, `files_skipped`, `bytes_read`.
  - **Merge instead of concatenate** — "files are each sorted by timestamp; yield globally sorted" → k-way merge with a heap of (line_key, file_idx); the classic escalation from iterator to merge-iterator (LC 23 in disguise).
  - **Why not just a generator function?** → `yield`-based version is 5 lines but can't do `get_state`/`set_state` (generator state isn't serializable) — the class exists *because* of resumability; saying this unprompted shows you know both forms.
- **Tips:**
  - Implement the iterator protocol **cleanly** so resumable/async bolt on without rewrite.
  - **Clarify "skip empty" semantics** at L1 — three plausible interpretations.
  - Narrate state shape: `(file_idx, fh.tell())` is enough; don't add fluff.
  - For Part 4: identical control flow, just `await`. **Don't restructure.**
- **Pitfalls:**
  - **Opening all files eagerly** — memory blowup for thousands of files.
  - **Losing position across save/restore** — pending line handling is the subtle bit.
  - **Last line without newline** — `readline()` returns `""` then, not a line.
  - **File changed between save/restore** — declare as undefined behavior in code.
  - Forgetting `__aiter__` returns `self`; forgetting `raise StopAsyncIteration` (not `StopIteration`).

### Take-home / work-trial
- **Tips:**
  - Ship Parts 1–3 with a `pytest` suite covering missing files, empty files, last-line-no-newline, save/restore roundtrip.
  - Note the async/nD extensions in the README.
  - For Part 5/6: a small `walk_2d(root)` / `walk_3d(root)` helper that flattens to a path list — same iterator works.
- **Pitfalls:**
  - No tests for the resume path.
  - Not handling missing files gracefully (crash instead of skip).
  - Off-by-one in `file_idx` (the file currently open vs the next to open).

## Company variants

- **OpenAI (canonical)** — "Problem 2" in their bank; full 6-part version.
- **Anthropic / Stripe-data / Databricks / Snowflake** — common in data-eng tracks; usually Parts 1–3.
- **Data-eng roles broadly** — log aggregation, ETL pipelines; same structure.

## Worked example trace

```
paths = ["a.txt", "missing.txt", "empty.txt", "b.txt"]
a.txt:       "line 1\nline 2\n"
empty.txt:   ""
b.txt:       "line 3\n"

Iterate:
  next() → "line 1"
  next() → "line 2"
  _advance(): "missing.txt" → OSError → skip; "empty.txt" → readline "" → skip; "b.txt" → open
  next() → "line 3"
  next() → StopIteration

state after 2 yields: file_idx=1 (just finished a.txt), pos = len(a.txt content)
restore to that state: reopen a.txt, seek to pos, resume from "line 2"
```

## Related
[[10-api-log-parser-token-aggregator]] (streaming) · [[08-multi-file-iterator]] · [[openai-interview-guide]] P2.