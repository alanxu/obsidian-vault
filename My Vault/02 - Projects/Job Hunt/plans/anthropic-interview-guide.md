# Anthropic Interview Guide for Non-ML Engineers: Applied AI Engineer, Software Engineer, and Forward Deployed Engineer (2025–2026)

## TL;DR
- **You do NOT need an ML/research background.** Anthropic states roughly half its technical staff came from non-ML backgrounds, and interviewing.io confirms verbatim: *"you do not have to know anything about machine learning or have research experience to interview with Anthropic as a software engineer."* The hard, non-negotiable bars are practical Python coding (multi-level CodeSignal problems), a values/culture round that fails the most candidates, and — for Applied AI/FDE — a customer-discovery conversation.
- **The three loops share a spine** (recruiter screen → progressive Python coding → hiring-manager deep dive → system design → values round) but diverge at the end: SWE adds a second coding round + infra system design; Applied AI/FDE swap one technical round for a Claude take-home build and a customer-conversation role-play that reportedly filters the majority of candidates who clear coding.
- **AI tools are strictly prohibited in live interviews and take-homes** (allowed only for prep/resume polish). The best-ROI prep: (1) drill the recurring coding bank (in-memory DB, web crawler, stack-trace→trace, duplicate files, LRU cache) under timed conditions in Python; (2) form a genuine, slightly skeptical point of view on AI safety from Anthropic's published materials.

## Key Findings

**1. The bar is high but the format is unusual, not LeetCode-hard.** Glassdoor rates Anthropic interviews ~3.3/5 difficulty overall (AI/ML Engineer rated hardest). Coding problems are "practical," "build-from-scratch," and progressive — you solve a simple version, then the interviewer layers constraints. Concurrency/multithreading recurs across rounds.

**2. The values/culture round is the most common failure point** "per Anthropic recruiters" (interviewing.io). It is described as "closer to a therapy session than a job interview" — emotionally probing, and it rewards genuine, skeptical engagement over rehearsed enthusiasm.

**3. Non-ML engineers are explicitly welcome**, but Applied AI and FDE roles expect *applied* LLM fluency (prompting, RAG, evals, tool use, Claude API) — NOT ML research/training. This is learnable for a strong backend engineer.

**4. Compensation is among the highest in tech**, heavily equity-weighted (Profit Participation Units / RSUs). Equity is now valued against Anthropic's **$965 billion post-money valuation** following its **$65 billion Series H** (announced May 28, 2026, led by Altimeter Capital, Dragoneer, Greenoaks, and Sequoia Capital — making Anthropic the most valuable AI startup, eclipsing OpenAI per CNBC/Bloomberg). Note that most public Levels.fyi compensation self-reports below predate this round and were priced against earlier (~$61.5B) valuations, so the equity component of current offers may be marked considerably higher. Anthropic is widely reported to be firm on offers (little negotiation).

---

## SHARED ELEMENTS (all three roles)

### Anthropic's AI-usage policy (verbatim guidance)
From Anthropic's official candidate guidance page:
- **Applications/resume:** draft yourself first, then "use Claude to refine it."
- **Take-home assessments:** "Complete these without Claude unless we indicate otherwise."
- **Live interviews:** "This is all you – no AI assistance unless we indicate otherwise."
- Google/Stack Overflow are allowed in coding screens (per a candidate's quoted Anthropic email); AI code generators are not. Anthropic says it uses LLMs to detect code "specifically engineered to pass tests rather than solving the problem genuinely."

**Why this matters:** Several prep sites (linkjob.ai, lockedinai.com, ophyai.com, etc.) market "undetectable" AI interview assistants. Using them violates Anthropic's policy and is disqualifying. This guide extracts the legitimate questions those sites report but does not recommend the tools.

### The recruiter screen (shared, ~30 min)
- Covers background, "Why Anthropic?" (*specifically* — not "why AI"), the B-Corp / public-benefit structure, and logistics.
- **It is a real gate, not a formality** — "technically strong candidates fail here because they haven't done the reading." interviewing.io advises *not* revealing salary expectations or where you are with other companies.
- For Applied AI/FDE, candidates report being "unexpectedly grilled on safety reasoning" and the Responsible Scaling Policy here.
- A Glassdoor candidate (Jun 2026): "Even though I only had a 20min phone call screening...90% of the time was a real formal interview with behavioral questions."

### The values / culture round (shared, ~45–60 min) — the #1 failure point
**What it tests** (interviewing.io, IGotAnOffer): "Whether you'll hold your values under real pressure, not whether you have the right opinions about AI. They actively look for skepticism and pushback." Multiple candidates describe it as deeply personal and emotionally probing; follow-ups focus on *how you felt*, not just what you did.

**Five reported question categories** (per AI interview expert Ridhima Khurana, via IGotAnOffer):
1. **AI safety reasoning** — e.g., "What are your thoughts on AI safety and the risks of advanced AI systems?"; "What do you see as the most pressing unsolved problem in AI alignment?"
2. **Proud-project deep dives** — "Tell me about a project or experience you're most proud of."
3. **Safety vs. speed** — judgment about when a model/feature is too risky to ship even if profitable.
4. **Technical misjudgment** — "Tell me about a technical misjudgment that delayed a project. What did you learn?"
5. **Open-ended brainstorming / ethics** — novel ethical situations with no clean answer; "How would you handle a conflict between your personal values and your work?"

**Anthropic's seven core values** (verbatim names, from Anthropic's company page): (1) Act for the global good; (2) Hold light and shade; (3) Be good to our users; (4) Ignite a race to the top on safety; (5) Do the simple thing that works (*"We don't invent a spaceship if all we need is a bicycle"*); (6) Be helpful, honest, and harmless (*"high-trust, low-ego"*); (7) Put the mission first.

