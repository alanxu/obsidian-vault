---
title: LFU Cache
slug: lfu-cache
type: leetcode-design
leetcode: 460
companies: [General design round]
difficulty: ★★★★☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 30–40 min
tags: [hashmap, frequency-buckets, eviction]
related: ["[[17-lru-cache]]"]
---

# LFU Cache (#460)

Harder sibling of LRU — evict **least-frequently used**, tie-break by least-recently used.

## Problem
`LFUCache(capacity)`: O(1) `get`/`put`; at capacity evict lowest-frequency, tie-broken by oldest.

## Core approach (format-agnostic)
Three maps: `key→(value,freq)`, `key→node`, **`freq→OrderedDict of keys`** (LRU within a freq). Track `min_freq`. On access move key `freq → freq+1`; if old bucket was `min_freq` and now empty, `min_freq += 1`. Evict from `min_freq` bucket's oldest.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** the `min_freq` bookkeeping is the whole problem — get the empty-bucket update right.
- **Pitfalls:** wrong `min_freq` after eviction, tie-break (must be LRU within the min-freq bucket), capacity 0.

### Live · CoderPad (human)
- **Follow-ups:** decay frequencies over time, approximate LFU (sampling), combine with TTL.
- **Tips:** narrate the freq-bucket structure before coding; reset `min_freq=1` on every new insert.
- **Pitfalls:** forgetting to bump freq on `get`, O(n) scans for the min bucket (track it).

## Related
[[17-lru-cache]] (do first).
