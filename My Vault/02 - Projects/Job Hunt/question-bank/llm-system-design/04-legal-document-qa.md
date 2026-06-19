---
title: Design a Legal Document Review / Q&A System (Harvey)
slug: legal-document-qa
area: 1 — Retrieval & Knowledge
companies: [Harvey]
difficulty: ★★★★☆
formats: [Live system design, Take-home design]
related: ["[[01-rag-with-citations]]", "[[29-guardrails-prompt-injection]]", "[[D0-areas-map]]"]
---

# Design a Legal Document Review / Q&A System (Harvey)

> RAG in a **high-stakes, auditable** domain: process 100k+ page documents, flag non-standard clauses, answer with **every conclusion traceable to a source span**. Errors carry legal liability → **abstention + verification** are mandatory.

## Problem
Review/answer over large legal corpora (contracts, case law). Variants: "flag non-standard clauses with high precision / low false-positive"; "every conclusion auditable to a source"; "handle 100k-page documents."

## Clarify first
- Cost of a wrong answer (high → must abstain + verify)? Auditability/regulatory requirements?
- Document scale per matter? Latency (interactive review vs batch)? Multi-tenant per law firm (data residency)?

## Architecture (3 planes)
- **Ingest:** layout-aware parsing (contracts have structure: sections, clauses, tables) → **clause-level chunking** preserving offsets → embed → hybrid index per matter/tenant, with strict tenant isolation.
- **Serving:** query → retrieve relevant clauses → re-rank → **grounded generation with span-level citations** → **verification pass** (every claim entailed by its cited span) → **abstain** if evidence weak. Clause-flagging = compare each clause to a standard-clause library (embedding similarity + classifier).
- **Quality:** expert-labeled golden set; precision-first thresholds; human-review queue for flagged items.

## Deep-dive — high-stakes grounding + auditability
- **Span-level citations:** resolve every claim to exact char offsets in the source doc; surface the span so a lawyer can verify.
- **Verification + abstention:** unverified claim → **block** (not just flag). Low retrieval confidence → "insufficient evidence," never guess.
- **Auditability:** log query, retrieved spans, prompt, model version, output for every answer; reproducible.
- **Tenant isolation:** per-firm namespaces; data residency; unauthorized matter content never reaches context.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Precision vs recall on clause flags | false positives waste lawyer time vs missed risk |
| Verify-then-answer | latency/cost vs liability |
| Long-doc: chunk vs long-context | retrieval precision vs whole-doc coherence (small-to-big) |

## Eval
Precision/recall on clause flags (precision-weighted), citation correctness, abstention quality, expert agreement. Expensive labels → curated golden set.

## Failure modes
Confident wrong answer (liability) · missed material clause · hallucinated citation · cross-tenant leak · long-doc context loss.

## Top follow-ups
- "Errors have legal liability — how?" → verify every claim, abstain on low confidence, span-level audit trail.
- "100k-page doc?" → clause chunking + small-to-big + retrieval (not whole-doc stuffing).
- "High precision, low false positive on clauses?" → standard-clause library + classifier + threshold by review cost.

## Related
[[01-rag-with-citations]] · [[29-guardrails-prompt-injection]] (governance) · [[D0-areas-map]] Areas 1 + 7.
