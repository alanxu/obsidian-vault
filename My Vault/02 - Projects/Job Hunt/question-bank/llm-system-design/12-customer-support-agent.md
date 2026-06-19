---
title: Design an AI Customer-Support / Workflow Agent
slug: customer-support-agent
area: 3 — Agentic Systems
companies: [Robinhood, Sierra, Decagon, Ada]
difficulty: ★★★☆☆
formats: [Live system design]
related: ["[[09-agent-platform]]", "[[01-rag-with-citations]]", "[[D0-areas-map]]"]
---

# Design an AI Customer-Support / Workflow Agent

> A production agent that resolves user requests end-to-end: understands intent, retrieves policy/account context (RAG), takes **real actions** via tools (refund, reset, escalate), with **guardrails + human handoff**. The applied-AI-product prompt (Sierra/Decagon/Ada; Robinhood agentic).

## Problem
"Design an agent that handles customer support: answer from knowledge base + take account actions + escalate when needed." Fintech variant (Robinhood): high-stakes actions, compliance.

## Clarify first
- Read-only answers vs **account-changing actions** (refunds, transfers)? Compliance/audit?
- Volume? Acceptable automation rate vs human escalation? Latency (chat)?
- Multi-tenant (per business)? Channels (chat/voice/email)?

## Architecture
User msg → **intent + retrieval** (policy + account context, RAG with ACL) → agent loop → **tools** (account API, refund, escalate) behind a **guardrail/approval layer** → response → **human handoff** on low confidence/high stakes. Trace + eval + feedback.

## Deep-dive — safe actions + escalation
- **Action guardrails:** classify action risk; auto-execute low-risk, **require confirmation/human approval** for high-risk (money movement) — especially fintech (Robinhood). Idempotent action calls.
- **Grounding + abstention:** answer only from retrieved policy; abstain/escalate when unsure (don't invent policy).
- **Escalation policy:** confidence threshold + sensitive-topic detection → route to human with full context.
- **Eval:** task resolution rate, escalation precision, CSAT, and **zero unauthorized actions** (a hard gate).

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Automation rate | cost savings vs error/harm risk |
| Auto vs confirm actions | speed vs safety (set by stakes) |
| Escalation threshold | human cost vs bad-resolution risk |
| Single bot vs per-intent | simplicity vs specialization |

## Numbers
Asymmetric costs: a wrong refund / wrong account action ≫ an unresolved ticket → conservative thresholds on actions. Resolution rate × escalation cost is the business.

## Failure modes
Unauthorized/incorrect account action · hallucinated policy · prompt injection from user input · over-escalation (no value) or under-escalation (harm) · cross-customer data leak.

## Top follow-ups
- "Let it take real actions safely?" → risk-tiered tools, confirm/human-approve high-stakes, idempotent, audited.
- "When to escalate?" → confidence + sensitive-topic detection → human with context.
- "Stop it inventing policy?" → RAG-grounded + abstain; never answer un-retrieved.
- "Fintech compliance?" → audit every action, human-in-loop for money movement, ACL on account data.

## Related
[[09-agent-platform]] · [[01-rag-with-citations]] · [[D0-areas-map]] Areas 3 + 7.
