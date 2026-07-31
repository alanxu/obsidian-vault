---
title: Production Agent Handbook
tags: [agent, llm, infra, handbook]
type: reference
status: living
---

# Production Agent Handbook

A condensed reference for designing, building, and shipping LLM agents that work in production. Organized as four orthogonal pillars + a cross-cutting appendix. Optimized for builders, not beginners.

```
Reasoning        — how the model thinks
Context & Memory — what the model knows
Harness          — the runtime wrapping the model
Governance       — operating it safely at scale
```

---

## 0. Definition

An **agent** is an LLM-driven loop that, given a goal, decides its own next actions against tools/state until a stopping condition is met. Everything else (memory, planning, multi-agent) is an extension of this loop.

```
observe → reason → act → observe …
```

If your system has no tools and no loop, it's a chatbot, not an agent.

---

# 1. Reasoning

The model's "brain" — the patterns and prompts that decide *what to do next*.

## 1.1 Architecture Patterns

| Pattern                                  | When to use                                      | Trade-off                                |
| ---------------------------------------- | ------------------------------------------------ | ---------------------------------------- |
| **ReAct** (reason + act inline)          | Tool-heavy, short tasks, observable reasoning    | Verbose, expensive tokens                |
| **Plan-and-Execute**                     | Multi-step, long-horizon (>5 steps, >3 branches) | Plan goes stale; needs replan            |
| **Router**                               | Many specialized sub-agents                      | Routing errors compound                  |
| **Multi-agent** (orchestrator + workers) | Parallelizable, role-specialized work            | Coordination overhead, conflicting state |
| **Reflection / Self-critique**           | Quality-sensitive outputs (code, writing)        | 2x cost, can loop forever                |

**Rule of thumb:** start with the simplest loop. Add a planner only when steps > 5 or branches > 3. Add reflection only when eval shows quality below bar.

## 1.2 Planning

- Default to **no explicit plan** for short tasks. The model can hold it in the scratchpad.
- For long-horizon work, generate a plan once, mark steps as you complete them, **replan on deviation**, not on schedule.
- A stale plan is worse than no plan. Detect drift: goal is in scratchpad, but actions don't match → replan.

## 1.3 Skills (≠ Tools)

**Tools** are atomic functions. **Skills** are composable, named procedures ("review a PR", "debug a test failure", "triage an incident") that orchestrate multiple tools + reasoning steps for a recurring class of task.

- Skills live in a registry, indexed by description. The model picks one when it matches.
- Each skill is a prompt + a tool sequence + success criteria — versioned, eval'd, and updateable without retraining.
- Build skills from observed successful traces, not from imagination. If the agent has done it well 3 times, you have a skill candidate.

**Anti-pattern:** a skill is not a wrapper around one tool. If it is, it's just a tool.

## 1.4 Prompting

A system prompt is a contract. Be precise.

**Structure that scales:**

```
1. Role         — one line. Who you are, who you serve.
2. Capabilities — what you can do. Bullets, not prose.
3. Constraints  — what you must never do. Hard rules.
4. Workflow     — the default loop, in 3–7 steps.
5. Output       — exact format, schema, when to use tools vs answer.
6. Examples     — 1–3 diverse, edge-case included.
```

**Key techniques:**

- **CoT only when needed.** For tool use, one short "think" line beats 5 paragraphs. Verbose CoT burns tokens and slows the loop.
- **Few-shot > instructions** for format adherence.
- **Negative examples** ("do not do X") are sticky.
- **Escape hatches.** Always include "if unsure, ask the user." Agents that hallucinate when blocked are toxic.
- **Versioned prompts.** Treat them like code: review, diff, canary, rollback.

## 1.5 Reflection

Two modes:

- **Per-step:** quick self-check before tool execution. Cheap, always on.
- **Per-task:** end-of-run critique that triggers a retry. 2x cost. Only when quality gap is measured.

If you can't point to a metric that reflection improves, turn it off.

---

# 2. Context & Memory

What the model knows. Context window is the real bottleneck — architect around it.

## 2.1 Three Layers

1. **Working memory** — current scratchpad, plan, last N tool results. Always in the prompt.
2. **Episodic memory** — past sessions, conversations. Retrieved by recency + relevance.
3. **Semantic memory** — facts, preferences, user profile. Curated, not auto-extracted.

## 2.2 Working Memory (the Scratchpad)

- Use **structured markdown sections** (`## Plan`, `## Findings`, `## Open questions`, `## Decisions`). Survives compaction far better than prose.
- Treat as append-mostly. Strike through, don't delete — the model can see what was tried.
- Inject tool results in a normalized shape: `tool`, `args`, `result_summary` (not raw 10k-token dumps).

## 2.3 Retrieval (Episodic + Semantic)

