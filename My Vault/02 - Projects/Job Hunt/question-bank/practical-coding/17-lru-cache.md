---
title: LRU Cache
slug: lru-cache
type: leetcode-design
leetcode: 146
companies: [Anthropic, Cohere, OpenAI, Google, Amazon, Meta, Microsoft, Stripe, "broadly all"]
difficulty: ★★★☆☆
frequency: very-high
formats: [OA·GCA/HR, Live, Onsite·NR]
levels: 1
time-box: 20–30 min
tags: [hashmap, doubly-linked-list, ordered-dict, thread-safety, eviction]
related: ["[[18-lfu-cache]]", "[[practical-oo-coding-deep-guide]]", "[[01-in-memory-key-value-database]]"]
---

# LRU Cache ⭐⭐ (#146)

The single most common design problem — know it cold, including a thread-safe variant. The base takes 15 minutes; the follow-ups are where you signal seniority.

## Problem

`LRUCache(capacity: int)`:
- `get(key) -> int` — O(1), returns value or -1, marks the key recently used.
- `put(key, value)` — O(1), inserts or updates; if at capacity, evict the least-recently-used.

## Core approach (format-agnostic)

Two structures working together:
- **HashMap** `key → node` for O(1) lookup.
- **Doubly-linked list** (DLL) of nodes ordered by recency (head=MRU, tail=LRU). DLL supports O(1) move-to-head, remove, append.

Operations:
- `get(key)`: lookup; if found, move-to-head, return value.
- `put(key, value)`: if key exists, update value + move-to-head. Else, insert at head. If over capacity, remove tail.

**Shortcut:** `collections.OrderedDict` with `move_to_end(last=False)` and `popitem(last=False)` does the same in fewer lines — but interviewers often require the hand-rolled DLL.

### Worked Python solutions

**With `OrderedDict`:**
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.cache = OrderedDict()

    def get(self, key: int) -> int:
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.cap:
            self.cache.popitem(last=False)
```

**Hand-rolled DLL** (for onsite NR or when `OrderedDict` is forbidden):
```python
class Node:
    __slots__ = ("key", "val", "prev", "next")
    def __init__(self, key, val):
        self.key, self.val = key, val
        self.prev = self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.cap = capacity
        self.map = {}
        self.head = Node(0, 0)            # sentinel
        self.tail = Node(0, 0)
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node):
        node.prev = self.head
        node.next = self.head.next
        self.head.next.prev = node
        self.head.next = node

    def get(self, key):
        if key not in self.map:
            return -1
        node = self.map[key]
        self._remove(node)
        self._add_to_front(node)
        return node.val

    def put(self, key, value):
        if key in self.map:
            self._remove(self.map[key])
        node = Node(key, value)
        self._add_to_front(node)
        self.map[key] = node
        if len(self.map) > self.cap:
            lru = self.tail.prev
            self._remove(lru)
            del self.map[lru.key]
```

**Complexity.** O(1) per op; O(capacity) memory.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** `OrderedDict` is fine and fastest to write; verify O(1) (no list scans); handle capacity 0.
- **Pitfalls:**
  - Capacity 0 — `put` should immediately drop.
  - Updating an existing key — must `move_to_end`/`_add_to_front` and overwrite.
  - `get` on missing returns `-1`, not `None`.

### Live · CoderPad (human)
- **How it appears:** base ~15 min, then follow-ups.
- **Follow-ups (real, reported):**
  - **Thread safety** — wrap with `threading.Lock` (or `RLock`); discuss trade-off (throughput vs correctness).
  - **`functools.lru_cache`** the `*args/**kwargs` key bug — "fix the cache" variant: `lru_cache(maxsize=128)` keys on the **string repr** of args, so `cache(1, 2)` and `cache(1.0, 2.0)` are the same key.
  - **TTL** — each value has an expiry; lazy on get, optional background sweep. → see [[01-in-memory-key-value-database]] L3.
  - **LFU** — least-frequently-used; tie-break by LRU within a freq bucket. → see [[18-lfu-cache]].
  - **Capacity resize** — grow/shrink at runtime.
  - **Async** — async-safe variant with `asyncio.Lock`.
  - **Distributed cache** — shard by hash, gossip invalidations.
  - **Eviction policy alternatives** — FIFO, ARC, 2Q.
  - **Cache stampede** — hot key expires, 1000 threads recompute simultaneously → per-key lock / single-flight (one computes, others wait), or probabilistic early refresh; the production follow-up behind "add TTL".
  - **What breaks LRU in production?** → scans: one batch job touching a million keys evicts the entire hot set → scan-resistant policies (2Q/ARC/segmented LRU keep a probation segment); one sentence that turns the puzzle into systems judgment.
  - **Sharded LRU for lock contention** — N independent LRU shards keyed by hash(key): global lock disappears, but LRU becomes approximate per-shard (eviction is no longer globally least-recent) — the concurrency-vs-exactness trade.
- **Tips:**
  - **Ask if `OrderedDict` is allowed**; if not, hand-roll the DLL and narrate the pointer surgery.
  - For thread safety: name the lock (`threading.Lock`), say it's needed because of the read-modify-write.
  - For the `functools.lru_cache` bug: explain that the key is `repr(args)` which collapses 1 == 1.0.
  - For TTL: combine with Q01's `_active` helper.
- **Pitfalls:**
  - **Broken DLL relinking** — losing a node during move; trace `put` on a 2-cap cache.
  - **Not updating the map on eviction** — `del self.map[lru.key]`.
  - **Sentinel mistakes** — head/tail must never be evicted; eviction is `tail.prev`, not `tail`.
  - **Lock deadlock** — re-entering a locked method; use `RLock` or restructure.

### Onsite · NR (Google-style, non-runnable)
- **Tips:** Write the DLL **by hand** compilably; "test" by tracing put/get/evict on a 2-capacity example aloud.
- **Pitfalls:**
  - Off-by-one in eviction (removing `tail` instead of `tail.prev`).
  - Sentinel head/tail not used (edge cases at ends).
  - Missing map update on eviction.

## Company variants

- **Anthropic / Cohere / OpenAI** — base + thread safety.
- **Google / Amazon / Meta / Microsoft / Stripe** — base problem everywhere.
- **"Fix the cache"** variants show up at Anthropic, Google, and Stripe.

## Worked example trace

```
LRUCache(2)
put(1, 1)        # map={1: Node(1,1)}, list: 1
put(2, 2)        # map={1,2}, list: 2→1
get(1)           # move 1 to front → list: 1→2; return 1
put(3, 3)        # evict 2 (LRU); list: 3→1; map={1,3}
get(2)           # not in map → -1
put(1, 10)       # update + move; list: 1→3
get(1)           # return 10
get(3)           # return 3
```

## Related
[[18-lfu-cache]] (harder sibling) · [[01-in-memory-key-value-database]] L3 (TTL variant) · [[practical-oo-coding-deep-guide]] §3 (Q17).