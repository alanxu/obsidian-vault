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

### L3 — Scheduled payments + cashback
- `pay(ts, id, amount) -> str | None` — withdraw `amount` from the account **immediately** (and it counts toward that account's **outgoing** total for `top_spenders`), then **schedule a cashback** of `floor(amount × 2%)` back to the **same account exactly 24 hours later** (`ts + MILLIS_PER_DAY`, `MILLIS_PER_DAY = 86_400_000`). Return a unique payment id `"payment1"`, `"payment2"`, … from a **global** counter (across all accounts, not per-account). Return `None` (or the spec's failure value) if the account is missing or has insufficient funds.
- `get_payment_status(ts, id, payment_id) -> str | None` — `"IN_PROGRESS"` before the cashback is applied, `"CASHBACK_RECEIVED"` after. Return `None` if the account doesn't exist, the `payment_id` is unknown, or the payment **doesn't belong to that account**.

> **The mechanic everyone gets wrong — lazy, time-ordered settlement.** Cashbacks are **not** applied by a background timer. They're applied **lazily at the start of every operation**: before doing anything at time `t`, drain all pending cashbacks whose payout time `≤ t`, **in payout-time order**, crediting each to its (current) owner. So a cashback due at `t = ts + 86_400_000` becomes visible to the *next* call at or after that time — including a `get_payment_status` / `get_balance` query, not just mutations. Implement pending cashbacks as a **min-heap keyed by payout time** and call a `_settle(t)` helper first in every public method.

> **Money & rounding:** integers only (no float). Cashback is **floored** (`amount * 2 // 100`) — a payment under 50 yields 0 cashback but still transitions to `CASHBACK_RECEIVED`. A cashback is an **inflow**, so it does **not** add to `outgoing`/`top_spenders`. The exact **delay, percent, rounding, and id format vary by variant** — confirm them from the worked examples before coding.

### L4 — Merge + history
- `merge_accounts(ts, id1, id2) -> bool` — combine two accounts (sum balances, sum outgoing totals, merge pending payments; reassign payment ids; `id2` is consumed).
- `get_balance(ts, id, time_at) -> int` — return the **balance at a past time** (`time_at ≤ ts`). Requires a balance history.

## Core approach (format-agnostic)

Two structural choices drive correctness. Make them at L1 and they pay off through L4.

**1. State**
```
account = {
  "balance": int,                # cents, NOT float
  "outgoing": int,               # total sent (for top_spenders)
  "history": [(ts, balance_after)],   # for get_balance
}
payments = { "paymentN": {"account": id, "refund": int, "done": bool} }  # global registry
```
Keep cashbacks in a **global** `payments` registry keyed by the `"paymentN"` id (not a per-account list) — `get_payment_status` looks up by id and checks the owner, and `merge` just reassigns the `account` field.

**2. Lazy event advance.** Before any public op at `ts`, **flush all scheduled cashbacks with `due ≤ ts`** from a min-heap `(due_ts, seq, payment_id)`. The `seq` breaks ties at identical timestamps deterministically; settling a payment credits its owner and marks it `done`.

For `get_balance(ts, id, time_at)`: keep a per-account `(ts, balance)` history (append on every balance change). At query time, binary-search for the largest entry with `ts ≤ time_at`. **This is the same primitive as Q01 / Q07** — reuse it.

For `merge`: combine balances, sum `outgoing`, **consolidate pending payments**, reassign ids to one namespace, delete the merged account.

### Worked Python solution (skeleton)

