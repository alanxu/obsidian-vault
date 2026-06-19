---
title: Multi-Agent Systems
slug: multi-agent
area: Agent Concepts
source_q: "Anthropic 100-Q #45–50"
companies: [Anthropic, OpenAI, agent-platform cos]
difficulty: ★★★★☆
related: ["[[16-agent-loops-and-control]]", "[[llm-system-design/11-multi-agent-system]]", "[[practical-coding/34-multi-agent-orchestration]]"]
---

# Multi-Agent Systems

## Prompt
Why use multiple agents? What is a supervisor agent? How do you avoid agent conflict, evaluate multiple agents, and what are the drawbacks?

## Answer
**Why multi-agent:** specialization and parallelism — distinct **roles** (researcher / writer / critic) each with their own tools, context, and prompt, can outperform one over-loaded agent and can run **in parallel**. Useful when subtasks are genuinely separable.

**Supervisor agent:** an **orchestrator** that decomposes the task, **routes** subtasks to worker agents, and aggregates results (orchestrator–worker pattern). It owns the global plan, the stopping condition, and conflict resolution. (Alternative: peer-to-peer with a handoff protocol like A2A.)

**Avoid conflict:** a single source-of-truth / supervisor that arbitrates; clear ownership of shared state (blackboard); a **critic** agent or voting to resolve disagreements; structured handoffs so two agents don't clobber each other.

**Evaluate:** end-to-end **task success**, plus **per-agent** contribution and **trajectory eval** (did each agent's step help?); trace the whole system for replay (non-determinism makes this essential).

**Drawbacks:** coordination cost; **errors propagate across agents** (compounding); cost multiplies by agent count; tangled shared state; harder to debug. → **default to a single agent + tools**; go multi-agent only when subtasks are truly parallel/specialized.

## Tradeoffs
| | Single agent | Multi-agent |
|---|---|---|
| Simplicity / shared context | ✓ | ✗ |
| Specialization / parallelism | ✗ | ✓ |
| Coordination + error propagation | low | high |
| Cost | lower | multiplies |

## Follow-ups
- *"Worth the complexity?"* → only for genuinely parallel/specialized subtasks; otherwise single-agent + tools.
- *"Stop them ping-ponging?"* → global step/cost budget + cross-agent progress detection + supervisor.
- *"Design it?"* → [[llm-system-design/11-multi-agent-system]]; code a small one → [[practical-coding/34-multi-agent-orchestration]].

## Pitfalls
- Reaching for multi-agent by default (coordination cost + propagated errors usually outweigh the benefit).
- No global termination/budget across the system.
- Unclear shared-state ownership → agents overwrite each other.

## Tips
Lead with **"specialization + parallelism, but coordination cost and propagated errors — so default single-agent + tools."** Right-sizing (knowing *when not to*) is the staff signal interviewers reward.
