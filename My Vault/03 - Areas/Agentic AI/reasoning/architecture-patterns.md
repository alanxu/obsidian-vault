---
title: Architecture Patterns
pillar: reasoning
parent: ./README.md
section: "1.1"
---

# 1.1 Architecture Patterns

| Pattern                                  | When to use                                      | Trade-off                                |
| ---------------------------------------- | ------------------------------------------------ | ---------------------------------------- |
| **ReAct** (reason + act inline)          | Tool-heavy, short tasks, observable reasoning    | Verbose, expensive tokens                |
| **Plan-and-Execute**                     | Multi-step, long-horizon (>5 steps, >3 branches) | Plan goes stale; needs replan            |
| **Router**                               | Many specialized sub-agents                      | Routing errors compound                  |
| **Multi-agent** (orchestrator + workers) | Parallelizable, role-specialized work            | Coordination overhead, conflicting state |
| **Reflection / Self-critique**           | Quality-sensitive outputs (code, writing)        | 2x cost, can loop forever                |

**Rule of thumb:** start with the simplest loop. Add a planner only when steps > 5 or branches > 3. Add reflection only when eval shows quality below bar.

See also: [[../harness/multi-agent|Multi-agent implementation]] in the Harness pillar.
