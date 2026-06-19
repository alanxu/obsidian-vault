---
title: Self-Attention vs RNN (and attention complexity)
slug: self-attention-vs-rnn
area: LLM Fundamentals
source_q: "Anthropic 100-Q #1, #2"
companies: [Anthropic, OpenAI, Cohere, NVIDIA, general AI-eng]
difficulty: ★★★☆☆
related: ["[[03-kv-cache]]", "[[02-context-window-limits]]", "[[D0-areas-map]]"]
---

# Self-Attention vs RNN (+ attention complexity)

## Prompt
Why is self-attention better than RNNs for large models? What is the time/space complexity of attention?

## Answer
**RNNs are sequential and lossy.** They process tokens one at a time, carrying a fixed-size hidden state, so (1) training can't parallelize across the sequence, and (2) long-range dependencies degrade (vanishing/exploding gradients; information bottleneck through one state vector).

**Self-attention fixes both.** Every token attends to every other token **directly** and **in parallel**:
- **Parallelism** → the whole sequence is one matmul, so you can saturate GPUs and train on far more data/params. This scalability is *the* reason Transformers won.
- **Direct long-range paths** → any two tokens are one "hop" apart (path length O(1) vs O(n) for RNNs), so long-range dependencies are modeled well.
- **Content-based routing** → attention weights are data-dependent (query·key), not fixed.

**Complexity:** self-attention is **O(n²·d)** time and **O(n²)** memory in sequence length `n` (every token × every token), vs RNN's O(n·d²) sequential. That quadratic cost is the price of the all-pairs interaction — and the reason long context is expensive (→ [[02-context-window-limits]]).

## Tradeoffs
| | RNN | Self-attention |
|---|---|---|
| Parallelism | none (sequential) | full (one matmul) |
| Long-range | weak (bottleneck) | strong (O(1) path) |
| Cost in n | O(n) linear | **O(n²) quadratic** |
| Inductive bias | strong recency/order | weak (needs positional encodings) |

## Follow-ups
- *"How does attention know token order?"* → it doesn't inherently; **positional encodings** (sinusoidal/RoPE/ALiBi) inject order.
- *"How to beat O(n²)?"* → FlashAttention (same math, IO-aware, less HBM traffic — not lower complexity); sparse/linear attention; sliding-window; the KV cache (amortizes *decode*, → [[03-kv-cache]]).
- *"GQA/MQA?"* → share K/V heads across query heads to shrink the KV cache, trading a little quality for big memory savings.

## Pitfalls
- Saying attention is "faster" than RNN — it's more **parallel**, but **more expensive** per token (quadratic). Don't conflate the two.
- Forgetting positional encodings exist (attention is permutation-invariant without them).
- Quoting O(n) for attention — it's O(n²).

## Tips
Lead with **"parallelism + direct long-range paths, at a quadratic cost."** Mention the quadratic immediately — it sets up KV cache, long-context, and FlashAttention follow-ups, which is where staff signal lives.
