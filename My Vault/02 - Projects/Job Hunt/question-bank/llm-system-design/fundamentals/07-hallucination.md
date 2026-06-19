---
title: Why Models Hallucinate (and how to mitigate)
slug: hallucination
area: LLM Fundamentals
source_q: "Anthropic 100-Q #10"
companies: [Anthropic, OpenAI, Cohere, Harvey, Perplexity]
difficulty: ★★★★☆
related: ["[[llm-system-design/01-rag-with-citations]]", "[[14-rag-evaluation]]", "[[D0-areas-map]]"]
---

# Why Models Hallucinate

## Prompt
Why do LLMs hallucinate? How do you reduce hallucination in production?

## Answer
**Root cause:** an LLM is a probabilistic next-token model trained to produce **plausible, fluent** text — not to be **truthful**. It has no built-in notion of "I don't know"; when the prompt asks something outside or under-represented in its parametric knowledge, it still samples the most likely continuation, which can be confidently wrong. Contributors: training objective rewards fluency over factuality; gaps/staleness in training data; **RLHF can even encourage confident-sounding answers** (raters prefer them); decoding randomness; and for RAG systems, **retrieval misses** (the right evidence isn't in context, so the model fills the gap).

**Mitigations (layered — there's no single fix):**
1. **Ground with retrieval (RAG)** and instruct "answer only from the sources" (→ [[llm-system-design/01-rag-with-citations]]). *Most production hallucinations are retrieval failures.*
2. **Citations + verification** — require a source per claim, then **verify entailment** (NLI/judge) and drop/flag unsupported claims.
3. **Allow abstention** — "I don't know" beats a confident wrong answer, especially high-stakes (Harvey/legal).
4. **Decoding/prompting** — lower temperature, constrained/structured output, chain-of-thought for reasoning.
5. **Eval + monitoring** — track **faithfulness** (your hallucination KPI, inverted) offline + on a judged prod sample.

## Tradeoffs
| Lever | Gains | Costs |
|---|---|---|
| RAG grounding | factuality, citability | retrieval can still miss |
| Verification pass | catches unsupported claims | latency + cost |
| Abstention | safety | lower coverage/utility |
| Low temperature | fewer wild outputs | less diversity |

## Follow-ups
- *"Detect hallucination?"* → claim-vs-source **entailment** (NLI/LLM-judge); flag uncited claims; track faithfulness; user feedback.
- *"Retrieval miss vs generation error?"* → decompose: Recall@k isolates retrieval, faithfulness isolates generation; fix the layer the metric indicts.
- *"High-stakes domain?"* → block unverified claims, mandatory abstention, span-level audit trail (→ [[llm-system-design/04-legal-document-qa]]).

## Pitfalls
- Claiming a single fix ("just use RAG") — RAG with a retrieval miss still hallucinates. It's layered.
- Confusing fluency with truthfulness in the explanation.
- Ignoring that RLHF can *increase* confident hallucination.

## Tips
Open with **"the model optimizes plausibility, not truth, and has no innate 'I don't know.'"** Then give the **layered** mitigation (ground → cite+verify → abstain → eval) — naming "most hallucinations are retrieval failures" is the staff insight.
