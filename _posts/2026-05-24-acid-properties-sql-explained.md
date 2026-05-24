---
layout: post
title: "ACID Properties Explained with Real SQL Examples"
date: "2026-05-24 00:00:00 +0530"
slug: acid-properties-sql-explained
description: "Understand ACID — Atomicity, Consistency, Isolation, and Durability — with clear SQL examples showing what each property actually protects you from."
categories: ["SQL", "wiki"]
tags: ["acid", "transactions", "sql", "database", "atomicity", "consistency", "isolation", "durability", "postgresql"]
---

ACID is one of those acronyms that gets dropped in interviews and architecture discussions, but is often explained in terms that are too abstract to be useful. At its core, ACID is a set of guarantees that a database gives you about what happens when things go wrong — a crash mid-transaction, two users updating the same row simultaneously, a disk failure after a write. Understanding each property concretely helps you reason about when you need transactions and what isolation level to choose. All examples use PostgreSQL syntax.

## What Is a Transaction?

A transaction is a group of SQL statements that the database treats as a single unit. Either all of them succeed, or none of them do.

```sql
BEGIN;
  UPDATE accounts SET balance = balance - 100 WHERE id = 1;
  UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;
```

Without a transaction, the two UPDATEs are independent. A crash between them would leave one account debited and the other never credited.

## A — Atomicity

**Atomicity** means all-or-nothing. If any statement in a transaction fails, the entire transaction is rolled back — as if none of it ever happened.

```sql
BEGIN;
  UPDATE accounts SET balance = balance - 500 WHERE id = 1;
  -- This UPDATE fails (id 999 doesn't exist, and a trigger rejects it)
  UPDATE accounts SET balance = balance + 500 WHERE id = 999;
ROLLBACK;  -- triggered automatically on error in most setups
```

After the rollback, account 1's balance is unchanged. The failed second update doesn't partially commit.

You can also roll back explicitly when your application detects a business rule violation:

```sql
BEGIN;
  UPDATE accounts SET balance = balance - 500 WHERE id = 1;

  -- Check the result in application code
  SELECT balance FROM accounts WHERE id = 1;
  -- If balance < 0, issue ROLLBACK instead of COMMIT
COMMIT;
```

## C — Consistency

**Consistency** means a transaction can only bring the database from one valid state to another. "Valid" is defined by your constraints, triggers, and rules.

```sql
CREATE TABLE accounts (
  id      SERIAL PRIMARY KEY,
  balance NUMERIC NOT NULL CHECK (balance >= 0)
);
```

Now trying to overdraw an account fails at the database level, not just in application code:

```sql
BEGIN;
  UPDATE accounts SET balance = balance - 10000 WHERE id = 1;
  -- ERROR: new row violates check constraint "accounts_balance_check"
ROLLBACK;
```

Consistency is partly the database's job (enforcing constraints) and partly your application's job (writing correct logic). ACID guarantees the database half — referential integrity, check constraints, unique constraints — all hold at every commit.

## I — Isolation

**Isolation** is the most nuanced property. It controls how concurrent transactions see each other's in-progress changes. SQL defines four isolation levels:

| Level | Dirty Read | Non-Repeatable Read | Phantom Read |
|---|---|---|---|
| Read Uncommitted | possible | possible | possible |
| **Read Committed** | prevented | possible | possible |
| Repeatable Read | prevented | prevented | possible |
| **Serializable** | prevented | prevented | prevented |

PostgreSQL defaults to **Read Committed** and supports up to **Serializable**. It doesn't implement Read Uncommitted.

### Dirty reads

A dirty read occurs when you read uncommitted data from another transaction. If that transaction rolls back, you've read data that never officially existed.

```sql
-- Transaction A
BEGIN;
UPDATE products SET price = 9.99 WHERE id = 1;
-- Not committed yet

-- Transaction B (Read Uncommitted level, not available in PG)
SELECT price FROM products WHERE id = 1;
-- Would see 9.99 even though A hasn't committed
```

PostgreSQL prevents this at all supported levels.

### Non-repeatable reads

Reading the same row twice within a transaction and getting different values because another transaction committed between your two reads.

```sql
-- Transaction A (Read Committed)
BEGIN;
SELECT balance FROM accounts WHERE id = 1;
-- Returns 1000

-- Transaction B commits at this point:
-- UPDATE accounts SET balance = 800 WHERE id = 1; COMMIT;

SELECT balance FROM accounts WHERE id = 1;
-- Returns 800 — different result within the same transaction
COMMIT;
```

Use **Repeatable Read** to prevent this:

```sql
BEGIN ISOLATION LEVEL REPEATABLE READ;
-- Both SELECTs return 1000, even after B commits
COMMIT;
```

### Phantom reads

A query returns a different set of rows when run twice because another transaction inserted or deleted rows that match your WHERE clause.

```sql
-- Transaction A (Repeatable Read)
BEGIN ISOLATION LEVEL REPEATABLE READ;
SELECT COUNT(*) FROM orders WHERE user_id = 5;
-- Returns 3

-- Transaction B inserts a new order for user 5 and commits

SELECT COUNT(*) FROM orders WHERE user_id = 5;
-- Still returns 3 under Repeatable Read in PostgreSQL (snapshot isolation)
COMMIT;
```

PostgreSQL's Repeatable Read actually prevents phantom reads too, because it uses snapshot isolation. Use **Serializable** when you need strict serial execution guarantees for complex logic.

### Choosing an isolation level

```sql
BEGIN ISOLATION LEVEL SERIALIZABLE;
-- Safest, but may cause serialization failures that your app must retry
```

For most web applications, **Read Committed** is the right default. Use **Repeatable Read** or **Serializable** only for financial transactions or any logic where reading stale data mid-transaction would produce incorrect results.

## D — Durability

**Durability** means once a transaction commits, the data survives crashes. The database writes to a write-ahead log (WAL) before confirming the commit, so even if the server loses power the instant after you get `COMMIT`, the transaction is recoverable.

```sql
BEGIN;
  INSERT INTO orders (user_id, total) VALUES (1, 49.99);
COMMIT;
-- From this point forward, the row exists even through a crash
```

Durability is mostly invisible in daily SQL work — it's a property of the storage layer. The key implication: `COMMIT` is a real guarantee, not optimistic. If your application receives a successful `COMMIT` response, the data is on disk.

## Practical patterns

### Use savepoints for nested logic

```sql
BEGIN;
  INSERT INTO orders (user_id, total) VALUES (1, 100.00);

  SAVEPOINT after_order;

  INSERT INTO order_items (order_id, product_id, qty) VALUES (1, 42, 2);
  -- If this fails:
  ROLLBACK TO SAVEPOINT after_order;
  -- The order INSERT is still live; only items were rolled back

COMMIT;
```

### Advisory locks for application-level coordination

```sql
BEGIN;
  SELECT pg_advisory_xact_lock(42);  -- application-defined lock ID
  -- Safe to do multi-step logic knowing no other session holds lock 42
COMMIT;
-- Lock is released automatically at transaction end
```

## Conclusion

Atomicity, Consistency, Isolation, and Durability each address a different failure mode: mid-transaction crashes, constraint violations, concurrent access, and disk failures. Most of the time your database handles these transparently — but knowing what each guarantee covers helps you choose the right isolation level, write safer transactions, and understand why "just wrap it in a transaction" is often the correct answer to race condition bugs.
