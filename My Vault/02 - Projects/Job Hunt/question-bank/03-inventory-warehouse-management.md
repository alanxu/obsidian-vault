---
title: Inventory / Warehouse Management
slug: inventory-warehouse-management
type: multi-level-stateful
leetcode: null
companies: [Anthropic (inventory variant), CodeSignal cos]
difficulty: ★★★☆☆
frequency: medium
formats: [OA·ICA, Live]
levels: 4
time-box: 90 min for 4 levels
tags: [oo-design, duplicates, naming, capacity]
related: ["[[01-in-memory-key-value-database]]"]
---

# Inventory / Warehouse Management

Anthropic's reported variant uses item **copies with auto-suffixed names**. Same extend-across-levels skeleton as [[01-in-memory-key-value-database]].

## Problem (by level)
- **L1:** `add_item(name, attrs)`, `get_item(name)`, `delete_item(name)`.
- **L2 — duplicates:** `copy_item(name)` → `name.dupe` / `name.copy2` …; `add_duplicate_items(name, k)`; collision-safe naming.
- **L3 — capacity / TTL:** per-location capacity limits or item TTL/expiry; reject or evict when over.
- **L4 — snapshot / move:** `backup`/`restore`, or `move(item, loc_a, loc_b)` respecting capacity.

## Core approach (format-agnostic)
Items in a dict; **per-base-name counter** for O(1) collision-free copy naming. Capacity = a per-location counter checked before insert. TTL/backup = reuse the version-list + timestamp primitive from Q01.

## By format

### OA · ICA (CodeSignal, 4 levels)
- **Tips:** get the **suffix algorithm** exactly right (graders check `.dupe`, `.copy2` naming and collision handling); keep capacity as a simple counter.
- **Pitfalls:** copy-of-a-copy naming, suffix collision when `x.dupe` already exists, restoring over capacity, deleting an original with live copies.

### Live · CoderPad
- **Follow-ups:** cheapest restock, query by attribute, merge two warehouses (dedupe), concurrency.
- **Tips:** clarify the exact suffix scheme up front (it varies); narrate the counter approach.
- **Pitfalls:** O(n) name-scan for the next free suffix (use a counter), off-by-one in copy numbering.

## Company variants
Anthropic's `.dupe`/`ADD_DUPLICATE_ITEMS` inventory skin; otherwise standard ICA. Pattern is identical to Q01 — drill that first.

## Related
[[01-in-memory-key-value-database]] · [[04-cloud-storage-file-host]].
