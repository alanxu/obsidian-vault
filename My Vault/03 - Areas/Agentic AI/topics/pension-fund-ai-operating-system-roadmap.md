# AI AS THE OPERATING SYSTEM OF THE PENSION FUND

**Roadmap for an enterprise agentic platform on AWS / Amazon Bedrock**

**Audience:** Chief Technology Officer, Technology Leadership, Investment & Enterprise Function Leaders

**Decision objective:** Establish a governed platform that makes AI a first-class interface to knowledge, work, and execution — while preserving fiduciary accountability and deterministic controls for material decisions.

---

> **Provenance.** This is the full contents of `Pension_Fund_Agentic_AI_Operating_System_Roadmap_v2.docx`, with §10 expanded to incorporate the governance elaboration from the source chat thread — material that was never written into the .docx because the file-generation tool was rate-limited. Nothing from either source has been dropped.

---

## Executive Summary

> **North star** — Build the **AI operating system of the fund**: agents do most of the work; people set direction, validate results, gate the decisions that matter, and coach agents to improve; the enterprise owns authority, policy and the systems of record.

**Four directions.**

**1. AI becomes the interface to work.** The AI workspace becomes where work starts, not another application to visit.

- **Ask, investigate, delegate.** Every employee can interrogate the fund's knowledge, run an investigation across systems, and hand off a unit of work — through a single trusted, always-available interface. Long-running and code-executing work runs inside an **isolated, guarded execution sandbox** with no ambient credentials and controlled egress, so an agent's blast radius is bounded by construction rather than by prompt.
- **Grounded in entitled enterprise knowledge**, with sources attached to every material answer. Entitlements are resolved *before* retrieval, never filtered after; provenance travels with the answer into whatever document, model or deck it ends up in.
- **Multi-channel by design** — terminal, browser, chat (`#`-mention), and mobile — over one context and one policy set, so an analyst can start a task at their desk, approve it from a phone, and have the audit trail read as a single session.

**2. Build an AI engineer that works autonomously toward a goal.** The shift from an assistant that answers to a worker that finishes. Four capabilities make it real:

- **Loop engineering.** Build long-running agents inside an explicit envelope — allowed tools, budgets, thresholds, stop conditions and escalation paths — and **make the output verifiable**. The engineering problem is not what the agent says; it is how it knows it is done and how it checks itself. Every loop needs a grader: tests, recomputation, schema validation, or reconciliation against a source of truth. Where no grader exists, we manufacture one before granting autonomy.
- **Graph engineering.** Agents coordinate multi-step workflows and pursue bounded goals automatically and autonomously. Deterministic graph on the outside for durability, resumability, approval seams and audit; agent loops on the inside where judgement is genuinely required. This is what makes a forty-step process survivable — and reconstructable afterwards.
- **Scheduling and event-driven facilities.** Work should start without a human starting it. Heartbeat, cron, hook and goal triggers let agents wake on the events the fund actually runs on — market opens, filings, limit breaches, reconciliation breaks, ticket creation, covenant tests — so monitoring becomes continuous rather than a periodic human sweep.
- **An OpenClaw-class personal agent, self-hosted per employee.** A persisted, personalized assistant that progressively learns and improves for each individual employee — enabling intelligence to emerge at the edge, then be captured, shared and composed into organizational knowledge. It doubles as a highly customizable personal AI workspace that accelerates how quickly individuals develop and deploy their own skills, tools and workflows. Always on and available on mobile, it lifts personal productivity continuously rather than per session. The pitfalls are cost and security.

**3. Unified Agentic Platform.** Build the primitives once, for everyone. Bedrock remains the foundation-model and managed AI control plane, and AgentCore can supply runtime, identity, gateway/tool integration, memory and observability. [1] **The fund retains what it must own: enterprise policy, data contracts, approval authorities and workflow semantics** — that boundary is the difference between leverage and lock-in.

- **Unified model routing.** Approved model catalog, task-based routing across frontier, small and specialist models, version pinning and fallback paths, abstraction layer to decouple agents with the underlying models for easier management and migration. *Challenge:* model upgrades change behaviour without changing the API, and agentic loops multiply cost per request.
- **Context and knowledge.** ACL-aware retrieval, hybrid search and reranking, point-in-time correctness, provenance on every material answer, query rewriting, chunking (semantic, fix-window, hierrachical), knowledge graph for entity lineage. *Challenge:* retrieval crosses security boundaries, semantic similarity is not truth, and structured numbers must be queried rather than retrieved.
- **Harness, runtime and orchestration.** 
	- Support different agentic paradims (react, plan/execution, reflection, multi-agent patterns); 
	- Durable execution with checkpoint and resume, 
	- context and memory management, 
	- human-in-the-loop as a platform primitive. 
	- guardrails
	- *Challenge:* 
		- non-deterministic failures leave partial side effects, and 
		- quality degrades over long horizons without a deliberate context strategy.
- **Tools, skills and MCP.** Typed contracts, idempotency, dry-run, audit metadata; MCP/OpenAPI wrappers over existing enterprise APIs rather than bespoke agent integrations. *Challenge:* Skill explosion and duplication, Prompt/instruction drift and versioning, .
- **Ecosystem and internal marketplace.** Developer SDK, capability registry (tools, mcp, skills, workflows), sandbox, automated certification, permission request, templates, cost attribution, . *Challenge:* skill duplication and drift, and central approval becoming the bottleneck that stalls adoption.
- Reliability. Timeouts, retries, circuit breakers, idempotency, checkpointing, resumable runs, graceful degradation; Challenges Non-deterministic failures and partial side effects
- Evaluation. 
	- Outcome metrics: task success, factuality, citation correctness, retrieval recall/precision, tool success, policy compliance, escalation quality.
	- Operational metrics: latency, token usage, cost per outcome, failure rate, retry count, queue depth, model fallback rate.
	- Agent trajectory tests: evaluate not just final answer but tool sequence, unnecessary actions, budget adherence, stopping behavior and recovery after tool failure.
	- Production observability: trace the full chain from user → model → retrieval → tool → workflow → system-of-record change. AgentCore Observability provides traces, metrics and OpenTelemetry-compatible telemetry for runtime environments.
	- LLM-as-judge

**4. Govern the capability and the action — not merely the model.** An AI control plane enforces identity, policy, approvals, budgets, kill switches and end-to-end lineage at runtime. The governing question is not "is this model approved?" but "what can this agent autonomously cause to happen in the real world?" Autonomy expands only where evaluation, auditability and rollback are stronger than the risk of the action.

- **Permission and access control.** Authority is resolved at runtime as `user ∩ agent ∩ tool ∩ data policy` — an agent never inherits the full permission set of the person who created it. RBAC establishes the baseline; **PBAC** carries the decision, evaluating purpose, data classification, action risk and context on every material call. Guardrails are expressed as **policy-as-code** in a central decision point, not as instructions in a prompt or logic duplicated inside each agent. Every call resolves to allow, deny or require-approval, and the decision is logged with the delegation chain behind it. *Challenge:* identity propagation through the agent → skill → tool chain is not solved at the protocol layer; without it, entitlement is enforced in the wrong place.
- **Cost and FinOps.** Agentic cost is per outcome, not per request, and superlinear — each turn resends context, and an unbounded loop is a financial incident. Budgets, step caps and circuit breakers belong in the runtime; model routing and caching are the primary levers; spend is attributed per agent, skill and team so cost has an owner. The managed metric is **cost per completed task**, not tokens or agents deployed. *Challenge:* an agent-per-employee model makes consumption unpredictable, so unit economics must be instrumented from day one rather than reconstructed after the first bill.

**The rule underneath all of it: separate reasoning from authority — agents reason, recommend and prepare; deterministic systems decide, execute and record.**

The strategy is explicitly *not* to build a single "super agent." It is to build the substrate that every AI experience runs on, so the tenth use case costs a fraction of the first.

