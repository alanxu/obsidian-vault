---
title: Framework Selection
pillar: harness
parent: ./README.md
section: "3.6"
---

# 3.6 Framework Selection

The first decision in the harness pillar: which agent framework (or none). Two
candidates dominate the 2026 production landscape — **LangGraph** and the
**Claude Agent SDK**. They look like competitors, but they target different
abstraction layers. Picking wrong costs weeks.

> Scope: this evaluates *orchestration* frameworks. Pure LLM-call wrappers
> (LiteLLM, raw OpenAI/Anthropic SDKs) are not in scope — they are tools, not
> harnesses. See [[tools|3.2 Tools]].

## Evaluation Axes

Ten dimensions matter for a production agent harness. We score both frameworks
on each.

| # | Axis                | Why it matters                                                          |
|---|---------------------|-------------------------------------------------------------------------|
| 1 | Control model       | Graph (explicit) vs. loop (implicit) — drives debuggability             |
| 2 | State persistence   | Does the framework own durability, or do you?                           |
| 3 | Multi-agent         | Subgraph vs. subagent; context isolation; attribution                   |
| 4 | Tool layer          | Custom JSON-Schema tools vs. built-in OS/file/web tools                 |
| 5 | Model binding       | Agnostic vs. single-vendor — affects cost, latency, lock-in             |
| 6 | Human-in-the-loop   | Interrupt/resume semantics; where approval gates live                   |
| 7 | Debugging           | Replay, time-travel, trace quality, cost attribution                   |
| 8 | Observability       | First-class traces/metrics vs. DIY                                     |
| 9 | Deployment shape    | Library you embed vs. harness you host; state store requirements        |
| 10| Best fit            | The honest use case — every framework has one                           |

---

## LangGraph

LangChain's response to "agents are state machines, stop pretending they're
chains." A graph is a set of **nodes** (functions) connected by **edges**
(static or conditional). State is a typed schema, checkpointed after every
node transition.

### Architecture

```
            ┌─────────────┐
   input →  │  start      │
            └──────┬──────┘
                   │ (entry edge)
                   ▼
            ┌─────────────┐
            │  plan       │ ◀──────────┐
            └──────┬──────┘            │ (loop edge)
                   │                   │
                   ▼                   │
            ┌─────────────┐            │
            │  tools      │ ───────────┘
            └──────┬──────┘
                   │ conditional edge
                   ▼
            ┌─────────────┐
            │  validate   │  (interrupt_before — human approval)
            └──────┬──────┘
                   │
                   ▼
            ┌─────────────┐
            │  end        │ → output
            └─────────────┘
```

State is a `TypedDict` (or Pydantic). Each node receives the current state and
returns a partial update; LangGraph merges and routes. With a checkpointer
attached, every transition is a snapshot.

### Key Features

- **State machine primitives.** `StateGraph`, nodes, edges, conditional edges,
  `add_conditional_edges`, `Send` for map-reduce fan-out. The control flow is
  the code, not a hidden loop.
- **Built-in persistence via checkpointers.**
  - `MemorySaver` — dev only, dies on restart.
  - `SqliteSaver` — single-machine, fine for prototype. Bottlenecks under
    concurrency; skip for production.
  - `PostgresSaver` — production target. Real durability, real concurrency.
  - `thread_id` is the session contract. Pass it in every `invoke` config.
  - `Store` API (separate from checkpointer) for cross-thread long-term memory.
- **Human-in-the-loop.** `interrupt_before=["node_name"]` pauses the graph;
  call `app.invoke(None, config)` with the same `thread_id` to resume. Works
  across process restarts because state is persisted.
- **Time-travel debugging.** Any checkpoint is resumable. Replay the graph
  from step N, fork it, or inspect what state looked like at any point. This
  alone justifies the framework for long-running workflows.
- **Subgraphs.** Nest a graph inside a node. The parent and child share state
  only via the explicit interface you define. No implicit coupling.
- **Streaming.** `app.stream(..., stream_mode="values"|"updates"|"events")` —
  expose intermediate state to UI without exposing internals.
- **Model-agnostic.** Works with any chat model that implements the LangChain
  `BaseChatModel` interface: OpenAI, Anthropic, Bedrock, Vertex, local vLLM.
  Swap by changing the bind, not the code.
