---
title: MCP & A2A (agent protocol stack)
slug: mcp-a2a
area: Agent Concepts
companies: [Anthropic, OpenAI, Anysphere, Cognition, "agent-platform teams broadly"]
difficulty: ★★★☆☆
related: ["[[16-agent-loops-and-control]]", "[[llm-system-design/37-mcp-tool-platform]]", "[[practical-coding/30-function-calling-tool-handler]]"]
added: 2026-07-08 (audit fill — rapid-fire staple at agent shops)
evidence: "GUIDE-LEVEL: MCP/A2A named a standard senior-loop topic in 2026 guides; MCP ubiquity in 2026 agent-engineering material corroborates. 'Rapid-fire staple' phrasing is my extrapolation; no company-specific candidate report."
---

# MCP & A2A

## Prompt
What is MCP? How is it different from function calling? What's A2A and when do agent-to-agent protocols matter?

## Answer
**Function calling** is a *model capability*: you pass tool schemas in the request; the model emits a structured call; *your code* executes it. Tools live inside your app — every app × every tool is a bespoke integration (N×M).

**MCP (Model Context Protocol)** standardizes the *integration layer*: tools/resources/prompts are served by independent **MCP servers**; any MCP **client** (Claude, an IDE, your agent) discovers and calls them over a standard protocol (JSON-RPC; stdio or HTTP). Turns N×M into N+M: the GitHub MCP server is written once, used by every client. Key primitives: **tools** (model-invoked actions), **resources** (readable context), **prompts** (reusable templates); discovery (`tools/list`) means capabilities are found at runtime, not compiled in.

**A2A (agent-to-agent)** protocols standardize *delegation between agents* — capability discovery ("agent cards"), task lifecycle (submit → working → artifacts), long-running async tasks. Rule of thumb: **MCP = agent→tool** (verticals: a capability the agent uses), **A2A = agent→agent** (peers: an opaque collaborator with its own reasoning). A2A matters for cross-org/cross-vendor agents; inside one platform, a simple orchestrator ([[19-multi-agent]]) usually beats a protocol.

## Tradeoffs
| Choice | Gains | Costs |
|---|---|---|
| MCP vs hardcoded tools | reuse, discovery, ecosystem, independent ownership | protocol overhead; supply-chain trust (third-party servers) |
| Runtime discovery vs compiled-in | flexibility | context bloat at 1000s of tools → tool retrieval; selection errors |
| A2A vs orchestrator-owned subagents | cross-vendor interop | contract weaker (peer is stochastic); budget/trust propagation unsolved |

## Follow-ups
- *"Is MCP just function calling with extra steps?"* → the model-side mechanics are identical (schema → structured call); MCP standardizes everything *around* it: transport, discovery, auth, ownership.
- *"Security concerns?"* → malicious/compromised servers (tool descriptions and outputs are injection vectors), credential scoping, the lethal trifecta → platform answer in [[llm-system-design/37-mcp-tool-platform]].
- *"Too many tools?"* → don't stuff the catalog into context; semantic retrieval over tool descriptions, namespaces, curated toolsets.
- *"When multi-agent over tools?"* → only when the callee needs its own reasoning loop/context; otherwise it's just a tool.

## Pitfalls
- Calling MCP a "model feature" — it's a client/server *integration protocol*; the model still just emits tool calls.
- Ignoring trust: treating third-party MCP servers like first-party code.
- Conflating MCP and A2A directions (tool vs peer).

## Tips
Sound-bite: **"function calling is the instruction set; MCP is the USB port; A2A is the network."** Then N×M→N+M, discovery at runtime, and the security caveat — that's the staff-level 90-second answer.
