---
title: Latency
pillar: governance
parent: ./README.md
section: "4.4"
---

# 4.4 Latency

- **TTFT ≪ total latency.** Stream. The user perceives the first token, not the last.
- **Per-phase budgets.** Plan: 500ms. Tool: 2s. Synthesis: 3s. Tell the user when you'll exceed.
- **Speculative decoding / smaller draft** for long outputs.
- **Pre-warm** the model and tool connections. Cold starts are death.
