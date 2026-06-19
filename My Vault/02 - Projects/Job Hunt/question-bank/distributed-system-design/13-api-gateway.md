---
title: "API Gateway"
slug: api-gateway
type: distributed-system-design
tier: "3 — API & traffic layer"
companies: [Kong, AWS API Gateway, Apigee, Nginx, Envoy, Cloudflare, Stripe, Robinhood, Lyft]
difficulty: ★★★☆☆
frequency: high
formats: [Onsite·SD, Mock]
time-box: 30–40 min
tags: [api-gateway, routing, auth, rate-limit, transformation, observability]
related: ["[[14-load-balancer]]", "[[02-rate-limiter]]", "[[15-cdn-edge-cache]]", "[[16-circuit-breaker-reliability]]"]
companies-likely: [Kong, AWS, Apigee, Stripe, Robinhood, Lyft, Cloudflare]
star: true
---

# API Gateway

**One-liner:** The single entry point for all client traffic that handles routing, auth, rate limiting, transformation, observability, and protocol translation — so individual services stay simple.

## Problem framing

Asked at any company with a microservices architecture (i.e., most). Variants: "Design Kong / AWS API Gateway", "Design the edge layer for our app", "Design an API gateway for a partner / B2B program". The interviewer wants to see that you can build a cross-cutting layer that *every* request goes through.

**Variants:**
- "Design a public API gateway" (Stripe, Robinhood)
- "Design a partner / B2B gateway" (separate rate limits, signing keys)
- "Design a mobile API gateway" (binary protocol, header optimization)
- "Design an internal east-west gateway" (service mesh control plane)

## Requirements (clarify first)

- **Functional:** route by path / host / header; transform (request/response); auth (validate JWT / API key); rate limit; aggregate; protocol translation (REST → gRPC).
- **Non-functional:**
  - Latency overhead: < 5ms p99 added by the gateway
  - Throughput: 100k–1M req/s
  - Availability: 99.99%
- **Constraints:** per-tenant configuration (limits, transforms, auth); versioned routes (v1, v2).
- **Out of scope:** business logic (gateway is dumb pipe + policy).

## Capacity estimation

- 100k req/s × 1KB request = 100MB/s ingress.
- 1000 gateway nodes × 100 req/s/node = 100k req/s. Linear.
- State: per-tenant config (1MB / tenant × 10k tenants = 10GB). Off-box.

## High-level architecture

```
Clients ──► L4 LB (NLB / HAProxy)
                │
                ▼
           API gateway fleet (Envoy / Kong / Nginx)
                │
                ├──► Auth filter (JWT / API key / OAuth)
                ├──► Rate limit filter (Redis-backed)
                ├──► Transform filter (REST → gRPC, JSON shaping)
                ├──► Routing (path → upstream service)
                └──► Observability (logs, metrics, traces)
                         │
                         ▼
                  Upstream services
```

## API / interfaces (gateway-as-a-service)

```
POST /v1/routes
{ "path": "/v2/checkout", "upstream": "checkout-svc",
  "auth": "jwt", "rate_limit": "100/m/user", 
  "transform": { "request": {...}, "response": {...} } }
→ { "route_id": "r-..." }

GET /v1/routes
→ [...]

DELETE /v1/routes/{id}
→ 204
```

## Deep dive #1 — The filter chain

A request flows through a chain of filters. Each filter is a small, composable unit. Common filters:

1. **TLS termination** — handle HTTPS, mTLS for partners.
2. **Auth** — verify JWT signature, check expiry, extract claims.
3. **Rate limit** — call the rate-limit service (or local token bucket).
4. **Routing** — match path → upstream service, add headers (request_id, trace_id).
5. **Transform** — REST → gRPC, version migration, JSON field renaming.
6. **Circuit breaker** — track upstream health; fail fast on known-bad.
7. **Retry / timeout** — bounded retry with budget.
8. **Logging / metrics / trace** — record everything.
9. **Response transform** — strip internal fields, add CORS headers, etc.

