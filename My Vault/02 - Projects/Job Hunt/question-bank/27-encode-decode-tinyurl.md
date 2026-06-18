---
title: Encode and Decode TinyURL
slug: encode-decode-tinyurl
type: leetcode-design
leetcode: 535
companies: [General, SD-lite]
difficulty: ★★☆☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 15–25 min
tags: [hashmap, id-generation, base62]
related: []
---

# Encode and Decode TinyURL (#535)

A coding-sized version of the URL-shortener design — the bridge between Track B and Track C.

## Problem
`encode(longUrl) → shortUrl`; `decode(shortUrl) → longUrl`.

## Core approach (format-agnostic)
`id → longUrl` map; key via **auto-increment id → base62**, random code (retry on collision), or hash. Optional reverse map to dedupe identical URLs.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** any consistent scheme passes; counter→base62 is clean.
- **Pitfalls:** decode of unknown code, duplicate long URLs, collision on random codes.

### Live · CoderPad (human)
- **Follow-ups:** **distributed id generation** (counter ranges / Snowflake), custom aliases, TTL/expiry, analytics, the **full system-design version** (→ Track C).
- **Tips:** discuss key-generation trade-offs (counter vs random vs hash) and collision handling; this previews the SD question.
- **Pitfalls:** unbounded growth (no TTL), predictable sequential ids (security), collisions.

## Related
Track C URL-shortener system design.
