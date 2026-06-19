---
tags: [job-hunt, interview-prep, question-bank, index]
title: "Question Bank (canonical)"
scope: "Canonical home for all coding/system-design question banks. One folder per area; each area has its own README and files."
location: "Top-level under `/question-bank/` (parent of all area sub-folders)."
related: ["[[interview-prep-master-plan-2026]]", "[[openai-interview-guide]]", "[[anthropic-interview-guide]]", "[[cohere-interview-guide]]"]
created: 2026-06-16
updated: 2026-06-18 (restructured into area sub-folders)
---

# Question Bank (canonical)

**One canonical home** for all coding + system-design question banks, organized by area. Each area is its own folder with a README that defines scope, formats, and how to use it.

> **Why an umbrella:** problems that show up in interview loops are easier to find when grouped by **interview topic** rather than by the **track** in the master plan. A problem's track is which skill it tests; its area folder is where you look it up.

## Areas

| Folder | Scope | Star problems to drill first |
|---|---|---|
| [[practical-coding/README]] | Practical / OO coding — build a stateful component across 3–6 escalating levels. Multi-level ICA + Anthropic live bank + LeetCode Design warm-ups + agentic primitives. (34 files.) | [[practical-coding/01-in-memory-key-value-database]], [[practical-coding/17-lru-cache]], [[practical-coding/12-multithreaded-web-crawler]], [[practical-coding/16-minimal-agent-loop]] |
| [[algorithmic-coding/README]] | Algorithmic / DSA — NeetCode 150 weighted to graphs / intervals / geospatial (AV+mobility) + concurrency. | (TBD — drill list in area README) |
| [[distributed-system-design/README]] | Distributed system design — rate limiters, KV caches, ride dispatch, metrics, payment ledgers, log ingestion, feed, job schedulers. | (TBD — drill list in area README) |
| [[llm-system-design/README]] | LLM / ML system design — RAG, inference serving, agents, training, eval, safety, real-time ML. **31 question cards across the 8 areas** + framework ([[D0-areas-map]]) + worked RAG ([[D1-rag-with-citations]]). | [[llm-system-design/06-llm-inference-serving-platform]], [[llm-system-design/09-agent-platform]], [[llm-system-design/13-distributed-training-70b]], [[llm-system-design/01-rag-with-citations]] |

## How to use

1. **For your target company**, identify which areas dominate (see per-company guides in `plans/`).
2. Drill the **star problems** in each area's README.
3. Re-implement from a blank file, **timed, in a bare web editor** — see [[practical-oo-coding-deep-guide]] §6.5.
4. For the practical-coding bank, read the "By format" section for the format your target company uses (see each file's `companies`/`formats` frontmatter), and rehearse those follow-ups.

## Boundary with `track-*` folders

The legacy `track-A-…-G/` folders still exist as **track-style** views (one folder per interview skill area in the master plan). The `question-bank/` folders are **area-style** views (one folder per coding/system-design topic). They overlap by intent but not by content — the canonical question files now live under `question-bank/`; the `track-*` folders hold guides + deep dives (e.g., [[track-B-practical-oo-coding/practical-oo-coding-deep-guide]]).

*Merged & relocated 2026-06-16. Restructured into area sub-folders 2026-06-18.*