---
title: Range Module
slug: range-module
type: leetcode-design
leetcode: 715
companies: [Google, Booking.com, Atlassian, "calendar / interval systems", "DB query planners"]
difficulty: ★★★★☆
frequency: low
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 35–45 min
tags: [intervals, binary-search, merge, sortedcontainers]
related: ["[[28-memory-allocator]]"]
---

# Range Module (#715)

Track a set of **half-open intervals** with add/query/remove — the hardest design warm-up. Combines interval merging with binary search; the implementation is fiddly but the structure is clean.

## Problem

- `addRange(left, right)` — add `[left, right)` to the set; merge with overlapping/adjacent intervals.
- `queryRange(left, right) -> bool` — true iff **all** of `[left, right)` is tracked.
- `removeRange(left, right)` — remove `[left, right)` from the set; split any interval that straddles it.

## Core approach (format-agnostic)

A **sorted, non-overlapping interval list** (or `SortedList` of endpoints). For each op:

- **Add:** find the span of intervals that overlap or touch `[left, right)`; replace with a single merged interval `[min_left, max_right)`.
- **Query:** find the interval covering `left`; check it spans `right`.
- **Remove:** find the span that overlaps `[left, right)`; for each, trim (keep the `[orig_left, left)` part if it exists, keep the `[right, orig_right)` part if it exists).

### Worked Python solution

```python
from sortedcontainers import SortedList

class RangeModule:
    def __init__(self):
        # list of [start, end) intervals, sorted, non-overlapping
        self.intervals = SortedList()

    def addRange(self, left: int, right: int) -> None:
        # Find all intervals that overlap or touch [left, right)
        i = self.intervals.bisect_left([left, left])
        j = self.intervals.bisect_right([right, right])
        # Check left neighbor (might be touching)
        if i > 0 and self.intervals[i - 1][1] >= left:
            i -= 1
        # Merge into [min_left, max_right)
        new_left, new_right = left, right
        for k in range(i, j):
            new_left = min(new_left, self.intervals[k][0])
            new_right = max(new_right, self.intervals[k][1])
        for k in range(j - 1, i - 1, -1):
            self.intervals.pop(k)
        self.intervals.add([new_left, new_right])

    def queryRange(self, left: int, right: int) -> bool:
        # Find the interval whose start is <= left
        i = self.intervals.bisect_right([left, float("-inf")]) - 1
        if i < 0:
            return False
        start, end = self.intervals[i]
        return start <= left and end >= right

    def removeRange(self, left: int, right: int) -> None:
        i = self.intervals.bisect_left([left, left])
        j = self.intervals.bisect_right([right, right])
        if i > 0 and self.intervals[i - 1][1] > left:
            i -= 1
        # Splits: keep left piece and right piece of straddling intervals
        new_intervals = []
        for k in range(i, j):
            start, end = self.intervals[k]
            if start < left:
                new_intervals.append([start, left])
            if end > right:
                new_intervals.append([right, end])
        for k in range(j - 1, i - 1, -1):
            self.intervals.pop(k)
        for iv in new_intervals:
            self.intervals.add(iv)
```

**Complexity.** `add` / `remove` / `query`: O(log n + k) per op, where k is intervals affected.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:**
  - `SortedList` / `bisect` on endpoints; be meticulous on half-open boundaries.
  - Test adjacency: `[1,2) + [2,3) → [1,3)`.
  - Test exact-boundary query: `query(2, 5)` when only `[1, 3)` is added → false.
  - Test removing a middle slice: `[1,10) - [4,6) → [1,4) + [6,10)`.
- **Pitfalls:**
  - **Adjacency merge** (`[1,2) + [2,3)` should merge to `[1,3)`).
  - **Exact-boundary query** — half-open means `[1,3)` covers 1 and 2, not 3.
  - **Removing a middle slice** splits one interval into two.
  - **Empty result** — after remove, list may be empty.
  - **Removing beyond the range** — `[1,5) - [0,10)` → empty.

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **Count covered length** — sum of interval lengths.
  - **K-th covered point** — find the K-th integer in any interval.
  - **Segment tree** for dynamic queries — efficient range add/remove/query.
  - **Persistence** — immutable intervals with versioning.
  - **Concurrency** — locks per interval or R-tree.
  - **Multi-dimensional** — rectangles instead of intervals.
  - **Lazy propagation** — for segment tree.
  - **Streaming** — process intervals as they arrive.
- **Tips:**
  - **Draw the intervals**; narrate the merge-on-add and split-on-remove cases explicitly.
  - For multi-dimensional: interval tree or R-tree.
  - For lazy segment tree: defer updates to query time.
  - For persistence: copy-on-write intervals.
- **Pitfalls:**
  - **The split case** (one interval → two) — easy to miss the right piece.
  - **Off-by-one on half-open** — `[1,3)` doesn't include 3.
  - **Forgetting adjacency** — `[1,2)` and `[2,3)` should merge.
  - **Modifying during iteration** — collect first, then apply.

### Onsite · NR (Google-style)
- **Tips:** Draw intervals and trace `add(1,5) → add(3,8) → query(2,4) → remove(4,6)`.
- **Pitfalls:** Forgetting the right half of a split.

## Company variants

- **Google / Booking.com / Atlassian** — calendar/scheduling reskin.
- **DB query planners** — same patterns at larger scale.

## Worked example trace

```
add(1, 5)        # intervals: [(1, 5)]
add(3, 8)        # merge → intervals: [(1, 8)]
add(10, 12)      # intervals: [(1, 8), (10, 12)]
query(2, 4)      # True (covered by [1, 8))
query(8, 10)     # False (8 not covered, 10 starts a new interval)
remove(4, 6)     # splits [1,8) → [(1,4), (6,8)]
                 # intervals: [(1, 4), (6, 8), (10, 12)]
query(2, 5)      # False (4 to 5 not covered)
query(5, 6)      # False
query(5, 7)      # True (covered by [6, 8))
```

## Related
[[28-memory-allocator]] · Track A intervals (#56/#57/#715).