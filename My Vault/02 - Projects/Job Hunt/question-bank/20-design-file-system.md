---
title: Design File System
slug: design-file-system
type: leetcode-design
leetcode: 1166
companies: [General, labs]
difficulty: ★★★☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 20–30 min
tags: [trie-or-hashmap, paths, validation]
related: ["[[09-cd-directory-navigation]]", "[[21-in-memory-file-system]]"]
---

# Design File System (#1166)

Create paths with values, guarding that the **parent exists** — a clean stateful-object warm-up.

## Problem
`createPath(path, value)` (only if parent exists and path doesn't); `get(path)` → value or −1.

## Core approach (format-agnostic)
A **dict `path→value`** suffices: validate `parent = path.rsplit('/',1)[0]` is root or present, and `path` absent. A **trie** of components generalizes to listing/prefix ops.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** the validation (parent exists, path new) is the whole test; dict is simplest.
- **Pitfalls:** root parent (`""`), duplicate create, malformed path (trailing `/`, empty component).

### Live · CoderPad (human)
- **Follow-ups:** list children, delete subtree (**trie** shines), rename/move, prefix queries (→ [[22-add-search-word-trie]]).
- **Tips:** ask whether listing/delete will come; if yes, build a trie up front.
- **Pitfalls:** dict approach can't list children efficiently (mention the trie trade-off).

## Related
[[21-in-memory-file-system]] · [[09-cd-directory-navigation]].
