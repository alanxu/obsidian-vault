---
title: Design an A/B Testing / Experimentation Platform (ML/LLM)
slug: ab-experimentation-platform
area: 5 — Evaluation & Quality
companies: [general big-tech, Lyft, Robinhood]
difficulty: ★★★☆☆
formats: [Live system design]
related: ["[[18-llm-eval-harness]]", "[[24-recommendation-ranking-system]]", "[[D0-areas-map]]"]
---

# Design an A/B Testing / Experimentation Platform

> The online half of eval: safely roll out and measure ML/model/prompt changes on real traffic with statistical rigor. The ground truth that offline eval approximates.

## Problem
"Design a platform to run experiments (model versions, prompts, ranking changes) with assignment, metrics, and significance." ML twist: outputs are non-deterministic; metrics are noisy; novelty effects.

## Clarify first
- What's experimented (model, prompt, ranker, feature)? Primary metric + guardrail metrics?
- Traffic volume (power)? Unit of randomization (user/session/request)? Latency to read out?

## Architecture
**Assignment service** (consistent hash user → variant, sticky) → **serving reads variant** → **event logging** (exposure + outcomes) → **metrics pipeline** (aggregate, dedup) → **stats engine** (significance, CIs, guardrails) → dashboard + auto-stop. Feature-flag/config layer.

## Deep-dive — valid experiments
- **Randomization unit + stickiness:** user-level (consistent experience) vs request-level (more power, but interference). Hash for deterministic, sticky assignment.
- **Statistics:** report effect size + CI + p-value (not single runs); pre-register the primary metric; **guardrail metrics** (latency, cost, safety) that auto-stop on regression; correct for **multiple comparisons / peeking** (sequential tests).
- **ML-specific:** novelty/primacy effects, network interference (recsys), long-term vs short-term metrics, **canary** before full A/B.
- **Online ↔ offline:** tie back to [[18-llm-eval-harness]] — offline gate first, then online A/B.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| User vs request randomization | consistency vs power/interference |
| Short vs long metric window | speed vs true effect (novelty) |
| Peeking/sequential vs fixed-horizon | speed vs false positives |
| Auto-stop strictness | safety vs prematurely killing winners |

## Numbers
Power depends on traffic × effect size — small effects need lots of traffic/time. Guardrail auto-stop in minutes for safety/latency regressions. Don't peek without sequential correction.

## Failure modes
Peeking → false positives · interference between variants · novelty effect mistaken for lift · sample-ratio mismatch (broken assignment) · optimizing a proxy metric that hurts the business.

## Top follow-ups
- "Significance with noisy ML output?" → effect size + CI + sequential tests + guardrails; pre-register metric.
- "Recsys interference?" → cluster/geo randomization; watch network effects.
- "Roll out a new model safely?" → offline gate → canary → A/B with guardrail auto-stop → full.

## Related
[[18-llm-eval-harness]] (offline half) · [[24-recommendation-ranking-system]] · [[D0-areas-map]] Area 5.
