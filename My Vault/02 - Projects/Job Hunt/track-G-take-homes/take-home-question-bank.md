---
tags: [job-hunt, interview-prep, track, take-home, question-bank]
track: "Track G — Take-homes & work trials"
plan-section: "§7.5"
parent: [[README]]
related: [[per-company-notes]], [[github-examples]], [[D1-rag-with-citations]], [[D3-agentic-platform-loop]]
compiled: 2026-06-17
---

# Take-home question bank — concrete prompts

> As many real, concrete take-home prompts as could be sourced (Q4'25–Q2'26), from candidate reports, job posts, and **100+ GitHub submissions** ([field guide](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/questions/06-home-assignments.md)). Repos for many of these are in [[github-examples]].
>
> ⭐ = highest-alignment with your target (Staff, Agentic/Applied AI). These are the prompts to *actually build* as dry-runs (see master plan §7.5 Week-8 dry-run).

**The distribution of what gets asked** (from 100+ repos): RAG systems **40%+** · agentic/tool-calling **30%+** · conversational AI **20%+** · document processing **15%** · LLM-as-judge eval **10%+**. If you build one RAG-with-citations system and one agent-with-eval system end to end, you cover the majority of real take-homes.

---

## 1. Named-company prompts (confirmed / strongly reported)

### Anthropic
- **Implement a bank with multiple transaction types**, where the task gets *progressively more complex* across levels (timed CodeSignal, 90 min). Same family as in-memory DB / expiring ledger — see [[practical-oo-coding-deep-guide]] and [[openai-interview-guide]] Problems 3–6. ⭐(coding)
- **Performance take-home (open-sourced)**: optimize a kernel on a custom **VLIW SIMD processor simulator**. Baseline 147,734 cycles; Claude Opus 4.5 hit 1,487 (99× speedup). Beat 1,487 → email performance-recruiting@anthropic.com. Repo in [[github-examples]]. ⭐(systems/infra — plays to your strength)

### OpenAI
- **Build a webhook delivery system** (reported work-trial build). Graded on reliability, code quality, testing — *not* feature count. 48 hr, paid. ⭐(backend — your strength)
- Pattern: any "build a small but *real* production service in 48 hr, with tests + a README that explains your design choices."

### Cohere
- **Build a sales-insights agent** that answers questions about subscription/revenue data. Must **detect and refuse PII requests** (emails, phone, card tokens); **no raw rows to the LLM — aggregates only**; evaluated on 3 dimensions: **accuracy, safety/refusal correctness, reasoning quality**. (Real candidate submission — repo in [[github-examples]].) ⭐⭐ *(agentic + safety + enterprise framing = exactly Cohere)*
- Case-study archetype: one or two open prompts on a Cohere-relevant scenario → deliver a **notebook/report/demo** with a narrative (framing → method → findings → recommendation → caveats). See [[cohere-interview-guide]] §Round 9 and [[per-company-notes]].

### Anysphere / Cursor
- Given access to **part of Cursor's real codebase**, clone it and **build a common data structure on top — e.g. a hash tree**. 4–8 hr, paid, GPT/Cursor allowed. ⭐

### Together AI
- **Inference-engine role**: implement or optimize a **CUDA kernel** (element-wise / reduction / softmax); or implement **attention from scratch with batching**; or a **batching scheduler** matching requests to GPU capacity with fairness; or **streaming token generation with cancellation**. (needs real CUDA)
- **Platform role**: a focused systems problem on the serving/API surface. ⭐(systems)

### Arcan-Tech (real published AI-Engineer test, 4 hr, Dockerized)
- **Predict change propagation in a software repo**: given files `Xs` that changed, output files `Ys` likely to change next, learned from **git diffs** (e.g. FFmpeg 4,417 files, Antlr4 9,528 files). Deliver model + **≤1000-word report** on data cleaning, model design, training & eval. Repo in [[github-examples]]. ⭐(ML on code — strong fit)

### Other labs/companies (process-confirmed, prompt-pattern)
- **Eightfold.ai** (Agentic AI): 3-day assignment to **build an AI agent**. ⭐
- **LangChain** (AI Engineer): take-home to **develop an agent**, then defend it, then applied system design. ⭐
- **Mistral** (Applied AI): take-home build inside a 7-round loop.
- **PostHog**: paid full-day **SuperDay** of real work (work-trial, not a build prompt).

---

## 2. RAG & document Q&A (40%+ of all take-homes) ⭐

