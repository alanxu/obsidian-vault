---
tags: [job-hunt, interview-prep, ai-companies, research, 2026]
created: 2026-06-16
updated: 2026-06-16
status: snapshot
data-freshness: 2026-06-16 — loops change; verify with recruiter
parent: [[interview-prep-master-plan-2026]]
companies: [Cognition (Devin), Glean, Notion, Whatnot, Fireworks AI, Together AI]
---

# Additional Target Companies — Interview Process & Concrete Questions

> Process + **actual reported questions** for six more targets, grouped by archetype. Pairs with [[interview-prep-master-plan-2026]] (map each company to the 6 prep surfaces) and [[ai-companies-toronto-research-2026-06-16]] (comp/valuation/Toronto status).
>
> **Reliability note:** loops below are synthesized from 2025–2026 candidate reports (1point3acres, Glassdoor, Taro, Exponent, techinterview.org). Smaller/newer companies (esp. **Cognition**) keep loops private and change them fast — treat as directional and confirm specifics with your recruiter. Difficulty ratings are /10.

---

## At-a-glance

| Company | What they do | Toronto? | Loop length | Distinctive surface | Difficulty |
|---|---|---|---|---|---|
| **Cognition (Devin)** | Autonomous coding agent | No (SF) | ~4–5 rounds, fast | Practical coding + customer roleplay + agents | 8/10 |
| **Glean** | Enterprise AI search/assistant | No (Palo Alto) | 3–6 rounds (~11 days) | Search/indexing system design + fast clean coding | 6–7/10 |
| **Notion** | Productivity / docs + Notion AI | No (SF) | Phone → tech screen → onsite | **Practical** coding (build a text editor), data modeling | 6–7/10 |
| **Whatnot** | Livestream shopping marketplace (ML-heavy) | No (SF) | 4 rounds + 1-way video | Coding + system design + **product sense** | 6–7/10 |
| **Fireworks AI** | Fast LLM inference API | No (Redwood City) | HM screen → loop | LeetCode-med + GPU/infra fundamentals | 7–8/10 |
| **Together AI** | Open-model inference + fine-tuning | No (SF) | Screen → (take-home) → 4–5 | **ML-systems/CUDA depth**, inference optimization | 8/10 |

**How these map to your prep surfaces:** Glean/Notion/Whatnot lean **A (coding) + C (distributed design)**, with Notion's design tilting to data modeling and Whatnot adding product sense. Fireworks/Together lean **A + D2 (inference serving)** + real **E (ML/LLM fundamentals)** — your D2 doc and inference-internals study are exactly on-target. Cognition leans practical coding + **D3 (agent loop)**.

---

## 1. Cognition (Devin) — autonomous AI software engineer

**Snapshot.** Maker of Devin, the autonomous coding agent; reportedly ~$25B valuation talks (Apr 2026); acquired Windsurf. SF, no Toronto. Loop is **rigorous, fast-moving, highly interactive**, weighted to real-world engineering over abstract puzzles. *(Data is sparse — this is the least-documented loop here.)*

**Process (reported / directional):**
1. Recruiter / hiring-manager screen — background, why Cognition, fit with fast pace.
2. Technical screen — foundational coding + systems knowledge (debugging enterprise environments).
3. Full loop — pair-programming coding + system/ML design, often with **customer-facing roleplay** (you act through a realistic scenario).
4. Behavioral / founder-culture conversation.

**Concrete questions & themes reported:**
- **Pair programming:** write clean, production-ready code while **narrating trade-offs, structure, and validation** (they grade your reasoning aloud, not just the answer).
- Foundational coding + systems knowledge for **debugging enterprise environments**.
- **ML classifier evaluation** — design a validation strategy for a model (e.g. clinical/enterprise context).
- **Design a batch ETL pipeline** that cleans datasets with data-quality checks and a daily SLA.
- Expected fluency: **Python, JavaScript/TypeScript, or Go**; distributed computing; **Docker/Kubernetes**.
- Marketing tell: Devin itself "passed practical engineering interviews from leading AI companies" — expect **practical, agent-flavored** engineering tasks, not Codeforces puzzles.

**How to prep:** rehearse think-aloud pair programming; have a crisp **agent-loop design** ready (planning → tool calls → run tests → self-correct → open PR — see [[interview-prep-master-plan-2026]] §6 D3); be a real Devin user and bring opinions; prep one ETL/data-quality story. Exponent lists ~9 verified Cognition questions — drill those.

