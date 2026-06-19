---
title: "Distributed Lock Service"
slug: distributed-lock-service
type: distributed-system-design
tier: "1 — Core data stores & consistency"
companies: [Redis, ZooKeeper, etcd, Google Chubby, AWS, Stripe, Robinhood, "any infra"]
difficulty: ★★★☆☆
frequency: high
formats: [Onsite·SD, Whiteboard]
time-box: 25–35 min
tags: [lock, consensus, redis, zookeeper, etcd, fencing]
related: ["[[01-distributed-kv-cache]]", "[[09-consensus-leader-election]]", "[[02-rate-limiter]]"]
companies-likely: [Redis, ZooKeeper, etcd, Google, Stripe, Robinhood, Confluent]
---

# Distributed Lock Service

**One-liner:** A coordination primitive that gives *one* client exclusive ownership of a resource across a fleet, with correctness under network partitions and process pauses.

## Problem framing

Asked when the interviewer wants to test your grasp of consensus, fencing, and the limits of "naive" implementations. Common at infra / platform / fintech shops. The killer answer involves Martin Kleppmann's fencing tokens — most candidates miss it.

**Variants:**
- "Design a distributed lock service" (general)
- "Design Redlock" (Redis-specific — and controversial)
- "Design Chubby / ZooKeeper locks" (consensus-based)
- "Mutex for a leader-election primitive"

## Requirements (clarify first)

- **Functional:** `acquire(resource, ttl)` → lock handle; `release(handle)`; `renew(handle)` to extend TTL.
- **Non-functional:**
  - **Mutual exclusion:** at most one client holds the lock at any time (the *correctness* property).
  - **Liveness:** if the holder dies, the lock is eventually released.
  - **Availability:** can tolerate N failures.
- **Constraints:** lock granularity (single resource / range / hierarchical), TTL (1s for short tasks / 1m for batch jobs).
- **Out of scope:** read/write locks (single-writer is enough).

## Capacity estimation

- 10k locks/s acquisition rate, average hold 30s → 300k active locks.
- Each lock = ~100B (resource + holder + ttl + fencing token). 30MB total. Trivial.
- Real bottleneck: latency of the *consensus* under contention, not memory.

## High-level architecture

```
Client A ─┐                                            ┌─► Acquire ok (token=42)
Client B ─┼──► Lock service (5-node quorum)            │
Client C ─┘    │                                       └─► Acquire fail (held)
                ├──► Consensus (Raft / Paxos)
                ├──► State machine: locks{resource → (holder, token, ttl)}
                └──► Watch / notify (ZooKeeper-style)
```

Two design philosophies:
1. **Consensus-based (ZooKeeper / etcd / Chubby):** correctness via Raft; ~10ms acquire latency.
2. **Quorum-based (Redlock):** cheaper (5-10ms) but has correctness holes Kleppmann famously pointed out.

## API / interfaces

```
POST /v1/lock/acquire
{ "resource": "order:1234", "ttl_s": 30 }
→ { "lock_id": "L-abc", "fencing_token": 42, "expires_at": 1718721630 }

POST /v1/lock/renew
{ "lock_id": "L-abc", "ttl_s": 30 }
→ { "expires_at": 1718721660 } | 410 Gone

POST /v1/lock/release
{ "lock_id": "L-abc" }
→ 204 | 409 Conflict
```

## Deep dive #1 — Correctness: fencing tokens are non-negotiable

**The naive failure:** client acquires lock, gets paused (GC / network), lock TTL expires, another client acquires the lock, first client wakes up and writes. **Two clients think they hold the lock.**

**The fix: fencing tokens.** Every acquire returns a monotonically-increasing token. The resource (DB / KV / whatever the lock protects) checks the token and rejects stale writes.

```
Client A: acquire → token=42, ttl=10s
Client A: GC paused for 20s (lock expired)
Client B: acquire → token=43
Client B: write(record, token=43) → accepted
Client A: wakes up, write(record, token=42) → REJECTED (token < current)
```

**This is the answer.** Kleppmann's "How to do distributed locking" — every interviewer who knows distributed locking knows this. Mention it before they ask.

## Deep dive #2 — Implementations

**Redis (Redlock, controversial):**
- N=5 independent Redis masters.
- Acquire: set key with `NX PX ttl` on majority (≥ N/2 + 1) within a time budget.
- **Problem:** relies on synchronized clocks (for TTL); GC pauses + clock drift = silent violation of mutual exclusion.
- Antirez's response: clock drift is bounded, GC pauses can be mitigated.
- **Verdict:** fine for *efficiency* (don't do the same work twice), **not safe for *correctness*** (don't protect a non-idempotent resource).

