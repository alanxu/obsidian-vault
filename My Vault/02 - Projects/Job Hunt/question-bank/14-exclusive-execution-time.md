---
title: Exclusive Execution Time from Logs
slug: exclusive-execution-time
type: live-coding
leetcode: 636
companies: [Anthropic]
difficulty: ★★★☆☆
frequency: high
formats: [Live, OA·GCA/HR]
levels: 2
time-box: 30–45 min
tags: [stack, simulation, timestamps, streaming, heap]
related: ["[[13-stack-trace-to-trace-conversion]]", "[[anthropic-interview-guide]]"]
---

# Exclusive Execution Time from Logs

LeetCode **#636**, Anthropic-flavored. Exclusive (self) time per function from chronological START/END logs via a stack.

## Problem
Logs `(id, 'START'|'END', timestamp)` chronological. Return exclusive time per id. **Follow-ups:** equal timestamps; **out-of-order stream** (buffer); detect N consecutive identical events. Code: [[anthropic-interview-guide]] worked solution (b).

## Core approach (format-agnostic)
Stack of active ids. On each event add `t − prev` to the top function, then push (START) / pop (END), update `prev`. Half-open timing: s→e lasts `e−s`. O(N).

## By format

### Live · CoderPad (human) — *primary (Anthropic)*
- **Follow-ups:** **out-of-order stream** → min-heap keyed `(timestamp, arrival_index)`; once heap > `max_delay`+1, pop smallest and process (O(max_delay) buffer, corrects local disorder online).
- **Tips:** narrate half-open timing and the tie-break preserving arrival order; dry-run nested calls.
- **Pitfalls:** double-counting at equal timestamps, recursion (same id nested), unbalanced logs.

### OA · GCA / HackerRank (#636, auto-graded)
- **Tips:** the plain #636 — single stack, careful at START-after-END at the same timestamp.
- **Pitfalls:** off-by-one on the `e−s` vs `e−s+1` convention (read the problem's definition).

## Related
[[13-stack-trace-to-trace-conversion]] · [[anthropic-interview-guide]] (b).
