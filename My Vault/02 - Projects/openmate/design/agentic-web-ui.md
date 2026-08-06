---
title: Agentic Web UI — Design Report
slug: agentic-web-ui
project: openmate
audience: VP of Tech
status: draft
version: 0.2
date: 2026-08-06
author: Mavis (mavis)
related:
  - "[[../../../03 - Areas/Agentic AI/topics/skills-tools-mcp-cli|Skills, Tools, MCPs, CLIs]]"
  - "[[../../../03 - Areas/Agentic AI/topics/aws-agent-infra|AWS Agent Infrastructure]]"
---

# Agentic Web UI — Design Report for openmate

> **TL;DR for the VP:** the agentic UI is no longer a chat box. It's a **3-pane workspace** (chat + work artifacts + control surface), with streaming everything, visible tool execution, bounded autonomy, and one-click course-correction. Build the chat-first MVP, instrument everything, and let usage data drive the V1 layout evolution. The competitive moat is the **trust surface** — the controls that make the agent safe enough to actually let it touch the user's code.

---

## 1. Executive summary

The agentic web UI in 2026 is a different category of product from a chatbot. The user is not "talking to a model" — they're **delegating work to an autonomous actor** that takes real, often irreversible, actions on their behalf. The UI's job is to make that delegation legible, controllable, and reversible.

**The single most important design principle:** the UI's value is not how smart the agent looks, it's how *trustworthy* the agent feels. Every UI decision is a trust decision.

**Recommended v1 architecture (the "3-pane workspace"):**

```
┌───────────────────────────────────────────────────────────────┐
│  Top bar: agent selector · run state · cost · user · settings│
├──────────────┬──────────────────────────────┬────────────────┤
│              │                              │                │
│  Chat /      │  Work surface                │  Inspector /   │
│  command     │  (code diff, file tree,      │  control       │
│  pane        │  browser preview, terminal)  │                │
│  (left)      │  (center)                    │  (right)       │
│              │                              │                │
└──────────────┴──────────────────────────────┴────────────────┘
```

- **Left pane** — chat, command, history. Where the user talks to the agent and sees its reasoning.
- **Center pane** — the work. Shows what the agent is doing: code diffs, file tree changes, browser state, terminal output, app preview.
- **Right pane** — inspector. The control surface: tool calls, plan view, cost so far, memory, settings, what the agent can / can't do, approval queue.

**Why 3 panes (not 2, not chat-only):** chat-only (Claude.ai style) hides the work; IDE-only (Cursor style) makes the chat a slave to the editor. The 3-pane layout puts the user in the position of a manager watching a report work — they can see, intervene, and course-correct without leaving the surface.

**Phased delivery:**

| Phase | Scope | Target | Effort |
|---|---|---|---|
| **MVP** | Chat-first with tool-call visibility, file diffs, single approval modal | 8 weeks | 2 eng + 1 design |
| **V1** | 3-pane workspace, parallel work, branchable threads, cost/latency HUD | 16 weeks (post-MVP) | +2 eng, +1 design |
| **V2** | Multi-agent orchestration UI, memory explorer, workflow editor, observability dashboard | +6 months | +1 eng |

**The risks that could sink us:**

1. **Latency** — if the agent takes >2s to acknowledge, the user re-engages and gets confused. Streaming + progressive UI is non-negotiable.
2. **Cost** — every visible token in the UI is a cost conversation with the user. Show it.
3. **Trust** — one unsupervised destructive action (delete branch, force-push, paid API call) and the user churns. The approval surface must be airtight.
4. **Complexity** — the 3-pane workspace is more product surface than a chat app. Don't ship the full thing in MVP; ship chat-first and let usage drive the layout.

---

## 2. The 2026 landscape — what others are doing

Six product archetypes worth studying. Each makes a different bet on what the user needs.

### 2.1 Chat-first (Anthropic Claude.ai, ChatGPT, Gemini)

**The bet:** the user wants a conversation; artifacts are bonuses.

```
┌────────────────────────────────────┐
│  History (left rail)               │
├────────────────────────────────────┤
│                                    │
│   Chat stream (centered)           │
│                                    │
│   ┌──────────┐                     │
│   │ Artifact │  ← right-side       │
│   │  panel   │    slide-out        │
│   └──────────┘                     │
│                                    │
└────────────────────────────────────┘
```

**Strengths:** lowest learning curve; works on phone; "Artifacts" pattern (Claude.ai) is great for code/UI/doc output.

**Weaknesses:** hides the agent's work; poor for multi-file changes; no sense of "what is it doing right now" beyond the message stream.

**For openmate:** good MVP pattern; we'll outgrow it.

### 2.2 IDE-first (Cursor, Windsurf, Cline)

**The bet:** the user lives in code; the chat is a sidekick.

```
┌──────────────────────────────────────────┐
│  Editor (90% of screen)                   │
│  ┌────────┬──────────────────────────┐   │
│  │ File   │                          │   │
│  │ tree   │      Code                │   │
│  │        │                          │   │
│  └────────┴──────────────────────────┘   │
│  Chat panel (bottom, ~30% height)         │
│  Composer / Cmd-K (overlay)               │
└──────────────────────────────────────────┘
```

