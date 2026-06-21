# 🎯 Job Hunt

Active project. Goal: land an offer at a top AI/AI-adjacent company (priority: Anthropic).

## Conventions (working agreement)
- **Save everything to markdown.** Any substantive answer Claude gives in chat must also be written into an `.md` file in this vault (the relevant track folder or `plans/`) — chat is not the system of record. Backfill if something was answered only in chat.
- Folder layout: `plans/` = guides, research, master plan · `track-A … track-G/` = per-track prep material · `question-bank/` = the canonical question bank by area: `practical-coding/` (35 enriched files), `algorithmic-coding/`, `distributed-system-design/`, `llm-system-design/` (+ `llm-system-design/fundamentals/` concept sub-bank) · `README.md` = index.
- **Runnable code lives OUTSIDE the vault** — a git repo at **`~/projects/interview-questions/`** whose subfolders mirror the bank (e.g. `practical-coding/01-in-memory-key-value-database/` with `*.py` + tests; run with `python3`). Split: the **vault = notes/banks**, the **repo = runnable code**. Claude can only write inside this vault, so any code it generates lands in `Job Hunt/source-code/` and is then `mv`'d into the repo (the `source-code/` staging dir is normally empty).
- Boundary: **Track B** = implement a stateful component (→ `question-bank/practical-coding/`). **Track G** = build a small project take-home (RAG/agent/doc-extraction). Delivery channel (OA/live/async) ≠ track.
- Cite sources in-file; verify present-day facts before stating them.

## Status
- **Focus target**: Anthropic (SWE / Applied AI / FDE)
- **Pipeline**: 12 companies tracked — see [[ai-ipo-interview-guide]]
- **Prep depth**: deep-read done on Anthropic — see [[anthropic-interview-guide]]
- **Next action**: drill the coding bank (in-memory DB, web crawler, LRU cache, duplicate files) under timed conditions

## Source material

| File | What it is |
|---|---|
| [[ai-ipo-interview-guide]] | 12-company IPO + interview comparison (Anthropic, OpenAI, Databricks, xAI, Anysphere, Scale, Perplexity, Cohere, Anduril, Mistral, Harvey, Glean) — rendered as Markdown for Obsidian |
| [[anthropic-interview-guide.md]] | Full guide: SWE / Applied AI / FDE interview loop, coding bank, values round, AI-usage policy, comp context |

The same two files are also mirrored as Notion sub-pages under [[Inbox 00]] (inbox-side) and tracked in Notion `02 — Projects`.

## Prep checklist
- [ ] Drill the Anthropic coding bank (4 problems × multiple levels)
- [ ] Read Anthropic's Responsible Scaling Policy
- [ ] Form a genuine point of view on AI safety
- [ ] Practice the values round with a peer (it's the #1 failure point)
- [ ] Apply to 3+ companies per week
- [ ] Track all applications and follow-ups

## Notes
_(link daily/weekly notes here as the project progresses)_

## Related
- [[01 - Daily Notes]] — daily context
- [[03 - Areas]] — Career area (long-term positioning)
