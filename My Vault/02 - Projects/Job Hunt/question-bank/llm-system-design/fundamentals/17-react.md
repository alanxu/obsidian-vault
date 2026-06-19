---
title: ReAct (Reason + Act)
slug: react
area: Agent Concepts
source_q: "Anthropic 100-Q #36–40"
companies: [Anthropic, OpenAI, Anysphere, Cognition]
difficulty: ★★★★☆
related: ["[[16-agent-loops-and-control]]", "[[18-agent-memory]]", "[[practical-coding/16-minimal-agent-loop]]"]
---

# ReAct (Reason + Act)

## Prompt
Explain the ReAct workflow. What's the difference between Thought, Action, and Observation? What are ReAct's flaws and how would you improve it?

## Answer
**ReAct interleaves reasoning and acting in a loop:**
- **Thought** — the model reasons about what to do next (a scratchpad: "I need the user's balance, so I'll call the account tool").
- **Action** — it emits a tool call (name + args).
- **Observation** — the system executes the tool and feeds the result back.
- Repeat Thought→Action→Observation until the model emits a final answer.

The **Thought** makes the policy's reasoning explicit (better tool choice, debuggable traces); the **Action** is the externalized effect; the **Observation** grounds the next step in real results instead of hallucinated ones. This grounding is why ReAct beats pure chain-of-thought for tool-use tasks — each step is anchored to reality.

**Flaws:** can **wander** / loop (no global plan); each turn adds latency + tokens; sensitive to tool-call formatting errors; long trajectories overflow context ("lost in the middle"); compounding errors over many steps.

**Improvements:** add a **plan** (plan-then-execute or planner/critic) for structure; **step/budget caps + loop detection** (→ [[16-agent-loops-and-control]]); **reflection** on failure; **memory/summarization** to keep context bounded (→ [[18-agent-memory]]); **self-consistency / verification** of each step.

## Tradeoffs
| | ReAct | Plan-then-execute |
|---|---|---|
| Adaptivity | high (reacts to observations) | low (fixed plan) |
| Predictability | low (can wander) | high |
| Best for | dynamic, unknown paths | well-structured tasks |

## Follow-ups
- *"Why observation matters?"* → grounds the next reasoning step in real results → less hallucination than pure CoT.
- *"ReAct vs CoT?"* → CoT reasons internally only; ReAct *acts* and *observes* between reasoning steps.
- *"Stop it wandering?"* → planning + step caps + reflection + loop detection.

## Pitfalls
- Describing ReAct as just "chain-of-thought" (it adds Act + Observe — the grounding).
- No bound on the loop (wandering, cost).
- Letting the trajectory grow unbounded (context overflow).

## Tips
Recite the loop crisply (**Thought→Action→Observation, repeat**) and explain *why observation grounds it*. Then name the flaws + fixes — interviewers probe "how would you improve ReAct?" specifically.