**Strengths:** developers already live here; fast inline edits; multi-file Composer.

**Weaknesses:** chat feels second-class; no good story for non-code tasks (browsing, deploying); the editor is the bottleneck when the agent wants to take a long autonomous action.

**For openmate:** wrong primary metaphor — we're not just an editor. We are an agent.

### 2.3 Workspace-first (Devin, Manus, Replit Agent)

**The bet:** the user wants to *delegate an entire project*, not write code.

```
┌──────────────────────────────────────────────────────┐
│  Plan / steps (top)                                  │
├────────────────┬─────────────────────┬───────────────┤
│  Chat          │  Live environment   │  Artifacts /  │
│  (left)        │  (browser, editor,  │  files        │
│                │   terminal)         │  (right)      │
└────────────────┴─────────────────────┴───────────────┘
```

**Strengths:** shows the *whole* environment; user can see the agent browsing, coding, running; closest to "watching an employee work."

**Weaknesses:** complex product; heavy compute (full VM per session); high cost; UI is dense.

**For openmate V1:** the right direction. Worth the engineering cost.

### 2.4 Canvas-first (Lovable, Bolt, v0, Figma Make)

**The bet:** the user wants to *see* the artifact, not read about it.

```
┌──────────────────┬────────────────────────┐
│                  │                        │
│   Chat           │     Live preview       │
│   (left)         │     (right)            │
│                  │                        │
│                  │     of generated       │
│                  │     UI / app           │
│                  │                        │
└──────────────────┴────────────────────────┘
```

**Strengths:** immediate visual feedback; great for design/UI tasks.

**Weaknesses:** narrow use case (UI generation); doesn't generalize to "fix the auth flow" or "migrate the database."

**For openmate:** borrow the live-preview pattern for any "show me" output.

### 2.5 Multi-agent orchestration (AutoGen Studio, LangGraph Studio, CrewAI)

**The bet:** one agent isn't enough; the user wants to coordinate a team.

```
┌──────────────────────────────────────────┐
│  Agent graph (top)                       │
│  ┌───┐ → ┌───┐ → ┌───┐                   │
│  │ A │   │ B │   │ C │                   │
│  └───┘   └───┘   └───┘                   │
├──────────────────────────────────────────┤
│  Per-agent log + state (bottom)          │
└──────────────────────────────────────────┘
```

**Strengths:** power-user feature; observability; lets users design workflows visually.

**Weaknesses:** expert-only; doesn't solve a 90% use case.

**For openmate V2:** essential for power users; skip in MVP.

### 2.6 Computer-use (ChatGPT Operator, Anthropic Computer Use, Adept)

**The bet:** the agent should be able to do *anything a human can do on a screen.*

**Strengths:** generalizes to anything with a UI; doesn't need a tool per API.

**Weaknesses:** slow, expensive, fragile; needs human approval for everything; high error rate.

**For openmate V1+:** include as an opt-in tool, not the default path. Code agents should prefer code APIs over computer use.

### 2.7 What this means for us

| Pattern | Where we are | When to reach for it |
|---|---|---|
| Chat-first | MVP | First 2 months |
| IDE-first | We are not this | Never — we're an agent, not an editor |
| Workspace-first | V1 target | Months 3–6 |
| Canvas-first | V1 (for UI generation only) | When we add UI generation |
| Multi-agent orchestration | V2 | When we have power users |
| Computer use | V1+ opt-in | When we have browser tools |

**The shape of the answer:** chat-first MVP → 3-pane workspace at V1 → multi-agent + computer use at V2. Don't ship all of it on day one.

---

## 3. Core UX principles for agentic UIs

These are the principles that distinguish a good agentic UI from a chatbot with tools bolted on.

### 3.1 Show the work

The agent's reasoning and tool calls are **first-class content**, not hidden plumbing.

| Bad | Good |
|---|---|
| "Done, I fixed the bug." | "I read src/auth.ts → ran the failing test → found the bug in the token validation → wrote a fix → re-ran tests (passing)." |
| Spinner for 30s | Live tool-call list: `read_file ✓ → grep_content ✓ → edit_file ⏳` |
| Final answer only | Each step visible as it happens, expandable for detail |

**Implementation:** every tool call renders as a card. The card expands to show args (formatted), result (truncated), duration, and a re-run button. Stack the cards like a timeline.

### 3.2 Bounded autonomy is a UI primitive

The user needs to see and control the agent's permission level. Not as a settings page, but as a visible badge.

| Level | What the agent can do | UI badge |
|---|---|---|
| **Read-only** | Read files, search, ask questions | 🟢 Read-only |
| **Workspace** | Read + write files in the project | 🟡 Workspace |
| **Full** | Read + write + network + run commands | 🔴 Full |
| **Custom** | User-defined allowlist | ⚙️ Custom |

**Default to the lowest level the user hasn't overridden.** Show the badge prominently in the top bar. When the agent tries to do something outside its level, show a modal: "This requires Workspace access. Allow once / Allow for this session / Allow always."

