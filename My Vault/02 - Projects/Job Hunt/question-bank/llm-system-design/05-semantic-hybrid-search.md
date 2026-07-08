---
title: Design a Semantic / Hybrid Search System
slug: semantic-hybrid-search
area: 1 — Retrieval & Knowledge
companies: [general, Cohere, big-tech]
difficulty: ★★★☆☆
formats: [Live system design]
related: ["[[01-rag-with-citations]]", "[[23-embedding-pipeline-incremental]]", "[[24-recommendation-ranking-system]]"]
---

# Design a Semantic / Hybrid Search System

> Retrieval without the generation half — search results (not answers): embeddings + lexical, ANN at scale, learned ranking. The substrate under RAG and recommendations. Variant: **type-ahead/autocomplete** (low-latency prefix ranking).

## Problem
Given a query, return ranked relevant items from a large corpus. Hybrid lexical + semantic; learned ranking from signals. Variants: product search, doc search, type-ahead suggestions.

## Clarify first
- Corpus size + QPS + latency SLA (type-ahead needs <100ms)? Personalized?
- What signals exist for learning-to-rank (clicks, purchases)? Freshness?

## Architecture (2 planes)
- **Index (offline):** embed items (bi-encoder) → **ANN index (HNSW/IVF-PQ)** + **inverted index (BM25)** + feature store for ranking features. Incremental upsert ([[23-embedding-pipeline-incremental]]).
- **Serving (online):** query → (dense + sparse) candidate retrieval → **fuse (RRF)** → **learning-to-rank re-ranker** (gradient-boosted trees or a neural ranker over features: relevance, popularity, personalization, freshness) → top-k.

## Deep-dive — two-stage retrieve-then-rank
- **Stage 1 (recall):** cheap, high-recall candidate generation (ANN + BM25 → hundreds).
- **Stage 2 (precision):** expensive learned ranker over rich features on the candidates only. This split is the canonical search/recsys architecture.
- **Type-ahead variant:** prefix trie / FST + popularity + a fast ranker; aggressive caching; <100ms.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Dense vs sparse vs hybrid | semantics vs exact-match; hybrid wins |
| HNSW vs IVF-PQ | recall+latency vs memory at scale |
| GBT vs neural ranker | interpretability/speed vs ceiling |

## Eval
Offline: **nDCG, MRR, Recall@k**. Online: CTR, session success, conversion. A/B every ranking change.

## Failure modes
Vocabulary mismatch (pure dense) · exact-ID misses · stale index · feedback loops (popular gets more popular) · latency blowup at high QPS.

## Top follow-ups
- "Dense or sparse?" → hybrid + RRF; dense for paraphrase, sparse for exact tokens/IDs.
- "Personalize?" → user/context features into the stage-2 ranker; careful with cold start.
- "Type-ahead <100ms?" → prefix structure + cache + lightweight ranker.
- "Where does the training data for LTR come from?" → clicks with **position-bias correction** (inverse propensity weighting or randomization buckets) — raw clicks teach the ranker to reproduce the current ranking, not relevance.
- "Query understanding layer?" → spell-correct → intent/category classify → entity extraction → (optional) LLM rewrite for tail queries; head queries skip straight to cache. Tail is where semantic retrieval earns its keep — head queries are memorized anyway.
- "Filters + ANN (price < $50, in-stock)?" → pre-filtered ANN (filter-aware HNSW / partitioned indexes), never post-filter top-k — narrow filters silently empty your results (same principle as ACL in [[02-enterprise-search-acl]]).

## Numbers
Two-stage economics: ANN+BM25 over 10⁸ items ~20–50ms → 500 candidates → LTR ~10–20ms → top 20 · type-ahead: <100ms end-to-end, so trie/FST + cache only (no ANN in the hot path) · index refresh: full nightly + incremental upserts ([[23-embedding-pipeline-incremental]]).

## Related
[[01-rag-with-citations]] · [[24-recommendation-ranking-system]] (same retrieve-then-rank) · [[23-embedding-pipeline-incremental]].
