---
title: Inventory / Warehouse Management
slug: inventory-warehouse-management
type: multi-level-stateful
leetcode: null
companies: [Anthropic, Roblox, Shopify, Amazon, Stripe-fulfillment, CodeSignal cos, "DoorDash-style logistics"]
difficulty: ★★★☆☆
frequency: medium
formats: [OA·ICA, Live]
levels: 4
time-box: 90 min for 4 levels
tags: [oo-design, duplicates, naming, capacity, suffix-algorithm]
related: ["[[01-in-memory-key-value-database]]", "[[04-cloud-storage-file-host]]"]
---

# Inventory / Warehouse Management

Anthropic's reported variant uses item **copies with auto-suffixed names** — `.dupe`, `.copy2`, `.copy3` — and the trickiest part of the whole problem is the **suffix collision algorithm**. Same extend-across-levels skeleton as [[01-in-memory-key-value-database]].

## Problem (by level)

The warehouse stores items in **locations**. Each item has a string `name` and a dict of attributes (e.g. `{"size": 10, "color": "red"}`).

### L1 — Core CRUD
- `add_item(name, attrs: dict) -> bool` — `false` if name already exists.
- `get_item(name) -> dict | ""` — return attrs or empty string.
- `delete_item(name) -> bool` — `true` if removed.

### L2 — Duplicates
- `copy_item(name) -> str` — return the new name; original name gets `".dupe"`, copy of `.dupe` gets `.copy2`, then `.copy3`, etc. The **algorithm varies by company** — get the spec right.
- `add_duplicate_items(name, k) -> list[str]` — make `k` copies at once; return new names.

### L3 — Capacity / TTL
Two flavors (read the spec carefully):
- **Capacity:** each location has a `max_items` and a `current_items`. `add_item` rejects when full.
- **TTL:** items have `expiry_ts`; `get_item(name, ts)` returns `""` if expired.

### L4 — Snapshot / move
- `backup() / restore()` snapshots (analogous to Q01 L4) — OR —
- `move(item, loc_a, loc_b)` — moves an item between locations, respecting capacity.

## Core approach (format-agnostic)

### Naming convention (the silent killer)

There are **at least four** conventions reported in the wild. **Confirm before coding.**

| Variant | Original | 1st copy | 2nd copy | 3rd copy |
|---|---|---|---|---|
| **A — Anthropic (`.dupe` family)** | `apple` | `apple.dupe` | `apple.copy2` | `apple.copy3` |
| **B — Plain numeric** | `apple` | `apple.dupe` | `apple.dupe2` | `apple.dupe3` |
| **C — Always numeric** | `apple` | `apple(1)` | `apple(2)` | `apple(3)` |
| **D — File-style** | `apple.txt` | `apple (1).txt` | `apple (2).txt` | `apple (3).txt` |

For **Variant A** (the Anthropic one), the rule is:
- 1st copy: append `.dupe` to the original.
- 2nd copy: if `.dupe` exists, append `.copy2`.
- 3rd copy: `.copy3` (NOT `.copy2` again).
- Nth copy: `.copyN` where N grows.

The collision test asks: "if I delete `apple.dupe`, then call `copy_item('apple')`, what do you get?" Answer: `apple.dupe` again (the next free slot). **Do not** re-number.

### Storage
- `items: dict[name → (attrs, location, expire_ts|None)]`
- `locations: dict[name → (capacity, current)]` (or just a `capacity_counter` per location)
- For suffix bookkeeping: a per-base-name counter or a `_next_suffix_index(name)` helper that scans only when the counter is reset (after deletions).

### Worked Python solution (Variant A)

