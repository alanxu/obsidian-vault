---
title: Design Underground System
slug: underground-system
type: leetcode-design
leetcode: 1396
companies: [General]
difficulty: ★★☆☆☆
frequency: low-med
formats: [OA·GCA/HR, Live]
levels: 1
time-box: 15–25 min
tags: [hashmap, checkin-checkout, running-average]
related: []
---

# Design Underground System (#1396)

Pair check-in/check-out events and report average travel times — a clean two-map design.

## Problem
`checkIn(id, station, t)`; `checkOut(id, station, t)`; `getAverageTime(start, end)`.

## Core approach (format-agnostic)
`inflight: id → (start_station, t)`; `totals: (start,end) → (sum, count)`. On checkout, accumulate + clear in-flight. Average = `sum/count`. O(1) ops.

## By format

### OA · GCA / HackerRank (auto-graded)
- **Tips:** two maps; float division at the end.
- **Pitfalls:** checkout without checkin, same start==end, no trips for a pair.

### Live · CoderPad (human)
- **Follow-ups:** median/percentile travel time (heaps), time-windowed averages, busiest route, concurrency.
- **Tips:** the in-flight + totals pattern; mention it generalizes to session/metrics tracking.
- **Pitfalls:** storing all trips when a running sum suffices, float precision.

## Related
[[02-banking-system]] (event aggregation).
