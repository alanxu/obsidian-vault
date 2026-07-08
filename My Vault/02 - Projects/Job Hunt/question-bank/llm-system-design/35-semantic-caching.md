---
title: Design a Semantic Caching Layer for LLM Calls
slug: semantic-caching
area: 8 — Observability, Cost & Reliability
companies: ["applied-AI everywhere", Robinhood, Cohere, "high-QPS LLM products"]
difficulty: ★★★☆☆
formats: [Live system design, follow-up inside gateway/RAG designs]
related: ["[[30-llm-gateway-router]]", "[[fundamentals/22-prompt-caching]]", "[[fundamentals/08-embeddings-and-similarity]]"]
added: 2026-07-08 (audit fill — reported standalone 2026 cost/latency question)
evidence: "GUIDE-LEVEL: 'what is semantic caching and how does it reduce cost/latency in RAG' appears in 2026 AI-eng interview question compilations. Company list = inference (any high-QPS LLM product); no company-specific candidate report."
---

# Design a Semantic Caching Layer

> "Cut LLM cost/latency by reusing answers to *similar* questions." **Open with the taxonomy** — three caches, often conflated: **exact-match** (hash of normalized prompt), **semantic** (embedding similarity of the *query*), **prefix/prompt cache** (KV-cache reuse *inside* the model, → [[fundamentals/22-prompt-caching]]). This card = the semantic layer; the interview trap is ignoring **false hits** and **context-dependence**.

## Problem
"1M q/day, many near-duplicates ('reset my password' asked 40K ways). Design the cache." Variants: cache inside a RAG pipeline (cache retrieval? generation? both), per-tenant caching, cache for an agent's tool results.

## Clarify first
- What's cacheable? Deterministic Q&A vs personalized/contextual answers (user data, time-sensitive)?
- Tolerance for a *wrong* cache hit (support answer vs financial advice)? Freshness/invalidation triggers (KB update, model/prompt version)?
- Hit-rate expectation — is the query distribution actually heavy-headed? (Measure first; if flat, don't build it.)

## Architecture
Request → normalize → **exact cache** (Redis, hash key) → miss → embed query (small fast model, ~10ms) → **vector lookup** (HNSW) among cached entries → similarity ≥ τ_high → serve cached · τ_low<s<τ_high → optional **cheap verifier** (small LLM: "same question?") → else miss → LLM → **write-behind**: store (query, embedding, answer, metadata: model+prompt version, KB version, tenant, TTL, hit-count). **Invalidation:** version keys (model/prompt/KB in the cache key) + TTL by content class + event-driven purge on KB change.

## Deep-dive — the false-hit problem
- Similarity ≠ same answer: "cancel my subscription" vs "cancelled subscription still charging?" embed close but need different answers. Mitigations: **high threshold** (tune on labeled pairs), **verifier model** in the gray zone, cache only **intent-classified** deterministic categories, exclude anything personalized.
- **Context-dependence:** same question, different user state → answer differs. Rule: cache key must include *everything the answer depends on* (tenant, locale, plan tier, KB version) — or don't cache. Personalization belongs *outside* the cached body (template + fill).
- **Threshold economics:** each τ trades hit-rate vs error-rate; plot both on labeled eval set; pick by cost of a wrong answer. Support bot: τ≈0.92+verifier; anything regulated: exact-match only.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Higher τ | fewer wrong hits vs lower hit rate |
| Verifier LLM in gray zone | accuracy vs +20–50ms and cost per lookup |
| Cache full answers vs templates | simple vs personalizable |
| TTL vs event invalidation | simple vs stale-window on KB changes |
| Global vs per-tenant cache | hit rate vs leakage risk (default per-tenant) |

## Numbers
Lookup: ~10ms embed + ~5ms ANN ≪ 1–5s generation · realistic hit rates: support/FAQ 20–60%, open-ended chat <10% (often not worth it) · saving = hit_rate × (LLM cost − lookup cost) · storage: 1M entries × (768-d fp16 + answer) ≈ few GB — cheap; the risk is quality, not cost.

## Eval
Hit rate + **false-hit rate** (sampled hits → LLM-judge "would fresh answer differ?") · latency saved p50 · $ saved/day · staleness incidents after KB updates · A/B: user satisfaction on cache-served vs fresh answers (the real test).

## Failure modes
Wrong-answer hits (the big one) · stale answers post-KB-update (version keys!) · **cross-tenant leakage** (cached answer contains tenant A's data, served to B) · cache poisoning (adversarial query caches bad answer served broadly) · embedding-model upgrade silently shifts similarity space (re-embed or flush) · negative caching of transient errors.

## Top follow-ups
- "How do you pick the threshold?" → labeled similar/different pairs; ROC of hit-rate vs false-hit; choose by cost of error.
- "Cache in RAG — where?" → three points: query→final-answer (this card), query→retrieved-docs (safer, still saves retrieval), prefix-cache the system prompt+few-shots (always).
- "Semantic vs prompt caching?" → different layers: semantic skips the call entirely (app layer); prompt caching cheapens the call (infra layer, exact-prefix only). Use both.
- "Personalized answers?" → exclude, or cache template + inject user fields; key on everything the answer depends on.
- "Invalidate on model upgrade?" → model+prompt version in key → natural flush; canary compare old-cache vs new-model before flush if cost matters.

## Related
[[30-llm-gateway-router]] (cache sits in the gateway) · [[fundamentals/22-prompt-caching]] (KV/prefix layer) · [[fundamentals/08-embeddings-and-similarity]] (why near≠same).
