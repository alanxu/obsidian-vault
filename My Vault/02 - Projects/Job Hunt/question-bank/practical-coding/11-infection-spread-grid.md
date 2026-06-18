---
title: Infection / Virus Spread on a Grid
slug: infection-spread-grid
type: simulation
leetcode: 994
companies: [OpenAI, Anthropic, Google, Amazon, Roblox, Databricks, "any DSA interview"]
difficulty: ★★★☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 2
time-box: 30–45 min
tags: [bfs, grid, multi-source, simulation]
related: ["[[openai-interview-guide]]", "[[Track A graphs]]"]
---

# Infection / Virus Spread on a Grid

The one mostly-algorithmic item in the practical bank: **multi-source BFS** (a Rotting-Oranges variant, LC **#994**). Tests your ability to coordinate parallel "spread" — the canonical "all sources advance together" pattern.

## Problem

Grid `m × n` of cells. Each cell is one of:
- `0` — empty
- `1` — healthy
- `2` — infected
- `3` — obstacle (immutable)

Each minute, every infected cell spreads to its **4-directional neighbors** (up/down/left/right) that are healthy. Obstacles block spread. Return either:
- **Grid after `k` minutes** (mutation variant), OR
- **Minutes until all reachable healthy are infected** (return `-1` if any are unreachable).

## Core approach (format-agnostic)

**Multi-source BFS:**
1. **Seed** the queue with **all** initially-infected cells at time `0`.
2. **Count** initial healthy cells.
3. **Pop** each cell, infect 4-dir healthy neighbors, push `(r, c, t+1)`.
4. When healthy count reaches `0`, the answer is the last `t`. If queue drains with healthy left → `-1`.

The "all sources advance together" is the key insight: seed **all** infected cells, not one at a time. This collapses what would be O(k × sources) work into O(m·n).

### Worked Python solution

```python
from collections import deque

def minutes_to_infect(grid):
    rows, cols = len(grid), len(grid[0])
    q = deque()
    healthy = 0

    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 2:
                q.append((r, c, 0))
            elif grid[r][c] == 1:
                healthy += 1

    if healthy == 0:
        return 0                                # nothing to infect

    minutes = 0
    while q:
        r, c, t = q.popleft()
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                grid[nr][nc] = 2                # mark infected (mutates)
                healthy -= 1
                q.append((nr, nc, t + 1))
                minutes = t + 1
        if healthy == 0:
            return minutes
    return -1                                  # unreachable healthy remain

def grid_after_k(grid, k):
    """Mutation variant: return the grid state after k minutes."""
    import copy
    work = copy.deepcopy(grid)
    rows, cols = len(work), len(work[0])
    q = deque()
    for r in range(rows):
        for c in range(cols):
            if work[r][c] == 2:
                q.append((r, c, 0))

    while q:
        r, c, t = q.popleft()
        if t == k:
            continue                            # don't spread past k
        for dr, dc in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < rows and 0 <= nc < cols and work[nr][nc] == 1:
                work[nr][nc] = 2
                q.append((nr, nc, t + 1))
    return work
```

**Complexity.** O(m·n) time, O(m·n) space for the queue.

## By format

### OA · GCA / HackerRank (auto-graded)
- **How it appears:** as a standalone grid simulation with hidden tests.
- **Tips:**
  - **Multi-source seed** — push all `2`s at t=0.
  - **Count healthy up front** — return early if 0.
  - Use a copy for the mutation variant (the input is usually read-only).
- **Pitfalls:**
  - "No infected initially → 0 if no healthy else −1" — easy to flip.
  - Obstacles: some variations call them `-1` or `4`; read the spec.
  - Bounds: `nr < rows` not `nr ≤ rows`.
  - Forgetting that infection can't spread through already-infected cells (no double-push).

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **8-directional spread** — diagonals included.
  - **Multiple infection types** — `2` and `4` are different strains, each with their own spread rules.
  - **Probabilistic spread** — `p` chance per minute; expected-time computation.
  - **Very large sparse grid** — store only active cells (cells with neighbors); use a dict.
  - **Multiple end-states** — return minutes-to-each-cell instead of just max.
  - **Animation / render** — `grid_at_time(t)` to support playback.
  - **Reverse** — given a final grid, find all possible initial configurations.
- **Tips:**
  - **Narrate why multi-source BFS** — all sources advance together.
  - **State the −1 condition** explicitly before coding.
  - For sparse grids, the dict-of-cells approach generalizes BFS to unbounded territory.
- **Pitfalls:**
  - **Mutating the grid while iterating the current frontier** — use level-by-level or push-then-mark.
  - **Counting minutes off-by-one** — the last infection happens at minute `t`, and the answer is `t`.
  - **Skipping obstacles** — check `grid[nr][nc] != 3` (or whatever the obstacle sentinel is).
  - **Forgetting the empty-queue / no-healthy edge case**.

### Onsite · NR (Google-style)
- **Tips:** Draw the queue state on a 4×4 example; trace each pop.
- **Pitfalls:** Forgetting to seed all infected cells.

## Company variants

- **OpenAI / Anthropic / Google / Amazon / Roblox / Databricks** — common in any DSA interview as a BFS warm-up.
- Sometimes reskinned as "rumor spread in a social network" (sparse variant).

## Worked example trace

```
Grid:
2 1 0
1 1 0
0 0 1

Initial: queue=[(0,0,0)], healthy=4
Pop (0,0,0): infect (0,1) and (1,0). healthy=2. queue=[(1,0,1),(0,1,1)].
Pop (1,0,1): infect (1,1). healthy=1. queue=[(0,1,1),(1,1,2)].
Pop (0,1,1): no healthy neighbors.
Pop (1,1,2): no healthy neighbors.
Queue empty, healthy=1 → return -1.
(The (2,2) cell is unreachable due to the 0-column barrier.)
```

## Related
Track A graphs (#994/#286 multi-source BFS) · [[openai-interview-guide]] P7.