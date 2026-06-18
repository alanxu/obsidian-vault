---
title: Versioned / Time-Based Key-Value Store
slug: versioned-time-based-kv-store
type: multi-level-stateful
leetcode: 981
companies: [OpenAI, Databricks]
difficulty: ★★★☆☆
frequency: high
formats: [Live, OA·GCA/HR]
levels: 4
time-box: live 45 min
tags: [oo-design, versioning, binary-search, thread-safety, serialization]
related: ["[[01-in-memory-key-value-database]]", "[[openai-interview-guide]]"]
---

# Versioned / Time-Based Key-Value Store ⭐

The purest expression of the Track B core primitive. OpenAI's most-reported coding problem; also LeetCode **#981**. Master this and the historical levels of Q01/Q02 fall out for free.

## Problem
- `put(key, value)` → auto-increment version (start 1), returns it; `get(key, version=None)` → value at that version or **latest ≤** requested; latest if `None`.
- **#981 variant:** `set(key, value, timestamp)` / `get(key, timestamp)`.

## Core approach (format-agnostic)
Per key, a **sorted list of `(version|ts, value)`**; `get` = `bisect_right` for largest ≤ requested, index−1. Append-only ⇒ O(1) writes, O(log n) reads. *This is the "append-only version list + binary search by timestamp" primitive.* Code (incl. persistence + locking): [[openai-interview-guide]] Problem 1.

## By format

### Live · CoderPad (human) — *primary (OpenAI)*
- **How it appears:** base in 10 min, then a chain of follow-ups — this question is **mostly its follow-ups**.
- **Follow-ups:** real **strictly-increasing timestamps** (block `put` via `threading.Condition`, inject a `clock` for tests); **thread safety** (`RLock`); **file persistence with no `json`/`pickle`** (length-prefixed / `|`-escaped records + hand parser).
- **Tips:** get the binary search right first; for serialization, define the record format out loud before coding.
- **Pitfalls:** `bisect` off-by-one (largest ≤, not <), same-timestamp ties, escaping the delimiter in custom serialization.

### OA · GCA / HackerRank (#981, auto-graded)
- **How it appears:** the plain #981 — `set`/`get` with timestamps, hidden tests.
- **Tips:** clean bisect; handle "timestamp before any set" → `""`.
- **Pitfalls:** linear scan instead of binary search (TLE on large inputs).

## Company variants
OpenAI's top-reported bank problem (with the persistence/threading follow-ups); LeetCode #981 reported at Databricks. Underlies Q01, Q02-L4, Q04 history.

## Related
[[01-in-memory-key-value-database]] (multi-level superset) · [[openai-interview-guide]] P1.
