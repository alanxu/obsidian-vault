---
title: Multithreaded Web Crawler
slug: multithreaded-web-crawler
type: concurrency
leetcode: 1242
companies: [Anthropic, general]
difficulty: ★★★★☆
frequency: very-high
formats: [Live, Take-home]
levels: 2
time-box: live 45–60 min
tags: [concurrency, threadpool, bfs, gil, dedup, rate-limiting]
related: ["[[anthropic-interview-guide]]"]
---

# Multithreaded Web Crawler ⭐⭐

**Anthropic's #1 reported live-coding question.** Single-threaded BFS first, then make it concurrent and thread-safe. The follow-ups (GIL, politeness, distribution) are where seniority shows.

## Problem
Given `get_urls(url)`, crawl from a seed, **same domain only**, normalize (strip fragments/`www`/trailing slash), **dedupe**. **Part 2:** multithreaded — thread-safe visited set + work queue. Code: [[anthropic-interview-guide]] worked solution (d).

## Core approach (format-agnostic)
Single-thread BFS with `visited:set` + `deque`. Multithread: `ThreadPoolExecutor` (or worker pool + `queue.Queue`); guard `visited` with a `Lock` (atomic check-and-add). **Termination/quiescence:** done when queue empty **and** no workers active.

## By format

### Live · CoderPad (human) — *primary (Anthropic)*
- **How it appears:** single-thread first (~15 min), then "make it concurrent," then a barrage of concept follow-ups.
- **Follow-ups:** **GIL** (I/O-bound → threads help; CPU-bound → multiprocessing/asyncio); per-host **politeness**/robots; asyncio vs threads vs processes; **distributed** (shard frontier by domain hash, shared seen via Redis/Bloom, at-least-once vs exactly-once).
- **Tips:** get single-thread correct + deduped first; introduce the lock only when you parallelize and **say why** (race on visited); discuss termination explicitly.
- **Pitfalls:** non-atomic visited check-and-add (double-crawl), never terminating (no quiescence tracking), crawling off-domain, not normalizing URLs.

### Take-home / work-trial
- **Tips:** ship single + multithreaded with a `--workers` flag, a politeness delay, and tests; README the GIL/asyncio trade-off.
- **Pitfalls:** unbounded threads, no rate limiting, shared-state races without a lock.

## Related
[[15-duplicate-file-detection]] (other systems-flavored Anthropic problem) · Track C distributed-crawler design.
