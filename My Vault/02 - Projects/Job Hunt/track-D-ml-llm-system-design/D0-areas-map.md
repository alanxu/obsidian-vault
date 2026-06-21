---
tags: [job-hunt, interview-prep, ml-system-design, llm, track-D, areas-map, foundation, D0]
created: 2026-06-17
updated: 2026-06-17
status: active
parent: [[interview-prep-master-plan-2026]]
covers: [meta-framework, retrieval, inference-serving, agents, training, evaluation, data-feature-pipelines, safety-guardrails, observability-cost]
purpose: "Structural map of the 8 competency areas underlying every Track D prompt, at staff depth. The connective tissue above D1–D8."
---

# D0 — ML / LLM System Design: Areas Map & Staff Knowledge Framework

> **What this is.** D1–D8 are *prompts*. This is the *map underneath them*. Every ML/LLM design question an interviewer can throw at you is a specific instantiation drawn from a small, finite set of **competency areas**. Learn the eight areas at staff depth and you can derive any prompt — including ones not on your list. Read this first; treat D1–D8 as worked examples of areas defined here.
>
> **The one-line thesis to anchor on:** *Classic system design asks "will it work?" (a binary). ML/LLM system design asks "how good is it, how do you know, and how fast does it silently get worse?" — quality is statistical, regresses invisibly, and costs GPU-dollars. So **eval, cost, and the offline/online split are first-class citizens**, not afterthoughts.*

---

## 0. How to use this document

- **Study by area, not by prompt.** Each of the 8 areas below has the same template: *scope → mental model → building blocks → key decisions & tradeoffs → numbers to know → failure modes → senior-vs-staff → maps-to → follow-ups.* Master the template per area and the prompts answer themselves.
- **§1 is the universal talk-track.** It's the driving framework that works for *any* D prompt. Internalize it so you never freeze on a new question.
- **§3 (cross-cutting) is the staff checklist** you run through on *every* answer regardless of area — latency, cost, multi-tenancy, parity, versioning, failure modes.
- **§5 is the coverage matrix** — areas → D-prompts → companies → "the one thing to nail." Use it to route your prep time.
- The worked solutions deepen specific areas: [[D1-rag-with-citations]] is Area 1; D2 is Area 2; D3 is Area 3; D4 is Area 4; D5 is Area 5; D6/D7/D8 are Area 6.

---

## 1. The meta-framework — what makes ML/LLM design different, and how to drive any prompt

### 1.1 Why this isn't just "system design with a model in it"
You already own distributed-systems rigor (Track C). ML/LLM design adds **four layers** most infra candidates under-weight — and these layers are exactly where staff signal lives:

| Added layer                | The shift in thinking                                                                                                                                                                   | Where candidates lose points                                                |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **Data**                   | The system's behavior is *learned from data*, not just coded. Data quality, freshness, and leakage determine quality more than code.                                                    | Treating data as a static input instead of a versioned, monitored pipeline. |
| **Model**                  | The core component is **probabilistic and non-deterministic** — same input, different output; confidently wrong.                                                                        | Reasoning about the model as if it's a deterministic function.              |
| **Eval**                   | "Correct" is **statistical and contested**. You must *define* what good means and *measure* it offline + online, or you're flying blind.                                                | Designing the architecture before stating the success metric.               |
| **Online / Offline split** | Almost every ML system is **two loops**: an offline *build* loop (train / index / compute features) and an online *serve* loop. Keeping them consistent (parity) is a top failure mode. | Drawing one pipeline and forgetting the build loop, or skew between them.   |

Three consequences that show up in *every* answer:

1. **Quality regresses silently.** A model or index can degrade with no error, no exception, no alert — until users churn. → eval gates and drift monitoring are mandatory, not optional.
2. **Cost is dominated by GPUs/tokens, not CPU/storage.** The expensive thing is the model call (inference) or the GPU fleet (training), often by 10–100×. → cost engineering is a design axis, not a footnote.
3. **The expensive resource is scarce and bursty.** GPUs are limited, expensive, and contended. Batching, caching, quotas, and autoscaling decisions are first-order.

### 1.2 The universal driving framework (works for D1–D8 and beyond)
Spend your time in roughly this ratio — the ratio itself signals seniority:

1. **(3–4 min) Clarify & scope.** Functional + non-functional, *plus the ML-specific questions* below. Refuse to design before you know the constraints.
2. **(2 min) State the success metric FIRST.** *"Before I draw anything: what does 'good' mean here, and how do we measure it offline and online?"* This single move separates staff from senior — you treat eval as the spec, not a later section.
3. **(3 min) Draw the two/three planes.** Get the whole board up before going deep:
   - **Data/build plane** (offline): sources → process → train/index/compute → versioned artifacts.
   - **Serving plane** (online): request → retrieve/route → model → post-process → response.
   - **Quality plane** (cross-cutting): eval, monitoring, feedback, rollback.
4. **(15–20 min) Deep-dive the highest-leverage component.** Usually retrieval (D1), the model call + batching (D2), the agent loop (D3), or the parallelism strategy (D4). Spend your compute where the quality/cost ceiling is set.
5. **(5 min) Eval & quality.** Offline metrics + online metrics + regression gates on every change.
6. **(5 min) Scale, latency, cost, reliability, multi-tenancy.** Real numbers, not adjectives.
7. **(throughout) Name tradeoffs & failure modes.** Every component: *"I'd start with X because Y; it fails at Z; when we hit Z I'd move to W."*

### 1.3 The ML-specific clarifying questions (memorize — ask the 4–5 that matter)
- **Quality bar / cost of a wrong answer.** Low-stakes (chat) vs high-stakes (legal/medical/finance → must support **abstention** and verification)?
- **Latency SLA.** Interactive (p95 < 2–3 s, stream first token < ~700 ms) vs async/batch (seconds–minutes OK)? Hugely changes the architecture.
- **Scale, two numbers.** QPS now + in 1 year; *and* corpus/model/data size (10K docs vs 1B; 7B vs 400B params). Drives index choice, parallelism, sharding.
- **Freshness.** Does the data/model need to reflect changes in seconds, minutes, hours, or is daily fine? Sets the offline-loop cadence.
- **Online vs batch.** Real-time inference vs offline scoring — different systems entirely.
- **Multi-tenancy & access control.** Per-user/per-tenant permissions? (Massive architectural impact — Glean/Harvey care a lot.)
- **Build vs buy.** Frontier API vs self-hosted open model? (Cost, latency, data residency, control — name the tradeoff.)

