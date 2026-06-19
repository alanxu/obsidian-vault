---
title: "Consensus & Leader Election (Raft / Paxos)"
slug: consensus-leader-election
type: distributed-system-design
tier: "1 — Core data stores & consistency"
companies: [etcd, Consul, CockroachDB, Spanner, Chubby, ZooKeeper, Kafka (KRaft), TiKV]
difficulty: ★★★★☆
frequency: high
formats: [Onsite·SD, Whiteboard]
time-box: 30–45 min
tags: [consensus, raft, paxos, leader-election, linearizability, replication]
related: ["[[01-distributed-kv-cache]]", "[[04-distributed-lock-service]]", "[[11-configuration-management]]"]
companies-likely: [etcd, Consul, CockroachDB, Spanner, FoundationDB, Kafka, TiKV]
star: true
---

# Consensus & Leader Election (Raft / Paxos)

**One-liner:** A replicated state machine where a majority of nodes agree on the order of every operation, with automatic leader election on failure and linearizable reads.

## Problem framing

Asked at infra / platform / database shops when the interviewer wants to test your grasp of *correct* distributed replication. The classic answer is **Raft** — explicitly designed to be understandable. Variants: Chubby (Google's lock service), etcd (Raft-backed KV), Spanner (Paxos + TrueTime), ZooKeeper (Zab).

**Variants:**
- "Explain Raft" (algorithm)
- "Design a leader-election service" (primitive)
- "Design etcd / Chubby" (consensus-backed KV)
- "How does Spanner do cross-region consistency?" (Paxos + TrueTime)

## Requirements (clarify first)

- **Functional:** clients propose values (commands); the cluster agrees on an order; replicas apply in that order; clients can read the latest applied value.
- **Non-functional:**
  - **Safety:** never return two different values for the same index.
  - **Liveness:** if a majority is up, the cluster makes progress.
  - Latency: commit in 1-2 RTTs (Raft) / 4-6 RTTs (Multi-Paxos).
- **Constraints:** typically 3 or 5 nodes per group; bounded number of groups for sharding.
- **Out of scope:** Byzantine fault tolerance (mention as variant), cross-group transactions.

## Capacity estimation

- 5-node Raft group, 1k ops/s, each op 1KB log entry → ~1MB/s log traffic. Trivial.
- Latency dominated by RTT: same-DC commit ~5ms; cross-region ~100-200ms (Spanner's experience).
- 1000s of Raft groups for horizontal scale → manageable per-group.

## High-level architecture

```
Clients ──► Leader (any node, currently)
              │
              ├──► Append entry to local log
              ├──► Replicate to followers
              ├──► Wait for majority ack
              ├──► Commit + apply to state machine
              └──► Respond to client
              
Followers ──► Election timeout (150-300ms random) ──► candidate
            ──► Request votes from peers
            ──► Win majority → become leader
```

## Deep dive #1 — Raft

**Three states:** Follower, Candidate, Leader. Persistent on each node: current term, voted-for, log.

**Leader election:**
1. Follower's election timer (150-300ms randomized) expires → becomes Candidate.
2. Increments term, votes for itself, sends RequestVote RPC to all peers.
3. Peers grant vote if their log is at least as up-to-date as the candidate's (log-up-to-date check: higher term wins; if same term, longer log wins).
4. Majority of votes → Candidate becomes Leader.
5. Sends heartbeats (empty AppendEntries) every ~50ms to suppress new elections.

**Log replication:**
1. Client sends command to Leader.
2. Leader appends to its log (uncommitted).
3. Leader sends AppendEntries RPC to all Followers with the new entry.
4. Followers append if log matches (consistency check by prevLogIndex + prevLogTerm).
5. Leader commits once a majority has replicated the entry.
6. Leader applies to state machine and responds to client.
7. Leader notifies Followers of commit in next AppendEntries.

**Safety properties Raft guarantees:**
- **Election safety:** at most one leader per term.
- **Log matching:** if two logs have an entry at the same index + term, the entries are identical and all preceding entries are identical.
- **Leader completeness:** if an entry is committed in term T, every leader in term > T has that entry.
- **State machine safety:** if a server applies an entry at index i, no other server applies a different entry at i.

**Failure modes Raft handles:**
- Leader crashes mid-replication → new election, log reconciled on next AppendEntries.
- Network partition → minority partition can't elect leader (no majority); majority keeps serving.
- Stale leader returns after partition → steps down on higher term seen.

## Deep dive #2 — Linearizability, log compaction, multi-group

**Linearizability:** every operation appears to take effect atomically at some point between invocation and response. Raft provides linearizable writes (committed at the leader before response). Reads need a round-trip with the leader (or read-index / lease-read optimization) to be linearizable.

**Read-index:** leader confirms it's still the leader by getting a heartbeat quorum, then serves the read at its commit index. Avoids going through the log.

**Lease-read:** leader assumes leadership for a short lease period (e.g. clock interval + RTT); serves reads locally. Faster but assumes bounded clock skew.

**Log compaction (snapshot + install):**
- Snapshots: when log grows too long, leader takes a snapshot of state machine, truncates log.
- InstallSnapshot: sends snapshot to far-behind followers (whose log doesn't have the prefix needed).

**Multi-Raft / sharding:**
- 1000s of Raft groups, each handling a range of keys.
- Coordination across groups for cross-key transactions: 2PC, or Percolator-style (Spanner's transactional layer).
- Rebalancing: move a key range from one group to another → snapshot + install.

**Paxos vs Raft:**
- Paxos: more general, harder to understand. Multi-Paxos amortizes leader election.
- Raft: explicit leader, understandable, equivalent to Multi-Paxos.
- **Spanner** uses Paxos with TrueTime for external consistency across regions.
- **etcd / Consul / CockroachDB / TiKV** use Raft.

## Scale & bottlenecks

- **Cross-region Raft:** RTT dominates (100ms+). Spanner's answer: Paxos + TrueTime; commit in 5-10 RTTs but linearly ordered globally.
- **Group count:** 1000s of Raft groups per cluster is normal. Each is a small, fast loop.
- **Leader bottleneck:** every write goes through the leader. Mitigation: leader leases + batched commits; multi-leader (in some systems).
- **Membership changes:** adding/removing a node during a joint-consensus phase (Raft's "single-server" or "joint consensus" config).

## Failure modes & mitigations

| Failure | Effect | Mitigation |
|---|---|---|
| Leader crash | Election (~1-2s) | Random timeouts; pre-vote; leadership transfer |
| Network partition | Minority can't elect | Joint consensus for membership; quorum |
| Slow disk | Log fsync stalls | SSD; batch fsync; separate log disk |
| Replay storm | New leader needs snapshot | InstallSnapshot; throttled streaming |
| Term thrashing | Frequent elections | Pre-vote phase; check-quorum; lease |

## "What I'd build first and why"

**Raft** for the consensus loop, **single-leader reads with read-index or lease-read** for linearizable reads, **snapshots + InstallSnapshot for log compaction**, **joint consensus for membership changes**.

The single highest-leverage thing is **getting the log + state machine + leader-election shape right** — once you have that, sharding is just running more groups.

## Follow-ups (real, reported)

1. **Raft vs Paxos** — name the differences (leader-centric vs leaderless).
2. **Pre-vote phase** — why? (Prevents disruption from partitioned nodes coming back.)
3. **Linearizable reads** — read-index vs lease-read vs quorum read.
4. **Log truncation / snapshots** — when, how, InstallSnapshot.
5. **Membership changes** — joint consensus (Raft) vs single-server changes.
6. **Cross-region consensus** — Spanner + TrueTime; Paxos over WAN.
7. **Leader-based bottleneck** — throughput limited by leader node.
8. **Joint consensus** — adding/removing a node without losing safety.
9. **Pre-vote** — prevents unnecessary term bumps from partitioned nodes.
10. **Byzantine fault tolerance** — when is PBFT / HotStuff needed? (Blockchain, mostly.)

## Tips (staff-level)

- **Draw the state diagram** — Follower, Candidate, Leader with the transitions.
- **Walk through a concrete scenario** — leader dies, new election, log catch-up.
- **Name the safety properties** — election safety, leader completeness, state machine safety.
- **Discuss linearizable reads** — most candidates skip this.
- **Acknowledge Raft ≠ Paxos** — be honest about why you'd pick one.

## Pitfalls

- **"Just use Raft".** Without understanding log + state machine + election, you can't debug.
- **Ignoring linearizable reads.** Reads from stale followers are not linearizable.
- **Skipping log compaction.** Long logs → long catch-up times.
- **No pre-vote.** Partitioned nodes cause term thrashing on return.
- **Single-leader assumption.** Multi-leader (e.g. Leaderless DynamoDB) is a different model.

## Worked narration (3 min)

"Goal: 5-node cluster, linearizable KV ops, automatic failover in < 2s, survives 2 simultaneous failures.

**Substrate:** Raft. One Leader, rest Followers. Log = sequence of (term, index, command) entries. State machine applies committed entries.

**Election:** Followers time out (150-300ms random) → become Candidates, request votes. Majority → Leader. Heartbeats every 50ms suppress new elections. Pre-vote prevents disruption from partitioned nodes.

**Replication:** Leader appends to log → sends AppendEntries → waits for majority → commits → applies → responds. Followers replicate optimistically.

**Reads:** linearizable via read-index — Leader confirms quorum, then reads at commit index. Lease-read is faster if you trust clocks.

**Failure:** Leader dies → new election in 1-2s. Follower far behind → InstallSnapshot. Term thrashing → pre-vote + check-quorum.

**Scaling:** 1000s of Raft groups, each handles a key range. Cross-group transactions via 2PC or Percolator.

**First build:** Raft loop + read-index + snapshots. Add joint consensus for membership changes; cross-region is a separate problem."

## Related

- [[01-distributed-kv-cache]] — Raft is the replication primitive.
- [[04-distributed-lock-service]] — locks are consensus-backed leases.
- [[11-configuration-management]] — etcd / Consul *are* consensus-backed KVs.
- [[10-job-scheduler-task-queue]] — leader election picks the scheduler.