---
title: LFU Cache
slug: lfu-cache
type: leetcode-design
leetcode: 460
companies: [Google, Amazon, Anthropic, OpenAI, "systems/DB teams"]
difficulty: ★★★★☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 30–40 min
tags: [hashmap, frequency-buckets, eviction, doubly-linked-list]
related: ["[[17-lru-cache]]"]
---

# LFU Cache (#460)

Harder sibling of LRU — evict **least-frequently used**, tie-break by least-recently used. The whole problem lives in the **`min_freq` bookkeeping**.

## Problem

`LFUCache(capacity)`:
- `get(key) -> int` — O(1); returns value or -1; bumps frequency.
- `put(key, value)` — O(1); inserts or updates; if at capacity, evict the lowest-frequency key, tie-broken by oldest access within that frequency.

## Core approach (format-agnostic)

**Three structures:**
- `key_to_val: dict[key → value]`
- `key_to_freq: dict[key → int]`
- `freq_to_keys: dict[freq → OrderedDict[key → None]]` — LRU within a freq bucket.
- `min_freq: int` — current minimum frequency across all keys.

On access (`get` or `put` updating):
- Move key from `freq_to_keys[freq]` to `freq_to_keys[freq+1]`.
- If old bucket was `min_freq` and is now empty → `min_freq += 1`.
- Update `key_to_freq`.

On eviction:
- Pop the oldest from `freq_to_keys[min_freq]`.

On insert:
- `min_freq = 1` (new keys start at freq 1).

### Worked Python solution

```python
from collections import OrderedDict, defaultdict

class LFUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.key_to_val = {}
        self.key_to_freq = {}
        self.freq_to_keys = defaultdict(OrderedDict)
        self.min_freq = 0

    def _bump(self, key):
        f = self.key_to_freq[key]
        self.freq_to_keys[f].pop(key)
        if not self.freq_to_keys[f] and f == self.min_freq:
            self.min_freq += 1
        self.key_to_freq[key] = f + 1
        self.freq_to_keys[f + 1][key] = None

    def get(self, key: int) -> int:
        if key not in self.key_to_val:
            return -1
        self._bump(key)
        return self.key_to_val[key]

    def put(self, key: int, value: int) -> None:
        if self.cap == 0:
            return
        if key in self.key_to_val:
            self.key_to_val[key] = value
            self._bump(key)
            return
        if len(self.key_to_val) >= self.cap:
            # Evict LRU within min_freq bucket
            evict_key, _ = self.freq_to_keys[self.min_freq].popitem(last=False)
            del self.key_to_val[evict_key]
            del self.key_to_freq[evict_key]
        self.key_to_val[key] = value
        self.key_to_freq[key] = 1
        self.freq_to_keys[1][key] = None
        self.min_freq = 1
```

**Complexity.** O(1) per op; O(capacity) memory.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:**
  - The `min_freq` bookkeeping is the whole problem — get the empty-bucket update right.
  - Use `OrderedDict` for `freq_to_keys` to get LRU-within-freq for free.
- **Pitfalls:**
  - Wrong `min_freq` after eviction (forgetting to bump when bucket empties).
  - Tie-break wrong (must be LRU within the min-freq bucket, not arbitrary).
  - Capacity 0 — `put` becomes no-op; `get` returns -1.
  - Forgetting to reset `min_freq = 1` on every new insert.

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **Decay frequencies over time** — multiply by 0.99 every minute; approximation.
  - **Approximate LFU** — sampling-based for higher throughput.
  - **Combine with TTL** — frequency decays to 0 after expiry.
  - **Persistent / distributed** — Redis-style cluster with sharded freq tables.
  - **Window-LFU** — keep last N accesses only; bounded memory.
  - **Per-key cost** — some keys are more expensive to recompute; weight by cost.
  - **Why do real systems rarely use exact LFU?** → new items enter at freq 1 and are instantly evicted before proving themselves (no admission grace), and history never ages without decay → production uses TinyLFU (frequency sketch + admission filter, e.g. Caffeine) or LRU variants; naming this shows systems taste beyond the puzzle.
- **Tips:**
  - **Narrate the freq-bucket structure** before coding.
  - **Reset `min_freq = 1` on every new insert** — common slip.
  - For decay: a background thread, or recompute on each access.
  - Discuss when LFU is better than LRU (e.g., skewed access patterns, like a few hot keys).
- **Pitfalls:**
  - Forgetting to bump freq on `get`.
  - O(n) scans for the min bucket (track it with `min_freq`).
  - Re-inserting a key after eviction — fresh freq 1, not preserved.
  - Edge case: `freq_to_keys` defaultdict returns empty `OrderedDict` for missing keys; check `not bucket` not `bucket is None`.

### Onsite · NR (Google-style)
- **Tips:** Draw the three maps; trace a 3-cap cache with 5 ops.
- **Pitfalls:** Off-by-one when `min_freq` bucket empties.

## Company variants

- **Google / Amazon / Anthropic / OpenAI** — classic systems design question.
- **DB teams** — buffer pool management is LFU-flavored.

## Worked example trace

```
LFUCache(2)
put(1, 1)        # freq: {1:1}, min=1
put(2, 2)        # freq: {1:1, 2:1}, min=1
get(1)           # freq: {1:2, 2:1}, min=1
put(3, 3)        # evict: lowest freq = 1, oldest in that bucket = key 2
                 # freq: {1:2, 3:1}, min=1
get(3)           # freq: {1:2, 3:2}; bucket-1 empties → min=2
put(4, 4)        # evict from min_freq=2 bucket: oldest there = key 1 (bumped before 3)
                 # freq: {3:2, 4:1}, min=1 (new insert resets)
```

## Related
[[17-lru-cache]] (do first; LFU is LRU with frequency bookkeeping).