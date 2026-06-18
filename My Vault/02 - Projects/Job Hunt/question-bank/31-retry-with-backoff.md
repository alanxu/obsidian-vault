---
title: Retry with Exponential Backoff (LLM/tool calls)
slug: retry-with-backoff
type: agentic
leetcode: null
companies: [Robinhood, OpenAI, Anthropic, general AI-eng/infra]
difficulty: ★★★☆☆
frequency: rising
formats: [Live, Take-home]
levels: 1
time-box: live 25–40 min
tags: [agent, retry, backoff, idempotency, reliability, async]
related: ["[[16-minimal-agent-loop]]", "[[06-gpu-credit-manager]]"]
---

# Retry with Exponential Backoff

Wrap a flaky LLM/tool call with retries — the reliability primitive every agent (and fintech infra) needs. A favorite at Robinhood and the labs' applied-AI teams.

## Problem
Implement `with_retry(fn, ...)` (decorator or wrapper): retry on **transient** errors (timeouts, 5xx, **429**), with **exponential backoff + jitter**, a max-attempts cap, an overall **deadline/budget**, respect for a `Retry-After` header, and **idempotency** (don't duplicate side effects on retry).

## Core approach (format-agnostic)
Loop attempts; on a **retryable** error sleep `min(cap, base * 2**attempt) + random_jitter`; stop at max attempts or when the deadline passes; **non-retryable** errors raise immediately. Classify errors explicitly. For idempotency, pass/derive an idempotency key so a retried call is de-duplicated server-side.

```python
import time, random
def with_retry(fn, *, retryable=(TimeoutError,), max_attempts=5, base=0.5, cap=8.0, deadline=None):
    start = time.monotonic()
    for attempt in range(max_attempts):
        try: return fn()
        except retryable as e:
            if attempt == max_attempts - 1: raise
            if deadline and time.monotonic() - start > deadline: raise
            sleep = min(cap, base * 2**attempt) + random.uniform(0, base)  # full jitter
            time.sleep(sleep)
```

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** "make this LLM API call robust."
- **Follow-ups:** **jitter** (why — thundering herd), honor **Retry-After**/rate-limit headers, **circuit breaker**, async version (`asyncio.sleep`), **idempotency** store, per-call deadline vs total budget.
- **Tips:** separate **retryable vs fatal** errors explicitly; mention jitter and the deadline up front; note idempotency for non-read calls.
- **Pitfalls:** retrying non-idempotent writes (double-charge → see [[06-gpu-credit-manager]]), retrying 4xx (won't fix), no cap (infinite), no jitter (synchronized retries), blocking sleep in async code.

### Take-home / work-trial
- **Tips:** ship sync + async, error classification, tests (transient succeeds-on-retry, fatal raises, deadline); README the idempotency story.
- **Pitfalls:** no tests for the retry path, swallowing the final error.

## Related
[[16-minimal-agent-loop]] (loop wraps tool calls in this) · [[06-gpu-credit-manager]] (idempotency) · Track C reliability.
