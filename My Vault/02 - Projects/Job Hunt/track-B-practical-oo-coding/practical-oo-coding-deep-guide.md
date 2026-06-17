---
tags: [job-hunt, interview-prep, track-b, oo-coding, practical-coding, codesignal]
track: "Track B — Practical / OO coding"
plan-section: "§3"
parent: [[interview-prep-master-plan-2026]]
created: 2026-06-16
covers: [company-formats, problem-bank, multi-level-problems, worked-solution, tips]
---

# Track B — Practical / OO Coding: Deep Guide

> The frontier-lab favorite. Not LeetCode puzzles — you **build one stateful object and extend it across 3–6 escalating levels** without breaking earlier levels. Tests clean abstractions, incremental design, edge-case discipline, and stdlib fluency. Companion to [[practical-oo-coding/README]], builds on [[openai-interview-guide]] (8-problem bank w/ code) and [[anthropic-interview-guide]] (live bank w/ code).

---

## 1. What this round actually is

A single, **domain-flavored, project-based problem** (an in-memory DB, a bank, a file system, a credit ledger) delivered in **progressive levels**. Level 1 is trivial CRUD; each later level layers on filtering, time/TTL, history, or persistence. The grader (or interviewer) runs hidden tests per level, and **levels unlock only when the prior level passes**.

**Why labs/fintech love it over LeetCode:**
- It looks like real work (a service with an API), so it predicts on-the-job ability better than graph trivia.
- It rewards **clean, extensible design** — the people who structure Level 1 well breeze through Level 4; the people who hack Level 1 get stuck.
- It's **self-scaling difficulty**: weak candidates clear L1–2, strong ones clear L4.

**What they grade (in priority order):** correctness per level → clean/extensible structure → edge-case handling → speed → communication. *Unlocking Level 4 beats perfecting Level 1.*

---

## 2. The formats different companies use ("the rules")

Same archetype, different delivery. Know which one you're walking into.

| Company                     | Platform / mode                            | Format                                                       | Time                      | Graded by            | Notable rules                                                                                                                        |
| --------------------------- | ------------------------------------------ | ------------------------------------------------------------ | ------------------------- | -------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Anthropic**               | CodeSignal ICA (screen) **+ live** 4-level | 1 project, 4 levels                                          | 90 min (OA); ~60 min live | hidden tests + human | Bank is "circulated"; interviewers **alert to over-rehearsed** solutions → may swap in a fresh problem if a round is "inconclusive." |
| **OpenAI**                  | CoderPad live screen + **work-trial**      | 1 base problem + **progressive follow-ups** (up to ~6 parts) | 60 min screen             | human                | Adds **thread safety, file persistence with custom serialization (no `json`/`pickle`), async**.                                      |
| **Anysphere (Cursor)**      | CodeSignal-style OA + live                 | practical build                                              | ~60–90 min                | tests + human        | Fast, clean code; streaming/cancellation flavors.                                                                                    |
| **xAI**                     | CodeSignal (proctored)                     | tight algorithmic + practical                                | 60 min                    | auto                 | Very tight timing.                                                                                                                   |
| **Robinhood**               | CodeSignal OA                              | ~4 tasks easy→hard (GCA-style) + sometimes concurrency       | 90 min                    | auto                 | Reliability/fintech flavor; concurrency basics.                                                                                      |
| **Harvey**                  | Take-home or CodeSignal                    | practical AI-eng build                                       | varies                    | human                | Often LLM/agent-flavored.                                                                                                            |
| **Also use CodeSignal ICA** | —                                          | —                                                            | —                         | —                    | Netflix, Capital One, Meta, Dropbox, Coinbase, The Trade Desk.                                                                       |

