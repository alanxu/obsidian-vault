---
title: Design an MCP / Tool-Integration Platform
slug: mcp-tool-platform
area: 3 — Agentic Systems (+ Area 7 safety)
companies: [Anthropic, OpenAI, Anysphere, Glean, Robinhood, "any agent-platform team"]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[09-agent-platform]]", "[[29-guardrails-prompt-injection]]", "[[fundamentals/23-mcp-a2a]]", "[[practical-coding/30-function-calling-tool-handler]]"]
added: 2026-07-08 (audit fill — MCP/A2A now standard in senior loops)
evidence: "GUIDE-LEVEL: 'prompt caching and MCP/A2A are now standard in senior-level loops' per one 2026 guide (letsdatascience 50 AI-eng questions); MCP as agent-stack topic corroborated across 2026 agent guides. The full 'design the tool platform' framing is my synthesis; company list = inference from agent-platform investment."
---

# Design an MCP / Tool-Integration Platform

> "Let any team expose tools to our agents; let agents at 1000s of tools stay reliable and safe." **Open with the shift:** function calling = model+tools compiled into *one* app; **MCP = tools as independently-owned network services** with discovery, auth, and versioning — so this is an **API-platform design** (registry, gateway, authZ) where the *client is stochastic*.

## Problem
"Design the tool platform for our org's agents: teams register tools (MCP servers), agents discover and call them, security reviews sleep at night." Variants: third-party tool marketplace, cross-org A2A, Claude-style connector ecosystem.

## Clarify first
- Internal-only tools vs third-party marketplace (trust boundary changes everything)?
- Tool risk classes — read-only lookups vs world-changing (payments, deletes)?
- Whose credentials do tools run with — the agent's service identity or **the end-user's** (on-behalf-of)?
- Scale: # tools, # agents, calls/day; latency budget per call?

## Architecture
**Registry/control plane:** teams register MCP servers → schema validation, semantic-versioned specs, **risk classification** (read / write / destructive), ownership + SLA metadata, staging→prod promotion with review for high-risk classes. **Gateway/data plane (every call flows through):** authN (agent identity) + **authZ (agent × tool × end-user-on-behalf-of scopes, OAuth token exchange)** → rate limits + quotas per (agent, tool) → schema-validate args → dispatch to MCP server (timeout, retry-if-idempotent, circuit breaker) → **response filtering** (size caps, PII scrubbing, injection heuristics) → trace + cost meter. **Discovery for agents:** at 1000s of tools you can't put all specs in context → **tool retrieval**: agent's task → search registry (semantic over descriptions) → inject top-k specs; namespaces + curated toolsets per agent.

## Deep-dive — security model (where staff signal lives)
- **Least privilege, per-call:** the agent gets *scoped, short-lived* credentials per tool call (token exchange), never a god-token. On-behalf-of: end-user's grants bound the agent — agent can't read docs the user can't ([[02-enterprise-search-acl]] logic at the tool layer).
- **The lethal trifecta** (private-data access + untrusted content + exfiltration channel): platform's job is ensuring no single agent context holds all three — policy engine can express "if agent has read private data this session, block tools that post externally."
- **Tool output is untrusted input:** a compromised/malicious MCP server can inject instructions via results → response filtering, provenance tagging (model told which text came from which tool), and destructive-action confirmation are gateway features, not agent courtesy ([[29-guardrails-prompt-injection]]).
- **Versioning for a stochastic client:** semver on schemas; breaking change = new version, old kept alive; **canary by agent cohort** — a "compatible" description rewrite can still shift model behavior, so description changes are also gated by agent-eval runs.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Central gateway vs direct agent→server | policy chokepoint + observability vs latency hop + blast-radius-of-gateway |
| All specs in context vs tool retrieval | reliable selection (small N) vs scales to 1000s (retrieval can miss) |
| Strict schema gate vs permissive | fewer runtime failures vs registration friction |
| Sync calls vs async job tools | simple loop vs long-running work (both; async = job-id + poll tool) |
| Marketplace open vs reviewed | ecosystem growth vs supply-chain risk (review + sandbox + scopes) |

## Numbers
Gateway overhead target <20ms p99 (vs tool latencies 50ms–30s) · tool-retrieval: top 5–20 specs ≈ 1–4K tokens vs 100K+ for a full catalog · spec quality matters: description text drives model selection accuracy — treat descriptions as prompts, eval them · call mix typically 90% read / 10% write → optimize read path, gate write path.

## Eval
Tool-selection accuracy (given task, did agent pick the right tool? — eval set per toolset) · call success rate by tool (schema errors vs server errors vs timeout) · end-task success before/after a tool's spec change (canary metric) · security: scope violations blocked, trifecta-policy triggers · p99 overhead; per-tool SLA compliance dashboards to owners.

## Failure modes
Tool description drift silently degrading agent selection · schema-valid but semantically-wrong calls (units, ID formats → examples in specs) · cascading retries: agent-level retry × gateway retry × server retry = storm (retry only at gateway, budget-capped) · one slow tool stalling agent loops (timeouts + async escape hatch) · malicious server in marketplace (review, sandbox, scoped creds, egress filtering) · orphaned tools with no owner (registry requires ownership + expiry).

## Top follow-ups
- "MCP vs plain function calling?" → decoupled ownership/discovery/auth/versioning; N×M → N+M integration ([[fundamentals/23-mcp-a2a]]).
- "1000s of tools — context?" → tool retrieval + namespaces + curated toolsets; eval selection accuracy.
- "Stop an agent leaking data through a tool?" → scoped per-call creds + trifecta policy + egress filtering on responses/requests.
- "Tool wants 10 minutes?" → async pattern: submit → job-id → status tool; agent loop continues or parks.
- "A2A / agent-to-agent?" → same gateway discipline, but the 'tool' is another stochastic agent → contract = task+artifact schema, plus budget propagation (caller's cost/step budget bounds callee).

## Related
[[09-agent-platform]] (the runtime consuming this) · [[29-guardrails-prompt-injection]] (threat model) · [[practical-coding/30-function-calling-tool-handler]] (code the dispatch) · [[fundamentals/23-mcp-a2a]] (concept card).
