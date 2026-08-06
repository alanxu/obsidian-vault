---
title: RAG Infrastructure — Foundational Design
slug: rag-infrastructure
project: openmate
audience: Tech Lead / Architect
status: draft
version: 0.2
date: 2026-08-06
author: Mavis (mavis)
related:
  - "[[agentic-web-ui|Agentic Web UI Design]]"
  - "[[../../../03 - Areas/Agentic AI/topics/skills-tools-mcp-cli|Skills, Tools, MCPs, CLIs]]"
  - "[[../../../03 - Areas/Agentic AI/topics/aws-agent-infra|AWS Agent Infrastructure]]"
---

# RAG Infrastructure — Foundational Design

> **TL;DR for the architect:** build a **9-layer RAG platform** on top of Bedrock Knowledge Bases, with a **knowledge-type-aware strategy layer** (code / docs / chat / FAQ / structured each get their own extraction + chunking + embedding + retrieval), **event-driven ingestion with SLAs** (gold = minutes, silver = hourly, bronze = daily), **tiered storage** (hot / warm / cold), and a **single high-level "knowledge API"** that hides all the Bedrock / vector store / embedding complexity from app developers. The corporate platform owns the platform; teams own their knowledge sources.

---

## 1. The problem this solves

Today, every team that wants RAG in openmate faces the same friction:

1. Pick a vector store (OpenSearch? S3 Vectors? Pinecone? pgvector?)
2. Pick a chunking strategy (default? hierarchical? semantic? custom?)
3. Pick an embedding model (Titan? Cohere? OpenAI? Bedrock default?)
4. Wire up an ingestion pipeline (S3 events? Lambda? Step Functions? EventBridge?)
5. Decide on retrieval (semantic only? hybrid? rerank?)
6. Set up the KB in Bedrock console
7. Wire their app to the right KB ID
8. Repeat for every new data source
9. Monitor ingestion, cost, recall, latency — forever

This is **6+ weeks of plumbing per team**, and it gets re-done for every data source. The result: KB sprawl, inconsistent retrieval quality, no cost attribution, no eval, no governance.

**The platform's job:** turn that 6-week onboarding into a **5-minute self-service flow** for the common cases, with the right defaults already chosen, and an escape hatch for advanced cases.

---

## 2. The 9-layer architecture

```
┌──────────────────────────────────────────────────────────────────────┐
│  Layer 9: Developer API + UI      "search my knowledge" / "add kb"  │
├──────────────────────────────────────────────────────────────────────┤
│  Layer 8: Multi-tenancy + Governance   org / project / user isolation│
├──────────────────────────────────────────────────────────────────────┤
│  Layer 7: Observability + Cost Attribution   per-KB metrics, eval   │
├──────────────────────────────────────────────────────────────────────┤
│  Layer 6: Retrieval Layer           hybrid + rerank + multi-KB route│
├──────────────────────────────────────────────────────────────────────┤
│  Layer 5: Storage Tiers             hot (OpenSearch) / cold (S3 V)  │
├──────────────────────────────────────────────────────────────────────┤
│  Layer 4: Ingestion Pipeline        events → Step Functions → KB     │
├──────────────────────────────────────────────────────────────────────┤
│  Layer 3: Strategy Registry         chunking/embed/retrieval per type│
├──────────────────────────────────────────────────────────────────────┤
│  Layer 2: Knowledge Source Onboarding  connectors, pre-flight, test  │
├──────────────────────────────────────────────────────────────────────┤
│  Layer 1: Bedrock Knowledge Bases + Vector Stores   the foundation  │
└──────────────────────────────────────────────────────────────────────┘
```

App developers only see Layer 9. Everything below is the platform team's concern.

---

## 3. Layer 1 — Bedrock Knowledge Bases (the foundation)

The base layer is AWS-managed. We don't reinvent the wheel; we orchestrate it.

