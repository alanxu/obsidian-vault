---
title: Stack-Trace → Trace Conversion
slug: stack-trace-to-trace-conversion
type: live-coding
leetcode: null
companies: [Anthropic, OpenAI, Datadog, Honeycomb, Sentry, "any observability/profiling team"]
difficulty: ★★★★★
frequency: high
formats: [Live]
levels: 2
time-box: live 45–60 min
tags: [stack, longest-common-prefix, profiling, recursion, flamegraph]
related: ["[[14-exclusive-execution-time]]", "[[anthropic-interview-guide]]"]
---

# Stack-Trace → Trace Conversion

The viral 2025 Anthropic question and the **hardest** of the live bank. Convert timestamped stack **samples** into start/end **events** for a flamegraph. The trick is **LCP-diffing consecutive stacks** — once you see it, the rest is bookkeeping. Tests whether you can derive an insight on the spot, not whether you can grind LeetCode.

## Problem

You're given a sequence of samples: `(timestamp, [frames_outer_to_inner])`. Examples:

```
(0,   ["main", "foo", "bar"])
(10,  ["main", "foo", "bar"])     # unchanged
(20,  ["main", "foo"])            # bar returned
(30,  ["main", "foo", "baz"])     # baz started
```

Produce a stream of events: `(timestamp, 'start'|'end', frame)`. The semantic constraint: **inner frames end before outer frames**. Recursion (same frame name at multiple depths) must work correctly.

**Follow-up:** only emit a frame's start when it has been stable for **≥ N consecutive samples** (to filter jitter / sampling noise).

## Core approach (format-agnostic)

The single insight: per sample, compare to the **previous** stack. Find the **longest common prefix (LCP)**.

- Frames in `prev` **below** the LCP depth **ended** (emit 'end' deepest-first, so `bar` before `foo` before `main`).
- Frames in `curr` **below** the LCP depth **started** (emit 'start' shallow→deep, so `baz` after `foo`).

**Identity = (depth, name)** so recursion (`foo → bar → foo` at depth 3 vs depth 1) is treated as two distinct frames.

After the last sample, **close any frames still on the current stack** (they ended after the last sample timestamp).

### Worked Python solution

```python
def lcp_depth(a, b):
    """Number of matching frames from the top (outer)."""
    i = 0
    while i < len(a) and i < len(b) and a[i] == b[i]:
        i += 1
    return i

def samples_to_events(samples):
    """samples: list of (ts, [frames])"""
    events = []
    prev = []                                    # empty stack at t=0
    last_ts = samples[0][0] if samples else 0

    for ts, curr in samples:
        # 1. Close frames in prev that are no longer present (below LCP)
        depth = lcp_depth(prev, curr)
        # deepest-first emit
        for f in reversed(prev[depth:]):
            events.append((ts, "end", f))
        # 2. Open frames in curr that are new (below LCP)
        for f in curr[depth:]:
            events.append((ts, "start", f))
        prev = curr
        last_ts = ts

    # 3. Close any frames still on the stack at the end
    for f in reversed(prev):
        events.append((last_ts, "end", f))
    return events
```

**Complexity.** O(S · L) total where S is samples and L is avg stack depth.

### ≥N-stable follow-up

Track how long each **live** frame has persisted — but a frame counts as continuing only while it stays inside the **LCP** with the previous sample. A call stack is a stack: if a shallower frame changes name, its caller returned, so every frame below it also returned — even if the same name reappears at the same depth. So key the streak by **depth** and reset it whenever the prefix above the frame changes, *not* just when its own `(depth, name)` disappears. (Keying independently by `(depth, name)` is the classic bug here — it would call a deep frame "stable" while its parent flickers, which is physically impossible.) Emit `start` when a streak reaches N; emit `end` when the frame drops out of the LCP.

