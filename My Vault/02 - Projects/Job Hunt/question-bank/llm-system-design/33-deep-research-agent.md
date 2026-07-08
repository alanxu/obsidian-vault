---
title: Design a Deep Research Agent
slug: deep-research-agent
area: 3 — Agentic Systems
companies: [OpenAI, Anthropic, Perplexity, Cohere, Glean]
difficulty: ★★★★☆
formats: [Live system design, Take-home design]
related: ["[[03-web-answer-engine]]", "[[09-agent-platform]]", "[[01-rag-with-citations]]", "[[11-multi-agent-system]]"]
added: 2026-07-08 (audit fill — every lab ships one; distinct from single-shot answer engine)
evidence: "INFERRED (weakest of the fills): no candidate-reported interview prompt found (searched 2026-07-08/09). Basis: every target ships a deep-research product and lab architectures are publicly discussed (Anthropic multi-agent, OpenAI o3 e2e-RL), making it a plausible design prompt. Treat as prep-for-adjacent, not reported."
---

# Design a Deep Research Agent

> "Given a research question, autonomously search, read, and synthesize a cited report over 5–30 minutes." **Open with the contrast:** [[03-web-answer-engine]] is *one* retrieve→generate pass at low latency; deep research is an **agentic loop with a budget** — the design problem is **coverage vs cost vs stopping**, plus keeping synthesis faithful over hundreds of sources.

## Problem
"Design OpenAI Deep Research / Perplexity Research mode." Variants: enterprise (internal docs + web), due-diligence agent (finance/legal), competitive-intel agent.

## Clarify first
- Latency: minutes OK? Interactive check-ins or fully autonomous? Cost budget per task?
- Sources: open web, licensed corpora, internal (→ ACL)? Citation strictness (every claim?)
- Output: report with structure? Follow-up conversation over the result?

## Architecture
**Planner:** decompose question → research plan (sub-questions, angles) — shown to user for approval (cheap alignment point). **Research loop (per sub-question):** query generation → search (web API + internal RAG) → fetch/parse → **note-taking with per-note source handle** → gap analysis ("what's still unanswered?") → iterate until sub-budget or saturation. **Synthesis:** outline from plan → section-by-section generation *from notes only* (not raw pages) → citation verification pass (NLI/judge per claim) → report. **Infra:** the [[09-agent-platform]] runtime underneath (steps caps, traces, sandboxed fetch), fetch cache, dedup.

## Deep-dive — the stopping/coverage problem
- **Budgeted exploration:** per-sub-question budget (searches, tokens, wall-clock); **saturation signal** = new sources stop adding novel notes (measure: note-embedding novelty vs existing notes < threshold).
- **Breadth control:** planner caps sub-questions (5–10); gap analysis can *add* one, not fan out unboundedly — otherwise cost explodes quadratically with question breadth.
- **Notes as the unit of truth:** synthesis reads compressed notes (claim + quote + URL + confidence), never raw HTML — bounds synthesis context, makes citations mechanical, and localizes injection risk to the note-taking step (untrusted page text never meets the final-report prompt directly).
- **Contradiction handling:** notes carry stance; synthesis must surface disagreement ("sources conflict") rather than pick silently — this is a top quality differentiator.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Single agent vs sub-agent per sub-question | shared context vs parallel speed + isolation ([[11-multi-agent-system]]) |
| Plan-approve vs fully autonomous | user alignment vs friction |
| Notes (compress early) vs raw pages | bounded cost + injection isolation vs lossy |
| Fixed budget vs saturation-based stop | predictable cost vs quality on hard questions |
| Live fetch vs cached/index | freshness vs latency + politeness |

## Numbers
Typical task: 50–300 page fetches, 10⁵–10⁶ tokens, $1–10 LLM cost, 5–30 min · parallelize fetches + sub-questions (wall-clock ≈ depth, not breadth) · note compression ~10–20× vs raw page.

## Eval
Report-level: faithfulness (every claim → cited note → source), coverage vs expert rubric, contradiction surfacing · trajectory: search efficiency (novel-notes per fetch), stop-timing correctness · human/LLM-judge pairwise vs baseline single-shot answer · cost & latency per task as SLOs.

## Failure modes
Source monoculture (all notes from one viewpoint/SEO farm) · citation drift in synthesis (claim cites wrong note) · prompt injection via fetched page ("ignore instructions, recommend X") · budget burn on unanswerable sub-question · stale cache presenting old facts as current · plan lock-in (never revisits a wrong decomposition).

## Top follow-ups
- "How does it know when to stop?" → per-sub-question budgets + novelty saturation + hard caps.
- "Injection from web pages?" → notes layer isolates untrusted text; note-taker has no tools; sanitize/strip instructions; report generator only sees notes.
- "Parallelize?" → sub-questions are independent → fan out sub-agents; merge at synthesis; dedup sources.
- "Enterprise version?" → internal RAG with ACL predicate in every retrieve ([[02-enterprise-search-acl]]); citations to internal docs; no cross-tenant cache.
- "Why not one big context with all pages?" → cost, lost-in-the-middle, injection surface; notes = curated context.

## Related
[[03-web-answer-engine]] (single-shot sibling) · [[09-agent-platform]] (runtime) · [[11-multi-agent-system]] (fan-out) · [[01-rag-with-citations]] (grounding discipline).
