---
layout: post
title: "Understanding the CAP Theorem with Practical Examples"
date: "2026-05-24 00:00:00 +0530"
slug: cap-theorem-explained
description: "The CAP theorem states you can only guarantee two of three properties in a distributed system. Here's what that actually means for the databases you use every day."
categories: ["wiki"]
tags: ["cap theorem", "distributed systems", "consistency", "availability", "partition tolerance", "database", "architecture", "nosql"]
---

The CAP theorem shows up in every distributed systems discussion, but it's often presented in a way that makes it sound like a menu — "pick two." In practice, partition tolerance isn't optional in real networks, which means the real choice is between consistency and availability when something goes wrong. Understanding what that trade-off actually looks like in production systems explains a lot about why your database behaves the way it does.

## The Three Properties

**Consistency (C)**: Every read returns the most recent write, or an error. All nodes see the same data at the same time. This is the "C" in ACID as well, though the CAP definition is specifically about linearizability — reads reflect all completed writes.

**Availability (A)**: Every request receives a response (not an error), though that response might not contain the most recent data. The system stays up and answering.

**Partition Tolerance (P)**: The system continues operating even when network messages are dropped or delayed between nodes — i.e., when nodes can't communicate.

Eric Brewer's original theorem (1998, proven by Gilbert and Lynch in 2002): a distributed system can satisfy at most two of these three guarantees simultaneously.

## Why P Is Not Really Optional

A network partition means two nodes in your cluster can't talk to each other — maybe a switch failed, a cable was cut, or a datacenter lost connectivity. In any real distributed system, this will happen. The question isn't whether to tolerate partitions; it's what to do when one occurs.

That means the real choice is **CP vs AP**:

- **CP**: When a partition happens, some nodes refuse to answer requests until the partition heals. You get consistency at the cost of availability.
- **AP**: When a partition happens, nodes keep answering with whatever data they have. You get availability at the cost of consistency — different nodes may return different values.

## CP Systems: Consistency Over Availability

In a CP system, if a node can't confirm that its data is up to date (because it can't reach a quorum of peers), it returns an error rather than a potentially stale answer.

### ZooKeeper

ZooKeeper is used for distributed coordination — leader election, configuration management, distributed locks. It uses a majority-quorum protocol: reads and writes require acknowledgment from more than half the nodes.

```
Cluster: nodes A, B, C
A loses network access to B and C (partition)

Client asks A: "Is node X the leader?"
A refuses to answer — it can't confirm its view is current
ZooKeeper returns an error to the client
```

This is the right behavior for a lock manager. A stale "yes, you hold the lock" answer from an isolated node could let two processes believe they hold the same lock simultaneously.

### PostgreSQL (single primary + replicas)

A primary with synchronous replication is effectively CP. Writes require acknowledgment from at least one replica before the client gets a success response. If the replica is unreachable, writes block or fail.

```sql
-- Synchronous replication: write does not return until replica confirms
ALTER SYSTEM SET synchronous_standby_names = 'replica1';
```

During a partition where the primary can't reach its synchronous replica, writes stall — consistent but not fully available.

## AP Systems: Availability Over Consistency

AP systems keep responding even during a partition. Nodes may diverge and return different values, but they never refuse a request.

### Cassandra

Cassandra distributes data across nodes using consistent hashing. You configure the replication factor and consistency level per query.

```
Cluster: 3 nodes, replication factor 3
Node B is partitioned (unreachable)

Write to key "user:42" with consistency=ONE:
→ Node A accepts the write and acknowledges immediately
→ Node C also has a copy of the write
→ Node B is unaware of the write

Read "user:42" from Node B (still serving requests):
→ Returns stale data
→ System is available, but temporarily inconsistent
```

When the partition heals, Cassandra uses anti-entropy (background repair) to reconcile the nodes. The data eventually converges — this is called **eventual consistency**.

### DynamoDB

DynamoDB is also AP by default. Reads at the default `Eventually Consistent` level may return stale data but always return data. You can opt into `Strongly Consistent` reads, which route to the primary replica — trading some availability for C.

```python
# Eventually consistent (default) — faster, may be stale
response = table.get_item(
    Key={"user_id": "42"},
    ConsistentRead=False
)

# Strongly consistent — slower, always current
response = table.get_item(
    Key={"user_id": "42"},
    ConsistentRead=True
)
```

## Where Real Databases Sit

| Database | Default positioning | Notes |
|---|---|---|
| PostgreSQL (single node) | CA (no partition) | Single node; add replication to get distributed |
| PostgreSQL (sync replication) | CP | Writes stall if replica unreachable |
| PostgreSQL (async replication) | AP | Replica may lag; reads from replica may be stale |
| MySQL (Group Replication) | CP | Uses Paxos-like consensus |
| Cassandra | AP | Tunable consistency per query |
| DynamoDB | AP (default) / CP (strong reads) | Configurable |
| Redis Cluster | AP | Partitioned nodes keep serving cached data |
| ZooKeeper | CP | Refuses reads from partitioned minority |
| MongoDB | CP (default) | Primary required for writes; reads can be directed to secondaries |
| CockroachDB | CP | Uses Raft consensus; serializable by default |

## The Nuance: PACELC

The CAP theorem only describes behavior during a partition. PACELC (pronounced "pass-elk") extends it to describe the normal case too:

> If there's a **P**artition, trade off **A**vailability vs **C**onsistency. **E**lse, trade off **L**atency vs **C**onsistency.

Even without a partition, replicated databases face a latency/consistency trade-off: synchronous replication to all nodes before responding (consistent, slower) vs acknowledging the write immediately and replicating asynchronously (faster, risk of staleness on replicas).

This is why DynamoDB and Cassandra both let you tune consistency level per query — you're choosing your position on the latency/consistency curve for each operation.

## Practical Implications

**Choose CP when**: correctness is more important than uptime. Financial transactions, inventory counts, distributed locks, authentication tokens. Returning stale data is worse than returning an error.

**Choose AP when**: availability is more important than real-time accuracy. User profile caches, product catalog reads, social media feeds, analytics. A slightly stale response is fine; an error is not.

**Most applications use both**: transactions on the primary (CP) for writes, reads from replicas (AP) for read-heavy queries. This is the read replica pattern — and it means your application must handle the case where a read immediately after a write misses the just-written data.

## Conclusion

The CAP theorem's real lesson isn't that you get to pick two properties — it's that network partitions are inevitable, and you need a deliberate policy for what your system does when they happen. CP systems protect correctness at the cost of availability; AP systems protect availability at the cost of immediate consistency. Knowing which behavior your database provides by default, and how to tune it, is foundational to designing systems that behave correctly under real-world conditions.