| Dimension               | Baseline problem                   | Target state                                                   | Executive metric                             |
| ----------------------- | ---------------------------------- | -------------------------------------------------------------- | -------------------------------------------- |
| Employee leverage       | Search + manual coordination       | AI workspace with grounded answers and task initiation         | % work completed through AI interface        |
| Investment intelligence | Research fragmented across systems | AI analyst layer with source provenance and scenario synthesis | Research cycle time; citation coverage       |
| Operations              | Human handoffs dominate            | Agents orchestrate workflows with deterministic controls       | Straight-through processing; exception rate  |
| Risk & compliance       | Reactive review                    | Continuous AI-assisted monitoring with human sign-off          | Alert precision; review time                 |
| Autonomy                | Scripts / isolated bots            | Goal-driven, bounded agents with policies and stop conditions  | % tasks autonomously completed within SLA    |
| Platform economics      | AI pilots with opaque cost         | Reusable platform + model routing + unit economics             | Cost per task / outcome; platform reuse rate |

> **Three strategic principles**
> 1. Separate reasoning from authority.
> 2. Treat tools and data as governed enterprise capabilities, not prompts.
> 3. Increase autonomy only when evaluation, auditability, and rollback are stronger than the risk of the action.

## Report at a Glance

1. Vision and target operating model
2. Target platform architecture on AWS / Bedrock
3. Comprehensive capability roadmap: 15 platform domains
4. Priority pension-fund use cases across investment and enterprise functions
5. Autonomy ladder and controls for financial / operational actions
6. Evaluation, observability, security, privacy, governance and model risk
7. 24-month roadmap, sequencing, milestones and KPIs
8. Organization, delivery model, investment priorities and executive decisions

---

## 1. Vision: From AI Applications to an AI Operating System

The operating-system metaphor is useful when it means "common execution substrate," not "one AI controls the enterprise." The platform should expose a stable set of capabilities that all AI experiences use: identity, context, knowledge, tools, policies, workflows, memory, evaluation and telemetry. Business applications then become thin experiences over the same governed substrate.

### 1.1 Target user experience

- **Ask:** natural-language interaction for questions, analysis, explanation, scenario exploration and navigation across trusted enterprise knowledge.
- **Work:** the assistant can draft, compare, reconcile, summarize, classify, create tickets, prepare approvals and hand work to deterministic workflows.
- **Act:** the agent can execute pre-authorized actions through governed tools, with explicit checkpoints for material decisions or irreversible changes.
- **Pursue a goal:** the user can give a bounded objective ("monitor covenant exceptions this quarter and escalate material breaches") with a budget, deadline, allowed tools, thresholds and escalation policy.
- **Learn:** the platform retains approved, auditable memory about the user, team, task and prior outcomes without turning raw conversation history into uncontrolled institutional memory.

### 1.2 What remains non-negotiably deterministic

- Trades, cash movements, accounting postings, payment instructions, legal commitments, material beneficiary decisions and regulated submissions should execute through deterministic systems and controls; AI may recommend, prepare or route them.
- Authorization must derive from enterprise identity, role, entitlements, transaction limits and policy — never from the model's interpretation of a prompt.
- Every material agent action must be attributable to a human or service principal, its policy decision, the exact tool version, relevant inputs, and the resulting system-of-record change.

---

## 2. Target Architecture

A five-plane architecture separates concerns and creates clear security / reliability boundaries. The design is intentionally compatible with AWS managed services while preserving portability at the application boundary.

| Plane | Responsibilities | Representative AWS / platform components |
|---|---|---|
| **Experience plane** | Employee workspace; role-specific copilots; APIs; Teams/web/mobile; workflow inbox | Web app / portal, enterprise SSO, API gateway, collaboration integrations |
| **Agent control plane** | Agent lifecycle, routing, planning, policies, tool registry, memory, evaluation, observability | Amazon Bedrock, Bedrock Guardrails, AgentCore Runtime / Gateway / Identity / Memory / Observability, orchestration framework |
| **Knowledge & data plane** | Enterprise search, structured analytics, unstructured content, graph, metadata, data quality, entitlements | Lakehouse / warehouse, S3, Bedrock Knowledge Bases, vector + keyword retrieval, knowledge graph / Neptune where justified |
| **Action & workflow plane** | Business APIs, deterministic workflows, approvals, human-in-the-loop, transactions, eventing | API Gateway, Lambda/ECS, Step Functions / workflow engine, EventBridge, service APIs, approval service |
| **Trust & platform plane** | IAM, secrets, network isolation, audit, privacy, records, evaluation, FinOps, SDLC | IAM/Identity, KMS, CloudTrail, CloudWatch, centralized logging, policy engine, CI/CD, model registry |

> **Architecture rule** — The agent is not the system of record. It is a policy-constrained reasoning and coordination layer over systems of record and deterministic workflow engines.

---

## 3. Model Foundation and Model Routing

The platform should optimize for business outcomes, not for one "best model." Bedrock provides the managed model access layer; the application should add a model-routing abstraction so agents can select among frontier, smaller, specialized and embedding/reranking models based on task, latency, sensitivity, cost and reliability.

- Create a model catalog with approved model versions, capabilities, regions, data-handling constraints, benchmark scores and cost characteristics.
- Use task-based routing: small/fast models for classification, extraction and simple tool selection; stronger reasoning models for investment synthesis, complex research and multi-step planning; specialized models for embeddings, reranking, parsing and document understanding.
- Pin critical workloads to versioned model configurations. Treat model upgrades as production changes requiring regression evaluation, cost comparison and risk review.
- Use inference profiles / cross-Region patterns where appropriate for throughput, cost and resilience; AWS documents inference profiles as a way to track cost/metrics and distribute inference across Regions. [2]
- Design for fallback: if the preferred model fails, degrade to an approved fallback or return "cannot complete safely" rather than improvising.

### Challenges

- Model behavior changes without API changes; model upgrades can silently change tool selection, reasoning style or extraction accuracy.
- Latency and cost vary by model and reasoning depth. Agentic workloads can amplify cost because one user request may create many model/tool calls.
- Benchmarking is multidimensional: accuracy alone is insufficient; require business success, policy compliance, citation quality, latency, cost and failure recovery metrics.

---

## 4. Enterprise Knowledge and Context

Enterprise knowledge is the core substrate of an AI operating system. Treat ingestion, authorization, freshness and provenance as first-class platform services. Bedrock Knowledge Bases supports retrieval, citations, reranking, multimodal content and structured-data access; current AWS guidance also highlights agentic retrieval that can decompose complex queries and iterate on retrieval. [3]

| Capability | Best practices | Key challenges |
|---|---|---|
| **Document ingestion** | Canonical source registry; versioning; chunking by semantic boundaries; metadata; ACL propagation; OCR/vision parsing for tables/charts; freshness SLAs | Broken layouts; duplicate versions; stale documents; ACL mismatch; hidden tables / spreadsheet logic |
| **Retrieval** | Hybrid retrieval; reranking; query rewriting/decomposition; domain-specific indexes; filters by authority/date/portfolio/entity | High recall can reduce precision; semantic similarity is not truth; retrieval can cross security boundaries |
| **Structured data** | Expose governed query services rather than embedding numeric truth; semantic layer for portfolio/ledger concepts; validation against source systems | Schema drift; ambiguous business definitions; point-in-time consistency; double counting |
| **Knowledge graph** | Use graph for entities, relationships, lineage and "who/what is connected" questions; combine with vector/keyword retrieval | Graph maintenance; ontology disputes; noisy relationships; query planning complexity |
| **Provenance** | Every material answer carries source identifiers, timestamps, data lineage and confidence/coverage signals | Citations can prove where a claim came from, not that the claim is correct |

> **Important Bedrock nuance** — Bedrock Guardrails do not automatically protect the raw reference material retrieved from a Knowledge Base at runtime. Apply authorization and data filtering before retrieval, and treat retrieval results as sensitive data. [4]

---

## 5. Identity, Security and Entitlements

Agent identity is fundamentally different from application authentication. An agent must have a durable, auditable identity plus a constrained set of capabilities. AWS AgentCore Identity is designed to manage identities and credentials for agents and automated workloads, including access to AWS resources and third-party services. [5]

