---
title: "Configuration Management (etcd / ZooKeeper-backed)"
slug: configuration-management
type: distributed-system-design
tier: "2 — Coordination & control plane"
companies: [etcd, Consul, ZooKeeper, Kubernetes, Spring Cloud Config, AWS AppConfig, Facebook]
difficulty: ★★★☆☆
frequency: medium
formats: [Onsite·SD, Mock]
time-box: 25–35 min
tags: [config, etcd, zookeeper, watch, versioned, feature-flags, dynamic-config]
related: ["[[11-service-discovery-registry]]", "[[09-consensus-leader-election]]", "[[04-distributed-lock-service]]"]
companies-likely: [Kubernetes shops, Spring Cloud, etcd users, Consul users]
---

# Configuration Management (etcd / ZooKeeper-backed)

**One-liner:** A strongly-consistent, versioned KV store for shared configuration and feature flags, with watch-based change notifications and fast convergence across a fleet.

## Problem framing

Asked at any microservices shop that needs dynamic config without redeploys, or when the interviewer wants to test your grasp of **watch semantics** (not just get/put). Variants: "Design etcd / Consul KV", "Design a feature-flag service", "Design Spring Cloud Config".

**Variants:**
- "Design a centralized config service" (general)
- "Design etcd / ZooKeeper" (the underlying primitive)
- "Design a feature-flag service" (LaunchDarkly / Split-style)
- "Design dynamic config for a microservices fleet" (1k services, 10k instances)

## Requirements (clarify first)

- **Functional:** `get(key) → {value, version}`, `put(key, value)`, `delete(key)`, `watch(key) → stream of changes`, `cas(key, expected_version, new_value)`.
- **Non-functional:**
  - **Strongly consistent** reads (linearizable).
  - Watch latency: change visible to subscribers in < 100ms.
  - Throughput: 10k reads/s, 1k writes/s.
  - Durability: zero data loss.
- **Constraints:** key/value size (small / 1MB), number of keys (10k / 1M), churn rate.
- **Out of scope:** access control (mention), audit log (variant).

## Capacity estimation

- 100k keys × 1KB = 100MB. Fits in RAM.
- 10k watches active; each fires on a change → O(100) subscribers per key max.
- Write traffic is low — config changes are rare. Reads are high — every service instance reads config on boot.

## High-level architecture

```
Config service API (REST / gRPC)
        │
        ▼
   Strongly-consistent KV (etcd / ZooKeeper)
   ├── Raft / Zab consensus
   ├── WAL + snapshot
   └── Watch manager (tracks active subscribers)
        │
        ├──► Client SDK (long-poll watch)
        ├──► Service A (caches, subscribes)
        ├──► Service B (caches, subscribes)
        └──► Service C (caches, subscribes)
```

## API / interfaces

```
GET /v1/config/{key}
→ { "value": "...", "version": 42, "modified_ts": ... }

PUT /v1/config/{key}
{ "value": "...", "expected_version": 42 }   # CAS
→ { "version": 43 } | 409 Conflict

DELETE /v1/config/{key}
→ 204

GET /v1/config/{key}/watch?since=42
→ SSE / long-poll stream of changes (each event: key, new_version, value)
```

## Deep dive #1 — Consistency, version, CAS

**Why strong consistency?**
- Two ops teams flipping the same flag should not overwrite each other silently.
- Bootstrap race: 1000 service instances starting at once read the same config — they must see the same value.
- Linearizable reads = the only way to be sure.

**Versioned values:**
- Every write bumps a monotonically-increasing version (cluster-wide or per-key).
- Read returns `(value, version)`.
- Write uses CAS: `put(key, value, expected_version)`. If version moved, reject.
- This is the primitive that makes "compare-and-set" feature-flag updates safe.

**Watch semantics:**
- Client opens a long-lived connection (long-poll HTTP, gRPC stream, WebSocket).
- Server holds the connection open; on a key change (or a prefix change), notifies subscribers.
- Client receives `version` and `value`; refreshes local cache.
- Resumable: client passes `since=version` to resume from a known point.

**Hierarchical keys:**
- ZooKeeper: tree structure (`/services/checkout/replicas`).
- etcd: flat keys with `/` separators (convention).
- Allow prefix watches (`/services/checkout/*`) for bulk subscriptions.

## Deep dive #2 — Failure modes & operations

**Watch storm:** a popular key changes → 10k clients reconnect to fetch. Mitigations:
- Server-side debounce / coalesce (notify subscribers every 100ms max, even if changes are more frequent).
- Client-side throttling (max 1 refresh per 5s for the same key).

**Split-brain / stale reads:** if a client reads from a non-leader, it might see stale data. Solution: linearizable reads always go through the leader (or read-index protocol).

