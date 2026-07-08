---
title: RAG Evaluation (offline + online)
slug: rag-evaluation
area: RAG Concepts
source_q: "Anthropic 100-Q #26–30"
companies: [Cohere, Anthropic, OpenAI, Perplexity]
difficulty: ★★★★☆
related: ["[[07-hallucination]]", "[[11-topk-recall-precision]]", "[[llm-system-design/18-llm-eval-harness]]"]
---

# RAG Evaluation

## Prompt
How do you evaluate a RAG system? How do you detect retrieval failure vs hallucination? Offline vs online eval?

## Answer
**Decompose** — RAG has two layers, eval each:
- **Retrieval:** **Recall@k / Hit@k** (is the gold chunk retrieved?) + **MRR/nDCG** (ranked high?). Recall@k is the single most important RAG metric.
- **Generation:** **faithfulness/groundedness** (is each claim entailed by the cited source?), **answer relevance**, and **context precision/recall** (RAGAS-style). Faithfulness = your hallucination KPI, inverted.

**Detecting which layer broke:** Recall@k isolates **retrieval** (gold chunk absent → fix chunking/retrieval); faithfulness isolates **generation** (chunk present but answer unsupported → fix prompting/grounding). This decomposition is the staff move.

**Build an eval set:** 200–1000 (query → relevant chunk IDs / gold answer) cases — seed from real traffic + LLM-generated Q/A over your corpus, then **human-verify**; keep it **contamination-controlled** and growing.

**Offline vs online:**
- **Offline** = golden-set metrics + LLM-as-judge; fast, safe, gates every change (new embedder/chunker/prompt/model).
- **Online** = A/B + implicit signals (click/dwell on citations, thumbs, regenerate rate, task success). The ground truth offline approximates.

## Tradeoffs
| | Offline | Online |
|---|---|---|
| Speed/safety | fast, safe | slow, real-traffic risk |
| Truth | proxy | ground truth |
Use offline as a **regression gate**, online as the final arbiter.

## Follow-ups
- *"Trust LLM-as-judge?"* → only after calibrating vs a human-audited sample; control length/position bias (→ [[llm-system-design/20-llm-as-judge-system]]).
- *"Detect hallucination automatically?"* → claim-vs-source **entailment** (NLI/judge); flag uncited claims.
- *"Ship a new embedder?"* → run Recall@k offline + online A/B before rollout.
- *"Real regression or noise on a 100-sample eval?"* → (reported Cohere probe) — paired comparison on the *same* queries + significance test (bootstrap/McNemar); 100 samples detect only large deltas → grow the set or accept wide error bars; never ship/block on a 2% wiggle.
- *"Eval multi-turn RAG?"* → per-turn faithfulness plus conversation-level task success; retrieval queries depend on rewritten context, so eval the query-rewriter as its own stage (three-layer decomposition).

## Pitfalls
- A single end-to-end score that hides whether retrieval or generation is at fault.
- Eval set leaking into training (contamination) → inflated numbers.
- Trusting an uncalibrated judge.

## Tips
Lead with **"decompose: Recall@k for retrieval, faithfulness for generation"** and **"offline gate + online A/B."** That two-layer answer is exactly what "how do you know it works?" wants.
