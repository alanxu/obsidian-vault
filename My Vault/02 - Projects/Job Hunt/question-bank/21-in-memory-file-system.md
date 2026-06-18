---
title: In-Memory File System
slug: in-memory-file-system
type: leetcode-design
leetcode: 588
companies: [General]
difficulty: ★★★★☆
frequency: low-med
formats: [Live, Onsite·NR]
levels: 1
time-box: 30–40 min
tags: [trie-tree, filesystem, recursion]
related: ["[[20-design-file-system]]"]
---

# In-Memory File System (#588)

A fuller file system — directories, files, listing — modeled as a tree.

## Problem
`ls(path)` (file → its name; dir → **sorted** children); `mkdir(path)` (create intermediates); `addContentToFile(path, content)` (create/append); `readContentFromFile(path)`.

## Core approach (format-agnostic)
**Tree of nodes**: `Node{is_file, children: dict, content}`. Walk/auto-create components; `ls` returns sorted keys or the file name.

## By format

### Live · CoderPad (human) — *primary*
- **Follow-ups:** delete, move/rename, metadata + TTL (→ [[01-in-memory-key-value-database]]), permissions/ACL, symlinks (→ [[09-cd-directory-navigation]]).
- **Tips:** one `Node` class with a children dict; a single `_walk(path, create=False)` helper powers every op.
- **Pitfalls:** `ls` on a file vs dir, mkdir idempotency, append vs overwrite, root listing.

### Onsite · NR (Google-style, non-runnable)
- **Tips:** define `Node` + `_walk` by hand; trace `mkdir('/a/b')` then `ls('/a')` aloud.
- **Pitfalls:** forgetting to sort `ls`, not auto-creating intermediate dirs.

## Related
[[20-design-file-system]] · [[04-cloud-storage-file-host]].
