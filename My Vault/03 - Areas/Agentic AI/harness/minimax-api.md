---
title: MiniMax Model API Reference
pillar: harness
parent: ./README.md
type: reference
---

# MiniMax Model API Reference

Provider-specific. The MiniMax M-series models expose two protocol-compat endpoints so existing Claude / OpenAI clients work unchanged. This is the Anthropic-compat (Messages API) spec; the OpenAI-compat (Chat Completions) spec is symmetric with the standard deviations noted below.

## E.1 Endpoints

| Protocol                            | Endpoint                                              |
| ----------------------------------- | ----------------------------------------------------- |
| **Anthropic Messages** (intl)       | `POST https://api.minimax.io/anthropic/v1/messages`   |
| **Anthropic Messages** (China)      | `POST https://api.minimaxi.com/anthropic/v1/messages` |
| **OpenAI Chat Completions** (intl)  | `POST https://api.minimax.io/v1/chat/completions`     |
| **OpenAI Chat Completions** (China) | `POST https://api.minimaxi.com/v1/chat/completions`   |

## E.2 Authentication

One key, two header styles:

```
Authorization: Bearer <API_KEY>     # preferred
x-api-key: <API_KEY>                # Anthropic-native header
```

If both are sent, `Authorization` wins.

## E.3 Models

| Model | Context | Multimodal | Notes |
|---|---|---|---|
| `MiniMax-M3` | 1,000,000 | text, image, video | Latest. Coding/agentic SOTA. Thinking controllable. |
| `MiniMax-M3[1m]` | 1,000,000 | yes | Explicit 1M-context mode (used by Claude Code config) |
| `MiniMax-M2.7` | 204,800 | text + tools | "Recursive self-improvement" framing, ~60 tps |
| `MiniMax-M2.7-highspeed` | 204,800 | text + tools | ~100 tps |
| `MiniMax-M2.5` | 204,800 | text + tools | ~60 tps |
| `MiniMax-M2.5-highspeed` | 204,800 | text + tools | ~100 tps |
| `MiniMax-M2.1` | 204,800 | text + tools | Multilingual programming focus |
| `MiniMax-M2.1-highspeed` | 204,800 | text + tools | ~100 tps |
| `MiniMax-M2` | 204,800 | text + tools | Older agentic baseline |

## E.4 Anthropic-compat Request Schema

| Field              | Type              | Required | Notes                                                                     |
| ------------------ | ----------------- | -------- | ------------------------------------------------------------------------- |
| `model`            | enum              | ✅        | See table above                                                           |
| `messages`         | array             | ✅        | Alternating user / assistant                                              |
| `max_tokens`       | int               |          | M3: rec **131072** / max **524288**. M2.x: rec **65536** / max **204800** |
| `system`           | string \| block[] |          | Plain text OR `[{type:text, text, cache_control?}]`                       |
| `temperature`      | 0–2               |          | default `1`                                                               |
| `top_p`            | 0–1               |          | default `0.95` (M3) / `0.9` (M2.x)                                        |
| `stream`           | bool              |          | default `false`                                                           |
| `tools`            | array             |          | `[{name, description, input_schema, cache_control?}]`                     |
| `tool_choice`      | object            |          | `type: auto \| none` only — **no forced-tool semantics**                  |
| `thinking`         | object            |          | `{type: disabled \| adaptive}`. M3 only; M2.x always thinks               |
| `service_tier`     | enum              |          | `standard` (default) or `priority` (1.5× price, faster admission)         |
| `metadata.user_id` | string            |          | Per-user rate limit / billing                                             |

## E.5 Request Content Blocks

| `type`            | Models      | Notes                                                               |
| ----------------- | ----------- | ------------------------------------------------------------------- |
| `text`            | all         | Plain text                                                          |
| `image`           | **M3 only** | `source: {type: base64\|url, ...}`, `detail: low\|default\|high`    |
| `video`           | **M3 only** | `source` like image; `fps` 0.2–5 (default 1); `max_long_side_pixel` |
| `tool_use`        | all         | Echo prior assistant tool call: `{id, name, input}`                 |
| `tool_result`     | all         | Tool execution result: `{tool_use_id, content: string\|block[]}`    |
| `thinking`        | all (echo)  | Must include `signature` unchanged                                  |
| `mid_conv_system` | **M3 only** | System instructions inserted mid-conversation                       |

**File limits:** image ≤10MB, video ≤50MB (URL/base64), video ≤512MB (Files API via `mm_file://{file_id}`), request body ≤64MB.