**For each knowledge source, we create a Bedrock KB with:**
- A data source (S3 / SharePoint / Confluence / Drive / etc.)
- A chunking strategy (from Layer 3 registry)
- An embedding model (from Layer 3 registry)
- A vector store (from Layer 5 — typically OpenSearch Serverless NextGen for hot, S3 Vectors for cold)
- Optional: a custom prompt template, an inline rerank

**What the platform adds on top of Bedrock KB:**
- A canonical registry of all KBs (their IDs, owners, configs, SLAs)
- A unified API that abstracts KB-specific concerns
- An ingestion orchestrator that handles multi-KB workflows
- A retrieval composer that can query multiple KBs and merge results
- Eval, observability, cost attribution

**Why not just use Bedrock KB directly?**
- Bedrock KB has 1 strategy per KB; we need 1 strategy per knowledge *type* (and a KB can hold multiple types)
- Bedrock KB has no first-class multi-tenancy story
- Bedrock KB has no eval set / scoring per KB
- Bedrock KB has no SLA tier concept (all KBs are best-effort)
- Bedrock KB doesn't expose chunk IDs back to the app (we need this for citations + UI)

We use Bedrock KB as the *underlying mechanism*. The platform is the *abstraction layer*.

---

## 4. Layer 2 — Knowledge source onboarding

**The goal:** a team can connect a new data source in < 5 minutes, with the right strategy auto-selected, and a working query in < 30 minutes.

### 4.1 The onboarding flow (self-service)

```
Step 1: Pick a data source type
        [S3 bucket] [SharePoint site] [Confluence space] [Google Drive folder]
        [OneDrive folder] [Web URL] [Salesforce object] [Custom API]

Step 2: Authenticate + scope
        → OAuth flow (per-user or per-service-account)
        → Pick the scope (full bucket, prefix, query, folder, etc.)
        → Test the connection (does it work? can we list files?)

Step 3: Pre-flight checks
        → File count, total size, file types
        → Estimated ingestion time + cost
        → Detected PII (warn before ingest)
        → Permission model (source has ACLs? we'll respect them)

Step 4: Pick a knowledge type (or auto-detect)
        [Code] [Documents] [Chat/email] [FAQ] [Structured data]
        → Auto-detect from file extensions + first-pass content scan
        → User can override

Step 5: Pick an SLA tier
        [Gold — minutes] [Silver — hourly] [Bronze — daily]
        → Gold: S3 events trigger immediate re-sync
        → Silver: EventBridge schedule, hourly
        → Bronze: EventBridge schedule, daily

Step 6: Review + create
        → Show the config (chunking, embedding, retrieval, cost estimate)
        → "Create" → platform provisions the KB + ingestion pipeline
        → First ingestion runs in background
        → Notify when ready

Time to first query: < 30 minutes for the common case
```

### 4.2 The underlying mechanism (what the platform does)

For each new knowledge source, the platform:

1. **Creates a Bedrock KB** with the right data source, chunking, embedding
2. **Creates an EventBridge rule** for change events (or a scheduled rule for periodic sync)
3. **Wires ingestion notifications** to the user (SLA-based: "synced" / "failed" / "stale")
4. **Registers the KB** in the platform's KB registry
5. **Provisions a query API** bound to the KB
6. **Starts observability** (per-KB metrics, eval)

The platform uses **infrastructure-as-code** (CDK or Terraform) for this — every KB is a config object, reproducible, auditable.

### 4.3 Pre-flight checks (the part teams skip if you don't enforce it)

| Check | Why |
|---|---|
| **Auth works** | Catches misconfigured OAuth before the user is stuck |
| **Scope is right** | "You picked the whole bucket — that's 2M files, want to scope to a prefix?" |
| **File count + size** | Cost estimate; "this will cost $X/month to store, OK?" |
| **PII scan** | Detect SSN, credit card, etc. before they go into embeddings |
| **Entitlement model** | "This SharePoint has per-user permissions — we'll enforce them at query time, OK?" |
| **First-pass content scan** | Auto-classify as code/docs/chat/FAQ; surface for override |