- **Just-in-time.** Don't pre-load. Embed query → search → inject only what's needed.
- **Hybrid recall.** Vector similarity for fuzzy, BM25/keyword for exact (names, IDs, error codes).
- **Cite every memory.** Return the source with the recall. Models can then choose to trust or ignore.
- **Memory ≠ truth.** Vector search is recall, not correctness. Validate on use.

## 2.4 Compaction

- Triggers: token threshold, step count, sub-goal complete, or user message. Don't wait for OOM.
- Keep recent turns verbatim, summarize older ones. Preserve: decisions, open questions, failed approaches, user preferences.
- Compaction is lossy by design. The lossier it is, the better your retrieval needs to be.

## 2.5 Memory Write Policy

- **Whitelist, don't blacklist.** Persist only what the user explicitly asked to remember, or what a validated reflection pass extracted.
- **No auto-everything.** Auto-memory-everything turns the store into a junk drawer.
- **TTL on everything.** Every memory has an expiry. The user (or a periodic sweep) prunes.

## 2.6 Anti-Patterns

- Stuffing the full conversation into every call.
- Storing raw tool outputs in long-term memory.
- Treating vector search as ground truth.
- Persisting without a clear schema → unsearchable.

---

# 3. Harness

The runtime that wraps the model. Engineering substrate, not LLM magic.

## 3.1 The Core Loop

Every agent is a state machine. Make it explicit:

```python
state = {goal, history, scratchpad, tools, budget}
while not done(state):
    decision = llm.decide(state)        # may be: tool_call | final | replan
    state = apply(state, decision)
    state = enforce_invariants(state)   # budget, loops, safety
return state.result
```

**Hard rules live in the loop, not the prompt:**

- Max steps (e.g. 25)
- Max tokens / cost per run
- Max wall time
- Loop detection (same tool call 3x → break)
- Schema validation before tool execution

## 3.2 Tools

Tools are the agent's API surface. Treat them like a public API.

- **One tool, one job.** `search_users` and `search_users_v2` is a smell.
- **JSON Schema, not prose.** Descriptions: short, with examples and when-NOT-to-use.
- **Errors are data.** Return `{ok, value}` or `{ok: false, error, retryable}`. Never raise raw exceptions across the tool boundary.
- **Idempotent where possible.** Same input → same side-effect-free result, or a clear `idempotency_key`.
- **Side-effects are explicit.** Mark destructive tools; require confirmation tokens in v1.
- **Pagination is the agent's #1 failure mode.** Provide `cursor` + `has_more`; teach the agent to loop until exhausted.
- **Latency matters.** > 2s tool calls tank the loop. Stream, parallelize, or pre-fetch.

```
Tool spec template:
  name: snake_case_verb_noun
  description: "One sentence. When to use, when NOT to use."
  params: typed JSON Schema with enums and examples
  returns: typed response, never free-form
  errors: enumerated, retryable flag
  cost_hint: tokens / latency class
```

## 3.3 State & Orchestration

Long-running agents die in the gap between requests. Build for resumability.

- **Durable state.** Persist after every step. Next turn picks up exactly where the last left off.
- **Idempotent step IDs.** Same step + same input → skip. Lets you retry safely.
- **Checkpointing.** Snapshot state every N steps or T seconds. Recovery is replay, not restart.
- **Event log.** Every decision, tool call, and result is a structured event. Append-only. This is your observability and replay substrate.
- **Out-of-band signals.** User "stop" / "edit" / new input must interrupt the loop cleanly. Cancel in-flight work, don't orphan it.

## 3.4 Multi-Agent (Implementation)

The *design* of multi-agent is in §1.1. The *implementation* concerns live here.

- **Clear ownership.** Who owns what state. Who can call whom. No shared mutable state across agents.
- **Orchestrator pattern beats free chat.** A planner that hands off to workers is far easier to debug than agents talking to each other.
- **Message schema > natural language between agents.** JSON with `{task, context, expected_output}`. Free-form "conversations" between agents are a debug nightmare.
- **Cost model.** N agents ≈ N x token cost at minimum. Make sure the task is worth it.
- **Failure isolation.** Each step has explicit success/failure, not implicit. One bad agent must not poison the run.

## 3.5 Errors & Recovery

Failures are the norm. Plan for them.

- **Tool failures.** Distinguish retryable (5xx, timeout) from non-retryable (4xx, validation). Auto-retry with backoff for the first; surface the second to the model.
- **Model failures.** JSON parse errors, schema violations, refusals. Re-prompt with the error inline. After 2 failures, escalate to the user.
- **Hallucinated tool calls.** Validate the schema before execution. Reject unknown tools, never guess.
- **Loops.** Detect (a) same tool N times, (b) no progress on goal for M steps, (c) token cost > threshold. Break with a clear message.
- **Partial completion.** If you must stop mid-task, return a structured `partial_result` plus what's left. Don't return nothing.

---

