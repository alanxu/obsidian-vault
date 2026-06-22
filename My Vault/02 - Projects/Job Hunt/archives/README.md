---
tags: [job-hunt, archives, index, notion-inbox]
title: "Archives — processed Notion inbox log"
purpose: "Log of items digested from the Notion 'brain → 00 — Inbox' and where they landed. Prevents re-processing on weekly runs."
updated: 2026-06-22
---

# Archives — Processed Inbox Log

Record of Notion **brain → 📥 00 — Inbox** items processed into this Job Hunt vault. After digesting, the source Notion page is moved to **brain → 05 — Archives** (so the inbox stays clean and weekly runs don't reprocess). Link-only pages are tracked in [[shared_link]].

## Processed log

| Date | Notion item | Type | Disposition |
|---|---|---|---|
| 2026-06-19 | Anthropic Interview Guide for Non-ML Engineers (2025–2026) | full page | **Duplicate** — content **verified identical** (2026-06-19) to `plans/anthropic-interview-guide.md`. No new digestion needed; Notion page → 05 — Archives. |
| 2026-06-19 | AI IPO Interview Guide — 12 Companies | full page | **Duplicate** — content **verified identical** (2026-06-19) to `plans/ai-ipo-interview-guide.md`. No new digestion needed; Notion page → 05 — Archives. |
| 2026-06-19 | 准备Anthropic SWE面试 (ChatGPT share) | link-only | **Digested (properly re-done 2026-06-19).** OA-vs-onsite intel → [[plans/anthropic-oa-vs-onsite]]; the 100-question bank → **21 enriched concept cards** in [[question-bank/llm-system-design/fundamentals/README]] + design Qs mapped onto [[llm-system-design/README]] + behavioral → Track F. Logged in [[shared_link]]; Notion page → 05 — Archives. *(First pass was a shallow title-list in Track E — deleted; standard now codified in [[inbox-digest-playbook]].)* |

## Left in inbox (not processed)
| Date | Notion item | Reason |
|---|---|---|
| 2026-06-19 | (untitled Xiaohongshu link) | Not accessible (see [[shared_link]] → Pending). Re-try when content can be pasted. Re-checked 2026-06-22 (weekly run): still the same unprocessed item, xhslink domain still blocked — left as-is, no other new inbox items this week. |

## Other digested sources (pasted in chat, not the Notion inbox)
| Date | Source | Digested into |
|---|---|---|
| 2026-06-19 | "Anthropic SDE 上岸 面经" case study (images) — Q1 rate limiter, Q2 web crawler | Q1 → new card [[question-bank/practical-coding/35-sliding-window-rate-limiter]]; Q2 → enriched [[question-bank/practical-coding/12-multithreaded-web-crawler]] (added async/aiohttp variant + full frontier/downloader/parser/storage architecture). Author not senior → **senior-review** notes added to both. |

## How the weekly run works
1. Read Notion `brain → 00 — Inbox`.
2. For each item **not already in this log**: digest into the right Job Hunt area (tracks / plans / question-bank).
3. Move the processed Notion page to `brain → 05 — Archives`; append a row here. Link-only pages also get a row in [[shared_link]].
4. If a link can't be accessed, **leave it in the inbox** and note it under "Left in inbox."

*Maintained by the weekly inbox-digest scheduled task.*
