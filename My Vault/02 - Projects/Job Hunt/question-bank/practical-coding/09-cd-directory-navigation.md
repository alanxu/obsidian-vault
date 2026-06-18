---
title: CD Directory Navigation
slug: cd-directory-navigation
type: live-coding
leetcode: null
companies: [OpenAI, Anthropic, Anthropic-infra, Cohere, Google-Cloud, AWS, "SysAdmin roles"]
difficulty: ★★★☆☆
frequency: medium
formats: [Live]
levels: 2
time-box: live 30–45 min
tags: [string-parsing, path-resolution, stack, soft-links, graph-cycles]
related: ["[[openai-interview-guide]]", "[[20-design-file-system]]", "[[21-in-memory-file-system]]"]
---

# CD Directory Navigation

Resolve a `cd` like a shell. Clean string/stack problem; the soft-links follow-up adds graph-ish resolution with cycle handling. The interviewer's testing two things: (1) clean segment-by-segment processing and (2) explicit handling of every special segment before coding.

## Problem

`cd(current_dir: str, change: str, soft_links: dict | None = None, home: str = "/home/user") -> str | None`

- `current_dir` — an absolute path like `/foo/bar`.
- `change` — relative or absolute path; may contain `..`, `.`, `~`.
- Return the resolved absolute path, or `None` if the result would be **above root**.
- **Follow-up:** `soft_links: dict` maps an absolute path to its target; resolve during traversal. Handle cycles.

## Segment handling

| Segment | Meaning | Action |
|---|---|---|
| `""` (empty) | path separator | skip |
| `"."` | current dir | skip |
| `".."` | parent dir | pop stack (return `None` if empty) |
| `"~"` or `"~/…"` | home dir | replace with `home` (or `home + rest`) |
| otherwise | dir/file name | push; **if candidate is a soft-link, replace stack with target** |

## Core approach (format-agnostic)

Build a `parts` stack — start empty if `change` is absolute or starts with `~`, else seeded from `current_dir`. Walk segments, applying the rules above. Soft-link resolution happens **after** each push: if the candidate path (root + current stack + new segment) is in `soft_links`, replace the stack with the target's segments. **Guard cycles** with a `visited` set + depth cap (default 32–64).

### Worked Python solution

```python
def cd(current_dir, change, soft_links=None, home="/home/user", max_depth=32):
    soft_links = soft_links or {}

    # 1. Resolve home expansion in change
    if change == "~":
        change = home
    elif change.startswith("~/"):
        change = home + change[1:]

    # 2. Initialize parts stack
    if change.startswith("/"):
        parts = []
        segments = [s for s in change.split("/") if s]
    else:
        parts = [s for s in current_dir.split("/") if s]
        segments = [s for s in change.split("/") if s]

    # 3. Walk
    for seg in segments:
        if seg in ("", "."):
            continue
        if seg == "..":
            if not parts:
                return None              # above root
            parts.pop()
            continue
        parts.append(seg)

        # 4. Soft-link resolution (with cycle guard)
        visited = set()
        while True:
            candidate = "/" + "/".join(parts)
            if candidate in visited:
                # Cycle; treat as error
                return None
            visited.add(candidate)
            if candidate not in soft_links:
                break
            target = soft_links[candidate]
            parts = [s for s in target.split("/") if s]
            if len(visited) > max_depth:
                return None              # depth cap

    return "/" + "/".join(parts) if parts else "/"
```

**Complexity.** O(|change| + |soft_links| × depth). Cycle guard makes it O(visited) per push — bounded.

## By format

### Live · CoderPad (human) — *primary*
- **How it appears:** base resolution first (~15 min), then "add symlinks" (~10 min), then probing on edge cases.
- **Follow-ups (real, reported):**
  - **Symlink cycles** — `A → B`, `B → A`; without a guard, infinite loop.
  - **Relative symlinks** — soft-link target is relative to the symlink's location, not root.
  - **Env-var expansion** — `$HOME`, `${HOME}`; substitute before processing.
  - **Case-insensitive FS** — normalize case (macOS HFS+ default, Windows NTFS).
  - **Drive letters** — Windows: `C:\foo\bar`. Add drive to the model.
  - **Permissions / access checks** — reject if segment isn't readable.
  - **Glob expansion** — `cd /foo/*` resolves all matching dirs (advanced).
  - **Validate input** — reject paths with NUL bytes, `..` segments in non-traversal context (security).
- **Tips:**
  - **Narrate the stack approach** — say "I'll keep a list of path components, and process one segment at a time."
  - **Enumerate the special segments** (`.`, `..`, `~`, `""`) **before coding**. This is the signal.
  - Write the `cd('/', '..') → None` test first.
  - For symlinks: handle cycles with a `visited` set; explain that without it, you'd recurse forever.
  - Ask: "should symlink targets be relative to the symlink's directory, or absolute?" The answer changes the code.
- **Pitfalls:**
  - **Above-root handling** — `cd('/a', '../../..')` → `None`.
  - **Trailing slashes** — `'/foo/bar/'` should equal `'/foo/bar'`.
  - **Soft-link cycles** — without `visited`, infinite loop or RecursionError.
  - **`~` mid-path** — `'/foo/~/bar'` is NOT a home reference; only at the start.
  - Empty path `cd('/foo', '')` should return `/foo`, not `/`.
  - Relative symlinks — don't assume target is absolute.

### Onsite · NR (Google-style)
- **Tips:** Define the parts stack and segment rules on the shared doc first. Trace `cd('/a/b', '../../c')` → `/c`, then `cd('/a/b', '..')` → `/a`.
- **Pitfalls:** Soft-link resolution without cycle guard.

## Company variants

- **OpenAI (canonical)** — "Problem 3" in their bank.
- **Anthropic / Cohere / Google Cloud / AWS / SysAdmin roles** — common in infrastructure-flavored interviews.
- Sometimes wrapped in "build a small filesystem shell" — extends to Q20/Q21.

## Worked example trace

```
cd("/a/b", "../c")             # parts=[a]; append c → /a/c
cd("/", "..")                  # parts=[] → None
cd("/a/b", "~")                # change=home → /home/user
cd("/a/b", "~/x")              # change="/home/user/x" → /home/user/x
cd("/a/b", "../../..")         # parts=[] → None
cd("/a/link", "x",
   soft_links={"/a/link": "/foo/bar"})  # → /foo/bar/x
cd("/a/A", "x",
   soft_links={"/a/A": "/a/B", "/a/B": "/a/A"})  # cycle → None
```

## Related
[[20-design-file-system]] · [[21-in-memory-file-system]] · [[openai-interview-guide]] P3.