- Use user identity + agent identity + tool identity; never collapse them into a shared service account.
- Use least privilege, short-lived credentials and scoped delegation. Production IAM policies should be purpose-built rather than broad development policies; AWS explicitly warns that development-oriented AgentCore CLI policies are not appropriate for production. [6]
- Propagate entitlements to retrieval: an agent should never retrieve a document the user could not access directly, unless an explicit service-level authority authorizes it.
- Create action risk tiers: read-only; reversible write; business-impacting write; irreversible / regulated action. Map each tier to approval, transaction limits, dual control and logging requirements.
- Protect against prompt injection and data exfiltration using layered controls: input filtering, tool allowlists, output inspection, secret isolation, egress controls and policy enforcement outside the model. Bedrock Guardrails supports prompt-attack filtering and configurable content / topic controls. [7][8]

### Challenges

- "The agent can read everything because the user can" is often false once agents act on shared service credentials. Build explicit delegation semantics.
- Tool descriptions themselves are attack surfaces. Treat tools, schemas and external content as untrusted inputs to planning.
- Human approval UI becomes a control boundary: the user must understand what will happen, which data will be used, what will change and what the agent recommends.

---

## 6. Tool and Action Plane

Tools are the agent's hands. Standardize them as reusable enterprise capabilities, not ad-hoc functions hidden inside prompts. Prefer existing APIs and deterministic services; wrap them with consistent schemas, authorization, idempotency and audit metadata. Bedrock AgentCore Gateway can centralize access to tools and backend targets and provide authentication / observability around agent-to-service calls. [9]

### 6.1 Developer Ecosystem: Make the Platform a Fund-Wide AI Factory

The platform should not only run agents built by a central AI team. It should become a governed internal ecosystem in which investment, risk, operations, technology and corporate teams can build reusable skills, tools and workflows without rebuilding infrastructure. The central platform team owns the paved road; domain teams own business capabilities and outcomes.

The design principle is to separate what a developer creates from what the platform governs. A developer should be able to package a skill or tool with a standard SDK, test it locally, publish it to a registry, request permissions, pass automated security/evaluation checks, and promote it through environments. **The safe path should be the easiest path.**

### 6.2 Standardize the Building Blocks

| Building block | What developers create | Platform contract | Pension-fund examples |
|---|---|---|---|
| **Tool** | Bounded callable capability with typed input/output | Schema, auth, authorization scope, timeout, idempotency, audit metadata, owner, SLA | Portfolio lookup; risk calculation; market-data query; document retrieval; ticket creation |
| **Skill** | Reusable instructions + decision procedure + tool composition | Manifest, inputs/outputs, allowed tools, policy constraints, eval suite, version, owner | Investment memo drafting; manager due diligence; earnings analysis; incident triage |
| **Workflow** | Deterministic or hybrid multi-step process | State model, retries, approvals, compensation, observability, SLA, human checkpoints | Quarterly valuation review; onboarding; compliance review; reporting package |
| **Agent** | Goal-directed application selecting skills/tools | Agent identity, model policy, tool allow-list, autonomy tier, memory policy, evals | Research assistant; operations agent; technology support agent |
| **Policy** | Machine-enforceable guardrail | Versioned rules evaluated at runtime with deny/approve semantics | Trading limits; data entitlements; segregation of duties; approval thresholds |

**Recommended ecosystem capabilities**

- **Developer SDK and templates:** Python/TypeScript libraries, CLI tooling, local emulators, standard manifests, typed tool schemas, tracing hooks and test harnesses. Developers should not need to understand the underlying Bedrock orchestration internals.
- **Skill and tool registry:** searchable catalog containing owner, description, version, dependencies, data classifications, permissions, evaluation results, SLA, cost profile, usage and lifecycle status. Skills/tools become first-class software assets.
- **Discovery and semantic routing:** registry metadata is exposed to agents so they can discover the right capability at runtime. Use explicit descriptions, examples and typed schemas rather than prompt text alone.
- **MCP/OpenAPI integration layer:** support open standards where useful so existing enterprise APIs and internal tools can be wrapped without proprietary agent-specific implementations. MCP is an integration option; governance remains a platform responsibility.
- **Sandbox and developer environments:** isolated environments with synthetic/masked data, restricted credentials and deterministic fixtures. Developers can test behavior before production access.
- **CI/CD and promotion pipeline:** linting, schema validation, unit tests, agent evaluations, security scanning, dependency scanning, prompt/instruction checks and policy validation before promotion.
- **Certification and trust tiers:** classify capabilities as experimental, team-approved, enterprise-approved and production-critical. Higher-risk tools require stronger evidence, ownership and approval.
- **Versioning and compatibility:** independently version tool schemas, skills, prompts/instructions, policies and workflows. Support compatibility, deprecation windows, rollback and pinning.
- **Permission broker:** bind every invocation to user, agent identity, purpose, data classification and requested action. Prefer short-lived, least-privilege credentials and runtime policy decisions.
- **Runtime governance:** enforce allow-lists, rate limits, budgets, DLP, data-residency rules, approval gates and maximum autonomy at runtime.
- **Evaluation service:** every published skill has a domain-specific eval suite covering correctness, grounding, tool selection, policy adherence and failure behavior. Production skills continuously collect regression cases.
- **Observability and lineage:** trace user → agent → skill → tool → data → model → action, including versions and policy decisions. This is essential for audit, incident investigation and model-risk management.
- **Usage and chargeback:** measure invocations, latency, model/tool cost and business value by team/capability. This enables FinOps and prevents uncontrolled agent proliferation.
- **Internal marketplace/catalog:** search, compare, request access, subscribe to approved skills and see documentation/evaluation status. Reuse should be visible.
- **Ownership and support:** every production capability has a business owner, technical owner, risk classification, support contact and review/retirement date. No orphaned production skill or tool.

### 6.3 Lifecycle: Build → Certify → Publish → Compose → Observe → Improve

A two-speed operating model is recommended. Domain teams move quickly inside a governed sandbox, while the central AI platform provides reusable infrastructure and controls. A capability becomes enterprise-grade only after passing automated and, where appropriate, human certification.

| Lifecycle stage | Platform responsibility |
|---|---|
| **Build** | SDK/templates, approved data access, local testing and standard telemetry. |
| **Certify** | Automated security, privacy, policy, reliability and domain-evaluation gates; human review for high-risk capabilities. |
| **Publish** | Registry metadata, ownership, permissions, dependencies, cost and trust tier. |
| **Compose** | Discovery and reuse through registry APIs, semantic search and governed composition. |
| **Observe** | Runtime traces, outcomes, policy decisions, cost, latency and user feedback. |
| **Improve** | Convert failures into regression tests; evaluate new versions and retain rollback. |

**Important architectural distinction:** a skill is not simply a prompt stored in a database. In a production platform it should be a versioned, testable, discoverable software artifact with explicit capabilities, dependencies, permissions and measurable behavior.

### 6.4 Ecosystem Governance Challenges

- **Skill explosion and duplication:** dozens of teams may create similar capabilities. Registry metadata, ownership and reuse analytics are needed to consolidate them.
- **Prompt/instruction drift:** changing a skill can change downstream agent behavior even when its API is unchanged. Treat behavioral changes as release events and run regression evaluations.
- **Composability versus safety:** free composition increases emergent behavior. Enforce capability boundaries and maximum autonomy at the agent/session level.
- **Supply-chain risk:** skills depend on code, packages, APIs, prompts, models and data. Apply dependency pinning, provenance, scanning and release controls.
- **Hidden privilege escalation:** a low-risk skill can become high-risk when combined with a powerful tool. Authorization must evaluate the effective action, not only the skill label.
- **Evaluation portability:** a skill that works for one investment team may fail in another context. Maintain generic platform evaluations plus domain-specific evaluations.
- **Central-platform bottleneck:** if every capability requires manual approval, adoption will stall. Automate low-risk certification and reserve human review for high-impact capabilities.
- **Vendor coupling:** Bedrock can remain the infrastructure foundation while skill/tool contracts stay model- and vendor-portable where practical.

### 6.5 Recommended Platform Products for Fund Developers

