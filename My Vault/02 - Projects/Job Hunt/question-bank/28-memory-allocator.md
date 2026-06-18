---
title: Design Memory Allocator
slug: memory-allocator
type: leetcode-design
leetcode: 2502
companies: [NVIDIA-adjacent, general]
difficulty: ★★★★☆
frequency: low
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 30–40 min
tags: [arrays, allocation, free-list, intervals]
related: ["[[29-range-module]]"]
---

# Design Memory Allocator (#2502)

Allocate/free contiguous blocks in a fixed array — a low-level design with a free-list/interval flavor (relevant to systems/GPU teams).

## Problem
`Allocator(n)`; `allocate(size, mID)` → first index of a free run of `size` (or −1); `free(mID)` → units freed.

## Core approach (format-agnostic)
Simple: `int[] units` (0=free), scan for first run of `size` zeros (O(n)/allocate). Senior: **sorted free-interval list / size-bucketed free list** (first-fit/best-fit) with coalescing on free.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** the array-scan version passes the base; correctness over speed.
- **Pitfalls:** no run large enough (−1), free of unknown mID (0), allocate size 0, full array.

### Live · CoderPad (human)
- **Follow-ups:** best-fit vs first-fit vs **buddy allocator**, coalescing, defragmentation/compaction, alignment, concurrency.
- **Tips:** start with the array, then offer the free-list/interval upgrade and **coalescing** on free; resonates with NVIDIA/systems.
- **Pitfalls:** fragmentation, not coalescing adjacent frees, O(n) scans when a free-list was expected.

## Related
[[29-range-module]] (interval merging).