**Slow consumer:** a subscriber is slow to ack → its watch connection lags → server may close. Mitigations: backpressure, snapshot at watch resume.

**Multi-DC config:**
- Async replication across DCs (eventual consistency for config is usually fine).
- Per-DC overrides: `config/global + config/dc-local`.

**Schema:**
- Validate at write (JSON Schema / Protobuf).
- Versioned config: `config.v1`, `config.v2` — services opt in.

**Feature flags:**
- Targeting rules (user_id, tenant_id, percentage rollout).
- Cached at client; SDK evaluates locally for performance.
- Server records the flag *definition* + *targeting*; client evaluates per request.

## Scale & bottlenecks

- **Key hot-spot:** one key watched by 10k services. Coalesce notifications.
- **Watch leaks:** clients disconnect ungracefully → server holds the watch forever. Mitigate: server-side timeout on idle watches.
- **Snapshot on resume:** a client resuming after 1h needs the current state. Server provides `get` + `watch_since_version` to rebuild.
- **Cold start:** 10k instances boot simultaneously, all read the same config → thundering herd. Mitigate: edge cache, hierarchical config (cluster → region → service).

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Consensus node down | Reduced quorum | 3-5 nodes; tolerates 1-2 failures |
| Watch connection drops | Client uses stale config | Reconnect + resume from `since_version` |
| Slow client | Watch backpressure | Server times out + closes; client retries |
| Schema invalid | Bad config deployed | Validation at write; canary / staged rollout |
| Network partition | Client can't reach config | Local cache; fail safe (default config) |

## "What I'd build first and why"

**A small Raft-backed KV (etcd model) with linearizable reads + watch streams + CAS writes.** Client SDK caches with TTL + invalidates on watch. Add feature-flag targeting later (most flag services start as plain KV).

The single highest-leverage thing is the **CAS primitive** — it makes flag updates safe under contention, which is the #1 operational pain point.

## Follow-ups (real, reported)

1. **etcd vs ZooKeeper** — implementation differences (lease vs session; tree vs flat).
2. **CAS for safe flag updates** — derive the conflict scenario.
3. **Watch storm** — coalesce + throttle; how Netflix did it.
4. **Long-poll vs streaming** — HTTP/1.1 long-poll vs SSE vs gRPC stream vs WebSocket.
5. **Hierarchical keys** — prefix watches; tree traversal.
6. **Feature-flag targeting** — user_id, percentage rollout, custom rules.
7. **Cold-start optimization** — edge cache + hierarchical config.
8. **Audit log** — who changed what when.
9. **Schema validation** — JSON Schema / Protobuf at write.
10. **Multi-DC** — async replication + per-DC overrides.

## Tips (staff-level)

- **Name etcd or ZooKeeper explicitly.** Show you know how the substrate works (Raft/Zab).
- **Talk about CAS.** Version + expected_version is the most important primitive.
- **Watch storm mitigation.** Coalesce + throttle. Concrete.
- **Feature flags layered on top.** Most "config services" are flag services underneath.
- **Quantify:** "100k keys, 10k watches, 10k reads/s, 1k writes/s — fits in a 3-node etcd cluster".

## Pitfalls

- **"Just use a regular DB".** Misses the watch primitive — that's the value.
- **No versioning.** Concurrent flag updates race; last-write-wins = surprise.
- **No CAS.** Same.
- **Polling instead of watching.** Wasteful, slow, doesn't scale.
- **No coalescing on watch storms.** Brief config changes DDoS the server.

## Worked narration (2 min)

"Goal: 100k config keys, 10k microservices instances, watch-based change notifications in < 100ms, safe concurrent updates.

**Substrate:** 3-node etcd cluster, Raft consensus, linearizable reads, MVCC store.

**API:** `get`/`put`/`delete` + `watch(key, since_version) → stream of changes`. All writes use CAS with expected_version.

**Watch:** long-poll HTTP / gRPC stream. Server coalesces events (notify max every 100ms) to avoid storm. Client SDK caches and invalidates on event.

**Feature flags:** targeting rules stored as config; SDK evaluates per-request (cached locally for hot flags).

**Failure:** etcd node down → leader re-elected in ~1s. Watch dropped → client reconnects + resumes from `since_version`. Watch storm → coalesce + throttle.

**First build:** etcd + CAS + watch streams + SDK cache. Add targeting rules, audit log, schema validation as workloads demand."

## Related

- [[11-service-discovery-registry]] — same substrate, different use case.
- [[09-consensus-leader-election]] — Raft is the inner loop.
- [[04-distributed-lock-service]] — locks often implemented on top of etcd.
- [[38-distributed-tracing]] — config drives sampling rules for tracing.