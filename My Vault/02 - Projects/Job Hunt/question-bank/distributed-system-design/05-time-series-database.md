---
title: "Time-Series Database"
slug: time-series-database
type: distributed-system-design
tier: "1 — Core data stores & consistency"
companies: [InfluxData, Timescale, Prometheus, Datadog, Wavefront, AWS Timestream, Grafana, Robinhood]
difficulty: ★★★☆☆
frequency: medium-high
formats: [Onsite·SD, Mock]
time-box: 30–40 min
tags: [time-series, tsdb, prometheus, downsampling, compression, cardinality]
related: ["[[17-realtime-metrics-monitoring]]", "[[19-event-streaming-kafka]]", "[[18-petabyte-log-ingestion]]"]
companies-likely: [InfluxData, Timescale, Datadog, Grafana, Robinhood, Wavefront]
---

# Time-Series Database

**One-liner:** A database optimized for high-cardinality, append-only, time-stamped data — write-heavy, read-pattern is range scans + aggregation, retention is the killer feature.

## Problem framing

Asked when the workload is metrics, IoT sensors, financial ticks, or app telemetry. The interviewer wants to see that you understand **why a general-purpose KV won't work** (write amplification, cardinality explosion, retention cost).

**Variants:**
- "Design a metrics / monitoring backend" (Prometheus-style)
- "Design an IoT sensor store" (millions of devices, low cardinality per device)
- "Design a financial tick store" (OHLC, sub-millisecond writes)
- "Design a logs / events store" (overlaps with [[18-petabyte-log-ingestion]])

## Requirements (clarify first)

- **Functional:** write(point{ts, tags, value}); query(time_range, tag_filter, agg_fn); retention policy.
- **Non-functional:**
  - Write rate: 1M samples/s sustained, 10M burst
  - Read pattern: last-N minutes for dashboards (high QPS), long-range for analytics (low QPS, large scans)
  - Compression: 10-50× vs raw (delta-of-delta + Gorilla / LZ4)
  - Retention: configurable per series (e.g. 1s resolution for 7d, 1m for 90d, 1h for 2y)
- **Constraints:** cardinality (total active series), per-series size, query latency.
- **Out of scope:** cross-series joins (mention as a variant), real-time alerting (separate service).

## Capacity estimation

- 1M samples/s × 86400s/day = 86.4B samples/day. At 2 bytes/sample after compression = 173GB/day raw, 17GB after compression. 30 days = 500GB. Reasonable.
- 100k active series, each tagged with 5 dimensions at 50B/tag = 25MB tag index. Fine.
- **Cardinality blow-up:** 1M `user_id` × 10k `url` × 100 `endpoint` = 1 trillion series. Don't do this. Bound the tag space.

## High-level architecture

```
Write path:
Producer → load balancer → ingest node (parse, validate)
                              │
                              ├──► Write-Ahead Log (Kafka / local WAL)
                              │
                              ▼
                       Storage node (shard by series hash)
                              │
                              ├──► Memtable (in-memory, sorted by ts)
                              ├──► Flush → immutable SST (columnar, compressed)
                              └──► Compaction (merge SSTs, drop expired)
                              
Read path:
Query → query planner → parallel scan across shards
       → push down agg → merge → return
```

## API / interfaces

```
POST /v1/write
{ "metric": "cpu_usage", "tags": {host, region}, "ts": 1718721600, "value": 0.42 }
→ 204

POST /v1/query
{ "metric": "cpu_usage", "tags": {region: "us-east"}, "from": ..., "to": ...,
  "agg": "avg", "step": "1m" }
→ { "series": [...], "points": [[ts, value], ...] }
```

## Deep dive #1 — Storage engine

**TSM / TSMM (Influx-style):**
- One file per shard. Each file is a series of *blocks*, each block holding one series' data over a time range.
- Block-level compression: **delta-of-delta on timestamps**, **Gorilla XOR on values** — 12 bytes/sample avg.
- Compaction merges blocks; cold data downsampled to lower-resolution blocks.

**Gorilla paper (Facebook, 2015):**
- Timestamps: delta-of-delta encoding. If delta-of-delta = 0 → 1 bit; if small → a few bits.
- Values: XOR with previous; if leading/trailing zeros match → 1 bit + bits that changed.
- Average 1.37 bytes/value on real telemetry. Used in Facebook's Gorilla TSDB.

**Prometheus / Thanos:**
- 2-hour blocks per shard. Each block = chunks of samples per series. mmap'd.
- Compaction merges 2-hour blocks into 6h, 24h. Each step applies a function (avg, max, min).
- WAL for crash recovery; out-of-order samples go to a separate "head block".

**Timescale (Postgres-extension):**
- Hypertable = partitioned by time into chunks. Standard Postgres indexes work.
- Compression via native columnar compression on closed chunks.

**Tradeoff to name:** columnar + block-based gives best compression and range-scan perf; row-based gives best point-lookup. Most production systems do columnar + a separate point-lookup cache.

## Deep dive #2 — Retention, downsampling, cardinality

**Retention tiers** (the killer feature most general DBs lack):
- Hot: raw 1s for 7 days on local SSD
- Warm: 1m rollup for 90 days on cheaper disk
- Cold: 1h rollup for 2y on S3

