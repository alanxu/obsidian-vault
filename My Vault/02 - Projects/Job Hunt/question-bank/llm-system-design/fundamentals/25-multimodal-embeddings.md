---
title: Multimodal Embeddings & Visual Retrieval
slug: multimodal-embeddings
area: RAG Concepts
companies: ["Harvey (doc-processing verified in loop)", "enterprise applied-AI (prep-bank topic; not candidate-verified elsewhere)"]
difficulty: ★★★☆☆
related: ["[[08-embeddings-and-similarity]]", "[[llm-system-design/38-multimodal-document-rag]]", "[[12-reranking]]"]
added: 2026-07-09 (audit follow-up — pairs with design card 38)
evidence: "MIXED: Harvey doc-processing round VERIFIED (techinterview.org guide); multimodal RAG appears in 2026 RAG prep banks (DataCamp, igmGuru) — guide-level. The embeddings-specific rapid-fire framing is my synthesis."
---

# Multimodal Embeddings & Visual Retrieval

## Prompt
How do you retrieve over images, charts, and tables? How do multimodal embeddings work, and what's ColPali-style retrieval?

## Answer
Three strategies, in increasing visual fidelity:
1. **Describe-then-embed:** VLM captions the image/chart/table at ingest → embed the *text*. Works with any text stack; quality capped by the caption (a lossy, one-time summary written before knowing the query).
2. **Joint-space embeddings (CLIP-family):** image encoder + text encoder trained (contrastively) into one vector space — text query directly matches image vectors. Great for natural images ("photo of a broken valve"); weak on **dense documents** — a single vector can't hold a page of fine-grained text/layout, and CLIP-style training under-represents text-in-image.
3. **Late-interaction visual retrieval (ColPali-style):** a VLM embeds a **page screenshot into many patch vectors** (multi-vector, ColBERT-style); query tokens match patches via MaxSim. No parsing/OCR at all — layout, charts, tables survive perfectly. Costs: 10–100× index size, heavier scoring (mitigate: pooling/quantization, or use as reranker over a cheap first stage).

**The mental model:** it's the same funnel as text RAG ([[12-reranking]]) — cheap wide net → precise scorer; you're choosing *which representation* each stage sees. Rule of thumb: natural images → CLIP-family; document pages (charts/tables/scans) → ColPali-style or describe-then-embed; need cell-level citations or numeric precision → parse to structure ([[llm-system-design/38-multimodal-document-rag]] design fork).

## Tradeoffs
| Strategy | Gains | Costs |
|---|---|---|
| Describe-then-embed | any text stack, cheap queries, debuggable | caption is lossy + query-blind; stale on VLM upgrade |
| Joint space (CLIP) | direct text↔image, single vector, fast | poor on dense text/layout; modality gap |
| Late-interaction (ColPali) | no parsing loss, SOTA on doc-visual benchmarks | index size, scoring cost, page-level (not cell-level) citations |

## Follow-ups
- *"Why does CLIP fail on documents?"* → one vector per page can't encode dense fine-grained content; contrastive training favors global semantics over text-in-image.
- *"Multi-vector index cost?"* → ~100–1000 patch vectors/page → pool/quantize, or two-stage: text/CLIP first stage → ColPali rerank top-50.
- *"How do you eval the retriever choice?"* → modality-sliced eval (only-from-chart / only-from-table questions); benchmark family: ViDoRe.
- *"Hybrid with text?"* → yes — extracted text (BM25+dense) and visual retrieval fused (RRF), same as hybrid search ([[13-hybrid-search]] logic).

## Pitfalls
- Using CLIP for chart/table pages because "it's multimodal" — wrong tool for dense documents.
- Treating captions as ground truth at answer time — re-show the image to the VLM; captions drift from pixels.
- Ignoring index/serving cost of multi-vector until it's 100× your text index.
- Forgetting citations degrade to page-level with pure visual retrieval — a product requirement, not a detail.

## Tips
Ladder answer: **describe-then-embed → CLIP joint space → ColPali late-interaction**, each with its failure mode (lossy / dense-text-blind / expensive). Close with routing by corpus + the two-stage hybrid — that's the staff-level 2 minutes.
