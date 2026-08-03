---
title: Reliability Ops
pillar: governance
parent: ./README.md
section: "4.6"
---

# 4.6 Reliability Ops

Operational reliability, not local logic.

- **Timeouts everywhere.** LLM calls, tool calls, total step. Pick numbers you can defend in an incident.
- **Rate limit awareness.** 429s mean back off + queue, not crash. Honor `Retry-After`.
- **Circuit breakers.** If a tool fails N times in M minutes, short-circuit and surface to the model.
- **Graceful degradation.** Tool down? Return a clear "X is currently unavailable" — don't loop.
- **Model fallbacks.** Primary → secondary model on rate limit / error. Same prompt contract.
- **Concurrency control.** Per-user locks for stateful agents. Global locks for expensive resources.

See also: [[../harness/errors-recovery|Errors & Recovery]] — the in-loop layer of the same concern.
