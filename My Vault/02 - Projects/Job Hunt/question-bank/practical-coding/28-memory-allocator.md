---
title: Design Memory Allocator
slug: memory-allocator
type: leetcode-design
leetcode: 2502
companies: [NVIDIA, Intel, VMware, "any systems / GPU / kernel team", "DB buffer pool teams"]
difficulty: ★★★★☆
frequency: low
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 30–40 min
tags: [arrays, allocation, free-list, intervals, fragmentation]
related: ["[[29-range-module]]"]
---

# Design Memory Allocator (#2502)

Allocate/free contiguous blocks in a fixed array — a low-level design with a free-list / interval flavor. Relevant to systems, GPU, and database buffer-pool teams.

## Problem

`Allocator(n)`:
- `allocate(size, mID) -> int` — first index of a free run of `size` consecutive units, or `-1` if none.
- `free(mID) -> int` — free all units owned by `mID`; return count freed.

## Core approach (format-agnostic)

**Approach A — Array scan (simple, slow at scale):**
- `int[] units` (0 = free, mID = owner).
- `allocate`: scan for first run of `size` zeros. O(n) per call.
- `free`: walk and zero out units owned by mID. O(n) per call.

**Approach B — Sorted free-interval list / size-bucketed free list (senior):**
- Maintain a list of free intervals `[start, end)`; first-fit or best-fit.
- `allocate(size)`: pop the first interval large enough; split if there's a remainder.
- `free`: append the freed interval; coalesce with adjacent neighbors.

### Worked Python solutions

**Array scan:**
```python
class Allocator:
    def __init__(self, n: int):
        self.units = [0] * n

    def allocate(self, size: int, mID: int) -> int:
        n = len(self.units)
        i = run = 0
        while i < n:
            if self.units[i] == 0:
                run += 1
                if run == size:
                    start = i - size + 1
                    for j in range(start, start + size):
                        self.units[j] = mID
                    return start
            else:
                run = 0
            i += 1
        return -1

    def free(self, mID: int) -> int:
        count = 0
        for i in range(len(self.units)):
            if self.units[i] == mID:
                self.units[i] = 0
                count += 1
        return count
```

**Sorted interval list (best-fit):**
```python
from sortedcontainers import SortedList

class Allocator:
    def __init__(self, n: int):
        self.n = n
        # free intervals: (start, length)
        self.free_intervals = SortedList([(0, n)])
        # owner -> list of intervals (for fast free)
        self.by_owner = {}                  # mID -> [(start, length)]

    def allocate(self, size: int, mID: int) -> int:
        # best-fit: smallest interval that fits
        idx = self.free_intervals.bisect_left((size, -1))  # lower bound trick
        # search a window for an interval that fits
        for i in range(len(self.free_intervals)):
            start, length = self.free_intervals[i]
            if length >= size:
                # pop and split
                self.free_intervals.pop(i)
                if length > size:
                    self.free_intervals.add((start + size, length - size))
                self.by_owner.setdefault(mID, []).append((start, size))
                return start
        return -1

    def free(self, mID: int) -> int:
        if mID not in self.by_owner:
            return 0
        total = 0
        for start, length in self.by_owner.pop(mID):
            self._add_interval(start, length)
            total += length
        return total

    def _add_interval(self, start, length):
        """Add and coalesce with neighbors."""
        end = start + length
        # Try to merge with predecessor
        idx = self.free_intervals.bisect_left((start, -1))
        # Coalesce: check left and right neighbors
        merged_start, merged_end = start, end
        # (left merge)
        if idx > 0:
            ps, pl = self.free_intervals[idx - 1]
            if ps + pl == start:
                merged_start = ps
                self.free_intervals.pop(idx - 1)
                idx -= 1
        # (right merge)
        if idx < len(self.free_intervals):
            rs, rl = self.free_intervals[idx]
            if merged_end == rs:
                merged_end = rs + rl
                self.free_intervals.pop(idx)
        self.free_intervals.add((merged_start, merged_end - merged_start))
```

**Complexity.** Array scan: O(n) per call. Interval list: O(log F) per call (F = number of free intervals).

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:**
  - The array-scan version passes the base; correctness over speed.
  - Test edge cases: empty allocator, full allocator, double-free.
- **Pitfalls:**
  - No run large enough (-1).
  - Free of unknown mID (return 0).
  - Allocate size 0 (returns 0 or -1; spec varies).
  - Full array.
  - Free followed by allocate — must reuse freed space.

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **Best-fit vs first-fit vs buddy allocator** — trade-off: best-fit minimizes wasted space but slower; buddy allocator is fast and limits external fragmentation.
  - **Coalescing** — when freeing, merge with adjacent free intervals.
  - **Defragmentation / compaction** — move allocations to consolidate free space.
  - **Alignment** — round up to multiples of N (e.g., 8-byte alignment).
  - **Concurrency** — locks per region; thread-local caches.
  - **Slab allocator** — caches of fixed-size objects.
  - **Pool allocator** — separate pools per size class.
  - **Garbage collection** — mark-and-sweep, refcount.
  - **NUMA-aware** — pin allocations to memory locality.
  - **Huge pages** — large contiguous blocks for databases/ML.
  - **GPU/KV-cache framing (AI shops)** — PagedAttention is exactly this problem: fixed-size pages kill *external* fragmentation at the cost of *internal* (last page half-used) — if interviewing at an inference shop, connect allocator → paged KV cache unprompted ([[../llm-system-design/06-llm-inference-serving-platform]]).
  - **Internal vs external fragmentation** — define both (waste inside a block vs unusable holes between) and which each strategy trades: buddy = internal, first-fit = external, pages = internal-bounded; interviewers reward the precise vocabulary.
- **Tips:**
  - **Start with the array**, then offer the free-list/interval upgrade and **coalescing** on free.
  - Mention the alignment requirement (often 8 or 16 bytes).
  - For buddy allocator: round sizes up to powers of 2; free blocks split/merge along binary tree.
  - For thread safety: per-thread caches that periodically refill from a shared pool.
- **Pitfalls:**
  - **Fragmentation** — many small holes that can't serve a large request.
  - **Not coalescing adjacent frees** — leads to many tiny intervals.
  - **O(n) scans when a free-list was expected** — slow at scale.
  - **Ignoring alignment** — pointer arithmetic breaks.
  - **Off-by-one in intervals** — half-open `[start, end)` is the convention.

### Onsite · NR (Google-style)
- **Tips:** Draw the free-interval list and trace `allocate(3) → allocate(2) → free(mID1) → allocate(2)`.
- **Pitfalls:** Not coalescing.

## Company variants

- **NVIDIA / Intel / VMware / systems teams** — production-flavored.
- **DB buffer pool teams** — same shape.

## Worked example trace

```
Allocator(10)
allocate(3, mID=1)   # → 0 (units 0,1,2 = 1)
allocate(2, mID=2)   # → 3 (units 3,4 = 2)
free(mID=1)          # → 3; units 0,1,2 freed; coalesce → interval [0, 3)
allocate(2, mID=3)   # → 0
```

## Related
[[29-range-module]] (interval merging) · Track A intervals.