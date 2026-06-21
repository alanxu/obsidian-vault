---
tags: [job-hunt, interview-prep, question-bank, practical-oo-coding, index]
title: "Practical / OO Coding — Question Bank (canonical)"
scope: "Self-contained practical/OO coding problems (master-plan Track B §3). Delivery-channel-agnostic. 34 files: multi-level ICA + Anthropic live bank + LeetCode Design warm-ups + agentic primitives."
location: "Under `/question-bank/practical-coding/` (the umbrella question-bank folder)."
related: ["[[track-B-practical-oo-coding/practical-oo-coding-deep-guide]]", "[[track-G-take-homes/README]]", "[[interview-prep-master-plan-2026]]", "[[openai-interview-guide]]", "[[anthropic-interview-guide]]", "[[cohere-interview-guide]]"]
count: 35
created: 2026-06-16
updated: 2026-06-18 (all files enriched with full prompts, code, follow-ups, pitfalls, tips)
---

# Practical / OO Coding — Question Bank

**One canonical home** (merged from the old Track B and Track G copies). One file per question; each file documents the problem **and every test format it appears in** (OA, live, take-home, onsite) with **per-format follow-ups, tips, and pitfalls**.

> **Scope (what belongs here):** problems where you **build/extend a stateful object or small system** with a known answer — the multi-level "stateful service" problems, the Anthropic live bank, the minimal agent loop, and the LeetCode **Design**-tagged warm-ups. **Not here:** pure algorithmic puzzles (Track A) and open-ended *project* take-homes like "build a RAG system" (Track G — [[take-home-question-bank]]).
>
> **Why top-level:** this is a shared resource. A problem's *delivery channel* (OA / live / async timed assessment) is **not** its track — these problems are Track B content no matter how a company delivers them. Round mechanics + worked walk-through: [[practical-oo-coding-deep-guide]].
>
> **Runnable code (outside the vault):** these cards are the *study notes*. Runnable solutions + tests live in the git repo **`~/projects/interview-questions/practical-coding/<problem>/`** (run with `python3`). Card ↔ folder map by the same name/number, e.g. `01-in-memory-key-value-database` → `~/projects/interview-questions/practical-coding/01-in-memory-key-value-database/`. (New code Claude generates first lands in `Job Hunt/source-code/`, then is `mv`'d into the repo.)

## Format legend (used in every file's "By format" section)
- **OA · ICA** — CodeSignal Industry Coding Assessment: 1 project, 4 progressive levels, auto-graded on hidden tests, 90 min.
- **OA · GCA/HR** — CodeSignal GCA or HackerRank: single auto-graded problem.
- **Live · CoderPad** — human pair-programming; narrate; progressive follow-ups added live.
- **Take-home** — async build or timed take-home (e.g. Anthropic 90-min assessment).
- **Onsite · NR** — non-runnable shared editor (Google-style): write compilable code by hand; "test" by tracing.
- **Whiteboard** — design/loop discussion (agentic, design-heavy).

---

## Tier 1 — Multi-level "stateful service" (CodeSignal ICA + lab live)
One object, 3–6 escalating levels, never break earlier levels.

| # | Question | LC | Formats | Companies | ⭐ |
|---|---|---|---|---|---|
| 01 | [[01-in-memory-key-value-database]] | — | ICA, Live, Take-home | Anthropic, OpenAI, Meta, Dropbox, Coinbase, Cohere, Netflix, Capital One | ⭐⭐ |
| 02 | [[02-banking-system]] | — | ICA, Live | Anthropic, fintech, CodeSignal cos | ⭐⭐ |
| 03 | [[03-inventory-warehouse-management]] | — | ICA, Live | Anthropic (inventory variant), CodeSignal cos | |
| 04 | [[04-cloud-storage-file-host]] | — | ICA, Live | CodeSignal cos, Anthropic, Dropbox-style | |
| 05 | [[05-expiring-credit-ledger]] | — | Live, Take-home | OpenAI | ⭐ |
| 06 | [[06-gpu-credit-manager]] | — | Live, Take-home | OpenAI | |
| 07 | [[07-versioned-time-based-kv-store]] | 981 | Live, OA·GCA/HR | OpenAI, Databricks | ⭐ |
| 08 | [[08-multi-file-iterator]] | — | Live, Take-home | OpenAI | ⭐ |
| 09 | [[09-cd-directory-navigation]] | — | Live | OpenAI | |
| 10 | [[10-api-log-parser-token-aggregator]] | — | Live, Take-home | OpenAI | |
| 11 | [[11-infection-spread-grid]] | 994-like | OA·GCA/HR, Live | OpenAI, general | |

## Tier 2 — Anthropic live bank
| # | Question | LC | Formats | Companies | ⭐ |
|---|---|---|---|---|---|
| 12 | [[12-multithreaded-web-crawler]] | 1242 | Live, Take-home | Anthropic (#1 live), many | ⭐⭐ |
| 13 | [[13-stack-trace-to-trace-conversion]] | — | Live | Anthropic (viral 2025) | ⭐ |
| 14 | [[14-exclusive-execution-time]] | 636 | Live, OA·GCA/HR | Anthropic | ⭐ |
| 15 | [[15-duplicate-file-detection]] | 609 | Live, Take-home | Anthropic | ⭐ |
| 35 | [[35-sliding-window-rate-limiter]] | — | Live, OA·GCA/HR | Anthropic (phone screen), Stripe, Cloudflare | ⭐ |

> *Agentic questions moved to their own **Tier 4** below. #35 is the general `should_allow` rate limiter (digested from an Anthropic case study); #23 is the simpler #359 logger variant.*

## Tier 3 — LeetCode "Design" warm-ups (pattern primitives)
| # | Question | LC | Formats | Companies | ⭐ |
|---|---|---|---|---|---|
| 17 | [[17-lru-cache]] | 146 | OA·GCA/HR, Live, Onsite·NR | Anthropic, Cohere, broadly all | ⭐⭐ |
| 18 | [[18-lfu-cache]] | 460 | OA·GCA/HR, Live | General | |
| 19 | [[19-insert-delete-getrandom]] | 380 | OA·GCA/HR, Live | General | |
| 20 | [[20-design-file-system]] | 1166 | OA·GCA/HR, Live | General / labs | |
| 21 | [[21-in-memory-file-system]] | 588 | Live, Onsite·NR | General | |
| 22 | [[22-add-search-word-trie]] | 211 | OA·GCA/HR, Live | General | |
| 23 | [[23-logger-rate-limiter]] | 359 | OA·GCA/HR, Live | Fintech / API platforms, Cohere | |
| 24 | [[24-hit-counter]] | 362 | OA·GCA/HR, Live | General | |
| 25 | [[25-design-leaderboard]] | 1244 | OA·GCA/HR, Live | Gaming / general | |
| 26 | [[26-underground-system]] | 1396 | OA·GCA/HR, Live | General | |
| 27 | [[27-encode-decode-tinyurl]] | 535 | OA·GCA/HR, Live | General / SD-lite | |
| 28 | [[28-memory-allocator]] | 2502 | OA·GCA/HR, Live | NVIDIA-adjacent, general | |
| 29 | [[29-range-module]] | 715 | OA·GCA/HR, Live | General | |

> **#981 Time-Based KV** is folded into **07** (it's the LeetCode form of the same problem); see that file.

## Tier 4 — Agentic (rising; agent-focused targets)
"Build me an agent" fragments into these concrete coding sub-problems — now a 2026 baseline at agent-focused shops. Most relevant to **Anthropic, OpenAI, Anysphere, Cognition, Robinhood**. (Design the *platform* → Track D **D3**; build a *full agent* → Track G.)

| # | Question | Formats | Companies | ⭐ |
|---|---|---|---|---|
| 16 | [[16-minimal-agent-loop]] | Live, Whiteboard | Anthropic, OpenAI, Anysphere, Cognition, Robinhood | ⭐ |
| 30 | [[30-function-calling-tool-handler]] | Live, Take-home | OpenAI, Anthropic, Anysphere, Cognition | ⭐ |
| 31 | [[31-retry-with-backoff]] | Live, Take-home | Robinhood, OpenAI, Anthropic | |
| 32 | [[32-streaming-response-handler]] | Live, Take-home | Anysphere, OpenAI, Anthropic | |
| 33 | [[33-conversation-memory-manager]] | Live, Take-home | Anthropic, OpenAI | |
| 34 | [[34-multi-agent-orchestration]] | Live, Whiteboard | agent-platform cos (also D3) | |

> Numbering: 16 predates this tier; 30–34 added 2026-06-16. The six together are the agentic group.

## Excluded (and why)
- **Pure algorithmic** (top-k decoding, longest-substring, binary-string reduction, streaming top-k): Track A. Even when a coding round uses them, they're not "build a stateful object."
- **Open-ended project builds** (RAG system, agent product, doc-extraction): Track G → [[take-home-question-bank]].
- **Anthropic thin one-offs** (image grayscale/scale; parse-URLs-count-domains → see [[12-multithreaded-web-crawler]]; "scale token-gen to 100k req/s" → Track C/D system design): too underspecified for a file.

## What each file contains

Every question file follows the same shape (see any one for the pattern):

1. **Frontmatter** — `companies`, `formats`, `levels`, `time-box`, `tags`, `related`.
2. **Problem (by level/part)** — full signatures with types, return-type contracts, edge-case list.
3. **Core approach** — the design primitive, trade-offs named out loud, **worked tested code** (Python) with complexity analysis.
4. **By format** — separate subsections per delivery channel (OA · ICA, OA · GCA/HR, Live · CoderPad, Take-home, Onsite · NR, Whiteboard). Each lists:
   - **How it appears** in that format
   - **Follow-ups** (5–10 real, reported probes in priority order)
   - **Tips** (actionable, with timing/economics)
   - **Pitfalls** (with explanations of why each fails)
5. **Company variants** — concrete reskins (signatures / behaviors) by employer.
6. **Worked example trace** — for narration during the interview.
7. **Related** — cross-links to siblings in the bank.

## How to use
1. Make **[[01-in-memory-key-value-database]]** and **[[17-lru-cache]]** automatic first — together ~80% of the pattern.
2. Read the **"By format"** section for the format your target company uses (see each file's `companies`/`formats`), and rehearse those follow-ups.
3. Re-implement from a blank file, **timed, in a bare web editor** (not your IDE) — [[practical-oo-coding-deep-guide]] §6.5.
4. **Agent-heavy targets** (Anthropic, OpenAI, Anysphere, Cognition, Robinhood) → drill **Tier 4** (the agentic group): the loop, tool handler, retry, streaming, memory, multi-agent.
5. For each new target, scan its **company variants** section — most firms have a recognizable skin of the underlying primitive.

*Enriched 2026-06-18 (full prompts + worked code + comprehensive follow-ups/pitfalls/tips per file). Merged & relocated 2026-06-16. Canonical home for practical/OO coding questions; Tracks B and G point here.*
