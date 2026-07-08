---
title: Find / Eliminate Duplicate Files
slug: duplicate-file-detection
type: live-coding
leetcode: 609
companies: [Anthropic, Dropbox, Google Drive, Backblaze, AWS-S3-lifecycle, "any systems-flavored team"]
difficulty: ★★★☆☆
frequency: high
formats: [Live, Take-home]
levels: 2
time-box: live 45 min
time-box-take-home: 4–8 hours
tags: [hashing, io-minimization, chunked-reads, system, content-addressed-storage]
related: ["[[anthropic-interview-guide]]", "[[04-cloud-storage-file-host]]", "[[12-multithreaded-web-crawler]]"]
---

# Find / Eliminate Duplicate Files

LeetCode **#609** taken to a **systems level** by Anthropic: minimize I/O, handle huge files, dedupe by content. The "naive hash everything" answer is correct but slow; the **three-stage funnel** is what senior candidates produce.

## Problem

Scan a directory tree; group files with **identical content**; optionally replace duplicates with **hard links** to save space. Constraints implicit in the question: 1M+ files, 10GB+ files, slow disks.

## Core approach (format-agnostic) — the three-stage funnel

```
                   ┌──────────────────────┐
1M files           │ Group by file size   │  ~1% pass
                   └──────────┬───────────┘
                              │ same size
                              ▼
                   ┌──────────────────────┐
                   │ Hash head + tail sig │  ~10% of those pass
                   └──────────┬───────────┘
                              │ same sig
                              ▼
                   ┌──────────────────────┐
                   │ Full SHA-256 (chunked)│  identical iff match
                   └──────────────────────┘
```

**Why:** hashing every file is O(total bytes); the funnel is O(unique-bytes). For 1M files where 99% are unique sizes, you never read their contents.

1. **Walk** the tree (`os.walk`), collect `(path, size)`.
2. **Group by size.** Unique size ⇒ skip. (Cheap; one stat per file.)
3. **Hash head + tail.** Read first N bytes and last N bytes (N ≈ 64KB–1MB). Hash them together with `(size, head, tail)`. Files that don't match → skip.
4. **Hash fully** (chunked, never load whole file). Only for collision groups.

**Optimization choices:**
- **Chunk size** — 64KB–1MB. Aligned to FS block (typically 4KB) to avoid double-reads at boundaries.
- **Hash algorithm** — SHA-256 (collision-resistant) for final; cheaper (xxhash, blake2b) for the head/tail signature.
- **Parallelism** — I/O-bound → threads/asyncio; CPU-bound (hashing) → multiprocess.
- **Streaming** — never `read()` a whole file. Use `read(size)` in a loop.

### Worked Python solution

```python
import os
import hashlib
from collections import defaultdict

CHUNK = 1024 * 1024                # 1MB
SIG_SIZE = 1024 * 64               # 64KB head + 64KB tail

def file_sig(path, size):
    """Head + tail signature; cheap collision-buster."""
    h = hashlib.blake2b(digest_size=16)
    h.update(size.to_bytes(8, "little"))
    try:
        with open(path, "rb") as f:
            head = f.read(SIG_SIZE)
            h.update(head)
            if size > SIG_SIZE * 2:
                f.seek(size - SIG_SIZE)
                tail = f.read(SIG_SIZE)
                h.update(tail)
    except OSError:
        return None
    return h.hexdigest()

def file_hash(path):
    """Full content hash, streamed."""
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            while True:
                buf = f.read(CHUNK)
                if not buf:
                    break
                h.update(buf)
    except OSError:
        return None
    return h.hexdigest()

def find_duplicates(root):
    # Stage 1: group by size
    by_size = defaultdict(list)
    for dirpath, _, filenames in os.walk(root):
        for fn in filenames:
            p = os.path.join(dirpath, fn)
            try:
                size = os.path.getsize(p)
            except OSError:
                continue
            by_size[size].append(p)

    # Stage 2: signature
    by_sig = defaultdict(list)
    for size, paths in by_size.items():
        if len(paths) < 2:
            continue                          # unique size → skip
        for p in paths:
            sig = file_sig(p, size)
            if sig:
                by_sig[(size, sig)].append(p)

    # Stage 3: full hash
    duplicates = []
    for key, paths in by_sig.items():
        if len(paths) < 2:
            continue
        by_hash = defaultdict(list)
        for p in paths:
            h = file_hash(p)
            if h:
                by_hash[h].append(p)
        for h, ps in by_hash.items():
            if len(ps) >= 2:
                duplicates.append(ps)
    return duplicates

def dedupe_hardlinks(duplicate_groups):
    """Replace duplicates with hard links to the first file in each group."""
    for group in duplicate_groups:
        keeper, *dupes = group
        for d in dupes:
            try:
                os.remove(d)
                os.link(keeper, d)
            except OSError:
                continue
    return duplicate_groups
```

