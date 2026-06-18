---
title: GPU Credit Manager
slug: gpu-credit-manager
type: multi-level-stateful
leetcode: null
companies: [OpenAI]
difficulty: ★★★★☆
frequency: medium
formats: [Live, Take-home]
levels: 3
time-box: live 45–60 min
tags: [oo-design, expiry, allocate-release, idempotency]
related: ["[[05-expiring-credit-ledger]]", "[[openai-interview-guide]]"]
---

# GPU Credit Manager

[[05-expiring-credit-ledger]]'s structure plus **reservation** semantics and **idempotency** — models metered GPU compute.

## Problem
- `add_credit(id, amount, ts, expiration)`; `allocate(id, amount, ts, request_id)` (reserve if sufficient; **idempotent** on request_id); `release(id, amount, ts)`; `available(id, ts)` = balance − allocated.

## Core approach (format-agnostic)
Reuse Q05's expiring-credit core (earliest-expiry-first, lazy replay). Track `allocated` separately; `available = balance − allocated`. **Idempotency:** `seen_requests` dict — a repeated `allocate(request_id)` returns the prior result, no double-charge. Code: [[openai-interview-guide]] Problem 5.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** builds on the ledger; the headline follow-up is **idempotency** ("what if allocate is retried?").
- **Follow-ups:** partial allocation, priority/fairness across users, TTL on reservations, **distributed counter** (→ Track C).
- **Tips:** implement idempotency with a request-id map and narrate why (network retries); separate `allocated` from `balance`.
- **Pitfalls:** double-charging on retry, releasing more than allocated, allocating against soon-to-expire credit.

### Take-home / work-trial
- **Tips:** include idempotency + a retry test in the repo; README the reservation accounting.
- **Pitfalls:** non-idempotent allocate; race between allocate/release (note the locking story).

## Related
[[05-expiring-credit-ledger]] (base) · Track C distributed-counter / rate-limiter design.
