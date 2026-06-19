---
title: Design an Agentic Platform / Agent Orchestration
slug: agent-platform
area: 3 — Agentic Systems
companies: [Robinhood, Anysphere, Harvey, Anthropic, OpenAI]
difficulty: ★★★★★
formats: [Live system design, ML-depth round]
related: ["[[10-autonomous-coding-agent]]", "[[11-multi-agent-system]]", "[[practical-coding/16-minimal-agent-loop]]", "[[D0-areas-map]]"]
---

# Design an Agentic Platform / Agent Orchestration

> A system where the LLM *acts* in a loop (plan → tool → observe → repeat). **Open with the mental model:** *reliability is the hard part, not capability* — a 95%-reliable step compounds to ~60% over 10 steps. Frame it as **reliability engineering on a stochastic policy.**

## Problem
"Design the platform that runs agents: planning, tool calls, memory, retries, sandboxing, eval, observability, cost control." Variants: coding agent ([[10-autonomous-coding-agent]]), multi-agent ([[11-multi-agent-system]]), support agent ([[12-customer-support-agent]]).

## Clarify first
- Task horizon (single tool call vs 50-step)? Autonomy level / human-in-the-loop? Tools (read-only vs world-changing)?
- Latency tolerance? Cost budget per task? Reliability bar?

## Architecture
**Agent runtime:** context builder → LLM policy (decide: answer or tool) → **tool dispatcher** (typed schemas, e.g. **MCP**) → sandboxed execution → observation → memory update → loop, with **step/budget caps**. **Platform:** tool registry, memory store (short/long/working), **trace logging**, eval harness, cost meter, guardrails.

## Deep-dive — making a stochastic loop reliable
- **Per-step verification** (compounding error: 0.95^10≈0.6) → check progress each turn; reflection on failure.
- **Bounded execution** — hard step cap + token/cost budget + loop detection (no-progress).
- **Memory** — short-term (context), long-term (vector/DB), working (summarized state to fit window) = context-window engineering.
- **Tool outputs are untrusted** — **prompt injection** via a retrieved page/tool result is a top risk → isolate untrusted text, least privilege, human-confirm destructive actions, sandbox.
- **Observability/eval** — full trace of every thought/tool-call/observation; **trajectory eval** (did each step progress?) + end-to-end task success; replay from traces (non-determinism makes this essential).

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Single vs multi-agent | simplicity/shared context vs specialization/coordination cost |
| ReAct vs plan-then-execute | flexible/wanders vs predictable/brittle |
| Autonomy level | automation vs control/safety |
| Memory strategy | recall vs context cost |
| Stop policy | task completion vs cost/step cap (bound both) |

## Numbers
0.95^10 ≈ 0.60 (verify per step) · a 10-step agent costs 10–50× a single call (→ prefix cache + context compression) · latency stacks per turn (→ parallelize independent tools).

## Failure modes
Compounding errors · context overflow / lost-in-the-middle · infinite loops · tool-call hallucination · **prompt injection via tool output** · runaway cost · non-reproducible bugs.

## Top follow-ups
- "Stop infinite loops?" → step/budget cap + progress check + loop detection.
- "Make it reliable?" → verify each step, constrain tools, retries+reflection, replayable traces, trajectory eval.
- "Multi-agent worth it?" → only for genuinely parallel/specialized subtasks; default single-agent + tools.
- "Security?" → treat tool outputs as untrusted; sandbox; least privilege; human-confirm destructive actions.

## Related
[[practical-coding/16-minimal-agent-loop]] (code the loop) · [[10-autonomous-coding-agent]] · [[11-multi-agent-system]] · [[D0-areas-map]] Area 3.
