---
title: Design a Multi-Model Serverless Inference Platform
slug: multi-model-inference-platform
area: 2 — Inference & Serving
companies: [Fireworks, Together, Modal, Replicate, Baseten]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[06-llm-inference-serving-platform]]", "[[15-multi-tenant-finetuning-service]]", "[[D0-areas-map]]"]
---

# Design a Multi-Model Serverless Inference Platform

> The Fireworks/Together prompt: serve **100+ open models** for many tenants on a **shared GPU fleet**, with per-model autoscaling, cold starts, and fair sharing. "Inference as a product."

## Problem
"Design the inference-serving system supporting 100+ open-source models with efficient GPU sharing." Variants: serverless (scale-to-zero), dedicated endpoints, multi-tenant LoRA (→ [[15-multi-tenant-finetuning-service]]).

## Clarify first
- How many models / sizes / traffic skew (few hot, long tail)? SLA tiers (serverless vs dedicated)?
- Cold-start tolerance? Multi-tenant isolation requirements? Cost target?

## Architecture
Request → **router** (model → GPU pool, by capacity/affinity) → **autoscaled per-model worker pools** (or shared workers that hot-swap weights) → serving engine ([[06-llm-inference-serving-platform]]) → response. Control plane: model registry, weight cache, autoscaler, quotas, billing.

## Deep-dive — GPU sharing across many models
- **Hot vs cold models:** keep hot models resident; **scale-to-zero** the long tail. Cold start = load weights to GPU (slow) → keep a **warm pool**, **fast weight loading** (mmap, layered cache), and **model caching** on local NVMe.
- **Multiplexing:** pack small models together on a GPU; isolate large ones. **LoRA multiplexing** — one base model + many adapters swapped per request (huge win for fine-tuned tenants).
- **Autoscaling per model** by its own traffic; scale-to-zero idle ones; predictive pre-warm for known spikes.
- **Fairness/quotas:** per-tenant token quotas + fair scheduler so one tenant can't starve others.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Scale-to-zero vs warm | cost (zero) vs cold-start latency |
| Dedicated vs shared pool | isolation/SLA vs utilization/cost |
| LoRA multiplex vs separate | density/cost vs per-model perf isolation |
| Local weight cache size | cold-start speed vs NVMe cost |

## Numbers
Cold start (weight load) can be seconds → warm pool + fast loading. Utilization × $/GPU-hr is the business; long-tail models kill utilization → scale-to-zero + multiplexing.

## Failure modes
Cold-start latency on a tail model · GPU fragmentation (can't fit a request) · noisy neighbor · weight-cache thrash · autoscale lag on a spike.

## Top follow-ups
- "100+ models, shared GPUs?" → hot resident + scale-to-zero tail + warm pool + LoRA multiplexing.
- "Cold starts?" → warm pool + fast weight load + local NVMe cache + predictive pre-warm.
- "Multi-tenant LoRA?" → one base + adapter swap per request; per-tenant quotas.
- "Serverless vs dedicated?" → serverless for bursty/cheap; dedicated for steady/SLA.

## Related
[[06-llm-inference-serving-platform]] · [[15-multi-tenant-finetuning-service]] · [[D0-areas-map]] Area 2.
