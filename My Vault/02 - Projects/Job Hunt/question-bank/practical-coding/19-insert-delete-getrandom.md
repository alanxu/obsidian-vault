---
title: Insert Delete GetRandom O(1)
slug: insert-delete-getrandom
type: leetcode-design
leetcode: 380
companies: [Google, Amazon, Meta, Uber, LinkedIn, Twitter, "any system that needs uniform sampling"]
difficulty: ★★★☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 20–30 min
tags: [array, hashmap, swap-remove, randomization]
related: ["[[17-lru-cache]]"]
---

# Insert Delete GetRandom O(1) (#380)

The "array + index map with swap-to-end removal" trick — a frequently reused primitive. Once you see it, the same pattern shows up in many other problems.

## Problem

`RandomizedSet`:
- `insert(val) -> bool` — O(1) avg; returns false if already present.
- `remove(val) -> bool` — O(1) avg; returns false if missing.
- `getRandom() -> int` — O(1) avg; uniform random element from the set.

## Core approach (format-agnostic)

**A list of values + dict `val → index`.** Remove by swapping target with last, fixing the moved element's index, popping. Random by `random.choice(list)`.

The list gives O(1) random (contiguous array); the dict gives O(1) lookup. Together, O(1) for all three.

### Worked Python solution

```python
import random

class RandomizedSet:
    def __init__(self):
        self.vals = []
        self.idx = {}                 # value -> index in vals

    def insert(self, val: int) -> bool:
        if val in self.idx:
            return False
        self.idx[val] = len(self.vals)
        self.vals.append(val)
        return True

    def remove(self, val: int) -> bool:
        if val not in self.idx:
            return False
        i = self.idx[val]
        last = self.vals[-1]
        if i != len(self.vals) - 1:
            # swap
            self.vals[i] = last
            self.idx[last] = i
        self.vals.pop()
        del self.idx[val]
        return True

    def getRandom(self) -> int:
        return random.choice(self.vals)
```

**#381 variant** (allow duplicates) uses `val → set of indices`:
```python
class RandomizedCollection:
    def __init__(self):
        self.vals = []
        self.idx = {}                 # val -> set of indices

    def insert(self, val):
        self.idx.setdefault(val, set()).add(len(self.vals))
        self.vals.append(val)
        return len(self.idx[val]) == 1

    def remove(self, val):
        if val not in self.idx or not self.idx[val]:
            return False
        i = self.idx[val].pop()       # any index of val
        last = self.vals[-1]
        if i != len(self.vals) - 1:
            self.vals[i] = last
            self.idx[last].add(i)
            self.idx[last].discard(len(self.vals) - 1)
        self.vals.pop()
        return True

    def getRandom(self):
        return random.choice(self.vals)
```

**Complexity.** O(1) average per op. The swap-remove is O(1) but breaks order — getRandom doesn't need order, so it's fine.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:**
  - The swap-remove is the trick; remove returns false if missing.
  - Don't `random.choice` on an empty list (raise).
- **Pitfalls:**
  - Forgetting to update the moved element's index.
  - Removing the last element (swap with itself is OK, but skip if `i == len-1`).
  - `random.choice` on empty set — `IndexError`.
  - Returning `None` instead of raising on empty.

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **#381 duplicates** (`val → set of indices`) — variant above.
  - **Weighted random** — `weight_map`, sample via prefix-sum + binary search, or alias method.
  - **Thread safety** — `threading.Lock`.
  - **getRandom with removal** — pop a uniform random element (`pop(random index)`).
  - **getRandom without mutation** — observe-only.
  - **Snapshot** — serialize state for persistence.
  - **Range sample** — `getRandomRange(k)` — sample k distinct elements; reservoir sampling.
  - **Concurrent set** — multiple writers, eventual consistency.
- **Tips:**
  - **Narrate why list + map** gives O(1) random (contiguous array) vs a set (no O(1) random).
  - For weighted: accept `weight` on insert; prefix-sum on query.
  - For thread safety: `Lock` around all three ops.
  - For #381: `set of indices` per value; pop an arbitrary index on remove.
- **Pitfalls:**
  - #381 set-of-indices bookkeeping on swap — must update both `idx[last].add(i)` and `idx[last].discard(len-1)`.
  - Weighted random without normalization.
  - Returning the same element twice in `getRandomRange`.

### Onsite · NR (Google-style)
- **Tips:** Walk through insert(1), insert(2), remove(1) on a whiteboard.
- **Pitfalls:** Forgetting the `last` swap when `i != len-1`.

## Company variants

- **Google / Amazon / Meta / Uber / LinkedIn / Twitter** — common warm-up; appears in many banks.
- **Sampling systems** — uniform reservoir, weighted reservoir.

## Worked example trace

```
insert(1): vals=[1], idx={1:0}
insert(2): vals=[1,2], idx={1:0, 2:1}
remove(1): i=0, last=2, swap → vals=[2], idx={2:0}
getRandom(): random.choice([2]) → 2
```

## Related
#381 (duplicates variant) · [[17-lru-cache]] (similar O(1) tricks).