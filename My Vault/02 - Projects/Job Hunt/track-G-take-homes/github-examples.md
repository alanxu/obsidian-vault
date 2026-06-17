---
tags: [job-hunt, interview-prep, track, take-home, github, examples]
track: "Track G — Take-homes & work trials"
plan-section: "§7.5"
parent: [[README]]
related: [[per-company-notes]], [[take-home-question-bank]]
compiled: 2026-06-17
---

# GitHub take-home examples — repos worth studying

> Real assignments + real candidate submissions to model. **Caveat:** most "submission" repos are candidate work of *varying* quality — study the **structure, README, and eval approach**, not necessarily the code. The gold-standard items are the two **official, company-published** assignments at the top.

---

## Tier 1 — Official, company-published assignments ⭐⭐ (study these first)

- **[anthropics/original_performance_takehome](https://github.com/anthropics/original_performance_takehome)** — Anthropic's *real* original performance take-home, open-sourced. Optimize a kernel on a custom **VLIW SIMD processor simulator**; baseline 147,734 cycles → Claude Opus 4.5 got 1,487 (99× speedup, beat most humans). Beat 1,487 and they invite you to email recruiting. Shows exactly how a frontier lab frames a **systems/perf** take-home + how they think about an AI-resistant test. *(Plays directly to your infra strength.)* Pairs with Anthropic's writeup [Designing AI-resistant technical evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations).
- **[Arcan-Tech/interview-test-aiengineer-2025](https://github.com/Arcan-Tech/interview-test-aiengineer-2025)** — a real, published **AI-Engineer technical test**: predict **code-change propagation** from git diffs (FFmpeg, Antlr4 datasets), 4-hour limit, Dockerized, deliver model + **≤1000-word report**. A clean template for "ML-on-code, time-boxed, report-graded."

## Tier 1 — The meta-resource ⭐⭐

- **[alexeygrigorev/ai-engineering-field-guide](https://github.com/alexeygrigorev/ai-engineering-field-guide)** — research into AI-eng interview assignments, take-homes, and hiring (Q4'25/Q1'26): built from **1,765 job descriptions + 100+ submission repos**. Most of [[take-home-question-bank]] is distilled from here.
  - [`interview/questions/06-home-assignments.md`](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/questions/06-home-assignments.md) — every assignment type + how-to-prepare + the source repos.
  - [`interview/01-interview-process.md`](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/01-interview-process.md) — per-company process breakdowns.
  - [`awesome.md`](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/awesome.md) — huge curated resource list (interview experiences, eval guides, case studies).

---

## Tier 2 — Candidate submissions to model, by type

Real submissions to actual company take-homes, **as collected by the [field guide](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/questions/06-home-assignments.md) (Q4'25/Q1'26)**. Use them to calibrate **scope, README depth, and eval harnesses** — the things graders reward.

> ⚠️ **Link-rot warning (verified 2026-06-17):** the two Tier-1 *official* repos are confirmed live. The Tier-2 links below are **individual candidate accounts** — they get renamed, made private, or deleted, and some weren't independently re-confirmed. If one 404s, re-resolve it from the field guide's footnote list (the maintained source of truth), or GitHub-search the company name + "ai engineer".

### RAG / document Q&A (the most common prompt)
- [ncapek/ai_engineer_interview_2025](https://github.com/ncapek/ai_engineer_interview_2025) — RAG chatbot w/ MongoDB Atlas.
- [LAWSA07/Company-Policy-Assistant](https://github.com/LAWSA07/Company-Policy-Assistant---Neura-Dynamics) — policy RAG with mandatory citations + a 7-question eval set (good eval example).
- [AsharAhmad/govgpt-agentic-rag](https://github.com/AsharAhmad/govgpt-agentic-rag) — 100% open-source agentic RAG, **RAGAS**-evaluated (faithfulness/relevancy/precision/recall).
- [gazitanbhir/RokomariTask](https://github.com/gazitanbhir/RokomariTask) — multi-vendor data pipeline + RAG with async rate-limited enrichment (CLI **and** API).

### Agents & tool-calling ⭐ (your space)
- **[Aaronxvc/cohere_sales_agent](https://github.com/Aaronxvc/cohere_sales_agent)** — reported **Cohere** take-home submission: sales-insights agent, PII refusal, aggregates-only, scored on accuracy/safety/reasoning. *Closest thing to a Cohere example in the wild — if the link is dead, GitHub-search "cohere sales agent" / "cohere take home".* ⭐ (couldn't re-confirm live on 2026-06-17)
- [Curling-AI/hiring-challenge-alpha](https://github.com/Curling-AI/hiring-challenge-alpha) — assistant agent: DB queries + doc search + bash-with-approval (the company's own challenge repo).
- [venki-byte/skylark-bi-insight-agent](https://github.com/venki-byte/skylark-bi-insight-agent) — dual-LLM BI insights agent.
- [vaishnavip-23/Transport-Query-Agent](https://github.com/vaishnavip-23/Transport-Query-Agent) — agent over 7 live APIs.

### Multi-agent / orchestration ⭐
- [jkbrooks/context-engineering-takehome](https://github.com/jkbrooks/context-engineering-takehome) — D&D multi-agent sim with an **explicit weighted rubric** (30/30/25/15) — great for seeing how graders score.
- [rak-shi/kasparro-...content-generation-system](https://github.com/rak-shi/kasparro-ai-agentic-content-generation-system-Rakshitha_Valipireddy) — 5-agent content pipeline, strict-JSON outputs.
- [abhishuman18/Minimal-Workflow-Agent-Engine-Tredence](https://github.com/abhishuman18/Minimal-Workflow-Agent-Enigne-Tredence-) — minimal graph workflow engine (nodes, branching/looping, cycle protection, unit tests). ⭐ a mini agent-framework.
- Hippocratic AI bedtime-story pipeline (Spec→Story→**LLM Judge**→Rewrite): [reonrash/AI-Agent-Deployment-Engineer-Takehome](https://github.com/reonrash/AI-Agent-Deployment-Engineer-Takehome), [pranav-gilda/agent_deployment_bedtime_stories](https://github.com/pranav-gilda/agent_deployment_bedtime_stories) — good **LLM-as-judge** examples.

### LLM infra / platform ⭐ (infra-strength flex)
- [Sushma-Sangolli/Smart-LLM-Router-Observability-Platform](https://github.com/Sushma-Sangolli/Smart-LLM-Router-Observability-Platform) — LLM router: multi-level caching, failover, tracing, perf targets (100+ req/s, p95 <2 s, >40% cache-hit).
- [jerichosuguru/AI-Coworker-Engine](https://github.com/jerichosuguru/AI-Coworker-Engine) — NPC system w/ a "Director Agent" detecting loops via semantic similarity + RAG (FastAPI + Claude + FAISS).

### Document extraction
- [gulmittal/Trestle_AI_Engineer_Intern_Assignment](https://github.com/gulmittal/Trestle_AI_Engineer_Intern_Assignment-) — marksheet → JSON with confidence scores.
- [Artush-Baghdasaryan/krisp_ai_engineer_role_task](https://github.com/Artush-Baghdasaryan/krisp_ai_engineer_role_task) — dedup/clustering evaluated with ARI/NMI/homogeneity/completeness.
- [Viren-55/voice-ai-assignment](https://github.com/Viren-55/voice-ai-assignment) — real-time earnings-call transcription + SSE insight streaming.

> More (refactor-a-RAG-app, physician notetaker, legal-contract analysis, investment bot, etc.) are footnoted in the field guide's [06-home-assignments.md](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/questions/06-home-assignments.md).

---

## Tier 3 — Curated lists, question banks, eval guides

- [KalyanKS-NLP/RAG-Interview-Questions-and-Answers-Hub](https://github.com/KalyanKS-NLP/RAG-Interview-Questions-and-Answers-Hub) — 100+ RAG Q&A.
- [aishwaryanr/awesome-generative-ai-guide](https://github.com/aishwaryanr/awesome-generative-ai-guide/blob/main/interview_prep/60_gen_ai_questions.md) — 60 curated GenAI interview questions.
- [themanojdesai/genai-llm-ml-case-studies](https://github.com/themanojdesai/genai-llm-ml-case-studies) — 500+ production case studies (architecture reference for your builds).
- [ombharatiya/ai-system-design-guide](https://github.com/ombharatiya/ai-system-design-guide) · [donnemartin/system-design-primer](https://github.com/donnemartin/system-design-primer) — design grounding.
- Eval craft (the #1 differentiator): [Hamel Husain — Evals FAQ](https://hamel.dev/blog/posts/evals-faq/) · [Hamel — LLM-as-judge](https://hamel.dev/blog/posts/llm-judge/) · [Shreya Shankar — In Defense of AI Evals](https://www.sh-reya.com/blog/in-defense-ai-evals/).

---

## How to use these

1. **Reverse-engineer the rubric.** Open 3–4 repos for the prompt type you expect; note what the strong ones include that the weak ones don't (almost always: an **eval harness**, a **trade-offs README**, and **one-command run**).
2. **Steal structure, not code.** Clone the *shape* — folder layout, README sections, test setup, eval set — into your own [[reusable-repo-scaffold]] (master plan §7.5).
3. **Find the eval gap.** Most candidate repos are weak on evaluation. Doing evals well is the cheapest way to land in the top decile.
4. **Watch the date.** These are 2025–26 submissions; frameworks (LangGraph, CrewAI, RAGAS) churn — confirm current versions before copying patterns.
5. **Don't copy a submission for an active loop.** Graders search GitHub. Model the approach; write your own.

### Sources
[anthropics/original_performance_takehome](https://github.com/anthropics/original_performance_takehome) · [Arcan-Tech/interview-test-aiengineer-2025](https://github.com/Arcan-Tech/interview-test-aiengineer-2025) · [ai-engineering-field-guide](https://github.com/alexeygrigorev/ai-engineering-field-guide) (home-assignments + awesome.md) · [Anthropic — AI-resistant evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations)