- ⭐ **RAG chatbot that ingests PDFs/docs → embeddings in a vector DB → answers with citations.** Must say *"I don't have that information"* when unavailable; answers strictly from retrieved context. (10+ submissions across 5+ companies — the single most common prompt.)
- ⭐ **Policy-document RAG assistant** with **mandatory source citations** on every answer; safe fallback for out-of-scope; ships with a **7-question eval set** across 3 categories (answerable / partially / unanswerable).
- **Document Q&A with citation tracking that handles multi-hop questions** (answer requires info from multiple docs/sections).
- **Live chat agent grounded in an FAQ knowledge base** — answer *only* from known FAQ data.
- **Customer-support chatbot via RAG, open-source models**: 100+ concurrent users, **<2 s latency**, grounded in company docs, analytics tracking.
- **CLI tool to summarize long PDFs** with configurable models + chunking strategies. (One engineer made it config-driven → two competing offers in 72 hr.)
- **Refactor a messy RAG app into clean architecture**: preserve exact API endpoints, kill global mutable state, make it testable without running services. (5+ submissions for one company.) ⭐(judgment/architecture)
- **Agentic RAG for government docs**: 100% open-source (Ollama + CrewAI + pgvector), integrate with OpenWebUI, evaluated with **RAGAS** (faithfulness, answer relevancy, context precision/recall).

> Build target: this is your [[D1-rag-with-citations]] worked solution turned into a running repo. Do it once, well.

## 3. Agents & tool-calling (30%+) ⭐⭐

- ⭐ **Assistant agent** handling **database queries + document search + bash commands**, where **bash requires explicit user approval**. (tool-use + human-in-the-loop guardrail)
- ⭐ **Autonomous agent on an open-source LLM with an observability / eval layer.** (the eval layer is the differentiator)
- ⭐ **Agent that reads customer CSV data → generates personalized email campaigns** with **evaluation metrics**.
- **Code-review agent** that analyzes Python files and gives actionable feedback. ⭐(dev-productivity AI — your space)
- **BI-insight agent**: turn Monday.com project data into conversational business insights (dual-LLM architecture).
- **Live-data query agent**: Singapore transport agent hitting **7 live APIs** (buses, trains, traffic, stations).
- **Customer-support agent** (generic YC prompt).
- **LLM hallucination-detection eval tool.** ⭐(eval)
- **AI judge for a Rock-Paper-Scissors variant**: classify inputs VALID/INVALID/UNCLEAR, handle typos/edge cases, tool-based state-management workflow.

> Build target: [[D3-agentic-platform-loop]] — ReAct loop, tool calling, memory, retries/error recovery, sandboxing, **eval + observability**, cost control. Wire in an eval harness from line one.

## 4. Multi-agent / orchestration ⭐

- ⭐ **Multi-agent content generation**: 5 agents (research, writing, editing, SEO, publishing). Input product JSON → output FAQ doc + product page + comparison page, all in **strict JSON**. (LangChain + Groq)
- ⭐ **Minimal workflow engine**: graph-based nodes, state management, branching/looping, tool-based logic, **max 50 steps, infinite-cycle protection, unit tests mandatory.** (6+ submissions — popular pattern) ⭐⭐ *(this is a mini agent-framework — perfect staff/infra showcase)*
- **5-agent CBT therapy system**: agents design/critique/refine exercises; **human-in-the-loop approval** before finalizing.
- **4-stage bedtime-story pipeline**: Spec Builder → Storyteller → **LLM Judge** → Rewriter; ≤2 revision cycles; judge evaluates against the spec.
- **Multi-agent D&D simulation**: Game-Master agent + Player agents; address ≥3 of 6 challenges (long campaigns, secrets, rulings, self-aware dungeon, living world, ambiguity). LangGraph. Explicit **weighted rubric**: 30% functionality / 30% challenge completion / 25% context engineering / 15% code quality.
- **NPC system for a job-sim platform**: 3 AI co-workers w/ distinct personalities + a **"Director Agent" that detects conversation loops via semantic similarity (0.85 threshold)** + RAG knowledge retrieval. (FastAPI + Claude API + FAISS)

## 5. LLM infra / platform builds ⭐ *(your infra strength → differentiator)*

- ⭐⭐ **LLM processing pipeline** with **intelligent routing, multi-level caching (exact + semantic), provider health monitoring with failover, distributed tracing.** Targets: **100+ req/s, p95 <2 s, >40% cache-hit.** *(LLM gateway/router — staff-level systems showcase; matches master-plan "LLM gateway/router" one-pager)*
- **Smart LLM router + observability platform** (same family, real submission).
- **Data pipeline**: process 1,000 messy products from 4 vendors → unified schema; **vendor-specific token-bucket rate-limited async** API enrichment; AI-powered duplicate detection; CLI **and** API. ⭐(backend judgment)
- **Markdown → slide-deck web app**: split content into logical sections for a target slide count; ≤150K-token doc, single API call. (Next.js + OpenAI)

