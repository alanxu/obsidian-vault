---
title: "Search Engine (Full-Text)"
slug: search-engine-fulltext
type: distributed-system-design
tier: "1 — Core data stores & consistency"
companies: [Google, Elastic, Algolia, Bing, Elasticsearch, Solr, OpenSearch, Cohere]
difficulty: ★★★★☆
frequency: medium
formats: [Onsite·SD, Mock]
time-box: 35–45 min
tags: [search, inverted-index, ranking, tf-idf, bm25, elasticsearch, lucene]
related: ["[[29-typeahead-autocomplete]]", "[[19-event-streaming-kafka]]", "[[34-recommendation-system]]"]
companies-likely: [Google, Elastic, Algolia, Bing, OpenSearch, Cohere, Glean]
star: true
---

# Search Engine (Full-Text)

**One-liner:** A system that indexes billions of documents and returns ranked results for free-text queries in < 100ms, with relevance + freshness + recall + precision balanced.

## Problem framing

Asked when the interviewer cares about ranking, indexing pipelines, or large-scale text retrieval. Variants: web search (Google), enterprise search (Glean / Elastic), app-internal search (Algolia / Coveo), e-commerce search (Amazon / Shopify).

**Variants:**
- "Design Google Search" (web-scale, ranking-heavy)
- "Design Elasticsearch" (inverted index + sharding)
- "Design Algolia" (real-time, faceted, low-latency)
- "Design a code search like Sourcegraph" (specialized corpus)

## Requirements (clarify first)

- **Functional:** index(doc), search(query, filters, sort) → ranked list; auto-complete; faceting; highlighting.
- **Non-functional:**
  - Query latency: p99 < 100ms (Algolia) / < 500ms (Elastic)
  - Index freshness: real-time (Algolia) / minutes (web search)
  - Recall + precision: tunable per use case
- **Constraints:** corpus size (10M docs / 1B / 100B pages), query QPS (1k / 100k / 100M/day).
- **Out of scope:** ads / ranking-by-revenue (mention as variant), personalization.

## Capacity estimation

- 1B docs × 10KB = 10TB raw; inverted index ~30-50% of raw = 3-5TB.
- 100k QPS, average query touches 1M docs → 100B doc-reads/s. Distributed across 1000 shards → 100M reads/s/shard. Lucene handles ~10k QPS/shard on SSD.
- Indexing: 1M new docs/day = ~12/sec. Easy.

## High-level architecture

```
Crawler ──► Document pipeline ──► Indexer (build inverted index)
                                       │
                                       ▼
                                Segment files (Lucene)
                                       │
                                       ▼
                                Distributed shard (Elasticsearch node)
                                       
Query → Frontend (parse, rewrite, plan) → parallel scatter-gather across shards
      → merge + rerank → return top-K
```

## API / interfaces

```
POST /v1/index
{ "id": "...", "fields": {...}, "text": "..." }
→ { "shard": "s-42", "doc_id": "..." }

POST /v1/search
{ "q": "machine learning", "filters": {...}, "limit": 10 }
→ { "hits": [...], "total": 12345, "took_ms": 42 }
```

## Deep dive #1 — Inverted index & ranking

**Inverted index** is the core data structure:
```
"machine"   → [(doc1, tf=2, pos=[3,17]), (doc2, tf=1, pos=[42]), ...]
"learning"  → [(doc1, tf=1, pos=[5]),  (doc3, tf=3, pos=[1,7,22]), ...]
```

For each term: posting list = docs containing it, with term frequency (tf), positions (for phrase queries), and optionally field-level boosts.

**Storage:** posting lists are sorted by doc ID, compressed with PFOR-DELTA or Roaring Bitmaps. Term dictionary is a finite-state transducer (FST) for O(term_length) lookup. The whole index is memory-mapped.

**Ranking functions:**
- **TF-IDF:** classic. tf × log(N/df). Simple, well-understood.
- **BM25:** TF-IDF done right. Handles tf saturation, document length normalization. Default in Lucene/Elastic.
- **Vector-space (cosine):** TF-IDF as vectors, cosine similarity. Baseline for ranking.
- **Learning-to-rank (LambdaMART, etc.):** train on click logs. LambdaMART is the standard pairwise/lambdarank model. Used by all modern search engines as a re-ranker.

**Free-text query pipeline:**
1. **Parse** the query: tokenize, normalize (lowercase, stem), handle synonyms.
2. **Rewrite:** expand abbreviations, apply synonyms, spell-correct.
3. **Retrieve:** BM25 over inverted index → top-1000 candidates.
4. **Re-rank:** learning-to-rank model on candidates → top-10.
5. **Snippet / highlight:** match positions from posting list.

## Deep dive #2 — Distributed indexing & sharding

**Two-stage indexing:**
1. **Map stage:** each indexer processes a batch of docs → produces a *segment* (immutable Lucene index).
2. **Reduce / merge stage:** merge segments periodically. Compaction drops deleted docs.

