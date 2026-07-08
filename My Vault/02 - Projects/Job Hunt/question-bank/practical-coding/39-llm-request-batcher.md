---
title: LLM Request Batcher (coalesce under max-size / max-wait)
slug: llm-request-batcher
type: agentic
leetcode: null
companies: [Anthropic, OpenAI, Fireworks, Together, "AI-infra teams"]
difficulty: ★★★★☆
frequency: rising
formats: [Live, Take-home]
levels: 2
time-box: live 40–50 min
tags: [batching, concurrency, futures, latency-throughput, coalescing, threading]
related: ["[[35-sliding-window-rate-limiter]]", "[[31-retry-with-backoff]]", "[[../llm-system-design/06-llm-inference-serving-platform]]"]
added: 2026-07-08 (audit fill — Anthropic reported: "LLM request batching")
evidence: "VERIFIED at topic level: Anthropic SWE question aggregators (prachub 2026) list 'LLM request batching' among common problems (alongside distributed rate limiter, time-based KV). The exact max-size/max-wait spec is my reconstruction of the standard form. Fireworks/Together = inference."
---

# LLM Request Batcher

Anthropic-reported coding prompt. GPU inference is efficient in batches, but callers arrive one at a time → **coalesce concurrent requests into a batch**, dispatch when **batch is full OR the oldest request has waited `max_wait_ms`**, and route each result back to its caller. The classic **latency-vs-throughput knob**, in ~60 lines of concurrency.

## Problem

```python
batcher = Batcher(model_fn,            # model_fn(list[prompt]) -> list[reply], one call = one batch
                  max_batch_size=8,
                  max_wait_ms=50)
batcher.submit(prompt) -> Future        # caller blocks on .result()
```

Rules: never exceed `max_batch_size` · no request waits more than `max_wait_ms` before its batch dispatches · results map back to the right caller **by position** · `model_fn` failure fails that batch's callers only · `shutdown()` flushes.

## Core approach (format-agnostic)

One background dispatcher thread + a condition variable. Dispatch condition: **full, or timer expired on oldest**.

```python
import threading, time
from concurrent.futures import Future

class Batcher:
    def __init__(self, model_fn, max_batch_size=8, max_wait_ms=50):
        self.model_fn = model_fn
        self.max_n = max_batch_size
        self.max_wait = max_wait_ms / 1000
        self.queue = []                      # (prompt, future, enq_time)
        self.lock = threading.Condition()
        self.closed = False
        threading.Thread(target=self._loop, daemon=True).start()

    def submit(self, prompt) -> Future:
        f = Future()
        with self.lock:
            if self.closed: raise RuntimeError("shutdown")
            self.queue.append((prompt, f, time.monotonic()))
            self.lock.notify()
        return f

    def _loop(self):
        while True:
            with self.lock:
                while not self.queue and not self.closed:
                    self.lock.wait()
                if self.closed and not self.queue:
                    return
                # wait until full or oldest expires
                deadline = self.queue[0][2] + self.max_wait
                while (len(self.queue) < self.max_n
                       and not self.closed
                       and (left := deadline - time.monotonic()) > 0):
                    self.lock.wait(timeout=left)
                batch, self.queue = self.queue[:self.max_n], self.queue[self.max_n:]
            self._dispatch(batch)            # OUTSIDE the lock — never call the model holding it

    def _dispatch(self, batch):
        prompts = [p for p, _, _ in batch]
        try:
            replies = self.model_fn(prompts)
            if len(replies) != len(prompts):
                raise RuntimeError("model returned wrong count")
            for (_, f, _), r in zip(batch, replies):
                f.set_result(r)
        except Exception as e:
            for _, f, _ in batch:
                f.set_exception(e)

    def shutdown(self):
        with self.lock:
            self.closed = True
            self.lock.notify_all()
```

**Complexity.** O(1) per submit; dispatcher wakes ≤ 2× per batch.
**The three lines that matter:** deadline computed from the **oldest** item (not "reset the timer on each arrival" — that starves under steady trickle); model call **outside the lock**; wrong-count from `model_fn` is a *batch* failure, not silent misrouting.

## By format

### Live · CoderPad — *primary*
- **How it appears:** "requests come in concurrently; the model likes batches; build the batcher" (~25 min), then policy probes.
- **Follow-ups (reported/likely):**
  - **Why both triggers?** → size alone starves low traffic; time alone wastes GPU at high traffic. Tail latency bound = `max_wait + model_time`.
  - **Tune the knobs** → high QPS: batch fills before timer (throughput mode); low QPS: timer dominates (latency mode ≈ +max_wait). Adaptive: shrink `max_wait` when queue is hot.
  - **Concurrent batches** — model can run N batches in parallel → dispatch into a `ThreadPoolExecutor(N)` instead of inline; backpressure when all N busy.
  - **Backpressure / queue cap** — bounded queue; `submit` blocks or rejects (fast-fail) when full → tie to [[35-sliding-window-rate-limiter]].
  - **Priorities** — two queues (interactive vs batch tier); interactive preempts; watch starvation.
  - **Per-caller fairness** — one caller floods → cap per-caller in-flight items per batch.
  - **Cancellation** — caller abandons: `Future.cancel()` before dispatch → drop from queue (check `f.set_running_or_notify_cancel()`).
  - **Retries** — batch fails: retry whole batch once, or re-enqueue items individually ([[31-retry-with-backoff]]); mind duplicate-execution semantics.
  - **asyncio version** — same logic; `asyncio.Future` + one dispatcher task; no locks needed (single loop) — mention.
  - **Continuous batching?** → the design-level answer (per-token scheduling in vLLM, → [[../llm-system-design/06-llm-inference-serving-platform]]); this card is request-level batching at the client/gateway.
- **Tips:**
  - Say the invariant set first: *bounded wait, bounded size, correct routing, isolated failures* — it's the rubric.
  - `time.monotonic()`, never `time.time()`.
  - Test: burst of 20 (→ batches of 8/8/4), single request (dispatches at ~max_wait), model exception (all futures errored).
- **Pitfalls:**
  - Timer reset on every arrival → oldest request waits unboundedly under trickle traffic.
  - Calling `model_fn` while holding the lock → submits block for the whole model call.
  - Zip misalignment on reorder/filter → user A gets user B's completion (privacy incident, say so).
  - Lost wakeup: `wait(timeout)` without re-checking conditions in a loop.
  - No flush on shutdown → hung callers.

### Take-home
- Ship: batcher + asyncio variant + metrics hooks (batch size histogram, wait p50/p99) + the three tests above; README the latency/throughput tradeoff with a measured table.

## Worked example trace

```
max_batch_size=3, max_wait=50ms
t=0ms   A arrives → queue=[A], deadline=t50
t=10ms  B arrives → queue=[A,B]
t=50ms  timer fires → dispatch [A,B] (size 2)
t=60ms  C,D,E,F arrive in 1ms → size hits 3 → dispatch [C,D,E] immediately; F waits (deadline t=111)
```

## Cross-track map
- **B** = this card (client/gateway-side batching)
- **D Area 2** = [[../llm-system-design/06-llm-inference-serving-platform]] (server-side continuous batching, the "go deeper" answer)
- **C** = queueing/backpressure vocabulary shared with [[../distributed-system-design/03-distributed-message-queue-pubsub]]

## Related
[[35-sliding-window-rate-limiter]] (admission control upstream) · [[31-retry-with-backoff]] (failure policy) · [[32-streaming-response-handler]] (per-request streaming downstream).
