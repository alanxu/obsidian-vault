---
title: DAG Task Scheduler (dependencies + concurrency)
slug: dag-task-scheduler
type: stateful-service
leetcode: "210 (course schedule II) — the toy version"
companies: [OpenAI, Anthropic, Databricks, Airbnb-style infra, "agent-platform teams"]
difficulty: ★★★★☆
frequency: high
formats: [Live, Take-home, Onsite·NR]
levels: 3
time-box: live 45–60 min
tags: [dag, topological-sort, concurrency, scheduler, retries, kahn, threadpool]
related: ["[[10-job-scheduler-task-queue|distributed-system-design/10]]", "[[31-retry-with-backoff]]", "[[34-multi-agent-orchestration]]", "[[12-multithreaded-web-crawler]]"]
added: 2026-07-08 (audit fill — OpenAI reported: job scheduler with dependency + distributed-execution follow-ups)
evidence: "VERIFIED: 'Design a job scheduler with follow-ups on distributed execution, fault tolerance, orchestration internals' reported as a real OpenAI question (jobright 2026); task-scheduler implementation also listed among OpenAI system-aware coding problems (prachub). Anthropic/Databricks = inference."
---

# DAG Task Scheduler

OpenAI-reported: "design/implement a job scheduler" with follow-ups walking up the stack (concurrency → failures → distribution). The coding round wants **Kahn's algorithm wearing a ThreadPool**: run tasks respecting dependencies, maximally parallel, with failure semantics. Also the skeleton of every agent **plan-executor** ([[34-multi-agent-orchestration]]) — say that at agent shops.

## Problem

```python
scheduler.add_task(name: str, fn: Callable, deps: list[str] = [])
scheduler.run(max_workers: int = 4) -> dict[str, TaskResult]  # status: success|failed|skipped
```

- **L1:** valid order, sequential (topo sort). Detect cycles → raise.
- **L2:** concurrent — independent tasks run in parallel; task starts the moment *all* deps succeed.
- **L3:** failure policy — dep failed → dependents `skipped` (cascade), independent branches keep running; per-task retries; timeout.

## Core approach (format-agnostic)

Kahn's with in-degree counting; completion of a task *unlocks* its dependents — event-driven, no polling:

```python
import threading
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

@dataclass
class TaskResult:
    status: str            # success | failed | skipped
    value: object = None
    error: str = None

class Scheduler:
    def __init__(self):
        self.fns, self.deps, self.dependents = {}, {}, {}

    def add_task(self, name, fn, deps=None):
        if name in self.fns: raise ValueError(f"duplicate: {name}")
        self.fns[name], self.deps[name] = fn, set(deps or [])
        self.dependents.setdefault(name, set())
        for d in self.deps[name]:
            self.dependents.setdefault(d, set()).add(name)

    def run(self, max_workers=4):
        unknown = {d for ds in self.deps.values() for d in ds} - self.fns.keys()
        if unknown: raise ValueError(f"unknown deps: {unknown}")
        self._check_cycle()

        results, lock = {}, threading.Lock()
        remaining = {n: len(ds) for n, ds in self.deps.items()}
        done = threading.Event()

        with ThreadPoolExecutor(max_workers) as pool:
            def finish(name, result):
                ready = []
                with lock:
                    # iterative cascade — recursing here would re-acquire a
                    # non-reentrant lock (classic deadlock; see pitfalls)
                    stack = [(name, result)]
                    while stack:
                        n, res = stack.pop()
                        if n in results: continue
                        results[n] = res
                        for child in self.dependents[n]:
                            if child in results: continue
                            if res.status != "success":
                                stack.append((child, TaskResult(
                                    "skipped", error=f"dep {n} {res.status}")))
                            else:
                                remaining[child] -= 1
                                if remaining[child] == 0: ready.append(child)
                    if len(results) == len(self.fns): done.set()
                for r in ready: pool.submit(work, r)

            def work(name):
                try:
                    finish(name, TaskResult("success", value=self.fns[name]()))
                except Exception as e:
                    finish(name, TaskResult("failed", error=str(e)))

            roots = [n for n, c in remaining.items() if c == 0]
            if not roots and self.fns: raise ValueError("cycle")   # belt & suspenders
            for n in roots: pool.submit(work, n)
            if self.fns: done.wait()
        return results

    def _check_cycle(self):
        indeg = {n: len(ds) for n, ds in self.deps.items()}
        q = [n for n, c in indeg.items() if c == 0]; seen = 0
        while q:
            n = q.pop(); seen += 1
            for c in self.dependents[n]:
                indeg[c] -= 1
                if indeg[c] == 0: q.append(c)
        if seen != len(self.fns): raise ValueError("cycle detected")
```

