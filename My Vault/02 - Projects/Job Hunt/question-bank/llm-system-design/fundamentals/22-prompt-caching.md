---
title: Prompt / Prefix Caching
slug: prompt-caching
area: Production & Serving Concepts
companies: [Anthropic, OpenAI, Anysphere, "any high-volume LLM product"]
difficulty: ★★★☆☆
related: ["[[03-kv-cache]]", "[[llm-system-design/35-semantic-caching]]", "[[llm-system-design/06-llm-inference-serving-platform]]"]
added: 2026-07-08 (audit fill — standard 2026 senior topic)
evidence: "GUIDE-LEVEL: named a now-standard senior-loop topic in a 2026 guide (letsdatascience). Mechanism facts (pricing ~10× discount, TTLs) from provider docs — stable. Companies = inference (any high-volume LLM shop)."
---

# Prompt / Prefix Caching

## Prompt
What is prompt caching? How does it differ from semantic caching, and how do you structure prompts to exploit it?

## Answer
Prompt (prefix) caching **reuses the KV cache** (→ [[03-kv-cache]]) for a prompt prefix that's byte-identical across requests. Prefill normally recomputes attention keys/values for every input token; if the first N tokens match a cached prefix, the server skips their prefill entirely — cutting **TTFT and cost** (cached input tokens are ~10× cheaper on Anthropic/OpenAI pricing).

**What it is not:** it doesn't skip the call or reuse *answers* — the model still decodes fresh output. Answer-reuse by query similarity is **semantic caching** ([[llm-system-design/35-semantic-caching]]) — app layer, fuzzy, risky; prompt caching is infra layer, exact-prefix, safe.

**Exploiting it — order the prompt stable→volatile:** system prompt → tool specs → few-shots → document/context → conversation history → user turn. Any changed byte invalidates everything *after* it, so never put timestamps, request IDs, or user names early. Multi-turn chat naturally extends the prefix (history is append-only). Agents benefit hugely: same system+tools prefix on every loop step ⇒ a 10-step agent pays full prefill ~once.

## Tradeoffs
| Choice | Gains | Costs |
|---|---|---|
| Cache long shared prefix | 10× cheaper input, TTFT ↓ | cache-write premium (~1.25×) — only pays off if reused |
| Stable prompt ordering | max hits | discipline; can conflict with "most important last" heuristics |
| Explicit breakpoints (Anthropic) vs automatic (OpenAI) | control | provider-specific code |

## Follow-ups
- *"Why exact-match only?"* → KV entries are position-dependent tensor state; one different token changes all subsequent K/V.
- *"TTL/eviction?"* → provider caches are short-lived (~5min–1hr, usage-refreshed); design for hit-within-session, not cross-day.
- *"Security?"* → cache is per-tenant/API-key scoped by providers; timing side-channels are why you never share cross-tenant.
- *"How does it interact with RAG?"* → retrieved chunks differ per query → put them *after* the stable prefix; the system+instructions still hit.

## Pitfalls
- Dynamic content (date, user ID) injected at the top of the system prompt — silently kills every hit.
- Assuming it caches *responses* — it only cheapens prefill.
- Paying the cache-write premium on one-shot prompts that never recur.

## Tips
One-liner: **"semantic caching skips the call; prompt caching cheapens the call."** Then: order stable→volatile, agents/multi-turn are the big winners, ~10× input-token discount. That covers 90% of probes.
