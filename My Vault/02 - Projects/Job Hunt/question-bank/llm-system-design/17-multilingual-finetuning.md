---
title: Design a Multilingual Fine-Tuning Pipeline (50+ languages)
slug: multilingual-finetuning
area: 4 — Training & Fine-tuning
companies: [Cohere]
difficulty: ★★★☆☆
formats: [Live system design, Take-home]
related: ["[[14-rlhf-pipeline]]", "[[16-pretraining-data-pipeline]]", "[[18-llm-eval-harness]]"]
---

# Design a Multilingual Fine-Tuning Pipeline

> The Cohere prompt: fine-tune for 50+ languages with **uneven data distribution** (English-heavy, many low-resource tongues). The core problem is **data balance + per-language eval**, not the training mechanics.

## Problem
"How would you approach multilingual model fine-tuning for 50+ languages with uneven data distribution?" Sub-problems: data balancing, tokenization fairness, per-language eval, avoiding high-resource dominance.

## Clarify first
- Which languages + how skewed is the data? Quality bar per language?
- Shared model vs per-language adapters? Eval data availability per language?

## Architecture
Per-language data ingestion ([[16-pretraining-data-pipeline]]) → **balanced sampling** (up-sample low-resource, temperature sampling) → fine-tune (shared model, optionally + per-language LoRA) → **per-language eval gate** → serve.

## Deep-dive — data balance + fairness + eval
- **Data imbalance:** naive training lets high-resource languages dominate → **temperature/​up-sampling** of low-resource languages to balance, without overfitting their small sets.
- **Tokenization fairness:** a tokenizer trained mostly on English uses far more tokens per word in other scripts → higher cost + worse quality; consider a balanced multilingual tokenizer.
- **Per-language eval:** a single aggregate metric hides per-language regressions → **eval each language separately**, gate on the worst performers, watch for cross-lingual interference (improving one hurts another).
- **Cross-lingual transfer:** related languages help each other; exploit it for low-resource ones.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Up-sample low-resource | fairness/coverage vs overfitting small sets |
| Shared model vs per-lang adapter | transfer/simplicity vs per-language control |
| Single tokenizer | simplicity vs per-script fairness/cost |
| Aggregate vs per-lang eval | one number vs catching regressions |

## Numbers
Tokenizer can use 2–4× more tokens for non-Latin scripts (cost + context). Per-language eval is mandatory; aggregate hides failures.

## Failure modes
High-resource languages dominating · low-resource overfitting · tokenizer unfairness (cost/quality) · cross-lingual interference · aggregate metric hiding a tanked language.

## Top follow-ups
- "Uneven data?" → temperature/up-sampling to balance; exploit cross-lingual transfer.
- "Know it works for all 50?" → per-language eval gates, not an aggregate.
- "Tokenizer?" → balanced multilingual tokenizer; watch token-inflation cost for non-English.

## Related
[[16-pretraining-data-pipeline]] · [[18-llm-eval-harness]] (per-language eval) · [[D0-areas-map]] Area 4.
