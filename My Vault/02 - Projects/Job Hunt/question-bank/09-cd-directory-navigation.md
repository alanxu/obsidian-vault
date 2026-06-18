---
title: CD Directory Navigation
slug: cd-directory-navigation
type: live-coding
leetcode: null
companies: [OpenAI]
difficulty: ★★★☆☆
frequency: medium
formats: [Live]
levels: 2
time-box: live 30–45 min
tags: [string-parsing, path-resolution, stack, soft-links]
related: ["[[openai-interview-guide]]", "[[20-design-file-system]]"]
---

# CD Directory Navigation

Resolve a `cd` like a shell. Clean string/stack problem; the soft-links follow-up adds graph-ish resolution.

## Problem
`cd(current_dir, new_dir) -> str | None`: absolute vs relative; handle `.`, `..`, `~`; collapse slashes; `None` if above root. **Follow-up:** `soft_links: dict` resolved during traversal.

## Core approach (format-agnostic)
Build a `parts` stack (start `[]` if absolute/home, else split `current_dir`). Per segment: `''`/`.` skip; `..` pop (None if empty); else push — and if the candidate path is a soft link, replace `parts` with the resolved target (guard cycles with a visited set). Code + tests: [[openai-interview-guide]] Problem 3.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** base resolution, then "add symlinks."
- **Follow-ups:** symlink **cycles**, relative symlinks, env-var expansion, case-insensitive FS.
- **Tips:** narrate the stack approach; enumerate the special segments (`.`/`..`/`~`/`''`) before coding; write the `cd('/', '..') → None` test.
- **Pitfalls:** above-root handling, trailing slashes, **soft-link cycles** (infinite loop without a visited-set + depth cap), `~` mid-path.

## Related
[[20-design-file-system]] · [[21-in-memory-file-system]] · [[openai-interview-guide]] P3.
