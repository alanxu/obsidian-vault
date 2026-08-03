---
title: Compaction
pillar: context
parent: ./README.md
section: "2.4"
---

# 2.4 Compaction

- Triggers: token threshold, step count, sub-goal complete, or user message. Don't wait for OOM.
- Keep recent turns verbatim, summarize older ones. Preserve: decisions, open questions, failed approaches, user preferences.
- Compaction is lossy by design. The lossier it is, the better your retrieval needs to be.
