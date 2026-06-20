---
title: Logger Rate Limiter
slug: logger-rate-limiter
type: leetcode-design
leetcode: 359
companies: [Stripe, Cloudflare, Cohere, OpenAI, Anthropic, "any API platform"]
difficulty: ★★☆☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 15–25 min
tags: [hashmap, time-window, rate-limiting, sliding-window]
related: ["[[24-hit-counter]]", "[[10-api-log-parser-token-aggregator]]"]
---

# Logger Rate Limiter (#359)

Print a message only if not seen in the last 10s. The base is trivial; the follow-ups are where it lives.

> **The general rate limiter** — Anthropic's `should_allow(user_id, ts)`, N requests in T seconds per user, with the concurrency → distributed-Redis arc — is **[[35-sliding-window-rate-limiter]]**. This card is the simpler LeetCode **#359 logger** variant.

## Problem

`shouldPrintMessage(timestamp, message) -> bool` — return `true` iff the message has not been printed in the last 10 seconds; record on `true`.

## Core approach (format-agnostic)

`dict[message → next_allowed_ts]`. Return `true` iff `timestamp ≥ next_allowed[message]`, then set `next_allowed = timestamp + 10`.

### Worked Python solution

```python
class Logger:
    def __init__(self):
        self.ok = {}                        # message -> next_allowed_ts

    def shouldPrintMessage(self, timestamp: int, message: str) -> bool:
        if message not in self.ok or timestamp >= self.ok[message]:
            self.ok[message] = timestamp + 10
            return True
        return False
```

**Complexity.** O(1) per call. Memory: unbounded (one entry per unique message ever seen).

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:**
  - Trivial map; clarify the boundary (exactly 10s later allowed?).
  - Most specs: `next_allowed = timestamp + 10` and `timestamp ≥ next_allowed` allows the print.
- **Pitfalls:**
  - Boundary off-by-one — confirm convention.
  - Out-of-order timestamps — `timestamp` may go backward; the condition `timestamp ≥ next_allowed` handles it.

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **Token-bucket** rate limiter — `(tokens, last_refill_ts)`; refill at `rate` per second; consume one per call.
  - **Sliding window log** — `deque[timestamps]` per message; pop old timestamps, check size.
  - **Sliding window counter** — fixed buckets, weighted by overlap with the previous bucket.
  - **Bounded memory** — evict stale entries (TTL on the map).
  - **Per-user / per-tenant limits** — `dict[(user, message) → next_allowed]`.
  - **Different limits per message class** — `INFO` → 10s, `ERROR` → 1s.
  - **Distributed rate limiting** — Redis with `INCR` + `EXPIRE`, or sliding-window via Lua. → Track C.
  - **Async** — `asyncio.Lock` for thread-safe access.
  - **Atomic batch** — flush N messages at once, returning which were allowed.
- **Tips:**
  - **Mention the unbounded-memory issue** and how you'd evict (TTL, LRU on the map).
  - **Offer the token-bucket extension** — common follow-up.
  - For distributed: name the Redis pattern; don't try to code it in a coding round.
- **Pitfalls:**
  - **Unbounded map growth** — every unique message ever seen stays forever.
  - **Assuming ordered timestamps** — they may arrive out of order.
  - **Per-user limits without namespacing** — collision with global limits.

### Onsite · NR (Google-style)
- **Tips:** State the map shape and the boundary convention.
- **Pitfalls:** Getting the boundary wrong.

## Company variants

- **Stripe / Cloudflare / Cohere / OpenAI / Anthropic** — canonical rate-limiter shape.
- **API platforms broadly** — same primitive.

## Worked example trace

```
shouldPrintMessage(1, "foo")   # True;  ok["foo"] = 11
shouldPrintMessage(2, "foo")   # False (2 < 11)
shouldPrintMessage(11, "foo")  # True;  ok["foo"] = 21
shouldPrintMessage(11, "bar")  # True;  ok["bar"] = 21
```

## Related
[[35-sliding-window-rate-limiter]] (the general should_allow version) · [[24-hit-counter]] · [[10-api-log-parser-token-aggregator]] · distributed design → `question-bank/distributed-system-design`.