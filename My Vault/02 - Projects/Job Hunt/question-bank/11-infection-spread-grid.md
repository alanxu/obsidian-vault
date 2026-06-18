---
title: Infection / Virus Spread on a Grid
slug: infection-spread-grid
type: simulation
leetcode: 994
companies: [OpenAI, general]
difficulty: ★★★☆☆
frequency: medium
formats: [OA·GCA/HR, Live]
levels: 2
time-box: 30–45 min
tags: [bfs, grid, multi-source, simulation]
related: ["[[openai-interview-guide]]"]
---

# Infection / Virus Spread on a Grid

The one mostly-algorithmic item in the practical bank: multi-source BFS (a Rotting-Oranges variant, LC **#994**).

## Problem
Grid: `0`=empty, `1`=healthy, `2`=infected, `3`=obstacle. Each minute infected cells spread to 4-dir healthy neighbors (not obstacles). Return grid after `k` minutes **or** minutes until all reachable healthy infected (`-1` if some can't be). Code: [[openai-interview-guide]] Problem 7.

## Core approach (format-agnostic)
**Multi-source BFS:** seed queue with all `2` cells at t=0; pop, infect neighbors, push `t+1`. Track remaining healthy; reach 0 → answer = last minute; queue drains with healthy left → `-1`. O(m·n).

## By format

### OA · GCA / HackerRank (auto-graded)
- **How it appears:** as a standalone grid simulation with hidden tests.
- **Tips:** multi-source seed (not single BFS per cell); count healthy up front.
- **Pitfalls:** forgetting "no infected initially → 0 if no healthy else −1", obstacles, bounds.

### Live · CoderPad (human)
- **Follow-ups:** 8-directional, multiple infection types, probabilistic spread, very large **sparse** grid (store only active cells).
- **Tips:** narrate why multi-source BFS (all sources advance together); state the −1 condition.
- **Pitfalls:** mutating the grid while iterating the current frontier (use level-by-level), counting minutes off-by-one.

## Related
Track A graphs (#994/#286 multi-source BFS) · [[openai-interview-guide]] P7.
