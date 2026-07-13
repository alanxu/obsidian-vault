---
tags: [job-hunt, playbook, memory, sop, question-sourcing, research]
title: "Question-Sourcing Playbook (memory / SOP)"
purpose: "How to FIND interview questions from published sources before concluding 'nothing new / not found'. Read this whenever the user asks whether a company has new/recent questions, or asks about a named problem."
created: 2026-07-13
related: ["[[inbox-digest-playbook]]", "[[plans/practical-coding-tools-platforms-2026-06-16]]", "[[question-bank/practical-coding/README]]"]
---

# Question-Sourcing Playbook (memory)

> **Why this exists:** when asked "does Anthropic have new coding questions?", a prior run searched only generic SEO aggregators, found nothing new, and said so — then the user named the **"Bootloader" problem**, which a targeted **1point3acres / 面经** search surfaced immediately (thread 1178806). The lesson: *generic search returning nothing ≠ nothing exists.* Never conclude "not found in published sources" until the **primary candidate-report tier** has actually been queried, in both English and Chinese.

## The cardinal rule
**Do not claim "no new/found questions" until you've searched the PRIMARY sources below — including Chinese-language 面经 and login-gated thread titles.** If still not found, report *what you searched* and that it's *unconfirmed*, never a flat "it doesn't exist."

## Source tiers (search top-down; trust top-down)

**Tier 1 — primary candidate reports (highest signal: "actually asked").** Always hit these before concluding anything:
- **1point3acres (一亩三分地)** — `1point3acres.com/interview/...` threads and `/bbs/` 面经. The single best source for lab/Anthropic OA + phone-screen reports. Search in **Chinese**: `<company> 面经`, `<company> OA`, `<company> CodeSignal 题`, `<company> 电面`.
- **LeetCode Discuss** — search `<company>` + `OA` / `Industry Coding Assessment` / `online assessment`; candidate-posted problems + solutions.
- **Glassdoor** → Interview experiences for the company/role.
- **Blind (teamblind.com)** — recent OA/loop chatter.
- **interviewing.io** — company pages (e.g. Anthropic) with concrete reported problems.
- **csoahelp.com** — posts the actual ICA problems (in-memory DB, banking, etc.) with walkthroughs. (Use for *published problems only* — never the proxy/cheating service; Anthropic disqualifies for AI-in-OA.)

**Tier 2 — curated aggregators (corroborate, don't discover).** SEO content, often recycled/stale: Exponent, IGotAnOffer, InterviewQuery, PracHub, linkjob.ai, YouTube "top N questions". Use to confirm a Tier-1 finding or the interview *structure*, not as proof something is or isn't asked.

**Tier 3 — open graders / practice repos.** LibreSignal (GitHub), CodeSignal Practice/Learn, `PaulLockett/CodeSignal_Practice_Industry_Coding_Framework`, other GitHub ICA repos. Good for reference solutions + graders once you know the problem.

## Technique that finds things generic search misses
1. **Search bilingually.** Chinese 面经 posts carry far more lab OA detail than English SEO pages. Run the Chinese query even if the user wrote English.
2. **Target the domains.** Use `WebSearch` with `allowed_domains` set to Tier-1 sites (`1point3acres.com`, `leetcode.com`, `glassdoor.com`, `interviewing.io`) — cuts through SEO noise.
3. **Read login-gated pages via their metadata.** 1point3acres `/interview/thread/<id>` bodies are login-gated, but the **page title + meta-description usually name the problem and its shape** ("bootloader problem with instructions handling and loop detection"). `web_fetch` the URL and read the meta — that's enough to confirm existence and reconstruct structure.
4. **Quote the problem name.** If the user names a problem ("Bootloader problem"), search it as a quoted string across Tier-1 domains before saying you can't find it.
5. **Recognize canonical reskins.** Many "named" prompts are reskins of well-known problems — reconstruct the spec from the known structure even when the report is thin:
   - **Bootloader** = "Handheld Halting" instruction VM (`acc/jmp/nop`, loop detect, one-swap repair).
   - **Banking system / in-memory DB / cloud storage / file cache** = the canonical CodeSignal **ICA 4-level** projects.
   - **Stack samples → trace / longest-running function** = execution-profiling on a call stack.
   Map first, then verify the details against the report.

## After you find one — hand off to digestion
Once a question is confirmed, digest it per **[[inbox-digest-playbook]]**: understand → enrich → place correctly. For practical/OO problems that means a full **card** in `question-bank/practical-coding/` **and** a runnable project (`.py` + stdlib `unittest` tests) in `interview-questions/practical-coding/<n>-<slug>/`, then **run the tests** to verify. Number the card by the **next free number across the repo AND vault** (they can diverge — check both, e.g. Bootloader became #42, not #36).

## Anti-patterns (what went wrong before — don't repeat)
- ❌ "No genuinely new questions" after only Tier-2 aggregator searches.
- ❌ Treating a login-gated page as a dead end without reading its title/meta.
- ❌ Searching only in English for a company with heavy Chinese-forum coverage.
- ❌ Trusting one SEO aggregator's list as authoritative.
- ✅ Instead: sweep Tier-1 (EN + 中文) → corroborate → if still empty, state the exact sources checked and call it *unconfirmed*.

## Quick checklist (paste into working notes)
- [ ] Tier-1 English: 1point3acres, LeetCode Discuss, Glassdoor, interviewing.io
- [ ] Tier-1 中文: `<company> 面经 / OA / CodeSignal 题 / 电面`
- [ ] `allowed_domains` targeted at primary sources
- [ ] Named problem searched as a quoted string
- [ ] Login-gated hits: read title + meta-description
- [ ] Mapped to a canonical structure if it's a reskin
- [ ] If found → digest (card + runnable code + tests, verified)
- [ ] If not found → report sources checked + "unconfirmed", not "doesn't exist"
