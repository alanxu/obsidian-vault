---
tags: [job-hunt, interview-prep, question-bank, llm-fundamentals, concept-qa, index]
title: "LLM / ML Fundamentals — Concept Q&A Bank"
scope: "Rapid-fire 'explain X' concept questions for AI-eng interviews. One enriched card per concept. Design prompts live in llm-system-design/; behavioral in Track F."
source_seed: "Anthropic 100-question bank (Notion inbox, ChatGPT share, 2026-06-19)"
related: ["[[llm-system-design/README]]", "[[track-D-ml-llm-system-design/D0-areas-map]]", "[[track-E-ml-llm-fundamentals/README]]", "[[plans/anthropic-oa-vs-onsite]]"]
created: 2026-06-19
status: building (Part 1 done; Parts 2–6 in progress)
---

# LLM / ML Fundamentals — Concept Q&A Bank

> **Location note:** this is a **sub-bank inside the LLM/ML system-design area** ([[llm-system-design/README]]) — *not* a separate interview format. Fundamentals get probed **within** the ML/LLM round, so they nest here rather than as a top-level question-bank area.

**One enriched card per concept** (prompt → answer → tradeoffs → follow-ups → pitfalls → tips). These are the *rapid-fire "explain it"* questions; the full **design prompts** ("Design X") live one level up in [[llm-system-design/README]], and **behavioral** in [[track-F-behavioral-staff-values/README]]. Seeded from a 100-question Anthropic-style bank ([[plans/anthropic-oa-vs-onsite]] has the OA-vs-onsite intel from the same source).

## Routing of the source 100 questions
Concept Qs → enriched cards **here**. Design Qs → existing **llm-system-design** cards. Behavioral → **Track F**.

### Part 1 — LLM Fundamentals (concept cards here)
| # | Card | Source Qs |
|---|---|---|
| 01 | [[01-self-attention-vs-rnn]] | self-attention vs RNN; attention complexity |
| 02 | [[02-context-window-limits]] | why context can't grow unboundedly |
| 03 | [[03-kv-cache]] | what is KV cache; why it speeds inference |
| 04 | [[04-pretraining-vs-finetuning]] | pretraining vs fine-tuning |
| 05 | [[05-sft-vs-rlhf]] | SFT vs RLHF; why RLHF improves UX |
| 06 | [[06-dpo]] | what is DPO |
| 07 | [[07-hallucination]] | why models hallucinate |

### Part 2 — RAG (concept cards here; full design → [[llm-system-design/01-rag-with-citations]])
| # | Card | Source Qs |
|---|---|---|
| 08 | [[08-embeddings-and-similarity]] | what is an embedding; why cosine similarity |
| 09 | [[09-vector-retrieval-failure]] | why vector retrieval fails |
| 10 | [[10-chunking]] | chunk size; chunk overlap |
| 11 | [[11-topk-recall-precision]] | top-K choice; recall vs precision |
| 12 | [[12-reranking]] | why rerankers work |
| 13 | [[13-hybrid-search]] | BM25 + vector; hybrid pros/cons |
| — | Production RAG (Q21–25: million docs, incremental index, ACL, real-time, latency) | → [[llm-system-design/01-rag-with-citations]], [[llm-system-design/02-enterprise-search-acl]], [[llm-system-design/23-embedding-pipeline-incremental]] |
| — | RAG eval (Q26–30) | → [[llm-system-design/18-llm-eval-harness]] + card [[14-rag-evaluation]] (concept) |

### Part 3 — Agents (concept cards here; full design → [[llm-system-design/09-agent-platform]])
| # | Card | Source Qs |
|---|---|---|
| 15 | [[15-agent-vs-chatbot]] | agent vs chatbot; why tool calling |
| 16 | [[16-agent-loops-and-control]] | why agents loop; bounding behavior; planning value |
| 17 | [[17-react]] | ReAct workflow; thought/action/observation; flaws |
| 18 | [[18-agent-memory]] | short/long-term memory; implement; retrieval |
| 19 | [[19-multi-agent]] | why multi-agent; supervisor; conflict; collaboration; drawbacks |

### Part 4 — AI System Design (→ existing design cards, no duplication)
Design Claude API → [[llm-system-design/06-llm-inference-serving-platform]] (+ streaming/rate-limit/prompt-cache/cost = its deep-dives). Design ChatGPT → 06 + [[llm-system-design/33-conversation-memory-manager|memory]] + [[llm-system-design/30-llm-gateway-router|tool use/gateway]]. Design RAG Platform → [[llm-system-design/01-rag-with-citations]] + [[llm-system-design/23-embedding-pipeline-incremental]]. Design Agent Platform → [[llm-system-design/09-agent-platform]] (registry/tools/workflow/state/eval = its deep-dives).

### Part 5 — Production AI / LLMOps (→ existing cards + 1 concept card)
Monitoring/tracing/cost/rollback/SLA/A-B/canary/prompt-versioning/timeouts/3p-failure → [[llm-system-design/31-llm-observability-cost]] + [[llm-system-design/30-llm-gateway-router]] + [[llm-system-design/19-ab-experimentation-platform]]. Concept card: [[20-prompt-regression-and-drift]].

### Part 6 — Behavioral & AI Safety
Behavioral (why Anthropic, Claude vs others, Responsible AI, safety-vs-innovation, refuse, future jobs) → **[[track-F-behavioral-staff-values/README]]** (story/values bank). Safety *design* (prompt-injection detect/defend, tool-use risk, agent DB-write, safety eval) → [[llm-system-design/29-guardrails-prompt-injection]]. Safety *concept* card: [[21-prompt-injection-concepts]].

## Priority (per the source, RAG/AI-eng background)
RAG ★★★★★ · AI System Design ★★★★★ · Production AI ★★★★★ · Agents ★★★★☆ · LLM Basics ★★★★☆ · Safety ★★★★☆.

## How to use
Drill as 2-min spoken answers. Each card's **Answer** is the spine; the **Follow-ups** are the interviewer's rapid-fire extensions. Pair with [[D0-areas-map]] for the design depth.

*Built 2026-06-19 re-digesting the 100-Q bank per [[inbox-digest-playbook]]. Part 1 cards done; Parts 2–6 in progress.*