- **AI Developer Portal** — documentation, catalog, templates, examples, access requests, ownership and certification status.
- **Agent/Skill SDK** — standard APIs, manifests, tracing, tool invocation, memory access and evaluation hooks.
- **Capability Registry** — source of truth for skills, tools, workflows, agents, policies, versions and dependencies.
- **AI Control Plane** — lifecycle, approvals, policy configuration, model routing, environment promotion and kill switches.
- **Agent Runtime** — execution, orchestration, state, retries, budgets, timeouts, concurrency and human-in-the-loop controls.
- **Evaluation Platform** — offline benchmark suites, scenario tests, red teaming, regression testing and production-quality monitoring.
- **Tool Gateway** — secure access to enterprise APIs, databases and external services with centralized authorization and audit.
- **AI Observability Platform** — end-to-end traces, quality metrics, policy events, cost, latency and business outcomes.

### 6.6 Ecosystem Roadmap

- **0–90 days:** publish SDK/manifest standard, initial tool registry, developer sandbox, 3–5 reference skills, CI evaluation gates and ownership model.
- **3–6 months:** launch the internal AI developer portal, semantic capability discovery, automated certification for low-risk skills, tool gateway and production tracing.
- **6–12 months:** enable cross-domain skill reuse, versioned workflow packages, policy-as-code, trust tiers, cost attribution and continuous regression evaluation.
- **12–24 months:** mature into an internal AI marketplace with composable capabilities, self-service promotion, automated governance and portfolio-level optimization based on business outcomes.

### 6.7 Tool Design Rules

| Design rule          | Best practice                                                                           | Failure mode to prevent                        |
| -------------------- | --------------------------------------------------------------------------------------- | ---------------------------------------------- |
| **Contract**         | OpenAPI / MCP-like schemas; explicit inputs, outputs, errors, permissions, side effects | Agent guesses API semantics                    |
| **Idempotency**      | Idempotency key on writes; safe retries; transaction status lookup                      | Duplicate trades / payments / tickets          |
| **Validation**       | Schema + business rule validation before execution                                      | LLM-generated invalid parameters               |
| **Dry run**          | Support preview / simulation before commit                                              | Unexpected irreversible action                 |
| **Audit**            | Capture caller, agent, tool version, policy decision, input hash, result and record ID  | No reconstructable evidence                    |
| **Rate / budget**    | Per-agent and per-user quotas, spend/time budgets                                       | Runaway loops and cost explosions              |
| **Human escalation** | Tool returns structured "approval required" outcome                                     | Agent bypasses approval through alternate path |

---

## 7. Agent Runtime and Orchestration

Separate three patterns: deterministic workflows, agentic workflows and general-purpose goal agents. Use the least agentic pattern that solves the problem. Bedrock supports managed agents and multi-agent collaboration; AWS guidance emphasizes clearly defined supervisor/collaborator roles and minimizing overlapping responsibilities. [10]

| Pattern                            | When to use                                                                             | Recommended control                                                                    |
| ---------------------------------- | --------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **Deterministic workflow**         | Known steps, regulated process, predictable branching                                   | Workflow engine; explicit state transitions; zero free-form planning in critical steps |
| **Agentic workflow**               | Known outcome, but reasoning is required to select documents, tools or route exceptions | State machine + LLM decisions bounded by schemas and policy                            |
| **Supervisor / specialist agents** | Distinct domains need specialized context or tools                                      | Clear domain boundaries, budgets, contracts, shared observability                      |
| **General goal agent**             | Open-ended investigation or bounded operational monitoring                              | Goal spec + constraints + stop conditions + budget + escalation + evidence log         |

> **Best practice** — Do not use multi-agent orchestration to compensate for poor tool contracts or poor data access. More agents generally increase latency, cost, coordination risk and evaluation complexity.

---

## 8. Memory and Personalization

Memory should be designed as a tiered, policy-controlled capability: session context, task memory, durable user/team preferences, and institutional knowledge. Bedrock AgentCore Memory supports short-term event history and long-term memory strategies, including semantic, summary, preference and episodic patterns. [11]

- Store durable facts only when they have an owner, source, freshness expectation and deletion / correction path.
- Differentiate "remembered by the agent" from "authoritative enterprise data." The latter must remain in systems of record.
- Use actor / user scoping and tenant boundaries; never let one employee's memory become another employee's context without explicit policy.
- Apply retention schedules and privacy controls to memory; treat agent memory as potentially sensitive business data.
- Use summaries and structured memories to control context growth rather than replaying entire histories.

> **Challenge** — Memory can create "sticky hallucinations": an early wrong statement becomes a durable fact and influences future reasoning. Memory writes should be more conservative than memory reads.

---

## 9. Goal-Driven Autonomy and Work Execution

Autonomy is the strategic differentiator, but also the highest-risk capability. The platform should introduce an explicit "goal object" rather than passing free-form goals directly to an agent. A goal object includes objective, scope, data sources, allowed tools, constraints, budget, time window, materiality threshold, approval policy, stop conditions, evidence requirements and escalation contacts.

| Autonomy level | Example | Minimum control |
|---|---|---|
| **L0 — Answer** | "What is the current exposure to X?" | Grounded retrieval + citations |
| **L1 — Recommend** | "Which managers merit deeper diligence?" | Evidence + rationale + human decision |
| **L2 — Prepare** | "Prepare a rebalancing proposal." | Simulation / draft only; no commit |
| **L3 — Execute with approval** | "Prepare and route the trade." | Policy check + human approval + deterministic execution |
| **L4 — Bounded autonomous execution** | "Monitor and remediate pre-defined operational exceptions." | Explicit policy, quotas, stop conditions, rollback, continuous monitoring |
| **L5 — Strategic autonomy** | "Optimize the portfolio toward a multi-year objective." | Not recommended as a direct execution mode; use AI for scenario generation and decision support |

> **Pension-fund guardrail** — For material investment, fiduciary, beneficiary, legal or cash decisions, the default mode should remain human-governed. The platform can autonomously perform surveillance, data preparation, reconciliation, routing and other bounded actions where the policy envelope is objectively testable.

---

## 10. AI Governance, Model Risk and Responsible AI

Governance should be embedded into the platform, not a review committee that manually approves every agent. The policy engine should know what an agent is allowed to do; evaluation gates should determine what model/tool versions are deployable; audit must make outcomes reconstructable.

For a pension fund, AI governance should be designed as a **technical control system**, not primarily as a committee or approval process. The key question is:

> How do we allow hundreds of people and eventually thousands of AI agents to build and use AI capabilities, while ensuring that every AI action is authorized, explainable, auditable, reversible, and within the fund's risk appetite?

Governance should therefore be a first-class layer of the AI Operating System.

### 10.1 Control domains and required evidence

| Control domain              | Best practice                                                                                       | Evidence / artifact                               |
| --------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------------------- |
| **Use-case classification** | Risk-tier every AI capability based on impact, autonomy, data sensitivity and reversibility         | AI use-case register + risk tier                  |
| **Model risk**              | Independent challenge for material models; benchmark on fund-specific tasks; monitor drift          | Model card + validation report + release approval |
| **Human oversight**         | Define meaningful oversight, not ceremonial approval; allow reject / modify / override              | Approval record + exception metrics               |
| **Explainability**          | Provide evidence, sources, assumptions, policy checks and decision trace where relevant             | Trace + citations + explanation packet            |
| **Privacy**                 | Privacy-by-design, purpose limitation, minimization, transparency, correction/deletion paths        | PIA / privacy assessment + data map               |
| **Third-party risk**        | Assess model/provider, data residency, retention, security, resilience and exit strategy            | Vendor risk assessment + contractual controls     |
| **Incident management**     | Treat AI failures like operational incidents with severity, containment, root cause and remediation | Incident record + postmortem                      |

### 10.2 Regulatory alignment

For a Canadian pension context, the governance model should be aligned to the fund's specific legal and regulatory perimeter. OSFI has highlighted frontier AI as an evolving technology / cyber / operational-resilience risk and explicitly points to technology, operational resilience and third-party risk disciplines. [12] Canada's Privacy Commissioner also recommends privacy-by-design, transparency, explainability and limiting the sharing of personal or confidential information in generative-AI deployments. [13] NIST AI RMF and its Generative AI Profile provide a useful cross-sector governance vocabulary covering trustworthy AI risk management. [14]

### 10.3 The governance model — six layers

