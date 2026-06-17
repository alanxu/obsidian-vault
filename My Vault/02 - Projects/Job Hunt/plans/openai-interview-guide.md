# OpenAI Interview Guide — Applied AI / SWE / FDE (2025–2026)

> **Role focus:** Software Engineer (SWE), Applied AI Engineer, Forward Deployed Engineer (FDE equivalent)
> **ML required?** No — SWE and applied/FDE tracks do not require ML modeling background
> **Primary language:** Python (strongly recommended; other languages risk running out of time)
> **Sources:** hellointerview.com, prachub.com, Medium (Anqi Silvia), Glassdoor (Apr–Jun 2026), 1Point3Acres, Exponent, vervecopilot.com, techprep.app, interviewquery.com

---

## TL;DR

- OpenAI has **shifted away from classic LeetCode** toward practical, multi-part, production-style coding problems drawn from a fixed bank of ~8 recurring problem types
- The coding bar is **non-negotiable** — multiple candidates report being told "we won't pass you at 2/4 on coding even if you ace everything else"
- You write **significantly more code** than at FAANG — volume and completeness matter as much as correctness
- For non-ML engineers: SWE and FDE/Applied tracks are accessible; the ML Engineer track (neural nets from scratch, transformer debugging) is separate and not covered here
- Total timeline: **3 weeks (SWE screen-only) to 8–12 weeks (staff onsite loop)**

---

## Interview Process

### Stage 1 — Recruiter Screen (30–45 min)
- Background, motivation for OpenAI, understanding of AGI mission
- "Why OpenAI specifically" (not just "why AI") — read OpenAI's Charter before this call
- Logistics, leveling, comp expectations
- Some candidates report light safety/values probing here at staff level

### Stage 2 — Technical Screen (60 min, CoderPad or HackerRank)
- Live coding with interviewer watching in real time
- Single problem, progressive gates — solve a simple version, then interviewer layers constraints
- Problems feel "more practical than LeetCode grinding" (multiple candidate reports)
- Concurrency and OOP design elements common here
- Communication while coding is evaluated — clarify, narrate, don't go silent

### Stage 3 — Work Trial / Take-Home (48-hour window, practical build)
- Build something real (e.g., a webhook delivery system)
- Evaluated on **reliability, code quality, and testing** — not feature count
- TDD approach (write tests first) is rewarded; prepare for this format specifically

### Stage 4 — Final Onsite Loop (4–6 hrs, virtual or in-person)
Typically 4–6 rounds in one day:
1. **Coding round** — another multi-part practical problem
2. **System design** — infrastructure/architecture grounded in OpenAI's actual scale
3. **Technical project presentation** — walk through a past project you owned; defend every decision
4. **Behavioral round(s)** — mission alignment, ambiguity handling, collaboration (staff: leadership focus)
5. *(Senior/Staff only)* Code refactoring round + cross-functional communication round

### Process by role/level
| Role | Rounds | Timeline | Hardest filter |
|---|---|---|---|
| SWE (mid) | 4–6 | 3–5 weeks | Coding volume |
| SWE (staff L5) | 6–8 | 8–12 weeks | Coding + project presentation |
| Applied AI / FDE | 5–7 | 4–8 weeks | Coding + customer simulation |

---

## The ~8-Problem Coding Bank

OpenAI draws all coding questions from a recurring bank. Below are the confirmed problem types with full descriptions and worked approaches.

---

### Problem 1 — Versioned / Time-Based Key-Value Store ⭐ (most reported)

**Description:** Implement a `KVStore` class. `put(key, value)` records the value and auto-increments a version number (starting at 1). `get(key, version)` returns the value at that version or the latest version before it. Follow-ups add real timestamps, thread safety, and file persistence with custom serialization (no `json`/`pickle`).

**Approach:**
- Store per key: a sorted list of `(version, value)` tuples
- `get` with version: binary search for the largest version ≤ requested version
- Thread safety: `threading.RLock()` wrapping all mutations
- File persistence: custom serialization (e.g., length-prefixed records or delimiter-escaped CSV) — no stdlib serializers allowed

