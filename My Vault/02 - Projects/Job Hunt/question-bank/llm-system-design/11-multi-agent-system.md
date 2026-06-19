---
title: Design a Multi-Agent System (orchestrator–worker)
slug: multi-agent-system
area: 3 — Agentic Systems
companies: [general, agent-platform cos]
difficulty: ★★★★☆
formats: [Live system design]
related: ["[[09-agent-platform]]", "[[practical-coding/34-multi-agent-orchestration]]", "[[D0-areas-map]]"]
---

# Design a Multi-Agent System

> Multiple role-agents collaborate on a task (researcher → writer → editor; or orchestrator decomposes → workers execute). **The staff move: default to single-agent + tools, and justify *when* multi-agent earns its coordination cost.**

## Problem
"Design a system where agents have different roles and collaborate." Variants: orchestrator–worker (lead decomposes, delegates), planner–critic, parallel fan-out/fan-in.

## Clarify first
- Are subtasks genuinely **parallel/specialized** (the only good reason to go multi-agent)? Shared state needs?
- Latency/cost budget (multi-agent multiplies cost)? Failure isolation needs?

## Architecture
**Orchestrator** (decomposes task, routes) → **worker agents** (each = an agent loop, [[09-agent-platform]]) → results merged on a **shared blackboard/state** → orchestrator aggregates → done. Communication via a message protocol (**A2A** is the emerging standard). Global step/cost budget.

## Deep-dive — orchestration patterns + coordination cost
- **Patterns:** chaining (pipeline), **routing** (classify → specialist), **parallelization** (fan-out/fan-in), **orchestrator–worker** (decompose/delegate), **planner–critic** (propose/evaluate).
- **Coordination is the cost:** errors propagate across agents (compounding); shared state gets tangled; cost = sum over all agents. **Default single-agent + tools;** go multi only when subtasks are parallel or need distinct specialized context/tools.
- **Failure isolation** — one agent erroring shouldn't crash the task; supervisor handles retries/reassignment.
- **Termination** — global budget + progress detection across the whole system, not just per agent.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Single vs multi-agent | simplicity/shared context vs specialization/parallelism + coordination cost |
| Orchestrator vs peer-to-peer | central control/bottleneck vs flexibility/chaos |
| Shared blackboard vs message bus | simple state vs decoupling |
| Parallel vs sequential | latency vs dependency handling |

## Numbers
Cost multiplies by agent count; errors compound across agents → verification + bounded budget critical. Parallelize only independent subtasks to win latency.

## Failure modes
Agents ping-ponging (no global termination) · error propagation · tangled shared state · cost blowup · one agent's failure cascading · coordination overhead exceeding the benefit.

## Top follow-ups
- "Multi-agent worth it?" → only for genuinely parallel/specialized subtasks; else single-agent + tools.
- "Stop it looping forever?" → global step/cost budget + cross-agent progress detection.
- "Agents conflict?" → supervisor/critic resolves; voting; or a single source-of-truth agent.

## Related
[[09-agent-platform]] · practical-coding [[practical-coding/34-multi-agent-orchestration]] (code it) · [[D0-areas-map]] Area 3.
