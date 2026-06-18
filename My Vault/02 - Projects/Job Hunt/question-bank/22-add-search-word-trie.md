---
title: Add and Search Word (Trie + wildcard)
slug: add-search-word-trie
type: leetcode-design
leetcode: 211
companies: [General]
difficulty: ★★★☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 25–35 min
tags: [trie, dfs, wildcard]
related: ["[[20-design-file-system]]"]
---

# Add and Search Word (#211)

Trie design with a `.` wildcard — the canonical trie warm-up (master #208 first).

## Problem
`addWord(word)`; `search(word)` → bool, where `.` matches any single char.

## Core approach (format-agnostic)
**Trie** `children: dict[char→node]` + `is_end`. `search` DFS: on `.`, recurse into **all** children; else follow the one; match `is_end` at the end.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** dict-children trie is cleanest; recursion or explicit stack.
- **Pitfalls:** empty word, all-wildcards, word longer than any branch, matching `is_end` (not just reaching a node).

### Live · CoderPad (human)
- **Follow-ups:** #212 Word Search II (trie + grid DFS), prefix counts, delete word, radix compaction.
- **Tips:** build the plain trie, then add the wildcard DFS branch; narrate the branching factor on `.`.
- **Pitfalls:** wildcard recursion exploding (note worst case), not handling the `.` at the last position.

## Related
#208 (plain trie), #212 (Word Search II) · [[20-design-file-system]] (trie reuse).