### 3.3 Reversibility is non-negotiable

Every action the agent takes should be undoable. The UI must make this obvious.

- **File changes** → show a diff; let the user revert any file
- **Git commits** → show the commit; let the user reset to any prior commit
- **Network calls** → log them; let the user re-run / cancel
- **Long-running processes** → show the process; let the user kill it
- **Memory writes** → show what the agent remembered; let the user delete entries

**The "rewind" button.** A "rewind to here" affordance at every step in the agent's timeline. The user can rewind to any point and continue from there. This is the single biggest trust signal you can ship.

### 3.4 The user is the manager, not the bystander

The UI should make the user feel like they're *managing* an employee, not *watching* a demo. That means:

- **Approval queue** for high-risk actions (delete, push, paid API calls)
- **Interrupt** — the user can pause the agent mid-action, redirect, resume
- **Redirect** — "instead of that, do X" works without losing the agent's state
- **Skip** — "I don't need that step" works too

**The agent should never block for >2s without showing progress.** If it does, the user assumes it's broken and re-engages, which is worse than a 30s wait with good progress.

### 3.5 The cost is the user's money

Token cost must be visible, in the user's currency, updated in real-time.

```
Session cost: $0.42
  ↳ Sonnet 5:    $0.31  (124K input, 8K output)
  ↳ Haiku 4.5:   $0.11  (routing + tool selection)
  ↳ Cache hits:  -$0.08
Time: 4m 23s · Steps: 12 · Tokens: 387K
```

**Why this matters:** the user is paying the bill. Hiding the cost is a trust violation. The cost display is also a *teaching* tool — the user learns what kinds of tasks are expensive.

### 3.6 Latency is felt, not measured

User perception of speed is more important than actual speed. Techniques:

- **Stream everything.** First token in <500ms. Tool calls stream as they happen. File diffs render progressively.
- **Skeleton states.** Show what the agent *is going to do* before it does it. "I'll read 3 files, run the tests, then write a fix."
- **Progressive disclosure.** Don't dump 50 tool results at once. Stream them.
- **Optimistic UI.** Show "Reading src/auth.ts..." the moment the model emits the tool call, before the runtime confirms.

### 3.7 The error is the design

When the agent fails (and it will), the UI's job is to make recovery obvious.

- **Tool call failed** → show the error, the args, the partial result; offer "retry" / "skip" / "abort"
- **Model hit a rate limit** → queue the next step, show a "throttled, retrying in 5s" indicator
- **Hallucinated a tool call** → runtime rejects it, show the user "the model tried to call a non-existent tool 'foo_bar'; treating as no-op"
- **Run out of context** → auto-compact, show "compressed 800K → 200K, continuing"
- **User needs to decide** → surface the question in the chat, pause the run

The error message is part of the product. Generic "Something went wrong" is a fail.

---

## 4. The key UI patterns (the building blocks)

These are the components every agentic UI needs. Build them once, compose them everywhere.

### 4.1 The streaming message

```
┌─────────────────────────────────────┐
│ User: "Fix the auth bug"            │
│                                     │
│ ┌─ Agent ─────────────────────────┐  │
│ │                                 │  │
│ │ I'll start by reading the auth  │  │  ← streams token by token
│ │ file...                         │  │
│ │                                 │  │
│ │ ┌── Tool call ───────────────┐  │  │  ← renders as it happens
│ │ │ 📄 read_file                │  │  │
│ │ │   src/auth.ts               │  │  │
│ │ │   ✓ 2.1KB · 87ms           │  │  │
│ │ └─────────────────────────────┘  │  │
│ │                                 │  │
│ │ Found it. The token validation  │  │
│ │ is...                           │  │
│ └─────────────────────────────────┘  │
└─────────────────────────────────────┘
```

**Implementation:** SSE or WebSocket from the agent runtime; render each event (token, tool_call_start, tool_call_result, message_end) as a separate React node. Use a virtualization library (react-virtuoso) if the message gets long.

### 4.2 The tool call card

```
┌─────────────────────────────────────────────┐
│ 📄 read_file                  ✓ 87ms        │
│   src/auth.ts                                │
│   ─────────────────────────                  │
│   2.1KB · 47 lines                          │
│   [view result] [re-run] [copy args]         │
└─────────────────────────────────────────────┘
```

Every tool call gets a card. The card shows:
- Tool icon + name
- Status (running, success, failed, awaiting-approval)
- Duration
- Args (formatted, truncated, expandable)
- Result preview (truncated, expandable)
- Actions (re-run, copy, view raw)

**Color coding:** gray for reads, blue for writes, red for destructive, yellow for awaiting-approval.

### 4.3 The diff viewer

When the agent edits a file, the diff is the most important UI element.

```
┌─────────────────────────────────────────────┐
│ src/auth.ts · edit_file                    │
│ ─────────────────────────────────────────  │
│  42 │  function validate(token: string) {   │
│  43 │ -    return token.length > 0;         │
│    │ +    if (!token) return null;          │
│    │ +    const decoded = jwt.verify(...)   │
│    │ +    return decoded.exp > Date.now()   │
│  44 │  }                                    │
│ ─────────────────────────────────────────  │
│ [view file] [revert this hunk] [revert all] │
└─────────────────────────────────────────────┘
```

