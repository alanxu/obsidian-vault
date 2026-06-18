---
title: Insert Delete GetRandom O(1)
slug: insert-delete-getrandom
type: leetcode-design
leetcode: 380
companies: [General]
difficulty: ★★★☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 20–30 min
tags: [array, hashmap, swap-remove, randomization]
related: []
---

# Insert Delete GetRandom O(1) (#380)

The "array + index map with swap-to-end removal" trick — a frequently reused primitive.

## Problem
`insert(val)`, `remove(val)`, `getRandom()` all average **O(1)**; `getRandom` uniform.

## Core approach (format-agnostic)
A **list** of values + dict `val→index`. Remove: **swap target with last**, fix the moved element's index, pop. getRandom: `random.choice(list)`.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** the swap-remove is the trick; remove returns false if missing.
- **Pitfalls:** forgetting to update the moved element's index, removing the last element (swap with itself), random over empty.

### Live · CoderPad (human)
- **Follow-ups:** **#381 duplicates** (`val → set of indices`), weighted random, thread safety.
- **Tips:** narrate why list+map gives O(1) random (contiguous array) vs a set (no O(1) random).
- **Pitfalls:** the #381 set-of-indices bookkeeping on swap.

## Related
#381 (duplicates variant).