**The killer question:** how do you make filters composable without ordering bugs? Answer: explicit ordered chain (Envoy's HTTP filter chain), or filter graph with explicit dependencies.

**Filter performance:**
- Each filter is O(request_size) — needs to be tight.
- No allocations on the hot path (Envoy is famous for this).
- Pre-compile filter chains where possible (Lua/WASM modules JIT'd).

## Deep dive #2 — Routing, config, observability

**Routing:**
- **Path-based:** `/users/*` → user service.
- **Host-based:** `api.example.com` vs `partner.example.com`.
- **Header-based:** `X-API-Version: v2` → v2 service.
- **Weighted:** 95% to v1, 5% to v2 for canary.
- **Sticky:** same `user_id` always routes to the same backend (session affinity).

**Config management:**
- Routes, rate limits, transforms, auth rules stored in config service (etcd / DB).
- Gateway watches for changes; reloads in < 1s.
- Per-tenant overrides via routing rules.

**Observability:**
- Every request: structured log (request_id, route, status, latency, user_id, upstream).
- Metrics: per-route QPS, p50/p99 latency, error rate.
- Tracing: pass `traceparent` header; gateway span + per-filter spans.

**Multi-region:**
- Regional gateway fleets; each region has local config.
- Config replicated from a central store.
- Edge routing (GeoDNS / anycast) directs clients to nearest gateway.

## Scale & bottlenecks

- **Gateway becomes the bottleneck:** all traffic goes through. Mitigation: stateless design, scale horizontally, edge LB in front.
- **Filter hot path:** filter chain adds latency. Profile per-filter; pre-compile critical paths.
- **Stateful filters:** rate-limit needs shared state (Redis). Auth may need JWKS refresh. Mitigation: cache aggressively.
- **Config reload storm:** 10k routes reload at once. Mitigation: incremental reload, route-level versioning.
- **Tenant config sprawl:** 10k tenants × 100 routes = 1M entries. Off-box config service; gateway caches hot routes in RAM.

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Upstream down | Errors to client | Circuit breaker + retry budget + fallback |
| Redis down | Rate limit can't check | Fail open with metric |
| Auth service down | All requests fail | JWKS cache with TTL; serve from cache |
| Config push fails | Stale routes | Versioned config; health check on reload |
| Gateway node down | Some traffic fails | LB takes it out; clients retry |

## "What I'd build first and why"

**Envoy-style filter chain: TLS → auth (JWT) → rate limit (Redis) → routing → circuit breaker → observability.** Stateless gateways behind an L4 LB. Config in etcd with watch-based reload. Skip transformation in v1; most teams add it later.

The single highest-leverage thing is **making the gateway stateless** — every piece of state (rate limit, auth cache, config) lives in a shared service. Then you scale linearly.

## Follow-ups (real, reported)

1. **Envoy / Kong / Nginx** — name one, know its filter model.
2. **REST → gRPC translation** — when the gateway speaks both.
3. **JWT validation at the edge** — JWKS refresh, key rotation.
4. **Canary routing** — weighted splits, sticky by header.
5. **Circuit breaker integration** — gateway knows upstream health.
6. **Per-tenant config** — versioned routes, limits, transforms.
7. **BFF pattern** — separate gateway per client type (mobile vs web vs partner).
8. **WebSocket / streaming passthrough** — different lifecycle than HTTP.
9. **API versioning** — path-based / header-based / content-negotiation.
10. **Edge observability** — request_id propagation, structured logs, RED metrics.

## Tips (staff-level)

- **Name a real gateway.** Envoy, Kong, Nginx, AWS API Gateway. Know one well.
- **Walk the filter chain.** Show you understand ordering, hot-path performance.
- **Stateless design.** Every state lives elsewhere. Then you scale.
- **Quantify:** "100k req/s × 5ms = 500ms total CPU / node; 1000 nodes → 1M req/s".
- **Talk about canary routing.** Most candidates miss it; it's a key staff-level topic.

## Pitfalls

- **Business logic in the gateway.** Wrong place — slows every request.
- **Synchronous calls on the hot path.** Auth / rate limit calls should be cached.
- **No rate limiting.** Single user can DOS the system.
- **No circuit breaker.** Slow upstream backpressure → gateway OOMs.
- **Stateless but stateful in practice.** Route config in local file = inconsistency.

## Worked narration (3 min)

"Goal: 100k req/s, p99 < 5ms gateway overhead, 10k tenants with per-tenant config, 99.99% availability.

**Fleet:** 1000 stateless Envoy nodes behind an L4 LB. Each node runs the filter chain: TLS → JWT auth → rate limit (Redis) → routing → circuit breaker → observability.

**Routing:** path-based with canary support (`X-Canary: true` → 100% canary; default 95/5). Watch-based config reload from etcd.

**Auth:** validate JWT against JWKS (cached, refresh every 5m). Per-route auth required/optional.

**Rate limit:** Redis-backed token bucket per `(tenant, route)`. Local cache absorbs 90% of checks.

**Failure:** upstream down → circuit breaker fails fast (50ms) with cached 503. Redis down → rate limit fails open. Config push fails → serve cached routes + alert.

**First build:** Envoy + JWT + Redis rate limit + path routing + watch-based config. Add transform, canary, partner API later."

## Related

- [[14-load-balancer]] — L4 LB fronts the gateway fleet.
- [[02-rate-limiter]] — the rate-limit filter is a gateway-resident concern.
- [[15-cdn-edge-cache]] — CDN is the outer layer; gateway is the next.
- [[16-circuit-breaker-reliability]] — circuit breaker lives in the gateway.