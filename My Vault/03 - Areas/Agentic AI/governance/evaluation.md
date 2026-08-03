---
title: Evaluation
pillar: governance
parent: ./README.md
section: "4.5"
---

# 4.5 Evaluation

Evals are the product. Without them, you're shipping vibes.

- **Golden sets.** Real tasks, real expected outcomes. Start at ~50, grow to 500+.
- **Three layers.**
  1. **Deterministic** — schema, tool calls, exact-match answers. Cheap, fast, CI-grade.
  2. **Heuristic** — regex, JSON shape, similarity scores, must-contain / must-not-contain.
  3. **LLM-as-judge** — for open-ended quality. Always blind, always paired with a rubric. Use a different model than the one being tested.
- **Per-task metrics.** Success rate, steps-to-success, cost, latency, user-thumbs. Track all.
- **Regression gates.** PR that drops success rate by N% blocks merge.
- **Offline + online.** Offline golden set gates releases. Online traces feed back into the set.
- **Anti-pattern.** Optimizing a single LLM-judge prompt without human spot-checks → agent that games the judge.

See also: [[../quality/pre-ship-checklist|Pre-Ship Checklist]] for where evals plug into the release gate.