```python
def stable_events(samples, n=3):
    events = []
    prev = []
    streak = {}        # depth -> [name, consecutive count]
    active = {}        # depth -> name (has emitted a start)
    last_ts = samples[0][0] if samples else 0

    for ts, curr in samples:
        lcp = lcp_depth(prev, curr)
        # Everything in prev at/below the divergence point is gone (deepest first)
        for d in range(len(prev) - 1, lcp - 1, -1):
            if d in active:
                events.append((ts, "end", active[d]))
                del active[d]
            streak.pop(d, None)
        # Present frames: extend the streak inside the LCP, start fresh below it
        for d, name in enumerate(curr):
            if d < lcp:
                streak[d][1] += 1
            else:
                streak[d] = [name, 1]
            if streak[d][1] == n and d not in active:
                events.append((ts, "start", name))
                active[d] = name
        prev = curr
        last_ts = ts

    for d in sorted(active, reverse=True):   # deepest first
        events.append((last_ts, "end", active[d]))
    return events
```

## By format

### Live · CoderPad (human) — *primary (Anthropic)*
- **How it appears:** the interviewer wants the **insight** (LCP-diff) more than tidy code; expect to derive it on the spot.
- **Follow-ups (real, reported):**
  - **≥N-stable emission** (above).
  - **Only-leaf events** — skip intermediate frames; only emit when a frame has no children.
  - **Merge identical adjacent frames** — if `start(A)` immediately follows `end(A)` with no time gap, coalesce.
  - **CPU time per frame** — given the samples are evenly spaced, weight events by sample interval.
  - **Self-time vs total-time** — exclusive time per frame (time not spent in children).
  - **Visualization** — render as a flamegraph (rectangles per frame, width = time).
  - **Streaming** — yield events as samples arrive, not at the end.
  - **Hash-cons frames** — use a stable integer id per frame name to save memory.
  - **What does sampling fundamentally miss?** → anything shorter than the sample interval (a 1ms call between 10ms samples never appears), and a frame present in two consecutive samples may have exited-and-reentered between them — the events you emit are a *plausible reconstruction*, not truth. Saying this shows you understand sampling profilers, which is the question's real subject.
  - **Sampling vs instrumented tracing** — samples: cheap, statistical, misses short calls; instrumentation: exact start/end but overhead + skew. This conversion bridges the two representations — one sentence of context that frames the whole problem.
- **Tips:**
  - **Work a tiny example by hand first** (2–3 samples) — the LCP rule emerges from writing it out.
  - **Narrate** "bigger prev ⇒ ends, bigger new ⇒ starts" while coding.
  - Identity = `(depth, name)` — say it out loud so recursion handling is obvious.
  - For the N-stable follow-up: separate "ever on the stack" from "actively emitting."
- **Pitfalls:**
  - **Wrong emit order** — ends are deepest-first (innermost exits first); starts are shallow-first (outer starts before inner).
  - **Recursion treated as one frame** — must use `(depth, name)` identity.
  - **Forgetting to close frames at the end** — leaks.
  - **Equal consecutive stacks** — LCP = full depth, no events; don't double-emit.
  - **Streak logic off-by-one** — emit at `streak == N`, not `streak > N`.
  - **Streak keyed independently per `(depth, name)`** — a deep frame's streak must reset when any *shallower* frame changes (it falls out of the LCP), because its caller returned. Tracking each depth in isolation wrongly reports an inner frame as "stable" while its parent flickers.
  - **Off-by-one in end-timestamp** — frame `f` ended at the current sample's timestamp, not the previous one's.

### Take-home / work-trial
- **Tips:** Ship base + ≥N-stable + a flamegraph renderer (ASCII or HTML).
- **Pitfalls:** Streaming version that's actually batch.

## Company variants

- **Anthropic (canonical)** — the viral 2025 question; one of the hardest in their bank.
- **OpenAI / Datadog / Honeycomb / Sentry** — observability-flavored reskin.
- Sometimes asked as "design a profiler" — a Track D question.

## Worked example trace

```
Samples:
(0,  [main, foo, bar])
(10, [main, foo, bar])         # unchanged → LCP=3, no events
(20, [main, foo])              # LCP=2, prev below: [bar] → emit "end bar"; new: [] → no starts
(30, [main, foo, baz])         # LCP=2, prev below: [] → no ends; new: [baz] → emit "start baz"
(40, [main])                   # LCP=1, prev below: [foo, baz] → emit "end baz", "end foo"
End-of-stream:                  # close remaining [main] → emit "end main"

Events:
(20, end, bar)
(30, start, baz)
(40, end, baz)
(40, end, foo)
(40, end, main)
```

## Related
[[14-exclusive-execution-time]] (sibling stack simulation) · [[anthropic-interview-guide]] (a).