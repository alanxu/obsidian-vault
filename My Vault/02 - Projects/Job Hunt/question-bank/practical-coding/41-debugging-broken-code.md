---
title: Debugging / Bug Squash (fix broken code)
slug: debugging-broken-code
type: debugging
leetcode: null
companies: [Stripe, Retool, Meta, "Anysphere/Cursor", Anthropic, "any product-eng team"]
difficulty: ★★★☆☆
frequency: high
formats: [Live, Onsite·NR, OA·GCA/HR]
levels: 3
time-box: live 45–60 min
tags: [debugging, bug-squash, reproduce, stack-trace, regression-test, code-reading, concurrency]
related: ["[[13-stack-trace-to-trace-conversion]]", "[[14-exclusive-execution-time]]", "[[practical-oo-coding-deep-guide]]", "[[12-multithreaded-web-crawler]]"]
source: "Web research 2026-07 (Coditioning Stripe Bug Squash guide, Tech Interview Handbook / zhenghao 'why include debugging', Retool interview guides, Medium 'Stripe & Retool debugging'); see Sources at bottom."
---

# Debugging / Bug Squash (fix broken code)

> **A whole round in its own right — most famous as Stripe's "Bug Squash."** You're dropped into **unfamiliar code with a failing test** and asked to find and fix the bug. They grade *how you debug* — systematic, evidence-driven, collaborative — not whether you already know the codebase. This is the one round that mirrors the real job: most engineering time is reading and repairing code you didn't write, not writing greenfield.

## Problem

You are given a codebase (or a single module) and a **symptom**: a failing test, a stack trace, or a bug report ("`get_balance` returns the wrong number after a refund"). Reproduce it, find the root cause, make the **smallest** fix that resolves the observed failure, and prove it with a test — while narrating your reasoning.

The exact skin varies by company (see **By format**), but the deliverable is always: *reproduce → localize → minimal fix → validate → regression test*, out loud.

## Core method (format-agnostic) — debugging as the scientific method

Interviewers are looking for a **repeatable loop**, not a lucky guess. Say each step out loud:

