---
title: Design File System
slug: design-file-system
type: leetcode-design
leetcode: 1166
companies: [Google, Anthropic, Notion, Dropbox, AWS, "any cloud storage team"]
difficulty: ★★★☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 20–30 min
tags: [trie-or-hashmap, paths, validation, filesystem]
related: ["[[09-cd-directory-navigation]]", "[[21-in-memory-file-system]]", "[[22-add-search-word-trie]]"]
---

# Design File System (#1166)

Create paths with values, guarding that the **parent exists** — a clean stateful-object warm-up. Two valid approaches; pick based on follow-up likelihood.

## Problem

- `createPath(path, value) -> bool` — only if parent exists and path doesn't already exist.
- `get(path) -> int` — return value or -1.

## Core approach (format-agnostic)

**Approach A — HashMap of paths** (simpler):
- `paths: dict[path → value]`.
- Validate `parent = path.rsplit('/', 1)[0]` is root or present, and `path` not in dict.

**Approach B — Trie of components** (generalizes to listing/prefix ops):
- Each node holds `value` (or None for non-leaf) and `children: dict[str, node]`.
- Walk components; create as needed; reject if path exists.

For the **base problem**, Approach A is faster to write. Switch to Approach B only if you anticipate listing/prefix/delete follow-ups.

### Worked Python solutions

**HashMap version:**
```python
class FileSystem:
    def __init__(self):
        self.paths = {"/": -1}                # root

    def createPath(self, path: str, value: int) -> bool:
        if path in self.paths or path == "/":
            return False
        parent = path.rsplit("/", 1)[0]
        if parent and parent not in self.paths:
            return False
        self.paths[path] = value
        return True

    def get(self, path: str) -> int:
        return self.paths.get(path, -1)
```

**Trie version:**
```python
class TrieNode:
    __slots__ = ("value", "children")
    def __init__(self):
        self.value = -1                       # -1 = not a file
        self.children = {}

class FileSystem:
    def __init__(self):
        self.root = TrieNode()

    def createPath(self, path: str, value: int) -> bool:
        node = self.root
        parts = [p for p in path.split("/") if p]
        for i, p in enumerate(parts):
            if p not in node.children:
                if i == len(parts) - 1:
                    node.children[p] = TrieNode()
                else:
                    return False              # parent doesn't exist
            node = node.children[p]
            if i == len(parts) - 1 and node.value != -1:
                return False                  # already a file
        if node.value != -1:
            return False
        node.value = value
        return True

    def get(self, path: str) -> int:
        node = self.root
        for p in path.split("/"):
            if not p: continue
            if p not in node.children:
                return -1
            node = node.children[p]
        return node.value
```

**Complexity.** HashMap: O(|path|) per op. Trie: same.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:**
  - The validation (parent exists, path new) is the whole test; dict is simplest.
  - Handle the root case: `createPath('/', 5)` is invalid (already exists).
- **Pitfalls:**
  - Root parent (`""` is root's parent) — treat as always-present.
  - Duplicate create — return false.
  - Malformed path (trailing `/`, empty component) — normalize.
  - `get('/nonexistent')` → -1.

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **List children** — `ls(path) -> list[str]`; trie shines.
  - **Delete subtree** — `delete(path) -> bool`; trie makes this recursive.
  - **Rename / move** — `mv(src, dst)`; recursive trie walk.
  - **Prefix queries** — `ls_prefix(path)`. → see [[22-add-search-word-trie]].
  - **Permissions / ACL** — per-node owner/group/mode.
  - **File vs directory type** — `mkdir` separate from `touch`.
  - **Symlinks** — `softlink(target, link)`. → see [[09-cd-directory-navigation]].
  - **Watch for changes** — pub/sub on path modifications.
  - **Persistence** — serialize the trie to disk.
  - **Quota / capacity** — sum of sizes under a path; reject creates that exceed.
- **Tips:**
  - **Ask whether listing/delete will come**; if yes, build a trie up front.
  - For move: `mv(src, dst)` is `createPath(dst, get(src))` + `delete(src)` with care for cycles.
  - For watch: a callback registry keyed by path prefix.
- **Pitfalls:**
  - **Dict approach can't list children efficiently** — mention the trie trade-off.
  - **Move that creates cycles** — `mv(/a, /a/b)`; reject.
  - **Delete a non-empty dir** — usually recursive; spec varies.
  - **Concurrent modifications** — locks per path.
  - **The dict-vs-trie decision, quantified** — dict: O(|path|) ops, O(1) per-path storage, but `ls` is O(all paths) scan; trie: `ls` is O(children), delete-subtree is O(subtree), shared prefixes stored once. State the read/write mix that flips the choice — that's the answer they want, not "trie is better."
  - **Path normalization as a security question** — `createPath("/a/../b", v)`: reject or resolve? If this backs an agent/file API, resolve-then-validate ([[09-cd-directory-navigation]] jail logic); if a pure store, reject non-canonical input — say which contract you're implementing.

### Onsite · NR (Google-style)
- **Tips:** Define the path-splitting logic; trace `createPath('/a/b/c', 5)` step by step.
- **Pitfalls:** Forgetting to validate parent before adding.

## Company variants

- **Google / Anthropic / Notion / Dropbox / AWS** — common.
- Often wrapped in [[21-in-memory-file-system]] (fuller version).

## Worked example trace

```
HashMap version:
createPath("/a", 1)       # parent="" is root → ok; paths={"/":-1, "/a":1}
createPath("/a/b", 2)     # parent="/a" present → ok; paths[...]["/a/b"]=2
createPath("/a/b", 3)     # already exists → false
createPath("/a/c/d", 4)   # parent="/a/c" missing → false
get("/a/b")               # 2
get("/a/x")               # -1
```

## Related
[[21-in-memory-file-system]] (fuller version) · [[09-cd-directory-navigation]] (cd / symlinks) · [[22-add-search-word-trie]] (trie patterns).