### 1.4 The staff lens (true across all areas)
A **senior** answer is *technically correct and complete*. A **staff** answer additionally:
- **Leads with the metric and the tradeoff**, not the components. States what "good" means and what it's trading away.
- **Names failure modes proactively** and designs the degraded-but-alive path for each.
- **Is cost- and latency-quantified.** Uses real numbers (KV-cache GB, recall@k, p99 ms, $/1M tokens), not "it scales."
- **Picks one thing to build first** and justifies the sequencing — judgment over breadth.
- **Treats eval, versioning, and rollback as architecture**, because quality regresses silently.
- **Thinks operationally and organizationally** — who's on call, how a bad model is rolled back in 5 minutes, how two teams share the GPU fleet.

> Keep this lens in mind for every area below — the "Senior vs Staff" box in each section is the concrete application of it.

---

## 2. The eight core areas

> Each area uses the same template. The areas are ordered roughly by interview frequency for AI-eng / staff roles. Areas 1–5 have (or will have) full worked solutions; Areas 6–8 are higher-frequency-as-follow-ups and cross-cutting.

### Area 1 — Retrieval & Knowledge Systems  → *worked solution: [[D1-rag-with-citations]]*

**Scope.** Getting the *right* external knowledge into the model's context: RAG, embeddings, vector + lexical indexes, hybrid retrieval, re-ranking, context assembly, citations/grounding. The dominant pattern for "make the LLM answer over *our* data."

**Mental model.** *RAG is a retrieval problem wearing a generation hat. Most failures are retrieval failures; the LLM can't answer faithfully from a chunk that isn't in its context.* Retrieval is a **funnel**: cast a wide cheap net (hundreds of candidates) → narrow with mid-cost compute (re-rank) → spend the most expensive compute (LLM) only on survivors.

**Building blocks.** Parse/clean → **chunk** (structure-aware, ~300–500 tok, ~15% overlap, parent linkage) → enrich (metadata, ACL, offsets) → **embed** (bi-encoder) → **index** (HNSW / IVF-PQ vector + BM25 lexical + doc store) ‖ **query** (rewrite, ACL pre-filter) → **hybrid retrieve** (dense + sparse) → **fuse** (RRF, k=60) → **cross-encoder re-rank** → **context assembly** (budget, order, dedup, citation handles) → **grounded generation** → **citation verification** (NLI / LLM-judge entailment).

**Key decisions & tradeoffs.**

| Decision | Options | The tradeoff |
|---|---|---|
| Chunking | fixed / structure-aware / semantic / small-to-big | precision (small) vs context (large); structure-aware is best ROI |
| Retrieval | dense / sparse / **hybrid** | dense=paraphrase, sparse=exact tokens/IDs; hybrid+RRF is the prod default |
| Index | HNSW / IVF-PQ | recall+latency (HNSW) vs memory at billion-scale (IVF-PQ) |
| Re-rank | none / cross-encoder | +precision, +50–200 ms; run on top-50–100 only |
| Citation strictness | link / span-level / verified | latency+cost of a verification pass vs auditability (Harvey/legal) |

**Numbers to know.** 10M docs × 8 chunks ≈ 80M chunks; 1024-dim fp32 ≈ 4 KB/vec → ~320 GB raw → quantize to ~80 GB. Retrieve 50+50 → RRF → 100 → rerank → top 3–8. HNSW M=16–64. Recall@k is the #1 RAG metric. p95 < 2–3 s, LLM dominates latency.

**Failure modes.** Retrieval miss (right chunk absent → model fabricates) · stale/conflicting sources · lost-in-the-middle · ACL leak (retrieving forbidden docs) · embedding-version skew between query and corpus.

> **Senior vs Staff.** Senior builds the pipeline. Staff (a) spends 80% of the time on retrieval not the LLM, (b) makes citation *verification* an explicit tunable policy by stakes, (c) enforces ACL *inside* the query not as a post-filter, and (d) gates every pipeline change on Recall@k offline + faithfulness online.

**Maps to.** D1, D8 (embedding pipeline). **Companies:** Perplexity, Cohere, Harvey, Glean, Anthropic, OpenAI.

**Top follow-ups.** "Dense or sparse?" → both, hybrid+RRF. "Stop hallucinations?" → fix retrieval first, then ground+abstain, then verify. "1B chunks?" → IVF-PQ, shard, quantize. (Full bank in [[D1-rag-with-citations]] §13.)

---

### Area 2 — Inference & Serving  → *worked solution: D2 (to write)*

**Scope.** Serving LLM tokens at scale under a latency SLA and a cost budget: KV cache, batching, attention memory, decoding throughput, autoscaling, multi-tenant quotas, p99. The "make the model call fast and cheap at QPS" area — where your infra strength most directly transfers.

**Mental model.** *LLM inference is two different workloads glued together.* **Prefill** (process the prompt) is **compute-bound** — one big parallel forward pass, FLOPS-limited. **Decode** (generate tokens one at a time) is **memory-bandwidth-bound** — each token reloads the growing KV cache. Optimizing one often hurts the other, which is *why* modern stacks separate them.

**Building blocks.**
- **KV cache** — cache attention keys/values for past tokens so decode is O(1) per token, not O(n). It's the memory hog: size = `2 × layers × kv_heads × head_dim × seq_len × batch × bytes`. GQA/MQA shrink it by sharing kv_heads.
- **Continuous (in-flight) batching** — dynamically add/evict requests from the running batch per-step instead of waiting for a fixed batch; the single biggest throughput win for mixed-length traffic.
- **PagedAttention (vLLM)** — page the KV cache like virtual memory to kill fragmentation and enable sharing/prefix reuse. Near-zero waste vs naïve contiguous allocation.
- **Prefix caching** — reuse the KV of a shared prefix (system prompt, few-shot, chat history) across requests; massive win for agents/chat with repeated context.
- **Chunked prefill** — split a long prefill into chunks interleaved with decode steps so one long prompt doesn't stall everyone (head-of-line blocking).
- **Prefill/decode disaggregation** *(2026 standard at scale)* — run prefill and decode on *separate* GPU pools (different parallelism, different scaling), streaming the KV cache between them over fast interconnect. Decouples the two workloads so each scales to its own bottleneck. Orchestrated by e.g. NVIDIA **Dynamo** over vLLM/SGLang/TensorRT-LLM. *Caveat: only wins at sufficient scale/long prompts; for short prompts, local prefill is simpler and faster.*
- **Speculative decoding** — a small draft model proposes k tokens, the big model verifies them in one pass; 2–3× decode speedup when acceptance is high. Variants: draft model, **Medusa** (extra heads), **EAGLE** (feature-level).
- **Quantization** — int8/int4 (GPTQ/AWQ) shrinks weights+KV → more batch, less memory, slight quality cost.
- **FlashAttention** — IO-aware attention kernel; compute the same math with far less HBM traffic.

