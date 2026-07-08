---
title: Structured Outputs & Constrained Decoding
slug: structured-outputs
area: Production & Serving Concepts
companies: [OpenAI, Anthropic, Cohere, "any applied-AI team"]
difficulty: ★★★☆☆
related: ["[[llm-system-design/36-structured-output-extraction]]", "[[practical-coding/30-function-calling-tool-handler]]", "[[practical-coding/37-streaming-json-parser]]"]
added: 2026-07-08 (audit fill — no prior coverage in bank)
evidence: "INFERRED: added for coverage (topic appears in AI-eng question cheat-sheets and is ubiquitous in applied-AI work), but I did not find a candidate report or company-specific guide naming it. Confidence rests on it underpinning verified topics (tool calling, extraction)."
---

# Structured Outputs & Constrained Decoding

## Prompt
How do you get reliable JSON out of an LLM? How does constrained decoding work, and what are the costs?

## Answer
Four levels of rigor:
1. **Prompting** ("respond in JSON", few-shots) — ~90–99% valid; fails at scale.
2. **Parse-and-repair** — extract the JSON block, fix trailing commas, retry with the error message on failure. Robust enough for many apps; costs retries.
3. **Function-calling / JSON mode** — provider fine-tuned the model + biases decoding toward valid JSON; no schema guarantee (fields can be missing/wrong type).
4. **Constrained (grammar-guided) decoding** — compile the JSON schema to a grammar/FSM; at each decode step **mask logits** so only tokens that keep the output grammatically valid can be sampled. Output is valid *by construction* (OpenAI Structured Outputs, `outlines`, `guidance`, llama.cpp grammars).

**Key mechanism detail:** the mask applies at the *token* level — the FSM must handle tokens spanning JSON structure (`","` or `"}\n` as one token), which is why implementations precompile schema→token-level automaton (that compile step is the latency cost on first use).

**The subtle cost:** constraints guarantee *shape*, not *quality*. Forcing structure can slightly degrade content (the model can't "think out loud" before committing) — mitigations: let it reason first then emit (CoT field / reasoning outside the schema), keep schemas flat, put constrained generation *after* free-form reasoning.

## Tradeoffs
| Choice | Gains | Costs |
|---|---|---|
| Constrained decoding | 100% parseable, no retries | provider/library lock-in; schema-compile latency; slight quality tax |
| Parse-and-repair | provider-agnostic | retry cost + tail latency; residual failure rate |
| Flat schema vs deep nesting | accuracy, easier masking | may need post-assembly |
| Enum/regex-constrained fields | eliminates format hallucination | over-constraining hides model uncertainty (it *must* pick something) |

## Follow-ups
- *"Valid JSON but wrong values?"* → orthogonal problem: validation layer (types, checksums, cross-field), confidence + span grounding → [[llm-system-design/36-structured-output-extraction]].
- *"Streaming + structure?"* → clients want partial UI updates → incremental/partial-JSON parsing → [[practical-coding/37-streaming-json-parser]].
- *"Why can forcing JSON hurt quality?"* → decoding path diverges from the model's natural distribution; no room for deliberation → reason-then-extract pattern.
- *"Union types / optional fields?"* → grammar handles it, but each choice point is a place the model can commit early and wrongly — prefer explicit discriminator fields.

## Pitfalls
- Trusting "JSON mode" to enforce a *schema* — it only enforces JSON-ness.
- Validating shape but not semantics (valid ≠ correct).
- Deep nested schemas → worse accuracy and hard-to-debug failures.
- Forgetting the model can emit valid-but-empty (`""`, `[]`) under constraint pressure — require + validate content.

## Tips
Ladder answer: **prompt → repair → JSON mode → grammar-constrained**, name the logit-masking mechanism, then land the staff point: **"structure is guaranteed; correctness still needs validation + eval."**
