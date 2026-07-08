---
title: Design Content Moderation at Scale (10B msgs/day)
slug: content-moderation-at-scale
area: 7 — Safety, Guardrails & Governance
companies: [Anthropic, OpenAI, Meta, TikTok]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[29-guardrails-prompt-injection]]", "[[18-llm-eval-harness]]", "[[D0-areas-map]]"]
---

# Design Content Moderation at Scale

> The Anthropic prompt: moderate 10B+ messages/day. **The staff framing: tiered cheap→expensive→human, with asymmetric thresholds** (missing CSAM ≫ a false flag) — cost and harm are both first-class.

## Problem
"Design a real-time content moderation system across 10B+ messages/day." Detect/handle policy violations (toxicity, CSAM, violence, spam) at scale, low latency, high stakes.

## Clarify first
- Categories + their harm asymmetry (CSAM ≫ mild toxicity)? Latency (inline-block vs async)?
- Volume/QPS? Languages/modalities (text/image)? Appeals/human review capacity? Regulatory?

## Architecture (tiered funnel)
Content → **cheap fast classifier on everything** (filters the obvious) → **escalate uncertain cases to a bigger model** → **human review queue** for the hardest/highest-stakes → action (allow/flag/block/escalate) + appeals + audit. Feedback → retrain.

## Deep-dive — tiering, thresholds, asymmetry
- **Tiered for cost:** can't run a frontier model on 10B msgs → cheap classifier catches most; only uncertain/risky escalate (cost-optimal).
- **Asymmetric thresholds by harm:** set operating points per category from **harm cost**, not F1 — for CSAM, maximize recall (false positives acceptable); for mild toxicity, protect precision (avoid over-blocking).
- **Inline vs async:** block-before-harm (inline, latency-critical) for severe categories; async review where latency allows.
- **Human-in-the-loop:** review queue for ambiguous/high-stakes; capacity planning; reviewer wellbeing for graphic content.
- **Adversarial:** users evade (leetspeak, obfuscation) → robust features, continual retraining, multi-modal.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Tier thresholds | cost (cheap-first) vs latency of escalation |
| Block vs flag vs review | safety vs utility/over-blocking |
| Inline vs async | latency vs catching-before-harm |
| Precision vs recall (per category) | over-blocking vs missed harm (set by harm cost) |

## Numbers
10B/day → tiered (cheap model on all, expensive on few). Asymmetric costs drive per-category thresholds. Human review is the scarce, expensive tier → escalate sparingly.

## Failure modes
Missing high-harm content (recall failure) · over-blocking (precision failure / safety theater) · adversarial evasion · human-review overload · latency on inline path · bias across languages/groups.

## Top follow-ups
- "10B msgs/day?" → tiered cheap→expensive→human; escalate only uncertain.
- "Thresholds?" → asymmetric per category from harm cost (CSAM recall ≫ precision), not F1.
- "Evasion?" → robust/multi-modal features + continual retraining.
- "Latency?" → inline for severe categories, async review elsewhere.
- "Moderating LLM *outputs* vs user content — what changes?" → you're policing your own model: streaming means checking partial text (classify incrementally, cut the stream on violation), and the model can be *induced* to violate (jailbreaks) → moderation + jailbreak-resistance are coupled systems, tie to [[29-guardrails-prompt-injection]].
- "Cross-language fairness?" → classifier quality is wildly uneven across languages → per-language eval slices, native-labeled data for major locales, and honest degraded-tier handling (escalate more where the cheap model is weak) — aggregate metrics hide that Tagalog recall is 30 points lower.
- "Policy changes weekly — how does the system keep up?" → policy-as-versioned-artifact: policy text drives labeling guidelines + few-shot prompts + eval sets together; on change, re-label a delta set, re-gate, re-ship — moderation is a *policy compiler*, not a static classifier.
- "Reviewer wellbeing as a design constraint?" → blur/limit graphic exposure, rotation caps, model-first triage of the worst content — mention it unprompted; it's a real ops cost and an values signal at Anthropic.

## Related
[[29-guardrails-prompt-injection]] · [[18-llm-eval-harness]] · [[D0-areas-map]] Areas 7 + 5.
