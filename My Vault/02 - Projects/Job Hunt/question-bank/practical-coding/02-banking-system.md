---
title: Banking System
slug: banking-system
type: multi-level-stateful
leetcode: null
companies: [Anthropic, OpenAI, Robinhood, Stripe, Coinbase, Capital One, Block, Plaid, "Cash App", Revolut, "CodeSignal fintech cos"]
difficulty: ★★★★☆
frequency: very-high
formats: [OA·ICA, Live]
levels: 4
time-box: 90 min for 4 levels
tags: [oo-design, ranking, scheduled-events, historical-state, time-ordered, heap, lazy-evaluation]
related: ["[[01-in-memory-key-value-database]]", "[[25-design-leaderboard]]", "[[practical-oo-coding-deep-guide]]", "[[05-expiring-credit-ledger]]"]
---

# Banking System ⭐⭐

The other dominant ICA project. **Accounts + time-ordered operations.** Tests ordered processing, ranking, and historical queries. Expects careful money handling (no floating point for balances).

## Problem (by level)

The bank tracks accounts (each with a string `id`), balances, and outgoing totals. All operations take a `ts` (timestamp) and must respect ordering.

### L1 — Core operations
- `create_account(ts, id) -> bool` — `false` if account already exists.
- `deposit(ts, id, amount) -> int` — returns the **new balance**; reject negative amounts (return `-1` or current balance, per spec).
- `transfer(ts, from_id, to_id, amount) -> int` — moves money between accounts; reject on insufficient funds (return `-1`) or missing accounts (return `-1`); on success return the **sender's new balance**.
- Optional: `top_spenders` may sneak into L1; confirm from the example.

### L2 — Ranking
- `top_spenders(ts, n) -> str` — top-N accounts by **total outgoing amount** (sum of `transfer` outflows + payments), tie-break by **id ascending**. Format usually `"id1(amount), id2(amount), …"`.

### L3 — Scheduled + cashback
- `pay(ts, id, amount) -> int` (or `-> payment_id`) — charge the account immediately, **schedule** a cashback (e.g., 2% of `amount`) to credit after a delay (e.g., 5 timestamps). Returns the new balance or `payment_id`.
- `get_payment_status(ts, id, payment_id) -> str` — returns `"IN_PROGRESS"` until the cashback is credited, `"COMPLETED"` after. Cashbacks process in **time order** as the clock advances.

> **Critical:** events process in **timestamp order**, not arrival order. If `pay` happened at `ts=2` with cashback-due `7`, and another op arrives at `ts=10`, the cashback must be credited **before** processing the `ts=10` op.

### L4 — Merge + history
- `merge_accounts(ts, id1, id2) -> bool` — combine two accounts (sum balances, sum outgoing totals, merge pending payments; reassign payment ids; `id2` is consumed).
- `get_balance(ts, id, time_at) -> int` — return the **balance at a past time** (`time_at ≤ ts`). Requires a balance history.

## Core approach (format-agnostic)

Two structural choices drive correctness. Make them at L1 and they pay off through L4.

**1. Per-account state**
```
account = {
  "balance": int,                # cents, NOT float
  "outgoing": int,               # total sent (for top_spenders)
  "history": [(ts, balance_after)],   # for get_balance
  "pending": [payment_id, ...],  # for cashback bookkeeping
}
```

**2. Lazy event advance.** Before any public op at `ts`, **flush all scheduled cashbacks with `due ≤ ts`** from a min-heap `(due_ts, arrival_idx, account_id, amount)`. The `arrival_idx` breaks ties at identical timestamps deterministically.

For `get_balance(ts, id, time_at)`: keep a per-account `(ts, balance)` history (append on every balance change). At query time, binary-search for the largest entry with `ts ≤ time_at`. **This is the same primitive as Q01 / Q07** — reuse it.

For `merge`: combine balances, sum `outgoing`, **consolidate pending payments**, reassign ids to one namespace, delete the merged account.

### Worked Python solution (skeleton)

