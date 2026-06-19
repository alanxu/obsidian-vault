---
title: Design an LLM Eval Harness / Capability-Regression Monitoring
slug: llm-eval-harness
area: 5 — Evaluation & Quality
companies: [Anthropic, OpenAI, Cohere, all AI-eng]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[20-llm-as-judge-system]]", "[[19-ab-experimentation-platform]]", "[[D0-areas-map]]"]
---

# Design an LLM Eval Harness / Capability-Regression Monitoring

> The area that makes every other change *safe*. **The thesis:** *you can't tell if a change helped by reading the diff — output is non-deterministic and quality is statistical. Eval is your compiler.* "How do you know it works?" is the question behind every ML prompt — have a crisp **offline + online** answer.

## Problem
"Design an eval harness that tracks capability degradation across fine-tunes / model swaps." Variant: "how do you measure success?" for any ML system.

## Clarify first
- What's the task + quality bar? Ground truth available, or must we judge?
- What changes ship (prompts, models, embedders, chunkers)? Stakes (gate strictness)?

## Architecture
**Golden set** (versioned) → **offline eval** (metrics + LLM-judge) → **regression gate** (must pass to ship) → **canary → A/B online** → **prod monitoring** (sampled + judged) → drift alerts. Eval-as-a-service callable by every team/CI.

## Deep-dive — the two layers + the gate
- **Golden/eval set:** curated (input → expected/labeled), seeded from real traffic + synthetic, human-verified, **contamination-controlled**, grown over time. The asset everything depends on.
- **Offline metrics** (task-dependent): retrieval (Recall@k, MRR, nDCG), classification (P/R/F1, PR-AUC), generation (faithfulness, answer-relevance, RAGAS), exact-match/code-exec for verifiable.
- **LLM-as-judge** ([[20-llm-as-judge-system]]) for no-ground-truth tasks — **must be calibrated against a human-audited sample** (judges have length/position/self-preference bias and drift).
- **Regression gate:** automated eval that must pass before any change ships → turns "quality regresses silently" into "build fails."
- **Drift/monitoring:** input-distribution shift + quality on a judged production sample + capability regression after a model/provider update.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Human vs LLM-judge vs metric | accuracy vs scale vs cheapness — tier them |
| Offline vs online weight | fast/safe vs real-but-slow |
| Eval-set size/freshness | power vs labeling cost |
| Gate strictness | ship velocity vs regression risk |

## Numbers
Golden set 200–1000 cases to start. Calibrate the judge to humans (≥~80% agreement before trusting). Faithfulness = hallucination KPI inverted. Report distributions/p-values on A/Bs.

## Failure modes
Judge bias treated as truth · eval-set leak into training (contamination) · offline-online gap · metric gaming · no gate → silent regression ships · stale eval set.

## Top follow-ups
- "How do you know it works?" → offline golden-set metrics + online A/B + judged prod sample.
- "Retrieval or generation broken?" → decompose: Recall@k isolates retrieval, faithfulness isolates generation.
- "Trust LLM-judge?" → only after calibrating to humans; monitor judge drift.
- "Ship a new model version?" → regression suite + canary + A/B before full rollout.

## Related
[[20-llm-as-judge-system]] · [[19-ab-experimentation-platform]] · [[D0-areas-map]] Area 5.
