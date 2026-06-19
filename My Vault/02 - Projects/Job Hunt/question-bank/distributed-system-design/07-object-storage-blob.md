---
title: "Object Storage (S3-like Blob Store)"
slug: object-storage-blob
type: distributed-system-design
tier: "1 — Core data stores & consistency"
companies: [AWS S3, Google Cloud Storage, Azure Blob, Cloudflare R2, MinIO, Backblaze, Dropbox]
difficulty: ★★★☆☆
frequency: medium-high
formats: [Onsite·SD, Mock]
time-box: 30–40 min
tags: [object-storage, blob, s3, erasure-coding, multipart, eventual-consistency]
related: ["[[01-distributed-kv-cache]]", "[[18-petabyte-log-ingestion]]", "[[35-batch-data-warehouse]]"]
companies-likely: [AWS, GCP, Azure, Cloudflare, MinIO, Backblaze, Dropbox]
---

# Object Storage (S3-like Blob Store)

**One-liner:** A petabyte-scale, eventually-consistent key-value store for binary blobs (images, videos, backups) with cheap storage, simple API, and 11-nines of durability.

## Problem framing

Asked when the workload is large files (not small KV), cost is a concern, and the interviewer wants you to think about **erasure coding** (vs replication) for cheap durable storage. Variants: S3, GCS, Azure Blob, Dropbox, Backblaze B2.

**Variants:**
- "Design S3" (general — durability, scale, eventual consistency)
- "Design Dropbox / Google Drive sync" (client-side + sync)
- "Design a video / image hosting backend" (CDN front)
- "Design a backup / archive store" (cold storage, very cheap)

## Requirements (clarify first)

- **Functional:** `PUT(key, blob)`, `GET(key)`, `DELETE(key)`, `LIST(prefix)`, multipart upload, range reads.
- **Non-functional:**
  - Durability: 99.999999999% (11 nines) — i.e. lose 1 object in 10M years at exabyte scale.
  - Availability: 99.9%–99.99% (varies by tier).
  - Latency: p99 < 100ms first byte for first-byte GET; < 1s for big objects.
  - Cost: cheapest storage tier at $0.001/GB-month (Glacier).
- **Constraints:** object size (0–5TB), request rate (3.5k PUT/s, 5.5k GET/s per prefix).
- **Out of scope:** POSIX filesystem semantics (mention as variant).

## Capacity estimation

- 1 exabyte stored = 1000PB. Erasure coding 6+3 → 1.5× raw = 1.5EB raw disk.
- 10B objects × 1MB avg = 10PB. Or 100M objects × 100MB = 10PB.
- 100k GET/s peak across the cluster.

## High-level architecture

```
Client ──► Edge / LB ──► Frontend (auth, rate limit)
                              │
                              ▼
                       Metadata service (object index, location)
                              │
                              ▼
                       Storage node (erasure-coded chunks on disk)
                              │
                              └──► Disk shelves with replication across zones
```

**Three planes:**
1. **Metadata plane:** where each object lives. Needs strong consistency (object must not be lost). Small enough to fit in RAM + SSD across a small cluster.
2. **Data plane:** the actual bytes, spread across many storage nodes with erasure coding.
3. **Control plane:** lifecycle, replication, repair, rebalancing.

## API / interfaces

```
PUT /v1/buckets/{bucket}/keys/{key}
  Body: <bytes>
  Headers: Content-MD5, x-amz-meta-*
  → 200 { ETag: "..." }

GET /v1/buckets/{bucket}/keys/{key}
  Headers: Range: bytes=0-1023
  → 200 { Body: <bytes>, ETag, x-amz-version-id }

DELETE /v1/buckets/{bucket}/keys/{key}
  → 204

POST /v1/buckets/{bucket}/keys/{key}?uploads   (initiate multipart)
POST /v1/buckets/{bucket}/keys/{key}?uploadId={id}&partNumber={n}
```

## Deep dive #1 — Erasure coding (why replication doesn't scale)

**Replication** (RF=3) costs 3× raw storage. For 11 nines durability on a 1EB dataset, RF alone is fine — but **cost**.

**Erasure coding** (Reed-Solomon):
- Split object into *k* data chunks + *m* parity chunks (e.g. k=6, m=3, RS(6,3)).
- Any 6 of 9 chunks can reconstruct the object.
- Storage overhead = (k+m)/k = 1.5× — half the cost of RF=3.
- Durability equivalent to RF≈3 (lose 2 of 9 chunks without data loss).

**Tradeoff:**
- **Repair cost:** lose a chunk → must reconstruct from 6 surviving. With k=6, m=3, this is 6× network + compute. **Repair is the bottleneck**, not storage.
- **Repair bandwidth:** Google's measurements show repair traffic can dominate. Mitigations: locally-repairable codes (LRC), lazy repair, prioritization.

**Coding parameters:**
- RS(6,3): storage 1.5×, durability ≈ 4 nines against correlated failure.
- RS(10,4): storage 1.4×, better durability, more chunks.
- LRC (Azure-style): RS(6,2,3) — 6 data + 2 global parity + 3 local parity. Local repair reads only local group.

**Placement:** chunks placed on different failure domains (rack, zone, region). Google's Colossus / Facebook's f4 use 6+3 across 3+ zones.

## Deep dive #2 — Metadata, consistency, scaling

**Metadata:** the index mapping `bucket/key → (storage_nodes, erasure_coded_chunks, version)`. This is small (1KB per object) compared to data — but there are 10B objects, so 10TB of metadata.

