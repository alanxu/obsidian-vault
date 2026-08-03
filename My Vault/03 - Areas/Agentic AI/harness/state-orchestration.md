---
title: State & Orchestration
pillar: harness
parent: ./README.md
section: "3.3"
---

# 3.3 State & Orchestration

Long-running agents die in the gap between requests. Build for resumability.

- **Durable state.** Persist after every step. Next turn picks up exactly where the last left off.
- **Idempotent step IDs.** Same step + same input → skip. Lets you retry safely.
- **Checkpointing.** Snapshot state every N steps or T seconds. Recovery is replay, not restart.
- **Event log.** Every decision, tool call, and result is a structured event. Append-only. This is your observability and replay substrate.
- **Out-of-band signals.** User "stop" / "edit" / new input must interrupt the loop cleanly. Cancel in-flight work, don't orphan it.
