---
tags: [job-hunt, interview-prep, track, take-home, per-company]
track: "Track G — Take-homes & work trials"
plan-section: "§7.5"
parent: [[README]]
related: [[cohere-interview-guide]], [[anthropic-interview-guide]], [[openai-interview-guide]], [[take-home-question-bank]], [[github-examples]]
compiled: 2026-06-17
---

# Per-company take-home notes — rules, process, format, window

> Companion files: [[take-home-question-bank]] (concrete prompts) · [[github-examples]] (real repos).
> **Confidence**: ✅ recruiter/official-confirmed · 🟡 candidate-reported · 🟥 inferred. Always re-confirm the *current* loop with your recruiter — these processes move fast.

The single biggest landscape fact: of 51 AI-eng companies with disclosed processes (Q4'25/Q1'26), **~33% include a take-home or async assignment**, and another ~10% use **paid work-trials** instead. The take-home is a *delivery format* — it repackages coding / system-design / ML work as async, on-your-own-time. It is a **relative advantage for you** (infra-strong, more time than a 45-min live round) *if* treated as a scored work sample. Most candidates lose on **scope, polish, and communication**, not raw ability. ([field guide](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/questions/06-home-assignments.md))

---

## Quick-reference matrix

| Company | Type | Window | Pass / weight | Graded on | AI allowed? |
|---|---|---|---|---|---|
| **Cohere** ✅ | Analysis + write-up/demo | ~48 hr | ~30% pass; gating round | Engineering judgment + **communication**, not just runnable code | Not stated → assume disclose-and-use |
| **OpenAI** ✅ | Paid work-trial / build | ~48 hr (reported ~$1k) | Make-or-break round | Production code quality, tests, README, scope/design | Practical roles: yes; live rounds: no |
| **Anthropic** ✅ | Timed coding (CodeSignal) | 90 min (was 2–4 hr) | Progressive levels | Correctness + clean incremental design under time | **No, unless they explicitly say so** (official) |
| **Harvey** 🟡 | Short take-home + pairing | ~1 hr take-home | 1 of 3–5 rounds | Coding + the *defense*/pairing that follows | Not stated |
| **Anysphere / Cursor** ✅ | Paid onsite project on real codebase | 4–8 hr (the decision round) | *The* signal | Senior-IC judgment; reject bad AI output | **Yes — GPT/Cursor openly encouraged** |
| **Together AI** ✅ | Realistic build | 4–8 hr | Senior/research roles | Inference: CUDA kernel; platform: systems problem | Not stated |
| **Mistral** 🟡 | Take-home assignment | (1 of 7 rounds) | Part of long loop | Applied build + value-fit | Not stated |

Companies that **don't** use take-homes (live loops / CodeSignal OAs instead, so don't over-prepare a build for them): **Google, NVIDIA, Waymo, Lyft, Robinhood** (Robinhood uses a timed CodeSignal OA, not an open build), **Wealthsimple** (pair-programming + "bring your own system"). See [[interview-prep-master-plan-2026]] §8.

---

## Cohere ✅ — *your highest-leverage take-home*

