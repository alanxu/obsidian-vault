---
tags: [job-hunt, interview-prep, track, ml-system-design, llm]
track: "Track D — ML / LLM system design"
plan-section: "§6"
budget-hrs: 18
parent: [[interview-prep-master-plan-2026]]
---

# Track D — ML / LLM System Design  (master plan §6)

**Charter:** where infra-strong candidates win AI roles — you bring distributed-systems rigor most ML candidates lack. Same frame as Track C + an ML layer (data, model, eval, online/offline). Write full answers for D1–D5 (cover ~90% of cases); rehearse D6–D8 verbally.

**Who leans on it:** every AI role — Anthropic, OpenAI, NVIDIA, Cohere, Harvey, Robinhood, Fireworks, Together, Glean, Perplexity.

## Foundation (read first)
- [[D0-areas-map]] — **the structural map underneath D1–D8.** Decomposes ML/LLM system design into the **8 competency areas** (retrieval · inference/serving · agents · training · eval · data/features · safety · observability/cost), each at staff depth: mental model, key tradeoffs, numbers, failure modes, senior-vs-staff, and which prompt/company it maps to. Includes the **universal driving framework** (works for any D prompt), the **cross-cutting staff checklist**, the **coverage matrix**, and a study sequence. *Learn the areas → derive any prompt.*

## Worked solutions
- [x] [[D1-rag-with-citations]] — **DONE.** RAG with citations (chunking, dense vs sparse, hybrid+RRF, re-rank, context assembly, hallucination, citation verification)
- [ ] `D2-inference-serving-platform.md` — continuous batching, KV cache, paged attention, speculative decoding, p99, multi-tenant quotas *(NVIDIA, OpenAI, Anthropic, Anysphere, Fireworks, Together)*
- [ ] `D3-agentic-platform-loop.md` — planning, tool calling, memory, retries, sandboxing, eval, cost *(Robinhood, Anysphere, Harvey, Anthropic, Cognition)*
- [ ] `D4-distributed-training-70b.md` — data/tensor/pipeline parallelism, checkpointing, fault tolerance *(OpenAI, NVIDIA, Cohere, Together)*
- [ ] `D5-llm-eval-harness.md` — offline+online eval, LLM-as-judge, regression/drift after fine-tunes *(Anthropic, OpenAI)*
- [ ] `D6-fraud-detection-llm.md` — feature pipeline, streaming inference, precision/recall *(Robinhood, Wealthsimple)*
- [ ] `D7-feature-store-realtime-serving.md` — online/offline parity, freshness, point-in-time correctness
- [ ] `D8-embedding-pipeline-or-av-sim.md` — 100M+ docs incremental *(Cohere, Glean)* OR AV simulation *(Waabi, Waymo)*

## One-paragraph answers to also have ready
Code-completion serving sub-100ms (Anysphere) · LLM gateway/router w/ caching+fallback+cost · content moderation at 10B msgs/day (Anthropic).

**Next up:** D2 + D3 (highest frequency).
