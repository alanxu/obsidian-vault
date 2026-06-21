---
title: In-Memory Key-Value Database
slug: in-memory-key-value-database
type: multi-level-stateful
leetcode: null
companies: [Anthropic, OpenAI, Meta, Dropbox, Coinbase, Cohere, Netflix, Capital One, "The Trade Desk", Roblox]
difficulty: ★★★★☆
frequency: very-high
formats: [OA·ICA, Live, Take-home]
levels: 4
time-box: 90 min for 4 levels
tags: [oo-design, ttl, time-travel, backup-restore, design-for-extension, append-only, bisect]
related: ["[[02-banking-system]]", "[[07-versioned-time-based-kv-store]]", "[[practical-oo-coding-deep-guide]]"]
---

# In-Memory Key-Value Database ⭐⭐

> *The* canonical multi-level "stateful service" problem. Records = `key → {field: value}`. The whole game is **designing Level 1 so Levels 3–4 bolt on without a rewrite.** Companies have been circulating variants since 2019; treat this as table stakes.

## Problem (by level)

The database stores **records**. A record is identified by a string `key`. Each record contains any number of **fields**, where a field is a `field-name → value` mapping. All values are strings.

### L1 — Core CRUD
Implement four methods, **in this exact signature** (the grader checks return types):
- `set(key: str, field: str, value: str) -> None`
- `get(key: str, field: str) -> str` — return the value, or `""` (empty string) if the field doesn't exist.
- `delete(key: str, field: str) -> str` — return `"true"` if a field was removed, `"false"` if there was nothing to delete.

