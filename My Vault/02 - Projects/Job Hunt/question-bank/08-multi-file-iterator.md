---
title: Multi-File Iterator (up to 6 progressive parts)
slug: multi-file-iterator
type: multi-level-stateful
leetcode: null
companies: [OpenAI]
difficulty: ★★★★☆
frequency: high
formats: [Live, Take-home]
levels: 6
time-box: live 45–60 min
tags: [oo-design, iterator-protocol, resumable-state, async, generators]
related: ["[[openai-interview-guide]]"]
---

# Multi-File Iterator ⭐

Iterate lines across many files as one stream — then **resumable**, then **async**, then 2D/3D. Tests the iterator protocol and clean state management across up to 6 parts.

## Problem (by part)
1. Yield lines across all paths in order, **skip empty/missing files**.
2. **Resumable:** `get_state()/set_state()`.
3. `ResumableMultiFileIterator` class. 4. **Async** (`__aiter__/__anext__`, `aiofiles`). 5. **2D** (files of files). 6. **3D**.

## Core approach (format-agnostic)
Hold `file_idx` + an open handle; `_advance()` opens the next non-empty file (skip `OSError`). `__next__`: read a line; if empty, `_advance()`; `StopIteration` when exhausted. Resumable state = `(file_idx, fh.tell())`. Async = identical control flow + `await`. Code (parts 1/2/4): [[openai-interview-guide]] Problem 2.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** part 1 fast, then parts added one at a time; pace yourself.
- **Follow-ups:** the parts themselves (resumable → async → nD); lazy open (don't open all files up front), parallel prefetch.
- **Tips:** implement the iterator protocol cleanly so resumable/async bolt on; clarify "skip empty" semantics.
- **Pitfalls:** opening all files eagerly (memory), losing position across save/restore, last line without newline, file changed between save/restore (declare undefined).

### Take-home / work-trial
- **Tips:** ship parts 1–3 with tests; note the async/nD extensions in the README.
- **Pitfalls:** no tests for the resume path; not handling missing files gracefully.

## Related
[[10-api-log-parser-token-aggregator]] (streaming) · [[openai-interview-guide]] P2.
