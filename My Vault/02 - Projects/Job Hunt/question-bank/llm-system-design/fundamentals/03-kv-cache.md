---
title: KV Cache — what it is and why it speeds inference
slug: kv-cache
area: LLM Fundamentals
source_q: "Anthropic 100-Q #4, #5"
companies: [NVIDIA, OpenAI, Anthropic, Fireworks, Together]
difficulty: ★★★★☆
related: ["[[01-self-attention-vs-rnn]]", "[[02-context-window-limits]]", "[[llm-system-design/06-llm-inference-serving-platform]]"]
---

# KV Cache

## Prompt
What is the KV cache, and why does it speed up inference?

## Answer
Autoregressive decoding generates one token at a time; each new token must attend to **all previous tokens**. Naively, step `t` recomputes the keys (K) and values (V) for all `t` prior tokens → O(t) work per token → O(n²) to generate n tokens.

The **KV cache stores the K and V vectors for every past token** so they're computed **once** and reused. Then each new token only computes **its own** Q/K/V and attends against the cached K/V → **O(1) recompute per step** (O(n) total instead of O(n²)). That's the speedup.

The cost is **memory**: cache size = `2 × layers × kv_heads × head_dim × seq_len × batch × bytes`. At long context × large batch it's tens of GB and becomes the binding constraint on how many requests fit on a GPU.

## Tradeoffs
| | Without KV cache | With KV cache |
|---|---|---|
| Compute/token | O(t) recompute | O(1) |
| Memory | low | **high, grows with seq×batch** |
- This is why decode is **memory-bandwidth-bound** (reloading the growing cache), while prefill is compute-bound — a key serving insight (→ [[llm-system-design/06-llm-inference-serving-platform]]).

## Follow-ups
- *"Shrink the KV cache?"* → **GQA/MQA** (fewer KV heads), **quantize** the cache (int8), **PagedAttention** (no fragmentation + sharing), **prefix caching** (reuse a shared system-prompt's KV).
- *"What's prefill vs decode?"* → prefill processes the prompt in one parallel pass (compute-bound); decode generates tokens serially, each reloading the KV cache (memory-bound).
- *"Memory math for a 70B at 8k context?"* → walk it concretely: 80 layers × 8 KV heads (GQA) × 128 head-dim × 8192 tokens × 2 (K+V) × 2 bytes (fp16) ≈ **2.7 GB per sequence** → batch 16 ≈ 43 GB, which crowds the weights on an 80GB GPU. Without GQA (64 heads) it's 8× worse — that's *why* GQA exists.
- *"Speculative decoding and the cache?"* → draft tokens are verified in one parallel pass; accepted tokens append their K/V — decode becomes partially parallel with identical outputs.

## Pitfalls
- Saying it "caches the output tokens" — it caches **K and V activations**, not tokens/logits.
- Ignoring the memory cost (the whole serving-design tension).
- Confusing it with prefix caching (prefix caching *reuses* KV across requests; KV cache is *within* one generation).

## Tips
Answer in two beats: **"avoids recomputing past K/V → O(1)/token instead of O(n²); the cost is memory, which dominates serving."** Then offer GQA/paged-attention as the mitigations — that's the inference-serving bridge interviewers love.
