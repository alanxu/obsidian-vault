---
title: Design Underground System
slug: underground-system
type: leetcode-design
leetcode: 1396
companies: [Uber, Lyft, "transit systems", "any session/metrics tracking"]
difficulty: ★★☆☆☆
frequency: low-med
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 15–25 min
tags: [hashmap, checkin-checkout, running-average, session-tracking]
related: ["[[02-banking-system]]"]
---

# Design Underground System (#1396)

Pair check-in/check-out events and report average travel times — a clean two-map design. The pattern generalizes to any "session start / session end with metric" tracker.

## Problem

- `checkIn(id, stationName, t)` — passenger `id` checks in at `stationName` at time `t`.
- `checkOut(id, stationName, t)` — passenger checks out at `stationName` at time `t`.
- `getAverageTime(startStation, endStation) -> float` — average travel time over all completed trips between these stations.

## Core approach (format-agnostic)

Two maps:
- `inflight: dict[id → (start_station, t)]` — passengers currently in the system.
- `totals: dict[(start, end) → (sum_t, count)]` — running sum and count.

On `checkOut`: pop from `inflight`; compute travel time; accumulate `(sum_t, count)` for `(start, end)`. `getAverageTime` = `sum / count`.

### Worked Python solution

```python
class UndergroundSystem:
    def __init__(self):
        self.inflight = {}                # id -> (start_station, t)
        self.totals = {}                  # (start, end) -> [sum, count]

    def checkIn(self, id: int, stationName: str, t: int) -> None:
        self.inflight[id] = (stationName, t)

    def checkOut(self, id: int, stationName: str, t: int) -> None:
        start, t0 = self.inflight.pop(id)
        key = (start, stationName)
        if key in self.totals:
            self.totals[key][0] += t - t0
            self.totals[key][1] += 1
        else:
            self.totals[key] = [t - t0, 1]

    def getAverageTime(self, startStation: str, endStation: str) -> float:
        s, c = self.totals[(startStation, endStation)]
        return s / c
```

**Complexity.** O(1) per op.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:**
  - Two maps; float division at the end.
  - Use lists `[sum, count]` instead of tuples for mutability.
- **Pitfalls:**
  - **Checkout without checkin** — defensive: ignore or raise; spec varies.
  - **Same start == end** — valid; trip time = checkout - checkin.
  - **No trips for a pair** — `getAverageTime` → 0 or undefined; spec varies.

### Live · CoderPad (human)
- **Follow-ups (real, reported):**
  - **Median / percentile travel time** — keep all trip times; `bisect` + index for percentiles.
  - **Time-windowed averages** — daily/weekly buckets; reset windows.
  - **Busiest route** — `max((start, end) → count)`.
  - **Concurrency** — locks per passenger or per route.
  - **Multi-modal** — bus, train, walking; each is a separate route type.
  - **Capacity** — limit concurrent passengers at a station.
  - **Persistence** — serialize the totals map.
  - **Real-time tracking** — current location of in-flight passengers; add to inflight map.
  - **Cancellation** — `cancel(id)` clears inflight without contributing to totals.
- **Tips:**
  - **The in-flight + totals pattern** — say it once and it generalizes.
  - Mention it generalizes to **session/metrics tracking**.
  - For percentiles: store `(start, end) → sorted_list` of trip times; `bisect` for median.
  - For busiest route: also track counts and find argmax.
- **Pitfalls:**
  - **Storing all trips** when a running sum suffices — memory waste.
  - **Float precision** — round to N decimals for display.
  - **Concurrent checkouts** — locks if the same passenger has two checkouts (network retry).

### Onsite · NR (Google-style)
- **Tips:** State the two-map structure; trace a 3-trip example.
- **Pitfalls:** Forgetting to `pop` from inflight on checkout.

## Company variants

- **Uber / Lyft / transit systems** — production-flavored.
- **Session tracking** (web analytics, perf monitoring) — same pattern.

## Worked example trace

```
checkIn(1, "A", 3)
checkOut(1, "B", 8)        # trip A→B took 5
checkIn(2, "A", 10)
checkOut(2, "B", 15)       # trip A→B took 5
getAverageTime("A", "B")   # (5+5)/2 = 5.0

checkIn(3, "A", 20)
checkOut(3, "C", 35)       # trip A→C took 15
getAverageTime("A", "C")   # 15.0
```

## Related
[[02-banking-system]] (event aggregation).