**Metadata storage:** typically a strongly-consistent KV (Spanner, FoundationDB) or a custom Paxos-replicated log. **Must be strongly consistent** — eventual consistency here = lost objects.

**Scaling metadata:**
- **Sharded by key prefix.** Each shard handles a range of keys.
- **Caching in RAM** at the frontend: most reads hit cache.
- **Separate data path:** large uploads go directly to storage nodes, metadata is updated async.

**Consistency:**
- **PUT-after-PUT:** eventually consistent. Two simultaneous PUTs to same key may both "succeed" but only one becomes the canonical version.
- **Read-after-PUT:** eventually consistent (typically < 1s).
- **Read-after-LIST:** eventually consistent — new object may not appear in LIST immediately.
- **Strong consistency is opt-in** (S3 added it in 2020 for HEAD/GET on existing keys — at significant engineering cost).

**Multipart upload:**
- Large object split into N parts (5MB–5GB each, up to 10k parts).
- Each part uploaded independently → assembled by storage layer on completion.
- Allows parallel upload, retry of failed parts, pause/resume.

## Scale & bottlenecks

- **Storage node disk full:** rebalance by moving chunks to less-full nodes. Background task, throttled.
- **Hot key:** one object gets 10k GETs/s. CDN in front is the answer (CloudFront / Cloudflare).
- **Repair storms:** a rack dies → must reconstruct all its chunks. Mitigate: priority queue, stagger repairs, throttled at network level.
- **List is slow at scale:** 1B objects per prefix → list must page. Maintain a separate index (S3 Inventory) for offline queries.

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Storage node disk dies | Chunks lost | Reconstruct from parity (k of k+m) |
| Rack / zone down | Multiple chunks | Place chunks across failure domains |
| Metadata service down | All ops fail | Replicated metadata; cached at frontends |
| Repair storm | Network saturated | Throttle, prioritize, LRC for local repair |
| Bucket sprawl | Cost grows | Lifecycle policies (transition to Glacier) |

## "What I'd build first and why"

**A metadata plane (strongly-consistent, sharded) + a data plane (storage nodes with RS(6,3) erasure coding, chunks spread across 3 zones) + a frontend (auth, rate limit, multipart orchestration).** Strong consistency on metadata, eventual on the data plane.

The single highest-leverage thing is **erasure coding vs replication** — naming RS(6,3) with cost math is the staff move.

## Follow-ups (real, reported)

1. **Why not replication?** Cost. RF=3 is 3×; RS(6,3) is 1.5×.
2. **RS(6,3) vs RS(10,4) vs LRC** — explain the trade.
3. **Repair cost / network** — the bottleneck at scale.
4. **Strong consistency** — how much does it cost you? (S3's experience.)
5. **Multipart upload** — why 5MB parts? Throughput vs metadata overhead.
6. **Lifecycle / tiering** — hot → warm → cold (Glacier-style).
7. **Versioning + delete markers** — soft delete + rollback.
8. **Object locking / WORM** — compliance use case.
9. **Cross-region replication** — async, eventually consistent.
10. **List / inventory at scale** — separate index for offline queries.

## Tips (staff-level)

- **Name the erasure code.** RS(6,3) with the math: 1.5× storage, ~equivalent durability to RF=3.
- **Talk about repair.** It's the operational pain point at scale.
- **Quantify:** "1EB at RS(6,3) = 1.5EB raw, $15M/year on commodity disks".
- **Distinguish metadata from data plane.** Strong consistency on metadata, eventual on data.
- **Know S3 quirks.** Eventual consistency was the headline for 14 years; strong consistency was added later.

## Pitfalls

- **Designing as "just a KV".** Erasure coding is the cost story.
- **Ignoring repair cost.** "Just reconstruct from parity" — at 1EB scale, that's the bottleneck.
- **No multipart.** Large uploads fail on network blips.
- **Strong consistency by default.** Eventual is fine for most; opt in for what needs it.
- **No lifecycle.** Petabytes of stale data at hot-tier prices.

## Worked narration (3 min)

"Goal: 1EB stored, 11 nines durability, 99.99% availability, ~$15M/year storage cost.

**Three planes:**
- **Metadata:** strongly-consistent sharded KV (Spanner/FDB style). Maps `bucket/key → chunk locations + version`.
- **Data:** storage nodes hold RS(6,3) erasure-coded chunks. 6 data + 3 parity; any 6 of 9 reconstructs. 1.5× storage overhead.
- **Control:** lifecycle (hot → cold), repair, rebalance.

**Placement:** 3 zones per region, 3 chunks per zone, 9 total. Lose any zone → reconstruct from the 6 surviving.

**Write:** client uploads to frontend → auth + rate limit → multipart parts go to storage nodes directly → metadata updated when all parts complete.

**Read:** frontend resolves metadata → issues parallel reads to k storage nodes → returns bytes.

**Repair:** background job detects chunks below replication target → reconstructs from parity → places on a healthy node. Throttled to avoid network saturation.

**Consistency:** metadata strong, data eventual. Read-after-PUT may be stale by ~1s (typical for S3).

**First build:** metadata sharded + data RS(6,3) + frontend with auth. Add lifecycle tiers, versioning, strong-consistency opt-in later."

## Related

- [[01-distributed-kv-cache]] — same distributed-systems primitives, different scale.
- [[18-petabyte-log-ingestion]] — object storage is often the landing zone.
- [[35-batch-data-warehouse]] — data lake on top of object storage.