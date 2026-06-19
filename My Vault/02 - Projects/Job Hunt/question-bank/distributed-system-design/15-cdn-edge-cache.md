---
title: "CDN & Edge Cache"
slug: cdn-edge-cache
type: distributed-system-design
tier: "3 — API & traffic layer"
companies: [Cloudflare, Akamai, AWS CloudFront, Fastly, Google Cloud CDN, Netflix Open Connect, Meta]
difficulty: ★★★☆☆
frequency: high
formats: [Onsite·SD, Mock]
time-box: 25–35 min
tags: [cdn, edge, cache, geo-routing, purge, tiered-cache, anycast]
related: ["[[14-load-balancer]]", "[[13-api-gateway]]", "[[07-object-storage-blob]]"]
companies-likely: [Cloudflare, Fastly, Akamai, AWS CloudFront, Netflix, Meta]
star: true
---

# CDN & Edge Cache

**One-liner:** A globally distributed network of caches that serves content from the edge closest to the user, with intelligent routing, tiered caching, and instant purge.

## Problem framing

Asked when latency / global reach / DDoS resilience matter — i.e., always. Variants: "Design Cloudflare", "Design a video CDN like Netflix Open Connect", "Design an edge cache for a global app". The interviewer wants to see how you think about geography, caching, and origin protection.

