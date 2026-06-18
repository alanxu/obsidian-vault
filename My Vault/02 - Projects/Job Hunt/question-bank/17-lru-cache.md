---
title: LRU Cache
slug: lru-cache
type: leetcode-design
leetcode: 146
companies: [Anthropic, Cohere, "broadly all"]
difficulty: ★★★☆☆
frequency: very-high
formats: [OA·GCA/HR, Live, Onsite·NR]
levels: 1
time-box: 20–30 min
tags: [hashmap, doubly-linked-list, ordered-dict, thread-safety]
related: ["[[18-lfu-cache]]", "[[practical-oo-coding-deep-guide]]"]
---

# LRU Cache ⭐⭐ (#146)

The single most common design problem — know it cold, including a thread-safe variant.

## Problem
`LRUCache(capacity)`: `get(key)` O(1) returns value or −1 and marks recently used; `put(key, value)` O(1), evicts LRU at capacity.

## Core approach (format-agnostic)
**HashMap + doubly-linked list** (head=MRU, tail=LRU); move/insert at head, evict from tail. `OrderedDict` (`move_to_end`, `popitem(last=False)`) is the shortcut — **but be ready to hand-roll the DLL** (often required). Hand-rolled code: [[practical-oo-coding-deep-guide]] §3 (Q17).

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** `OrderedDict` is fine and fastest to write; verify O(1) (no list scans).
- **Pitfalls:** capacity 0, updating an existing key (move + overwrite), `get` on missing returns −1.

### Live · CoderPad (human)
- **Follow-ups:** **thread-safe** (wrap with `Lock`), the `functools.lru_cache` `*args/**kwargs` key bug ("fix the cache" variant), TTL (→ [[01-in-memory-key-value-database]]), LFU (→ [[18-lfu-cache]]).
- **Tips:** ask if `OrderedDict` is allowed; if not, hand-roll the DLL and narrate the pointer surgery.
- **Pitfalls:** broken DLL relinking (lose a node), not updating the map on eviction.

### Onsite · NR (Google-style, non-runnable)
- **Tips:** write the DLL **by hand** compilably; "test" by tracing put/get/evict on a 2-capacity example aloud.
- **Pitfalls:** off-by-one in eviction, sentinel head/tail not used (edge cases at ends).

## Related
[[18-lfu-cache]] (harder sibling) · [[01-in-memory-key-value-database]] (TTL variant).