## 6. Document extraction & processing (15%)

- **Marksheet extraction API**: parse complex table layouts + handwriting → structured JSON (with confidence scores).
- **Physician notetaker**: physician–patient conversation → structured clinical documentation.
- **Legal-document analysis for contracts**: extract key info, flag risks (auto-renewal traps, liability, IP ownership, non-competes), structured summaries. ⭐(Harvey-adjacent)
- **CBT assistant = RAG + safety**: mandatory crisis detection, PII redaction/pseudonymization, no secrets in logs, "educational only."
- **Blood-test report (PDF) → explain issues + suggestions**, fetched from online articles with **source links**.
- **Question dedup & clustering pipeline**: exact dedup → semantic dedup → LLM cluster discovery → classification; evaluated with **ARI, NMI, homogeneity, completeness**.
- **Transaction-to-user matching**: find users named in transaction descriptions, similar txns via text matching, propose improvements (embeddings, DB). (Spring Boot + Java)
- **Real-time earnings-call transcription + insight streaming**: Whisper audio→text, real-time extraction of revenue/guidance/risks/outlook, **SSE** output.

## 7. Full-stack / product AI

- **AI-first CRM module**: React/Redux + FastAPI + **LangGraph with 5+ tools**. Deliverable: GitHub repo + **10–15 min demo video**.
- **Telegram investment-coaching bot** with safety filtering (educational only, no personalized financial advice).
- **Memory + personality-transformation system**: extract structured long-term memory from chat history as JSON; transform responses by persona (calm mentor / witty friend / therapist). Open-source LLMs only.
- **LLM rating-prediction + prompt-evaluation system** with user/admin dashboards. (Node.js + MongoDB + Google Generative AI)

---

## 8. Evaluation criteria you'll be scored against

Recurring rubric items across assignments (bake these into anything you submit):

- **Functional correctness** — works end-to-end, handles edge cases, correct outputs.
- **Code quality & architecture** — modular, clean, extensible, real error handling.
- **Evaluation methodology** — did you build an **eval harness**, define metrics, measure quality systematically? *(the #1 differentiator)*
- **Production readiness** — scalability, caching, monitoring, cost, security (PII handling, input sanitization, rate limiting).
- **Performance targets** — e.g. <2 s p95, 100+ req/s, >40% cache-hit, >30% cost reduction.
- **Testing** — unit tests (sometimes mandatory), coverage targets (~80%), edge cases.
- **Documentation** — README quality, design-decision explanations, trade-off analysis.
- **Quantitative metrics** by domain — RAGAS for RAG; ARI/NMI for clustering; confidence scores for extraction.
- **Weighted rubrics** — some give explicit weights (e.g. 30/30/25/15).

---

## 9. Your dry-run shortlist (build these before a real one lands)

To prep the *reactive* take-home well with minimum reps, build two complete repos using the [[per-company-notes]] "what graders reward" checklist, each with an eval harness + clean README:

1. ⭐⭐ **RAG-with-citations service** (§2) — covers 40% of prompts; reuse [[D1-rag-with-citations]].
2. ⭐⭐ **Tool-using agent with an eval/observability layer** (§3) — covers 30%; reuse [[D3-agentic-platform-loop]].
3. *(stretch, plays to infra strength)* **LLM router/gateway with caching + failover + tracing** (§5) — the staff-level systems flex.

Each must: run from a clean clone in one command · ship tests · ship an eval set · README = framing → approach → trade-offs → results → limitations → next steps · list explicitly what you cut and why.

---

### Sources
[field guide — home assignments](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/questions/06-home-assignments.md) · [field guide — process](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/01-interview-process.md) · [Anthropic perf take-home repo](https://github.com/anthropics/original_performance_takehome) · [Arcan-Tech AI-eng test](https://github.com/Arcan-Tech/interview-test-aiengineer-2025) · [Cohere sales-agent submission](https://github.com/Aaronxvc/cohere_sales_agent) · [techinterview — Together](https://www.techinterview.org/companies/together-ai/) · [techinterview — Cursor](https://www.techinterview.org/companies/cursor/) · [interviewcoder — OpenAI](https://www.interviewcoder.co/blog/openai-interview-process) · [PromptLayer — agentic interview](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/) · [[cohere-interview-guide]] · [[anthropic-interview-guide]] · [[openai-interview-guide]]
