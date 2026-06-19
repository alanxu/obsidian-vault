---
title: Hybrid Search (BM25 + dense)
slug: hybrid-search
area: RAG Concepts
source_q: "Anthropic 100-Q #19, #20"
companies: [Cohere, Glean, Perplexity, Harvey]
difficulty: ★★★☆☆
related: ["[[08-embeddings-and-similarity]]", "[[09-vector-retrieval-failure]]", "[[12-reranking]]"]
---

# Hybrid Search (BM25 + dense)

## Prompt
How do you combine BM25 and vector search? Pros and cons of hybrid retrieval?

## Answer
**Dense** (embeddings) wins on paraphrase/semantics; **sparse** (BM25, lexical) wins on exact terms/IDs/jargon. Their failure modes are complementary, so **run both and fuse**. The robust fusion is **Reciprocal Rank Fusion (RRF)** — combine by **rank**, not score, so you don't have to calibrate an unbounded BM25 score against a 0–1 cosine:

`RRF(d) = Σ_retrievers 1 / (k + rank_r(d))`, with **k = 60**.

Typical: BM25 top-50 + dense top-50 → RRF → top-100 → cross-encoder rerank → top 3–8. This catches the cases dense misses (exact tokens) and BM25 misses (paraphrase).

**Pros:** higher recall across query types; robust default. **Cons:** more infra (two indexes), more moving parts to tune, slightly more latency.

## Tradeoffs
| | Dense only | Sparse only | Hybrid + RRF |
|---|---|---|---|
| Paraphrase | ✓ | ✗ | ✓ |
| Exact terms/IDs | ✗ | ✓ | ✓ |
| Infra | 1 index | 1 index | 2 indexes + fusion |

## Follow-ups
- *"Why RRF over weighted score fusion?"* → rank-based, no score calibration; robust. Weighted fusion works if you've calibrated scores.
- *"Then rerank?"* → yes — RRF for recall, cross-encoder for precision (→ [[12-reranking]]).
- *"Why k=60?"* → standard smoothing constant; dampens the influence of low ranks.

## Pitfalls
- Linearly adding a cosine (0–1) and a BM25 score (unbounded) without calibration → one dominates.
- Assuming dense alone suffices (whiffs on exact IDs/codes).
- Forgetting RRF still needs a reranker for top-end precision.

## Tips
Say **"both, fused with RRF (k=60), then rerank"** — and name *why* (dense=paraphrase, sparse=exact). The rank-based-no-calibration point shows you've actually built it.
