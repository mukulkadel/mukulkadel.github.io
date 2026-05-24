---
layout: post
title: "Database Sharding and Partitioning: When and How"
date: "2026-05-24 00:00:00 +0530"
slug: database-sharding-partitioning-explained
description: "Understand the difference between database sharding and partitioning, when each technique applies, and what trade-offs you accept when you split your data."
categories: ["SQL", "wiki"]
tags: ["sharding", "partitioning", "database", "scalability", "postgresql", "horizontal scaling", "architecture", "sql", "nosql"]
---

When a single database table grows past tens of millions of rows, queries slow down, index builds take forever, and eventually even hardware upgrades stop helping. Sharding and partitioning are the two main techniques for splitting that data into manageable pieces — but they operate at different levels and come with very different trade-offs. Understanding the distinction before you reach for either will save you from an architecture that's harder to maintain than the original problem.

## Partitioning vs Sharding

These terms get conflated, but they're meaningfully different:

- **Partitioning** splits a table into smaller physical pieces within a single database instance. The split is transparent to queries — you still query one logical table.
- **Sharding** splits data across multiple database instances (separate servers). Each shard is an independent database with a subset of the rows. Your application or a routing layer must know which shard to talk to.

Partitioning is a storage optimization. Sharding is a distributed systems problem.

## Table Partitioning in PostgreSQL

PostgreSQL supports declarative partitioning natively since version 10. You create a parent table with a partitioning strategy, then attach child tables for each partition.

### Range partitioning (most common)

Split by date, ID range, or any ordered value. Great for time-series data where you mostly query recent rows and want to drop old data cheaply.

```sql
CREATE TABLE orders (
  id          BIGSERIAL,
  user_id     INT NOT NULL,
  total       NUMERIC NOT NULL,
  created_at  TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (created_at);

CREATE TABLE orders_2024_q1 PARTITION OF orders
  FOR VALUES FROM ('2024-01-01') TO ('2024-04-01');

CREATE TABLE orders_2024_q2 PARTITION OF orders
  FOR VALUES FROM ('2024-04-01') TO ('2024-07-01');

CREATE TABLE orders_2024_q3 PARTITION OF orders
  FOR VALUES FROM ('2024-07-01') TO ('2024-10-01');

CREATE TABLE orders_2024_q4 PARTITION OF orders
  FOR VALUES FROM ('2024-10-01') TO ('2025-01-01');
```

Queries with a date filter will hit only the relevant partition(s):

```sql
EXPLAIN SELECT * FROM orders WHERE created_at >= '2024-07-01' AND created_at < '2024-10-01';
-- Only orders_2024_q3 is scanned
```

Dropping a quarter's worth of old data is now instant — `DROP TABLE orders_2024_q1` vs a slow `DELETE` on millions of rows.

### List partitioning

Split by discrete values. Useful when you have a known, finite set of categories:

```sql
CREATE TABLE events (
  id      BIGSERIAL,
  region  TEXT NOT NULL,
  payload JSONB
) PARTITION BY LIST (region);

CREATE TABLE events_us PARTITION OF events FOR VALUES IN ('us-east', 'us-west');
CREATE TABLE events_eu PARTITION OF events FOR VALUES IN ('eu-west', 'eu-central');
CREATE TABLE events_apac PARTITION OF events FOR VALUES IN ('ap-south', 'ap-east');
```

### Hash partitioning

Distribute rows evenly across N partitions by hashing a column. Good when there's no natural range or list key:

```sql
CREATE TABLE sessions (
  id      UUID NOT NULL,
  user_id INT NOT NULL,
  data    JSONB
) PARTITION BY HASH (user_id);

CREATE TABLE sessions_0 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 0);
CREATE TABLE sessions_1 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 1);
CREATE TABLE sessions_2 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 2);
CREATE TABLE sessions_3 PARTITION OF sessions FOR VALUES WITH (MODULUS 4, REMAINDER 3);
```

### Indexes on partitioned tables

Create indexes on the parent table — PostgreSQL automatically creates matching indexes on all partitions:

```sql
CREATE INDEX ON orders (user_id);
CREATE INDEX ON orders (created_at);
```

### When partitioning helps

- Table is large (100M+ rows for most workloads)
- Queries almost always filter on the partition key
- You need cheap bulk deletes of old data (`DROP TABLE partition`)
- You want parallel query across partitions on a multi-core machine

### When partitioning doesn't help

- Most queries don't filter on the partition key (all partitions scan anyway)
- The table has lots of small, random writes (partition routing adds overhead)
- The bottleneck is write throughput, not read latency

## Sharding

Sharding distributes rows across multiple independent database servers. The canonical example is sharding by `user_id`: users 1–1M go to shard 1, users 1M–2M go to shard 2, and so on.

### Shard key selection

The shard key is the most important decision. A poor choice causes:

- **Hot spots**: one shard gets all the traffic (e.g., sharding a social network by user_id when a few celebrity accounts generate 80% of reads)
- **Cross-shard queries**: any query that can't be answered by a single shard requires scatter-gather across all shards, which is slow and complex

Good shard keys:
- High cardinality (many distinct values)
- Evenly distributed in access patterns
- Present in most queries as a filter

### Routing strategies

**Range sharding**: shard 0 handles IDs 0–999999, shard 1 handles 1000000–1999999, etc. Easy to reason about, but uneven if new IDs cluster on the highest shard.

**Hash sharding**: `shard = hash(user_id) % num_shards`. Even distribution, but adding or removing shards requires re-hashing most data.

**Consistent hashing**: a ring-based approach where adding a shard only moves a fraction of data. Used by Cassandra, DynamoDB, and Vitess.

### The operational cost

Sharding introduces problems that partitioning avoids entirely:

- **Cross-shard joins**: a query joining users to orders when they're on different shards must be done in application code or a middleware layer
- **Distributed transactions**: atomic writes across shards require two-phase commit or event-based sagas
- **Schema migrations**: must be applied to every shard, often with careful coordination
- **Rebalancing**: when traffic grows unevenly, moving data between shards is a major operation

### Tools that manage sharding for you

Rather than sharding manually, most teams use a layer that handles routing:

- **Vitess**: MySQL sharding proxy used by YouTube, GitHub, Slack
- **Citus** (PostgreSQL extension): turns PostgreSQL into a distributed database
- **PlanetScale**: MySQL-compatible, Vitess-backed cloud database
- **CockroachDB / Spanner**: distributed SQL databases with automatic sharding

```bash
# Citus example: distribute a table across workers
SELECT create_distributed_table('orders', 'user_id');
```

## Deciding Which Approach to Use

```
Single machine, table too large for comfortable queries?
  → Try partitioning first

Still too slow after partitioning + indexing?
  → Check if vertical scaling (bigger instance) defers the problem affordably

Write throughput exceeds what one machine can handle?
  → Sharding (or a purpose-built distributed database)

Multi-tenant SaaS, data isolation required per tenant?
  → Sharding by tenant_id (or separate databases per tenant)
```

The honest answer for most applications: you won't need sharding. PostgreSQL handles billions of rows on a large instance with good partitioning and indexing. Sharding is a last resort that trades simplicity for scale — only reach for it after exhausting every other option.

## Conclusion

Partitioning is a local optimization — one database, one logical table, multiple physical files. It's transparent to queries, easy to add, and solves the common problem of large append-mostly tables. Sharding is a distributed systems decision that affects your entire application architecture. Most teams benefit from range partitioning on `created_at` long before they need to think about shards, and many never need sharding at all. Start simple, measure, and scale the part that's actually the bottleneck.
