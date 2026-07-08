---
title: Design a Real-Time Fraud Detection System
slug: realtime-fraud-detection
area: 6 — Data, Features, Embeddings
companies: [Robinhood, Stripe, Wealthsimple, OpenAI (payments)]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[21-feature-store-realtime-serving]]", "[[D0-areas-map]]"]
---

# Design a Real-Time Fraud Detection System

> Score transactions for fraud **in-line under tight latency**, with a feedback loop on late-arriving labels. **The staff move: the precision/recall threshold is a *business* decision** (cost of a false decline vs a missed fraud), not an F1 optimization.

## Problem
"Design fraud detection for payments/transactions." LLM variant (OpenAI): "use an LLM to detect fraud." Sub-problems: streaming features, low-latency scoring, label latency, concept drift, threshold.

## Clarify first
- Latency budget (block before authorizing → ms)? Volume/QPS? Cost of false positive (declined good customer) vs false negative (fraud)?
- Label availability/latency (chargebacks arrive weeks later)? Adversarial (fraudsters adapt)?

## Architecture
Transaction → **streaming feature computation** (velocity, device, graph features) from a feature store ([[21-feature-store-realtime-serving]]) → **model scores in-line** → **threshold/policy** → approve / decline / step-up (2FA) / review queue → **feedback loop** (labels arrive late → retrain). Rules + ML hybrid.

## Deep-dive — latency, labels, drift, threshold
- **In-line scoring:** features + model must return within the auth budget (ms) → precomputed/streaming features + a fast model; LLM only if latency allows (or async for review).
- **Label latency:** ground truth (chargeback) arrives weeks later → train on delayed labels; use weak signals (user reports) meanwhile; careful with the feedback loop (blocked frauds never get labeled → bias).
- **Concept drift:** fraudsters adapt → monitor score distribution, retrain frequently, champion/challenger models.
- **Threshold = business:** set the operating point from **cost of FP vs FN**, not F1; different thresholds per segment; step-up auth as a middle option.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Precision vs recall threshold | false declines (revenue/UX) vs missed fraud (loss) |
| Rules vs ML vs hybrid | interpretability/speed vs adaptivity |
| Block vs step-up vs review | friction vs safety |
| Sync ML vs async LLM | latency vs richer signal |

## Numbers
Auth latency budget = milliseconds → streaming features + fast model. Asymmetric costs drive the threshold. Drift → frequent retrain. Label latency → delayed feedback loop.

## Failure modes
Latency blowing the auth budget · feedback-loop bias (blocked frauds never labeled) · concept drift (model goes stale) · too many false declines (revenue/UX) · adversarial evasion · train/serve skew on features.

## Top follow-ups
- "Real-time latency?" → streaming features + in-line fast model; LLM async for review queue.
- "Labels are delayed?" → train on delayed + weak labels; manage feedback-loop bias.
- "Set the threshold?" → cost of FP vs FN (business), per-segment, with step-up auth.
- "Fraudsters adapt?" → drift monitoring + frequent retrain + champion/challenger.
- "Graph features — why and how fast?" → fraud rings share devices/cards/addresses; degree/community features are top predictors but expensive → precompute graph aggregates near-real-time (streaming upserts to the feature store), full graph algorithms offline nightly; know which features tolerate staleness.
- "Extreme class imbalance (1:10³–10⁴)?" → PR-AUC not ROC-AUC (ROC flatters at imbalance), score calibration so thresholds mean something, downsample negatives at train + reweight — and per-segment metrics, because aggregate hides that new-account fraud recall is terrible.
- "Model explains a decline?" → regulatory + support reality: reason codes from the model (top features/SHAP-lite) logged per decision; a pure black box fails compliance review in fintech — say this before being asked at Robinhood/Stripe.
- "Cold start on a new fraud pattern?" → rules bridge the gap (analyst writes a rule today, model learns it in weeks), which is *the* argument for the hybrid rules+ML architecture — rules are the fast path for adversarial novelty.

## Related
[[21-feature-store-realtime-serving]] · [[D0-areas-map]] Area 6.