- **LangSmith observability.** First-class tracing. Free tier: 5,000
  traces/month, 14-day retention. Plus: $39/seat/month, 10,000 traces.
  Tracing includes per-node latency, token cost, retry counts, and the exact
  prompt sent to the model.

### Pros

- **The persistence story is the best in class.** Checkpointers + thread_id +
  time-travel is what production agents actually need. Most "agent
  frameworks" punt this to the user.
- **Explicit control flow.** When the agent makes a wrong turn, you can see
  it in the graph, replay it, and fix the routing. The "agent is a magic
  loop" abstraction hides bugs; the graph exposes them.
- **Provider freedom.** Not locked to one vendor. Cost-optimize across
  models per node. Critical when one task is GPT-5-cheap and another is
  Claude-Opus-required.
- **Mature ecosystem.** LangSmith, LangGraph Studio (visual debugger), a year
  of production hardening. Documented failure modes. Long memory of bugs.
- **Subgraphs map cleanly to teams.** One team owns a subgraph; they expose a
  state schema; the parent graph composes them. Natural team boundary.

### Cons

- **Conceptual overhead.** State, reducers, channels, conditional edges,
  checkpointers, subgraphs, the binding layer — there is a real learning
  curve. The first agent takes longer than it should.
- **LangChain coupling.** The `BaseChatModel` and `Tool` abstractions are
  LangChain. If you already have clean abstractions of your own, you
  rebuild them or fight the framework.
- **Verbose for simple cases.** A 5-line "call LLM, parse, return" is a
  30-line graph with a `MessagesState`, a node, a single edge, and a
  compiled app. Bring LangGraph when you actually need the control flow.
- **The "LangChain tax."** Public perception still associates LangGraph with
  LangChain's earlier abstractions. Some teams will not adopt for cultural
  reasons regardless of the technical merit.
- **No built-in tools.** You wire up your own tool definitions and execution
  layer. Fine if you have a tool registry; painful if you don't.

---

## Claude Agent SDK

The same agent loop that powers Claude Code, exposed as a library. Philosophy:
**give the model a computer** — bash, files, the network, MCP — and let it
figure out the steps. The SDK ships with the toolset, permission system, and
context management that Anthropic built for Claude Code, abstracted from the
CLI and made programmatic.

### Architecture

```
  your_app.query(prompt, options)
        │
        ▼
  ┌──────────────────────────────────────┐
  │  Agent loop (driven by Claude Code)  │
  │                                      │
  │   1. read settings (CLAUDE.md,       │
  │      .claude/skills, hooks)          │
  │   2. think                           │
  │   3. pick tool                       │
  │   4. execute (built-in / MCP / sub)  │
  │   5. observe result                  │
  │   6. back to 2 until stop            │
  └──────────────────────────────────────┘
        │
        ├─→ built-in tools (Read/Write/Edit/Bash/Glob/Grep/WebFetch/...)
        ├─→ MCP servers (deep integration, native)
        └─→ subagents (own context, own tool list, parent_tool_use_id)
```

There is no graph. There is a loop, a toolset, and a context window. The
control flow lives in the model's head.

### Key Features

- **Built-in tool set, no boilerplate.** `Read`, `Write`, `Edit`, `Bash`,
  `Glob`, `Grep`, `WebSearch`, `WebFetch`, `Monitor`, `AskUserQuestion` —
  shipped, scoped via `allowed_tools`. No JSON Schema to author for the
  common cases.
- **MCP at the deepest tier.** MCP is not a third-party plugin; it is the
  SDK's extension model. Tools from MCP servers are first-class alongside
  built-ins, with the same permission and scoping semantics.
- **Subagents with isolated context windows.** Each subagent gets its own
  context, its own (usually narrower) `allowed_tools`, and reports a
  summary back. The orchestrating agent never sees the subagent's full
  history — that is the isolation boundary. Messages carry
  `parent_tool_use_id` for cost attribution.
- **Skills.** Reusable instructions packaged as `SKILL.md` files in
  `.claude/skills/<name>/`. The agent loads them automatically or invokes
  them by `/name`. Treat skills as versioned, filesystem-checked-in
  capabilities.
