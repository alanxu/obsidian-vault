---
title: Design a Data Labeling / Annotation Pipeline (Scale-style)
slug: data-labeling-pipeline
area: 6 — Data, Features, Embeddings
companies: [Scale, data/eval cos, Anthropic/OpenAI (RLHF data)]
difficulty: ★★★☆☆
formats: [Live system design]
related: ["[[14-rlhf-pipeline]]", "[[18-llm-eval-harness]]", "[[D0-areas-map]]"]
---

# Design a Data Labeling / Annotation Pipeline

> The Scale prompt: label 10M items/day with quality control. Also the **RLHF preference-data** pipeline (Anthropic/OpenAI). **The core problem is quality at scale** — inter-annotator agreement, consensus, and catching bad labelers.

## Problem
"Design a data labeling pipeline that processes 10M images/day with quality control, inter-annotator agreement, and escalation." Variant: RLHF preference collection (rank A vs B).

## Clarify first
- Task type (classification, bbox, preference ranking)? Quality bar? Throughput (items/day)?
- Human + model-assisted? Ambiguous ground truth? Cost budget?

## Architecture
Tasks → **task queue** (priority, SLA) → **annotators** (multiple per item) → **consensus/aggregation** → **QC** (gold tasks, IAA, model-assist pre-labels) → **escalation** (disagreement → expert/review) → labeled dataset → feeds training/eval.

## Deep-dive — quality control at scale
- **Redundancy + consensus:** N annotators per item; aggregate (majority / Dawid-Skene); confidence from agreement.
- **Inter-annotator agreement (IAA):** measure per-annotator agreement (Cohen's/Fleiss' kappa); **detect bad/adversarial labelers** (low agreement with gold/consensus) → down-weight or remove.
- **Gold/honeypot tasks:** seed known-answer tasks to score annotators continuously.
- **Model-assist:** pre-label with a model, humans correct (active learning: route uncertain items to humans) → big throughput win.
- **Escalation:** high-disagreement or ambiguous items → expert review queue.
- **Ambiguous truth:** some tasks have no single answer → capture distribution, not a forced label.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| #annotators per item | quality/confidence vs cost |
| Model pre-label | throughput vs automation bias |
| Gold-task frequency | QC signal vs wasted effort |
| Consensus method | simplicity (majority) vs accuracy (Dawid-Skene) |

## Numbers
10M/day → model-assist + active learning (humans only on uncertain). IAA/kappa to detect bad labelers. Gold tasks for continuous scoring.

## Failure modes
Bad/adversarial labelers · automation bias (rubber-stamping model pre-labels) · ambiguous-truth forced labels · throughput bottleneck · label drift over time · biased label distribution.

## Top follow-ups
- "Quality at scale?" → redundancy + consensus + gold tasks + IAA to catch bad labelers.
- "10M/day?" → model pre-label + active learning (humans on uncertain only).
- "Ambiguous ground truth?" → capture distribution; escalate; measure agreement not just correctness.
- "RLHF preference data?" → pairwise ranking + IAA + prompt sampling (see [[14-rlhf-pipeline]]).
- "LLM as annotator (2026 reality)?" → LLMs pre-label or fully label the easy tier; humans move up-stack to hard cases + auditing the LLM's labels — QC machinery (gold tasks, agreement) now applies to the *model* annotator too, including its systematic biases (a bad human is random, a bad model is *correlated* across millions of labels — the scarier failure).
- "Annotator disagreement is signal, not noise?" → for subjective tasks (toxicity, preference), high-IAA-by-construction means you've flattened real distributional truth → store per-annotator labels + demographics, train on soft labels where the product needs it.
- "Expert domains (medical, legal)?" → scarce/expensive experts → tier: model + generalists filter and draft, experts adjudicate only contested/critical items; expert-time-per-label is the binding constraint to optimize.

## Related
[[14-rlhf-pipeline]] · [[18-llm-eval-harness]] (golden sets) · [[D0-areas-map]] Area 6.
