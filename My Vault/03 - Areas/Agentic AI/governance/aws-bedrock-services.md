---
title: AWS Agentic AI Services Reference
pillar: governance
parent: ./README.md
type: reference
---

# AWS Agentic AI Services Reference

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
