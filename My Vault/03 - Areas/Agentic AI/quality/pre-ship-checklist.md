---
title: Pre-Ship Checklist
pillar: quality
parent: ./README.md
type: checklist
---

# A. Pre-Ship Checklist

Cross-cuts all four pillars. Run before every release.

**Reasoning**
- [ ] System prompt is versioned + reviewable
- [ ] Skills registry exists where applicable, indexed by description
- [ ] Reflection only on measured quality gap

**Context & Memory**
- [ ] Working memory uses structured sections
- [ ] Retrieval is hybrid (vector + keyword) with source citation
- [ ] Compaction trigger is defined and tested
- [ ] Memory write policy is whitelisted, with TTLs

**Harness**
- [ ] Loop has hard limits (steps, tokens, wall time, loop detection)
- [ ] Tools have JSON Schema, error contracts, idempotency keys
- [ ] State is durable; turns are resumable
- [ ] Inter-agent messages are JSON, not prose
- [ ] Error path returns structured `partial_result`

**Governance**
- [ ] Safety: input scrub, tool allowlist, output validate
- [ ] Every tool call is traced; traces are replayable
- [ ] Eval suite covers happy + adversarial paths
- [ ] Cost / task measured and budgeted
- [ ] Failure modes have a user-visible message, not a stack trace
- [ ] Kill switch + human-in-the-loop for destructive ops