# 4. Governance

Operating the agent safely at scale. Concerns that span runs, users, and time.

## 4.1 Safety & Guardrails

Defense in depth. No single layer is enough.

- **Input.** PII detection, prompt-injection scrubber, length cap, jailbreak classifier. Treat untrusted content (web results, file contents, user uploads) as data, never as instructions.
- **System prompt boundary.** Hard separator; reject any user message that tries to redefine the role.
- **Tool policy.** Allowlist by default. Destructive ops need explicit confirmation, scoped tokens, or human-in-the-loop.
- **Output.** Schema-validate, content-filter, action-confirm (e.g. "this will email 47 people — proceed?").
- **Sandbox.** Code execution runs in a fresh container with no network, no host FS. Time-bound. Resource-bound.
- **Audit.** Every action against a side-effecting tool gets logged with intent, args, and result. Retention policy.

### 4.1.1 Prompt Injection

The #1 production failure mode for agents that touch untrusted content. Direct injection is a user message trying to override instructions. **Indirect injection** — where a web page, email, or document contains adversarial text the agent later ingests — is the more dangerous and more common variant.

**Core patterns:**

- **Data vs. instructions separation.** Wrap untrusted content in explicit markers (`<untrusted>...</untrusted>`, fenced blocks, distinct role) and tell the model to never treat content inside as instructions. Belt + suspenders: also strip control-like patterns (e.g. "ignore previous", "system:", "assistant:") from untrusted sources before they enter the context.
- **Instruction hierarchy.** Make explicit which layer wins: system > developer > user > tool output. Most providers support this natively; lean on it.
- **Tool-result filtering.** The most common indirect-injection sink. After every tool call, classify the result as data, not instructions. Strip or escape anything that looks like control tokens.
- **Capability restriction on injected paths.** A tool that fetches untrusted content shouldn't be allowed to call side-effecting tools in the same turn. Compartmentalize.

**Defense in depth — none of these alone is enough:**

