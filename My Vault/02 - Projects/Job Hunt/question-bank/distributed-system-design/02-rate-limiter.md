---
title: "Rate Limiter"
slug: rate-limiter
type: distributed-system-design
tier: "3 — API & traffic layer"
companies: [Robinhood, Stripe, Cloudflare, AWS, Anthropic, OpenAI, Cohere, "any API platform"]
difficulty: ★★☆☆☆
frequency: very-high
formats: [Onsite·SD, Live, Whiteboard]
time-box: 25–35 min
tags: [rate-limit, token-bucket, sliding-window, redis, distributed-counter]
related: ["[[01-distributed-kv-cache]]", "[[04-distributed-lock-service]]", "[[13-api-gateway]]"]
companies-likely: [Robinhood, Stripe, Cloudflare, AWS, Anthropic, OpenAI, Cohere]
star: true
---

# Rate Limiter

**One-liner:** A service that caps how many requests a client can make per unit time across a fleet, with strict per-tenant limits and accurate counts under high concurrency.

## Problem framing

Asked at almost every API-platform / fintech / infra interview. Robinhood, Stripe, Cloudflare, AWS — all care deeply about this. Variants: per-user, per-IP, per-API-key, per-tenant, per-endpoint, or combinations.

**Variants:**
- "Design a rate limiter for our public API" (general)
- "Design a per-user quota system" (SaaS)
- "How does Cloudflare's rate limiter work?" (edge)
- "Per-tenant throttling" (multi-tenant SaaS)

## Requirements (clarify first)

- **Functional:** `check(key, limit, window) -> allowed | denied`; configurable limits per tier.
- **Non-functional:**
  - Latency: p99 < 5ms (inline on request path)
  - Throughput: matches API gateway (~100k–1M QPS)
  - Strictness: allow a tiny over-limit (1-2%) for availability, or hard-cap?
- **Constraints:**
  - Limits: 100/min free, 10k/min pro, custom for enterprise.
  - Window: 1s, 1m, 1h, 1d?
  - Per: (user, ip, api_key, endpoint, tenant) — combinations.
- **Out of scope:** billing, fraud detection (mention as next layer).

## Capacity estimation

- 1M QPS / 1000 app servers = 1000 RPS per server → local check feasible for many.
- But for **distributed** accuracy (not per-instance), need a shared counter: 1M ops/sec against a Redis cluster is fine; against a single Redis is not.
- Memory: 100M active keys × (counter + timestamp) × 32B = 3.2GB. Fine for Redis.

## High-level architecture

```
client → API gateway
            │
            ▼
       Rate-limit middleware (in-process LRU + remote counter)
            │
            ├──► Local token-bucket (fast path, may over-allow)
            └──► Redis (Lua / atomic INCR)   ← ground truth
                       │
                       ▼
                 Decision: allow / deny / challenge
```

Two-tier: **local** for hot keys (fast), **distributed** for accuracy.

## API / interfaces

```
POST /v1/ratelimit/check
{ "key": "user:123", "limit": 100, "window_s": 60 }
→ { "allowed": true,  "remaining": 42, "reset_at": 1718721600 }

POST /v1/ratelimit/keys
{ "key": "user:123", "limit": 100, "window_s": 60, "action": "set" }
```

## Deep dive #1 — Algorithms (pick one, name the tradeoff)

| Algorithm | Memory | Strictness | Notes |
|---|---|---|---|
| **Fixed window** | O(keys × 1) | Inaccurate at boundaries (2× burst) | Simplest; Redis INCR + EXPIRE |
| **Sliding window log** | O(keys × window) | Strict | `deque[timestamps]` per key; pop old |
| **Sliding window counter** | O(keys × 2) | ~Accurate | Weight current + previous bucket by overlap |
| **Token bucket** | O(keys × 2) | Allows bursts up to bucket size | `(tokens, last_refill_ts)`; refill at rate |
| **Leaky bucket** | O(keys × 2) | Smooths; no bursts | Same shape, different semantics |
| **GCRA / TAT** | O(keys × 1) | Strict, single int | Used by Stripe; TAT = theoretical arrival time |

**Default answer:** token bucket — most flexible, allows bursting, easy to reason about. **Stripe answer:** GCRA — single integer per key, very fast.

## Deep dive #2 — Distributed counters

**Single Redis with Lua:**
```lua
local cur = redis.call('INCR', KEYS[1])
local ttl = redis.call('TTL', KEYS[1])
if ttl < 0 then redis.call('EXPIRE', KEYS[1], ARGV[1]) end
if cur > tonumber(ARGV[2]) then return 0 else return 1 end
```
Atomic, fast, but single-region.

