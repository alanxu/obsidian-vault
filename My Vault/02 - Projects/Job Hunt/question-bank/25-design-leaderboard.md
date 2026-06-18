---
title: Design a Leaderboard
slug: design-leaderboard
type: leetcode-design
leetcode: 1244
companies: [Gaming, general]
difficulty: ★★★☆☆
frequency: low-med
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 20–30 min
tags: [hashmap, ranking, top-k, heap-or-sorted]
related: ["[[02-banking-system]]"]
---

# Design a Leaderboard (#1244)

Add scores, sum top-K, reset players — same `top_spenders` muscle as the banking problem.

## Problem
`addScore(playerId, score)` (accumulate); `top(K)` → sum of K highest; `reset(playerId)`.

## Core approach (format-agnostic)
`dict player→score`; `top(K)` = `nlargest(K, scores.values())`. If `top` is hot, keep a **sorted structure** (SortedList / ZSET) for O(log n) updates + O(K) top.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** dict + heap is enough for the constraints; reset removes or zeroes.
- **Pitfalls:** K > #players, reset of unknown player, ties.

### Live · CoderPad (human)
- **Follow-ups:** player **rank** query, live updates at scale (Redis ZSET / SortedList), pagination, time-windowed leaderboard.
- **Tips:** discuss the **heap-vs-sorted-structure** trade-off based on read/write mix.
- **Pitfalls:** re-sorting on every `top` when updates are rare (or vice versa).

## Related
[[02-banking-system]] (`top_spenders`).