**Requirements:** syntax highlighting, side-by-side or unified (user choice), line numbers, ability to revert any hunk. Use Monaco or CodeMirror for the diff renderer.

### 4.4 The approval modal

For destructive actions, the user must approve before the action runs.

```
┌─────────────────────────────────────────────┐
│ ⚠ The agent wants to run:                   │
│                                             │
│   git push --force-with-lease origin main   │
│                                             │
│ Risk: HIGH (force-push to main)             │
│ Reversibility: partial (history rewrite)   │
│ Estimated cost: 0 (free)                    │
│                                             │
│ [Reject]  [Run once]  [Allow for session]   │
│                                             │
│ ☐ Always allow this exact command           │
└─────────────────────────────────────────────┘
```

**Non-negotiables:** show the *exact* command, classify the risk, offer session-level and always-allow options. Never silently run destructive actions.

### 4.5 The plan / step timeline

For multi-step tasks, show the plan up front and tick steps as they complete.

```
📋 Plan: Fix the auth bug
  1. ✓ Read src/auth.ts                          (1.2s)
  2. ✓ Search for related test files            (0.4s)
  3. ⏳ Run failing test to confirm the bug     (running...)
  4. ⏸ Edit src/auth.ts to fix the validation   (waiting for approval)
  5. ◯ Re-run the test suite                    (pending)
  6. ◯ Commit the fix                           (pending)
```

The plan is editable — the user can remove steps, add steps, reorder. The agent adapts.

### 4.6 The cost / latency HUD

Persistent display in the top bar or footer.

```
$0.42  ·  4m 23s  ·  12 steps  ·  Sonnet 5
```

Click to expand → full breakdown by model, by phase, by tool.

### 4.7 The memory / context inspector

A right-panel view showing what the agent "remembers" — the active context, the conversation history, the memory store.

```
┌─────────────────────────────────────┐
│ Context (847K / 1M)                 │
│ ─────────────────────────────       │
│  System prompt      2.1K            │
│  Tools (24)        18.4K            │
│  Skills (3)         4.2K            │
│  History (47 turns) 312K            │
│  Tool results       487K            │
│  Plan + scratchpad  23.4K           │
│ ─────────────────────────────       │
│  Cache hit: 73% (saved $0.21)      │
│  [view full] [clear]                │
└─────────────────────────────────────┘
```

**Why this matters:** the user wants to know what the agent is "looking at." It also makes compaction visible (the user sees context drop from 800K to 200K after a compact).

### 4.8 The branchable thread

A conversation is a tree, not a list. The user can branch from any point.

```
Main:  "Fix the auth bug"  →  ✓ done
       ├─ Branch: "What if we used OAuth instead?"  →  in progress
       └─ Branch: "Apply the fix to staging"  →  ✓ done
```

Click on a branch node → fork the conversation from that point. The original continues unchanged. **This is the single biggest power-user feature for an agentic UI in 2026.**

---

## 5. The recommended architecture for openmate

### 5.1 The 3-pane workspace (V1)

```
┌────────────────────────────────────────────────────────────────────────┐
│ Top bar:  [openmate]  Agent: coding-1 ▾  Mode: Workspace ▾  ⏸  $0.42 👤│
├──────────────┬──────────────────────────────────┬──────────────────────┤
│ LEFT         │ CENTER                           │ RIGHT                │
│              │                                  │                      │
│ Chat         │ Tab bar:                         │ Inspector:           │
│  (350px)     │  [Files] [Diff] [Browser] [Term] │  Tabs:               │
│              │                                  │  [Steps] [Plan]      │
│ Thread list  │ ┌────────────────────────────┐   │  [Cost] [Memory]     │
│  at top      │ │                            │   │  [Logs] [Settings]   │
│              │ │  File tree + code          │   │                      │
│ Message      │ │  OR                        │   │ Step 3/12:           │
│  stream      │ │  Diff view                 │   │  read_file           │
│  below       │ │  OR                        │   │  src/auth.ts         │
│              │ │  Browser preview           │   │  ✓ 87ms             │
│ Input box    │ │  OR                        │   │                      │
│  at bottom   │ │  Terminal                  │   │ [All steps]          │
│              │ │                            │   │  ✓ read_file 87ms    │
│              │ └────────────────────────────┘   │  ✓ grep 23ms         │
│              │                                  │  ⏳ test_running     │
│              │                                  │  ⏸ edit_awaiting     │
│              │                                  │  ◯ re_run            │
└──────────────┴──────────────────────────────────┴──────────────────────┘
```

**Pane behaviors:**

