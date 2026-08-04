# Financial Data Types — and How to Serve Each One to an Agent
*Compiled Aug 2026. Organized by data class, not by vendor. Source tiers at the end.*

---

## 0. Four rules that decide most of the architecture

**1. Never RAG a number you can query.**
Format alone moves accuracy by two orders of magnitude. XBRL US measured **scaling errors of 8.16% from text, 5.81% from HTML, and 0.11% from XBRL** — same facts, same models, different serving format. If a value exists in a structured source, retrieving prose that mentions it is malpractice.

**2. Resolve identity before you retrieve.**
One equity is a ticker in the OMS, a CUSIP in settlement, an ISIN in global reporting, and a FIGI in market data. Identifier resolution is a **deterministic pre-step tool**, never something the model infers. Standard architecture: an internal canonical ID as primary key, with all external identifiers mapped to it.

**3. Return handles, not payloads.**
A single equity can generate ~10,000 ticks per minute. Tables are not context. The agent gets a query tool and a dataframe reference; the data never enters the window.

**4. Every value carries `(value, source, knowledge_date, effective_date)`.**
Two time axes, always. Without them, no backtest, no compliance reconstruction, no "why did it say that in March."

**One more, empirical:** Snowflake benchmarked ~23,000 SEC filings (5 years, top 1,000 companies, ~3.2M chunks at 1,800 tokens/300 overlap) and found **chunking and retrieval strategy matter more to output quality than model capability — even with long-context models.** Long context does not rescue bad data serving.

---

## 1. The taxonomy

| # | Data class | Shape | Update rate | Serving pattern | Primary trap |
|---|---|---|---|---|---|
| 1 | Real-time market data | Streaming ticks/quotes/book | ms | **P3** snapshot tool | Streaming into the context window |
| 2 | Historical prices & bars | Large time-series | Daily/batch | **P4** code over handles | Row dumps; unadjusted series |
| 3 | Positions, trades, books of record | Relational, internal | Intraday | **P2** semantic layer | Text-to-SQL guessing grain |
| 4 | Risk & analytics output | Derived tabular | Batch | **P2** + provenance of the *model* | Treating output as ground truth |
| 5 | Security master & identifiers | Reference | Slow | **P1** resolver | Letting the LLM map tickers |
| 6 | Corporate actions & calendars | Event reference | Event-driven | **P1** + adjustment service | Silent split/dividend errors |
| 7 | Legal-entity & counterparty ref | Graph (LEI, D-U-N-S) | Slow | **P1** + graph traversal | Name-string matching |
| 8 | Fundamentals / XBRL | Structured facts | Quarterly + restatements | **P5** as-of API | as-reported vs standardized confusion |
| 9 | Estimates & consensus | Panel, revision-heavy | Continuous | **P5** vintage-aware | Look-ahead via revised consensus |
| 10 | Macro / economic series | Time-series with **vintages** | Scheduled + revised | **P5** vintage API | Using final values in a backtest |
| 11 | Filings & disclosures | Long documents + tables | Event-driven | **P6** typed graph + citation | Flat chunking; chunked tables |
| 12 | Transcripts & expert calls | Long text, speaker-structured | Event-driven | **P6** + speaker/section metadata | Losing Q&A attribution |
| 13 | Research & internal knowledge | Mixed docs | Continuous | **P6** + **P7** entitlement | MiFID II research redistribution |
| 14 | Client / KYC / PII | Records + documents | Event-driven | **P7** tokenized, purpose-bound | PII crossing the model boundary |
| 15 | Communications & surveillance | Chat/email corpora | Continuous | **P7** read-only, isolated | Untrusted content → injection |
| 16 | Alternative data | Wildly heterogeneous | Varies | **P7** + MNPI gate | MNPI contamination |

---

## 2. Class-by-class

### Family A — High-volume structured (never goes in context)

**1. Real-time market data.** REST for snapshot retrieval; WebSocket/SSE/FIX for streams. An agent loop runs 10²–10⁴ ms; the stream runs faster than the agent can think.
→ **Serve:** a `get_quote(as_of)` / `get_book_snapshot()` tool that returns a *point*, plus a subscription managed *outside* the agent that writes to a store the agent queries. Event-driven pipeline feeds the store; the agent never subscribes.
→ **Anti-pattern:** piping a WebSocket into the model. It's a cost incident and a correctness one.

**2. Historical prices & bars.** The trap is adjustment: split- and dividend-adjusted series change retroactively, so "the same query" returns different numbers over time.
→ **Serve:** code execution against a dataframe handle, with adjustment policy an explicit parameter (`adjusted=True/False`, `adjustment_date`). Return aggregates, not rows.

