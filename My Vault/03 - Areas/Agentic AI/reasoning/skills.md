---
title: Skills (≠ Tools)
pillar: reasoning
parent: ./README.md
section: "1.3"
---

# 1.3 Skills (≠ Tools)

**Tools** are atomic functions. **Skills** are composable, named procedures ("review a PR", "debug a test failure", "triage an incident") that orchestrate multiple tools + reasoning steps for a recurring class of task.

- Skills live in a registry, indexed by description. The model picks one when it matches.
- Each skill is a prompt + a tool sequence + success criteria — versioned, eval'd, and updateable without retraining.
- Build skills from observed successful traces, not from imagination. If the agent has done it well 3 times, you have a skill candidate.

**Anti-pattern:** a skill is not a wrapper around one tool. If it is, it's just a tool.
