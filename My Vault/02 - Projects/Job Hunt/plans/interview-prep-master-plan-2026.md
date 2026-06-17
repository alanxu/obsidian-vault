---
tags: [job-hunt, interview-prep, master-plan, staff-engineer, ai-engineer, 2026]
created: 2026-06-16
updated: 2026-06-16
status: active
horizon: 10 weeks (8–12 week window)
budget: <10 hrs/week (~90 hrs total)
profile: backend/infra-strong, closing ML/LLM gap, Staff level
targets: [Anthropic, OpenAI, Google, NVIDIA, Cohere, Harvey, Waymo, Robinhood, Waabi, Wealthsimple, Lyft, Anysphere]
---

# Staff AI Engineer — Master Interview Prep Plan (2026)

**One plan, all 12 targets.** This is the orchestration layer. Where a company already has its own deep-dive in this folder, this plan points to it instead of repeating it:
- [[anthropic-interview-guide]] — Anthropic (SWE / Applied AI / FDE, coding bank, values round)
- [[openai-interview-guide]] — OpenAI (8-problem coding bank with worked solutions)
- [[cohere-interview-guide]] — Cohere (enterprise LLM, take-home)
- [[ai-ipo-interview-guide]] — Anthropic, OpenAI, Cohere, Anysphere, Harvey + 7 more (process + questions)
- [[ai-companies-toronto-research-2026-06-16]] — company scoring, comp, open roles

---

## 0. Strategy — why one plan covers all 12

