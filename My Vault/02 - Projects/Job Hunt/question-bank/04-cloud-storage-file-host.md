---
title: Cloud Storage / File Host
slug: cloud-storage-file-host
type: multi-level-stateful
leetcode: null
companies: [CodeSignal cos, Anthropic, Dropbox-style]
difficulty: ★★★★☆
frequency: medium
formats: [OA·ICA, Live]
levels: 4
time-box: 90 min for 4 levels
tags: [oo-design, users, capacity, ranking, merge, backup]
related: ["[[01-in-memory-key-value-database]]", "[[21-in-memory-file-system]]"]
---

# Cloud Storage / File Host

CodeSignal ICA staple: files with sizes → **users with capacity** → merges & backups.

## Problem (by level)
- **L1:** `add_file(name, size)` (false if exists), `get_file_size(name)`, `delete_file(name)` → freed size or null.
- **L2 — query:** `get_n_largest(prefix, n)` → top-N file names by size (tie-break lexicographic), prefix-matched.
- **L3 — users + capacity:** `add_user(id, capacity)`; `add_file_by(user, name, size)` (reject if over remaining capacity); `merge_user(a, b)`.
- **L4 — backup/restore:** `backup_user(id)`; `restore_user(id)` (re-check capacity / overwrite current).

## Core approach (format-agnostic)
`files: name → (size, owner)`; `users: id → {capacity, used, files}`. Capacity check `used + size ≤ capacity`. `get_n_largest` = filter prefix → heap of size n. Merge: move ownership + sum remaining capacity, resolve clashes.

## By format

### OA · ICA (CodeSignal, 4 levels)
- **Tips:** keep `used` incrementally (don't recompute), exact tie-break (size desc, then name asc) for `get_n_largest`.
- **Pitfalls:** over-capacity insert must reject **before** mutating, delete returning freed size, merge name clashes, restore exceeding current capacity.

### Live · CoderPad
- **Follow-ups:** per-user TTL, **dedupe identical files** (content hash → [[15-duplicate-file-detection]]), sharing/ACLs, compaction.
- **Tips:** narrate the two-map design; clarify merge semantics (capacity sum? file overwrite?).
- **Pitfalls:** `get_n_largest` sorting everything (use a heap), forgetting prefix filter.

## Related
[[01-in-memory-key-value-database]] · [[21-in-memory-file-system]] · [[15-duplicate-file-detection]].
