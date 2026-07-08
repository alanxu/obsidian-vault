---
title: Tokenizer — Encode/Decode (+ streaming detokenize)
slug: tokenizer-encode-decode
type: agentic
leetcode: null
companies: [Anthropic, OpenAI, Cohere, "AI-infra teams"]
difficulty: ★★★☆☆
frequency: rising
formats: [Live, Code-review, OA·GCA/HR]
levels: 2
time-box: live 30–45 min
tags: [tokenizer, bpe, streaming, buffering, code-review, greedy-matching, trie]
related: ["[[32-streaming-response-handler]]", "[[13-stack-trace-to-trace-conversion]]", "[[practical-oo-coding-deep-guide]]"]
added: 2026-07-08 (audit fill — Anthropic reported: tokenize/detokenize code review + streaming tokenization with buffering)
evidence: "VERIFIED (strongest tier available): Anthropic question aggregators with candidate reports (prachub, linkjob, aiofferly 2026) describe tokenize/detokenize code-review and streaming-tokenization-with-buffering problems. OpenAI/Cohere = inference."
---

# Tokenizer — Encode/Decode

Reported at Anthropic in two skins: **(a) code review** — "here's a `tokenize`/`detokenize` implementation; find what's wrong" — and **(b) build** — greedy vocab tokenizer, then extend to **streaming detokenization with buffering**. Not full BPE *training* (that's a rare deep-cut); it's vocab-based encode/decode + invariants.

## Problem

Given `vocab: dict[str, int]` (token string → id), implement:

```python
encode(text: str) -> list[int]      # greedy longest-match; every char must be coverable
decode(ids: list[int]) -> str       # inverse
# Level 2 (streaming):
class StreamingDecoder:
    def feed(self, ids: list[int]) -> str   # returns printable text so far
    def flush(self) -> str                   # end of stream
```

**Core invariant to state out loud:** `decode(encode(text)) == text` (round-trip). Streaming twist: multi-byte characters / merge-dependent tokens can't always be printed immediately — **buffer until safe**.

## Core approach (format-agnostic)

Greedy longest-match with a max-token-length bound (or a trie for O(text) with alphabet-bounded steps):

```python
class Tokenizer:
    def __init__(self, vocab: dict[str, int]):
        self.vocab = vocab
        self.inv = {i: t for t, i in vocab.items()}
        if len(self.inv) != len(vocab):
            raise ValueError("duplicate ids")
        self.max_len = max(map(len, vocab), default=0)

    def encode(self, text):
        ids, i = [], 0
        while i < len(text):
            for L in range(min(self.max_len, len(text) - i), 0, -1):
                tok = text[i:i+L]
                if tok in self.vocab:
                    ids.append(self.vocab[tok]); i += L; break
            else:
                raise ValueError(f"unencodable char at {i}: {text[i]!r}")
        return ids

    def decode(self, ids):
        try:
            return "".join(self.inv[i] for i in ids)
        except KeyError as e:
            raise ValueError(f"unknown id: {e}")
```

Streaming decode (byte-level vocab, the real-world case — GPT/Claude vocabs are byte-level, so a token can end mid-UTF-8-character):

```python
class StreamingDecoder:
    def __init__(self, inv: dict[int, bytes]):
        self.inv = inv
        self.buf = b""

    def feed(self, ids):
        self.buf += b"".join(self.inv[i] for i in ids)
        # emit the longest prefix that is valid UTF-8; keep the partial tail
        for cut in range(len(self.buf), max(len(self.buf) - 4, -1), -1):
            try:
                out = self.buf[:cut].decode("utf-8")
                self.buf = self.buf[cut:]
                return out
            except UnicodeDecodeError:
                continue
        return ""

    def flush(self):
        out = self.buf.decode("utf-8", errors="replace")
        self.buf = b""
        return out
```

**Complexity.** Encode: O(n·max_len) with dict (O(n) with trie). Decode: O(#ids). Streaming: buffer ≤ 3 bytes (max UTF-8 tail).

## By format

### Code review (Anthropic-reported skin) — *primary*
- **How it appears:** a flawed implementation; "what's wrong, and fix it."
- **Planted bugs to hunt (checklist):**
  - **Shortest-match instead of longest-match** greedy → round-trip breaks (`"in", "int"` — encodes `"int"` as `in`+`t?`).
  - **No else on the inner loop** — unencodable char → infinite loop or silent skip (dropped characters).
  - **Inverse map collisions** — two tokens, same id (or same string twice) → decode ambiguity; check at init.
  - **Concatenation ambiguity** — decode joins tokens with a delimiter (or trims spaces) → violates round-trip.
  - **Off-by-one on the slice window** (`min(max_len, len-i)`).
  - **Unicode:** slicing bytes vs str; `len()` on bytes of multibyte chars.
- **Tips:** run round-trip property in your head with a 2-token adversarial vocab; say the invariant first — it's the rubric.

### Live · CoderPad (build)
- **Follow-ups (reported/likely):**
  - **Streaming detokenize with buffering** (Level 2 above) — the reported extension; state *why* buffering is needed (token ≠ character boundary).
  - Greedy isn't optimal — text encodable only with a non-greedy split (`vocab={"ab","a","bc"}`, text `"abc"`: greedy `ab`+dead-end) → backtracking or DP (word-break) for "fewest tokens" / "any valid split".
  - Trie for encode; complexity comparison.
  - Special tokens (`<eos>`) that must match before normal rules; never emitted from user text (injection-adjacent — say it).
  - `tiktoken`-style: count tokens without full encode (same cost — no shortcut; caching per string).
- **Pitfalls:** regex-splitting on spaces (vocabs contain spaces, e.g. `" the"`); mutating the buffer while iterating; forgetting `flush()`.

### OA · GCA/HR
- Appears as "word-break"-flavored deterministic version with exact expected outputs; DP is the safe choice there.

## Worked example trace

```
vocab = {"he":1, "hell":2, "hello":3, "o":4, " ":5, "w":6}
encode("hello w") → greedy at 0: try "hello " (no), "hello"(yes)=3 → " "=5 → "w"=6 → [3,5,6]
decode([3,5,6]) → "hello w" ✓ round-trip

Streaming (byte vocab): "é" = b'\xc3\xa9' split across two tokens:
feed([id(b'\xc3')]) → buffer holds partial → returns ""    (don't emit garbage)
feed([id(b'\xa9')]) → buffer decodes → returns "é"
```

## Cross-track map
- **B** = this card (encode/decode + streaming)
- **E** = why BPE exists, vocab-size tradeoffs, byte-level vs char-level ([[../llm-system-design/fundamentals/README]])
- [[32-streaming-response-handler]] = same buffering discipline one level up (SSE chunks)

## Related
[[32-streaming-response-handler]] (stream sibling) · [[37-streaming-json-parser]] (partial-input parsing) · [[22-add-search-word-trie]] (trie primitive).
