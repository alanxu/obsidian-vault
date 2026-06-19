---
title: Design a Distributed Training Pipeline for a 70B Model
slug: distributed-training-70b
area: 4 — Training & Fine-tuning
companies: [OpenAI, NVIDIA, Cohere, Together, Google, Anthropic]
difficulty: ★★★★★
formats: [Live system design, ML-depth round]
related: ["[[16-pretraining-data-pipeline]]", "[[14-rlhf-pipeline]]", "[[D0-areas-map]]"]
---

# Design a Distributed Training Pipeline for a 70B Model

> Your **infra flex**. Open with the mental model: *training a large model is a tightly-coupled distributed system where the bottleneck is usually communication, not compute, and one GPU failure among thousands stalls everyone.* The game: **fit the model+optimizer+activations in memory** and **keep GPUs busy** despite comms and failures.

## Problem
"Design the system to train a 70B model across thousands of GPUs — handle memory, parallelism, checkpointing, fault tolerance, communication overhead." Variant: "it won't fit on a GPU — what now?"

## Clarify first
- Model size + token budget? GPU count/type + interconnect (NVLink/InfiniBand)?
- Pretrain vs fine-tune? Time/cost budget? Failure-rate expectations?

## Architecture
**Data pipeline** ([[16-pretraining-data-pipeline]]) → **3D-parallel training** (DP × TP × PP) on a GPU cluster with **ZeRO/FSDP** sharding + **distributed checkpointing** to object store + **monitoring** (loss, throughput, hardware) + auto-restart.

## Deep-dive — memory + parallelism + fault tolerance
- **Memory math:** training ≈ **16–20 bytes/param** (fp16 weight 2 + grad 2 + Adam 8 + activations) → 70B ≈ 1.2–1.5 TB *just for state* → **must shard**.
- **ZeRO/FSDP** — shard optimizer states, grads, params across data-parallel ranks (vs replicate) → trains far bigger models on the same HW. + bf16 mixed precision + **gradient checkpointing** (recompute activations).
- **Parallelism mix (by bottleneck):** **TP** (split matmuls, high comms → keep intra-node/NVLink) · **PP** (split layers into stages, micro-batches to fill the bubble) · **DP** (replicate, split batch, all-reduce) · **3D** = compose all three.
- **Fault tolerance (your differentiator):** at 1000s of GPUs, hardware *will* fail → async distributed checkpointing (frequent enough to bound lost work, not so frequent it stalls), auto detect-and-restart, **elastic training**.
- **Comms:** all-reduce often dominates → overlap comms with compute.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| TP vs PP vs DP mix | comms pattern vs memory vs pipeline bubble |
| Checkpoint frequency | lost-work-on-failure vs I/O stall |
| Sync vs async | convergence stability vs straggler tolerance |
| bf16 / fp8 | throughput/memory vs numerical stability |

## Numbers
70B ≈ 1.2–1.5 TB state → shard across many 80GB GPUs. MTBF shrinks with GPU count → checkpoint cadence accordingly. Comms can dominate → overlap.

## Failure modes
Stragglers stalling sync all-reduce · node failure losing hours (→ checkpoint cadence) · activation-memory OOM · loss divergence (→ grad clip, LR schedule, rollback) · data-loader starving GPUs.

## Top follow-ups
- "Won't fit?" → FSDP/ZeRO + 3D parallelism + grad checkpointing + bf16; show the memory math.
- "1000 GPUs, one dies?" → distributed checkpointing + auto-restart + elastic; bound lost work.
- "Bottleneck?" → identify memory vs comms vs bubble vs data-loading; pick the parallelism mix accordingly.
- "MoE?" → expert parallelism; more capacity/FLOP but routing/load-balance complexity.

## Related
[[16-pretraining-data-pipeline]] · [[14-rlhf-pipeline]] · [[D0-areas-map]] Area 4.
