---
title: Harness
pillar: harness
parent: ../Production Agent Handbook.md
---

# Harness

The runtime that wraps the model. Engineering substrate, not LLM magic.

## Sections

- [[core-loop|3.1 The Core Loop]] — state machine, hard limits in code not prompts
- [[tools|3.2 Tools]] — API surface, JSON Schema, error contracts
- [[state-orchestration|3.3 State & Orchestration]] — durability, checkpoints, event log
- [[multi-agent|3.4 Multi-Agent (Implementation)]] — ownership, message schemas, failure isolation
- [[errors-recovery|3.5 Errors & Recovery]] — retryable vs not, loops, partial completion
- [[framework-evaluation|3.6 Framework Selection]] — LangGraph vs. Claude Agent SDK, when to use which

## Reference

- [[minimax-api|MiniMax Model API Reference]] — wire-level spec for the M-series (Anthropic & OpenAI compat).
