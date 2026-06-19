---
tags: [job-hunt, playbook, memory, sop, inbox-digest]
title: "Inbox-Digest Playbook (memory / SOP)"
purpose: "How to digest Notion brain-inbox notes into the Job Hunt vault PROPERLY. Read this before processing the inbox (manual or weekly task)."
created: 2026-06-19
---

# Inbox-Digest Playbook (memory)

> **Why this exists:** a prior run digested a saved ChatGPT conversation (a 100-question Anthropic interview bank) by just copying the *short question titles* into one mis-located file. That's a table of contents, not digestion. This playbook is the standard so it never happens again.

## The cardinal rule
**Understand → enrich → place correctly. Never copy/list.** A digest is *not* a link dump or a list of titles. For each piece of substance in a note, produce a **proper, enriched artifact** in the **correct vault location**, matching the standard of the surrounding files.

## Step 0 — Read and actually understand the source
- Open the link/note and read the *content*, not the title. For JS-gated links (ChatGPT share) use Claude-in-Chrome. For blocked domains (xiaohongshu/rednote/xhslink) — leave in inbox, ask the user to paste.
- Identify the **atomic items** inside (each question, each problem, each company, each concept) — these become individual artifacts.

## Step 1 — Classify each atomic item, then route it
Match each item to the EXISTING structure (don't invent new top-level structure unless a whole new category appears):

| Item type | Goes to | Granularity |
|---|---|---|
| Practical / OO coding problem (build a stateful object) | `question-bank/practical-coding/` | one enriched file per problem |
| Algorithmic / DSA problem | `question-bank/algorithmic-coding/` | one per problem |
| Distributed system-design prompt | `question-bank/distributed-system-design/` | one per prompt |
| **LLM/ML system-design prompt** (Design X) | `question-bank/llm-system-design/` | one per prompt (map to an existing card if already covered) |
| **LLM/ML concept / "explain X" Q** (fundamentals: attention, RAG concepts, agent concepts, decoding, eval terms) | `question-bank/llm-fundamentals/` | one enriched concept card per question (merge only truly-paired Qs) |
| Behavioral / values / "why company" Q | `track-F-behavioral-staff-values/` | story-bank / per-company hooks |
| Company interview *intel* (process, OA-vs-onsite, rounds, comp) | `plans/` | a research/intel note |
| Tooling / platform info | `plans/` | a snapshot note |

**The placement test:** ask *"is it fundamental, a design prompt, a coding problem, behavioral, or intel?"* — that answer is the folder. Do **not** put non-fundamentals in Track E. Do **not** put concept Q&A in the system-design bank.

## Step 2 — Enrich every item to the bank standard
Each question/problem file must have (matching existing cards):

- **Frontmatter:** `title · slug · type/area · companies · difficulty · related ([[wikilinks]])` (+ `formats`/`leetcode` where relevant).
- **Prompt** — the actual question/problem, plus realistic variants.
- **Answer / solution** — a real model answer or worked solution (code for coding, architecture for design, a crisp explanation for concepts). Not a one-liner.
- **Tradeoffs** — the decisions and what each costs (table where useful).
- **Follow-ups** — the rapid-fire extensions an interviewer adds, each with a crisp answer.
- **Pitfalls** — what graders/interviewers penalize.
- **Tips** — how to perform well.
- Cross-link related cards and the framework docs ([[D0-areas-map]], deep guides).

If an item is **already covered** by an existing card → don't duplicate; cross-reference it (and enrich the existing card if the new source adds a follow-up/pitfall).

## Step 3 — Index + archive
- Update/produce the area **README index** so the new items are discoverable (table: # · question · companies · difficulty).
- **Dedup by content, not title:** if an inbox item's title matches an existing vault file, FETCH and DIFF the content before treating it as a duplicate (a Notion page may have edits the vault lacks).
- Move the processed Notion page to `brain → 05 — Archives` (page id `380eab7d-16c7-8136-96a8-d6262e369c62`); append to `archives/README.md`; link-only pages → `archives/shared_link.md`. Unreadable links → **leave in inbox**, note under "Left in inbox."

## Anti-patterns (do NOT do these)
- ❌ Copy the list of question *titles* into one file and call it digested.
- ❌ Dump multi-topic content into a single track folder because it's convenient.
- ❌ Put design prompts in the fundamentals bank, or concept Qs in the design bank, or anything non-fundamental in Track E.
- ❌ Skip enrichment (no answer/tradeoffs/follow-ups/pitfalls/tips).
- ❌ Assume a title-match means duplicate without diffing content.

## Quick reference — the vault map
`plans/` = guides/research/intel · `track-A…G/` = per-skill prep + deep guides · `question-bank/{practical-coding, algorithmic-coding, distributed-system-design, llm-system-design, llm-fundamentals}/` = canonical enriched question banks · `archives/` = processed-inbox log + shared links · `interview-prep-master-plan-2026.md` = master plan.

*Memory created 2026-06-19 after a bad digest. The weekly `weekly-notion-inbox-digest` task must follow this playbook.*
