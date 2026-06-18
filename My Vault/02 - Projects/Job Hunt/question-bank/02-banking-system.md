---
title: Banking System
slug: banking-system
type: multi-level-stateful
leetcode: null
companies: [Anthropic ("bank w/ transactions"), fintech, CodeSignal cos (Capital One, Coinbase), Robinhood-style]
difficulty: ★★★★☆
frequency: very-high
formats: [OA·ICA, Live]
levels: 4
time-box: 90 min for 4 levels
tags: [oo-design, ranking, scheduled-events, historical-state, time-ordered]
related: ["[[01-in-memory-key-value-database]]", "[[25-design-leaderboard]]", "[[practical-oo-coding-deep-guide]]"]
---

# Banking System ⭐⭐

The other dominant ICA project. Accounts + **time-ordered** operations. Tests ordered processing, ranking, and historical queries.

## Problem (by level)
- **L1 — core:** `create_account(ts, id)` (false if exists); `deposit(ts, id, amount)` → new balance; `transfer(ts, from, to, amount)` → respect insufficient funds / missing accounts.
- **L2 — ranking:** `top_spenders(ts, n)` → top N by **total outgoing**, tie-break by id ascending.
- **L3 — scheduled + cashback:** `pay(ts, id, amount)` schedules e.g. **2% cashback after a delay**; `get_payment_status(ts, id, pid)`; events process in **time order** as the clock advances.
- **L4 — merge + history:** `merge_accounts(ts, id1, id2)`; `get_balance(ts, id, time_at)` → **balance at a past time**.

## Core approach (format-agnostic)
Account = `{balance, total_outgoing, payments}`. **Process scheduled events lazily**: before any op at `ts`, apply all cashbacks with `due ≤ ts` from a **min-heap** keyed by `due_ts`. For `get_balance(..., time_at)`: keep a **per-account `(ts, balance)` history** and binary-search ≤ `time_at` (same primitive as Q01). Merge: combine balances + outgoing totals + pending payments; reassign payment ids.

```python
import heapq
class Bank:
    def __init__(self): self.a={}; self.pending=[]
    def _advance(self, ts):
        while self.pending and self.pending[0][0] <= ts:
            due, aid, amt = heapq.heappop(self.pending)
            if aid in self.a:
                self.a[aid]["bal"] += amt
                self.a[aid]["hist"].append((due, self.a[aid]["bal"]))
    # every public op calls self._advance(ts) first
```

## By format

### OA · ICA (CodeSignal, 4 levels, auto-graded)
- **How it appears:** the canonical 4-level banking project; hidden tests; levels unlock.
- **Tips:** build the **lazy event-advance** in L1 even though L1 doesn't need it (L3 does); keep a balance history from L1 for L4; exact return types (string vs number — clarify from examples).
- **Pitfalls:** applying cashbacks at the wrong time (must be **ordered** by due_ts), ranking tie-break wrong, `get_balance` off-by-one at the query time, merge losing outgoing totals (breaks `top_spenders`).

### Live · CoderPad (human, narrate)
- **How it appears:** L1–L2 live; interviewer extends to scheduling/history verbally.
- **Follow-ups:** cancel a scheduled payment, interest accrual, **idempotent transfers** (request id), concurrency.
- **Tips:** narrate "I process events in time order via a heap, advanced on each op"; write a transfer + a top_spenders test.
- **Pitfalls:** floating-point money (use integer cents), self-transfer, transfer to missing account.

## Company variants
Anthropic's circulated "implement a bank with multiple transaction types." Otherwise a standard CodeSignal ICA fintech skin; mirrors Robinhood's reliability/ledger emphasis (also see Track C **payment-ledger** design).

## Related
[[01-in-memory-key-value-database]] (sibling ICA) · [[25-design-leaderboard]] (same `top_spenders` muscle) · Track C payment-ledger design.
