---
title: Multi-Agent Orchestration (roles collaborate)
slug: multi-agent-orchestration
type: agentic
leetcode: null
companies: [general AI-eng, agent-platform cos; also D3]
difficulty: ★★★★☆
frequency: rising
formats: [Live, Whiteboard]
levels: 1
time-box: live 35–45 min
tags: [agent, multi-agent, orchestration, handoff, coordinator]
related: ["[[16-minimal-agent-loop]]", "[[interview-prep-master-plan-2026]]"]
---

# Multi-Agent Orchestration

A small coded orchestrator where role-agents (e.g., **researcher → writer → editor**) collaborate via handoffs to finish a task. The *small* version is Track B; the *platform* is D3.

## Problem
Implement a `Coordinator` that runs several role-agents on a task: each agent has a `role` and a `step(state) → (output, next_role|DONE)`; the coordinator routes outputs between agents over a shared state, until `DONE` or a step cap. Support a **supervisor** that decides the next agent.

## Core approach (format-agnostic)
Agents = objects with `step(state)`. Coordinator loop: current agent acts → updates **shared state (blackboard)** → returns handoff target (or supervisor picks next) → repeat with a **max-steps** guard. Reuse the single-agent loop ([[16-minimal-agent-loop]]) for each agent's internal turn.

```python
class Coordinator:
    def __init__(self, agents, supervisor=None, max_steps=20):
        self.agents={a.role:a for a in agents}; self.sup=supervisor; self.max=max_steps
    def run(self, task):
        state={"task":task,"history":[]}; cur=next(iter(self.agents))
        for _ in range(self.max):                       # termination guard
            out, nxt = self.agents[cur].step(state)
            state["history"].append((cur, out))
            if nxt == "DONE": return state
            cur = self.sup(state) if self.sup else nxt   # routing: handoff or supervisor
        return state                                     # hit step cap
```

## By format

### Live · CoderPad (human)
- **How it appears:** "orchestrate a few agents with different roles to do X."
- **Follow-ups:** **parallel** agents + merge, conflict resolution between agents, **supervisor/router** pattern, message bus vs shared blackboard, failure isolation (one agent errors), loop/termination detection across agents, cost control.
- **Tips:** reuse the single-agent loop per role; make handoff explicit (return next role); guard total steps; keep shared state simple.
- **Pitfalls:** no global termination (agents ping-pong forever), no failure isolation, unbounded fan-out/cost, tangled shared state.

### Whiteboard (when it tilts to design)
- **Tips:** draw agents + coordinator + shared state + the handoff/supervisor protocol; **state the termination + cost guards**.
- **Pitfalls:** drifting into full platform architecture — that's **D3** (planning, memory, observability, eval at scale). Keep the coded version small.

## Cross-track map
B = code a small orchestrator (here) · **D3 = design the multi-agent platform** · G = build a multi-agent take-home (CrewAI/AutoGen-style). See [[interview-prep-master-plan-2026]] §6.
