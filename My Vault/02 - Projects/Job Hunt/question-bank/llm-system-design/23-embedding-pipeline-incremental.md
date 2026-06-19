---
title: Design an Embedding Pipeline at Scale (100M+ docs, incremental)
slug: embedding-pipeline-incremental
area: 6 — Data, Features, Embeddings
companies: [Cohere, Glean, vector-DB cos]
difficulty: ★★★☆☆
formats: [Live system design, Take-home]
related: ["[[01-rag-with-citations]]", "[[05-semantic-hybrid-search]]", "[[D0-areas-map]]"]
---

# Design an Embedding Pipeline at Scale (incremental updates)

> The Cohere/Glean prompt: embed 100M+ docs and keep the index fresh on create/update/delete. **The staff insight: re-embedding on a model change is a *migration*, not an update — never mix embedding versions in one index.**

## Problem
"Design an embedding pipeline that handles 100M documents with daily incremental updates." Sub-problems: batch embed at scale, incremental upsert, deletes, re-embedding migrations.

## Clarify first
- Corpus size + update rate (creates/updates/deletes per day)? Freshness SLA?
- Embedding model stability (how often does it change)? Latency for queries?

## Architecture
**Initial backfill:** batch embed (GPU fleet, batched inference) → build vector index (HNSW/IVF-PQ) + lexical + doc store. **Incremental:** change-feed (create/update/delete) → re-chunk → re-embed changed docs → **upsert** vector + lexical; **tombstone** deletes. **Migration path:** new model → rebuild index offline → dual-write → cut over.

## Deep-dive — incremental upsert + re-embedding migration
- **Incremental upsert:** on doc change, re-chunk + re-embed only the changed doc, upsert by stable chunk IDs; **tombstone** on delete (and garbage-collect). Dedup near-identical content.
- **Re-embedding migration:** a new embedding model means **every vector is incomparable to old ones** → rebuild the whole index offline, **dual-write** old+new during transition, then cut over reads. Never serve mixed versions (garbage similarity).
- **Throughput:** batched GPU inference; backpressure; checkpoint the backfill (100M docs takes a while).
- **Versioning:** tag the index with the embedding model+version.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Full re-embed vs incremental | correctness on model change (full) vs cost/freshness |
| HNSW vs IVF-PQ | recall+latency vs memory at 100M+ |
| Re-chunk granularity | precision vs re-embed cost on update |
| Dual-write window | safety vs double storage/cost |

## Numbers
100M docs × ~8 chunks ≈ 800M vectors → quantize + shard. Re-embedding = offline rebuild + dual-write + cutover. Tag every index with its embedding version.

## Failure modes
**Mixed embedding versions in one index** (garbage similarity) · stale index on missed updates · orphaned vectors after delete (no tombstone/GC) · backfill OOM/timeout (no checkpointing) · throughput bottleneck.

## Top follow-ups
- "Model upgrade?" → offline rebuild + dual-write + cut over; never mix versions.
- "Daily updates?" → change-feed → re-embed changed docs → upsert; tombstone deletes.
- "100M docs?" → batched GPU embed, quantize, shard, checkpoint the backfill.

## Related
[[01-rag-with-citations]] (consumer) · [[05-semantic-hybrid-search]] · [[D0-areas-map]] Area 6.