> **Design note — why L1 writes at `ts=0`:** L1 (`set`/`get`/`delete`) and L3 (`set_at`/`get_at`) are *separate API families*; the grader uses one per scenario and never interleaves them. Writing L1 at the fixed sentinel `ts=0` lets L1 reuse the L3 version-list engine (no second code path) **and stays deterministic** — a wall clock (`time.time()`) would make the auto-grader flaky. A value set at 0 *is* still returned by `get_at(ts)` for any `ts ≥ 0` (it's the latest version with `set_ts ≤ ts`); it only gets shadowed if you interleave the two families, which the spec doesn't. If you ever need genuinely unified semantics, use a **logical auto-increment counter** (`self._clock += 1` per write) rather than `now()` — deterministic, monotonic, and immune to clock skew.

### L2 — Scan / filter
- `scan(key: str) -> str` — return **all fields of a record** formatted as `"field1(value1), field2(value2), …"` **sorted alphabetically by field name**. If the record has no fields, return `""`.
- `scan_by_prefix(key: str, prefix: str) -> str` — same, but only include fields whose name starts with `prefix`. Empty result ⇒ `""`.

### L3 — Time + TTL
Replace the simple CRUD set with timestamped versions and add TTL (time-to-live):
- `set_at(key, field, value, ts)` — write a version at timestamp `ts` (no expiry).
- `set_at_with_ttl(key, field, value, ts, ttl)` — write a version at `ts` that is alive in the half-open interval `[ts, ts + ttl)`.
- `get_at(key, field, ts)` — return the value of the latest version with `set_ts ≤ ts` that is still alive at `ts`, or `""`.
- `delete_at(key, field, ts)` — tombstone at `ts`.
- `scan_at(key, ts)` and `scan_by_prefix_at(key, prefix, ts)` — same as L2 but evaluated at `ts`.

> **Half-open TTL convention is the silent killer:** a field set at `ts=10` with `ttl=5` is **alive** at `ts=14`, **dead** at `ts=15`. Confirm the convention by dry-running example tests — Anthropic's spec uses half-open.

### L4 — Backup / Restore (the culmination)
- `backup(ts) -> int` — snapshot the **current state evaluated at `ts`** and return the count of records that have **at least one live field**. Each field stores its **remaining** TTL (not the original TTL).
- `restore(ts, ts_to_restore)` — discard current state and restore from the latest backup whose snapshot-time `≤ ts_to_restore`. After restore, all TTLs resume relative to the **new current `ts`** (i.e. a field whose remaining TTL was 7 at backup time will expire `ts + 7` after restore).

> **Clarify — `ts` earlier than a field's create-time:** `backup(ts)` is a time-travel read of the world *as of `ts`*, so a field whose `set_ts > ts` **doesn't exist yet → excluded** (and a record counts only if ≥1 field was created at/before `ts` and is still alive at `ts`). No special case needed — it falls out of the "latest version with `set_ts ≤ ts`" rule: `bisect_right(set_ts_list, ts) − 1 = −1` ⇒ `None`. (Likewise `restore`'s `ts_to_restore` earlier than the first backup ⇒ no matching backup ⇒ no-op; clarify whether that should instead clear state.)

## Core approach (format-agnostic)

**The single insight that unlocks all four levels:** store, per `(key, field)`, an **append-only sorted list of `(set_ts, value, expire_at|None)`** triples. Every other operation is a derived view of that list.

```
get / get_at   = bisect_right for largest set_ts ≤ ts, then check expire_at > ts
set / set_at   = append a triple
delete          = append a tombstone triple (empty value, expire_at = ts)
scan            = gather live fields at ts, sort, format
backup          = walk every record at ts, snapshot (value, remaining_ttl)
restore         = replace state, re-append versions with shifted TTLs
```

This primitive gives you **one structure that serves every level** — no rewrite at L3, no rewrite at L4. The alternative (separate "live" dict + history list) forces a refactor at L3 and a second one at L4. **Memorize the version-list primitive.**

### Worked Python solution

```python
import bisect

class InMemoryDB:
    def __init__(self):
        # key -> field -> list of (set_ts, value, expire_at|None), sorted by set_ts
        self._d = {}
        # list of (backup_ts, {key -> {field -> (value, remaining_ttl|None)}})
        self._backups = []

    # ---------- internal helpers ----------
    def _versions(self, key, field):
        return self._d.setdefault(key, {}).setdefault(field, [])

    def _active(self, key, field, ts):
        v = self._d.get(key, {}).get(field)
        if not v:
            return None
        ts_list = [x[0] for x in v]
        i = bisect.bisect_right(ts_list, ts) - 1
        if i < 0:
            return None
        _, val, exp = v[i]
        if exp is not None and exp <= ts:
            return None        # expired (half-open)
        return val

    def _put(self, key, field, value, ts, exp):
        self._versions(key, field).append((ts, value, exp))

    @staticmethod
    def _fmt(d):
        return ", ".join(f"{f}({d[f]})" for f in sorted(d))

    def _live_fields(self, key, ts):
        out = {}
        if key not in self._d:
            return out
        for f in self._d[key]:
            v = self._active(key, f, ts)
            if v is not None:
                out[f] = v
        return out

    # ---------- L1 ----------
    def set(self, key, field, value):
        self._put(key, field, value, 0, None)

    def get(self, key, field):
        return self._active(key, field, 0) or ""

    def delete(self, key, field):
        if self._active(key, field, 0) is None:
            return "false"
        self._put(key, field, "", 0, 0)
        return "true"

    # ---------- L2 ----------
    def scan(self, key):
        return self._fmt(self._live_fields(key, 0))

    def scan_by_prefix(self, key, prefix):
        return self._fmt({f: v for f, v in self._live_fields(key, 0).items()
                          if f.startswith(prefix)})

    # ---------- L3 ----------
    def set_at(self, key, field, value, ts):
        self._put(key, field, value, ts, None)

    def set_at_with_ttl(self, key, field, value, ts, ttl):
        self._put(key, field, value, ts, ts + ttl)

    def get_at(self, key, field, ts):
        return self._active(key, field, ts) or ""

    def delete_at(self, key, field, ts):
        self._put(key, field, "", ts, ts)

    def scan_at(self, key, ts):
        return self._fmt(self._live_fields(key, ts))

    def scan_by_prefix_at(self, key, prefix, ts):
        return self._fmt({f: v for f, v in self._live_fields(key, ts).items()
                          if f.startswith(prefix)})

    # ---------- L4 ----------
    def backup(self, ts):
        snap, count = {}, 0
        for k in self._d:
            live = {}
            for f in self._d[k]:
                v = self._active(k, f, ts)
                if v is None:
                    continue
                # pull expire_at from the same version we just used
                vlist = self._d[k][f]
                _, _, exp = vlist[bisect.bisect_right([x[0] for x in vlist], ts) - 1]
                remaining = (exp - ts) if exp is not None else None
                live[f] = (v, remaining)
            if live:
                snap[k] = live
                count += 1
        self._backups.append((ts, snap))
        return count

    def restore(self, ts, ts_to_restore):
        candidates = [b for b in self._backups if b[0] <= ts_to_restore]
        if not candidates:
            return
        _, snap = max(candidates, key=lambda b: b[0])
        # Wipe and replay
        self._d = {}
        for k, fields in snap.items():
            for f, (val, remaining) in fields.items():
                new_exp = (ts + remaining) if remaining is not None else None
                self._put(k, f, val, ts, new_exp)
```

**Complexity.** `set` / `delete`: O(1) amortized (list append). `get`: O(log V) per cell where V is versions-per-cell (typically tiny). `scan`: O(F log F) where F is fields per record. `backup`: O(K · F · log V). `restore`: O(K · F). Memory is O(total versions written) — append-only, so it grows unboundedly; a senior follow-up is to compact expired versions on snapshot.

## By format

### OA · ICA (CodeSignal, 4 levels, auto-graded, 90 min) — *most common channel*
- **How it appears:** levels unlock sequentially; hidden tests per level; you keep one codebase that must keep passing earlier levels.
- **The "follow-ups" are the later levels** — there is no interviewer to add more; unlocking L4 is the bar.
- **Time budget** (rule of thumb): L1 ~15 min, L2 ~15 min, L3 ~25 min, L4 ~25 min, ~10 min reserve for debugging. Don't perfect L1.
- **Tips:**
  - Design for L4 **at L1** (append-only version list, not value-only dict). It is the single highest-leverage move.
  - Submit & re-run hidden tests **per level**. Don't accumulate bugs across levels.
  - Match output **exactly**: field order sorted alphabetically, `field(value)` format, empty result is `""` not `"None"` or `null`.
  - Keep a **1-line smoke test** at the top of the file you run after every change: set / get / delete / scan / scan_by_prefix / TTL expiry / backup / restore.
- **Pitfalls:**
  - **Half-open TTL off-by-one** — most common spec violation. Test `set_at_with_ttl(k,f,v,10,5)` then `get_at(k,f,15)` ⇒ `""`.
  - **Breaking earlier levels** when adding L3/L4 — re-run their hidden tests after each level.
  - `restore` **replaces** state (does not merge).
  - `backup` stores **remaining** TTL (not absolute `expire_at`) — the restore semantics hinge on this.
  - Returning the wrong type (Python `False` vs the spec's `"false"` string).

### Live · CoderPad (human, narrate)
- **How it appears:** usually L1–L2 live in ~25 min, then the interviewer **adds follow-ups verbally** in the last 30–35 min.
- **Follow-ups (real, reported):**
  - **Thread safety** — wrap in `threading.RLock`. Discuss `RLock` vs `Lock` (reentrancy when methods call each other).
  - **Persistence with no `json`/`pickle`** — design a length-prefixed or delimiter-escaped format and hand-write the parser. Define the format on the whiteboard before coding.
  - **Lazy vs background expiry sweep** — `O(1) get` with lazy deletion, or a sweeper thread that compacts.
  - **Compaction** — at L4 you'll see memory grow; offer to drop expired versions on snapshot or under a memory threshold.
  - **Snapshot the whole history** vs **diff against previous backup** — bandwidth / I/O trade-off.
  - **Bulk imports** — `multi_set(keys, fields)` transactional semantics (all or nothing).
- **Tips:**
  - State the version-list interface **before** writing code; draw the data structure on the shared doc.
  - Write 2–3 test calls and **narrate** the expected output as you go.
  - When asked about thread safety, **say why** the lock is needed, not just that you'll add one.
  - Be ready to be interrupted at L1 and have a clean abstraction so you can extend.
- **Pitfalls:**
  - Over-engineering L1 (premature optimization with locks, classes, persistence) — costs you time on the levels that unlock later.
  - Silent failure when an L1 hack blocks the verbal L3/L4 extension (e.g., overwriting instead of versioning).
  - Caching or memoization that breaks TTL semantics.

### Take-home / timed async (Anthropic-style 90-min)
- **How it appears:** same 4-level problem, async/proctored; you self-check (no visible hidden tests).
- **Tips:**
  - **Reason out your own edge cases** — no grader to lean on. Empty inputs, TTL boundary, restore-then-modify.
  - Add a tiny `if __name__ == "__main__":` block with smoke tests.
  - Leave a one-line note on assumptions (TTL half-open, restore semantics) if a README is allowed.
  - Resist the urge to polish L1 — getting to L3 is worth more than a perfect L1.
- **Pitfalls:**
  - Running out of time polishing L1 instead of unlocking L3/L4.
  - No tests for the L4 backup/restore interaction with TTL.
  - Implicit assumptions not documented.

### Onsite · NR (Google-style, non-runnable)
- **How it appears:** rare for this problem, but if it appears, you'll write it by hand in a shared editor.
- **Tips:** Write the **whole version-list class**; trace `backup` → `restore` on a 2-record example aloud; explicitly state the half-open TTL convention.
- **Pitfalls:** Forgetting the in-place `restore` semantics; off-by-one in `_active` indexing.

### Whiteboard (when asked to "design the data model")
- **Tips:** Draw three boxes (key-indexed dict, field-indexed dict, append-only version list) and label every operation's path through them. Cite complexity per op.
- **Pitfalls:** Drifting into "how would you shard this across machines?" — that's Track C territory, not the question.

## Company variants

- **Anthropic (canonical)** — `SEND_MESSAGE_WITH_EXPIRY` / `ZIP/UNZIP_MESSAGES` / `LIST_MESSAGES_AT` (a chat-log reskin); also a **file-compression** L4 (gzip in-memory); and the circulated "bank with transactions" (see Q02).
- **OpenAI (P6 in their bank)** — `SET key value [EX seconds]`, `SCAN prefix`, `BACKUP/RESTORE ts`. The follow-ups add thread safety + custom file persistence.
- **Cohere** — smaller "tiny in-memory KV with TTL" live; L1–L2 only.
- **Meta / Dropbox** — full 4-level version; Dropbox sometimes asks for capacity/quotas at L3.
- **Coinbase / Capital One / The Trade Desk** — fintech skin: balance snapshots, audit-trail semantics.
- **Netflix** — "rate-limit state per user" reskin of L2/L3.
- **Roblox** — game-state-snapshot reskin.

## Worked example trace (for narration)

```
ts=0  set("u1","name","alice")          # _d["u1"]["name"] = [(0,"alice",None)]
ts=5  set_at("u1","name","alicia",5)    # _d["u1"]["name"] = [(0,"alice",None),(5,"alicia",None)]
ts=10 get_at("u1","name",7)             # bisect_right([0,5],7)=2, i=1 -> "alicia"
ts=15 set_at_with_ttl("u1","tok","abc",15,10)  # exp=25
ts=30 get_at("u1","tok",30)             # 25 <= 30 -> None -> ""
```

## Related
[[02-banking-system]] (sibling ICA, time-ordered ops) · [[07-versioned-time-based-kv-store]] (the core primitive isolated) · [[03-inventory-warehouse-management]] · [[04-cloud-storage-file-host]] · [[practical-oo-coding-deep-guide]] §4 (worked tests).