**Redis cluster:**
- Key → slot by hash; one counter per slot.
- Cross-slot transactions = expensive. Workaround: hash the limit key so all reads/writes hit the same slot.

**Sliding window across the cluster:**
- "Rolling counters" with multiple buckets per window (e.g. 60 1-second buckets).
- Read 60 keys, sum, expire old. ~60× more reads.

**Local + remote (best practical answer):**
- Each app server keeps a local token bucket refilled every N seconds from the remote counter.
- Allows up to N × burst overshoot in the worst case (rare).
- Used by Cloudflare and most big-tech gateways.

**Failure mode:** if Redis is unreachable, **fail open** (allow) or **fail closed** (deny). Default: fail open with metric + alert. Be explicit about which.

## Scale & bottlenecks

- **Hot user:** one user at 50% of traffic → hot Redis slot. Mitigation: shard counter by (user_id, time_bucket), or move hot users to dedicated slots.
- **Clock skew across nodes:** sliding window log uses wall time. Use Redis's TIME command to avoid client clock skew.
- **Memory pressure:** 100M keys × 32B = 3.2GB. Set TTL; evict cold keys (volatile-lru).
- **Atomicity:** don't `GET` then `SET` — race condition. Always use Lua / INCR.

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Redis down | Can't check | Fail open + alert; local cache fallback |
| Redis slow | p99 latency explodes | Lua (1 RTT) + replica reads |
| Clock skew | Wrong window | Server-side TIME |
| Hot key | Slot saturated | Read-spread / local cache |
| Burst overflow | Over-limit briefly | Token bucket naturally absorbs |

## "What I'd build first and why"

A **token-bucket-per-user in Redis** with a **local cache** in each gateway. Lua script for atomicity. Start there; add GCRA or sliding-window later if precision demands it.

The single highest-leverage thing is **failing open vs closed** — say it out loud. Most candidates don't.

## Follow-ups (real, reported)

1. **Local vs distributed** — when is local enough? When must you check remote?
2. **Stripe-style GCRA** — derive it; show the TAT math.
3. **Multi-tier limits** — per-user AND per-tenant AND per-IP. Composable.
4. **Cost-aware** — reject requests that would cost more than the limit they're under.
5. **Burst handling** — token bucket with bucket size = burst capacity.
6. **Distributed fairness** — all clients see the same counter; consistent hashing.
7. **Failure mode policy** — fail open vs closed, and how to detect which mode you're in.
8. **Per-endpoint vs global** — limits that compose.
9. **Quota rollover** — daily / monthly quotas with reset semantics.
10. **Soft vs hard limits** — challenge (CAPTCHA) vs reject vs 429.

## Tips (staff-level)

- **Name one algorithm by name** (token bucket, GCRA, sliding window log) — don't list all four.
- **Quantify:** "1M QPS, 1k app servers = 1000 RPS each, local token bucket covers ~80%, the other 20% needs Redis — 200k Redis ops/s = 5 instances, $X".
- **Lua-script the counter.** Single RTT, atomic, fast.
- **Say "fail open" out loud.** Most candidates don't think about it.
- **Be opinionated about local+remote.** That's what real systems do.

## Pitfalls

- **Race condition** — `GET` then `SET`. Use INCR or Lua.
- **Ignoring Redis downtime** — your whole API is down. Plan for it.
- **Per-user vs per-IP** — interview question. Per-user is what you charge for; per-IP is what you defend with.
- **Bucket sizing** — too small = false rejections under burst; too big = no protection.
- **Time math** — wall-clock skew across nodes. Use server-side time.

## Worked narration (2 min)

"Goal: 100k QPS API, 100 req/min per user, fail-open on backend failure, p99 < 5ms.

**Algorithm:** token bucket per user. Bucket size = 100, refill 100/60s ≈ 1.67 tokens/sec.

**Storage:** Redis cluster. Lua script does `INCR + EXPIRE + compare` in one round-trip — atomic, single RTT. Each user maps to one key; TTL = window length.

**Local fast-path:** each gateway keeps a 1-second local token bucket, refilled by the ground truth. Absorbs 95% of checks locally.

**Failure:** Redis down → fail open with a `ratelimit_degraded` metric and alert at p95 > 50ms.

**Hot users:** if a user exceeds 10× the limit, push the counter to a per-user Redis cluster key.

First build: token bucket in Redis with Lua, plus local cache. Add GCRA only if we measure stampedes."

## Related

- [[01-distributed-kv-cache]] — Redis IS a distributed KV; rate-limiter rides on it.
- [[04-distributed-lock-service]] — same distributed-counter problem in a different shape.
- [[13-api-gateway]] — where the rate-limiter middleware lives.
- `[[question-bank/practical-coding/23-logger-rate-limiter]]` and `[[24-hit-counter]]` — code-level versions.