**3. Positions, transactions, books of record.** This is where **semantic layer beats text-to-SQL** decisively. Text-to-SQL re-infers joins, grain, and filters from column names on every query — flexible and fragile. A semantic layer solves joins, grain, and metric math **once**, in the data team's hands, and emits deterministic SQL.
→ **Serve:** governed metrics exposed over MCP. "Net exposure" should be one definition, not a guess.
→ The regulated-enterprise consensus for 2026: **RAG as the retrieval tier, semantic layer as the answering tier** — RAG fetches the policy or constraint, the semantic layer computes the number under it.

**4. Risk & analytics output.** Factor exposures, VaR, sensitivities, curves. These are *model outputs*, not facts.
→ **Serve:** with the model version, parameterization, and run timestamp attached. An agent that cites a VaR without the model run ID has produced an unauditable claim.

### Family B — Reference data (small, slow, and the foundation of everything)

**5. Security master & identifiers.** ISIN (12-char, country-prefixed), CUSIP (9-char, US/Canada), FIGI (12-char, global), plus tickers and vendor RICs.
→ **Serve:** `resolve_instrument(any_identifier) → canonical_id` as a mandatory first call, returning all mappings plus validity dates. Ticker reuse across time is a real hazard — resolution must be as-of.
→ **Anti-pattern:** letting the model map "AAPL" to an instrument. It will be right 99% of the time, which is exactly the failure profile you can't audit.

**6. Corporate actions & calendars.** Splits, dividends, M&A, symbol changes, exchange holidays.
→ **Serve:** an adjustment service the agent *calls*, never re-implements. Expose trading calendars as a tool so date arithmetic isn't hallucinated.

**7. Legal-entity & counterparty reference.** Corporate hierarchies, beneficial ownership, LEI, D-U-N-S.
→ **Serve:** as a graph with traversal tools (`parent_of`, `subsidiaries_of`, `ultimate_owner`), not as flattened rows. AI-assisted MDM reportedly cuts manual stewardship ~31% and improves entity-resolution accuracy ~21%.
→ **Why it matters:** every join downstream is wrong if this is wrong, and it fails silently.

### Family C — Structured with time-semantics traps

**8. Fundamentals / XBRL.** Two distinct products: **as-reported** (what the filer filed, quirks included) and **standardized** (mapped to a common syntax for cross-company and cross-period comparison). Variance between vendors comes from restatements, data-quality issues, and extraction methodology. XBRL US now maintains **196 automated DQC checks** for US GAAP/IFRS filers — a useful signal of how much dirt is in as-filed data.
→ **Serve:** an as-of API that answers "what was reported for FY23 Q2 *as known on* date X," with restatement lineage rather than in-place overwrite. Make as-reported vs standardized an explicit, required parameter — never a default.
→ SEC EDGAR's XBRL/Frames API and XBRL US's API are the free baselines; XBRL US also ships a no-code **MCP AI Connector** for as-filed data.

**9. Estimates & consensus.** Consensus is revised constantly, and revised history is the single easiest way to leak the future into a backtest.
→ **Serve:** vintage-aware — "consensus as it stood on date X." Same rule as macro.

**10. Macro / economic series.** GDP, CPI, employment all get revised. **Vintages are the whole game.**
→ **Serve:** a vintage API (`get_series(id, vintage_date)`). If your macro store overwrites on revision, every historical agent evaluation is invalid.

### Family D — Long-form unstructured

**11. Filings & disclosures.** The dominant finding of 2026: **stop chunking tables.** Rather than treating filings as flat text, invest in structured formats — XBRL and HTML sections — as a **typed graph** before scaling embeddings, because *path-finding beats guessing similar paragraphs*.
→ **Serve:** layout-aware parsing → section/table graph → hybrid retrieval with **per-field citations grounded to specific table cells**. Best-in-class extraction runs an **agentic self-verification loop** (extract → verify → correct) rather than single-pass.
→ Prefer **navigation over retrieval** where structure exists: an agent that can jump to "Item 7A" beats one that searches for paragraphs resembling "market risk."

**12. Transcripts & expert calls.** Structure is speaker + section (prepared remarks vs Q&A) and it's semantically load-bearing — a CFO hedging in Q&A is not the same fact as guidance in prepared remarks.
→ **Serve:** preserve speaker, role, timestamp, and section as retrievable metadata; return verbatim excerpts linked to source.

**13. Research & internal knowledge.** Sell-side research is the most contractually restricted content in the building (MiFID II unbundling, per-seat entitlements).
→ **Serve:** entitlement-gated retrieval with redistribution rules enforced at the tool boundary, and derived-output restrictions carried into whatever the agent produces.

### Family E — Restricted and adversarial

**14. Client / KYC / PII.** Crossing a model-provider boundary with KYC data is a regulated transfer.
→ **Serve:** tokenize or redact before the model sees it; resolve real values only in the deterministic layer. Bind access to purpose, not just role. Strong driver toward VPC/on-prem and open-weights — more than cost is.

