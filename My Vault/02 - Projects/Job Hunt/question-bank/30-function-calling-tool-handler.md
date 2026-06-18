---
title: Function-Calling / Tool-Use Handler
slug: function-calling-tool-handler
type: agentic
leetcode: null
companies: [OpenAI, Anthropic, Anysphere, Cognition, general AI-eng]
difficulty: ★★★☆☆
frequency: rising
formats: [Live, Take-home]
levels: 1
time-box: live 30–45 min
tags: [agent, tool-calling, schema-validation, parsing, registry]
related: ["[[16-minimal-agent-loop]]", "[[practical-oo-coding-deep-guide]]"]
---

# Function-Calling / Tool-Use Handler

The **single-step dispatch** the agent loop calls: take a model's tool call, validate it, run the tool, return a structured result. Distinct from [[16-minimal-agent-loop]] (the loop) — this is the registry + validation + dispatch component.

## Problem
The model emits a tool call (JSON: `{"name": ..., "arguments": {...}}`). Implement a `ToolHandler`: a **registry** of tools (name → fn + arg schema); `dispatch(call)` parses, **validates/coerces args against the schema**, runs the tool, and returns `{ok, result}` or a **structured error** the model can read. Also expose `tool_specs()` (the JSON-schema list you'd send the model).

## Core approach (format-agnostic)
`tools: name → {fn, params}`. `dispatch`: (1) parse JSON (catch malformed → error), (2) unknown tool → error, (3) validate required args + types, coerce where safe, (4) `try` the call, capture exceptions as `{ok: False, error}`. Keep tool side effects out of the handler; it only routes.

```python
import json, inspect
class ToolHandler:
    def __init__(self): self.tools = {}
    def register(self, name, fn): self.tools[name] = fn
    def specs(self): return [{"name": n, "params": list(inspect.signature(f).parameters)} for n,f in self.tools.items()]
    def dispatch(self, call):
        try: c = json.loads(call) if isinstance(call, str) else call
        except json.JSONDecodeError as e: return {"ok": False, "error": f"bad json: {e}"}
        name, args = c.get("name"), c.get("arguments", {})
        if name not in self.tools: return {"ok": False, "error": f"unknown tool {name}"}
        try: return {"ok": True, "result": self.tools[name](**args)}
        except TypeError as e: return {"ok": False, "error": f"bad args: {e}"}
        except Exception as e: return {"ok": False, "error": str(e)}
```

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** "implement the part of an agent that handles the model's tool call."
- **Follow-ups:** generate **JSON-schema tool specs** for the model; **parallel** tool calls; argument **type coercion**; streaming/partial tool-call args (→ [[32-streaming-response-handler]]); a `confirm` gate for dangerous tools.
- **Tips:** return errors as **data the model can act on** (not exceptions); keep the registry + dispatch tiny and testable; validate before calling.
- **Pitfalls:** crashing on malformed JSON / unknown tool / wrong args (must be graceful), executing dangerous tools without an allowlist, letting one tool's exception kill the agent.

### Take-home / work-trial
- **Tips:** ship the registry + schema validation + tests for malformed/unknown/bad-args; README the spec-generation.
- **Pitfalls:** no schema validation, no structured error contract, no tests for the failure paths.

## Cross-track map
B = code the handler (here) · D3 = tool-platform design (sandboxing, observability) · G = build a tooled agent (take-home). See [[16-minimal-agent-loop]] for the loop that calls this.
