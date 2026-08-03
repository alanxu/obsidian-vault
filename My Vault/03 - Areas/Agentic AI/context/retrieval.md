---
title: Retrieval
pillar: context
parent: ./README.md
section: "2.3"
---

# 2.3 Retrieval (Episodic + Semantic)

- **Just-in-time.** Don't pre-load. Embed query → search → inject only what's needed.
- **Hybrid recall.** Vector similarity for fuzzy, BM25/keyword for exact (names, IDs, error codes).
- **Cite every memory.** Return the source with the recall. Models can then choose to trust or ignore.
- **Memory ≠ truth.** Vector search is recall, not correctness. Validate on use.