**15. Communications & surveillance.** Chat and email corpora are simultaneously the highest-value internal source and **untrusted input**.
→ **Serve:** read-only, in an isolated context, with no tool-calling authority downstream. This is a live prompt-injection surface where the "act" leg can move money.

**16. Alternative data.** Card panels, geolocation, web scrape, expert networks.
→ **The distinctive risk is MNPI.** The SEC's evolving interpretation of what constitutes MNPI in alt data creates real legal uncertainty; investment firms now expect detailed **data provenance** on every source, including paid subscriptions, surveys, industry conversations, and scraping. One notable compliance suggestion: a deliberate **training/knowledge cutoff**, since staler data is less likely to embed MNPI.
→ **Serve:** through a compliance-gated proxy with provenance metadata mandatory per record, and an explicit MNPI classification per source.
→ **Governance failure mode to name:** *an agent that can't reach a database through the sanctioned MCP server will scrape the web app for the same data* — or a developer builds a shortcut connector that routes around governance entirely. Also note EDPB **Guidelines 03/2026** (adopted 7 July 2026), the first comprehensive GDPR framework for large-scale scraping for generative AI.

---

## 3. The serving-pattern catalogue

| Pattern | What it is | Use when | Failure it prevents |
|---|---|---|---|
| **P1 Resolver** | Deterministic ID → canonical ID, as-of | Any reference lookup | Silent wrong-entity joins |
| **P2 Semantic layer** | Pre-defined metrics/dimensions; layer emits SQL | Governed internal tabular data | Re-guessed grain and joins |
| **P3 Snapshot tool** | Point-in-time read of a live stream | Real-time anything | Streams in the context window |
| **P4 Handle + code** | Return a dataframe reference; agent writes code | Large result sets | Token blowup, arithmetic errors |
| **P5 As-of / vintage API** | Query by knowledge date | Fundamentals, estimates, macro | Look-ahead bias, invalid replay |
| **P6 Typed graph + cited extraction** | Layout-aware parse → section/table graph, cell-level citations | Long documents | Chunked tables, unattributable numbers |
| **P7 Entitlement-gated proxy** | User identity propagated, purpose-bound, logged | Licensed, PII, restricted, alt data | Redistribution breach, MNPI, injection |

**Selection rule:** *Is the truth a number in a governed store, or a statement in a document?* Number → P2/P4/P5. Statement → P6. Identity → P1. Live → P3. Restricted → P7 wrapping whichever applies.

---

## 4. Build order

1. **P1 resolver + security master.** Nothing above it is trustworthy without it. Cheapest, highest leverage, always skipped.
2. **P5 time semantics** on fundamentals, estimates, macro. Retrofitting bitemporality later is the multi-quarter surprise.
3. **P7 entitlement proxy** as the single egress point. One gateway, not N vendor integrations.
4. **P2 semantic layer** on the top ~20 metrics people actually ask for. Not the whole warehouse.
5. **P6 document pipeline** — layout-aware parse and typed graph before you scale embeddings.
6. **P3/P4** for market data last; it's the most visible and the least likely to be the bottleneck.

**The test for any of these:** can the agent produce a number, and can you trace that number to a source cell, a knowledge date, and an entitlement check? If not, the data isn't agent-ready regardless of how good the retrieval looks in a demo.

---

## Sources

**Tiers:** [P] primary/official · [R] arXiv/peer-reviewed · [E] engineering writeup · [S] secondary/vendor.

