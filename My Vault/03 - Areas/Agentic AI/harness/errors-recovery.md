---
title: Errors & Recovery
pillar: harness
parent: ./README.md
section: "3.5"
---

# 3.5 Errors & Recovery

Failures are the norm. Plan for them.

- **Tool failures.** Distinguish retryable (5xx, timeout) from non-retryable (4xx, validation). Auto-retry with backoff for the first; surface the second to the model.
- **Model failures.** JSON parse errors, schema violations, refusals. Re-prompt with the error inline. After 2 failures, escalate to the user.
- **Hallucinated tool calls.** Validate the schema before execution. Reject unknown tools, never guess.
- **Loops.** Detect (a) same tool N times, (b) no progress on goal for M steps, (c) token cost > threshold. Break with a clear message.
- **Partial completion.** If you must stop mid-task, return a structured `partial_result` plus what's left. Don't return nothing.

See also: [[../governance/reliability-ops|Reliability Ops]] for timeouts, rate limits, and circuit breakers.