**Type**: Analysis + write-up/presentation (the "narrative" archetype). This is the one your coding-heavy prep does *not* cover.
**Window**: ~48 hours.
**Where in loop**: Stage 3 of ~4 (after HR screen + 1-hr OA), before the virtual onsite. **Gating round, ~30% pass** (recruiter-confirmed).
**Deliverable**: One or two open-ended prompts on a Cohere-relevant scenario. Submit as a **notebook, report, or demo**. You then defend it in a later round.
**Graded on**: "Not just solving the problem, but explaining *why* a particular method was chosen and potential optimizations or limitations." Analytical thinking, **engineering judgment, and communication** — organizing thoughts, presenting a clear solution, high-quality analysis under time. *Difficulty is less about algorithms, more about clarity.*
**Approach that wins** (see [[cohere-analysis-presentation-playbook]] when built): lead with the **insight/answer**, then support it; 2–3 clean visuals, cut the rest; tie to **enterprise reality** (cost, latency, data residency, deployment) — Cohere's whole positioning; rehearse the **verbal walkthrough** to time.
**AI policy**: not publicly stated. Default to using AI well *and disclosing how* — appropriate for an applied-AI role.
Sources: [[cohere-interview-guide]] · [linkjob](https://www.linkjob.ai/interview-questions/cohere-interview-process-and-questions/) · [Taro](https://www.jointaro.com/interviews/companies/cohere/?tab=experiences)

## OpenAI ✅ — paid work-trial

**Type**: Open-ended practical build (paid work-trial); sometimes a paid on-site work day.
**Window**: ~48 hours. Reported as paid (~$1,000) for the trial. 🟡 Confirm with recruiter.
**Where in loop**: After the technical screen (CoderPad); "the make-or-break round most candidates underprepare for."
**Deliverable**: Build something *real* — reported example: a **webhook delivery system**. Graded on **reliability, code quality, and testing — not feature count**.
**Graded on**: real production code — shipping speed, code structure, design choices, how you write tests in 48 hr. **A detailed README explaining design choices is a major plus.** "They don't care how fast you finish."
**Prep**: ship one production-quality, LLM-adjacent project in 48 hr *before* the real one — small scope, README, tests, timed. The compressed timeline is the hard part, not the coding.
**AI policy**: practical roles generally allow AI tooling; **no AI in live rounds**.
Sources: [interviewcoder](https://www.interviewcoder.co/blog/openai-interview-process) · [interviewing.io](https://interviewing.io/openai-interview-questions) · [OpenAI official guide](https://openai.com/interview-guide/) · [[openai-interview-guide]]

## Anthropic ✅ — timed assessment, AI *off* by default

**Type**: Timed coding assessment (CodeSignal), **not** an open build. Progressive levels.
**Window**: **90 min** most commonly (site mentions a 60-min live variant for some roles). The *original* perf take-home was 4 hr → 2 hr; now open-sourced (see [[github-examples]]).
**Deliverable**: A task that gets **progressively more complex** — reported example: *implement a bank with multiple transaction types* (same family as your in-memory-DB / ledger bank in [[practical-oo-coding-deep-guide]]).
**Graded on**: correctness + clean incremental design under time, without breaking earlier levels. Prep = your Track A/B work; no special build needed.
**AI policy** — ⚠️ **the myth-buster, from Anthropic's official page**: *"During take-home assessments — complete these without Claude unless we indicate otherwise… We'll be clear when AI is allowed (e.g. 'You may use Claude for this coding challenge')."* So the **default is NO AI**; some ML/prompt roles get an explicit green light. Encouraged: AI for *prep* and *resume refinement*. Not allowed: AI writing your assessment code unless permitted. They keep **redesigning the test** as each Claude model gets better at it.
Sources: [Anthropic official AI-usage policy](https://www.anthropic.com/candidate-ai-guidance) · [Anthropic: designing AI-resistant evaluations](https://www.anthropic.com/engineering/AI-resistant-technical-evaluations) · [TechCrunch](https://techcrunch.com/2026/01/22/anthropic-has-to-keep-revising-its-technical-interview-test-so-you-cant-cheat-on-it-with-claude/) · [[anthropic-interview-guide]]

## Harvey 🟡 — short take-home, then defense

**Type**: Short take-home to assess coding, immediately feeding a paired-coding round.
**Window**: ~1 hour for the take-home (Exponent-reported).
**Loop**: recruiter → **1-hr take-home** → paired coding with a Harvey engineer → solution-architecture presentation (panel) → director interview. 3–5 rounds, 2–4 weeks.
**Graded on**: coding, but more so the deep-dive into *how* you built it — execution, ownership, trade-offs, navigating ambiguity. For Harvey specifically, frame for **legal/regulated**: auditability, every conclusion traceable to a source, hallucination = liability.
**AI policy**: not stated.
Sources: [Exponent — Harvey](https://www.tryexponent.com/companies/harvey-ai) · [1Point3Acres](https://www.1point3acres.com/interview/company/harvey)

## Anysphere / Cursor ✅ — paid project on the real codebase

**Type**: Paid onsite **project** (4–8 hr) — *this is the actual decision round*, not a warm-up.
**Window**: 4–8 hr; substantial and a meaningful signal.
**Deliverable**: You get access to **part of Cursor's real codebase**, clone it, and build a common data structure on top (reported: a **hash tree**).
**Graded on**: functioning **senior IC** judgment — they're <100 ICs, every hire ships week one. Bar is "promising junior ≠ enough."
**AI policy** — ✅ **the most permissive**: *"Cursor technical rounds allow open usage of GPT and Cursor."* But **pasting raw model output without judgment, debugging, or rejecting bad suggestions is the fastest way to get rejected.** Using AI *well* is the literal job.
Sources: [techinterview — Cursor](https://www.techinterview.org/companies/cursor/) · [interviewcoder — Cursor](https://www.interviewcoder.co/blog/cursor-software-engineer-interview)

## Together AI ✅ — realistic systems/CUDA build

**Type**: Realistic engineering problem (senior/research roles).
**Window**: 4–8 hours.
**Deliverable**: **Inference-engine roles** → implement or optimize a **CUDA kernel**. **Platform roles** → a focused systems problem (e.g., batching scheduler, streaming generation).
**Graded on**: real ML-systems depth + performance awareness; difficulty "comparable to NVIDIA / mid-frontier-lab inference teams" (8/10).
**AI policy**: not stated.
**For you**: only relevant if you target inference-engine (needs real CUDA). Platform/systems take-home plays to your infra strength.
Sources: [techinterview — Together AI](https://www.techinterview.org/companies/together-ai/)

## Mistral 🟡 — take-home inside a long loop

**Type**: Take-home assignment, one of **7** rounds (LLM theory → coding → project deep-dive → tech-manager → ML system design → **take-home** → value talk).
**Graded on**: applied build + value-fit. Long process — pace yourself.
Sources: [Glassdoor — Mistral Applied AI Engineer](https://www.glassdoor.com/Interview/Mistral-AI-Applied-AI-Engineer-Interview-Questions-EI_IE9945031.0,10_KO11,30.htm) · [field guide](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/01-interview-process.md)

---

## AI-usage policy — cross-company rules

The single rule: **know the policy before you start, and never submit code you can't explain and extend live.** Many take-homes feed a defense round.

| Stance | Companies | Practical rule |
|---|---|---|
| **Openly encouraged** | Anysphere/Cursor; FlowFuse ("AI tools encouraged"); Zapier, Datadog, CDW, Oscar Health, AssemblyAI, SandboxAQ (published candidate-AI guidance) | Use it — but show judgment: debug, reject bad output, explain every line. |
| **Off by default, on when told** | **Anthropic** (official) | No AI on the take-home unless the instructions explicitly permit it. Use AI freely for *prep* and resume polish. |
| **Live rounds: never** | All | Live coding / onsite = you only, no AI, unless stated. |
| **Unstated** (the majority) | Cohere, OpenAI build, Harvey, Together, Mistral, most startups | Field-guide finding: **only 1 company explicitly *allowed* AI; none explicitly *banned* it for take-homes** (bans were live-round only); most say nothing. Default: use AI as an accelerant, **disclose how you used it** in the README, and be ready to defend it. |

Anthropic's framework is the gold standard to internalize ([full text](https://www.anthropic.com/candidate-ai-guidance)): ✅ refine/articulate your real work, ✅ interview prep & research; ❌ invent experiences, ❌ generate assessment answers when not permitted. Three expectations: **use AI thoughtfully, be yourself, be transparent.**

---

## What graders actually reward (every company)

From 100+ analyzed submissions + interviewer write-ups, the consistent signal:

1. **Start with evals.** Build an eval harness *before* the main logic. YC startups call *not* doing this the #1 red flag: "Red flag if candidate doesn't start with evals." This is the single biggest differentiator.
2. **Scope ruthlessly; document what you cut.** "Given the window I prioritized X; with more time I'd add Y." Scope judgment *is* the staff signal.
3. **README like a staff engineer**: problem framing → approach → key decisions & trade-offs → results → limitations → next steps.
4. **Runs from a clean clone, one command.** A broken setup sinks an otherwise-good submission.
5. **Tests** — even when not required. Edge cases, basic coverage.
6. **Production awareness** — error handling, monitoring hooks, cost estimates; connect technical metrics to business outcomes.
7. **Prepare the defense** — the follow-up walkthrough is often weighted higher than the code.

Common losses: not asking clarifying questions first; *under*-investing ("most engineers put way too little effort into take-homes"); over-engineering beyond the ask; ignoring eval/testing of AI outputs.

Sources: [field guide — home assignments](https://github.com/alexeygrigorev/ai-engineering-field-guide/blob/main/interview/questions/06-home-assignments.md) · [Fonzi AI (50+ interviews)](https://medium.com/fonzi-ai/what-ive-learned-from-sitting-in-on-50-ai-engineer-interviews-c493696453c4) · [r/ycombinator](https://www.reddit.com/r/ycombinator/comments/1jnfijm/what_is_your_interview_assignment_for_ai_engineers/) · [PromptLayer — agentic system design interview](https://blog.promptlayer.com/the-agentic-system-design-interview-how-to-evaluate-ai-engineers/)