**Complexity.** O(V+E) scheduling overhead; wall-clock = critical-path length given enough workers.
**Subtleties worth narrating:** cascade-skip must be **iterative** inside the lock — a recursive `finish` re-acquires the non-reentrant `Lock` and deadlocks (RLock hides the bug; restructuring removes it); `done.wait()` instead of `pool.shutdown` ordering games; validate unknown deps *before* running anything.

## By format

### Live · CoderPad — *primary*
- **How it appears:** L1 asked plainly; L2/L3 as "now make it parallel / now a task fails."
- **Follow-ups (reported/likely):**
  - **Cycle detection** — Kahn count vs DFS colors; report *which* nodes form the cycle (nodes never reaching in-degree 0).
  - **Fail policy variants** — fail-fast (cancel everything) vs continue-independent (above) vs retry-then-skip → plug [[31-retry-with-backoff]] into `work`.
  - **Priorities** — among ready tasks, heap by priority instead of FIFO submit.
  - **Timeout per task** — future with timeout; on timeout mark failed, *don't* orphan the thread (note Python can't kill threads — say it).
  - **Dynamic tasks** — a task adds tasks at runtime (agent planners do this) → `done` condition becomes "no running + no ready", not a fixed count.
  - **Persistence / resume** — journal results; on restart skip `success`, reset `running` → crash-safe re-run needs **idempotent tasks** (say the word).
  - **"Distribute it"** → the design escalation: queue + workers + heartbeat + exactly-once-ish claims → [[10-job-scheduler-task-queue|distributed bank #10]]; keep the coding answer single-process.
- **Tips:**
  - Start with the **state machine**: pending → ready → running → success/failed/skipped. Draw it; code falls out.
  - Event-driven unlock (dep-count decrement) — polling loops read as junior.
  - Test with the diamond: A → B,C → D; fail B → D skipped, C still ran.
- **Pitfalls:**
  - Deadlock: waiting on futures of tasks that were never submitted (skip-cascade forgot to mark them → `done` never fires).
  - Race on `remaining` without lock.
  - **Recursive cascade-skip while holding a non-reentrant lock** — deadlocks the moment a task with dependents fails; iterate with an explicit stack instead.
  - Detecting cycles *after* side effects started — validate first.
  - `pool.submit` while holding the lock → fine here, but submitting `finish`-work recursively can starve; know why yours doesn't.

### Take-home
- Ship: scheduler + retries + timeout + JSON DAG spec input + tests (diamond, cycle, fail-cascade, parallelism assertion via timing/counters).

### Onsite · NR
- Write topo sort + the state machine by hand; trace the diamond on failure; skip the ThreadPool (describe it).

## Worked example trace

```
A(2s)   B(after A, fails)   C(after A)   D(after B and C)
t=0   A running
t=2   A ✓ → B, C both start (parallel)
t=3   B ✗ → D skipped immediately (doesn't wait for C)
t=4   C ✓ → all accounted → done
results: A=success B=failed C=success D=skipped(dep B failed)
```

## Cross-track map
- **B** = this card · **C** = [[10-job-scheduler-task-queue|distributed #10]] (the "scale it" answer) · **agentic** = [[34-multi-agent-orchestration]] runs on exactly this executor.

## Related
[[31-retry-with-backoff]] (per-task retry) · [[12-multithreaded-web-crawler]] (ThreadPool discipline sibling) · [[34-multi-agent-orchestration]] (agent skin).