**Image detail → rough tokens:** `low` ~few hundred, `default` ~1k–3k, `high` up to ~15k+. Use `count_tokens` endpoint for exact.

## E.6 Response

```
{
  id, type: "message", role: "assistant", model,
  content: [
    {type: "text",      text},
    {type: "tool_use",  id, name, input},
    {type: "thinking",  thinking, signature}   // M3 only when thinking enabled
  ],
  stop_reason: "end_turn" | "max_tokens" | "tool_use",
  usage: {input_tokens, output_tokens, cache_creation_input_tokens, cache_read_input_tokens}
}
```

## E.7 Streaming (SSE)

`Content-Type: text/event-stream`. Each event is a JSON object on a `data:` SSE line.

**Top-level event types:** `message_start` · `ping` · `content_block_start` · `content_block_delta` · `content_block_stop` · `message_delta` · `message_stop`

**Delta types (inside `content_block_delta.delta.type`):** `text_delta` · `thinking_delta` · `signature_delta`

### E.7.1 `message_start`

First event in every stream. Full message envelope, `content: []` (blocks arrive after).

```json
{
  "type": "message_start",
  "message": {
    "id": "msg_xxx",
    "type": "message",
    "role": "assistant",
    "content": [],
    "model": "MiniMax-M3",
    "stop_reason": null,
    "stop_sequence": null,
    "usage": { "input_tokens": 0, "output_tokens": 0,
               "cache_creation_input_tokens": 0, "cache_read_input_tokens": 1366 },
    "service_tier": "standard"
  }
}
```

`usage` here is provisional — final numbers come in `message_delta`.

### E.7.2 `ping`

Heartbeat. Just `{ "type": "ping" }`. Ignore unless you're measuring keep-alive.

### E.7.3 `content_block_start`

Opens a new content block. `index` is 0-based and identifies the block for subsequent deltas.

```json
{ "type": "content_block_start", "index": 0,
  "content_block": { "type": "thinking", "thinking": "" } }
```

For `tool_use` the block is `{type:"tool_use", id, name, input:{}}` (input arrives via deltas).

### E.7.4 `content_block_delta`

Incremental update to a block. Each delta is small — one or a few tokens.

```json
{ "type": "content_block_delta", "index": 0,
  "delta": { "type": "thinking_delta", "thinking": "..." } }
```

Field on `delta` matches the type: `delta.text`, `delta.thinking`, or `delta.signature`. A thinking block typically ends with a `signature_delta` (the verifiable hash) just before its `content_block_stop`.

For `tool_use`, deltas carry `delta.partial_json` — concatenate across all deltas and `json.loads()` after `content_block_stop`. Don't try to parse the first delta as valid JSON.

### E.7.5 `content_block_stop`

Closes the block at `index`. `{ "type": "content_block_stop", "index": 0 }`.

### E.7.6 `message_delta`

Emitted once, just before `message_stop`. Carries the final `stop_reason` and total `usage`.

```json
{ "type": "message_delta",
  "delta": { "stop_reason": "end_turn" },
  "usage": { "input_tokens": 1252, "output_tokens": 213,
             "cache_creation_input_tokens": 0, "cache_read_input_tokens": 114 } }
```

### E.7.7 `message_stop`

Terminal. `{ "type": "message_stop" }`. Stream is done.

### E.7.8 Stream Anatomy (M3 with thinking)

```
message_start
  └─ message { content: [], model, usage: { input, cache_read } }
ping                                       (optional keep-alive)
content_block_start index=0
  └─ content_block { type: thinking, thinking: "" }
content_block_delta index=0   × N           (thinking_delta chunks)
content_block_delta index=0
  └─ delta { type: signature_delta, signature: "..." }
content_block_stop index=0
content_block_start index=1
  └─ content_block { type: text, text: "" }
content_block_delta index=1   × N           (text_delta chunks)
content_block_stop index=1
message_delta
  └─ delta { stop_reason: "end_turn" }, usage { final }
message_stop
```

For tool-use, swap the second block for a `tool_use` block whose `input` arrives as `partial_json` deltas (concatenate, then parse once).

### E.7.9 Errors Mid-Stream

Not a numbered event type — comes as an SSE `event: error` line:

```
event: error
data: {"type":"error","request_id":"req_xxx","error":{"type":"rate_limit_error","message":"…"}}
```

Stop reading, drop the partial content, surface the error.

## E.8 Errors