**ZooKeeper / etcd / Chubby (consensus-based, the right answer):**
- 3-5 node ensemble, Raft/Zab consensus.
- Locks are *sequential ephemeral znode* (ZooKeeper) or *lease with revision* (etcd).
- Acquire: create ephemeral znode with sequence; you hold the lock if your znode is the lowest sequence.
- Watch the next-lowest znode for release notification.
- TTL via session; session timeout triggers ephemeral node deletion.
- **Linearizable, correct, ~10ms latency.**

**Lease-based (Chubby):**
- Master holds a lease, cached on clients. Cache + keepalive; on cache miss, re-acquire.
- Fencing tokens built in.

## Scale & bottlenecks

- **Hot lock:** every request for resource X takes the same lock. Mitigation: sharded locks (e.g. `order:1234` → `order_bucket:1`), or optimistic concurrency if the protected resource supports CAS.
- **Lock holder slowness:** TTL too short → expires mid-work; too long → long recovery from crashes. Tune to p99 of the work.
- **Quorum / ensemble under partition:** minority partition can't acquire; clients get errors. Standard Raft behavior.
- **ZooKeeper herd effect:** "all watchers wake on the same znode deletion" solved by `zxid`-ordered watchers; clients only re-check when their predecessor changes.

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Holder GC pause | Lock expires while "holding" | **Fencing tokens** (mandatory) |
| Network partition | Both sides think they have the lock | Quorum (only majority acquires) |
| Clock skew (Redlock) | TTL misjudged | Use monotonic clocks + bounded skew |
| Session timeout | Ephemeral znode deleted → lock lost | Heartbeat with safety margin (TTL/3) |
| Split brain | Two leaders both hold a lock | Linearizable consensus (Raft/Zab) |

## "What I'd build first and why"

**Consensus-based lease + fencing tokens.** ZooKeeper or etcd as the substrate. Every protected resource enforces the fencing token on write. Acquire is ~10ms, fine for >99% of workloads.

The single highest-leverage thing is naming the **fencing token** — it's the difference between a junior answer and a staff answer.

## Follow-ups (real, reported)

1. **Redlock correctness debate** — name it; say you'd use ZooKeeper for correctness, Redlock only for efficiency.
2. **Fencing tokens** — derive the GC-pause scenario; show how a token prevents the violation.
3. **Lease vs lock** — Chubby uses leases; talk about caching + keepalive.
4. **Herding** — ZooKeeper watch storm on lock release; how to mitigate.
5. **Hierarchical locks** — ZooKeeper's tree structure; lock a subtree.
6. **Read/write locks** — single-writer vs many-readers.
7. **Fairness** — FIFO acquisition (znode sequence gives this for free in ZooKeeper).
8. **Lock vs compare-and-swap** — when CAS on the resource itself is the better answer.
9. **Process pause** — the Kleppmann "stop-the-world GC" example.
10. **Cross-region locking** — consensus across regions = high latency; usually a regional lock + cross-region reconciliation.

## Tips (staff-level)

- **Name fencing tokens first.** Don't wait to be asked.
- **Distinguish correctness vs efficiency locks.** Most candidates blur this.
- **Acknowledge Redlock is controversial.** Saying "Redlock is fine" is a yellow flag; saying "Redlock has known issues, here's how I'd mitigate" is a green flag.
- **Quantify:** "10k locks/s, 30s hold = 300k active, ~30MB state, fits in 3-node ensemble".
- **Show you've run into GC pauses.** Real ops experience.

## Pitfalls

- **No fencing token.** Lock + unprotected resource = data corruption waiting to happen.
- **TTL too long.** Recovery from a dead holder is slow.
- **TTL too short.** Lock expires mid-work.
- **Synchronized clocks assumed** without verifying.
- **Not testing for clock skew** — set up a chaos test.

## Worked narration (2 min)

"Goal: exclusive access to a resource across 1000 app servers, correct under GC pauses and partitions.

**Substrate:** etcd (or ZooKeeper) — 3-node Raft ensemble, ~10ms acquire latency.

**API:** `acquire(resource, ttl) → {lock_id, fencing_token, expires_at}`. Every protected write checks the token; storage layer rejects stale tokens.

**Why fencing:** a client can be paused (GC, network) past TTL — when it wakes, it doesn't hold the lock anymore. Token prevents stale writes.

**Why not Redlock:** known issues with clock drift + GC pauses. Fine for 'don't process twice' (efficiency), unsafe for 'don't corrupt data' (correctness).

**Failure:** holder dies → session expires → ephemeral znode deleted → next waiter gets the lock. Network partition → only majority acquires.

**First build:** etcd-backed leases with fencing tokens. Tune TTL to p99 of the work, retry budget = TTL/3."

## Related

- [[01-distributed-kv-cache]] — consensus is the inner loop.
- [[09-consensus-leader-election]] — Raft / Paxos is the same primitive.
- [[02-rate-limiter]] — same distributed-counter problem in disguise.
- [[10-job-scheduler-task-queue]] — locks used to claim work units.