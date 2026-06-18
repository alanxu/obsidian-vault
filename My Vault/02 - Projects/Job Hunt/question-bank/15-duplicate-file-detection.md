---
title: Find / Eliminate Duplicate Files
slug: duplicate-file-detection
type: live-coding
leetcode: 609
companies: [Anthropic]
difficulty: ★★★☆☆
frequency: high
formats: [Live, Take-home]
levels: 2
time-box: live 45 min
tags: [hashing, io-minimization, chunked-reads, system]
related: ["[[anthropic-interview-guide]]", "[[04-cloud-storage-file-host]]"]
---

# Find / Eliminate Duplicate Files

LeetCode **#609** taken to a systems level by Anthropic: minimize I/O, handle huge files, dedupe by content.

## Problem
Scan a directory tree; group files with **identical content**; optional hard-link replacement. Code: [[anthropic-interview-guide]] worked solution (c).

## Core approach (format-agnostic) — the three-stage funnel
1. **Group by size** (unique size ⇒ skip). 2. Hash a **small head+tail signature** to split groups cheaply. 3. Only for collisions, **full SHA-256** (optionally byte-compare). Stream files in chunks — never load whole.

## By format

### Live · CoderPad (human) — *primary (Anthropic)*
- **How it appears:** naive "hash everything" first, then "make it efficient for 1M files / 10GB files."
- **Follow-ups:** chunk size (align to FS block, 64KB–1MB); SHA-256 vs MD5; **I/O-bound → parallelize reads/async, CPU-bound → multiprocess**; cross-machine dedup (content-addressed storage, distribute by hash prefix); **incremental** (reverse index keyed by (size, sig, full hash) + buckets ≥2 → O(1) query).
- **Tips:** lead with the funnel and **why** (avoid hashing unique-size files); handle `OSError`.
- **Pitfalls:** loading whole files, hashing everything (no size pre-filter), ignoring permission errors / vanished files, collision handling.

### Take-home / work-trial
- **Tips:** ship the funnel + chunked reads + a hard-link mode behind a flag + tests; README the I/O-vs-CPU analysis.
- **Pitfalls:** no streaming (OOM on big files), no error handling, no tests for the collision path.

## Related
[[04-cloud-storage-file-host]] (dedupe follow-up) · [[anthropic-interview-guide]] (c).
