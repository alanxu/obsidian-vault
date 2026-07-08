---
title: Embeddings & Cosine Similarity
slug: embeddings-and-similarity
area: RAG Concepts
source_q: "Anthropic 100-Q #11, #12"
companies: [Cohere, Perplexity, Glean, OpenAI]
difficulty: ★★★☆☆
related: ["[[09-vector-retrieval-failure]]", "[[13-hybrid-search]]", "[[llm-system-design/01-rag-with-citations]]"]
---

# Embeddings & Cosine Similarity

## Prompt
What is an embedding? Why is cosine similarity the common distance metric?

## Answer
An **embedding** maps text (or any input) to a **dense vector** in a learned space where **semantic similarity ≈ geometric proximity** — "cancel my plan" and "stop my subscription" land near each other even with no shared words. Produced by a **bi-encoder** trained (often contrastively) so related pairs are close and unrelated pairs far. This is what lets you retrieve by *meaning*, not keywords (the basis of vector search).

**Cosine similarity** measures the **angle** between two vectors (dot product normalized by magnitudes), so it captures **direction/semantic orientation** while ignoring magnitude. That matters because embedding *magnitude* often reflects token count / frequency, not meaning — cosine focuses on the semantic direction. (On normalized vectors, cosine and dot product rank identically, which is why many ANN indexes use inner product.)

## Tradeoffs
| Choice | Note |
|---|---|
| Cosine vs Euclidean | cosine ignores magnitude (usually wanted for text); L2 sensitive to it |
| Cosine vs dot product | identical ranking on normalized vectors; dot is cheaper |
| Embedding dim | higher = more expressive, more memory/latency |

## Follow-ups
- *"Why not keyword search?"* → embeddings handle **paraphrase/synonyms**; keywords (BM25) handle exact terms/IDs → use **both** ([[13-hybrid-search]]).
- *"Pick an embedding model?"* → by **Recall@k on your own corpus**, not a leaderboard; same model+version for query and corpus (version skew = garbage similarity).
- *"Cross-encoder vs bi-encoder?"* → bi-encoder embeds independently (cheap, pre-computable); cross-encoder scores a (query,doc) pair jointly (accurate, used for re-ranking → [[12-reranking]]).
- *"Matryoshka embeddings?"* → trained so prefixes of the vector are usable embeddings — truncate 3072→256 dims for a cheap first pass, full dims to refine; one model, tiered cost.
- *"How do you migrate embedding models on a live index?"* → dual-write new vectors, backfill in batches, A/B Recall@k old vs new, cut over per-collection — never mix versions in one similarity space.
- *"Is similarity symmetric for queries and docs?"* → not necessarily: retrieval models often train with instruction prefixes ("query: …" / "passage: …"); dropping them at inference silently degrades recall.

## Pitfalls
- Mixing embedding **model versions** in one index (incomparable vectors).
- Assuming cosine ≠ dot product (they rank the same on normalized vectors).
- Thinking embeddings capture exact tokens/IDs well — they don't (that's BM25's job).

## Tips
Define it as **"meaning → geometry; cosine compares direction, ignoring magnitude."** Immediately note the dense-misses-exact-terms gap to tee up hybrid search — the production-relevant point.