1. Input classifier (cheap model flags injection attempts in user input)
2. Structural markers around untrusted data
3. Output validator (does the response try to do something the user didn't ask for?)
4. Tool policy + action confirmations for side effects

**Red-team your own agent.** Build a fixture set of indirect-injection attempts: poisoned docs, malicious emails, adversarial web pages. Run them in CI. Track the bypass rate over time like a security metric.

**When to escalate to a human:** any tool call with destructive or external side effects (email, file write, code exec) where the trigger came from a tool result, not from the user's direct request. Default: confirm.

## 4.2 Observability

You cannot improve what you cannot see.

- **Trace every turn.** Input → decisions → tool calls → outputs → final. Span per LLM call, per tool, per step.
- **Log the full prompt/response in dev; redact in prod.** PII, secrets, system prompt at minimum.
- **Structured logs, not strings.** `step=3 action=search query=… latency=… tokens=…`.
- **Run metadata.** session_id, user_id, model version, prompt version, tool versions. Reproducibility starts here.
- **Replays.** A trace should be replayable against a new model/prompt to A/B cheaply.
- **Dashboards.** Step count, success rate, cost per task, retry rate, loop rate, TTFT. Alert on regression, not absolute.

## 4.3 Cost

Production agents spend money by the second. Budget everything.

| Lever                      | Effect                                                               |
| -------------------------- | -------------------------------------------------------------------- |
| **Model tiering**          | Router on small model, reasoning on big. 3–10x cost cut.             |
| **Prompt caching**         | Static system prompt + few-shots cached. 50–90% cut on long context. |
| **Tool result truncation** | Cap at N tokens; summarize beyond.                                   |
| **Parallel tool calls**    | Independent reads → fan out.                                         |
| **Batching**               | Aggregate independent LLM calls in async paths.                      |
| **Early stop**             | If `done` after 2 tool calls, don't keep thinking.                   |

**Always measure cost per task and per success.** A 2x more expensive agent that succeeds 3x as often is a win.

## 4.4 Latency

- **TTFT ≪ total latency.** Stream. The user perceives the first token, not the last.
- **Per-phase budgets.** Plan: 500ms. Tool: 2s. Synthesis: 3s. Tell the user when you'll exceed.
- **Speculative decoding / smaller draft** for long outputs.
- **Pre-warm** the model and tool connections. Cold starts are death.

## 4.5 Evaluation

Evals are the product. Without them, you're shipping vibes.

- **Golden sets.** Real tasks, real expected outcomes. Start at ~50, grow to 500+.
- **Three layers.**
  1. **Deterministic** — schema, tool calls, exact-match answers. Cheap, fast, CI-grade.
  2. **Heuristic** — regex, JSON shape, similarity scores, must-contain / must-not-contain.
  3. **LLM-as-judge** — for open-ended quality. Always blind, always paired with a rubric. Use a different model than the one being tested.
- **Per-task metrics.** Success rate, steps-to-success, cost, latency, user-thumbs. Track all.
- **Regression gates.** PR that drops success rate by N% blocks merge.
- **Offline + online.** Offline golden set gates releases. Online traces feed back into the set.
- **Anti-pattern.** Optimizing a single LLM-judge prompt without human spot-checks → agent that games the judge.

## 4.6 Reliability Ops

Operational reliability, not local logic.

- **Timeouts everywhere.** LLM calls, tool calls, total step. Pick numbers you can defend in an incident.
- **Rate limit awareness.** 429s mean back off + queue, not crash. Honor `Retry-After`.
- **Circuit breakers.** If a tool fails N times in M minutes, short-circuit and surface to the model.
- **Graceful degradation.** Tool down? Return a clear "X is currently unavailable" — don't loop.
- **Model fallbacks.** Primary → secondary model on rate limit / error. Same prompt contract.
- **Concurrency control.** Per-user locks for stateful agents. Global locks for expensive resources.

## 4.7 UX & Trust

The user is the slowest, most expensive component. Don't waste their time.

- **Show the plan before acting on side effects.** "I'll do X, Y, Z — proceed?"
- **Stream the thinking + tool calls.** A spinner for 30s is unacceptable; a live trace is trust.
- **Citations / sources on every factual claim.** Link, don't paste.
- **Reversibility.** Every action should have an "undo" or be reversible. If it can't, mark it.
- **Honest failure.** "I couldn't do this" beats a hallucinated success. Always.

---

# Agentic AI Fundamentals

Reference material that complements the core principles in §0–4. Provider-specific service maps, model API specs, and curated further reading. Not part of the principles — use it as a lookup when you need to know *what exists* or *how the wire looks*, not *what to do*.

# A. Pre-Ship Checklist

Cross-cuts all four pillars. Run before every release.

**Reasoning**
- [ ] System prompt is versioned + reviewable
- [ ] Skills registry exists where applicable, indexed by description
- [ ] Reflection only on measured quality gap

**Context & Memory**
- [ ] Working memory uses structured sections
- [ ] Retrieval is hybrid (vector + keyword) with source citation
- [ ] Compaction trigger is defined and tested
- [ ] Memory write policy is whitelisted, with TTLs

**Harness**
- [ ] Loop has hard limits (steps, tokens, wall time, loop detection)
- [ ] Tools have JSON Schema, error contracts, idempotency keys
- [ ] State is durable; turns are resumable
- [ ] Inter-agent messages are JSON, not prose
- [ ] Error path returns structured `partial_result`

**Governance**
- [ ] Safety: input scrub, tool allowlist, output validate
- [ ] Every tool call is traced; traces are replayable
- [ ] Eval suite covers happy + adversarial paths
- [ ] Cost / task measured and budgeted
- [ ] Failure modes have a user-visible message, not a stack trace
- [ ] Kill switch + human-in-the-loop for destructive ops

---

# B. Anti-Patterns (short list)

- **Prompt-only safety.** It will be bypassed. Layer it.
- **Free-form tool outputs.** Always parse/validate.
- **Auto-memory everything.** Memory becomes a junk drawer.
- **"Just add another agent."** Most coordination problems are state-management problems.
- **Optimizing the wrong metric.** Success rate, not vibes.
- **Skipping evals because "it's just a prompt change."** Prompts are code.
- **Hiding the loop from the user.** Black boxes breed distrust.
- **Skill = wrapper around one tool.** That's just a tool with extra steps.
- **Reflection without a metric.** Pure cost, no signal.

---

# C. AWS Agentic AI Services Reference

Provider-specific map. The principles in §1–4 are framework-agnostic; this appendix is for builders using AWS as the substrate. State as of late 2026 — the umbrella is **Bedrock AgentCore** (GA Oct 2025, still expanding).

## D.1 Model Serving

| Service | What it is |
|---|---|
| **Amazon Bedrock** | Managed FMs — Claude, Nova, Llama, Mistral, Cohere. Unified API, per-token pricing. |
| **Bedrock Marketplace** | 3rd-party / community models in the same API. |
| **SageMaker / SageMaker JumpStart** | Training + custom deployment, hosting of fine-tunes. |
| **Custom Model Import** | Bring your own weights to Bedrock. |

## D.2 RAG / Knowledge

| Service | Status |
|---|---|
| **Bedrock Knowledge Bases (BMKB)** | ✅ The canonical answer. Managed RAG, hybrid search, agentic retrieval, multimodal. GA June 2026. |
| **Amazon Kendra** | ⚠️ **Maintenance mode since June 30, 2026. Stops accepting new customers July 30, 2026.** Don't start new projects on it. |
| **OpenSearch Service** | Vector + lexical. Underpins customer-managed KBs. |
| **Aurora pgvector** | Postgres with vector. Good if you want a single OLTP+vector store. |
| **Neptune Analytics** | Graph-based RAG (knowledge graphs). Niche but useful for relational docs. |

## D.3 Agent Frameworks / SDK

| | Notes |
|---|---|
| **Bedrock Agents** | Managed, low-code agent builder. Native KB + action-group + Lambda tools. Easiest path, least flexible. |
| **Strands Agents SDK** | Open-source, model-agnostic, AWS-flavored but works with OpenAI, Gemini, etc. This is the one to know — it's what AWS itself uses in samples. |
| **LangGraph / CrewAI / OpenAI Agents SDK** | All run on AgentCore Runtime. AWS is framework-agnostic here. |

## D.4 Agent Hosting / Runtime

| | Notes |
|---|---|
| **AgentCore Runtime** | **The** serverless runtime purpose-built for agents. Session isolation, long-running support, multi-modal. Fast cold starts. Framework-agnostic. |
| **ECS / EKS / Fargate** | Bring-your-own container, full control, you manage it. |
| **AWS App Runner** | Simpler container hosting, less ops. |
| **Lambda** | For short-lived, stateless agent calls only. Bad for long-running sessions. |
| **EC2** | Old-school. Most cases overkill. |

## D.5 Agent Orchestration

| | Notes |
|---|---|
| **AgentCore Gateway** | Turns APIs / Lambda / existing MCP servers into MCP-compatible tools. Governed tool access. The cleanest "give my agent access to my systems" story. |
| **Bedrock Flows** | Visual workflow builder for multi-step LLM pipelines. Good for non-devs, brittle for complex logic. |
| **Step Functions** | General-purpose orchestration, can call Bedrock / Lambda. Best for long-running async workflows with retries. |
| **EventBridge** | Event-driven triggers — schedule an agent, react to events. |
| **Bedrock Agents (orchestration mode)** | Built-in multi-agent / sub-agent routing. |

## D.6 Memory

| | Notes |
|---|---|
| **AgentCore Memory** | Short-term (multi-turn) + long-term (cross-session), configurable strategies, shareable across agents. |
| **Bedrock Agents built-in memory** | Simpler, less control. Use if you don't need AgentCore's strategy knobs. |
| **DynamoDB / ElastiCache** | If you want to roll your own. |

## D.7 Identity & Auth

| | Notes |
|---|---|
| **AgentCore Identity** | Agent-aware IAM. Works with Cognito, Okta, Entra ID, Auth0. Handles user-on-behalf-of + agent-as-principal patterns. |
| **Cognito** | User pools / identity pools. Feeds into AgentCore Identity. |
| **IAM** | Standard AWS authz, the substrate. |

## D.8 Sandboxed Execution

| | Notes |
|---|---|
| **AgentCore Code Interpreter** | Isolated microVM, Python/JS/TS. The "let the agent run code" answer. |
| **AgentCore Browser** | Managed cloud browser, Playwright / BrowserUse compatible. |
| **Firecracker** (under the hood) | What Code Interpreter runs on. |

## D.9 Safety & Guardrails

| | Notes |
|---|---|
| **Bedrock Guardrails** | Content filters, PII, topic deny, word filters. Apply to any model invocation. |
| **AgentCore Policy** (preview) | Deterministic guardrails on tool calls — e.g. "this tool can only be called with X args." |
| **Macie** | PII discovery in S3. Pre-ingestion. |

## D.10 Observability & Eval

| | Notes |
|---|---|
| **AgentCore Observability** | OTEL-native traces → CloudWatch. Spans per LLM call, tool, step. |
| **AgentCore Evaluations** (preview) | Built-in agent quality eval. Sessions / traces / spans. |
| **Bedrock Evaluations** | Model-level eval (RAG, summarization, classification). Different layer than AgentCore Evaluations. |
| **CloudWatch GenAI Observability** | Dashboard surface. |
| **X-Ray** | Distributed tracing if you're going multi-service. |

## D.11 Scheduling / Async

| | Notes |
|---|---|
| **Bedrock Batch Inference** | Async batch model calls, 50% cheaper. Good for eval sweeps. |
| **EventBridge Scheduler** | Cron-style triggers for agents. |
| **Step Functions** | Long-running async workflows with state. |
| **Bedrock Agents async invoke** | Long-horizon agent tasks (multi-hour). |
| **SQS / SNS** | Message-based fan-in / fan-out around agents. |

## D.12 Built-in Agents (products, not infra)

| | Notes |
|---|---|
| **Amazon Q Developer** | Coding agent. Direct competitor to Claude Code / Copilot. |
| **Amazon Q for Business** | Enterprise Q&A agent over your docs / wikis / corp data. |
| **AWS Transform** | Code modernization agent, built on Strands + AgentCore. |
| **Amazon Connect AI agents** | Contact center agents. |

## D.13 Registry / Marketplace

| | Notes |
|---|---|
| **AgentCore Registry** | Governed publish / review / discover for MCP servers, agents, skills, custom resources. Hybrid semantic + keyword search. |

## D.14 The 3 That Matter

If picking only 3 services for a new agent platform in 2026:

1. **AgentCore Runtime** — the hosting layer is genuinely the best DX. Session isolation, long-running, framework-agnostic, MCP-native.
2. **AgentCore Gateway** — the "agent needs to call my 47 internal APIs" problem, solved cleanly with MCP + IAM.
3. **Bedrock Knowledge Bases (BMKB)** — for RAG. The agentic retrieval API is the standout.

The rest is mostly either commodity (Lambda, Step Functions, CloudWatch), sunset (Kendra), or too new to bet on (AgentCore Policy / Evaluations are still preview).

**For multi-cloud platforms:** lean on **Strands SDK** for portability and only use AgentCore services where they add real value (Runtime + Gateway are worth it). For AWS-first, the full stack is genuinely good. Just don't build your own runtime — AgentCore is hard to beat on cold starts and isolation.

---

# D. MiniMax Model API Reference

Provider-specific. The MiniMax M-series models expose two protocol-compat endpoints so existing Claude / OpenAI clients work unchanged. This is the Anthropic-compat (Messages API) spec; the OpenAI-compat (Chat Completions) spec is symmetric with the standard deviations noted below.

## E.1 Endpoints

| Protocol | Endpoint |
|---|---|
| **Anthropic Messages** (intl) | `POST https://api.minimax.io/anthropic/v1/messages` |
| **Anthropic Messages** (China) | `POST https://api.minimaxi.com/anthropic/v1/messages` |
| **OpenAI Chat Completions** (intl) | `POST https://api.minimax.io/v1/chat/completions` |
| **OpenAI Chat Completions** (China) | `POST https://api.minimaxi.com/v1/chat/completions` |

## E.2 Authentication

One key, two header styles:

```
Authorization: Bearer <API_KEY>     # preferred
x-api-key: <API_KEY>                # Anthropic-native header
```

If both are sent, `Authorization` wins.

## E.3 Models

| Model | Context | Multimodal | Notes |
|---|---|---|---|
| `MiniMax-M3` | 1,000,000 | text, image, video | Latest. Coding/agentic SOTA. Thinking controllable. |
| `MiniMax-M3[1m]` | 1,000,000 | yes | Explicit 1M-context mode (used by Claude Code config) |
| `MiniMax-M2.7` | 204,800 | text + tools | "Recursive self-improvement" framing, ~60 tps |
| `MiniMax-M2.7-highspeed` | 204,800 | text + tools | ~100 tps |
| `MiniMax-M2.5` | 204,800 | text + tools | ~60 tps |
| `MiniMax-M2.5-highspeed` | 204,800 | text + tools | ~100 tps |
| `MiniMax-M2.1` | 204,800 | text + tools | Multilingual programming focus |
| `MiniMax-M2.1-highspeed` | 204,800 | text + tools | ~100 tps |
| `MiniMax-M2` | 204,800 | text + tools | Older agentic baseline |

## E.4 Anthropic-compat Request Schema

| Field | Type | Required | Notes |
|---|---|---|---|
| `model` | enum | ✅ | See table above |
| `messages` | array | ✅ | Alternating user / assistant |
| `max_tokens` | int | | M3: rec **131072** / max **524288**. M2.x: rec **65536** / max **204800** |
| `system` | string \| block[] | | Plain text OR `[{type:text, text, cache_control?}]` |
| `temperature` | 0–2 | | default `1` |
| `top_p` | 0–1 | | default `0.95` (M3) / `0.9` (M2.x) |
| `stream` | bool | | default `false` |
| `tools` | array | | `[{name, description, input_schema, cache_control?}]` |
| `tool_choice` | object | | `type: auto \| none` only — **no forced-tool semantics** |
| `thinking` | object | | `{type: disabled \| adaptive}`. M3 only; M2.x always thinks |
| `service_tier` | enum | | `standard` (default) or `priority` (1.5× price, faster admission) |
| `metadata.user_id` | string | | Per-user rate limit / billing |

## E.5 Request Content Blocks

| `type` | Models | Notes |
|---|---|---|
| `text` | all | Plain text |
| `image` | **M3 only** | `source: {type: base64\|url, ...}`, `detail: low\|default\|high` |
| `video` | **M3 only** | `source` like image; `fps` 0.2–5 (default 1); `max_long_side_pixel` |
| `tool_use` | all | Echo prior assistant tool call: `{id, name, input}` |
| `tool_result` | all | Tool execution result: `{tool_use_id, content: string\|block[]}` |
| `thinking` | all (echo) | Must include `signature` unchanged |
| `mid_conv_system` | **M3 only** | System instructions inserted mid-conversation |

**File limits:** image ≤10MB, video ≤50MB (URL/base64), video ≤512MB (Files API via `mm_file://{file_id}`), request body ≤64MB.

**Image detail → rough tokens:** `low` ~few hundred, `default` ~1k–3k, `high` up to ~15k+. Use `count_tokens` endpoint for exact.

## E.6 Response

```
{
  id, type: "message", role: "assistant", model,
  content: [
    {type: "text",      text},
    {type: "tool_use",  id, name, input},
    {type: "thinking",  thinking, signature}   // M3 only when thinking enabled
  ],
  stop_reason: "end_turn" | "max_tokens" | "tool_use",
  usage: {input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens}
}
```

## E.7 Streaming (SSE)

`Content-Type: text/event-stream`. Each event is a JSON object on a `data:` SSE line.

**Top-level event types:** `message_start` · `ping` · `content_block_start` · `content_block_delta` · `content_block_stop` · `message_delta` · `message_stop`

**Delta types (inside `content_block_delta.delta.type`):** `text_delta` · `thinking_delta` · `signature_delta`

### E.7.1 `message_start`

First event in every stream. Full message envelope, `content: []` (blocks arrive after).

```json
{
  "type": "message_start",
  "message": {
    "id": "msg_xxx",
    "type": "message",
    "role": "assistant",
    "content": [],
    "model": "MiniMax-M3",
    "stop_reason": null,
    "stop_sequence": null,
    "usage": { "input_tokens": 0, "output_tokens": 0,
               "cache_creation_input_tokens": 0, "cache_read_input_tokens": 1366 },
    "service_tier": "standard"
  }
}
```

`usage` here is provisional — final numbers come in `message_delta`.

### E.7.2 `ping`

Heartbeat. Just `{ "type": "ping" }`. Ignore unless you're measuring keep-alive.

### E.7.3 `content_block_start`

Opens a new content block. `index` is 0-based and identifies the block for subsequent deltas.

```json
{ "type": "content_block_start", "index": 0,
  "content_block": { "type": "thinking", "thinking": "" } }
```

For `tool_use` the block is `{type:"tool_use", id, name, input:{}}` (input arrives via deltas).

### E.7.4 `content_block_delta`

Incremental update to a block. Each delta is small — one or a few tokens.

```json
{ "type": "content_block_delta", "index": 0,
  "delta": { "type": "thinking_delta", "thinking": "..." } }
```

Field on `delta` matches the type: `delta.text`, `delta.thinking`, or `delta.signature`. A thinking block typically ends with a `signature_delta` (the verifiable hash) just before its `content_block_stop`.

For `tool_use`, deltas carry `delta.partial_json` — concatenate across all deltas and `json.loads()` after `content_block_stop`. Don't try to parse the first delta as valid JSON.

### E.7.5 `content_block_stop`

Closes the block at `index`. `{ "type": "content_block_stop", "index": 0 }`.

### E.7.6 `message_delta`

Emitted once, just before `message_stop`. Carries the final `stop_reason` and total `usage`.

```json
{ "type": "message_delta",
  "delta": { "stop_reason": "end_turn" },
  "usage": { "input_tokens": 1252, "output_tokens": 213,
             "cache_creation_input_tokens": 0, "cache_read_input_tokens": 114 } }
```

### E.7.7 `message_stop`

Terminal. `{ "type": "message_stop" }`. Stream is done.

### E.7.8 Stream Anatomy (M3 with thinking)

```
message_start
  └─ message { content: [], model, usage: { input, cache_read } }
ping                                       (optional keep-alive)
content_block_start index=0
  └─ content_block { type: thinking, thinking: "" }
content_block_delta index=0   × N           (thinking_delta chunks)
content_block_delta index=0
  └─ delta { type: signature_delta, signature: "..." }
content_block_stop index=0
content_block_start index=1
  └─ content_block { type: text, text: "" }
content_block_delta index=1   × N           (text_delta chunks)
content_block_stop index=1
message_delta
  └─ delta { stop_reason: "end_turn" }, usage { final }
message_stop
```

For tool-use, swap the second block for a `tool_use` block whose `input` arrives as `partial_json` deltas (concatenate, then parse once).

### E.7.9 Errors Mid-Stream

Not a numbered event type — comes as an SSE `event: error` line:

```
event: error
data: {"type":"error","request_id":"req_xxx","error":{"type":"rate_limit_error","message":"…"}}
```

Stop reading, drop the partial content, surface the error.

## E.8 Errors

| HTTP | `error.type` | When | Retryable? |
|---|---|---|---|
| 400 | `invalid_request_error` | Bad params, unsupported content type, tool input not a JSON object | No |
| 401 | `authentication_error` | API key missing/invalid | No (fix key) |
| 403 | `permission_error` | No access to model/path | No (request access) |
| 404 | `not_found_error` | Model doesn't exist | No |
| 413 | `request_too_large` | Body >64MB or file over its limit | No (resize) |
| 429 | `rate_limit_error` | RPM/TPM/connection limit | **Yes** (backoff) |
| 500 | `api_error` | Internal | Maybe (backoff) |
| 529 | `overloaded_error` | Upstream overloaded | **Yes** (backoff) |

Error body: `{type: "error", request_id, error: {type, message}}`. During streaming, errors arrive as `event: error` SSE events with the same body — stop reading and clean up session state on receipt.

## E.9 OpenAI-compat Differences (Chat Completions)

Same models, same auth, but the request/response shape is OpenAI's. Notable differences from the Anthropic-compat path:

| Behavior | OpenAI-compat | Anthropic-compat |
|---|---|---|
| Request shape | `messages[]` with `role`/`content` | `messages[]` with `system` separate + content blocks |
| Response shape | `choices[].message.content` | `content[]` blocks (text/tool_use) |
| Tool calling | `tools[]` function spec, `tool_calls` in response | `tools[]` w/ `input_schema`, `tool_use` blocks |
| Streaming | SSE via `[DONE]` sentinel | SSE w/ event types (`message_start`, …) |
| Thinking | `<think>...</think>` inlined in `content` (default), OR `reasoning_content` / `reasoning_details` if `reasoning_split=true` | `thinking` blocks in response content |
| Multimodal | `image_url` content parts | Image / video content blocks |
| `tool_choice` | `auto` / `none` / specific function | `auto` / `none` only |

**Critical gotcha (OpenAI-compat):** when `reasoning_split=false` (default), thinking is embedded as `<think>...</think>` *inside* the `content` string. Strip or re-serialize naively → you destroy the reasoning trace. Either set `reasoning_split=true` and parse `reasoning_content` separately, or preserve `content` byte-for-byte.

## E.10 Prompt Caching

`cache_control: {type: "ephemeral"}` is supported on:
- `system[]` text blocks
- each `tools[]` entry
- request `content[]` blocks (text, image, video, tool_use, tool_result)

Cache behavior is reported in the response `usage`:
```
cache_creation_input_tokens   # tokens used to populate the cache
cache_read_input_tokens       # tokens served from cache (cheap)
```

Strategy: front-load stable content (system prompt, tool definitions, few-shots) with a single `cache_control` marker, keep variable content (user input, tool results) unmarked.

## E.11 Setup Recipes

**Claude Code (use Anthropic-compat):**
```bash
export ANTHROPIC_BASE_URL="https://api.minimax.io/anthropic"
export ANTHROPIC_AUTH_TOKEN="<MINIMAX_API_KEY>"
export ANTHROPIC_MODEL="MiniMax-M3[1m]"
```

**Cursor / Continue / Aider (use OpenAI-compat):**
```bash
export OPENAI_BASE_URL="https://api.minimax.io/v1"
export OPENAI_API_KEY="<MINIMAX_API_KEY>"
# model id: MiniMax-M3
```

**Native Anthropic SDK (Python):**
```python
from anthropic import Anthropic
client = Anthropic(
    base_url="https://api.minimax.io/anthropic",
    auth_token="<MINIMAX_API_KEY>",   # not api_key
)
msg = client.messages.create(
    model="MiniMax-M3",
    max_tokens=1024,
    messages=[{"role": "user", "content": "hello"}],
)
```

## E.12 Gotchas

1. **Reasoning trace preservation** — biggest footgun in OpenAI-compat. See §E.9.
2. **`tool_choice: tool` not supported** — can't force a specific tool by name on either protocol. Enforce in prompt + parse, not API.
3. **Region matters** — international vs China endpoints are separate accounts, no failover.
4. **Highspeed ≠ lower quality** — same model, different infra tier. Pick on latency budget.
5. **No native batch API** in either compat layer (wrap it yourself).
6. **Files API for video** — `mm_file://{file_id}` is the only way to send video >50MB. Upload first, then reference.
7. **`thinking` defaults differ by model** — M3 off by default, M2.x always on. Set explicitly to avoid surprise.
8. **`auth_token=` not `api_key=`** in the Anthropic SDK when pointing at MiniMax — common copy-paste error.

---

# E. Further Reading

- Anthropic — *Building effective agents* (2024)
- OpenAI — *A practical guide to building agents* (2024)
- LangChain — *Agent tracing & evaluation* docs
- Papers: ReAct, Reflexion, MRKL, AutoGPT, Voyager, SWE-Agent
- Real systems: Claude Code, OpenHands, Devin, Manus
- AWS — *Amazon Bedrock AgentCore developer guide*
- MiniMax — *Platform docs: Anthropic API* · *OpenAI API*

---

*Living doc. Update when something bites you in prod.*
