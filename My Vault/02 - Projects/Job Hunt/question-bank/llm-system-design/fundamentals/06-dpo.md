---
title: DPO (Direct Preference Optimization)
slug: dpo
area: LLM Fundamentals
source_q: "Anthropic 100-Q #9"
companies: [Anthropic, OpenAI, Cohere]
difficulty: ★★★★☆
related: ["[[05-sft-vs-rlhf]]", "[[llm-system-design/14-rlhf-pipeline]]"]
---

# DPO (Direct Preference Optimization)

## Prompt
What is DPO, and how does it differ from PPO-based RLHF?

## Answer
**DPO optimizes a model directly on preference pairs without training a separate reward model or running RL.** Classic RLHF is two stages: (1) train a reward model on comparisons, (2) use PPO (online RL) to maximize that reward. DPO shows that, under the standard RLHF objective, you can **skip the RM and the RL loop** and instead apply a simple **classification-style loss on (preferred, rejected) pairs** that increases the relative log-probability of the preferred response (relative to a frozen reference policy, which plays the role of the KL constraint).

**Net:** same goal (align to human preference), but **simpler, more stable, cheaper** — no reward model, no online sampling, no PPO tuning. It's become a common default; PPO is kept when you want online exploration / finer control.

## Tradeoffs
| | PPO-RLHF | DPO |
|---|---|---|
| Pieces | RM + online RL | one offline loss |
| Stability | finicky (RL) | more stable |
| Compute | high (online gen) | lower (offline) |
| Control/exploration | more | less |

## Follow-ups
- *"Where's the KL constraint in DPO?"* → implicit, via the **reference model** term (keeps the policy near the SFT model).
- *"When still use PPO?"* → when you need online exploration, an explicit reward you can shape, or iterated/online preference collection.
- *"DPO variants?"* → IPO, KTO, ORPO (different loss formulations / no-reference variants).

## Pitfalls
- Saying DPO "has no reward model so it ignores preferences" — it **uses** the preference pairs directly; it just doesn't train a *separate* RM.
- Forgetting the reference model (drop it and the policy degenerates).

## Tips
One line: **"DPO turns RLHF into a single offline classification loss on preferred-vs-rejected pairs — no reward model, no PPO — so it's simpler and more stable."** Mentioning the implicit-KL-via-reference-model detail signals you actually understand it.
