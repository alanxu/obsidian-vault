---
title: Safety & Guardrails
pillar: governance
parent: ./README.md
section: "4.1"
---

# 4.1 Safety & Guardrails

Defense in depth. No single layer is enough.

- **Input.** PII detection, prompt-injection scrubber, length cap, jailbreak classifier. Treat untrusted content (web results, file contents, user uploads) as data, never as instructions.
- **System prompt boundary.** Hard separator; reject any user message that tries to redefine the role.
- **Tool policy.** Allowlist by default. Destructive ops need explicit confirmation, scoped tokens, or human-in-the-loop.
- **Output.** Schema-validate, content-filter, action-confirm (e.g. "this will email 47 people — proceed?").
- **Sandbox.** Code execution runs in a fresh container with no network, no host FS. Time-bound. Resource-bound.
- **Audit.** Every action against a side-effecting tool gets logged with intent, args, and result. Retention policy.

## 4.1.1 Prompt Injection

The #1 production failure mode for agents that touch untrusted content. Direct injection is a user message trying to override instructions. **Indirect injection** — where a web page, email, or document contains adversarial text the agent later ingests — is the more dangerous and more common variant.

**Core patterns:**

- **Data vs. instructions separation.** Wrap untrusted content in explicit markers (`<untrusted>...</untrusted>`, fenced blocks, distinct role) and tell the model to never treat content inside as instructions. Belt + suspenders: also strip control-like patterns (e.g. "ignore previous", "system:", "assistant:") from untrusted sources before they enter the context.
- **Instruction hierarchy.** Make explicit which layer wins: system > developer > user > tool output. Most providers support this natively; lean on it.
- **Tool-result filtering.** The most common indirect-injection sink. After every tool call, classify the result as data, not instructions. Strip or escape anything that looks like control tokens.
- **Capability restriction on injected paths.** A tool that fetches untrusted content shouldn't be allowed to call side-effecting tools in the same turn. Compartmentalize.

**Defense in depth — none of these alone is enough:**

1. Input classifier (cheap model flags injection attempts in user input)
2. Structural markers around untrusted data
3. Output validator (does the response try to do something the user didn't ask for?)
4. Tool policy + action confirmations for side effects

**Red-team your own agent.** Build a fixture set of indirect-injection attempts: poisoned docs, malicious emails, adversarial web pages. Run them in CI. Track the bypass rate over time like a security metric.

**When to escalate to a human:** any tool call with destructive or external side effects (email, file write, code exec) where the trigger came from a tool result, not from the user's direct request. Default: confirm.

See also: [[../harness/tools|Tools]] for tool contracts and the destructive-tool confirmation pattern.
