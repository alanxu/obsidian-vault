---
title: SFT vs RLHF (and why RLHF improves UX)
slug: sft-vs-rlhf
area: LLM Fundamentals
source_q: "Anthropic 100-Q #7, #8"
companies: [Anthropic, OpenAI, Cohere, Scale]
difficulty: ★★★★☆
related: ["[[06-dpo]]", "[[04-pretraining-vs-finetuning]]", "[[llm-system-design/14-rlhf-pipeline]]"]
---

# SFT vs RLHF (and why RLHF improves UX)

## Prompt
What's the difference between SFT and RLHF? Why does RLHF improve the user experience?

## Answer
- **SFT (Supervised Fine-Tuning)** — train on **(prompt → ideal response)** demonstrations. The model imitates good answers. Teaches format/instruction-following, but it's limited to the demonstrations you can write, and there's **no signal about what's *better* vs *worse*** among acceptable answers.
- **RLHF (RL from Human Feedback)** — optimize against **human preference**: collect **comparisons** (response A vs B), train a **reward model (RM)** to predict preference, then optimize the policy (PPO) to maximize RM reward with a KL penalty to stay near SFT.

**Why RLHF improves UX:** preferences capture **subtle, hard-to-demonstrate qualities** — helpfulness, tone, harmlessness, "don't be evasive," calibrated confidence — that are easy to *rank* but hard to *write* as gold answers. It also lets the model learn from **its own samples** (which to prefer), going beyond imitation. Result: more helpful, safer, better-aligned responses than SFT alone.

## Tradeoffs
| | SFT | RLHF |
|---|---|---|
| Signal | imitate demonstrations | optimize ranked preference |
| Captures | format, instruction-following | nuanced helpful/harmless/tone |
| Cost/complexity | low | high (RM + RL loop, unstable) |
| Risk | limited by demos | **reward hacking**, mode collapse |

## Follow-ups
- *"DPO vs PPO?"* → DPO collapses RM+RL into one preference-optimization step — simpler, stabler, no separate RM (→ [[06-dpo]]).
- *"Reward hacking?"* → policy games RM weaknesses (RM-score ↑ but human eval ↓) → KL penalty, RM ensembles/freshness, **evaluate with humans/judge, not RM score**.
- *"RLAIF / Constitutional AI?"* → use AI feedback against a written constitution instead of human labels → cheaper, scalable.
- *"How do you know RLHF worked?"* → **not** RM score (hackable): held-out human/judge **win rate vs the SFT baseline** + capability-regression evals (RLHF can tax reasoning/calibration — the "alignment tax").
- *"Why not RL straight from the base model?"* → SFT first puts the policy in-distribution (instruction-following); RL from base is sample-inefficient and unstable — the stages are complementary, not alternatives.
- The full pipeline / infra → [[llm-system-design/14-rlhf-pipeline]].

## Pitfalls
- Saying RLHF "makes the model smarter" — it aligns **behavior/preference**, not raw capability.
- Forgetting the **KL penalty** (without it, the policy drifts to gibberish that games the RM).
- Reporting RM score as success (reward hacking makes that misleading).

## Tips
Two beats: **"SFT imitates demonstrations; RLHF optimizes ranked human preference, which captures the hard-to-write qualities (helpful/harmless/tone)."** Then drop DPO + reward-hacking to show depth.