Your 12 targets look different but draw from the **same 7 interview surfaces**. Prep the surfaces once; re-skin per company in the final week. (Surface **G — take-home** is a *delivery format*, not a topic: it repackages A/B/D as async work-on-your-own-time, and for Cohere it's the gating round.)

| Surface | What it tests | Who leans on it hardest |
|---|---|---|
| **A. Algorithmic coding** | LeetCode med/hard, patterns, speed | Google, NVIDIA, Waymo, Lyft, Robinhood |
| **B. Practical / OO coding** | Multi-part stateful service ("in-memory DB", ledger, KV store) | Anthropic, OpenAI, Anysphere, Harvey |
| **C. Distributed system design** | Scalable backend (your strength) | Google, NVIDIA, Robinhood, Lyft, Wealthsimple |
| **D. ML / LLM system design** | RAG, inference serving, agents, training | Every AI role — your growth area |
| **E. ML / LLM fundamentals** | Attention, decoding, fine-tuning, RLHF | Frontier labs + all "AI Engineer" titles |
| **F. Behavioral / staff / values** | Scope, influence, judgment, mission fit | All — #1 failure point at frontier labs |
| **G. Take-home / work-trial** | Async coding/ML build, or analysis + **write-up/presentation** | **Cohere (gating, ~30% pass)**, OpenAI (work-trial), Anthropic, Harvey, Anysphere, Together |

**Company → archetype map:**

- **Frontier labs** (Anthropic, OpenAI, Cohere, Anysphere, Harvey): heavy on **B + D + E + F**, and most gate via **G (take-home/work-trial)**. Algorithmic bar exists but the differentiator is practical coding + AI depth + mission.
- **Big Tech / AV** (Google, NVIDIA, Waymo, Lyft, Robinhood): heavy on **A + C + D + F**. Classic loop, staff = more system design and leadership signal.
- **Toronto product/AV** (Wealthsimple, Waabi): pragmatic **A + C + F**, lighter algorithmic bar, strong "bring your own system" / real-world judgment.

### Your calibration (from intake)
- **10-week horizon, <10 hrs/week → ~90 hrs total.** Every hour is budgeted below. Do not over-invest in any single surface.
- **Backend/infra-strong → ML-lighter.** We *spend down* your systems strength (Surface C is mostly re-skinning) and *invest* the freed time into **D + E** (ML/LLM), your highest-ROI gap.
- **Staff level.** Coding still gates you at labs, but the bar that *distinguishes* you is system design depth, technical judgment, and influence stories. Budget reflects that: less algo grinding than a new-grad plan, more design + narrative.

### Budget allocation (~90 hrs)

| Track | Hours | Why this weight |
|---|---|---|
| A — Algorithmic coding | 20 | Re-sharpen patterns + speed; labs & big tech still gate on it |
| B — Practical / OO bank | 12 | Highest-yield for labs; pattern-dense, fast to learn |
| C — Distributed system design | 8 | Your strength — adapt, don't rebuild |
| D — ML / LLM system design | 18 | Core of every AI role; your growth area |
| E — ML / LLM fundamentals | 18 | Closes your infra→ML gap; unlocks D and E rounds |
| F — Behavioral / staff / values | 8 | Cheap to prep, decisive at labs |
| G — Take-home dry-run + template | 4 | One practice build + reusable scaffold; the rest is *reactive* (see §7.5) |
| Mocks + buffer | 4 | Timed reps, slippage |

> **G is mostly reactive.** The 4 hrs above buy a *dry-run + reusable template* so you're not starting cold. When a real take-home lands (esp. Cohere), it temporarily becomes your top priority — clear that week's other tracks and spend 8–15 focused hrs on it. Build the template now so that week is execution, not panic.

---

## 1. The 10-week schedule

~9 hrs/week, 3 sessions/week (e.g. 2× weekday evenings ~2.5 hrs + 1 weekend block ~4 hrs). Each week has a **theme**, a **coding rep target**, and a **non-coding focus**. Check boxes as you go.

### Phase 1 — Foundations (Weeks 1–2): close the ML gap early, re-sharpen coding

**Week 1 — Diagnostic + ML fundamentals kickoff**
- [ ] (1.5h) Diagnostic: 1 timed LeetCode medium (e.g. **#56 Merge Intervals**) + 1 OO problem (**#146 LRU Cache**). Note where you stall — this calibrates the plan.
- [ ] (3h) **E**: Transformers from zero → §4 Block 1. Watch one lecture (Karpathy "Let's build GPT" or 3Blue1Brown attention), then write attention math by hand.
- [ ] (2h) **A**: Arrays/Hashing/Two-pointer warm-up — #1, #49, #271, #125, #15.
- [ ] (2h) **F**: Draft your staff story skeleton (§7) — list 8 candidate stories, one line each. No polishing yet.

**Week 2 — Attention + sliding window/stack + story scoping**
- [ ] (3h) **E**: Implement multi-head attention + softmax + layernorm in NumPy from scratch (no framework). This single exercise pays off in B, D, and E rounds.
- [ ] (3h) **A**: Sliding window + stack — #3, #424, #76, #20, #155, #739.
- [ ] (1.5h) **B**: #981 Time-Based KV Store + read OpenAI guide Problem 1 (versioned KV) — internalize the pattern.
- [ ] (1.5h) **F**: Expand 2 stories to full STAR + add staff signals (§7).

### Phase 2 — Core build (Weeks 3–5): depth in coding, OO, ML fundamentals; begin ML design

**Week 3 — Graphs + ML training fundamentals**
- [ ] (3h) **A**: Graphs (your AV/infra targets love these) — #200, #695, #207, #210, #133, #994.
- [ ] (2.5h) **E**: Fine-tuning landscape — full vs LoRA/QLoRA, RLHF (SFT→RM→PPO/DPO). Be able to draw the RLHF pipeline.
- [ ] (2h) **B**: #380 Insert/Delete/GetRandom, #155 Min Stack, #208 Trie.
- [ ] (1.5h) **F**: 2 more stories to full STAR.

**Week 4 — DP + intervals + inference fundamentals**
- [ ] (3h) **A**: DP + intervals — #322, #300, #139, #57, #253, #1851.
- [ ] (2.5h) **E**: Inference internals — KV cache, continuous batching, paged attention, quantization, speculative decoding, flash attention. Know the memory math.
- [ ] (2h) **D**: First ML design — **Design a RAG system with citations** (§6 D1). Write a full answer; compare to Cohere/Perplexity notes in your guides.
- [ ] (1.5h) **B**: #146 LRU + #460 LFU back-to-back, timed.

**Week 5 — Design-pattern coding + first distributed design + decoding**
- [ ] (3h) **B**: Multi-part stateful service — work OpenAI guide Problems 4–6 (expiring ledger, GPU credit manager, in-memory DB w/ TTL). These are *the* lab pattern.
- [ ] (2h) **C**: **Design a rate limiter** + **Design a distributed KV/cache** (§5). Re-skin your existing systems knowledge to the SD interview format (HelloInterview structure).
- [ ] (2h) **E**: Decoding (greedy/beam/top-k/top-p/temperature) + embeddings/vector DB/ANN (HNSW, IVF). Implement top-k + top-p sampling in NumPy.
- [ ] (2h) **A**: Trees + heaps — #102, #98, #230, #236, #703, #215.

### Phase 3 — Integration (Weeks 6–8): system design heavy, behavioral polish, company-specific

**Week 6 — ML system design block**
- [ ] (3.5h) **D**: **Design an LLM inference serving platform** (§6 D2) + **Design an agentic platform / agent loop** (§6 D3). The agent one is critical for Robinhood, Anysphere, Harvey, Anthropic.
- [ ] (2h) **C**: **Design ride-matching/dispatch (geospatial)** + **real-time metrics/monitoring service** (§5). Hits Lyft, Waymo, Robinhood.
- [ ] (2h) **A**: Backtracking + advanced graphs — #39, #79, #269 Alien Dictionary, #1584 MST.
- [ ] (1.5h) **F**: Write "Why [company]" hooks for your top 4 (§8 cheat sheets).

**Week 7 — Distributed design + training design + behavioral depth**
- [ ] (3h) **D**: **Design a distributed training pipeline (70B model)** + **Design an LLM eval harness** (§6 D4–D5). Lean on your infra strength here — this is where you shine.
- [ ] (2h) **C**: **Design a payment/ledger with idempotency** + **petabyte log ingestion pipeline** (§5). Robinhood/Wealthsimple/Waymo.
- [ ] (2h) **B**: Anthropic coding bank — #636 Exclusive Time (stack-trace), #609 Duplicate Files, #1242 Web Crawler. See [[anthropic-interview-guide]].
- [ ] (2h) **F**: Full mock of the **values/behavioral round** out loud (record yourself). Labs fail people here.

**Week 8 — ML coding + RAG/agents deep + mock #1**
- [ ] (2.5h) **E/B**: ML coding round (Waymo-style) — implement k-means, logistic regression w/ gradient descent, and a tiny ReAct agent loop (tool call → observe → act).
- [ ] (2h) **D**: **Design fraud detection w/ LLMs** + **Design a feature store / real-time ML serving** (§6 D6–D7). Robinhood, Wealthsimple, Stripe-style.
- [ ] (2.5h) **MOCK**: One full mock loop — 1 coding (timed 45 min) + 1 system design (45 min). Use a peer or Pramp/interviewing.io. Debrief in writing.
- [ ] (2h) **G**: Take-home **dry-run** — build the reusable scaffold from §7.5 on a realistic AI-eng task (e.g. a small RAG/eval script) so a real one is execution, not panic.

### Phase 4 — Simulation + company-specific (Weeks 9–10): reps under pressure, re-skin per company

**Week 9 — Company-specific drilling + mock #2**
- [ ] (3h) **Company block**: For your top 4 companies, do the "if you only do one thing" item from each cheat sheet (§8).
- [ ] (2.5h) **MOCK**: Second full loop — emphasize whichever surface scored lowest in Week 8.
- [ ] (2h) **A**: Timed mixed set — 4 random mediums in 90 min (simulates CodeSignal OA used by Robinhood, xAI, Anysphere).
- [ ] (1.5h) **D/E**: Re-read your weakest ML topic; re-answer one ML design prompt cold.

**Week 10 — Taper, polish, logistics**
- [ ] (2h) **F**: Final pass on all stories + "questions to ask" per company. Memorize your 3 strongest stories cold.
- [ ] (2h) **B/A**: Light — re-solve 3 problems you previously failed, confirm they're now automatic. No new material.
- [ ] (2h) **Company block**: Final cheat-sheet review for the 2–3 companies interviewing first. Mission/values talking points.
- [ ] (1h) Logistics: confirm setup (IDE, CoderPad familiarity, camera/mic), sleep, schedule buffer. **Do not cram new topics.**

> **Slip rule:** if a week runs over, protect **E (fundamentals)** and **F (behavioral)** first — they're your gap and the cheapest points. Algorithmic volume (A) is the safe place to trim.
>
> **Take-home override:** a real take-home (esp. **Cohere**, ~30% pass) outranks everything. When one lands, pause the week's tracks and pour 8–15 hrs into it using the §7.5 playbook. It's a scored work sample — treat it like the job.

---

## 2. Track A — Algorithmic coding (exact problem bank, ~22 hrs)

Backbone = **NeetCode 150** patterns. You don't need all 150; below is the **prioritized ~55** weighted to these companies (graphs/intervals/geospatial for AV+mobility, design for labs). Do them by pattern, not randomly. Target: medium in ≤25 min, hard in ≤40 min, talking the whole time.

**Arrays / Hashing / Two-pointer / Sliding window**
- #1 Two Sum · #49 Group Anagrams · #271 Encode/Decode Strings · #238 Product Except Self · #128 Longest Consecutive
- #125 Valid Palindrome · #15 3Sum · #11 Container With Most Water
- #3 Longest Substring No Repeat · #424 Longest Repeating Char Replacement · #76 Minimum Window Substring

**Stack / Binary search**
- #20 Valid Parens · #155 Min Stack · #150 Eval RPN · #739 Daily Temperatures · #84 Largest Rectangle
- #704 Binary Search · #153 Min in Rotated · #33 Search Rotated · #875 Koko Eating Bananas

**Linked list / Trees / Tries / Heap**
- #206 Reverse List · #21 Merge Two Lists · #143 Reorder · #23 Merge k Lists · #138 Copy w/ Random Pointer
- #102 Level Order · #98 Validate BST · #230 Kth Smallest BST · #236 LCA · #297 Serialize/Deserialize Tree
- #208 Trie · #211 Add/Search Word · #212 Word Search II
- #703 Kth Largest Stream · #215 Kth Largest Array · #295 Median from Stream · #355 Design Twitter

**Graphs (high priority — Waymo/Lyft/Google)**
- #200 Number of Islands · #695 Max Area Island · #133 Clone Graph · #994 Rotting Oranges
- #207 Course Schedule · #210 Course Schedule II · #417 Pacific Atlantic · #743 Network Delay (Dijkstra)
- #269 Alien Dictionary (topo sort) · #1584 Min Cost Connect Points (MST) · #684 Redundant Connection (union-find) · #127 Word Ladder

**DP / Intervals / Greedy (intervals high priority)**
- #70 Climbing Stairs · #198 House Robber · #322 Coin Change · #300 LIS · #139 Word Break · #152 Max Product Subarray
- #62 Unique Paths · #1143 LCS · #72 Edit Distance
- #57 Insert Interval · #56 Merge Intervals · #435 Non-overlapping · #253 Meeting Rooms II · #1851 Min Interval to Include Query
- #53 Max Subarray · #55 Jump Game · #134 Gas Station

**Concurrency (Robinhood/NVIDIA/Waymo C++ threading)** — do if targeting these
- #1114 Print in Order · #1115 Print FooBar · #1116 Print Zero Even Odd · #1242 Web Crawler Multithreaded

**How to practice:** First pass untimed, learn the pattern. Second pass timed, narrate aloud. Keep a "failed problems" list and re-drill only those in Weeks 9–10. Pick **one language and stay in it** — Python is the safe default for AI roles (C++ only if targeting NVIDIA/Waymo perf teams).

---

## 3. Track B — Practical / OO coding bank (the lab favorite, ~12 hrs)

Frontier labs (Anthropic, OpenAI, Anysphere) and CodeSignal OAs (Robinhood, xAI) favor a **multi-part, stateful-service** problem over pure algorithms: you build one object across 3–6 escalating levels (add TTL, add transactions, add history). They test clean abstractions, incremental design, and not breaking earlier levels.

**LeetCode "Design"-tagged core (do all):**
- #146 LRU Cache · #460 LFU Cache · #981 Time-Based KV Store · #380 Insert/Delete/GetRandom O(1)
- #1166 Design File System · #588 In-Memory File System · #211 Add/Search Word
- #359 Logger Rate Limiter · #362 Hit Counter · #1244 Design Leaderboard · #1396 Underground System
- #535 Encode/Decode TinyURL · #2502 Design Memory Allocator · #715 Range Module

**Frontier-lab multi-level problems (worked solutions in [[openai-interview-guide]]):**
1. **In-memory database** — SET/GET/DELETE/SCAN, then add TTL/expiry, then transactions (BEGIN/COMMIT/ROLLBACK). *The* canonical one.
2. **Versioned / time-based KV store** (#981 generalized to history queries).
3. **Expiring credit ledger** — apply out-of-order, time-bounded credits; query balance at time T.
4. **GPU credit manager** — allocate/reclaim quota across users with limits.
5. **API log parser / token-usage aggregator** — parse logs, aggregate by window/user.
6. **Multi-file iterator** + **CD directory navigation** (path resolution like #1166).

**Anthropic-specific bank (see [[anthropic-interview-guide]]):**
- #636 Exclusive Time of Functions ("longest-running function from stack-trace samples")
- #609 Find Duplicate File in System ("duplicate file detection/elimination")
- #1242 / #1236 Web Crawler

**How to practice:** Solve each as if levels will be added — favor a clean class with small methods over a clever one-liner. Practice saying your interface *before* coding. Re-solve #146 and the in-memory DB until they're muscle memory; they recur most.

---

## 4. Track E — ML / LLM fundamentals (your gap, ~18 hrs)

You're infra-strong, so you'll learn the *systems* of ML fast; the gap is the **modeling vocabulary**. Bar to hit: for each item, be able to (a) explain it to a peer in 2 min, (b) whiteboard the shape, and for starred items (c) implement a toy version in NumPy. Do these in the schedule's order.

**Block 1 — Transformer architecture** ⭐
- Self-attention & **multi-head attention** ⭐ (implement) · scaled dot-product, why √d_k
- Positional encodings: sinusoidal vs **RoPE** vs ALiBi
- Transformer block: attention + FFN + residual + **LayerNorm** ⭐ (pre-LN vs post-LN)
- **GQA vs MHA vs MQA** + KV-cache memory math (this exact tradeoff is a staff-level probe)
- MoE / sparse routing (Mixtral) — what's sparse, what's the tradeoff

**Block 2 — Training**
- Pretraining objective (next-token), cross-entropy ⭐, perplexity
- Fine-tuning: full vs **LoRA/QLoRA** vs prompt/PEFT — *when to use which* (decision framework)
- **RLHF**: SFT → reward model → PPO; **DPO** and what it simplifies — draw the pipeline
- Optimizers (Adam/AdamW), LR warmup + schedule, gradient clipping
- Scale tricks: mixed precision (bf16), gradient checkpointing, **ZeRO/FSDP**
- Parallelism: **data / tensor / pipeline / sequence** — what each splits

**Block 3 — Inference** ⭐
- **KV cache** ⭐, continuous batching, **paged attention** (vLLM)
- Quantization: int8/int4, GPTQ/AWQ, GGUF
- **Speculative decoding**, **flash attention** (memory-IO win)
- Decoding: greedy, beam, **top-k / top-p / temperature** ⭐ (implement sampling)
- Serving metrics: throughput vs latency, **TTFT vs TPOT**, p50/p99

**Block 4 — RAG & agents**
- Embeddings, vector DBs, ANN: **HNSW, IVF** · exact vs approximate tradeoff
- Chunking strategies, **hybrid search** (BM25 + dense), **re-ranking** (cross-encoder)
- Hallucination: causes + mitigations (grounding, citations, constrained decoding)
- **Agent loop**: ReAct, planning, tool calling, memory, reflection, error recovery
- Eval: offline metrics, **LLM-as-judge**, human eval, regression/capability suites

**Block 5 — Safety (Anthropic / OpenAI only)**
- Alignment basics, red-teaming, jailbreaks
- Anthropic **Responsible Scaling Policy** / OpenAI **Preparedness Framework** — have an informed POV (see [[anthropic-interview-guide]] values section)

**Resources:** Karpathy "Zero to Hero" (esp. "Let's build GPT"), Jay Alammar "Illustrated Transformer", Lilian Weng's blog (agents, RLHF), the vLLM paged-attention paper, HuggingFace LLM course. Pick one source per topic — don't tab-hoard.

---

## 5. Track C — Distributed system design (your strength, ~8 hrs)

You already have the systems chops; the job here is **format + re-skinning**, not learning. Use the HelloInterview framework: requirements → API → high-level → deep-dive on 1–2 components → scale/bottlenecks. Practice these prompts (each maps to specific targets):

| Prompt                                     | Re-skins to                                          | Key probes                                           |
| ------------------------------------------ | ---------------------------------------------------- | ---------------------------------------------------- |
| **Rate limiter**                           | Robinhood, any API platform                          | token bucket vs sliding window, distributed counters |
| **Distributed KV store / cache**           | Google, NVIDIA                                       | consistency, partitioning, eviction, replication     |
| **Ride-matching / dispatch (geospatial)**  | Lyft, Uber, Waymo                                    | geohash/quadtree, supply-demand, latency             |
| **Real-time metrics / monitoring service** | Waymo (disengagements), Robinhood (incident metrics) | time-series, aggregation windows, alerting           |
| **Payment / ledger with idempotency**      | Robinhood, Wealthsimple                              | exactly-once, double-entry, idempotency keys         |
| **Petabyte log ingestion pipeline**        | Waymo (vehicle logs), NVIDIA                         | batching, partitioning, backpressure, cost           |
| **News feed / notification system**        | general big-tech                                     | fan-out, push vs pull                                |
| **Distributed job scheduler / task queue** | NVIDIA (training jobs), Scale                        | priority, SLA, retries, dead-letter                  |

**Tip:** at staff level, lead with **requirements clarification + explicit tradeoffs + failure modes**, and name the *one* thing you'd build first and why. Interviewers score judgment over breadth.

---

## 6. Track D — ML / LLM system design (core of the AI role, ~18 hrs)

This is where infra-strong candidates win AI roles — you bring the distributed-systems rigor most ML candidates lack. Same framework as C, plus an ML layer (data, model, eval, online/offline). Drill these 8 prompts (named **D1–D8** in the schedule):

- **D1 — RAG system with citations.** Chunking, dense vs sparse retrieval, hybrid + re-ranking, context assembly, hallucination mitigation, citation verification. *(Perplexity, Cohere, Harvey, Glean)*
- **D2 — LLM inference serving platform.** Continuous batching, KV cache, paged attention, speculative decoding, autoscaling, p99 latency, multi-tenant quotas. *(NVIDIA, OpenAI, Anthropic, Anysphere)*
- **D3 — Agentic platform / agent orchestration loop.** Planning, tool calling, memory, retries/error recovery, sandboxing, eval, observability, cost control. *(Robinhood agentic AI, Anysphere, Harvey, Anthropic)*
- **D4 — Distributed training pipeline (70B model).** Data/tensor/pipeline parallelism, checkpointing, fault tolerance, comms overhead, data loading. *(OpenAI, NVIDIA, Cohere — your infra strength shines)*
- **D5 — LLM eval harness / capability-regression monitoring.** Offline + online eval, LLM-as-judge, regression suites, drift detection after fine-tunes. *(Anthropic, OpenAI)*
- **D6 — Real-time fraud detection with LLMs/ML.** Feature pipeline, streaming inference, precision/recall tradeoff, feedback loop. *(Robinhood, OpenAI reported, Wealthsimple)*
- **D7 — Feature store + real-time ML serving.** Online/offline parity, freshness, point-in-time correctness. *(Robinhood, Wealthsimple, Stripe-style)*
- **D8 — Embedding pipeline at 100M+ docs w/ incremental updates** *(Cohere, Glean)* **or AV simulation/scenario generation** *(Waabi, Waymo)* — pick based on your top targets.

**Also have a one-paragraph answer ready for:** code-completion serving sub-100ms (Anysphere), LLM gateway/router with caching+fallback+cost (applied-AI roles), content moderation at 10B msgs/day (Anthropic).

**How to practice:** write a full structured answer for D1–D5 (these cover ~90% of cases), then verbally rehearse D6–D8. Cross-reference the company guides — Cohere/Perplexity/Harvey entries in [[ai-ipo-interview-guide]] list the exact ML-design questions reported.

---

## 7. Track F — Behavioral / staff narrative / values (~8 hrs)

At frontier labs this is **the #1 failure point** (see [[anthropic-interview-guide]] values section). Staff level means your stories must show **scope, technical leadership, influence without authority, judgment under ambiguity, and multiplying other engineers** — not just "I coded a feature."

**Story bank — prepare 6–8 STAR stories, each tagged with the staff signal it shows:**

1. **Biggest technical impact** — measurable outcome, your specific leverage.
2. **Cross-team influence / drove consensus** — influence without authority.
3. **Disagreement / conflict** — with a senior person; how you resolved it with data.
4. **Failure & what you learned** — real failure, real lesson, no humble-brag.
5. **Ambiguous / underspecified problem** — how you created clarity.
6. **Tradeoff under constraint** — where you chose B over A and why (judgment).
7. **Mentoring / multiplying** — made others better; raised the bar.
8. **Incident / firefight** — calm under pressure, systematic debugging.

For each: 30-sec version + 2-min version. Lead with the result, then how. Quantify. Name the tradeoff you owned.

**Values / mission prep (company-specific):**
- **Anthropic** — safety-first, honesty, "do the right thing." Have a *genuine* POV on AI safety + read the Responsible Scaling Policy. They probe for it directly.
- **OpenAI** — mission ("benefit all of humanity"), intensity, agency. Why this matters to *you*.
- **Google** — "Googliness" + General Cognitive Ability; collaboration, humility, navigating ambiguity at scale.
- **Robinhood / Wealthsimple** — democratizing finance; ownership, reliability, user trust.
- **Waymo / Waabi** — safety-critical engineering culture; rigor, verification mindset.
- **NVIDIA** — performance obsession, technical depth, pace.

**Always prepare 3–4 questions to ask** each interviewer (team's hardest current problem, how decisions get made, what success looks like in 6 months). For each company write **one specific "why this company"** line tied to their actual product/research (§8).

---

## 7.5 Track G — Take-homes & work trials (~4 hrs prep + reactive)

Several targets gate on async assignments. They're a **relative advantage for you** (infra-strong, more time than a 45-min live round) — *if* you treat them as a scored work sample, not a quick script. Most candidates lose here on **polish, scope, and communication**, not raw ability.

**Who uses them & what type:**

| Company | Type | Notes |
|---|---|---|
| **Cohere** | **Analysis + write-up/presentation** | The gating round, ~30% pass. ~48-hr window. *Communication-graded, not just code.* See [[cohere-interview-guide]]. |
| **OpenAI** | Work-trial / take-home build | ~48-hr practical build; sometimes paid on-site work day. |
| **Anthropic** | Coding assessment (90 min, 4 progressive levels) | More timed-assessment than open build; see [[anthropic-interview-guide]] (incl. their **AI-usage policy**). |
| **Harvey / Anysphere** | Practical AI-eng take-home or CodeSignal | Build something real (often LLM/agent-flavored). |
| **Together** | 4–8 hr build (senior/research) | Inference-engine → CUDA kernel; platform → systems problem. |

### The three types and what graders reward
1. **Timed coding assessment** (Anthropic, CodeSignal OAs) → correctness + clean incremental design under time. *Prep = your A/B tracks; no special work.*
2. **Open-ended build** (OpenAI, Harvey, Anysphere, Together) → working software + judgment. Graded on: does it run, is it correct, is the code clean, did you make sane scope/tradeoff calls, is it tested, is the README clear.
3. **Analysis + presentation** (Cohere) → a *narrative*: framing, method, findings, and a crisp write-up/deck. Graded on **communication and reasoning** as much as the analysis. This is the one your coding-heavy prep does *not* cover — practice it.

### Reusable take-home playbook (build the scaffold once, in the Week 8 dry-run)
- [ ] **Re-read the prompt twice; restate the goal + success criteria in one sentence** before coding. Email a clarifying question if scope is ambiguous — asking is a positive signal.
- [ ] **Time-box and scope ruthlessly.** Pick the 80% that demonstrates competence; explicitly list what you cut and why ("Given the window, I prioritized X; with more time I'd add Y"). Scope judgment is exactly the staff signal they're testing.
- [ ] **Reusable repo scaffold:** clean structure, `README` (how to run, decisions, tradeoffs, what you'd do next), dependency/env file, a few **tests**, sample input/output. Have this skeleton ready so the real one is execution.
- [ ] **Make it run from a clean clone** with one command. A broken setup sinks an otherwise-good submission.
- [ ] **Write the README like a staff engineer:** problem framing → approach → key decisions & tradeoffs → results → limitations → next steps. This is where you show seniority.
- [ ] **Don't gold-plate.** Polish what matters (correctness, clarity, the core demo); skip irrelevant flourishes.
- [ ] **AI-usage:** know the company's policy. Anthropic publishes explicit guidance (see [[anthropic-interview-guide]]); when allowed, using AI well *and disclosing how* is fine and often expected for AI-eng roles. Never pass off un-understood code — they'll probe it live.
- [ ] **Expect a follow-up defense.** Many take-homes feed a live round where you walk through and extend your code. Build only what you can explain and modify on the spot.

### Cohere-specific (the analysis + presentation one — your highest-leverage take-home)
- Deliver a **clear narrative**, not a notebook dump: question → data/method → findings → recommendation → caveats.
- Lead with the **answer/insight**, then support it. Make 2–3 clean visuals; cut the rest.
- Tie it to **enterprise/product reality** (cost, latency, data residency, deployment) — Cohere's whole positioning.
- Practice the **verbal walkthrough** to time; they assess how you communicate, not just what you found.

---

## 8. Company cheat sheets — all 12

Loop shapes from 2025–2026 reports (see Sources §9). For each: **shape**, **distinctive surface**, **if-you-only-do-one-thing**, and a **hook**.

### Frontier labs

**Anthropic** — *Full guide: [[anthropic-interview-guide]]*
- Shape: recruiter → practical coding → take-home/4-level coding → HM deep-dive → onsite (ML/applied design + coding + **values**).
- Distinctive: **B (practical coding)** + **values round** (top failure point).
- One thing: drill the coding bank (#636, #609, #1242, in-memory DB) **and** rehearse the values round out loud with a real AI-safety POV.
- Hook: pick a specific Claude/Constitutional-AI/RSP angle you genuinely care about.

**OpenAI** — *Full guide: [[openai-interview-guide]]*
- Shape: recruiter → technical screen (CoderPad) → work-trial/take-home → onsite (coding, ML design, research depth, behavioral) → mission/values.
- Distinctive: **B (8-problem bank)** + **D (ML design)** + intensity signal.
- One thing: work all 8 problems in the OpenAI guide; have D2/D4 (inference, training) crisp.
- Hook: a real reason the mission matters to you; show agency/bias-to-build.

**Cohere** — *Full guide: [[cohere-interview-guide]]*
- Shape: recruiter → **48-hr take-home** (analysis + presentation, ~30% pass) → 2–3 technical (LLM concepts, coding, design) → HM fit.
- Distinctive: take-home quality + enterprise/sovereign-AI design.
- One thing: nail the take-home (clear write-up + presentation); prep D1 (RAG) and D8 (embedding pipeline) with cost/enterprise framing.
- Hook: enterprise/multilingual deployment, data residency, cost-per-token.

**Anysphere (Cursor)** — *see [[ai-ipo-interview-guide]]*
- Shape: recruiter → take-home/CodeSignal → onsite (system design + live coding) → founder/culture.
- Distinctive: **B + D3 (agent loop)** + code-completion latency.
- One thing: design the autonomous coding-agent loop (run tests, fix, open PR) + sub-100ms completion serving; be fast and clean in live coding.
- Hook: codebase-understanding at 100k+ files; you're a power user with opinions.

**Harvey** — *see [[ai-ipo-interview-guide]]; Toronto office (Oct 2025)*
- Shape: recruiter → take-home/coding → onsite (LLM system design + domain) → mission/product.
- Distinctive: **D (high-stakes RAG/citations)** — auditable, low false-positive.
- One thing: D1 RAG but framed for legal — every conclusion traceable to a source, hallucination = liability.
- Hook: vertical AI for a regulated domain; precision + auditability over flash.

### Big Tech / AV

**Google** — *L6 = Staff*
- Shape: **Google Hiring Assessment** → recruiter → 1–2 phone screens → onsite: **1–2 coding + 2–3 system design + Googliness/GCA**. ~60 days avg for staff.
- Distinctive: **A + C** at depth; staff differentiator = architectural leadership + org influence.
- One thing: 2 strong system-design rounds + crisp Googliness stories; coding is assumed, don't fumble it.
- Hook: Gemini/Applied AI or Cloud AI team-specific interest.

**NVIDIA**
- Shape: 1–2 phone screens → onsite 4–6 rounds (≥1 system design, 2–3 coding, 1–2 behavioral). Python/C++; C++ for perf roles.
- Distinctive: **A + D2/D4** (GPU/inference/training infra) + performance reasoning.
- One thing: distributed training across multi-GPU/nodes (D4) and inference serving (D2); know GPU/parallelism tradeoffs cold.
- Hook: performance obsession; CUDA/TensorRT/inference stack.

**Waymo** — *Toronto = mainly infra*
- Shape: 5–6 rounds: coding (DSA, **geometry/graph/linear-algebra flavor**), **ML coding** (NumPy), **ML system design** (discussion), 2× behavioral. C++ or Python; they probe memory/threading.
- Distinctive: **A (graphs/geometry) + ML coding + AV-infra design** (petabyte logs, disengagement metrics, Lidar indexing).
- One thing: graph/geometry mediums + the AV-flavored data-infra design (§5 metrics/log prompts).
- Hook: safety-critical verification mindset.

**Robinhood** — *agentic AI + dev-productivity AI teams*
- Shape: **CodeSignal OA (90 min, ~4 tasks)** → recruiter → technical screen (DSA + sometimes concurrency) → onsite (coding, system design, behavioral).
- Distinctive: **A + C (reliability/ledger)**; for AI teams add **D3 (agents)**.
- One thing: timed CodeSignal reps (Week 9 mixed set) + payment/ledger idempotency design + agent loop if AI team.
- Hook: agentic systems for finance; reliability and user trust.

**Lyft**
- Shape: recruiter → phone screen (CoderPad, 1–2 mediums) → onsite: **system design (1h) + coding (1h)** + behavioral; values = ownership/safety/judgment.
- Distinctive: **A (graphs, intervals, geospatial)** + dispatch/matching design.
- One thing: graph/geospatial mediums + ride-matching design (§5).
- Hook: Applied AI / developer-productivity AI team specifically.

### Toronto product / AV

**Waabi** — *Toronto HQ, Raquel Urtasun*
- Shape: recruiter → technical (coding + role-specific) → onsite (coding, ML/AV system design, behavioral). AV-first, simulation-heavy.
- Distinctive: **A + AV simulation/scenario design (D8)**; strong fundamentals in C++/Python.
- One thing: simulation/scenario-generation design + solid graph/geometry coding.
- Hook: AI-first autonomy, simulation as the path to safety.

**Wealthsimple** — *Toronto HQ*
- Shape: recruiter → **pair-programming** (e.g. Mars Rover state/coords) → **"Bring your own system"** + possibly component/system design → behavioral w/ manager. ~2–4 weeks.
- Distinctive: pragmatic coding + **explain a real system you built** clearly.
- One thing: prep a clean "bring your own system" walkthrough (your strongest infra project, explainable to juniors) + practice pair-programming aloud.
- Hook: democratizing finance; AI platform build-out.

---

## 9. Resources & sources

### Your existing guides (start here — don't re-research)
- `anthropic-interview-guide.md` · `openai-interview-guide.md` · `cohere-interview-guide.md` · `ai-ipo-interview-guide.md` · `ai-companies-toronto-research-2026-06-16.md`

### Coding (Tracks A & B)
- **NeetCode 150 / Roadmap** — https://neetcode.io/practice
- **LeetCode** (problems by number above) — https://leetcode.com/
- **CodeSignal** practice (Robinhood/xAI/Anysphere OA format) — https://codesignal.com/
- **Pramp / interviewing.io** (mock coding) — https://www.pramp.com/ · https://interviewing.io/

### System design (Tracks C & D)
- **Hello Interview** (modern SD framework + company guides) — https://www.hellointerview.com/
- **Google L6 guide** — https://www.hellointerview.com/guides/google/l6
- **System Design Primer** (GitHub) — https://github.com/donnemartin/system-design-primer
- **NVIDIA system design questions** — https://www.codinginterview.com/guide/nvidia-system-design-interview-questions/

### ML / LLM fundamentals (Track E)
- **Karpathy — Neural Nets: Zero to Hero** (esp. "Let's build GPT") — https://karpathy.ai/zero-to-hero.html
- **Jay Alammar — Illustrated Transformer** — https://jalammar.github.io/illustrated-transformer/
- **Lilian Weng's blog** (agents, RLHF, prompting) — https://lilianweng.github.io/
- **HuggingFace LLM Course** — https://huggingface.co/learn
- **vLLM / PagedAttention paper** — https://arxiv.org/abs/2309.06180
- **LLM interview Q banks** — https://github.com/Devinterview-io/llms-interview-questions · https://www.datacamp.com/blog/rag-interview-questions

### Company interview-process research (pulled 2026-06-16)
- Google SWE/Staff — https://www.hellointerview.com/guides/google/l6 · https://igotanoffer.com/blogs/tech/google-software-engineer-interview · https://www.tryexponent.com/guides/google-swe-interview
- NVIDIA — https://igotanoffer.com/en/advice/nvidia-software-engineer-interview · https://www.interviewquery.com/interview-guides/nvidia-machine-learning-engineer
- Waymo — https://www.interviewquery.com/interview-guides/waymo-software-engineer · https://www.interviewquery.com/interview-guides/waymo-machine-learning-engineer
- Robinhood — https://www.techprep.app/blog/robinhood-interview-process · https://www.interviewquery.com/interview-guides/robinhood-software-engineer · https://www.1point3acres.com/interview/company/robinhood
- Lyft — https://www.tryexponent.com/guides/lyft-swe-interview · https://prepfully.com/interview-guides/lyft-software-engineer
- Wealthsimple — https://www.glassdoor.com/Interview/Wealthsimple-Software-Engineer-Interview-Questions-EI_IE908271.0,12_KO13,30.htm · https://tech-wisdom.medium.com/wealthsimple-interview-experience-8ef4104686b1
- Waabi — https://waabi.ai/careers · https://jobs.lever.co/waabi
- **1point3acres interview library** (highest-signal candidate reports) — https://www.1point3acres.com/interview/

### Mocks & comp
- **Levels.fyi** (comp benchmarks) — https://www.levels.fyi/
- **Glassdoor interview reviews** — https://www.glassdoor.com/

---

## 10. Weekly operating cadence
- **Apply** to 3+ roles/week (per README checklist); keep the funnel full while prepping.
- **Track** every application, round, and debrief in one place.
- **Mock** every 1–2 weeks from Week 6; always write a debrief.
- **Protect E + F** when time slips — they're your gap and your cheapest points.
- **One language, one resource per topic.** Depth over tab-hoarding.

*Plan created 2026-06-16. Calibrated to: 10-week horizon, <10 hrs/week, backend/infra-strong closing ML gap, Staff level. Re-skin per company in Weeks 9–10.*
