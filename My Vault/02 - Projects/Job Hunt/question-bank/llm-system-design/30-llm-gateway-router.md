---
title: Design an LLM Gateway / Router (caching, fallback, cost)
slug: llm-gateway-router
area: 8 — Observability, Cost & Reliability
companies: [applied-AI everywhere, Anthropic, OpenAI, Anysphere]
difficulty: ★★★★☆
formats: [Live system design]
related: ["[[06-llm-inference-serving-platform]]", "[[31-llm-observability-cost]]", "[[D0-areas-map]]"]
---

# Design an LLM Gateway / Router

> The control plane in front of model providers: route, cache, fall back, rate-limit, and meter cost — so the app is decoupled from providers and doesn't go down or broke. The practical answer to "multi-model, multi-provider, reliable, cheap."

## Problem
"Design a gateway that sits between apps and multiple LLM providers (OpenAI, Anthropic, self-hosted) handling routing, caching, fallback, rate limiting, and cost." Applied-AI infra everywhere.

## Clarify first
- Multiple providers/models? Optimize for cost, latency, or quality routing? Cache acceptable (staleness)?
- Multi-tenant quotas? SLA / failover requirements? Streaming?

## Architecture
App → **gateway**: auth/quota → **cache check** (exact + semantic) → **router** (pick model by cost/quality/capability) → provider call with **retries/timeout/circuit-breaker** → **fallback** provider on failure → stream back → **log tokens+cost+latency** (→ [[31-llm-observability-cost]]). Unified API across providers.

## Deep-dive — cache, route, fallback
- **Caching:** **exact** (hash of prompt) + **semantic** (embed prompt, reuse near-duplicate answers) + **prefix caching** (Area 2). Caching a hot fraction cuts spend 30–70%. Watch **semantic-cache false hits** (wrong answer reused).
- **Routing:** cheap model by default, **escalate hard queries** to a frontier model (classify difficulty); route by capability (code → code model), cost, latency, or A/B.
- **Fallback + reliability:** provider B if A errors/times out; **circuit breaker**; **graceful degradation** (smaller model / cached / BM25-only) when premium path is down; multi-region.
- **Quotas/rate limits:** per-tenant token budgets + fair limiting; protect against retry storms.
- **Unified interface:** one API; normalize across providers (decouples app from any single vendor).

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Cache aggressiveness | cost/latency savings vs staleness + semantic false hits |
| Model routing | cost (cheap default) vs quality risk on misroute |
| Fallback quality | availability vs degraded answer |
| Gateway hop | control/observability vs added latency |

## Numbers
Tokens dominate the bill → caching hot traffic cuts 30–70%. Report p50/**p99**. Circuit-break + budget to stop retry-storm cost blowups. Rollback/canary in minutes.

## Failure modes
Semantic-cache false positives (stale/wrong) · provider outage with no fallback · retry-storm cost blowup · gateway as a single point of failure · misrouting hard queries to a weak model · PII in logs.

## Top follow-ups
- "Cut cost?" → semantic+prefix cache + route to cheaper model + trim context + per-tenant quotas.
- "Provider goes down?" → multi-provider fallback + circuit breaker + degrade to cached/smaller.
- "Route smartly?" → classify difficulty → cheap default, escalate hard; route by capability.
- "Cache safely?" → exact for identical; semantic with a high similarity threshold + monitoring.
- "How does the difficulty classifier work and what if it's wrong?" → small model / heuristics (length, domain, code-detection, past-failure lookup) with ~10ms budget; misroutes show up as regeneration/thumbs-down on cheap-model answers → feed those back as router training data; keep an escalate-on-user-retry path so a misroute costs one bad answer, not a stuck user.
- "Streaming through the gateway?" → SSE pass-through with token counting on the fly, mid-stream failover is ugly (provider dies at token 500 → restart on fallback and replay? dedupe by request-id, accept the latency hit) — mention that failover mid-generation is a design decision, not free.
- "Semantic-cache design in depth?" → own card: [[35-semantic-caching]] (thresholds, false hits, invalidation).
- "Data residency / compliance routing?" → routing is also a *policy* function: EU tenants → EU-region providers, no-training-clause providers for sensitive tenants, PII-detected requests pinned to self-hosted — the router is where compliance becomes enforceable code.

## Related
[[06-llm-inference-serving-platform]] (the backends) · [[31-llm-observability-cost]] · [[D0-areas-map]] Area 8.
