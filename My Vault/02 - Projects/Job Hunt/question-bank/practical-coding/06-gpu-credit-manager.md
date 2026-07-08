---
title: GPU Credit Manager
slug: gpu-credit-manager
type: multi-level-stateful
leetcode: null
companies: [OpenAI, Anthropic, CoreWeave, Lambda, "AWS EC2 spot", "Together AI", "Replicate", "Modal"]
difficulty: ★★★★☆
frequency: medium
formats: [Live, Take-home]
levels: 3
time-box: live 45–60 min
time-box-take-home: 4–8 hours
tags: [oo-design, expiry, allocate-release, idempotency, reservation]
related: ["[[05-expiring-credit-ledger]]", "[[02-banking-system]]", "[[31-retry-with-backoff]]", "[[openai-interview-guide]]"]
---

# GPU Credit Manager

[[05-expiring-credit-ledger]]'s structure plus **reservation** semantics and **idempotency** — models metered GPU compute. Common at AI infra shops where every inference call needs a quota check before dispatch.

## Problem

Track per-user GPU credits with **two** concepts: *granted balance* (deposits with expiration) and *allocated* (reservations against the balance).

- `add_credit(user_id, amount, ts, expiration)` — add a credit grant.
- `allocate(user_id, amount, ts, request_id)` — reserve `amount` against the user's **available** (= balance − allocated) at `ts`. **Idempotent** on `request_id`: a repeated call returns the same result without double-charging.
- `release(user_id, amount, ts)` — return previously allocated credits.
- `available(user_id, ts)` — `balance − allocated` at `ts`.

**The headline follow-up is idempotency** — "what if the API call retries?" Network retries are the norm in distributed GPU scheduling; double-allocation would silently overdraw.

## Core approach (format-agnostic)

Reuse Q05's expiring-credit core (earliest-expiry-first, lazy replay). Layer two bookkeeping items on top:

1. **`allocated` counter** — sum of currently-reserved credits; deducted on `release`, refunded on TTL expiry of the allocation.
2. **`seen_requests: dict[request_id → result]`** — idempotency cache. `allocate` first checks `seen`. If present, return cached result. Otherwise compute, cache, return.

**TTL on allocations** — reservations should expire too. If a request reserves GPU but never releases, it should free after some timeout (e.g., 60s). This is a heap of `(expire_ts, request_id, amount)` advanced on each op.

### Worked Python solution

```python
import heapq

class GPUCreditManager:
    def __init__(self):
        self._events = []               # event log for lazy replay
        self._idx = 0
        self._seen = {}                 # request_id -> cached allocate result

    # ---------- writes ----------
    def add_credit(self, uid, amount, ts, expiration):
        self._idx += 1
        self._events.append((ts, self._idx, "add", (uid, amount, expiration)))

    def allocate(self, uid, amount, ts, request_id):
        # Idempotency
        if request_id in self._seen:
            return self._seen[request_id]
        # Lazy replay to compute state
        balance, allocated = self._replay(uid, ts)
        if balance - allocated >= amount:
            self._idx += 1
            self._events.append((ts, self._idx, "alloc", (uid, amount, request_id)))
            result = True
        else:
            result = False
        self._seen[request_id] = result
        return result

    def release(self, uid, amount, ts):
        self._idx += 1
        self._events.append((ts, self._idx, "release", (uid, amount)))

    def available(self, uid, ts):
        balance, allocated = self._replay(uid, ts)
        return balance - allocated

    # ---------- internal replay ----------
    def _replay(self, uid, ts):
        relevant = sorted(
            (e for e in self._events if e[0] <= ts),
            key=lambda e: (e[0], e[1]),
        )
        grants = []                     # (exp, remaining)
        allocated = 0
        for _, _, kind, payload in relevant:
            if kind == "add":
                u, amt, exp = payload
                if u != uid: continue
                if exp <= ts: continue
                heapq.heappush(grants, [exp, amt])
            elif kind == "alloc":
                u, amt, _rid = payload
                if u != uid: continue
                # consume earliest-expiring first
                rem_amt = amt
                while rem_amt > 0 and grants:
                    exp, left = grants[0]
                    if exp <= ts:
                        heapq.heappop(grants); continue
                    take = min(left, rem_amt)
                    grants[0][1] -= take
                    rem_amt -= take
                    if grants[0][1] == 0:
                        heapq.heappop(grants)
                allocated += (amt - rem_amt)
                # if rem_amt > 0, under-allocated (insufficient at this ts);
                # spec usually means allocate returns false in that case
            elif kind == "release":
                u, amt = payload
                if u != uid: continue
                allocated = max(0, allocated - amt)
        balance = sum(rem for _, rem in grants)
        return balance, allocated
```

