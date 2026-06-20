---
title: Multithreaded Web Crawler
slug: multithreaded-web-crawler
type: concurrency
leetcode: 1242
companies: [Anthropic, OpenAI, Stripe, Notion, "Common Crawl", Exa, Perplexity, Google, "search/AI-eng roles broadly"]
difficulty: ★★★★☆
frequency: very-high
formats: [Live, Take-home]
levels: 2
time-box: live 45–60 min
time-box-take-home: 6–10 hours
tags: [concurrency, threadpool, bfs, gil, dedup, rate-limiting, politeness, async]
related: ["[[anthropic-interview-guide]]", "[[15-duplicate-file-detection]]", "[[Track C distributed-crawler design]]"]
---

# Multithreaded Web Crawler ⭐⭐

**Anthropic's #1 reported live-coding question.** Single-threaded BFS first, then make it concurrent and thread-safe. The follow-ups (GIL, politeness, distribution) are where **seniority shows** — most candidates clear the single-thread base; far fewer can defend the parallelism choice with a real concurrency model.

## Problem

You are given `get_urls(url) -> list[str]` (the network stub). Crawl from a seed URL:
- **Same domain only** (don't leave `anthropic.com`).
- **Normalize URLs** — strip fragments, lowercase host, strip trailing `/`/`www.`, etc.
- **Dedupe** — don't re-crawl.
- **Part 2:** make it multithreaded — thread-safe visited set + work queue.

The exact normalization rules vary. **Clarify upfront** ("do we strip `www.`? do we keep query strings?"). The grader checks edge cases like `http://Foo.com` vs `https://foo.com/` vs `https://www.foo.com`.

## Core approach (format-agnostic)

### Single-thread BFS
```python
from collections import deque
from urllib.parse import urlparse, urlunparse

def normalize(url, base_host):
    p = urlparse(url)
    host = (p.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    if host != base_host:
        return None                              # off-domain; skip
    # strip fragment, normalize trailing slash
    path = p.path.rstrip("/") or "/"
    return urlunparse(("https", host, path, "", p.query, ""))

def crawl(seed, get_urls):
    base_host = urlparse(seed).netloc.lower().lstrip("www.")
    visited = {seed}
    queue = deque([seed])
    while queue:
        url = queue.popleft()
        for nxt in get_urls(url):
            nu = normalize(nxt, base_host)
            if nu and nu not in visited:
                visited.add(nu)
                queue.append(nu)
    return visited
```

### Multithread version
```python
from concurrent.futures import ThreadPoolExecutor
import threading

def crawl_parallel(seed, get_urls, workers=8):
    base_host = urlparse(seed).netloc.lower().lstrip("www.")
    visited_lock = threading.Lock()
    visited = {seed}
    queue = deque([seed])
    in_flight = 0
    in_flight_lock = threading.Lock()
    done_event = threading.Event()

    def submit_more(executor):
        nonlocal in_flight
        while True:
            with in_flight_lock:
                if in_flight >= workers * 2:
                    return
            try:
                url = queue.popleft()
            except IndexError:
                return
            with visited_lock:
                if url in visited:
                    continue
                visited.add(url)
            with in_flight_lock:
                in_flight += 1
            executor.submit(worker, url)

    def worker(url):
        nonlocal in_flight
        try:
            for nxt in get_urls(url):
                nu = normalize(nxt, base_host)
                if not nu:
                    continue
                with visited_lock:
                    if nu in visited:
                        continue
                    visited.add(nu)
                queue.append(nu)
        finally:
            with in_flight_lock:
                in_flight -= 1
            if in_flight == 0 and not queue:
                done_event.set()

    with ThreadPoolExecutor(max_workers=workers) as ex:
        submit_more(ex)
        done_event.wait()
    return visited
```

**The termination invariant:** "done" = queue is empty **and** no worker is currently fetching. Track `in_flight` atomically; signal done when both are zero.

## Design half — full crawler architecture (Anthropic onsite often pairs design + coding)
Reported as a mixed onsite round (half design, half coding): lead with the architecture, then drill one component in code.
- **URL Frontier** — the queue of URLs to fetch. Concerns: storage (in-mem → Redis/Kafka at scale), **priority** (freshness/importance), and **dedup** — a `seen` set keyed by *normalized* URL; at web scale a **Bloom filter** or Redis set.
- **Downloader** — pulls from the frontier, issues HTTP GETs. Engineering: timeouts + **retries/backoff**, a polite **User-Agent**, **per-host rate limiting**, **robots.txt** compliance.
- **Parser** — extracts (a) page text/content for storage and (b) new outlinks → normalize → back to the frontier.
- **Storage** — raw HTML and/or parsed text+metadata; distributed FS or DB; **content-addressed** to dedupe identical pages.
- **Distributed:** shard the frontier by **domain hash** across workers (this also keeps per-host politeness on one shard); shared "seen" via Redis/Bloom; at-least-once vs exactly-once; termination = global frontier empty + no in-flight.

## Async variant (asyncio + aiohttp) — better for I/O-bound crawling
Crawling is network-I/O-bound, so `asyncio` scales concurrent connections more cheaply than threads (one event loop, no per-thread stack). Same structure as the threaded version, with `await`:
```python
import asyncio, aiohttp

async def downloader(queue, session, visited, base_host, results):
    while True:
        url = await queue.get()
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                html = await resp.text()
            results[url] = html
            for nxt in extract_links(html):
                nu = normalize(nxt, base_host)
                if nu and nu not in visited:
                    visited.add(nu)
                    await queue.put(nu)
        except (aiohttp.ClientError, asyncio.TimeoutError):
            pass                      # senior: retry-with-backoff or dead-letter — don't silently drop
        finally:
            queue.task_done()
# run N downloader tasks against one asyncio.Queue + one aiohttp.ClientSession; await queue.join() to terminate
```

### Senior review of the reported answer (author not very senior)
The reported answer had the standard architecture + an async downloader with `ClientError`/`TimeoutError` handling — solid. A stronger answer would also: (1) say **how** the frontier dedupes (normalized-URL `seen` set / **Bloom filter** at scale), not just "avoid duplicates"; (2) add **per-host rate limiting** — it mentioned User-Agent + robots.txt but not throttling, which is what actually gets you IP-banned; (3) cover the **distributed frontier** (shard by domain hash) and **termination/quiescence**; (4) on failure, **retry with backoff / dead-letter**, not a silent `pass`; (5) **content-address storage** to dedupe identical pages. *(Most are in the follow-ups below — the gap was not volunteering them.)*

## By format

### Live · CoderPad (human) — *primary (Anthropic)*
- **How it appears:** single-thread first (~15 min), then "make it concurrent" (~15 min), then a barrage of concept follow-ups (~15 min).
- **Follow-ups (real, reported, in order of likelihood):**
  1. **Thread safety of `visited`** — atomic check-and-add with a `Lock`. State *why* — race produces double-crawl.
  2. **GIL** — I/O-bound (this is!) → threads help; CPU-bound → use `multiprocessing` or `asyncio`.
  3. **Per-host politeness / robots.txt** — sleep between fetches per host; respect `robots.txt` (or a simple version).
  4. **asyncio vs threads vs processes** — for I/O-bound, asyncio is often better; threads are simpler; processes for CPU.
  5. **Distributed crawler** — shard frontier by domain hash; shared "seen" via Redis or a Bloom filter; at-least-once vs exactly-once.
  6. **Backpressure** — limit concurrent fetches; reject new URLs when at capacity.
  7. **Failure handling** — what if `get_urls` raises? Retry with backoff? Mark URL as failed?
  8. **Result aggregation** — return ordered crawl vs just visited set; BFS order vs DFS.
  9. **URL canonicalization edge cases** — case sensitivity, default ports, encoded characters.
- **Tips:**
  - **Get single-thread correct + deduped first.** Don't reach for threads until the base works.
  - Introduce the lock only when you parallelize and **say why** (race on `visited`).
  - Discuss termination explicitly: "I'm done when the queue is empty AND no worker is active."
  - For GIL: state the rule (I/O releases GIL, CPU doesn't); recommend the right primitive.
- **Pitfalls:**
  - **Non-atomic visited check-and-add** — double-crawl.
  - **Never terminating** — no quiescence tracking.
  - **Crawling off-domain** — confirm normalization rules.
  - **Not normalizing URLs** — `http://Foo.com` and `https://foo.com/` are the same.
  - **Holding the lock during `get_urls`** — blocks all other workers on a slow fetch.
  - **Race in `queue.append` from worker** — `deque.append` is thread-safe in CPython, but document the assumption.

### Take-home / work-trial
- **Tips:**
  - Ship single + multithreaded with a `--workers` flag and a politeness delay.
  - Add a `robots.txt` simple parser (skip disallowed paths).
  - README the GIL/asyncio trade-off with concrete reasoning.
  - Add benchmarks: workers=1, 4, 16, 64 with a mock slow `get_urls`.
- **Pitfalls:**
  - **Unbounded threads** — `ThreadPoolExecutor(max_workers=...)` cap.
  - **No rate limiting** — one host's politeness is another's courtesy.
  - **Shared-state races without a lock.**
  - **Not handling `get_urls` exceptions** — single bad URL kills the worker.

### Onsite · NR (Google-style)
- **Tips:** Define normalize + BFS by hand; trace the concurrent termination invariant aloud.
- **Pitfalls:** Confusing GIL release with parallel CPU execution.

## Company variants

- **Anthropic (canonical)** — top reported live question; the "viral" 2024 question.
- **OpenAI / Stripe / Notion / Exa / Perplexity / Common Crawl** — common at search and AI-eng teams.
- **Google** — scaled-out version in system-design rounds.

## Worked example trace

```
seed = "https://example.com/a"
get_urls("https://example.com/a") → ["https://example.com/b", "https://other.com/x", "https://example.com/a#frag"]

normalize("https://example.com/a#frag") → "https://example.com/a"      # dedupes with seed
normalize("https://other.com/x")        → None                          # off-domain, skip
normalize("https://example.com/b")       → "https://example.com/b"

Queue: [a] → visit → enqueue b
Queue: [b] → visit → enqueue whatever b links to
```

## Related
[[15-duplicate-file-detection]] (system-flavored sibling) · Track C distributed-crawler design · [[anthropic-interview-guide]] worked solution (d).