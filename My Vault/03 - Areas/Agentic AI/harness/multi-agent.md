---
title: Multi-Agent (Implementation)
pillar: harness
parent: ./README.md
section: "3.4"
---

# 3.4 Multi-Agent (Implementation)

The *design* of multi-agent is in [[../reasoning/architecture-patterns|Architecture Patterns]]. The *implementation* concerns live here.

- **Clear ownership.** Who owns what state. Who can call whom. No shared mutable state across agents.
- **Orchestrator pattern beats free chat.** A planner that hands off to workers is far easier to debug than agents talking to each other.
- **Message schema > natural language between agents.** JSON with `{task, context, expected_output}`. Free-form "conversations" between agents are a debug nightmare.
- **Cost model.** N agents ≈ N x token cost at minimum. Make sure the task is worth it.
- **Failure isolation.** Each step has explicit success/failure, not implicit. One bad agent must not poison the run.
