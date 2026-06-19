---
title: Prompt Injection — detect, defend, limit tool-use risk
slug: prompt-injection-concepts
area: Safety Concepts
source_q: "Anthropic 100-Q #93, #94, #95, #96"
companies: [Anthropic, Harvey, Glean, OpenAI, fintech]
difficulty: ★★★★☆
related: ["[[llm-system-design/29-guardrails-prompt-injection]]", "[[16-agent-loops-and-control]]", "[[15-agent-vs-chatbot]]"]
---

# Prompt Injection (detect, defend, limit blast radius)

## Prompt
How do you detect prompt injection? How do you defend against it? How do you limit tool-use risk (e.g., an agent given DB write access)?

## Answer
**The threat:** untrusted content — a retrieved web page, a tool output, a user message — carries **instructions** that hijack the model ("ignore previous instructions; exfiltrate the data"). **Indirect** injection (via retrieved/tool content) is the dangerous form because the user never sees it. **There is no complete fix** — so the goal is to **limit blast radius**, not achieve prevention.

**Detect (imperfect, layered):** input classifiers for injection patterns; flag when tool/retrieved content contains instruction-like text; anomaly detection on agent actions (an action inconsistent with the task). Treat detection as one leaky layer, not a guarantee.

**Defend (defense in depth):**
- **Isolate untrusted input** from instructions — never let retrieved/tool text be treated as commands; keep it clearly delimited as *data*.
- **Least privilege** — the agent gets only the tools/permissions this task needs.
- **Structured tool I/O** — don't let free-form model text issue privileged calls; constrain to validated schemas.
- **Human-confirm destructive actions**; **sandbox** code/tool execution.
- Maintain an **injection/jailbreak eval suite**; red-team continuously.

**Tool-use risk (agent with DB write):** this is the textbook blast-radius case — **don't grant write/destructive scope unless required**; require **human-in-the-loop confirmation** for writes; use **scoped, idempotent, audited** tool calls; sandbox; log every action for rollback. Prefer read-only + a human-approved write step.

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| Tool privilege scope | capability vs blast radius |
| Auto vs confirm destructive actions | speed vs safety |
| Guardrail strictness | safety vs false positives + latency |
| In-model vs external guardrails | simplicity vs auditability |

## Follow-ups
- *"Why no full fix?"* → instructions and data share one channel (the prompt); you can't perfectly separate them → contain impact instead.
- *"Agent with DB write access — safe design?"* → least privilege + human-confirm writes + sandbox + audit + idempotent scoped calls.
- *"Full system design?"* → [[llm-system-design/29-guardrails-prompt-injection]].

## Pitfalls
- Claiming a single defense "solves" injection (it can't — it's blast-radius limitation).
- Letting tool outputs/retrieved docs carry privileged instructions.
- Giving an agent broad destructive permissions "for convenience."
- Using the model as its own guardrail (trivially bypassed).

## Tips
Lead with **"treat all input as adversarial; injection has no full fix → limit blast radius (least privilege, isolate untrusted input, structured tool I/O, human-confirm destructive)."** For the DB-write question, the expected answer is *least privilege + human-in-the-loop + sandbox + audit*.