```python
import heapq

MILLIS_PER_DAY = 24 * 60 * 60 * 1000   # 86_400_000 — cashback lands 24h after the payment
CASHBACK_PERCENT = 2                    # 2% cashback, floored to an integer

class Bank:
    def __init__(self):
        self.accounts = {}             # id -> state dict
        self.pending = []              # min-heap of (due_ts, seq, pid)
        self.payments = {}             # "paymentN" -> {"account", "refund", "done"}
        self._seq = 0                  # deterministic heap tie-break
        self._npay = 0                 # global counter -> "payment1", "payment2", ...

    def _advance(self, ts):
        # Lazy, time-ordered settlement: credit every cashback due by `ts`.
        while self.pending and self.pending[0][0] <= ts:
            due, _, pid = heapq.heappop(self.pending)
            p = self.payments[pid]
            aid = p["account"]
            if aid in self.accounts and p["refund"]:   # owner may have merged away
                acc = self.accounts[aid]
                acc["balance"] += p["refund"]
                acc["history"].append((ts, acc["balance"]))
            p["done"] = True            # status -> CASHBACK_RECEIVED (even if refund==0)

    def _ensure(self, ts, id):
        self._advance(ts)
        if id not in self.accounts:
            return None
        return self.accounts[id]

    def create_account(self, ts, id):
        self._advance(ts)
        if id in self.accounts:
            return False
        self.accounts[id] = {"balance": 0, "outgoing": 0, "history": [(ts, 0)]}
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

    def pay(self, ts, id, amount):
        # Signature is exactly pay(ts, id, amount) — the grader calls it with 3 args.
        # The %, delay, and rounding are FIXED by the spec (constants), not parameters.
        acc = self._ensure(ts, id)
        if acc is None or amount <= 0 or acc["balance"] < amount:
            return None
        acc["balance"] -= amount
        acc["outgoing"] += amount                       # payment counts as outgoing
        acc["history"].append((ts, acc["balance"]))
        self._npay += 1
        pid = f"payment{self._npay}"                    # global id, not per-account
        refund = amount * CASHBACK_PERCENT // 100       # floored 2% (may be 0)
        self.payments[pid] = {"account": id, "refund": refund, "done": False}
        heapq.heappush(self.pending, (ts + MILLIS_PER_DAY, self._seq, pid))
        self._seq += 1
        return pid

    def get_payment_status(self, ts, id, pid):
        self._advance(ts)
        if id not in self.accounts:
            return None
        p = self.payments.get(pid)
        if p is None or p["account"] != id:            # unknown id or wrong owner
            return None
        return "CASHBACK_RECEIVED" if p["done"] else "IN_PROGRESS"

    def merge_accounts(self, ts, id1, id2):
        self._advance(ts)
        if id1 not in self.accounts or id2 not in self.accounts or id1 == id2:
            return False
        a, b = self.accounts[id1], self.accounts[id2]
        a["balance"] += b["balance"]
        a["outgoing"] += b["outgoing"]
        a["history"].extend(b["history"])
        a["history"].sort()
        for p in self.payments.values():   # pending cashbacks now credit id1
            if p["account"] == id2:
                p["account"] = id1
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
  - **Authorization holds (two-phase transfer)** — `hold(ts, id, amount) -> hold_id` reserves funds (available vs ledger balance split), then `capture`/`release`; the real card-payments model and a natural L5 — needs `available = balance − Σ holds`.
  - **Overdraft policy** — allow negative to a limit with fee event scheduled? Shows you treat "reject on insufficient funds" as a policy choice, not a law.
  - **Historical `top_spenders(ts, n, time_at)`** — ranking *as of a past time* needs outgoing history per account (same binary-search primitive as `get_balance`) — the composition interviewers escalate to.
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
# NOTE: trace uses a tiny delay D=5 in place of MILLIS_PER_DAY (86_400_000) purely
# for readability. In real code the cashback from pay@t=5 would land at t=86_400_005.
t=0  create_account("a1")           # a1: balance=0, history=[(0,0)]
t=1  create_account("a2")
t=2  deposit("a1", 100)              # a1: balance=100, history +=(2,100)
t=3  transfer("a1","a2",30)          # a1: 70, outgoing=30; a2: 30
t=5  pay("a1", 50)                   # a1: 20, outgoing=80; -> "payment1", cashback=1 due@t=5+D=10
t=8  deposit("a2", 10)               # settle first: cashback@10 not yet due → noop
t=10 deposit("a1", 5)                # settle fires: a1 +=1 → 21 (payment1 -> CASHBACK_RECEIVED); then deposit → 26
t=12 top_spenders(2)                 # a1: outgoing=80, a2: outgoing=0 → "a1(80), a2(0)"
t=15 get_balance(15,"a1", 5)         # hist: [(0,0),(2,100),(5,20),(10,21),(15,26)]
                                     # bisect ≤5 → (5,20) → 20
```

## Related
[[01-in-memory-key-value-database]] (sibling ICA, version-list primitive) · [[25-design-leaderboard]] (same `top_spenders` muscle) · [[05-expiring-credit-ledger]] (out-of-order variant) · Track C payment-ledger design.