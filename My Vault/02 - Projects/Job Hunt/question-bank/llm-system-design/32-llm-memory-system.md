---
title: Design a Long-Term Memory System for an Assistant
slug: llm-memory-system
area: 3 — Agentic Systems
companies: [OpenAI, Anthropic, Anysphere, Robinhood, "any assistant product"]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[fundamentals/18-agent-memory]]", "[[09-agent-platform]]", "[[practical-coding/33-conversation-memory-manager]]", "[[01-rag-with-citations]]"]
added: 2026-07-08 (audit fill — standard 2026 senior prompt)
evidence: "GUIDE-LEVEL: 'how do you design long-term memory without polluting it' + memory-types questions appear in 2026 AI-eng interview compilations (adilshamim8 Medium '100+ real interviews', Callsphere agentic guide). Company list is domain inference — no candidate report ties this prompt to a specific target."
---

# Design a Long-Term Memory System for an Assistant

> "Design ChatGPT/Claude memory: the assistant remembers facts about the user across sessions." **Open with:** memory = **write path (what to store) + read path (what to inject) + lifecycle (update/decay/delete)** — most candidates only design the read path. The hard part is *precision*: a wrong or stale memory is worse than no memory.

## Problem
"Users chat daily; the assistant should recall preferences, facts, and past decisions across sessions. Design it for 100M users." Variants: agent memory (task episodes), team/org shared memory, "memory without polluting it."

## Clarify first
- Memory of *what*: user facts/preferences vs episodic (past conversations) vs procedural (learned workflows)?
- Explicit ("remember this") vs implicit (extracted silently)? User-visible/editable? Privacy/deletion (GDPR) requirements?
- Read latency budget (in the hot path of every message)?

## Architecture
**Write path (async, off hot path):** after each session/turn-batch → **extraction LLM** proposes candidate memories (fact, category, confidence, source turn) → **dedup/merge against existing** (semantic match → update vs insert vs contradict) → store: **fact store (structured, per-user)** + **episodic store (embedded summaries)** + raw transcript pointer. **Read path (hot, <50ms):** retrieve by **semantic similarity + recency + importance** → rank, cap k → inject into system prompt as labeled block. **Lifecycle:** confidence decay, contradiction resolution (new overrides old, keep provenance), user-visible CRUD, hard-delete on request.

## Deep-dive — the write path (where quality is won)
- **Selectivity beats recall:** store little, store well. Extraction gate: is it stable (not "I'm hungry"), user-specific, useful later? Otherwise memory bloat → retrieval noise → wrong injections.
- **Update-vs-insert** is the core operation: new candidate → semantic search existing → same fact (skip/refresh timestamp), refinement (merge), contradiction (supersede + keep history). This is why the store is *structured facts*, not raw chunks.
- **Provenance:** every memory links to source conversation — enables user audit, debugging, and trust.
- **Isolation:** memory is per-user PII — encrypt, never cross-tenant, never into training. Injection framing: memories are *context, not instructions* (prompt-injection surface if extraction stored attacker text → sanitize on write).

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Extract per-turn vs per-session | freshness vs cost + noise |
| Structured facts vs raw-chunk RAG | precise updates/deletes vs simpler pipeline |
| Inject always vs retrieve-on-demand | recall vs token cost + distraction |
| Confidence threshold high vs low | miss facts vs pollute context |
| LLM-merge vs rule-merge | quality vs cost/latency of write path |

## Numbers
Read path budget ~30–50ms (vector + KV lookup) · inject ≤ ~1–2K tokens of memory (competes with task) · write path: 1 extraction call per session ≈ +2–5% total LLM cost · fact store per user: hundreds of facts, not millions — it's a curated set.

## Eval
Memory precision (injected memory was relevant/correct — LLM-judge + user feedback) · recall on planted-fact probes ("user said X three sessions ago") · contradiction rate · downstream A/B: task success / thumbs-up with memory on vs off · deletion compliance audit.

## Failure modes
Stale memory injected after user changed preference · memory bloat → retrieval noise · cross-user leakage · injected memory treated as instruction (injection) · extraction hallucinating facts never said · deletion that misses derived copies (summaries, caches).

## Top follow-ups
- "How do you avoid polluting memory?" → extraction gate + confidence + dedup/merge + decay; store facts, not transcripts.
- "Handle contradictions?" → supersede with provenance; recency wins, keep history for audit.
- "Memory vs long context?" → retrieval is cheaper and scales across sessions; long context can't span months and costs per-call.
- "GDPR delete?" → hard-delete fact + derived summaries + embeddings; provenance links make derived copies findable.
- "Shared team memory?" → ACL on memory rows (same as [[02-enterprise-search-acl]]) + write-attribution.

## Related
[[fundamentals/18-agent-memory]] (concept) · [[practical-coding/33-conversation-memory-manager]] (code the budget) · [[09-agent-platform]] (memory as platform component) · [[01-rag-with-citations]] (read path is RAG).
