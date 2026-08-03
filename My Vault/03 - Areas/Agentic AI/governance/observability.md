---
title: Observability
pillar: governance
parent: ./README.md
section: "4.2"
---

# 4.2 Observability

You cannot improve what you cannot see.

- **Trace every turn.** Input → decisions → tool calls → outputs → final. Span per LLM call, per tool, per step.
- **Log the full prompt/response in dev; redact in prod.** PII, secrets, system prompt at minimum.
- **Structured logs, not strings.** `step=3 action=search query=… latency=… tokens=…`.
- **Run metadata.** session_id, user_id, model version, prompt version, tool versions. Reproducibility starts here.
- **Replays.** A trace should be replayable against a new model/prompt to A/B cheaply.
- **Dashboards.** Step count, success rate, cost per task, retry rate, loop rate, TTFT. Alert on regression, not absolute.

See also: [[../harness/state-orchestration|State & Orchestration]] — the event log is the substrate.
