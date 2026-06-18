---
title: Streaming LLM Response Handler (incremental parse + cancellation)
slug: streaming-response-handler
type: agentic
leetcode: null
companies: [Anysphere, OpenAI, Anthropic, general AI-eng]
difficulty: ★★★☆☆
frequency: rising
formats: [Live, Take-home]
levels: 1
time-box: live 30–45 min
tags: [agent, streaming, generators, async, cancellation, partial-json]
related: ["[[16-minimal-agent-loop]]", "[[30-function-calling-tool-handler]]", "[[08-multi-file-iterator]]"]
---

# Streaming LLM Response Handler

Consume a token/chunk stream, render incrementally, detect tool-call boundaries, and support **cancellation** mid-stream. Core to low-latency UX (Anysphere/Cursor completions, OpenAI streaming).

## Problem
Given a stream of chunks (text deltas, or tool-call deltas), implement a handler that: yields assembled text incrementally, **detects when the model is emitting a tool call** (assemble partial JSON args), signals completion, and can be **cancelled** cooperatively (stop consuming, clean up).

## Core approach (format-agnostic)
A generator/async-iterator over chunks with a small **buffer**: append deltas, emit renderable text as it arrives; when a tool-call marker appears, accumulate arg fragments until valid JSON, then hand off to [[30-function-calling-tool-handler]]. Cancellation = a cooperative flag / `asyncio` task cancel checked each chunk; flush/cleanup on exit.

```python
async def stream_handler(chunks, on_text, cancel_event):
    buf, tool_buf = [], []
    async for ch in chunks:
        if cancel_event.is_set(): break            # cooperative cancellation
        if ch.get("type") == "text":
            on_text(ch["delta"]); buf.append(ch["delta"])
        elif ch.get("type") == "tool":
            tool_buf.append(ch["delta"])            # accumulate partial JSON args
    return "".join(buf), "".join(tool_buf)
```

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** "handle a streaming model response," then "support cancel," then "what about streamed tool-call args?"
- **Follow-ups:** **partial-JSON** parsing for streamed tool args, **backpressure**, time-to-first-token vs total, SSE parsing, multiplexing multiple streams, reconnect/resume.
- **Tips:** make the consumer a generator so cancellation and incremental render fall out; check the cancel flag every chunk; flush partials on stop.
- **Pitfalls:** buffering the whole stream (kills TTFT benefit), no cancellation path (runaway cost), assuming tool-call JSON arrives whole, not cleaning up on cancel.

### Take-home / work-trial
- **Tips:** sync + async iterators, a cancellation test, a partial-JSON-args test; README the backpressure approach.
- **Pitfalls:** blocking the event loop, no timeout, losing the last partial chunk.

## Related
[[30-function-calling-tool-handler]] (consumes the assembled tool call) · [[08-multi-file-iterator]] (iterator/async patterns) · [[16-minimal-agent-loop]].
