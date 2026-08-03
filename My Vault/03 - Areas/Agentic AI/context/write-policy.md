---
title: Memory Write Policy
pillar: context
parent: ./README.md
section: "2.5"
---

# 2.5 Memory Write Policy

- **Whitelist, don't blacklist.** Persist only what the user explicitly asked to remember, or what a validated reflection pass extracted.
- **No auto-everything.** Auto-memory-everything turns the store into a junk drawer.
- **TTL on everything.** Every memory has an expiry. The user (or a periodic sweep) prunes.
