---
title: Design a RAG System with Citations
slug: rag-with-citations
area: 1 — Retrieval & Knowledge
companies: [Perplexity, Cohere, Harvey, Glean, Anthropic, OpenAI]
difficulty: ★★★★☆
formats: [Live system design, Take-home design]
related: ["[[D1-rag-with-citations]]", "[[D0-areas-map]]", "[[05-semantic-hybrid-search]]"]
---

# Design a RAG System with Citations

> **Full worked solution:** [[D1-rag-with-citations]] (talk-track, architecture diagram, all deep-dives, eval, follow-ups). This card is the index/summary.

## Problem
"Make an LLM answer over *our* corpus, with every claim traceable to a source." Variants: "production RAG for 10M docs at 1K QPS"; "cite every sentence"; "auditable answers."

## Anchor
*RAG is a retrieval problem wearing a generation hat — most failures are retrieval failures.* Retrieval is a funnel: wide cheap net → re-rank → LLM on survivors only.

## Architecture (one line)
Offline: parse → **chunk** (structure-aware ~300–500 tok) → embed → **HNSW vector + BM25 + doc store**. Online: query rewrite + **ACL filter** → **hybrid retrieve (dense+sparse) → RRF (k=60) → cross-encoder re-rank → context assembly (citation handles)** → grounded generation → **citation verification (NLI/judge)**.

## Top follow-ups (full answers in [[D1-rag-with-citations]] §13)
- Dense or sparse? → both, hybrid + RRF.
- Stop hallucinations? → fix retrieval first → ground+abstain → post-hoc citation verification.
- 1B chunks? → IVF-PQ, shard, quantize, two-stage.
- Per-user permissions? → ACL predicate *inside* the query, never post-filter.
- How do you know it works? → Recall@k offline + faithfulness online; decompose to isolate retrieval vs generation.

## Companies
Perplexity (web answer engine), Cohere (enterprise), Harvey (legal auditability), Glean (enterprise ACL), Anthropic/OpenAI (applied). See [[02-enterprise-search-acl]], [[03-web-answer-engine]], [[04-legal-document-qa]] for the company-specific skins.
