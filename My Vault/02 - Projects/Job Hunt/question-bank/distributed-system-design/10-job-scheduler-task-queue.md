---
title: "Distributed Job Scheduler / Task Queue"
slug: job-scheduler-task-queue
type: distributed-system-design
tier: "2 — Coordination & control plane"
companies: [NVIDIA, Scale, Airbnb, Slack, Stripe, Robinhood, Sidekiq, Temporal, AWS Batch]
difficulty: ★★★☆☆
frequency: high
formats: [Onsite·SD, Mock]
time-box: 30–45 min
tags: [scheduler, task-queue, cron, sla, priority, retries, dlq, sidekiq, temporal]
related: ["[[03-distributed-message-queue-pubsub]]", "[[04-distributed-lock-service]]", "[[11-service-discovery-registry]]"]
companies-likely: [NVIDIA, Scale, Airbnb, Stripe, Robinhood, Slack, Temporal]
star: true
---

# Distributed Job Scheduler / Task Queue

**One-liner:** A system that enqueues async work, assigns it to workers, retries on failure, prioritizes by SLA, and surfaces poison-pill jobs to a dead-letter queue — without double-execution.

## Problem framing

Asked at any company with backend work that isn't synchronous request/response: training jobs, billing runs, batch imports, email sends, video transcoding. Variants: "Design Sidekiq / Temporal", "Design a cron service at scale", "Design an ML training scheduler".

**Variants:**
- "Design a task queue" (Sidekiq / Celery / SQS-style)
- "Design a workflow engine" (Temporal / Airflow)
- "Design a cron service at scale" (replacing crontab on 10k machines)
- "Design an ML training scheduler" (NVIDIA / Scale flavor — GPU allocation, gang scheduling, preemption)

## Requirements (clarify first)

- **Functional:** `submit(job, priority, deadline)`, `cancel(id)`, `list()`, status, retries, dependencies (DAG).
- **Non-functional:**
  - Throughput: 10k–1M jobs/min
  - Latency to start: < 1s for high-priority, < 1m for batch
  - **At-least-once** with idempotent jobs, or **exactly-once** for sensitive workflows
  - SLA-aware: priority queue + deadline scheduling
- **Constraints:** job runtime (1s / 1m / 1h / 24h), resource needs (CPU/GPU/RAM), retry policy.
- **Out of scope:** real-time scheduling (sub-second, separate system).

## Capacity estimation

- 100k jobs in flight, each 1 min avg → 1.6k jobs/sec completion rate.
- Workers: 10k workers × 1 job/min = 167 jobs/sec. So ~6× workers needed for burst.
- Scheduler state: 100k active jobs × 200B = 20MB. Trivial.

## High-level architecture

```
Producer ──► Job queue (Kafka / Redis / DB-backed)
                  │
                  ▼
            Scheduler (leader-elected, picks next job per worker class)
                  │
                  ├──► Worker pool A (CPU-bound)
                  ├──► Worker pool B (GPU-bound)
                  └──► Worker pool C (I/O-bound)
                          │
                          ├──► Job run + heartbeat back to scheduler
                          ├──► Success → mark done
                          ├──► Retryable fail → re-enqueue with backoff
                          └──► Non-retryable → DLQ
```

## API / interfaces

```
POST /v1/jobs
{ "type": "render_video", "priority": "high", "deadline_ts": ..., 
  "args": {...}, "max_retries": 3, "idempotency_key": "..." }
→ { "job_id": "J-...", "state": "queued" }

GET /v1/jobs/{job_id}
→ { "state": "running", "worker": "w-42", "started_ts": ..., "attempts": 1 }

POST /v1/jobs/{job_id}/cancel
→ 204

POST /v1/jobs/{job_id}/heartbeat   (worker → scheduler)
→ 204
```

## Deep dive #1 — Scheduling algorithm

**Queues:**
- **Priority queues:** per-priority FIFO (or multi-level feedback queue). High-priority jobs starve low.
- **Fair scheduling:** round-robin across tenants / classes; prevents starvation. Used by Kubernetes, Mesos.
- **Deadline-aware:** EDF (earliest deadline first) — picks the job closest to its deadline.

**Worker assignment (push vs pull):**
- **Push:** scheduler pushes job to worker. Good for latency-sensitive; bad if worker busy.
- **Pull:** workers poll scheduler ("give me work"). Good for batch; latency tax per poll.

**Hybrid (Airflow / Temporal):** workers pull from scheduler; scheduler runs admission control.

**State management:**
- **Lease-based:** scheduler assigns a job with a lease (TTL). Worker heartbeats every lease/3 to renew. Missed heartbeat → scheduler re-assigns.
- **Optimistic concurrency:** worker CAS-claims the job via `UPDATE jobs SET worker_id=? WHERE id=? AND worker_id IS NULL`. Cheap, no separate lease.
- **Visibility timeout (SQS-style):** when worker picks up job, it's invisible for N seconds. If not completed within N, becomes visible again.

**At-least-once vs exactly-once:**
- **At-least-once:** the default. Job can run twice if worker crashes after running but before acking. Jobs MUST be idempotent (use `idempotency_key`).
- **Exactly-once:** Temporal-style — worker returns result; framework records the completion; if worker retries, framework returns the recorded result. Strong, expensive (~30% throughput tax).

## Deep dive #2 — Retries, DLQ, dependencies

**Retry strategies:**
- **Exponential backoff with jitter:** `delay = min(max_delay, base * 2^attempt) + random(0, jitter)`.
- **Max attempts + DLQ:** after N retries → dead-letter queue for human review.
- **Per-error policy:** 5xx retryable, 4xx non-retryable.
- **Circuit breaker:** if downstream service is failing, pause new submissions to it.

