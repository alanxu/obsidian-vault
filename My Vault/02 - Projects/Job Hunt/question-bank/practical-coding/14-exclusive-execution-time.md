---
title: Exclusive Execution Time from Logs
slug: exclusive-execution-time
type: live-coding
leetcode: 636
companies: [Anthropic, Datadog, Honeycomb, Sentry, "any observability/profiling team"]
difficulty: ★★★☆☆
frequency: high
formats: [Live, OA·GCA/HR]
levels: 2
time-box: 30–45 min
tags: [stack, simulation, timestamps, streaming, heap]
related: ["[[13-stack-trace-to-trace-conversion]]", "[[anthropic-interview-guide]]"]
---

# Exclusive Execution Time from Logs

LeetCode **#636**, Anthropic-flavored. Compute the **exclusive (self) time** per function from chronological START/END logs via a stack. The follow-ups (out-of-order streams, equal timestamps, recursion) are where the question lives.

## Problem

Logs are triples `(id, 'START'|'END', timestamp)` in arrival order (usually chronological). Compute **exclusive time** per `id` — i.e., time not spent in any child call.

```
Example input:
0 START 0
1 START 1
1 END 2
0 END 3

Output (exclusive time):
[0, 1]      # function 0 ran 1 unit on its own; function 1 ran 1 unit
```

**Follow-ups (real, reported):**
- **Equal timestamps** — what if two events share the same time?
- **Out-of-order stream** — events arrive out of timestamp order; buffer them.
- **Detect N consecutive identical events** — debounce / collapse.

## Core approach (format-agnostic)

**Stack of active ids.** On each event:
1. Add `(ts − prev_ts)` to the **top function's exclusive counter**.
2. Then push (START) or pop (END).
3. Update `prev_ts = ts`.

**Half-open timing convention:** a call from `s` to `e` lasts `e − s`. So the function was "exclusive" during `[s, e)` while no child was active. When a child START arrives at `e`, the parent's exclusive time gets `e − prev_ts` added — which is the gap since the last END.

### Worked Python solution

```python
def exclusive_time(n, logs):
    """n: number of function ids (0..n-1). logs: list[str]."""
    stack = []
    exclusive = [0] * n
    prev_ts = 0

    for log in logs:
        fid, kind, ts = log.split(":")
        fid, ts = int(fid), int(ts)
        if kind == "START":
            if stack:
                exclusive[stack[-1]] += ts - prev_ts
            stack.append(fid)
        else:  # END
            exclusive[stack[-1]] += ts - prev_ts + 1     # inclusive of END ts
            stack.pop()
        prev_ts = ts + (1 if kind == "END" else 0)

    return exclusive
```

**Note on the `+1` and `prev_ts` shift:** LeetCode #636 uses an **inclusive END** convention (a call ENDing at `t=5` consumed the slot `t=5`). If your problem uses **half-open** (END at `t=5` means it consumed `[s, 5)`), drop the `+1`s.

### Out-of-order stream

Buffer events in a min-heap keyed `(timestamp, arrival_idx)`. When the heap top is at least `max_delay` old, pop and process. This makes reads O(1) amortized (over a bounded buffer) while still correcting local disorder.

```python
import heapq

class OutOfOrderExclusive:
    def __init__(self, n, max_delay=5):
        self.n = n
        self.max_delay = max_delay
        self.heap = []                                # (ts, arrival_idx, kind, id)
        self.arrival_idx = 0
        self.exclusive = [0] * n
        self.stack = []
        self.prev_ts = 0
        self.latest_processed = -1

    def feed(self, log):
        fid, kind, ts = log.split(":")
        self.arrival_idx += 1
        heapq.heappush(self.heap, (int(ts), self.arrival_idx, kind, int(fid)))
        # Drain events whose ts is old enough that later arrivals can't precede them
        # We need ts + max_delay < current "latest seen" timestamp to guarantee order
        latest = max(h[0] for h in self.heap) if self.heap else 0
        while self.heap and latest - self.heap[0][0] >= self.max_delay:
            self._process_one()

    def _process_one(self):
        ts, _, kind, fid = heapq.heappop(self.heap)
        # ... same logic as the synchronous version

    def flush(self):
        while self.heap:
            self._process_one()
```

## By format

### Live · CoderPad (human) — *primary (Anthropic)*
- **How it appears:** base in ~10 min; follow-ups layered on.
- **Follow-ups (real, reported):**
  - **Equal timestamps** — START immediately after END at the same time: which gets credit? Spec varies.
  - **Out-of-order stream** — buffer with heap (above).
  - **Recursion** — same id nested (`foo START, foo START, foo END, foo END`); counter is correct because the stack handles it.
  - **Detect N consecutive identical events** — debounce: don't re-emit the same state N times in a row.
  - **Per-thread aggregation** — multiple threads, each with its own stack.
  - **Visualize** — render as a flamegraph using the same data.
- **Tips:**
  - **Narrate half-open timing and the tie-break** — make the convention audible.
  - **Dry-run nested calls** on a 3-event example.
  - For out-of-order: state the buffer-size / `max_delay` trade-off.
- **Pitfalls:**
  - **Double-counting at equal timestamps** — confirm convention.
  - **Recursion** — same id nested; verify with `foo START 0, foo START 1, foo END 2, foo END 3` → exclusive = `[0, 2]`.
  - **Unbalanced logs** — defensive: ignore an END with empty stack.
  - **Empty input** — return `[0] * n` or `[]`.
  - **END convention** — `e − s` vs `e − s + 1`. Read the problem.

### OA · GCA / HackerRank (#636, auto-graded)
- **Tips:** the plain #636 — single stack, careful at START-after-END at the same timestamp.
- **Pitfalls:** off-by-one on the `e−s` vs `e−s+1` convention. LeetCode uses inclusive END; many spec sheets use half-open.

### Onsite · NR (Google-style)
- **Tips:** Define the stack invariant on the shared doc; trace a 4-event nested call.
- **Pitfalls:** Forgetting to update `prev_ts` after END.

## Company variants

- **Anthropic (canonical)** — sometimes wrapped with their stack-trace-to-trace question.
- **Datadog / Honeycomb / Sentry** — observability-flavored reskin; often with persistent storage.
- **OpenAI / Stripe** — sometimes used to test parallel-stack handling.

## Worked example trace

```
Logs:
"0:START:0"   → stack=[], prev=0; stack.append(0); stack=[0]; prev=0
"1:START:2"   → stack=[0], exclusive[0] += 2-0 = 2; stack.append(1); stack=[0,1]; prev=2
"1:END:5"     → exclusive[1] += 5-2+1 = 4; stack.pop; stack=[0]; prev=6 (5+1)
"0:END:7"     → exclusive[0] += 7-6+1 = 2; stack.pop; stack=[]; prev=8

Result: exclusive = [4, 4]
```

## Related
[[13-stack-trace-to-trace-conversion]] · [[anthropic-interview-guide]] (b).