```python
import threading
import bisect

class KVStore:
    def __init__(self):
        self._store = {}          # key -> sorted list of (version, value)
        self._lock = threading.RLock()

    def put(self, key: str, value: str) -> int:
        with self._lock:
            if key not in self._store:
                self._store[key] = []
            versions = self._store[key]
            new_version = (versions[-1][0] + 1) if versions else 1
            versions.append((new_version, value))
            return new_version

    def get(self, key: str, version: int = None) -> str | None:
        with self._lock:
            if key not in self._store:
                return None
            versions = self._store[key]
            if not versions:
                return None
            if version is None:
                return versions[-1][1]
            # Binary search: largest version <= requested
            keys = [v for v, _ in versions]
            idx = bisect.bisect_right(keys, version) - 1
            if idx < 0:
                return None
            return versions[idx][1]

    def save(self, filepath: str):
        """Custom serialization: escape | and newlines in values."""
        with self._lock:
            with open(filepath, 'w') as f:
                for key, versions in self._store.items():
                    for ver, val in versions:
                        k = key.replace('\\', '\\\\').replace('|', '\\|')
                        v = val.replace('\\', '\\\\').replace('|', '\\|').replace('\n', '\\n')
                        f.write(f"{k}|{ver}|{v}\n")

    def load(self, filepath: str):
        with self._lock:
            self._store = {}
            with open(filepath, 'r') as f:
                for line in f:
                    line = line.rstrip('\n')
                    # Split on unescaped |
                    parts = line.split('|')  # simplified; production: proper parser
                    key, ver, val = parts[0], int(parts[1]), parts[2]
                    self._store.setdefault(key, []).append((ver, val))
```

**Complexity:** `put` O(1) amortized; `get` O(log n) per key; `save`/`load` O(N total entries).

**Follow-up: real timestamps (strictly increasing)**
- Replace version with `timestamp`; use a `threading.Condition` to block `put` until timestamp > last recorded; `get(key, ts)` does the same binary search on timestamps.
- Mock timestamps in tests: inject a `clock` callable (default `time.time`), override in tests with a counter.

**Lock comparison follow-up:** `threading.Lock` (non-reentrant, faster) vs `threading.RLock` (reentrant — same thread can acquire multiple times, needed if `put` internally calls another method that also locks). Use `RLock` when methods call each other; `Lock` otherwise.

---

### Problem 2 — Multi-File Iterator (up to 6 progressive parts) ⭐

**Description:** Given a list of file paths, implement an iterator that yields lines across all files in order, skipping empty files. Part 2: make it resumable (save/restore state). Part 3: `ResumableMultiFileIterator`. Part 4: async version. Part 5: 2D (files of files). Part 6: 3D.

**Core approach (Part 1):**
```python
class MultiFileIterator:
    def __init__(self, paths: list[str]):
        self._paths = paths
        self._file_idx = 0
        self._fh = None
        self._advance()

    def _advance(self):
        """Open next non-empty file."""
        if self._fh:
            self._fh.close()
            self._fh = None
        while self._file_idx < len(self._paths):
            try:
                self._fh = open(self._paths[self._file_idx], 'r')
                self._file_idx += 1
                return
            except OSError:
                self._file_idx += 1
        # No more files

    def __iter__(self):
        return self

    def __next__(self) -> str:
        while self._fh is not None:
            line = self._fh.readline()
            if line:
                return line.rstrip('\n')
            self._advance()   # current file exhausted
        raise StopIteration
```

**Part 2 — Resumable (save/restore position):**
```python
def get_state(self) -> dict:
    pos = self._fh.tell() if self._fh else None
    return {'file_idx': self._file_idx, 'pos': pos}

def set_state(self, state: dict):
    if self._fh:
        self._fh.close()
    self._file_idx = state['file_idx']
    # Re-open the current file at saved position
    if self._file_idx <= len(self._paths):
        self._fh = open(self._paths[self._file_idx - 1], 'r')
        if state['pos']:
            self._fh.seek(state['pos'])
```

**Part 4 — Async:**
Replace `open` with `aiofiles.open`, `readline` → `await fh.readline()`, `__next__` → `async def __anext__`, `__iter__` → `__aiter__`. The pattern is identical; just add `await` and `async`.

