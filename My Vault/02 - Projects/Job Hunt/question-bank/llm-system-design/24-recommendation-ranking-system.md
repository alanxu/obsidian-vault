---
title: Design a Recommendation / Feed Ranking System
slug: recommendation-ranking-system
area: 6 — Data, Features, Embeddings
companies: [Lyft, Pinterest, big-tech (YouTube/Netflix/Meta)]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[05-semantic-hybrid-search]]", "[[25-ctr-ad-prediction]]", "[[21-feature-store-realtime-serving]]"]
---

# Design a Recommendation / Feed Ranking System

> The classic ML system design (YouTube recs, Netflix Top Picks, IG Explore, FB feed). **The canonical architecture is retrieve-then-rank** (candidate generation → ranking) — say that first.

## Problem
"Design YouTube's recommendations / a news feed ranking system." Predict which items a user will engage with; serve a ranked list at low latency and huge scale.

## Clarify first
- Objective (clicks, watch time, long-term retention)? Catalog + user scale? Latency SLA?
- Cold start (new users/items)? Freshness (real-time vs batch)? Diversity/fairness constraints?

## Architecture (multi-stage funnel)
**Candidate generation** (retrieve hundreds from millions: two-tower embeddings + co-occurrence + recency) → **ranking** (heavy model over rich features: user×item×context) → **re-ranking** (diversity, business rules, freshness) → serve. Feature store ([[21-feature-store-realtime-serving]]) + logging → training.

## Deep-dive — the stages + objective
- **Candidate generation (recall):** cheap, high-recall — **two-tower** (user tower, item tower) for ANN retrieval + heuristic sources (trending, followed). Reduce millions → hundreds.
- **Ranking (precision):** a deep model (e.g. DLRM / wide-and-deep / transformer) scoring engagement probability over many features; this is where most quality comes from.
- **Objective design:** pick the metric carefully — optimizing raw clicks → clickbait; optimize a blend (watch time, satisfaction, long-term retention); multi-task heads.
- **Re-ranking:** diversity (MMR), freshness, business rules, fairness; avoid filter bubbles.
- **Cold start:** content features for new items; popularity/exploration for new users.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Objective (clicks vs watch vs retention) | easy-to-measure vs true value (clickbait risk) |
| Two-tower vs cross-features in retrieval | speed/ANN vs accuracy |
| Real-time vs batch features | freshness vs cost |
| Exploration vs exploitation | discovery/cold-start vs short-term engagement |

## Numbers
Millions of items → can't score all → retrieve-then-rank funnel. Offline nDCG/MRR/AUC; online CTR/watch-time/retention. A/B every change. Feedback loops (popularity) need exploration.

## Failure modes
Optimizing a proxy (clickbait) · feedback loop / filter bubble · cold start · stale features (train/serve skew) · popularity bias · latency at scale.

## Top follow-ups
- "Architecture?" → retrieve-then-rank: candidate generation (two-tower) → ranking → re-rank.
- "What objective?" → blend engagement + satisfaction + retention; beware clickbait from raw clicks.
- "Cold start?" → content features + exploration.
- "Real-time?" → streaming features + online ranking; A/B everything.

## Related
[[05-semantic-hybrid-search]] · [[25-ctr-ad-prediction]] · [[21-feature-store-realtime-serving]] · [[D0-areas-map]] Area 6.
