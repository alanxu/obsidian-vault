---
title: Conversation Memory / Context Manager
slug: conversation-memory-manager
type: agentic
leetcode: null
companies: [Anthropic, OpenAI, Anysphere, Cognition, "any chat / agent product"]
difficulty: ★★★☆☆
frequency: rising
formats: [Live, Take-home]
levels: 1
time-box: live 30–45 min
time-box-take-home: 4–8 hours
tags: [agent, memory, token-budget, sliding-window, summarization, retrieval]
related: ["[[17-lru-cache]]", "[[16-minimal-agent-loop]]", "[[D1-rag-with-citations]]"]
---

# Conversation Memory / Context Manager

Keep chat history inside a **token budget** — sliding window, summary buffer, and pinning. The agent's working memory; an extremely common 2026 ask. The interesting parts are the **policies**, not the data structure.

## Problem

Implement a `Memory`:

- `add(role, content)` — append a message.
- `context() -> list[msg]` — return messages that fit `max_tokens`, **always keeping**:
  - the system prompt (pinned),
  - the most recent turns,
  - and **summarizing/compacting** older turns when over budget.
- Optional `summarize(messages) -> str` injected for summary-buffer strategy.

## Strategies (the trade-off space)

| Strategy | Read | Write | Loss | Cost |
|---|---|---|---|---|
| **Sliding window** | O(M) | O(1) | drops oldest turns | free |
| **Summary buffer** | O(M) | O(1) amortized | older turns compressed | LLM call |
| **Retrieval** | O(M) | O(1) amortized | retrieved vs dropped | embedding + vector lookup |
| **Hybrid** (window + retrieval) | O(M) | O(1) amortized | tunable | embedding + storage |

The **window-only** approach is simplest and always safe. **Summary** adds cost but preserves gist. **Retrieval** scales to long conversations but needs infra.

## Core approach (format-agnostic)

```python
class Memory:
    def __init__(self, max_tokens, token_fn, summarize=None):
        self.msgs = []
        self.max = max_tokens
        self.tok = token_fn                # injectable for testability
        self.summarize = summarize

    def add(self, role, content):
        self.msgs.append({"role": role, "content": content})

    def context(self):
        system = [m for m in self.msgs if m["role"] == "system"]
        rest = [m for m in self.msgs if m["role"] != "system"]
        budget = self.max - sum(self.tok(m["content"]) for m in system)

        kept = []
        for m in reversed(rest):           # newest first
            t = self.tok(m["content"])
            if t <= budget:
                kept.append(m)
                budget -= t
            else:
                break
        kept.reverse()
        dropped = rest[:len(rest) - len(kept)]

        if dropped and self.summarize:
            summary = self.summarize(dropped)
            kept = [{"role": "system", "content": f"Earlier summary: {summary}"}] + kept
        return system + kept
```

**Complexity.** Per `context()`: O(M). With caching: O(1) until a new `add`.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** "manage the chat history so it fits the context window" (~15 min), then "what about very long conversations?" (~15 min).
- **Follow-ups (real, reported):**
  - **Summary buffer** vs pure sliding window vs **retrieval** over old turns → see [[D1-rag-with-citations]].
  - **Per-tool-result truncation** — long tool outputs are a memory sink; truncate first.
  - **Importance-weighted eviction** — older turns aren't all equal; some should survive.
  - **Summarize-via-LLM cost** — every context build may call the LLM; cache the summary.
  - **Per-message metadata** — pin certain messages (tool definitions, user constraints) so they're never dropped.
  - **Streaming summary** — generate summary incrementally as messages arrive.
  - **Token estimation accuracy** — tiktoken vs heuristic; off by 10–20% matters at scale.
  - **Conversation branching** — fork a conversation; both branches share history up to fork.
  - **Persistence** — serialize messages; reload on startup.
  - **Multi-user / multi-conversation** — namespacing, isolation.
  - **Privacy / redaction** — scrub PII before adding to context.
- **Tips:**
  - **Pin system + most recent** — both are sacred.
  - **Make `token_fn` injectable** — passes the testability point.
  - **Name the three strategies** (window / summary / retrieval) up front.
  - For token counting: inject a tiktoken-based function in production, a `len(content) // 4` heuristic in tests.
  - For retrieval: per-embed each message; at context time, retrieve top-K by similarity to the latest user turn.
- **Pitfalls:**
  - **Dropping the system prompt** — breaks every instruction.
  - **Dropping the latest user turn** — even worse; the model loses the question.
  - **Counting tokens wrong** — off by message overhead (typically 3–4 tokens per message for role/format).
  - **Unbounded growth** — `add` never compacts; eventually OOM.
  - **Summarizing every call** — cost; summarize lazily or when crossing a threshold.
  - **Summarization losing key facts** — names, IDs, decisions; instruct the summarizer to preserve these.
  - **Recursive summaries** — summarizer summarizing a previous summary; quality degrades.

### Take-home / work-trial
- **Tips:**
  - Implement window + summary strategies behind a flag.
  - Tests for the budget boundary (exactly at budget, one token over).
  - README the retrieval extension.
  - Include a benchmark with a long conversation showing memory shape over time.
- **Pitfalls:**
  - **No budget enforcement** — the bug the question is testing.
  - **No tests** — silent failures on edge cases.
  - **Summarization that loses key facts** — add a "preserve" instruction.

### Whiteboard (when asked to "design memory")
- **Tips:** Draw the three strategies; show data flow.
- **Pitfalls:** Confusing with retrieval (D1).

## Company variants

- **Anthropic / OpenAI** — canonical.
- **Anysphere / Cognition / agent-product cos** — memory is core UX.
- **Chat-product cos broadly** — every chat needs context management.

## Worked example trace

```
max_tokens = 100, token_fn = len(s)//4

Add:
  system: "You are a helpful assistant."   (5 tokens)
  user:   "Hi"                              (1 token)
  assistant: "Hello! How can I help?"       (4 tokens)
  user:   "Tell me about X"                 (3 tokens)
  assistant: "(long 50-token answer)"      (50 tokens)
  user:   "And Y?"                          (2 tokens)

Budget for non-system: 95 tokens.
Walking newest-first:
  user "And Y?" (2) → keep, budget 93
  assistant long (50) → keep, budget 43
  user "Tell me about X" (3) → keep, budget 40
  assistant "Hello!" (4) → keep, budget 36
  user "Hi" (1) → keep, budget 35

Result: all 5 non-system messages fit. context() = 6 messages.
```

If the assistant answer had been 60 tokens:
```
  user "And Y?" (2) → keep, budget 93
  assistant 60 → keep, budget 33
  user "Tell me about X" (3) → keep, budget 30
  assistant "Hello!" (4) → keep, budget 26
  user "Hi" (1) → keep, budget 25
```

Still fits. Add 6 more long turns → user "Hi" would be dropped (with summary buffer, it'd be summarized).

## Related
[[17-lru-cache]] (eviction thinking) · [[16-minimal-agent-loop]] (the loop's memory) · [[D1-rag-with-citations]] (retrieval memory) · [[32-streaming-response-handler]] (when streaming affects memory).