**Key edge cases:** empty files (skip silently), files that don't exist (catch `OSError`), files modified between `get_state` and `set_state` (document as undefined behavior), `next()` on an iterator whose files were deleted.

---

### Problem 3 — CD Directory Navigation

**Description:** Implement `cd(current_dir: str, new_dir: str) -> str | None`. Handles absolute paths starting with `/`, relative paths, `..`, `.`, `~` (home directory). Returns `None` if the result would be above root. Follow-up: add a `soft_links: dict` third parameter.

```python
def cd(current_dir: str, new_dir: str, soft_links: dict = None,
       home: str = '/home/user') -> str | None:
    if soft_links is None:
        soft_links = {}
    
    # Resolve home
    if new_dir == '~' or new_dir.startswith('~/'):
        new_dir = home + new_dir[1:]
    
    # Start point
    if new_dir.startswith('/'):
        parts = []           # absolute: start from root
        segments = new_dir[1:].split('/')
    else:
        parts = [p for p in current_dir.split('/') if p]
        segments = new_dir.split('/')
    
    for seg in segments:
        if seg == '' or seg == '.':
            continue
        elif seg == '..':
            if not parts:
                return None  # above root
            parts.pop()
        else:
            # Resolve soft link
            candidate = '/' + '/'.join(parts + [seg])
            if candidate in soft_links:
                resolved = soft_links[candidate]
                parts = [p for p in resolved.split('/') if p]
            else:
                parts.append(seg)
    
    return '/' + '/'.join(parts) if parts else '/'
```

**Tests to narrate:**
```
cd('/foo/bar', 'baz')        -> '/foo/bar/baz'
cd('/foo/../', 'baz')        -> '/baz'
cd('/', '..')                -> None
cd('/a/b', '../../..')       -> None
cd('/home/user', '~')        -> '/home/user'
```

---

### Problem 4 — Expiring Credit Ledger (out-of-order events) ⭐

**Description:** Implement a credit system with out-of-order event support:
- `add_credit(id, amount, timestamp, expiration)` — adds credit that expires at `expiration`
- `use_credit(id, amount, timestamp)` — deducts from earliest-expiring non-expired credits first
- `balance(id, timestamp)` — sum of non-expired credits minus used credits at this timestamp

**Approach:** Per user, maintain a sorted list of credit grants `(expiration, amount_remaining)`. For `use_credit`, consume from earliest-expiring first (greedy). Out-of-order: buffer events and process in timestamp order — use a heap or sort on query.

```python
import heapq

class CreditLedger:
    def __init__(self):
        # user_id -> list of (expiration, granted_at, remaining)
        self._credits = {}
        # user_id -> list of (timestamp, amount) debit events
        self._debits = {}

    def add_credit(self, uid: str, amount: float, ts: float, exp: float):
        self._credits.setdefault(uid, [])
        heapq.heappush(self._credits[uid], (exp, ts, amount))

    def use_credit(self, uid: str, amount: float, ts: float):
        self._debits.setdefault(uid, []).append((ts, amount))

    def balance(self, uid: str, ts: float) -> float:
        # Sum non-expired credits granted at or before ts
        available = 0.0
        for exp, granted_at, amt in self._credits.get(uid, []):
            if granted_at <= ts and exp > ts:
                available += amt
        # Subtract debits at or before ts (in order, consuming earliest-expiring first)
        # Simplified: subtract total debits (full simulation requires replay)
        used = sum(a for t, a in self._debits.get(uid, []) if t <= ts)
        return max(0.0, available - used)
```

**Narrate:** the hard part is out-of-order `use_credit` events — a debit at t=5 might arrive after a debit at t=10. Full correctness requires replaying all events in timestamp order on each `balance` query, or maintaining an event log and sorting on query. Trade-off: eager processing (fast writes, slow reads) vs lazy/replay (fast writes, O(n log n) reads). Ask the interviewer which they prefer.

---

### Problem 5 — GPU Credit Manager

