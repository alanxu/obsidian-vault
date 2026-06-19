---
title: Design Sub-100ms Code-Completion Serving (Cursor/Anysphere)
slug: code-completion-serving-sub100ms
area: 2 — Inference & Serving
companies: [Anysphere, GitHub Copilot-style]
difficulty: ★★★★☆
formats: [Live system design]
related: ["[[06-llm-inference-serving-platform]]", "[[10-autonomous-coding-agent]]", "[[D0-areas-map]]"]
---

# Design Sub-100ms Code-Completion Serving

> The Anysphere/Cursor prompt: stream code completions at **sub-100ms** while the user types, across 100k-file repos. Latency is the product — every architectural choice serves TTFT.

## Problem
As the user types, return a relevant completion in <100ms. Sub-problems: codebase context (which files/symbols?), low-latency inference, cancellation (keystrokes invalidate in-flight requests), cost at scale.

## Clarify first
- Inline single-line vs multi-line vs whole-function? Repo size? Privacy (proprietary code)?
- Acceptable quality/latency trade? Self-hosted models?

## Architecture
Editor → debounce + cancel-previous → **context builder** (open file + nearby symbols + retrieved repo context) → **completion model** (small/distilled, GPU-resident) with **aggressive prefix cache on the open file** → stream → client renders + cancellation.

## Deep-dive — winning the latency budget
- **Small/distilled model** kept **GPU-resident** (no cold load); speculative decoding for the few tokens.
- **Prefix caching on the current file** — the file context repeats across keystrokes; cache its KV so each keystroke only processes the delta.
- **Codebase context** — index the repo (embeddings + symbol graph); retrieve a tight, relevant context (not the whole repo) — this is RAG with a sub-ms budget, so precompute/cache.
- **Cancellation** — every keystroke cancels the in-flight request (cooperative cancel) to avoid wasted compute; debounce.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Model size | latency/cost (small) vs completion quality (big) |
| Context breadth | relevance (more files) vs latency/cost |
| Speculative decoding | latency win vs draft cost |
| Cache aggressiveness | speed vs staleness as file changes |

## Numbers
<100ms TTFT budget → small model, prefix cache, GPU-resident, minimal context assembly. Cancellation rate is high (most completions are abandoned) → cheap-to-cancel matters.

## Failure modes
Latency spikes from large context assembly · cold model load · cache invalidation on every edit · wasted compute on cancelled requests · poor completion from too-narrow context.

## Top follow-ups
- "Sub-100ms?" → small GPU-resident model + prefix cache on open file + speculative decoding + tight context.
- "100k-file repo context?" → index (embeddings + symbol graph), retrieve a small relevant slice, precompute/cache.
- "Cancellation?" → debounce + cancel-previous; design tools to be cheap to abort.

## Related
[[06-llm-inference-serving-platform]] (Area 2 base) · [[10-autonomous-coding-agent]] (the agent half) · [[D0-areas-map]] Areas 2+3.
