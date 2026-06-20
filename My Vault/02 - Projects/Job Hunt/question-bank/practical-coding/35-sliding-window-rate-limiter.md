---
title: Sliding-Window Rate Limiter (should_allow)
slug: sliding-window-rate-limiter
type: live-coding + design follow-ups
leetcode: null
companies: [Anthropic (reported phone screen), Stripe, Cloudflare, OpenAI, "any API platform"]
difficulty: ★★★☆☆
frequency: high
formats: [Live, OA·GCA/HR]
levels: 4
time-box: live 30–45 min
tags: [rate-limiting, sliding-window, concurrency, locks, redis, distributed]
related: ["[[23-logger-rate-limiter]]", "[[24-hit-counter]]", "[[12-multithreaded-web-crawler]]"]
source: "Anthropic interview case study (Notion inbox / image, 2026-06-19) — author not senior; senior review added"
---

# Sliding-Window Rate Limiter (`should_allow`)

> **Reported Anthropic phone technical screen.** Classic "system-design-meets-coding" — they grade *how you think and iterate*, not a single optimal answer. The realistic arc: a simple data structure → memory optimization → thread safety → distributed.

## Problem
Implement `should_allow(user_id, timestamp) -> bool`: return `True` if the request is allowed, else `False`. The limit is **no more than N requests in the last T seconds for any given user**.

> **Clarify first (the author skipped this):** Is the key the **user** (yes — "per user")? Window boundary inclusive/exclusive — is it `(ts-T, ts]`? Are timestamps monotonic or can they arrive out of order? Single process or distributed? **Exact** limiting or is approximate OK (changes the algorithm)?

## Core approach — sliding-window log (exact)
Per user, keep a **deque of recent request timestamps**. On each call: evict timestamps outside the window, then allow iff the count is `< N`.

```python
from collections import defaultdict, deque

class RateLimiter:
    def __init__(self, n: int, t: int):
        self.n, self.t = n, t
        self.reqs = defaultdict(deque)          # user_id -> deque[timestamp]

    def should_allow(self, user_id, ts) -> bool:
        q = self.reqs[user_id]
        while q and q[0] <= ts - self.t:        # drop requests outside (ts-T, ts]
            q.popleft()
        if len(q) < self.n:
            q.append(ts)
            return True
        return False
```
**Complexity:** amortized O(1) per call; **memory O(N) per active user** (it stores every in-window timestamp) — this is the catch.

## The interview arc (levels)
- **L1 — basic:** the deque-per-user above. *(Author got here.)*
- **L2 — memory at scale:** "millions of users — memory?" → a **hash map `user_id → deque`** allocates on demand (author's answer; correct). Senior add: **the sliding-window LOG is itself O(N) per user** — for large N use an **approximate** algorithm with O(1) memory (see tradeoffs).
- **L3 — thread safety:** "is this thread-safe?" → No. Concurrent calls for the same user race on the deque. Use a **per-user lock** (a global lock serializes everyone → too slow). *(Author got here.)* Senior add: the **lock-map itself needs synchronization** when creating a user's lock (double-checked locking or `setdefault`), else two threads create two locks.
- **L4 — distributed:** "deployed on many machines?" → in-memory map doesn't share state → **Redis**. Author's answer (correct): a **sorted set per user**, `score = timestamp`, `member = request_id`; per request `ZREMRANGEBYSCORE` (evict) → `ZCARD` (count) → `ZADD` (insert), wrapped in a **Lua script** for atomicity.

## Tradeoffs — rate-limiting algorithms (the author only did the log)
| Algorithm | Memory | Accuracy | Notes |
|---|---|---|---|
| **Sliding-window log** | O(N)/user | exact | what the author built; heavy at high N |
| **Fixed-window counter** | O(1) | bursty at boundaries | cheapest; 2× burst at window edge |
| **Sliding-window counter** | O(1) | ~exact (interpolates) | best practical default |
| **Token bucket** | O(1) | allows controlled bursts | great for "burst then steady" APIs |

## Senior review of the reported answer
Solid progression, but a stronger candidate would also: (1) **clarify** the window boundary + key + exactness up front; (2) name the **log's O(N) memory** and offer **token-bucket / sliding-window-counter** as O(1) alternatives; (3) call out the **lock-creation race** in the per-user-lock map; (4) on Redis, **set `EXPIRE`/TTL** on each user's key (sorted sets grow forever for inactive users — the author omitted this) and note that the sorted-set log is also memory-heavy → a Redis token-bucket (`INCR`+`EXPIRE` per bucket) is O(1) for huge scale; (5) mention **clock skew** across app servers → use Redis server time or a consistent clock; (6) `request_id` as the sorted-set **member** is the right call (timestamps can collide) — that's why the signature carries an id distinct from the user key.

## By format
### Live · CoderPad — *primary (Anthropic phone screen)*
- **Follow-ups:** the L2–L4 arc above; per-endpoint vs per-user limits; different limits per tier; fail-open vs fail-closed when Redis is down.
- **Tips:** narrate the clarify step; build L1 cleanly, then *volunteer* the memory/thread/distributed extensions; for distributed, **describe** the Redis+Lua pattern, don't code Redis live.
- **Pitfalls:** wrong window boundary; global lock (too slow); forgetting Redis TTL; assuming monotonic timestamps; counting the current request on the wrong side of the check.

### OA · GCA / HR (auto-graded)
- **Tips:** the deque-per-user log passes; mind the boundary convention.
- **Pitfalls:** off-by-one on `ts - T`; not evicting before counting.

## Related
[[23-logger-rate-limiter]] (the simpler #359 logger variant) · [[24-hit-counter]] (sliding-window counting) · distributed design → `question-bank/distributed-system-design` (rate-limiter prompt).