### 2a. CodeSignal **Industry Coding Assessment (ICA)** — the dominant format
- **Structure:** exactly **1 domain-agnostic, project-based question with 4 progressive levels**. Requirements accumulate (L_n includes everything in L_{n-1}).
- **Time:** **90 minutes total**; you are *not* expected to finish all 4. Partial completion is normal and still scores.
- **Level shape (the reliable pattern):**
  - **L1 — basic implementation** of core operations + corner cases (CRUD on records/fields).
  - **L2 — data processing**: filtering, scanning, aggregation, export, ranking.
  - **L3 — time/TTL**: timestamped operations and time-to-live expiry.
  - **L4 — culmination**: look-back/history queries, or backup/restore, or merge — a substantial extension.
- **Mechanics:** levels **unlock sequentially** (must pass current to see next); you can re-run hidden tests anytime; you keep one codebase that must keep passing earlier levels.
- **Scoring:** weighted toward later levels; correctness on hidden tests + (for some) code-quality signal.

### 2b. CodeSignal **General Coding Assessment (GCA)** — don't confuse it with ICA
- **4 separate algorithmic questions** (≈2 easy, 1 medium, 1 harder), ~70 min, auto-graded. This is **Track A territory** (DSA), not the OO/project style. Some companies screen with GCA, then do the ICA/live OO round later.

### 2c. The live / human-proctored variant (Anthropic, OpenAI)
- Same multi-level problem, but a human watches you **narrate and design**. Here, **communication and extension-readiness are graded directly**. Follow-ups go deeper than the OA: thread safety, persistence, async, distribution.
- **Anti-memorization:** the well-known problems (in-memory DB, bank) are flagged as "circulated." Understand the *pattern* so you can handle a twist; reciting a memorized solution reads as a red flag.

### 2d. Take-home variant (Harvey, OpenAI work-trial, Together)
- Same idea, more time → higher bar on tests, README, and structure. See [[track-G-take-homes/README]].

**The common thread across all formats:** *build a stateful object, extend it across levels, never break earlier levels, narrate your interface before coding.*

### 2e. What it's actually like — OA vs live vs take-home, testing, and what "pass" means

This is the part candidates are most unsure about. The three settings feel very different:

| Dimension               | **OA** (CodeSignal ICA / GCA, async)                                              | **Live / onsite** (CoderPad, Zoom, Google editor)                                    | **Take-home**                                    |
| ----------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------------------ |
| Who grades you          | **Automated** — hidden test cases                                                 | **Human** interviewer(s) on a rubric                                                 | **Human** reviewer(s)                            |
| Are tests provided?     | **Yes** — a few example cases in the prompt + a hidden suite that sets your score | Sometimes a couple of example inputs; **often none**                                 | Usually just a spec                              |
| Do **you** write tests? | Optional self-check, **not graded**                                               | **Smart to write a few yourself** to verify — doing it unprompted is a strong signal | **Yes — expected and graded** as part of quality |
| Can you run code?       | Yes — "Run" against sample cases                                                  | CoderPad: yes. **Google onsite: often NO** (write compilable code by hand)           | Yes, on your machine                             |
| Level pacing            | Levels **unlock sequentially** (must pass to advance)                             | Interviewer paces it; **follow-ups added live** (thread-safety, async, persistence)  | All levels visible upfront                       |
| Proctoring              | Webcam + screen; no paste / tab-switch                                            | Camera on; narrate throughout                                                        | None                                             |
| What **"pass"** means   | A **company-set cut score**                                                       | A **holistic hire signal** (no number)                                               | Tests + README + design judgment                 |

**OA — how scoring & "pass" work.** CodeSignal auto-grades against **hidden test cases per level**. The ICA score is on a **200–600** scale (GCA historically 300–850), and it weighs **task difficulty × correctness on hidden tests × time efficiency**, with **partial credit** for passing some tests. The **pass bar is a confidential cut score each company sets** (and varies by role/candidate pool — e.g., reports of "≥X to advance"). Practical rule of thumb: **clearing Levels 1–3 cleanly is a solid pass at most companies; Level 4 is what separates top candidates.** You don't write tests — but you *do* run your code against the visible examples and should reason out edge cases yourself, because the hidden suite is checking exactly those.