**Variants:**
- "Design a CDN" (general — Cloudflare, CloudFront)
- "Design a video CDN" (Netflix Open Connect, YouTube)
- "Design an edge cache layer" (in front of your origin)
- "Design a tiered cache" (Cloudflare's regional + edge model)

## Requirements (clarify first)

- **Functional:** serve cached content; fall through to origin on miss; purge / invalidate; dynamic content routing.
- **Non-functional:**
  - Latency: p99 < 50ms from any continent
  - Cache hit ratio: > 95% for static, lower for dynamic
  - Origin load: < 5% of edge traffic
  - Throughput: millions of req/s per region
- **Constraints:** cacheable content (static / dynamic / streaming); freshness (TTL); purge capability.
- **Out of scope:** content delivery for non-HTTP (mention).

## Capacity estimation

- 100M MAU × 50 req/day = 5B req/day = 60k QPS avg, 500k QPS peak.
- 100 PoPs × 5k QPS each.
- 1PB working set in edge cache; eviction policy.
- Origin receives < 1% of traffic (cache hit ratio > 99%).

## High-level architecture

```
                              Tier 1: Regional cache
                              (a few per region)
                                       │
                                       ▼
Clients ──► Edge PoPs (Tier 2: 100s worldwide) ──► Origin
            (anycast IP,                          (your app)
             TLS term,                             
             simple cache)                          
```

**Tiered cache:** edge (Tier 2, leaf nodes) hit misses go to regional (Tier 1, mid-tier) before reaching origin. Saves origin bandwidth by ~10×.

## API / interfaces

```
POST /v1/cache/purge
{ "url": "/static/app.js", "purge_all": false }
→ 204

POST /v1/cache/purge
{ "tag": "release-v2" }   # tag-based purge
→ 204

GET /v1/cache/stats?region=us-east
→ { "hit_ratio": 0.97, "requests": ..., "bytes_served": ... }
```

## Deep dive #1 — Routing, anycast, GeoDNS

**Anycast:**
- Same IP announced from every PoP via BGP.
- Routers direct traffic to the *nearest* (in BGP terms) PoP.
- Used by Cloudflare, Fastly. **Pro:** fast, no DNS lookup. **Con:** hard to control which PoP you land on (depends on routing).

**GeoDNS:**
- DNS server returns different IPs based on client location.
- **Pro:** explicit control. **Con:** DNS caching can pin clients to a wrong region.

**Unicast + LB:**
- Each PoP has a unique IP; load balancer at the PoP distributes.
- More control, more ops.

**POP-to-origin:**
- Long-haul traffic: PoP connects to origin over public internet or private backbone (Cloudflare's Argo, Meta's Express Backbone).
- Private backbone: ~30-50% latency reduction vs public internet.

**Tiered cache flow:**
1. Request lands at edge PoP.
2. Cache miss → edge asks regional cache.
3. Regional cache miss → fetch from origin.
4. Both caches populated on the way back.

## Deep dive #2 — Caching strategies

**Cache key:**
- Default: `host + path + (query)`. Same URL → same cache entry.
- Variations: vary by header (`Accept-Encoding`, `Accept-Language`), vary by cookie (logged-in users).
- **Vary-by-cookie is the cache-killer.** Strip cookies at the edge; pass session info in a header set by the gateway.

**Cache control:**
- HTTP `Cache-Control: max-age=N, s-maxage=N, public, private`.
- `s-maxage` is the shared-cache (CDN) TTL; `max-age` is the browser TTL.
- `private` → don't cache in CDN; only browser.
- `no-store` → don't cache anywhere.

**Cache invalidation:**
- **TTL-based:** expires after N seconds. Simple, but stale up to TTL.
- **Active purge:** explicit `purge /url` API. Instant.
- **Tag-based purge:** tag entries at write; `purge ?tag=...` removes all entries with the tag. Used by Cloudflare / Fastly.
- **Soft purge:** mark stale, but serve from cache while refetching in background.

**Tiered cache invalidation:**
- Purge edge → push invalidation to regional → regional evicts.
- Tag-based: tag store is the source of truth; edges pull on tag purge.

**Edge compute (Cloudflare Workers / Fastly Compute@Edge):**
- Run JavaScript / WASM at the edge.
- Use cases: A/B test, redirect, header rewrite, simple auth.
- Cold-start latency is the killer — keep workers warm.

**Streaming / large object caching:**
- Range requests: cache by range, not whole object.
- HLS / DASH: cache manifest short, cache segments long.
- Video: byte-range serving from edge; partial cache hit acceptable.

## Scale & bottlenecks

- **Origin protection:** origin is the bottleneck if cache miss ratio is high. Tiered cache + origin shield + aggressive TTLs.
- **Cold cache:** new deployment → cache miss storm → origin overwhelms. Mitigations: stale-while-revalidate, pre-warm, canary at edge.
- **Hot key (a viral URL):** all edge nodes fetch the same URL → origin stampede. Mitigations: request coalescing at origin, edge-side prefetch.
- **PoP failure:** anycast re-routes automatically; but if regional cache is down, edges flood origin. Mitigations: regional cache HA, origin shield.
- **Geo-fencing / data residency:** some content can't leave certain regions. Edge enforces.

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Origin down | All misses fail | Stale-while-revalidate; cached stale responses |
| PoP down | Traffic rerouted | Anycast + LB health check |
| Cache poison | Wrong content served | Purge + signing (HMAC) for sensitive content |
| DDoS | Origin overwhelmed | Edge absorbs; rate limit; WAF |
| Cold cache (deploy) | Origin stampede | Pre-warm, stale-while-revalidate |

## "What I'd build first and why"

**Anycast edge PoPs + tiered cache (edge → regional → origin) + TTL + active purge API.** Skip edge compute in v1 — most teams don't need it.

The single highest-leverage thing is **the cache key + Vary strategy** — getting it wrong gives you 20% hit ratio instead of 95%. Cookies, query strings, and headers are the killers.

## Follow-ups (real, reported)

1. **Tiered cache** — edge → regional → origin; the math on origin bandwidth.
2. **Cache key + Vary** — what's in the key, what breaks hit ratio.
3. **Active purge + tag-based** — instant invalidation patterns.
4. **Stale-while-revalidate** — serve stale, refresh async.
5. **Cold cache storm** — pre-warm, canary, shield.
6. **Edge compute** — Workers / Compute@Edge; use cases + cold-start.
7. **Range requests** — for video / large objects.
8. **HLS / DASH** — manifest + segment caching.
9. **Geo-fencing + data residency** — keep content in region.
10. **DDoS protection** — edge as the shield.

## Tips (staff-level)

- **Name the cache key + Vary strategy** — it's the most-asked follow-up.
- **Tiered cache math:** "5% miss at edge, 20% miss at regional = 1% origin hit ratio".
- **Stale-while-revalidate** — staff signal; means you've run a real CDN.
- **Origin shield / pre-warm.** Cold cache is a real ops problem.
- **Quantify:** "100 PoPs, 1PB edge cache, 95%+ hit ratio, 500k QPS peak".

## Pitfalls

- **Default cache key without thinking about Vary.** Cookies, query strings, headers kill hit ratio.
- **No tiered cache.** Edge → origin directly = origin melts on miss storms.
- **No purge.** Stale content forever.
- **No origin protection.** Cache miss during deploy = outage.
- **No stale-while-revalidate.** Origin down = total cache miss = 100% errors.

## Worked narration (3 min)

"Goal: 100 PoPs worldwide, p99 < 50ms, cache hit ratio > 95%, origin load < 5% of edge traffic.

**Topology:** Tier 2 edge PoPs (anycast IP) front Tier 1 regional caches, front origin. Cache miss: edge → regional → origin.

**Routing:** anycast for clients → edge PoP. Private backbone for PoP-to-origin (Cloudflare Argo / Meta backbone).

**Cache key:** `host + path + Vary: Accept-Encoding`. Strip cookies at the edge; pass session in a header.

**Invalidation:** TTL + active purge API + tag-based purge (tags set on cache write, purge by tag).

**Cold cache:** stale-while-revalidate (serve stale, refresh async) + pre-warm on deploy.

**Edge compute (v2):** Workers for redirects, A/B test routing, header rewrite.

**Failure:** origin down → serve stale. PoP down → anycast re-routes. DDoS → edge absorbs + WAF.

**First build:** anycast edges + tiered cache + TTL + purge API + stale-while-revalidate. Skip edge compute initially."

## Related

- [[14-load-balancer]] — edge is the outer LB.
- [[13-api-gateway]] — gateway sits behind CDN for dynamic / auth-required requests.
- [[07-object-storage-blob]] — origin is often object storage for static content.