**Structured data & serving patterns**
- [dbt, *Semantic Layer vs. Text-to-SQL: 2026 Benchmark Update*](https://docs.getdbt.com/blog/semantic-layer-vs-text-to-sql-2026) [P/E] — the joins/grain/filters-solved-once argument.
- [Cube, *Semantic Layer for AI Agents (2026)*](https://cube.dev/articles/semantic-layer-for-ai-agents-2026) [S] · [ColRows, *RAG vs. Semantic Layer (2026)*](https://colrows.com/blogs/rag-vs-semantic-layer/) [S] — source of "RAG as retrieval tier, semantic layer as answering tier."
- [arXiv 2606.31041, *A Semantic-Layer-Mediated Agent for NL-to-SQL over Heterogeneous Enterprise Databases*](https://arxiv.org/pdf/2606.31041) [R]
- [arXiv 2602.21480, *Both Ends Count! How Good are LLM Agents at "Text-to-Big SQL"?*](https://arxiv.org/pdf/2602.21480) [R]

**Market data delivery**
- [Coinpaprika, *Real-time data for AI agents: SSE, WebSocket, and streaming patterns*](https://coinpaprika.com/education/real-time-data-for-ai-agents-sse-websocket-and-streaming-patterns/) [E]
- [Qveris, *Market Data API for AI Agents: 7 Best Providers (2026)*](https://qveris.ai/guides/market-data-api-for-ai-agents/) [S] — REST-for-snapshot / WebSocket-or-FIX-for-stream split; the ~10,000 ticks/minute figure.
- [OpenWeb Solutions, *Real-Time Trading Platform Architecture: AI & Event Streaming in 2026*](https://openwebsolutions.in/blog/real-time-trading-platform-architecture-ai-event-streaming/) [S]

**Fundamentals / XBRL**
- [XBRL US, *Getting XBRL in LLMs for as-filed research*](https://xbrl.us/xbrl-and-llms/) [P] — **the 8.16% / 5.81% / 0.11% scaling-error comparison**, and the no-code MCP AI Connector. Strongest single data point in this document.
- [XBRL US, *AI is smarter with structured standardized data*](https://xbrl.us/ai-smarter-with-structured-data/) [P] · [XBRL API](https://xbrl.us/home/priorities/use/xbrl-api/) [P] — 196 DQC automated checks.
- [SEC, *EDGAR Application Programming Interfaces*](https://www.sec.gov/search-filings/edgar-application-programming-interfaces) [P]
- [Intrinio, *Understanding XBRL Financial Statements & Filings*](https://intrinio.com/blog/normalized-xbrl-data) [S] — as-reported vs standardized; sources of vendor variance.
- [arXiv 2605.29586, *FinVerBench: Benchmark Validity and Calibration in LLM Financial Statement Verification*](https://arxiv.org/pdf/2605.29586) [R]

**Identifiers & security master**
- [Intrinio, *Modern Security Master Architecture: Unifying Ticker, CUSIP, ISIN and FIGI at Scale*](https://intrinio.com/blog/modern-security-master-architecture-unifying-ticker-cusip-isin-and-figi-data-at-scale) [S] — internal canonical ID pattern.
- [Khraisha, *Financial Data Engineering Series: Financial Identifiers*](https://tamer-khraisha.medium.com/financial-data-engineering-series-3-n-financial-identifiers-99a32a6eb321) [E]
- [LUSID/FINBOURNE, *Understanding instrument identifiers*](https://support.lusid.com/docs/understanding-instrument-identifiers) [P] — auto-resolution across source identifiers.

**Documents**
- [Snowflake Engineering, *Long-Context Isn't All You Need: How Retrieval & Chunking Impact Finance RAG*](https://www.snowflake.com/en/engineering-blog/impact-retrieval-chunking-finance-rag/) [E] — the 23,000-filing / 3.2M-chunk benchmark and the retrieval-beats-model finding. **Best engineering source here.**
- [Red Hat Developer, *Stop chunking tables: building agentic GraphRAG for financial disclosures with Docling* (22 Jul 2026)](https://developers.redhat.com/articles/2026/07/22/how-we-built-agentic-graphrag-financial-disclosures) [E] — typed graph over embeddings; path-finding beats paragraph similarity.
- [AlphaCreek, *SEC Retrieval MCP: RAG vs Navigation for filings agents*](https://www.alphacreek.ai/blog/ai-agents-sec-filings-rag-vs-navigation) [S] — navigation-over-retrieval argument.
- [Reducto, *Best Document Extraction for Financial Documents (2026)*](https://llms.reducto.ai/best-document-extraction-financial-documents) [S] — per-field citations to table cells; agentic verify-and-correct loop. Vendor source.

**Restricted data, MNPI, governance**
- [Lowenstein Sandler, *Key Considerations for Alternative Data and AI Vendors to Investment Firms*](https://www.lowenstein.com/news-insights/publications/articles/key-considerations-for-alternative-data-and-ai-vendors-to-investment-firms-demonstrating-compliance-in-the-face-of-an-evolving-regulatory-environment) [P/E] — SEC MNPI uncertainty, provenance expectations, the training-cutoff suggestion. Law-firm source, highest quality in this group.
- [Reed Smith, *EDPB web scraping guidelines for AI*](https://www.reedsmith.com/our-insights/blogs/technology-law-dispatch/102nbqu/edpb-web-scraping-guidelines-for-ai-making-the-impossible-possible/) [P/E] — Guidelines 03/2026, adopted 7 July 2026.
- [Strata, *Agentic AI Risks: A 2026 Guide*](https://www.strata.io/blog/agentic-identity/agentic-ai-governance-how-to-approach-it/) [S] — the "agent routes around the sanctioned MCP server" failure mode.
- [Forbes Tech Council, *Autonomous Data Stewardship: AI Agents and MDM in Financial Services*](https://www.forbes.com/councils/forbestechcouncil/2026/05/21/autonomous-data-stewardship-how-ai-agents-are-redefining-master-data-management-in-financial-services/) [E] — 31% / 21% MDM figures.

**Mine, not cited** — the 16-class taxonomy, the P1–P7 pattern catalogue, the selection rule, and the build order. Your own architectural position; don't attribute them.