Each tier has its own compaction step. **Continuous aggregation** (materialized views updated on write) for dashboards.

**Downsampling** is **lossy by design** — preserve agg (avg, max, p99, count), drop individual samples. A 7d retention at 1s → 7d at 1m keeps 1/60th the data and ~99% of the query value.

**Cardinality control:**
- **Bound the tag space.** `user_id` as a tag = cardinality bomb.
- **Series limits:** per-metric cap (e.g. 10M series max); reject writes that would exceed.
- **Tag normalization:** strip high-cardinality labels at ingest.

## Scale & bottlenecks

- **Hot shard (one series with 10× write rate):** salt the series key with a sub-bucket, or split by time range. Or accept the imbalance (cheap SSDs handle 100k writes/s easily).
- **Compaction stall:** under sustained high write, compaction can't keep up. Mitigate: tiered compaction (L0 → L1 → L2), background scheduler with rate limits, separate compaction nodes.
- **Long-range query kills the cluster:** a 6-month scan of 100B samples = OOM. Mitigate: pre-aggregated rollups, query timeouts, sample-on-read.
- **Cardinality explosion:** user-controlled high-cardinality tags → OOM in tag index. Mitigate: schema enforcement, rate limits, alerts on tag cardinality growth.

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Ingest node down | Buffer on Kafka | Kafka absorbs; restart + replay |
| Storage node disk full | Writes fail | Retention policy; tiered storage |
| Compaction falls behind | Reads slow, disk fills | Schedule priority; SSD for hot tier |
| Query OOM | Query killed | Pre-aggregations, query limits, timeouts |
| Cardinality explosion | OOM | Tag schema enforcement, alerts |

## "What I'd build first and why"

**Kafka for ingest + a columnar TSDB (TSM / Gorilla-style) for storage + tiered retention (hot SSD / warm HDD / cold S3) + downsampling on compaction.** Start with raw + 7d hot; add rollups and tiers as the data grows.

The single highest-leverage thing is **bounding cardinality upfront** — once it explodes, you can't recover without a hard reset.

## Follow-ups (real, reported)

1. **Compression ratio** — Gorilla achieves ~12 bytes/sample. Why? (Delta-of-delta + XOR.)
2. **Downsampling strategy** — which agg to keep? (avg + min + max + p99 + count.)
3. **High cardinality** — what to do about `user_id`-style tags? (Don't tag them; bucket at ingest.)
4. **Out-of-order writes** — late-arriving samples. (Head block for last N hours, then sealed into chunks.)
5. **Continuous queries / materialized views** — for dashboard performance.
6. **Cross-series joins** — why most TSDBs don't support them. (Cardinality × cardinality = disaster.)
7. **Tiered storage** — hot / warm / cold with automated migration.
8. **Multi-tenancy** — per-tenant quotas + isolation.
9. **Push vs pull (Prometheus model)** — pull from instrumented endpoints vs push from agents.
10. **OpenTelemetry integration** — the standard telemetry data model.

## Tips (staff-level)

- **Explain why a general DB fails** — write amplification, no retention tier, cardinality explosion.
- **Name the compression algorithm** — Gorilla / delta-of-delta / XOR. Don't hand-wave.
- **Quantify:** "1M samples/s × 2B = 2MB/s raw, 17GB/day compressed, 30d = 500GB".
- **Cardinality is the silent killer.** Bring it up before the interviewer does.
- **Show you've worked with one.** Prometheus, InfluxDB, Datadog — name a real one and its limit.

## Pitfalls

- **Treating it as "just a KV with timestamps".** No — compression + retention + rollups are the value.
- **No cardinality bounds.** A `user_id` tag kills you.
- **No downsampling.** 6-month scans are impossible without rollups.
- **Compaction not prioritized.** Disk fills, reads slow, ops pages you at 3am.
- **Over-modeling tags.** Every dimension becomes a tag = combinatorial explosion.

## Worked narration (2 min)

"Goal: 1M samples/s ingest, 100k active series, 30-day retention at 1s, 90d at 1m, 2y at 1h. p99 read < 1s for last-hour dashboards.

**Why not a KV:** 86B samples at 1KB each = 86TB raw. Compression + tiered retention + rollups bring this to 5-10TB.

**Storage:** columnar, block-based, one file per shard per time window. Gorilla compression (delta-of-delta timestamps + XOR values) → ~12 bytes/sample.

**Write path:** Kafka for durability + replay; storage node flushes memtable to immutable blocks; background compaction merges and downsamples.

**Retention tiers:** hot (1s, 7d, SSD) → warm (1m, 90d, HDD) → cold (1h, 2y, S3). Continuous aggregation updates on each compaction.

**Cardinality control:** schema-enforced tag space, per-metric series cap (10M), reject high-cardinality tags like `user_id`.

**First build:** Kafka + columnar TSDB + 7-day hot retention. Add tiered storage and downsampling once data exceeds 1TB."

## Related

- [[17-realtime-metrics-monitoring]] — TSDB is the storage layer for monitoring.
- [[19-event-streaming-kafka]] — Kafka is the typical ingest layer.
- [[18-petabyte-log-ingestion]] — same write-heavy patterns.