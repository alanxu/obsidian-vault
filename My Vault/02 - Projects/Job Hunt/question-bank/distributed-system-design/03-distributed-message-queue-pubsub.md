---
title: "Distributed Message Queue / Pub-Sub"
slug: distributed-message-queue-pubsub
type: distributed-system-design
tier: "1 — Core data stores & consistency"
companies: [Kafka, RabbitMQ, AWS, Google, LinkedIn, Uber, Stripe, Robinhood]
difficulty: ★★★☆☆
frequency: high
formats: [Onsite·SD, Mock]
time-box: 35–45 min
tags: [queue, pubsub, kafka, ordering, exactly-once, partitioning, consumer-groups]
related: ["[[01-distributed-kv-cache]]", "[[19-event-streaming-kafka]]", "[[20-change-data-capture]]"]
companies-likely: [LinkedIn, Uber, Stripe, Robinhood, Cloudflare, Confluent]
star: true
---

# Distributed Message Queue / Pub-Sub

**One-liner:** A durable, partitioned, ordered log that decouples producers from consumers with at-least / exactly-once delivery and tunable retention.

## Problem framing

Asked whenever the interviewer cares about async work, event-driven architecture, or decoupling. LinkedIn (Kafka), Uber, Stripe, Robinhood all lean on this. Variants include message queue (RabbitMQ-style) vs log (Kafka-style) — pick one and own the tradeoff.

**Variants:**
- "Design Kafka / Pulsar" (log-flavored, append-only, replayable)
- "Design a task queue" (RabbitMQ-style, ack-based, in-flight)
- "Design a pub/sub" (topic fanout, push delivery)
- "Webhook delivery system" (durable + retry + at-least-once)

## Requirements (clarify first)

