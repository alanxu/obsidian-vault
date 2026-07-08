---
title: Design an LLM Inference Serving Platform
slug: llm-inference-serving-platform
area: 2 — Inference & Serving
companies: [NVIDIA, OpenAI, Anthropic, Fireworks, Together]
difficulty: ★★★★★
formats: [Live system design, ML-depth round]
related: ["[[07-code-completion-serving-sub100ms]]", "[[08-multi-model-inference-platform]]", "[[30-llm-gateway-router]]", "[[D0-areas-map]]"]
---

# Design an LLM Inference Serving Platform

> Serve LLM tokens at QPS under a latency SLA and a cost budget. The canonical infra-flex prompt. **Open with the mental model:** *prefill is compute-bound, decode is memory-bandwidth-bound* — design around that split.

## Problem
"Design the system that serves a 70B model to many users with low latency and high throughput." Variants: multi-tenant quotas; p99 tail; "serve 100+ models with shared GPUs" (→ [[08-multi-model-inference-platform]]).

## Clarify first
- Latency SLA: **TTFT** (interactive feel) and **TPOT** (throughput)? Streaming?
- QPS + prompt/output length distribution? Model size(s)? Self-host vs API?
- Multi-tenant? SLA tiers? Cost target ($/1M tokens)?

## Architecture
Request → **router/gateway** (admission control, quotas) → **scheduler** (continuous batching) → **GPU worker pool** running the model (KV cache, paged attention) → stream tokens back. Offline: model load/quantize, warm pool, autoscaler.

## Deep-dive — the serving engine
- **KV cache** — caches attention K/V so decode is O(1)/token; the memory hog. Size `= 2 × layers × kv_heads × head_dim × seq × batch × bytes`. GQA/MQA shrink it.
- **Continuous (in-flight) batching** — add/evict requests per step (not fixed batches) → biggest throughput win for mixed lengths.
- **PagedAttention (vLLM)** — page the KV cache → no fragmentation + prefix sharing.
- **Prefix caching** — reuse KV of shared system prompt / chat history.
- **Chunked prefill** — interleave a long prefill with decodes so one big prompt doesn't head-of-line-block.
- **Speculative decoding** — small draft proposes k tokens, big model verifies in one pass → 2–3× when acceptance high.
- **Quantization** (int8/int4) — more batch, less memory, slight quality cost. **FlashAttention** — IO-aware kernel.
- **Prefill/decode disaggregation** (2026, at scale) — separate GPU pools for the two workloads, stream KV between them.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Batch size | throughput ↑ vs per-request latency ↑ |
| Disaggregate prefill/decode | scales each independently vs KV-transfer + complexity; only at scale |
| Speculative decoding | latency win vs draft cost; depends on acceptance |
| Quantization level | memory/cost vs quality (measure on your eval) |
| Shared vs per-tenant fleet | utilization vs isolation/SLA |

## Numbers
70B fp16 ≈ 140 GB weights → ≥2× 80GB GPUs before KV. Report TTFT + TPOT + p50/**p99**, never averages. Decode throughput scales with HBM bandwidth × batch.

## Failure modes
KV-cache OOM under long-context burst (→ admission control/preemption) · head-of-line blocking (→ chunked prefill) · noisy neighbor (→ quotas/fair sched) · autoscale cold start (→ warm pool) · prefix cache stampede.

## Top follow-ups
- "Improve throughput?" → continuous batching + paged attention + quantize + bigger batch to the latency limit.
- "Cut p99 tail?" → chunked prefill, admission control, separate latency-class queues, prefix caching.
- "Multi-tenant?" → per-tenant token quotas + fair scheduler + dedicated pools for premium SLAs.
- "When NOT to disaggregate?" → small scale / short prompts — added complexity loses.
- "Walk me through where a token's latency goes." → queue wait → prefill (prompt_len × compute) → per-token decode (KV reload, HBM-bandwidth-bound) → detok/stream; know which stage each knob attacks: prefix cache→prefill, batching→throughput not latency, speculative→decode.
- "How do you *benchmark* it?" → fixed workload traces (prompt/output length distributions from prod), report TTFT/TPOT p50/p99 at target QPS, sweep batch-size for the latency-throughput frontier; never a single number.
- "Reasoning models change what?" → long autoregressive 'thinking' shifts the mix decode-heavy: KV grows for thousands of hidden tokens, TTFT-to-first-*visible*-token balloons → stream reasoning summaries, cap thinking budgets per tier, decode-optimized pools matter more.

## Related
[[07-code-completion-serving-sub100ms]] · [[08-multi-model-inference-platform]] · [[D0-areas-map]] Area 2.
