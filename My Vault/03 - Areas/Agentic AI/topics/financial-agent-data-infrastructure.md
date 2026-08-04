# Data & Foundational Infrastructure for Financial AI Agents
### Opportunities · use cases · challenges & solutions · success stories
*Compiled Aug 2026. Companion to `agentic-ai-in-finance.md`. Source tiers at the end.*

---

## 0. Thesis

> **The connection layer commoditized in about twelve months. Value moved one layer *up* — to entitlement propagation, provenance, and runtime governance — and one layer *down* — to structured, attributable, point-in-time data. In finance, agent quality is a data-infrastructure outcome, not a model outcome.**

The evidence is a benchmark, not an opinion. On **Vals AI Finance Agent v2** — realistic analyst tasks across qualitative work, comps, precedents, earnings, disclosure, and modeling — frontier models sit around **52–59%** (Claude Opus 5 ≈58.6% on the July 2026 snapshot; GPT-5.5 ≈52% in May; ~40 models clustered below). Analyst workflows tolerate roughly **5–10% error** before output is unusable without full human review.

That gap does not close by waiting for a better model. It closes by feeding the agent data that is already structured, already attributed, already entitled, and already correct as-of a date — and by verifying the output deterministically. **That is an infrastructure program, not an ML program.** It's also the most defensible thing you can say in an interview about this space.

---

## 1. The stack

| Layer | Function | Who plays | The hard part |
|---|---|---|---|
| **L0 Source content** | Filings, transcripts, IC packs, LP filings, market data, internal systems of record | Exchanges, regulators, vendors, internal | Licensing terms; unstructured majority |
| **L1 Extraction & structuring** | Documents → model-ready rows with cell-level lineage | Daloopa, Kensho pipeline, Hebbia, Canoe, Accelex | Accuracy at the tail; private-markets docs |
| **L2 Identity spine** | Security master, entity resolution, unique IDs | LEI, D-U-N-S, S&P/Kensho reference data, internal MDM | The unglamorous prerequisite everything else assumes |
| **L3 Storage & time semantics** | Bitemporal / point-in-time, time-series, snapshots | FINBOURNE, kdb-class stores, lakehouse | Restatements, as-of queries, replay corpora |
| **L4 Access & entitlement** | MCP servers, gateways, identity propagation | FactSet, S&P/Kensho, LSEG, Bloomberg, Genesis, FINBOURNE | **Whose identity is the agent acting under?** |
| **L5 Governance runtime** | Catalog, lineage, policy, audit over agents/tools/MCPs | Databricks Unity AI Gateway, Snowflake, internal gateways | Runtime interactions, not just assets at rest |
| **L6 Harness & eval** | Agent templates, subagents, permissions, benchmarks | Claude for FS, Managed Agents; Vals AI, BigFinanceBench | Firm-specific eval on your own corpus |

**Where the money and the difficulty are:** L2, L3, L4. L1 is being solved by vendors; L0 is a procurement problem; L6 is immature but visible. **L4 is where the industry is actually stuck.**

---

## 2. What happened in the last twelve months

**The vendor land grab (chronological, and it moved fast):**

