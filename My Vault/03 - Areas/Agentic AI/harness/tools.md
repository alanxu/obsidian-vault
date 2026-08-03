---
title: Tools
pillar: harness
parent: ./README.md
section: "3.2"
---

# 3.2 Tools

Tools are the agent's API surface. Treat them like a public API.

- **One tool, one job.** `search_users` and `search_users_v2` is a smell.
- **JSON Schema, not prose.** Descriptions: short, with examples and when-NOT-to-use.
- **Errors are data.** Return `{ok, value}` or `{ok: false, error, retryable}`. Never raise raw exceptions across the tool boundary.
- **Idempotent where possible.** Same input → same side-effect-free result, or a clear `idempotency_key`.
- **Side-effects are explicit.** Mark destructive tools; require confirmation tokens in v1.
- **Pagination is the agent's #1 failure mode.** Provide `cursor` + `has_more`; teach the agent to loop until exhausted.
- **Latency matters.** > 2s tool calls tank the loop. Stream, parallelize, or pre-fetch.

```
Tool spec template:
  name: snake_case_verb_noun
  description: "One sentence. When to use, when NOT to use."
  params: typed JSON Schema with enums and examples
  returns: typed response, never free-form
  errors: enumerated, retryable flag
  cost_hint: tokens / latency class
```

See also: [[../governance/safety-guardrails|Safety & Guardrails]] for tool allowlist and side-effect controls.
