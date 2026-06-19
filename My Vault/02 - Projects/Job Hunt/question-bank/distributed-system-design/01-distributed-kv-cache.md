---
title: "Distributed KV Store / Cache"
slug: distributed-kv-cache
type: distributed-system-design
tier: "1 — Core data stores & consistency"
companies: [Google, NVIDIA, Meta, Stripe, Robinhood, Cache, Redis, Memcached]
difficulty: ★★★☆☆
frequency: very-high
formats: [Onsite·SD, Phone·SD, Mock]
time-box: 35–45 min
tags: [kv, cache, consistency, partitioning, replication, eviction, cap-theorem]
related: ["[[02-rate-limiter]]", "[[03-distributed-message-queue-pubsub]]", "[[09-consensus-leader-election]]"]
companies-likely: [Google, NVIDIA, Meta, Stripe, Robinhood, Cloudflare]
star: true
---

# Distributed KV Store / Cache

**One-liner:** A horizontally-scalable, low-latency key-value store with tunable consistency, partitioning, replication, and eviction — the canonical distributed-systems design question.

## Problem framing

Most-asked distributed systems design question at FAANG staff level. The interviewer wants to see that you understand the *fundamentals* (CAP, partitioning, replication, consistency models, eviction) and can apply them to a concrete design with explicit tradeoffs.

**Variants the interviewer might ask:**
- "Design Redis / Memcached" (cache-flavored)
- "Design a distributed cache for a web tier" (cache-aside)
- "Design a persistent KV store like DynamoDB / Cassandra / Bigtable" (storage-flavored)
- "Design a session store" (TTL + replication)

## Requirements (clarify first)

- **Functional:** `get(key)`, `put(key, value, ttl?)`, `delete(key)`, optional `scan`/`range_query`.
- **Non-functional:**
  - Latency target: p99 < 1ms (cache), < 10ms (persistent KV)
  - Throughput: 100k–1M ops/sec/shard
  - Availability: 99.99% (cache) / 99.999% (persistent)
  - Durability: zero (cache) / "no data loss" (persistent)
- **Constraints:** item size (1KB cache / 1MB KV), key cardinality (10M / 1B / 100B), value size distribution.
- **Out of scope:** transactions, secondary indexes (mention as a variant), full-text search.

## Capacity estimation

- 1B keys × 1KB = 1TB working set (cache) → need ~2TB with replicas.
- 100B keys × 4KB = 400TB (persistent KV) → can't fit in memory, must disk + caching tier.
- 1M QPS → 1k shards × 1k QPS each, or 100 shards × 10k QPS each (depends on shard granularity).
- Replication factor 3 → 3× storage and 3× write traffic.

## High-level architecture

```
client ──► Coordinator (stateless, consistent-hash ring lookup)
            │  route to N replicas (preference list)
            ├──► Shard A1 / A2 / A3   (one is coordinator/leader per op)
            ├──► Shard B1 / B2 / B3
            └──► Shard C1 / C2 / C3
                                      │
                                      ▼
                              Storage engine (LSM / B-Tree / in-mem)
                                      │
                                      ▼
                              Replication + WAL + snapshots
```

- **Coordinator:** stateless nodes that route by consistent hashing. ~10s of nodes behind a L4 LB.
- **Shards:** the unit of partitioning and replication. Each shard is a Raft/Paxos group of 3–5 replicas.
- **Storage engine:** LSM (write-heavy, RocksDB-style) for persistent; hash+skip-list (Redis-style) for cache.

## API / interfaces

```
GET /v1/kv/{key}                    → {value, version, cas_token} | 404
PUT /v1/kv/{key}  {value, ttl?}     → {version, cas_token}
DELETE /v1/kv/{key}                 → 204
CAS  /v1/kv/{key}  {value, cas}     → {version} | 409 conflict
```

## Deep dive #1 — Partitioning & replication

**Consistent hashing** (with virtual nodes / vnodes) partitions the keyspace. Each key maps to a position on a 64-bit ring; each shard owns a contiguous range. vnodes (e.g. 256 per shard) rebalance smoothly when shards are added/removed.

**Replication:** each key has a *preference list* of N replicas (e.g. N=3) chosen by walking clockwise from the key's position on the ring, skipping nodes in the same failure domain (rack/zone/region). One replica is the **coordinator** for the op; the others are followers.

**Quorum reads/writes:**
- N = 3, R = 2, W = 2 → strong consistency (W + R > N).
- N = 3, R = 1, W = 1 → eventual consistency, low latency.
- **Sloppy quorum** (Cassandra-style): if the coordinator can't reach its preference list (e.g. all down), writes go to the *next* healthy node ("hinted handoff"), and reconciliation happens later.
- **Read repair:** on a read, if replicas disagree, fix the stale ones in the background.
- **Anti-entropy (Merkle trees):** background process per shard that hashes each key range and reconciles divergent replicas.

**Tradeoff to name out loud:** strong consistency = latency + availability tax. The classic DynamoDB / Cassandra choice is *eventual* + tunable per-query (R/W/N).

## Deep dive #2 — Consistency, eviction, failure

**Consistency models:**
- **Linearizable:** every op appears to take effect atomically at some point between invocation and response. Required for locks, leader election.
- **Sequential:** all ops appear in some total order consistent with each client's order.
- **Causal:** causally-related ops are ordered; concurrent ops may interleave. Cheaper.
- **Eventual:** if writes stop, all replicas converge. Cheapest.

**Eviction (cache only):**
- **LRU:** doubly-linked list + hashmap. O(1) get/put. ~Redis default.
- **LFU:** counter-based, decay over time. Better hit rate for skewed workloads.
- **TinyLFU / W-TinyLFU:** Caffeine's design — small window of admission + frequency sketch.
- **ARC / CAR:** adaptive between recency and frequency.
- **TTL:** always support; most production caches evict by TTL > LRU.

