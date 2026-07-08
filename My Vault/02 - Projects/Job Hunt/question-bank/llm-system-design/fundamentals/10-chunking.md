---
title: Chunking — size and overlap
slug: chunking
area: RAG Concepts
source_q: "Anthropic 100-Q #14, #15"
companies: [Cohere, Perplexity, Harvey, Glean]
difficulty: ★★★☆☆
related: ["[[09-vector-retrieval-failure]]", "[[llm-system-design/01-rag-with-citations]]"]
---

# Chunking (size & overlap)

## Prompt
How do you choose chunk size? Why is chunk overlap useful?

## Answer
**Chunking splits documents into retrievable units.** It's the most under-rated RAG lever — bad chunks = bad retrieval, unfixable downstream.

**Size — the core tradeoff:** *small chunks → precise retrieval but fragmented context; large chunks → rich context but diluted embeddings and wasted tokens.* A single big chunk's embedding averages many topics, so it matches everything weakly. A tiny chunk may match precisely but lack the context to answer. Practical default: **structure-aware, ~300–500 tokens**, split on headings/paragraphs, with a **context header** (Title > Section) prepended so orphan chunks stay findable.

**Overlap (~10–20%):** carry a slice of the previous chunk into the next so an answer that **straddles a boundary** isn't cut in half — without overlap, a fact split across the cut is unretrievable from either chunk.

**Best of both — small-to-big:** embed small units for precise matching, but **return the surrounding parent** window/section to the LLM for enough context.

## Tradeoffs
| Strategy | When |
|---|---|
| Fixed-size + overlap | uniform text, baseline |
| Structure-aware | docs with headings (best ROI) |
| Semantic | topic drift within docs |
| Small-to-big | need precise match + context |

## Follow-ups
- *"Tune chunk size?"* → empirically, via **Recall@k** on a golden set — there's no universal number.
- *"Tables/code/PDFs?"* → layout-aware parsing; don't split tables; preserve offsets for citations.
- *"Overlap downside?"* → duplicate near-identical chunks → dedup at context assembly (MMR).
- *"Contextual retrieval (Anthropic-style)?"* → prepend an LLM-generated situating sentence to each chunk before embedding ("This chunk is from X's Q3 filing, discussing…") — big recall gains on ambiguous chunks; ingest-time LLM cost, made cheap by prompt caching.
- *"Late chunking?"* → embed the full document through a long-context embedder first, *then* pool per-chunk — chunk vectors inherit document context without any header engineering.

## Pitfalls
- Naïve fixed-size splitting that cuts mid-sentence / mid-table.
- No overlap → boundary-straddling answers lost.
- Orphan chunks with no context header (don't match).
- Treating chunk size as fixed instead of tuned on your data.

## Tips
State the **precision-vs-context tradeoff** in one line, then default to **"structure-aware ~300–500 tok, 15% overlap, small-to-big, tuned by Recall@k."** That shows you'd measure, not guess.