**How to prepare (interviewing.io's explicit list):**
- Read: Dario Amodei's "Machines of Loving Grace" (2024) and "The Adolescence of Technology" (Jan 2026); Anthropic's "Core Views on AI Safety" (2023); watch a long-form Dario interview (Dwarkesh or Lex Fridman). *"Internalize the world view, not parrot talking points."*
- Also read the Responsible Scaling Policy and Constitutional AI (candidates who reference these naturally perform well).
- Use deep, emotionally real examples; talk about emotions, not just events; *"Be a person, not a framework"*; *"If you find yourself disagreeing with something Dario says, that's a good sign. Bring that disagreement in."*
- Know the Anthropic-vs-OpenAI distinction: per IGotAnOffer, "the company's founding team left OpenAI after growing concerns about how quickly AI systems were scaling and how little was understood about their inner workings" (2021); Anthropic was structured from the start as a public-benefit corporation where safety is the organizing principle, not a constraint.
- **Caution** (IGotAnOffer): heavily scripted STAR stories "can do more harm than good" in this specific round; avoid the "dream company" trap and the urge to agree with everything.

A cautionary Blind report: one candidate was "quizzed about Dario's book that I didn't read" at onsite and got no offer — the reading is real prep, not optional.

### Compensation (shared context; Levels.fyi, last updated June 2026 — most reports priced before the May 2026 Series H)
Anthropic uses ~L3–L7 numeric levels. Equity is ~60–70% of TC at L4+, as PPUs/RSUs, vesting 4 years with ~annual secondary tender liquidity. Reported bands:
- **Senior Software Engineer:** ~$445K–$575K+ (median ~$563K).
- **Software Engineer (US, all levels):** ~$563K–$785K range cited; median US TC ~$582K–$665K; SF Bay Area median ~$595K; top reported ~$920K.
- **Per-level self-reports:** L3 floor ~$300K; L4 ~$475K (one source: L4 ~$665K with ~$275K base + ~$445K equity); L5 ~$575K–$725K; L6 $850K+. One Blind poster reported an L6 offer at $1.5M→$1.7M TC.
- **Applied AI Engineer / FDE:** ~$300K (L3) to ~$1.2M (L6); most FDE-track roles land L4–L5 at ~$665K–$750K TC; base $220K–$340K. Senior ICs ~$450K–$550K all-in (Levels.fyi).
- Anthropic reportedly does NOT apply geographic pay adjustments and is firm on offers.

### Timeline & decision process (shared)
- **Total:** most report 3–4 weeks; can stretch to 3+ months with team matching/reference checks. Glassdoor average ~19–20 days.
- **Hiring by consensus** (everyone must agree to hire; hiring manager breaks ties). References are taken seriously and probe how you handled conflict and ethical friction.
- Some candidates describe **two onsite loops on separate days, with the second canceled if the first fails** (Exponent). Anthropic provides no rejection feedback.

---

## ROLE 1 — SOFTWARE ENGINEER (SWE / backend / full-stack / infra)

### Sources (recency / credibility)
- **interviewing.io** (Anthropic guide, "based on conversations with Anthropic engineers in 2026") — high credibility, engineer-sourced.
- **Exponent** (tryexponent.com SWE guide, updated 2026; 71 questions, 6 interview experiences) — strong, candidate + interviewer-sourced.
- **Glassdoor** (37+ SWE interviews; 167+ total Anthropic interviews) — raw first-person reports.
- **Blind** (Anthropic Interview Megathread; TC-tagged) — verified-employer posts, mixed reliability.
- **1Point3Acres** (412 Anthropic threads, 5,545 replies; recent dated 面经) — strongest for recent dated onsite questions.
- **Medium** first-person 2025–2026 write-ups (Anqi Silvia; Ajay Kumar "Infrastructure SWE loop, 5 rounds over 3 weeks").
- **PracHub, staffengprep.com, leetcodewizard, IGotAnOffer, aiofferly** — aggregators with worked solutions (treat solutions as study aids; verify independently).
- **GitHub (ryanhestin/anthropic-challenge)** — a candidate's worked Python solution to the viral stack-trace question.
- *Caveat:* linkjob.ai reports real questions but promotes a cheating tool — questions extracted, tool ignored.

### Process (SWE)
interviewing.io's clean 3-step version: **Recruiter call (30 min) → Coding challenge (60–90 min; sometimes skipped for referrals) → Onsite (4–5 hrs, ~5 sessions)**.

Exponent's fuller version:
1. Recruiter screen(s) — 30 min, may split into two calls (second covers comp + sends values docs).
2. **Technical screen** — 60–90 min in CodeSignal/Colab/Replit, shared Python env, multi-tiered.
3. **Hiring manager screen** — 45–60 min, engineering judgment + project deep dive; may include reading/critiquing code in multiple languages.
4. **Onsite loop 1** — 2–3× 60-min: system design, coding, culture fit.
5. **Onsite loop 2** — 2–3× 60-min: experience/behavioral, values alignment, project deep dive.

The onsite (interviewing.io) typically: Hiring manager call (1h) · Coding (1h, CodeSignal) · System design (1h, shared Google Doc) · Second role-specific coding (1h) · Company values (1h).

**The CodeSignal OA format (critical):** 90 minutes, ONE problem in **4 escalating levels**; you must pass all tests at a level to unlock the next. Scored to 600 (some report 1000). Reported passing bar: Anthropic HR states a cutoff (one source: 480), but candidates with 540–590 have failed; the practical bar appears closer to 600 / completing level 3 fully + reaching level 4. Candidates routinely run out of time. *"Spec interpretation could only be obtained by repeatedly running your code against a black-box grader"* — it rewards reading ambiguous specs and testing theories.

**Difficulty/failure patterns:** Values round fails the most candidates. Coding time-pressure on level 4 is the second filter. Multiple FAANG engineers report failing. One Blind poster: cleared SWE loop in <2 days, "no LC BS," got L6. Another: full CodeSignal score → recruiter → onsite → references → offer.

### Questions by round (SWE)

**Recruiter:** Why Anthropic? What roles are you looking for? Where have you worked? (+ AI safety views.)

**Coding — the recurring "small bank" (≈6 problems, reported across many candidates):**
- **In-memory key-value database (MOST common, 4 levels):** SET/GET/DELETE → filtered SCAN by value/prefix → TTL expiry with timestamps → file compression/decompression OR backup/restore (`SEND_MESSAGE_WITH_EXPIRY`, `ZIP_MESSAGES`, `UNZIP_MESSAGES`, `LIST_MESSAGES_AT`). Confirmed variants: **implement a bank with multiple transaction types** (interviewing.io notes this "has been widely circulated and spotted on Blind/YouTube. Anthropic still uses it, but...interviewers may be alert to over-rehearsed solutions"); inventory management (`ADD ITEM`/`COPY_ITEM`/`ADD_DUPLICATE_ITEMS` with `.dupe` suffix); cloud database with transactional consistency; file cache with eviction policy.
- **Multithreaded web crawler (the #1 live-coding question):** given a `get_links(url)`/`get_urls(url)` helper, BFS from a seed URL, same-domain only, strip fragments, dedupe. Part 2: make it multithreaded (ThreadPoolExecutor) with a thread-safe visited set + queue. Follow-ups: asyncio vs threads vs multiprocessing, Python GIL impact, per-host rate limiting/politeness, distributing URLs across a cluster.
- **Stack trace → trace conversion (viral 2025 question):** given timestamped stack samples (each `(ts, [frames outer→inner])`), emit start/end events for a trace visualizer using longest-common-prefix diffing; inner ends before outer; handle recursion (same name at different depths = distinct frames). Follow-up: only emit events for frames stable ≥N consecutive samples.
- **Exclusive execution time from logs:** given `(id, 'START'/'END', timestamp)` chronological logs, compute exclusive time per function id (stack simulation). Follow-ups: equal timestamps / slightly-out-of-order stream (buffer with a heap, `max_delay`); detect N consecutive identical categorical events.
- **Find/eliminate duplicate files:** scan directory, group by size → partial hash (head/tail) → full SHA-256 → exact bytes; minimize I/O; handle large files via chunked reads (don't load whole file); handle permission errors / files changing during scan; mode to replace dupes with hard links. Follow-ups: chunk-size choice, hashing algorithm, is the bottleneck I/O or CPU, parallelization, cross-machine dedup, incremental updates (ADD/MODIFY/DELETE/QUERY maintaining duplicate groups).
- **LRU cache:** production-grade, thread-safe, error handling, complexity in comments. Variant: fix an existing LRU cache that mishandles `*args`/`**kwargs`; or find-the-bug in a provided cache (key-generation bug).
- **Other reported:** image processing (grayscale/scale ops, small→large images); parse URLs and count domain matches; scale a token-generating function to 100k req/s.

**System design (SWE) — AI-infra flavored, but pure-infra candidates with no ML do well:**
- "Design the Claude chat service." / "Design a Claude/GPT multi-question single-thread service."
- **Inference batching system:** single GPU, ≤100 inputs/batch, synchronous waiting users — design intake → batching → GPU routing → response delivery. Probes: which GPU has capacity, failover.
- "Design an API for serving LLMs efficiently" — request batching, queuing, GPU utilization under variable load, priority queue, streaming responses, variable-length requests, GPU memory under concurrency.
- Distributed search for 1B documents / 1M QPS (sharding, caching) + LLM inference at 10k req/s.
- Distributed job queue; design a prompt playground (real-time streaming, global scale); handle 100x traffic spikes without crashing external APIs; file-sharing/distribution system; banking app.
- "Don't worry about memory constraints; focus on interesting architectural considerations" (one candidate's interviewer). Evaluation is "entirely on infrastructure/distributed systems: queuing, batching, load balancing, fault tolerance, scale" (Exponent) — i.e., no ML needed.

**Hiring manager / project deep dive:** Walk through a project you owned end-to-end; key technical decisions and tradeoffs; what you'd do differently; defend every architectural choice "as if in a design review with a skeptical senior engineer." Sometimes a code-review exercise across languages. The project deep dive (often in loop 2, ~20 min present + 40 min questions, in Notion/slides) is "closer to behavioral than technical."

**Behavioral:** Disagreement with a teammate (use STAR; be concise); time you failed; ownership; conflict resolution; "What would you do if midway through a project you realized it was infeasible?"

### Deep worked solutions (SWE)

**(a) Stack trace → trace conversion.** *Reasoning to narrate:* Track a "current stack." For each new sample, compute the longest common prefix (LCP) with the previous stack. Frames in the old stack *below* the LCP have ended (emit end events deepest-first); frames in the new stack below the LCP have started (emit start events shallow→deep). The key insight (from the GitHub solution): "if the tracked stack is bigger than the sample, functions ended; if smaller, functions started." Recursion is handled because identity is (depth, name) within the LCP, so the same name at a new depth is a new frame.
```python
def samples_to_trace(samples):
    events = []          # (timestamp, 's'|'e', name)
    prev = []            # current tracked stack
    for ts, stack in samples:
        # longest common prefix
        i = 0
        while i < len(prev) and i < len(stack) and prev[i] == stack[i]:
            i += 1
        # ends: anything in prev below the LCP, deepest first
        for d in range(len(prev) - 1, i - 1, -1):
            events.append((ts, 'e', prev[d]))
        # starts: anything in stack below the LCP, shallow->deep
        for d in range(i, len(stack)):
            events.append((ts, 's', stack[d]))
        prev = stack
    # finalize: close remaining frames at last timestamp
    last_ts = samples[-1][0] if samples else 0
    for d in range(len(prev) - 1, -1, -1):
        events.append((last_ts, 'e', prev[d]))
    return events
```
Complexity: O(S) total stack entries; O(D) extra space (max depth). Edge cases: identical consecutive stacks (LCP = full → no events), empty input, single sample (emit all starts then all ends). Follow-up (≥N consecutive samples): track per-depth `(name, first_seen_ts, streak, emitted?)`; only emit a start once streak hits N, using the streak's first timestamp.

**(b) Exclusive execution time from logs.**
```python
def exclusive_times(logs):
    times, stack, prev = {}, [], None
    for fid, event, t in logs:        # logs chronological
        times.setdefault(fid, 0)
        if stack and prev is not None:
            times[stack[-1]] += t - prev
        if event == 'START':
            stack.append(fid); prev = t
        else:                          # END
            stack.pop(); prev = t      # half-open: END at t stops at t
    return times
```
Follow-up (out-of-order stream, `max_delay`): push each entry into a min-heap keyed `(timestamp, arrival_index)`; once heap size > `max_delay`+1, pop the smallest and process. This corrects local disorder online with O(max_delay) buffer. Narrate half-open timing (a call s→e lasts e−s) and the tie-break preserving arrival order.

**(c) Duplicate files (the three-stage funnel — narrate the I/O minimization).** Stage 1 group by size (unique size ⇒ no dup, skip). Stage 2 within a size group, hash a small head+tail signature. Stage 3 full SHA-256 (and optionally exact byte compare to defeat collisions).
```python
import hashlib, os
def find_duplicates(root, chunk=8192):
    by_size = {}
    for dirpath, _, files in os.walk(root):
        for f in files:
            p = os.path.join(dirpath, f)
            try: by_size.setdefault(os.path.getsize(p), []).append(p)
            except OSError: continue          # permission / vanished
    groups = []
    for size, paths in by_size.items():
        if len(paths) < 2: continue           # unique size -> skip hashing
        by_hash = {}
        for p in paths:
            try:
                h = hashlib.sha256()
                with open(p, 'rb') as fh:
                    for block in iter(lambda: fh.read(chunk), b''):
                        h.update(block)        # streamed, no full load
                by_hash.setdefault(h.hexdigest(), []).append(p)
            except OSError: continue
        groups += [g for g in by_hash.values() if len(g) >= 2]
    return groups
```
Talking points the interviewer probes: chunk size (balance syscalls vs memory; align to filesystem block, e.g., 64KB–1MB for large files); SHA-256 vs MD5 (collision resistance vs speed); is the bottleneck I/O (then parallelize reads / async) or CPU (then multiprocess the hashing); cross-machine dedup (content-addressed storage, distribute by hash prefix); incremental version (maintain a reverse index keyed by (size, head/tail sig, full hash, exact content) and a set of buckets with ≥2 members so QUERY is O(1)).

**(d) Multithreaded web crawler.** Single-threaded BFS first; then ThreadPoolExecutor with a thread-safe `set` guarded by a `Lock` (or `queue.Queue` + worker pool). Narrate: race on visited set (check-and-add under lock); termination/quiescence (track in-flight count; done when queue empty AND no workers active); per-host politeness (rate limit); URL normalization (strip fragments, www, trailing slash). GIL point: crawling is I/O-bound so threads release the GIL on network waits → threads help; for CPU-bound parsing, prefer multiprocessing or asyncio. Distributed: shard the frontier by domain hash, use a shared "seen" structure (e.g., Redis/bloom filter), at-least-once vs exactly-once semantics.

**(e) In-memory DB (4 levels) — strategy more than code.** Use a dict for storage; design for extension from level 1 (e.g., store values as records, keep an index for SCAN). For TTL, store `(value, expiry_ts)` and lazily expire on read plus optionally a sweep. For backup/restore, snapshot the dict (deep copy) keyed by timestamp. **Narration tips:** write modular helpers each level can extend; submit working code early; prioritize unlocking level 4 over perfecting level 1; test against the grader continuously.

### Tips (SWE)
- Practice in a **shared Python env** (Colab/Replit/CodeSignal), not your IDE; use a large monitor.
- Know the **standard library cold**; "do the simple thing that works" — interviewers prefer a clean loop over a clever one-liner.
- Drill **concurrency** (threading, asyncio, locks, GIL) — it recurs across rounds.
- Don't memorize-and-regurgitate: bank questions are detected ("inconclusive" rounds get a fresh problem if they suspect you've seen it).
- Narrate assumptions, interfaces, failure modes, and extension points as you build.

---

## ROLE 2 — APPLIED AI ENGINEER

### What the role is (and isn't)
Anthropic's Applied AI Engineer is their version of a Forward Deployed / solutions engineer — customer-embedded, shipping production Claude deployments at named enterprise accounts. The role sits in go-to-market but is held to engineering quality bars. Reported day-to-day: ~40% prototyping with the Claude API at customer sites, ~30% architecture with customer eng teams, ~30% feeding signal back to product/research. **Not** model training/research. Expects *applied* LLM fluency: prompting, RAG, evals, tool use/MCP, agents — achievable for a non-ML backend engineer.

### Sources
- **getperspective.ai** (detailed 5-stage Applied AI loop, May 2026) — vendor (sells discovery tooling), concrete but self-interested; the "~60% filter" stat is its own survey, unverified.
- **Anthropic Greenhouse/careers** + Deloitte "Anthropic FDE — GPS" posting (real JD requirements).
- **Glassdoor** Applied AI candidate review (opaque-process complaint, useful on what's tested).
- **datainterview.com, dataford.io** (AI Engineer guides) — note datainterview leans ML-heavy (neural-net-from-scratch claims) which applies more to ML Engineer than Applied AI; treat its ML claims cautiously for this role.

### Process (Applied AI; getperspective.ai 5-stage, ~4–6 weeks, 5–10 day gaps)
1. **Recruiter screen (30 min)** — background, motivation, RSP/safety fit check. Generic "I want to work on frontier AI" gets downgraded.
2. **Technical phone screen (60 min)** — practical Python, LLM-adjacent: build a retrieval scorer, a token-budget allocator, or a tool-use orchestrator. Bar: "build something that works and reason about its failure modes." Pragmatic Python + async; don't show off Rust/Haskell.
3. **Take-home / extended live build (3–4 hrs; 1-week window, most submit in 48–72h)** — build a small Claude-powered app against a fictional customer brief. Graded on shipped behavior, API hygiene, and handling ambiguous requirements *without* asking for clarification.
4. **Customer-conversation simulation (60–90 min)** — THE highest-signal round; reportedly filters the majority of those who pass coding. Interviewer plays a buyer (e.g., "VP of Engineering at a 5,000-person fintech evaluating Claude for an internal copilot"); run a ~45-min discovery call.
5. **Virtual onsite (4–5 hrs)** — system design for a multi-tenant Claude deployment (increasingly **eval-harness design**, not RAG architecture), values interview, technical deep dive with a senior engineer, bar-raiser with a cross-functional lead.

### Questions by round (Applied AI)

**Practical/applied coding:** retrieval scorer; token-budget allocator; tool-use orchestrator; "design a product like ChatGPT Playground" (full-stack, streaming, scalable); prompt-iteration exercise in an "Excel-based playground"/Colab (batch-process prompts, analyze outputs systematically); build systems that call LLM APIs efficiently (token management, rate limits, cost models); multi-step reasoning chaining multiple LLM calls.

**System design (applied AI-product):** multi-tenant Claude deployment; **evaluation harness** ("how do you measure whether Claude is actually helping the customer?"); RAG pipeline; content-moderation/safety-filter layer; agent harness (tool schemas, token budgets, prevent prompt injection via tool outputs, human-in-the-loop). Red flags interviewers watch (per system-design coaches): treating the LLM as a source of truth (no grounding/citations), skipping an eval/monitoring plan, defaulting to fine-tuning before trying prompting/RAG/tools.

**Customer-conversation (the differentiator):** see FDE section below — identical skill.

**Values/safety:** RSP familiarity, Constitutional AI at a conceptual level, alignment-vs-capabilities distinction; "generic answers about 'responsible AI' do not pass."

### Deep guidance (Applied AI system design — applied level, not ML research)

**RAG pipeline reference architecture to draw:** ingest → chunk (semantic/overlapping, ~few-hundred tokens) → embed (managed embedding model) → vector store (with metadata for filtering) → at query time: embed query → retrieve top-k → **rerank** → assemble prompt within token budget → Claude → post-process/cite → log. Name failure modes unprompted: "lost in the middle" (long-context degradation), stale index, retrieval misses (add hybrid keyword+vector), hallucination (grounding + citations + "I don't know" fallback), prompt injection from retrieved docs. Trade-offs: RAG vs fine-tuning (RAG for fresh/changing knowledge + citability; fine-tuning for style/format/latency) — "default to prompting → RAG → tools before fine-tuning."

**Evaluation harness (what Anthropic increasingly cares about):** layered evals — (1) cheap automated metrics (exact match/F1 for structured tasks); (2) **LLM-as-judge** (a stronger model grades a weaker one's outputs against a rubric); (3) human review on a sampled slice; plus regression tests on a golden set, online metrics (task success, deflection, latency, cost), and drift monitoring. The interviewer wants you to answer "how do you *know* it's working?" concretely.

**Cost/latency controls:** model tiering (route easy queries to a cheaper/faster model, hard ones to a stronger one), prompt caching, streaming, batching, token budgeting, caching safe/known outputs.

### Tips (Applied AI)
- Actually build something on the Claude API before interviewing (a small RAG app or agent). Anthropic encourages Claude Artifacts for fast prototyping (no API-key/cost overhead).
- For the take-home: ship working behavior and clean API usage; make reasonable assumptions and document them rather than asking for clarification.
- Prepare the customer-conversation as a *research interview*, not a pitch (next section).

---

## ROLE 3 — FORWARD DEPLOYED ENGINEER (FDE)

### What the role is
Per Anthropic's actual JD (Greenhouse): "embed directly with our most strategic customers... ship advanced AI applications that solve real-world business problems," deliver "MCP servers, sub-agents, and agent skills... used in production," provide "white-glove deployment support." Requirements: "3+ years in a technical, customer-facing role such as Forward Deployed Engineer, or a Software Engineer with consulting experience"; "Production experience with LLMs including advanced prompt engineering, agent development, evaluation frameworks, and deployment at scale"; Python proficiency (+ ideally TypeScript/Java); "high agency... navigate ambiguity." A Deloitte-partnered "Anthropic FDE – GPS" posting adds: Claude API/Claude for Enterprise/Claude Code, ~50% travel, US government clearance eligibility for the public-sector variant. Anthropic's FDE = the industry's "Applied AI Engineer"; equivalent to Palantir FDSE / OpenAI Forward Deployed.

### Sources
- **Anthropic Greenhouse JD** + Deloitte GPS posting (primary).
- **getperspective.ai** FDE/Applied AI content (concrete, vendor-biased).
- **Exponent** "Definitive 2026 FDE Guide" + "Decomposition Interview Guide" (June 2026; aggregates Palantir/OpenAI/Anthropic candidate reports) — strong.
- **Prepfully** Palantir Deployment Strategist + FDSE guides (Apr 2026); **Palantir's own** "Navigating Open-Ended Questions" (primary anchor); **datainterview.com** Palantir FDE; **Glassdoor** Palantir FDE (196 reviews).
- *Note:* much FDE interview structure is extrapolated from Palantir/OpenAI because Anthropic FDE-specific public reports are thinner; flagged where so.

### Process (FDE; generic frontier-lab loop, 5–8 stages over 3–6 weeks)
Recruiter screen (30) → Hiring-manager screen (45–60) → Practical coding (60) → System design/architecture (60) → **Decomposition / open-ended case (45–60; the hardest filter)** → **Client-simulation / role-play (45)** → Behavioral/values (45) → (AI labs) take-home build (4–8 hrs). Anthropic's specific FDE loop tracks the Applied AI 5-stage loop above, with the customer-conversation simulation as the highest-signal round.

### Questions by round (FDE)

**Behavioral / motivation (what interviewers listen for in parentheses):**
- "Why FDE, not a regular SWE role?" (connect specific past experience to customer-facing technical work; "consulting but technical" and "I want to work at [famous company]" fail).
- "Tell me about a time you handled a demanding stakeholder." / "deliver bad news to a customer" (delivered early, with options + empathy + a path forward).
- "Describe a complex project you owned 0→1." ("I" not "we"; managers screen aggressively for individual ownership).
- "Tell me about a time you failed." / "a technical decision you reversed" ("I haven't had to reverse one" is a bad answer).
- "Describe your first 30/60/90 days in a new FDE role."
- Calibrated commitments: never overpromise in role-play; "customer trust is built on calibrated commitments."

**Customer-discovery / JTBD questions a strong candidate ASKS the simulated buyer** (the core skill; from getperspective.ai's discovery playbooks):
- *The four layered questions* when a "CTO" says "convince me Claude beats ChatGPT": ask about (1) their current **evaluation criteria** ("how will you judge whether this is good?"), (2) **previous failed AI deployments** ("what did you try before and why didn't it stick?"), (3) **constraints they can't change** — compliance, latency, data residency, (4) the **specific workflow they'd replace**. Take notes, reflect back, *don't open a code editor*.
- *End-user discovery script:* "Walk me through the last time you did X." / "What's the part of this you'd pay someone to do for you?" / "When does the standard process not apply?" (edge cases = hidden eval requirements) / "What systems do you touch daily? Which can't change?"
- *Persona triage* — Executive sponsor: strategic outcomes, success metrics, political constraints. SME/eval owner: "what separates a great output from a passable one? Where do junior people get it wrong?" (give them real outputs to grade). IT/Admin: data-access patterns, audit/SSO, retention. "The Skeptic": "What would have to be true for this to work? Where have similar projects failed here?"

**Decomposition / case-study prompts (reported across FDE loops):**
- "A major city wants to reduce 911 emergency response times. They have call data, traffic data, and ambulance GPS data. You have 60 minutes." (the most-cited FDE prompt)
- "A regional bank wants to unify fraud detection across three legacy systems acquired via M&A; data isn't labeled consistently. Scope the first 90 days."
- "Architect a RAG system for a company's internal wikis."
- "An insurer wants LLM-powered claim summarization across 30M historical claims, subject to state-by-state regulation. How do you scope?"
- "A pharma company wants an AI assistant for researchers to query internal compounds data, with legal/IP/compliance constraints. How do you start?"
- Palantir-style: "How would you use data to reduce opioid/overdose deaths in a mid-sized city?"; "You work for the IRS and need to identify fraudulent activity — how would you build a model?"; "Design a data platform for an enterprise with 500 disparate data sources."

**Coding/system design (FDE):** practical, e.g., "Here's a messy 1GB JSON file — parse, clean, expose a query API"; "design a real-time analytics pipeline"; data-heavy + LLM-app design.

### Deep frameworks (FDE)

**The decomposition framework (the universal rubric — narrate every step):**
1. **Restate & clarify** before solving (most-skipped = most common failure). E.g., "Are we optimizing average, worst-case, or equity of 911 coverage? Different systems."
2. **Define success + hard constraints**; state assumptions out loud ("I'll assume we care about p90 response time").
3. **Map inputs** — what data/systems exist, owner, freshness; ground in real components.
4. **Decompose MECE** into 3–5 workstreams; sequence by risk and value.
5. **Sketch end-to-end "walking skeleton" first, then go deep** (polishing one piece while ignoring the rest = rejection signal); confirm priorities with the interviewer.
6. **Surface trade-offs + iterate** — ≥2 options per key decision compared on cost/latency/complexity/maintainability; name failure modes ("breaks if warehouse data is >24h stale") and graceful degradation.

The 7 scored signals: clarify-first; MECE boundaries; edge cases/failure modes; explicit assumptions; trade-off reasoning (≥2 options); coherent communication under pressure; keep returning to the end user and the decision enabled. The #1 rejection reason everywhere: **jumping to a solution before scoping**; also going silent (narrate continuously), staying abstract, and asserting one "best" answer.

**Client-simulation rewarded patterns:** ownership language; diagnostic questions before solutions; acknowledge what the customer is right about before pushing back; offer options with explicit trade-offs; never promise what you can't deliver. Evaluation literacy ("how do you know it's working?") is the AI-lab-specific differentiator.

### Tips (FDE)
- Treat the customer round like JTBD research, not a demo. Run real discovery: layered questions, take notes, reflect back constraints.
- Prepare concrete, specific examples of the company's actual work/customers — generic interest reads as low effort.
- Have a real evaluation answer ready ("how do you know it's working?").
- Comp note: Anthropic FDE/Applied AI ~$300K–$1.2M TC (most L4–L5 ~$665K–$750K); firm on offers, equity-heavy.

---

## Recommendations

**Stage 0 — Decide fit and target role (now).** If you want maximal coding and least customer-facing work, target **SWE (infrastructure)** — pure-infra/distributed-systems strength with no ML does well on the system-design round. If you enjoy customer interaction and can build on the Claude API, **Applied AI / FDE** is very achievable for a non-ML engineer and pays comparably. Apply via referral if possible (Blind reports referrals materially help and can compress the loop).

**Stage 1 — Coding fluency (2–4 weeks).** Drill the recurring bank in **Python, in a shared editor, under a timer**: in-memory DB (4 levels), multithreaded web crawler (+ asyncio/GIL follow-ups), stack-trace→trace, exclusive-time-from-logs, duplicate files (size→partial→full hash), LRU cache (thread-safe, `*args`/`**kwargs`). Benchmark: finish 4 levels of an in-memory-DB problem in 90 min with all tests green. Practice reading ambiguous specs against your own tests.

**Stage 2 — System design (1–2 weeks).** Be fluent in queues, batching, caching, sharding, rate limiting, retries, fault tolerance, throughput-vs-latency. For Applied AI/FDE, additionally practice RAG pipeline, eval harness, agent/tool design, and cost/latency controls at the applied level. Always name failure modes and tradeoffs unprompted and drive the conversation.

**Stage 3 — Values round (ongoing, start early).** Read "Machines of Loving Grace," "The Adolescence of Technology," "Core Views on AI Safety," the Responsible Scaling Policy, and a Constitutional AI summary; watch one long Dario interview. Form a genuine view — including one or two points of honest disagreement. Prepare 2–3 emotionally real stories about ethical friction. Practice talking about feelings, not just outcomes. Do NOT script STAR answers for this round.

**Stage 4 (Applied AI/FDE only) — Customer-discovery reps (1–2 weeks).** Memorize the layered discovery questions and persona cheat-sheet; do mock buyer role-plays where you ask before pitching, take notes, reflect back constraints (compliance/latency/data residency), and end with a calibrated next step. Have an evaluation answer ready.

**Thresholds that change the plan:** If you can't reliably clear CodeSignal level 3 under time, delay applying and keep drilling — it's an early hard gate. If mock values-round feedback says you sound rehearsed or like a "fanboy," shift to forming genuine opinions and using real emotional examples. If you have no Claude-API project, build one before pursuing Applied AI/FDE.

## Caveats
- **Source reliability varies.** The most reliable: Anthropic's own pages (AI guidance, values, engineering blog), interviewing.io (engineer-sourced), Exponent, Levels.fyi, and first-person dated reports on Glassdoor/1Point3Acres/Medium/Blind. Treat aggregator "question banks" (PracHub, linkjob.ai, aiofferly, dataford, jobright, leetcodewizard, staffengprep, getperspective) as leads to verify — several are SEO/marketing-driven, and some (linkjob.ai, lockedinai.com, ophyai.com) promote AI-cheating tools that violate Anthropic's policy. This guide excluded their tooling advice and used only the questions/process details they report.
- **The "majority filter" on the FDE customer round, the "~60%" figure, and some loop durations are vendor/candidate estimates, not official.** Anthropic publishes no pass-rate data.
- **Process varies by team, level, and time.** Reports conflict on exact round counts (3 vs 5–9 stages), the CodeSignal cutoff (480 vs ~600), and whether there are one or two onsite loops. Anthropic is hiring fast, which both speeds loops and occasionally adds friction.
- **Compensation figures lag the latest funding.** Most Levels.fyi self-reports above were priced against earlier valuations; Anthropic's May 2026 Series H ($65B raised, $965B post-money) likely marks current equity grants higher. Equity is illiquid (private company; liquidity via periodic secondary tenders), so weight the cash component when comparing offers.
- **Coding question bank rotates.** The "duplicate files" question reportedly has "old" and "new" (post-Sep 2025) versions; the in-memory-DB and crawler questions are widely circulated, so interviewers may probe harder or swap problems if they suspect memorization. Anthropic actively works to make evaluations AI-resistant (see its engineering blog on redesigning a take-home that newer Claude models could solve).
- **datainterview.com's ML-heavy claims** (e.g., "implement a neural network from scratch," transformer internals "basically mandatory") apply to the **ML Engineer / Research** tracks, NOT to non-ML SWE or Applied AI/FDE. Do not over-prepare ML theory for the three roles in scope.
- This guide is for **legitimate preparation only**; AI assistance is prohibited in Anthropic's live interviews and take-homes.