- **Functional:** `publish(topic, msg)`, `subscribe(topic, consumer_group)`, ack/nack, replay from offset.
- **Non-functional:**
  - Throughput: 100k–10M msg/s per cluster
  - Latency: end-to-end p99 < 100ms
  - Durability: zero message loss (replicated, fsync'd)
  - Ordering: per-key (partition key), not global
- **Constraints:** message size (1KB avg / 1MB max), retention (7 days default), replay requirement.
- **Out of scope:** exactly-once transactions across heterogeneous systems (mention; rarely achievable).

## Capacity estimation

- 1M msg/s × 1KB = 1GB/s ingest. 7-day retention = 600TB.
- 1000 partitions / 100 brokers = 10 partitions/broker. ~10k msg/s/partition for sub-ms latency.
- Replication factor 3 → 1.8PB total storage.

## High-level architecture (Kafka-style log)

```
Producer ──► Broker (partition leader) ──► WAL (segment files on disk)
                  │
                  ├──► ISR replica 1
                  └──► ISR replica 2
                          
Consumer group ──► reads partitions assigned to its members
                  commits offset to __consumer_offsets
```

- **Broker:** stateless log storage. Append-only segment files, one per partition, rotated at 1GB.
- **Partition:** unit of parallelism and ordering. Producer picks partition by key hash (or round-robin if no key).
- **Consumer group:** set of consumers that share work; each partition is read by exactly one consumer in the group.
- **ZooKeeper / KRaft:** cluster metadata + leader election.

## API / interfaces

```
POST /v1/produce   { topic, key, value, headers? }   → { offset, partition }
GET  /v1/consume   { topic, group, partition, offset, max }  → { records }
POST /v1/commit    { topic, group, partition, offset }
POST /v1/subscribe { topic, group, consumer_id }
```

## Deep dive #1 — Ordering & delivery semantics

**Ordering:** guaranteed **per partition**, not globally. Producer hashes key → same partition → same consumer. Use partition key = `user_id` / `order_id` / `account_id` to keep related events in order.

**Delivery semantics:**
- **At-most-once:** producer doesn't retry; consumer commits before processing. Fast, lossy.
- **At-least-once:** producer retries on ack timeout; consumer commits after processing. Default. Risk: duplicate processing.
- **Exactly-once:** Kafka's transactional API: producer-side idempotent + transactional writes, consumer reads committed offsets within the transaction. Strong but expensive (~30% throughput hit).
- **Effectively-once:** idempotent consumer (dedup on `(key, seq)`) on top of at-least-once. Most production systems do this.

**The classic interview question:** "How do you guarantee no duplicates?" Answer: you can't, cheaply. Either pay for exactly-once or make consumers idempotent (most common).

## Deep dive #2 — Durability & retention

- **Write path:** producer → leader broker → append to WAL (page cache + async fsync) → replicate to followers → ack producer when `acks=all` (or `acks=1` for leader-only).
- **acks=all + min.insync.replicas=2** → durable under single broker loss.
- **Segment files:** 1GB append-only files; consumer reads by offset → file + position lookup. mmap'd for speed.
- **Retention:** time-based (7 days) or size-based (1TB per topic) — drop oldest segments. Logs become ephemeral by default.
- **Compaction:** log compaction keeps only the latest value per key (used for change-data-capture / state topics).

**Failure mode: leader failure.** Controller detects via ZooKeeper/KRaft session expiry, elects new leader from ISR, producers retry. ~1-2s of unavailability.

## Scale & bottlenecks

- **Hot partition:** one key gets 50% of traffic → that one partition is the bottleneck. Mitigation: salting (`user_id_0..user_id_9`), or split by a sub-key.
- **Consumer lag:** consumers fall behind. Metric: `records-lag-max`. Mitigate: scale consumer group (add members up to partition count), batch, or backpressure producers.
- **Broker disk full:** retention helps, but a spike can fill disk. Mitigate: alerts at 70% / 85% / 95%, tiered storage (Kafka 3.6+) for cold data.
- **Replication amplification:** RF=3 with acks=all means 3× write traffic. Don't use `acks=0` unless you can lose messages.

## Failure modes & mitigations

| Failure | Detection | Mitigation |
|---|---|---|
| Broker crash | ZooKeeper/KRaft session | New leader from ISR, ~1-2s unavailability |
| Disk full | Monitoring | Retention policy + tiered storage + alerts |
| Slow consumer | Lag metric | Auto-scale consumers; producer backpressure |
| Network partition | acks timeout | Producer retries with exponential backoff + jitter |
| Producer dup | Network retry | Idempotent producer (PID + sequence) |
| Split brain (old leader) | Epoch bump | `leader_epoch` check rejects stale writes |

## "What I'd build first and why"

A **partitioned append-only log** on local disk (mmap'd segment files), with **leader-follower replication** and **consumer-group offset tracking**. Start with at-least-once + idempotent consumers. Skip exactly-once until a real workload needs it.

The single highest-leverage thing is the **partition + consumer-group model** — that's the primitive everything else is layered on.

## Follow-ups (real, reported)

1. **Kafka vs RabbitMQ** — when to use which? (Throughput + replay vs simple work queue.)
2. **Exactly-once** — is it real? Cost? When does it break?
3. **Ordering guarantees** — per partition? per key? global?
4. **Backpressure** — what happens when consumers can't keep up?
5. **Replay / time-travel** — re-consume from a past offset. Use case: rebuild a read model.
6. **Schema evolution** — Avro / Protobuf with a schema registry; backward / forward / full compatibility.
7. **Dead-letter queue** — poison messages; isolate + alert.
8. **Cross-region replication** — MirrorMaker 2, cluster linking.
9. **Tiered storage** — hot on local SSD, cold on S3.
10. **Stream processing** — Kafka Streams / Flink / Spark on top.

## Tips (staff-level)

- **Pick log vs queue and own it.** Don't design both. Say "I'll go log because the workload is replay + high throughput".
- **Name the delivery semantics** — at-least-once is the default; exactly-once is opt-in and expensive.
- **Quantify:** "1M msg/s × 1KB = 1GB/s ingest; 100 brokers, 10 partitions each, RF=3 → 1.8PB retention at 7 days".
- **Failure modes table.** Especially leader election + acks=all.
- **Say what you'd skip:** exactly-once transactions, schema registry, tiered storage — flag as variants.

## Pitfalls

- **Confusing Kafka (log) with RabbitMQ (queue).** They have different semantics.
- **Not naming the delivery semantic.** Always-on at-least-once is the safe default; say why.
- **Single partition for "ordering".** Doesn't scale.
- **No DLQ.** Poison messages jam the partition.
- **Backpressure ignored.** Slow consumer = OOM at the broker or unbounded lag.

## Worked narration (3 min)

"Goal: 1M msg/s, 1KB avg, 7-day retention, at-least-once with idempotent consumers, per-key ordering.

**Model:** partitioned append-only log. Producer hashes partition key → partition. Consumer group has one consumer per partition; commits offset to `__consumer_offsets`.

**Storage:** segment files on local SSD, 1GB each, mmap'd. Retention drops old segments; log compaction for state topics.

**Replication:** RF=3, `acks=all`, leader + ISR. Leader epoch rejects stale writes. KRaft for metadata (no ZooKeeper).

**Delivery:** at-least-once + idempotent consumer. Producer has PID + sequence; dedup on consumer side.

**Failure:** leader dies → new leader from ISR in ~1-2s. Broker disk full → tiered storage moves cold segments to S3. Hot partition → salt the key.

**First build:** log + ISR replication + consumer groups. Add exactly-once transactions only if a workload demands it."

## Related

- [[01-distributed-kv-cache]] — replication + consistency live there.
- [[19-event-streaming-kafka]] — Kafka-specific deep dive.
- [[20-change-data-capture]] — log compaction is the primitive.
- [[10-job-scheduler-task-queue]] — at-least-once delivery is shared DNA.