- **Left pane (Chat).** Threaded conversation. User types here. The agent's tool calls appear here as cards. Streaming messages. Branch button on any message.
- **Center pane (Work).** The thing the agent is acting on. Tabbed: Files / Diff / Browser / Terminal. Default tab depends on the current step. Files tab = file tree + Monaco editor (read-only by default; the agent edits). Diff tab = side-by-side diff of pending changes. Browser tab = embedded browser for web tasks. Terminal tab = embedded shell for build/test.
- **Right pane (Inspector).** Per-step detail. Tabs: Steps / Plan / Cost / Memory / Logs / Settings. Steps = the timeline of what the agent has done, with the current step highlighted. Plan = the high-level task plan with editable steps. Cost = live cost breakdown. Memory = what's in the agent's context. Logs = raw tool-call log. Settings = per-session config (model, autonomy level, etc.).

**Why this layout works:**

1. **The user is always oriented.** At any moment, they know: what they asked (left), what the agent is doing (center), what the agent has done (right).
2. **The right pane is the trust surface.** This is where approvals, costs, and the step log live. It should be the most visible, most polished part of the UI.
3. **The center pane is a "viewport" into the agent's work.** Whatever the agent is acting on, it lives here. This is also where the user can take over (edit the file manually, run a command themselves).
4. **Panes are resizable and collapsible.** A power user with two monitors may want all three panes at full width. A mobile user (read-only mode) gets just the left pane.

### 5.2 The MVP scope (ship in 8 weeks)

For MVP, **ship a 2-pane layout** (chat + inspector), defer the center pane to V1.

```
┌────────────────────────────────────────────────────────────────┐
│ Top bar                                                          │
├──────────────────────────────────┬──────────────────────────────┤
│                                  │                              │
│  Chat (left, 60%)                │  Inspector (right, 40%)     │
│  ────                            │  ────                        │
│  Streaming messages              │  Steps timeline              │
│  Tool call cards                 │  Plan view                   │
│  File diffs inline               │  Cost HUD                    │
│  Approval modals                 │  Memory inspector (read)     │
│                                  │  Logs (raw)                  │
│                                  │                              │
│                                  │                              │
└──────────────────────────────────┴──────────────────────────────┘
```

**Why defer the center pane:** the center pane requires a real-time file tree, a code editor, an embedded browser, and a terminal — each is a non-trivial engineering effort. The chat + inspector is enough to validate the agent experience. **Add the center pane when the agent is doing work the user wants to see directly (browsing, code editing, long-running commands).**

**MVP feature list:**

- Streaming chat with token-by-token rendering
- Tool call cards (read, write, destructive)
- Inline file diffs
- Approval modal for destructive actions (destructive tools, paid APIs, force-push)
- Step timeline (right pane)
- Plan view (right pane)
- Cost HUD (top bar, live)
- Memory inspector (read-only, right pane)
- Autonomy level badge + setting
- Branchable threads (read-only at MVP; write at V1)
- 5 example skills (review-pr, debug-test, refactor, draft-doc, search-code)
- MCP server support (3 example MCP servers: GitHub, file system, web search)
- CLI fallback (auto-detect `gh`, `git`, `npm` etc. and use as tools)

**MVP non-goals:**

- Multi-agent orchestration
- Workflow editor
- Observability dashboard (beyond per-session step log)
- Voice input
- Mobile-optimized (desktop only at MVP)
- Self-hosted (cloud only at MVP)

### 5.3 The tech stack (recommended)

**Frontend:**

- **Next.js 15** (App Router) — React 19, server components, streaming SSR
- **TypeScript** — strict, no `any` in shared code
- **Tailwind CSS 4** — utility-first, design tokens via CSS variables
- **shadcn/ui** — headless component primitives, copy-paste, owned
- **Zustand** — client state (chat stream, current step, autonomy level)
- **TanStack Query** — server state (sessions, threads, file content)
- **react-virtuoso** — virtualize long message lists
- **Monaco Editor** — code + diff (V1; not MVP)
- **xterm.js** — embedded terminal (V1; not MVP)
- **Vercel AI SDK** — streaming patterns, tool-call rendering

**Backend (already covered in `aws-agent-infra.md`):**

- **Amazon Bedrock** — model access (Claude Opus 5, Sonnet 5, Haiku 4.5)
- **Bedrock AgentCore Runtime** — host the agent sessions (microVM-isolated, 8h ceiling)
- **AgentCore Gateway** — turn MCP servers into a unified tool surface
- **AgentCore Identity** — OAuth brokering (GitHub, Google, etc.)
- **AgentCore Memory** — short-term session + long-term semantic memory
- **AgentCore Observability** — CloudWatch + OTEL traces
- **AgentCore Evaluations** — online + on-demand quality scoring
- **S3 Vectors** — archive of conversation embeddings for search
- **Aurora PostgreSQL with pgvector** — hot tier for memory, skill/tool retrieval
- **ElastiCache Redis** — session cache, rate-limit counters, prompt cache hits
- **CloudFront** — static assets, the openmate web app itself
- **Step Functions** — long-running orchestration (deploys, migrations)

**Real-time:**

- **WebSocket** via API Gateway for the agent stream (or SSE for one-way)
- **EventBridge** for cross-session events (the agent triggers a deploy → frontend shows toast)
- **CloudWatch + OTEL** for observability (every tool call, every model call, traced)