```python
class Warehouse:
    def __init__(self):
        self.items = {}                  # name -> {"attrs": {...}, "loc": str, "exp": ts|None}
        self.locs = {}                   # loc -> {"cap": int, "used": int}
        self._suffix_idx = {}            # base_name -> next integer suffix

    # ---------- L1 ----------
    def add_item(self, name, attrs):
        if name in self.items:
            return False
        self.items[name] = {"attrs": dict(attrs), "loc": None, "exp": None}
        return True

    def get_item(self, name):
        item = self.items.get(name)
        return item["attrs"] if item else ""

    def delete_item(self, name):
        if name in self.items:
            del self.items[name]
            return True
        return False

    # ---------- L2 ----------
    def _base(self, name):
        # strip known suffixes to recover the "base" name
        for suf in (".dupe",):
            if name.endswith(suf):
                return name[:-len(suf)]
        if ".copy" in name:
            return name.split(".copy")[0]
        return name

    def _next_name(self, base):
        # Variant A: try .dupe first, then .copyN starting from 2
        if f"{base}.dupe" not in self.items:
            return f"{base}.dupe"
        n = 2
        while f"{base}.copy{n}" in self.items:
            n += 1
        return f"{base}.copy{n}"

    def copy_item(self, name):
        if name not in self.items:
            return ""
        base = self._base(name)
        new = self._next_name(base)
        self.items[new] = {"attrs": dict(self.items[name]["attrs"]),
                           "loc": self.items[name]["loc"],
                           "exp": self.items[name]["exp"]}
        return new

    def add_duplicate_items(self, name, k):
        return [self.copy_item(name) for _ in range(k)]

    # ---------- L3 (capacity flavor) ----------
    def add_location(self, name, capacity):
        self.locs[name] = {"cap": capacity, "used": 0}

    def add_item_to_location(self, item, loc):
        loc_state = self.locs.get(loc)
        if not loc_state or loc_state["used"] >= loc_state["cap"]:
            return False
        if item not in self.items:
            return False
        self.items[item]["loc"] = loc
        loc_state["used"] += 1
        return True

    # ---------- L4 (move) ----------
    def move_item(self, item, dst):
        src = self.items[item]["loc"]
        if not self.add_item_to_location(item, dst):
            return False
        if src:
            self.locs[src]["used"] -= 1
        return True
```

**Complexity.** CRUD O(1). `copy_item` O(k) where k is the size of the suffix gap (typically ≤ number of copies; amortized O(1) with a counter). Move O(1).

## By format

### OA · ICA (CodeSignal, 4 levels)
- **How it appears:** Anthropic-style 4-level skin; the suffix rule is the L2 trip-wire.
- **Tips:**
  - Get the suffix algorithm **exactly right** — graders check `.dupe`, `.copy2`, `.copy3` naming and collision handling.
  - Keep capacity as a simple counter, not a list scan.
  - Re-run earlier hidden tests after each level change.
- **Pitfalls:**
  - **Copy-of-a-copy naming** — copy `apple.dupe` should yield `apple.copy2` (NOT `apple.dupe.dupe`).
  - **Suffix collision** — if `apple.dupe` is deleted, the next copy should produce `apple.dupe`, not `apple.copy2`.
  - Restoring over capacity → reject the restore.
  - Deleting an original with live copies — should work fine (no cascade), but spec may differ.
  - Move: decrement source capacity **only if** the destination accept succeeded.

### Live · CoderPad
- **Follow-ups:**
  - **Cheapest restock** — query: which items do I need most? attribute-based filter.
  - **Query by attribute** — "all items with size > 5 in location X" → invert index.
  - **Merge two warehouses** — dedupe by `(name, attrs)`; capacity sum.
  - **Concurrency** — multi-worker picker; `threading.Lock` or per-location locks.
  - **Bulk move** — transactional move of N items at once.
- **Tips:**
  - **Clarify the exact suffix scheme up front** by asking "if I copy `apple` then copy `apple.dupe`, what should I get?" — silence here = wrong answer.
  - Narrate the counter approach; mention that you only scan when the counter is invalid.
- **Pitfalls:**
  - O(n) name-scan for the next free suffix (use a counter).
  - Off-by-one in copy numbering (`.copy2` starts at 2, not 1).
  - TTL flavor vs capacity flavor — they're different L3 specs.

## Company variants

- **Anthropic** — Variant A `.dupe`/`ADD_DUPLICATE_ITEMS` skin.
- **Roblox / Shopify / Amazon** — capacity + L4 move/reserve variant; sometimes weight/priority at L4.
- **DoorDash-style logistics** — "fulfillment center" reskin (location = hub, capacity = shelf space).
- Otherwise a standard ICA — pattern is identical to Q01, so **drill Q01 first**.

## Worked example trace

```
add_item("apple", {"size":3})
copy_item("apple")                    # → "apple.dupe"
copy_item("apple")                    # → "apple.copy2"
copy_item("apple.dupe")               # → "apple.copy3" (NOT apple.dupe.dupe)
delete_item("apple.dupe")
copy_item("apple")                    # → "apple.dupe" (NOT apple.copy4)
```

## Related
[[01-in-memory-key-value-database]] · [[04-cloud-storage-file-host]] · [[15-duplicate-file-detection]] (system-flavored sibling).