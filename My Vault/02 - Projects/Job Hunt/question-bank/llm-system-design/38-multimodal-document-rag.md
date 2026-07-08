---
title: Design Multimodal RAG (charts, tables, figures)
slug: multimodal-document-rag
area: 1 — Retrieval & Knowledge Systems
companies: ["Harvey (verified: loop covers PDF parsing/OCR/dense tables)", "Glean (inferred: RAG round confirmed, tables not specifically)", "Cohere (inferred from product focus, not a reported Q)", "financial/enterprise applied-AI (topic appears in 2026 RAG prep banks)"]
difficulty: ★★★★☆
formats: [Live system design, Take-home design]
related: ["[[01-rag-with-citations]]", "[[36-structured-output-extraction]]", "[[fundamentals/25-multimodal-embeddings]]", "[[fundamentals/10-chunking]]"]
added: 2026-07-09 (audit follow-up — no prior non-text retrieval coverage)
evidence: "Verified: Harvey interview guide (techinterview.org, 2026) explicitly lists PDF parsing, structured extraction, OCR, dense tables. Topic-level: multimodal RAG appears in 2026 RAG interview-prep banks (DataCamp, igmGuru). NOT candidate-verified at Glean/Cohere/Anthropic/OpenAI — treat as likely-adjacent, not reported."
---

# Design Multimodal RAG (charts, tables, figures)

> "RAG over 10-K filings / research papers / slide decks — where the answer lives in a chart, a table, or a diagram." **Open with the failure mode:** text-only RAG **silently drops** the highest-value content — a revenue trend exists only as a line chart; a comparison only as a table. The design question is **what representation each modality gets in the index**, and the modern fork is **parse-to-text vs page-image retrieval (ColPali-style)**.

## Problem
"Q&A over financial reports with charts and tables, cited." Variants: research-paper QA (figures/equations), slide-deck search, product-manual QA (diagrams), "why is table QA failing in our RAG?"

## Clarify first
- Corpus: born-digital PDFs vs scans? Chart-heavy (finance) vs table-heavy (ops) vs diagram-heavy (manuals)?
- Query types: lookup ("Q3 revenue?") vs reasoning over a table (aggregation, trend) vs cross-doc?
- Citation requirement — cite the *figure/cell*, not just the page? Latency/cost bar; VLM budget at ingest?

## Architecture (two viable designs — name both, pick by corpus)
**A. Parse-everything-to-text (classic):** layout-aware parse → route by element type: **tables** → preserve structure (markdown/HTML; never flatten to prose) + **LLM-generated table summary** for embedding; **charts/figures** → VLM caption + extracted data points + axis/series metadata; **text** → normal chunks. All become text-index entries with element type, doc/page/bbox for citation. Retrieval = hybrid ([[01-rag-with-citations]]) + element-type boosts; on hit, feed the LLM the *structured original* (table markup, chart data or image), not the summary.
**B. Page-image retrieval (ColPali-style):** embed **page screenshots** directly with a vision-language retriever (late-interaction over image patches); retrieve pages as images; a **VLM answers from the images**. Skips brittle parsing entirely — charts/layout preserved perfectly. Costs: VLM at query time, larger index (multi-vector), weaker fine-grained citation (page-level, not cell-level).
**Pragmatic hybrid:** B for retrieval recall on visual-heavy corpora + A's extracted tables for numeric precision and cell-level citation.

## Deep-dive — the table & chart problems
- **Tables:** three representations, use all: (1) structural (markdown w/ headers, merged-cell handling) for the generator, (2) natural-language summary ("quarterly revenue by region, FY24") for embedding — raw cell soup embeds terribly, (3) optionally rows-as-records for big tables (retrieve relevant rows, not the whole table). Aggregation queries ("average across quarters") → don't make the LLM do arithmetic over markdown: **tool call** (code-interpreter over the extracted dataframe) — say this, it's the staff move.
- **Charts:** ingest-time VLM pass → caption + underlying data estimate + series/axes; index that. At answer time, pass the chart *image* to the VLM for verification (captions drift from pixels). Numeric reads off charts are estimates — answer should say so or prefer a matching table if one exists (charts and tables often duplicate; link them at ingest).
- **Citations:** element-level handles (doc, page, bbox, table-cell coords) flow through the whole pipeline — the UI highlights the exact figure/cell ([[36-structured-output-extraction]] uses the same span discipline).

## Tradeoffs
| Decision                                      | Tradeoff                                                                                                   |
| --------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| Parse-to-text (A) vs page-image (B)           | precise citations + cheap queries + debuggable vs no parsing loss + visual fidelity; B needs VLM per query |
| VLM captioning at ingest                      | one-time cost, fast queries vs captions go stale vs model upgrades (re-run)                                |
| Table summary vs raw-cell embedding           | retrieval quality vs an extra LLM pass per table                                                           |
| Whole-table vs row-level chunks               | small tables fine whole; big tables need row retrieval (but lose column context — keep headers per chunk)  |
| Answer numeric from chart vs abstain/redirect | coverage vs precision — finance targets expect abstain-or-table                                            |

## Numbers
Ingest cost dominates: VLM caption ~$0.002–0.01/image, ~1–5 figures+tables per page · ColPali-style index: ~100–1000 vectors/page (multi-vector) vs 1–3 chunks/page text — 10–100× index size · table-parse accuracy is the ceiling: born-digital ~95%+, scanned ~80–90% → the "worst source of errors" note from [[36-structured-output-extraction]] applies to retrieval too.

## Eval
Build the eval set **by modality**: questions answerable only-from-table / only-from-chart / only-from-text / cross-modal — recall@k and answer accuracy *per slice* (aggregate hides the gap that motivated this design) · numeric-answer exactness (cell-cited vs chart-estimated tracked separately) · citation precision at element level · regression gate on parser/VLM/embedder upgrades.

## Failure modes
Chart data silently absent from index (text-only ingest — the original sin) · table flattened to prose → aggregation questions fail · caption hallucinating chart values → grounded answer that's wrong with a confident citation · merged-cell/nested-header tables mangled → wrong cell cited · figure retrieved but referenced text ("see Fig. 3") not co-retrieved (link figure↔caption↔referencing paragraphs at ingest) · VLM upgrade shifts captions → stale index (version + re-ingest policy).

## Top follow-ups
- "Why does naive RAG fail on tables?" → embedding cell soup retrieves poorly + flattening destroys structure the generator needs; summary-for-embedding, structure-for-generation.
- "ColPali vs parse-to-text?" → tradeoff table above; pick B for visual-heavy + parsing-hostile corpora, A when cell-level citations/numeric precision are required; hybrid is the real answer.
- "Numeric question over a big table?" → retrieve rows → dataframe → code-interpreter tool; LLM narrates, code computes.
- "How do you eval it?" → modality-sliced eval set; only-from-chart questions are the canary.
- "Diagrams/flowcharts?" → VLM structural description (nodes/edges) at ingest; answer-time image pass; treat as figures with graph semantics.

## Related
[[01-rag-with-citations]] (base pipeline) · [[36-structured-output-extraction]] (parsing/table machinery shared) · [[fundamentals/25-multimodal-embeddings]] (retriever choices) · [[fundamentals/10-chunking]] (element-aware chunking).