```
        ┌─────────────────────────────┐
        │      AI Governance          │
        │  Risk appetite / policies   │
        │  Standards / accountability │
        └──────────────┬──────────────┘
                       │
        ┌──────────────▼───────────────┐
        │      AI Control Plane        │
        │  Policy engine               │
        │  Identity / authorization    │
        │  Approval / autonomy controls│
        │  Registry / lifecycle        │
        └──────────────┬───────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
┌───▼──────┐   ┌───────▼────────┐   ┌─────▼──────────┐
│ AI/Agent │   │ Skills / Tools │   │ Knowledge/Data │
│ Runtime  │   │  Governance    │   │  Governance    │
└───┬──────┘   └───────┬────────┘   └─────┬──────────┘
    │                  │                  │
    └──────────────────┼──────────────────┘
                       │
        ┌──────────────▼───────────────┐
        │      Audit / Evidence        │
        │ Full action + decision trail │
        └──────────────────────────────┘
```

The important idea is that **governance policies are enforced by the platform**, rather than asking developers or users to remember a hundred rules.

### 10.4 Governance should govern four different things

A common mistake is to treat "AI governance" as one thing. For an agentic platform, there are four distinct governance objects.

**A. The AI model.** Examples: Claude, Amazon Bedrock models, OpenAI models, embedding models, reasoning models. Govern:

- which models can be used
- which data classifications can reach each model
- geographic/data-residency restrictions
- model version
- model risk rating
- approved use cases
- performance/evaluation requirements
- cost limits

**B. The AI application / agent.** For example, the Investment Research Agent. Govern:

- who owns it
- what it is allowed to do
- which models it can use
- which tools it can call
- what data it can access
- autonomy level
- maximum execution budget
- memory policy
- human approval requirements

**C. Skills and tools.** This is particularly important for the ecosystem concept in §6.

```
Investment Research Agent
│
├── Earnings Analysis Skill
│   ├── SEC/filing retrieval tool
│   ├── Market data tool
│   └── Research database tool
│
├── Portfolio Analysis Skill
│   ├── Portfolio DB
│   └── Risk Engine
│
└── Report Generation Skill
    └── Document system
```

The governance problem isn't just *"Is the Investment Agent approved?"* It is: **"What can every component underneath this agent actually do?"** A seemingly harmless skill could become dangerous if it can invoke a powerful tool.

**D. The action.** This is the most important level for autonomy.

| Action | Risk |
|---|---|
| Read public research | Low |
| Search internal documents | Low |
| Summarize portfolio | Low |
| Draft investment memo | Medium |
| Modify internal analysis | Medium |
| Create purchase order | High |
| Send external communication | High |
| Modify portfolio | Very high |
| Execute trade | Very high |

Governance should therefore ultimately answer:

> "Is this particular action allowed for this particular agent, for this particular user, against this particular resource, at this particular moment?"

### 10.5 AI Capability Risk Tiers

**Tier 0 — Informational.** AI only provides information. Examples: summarize documents, answer questions, search knowledge, explain policies. No external side effects. Autonomy: unrestricted within data permissions.

**Tier 1 — Assistive.** AI prepares work for a human. Examples: draft investment memo, prepare manager review, prepare compliance report, analyze portfolio exposure, prepare meeting package. Human must approve the result. Autonomy: prepare, but don't execute.

**Tier 2 — Controlled execution.** AI can execute bounded actions after explicit approval.

```
Agent:
"I found three exceptions.
 I recommend closing tickets A, B and C."

Human:
Approve

Agent:
→ closes tickets
→ records evidence
```

**Tier 3 — Bounded autonomy.** The agent can execute without asking every time, but only within predefined boundaries. For example:

> "You may resolve operational tickets classified as P3 or lower, provided no production configuration changes are required."

This is where meaningful agentic automation begins.

**Tier 4 — High-impact autonomous action.** Examples: investment decisions, trading, material financial commitments, changes to regulatory reporting, changes to critical infrastructure. These should normally require explicit human authorization, potentially with segregation-of-duties controls.

> **Relationship to the §9 autonomy ladder** — The L0–L5 ladder in §9 describes what the *agent is asked to do*; the Tier 0–4 classification here describes what the *capability is permitted to cause*. They are complementary: L0–L1 map to Tier 0–1, L2 to Tier 1–2, L3 to Tier 2, L4 to Tier 3, and L5 sits above Tier 4 and is not recommended as a direct execution mode. Register each capability against both.

### 10.6 Governance should be expressed as policy-as-code

This is one of the most important architectural recommendations. Don't implement *"Agents should not trade without approval"* as a document. Implement it as an enforceable platform policy.

```
IF
  agent.action == "execute_trade"
AND
  approval.status != "approved"
THEN
  DENY
```

```
IF
  data.classification == "restricted"
AND
  model.provider NOT IN approved_models
THEN
  DENY
```

```
IF
  agent.autonomy_level >= HIGH
AND
  action.risk_level >= MATERIAL
THEN
  REQUIRE human approval
```

The platform becomes the enforcement point.

### 10.7 The Policy Decision Point

Introduce a centralized **AI Policy Engine**. Every important agent action goes through it.

```
        Agent
          │
          │ "Call Portfolio DB"
          ▼
┌──────────────────────┐
│   AI Policy Engine   │
│                      │
│  Who?                │
│  Agent?              │
│  User?               │
│  What action?        │
│  What data?          │
│  What environment?   │
│  Risk level?         │
│  Approval required?  │
└──────────┬───────────┘
           │
   ALLOW / DENY /
   REQUIRE APPROVAL
           │
           ▼
     Tool Gateway
           │
           ▼
     Enterprise API
```

This is fundamentally different from putting authorization logic inside every agent.

### 10.8 Agent identity becomes critical

Every agent should have its own identity.

```
User:   john.smith
Agent:  investment-research-agent-prod
Skill:  portfolio-analysis-v3
Tool:   portfolio-read-api
```

The platform records the chain:

```
John Smith
   ↓
Investment Research Agent
   ↓
Portfolio Analysis Skill
   ↓
Portfolio Read Tool
   ↓
Portfolio Database
```

This gives end-to-end accountability. You don't want audit logs saying *"API called by AI."* You want: **John Smith → Investment Research Agent v4 → Portfolio Analysis Skill v3 → Portfolio API → Portfolio XYZ.**

### 10.9 Separate user permissions from agent permissions

Suppose a user has access to portfolio data. That doesn't automatically mean an agent they create should have unrestricted access to everything they can access. Use:

```
User identity ∩ Agent identity ∩ Tool permission ∩ Data policy
```

For example:

```
User:          Investment Analyst
Agent:         Research Agent
Allowed data:  Investment Research + Portfolio Data
Allowed actions: READ

Not allowed:
  Trade execution
  Portfolio modification
  External communication
```

This prevents the common problem of *"the agent inherited the user's entire permission set."* It is the enforcement mechanism behind the delegation-semantics warning in §5.

### 10.10 Skill governance

This becomes particularly important once the whole fund can build skills. Every skill should have a manifest.

```yaml
name: manager-due-diligence
version: 2.3.0

owner:
  business: Private Equity
  technical: AI Platform

risk:
  tier: 2

data:
  classifications:
    - confidential

tools:
  allowed:
    - manager-database-read
    - document-search

actions:
  external_write: false
  financial_transaction: false

human_approval:
  required: true

evaluation:
  benchmark: manager-dd-v4
```

The registry described in §6.2 thereby becomes the **AI software bill of materials** for the fund.

### 10.11 The dangerous problem: capability composition

This is one of the biggest challenges that traditional application governance doesn't fully address. Suppose:

- **Skill A** — Analyze portfolio. Low risk.
- **Tool B** — Send email. Medium risk.
- **Tool C** — Create transaction. High risk.

Individually: A = safe, B = moderate, C = high. But an agent that can combine **A + B + C** may become extremely powerful.

Therefore: **risk must be evaluated on the effective capability of the composition, not merely individual components.** This is the mechanism behind the "hidden privilege escalation" challenge named in §6.4.

The platform should calculate something like:

```
Agent effective capability
=
  Model capability
+ Data access
+ Skill access
+ Tool access
+ Autonomy level
```

### 10.12 Human-in-the-loop should be a platform primitive

Don't implement approval separately inside every workflow. Make it a native platform capability.

