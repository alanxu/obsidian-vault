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

## To elaborate here
- [ ] `design-problems-leetcode.md` — worked solutions: #146, #460, #981, #380, #1166, #588, #211, #359, #362, #1244, #1396, #535, #2502, #715
- [ ] `multilevel-inmemory-db.md` — SET/GET/DELETE/SCAN → TTL → transactions (the canonical one)
- [ ] `multilevel-ledger-and-kv.md` — expiring credit ledger, GPU credit manager, versioned KV, token-usage aggregator
- [ ] `anthropic-bank.md` — #636 Exclusive Time (stack-trace), #609 Duplicate Files, #1242 Web Crawler
- [ ] `oo-design-checklist.md` — how to structure classes so levels bolt on cleanly

## Drill priority
Re-solve **#146 LRU** and the **in-memory DB** until automatic — they recur most.