---

## 5. Layer 3 — Strategy registry (the per-knowledge-type engine)

**The insight:** different knowledge types need different strategies. One-size-fits-all is why RAG often fails.

### 5.1 The 5 knowledge types + their strategies

| Type | Examples | Chunking | Embedding | Retrieval | Notes |
|---|---|---|---|---|---|
| **Code** | Source files, code snippets | Code-aware (tree-sitter, line ranges) | Code embedding (Cohere embed-v3, Voyage Code, or text-embedding-3 with code prefix) | Hybrid: BM25 on symbols + vector on semantics; filter by file path / language | Respect existing structure (functions, classes) |
| **Documents** | PDFs, Word, Markdown, Notion | Hierarchical (parent 2K, child 500) | Titan v2 or Cohere v3 (default) | Hybrid: BM25 + vector, with RRF + rerank | Default for most enterprise content |
| **Chat / email** | Slack, Teams, email threads | Conversational turn-aware (whole thread) | Titan v2 | Hybrid + temporal filter (recent first) | Need speaker metadata; thread structure |
| **FAQ / snippets** | Help center, snippets, policy docs | No chunking (whole doc) | Titan v2 | Pure vector; rerank aggressively | Short, high-signal content; whole-doc embedding is fine |
| **Structured data** | CSV, Parquet, DB rows | Row-level (one row = one chunk) | Embed the row's text columns; metadata is the schema | Filter-first (SQL-equivalent), then vector on the matched subset | Hybrid of search + filter; the structure is the data |

### 5.2 The registry

```python
class KnowledgeType(Enum):
    CODE = "code"
    DOCUMENTS = "documents"
    CHAT = "chat"
    FAQ = "faq"
    STRUCTURED = "structured"

STRATEGY_REGISTRY: dict[KnowledgeType, Strategy] = {
    KnowledgeType.CODE: Strategy(
        chunking=CodeAwareChunking(
            parser="tree-sitter", max_chunk_tokens=2000, overlap_tokens=200,
        ),
        embedding=CohereEmbedV3(model="embed-english-v3.0", input_type="search_document"),
        retrieval=HybridRetrieval(
            bm25=BM25Config(fields=["symbols", "identifiers"], boost_code=True),
            vector=VectorConfig(distance="cosine", k=50),
            rerank=AmazonRerank1(top_n=10),
        ),
    ),
    KnowledgeType.DOCUMENTS: Strategy(
        chunking=HierarchicalChunking(parent=2000, child=500, overlap=60),
        embedding=TitanV2(model="amazon.titan-embed-text-v2:0", dim=1024),
        retrieval=HybridRetrieval(
            bm25=BM25Config(fields=["content", "title"]),
            vector=VectorConfig(distance="cosine", k=50),
            rerank=AmazonRerank1(top_n=10),
        ),
    ),
    # ... etc
}
```

**The user can override** the strategy per knowledge source. The default is sensible; the override is for advanced users.

### 5.3 A/B testing strategies

For a given KB, the platform can run **two strategies in parallel** and compare:

```
Strategy A: hierarchical chunking, Titan v2, hybrid + rerank
Strategy B: semantic chunking, Cohere v3, hybrid + rerank

→ Run a 100-case eval set against both
→ Surface the comparison in the UI: "Strategy B has 12% better recall on your eval set"
→ User picks; promotion is a config change, no re-ingestion needed
```

This is the eval loop from the harness design, applied per-KB.

---

## 6. Layer 4 — Ingestion pipeline

**The goal:** changes in source data flow into the KB within the SLA, with retries, dead-letter, and notifications.

### 6.1 The pipeline (event-driven)

