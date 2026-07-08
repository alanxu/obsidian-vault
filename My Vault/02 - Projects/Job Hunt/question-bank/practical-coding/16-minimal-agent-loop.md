---
title: Minimal Agent Loop (ReAct)
slug: minimal-agent-loop
type: agentic
leetcode: null
companies: [Anthropic, OpenAI, Anysphere, Cognition, Robinhood, Harvey, "any agent-focused shop"]
difficulty: ★★★☆☆
frequency: rising
formats: [Live, Whiteboard]
levels: 1
time-box: live 30–45 min
tags: [agent, react, tool-calling, loop-breaking, state-machine, stop-conditions]
related: ["[[practical-oo-coding-deep-guide]]", "[[30-function-calling-tool-handler]]", "[[31-retry-with-backoff]]", "[[interview-prep-master-plan-2026]]"]
---

# Minimal Agent Loop (ReAct)

New baseline in 2026: "build me an agent / show the inference loop." A stateful object — loop + tool registry + state machine — so it's Track B. Keep it **small and correct**; platform depth is the **D3 design** and the **Track G build**, not a coding round.

## Problem

An agent that loops: ask the (mock) model for an action → if a **tool call**, dispatch + feed back the observation → repeat → until a **final answer** or a stop condition.

```python
agent.run(task: str) -> {"status": str, "answer": Any, "history": [...]}
```

Return statuses: `"done"` (final answer), `"max_steps"` (hit cap), `"budget_exceeded"` (token limit), `"loop_detected"` (repeated action).

## Core approach (format-agnostic)

The skeleton is 15 lines. The **grading** is in the failure modes. Keep these in mind from the first commit:

1. **Mock the model** with `policy(history) -> action` so the code runs offline.
2. **Stop conditions:** `final` answer · `max_steps` cap · `token_budget` exceeded.
3. **Loop detection:** repeated `(tool, args)` → bail with `"loop_detected"`.
4. **Tool-error capture:** exceptions become observations, not crashes.

### Worked Python solution

```python
class Agent:
    def __init__(self, policy, tools, max_steps=10, token_budget=10000):
        self.policy = policy          # callable(history) -> action dict
        self.tools = tools            # name -> callable(**args) -> observation
        self.max_steps = max_steps
        self.token_budget = token_budget

    def run(self, task):
        history = [{"role": "user", "content": task}]
        tokens = 0
        seen = set()                                  # loop detection
        for _ in range(self.max_steps):
            action = self.policy(history)
            tokens += action.get("tokens", 0)
            if tokens > self.token_budget:
                return {"status": "budget_exceeded", "history": history}
            if action["type"] == "final":
                return {"status": "done", "answer": action["answer"], "history": history}
            key = (action["tool"], str(action.get("args", {})))
            if key in seen:
                return {"status": "loop_detected", "history": history}
            seen.add(key)
            name, args = action["tool"], action.get("args", {})
            history.append({"role": "assistant", "content": f"call {name}({args})"})
            if name not in self.tools:
                obs = f"error: unknown tool '{name}'"
            else:
                try:
                    obs = self.tools[name](**args)
                except Exception as e:
                    obs = f"error: {e}"
            history.append({"role": "tool", "name": name, "content": str(obs)})
        return {"status": "max_steps", "history": history}
```

**Complexity.** O(steps × policy_cost). The loop is cheap; the policy (LLM call) dominates in production.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** "implement a simple agent that can use tools" (~15 min), then probing on robustness (~15 min).
- **Follow-ups (real, reported):**
  - **Infinite-loop / no-progress detection** — repeated `(tool, args)` or repeated `observation`.
  - **Conflicting tool results** — vote, re-ask, or pick latest.
  - **Token budget → summarize / truncate history** → see [[33-conversation-memory-manager]].
  - **Retries with backoff** for tool calls → see [[31-retry-with-backoff]].
  - **Idempotent tool calls** — pass `request_id` so retries don't double-fire.
  - **Parallel tool calls** — dispatch multiple tools in one step, wait for all.
  - **Sandboxing** — tools run in a restricted environment.
  - **Eval / observability** — log every step; compute success rate, steps-per-task, cost-per-task → Track D5.
  - **Reflection / self-critique** — after a final answer, ask the model to check itself; loop back if not satisfied.
  - **Plan-then-execute** — separate "make a plan" step from "execute each step" steps.
  - **Context assembly per turn** — what exactly goes into `policy(history)` at step 30? Full transcript is wrong (cost + window) → compressed state: system + plan + recent turns + summarized older ([[33-conversation-memory-manager]]); asking "what's my context policy" unprompted is a 2026 differentiator.
  - **Pause/resume (durable agent)** — serialize `(history, budgets, seen)` so the loop can survive a restart or await human approval mid-task; needs idempotent tools on resume — the durable-execution probe.
- **Tips:**
  - **Mock the model** so it runs; `policy = lambda h: next_action` is enough.
  - Build the 3 stops + loop guard **first**; happy path is trivial.
  - **Narrate** "the happy path is trivial — the value is in the failure modes."
  - For parallel tool calls: dispatch via `concurrent.futures.ThreadPoolExecutor`, gather observations, append all in one step.
  - Distinguish **exhausting steps** vs **looping** vs **budget exhaustion** — three different statuses.
- **Pitfalls:**
  - **No termination guard** — infinite loop; spec says max 10 steps; respect it.
  - **Tool exception crashing the agent** — wrap every dispatch in try/except.
  - **No budget** — runaway cost; spec usually names a budget.
  - **Treating it as a full platform** — scope creep into D3.
  - **Off-by-one on `max_steps`** — `for _ in range(10)` allows 10 steps, not 11.
  - **Loop detection on stringified args** — `{"a": 1}` vs `{"a": 1.0}` vs `{"a": True}` may not dedupe. Normalize.

### Whiteboard (when asked to "show the loop")
- **Tips:**
  - Draw think → act → observe with the stop conditions labeled.
  - Keep it to ~15 lines of pseudocode.
  - State the three failure modes (max_steps, loop, budget).
- **Pitfalls:**
  - Drifting into platform architecture (memory, eval, observability at scale) — that's D3.
  - Writing too much detail in pseudocode.

## Company variants

- **Anthropic / OpenAI / Anysphere / Cognition** — canonical; sometimes wrapped in "build Claude Code-lite."
- **Robinhood** — applied-AI agent for finance ops; reliability emphasis.
- **Harvey / Casetext** — legal AI; tool use for case lookup.
- **Any agent-focused shop** — base expectation in 2026.

## Worked example trace

```
Task: "What's the weather in Paris?"
Policy (mock):
  step 0: {tool:"get_weather", args:{city:"Paris"}, tokens:120}
  step 1: {type:"final", answer:"Paris: 18°C, clear", tokens:50}

Run:
  step 0: append "call get_weather(...)"; dispatch; obs = "18°C, clear"; append tool msg
  step 1: tokens total = 170 < budget; "final" → return done
```

## Cross-track map
- **B** = code the loop (here)
- **D3** = design the platform (planning, memory, observability, cost)
- **G** = build a real agent (take-home)
- **E Block 4** = theory (ReAct, reflection, planning)

See [[practical-oo-coding-deep-guide]] §3.5.

## Related
[[30-function-calling-tool-handler]] (the dispatch) · [[31-retry-with-backoff]] (tool reliability) · [[33-conversation-memory-manager]] (history budget) · [[34-multi-agent-orchestration]] (multiple agents).