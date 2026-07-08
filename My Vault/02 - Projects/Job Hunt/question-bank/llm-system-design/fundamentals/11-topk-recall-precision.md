---
title: Top-K, Recall vs Precision in Retrieval
slug: topk-recall-precision
area: RAG Concepts
source_q: "Anthropic 100-Q #16, #17"
companies: [Cohere, Perplexity, Glean]
difficulty: ★★★☆☆
related: ["[[12-reranking]]", "[[14-rag-evaluation]]", "[[llm-system-design/01-rag-with-citations]]"]
---

# Top-K, Recall vs Precision

## Prompt
How do you choose top-K for retrieval? How do you balance recall and precision?

## Answer
**Top-K = how many candidates you pass forward.** The two-stage funnel resolves the recall/precision tension:
- **Stage 1 (retrieve) optimizes recall** — cast a **wide** net (K ≈ 50–100 candidates) so the right chunk is *somewhere* in the set. Missing it here is fatal; nothing downstream can recover.
- **Stage 2 (re-rank) optimizes precision** — a cross-encoder reorders those candidates; you keep the **top 3–8** for the LLM context (→ [[12-reranking]]).

So you don't pick one K — you use a **big K for recall, then a small K for precision**. Too-small retrieval K → recall misses; too-large final K → diluted context, more cost/latency, and "lost in the middle."

**Recall vs precision tradeoff:** more chunks in context = higher recall (the answer is more likely present) but lower precision (more distractors, more tokens, more chance the model latches onto an irrelevant chunk). Tune the final K to the **smallest set that keeps Recall@k high**.

## Tradeoffs
| Setting | Effect |
|---|---|
| ↑ retrieve K | ↑ recall, ↑ rerank latency (>100 rarely helps) |
| ↑ final K (context) | ↑ recall, ↓ precision, ↑ cost, lost-in-the-middle |
| Add reranker | ↑ precision at fixed recall |

## Follow-ups
- *"Right metric?"* → **Recall@k** for retrieval, **nDCG/MRR** for ranking, faithfulness for the end answer.
- *"Going above 100 candidates?"* → rarely helps, adds reranker latency.
- *"Order in the context?"* → put the best chunks first/last (lost-in-the-middle).
- *"Should K be fixed?"* → better: **similarity/score thresholding or adaptive K** — easy queries need 2 chunks, hard ones 10; fixed K wastes tokens or starves recall. Calibrate the threshold on the golden set.
- *"What if recall is high but answers are still wrong?"* → precision problem downstream: distractor chunks outrank gold in the LLM's attention → rerank harder, dedup near-duplicates (MMR), shrink final K.

## Pitfalls
- One K for everything (conflating recall and precision stages).
- Huge final context "to be safe" → distraction + cost + lost-in-the-middle.
- Not measuring Recall@k (flying blind on the binding metric).

## Tips
Answer with the **funnel**: "big K for recall, rerank, small K for precision." Naming Recall@k as the stage-1 KPI is the signal you understand where RAG quality is set.