### 5.4 The data model for the UI

```typescript
// Core types the frontend cares about

type AutonomyLevel = "read_only" | "workspace" | "full" | "custom";

type Session = {
  id: string;
  userId: string;
  agentId: string;
  threadId: string;
  parentMessageId?: string;     // for branching
  autonomyLevel: AutonomyLevel;
  createdAt: string;
  status: "running" | "paused" | "awaiting_approval" | "completed" | "failed";
  costUsd: number;
  totalTokens: number;
  stepCount: number;
  startedAt: string;
  endedAt?: string;
};

type Message = {
  id: string;
  sessionId: string;
  role: "user" | "assistant" | "tool" | "system";
  content: ContentBlock[];
  createdAt: string;
  // For branching:
  parentMessageId?: string;
  childMessageIds: string[];
};

type ContentBlock =
  | { type: "text"; text: string; streaming: boolean }
  | { type: "tool_call"; toolName: string; args: object; result?: ToolResult; status: ToolStatus; durationMs?: number; }
  | { type: "file_diff"; path: string; before: string; after: string; hunks: DiffHunk[] }
  | { type: "approval_request"; toolCallId: string; preview: string; riskClass: RiskClass; expiresAt: string }
  | { type: "image"; url: string; alt: string }
  | { type: "error"; code: string; message: string; retryable: boolean };

type Step = {
  id: string;
  sessionId: string;
  index: number;
  plan: string;
  status: "pending" | "running" | "awaiting_approval" | "completed" | "failed" | "skipped";
  toolCalls: ToolCall[];
  startedAt?: string;
  endedAt?: string;
  costUsd: number;
};

type Approval = {
  id: string;
  sessionId: string;
  toolCallId: string;
  description: string;
  riskClass: "low" | "medium" | "high" | "destructive";
  preview: string;
  status: "pending" | "approved" | "rejected" | "expired";
  expiresAt: string;
  userChoice?: "run_once" | "session" | "always";
};
```

**These types should live in a shared package** (not duplicated in client and server). Use TypeScript's `tsc --noEmit` to enforce type parity.

### 5.5 The streaming protocol

The agent runtime emits events over WebSocket. The frontend renders each event type as a different UI affordance.

```typescript
type StreamEvent =
  | { type: "message_start"; messageId: string; role: "assistant" }
  | { type: "text_delta"; messageId: string; delta: string }       // streaming token
  | { type: "tool_call_start"; toolCallId: string; name: string; args: object }
  | { type: "tool_call_result"; toolCallId: string; result: ToolResult; durationMs: number }
  | { type: "approval_required"; toolCallId: string; preview: string; riskClass: RiskClass }
  | { type: "step_start"; stepId: string; plan: string }
  | { type: "step_end"; stepId: string; status: StepStatus; costUsd: number }
  | { type: "cost_update"; sessionCostUsd: number; tokens: number }
  | { type: "message_end"; messageId: string; reason: "stop" | "tool_use" | "length" | "error" }
  | { type: "error"; code: string; message: string; retryable: boolean };
```

**Reconnection:** the WebSocket should support resumption. If the connection drops, the client sends `lastEventId` and the server replays missed events from the session log. Use SSE as a fallback for users behind aggressive proxies.

**Backpressure:** if the user closes the tab, the agent keeps running. The session is server-side. Reopening the tab replays the events.

---

## 6. The 2026 trends worth betting on

### 6.1 Trend 1: Computer use is becoming a tool, not the whole product

ChatGPT Operator, Anthropic Computer Use, Adept — the early demos were "the agent IS the computer." The 2026 product reality: **computer use is one tool in the agent's belt**, used when no API is available, with explicit human approval for every action.

**For openmate:** include browser-use as an opt-in tool, default to API tools when available, never silent computer-use.

### 6.2 Trend 2: Multi-agent orchestration is the power-user feature

The 2026 cohort (Cursor Composer, Devin's planning agent, Manus's sub-agents) shows that sophisticated users want to *coordinate* agents, not just prompt one. The UI for this is a graph view: agents as nodes, handoffs as edges.

**For openmate V2:** ship a workflow editor where users can compose agents, skills, and tools into a graph. Skip in MVP.

### 6.3 Trend 3: Cost transparency is the differentiator

Every serious agent product in 2026 surfaces cost in the UI. The ones that hide it get roasted in reviews. The ones that show it well (Cursor, v0) build trust.

**For openmate:** show cost in the top bar from day one. The cost display is a *feature*, not a *setting*.

### 6.4 Trend 4: Memory is becoming user-visible and user-editable

ChatGPT's Memory, Claude's Projects, Cursor's codebase indexing — all expose "what the AI remembers" to the user, and let the user edit / delete it. The 2026 expectation: memory is a first-class UI surface.

**For openmate:** ship the memory inspector at V1. Let users see what's in context, delete entries, add manual notes. Skip in MVP.

### 6.5 Trend 5: Voice + vision are first-class input

GPT-4o voice mode, Gemini Live, Claude with computer vision — multimodal input is no longer a demo. Users expect to talk to their agent and show it things.