**Description:** Similar to Problem 4 but models GPU compute credits with allocation and release:
- `add_credit(id, amount, timestamp, expiration)`
- `allocate(id, amount, timestamp)` — reserve if sufficient non-expired balance
- `release(id, amount, timestamp)` — return previously allocated credits
- `available(id, timestamp)` — balance minus allocated

Approach is identical to Problem 4 with an additional `allocated` tracking dict. Key follow-up: **idempotency** (what if `allocate` is called twice with the same request ID?) → add a `request_id` parameter and deduplicate.

---

### Problem 6 — In-Memory Database (SET/GET/DELETE/SCAN + TTL)

Very similar to Anthropic's bank — see Anthropic guide for full solution. OpenAI variant specifics:
- `SET key value [EX seconds]`
- `GET key` (returns None if expired or missing)
- `DELETE key`
- `SCAN prefix` — return all live keys with this prefix
- `BACKUP` / `RESTORE ts` — snapshot and restore to a prior timestamp

```python
import time
from collections import defaultdict

class InMemoryDB:
    def __init__(self):
        self._store = {}          # key -> (value, expiry or None)
        self._history = []        # list of (timestamp, snapshot)

    def set(self, key, value, ex=None):
        expiry = time.time() + ex if ex else None
        self._store[key] = (value, expiry)

    def get(self, key):
        if key not in self._store:
            return None
        val, exp = self._store[key]
        if exp and time.time() > exp:
            del self._store[key]
            return None
        return val

    def delete(self, key):
        self._store.pop(key, None)

    def scan(self, prefix):
        now = time.time()
        return [k for k, (v, exp) in self._store.items()
                if k.startswith(prefix) and (not exp or exp > now)]

    def backup(self):
        import copy
        self._history.append((time.time(), copy.deepcopy(self._store)))

    def restore(self, ts):
        # Find latest backup at or before ts
        for snap_ts, snap in reversed(self._history):
            if snap_ts <= ts:
                self._store = snap
                return
        self._store = {}
```

---

### Problem 7 — Virus/Infection Spread on a Grid (Conway variant)

