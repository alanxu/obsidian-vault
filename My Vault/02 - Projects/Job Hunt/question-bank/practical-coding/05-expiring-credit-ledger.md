---
title: Expiring Credit Ledger (out-of-order events)
slug: expiring-credit-ledger
type: multi-level-stateful
leetcode: null
companies: [OpenAI, Anthropic, Stripe, Coinbase, "AWS Billing", "Databricks", "Snowflake"]
difficulty: ★★★★☆
frequency: high
formats: [Live, Take-home]
levels: 3
time-box: live 45–60 min
time-box-take-home: 4–8 hours
tags: [oo-design, expiry, out-of-order, greedy-consumption, event-sourcing, replay]
related: ["[[06-gpu-credit-manager]]", "[[02-banking-system]]", "[[openai-interview-guide]]"]
---

# Expiring Credit Ledger ⭐

OpenAI favorite and a recurring Stripe/Billing pattern. Credits **expire**, are consumed **earliest-expiring first**, with **out-of-order** events — the hard part is correctness under reordering. Tests your ability to articulate the eager-vs-lazy trade-off out loud before coding.

## Problem

Track per-user credit grants; each grant has an `expiration` timestamp. Operations:

- `add_credit(user_id, amount, ts, expiration)` — add a credit grant.
- `use_credit(user_id, amount, ts)` — deduct `amount` from the user's earliest-expiring non-expired credits first.
- `balance(user_id, ts)` — return the user's available credit at `ts`.

The **hard constraint:** events may arrive **out of timestamp order**. A `use_credit` at `ts=5` may arrive after a `use_credit` at `ts=10`.

## Core approach (format-agnostic)

There are exactly two strategies. **State the trade-off before writing any code** — the interviewer is testing whether you see the trade-off, not whether you can write the loop.

### Strategy A — Eager (apply on write)
- Maintain per-user running balance and per-grant `remaining`.
- On `add_credit`: append grant; bump available.
- On `use_credit`: deduct earliest-expiring first; track per-grant `remaining`.
- `balance(ts)` = sum non-expired `remaining`.
- **Pros:** O(1) reads.
- **Cons:** **wrong** under reordering. If a later `use_credit` at `ts=2` arrives after `ts=10` deducted from grant X, but `ts=2` should have hit grant Y first, your deductions are in the wrong grants.

### Strategy B — Lazy / event-sourced (correct)
- Append every event to an event log `(ts, type, …)`.
- On `balance(ts)`: **replay all events with `ts ≤ ts_query` in timestamp order**, building a fresh in-memory state with a heap of `(exp, remaining)` for non-expired grants. Consume earliest-expiring first.
- `use_credit` during replay: same logic.
- **Pros:** always correct under reordering.
- **Cons:** O(n log n) per `balance` query; replays must be bounded (cap log size or memoize).

### Hybrid
Keep a recent "replay window" (last N events) plus a materialized snapshot for `ts < oldest_in_window`. Compromise on complexity.

### Worked Python solution (Lazy / event-sourced)

```python
import heapq

class CreditLedger:
    def __init__(self):
        # event log; sorted lazily on query
        self._events = []               # list of (ts, idx, kind, payload)
        self._idx = 0

    def add_credit(self, uid, amount, ts, expiration):
        self._idx += 1
        self._events.append((ts, self._idx, "add", (uid, amount, expiration)))

    def use_credit(self, uid, amount, ts):
        self._idx += 1
        self._events.append((ts, self._idx, "use", (uid, amount)))

    def balance(self, uid, ts):
        # Replay events with ts <= query ts, in (ts, idx) order
        relevant = [e for e in self._events if e[0] <= ts]
        relevant.sort(key=lambda e: (e[0], e[1]))

        # user -> min-heap of (expiration, remaining)
        grants = {}
        used = 0
        for _, _, kind, payload in relevant:
            if kind == "add":
                u, amt, exp = payload
                if u != uid:
                    continue
                if exp <= ts:
                    continue              # already expired at query time
                heapq.heappush(grants.setdefault(u, []), [exp, amt])
            else:  # use
                u, amt = payload
                if u != uid:
                    continue
                # consume earliest-expiring first
                h = grants.setdefault(u, [])
                while amt > 0 and h:
                    exp, rem = h[0]
                    if exp <= ts:
                        heapq.heappop(h)
                        continue
                    take = min(rem, amt)
                    h[0][1] -= take
                    amt -= take
                    if h[0][1] == 0:
                        heapq.heappop(h)
                if amt > 0:
                    used += amt            # overdrawn — spec-dependent
        return sum(rem for _, rem in grants.get(uid, []))
```