```
Agent
  ↓
Generate recommendation
  ↓
Risk engine
  ↓
Approval required
  ↓
Human approval UI
  ↓
Policy engine
  ↓
Tool execution
```

The approval event should itself be auditable:

```
Who approved?
What did they approve?
What information did they see?
What version of the agent generated it?
What version of the skill?
What data was used?
When?
```

This becomes especially important for investment and regulatory processes.

### 10.13 Governance needs an evidence trail

For every material agent action, capture:

```
User
Agent
Agent version
Skill version
Tool version
Model
Model version
Prompt/instruction version
Input data references
Retrieved documents
Policy decisions
Human approvals
Tool calls
Outputs
External actions
Timestamp
Cost
Outcome
```

This creates an **AI lineage graph**. For a pension fund, treat it as a first-class platform capability rather than ordinary application logging.

### 10.14 Don't attempt to audit "chain of thought"

There is an important distinction. The fund needs to know: *why was an action permitted and what evidence supported it?* It does **not** necessarily need to store the model's private reasoning trace.

Instead capture decision evidence:

```
Recommendation:
  Reduce exposure to X

Evidence:
  - Portfolio exposure report
  - Risk model output
  - Research documents A/B/C

Policy:
  Investment recommendation policy v7

Agent:
  Investment Research Agent v4

Human:
  Investment manager approved
```

This gives useful auditability without making internal model reasoning the system of record.

### 10.15 Change management

Agentic systems introduce a new problem: **software can change behavior without changing the API.** For example:

```
Agent v1        →      Agent v1
Model A                Model A v2
Skill v3               Skill v3
Prompt v7              Prompt v7
```

The application version hasn't changed, but behavior may have changed significantly. Therefore model, skill, prompt/spec, tool and policy versions should all be tracked. A production deployment should look more like:

```
Agent
├── Model version
├── System spec version
├── Skill versions
├── Tool versions
├── Policy versions
├── Knowledge index version
└── Evaluation version
```

### 10.16 Certification before production

Create an **AI Capability Certification Pipeline**.

```
Developer
   ↓
Build
   ↓
Unit tests
   ↓
Security scan
   ↓
Data/privacy check
   ↓
Agent evaluation
   ↓
Policy evaluation
   ↓
Red-team tests
   ↓
Risk classification
   ↓
Business owner approval
   ↓
Production
```

Most of this can be automated. You don't want a governance team manually reviewing every low-risk summarization skill — see the central-platform-bottleneck challenge in §6.4.

### 10.17 Continuous governance

Certification shouldn't happen once.

```
Skill certified
   ↓
Production
   ↓
Continuous monitoring
   ↓
New failure detected
   ↓
Regression test created
   ↓
Evaluation fails
   ↓
Capability automatically quarantined
```

This makes governance **runtime + continuous**, rather than annual compliance.

### 10.18 Kill switches and circuit breakers

Every autonomous agent should have platform-level controls for:

- stop agent
- disable skill
- disable tool
- revoke credentials
- disable model
- disable workflow
- impose spending limit
- impose invocation limit
- require human approval

For example:

```
Agent
  ↓
100 failed tool calls in 5 minutes
  ↓
Circuit breaker
  ↓
Agent suspended
  ↓
Security/Operations notified
```

This is essential once agents operate autonomously.

### 10.19 Autonomy contracts for autonomous agents

Introduce an explicit **Autonomy Contract**. Every production agent declares:

```
Objective
Allowed actions
Forbidden actions
Maximum duration
Maximum cost
Maximum number of iterations
Maximum financial impact
Allowed data
Allowed tools
Required approvals
Escalation conditions
Termination conditions
```

For example:

```
Operations Agent

Objective:
  Resolve operational incidents.

Allowed:
  - Read monitoring data
  - Search runbooks
  - Restart approved services

Forbidden:
  - Modify production configuration

Autonomy:
  Tier 3

Budget:
  $20 / incident

Escalation:
  P1/P2 incidents

Termination:
  30 minutes
  or 20 tool calls
```

This is much safer than *"Agent, solve the incident."* The Autonomy Contract is the runtime expression of the goal object in §9 and the policy schema in Appendix B.

### 10.20 Governance organization

Do **not** create one giant AI governance committee that approves everything. Instead:

**AI Platform Team** owns: runtime, control plane, registry, SDK, policy engine, observability, evaluation platform, developer experience.

**Domain AI Owners** (Investment, Risk, Operations, Finance, HR, etc.) own: skills, workflows, domain evaluations, business outcomes.

**Risk / Compliance** own: risk framework, materiality thresholds, regulatory requirements, independent challenge.

**Cybersecurity** owns: identity, secrets, threat modeling, supply chain, data leakage, adversarial testing.

**Enterprise Architecture** owns: architectural standards, integration patterns, technology lifecycle.

**Internal Audit** provides independent assurance.

The critical principle is: **centralize controls; decentralize innovation.** See §16 for the full staffing pattern.

### 10.21 Governance should become progressively stricter

Think of it as a pyramid:

```
              HIGH RISK
                  ▲
                  │
          Human approval
          Risk committee
          Strong evidence
                  │
        ─────────────────────
                  │
              Tier 3
        Bounded autonomy
                  │
        ─────────────────────
                  │
              Tier 2
      Controlled execution
                  │
        ─────────────────────
                  │
              Tier 1
          AI assistance
                  │
        ─────────────────────
                  │
              Tier 0
        Information only
                  ▼
              LOW RISK
```

This avoids the mistake of applying Tier-4 governance to every chatbot.

### 10.22 The most important governance principle for the CTO

> **Govern the capability and the action — not merely the model.**

Traditional AI governance tends to ask:

> "Is this model approved?"

Agentic AI requires asking:

> "What can this agent do?"

And ultimately:

> "What can this agent autonomously cause to happen in the real world?"

That shift is fundamental. The **AI Control Plane** should therefore be one of the core components of the target architecture in §2:

```
        ┌───────────────────────┐
        │    AI Applications    │
        │  Agents / Assistants  │
        └───────────┬───────────┘
                    │
        ┌───────────▼───────────┐
        │     Agent Runtime     │
        └───────────┬───────────┘
                    │
┌───────────────────▼────────────────────┐
│           AI CONTROL PLANE             │
│                                        │
│  Identity & Authorization              │
│  Policy-as-Code                        │
│  Risk & Autonomy                       │
│  Approval / HITL                       │
│  Skill & Tool Registry                 │
│  Lifecycle / Certification             │
│  Model Governance                      │
│  Data Governance                       │
│  Cost / Budget                         │
│  Kill Switch / Circuit Breaker         │
└───────────────────┬────────────────────┘
                    │
        ┌───────────▼───────────┐
        │   Tool / Data Plane   │
        │   APIs / DB / SaaS /  │
        │  Investment Systems   │
        └───────────────────────┘
```

**This is what turns an agent framework into an enterprise AI operating system.** The model layer — Bedrock in this case — is only one component. The control plane is what allows the fund to scale from 10 carefully built agents to hundreds or thousands of AI capabilities without losing control.

---

## 11. Evaluation, Testing and Observability

Traditional software tests are necessary but insufficient. Agentic systems need continuous behavioral evaluation. Build an evaluation harness before scaling the number of agents.

- **Golden tasks:** representative fund questions, document retrieval tasks, tool calls, exception scenarios and workflow cases.
- **Policy tests:** unauthorized data request, prompt injection, exfiltration attempt, bypass approval, unsafe tool arguments, excessive autonomy.
- **Outcome metrics:** task success, factuality, citation correctness, retrieval recall/precision, tool success, policy compliance, escalation quality.
- **Operational metrics:** latency, token usage, cost per outcome, failure rate, retry count, queue depth, model fallback rate.
- **Agent trajectory tests:** evaluate not just final answer but tool sequence, unnecessary actions, budget adherence, stopping behavior and recovery after tool failure.
- **Production observability:** trace the full chain from user → model → retrieval → tool → workflow → system-of-record change. AgentCore Observability provides traces, metrics and OpenTelemetry-compatible telemetry for runtime environments. [15]

> **Metric shift** — The primary KPI should be "business outcome per unit of cost and risk," not tokens, model quality scores or number of agents deployed.

