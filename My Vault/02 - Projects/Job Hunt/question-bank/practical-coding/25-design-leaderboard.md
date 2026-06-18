---
title: Design a Leaderboard
slug: design-leaderboard
type: leetcode-design
leetcode: 1244
companies: [Roblox, Riot-Games, "any gaming / competitive platform", "Sports/social leaderboards"]
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

- `addScore(playerId, score)` — accumulate score for the player.
- `top(K) -> int` — sum of the top K players' scores.
- `reset(playerId)` — remove the player.

## Core approach (format-agnostic)

**Approach A — Hashmap + sort on demand:**
- `dict[player → score]`.
- `top(K)` = `sum(sorted(scores.values(), reverse=True)[:K])`.
- O(U log U) per `top`.

**Approach B — Heap on demand:**
- `heapq.nlargest(K, scores.values())` — O(U log K).

**Approach C — Sorted structure (if `top` is hot):**
- `sortedcontainers.SortedList` of `(score, playerId)` tuples, or `bisect`-maintained sorted list.
- O(log U) update, O(K) top.

For OA-style constraints, Approach A is fast enough. Use Approach C only if you anticipate per-update top queries.

### Worked Python solutions

**Hashmap + sort:**
```python
class Leaderboard:
    def __init__(self):
        self.scores = {}

    def addScore(self, playerId: int, score: int) -> None:
        self.scores[playerId] = self.scores.get(playerId, 0) + score

    def top(self, K: int) -> int:
        return sum(sorted(self.scores.values(), reverse=True)[:K])

    def reset(self, playerId: int) -> None:
        self.scores.pop(playerId, None)
```

**Heap version:**
```python
import heapq

class Leaderboard:
    def __init__(self):
        self.scores = {}

    def addScore(self, playerId: int, score: int) -> None:
        self.scores[playerId] = self.scores.get(playerId, 0) + score

    def top(self, K: int) -> int:
        return sum(c for _, c in heapq.nlargest(K, [(s, p) for p, s in self.scores.items()]))

    def reset(self, playerId: int) -> None:
        self.scores.pop(playerId, None)
```

**Complexity.** Hashmap + sort: O(U log U) per `top`. Heap: O(U log K).

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:**
  - Dict + heap is enough for the constraints.
  - Reset removes or zeroes — confirm.
- **Pitfalls:**
  - `K > #players` — sum all available.
  - Reset of unknown player — silent (no-op).
  - Tie-break — usually irrelevant for `sum`, matters for `rank`.

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **Player rank query** — `rank(playerId) -> int` — what position is this player?
  - **Live updates at scale** — Redis ZSET, SortedList, balanced BST.
  - **Pagination** — `top(K, page)` for very large K.
  - **Time-windowed leaderboard** — daily / weekly reset.
  - **Per-region / per-leaderboard** — namespacing.
  - **Score decay** — old scores count less; weighted by recency.
  - **Tournament-style** — elimination brackets, head-to-head.
  - **Distributed** — shard players; aggregate top per shard, then global top.
- **Tips:**
  - **Discuss the heap-vs-sorted-structure trade-off** based on read/write mix.
  - For rank: `(score, playerId)` tuple with a stable tie-break (playerId asc).
  - For time-windowed: a `(timestamp → scores)` map; reset by dropping old windows.
- **Pitfalls:**
  - **Re-sorting on every `top` when updates are rare** — fine; mention as design point.
  - **Re-sorting on every update when reads are rare** — also fine.
  - **Concurrent updates** — locks or per-player locks.

### Onsite · NR (Google-style)
- **Tips:** State the heap-vs-sort trade-off explicitly.
- **Pitfalls:** Forgetting the `K > U` edge case.

## Company variants

- **Roblox / Riot Games / competitive platforms** — production-flavored.
- **Sports / social** — same patterns at different scale.

## Worked example trace

```
addScore(1, 73); addScore(2, 56); addScore(3, 78); addScore(4, 51)
top(3)              # 78 + 73 + 56 = 207
addScore(2, 32)     # 2 now has 88
top(3)              # 88 + 78 + 73 = 239
reset(2)
top(3)              # 78 + 73 + 51 = 202
```

## Related
[[02-banking-system]] (`top_spenders`).