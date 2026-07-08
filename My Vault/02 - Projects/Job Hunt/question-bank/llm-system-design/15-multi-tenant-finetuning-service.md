---
title: Design a Multi-Tenant Fine-Tuning Service (LoRA)
slug: multi-tenant-finetuning-service
area: 4 — Training & Fine-tuning
companies: [Together, Cohere, OpenAI, Fireworks]
difficulty: ★★★★☆
formats: [Live system design]
related: ["[[08-multi-model-inference-platform]]", "[[13-distributed-training-70b]]", "[[D0-areas-map]]"]
---

# Design a Multi-Tenant Fine-Tuning Service (LoRA adapters)

> The Together/Cohere prompt: let many customers fine-tune on their data and serve the results cheaply via **LoRA adapter multiplexing** on a shared base model, with per-tenant isolation.

## Problem
"Design the fine-tuning service with multi-tenant LoRA adapter management and per-customer isolation." Both the **training** side (run jobs) and the **serving** side (host many adapters).

## Clarify first
- Number of tenants/adapters? Base model(s)? Data isolation/residency requirements?
- Training SLA (how fast a job)? Serving traffic per adapter (hot vs cold)?

## Architecture
- **Training plane:** per-tenant job queue → schedule on GPU pool → **LoRA/QLoRA** fine-tune (cheap, small adapters) → validate (eval gate) → store adapter (versioned) in registry. Tenant data isolated.
- **Serving plane:** one **base model resident** + **swap LoRA adapters per request** (adapter multiplexing — many tenants, one base) → route by tenant/adapter → serving engine ([[08-multi-model-inference-platform]]).

## Deep-dive — LoRA multiplexing + isolation
- **Why LoRA:** full fine-tune per tenant is prohibitively expensive; LoRA adapters are tiny (MBs) and **share one base model** → serve thousands of tenants on a few GPUs.
- **Adapter multiplexing:** load/unload adapters dynamically; hot adapters resident, cold ones in cache; batch requests across adapters where the engine supports it (e.g. punica/S-LoRA-style).
- **Isolation:** tenant data never crosses; per-tenant quotas; data residency; adapter access control.
- **Eval gate:** auto-eval each fine-tune before it's servable (don't ship a regressed adapter).

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| LoRA vs full fine-tune | cost/density/many-tenants vs max quality |
| Adapter resident vs cached | latency vs memory |
| Shared base vs per-tenant model | cost/density vs isolation |
| Eval strictness | ship speed vs quality |

## Numbers
LoRA adapter ≈ MBs vs full model ≈ 100s of GB → thousands of adapters per base. Adapter swap is cheap vs full model load. Memory per GPU bounds resident adapters.

## Failure modes
Adapter cache thrash on cold tenants · cross-tenant data leak in training · a bad adapter shipped (no eval gate) · base-model version skew vs adapters · noisy neighbor.

## Top follow-ups
- "Serve many fine-tunes cheaply?" → one base + LoRA adapter multiplexing; hot resident, cold cached.
- "Per-customer isolation?" → data isolation in training, per-tenant quotas + ACL on adapters, residency.
- "LoRA vs full?" → LoRA for cost/density; full only when quality demands deep change.
- "Batching across adapters — how does that work?" → S-LoRA/punica-style: base-model matmuls batch normally; per-request adapter deltas applied via gathered/batched LoRA kernels — tenants share one forward pass. Without this, per-adapter batches fragment and utilization dies; it's the key serving trick, name it.
- "Base model upgrade with 5,000 live adapters?" → adapters are coupled to base weights: keep old base serving, auto-retrain/re-eval adapters against the new base (customer data permitting), migrate per-tenant on green evals, deprecate on a timeline — a fleet migration problem, not a flag flip.
- "Customer data quality is garbage — whose problem?" → the platform's: ingestion validation (format, dedup, contamination against their own eval split), auto-generated eval set from held-out data, and a 'your fine-tune did not beat the base model' report — refusing to ship a regression is a feature.
- "GDPR delete for a tenant?" → delete training data, adapters, *and* eval artifacts + any cached generations; adapters are derived data — provenance tracking makes the purge provable.

## Related
[[08-multi-model-inference-platform]] (serving) · [[13-distributed-training-70b]] (training infra) · [[D0-areas-map]] Area 4.
