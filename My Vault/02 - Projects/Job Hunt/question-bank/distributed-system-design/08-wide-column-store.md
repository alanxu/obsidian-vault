---
title: "Wide-Column Store (Cassandra / Bigtable)"
slug: wide-column-store
type: distributed-system-design
tier: "1 — Core data stores & consistency"
companies: [Cassandra, ScyllaDB, Google Bigtable, Apache HBase, AWS DynamoDB, Netflix, Apple]
difficulty: ★★★☆☆
frequency: medium-high
formats: [Onsite·SD, Mock]
time-box: 30–40 min
tags: [wide-column, cassandra, bigtable, dynamodb, lsm, eventually-consistent]
related: ["[[01-distributed-kv-cache]]", "[[03-distributed-message-queue-pubsub]]", "[[09-consensus-leader-election]]"]
companies-likely: [Netflix, Apple, Instagram, Cassandra shops, DynamoDB users]
---

# Wide-Column Store (Cassandra / Bigtable)

**One-liner:** A partitioned, eventually-consistent, write-optimized store that scales linearly by adding nodes, with a sorted key range per partition and tunable consistency per query.

## Problem framing

Asked at shops using Cassandra, Bigtable, HBase, or DynamoDB — and increasingly in interviews where the interviewer wants to see that you can scale a write-heavy workload horizontally without sharding by hand. Variants: "Design Cassandra", "Design Bigtable", "Design DynamoDB".

**Variants:**
- "Design Cassandra" (eventually-consistent, peer-to-peer)
- "Design Bigtable" (singleton master + tablets)
- "Design DynamoDB" (managed, single-digit-ms latency)
- "Design a message inbox at Instagram scale" (Cassandra in anger)

## Requirements (clarify first)

- **Functional:** `put(row_key, column_family, columns)`, `get(row_key)`, `range(row_start, row_end)`, secondary indexes.
- **Non-functional:**
  - Linear scalability: 2× nodes = ~2× throughput.
  - Latency: p99 < 10ms for point reads/writes.
  - Write throughput: 1M writes/s/node × 100 nodes = 100M writes/s.
  - Availability: 99.99% — no single point of failure.
- **Constraints:** row size (small / megabyte), partition size (< 100MB ideally), consistency requirement (tunable).
- **Out of scope:** transactions (mention as variant), joins.

## Capacity estimation

- 10TB working set on 100 nodes × 100GB. Add a node → rebalance → +1TB.
- 1M writes/s × 1KB = 1GB/s ingest.
- Row range scan: 10M rows in a partition × 1KB = 10GB. **Partition size limit ~100MB** is the classic footgun.

## High-level architecture (Cassandra-style)

```
Client ──► Coordinator node (any node can coordinate)
              │
              ├──► Token ring: hash(key) → node (consistent hash with vnodes)
              ├──► Replica nodes (N=3, by snitch: rack/zone aware)
              └──► Local storage engine: LSM tree + memtable + SSTables
```

**No master.** Every node is symmetric; any node can coordinate a read/write. Gossip for membership; failure detection via φ-accrual.

## API / interfaces (CQL-ish)

```
INSERT INTO events (bucket, ts, event_id, payload) 
VALUES ('2026-06-18', 1718721600, 'e-123', '...');

SELECT * FROM events 
WHERE bucket = '2026-06-18' AND ts > 1718721600 
LIMIT 100;
```

## Deep dive #1 — Storage engine: LSM tree

**Write path:**
1. Write to **commit log** (WAL on disk, sequential, fsync).
2. Write to **memtable** (in-memory sorted structure, typically skip list or B-tree).
3. When memtable fills → flush to immutable **SSTable** on disk.

**SSTable:** sorted (key, value, timestamp) pairs, with a sparse index at the end. Bloom filter per SSTable for point lookups.

**Compaction:** periodically merge SSTables to:
- Drop tombstones (deletes).
- Drop overwritten values.
- Reclaim space.
- **Strategies:**
  - **Size-tiered (STCS):** merge small SSTables into larger ones. Write-friendly, more space amp.
  - **Leveled (LCS):** SSTables organized in levels; each level 10× the size of the previous, with bounded overlap. Read-friendly, less space amp.
  - **Time-window (TWCS):** compact SSTables within a time window. Best for time-series with TTL.

**Read path:**
1. Check memtable + immutable memtables.
2. Check Bloom filter on each SSTable (skip if "definitely not").
3. Binary search index → scan SSTable.
4. Merge results across SSTables; resolve conflicts by timestamp.

**Tombstones:** deletes are a special tombstone record, propagated through compaction. **gc_grace_seconds** is how long tombstones linger before GC — typically 10 days. Replica repair during this window can resurrect deleted data (operational footgun).

## Deep dive #2 — Replication, consistency, failure

**Replication factor (N):** each row's data is written to N nodes (the preference list, picked by walking the consistent-hash ring from the key's position).

**Consistency level (CL):** per-query tunable.
- `ONE`: fastest; first replica to respond.
- `QUORUM`: majority of replicas (R + W > N).
- `LOCAL_QUORUM`: majority in the local DC.
- `ALL`: all replicas (slow, fragile).
- `EACH_QUORUM`: quorum in each DC (cross-DC strong).

**Write CL + Read CL = N** → strong consistency. Default is `LOCAL_QUORUM` write + `LOCAL_QUORUM` read → strong within DC.

