---
title: Prompting
pillar: reasoning
parent: ./README.md
section: "1.4"
---

# 1.4 Prompting

A system prompt is a contract. Be precise.

**Structure that scales:**

```
1. Role         — one line. Who you are, who you serve.
2. Capabilities — what you can do. Bullets, not prose.
3. Constraints  — what you must never do. Hard rules.
4. Workflow     — the default loop, in 3–7 steps.
5. Output       — exact format, schema, when to use tools vs answer.
6. Examples     — 1–3 diverse, edge-case included.
```

**Key techniques:**

- **CoT only when needed.** For tool use, one short "think" line beats 5 paragraphs. Verbose CoT burns tokens and slows the loop.
- **Few-shot > instructions** for format adherence.
- **Negative examples** ("do not do X") are sticky.
- **Escape hatches.** Always include "if unsure, ask the user." Agents that hallucinate when blocked are toxic.
- **Versioned prompts.** Treat them like code: review, diff, canary, rollback.
