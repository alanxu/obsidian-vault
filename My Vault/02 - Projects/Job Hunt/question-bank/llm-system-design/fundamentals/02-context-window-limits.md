---
title: Why Context Windows Can't Grow Unboundedly
slug: context-window-limits
area: LLM Fundamentals
source_q: "Anthropic 100-Q #3"
companies: [Anthropic, OpenAI, NVIDIA, general AI-eng]
difficulty: ★★★☆☆
related: ["[[01-self-attention-vs-rnn]]", "[[03-kv-cache]]", "[[10-chunking]]"]
---

# Why Context Windows Can't Grow Unboundedly

## Prompt
Why can't the context window just keep growing? What breaks at long context?

## Answer
Three pressures:
1. **Compute/memory cost is quadratic.** Attention is O(n²) (→ [[01-self-attention-vs-rnn]]); doubling context ~4×'s attention cost. Prefill compute and the **KV cache** memory (linear in n × batch) blow up — KV cache becomes the dominant GPU-memory consumer at long context.
2. **Quality degrades — "lost in the middle."** Models attend best to the **start and end** of the context; information buried in the middle is under-used, so just stuffing more tokens doesn't linearly help and can hurt.
3. **Training distribution.** A model trained on ≤k tokens extrapolates poorly beyond k; position encodings (RoPE) need scaling tricks (interpolation) to extend, often with quality cost.

So long context is **expensive and has diminishing/negative returns** — which is exactly why **retrieval (RAG)** exists: fetch the few relevant chunks instead of dumping everything (→ [[10-chunking]], [[llm-system-design/01-rag-with-citations]]).

## Tradeoffs
| Lever | Gains | Costs |
|---|---|---|
| Longer context | more in-context info, fewer retrieval misses | O(n²) compute, big KV cache, lost-in-the-middle |
| RAG (short context) | cheap, fresh, citable | retrieval can miss the right chunk |
| Context compression/summary | fits more "effective" info | lossy |

## Follow-ups
- *"Long context vs RAG — when which?"* → RAG for large/fresh/changing corpora + citability; long context for a single document/coherent reasoning where retrieval would fragment it.
- *"How do models extend context (RoPE scaling)?"* → position interpolation / NTK-aware scaling + continued training; quality often drops at the extreme.
- *"Cut long-context cost?"* → GQA/MQA (smaller KV), paged attention, prefix caching, chunked prefill.
- *"How do you measure long-context quality?"* → needle-in-a-haystack is necessary-but-weak (pure lookup); RULER-style multi-needle/aggregation tasks expose the real gap — **effective context < advertised**, degrading gradually ("context rot"), not at a cliff.
- *"Million-token windows exist — is RAG dead?"* → no: you pay the whole window per call (cost + latency scale with tokens), and freshness/ACL/citability still need retrieval. Long context raises the RAG cutoff; it doesn't remove it.

## Pitfalls
- Claiming "bigger context = better" — ignores cost and lost-in-the-middle.
- Forgetting the KV-cache memory blowup (people only cite compute).

## Tips
Frame it as **cost (quadratic + KV cache) × quality (lost-in-the-middle) × training-distribution** — then pivot to "this is why RAG exists," which bridges to the highest-value area.
