---
title: "Service Discovery & Registry"
slug: service-discovery-registry
type: distributed-system-design
tier: "2 — Coordination & control plane"
companies: [Netflix Eureka, Consul, etcd, Kubernetes, AWS ALB, Linkerd, Istio, Cloudflare]
difficulty: ★★★☆☆
frequency: medium-high
formats: [Onsite·SD, Mock]
time-box: 25–35 min
tags: [service-discovery, registry, eureka, consul, dns, health-check, load-balancing]
related: ["[[11-configuration-management]]", "[[04-distributed-lock-service]]", "[[13-api-gateway]]"]
companies-likely: [Netflix, Consul, Kubernetes shops, linkerd/Istio users]
---

# Service Discovery & Registry

**One-liner:** A system that maps a logical service name to a healthy instance endpoint, with fast lookups, automatic registration / deregistration, and health-driven routing.

## Problem framing

Asked at any microservices shop. Variants: "Design Eureka / Consul / Kubernetes DNS". The interviewer wants to see how you handle *change* — instances come and go, IPs are dynamic in K8s, failures happen. Pull-based vs push-based registration is the classic axis.

**Variants:**
- "Design service discovery" (general)
- "Design Kubernetes DNS / kube-proxy" (kubelet-level)
- "Design Consul" (DNS + health checks + KV)
- "Design a service mesh control plane" (Istio / Linkerd)

## Requirements (clarify first)

- **Functional:** `register(service_id, host, port, metadata)`, `deregister(service_id)`, `lookup(service_name) → [endpoints]`, health checks.
- **Non-functional:**
  - Lookup latency: < 5ms (in-process cache hit) / < 50ms (cold)
  - Freshness: detect failures in < 10s
  - Consistency: eventual (clients cache) is fine; tight loops cause thundering herds
- **Constraints:** number of services (100s / 1000s), instances per service (1 / 10 / 1000), churn (low / high).
- **Out of scope:** load balancing policy (just return healthy endpoints).

## Capacity estimation

- 10k service instances, each 200B registry entry → 2MB total. Fits in RAM on a single node.
- 100k lookups/s across the fleet; with 5s in-process cache TTL → 20k lookups/s reach the registry.
- Health checks: 10k instances × 1 check/10s = 1k checks/s. Easy.

## High-level architecture

```
Service A ──► Registry (Consul / Eureka / etcd)
                  │  (push registration + heartbeat)
                  │
                  ▼
            Watch / health check
                  │
                  ├──► Healthy endpoint set
                  └──► Unhealthy (after N failures)
                          
Service B ──► Client-side resolver / sidecar
                  │  (cache, refresh every Ns)
                  │
                  └──► Load-balances across healthy endpoints
```

## API / interfaces

```
POST /v1/catalog/register
{ "service": "checkout", "instance_id": "i-123", 
  "address": "10.0.1.5", "port": 8080, "metadata": {...}, "ttl_s": 30 }
→ 200

DELETE /v1/catalog/register/i-123
→ 200

GET /v1/catalog/services/checkout
→ { "endpoints": [
     { "instance_id": "i-123", "address": "10.0.1.5:8080", "healthy": true },
     { "instance_id": "i-124", "address": "10.0.1.6:8080", "healthy": true },
     ...
   ]
}

GET /v1/health/checkout/i-123
→ 200 { "status": "passing" }
```

## Deep dive #1 — Registration models

**Self-registration (push):**
- Service instance registers on startup with the registry.
- Heartbeats every TTL/3 to keep the lease alive.
- Deregister on graceful shutdown.
- **Used by:** Eureka, Consul agents.
- **Pro:** simple, single source of truth.
- **Con:** split-brain if instance can reach some clients but not the registry.

**Third-party registration (pull):**
- External process (e.g. K8s controller, consul-agent, linkerd-proxy) watches the platform for new instances and registers them.
- **Used by:** Kubernetes DNS, Consul in agent mode.
- **Pro:** robust; instance doesn't need to know about the registry.
- **Con:** more moving parts.

**DNS-based:**
- Service resolves via DNS (e.g. `checkout.svc.cluster.local`).
- DNS records updated by the platform (kube-dns / CoreDNS).
- TTL on the DNS record controls freshness.
- **Pro:** universal client compatibility, no SDK.
- **Con:** DNS caching can mask failures; TTL management is hard.

**Service mesh:**
- Sidecar proxy (Envoy / linkerd-proxy) on every instance.
- Sidecar registers with the control plane; sidecar handles all lookups.
- **Pro:** transparent to the app; rich L7 routing.
- **Con:** operational overhead; every hop has a sidecar.

## Deep dive #2 — Health checks & client-side behavior

**Health check types:**
- **Active:** registry pings the instance on a schedule (HTTP `/health` on port 8080).
- **Passive (in-band):** registry learns from real traffic — if 5 consecutive requests fail, mark unhealthy.
- **TTL / heartbeat:** instance heartbeats every Ns; missing N heartbeats → unhealthy.