---

## 12. Platform Engineering, Reliability and FinOps

| Area                     | Best practices                                                                                          | Challenges                                                                                          |
| ------------------------ | ------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------- |
| **Agent lifecycle**      | Templates, golden paths, environment promotion, versioned prompts/tools/policies, canary releases       | Agent configuration is often distributed across code, prompts, model settings and external services |
| **Reliability**          | Timeouts, retries, circuit breakers, idempotency, checkpointing, resumable runs, graceful degradation   | Non-deterministic failures and partial side effects                                                 |
| **Cost**                 | Token budgets, model routing, caching, retrieval limits, concurrency control, per-task cost attribution | Agent loops multiply cost; users underestimate hidden downstream tool costs                         |
| **Scale**                | Queue-based async execution for long jobs; isolate workloads; quotas                                    | Burstiness and long-running agents consume shared capacity                                          |
| **Portability**          | MCP/OpenAPI tool contracts; model abstraction; portable policy semantics                                | Managed services can create lock-in; portability can add complexity                                 |
| **Developer experience** | CLI/templates, local test harness, trace viewer, policy simulator, synthetic test data                  | Without a paved road, teams build inconsistent agent stacks                                         |
| **Disaster recovery**    | Replayable task state, versioned artifacts, backup of memory and policy configuration                   | Reproducing an agent run after model/provider changes can be difficult                              |

---

## 13. Pension-Fund Use-Case Portfolio

Prioritize by business value × data readiness × execution feasibility × risk. The first wave should create reusable capabilities, not isolated demos.

| Use case | Value | Priority | Autonomy target | Primary platform requirement |
|---|---|---|---|---|
| **Investment research assistant** | Research memo synthesis, manager / asset / market question answering | High | L1–L2 | Grounded retrieval, citations, point-in-time data |
| **Portfolio monitoring agent** | Monitor exposures, mandates, limits, news and deviations; create alerts | Very high | L2–L4 | Event-driven monitoring + thresholds + human escalation |
| **Due-diligence agent** | Collect documents, extract fields, compare manager responses, identify gaps | High | L2–L3 | Evidence provenance + structured extraction |
| **Investment committee pack** | Assemble inputs, reconcile facts, draft narrative, highlight unresolved issues | High | L2–L3 | Source locking + deterministic calculations |
| **Risk & compliance surveillance** | Continuous monitoring of policy breaches / anomalies / exceptions | Very high | L2–L4 | Low false-positive rate + audit trail |
| **Operations exception resolution** | Investigate breaks, classify root cause, propose remediation, route cases | Very high | L2–L4 | Deterministic case management + approvals |
| **Data quality steward** | Profile data, detect anomalies, open remediation tickets, track closure | High | L2–L4 | Data quality rules + bounded writes |
| **Legal / policy assistant** | Find policies, precedents, clauses, obligations; draft review packs | High | L1–L2 | Matter-level access controls; legal privilege boundaries |
| **Treasury / cash operations** | Cash forecast, reconciliation, exception handling, payment preparation | High | L2–L3 | Strict transaction controls and dual approval |
| **Corporate services** | HR / procurement / IT service workflows and knowledge | High | L2–L4 | Lower-risk automation domain to build platform muscle |
| **Executive intelligence** | Daily operating brief, emerging risks, cross-domain questions | High | L1–L2 | Source provenance + confidence / unresolved issues |
| **Autonomous control-room agent** | Continuously monitors defined operational objectives and triggers remediation | Strategic | L4 | Goal spec, budgets, stop conditions, rollback |

---

## 14. Roadmap — 24 Months

Sequencing matters. **The platform should earn trust before it earns autonomy.** Each phase delivers both business value and a reusable platform capability.

| Phase | Timing | Theme | Platform / control deliverables | Outcome |
|---|---|---|---|---|
| **Phase 0** | 0–3 months | Foundation and policy | Platform charter; use-case register; AI risk taxonomy; identity model; Bedrock model catalog; secure runtime pattern; telemetry; evaluation harness; first knowledge domain | Enterprise AI platform baseline; 2–3 lighthouse copilots |
| **Phase 1** | 3–6 months | AI assistant at scale | Unified AI workspace; governed enterprise search/RAG; citations; role-aware retrieval; tool registry; prompt / agent templates; FinOps dashboards | 5–10 high-value assistants across investment + corporate functions |
| **Phase 2** | 6–12 months | Workflow execution | Workflow adapters; approvals; deterministic orchestration; agentic exception handling; memory; event-driven triggers; structured audit | 20+ production workflows; measurable time-to-completion gains |
| **Phase 3** | 12–18 months | Bounded autonomy | Goal objects; budgets; policy engine; autonomous monitoring; multi-step agents; dynamic planning; rollback patterns | Selected L4 workflows with hard policy boundaries |
| **Phase 4** | 18–24 months | AI operating layer | Cross-domain agent routing; institutional memory; proactive intelligence; continuous improvement loop; platform-as-a-product operating model | AI becomes default interface for knowledge + work |

---

## 15. Capability Roadmap by Platform Domain

| Domain | Phase 1 | Phase 2 | Phase 3 | Phase 4 |
|---|---|---|---|---|
| **Model layer** | Approved model catalog | Task routing | Adaptive routing + fallback | Continuous benchmark optimization |
| **Agent runtime** | Golden runtime pattern | Shared runtime + quotas | Long-running / async agents | Elastic goal execution |
| **Tools** | Tool registry + contracts | Broad enterprise API coverage | Transactional tools + approvals | Policy-aware autonomous tools |
| **Knowledge** | Priority KBs + ACLs | Hybrid + rerank + freshness | Structured + unstructured fusion | Graph + enterprise semantic layer |
| **Memory** | Session state | User/task memory | Team / workflow memory | Curated institutional memory |
| **Workflow** | Manual handoff | Agent-prepared workflows | Agent-orchestrated workflows | Bounded autonomous workflows |
| **Identity** | User SSO + service identity | Agent identity + delegation | Fine-grained action entitlements | Dynamic risk-adaptive controls |
| **Governance** | Risk taxonomy | Policy-as-code | Continuous compliance | Real-time control plane |
| **Evaluation** | Golden sets | CI evaluation gates | Online quality monitoring | Outcome-based optimization |
| **Observability** | Traces + logs | Cost / quality dashboards | Trajectory analytics | Closed-loop optimization |
| **FinOps** | Cost attribution | Per-agent budgets | Cost per workflow | Business-value / risk / cost optimization |
| **Developer platform** | Templates | Self-service agent delivery | Reusable domain kits | Platform product ecosystem |

---

## 16. Operating Model and Organization

The platform should operate like a product with a platform engineering core and domain-owned business capabilities. Central governance should define controls and paved roads; domain teams should own business outcomes and domain-specific evaluations.

| Team / role | Primary accountability | Recommended staffing pattern |
|---|---|---|
| **AI Platform Engineering** | Runtime, tools, memory, model access, observability, FinOps, developer experience | Central platform team; core engineering ownership |
| **AI Architecture / Enterprise Architecture** | Reference architecture, standards, portability, integration patterns | Small architecture function + design authority |
| **AI Risk & Governance** | Risk tiers, policy, model validation, oversight, regulatory alignment | Independent 2nd-line partnership where appropriate |
| **Domain AI squads** | Investment / risk / operations use cases and domain evaluation | Cross-functional squad: product + engineer + domain SME + data |
| **AI Security / Privacy** | Identity, data boundaries, threat modeling, privacy-by-design | Embedded security + privacy review |
| **AI SRE / Operations** | Production reliability, incident response, performance, cost | Platform SRE capability from Phase 2 onward |

---

## 17. Executive Scorecard

| Dimension | Baseline problem | Target state | Executive metric |
|---|---|---|---|
| **Adoption** | # active users | % target population active monthly | Weekly / monthly active users |
| **Utility** | Low task completion through AI | AI completes or materially accelerates work | Task success / time saved |
| **Trust** | Low citation / policy confidence | High groundedness + low policy incidents | Citation correctness; incident rate |
| **Automation** | Human handoffs | Bounded straight-through processing | % eligible workflows auto-completed |
| **Quality** | Variable agent trajectories | Stable production quality | Regression pass rate; trajectory failure rate |
| **Economics** | Opaque AI spend | Measured cost per business outcome | $/completed task; model utilization |
| **Resilience** | Fragile pilots | Recoverable, observable platform | MTTR; fallback success rate |
| **Platform leverage** | Duplicate agents | Shared primitives reused across domains | % workloads using platform components |

