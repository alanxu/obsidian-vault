---
title: Design an Autonomous Coding Agent (Cursor / Devin)
slug: autonomous-coding-agent
area: 3 — Agentic Systems
companies: [Anysphere, Cognition]
difficulty: ★★★★☆
formats: [Live system design]
related: ["[[09-agent-platform]]", "[[07-code-completion-serving-sub100ms]]", "[[D0-areas-map]]"]
---

# Design an Autonomous Coding Agent (Cursor / Devin)

> An agent that takes a task ("fix this bug / add this feature"), explores a repo, edits code, **runs tests**, and opens a PR. The key insight: **tests are the verifier in the loop** — that's what makes a coding agent reliable.

## Problem
"Design the agent loop for an autonomous coding agent that runs tests, fixes bugs, and opens PRs." Sub-problems: codebase understanding (100k+ files), the plan/edit/test loop, sandboxed execution, verification.

## Clarify first
- Scope: single-file fix vs multi-file feature vs full task? Repo size/languages?
- Autonomy (suggest vs auto-merge)? Test coverage available? Latency/cost budget?

## Architecture
Task → **codebase understanding** (embeddings + symbol graph + retrieval) → **plan** → **edit** (apply diffs) → **run tests in a sandbox** → observe results → **reflect & retry** on failure → open PR. Budget + step caps throughout.

## Deep-dive — tests as the verifier + codebase context
- **Tests close the loop:** after each edit, run the test suite in a **sandboxed container**; failing tests = the feedback signal that drives the next iteration. This converts a stochastic editor into a convergent one.
- **Codebase understanding at 100k+ files:** can't fit the repo in context → index (embeddings + AST/symbol graph), retrieve only relevant files/symbols per step. RAG over code.
- **Sandboxing** — code execution is dangerous → isolated container, network egress rules, resource caps, no prod credentials.
- **Bounded retries** — cap iterations; if tests still fail, surface to human, don't loop forever.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Autonomy (auto-merge vs suggest) | speed vs safety |
| Context breadth per step | relevance vs latency/cost |
| Whole-task vs incremental | coherence vs error recovery |
| Test reliance | strong verifier vs flaky/missing tests |

## Numbers
Step reliability compounds → per-step test verification matters more than raw model IQ. Long tasks → many tokens → context compression + prefix cache essential.

## Failure modes
No/flaky tests (weak verifier) · context too narrow (wrong edit) · sandbox escape · infinite fix-loop · merging a plausible-but-wrong change · prompt injection from repo content.

## Top follow-ups
- "Make it reliable?" → tests as the loop verifier + reflection + bounded retries + human fallback.
- "100k-file repo?" → index (embeddings + symbol graph), retrieve per step.
- "Safety of running code?" → sandbox (container, no prod creds, egress rules, resource caps).
- "Sub-100ms completions too?" → that's a *separate* serving path ([[07-code-completion-serving-sub100ms]]).
- "No tests in the repo — now what?" → weaker verifiers in order: have the agent *write* characterization tests first, then type-check/lint/build as gates, then LLM code review as last resort; be explicit that autonomy should shrink as verifier strength drops.
- "How do you eval the agent itself?" → SWE-bench-style: real issues + hidden gold tests, pass@k + cost/time per resolved issue; plus trajectory metrics (edit-locality, steps-to-green) to debug *why* it fails, not just how often.
- "Long tasks blow the context — what's in it at step 40?" → not the transcript: compressed state = plan + current diff + last test output + retrieved files; summarize/evict old steps ([[fundamentals/18-agent-memory]]); the diff itself is the durable memory.
- "Concurrent agents on one repo?" → each in its own branch/worktree + sandbox; merge conflicts surface at PR like humans; never share a mutable checkout.

## Related
[[09-agent-platform]] · [[07-code-completion-serving-sub100ms]] · practical-coding [[practical-coding/16-minimal-agent-loop]] · [[D0-areas-map]] Area 3.
