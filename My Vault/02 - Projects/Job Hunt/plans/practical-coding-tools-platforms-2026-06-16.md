---
tags: [job-hunt, interview-prep, tools, platforms, practical-coding, codesignal, coderpad]
created: 2026-06-16
updated: 2026-06-16
status: snapshot
data-freshness: 2026-06-16 — platforms/policies change; verify with recruiter
related: [[interview-prep-master-plan-2026]], [[track-B-practical-oo-coding/practical-oo-coding-deep-guide]]
---

# Practical-Coding Tools & Platforms (2026)

> The tools you'll be **tested on** vs. the tools you **practice with**, for the practical/OO coding round (Track B). Mapped to the 12 target companies where known.

## A. Assessment platforms companies test you on

| Tool                                                                                  | Mode                                                      | Used by (your targets)                                                                                                     | What it means for you                                                                  |
| ------------------------------------------------------------------------------------- | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **CodeSignal** — ICA & GCA, proctored https://app.codesignal.com/assessments/practice | Async OA; auto-graded; portable "Coding Score"            | **Anthropic** (ICA + live), **Robinhood**, **xAI**, **Anysphere** (also Meta / Netflix / Capital One / Dropbox / Coinbase) | In-browser, no IDE/autocomplete; ICA = the 4-level project; run hidden tests as you go |
| **CoderPad**                                                                          | Live pair-programming, 99+ langs, code playback           | **OpenAI**, **Notion**, **Lyft**, NVIDIA phone screens                                                                     | Narrate aloud; interviewer watches keystrokes; runnable but minimal tooling            |
| **HackerRank**                                                                        | Async OA + live "Interviews"                              | Broadly used; some big-tech screens                                                                                        | Largest question bank; auto-graded MCQ + coding                                        |
| **Codility**                                                                          | Async, strong plagiarism detection                        | Common at enterprises / fintech                                                                                            | Unsupervised but heavily monitored — don't paste                                       |
| **Karat**                                                                             | Outsourced live interview-as-a-service                    | Companies that outsource first rounds                                                                                      | A Karat engineer (not the company) interviews you; structured rubric                   |
| **HackerEarth / Coderbyte**                                                           | Async OA                                                  | Smaller / older funnels                                                                                                    | Similar to HackerRank                                                                  |
| **Google Hiring Assessment + onsite editor**                                          | Proprietary; shared Google-Docs-style / Chromebook editor | **Google**                                                                                                                 | No code execution at onsite — write compilable code by hand                            |
| **Take-home in a Git repo** (GitHub/GitLab)                                           | Async build, submitted as repo                            | **Cohere** (analysis + presentation), **OpenAI** work-trial, **Harvey**, **Together**                                      | Graded on tests + README + structure; see [[track-G-take-homes/README]]                |
| **Notebook tools** (Jupyter / Colab / Hex / Deepnote)                                 | ML / data take-homes                                      | ML / research roles (Cohere, Together)                                                                                     | For data-analysis deliverables                                                         |
| **Video + shared editor** (Zoom / Meet + the above)                                   | Onsite loops                                              | Most                                                                                                                       | Camera/mic on; some require screen-share                                               |

**AI-era shift (2026):** CodeSignal and CoderPad now ship **AI-assisted and "agentic" assessment modes**, and some companies (e.g., **Notion's "AI-enabled round"**) explicitly let you code *with* an LLM — so confirm each company's **AI-usage policy** before the round.

## B. Tools to practice with

- **LeetCode** — problems by number + the "Design" tag; in-browser editor mimics OA conditions
- **NeetCode** — the 150 roadmap (Track A backbone)
- **CodeSignal's own practice** + the community **ICA practice repo** — rehearse the exact 4-level format
- **Pramp** and **interviewing.io** — live mock interviews with real humans (use from Week 6)
- **Replit / Google Colab / a bare web editor** — practice with **no IDE autocomplete** (the real OA condition)
- **Local plain editor + Python REPL** — timed self-drills

## Key prep implication
The labs/fintech that gate on **CodeSignal ICA** and **CoderPad** give you a **minimal, no-autocomplete, run-the-tests-yourself** environment. So practice in **Replit / Colab / CodeSignal practice**, not your fully-loaded IDE, and get fluent with the **Python stdlib by hand** (`bisect`, `heapq`, `collections`, `dataclasses`).

## C. Where to get real practical/OO question banks WITH solutions (so you don't rely on AI-curated)
> **Key constraint:** the actual **CodeSignal ICA** problems are CodeSignal's proprietary IP — **nobody legally sells "the real Anthropic/Meta ICA bank."** But the *problems* (in-memory DB, banking) are heavily reused, so a few canonical ones cover most of the surface. Treat our `question-bank/practical-coding/` as the **digest**; use these as the **primary sources + graders** to practice against.

**Free — real problems + solutions + grader:**
- **CodeSignal Practice** — https://app.codesignal.com/assessments/practice — the actual ICA/ICF format in the real IDE; source of truth for the format. + **CodeSignal Learn** courses.
- **LibreSignal** (open-source) — https://github.com/EricZheng0404/LibreSignal — multi-level (L1–4) **banking + in-memory DB** with **reference solutions + test suites**. Closest free "practice the canonical problems with a grader."
- **LeetCode Discuss → "Industry Coding Assessment" threads** — real candidate-posted ICA problems (eBay/Coinbase/etc.) + community solutions, e.g. https://leetcode.com/discuss/post/7302772/
- **Community ICA practice repo** — https://github.com/PaulLockett/CodeSignal_Practice_Industry_Coding_Framework

**Paid — real questions + human-backed practice:**
- **interviewing.io** — company-specific guides (incl. Anthropic) + question database + **live mocks with FAANG/lab engineers**. Best paid option for "actually asked" + non-AI practice.
- **Exponent (tryexponent.com)** — subscription; company question banks + coding/system-design + mocks; covers AI companies.
- **1point3acres (一亩三分地)** — real candidate ICA reports (some points-gated); **csoahelp.com** posts the actual problems (in-memory DB, banking) with walkthroughs.

**Adjacent (only if you also have an OOD round):** DesignGurus / Educative **"Grokking the Object-Oriented Design Interview"** — OOD (parking lot, etc.), *not* CodeSignal-ICA.

**⚠️ Avoid:** "OA 代做" / "undetectable AI interview assistant" services (some csoahelp/linkjob/lockedinai offerings). They **violate company policy — Anthropic explicitly prohibits AI in OAs/take-homes and disqualifies for it.** Use those sites only for the *published problems/solutions*, never the proxy/cheating service.

**Recommendation:** paid + comprehensive + human → **interviewing.io** (or Exponent). Free real problems+solutions+grader → **CodeSignal Practice + LibreSignal + LeetCode Discuss**.

## Sources
- HackerRank — best coding assessment tools 2026: https://www.hackerrank.com/writing/best-coding-assessment-tools
- HackerRank — remote technical screening tools Q1 2026: https://www.hackerrank.com/writing/remote-coding-interviews-best-technical-screening-tools-q1-2026
- Playcode — best coding interview platforms 2026: https://playcode.io/blog/best-coding-interview-platforms-2026
- SelectSoftware Reviews — coding interview tools: https://www.selectsoftwarereviews.com/buyer-guide/online-coding-interview-tools
- CodeSignal — AI-assisted / agentic assessments: https://codesignal.com/newsroom/press-releases/codesignal-launches-ai-assisted-coding-assessments-and-interviews-redefining-technical-hiring-in-the-ai-era/

*Snapshot 2026-06-16. Companion to [[interview-prep-master-plan-2026]] and the Track B deep guide.*
