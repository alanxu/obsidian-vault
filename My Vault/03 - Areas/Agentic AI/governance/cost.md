---
title: Cost
pillar: governance
parent: ./README.md
section: "4.3"
---

# 4.3 Cost

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
