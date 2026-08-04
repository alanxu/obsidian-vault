# RAG System for a Financial Services Company on AWS

> Design notes for an interview. Optimised to demonstrate architecture depth,
> not just AWS service recall. The shape: a **decoupled ingestion pipeline**
> feeding a **multi-store retrieval core**, fronted by a **polyglot client
> gateway** that supports sync UI, agent tool use, event triggers, and cron
> jobs — all wrapped in **financial-grade** cross-cutting concerns
> (immutable audit, ACL-aware retrieval, multi-region resilience, PII handling).

---

## 0. Architecture at a glance

```
                ┌────────────────────────────────────────────────────────────┐
                │                       INGESTION                            │
                │                                                            │
  Sources ─► Connectors ─► Pre-process ─► Extract/LLM ─► Chunk/Enrich ─► Index
   (SFTP,       (Lambda,        (Textract,    (Bedrock,     (semantic,    (OpenSearch,
   SP, S3,      Step            Transcribe,   Comprehend,   parent-child, pgvector,
   API,         Functions)      Macie)        Nova/Claude)  late)         Neptune,
   Kinesis,                                                                        S3)
   email)                                                                        │
                └────────────────────────────────────────────────────────────┘
                                                  │
                                                  ▼
                ┌────────────────────────────────────────────────────────────┐
                │                       RETRIEVAL                            │
                │                                                            │
  Clients ─► Gateway ─► Query Planner ─► Hybrid Recall ─► Rerank ─► Generate
   (UI,         (API GW,     (intent,         (BM25 +        (Cohere/     (Bedrock
   Agent,       AppSync,     rewrite,         ANN,           LLM)         Claude,
   Event,       EventBridge, HyDE)            ACL-filter)                 streaming)
   Cron)        SQS)                                                            │
                                                  │                             ▼
                                       ┌──────────┴──────────┐             Citations,
                                       │  Feedback / Eval    │             provenance
                                       │  (Langfuse,         │
                                       │   human-in-loop)    │
                                       └─────────────────────┘
```

Two non-negotiable design choices up front:

1. **Decouple ingestion from retrieval.** They have very different SLOs
   (ingestion: minutes-to-hours, throughput-bound, best-effort ok on retry;
   retrieval: sub-second p95, latency-bound, never-fail-noisy-neighbour).
2. **Stores are polyglot, not one DB to rule them all.** Vector for semantic,
   keyword/BM25 for exact/regulatory citations, graph for entity relationships,
   relational for structured fact tables, object store for the raw artefact.
   A single store would force the wrong shape onto at least one workload.

---

## 1. Ingestion Subsystem

### 1.1 Source catalogue

Financial services have an unusually wide source surface. Covering it
honestly is itself an interview signal.

| Source class           | Examples                                         | Connector pattern |
|------------------------|--------------------------------------------------|-------------------|
| File transfer (legacy) | SFTP from custodians, fund admins, exchanges     | AWS Transfer Family → S3 events → Lambda |
| SaaS document stores   | SharePoint, Box, Confluence, internal portals     | Graph API poller (EventBridge schedule) + delta-token |
| Public/SaaS HTTP APIs  | SEC EDGAR, Refinitiv, Bloomberg BLP, KYC vendors | API Gateway → Lambda; pagination + retry budget |
| Vendor webhooks        | DocuSign envelopes, sanction-list push, KYC      | API Gateway with HMAC signature verification |
| Email                   | Statements, counterparty notices, internal mail  | SES → receipt rule → S3 (raw EML + attachments) |
| S3 drops (B2B)         | Custody statements, GIPS composites, audit packs | S3 Event Notifications → SQS |
| Streaming               | Market data, trade events, chat ops, KYC events  | Kinesis Data Streams / MSK (Kafka) |
| Database CDC            | Core banking (Postgres, Oracle), CRM, portfolio  | DMS → Kinesis → S3 (Parquet, partitioned) |
| News / RSS / web       | Regulatory news, market commentary               | Lambda scraper (rate-limited) or 3rd-party News API |
| Voice / audio           | Earnings calls, voicemails, compliance calls     | S3 drops → Transcribe |
| Mobile / scan          | KYC selfies, signed agreements, expense receipts | App → S3 via presigned URL; Textract async |
| FIX / SWIFT            | Trade messages (FIX 4.4/5.0), SWIFT MT/MX        | On-prem bridge → Kinesis; parse + normalise |
| XBRL                    | 10-K, 10-Q, 13F, regulatory filings              | EDGAR pull + XBRL parser (Arelle) |

A `Source Registry` (DynamoDB table) holds connector config per source
(credentials, schedule/rate, schema, owner team, retention class). New
connectors are added by registering config and dropping a Lambda
implementation; the runtime picks them up via Step Functions Map state.

### 1.2 Format catalogue and pre-processing

| Format             | Examples                              | Pre-process on AWS                                                                                                   |
| ------------------ | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| PDF (text + scan)  | Prospectus, 10-K, contracts           | Textract (`DetectDocumentText` + `AnalyzeDocument` with `FORMS`/`TABLES`); fall back to PyMuPDF for text-native PDFs |
| Scanned images     | KYC, signed paper forms               | Textract; flag low-confidence for human review                                                                       |
| Structured text    | CSV, XLSX, Parquet, JSON, XML         | Glue Crawler → Glue Data Catalog; schema inferred + versioned                                                        |
| Unstructured text  | RTF, TXT, Markdown, log lines         | Glue / plain Lambda                                                                                                  |
| Email              | EML, MSG                              | SES + `mailparser` / `email` lib; extract body + attachments                                                         |
| Office             | DOCX, PPTX, XLSM                      | Convert via `LibreOffice` headless on Lambda or `mammoth` for DOCX                                                   |
| HTML               | News, portals                         | `trafilatura` / `BeautifulSoup` boilerplate strip                                                                    |
| Audio / video      | Earnings calls, compliance recordings | Transcribe (speaker diarisation on, custom vocabulary per ticker list)                                               |
| Images with charts | Chart PDFs, heatmaps, dashboards      | Nova/Claude Vision (multimodal Bedrock) — extract data, table, narrative                                             |
| XBRL               | Filings                               | Arelle + Glue ETL → relational facts                                                                                 |
| FIX / SWIFT        | Trade and cash messages               | QuickFIX/J or simple `pyfix` parser → JSON canonical                                                                 |

Every artefact lands in S3 with an **immutable, content-addressed key**:
`s3://rag-raw-{region}/{source}/{tenant}/{yyyy}/{mm}/{dd}/{sha256}.{ext}`.
The SHA-256 is the canonical id; idempotency in the pipeline is free.

### 1.3 Pipeline stages (the LLM-shaped middle)

A single Step Functions state machine per document class, parameterised by
an EventBridge rule. State machine (textual, with the LLM call highlighted):

```
[Receive]                S3 PutObject | API push | scheduled pull
   │
[Validate]               Schema check, virus scan (ClamAV Lambda), size limits
   │                     reject + DLQ + alert
[Pre-process]            Format-specific (Textract, Transcribe, etc.)
   │
[Classify]               Bedrock Claude Haiku: doc_type, language, jurisdiction,
   │                     confidentiality, PII flag  (small, cheap, fast)
   │
[Extract]                Bedrock Claude Sonnet (or Nova Pro for multimodal):
   │                     structured extraction with JSON Schema / Tool Use
   │                     → {entities, figures, dates, clauses, tables, claims}
   │                     → Pydantic-validated JSON; retry on schema fail
   │
[Chunk]                  Strategy chosen by doc_type (see §1.4)
   │
[Embed]                  Bedrock Titan Embeddings v2 / Cohere Embed v3
   │                     (1024–1536 dim, normalised)
   │
[Enrich]                 Attach metadata, lineage, ACL tags, source citations
   │
[Persist]                Fan-out writes to:
   │                     • S3 (chunk JSON + raw text + figures)
   │                     • OpenSearch vector index (with BM25 inverted index)
   │                     • Aurora PostgreSQL (structured facts via pgvector
   │                       or relational table for facts)
   │                     • Neptune (entity-relationship graph edges)
   │                     • DynamoDB (manifest, ACL, version pointer)
   │
[Index]                  Refresh k-NN graph; OpenSearch ISM rolls over shards
   │
[Done]                   Emit `ingest.completed` event → subscribers
```

**Why JSON Schema + Tool Use, not free-form prompting?**
Determinism. In FS, downstream consumers (compliance dashboards, fact lookup)
do not tolerate "almost-right" extraction. We force the LLM to call
`extract_facts(document) -> Facts` with a typed schema. Failed validations
go to a human review queue (Saga pattern, not a hard block — ingestion
keeps moving, bad rows quarantined).

**Why classify before extract?**
You do not want Sonnet burning tokens classifying PDFs into 40 categories
when Haiku does it at 1/30 the cost and 3× the speed. Model routing
(classifier → router → model) is one of the highest-ROI optimisations.