- **Filesystem-based memory.** `CLAUDE.md` (project) and `~/.claude/CLAUDE.md`
  (user) — durable context that survives sessions. The agent writes files to
  remember things; you read them to understand what it remembered.
- **Hooks.** Lifecycle callbacks (`PreToolUse`, `PostToolUse`,
  `Stop`, `SubagentStop`, etc.) for policy, logging, blocking destructive
  actions, or modifying context. Clean place to put your guardrails — not
  in the prompt.
- **Session resume.** Capture `session_id` from the init message; pass
  `options.resume` to continue. The session boundary includes the full
  context, not just your prompt.
- **Provider routing.** Anthropic API, Amazon Bedrock, Google Vertex AI.
  Same SDK; you point it at a different base. Model class is still Claude
  (Opus, Sonnet, Haiku) — the model layer is not abstracted away.
- **Dynamic workflows (2026-06).** Lead agent plans and fans out tens to
  hundreds of parallel subagents in a single session. Performance Outcomes:
  a separate grader sends each subagent back to revise against a rubric
  until it passes.

### Pros

- **Zero tool-layer boilerplate.** When your agent needs to read a file,
  run grep, fetch a URL, or shell out, the tool exists. You do not author
  JSON Schema for the 80% case. Shipping speed is real.
- **The MCP integration is the deepest in any framework.** MCP is not an
  afterthought bolted on; it is the extension model. If you have many
  tools and want one consistent permission/scoping story, this is the
  path of least resistance.
- **Battle-tested in Claude Code.** The loop, permission system, error
  recovery, and subagent model all run millions of times a day in
  production at Anthropic. The bug surface is small and well-known.
- **Filesystem-based skills/memory are versionable.** A skill is a
  markdown file. It goes in git. It has a diff. It has a review. Compare
  with "edit the agent's system prompt in the deploy config."
- **The subagent model is honest about context isolation.** Each
  subagent has its own window; the parent only sees the summary. The
  framework prevents the "context soup" failure mode where every
  sub-step's noise ends up in the main prompt.
- **Hooks are a clean place for guardrails.** Pre-tool-use hook checks
  destructive actions. Post-tool-use hook logs/redacts. Stops the
  guardrail logic from polluting the system prompt.

### Cons

- **Claude-only at the model layer.** You can route to Bedrock or Vertex,
  but the model is always Claude. If your cost model requires per-node
  model selection across vendors, this is a hard wall. The 2026 Anthropic
  pricing on Opus is also a real line item.
- **Implicit control flow.** When the agent makes a wrong turn, the loop
  is opaque. There is no graph to inspect, no node to step into. Debugging
  means reading the message log and guessing. For deterministic,
  audit-required workflows, this hurts.
- **State persistence is your problem.** The SDK does not own durability.
  You wire up a session store, decide what to checkpoint, and own the
  resume contract. Compared to LangGraph's `PostgresSaver`, this is
  meaningful work.
- **Vendor lock-in beyond the model.** `CLAUDE.md`, `.claude/skills/`,
  the agent loop's exact semantics, the subagent conventions — moving to
  another framework is a rewrite, not a config change.
- **The "give it a computer" model is not appropriate for every domain.**
  If your agent is a customer-service triage bot, granting bash + filesystem
  is wildly over-scoped. The SDK's defaults assume a coding/OS automation
  environment. Other domains need aggressive `allowed_tools` restriction
  and hooks to be safe.
- **No equivalent of LangSmith for first-class observability.** Tracing
  exists, but you build dashboards. Cost attribution per subagent is
  there (`parent_tool_use_id`); aggregate views are not.
- **Tighter coupling between model quality and outcomes.** Because the
  loop trusts the model to plan, agent quality tracks Claude's
  capability delta. On a task where Claude is not the best model, the
  whole agent is suboptimal with no easy way out.

---

## Side-by-Side Matrix

