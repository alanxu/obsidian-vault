---
title: Design an AV Simulation / Scenario-Generation System
slug: av-simulation-scenario-generation
area: 6 — Data, Features, Embeddings
companies: [Waabi, Waymo, Aurora]
difficulty: ★★★★☆
formats: [Live system design, ML-depth round]
related: ["[[18-llm-eval-harness]]", "[[16-pretraining-data-pipeline]]", "[[D0-areas-map]]"]
---

# Design an AV Simulation / Scenario-Generation System

> The Waabi/Waymo prompt: generate and run driving scenarios to **test/train autonomy at scale** (you can't validate a self-driving stack on real roads alone). Sim is the path to safety — coverage of rare/dangerous events is the whole point.

## Problem
"Design the simulation system to test the autonomy stack" / "generate diverse driving scenarios." Sub-problems: scenario generation (incl. rare edge cases), realistic sensor sim, large-scale parallel execution, metrics/regression.

## Clarify first
- Goal: regression testing, training-data generation, or both? Sensor fidelity needed (camera/Lidar)?
- Scenario sources (logged real drives, procedural, adversarial)? Scale (scenarios/day)? Metrics for "passed"?

## Architecture
**Scenario sources** (real-log replay + procedural generation + adversarial/learned generation) → **simulator** (world + agents + sensor models) → run the autonomy stack in the loop → **metrics** (collisions, disengagements, comfort, rule violations) → **regression dashboard** + scenario library. Massive parallel execution (cloud fleet).

## Deep-dive — coverage + realism + scale
- **Scenario coverage:** real drives are mostly boring → **generate rare/dangerous edge cases** (cut-ins, jaywalkers, occlusions); adversarial/learned generation to find failures; parameterize + fuzz scenarios.
- **Realism / sim-to-real gap:** the sim must be realistic enough that passing sim predicts real performance → calibrate sensor models (esp. Lidar), domain randomization; the gap is the central risk.
- **Scale:** run millions of scenarios in parallel (cloud) → petabyte log handling, deterministic replay, result aggregation.
- **Metrics/regression:** every stack change re-runs the scenario suite → catch safety regressions before the road (this is eval, AV-flavored).

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Real-log replay vs procedural vs learned | realism vs coverage of rare events |
| Sensor fidelity | realism (sim-to-real) vs compute cost |
| Scenario count | coverage vs compute |
| Determinism | reproducibility vs realism (stochastic agents) |

## Numbers
Real driving is mostly uneventful → must synthesize rare events for coverage. Sim-to-real gap is the validity threat. Millions of scenarios → massive parallel + petabyte logs.

## Failure modes
Sim-to-real gap (passes sim, fails road) · missing edge-case coverage · non-deterministic/unreproducible runs · unrealistic sensor models · compute cost blowup.

## Top follow-ups
- "Cover rare events?" → procedural + adversarial/learned scenario generation; fuzz parameters.
- "Sim-to-real gap?" → calibrate sensor models, domain randomization, validate sim predictivity vs road.
- "Scale?" → parallel cloud execution, deterministic replay, petabyte log pipeline.
- "Know the stack is safe to ship?" → regression scenario suite gate on every change.

## Related
[[18-llm-eval-harness]] (eval analogue) · [[16-pretraining-data-pipeline]] (data scale) · [[D0-areas-map]] Area 6.