**Key decisions & tradeoffs.**

| Decision | The tradeoff (the staff framing) |
|---|---|
| Batch size | ↑ throughput vs ↑ per-request latency (TTFT/TPOT). Continuous batching gets both, to a point. |
| Disaggregate prefill/decode? | scales each workload independently vs KV-transfer overhead + orchestration complexity; only at scale. |
| Speculative decoding | latency win vs draft-model cost + complexity; depends on acceptance rate for your traffic. |
| Quantization level | memory/cost/throughput vs quality drop; measure on *your* eval, not a leaderboard. |
| Shared vs per-tenant fleet | utilization (shared) vs isolation/noisy-neighbor + SLA guarantees (per-tenant). |
| Self-host vs API | control/cost-at-scale/data-residency vs zero-ops + frontier quality. |

**Numbers to know.** TTFT (time-to-first-token, what users *feel*) vs TPOT (time-per-output-token, sets tokens/sec) — report both + p50/p99, never just average. A 70B model in fp16 ≈ 140 GB weights → needs ≥2× 80 GB GPUs *before* KV cache. KV cache can be tens of GB at long context × batch. Decode is memory-bound → throughput scales with HBM bandwidth and batch size.

**Failure modes.** KV-cache OOM under long-context burst (need admission control/preemption) · head-of-line blocking from one huge prompt (→ chunked prefill) · noisy neighbor starving a tenant (→ quotas/fair scheduling) · cold-start latency on autoscale (GPUs are slow to spin up → keep warm pool) · cache stampede on a popular prefix.

> **Senior vs Staff.** Senior names KV cache + batching. Staff (a) opens with *"prefill is compute-bound, decode is memory-bound"* and designs around it, (b) gives a real latency budget (TTFT vs TPOT, p99), (c) reasons about **GPU economics** (utilization × $/GPU-hr) and multi-tenant fairness, and (d) knows *when not to* disaggregate / speculate (small scale → added complexity loses).

**Maps to.** D2. **Companies:** NVIDIA, OpenAI, Anthropic, Anysphere (sub-100 ms completion), Fireworks, Together, Baseten.

**Top follow-ups.** "Improve throughput?" → continuous batching + paged attention + quantize + bigger batch to the latency limit. "Cut p99 tail?" → chunked prefill, admission control, separate latency-class queues, prefix caching. "Sub-100 ms code completion?" → small/distilled model, aggressive prefix cache on the open file, speculative decoding, keep it on-GPU-resident. "Multi-tenant?" → per-tenant token quotas + fair scheduler + optional dedicated pools for premium SLAs.

---

### Area 3 — Agentic Systems  → *worked solution: D3 (to write)*

**Scope.** Systems where the LLM *acts* in a loop — plans, calls tools, observes results, and iterates — rather than answering once. Tool/function calling, the agent loop, memory, multi-agent orchestration, sandboxing, error recovery, eval, and cost control. The highest-growth area and the one most tied to "Agentic AI" staff roles.

**Mental model.** *An agent is a control loop around a stochastic policy (the LLM): `observe → think → act (tool) → observe …` until a goal or budget is hit.* The LLM is the planner; the system around it provides tools, memory, guardrails, and the stopping condition. **Reliability is the hard part, not capability** — a 95%-reliable step compounds to ~60% over 10 steps.

**Building blocks.**
- **The loop** — ReAct (reason+act), or plan-then-execute, or planner/critic (one proposes, one evaluates). Each turn: build context → LLM decides (answer or call tool) → execute tool → append observation → repeat.
- **Tools / function calling** — typed tool schemas the model can invoke. **MCP (Model Context Protocol)** — Anthropic's open standard (Nov 2024, since adopted by OpenAI & Google) for connecting models to tools/data through a uniform interface; the emerging default so you don't hand-roll every integration.
- **Memory** — short-term (the running context/scratchpad), long-term (vector store or DB of past facts/episodes), and *working* memory (summarized state to fit the window). Memory management = context-window engineering.
- **Orchestration patterns** — prompt **chaining** (pipeline), **routing** (classify → specialist), **parallelization** (fan-out/fan-in), **orchestrator–worker** (a lead agent decomposes and delegates to sub-agents), **planner–critic** (iterate to refine). **A2A (Agent2Agent)** is the emerging protocol for cross-agent communication (vs MCP which is agent→tools).
- **Sandboxing** — tools that run code / touch the world execute in an isolated, permissioned sandbox (containers, network egress rules, filesystem jails). Non-negotiable for code-exec or autonomous agents.
- **Error recovery** — retries with backoff, reflection ("that failed, try differently"), fallbacks, and a hard **budget/step cap** so a stuck agent can't loop forever or burn unbounded tokens.
- **Eval & observability** — trajectory eval (did each step make progress?) + end-to-end task success; full trace logging of every thought/tool-call/observation.

**Key decisions & tradeoffs.**

| Decision | The tradeoff |
|---|---|
| Single agent vs multi-agent | simplicity + shared context (single) vs specialization + parallelism + coordination cost & error propagation (multi) |
| Autonomy level | capability/automation vs control, safety, predictability; more autonomy = more guardrails needed |
| Planning style | ReAct (flexible, can wander) vs plan-then-execute (predictable, brittle to surprises) |
| Memory strategy | recall quality vs context cost; summarize/compress vs raw history |
| Tool granularity | few coarse tools (less model confusion) vs many fine tools (flexibility, but harder selection) |
| Stopping policy | task completion vs cost/step budget — must bound both |

**Numbers to know.** Step reliability compounds: 0.95^10 ≈ 0.60 — so per-step verification matters more than raw model IQ. Cost = Σ tokens over all turns; a 10-step agent with growing context can cost 10–50× a single call → prefix caching + context compression are essential. Latency stacks per turn → parallelize independent tool calls.

**Failure modes.** Compounding errors over long horizons · context-window overflow / "lost in the middle" as history grows · infinite loops / no progress (→ step cap + loop detection) · tool-call hallucination (wrong args, nonexistent tool) · **prompt injection via tool outputs** (a retrieved web page tells the agent to exfiltrate data — a top security risk; see Area 7) · runaway cost · non-determinism making bugs unreproducible.

