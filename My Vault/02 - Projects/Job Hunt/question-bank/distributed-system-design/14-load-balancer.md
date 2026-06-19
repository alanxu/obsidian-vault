---
title: "Load Balancer (L4 / L7)"
slug: load-balancer
type: distributed-system-design
tier: "3 — API & traffic layer"
companies: [AWS ALB/NLB, Google Cloud Load Balancing, Nginx, HAProxy, Envoy, F5, Cloudflare]
difficulty: ★★★☆☆
frequency: high
formats: [Onsite·SD, Mock]
time-box: 25–35 min
tags: [load-balancer, l4, l7, routing, health-check, consistent-hashing, anycast]
related: ["[[13-api-gateway]]", "[[14-cdn-edge-cache]]", "[[11-service-discovery-registry]]"]
companies-likely: [AWS, GCP, Cloudflare, Nginx/HAProxy users, F5]
---

# Load Balancer (L4 / L7)

**One-liner:** A traffic distributor that takes incoming requests on a virtual IP and forwards them to a healthy backend, with smart routing at L4 (TCP/UDP) or L7 (HTTP/gRPC) granularity.

## Problem framing

Asked when the interviewer wants to test your grasp of network plumbing, health-check-driven routing, and the L4/L7 tradeoff. Variants: "Design HAProxy / Nginx", "Design AWS ALB", "Design an L4 LB for gRPC".

**Variants:**
- "Design an L4 load balancer" (TCP / UDP — fast, dumb)
- "Design an L7 load balancer" (HTTP / gRPC — slow, smart)
- "Design a global load balancer" (GeoDNS / anycast — cross-region)
- "Design Envoy / Nginx"

## Requirements (clarify first)

- **Functional:** accept on VIP:port; distribute to backends by algorithm; health-check backends; session affinity (optional).
- **Non-functional:**
  - L4: line-rate forwarding, < 100µs added latency
  - L7: < 5ms p99 added latency, header-aware routing
  - Throughput: millions of new connections/s
  - Availability: 99.99%