```
Source change (S3 ObjectCreated / SharePoint webhook / etc.)
   │
   ▼
EventBridge (per-source rule)
   │
   ▼
Ingestion Orchestrator (Step Functions)
   │
   ├── Pre-flight: validate, dedupe, batch
   │
   ├── Trigger Bedrock KB ingestion job
   │     │
   │     ├── Success: update KB status, emit "ingestion_complete" event
   │     ├── Failure (retryable): retry with backoff (3 attempts)
   │     └── Failure (final): DLQ + alert
   │
   ├── Post-ingest: run eval sample (5%), update KB health score
   │
   └── Notify user (per SLA: minutes for gold, hourly for silver, daily for bronze)
```

### 6.2 SLA tiers

| Tier | Sync latency | Use case | Cost | Trigger |
|---|---|---|---|---|
| **Gold** | < 5 minutes | Customer-facing content; data the agent needs immediately | $$$ | S3 events, webhooks, real-time |
| **Silver** | < 1 hour | Internal docs, runbooks, recent changes | $$ | EventBridge schedule (hourly) |
| **Bronze** | < 24 hours | Archives, historical data, compliance content | $ | EventBridge schedule (daily) |

The user picks the tier at onboarding. The cost difference is real — Gold means an active ingestion pipeline; Bronze means a daily batch.

### 6.3 The ingestion orchestrator (Step Functions)

```json
{
  "Comment": "Ingestion orchestrator — one execution per (source, change event)",
  "StartAt": "Preflight",
  "States": {
    "Preflight": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:ingest-preflight",
      "Next": "BatchChanges"
    },
    "BatchChanges": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:ingest-batch",
      "Next": "TriggerKBIngest"
    },
    "TriggerKBIngest": {
      "Type": "Task",
      "Resource": "arn:aws:states:::bedrock:startIngestionJob",
      "Next": "WaitForCompletion",
      "Catch": [{
        "ErrorEquals": ["States.TaskFailed"],
        "Next": "RetryOrDLQ"
      }]
    },
    "WaitForCompletion": {
      "Type": "Wait",
      "Seconds": 30,
      "Next": "CheckStatus"
    },
    "CheckStatus": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:check-ingest-status",
      "Choices": [
        {"Variable": "$.status", "StringEquals": "COMPLETE", "Next": "PostIngestEval"},
        {"Variable": "$.status", "StringEquals": "IN_PROGRESS", "Next": "WaitForCompletion"},
        {"Variable": "$.status", "StringEquals": "FAILED", "Next": "RetryOrDLQ"}
      ]
    },
    "PostIngestEval": {
      "Type": "Task",
      "Resource": "arn:aws:lambda:...:function:post-ingest-eval",
      "Next": "NotifySuccess"
    },
    "NotifySuccess": {
      "Type": "Task",
      "Resource": "arn:aws:sns:::openmate-notify",
      "End": true
    },
    "RetryOrDLQ": {
      "Type": "Choice",
      "Choices": [
        {"Variable": "$.attempt", "NumericLessThan": 3, "Next": "BackoffRetry"},
        {"Variable": "$.attempt", "NumericGreaterThanEquals": 3, "Next": "DLQ"}
      ]
    },
    "BackoffRetry": {
      "Type": "Wait",
      "SecondsPath": "$.backoff_seconds",
      "Next": "TriggerKBIngest"
    },
    "DLQ": {
      "Type": "Task",
      "Resource": "arn:aws:sqs:::openmate-ingest-dlq",
      "End": true
    }
  }
}
```

### 6.4 Failure handling (the part teams forget)

- **Retry with backoff** — 3 attempts with exponential backoff
- **Dead letter queue** — failed ingestions go to a DLQ for human review
- **Stale detection** — if a Gold-tier KB hasn't synced in 30 min, alert
- **Partial success** — if 95% of files ingested, surface the 5% that didn't
- **Idempotency** — same source change event never ingests twice

---

## 7. Layer 5 — Storage tiers

