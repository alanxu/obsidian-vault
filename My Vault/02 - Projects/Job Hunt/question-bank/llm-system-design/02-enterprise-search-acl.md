---
title: Design Enterprise Search across SaaS apps (permission-aware)
slug: enterprise-search-acl
area: 1 — Retrieval & Knowledge
companies: [Glean]
difficulty: ★★★★☆
formats: [Live system design]
related: ["[[01-rag-with-citations]]", "[[D0-areas-map]]"]
---

# Design Enterprise Search across Slack / Drive / Jira / Salesforce

> The Glean prompt. The hard part isn't retrieval quality — it's **permission-aware** results across heterogeneous sources with different ACL models, kept fresh.

## Problem
Index data from many SaaS connectors; answer/search so results **respect each app's existing permissions**, stay fresh (<60s), and rank well across structured + unstructured data. Variant: "build the assistant on top."

## Clarify first
- How many connectors / data volume / QPS? Per-user or per-tenant permissions (both)?
- Freshness SLA? Real-time (Slack message) vs daily (wiki)?
- Search only, or RAG-assistant on top? Latency SLA?

## Architecture (3 planes)
- **Ingest/offline:** per-connector crawlers (full + incremental via webhooks/change-APIs) → normalize → **capture each doc's ACL** (users/groups) as indexed metadata → chunk → embed → **hybrid index (vector + BM25) + doc store**, all carrying ACL + source + timestamp.
- **Serving/online:** resolve the **user's group memberships** → build an **ACL filter predicate** → hybrid retrieve **with the ACL filter applied inside the query** → RRF → re-rank (personalized by role/recency/source) → (optional) RAG answer with citations.
- **Quality:** click/dwell signals → learned ranking; freshness + permission-correctness monitoring.

## Deep-dive — permission-aware retrieval (the whole question)
- **Enforce ACL inside the index query**, never as a post-filter (post-filtering leaks existence + breaks top-k). Store `allow_principals` per doc; filter to `user_groups ∩ allow_principals ≠ ∅`.
- **Permission freshness:** ACLs change (someone leaves a channel) — propagate revocations fast or you leak. Cache group membership with short TTL; re-check at query time.
- **Late-binding vs index-time ACL:** index-time is fast but stale on revocation; late-binding (check live) is correct but slower — hybrid: index coarse ACL, verify fine ACL at serve.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Index-time vs query-time ACL | speed/freshness vs correctness on revocation |
| Per-connector freshness | webhook complexity vs staleness |
| Unified vs per-source ranking | consistency vs source-specific signals |

## Eval
Permission-correctness (zero leaks — a hard gate), Recall@k per source, click-through / session success, freshness lag.

## Failure modes
ACL leak (the cardinal sin) · stale permissions after revocation · connector rate limits / outages → stale index · ranking dominated by one noisy source.

## Top follow-ups
- "Respect Slack + Salesforce ACLs simultaneously?" → normalize to a principal model; intersect at query.
- "Real-time freshness?" → webhooks/change-feeds + incremental upsert; tombstone on delete.
- "Someone loses access mid-session?" → short-TTL membership cache + query-time re-check.
- "Group expansion is expensive — a user in 500 nested groups?" → precompute flattened membership offline (transitive closure), cache per-user principal set with TTL + event-driven invalidation on group change; query filter is then one set-intersection, not a graph walk.
- "How do you *test* zero-leak?" → adversarial eval set: (user, doc-they-must-NOT-see) pairs per connector; run on every index/ranking change as a hard CI gate — treat like a security regression suite, not a quality metric.
- "RAG answer synthesized from 5 docs — what ACL does the answer have?" → intersection: every source doc must be visible to the requester *at generation time*; cache answers keyed by principal-set, never share across users with different access.

## Numbers
Connector fan-out: 10–100+ SaaS apps · ACL metadata often 10–30% of index size · membership cache TTL 1–5 min (leak window vs lookup cost) · webhook lag: Slack seconds, Drive minutes, some connectors poll-only (hours) — state per-connector freshness SLAs, not one number.

## Related
[[01-rag-with-citations]] (retrieval core) · [[D0-areas-map]] Area 1 + §3 (ACL cross-cutting).
