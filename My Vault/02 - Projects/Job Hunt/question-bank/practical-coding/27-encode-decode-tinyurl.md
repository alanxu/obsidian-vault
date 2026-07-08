---
title: Encode and Decode TinyURL
slug: encode-decode-tinyurl
type: leetcode-design
leetcode: 535
companies: [Google, Meta, Bitly, TinyURL, "any URL-shortener service"]
difficulty: ★★☆☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 15–25 min
tags: [hashmap, id-generation, base62, distributed-id]
related: ["Track C URL-shortener system design"]
---

# Encode and Decode TinyURL (#535)

A coding-sized version of the URL-shortener design — the bridge between Track B and Track C. The coding is short; the design follow-ups are where the interview lives.

## Problem

- `encode(longUrl) -> shortUrl`
- `decode(shortUrl) -> longUrl`

The base doesn't specify the format of `shortUrl` — usually `"http://tinyurl.com/<code>"`.

## Core approach (format-agnostic)

Three viable key-generation strategies:

1. **Auto-increment + base62** — `id++; encode_id(id)`. Predictable but enumerable.
2. **Random code** — generate 6–7 chars from `[a-zA-Z0-9]`; retry on collision.
3. **Hash** — `hashlib.md5(longUrl)[:6]`. Deterministic; collision possible.

Pick based on requirements:
- For predictability + global uniqueness → (1) with distributed counter ranges.
- For unguessability → (2).
- For determinism (same URL → same short) → (3).

Also maintain a reverse map `short → long` for `decode`, and an optional forward map `long → short` to dedupe identical long URLs.

### Worked Python solution

```python
import hashlib
import secrets
import string

CHARS = string.ascii_letters + string.digits

class Codec:
    def __init__(self):
        self.encode_map = {}                # short_code -> long_url
        self.decode_map = {}                # long_url -> short_code (dedup)
        self._counter = 0

    def encode(self, longUrl: str) -> str:
        if longUrl in self.decode_map:
            return "http://tinyurl.com/" + self.decode_map[longUrl]

        # Strategy 1: counter + base62
        self._counter += 1
        code = self._to_base62(self._counter)

        # Optional: Strategy 2 fallback on collision
        # while code in self.encode_map:
        #     code = "".join(secrets.choice(CHARS) for _ in range(7))

        self.encode_map[code] = longUrl
        self.decode_map[longUrl] = code
        return "http://tinyurl.com/" + code

    def decode(self, shortUrl: str) -> str:
        code = shortUrl.rsplit("/", 1)[-1]
        return self.encode_map.get(code, "")

    @staticmethod
    def _to_base62(n: int) -> str:
        s = ""
        while n > 0:
            s = CHARS[n % 62] + s
            n //= 62
        return s or "0"
```

**Hash-based variant:**
```python
class Codec:
    def __init__(self):
        self.encode_map = {}

    def encode(self, longUrl: str) -> str:
        code = hashlib.md5(longUrl.encode()).hexdigest()[:6]
        self.encode_map[code] = longUrl
        return "http://tinyurl.com/" + code

    def decode(self, shortUrl: str) -> str:
        code = shortUrl.rsplit("/", 1)[-1]
        return self.encode_map.get(code, "")
```

**Complexity.** O(|code|) per op.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:**
  - Any consistent scheme passes; counter → base62 is clean.
  - Verify roundtrip: `decode(encode(url)) == url` for a few inputs.
- **Pitfalls:**
  - **Decode of unknown code** — return "" or original; spec varies.
  - **Duplicate long URLs** — dedup map avoids two codes for the same URL.
  - **Collision on random codes** — retry loop.

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **Distributed id generation** — counter ranges (each node gets `[N*K, (N+1)*K)`), Snowflake IDs.
  - **Custom aliases** — `encode(url, alias="my-link")`.
  - **TTL / expiry** — links expire after N days; lazy delete.
  - **Analytics** — click counts, geo distribution.
  - **Rate limiting** — limit encodes per IP.
  - **The full system-design version** — Track C (consistent hashing, cache, DB, scale).
  - **Anti-spam / malware** — block known-bad URLs.
  - **Custom domain** — `bit.ly` vs `tinyurl.com`.
  - **QR code generation** — for the short URL.
  - **Bulk encode** — paste a list, get a list.
  - **Privacy** — long URL may contain sensitive query params; warn the user.
  - **Hash + dedup interaction trap** — md5-truncation collides eventually; "retry with salt" breaks determinism, so hash-based + dedup-by-content are mutually exclusive goals past a scale point — walk the birthday math (6 base62 chars ≈ 57B space; collisions expected ~√ ≈ 240k entries).
  - **Read:write ratio drives the design** — shorteners are ~100:1 reads → decode path gets the cache/CDN; encode can be slow — the one-liner that pivots cleanly into the Track C version.
- **Tips:**
  - **Discuss key-generation trade-offs** (counter vs random vs hash) up front.
  - **Discuss collision handling** (retry with longer code).
  - For distributed: mention Snowflake briefly; the full design is Track C.
  - Note that **predictable sequential IDs** are a security issue if you want unguessable links.
- **Pitfalls:**
  - **Unbounded growth** (no TTL).
  - **Predictable sequential IDs** (security).
  - **Collisions** on hash-based keys.
  - **No analytics** when the question asks for them.

### Onsite · NR (Google-style)
- **Tips:** State the three key strategies; pick one and justify.
- **Pitfalls:** Forgetting dedup.

## Company variants

- **Google / Meta / Bitly / TinyURL** — canonical.
- **Track C URL-shortener system design** — production-flavored deep-dive.

## Worked example trace

```
encode("https://example.com/foo")
  → counter = 1 → base62("1") = "b" → return "http://tinyurl.com/b"
encode("https://example.com/bar")
  → counter = 2 → base62("2") = "c" → return "http://tinyurl.com/c"
decode("http://tinyurl.com/b") → "https://example.com/foo"
encode("https://example.com/foo")  # dedup → "http://tinyurl.com/b" (same code)
```

## Related
Track C URL-shortener system design.