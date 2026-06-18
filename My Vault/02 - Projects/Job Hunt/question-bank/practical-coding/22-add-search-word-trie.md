---
title: Add and Search Word (Trie + wildcard)
slug: add-search-word-trie
type: leetcode-design
leetcode: 211
companies: [Google, Amazon, Meta, "any search/autocomplete team", "Word search games"]
difficulty: ★★★☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 25–35 min
tags: [trie, dfs, wildcard, autocomplete]
related: ["[[20-design-file-system]]", "[[#208 Implement Trie]]"]
---

# Add and Search Word (#211)

Trie design with a `.` wildcard — the canonical trie warm-up (master **#208** first).

## Problem

- `addWord(word)` — store the word in a trie.
- `search(word) -> bool` — does any stored word match `word`, where `.` matches any single character?

## Core approach (format-agnostic)

**Trie** `children: dict[char → node]` + `is_end: bool`.

`addWord`: walk characters, creating nodes as needed; mark the final node `is_end = True`.

`search`: DFS with the wildcard branch — on `.`, recurse into **all** children; otherwise follow the one. At the end, return whether `is_end` is set.

### Worked Python solution

```python
class TrieNode:
    __slots__ = ("children", "is_end")
    def __init__(self):
        self.children = {}
        self.is_end = False

class WordDictionary:
    def __init__(self):
        self.root = TrieNode()

    def addWord(self, word: str) -> None:
        node = self.root
        for ch in word:
            if ch not in node.children:
                node.children[ch] = TrieNode()
            node = node.children[ch]
        node.is_end = True

    def search(self, word: str) -> bool:
        return self._dfs(self.root, word, 0)

    def _dfs(self, node, word, i):
        if i == len(word):
            return node.is_end
        ch = word[i]
        if ch == ".":
            return any(self._dfs(child, word, i + 1)
                       for child in node.children.values())
        if ch not in node.children:
            return False
        return self._dfs(node.children[ch], word, i + 1)
```

**Complexity.** `addWord`: O(|word|). `search`: O(|word| × branching); worst-case exponential in wildcards.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:**
  - Dict-children trie is cleanest; recursion or explicit stack.
  - For very long words with many wildcards, pruning helps.
- **Pitfalls:**
  - Empty word — `search("")` returns `True` iff `root.is_end` (usually False).
  - All-wildcards — `search("...")` matches any 3-char word.
  - Word longer than any branch — returns False correctly.
  - **Matching `is_end` (not just reaching a node)** — the difference between prefix and full word.

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **#212 Word Search II** (trie + grid DFS) — find all dictionary words in a grid.
  - **Prefix counts** — how many words share this prefix.
  - **Delete word** — unmark `is_end`; optionally prune empty branches.
  - **Radix compaction** — collapse single-child chains into one edge (saves space, complicates DFS).
  - **Autocomplete** — return top-K words matching a prefix.
  - **Search with `*`** — match zero or more characters (regex-lite); usually a DP problem.
  - **Concurrency** — multi-thread adds/searches; locks per node or global.
  - **Persistence** — serialize the trie to disk.
  - **Compressed / DAWG** — directed acyclic word graph; same content with shared suffixes.
- **Tips:**
  - **Build the plain trie, then add the wildcard DFS branch.**
  - **Narrate the branching factor on `.`** — set context for complexity analysis.
  - For autocomplete: DFS through the subtree, collecting words up to K.
  - For #212: prune the trie as you find words (mark `found`); big perf win.
- **Pitfalls:**
  - **Wildcard recursion exploding** — worst-case exponential; note it.
  - **Not handling `.` at the last position** — should still check `is_end` at the end.
  - **Delete without pruning** — leaves dead branches; usually OK, but document.
  - **Concurrency race on `is_end`** — locks if needed.

### Onsite · NR (Google-style)
- **Tips:** Draw a small trie (3 words) and trace `search(".at")`.
- **Pitfalls:** Forgetting the `is_end` check at leaf.

## Company variants

- **Google / Amazon / Meta** — classic.
- **Search / autocomplete teams** — production-flavored.
- **Word games** (Words With Friends) — common.

## Worked example trace

```
addWord("bad")
addWord("dad")
addWord("mad")

search("pad")    # False
search("bad")    # True
search(".ad")    # True (matches bad, dad, mad)
search("b..")    # True (matches bad)
search("b.d")    # True (matches bad)
search("...")    # True
search("....")   # False (no 4-char word)
```

## Related
#208 (plain trie) · #212 (Word Search II) · [[20-design-file-system]] (trie reuse).