---
title: Multi-Agent Orchestration (roles collaborate)
slug: multi-agent-orchestration
type: agentic
leetcode: null
companies: [Anthropic, OpenAI, Cognition, CrewAI, AutoGen-shops, "agent-platform cos broadly", "Microsoft Research"]
difficulty: ★★★★☆
frequency: rising
formats: [Live, Whiteboard]
levels: 1
time-box: live 35–45 min
tags: [agent, multi-agent, orchestration, handoff, coordinator, supervisor, blackboard]
related: ["[[16-minimal-agent-loop]]", "[[34-multi-agent-orchestration]]", "[[interview-prep-master-plan-2026]]"]
---

# Multi-Agent Orchestration

A small coded orchestrator where role-agents (e.g., **researcher → writer → editor**) collaborate via handoffs to finish a task. The *small* version is Track B; the *platform* is D3.

## Problem

Implement a `Coordinator` that runs several role-agents on a task:

- Each agent has a `role` and a `step(state) -> (output, next_role|DONE)`.
- The coordinator routes outputs between agents over a **shared state** (a "blackboard").
- Until `DONE` or a step cap.

Optional **supervisor** pattern: instead of fixed handoffs, a supervisor agent decides the next agent based on state.

## Core approach (format-agnostic)

**Reuse the single-agent loop ([[16-minimal-agent-loop]]) for each agent's internal turn.** Wrap them in a coordinator that handles handoffs.

```python
class Coordinator:
    def __init__(self, agents, supervisor=None, max_steps=20):
        self.agents = {a.role: a for a in agents}
        self.sup = supervisor
        self.max = max_steps

    def run(self, task):
        state = {"task": task, "history": [], "results": {}}
        cur = next(iter(self.agents))        # initial agent (or supervisor picks)
        for step in range(self.max):
            agent = self.agents[cur]
            try:
                out, nxt = agent.step(state)
            except Exception as e:
                out = f"error: {e}"
                nxt = "DONE"
            state["history"].append((cur, out))
            if nxt == "DONE":
                state["final"] = out
                return state
            # routing
            cur = self.sup(state) if self.sup else nxt
        state["final"] = f"max_steps={self.max} reached"
        return state
```

**Blackboard vs message bus:**
- **Blackboard** (shared state dict): simple; risk of stale writes.
- **Message bus** (agents publish/subscribe): clearer ownership, more plumbing.

For the coding round, the **blackboard** is enough. Mention the bus as the production-grade alternative.

## By format

### Live · CoderPad (human)
- **How it appears:** "orchestrate a few agents with different roles to do X" (~25 min), then probing on robustness (~15 min).
- **Follow-ups (real, reported):**
  - **Parallel** agents + merge — dispatch N agents at once on the same task; merge outputs (vote, rank, or synthesize).
  - **Conflict resolution** — two agents disagree; vote? re-ask? supervisor decides?
  - **Supervisor / router** pattern — dynamic next-agent selection.
  - **Message bus** vs shared blackboard.
  - **Failure isolation** — one agent errors; the rest continue.
  - **Loop / termination detection across agents** — A → B → A ping-pong.
  - **Cost control** — cap total tokens across all agents.
  - **Per-agent memory** — does each agent keep its own context, or share?
  - **Per-agent tools** — does each role have its own toolset?
  - **Hierarchical** — a coordinator of coordinators (tree of agents).
  - **Cyclic dependencies** — agents depending on each other's outputs.
  - **Eval** — measure which agent composition succeeds most often.
  - **Typed handoff contract** — replace free-text state with a schema per handoff (researcher emits `{claims: [...], sources: [...]}`) → validation at each hop catches drift early; the structured-outputs discipline ([[../llm-system-design/fundamentals/24-structured-outputs]]) applied between agents.
  - **DAG execution under the hood** — fixed role-chains are a linear DAG; "writer needs researcher AND fact-checker" makes the coordinator exactly [[38-dag-task-scheduler]] with agents as tasks — say the reduction, then reuse that machinery (parallelism, skip-cascade on failure).
- **Tips:**
  - **Reuse the single-agent loop** per role — don't reinvent.
  - **Make handoff explicit** — return `next_role` from `step`.
  - **Guard total steps** — `max_steps` on the coordinator, not just per agent.
  - **Keep shared state simple** — dict-of-strings or dict-of-dicts; resist typed objects.
  - For supervisor: `def supervisor(state) -> role_name`.
  - For failure isolation: try/except per agent; mark `state["results"][role] = "failed"`.
- **Pitfalls:**
  - **No global termination** — agents ping-pong forever; the step cap is essential.
  - **No failure isolation** — one crash kills the whole pipeline.
  - **Unbounded fan-out** — N parallel agents = N×cost.
  - **Tangled shared state** — keys collide, no namespacing.
  - **Recursion** — coordinator calls itself; depth limit.
  - **Token budget per agent vs total** — easy to forget the total.
  - **Determinism** — tests are easier with deterministic handoffs; randomness breaks reproducibility.

### Whiteboard (when it tilts to design)
- **Tips:**
  - Draw agents + coordinator + shared state + the handoff/supervisor protocol.
  - **State the termination + cost guards** explicitly.
- **Pitfalls:**
  - Drifting into full platform architecture — that's **D3** (planning, memory, observability, eval at scale). Keep the coded version small.

### Take-home / work-trial
- **Tips:**
  - Ship a small multi-agent system with 2–3 roles.
  - Tests for: handoff chain, failure isolation, step cap, total token budget.
  - README the routing strategy (handoff vs supervisor).
- **Pitfalls:**
  - No termination tests.
  - No budget enforcement.

## Company variants

- **Anthropic / OpenAI / Cognition** — agent platforms.
- **CrewAI / AutoGen / LangGraph shops** — full multi-agent framework.
- **Microsoft Research / academic agents** — research-flavored reskin.

## Worked example trace

```
Agents: researcher, writer, editor
Task: "Write a short blog post about Redis"

step 0: researcher.step(state) → ("research notes about Redis...", "writer")
step 1: writer.step(state) → ("draft article...", "editor")
step 2: editor.step(state) → ("polished article...", "DONE")

state["final"] = "polished article..."
state["history"] = [(researcher, "research notes..."), (writer, "draft..."), (editor, "polished...")]
```

If `editor.step` raises an exception:
```
step 2: editor.step(state) → exception → ("error: ...", "DONE")
state["final"] = "error: ..."
```

## Cross-track map
- **B** = code a small orchestrator (here)
- **D3** = design the multi-agent platform (planning, memory, observability, eval at scale)
- **G** = build a multi-agent take-home (CrewAI / AutoGen-style)
- See [[interview-prep-master-plan-2026]] §6

## Related
[[16-minimal-agent-loop]] (per-role loop) · [[30-function-calling-tool-handler]] (per-agent tools) · [[33-conversation-memory-manager]] (per-agent memory).