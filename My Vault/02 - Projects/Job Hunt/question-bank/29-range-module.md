---
title: Range Module
slug: range-module
type: leetcode-design
leetcode: 715
companies: [General]
difficulty: ★★★★☆
frequency: low
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 35–45 min
tags: [intervals, binary-search, merge]
related: ["[[28-memory-allocator]]"]
---

# Range Module (#715)

Track a set of half-open intervals with add/query/remove — the hardest design warm-up (interval merging + binary search).

## Problem
`addRange(left, right)`; `queryRange(left, right)` → true iff **all** of `[left,right)` tracked; `removeRange(left, right)`.

## Core approach (format-agnostic)
A **sorted, non-overlapping interval list** (or `SortedList` of endpoints). Add: binary-search span, **merge** overlapping/adjacent. Remove: **split** straddling intervals. Query: find the interval covering `left`, check it spans `right`. O(log n + k)/op.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** `SortedList`/`bisect` on endpoints; be meticulous on half-open boundaries.
- **Pitfalls:** adjacency merge (`[1,2)+[2,3)`), exact-boundary query, removing a middle slice (splits into two).

### Live · CoderPad (human)
- **Follow-ups:** count covered length, k-th covered point, **segment tree** for dynamic queries, persistence.
- **Tips:** draw the intervals; narrate the merge-on-add and split-on-remove cases explicitly.
- **Pitfalls:** the split case (one interval → two), off-by-one on half-open, forgetting adjacency.

## Related
[[28-memory-allocator]] · Track A intervals (#56/#57/#715).
