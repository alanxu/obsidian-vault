---
title: Streaming / Partial JSON Parser
slug: streaming-json-parser
type: agentic
leetcode: null
companies: [Anysphere, OpenAI, Anthropic, Cognition, "agent-UI teams"]
difficulty: ★★★★☆
frequency: rising
formats: [Live, Take-home]
levels: 2
time-box: live 40–50 min
tags: [streaming, json, parser, state-machine, tool-calls, incremental]
related: ["[[32-streaming-response-handler]]", "[[30-function-calling-tool-handler]]", "[[36-tokenizer-encode-decode]]"]
added: 2026-07-08 (audit fill — Cursor/OpenAI reported: handle streaming LLM output incl. partial tool-call JSON)
evidence: "PARTIAL: Cursor guides (techinterview.org, jobsbyculture 2026) list 'handling streaming LLM output' as a real interview task — verified at topic level. The partial-JSON-parser framing is my distillation of that task; OpenAI/Anthropic/Cognition = inference."
---

# Streaming / Partial JSON Parser

LLMs stream tool-call arguments as **JSON fragments**: `{"na` → `me": "get_w` → `eather", "args`… The UI wants to render partial args live; the loop wants to know the instant `name` is complete. Build a parser that accepts chunks and exposes the **best-effort current value**. This is the coding-round distillation of a real Cursor/OpenAI-client problem.

## Problem

```python
class StreamingJsonParser:
    def feed(self, chunk: str) -> None      # arbitrary split points, even mid-escape
    def current(self) -> Any                 # best-effort parse of what's arrived
    def is_complete(self) -> bool
```

Rules to clarify (and the usual expected answers): partial **strings** → return the prefix (`{"name": "get_w`… → `{"name": "get_w"}`); partial **key** with no value yet → omit the key; partial **`tru`/`fals`** → omit; partial **numbers** → clarify (`12` may become `123`; returning the prefix is usually accepted — the strict answer is "final only on delimiter"); nested objects/arrays → same rules recursively.

## Core approach (format-agnostic)

Level 1 (usually enough live): **close-then-trim** — keep the full buffer; on `current()`, close whatever's open with a string-aware stack scan; if that still doesn't parse (dangling key or partial literal), trim from the tail and retry. Level 2: true incremental state machine (event/SAX style). Write Level 1 well and *name* Level 2.

```python
import json

class StreamingJsonParser:
    def __init__(self):
        self.buf = ""

    def feed(self, chunk: str):
        self.buf += chunk

    def is_complete(self) -> bool:
        try:
            json.loads(self.buf); return True
        except ValueError:
            return False

    def current(self):
        s = self.buf
        while s.strip():
            try:
                return json.loads(self._close(s))
            except ValueError:
                s = s[:-1].rstrip()   # dangling key / partial literal → trim, retry
        return None

    def _close(self, s: str) -> str:
        """String-aware scan: close an open string, drop a dangling escape,
        strip a trailing comma/colon, close open brackets."""
        stack, in_str, esc = [], False, False
        for ch in s:
            if in_str:
                if esc: esc = False
                elif ch == "\\": esc = True
                elif ch == '"': in_str = False
            else:
                if ch == '"': in_str = True
                elif ch in "{[": stack.append(ch)
                elif ch in "}]":
                    if stack: stack.pop()
        if esc: s = s[:-1]                       # drop dangling backslash
        if in_str: s += '"'                      # close open string
        t = s.rstrip()
        if t.endswith((",", ":")):
            t = t[:-1]
        return t + "".join("}" if c == "{" else "]" for c in reversed(stack))
```

**Complexity.** `feed`: O(chunk). `current`: O(buffer) typical; the trim-retry fallback (dangling key / partial literal) is O(buffer²) worst case but trims only a few chars in practice — fine for UI-frame rates. The incremental FSM makes it O(chunk) amortized (mention, don't build).

**The two state bits that earn the hire signal: `in_str` and `esc`.** Braces inside strings (`{"code": "if (x) {"`), escaped quotes (`\"`) — every naive bracket-counter dies here; say it before you're asked.

## By format

### Live · CoderPad — *primary*
- **How it appears:** "the model streams JSON; render partial state" (~25 min), then robustness probes.
- **Follow-ups (reported/likely):**
  - **Escaped quotes / braces inside strings** — the classic trap (handled above).
  - **`is_complete` per-field:** "tell me the moment `name` is final" → key is complete when its value's closing delimiter arrives → callback/subscription API (`on_field("name", cb)`).
  - **Partial number ambiguity** — `12` might become `123`; only final on delimiter. Same for `tru`/`true`.
  - **Multiple JSON docs in one stream** (NDJSON / concatenated tool calls) → after complete parse, reset buffer with remainder.
  - **Unicode escape split across chunks** (`\u00e` + `9`) → the `esc` handling generalizes: buffer incomplete escapes.
  - **Malformed JSON from the model** → repair vs reject: surface error + raw buffer; never crash the stream ([[30-function-calling-tool-handler]] contract).
  - **Why not regex?** → JSON strings aren't regular (nesting); FSM/stack is the right tool.
- **Tips:**
  - Clarify partial-value semantics **first** — it defines your test cases.
  - Write the string/escape FSM before anything else; test with `'{"a": "b\\"c{", "d'`.
  - Keep `feed` dumb (append) and `current` smart — simplest correct split.
- **Pitfalls:**
  - Bracket counting without string awareness (instant fail on realistic input).
  - Emitting a *wrong* partial (`"count": 12` when stream says `123`) — worse than omitting.
  - O(buffer²) by re-parsing on every `feed` instead of on `current()` demand.
  - Dropping the tail after a complete doc when stream continues.

### Take-home
- Ship: the parser + property tests (random split points of valid JSONs: `current()` never throws, final equals `json.loads`) + NDJSON mode + a small demo streaming a tool call.
- **Pitfall:** skipping the random-split property test — it's exactly what graders run.

## Worked example trace

```
feed('{"name": "get_we')   current() → {"name": "get_we"}
feed('ather", "args": {"city": "Par')
                            current() → {"name": "get_weather", "args": {"city": "Par"}}
feed('is"}}')               is_complete() → True; current() → full object
Trap check: '{"code": "if (x) {"'  → repaired to {"code": "if (x) {"} (brace inside string ignored) ✓
```

## Cross-track map
- **B** = this card
- [[32-streaming-response-handler]] = transport layer (SSE chunks → text); this card = structure layer on top
- **D3** = why agent UIs need it (perceived latency, progressive tool-call display)

## Related
[[32-streaming-response-handler]] (feeds this) · [[30-function-calling-tool-handler]] (consumes the parsed call) · [[36-tokenizer-encode-decode]] (same buffer-until-safe discipline).
