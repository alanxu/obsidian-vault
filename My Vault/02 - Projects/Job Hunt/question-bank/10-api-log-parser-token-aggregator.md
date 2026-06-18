---
title: API Log Parser / Token-Usage Aggregator
slug: api-log-parser-token-aggregator
type: live-coding
leetcode: null
companies: [OpenAI]
difficulty: ★★★☆☆
frequency: medium
formats: [Live, Take-home]
levels: 3
time-box: live 30–45 min
tags: [parsing, aggregation, streaming, robustness]
related: ["[[openai-interview-guide]]", "[[08-multi-file-iterator]]"]
---

# API Log Parser / Token-Usage Aggregator

LLM-flavored parsing: aggregate token usage from API logs. Tests clean parsing + graceful messy-input handling + a streaming follow-up.

## Problem
Lines `user_id | endpoint | tokens_used | timestamp`. Total tokens per user, sorted desc. **Follow-ups:** malformed lines, per-endpoint breakdown, **per-minute rate**, **streaming** (line-by-line). Code: [[openai-interview-guide]] Problem 8.

## Core approach (format-agnostic)
Single pass into `dict[user]→total`; `sorted(items, key=-tokens)`. Rate: bucket by `timestamp // 60`. Streaming: a generator maintaining running aggregates. O(N) + O(U log U).

## By format

### Live · CoderPad (human) — *primary*
- **Follow-ups:** top-k with a **heap** (don't sort all), windowed rate (→ [[23-logger-rate-limiter]]), out-of-order timestamps, multi-file (→ [[08-multi-file-iterator]]).
- **Tips:** ask about malformed-line policy (skip vs error) before coding; mention streaming early.
- **Pitfalls:** crashing on a short/garbage line, loading the whole log into memory, integer parse errors.

### Take-home / work-trial
- **Tips:** ship the streaming version + tests for malformed lines + a README on assumptions.
- **Pitfalls:** no robustness tests; O(N) memory when streaming was the point.

## Related
[[08-multi-file-iterator]] · [[23-logger-rate-limiter]] · [[openai-interview-guide]] P8.