**Near-real-time (NRT):** Lucene's `getReader()` refresh every 1s — new docs visible within 1s of being written. Refresh = reopen segment.

**Distributed shards:**
- Documents routed to a shard by `hash(doc_id) % N`.
- Each shard is N replicas (1 primary + N-1 replicas) on different nodes.
- Search parallel across all shards; coordinator merges.

**Scaling shards:**
- **Re-sharding** is expensive: rebuild the whole index. **Elasticsearch's ILM** does time-based indices (index per day/week) so old data can be force-merged then frozen, new data goes to fresh shards.
- **Tiered storage:** hot indices on SSD, frozen on S3 + searchable snapshots.

**Replicas serve reads.** 1 primary + 2 replicas = 3× storage, but each replica can serve reads → 3× read throughput.

## Scale & bottlenecks

- **Deep pagination:** `offset=1000000` is brutal. Use search-after / scroll / cursor-based pagination.
- **Index bloat:** never-deleted docs + frequent updates → many small segments → slow search. Force-merge to compact.
- **Heap pressure:** Lucene keeps fielddata (sorted strings) in JVM heap. Doc values on disk avoid this — always use doc_values for large string fields.
- **Phrase queries:** position lookups are slow on long fields. Set `position_increment_gap`; don't index long bodies with `analyzed`.
- **Multi-tenant:** a fat query from one tenant can starve others. Per-shard query budgets.

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Shard down | Some docs missing | Replica serves; rebuild replica from primary |
| Index corrupt | Search fails on shard | Restore snapshot; rebuild from source |
| Reindex storm | Cluster overloaded | Throttle indexing rate; off-peak batch |
| Query latency spike | GC pause / heap | Tune heap, use doc_values, profile |
| Disk full | Writes fail | ILM deletes / archives cold indices |

## "What I'd build first and why"

**Lucene-style inverted index** in memory-mapped segment files, **BM25 ranking**, **shard by doc_id hash**, **refresh every 1s for NRT**, **learning-to-rank re-ranker in v2 once you have click data**.

The single highest-leverage thing is **choosing the right ranking function for v1** — BM25 is the safe default; don't try to build a neural ranker until you have data.

## Follow-ups (real, reported)

1. **BM25 vs TF-IDF** — explain the saturation curve.
2. **Phrase queries** — position index in posting lists; how slop works.
3. **Multi-language / CJK** — tokenization, ICU analysis.
4. **Synonyms + query rewriting** — synonym graph at index or query time.
5. **Faceting / aggregations** — doc_values + inverted; filter cache.
6. **Vector search (semantic)** — kNN over embeddings, ANN indexes (HNSW). Hybrid with BM25.
7. **Learning-to-rank** — LambdaMART, click logs, train/serve separation.
8. **Indexing pipeline at scale** — Kafka → indexer nodes → segments.
9. **Near-real-time** — refresh interval vs throughput tradeoff.
10. **Site-search vs enterprise vs web** — different scale, different freshness.

## Tips (staff-level)

- **Name BM25 explicitly.** "I'll use BM25 for v1 ranking" is a green flag.
- **Sketch the inverted index.** `term → postings`. Most candidates do.
- **Quantify:** "1B docs × 10KB = 10TB, index 3-5TB, 100 shards × 50GB, fits on commodity boxes".
- **Talk about ranking.** Recall is the easy part; precision is the hard part.
- **Say "no neural ranker in v1".** Build it when you have click logs.

## Pitfalls

- **Only explaining the inverted index.** Ranking is the hard part.
- **"We'll use machine learning for ranking"** as a hand-wave. Get specific: BM25 → LambdaMART → neural.
- **Ignoring NRT.** Many use cases need fresh docs in < 5s.
- **Big heap + GC pauses.** Use doc_values; profile GC.
- **Treating all docs equally.** Boost recency, authority, freshness per use case.

## Worked narration (3 min)

"Goal: 1B docs, 10KB each, 100k QPS, p99 < 200ms, sub-second freshness.

**Storage:** inverted index in Lucene segment files, mmap'd, sharded by `hash(doc_id) % N`. Each shard is a primary + 2 replicas.

**Indexing:** Kafka → indexer nodes → segments. Refresh every 1s for NRT. Background compaction merges small segments.

**Retrieval:** BM25 over inverted index → top-1000 candidates per shard in parallel → coordinator merges with BM25 scores → learning-to-rank (LambdaMART) re-ranks → top-10.

**Phrase + filter:** position postings for phrases; doc_values for filters / sort; FST for term dictionary lookups.

**Failure:** shard dies → replica serves. Reindex storm → throttle. Latency spike → profile, force-merge, doc_values.

**First build:** Lucene + BM25 + sharded + 1s refresh. Add LambdaMART when we have click data; add vector search when we need semantic queries."

## Related

- [[29-typeahead-autocomplete]] — same inverted-index primitive, different query shape.
- [[19-event-streaming-kafka]] — Kafka is the typical indexing pipeline.
- [[34-recommendation-system]] — same retrieval + ranking pattern; vectors more central.