**Description:** Given an m×n grid where `0`=empty, `1`=healthy plant, `2`=infected, `3`=obstacle, simulate spread. Each minute, each infected cell spreads to 4-directional neighbors (not obstacles). Return the grid state after k minutes, or the number of minutes until all reachable plants are infected (or -1 if some can't be).

```python
from collections import deque

def simulate_infection(grid, k=None):
    rows, cols = len(grid), len(grid[0])
    q = deque()
    healthy = 0
    
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                q.append((r, c, 0))
            elif grid[r][c] == 1:
                healthy += 1
    
    infected = 0
    minutes = 0
    
    while q:
        r, c, t = q.popleft()
        if k is not None and t >= k:
            continue
        for dr, dc in [(-1,0),(1,0),(0,-1),(0,1)]:
            nr, nc = r+dr, c+dc
            if 0<=nr<rows and 0<=nc<cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2
                infected += 1
                minutes = t + 1
                q.append((nr, nc, t+1))
    
    if k is not None:
        return grid
    return minutes if infected == healthy else -1
```

---

### Problem 8 — API Log Parser / Token Usage Aggregator

**Description:** Given a string of API call logs (each line: `user_id | endpoint | tokens_used | timestamp`), extract total token consumption per user, sort by total descending.

```python
def parse_token_usage(log_str: str) -> list[tuple[str, int]]:
    usage = {}
    for line in log_str.strip().split('\n'):
        if not line.strip():
            continue
        parts = [p.strip() for p in line.split('|')]
        user_id, endpoint, tokens, ts = parts[0], parts[1], int(parts[2]), parts[3]
        usage[user_id] = usage.get(user_id, 0) + tokens
    return sorted(usage.items(), key=lambda x: -x[1])
```

Follow-ups: handle malformed lines gracefully; aggregate by endpoint per user; compute per-minute rate; stream processing (process line by line, not load all at once).

---

## System Design Questions

OpenAI system design is "entirely about infrastructure and distributed systems: queuing, batching, load balancing, fault tolerance, scale" — no ML needed.

### Reported questions:
1. Design the ChatGPT service (multi-user, persistent threads, streaming)
2. Design an LLM inference API at 10k req/s — batching, GPU routing, streaming responses
3. Design a distributed search for 1B documents + 1M QPS
4. Design a webhook delivery system (reliable, at-least-once, with retries and dead-letter queues)
5. Design a rate limiter (sliding window, distributed, Redis-backed)
6. Design a payment processing system with LLM-based fraud detection

### Key patterns interviewers probe:
- **Request batching** — how do you maximize GPU utilization without increasing p99 latency?
- **Queueing** — priority queues, backpressure, consumer groups
- **Streaming** — SSE vs WebSockets for token-by-token delivery
- **Fault tolerance** — what fails, how do you detect it, how do you recover?
- **Cost controls** — model tiering (cheap model for easy queries), caching, prompt deduplication
- Always name **2+ options** per decision and compare trade-offs explicitly

---

## Behavioral & Values Questions

OpenAI's mission is AGI — read their **Charter** before any conversation. Key themes:

- "Why OpenAI — and what do you think about the path to AGI?"
- "Describe a time you handled ambiguity in a high-stakes project"
- "Tell me about a technical decision you reversed"
- "How do you work with researchers vs. product vs. ops?"
- "Describe a collaboration that went wrong — what would you do differently?"
- "What does safety mean to you in the context of deploying AI systems?"

**Communication is explicitly evaluated** — getting the right answer silently is not enough. Multiple candidates report: "explaining your reasoning live is the differentiator."

---

## Tips & Prep Strategy

### Coding prep (most important)
1. Practice the 8-problem bank in a **shared editor** (CoderPad), not your IDE
2. Use **Python exclusively** — other languages risk not finishing
3. Drill **TDD**: write tests first, then implement; practice this format specifically
4. Focus on **completeness** — all test cases passing > a clever partial solution
5. Practice **narrating while typing** — interviewers evaluate communication throughout
6. Know `threading`, `asyncio`, `bisect`, `heapq`, `collections` cold

### System design prep
- Know queuing deeply (Kafka, SQS semantics, at-least-once vs exactly-once)
- Know GPU batching basics (continuous batching, request padding, KV cache)
- Practice driving the conversation: scope → components → deep-dive one area → trade-offs → failure modes

### Mission alignment
- Read OpenAI's Charter (openai.com/charter) before any conversation
- Have a genuine answer to "why AGI safety matters" that isn't just parroting talking points
- Staff level: prepare a 20-min technical project presentation you can defend under heavy questioning

### Timeline
- Apply via referral if possible — accelerates scheduling
- Staff loop (8–12 weeks) can stretch to 4+ months; follow up proactively after each stage
- Expect gaps of 2–3 weeks between stages at staff level

---

## Compensation (Levels.fyi, 2025–2026)

| Level | Role | Approx TC |
|---|---|---|
| L3 | SWE | ~$300K–$400K |
| L4 | SWE | ~$400K–$550K |
| L5 (Staff) | SWE | ~$600K–$800K |
| L6 | SWE | ~$900K–$1.2M |
| L4–L5 | Applied AI / FDE | ~$450K–$700K |

Equity is stock options (not RSUs), vesting 4 years. OpenAI runs periodic secondary liquidity windows.

---

## Sources to Explore Further

| Source | What it's good for |
|---|---|
| [prachub.com/companies/openai](https://prachub.com/companies/openai/categories/coding-and-algorithms) | Live, dated question bank — best for current problems |
| [hellointerview.com/blog/openai-coding-questions](https://www.hellointerview.com/blog/openai-coding-questions) | Worked approaches, candidate reports |
| Medium — Anqi Silvia "My 8 Coding Questions from 2025 OpenAI" | First-person account, all 8 problems |
| Glassdoor — OpenAI Software Engineer interviews | Raw candidate reports, 2025–2026 |
| 1Point3Acres — search `OpenAI 面经 2026` | Most detailed dated onsite reports |
| Blind — OpenAI megathread | TC-verified, comp + process reports |
| [interviewing.io/openai-interview-questions](https://interviewing.io/openai-interview-questions) | Engineer-sourced process breakdown |

---

*Last updated: June 2026 | Next: See Anthropic Interview Guide for comparison*
