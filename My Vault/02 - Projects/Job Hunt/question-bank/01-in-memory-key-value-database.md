---
title: In-Memory Key-Value Database
slug: in-memory-key-value-database
type: multi-level-stateful
leetcode: null
companies: [Anthropic, OpenAI, Meta, Dropbox, Coinbase, Cohere, Netflix, Capital One, "The Trade Desk"]
difficulty: ★★★★☆
frequency: very-high
formats: [OA·ICA, Live, Take-home]
levels: 4
time-box: 90 min for 4 levels
tags: [oo-design, ttl, time-travel, backup-restore, design-for-extension]
related: ["[[02-banking-system]]", "[[07-versioned-time-based-kv-store]]", "[[practical-oo-coding-deep-guide]]"]
---

# In-Memory Key-Value Database ⭐⭐

> *The* canonical multi-level "stateful service" problem. Records = `key → {field: value}`. The whole game is **designing Level 1 so Levels 3–4 bolt on without a rewrite.**

## Problem (by level)
- **L1 — core:** `set(key, field, value)`; `get(key, field)` → value or `""`; `delete(key, field)` → `"true"/"false"`.
- **L2 — scan/filter:** `scan(key)` → `"field(value), …"` sorted by field; `scan_by_prefix(key, prefix)`.
- **L3 — time + TTL:** `set_at`, `set_at_with_ttl(key, field, value, ts, ttl)`, `get_at`, `delete_at`, `scan_at`, `scan_by_prefix_at`. Field alive in half-open `[ts, ts+ttl)`.
- **L4 — culmination:** `backup(ts)` → count of non-empty records (preserving each field's **remaining** TTL); `restore(ts, ts_to_restore)` → restore latest backup ≤ `ts_to_restore`; TTLs resume relative to `ts`.

## Core approach (format-agnostic)
**Append-only version list per `(key, field)`**: `(set_ts, value, expire_at|None)` sorted by `set_ts`. `get` = binary-search rightmost version ≤ query ts, then check `expire_at`. One structure serves L1 (ts=0), L3 (real ts + TTL), L4 (time-travel + remaining-TTL backup). *Memorize this primitive.* Complexity: `set` O(1) amortized, `get` O(log n)/cell, `scan` O(F log F).

```python
import bisect
class InMemoryDB:
    def __init__(self): self._d={}; self._b=[]
    def _active(self,k,f,ts):
        v=self._d.get(k,{}).get(f)
        if not v: return None
        i=bisect.bisect_right([x[0] for x in v],ts)-1
        if i<0: return None
        _,val,exp=v[i]
        return None if (exp is not None and exp<=ts) else val
    def _put(self,k,f,val,ts,exp): self._d.setdefault(k,{}).setdefault(f,[]).append((ts,val,exp))
    def set(self,k,f,v): self._put(k,f,v,0,None)
    def get(self,k,f): return self._active(k,f,0) or ""
    def delete(self,k,f):
        if self._active(k,f,0) is None: return "false"
        self._put(k,f,"",0,0); return "true"
    def _live(self,k,ts): return {f:self._active(k,f,ts) for f in self._d.get(k,{}) if self._active(k,f,ts) is not None}
    def scan(self,k): return self._fmt(self._live(k,0))
    def scan_by_prefix(self,k,p): return self._fmt({f:v for f,v in self._live(k,0).items() if f.startswith(p)})
    @staticmethod
    def _fmt(d): return ", ".join(f"{f}({d[f]})" for f in sorted(d))
    def set_at(self,k,f,v,ts): self._put(k,f,v,ts,None)
    def set_at_with_ttl(self,k,f,v,ts,ttl): self._put(k,f,v,ts,ts+ttl)
    def get_at(self,k,f,ts): return self._active(k,f,ts) or ""
    def backup(self,ts):
        snap,n={},0
        for k in self._d:
            live={}
            for f in self._d[k]:
                val=self._active(k,f,ts)
                if val is None: continue
                _,_,exp=self._d[k][f][bisect.bisect_right([x[0] for x in self._d[k][f]],ts)-1]
                live[f]=(val,(exp-ts) if exp is not None else None)
            if live: snap[k]=live; n+=1
        self._b.append((ts,snap)); return n
    def restore(self,ts,ttr):
        c=max((b for b in self._b if b[0]<=ttr),default=None,key=lambda b:b[0])
        if not c: return
        self._d={}
        for k,fs in c[1].items():
            for f,(val,rem) in fs.items(): self._put(k,f,val,ts,(ts+rem) if rem is not None else None)
```
Full tested version: [[practical-oo-coding-deep-guide]] §4.

## By format

### OA · ICA (CodeSignal, 4 levels, auto-graded, 90 min) — *most common channel*
- **How it appears:** levels unlock sequentially; hidden tests per level; you keep one codebase that must keep passing earlier levels.
- **The "follow-ups" are the later levels** — there's no interviewer to add more; unlocking L4 is the bar.
- **Tips:** design for L4 at L1 (versioned storage); submit & re-run hidden tests per level; match output **exactly** (sorted, `field(value)`); budget ~12/18/25/30 min.
- **Pitfalls:** half-open TTL off-by-one; **breaking earlier levels** with an L3/L4 change (re-run their tests); restore **replaces** state; backup stores **remaining** not absolute TTL.

### Live · CoderPad (human, narrate)
- **How it appears:** usually L1–L2 live, then the interviewer **adds follow-ups verbally**.
- **Follow-ups:** thread safety (`RLock`), persistence with **no `json`/`pickle`**, lazy-expire vs background sweep.
- **Tips:** state the version-list interface **before** coding; write 2–3 test calls and narrate them.
- **Pitfalls:** over-engineering L1; silent failure when an L1 hack blocks the verbal L3/L4 extension.

### Take-home (Anthropic 90-min timed assessment)
- **How it appears:** same 4-level problem, async/proctored; you self-check (no visible hidden tests).
- **Tips:** reason out your **own** edge cases (no grader to lean on); leave a one-line note on assumptions if a README is allowed.
- **Pitfalls:** running out of time polishing L1 instead of unlocking later levels.

## Company variants
Anthropic — `SEND_MESSAGE_WITH_EXPIRY` / `ZIP/UNZIP_MESSAGES` / `LIST_MESSAGES_AT`, or file compression at L4; also the circulated "bank with transactions." OpenAI (P6) — `SET key value [EX seconds]`, `SCAN prefix`, `BACKUP/RESTORE ts`. Cohere — smaller "tiny in-memory KV with TTL," live.

## Related
[[02-banking-system]] (other dominant ICA) · [[07-versioned-time-based-kv-store]] (the core primitive) · [[03-inventory-warehouse-management]] · [[04-cloud-storage-file-host]].
