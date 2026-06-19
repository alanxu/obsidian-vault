---
title: Design a Pretraining Data Pipeline
slug: pretraining-data-pipeline
area: 4 — Training & Fine-tuning
companies: [OpenAI, Cohere, Together, Anthropic]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[13-distributed-training-70b]]", "[[26-data-labeling-pipeline]]", "[[D0-areas-map]]"]
---

# Design a Pretraining Data Pipeline

> The data that determines model quality more than the architecture. Ingest web-scale raw text → clean → dedup → filter → tokenize → shard → stream to training so GPUs never wait. *Data quality > data quantity.*

## Problem
"Design the data pipeline that feeds large-model pretraining: from raw sources to tokenized, sharded, streamable training data." Variant: "how do you ensure data quality / avoid contamination?"

## Clarify first
- Sources (web crawl, code, books, licensed)? Scale (trillions of tokens)? Languages/modalities?
- Quality bar / dedup strictness? Eval-contamination concerns? Compliance/licensing?

## Architecture (offline batch)
Raw sources → **extract/parse** → **clean** (boilerplate, encoding) → **dedup** (exact + near-dup MinHash/LSH) → **quality filter** (classifier / heuristics / perplexity) → **decontaminate** (remove eval-set overlap) → **tokenize** → **shard + index** → stream/prefetch to training. Versioned, reproducible.

## Deep-dive — quality + dedup + contamination
- **Dedup** — exact (hashes) + **near-dup** (MinHash + LSH) across the whole corpus; duplicates waste compute and hurt generalization. Big distributed-systems problem (dedup at trillion-token scale).
- **Quality filtering** — train a classifier (good vs junk), or perplexity/heuristic filters; balance quality vs diversity (over-filtering loses coverage).
- **Decontamination** — remove documents overlapping your eval sets, or your benchmark numbers are inflated (a top silent failure).
- **Throughput** — tokenize + shard + prefetch so the data loader never starves the GPUs (the training bottleneck is sometimes data loading).
- **Provenance/licensing** — track source + license; ability to purge.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Filter strictness | quality vs diversity/coverage |
| Exact vs near dedup | cost vs thoroughness |
| Dedup scope | within-source vs global (expensive) |
| Streaming vs materialized | freshness/flexibility vs simplicity |

## Numbers
Trillion-token scale → distributed dedup (MinHash/LSH). Data quality > quantity. Decontamination is mandatory for trustworthy evals. Data-loader throughput must exceed GPU consumption.

## Failure modes
**Eval contamination** (inflated benchmarks) · duplicate-heavy data (wasted compute, memorization) · over-filtering (lost diversity) · silent data corruption/poisoning · data-loader bottleneck starving GPUs · licensing violations.

## Top follow-ups
- "Ensure quality?" → dedup (exact+near) + quality classifier + decontaminate; quality > quantity.
- "Avoid contamination?" → remove eval-set overlap before training; track provenance.
- "Don't starve the GPUs?" → tokenize/shard/prefetch pipeline; measure loader throughput vs consumption.

## Related
[[13-distributed-training-70b]] · [[26-data-labeling-pipeline]] (labeled/preference data) · [[D0-areas-map]] Areas 4 + 6.
