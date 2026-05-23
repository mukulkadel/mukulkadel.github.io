---
layout: post
title: "Database Indexing Explained: B-Trees, Covering Indexes, and When Indexes Hurt"
date: "2026-05-24 00:00:00 +0530"
slug: database-indexing-explained
description: "A practical guide to database indexing — how B-tree indexes work, when to use composite and covering indexes, and the hidden costs that make over-indexing a real problem."
categories: ["SQL", "wiki"]
tags: ["database", "indexing", "b-tree", "sql", "postgresql", "mysql", "performance", "query optimization", "covering index"]
---

An index is the single most impactful tool for query performance — and the most misunderstood. Adding an index to the right column can turn a 30-second query into a 30-millisecond one. Adding one to the wrong column, or adding too many, slows down every write operation and wastes storage. Understanding how indexes actually work makes it much easier to know when to use them and when to leave them off.

## How a B-Tree Index Works

Most database indexes use a **B-tree** (balanced tree) structure. Think of it like a phone book: entries are sorted alphabetically, so you can flip to the right section in a few steps instead of scanning every page.

A B-tree index stores a sorted copy of the indexed column's values alongside pointers to the actual table rows. When you run:

```sql
SELECT * FROM users WHERE email = 'alice@example.com';
```

Without an index, the database reads every row (a **sequential scan** or **full table scan**). With a B-tree index on `email`, it traverses the tree — O(log n) rather than O(n) — and jumps directly to the matching rows.

```sql
-- Create an index
CREATE INDEX idx_users_email ON users (email);

-- Verify it's being used
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'alice@example.com';
```

```
Index Scan using idx_users_email on users
  Index Cond: ((email)::text = 'alice@example.com'::text)
  Rows Removed by Filter: 0
  Actual rows: 1  Actual time: 0.045 ms
```

## Composite Indexes: Column Order Matters

A composite index covers multiple columns. The order of columns in the index definition determines which queries can use it.

```sql
CREATE INDEX idx_orders_user_status ON orders (user_id, status);
```

This index can efficiently serve:

```sql
SELECT * FROM orders WHERE user_id = 42;                         -- uses index
SELECT * FROM orders WHERE user_id = 42 AND status = 'pending'; -- uses index
SELECT * FROM orders WHERE status = 'pending';                   -- cannot use index
```

The rule: the database can use the index from the leftmost column forward. A query on only `status` can't use this index because `status` is not the leading column.

**Put the most selective column first** (the one that eliminates the most rows), unless your query patterns demand otherwise. For queries that filter on both `user_id` and `status`, putting the high-cardinality `user_id` first usually wins.

## Covering Indexes

A **covering index** includes all the columns a query needs — so the database can answer the query entirely from the index without touching the table rows at all. This is called an **index-only scan**.

```sql
-- Suppose this query runs thousands of times per minute:
SELECT user_id, status, created_at FROM orders WHERE user_id = 42;

-- A covering index for it:
CREATE INDEX idx_orders_covering ON orders (user_id, status, created_at);
```

```
Index Only Scan using idx_orders_covering on orders
  Heap Fetches: 0
  Actual time: 0.018 ms
```

"Heap Fetches: 0" means the query never touched the table — everything came from the index. This is often 2–5x faster than an index scan that still has to fetch rows.

## Partial Indexes

A **partial index** indexes only a subset of rows, defined by a `WHERE` clause:

```sql
-- Only index pending orders — if 95% of orders are completed, this index is much smaller
CREATE INDEX idx_orders_pending ON orders (user_id)
WHERE status = 'pending';
```

A smaller index fits better in memory, is faster to scan, and cheaper to maintain. Use partial indexes when queries consistently filter on a low-cardinality column with a dominant value.

## Unique Indexes

A unique index both enforces a constraint and speeds up equality lookups:

```sql
CREATE UNIQUE INDEX idx_users_email ON users (email);
```

This does double duty — it's effectively a constraint (`INSERT` of a duplicate email fails) and an index. Primary keys always have a unique index created automatically.

## When Indexes Hurt

Indexes are not free. Every write operation — `INSERT`, `UPDATE`, `DELETE` — must also update all indexes on the affected table.

**Too many indexes** on a write-heavy table (e.g., an event log or metrics table) can make writes significantly slower:

```sql
-- Each insert here must update 8 indexes
INSERT INTO events (user_id, type, data, created_at) VALUES (...);
```

**Indexes on low-cardinality columns** — like a boolean `is_active` or a `status` with three possible values — rarely help. The database will often choose a full table scan anyway because the index points to too many rows to make the extra lookup step worthwhile.

**Unused indexes** waste disk space and slow every write. In PostgreSQL, you can find them:

```sql
SELECT schemaname, tablename, indexname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0
  AND indexname NOT LIKE '%pkey%'
ORDER BY tablename;
```

Any index with `idx_scan = 0` since the last stats reset is a candidate for removal.

## Index Types Beyond B-Tree

PostgreSQL supports several index types for specific use cases:

| Type | Best for |
|---|---|
| `HASH` | Equality-only lookups (`=`), faster than B-tree for this case |
| `GIN` | Full-text search, arrays, JSONB containment |
| `GiST` | Geospatial data, range types, nearest-neighbor search |
| `BRIN` | Very large tables where rows are physically ordered (e.g., time-series) |

For most queries on standard columns, B-tree is the right choice. Reach for GIN when querying JSONB or `tsvector`, and BRIN for append-only tables with hundreds of millions of rows.

```sql
-- GIN index for JSONB
CREATE INDEX idx_products_attrs ON products USING gin (attributes);
SELECT * FROM products WHERE attributes @> '{"color": "red"}';

-- Full-text search
CREATE INDEX idx_articles_fts ON articles USING gin (to_tsvector('english', body));
SELECT * FROM articles WHERE to_tsvector('english', body) @@ to_tsquery('python & tutorial');
```

## Reading EXPLAIN Output

`EXPLAIN ANALYZE` is the primary tool for understanding what the query planner actually does:

```sql
EXPLAIN ANALYZE SELECT * FROM orders WHERE user_id = 42 AND status = 'pending';
```

Key terms to understand:

- **Seq Scan** — full table scan. Expected on small tables; a red flag on large ones.
- **Index Scan** — uses an index, then fetches rows from the table (heap).
- **Index Only Scan** — all data comes from the index; no heap access.
- **Bitmap Index Scan** — used when many rows match; collects row pointers in a bitmap before fetching.
- **cost=X..Y** — estimated cost units (not milliseconds). The second number is total cost.
- **Actual time** — real milliseconds. Compare to cost to gauge planner accuracy.

## A Practical Indexing Workflow

1. Identify slow queries via `pg_stat_statements` or your application's slow query log.
2. Run `EXPLAIN ANALYZE` on each slow query.
3. Look for sequential scans on large tables or high row counts at filter nodes.
4. Add an index on the filter/join columns, considering covering and partial index options.
5. Re-run `EXPLAIN ANALYZE` to confirm the index is used.
6. Monitor write performance to confirm the new index doesn't degrade inserts.
7. Periodically audit `pg_stat_user_indexes` and drop unused indexes.

## Conclusion

A good index is invisible — queries just run fast. A missing index shows up as production incidents. A bad index shows up as slow writes that nobody can explain. The mental model to keep: indexes trade write overhead for read speed, they're most effective on high-cardinality columns used in `WHERE` and `JOIN` clauses, and covering indexes are the ceiling of what an index can do for a given query. Start with `EXPLAIN ANALYZE`, add indexes surgically, and audit for unused ones regularly.