**Live — how it's judged.** Usually **no auto-grader**. A human scores you on a rubric: problem-solving approach, correctness, **clean/extensible structure**, **communication (narration)**, edge-case handling, and **how you handle the live follow-ups**. The outcome is a calibrated **strong-hire / hire / lean / no-hire** signal, combined across interviewers — not a percentage. Here you typically **write your own quick test calls / driver code** to demonstrate correctness (or the interviewer hands you example inputs); volunteering a couple of edge-case checks reads as senior. On **Google's onsite editor you often can't execute** — so "testing" means **dry-running/tracing your code aloud and stating the assertions** that should hold.

**Take-home — how it's judged.** Humans review the repo; **tests are expected and graded** alongside the README and design. See [[track-G-take-homes/README]].

**By company (what to expect):**
- **Anthropic** — CodeSignal **ICA screen** (auto, hidden tests, cut score) → **live 4-level** (human, narrate, deep follow-ups, anti-memorization).
- **OpenAI** — **CoderPad live** (human rubric, progressive follow-ups: thread-safety, no-`json` persistence, async) + work-trial.
- **Robinhood / xAI** — **CodeSignal OA** first (auto cut score) → live coding.
- **Google** — Hiring Assessment + onsite in a **non-runnable** shared editor → write compilable code by hand, committee-reviewed.
- **Cohere / Harvey / Together** — **take-home**: you write tests; reviewed by humans on tests + README + design.

> **Bottom line on tests:** OA = tests come from the platform (you self-check, optionally). Live = you write a few yourself and narrate them. Google onsite = you can't run, so trace + assert. Take-home = full tests expected.

---

## 3. The concrete problem bank

### 3a. Multi-level "stateful service" problems (the core of this round)