**Why a state machine, not a single Lambda?**
Long-running, retryable, observable per stage, human-in-the-loop inserts
naturally, and it survives partial failures. Step Functions also gives us
**eventual consistency** in the literal AWS sense: if extraction fails
transiently, the state retries; if it fails structurally, the document
goes to a DLQ and an alert fires, but the rest of the system keeps
serving the documents that did succeed.

### 1.4 Chunking strategies — chosen per document type

There is no "best" chunker. The interview talking point is **strategy
selection based on document structure and downstream query patterns**.

| Doc type                  | Strategy                                                                                                                                                      | Why                                                                                                |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Regulatory filings (10-K) | **Hierarchical parent-child**: page = parent, paragraph = child, table = own chunk                                                                            | Queries hit a specific clause; retrieval returns the child but the LLM gets the parent for context |
| Prospectus / contract     | **Clause-aware** chunking (LangChain `RecursiveCharacterTextSplitter` over clause regex); never break a "Representations and Warranties" section mid-sentence | Cross-clause answers need the whole clause                                                         |
| Tables (CSV/XLSX/PDF)     | **One row = one chunk** when ≤ 200 rows; **schema summary + sample rows** when larger; preserve column types in metadata                                      | "What is AAPL's Q3 net income?" hits one chunk, not a 10k-row slice                                |
| Earnings call transcript  | **Speaker turn** as chunk + rolling **5-turn window** as parent                                                                                               | "What did the CFO say about margins?" wants the answer in context                                  |
| News article              | **Sentence-window** with overlap; embed title separately and boost its weight                                                                                 | Title is the strongest signal                                                                      |
| Scanned PDF (low OCR)     | **Page-level** first, then re-chunk on second pass if text density is high                                                                                    | Don't fight bad OCR with semantic chunking — first you have to have text                           |
| Email thread              | **Per-message** with `In-Reply-To` chain as parent                                                                                                            | Thread context is everything                                                                       |
| Code (e.g. API docs)      | **Function/class** boundaries; LangChain `LanguageAwareSplitter`                                                                                              | Symbols matter, prose is glue                                                                      |
| Charts / images           | **Whole-image embedding** via multimodal embed; also extract data table and embed as text chunk                                                               | Multimodal + structured both retrieved                                                             |
|                           |                                                                                                                                                               |                                                                                                    |

**Late chunking** is a strong choice for documents where cross-chunk
semantics matter (long contracts): embed the whole document first, then
chunk the contextualised token embeddings. Implemented via
`jina-late-chunking` style on Bedrock or by chunking after a
long-context embedding pass with Titan v2 (8k context).

**Semantic chunking** (split where cosine similarity between adjacent
sentences drops below a threshold) is the most expensive but best for
narrative-heavy prose (equity research, internal memos).

### 1.5 Extraction — beyond "ask the LLM"

- **Tool Use / Structured Output**: every extract step uses Bedrock
  Tool Use with a JSON Schema; responses are validated by Pydantic before
  they enter the system. Invalid responses are retried with the error
  message in the next prompt (up to 3 attempts), then quarantined.
- **Multi-pass extraction**: first pass = entities + figures; second pass
  = relations between entities; third pass = risk flags / regulatory
  tags. Each pass uses a smaller, cheaper model. This composes better
  than a single giant extraction prompt.
- **Multimodal extraction**: charts and tables embedded in PDFs go
  through Nova/Claude Vision to produce both an image embedding and a
  text description + structured table. The text version is what
  retrieval matches against; the image is returned as a citation.
- **Cross-document reconciliation**: trade messages, news, and filings
  about the same entity are linked via entity resolution (Neptune + a
  small model) so a query "any news or filings on AAPL Q3?" pulls from
  multiple source classes coherently.
- **PII / sensitive redaction**: before any chunk is sent to the
  embedding model, run **Comprehend PII detection** and **Macie** over
  the raw artefact. Redacted versions are stored separately (`*-redacted`),
  tagged in the ACL index, and the original is gated to a stricter
  permission boundary. Embeddings themselves can leak; we never embed
  raw PII.

### 1.6 Reranking at ingestion — yes, at ingestion

Most tutorials rerank only at query time. Doing it at ingestion too
catches quality problems before they pollute the index.

- **Cohere Rerank 3.5 on Bedrock** scores every candidate chunk against
  a synthetic "this is the kind of question this chunk should answer"
  prompt (generated by Sonnet during enrichment). Chunks whose top score
  is below a threshold are flagged for re-chunking or human review.
- **Diversity rerank** (MMR, k=4) is applied when many chunks come from
  the same document, to prevent one filing from dominating a result set.
- **Embedding drift detection**: nightly job re-embeds a sample of chunks
  and alerts on cosine shift > ε (model upgrade, drift).

### 1.7 Storage layout

| Store             | What lives there                            | Service                                                  | Access pattern                                        |
| ----------------- | ------------------------------------------- | -------------------------------------------------------- | ----------------------------------------------------- |
| Raw artefacts     | Original PDF/email/CSV/etc. (WORM, 7 yr)    | S3 + Object Lock (Compliance)                            | Rare; lineage + audit                                 |
| Canonical text    | Extracted text per artefact                 | S3 (Standard)                                            | Re-chunking, eval                                     |
| Chunks + metadata | Chunk JSON with metadata, citations         | S3 (Standard-IA)                                         | Re-embed, debug                                       |
| Vector index      | Embeddings + sparse + dense hybrid          | OpenSearch Serverless or provisioned with `k-NN` (HNSW)  | k-NN search                                           |
| Keyword index     | BM25 inverted index, same docs              | OpenSearch (same cluster, separate index)                | Lexical + citation lookup                             |
| Structured facts  | Tables, figures, dates, entities            | Aurora PostgreSQL (pgvector for any that need embedding) | SQL, joins, BI                                        |
| Graph             | Entity relations, document links, citations | Neptune (or Neptune Serverless)                          | Multi-hop reasoning, "show me everything linked to X" |
| Manifest + ACL    | Doc id → locations, versions, perms         | DynamoDB (GSI on tenant + tag)                           | Lookup, ACL pre-filter                                |
| Eval + feedback   | Queries, answers, ratings, traces           | S3 + Athena or OpenSearch                                | Offline eval                                          |

The **manifest in DynamoDB is the source of truth** for "where is this
document?" All other stores are downstream projections. This makes
deletes, retention, GDPR right-to-be-forgotten, and re-indexing
tractable — you find the manifest row, fan-out delete.

---

## 2. Retrieval Subsystem

### 2.1 Client patterns

| Client                                                                      | Latency need              | Interaction                                | Backend                                                                                           |
| --------------------------------------------------------------------------- | ------------------------- | ------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| **Web UI** (analyst dashboard)                                              | <2s p95, streaming        | Sync request/response, then SSE stream     | API Gateway → Lambda (sync) → AppSync (GraphQL subscriptions for streaming)                       |
| **Agent tool use** (Bedrock Agent action group)                             | <5s typical, up to 60s    | Tool-call return; long runs are background | Direct Lambda invoke (with `actionGroupInvocation` payload), or Step Functions for multi-step     |
| **Event-driven** (e.g. "alert me if a new filing changes my answer")        | Fire-and-forget           | Async; idempotent                          | EventBridge → SQS → Lambda fan-out                                                                |
| **Cron / scheduled** (morning research brief, end-of-day compliance digest) | Minutes OK, must complete | Async batch                                | EventBridge schedule → Step Functions → parallel Lambda map → writes output to S3 + notifies user |

**The retrieval API has two endpoints, not one:**

- `POST /sync-query` — UI, simple agent tool calls. Returns within 30s or 504.
- `POST /async-query` — returns `{jobId}` immediately; status pollable
  via `GET /jobs/{id}`; results streamable via WebSocket when ready.

A query **auto-promotes to async** if Step Functions detects it will
take > 25s (e.g. multi-hop graph traversal + large rerank). This is
the long-running story: **the system is the same; the client gets to
choose its patience**.

### 2.2 Query planning

The first stage of retrieval is **understanding the query**, not searching.

1. **Intent classification** (Haiku): is this `factual`, `analytical`,
   `comparative`, `list`, `lookup_figure`, `summarise_doc`?
2. **Query rewriting**:
   - **HyDE** (Hypothetical Document Embeddings): generate a synthetic
     answer with Haiku, embed that, use it for the first-stage vector
     recall. Especially helpful for short analyst questions.
   - **Multi-query expansion**: turn "AAPL Q3" into 3–5 variants, run
     them in parallel, fuse with reciprocal rank fusion (RRF).
   - **Step-back prompting**: "What broader question is this an
     instance of?" — useful for regulatory lookups where the user
     asks a narrow question but the answer requires a statute.