- **FactSet — Dec 2025**: launched what it billed as the **industry's first production-grade MCP server**, after a beta with **45 firms and 800+ institutional users**. Explicitly positioned against "demo or warehouse-dependent" offerings. FactSet has also published its governance pattern: **central tool registries, proxied access, controller/worker hierarchies.**
- **S&P Global — Mar 2026**: repositioned Capital IQ Pro as an **agent-native platform**. MCP servers are one of two core pillars of its GenAI strategy. Single access point = the **Kensho Grounding Agent**. Critically, **click-through-to-source survives into the agentic layer** — a client querying via Claude can still trace any data point to the originating document and methodology. Enterprise pricing (Document Intelligence bundled, no per-module add-ons) as an adoption lever.
- **LSEG — through H1 2026**: "**LSEG Everywhere**" — licensed data exposed via MCP into Claude for Financial Services, Microsoft Copilot Studio, Amazon Quick, plus AWS, OpenAI, Snowflake, Databricks.
- **Bloomberg — ongoing**: deliberately cautious about external exposure; converged its **internal** GenAI tool protocol on MCP and is pushing industry work on the protocol primitives financial workloads actually need — **async tools, structured outputs, HTTP-only transport.**
- **Anthropic — May 2026**: Claude for Financial Services shipped **ten agent templates** (pitch builder, earnings reviewer, model builder, valuation reviewer, GL reconciler, month-end closer, statement auditor, KYC screener, market researcher, meeting preparer), each packaging *skills + connectors + subagents*. Connector roster spans FactSet, S&P Capital IQ, MSCI, PitchBook, Morningstar, LSEG, Daloopa, Chronograph, plus new ones (D&B, Moody's MCP app, Guidepoint, Third Bridge, Intralinks, Verisk, IBISWorld). Managed Agents add long-running sessions, per-tool permissions, credential vaults, and full audit logs.
- **Databricks — DAIS 2026**: **Unity AI Gateway** brings models, agents, tools and MCPs under one **runtime** governance layer. The framing matters: *agents don't just access assets, they act through them.* Governance of interactions, not inventory.

**The one-sentence read:** *"Every major vendor now has an MCP endpoint. That means the connection layer is table stakes, and the differentiator is the entitlement and provenance model published alongside it — which is exactly what the content vendors have been least explicit about."*

---

## 3. Challenges → solutions

### 3.1 Identity & entitlement propagation — the defining unsolved problem
**Challenge.** In capital markets, entitlements are granular and contractual. Front-office desks see content compliance cannot, inside the same firm. Vendor redistribution clauses limit what derived output can be persisted, shared internally, or shown to a client. None of this maps onto an architecture where a **non-human identity — the agent's service account — fronts requests on behalf of an end user** whose identity must be carried through the call chain *and reflected in the response*.

**Solutions in the field:**
- **Entitlement-first application platforms**: Genesis Global built MCP *on top of* an existing entitlements framework so every piece of data carries entitlements specifying who can see it; FINBOURNE describes its Claude integration as agentic actions "with full entitlement checks and data lineage." Notably, **the application platforms foregrounded this; the content vendors largely have not.** That asymmetry is the buying question.
- **Internal MCP gateway** — on-behalf-of token exchange, deny-by-default tool exposure, per-user entitlement resolution at the gateway rather than at each vendor.
- **Protocol-level identity propagation** — *not solved today.* Track this: it determines whether agentic access can meet contractual obligations at all.

**Interview line:** *"The agent's service account is a confused deputy by construction. Until identity propagates through the call chain and into the response, entitlement enforcement is happening in the wrong place."*

### 3.2 Provenance — and why S&P's design choice is the template
**Challenge.** An answer without a traceable source is unusable in a regulated workflow, regardless of correctness.

**Solutions.** Preserve **click-through-to-source through the agentic layer** (S&P's explicit design decision). At L1, demand **cell-level attribution back to the filing** — Daloopa's pitch is exactly this: ~5,000 public companies, 150+ institutions, claimed >99% accuracy *with full source attribution*. Hebbia's equivalent is **sentence-level proof** across thousands of documents. Architecturally: extraction must emit `(value, source_doc_id, page/cell, extraction_method, timestamp)`, and the agent must be forbidden from restating a number without carrying that tuple.

### 3.3 Point-in-time / bitemporal correctness
**Challenge.** Two different time axes — when a fact was *true* and when it was *known* — plus restatements, late filings, and survivorship. Get this wrong and every backtest, every compliance reconstruction, and every "why did the agent do that in March" investigation is invalid.

**Solutions.** Bitemporal storage with as-of query semantics; immutable snapshot corpora hashed per run so trajectories can be replayed against the exact data the agent saw; restatement lineage rather than in-place update. **This is usually the real critical path** — most enterprise data platforms are not bitemporal, and retrofitting is multi-quarter work.

### 3.4 Entity resolution — the prerequisite nobody demos
**Challenge.** Agents reason over entities. If "Acme Corp," "ACME Corporation," and an LEI don't resolve to one identifier, every downstream join is silently wrong.

**Solutions.** Automated entity-identification pipelines that assign unique IDs mapped to a reference-data spine — S&P's Kensho pipeline is the visible example, and it's what let them take **20,000+ private-markets documents** (IC meeting packs, tender documents, LP filings) from acquisition to live inside Document Intelligence **within roughly one quarter**. External anchors: **LEI** for legal entities, **D-U-N-S** for business identity (D&B's positioning is explicitly "agents in risk workflows must know who they're dealing with… deterministic, auditable outcomes"). Reported AI-assisted MDM gains: **~31% less manual stewardship workload, ~21% better entity-resolution accuracy.**

### 3.5 MCP portfolio sprawl
**Challenge.** Institutions won't consume one MCP server — they'll consume a **portfolio**: LSEG, S&P, FactSet, Bloomberg, plus a long tail of alt-data, each with its own auth model, audit pattern, versioning cadence, and rate-limit behavior. Reported operational symptoms already: **context bloat** (agents pulling too much from too many tools) and **lack of synchronization across MCP servers inside one organization**. The buy-side's familiar vendor-management problem, rebuilt one layer up the stack.

**Solutions.** Central **tool registry + proxy** (FactSet's published pattern: controller/worker hierarchies); marketplace-as-catalog (Databricks Marketplace, Snowflake moving similarly); runtime governance over tool/MCP invocation (Unity AI Gateway class). **Open question worth quoting:** *which governance layer wins enterprise adoption — an internal gateway built by the data-management team, a vendor marketplace catalogue, or a third-party intermediary none of the incumbents has yet named?*

### 3.6 Evaluation infrastructure
**Challenge.** Public benchmarks measure the *model*; production failures live in the *plumbing*. And the benchmarks are young.

**Landscape.** **Vals AI Finance Agent v2** is the commercial reference (realistic analyst tasks; ~40 models tracked). Academic entrants: **BigFinanceBench** (workflow-grounded financial-research agents), **FinRetrieval** (financial data retrieval *by agents* — the closest thing to an infra benchmark), **QuantCode-Bench** (executable trading strategy generation), **LATTICE** (decision-support utility). **Solution:** treat public benchmarks as model selection only; build a firm-specific eval on your own corpus, with regression cases drawn from real failures, and grade programmatically wherever a source-of-truth exists (recompute the number, diff the DB state) rather than with an LLM judge.

---

## 4. Opportunities — where the gaps actually are

1. **Entitlement propagation as a product.** No incumbent owns it, the protocol doesn't solve it, and it blocks every regulated agentic deployment. Highest-leverage gap in the stack.
2. **The neutral MCP governance gateway.** Explicitly named as an unresolved contest. Whoever wins it sits between every firm and every vendor.
3. **Bitemporal agent memory.** Agent memory today is append-and-retrieve. Finance needs as-of memory with restatement lineage. Nobody ships this.
4. **Finance-specific eval infrastructure.** Trajectory-level, entitlement-aware, point-in-time-correct. The benchmarks that exist are model benchmarks.
5. **Private-markets unstructured data.** GPs report dissatisfaction with data availability while being unsure of AI's value — a classic underserved-plus-skeptical market. The Kensho/With Intelligence pipeline shows the shape of the answer.
6. **Protocol primitives for finance**: async tools (long-running queries), structured outputs (typed financial records, not prose), HTTP-only transport. Bloomberg is pushing these; they're not settled.

---

## 5. Success stories

| Organization | What was reported | Layer it validates |
|---|---|---|
| **FIS** | Agent that "compresses AML investigations from **days to minutes**"; credit decisioning, fraud, deposit-retention agents to follow — delivered so clients "won't need to build this infrastructure themselves" | L6 + productized vertical infra |
| **BNY** | "Eliza" + Claude — digital employees working cases **end to end** | Workflow agents on internal systems |
| **Citadel** | Claude for Excel used to build/update coverage models and pressure-test work — "step-change in efficiency" | L1→L6 in the analyst's native tool |
| **Walleye Capital** | **100% of employees** at the 400-person fund use Claude Code | Org-wide adoption, non-technical roles included |
| **Mizuho** | Meeting prep compressed — "prep time transformed into idea time" | Research/coverage agents |
| **Hg** | Due diligence and financial modeling from unstructured data with minimal prompting | L1 extraction + modeling |
| **S&P Global / With Intelligence** | **20,000+** private-markets documents structured, tagged, entity-linked and live in ~one quarter post-acquisition | L1+L2 pipeline as a repeatable asset |
| **FactSet** | 45 firms / 800+ institutional users in MCP beta before GA | L4 demand is real, not speculative |
| **Daloopa** | 150+ institutions, ~5,000 companies, claimed >99% accuracy with full filing attribution | L1 with provenance |
| **MDM programs** | ~31% less manual stewardship, ~21% better entity resolution | L2 |

*Caveat to carry into the room: these are vendor-published and press-released. Cite them as "reported," and note that none has an independent control group.*

---

## 6. Reference blueprint

```
                    ┌──────────────── Audit log (immutable, replayable) ────────────────┐
                    │                                                                    │
User identity ──► MCP Gateway ──► [entitlement resolution · tool registry · rate limit] ─┤
                    │                                                                    │
                    ├─► Vendor MCP servers (FactSet · S&P/Kensho · LSEG · Moody's)       │
                    ├─► Internal MCP (positions · risk · CRM · books of record)          │
                    └─► Extraction service (docs → values + cell-level lineage)          │
                                        │                                                │
                          Bitemporal store (as-of queries, snapshot hashes) ─────────────┤
                                        │                                                │
                    Agent harness (skills · subagents · per-tool permissions)            │
                                        │                                                │
                    Deterministic verifier (recompute · schema · entitlement check)      │
                                        │                                                │
                    Human review ──► action ─────────────────────────────────────────────┘
```

**Build checklist**
1. Identity spine before agents. No entity resolution → no reliable joins → no trustworthy agent.
2. Bitemporal from day one. Retrofitting is the multi-quarter surprise.
3. One gateway, not N vendor integrations. Entitlements resolved centrally, logged centrally.
4. Provenance tuples mandatory at extraction; agents may not restate a number without one.
5. Snapshot + hash the retrieval corpus per run so trajectories replay.
6. Firm-specific eval on your own corpus; public benchmarks for model selection only.
7. Negotiate the exit: entitlement model, audit export, and model-version pinning go in the contract.

---

## Sources

**Tiers:** [P] primary/official · [R] arXiv/peer-reviewed · [E] trade press / practitioner · [S] secondary or vendor marketing.

**The two most valuable reads**
- [A-Team Insight, *Now the MCP Layer is Commoditised, Are Entitlements the Next Challenge?* (6 May 2026)](https://a-teaminsight.com/blog/now-the-mcp-layer-is-commoditised-are-entitlements-the-next-challenge/) [E] — source for §0 thesis, §2 vendor timeline, §3.1 identity problem, §3.5 sprawl, and the open question about which governance layer wins. Best single piece written on this topic.
- [A-Team Insight, *S&P Global Bets on Agent-Native Architecture as Capital IQ Pro Consolidation Accelerates* (19 Mar 2026)](https://a-teaminsight.com/blog/sp-global-bets-on-agent-native-architecture-as-capital-iq-pro-consolidation-accelerates/) [E] — Kensho Grounding Agent, click-through-to-source in the agentic layer, the With Intelligence pipeline, enterprise pricing. Includes direct quotes from Warren Breakstone, Head of Data & Research, S&P Market Intelligence.

**Vendor / platform primary**
- [Anthropic, *Agents for financial services* (5 May 2026)](https://www.anthropic.com/news/finance-agents) [P] — ten agent templates, connector roster, Managed Agents controls, and all customer quotes in §5 (FIS, BNY, Citadel, Walleye, Mizuho, Hg, D&B, Morningstar, FactSet).
- [FactSet, *Meets Demand for AI-Ready Data, First to Announce MCP Sans Intermediary*](https://investor.factset.com/news-releases/news-release-details/factset-meets-demand-ai-ready-data-first-announce-mcp-sans) [P]
- [Databricks, *What's new with Unity Catalog at Data + AI Summit 2026*](https://www.databricks.com/blog/whats-new-unity-catalog-data-ai-summit-2026) [P] — Unity AI Gateway; runtime governance over agents/tools/MCPs.
- [Qubika, *Everything Databricks Announced at DAIS 2026*](https://qubika.com/blog/everything-databricks-announced-dais-data-ai-summit-2026/) [E]
- [Daloopa, *AI-Based Data Extraction for Financial Services*](https://www.daloopa.com/blog/ai-based-data-extraction-for-financial-services) [S] · [Daloopa vendor profile](https://idp-software.com/vendors/daloopa/) [S] — coverage and accuracy claims are vendor-stated.
- [Hebbia, *AlphaSense competitors* (sentence-level proof, agentic document synthesis)](https://www.hebbia.com/resources/alphasense-competitors) [S] — vendor comparison, read accordingly.

**Benchmarks & evaluation**
- [Vals AI Finance Agent benchmark](https://www.vals.ai/benchmarks/finance_agent) [P] · [Finance Agent v2 leaderboard snapshot, Jul 2026](https://benchlm.ai/benchmarks/financeagentv2) [S] · [KuCoin write-up of v2 results](https://www.kucoin.com/blog/can-ai-replace-financial-analysts-in-2026-vals-ai-finance-agent-v2-reveals-gpt-5-5-hits-just-52-percent-accuracy) [S]
- [arXiv 2606.03829, *BigFinanceBench: A Workflow-Grounded Benchmark for Financial-Research Agents*](https://arxiv.org/pdf/2606.03829) [R]
- [arXiv 2603.04403, *FinRetrieval: A Benchmark for Financial Data Retrieval by AI Agents*](https://arxiv.org/pdf/2603.04403) [R]
- [arXiv 2604.15151, *QuantCode-Bench*](https://arxiv.org/pdf/2604.15151) [R] · [arXiv 2604.26235, *LATTICE*](https://arxiv.org/pdf/2604.26235) [R]
- [arXiv 2505.19197, *Structuring the Unstructured: Multi-Agent Extraction of Financial KPIs and Guidance*](https://arxiv.org/pdf/2505.19197) [R]
- [Prigent, *Financial AI Benchmarks: What They Test and What They Miss*](https://www.bprigent.com/article/fpna-ai-benchmarks) [E]

**Governance, MDM, security**
- [Forbes Tech Council, *Autonomous Data Stewardship: How AI Agents Are Redefining MDM in Financial Services* (May 2026)](https://www.forbes.com/councils/forbestechcouncil/2026/05/21/autonomous-data-stewardship-how-ai-agents-are-redefining-master-data-management-in-financial-services/) [E] — the 31%/21% MDM figures.
- [Promethium, *AI Agent Data Governance: Enterprise Playbook 2026*](https://promethium.ai/guides/ai-agent-data-governance-enterprise-playbook-2026/) [S] — the agent identity / runtime enforcement / auditing / lineage four-component framing.
- [Halborn, *Securing AI Agents in Financial Infrastructure: Threat Models & Controls*](https://www.halborn.com/reports/securing-ai-agents-in-financial-infrastructure) [E] · [ARMO, *How Financial Services Teams Should Secure AI Agents in 2026*](https://www.armosec.io/blog/financial-services-ai-agent-security/) [E] — also the source for FINRA's 2026 Annual Regulatory Oversight Report guidance (human-in-the-loop checkpoints before agents with transaction authority act) and Treasury's FS AI RMF (Feb 2026).
- [A-Team, *AI in Capital Markets Handbook 2026*](https://a-teaminsight.com/guides/ai-in-capital-markets-handbook-2026/) [E] — worth reading in full if you want the buy-side vocabulary.

**My framing, not cited** — the seven-layer stack (§1), the challenge→solution pairings (§3), the opportunity list (§4), and the reference blueprint and checklist (§6). Defensible as your own architectural position.
