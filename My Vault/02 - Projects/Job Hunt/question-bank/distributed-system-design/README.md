---
tags: [job-hunt, interview-prep, system-design, distributed]
track: "Distributed system design (Track C)"
plan-section: "§5"
budget-hrs: 8
parent: [[interview-prep-master-plan-2026]]
related: ["[[track-C-distributed-system-design/README]]"]
created: 2026-06-18
---

# Distributed System Design

**Charter:** your strength — this is format + re-skinning, not learning. Use the HelloInterview frame: requirements → API → high-level → deep-dive 1–2 components → scale/bottlenecks. At staff level, lead with requirements clarification, explicit tradeoffs, failure modes, and "what I'd build first and why."

**Who leans on it:** Google, NVIDIA, Robinhood, Lyft, Wealthsimple.

## To elaborate here (one note per prompt; each maps to target companies)
- [ ] `rate-limiter.md` — Robinhood / API platforms (token bucket vs sliding window, distributed counters)
- [ ] `distributed-kv-cache.md` — Google / NVIDIA (consistency, partitioning, eviction, replication)
- [ ] `ride-matching-dispatch.md` — Lyft / Waymo (geohash/quadtree, supply-demand, latency)
- [ ] `realtime-metrics-monitoring.md` — Waymo disengagements / Robinhood incident metrics (time-series, windows, alerting)
- [ ] `payment-ledger-idempotency.md` — Robinhood / Wealthsimple (exactly-once, double-entry, idempotency keys)
- [ ] `petabyte-log-ingestion.md` — Waymo vehicle logs / NVIDIA (batching, partitioning, backpressure, cost)
- [ ] `feed-notifications.md` — general big-tech (fan-out, push vs pull)
- [ ] `job-scheduler-task-queue.md` — NVIDIA training jobs / Scale (priority, SLA, retries, DLQ)

## Note
Lighter budget on purpose — re-skin existing knowledge to the SD interview format; don't rebuild from scratch.

> Legacy alias: this folder replaces `track-C-distributed-system-design/` (same content; cleaner naming).