1. **Reproduce first.** Run the failing case; read the *actual* error/stack trace. If you can't reproduce it, you can't prove you fixed it. (Skipping this is the #1 failure mode.)
2. **Read the code by call path.** Narrate intent: "this function is *supposed* to return X because…". Follow the trace from symptom toward source.
3. **Form ONE hypothesis.** State what you think is wrong and *why* **before** touching anything. "I think the window is inclusive when it should be half-open — if so, `getHits(300)` would count a hit at `t=0`."
4. **Prove/disprove it cheaply.** A print/log, a breakpoint, a smaller input, or bisecting the input — the cheapest evidence that confirms or kills the hypothesis. Don't edit code to "see if it helps."
5. **Make the smallest fix that matches the failure.** A one-line change beats a rewrite. The fix should follow directly from the root cause you proved.
6. **Validate.** Re-run the failing case *and* the rest of the suite (don't fix one bug and break two).
7. **Add a regression test** that would have caught this bug before the fix. This is the single strongest senior signal.
8. **Note related risk** (senior/staff): "the same off-by-one likely affects `getHitsInRange`; I'd audit that next."

> **Why this is tested:** real work is 5 activities — *searching, comprehension, exploration, incrementation, writing*. Greenfield algorithm rounds only test the last one. Debugging tests all five, which is why Stripe, Retool, and others added it. (Tech Interview Handbook / zhenghao.)

## Bug taxonomy — what you're actually hunting

The vast majority of planted/real bugs fall into a handful of classes. Recognizing the *class* from the symptom is most of the speed. (Runnable examples: the companion repo folder — see below.)

| Class | Typical symptom | Tell |
|---|---|---|
| **Off-by-one / boundary** | last (or first) element wrong; edge input fails | `<=` vs `<`, `range(n)` vs `range(n+1)`, inclusive vs half-open window |
| **None / null deref** | `AttributeError`/NPE on some inputs only | missing "not found" branch; optional not checked |
| **Mutable default arg** (Py) | state "leaks" across calls | `def f(x, acc=[])` / `={}` shared across invocations |
| **Aliasing / shared reference** | writing one row/cell changes all | `[[0]*n]*m`; shallow copy of nested structure |
| **Late-binding closure** (Py) | all callbacks use the last loop value | `[lambda: i for i in range(n)]` |
| **Integer/float** | truncated averages, rounding drift, `/` vs `//` | money in floats; `//` where `/` meant |
| **Mutation during iteration** | `RuntimeError: dict changed size` | editing a dict/list while looping it |
| **`is` vs `==`** | equality works sometimes (small ints/None) | identity used for value comparison |
| **Race condition** | flaky under threads; lost updates | non-atomic read-modify-write on shared state |
| **Swallowed exception** | silent wrong result, no error | bare `except:` / `except: pass` hiding the real failure |
| **Cache invalidation** | stale result after inputs change | memo key omits an argument; TTL not honored |
| **Wrong operator / inverted condition** | logic "mostly" works | `and`/`or`, `>=`/`>`, negation flipped |

## By format

### Live · Bug Squash (Stripe — the canonical version)
- **How it appears:** onsite, 45–60 min, **side-by-side** with an engineer. A **real historical bug** in an **open-source project in your language**; you get a repo with a failing test. Written rubrics guide the grade.
- **Follow-ups (in order):** reproduce the failing test → read the stack trace → localize by call path → targeted fix → **add a regression test** → "what related failures would you audit?" (senior) → "what would prevent this class of bug?" (types, invariants, CI).
- **Tips:** run the test in the first 2 minutes; narrate intent while reading; change one thing at a time; keep the diff tiny; end by writing the regression test even if not asked.
- **Pitfalls:** random edits with no hypothesis; **skipping reproduction**; rewriting the function instead of debugging it; fixing the symptom (`if x is None: return 0`) instead of the cause.

### Live · First-round multi-bug (Retool style)
- **How it appears:** a **custom codebase with *several* planted bugs** (often front-end/app or a small service), used as a **first-round** screen. Trace data flow with logs/console.
- **Follow-ups:** triage which bug to fix first (usually the one blocking the others); fix independently; don't let one fix mask another.
- **Tips:** binary-search the data flow (log at the midpoint of the pipeline to halve the search space); fix the highest-leverage bug first; re-run after each fix.
- **Pitfalls:** shotgunning fixes; conflating two independent bugs; not re-verifying earlier fixes after a later change.

### OA · "make the failing tests pass"
- **How it appears:** auto-graded; a repo with red tests, sometimes a time limit. No interviewer to narrate to.
- **Tips:** let the tests *be* the spec — read them first; fix the cause, not the assertion; run the whole suite, watch for regressions.
- **Pitfalls:** editing the test to match the bug; over-fitting to one case and breaking a hidden one.

### Onsite · NR (trace by hand)
- **How it appears:** non-runnable editor; you "run" the code in your head and explain the bug.
- **Tips:** dry-run a concrete small input on the whiteboard, tracking state in a table (this is exactly [[14-exclusive-execution-time]] / [[13-stack-trace-to-trace-conversion]] energy); point at the exact line and state the corrected behavior.
- **Pitfalls:** hand-waving "somewhere around here"; not committing to a specific line + fix.

## Company variants
- **Stripe** — the flagship Bug Squash: one real bug in a real OSS repo, side-by-side, regression test expected. Prep by fixing small issues in an unfamiliar repo in your strongest language.
- **Retool** — debugging as a **first-round**, **multiple** bugs in a custom app codebase; data-flow tracing with logs.
- **Meta / general product teams** — a debugging component often folded into a coding round: "here's code that's wrong on some inputs, fix it."
- **Anysphere/Cursor, Anthropic & agent shops** — increasingly: **debug AI-generated / streaming code**, or fix a bug in a small agent/parser (pairs with [[37-streaming-json-parser]], [[13-stack-trace-to-trace-conversion]]). Modern angle: reading a stack trace and instrumenting with logs is the same skill their products automate.

## Strong signals (the rubric)
- Reproduces before editing; reads the real error.
- Hypothesis → evidence → fix (not edit → hope).
- Smallest reasonable diff; fixes the **cause**, not the symptom.
- Re-runs the whole suite; adds a regression test.
- Calm, collaborative narration in unfamiliar code; asks clarifying questions.
- (Senior) names the bug *class*, audits related code, suggests a systemic guard.

## Common failure modes (pitfalls)
- **Random edits** with no hypothesis — the biggest red flag.
- **Skipping reproduction** — you can't prove a fix you never saw fail.
- **Rewriting instead of debugging** — the round is code navigation + targeted repair.
- **Symptom-patching** — `try/except` around the crash instead of the wrong computation underneath.
- **Silent scope creep** — "cleaning up" unrelated code and introducing new bugs.
- **No regression test** — leaves the interviewer unsure the bug is truly dead.

## Worked example trace (narration)
> *Symptom:* `HitCounter.getHits(300)` returns 4 but should be 3.
> "First, reproduce — yes, red. The window should be `(t-300, t]`, half-open. Hypothesis: eviction uses `<` where it should use `<=`, so a hit at `t=0` survives at `t=300`. Evidence: I'll print the deque before the count → `[0,1,2,300]`, and `0` shouldn't be there. Confirmed. Smallest fix: `while q and q[0] <= t-300: q.popleft()`. Re-run: green, and the other cases still pass. Regression test: `getHits(300)==3` after hits at 0,1,2,300. Related risk: any other place computing this window — none here."

## Runnable companion
Practice repo (outside the vault): **`/Users/alanxu/projects/interview-questions/practical-coding/41-debugging-broken-code/`** — ~10 classic planted bugs (one per taxonomy row) as small functions, each documented with the reported symptom, the buggy line, the root cause, and the fix, plus regression tests that pin them. Run `python3 test_debugging_drills.py`. To drill *actively*, reintroduce the buggy line shown in each docstring and fix it back to green.

## Related
- [[13-stack-trace-to-trace-conversion]] — reading stacks/traces is the core sub-skill.
- [[14-exclusive-execution-time]] — hand-tracing state to find the off-by-one.
- [[12-multithreaded-web-crawler]] — where concurrency bugs (races) actually bite.
- [[practical-oo-coding-deep-guide]] — round mechanics + how to narrate.

## Sources
- Coditioning — *Stripe SWE Interview: Bug Squash Guide* (mechanics, rubric, failure modes): https://www.coditioning.com/blog/804/stripe-swe-bug-squash-interview
- Tech Interview Handbook — *Why you should include debugging in the interview process* (the 5 programming activities): https://www.techinterviewhandbook.org/blog/why-you-should-include-debugging-in-the-interview-process/ and https://www.zhenghao.io/posts/debugging-interview
- Medium (Tech Pulse) — *Navigating the Debugging Interview: Insights from Stripe and Retool*: https://medium.com/tech-pulse/navigating-the-debugging-interview-insights-from-stripe-and-retool-697cead7c4db
- Retool SWE interview guide (debugging first-round, multi-bug): https://www.interviewquery.com/interview-guides/tryretool-software-engineer
- GeeksforGeeks — *Debugging in Interview Process*: https://www.geeksforgeeks.org/blogs/debugging-in-interview-process/