### Developer Ecosystem KPIs

- **Reuse rate:** percentage of new AI applications using existing certified skills/tools.
- **Time to production:** median time from registration to certified production capability.
- **Certification coverage:** percentage of production capabilities with current evaluations and named owners.
- **Capability health:** failure rate, policy violations, latency, cost and rollback frequency by skill/tool.
- **Ecosystem concentration:** percentage of critical workflows dependent on a single vendor/model/tool implementation.

---

## 18. CTO Decisions Required

1. Approve the AI operating-system charter and the separation of reasoning from authority.
2. Adopt the five-plane reference architecture as the default for new AI capabilities.
3. Fund a central AI platform team responsible for runtime, tool plane, evaluation, observability, governance integration and developer experience.
4. Mandate a risk-tiered autonomy policy, with explicit prohibition of unrestricted autonomous execution of material financial / fiduciary actions.
5. Choose 3–5 lighthouse workflows that combine strong business value with manageable risk and reusable platform requirements.
6. Require every production agent to have a documented identity, tool inventory, data sources, risk tier, evaluation suite, operating budget, audit trail and rollback / stop strategy.

---

## 19. Principal Risks and Mitigations

| Risk                                       | Why it matters to a pension fund                              | Mitigation                                                                                                  |
| ------------------------------------------ | ------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| **Hallucinated investment / policy facts** | Could mislead decisions or create inaccurate records          | Grounded retrieval, citations, source locking, independent calculations, human sign-off                     |
| **Prompt injection / data exfiltration**   | Untrusted documents or websites can manipulate agent behavior | Layered isolation, allowlisted tools, retrieval authorization, secret isolation, guardrails, egress control |
| **Over-privileged agents**                 | AI could perform actions beyond intended authority            | Agent identity, least privilege, scoped delegation, action-risk tiers, approvals                            |
| **Model drift / provider changes**         | Behavior may change without code changes                      | Version pinning, benchmark gates, canaries, fallback models, change management                              |
| **Runaway autonomy**                       | Long-running loops can create cost or operational damage      | Budgets, deadlines, max steps, stop conditions, circuit breakers, approval gates                            |
| **Institutional memory contamination**     | Wrong or stale information can become durable context         | Conservative memory writes, provenance, expiry, correction workflow                                         |
| **Vendor concentration**                   | Deep Bedrock dependency can increase switching cost           | Standard tool contracts, model abstraction, portable policy semantics, exportable audit                     |
| **Shadow AI**                              | Employees may bypass platform controls                        | Useful default AI workspace, DLP controls, policy, training, approved model access                          |
| **Weak evaluation**                        | Demos work, production fails on edge cases                    | Fund-specific test sets, adversarial tests, trajectory evaluation, online monitoring                        |

---

## 20. 90-Day Implementation Playbook

1. Create the enterprise AI platform charter, risk taxonomy and architecture standards.
2. Inventory current AI experiments, models, data sources, tools, vendors and shadow AI usage.
3. Stand up the secure Bedrock baseline with approved models, IAM, encryption, logging, network boundaries and initial guardrails.
4. Implement the agent/tool registry and a single production-grade tool contract pattern with idempotency and audit metadata.
5. Build one governed enterprise knowledge domain with ACL propagation, citations, freshness monitoring and evaluation.
6. Implement the agent evaluation harness and CI gate before onboarding additional production agents.
7. Launch an AI workspace for a constrained user group with three lighthouse use cases: investment research, operations exception resolution, and executive intelligence.
8. Define the first two L3 workflows where agents prepare work and humans approve execution; instrument the end-to-end control path.
9. Publish the first executive scorecard covering adoption, quality, risk, automation and unit economics.

> **Success criterion for 90 days** — The goal is not a high number of pilots. The goal is one trusted production platform that can be reused by the next ten AI use cases without rebuilding identity, tools, knowledge, evaluation and observability.

---

## Appendix A — Selected Reference Sources

1. AWS, *Amazon Bedrock AgentCore Overview* — runtime, gateway, memory, identity and observability capabilities. https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/
2. AWS, *Supported models / regions for Amazon Bedrock Knowledge Bases* — inference profiles and cross-Region inference. https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-supported.html
3. AWS, *Retrieving information using Amazon Bedrock Knowledge Bases* — Retrieve, RetrieveAndGenerate, reranking and AgenticRetrieveStream. https://docs.aws.amazon.com/bedrock/latest/userguide/kb-how-retrieval.html
4. AWS, *Query a knowledge base* — Guardrails apply to input and generated response, not retrieved references. https://docs.aws.amazon.com/bedrock/latest/userguide/kb-test-retrieve.html
5. AWS, *Bedrock AgentCore Identity* — agent identity and credential management. https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/identity.html
6. AWS, *IAM Permissions for AgentCore Runtime* — least-privilege production IAM guidance. https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/runtime-permissions.html
7. AWS, *Bedrock Guardrails* — configurable safety, privacy and prompt-attack controls. https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html
8. AWS, *Detect prompt attacks with Bedrock Guardrails.* https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-prompt-attack.html
9. AWS, *Bedrock AgentCore Runtime / Gateway targets and tool integration.* https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/gateway-target-http-runtime.html
10. AWS, *Multi-agent collaboration with Amazon Bedrock Agents* — supervisor / collaborator model. https://docs.aws.amazon.com/en_us/bedrock/latest/userguide/agents-multi-agent-collaboration.html
11. AWS, *Bedrock AgentCore Memory* — short-term and long-term memory strategies. https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/memory-get-started.html
12. OSFI, *Frontier Artificial Intelligence: Implications for Technology, Cyber Security, and Operational Resilience* (April 2026). https://www.osfi-bsif.gc.ca/en/risks/technology-cyber-risk-management/technology-risk-bulletin/frontier-artificial-intelligence-implications-technology-cyber-security-operational-resilience
13. Office of the Privacy Commissioner of Canada, *AI, privacy and your business* (modified May 2025; current guidance accessed 2026). https://www.priv.gc.ca/en/privacy-topics/technology/artificial-intelligence/ai_business/
14. NIST, *AI RMF 1.0 and Generative AI Profile.* https://www.nist.gov/itl/ai-risk-management-framework · https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence-profile
15. AWS, *Bedrock AgentCore Observability* — traces, metrics and OpenTelemetry-compatible telemetry. https://docs.aws.amazon.com/bedrock-agentcore/latest/devguide/observability.html

---

## Appendix B — Reference Policy Schema for a Goal-Driven Agent

A practical policy object should be machine-readable and versioned. The exact implementation can be JSON, a policy engine, or a workflow contract, but the semantic fields should be stable across agents.

| Field | Purpose |
|---|---|
| `goal` | Business objective in unambiguous terms |
| `scope` | Entities, portfolios, systems and geography in scope |
| `time_window` | Start / end or recurring schedule |
| `allowed_tools` | Explicit tools and operations permitted |
| `data_scope` | Permitted data classes, sources and entitlements |
| `budget` | Max model cost, tool calls, wall-clock time and concurrency |
| `materiality` | Thresholds requiring human approval |
| `approval_policy` | Who may approve which action; dual control when required |
| `stop_conditions` | Errors, drift, uncertainty, repeated failure, budget exhaustion, policy change |
| `rollback` | Compensating action or workflow to reverse / contain side effects |
| `evidence` | Required citations, records, calculations and audit artifacts |
| `escalation` | Person / team, severity and timeout rules |
| `retention` | How long to retain task state, memory and evidence |
| `version` | Policy version tied to agent and tool versions |

> **Final recommendation** — Build the platform as an enterprise control plane, not a collection of copilots. Bedrock provides the managed foundation-model layer; the fund differentiates through governed enterprise context, action contracts, workflow integration, policy, evaluation, and institutional learning. **Trust is the gating factor for autonomy.**

