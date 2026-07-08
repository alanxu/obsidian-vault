---
title: Design an LLM Observability / Cost & Tracing System
slug: llm-observability-cost
area: 8 — Observability, Cost & Reliability
companies: [applied-AI everywhere, Anthropic, OpenAI]
difficulty: ★★★☆☆
formats: [Live system design]
related: ["[[30-llm-gateway-router]]", "[[18-llm-eval-harness]]", "[[D0-areas-map]]"]
---

# Design an LLM Observability / Cost & Tracing System

> **The thesis:** *an LLM system can be up, fast, and confidently wrong while quietly costing 10× — so observability must capture **quality and cost**, not just latency and errors.* Every model/prompt/index is a versioned, rollback-able artifact.

## Problem
"Design observability for an LLM product: tracing, cost attribution, quality monitoring, versioning/rollback." The LLMOps layer under every applied-AI system.

## Clarify first
- Single app or platform (many teams)? Agents (multi-step traces)? PII in prompts (logging policy)?
- Cost-attribution granularity (per tenant/feature)? Quality signals available?

## Architecture
Every request → **trace** (prompt, response, model+prompt version, retrieved chunk IDs, tool calls, latency TTFT/TPOT, **tokens+cost**) → trace store → **dashboards** (latency, cost, quality) + **alerts** (cost spike, quality drop, error rate). **Quality-in-prod:** sample outputs → LLM-judge/human → quality dashboard (ties to [[18-llm-eval-harness]]). Version registry + rollback.

## Deep-dive — what to capture + cost + versioning
- **Tracing (the foundation):** log enough to **reproduce** any answer — prompt, sources, **model & prompt version**, params, tool calls. Non-determinism makes traces the only way to debug. For agents: full trajectory (every thought/tool/observation), replayable.
- **Cost engineering:** tokens dominate → attribute cost **per tenant/feature/model**; alert on spikes (retry storm, agent loop); dashboards for $/request.
- **Quality-in-prod:** green latency/error dashboards can hide silent quality regression → sample + judge a stream; track faithfulness, refusal rate, user feedback.
- **Versioning + rollback:** models, prompts, embeddings, indexes are versioned; ship canary → A/B → rollout with **minute-scale rollback** (quality regresses silently).
- **PII in logs:** redact/scrub; sample full prompt/response if volume/PII require; retention controls. Tools: LangSmith/Langfuse/Arize-style.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Log verbosity | debuggability/audit vs storage cost + PII exposure |
| Full vs sampled traces | completeness vs cost |
| Inline vs async quality eval | freshness vs latency/cost |
| Alert sensitivity | catch regressions vs alert fatigue |

## Numbers
Report p50/**p99**, not averages. Log all metadata; sample full prompt/response by volume/PII. Canary % + rollback time (target minutes) are real design params. Caching/cost dashboards per tenant.

## Failure modes
Silent quality regression with green dashboards · cost blowup undetected (retry/agent loop) · PII sitting in logs · un-versioned prompt change with no rollback · unreproducible bug (insufficient trace).

## Top follow-ups
- "Debug a bad answer?" → pull the trace (prompt+sources+versions), replay, isolate the layer.
- "Catch silent quality drops?" → quality-in-prod: sample + judge a stream; alert on faithfulness/feedback.
- "Control cost?" → per-tenant token/cost attribution + spike alerts + budgets/circuit breakers.
- "Ship a prompt safely?" → version it, canary, A/B with the regression gate, one-click rollback.
- "Agent traces are 100× chat traces — what changes?" → hierarchical spans (task → steps → tool calls) with a trace tree, not a flat log; cost/latency roll up per level; sampling keeps *full* trajectories (a sampled 40% of steps is useless for replay) — sample at task granularity.
- "What alerts page a human at 3am?" → cost-rate spike (agent loop, retry storm), error-rate on a provider, guardrail-block-rate spike (attack or regression), and *sustained* faithfulness drop; quality wobbles wait for morning — alert design = separating incidents from drift.
- "Prompt/config drift across teams?" → central prompt registry with versions + owners + eval-gate status; the anti-pattern is prompts as inline strings in five services — you can't roll back what you can't enumerate.
- "Unit economics dashboard?" → $/resolved-task (not $/request) per feature and tenant, trended across model swaps — the number the CFO and the staff engineer both need; requests hide agents that take 40 calls to finish.

## Related
[[30-llm-gateway-router]] · [[18-llm-eval-harness]] (quality half) · [[D0-areas-map]] Area 8.
