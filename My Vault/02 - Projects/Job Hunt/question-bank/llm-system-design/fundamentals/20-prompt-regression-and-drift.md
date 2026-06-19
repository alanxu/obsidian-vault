---
title: Prompt Regression & Model Drift
slug: prompt-regression-and-drift
area: Production AI Concepts
source_q: "Anthropic 100-Q #72, #73, #74"
companies: [Anthropic, OpenAI, applied-AI everywhere]
difficulty: ★★★★☆
related: ["[[14-rag-evaluation]]", "[[llm-system-design/31-llm-observability-cost]]", "[[llm-system-design/18-llm-eval-harness]]"]
---

# Prompt Regression & Model Drift

## Prompt
How do you detect prompt regression? How do you detect model degradation/drift? How do you track hallucination in production?

## Answer
The core problem: **quality regresses silently** — no error, no exception, just worse outputs — because output is non-deterministic and "correct" is statistical. So you need eval and monitoring as a *system*, not a one-off.

- **Prompt regression** (you changed a prompt): gate every prompt change behind an **offline regression suite** on a golden set; **version** prompts; ship via **canary → A/B**; compare faithfulness/answer-relevance/task-success before vs after. A regression = build fails / rollback.
- **Model drift / degradation** (the *world* or the *provider* changed): monitor **input-distribution shift** (are queries changing?) and **output quality** on a **sampled-and-judged** production stream; watch for **capability regression after a provider model update** (a silent model swap upstream can tank you). Champion/challenger comparisons.
- **Hallucination tracking:** sample outputs → **claim-vs-source entailment** (NLI/LLM-judge) → faithfulness dashboard + refusal rate + user "wrong"/regenerate signals. Faithfulness is the hallucination KPI, inverted.

**Foundation:** **tracing** — log prompt, response, **model & prompt version**, retrieved chunk IDs, tokens/cost — so any bad output is **reproducible** (→ [[llm-system-design/31-llm-observability-cost]]).

## Tradeoffs
| Lever | Gains | Costs |
|---|---|---|
| Full eval gate | catches regressions | slows shipping |
| Sample + judge in prod | scalable quality signal | judge cost/bias |
| Versioning + canary | safe rollout, fast rollback | infra overhead |

## Follow-ups
- *"How do you *know* a new model version is safe to ship?"* → regression suite + canary + online A/B before full rollout.
- *"Green dashboards but users unhappy?"* → latency/error SLOs miss quality → add **quality-in-prod** monitoring (sample + judge).
- *"Roll back?"* → versioned prompts/models/indexes + one-click rollback (minutes).

## Pitfalls
- Monitoring only latency/errors (silent quality regression slips through).
- Shipping a prompt change with no version/gate/rollback.
- Trusting an uncalibrated LLM-judge for the quality signal.

## Tips
Anchor on **"quality regresses silently → eval gates + drift monitoring + versioned rollback as architecture."** Separate the three causes (prompt change, model/provider change, world change) and give each its detector.