Each is one object extended across levels. Specs below are the **commonly reported structures** (reconstruct, don't memorize verbatim).

**① In-memory key–value database** ⭐ — *the single most common ICA problem (Anthropic, Meta, Dropbox, Coinbase, …).* Records = `key → {field: value}`.
- **L1:** `set(key, field, value)`; `get(key, field)` → value or empty; `delete(key, field)` → true/false.
- **L2:** `scan(key)` → `"field(value), …"` sorted by field; `scan_by_prefix(key, prefix)` → same, prefix-filtered.
- **L3:** timestamped + TTL — `set_at`, `set_at_with_ttl(key, field, value, ts, ttl)`, `get_at`, `delete_at`, `scan_at`, `scan_by_prefix_at`. A field is alive in `[ts, ts+ttl)`.
- **L4:** `backup(ts)` → count of non-empty records (preserving each field's **remaining** TTL); `restore(ts, ts_to_restore)` → restore from latest backup ≤ `ts_to_restore`, TTLs resume relative to `ts`.
- *Full worked solution in §4.*

**② Banking system** ⭐ — *the other dominant ICA problem (fintech + general).* Accounts with balances + time-ordered ops.
- **L1:** `create_account(ts, id)`; `deposit(ts, id, amount)`; `transfer(ts, from, to, amount)` (respect insufficient funds).
- **L2:** `top_spenders(ts, n)` — top N accounts by total outgoing (transfers + payments), tie-break by id.
- **L3:** `pay(ts, id, amount)` with **scheduled cashback** (e.g., 2% refunded after a delay) + `get_payment_status(ts, id, payment_id)`; payments/cashbacks process in time order.
- **L4:** `merge_accounts(ts, id1, id2)` (combine balances + history); `get_balance(ts, id, time_at)` — **historical balance** at a past time.

**③ Inventory / warehouse management** — items with copies/duplicates.
- **L1:** `add_item`, `get_item`, `delete_item`. **L2:** `copy_item` (adds `.dupe`/`.copyN` suffix), `add_duplicate_items`. **L3:** capacity limits / TTL on items. **L4:** snapshot/restore or move-between-locations.

**④ Cloud storage / file host** — users, files, capacity.
- **L1:** `add_file(name, size)`, `get_file_size`, `delete_file`. **L2:** `get_n_largest` / by prefix. **L3:** **users with storage capacity**, `add_file_by(user, …)`, `merge_user`. **L4:** `backup_user`/`restore_user`, compression.

**⑤ Expiring credit ledger** ⭐ (OpenAI) — out-of-order events; consume earliest-expiring first. *Worked in [[openai-interview-guide]] Problem 4.*

**⑥ GPU credit manager** (OpenAI) — add/allocate/release/available + **idempotency** (dedupe by `request_id`). *OpenAI Problem 5.*

**⑦ Versioned / time-based KV store** ⭐ (OpenAI) — `put` auto-versions; `get(key, version)` binary-searches ≤ version; follow-ups: real timestamps (strictly increasing via `Condition`), thread safety, **custom file persistence (no json/pickle)**. *OpenAI Problem 1 — full code there.*

**⑧ Multi-file iterator** (OpenAI, 6 parts) — iterate lines across files, skip empties → resumable (save/restore state) → async → 2D/3D. *OpenAI Problem 2.*

**⑨ CD directory navigation** (OpenAI) — resolve `/`, `..`, `.`, `~`, then soft-links. *OpenAI Problem 3.*

**⑩ API log parser / token-usage aggregator** (OpenAI) — parse `user|endpoint|tokens|ts` lines, aggregate per user, sort; follow-ups: malformed lines, per-minute rate, streaming. *OpenAI Problem 8.*

### 3b. Anthropic live-coding bank (human-proctored; full solutions in [[anthropic-interview-guide]])
- **Multithreaded web crawler** ⭐ (their #1 live question) — BFS from seed, same-domain, dedupe; then `ThreadPoolExecutor` + thread-safe visited set; follow-ups: asyncio vs threads, **GIL**, per-host politeness, distribution.
- **Stack-trace → trace conversion** (viral 2025) — LCP-diff consecutive stack samples to emit start/end events; handle recursion.
- **Exclusive execution time from logs** (≈ LeetCode **#636**) — stack simulation; follow-up: out-of-order stream buffered with a heap + `max_delay`.
- **Find/eliminate duplicate files** (≈ LeetCode **#609**) — size → partial hash → full SHA-256 funnel; minimize I/O; chunked reads; hard-link mode.
- **LRU cache** (**#146**) — production-grade, thread-safe; variant: **find-the-bug** in a provided cache.

### 3c. LeetCode "Design"-tagged warm-up bank (build muscle for the pattern)
Core: **#146** LRU · **#460** LFU · **#981** Time-Based KV · **#380** Insert/Delete/GetRandom O(1) · **#1166** Design File System · **#588** In-Memory File System · **#211** Add/Search Word · **#359** Logger Rate Limiter · **#362** Hit Counter · **#1244** Leaderboard · **#1396** Underground System · **#535** TinyURL · **#2502** Memory Allocator · **#715** Range Module.

---

## 4. Fully worked example — In-Memory DB, all 4 levels

The teaching point isn't the answer — it's **designing Level 1 so Levels 3–4 bolt on**. Notice: one history list per `(key, field)` carries values, timestamps, and expiries, so the timed/TTL/backup levels reuse the same structure instead of rewriting it.

```python
import bisect
from typing import Optional

class InMemoryDB:
    def __init__(self):
        # key -> field -> list of versions, each: (set_ts, value, expire_at|None)
        # versions are append-only and sorted by set_ts → enables time-travel + TTL + backup
        self._data: dict[str, dict[str, list[tuple[int, str, Optional[int]]]]] = {}
        self._backups: list[tuple[int, dict]] = []   # (backup_ts, deep snapshot)

    # ---------- helpers (every level reuses these) ----------
    def _active_version(self, key, field, ts):
        """Latest version with set_ts <= ts that is not expired at ts."""
        versions = self._data.get(key, {}).get(field)
        if not versions:
            return None
        # binary search rightmost set_ts <= ts
        idx = bisect.bisect_right([v[0] for v in versions], ts) - 1
        if idx < 0:
            return None
        set_ts, value, expire_at = versions[idx]
        if expire_at is not None and expire_at <= ts:
            return None                      # expired
        return value

    def _put(self, key, field, value, ts, expire_at):
        self._data.setdefault(key, {}).setdefault(field, []).append((ts, value, expire_at))

    def _live_fields(self, key, ts):
        out = {}
        for field in self._data.get(key, {}):
            v = self._active_version(key, field, ts)
            if v is not None:
                out[field] = v
        return out

    # ---------- Level 1 (treat L1/L2 as ts=0 over the timed core) ----------
    def set(self, key, field, value):      self._put(key, field, value, 0, None)
    def get(self, key, field):             return self._active_version(key, field, 0) or ""
    def delete(self, key, field):
        if self._active_version(key, field, 0) is None:
            return "false"
        self._put(key, field, "", 0, 0)    # tombstone (expired immediately)
        return "true"

    # ---------- Level 2 (scan / prefix) ----------
    def scan(self, key):                   return self._format(self._live_fields(key, 0))
    def scan_by_prefix(self, key, prefix):
        fields = {f: v for f, v in self._live_fields(key, 0).items() if f.startswith(prefix)}
        return self._format(fields)

    @staticmethod
    def _format(fields):
        return ", ".join(f"{f}({fields[f]})" for f in sorted(fields))

    # ---------- Level 3 (timestamped + TTL) ----------
    def set_at(self, key, field, value, ts):              self._put(key, field, value, ts, None)
    def set_at_with_ttl(self, key, field, value, ts, ttl): self._put(key, field, value, ts, ts + ttl)
    def get_at(self, key, field, ts):                     return self._active_version(key, field, ts) or ""
    def delete_at(self, key, field, ts):
        if self._active_version(key, field, ts) is None:
            return "false"
        self._put(key, field, "", ts, ts)   # tombstone at ts
        return "true"
    def scan_at(self, key, ts):                           return self._format(self._live_fields(key, ts))
    def scan_by_prefix_at(self, key, prefix, ts):
        fields = {f: v for f, v in self._live_fields(key, ts).items() if f.startswith(prefix)}
        return self._format(fields)

    # ---------- Level 4 (backup / restore, preserving remaining TTL) ----------
    def backup(self, ts):
        snapshot, non_empty = {}, 0
        for key in self._data:
            live = {}
            for field in self._data[key]:
                versions = self._data[key][field]
                idx = bisect.bisect_right([v[0] for v in versions], ts) - 1
                if idx < 0:
                    continue
                set_ts, value, expire_at = versions[idx]
                if expire_at is not None and expire_at <= ts:
                    continue
                remaining = (expire_at - ts) if expire_at is not None else None
                live[field] = (value, remaining)   # store REMAINING ttl, not absolute
            if live:
                snapshot[key] = live
                non_empty += 1
        self._backups.append((ts, snapshot))
        return non_empty

    def restore(self, ts, ts_to_restore):
        # most recent backup with backup_ts <= ts_to_restore
        chosen = None
        for b_ts, snap in self._backups:
            if b_ts <= ts_to_restore and (chosen is None or b_ts >= chosen[0]):
                chosen = (b_ts, snap)
        if chosen is None:
            return
        self._data = {}                       # restore replaces current state
        for key, fields in chosen[1].items():
            for field, (value, remaining) in fields.items():
                expire_at = (ts + remaining) if remaining is not None else None
                self._put(key, field, value, ts, expire_at)   # TTLs resume relative to `ts`
```

**Narrate while building this:**
- "I'll store **per-(key,field) version history** from Level 1, even though L1 only needs the latest — because L3/L4 need time-travel and TTL, and I don't want to rewrite the core."
- "`get` is a binary search for the newest version ≤ the query timestamp; TTL is just an `expire_at` check on that version — so the timed level reuses the same lookup."
- "Backups store **remaining** TTL (not absolute expiry) so restore can resume them relative to the restore time — that's the subtle correctness point in Level 4."
- Edge cases to call out: delete of a missing field (`"false"`), expiry boundary is half-open `[ts, ts+ttl)`, scan ordering (sorted by field), restore replacing vs merging state.

> If you only memorize one design, memorize **"append-only version list per cell + binary search by timestamp."** It solves in-memory DB, versioned KV, historical bank balance, and any "value at time T" follow-up.

---

## 5. Tips & playbook (how to actually pass)

**Design**
- **Design Level 1 for Level 4.** Store richer state than L1 needs (records/versions/indices). The candidates who clear L4 are the ones who structured L1 well.
- **Small methods + private helpers.** Each level should add methods that *call* helpers, not copy logic. One `_active_version` helper unlocked three levels above.
- **State the interface out loud before coding** ("a record is key→field→versions; here are my methods").

**Execution**
- **Submit working code per level; re-run hidden tests continuously.** Don't write all four levels then debug.
- **Unlocking L4 > perfecting L1.** Partial-but-progressing beats polished-but-stuck. You're not expected to finish all 4 in 90 min.
- **Time-box:** roughly L1 ~12 min, L2 ~18, L3 ~25, L4 ~30, leaving buffer. If a level stalls, lock in what passes and move on.
- **Don't break earlier levels** — re-run their tests after each change (the #1 silent failure).

**Language & tooling**
- **Use Python**; know the stdlib cold: `bisect`, `heapq`, `collections` (`defaultdict`, `deque`, `OrderedDict`, `Counter`), `dataclasses`, string methods. Clean loop > clever one-liner.
- Practice in a **shared web editor** (CodeSignal practice, Replit, Colab) — not your IDE; no autocomplete, big monitor.

**Frequent follow-ups — be ready to add live**
- **Thread safety and concurrency:** wrap mutations in a lock. `Lock` (non-reentrant, faster) vs **`RLock`** (reentrant — needed when a locked method calls another locked method).
- **Persistence with custom serialization (no `json`/`pickle`):** length-prefixed or delimiter-escaped records; write a tiny parser. (OpenAI loves this.)
- **Async:** `async def`, `await`, `aiofiles`; same structure + `await`.
- **GIL:** I/O-bound (crawling) → threads help (GIL released on I/O); CPU-bound → multiprocessing/async.
- **Idempotency:** dedupe repeated requests by `request_id`.

**Anti-patterns / pitfalls**
- Mutating a dict while iterating it (snapshot keys or build a new dict).
- TTL off-by-one — confirm half-open `[ts, ts+ttl)`; lazy-expire on read vs periodic sweep.
- Reciting a memorized circulated solution — **labs detect it** and will swap in a fresh problem. Understand the pattern instead.
- Forgetting tie-breaks/sorting in scan/ranking outputs (graders check exact format).

**Edge-case checklist to narrate:** missing key/field, empty inputs, duplicate keys, expired-vs-deleted distinction, timestamp ties, out-of-order events, capacity/limit boundaries, restore replacing state, very large inputs (don't load whole files — chunk).

---

## 6. Drill plan (~12 hrs, fits master-plan budget)
1. **(2h) Pattern fluency** — solve **#146 LRU** and **#981 Time-Based KV** until automatic. These two encode 80% of the pattern.
2. **(3h) The canonical multi-level problem** — implement the **in-memory DB all 4 levels** from a blank file, timed 90 min. Then re-do it a week later cold.
3. **(2h) Banking system 4 levels** — the other dominant ICA problem; practice ranking (L2) + historical balance (L4).
4. **(2h) OpenAI bank** — work Problems 4–6 (expiring ledger, GPU credit, in-memory DB w/ persistence) from [[openai-interview-guide]]; add thread-safety + no-json serialization follow-ups.
5. **(2h) Anthropic live bank** — web crawler (single → multithreaded), #636 exclusive time, #609 duplicate files; narrate aloud / record yourself.
6. **(1h) Design-bank warm-ups** — #380, #1166, #460, #1244 for variety.
- **Re-drill only what you failed** (keep a log). Practice on **CodeSignal's own practice** + the community ICA practice repo (Sources).

---

## 6.5 How to practice on real questions (method + where to find them)

The trap: *reading* a solution (the in-memory DB, the bank) feels like progress, but the skill tested is building cleanly under time **without seeing the future levels**. Practice has to simulate that.

**Core principle — reproduce the real conditions exactly:**
- **Bare web editor** (Replit, Colab, or CodeSignal practice) — *not* your IDE. No autocomplete/Copilot. That's the OA condition.
- **90-min timer, one blank file, all levels in one codebase.**
- **Write your own tests as you go.** The real ICA grades on *hidden* tests, so the transferable skill is **reasoning out edge cases yourself** (missing keys, TTL boundaries, ties, out-of-order events) and checking them before moving on. This habit is what separates people who clear Level 4.

**The drill that builds the actual skill (design-for-extension under uncertainty):**
1. Pick a real problem but **read only Levels 1–2.** Implement them cold.
2. *Then* reveal Levels 3–4 and bolt them on **without rewriting the core.** If you need a heavy refactor, your L1 design was wrong — that's the lesson; redo it.
3. This trains the exact thing the round tests: you never see later levels when you design Level 1.

**Prove you're pattern-fluent, not memorizing.** Labs flag circulated solutions and will swap in a fresh problem. After you can do the in-memory DB, do **2–3 variants** (banking system, file host, inventory) and confirm the same primitives carry over (e.g., the **append-only version list + binary search by timestamp** from §4 solves every "value at time T" level). If you can re-derive the pattern on a new skin, you're ready; if you're recalling keystrokes, you're not.

**Where the *real* questions live:**
- **CodeSignal practice mode** — ships an official sample ICA in the exact format; do this first to learn the interface.
- **Community ICA practice repo** + **csoahelp / LeetCode Discuss** ICA threads (see §7) — the actual circulated multi-level problems.
- **1point3acres / Blind / Glassdoor** — recent candidate reports give the *current* problems and per-company twists (freshest signal).
- **This vault:** the **OpenAI 8-problem bank** and **Anthropic live bank** are real reported questions with worked solutions — **re-implement from scratch**, don't just read.
- **LeetCode "Design" tag** (#146, #981, #380, #1166 …) for the building-block primitives.
- **Pramp / interviewing.io** for the *live* variant — narrate aloud to a human, since OpenAI/Anthropic grade your reasoning, not just final code.

**If you do only one thing:** re-implement the **in-memory DB** and the **banking system** from a blank file, timed, in Replit, writing your own edge-case tests — then repeat each a week later cold. Two problems × two clean reps ≈ 80% of what this round throws at you. Rehearse the common follow-ups aloud too (thread-safety with `RLock`, custom serialization without `json`, async).

---

## 7. Sources
- CodeSignal — Industry Coding Framework / ICA structure & rules: https://codesignal.com/resource/industry-coding-framework/ · https://support.codesignal.com/hc/en-us/articles/19116922232983-What-are-the-Industry-Coding-Assessment-ICA-rules · GCA structure: https://support.codesignal.com/hc/en-us/articles/360040370853
- CodeSignal — scoring & "pass" (200–600 scale, difficulty × hidden-test correctness × time, partial credit): https://support.codesignal.com/hc/en-us/articles/13261190299287-Understanding-Assessment-Score · company cut scores: https://support.codesignal.com/hc/en-us/articles/23458723018391-Guide-to-Setting-Cut-Scores
- In-memory DB ICA (level breakdown, candidate reports): https://www.1point3acres.com/interview/thread/1110874 · https://csoahelp.com/2025/02/09/codesignal-in-memory-database-industry-oa/ · https://github.com/MayukhSobo/in-memory-db
- ICA practice repo: https://github.com/PaulLockett/CodeSignal_Practice_Industry_Coding_Framework
- Companies using CodeSignal: https://blog.techdatapark.com/companies-using-codesignal/
- Anthropic CodeSignal experience: https://www.linkjob.ai/interview-questions/anthropic-software-engineer-interview/
- Worked solutions (in this vault): [[openai-interview-guide]] (8-problem bank), [[anthropic-interview-guide]] (live bank: crawler, stack-trace, exclusive-time, dup-files, LRU)

*Track B deep guide — created 2026-06-16. Pattern to internalize: build a stateful object, store more than L1 needs, extend across levels, never break earlier tests.*
