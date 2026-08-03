---
title: Anti-Patterns
pillar: quality
parent: ./README.md
type: reference
---

# B. Anti-Patterns (short list)

- **Prompt-only safety.** It will be bypassed. Layer it.
- **Free-form tool outputs.** Always parse/validate.
- **Auto-memory everything.** Memory becomes a junk drawer.
- **"Just add another agent."** Most coordination problems are state-management problems.
- **Optimizing the wrong metric.** Success rate, not vibes.
- **Skipping evals because "it's just a prompt change."** Prompts are code.
- **Hiding the loop from the user.** Black boxes breed distrust.
- **Skill = wrapper around one tool.** That's just a tool with extra steps.
- **Reflection without a metric.** Pure cost, no signal.

See also: [[../context/anti-patterns|Context anti-patterns]] for the memory-specific list.
