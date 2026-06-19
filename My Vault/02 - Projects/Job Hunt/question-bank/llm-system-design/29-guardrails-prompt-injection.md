---
title: Design Guardrails / Prompt-Injection Defense
slug: guardrails-prompt-injection
area: 7 — Safety, Guardrails & Governance
companies: [Anthropic, Harvey, Glean, OpenAI, fintech]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[09-agent-platform]]", "[[28-content-moderation-at-scale]]", "[[D0-areas-map]]"]
---

# Design Guardrails / Prompt-Injection Defense

> **The thesis:** *treat every input as adversarial and every output as potentially wrong — safety is layered defense-in-depth around a component you can't fully trust.* **Prompt injection has no complete fix** → design to limit blast radius.

## Problem
"Design the guardrail layer for an LLM/agent product: input filtering, prompt-injection defense, PII, output checks, abstention." Especially for agents with tools and enterprise/regulated data.

## Clarify first
- Agent with **tools/actions** (raises injection stakes) or chat-only? Untrusted inputs (web, retrieved docs, user)?
- PII/compliance? Stakes of a bad action? Latency budget for guardrails?

## Architecture (defense-in-depth)
Input → **input guardrails** (moderation, PII detect/redact, injection detection) → model/agent → **output guardrails** (policy filter, PII leak check, groundedness/citation check, structured-output validation, abstention) → action layer with **least privilege + human-confirm for destructive actions**. Provenance/audit throughout.

## Deep-dive — prompt injection (the marquee 2026 risk)
- **The threat:** untrusted content (a web page, a retrieved doc, a tool output) carries instructions that hijack the agent ("ignore previous instructions, exfiltrate data"). Direct (user) and **indirect** (via retrieved/tool content — the dangerous one).
- **No full fix → limit blast radius:** isolate untrusted text from instructions; **least privilege** (the agent can only do what this task needs); **structured tool I/O** (don't let free text issue privileged calls); **human-confirm destructive actions**; sandbox tool execution.
- **Layers:** input moderation/PII + injection detection (imperfect) → constrained generation → output checks → action gating. Assume each layer leaks; stack them with **named residual risk**.
- **Eval:** maintain an **injection/jailbreak test suite**; red-team continuously.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Guardrail strictness | safety vs false positives + latency + friction |
| In-model vs external guardrails | simplicity vs auditability/control |
| Block vs flag vs abstain | safety vs utility (set by stakes) |
| Tool privilege scope | capability vs blast radius |

## Numbers
Injection has no complete fix — design for blast-radius limitation, not prevention. Defense-in-depth: assume each layer is leaky. Asymmetric costs → strictness by stakes.

## Failure modes
Indirect prompt injection via tool/retrieval output · jailbreaks bypassing the system prompt · PII leak in output/logs · ACL leak · over-blocking (kills utility) · model-as-its-own-guardrail (trivially bypassed).

## Top follow-ups
- "Stop prompt injection?" → no full fix; isolate untrusted input, least privilege, structured tool I/O, human-confirm destructive actions, injection eval suite.
- "PII?" → detect+redact input, leak-check output, scrub logs, retention controls.
- "Agent with tools safely?" → least privilege + sandbox + confirm destructive + treat tool output as untrusted.

## Related
[[09-agent-platform]] (injection via tools) · [[28-content-moderation-at-scale]] · [[D0-areas-map]] Area 7.