**For openmate V1+:** voice input for chat (push-to-talk is fine), image input for screenshots and photos, file upload for documents.

### 6.6 Trend 6: The "agent desktop" pattern is emerging

A full OS-like environment in the browser: file system, browser, terminal, apps, all agent-controllable. Devin pioneered this; Manus and Replit followed. The agent has a *computer* — not just tools.

**For openmate V2+:** this is the natural evolution. For MVP/V1, the 3-pane workspace is the right scope.

### 6.7 Trend 7: Skills and workflows are user-customizable

Cursor's `.cursorrules`, Claude's custom Skills, openmate's own SKILL.md convention — the 2026 expectation is that **users can write and share their own skills**, not just consume the platform's defaults.

**For openmate:** ship a skill editor in V1. Skills live in the repo (`.openmate/skills/`), get versioned, get evaluated. Same pattern as the rest of the platform.

---

## 7. Risks and tradeoffs

### 7.1 Latency is the silent killer

**The risk:** the agent takes 30s to do meaningful work. The user re-engages, gets confused, types a competing instruction, the agent gets two instructions, the work is wasted.

**Mitigations:**
- Stream everything (TTFT < 500ms)
- Show the plan before execution (so the user knows what's coming)
- Progressive disclosure (don't dump results all at once)
- Optimistic UI (show "Reading src/auth.ts..." the moment the model emits the call, before the runtime confirms)
- "Pause" button always available
- Don't have the model write more than 200 words per turn; break long outputs into chunks

### 7.2 The cost conversation

**The risk:** the user opens the app, runs three tasks, gets a $20 bill, churns.

**Mitigations:**
- Show cost in real-time, prominently
- Set a default session cost cap (e.g., $5, configurable)
- Show estimated cost *before* long-running tasks ("This task may cost $0.50–$2.00; continue?")
- Route cheap tasks to Haiku, expensive reasoning to Opus
- Cache aggressively (prompt caching, tool result caching)
- Free tier with hard limits; paid tier with usage-based pricing
- **Don't surprise the user with cost** — ever

### 7.3 Trust is earned in drops, lost in buckets

**The risk:** one unsupervised destructive action (delete a branch, force-push to main, send an email) and the user never trusts the product again.

**Mitigations:**
- Default autonomy is "read-only"; user must opt in to higher levels
- Every destructive action requires explicit approval, every time
- Risk classification is a runtime concern, not a UI concern — the runtime refuses destructive actions outside policy
- Audit log: every action is logged with user, session, timestamp, args, result
- "Rewind" affordance: undo any action, even ones already approved
- Educate the user about risk classes in the onboarding flow

### 7.4 Complexity creep

**The risk:** the 3-pane workspace + branchable threads + workflow editor + multi-agent + memory inspector becomes a Confluence-tier product. Users open it once, get confused, leave.

**Mitigations:**
- MVP is chat-only; add panes based on usage data
- Progressive disclosure — hide advanced features behind menus
- Default state is the simplest useful state; power features are opt-in
- "I'm new" onboarding that walks through the basics
- "I'm experienced" mode that turns on everything

### 7.5 The "tool graveyard"

**The risk:** users accumulate 50 enabled tools, 20 enabled skills, 10 enabled MCP servers. The model gets confused (selection error rate goes up), the context gets bloated (cost goes up), nothing works.

**Mitigations:**
- Curated toolset per agent (the openmate platform enables only the tools each agent needs)
- Tool retrieval (semantic search over tool descriptions, top-k per turn — same pattern as skill retrieval)
- Skill retrieval for >50 skills
- "Tool health" indicator — show which tools are stale, broken, or rarely used
- One-click "disable all tools except the basics"

### 7.6 Open-source distribution

**The risk:** openmate is open-source, but the agent runtime, observability, and UI are tightly coupled to AWS. The "open" part is the protocol, not the stack.

**Mitigation:** this is a *positioning* question, not a technical one. Define what's open (skills, MCP servers, agent configs, eval sets, the UI itself) vs what's cloud-managed (the runtime, observability, the FM calls). The user's call.

---

## 8. Phased roadmap

### Phase 0: Foundation (weeks 1–4, parallel to MVP build)

- Set up the AgentCore Runtime skeleton
- Set up the Bedrock + AgentCore Gateway + Identity stack
- Set up the streaming protocol (WebSocket + SSE fallback)
- Define the data model (Session, Message, Step, Approval types)
- Set up observability (OTEL traces, CloudWatch, structured logs)
- Set up eval set (10 golden threads, scored nightly)
- **Owner:** 1 eng + 1 SRE

### Phase 1: MVP — Chat-first (weeks 5–12)

- Next.js + shadcn/ui skeleton
- 2-pane layout (chat + inspector)
- Streaming chat with tool-call cards
- File diffs inline
- Approval modal for destructive actions
- 5 example skills
- 3 example MCP servers
- CLI auto-detection
- Cost HUD in top bar
- Autonomy level badge + setting
- **Owner:** 2 eng + 1 design
- **Acceptance:** 10 internal users complete 3 tasks each with > 70% satisfaction

### Phase 2: V1 — 3-pane workspace (weeks 13–28)

- Center pane (Files / Diff / Browser / Terminal tabs)
- Monaco editor integration
- Embedded browser (Playwright or similar)
- xterm.js for terminal
- Memory inspector (read-write)
- Branchable threads (write)
- Voice input (push-to-talk)
- Image input
- Skill editor (`.openmate/skills/`)
- **Owner:** +2 eng, +1 design
- **Acceptance:** 50 beta users, 80% week-2 retention, <2% destructive-action incidents

### Phase 3: V2 — Multi-agent + observability (months 7–12)

- Multi-agent orchestration UI (graph view)
- Workflow editor (LangGraph-style)
- Observability dashboard (per-session traces, per-skill eval, cost analytics)
- MCP server registry + marketplace
- Self-hosted option (Docker compose for the runtime)
- **Owner:** +1 eng
- **Acceptance:** power-user adoption, marketplace GMV if applicable

---

## 9. Cost & team estimate

### Team (rough)

| Phase | Eng | Design | SRE | Total |
|---|---|---|---|---|
| MVP | 2 | 1 | 0.5 | 3.5 FTE |
| V1 | 4 | 1 | 1 | 6 FTE |
| V2 | 5 | 1 | 1 | 7 FTE |

### Per-user infra cost (rough, 2026 pricing)

A typical "active" openmate user runs ~10 sessions/month, each averaging 1M input tokens, 50K output tokens, with Haiku routing + Sonnet 5 reasoning.

```
Per session (rough):
  Input:  1M tokens × $3/1M (Sonnet 5) = $3.00
  Output: 50K tokens × $15/1M (Sonnet 5) = $0.75
  Cache savings:  -$1.50 (with prompt caching)
  Tool calls:  ~$0.20 (avg 20 tool calls, mixed)
  Runtime:  ~$0.10 (AgentCore invocations)
  ─────────────────────────────
  Per session: ~$2.55

Per user / month: 10 × $2.55 = $25.50
```

**Pricing implications:** at $25.50 infra cost per active user, you can charge $30–$60/month and have healthy unit economics. Free tier should be 5–10 sessions/month to drive adoption without bankrupting.

**Cost levers:**
- Route cheap tasks to Haiku 4.5 (10× cheaper)
- Aggressive prompt caching (40–90% off)
- Tool result caching
- Compact conversations aggressively
- Use S3 Vectors for cold tier (not OpenSearch)

---

## 10. Open questions for the VP

These are the decisions that shape the build. We need to resolve them before or during MVP.

1. **Pricing model.** Per-seat? Per-session? Per-token pass-through? Freemium with usage caps? The UI design has cost-transparency features that work differently depending on the model.
2. **Autonomy defaults.** What does a new user get? My recommendation: read-only + 5 starter skills, no destructive tools enabled, no network tools. Opt-in for everything.
3. **Open-source strategy.** What's open (UI, skills, MCP servers, eval sets) vs cloud-managed (runtime, observability, FMs)? This affects what the UI ships with vs what the platform enables.
4. **Multi-tenant model.** Per-user isolation? Per-team? Per-org? Affects auth, RBAC, and the inspector's per-step visibility.
5. **Mobile story.** Read-only mobile (view the agent, get notifications) at V1? Or full mobile at V2? Recommendation: read-only mobile at V1.
6. **Enterprise / compliance.** SOC 2? FedRAMP? HIPAA? Each adds a layer to the approval surface, the audit log, and the data model.
7. **The "computer use" question.** Do we ship a browser tool at V1, or wait for the technology to mature? Recommendation: ship at V1 as opt-in, never default.
8. **Self-hosted timeline.** Docker compose at V2? A proper on-prem install at V3? Affects what the runtime architecture must support.
9. **The model mix.** Single provider (Anthropic) for simplicity, or multi-provider (Anthropic + OpenAI + Google) for flexibility and cost arbitrage? Affects the model routing layer and the cost HUD.
10. **The eval surface.** Do we expose the eval set to users (let them contribute), or keep it internal? Affects the trust model and the long-term quality of the platform.

---

## 11. The one-paragraph version

**The agentic web UI in 2026 is a 3-pane workspace — chat on the left, work surface in the center, inspector on the right — with streaming everything, visible tool execution, bounded autonomy as a UI primitive, one-click course-correction, cost transparency, and reversibility by default. Build chat-first MVP in 8 weeks (2 eng + 1 design), then add the center pane at V1. Tech: Next.js 15 + React 19 + shadcn/ui + Vercel AI SDK on the frontend, Bedrock + AgentCore on the backend. The competitive moat is the trust surface — the controls that make the agent safe enough to actually let it touch the user's code. The biggest risks are latency (mitigated by streaming), cost (mitigated by transparency + caching), and trust (mitigated by bounded autonomy + reversibility + audit). Ship the chat-first MVP, instrument everything, let usage data drive the V1 layout. The single biggest mistake would be trying to ship the full 3-pane workspace on day one.**