| Axis              | LangGraph                                           | Claude Agent SDK                                          |
| ----------------- | --------------------------------------------------- | --------------------------------------------------------- |
| Control model     | Explicit graph (nodes, edges, conditionals)         | Implicit loop, model-driven decisions                     |
| State persistence | Built-in checkpointers (Postgres in prod)           | Developer-owned; sessions via `resume`                    |
| Multi-agent       | Subgraphs (shared/explicit state)                   | Subagents (isolated context windows)                      |
| Tool layer        | Your JSON-Schema tools + LangChain tools            | Built-in OS/file/web tools + MCP                          |
| Model binding     | Any `BaseChatModel`                                 | Claude only (Anthropic / Bedrock / Vertex)                |
| Human-in-the-loop | `interrupt_before`/`interrupt_after` + checkpointer | Hooks + tool-permission system                            |
| Debugging         | Time-travel from any checkpoint + Studio            | Message-log replay; no step-by-step                       |
| Observability     | LangSmith (first-class, $$ tiered)                  | Built-in traces; you build the dashboard                  |
| Deployment shape  | Library + state store (PG/Redis)                    | Library + filesystem (`CLAUDE.md`, skills)                |
| Best fit          | Long-running, stateful, multi-team                  | Coding/OS-automation, MCP-rich domains                    |
| Worst fit         | Throwaway scripts; "just call an LLM"               | Vendor-neutral needs; cost-optimized heterogeneous models |

---

## When To Use Which

**Use LangGraph when:**
- The agent runs longer than one turn and must survive a restart.
- You need explicit, auditable control flow (regulated domain, finance, ops).
- Multiple teams or services compose into one agent (subgraphs as team boundary).
- You must mix models per node for cost or capability reasons.
- You will spend real time debugging production runs and need time-travel.

**Use Claude Agent SDK when:**
- The agent is a coding assistant, dev-tooling, or any "give it a computer" task.
- MCP is the central tool story and you have many MCP servers.
- The Claude model tier is the right fit (or required) for your domain.
- Speed-to-first-agent matters more than long-term control.
- You want to inherit Claude Code's permission system, subagent model, and
  hook surface instead of reinventing them.

**Use neither when:**
- The "agent" is a one-shot LLM call with a structured output. Use the raw
  provider SDK + a JSON Schema validator. The framework tax exceeds the value.
- You are prototyping a new architecture. The first version should be 200
  lines of Python and a hardcoded loop. Pick a framework when the second
  version needs persistence, observability, or a team boundary.

**Use both (hybrid) when:**
- The orchestrator is a LangGraph (state, multi-team, persistence) and one
  of its nodes delegates a bounded subtask to a Claude Agent SDK sub-process
  (coding task, OS operation). Wrap the SDK call in a node; treat its output
  as a structured return value; checkpoint the return, not the SDK session.
  This is the pattern when the orchestration problem and the coding problem
  are genuinely different shapes.

---

## Anti-Patterns

- **Picking LangGraph for a 5-step dev script.** The boilerplate is the
  product; the loop is over-engineering. Use the raw provider SDK.
- **Picking the Claude Agent SDK for a multi-tenant regulated workload.**
  Implicit control flow, no built-in durable state, model-only — you will
  rebuild half the framework badly.
- **Wrapping one in the other without a clear interface.** If the
  LangGraph node calls the SDK and the SDK spawns subagents that emit
  back into the graph, you have a state-mirroring problem. Define the
  contract (input schema, output schema, error contract) and keep the
  boundary clean.
- **Picking a framework because the team lead used it before.** Re-evaluate
  the ten axes against the current task. The framework landscape moves
  fast; "we always use X" ages in months.

---

## Cross-References

- [[core-loop|3.1 The Core Loop]] — every framework implements some version
  of this state machine; the framework should make it more explicit, not
  less.
- [[state-orchestration|3.3 State & Orchestration]] — the persistence
  requirements that differentiate LangGraph's checkpointer story from the
  SDK's "you own it" model.
- [[multi-agent|3.4 Multi-Agent (Implementation)]] — subgraph vs. subagent
  maps directly to the implementation choices here.
- [[tools|3.2 Tools]] — the JSON Schema tool contract that LangGraph
  assumes and the Claude Agent SDK ships as built-ins.
- [[../governance/evaluation|4.5 Evaluation]] — every framework choice
  needs an eval harness; the framework does not include one.
- [[errors-recovery|3.5 Errors & Recovery]] — the retry/replay semantics
  differ materially between the two.