Not all knowledge has the same access pattern. Tier the storage.

| Tier | Use case | Storage | Latency | Cost |
|---|---|---|---|---|
| **Hot** | Active KBs, queried frequently | OpenSearch Serverless NextGen | 5-10ms | $0.24/OCU-hr + storage |
| **Warm** | KBs queried weekly/monthly | OpenSearch managed cluster (smaller) | 20-50ms | Lower OCU count |
| **Cold** | Archives, compliance, infrequent | S3 Vectors | 100ms | $0.06/GB-mo |

**The pattern:** write to hot, migrate to warm after 30 days of low query rate, migrate to cold after 90 days. Or: user picks the tier at onboarding.

For an openmate KB that the agent queries every turn, **hot** is the right default. For an audit log of past conversations, **cold** is enough.

---

## 8. Layer 6 — Retrieval layer

**The goal:** every query gets the right chunks, regardless of which KB they live in.

### 8.1 Single-KB retrieval (the common case)

```python
def retrieve(query: str, kb_id: str, k: int = 10) -> list[Chunk]:
    """Standard retrieve — one query, one KB, hybrid + rerank."""
    return bedrock_agent.retrieve(
        knowledgeBaseId=kb_id,
        retrievalQuery={"text": query},
        retrievalConfiguration={
            "vectorSearchConfiguration": {
                "numberOfResults": k,
                "overrideSearchType": "HYBRID",
            }
        },
    )
```

### 8.2 Multi-KB retrieval (the corporate case)

When the user says "find docs about Q3 results," the platform needs to figure out which KBs to query. This is **query routing**.

```python
def multi_kb_retrieve(query: str, user_id: str, k: int = 20) -> list[Chunk]:
    # 1. Classify the query — which KBs are relevant?
    relevant_kbs = kb_router.classify(query, user_id)  # small FM call

    # 2. Query each in parallel
    results_per_kb = await asyncio.gather(*[
        retrieve(query, kb.id, k=k) for kb in relevant_kbs
    ])

    # 3. Merge with RRF
    merged = rrf_fuse(results_per_kb, k=60)[:k]

    # 4. Rerank the merged top-K
    reranked = rerank(query, merged, top_n=10)

    return reranked
```

The kb_router can be:
- A small FM call (Haiku) that picks KBs based on the query
- A learned classifier (faster, cheaper)
- An embedding-similarity lookup (cheapest, lowest quality)

### 8.3 Metadata filtering (the entitlement layer)

Every query carries the user's identity. The platform translates that into metadata filters:

```python
def build_metadata_filter(user: User) -> dict:
    """Translate user identity → KB metadata filter."""
    return {
        "andAll": [
            # Tenant isolation
            {"equals": {"key": "org_id", "value": user.org_id}},
            # User-level access (if the KB has per-user ACLs)
            {"orAll": [
                {"equals": {"key": "allowed_users", "value": user.id}},
                {"equals": {"key": "visibility", "value": "org"}},
            ]},
            # Optional: time-bounded (e.g., for confidential content)
            {"lessThan": {"key": "confidential_until", "value": now()}},
        ]
    }
```

This is where **entitlements from source systems flow through**. If a SharePoint doc has per-user ACLs, those propagate as metadata at ingestion time; the filter enforces them at query time.

### 8.4 Reranking

Rerank is enabled by default for hot-tier KBs. The platform uses **Amazon Rerank 1.0** (the AWS-native option) or **Cohere Rerank 3.5** for higher quality. The cost is per query; the platform eats it on hot-tier KBs, charges it through on cold.

---

## 9. Layer 7 — Observability + cost attribution

Every KB has a dashboard. Every team sees their own cost.

### 9.1 Per-KB metrics

