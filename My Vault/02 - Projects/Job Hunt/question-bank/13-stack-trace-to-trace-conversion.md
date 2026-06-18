---
title: Stack-Trace → Trace Conversion
slug: stack-trace-to-trace-conversion
type: live-coding
leetcode: null
companies: [Anthropic]
difficulty: ★★★★★
frequency: high
formats: [Live]
levels: 2
time-box: live 45–60 min
tags: [stack, longest-common-prefix, profiling, recursion]
related: ["[[anthropic-interview-guide]]", "[[14-exclusive-execution-time]]"]
---

# Stack-Trace → Trace Conversion

The viral 2025 Anthropic question and the **hardest** of the live bank. Convert timestamped stack **samples** into start/end **events** for a flamegraph. The trick is LCP-diffing consecutive stacks.

## Problem
Samples `(ts, [frames outer→inner])` → emit `(ts, 'start'|'end', frame)`. Inner ends before outer; handle recursion. **Follow-up:** only emit a frame stable for **≥N consecutive samples**. Code: [[anthropic-interview-guide]] worked solution (a).

## Core approach (format-agnostic)
Track a "current stack." Per new sample, compute the **longest common prefix** with the previous: frames in `prev` below the LCP **ended** (emit deepest-first); frames in the new stack below the LCP **started** (emit shallow→deep). Identity = `(depth, name)` so recursion just works. Finalize by closing remaining frames. O(S) total.

## By format

### Live · CoderPad (human) — *primary (Anthropic)*
- **How it appears:** the interviewer wants the **insight** (LCP-diff) more than tidy code; expect to derive it on the spot.
- **Follow-ups:** ≥N-stable emission (track per-depth streaks, emit start at streak's first ts), only-leaf events, merge identical adjacent frames.
- **Tips:** **work a tiny example by hand first** (2–3 samples) to discover the LCP rule, then code; narrate "bigger prev ⇒ ends, bigger new ⇒ starts."
- **Pitfalls:** wrong emit order (ends deepest-first, starts shallow-first), recursion treated as one frame, forgetting to close frames at the end, equal consecutive stacks (LCP=full → no events).

## Related
[[14-exclusive-execution-time]] (sibling stack-simulation) · [[anthropic-interview-guide]] (a).
