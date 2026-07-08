---
title: Design an LLM-as-Judge / Automated Eval System
slug: llm-as-judge-system
area: 5 — Evaluation & Quality
companies: [general AI-eng, Anthropic, OpenAI]
difficulty: ★★★☆☆
formats: [Live system design]
related: ["[[18-llm-eval-harness]]", "[[D0-areas-map]]"]
---

# Design an LLM-as-Judge / Automated Eval System

> Scale eval where there's no ground truth: use a strong model to score outputs on a rubric. **The catch (and the staff signal): the judge is biased and drifts — it must be calibrated against humans.**

## Problem
"Design a system to automatically evaluate LLM outputs at scale (factuality, relevance, coherence) without ground-truth labels." Used inside [[18-llm-eval-harness]] and prod monitoring.

## Clarify first
- What dimensions (faithfulness, helpfulness, safety, format)? Pairwise vs pointwise scoring?
- Volume? Cost budget for judge calls? How much human labeling is available to calibrate?

## Architecture
Outputs → **judge prompt** (rubric, criteria, few-shot anchors) → judge model scores (pointwise rubric or pairwise A/B) → aggregate → dashboard. **Calibration loop:** sample → human-label → measure judge-human agreement → adjust rubric/model.

## Deep-dive — making the judge trustworthy
- **Bias control:** judges favor **longer** answers, **first/last position** (pairwise), and **their own** outputs → randomize order, control for length, use a different family as judge, prefer pairwise + swap.
- **Calibration:** measure agreement with a human-audited sample; **don't trust the judge until agreement is high** (~≥80%); re-calibrate as the judge model changes.
- **Rubric design:** specific criteria + few-shot anchors beat "rate 1–10"; chain-of-thought before the score.
- **Cost:** judge runs on every eval → use a cheaper judge for bulk, frontier judge for spot-checks; cache.
- **Frameworks:** G-Eval, RAGAS (for RAG faithfulness/context metrics).

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Pointwise vs pairwise | absolute score vs more-reliable comparison |
| Frontier vs cheap judge | quality vs cost-per-eval |
| Judge family vs self | bias reduction vs convenience |
| Rubric detail | reliability vs prompt cost |

## Numbers
Calibrate to humans (≥~80% agreement) before trusting. Pairwise + order-swap reduces position bias. Length bias is real — control for it.

## Failure modes
Bias (length/position/self-preference) treated as truth · judge drift on model update · rubric too vague → noisy scores · gaming (optimize what the judge likes) · cost blowup.

## Top follow-ups
- "Trust the judge?" → calibrate vs human sample; monitor drift; control biases.
- "Reduce bias?" → pairwise + order-swap, length control, different judge family, CoT-then-score.
- "Cost?" → cheap judge for bulk + frontier for spot-check + cache.
- "When does LLM-judge fundamentally break?" → (reported Cohere probe) when judging exceeds the judge's own competence: deep domain correctness (medicine, law, niche code), subtle factuality the judge can't verify, and anything adversarially optimized *against* the judge — for those, tier up to humans/experts or programmatic verifiers; a judge can check *groundedness to a source* far more reliably than *truth*.
- "Jury over judge?" → ensemble of 3+ diverse smaller judges + majority/mean beats one frontier judge on bias and cost (Cohere-style result); disagreement rate itself is a useful uncertainty signal → route high-disagreement cases to humans.
- "Judge score inflation over time?" → outputs optimize toward the judge (direct or indirect Goodhart) → freeze a judge version per experiment, track judge-human agreement quarterly, rotate rubrics/anchors when agreement decays.

## Related
[[18-llm-eval-harness]] (the harness that uses it) · [[D0-areas-map]] Area 5.