- **Constraints:** backend set size (10 / 1000), backend health volatility, protocol (TCP/UDP/HTTP/gRPC).
- **Out of scope:** TLS termination (mention), auth (gateway's job).

## Capacity estimation

- 1M new connections/s × 1KB = 1GB/s of connection setup. Line-rate.
- 100 backends × 10k QPS = 1M QPS total.
- LB has 1-2µs forwarding overhead in kernel (eBPF / XDP) vs 50µs in userspace.

## High-level architecture

```
Clients ──► Anycast IP / DNS
                │
                ▼
           L4 LB (kernel / eBPF)        ← L7 LB (userspace proxy)
                │                          │
                ▼                          ▼
        Backend pool (TCP)             Parse HTTP headers
        (e.g., gateway fleet)          Route by path/host/header
                                       Rewrite, transform
                                       Forward to upstream
```

## API / interfaces

```
POST /v1/pools
{ "vip": "10.0.0.1:443", "protocol": "tcp",
  "backends": [ "10.0.1.5:8080", "10.0.1.6:8080", ... ],
  "algorithm": "maglev", "health_check": { "type": "tcp", "interval_s": 5 } }
→ { "pool_id": "p-..." }

GET /v1/pools/{id}/backends
→ { "healthy": [...], "unhealthy": [...] }
```

## Deep dive #1 — L4 vs L7

**L4 (TCP/UDP forwarding):**
- Sees only IP / port / protocol.
- Decisions: pick a backend, forward the bytes.
- **Pros:** kernel-bypass (eBPF / XDP) → millions of pps; protocol-agnostic; very low latency.
- **Cons:** no header awareness; no per-request routing; no protocol-specific optimizations.
- **Used for:** large-scale TCP services, game servers, databases, gateway front-ends.

**L7 (HTTP / gRPC / HTTP/2):**
- Parses headers, sometimes body.
- Decisions: route by host / path / header / cookie / JWT claim.
- **Pros:** canary routing, A/B testing, content-based routing, header rewriting.
- **Cons:** parsing overhead, larger attack surface, more complex.
- **Used for:** HTTP APIs, gRPC mesh, anything where routing needs request context.

**The classic interview move:** ask "what layer do you need?" If the answer is "gRPC with header-based routing" → L7. If "1M new TCP connections to backend gateway fleet" → L4. Most candidates default to L7 when L4 would do.

## Deep dive #2 — Algorithms, health, consistency

**Load-balancing algorithms:**
- **Round-robin:** simple, ignores load. Fine for homogeneous backends.
- **Least connections:** picks the backend with fewest in-flight. Better for variable request duration.
- **Weighted round-robin:** assign weights per backend (different capacity).
- **Random:** surprisingly good; uniform distribution with O(1) state.
- **Consistent hashing:** hash a key (e.g. `user_id`) to pick a backend. Stable across backend adds/removes. Used by Maglev (Google).
- **EWMA latency-weighted:** pick the backend with lowest recent latency. Best for variable-load backend pools.
- **Power-of-two-choices:** pick 2 random backends, choose the less-loaded. Avoids the worst-case of pure random.

**Maglev (Google):**
- Pre-computed lookup table of size 65537 (or 2^17).
- Hashes a consistent-hash key → table lookup → backend in O(1).
- Bounded disruption: adding a backend disrupts only 1/N connections.

**Health checks:**
- **Active:** LB pings the backend on a schedule (TCP SYN, HTTP GET `/health`).
- **Passive (in-band):** LB observes real traffic; if 5 consecutive failures, mark unhealthy.
- **Hysteresis:** N consecutive healthy checks to mark up; 1 fail to mark down. Prevents flapping.

**Connection draining:** when removing a backend, send existing connections to completion (or until idle) before closing.

## Scale & bottlenecks

- **Single LB bottleneck:** one LB can forward ~10M pps (kernel-bypass). Beyond that, ECMP / anycast.
- **State:** connection-tracking tables in kernel (conntrack). At 1M concurrent connections, ~1GB. Fine.
- **Hot backend:** one backend gets all the traffic (e.g., all requests hash to the same key). Consistent hashing doesn't solve it — only consistent *distribution*.
- **Health check storms:** 1000 backends × check every 5s = 200 checks/s. Trivial. But 100k backends = 20k/s. Need to be careful.

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| LB node down | Traffic affected | Active-active pair; ECMP / anycast |
| Backend down | Errors to clients | Active health check + fast drain |
| Backend slow | Latency spike | EWMA / passive health check + circuit breaker |
| Connection table full | New connections rejected | Tuned kernel params; backend scaling |
| Flapping | Routes thrash | Hysteresis |

## "What I'd build first and why"

**L4 LB (kernel-bypass, eBPF / XDP) for the outer edge + L7 LB (Envoy / Nginx) for inner routing.** L4 picks a gateway; gateway's L7 logic handles header-based routing.

The single highest-leverage thing is **picking the right layer** — L4 is 10× faster but blind to the request. Don't reach for L7 when L4 works.

## Follow-ups (real, reported)

1. **L4 vs L7** — name the tradeoff in concrete numbers (latency, throughput).
2. **Maglev consistent hashing** — bounded disruption; how it works.
3. **EWMA latency-weighted** — what it adds over random / round-robin.
4. **Power-of-two-choices** — slightly better than random; cheaper than EWMA.
5. **eBPF / XDP for kernel-bypass** — 10× faster than userspace.
6. **Anycast vs GeoDNS** — global routing.
7. **Health check hysteresis** — prevent flapping.
8. **Connection draining** — graceful backend removal.
9. **TLS termination** — at the LB or at the backend?
10. **Backend hot key** — consistent hashing doesn't help; need read-spread.

## Tips (staff-level)

- **Name the algorithm.** Maglev, EWMA, power-of-two — don't say "round-robin".
- **L4 vs L7 first.** Most candidates default to L7.
- **Quantify:** "1M pps, 100µs added latency, 1000 backends".
- **Hysteresis + drain.** Real ops experience.
- **Kernel-bypass (eBPF/XDP).** Staff signal — know the modern hot path.

## Pitfalls

- **"L7 is always better".** It's slower; choose deliberately.
- **No health check.** Backend crashes → connect-refused to client.
- **No hysteresis.** Flapping kills you.
- **Sticky-by-cookie without expiry.** Backend changes break stickiness.
- **Single LB** without HA pair.

## Worked narration (2 min)

"Goal: 1M QPS, 100µs added latency, 1000 backends, canary routing for new versions.

**Outer L4:** kernel-bypass (eBPF/XDP) on commodity boxes. Maglev consistent hash on `src_ip` or connection ID for backend affinity. 1M pps per node, ~50µs added latency.

**Inner L7:** Envoy fleet. Path-based routing (`/v1/*`, `/v2/*`), canary by header (`X-Canary: v2`), header rewriting.

**Algorithm:** Maglev at L4 for backend stickiness; EWMA latency-weighted at L7 for canary groups.

**Health:** active TCP check every 5s + passive (3 consecutive failures). Hysteresis: 2 healthy checks to mark up, 1 fail to mark down.

**Failure:** backend dies → marked unhealthy in ~10s; traffic drains. LB node dies → anycast shifts traffic. Canary backend slow → EWMA demotes.

**First build:** L4 with Maglev + active health + 3-node HA. Add L7 with header routing when canary needs per-request splits."

## Related

- [[13-api-gateway]] — L7 LB is essentially a dumb gateway.
- [[15-cdn-edge-cache]] — CDN is the outermost layer.
- [[11-service-discovery-registry]] — LB needs the backend set.