> **Senior vs Staff.** Senior wires up a ReAct loop with tools. Staff (a) frames the problem as *reliability engineering on a stochastic policy* (compounding error, verification per step), (b) bounds cost and steps explicitly and designs the degraded path, (c) treats tool outputs as **untrusted input** (injection, sandboxing), and (d) builds **trajectory eval + replay from traces** because non-determinism makes everything else undebuggable.

**Maps to.** D3. **Companies:** Robinhood (agentic AI), Anysphere/Cursor (coding agent), Harvey, Anthropic, Cognition, OpenAI.

**Top follow-ups.** "Stop infinite loops?" → step/budget cap + progress check + loop detection. "Multi-agent worth it?" → only when subtasks are genuinely parallel/specialized; default to single agent + tools. "Make it reliable?" → verify each step, constrain tools, retries+reflection, replayable traces, eval on real trajectories. "Coding agent (Cursor)?" → run tests as the verifier in the loop, sandbox exec, sub-100 ms completion served separately (Area 2).

---

### Area 4 — Training & Fine-tuning Infrastructure  → *worked solution: D4 (to write)*

**Scope.** Building/adapting the model: pretraining and fine-tuning at scale, the parallelism strategies, memory/throughput optimization, checkpointing, fault tolerance, and the data pipeline that feeds it. The area where your distributed-systems background is the *strongest* differentiator — most ML candidates can't reason about 1000-GPU fault tolerance; you can.

**Mental model.** *Training a large model is a tightly-coupled distributed system where the bottleneck is usually communication, not compute, and a single failure among thousands of GPUs stalls everyone.* The whole game is **fitting the model+optimizer+activations in memory** and **keeping GPUs busy** despite the communication and failures.