**Complexity.** `add_credit` / `use_credit`: O(1). `balance(ts)`: O(N log N + G) where N = total events and G = grants for the user. For take-home: amortize by caching per-(user, max-ts) snapshots.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** you start with Strategy A (eager, simple), the interviewer reveals an out-of-order test, you pivot to Strategy B (replay). **The pivot itself is the test.**
- **Follow-ups (real, reported):**
  - **Idempotent events** — pass a `request_id`, dedupe in `seen: set`.
  - **Persistence** — append the event log to disk; reload on startup.
  - **Per-user sharding** — split the log by user; parallel replay.
  - **Available-at-future-ts projection** — `balance(uid, ts)` for many ts values; precompute a piecewise function.
  - **Cap vs reject on overdraw** — when `use_credit` exceeds available, do you cap (use what's there) or reject (return false)?
  - **Time-range query** — "credits that expire between ts_a and ts_b".
  - **Concurrency** — multiple writers; lock or per-user mutex.
- **Tips:**
  - **Ask early:** "Can events arrive out of order?" Most interviewers say yes; some say no. Your trade-off framing only lands if you ask.
  - **Name the eager-vs-replay trade-off out loud** before coding. Mention memory vs compute.
  - Write an out-of-order test yourself and trace it through both strategies.
  - For idempotency: `seen: set[request_id]` + return cached result.
- **Pitfalls:**
  - **Assuming ordered input** — the question's whole point.
  - **Expiry exactly at `ts`** — confirm half-open `[granted, expired)` convention.
  - **Using more than available** — clarify cap vs reject.
  - **Replay ignoring `ts > query_ts`** — events that haven't "happened yet" at the query time must be skipped.
  - **Float vs int** — use integer cents for money.

### Take-home / work-trial (async build)
- **How it appears:** small service with tests; sometimes with a REST/gRPC API.
- **Tips:**
  - Ship the **correct (replay)** version + edge-case tests + a README explaining the trade-off.
  - Include the `request_id` idempotency layer.
  - Provide a benchmark: O(events) replay time at 10k, 100k, 1M events.
  - Optional: snapshot compaction (drop events older than `min(current_grant_exp)`).
- **Pitfalls:**
  - Untested reordering path — the bug surface.
  - No idempotency on retried events → double-charge.
  - Replay cost grows unboundedly — no compaction.

## Company variants

- **OpenAI** — the canonical "Problem 4" in their bank; default eager → replay pivot.
- **Anthropic** — reskinned as "API token credits with monthly expiration" in applied-AI tracks.
- **Stripe** — "subscription credits with proration and expiration" extension.
- **Coinbase / AWS Billing** — same structure; sometimes with **partial consumption** (use 50 of a 100-credit grant, leaving 50 with the original expiration).
- **Databricks / Snowflake** — "compute credits per workspace" reskin.

## Worked example trace

```
t=0  add_credit("u1", 100, 0, 10)         # grant1: exp=10
t=1  add_credit("u1", 50, 1, 5)           # grant2: exp=5
t=2  use_credit("u1", 30, 2)              # consume grant2 (exp=5): grant2=20
t=20 use_credit("u1", 50, 20)             # OUT-OF-ORDER arrives late
                                           # replay events ≤20: grants=20 (from g1)
                                           # consume 20 from g1: g1=80
                                           # need 30 more — grant1 left = 80, take 30 → g1=50
balance("u1", 20) → 50 (from grant1)
```

If processed eagerly: the late `use_credit` would either silently overdraw or be rejected.

## Related
[[06-gpu-credit-manager]] (adds allocate/release + idempotency) · [[02-banking-system]] (time-ordered sibling) · [[10-api-log-parser-token-aggregator]] (token accounting).