**Failure handling:**
- **Hinted handoff:** if a replica is down, write to the next node with a *hint*; replay when the original comes back. Bounded queue (e.g. 1h).
- **Merkle-tree anti-entropy:** periodic sync to fix long-term drift.
- **Gossip:** membership + failure detection (φ-accrual / SWIM). ~10s detection time.
- **Split-brain:** use a quorum (R/W) so minority partition can't accept writes.

## Scale & bottlenecks

- **Coordinator hot spot:** one key / one shard takes most traffic (celebrity problem). Mitigate: cache at edge, replicate hot keys to many shards ("hot shard" detection + read-spread).
- **Replication lag:** followers fall behind on heavy write. Detect via version vector on read.
- **Rebalance cost:** adding a node requires streaming N×key_range to it. Throttle + prioritize based on load (Dynamo-style "load-aware rebalancing").
- **Compaction:** LSM compaction stalls writes. Tiered vs leveled; size-tiered for write-heavy, leveled for read-heavy.

## Failure modes & mitigations

| Failure | Detection | Mitigation |
|---|---|---|
| Replica crash | gossip / heartbeat | Hinted handoff + Raft leader re-election |
| Network partition | timeout-based | Quorum (W + R > N) — minority rejects writes |
| Slow replica | percentile tracking | R = fast_quorum (e.g. R = N-1, oldest first) |
| Shard hot-spot | per-shard QPS monitoring | Cache at edge + read-spread for hot keys |
| Corrupt data | checksum on read + Merkle diff | Restore from snapshot; re-replicate |
| Clock skew | NTP / TrueTime | Logical clocks (vector / hybrid) where order matters |

## "What I'd build first and why"

A **stateless coordinator + 3-replica consistent-hash shards** with **R/W tunable** (default R=1, W=1 for cache; W=2, R=2 for persistent). Storage is **LSM** if persistent, **in-memory hash+linked-list** if cache. Start simple — strong consistency only for explicit needs, default to eventual + read-repair.

The single highest-leverage thing is choosing **R/W/N to match the workload** — most candidates fixate on partition strategy and ignore the consistency knob.

## Follow-ups (real, reported)

1. **Consistency vs availability** — name a workload where you'd pick CP and one where you'd pick AP. (Lock service: CP. Shopping cart: AP.)
2. **Cache stampede** — popular key expires and 1k clients race to refill. Mitigations: request coalescing, early refresh (XFetch), probabilistic early expiration.
3. **Hot key handling** — one key gets 50% of traffic (product launch). Read-spread / cache at edge / dedicated shard.
4. **Eviction policy choice** — when LRU vs LFU vs TinyLFU. (Skewed: LFU. Steady: LRU. Mixed: ARC.)
5. **Replication factor choice** — 2 vs 3 vs 5. (Cost vs availability; RF=3 is the sweet spot.)
6. **Range queries** — how do they work on a consistent-hash partition? (Partition by key range, not hash; or maintain a secondary index.)
7. **TTL semantics** — absolute vs sliding. (Sliding TTL on every read is expensive — most use absolute + manual refresh.)
8. **Read-your-writes** — client wants to read what they just wrote across regions. (Sticky routing by session, or read from local replica + version check.)
9. **Snapshot isolation** — for backup / point-in-time reads.
10. **Cross-region replication** — async vs sync; conflict resolution (LWW vs vector clocks vs CRDTs).

## Tips (staff-level)

- **Lead with CAP**, then say "for *this* workload I'd pick AP because…". Saying CAP without picking a side is a yellow flag.
- **Quantify:** "1B keys × 1KB = 1TB, 3× replicas = 3TB, fits in one rack of 12× 256GB boxes = $X".
- **Name the algorithms:** consistent hashing with vnodes, Raft for replication, gossip for membership. Don't hand-wave.
- **Tell the interviewer what you'd skip:** "I'm not designing transactions / secondary indexes in v1 — flag them as variants".
- **Staff signal: failure modes table.** Sketch it on the whiteboard. Shows you've run systems, not just designed them.

## Pitfalls

- **"Use Redis" as the whole answer.** Redis is one node. The question is *distributed* — what do you do when you need 10TB?
- **Ignoring consistency.** Talking about partitioning without naming R/W/N is a common miss.
- **Forgetting failure modes.** Most candidates skip partition behavior. Bring it up yourself.
- **Choosing LSM without explaining why.** LSM is great for writes, terrible for range scans. Say which your workload needs.

## Worked narration (3 min)

"Goal: 1B keys, 1KB each, p99 < 5ms, 100k QPS, 99.99% available. CAP: pick **AP** — losing the cache is worse than staleness for this workload.

**Architecture:** stateless coordinators front consistent-hash shards, each shard is a 3-replica Raft group, in-memory hash+linked-list for the cache tier, LSM if persistent.

**Consistency:** default R=1, W=1; offer R=2, W=2 for keys the app tags strong. Quorum covers network partitions — minority partition rejects writes.

**Hot keys:** cache popular reads at the edge (CDN / per-app-process LRU), and if one shard still melts, read-spread by replicating the key across N shards and load-balancing reads.

**Failure:** hinted handoff for short outages, Merkle-tree anti-entropy for long, gossip for membership.

**First build:** coordinator + 3-replica shards with R/W/N tunable. Don't start with transactions or indexes — wait for the use case."

## Related

- [[02-rate-limiter]] — both have the "distributed counter" question lurking inside.
- [[03-distributed-message-queue-pubsub]] — durability + ordering live there.
- [[09-consensus-leader-election]] — Raft is the inner loop of replication.
- [[08-wide-column-store]] — DynamoDB / Cassandra *are* this design with extra features.