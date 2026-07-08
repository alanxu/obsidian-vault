---
title: Design a CTR / Ad Click-Through-Rate Prediction System
slug: ctr-ad-prediction
area: 6 — Data, Features, Embeddings
companies: [Google, Meta, big-tech, Index Exchange]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[24-recommendation-ranking-system]]", "[[21-feature-store-realtime-serving]]", "[[D0-areas-map]]"]
---

# Design a CTR / Ad Click-Through-Rate Prediction System

> Predict P(click) for ads under huge scale, tight latency, and **calibration** requirements (the probability feeds the auction/bidding, so it must be *accurate*, not just well-ranked).

## Problem
"Design click-through-rate prediction for Google/Meta Ads." Score candidate ads for a user/context; the prediction drives ranking × bid in the auction.

## Clarify first
- Auction mechanics (does calibrated probability matter? — yes)? Latency (ms)? Scale (billions of events/day)?
- Features (user, ad, context, cross)? Freshness? Privacy constraints?

## Architecture
Request → candidate ads → **CTR model** (over user×ad×context features) → **pCTR** → **auction** (pCTR × bid) → serve → log impression+click → **online/continual training**. Feature store ([[21-feature-store-realtime-serving]]).

## Deep-dive — calibration, scale, sparsity
- **Calibration:** pCTR feeds the auction → it must be **well-calibrated** (predicted 2% ≈ actual 2%), not just well-ranked → calibration layer (Platt/isotonic), monitor calibration drift. This is the CTR-specific staff point.
- **Feature sparsity / high cardinality:** billions of IDs (user, ad) → **embeddings** for categoricals + cross features; hashing tricks; huge embedding tables (sharded parameter server).
- **Scale + freshness:** billions of events/day → online/continual learning to track drift; recent data matters most.
- **Class imbalance:** clicks are rare (~1%) → handle imbalance (weighting), use PR-AUC/log-loss not accuracy.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Calibration method | accuracy of probability vs complexity |
| Embedding dim / table size | quality vs memory/latency |
| Online vs batch training | freshness/drift vs stability |
| Model complexity | ceiling vs latency/cost at billions QPS |

## Numbers
Clicks ~1% (imbalanced) → log-loss/PR-AUC, not accuracy. Calibration matters because pCTR × bid sets the auction. Embedding tables can be TBs → sharded.

## Failure modes
Miscalibration (breaks the auction economics) · feedback loop (shown ads get clicks) · stale model (drift) · embedding-table memory blowup · position bias (top slots get clicks regardless).

## Top follow-ups
- "Why calibration?" → pCTR feeds the auction; ranking-only isn't enough; add a calibration layer + monitor.
- "Billions of sparse IDs?" → embeddings + hashing + sharded param server.
- "Drift?" → online/continual training on recent data; monitor calibration + log-loss.
- "Position bias?" → model position as a feature / debias.
- "How do you *measure* calibration?" → reliability diagram + expected calibration error, sliced by segment (new ads, small advertisers) — global calibration with per-slice miscalibration still misprices the tail; recalibrate per-slice or add slice features.
- "Delayed clicks (conversion arrives hours later)?" → naive online training labels recent impressions negative-then-flips → delayed-feedback modeling (importance weighting, fake-negative correction) — the CTR-specific version of fraud's label-latency problem.
- "Exploration in ads?" → new ads have no history and the feedback loop starves them → explicit exploration budget (ε or Thompson on pCTR uncertainty) priced against short-term revenue loss; without it the marketplace ossifies.

## Related
[[24-recommendation-ranking-system]] · [[21-feature-store-realtime-serving]] · [[D0-areas-map]] Area 6.
