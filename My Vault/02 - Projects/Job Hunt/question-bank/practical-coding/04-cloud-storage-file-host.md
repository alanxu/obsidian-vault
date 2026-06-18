---
title: Cloud Storage / File Host
slug: cloud-storage-file-host
type: multi-level-stateful
leetcode: null
companies: [Dropbox, Google-Drive, Anthropic, Box, "The Trade Desk", CodeSignal cos, AWS-S3-style, "Backblaze/B2"]
difficulty: ★★★★☆
frequency: medium
formats: [OA·ICA, Live]
levels: 4
time-box: 90 min for 4 levels
tags: [oo-design, users, capacity, ranking, merge, backup, heap, partial-sort]
related: ["[[01-in-memory-key-value-database]]", "[[21-in-memory-file-system]]", "[[15-duplicate-file-detection]]"]
---

# Cloud Storage / File Host

A CodeSignal ICA staple: **files with sizes → users with capacity → merges & backups**. Tests your ability to manage two related state machines (files and users) and answer top-k queries efficiently.

## Problem (by level)

### L1 — Files
- `add_file(name, size) -> bool` — `false` if name exists.
- `get_file_size(name) -> int | ""` — `""` if missing.
- `delete_file(name) -> int | None` — return the freed size, or `None`/`-1` if missing.

### L2 — Query
- `get_n_largest(prefix, n) -> str` — top-N file names by **size desc**, **tie-break by name asc**, **prefix-matched**. Format `"name(size), name(size), …"`.

### L3 — Users + capacity
- `add_user(id, capacity) -> bool`.
- `add_file_by(user, name, size) -> bool` — file counts against the user's remaining capacity; **reject if it would exceed**.
- `merge_user(id_a, id_b) -> bool` — combine users (sum capacities, transfer files; **decide** collision policy: keep both names? rename conflicts? Spec varies — usually rename `b/name` → `a/name` on conflict).

### L4 — Backup / restore
- `backup_user(id) -> bool` — snapshot the user's current state (file ownership + remaining capacity).
- `restore_user(id) -> bool` — restore from the latest snapshot. **Re-check capacity** (if the user has consumed more capacity since the backup, restore rejects OR overwrites — read spec).

## Core approach (format-agnostic)

### Storage
- `files: dict[name → (size, owner|None)]`
- `users: dict[id → {"cap": int, "used": int, "files": set, "backups": [snapshots]}]`

### Capacity check
A single comparison `used + size ≤ capacity` — **before** any mutation.

### `get_n_largest(prefix, n)`
Two viable approaches. Pick based on query frequency vs update frequency:
- **Per-query scan + heap** — filter prefix, push into min-heap of size `n`, pop smallest when size > n. O(F log n) where F is matching files.
- **Maintain a sorted structure** (SortedList from `sortedcontainers`, or a custom index) for O(log F) update + O(n) top.

For ICA grading the **heap approach is fast enough** and simpler to write correctly. Reach for SortedList only if the interviewer asks for scale.

### Merge
Decide and document the collision policy:
- **Drop conflicts** from `b` — simple, lossy.
- **Rename conflicts** — `b/name` → `a/name-{ts}` or `a/name (copy)`. Spec-dependent.

### Worked Python solution

