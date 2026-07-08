---
title: Pretraining vs Fine-tuning
slug: pretraining-vs-finetuning
area: LLM Fundamentals
source_q: "Anthropic 100-Q #6"
companies: [Anthropic, OpenAI, Cohere, Together, general AI-eng]
difficulty: ★★★☆☆
related: ["[[05-sft-vs-rlhf]]", "[[llm-system-design/13-distributed-training-70b]]", "[[D0-areas-map]]"]
---

# Pretraining vs Fine-tuning

## Prompt
What's the difference between pretraining and fine-tuning? When do you reach for each?

## Answer
- **Pretraining** — train from scratch on a huge, broad corpus with **self-supervised next-token prediction**. Learns general language/world knowledge and capabilities. Enormously expensive (thousands of GPUs, trillions of tokens). Done once by the model owner.
- **Fine-tuning** — take a pretrained model and continue training on a **smaller, targeted dataset** to adapt **behavior/style/format/domain**. Orders of magnitude cheaper; changes *how* the model responds, not its core knowledge.

The staff framing is the **adaptation ladder** — start at the cheapest rung that clears the bar:
**prompting/few-shot → RAG (add knowledge, no weight change) → PEFT/LoRA (cheap behavioral tweak) → full SFT (deep behavior change) → RLHF/preference tuning (align to preference).**

## Tradeoffs
| | Pretraining | Fine-tuning |
|---|---|---|
| Data | massive, broad, unlabeled | small, targeted |
| Cost | enormous | small–moderate |
| Changes | core capability/knowledge | behavior/style/domain |
| When | building a base model | adapting one you have |

## Follow-ups
- *"Fine-tune vs RAG for new knowledge?"* → **RAG** for fresh/changing/citable knowledge; fine-tuning for **style/format/latency** or baking in a fixed behavior. Default to prompting → RAG → tools **before** fine-tuning.
- *"LoRA vs full fine-tune?"* → LoRA for cheap, many-adapter, fast; full for maximal/deep change (→ [[llm-system-design/15-multi-tenant-finetuning-service]]).
- *"Catastrophic forgetting?"* → fine-tuning can erode general ability; mitigate with low LR, LoRA, mixing in general data.
- *"Continued/domain-adaptive pretraining?"* → the missing middle rung: same self-supervised objective, domain corpora (legal/code/medical) — adds domain **knowledge** (unlike SFT, which shapes behavior); replay general data to avoid forgetting.
- *"How much data to SFT?"* → quality ≫ quantity: hundreds–thousands of curated examples routinely beat 100k noisy ones (LIMA-style result); every example should teach an identifiable behavior.

## Pitfalls
- Reaching for fine-tuning to inject **facts** (that's RAG's job; fine-tuning teaches *behavior*, not reliable recall).
- Ignoring catastrophic forgetting / eval-regression after fine-tuning.
- Treating "fine-tuning" and "RLHF" as the same (RLHF is a *kind* of preference fine-tuning → [[05-sft-vs-rlhf]]).

## Tips
Answer with the **ladder** and "start at the cheapest rung that meets the bar" — that one line signals you won't reflexively fine-tune, which is the common junior mistake.