**Hinted handoff:** if a replica is down, coordinator writes to the *next* node with a *hint* about the intended target. Replay when the original is back. Bounded (max_hint_window_in_ms = 3h by default).

**Read repair:** on a read, if replicas return different values, the coordinator writes the newest value to the stale replicas. Synchronous or asynchronous.

**Anti-entropy (Merkle tree):** background process per node that hashes the key range and reconciles divergent replicas. Catches drift that read-repair missed.

**Failure scenarios:**
- Node down: hints absorb writes for the window; Merkle tree reconciles.
- Network partition: minority partition can't reach QUORUM → writes fail; majority keeps serving.
- Partition heals: anti-entropy repairs the minority; hints replay.

## Scale & bottlenecks

- **Hot partition:** one partition key (e.g. today's date) takes most traffic → only N nodes are loaded. Mitigation: bucket the partition key (e.g. `date_bucket`), or accept and over-provision.
- **Compaction storms:** sustained write load triggers continuous compaction; latency spikes. Mitigation: tiered compaction strategy, dedicated compaction bandwidth, scale-out.
- **Wide rows / unbounded partitions:** partition grows beyond 100MB → slow reads, GC pressure. Always bucket by time or hash.
- **Read amplification:** reading across many SSTables. Mitigation: leveled compaction, larger memtable.
- **Tombstone bloat:** time-series workloads generate many tombstones on TTL expiry → TWCS + correct gc_grace.

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Node down | Hints absorb | Replay on return; rebuild from Merkle |
| Disk full | Compaction fails | Alerts; tiered storage; TTL policy |
| Partition hot | Saturation | Bucket partition key; read-spread |
| Wide partition | Slow reads | Bound partition size at design time |
| Tombstone resurrection | Deleted data reappears | gc_grace_seconds + repair window discipline |
| Network partition | Minority can't write | Tunable CL; cross-DC consistency |

## "What I'd build first and why"

**Consistent-hash ring with vnodes + LSM-tree storage + tunable consistency per query.** Start with `LOCAL_QUORUM` for everything; loosen for specific use cases. Skip transactions, secondary indexes in v1 — they're a complexity multiplier.

The single highest-leverage thing is **partition key design** — get it wrong and you get hot partitions or unbounded growth. Get it right and everything else is operational tuning.

## Follow-ups (real, reported)

1. **Cassandra vs Bigtable vs DynamoDB** — peer-to-peer vs master-tablet vs managed; when each shines.
2. **LSM vs B-tree** — write amp, read amp, space amp tradeoff.
3. **Compaction strategies** — STCS vs LCS vs TWCS; when each.
4. **Tombstone resurrection** — the gc_grace window footgun.
5. **Tunable consistency** — name three CL settings and the tradeoff.
6. **Hinted handoff** — how it works and its limits.
7. **Read repair vs anti-entropy** — synchronous vs background.
8. **Hot partition** — bucket the key, hash suffix, accept and scale.
9. **Secondary indexes** — local (per-node) vs global (separate index table).
10. **Materialized views** — pre-computed for read patterns; consistency caveats.

## Tips (staff-level)

- **Name LSM.** Memtable + SSTables + compaction. Then go deeper with the strategy.
- **Draw the consistent-hash ring.** Walk through a key → preference list → replicas.
- **Name the consistency levels.** ONE / QUORUM / LOCAL_QUORUM / ALL.
- **Quantify:** "10TB on 100 nodes, +10 nodes = +1TB working set, ~linear write scaling".
- **Acknowledge the partition-key footgun.** Most candidates miss it.

## Pitfalls

- **"It's just a KV".** LSM + tunable consistency + linear scaling is the value.
- **Ignoring partition key design.** Most common prod incident.
- **Strong consistency everywhere.** Defeats the point — make it tunable.
- **No TTL.** Time-series without TTL = unbounded growth.
- **Wide rows.** Scanning a 1GB partition kills you.

## Worked narration (3 min)

"Goal: 1M writes/s, 10TB working set, linear scale by adding nodes, eventually consistent, tunable strong reads.

**Architecture:** consistent-hash ring with 256 vnodes per node. Each row hashed to a position; preference list = next 3 nodes (rack-aware snitch).

**Storage:** LSM tree. Writes hit WAL + memtable → flush to SSTable. Compaction (LCS by default) merges SSTables, drops tombstones, reclaims space. Bloom filter per SSTable for point lookups.

**Consistency:** tunable per query. Default `LOCAL_QUORUM` write + `LOCAL_QUORUM` read = strong within DC. Cross-DC: `LOCAL_QUORUM` per DC + `EACH_QUORUM` for global strong.

**Failure:** node down → hinted handoff to next node; Merkle tree reconciles when it returns. Partition hot → bucket the partition key (e.g. `date_bucket`). Tombstones → gc_grace=10d, TWCS for time-series.

**First build:** consistent-hash + LSM + `LOCAL_QUORUM`. Skip secondary indexes, materialized views, transactions. Add when a workload needs them."

## Related

- [[01-distributed-kv-cache]] — same partition/replication model.
- [[03-distributed-message-queue-pubsub]] — durable ordered log is the other side of the same coin.
- [[09-consensus-leader-election]] — Raft replaces gossip for stronger consistency (Spanner-style).
- [[20-change-data-capture]] — log compaction is the primitive that powers CDC.