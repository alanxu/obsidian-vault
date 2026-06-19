---
title: Agent vs Chatbot (and why tool calling matters)
slug: agent-vs-chatbot
area: Agent Concepts
source_q: "Anthropic 100-Q #31, #32"
companies: [Anthropic, OpenAI, Anysphere, Cognition, Robinhood]
difficulty: ★★★☆☆
related: ["[[16-agent-loops-and-control]]", "[[17-react]]", "[[llm-system-design/09-agent-platform]]"]
---

# Agent vs Chatbot (+ why tool calling matters)

## Prompt
What's the difference between an agent and a chatbot? Why is tool calling important?

## Answer
A **chatbot** is a single-turn (or multi-turn) **text→text** function: prompt in, response out, fixed pipeline. An **agent** wraps the LLM in a **control loop** where the model **decides actions, calls tools, observes results, and iterates** toward a goal — a dynamic *sense→plan→act* cycle rather than one shot. The LLM is the *planner*; the system around it provides tools, memory, guardrails, and a stopping condition.

**Why tool calling is the unlock:** an LLM alone is frozen (knowledge cutoff), can't act, and can't verify. **Tools** let it *retrieve* fresh data, *act* on the world (run code, query a DB, send an email), and *ground/verify* its outputs. Without tools an agent is just a chatbot narrating; tools are what make it *do* things. The model emits a structured **tool call** (name + args), the system executes it, and the result is fed back as an observation.

## Tradeoffs
| | Chatbot | Agent |
|---|---|---|
| Control flow | fixed pipeline | dynamic loop |
| Can act/verify | no | yes (tools) |
| Reliability | predictable | compounding-error risk |
| Cost/latency | one call | many calls |

## Follow-ups
- *"When NOT to use an agent?"* → if a fixed pipeline (retrieve→generate) solves it, do that — agents add cost + failure modes. Use agents when the path is **dynamic/unknown**.
- *"How does the model call a tool?"* → typed tool schemas (function calling / **MCP**); validate args, dispatch, feed back the observation (→ [[practical-coding/30-function-calling-tool-handler]]).
- *"Biggest agent challenge?"* → **reliability**, not capability (compounding error → [[16-agent-loops-and-control]]).

## Pitfalls
- Calling any LLM-with-RAG an "agent" — RAG is a fixed pipeline; an agent *decides* when/which to retrieve.
- Over-agentifying a problem a simple chain solves (cost + brittleness).

## Tips
Define an agent as **"an LLM in a loop that decides actions and uses tools,"** then say tools give it *fresh data, the ability to act, and a way to verify*. Adding "default to a fixed pipeline unless the path is dynamic" is the right-sizing signal.
