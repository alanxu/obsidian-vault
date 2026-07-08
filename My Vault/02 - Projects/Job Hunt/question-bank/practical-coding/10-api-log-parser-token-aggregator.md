---
title: API Log Parser / Token-Usage Aggregator
slug: api-log-parser-token-aggregator
type: live-coding
leetcode: null
companies: [OpenAI, Anthropic, Cohere, Mistral, Together, "any AI-eng team", Stripe-events, Datadog]
difficulty: ★★★☆☆
frequency: medium
formats: [Live, Take-home]
levels: 3
time-box: live 30–45 min
time-box-take-home: 3–6 hours
tags: [parsing, aggregation, streaming, robustness, heap, top-k]
related: ["[[openai-interview-guide]]", "[[08-multi-file-iterator]]", "[[23-logger-rate-limiter]]"]
---

# API Log Parser / Token-Usage Aggregator

LLM-flavored parsing: aggregate token usage from API logs. Tests clean parsing + graceful messy-input handling + a streaming follow-up. The "real" version (roll-up + per-endpoint + per-minute rate) is what AI-eng teams actually run.

## Problem

Logs are pipe-delimited lines: `user_id | endpoint | tokens_used | timestamp`.

Operations:
- `total_per_user(logs) -> list[(user, total_tokens)]` — sorted desc by total; tie-break by `user_id` asc.
- `by_endpoint(logs) -> dict[endpoint → total]` — totals broken down by endpoint.
- `per_minute(logs) -> dict[minute_bucket → total]` — rate at minute granularity.
- **Follow-ups:** malformed lines (skip / raise / log), streaming (line-by-line without loading), top-K with heap, out-of-order timestamps.

## Core approach (format-agnostic)

**Three-pass variant:**
1. **Parse** — split on `|`, validate columns, drop malformed (or count them).
2. **Aggregate** — single pass into `dict[user] → total`.
3. **Sort** — `sorted(items, key=lambda x: (-x[1], x[0]))`.

**Streaming variant:** generator that yields `(user, endpoint, tokens, ts)` tuples; running aggregates maintained in dicts; no per-line memory.

**Per-minute rate:** `bucket = timestamp // 60`; `dict[bucket] → total`.

**Top-K with heap:** if you only need top-K, use a min-heap of size K — don't sort all N. Push; replace root when size > K; finalize by sorting heap.

### Worked Python solution

```python
import heapq
from collections import defaultdict

def parse_line(line):
    """Returns (user, endpoint, tokens, ts) or None if malformed."""
    parts = [p.strip() for p in line.split("|")]
    if len(parts) != 4:
        return None
    user, endpoint, tokens_s, ts_s = parts
    try:
        return (user, endpoint, int(tokens_s), int(ts_s))
    except ValueError:
        return None

def total_per_user(logs):
    agg = defaultdict(int)
    bad = 0
    for line in logs:
        rec = parse_line(line)
        if rec is None:
            bad += 1
            continue
        agg[rec[0]] += rec[2]
    return sorted(agg.items(), key=lambda x: (-x[1], x[0])), bad

def by_endpoint(logs):
    agg = defaultdict(int)
    for line in logs:
        rec = parse_line(line)
        if rec: agg[rec[1]] += rec[2]
    return dict(agg)

def per_minute(logs):
    agg = defaultdict(int)
    for line in logs:
        rec = parse_line(line)
        if rec: agg[rec[3] // 60] += rec[2]
    return dict(sorted(agg.items()))

def top_k(logs, k):
    """Top-K users by total tokens."""
    agg = defaultdict(int)
    for line in logs:
        rec = parse_line(line)
        if rec: agg[rec[0]] += rec[2]
    # nlargest equivalent: heapq.nlargest
    return heapq.nlargest(k, agg.items(), key=lambda x: (x[1], -ord(x[0][0]) if x[0] else 0))

# ---------- streaming variant ----------
def iter_records(lines):
    """Generator yielding parsed records; skip malformed silently."""
    for line in lines:
        rec = parse_line(line)
        if rec:
            yield rec

class StreamingAggregator:
    def __init__(self):
        self._by_user = defaultdict(int)
        self._by_endpoint = defaultdict(int)
        self._bad = 0
        self._n = 0

    def feed(self, line):
        rec = parse_line(line)
        if rec is None:
            self._bad += 1
            return
        self._n += 1
        user, endpoint, tokens, _ts = rec
        self._by_user[user] += tokens
        self._by_endpoint[endpoint] += tokens

    def top_users(self):
        return sorted(self._by_user.items(), key=lambda x: (-x[1], x[0]))

    def stats(self):
        return {"n_ok": self._n, "n_bad": self._bad}
```

