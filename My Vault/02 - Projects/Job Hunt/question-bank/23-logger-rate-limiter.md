---
title: Logger Rate Limiter
slug: logger-rate-limiter
type: leetcode-design
leetcode: 359
companies: [Fintech, API platforms, Cohere]
difficulty: ★★☆☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 15–25 min
tags: [hashmap, time-window, rate-limiting]
related: ["[[24-hit-counter]]"]
---

# Logger Rate Limiter (#359)

Print a message only if not seen in the last 10s — bridges to the Track C rate-limiter design.

## Problem
`shouldPrintMessage(timestamp, message)` → true iff not printed in the last 10s; record on true.

## Core approach (format-agnostic)
`dict message → next_allowed_ts`. Return true iff `timestamp ≥ next_allowed[message]`, then set `= timestamp + 10`.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** trivial map; clarify the boundary (exactly 10s later allowed?).
- **Pitfalls:** boundary off-by-one, out-of-order timestamps.

### Live · CoderPad (human)
- **Follow-ups:** **token-bucket** rate limiter (Cohere/OpenAI variant), bounded memory (evict stale), sliding vs fixed window, per-user limits, **distributed** (→ Track C).
- **Tips:** mention the unbounded-memory issue and how you'd evict; offer the token-bucket extension.
- **Pitfalls:** unbounded map growth, assuming ordered timestamps.

## Related
[[24-hit-counter]] · [[10-api-log-parser-token-aggregator]] · Track C rate-limiter design.