```python
import heapq

class Bank:
    def __init__(self):
        self.accounts = {}             # id -> state dict
        self.pending = []              # min-heap of (due_ts, idx, id, amount)
        self._counter = 0              # for deterministic tie-break

    def _advance(self, ts):
        while self.pending and self.pending[0][0] <= ts:
            due, _, aid, amount = heapq.heappop(self.pending)
            if aid not in self.accounts:
                continue                # account may have been merged/deleted
            acc = self.accounts[aid]
            acc["balance"] += amount
            acc["history"].append((ts, acc["balance"]))

    def _ensure(self, ts, id):
        self._advance(ts)
        if id not in self.accounts:
            return None
        return self.accounts[id]

    def create_account(self, ts, id):
        self._advance(ts)
        if id in self.accounts:
            return False
        self.accounts[id] = {"balance": 0, "outgoing": 0,
                             "history": [(ts, 0)], "pending": set()}
        return True

    def deposit(self, ts, id, amount):
        if amount < 0:
            return -1
        acc = self._ensure(ts, id)
        if acc is None:
            return -1
        acc["balance"] += amount
        acc["history"].append((ts, acc["balance"]))
        return acc["balance"]

    def transfer(self, ts, src, dst, amount):
        if amount < 0:
            return -1
        self._advance(ts)
        if src not in self.accounts or dst not in self.accounts:
            return -1
        if self.accounts[src]["balance"] < amount:
            return -1
        self.accounts[src]["balance"] -= amount
        self.accounts[src]["outgoing"] += amount
        self.accounts[dst]["balance"] += amount
        self.accounts[src]["history"].append((ts, self.accounts[src]["balance"]))
        self.accounts[dst]["history"].append((ts, self.accounts[dst]["balance"]))
        return self.accounts[src]["balance"]

    def top_spenders(self, ts, n):
        self._advance(ts)
        ranked = sorted(
            ((acc["outgoing"], id) for id, acc in self.accounts.items()),
            key=lambda x: (-x[0], x[1]),
        )[:n]
        return ", ".join(f"{id}({out})" for out, id in ranked)

    def pay(self, ts, id, amount, cashback_pct=2, delay=5):
        acc = self._ensure(ts, id)
        if acc is None or amount <= 0 or acc["balance"] < amount:
            return None
        acc["balance"] -= amount
        acc["outgoing"] += amount
        acc["history"].append((ts, acc["balance"]))
        self._counter += 1
        cashback = (amount * cashback_pct) // 100
        if cashback > 0:
            heapq.heappush(self.pending, (ts + delay, self._counter, id, cashback))
            acc["pending"].add(self._counter)
        return self._counter

    def get_payment_status(self, ts, id, pid):
        self._advance(ts)
        if pid in self.accounts.get(id, {}).get("pending", set()):
            return "IN_PROGRESS"
        return "COMPLETED"

    def merge_accounts(self, ts, id1, id2):
        self._advance(ts)
        if id1 not in self.accounts or id2 not in self.accounts or id1 == id2:
            return False
        a, b = self.accounts[id1], self.accounts[id2]
        a["balance"] += b["balance"]
        a["outgoing"] += b["outgoing"]
        a["history"].extend(b["history"])
        a["history"].sort()
        a["pending"].update(b["pending"])
        del self.accounts[id2]
        return True

    def get_balance(self, ts, id, time_at):
        self._advance(ts)
        if id not in self.accounts:
            return -1
        hist = self.accounts[id]["history"]
        # binary search for largest ts <= time_at
        lo, hi = 0, len(hist) - 1
        ans = -1
        while lo <= hi:
            mid = (lo + hi) // 2
            if hist[mid][0] <= time_at:
                ans = hist[mid][1]
                lo = mid + 1
            else:
                hi = mid - 1
        return ans
```

**Complexity.** All ops O(log H) where H is pending heap size; `top_spenders` O(A log A) where A is accounts; `get_balance` O(log H_hist) per account.

## By format

### OA · ICA (CodeSignal, 4 levels, auto-graded)
- **How it appears:** the canonical 4-level banking project; hidden tests; levels unlock sequentially.
- **Tips:**
  - Build the **lazy event-advance** in L1 even though L1 doesn't need it (L3 does). Same for the per-account `history` list (L4 needs it).
  - Use **integer cents** for money — never `float`. Floats cause hidden-test failures on boundary amounts (0.1 + 0.2 ≠ 0.3).
  - Match the **exact return type** from the examples — string vs int vs bool. Anthropic's bank uses string returns (`"true"`/`"false"`).
  - Confirm `top_spenders` tie-break direction (usually `id ascending`).
