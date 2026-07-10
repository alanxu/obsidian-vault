---
title: Function-Calling / Tool-Use Handler
slug: function-calling-tool-handler
type: agentic
leetcode: null
companies: [OpenAI, Anthropic, Anysphere, Cognition, Cohere, "any AI-eng team", "agent-focused shops broadly"]
difficulty: ★★★☆☆
frequency: rising
formats: [Live, Take-home]
levels: 1
time-box: live 30–45 min
time-box-take-home: 4–8 hours
tags: [agent, tool-calling, schema-validation, parsing, registry, json-schema]
related: ["[[16-minimal-agent-loop]]", "[[31-retry-with-backoff]]", "[[32-streaming-response-handler]]", "[[practical-oo-coding-deep-guide]]"]
---

# Function-Calling / Tool-Use Handler

The **single-step dispatch** the agent loop calls: take a model's tool call, validate it, run the tool, return a structured result. Distinct from [[16-minimal-agent-loop]] (the loop) — this is the registry + validation + dispatch component. In production this is one of the highest-stakes code paths in any agent.

## Problem

The model emits a tool call as JSON: `{"name": "...", "arguments": {...}}` (sometimes wrapped in `function_call` or `tool_calls`). Implement a `ToolHandler`:

- **Registry** of tools (name → fn + arg schema).
- `dispatch(call) -> {"ok": bool, "result": Any}` (or `{"ok": False, "error": str}`).
- `tool_specs() -> list[dict]` — the JSON-schema you'd send the model so it knows what tools exist.

**The headline requirement:** errors are **data the model can act on**, not Python exceptions that crash the loop.

## Core approach (format-agnostic)

```python
import json

class ToolHandler:
    def __init__(self): self.tools = {}     # name -> {"fn": callable, "schema": dict}

    def register(self, name, fn, schema=None):
        self.tools[name] = {"fn": fn, "schema": schema or {}}

    def specs(self):
        return [
            {"name": n, "parameters": t["schema"]}
            for n, t in self.tools.items()
        ]

    def dispatch(self, call):
        # 1. Parse JSON
        try:
            c = json.loads(call) if isinstance(call, str) else dict(call)
        except (json.JSONDecodeError, TypeError) as e:
            return {"ok": False, "error": f"bad json: {e}"}

        # 2. Locate tool
        name = c.get("name")
        if name not in self.tools:
            return {"ok": False, "error": f"unknown tool: {name!r}"}

        # 3. Coerce / validate args against schema
        args = c.get("arguments", {}) or {}
        if not isinstance(args, dict):
            return {"ok": False, "error": "arguments must be an object"}
        coerced, err = self._validate(args, self.tools[name]["schema"])
        if err:
            return {"ok": False, "error": f"bad args: {err}"}

        # 4. Run, capture exceptions as data
        try:
            return {"ok": True, "result": self.tools[name]["fn"](**coerced)}
        except Exception as e:
            return {"ok": False, "error": f"{type(e).__name__}: {e}"}

    def _validate(self, args, schema):
        # Minimal validator: required + types. Real impl uses jsonschema or pydantic.
        out = {}
        for k, t in (schema.get("properties") or {}).items():
            if k in args:
                val = args[k]
                if t == "integer" and not isinstance(val, int):
                    try: val = int(val)
                    except (TypeError, ValueError):
                        return None, f"{k} must be integer"
                elif t == "number" and not isinstance(val, (int, float)):
                    try: val = float(val)
                    except (TypeError, ValueError):
                        return None, f"{k} must be number"
                elif t == "string" and not isinstance(val, str):
                    val = str(val)
                elif t == "boolean" and not isinstance(val, bool):
                    val = bool(val)
                out[k] = val
        for req in schema.get("required", []):
            if req not in out:
                return None, f"missing required: {req}"
        return out, None
```