**Complexity.** Walk O(files). Stage 1 O(files). Stage 2 O(|collision-by-size| × 128KB). Stage 3 O(|collision-by-sig| × file_size). For typical inputs, stages 2–3 are bounded by a tiny fraction of stage 1's I/O.

## By format

### Live · CoderPad (human) — *primary (Anthropic)*
- **How it appears:** naive "hash everything" first (~10 min), then "make it efficient for 1M files / 10GB files" (~20 min), then concept follow-ups.
- **Follow-ups (real, reported):**
  - **Chunk size** — trade-off: too small → many syscalls; too large → memory + bad alignment. 64KB–1MB typical.
  - **SHA-256 vs MD5 vs xxhash** — collision resistance vs speed.
  - **I/O-bound vs CPU-bound** — parallelize accordingly: threads/asyncio for I/O, multiprocess for hashing.
  - **Cross-machine dedup** — content-addressed storage (CAS); distribute by hash prefix (shard by `hash[0:2]`).
  - **Incremental** — maintain a reverse index `(size, sig, full_hash) → paths`; query is O(1) lookup.
  - **Compression-aware** — gzip files may have different content but same logical data; decompress before hashing.
  - **Permissions / owner preservation** — hard-link replaces file with shared inode.
  - **Symlinks** — don't follow (avoid cycles); or follow with `--follow` flag.
  - **Memory pressure** — at 1M files, the index is ~hundreds of MB; spill to disk.
  - **Error handling** — file disappears between stat and read; permission denied; long paths.
  - **Near-duplicate detection** — "95% identical files (logs with one extra line)?" → exact hashing fails by design → chunk-level dedup (fixed or content-defined chunking / rolling hash, rsync-style) or similarity sketches (MinHash) — a different problem family; naming CDC is the depth signal.
  - **TOCTOU on the dedupe step** — file modified between hash and hard-link → re-verify (size+mtime or rehash) immediately before linking, or link-then-verify; the race is small but the data loss is real.
- **Tips:**
  - **Lead with the funnel** and **why** (avoid hashing unique-size files).
  - **Handle `OSError` gracefully** — file vanished, permission denied. Don't crash.
  - For parallel: articulate the I/O-vs-CPU split before reaching for `concurrent.futures`.
  - For incremental: describe the reverse index as `dict[(size, sig, hash) → list[paths]]`.
- **Pitfalls:**
  - **Loading whole files** — `read()` on a 10GB file = OOM.
  - **Hashing everything** — no size pre-filter.
  - **Ignoring permission errors / vanished files.**
  - **Collision handling** — two files with same SHA but different contents is astronomically unlikely with SHA-256; document the assumption.
  - **Naive hard-link** — breaks if the original file is later modified (other "copies" change too).
  - **Hashing text vs binary** — read in binary mode (`"rb"`) to avoid newline translation on Windows.

### Take-home / work-trial
- **Tips:**
  - Ship the funnel + chunked reads + a hard-link mode behind a flag.
  - Add an `--incremental` mode that persists the index to JSON / sqlite.
  - README the I/O-vs-CPU analysis.
  - Provide a benchmark on a synthetic 10k-file tree.
- **Pitfalls:**
  - **No streaming** — OOM on big files.
  - **No error handling** — single bad file crashes.
  - **No tests for the collision path** — Stage 3 is exactly where bugs hide.
  - **Hashing text** — silent corruption on Windows.

### Onsite · NR (Google-style)
- **Tips:** Draw the funnel on the whiteboard with the cost at each stage.
- **Pitfalls:** Forgetting Stage 1.

## Company variants

- **Anthropic (canonical)** — the systems-flavored Anthropic problem; very common live.
- **Dropbox / Google Drive / Backblaze / AWS S3 lifecycle** — production-flavored dedup.
- **Any systems-flavored team** — storage, backup, build systems.

## Worked example trace

```
Tree:
a/1.txt (1KB, content "hello")
a/2.txt (1KB, content "hello")
a/3.txt (1KB, content "world")
b/4.txt (2KB, content "abc...")
b/5.txt (3KB, content "xyz...")

Stage 1 (by size):
  1KB: [a/1.txt, a/2.txt, a/3.txt]
  2KB: [b/4.txt]
  3KB: [b/5.txt]

Stage 2 (sig of 1KB group):
  (1KB, "sig_hello"): [a/1.txt, a/2.txt]
  (1KB, "sig_world"): [a/3.txt]

Stage 3 (full hash):
  sha("hello"): [a/1.txt, a/2.txt]  ← duplicate group

Result: [{a/1.txt, a/2.txt}]
```

## Related
[[04-cloud-storage-file-host]] (dedupe follow-up) · [[12-multithreaded-web-crawler]] (I/O patterns) · [[anthropic-interview-guide]] (c).