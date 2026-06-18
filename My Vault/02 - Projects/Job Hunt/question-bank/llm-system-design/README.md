---
tags: [job-hunt, interview-prep, system-design, ml, llm, ai-systems]
track: "LLM / ML system design (Track D)"
plan-section: "§4"
parent: [[interview-prep-master-plan-2026]]
related: ["[[track-D-ml-llm-system-design/README]]", "[[track-D-ml-llm-system-design/D0-areas-map]]", "[[track-D-ml-llm-system-design/D1-rag-with-citations]]"]
created: 2026-06-18
---

# LLM / ML System Design

**Charter:** applied-AI / LLM-flavored system design — the high-leverage track for frontier-lab applied-AI / FDE / member-of-technical-staff roles. Architecture choices under uncertainty (retrieval vs long context, fine-tuning vs prompting, sync vs streaming), eval methodology, cost + latency + reliability tradeoffs.

**Who leans on it:** Anthropic (Applied AI / FDE), OpenAI, Anysphere, Cohere, Glean, Harvey, Mistral.

## Structure

The LLM/ML system-design space decomposes into ~6 areas. The previous folder already has working notes for two:

- **D0 — Areas map.** Index of all LLM-system-design areas with cross-company framing. See `track-D-ml-llm-system-design/D0-areas-map.md` (working notes live there for now; copy or symlink when convenient).
- **D1 — RAG with citations.** Worked system-design answer for retrieval-augmented generation. See `track-D-ml-llm-system-design/D1-rag-with-citations.md`.

## To elaborate here (one note per area)
- [ ] `D0-areas-map.md` — promote from `track-D-ml-llm-system-design/`
- [ ] `D1-rag-with-citations.md` — promote from `track-D-ml-llm-system-design/`
- [ ] `D2-fine-tuning-vs-prompting.md` — when to fine-tune, when to prompt, when to RAG
- [ ] `D3-agent-platform.md` — multi-agent platform (planning, memory, tool registry, eval, observability, cost)
- [ ] `D4-llm-infra.md` — token economics, batching, KV cache, streaming, serverless inference
- [ ] `D5-eval-framework.md` — offline + online eval, A/B harness, drift detection, golden sets
- [ ] `D6-safety-policy.md` — content policy, jailbreak resistance, red-team harness, refusal design
- [ ] `D7-real-time-ml.md` — streaming features, online learning, ranking at low latency

## Convention
Pull existing notes over from `track-D-ml-llm-system-design/` rather than rewriting — the structure there is good.

> Legacy alias: this folder replaces `track-D-ml-llm-system-design/` (same scope; cleaner naming).