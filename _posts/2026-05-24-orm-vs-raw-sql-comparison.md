---
layout: post
title: "ORM vs Raw SQL: Trade-offs and When to Switch"
date: "2026-05-24 00:00:00 +0530"
slug: orm-vs-raw-sql-comparison
description: "Compare ORMs like SQLAlchemy and Prisma against raw SQL, understand the performance and maintainability trade-offs, and know when to drop down to raw queries."
categories: ["SQL", "wiki"]
tags: ["orm", "sql", "sqlalchemy", "prisma", "database", "python", "javascript", "backend", "performance", "comparison"]
---

Every backend developer eventually faces the ORM vs raw SQL debate, usually after hitting a query that the ORM generates badly or after spending an afternoon debugging why SQLAlchemy is doing seven round trips instead of one. Both approaches have legitimate uses, and the pragmatic answer is almost always "use both" — but knowing when to switch is the skill worth developing. This post covers the real trade-offs with concrete examples in Python (SQLAlchemy) and JavaScript/TypeScript (Prisma).

## What an ORM Does

An ORM (Object-Relational Mapper) lets you interact with your database using the language's native objects instead of SQL strings. It handles connection management, query generation, and (in most ORMs) migrations.

### SQLAlchemy (Python)

```python
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import User, Order

engine = create_engine("postgresql://localhost/mydb")

with Session(engine) as session:
    users = session.scalars(
        select(User)
        .where(User.created_at > "2024-01-01")
        .order_by(User.name)
        .limit(50)
    ).all()
```

Generated SQL (roughly):

```sql
SELECT users.id, users.name, users.email, users.created_at
FROM users
WHERE users.created_at > '2024-01-01'
ORDER BY users.name
LIMIT 50;
```

### Prisma (TypeScript)

```typescript
const users = await prisma.user.findMany({
  where: { createdAt: { gt: new Date("2024-01-01") } },
  orderBy: { name: "asc" },
  take: 50,
});
```

Both produce the same SQL from type-safe, autocompleted code.

## Where ORMs Win

### Boilerplate elimination

CRUD operations that would each require a parameterized SQL string become one-liners:

```python
# Create
user = User(name="Alice", email="alice@example.com")
session.add(user)
session.commit()

# Update
user.name = "Alice Smith"
session.commit()

# Delete
session.delete(user)
session.commit()
```

### Parameterization is automatic

ORMs handle query parameterization, so you never accidentally write:

```python
# This is SQL injection waiting to happen
query = f"SELECT * FROM users WHERE name = '{user_input}'"
```

With an ORM, user input is always passed as a parameter, not interpolated into the query string.

### Migrations and schema management

Tools like Alembic (SQLAlchemy) and Prisma Migrate generate migration files from your model definitions:

```bash
# Prisma: generate migration after changing schema.prisma
$ npx prisma migrate dev --name add_role_to_users

# Alembic: generate migration after changing models.py
$ alembic revision --autogenerate -m "add role to users"
```

### Relationship loading

ORMs let you express relationships declaratively and handle join logic for you:

```python
# SQLAlchemy: load user with their orders in one query
user = session.scalars(
    select(User)
    .options(selectinload(User.orders))
    .where(User.id == 42)
).one()

for order in user.orders:
    print(order.total)
```

## Where ORMs Struggle

### Complex aggregations

Anything beyond simple GROUP BY usually produces awkward ORM code or forces you into raw expressions anyway:

```python
# ORM way — verbose and hard to read
from sqlalchemy import func

result = session.execute(
    select(
        User.id,
        func.count(Order.id).label("order_count"),
        func.sum(Order.total).label("lifetime_value"),
    )
    .join(Order, Order.user_id == User.id)
    .where(User.created_at > "2024-01-01")
    .group_by(User.id)
    .having(func.sum(Order.total) > 1000)
    .order_by(func.sum(Order.total).desc())
).all()
```

Raw SQL version:

```sql
SELECT
  u.id,
  COUNT(o.id)     AS order_count,
  SUM(o.total)    AS lifetime_value
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.created_at > '2024-01-01'
GROUP BY u.id
HAVING SUM(o.total) > 1000
ORDER BY SUM(o.total) DESC;
```

The SQL is shorter, clearer, and easier to paste into a query analyzer.

### The N+1 query problem

The classic ORM footgun: loading a list of objects and then accessing a relationship on each one triggers a separate query per row.

```python
# This fires 1 + N queries (one for users, one per user for orders)
users = session.scalars(select(User)).all()
for user in users:
    print(len(user.orders))  # lazy load fires here
```

Fix it with eager loading:

```python
users = session.scalars(
    select(User).options(selectinload(User.orders))
).all()
# Now it's 2 queries: one for users, one for all orders
```

But knowing when this will happen requires understanding what the ORM does under the hood — which somewhat defeats the abstraction.

### Generated SQL quality

ORMs sometimes produce queries that are technically correct but inefficient. The only way to know is to log and inspect the SQL:

```python
# SQLAlchemy: enable query logging
import logging
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)
```

```typescript
// Prisma: log all queries
const prisma = new PrismaClient({ log: ["query"] });
```

Always check the generated SQL for performance-critical paths.

## Dropping Down to Raw SQL

Both SQLAlchemy and Prisma support raw queries when you need them.

### SQLAlchemy raw SQL

```python
from sqlalchemy import text

result = session.execute(
    text("""
        SELECT
          u.id,
          u.name,
          COUNT(o.id) FILTER (WHERE o.status = 'completed') AS completed_orders
        FROM users u
        LEFT JOIN orders o ON o.user_id = u.id
        WHERE u.created_at > :since
        GROUP BY u.id, u.name
        ORDER BY completed_orders DESC
        LIMIT :limit
    """),
    {"since": "2024-01-01", "limit": 20},
).mappings().all()
```

Parameters are still bound properly — no injection risk.

### Prisma raw SQL

```typescript
const results = await prisma.$queryRaw<UserStats[]>`
  SELECT
    u.id,
    u.name,
    COUNT(o.id) FILTER (WHERE o.status = 'completed') AS completed_orders
  FROM users u
  LEFT JOIN orders o ON o.user_id = u.id
  WHERE u.created_at > ${new Date("2024-01-01")}
  GROUP BY u.id, u.name
  ORDER BY completed_orders DESC
  LIMIT ${20}
`;
```

The tagged template literal automatically parameterizes interpolated values.

## When to Use What

| Situation | Recommendation |
|---|---|
| Standard CRUD operations | ORM |
| Simple filtering, sorting, pagination | ORM |
| Migrations and schema management | ORM tooling |
| Complex aggregations, window functions | Raw SQL |
| Reporting queries | Raw SQL |
| N+1 problem you can't easily fix | Raw SQL with JOIN |
| Query needs EXPLAIN tuning | Raw SQL |
| Full-text search, JSON operations | Raw SQL (or ORM expressions) |

A practical middle ground: use the ORM for all CRUD and simple reads, but maintain a `queries/` directory of `.sql` files for complex reports and analytics. Load them with `text()` or `$queryRaw`. This keeps the benefits of ORM (migrations, connection pooling, parameterization) while letting complex queries be written and tested as SQL.

## Conclusion

ORMs are not an abstraction over SQL — they're a productivity layer on top of it. They shine for CRUD, schema management, and straightforward reads. They become a liability when query complexity grows, when generated SQL performs poorly, or when you need database-specific features. The best codebases use ORMs as the default and drop to raw SQL when the problem calls for it, rather than committing fully to one side of the debate.
