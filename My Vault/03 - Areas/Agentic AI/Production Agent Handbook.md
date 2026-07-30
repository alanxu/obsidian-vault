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

# D. AWS Agentic AI Services Reference

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

# E. Further Reading

- Anthropic — *Building effective agents* (2024)
- OpenAI — *A practical guide to building agents* (2024)
- LangChain — *Agent tracing & evaluation* docs
- Papers: ReAct, Reflexion, MRKL, AutoGPT, Voyager, SWE-Agent
- Real systems: Claude Code, OpenHands, Devin, Manus
- AWS — *Amazon Bedrock AgentCore developer guide*

---

*Living doc. Update when something bites you in prod.*
