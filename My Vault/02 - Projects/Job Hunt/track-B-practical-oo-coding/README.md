---
tags: [job-hunt, interview-prep, track, oo-coding, practical-coding]
track: "Track B — Practical / OO coding bank"
plan-section: "§3"
budget-hrs: 12
parent: [[interview-prep-master-plan-2026]]
---

# Track B — Practical / OO Coding Bank  (master plan §3)

**Charter:** the frontier-lab favorite — build one stateful object across 3–6 escalating levels (add TTL, transactions, history) without breaking earlier levels. Tests clean abstractions, incremental design, and saying your interface before coding.

**Who leans on it:** Anthropic, OpenAI, Anysphere, Harvey (and CodeSignal OAs at Robinhood/xAI). Cross-ref [[openai-interview-guide]] (worked solutions) and [[anthropic-interview-guide]].

## Question bank → moved to the canonical [[question-bank/README|/question-bank]]
The per-question bank now lives **outside the track folders** at **[[question-bank/README|/question-bank]]**, under **[[question-bank/practical-coding/README|/question-bank/practical-coding]]** — it's a shared resource, because these problems are Track B content *regardless* of whether a company delivers them as OA, live, or async take-home (delivery channel ≠ track). The old Track B and Track G copies were merged there (34 questions, one file each, fully enriched).

Each file has frontmatter (`companies · formats · difficulty · LC#`), a worked solution/sketch, **and a "By format" section with per-format follow-ups, tips & pitfalls** (OA·ICA / GCA·HR / live / take-home / onsite).

Start with [[01-in-memory-key-value-database|01 — in-memory DB]] and [[17-lru-cache|17 — LRU]] (together ~80% of the pattern). Round mechanics & worked walk-through: [[practical-oo-coding-deep-guide]].

> **Boundary (B vs G):** Track B = *implement a stateful component* (known answer; this bank). Track G = *build a small project* over hours–days (RAG/agent/doc-extraction; [[take-home-question-bank]]). A timed async coding assessment is a Track B problem delivered async.

## Drill priority
Re-solve **#146 LRU** and the **in-memory DB** until automatic — they recur most.
