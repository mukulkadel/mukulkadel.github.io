---
layout: post
title: "Connection Pooling Explained: Why max_connections Isn't Enough"
date: "2026-05-25 00:00:00 +0530"
slug: database-connection-pooling-explained
description: "Understand how database connection pooling works, why raising max_connections alone won't prevent connection storms, and how PgBouncer solves the problem at scale."
categories: ["wiki", "SQL"]
tags: ["connection pooling", "pgbouncer", "database", "postgresql", "performance", "backend", "scalability", "connections"]
---

Every time your application opens a database connection, PostgreSQL forks a new backend process and completes a TCP handshake — a process that can add 20–50ms of latency per request. That overhead is acceptable for a handful of users, but catastrophic when hundreds of API requests pile up simultaneously. Connection pooling solves this by maintaining a set of open, reusable connections. The catch: setting `max_connections = 500` in `postgresql.conf` doesn't give you a pool. It just raises the ceiling, and that's a different problem entirely.

## What a Connection Actually Costs

Each PostgreSQL connection spawns a backend process that reserves roughly 5–10 MB of memory for its working set. With 200 connections open simultaneously, you've burned 1–2 GB before a single query runs. Beyond memory, every extra connection adds overhead to PostgreSQL's internal lock management and connection scheduler.

The practical ceiling for direct connections to a healthy PostgreSQL instance is around 100–300, depending on server RAM and query complexity.

## How Connection Pooling Works

A connection pool sits between your application and the database. On startup, it opens a fixed number of connections and holds them open. When your app needs the database:

1. It requests a connection from the pool
2. The pool hands over an idle connection
3. The app runs its query and returns the connection
4. The pool reuses that connection for the next request — no teardown, no new TCP handshake

```
App servers (many threads)
         |
         v
  Pool (small set of open connections)
         |
         v
     PostgreSQL
```

The pool acts as a multiplexer: many concurrent application threads share a small number of actual database connections.

## Application-Level Pooling

Most database drivers include pooling. With Python's SQLAlchemy:

```python
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://user:pass@localhost/mydb",
    pool_size=10,         # connections kept open
    max_overflow=5,       # extra connections allowed when pool is full
    pool_timeout=30,      # seconds to wait before raising an error
    pool_recycle=1800,    # recycle connections older than 30 min to avoid stale sockets
)
```

With Node.js and `pg`:

```javascript
const { Pool } = require('pg')

const pool = new Pool({
  connectionString: 'postgresql://user:pass@localhost/mydb',
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
})

const result = await pool.query('SELECT * FROM orders WHERE id = $1', [orderId])
```

Application-level pooling works well for a single server. The problem emerges when you run 20 application server instances, each with a pool of 10 connections — that's 200 connections to PostgreSQL before any request is slow.

## PgBouncer: Pooling at the Infrastructure Level

[PgBouncer](https://www.pgbouncer.org/) is a lightweight, standalone pooler that sits in front of PostgreSQL. All your application servers connect to PgBouncer, and PgBouncer maintains a small set of real PostgreSQL connections.

```
App server 1 (pool_size=10) ─┐
App server 2 (pool_size=10) ─┤──▶  PgBouncer (20 real connections)  ──▶  PostgreSQL
App server 3 (pool_size=10) ─┘
```

A minimal `pgbouncer.ini`:

```ini
[databases]
mydb = host=127.0.0.1 port=5432 dbname=mydb

[pgbouncer]
listen_port = 6432
listen_addr = 0.0.0.0
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
server_pool_size = 20
max_client_conn = 1000
```

Point your apps at port 6432 instead of 5432. PostgreSQL sees only 20 connections; PgBouncer multiplexes up to 1,000 client connections across those 20.

## Pool Modes: Session, Transaction, Statement

PgBouncer's three pooling modes have different trade-offs:

**Session pooling**: a server connection is assigned for the lifetime of the client session. Works with all PostgreSQL features — prepared statements, advisory locks, `SET` variables — but provides the least multiplexing.

**Transaction pooling**: a server connection is assigned only for the duration of a transaction and released immediately after `COMMIT` or `ROLLBACK`. This is the most effective mode for API servers. A connection is only held while a query is in-flight. Trade-off: session-level features like `LISTEN/NOTIFY` and session-scoped prepared statements don't work.

**Statement pooling**: a connection is released after every individual statement. Breaks multi-statement transactions; rarely used in production.

For most web backends, transaction pooling gives the best throughput:

```ini
pool_mode = transaction
```

## Sizing Your Pool

Counterintuitively, a larger pool isn't always better. PostgreSQL can only process one query per CPU core at a time. Piling more connections on top just adds processes waiting for CPU time, increasing latency through context switching.

A practical starting formula (from the HikariCP documentation):

```
pool_size = (core_count * 2) + effective_spindle_count
```

For a 4-core server with SSDs (spindle count = 1), that's roughly 9 connections. That sounds small, but a 9-connection pool on a properly sized server often outperforms a 100-connection pool because there's no scheduling overhead.

Monitor PostgreSQL's `pg_stat_activity` to tune from there:

```sql
SELECT state, count(*)
FROM pg_stat_activity
WHERE datname = 'mydb'
GROUP BY state;
```

```
     state      | count
----------------+-------
 active         |     8
 idle           |    12
 idle in trans  |     2
(3 rows)
```

A persistently high `idle in transaction` count means your application is holding transactions open longer than necessary — a connection leak pattern.

## Connection Storms and Why `max_connections` Doesn't Prevent Them

A connection storm happens when many application instances restart simultaneously — after a deploy or a crash — and each one tries to open its full pool of connections at once. PostgreSQL rejects connections above `max_connections` with:

```
FATAL: sorry, too many clients already
```

Raising `max_connections` just raises the ceiling for how badly a storm can hurt you. PgBouncer absorbs the impact: client connections queue at PgBouncer, and PgBouncer slowly acquires server connections as they become available. The database stays healthy while your app fleet restarts.

## Checking Connection Health

Beyond `pg_stat_activity`, watch `pg_stat_bgwriter` for checkpoint performance and check your pool stats via PgBouncer's admin console:

```bash
$ psql -h 127.0.0.1 -p 6432 -U pgbouncer pgbouncer
```

```sql
SHOW POOLS;
```

```
 database | user     | cl_active | cl_waiting | sv_active | sv_idle | maxwait
----------+----------+-----------+------------+-----------+---------+--------
 mydb     | appuser  |        18 |          0 |        12 |         8 |       0
```

`cl_waiting > 0` means clients are queuing for a connection — your `server_pool_size` may be too low or your queries are running long.

## Conclusion

Connection pooling is one of the highest-leverage performance improvements for any database-backed application. Application-level pools handle single-server deployments well. Once you scale to multiple app servers, a dedicated pooler like PgBouncer is essential — it prevents connection storms, reduces PostgreSQL memory pressure, and lets transaction pooling dramatically increase throughput. Size your pool based on your database server's CPU count, not your application's thread count, and let `pg_stat_activity` and PgBouncer's admin console guide your tuning.