3. **Structured-query extraction** (when the query has facets): "AAPL
   Q3 2024 net income" → filter `{ticker: AAPL, period: 2024-Q3,
   metric: net_income}` pre-search; the semantic search happens *over
   the filtered set* (post-filter is too slow at scale; pre-filter
   reduces recall badly if the facet is wrong, so we keep both branches
   and merge).
4. **ACL filter** — pre-built from the user's identity, role, tenant,
   and document classification. The OpenSearch query carries a
   `terms` filter on the `acl_tags` field; chunks the user cannot
   see are not in the candidate set, full stop. (See §3.3.)

### 2.3 Multi-stage retrieval

```
Query ──► [Plan + Rewrite] ──► [Filter by ACL] ──► [Hybrid Recall]
                                                       │
                                              ┌────────┴────────┐
                                              │                │
                                          BM25 (top 50)   k-NN (top 50)
                                              │                │
                                              └────────┬────────┘
                                                       │
                                                  RRF fusion (k=60)
                                                       │
                                              [Rerank: Cohere top 20]
                                                       │
                                          [LLM rerank: top 5 with reasoning]
                                                       │
                                          [Generate: Bedrock Claude]
                                                       │
                                          [Verify + cite: extract provenance]
                                                       │
                                                Streaming response
```

- **Hybrid recall** is non-negotiable in FS. A vector-only retriever
  misses exact figures, ticker symbols, and regulatory citations that
  are *literally* the answer. A BM25-only retriever misses the semantic
  match in a paraphrased 10-K. Reciprocal rank fusion (k=60) is the
  cheapest quality win in the whole stack.
- **Two rerank stages** because they have different cost/benefit:
  - Cohere Rerank 3.5 is fast, cheap, and high-quality. Cuts 50→20
    with minimal loss.
  - LLM rerank on top 20 using Sonnet *with chain-of-thought* is the
    quality tier; cuts 20→5 with very high precision. Used only when
    the query is high-stakes or low-confidence (rerank score spread
    is small).
- **Self-correction loop**: if the LLM's draft answer is not grounded
  in the retrieved chunks (string-match citation coverage < 70%), the
    system re-queries with a refined query. Up to 2 retries.
- **Citation provenance**: every claim in the answer is tagged with
  chunk id → document id → S3 URI. The UI renders clickable
  citations. This is a regulatory requirement, not a nice-to-have
  (you must be able to show the auditor the source of every fact).

### 2.4 Generation

- **Model**: Bedrock Claude (Sonnet 4 for quality, Haiku for cost on
  routine factual queries). Model ID chosen per query by the router.
- **Prompt caching**: the system prompt + retrieved chunks go in
  Bedrock's prompt cache; a 5-turn UI session drops cost ~80% and
  latency ~40% on the cache hit path. (Interview point: prompt
  caching is the single biggest cost lever and most teams don't
  enable it.)
- **Streaming**: API Gateway + Lambda response streaming
  (Node 20 / Python 3.12) for the UI; AppSync GraphQL subscriptions
  for real-time UX. Agent tool calls return the full result, not
  a stream — agents prefer complete objects.
- **Guardrails**: Bedrock Guardrails blocks PII exfiltration, jailbreak
  prompts, and topics outside scope (e.g. "personal financial advice
  to retail customers" if we're B2B). Applied at both ingest
  (redaction) and retrieve (output filtering).

### 2.5 Long-running, async, stateful

For the queries that won't fit in 30 seconds — multi-document
synthesis, cross-period comparisons, anything the agent wants to
break into steps — the same retrieval core runs inside a Step
Functions state machine:

```
[Receive job]
   │
[Plan decomposition]     Sonnet breaks the question into 3–7 sub-questions
   │
[Parallel sub-queries]   Map state: each sub-query goes through §2.2–2.3
   │
[Aggregate]              Map state results → final synthesis context
   │
[Generate]               Sonnet with full context
   │
[Verify + cite]
   │