**Complexity.** Parse O(N); aggregate O(N); sort O(U log U) where U is unique users. Streaming: O(1) memory per call beyond the dicts.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** start with `total_per_user`, follow-ups layer on.
- **Follow-ups (real, reported):**
  - **Top-K with a heap** (don't sort all N).
  - **Windowed rate** — last 60s rate, not just per-minute buckets. → see [[23-logger-rate-limiter]].
  - **Out-of-order timestamps** — sort first, then bucket.
  - **Multi-file** — feed multiple files into the aggregator. → see [[08-multi-file-iterator]].
  - **Per-endpoint percentiles** — p50, p95, p99 latency/tokens.
  - **Real-time alert** — "alert if any user exceeds 1M tokens in 1 min."
  - **CSV vs pipe-delimited** — make the delimiter configurable.
  - **Negative or zero tokens** — clamp / reject / log.
  - **Cost attribution** — extend tokens → dollars with a per-model price table (prompt vs completion tokens priced differently); the [[../llm-system-design/31-llm-observability-cost]] connection in 20 lines.
  - **Exact percentiles without storing all values?** → you can't — O(1)-memory percentile needs a sketch (t-digest / fixed histogram buckets); saying "approximate with a histogram, exact needs the data" beats hand-waving a running p99.
  - **Two-pass vs streaming top-K trap** — top-K users needs *totals* first, so pure single-pass heap-on-lines is wrong (a user's total accumulates); heap applies after aggregation, or over the dict — interviewers plant this.
- **Tips:**
  - **Ask about malformed-line policy** (skip vs error vs log) before coding. Most teams say "skip + count."
  - **Mention streaming early** — even if not asked, offer it as a follow-up design point.
  - For top-K, prefer `heapq.nlargest` over sorting when K << U.
  - Pin the format assumption: 4 columns, pipe-delimited, integer tokens, integer epoch seconds.
- **Pitfalls:**
  - **Crashing on a short/garbage line** — silent fail is fine, but `KeyError` is not.
  - **Loading the whole log into memory** when streaming was the point.
  - **Integer parse errors** — wrap in try/except.
  - **Float timestamps** — confirm integer seconds (epoch) vs ISO 8601 string.
  - **Tie-break direction** — confirm "user_id ascending" vs descending.

### Take-home / work-trial
- **Tips:**
  - Ship the **streaming** version + tests for malformed lines + a README on assumptions.
  - Include a `--top-k N` CLI flag.
  - Add a benchmark showing streaming vs in-memory for a 1M-line log.
  - If asked for "real-time": add an alert threshold and a counter for breaches.
- **Pitfalls:**
  - **No robustness tests** — the spec's whole point.
  - **O(N) memory** when streaming was the requirement.
  - **No timestamps validation** — negative timestamps, future timestamps.

## Company variants

- **OpenAI (canonical)** — "Problem 8" in their bank; tokens are dollars-equivalent in some reskins.
- **Anthropic / Cohere / Mistral / Together** — LLM-flavored reskin.
- **Stripe events / Datadog** — observability-flavored reskin; per-endpoint percentiles.
- **Any AI-eng team** — billing & rate-limit analytics.

## Worked example trace

```
Lines:
u1 | /v1/chat | 100 | 1700000000
u2 | /v1/embed | 50  | 1700000030
u1 | /v1/chat | 200 | 1700000060
bad line

total_per_user → [("u1", 300), ("u2", 50)], bad=1
by_endpoint   → {"/v1/chat": 300, "/v1/embed": 50}
per_minute    → {28333333: 150 (100+50), 28333334: 200}
```

## Related
[[08-multi-file-iterator]] (multi-file streaming) · [[23-logger-rate-limiter]] (windowed rate) · [[openai-interview-guide]] P8.