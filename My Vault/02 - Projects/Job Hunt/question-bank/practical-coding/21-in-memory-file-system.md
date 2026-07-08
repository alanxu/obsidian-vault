---
title: In-Memory File System
slug: in-memory-file-system
type: leetcode-design
leetcode: 588
companies: [Google, Anthropic, Notion, Dropbox, "any cloud IDE / file service"]
difficulty: ★★★★☆
frequency: low-med
formats: [Live, Onsite·NR]
levels: 1
time-box: 30–40 min
tags: [trie-tree, filesystem, recursion, walk]
related: ["[[20-design-file-system]]", "[[04-cloud-storage-file-host]]"]
---

# In-Memory File System (#588)

A fuller file system — directories, files, listing — modeled as a tree. Builds on [[20-design-file-system]] with content operations.

## Problem

- `ls(path) -> list[str]` — file → `[name]`; directory → **sorted** children.
- `mkdir(path) -> None` — create intermediate directories as needed (idempotent).
- `addContentToFile(path, content) -> None` — create file or append to existing.
- `readContentFromFile(path) -> str` — return accumulated content.

## Core approach (format-agnostic)

**Tree of nodes:**
```
Node {
    is_file: bool,
    children: dict[str, Node],   # only for directories
    content: str                  # only for files
}
```

**One helper `_walk(path, create=False)`** powers every op. Walks components from root, creating intermediate nodes when `create=True`. Returns the destination node.

### Worked Python solution

```python
class Node:
    __slots__ = ("is_file", "children", "content")
    def __init__(self, is_file=False):
        self.is_file = is_file
        self.children = {}
        self.content = ""

class FileSystem:
    def __init__(self):
        self.root = Node()

    def _walk(self, path, create=False):
        # path is absolute, starting with "/"
        parts = [p for p in path.split("/") if p]
        node = self.root
        for p in parts:
            if p not in node.children:
                if not create:
                    return None
                node.children[p] = Node()
            node = node.children[p]
        return node

    def ls(self, path: str) -> list[str]:
        node = self._walk(path)
        if node is None:
            return []
        if node.is_file:
            return [path.rsplit("/", 1)[-1]]
        return sorted(node.children.keys())

    def mkdir(self, path: str) -> None:
        self._walk(path, create=True)

    def addContentToFile(self, path: str, content: str) -> None:
        node = self._walk(path, create=True)
        node.is_file = True
        node.content += content

    def readContentFromFile(self, path: str) -> str:
        node = self._walk(path)
        return node.content if node else ""
```

**Complexity.** O(|path|) for walk; O(F log F) for `ls` on a directory with F children.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** base in 15–20 min; follow-ups layered on.
- **Follow-ups (real, reported):**
  - **Delete** — `rm(path)`; reject if non-empty directory unless recursive.
  - **Move / rename** — `mv(src, dst)`; reject cycles.
  - **Metadata + TTL** — `mtime`, `size`, `expire_at`. → see [[01-in-memory-key-value-database]] L3.
  - **Permissions / ACL** — per-node owner/group/mode bits.
  - **Symlinks** — symbolic links resolved during walk. → see [[09-cd-directory-navigation]].
  - **File handle / cursor** — open file, read N bytes, seek.
  - **Concurrent writes** — `RLock` per path.
  - **Quota** — per-user tree capacity.
  - **Watch** — pub/sub on path changes.
  - **Find** — `find(prefix)` — recursive walk.
  - **Persistence** — serialize the tree.
  - **Content as one string breaks at scale** — `content += chunk` is O(existing) per append (string immutability) → list-of-chunks joined on read, or block storage (fixed-size blocks + index) once "seek/read N bytes" appears; the append-performance probe is the most common escalation here.
  - **Hard links** — two paths, one content node → separate the *name tree* (dentries) from *content nodes* (inodes) with refcounts; one sentence of real-FS vocabulary (inode vs dentry) reframes your whole design as informed, not improvised.
- **Tips:**
  - **One `Node` class with a children dict** — uniform code path.
  - **A single `_walk(path, create=False)` helper** powers every op.
  - For TTL: store `expire_at` on the node; lazy check on read.
  - For move: detach node from old parent, attach to new parent; reject if `dst` is under `src` (cycle).
- **Pitfalls:**
  - **`ls` on a file vs dir** — file returns `[name]`, dir returns sorted children. Easy to mix up.
  - `mkdir` idempotency — calling twice should succeed.
  - `addContentToFile` append vs overwrite — most specs say append.
  - **Root listing** — `ls('/')` should return root's children.
  - **Trailing slash** — `/a/b/` should equal `/a/b`.
  - **Auto-creating intermediate dirs in `addContentToFile`** — usually expected.

### Onsite · NR (Google-style, non-runnable)
- **Tips:**
  - Define `Node` + `_walk` by hand.
  - Trace `mkdir('/a/b')` then `ls('/a')` aloud.
- **Pitfalls:**
  - Forgetting to sort `ls`.
  - Not auto-creating intermediate dirs.

### Take-home / work-trial
- **Tips:** Ship the base + delete + move + a watch API + a `tree()` pretty-printer for debug.
- **Pitfalls:**
  - Move without cycle check.
  - No tests for the content-append behavior.

## Company variants

- **Google / Anthropic / Notion / Dropbox** — common.
- **Cloud IDEs** (Replit, CodeSandbox, GitHub Codespaces) — production-flavored.

## Worked example trace

```
mkdir("/a/b")
addContentToFile("/a/b/c.txt", "hello ")
addContentToFile("/a/b/c.txt", "world")
ls("/a")              # ["b"]
ls("/a/b")            # ["c.txt"]
ls("/a/b/c.txt")      # ["c.txt"]            # file case
readContentFromFile("/a/b/c.txt")  # "hello world"
```

## Related
[[20-design-file-system]] (simpler sibling) · [[04-cloud-storage-file-host]] · [[09-cd-directory-navigation]] (symlinks).