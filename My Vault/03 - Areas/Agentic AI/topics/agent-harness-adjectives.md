---
title: Agent Harness — Quality Vocabulary
slug: agent-harness-adjectives
area: Agent Concepts
difficulty: ★★★☆☆
related:
  - "[[skills-tools-mcp-cli|Skills, Tools, MCPs, CLIs]]"
  - "[[../../02 - Projects/openmate/design/agentic-web-ui|Agentic Web UI Design]]"
added: 2026-08-06 (vocabulary card for evaluating / describing agent harnesses — the 6 categories, the 10 that capture the essence, the 5 that mean run)
evidence: "GUIDE-LEVEL: vocabulary synthesised from production harness patterns (Mavis / Claude / OpenClaw / Cursor / Devin / Strands / LangGraph); the 6 categories are my framing. MIXED: specific adjective choices (resilient, traceable, bounded, ...) are widely used in 2026 agent-engineering discussions but the canonical vocabulary is not formally standardised."
---

# Agent Harness — Quality Vocabulary

> **The one-line mental model:** A *good* agent harness is **bounded, traceable, reversible, sandboxed, confirmable, durable, streamy, cost-transparent, pluggable, eval-gated**. A *bad* one is **leaky, opaque, brittle, runaway, trustless**. This card is the vocabulary for telling the two apart.

An agent harness is the runtime scaffolding around an LLM — model interface, context management, tool dispatch, session state, the agent loop, skills, safety, observability, streaming, identity, cost controls, concurrency. The adjectives below describe qualities at each of those layers.

---

## 1. Reliability — does it work under load, fail gracefully, recover?

| Adjective | What it means |
|---|---|
| **Resilient** | Recovers from transient failures (model 429s, tool timeouts) without user-visible errors |
| **Idempotent** | Same call → same result; retries are safe |
| **Fault-isolated** | One session's failure can't take down the platform |
| **Self-healing** | Recovers automatically (reconnect WebSocket, retry MCP server, refresh stale token) |
| **Bounded** | Every loop has a hard cap; no infinite runs, no runaway costs |
| **Deterministic** | Same inputs + same model + same tools → same outputs (where possible) |
| **Reproducible** | A trace can be replayed bit-for-bit |
| **Backpressured** | Slow consumers don't stall the agent |

## 2. Safety — can it hurt the user or the system?

| Adjective | What it means |
|---|---|
| **Sandboxed** | The agent runs in an isolated environment (microVM, container) |
| **Bounded** | Autonomy is tiered (read / workspace / full / custom) and user-controlled |
| **Confirmable** | Destructive actions always require explicit human approval |
| **Auditable** | Every action has a user, session, timestamp, args, result — queryable |
| **Tamper-evident** | The audit log is append-only with a hash chain or external sink |
| **Least-privilege** | Each tool gets the minimum scope; on-behalf-of the end user, not a god-token |
| **Scrubbed** | Tool outputs are filtered for PII and prompt-injection before reaching the model |
| **Trifecta-broken** | Policy engine prevents "private data + untrusted content + exfil" in one context |

## 3. Observability — can you see what it did and why?

| Adjective | What it means |
|---|---|
| **Traceable** | OTEL spans per tool call, per step, per session — queryable by ID |
| **Replayable** | From the trace log, replay any session with the exact same state |
| **Inspectable** | The user can see what's in the context, what the plan is, what the model is "thinking" |
| **Attributable** | Cost and latency are attributed per skill, per tool, per model |
| **Alertable** | Regressions (cost spike, error spike, eval drop) page someone |
| **Transparent** | The user can see *why* the agent did what it did (the reasoning, the tool calls) |
| **Diagnosable** | When something goes wrong, the trace tells you where |

## 4. Composability — can you extend it without rewriting?

| Adjective | What it means |
|---|---|
| **Modular** | Each layer (model, context, tools, skills, safety) is independent |
| **Pluggable** | New tools, skills, MCP servers drop in without code changes |
| **Versioned** | Every skill, tool, and config has a version; breaking changes are explicit |
| **Portable** | Skills work across harnesses (Mavis ↔ Claude ↔ OpenClaw) |
| **Standardized** | Uses the same protocol everyone else uses (MCP, JSON Schema, OTEL) |
| **Interoperable** | Talks to other agents (A2A / ACP) and other tools (MCP) |
| **Eval-gated** | Every change is tested against the eval set before promotion |
| **Cacheable** | Prompt prefix, tool results, and skill bodies are cacheable |

## 5. State — does it remember, resume, and rewind?

| Adjective | What it means |
|---|---|
| **Durable** | Sessions survive server restart |
| **Resumable** | After a disconnect, the user reopens and sees the same conversation from the right point |
| **Branchable** | Conversations are trees; the user can fork from any point |
| **Replayable** | The agent's full trajectory is reproducible from the log |
| **Stateless-friendly** | Components that can be stateless (tool dispatch, model calls) are stateless |
| **Stateful-where-needed** | Components that must be stateful (session, memory) are explicitly so |
| **Idempotent** | State transitions are safe to retry |
| **Continuous** | No "session lost" errors; the user never loses work |

## 6. UX — does it feel right to use?

| Adjective | What it means |
|---|---|
| **Streamy** | Everything streams — tokens, tool calls, results, costs |
| **Visible** | The agent's work is on-screen; the user never wonders "what's it doing" |
| **Reversible** | Every action can be undone (rewind, revert, retry) |
| **Interruptible** | The user can pause / redirect / skip at any point |
| **Latency-tolerant** | Long operations have good progress indication (skeleton, optimistic UI) |
| **Cost-transparent** | The user sees what they're spending, in real time |
| **Legible** | The output is structured and readable; the model doesn't dump prose |
| **Trustworthy** | The user feels safe letting it act — because the safety surface is visible |
| **Recoverable** | Errors are clear, actionable, and the next step is obvious |
| **Progressive** | Advanced features are opt-in; default state is the simplest useful state |

---

## The 10 that capture the essence

If you only remember ten:

1. **Bounded** — every loop has a cap (steps, cost, time)
2. **Traceable** — every action is in the trace
3. **Reversible** — every action can be undone
4. **Sandboxed** — the blast radius is the microVM
5. **Confirmable** — destructive actions need explicit approval
6. **Durable** — sessions survive restart
7. **Streamy** — everything streams to the UI
8. **Cost-transparent** — the user sees the bill
9. **Pluggable** — new tools drop in, no code changes
10. **Eval-gated** — every change passes the eval before it ships

## The 5 that mean "run"

If a review says any of these, walk away:

1. **Leaky** — secrets, PII, or internal errors bleed into the model context
2. **Opaque** — you can't see what the agent did or why
3. **Brittle** — one bad tool call crashes the session
4. **Runaway** — the agent loops forever, burns cost, no cap
5. **Trustless** — destructive actions happen silently, no approval

---

## How to use this card

- **In a design review:** score a harness 1-5 on each adjective. Anything below 3 in Safety is a no-ship.
- **In a product spec:** "the harness must be bounded, traceable, reversible, and confirmable" — these four are non-negotiable for any user-facing agent.
- **In an interview:** when asked "what makes a good agent harness," reach for the 10-essence list. When asked for depth, pick one category and walk through the adjectives with concrete examples.
- **In a competitor analysis:** score 2-3 competitor harnesses on the same adjectives. The differences surface immediately.
