---
title: Design Hit Counter
slug: hit-counter
type: leetcode-design
leetcode: 362
companies: [Twitter, Datadog, Cloudflare, Stripe, "any metrics/monitoring team"]
difficulty: ★★☆☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 15–25 min
tags: [queue, time-window, counting, circular-buffer]
related: ["[[23-logger-rate-limiter]]"]
---

# Design Hit Counter (#362)

Count hits in the trailing 300s window — a sliding-window counting primitive. Two viable structures; pick based on QPS.

## Problem

- `hit(timestamp)` — record a hit at `timestamp` (seconds).
- `getHits(timestamp) -> int` — return hits in the last 300 seconds (i.e., `(timestamp − 300, timestamp]`).

## Core approach (format-agnostic)

**Approach A — Deque of timestamps:** Each `hit` appends; each `getHits` pops the front while `front ≤ timestamp − 300`, then returns length. O(1) amortized per `hit`, O(W) per `getHits` (W = hits in window).

**Approach B — 300 fixed buckets** (preferred for high QPS): array of 300 `(time, count)` slots indexed by `timestamp % 300`. On `hit`, expire the slot if its `time != timestamp`, then increment. On `getHits`, sum counts of slots where `time > timestamp − 300`.

### Worked Python solutions

**Deque version:**
```python
from collections import deque

class HitCounter:
    def __init__(self):
        self.hits = deque()

    def hit(self, timestamp: int) -> None:
        self.hits.append(timestamp)

    def getHits(self, timestamp: int) -> int:
        while self.hits and self.hits[0] <= timestamp - 300:
            self.hits.popleft()
        return len(self.hits)
```

**Bucket version:**
```python
class HitCounter:
    def __init__(self):
        self.buckets = [[0, 0] for _ in range(300)]   # [time, count]

    def hit(self, timestamp: int) -> None:
        i = timestamp % 300
        if self.buckets[i][0] != timestamp:
            # expire and reset
            self.buckets[i] = [timestamp, 1]
        else:
            self.buckets[i][1] += 1

    def getHits(self, timestamp: int) -> int:
        return sum(c for t, c in self.buckets if t > timestamp - 300)
```

**Complexity.** Deque: O(1) amortized per hit, O(W) per query. Bucket: O(1) per hit, O(300) per query. Bucket is **bounded** regardless of QPS — better for production.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** Deque is fine for the base; mention buckets for scale.
- **Pitfalls:**
  - Window boundary — `≤ timestamp − 300` (inclusive eviction).
  - Many hits same second — handle in both versions.

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **Concurrency** — the **classic follow-up**. Locks or per-bucket atomics.
  - **Configurable window** — accept `window` in the constructor.
  - **Per-user / per-tenant** — `dict[user → HitCounter]`.
  - **Distributed counting** — shard by hash; merge via periodic flush (Track C).
  - **Percentile / p95** — keep individual hits in a sliding window; compute percentile.
  - **Decay** — exponential moving average instead of hard window.
  - **Top-K** — which endpoints / users have the most hits.
- **Tips:**
  - **Lead with the 300-bucket** circular array as the senior answer.
  - **Discuss thread safety** — `threading.Lock` around all ops; per-bucket locks for fine-grained parallelism.
  - For per-user: each user has their own HitCounter; aggregate on read.
- **Pitfalls:**
  - **Unbounded deque under high QPS** — the bucket version exists precisely for this.
  - **Race on the buckets** — increment + check-and-reset are not atomic together.
  - **Window edge cases** — query exactly at window boundary.

### Onsite · NR (Google-style)
- **Tips:** State both approaches; pick one and trace through a 3-hit example.
- **Pitfalls:** Forgetting the bucket-expiry logic.

## Company variants

- **Twitter / Datadog / Cloudflare / Stripe** — metrics/observability-flavored.
- **High-QPS systems** — bucket version is the production answer.

## Worked example trace

```
hit(1), hit(2), hit(301)         # deque: [1, 2, 301]
getHits(301)                      # window is (1, 301]; pop 1; → 2 hits
getHits(302)                      # window is (2, 302]; pop 2; → 1 hit
```

## Related
[[23-logger-rate-limiter]] · Track C metrics/monitoring design.