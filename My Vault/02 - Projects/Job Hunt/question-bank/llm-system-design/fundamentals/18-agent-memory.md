---
title: Agent Memory (short/long-term, working)
slug: agent-memory
area: Agent Concepts
source_q: "Anthropic 100-Q #41–44"
companies: [Anthropic, OpenAI, Anysphere, Robinhood]
difficulty: ★★★★☆
related: ["[[17-react]]", "[[02-context-window-limits]]", "[[practical-coding/33-conversation-memory-manager]]", "[[llm-system-design/09-agent-platform]]"]
---

# Agent Memory

## Prompt
What are short-term and long-term memory in an agent? How do you implement agent memory, and what's the retrieval strategy?

## Answer
**Memory management = context-window engineering** — fitting the *right* information into a bounded window (→ [[02-context-window-limits]]).
- **Short-term (working) memory** — the running context/scratchpad of the current task: recent turns, tool observations, the plan. Lives in the prompt; bounded by the context window.
- **Long-term memory** — facts/episodes that persist **across** sessions: stored in a **vector store or DB** and **retrieved** when relevant (this is RAG applied to the agent's own history).
- **Working memory** — a **summarized/compressed** state that keeps long-horizon context within budget (summarize old turns instead of carrying raw history).

**Implementation:** keep recent turns verbatim; **summarize or evict** older turns when over the token budget (sliding window or summary-buffer); write salient facts to long-term store (embedded); on each step, **retrieve** the top-k relevant memories and inject them. Pin the system prompt + most recent user turn.

**Retrieval strategy:** semantic similarity to the current query/state, plus **recency** and **importance** weighting; dedup; cap how much memory enters the context (it competes with the task for tokens).

## Tradeoffs
| Strategy | Gains | Costs |
|---|---|---|
| Sliding window | simple, cheap | drops old info |
| Summary buffer | keeps gist | lossy, extra LLM cost |
| Vector long-term | recall across sessions | retrieval can miss; infra |

## Follow-ups
- *"Long context vs memory retrieval?"* → retrieval scales better and is cheaper than stuffing everything (→ [[02-context-window-limits]]).
- *"What to remember?"* → importance/utility, not everything; summarize; avoid memory bloat.
- *"Implement it in code?"* → [[practical-coding/33-conversation-memory-manager]] (token-budget truncation + summary buffer).

## Pitfalls
- Dropping the system prompt / latest user turn when truncating.
- Unbounded history → context overflow + cost.
- Summarizing on every call (cost) or losing key facts in summaries.

## Tips
Three buckets — **short-term (context), long-term (vector store), working (summarized)** — and frame it as **"context-window engineering."** Retrieval = semantic + recency + importance. That structure answers all four sub-questions at once.
