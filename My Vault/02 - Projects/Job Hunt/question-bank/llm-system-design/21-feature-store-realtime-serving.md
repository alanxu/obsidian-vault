---
title: Design a Feature Store + Real-Time ML Serving
slug: feature-store-realtime-serving
area: 6 — Data, Features, Embeddings
companies: [Robinhood, Wealthsimple, Stripe-style, big-tech]
difficulty: ★★★★☆
formats: [Live system design]
related: ["[[22-realtime-fraud-detection]]", "[[24-recommendation-ranking-system]]", "[[D0-areas-map]]"]
---

# Design a Feature Store + Real-Time ML Serving

> **The thesis:** *the #1 silent ML bug is **training/serving skew** — features computed offline for training differ from those computed online for serving.* A feature store's whole point is one definition serving both. Your data-infra strength shines.

## Problem
"Design the feature platform that computes/stores/serves features for training and low-latency inference, with parity." Used by fraud ([[22-realtime-fraud-detection]]), recsys ([[24-recommendation-ranking-system]]).

## Clarify first
- Feature types (streaming aggregates vs batch)? Serving latency SLA? Freshness per feature?
- Scale (#features, QPS)? Point-in-time training-data needs?

## Architecture (two stores, one definition)
**Feature definitions** (shared transform code) → **offline store** (columnar/warehouse, for training, **point-in-time joins**) + **online store** (low-latency KV, for serving). Streaming pipeline (Flink/Kafka) for real-time aggregates; batch pipeline for daily. Serving reads online store at inference.

## Deep-dive — parity + point-in-time correctness
- **Online/offline parity:** the *same* transformation produces training and serving features — share definitions/code, never re-implement. Skew here corrupts the model invisibly.
- **Point-in-time correctness:** when building training data, each label joins only to feature values **as of that timestamp** — no future leakage. Leakage inflates offline metrics and tanks prod.
- **Freshness per feature:** streaming (last-N-seconds aggregates) vs batch (daily) — choose **per feature** from its freshness need, not uniformly.
- **Online store:** in-memory KV (Redis-style) for sub-ms reads; precompute vs on-demand.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Streaming vs batch features | freshness vs simplicity/cost |
| Precompute vs on-demand | serving latency vs storage/staleness |
| Online store tech | latency vs cost/scale |
| Parity mechanism | shared-code complexity vs skew risk |

## Numbers
Point-in-time joins are *the* training-data correctness lever. Online reads must hit the serving SLA (often <10ms). Parity is the headline failure to prevent.

## Failure modes
**Train/serve skew** (the headline) · label leakage / no point-in-time → great offline, awful online · stale online features · slow online store blowing the SLA · feature pipeline lag.

## Top follow-ups
- "Avoid train/serve skew?" → single feature definition serving both stores; share transform code.
- "Point-in-time correctness?" → as-of joins; never join future feature values to past labels.
- "Freshness?" → streaming vs batch *per feature*, from the requirement.

## Related
[[22-realtime-fraud-detection]] · [[24-recommendation-ranking-system]] · [[D0-areas-map]] Area 6.