**Dependencies (DAG):**
- **Workflow engines:** Temporal, Airflow, Argo. Define `task_a → task_b → task_c` DAGs; scheduler ensures dependencies complete first.
- **Per-task idempotency** + **workflow-level state** stored in the engine.

**Cron at scale:**
- Naive crontab on 10k machines → duplicated triggers. 
- **Centralized scheduler** (one leader per shard) triggers once; dispatches to workers.
- **Distributed locks** on the trigger step to prevent double-fire.
- **Catch-up logic** if scheduler was down during a scheduled time.

**Resource-aware scheduling:**
- **Gang scheduling:** all workers in a group must be available together (ML training — 8 GPUs at once). 
- **Bin-packing:** pack jobs to minimize wasted resources (cluster utilization vs fairness tradeoff).
- **Preemption:** low-priority jobs killed when high-priority needs resources. Cost: wasted work.

## Scale & bottlenecks

- **Hot queue:** one job type saturates workers. Mitigation: dedicated worker pool, separate queue.
- **Scheduler becomes the bottleneck:** single scheduler for all jobs → leader bottleneck. Shard by job type or tenant.
- **Worker heartbeat storm:** 100k workers heartbeating every 1s = 100k ops/s to scheduler. Mitigation: batched heartbeats, jittered intervals, hierarchy (workers → team leader → scheduler).
- **Job state bloat:** millions of completed jobs in DB. Mitigation: TTL on completed jobs, separate archive.
- **Long-running jobs:** 24h training jobs + worker pool autoscaling → if worker dies mid-job, must restart from checkpoint.

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Worker dies mid-job | Job hangs | Lease timeout → reassign + retry |
| Scheduler dies | No new dispatch | New leader elected (Raft / ZooKeeper) |
| Queue (Kafka / Redis) down | No submissions | Multiple replicas + DLQ absorbs spikes |
| Poison pill | Workers keep failing | DLQ after N attempts; alert ops |
| Resource exhausted | Jobs queue forever | Admission control; reject when at capacity |
| Clock skew | Deadline miscalculation | Server-side time; bounded skew tolerance |

## "What I'd build first and why"

**Priority queues (Kafka or DB-backed) + worker pull with lease-based claim + exponential backoff with jitter + DLQ + idempotent jobs.** Start simple; add DAG (Temporal-style), gang scheduling, and preemption only when the workload demands it.

The single highest-leverage thing is **making jobs idempotent** — at-least-once delivery is cheap; exactly-once is hard. Push the burden to the job author.

## Follow-ups (real, reported)

1. **At-least-once vs exactly-once** — when does each make sense?
2. **Priority + fairness** — high-priority doesn't starve low. (Hierarchical queues, fair scheduling.)
3. **Cron at scale** — replacing crontab on 10k machines.
4. **DAG / workflow** — Temporal / Airflow model; dependencies between tasks.
5. **Gang scheduling** — all-or-nothing resource allocation (ML training).
6. **Preemption** — killing low-priority for high. When acceptable?
7. **Lease vs CAS claim** — which, when.
8. **Idempotency** — how to make a job safe to re-run.
9. **DLQ as a feature** — ops view + replay tooling.
10. **Multi-region scheduling** — data locality + cross-region jobs.

## Tips (staff-level)

- **Pick at-least-once, push idempotency to jobs.** Most candidates say "exactly-once" and lose marks.
- **Name a real system.** Sidekiq / Temporal / Airflow / Celery. Know one well.
- **Quantify:** "100k jobs/min, 10k workers, lease 30s, heartbeat 10s, ~p99 1s".
- **Talk about poison-pill handling.** DLQ + retry budget + circuit breaker.
- **Acknowledge the scheduler-as-bottleneck problem** and name the sharding approach.

## Pitfalls

- **"Exactly-once is the default".** It isn't. At-least-once + idempotent jobs is the right answer for most.
- **No DLQ.** Poison-pill jobs jam the queue forever.
- **No idempotency.** Re-runs cause data corruption / double-charges.
- **Synchronous "wait for result" API.** That defeats the purpose; async with callback.
- **Single global scheduler.** Bottleneck at scale.

## Worked narration (3 min)

"Goal: 100k jobs/min, mix of 1s (email) and 1h (training) jobs, retry + DLQ, no double-execution, SLA-aware priority.

**Substrate:** Kafka for the queue + ZooKeeper (or etcd) for scheduler leader election. Workers pull from Kafka; the scheduler assigns workloads based on priority + lease.

**Job lifecycle:** submit → Kafka → worker pulls → CAS-claim (or lease) → run + heartbeat → ack → done. If heartbeat missed → reassign.

**Delivery:** at-least-once. **Idempotency keys mandatory** for every job type; the framework stores `(job_id, attempt_id) → result` for replay.

**Retries:** exponential backoff with jitter; max 5 attempts; on 6th → DLQ with the failure trace for ops.

**Priority + fairness:** hierarchical queues — high/med/low within each tenant; round-robin across tenants prevents starvation.

**Cron:** centralized scheduler, sharded by trigger time. Catch-up replay on restart.

**Failure:** worker dies → lease expires → reassign. Scheduler dies → leader election (1-2s). Poison pill → DLQ. Hot queue → dedicated worker pool.

**First build:** Kafka + lease-based claim + idempotency keys + DLQ. Add DAG and gang scheduling only when a workload needs them."

## Related

- [[03-distributed-message-queue-pubsub]] — Kafka is the typical queue substrate.
- [[04-distributed-lock-service]] — used for trigger-time locks in cron.
- [[11-service-discovery-registry]] — workers need to find services.
- [[37-serverless-platform]] — serverless *is* a task queue + autoscaler.