**Active is more accurate** (catches silent failures); **passive is faster** (catches failures on real traffic). Use both.

**Client-side caching:**
- Client resolves once, caches for N seconds.
- Refresh triggers: TTL expiry, watch from registry (push notification), or periodic refresh.
- **Watch model (preferred):** registry pushes invalidation events to clients; clients refetch on event. Sub-second freshness.

**Load balancing on the client side:**
- Random / round-robin / least-connections / consistent hashing.
- Eager vs lazy connection pool.
- Circuit breaker integration: mark endpoint bad on repeated failures.

**Multi-DC:**
- Local registry (DC-local instances) preferred.
- Fallback to remote DC if no local healthy.
- Cross-DC registration via replication.

## Scale & bottlenecks

- **Hot service:** one service has 10k instances. Registry can return a sliced view; client picks from a sample.
- **Registry hotspot:** every client hits the same registry node. Mitigation: client-side caching; tiered registry (local proxy → regional → global).
- **Health check storm:** 10k instances × 1 check/5s = 2k checks/s; mitigate by randomizing intervals.
- **Flapping:** an instance oscillates healthy/unhealthy. Mitigation: hysteresis (need N consecutive healthy checks to mark up; 1 fail to mark down).
- **Cache staleness:** DNS TTL = 30s means up to 30s of stale routing during a failure. Use watch + short TTL.

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Instance crash | Stale routing | Health check + deregistration |
| Registry down | No new lookups work | Client cache + fallback to last-known |
| Network partition | Instance can't heartbeat | TTL expiry → deregistered → traffic stops |
| Flapping | Thundra of routing | Hysteresis (N consecutive checks) |
| Slow health check | Long failure detection | Timeout per check; mark suspect fast |

## "What I'd build first and why"

**Self-registration + active health check + watch-based client cache.** Single registry backend (etcd or Consul). Clients cache for ~5s with a watch channel for invalidation. Add a sidecar / mesh only when the operational load demands it.

The single highest-leverage thing is **the watch channel** — without it, every cache miss is a thundering herd against the registry.

## Follow-ups (real, reported)

1. **DNS vs SDK lookup** — pros/cons; caching implications.
2. **Active vs passive health checks** — when to use each.
3. **Consul / Eureka / etcd** — name a real implementation and its limits.
4. **Watch channel vs polling** — invalidation push vs TTL.
5. **Hysteresis** — prevent flapping with N consecutive checks.
6. **Service mesh integration** — Envoy / linkerd-proxy as the client.
7. **Multi-DC discovery** — local-first, fallback to remote.
8. **Sticky routing** — session affinity + consistency hash.
9. **Security** — mTLS between registered services; registry as the trust root.
10. **Client-side load balancing** — random / round-robin / EWMA latency-weighted.

## Tips (staff-level)

- **Name a real system.** Consul, Eureka, Kubernetes DNS. Know one.
- **Talk about cache invalidation** — watch channel vs TTL.
- **Health checks are the heart of this.** Active + passive; hysteresis to prevent flapping.
- **Quantify:** "10k instances, 2MB registry, 100k lookups/s with caching → 20k registry hits/s".
- **Acknowledge the failure mode:** stale cache + split-brain + flapping.

## Pitfalls

- **"Just use DNS".** DNS TTL is hard; cache invalidation is the hard part.
- **Synchronous registration on startup.** Slow boot; boot ordering issues.
- **No health checks.** Stale routing to dead instances.
- **No client cache.** Registry becomes a bottleneck.
- **No hysteresis.** Flapping kills you.

## Worked narration (2 min)

"Goal: 10k service instances, lookup < 5ms, detect failure in < 10s, no single point of failure.

**Registry:** etcd-backed, sharded by service name. Instances self-register on startup, heartbeating every 10s. Active health check every 5s.

**Client side:** SDK resolves `checkout → [endpoints]`, caches for 5s, subscribes to a watch channel. On invalidation event (deregister / health change), refetch.

**Health:** active HTTP `/health` every 5s. After 2 consecutive failures → unhealthy. After 3 consecutive passes → healthy again (hysteresis).

**Failure:** instance crash → health check fails → deregistered → watch fires → clients refetch within ~1s. Registry node dies → clients use cache + leader re-elects.

**First build:** self-registration + active health + 5s cache + watch channel. Add service mesh (Envoy) when L7 routing and mTLS become requirements."

## Related

- [[11-configuration-management]] — same registry substrate (etcd).
- [[04-distributed-lock-service]] — locks for service-init coordination.
- [[13-api-gateway]] — gateway often uses the registry for upstream routing.
- [[14-load-balancer]] — same health-check + endpoint-set problem, L4 vs L7.