```yaml
KB: "acme-financials-2026"
  Strategy: documents / hierarchical / Titan v2
  Storage: hot (OpenSearch NextGen)
  SLA: gold

  Ingestion:
    Last sync: 2026-08-06 10:15 UTC
    Success rate (7d): 99.7%
    Avg sync latency: 2m 18s
    P95 sync latency: 4m 02s
    Failed syncs (7d): 1
    DLQ depth: 0

  Retrieval:
    Queries (7d): 14,238
    Avg latency: 87ms
    P95 latency: 412ms
    Cache hit rate: 38%
    Top-5 hit rate (eval): 92%

  Cost (7d):
    Embedding: $4.21
    Storage: $2.18
    Query: $8.92
    Rerank: $3.14
    Total: $18.45

  Quality:
    Eval set size: 50
    Last eval: 2026-08-05
    Recall@5: 0.92
    MRR: 0.78
    Drift (vs baseline): -1.2%  ⚠️
```

### 9.2 Cost attribution

```python
def attribute_cost(usage: UsageRecord) -> None:
    """Tag every cost to org / project / KB / team."""
    usage.cost_breakdown.cost_center = kb.org_id
    usage.cost_breakdown.project_id = kb.project_id
    usage.cost_breakdown.kb_id = kb.id
    usage.cost_breakdown.embedding_cost = compute_embedding_cost(usage)
    usage.cost_breakdown.storage_cost = compute_storage_cost(usage, kb.storage_tier)
    usage.cost_breakdown.query_cost = compute_query_cost(usage, kb.storage_tier)
    # ... write to cost analytics (e.g., tagged for Cost Explorer)
```

This lets a finance team answer: "what did the openmate bill look like for the legal team last month, broken down by KB?"

---

## 10. Layer 8 — Multi-tenancy + governance

**The corporate reality:** different teams, different sensitivity levels, different entitlements.

### 10.1 The tenancy model

```
Organization
  ├── Project (e.g., "Legal RAG", "Engineering Wiki")
  │     ├── Knowledge Source 1
  │     ├── Knowledge Source 2
  │     └── Knowledge Source 3
  └── Project
        └── ...
```

- **Org** — billing boundary, default policy
- **Project** — sharing boundary, RBAC
- **Knowledge Source** — a single data source (one KB or a group of related KBs)

### 10.2 RBAC matrix

| Role | Can create KB | Can edit strategy | Can query | Can delete |
|---|---|---|---|---|
| **Org admin** | ✓ (any project) | ✓ (any) | ✓ (any) | ✓ (any) |
| **Project owner** | ✓ (in their project) | ✓ (in their project) | ✓ (in their project) | ✓ (in their project) |
| **KB owner** | ✗ | ✓ (their KB) | ✓ (their KB) | ✓ (their KB, after 7d soft-delete) |
| **Reader** | ✗ | ✗ | ✓ (their KB) | ✗ |
| **End user** | ✗ | ✗ | ✓ (KBs they have access to) | ✗ |

### 10.3 The audit log

Every action is logged:
- Who created / edited / queried / deleted the KB
- What the query was
- What the response was (top-K chunk IDs)
- Cost incurred

Append-only, hash-chained, exportable to S3 for compliance.

---

## 11. Layer 9 — The developer API (the abstraction)

**This is the only layer the app developer sees.** Everything below is the platform.

### 11.1 The high-level API

```python
# Onboard a new knowledge source
kb = await rag.knowledge.create(
    source="s3://acme-financials-2026/",
    type="documents",
    sla="gold",
    name="acme-financials",
)
# → platform provisions Bedrock KB + EventBridge rule + ingestion pipeline
# → first sync in < 5 minutes (gold SLA)
# → returns the kb.id

# Query
chunks = await rag.query(
    text="What was Q3 revenue?",
    knowledge=["acme-financials", "acme-runbooks"],  # by name, not KB ID
    user=current_user,  # for entitlement filtering
    k=10,
    rerank=True,
)
# → platform routes to right KBs, filters by user entitlements, hybrid + rerank
# → returns chunks with source attribution

# Or: get a generated answer
answer = await rag.ask(
    text="What was Q3 revenue?",
    knowledge=["acme-financials"],
    user=current_user,
    model="claude-sonnet-5",
)
# → platform does retrieval + generation + citations
# → returns { answer, sources, cost }
```