- **Pitfalls:**
  - Applying cashbacks at the **wrong time** (must be ordered by `due_ts`); forgetting to advance before reading state.
  - **Ranking tie-break wrong** (off-by-one direction, missing id sort).
  - `get_balance` **off-by-one** at the query time (≤ vs <).
  - `merge_accounts` losing `outgoing` totals (breaks `top_spenders`).
  - Self-transfer (`transfer(a, a, n)`) — spec usually says reject or no-op.

### Live · CoderPad (human, narrate)
- **How it appears:** L1–L2 live in ~25 min; interviewer extends to scheduling/history verbally.
- **Follow-ups (real, reported):**
  - **Cancel a scheduled payment** — needs a tombstone in the heap; check on pop.
  - **Idempotent transfers** — accept a `request_id`, dedupe in a `seen: dict[request_id → result]`.
  - **Interest accrual** — periodic `rate` per `time_unit`; lazy accrual at query time is the clean answer.
  - **Concurrency** — `threading.Lock`; per-account locks for fine-grained parallelism.
  - **Multi-currency / FX** — each account has a currency; conversion at transfer time.
  - **Audit log / replay** — append-only event log; full state rebuildable from log.
  - **Daily settlement file** — output all balances at end-of-day; tie into streaming.
- **Tips:**
  - Narrate "I process events in time order via a heap, advanced on each op" — make the design audible.
  - Write a transfer + a `top_spenders` test and trace the output aloud.
  - When asked about idempotency, **say why** (network retries in fintech infra).
  - Mention the integer-cents choice unprompted — reads as senior.
- **Pitfalls:**
  - Floating-point money — silent test failures.
  - Self-transfer (`id1 == id2`) — confirm spec.
  - Transfer to missing account (return value semantics).
  - Heap entries referencing deleted accounts after merge — guard on pop.

### Take-home / timed async
- **Tips:**
  - Ship L1–L3 with a `--seed` mode and a `pytest` suite that covers ordering + cashback timing.
  - README the integer-cents decision and the lazy-advance trade-off.
- **Pitfalls:**
  - No tests for the cashback ordering (out-of-order arrivals).
  - No tests for `merge` losing history.

## Company variants

- **Anthropic (canonical)** — circulated "bank with multiple transaction types"; L3 cashback with delay.
- **OpenAI** — sometimes reskinned as "credits with scheduled refunds" → see [[05-expiring-credit-ledger]].
- **Robinhood** — strong reliability + idempotency emphasis; concurrency follow-up almost guaranteed.
- **Stripe / Coinbase / Plaid** — full 4-level with audit-log L4; expect idempotency-key follow-up.
- **Cash App / Block / Revolut** — fintech ICA skins with similar mechanics.
- Mirrors Robinhood's reliability/ledger emphasis (also see Track C **payment-ledger** design).

## Worked example trace (for narration)

```
t=0  create_account("a1")           # a1: balance=0, history=[(0,0)]
t=1  create_account("a2")
t=2  deposit("a1", 100)              # a1: balance=100, history +=(2,100)
t=3  transfer("a1","a2",30)          # a1: 70, outgoing=30; a2: 30
t=5  pay("a1", 50)                   # a1: 20, outgoing=80; cashback=1 due@t=10
t=8  deposit("a2", 10)               # advance first: cashback@10 not yet due → noop
t=10 deposit("a1", 5)                # advance fires: a1 +=1 → 21; then deposit → 26
t=12 top_spenders(2)                 # a1: outgoing=80, a2: outgoing=0 → "a1(80),a2(0)"
t=15 get_balance(15,"a1", 5)         # hist: [(0,0),(2,100),(5,20),(10,21),(15,26)]
                                     # bisect ≤5 → (5,20) → 20
```

## Related
[[01-in-memory-key-value-database]] (sibling ICA, version-list primitive) · [[25-design-leaderboard]] (same `top_spenders` muscle) · [[05-expiring-credit-ledger]] (out-of-order variant) · Track C payment-ledger design.