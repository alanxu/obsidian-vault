---
title: Minimal Agent Loop (ReAct)
slug: minimal-agent-loop
type: agentic
leetcode: null
companies: [Anthropic, OpenAI, Anysphere, Cognition, Robinhood]
difficulty: ★★★☆☆
frequency: rising
formats: [Live, Whiteboard]
levels: 1
time-box: live 30–45 min
tags: [agent, react, tool-calling, loop-breaking, state-machine]
related: ["[[practical-oo-coding-deep-guide]]", "[[interview-prep-master-plan-2026]]"]
---

# Minimal Agent Loop (ReAct)

New baseline in 2026: "build me an agent / show the inference loop." A stateful object — loop + tool registry + state machine — so it's Track B. Keep it **small and correct**; platform depth is the **D3 design** and the **Track G build**, not a coding round.

## Problem
An agent that loops: ask the (mock) model for an action → if a **tool call**, dispatch + feed back the observation → repeat → until a **final answer** or a stop condition. Full tested code: [[practical-oo-coding-deep-guide]] §3.5.

## Core approach (format-agnostic)
Keep `history` + a `tools` registry; `policy(history)->action` stands in for the LLM (keeps it runnable). The signal is the **stop conditions & failure modes**: final / `max_steps` / token budget; **loop detection** (repeated `(tool,args)`); **tool errors captured as observations**, not crashes.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** "implement a simple agent that can use tools," then probing on robustness.
- **Follow-ups:** infinite-loop/no-progress detection, conflicting tool results (vote/re-ask), token budget → summarize/truncate history (memory), retries w/ backoff + **idempotency**, parallel tool calls, sandboxing, **eval** (success rate, steps, cost → D5).
- **Tips:** mock the model so it runs; build the 3 stops + loop guard first; narrate "the happy path is trivial — the value is the failure modes."
- **Pitfalls:** no termination guard (infinite loop), tool exception crashing the agent, no budget, treating it as a full platform (scope creep).

### Whiteboard (when asked to "show the loop")
- **Tips:** draw think→act→observe with the stop conditions labeled; keep it to ~15 lines of pseudocode.
- **Pitfalls:** drifting into platform architecture (that's D3) instead of the loop itself.

## Cross-track map
B = **code the loop** (here) · D3 = **design the platform** (planning/memory/observability/cost) · G = **build a real agent** (take-home) · E Block 4 = **theory** (ReAct/reflection). See [[practical-oo-coding-deep-guide]] §3.5.