### 11.2 The full type surface

```python
class RAG:
    knowledge: KnowledgeAPI   # create, list, get, update, delete
    query: QueryAPI           # query, ask, stream_ask
    eval: EvalAPI             # run_eval, get_recall, get_drift
    observability: ObsAPI     # get_metrics, get_cost, get_audit
    admin: AdminAPI           # RBAC, project, billing

class KnowledgeAPI:
    async def create(source: str, type: KnowledgeType, sla: SLATier, ...) -> Knowledge
    async def list(user: User) -> list[Knowledge]
    async def get(kb_id: str) -> Knowledge
    async def update(kb_id: str, config: KnowledgeConfig) -> Knowledge
    async def delete(kb_id: str) -> None
    async def sync_now(kb_id: str) -> SyncJob

class QueryAPI:
    async def query(text: str, knowledge: list[str], user: User, k: int = 10, ...) -> list[Chunk]
    async def ask(text: str, knowledge: list[str], user: User, model: str, ...) -> Answer
    def stream_ask(text: str, ...) -> AsyncIterator[AnswerEvent]
```

### 11.3 The UI

The platform ships a **knowledge admin UI** that mirrors the API:

- List of all knowledge sources (filterable by org / project / type / SLA)
- Onboarding wizard (the 5-minute flow)
- Per-KB dashboard (the metrics above)
- Cost breakdown by team
- Eval set editor
- Strategy A/B test runner