**Complexity.** `add_credit` O(1). `allocate` O(N log G) where N is events for the user and G is grants — bounded in practice; consider per-user event compaction. `release` O(1) plus replay. `available` O(N log G).

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** builds on Q05; the headline follow-up is **idempotency**.
- **Follow-ups (real, reported):**
  - **Partial allocation** — what if user has 7 credits but requests 10? Reject? Allocate 7?
  - **Priority / fairness** — across users: when GPU is scarce, who gets priority? FIFO? Tier-based?
  - **TTL on reservations** — allocation expires if not used in N seconds; heap-driven.
  - **Distributed counter** — multi-node deployment; consistency story (leader-elected counter, CRDT, etc.). → Track C.
  - **Per-region budgets** — credits pinned to a region; cross-region allocation requires conversion.
  - **Burst / burstable quotas** — allow 2× the steady-state for short windows.
  - **Same request_id, different args** — retry with `("r1", 50)` after `("r1", 30)`: cached-result blindly returned is wrong → idempotency key must bind the full request fingerprint; mismatch = error, not replay. The subtle idempotency probe.
  - **allocate → use → release lifecycle** — split reservation from consumption (`commit(request_id)` converts allocated → spent); models real GPU billing (reserve at enqueue, bill at completion) and forces a 3-state machine.
- **Tips:**
  - Implement idempotency with a `request_id → result` map and **narrate why** (network retries).
  - Separate `allocated` from `balance` in your data model — easy to conflate.
  - For TTL on allocations: same heap + lazy-advance pattern as Q02 cashbacks.
  - Mention integer cents / integer units for money.
- **Pitfalls:**
  - **Double-charging on retry** — the bug the question is designed to surface.
  - **Releasing more than allocated** — guard with `max(0, allocated - amount)`.
  - **Allocating against soon-to-expire credit** — confirm policy (consume earliest-expiring is usually right).
  - **Idempotency cache never expires** — bounded LRU or TTL on the cache.
  - **Replay skipping future events** — events with `ts > query_ts` must not affect state.

### Take-home / work-trial
- **Tips:**
  - Ship idempotency + a retry test in the repo.
  - README the reservation accounting, replay strategy, and TTL-on-alloc.
  - Provide an in-memory persistence option (append event log to file, reload on startup).
- **Pitfalls:**
  - Non-idempotent allocate → silent overdraw on retry.
  - Race between allocate/release (note the locking story; even single-threaded, ordering matters).
  - Unbounded event log → memory pressure; document compaction.

## Company variants

- **OpenAI (canonical)** — "Problem 5" in their bank.
- **Anthropic / CoreWeave / Lambda / Together / Replicate / Modal** — metered GPU APIs with reservation semantics; idempotency is non-negotiable.
- **AWS EC2 spot** — reskin with reservation IDs.

## Worked example trace

```
add_credit("u1", 100, 0, 100)          # grant1: exp=100
allocate("u1", 30, 5, "r1")            # ok; cached as True
allocate("u1", 30, 5, "r1")            # idempotent → True (no double-charge)
allocate("u1", 80, 6, "r2")            # available = 100 - 30 = 70 → False
release("u1", 30, 10)                  # allocated = 0
available("u1", 10) → 100
```

## Related
[[05-expiring-credit-ledger]] (base) · [[31-retry-with-backoff]] (idempotency story) · [[02-banking-system]] (time-ordered sibling) · Track C distributed-counter / rate-limiter design.