---
title: Why Vector Retrieval Fails
slug: vector-retrieval-failure
area: RAG Concepts
source_q: "Anthropic 100-Q #13"
companies: [Perplexity, Cohere, Glean, Harvey]
difficulty: ★★★☆☆
related: ["[[08-embeddings-and-similarity]]", "[[13-hybrid-search]]", "[[10-chunking]]"]
---

# Why Vector Retrieval Fails

## Prompt
Why does vector (semantic) retrieval sometimes fail to find the right document?

## Answer
Common failure modes:
1. **Exact-term / rare-token misses** — dense embeddings blur exact identifiers (error code `TS-4021`, a SKU, a statute number, a function name). Semantically "near" isn't good enough when the user needs that exact token → **BM25/hybrid** fixes this.
2. **Chunking destroyed the answer** — the relevant span got split across chunks, or the chunk lost its context (orphaned without its heading), so its embedding doesn't match the query (→ [[10-chunking]]).
3. **Query–document asymmetry** — a short keyword query and a long document embed differently; the embedding of "RTO policy?" may not sit near a verbose policy paragraph (→ query rewriting / HyDE).
4. **Embedding model weakness / domain shift** — a general model on specialized jargon (legal/medical/code) embeds poorly; **version skew** between query and corpus embeddings ruins similarity.
5. **ANN approximation** — the index (HNSW/IVF) trades recall for speed; a low `efSearch`/few probes can skip the true nearest neighbor.

## Tradeoffs
| Lever | Helps | Cost |
|---|---|---|
| Add BM25 (hybrid) | exact terms | more infra |
| Better chunking | context preserved | tuning |
| Query rewrite/HyDE | asymmetry | extra LLM call |
| Higher ANN recall | fewer misses | latency |

## Follow-ups
- *"How do you know retrieval failed (not generation)?"* → **Recall@k** on a golden set isolates retrieval; faithfulness isolates generation.
- *"Fix exact-match misses?"* → hybrid (dense + BM25) + RRF.
- *"Fix asymmetry?"* → query rewriting, HyDE (embed a hypothetical answer), better chunk context headers.

## Pitfalls
- Blaming the LLM for a hallucination that's really a **retrieval miss** (the #1 RAG misdiagnosis).
- Assuming dense retrieval covers exact tokens.
- Ignoring ANN recall settings as a cause.

## Tips
Group the causes as **"exact-term miss · chunking · query asymmetry · model/version · ANN recall."** Then say "most RAG hallucinations are retrieval failures, so I'd measure Recall@k first" — that's the staff diagnosis.
