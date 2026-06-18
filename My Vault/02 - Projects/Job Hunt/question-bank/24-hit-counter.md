---
title: Design Hit Counter
slug: hit-counter
type: leetcode-design
leetcode: 362
companies: [General]
difficulty: ★★☆☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 15–25 min
tags: [queue, time-window, counting]
related: ["[[23-logger-rate-limiter]]"]
---

# Design Hit Counter (#362)

Count hits in the trailing 300s window — a sliding-window counting primitive.

## Problem
`hit(timestamp)`; `getHits(timestamp)` → hits in the last 300s.

## Core approach (format-agnostic)
A **deque** of timestamps; `getHits` pops front while `front ≤ timestamp − 300`, returns length. For high QPS, store **300 fixed buckets** `(time, count)` instead of per-hit.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** deque is fine for the base; mention buckets for scale.
- **Pitfalls:** window boundary (`≤ t−300`), many hits same second.

### Live · CoderPad (human)
- **Follow-ups:** **concurrency** (the classic follow-up — lock or per-bucket atomics), configurable window, distributed counting.
- **Tips:** lead with the **300-bucket** circular array as the senior answer; discuss thread safety.
- **Pitfalls:** unbounded deque under high QPS, race on the buckets.

## Related
[[23-logger-rate-limiter]] · Track C metrics/monitoring design.
