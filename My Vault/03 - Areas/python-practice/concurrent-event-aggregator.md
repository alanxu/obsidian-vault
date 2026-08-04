# Concurrent Event Aggregator

Practice **concurrency primitives** + **`collections`** by building the aggregation
layer of a real-time event monitoring service.

Multiple producers push events into an asyncio queue at varying rates. You
consume them, maintain rolling stats, and answer queries.

---

## Event shape

```python
{
  "source": str,        # e.g. "auth-svc", "api-gateway", "billing"
  "level": str,         # "INFO" | "WARN" | "ERROR" | "DEBUG"
  "timestamp": float,   # seconds since epoch (monotonic-ish, from producer)
  "message": str,
}
```

---

## Class to build

```python
class EventAggregator:
    def __init__(self, window_seconds: float = 5.0):
        ...

    async def consume(self, queue: asyncio.Queue) -> None:
        """Pull events from `queue` until a `None` sentinel arrives."""

    def snapshot(self) -> dict:
        """JSON-serializable view of current stats."""

    def summary(self) -> str:
        """Human-readable summary, e.g. for a CLI dashboard."""

    # stretch
    def rate_alerts(self, threshold: float) -> list[tuple[str, str, float]]:
        """Sources whose ERROR rate (events/sec) over the window exceeds threshold."""
```

---

## Levels — build incrementally

### Level 1 — Single consumer, basic counts *(warm-up)*

Run **one** `consume()` task. Track:

| Stat | Suggested collection |
| --- | --- |
| Total count by level | `Counter` |
| Count by `(source, level)` | `defaultdict(Counter)` |
| Total event count | `int` (or `Counter` on a special key) |

**Goal:** `snapshot()` returns a dict you can `json.dumps`.

### Level 2 — Multi-consumer, concurrency-safe

Run **N** consumers via `asyncio.gather(...)` on the same `EventAggregator`.
Make the shared state safe.

> ⚠️ `collections.Counter` is **not** atomic under concurrent updates. You'll
> need a lock. Decide: one global `asyncio.Lock`, or per-source locks
> (`defaultdict(asyncio.Lock)`) for higher throughput? Try both and time it.

### Level 3 — Sliding time window

For each source, keep events from the **last `window_seconds`** using
`collections.deque(maxlen=...)` — or, better, a `deque` of `(timestamp, ...)`
and prune in O(n) during `consume` (fine for a practice problem; for prod
you'd use a bucketed histogram).

Expose:

- `events_in_window(source: str) -> int`
- `top_k_error_sources(k: int) -> list[tuple[str, int]]` — use
  `heapq.nlargest` or sort the snapshot.

### Level 4 — Stretch goals

Pick any/all:

- **Rate limiting per source.** Token bucket implemented with a `deque` of
  timestamps. Reject events beyond the budget; expose `dropped_by_source`.
- **Live alerts channel.** After each `consume`, if a source's ERROR rate in
  the window exceeds `threshold`, push `(source, "rate_alert", rate)` into an
  output `asyncio.Queue`. Have a separate task drain it and print.
- **Latency percentiles.** Add a `latency_ms` field to events. Use
  `collections.deque` per source + `statistics.quantiles` for p50/p95.
- **Backpressure.** Make the queue `asyncio.Queue(maxsize=N)` and have
  producers `await queue.put(...)` so the system self-throttles.
- **Periodic flush.** Run a side task that prints `summary()` every second
  while producers run, then a final summary at the end.

---

## Suggested tools

- `asyncio.Queue`, `asyncio.create_task`, `asyncio.gather`, `asyncio.Lock`
- `collections.Counter`, `defaultdict`, `deque`, `OrderedDict`
- `heapq.nlargest` (for top-K)
- `statistics.quantiles` (for percentiles)
- `time.perf_counter()` (for timestamps)

---

## Reference producers / driver

```python
import asyncio, random, time

LEVELS = ["INFO", "INFO", "INFO", "DEBUG", "WARN", "ERROR", "ERROR"]
SOURCES = ["auth-svc", "api-gateway", "billing", "search", "notify"]

async def producer(queue: asyncio.Queue, n: int, seed: int) -> None:
    rng = random.Random(seed)
    for _ in range(n):
        await queue.put({
            "source": rng.choice(SOURCES),
            "level":  rng.choice(LEVELS),
            "timestamp": time.perf_counter(),
            "message": "...",
            "latency_ms": rng.gauss(50, 15),  # optional, for level 4
        })
        await asyncio.sleep(rng.uniform(0, 0.001))

async def main() -> None:
    agg = EventAggregator(window_seconds=5.0)
    queue: asyncio.Queue = asyncio.Queue(maxsize=1000)

    producers = [asyncio.create_task(producer(queue, 5_000, i)) for i in range(4)]
    consumers = [asyncio.create_task(agg.consume(queue)) for _ in range(3)]

    # optional: live summary ticker
    # ticker = asyncio.create_task(ticker(agg))

    await asyncio.gather(*producers)
    for _ in consumers:
        await queue.put(None)
    await asyncio.gather(*consumers)

    print(agg.summary())

asyncio.run(main())
```

---

## What "done" looks like

1. All 4 levels built, ~150 lines of code.
2. The final `summary()` prints something like:
   ```
   20000 events ingested (4 producers, 3 consumers)
   by level:  INFO=11200  WARN=2400  ERROR=4200  DEBUG=2200
   top error sources:
     auth-svc      1142
     api-gateway    980
     billing        760
   ```
3. Bonus: a one-line benchmark showing per-source locking ≈ 2× faster than a
   global lock under heavy contention. Worth doing — it's the kind of
   "obvious-after-you-see-it" finding that interviews love.

---

## Things to think about while you build

- **Where does the lock go?** Around the whole `consume()`, or only around
  the in-memory update? Smaller critical section = better throughput.
- **Memory.** What if the stream runs forever? When do old entries leave the
  `deque`? Hint: prune at write time vs. lazily at read time.
- **Single consumer vs. multi.** With one consumer, no lock needed — but
  throughput is bottlenecked. Where's the tradeoff? Profile it.
- **Sentinel handling.** A `None` sentinel only stops one consumer. If you
  spawn N consumers, do you put N `None`s, or use a different stop signal?