**Sources:** [Dataford — Cognition AI Engineer guide](https://dataford.io/interview-guides/cognition/ai-engineer) · [Exponent — Cognition questions](https://www.tryexponent.com/questions?company=cognition-ai) · [Cognition careers (Ashby)](https://jobs.ashbyhq.com/cognition) · [Cognition — Devin 2025 review](https://cognition.ai/blog/devin-annual-performance-review-2025)

---

## 2. Glean — enterprise AI search & assistant

**Snapshot.** Enterprise search + assistant over Slack/Drive/Jira/Salesforce; ~$7B+. Palo Alto, no Toronto. Values **practical engineering speed + startup adaptability** — clean, bug-free code, fast, with edge cases handled in real time. Fast loop (~11 days avg).

**Process (reported):**
- Some candidates: **3 rounds** — 2 coding + a tech-lead discussion.
- Others: up to **6 rounds** — hiring manager, multiple technical, system design, cultural.

**Concrete coding questions reported:**
- "**Implement a graph DFS** to solve a connectivity problem." (part-by-part, each part harder)
- "**Write a program to play Connect 4**, including the logic to detect a winner."
- Medium → slightly-hard, **progressive multi-part** format (assesses several problem-solving methods on one base problem — same shape as the lab "OO bank," see [[interview-prep-master-plan-2026]] §3).

**Concrete system-design questions reported (their core domain):**
- "**Design a search engine for internal company documents** — handle indexing, ranking, and query optimization."
- "**Build a real-time indexing system** that ensures low latency while maintaining consistency and reliability."
- Expect permission-aware search (ACLs across connected apps), freshness, and relevance ranking — overlaps heavily with your **D1 RAG** doc (retrieval, ranking, ACL filtering).

**How to prep:** drill graph/DFS + a multi-part design-style coding problem under time; rehearse the **enterprise search / real-time indexing** design (lean on [[D1-rag-with-citations]] for retrieval + ACL framing); optimize for speed and clean edge-case handling.

**Sources:** [Glean SWE interview guide (NoraHQ)](https://interview.norahq.com/interview-guides/glean-software-engineer-interview-guide-2026) · [Dataford — Glean SWE](https://dataford.io/interview-guides/glean-(ca)/software-engineer) · [Glassdoor — Glean SWE](https://www.glassdoor.com/Interview/Glean-CA-Software-Engineer-Interview-Questions-EI_IE5795738.0,8_KO9,26.htm) · [1point3acres — Glean](https://www.1point3acres.com/interview/company/glean)

---

## 3. Notion — productivity / docs + Notion AI

**Snapshot.** Collaborative docs/workspace + Notion AI. SF, no Toronto office (per [[ai-companies-toronto-research-2026-06-16]]). Interviews are **practical, real-world**, not LeetCode-style. ~19-day process, 2–3 business days between rounds.

**Process (reported):**
1. Recruiter phone screen.
2. **Technical screen (CoderPad):** implement a basic **text editor** by completing several pre-stubbed functions — very practical, not algorithm-puzzle.
3. **Onsite (several rounds):** technical/coding (incl. an **AI-enabled round** — a normal coding round where you use an LLM), **system design**, and **values/behavioral**.

**Concrete questions & themes reported:**
- **Coding:** "Implement the functionality of a **basic text editor**" (complete stubbed functions). Practical, stateful-object flavor.
- **System design (data-modeling heavy):** deep-dive **database schema + indexes**, API design, and **efficient SQL queries**.
- **System design (scale):** "**Design collaborative tools at Notion scale**" / "how would you improve Notion's infrastructure?" (think collaborative editing, sync, real-time).
- **AI-enabled round:** a regular coding round **using an LLM** — they want to see how you actually work with AI tooling.
- **Values:** practical, collaboration-oriented; why Notion, real past work.

**How to prep:** practice building a small **stateful object / editor** cleanly (relates to your OO bank — [[interview-prep-master-plan-2026]] §3); brush up **data modeling, indexes, SQL**; have a **collaborative-editing / real-time sync** design ready (CRDTs/OT at a high level); be comfortable coding *with* an AI assistant out loud.

**Sources:** [InterviewQuery — Notion Labs SWE](https://www.interviewquery.com/interview-guides/notion-labs-software-engineer) · [Glassdoor — Notion Labs SWE](https://www.glassdoor.com/Interview/Notion-Labs-Software-Engineer-Interview-Questions-EI_IE3304926.0,11_KO12,29.htm) · [linkjob — passing Notion SWE 2026](https://www.linkjob.ai/interview-questions/notion-software-engineer-interview-questions/) · [1point3acres — Notion](https://www.1point3acres.com/interview/company/notion)

---

## 4. Whatnot — livestream shopping marketplace (ML-driven)

**Snapshot.** Livestream commerce marketplace, ~$11.5B (2025); ML-heavy (rec/ranking, buyer growth, trust). SF, no Toronto; some Remote-CA possible. Loop assesses technical + problem-solving + **product sense / culture fit**.

**Process (reported):**
0. **One-way video screen (~15 min):** ~6 questions, ~20–25 s prep each. (Async; do not skip prep.)
1. Recruiter phone screen — background, why Whatnot.
2. **Technical screen** — algorithmic problem-solving + data structures.
3. **Coding round.**
4. **System design round.**
5. **Product sense / behavioral round.**

**Concrete questions & themes reported:**
- **Coding:** algorithmic / DSA (medium); standard arrays/strings/graphs/DP-style.
- **System design:** marketplace/real-time-commerce flavored (e.g. live auction/bidding, feed ranking, notifications at scale) — bring scalability, consistency, low latency.
- **Product sense (distinctive):** "**Why does Whatnot interest you?**", reasoning about features/marketplace tradeoffs, past experience and exceptions handled. They want product judgment, not just code.
- ML roles (Buyer Growth / rec): expect ranking/recommendation discussion (BM25 + embeddings, feature pipelines) — overlaps [[interview-prep-master-plan-2026]] §6 D6/D7.

**How to prep:** treat coding as standard NeetCode-medium; prep a **real-time marketplace / live-auction** system design; **rehearse the one-way video** (record yourself answering "why Whatnot" + behavioral in <90 s); have a crisp product opinion about the app.

**Sources:** [Glassdoor — Whatnot SWE](https://www.glassdoor.com/Interview/Whatnot-Software-Engineer-Interview-Questions-EI_IE5065998.0,7_KO8,25.htm) · [Taro — Whatnot SWE experience (2025)](https://www.jointaro.com/interviews/companies/whatnot/experiences/software-engineer-united-states-july-1-2025-accepted-offer-positive-119ad58e/) · [Glich — Whatnot L4](https://hw.glich.co/resources/companies/whatnot/interview-process/l4-software-engineer) · [1point3acres — Whatnot](https://www.1point3acres.com/interview/company/whatnot)

---

## 5. Fireworks AI — fast LLM inference API

**Snapshot.** Fast LLM inference / serving API. Redwood City, no Toronto. **Extremely selective** — fails the majority of engineers. Loop blends LeetCode-medium with **GPU/infra fundamentals** tied to the actual work.

**Process (reported):**
1. **Initial screening call with the hiring manager.**
2. **Full team loop** — LeetCode-medium coding + systems-level discussions. Round timing reported as tight (~30 min coding / ~10 min technical Q&A / ~5 min your questions in some panels).

**Concrete questions & themes reported:**
- **Coding:** LeetCode easy-to-medium, including **graph problems** — e.g. "**check if a given undirected graph is a single chain**." Python (or C++).
- **Fundamentals / systems:** **GPUs**, **inter-GPU communication**, **CI/CD**, **Kubernetes**, **NVIDIA device plugins for Kubernetes** — i.e. how you'd actually run inference at scale.
- Panel format: LeetCode-style + system design relevant to inference serving.

**How to prep:** solid graph/array mediums (fast and clean); be able to talk **GPU scheduling on K8s, inter-GPU comms (NCCL), continuous batching, KV cache** — your [[interview-prep-master-plan-2026]] §4 Block 3 (inference internals) + the **D2 inference-serving** design. Be a Fireworks API user; know where they win on latency/cost.

**Sources:** [Glassdoor — Fireworks AI SWE](https://www.glassdoor.ca/Interview/Fireworks-AI-Software-Engineer-Interview-Questions-EI_IE9514416.0,12_KO13,30.htm) · [Taro — Fireworks SWE experience (2025)](https://www.jointaro.com/interviews/companies/fireworksai/experiences/software-engineer-united-states-july-14-2025-no-offer-negative-4ca1699f/) · [1point3acres — Fireworks AI](https://www.1point3acres.com/interview/company/fireworks%20ai) · [Prachub — Fireworks AI SWE](https://prachub.com/companies/fireworks-ai/positions/software-engineer)

---

## 6. Together AI — open-model inference + fine-tuning

**Snapshot.** Cloud platform for open/custom models — fast inference (Llama, Mixtral, DeepSeek, Qwen), fine-tuning, enterprise deployment. SF, ~200 people, **academic-adjacent** culture (co-founder Ce Zhang). No Toronto. **Difficulty 8/10**; inference-engine/research roles approach frontier-lab rigor. Best-documented loop here.

**Process (reported):**
1. **Recruiter screen (30 min)** — background, why Together, team triage (inference-engine vs platform vs training vs research vs enterprise — depths differ a lot).
2. **Technical phone screen (60 min)** — one medium-hard coding problem; Python / C++ / CUDA by role; ML-systems-applied (implement an attention primitive, streaming generation, efficient batching).
3. **Take-home (many senior/research roles)** — 4–8 hrs; inference-engine → implement/optimize a CUDA kernel; platform → a focused systems problem.
4. **Onsite / virtual (4–5 rounds):** 2 coding (1 algorithms, 1 applied ML-systems), 1 system design, 1–2 ML/research (research-eng roles), 1 behavioral/HM.
- Infra/SRE variant: 1 code screen + 4 loop rounds (infra, troubleshooting, HM, system design) + 1 VP round.

**Concrete coding questions reported:**
- **Implement attention from scratch** with batching considerations.
- **Write a CUDA kernel** for a given op (element-wise, reduction, softmax).
- **Design a batching scheduler** matching incoming requests to GPU capacity with fairness.
- **Streaming token generation with cancellation handling.**
- Classic graphs/DP/priority-queue problems with ML-systems twists (difficulty comparable to NVIDIA core GPU / mid-frontier-lab inference teams).

**Concrete system-design questions reported:**
- "**Design the inference-serving system supporting 100+ open-source models with shared/efficient GPU sharing.**"
- "**Design the fine-tuning service with multi-tenant LoRA adapter management** and per-customer isolation."
- "**Design the speculative-decoding pipeline working across diverse model architectures.**"
- "**Design the custom-deployment offering for enterprise customers with dedicated capacity.**"
- *What scores:* specific numbers (H100/Blackwell memory, KV-cache footprint per model, latency budgets), engaging real research (vLLM PagedAttention, FlashAttention variants), enterprise realities. *What fails:* generic "design a serverless platform" with no AI-specific constraints.

**Concrete ML/research-round topics:**
- Walk through a Together AI paper (serving/training) you know.
- Trade-offs between **speculative-decoding** approaches.
- **Quantization** schemes: INT8 vs FP8 vs mixed precision.
- Design an experiment to evaluate a new inference-optimization technique.

**Concrete behavioral prompts:**
- "Tell me about the **fastest meaningful improvement** you shipped to a production AI system."
- "How do you **balance research-informed work with shipping** production systems?"
- "Describe a **production ML system you owned end-to-end**."
- "Tell me about engaging with an **enterprise customer's AI-infra problem**."

**How to prep:** this is the most ML-systems-demanding loop on your list — exactly where your infra background + closed ML gap pays off.
- Coding: implement attention, softmax, a batching scheduler, streaming-with-cancellation; LeetCode med/hard. CUDA only if targeting inference-engine roles (then read *Programming Massively Parallel Processors*).
- Design: your **D2 inference-serving** doc + **D4 training/fine-tuning** — frame with real numbers and named research.
- Fundamentals: vLLM/PagedAttention, FlashAttention (1/2/3), speculative decoding (orig + Medusa/Lookahead), quantization — [[interview-prep-master-plan-2026]] §4 Block 3.
- Product: run real workloads on Together's API; form an opinion on open vs closed; read their blog/papers.

**Sources:** [techinterview.org — Together AI 2026 guide](https://www.techinterview.org/companies/together-ai/) · [Glassdoor — together.ai](https://www.glassdoor.com/Interview/together-ai-CA-Interview-Questions-E10746640.htm) · [1point3acres — Together AI](https://www.1point3acres.com/interview/company/together%20ai) · [Prachub — Together AI SWE](https://prachub.com/companies/together-ai/positions/software-engineer)

---

## Cross-company prep takeaways

1. **Two clusters.** App-layer (Cognition, Glean, Notion, Whatnot) reward **practical, fast, clean coding + product/system judgment** — not Codeforces. Infra-layer (Fireworks, Together) reward **ML-systems depth** (inference optimization, GPU, serving) — your D2/D4 + §4 Block 3.
2. **Practical coding shows up everywhere** (Notion text editor, Glean Connect-4/DFS, Cognition pair-programming). Your **OO/practical bank** ([[interview-prep-master-plan-2026]] §3) covers all of them — narrate trade-offs as you code.
3. **Be a user.** Fireworks/Together/Cognition/Notion all reward having run their product and formed real opinions. Cheap, high-signal prep.
4. **Inference fundamentals are the unlock** for Fireworks + Together (and reinforce NVIDIA/OpenAI/Anthropic from your main list): KV cache, continuous batching, PagedAttention, FlashAttention, speculative decoding, quantization.
5. **Async/product rounds:** Whatnot's one-way video and Notion's AI-enabled round are easy to underestimate — rehearse both formats explicitly.

*Snapshot 2026-06-16. Verify each loop with your recruiter before interviewing. Companion to [[interview-prep-master-plan-2026]], [[D1-rag-with-citations]], and [[ai-companies-toronto-research-2026-06-16]].*
