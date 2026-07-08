---
title: Design a Document → Structured Data Extraction Pipeline
slug: structured-output-extraction
area: 6 — Data, Features, Embeddings (+ Area 5 eval)
companies: [Harvey, Glean, Cohere, "Scale, enterprise applied-AI", Robinhood]
difficulty: ★★★★☆
formats: [Live system design, Take-home design (very common FDE/applied take-home)]
related: ["[[04-legal-document-qa]]", "[[26-data-labeling-pipeline]]", "[[fundamentals/24-structured-outputs]]", "[[18-llm-eval-harness]]"]
added: 2026-07-08 (audit fill — the enterprise applied-AI workhorse prompt)
evidence: "MIXED: Harvey VERIFIED — interview guide (techinterview.org 2026) explicitly covers PDF parsing, structured extraction, OCR, dense tables. GUIDE-LEVEL: 'insurance-claims agent: ingest claims → approval decision via RAG under token-cost control' cited as a standard 2026 agent-design prompt (KORE1/Exponent aggregations). Glean/Cohere/Scale/Robinhood = domain inference."
---

# Design a Document → Structured Data Extraction Pipeline

> "Turn 1M messy PDFs (invoices/contracts/claims) into database rows with known accuracy." **Open with:** this is an **accuracy-accounting problem** — the design revolves around **schema-constrained generation + per-field confidence + human-in-the-loop routing**, because the output feeds systems that act on it.

## Problem
"Extract line items from invoices at 99% field accuracy" / "pull 40 clauses from contracts" / "insurance-claims intake agent." Variants: tables/handwriting (OCR), multi-hundred-page docs, evolving schema, per-customer schema (FDE flavor).

## Clarify first
- Schema: fixed vs per-customer? Field count? Which fields are high-stakes (amounts, dates, parties)?
- Accuracy bar *per field* and what happens downstream (auto-pay? human review anyway?)
- Volume/latency: batch overnight vs real-time intake? Doc quality (born-digital vs scans)?

## Architecture
**Ingest:** classify doc type → parse (layout-aware: text + tables + coordinates; OCR fallback for scans) → segment (long docs: locate relevant sections first — retrieval, not full-context). **Extract:** per doc-type prompt + **schema-constrained decoding** (JSON schema / function-call mode, → [[fundamentals/24-structured-outputs]]) → per-field output: `{value, source_span, confidence}`. **Validate:** deterministic checks first (types, regex, checksums, cross-field: line items sum to total; date order) → **confidence router**: pass ≥τ auto-accept · gray zone → second model or re-ask with focused context · fail/low → **human review queue** (UI shows source span highlighted). **Learn:** human corrections → eval set + few-shot pool + fine-tune data ([[26-data-labeling-pipeline]] loop).

## Deep-dive — accuracy accounting & the router
- **Per-field, not per-doc metrics:** a 40-field doc at 99%/field = 67% chance of a perfect doc — so downstream must tolerate field-level review. Track precision/recall *per field type*; high-stakes fields get stricter τ.
- **Confidence that means something:** raw LLM logprobs are miscalibrated → calibrate on labeled data (or use agreement-of-two-models / self-consistency as proxy). The router's economics: human review costs ~$X/doc; auto-error costs $Y; τ set where marginal error cost = review cost.
- **Grounding = source spans:** every value cites char/page coordinates → reviewer verifies in seconds, not minutes; also catches hallucinated values (span missing/mismatched → auto-flag).
- **Long docs:** don't stuff 300 pages — section-retrieval per field group; cheaper and *more* accurate (less distraction).

## Tradeoffs
| Decision | Tradeoff |
|---|---|
| One big extraction call vs per-field-group calls | cheap vs accurate + parallelizable + partial-retry |
| Constrained decoding vs parse-and-repair | guaranteed shape vs slight quality tax, provider lock-in |
| Strict τ vs loose | human cost vs downstream error cost (economics, not vibes) |
| Generic model vs fine-tuned per doc-type | flexibility vs accuracy at volume |
| OCR+LLM vs multimodal LLM direct | controllable/debuggable vs simpler, better on layout — trend is multimodal |

## Numbers
Per-doc cost: parse ~free–$0.01 (OCR) + LLM $0.01–0.10 · human review $0.5–3/doc → router savings dominate ROI · throughput = batch + parallel (no interactivity constraint) · field accuracy: born-digital 97–99.5% achievable; scans/handwriting 85–95% → review rates 5–30%.

## Eval
Golden set per doc type (human-labeled, versioned) · per-field precision/recall + exact-match · **calibration curve** (confidence vs actual accuracy) · auto-accept error rate (sampled audit — the number the business cares about) · review-queue rate + reviewer overturn rate · regression gate on prompt/model change ([[18-llm-eval-harness]]).

## Failure modes
Hallucinated values that *look* valid (span-grounding catches) · systematic per-template failures (new vendor invoice format → drift monitor by doc-type accuracy) · miscalibrated confidence → silent auto-accept errors · schema evolution breaking old extractions (version the schema; re-extract or map) · table structure mangled by parser (worst source of errors — invest here) · prompt injection via document text ("ignore instructions…" in a PDF → treat doc text as data, constrained output limits blast radius).

## Top follow-ups
- "How do you *know* it's 99% accurate?" → golden set + sampled audit of auto-accepts + per-field tracking; never trust the model's self-report.
- "Where do humans fit?" → confidence router; review UI with span highlights; corrections feed evals + training.
- "New document format shows up?" → doc-type classifier flags unknown → route to human → few-shots added → accuracy recovers without deploy.
- "Why not just RAG-QA per field?" → that *is* the long-doc pattern (retrieval per field group); extraction adds schema constraint + batch economics.
- "Model upgrade?" → shadow-run on golden set + live sample, compare per-field, gate ([[18-llm-eval-harness]]).

## Related
[[04-legal-document-qa]] (QA sibling) · [[26-data-labeling-pipeline]] (correction loop) · [[fundamentals/24-structured-outputs]] (mechanism) · [[18-llm-eval-harness]] (gate).
