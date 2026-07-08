---
title: Why Agents Loop, and How to Bound Them
slug: agent-loops-and-control
area: Agent Concepts
source_q: "Anthropic 100-Q #33, #34, #35"
companies: [Anthropic, OpenAI, Anysphere, Robinhood, Cognition]
difficulty: ★★★★☆
related: ["[[17-react]]", "[[19-multi-agent]]", "[[llm-system-design/09-agent-platform]]", "[[practical-coding/16-minimal-agent-loop]]"]
---

# Why Agents Loop, and How to Bound Them

## Prompt
Why do agents get stuck in loops? How do you bound an agent's behavior? What's the value of planning?

## Answer
**Why they loop:** the policy is a **stochastic LLM** with imperfect memory of what it already tried. It can repeat the same failing tool call, oscillate between two actions, or never decide it's "done" — especially as the context grows and earlier steps get lost. And **errors compound**: a 95%-reliable step is only `0.95^10 ≈ 0.60` over 10 steps, so long horizons drift.

**How to bound it (defense in depth):**
- **Hard caps:** `max_steps` and a **token/cost budget** — a stuck agent can't run forever or burn unbounded money.
- **Loop/no-progress detection:** detect repeated `(tool, args)` or lack of state change → abort or change strategy.
- **Per-step verification / reflection:** check progress each turn; on failure, reflect and try differently.
- **Constrain the action space:** fewer, well-scoped tools; **least privilege**; human-confirm destructive actions.
- **Clear stopping condition:** explicit "done" criteria, not just "until it feels finished."

**Value of planning:** decomposing the task up front (plan-then-execute, or a planner/critic) gives structure, makes progress checkable, and reduces aimless wandering — at the cost of brittleness if the world surprises the plan (ReAct is more adaptive; → [[17-react]]).

## Tradeoffs
| Lever | Gains | Costs |
|---|---|---|
| Step/budget cap | bounded cost/time | may cut off a long-but-valid task |
| Planning up front | structure, checkability | brittle to surprises |
| More autonomy | capability | needs more guardrails |
| Fewer tools | less confusion | less flexibility |

## Follow-ups
- *"Detect a stuck agent?"* → repeated action / no state change / step cap + progress check.
- *"Why does reliability matter more than model IQ?"* → 0.95^10 ≈ 0.6 → per-step verification beats a slightly smarter model.
- *"Plan-then-execute vs ReAct?"* → predictable-but-brittle vs flexible-but-wanders (→ [[17-react]]).
- *"Does the compounding math actually hold?"* → it assumes independent, unrecoverable errors — the point of **verification + retry/reflection** is to break both assumptions: a detected error becomes a retry, not a failure, so effective per-step reliability rises above raw model reliability. That's *why* verification beats a smarter model.
- *"Checkpoint/resume for long tasks?"* → persist state at plan boundaries (sub-task done + artifacts); on crash or bad step, resume from last good checkpoint instead of restarting — turns a 60%-success 10-stepper into near-reliable batches.

## Pitfalls
- No step/budget cap (runaway loops + cost — the classic production incident).
- Giving an agent broad/destructive tools without confirmation or sandbox.
- Treating it as a capability problem when it's a **reliability** problem.

## Tips
Frame agents as **"reliability engineering on a stochastic loop"** — lead with compounding error (0.95^10≈0.6) and the bounded-execution guardrails. That single framing is the staff signal across every agent question.
