---
tags: [job-hunt, interview-prep, anthropic, intel, oa-vs-onsite, digested]
title: "Anthropic — OA vs On-site (interview intel)"
source: "Notion inbox → ChatGPT share '准备Anthropic SWE面试' (digested 2026-06-19)"
source_url: https://chatgpt.com/share/6a354e57-7120-83ea-a774-6439f7ecb759
related: ["[[anthropic-interview-guide]]", "[[track-B-practical-oo-coding/practical-oo-coding-deep-guide]]", "[[llm-system-design/README]]"]
---

# Anthropic — OA vs On-site

> Interview *intel* digested from a saved ChatGPT conversation. The 100-question bank from the same source was digested into [[question-bank/llm-system-design/fundamentals/README]] (concept Qs) and mapped onto the existing [[llm-system-design/README]] design cards. Reinforces [[anthropic-interview-guide]] and [[practical-oo-coding-deep-guide]] §2e.

The split isn't difficulty — it's **dimension tested**: *OA = "can you write code?"; On-site = "do we want to build Claude **with** you?"*

| | **OA** | **On-site** |
|---|---|---|
| Tests | execution: Python, data structures, code quality, requirement-reading | engineering judgment: architecture, tradeoffs, extensibility, communication |
| Shape | clear, self-contained, time-pressured (60–120 min) | **open-ended, requirements piled on live** |
| Example | implement KV store / cache / event system / data pipeline | "we need a KV store" → +TTL → +snapshot → +replication → +recovery → +concurrent access |
| Rounds | one functional task | coding (pair-programming, interrupted) + **system design** + **code review/debugging** + **AI/safety discussion** |

- **On-site coding = pair programming:** the interviewer interrupts — "what if 1000× the data? concurrent writes? not enough memory? is this API reasonable?" → you keep adjusting the design. (Exactly the multi-level extend-the-object skill — [[practical-oo-coding-deep-guide]].)
- **System design (on-site only):** Anthropic avoids "Design Twitter/Instagram"; prefers **Design Claude API · Design Retrieval System · Design Evaluation Pipeline · Design Agent Framework · Design Distributed Job Queue** → [[llm-system-design/README]].
- **Code review / debugging round** (distinctive): given a real snippet — where's the bug? the perf bottleneck? how would you refactor? (the "fix the cache" variant in [[anthropic-interview-guide]]).
- **AI / Safety discussion** (not in OA): why Anthropic? Claude's safety boundaries? how to evaluate if a model is ready to ship? what if it emits harmful output? → [[track-F-behavioral-staff-values/README]].
- **Applied-AI / AI-leaning SWE:** OA stays generic eng (cache/queue/data/API); **on-site pivots to AI** — design a RAG system, agent system, eval framework, optimize retrieval, LLM serving.

*Digested 2026-06-19. Source archived in [[archives/shared_link]].*
