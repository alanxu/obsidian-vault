---
title: Retry with Exponential Backoff (LLM/tool calls)
slug: retry-with-backoff
type: agentic
leetcode: null
companies: [Robinhood, OpenAI, Anthropic, Stripe, Cloudflare, "any AI-eng/infra team"]
difficulty: ★★★☆☆
frequency: rising
formats: [Live, Take-home]
levels: 1
time-box: live 25–40 min
time-box-take-home: 3–6 hours
tags: [agent, retry, backoff, idempotency, reliability, async, jitter, circuit-breaker]
related: ["[[16-minimal-agent-loop]]", "[[06-gpu-credit-manager]]", "[[30-function-calling-tool-handler]]"]
---

# Retry with Exponential Backoff

Wrap a flaky LLM/tool call with retries — the reliability primitive every agent (and fintech infra) needs. A favorite at Robinhood and the labs' applied-AI teams. The base case is 10 lines; the **interview** lives in the follow-ups.

## Problem

Implement `with_retry(fn, ...)` — a decorator or wrapper:

- Retry on **transient** errors (timeouts, 5xx, **429**).
- **Exponential backoff + jitter**.
- Max-attempts cap.
- Overall **deadline/budget** (don't retry past time T).
- Respect `Retry-After` header when present.
- **Idempotency** for non-read calls (don't duplicate side effects on retry).

## Core approach (format-agnostic)

**Loop attempts; on a retryable error, sleep `min(cap, base * 2**attempt) + random_jitter`; stop at max attempts or when the deadline passes. Non-retryable errors raise immediately. Classify errors explicitly.**

```python
import time, random

class RetryableError(Exception): pass
class FatalError(Exception): pass

def with_retry(fn, *,
               retryable=(TimeoutError, ConnectionError, RetryableError),
               max_attempts=5,
               base=0.5, cap=8.0,
               deadline=None,
               retry_after_fn=None):
    start = time.monotonic()
    for attempt in range(max_attempts):
        try:
            return fn()
        except retryable as e:
            if attempt == max_attempts - 1:
                raise
            if deadline and time.monotonic() - start >= deadline:
                raise
            # Honor Retry-After if provided
            sleep = None
            if retry_after_fn:
                ra = retry_after_fn(e)
                if ra is not None:
                    sleep = float(ra)
            if sleep is None:
                # Full jitter: random in [0, min(cap, base*2**attempt)]
                sleep = random.uniform(0, min(cap, base * 2 ** attempt))
            time.sleep(sleep)
    # unreachable
```

**Async variant:** `asyncio.sleep` instead of `time.sleep`; same logic, `async def with_retry`.

**Idempotency:** caller passes an idempotency key (e.g., request UUID); the underlying call embeds it; downstream dedupes. The retry wrapper itself is idempotent if the call is.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** "make this LLM API call robust" (~15 min), then probing on classification & policy (~10 min).
- **Follow-ups (real, reported):**
  - **Jitter** — why? **Thundering herd** if all clients retry at the same instant; jitter desynchronizes them.
  - **Honor `Retry-After`/rate-limit headers** — third-party tells you when to come back; respect it.
  - **Circuit breaker** — after N consecutive failures, stop calling for a cooldown window.
  - **Async version** — `asyncio.sleep`; non-blocking retry.
  - **Idempotency store** — server-side dedup keyed by request ID.
  - **Per-call deadline vs total budget** — one limits a single attempt; the other limits the whole operation.
  - **Exponential vs linear vs constant** — trade-off; exponential + jitter is the default.
  - **Capped exponential** — `min(cap, base * 2**attempt)` prevents pathological waits.
  - **Errors classification** — `429` retryable, `400` not, `500` retryable, `501` not. Don't blanket-retry.
  - **Observability** — log every retry with attempt #, sleep duration, error class.
  - **Token budget interaction** — if the retry also costs tokens, total budget may be exceeded.
  - **Poison pill** — a request that will always fail; retries just waste time. Detect and bail.
- **Tips:**
  - **Separate retryable vs fatal errors explicitly** — different exception types is clearest.
  - **Mention jitter up front** — explains the design before they ask.
  - **Mention idempotency for non-read calls** — set context early.
  - For circuit breaker: state machine (CLOSED → OPEN → HALF_OPEN).
  - For async: same shape; just `await` everywhere.
- **Pitfalls:**
  - **Retrying non-idempotent writes** — double-charge → see [[06-gpu-credit-manager]].
  - **Retrying 4xx** — won't fix; wastes time and quota.
  - **No cap** — `base * 2**100` is absurd.
  - **No jitter** — synchronized retries hammer the server when it recovers.
  - **Blocking sleep in async code** — `time.sleep` in async freezes the loop; use `asyncio.sleep`.
  - **Sleep past the deadline** — cap the sleep, not just the count.
  - **Logging the call args on every retry** — leaks PII / secrets; redact.

### Take-home / work-trial
- **Tips:**
  - Ship sync + async variants.
  - Error classification (`retryable` predicate or exception classes).
  - Tests: transient succeeds-on-retry, fatal raises immediately, deadline respected, jitter bounded.
  - README the idempotency story.
- **Pitfalls:**
  - **No tests for the retry path** — the bug surface.
  - **Swallowing the final error** — must propagate.
  - **Tests that don't actually wait** — use `monkeypatch` to stub `time.sleep`.
  - **Retry budget not aligned with the call's own timeout** — call may run 30s while deadline is 5s.

### Onsite · NR (Google-style)
- **Tips:** Draw the loop with attempt counter, sleep, and decision branches.
- **Pitfalls:** Forgetting to honor `Retry-After`.

## Company variants

- **Robinhood (canonical)** — applies to every infra call; reliability bar is high.
- **OpenAI / Anthropic / Stripe / Cloudflare** — same primitive, different scopes.
- **Any AI-eng / infra team** — non-negotiable baseline.

## Worked example trace

```
fn = lambda: call_llm()      # raises TimeoutError 1/3 of the time
max_attempts=5, base=0.5, cap=8

attempt 0: TimeoutError → sleep uniform(0, 0.5)
attempt 1: TimeoutError → sleep uniform(0, 1.0)
attempt 2: success → return result
```

If `429 Too Many Requests` with `Retry-After: 2`: skip the backoff formula, sleep exactly 2s.

## Related
[[16-minimal-agent-loop]] (loop wraps tool calls in this) · [[06-gpu-credit-manager]] (idempotency story) · [[30-function-calling-tool-handler]] (when this wraps a tool dispatch).