[Notify]                 EventBridge → SNS / WebSocket / email / Slack
```

Clients poll `GET /jobs/{id}` or subscribe to a WebSocket channel. The
state machine is the audit log; every transition is recorded with
input, output, and timing. This is the artefact regulators want.

---

## 3. Cross-cutting concerns

This is the section that separates "designed a chatbot" from "designed
a financial system". Each concern is load-bearing.

### 3.1 Reliability

- **Multi-AZ everywhere** for hot path; multi-Region active-passive
  for the data plane. OpenSearch cross-cluster replication; Aurora
  global database; S3 cross-region replication.
- **Circuit breakers** on every LLM call (Anthropic, Cohere) and
  every external API; on open, fall back to degraded mode
  (BM25-only retrieval, cached answers, smaller model).
- **Retry budgets** with exponential backoff + jitter; idempotency
  keys on every external call (Bedrock doesn't dedupe; we do).
- **DLQs** at every stage boundary; alarms on DLQ depth > 0.
- **Backpressure**: Step Functions Map with `MaxConcurrency` to
  protect downstream rate limits (Anthropic TPM, OpenSearch bulk
  throughput).
- **Chaos drills**: monthly `gameday` kills one AZ or one service
  (OpenSearch, Bedrock, S3) in pre-prod; verify retrieval still
  serves within degraded SLO.

### 3.2 Observability

- **OpenTelemetry** as the only instrumentation. Every Lambda, every
  Step Function, every Bedrock call, every OpenSearch query emits
  spans. One trace id flows from UI click → answer rendered.
- **CloudWatch + X-Ray** for AWS-native signal; **Langfuse** (or
  Arize Phoenix) for LLM-specific: prompt, completion, token counts,
  retrieval scores, user feedback (👍/👎), eval scores.
- **Structured logging** in JSON; PII redaction at log write
  (Comprehend PII on log lines in the centralisation layer).
- **SLOs** declared explicitly:
  - Retrieval sync p95 < 1.5s, p99 < 3s
  - Ingestion end-to-end p95 < 10 min for a typical filing
  - Index freshness: new doc retrievable within 60s of `indexed`
  - Answer groundedness ≥ 0.85 (Langfuse eval, sampled 5% of traffic)
- **Eval harness** running nightly on a golden set of 500+
  question/answer/citation triples; tracks regression on
  retrieval recall@10, answer faithfulness, citation coverage.
  Wired into CI for any retrieval/embedding change.

### 3.3 Financial regulation

This is where most "AWS RAG" answers fall apart. The system must
be designed for the auditor, not just the user.

- **SEC Rule 17a-4(f)**: trading-related records in **WORM** storage
  (S3 Object Lock in Compliance mode) for the regulatory retention
  period. 7 years for most broker-dealer records; some go 10+.
  Object Lock cannot be shortened even by root — that's the point.
- **FINRA Rule 4511**: same — general business records, WORM,
  7 years, readily accessible for the first 2.
- **MiFID II** (if EU exposure): 5-year retention, timestamping
  at millisecond granularity; we use AWS Time Sync Service.
- **GDPR / CCPA**: right-to-erasure is a fan-out delete from the
  manifest + every store. Embedding-based redaction (delta
  embedding recompute for affected docs) is a non-trivial but
  solvable problem. The manifest makes it tractable.
- **SOX**: change management — every change to the retrieval
  pipeline is in CodePipeline with manual approval; every change
  to the index is traceable to a commit.
- **Model risk management** (SR 11-7, OCC 2011-12): the LLM is a
  "model" in the regulatory sense. The eval harness + lineage +
  human-in-the-loop review + monitoring of drift *is* the
  MRM programme. We treat the LLM like any other model under
  model governance: documented, versioned, monitored, signed off.
- **Audit trail**: every query logs `{who, when, what, retrieved
  chunks, generated answer, model version, citations}`. Tamper-
  evident via S3 Object Lock + CloudTrail Lake (immutable query log).
  An auditor should be able to ask "show me every answer this user
  received on 2025-03-15" and we answer in one query.
- **Data residency**: tenant can be pinned to a region; ingest
  and retrieve stay in-region. We model tenant as a top-level
  partition key everywhere; we never cross regions for a single
  tenant without explicit re-keying.

### 3.4 Permission control (the *hard* one)

Vector search + documents with per-row ACLs is a classic
trap. Filtering is the easy part; **making it the source of truth
across every store, with no bypass path, is the work.**

- **Identity**: Amazon Cognito (users) + IAM Identity Center (workforce);
  service-to-service is IAM roles with permission boundaries.
  Machine identities get scoped down to a single tenant.
- **Authorisation model**: ABAC (attribute-based) with three
  primary attributes — `tenant_id`, `user_role` (analyst, compliance,
  trader, …), `data_classification` (public, internal, confidential,
  restricted). Documents carry `acl_tags` = `{tenant_id, classification,
  allowlist_teams, deny_flags}`. Queries carry the same tags from the
  caller's identity.
- **Enforcement points** (every store, every time, never trust the caller):
  - **OpenSearch**: `terms` filter on `acl_tags` injected by a
    query-rewriting Lambda. Tested with adversarial inputs.
  - **Aurora / Neptune**: row-level security via Postgres RLS;
    Neptune uses property-graph ACL via a query-rewriter.
  - **S3**: bucket policy + IAM session policy scoped to the
    caller's tenant; per-object ACL is *not* relied on (too easy
    to misconfigure). Bucket prefix = tenant = primary isolation.
  - **Bedrock**: Guardrails + per-tenant KMS keys (envelope
    encryption with a tenant-specific CMK) so a leaked key
    compromises one tenant, not all.
- **Negative testing**: a security test suite in CI runs known
  cross-tenant queries and asserts the response is empty. This
  test fails CI if anyone removes the ACL filter from a query path.
- **Privileged access**: admins with break-glass access are
  recorded; their queries are flagged in the audit log; the
  events route to a separate security-review queue, not the
  normal audit queue.
- **Prompt injection defence**: untrusted content (e.g. a PDF
  scraped from the web) cannot exfiltrate via retrieved context
  because retrieved chunks are wrapped in a structural delimiter
  the LLM is trained to treat as data, not instructions. Bedrock
  Guardrails adds a second-layer prompt-attack classifier on the
  *output*. Citations also act as a natural guardrail: the
  answer is required to cite, so the user can always check the
  source.

### 3.5 Data availability and resilience

- **RPO / RTO targets** declared and tested:
  - Tier 1 (retrieval hot path): RPO 0, RTO 60s — multi-AZ, no
    async replication gap.
  - Tier 2 (recent ingested data, last 30 days): RPO 5 min,
    RTO 15 min — cross-AZ + cross-region async.
  - Tier 3 (archival > 30 days): RPO 1 hour, RTO 4 hours — S3
    cross-region replication + Glacier.
- **Storage classes** are chosen by the manifest, not ad-hoc.
  Hot vector index in OpenSearch (Provisioned, multi-AZ);
  warm artefacts in S3 Standard-IA; cold archives in S3 Glacier
  Instant Retrieval after 90 days, Deep Archive after 7 years.
- **Backup**: Aurora automated backups + PITR; OpenSearch
  snapshots to S3 daily; DynamoDB PITR enabled; Neptune
  snapshots weekly.
- **DR runbook** with quarterly game days. Region failover is
  a Route 53 health-check-driven weighted record set; the
  retrieval service is stateless behind ALB so failover is
  cheap. The *state* (OpenSearch, Aurora, Neptune) is the
  expensive part and is replicated.
- **Graceful degradation**: if the vector store is unreachable,
  fall back to BM25 + Claude on a cached "best-of" corpus for
  the most common questions. If Bedrock is down, return the
  top-k retrieved chunks raw with no synthesis. The system
  always returns *something* useful, never a blank page.

---

## 4. AWS services mapping (cheat sheet)

| Capability                  | Service                                                |
| --------------------------- | ------------------------------------------------------ |
| LLM (chat, vision)          | Bedrock — Claude Sonnet/Haiku, Nova Pro/Lite           |
| Embeddings                  | Bedrock — Titan v2, Cohere Embed v3                    |
| Reranking                   | Bedrock — Cohere Rerank 3.5                            |
| Guardrails / PII            | Bedrock Guardrails, Comprehend PII, Macie              |
| OCR                         | Textract (`AnalyzeDocument` with TABLES/FORMS)         |
| Speech-to-text              | Transcribe (diarisation, custom vocab)                 |
| Object storage (WORM)       | S3 + Object Lock (Compliance mode)                     |
| Vector + keyword hybrid     | OpenSearch Service (k-NN + BM25, ISM)                  |
| Structured facts            | Aurora PostgreSQL (pgvector optional)                  |
| Graph (entities, relations) | Neptune (Serverless)                                   |
| Manifest / ACL              | DynamoDB                                               |
| Orchestration               | Step Functions, EventBridge, SQS, SNS                  |
| Compute                     | Lambda (Node 20 / Python 3.12); Fargate for long jobs  |
| API                         | API Gateway (REST + WebSocket), AppSync                |
| Identity                    | Cognito, IAM Identity Center                           |
| Secrets / keys              | Secrets Manager, KMS (per-tenant CMK)                  |
| Observability               | CloudWatch, X-Ray, OpenTelemetry, Langfuse             |
| Audit / governance          | CloudTrail Lake, AWS Config, Audit Manager             |
| Streaming ingest            | Kinesis Data Streams, Kinesis Firehose, MSK            |
| File transfer               | AWS Transfer Family (SFTP/FTPS)                        |
| CDC                         | DMS                                                    |
| Schema discovery            | Glue Crawler + Glue Data Catalog                       |
| Build / deploy              | CodePipeline, CodeBuild, CDK or Terraform              |
| Cost / FinOps               | Cost Explorer, custom OpenSearch token-cost dashboards |

A "fully managed RAG" shortcut exists: **Bedrock Knowledge Bases**
(managed ingestion + retrieval + OpenSearch) plus **Bedrock Agents**
(managed agent loop with tool use). For a small team, this is the
right starting point. The architecture above is the "we outgrew
Knowledge Bases" version — typically 6–12 months in, once you need
custom chunking, ACL pre-filter at scale, multi-tenant isolation,
or evaluable fine-grained grounding.

---

## 5. Trade-offs and design decisions worth defending in an interview

| Decision                              | Alternative                    | Why I chose this |
|---------------------------------------|--------------------------------|------------------|
| Polyglot persistence                  | One vector DB (e.g. Pinecone)  | Different queries need different shapes; OpenSearch gives hybrid recall + WORM + ACL in one |
| OpenSearch for vector                 | Aurora pgvector, S3 Vectors, Pinecone | OpenSearch is the only one that does BM25 + k-NN + ACL filters + ISM in one place. S3 Vectors is promising but new and lacks hybrid. |
| Step Functions for long jobs           | ECS / Fargate long-runner      | Built-in retries, audit log, no idle cost, integrates with EventBridge |
| Cohere + LLM two-stage rerank         | Either alone                   | Cohere is fast/cheap; LLM rerank only on top-20 cuts cost without sacrificing quality |
| DynamoDB as manifest source-of-truth  | Postgres                       | Single-digit-ms lookups, scales, no schema migration to add a new store |
| Hierarchical parent-child chunks      | Fixed-size 512-token chunks    | FS queries are clause-level; we want to return a paragraph but show the section |
| Pre-filter ACL on the vector query    | Post-filter after recall       | Post-filter breaks at scale (recall collapses when ACL excludes >80% of corpus, which happens for restricted docs) |
| JSON Schema + Tool Use for extraction | Free-form prompting            | Determinism for downstream; can validate; can diff versions |
| Bedrock prompt caching                | No caching                     | 80% cost reduction on multi-turn UI; trivial to enable |
| Object Lock (Compliance) for raw data | Glacier without lock           | Regulator-mandated WORM; Glacier alone is not tamper-proof |

---

## 6. Cost Reduction

The senior-engineer signal here is that **cost is a design
constraint, not a FinOps afterthought**. The choices in §1–§5
already bias toward cost efficiency (model routing, hybrid recall,
prompt caching). This section lists the levers explicitly, with
order-of-magnitude impact, so the architecture stays cheap as
volume grows.

### 6.1 Where the money actually goes

A representative 10k-query/day FS RAG workload looks roughly like
this (token prices shift; numbers here are illustrative):

| Component                   | % of total | Why |
|-----------------------------|------------|-----|
| Generation (Sonnet answer)  | 40–55%     | Long context windows, high output tokens, multi-turn UI |
| Embeddings (Titan / Cohere) | 10–15%     | One-time at ingest; tiny per-query (just the query) |
| Rerank (Cohere + LLM)       | 5–10%      | Per-query; LLM rerank is the expensive bit |
| Vector + keyword search     | 10–20%     | OpenSearch OCU-hours dominate at scale |
| Storage (S3, OpenSearch, Aurora) | 10–20% | S3 + OpenSearch index footprint |
| Orchestration (Step Fn, Lambda) | 1–5%   | Step Functions state transitions + Lambda invocations |
| Network / data transfer     | 1–3%       | Inter-AZ; usually small inside one region |

The mistake most teams make: optimising embeddings (a small line)
while the generation tab grows 3× because nobody enabled prompt
caching. **Rank levers by impact, not by how interesting they are.**

### 6.2 Levers at the LLM generation layer (biggest line item)

**1. Prompt caching (Bedrock)** — the single highest-ROI control.
The system prompt + retrieved context block is identical across
many calls in a session. Bedrock prompt cache writes cost ~25%
more per token but reads cost ~10% of a fresh token, with a 5-min
TTL. On a typical 5-turn analyst session with 8k cached context,
**effective generation cost drops 60–85%**. Trivially enabled;
non-negotiable in production.

**2. Model routing / cascading**
- **Haiku** handles ~60% of queries: factual lookups,
  list questions, simple extractions, query rewriting,
  intent classification, HyDE generation.
- **Sonnet** handles the ~30% that need reasoning: multi-doc
  synthesis, comparative analysis, ambiguous questions.
- A small custom router (or Bedrock's `InvokeModel` with a
  cheap classifier) decides which model to call. Net effect:
  average per-query cost drops 40–60% vs always-Sonnet.

**3. Cap output length.** Most RAG answers should be 200–500
tokens. Set `max_tokens` aggressively; many APIs let clients
stream the answer and we cut at "answer is complete" (an
end-of-turn detector model or simple stop-token heuristic).
Saves 20–30% on output tokens.

**4. Bedrock batch inference** for non-urgent async jobs (cron
digests, bulk report generation, nightly re-extraction of new
filings). Same model, 50% discount, but minutes-to-hours latency
instead of seconds. We *deliberately* route cron and bulk
backfills through batch, never through the on-demand path.

**5. Provisioned throughput / model tokens** when sustained
volume on a single model exceeds ~5× the break-even. Lock in
predictable cost for the hot path; let burst go on-demand.

**6. Prompt compression.** For long retrieved contexts, run
a cheap model (Haiku) to compress to 30–50% of original size
while preserving the answer-relevant facts, then send the
compressed context to the generator. Tools: `llmlingua`,
selective-context. Saves 20–40% of input tokens with minimal
quality loss; verify with the eval harness, don't ship blind.

**7. Smaller context windows.** Default the retriever to top-5
chunks, not top-20. A longer context window is a cost, not a
free lever — every additional chunk adds tokens to *every*
generation. Tune top-k on the eval harness.

### 6.3 Levers at the embedding layer

**1. Lower dimensionality with no real recall loss.** Bedrock
Titan v2 supports 256 / 512 / 1024 dimensions. A well-tuned
512-d model often retains ≥95% of 1024-d recall. Storage and
search cost scale roughly linearly with dimensions; 1/2 the
dimensions = 1/2 the OpenSearch footprint and ~30% faster
queries. Pick 1024 as a safe default; A/B down to 512 with
the eval harness before going lower.

**2. Binary / scalar / product quantization in OpenSearch.**
- **Binary quantization**: 32× storage compression, ~1% recall
  hit, sub-millisecond search. Default for high-volume indexes.
- **Scalar quantization (int8)**: 4× compression, ~0% recall
  hit, default I would not disable.
- **Product quantization (PQ)**: 8–32× compression, configurable
  recall. Worth the engineering when indexes pass 10M vectors.

The OpenSearch k-NN plugin supports all three; we enable binary
quantization on the hot index and keep the original fp32
embeddings in S3 for re-quantization later. This is the
single biggest storage lever.

**3. Matryoshka representation learning** (Cohere Embed v3):
train embeddings such that the first 256 dims are meaningful
on their own. Lets us *embed once* and search at any of
{256, 512, 1024, 1536} dims without re-embedding. Cuts
inference and storage costs during A/B.

**4. Embedding cache + dedup at ingest.** Documents frequently
arrive in updates that are 95% identical to what's already
indexed (e.g. an issuer republishes a 10-K with one paragraph
changed). Hash each chunk, embed only the new ones. Saves
30–50% of ingest embedding cost on typical FS source mixes.

**5. Batch embedding calls.** Bedrock charges per token, not
per request, but invoking `InvokeModel` 1000 times in 1000
Lambdas is still 1000× Lambda overhead. Batch up to 96
chunks per call; use Step Functions Map with batching.

### 6.4 Levers at the retrieval / search layer

**1. Semantic cache** (the highest-impact retrieval lever
after prompt caching). Many analyst queries are semantically
identical ("AAPL Q3 net income" asked 50 times today).
- Cache key: embedding of the rewritten query (after ACL
  filter applied) + tenant + model version.
- Cache store: ElastiCache (Redis) with TTL = 5–60 min
  depending on source freshness.
- Hit rate in real FS deployments: 20–40% on analyst
  traffic, 50%+ on internal dashboard traffic.
- Saves the full retrieval + generation cost on a hit
  (only embedding + cache lookup). At 30% hit rate, that's
  ~30% off the entire query bill.

**2. Result cache for deterministic queries** — separate
from semantic cache. "List all 10-K filings for AAPL in
the last 5 years" returns the same answer for hours.
Cache by `(query_hash, source_version)`; invalidate on
new ingestion events for the relevant entity.

**3. Tiered indexes by frequency / freshness.**
- **Hot index**: last 30 days, in-memory, OpenSearch with
  higher replica count and faster hardware. Serves 80% of
  queries.
- **Warm index**: 30 days – 1 year, fewer replicas, denser
  packing. Searched when the hot index misses.
- **Cold index**: > 1 year, S3 + Athena, OpenSearch
  Serverless at the lowest tier, or a smaller OpenSearch
  cluster. Searched on archive queries.
A query planner routes to the right tier based on the
date/recency filter in the query. Cuts OpenSearch cost
40–60% on archive-heavy workloads.

**4. Right-size OpenSearch.** The default is to over-provision
OCUs. Use OpenSearch's `Compute Savings Plans` for steady
workloads (up to ~30% off) and autoscale on provisioned
clusters. Review weekly — OCU-hours are a surprisingly
forgiving optimisation target.

**5. Limit rerank to top-N, not all candidates.** Cohere
Rerank 3.5 charges per query, not per document, but going
from 50→25 candidates still halves the latency and lets
us run the rerank call on a smaller machine tier. LLM
rerank should never see more than 20 candidates.

**6. ACL pre-filter on a partitioned index.** A pre-filtered
OpenSearch query scans only the partitions the user can
see. Index documents partitioned by `tenant_id` and
`classification`; queries hit only the relevant partition.
This is both a security and a cost win — restricted docs
have a separate, smaller index; the bulk of analysts never
search it.

### 6.5 Levers at the storage layer

**1. S3 Intelligent-Tiering** for raw and chunk artefacts.
Moves objects to cheaper tiers automatically; no retrieval
penalty for our access pattern. Default it on, no thinking
required.

**2. S3 lifecycle policy**
- Raw artefacts: Standard → Standard-IA (30 days) → Glacier
  Instant Retrieval (90 days) → Glacier Deep Archive
  (1 year for most, 7 years for 17a-4 records, with
  Object Lock preventing early deletion).
- Chunk JSON: Standard-IA from day 30.
- Embeddings cache: Intelligent-Tiering, set to archive
  after 60 days.
- Manifest DynamoDB: PITR enabled; old versions expired
  after 90 days via TTL.

**3. Compress chunks before storage.** Stored chunks are
JSON with long text fields. Gzip at the S3 level + a
compact representation (numbers as numbers, not strings)
halves the size. Athena can read gzip natively.

**4. Deduplicate across sources.** Same news story arriving
from Bloomberg and Reuters: content-hash and keep one.
The manifest stores the alternate source pointers; the
chunk is shared. 5–15% storage savings on news-heavy
workloads.

**5. Right-size OpenSearch storage.**
- Use `index.codec: best_compression` (LZ4 → zstd, 30–50%
  reduction on the index).
- Forcing merge old segments to 1 (`_forcemerge?max_num_segs=1`)
  after rollover reclaims 30–50% disk.
- ISR replica count = 1 (not 2) when RTO allows; saves
  1× storage and 1× write cost.

### 6.6 Levers at the compute / orchestration layer

**1. Lambda + Graviton (arm64).** Up to 20% better
price-performance vs x86_64. Most retrieval Lambdas
are CPU-light; Graviton is a free win. Step Functions
does not care about the underlying compute.

**2. Lambda memory tuning.** Lambda charges per GB-second.
A 512 MB / 200 ms invocation costs the same as a 1024 MB /
100 ms invocation, but the latter often runs faster end-
to-end. Right-size by running `AWS Lambda Power Tuning`
(state machine, free) against representative payloads.

**3. Step Functions Express vs Standard.** Express
Workflows are 100× cheaper per transition but max 5 min
duration and at-least-once. Use Express for ingestion
where we have idempotency, Standard for the long
retrieval jobs where we need exactly-once state semantics.

**4. Step Functions Map with batching + concurrency
limits.** Don't fan out 10k parallel Lambdas to embed
10k chunks; that throttles Bedrock and explodes cost.
Batches of 10 chunks per Lambda + `MaxConcurrency` cap
keeps the request rate inside Bedrock's TPM budget.

**5. S3 Event Notifications → SQS → Lambda** instead of
S3 → Lambda direct. Lets us batch, dedup, and rate-limit
the connector-triggered ingestion. Saves Lambdas and
avoids throttling on burst drops.

**6. Spot for Fargate / EC2 batch jobs.** If a workload
can tolerate interruption (e.g. nightly re-embedding
of a refreshed corpus), run on Spot. 70% discount is
typical.

**7. VPC endpoints** for all AWS-service traffic. Avoids
NAT gateway data-processing charges (~$0.045/GB) and
reduces data transfer costs across services.

### 6.7 Levers at the network / data transfer layer

**1. Inter-AZ traffic** is the surprise line item in many
bills. Pin a request to a single AZ wherever possible
(ALB sticky + Lambda AZ affinity, OpenSearch client to
co-located AZ). Cuts transfer costs by 60–80% for
chatty services.

**2. CloudFront in front of S3** for any user-facing
artefact (PDF previews, generated reports). $0.085/GB
vs $0.09/GB S3 GET, but more importantly, offloads
cacheable content to the edge and reduces origin hits.

**3. Keep tenants regional.** Cross-region replication
is expensive (S3 CRR $0.02/GB + inter-region transfer).
Pinning tenants to a single region avoids the charge
unless a tenant explicitly opts into multi-region DR.

**4. Avoid Bedrock cross-region inference** unless
required for capacity. The cross-region endpoint adds
data transfer cost on every call; only enable it as a
fallback for throttling or capacity, not as the default.

### 6.8 Architectural cost patterns (the interview-grade ones)

**Pattern A: Cascading router**
```
User query
   │
   ▼
