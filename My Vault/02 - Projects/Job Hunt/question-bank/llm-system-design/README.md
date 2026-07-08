---
tags: [job-hunt, interview-prep, question-bank, llm-system-design, ml-system-design, index]
title: "LLM / ML System Design — Question Bank"
scope: "Concrete design prompts for AI/ML system-design rounds (master-plan Track D §6). One file per question. Framework lives in D0; this bank is the worked prompt set."
location: "Under `/question-bank/llm-system-design/`."
related: ["[[track-D-ml-llm-system-design/D0-areas-map]]", "[[track-D-ml-llm-system-design/D1-rag-with-citations]]", "[[interview-prep-master-plan-2026]]", "[[ai-ipo-interview-guide]]"]
count: 38
created: 2026-06-18
updated: 2026-07-09 (added 38 multimodal RAG + fundamentals 25). Prior: 2026-07-08 audit fill 32–37; see [[question-bank/README]] §Audit & evidence
---

# LLM / ML System Design — Question Bank

**One file per design prompt.** Each card: the problem + variants, the **clarifying questions** that matter, an **architecture** (the 2–3 planes), the **deep-dive** on the high-leverage component, **tradeoffs**, **eval/metrics**, scale/cost/latency, **failure modes**, **top follow-ups**, and **companies**.

> **Read the framework first:** [[D0-areas-map]] defines the **8 competency areas** and the universal staff talk-track (clarify → state the metric → draw the planes → deep-dive → eval → scale/cost → failure modes). Every card here is an instantiation of one area; don't re-derive the framework per card — internalize D0, then drill cards.
>
> **The one-line thesis (from D0):** *classic system design asks "will it work?"; ML/LLM design asks "how good is it, how do you know, and how fast does it silently get worse?" — so **eval, cost, and the offline/online split are first-class**.*

## Format
Mostly **live system design** (45–60 min, whiteboard/CoderPad-doc) and **take-home design write-ups**. A few (training, safety) also appear as **ML-depth/research rounds**. Difficulty ★1–5 = staff-readiness effort.

## Fundamentals / Concept Q&A (sub-bank)
The ML/LLM round also probes **fundamentals** ("explain attention / KV cache / RLHF / chunking / the agent loop"). Fundamentals are **not a separate interview format** — they're tested *inside this round* — so they live as a concept-Q&A **sub-bank in this area**: **[[fundamentals/README|/llm-system-design/fundamentals]]** (25 enriched cards: LLM basics, RAG concepts, agent concepts, production & safety concepts). Drill those as rapid-fire 2-min answers; the **design prompts** below are the whiteboard set.

---

## Area 1 — Retrieval & Knowledge Systems
*Quality ceiling = retrieval. Citations/grounding, ACL, hybrid search, re-ranking.* Framework: [[D0-areas-map]] Area 1.

| # | Question | Companies | ★ |
|---|---|---|---|
| 01 | [[01-rag-with-citations]] (full worked solution → [[D1-rag-with-citations]]) | Perplexity, Cohere, Harvey, Glean, Anthropic, OpenAI | ★★★★☆ |
| 02 | [[02-enterprise-search-acl]] | Glean | ★★★★☆ |
| 03 | [[03-web-answer-engine]] | Perplexity | ★★★★☆ |
| 04 | [[04-legal-document-qa]] | Harvey | ★★★★☆ |
| 05 | [[05-semantic-hybrid-search]] | general, Cohere | ★★★☆☆ |
| 38 | [[38-multimodal-document-rag]] *(2026-07 fill)* | Harvey (verified); Glean/Cohere inferred — see card `evidence` | ★★★★☆ |

## Area 2 — Inference & Serving
*Prefill compute-bound, decode memory-bound. KV cache, batching, p99, cost.* Framework: [[D0-areas-map]] Area 2.

| # | Question | Companies | ★ |
|---|---|---|---|
| 06 | [[06-llm-inference-serving-platform]] | NVIDIA, OpenAI, Anthropic, Fireworks, Together | ★★★★★ |
| 07 | [[07-code-completion-serving-sub100ms]] | Anysphere | ★★★★☆ |
| 08 | [[08-multi-model-inference-platform]] | Fireworks, Together, Modal | ★★★★☆ |

## Area 3 — Agentic Systems
*Reliability of a stochastic loop. Tools, memory, orchestration, sandboxing, eval.* Framework: [[D0-areas-map]] Area 3.

| # | Question | Companies | ★ |
|---|---|---|---|
| 09 | [[09-agent-platform]] | Robinhood, Anysphere, Harvey, Anthropic | ★★★★★ |
| 10 | [[10-autonomous-coding-agent]] | Anysphere, Cognition | ★★★★☆ |
| 11 | [[11-multi-agent-system]] | general, agent-platform cos | ★★★★☆ |
| 12 | [[12-customer-support-agent]] | Robinhood, Sierra, Decagon | ★★★☆☆ |
| 32 | [[32-llm-memory-system]] *(2026-07 fill)* | OpenAI, Anthropic, Anysphere, Robinhood | ★★★★☆ |
| 33 | [[33-deep-research-agent]] *(2026-07 fill)* | OpenAI, Anthropic, Perplexity, Cohere | ★★★★☆ |
| 34 | [[34-realtime-voice-agent]] *(2026-07 fill)* | OpenAI, Sierra/Decagon, voice-AI | ★★★★☆ |
| 37 | [[37-mcp-tool-platform]] *(2026-07 fill)* | Anthropic, OpenAI, Anysphere, Robinhood | ★★★★☆ |