The UI is for KB owners and admins. End users (the agent's callers) never see it.

---

## 12. The 5 design decisions that matter most

### 12.1 Why not just use Bedrock KB directly?

Because corporate RAG needs more than Bedrock KB gives you out of the box:
- **Multi-tenant + RBAC + entitlements** — not in Bedrock KB
- **Per-KB eval + drift detection** — not in Bedrock KB
- **SLA tiers with notifications** — not in Bedrock KB
- **Multi-KB routing + query understanding** — not in Bedrock KB
- **Cost attribution per team / project / KB** — not in Bedrock KB
- **A/B testing strategies** — not in Bedrock KB

Bedrock KB is the *mechanism*. The platform is the *abstraction*.

### 12.2 Why a strategy registry, not a strategy per KB?

Because 80% of KBs in a corporate setting will be one of 5 types (code / docs / chat / FAQ / structured). Encoding the right default for each type saves 6 weeks per team. The escape hatch is "user picks custom strategy" for the long tail.

### 12.3 Why per-knowledge-type embedding, not one model for all?

Because the embedding model is the biggest lever on retrieval quality:
- Code → Cohere embed-v3 (input_type=search_document) or Voyage Code
- Documents → Titan v2 (general-purpose, 1024-dim)
- FAQ → Titan v2 (small, fast, fine for short docs)
- Structured → embedding on the text columns, but the metadata filter is the real retrieval

One embedding model for all means one retrieval quality for all. Per-type means each type gets its best.

### 12.4 Why metadata filtering at query time, not at ingestion time?

Because at ingestion time, you don't know which users will query. At query time, you do. The metadata filter at query time enforces entitlements dynamically — the same KB can serve a junior engineer and a senior partner with different access.

But: the *metadata* is set at ingestion time. The platform extracts it from the source (SharePoint permissions, S3 tags, document metadata) and stores it as KB metadata. The query-time filter uses it.

### 12.5 Why a developer API, not a UI for everything?

Because the most common caller is the agent runtime, not a human. The API is the primary interface; the UI is the admin tool. If the API is well-designed, the UI is a thin layer on top.

---

## 13. Phased delivery

### Phase 0: Foundation (weeks 1–4)

- Bedrock KB provisioning via CDK
- The 5-knowledge-type strategy registry
- The ingestion orchestrator (Step Functions + EventBridge)
- The hot tier (OpenSearch Serverless NextGen) + cold tier (S3 Vectors)
- The developer API (Layers 7-9 in skeletal form)
- **Owner:** 1 eng + 1 SRE

### Phase 1: Self-service onboarding (weeks 5–8)

- The 5-minute onboarding flow (UI + API)
- Pre-flight checks (auth, scope, cost estimate, PII scan)
- Multi-KB routing
- Metadata filtering + entitlements
- The knowledge admin UI
- Per-KB dashboard (basic metrics)
- **Owner:** +1 eng, +1 design
- **Acceptance:** 3 internal teams onboard 5 KBs each in < 30 min total

### Phase 2: Quality + governance (weeks 9–16)

- Per-KB eval set + drift detection
- Strategy A/B testing
- Cold tier migration (warm → cold after N days)
- Full RBAC matrix
- Audit log (hash-chained, exportable)
- Cost attribution per team / project / KB
- **Owner:** +1 eng
- **Acceptance:** 10 teams in production, 99% ingestion SLA, < 5% recall drift week-over-week

### Phase 3: Power features (months 5–8)

- Custom strategies (escape hatch for the long tail)
- Cross-KB graph (query understanding that uses the KB topology)
- Per-tenant model fine-tuning (fine-tune the embedding on the tenant's own data)
- Self-hosted option (BYO vector store)
- **Owner:** +1 eng, +1 ML eng

---

## 14. Risks and tradeoffs

### 14.1 Bedrock KB is the dependency

If AWS raises prices, breaks the API, or deprecates a feature, the platform inherits the risk. **Mitigation:** keep the platform API stable, the implementation can change. If needed, swap Bedrock KB for OpenSearch + custom pipeline.

### 14.2 The strategy registry is opinionated

If we pick the wrong default for a knowledge type, every team inherits the bad default. **Mitigation:** the eval set per KB detects drift; users can override; the A/B test runner lets teams experiment.

### 14.3 Multi-KB routing is a new failure mode

Single-KB retrieval is well-understood; multi-KB adds query routing, which is a learned component that can fail. **Mitigation:** show the user which KBs were queried; let them override; eval the router.

### 14.4 Cold tier has higher latency

If a KB is on S3 Vectors (cold) but the user expects hot-tier latency, the UX suffers. **Mitigation:** clear labeling of tier in the dashboard; warn at onboarding; auto-promote hot if query rate exceeds threshold.

### 14.5 The platform can become a tax

If every team has to go through the platform, the friction can outweigh the benefit. **Mitigation:** the 5-minute onboarding is the design center. The escape hatch (custom strategy, custom KB) is always available.

---

## 15. The one-paragraph version

**The openmate RAG infrastructure is a 9-layer platform: Bedrock KB as the foundation, a self-service onboarding flow that takes a team from "I have data" to "I can query it" in < 30 minutes, a strategy registry that picks the right chunking / embedding / retrieval per knowledge type (code / documents / chat / FAQ / structured — each with its own defaults), an event-driven ingestion pipeline with gold / silver / bronze SLA tiers, tiered storage (hot OpenSearch Serverless / cold S3 Vectors), a retrieval layer that handles multi-KB routing + metadata filtering + reranking, per-KB observability and cost attribution, multi-tenant RBAC with entitlements, and a single developer API that hides all the complexity. The platform's job is to turn 6 weeks of RAG plumbing into 5 minutes of self-service, with the right defaults already chosen and an escape hatch for advanced cases. The single biggest mistake: trying to use Bedrock KB directly without the abstraction layer — it gets you 60% of the way, but the missing 40% (multi-tenancy, eval, SLA, cost attribution, strategy A/B testing) is the part that makes corporate RAG work.**