[Haiku: classify + rewrite + ACL filter]     ~$0.0001
   │
   ├─ simple → [BM25 + small model]           ~$0.001
   ├─ standard → [hybrid + Cohere + Haiku gen] ~$0.01
   └─ complex → [hybrid + Cohere + LLM rerank
                  + Sonnet gen]               ~$0.05
```
80% of queries land in "standard" at 1/5 the cost of the
"always-Sonnet" baseline. Pattern is generalisable to any
LLM stack.

**Pattern B: Two-stage generation**
For long answers (morning brief, compliance digest), generate
the *outline* with Haiku, the *detail* with Sonnet, only
for the sections the user actually expands. Saves 50–70%
on output tokens.

**Pattern C: Pre-computed common aggregations**
"The 5 biggest holdings in the portfolio" is a query the
system runs thousands of times a day. Pre-compute it on
ingest and serve the cached value. Same pattern for
top-10 filers, latest filings, sector heatmap, etc.
We call these *materialised answers*; they live in DynamoDB
with TTL and refresh on relevant ingest events.

**Pattern D: Cheaper extraction with fine-tuned small models**
Once extraction schemas are stable, fine-tune Haiku (via
Bedrock Custom Model or SageMaker) on 5k–10k labelled
extraction examples. Custom Haiku can match Sonnet on
extraction at 1/10 the cost. Same for classification.

**Pattern E: Smart streaming**
For the UI, start streaming tokens as soon as the first
chunk is ready. From a cost perspective, this doesn't
reduce tokens, but it cuts *perceived* latency, which
matters for the "is this worth the cost?" user question.
Worth pairing with prompt caching: cached system prompt
+ streamed answer = best UX at the lowest per-query cost.

### 6.9 FinOps practices (the governance layer)

Cost reduction without FinOps drifts back within a quarter.
These are the practices that hold the savings:

- **Cost allocation tags** (`Tenant`, `Team`, `SourceSystem`,
  `ModelVersion`) on every resource. Cost Explorer
  dashboards per tenant, per team, per model version.
- **Per-query cost attribution.** Emit a span with
  `{tokens_in, tokens_out, model, embed_dim, rerank_used,
  llm_rerank_used, semantic_cache_hit, cost_usd}` to
  CloudWatch / Langfuse. Tag by tenant and team. This is
  the data source for showback, chargeback, and unit
  economics ("$0.07 per query for analyst team, $0.02
  for the trading desk's cached dashboard").
- **Budgets + anomaly detection** per team, per tenant.
  AWS Budgets with alert at 80%, 100%, 120%. Cost
  Anomaly Detection on by default.
- **Weekly cost review** for the first 3 months, monthly
  thereafter. The same people who own the SLOs own the
  cost; no separate FinOps team in the early days.
- **Unit economics dashboard** that shows cost-per-query,
  cost-per-ingested-document, cost-per-tenant, and the
  trend lines. Publicly visible inside the team. Targets
  written down (e.g. "≤ $0.05 per query at 10k/day").
- **Architectural guardrails in CI.** PRs that add a new
  Bedrock call, increase top-k, or disable a cache have
  to update the cost model in the same PR. The eval
  harness runs a cost check on a sample of golden queries
  and fails the build if per-query cost regresses > 10%.
- **Quarterly "cost day"** — one person-day dedicated to
  rerunning the cost model, looking at the dashboards,
  and shipping one optimisation. This is the single best
  predictor of long-term cost discipline.

### 6.10 Cost-reduction order of operations

When the bill is too high, work the levers in this order.
Each tier is a bigger lift but bigger payoff.

1. **Tier 1 (a few hours of work)**: enable prompt caching,
   cap `max_tokens`, set Bedrock batch for async jobs, switch
   Lambda to Graviton, enable S3 Intelligent-Tiering, set
   OpenSearch `best_compression`. Expected savings: 30–50%.
2. **Tier 2 (a sprint)**: build semantic cache, add
   model routing, tune top-k and rerank top-N, set up
   per-query cost telemetry, enable tiered indexes. Expected
   savings: another 20–30%.
3. **Tier 3 (a quarter)**: fine-tune a small model for
   extraction, build materialised answers, restructure
   indexes by tenant and partition, implement prompt
   compression, renegotiate OpenSearch with reserved
   capacity. Expected savings: another 15–25%.
4. **Tier 4 (ongoing)**: cost per query keeps dropping as
   traffic patterns stabilise, eval harness catches
   regressions, and the team builds cost awareness into
   every PR.

The interview-grade insight is that **the biggest savings are
structural, not tactical** — semantic cache, model routing,
and prompt caching together routinely halve the bill. Tuning
top-k from 20 to 5 is rounding error by comparison.

---

## 7. Provenance

Provenance is the *least flashy* part of the design and the *most
expensive* to retrofit. In financial services it is also the part
the regulator will ask about first. The bar is not "we logged it
somewhere" — it is "we can reconstruct, for any answer the system
has ever given, exactly which document, page, extraction, model
version, and prompt produced it, and we can prove it was not
tampered with afterwards."

### 7.1 What provenance means at each layer

| Layer            | Provenance question                                              | Captured where |
|------------------|-------------------------------------------------------------------|----------------|
| Source artefact  | Where did this file come from, when, and from whom?               | Source registry + connector logs + S3 metadata (Object Lock) |
| Raw bytes        | Is this byte sequence the original? Has it been altered?         | S3 Object Lock (WORM) + sha256 in manifest |
| Canonical text   | What OCR/transcription produced this text, at what confidence?    | Textract/Transcribe job id in chunk metadata |
| Extraction       | Which model + prompt + schema produced these structured facts?    | Chunk metadata; Bedrock invocation id |
| Chunking         | Which strategy + boundaries produced this chunk?                   | Chunk metadata (chunk_id, parent_id, strategy) |
| Embedding        | Which model, dim, version produced this vector?                   | Vector record metadata; embedding model id in manifest |
| Index entry      | When did this chunk enter the index, in which version?            | OpenSearch version + DynamoDB index pointer |
| Retrieval        | Which query, planner, filters, recall set produced this candidate? | Retrieval trace (OTel spans + Langfuse) |
| Generation       | Which model + prompt version produced this answer?                | Generation span (OTel) + Langfuse trace |
| Citation         | Which chunk(s) ground this exact claim?                           | Citation object in answer + manifest lookup |
| Delivery         | Who saw this answer, when, in what UI?                            | API Gateway access log + CloudTrail |

**The "manifest" in DynamoDB is the spine of all of this.** Every
other store is a projection of the manifest. The manifest row is
the join key that lets an auditor reconstruct the full lineage of
any answer in one query.

### 7.2 The provenance envelope on every chunk

Every chunk, every embedding, every cited fact carries the same
envelope-shaped metadata:

```json
{
  "chunk_id": "sha256:9f0a…",
  "doc_id": "doc_8c12",
  "doc_version": 3,
  "source": {
    "type": "edgar",
    "url": "https://www.sec.gov/Archives/edgar/data/320193/.../aapl-20240928.htm",
    "fetched_at": "2025-10-30T14:22:01Z",
    "fetched_by": "connector-edgar-lambda:v2.4.1",
    "connector_run_id": "edgar-2025-10-30-014"
  },
  "raw": {
    "s3_uri": "s3://rag-raw-us-east-1/edgar/320193/2025/10/30/9f0a….htm",
    "sha256": "9f0a…",
    "bytes": 4_312_889
  },
  "pre_process": {
    "tool": "textract",
    "job_id": "abc-123",
    "confidence_avg": 0.97
  },
  "extraction": {
    "model_id": "anthropic.claude-sonnet-4-5-20250929-v1:0",
    "prompt_version": "extract.v7",
    "schema_version": "facts.v3",
    "invocation_id": "bedrock-inv-…",
    "extracted_at": "2025-10-30T14:25:13Z"
  },
  "chunking": {
    "strategy": "parent_child",
    "parent_chunk_id": "sha256:1a2b…",
    "start_char": 12_345,
    "end_char": 13_201
  },
  "embedding": {
    "model_id": "amazon.titan-embed-text-v2:0",
    "dim": 1024,
    "vector_id": "vec_8c12_chunk_3"
  },
  "acl": {
    "tenant_id": "fs-tenant-a",
    "classification": "confidential",
    "allowlist_teams": ["research", "compliance"]
  },
  "lineage": {
    "supersedes": ["sha256:7z9y…", "sha256:5q8w…"],
    "superseded_by": null,
    "as_of": "2025-10-30T14:25:13Z"
  }
}
```

Every store that holds a projection of this chunk (OpenSearch
document, Aurora row, Neptune node) carries the same envelope as
a sub-object. The cost of carrying it is small; the cost of
*not* having it during an audit is enormous.

### 7.3 Lineage: the manifest as the source of truth

DynamoDB table `rag_manifest` (one row per *document*, not chunk):

```
PK: doc_id                       # sha256 of the canonical text
   version                       # monotonic int
   status: active | superseded | withdrawn | gdpr_erased
   content_type, source, source_uri
   raw_s3_uri, canonical_s3_uri
   sha256
   parent_doc_id                 # if re-extraction of same source
   supersedes                    # list of doc_ids this replaces
   superseded_by                 # current head
   acl_tags
   tenant_id
   as_of                         # when this version became "the answer"
   ttl
   created_at, created_by