**Building blocks.**
- **The fine-tuning ladder** (know *when to use which* — it's a decision framework, not a list): prompt/few-shot → **RAG** (knowledge, no weight change) → **PEFT/LoRA/QLoRA** (cheap behavioral adaptation, small adapters) → **full SFT** (deep behavior change, expensive) → **RLHF/preference tuning** (align to human preference). Start at the cheapest rung that meets the bar.
- **RLHF pipeline** — SFT → train a **reward model** on human preference pairs → optimize the policy with **PPO**; **DPO** collapses RM+RL into one preference-optimization step (simpler, no separate RM, now common). Be able to draw it.
- **Parallelism (the core vocabulary — name what each splits):**
  - **Data parallel (DP)** — replicate model, split the batch; all-reduce gradients. Simple, communication-heavy at scale.
  - **Tensor parallel (TP)** — split individual matrix multiplies across GPUs; high comms, keep within a node (NVLink).
  - **Pipeline parallel (PP)** — split layers into stages across GPUs; micro-batches to fill the "bubble."
  - **Sequence/context parallel** — split the sequence dim for very long context.
  - **Expert parallel (EP)** — for **MoE**, place different experts on different GPUs; route tokens to them. (MoE = more params, fewer *active* per token — e.g. DBRX: 132B total / 36B active.)
  - **3D parallelism** = DP × TP × PP composed — how 70B–400B models are actually trained.
- **Memory optimization** — **ZeRO / FSDP** shard optimizer states, gradients, and params across data-parallel ranks (vs replicating) → trains far bigger models on the same hardware. Plus **mixed precision (bf16)**, **gradient checkpointing** (recompute activations to save memory), gradient accumulation.
- **Checkpointing & fault tolerance** — at 1000s of GPUs, hardware *will* fail mid-run. Asynchronous/distributed checkpointing, frequent enough to bound lost work but not so frequent it stalls; automatic detect-and-restart from last checkpoint; elastic training. **This is your infra-strength flex.**
- **Data pipeline** — dedup, quality filtering, tokenization, sharding, streaming/prefetch so the GPUs never wait on data. Data quality > data quantity.

**Key decisions & tradeoffs.**

| Decision | The tradeoff |
|---|---|
| LoRA vs full fine-tune | cost/speed/many-adapters (LoRA) vs maximal quality/deep change (full) |
| DPO vs PPO (RLHF) | simplicity, stability, no RM (DPO) vs more control/exploration (PPO) |
| TP vs PP vs DP mix | comms pattern vs memory vs bubble; TP intra-node, PP/DP inter-node |
| Checkpoint frequency | lost-work-on-failure vs checkpoint I/O stall |
| Sync vs async | convergence stability (sync) vs straggler tolerance/throughput (async) |
| bf16 / fp8 | throughput+memory vs numerical stability |

**Numbers to know.** Memory per param in training ≈ **16–20 bytes** (fp16 weight 2 + grad 2 + Adam states 8 + activations) → a 70B model needs ~1.2–1.5 TB *just for state* → must shard (ZeRO/FSDP) across many GPUs. Communication (all-reduce) often dominates → overlap comms with compute. MoE: active params ≪ total params (that's the point). Mean-time-to-failure shrinks with GPU count → checkpoint accordingly.

**Failure modes.** Stragglers stalling a sync all-reduce · node failure losing hours of work (→ checkpoint cadence) · OOM from underestimated activation memory · loss spikes/divergence (→ grad clip, LR schedule, checkpoint rollback) · data-loader bottleneck starving GPUs · silent data corruption/leakage poisoning the model.

> **Senior vs Staff.** Senior lists the parallelism types. Staff (a) reasons about *which bottleneck* (memory vs comms vs bubble vs data-loading) dominates and picks the parallelism mix accordingly, (b) treats **fault tolerance & checkpointing as the central design problem** at scale (this is where infra people win), (c) starts at the cheapest fine-tuning rung that clears the bar, and (d) makes the data pipeline and data quality a first-class concern, not an afterthought.

**Maps to.** D4. **Companies:** OpenAI, NVIDIA, Cohere, Together, Google, Anthropic.

**Top follow-ups.** "Adapt to our domain — how?" → climb the ladder: RAG/LoRA before full FT before RLHF; justify the rung. "Train 70B, won't fit?" → FSDP/ZeRO + 3D parallelism + grad checkpointing + bf16; show the memory math. "1000 GPUs, one dies?" → distributed checkpointing + auto-restart + elastic; bound lost work. "MoE tradeoff?" → more capacity per FLOP, but routing/load-balance complexity + expert-parallel comms.

---

### Area 5 — Evaluation & Quality Systems  → *worked solution: D5 (to write)*

**Scope.** Knowing whether the system is good — and catching when it silently gets worse. Offline eval (golden sets, metrics), online eval (A/B, production signals), **LLM-as-judge**, regression gates, drift detection after fine-tunes or model swaps. This is the area that makes every other area *safe to change*, and the one infra candidates most under-invest in.

**Mental model.** *In ML, you can't tell if a change helped by reading the diff — output is non-deterministic and quality is statistical. Eval is your compiler and your test suite. No eval = no safe iteration.* "How do you know it works?" is the question behind every ML design prompt; have a crisp two-layer (offline + online) answer ready.

**Building blocks.**
- **Golden / eval set** — a curated, version-controlled set of (input → expected/labeled output) cases. Seed from real traffic + synthetic generation, then human-verify. The asset everything else depends on; growing and curating it is ongoing work.
- **Offline metrics** — task-dependent: retrieval (**Recall@k, MRR, nDCG**), classification (precision/recall/F1, PR-AUC), generation (faithfulness/groundedness, answer relevance, **RAGAS** context precision/recall), exact-match/code-exec for verifiable tasks.
- **LLM-as-judge** — use a strong model to score outputs on a rubric (factuality, relevance, coherence) when there's no ground truth. Frameworks: **G-Eval**, **RAGAS**. *Must be calibrated against a human-audited sample* — the judge has biases (length, position, self-preference) and can drift.
- **Online eval** — A/B tests, interleaving, and implicit signals (thumbs, click/dwell on citations, regenerate rate, task completion, retention). The ground truth that offline approximates.
- **Regression gates** — automated eval that must pass before any change ships (new embedder, prompt, model version, chunker). Turns "quality regresses silently" into "quality regresses → build fails."
- **Drift & monitoring** — track input distribution shift, output quality on a sampled-and-judged stream, and capability regression after a model/provider update.

**Key decisions & tradeoffs.**

| Decision | The tradeoff |
|---|---|
| Human vs LLM-judge vs metric | accuracy/trust (human) vs scale/cost (LLM-judge) vs cheap/narrow (metric) — use all three in tiers |
| Offline vs online weight | fast/safe iteration (offline) vs real ground truth but slow & risky (online) |
| Eval-set size & freshness | coverage/statistical power vs labeling cost; must evolve with traffic |
| Gate strictness | ship velocity vs regression risk; set thresholds by stakes |
| Judge model choice | quality (frontier judge) vs cost (judge runs on every eval) |

**Numbers to know.** Golden set 200–1000 labeled cases to start. Always sample-and-audit the LLM-judge against humans (e.g., judge agreement ≥ ~80% before you trust it). Faithfulness = your hallucination KPI, inverted. Report distributions/p-values on A/Bs, not single runs.

**Failure modes.** Judge bias (length/position/self-preference) treated as truth · eval set leaks into training (contamination) → inflated scores · offline-online gap (good on golden set, bad in prod) · "metric gaming" (optimize the metric, not the goal) · no gate → silent regression ships · stale eval set that no longer reflects traffic.

> **Senior vs Staff.** Senior reports a metric. Staff (a) *defines the success metric before the architecture*, (b) builds **offline + online + a regression gate** as a system, (c) is skeptical of LLM-as-judge and calibrates it against humans, and (d) treats the eval set as a maintained, contamination-controlled asset. Staff make eval the thing that lets the team move fast safely.

**Maps to.** D5; underpins D1 (faithfulness) and D3 (trajectory eval). **Companies:** Anthropic, OpenAI, Cohere, and *every* serious AI-eng role.

**Top follow-ups.** "How do you know it works?" → offline golden-set metrics + online A/B + judged production sample. "Is retrieval or generation the problem?" → decompose: Recall@k isolates retrieval, faithfulness isolates generation; fix the layer the metrics indict. "Trust LLM-as-judge?" → only after calibrating against a human-audited sample; monitor judge drift. "New model version — ship it?" → run the regression suite + canary + online A/B before full rollout.

---

### Area 6 — Data, Features & Embedding Pipelines  → *worked solutions: D6, D7, D8 (to write)*

**Scope.** The systems that *feed* the models: feature stores, online/offline parity, point-in-time correctness, streaming vs batch ingestion, freshness, and large-scale embedding pipelines with incremental updates. The classic-ML-meets-LLM area; pairs naturally with your data-infra strength.

**Mental model.** *The model is only as good as the freshest correct data you can get to it at inference time — and the #1 silent bug is **training/serving skew**: the features computed offline for training differ from those computed online for serving.* Most "the model worked in the notebook but not in prod" failures live here.

**Building blocks.**
- **Feature store** — a system that computes, stores, and serves features with **two faces**: an **offline store** (columnar, for training, point-in-time joins) and an **online store** (low-latency KV, for serving). The point is a *single definition* serving both → parity.
- **Online/offline parity** — the same transformation logic produces training and serving features. Achieved by sharing code/definitions, not re-implementing. Skew here corrupts the model invisibly.
- **Point-in-time correctness** — when building training data, each label must join only to feature values *as of that timestamp* — no peeking at the future. Leakage here inflates offline metrics and tanks production.
- **Freshness** — streaming features (last-N-seconds aggregates) vs batch (daily). Sets the ingestion architecture; real-time fraud needs sub-second, recommendations may tolerate hours.
- **Embedding pipeline at scale (D8)** — for 100M+ docs: incremental upsert on create/update/delete (re-chunk → re-embed → upsert vector + lexical), tombstone deletes, dedup, and **re-embedding migrations** (a model upgrade = rebuild the whole index, dual-write, cut over). Never mix embedding versions in one index.
- **Streaming inference (D6 fraud)** — features computed on an event stream, model scores in-line under tight latency, with a feedback loop (labels arrive late → retrain).

**Key decisions & tradeoffs.**

| Decision | The tradeoff |
|---|---|
| Streaming vs batch features | freshness (streaming) vs simplicity & cost (batch) |
| Precompute vs on-demand features | serving latency (precompute) vs storage & staleness (precompute) / freshness (on-demand) |
| Online store tech | latency (in-memory KV) vs cost/scale |
| Full re-embed vs incremental | correctness on model change (full) vs cost/freshness (incremental) |
| Label latency handling (fraud) | precision (wait for confirmed labels) vs recall/freshness (act on weak signals) |

**Numbers to know.** Point-in-time joins are the correctness lever for training data. Re-embedding 100M+ docs is a *migration*, not an update — plan dual-write + cutover. Fraud: precision/recall tradeoff is a *business* decision (cost of a false positive vs a missed fraud), set the threshold with that, not by F1 alone.

**Failure modes.** **Training/serving skew** (the headline bug) · label leakage / no point-in-time correctness → great offline, awful online · stale online features · mixed embedding versions in one index → garbage similarity · feedback-loop bias (model affects the data it's later trained on) · slow online store blowing the latency SLA.

> **Senior vs Staff.** Senior builds a feature pipeline. Staff (a) makes **parity and point-in-time correctness the central design constraint**, (b) chooses streaming vs batch *per feature* from the freshness requirement, not uniformly, (c) treats re-embedding as a versioned migration with cutover, and (d) names the precision/recall threshold as a business tradeoff (fraud).

**Maps to.** D6 (fraud), D7 (feature store), D8 (embedding pipeline). **Companies:** Robinhood, Wealthsimple, Stripe-style, Cohere, Glean.

**Top follow-ups.** "Avoid train/serve skew?" → single feature definition serving both stores; share transform code. "Point-in-time correctness?" → as-of joins; never join future feature values to past labels. "100M docs, model upgrade?" → offline rebuild + dual-write + cut over; never mix versions. "Real-time fraud latency?" → streaming features + in-line scoring + async label/retrain loop; set threshold by cost of FP vs FN.

---

### Area 7 — Safety, Guardrails & Governance  → *cross-cutting; prompt: content moderation at 10B msgs/day*

**Scope.** Keeping the system safe, compliant, and bounded: input/output filtering, **prompt-injection** defense, PII handling, jailbreak resistance, moderation at scale, abstention, access control, and provenance/audit. Cross-cuts every area; a *required* follow-up at frontier labs and regulated domains, and its own design prompt (content moderation).

**Mental model.** *Treat every model input as potentially adversarial and every model output as potentially wrong. Safety is layered defense-in-depth around a component you can't fully trust — there's no single fix, only stacked mitigations with explicit residual risk.*

**Building blocks.**
- **Input guardrails** — moderation classifiers (toxicity, CSAM, violence), PII detection/redaction, **prompt-injection** detection. Injection is the marquee 2026 risk: untrusted content (a web page, a retrieved doc, a tool output) carries instructions that hijack the agent → isolate untrusted text, never let it issue privileged actions, prefer structured tool I/O.
- **Output guardrails** — toxicity/policy filters, PII leak checks, **groundedness/citation verification** (Area 1/5), structured-output validation, and **abstention** ("I don't know") for low-confidence/high-stakes.
- **Access control & multi-tenancy** — ACL enforced *inside* the retrieval/query (Area 1), per-tenant isolation, "unauthorized content never reaches the context." A security boundary, not a post-filter.
- **Moderation at scale (the prompt)** — 10B msgs/day → tiered: cheap fast classifier on everything → escalate uncertain cases to a bigger model / human review queue. Optimize for the precision/recall point the policy demands; asymmetric costs (missing CSAM ≫ a false flag).
- **Governance / provenance** — log query, sources, prompt, model version, output for audit; ability to purge a poisoned/illegal doc and its derived chunks fast; data-residency and retention controls.
- **Alignment basics (labs)** — RLHF/Constitutional AI for behavior, red-teaming, jailbreak testing; Anthropic **Responsible Scaling Policy** / OpenAI **Preparedness Framework** — have an informed POV (see [[anthropic-interview-guide]]).

**Key decisions & tradeoffs.**

| Decision | The tradeoff |
|---|---|
| Guardrail strictness | safety/compliance vs false positives + latency + user friction |
| Tiered moderation | cost (cheap-first) vs latency of escalation + human-review capacity |
| Block vs flag vs abstain | safety (block) vs utility (flag/abstain) — set by stakes |
| In-model vs external guardrails | simplicity (model self-polices) vs auditability & control (external filters) |
| Inline vs async moderation | latency (async) vs catching-before-harm (inline) |

**Numbers to know.** Costs are asymmetric — choose the precision/recall operating point from *harm cost*, not F1. Defense-in-depth: assume each layer is leaky; stack them. Prompt injection has *no complete fix* — design to *limit blast radius* (least privilege, sandbox, human-confirm for destructive actions).

**Failure modes.** Prompt injection via tool/retrieval output (Area 3) · jailbreaks bypassing the system prompt · PII leakage in outputs or logs · ACL leak (retrieving forbidden docs) · over-blocking (safety theater that kills utility) · poisoned source with no fast purge path · the model itself being the guardrail (trivially bypassed).

> **Senior vs Staff.** Senior adds an input/output filter. Staff (a) treats all inputs as adversarial and all outputs as unverified (defense-in-depth with named residual risk), (b) makes block/flag/abstain an explicit policy by stakes, (c) enforces ACL *inside* the query and limits agent blast radius (least privilege + sandbox), and (d) builds provenance/purge for audit and incident response.

**Maps to.** Content-moderation prompt; cross-cuts D1 (citations/ACL), D3 (injection/sandboxing), D5 (verification). **Companies:** Anthropic, OpenAI, Harvey (legal liability), Glean (enterprise ACL), Robinhood/Wealthsimple (compliance).

**Top follow-ups.** "Stop prompt injection?" → no full fix; isolate untrusted input, least privilege, structured tool I/O, human-confirm destructive actions, eval against an injection suite. "Moderate 10B msgs/day?" → tiered cheap→expensive→human, asymmetric thresholds, async where latency allows. "PII?" → detect+redact on input, leak-check output, scrub logs, retention controls. "Per-user permissions?" → ACL predicate inside the index query; never post-filter.

---

### Area 8 — Observability, Cost & Reliability (LLMOps)  → *cross-cutting; prompt: LLM gateway/router*

**Scope.** Operating LLM systems in production: tracing, cost attribution, caching, routing/fallbacks, rate limiting, SLOs, and versioning/rollback for models, prompts, and indexes. The "make it survive contact with real traffic and a real budget" area — pure staff territory, and an explicit prompt (LLM gateway/router with caching + fallback + cost).

**Mental model.** *An LLM system fails differently from a normal service: it can be up, fast, and confidently wrong, while quietly costing 10× last week. So observability must capture **quality and cost**, not just latency and errors — and every component (model, prompt, index) needs a version and a rollback.*

**Building blocks.**
- **Tracing** — log per request: prompt, response, **model version, prompt version**, retrieved chunk IDs, latency (TTFT/TPOT), **token counts + cost**, and tool calls (agents). Reproducibility is the foundation of debugging a non-deterministic system. Tools: LangSmith/Langfuse/Arize-style.
- **Quality-in-prod** — sample outputs → LLM-judge / human review → dashboards (faithfulness, refusal rate, user feedback). Ties to Area 5.
- **Cost engineering** — tokens dominate $. Levers: semantic/exact **caching** (skip the call on repeats), **prompt caching** (Area 2 prefix reuse), **model routing** (cheap model for easy queries, escalate hard ones), context trimming, and quotas. Attribute cost per tenant/feature.
- **LLM gateway/router (the prompt)** — a control plane in front of providers: routing (by cost/quality/capability), **caching**, **fallback** (provider B if A errors/times out), rate limiting + quotas, retries, and unified logging/cost. Decouples app from provider; the practical answer to "multi-model, multi-provider, don't go down or broke."
- **Reliability patterns** — timeouts + retries with backoff, circuit breakers, **graceful degradation** (smaller model / cached answer / BM25-only retrieval when the premium path is down), load shedding, multi-provider/multi-region failover.
- **Versioning & rollback** — models, prompts, and embeddings are all versioned artifacts; ship via canary → A/B → rollout, with **one-click rollback** because quality regresses silently (Area 5).

**Key decisions & tradeoffs.**

| Decision | The tradeoff |
|---|---|
| Cache aggressiveness | cost/latency savings vs staleness & cache-correctness (semantic cache false hits) |
| Model routing | cost (cheap default) vs quality risk on misrouted hard queries |
| Fallback model quality | availability (always answer) vs degraded quality on fallback |
| Log verbosity | debuggability/audit vs storage cost + PII exposure in logs |
| Self-host vs API (ops view) | control & cost-at-scale vs zero-ops & burst capacity |

**Numbers to know.** Token cost dominates the bill → caching a hot fraction can cut spend 30–70%. Always report p50/**p99**, not averages. Trace sampling: log all metadata, sample full prompt/response if volume/cost/PII require. Canary % and rollback time (target minutes) are real design parameters.

**Failure modes.** Silent quality regression with green dashboards (→ quality-in-prod monitoring) · cost blowup from a retry storm or an agent loop (→ budgets + circuit breakers) · cache serving stale/wrong answers (semantic-cache false positives) · provider outage with no fallback · prompt change shipped with no version/rollback · PII sitting in logs.

> **Senior vs Staff.** Senior monitors latency and errors. Staff (a) monitors **quality and cost as first-class SLOs**, (b) designs the **gateway** (routing + cache + fallback + quotas) as the reliability/cost control plane, (c) versions models/prompts/indexes with canary + fast rollback, and (d) designs explicit graceful-degradation paths for every dependency.

**Maps to.** LLM-gateway prompt; cross-cuts *all* areas (every system needs this layer). **Companies:** applied-AI roles everywhere; Anthropic/OpenAI (scale + cost), Anysphere/Fireworks/Together (serving economics).

**Top follow-ups.** "Cut cost?" → cache (semantic+prefix) + route to cheaper model + trim context + quotas; attribute per tenant. "Provider goes down?" → gateway with multi-provider fallback + circuit breaker + degrade to cached/smaller. "Debug a bad answer?" → pull the trace (prompt+sources+versions), replay, isolate the layer. "Ship a new prompt safely?" → version it, canary, A/B with the regression gate, one-click rollback.

---

## 3. Cross-cutting concerns — the staff checklist for *every* prompt

Regardless of the area, run through these. Naming them *proactively* (before the interviewer asks) is a reliable staff tell. These are the seams where ML systems break in production.

1. **Latency budget, quantified.** Where does the time go? TTFT vs TPOT, p50/**p99** (not averages), stream tokens to hide LLM latency, parallelize independent stages. State the SLA, then allocate it across stages.
2. **Cost engineering.** GPUs/tokens dominate. Cache (semantic + prefix), route to the cheapest model that clears the bar, trim context, quantize, quota per tenant. Cost is a *design axis*.
3. **Multi-tenancy, isolation & ACL.** Per-tenant quotas, fair scheduling, noisy-neighbor defense; ACL enforced *inside* the query/index, never as a post-filter. Unauthorized data never reaches the model.
4. **Online/offline parity.** The offline build loop and online serve loop must agree — share definitions/code. Train/serve skew and embedding-version skew are top silent killers.
5. **Versioning, migration & rollback.** Models, prompts, embeddings, indexes are versioned artifacts. Canary → A/B → rollout, with minute-scale rollback. Never mix embedding versions in one index.
6. **The non-determinism tax.** Same input → different output; quality regresses silently. → eval gates on every change, drift monitoring, replayable traces. (Area 5 + 8.)
7. **Failure modes & graceful degradation.** For every dependency, name the failure and the degraded-but-alive path (vector store down → BM25-only; premium model down → smaller/cached; agent stuck → step cap + abort).
8. **Human-in-the-loop & feedback.** Where do humans label, review, or correct? How does that feedback close the loop into retraining/eval? High-stakes → human review queue.
9. **Security / adversarial input.** Treat inputs as adversarial (prompt injection), outputs as unverified. Least privilege, sandboxing, provenance/purge. (Area 7.)

---

## 4. Universal staff signals (the consolidated cheat sheet)

What turns a complete, correct answer into a *staff* answer — independent of area:

- **Metric-first.** Open with *"what does good mean and how do we measure it offline + online?"* before architecture.
- **Tradeoffs named, not hidden.** Every choice: *"X over Y because Z; the cost is W."* Judgment over recall.
- **Quantified.** Real numbers — recall@k, KV-cache GB, p99 ms, $/1M tokens, 0.95^10≈0.6 — not "it scales."
- **Failure-mode fluent.** Proactively name what breaks and the degraded path; design for the unhappy case.
- **Sequencing judgment.** *"The one thing I'd build first is ___ because it sets the quality/cost ceiling."*
- **Eval & rollback as architecture.** Because quality regresses silently — gates, canaries, versioning, drift.
- **Cost-aware by default.** GPU/token economics surface in the design, not as an afterthought.
- **Operationally + organizationally literate.** On-call, multi-team GPU sharing, 5-minute rollback, migration plans.
- **Knows the boundaries of its own techniques.** *When not to* disaggregate / go multi-agent / full-fine-tune. Senior over-applies; staff right-sizes.

> **The interview-day reflex:** for any prompt — (1) clarify + state the metric, (2) draw the two/three planes, (3) deep-dive the leverage component with tradeoffs, (4) eval + regression gate, (5) scale/cost/reliability/multi-tenancy, (6) name failure modes + the one thing to build first. That sequence *is* the staff signal.

---

## 5. Coverage matrix — areas → prompts → companies → the one thing to nail

| Area                                    | Worked prompt(s)   | Also shows up in              | Heaviest companies                                        | The one thing to nail                                                     |
| --------------------------------------- | ------------------ | ----------------------------- | --------------------------------------------------------- | ------------------------------------------------------------------------- |
| **1. Retrieval & Knowledge**            | **D1** (done)      | D8; follow-ups everywhere     | Perplexity, Cohere, Harvey, Glean, Anthropic              | Retrieval is the quality ceiling; citation *verification* by stakes       |
| **2. Inference & Serving**              | **D2**             | sub-100ms completion; gateway | NVIDIA, OpenAI, Anthropic, Anysphere, Fireworks, Together | "Prefill compute-bound, decode memory-bound" → batching, KV, p99          |
| **3. Agentic Systems**                  | **D3**             | Cursor agent; fraud agent     | Robinhood, Anysphere, Harvey, Anthropic, Cognition        | Reliability of a stochastic loop: compounding error, step caps, injection |
| **4. Training & Fine-tuning**           | **D4**             | RLHF/LoRA in E-round          | OpenAI, NVIDIA, Cohere, Together, Google                  | Parallelism mix by bottleneck + fault-tolerant checkpointing (your flex)  |
| **5. Evaluation & Quality**             | **D5**             | underpins D1, D3              | Anthropic, OpenAI, Cohere, all AI-eng                     | Metric-first; offline+online+regression gate; calibrated LLM-judge        |
| **6. Data, Features, Embeddings**       | **D6, D7, D8**     | D1 indexing                   | Robinhood, Wealthsimple, Cohere, Glean                    | Train/serve parity + point-in-time correctness; re-embed = migration      |
| **7. Safety & Guardrails**              | content moderation | D1 ACL, D3 injection          | Anthropic, Harvey, Glean, OpenAI, fintech                 | Defense-in-depth; injection has no full fix → limit blast radius          |
| **8. Observability, Cost, Reliability** | LLM gateway/router | *every* prompt                | applied-AI everywhere; serving-cost shops                 | Quality+cost as SLOs; gateway = cache+route+fallback; versioned rollback  |

**One-paragraph prompts (have ready, don't write full):** code-completion serving sub-100 ms (Anysphere) = Area 2 + 3 · LLM gateway/router (applied-AI) = Area 8 · content moderation 10B msgs/day (Anthropic) = Area 7 + 5.

---

## 6. How to study Track D with this map (~18 hr budget, per master plan §6)

1. **Read this doc once end-to-end** (~45 min). Internalize §1 (driving framework) + §4 (staff signals) — they're reusable across all 8 prompts.
2. **Write full worked solutions for D1–D5** (Areas 1–5) — these cover ~90% of cases. [[D1-rag-with-citations]] is the depth/format template to match. Each: drive-the-interview talk-track → requirements → architecture → deep-dive → eval → scale/cost → follow-ups.
3. **Rehearse D6–D8 verbally** (Area 6) — structured out loud, no full write-up. Pick D8's variant (embedding pipeline vs AV sim) by your top targets.
4. **Drill the cross-cutting checklist (§3)** until you name it reflexively — it's the cheapest staff signal.
5. **Route by target** using §5: labs → Areas 1,2,3,5,7; NVIDIA → 2,4; Robinhood/fintech → 3,6,8; Cohere → 1,6 + take-home; AV → 4,6.
6. **Re-skin per company in Weeks 9–10** — same areas, company framing (Harvey = Area 1 with legal auditability; Anysphere = Area 2+3 latency; Cohere = Area 1+6 enterprise/cost).

> **Slip rule (from the master plan):** if time runs short, protect **Area 5 (eval)** and the **§1 framework** — they make every other area defensible and are the cheapest points. Trim depth on D6–D8 first.

---

## 7. Sources

**Currency-checked 2026-06-17** (fast-moving areas; fundamentals from established knowledge):
- Inference serving — prefill/decode disaggregation, vLLM/SGLang, chunked prefill, prefix caching, NVIDIA Dynamo — https://bentoml.com/llm/inference-optimization/prefill-decode-disaggregation · https://github.com/sgl-project/sglang · https://www.spheron.network/blog/prefill-decode-disaggregation-gpu-cloud/
- Agents — MCP (Anthropic, Nov 2024; adopted by OpenAI/Google), A2A, orchestration patterns (chaining/routing/parallelization/planner-critic) — https://en.wikipedia.org/wiki/Model_Context_Protocol · https://en.wikipedia.org/wiki/Agent2Agent
- Training — DeepSpeed/ZeRO, FSDP, MoE (DBRX 132B/36B active) — https://en.wikipedia.org/wiki/DeepSpeed
- Eval & observability + 2026 staff-interview framing (LLM-as-judge, G-Eval/RAGAS, trace logging, cost/observability tradeoffs) — https://prachub.com/resources/genai-llm-system-design-interview-guide-2026 · https://www.tryexponent.com/blog/machine-learning-system-design-interview-guide · https://www.confident-ai.com/knowledge-base/compare/top-7-llm-observability-tools

**Canonical references (search by name):** PagedAttention/vLLM (Kwon et al.) · FlashAttention (Dao et al.) · Speculative decoding (Leviathan et al.), Medusa, EAGLE · ZeRO (Rajbhandari et al.) · Megatron-LM 3D parallelism · LoRA (Hu et al.), QLoRA · RLHF (Ouyang et al. / InstructGPT), DPO (Rafailov et al.) · ReAct (Yao et al.) · RRF (Cormack et al.), HNSW (Malkov & Yashunin), ColBERT · RAGAS, G-Eval · Lost-in-the-Middle (Liu et al.).

**Companion files:** [[interview-prep-master-plan-2026]] §6 (the prompt list + budget) · [[D1-rag-with-citations]] (Area 1 worked) · [[anthropic-interview-guide]] (safety POV, values) · [[cohere-interview-guide]] (enterprise framing) · [[ai-ipo-interview-guide]] (per-company reported questions).

---

*Created 2026-06-17. The structural foundation for Track D — the 8 competency areas underneath D1–D8, at staff depth. Read this first, then write D2–D5 as worked solutions of Areas 2–5. Pair with [[interview-prep-master-plan-2026]] §6.*