**Complexity.** Per dispatch: O(args + schema size). Validation can be expensive; precompile schemas if hot.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** "implement the part of an agent that handles the model's tool call" (~20 min), then probing on robustness (~10 min).
- **Follow-ups (real, reported):**
  - **Generate JSON-schema tool specs** for the model — accept Python type hints and emit the schema.
  - **Parallel tool calls** — model emits `[call1, call2, call3]`; dispatch concurrently with `concurrent.futures.ThreadPoolExecutor`; gather results.
  - **Argument type coercion** — `"42"` → `42`, `"true"` → `True`, with safe fallbacks.
  - **Streaming / partial tool-call args** — model emits arg fragments over multiple chunks → see [[32-streaming-response-handler]].
  - **`confirm` gate for dangerous tools** — `register(name, fn, dangerous=True)`; dispatch returns `{"ok": False, "error": "needs confirmation"}` until a flag is set.
  - **Per-tool retry policy** — idempotent tools retry freely; non-idempotent tools retry with backoff only on transient errors.
  - **Tool allowlist per call** — the agent's policy decides which tools are even callable.
  - **Argument redaction** — log call without sensitive args; redact keys marked `secret: true`.
  - **Tracing** — emit a span per dispatch with timing + error class.
  - **Async dispatch** — same interface but `async def dispatch` for async tools.
  - **Output-size discipline** — a tool returning 2MB of JSON floods the context → truncate/paginate at the handler (`max_result_tokens` per tool, "result truncated, use page=2"), don't trust tools to self-limit; the context-economy angle interviewers increasingly probe.
  - **MCP framing** — this handler is what an MCP *client* does (discovery→validate→dispatch across servers); if the interviewer says MCP, map registry→`tools/list`, dispatch→`tools/call`, and add the trust boundary (third-party server output is untrusted → [[../llm-system-design/37-mcp-tool-platform]]).
- **Tips:**
  - **Return errors as data the model can act on** — never `raise` out of dispatch.
  - Keep the **registry + dispatch tiny and testable**; resist feature creep.
  - **Validate before calling** — better error messages to the model.
  - For parallel: dispatch concurrently, but **gather observations in order** for stable history.
  - For schemas: use `inspect.signature` to auto-derive from Python type hints if spec allows.
- **Pitfalls:**
  - **Crashing on malformed JSON / unknown tool / wrong args** — must be graceful.
  - **Executing dangerous tools without an allowlist** — confirm before destructive actions.
  - **Letting one tool's exception kill the agent** — capture in the dict.
  - **Schema-validation that lets wrong types through** — `"42"` for an integer field should coerce or reject (clarify).
  - **Calling tool before validating** — wasted execution, leaks side effects.
  - **Tool name collision** — case sensitivity, namespace.

### Take-home / work-trial
- **Tips:**
  - Ship the registry + schema validation + tests for malformed/unknown/bad-args/exception paths.
  - README the spec-generation.
  - If asked: add a `--confirm-dangerous` flag and a `--dry-run` mode.
- **Pitfalls:**
  - **No schema validation** — model can call with garbage.
  - **No structured error contract** — loop can't reason about failures.
  - **No tests for the failure paths** — the whole point.
  - **Tools with side effects in the registry** — tests should use mocks.

### Whiteboard (when asked "design tool use")
- **Tips:** Sketch the contract between model and handler: spec out, parse, validate, dispatch, observe.
- **Pitfalls:** Confusing with the agent loop.

## Company variants

- **OpenAI / Anthropic / Anysphere / Cognition** — canonical.
- **Cohere / any AI-eng team** — increasingly expected.
- **Vertical AI shops** (Harvey / Casetext / Glean) — heavy tool use.

## Worked example trace

```
Registered:
  "get_weather": {"fn": get_weather, "schema": {
      "properties": {"city": "string", "units": "string"},
      "required": ["city"]}}

Call 1: '{"name": "get_weather", "arguments": {"city": "Paris"}}'
  → validate OK; run get_weather("Paris"); return {"ok": True, "result": "18°C"}

Call 2: '{"name": "unknown", "arguments": {}}'
  → unknown tool → {"ok": False, "error": "unknown tool: 'unknown'"}

Call 3: '{"name": "get_weather", "arguments": {}}'
  → missing "city" → {"ok": False, "error": "bad args: missing required: city"}

Call 4: '{"name": "get_weather", "arguments": {"city": "Paris", "units": "metric"}}'
  → validate OK; run → success
```

## Cross-track map
- **B** = code the handler (here)
- **D3** = tool-platform design (sandboxing, observability, eval)
- **G** = build a tooled agent (take-home)
- [[16-minimal-agent-loop]] is the loop that calls this.

## Related
[[16-minimal-agent-loop]] (the caller) · [[31-retry-with-backoff]] (per-tool reliability) · [[32-streaming-response-handler]] (when args arrive as a stream).