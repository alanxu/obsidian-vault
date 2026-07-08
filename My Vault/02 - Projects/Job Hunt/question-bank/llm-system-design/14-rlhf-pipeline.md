---
title: Design an RLHF / Preference-Tuning Pipeline
slug: rlhf-pipeline
area: 4 — Training & Fine-tuning
companies: [Anthropic, OpenAI, Cohere, Scale]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[13-distributed-training-70b]]", "[[26-data-labeling-pipeline]]", "[[D0-areas-map]]"]
---

# Design an RLHF / Preference-Tuning Pipeline

> Align a model to human preference at scale: data collection → reward modeling → policy optimization. **Be able to draw it.** Know DPO as the modern simplification.

## Problem
"Design an RLHF pipeline at scale: data collection, annotation, reward modeling, PPO training." Variant: "how would you align a model to be more helpful/harmless?"

## Clarify first
- What behavior are we aligning (helpfulness, safety, format)? Preference data source (human, AI feedback)?
- Scale of preference data? PPO vs DPO? Eval for "aligned"?

## Architecture / the pipeline (draw this)
**SFT** (supervised fine-tune on demonstrations) → collect **preference pairs** (humans rank A vs B) → train a **reward model** (RM) on pairs → optimize the **policy** with **PPO** against the RM (+ KL penalty to stay near SFT). **DPO** collapses RM+RL into one preference-optimization step (no separate RM/PPO loop — simpler, stable, now common). **RLAIF** = AI feedback instead of human (Constitutional AI).

## Deep-dive — the components + their failure modes
- **Preference data** ([[26-data-labeling-pipeline]]): prompt sampling → human comparison → quality control (inter-annotator agreement). Data quality dominates.
- **Reward model:** trained on pairs to predict human preference; the policy optimizes *it*, so **reward hacking** (policy games RM weaknesses) is the central risk → KL penalty, RM ensembles, fresh data.
- **PPO vs DPO:** PPO = more control/exploration but unstable + needs RM + online generation; DPO = direct, stable, offline-ish, no separate RM. Default DPO unless you need PPO's control.
- **Eval:** win-rate vs baseline (human or judge), safety evals, capability regression check (alignment can degrade other skills).

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| PPO vs DPO | control/exploration vs simplicity/stability |
| Human vs AI feedback (RLAIF) | quality/cost vs scale |
| KL penalty strength | stay-near-SFT (safe) vs move-toward-reward (capable) |
| RM size/freshness | reward quality vs cost / hacking risk |

## Numbers
Preference data quality > quantity. KL coefficient tunes the helpfulness-vs-drift trade. Reward hacking shows as RM-score ↑ but human eval ↓ → always human/judge eval, not RM score.

## Failure modes
**Reward hacking** (optimize RM, not the goal) · alignment tax (capability regression) · noisy/biased preference labels · KL too low (mode collapse / gibberish) · eval-set contamination.

## Top follow-ups
- "PPO or DPO?" → DPO by default (simpler, stable, no RM); PPO when you need control/exploration.
- "Reward hacking?" → KL penalty, RM ensembles/freshness, human eval not RM score.
- "Scale the human data?" → active sampling, RLAIF/Constitutional AI for cheap feedback, QC via IAA.
- "RLVR / verifiable rewards?" → the 2025-26 shift: for math/code/agent tasks, replace the learned RM with **programmatic verifiers** (tests pass, answer checks) — no reward hacking of a proxy, enables o1/R1-style reasoning RL; the RM survives where 'good' isn't checkable (tone, helpfulness).
- "Infra difference PPO vs SFT?" → PPO is a *serving+training hybrid*: policy generates online (inference engine) while training (trainer ranks), plus RM + reference model resident — 3–4 models in memory, generation usually the throughput bottleneck; that's why DPO's offline-only loop is operationally attractive.
- "How much preference data?" → RMs train usably on ~50k–1M pairs; quality/diversity of *prompts* matters more than raw pair count; monitor RM accuracy on held-out pairs (~70–75% human-agreement ceiling — humans disagree with each other too).

## Related
[[13-distributed-training-70b]] (the training infra) · [[26-data-labeling-pipeline]] (preference data) · [[D0-areas-map]] Area 4.
