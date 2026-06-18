---
title: Expiring Credit Ledger (out-of-order events)
slug: expiring-credit-ledger
type: multi-level-stateful
leetcode: null
companies: [OpenAI]
difficulty: ★★★★☆
frequency: high
formats: [Live, Take-home]
levels: 3
time-box: live 45–60 min
tags: [oo-design, expiry, out-of-order, greedy-consumption, event-sourcing]
related: ["[[06-gpu-credit-manager]]", "[[openai-interview-guide]]"]
---

# Expiring Credit Ledger ⭐

OpenAI favorite. Credits **expire**, consumed **earliest-expiring first**, with **out-of-order** events — the hard part is correctness under reordering.

## Problem
- `add_credit(id, amount, ts, expiration)`; `use_credit(id, amount, ts)` (deduct earliest-expiring non-expired first); `balance(id, ts)`.

## Core approach (format-agnostic)
Events can arrive **out of timestamp order**. Two strategies — state the trade-off:
- **Eager** (apply on write): fast reads, **wrong** under reorder.
- **Lazy / event-sourced** (correct): append-only event log; on `balance(ts)`, **replay events with time ≤ ts in timestamp order**, consuming earliest-expiry-first via a heap. O(n log n)/query, fast writes.
Worked code + narration: [[openai-interview-guide]] Problem 4.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** start eager, interviewer reveals an out-of-order test → you pivot to replay. The pivot **is** the test.
- **Follow-ups:** idempotent events (request id), persistence, per-user sharding, "available at a future ts" projection.
- **Tips:** **ask** "can events arrive out of order?" early; name the eager-vs-replay trade-off explicitly; write an out-of-order test yourself.
- **Pitfalls:** assuming ordered input; expiry exactly at `ts` (half-open); using more than available (cap vs reject — clarify).

### Take-home / work-trial (async build)
- **How it appears:** as a small service with tests.
- **Tips:** ship the **correct** (replay) version + a few edge tests + a README noting the eager/lazy trade-off.
- **Pitfalls:** untested reordering path; no idempotency on retried events.

## Related
[[06-gpu-credit-manager]] (adds allocate/release + idempotency) · [[10-api-log-parser-token-aggregator]] (token accounting).