## Area 4 — Training & Fine-tuning Infrastructure
*Your infra flex. Parallelism by bottleneck + fault-tolerant checkpointing.* Framework: [[D0-areas-map]] Area 4.

| # | Question | Companies | ★ |
|---|---|---|---|
| 13 | [[13-distributed-training-70b]] | OpenAI, NVIDIA, Cohere, Together | ★★★★★ |
| 14 | [[14-rlhf-pipeline]] | Anthropic, OpenAI, Cohere | ★★★★☆ |
| 15 | [[15-multi-tenant-finetuning-service]] | Together, Cohere | ★★★★☆ |
| 16 | [[16-pretraining-data-pipeline]] | OpenAI, Cohere, Together | ★★★★☆ |
| 17 | [[17-multilingual-finetuning]] | Cohere | ★★★☆☆ |

## Area 5 — Evaluation & Quality Systems
*Metric-first; offline + online + regression gate; calibrated LLM-judge.* Framework: [[D0-areas-map]] Area 5.

| # | Question | Companies | ★ |
|---|---|---|---|
| 18 | [[18-llm-eval-harness]] | Anthropic, OpenAI, Cohere, all AI-eng | ★★★★☆ |
| 19 | [[19-ab-experimentation-platform]] | general big-tech | ★★★☆☆ |
| 20 | [[20-llm-as-judge-system]] | general AI-eng | ★★★☆☆ |

## Area 6 — Data, Features, Embeddings (+ classic ML)
*Train/serve parity, point-in-time correctness, incremental embeddings, ranking.* Framework: [[D0-areas-map]] Area 6.

| # | Question | Companies | ★ |
|---|---|---|---|
| 21 | [[21-feature-store-realtime-serving]] | Robinhood, Wealthsimple, Stripe-style | ★★★★☆ |
| 22 | [[22-realtime-fraud-detection]] | Robinhood, Stripe, Wealthsimple | ★★★★☆ |
| 23 | [[23-embedding-pipeline-incremental]] | Cohere, Glean | ★★★☆☆ |
| 24 | [[24-recommendation-ranking-system]] | Lyft, Pinterest, big-tech | ★★★★☆ |
| 25 | [[25-ctr-ad-prediction]] | Google, Meta, big-tech | ★★★★☆ |
| 26 | [[26-data-labeling-pipeline]] | Scale, data/eval cos | ★★★☆☆ |
| 27 | [[27-av-simulation-scenario-generation]] | Waabi, Waymo | ★★★★☆ |
| 36 | [[36-structured-output-extraction]] *(2026-07 fill)* | Harvey, Glean, Cohere, enterprise applied-AI | ★★★★☆ |

## Area 7 — Safety, Guardrails & Governance
*Defense-in-depth; injection has no full fix → limit blast radius.* Framework: [[D0-areas-map]] Area 7.

| # | Question | Companies | ★ |
|---|---|---|---|
| 28 | [[28-content-moderation-at-scale]] | Anthropic, OpenAI | ★★★★☆ |
| 29 | [[29-guardrails-prompt-injection]] | Anthropic, Harvey, Glean | ★★★★☆ |

## Area 8 — Observability, Cost & Reliability (LLMOps)
*Quality + cost as SLOs; gateway = cache + route + fallback; versioned rollback.* Framework: [[D0-areas-map]] Area 8.

| # | Question | Companies | ★ |
|---|---|---|---|
| 30 | [[30-llm-gateway-router]] | applied-AI everywhere | ★★★★☆ |
| 31 | [[31-llm-observability-cost]] | applied-AI everywhere | ★★★☆☆ |
| 35 | [[35-semantic-caching]] *(2026-07 fill)* | applied-AI everywhere | ★★★☆☆ |

---

## How to use
1. **Read [[D0-areas-map]] once** (§1 driving framework + §4 staff signals) — reusable across every card.
2. **Write full worked answers for the area that dominates your targets** (use [[D1-rag-with-citations]] as the depth/format template). Route by §5 of D0: labs → Areas 1,2,3,5,7 · NVIDIA → 2,4 · Robinhood/fintech → 3,6,8 · Cohere → 1,6 · AV (Waabi/Waymo) → 4,6.
3. **Rehearse the rest verbally** — each card's "Top follow-ups" is the rapid-fire set.
4. **Run the cross-cutting checklist** (D0 §3) on every answer: latency, cost, multi-tenancy/ACL, parity, versioning/rollback, eval gate, failure modes, security.

*Built 2026-06-18. Framework = [[D0-areas-map]]; worked RAG = [[D1-rag-with-citations]]; per-company reported prompts = [[ai-ipo-interview-guide]].*