| HTTP | `error.type` | When | Retryable? |
|---|---|---|---|
| 400 | `invalid_request_error` | Bad params, unsupported content type, tool input not a JSON object | No |
| 401 | `authentication_error` | API key missing/invalid | No (fix key) |
| 403 | `permission_error` | No access to model/path | No (request access) |
| 404 | `not_found_error` | Model doesn't exist | No |
| 413 | `request_too_large` | Body >64MB or file over its limit | No (resize) |
| 429 | `rate_limit_error` | RPM/TPM/connection limit | **Yes** (backoff) |
| 500 | `api_error` | Internal | Maybe (backoff) |
| 529 | `overloaded_error` | Upstream overloaded | **Yes** (backoff) |

Error body: `{type: "error", request_id, error: {type, message}}`. During streaming, errors arrive as `event: error` SSE events with the same body — stop reading and clean up session state on receipt.

## E.9 OpenAI-compat Differences (Chat Completions)

Same models, same auth, but the request/response shape is OpenAI's. Notable differences from the Anthropic-compat path:

| Behavior | OpenAI-compat | Anthropic-compat |
|---|---|---|
| Request shape | `messages[]` with `role`/`content` | `messages[]` with `system` separate + content blocks |
| Response shape | `choices[].message.content` | `content[]` blocks (text/tool_use) |
| Tool calling | `tools[]` function spec, `tool_calls` in response | `tools[]` w/ `input_schema`, `tool_use` blocks |
| Streaming | SSE via `[DONE]` sentinel | SSE w/ event types (`message_start`, …) |
| Thinking | `<think>...</think>` inlined in `content` (default), OR `reasoning_content` / `reasoning_details` if `reasoning_split=true` | `thinking` blocks in response content |
| Multimodal | `image_url` content parts | Image / video content blocks |
| `tool_choice` | `auto` / `none` / specific function | `auto` / `none` only |

**Critical gotcha (OpenAI-compat):** when `reasoning_split=false` (default), thinking is embedded as `<think>...</think>` *inside* the `content` string. Strip or re-serialize naively → you destroy the reasoning trace. Either set `reasoning_split=true` and parse `reasoning_content` separately, or preserve `content` byte-for-byte.

## E.10 Prompt Caching

`cache_control: {type: "ephemeral"}` is supported on:
- `system[]` text blocks
- each `tools[]` entry
- request `content[]` blocks (text, image, video, tool_use, tool_result)

Cache behavior is reported in the response `usage`:
```
cache_creation_input_tokens   # tokens used to populate the cache
cache_read_input_tokens       # tokens served from cache (cheap)
```

Strategy: front-load stable content (system prompt, tool definitions, few-shots) with a single `cache_control` marker, keep variable content (user input, tool results) unmarked.

## E.11 Setup Recipes

**Claude Code (use Anthropic-compat):**
```bash
export ANTHROPIC_BASE_URL="https://api.minimax.io/anthropic"
export ANTHROPIC_AUTH_TOKEN="<MINIMAX_API_KEY>"
export ANTHROPIC_MODEL="MiniMax-M3[1m]"
```

**Cursor / Continue / Aider (use OpenAI-compat):**
```bash
export OPENAI_BASE_URL="https://api.minimax.io/v1"
export OPENAI_API_KEY="<MINIMAX_API_KEY>"
# model id: MiniMax-M3
```

**Native Anthropic SDK (Python):**
```python
from anthropic import Anthropic
client = Anthropic(
    base_url="https://api.minimax.io/anthropic",
    auth_token="<MINIMAX_API_KEY>",   # not api_key
)
msg = client.messages.create(
    model="MiniMax-M3",
    max_tokens=1024,
    messages=[{"role": "user", "content": "hello"}],
)
```

## E.12 Gotchas

1. **Reasoning trace preservation** — biggest footgun in OpenAI-compat. See §E.9.
2. **`tool_choice: tool` not supported** — can't force a specific tool by name on either protocol. Enforce in prompt + parse, not API.
3. **Region matters** — international vs China endpoints are separate accounts, no failover.
4. **Highspeed ≠ lower quality** — same model, different infra tier. Pick on latency budget.
5. **No native batch API** in either compat layer (wrap it yourself).
6. **Files API for video** — `mm_file://{file_id}` is the only way to send video >50MB. Upload first, then reference.
7. **`thinking` defaults differ by model** — M3 off by default, M2.x always on. Set explicitly to avoid surprise.
8. **`auth_token=` not `api_key=`** in the Anthropic SDK when pointing at MiniMax — common copy-paste error.
