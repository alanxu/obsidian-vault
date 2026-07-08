---
title: Streaming LLM Response Handler (incremental parse + cancellation)
slug: streaming-response-handler
type: agentic
leetcode: null
companies: [Anysphere, OpenAI, Anthropic, Cursor, Notion-AI, "any low-latency AI UX"]
difficulty: ★★★☆☆
frequency: rising
formats: [Live, Take-home]
levels: 1
time-box: live 30–45 min
time-box-take-home: 4–8 hours
tags: [agent, streaming, generators, async, cancellation, partial-json, sse]
related: ["[[16-minimal-agent-loop]]", "[[30-function-calling-tool-handler]]", "[[08-multi-file-iterator]]"]
---

# Streaming LLM Response Handler

Consume a token/chunk stream, render incrementally, detect tool-call boundaries, and support **cancellation** mid-stream. Core to low-latency UX (Anysphere/Cursor completions, OpenAI streaming). The base case is straightforward; the follow-ups separate juniors from seniors.

## Problem

Given a stream of chunks (text deltas, or tool-call deltas), implement a handler that:
1. Yields assembled text incrementally.
2. **Detects when the model is emitting a tool call** (assemble partial JSON args).
3. Signals completion.
4. Can be **cancelled** cooperatively (stop consuming, clean up).

```python
async def stream_handler(chunks, on_text, cancel_event) -> (text, tool_calls)
```

## Core approach (format-agnostic)

A **generator/async-iterator** over chunks with a small **buffer**:

- Append deltas to `buf`; emit renderable text as it arrives via `on_text(delta)`.
- When a tool-call marker appears (often a special token or a chunk `type`), accumulate arg fragments in `tool_buf` until valid JSON, then yield the assembled call.
- **Cancellation** = a cooperative flag / `asyncio` task cancel, checked each chunk. Flush partials on stop.

```python
import asyncio
import json

async def stream_handler(chunks, on_text, cancel_event=None):
    """chunks: async iterator yielding {"type": "text"|"tool", "delta": str, ...}"""
    text_buf, tool_buf = [], []
    in_tool = False
    depth = 0                       # JSON brace depth to detect valid JSON

    async for ch in chunks:
        if cancel_event and cancel_event.is_set():
            break
        kind = ch.get("type")
        delta = ch.get("delta", "")
        if kind == "text":
            on_text(delta)
            text_buf.append(delta)
        elif kind == "tool":
            in_tool = True
            tool_buf.append(delta)
            # Cheap JSON-completeness check via brace depth
            depth += delta.count("{") - delta.count("}")
            if depth <= 0 and tool_buf:
                full = "".join(tool_buf)
                try:
                    obj = json.loads(full)
                    tool_buf = []
                    depth = 0
                    # Hand assembled tool call to handler
                    yield {"type": "tool_call", "call": obj}
                except json.JSONDecodeError:
                    pass       # still incomplete; keep accumulating
    yield {"type": "text_done", "text": "".join(text_buf)}
    if cancel_event and cancel_event.is_set():
        yield {"type": "cancelled"}
```

**Complexity.** O(chunks) work; O(buffered JSON) memory.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** "handle a streaming model response" (~15 min), then "support cancel" (~5 min), then "what about streamed tool-call args?" (~10 min).
- **Follow-ups (real, reported):**
  - **Partial-JSON parsing** for streamed tool args — incremental parser or "wait until balanced braces + valid JSON."
  - **Backpressure** — when the consumer is slow, drop intermediate chunks or coalesce.
  - **Time-to-first-token (TTFT)** vs total latency — measure both.
  - **SSE parsing** — `data: {...}\n\n` format; handle multi-line events, comments, heartbeats.
  - **Multiplexing multiple streams** — fan-in from N model calls.
  - **Reconnect / resume** — when a stream drops mid-way, can we resume from the last received token?
  - **Error mid-stream** — emit a structured error object instead of dropping.
  - **Cancellation cleanup** — close the HTTP connection, mark task cancelled, propagate to the model provider if possible.
  - **Render strategy** — debounce text updates to a UI; coalesce N tokens into one render call.
  - **Encoding** — UTF-8, surrogate pairs, emoji ZWJ sequences (sometimes split mid-grapheme).
  - **Robust partial-JSON parsing** — the brace-depth heuristic here breaks on braces *inside strings* (`{"code": "if (x) {"`); the string-aware FSM version is its own card → [[37-streaming-json-parser]]; know which rigor level the interviewer wants.
  - **Guardrails on a stream** — content policy must check text *before* the user sees it, but you're rendering as it arrives → incremental classification with a small look-ahead buffer + ability to retract/stop mid-stream; the safety×streaming collision is a real design point at labs.
  - **Usage accounting mid-stream** — tokens are billed even if the user cancels at token 500 → count deltas as they arrive, report usage on cancel — ties streaming to the cost story ([[../llm-system-design/31-llm-observability-cost]]).
- **Tips:**
  - **Make the consumer a generator** so cancellation and incremental render fall out.
  - **Check the cancel flag every chunk.**
  - **Flush partials on stop** — partial text is useful for resume UX.
  - For partial JSON: use a streaming parser (`json-stream`, `ijson`) or the brace-counting heuristic.
  - Narrate the **TTFT vs total** trade-off: streaming improves perceived latency even at the same total time.
- **Pitfalls:**
  - **Buffering the whole stream** — kills TTFT benefit.
  - **No cancellation path** — runaway cost; user closes the tab but the call keeps going.
  - **Assuming tool-call JSON arrives whole** — it streams too.
  - **Not cleaning up on cancel** — leaked HTTP connection, leaked model quota.
  - **Blocking the event loop** — sync I/O inside an async generator.
  - **Dropping partial text on cancel** — UX cost.
  - **Time-to-first-byte vs time-to-first-token confusion** — TTFT is what users feel.

### Take-home / work-trial
- **Tips:**
  - Ship sync + async iterators.
  - Cancellation test: start a stream, cancel mid-flight, verify clean exit + partial text preserved.
  - Partial-JSON-args test: stream `{"name":` then `"foo",` then `"args":{}` then `}`; assemble correctly.
  - README the backpressure approach.
- **Pitfalls:**
  - **Blocking the event loop** in async tests.
  - **No timeout** — runaway stream.
  - **Losing the last partial chunk** — drain on cancel.

### Whiteboard (when asked "design streaming UX")
- **Tips:** Draw the chunk → buffer → render path; mark the cancellation check; show the tool-call assembly.
- **Pitfalls:** Confusing streaming with chunked HTTP transfer encoding.

## Company variants

- **Anysphere (Cursor)** — the canonical low-latency AI UX shop; this is table stakes.
- **OpenAI / Anthropic** — API surface area.
- **Notion AI / Linear / any AI UX** — streaming is the default.

## Worked example trace

```
Chunks:
  {"type":"text","delta":"The weather "}
  {"type":"text","delta":"in Paris is "}
  {"type":"tool","delta":"{\""}
  {"type":"tool","delta":"name\":\""}
  {"type":"tool","delta":"get_weather\",\""}
  {"type":"tool","delta":"arguments\":{\"city\":\""}
  {"type":"tool","delta":"Paris\"}}"}

  → on_text fires twice ("The weather ", "in Paris is ")
  → tool buffer accumulates; depth becomes 0; json.loads → tool_call
  → yield {"type":"tool_call", "call": {"name":"get_weather","arguments":{"city":"Paris"}}}
```

## Related
[[30-function-calling-tool-handler]] (consumes the assembled tool call) · [[08-multi-file-iterator]] (iterator/async patterns) · [[16-minimal-agent-loop]].