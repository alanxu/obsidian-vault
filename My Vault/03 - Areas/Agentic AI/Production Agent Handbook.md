---
title: Production Agent Handbook
tags: [agent, llm, infra, handbook]
type: reference
status: living
index: true
---

# Production Agent Handbook

A condensed reference for designing, building, and shipping LLM agents that work in production. Organized as four orthogonal pillars + a cross-cutting appendix. Optimized for builders, not beginners.

```
Reasoning        — how the model thinks
Context & Memory — what the model knows
Harness          — the runtime wrapping the model
Governance       — operating it safely at scale
Quality          — release gate, anti-patterns, further reading
```

---

## 0. Definition

An **agent** is an LLM-driven loop that, given a goal, decides its own next actions against tools/state until a stopping condition is met. Everything else (memory, planning, multi-agent) is an extension of this loop.

```
observe → reason → act → observe …
```

If your system has no tools and no loop, it's a chatbot, not an agent.

---

## Pillars

- [[reasoning/README|Reasoning]] — architecture patterns, planning, skills, prompting, reflection
- [[context/README|Context & Memory]] — memory layers, scratchpad, retrieval, compaction, write policy
- [[harness/README|Harness]] — the core loop, tools, state, multi-agent, errors, model API
- [[governance/README|Governance]] — safety, observability, cost, latency, eval, reliability, UX
- [[quality/README|Quality]] — pre-ship checklist, anti-patterns, further reading

## Reference Material

- [[harness/minimax-api|MiniMax Model API Reference]] — wire-level spec for MiniMax M-series (Anthropic & OpenAI compat)
- [[governance/aws-bedrock-services|AWS Agentic AI Services Reference]] — provider map for the AWS / Bedrock AgentCore substrate

## Conventions

- Every sub-file has frontmatter with `pillar:` and `parent:` wikilinks — open the pillar README first.
- Cross-pillar links are written as `../<pillar>/<file>` so wikilinks resolve from any file.
- Pillar numbers (§1, §2, …) match the original handbook for easy mental mapping.
