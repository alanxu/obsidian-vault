---
title: Versioned / Time-Based Key-Value Store
slug: versioned-time-based-kv-store
type: multi-level-stateful
leetcode: 981
companies: [OpenAI, Databricks, Snowflake, Anthropic, Cohere, Stripe-events, "AWS DynamoDB versions"]
difficulty: ★★★☆☆
frequency: high
formats: [Live, OA·GCA/HR]
levels: 4
time-box: live 45 min
time-box-oa: 25 min
tags: [oo-design, versioning, binary-search, thread-safety, serialization, persistence]
related: ["[[01-in-memory-key-value-database]]", "[[openai-interview-guide]]", "[[02-banking-system]]"]
---

# Versioned / Time-Based Key-Value Store ⭐

The **purest expression** of the Track B core primitive. OpenAI's most-reported coding problem; also LeetCode **#981**. Master this and the historical levels of Q01/Q02 fall out for free. The question itself is mostly its **follow-ups** — base is 10 minutes; the rest is thread-safety, persistence, and timestamps.

## Problem

Two signatures you'll see:

**Version-based (OpenAI's default):**
- `put(key, value) -> int` — auto-increment version (start 1), return it.
- `get(key, version=None) -> value | None` — value at that version, or the **latest version ≤ requested** if `version` is provided, or latest if `None`.

**Timestamp-based (LeetCode #981):**
- `set(key, value, timestamp)` — write at timestamp.
- `get(key, timestamp) -> value | ""` — value at the latest timestamp `≤` requested.

The two are isomorphic — version is just a monotonically-increasing-integer timestamp. Most interviewers let you pick either and stick with it.

## Core approach (format-agnostic)

**One primitive, all levels:**
- Per key, store a **sorted list of `(version|ts, value)`**.
- `get` = `bisect_right(versions, requested)` to find the insertion point, index − 1 is the answer.
- Append-only ⇒ O(1) writes, O(log n) reads.
- Identity = `(key, version)` makes restore / persistence straightforward.

This is **the same primitive as Q01 / Q07's history** — once you see it, the multi-level Q01 is a generalization to records/fields and the Q02 banking history is a per-account version list.

### Worked Python solution (with thread safety + persistence)

```python
import bisect
import threading

class KVStore:
    def __init__(self, persist_path=None):
        self._store = {}                 # key -> [(ts, value)]
        self._lock = threading.RLock()
        self._last_ts = 0
        self.persist_path = persist_path

    def put(self, key, value, ts=None):
        with self._lock:
            if ts is None:
                ts = self._last_ts + 1
            self._last_ts = max(self._last_ts, ts)
            self._store.setdefault(key, []).append((ts, value))
            return ts

    def get(self, key, ts=None):
        with self._lock:
            if key not in self._store:
                return None
            versions = self._store[key]
            if not versions:
                return None
            if ts is None:
                return versions[-1][1]
            keys = [v for v, _ in versions]
            i = bisect.bisect_right(keys, ts) - 1
            if i < 0:
                return None
            return versions[i][1]

    # ---------- persistence (no json / no pickle) ----------
    def save(self, path=None):
        path = path or self.persist_path
        if not path:
            return
        with self._lock, open(path, "w") as f:
            for key, versions in self._store.items():
                for ts, val in versions:
                    f.write(self._encode(key, ts, val))

    @staticmethod
    def _encode(key, ts, val):
        # length-prefixed records: 4-byte big-endian ts, then key/val as
        # escaped UTF-8 with our own delimiter.
        # Format: <ts>|<escaped key>|<escaped val>\n
        return f"{ts}|{key.replace('|', '\\|')}|{val.replace('|', '\\|').replace(chr(10), '\\n')}\n"

    def load(self, path=None):
        path = path or self.persist_path
        if not path:
            return
        with self._lock:
            self._store.clear()
            with open(path) as f:
                for line in f:
                    ts, key, val = self._decode_line(line.rstrip("\n"))
                    self._store.setdefault(key, []).append((ts, val))

    @staticmethod
    def _decode_line(line):
        # Naive split is wrong if '|' appears in values — write a real parser.
        parts, buf, escaped = [], [], False
        for ch in line:
            if escaped:
                buf.append(ch); escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == "|":
                parts.append("".join(buf)); buf = []
            else:
                buf.append(ch)
        parts.append("".join(buf))
        ts = int(parts[0]); key, val = parts[1], parts[2]
        return ts, key, val.replace("\\n", "\n")
```

**Complexity.** `put` O(1) amortized; `get` O(log n); `save`/`load` O(total entries).

## By format

### Live · CoderPad (human) — *primary (OpenAI)*
- **How it appears:** base in 10 min, then a chain of follow-ups — this question is **mostly its follow-ups**.
- **Follow-ups (real, reported, in order of likelihood):**
  1. **Real timestamps** — strictly-increasing via `threading.Condition`; `put` blocks until `ts > last_ts`.
  2. **Inject a `clock`** — replace `time.time()` with a callable parameter; default `time.time`, override in tests with a counter.
  3. **Thread safety** — `threading.RLock` (re-entrant, in case methods call each other) vs `threading.Lock` (faster, non-re-entrant).
  4. **File persistence** with **no `json`/`pickle`** — length-prefixed records, delimiter-escaped values, hand-rolled parser. Define the format on the whiteboard first.
  5. **Snapshot + restore** — pickling or a custom dump; restore re-creates the sorted structure.
  6. **TTL on values** — each value has an expiry; same `_active` logic as Q01 L3.
  7. **Range scan** — `scan(key, ts_start, ts_end)` returns the history in a window.
  8. **Memory compaction** — drop versions older than some horizon; rebuild on demand.
  9. **`delete(key, ts)` semantics** — tombstone version (get_at before the delete still works) vs hard delete (history gone) — mirrors Q01's tombstone; interviewer wants you to *ask* which.
  10. **Write-ahead durability** — append each `put` to the file *before* acking (fsync tradeoff), vs save-on-demand: crash-consistency question that bridges to the distributed bank.
- **Tips:**
  - Get the **bisect right first**; verify with `put(a,1) put(a,2) put(a,3) get(a,1)` → 1.
  - For thread safety: **state the lock choice** (`RLock` for re-entrancy, `Lock` otherwise).
  - For serialization: **define the record format out loud** before coding (length-prefix vs delimited, escape rules, byte vs str).
  - For timestamps: `threading.Condition` + a `clock` injection — the testability point is what they're really grading.
- **Pitfalls:**
  - `bisect` **off-by-one** (largest ≤, not <). Trace `get(ts=before any put)` → `None`.
  - Same-timestamp ties — last-wins is the usual spec; confirm.
  - Escaping the delimiter in custom serialization (the naive `split('|')` fails if values contain `|`).
  - `RLock` deadlock if a thread re-acquires after raising; prefer `Lock` when methods don't call each other.
  - Persistence ordering — versions must be re-loaded in order so the bisect stays sorted.

### OA · GCA / HackerRank (#981, auto-graded)
- **How it appears:** plain #981, `set`/`get` with timestamps, hidden tests.
- **Tips:**
  - Clean bisect; verify with empty key, future ts, past ts.
  - `""` for missing or "before any set" — confirm from examples.
  - TLE guards: avoid linear scans, avoid `key in store` followed by `store[key]` (one lookup).
- **Pitfalls:**
  - Linear scan instead of binary search (TLE on large inputs).
  - Off-by-one on `≤` vs `<` at the boundary.
  - Storing timestamps as strings (sort lexicographically wrong).

### Onsite · NR (Google-style, non-runnable)
- **Tips:** Write the version-list class with persistence stub; trace put/get/save/load on a 3-key example aloud.
- **Pitfalls:** Persistence format not defined; the question is really a design conversation.

## Company variants

- **OpenAI (canonical)** — top-reported bank problem (with the persistence + threading + timestamp-condition follow-ups).
- **Databricks / Snowflake** — Delta Lake time-travel reskin.
- **Anthropic** — same primitive, often wrapped in Q01 L4 backup/restore.
- **Cohere** — small base + thread safety only.
- **Stripe events / AWS DynamoDB versions** — production-flavored reskin.

## Worked example trace

```
put("a", "v1")    → 1   ; store["a"] = [(1,"v1")]
put("a", "v2")    → 2   ; store["a"] = [(1,"v1"),(2,"v2")]
get("a")          → "v2"
get("a", 1)       → "v1"    ; bisect_right([1,2], 1)=1 → idx 0
get("a", 0)       → None    ; bisect_right([1,2], 0)=0 → idx -1
get("missing")    → None
```

## Related
[[01-in-memory-key-value-database]] (multi-level superset) · [[02-banking-system]] (per-account version list at L4) · [[openai-interview-guide]] P1.