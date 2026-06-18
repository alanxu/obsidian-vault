---
title: Conversation Memory / Context Manager
slug: conversation-memory-manager
type: agentic
leetcode: null
companies: [Anthropic, OpenAI, general AI-eng]
difficulty: ★★★☆☆
frequency: rising
formats: [Live, Take-home]
levels: 1
time-box: live 30–45 min
tags: [agent, memory, token-budget, sliding-window, summarization]
related: ["[[17-lru-cache]]", "[[16-minimal-agent-loop]]"]
---

# Conversation Memory / Context Manager

Keep chat history inside a **token budget** — sliding window, summary buffer, and pinning. The agent's working memory; an extremely common 2026 ask.

## Problem
Implement a `Memory`: `add(role, content)`; `context()` returns the messages that fit a `max_tokens` budget, **always keeping the system prompt + the most recent turns**, and **summarizing/compacting** older turns when over budget.

## Core approach (format-agnostic)
Store messages with a token count each (inject a `token_fn`). `context()`: always include `system` + walk from newest, accumulating until the budget; older overflow is **dropped (sliding window)** or **summarized** (summary-buffer: replace the oldest block with a short summary). Pin the system message; never evict the last user turn.

```python
class Memory:
    def __init__(self, max_tokens, token_fn, summarize=None):
        self.msgs=[]; self.max=max_tokens; self.tok=token_fn; self.summarize=summarize
    def add(self, role, content): self.msgs.append({"role":role,"content":content})
    def context(self):
        system=[m for m in self.msgs if m["role"]=="system"]
        rest=[m for m in self.msgs if m["role"]!="system"]
        budget=self.max-sum(self.tok(m["content"]) for m in system)
        kept=[]
        for m in reversed(rest):                      # newest first
            t=self.tok(m["content"])
            if t<=budget: kept.append(m); budget-=t
            else: break
        kept.reverse()
        dropped=rest[:len(rest)-len(kept)]
        if dropped and self.summarize:                # summary-buffer strategy
            kept=[{"role":"system","content":self.summarize(dropped)}]+kept
        return system+kept
```

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** "manage the chat history so it fits the context window," then "what about very long conversations?"
- **Follow-ups:** **summary buffer** vs pure sliding window vs **retrieval** over old turns (→ RAG/[[D1-rag-with-citations]]); per-tool-result truncation; importance-weighted eviction; summarize-via-LLM cost.
- **Tips:** pin system + most recent; make `token_fn` injectable (testable); name the window-vs-summary-vs-retrieval trade-off.
- **Pitfalls:** dropping the system prompt or the latest user turn, counting tokens wrong (off by the message overhead), unbounded growth, summarizing every call (cost).

### Take-home / work-trial
- **Tips:** implement window + summary strategies behind a flag, tests for the budget boundary, README the retrieval extension.
- **Pitfalls:** no budget enforcement, no tests, summarization that loses key facts.

## Related
[[17-lru-cache]] (eviction thinking) · [[16-minimal-agent-loop]] (the loop's memory) · [[D1-rag-with-citations]] (retrieval memory).