```

Retrieval uses the manifest to know **which version of a doc is
"live"** for citation. The previous version stays indexed (so a
"what did we believe on date X?" query still works) but is marked
`status: superseded` and ranked below the current version.

When a doc is re-ingested, we don't blow away the old version. We:
1. Write the new manifest row with `supersedes: [old_id]`.
2. Update the old row's `superseded_by` to point at the new one.
3. Re-extract, re-chunk, re-embed only the diff (content-addressed
   chunks; unchanged chunks are reused — see §6.3).
4. OpenSearch index is updated via a soft delete on old chunks
   (filter on `as_of`) and a write of new ones.
5. The old chunks' provenance envelopes are preserved in S3;
   they're just excluded from the active candidate set by default.

This is the difference between *immutable raw* and *mutable answer*:
the bytes never change, but the system's "current belief" can
evolve, and both states are queryable.

### 7.4 Citation in the answer

Every answer is an *answer + citations*, not just an answer. The
citation is not a footnote — it is a first-class object the UI
must render and the LLM must be trained (via prompt + eval) to
produce.

**Citation object:**
```json
{
  "claim": "Apple reported Q3 2024 net income of $21.4B.",
  "chunk_id": "sha256:9f0a…",
  "doc_id": "doc_8c12",
  "source": {
    "uri": "https://www.sec.gov/Archives/edgar/data/320193/.../aapl-20240928.htm",
    "page": 42,
    "section": "Consolidated Statements of Operations"
  },
  "extracted_at": "2025-10-30T14:25:13Z",
  "model_id": "anthropic.claude-sonnet-4-5-20250929-v1:0",
  "grounding_score": 0.94,
  "freshness_days": 12
}
```

**Patterns:**
- **Inline citation tags** in the answer text: `[AAPL Q3 2024
  net income¹]`. UI renders hover/click → citation panel.
- **Per-claim citation** (not per-answer): a long answer has many
  claims, each with its own citation. This is what the auditor
  needs; "the answer cited doc X" is not enough.
- **Citation coverage check**: after generation, a cheap model
  scores each claim against its cited chunk. If coverage < 70%
  on a claim, the system re-generates with a refined query
  (§2.3 self-correction loop). Coverage < 100% on a fact-lookup
  query is a *failed* answer; we don't return it.
- **No citation = no answer.** A claim the LLM cannot ground in a
  retrieved chunk is refused or flagged as low-confidence. The
  user sees "I don't have a source for that" instead of a
  hallucinated figure.

### 7.5 Provenance-aware retrieval

Provenance isn't only post-hoc — it shapes retrieval itself.

**Trust signals baked into rerank:**
- **Source tier**: primary issuer filings (10-K, prospectus) >
  reputable secondary (Bloomberg, Reuters) > user-generated
  (analyst notes) > scraped web. Embed as a `source_tier` field
  and let the reranker weight it.
- **Extraction confidence**: Textract/Transcribe emit per-region
  confidence. Chunks below a threshold are marked
  `low_confidence: true`; reranker demotes them or surfaces a
  warning in the UI.
- **Freshness**: a chunk that has been superseded is demoted
  unless the user explicitly asked "as of [date]".
- **Model version**: chunks extracted by an older model version
  can be flagged. Useful when the eval harness shows a regression
  on a model upgrade; we can fall back to the older model's
  chunks for the affected doc type until they're re-extracted.

**Practically:** rerank features include
`[semantic_score, bm25_score, acl_match, source_tier,
extraction_confidence, freshness_days, model_version_match]`.
Cohere Rerank 3.5 supports custom features via metadata; or we
run a small LLM rerank with these in the prompt.

### 7.6 Tamper-evident audit trail

Capturing provenance is necessary but not sufficient — the audit
trail must be tamper-evident. Several layers:

**1. S3 Object Lock (Compliance mode)** on the raw artefact bucket.
The bytes cannot be deleted or overwritten, even by root, until
the retention period expires. This is the foundation.

**2. S3 Object Lock on a dedicated audit log bucket.** Every
provenance event (ingest completed, chunk indexed, query served,
answer delivered) is written as an append-only JSON file with
Object Lock. Same retention as 17a-4 (7 years).

**3. CloudTrail Lake** for AWS API-level events (who touched
which bucket, which KMS key was used, which IAM role invoked
which Bedrock model). CloudTrail Lake stores events in an
immutable, queryable SQL log. The auditor's first stop.

**4. Cryptographic chaining of the audit log.** Each audit event
includes `prev_event_hash`, forming a hash chain. A Lambda
verifier runs hourly; if any link is broken, page the security
team. This catches insider tamper attempts that bypass S3 ACLs
(e.g. someone with `s3:PutObject` rewriting an old log file).
For a small workload, use `aws-kms` signed entries; for high
volume, use a QLDB-style ledger DB or a third-party (e.g.
Constellation,immudb).

**5. Per-tenant KMS keys + signed answers.** For high-stakes
answers (e.g. compliance memos that will be re-read in court),
the (answer, citations, model_id, prompt_version) tuple is
hashed and signed with the tenant CMK. The signature is stored
alongside the answer. Anyone reading the answer later can verify
it was not retroactively edited. This is overkill for analyst
chat; cheap insurance for regulated workflows.

**6. AWS Audit Manager** for automated evidence collection.
Pre-built frameworks (e.g. for SOC 2, PCI, ISO 27001) can pull
RAG-specific evidence (Object Lock retention, KMS rotation,
IAM policy diff, Guardrails log) into the audit package.

### 7.7 "As-of" queries — time travel for audit

The most important question in a financial audit is *"what did
the system know, and say, on date X?"* The architecture supports
this as a first-class query.

**Implementation:**
- Every chunk, every manifest row, every index entry has an
  `as_of` timestamp and a `superseded_by` pointer.
- The OpenSearch index is a single version; queries can filter
  `as_of <= :date AND (superseded_by IS NULL OR superseded_by > :date)`.
- Pre-aggregated snapshots: every Sunday, the manifest + index
  are snapshotted to S3 (OpenSearch snapshot, DynamoDB export to
  S3). A "what did the index look like on 2025-06-15?" question
  is answered by restoring that snapshot into a separate read-
  only OpenSearch cluster (or using OpenSearch's time-based
  queries) and running the audit query against it.

**Auditor workflow:**
1. "Show me every answer user U received on 2025-06-15." →
   CloudTrail Lake / audit log → list of answer ids.
2. "For each answer, what documents were cited?" → answer →
   citations → manifest → S3 URIs of the raw files at that
   point in time (Object Lock guarantees the bytes match).
3. "Were those documents authoritative on 2025-06-15?" →
   manifest as_of + supersession chain → yes/no per citation.
4. "What model produced the answer?" → trace metadata.
5. "Has the system since revised its view?" → current manifest
   for the same docs → diff.

The whole audit query is one SQL over CloudTrail Lake + a few
manifest lookups. The architecture is what makes this possible
in minutes instead of weeks.

### 7.8 Lineage-driven operations

Provenance pays for itself the first time something goes wrong.

**GDPR right-to-erasure.** Manifest row's status flips to
`gdpr_erased`; downstream projections are deleted; original
artefact's Object Lock is *not* lifted (regulator retention
wins over GDPR in most jurisdictions; consult counsel); the
audit log records the erasure event with its legal basis. The
manifest knows every store the chunk was in, so the delete is
fan-out, not a hunt.

**Supersession of stale answers.** When a 10-K is restated, the
old chunks are marked superseded; any answer that cited them
shows a "stale — see restatement" banner on subsequent
retrievals. The UI never silently serves a withdrawn figure.

**Re-embedding after model upgrade.** When we upgrade Titan v2 →
v3, we re-embed in the background. The provenance envelope
records the embedding model per chunk, so a "what was this chunk
embedded with?" query is one manifest lookup, not an index scan.
A/B tests use `embedding.model_id` as a facet.

**Drift detection on external sources.** A nightly job re-fetches
the source URL of every active doc; if the bytes differ from
the stored sha256, an alert fires. The system catches a
counterparty quietly editing a public filing (it happens).

**Recall on bad extraction.** When the eval harness flags a
model regression on a doc type, the manifest lets us identify
every chunk extracted with the bad model version, re-extract
them with the new model, and swap them in. The lineage is
preserved (we don't overwrite — we supersede).

### 7.9 Provenance signals exposed to the user

The user — analyst, compliance officer, trader — needs to see
provenance, not just the system. UI patterns:

- **Citation panel** on every claim: source, page, date, model.
- **"As of" date** on every answer: the system tells the user
  which version of which document is reflected.
- **Confidence indicator**: low-extraction-confidence chunks
  get a ⚠️ in the citation panel; the user can decide to trust
  or re-verify.
- **Stale banner**: if a cited doc has been superseded since
  the answer was generated, the UI shows "this answer reflects
  the version as of [date]; a newer version exists".
- **Source tier icon**: filing / news / email / web, so the
  user knows the epistemic weight of the citation.
- **"Show me the source"** click → renders the PDF page or the
  email header inline, with the relevant region highlighted
  via the chunk's char offsets.

The "show me the source" affordance is the *single most important
trust feature* of the whole UI. Without it, citations are
decorative. With it, the user can verify in one click and the
system's job is to make that verification easy.

### 7.10 Interview talking points — provenance

If the conversation turns to provenance, regulation, or audit,
land these:

1. **Provenance is captured at every layer, not bolted on.** The
   manifest is the spine; every chunk, every embedding, every
   citation carries the same envelope (source, model, version,
   timestamps, ACL, supersession chain).
2. **Citations are per-claim, not per-answer, and the system
   refuses ungrounded claims.** Coverage check; no source, no
   answer.
3. **The audit trail is tamper-evident**: S3 Object Lock on raw
   + audit log, CloudTrail Lake for API events, hash-chained
   audit log for insider-tamper protection, signed answers for
   high-stakes workflows.
4. **"As-of" queries are first-class.** Any answer can be
   reconstructed for any date. Snapshots + supersession chain
   make this minutes, not weeks.
5. **Provenance shapes retrieval**, not just audit. Source tier,
   extraction confidence, freshness, and model version are
   rerank features; superseded chunks are demoted unless
   explicitly requested.
6. **Lineage-driven operations** (GDPR delete, supersession,
   re-embedding, drift detection) are tractable because the
   manifest is the source of truth and every store is a
   projection. The first time something goes wrong, the design
   pays for itself.

---

## 8. Interview talking points — the 90-second version

If the interviewer says "summarise the architecture", I want to
land these beats:

1. **Ingestion and retrieval are decoupled, with very different SLOs.**
   Ingestion is a Step Functions pipeline that does format-specific
   pre-processing, classifies, extracts with a Bedrock LLM using
   JSON Schema / Tool Use, chunks by document type, embeds with
   Titan/Cohere, reranks with Cohere, and fans out to OpenSearch
   (vector + BM25), Aurora, Neptune, S3, and a DynamoDB manifest.
2. **Retrieval is a multi-stage funnel** — query planning (intent,
   rewrite, HyDE, multi-query, structured facets), ACL pre-filter,
   hybrid BM25 + k-NN with reciprocal rank fusion, two-stage rerank
   (Cohere + LLM), and grounded generation with citations. Long
   queries run as Step Functions async jobs.
3. **Stores are polyglot by query shape**, not by team preference.
   Vector for semantic, BM25 for exact/regulatory, graph for
   relations, relational for facts, object store for the artefact.
4. **Cross-cutting concerns are first-class, not afterthoughts:**
   - Reliability — multi-AZ, circuit breakers, DR runbooks
   - Observability — OTel, Langfuse, nightly eval harness
   - Regulation — S3 Object Lock for 17a-4, audit trail for SOX,
     the LLM treated as a model under SR 11-7 governance
   - Permission — ABAC enforced at every store, negative tests
     in CI, no path that bypasses ACL
   - Resilience — declared RPO/RTO per tier, tested quarterly
   - Provenance — every layer carries lineage; "as-of" queries
     are first-class; audit trail is tamper-evident
   - Cost — design constraint from day one, not a FinOps tax
5. **The system has a "fully managed" and a "custom" tier.**
   Bedrock Knowledge Bases + Agents is the right starting point.
   The architecture here is what you graduate to when you need
   custom chunking, fine-grained ACL, multi-tenant isolation,
   cost discipline at scale, or eval-driven quality controls.

---

## 9. Open questions to surface (shows senior thinking)

- **Do we need a graph store on day one?** Many FS RAG systems
  ship without Neptune and add it when the first "show me
  everything related to issuer X" question arrives. I'd
  defer until the first concrete use case.
- **Build vs buy for embeddings.** Bedrock Titan v2 is fine for
  a first cut. If retrieval eval shows we need domain
  embeddings (financial jargon, ticker symbols), plan a
  fine-tuning cycle on Bedrock Custom Model or a self-hosted
  model on SageMaker. Don't over-engineer on day one.
- **Real-time vs batch freshness.** Decide explicitly per source:
  market data is seconds; filings are hours; internal docs are
  days. The pipeline's max fan-in and Step Functions concurrency
  budgets are set by this decision.
- **Cost ceiling.** A mid-size FS RAG serving 10k queries/day with
  hybrid retrieval + Cohere rerank + Sonnet generation lands
  around $0.05–0.15 per query. The biggest cost levers are
  (1) prompt caching, (2) LLM rerank budget, (3) embedding
  dimensionality. Always have a cost-per-query dashboard.
- **Eval before product.** The eval harness and golden set
  should land in sprint 1, not sprint 10. Without it, every
  later decision is uninformed.

---

## 10. One-page diagram (text)

```
                            ┌───────────────────────────────────────────┐
                            │              SOURCES                       │
                            │ SFTP, SharePoint, HTTP, Email, S3 drops,  │
                            │ Kinesis, DMS-CDC, news, audio, webhooks   │
                            └─────────────────────┬─────────────────────┘
                                                  │ (connectors)
                                                  ▼
                            ┌───────────────────────────────────────────┐
                            │  INGEST (Step Functions, per-doc)          │
                            │  Validate → Pre-process → Classify →       │
                            │  Extract (Bedrock + JSON Schema) →         │
                            │  Chunk (doc-type aware) → Embed →          │
                            │  Rerank (Cohere) → Enrich →                │
                            │  Fan-out + Emit event                      │
                            └────┬──────────┬──────────┬────────┬────────┘
                                 │          │          │        │
                                 ▼          ▼          ▼        ▼
                            ┌────────┐ ┌────────┐ ┌────────┐ ┌────────────┐
                            │  S3    │ │OpenSrch│ │ Aurora │ │  Neptune   │
                            │  WORM  │ │vec+BM25│ │  facts │ │  entities  │
                            └───┬────┘ └───┬────┘ └───┬────┘ └─────┬──────┘
                                │          │          │            │
                                └──────────┴────┬─────┴────────────┘
                                               │ (DynamoDB manifest)
                                               ▼
                            ┌───────────────────────────────────────────┐
                            │  RETRIEVE (sync + async, same core)       │
                            │  Plan → ACL filter → Hybrid recall (RRF)  │
                            │  → Rerank (Cohere → LLM) → Generate       │
                            │  (Bedrock, prompt-cached, streamed)       │
                            │  → Verify + cite                          │
                            └─────────────────────┬─────────────────────┘
                                                  │
                ┌────────────────┬─────────────────┼─────────────────┐
                ▼                ▼                 ▼                 ▼
            ┌──────┐         ┌──────┐          ┌──────┐          ┌──────┐
            │  UI  │         │Agent │          │Event │          │ Cron │
            │(sync │         │(sync │          │(async│          │(async│
            │ +SSE)│         │/tool)│          │ fan) │          │ batch│
            └──────┘         └──────┘          └──────┘          └──────┘

  Cross-cutting everywhere: OTel/Langfuse observability, IAM/ABAC at every
  store, KMS per tenant, S3 Object Lock + CloudTrail Lake for audit, multi-
  AZ/multi-Region, circuit breakers, eval harness, prompt caching, Guardrails.
```