```python
import heapq

class CloudStorage:
    def __init__(self):
        self.files = {}                 # name -> (size, owner)
        self.users = {}                 # id -> {"cap","used","files","backups"}

    # ---------- L1 ----------
    def add_file(self, name, size):
        if name in self.files:
            return False
        self.files[name] = (size, None)
        return True

    def get_file_size(self, name):
        if name not in self.files:
            return ""
        return self.files[name][0]

    def delete_file(self, name):
        if name not in self.files:
            return -1
        size, owner = self.files[name]
        if owner and owner in self.users:
            self.users[owner]["used"] -= size
            self.users[owner]["files"].discard(name)
        del self.files[name]
        return size

    # ---------- L2 ----------
    def get_n_largest(self, prefix, n):
        heap = []
        for name, (size, _) in self.files.items():
            if not name.startswith(prefix):
                continue
            # sort key: (-size, name) — we want size desc, name asc
            if len(heap) < n:
                heapq.heappush(heap, (size, name))
            else:
                # worst (smallest) is at root; size asc, name asc
                if heap and (size, name) > heap[0]:
                    heapq.heapreplace(heap, (size, name))
        # Sort the result: size desc, name asc
        result = sorted(heap, key=lambda x: (-x[0], x[1]))
        return ", ".join(f"{n}({s})" for s, n in result)

    # ---------- L3 ----------
    def add_user(self, uid, capacity):
        if uid in self.users:
            return False
        self.users[uid] = {"cap": capacity, "used": 0, "files": set(), "backups": []}
        return True

    def add_file_by(self, uid, name, size):
        if name in self.files or uid not in self.users:
            return False
        u = self.users[uid]
        if u["used"] + size > u["cap"]:
            return False                 # reject BEFORE mutation
        self.files[name] = (size, uid)
        u["used"] += size
        u["files"].add(name)
        return True

    def merge_user(self, dst, src):
        if dst not in self.users or src not in self.users or dst == src:
            return False
        d, s = self.users[dst], self.users[src]
        d["cap"] += s["cap"]
        # transfer files; on collision, rename src's to avoid clash
        for name in list(s["files"]):
            if name in d["files"]:
                new_name = f"{name}_{src}"
                self.files[new_name] = (self.files[name][0], dst)
                d["files"].add(new_name)
                d["used"] += self.files[name][0]
            else:
                self.files[name] = (self.files[name][0], dst)
                d["files"].add(name)
                d["used"] += self.files[name][0]
            s["files"].discard(name)
        s["files"].clear()
        s["used"] = 0
        return True

    # ---------- L4 ----------
    def backup_user(self, uid):
        if uid not in self.users:
            return False
        u = self.users[uid]
        import copy
        snap = {"cap": u["cap"], "used": u["used"], "files": set(u["files"])}
        u["backups"].append(snap)
        return True

    def restore_user(self, uid):
        u = self.users.get(uid)
        if not u or not u["backups"]:
            return False
        snap = u["backups"][-1]
        # drop current files belonging to user
        for name in list(u["files"]):
            if name in self.files:
                del self.files[name]
        # restore files
        for name in snap["files"]:
            if name in self.files:
                # keep restored file with original size; reassign owner
                self.files[name] = (self.files[name][0], uid)
                u["used"] += self.files[name][0]
        u["cap"] = snap["cap"]
        return True
```

**Complexity.** CRUD O(1). `get_n_largest` O(F log n). Merge O(|src.files|). Backup/restore O(|user.files|).

## By format

### OA · ICA (CodeSignal, 4 levels)
- **How it appears:** 4 levels; L1/L2 trivial; L3/L4 is where most candidates lose time.
- **Tips:**
  - Keep `used` **incrementally** — don't recompute by summing file sizes on every query.
  - Exact tie-break (size desc, then name asc) for `get_n_largest`. The heap order matters; verify with a 3-element test.
  - For capacity, reject **before** mutating state — partial-update bugs are the #1 cause of failed hidden tests.
- **Pitfalls:**
  - Over-capacity insert mutating before the check fails.
  - `delete` returning freed size only when there was an owner (consistency check).
  - Merge name clashes silently dropped (lose data) or duplicated.
  - Restore exceeding current capacity (spec varies — confirm).

### Live · CoderPad
- **Follow-ups:**
  - **Per-user TTL** — files expire after N days; lazy vs sweep.
  - **Dedupe identical files** — content hash, store one copy + refcount. → see [[15-duplicate-file-detection]].
  - **Sharing / ACLs** — files visible to a group of users; per-user quota vs shared quota.
  - **Compression** — `add_file(name, content) -> name`; on dedupe, count saved bytes.
  - **Pagination** — `get_n_largest(prefix, n, page)` for very large result sets.
  - **Migration** — move a user's files to another user with progress tracking.
- **Tips:**
  - Narrate the **two-map design** (files vs users).
  - **Clarify merge semantics** (capacity sum? file overwrite? rename?) — different specs change the implementation.
  - For `get_n_largest` at scale, mention the SortedList alternative.
- **Pitfalls:**
  - `get_n_largest` sorting everything when a heap would suffice.
  - Forgetting the prefix filter (returning all files).
  - Restore that overwrites files added after backup without warning.

## Company variants

- **Dropbox / Google Drive / Box** — canonical skin; merging is common.
- **Anthropic** — sometimes appears with file-compression at L4 (gzip in-memory).
- **AWS-S3 / Backblaze B2** — capacity is the bucket quota; L4 is bucket versioning.
- **The Trade Desk** — ad-asset storage reskin; dedupe is the L4 focus.

## Worked example trace

```
add_user("u1", 100); add_user("u2", 100)
add_file_by("u1", "a.txt", 30)         # u1.used = 30
add_file_by("u1", "b.txt", 50)         # u1.used = 80
add_file_by("u1", "c.txt", 30)         # 80 + 30 > 100 → False
add_file_by("u2", "ab.txt", 25)
get_n_largest("a", 3)                  # a.txt(30), ab.txt(25)
merge_user("u1", "u2")                 # u1.cap = 200, used = 105; ab.txt now owned by u1
```

## Related
[[01-in-memory-key-value-database]] · [[21-in-memory-file-system]] · [[15-duplicate-file-detection]] · [[04-cloud-storage-file-host]].