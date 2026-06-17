---
tags: [job-hunt, interview-prep, track, ml-fundamentals, llm]
track: "Track E — ML / LLM fundamentals"
plan-section: "§4"
budget-hrs: 18
parent: [[interview-prep-master-plan-2026]]
---

# Track E — ML / LLM Fundamentals  (master plan §4)

**Charter:** close the infra→ML gap. Bar per item: (a) explain to a peer in 2 min, (b) whiteboard the shape, (c) for ⭐ items, implement a toy version in NumPy. This is your highest-ROI investment and unlocks Tracks D + E rounds.

**Who leans on it:** frontier labs + every "AI Engineer" title (esp. Fireworks, Together, NVIDIA, OpenAI, Anthropic, Cohere).

## To elaborate here (one note per block)
- [ ] `block-1-transformers.md` ⭐ — attention, MHA, positional enc (RoPE/ALiBi), the block, GQA vs MHA vs MQA + KV-cache math, MoE
- [ ] `block-2-training.md` — pretraining objective, cross-entropy/perplexity, full vs LoRA/QLoRA, RLHF (SFT→RM→PPO/DPO), optimizers, FSDP/ZeRO, parallelism (data/tensor/pipeline/sequence)
- [ ] `block-3-inference.md` ⭐ — KV cache, continuous batching, paged attention, quantization, speculative decoding, flash attention, decoding (top-k/p/temp), TTFT vs TPOT
- [ ] `block-4-rag-agents.md` — embeddings/ANN (HNSW/IVF), hybrid search, re-ranking, hallucination, agent loop (ReAct), eval/LLM-as-judge
- [ ] `block-5-safety.md` — alignment, red-teaming, Anthropic RSP / OpenAI Preparedness (for labs)
- [ ] `numpy-implementations/` — attention, softmax, layernorm, top-k/p sampling, cross-entropy

## Resources
Karpathy Zero-to-Hero · Illustrated Transformer · Lilian Weng's blog · HF LLM course · vLLM PagedAttention paper.
