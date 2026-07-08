---
title: Reranking (cross-encoders)
slug: reranking
area: RAG Concepts
source_q: "Anthropic 100-Q #18"
companies: [Cohere, Perplexity, Glean, Harvey]
difficulty: ★★★☆☆
related: ["[[11-topk-recall-precision]]", "[[08-embeddings-and-similarity]]", "[[13-hybrid-search]]"]
---

# Reranking

## Prompt
Why do rerankers improve RAG? How do they differ from the first-stage retriever?

## Answer
The first stage (bi-encoder + ANN, or BM25) embeds query and document **independently**, so it can only compare pre-computed vectors — fast, but it misses fine-grained query–document interactions. A **cross-encoder reranker** feeds the **(query, document) pair together** through a transformer and outputs a single relevance score, so it can model **exact interactions** ("does *this* doc actually answer *this* query?"). That's much more accurate — but **O(N) model calls**, so you only run it on the **~50–100 candidates** from stage 1, never the whole corpus.

**Net:** retrieve cheap & wide (recall) → rerank expensive & narrow (precision) → keep top 3–8. Empirically, hybrid + RRF + cross-encoder rerank is the strongest cheap-ish combo (e.g., Recall@5 ~0.82 vs ~0.70 for hybrid alone).

## Tradeoffs
| | Bi-encoder (retrieve) | Cross-encoder (rerank) |
|---|---|---|
| Query–doc interaction | none (independent) | full (joint) |
| Cost | cheap, pre-computable | O(N) per query (~50–200ms) |
| Use | stage 1, whole corpus | stage 2, top candidates only |

## Follow-ups
- *"Latency?"* → reranking is often the 2nd-biggest online cost after the LLM; cache hot queries, distill a smaller reranker, or cap N.
- *"Which reranker?"* → bge-reranker, Cohere Rerank, Jina — pick by Recall@k on your corpus.
- *"Late interaction (ColBERT)?"* → token-level multi-vector; middle ground between bi- and cross-encoder (more storage, better quality).
- *"LLM-as-reranker?"* → prompt an LLM to score/listwise-rank candidates — strongest quality, highest cost/latency; practical as a distillation teacher for a small cross-encoder rather than in the hot path.
- *"When does reranking NOT help?"* → when stage-1 recall is the bottleneck (gold chunk not in the candidate set — reranker can't rank what isn't there) or candidates are near-duplicates; measure Recall@50 before buying precision.

## Pitfalls
- Trying to run a cross-encoder over the whole corpus (intractable — it's a *second* stage).
- Skipping reranking and over-stuffing context to compensate (worse precision).
- Forgetting reranker latency in the budget.

## Tips
One line: **"cross-encoders score query+doc jointly, so they're more precise but O(N) — run only on the top-50/100 candidates."** That's the retrieve-then-rerank insight.
