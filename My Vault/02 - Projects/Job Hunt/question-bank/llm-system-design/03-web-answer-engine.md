---
title: Design a Web-Scale Answer Engine (Perplexity)
slug: web-answer-engine
area: 1 — Retrieval & Knowledge
companies: [Perplexity]
difficulty: ★★★★☆
formats: [Live system design]
related: ["[[01-rag-with-citations]]", "[[D0-areas-map]]"]
---

# Design a Web-Scale Answer Engine (Perplexity-style)

> RAG over the **live web** at 1.5B+ queries/month: crawl → index billions of pages → retrieve → generate a **cited** answer with real-time citation verification, p99 < ~2s.

## Problem
Given a query, return a synthesized, **cited** answer grounded in current web sources. Sub-problems: web crawl (freshness vs coverage), indexing billions of pages, retrieval + re-rank, citation verification against the actual source, low latency.

## Clarify first
- Freshness need (breaking news vs evergreen)? Latency SLA + streaming? Query volume?
- Open web vs curated sources? How strict must citations be?

## Architecture (3 planes)
- **Crawl/index (offline, continuous):** distributed crawler (politeness, dedup, quality filtering) → freshness-prioritized recrawl → parse → chunk → embed → **hybrid web index** (vector + inverted) + page store. Freshness tiers: hot (news, minutes) vs cold (recrawl days).
- **Serving (online):** query understanding/rewrite → retrieve top-N web chunks (hybrid) → re-rank → **assemble context with source handles** → stream a cited answer → **citation verification** (does the cited page actually support the claim?).
- **Quality:** click/citation-click signals, source-quality scoring, hallucinated-citation detection.

## Deep-dive — crawl freshness vs coverage + citation verification
- **Crawl:** can't recrawl the whole web constantly → prioritize by change rate + popularity + query demand; dedup near-identical pages; filter spam/low-quality. Shard frontier by domain hash; shared "seen" (Bloom/Redis).
- **Citation verification:** the model can cite a page it didn't actually use → verify each claim is **entailed** by the cited span (NLI/judge); drop/flag unsupported claims. This is Perplexity's differentiation.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Crawl freshness | coverage/cost vs staleness; tier by change rate |
| Index size | recall vs cost; quantize, shard |
| Verify citations | latency/cost vs trust (the product promise) |

## Eval
Answer faithfulness (cited-claim entailment), citation correctness, freshness lag on trending queries, p99 latency, click-on-citation rate.

## Failure modes
Hallucinated citations (kills trust) · stale answer on breaking news · crawler blocked/rate-limited · spam/SEO pollution in retrieval · slow verification blowing latency.

## Top follow-ups
- "Crawl billions of pages?" → prioritized recrawl, dedup, quality filter, sharded frontier.
- "Verify a cited source in real time?" → NLI/judge entailment of claim vs cited span; tier by stakes.
- "p99 < 2s with verification?" → stream the answer, verify async/inline on the top claims, cache hot queries.
- "SEO spam / content farms polluting answers?" → source-quality score (domain authority, spam classifier, historical citation-click rate) as a *retrieval feature* and a generation-time trust hint; demote, don't just filter (recall on long-tail queries).
- "Same query, breaking news 10 min ago?" → query classifier routes 'fresh' intents to a hot index + live search API fallback; blend recency into rank; show timestamps so staleness is visible rather than silent.
- "Multi-step questions ('compare X and Y's earnings')?" → decompose → parallel retrieval per sub-question → synthesis over notes; this is the boundary where the answer engine becomes [[33-deep-research-agent]].

## Numbers
Index: ~10⁹–10¹⁰ pages, hot tier recrawled in minutes, cold in days–weeks · latency budget: retrieve ~100–200ms, rerank ~50–100ms, TTFT ~300ms, verify inline on top-3 claims · cache hit on head queries 30–50% (news queries barely cache — freshness invalidates).

## Related
[[01-rag-with-citations]] · practical-coding [[practical-coding/12-multithreaded-web-crawler]] (the crawler component) · [[D0-areas-map]] Area 1.
